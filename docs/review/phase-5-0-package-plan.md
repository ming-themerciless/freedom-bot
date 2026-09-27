# Package 5.0 — Migration and cutover harness

Readiness statement, design proposal, work breakdown and impact assessment.
**Revision 12 — remediation R11. Independently security re-reviewed 2026-09-02;
P5.0-SR1 and P5.0-SR2 Closed on design; package remains `not ready`.**

**Current governance update, 2026-09-22.** I3 is Closed on the accepted clean
R8 replacement evidence. The two R6 findings are Closed as retained historical
violations; R6 remains inadmissible as gate evidence. This removes the I3/R6
decision dependency only. **P5.0-R5 remains Blocking, OD-62 remains Open with
G-A provisional, `plan.is_executable=False`, and this package remains not
ready.** No host action, implementation, migration or `--execute` is authorized.

**Post-cutover verification decision, 2026-09-22.** Each approved field-group
cutover has a **four-week** verification window. Its source Sheet is frozen
read-only and retained with the export, connector, credential and rollback path.
PostgreSQL is the sole authority; no dual writes and no live diagnostic Sheet
are permitted. Retirement requires the completed verification gate and explicit
maintainer approval.

**Current implementation authorization, 2026-09-13.** C-P5.0-LAB-I authorizes
repository implementation and local tests for the accepted r6 laboratory
mechanism and the bounded code required to address C-7 and EH-R16-1. It does not
authorize target access, preflight, provisioning, database operations or
execution. The implementation returns for independent Codex technical and
security review; all package gates retain their current states.

**Prior evidence status, 2026-09-13.** Codex's independent
[LAB-1 R3 re-review](project-review-2026-09-13-lab1-rereview-r3.md) accepts the
bounded local remediation with no residual finding. LAB-1 is closed locally,
but no package gate moves: C-7 and EH-R16-1 remain unresolved, the twelve target
facts remain unconfirmed, P5.0-R5 remains Blocking, OD-62 remains Open and
`is_executable` remains `False`. No host action or execution is authorized.

**Historical evidence direction, 2026-09-10 — C-P5.0-LAB-1.** Follow the
[reserved-laboratory direction](phase-5-0-reserved-laboratory-direction.md) and
[Claude prompt](phase-5-0-reserved-laboratory-claude-prompt.md). VM expansion is
deferred. This changes the laboratory trust premise and next work assignment,
not the accepted production controls, schema or recovery criteria. No finding
closes; readiness, operational execution and product implementation remain gated.
Any required criterion split must return for an explicit decision.

**Historical evidence-harness proposal update, 2026-09-10.** The current action is Claude's
independent review of Codex's [VM alternative](phase-5-0-evidence-vm-design.md)
and [proposed ADR 0011](../adr/0011-disposable-vm-evidence-boundary.md), under
the explicit prompt in [Handover information](Handover%20information).
The proposal changes the outer laboratory ownership/cleanup contract only if
accepted; it does not amend this package's journal/probe recovery requirements.
Neither the architecture nor its new management surface is accepted. The
September 10 findings and EH-R16-1 remain open; no readiness, implementation,
host inspection, provisioning or execution approval is implied. Revision 12's
accepted design inputs remain binding; this pointer does not revise its schema.

**Governance update, 2026-09-02.** Peter Duscha approved OD-64 Option A,
OD-65 Option B and OD-66 Option A / J-1. OD-62 remains Open with G-A recorded
only as the provisional direction pending P5.0-R5 operational evidence and
independent review. These rulings supersede the older open-state wording
retained later in this revision for decision history. Residuals R-5.0-12 through
R-5.0-16 still require explicit disposition; the package remains `not ready`
and implementation remains unauthorized.

Date: 2026-08-31

Prepared by: Claude — implementer and working Technical Lead (designated by
Peter Duscha, OD-61)

Acceptance Authority, Product Owner, Data Owner, Operations Owner, Delivery
Lead: Peter Duscha

Independent Reviewer, independent logical-schema reviewer and Security
Reviewer: Codex (OD-61, closed 2026-08-31).

> **Security review of revision 11, 2026-08-31: changes requested; no readiness
> recommendation.** `docs/review/phase-5-0-security-review.md` raised two
> findings. **P5.0-SR1 — Blocking:** the deployment integrity check can be
> skipped silently, because `deployment_manifest_digest()` compares a digest of
> the live deployed bytes with a caller-supplied copy of that same value and
> therefore establishes consistency after deployment, not **provenance from the
> reviewed commit**. **P5.0-SR2 — Important:** §2.12.2 said `freedomcoord` and
> `freedomsheet` were members of their own groups only while §2.13.3 and the
> E1–E8 evidence identities required both to be members of `freedomjournal`, so
> the two contracts could not both be followed. **Revision 12 is the remediation
> of both, and claims no finding closed.** §2.12.5a states a fail-closed
> reviewed-source provenance contract binding deployment and generation
> registration to an immutable Git object and an out-of-band approval record,
> with the negative test the finding requires; §2.12.2 becomes the single
> canonical primary/supplementary membership table that provisioning, the holder
> table and E1–E8 all cite. **The `C-1` host check is still not run, the C-3 and
> C-4 operational checks are still not authorized, the three declared residuals
> are still unaccepted, P5.0-R5 remains Blocking, and Package 5.0 remains `not
> ready`.** An independent security re-review of revision 12 is required.

> **Independent re-review of revision 11, 2026-08-31: no new Blocking or
> Important design finding.** R10-A through R10-C are materially addressed on
> paper. The `capsh(1)` construction has a documented execution order, states
> the launching bounding-set prerequisite, derives every E1–E8 capability mask,
> and makes the E4/E6 and E1/E2 controls isolate the authority they claim.
> `git diff --check` is clean. No privileged or implementation suite was run:
> A-5.0-5 is unconfirmed and this package remains documentation/design-only.
> This review closes the R10 remediation request, **not P5.0-R5 and not the
> package gate**. P5.0-R5 remains Blocking pending authorized operational
> evidence; P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed; OD-62
> through OD-66 remain Open; the Security Reviewer remains unnamed; Package 5.0
> remains `not ready`; and implementation, migration, deployment, cutover and
> Package 5.1+ remain unauthorized.

> **Independent re-review of revision 10, 2026-08-31: changes requested;
> P5.0-R5 remains Blocking.** R9-A's owner/`CAP_FOWNER` decomposition and
> R9-B's primitive-versus-holder separation are materially improved, but R9-C
> is not executable as specified. The E2–E6 recipes use
> `setpriv --securebits=+keep_caps,+no_setuid_fixup`; util-linux 2.39.3 rejects
> `keep_caps` because `execve` clears that bit, so those commands exit before
> producing the declared identities. E8 declares `CapBnd=0x0` without dropping
> its bounding set, and E7 does not state complete inheritable and ambient
> masks despite the complete-mask requirement. The mandatory
> `/proc/self/status` precondition would therefore make the affected
> `JNL-49`/`JNL-50` cases inconclusive rather than executable. Remediation R10
> must define syntactically valid launch recipes for the named target tool,
> state every P/E/I/A/B mask for E1–E8, and make each recipe and declared mask
> agree. No privileged case needs to be run during this documentation-only
> remediation, but constructibility must be checked against the target tool's
> documented contract. No implementation, migration or environment change is
> authorized.

> **Independent re-review of revision 9, 2026-08-30: changes requested;
> P5.0-R5 remains Blocking.** The R8 deployment-digest, cleanup-state and
> forged-host-identity corrections are materially addressed. The replacement
> authority model is not yet executable: Linux `FS_IOC_SETFLAGS` requires the
> caller to own the inode or hold `CAP_FOWNER`, in addition to
> `CAP_LINUX_IMMUTABLE` for `FS_IMMUTABLE_FL`/`FS_APPEND_FL`. Therefore a
> non-root process holding only `CAP_LINUX_IMMUTABLE` cannot clear `+i` on the
> root-owned archive as claimed, and A1 combined with A3 or A4 is insufficient
> when DAC was obtained without ownership or `CAP_FOWNER`. The register also
> says A1–A6 confer nothing on one another while F-1a says every real A3 holder
> also holds A2. Remediation R9 and revision 10 must correct the authority
> primitives, combinations and executable evidence before another review. No
> implementation, migration or environment change is authorized.

> **Submission status: revision 11 is remediation R10. Package 5.0 remains
> `not ready` and implementation remains unauthorized.** Codex's 2026-08-31
> independent re-review of revision 10 found that R9-C's executable-identity
> recipes do not construct the identities they declare. **The defect is conceded
> and corrected here**, and it is written into §2.13.1 as defects **25–28**
> *before* its replacement is presented. **R9-A's owner/`CAP_FOWNER`
> decomposition and R9-B's primitive-versus-holder separation are preserved
> unchanged in substance**, as the R10 brief requires: no authority row, no
> falsification row, no holder row and no bounded claim moves.
>
> - **R10-A — the launch recipes were not valid for the tool they named.**
>   Revision 10 built **E2 … E6** with
>   `setpriv --securebits=+keep_caps,+no_setuid_fixup`. The installed and named
>   `setpriv(1)` from util-linux **2.39.3** documents its accepted securebits as
>   *"noroot, noroot\_locked, no\_setuid\_fixup, no\_setuid\_fixup\_locked, and
>   keep\_caps\_locked"* and states that *"keep\_caps is cleared by execve(2) and
>   is therefore not allowed"*. Those five commands exit **127** at option
>   parsing, before any identity exists. **Conceded without argument.** Revision
>   11 does not patch the option list: it **changes the mechanism** to
>   `capsh(1)` from libcap **2.66**, because `setpriv(1)` does not document the
>   order in which it applies securebits, the UID/GID change and the three
>   capability sets — and every declared mask depends on that order — whereas
>   `capsh(1)` documents that it *"takes a number of optional arguments, acting
>   on them in the order they are provided"*. §2.13.5c states the mechanism, its
>   ownership, mode, absence of file capabilities, lifecycle, cleanup, authority
>   and security-review consequence, and the **seven-step construction** with the
>   kernel rule each step relies on.
> - **R10-B — three identities declared masks their own recipes did not
>   produce.** The re-review named **E8**, which declared `CapBnd=0x0` and never
>   dropped its bounding set, and **E7**, which wrote dashes for inheritable and
>   ambient. A mechanical recipe-versus-mask comparison finds a **third**, which
>   revision 10 did not notice: **E2 … E6** requested
>   `--bounding-set=+linux_immutable`, which is an **add** to the bounding set —
>   the same `setpriv(1)` page states that *"the kernel does not permit
>   capabilities to be added to the bounding set"* — and which, starting from
>   root's full set, would have left `CapBnd` at `0x000001ffffffffff` rather than
>   the declared `0x200`. Revision 11 states **E1 … E8** with exact effective
>   UID, GID, the exact supplementary-group list, exact `CapPrm`, `CapEff`,
>   `CapInh`, `CapAmb`, `CapBnd` **and securebits**, gives each a complete
>   invocation rather than *"as E2/E3"*, and carries a **mask-versus-recipe
>   comparison table** in which every cell is derived from the command line.
> - **R10-C — the dependent evidence is revalidated, and one control pair is
>   redesigned.** Every E-identity reference in `JNL-49`, `JNL-50`, `JNL-13`,
>   `JNL-35`, `JNL-38`, `JNL-48`, A-5.0-5 and the logical-schema evidence mapping
>   was rechecked. **The case counts do not change** — `JNL-49` and `JNL-50` stay
>   at twelve each and the band stays at **fifty identifiers and eighty-eight
>   cases** — because R10 corrects how an identity is built, not which cases
>   exist. **One pair did change and is redesigned rather than defended**:
>   `JNL-50` case 7 and `JNL-49` case 11 named **E2** as the positive control for
>   an **E4** refusal, but E2 differs from E4 in uid, groups **and** two
>   capabilities. The isolating control is **E6**, which differs from E4 in
>   `CAP_FOWNER` and nothing else; E2 is retained as a **corroborating** control
>   by the ownership route and is labelled as such. A second control form is
>   added for `JNL-50` case 4, where no identity differing by one capability
>   exists: hold the identity fixed and **vary the inode's owner**.
> - **No privileged case is claimed to have run.** **A-5.0-5** is widened to name
>   the new mechanism and remains **unconfirmed**. The host was **read**
>   non-mutatingly for the tool contract — §8.1 **H-6** — and was not written.
>
> **Claude claims no finding closed.** Closure belongs to the Independent
> Reviewer. In particular:
>
> - **P5.0-R5 remains Blocking.** Revision 11 answers the R10 findings; it does
>   not decide whether they are answered. **An independent re-review of revision
>   11 is required.**
> - **The R8-A deployment-digest lifecycle, the R8-B cleanup state machine, the
>   R8-D/F-7 residual treatment and revision 10's R9-A and R9-B corrections are
>   preserved unchanged in substance**, as the R10 brief requires. **No corrected
>   executable identity produced a conflict with any of them**, so nothing was
>   stopped and reported under the brief's conflict clause.
> - **P5.0-R1's Sheet half is still not closed and is not claimed closed.**
>   §2.10.2's conclusion is unchanged, and revision 11 narrows **R-5.0-8** by no
>   cases at all. **P5.0-R4's operational evidence is not claimed passed.**
>   **P5.0-R2 remains closed**, and OD-55 and OD-58 remain preserved.
> - **D5.0-9 … D5.0-13 / OD-62 … OD-66 remain Open**, and the Security Reviewer
>   remains **unnamed**. **No option, risk, decision or schema object is adopted
>   or closed by R10**, and no decision number is added. The `capsh` mechanism is
>   an **evidence-harness** correction inside A-5.0-5's unconfirmed scope; it is
>   not a production-tooling change, not an adopted option, and it is routed to
>   the Security Reviewer in §9.2 rather than decided here.
> - **Package 5.0 is `not ready` and implementation remains unauthorized.**
>
> **No implementation or environment change occurred.** No production code, no
> migration `0014`, no table, no database role, no operating-system account or
> group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
> Google access change, no configuration or environment change, no directory,
> file, file mode or **filesystem attribute**, no deployment, no service restart,
> no `systemd-run`, no `chattr`, no `setpriv`, no `capsh`, no privileged probe,
> no data mutation, no Sheet access, no authority cutover, no Package 5.1+ work.
> `/var/lib/freedom-sheet-writer` does not exist on this host and was not
> created; **no probe arena, no `…/probe-ro` and no `fbprobe` identity were
> created anywhere.** **The host was read and not written**: §8.1 **H-6** records
> `setpriv --version`, `dpkg -l`, `ls -l`, `getcap` and `/proc/*/status` reads,
> all non-mutating, and no capability set, UID, GID or securebit was constructed
> anywhere. The only changes are to documents.

> **Superseded submission status: revision 10 was remediation R9. Package 5.0 remained
> `not ready` and implementation remained unauthorized.** Codex's 2026-08-30
> independent re-review of revision 9 found the replacement authority model
> incorrect against the Linux contract it depends on. **The defect was conceded
> and corrected there**, and it is written into §2.13.1 as defects **22–24**
> *before* its replacement is presented.
>
> - **R9-A — the inode-flag authority model omitted half of the kernel's
>   check.** `FS_IOC_SETFLAGS` requires the caller's **effective UID to match the
>   inode's owner, or `CAP_FOWNER`**; changing `FS_IMMUTABLE_FL` or
>   `FS_APPEND_FL` requires **`CAP_LINUX_IMMUTABLE` in addition**.
>   `CAP_DAC_OVERRIDE` is not a substitute for the owner check. Revision 9's
>   **A1** carried only the capability, so a non-root `CAP_LINUX_IMMUTABLE`-only
>   process was credited with clearing `+i` on the **root-owned** archive, which
>   it cannot do — it receives `EPERM` from the ioctl and never reaches the open.
>   **§2.13.5c is redesigned**: the kernel's checks are stated in a table of
>   their own *before* the register; **A1** is narrowed to the special-bit half;
>   **A10** (owner authorization over the `freedomsheet`-owned journal) and
>   **A11** (owner authorization over the root-owned seal and archive) are added
>   as separate rows, because their holder sets on this host are completely
>   different; and **eleven of the thirteen falsification rows gain a
>   prerequisite** — F-1a, F-4, F-5, F-8 … F-12 gain **A11**, F-1b gains **A10
>   and A11**, F-2 and F-5 gain **A10**. **Every correction makes an alteration
>   harder to construct**; no refusal is strengthened and no guarantee moves.
>   §2.13.4 gains the two flag rows the table never contained, and §2.13.7's
>   *"clearing needs `CAP_LINUX_IMMUTABLE`"* is completed.
> - **R9-B — the register asserted independence and reasoned from implication.**
>   Revision 9 said **A1 … A6 confer nothing on one another** and then, under
>   **F-1a**, that *"every real holder of A3 also holds A2"*. **Both cannot be
>   live text in one register.** Revision 10 separates what an authority **is**
>   from who can **hold** it: the register keeps the independence claim for the
>   **primitives**, a new **holder table** states which identities on this host
>   bundle which rows, and every falsification row is assessed **twice** — once
>   against its minimum combination, once against the **smallest identity that
>   can actually hold it**. **Bounded claim 2 is rewritten and materially
>   narrowed**: only **F-2, F-3 and F-6** are bounded by the attacker's authority
>   rather than by its choice of alteration.
> - **R9-C — the executable evidence contract asserted a result the kernel does
>   not produce.** Revision 9's `JNL-50` case 9 had a non-root
>   `CAP_LINUX_IMMUTABLE`-only identity clear `+i` *"successfully"* and then
>   receive `EACCES`; and `setpriv --ambient-caps=+linux_immutable` does not
>   build that set in any case, because an ambient capability must also be
>   permitted and inheritable and a `setuid` away from 0 clears the permitted set
>   without `SECBIT_KEEP_CAPS`/`SECBIT_NO_SETUID_FIXUP`. §2.13.5c adds an
>   **executable-identity table** — **E1 … E8**, each with effective UID, GID,
>   supplementary groups, complete permitted/effective/inheritable/ambient/
>   bounding sets as hexadecimal masks, its full `setpriv` invocation including
>   securebits, and a `/proc/self/status` assertion that runs **before** the
>   operation under test. `JNL-49` and `JNL-50` are rewritten at **twelve cases
>   each**, every negative flag case running with all other prerequisites
>   satisfied and carrying a **positive control that succeeds** — the **E4/E6**
>   pair isolating the owner check, **E2** isolating the capability against the
>   writer's own inode, and **E5** replacing revision 9's non-constructible case
>   with a real clear followed by a real `EACCES`. **These cases are not claimed
>   to have run**: **A-5.0-5** is corrected rather than carried forward, and
>   remains **unconfirmed**.
>
> **Claude claims no finding closed.** Closure belongs to the Independent
> Reviewer. In particular:
>
> - **P5.0-R5 remains Blocking.** Revision 10 answers the R9 findings; it does
>   not decide whether they are answered.
> - **The R8-A deployment-digest lifecycle, the R8-B cleanup state machine and
>   the R8-D withdrawal of F-7's forged-host-identity detector are preserved**,
>   as the R9 brief requires. They are neither reopened nor weakened: §2.13.2b,
>   §2.13.2c, F-7 and **R-5.0-13** are carried forward unchanged in substance.
> - **P5.0-R1's Sheet half is still not closed and is not claimed closed.**
>   §2.10.2's conclusion is unchanged, and revision 10 narrows **R-5.0-8** by no
>   cases at all.
> - **P5.0-R4's operational evidence is not claimed passed.** OD-64, OD-65, the
>   Security Reviewer and the named privileged checks remain open.
> - **P5.0-R2 remains closed**, and OD-55 and OD-58 remain preserved.
> - **D5.0-9 … D5.0-13 / OD-62 … OD-66 remain open**, and the Security Reviewer
>   remains **unnamed**. **No option is adopted and no decision number is added.**
>   D5.0-13 / OD-66 option A's *content* does not move either: R9 corrects the
>   description of a kernel check option A already depended on.
>
> **No implementation or environment change occurred.** No production code, no
> migration `0014`, no table, no database role, no operating-system account or
> group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
> Google access change, no configuration or environment change, no directory,
> file, file mode or **filesystem attribute**, no deployment, no service
> restart, no `systemd-run`, no `chattr`, no `setpriv`, no privileged probe, no
> data mutation, no Sheet access, no authority cutover, no Package 5.1+ work.
> `/var/lib/freedom-sheet-writer` does not exist on this host and was not
> created; **no probe arena, no `…/probe-ro` and no `fbprobe` identity were
> created anywhere**. **The host was neither read nor written for this
> remediation.** The only changes are to documents.

> **Superseded submission status: revision 9 was remediation R8. Package 5.0 remained
> `not ready` and implementation remained unauthorized.** Codex's 2026-08-30
> independent re-review of revision 8 found four Blocking internal
> inconsistencies. **All four are conceded and corrected here**, and each is
> written into §2.13.1 as defects **18–21** *before* its replacement is
> presented.
>
> - **R8-A — the deployment digest was consumed before it was validated, and
>   what C2 compared was not an independent source.** Revision 8's **C1** passed
>   the operator-supplied `writer_deployment_digest` to the probe, which copied
>   it into the report; **C2** then compared the report's copy with the supplied
>   value. That comparison is a tautology — it passes for **any** string,
>   including a wrong one — and it sits *after* the step that consumed the value,
>   so the asserted `produced < validated ≤ consumed` was false in its first row.
>   Revision 9 corrects the **design**: **C0 computes the digest itself** over
>   the deployed writer's manifest and refuses unless the supplied value equals
>   the computed one, so the value C1 consumes has been validated against the
>   **deployed bytes**; **C2 keeps a post-production consistency check** and adds
>   a **second computation** that detects a deployment changed between C0 and the
>   probe's capture. §2.13.2c defines who computes the digest, over exactly which
>   bytes, and when it becomes final; the universal inequality is **withdrawn**
>   and replaced by five precise invariants **I-1 … I-5** that every row of the
>   value table satisfies. `JNL-46` grows from one case to **five**.
> - **R8-B — cleanup failure was required to produce two mutually exclusive
>   states.** `JNL-47` asserted that a failure injected in cleanup leaves **no**
>   `…/probe` or `…/probe-ro` residue, while `JNL-48(d)` planted an undeletable
>   artifact and required it to **remain**, be reported, and make the next **C0**
>   refuse. Revision 9 replaces both with one explicit state machine — **new
>   §2.13.2b** — distinguishing *probe-stage failure with cleanup succeeding*,
>   *cleanup failure*, and *the next invocation*. **“No generation artifact”
>   stays true in every state; “no transient residue” is stated as conditional on
>   cleanup success.** For the next invocation the design now specifies **one**
>   behaviour and not two: **C0 and `verify-capability` refuse for operator
>   recovery**, and revision 8's automatic residue clean-and-reuse step is
>   **withdrawn**. `JNL-47` grows from five cases to **six**.
> - **R8-C — `CAP_LINUX_IMMUTABLE` was treated as bypassing discretionary access
>   control.** It permits flag control and nothing else: a non-root holder can
>   clear `+i` on a `root:freedomcoord 0440` archive file inside a
>   `root:freedomcoord 0750` directory and still receive `EACCES` on the open.
>   The eight-capability register is **withdrawn** and replaced by **nine
>   independently constructible authorities** — flag control, DAC on the journal
>   file, DAC on `…/journal` and its seal, DAC on `…/archive`, DAC on the
>   deployment path, host identity/restoration, full host-root identity,
>   coordinator authentication/insertion, and PostgreSQL mutation — with every
>   falsification row stating the minimum **combination**. **F-2, F-4 and F-5 are
>   re-evaluated and each changes**; `JNL-49` and `JNL-50` grow to **ten cases
>   each** and are executed under identities and capability sets that really hold
>   the combination.
> - **R8-D — F-7 named a host-identity detector that does not exist.** If **A6**
>   rewrites `/etc/machine-id` to the recorded value, **W10 passes** and **C-d
>   compares the registered row against the same value**, so nothing refuses.
>   Revision 9 takes the honest option: a forged matching host identity is
>   **classified as a residual that neither W10 nor C-d detects** (**R-5.0-13**),
>   the changed-device/inode reasoning is **withdrawn** as incidental, and the
>   independent operational evidence that remains is named. The alternative — a
>   genuinely independent authenticated host-bound value — is **routed** as
>   D5.0-13 / OD-66 **option A-2** under §0.2 and is **not adopted**.
>
> **Claude claims no finding closed.** Closure belongs to the Independent
> Reviewer. In particular:
>
> - **P5.0-R5 remains Blocking.** Revision 9 answers the R8 findings; it does not
>   decide whether they are answered.
> - **P5.0-R1's Sheet half is still not closed and is not claimed closed.**
>   §2.10.2's conclusion is unchanged: no accepted-request completion barrier
>   exists in the published Google surface. **A durable journal does not become
>   one** (§2.13.10), and revision 9 narrows **R-5.0-8** by no cases at all. The
>   journal remains an **enumeration control**.
> - **P5.0-R4's operational evidence is not claimed passed.** OD-64, OD-65, the
>   Security Reviewer and the named privileged checks remain open, and the
>   revision-4 host-boundary denial matrix is retained unchanged.
> - **P5.0-R2 remains closed**, and OD-55 and OD-58 remain preserved.
> - **D5.0-9 … D5.0-13 / OD-62 … OD-66 remain open**, and the Security Reviewer
>   remains **unnamed**.
> - **No decision number is added.** The one design movement that changes the
>   surface — an authenticated host-bound value — is raised as a **new option
>   inside the already-open D5.0-13 / OD-66** and is explicitly not adopted; the
>   other three corrections change option A's content, which §5.3 re-states.
> - **R7-B's exact S4-2 target and its positive DAC control are retained
>   unchanged**, as the R8 brief requires; only their cleanup contract moves.
>
> **No implementation or environment change occurred.** No production code, no
> migration `0014`, no table, no database role, no operating-system account or
> group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
> Google access change, no configuration or environment change, no directory,
> file, file mode or **filesystem attribute**, no deployment, no service
> restart, no `systemd-run`, no `chattr`, no `setpriv`, no data mutation, no
> Sheet access, no authority cutover, no Package 5.1+ work.
> `/var/lib/freedom-sheet-writer` does not exist on this host and was not
> created, and **no probe arena and no `…/probe-ro` were created anywhere**.
> **The host was neither read nor written for this remediation.** The only
> changes are to documents.

> **Superseded re-review outcome, 2026-08-30: revision 8, changes requested.**
> Revision 8 did not close P5.0-R5. Four Blocking internal inconsistencies were
> found:
>
> - **R8-A:** the supplied `writer_deployment_digest` is consumed at C1 but its
>   equality with the report is validated at C2, contradicting the asserted
>   `produced < validated ≤ consumed` invariant.
> - **R8-B:** `JNL-47` requires cleanup failure to leave no transient residue,
>   while `JNL-48(d)` requires the planted undeletable residue to remain, be
>   reported, and make the next C0 refuse.
> - **R8-C:** `CAP_LINUX_IMMUTABLE` can clear immutable flags but does not by
>   itself bypass archive DAC, so treating it alone as K4 leaves the capability
>   matrix and affected tests incorrect.
> - **R8-D:** when K6 rewrites `/etc/machine-id` to the value already recorded,
>   both W10 and C-d's comparison with the registered row see the same value;
>   F-7 therefore names no independent host-identity detector.
>
> R7-B's exact S4-2 positive-control design was recorded as materially
> addressed, subject to R8-B's cleanup correction. This block is retained as
> review history; revision 9 above is the response.

> **Superseded submission status: revision 8 was submitted for independent re-review under remediation R7.
> Package 5.0 remains `not ready` and implementation remains unauthorized.**
> Codex's 2026-08-30 re-review of revision 7 found three Blocking design defects
> and one Important governance defect. **All four are conceded and corrected
> here.**
>
> - **R7-A — Algorithm C had no executable order.** Step **C0** refused unless
>   `verify-capability` had already *"passed in this invocation, all four
>   stages"*, with a report whose `writer_deployment_digest` matched — and step
>   **C1** was the step that ran those stages and built that report. **An ordered
>   algorithm cannot validate an output before producing it.** Revision 8 takes
>   the re-review's preferred minimal correction: **C0** keeps only the
>   preconditions that exist before the probe runs; **C1** remains the single
>   invocation of the probe stages and the single creation point of the report;
>   a new **C2** validates the result-dependent facts — pass state, report
>   completeness, deployment-digest equality and cleanup success — **before any
>   persistent artifact exists**; and every subsequent step is renumbered to
>   **C0 … C13**, with the dependency graph, the refusal points, the
>   `verify-capability`/`init-generation` preconditions, the tests and every
>   cross-reference updated with it. A **value-dependency table** now states,
>   for every value the algorithm consumes, where it is produced, where it is
>   validated and where it is first consumed, so *produced < validated ≤
>   consumed* is checkable rather than asserted; **`JNL-46`** walks the
>   algorithm in order and proves it, and **`JNL-47`** injects a failure in each
>   of Stage 1 … Stage 4 and cleanup and proves that **no journal, seal, symlink
>   or registration row is created**.
> - **R7-B — S4-2 attributed `EROFS` without a positive control.** It appended
>   to an unspecified path *"outside `ReadWritePaths=`"* and treated `EROFS` as
>   evidence of `ProtectSystem=strict`, **without first proving that the same
>   path and file are writable by `freedomsheet` without the sandbox** — the
>   same attribution defect Stage 1 was created to correct, left uncorrected in
>   the one stage that runs under systemd. Revision 8 defines the **exact
>   target** and its whole lifecycle: a second transient directory
>   **`…/probe-ro`**, identical in ownership and mode to the arena, on the same
>   mount, inside `ProtectSystem=strict`'s read-only tree and **outside** the
>   substituted `ReadWritePaths=`; a new case **`S4-0`** proves open, append,
>   `fsync`, `rename` and `unlink` are permitted by DAC on that exact target
>   under the writer's uid **outside any unit**; and only then is `EROFS`
>   accepted, with `EACCES` classified as **`inconclusive`** and success as a
>   **failed** stage. Stage 4's cases become **`S4-0 … S4-3`**, the canonical
>   probe bytes, the evidence band, the estimate and every reference follow, and
>   **`JNL-48`** distinguishes the four outcomes the handoff enumerates.
> - **R7-C — the attacker-class matrix claimed reach its classes could not
>   construct.** Class 1 was defined as unable to clear `FS_APPEND_FL` and then
>   said to reach *"every row except F-1b"*, which its own definition forbids;
>   **F-2 was assigned class 1 while its own note conceded that rewriting record
>   0 requires class 2**. The two-class model is **withdrawn**, and with it every
>   "reaches every row except" claim. In its place: a register of **eight
>   independent capabilities** — seal write, journal-directory write,
>   journal-content rewrite needing `CAP_LINUX_IMMUTABLE`, archive
>   write/attribute control, deployment-path write, host identity/restoration
>   control, coordinator execution/authentication, and PostgreSQL row mutation or
>   insertion — and a per-row statement of the **minimum capability**, whether it
>   also reaches the **detector**, the **independent actor or artifact** that
>   refuses it, the **exact step and code**, and the **residual when the attacker
>   holds both**. **F-2 is corrected to `K3`** and F-3 … F-12 are re-evaluated;
>   **F-7's claim is corrected in the opposite direction**, because
>   `/etc/machine-id` is root-writable and revision 7 said it was not. The
>   negative assertion the re-review asks to keep is kept: a self-consistent
>   privileged host rewrite **passes V-W** and is refused only by the registered
>   PostgreSQL digests. Impossible pairings are marked **not constructible with
>   the control that makes them so**, and `JNL-49`/`JNL-50` give one case per
>   feasible pairing and one per not-constructible cell.
> - **R7-D — the controlled active-handoff reference.** Implementation-plan §20's
>   correction to revision 7 / R7 is **preserved** and updated to name revision 8
>   as the submitted response, and status, RAID, decisions, open-decisions and
>   the change log all name **R7** as the active remediation cycle.
>
> **Claude claims no finding closed.** Closure belongs to the Independent
> Reviewer. In particular:
>
> - **P5.0-R5 remains Blocking.** Revision 8 answers the R7 findings; it does not
>   decide whether they are answered.
> - **P5.0-R1's Sheet half is still not closed and is not claimed closed.**
>   §2.10.2's conclusion is unchanged: no accepted-request completion barrier
>   exists in the published Google surface. **A durable journal does not become
>   one** (§2.13.10), and revision 8 narrows **R-5.0-8** by no cases at all.
> - **P5.0-R4's operational evidence is not claimed passed.** OD-64, OD-65, the
>   Security Reviewer and the named privileged checks remain open, and the
>   revision-4 host-boundary denial matrix is retained unchanged.
> - **P5.0-R2 remains closed**, and OD-55 and OD-58 remain preserved.
> - **D5.0-9 … D5.0-13 / OD-62 … OD-66 remain open**, and the Security Reviewer
>   remains **unnamed**.
> - **No decision number is added.** Both design movements — `…/probe-ro` with
>   its control, and Algorithm C's validation step — are changes to the content
>   of **D5.0-13 / OD-66 option A**, which is already open, and they are recorded
>   there rather than adopted (§5.3).
> - The journal remains an **enumeration control, not a Google accepted-request
>   completion barrier**.
>
> **No implementation or environment change occurred.** No production code, no
> migration `0014`, no table, no database role, no operating-system account or
> group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
> Google access change, no configuration or environment change, no directory,
> file, file mode or **filesystem attribute**, no deployment, no service
> restart, no `systemd-run`, no `chattr`, no `setpriv`, no data mutation, no
> Sheet access, no authority cutover, no Package 5.1+ work.
> `/var/lib/freedom-sheet-writer` does not exist on this host and was not
> created, and **no probe arena and no `…/probe-ro` were created anywhere**.
> **The host was neither read nor written for this remediation.** The only
> changes are to documents.
>
> The revision-7 status block is superseded; its findings are recorded as
> defects 14–17 in §2.13.1 and are the subject of this revision.


Authority for this document: Peter Duscha approved the Phase 4 gate on
2026-08-29 (`C-P4-L`), selected package 5.0 for readiness planning (`C-P4-M`),
ruled D5.0-1 … D5.0-7 and partly D5.0-8 as OD-54 … OD-61 (`C-P5.0-B`), and
issued `docs/review/Handover information` — now the **post-review readiness and
authorization brief**, which authorizes no implementation and routes the open
decisions, security review and operational-evidence prerequisites to their
accountable owners.

Companion document: **[`phase-5-0-logical-schema.md`](phase-5-0-logical-schema.md)** —
the mandatory logical schema artifact, ER diagram, authority-state matrix and
schema decision table. It must be independently reviewed before any migration or
production code.

Revision-11 handback:
**[`phase-5-0-remediation-r10-handback.md`](phase-5-0-remediation-r10-handback.md)** —
the completed R10 response retained as review history. The independent
re-review closed R10 on 2026-08-31 without closing P5.0-R5 or authorizing the
package. The superseded
[`phase-5-0-remediation-r9-handback.md`](phase-5-0-remediation-r9-handback.md),
[`phase-5-0-remediation-r8-handback.md`](phase-5-0-remediation-r8-handback.md),
[`phase-5-0-remediation-r7-handback.md`](phase-5-0-remediation-r7-handback.md),
[`phase-5-0-remediation-r6-handback.md`](phase-5-0-remediation-r6-handback.md),
[`phase-5-0-remediation-r5-handback.md`](phase-5-0-remediation-r5-handback.md),
[`phase-5-0-remediation-r4-handback.md`](phase-5-0-remediation-r4-handback.md),
[`phase-5-0-remediation-r3-handback.md`](phase-5-0-remediation-r3-handback.md) and
[`phase-5-0-remediation-r2-handback.md`](phase-5-0-remediation-r2-handback.md) are
retained as review history.

## What changed in revision 12

Revision 12 is a **documentation and design remediation of the two findings the
Package 5.0 security review returned on 2026-08-31**, under a handoff that
authorizes documentation and design only. Both findings are conceded in
**§2.13.1 rows 29 and 30** before either replacement is presented. **No
production code, migration, database object, host artifact or environment state
was touched, no privileged probe, capability set, UID change, `chattr`, `capsh`
or `git` write was run, and no host object was created.** Revision 12 **rules
none of OD-62 … OD-66, claims no finding closed, and does not assert Package 5.0
ready.**

| Input | Effect on this plan |
|---|---|
| **P5.0-SR1** — *Blocking; make reviewed-source provenance a fail-closed input to deployment and generation activation* | **New §2.12.5a**, the deployment contract, and the withdrawal of §2.12.5's one-sentence *"compare the recorded SHA-256 of each deployed file against that commit"*, which is the control the finding says fails silently. Three facts must now agree and each comes from a **different** source: an **approved-revision record** `APR` installed by root out of band and naming the commit a review approved; a **trusted manifest** `TM` computed from **Git object bytes** in a root-owned bare mirror no service identity may read or write, addressed by object id and never through a ref, branch or tag; and the **deployed bytes**, projected through a new `deployed_source_manifest_digest()` so it is comparable with `TM`. The deploy step becomes an ordered algorithm **D0 … D8** with its own refusal family `DEP-01 … DEP-09`, a **closed two-region partition** of the deployed root — reviewed source and hash-pinned dependencies, with any unaccounted file a refusal — and a **provenance record** `PVR` written last, outside the deployed root so no digest covers itself. **Algorithm C `C0` gains the provenance preconditions and refuses when `PVR` is absent**, so omission is a refusal and never a default; **`SB` carries `source_commit`, `source_tree_id` and `source_manifest_digest`**; the writer re-checks them at new step **W11a**; and **`V-R` refuses to register a generation whose source revision has no row in the new `approved_source_revisions` table**, which is the database half — a `NOT NULL` foreign key, so an unprovenanced generation cannot be registered and the activation trigger's registered-generation precondition therefore cannot be met |
| **P5.0-SR2** — *Important; one canonical primary/supplementary membership table, used consistently* | **§2.12.2 becomes that table**, with primary and supplementary groups for every identity, a **group → members inverse** stating what each membership grants and does not grant, and a rule that **no other passage states a membership of its own**. The revision-11 sentence *"`freedomcoord` … is in no group any service identity holds"* is **withdrawn as false**, and replaced by the three claims that are true and separately testable. §2.13.3, §2.13.5c, §2.12.6, §2.12.7, §2.13.7 and logical schema §4.3.2 now **cite** it. **`E8` gains `freedomjournal`**, so the identity the evidence calls `freedomcoord` is the `freedomcoord` provisioning creates, and the identity table gains a column saying which provisioned identity each of `E1 … E8` corresponds to — three of them correspond to none and are labelled synthetic |
| Consequence — the evidence band | `TC-5.0-JNL` grows from **fifty identifiers to fifty-three** and from **eighty-eight cases to one hundred and fourteen**. `JNL-46` 5 → **9** (provenance record absent; a commit disagreeing with the approval record; a deployed byte changed after deploy; an unaccounted file). **`JNL-51`** — the deployment contract, **eight cases**, including **the negative test P5.0-SR1 requires**: the provenance step omitted, and `init-generation` then proved unable to create or register a generation at all. **`JNL-52`** — the canonical membership, **eight cases**: positive and negative `id`, `namei -l` and `open` evidence for `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`. **`JNL-53`** — the three new fail-closed conditions **J-26 … J-28**, **six cases**, one per condition per actor |
| Consequence — the fail-closed conditions | **§2.13.6 grows from twenty-five rows to twenty-eight** and the writer's refusal family from `SW-J01 … SW-J25` to **`SW-J01 … SW-J28`**. A separate family **`DEP-01 … DEP-09`** belongs to the deploy step, which is not the writer and not the coordinator |
| Consequence — the authority register and the matrix | **Eleven authorities, unchanged in number.** **`A5` is widened** to cover the root-owned source mirror, the approval record and the provenance record, because they are root-owned deployment-path artifacts and inventing a twelfth authority for them would misstate the holder set. The falsification matrix grows from **thirteen rows to fourteen**: **F-13**, an unreviewed deployment substituted for the approved one, refused by C0's four-way agreement, by **W11a** and by `V-R`'s foreign key — and **not** refused where the attacker also holds **A8**, which is residual **R-5.0-15** |
| Consequence — the schema | **One new table, `approved_source_revisions`** — the seventh — and **four new columns** on `sheet_writer_journal_generations`, one of them a `NOT NULL` foreign key. Grants, constraints, the append-only trigger and the evidence bands follow. There is **no withdrawal flag**: superseding an approved revision means approving another, and a generation binds to exactly one |
| Consequence — estimate and security-review effort | **Both rise, and the arithmetic is shown.** PERT **40.9 → 47.6** implementer-days, decomposed in §4 across WP-2, WP-4b, WP-6, WP-8, WP-9, WP-14, WP-15 and the new **WP-16**. Security review **3.5–4.5 → 4.5–5.5** reviewer-days over **twelve** surfaces, the twelfth being the reviewed-source provenance chain itself: an approval record, a root-owned object store and a root-run algorithm that installs code carrying authority |
| Consequence — the residuals and the risks | **One residual is added.** **R-5.0-15**: the approval record's integrity is root ownership and mode, so an actor holding **A7** writes it, and an actor holding **A8** can register a generation against a revision it approved — that boundary is operator trust, not a technical control, and it is recorded rather than described as a refusal. **R-5.0-16** records the availability cost: a deployment with no approval record cannot produce a generation at all. §7.1 gains rows **29** and **30**; stop conditions **10o** and **10p** are added |
| Consequence — the decisions | **No decision number and no option is added, and none is ruled.** **OD-65's scope is extended** by the root-owned source mirror, the approval record and the provenance record, and by the canonical membership table it must provision; **OD-66 option A's cost** gains the seventh table and the four columns, and a routed **option A-3** — a cryptographically signed approval record verified against a root-held keyring — is stated and **not adopted** |
| **The preserved corrections** | **§2.13.2b, §2.13.2c's `deployment_manifest_digest()` contract, F-7/R-5.0-13, the kernel-requirements table, the eleven-authority register, the holder table and the revision-11 `capsh(1)` construction are preserved unchanged in substance.** §2.13.2c is **extended** by the source projection and the region partition; nothing in it is reopened or weakened |
| **P5.0-R1**, **P5.0-R4**, **P5.0-R5** | **Unchanged, and deliberately so.** No operational evidence is claimed passed, and **P5.0-R5 remains Blocking** |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |

### What changed in revision 11 — retained

Revision 11 is a **documentation and design remediation of revision 10's own
executable-evidence contract**, under a handoff that authorizes documentation and
design only. Every row is a defect the re-review named — or, in one case, a
fourth that a mechanical check found — conceded, and replaced. **No production
code, migration, database object, host artifact or environment state was touched,
and no privileged probe, capability set, UID change or `chattr` was run.** The
host was **read** non-mutatingly to record the tool contract (§8.1 **H-6**).

| Input | Effect on this plan |
|---|---|
| **R10-A** — *replace the invalid capability-launch recipes* | **§2.13.5c's executable-identity subsection, rewritten.** The mechanism changes from `setpriv(1)` to **`capsh(1)`** (libcap 2.66, `/usr/sbin/capsh`, `root:root 0755`, **no file capabilities**, already installed as part of `libcap2-bin`). Two reasons, both from the tools' own manuals: `setpriv(1)` 2.39.3 **rejects `keep_caps`**, and it **does not document the order** in which it applies securebits, the UID/GID change and the three capability sets — on which every declared mask depends — whereas `capsh(1)` documents that it *"takes a number of optional arguments, acting on them in the order they are provided"*. `+keep_caps` is **not used anywhere**, and is not needed: `capabilities(7)` states that `SECBIT_NO_SETUID_FIXUP` *"provides a superset of the effect of"* `SECBIT_KEEP_CAPS` and, unlike it, survives `execve`. A **seven-step construction** is stated with the kernel rule each step relies on, ending in the `execve` transformation that makes `CapPrm`, `CapEff` and `CapAmb` all equal the ambient set for a file carrying no capabilities. The **prerequisite on the launching process's bounding set** is stated and asserted: no capability can be **added** to a bounding set by any tool, and `capsh` offers only `--drop` |
| **R10-B** — *make every identity complete and internally consistent* | **§2.13.5c's identity table, rebuilt.** **E1 … E8** each state exact effective UID and GID, the **exact supplementary-group list**, exact `CapPrm`, `CapEff`, `CapInh`, `CapAmb`, `CapBnd` **and securebits**, and a **complete invocation** — no *"as E2/E3"* shorthand survives. **E7's dashes are replaced** by the values read from this host: `CapInh` `0x0`, `CapAmb` `0x0`, and `0x000001ffffffffff` for permitted, effective and bounding, which is `CAP_LAST_CAP = 40` on kernel 6.8.0-138. **E8 gains the bounding-set drop** its declared `0x0` requires. A **mask-versus-recipe comparison table** is added, and it records **three** disagreements in revision 10, not two: the named E7 and E8 defects, and `--bounding-set=+linux_immutable` in **E2 … E6**, which asks for an addition the kernel forbids and would have left `CapBnd` at the full set |
| **R10-C** — *revalidate dependent evidence and claims* | **§2.13.8**, `JNL-49`, `JNL-50`, `JNL-13`, `JNL-35`, `JNL-38`, `JNL-48`, §2.13.2a, A-5.0-5 and logical-schema §9. **One control pair is redesigned rather than defended**: the isolating positive control for an **E4** owner-check refusal is **E6**, which differs from E4 by `CAP_FOWNER` alone — **E2**, which revision 10 named, differs in uid, groups and two capabilities, and is retained only as a **corroborating** control by the ownership route. A **second control form** is defined for `JNL-50` case 4, where no one-capability-apart identity exists: hold the identity fixed and **vary the inode's owner**. §2.13.2a's `setpriv --reuid=freedomsheet` privilege drop is **kept** and is explicitly **not** identity E1 |
| Consequence — the evidence band | **Unchanged: fifty identifiers and eighty-eight cases.** `JNL-49` stays at **twelve** and `JNL-50` at **twelve**; `JNL-13` stays at fifteen rows in one case. **R10 changes how an identity is constructed and which identity is the control, not which cases exist**, so there is no arithmetic to show |
| Consequence — the authority register, the matrix and the claims | **All unchanged.** Eleven authorities, thirteen falsification rows, the holder table, the two-column reach assessment and the six bounded claims are carried forward **verbatim in substance**. R10 touched no row of any of them, and **no corrected identity produced a conflict** with the preserved R8-A, R8-B, R8-D/F-7 or R9-A/R9-B corrections |
| Consequence — estimate and security-review effort | **Both unchanged — PERT 40.9 implementer-days and 3.5–4.5 reviewer-days.** The capability harness was already budgeted under WP-8 (+0.40) and WP-9 (+0.08) in revision 10; R10 substitutes one already-installed, non-setuid, no-file-capability system binary for another inside that machinery and adds one `prctl(PR_GET_SECUREBITS)` assertion. No case, identifier, artifact class, privileged command or host account is added, so there is no arithmetic to show and none is invented |
| Consequence — the schema | **None.** No column, constraint, index, trigger, sequence, vocabulary, table, command or health check changes. Logical schema §9's evidence mapping and §4.3.8's Band 3 are corrected in wording only |
| Consequence — the residuals and the risks | **No residual is added and none is narrowed.** §7.1 gains row **28**, a recurrence risk for the R10 defect class, and stop condition **10n** is added beside **10m** |
| Consequence — the assumptions | **A-5.0-5 is widened and corrected**: it now names `capsh` rather than `setpriv` for the E-identity harness, adds `libcap2-bin` on the target host and the launching process's full bounding set as prerequisites, and **remains unconfirmed** |
| **The preserved corrections** | **§2.13.2b, §2.13.2c, F-7/R-5.0-13 and revision 10's §2.13.5c kernel-requirements table, eleven-authority register, holder table and falsification matrix are preserved unchanged in substance.** None is reopened and none is weakened |
| **P5.0-R1**, **P5.0-R4** | **Unchanged, and deliberately so.** §2.10's barrier search stands, §2.12's host boundary stands, and **no operational evidence is claimed passed** for either |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |
| Decisions | **No decision number added and no option added.** D5.0-13 / OD-66's options do not move. Nothing here is approved, adopted or closed |

### What changed in revision 10 — retained

Revision 10 is a **documentation and design remediation of revision 9's own
authority model**, under a handoff that authorizes documentation and design only.
Every row is a defect the re-review named, conceded, and replaced. **No
production code, migration, database object, host artifact or environment state
was touched, and no privileged probe was run.**

| Input | Effect on this plan |
|---|---|
| **R9-A** — *correct the inode-flag authority model* | **§2.13.5c, redesigned.** A **kernel-requirements table** is stated before the register, naming every check `FS_IOC_SETFLAGS` makes: path traversal, open, **owner-or-`CAP_FOWNER`**, and `CAP_LINUX_IMMUTABLE` for the two flags — together with the two orderings that matter, that immutability is checked before DAC on a write open, and that the owner check is evaluated whether or not the flag capability is held. **A1** is narrowed to the special-bit half and explicitly confers **nothing on its own**. **A10** — owner authorization over the `freedomsheet`-owned journal file, held by `freedomsheet` **by ownership** — and **A11** — owner authorization over the root-owned seal and archive, held only by uid 0 or a `CAP_FOWNER` holder — are **separate rows**, because their holder sets on this host do not overlap. The register grows from nine authorities to **eleven**. **Eleven of the thirteen falsification rows gain a prerequisite**: F-1a, F-4, F-5, F-8, F-9, F-10, F-11 and F-12 gain **A11**; F-1b gains **A10 and A11**; F-2 and F-5 gain **A10**. F-3, F-6 and F-7 are unchanged, because none of them changes an inode flag. §2.13.4 gains the two rows the manipulation table never contained — `chattr -i` on the seal and on an archived file — reaching **fifteen rows**; §2.13.5b's verifier table restates its two authority combinations; and §2.13.7's *"clearing needs `CAP_LINUX_IMMUTABLE`"* is completed to name both requirements, which is a second and independent reason `freedom-journal-admin` runs as root |
| **R9-B** — *remove the A3/A2 contradiction* | **§2.13.5c**, which separates what an authority **is** from who can **hold** it. The register keeps the independence claim **for the primitives** — no row confers another by definition — and a new **holder table** states which identities on this host bundle which rows: the deployed writer, the writer's uid with an ambient capability, `freedomcoord`, the three other service identities, four non-root capability sets, uid 0 and a PostgreSQL superuser. **Every falsification row is then assessed twice**, against its minimum combination *and* against the smallest identity that can actually hold it, and the matrix carries both answers in one column. F-1a's qualification is no longer a footnote contradicting the register: it is the general case, stated as **bounded claim 2** and **materially narrowed** — only **F-2**, **F-3** and **F-6** are bounded by the attacker's authority rather than by its choice of alteration |
| **R9-C** — *rewrite the executable evidence contract* | **§2.13.5c's executable-identity table** and **§2.13.8's `JNL-49`/`JNL-50`**. Eight identities **E1 … E8**, each with effective UID, GID, supplementary groups, complete permitted/effective/inheritable/ambient/bounding sets as hexadecimal masks, the full `setpriv` invocation **including securebits**, and a `/proc/self/status` assertion of all of them that runs **before** the operation under test — an unasserted identity yielding **`inconclusive`**. Each case names its syscall, its expected result and its `errno`. Every negative flag case runs with **all other prerequisites satisfied** and carries a **positive control that succeeds** and differs by exactly the privilege under test: **E4/E6** isolate the owner check with DAC fully satisfied, **E1/E2** isolate the capability against the writer's own inode, and **E5** replaces revision 9's non-constructible case with a **real** `+i` clear followed by a **real** `EACCES` on the open. **`A-5.0-5` is corrected rather than carried forward** — the revision-9 assumption is withdrawn as not constructible — and remains **unconfirmed**; **no privileged case is claimed to have run** |
| Consequence — the falsification count | **Unchanged at thirteen** — F-1a, F-1b and F-2 … F-12. R9-A adds prerequisites to eleven rows; it adds, removes and reclassifies none |
| Consequence — the authority register | **Nine → eleven.** `A10` and `A11` are added; `A1` is narrowed; `A2` … `A9` keep their labels and their meanings, so every cross-reference elsewhere in the package plan and the logical schema remains valid |
| Consequence — the state table | **§2.13.6 stays at twenty-five rows**, and refusal codes stay `SW-J01 … SW-J25`. **No condition is added**: R9 corrects who can construct an alteration, not what the writer or the coordinator checks |
| Consequence — the evidence band | `TC-5.0-JNL` stays at **fifty identifiers** and grows from eighty-four cases to **eighty-eight**: `JNL-49` 10 → **12** and `JNL-50` 10 → **12**. **No identifier is added.** `JNL-13`, `JNL-30`, `JNL-35`, `JNL-38` and `JNL-48` change contract without changing count, and `JNL-13`'s manipulation matrix grows from thirteen rows to **fifteen**. §6.5 grows from nineteen items to **twenty** |
| Consequence — the schema | **None to the tables.** No column, constraint, index, trigger, sequence, vocabulary, table, command or health check changes. Logical schema §3.7's *What this table uniquely can do*, §3.7.1's `A9` row, §4.3.8's Band 3 and §9's traceability are corrected in wording and case counts |
| Consequence — estimate and controls | PERT **40.9** implementer-days, up from 40.4, decomposed in §4: WP-8 **+0.40**, WP-9 **+0.08**, WP-15 **+0.05**; every other package unchanged, **WP-4b included**, because R9 corrects the model of a kernel check the writer never invokes. Remediation allowance **11.9**; contingency 4.0. Security review rises to **3.5–4.5** reviewer-days — eleven authorities, a holder table to confirm identity by identity, and eleven changed combinations — with **eleven** surfaces unchanged and **two added reviewer questions**. New stop condition **10m**; **10k** extended. **No new numeric control** |
| Consequence — the residuals | **None added.** **R-5.0-12's authority set is corrected** to `A1 + A2 + A3 + A10 + A11 + A9`, which is a **larger** set than revision 9 named; **R-5.0-13** and **R-5.0-14** are unchanged. §7.1 gains row **27**, which is a recurrence risk for the R9-A defect class rather than a new residual |
| **The preserved R8 corrections** | **§2.13.2b's cleanup state machine, §2.13.2c's deployment digest and F-7's withdrawn detector are preserved unchanged in substance**, as the R9 brief requires. None is reopened and none is weakened |
| **P5.0-R1**, **P5.0-R4** | **Unchanged, and deliberately so.** §2.10's barrier search stands, §2.12's host boundary stands, and **no operational evidence is claimed passed** for either |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |
| Decisions | **No decision number added and no option added.** D5.0-13 / OD-66 option A's content does not move: R9 corrects the description of a kernel check option A already depended on. Nothing here is approved |

### What changed in revision 9 — retained

Revision 9 is a **documentation and design remediation of revision 8's own
claims**, under a handoff that authorizes documentation and design only. Every
row is a defect the re-review named, conceded, and replaced. **No production
code, migration, database object, host artifact or environment state was
touched.**

| Input | Effect on this plan |
|---|---|
| **R8-A** — *make Algorithm C's validation order truthful and executable* | **New §2.13.2c** defines the deployment digest before any algorithm consumes it: **who computes it** (root, from the deployed manifest, using the single named function the writer also runs at **W11**), **the exact bytes** (every file under the deployed writer root and its unit file and drop-ins, each with its path, mode, uid, gid and content digest, canonically encoded and sorted), and **when it becomes final** (at the end of the deploy step, invariant until the next deployment, which forces a rotation). **§2.13.5a**: **C0** now **computes** the digest and refuses unless the supplied value equals the computed one — so C1 consumes a value validated against the **deployed bytes**, not against a copy of itself — and the supplied string is discarded at C0; **C2** keeps the report-consistency check **and recomputes the manifest digest a second time**, which is what detects a deployment changed between C0 and the probe's capture. The universal *produced < validated ≤ consumed* claim is **withdrawn** and replaced by five invariants **I-1 … I-5** distinguishing **pre-consumption validation of external inputs** from **post-production consistency checking of internally produced values**; the value table gains a **class** column and the graph gains the `[computed & compared, C0]` gate. **`JNL-46` grows from one case to five**: the ordered walk, a malformed supplied digest, a wrong supplied digest, a deployment changed between C0 and C1, and a report whose field differs from the validated input — each refusing before **C5** and creating **no generation artifact** |
| **R8-B** — *give cleanup failure one possible, recoverable outcome* | **New §2.13.2b**, one explicit state machine with three states: **S-A** probe-stage failure with cleanup succeeding — no transient residue and no generation or database artifact; **S-B** cleanup failure — **no** generation or database artifact, but the exact remaining residue reported by absolute path with its operation and `errno`; and **S-C** success. For the next invocation the design specifies **one** behaviour: **`verify-capability` and `init-generation` C0 refuse for operator recovery**, and revision 8's *"reports it, cleans it as an explicit first step, and records that it did"* is **withdrawn** — residue is never silently reused **and never automatically cleaned**. Recovery is a named operator procedure in the WP-9 operations document, not a command this design offers. `JNL-30`, `JNL-47`, `JNL-48`, **C0**/**C1**/**C2**, §2.13.4's transient row, §2.13.7's lifecycle table, the failure-cost paragraph, WP-8, WP-15, WP-9 and logical schema §4.3.8/§9 are reconciled: **“no generation artifact” remains unconditional; “no transient residue” is conditional on cleanup success.** **`JNL-47` grows from five cases to six** — one per probe stage with cleanup succeeding, plus cleanup failure after a probe-stage failure and cleanup failure after a fully passing probe — each asserting exit status, safe path reporting, generation and database absence, residue state, next-run behaviour and recovery |
| **R8-C** — *separate immutable-flag authority from DAC authority* | **§2.13.5c, rewritten again.** The eight-capability register is **withdrawn**, because it treated `CAP_LINUX_IMMUTABLE` as if it bypassed Unix DAC. In its place: **nine independently constructible authorities** — **A1** flag control, **A2** DAC on the journal *file*, **A3** DAC on `…/journal` and the seal within it, **A4** DAC on `…/archive` and its files, **A5** DAC on the deployment path, **A6** host identity and restoration control, **A7** full host-root identity (a composite, listed because it is how the others are acquired in practice), **A8** coordinator authentication and insertion, **A9** PostgreSQL mutation. Every F-row states the **minimum combination**, detector reach, the independent refusing actor or artifact, the exact step and code, and the residual. **F-2 becomes `A1 + A2`** — the writer already owns the journal file, so the flag is the whole of what refuses it; **F-4 becomes `A1 + A4`** — clearing `+i` on an archived file leaves `EACCES` on the open; **F-5 becomes `A1 + A3`** — an `+a` victim cannot be unlinked or renamed over until the flag is cleared. An *achieved ability* such as “archive write” is separated throughout from the Linux privileges needed to achieve it. `JNL-49` and `JNL-50` grow to **ten cases each**, and the new cases are executed under a **flag-control-only, non-root capability set** that proves `CAP_LINUX_IMMUTABLE` does not confer DAC |
| **R8-D** — *correct or withdraw F-7's host-identity refusal* | **Withdrawn and reclassified, not re-worded.** If **A6** rewrites `/etc/machine-id` to the recorded value, `SB.host_machine_id`, `/etc/machine-id` and the registered row all carry the **same** value, so **W10 passes and C-d has nothing to disagree with**. Storage outside the restored tree creates no mismatch, and changed device/inode values are **incidental** — a restore that changes them is refused as **F-5**/**F-10**/**F-11** by a *named* field, and a restore that preserves them is not detected at all. Revision 9 takes the honest classification: a forged matching host identity is a **residual**, **R-5.0-13**, and the independent operational evidence that remains is named — the production PostgreSQL the restored tree does not carry, `sudo log_output`, journald, `audit_events`, and the absence of a `seal` record, `.close` manifest and archive behind a forged head. **F-7**, **A6**, §2.13.5b's verifier table, §2.13.5c's bounded claims, §2.13.6 **J-23**, `JNL-40` (now two cases), `JNL-49` case 3, logical schema §3.7's `host_machine_id` rule, §3.7.1 and §9 are all corrected. The second option — a genuinely independent authenticated host-bound value — is **routed** as D5.0-13 / OD-66 **option A-2** with its authority, provisioning, rotation, backup/restore and verification named, and is **not adopted** |
| Consequence — the falsification count | **Unchanged at thirteen** — F-1a, F-1b and F-2 … F-12. R8-C re-evaluates rows and R8-D reclassifies one outcome; neither adds nor removes a row |
| Consequence — the state table | **§2.13.6 stays at twenty-five rows**, and refusal codes stay `SW-J01 … SW-J25`. **J-23**'s *description* is narrowed to the unforged mismatch it actually detects; no condition is added, because R8-D **removes** a claimed detection rather than adding one, and C0/C2 refusals are `init-generation` exits rather than writer or coordinator conditions |
| Consequence — the evidence band | `TC-5.0-JNL` stays at **fifty identifiers** and grows from seventy-four cases to **eighty-four**: `JNL-46` 1 → **5**, `JNL-47` 5 → **6**, `JNL-49` 8 → **10**, `JNL-50` 8 → **10**, `JNL-40` 1 → **2**. **No identifier is added**, because every R8 correction is either a change to an existing case's contract or an added case under an existing identifier. `JNL-30` and `JNL-48` change contract without changing case count. §6.5 grows from eighteen items to **nineteen** |
| Consequence — the schema | **None to the tables.** No column, constraint, index, trigger, sequence, vocabulary, table, command or health check changes. `append_only_probe_version` still reads `jnl-probe-1`; what that value denotes gains a **pre-consumption digest validation** and a **cleanup state machine**, which are changes to the procedure the closed vocabulary names and not to the vocabulary. Logical schema §3.7's `host_machine_id` and `writer_deployment_digest` notes, §3.7.1's enforce/record division, §4.3.8's Band 3 and §9's traceability are corrected in wording and case counts, and §9 gains **two** rows |
| Consequence — estimate and controls | PERT **40.4** implementer-days, up from 39.5, decomposed in §4: WP-8 **+0.53**, WP-15 **+0.20**, WP-9 **+0.12**, WP-4b **+0.08**; every other package unchanged. Remediation allowance **11.9**; contingency 4.0. Security review rises to **3.0–4.0** reviewer-days — the register is now nine authorities whose **combinations** must each be checked against real DAC, and there are now **two** residuals — with **eleven** surfaces unchanged and **two added reviewer questions**. New stop condition **10l**; **10b**, **10f** and **10h** extended and **10j** re-worded to the invariants that replace the withdrawn inequality. **No new numeric control** — the register stays at nine |
| Consequence — the residuals | **R-5.0-13, new** — a forged matching `/etc/machine-id` is detected by nothing in this design. **R-5.0-14, new** — a failed privileged cleanup leaves a writer-writable transient directory in the state hierarchy until an operator acts, and blocks generation creation while it is there. **R-5.0-12 is retained unchanged.** §7.1 gains rows **25** and **26** |
| **P5.0-R1**, **P5.0-R4** | **Unchanged, and deliberately so.** §2.10's barrier search stands, §2.12's host boundary stands, and **no operational evidence is claimed passed** for either |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |
| Decisions | **No decision number added.** D5.0-13 / OD-66 option A's **content** changes in three places, and a **new option A-2** is raised inside it for the authenticated host binding R8-D routes rather than adopts; D5.0-9 … D5.0-12 are untouched. Nothing here is approved |

### What changed in revision 8 — retained

Revision 8 is a **documentation and design remediation of revision 7's own
claims**, under a handoff that authorizes documentation and design only. Every
row is a defect the re-review named, conceded, and replaced. **No production
code, migration, database object, host artifact or environment state was
touched.**

| Input | Effect on this plan |
|---|---|
| **R7-A** — *make Algorithm C executable in its stated order* | **§2.13.5a.** **C0** now checks only pre-probe preconditions and **reads no probe result**; **C1** runs all four stages and is the single creation point of `PR`; a new **C2** validates the result-dependent facts — all four stages present, every case passed, `writer_deployment_digest` equal to the supplied one, and cleanup complete — **before any persistent artifact exists**; and the algorithm is renumbered **C0 … C13**. A **value-dependency table** states, per value, where it is produced, validated and first consumed, and the dependency graph now carries the `[validated, C2]` gate on the only path out of `PR`. `verify-capability` and `init-generation`'s preconditions in §2.13.7 are split by *when they can be known*; `rotate` no longer lists a separate `verify-capability` step, which would have been a second probe invocation. **`JNL-46`** walks the order and proves every consumed value exists, is final and is validated before use; **`JNL-47`** injects a failure in each of Stage 1 … Stage 4 and cleanup and proves that **no journal, seal, symlink or registration row is created**. Every reference to C1 … C12 in both documents is renumbered |
| **R7-B** — *give S4-2 an exact positive DAC control* | **§2.13.2a.** The exact target is **`…/probe-ro/s4-2.target`**, in a second transient directory `root:freedomsheet 0770` on the same mount, inside `ProtectSystem=strict`'s read-only tree and **outside** the substituted `ReadWritePaths=` — which is why it is a sibling of the arena rather than a path inside it. New case **`S4-0`** proves, under the writer's uid through `setpriv` and **outside any unit**, that open, append, `fsync`, `rename` and — on an identically created sibling — `unlink` are permitted by DAC on that exact file. Only then is `EROFS` accepted for **S4-2**: `EACCES` is **`inconclusive`**, and success is a **failed** stage. Stage 4's cases become **`S4-0 … S4-3`**; the canonical probe bytes in **C1** carry them and the target path and its `st_dev`; the attribution table gains three rows separating `EROFS` with a passing control, `EROFS` without one, and S4-2 succeeding; §2.13.3 gains a `…/probe-ro` row; §2.13.4's arena row covers both directories; the `finally` cleanup, the residue report and the **C0** refusal cover both; and **`JNL-48`** produces and distinguishes the four outcomes the handoff enumerates |
| **R7-C** — *replace the attacker-class matrix with capability-correct cases* | **§2.13.5c, rewritten.** The two-class model and every *"reaches every row except"* claim are **withdrawn**. A register of **eight independent capabilities** — `K1` seal write, `K2` journal-directory write, `K3` journal-content rewrite needing `CAP_LINUX_IMMUTABLE`, `K4` archive write/attribute control, `K5` deployment-path write, `K6` host identity/restoration control, `K7` coordinator execution/authentication, `K8` PostgreSQL row mutation or insertion — states for each what it is, who can hold it, what it also confers and what it does not. Every F-row now gives the **minimum capability**, whether that capability **also reaches the detector**, the **independent actor or artifact** that refuses it, the **exact step and code**, and the **residual when the attacker holds both**. **F-2 is corrected from class 1 to `K3`**; **F-7 is corrected in the opposite direction**, because `/etc/machine-id` is root-writable; F-3 … F-12 are re-evaluated. The identity boundary is stated: `CAP_LINUX_IMMUTABLE` **alone**, full root, and a PostgreSQL superuser are three distinct authorities, not a ladder. Not-constructible pairings are marked **with the control that makes them so**, and `JNL-49`/`JNL-50` give one case per feasible pairing, the three combined-authority residuals, and an executed assertion per not-constructible cell |
| **R7-D** — *keep the controlled active-handoff reference current* | **Implementation-plan §20**'s correction to revision 7 / R7 is **preserved** and extended to name revision 8 as the submitted response; status, RAID, the decision register, open decisions and the change log all name **R7** as the active cycle and revision 8 as what is returned against it |
| Consequence — the falsification count | **Corrected.** Revision 7 described §2.13.5c as *"twelve falsification rows"* while listing **thirteen** — F-1a, F-1b and F-2 … F-12. The count is corrected here, in WP-8, in §6.5 item 16 and in logical schema §9 |
| Consequence — the state table | **§2.13.6 stays at twenty-five rows**, and refusal codes stay `SW-J01 … SW-J25`. **J-25** already covers a probe report that is absent, altered, unsupported or not a pass, which is what a failing **S4-0** produces; no new condition and no new code is needed |
| Consequence — the evidence band | `TC-5.0-JNL` grows from forty-five identifiers to **fifty**, and from forty-eight cases to **seventy-four**. `JNL-46` (construction order), `JNL-47` (five construction failure injections), `JNL-48` (four S4-0/S4-2 outcomes), `JNL-49` (eight capability pairings and residuals) and `JNL-50` (eight not-constructible cells) are added; `JNL-29` gains the S4-0 assertions and the S4-0-before-S4-2 ordering. §6.5 grows from seventeen items to **eighteen** |
| Consequence — the schema | **None to the tables.** No column, constraint, index, trigger, sequence, vocabulary, table, command or health check changes. `append_only_probe_version` still reads `jnl-probe-1`; what that value denotes gains a fourth-stage control case, which is a change to the procedure the closed vocabulary names and not to the vocabulary. Logical schema §3.7's `append_only_probe_digest` note, §3.7.1's sandbox row, §4.3.8's Band 3 and §9's traceability are corrected in wording and case counts only |
| Consequence — estimate and controls | PERT **39.5** implementer-days, up from 38.2, decomposed in §4: WP-8 **+0.87**, WP-15 **+0.30**, WP-9 **+0.10**; every other package unchanged. Remediation allowance **11.5**; contingency 4.0; security review unchanged at **2.5–3.5** reviewer-days, with **one added surface element** (`…/probe-ro`) and **two added reviewer questions**. New stop conditions **10i**, **10j** and **10k**; new §7.1 risk row **24** and RAID row **R-5.0-12**. **No new numeric control** — the register stays at nine |
| Consequence — the residual that is new, and is not a control | **R-5.0-12.** An attacker holding `CAP_LINUX_IMMUTABLE`-bearing root **and** PostgreSQL superuser authority writes both copies the design compares, so **no check in this design refuses it**. Revision 8 records that as a residual for the Acceptance Authority, with what actually remains — `sudo log_output`, journald, the `audit_events` chain, offline backups, and a forged head with no `seal` record, `.close` manifest or archive — rather than describing a refusal that does not exist. `JNL-49` case 7 asserts the limit |
| **P5.0-R1**, **P5.0-R4** | **Unchanged, and deliberately so.** §2.10's barrier search stands, §2.12's host boundary stands, and **no operational evidence is claimed passed** for either |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |
| Decisions | **No decision number added.** D5.0-13 / OD-66 option A's **content** changes again — `…/probe-ro` with its control, and Algorithm C's validation step — and is re-stated in §5.3; D5.0-9 … D5.0-12 are untouched. Nothing here is approved |

### What changed in revision 7 — retained

Revision 7 is a **documentation and design remediation of revision 6's own
claims**, under a handoff that authorizes documentation and design only. Every
row is a defect the re-review named, conceded, and replaced. **No production
code, migration, database object, host artifact or environment state was
touched.**

| Input | Effect on this plan |
|---|---|
| **R6-A** — *reconcile the probe report lifecycle* | **§2.13.2a.** Stage 4 moves from deployment to **provisioning**, inside the same `verify-capability` invocation and **before** the report is built, so `append_only_probe_digest` covers the four stages it is said to cover. Its cases are named **`S4-1 … S4-3`**: an append inside the substituted `ReadWritePaths=`, an append outside it refused `EROFS`, and a `systemctl show` capture whose applied directive set is hashed and compared with the deployed unit — a mismatch is **`inconclusive`**. `verify-capability` gains two preconditions (the unit file deployed, the deployment digest supplied) and Algorithm C **C0** refuses unless the report's `writer_deployment_digest` equals the one it was given. **Invalidation reuses the existing rule** — redeployment forces a rotation (**J-22**, **F-6**) — so no second invalidation rule, artifact, digest, authority or refusal code exists. *(Superseded 2026-09-23 as to the invalidation rule only, pending review: C-P5.0-R5-R1/R2 add a second invalidation condition — a systemd or package identity change, enforced at W4/C-a under J-25 — with no second artifact or refusal-code family; see §2.13.2a.)* The re-review's **option 2** is priced and rejected in the same table, with its own requirement — *how does the writer authenticate deployment evidence without PostgreSQL?* — given as the reason |
| **R6-B** — *make the whole-seal claim true or narrow it* | **Both, because one alone would have left something false.** **§2.13.5a**: `BND.sealed_at` and `BND`'s own format field are **withdrawn**; the binding holds exactly `genesis_record_digest`, `journal_device` and `journal_inode`, encoded at a **`binding_format_version` carried in the chain-authenticated body**, and the seal file's length is exactly `len(SB) + len(BND)`. **§2.13.5b** adds a field-by-field table naming the **V-W** step that recomputes or compares each, plus the one-row statement for the body (`W13` against record 0). **§2.13.5c** splits **F-1** into **F-1a** — refused by the writer with no database — and **F-1b** — a `CAP_LINUX_IMMUTABLE` holder rewriting the seal *and* record 0 consistently, refused **only** by the coordinator against PostgreSQL — and adds **F-9 … F-12** for `genesis_record_digest`, device, inode and a planted `sealed_at`. Two **attacker classes** are stated, and *"each half fails closed alone"* is reconciled to what each half covers. **`chattr +i` is not the answer**, and the section says why |
| **R6-C** — *correct `JNL-32` everywhere* | **§2.13.8.** `JNL-32a` — `+a` present, the start reaches **W18**, W17 is the only write and appends exactly one `startup` record, seal and archive unchanged. `JNL-32b` — `+a` absent, the start refuses at **W9** with `SW-J06` **before W17**, no write-mode journal open at all, no `startup` record, journal, seal and archive **byte-for-byte unchanged**. Corrected in the same terms in WP-4b, §6.5 item 15, logical schema §9 and every traceability row |
| **R6-D** — *preserve a valid review record* | **`phase-5-0-remediation-r6-handback.md`**, complete Markdown, `git diff --check` clean, replacing the corrupt R5 handback, which stays in Git history only |
| **R6-E** — *correct cross-reference defects* | **§2.13.5a C1**: *"written in C4"* is corrected — C4 writes the genesis record, and the report reaches disk only inside the seal body at **C8**. **§2.13.2a**: `M-1` and `M-2` are **defined** as Stage 3's two named cases, and `S4-1 … S4-3` as Stage 4's, so every case a canonical artifact names has one definition |
| Consequence — the state table | **§2.13.6 stays at twenty-five rows.** **J-24** widens to cover an unsupported binding version, a short binding, and any byte after the binding — including a planted `sealed_at`. No refusal code is added; the family stays `SW-J01 … SW-J25` |
| Consequence — the evidence band | `TC-5.0-JNL` grows from forty-one identifiers to **forty-five**, and from forty-two cases to **forty-eight**. `JNL-32` and `JNL-34` split; `JNL-42 … 45` cover the binding fields and the planted field; `JNL-29` gains the four-stage and digest-coverage assertions. §6.5 grows from sixteen items to **seventeen** |
| Consequence — the schema | **None to the tables.** `sealed_at` was never a database column; no column, constraint, trigger, index, command or health check changes. Logical schema §3.7's column notes, §3.7.1's division, §4.3.8's Band 3 and §9's traceability are corrected in wording and case counts only |
| Consequence — estimate and controls | PERT **38.2** implementer-days, up from 37.7, decomposed in §4: WP-8 **+0.4**, WP-15 **+0.1**, WP-4b **+0.05**; every other package unchanged. Remediation allowance **11.1**; contingency 4.0; security review unchanged at **2.5–3.5** reviewer-days, with **one added surface element** (Stage 4's transient root-started unit) and **one added reviewer question**. New stop condition **10h**. **No new numeric control** — the register stays at nine |
| **P5.0-R1**, **P5.0-R4** | **Unchanged, and deliberately so.** §2.10's barrier search stands, §2.12's host boundary stands, and **no operational evidence is claimed passed** for either |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |
| Decisions | **No decision number added.** D5.0-13 / OD-66 option A's **content** changes again and is re-stated in §5.3; D5.0-9 … D5.0-12 are untouched. Nothing here is approved |

### What changed in revision 6 — retained

Revision 6 is a **remediation of revision 5's own contract**, not of an external
limit. Every row below is a defect the re-review named, conceded, and replaced.

| Input | Effect on this plan |
|---|---|
| **R5-A** — *replace the circular cryptographic construction* | **New §2.13.5a.** The seal is split into a **body** (fixed before the journal exists) and a **binding section** (fixed after). The genesis record's `prev_hash` becomes **`seal_body_digest`**, not `seal_digest`, and its whole content is a pure function of the seal body — so any holder of the seal can *derive* the genesis digest instead of trusting it. `seal_digest` is a **leaf**: no on-disk artifact contains it. **Algorithm C** gives twelve ordered steps naming the exact canonical bytes, the excluded fields, the actor, the artifact that already exists, and the placement of every `fsync`, `rename`, `+a` and `+i`; a dependency graph makes the acyclicity checkable; the first-generation/successor difference is a table; and the disk-versus-PostgreSQL comparison is one-directional, because **nothing on disk depends on a database value**. **New §2.13.5b** gives verification algorithms **V-W** (writer), **V-C** (coordinator) and **V-R** (registration), and **new §2.13.5c** gives the eight-case falsification matrix the handoff enumerates |
| **R5-B** — *align permissions with validation responsibilities* | **§2.13.3**: a third system group **`freedomjournal`** holds exactly `freedomcoord` and `freedomsheet`; `…/journal` becomes **`root:freedomjournal 0750`** and the seal **`root:freedomjournal 0440`**, `chattr +i` — the handoff's first permitted contract, *grant the minimum read-only access to a non-sensitive seal*, made minimal rather than made world-readable. The obvious edit — a `0444` seal under the old `0751` directory — is rejected in the same paragraph, because it would have been readable by `discordbot` and `freedomweb` too. **Every identity that is neither the writer nor the coordinator loses the traverse revision 5 gave it.** The reason the second option was not taken is stated: the genesis, inode, ownership and mode checks must happen **before the writer appends**, in a process with no database and no human. **§2.13.5b** divides the checks explicitly and states what each verifier cannot establish. §2.13.4 gains three rows and changes one: **read the seal — permitted; modify, replace, unlink or rename it — refused**, with the mechanism and `errno` for each. The disclosure is assessed rather than asserted, and raised as security-review **surface 11** (§9.2) rather than settled by the implementer. **The writer remains unable to modify, replace, rotate, seal, archive or dispose of evidence** |
| **R5-C** — *make the append-only capability probe valid and safe* | **New §2.13.2a.** Four stages in a disposable **arena** — `…/probe`, `root:freedomsheet 0770`, holding files the tested identity **owns** at `0600` — so that discretionary permissions are never the reason for a refusal. **Stage 1 is a control stage**: the same six operations must *succeed* without `+a`, or the result is **`inconclusive`**, never `passed`. Stage 2 asserts nine cases with their expected `errno`, including `pwrite`-on-`O_APPEND`, which is deliberately **not** a refusal. Stage 3 attributes the storage; Stage 4 attributes the systemd sandbox. An **attribution table** separates `EACCES` (DAC), `EROFS` (read-only mount or sandbox), `EPERM` with `FS_APPEND_FL` present (append-only) and `ENOTTY` (no flag interface). **Startup performs no destructive operation against live evidence** — §2.13.5b **V-W** is read-only apart from one appended `startup` record — and privileged cleanup runs in a `finally`, reports residue, and exits non-zero if it fails |
| **R5-D** — *correct the database-evidence claim* | **New §2.13.8a**, and the column `append_only_verified` with its `CHECK` is **withdrawn**. The probe report now lives **inside the seal body**, covered by `seal_body_digest`, the genesis anchor and `chattr +i`; the registered row carries `append_only_probe_version`, `append_only_probe_digest` and `append_only_probe_at`. §2.13.8a names the authenticated actor, the immutable fields, the binding to the exact generation/filesystem/probe version, and gives a line-by-line table of **what PostgreSQL enforces versus what it merely records**. The honest statement is written down: **no database constraint can observe a host**; what establishes that the probe ran is the seal, `sudo log_output`, journald, `audit_events` and `archive-verify`. **The writer still opens no database connection** |
| Consequence — the state table | §2.13.6 grows from twenty-one rows to **twenty-five**. **J-22** (writer deployment digest mismatch), **J-23** (host identity mismatch), **J-24** (the seal's structure or genesis derivation fails) and **J-25** (the probe report absent, altered, unsupported or not a pass) are checks the writer could not previously perform, because it could not read the seal. Refusal codes become `SW-J01 … SW-J25` |
| Consequence — the evidence band | `TC-5.0-JNL` grows from twenty-six cases to **forty-one**. `JNL-27` … `JNL-30` cover the probe's control stage, refusal attribution, sandbox attribution and privileged cleanup; `JNL-31` proves the construction is acyclic by re-deriving the genesis record with an independent implementation; `JNL-32` proves startup is non-destructive **by syscall trace, including with `+a` absent**; `JNL-33` proves the writer's seal access is exactly *read*; `JNL-34 … 41` are the eight falsification cases. §6.5 grows from fourteen items to **sixteen** |
| Consequence — the schema | The sixth table's columns change (logical schema §3.7): `append_only_verified` **withdrawn**; `seal_body_digest`, `append_only_probe_version`, `append_only_probe_digest` and `append_only_probe_at` added. The activation trigger's fifth condition, the three evidence columns and the fifth command are **unchanged** |
| Consequence — estimate and controls | PERT **37.7** implementer-days, up from 35.5, decomposed in §4. WP-15, WP-4b, WP-8, WP-6, WP-2 and WP-9 grow; **no new work package**. Remediation allowance **11.0**; contingency 4.0; security review raised to **2.5–3.5** reviewer-days. **No new numeric control**: the register stays at nine, N5.0-21 … N5.0-23 unchanged. New stop conditions **10f** and **10g**; 10b and 10d extended. Security-review surfaces grow from ten to **eleven**, with two added reviewer questions |
| **P5.0-R1**, **P5.0-R4** | **Unchanged, and deliberately so.** §2.10's barrier search stands, §2.12's host boundary stands, and **no operational evidence is claimed passed** for either |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged**, and stated as such in logical schema §2.1, §2.5 and §11 |

### What changed in revision 5 — retained

| Input | Effect on this plan |
|---|---|
| **P5.0-R5 item 1** — *use a durable filesystem, not `/run`* | **§2.13** replaces the one-line journal specification with a storage contract. The journal moves to **`/var/lib/freedom-sheet-writer/journal/`**, whose filesystem was **read** on 2026-08-29 rather than inferred: `/run` is `tmpfs` and `/var/lib` is the same `ext4` volume as `/opt/freedom-blades` (§8.1, rows **H-4** and **H-5**). **Revision 6 preserves this direction**, as the R5 handoff requires |
| **P5.0-R5 item 2** — *owner, group, mode, filesystem, authorities, and protection against unlink, rename, replacement, truncation and parent manipulation* | **§2.13.3** gives the full hierarchy and **§2.13.4** the manipulation matrix. The load-bearing change: **the writer has no write permission on the directory holding its journal**, so it cannot create, unlink, rename, link or replace anything there; `chattr +a` is a *second, independent* layer over that rather than the only one. `StateDirectory=` is deliberately **not** used, because it would make systemd create the directory owned by the writer |
| **P5.0-R5 item 3** — *a durable generation bound to the writer deployment and the cutover observation* | **§2.13.5**: a generation is a root-created, `chattr +i` **sealed** identity carrying the writer unit, the deployed writer's digest, the host machine id and the journal's `(device, inode)`. It must be **registered in PostgreSQL** before the writer may run on it — the sixth table (logical schema §3.7) — and the activation trigger refuses evidence that does not name the current registered generation. **A new or reset journal is therefore never indistinguishable from a valid empty history**, for three independent reasons |
| **P5.0-R5 item 4** — *startup and recovery behaviour for every named condition* | **§2.13.6**, a state table in which every row names how the condition is detected, what the **writer** does (refuse new Sheet mutations) and what the **coordinator** does (refuse `dispatch_journal_clear`, so the activation trigger refuses). **No row resolves to "continue"** |
| **P5.0-R5 item 5** — *privileged sealing, rotation, archival, retention, clearing and disposal* | **§2.13.7** specifies `freedom-journal-admin`, a second root-owned wrapper under its own `sudoers` `Cmnd_Alias`. The writer cannot seal, rotate, clear or dispose, and **cannot erase or replace evidence it authored** (§2.13.4). Revision 4's *"clearing it needs `CAP_LINUX_IMMUTABLE`"* is withdrawn as a specification |
| **P5.0-R5 item 6** — *state what completeness establishes; remove the contradiction* | **§2.13.9.** The statement *"nothing in the fence depends on the journal being complete"* is **withdrawn as false** and `dispatch_journal_clear` is **kept** as a required method, with a one-direction dependency and a named residual, **R-5.0-10** |
| **P5.0-R5 item 7** — *keep the Google residual separate* | **§2.13.10**, and §2.10.2 is unchanged. **A durable journal is not a barrier**, is not offered as one, and does not narrow **R-5.0-8** by a single case |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged** |
| Revision 4's *"no table is added"* claim | **Superseded.** A trigger cannot refuse what the database does not know. **The property that mattered is preserved**: the writer still never reads or writes PostgreSQL, so the legacy mutation path still takes **no** database dependency |

### What changed in revision 4 — retained

| Input | Effect on this plan |
|---|---|
| **R3-A** — *prove the Sheet boundary or reject it* | **§2.10 Part B is rewritten as a barrier search.** Thirteen candidate barriers are traced against the published Google surface and each is answered; the seven cases the handoff enumerates are answered in one table. **The conclusion is the handoff's option 2:** no externally verifiable barrier proving accepted-request completion exists in the published Sheets v4 / Drive v3 surface. §2.10 therefore names the invariant that cannot be guaranteed (**I-SHEET-COMPLETE**), the six weaker guarantees that can (**W-1 … W-6**), and returns a newly priced choice as **D5.0-9 / OD-62, reframed a third time**. The fence ordering changes — **drain, then terminate, then revoke** — and the writer gains an explicit request timeout and a host-local dispatch journal. §7.1, §7.2, §8.3 and §6.5 follow |
| **R3-B** — *bind peer authentication to an isolated OS identity* | **New §2.12** specifies the dedicated coordinator OS user and group, the exact `pg_hba.conf` ordering and `pg_ident.conf` map, the sudo execution boundary, the root-owned deployment path, ownership and modes for every artifact, a per-vector argument that no service process can become the coordinator, and provisioning/audit/revocation/recovery/rotation. Logical schema §4.3 carries the full grant and authentication matrix and the host-boundary evidence plan. **Three host observations made on 2026-08-29 are recorded rather than assumed away** (§8.1): the repository tree is group-writable by the bot's OS identity, `freedom-bot.service.tmpl` carries no hardening directives, and the PostgreSQL socket directory is reachable by every local identity |
| Consequence of R3-B | The design needs **two new OS identities**, a root-owned deployment path outside `/opt/freedom-blades/platform`, a `sudoers` drop-in, `pg_hba`/`pg_ident` lines and hardening on a live unit. That is an accepted-topology change, so **D5.0-11 / OD-64 is extended** and **D5.0-12 / OD-65 is raised**; neither is adopted here. New work package **WP-14** |
| Consequence of R3-A | Two numeric controls are **reframed** and two are **new**, so D5.0-10 / OD-63 grows from four to six. **WP-13 is demoted**: it can inform an operational margin and can no longer close anything. **No table is added** — the dispatch journal is deliberately a host file, not a PostgreSQL table, so the legacy mutation path gains no database dependency |
| Estimate | PERT **29.2** implementer-days, up from 23.7; remediation allowance 8.4; contingency 3.5; security review raised to 1.5–2.5 reviewer-days |
| **P5.0-R2**, **OD-55**, **OD-58** | **Preserved unchanged**, and stated as such in logical schema §2.1, §2.5 and §11 |

### What changed in revision 3 — retained

| Input | Effect on this plan |
|---|---|
| **P5.0-R1** still Blocking — a lease cannot fence an external writer | **§2.10 is rewritten** around the four options the handoff names, each answered against `SIGSTOP`, resume, GC pause, out-of-systemd duplicates, a request past its last check, partial shutdown, failed restart, rollback and operator death. The recommendation changes from *leased self-fencing* to **a lifecycle boundary**: the fence a store gets is the fence that store can enforce. PostgreSQL writes are fenced **inside the transaction**; the Sheet writer is fenced by **termination plus revoked Google write access**. The lease, the renewal, the headroom rule, the drain acknowledgement and the whole clock model are **withdrawn**. **§7.2** and WP-4 are rewritten accordingly |
| **P5.0-R4** new Blocking — shared-role proof ownership | **New §2.11** compares the three ownership designs the handoff names and recommends removing runtime-authored proof entirely, realized through a privileged coordinator principal. Logical schema §4.3 traces who authenticates, which SQL principal PostgreSQL sees, who may write which row, how the credential is provisioned and rotated, and whether a compromised process can falsify another's proof. **The runtime role ends with no write privilege anywhere on the authority plane** |
| The handoff's *"raise the concrete choice for Peter"* | **D5.0-9 / OD-62 is reframed**, not extended. Its old options were priced around the lease and are withdrawn. The new options are priced around outage, topology and production-access cost (§5.3) |
| Consequences | **Five tables instead of six**; six numeric controls withdrawn and four raised; a new decision **D5.0-11 / OD-64** for the database principal; a new work package **WP-13**; risks R-5.0-5 and R-5.0-6 restated; PERT **23.7** implementer-days, up from 20.8 |
| **P5.0-R2**, **OD-55** | **Preserved unchanged**, and stated as such in logical schema §2.1 and §11 so a reviewer can confirm nothing drifted while R1 and R4 were addressed |

---

## 1. Outcome, scope and exclusions

### 1.1 Outcome

The reusable safety controls that must exist **before** the first
database-backed character mutation or field cutover, and that every later Phase 5
package specializes without bypassing its own typed schema, migration,
correction and rule gates:

- one durable, append-only record of **which authority owns each migration unit
  right now** — legacy, shadow, cutover or database — that no process can
  disagree with and no code path can rewrite;
- a **database-enforced authority fence** that refuses any PostgreSQL write to a
  unit whose authority is not PostgreSQL, evaluated inside the writing
  transaction so that no elapsed time, pause or stale snapshot can defeat it;
- the **strongest boundary that is actually available** for the one store
  PostgreSQL cannot fence — the Google Sheet — consisting of a separately
  terminable writer that is drained before it is killed, a **durable, sealed,
  generation-bound, hash-chained dispatch journal** (§2.13) that makes the set of
  unacknowledged requests enumerable and makes every unknown journal state a
  refusal, a fail-closed activation that refuses while that set is non-empty or
  indeterminate, a Google-side write-access revocation that refuses anything the
  host controls missed, and a post-import divergence re-read. **This is explicitly
  not a proof of accepted-request completion**, because §2.10 concludes that no
  such proof exists in the published Google surface and §2.13.10 records that
  durability does not create one; it is a bounded, enumerated and detected
  residual returned to the Product Owner as D5.0-9 / OD-62;
- a complete, written **authority-state matrix** stating for every state which
  store is read-authoritative, which may accept writes, whether comparison reads
  occur, the condition of the legacy path, the valid process configuration, and
  the permitted transitions and their prerequisites;
- an **effective-time model** in which a revision that has been authorized but
  not activated is authority for nothing, so no future-dated change can take
  effect early and no unit can have two current heads;
- an **observed, never attested, quiescence-evidence record**, written by a
  database principal that no application process can authenticate as **because
  a dedicated operating-system identity, an exact peer map and a host privilege
  boundary make the attempt fail in the kernel and in `pg_hba.conf`** (§2.12),
  that the activation is fenced against;
- a **transaction boundary** that commits a durable domain effect, its
  idempotency receipt and its success audit row together, proved against real
  PostgreSQL rather than asserted;
- the shared **idempotency, authorization, audit/correlation and
  optimistic-concurrency conventions**, built on the accepted Phase 4 contracts
  rather than on a second mechanism beside them;
- the common **migration preview/apply, reconciliation, control-total and
  comparison-telemetry conventions**, as a written contract whose first typed
  implementations belong to packages 5.1 and 5.2 with their real consumers;
- the common **cutover, rollback and recovery procedure**, including the fence
  protocol, the rollback data path, and keeping the legacy Freedom bot and Sheet
  path available and undegraded outside the bounded fence windows; and
- **cutover monitoring**, numeric success and rollback thresholds, and a bounded
  verification-window template.

The gate is **first-mutation and cutover control** (plan §12.0, Phase 5 package
table). Test counts do not close it.

### 1.2 In scope, with the concrete consumer of every deliverable

| # | Deliverable | Layer | Concrete package-5.0 consumer |
|---|---|---|---|
| 1 | `domain/migration_authority.py` — the `Authority` states, the legal-transition rule as a value object, the epoch/chain arithmetic, the fence-method vocabulary and the `UnitKey` identity | domain | deliverables 3, 4, 5 and 7 construct and validate every revision, disposition and evidence row through it |
| 2 | Migration `0014`: `migration_units`, `migration_authority_transitions`, `migration_authority_revisions`, `migration_authority_dispositions`, `migration_quiescence_evidence`, **`sheet_writer_journal_generations`** (new in revision 5), the `control_plane_version` and journal-generation sequences, the seed, the **four** append-only triggers, the activation-fence trigger, the evidence-recording trigger, the **authority-fence trigger function**, the coordinator role and the grants | adapter | deliverables 3, 4, 5, 7 and 13 all read or write these |
| 3 | `application/migration_authority.py` — the repository protocols and the **five** commands `AuthorizeAuthorityChange`, `RecordQuiescenceEvidence`, `ActivateAuthorityChange`, `AbandonAuthorityRevision` and **`RegisterJournalGeneration`**, on the Phase 4 `CommandEnvelope`/`CommandReceipt`/`idempotency_keys` contracts | application | the coordinator command (7) is their only caller and exists in this package |
| 4 | **The database authority fence** — the trigger function, installed on package 5.0's own tables and on one synthetic migrating unit, plus the startup authority read and capability refusal in all three services and the additive typed bot settings boundary | adapters + tools | **the deployed processes.** With every unit seeded `legacy` it already refuses every database-path mutation — a live control from day one, enforced by PostgreSQL rather than by application code |
| 5 | **`freedom-sheet-writer`** — the separately terminable process that holds the Google credential and is the only issuer of `values.batchUpdate`, plus its **hardened** systemd unit template, its own OS identity, its IPC boundary, its failure semantics, its **explicit per-request timeout**, its **drain-on-`SIGTERM`** behaviour, its **durable generation-validated dispatch journal client** (§2.13), its typed journal refusal codes, and the bot-side client | adapters + infra | **the Freedom bot.** Its drain and termination are the legacy boundary; today its write surface is already one function (`connectors/sheets.py:31`) called from two sites, so this makes an existing code boundary a process boundary. **Blocked by D5.0-9, D5.0-12 and D5.0-13** |
| 6 | ~~`shadow_comparisons` and its bounded write path~~ | — | **Withdrawn by OD-55.** Package 5.1 owns the table, write path and schema. Package 5.0 retains the written telemetry contract as part of deliverable 9 (§11) |
| 7 | `tools/migration_authority.py` — host-local `preview`, `authorize`, `observe`, `activate`, `abandon`, `status`, `diagnostics` and **`register-journal-generation`**, on the accepted `tools/web_operator.py` pattern, connecting as `freedom_migration_coordinator` | operator surface | the operator; and it is the only writer of deliverable 3's tables, the evidence table and **the journal-generation register** |
| 7b | **The coordinator host boundary** — the dedicated `freedomcoord` OS user and group, the `pg_hba.conf`/`pg_ident.conf` mapping, the `sudoers` drop-in, the root-owned `/opt/freedom-blades/coordinator` deployment path with its ownership and modes, and the provisioning/rotation/revocation procedure (§2.12) | infra + docs | **deliverable 7.** Without it, peer authentication names no identity and P5.0-R4's claim is unproved. **Blocked by D5.0-11** |
| 8 | `/healthz` checks `migration_authority_capability`, `migration_authority_pending` and `migration_sheet_writer` plus the bounded queries behind them | application + web | the monitoring path and the §8.3 thresholds |
| 9 | `docs/contracts/phase-5-migration-and-cutover-contract.md` — preview/apply, the fence protocol, the rollback data path, reconciliation, control totals, the comparison-telemetry contract (§11), the verification-window template and the numeric register | docs | packages 5.1+ specialize it; 5.0's own rehearsal is run against it |
| 10 | `docs/operations/migration-cutover-and-rollback.md` — the cutover, rollback, recovery and Freedom-bot-availability procedure, rehearsed on the disposable database | docs + rehearsal | the Operations Owner, at the 5.0 gate |
| 11 | The Google-access feasibility record — measured propagation and rollback latency for a Drive write-permission change, against a **disposable** spreadsheet and a **disposable** service account. **Demoted in revision 4:** it informs the N5.0-18 operational margin and **closes nothing** (§2.10) | docs + evidence | D5.0-10's N5.0-18 value |
| 12 | Package submission, traceability, RAID, status, change-log and decision-register updates | docs | the gate |
| **13** | **New in revision 5; rebuilt in revision 6; corrected in revisions 7 and 8. The dispatch journal's durable storage and lifecycle** (§2.13) — the root-owned `/var/lib/freedom-sheet-writer` hierarchy with its ownership, modes and filesystem requirement; the **acyclically constructed and executably ordered** (C0 … C13), sealed, registered generation whose **every binding field V-W authenticates** (§2.13.5a, §2.13.5b); the four-stage capability probe **whose four stages all run before the report is sealed and whose every negative case has a positive control on its exact target** (§2.13.2a); the hash-chained record format; the **twenty-five**-state fail-closed contract; and **`freedom-journal-admin`**, the privileged `verify-capability` / `init-generation` / `seal` / `rotate` / `archive-verify` / `dispose` tool with its own `sudoers` entry | infra + tools + docs | **deliverable 5** writes the journal and **deliverable 7** reads it; without this, `dispatch_journal_clear` is the control P5.0-R5 found. **Blocked by D5.0-13** |
| **14** | **New in revision 12; this is remediation R11-A. The reviewed-source provenance contract** (§2.12.5a) — the root-owned bare Git object store and its authenticated refresh; the approved-revision record `APR`; the reviewed deployment map and the hash-pinned dependency lock; `source_manifest_digest()` and `deployed_source_manifest_digest()`; **Algorithm D `D0 … D8`** with the refusal family `DEP-01 … DEP-09`, the closed two-region partition and the rollback at D7/D8; and the provenance record `PVR` | host + tooling | deliverables 2, 3, 5, 7, 7b and 13. It is the input `init-generation` **C0** refuses without, the value the seal body carries, the fact **W11a** re-checks, and the row `V-R`'s `NOT NULL` foreign key requires. **Blocked by D5.0-12** |

**Deliverable 9 is prose, deliberately.** The handover forbids a generic
migration framework without a package-5.0 use case, and 5.0 migrates nothing.
Preview/apply, reconciliation and comparison telemetry become typed code in
packages 5.1 and 5.2, where the first real migration and the first real shadow
consumer need them.

### 1.3 Explicitly out of scope, and binding on this package

- **No legacy field is migrated.** Not one row of the migration register moves
  from `Legacy`. No Sheet value is read, written, reconciled or imported.
- **No generic character-state store**, no key/value table, no JSON operational
  authority, and no ledger table (OD-58).
- **No comparison-telemetry table and no comparison write path** (OD-55).
- **No `/info`, `/xchange`, lifestyle, mining, work, crafting, sales, trades,
  learning, missions or Bastion behavior.** No Phase 5.1+ feature.
- **No Sheet field becomes database-authoritative.** No unit leaves `legacy`
  during this package; 5.0 builds the mechanism and uses it on nothing.
- **No dual writes and no second authority**, at any moment, in any process, in
  any of the four states.
- **No Freedom-bot behavior is weakened, disabled or deleted.** Moving the Sheet
  write surface into its own process changes no command, no output and no rule;
  the availability consequence of the fence windows is raised as **D5.0-9**
  rather than assumed.
- **No production Google access is changed by this package.** The feasibility
  measurement in deliverable 11 uses a disposable spreadsheet and a disposable
  service account. Changing production access is a cutover step under D5.0-9 and
  the Security Reviewer's review, not an implementation step here.
- **No permanent Discord character-mutation interface**, no new web route, no new
  slash command (OD-59).
- **No production deployment**, no service restart, no production database
  contact, no live Discord, Sheets or Foundry contact, no credential change.
- **No real player or snapshot data** in fixtures or anywhere else.
- **The gate is not claimed** from implementation or from green tests.

---

## 2. Current-path inventory

Traced from the code as it stands on 2026-08-29, with the file each claim rests
on. Its purpose is to make *reuse versus replacement* an explicit decision in
every row rather than a default.

### 2.1 Unit of work and transaction boundary

| Fact | Evidence |
|---|---|
| One use case owns one transaction; repositories join it and never commit | ADR 0003; `adapters/database/unit_of_work.py:58` |
| The isolation level is pinned at `READ COMMITTED` on the unit of work, not inherited from the role or cluster | `adapters/database/unit_of_work.py:53` |
| No ORM or driver exception escapes: `TranslatingSession` yields `UniquenessConflict` naming a rule, or `PersistenceError` | `adapters/database/translation.py`, `application/errors.py` |
| `application.repositories.UnitOfWork` carries twelve repositories | `application/repositories.py:196` |
| Phase 4 introduced a **narrower** `LedgerUnitOfWork` — ledger, idempotency, audit — because a service should depend on what it uses | `application/ledger.py` |
| The composite in-memory/PostgreSQL unit of work does **not** claim cross-store atomicity, and says so | `adapters/ledger/in_memory.py` |

**Disposition: reuse, and follow the Phase 4 precedent.** Package 5.0 adds a
narrow `MigrationAuthorityUnitOfWork` — revisions, dispositions, evidence,
journal generations, idempotency, audit — and the matching repositories on
`SqlAlchemyUnitOfWork`. It
adds **no** second unit of work implementation, no second isolation policy and no
second translation layer.

**One addition revision 3 makes explicit:** the authority-fence trigger runs
*inside* whatever transaction the writing service opened, so it composes with the
existing unit of work rather than sitting beside it. A refused write raises a
`PersistenceError` through the existing translation layer, and the service's
transaction rolls back exactly as it does for any other constraint.

### 2.2 Idempotency

| Fact | Evidence |
|---|---|
| `idempotency_keys` is unique on `(scope, key)`; `request_hash` is a 32-byte SHA-256 with a `CHECK`; `status` is a `CHECK`ed vocabulary | live schema; `migrations/versions/0001_database_foundation.py` |
| *"Have I seen this key"* and *"was it the same request"* are answered separately: retry returns the stored receipt, conflicting reuse fails closed | `application/idempotency.py` |
| `canonical_request_hash` is typed, length-delimited and schema-versioned — the P4-R3 remediation | `application/idempotency.py` |
| `admission_id` may be NULL for every scope except the Foundry submission's, by an existing `CHECK` | live schema, `ck_idempotency_keys_submission_names_its_admission` |
| Phase 4 proved retry, conflicting reuse and concurrent callers on this table against real PostgreSQL | `tests/test_p4_idempotent_execution.py` |

**Disposition: reuse unchanged.** Package 5.0 adds four scopes —
`migration.authorize_authority`, `migration.record_quiescence_evidence`,
`migration.activate_authority`, `migration.abandon_revision` and — new in
revision 5 — `migration.register_journal_generation`, and one digest schema.
**No migration to this table, no column, no second idempotency mechanism.**

### 2.3 Audit and correlation

| Fact | Evidence |
|---|---|
| `audit_events` is append-only by trigger **and** by withheld grants; the trigger refuses the schema owner too | live schema, `audit_events_append_only`; `runtime-grants.sql.tmpl` |
| A human capability requires an identified person — a platform account or the historical Discord column | `ck_audit_events_human_action_has_an_attribution`; `application/audit.py` |
| Payloads are frozen recursively and restricted to JSON-safe finite scalars | `application/audit.py` |
| Every payload key written anywhere in the repository must be classified in the audit projection, enforced by a regression test | `application/web/audit_search.py`; `test_every_payload_key_this_repository_writes_is_classified` |
| One attempt has one correlation identity across effect, receipt and audit — the P4-R5 rule | `application/ledger.py` |

**Disposition: reuse unchanged.** Five new actions —
`migration.authority_authorized`, `migration.quiescence_observed`,
`migration.authority_activated`, `migration.revision_abandoned` and, new in
revision 5, `migration.journal_generation_registered` — attributed to
`ActorCapability.PLATFORM_ADMINISTRATOR` with `actor_platform_account_id` set and
`AuditSource.SYSTEM`. Their payload keys must be added to the classified set in
`application/web/audit_search.py` — a code change, **not** a schema change.

### 2.4 Authorization

| Fact | Evidence |
|---|---|
| Authority is resolved at execution through a port, never taken from the request; preview permission is not apply permission | `application/authorization.py` |
| One current Guild Council member is sufficient for Council actions; Platform Administrator is a separate capability (OD-24) | `application/authorization.py`; plan §4 |
| Non-human callers hold enum scopes, never free-text; `ServicePrincipalScope` has exactly one member and widening it is a decision | `application/service_principals.py` |
| Phase 4 added a consumer-owned `LedgerPrincipalPort` rather than widening the accepted Foundry credential vocabulary | `application/ledger.py` |
| Host-local operator commands establish a validated database target **before** connecting, a **named** operator, and no HTTP surface | `tools/web_operator.py:1`, `resolve_engine` |

**Disposition: reuse, and add one database principal.** Changing a migration
authority is a **Platform Administrator** action, not a Council one — it is a
deployment/authority control, not a game-policy decision. The command resolves
the administrator through the accepted `AuthorizationPort` at execution, for the
authorize, observe and activate steps, so an administrator whose capability is
withdrawn between them is refused at the next. **No application scope is widened
and no new service-principal capability is invented** (OD-60).

What is new in revision 3 is one layer below the application: the command
connects to PostgreSQL as `freedom_migration_coordinator` rather than as the
shared runtime role, so *"only the operator may change authority"* becomes a
database fact rather than a code fact (logical schema §4.3). That is a database
role and credential-topology change, raised as **D5.0-11 / OD-64**.

### 2.5 Feature flags and configuration

| Fact | Evidence |
|---|---|
| **No feature-flag mechanism exists anywhere in this repository.** A repository-wide search for `feature_flag`, `FEATURE_`, `FeatureFlag` returns nothing | verified 2026-08-29 |
| The bot's configuration is 47 lines of `os.getenv` plus `sys.exit`, with no typed settings object and no refusal vocabulary | `config.py` |
| The web application's configuration is the opposite: a frozen dataclass tree, built once, collecting **every** problem, echoing **no** value, with fifteen identified startup refusals `S-01…S-15` | `application/web/config.py` |
| Ceilings, not defaults: configuration may make the platform stricter than an accepted policy value and never looser | `application/web/config.py` |
| `WORKER_ENABLED` is the one existing behavioural switch, and its two-process asymmetry is documented in `.env.example` | `.env.example:304` |

**Disposition: build, on the accepted web pattern; and take authority out of
configuration entirely.** No process has a per-unit authority environment
variable, and none is added to `.env.example`. Authority is read from the
database at start and enforced by the database at every write.

Two consequences remain worth a reviewer's attention:

1. **A per-process environment variable cannot prevent split brain, and neither
   can a startup check.** Three processes read three environment files, and a
   check that runs once at startup says nothing about the next four hours. In
   revision 2 the answer to this was a lease. In revision 3 the answer is that
   the *startup check is not load-bearing at all*: it exists so a process that
   cannot serve a unit's authority refuses to start, and the actual fence is in
   the database and in the writer's lifecycle. A startup check that is wrong
   costs a refused start, not a dual write.
2. **The bot's configuration module is not fit to carry a refusal.** `config.py`
   calls `sys.exit` with a bare string. The bot must refuse startup with an
   identified refusal code, so a small typed settings boundary for the bot is in
   scope — **additive, beside `config.py`, changing no existing variable and no
   existing behaviour**. Rewriting `config.py` is not in scope.

### 2.6 Migration tooling

| Fact | Evidence |
|---|---|
| Alembic, thirteen committed revisions, head `0013`; an applied migration is never edited | `migrations/versions/`; ADR 0003 |
| The migration entry point validates its connection target and refuses anything but a Unix-domain socket | `adapters/database/config.py`, `adapters/database/safety.py` |
| Migration `0013` establishes the precedent for a downgrade that **refuses** rather than silently destroying committed effects (dependency D-09) | `migrations/versions/0013_effect_publication_recovery.py:341` |
| `reject_history_mutation()` already exists and is the accepted append-only mechanism | `migrations/versions/0002_foundry_snapshot_and_identity.py:185` |
| Held-lock, round-trip and restored-backup migration evidence already exists as a pattern (findings I-18 … I-21) | Phase 3 review record |

**Disposition: reuse. One additive revision `0014`.** Its downgrade follows the
`0013` precedent and refuses once any unit has left genesis (logical schema §6).

### 2.7 Backup, restore and recovery

| Fact | Evidence |
|---|---|
| A full dump → checksum → destroy → restore → inventory-compare drill exists and refuses production outright, and staging without two independent signals | `infra/postgresql/backup-restore-drill.sh` |
| It validates the *server*, not the name: `PGHOSTADDR` refused, `PGHOST` only as a socket directory, and both server addresses required to be NULL | same |
| Restore evidence, not backup-success messages, is the plan's requirement | plan §14.3 |
| Operational recovery procedures live in `docs/operations/` | `database-development.md` and others |

**Disposition: reuse the drill unchanged; add one operations document.** A
restore can silently return a unit to an earlier authority, so the operations
document opens with an authority `status` check before any service is started
(logical schema §6; risk R-5.0-3).

### 2.8 Deployment boundary

| Fact | Evidence |
|---|---|
| Three systemd units — `freedom-bot`, `freedom-web`, `freedom-worker` — all currently active on this host | `infra/systemd/`; verified 2026-08-29 |
| `freedom-bot.service.tmpl` is `Type=simple`, `Restart=on-failure`, with no `KillSignal` or `TimeoutStopSec` override, so `systemctl stop` sends `SIGTERM` and escalates to `SIGKILL` at the default `DefaultTimeoutStopSec` | `infra/systemd/freedom-bot.service.tmpl` |
| The other two units set `TimeoutStopSec=30` and `KillSignal=SIGTERM` explicitly, so a stop that overruns is a documented escalation rather than a hang | `freedom-web.service.tmpl`, `freedom-worker.service.tmpl` |
| systemd places each unit's processes in its own cgroup and stops the whole cgroup, which is what makes an *empty-set* termination proof possible | systemd unit semantics; used by evidence method `cgroup_empty` |
| Migrations run as the schema owner, invoked by the deployment; the application connects as a restricted role with no `CREATE` | ADR 0003; `runtime-grants.sql.tmpl` |
| The portal refuses to start if it cannot read `alembic_version` over the runtime connection (S-14) | `runtime-grants.sql.tmpl`; `application/web/startup.py` |
| `/healthz` reports named checks and pass/fail only — no connection string, host, credential, player count or queue content | `application/web/startup.py:237` |
| A ten-step deployment gate is defined | plan §14.2 |

**Disposition: reuse, and add one unit.** Package 5.0 adds **four** `/healthz`
checks, one migration and — under D5.0-9 — a fourth systemd unit,
`freedom-sheet-writer`, to the existing deployment sequence. **It does not
deploy.** Its deployment *requirements* are that the writer unit and the fence
build are in place on all services before any unit is authorized out of genesis
(§2.10, partial deployment), and — new in revision 5 — that **the journal
hierarchy is provisioned and a generation is registered before the writer is
started at all** (§2.13.5). A writer with no valid journal refuses to dispatch,
which is the intended failure direction and is stated so the Operations Owner
expects it.

### 2.9 The Google Sheets write surface, traced

This is new in revision 3, and it is the fact the whole R1 remediation rests on.

| Fact | Evidence |
|---|---|
| The repository has **exactly one** Sheet write function | `connectors/sheets.py:31`, `batch_update` |
| It is called from **exactly two** places in production code | `models/actor.py:230`, `models/trade.py:66` |
| A regression test already asserts no import path calls it | `tests/test_sheet_bootstrap_boundary.py:28` |
| The read path is a separate function and a separate adapter, and the identity-migration adapter is read-only by construction | `connectors/sheets.py:22`; `adapters/sheets/read_only.py`; `adapters/sheets/identity_evidence.py:14` |
| Authentication is one Google **service account** from `SERVICE_ACCOUNT_JSON`, scoped to `https://www.googleapis.com/auth/spreadsheets`, against one `GUILD_SHEET_ID` | `connectors/sheets.py:5-8`; `config.py` |
| Sheets API v4 exposes **no** conditional-write precondition — no ETag, no `If-Match`, no revision id, no expected-value guard — on `values.update`, `values.batchUpdate` or `spreadsheets.batchUpdate` | the published API surface; §2.10 option F-9 |
| **The client sets no explicit request timeout.** `build("sheets", "v4", …)` is constructed with no `http` of its own, so the request deadline is whatever the underlying transport defaults to. **The in-flight window is therefore unbounded by anything this repository states**, which is new in revision 4 and is a precondition of any drain being bounded | `connectors/sheets.py:12-19` — read on 2026-08-29 |
| The client requests **no retries** (`num_retries` is not passed), so one call is one dispatch. That is the one thing about the current client that helps: there is no hidden second request to reason about | `connectors/sheets.py:31-39` |

**Disposition: isolate, bound and journal.** Because the write surface is one
function behind two call sites, moving it into its own process is a bounded
change rather than a rewrite, and it converts *"the bot must stop writing"* from
a request the bot has to honour into an event the operating system performs.
Because Google offers no write precondition, the only Google-side enforcement
point that exists is **authorization**, which is why the second control is a
permission change and not a conditional write.

**Two additions revision 4 makes, both forced by R3-A.** The writer sets an
**explicit per-request timeout**, because a drain cannot be bounded while the
request deadline is not; and it writes a **`fsync`-ed dispatch journal** before
each call and again on each response, because the only fact that says anything at
all about an accepted request is *whether its response came back*, and that fact
is worthless if it is not durable. Neither is a fence. Both are what make the
residual **enumerable** instead of unknown (§2.10 Part B).

**What revision 5 corrects about the second of those.** Revision 4 said
*"durable"* and then put the file on `/run`, which on this host is a `tmpfs` that
does not survive a reboot; and it claimed `chattr +a` from the filesystem type of
an unrelated path. **A journal that a reboot silently empties is worse than no
journal**, because an empty unresolved set is the answer that *permits* the
coordinator to record `dispatch_journal_clear`. Revision 5 replaces the
one-line specification with the storage, generation, integrity, lifecycle and
failure contract in **§2.13**, and the facts it rests on were read from this host
rather than inferred (§8.1 **H-4**, **H-5**).

### 2.10 Write-authority fencing — the comparison P5.0-R1 requires, and the barrier that does not exist

The handoff names four options to compare and requires each to be answered
against nine failure cases, with any option rejected that still permits the old
writer to resume after activation.

**The property that must hold.** At no instant may two processes both be
entitled to write a migration unit's authoritative store. Revisions 1 and 2 both
looked for one mechanism that would deliver this for both stores. That was the
error. The two stores differ in the only way that matters — one can refuse a
stale write at the moment it arrives and one cannot — so the fence is split.

**Part A — PostgreSQL-authoritative writes. Settled, and not a decision.**

Every write to a database-authoritative table passes a `BEFORE` trigger that
reads the unit's current activated disposition **in the writing transaction** and
refuses unless it is `cutover` or `database`. This is revision 1's option F-3,
which was correctly called *necessary, not sufficient* when it was expected to
fence the Sheet as well. For a transactional store it is not merely sufficient —
it is complete:

| Failure case | Answer |
|---|---|
| `SIGSTOP` | irrelevant. The check happens at write time, not at admission time |
| Process resume after activation | the resumed transaction re-evaluates against the disposition that is current *now* and is refused. This is the exact counterexample that defeated revision 2, and it does not survive here |
| GC pause | as above |
| Out-of-systemd duplicate | a duplicate holds the same restricted role, so it is refused by the same trigger |
| Request past its last check | there is no "last check": the check and the write are one statement |
| Partial shutdown / failed restart | a process that is down writes nothing; a process that is up is fenced |
| Rollback | `cutover → legacy` makes the trigger refuse database writes from the instant the disposition is inserted |
| Operator death | nothing changed authority, so nothing is unfenced |

No option comparison is offered for Part A because no alternative is competitive:
an application-side check is strictly weaker, and there is no cost to enforcing
it in the database.

**Part B — the Google Sheet.** This is what R3-A reopened, and revision 4
answers it differently from revision 3.

Revision 3 offered a *composite* — terminate the writer, revoke its Google write
access — and called the pair enforceable. The re-review's objection is exact and
it is correct: neither control says anything about a request **Google already
accepted**. Terminating a client does not undo work the server has taken on.
Revoking a permission does not, on any published statement, cancel a request that
was authorized when it arrived. So the composite bounds *new* writes and says
nothing about the last one, and the property the final import needs is precisely
about the last one.

**The property, named once and used throughout.**

> **I-SHEET-COMPLETE.** Every `spreadsheets.values.batchUpdate` request that
> Google accepted before the fence began is durably reflected in the spreadsheet
> before the final import reads it.

The handoff permits two answers: evidence an externally verifiable barrier that
proves I-SHEET-COMPLETE, or conclude that the published APIs cannot provide one
and return a priced choice. **This revision takes the second**, and records the
search that led there so a reviewer can attack the search rather than the
conclusion.

#### 2.10.1 The barrier search

Thirteen candidates. Each is judged against one question: *does it distinguish
"the accepted request has been applied" from "the accepted request has not been
applied **yet**"?* An observation that cannot separate those two is not a barrier,
whatever else it is useful for.

**How the API claims below were established, and their standing.** Each row's
middle column is an *implementer's reading of the published reference surface as
of 2026-08-29*, in the same register revision 3 used for the no-precondition
claim. It is stated as **not found in the published surface**, never as a proof
of absence. If the Independent Reviewer knows of a published statement that
contradicts a row, that row is wrong and the conclusion changes — which is the
outcome this package would prefer.

| # | Candidate barrier | What the published surface provides | Proves I-SHEET-COMPLETE? |
|---|---|---|---|
| **B-1** | **The `batchUpdate` HTTP response itself** | `spreadsheets.values.batchUpdate` returns `BatchUpdateValuesResponse` with `totalUpdatedCells` and per-range results. A received response is a statement by Google that the update was applied | **For the requests whose response the client received — yes, and this is the only affirmative fact in the whole table.** For a request whose response was lost, it says nothing. That is exactly the case the finding names |
| **B-2** | A request or operation identifier queryable afterwards | none found. Sheets v4 defines no operation resource, no `google.longrunning.Operation`, and echoes no request id that can later be asked about | **No** — there is nothing to query |
| **B-3** | An idempotency or request token | none found on `values.update`, `values.batchUpdate` or `spreadsheets.batchUpdate` | **No** — a retry cannot establish the original's outcome, and may itself apply twice |
| **B-4** | A conditional write / precondition | none found: no ETag, `If-Match`, revision id or expected-value guard. This is revision 3's F-9 and it is unchanged | **No** |
| **B-5** | Drive `files.get(fields=version, modifiedTime)` | `version` is documented as a monotonically increasing number that changes when the file is modified. No published relationship to a *specific pending* request; no published read-after-write guarantee across principals | **No.** It describes applied state, so it can only ever support *"nothing has changed for N seconds"* — a quiet period, which the handoff rejects and which is rejected here for the same reason: there is no published maximum to wait for |
| **B-6** | Drive `revisions.list` | revisions of an editor file are created at the service's discretion. No published one-revision-per-API-write rule and no published creation latency | **No** — same class as B-5, with an extra unpublished property |
| **B-7** | Drive Activity API v2 | reports activity on a file. No published completeness or latency guarantee | **No** |
| **B-8** | Drive `files.watch` push notifications | documented as best-effort delivery, not ordered, not guaranteed | **No.** A barrier may not be built on a channel that is permitted to drop a message |
| **B-9** | **A marker write by the same client, read back** | would require a published per-document write-ordering or serialization guarantee for the Sheets API. None found | **No — and it adds nothing even if it existed.** To issue a marker and observe its response the writer must be alive and functioning; in that case B-1 has already answered for every earlier request. In the case that matters — the client is dead — there is nobody left to issue the marker |
| **B-10** | Protected ranges (`AddProtectedRangeRequest`) instead of a Drive ACL | a documented Sheets feature. The point at which protection is evaluated relative to an already-accepted request is not published | **No** — and the protecting call is itself a write facing the same race. It is also a mutation of the live Sheet's content, where the ACL change is not |
| **B-11** | `files.copy`, then import from the copy | no published point-in-time consistency guarantee for a copy | **No.** It replaces one unproven property with two, and a request accepted before the copy may still apply after it |
| **B-12** | Apps Script `SpreadsheetApp.flush()` | flushes the pending operations of *that script execution*. Not a document barrier; it cannot flush another client's in-flight API request | **No** — and it would add a production Apps Script dependency to the live Sheet for no gain |
| **B-13** | Waiting a fixed or measured interval after revocation | nothing. Google publishes no maximum propagation or completion bound | **No.** This is what revision 3's N5.0-17 and N5.0-18 amounted to and it is what the re-review rejected. **Retained in the design as an operational margin and never again described as a barrier** |

**One further question, asked because the design leaned on it implicitly.**
*Does revoking the Drive permission cancel a request Google already accepted?*
No published statement was found about when authorization is evaluated relative
to application. Revocation therefore bounds **new** requests and must not be
argued to abort accepted ones. Revision 3 came close to arguing that; revision 4
does not.

#### 2.10.2 The conclusion

**No observable fact available to this project distinguishes *"applied"* from
*"not applied yet"* for a request whose response was lost.** Every candidate
either reduces to a quiet period (B-5, B-6, B-13), depends on an unpublished
implementation property (B-9, B-10, B-11), is documented as unreliable (B-7,
B-8), or does not exist (B-2, B-3, B-4, B-12).

> **I-SHEET-COMPLETE cannot be guaranteed with the published Google APIs.**
> P5.0-R1's Sheet half is not closed by this revision and is not claimed closed.
> No barrier is invented, and no timeout, repeated `403`, ACL readback, process
> death, quiet period or sampled propagation distribution is relabelled as one.

#### 2.10.3 What *can* be guaranteed instead

Six properties, each externally verifiable, each stated with what it does not do.
They are the substance of the recommended option and they are deliberately
modest.

| # | Achievable guarantee | How it is established | What it does **not** do |
|---|---|---|---|
| **W-1** | **Client-observed completion.** Every request whose response the writer received is proved applied | B-1, the response itself. Under a clean drain this is *every* request the writer ever dispatched | says nothing about a request whose response was lost |
| **W-2** | **The unresolved set is enumerable, durable across a reboot, and normally empty.** The writer appends a record to a **durable, sealed, generation-bound, hash-chained** journal **before** dispatch (target ranges, payload digest, monotonic sequence, chain hash) and again on response (outcome), `fsync`-ing each. After termination the coordinator computes *dispatched with no recorded outcome* | **§2.13** in full: `/var/lib/freedom-sheet-writer/journal/` on the verified ext4 root volume; a directory the writer may not write, so it cannot unlink, rename or replace the file; `chattr +a` as a second layer, **probed rather than inferred**; a `chattr +i` generation seal; and a registered generation the activation trigger checks | **it is a completeness aid, not a proof.** A writer whose *dispatch path itself* has been replaced can dispatch without journalling, and no record it authors bounds that — **R-5.0-10**. Revision 4 also claimed *"nothing in the fence depends on the journal being complete"*; **that sentence is withdrawn as false** and §2.13.9 states the one direction in which activation does depend on it |
| **W-3** | **Fail-closed activation, on an unknown state as well as on a non-empty one.** The activation trigger requires a coordinator-recorded `dispatch_journal_clear` evidence row naming the **current registered generation**. The coordinator records it only when the journal validates *and* the unresolved set is empty | the same trigger mechanism as the other four fence methods; N5.0-20 fixes the permitted set size at **zero**; §2.13.6 fixes every unknown state at *refuse*; and the trigger additionally refuses evidence naming a superseded generation, or evidence older than a generation registration | it refuses; it does not resolve. A non-empty set is adjudicated by a human against the Sheet, and *"not reflected now, may apply later"* has no good answer — the operator abandons, re-fences, or accepts the residual explicitly |
| **W-4** | **Containment.** Nothing that happens on the Sheet after the final import can reach PostgreSQL | after activation the unit is PostgreSQL-authoritative; the import does not run again; the authority fence refuses every database write for a unit that is not at `cutover`/`database`, and no Sheet-derived write path exists for one that is | it does not protect the *legacy* store, which is exactly what a rollback would replay from |
| **W-5** | **Detection.** A late apply is found, not prevented | the fenced ranges are re-read and compared against the imported snapshot twice: once at import + N5.0-18, and once at the end of the N5.0-4 verification window | detection is bounded by the window; a divergence discovered is still a divergence that happened |
| **W-6** | **Rollback disclosure.** A `→ legacy` replay overwrites the Sheet, so any detected divergence is shown to the operator *before* the replay runs | a required step in the operations document and a named line item in the WP-9 rehearsal | it informs a decision; it does not preserve the divergent content unless the operator chooses to |

**The residual, stated once, plainly:** *a `values.batchUpdate` request that Google
accepted, whose response never reached the writer, and which Google applies after
the final import has read the Sheet, is not prevented and cannot be proved absent.
It is enumerated if the writer was working correctly, it is refused as a cutover
precondition while it is outstanding, it cannot corrupt PostgreSQL, and it is
detected within the verification window.* That sentence is the whole claim.

#### 2.10.4 The seven cases the handoff requires

Answered against the recommended control set: **drain → verify the journal →
terminate → revoke → observe → margin → import → activate**. The ordering is new
in revision 4 and §7.2 carries it.

| Case | Answer | Proven? |
|---|---|---|
| **1. A request accepted immediately before revocation whose response is lost when the client is killed** | The ordering change is the point: the writer is **drained first** — `SIGTERM` puts it in refuse-new-work mode and it waits out its own explicit request timeout for outstanding calls (N5.0-19), so in the normal case the response *does* arrive and W-1 answers. `SIGKILL` escalation remains the backstop for a writer that will not drain, and then W-2 enumerates what was outstanding and W-3 refuses the cutover. **Revoking first, as revision 3 did, is worse**: it converts *completed and known* into *failed and unknown*, because no published statement makes `values.batchUpdate` atomic across its `data` entries (an atomicity statement *was* found for the structural `spreadsheets.batchUpdate`; none was found for the values method this platform uses) | **No.** Bounded, enumerated and refused; not proven |
| **2. Delayed server-side application after the final import begins** | Not preventable and not detectable at the moment it happens. Contained by W-4 — it cannot reach PostgreSQL — and found by W-5's two re-reads | **No.** Contained and detected |
| **3. Permission propagation slower than every observed sample** | Accepted as unbounded. N5.0-18 is **reframed as an operational margin, not a barrier**, and WP-13's measurement is demoted to informing that margin. The control that does not depend on propagation is the writer being *absent*, which is a host fact | **Not applicable** — the design no longer rests on this number |
| **4. An out-of-systemd duplicate, and a writer starting after the host scan** | The duplicate is caught by `host_scan_clear` if it is running at scan time, and refused by Google after revocation propagates. A writer starting *after* the scan is **not observed** — R-5.0-5, restated and unchanged. It also has no journal entry the coordinator will see, so W-2 does not cover it either, and this is said rather than left to be inferred | **No.** This is the design's second acknowledged residual |
| **5. Rollback and replay, in both directions** | Identical protocol, no emergency path. `→ legacy` replays PostgreSQL's changes back to the Sheet under the **coordinator's** access while the writer is down; W-6 requires the divergence report first. `→ cutover` re-entry after a rollback repeats the whole fence, including a fresh journal check | **The protocol is symmetric; the residual is symmetric too** |
| **6. Operator death at every step** | *Before authorize:* nothing happened. *After authorize, before activate:* the revision stays pending, expires at `activation_deadline_at`, and can then only be abandoned. *After drain, before revoke:* the writer is down — a mutation outage, no integrity effect. *After revoke, before import:* the Sheet is read-only to the service account until a human restores it (R-5.0-7). *After import, before activate:* authority is unchanged, the import is idempotent and is re-run. *After activate, before restart:* authority moved, the writer is down, `/healthz` reports it. **Every step fails closed and none of them fails to a state where two writers are entitled** | **Yes**, for the property *"no step leaves two entitled writers"* |
| **7. The observable fact that establishes, or fails to establish, the final pre-import Sheet state** | **The writer's own received responses, and nothing else.** Together with an empty unresolved set they establish that the writer issued no unacknowledged mutation. They do **not** establish the Sheet's state, because a human editing the Sheet in a browser, or a duplicate the scan missed, leaves no journal entry. **So the honest answer to case 7 is: no observable fact establishes the final pre-import Sheet state**, and the import's control totals are a reconciliation of what was read, not a proof of what existed | **No** — and this is the sentence the whole finding turns on |

#### 2.10.5 The options, priced

**This is D5.0-9 / OD-62, reframed a third time** (§5.3). The revision-2 lease
options and the revision-3 *"which cost do you accept"* framing are both
withdrawn: the first was priced on a design that did not close the finding, the
second on a claim of enforceability that §2.10.2 retracts.

| | Option | What it gives | What it costs | Verdict |
|---|---|---|---|---|
| **G-A** | **Drain-first boundary with an enumerable unresolved set** (recommended). W-1 … W-6, in the §7.2 ordering, with the isolated writer, the explicit request timeout, the dispatch journal, the ACL revocation and the two divergence re-reads | The strongest set of *verifiable* properties available. Every request the writer completed is proved complete; anything outstanding refuses the cutover; nothing reaches PostgreSQL; a late apply is detected inside the window | A fourth systemd unit and a fifth OS identity; a Sheet-mutation outage for the fence window at each cutover and rollback; a production Drive-permission change at each cutover; an `fsync` on the legacy mutation path; an operator adjudication step; **and an explicitly accepted, unprovable residual** | **Recommended, with the residual named.** It does not close P5.0-R1's Sheet half and is not offered as doing so |
| **G-B** | **Pre-cutover write-path retirement.** Deploy a build in which the Sheet write path for the migrating unit is *absent*; refuse those mutations for an operator-accepted period; verify the journal stayed empty throughout; then import and cut over | Stronger *in kind* than G-A: the in-flight set is empty because of a **deployment**, not because of a timing argument. The residual window becomes *"a request accepted before a deploy that happened days ago"* | A per-unit deploy and a mutation outage measured in days, roughly forty times. **Variant G-B′:** do it once for the whole bot instead of per unit — one long outage rather than forty short ones, and a much larger product decision | **The strongest available, and the most expensive.** Still not a proof: it rests on the journal's completeness and on no predecessor request being outstanding at deploy time |
| **G-C** | **Accept a measured quiet period as the boundary.** Revoke, wait WP-13's observed distribution plus a margin, import | Simplicity, and no journal | **This is what the re-review rejected.** The implementer's assessment is that it does not close P5.0-R1 and never can, because no published maximum exists to measure against | **Listed so Peter can accept the residual knowingly rather than have the implementer relabel it.** Not recommended |
| **G-D** | **Cut no Sheet-authoritative unit over at all.** Package 5.0 still delivers the PostgreSQL fence — complete on its own — the isolated writer, the journal, the ACL control, the detection and the monitoring. The first Sheet-authoritative cutover waits for an accepted authority design | P5.0-R1 stays open by decision rather than by oversight; nothing is claimed that is not true | Phase 5's field cutovers do not proceed. Shadow comparison and the whole platform build can still continue, so this is a pause on cutover, not on Phase 5 | **The conservative bound.** It is a real option and is priced as one |

**Owner: Product Owner, with the Operations Owner and the Security Reviewer.
Required by: before WP-4b.** The implementer does not choose, because
`.agents/AGENTS.md` forbids degrading the Freedom bot and forbids production
access changes without approval, and because **accepting an unprovable residual
on the authoritative store of a live community's game state is a risk-acceptance
decision, which is the Acceptance Authority's and not an agent's.**

#### 2.10.6 Retained from revision 3 — the host-side option comparison

Retained in full rather than deleted, because the handoff requires that prior
proposals not be rewritten as though they were never made, and because **F-7 is
still the host-side control inside G-A and F-6 is still its fallback.** What
revision 4 withdraws is not this table but the *claim built on it* — that F-7 and
F-8 together constitute an enforceable fence. They do not; §2.10.2 says why.

| | Option | What it guarantees | `SIGSTOP` / resume / GC | Out-of-systemd duplicate | Request past last check | Partial shutdown | Failed restart | Rollback | Operator death | Verdict, as revised |
|---|---|---|---|---|---|---|---|---|---|---|
| **F-6** | **Stop the legacy-writing process before the final import and activation**, verify termination at the process/cgroup level, start only a build whose legacy writer is disabled by the activated authority | A terminated process writes nothing. There is no clock, no lease and no protocol to get wrong | **Defeated by termination.** `SIGKILL` is not blockable and is delivered to a `SIGSTOP`ped process, so `systemctl stop`'s escalation kills a paused process. There is nothing to resume | **Not covered by the unit stop or the cgroup check** — both observe what systemd started. Covered only by a host-wide process scan, which is point-in-time | **Not covered.** A call already dispatched to Google cannot be recalled, and revision 4 no longer claims a wait bounds it | `systemctl stop` is all-or-nothing at cgroup level; if it overruns, the unit reports non-`inactive` and the cgroup is non-empty, so the coordinator records nothing and the activation trigger refuses. Fail-closed | The bot stays down: an outage, no dual write. The Sheet remains the rollback source | Same protocol reversed. No emergency path | Revision stays pending; writer stays down; `activation_deadline_at` expires it. Fail-closed | **The declared fallback**, if the fourth unit is judged too invasive. Same properties as F-7, whole-bot outage |
| **F-7** | **Isolate the legacy Sheet writer in a separately terminable helper process** | Everything F-6 gives, with the outage scoped to *Sheet mutations*. Reads, `/info` and every non-mutating command keep serving | identical to F-6 | identical to F-6 | identical to F-6 | identical to F-6 | only the writer is down; the bot stays online and refuses affected mutations with a typed message | identical to F-6 | identical to F-6 | **Retained as the host-side control inside G-A**, and in revision 4 it also carries the drain, the explicit request timeout and the dispatch journal, which is where its added value now is. **Cost: a topology change — a fourth systemd unit and a fifth OS identity holding the Google credential** |
| **F-8** | **Revoke the legacy writer's Google write access for the duration of the cutover** | Refuses **new** requests at Google after propagation | a resumed process's *new* write is refused with `403` | **covered** for new requests, continuously rather than at a point in time | **not covered.** Revision 3 claimed a call accepted before revocation *"is captured by the final import"*; **that claim is withdrawn** — §2.10.1's B-13 and the note under it | not applicable | not applicable | restore the permission as the last step | the permission stays revoked: read-only until a human restores it. Fail-closed | **Retained as a control against duplicates and restarts, demoted from *fence* to *access bound*.** Its propagation latency is an operational margin (N5.0-18), not a barrier |
| **F-8b** | **Rotate or disable the service-account key** | — | — | — | — | — | — | — | — | **Rejected, unchanged.** It removes reads as well as writes; an already-minted access token stays valid for its remaining lifetime, so it is not a prompt fence; and its rollback is credential redistribution rather than one API call |
| **F-9** | **A Google-supported conditional or fencing mechanism** | — | — | — | — | — | — | — | — | **Not available, unchanged** — and now one row of a thirteen-row search (§2.10.1 B-4) rather than a single lookup |
| **F-4** | *Leased self-fencing with drain acknowledgement* (revision 2) | — | **Fails.** A process paused between its headroom check and its external write and resumed after the horizon emits one legacy write | — | — | — | — | — | — | **Rejected — this is finding P5.0-R1.** Retained so nothing reintroduces it |
| **F-1** | *Startup check plus restart order* (revision 1) | — | **Fails.** A process that started before the change keeps its authority until it restarts | — | — | — | — | — | — | **Rejected — this was the original finding** |

**The three costs revision 3 tabulated are unchanged and still apply to G-A and
G-B**, and revision 4 adds a fourth:

| Cost | Which options | Who must accept it |
|---|---|---|
| A **bounded Freedom-bot mutation outage** at every cutover and rollback — scoped to Sheet mutations under F-7, whole-bot under F-6, measured in days under G-B | all | Product Owner and Operations Owner. `.agents/AGENTS.md` forbids degrading the bot |
| A **topology change** — a fourth systemd unit and a dedicated OS identity holding the Google service-account credential, moving that credential *out* of the bot process | F-7 | Operations Owner and the Security Reviewer. **D5.0-12 / OD-65** |
| A **production Google access change** at each cutover — a Drive permission edited and restored | F-8 | Product Owner and the Security Reviewer |
| **New in revision 4: an accepted, unprovable residual** on the legacy store at each Sheet-authoritative cutover | G-A, G-B, G-C | **Acceptance Authority.** This is a risk acceptance, not a design choice, and §2.10.3's closing sentence is what is being accepted |

---

### 2.11 Proof ownership — the design comparison P5.0-R4 requires

The handoff names three options. Each is traced for who authenticates the writer,
which SQL principal PostgreSQL sees, who may write which row, how credentials are
provisioned and rotated, and whether a compromised process can falsify another
instance's proof.

| | Option | Who authenticates the writer | SQL principal PostgreSQL sees | Who may write which row | Credential provisioning and rotation | Can a compromised bot / web / worker falsify a proof? |
|---|---|---|---|---|---|---|
| **O-1** | **Distinct least-privilege principals per process role or instance**, with row-level security or security-definer procedures binding writes to the authenticated principal | PostgreSQL, against a per-role credential in each service's environment file | `freedom_bot`, `freedom_web`, `freedom_worker` — a **role**, never a process instance | RLS binds a row to `current_user`, so a role may write only rows carrying its own role name | **Three** new credentials, in three environment files, with three rotations and three ways to get a deployment wrong. Per *instance* is worse: an instance is created at each restart, so per-instance credentials would need dynamic provisioning this platform has no mechanism for | **Another instance's: no. Its own: yes.** And its own is the case that matters — the process being fenced is exactly the one whose statement about itself is worthless. RLS authenticates the liar |
| **O-2** | **A privileged coordinator alone records observed termination or drain evidence; application runtime roles receive no authority-proof write privilege** | PostgreSQL, by **peer** authentication over the Unix-domain socket, against the host account that runs the operator command | `freedom_migration_coordinator`, which no service unit can reach: no password, no TCP login, no environment file entry | Only the coordinator inserts evidence, revisions and dispositions. The runtime role holds nothing on the evidence table and `SELECT` only on the rest | **One** principal, and **no secret to distribute**: peer authentication makes the secret host access, which `docs/operations/break-glass-credential-custody.md` already governs. Rotation is a `pg_hba.conf` and grant change, not a secret redistribution | **No, in either direction.** There is no row any application process is permitted to write |
| **O-3** | **Remove runtime-authored acknowledgements entirely**, if the P5.0-R1 lifecycle fence supplies stronger independently verifiable evidence | not applicable — no runtime process writes anything | not applicable | nobody, from the application side | nothing to provision | **Unconstructable.** There is no acknowledgement to forge |

**Recommendation: O-3, realized through O-2.**

O-3 is the primary answer and it is available precisely *because* R1's
remediation replaced a self-reported drain with an externally observed lifecycle
event. The two findings are answered by one change: once the fence is
*termination observed by the supervisor* and *access revoked by Google*, there is
nothing left for a runtime process to attest, so the tables that held its
attestations are withdrawn rather than secured.

O-2 supplies the principal that records what was observed. It is preferred over
O-1 on three counts: it removes self-forgery rather than authenticating it; it
adds one credential-free principal instead of three distributed secrets; and it
follows the accepted host-local operator pattern (`tools/web_operator.py`, the
submission-admission fence) rather than inventing a second authorization model.

**O-1 is rejected as the primary control and one element of it is kept.** Its
conclusion about grants — that the runtime role should hold no write privilege on
the authority plane — is adopted in full (logical schema §4.3). What is rejected
is the idea that authenticating a self-report makes it trustworthy.

**Consequences that must be accepted, not assumed.** Introducing
`freedom_migration_coordinator` is a database-role and credential-topology change
and therefore a security/operations design: it needs an impact assessment and the
named Security Reviewer's review. It introduces no new secret, because peer
authentication has none.

**Revision 4 corrects one sentence that stood here.** Revision 3 said this *"does
not change the accepted production topology"*. That was true of the database role
considered alone and **is not true of the control**: a peer-authenticated role
isolates nothing until the operating-system identity it trusts is named, and
naming it requires an OS account, a `sudoers` drop-in, a `pg_ident` map and a
deployment path outside the repository — §2.12. **It does change the accepted
topology**, which is why D5.0-11 / OD-64 is extended and D5.0-12 / OD-65 is
raised. OD-20/21/22's substance still stands — same host, loopback, separate
roles and environment files, no shared credential — but the claim of *no change*
does not. If Peter prefers the existing schema-owner credential for the
coordinator rather than a new role, the design still works and is strictly more
privileged than necessary; that variant is §5.3's Option C.

---

### 2.12 The coordinator's operating-system identity — the boundary P5.0-R4 requires

Revision 3 named a database principal and stopped there. The re-review's
objection is exact: **peer authentication trusts the operating-system identity of
the connecting process, and revision 3 never said which identity that is.** A
role called `freedom_migration_coordinator` that any local process can
authenticate as is not isolated; it is renamed.

This section supplies the missing half. **None of it is adopted here** — it
creates two OS accounts, a `sudoers` drop-in, `pg_hba.conf` and `pg_ident.conf`
lines, a deployment path outside the repository, and hardening on a live unit,
all of which change the accepted topology. It is raised as **D5.0-11 / OD-64,
extended** and **D5.0-12 / OD-65, new** (§5.3).

#### 2.12.1 The starting position, observed rather than assumed

Three facts about this host, read on 2026-08-29, that the design must not assume
away. They are recorded in §8.1 with how each was observed.

| # | Observation | Why it matters here |
|---|---|---|
| **H-1** | `/opt/freedom-blades/platform` is `drwxrwsr-x foundry:discordbot` and its files are `-rwxrwxr-x foundry:discordbot`. `freedomweb` is a member of group `discordbot` (`getent group discordbot` → `discordbot:x:997:freedomweb`) | **The bot, web and worker processes can rewrite every module in this repository today**, including everything under `tools/` and `migrations/`. A coordinator that executed `python -m tools.migration_authority` from this tree would execute code a compromised service process can choose. **This alone defeats the revision-3 design**, and it is the reason for the separate root-owned deployment path below |
| **H-2** | `infra/systemd/freedom-bot.service.tmpl` sets no `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem` or `ProtectHome`. This is Phase 0 topology finding **F-3**, still open | Every argument of the form *"a service process cannot gain privileges"* is weaker for the bot than for the web and worker units, which do set them. The fence should not depend on an unhardened unit |
| **H-3** | `/var/run/postgresql` is `drwxrwsr-x postgres:postgres` | Every local identity can reach the PostgreSQL socket. **The isolation is therefore the `pg_ident` map, not the socket path.** A private socket directory was considered and is *not* proposed: it adds a failure mode and nothing the map does not already give |

#### 2.12.2 The identities — **the canonical membership table.** Rewritten in revision 12; this is remediation R11-B

**The defect, conceded before its replacement.** Revision 11's version of this
subsection gave `freedomcoord` and `freedomsheet` the groups *"its own only"*,
and then asserted that **`freedomcoord` … is in no group any service identity
holds**. **Both statements were false from revision 6 onward**, and they were
false against this package's own design: §2.13.3 creates the system group
`freedomjournal` holding exactly `freedomcoord` and `freedomsheet`, the `0750`
journal directory and the `0440` seal are unreadable without it, and the E1/E2
evidence identities of §2.13.5c are constructed with it. Following this
subsection made the writer unable to perform the startup validation §2.13.5b
requires of it and invalidated **C-4**; following §2.13.3 contradicted this
subsection. That is security-review finding **P5.0-SR2**, and the fix is not a
corrected sentence: **this table becomes the single place a membership is
stated**, and every other passage cites it.

**The rule, stated before the table.** *Every* identity, primary group and
supplementary group in Package 5.0 appears **here and nowhere else**. §2.12.6,
§2.12.7, §2.13.3, §2.13.5c's `E1 … E8`, §2.13.7 and logical schema §4.3.2 refer
to this table and **state no membership of their own**. A membership that appears
in another passage without this table changing is a defect under stop condition
**10p**, not a detail.

**The R7 amendment — the `postgres` account.** Ruled by Peter Duscha,
Acceptance Authority, on **2026-09-06**, on Codex's recommendation, and recorded
under change-log **C-P5.0-AE**: **Option A is accepted**, and the complete
supplementary-group set permitted for the `postgres` operating-system account is
**exactly `ssl-cert`**, with primary group `postgres`.

The gap this closes is evidence-harness finding **EH-R6-1**. The harness's
database steps run as `postgres`, but this table covered six identities and
`postgres` was not one of them, so the harness had no reviewed set to construct a
credential from and refused every such step. Three limits on the amendment,
stated rather than left to be inferred:

1. **This package does not provision, modify or own the account.** It is an
   existing host identity, marked as such, and nothing here creates it or
   changes its memberships. The row states what is *permitted*; a host that
   differs is a **finding**, refused before a process exists, exactly as the
   `JNL-52` rule requires of every other row.
2. **The ruling covers the membership and nothing else.** The shell, password
   and home columns are recorded as *not asserted by this package*, because the
   ruling did not state them and no check in this package reads them. Writing a
   plausible value into them would be the same defect this table exists to
   prevent.
3. **`ssl-cert` and `postgres` gain inverse rows** because the identity row names
   them and this table's rule is that a membership appears here and nowhere else.
   Their member lists are exact for the same reason every other row's is, so an
   unexpected member is a failed `JNL-52` case rather than a difference to note.
   **Corrected by the R8 amendment below:** the two rows are exact in different
   ways, because `postgres` is the account's *primary* group and `ssl-cert` its
   supplementary one, and only the second is an explicit `getent group`
   membership.

**The R8 amendment — what the inverse table's member column means.** Codex
evidence-harness finding **EH-R8-1**, 2026-09-06. The R7 amendment wrote
`postgres` into the member list of the `postgres` group. That conflated two
different relations, and it made this table assert a fact the ruling never
stated:

- **the identity table's `Primary group` column** is the account's passwd
  record. It is observed with `id`, and `JNL-52`'s per-identity case compares it.
- **the inverse table's `Members, exactly` column** is the **fourth field of
  `getent group`** — the group's *explicit* member list. An account is **not**
  listed there merely because the group is its primary group; `useradd` does not
  put it there and `getent` does not report it there.

So a correctly configured host reports `postgres:x:<gid>:` with an empty fourth
field, and R7's row would have **failed** `JNL-52-GROUP-postgres` for a host that
matches the ruling exactly. The `postgres` row's member list is therefore
**empty**, which is the set this table's own identity half implies: the
supplementary lists are complete, and no identity row names `postgres` as a
supplementary group. The row is kept rather than deleted because the empty list
is a claim worth failing on — an account explicitly added to `postgres` would
hold the cluster's data directory through a group, and that is a finding.

**The ruled facts are unchanged.** Primary group `postgres`, complete
supplementary set exactly `ssl-cert`. R8 corrects a representation, not the
membership Peter Duscha ruled, and it seeks no new ruling.

**R9 ruling — correct the four pre-existing inverse rows.** Peter Duscha,
Acceptance Authority, accepted Codex's recommendation on **2026-09-06**. This
is a representational correction under the R8 definition of the inverse table,
not a change to any account's primary or supplementary memberships. The exact
explicit-member sets are:

- `freedomcoord`: none;
- `freedomsheet`: none;
- `discordbot`: `freedomweb` only; and
- `fbprobe`: none.

Peter Duscha additionally accepted Codex's recommendation on **2026-09-06**
that the missing inverse row for the already-recorded supplementary membership
`foundry -> users` is **`users`: `foundry` only**. This likewise changes no
account membership; it completes the explicit inverse relation already stated
by the identity table.

The prior defect and its impact are retained here as the reason for the ruling.
`freedomcoord`, `freedomsheet`, `discordbot` and `fbprobe` each list in their
inverse row the account whose primary group they are. On a host provisioned as
§2.13.3 requires, `getent group` reports an empty fourth field for the first
three and `freedomweb` alone for `discordbot`, so those four `JNL-52-GROUP-*`
cases would fail and the membership matrix would gate off the access cases. This
is `JNL-52` correctness finding **EH-R8-2**. It fails closed, but it prevents the
required evidence from being collected on a correctly provisioned host. The R9
remediation is authorized to apply only the four exact sets above, remove the
temporary `PRE_EXISTING_PRIMARY_IN_INVERSE` hold, update focused tests and
regenerate covered artifacts. It does not authorize harness execution, host
inspection or any account/group mutation. See change-log **C-P5.0-AF**.

**Post-R9 independent disposition and evidence-harness target-root ruling.**
Codex independently reviewed the implemented R9 correction on **2026-09-06**
and closed **EH-R8-2** and **DS-R8-2**. Peter Duscha accepted Codex's next
recommendation the same day: concrete-plan conflict **C-1** is resolved by
allowing the harness to create and later remove its own exact disposable target
root, in addition to paths contained beneath it. The exception applies only
after the existing `DisposableTarget` validation has established an absolute
`fb-evidence-*` path at the required minimum depth and outside all forbidden
ancestors, production locations and the repository. Cleanup is the existing
non-recursive `rmdir`; unexpected content therefore leaves reported residue and
cannot be recursively deleted. No arbitrary, shallow, unresolved, sibling or
escaped path is admitted. This ruling authorizes bounded implementation of
concrete-plan conflicts **C-2 through C-5**, tests, regenerated dry-run artifacts
and handback documentation only. It authorizes no evidence run, generated
vector, SSH, host inspection, privileged command or host/database mutation.
See change-log **C-P5.0-AG**.

**Post-R10 runtime ruling — Option B.** Peter Duscha accepted Codex's
recommendation on **2026-09-06**. The reviewed case program is an interpreted
Python source file, and every vector names the documented Python 3.12
interpreter explicitly before that file; a shebang is not relied upon. The
interpreter is invoked with `-I -S`, and the permitted surface is the closed set
of exact reviewed case-program vectors, not arbitrary Python execution. The
case-program source and installed bytes are identical and covered by the review
manifest. Preflight records and validates the interpreter's absolute path,
version and executable SHA-256; any mismatch makes the affected evidence
`inconclusive` and prevents a pass. The program may use only Python built-ins
and the standard-library modules necessary for the already-enumerated bounded
operations, with no third-party package or site initialization.

The shebang option is rejected because it conceals the actual executable from
the reviewed vector and causes P-03/P-04 to assert about the script rather than
the interpreter. Compiling on the target is rejected because the compiler and
generated bytes would not be pinned by the pre-execution manifest. This ruling
authorizes only bounded R11 harness remediation for C-2, dependent C-3 and C-5,
tests and regenerated dry-run artifacts. It grants no harness execution, SSH,
host/database mutation, Package 5.0 implementation, migration `0014`, cutover,
OD-62 ruling or Package 5.1+ authority. See change-log **C-P5.0-AH**.

**Identities — primary group, and the complete supplementary list.** *Complete*
means exhaustive: an identity whose supplementary list is `—` is asserted to be
in **no** supplementary group, and `JNL-52` fails the case rather than passing it
if `id` reports one.

| Identity | Primary group | Supplementary groups, **complete** | Shell | Password | Home | Runs | Reachable how |
|---|---|---|---|---|---|---|---|
| **`freedomcoord`** *(new, proposed)* | `freedomcoord` | **`freedomjournal`** | `/usr/sbin/nologin` | locked; `PASSWORD NULL` in PostgreSQL too | none | `migration-authority`, the only OS identity `pg_ident` maps to the coordinator role | **only** through the §2.12.4 `sudoers` drop-in. No `authorized_keys`; `su` is refused by the shell |
| **`freedomsheet`** *(new, proposed, D5.0-12)* | `freedomsheet` | **`freedomjournal`** | `/usr/sbin/nologin` | locked | none | `freedom-sheet-writer`; holds the Google service-account credential moved out of the bot | systemd only |
| `discordbot` *(existing)* | `discordbot` | **—** | `/bin/bash` *(existing)* | existing | existing | `freedom-bot` | systemd; and anything that can already run as it |
| `freedomweb` *(existing)* | `freedomweb` | **`discordbot`** | `/usr/sbin/nologin` | — | — | `freedom-web`, `freedom-worker` | systemd |
| `foundry` *(existing)* | `foundry` | **`sudo`, `users`** | `/bin/bash` | existing | existing | the maintainer's interactive account; the named Platform Administrator | interactive login |
| **`postgres`** *(existing; **not** provisioned by this package — added by the R7 amendment, change-log **C-P5.0-AE**)* | `postgres` | **`ssl-cert`** | not asserted by this package | not asserted | not asserted | the PostgreSQL 16 server, and the `psql` and `install` steps the evidence plan runs as it | systemd, and the evidence harness's own process boundary |
| `fbprobe` *(disposable; **evidence only**, inside unconfirmed A-5.0-5)* | `fbprobe` | **—** | `/usr/sbin/nologin` | locked | none | nothing. It runs no service and owns no artifact in the hierarchy | created and removed by the root evidence harness of §2.13.5c, and by nothing else |

**Groups — the inverse, which is the half a membership table usually omits.**
The **fourth field** of `getent group` must report exactly these members, and an
unexpected member is a **failed** `JNL-52` case rather than an incidental
difference. That field is the group's *explicit* member list: a primary
membership is stated in the identity table above and observed with `id`, and it
does **not** appear here — the R8 amendment, finding **EH-R8-1**.

| Group | Members, exactly | What membership grants | What it does **not** grant |
|---|---|---|---|
| **`freedomjournal`** *(new)* | **`freedomcoord`, `freedomsheet`** — and nobody else | `r-x` on `…/journal` (`0750 root:freedomjournal`) and `r--` on `…/journal/__GEN__.seal` (`0440 root:freedomjournal`) | **no `w` on either**; nothing in `…/archive`; no database privilege of any kind; and **no identity transition** — see the three claims below |
| **`freedomcoord`** | **none** — `freedomcoord` is the account's primary group, not an explicit membership | `r-x` on `…/archive` (`0750 root:freedomcoord`) and `r--` on its `0440` files; and it is the **group** of `…/journal/__GEN__.journal` (`0640 freedomsheet:freedomcoord`), which is **read** | no write anywhere in the hierarchy; no `sudo` rule; no capability |
| **`freedomsheet`** | **none** — `freedomsheet` is the account's primary group, not an explicit membership | nothing by itself. The writer's access to its own journal file is **ownership**, not this group | nothing in `…/journal` the directory, the seal or the archive |
| `discordbot` *(existing)* | **`freedomweb`** — `discordbot` is the account's primary group and does not appear in this explicit-member relation | group write on the repository worktree — observation **H-1**, a pre-existing condition raised as D5.0-12 / OD-65 item 3 | nothing under `/var/lib/freedom-sheet-writer`, `/opt/freedom-blades/coordinator` or `/etc/freedom-blades`; **and nothing the deploy step reads** (§2.12.5a) |
| `sudo` *(existing)* | `foundry` | the two `Cmnd_Alias` entries §2.12.4 and §2.13.7 define, each with a fixed absolute executable and no `NOPASSWD` | nothing else by these drop-ins. Whether some *other* rule in `/etc/sudoers.d/` widens it is check **C-1**, **still not run** (§8.1) |
| `users` *(existing; inverse row completed by the R9 ruling)* | `foundry` — and nobody else | the existing supplementary membership already stated by the `foundry` identity row | no Package 5.0 filesystem, database or identity-transition authority |
| **`postgres`** *(existing; added by the R7 amendment, member list corrected by the R8 amendment)* | **none** — it is the `postgres` account's *primary* group, so its `getent group` fourth field is empty, and no other identity in this table names it as a supplementary group | ownership of the cluster's data directory and of `/var/run/postgresql`, which is observation **H-3** and is how the server reaches its own socket | nothing under `/var/lib/freedom-sheet-writer`, `/opt/freedom-blades/coordinator` or `/etc/freedom-blades`; no membership of `freedomjournal` or `freedomcoord`; and **no `sudo` rule** |
| **`ssl-cert`** *(existing; added by the R7 amendment)* | `postgres` — and nobody else | read of the server's TLS private key under `/etc/ssl/private`, which is the reason the account holds the membership at all | nothing in this package's hierarchy and no database privilege. It is recorded here because this table is the only place a membership may be stated, **not** because this package grants it |
| `fbprobe` *(disposable)* | **none** — `fbprobe` is the account's primary group, not an explicit membership | nothing. It is not in `freedomjournal` or `freedomcoord`, which is what makes `JNL-50` case 8's `EACCES` attributable | — |

**Which provisioned identity each evidence identity is.** §2.13.5c's `E1 … E8`
are launched by a root harness, and three of them correspond to **no** provisioned
identity at all. That is legitimate — they exist to isolate a kernel check — but
it must be visible, because an evidence identity that silently differs from the
identity it is named after proves something about a process nobody runs.

| Evidence identity | Corresponds to | Note |
|---|---|---|
| **E1**, **E2** | **`freedomsheet`** as this table provisions it | uid, gid and the complete supplementary list all match. E2 additionally carries an ambient `CAP_LINUX_IMMUTABLE` the deployed unit can never hold |
| **E8** | **`freedomcoord`** as this table provisions it | **Corrected in revision 12:** E8 carries `freedomcoord` **and `freedomjournal`**. Revision 11 gave it `freedomcoord` only, which is not the identity provisioning creates |
| **E3**, **E4**, **E6** | **none — synthetic** | `fbprobe` with constructed capability sets. Deliberately in no group in this table, which is the property `JNL-50` case 8 relies on |
| **E5** | **none — synthetic** | `fbprobe` **plus `freedomcoord`**, a combination this table provisions for nobody. It exists to give a non-root identity `…/archive` traversal while it clears a flag, and it is labelled synthetic here so no reader takes it for a real holder set |
| **E7** | root | the harness's own process |

**The isolation claim, restated so that it is true.** Revision 11's sentence is
**withdrawn**. What holds is three separate claims, each with its own evidence
case in `JNL-52` and none of which the shared group weakens:

1. **The shared group is read-only, and covers one directory and one file.**
   `freedomcoord` and `freedomsheet` share exactly one group, `freedomjournal`.
   Its whole grant is `r-x` on `…/journal` and `r--` on the seal. There is **no
   `w` for it anywhere** — the directory is `0750` with group `r-x`, and the seal
   is `0440` and additionally `chattr +i`. `JNL-52` cases 2 and 4 assert the
   refusals from both sides.
2. **Sharing a group is not an identity transition.** Nothing about being in a
   group with `freedomcoord` lets `freedomsheet` *become* it. Peer authentication
   reads the connecting process's **uid** from `SO_PEERCRED`, which a process
   cannot forge; `pg_ident.conf` maps a **system user**, and its one line names
   `freedomcoord` (§2.12.3); the `sudoers` drop-in names **`foundry`** as the
   invoker and `freedomcoord` as the target (§2.12.4), and no service identity is
   in `sudo`. **No PostgreSQL, `sudo` or kernel mechanism in this design consults
   a group to decide who a process is.**
3. **`freedomcoord` holds no write authority that `freedomsheet` could inherit
   through the group.** `freedomcoord` is in `freedomcoord` and `freedomjournal`,
   and neither grants `w` anywhere in the hierarchy — its access to `…/archive`
   is read and traverse, and the journal file's group bits are `r--`. So even a
   hypothetical group-mediated escalation would arrive at no write bit.

**What the shared group does cost, stated rather than argued away.** It gives the
writer's identity read access to the seal — which is the grant remediation R5-B
required and §2.13.3 assesses — and it means the sentence *"the coordinator
shares no group with any service identity"* can no longer be used as a shortcut
anywhere in this package. It is listed as security-review surface 11 in §9.2 with
its question attached, and **the security reviewer is asked to test the three
claims above rather than accept them**.

#### 2.12.3 PostgreSQL authentication, exactly

`pg_hba.conf`, placed **above** any broader `local all all …` line — PostgreSQL
uses the **first** matching rule, so ordering is the control and not a
formatting preference:

```
# TYPE       DATABASE        USER                            ADDRESS  METHOD  OPTIONS
local        __PROD_DB__     freedom_migration_coordinator            peer    map=freedom_coord
local        all             freedom_migration_coordinator            reject
host         all             freedom_migration_coordinator   all      reject
hostssl      all             freedom_migration_coordinator   all      reject
hostnossl    all             freedom_migration_coordinator   all      reject
```

`pg_ident.conf` — exactly one line for the map, no regular expression and no
wildcard:

```
# MAPNAME        SYSTEM-USERNAME    PG-USERNAME
freedom_coord    freedomcoord       freedom_migration_coordinator
```

The role itself:

```sql
CREATE ROLE freedom_migration_coordinator
    LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
    NOINHERIT NOREPLICATION NOBYPASSRLS
    PASSWORD NULL
    CONNECTION LIMIT 2;
REVOKE CONNECT ON DATABASE __PROD_DB__ FROM PUBLIC;
GRANT  CONNECT ON DATABASE __PROD_DB__ TO freedom_migration_coordinator;
```

Four independent things must all hold before a connection as this role succeeds,
and they fail in different layers:

1. the kernel reports the connecting peer's uid as `freedomcoord`
   (`SO_PEERCRED`; a process cannot forge it);
2. `pg_ident` translates that system user to this role — no other system user is
   listed;
3. the first matching `pg_hba` line is the `peer` line, which requires `local`
   transport and the production database; every other combination hits a
   `reject`; and
4. `PASSWORD NULL` means no password authentication can ever succeed for the
   role, so a leaked `.pgpass`, `PGPASSWORD` or environment file is worthless.

**Rule (3) is why the TCP rejects are written out** rather than left to the
absence of a permissive line: a later edit that adds a broad `host all all
scram-sha-256` line must not silently make this role reachable over the network,
and a `reject` above it means it cannot.

#### 2.12.4 Who may invoke the command, and what it executes

`/etc/sudoers.d/freedom-migration-coordinator`, owner `root:root`, mode `0440`,
installed only through `visudo -c -f`:

```
Cmnd_Alias FREEDOM_MIGRATION_AUTHORITY = /opt/freedom-blades/coordinator/bin/migration-authority
Defaults!FREEDOM_MIGRATION_AUTHORITY env_reset, !setenv, log_output, \
    secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
foundry ALL=(freedomcoord:freedomcoord) FREEDOM_MIGRATION_AUTHORITY
```

Four properties of that rule, each deliberate:

- **`foundry` only.** No service identity is named, and none is in `sudo`
  (`getent group sudo` → `sudo:x:27:foundry`, read 2026-08-29). The named
  Platform Administrator is a *person*, and the command additionally requires
  `--operator`, so the audit row names a human and not "the system", exactly as
  `tools/web_operator.py` already requires.
- **No `NOPASSWD`.** An authority cutover re-authenticates. This is a deliberate
  departure from convenience: the command changes which store the platform
  believes.
- **`env_reset`, `!setenv`, `secure_path`.** `PYTHONPATH`, `PYTHONHOME`,
  `PYTHONSTARTUP`, `LD_PRELOAD`, `LD_LIBRARY_PATH` and the whole `PG*` family are
  discarded at the boundary and cannot be re-supplied with `sudo -E`.
- **One fixed absolute path, and it is not a Python module.** The rule permits
  arguments — the subcommands need them — so the *executable* must be one that
  cannot be told to run a different file. It is a root-owned wrapper, not
  `python -m …`, precisely because `-m` resolves through a path a caller could
  otherwise influence.

The wrapper, `/opt/freedom-blades/coordinator/bin/migration-authority`, does four
things and nothing else:

```sh
#!/bin/sh
set -eu
unset PYTHONPATH PYTHONHOME PYTHONSTARTUP PGHOST PGPORT PGUSER PGDATABASE \
      PGPASSWORD PGPASSFILE PGSERVICE PGSERVICEFILE PGSYSCONFDIR PGOPTIONS
cd /var/lib/freedom-coordinator
exec /opt/freedom-blades/coordinator/venv/bin/python -I -P \
     -m migration_authority "$@"
```

`-I` runs Python in isolated mode — it ignores `PYTHONPATH` and the user site
directory and does not place the current directory on `sys.path`; `-P` states the
same path property explicitly rather than relying on `-I` implying it. Together
with `env_reset` that closes the environment, path and current-directory
injection routes the handoff names.

#### 2.12.5 Ownership and modes

| Path | Owner : group | Mode | Reason |
|---|---|---|---|
| `/opt/freedom-blades/coordinator` | `root:root` | `0755` | the deployment root, **outside** the group-writable `platform` tree of H-1 |
| `…/bin/migration-authority` | `root:root` | `0755` | the only `sudo`-permitted entry point |
| `…/venv` and everything under it | `root:root` | `0755` dirs, `0644`/`0755` files | its own interpreter and dependencies. It does **not** share `runtime/venv-bot` or `runtime/venv-web` |
| `…/lib/migration_authority/**` | `root:root` | `0755` dirs, `0644` files | the deployed coordinator code |
| `…/etc/migration-authority.conf` | `root:freedomcoord` | `0640` | the database name and socket path. **It holds no credential**, because peer authentication has none |
| `/var/lib/freedom-coordinator` | `freedomcoord:freedomcoord` | `0700` | the working directory; the only path the process may write |
| ~~`/run/freedom-sheet-writer/dispatch.journal`~~ | — | — | **Withdrawn by revision 5. This is finding P5.0-R5.** `/run` is `tmpfs` on this host (§8.1 **H-4**) and the `chattr +a` claim was inferred from a different filesystem. The replacement hierarchy, with an owner, group, mode, filesystem and authority for **every** artifact, is **§2.13.3** |
| `/var/lib/freedom-sheet-writer/**` | see **§2.13.3** | see §2.13.3 | the durable journal hierarchy. Root-owned directories the writer may traverse and never write; an append-only journal file it owns; an immutable generation seal it does not |
| `…/coordinator/bin/freedom-journal-admin` | `root:root` | `0755` | **new in revision 5.** The second `sudo`-permitted entry point, for the privileged journal lifecycle (§2.13.7). It is a separate executable from `migration-authority` because it is the only thing that runs **as root**, and a `Cmnd_Alias` that mixed the two would widen the authority of both |
| `/etc/freedom-blades/sheet-writer.env` | `root:freedomsheet` | `0640` | the relocated Google service-account credential. The bot's environment file loses it |
| `/opt/freedom-blades/sheet-writer` | `root:root` | `0755` | **new in revision 12.** The writer's deployment root, outside the group-writable `platform` tree of H-1, and the root of §2.13.2c's manifest. Partitioned into region **S** (reviewed source) and region **D** (hash-pinned dependencies) by §2.12.5a, with **no third region** |
| `/opt/freedom-blades/coordinator/source.git` | `root:root` | **`0700`** | **new in revision 12; this is remediation R11-A.** A **bare** Git object store holding the reviewed commits, refreshed only by root from an authenticated origin. It is `0700` rather than `0755` deliberately: no service identity may read it, so no service identity can learn which objects a future deployment will trust, and none can write one. **It is not a worktree**, and §2.12.5a resolves objects in it by object id only |
| `/opt/freedom-blades/coordinator/staging` | `root:root` | `0700` | **new in revision 12.** Where a deployment is assembled and verified before it is installed. Removed by the deploy step in a `finally`; residue refuses the next deployment rather than being cleaned, on the §2.13.2b precedent |
| `/etc/freedom-blades/approved-source-revision` | `root:root` | **`0444`** | **new in revision 12.** The **approved-revision record** `APR`: the commit and tree object ids and the source-manifest digest a review approved, installed out of band by root. World-readable because it contains no secret and the writer compares against it; **writable by root alone**, which is the whole of its integrity — residual **R-5.0-15** |
| `/etc/freedom-blades/sheet-writer.provenance` | `root:root` | `0444` | **new in revision 12.** The **provenance record** `PVR` the deploy step writes at **D8**. It is deliberately **outside** the deployed root, so `deployment_manifest_digest()` does not cover a file containing its own value and no cycle exists |
| `/etc/sudoers.d/freedom-migration-coordinator` | `root:root` | `0440` | `sudo` refuses a group- or world-writable drop-in anyway; stated so a deploy cannot get it wrong quietly |
| `/etc/sudoers.d/freedom-journal-admin` | `root:root` | `0440` | **new in revision 5**, and deliberately a **separate file** so that revoking journal authority and revoking cutover authority are two independent acts (§2.13.7) |

**The deploy step is a root action** — and revision 11's one-sentence account of
it is **withdrawn**. It read: *"`migration-authority` is copied from the reviewed
repository commit into the root-owned tree, and the operations document requires
the recorded SHA-256 of each deployed file to be compared against that commit."*
**That sentence describes a procedure, not a control.** It named no artifact that
carries the reviewed commit's identity, no place the comparison's trusted side
comes from, and no step that refuses when the comparison is skipped — so an
operator who omitted it deployed bytes, computed their digest, created a
generation and passed **W11** thereafter, with nothing anywhere recording that
the comparison had not happened. That is security-review finding **P5.0-SR1**,
and **§2.12.5a replaces the sentence with a fail-closed contract** in which the
trusted side is produced from an immutable Git object, the approval arrives out
of band, and **omitting the provenance step refuses rather than defaults**.

**H-1 is still worked around rather than fixed, and the boundary is now sharper
about how.** A compromised service process can still edit the *worktree* at
`/opt/freedom-blades/platform`. What §2.12.5a adds is that **nothing in the
deploy path reads that worktree** — the reviewed bytes come out of the root-owned
object store at `…/coordinator/source.git`, which is `0700 root:root`, and
`JNL-51` case (h) asserts by syscall trace that no path under the worktree is
opened during a deployment. **That the repository is writable by a service
identity at all is still raised as D5.0-12 / OD-65**, because it is a pre-existing
condition wider than this package.

#### 2.12.5a The deployment contract — reviewed-source provenance, fail-closed. **New in revision 12; this is remediation R11-A**

**The defect, conceded before its replacement.** Revision 11 had one function,
`deployment_manifest_digest()`, and three consumers: the deploy step recorded it,
the operator supplied it, and **C0** compared the supplied value with a fresh
computation over the **same live bytes**. That establishes that the deployment
has not changed since somebody looked at it. **It establishes nothing about where
those bytes came from.** No artifact, no registration input and no activation
precondition named a reviewed commit, and no step refused when the separate
comparison against that commit was omitted — so an operator who skipped it left
**no durable indication anywhere** that it had been skipped, and a service
identity that had rewritten a source tree through **H-1** would have been
deployed, digested, sealed and re-verified at **W11** for the life of the
generation. The gap matters because the deployed program is **root-owned and
carries authority to change the authority plane and administer journal
evidence**, which is precisely the separation the control was claimed to make.

**What this section adds, in one sentence.** A deployment is admissible only when
**three facts from three different sources agree**, and a generation is
registrable only when a **fourth, in PostgreSQL**, agrees with them.

##### The four facts, and why each comes from somewhere the others do not

| | Fact | Where it comes from | Why it is independent |
|---|---|---|---|
| **APR** | the **approved revision** — `source_commit`, `source_tree_id`, `source_manifest_digest`, the review reference, the approver and the approval time | `/etc/freedom-blades/approved-source-revision`, `root:root 0444`, installed **out of band** by root from the accepted gate package | it is not derived from any deployed byte and not from the object store. It is the only place a human's *approval* enters the algorithm, and nothing in the deploy path can write it |
| **TM** | the **trusted manifest** — `source_manifest_digest()` computed over the **Git object bytes** of `APR.source_commit`'s tree | `/opt/freedom-blades/coordinator/source.git`, a **bare** store, `root:root 0700`, addressed **by object id only** | Git objects are content-addressed and the store is unreachable by every non-root identity. **No ref, branch, tag, `HEAD` or symbolic name is resolved anywhere in this algorithm**, so moving a ref changes nothing |
| **SM** | the **deployed source manifest** — `deployed_source_manifest_digest()` over the live installed bytes, projected onto the facts Git can express | the deployed root and the deployed unit and drop-ins | it is the reality the writer will actually execute, computed the same way the writer computes it at **W11a** |
| **ASR** | the **approved-revision row** in `approved_source_revisions` | PostgreSQL, inserted by the coordinator under **A8**, append-only under **A9** | it is the one copy of the provenance an actor holding only host authority did not write, on exactly the **F-1b** precedent |

**`APR`, `TM` and `SM` must be equal at deployment and again at every
`init-generation`; `ASR` must exist and agree at registration. Any disagreement,
and any absence, is a refusal.**

##### `source_manifest_digest()` — the exact bytes, and why they are not `deployment_manifest_digest()`'s

`deployment_manifest_digest()` (§2.13.2c) covers **path, mode, uid, gid, size and
content** — facts about a *deployment*. **Git records none of uid, gid or the full
permission bits**, so a manifest computed from a Git tree cannot reproduce them,
and a comparison that pretended otherwise would fail on every correct deployment.
The two functions are therefore **different functions over overlapping bytes**,
and both are named, specified and separately tested.

`source_manifest_digest(entries)` is SHA-256 over the canonical, typed,
length-delimited, schema-versioned encoding `application/idempotency.py`'s
`canonical_request_hash` establishes, over a list **sorted by deployed relative
name**:

| Field per entry | Detail |
|---|---|
| `deployed_name` | the **same fixed relative names §2.13.2c uses** — a path relative to the deployed root, or `unit:freedom-sheet-writer.service`, or `unit.d:<name>` |
| `source_path` | the path **inside the reviewed tree** the entry is taken from |
| `entry_class` | `regular` \| `executable` \| `symlink` — the three states a Git tree distinguishes, and the only mode facts both sides can produce |
| `content_digest` | SHA-256 over the content bytes: the blob's bytes on the trusted side, the file's bytes on the deployed side. For a symlink, over the target string |

with `source_manifest_format_version` as the first field, so a later definition is
a visible, versioned change rather than a silent drift.

**Deliberately excluded, and why:** uid, gid and the numeric mode — Git does not
record them, and they are checked **separately and exactly** against the
deployment map at **D7**; timestamps and inode numbers — they differ between two
byte-identical deployments; and everything in region **D** below, which has its
own binding.

**Why the SHA-256 matters and not only the commit id.** A Git object id is a
SHA-1 digest, and SHA-1 is no longer collision-resistant. **`APR` therefore
carries `source_manifest_digest` as well as `source_commit` and `source_tree_id`,
and `D3` refuses unless the manifest recomputed from the store's object bytes
equals it.** A substituted object that collided under SHA-1 would have different
content bytes and therefore a different SHA-256, so the binding does not rest on
the weaker digest. This is stated here rather than assumed, because a design that
binds to "the commit" and says nothing about SHA-1 has assumed it.

##### The deployment map — which files are deployed, and with what ownership, is itself reviewed

`infra/deploy/sheet-writer.deployment-map` (and one for the coordinator) is a
canonical file **inside the reviewed tree**, listing for every deployed artifact
its `source_path`, its absolute `deployed_path`, its `entry_class`, and the
**owner, group and mode** the deploy must apply. Because it is an entry in the
source manifest, **which files get deployed and who owns them is a reviewed fact
rather than a deploy-time argument.** An operator cannot add a file to a
deployment without changing the map, which changes `TM`, which requires a new
approval.

##### The two regions, and the closed partition

| Region | What it is | How it is bound |
|---|---|---|
| **S — reviewed source** | every path the deployment map names, including the unit file and its drop-ins | `TM` = `SM`, and the ownership/mode facts against the map |
| **D — pinned dependencies** | the interpreter and third-party distributions under `…/venv` | `dependency_lock_digest`: the hash-pinned lock file lives in region **S**, and **D4** refuses on any distribution whose artifact digest is not the lock's, on any **extra** distribution and on any **missing** one |

**There is no third region.** A file in the deployed root belonging to neither is
a refusal at **D5** and again at **C0**. This is what stops the failure that a
whole-tree digest cannot see: deploying the reviewed files correctly *and adding
one more*.

##### Algorithm D — deploy. Executed by root, and by nothing else

**No step is performed by this remediation.** The refusal family
`DEP-01 … DEP-09` belongs to the deploy step alone; it is neither the writer's
`SW-Jxx` family nor the coordinator's `J-xx` family, because the deploy step is
neither actor.

| Step | Action | Refusal |
|---|---|---|
| **D0** | Read **`APR`**. Refuse unless it is present, `root:root`, mode `0444`, structurally valid at a supported `format_version`, and its `component` is the one being deployed. **An absent or unreadable approval record is a refusal, never a default** — that is the whole of what P5.0-SR1 says was missing | **`DEP-01`** |
| **D1** | Refuse unless `…/coordinator/source.git` is `root:root 0700`, is a **bare** store, and holds `APR.source_commit` as a **commit** object. The store is opened with a fixed `--git-dir`, no worktree, and directory discovery disabled, so no ambient repository can be picked up. **No ref, branch, tag, `HEAD` or `@{…}` expression is resolved at any point** | **`DEP-02`** |
| **D2** | Read the commit object; refuse unless its root tree id equals `APR.source_tree_id` | **`DEP-03`** |
| **D3** | Extract the reviewed tree into `…/coordinator/staging/<commit>` (`root:root 0700`) **from the object store alone**; read the deployment map **from that extraction**; compute **`TM`** = `source_manifest_digest()` over region **S**. **Refuse unless `TM` equals `APR.source_manifest_digest`.** This is the check that does not rest on SHA-1 | **`DEP-04`** |
| **D4** | Install region **D** into the staging tree from the pinned lock; refuse on a distribution artifact whose digest is not the lock's, on an extra distribution, or on a missing one | **`DEP-05`** |
| **D5** | Refuse unless the staging tree's file set is **exactly** region S ∪ region D. **No unaccounted file** | **`DEP-06`** |
| **D6** | Apply the deployment map's owner, group and mode to every region-S artifact and the fixed `root:root` policy to region D; install the tree at the deployed root; install the unit file and its drop-ins at their deployed paths; `systemctl daemon-reload` | **`DEP-07`** |
| **D7** | Over the **live deployed bytes**, compute **`SM`** = `deployed_source_manifest_digest()` and **`DD`** = `deployment_manifest_digest()` (§2.13.2c, unchanged). Refuse unless `SM` equals `TM` **and** every uid, gid and mode equals the deployment map's. **A refusal here removes the deployed tree and restores its predecessor**, so a deployment that cannot prove its provenance does not survive the command that made it | **`DEP-08`** |
| **D8** | Write **`PVR`** to `/etc/freedom-blades/<component>.provenance` as `format_version`, `component`, `source_commit`, `source_tree_id`, `source_manifest_digest` = `TM`, `deployment_manifest_digest` = `DD`, `dependency_lock_digest`, `approved_by`, `approved_at`, `review_reference`, `deployed_at`, `deployed_by`; `fsync`; atomic `rename`; `fsync` the directory. **If it cannot be written, the deployment is rolled back**: there is no deployed state without a provenance record | **`DEP-09`** |

**`PVR` is outside the deployed root, and that is load-bearing.**
`deployment_manifest_digest()` covers `/opt/freedom-blades/sheet-writer/` and the
unit and drop-ins; `PVR` lives in `/etc/freedom-blades/`, so **no digest covers a
file containing its own value** and §2.13.5a's acyclicity property (stop
condition **10g**) is preserved rather than argued.

**Cleanup.** The staging directory is removed in a `finally`. A failed cleanup is
a distinct non-zero exit that **names the residue by absolute path and refuses
the next deployment rather than cleaning it** — the same choice, for the same
reason, that §2.13.2b makes for `…/probe`.

##### Where the provenance is then consumed, fail-closed at each point

| Consumer | What it does | Refusal |
|---|---|---|
| **`init-generation` C0**, root | reads `PVR` and `APR`; refuses if either is **absent**, malformed, wrongly owned or wrongly moded; refuses unless `PVR` and `APR` agree on all three provenance values; **recomputes `TM` from the object store** and refuses on disagreement; **recomputes `SM` over the live deployed bytes** and refuses on disagreement; refuses unless `PVR.deployment_manifest_digest` equals the `DD` **C0** already computes; and refuses unless the operator's supplied `--source-commit` equals `APR.source_commit`, the supplied string then being discarded exactly as the supplied digest is | §2.13.5a **C0**; §2.13.6 **J-26** |
| **the seal body `SB`**, at **C3** | carries `source_commit`, `source_tree_id`, `source_manifest_digest` and `approved_revision_reference`, so the provenance is **chain-anchored**: altering it changes `seal_body_digest`, which changes the derived genesis record, which **W13** compares byte for byte against record 0 | §2.13.6 **J-24** |
| **the writer, at W11a** | recomputes `deployed_source_manifest_digest()` over its own deployed bytes and compares with `SB.source_manifest_digest`; reads `PVR` and compares its three provenance values with `SB`'s | **`SW-J26`**, **`SW-J27`** |
| **`V-R`, at registration** | refuses unless a row in `approved_source_revisions` matches `(component, source_commit, source_tree_id, source_manifest_digest)`; the inserted generation row carries a **`NOT NULL` foreign key** to it | §2.13.6 **J-28** |
| **activation** | needs a registered generation for `fenced_writer = 'sheet_writer'` (§2.13.5b **C-c**), and no such row can exist without the foreign key above. **So an unprovenanced deployment cannot reach activation at all**, and the refusal is a schema constraint rather than a procedure step | logical schema §3.7, §3.8 |

##### What the writer can and cannot establish about provenance

Stated because unequal verifiers are only safe when the inequality is written
down, and because `0700` on the object store means the writer genuinely cannot
read it.

| | Writer (**W11a**) | Root (**D3**, **C0**) | Coordinator (**V-R**) |
|---|---|---|---|
| its own deployed bytes match the sealed source manifest | **yes** | yes | yes, transitively |
| that manifest was produced from the approved commit's Git objects | **no — it cannot read the store** | **yes** | no |
| the approved commit is one a review approved | **no** | reads `APR`, whose integrity is root ownership — **R-5.0-15** | **yes**, against `approved_source_revisions` |
| an actor holding **A5** substituted the whole set — store, `APR`, `PVR`, deployment | **no** | **no** | **yes**, unless that actor also holds **A8** — **R-5.0-15** |

##### What this contract does not do

- **It does not fix H-1.** The worktree stays group-writable; what changes is
  that nothing in the deploy path reads it (`JNL-51` case (h)).
- **It does not authenticate `APR` cryptographically.** Its integrity is root
  ownership and mode. An actor holding **A7** writes it, and an actor holding
  **A8** can register a generation against a revision it approved itself. That is
  **R-5.0-15**, recorded as a residual and **not** described as a refusal; the
  signed alternative is routed as **D5.0-13 / OD-66 option A-3** and is not
  adopted.
- **It does not prove a human read the commit.** It binds the deployment to what
  the approval record names, and makes disagreement and omission refuse. Whether
  the named commit was actually reviewed is a governance fact carried by
  `review_reference`, not a property this algorithm can establish.
- **It does not make the deployment reproducible.** Region D is pinned by
  artifact digest, not built from source; a distribution whose published artifact
  changes under a fixed version is refused at **D4**, which is detection, not
  prevention.

#### 2.12.6 Why a compromised service process cannot become the coordinator

One row per vector the handoff names. Each says what stops it and, where
something is unverified, says that instead of asserting.

| Vector | What stops it | State |
|---|---|---|
| **Change uid to `freedomcoord`** | `setuid(2)` needs `CAP_SETUID`. No unit grants it; all three run as unprivileged users. `freedom-web` and `freedom-worker` set `NoNewPrivileges=true`, so they cannot gain it through a setuid binary either | **`freedom-bot` sets none of that (H-2).** The design *requires* the hardening directives to be added to that unit, which is a change to a live unit and is D5.0-12 / OD-65 |
| **Use `sudo` to become it** | No service identity is in `sudo` and the drop-in names `foundry` only | **Partly verified.** `getent group sudo` was read. `/etc/sudoers.d/` **could not be read** without privilege on 2026-08-29 and is recorded as a check not run — the Security Reviewer must enumerate it |
| **Use a setuid binary** | A `find / -perm -4000` audit is required evidence | **Not run.** A partial listing of `/usr/bin`, `/usr/sbin`, `/bin`, `/sbin` was taken and showed the distribution's usual set; that is not an audit and is not offered as one |
| **Alter the code the coordinator executes** | The root-owned deployment path (§2.12.5), **the fail-closed reviewed-source provenance contract of §2.12.5a** — an approval record root alone can write, a trusted manifest computed from Git object bytes in a `0700 root:root` store, a closed two-region partition, and a provenance record whose **absence refuses** at `init-generation` **C0** — and `sudo`'s single fixed executable path | **This is the vector revision 3 failed** (H-1), and revision 11 closed it with a digest whose only source was the bytes being checked, which is security-review finding **P5.0-SR1**. It is now closed by a binding to an **immutable reviewed Git object**, with `JNL-51` case (g) proving that omitting the provenance step prevents activation and `JNL-51` case (h) proving by syscall trace that the deploy path reads no file in the group-writable worktree |
| **Use the `freedomjournal` group `freedomcoord` shares with `freedomsheet`** | Nothing in this design decides who a process **is** from a group. Peer authentication reads the uid from `SO_PEERCRED`; `pg_ident.conf` maps a system **user** and names `freedomcoord` alone; the `sudoers` rule names `foundry` as invoker and `freedomcoord` as target. The group's entire grant is `r-x` on `…/journal` and `r--` on the seal — **no write bit anywhere**, and no access to `…/archive` | **New row in revision 12.** Revision 11 claimed instead that no such shared group existed, which was false — security-review finding **P5.0-SR2**. §2.12.2 now carries the canonical membership and `JNL-52` tests all four identities positively and negatively |
| **Inject through `PYTHONPATH`, `PYTHONHOME`, the current directory or a shadowing module** | `env_reset` + `!setenv` + `secure_path` at the `sudo` boundary; `unset` in the wrapper; `python -I -P`; a working directory the services cannot write | Verifiable directly: the `diagnostics` subcommand prints the effective `sys.path`, and the test asserts **no entry on it is writable by `discordbot`, `freedomweb` or `freedomsheet`** |
| **Steal the coordinator's database credential** | There is none. `PASSWORD NULL` plus `pg_hba` `reject` for every non-peer method | Verified by construction, and tested by attempting a password connection |
| **Reach the role over the socket as another uid** | `pg_ident` maps exactly one system user; the socket directory being world-reachable (H-3) is irrelevant to who the peer *is* | Tested per runtime identity |
| **Reach the role over TCP** | four `reject` lines above any permissive rule | Tested from loopback, with and without a password |
| **Forge evidence without being the coordinator** | the runtime role holds **nothing** on `migration_quiescence_evidence` (logical schema §4.3) | Recorded as **unconstructable**, with the `has_table_privilege` proof rather than a test that tries and fails |

#### 2.12.7 Provisioning, audit, revocation, recovery and rotation

| Lifecycle event | Procedure | Who |
|---|---|---|
| **Provision** | **Restated in revision 12 so the group order is explicit and the deployment step is the contract rather than a comparison.** In order: create the group `freedomjournal`; create the OS users `freedomcoord` and `freedomsheet` with their primary groups; add **exactly those two** to `freedomjournal`; assert `getent group freedomjournal` lists exactly two members and that `id` for every identity in §2.12.2 matches that table **before anything else runs** (`JNL-52`); create the root-owned `…/coordinator/source.git` store and fetch the reviewed commit into it from an authenticated origin; install the approved-revision record `APR`; run **Algorithm D** of §2.12.5a, which deploys the root-owned tree and writes the provenance record or refuses; install both `sudoers` drop-ins with `visudo -c -f`; create the role; apply the extended grants template; add the `pg_hba` and `pg_ident` lines; `SELECT pg_reload_conf()` — a **reload**, not a restart; insert the approved-revision row; then run the denial matrix and the §2.12.2 membership matrix before the first use | root and the database superuser, from the operations document. **No step is performed by this remediation** |
| **Audit — membership** | **New in revision 12.** `getent group` for every group in §2.12.2 and `id` for every identity in it, compared against that table. Re-read after any account, group or deployment change, and after any restore. **An unexpected member is a finding, not a difference** | Operations Owner |
| **Audit — provenance** | **New in revision 12.** `APR`, `PVR` and the object store's ownership and mode read; `TM` recomputed from the store; `SM` recomputed over the deployed bytes; the three compared, and compared with the registered `approved_source_revisions` row. This is the same computation `init-generation` **C0** performs, run deliberately rather than incidentally | Operations Owner |
| **Audit** | three independent records that must agree: `sudo`'s `log_output` I/O log and journald entry naming the invoking uid; PostgreSQL's connection log naming the authenticated role; and the `audit_events` row naming the platform account. The operations document requires them to be cross-read after every authority change | Operations Owner. **`log_connections` is a `postgresql.conf` setting whose current value was not verified** and is a check not run |
| **Revoke — group membership** | **New in revision 12.** Removing an identity from `freedomjournal` removes its read of `…/journal` and the seal. For `freedomsheet` that is **fail-closed and drastic**: the writer refuses at **W2** with `SW-J17` and dispatches nothing. It is listed because it is a revocation the table previously left unstated, not because it is a recommended act | Operations Owner |
| **Revoke** | any one of three, each fail-closed and each sufficient: remove the operator from the `sudoers` drop-in; `ALTER ROLE freedom_migration_coordinator NOLOGIN`; remove the `pg_ident` line and reload. **Revocation can only prevent cutovers, never enable one**, because activation requires an `INSERT` no other principal may make | Operations Owner |
| **Recover** | a broken mapping means no cutover can be activated — the closed direction. Restoring it is a root and superuser action on two configuration lines; **no service process can perform it**, which is the property that makes the failure safe | Operations Owner |
| **Rotate — the approved revision** | **New in revision 12.** A redeployment is a new approval: insert the new `approved_source_revisions` row, install the new `APR`, fetch the commit into the store, run Algorithm D, then **rotate the journal generation** — row **J-22** already requires that, because the deployment digest changes. Both intermediate states refuse rather than degrade: an `APR` newer than the deployment refuses at **C0**, and a deployment newer than the seal refuses at **W11**/**W11a** | Operations Owner |
| **Rotate** | there is no secret, so rotation means changing *which OS account maps to the role*: add the new `pg_ident` line, reload, prove the new account authenticates and the old is refused, remove the old line, reload, re-prove. Both intermediate states are testable | Operations Owner, recorded in the change log |

#### 2.12.8 The option comparison this section is choosing between

| | Option | Isolation from service identities | Cost | Verdict |
|---|---|---|---|---|
| **I-1** | **A dedicated `freedomcoord` OS account** as specified above | Complete, and provable one identity at a time | two OS accounts, a `sudoers` drop-in, two PostgreSQL configuration lines, a root-owned deployment path, hardening on a live unit | **Recommended.** It is what the handoff asks for |
| **I-2** | **Map the existing `foundry` operator account instead** | Adequate *against service identities* — no service can become `foundry` — and **absent against operator error and against anything else `foundry` runs**, including an interactive shell. `foundry` is in `sudo`, so it can already reach every identity on the host | no new OS account; still needs the deployment path, because H-1's group writability is what lets a service edit code `foundry` would run | **Weaker, and honest about it.** Listed because it is the cheapest thing that satisfies the literal requirement, and because a reviewer should see it rejected rather than ignored |
| **I-3** | **Keep one shared principal** | none | none | **This is the P5.0-R4 finding.** Listed for completeness, not recommended |

---

### 2.13 The dispatch journal — the durable storage and lifecycle contract P5.0-R5 requires

Revision 4 specified this control in one table row and one clause. Revision 5
replaced the row with a contract, and the re-review found that the contract was
**not implementable as written**. Revision 6 rewrites the parts that were not,
and leaves the rest where revision 5 put it.

#### 2.13.1 What was wrong, stated before it is fixed

**Revision 4's defects, and their corrections, retained.**

| # | Revision 4 said | The fact |
|---|---|---|
| 1 | the journal lives at `/run/freedom-sheet-writer/dispatch.journal` | **`/run` is a separate volatile `tmpfs` mount.** Read from `/proc/mounts` on this host: `tmpfs /run tmpfs rw,nosuid,nodev,noexec,relatime,size=806112k,mode=755,inode64` (§8.1 **H-4**). It is emptied at every boot |
| 2 | `chattr +a` is available, "ext4 confirmed" | **The confirmation was of a different path.** `df -T /opt/freedom-blades` reported ext4; nothing was read about `/run`, and a filesystem type is in any case not a runtime capability test |
| 3 | the failure direction is over-reporting, which is safe | **Only while the file survives.** A reboot, a replacement or a missing file turns *unknown history* into an *apparently empty unresolved set*, which is the answer that lets the coordinator record `dispatch_journal_clear`. The failure direction inverted from safe to unsafe exactly where it mattered |
| 4 | "nothing in the fence depends on the journal being complete" | **False while `dispatch_journal_clear` is a required fence method.** §2.13.9 |

**Revision 5's defects. These are what revision 6 exists to fix, and each is
conceded rather than argued with.**

| # | Revision 5 said | The fact | Fixed in |
|---|---|---|---|
| 5 | the seal carries `genesis_record_digest`, and the genesis record's `prev_hash` is `seal_digest` | **The two values depend on each other and neither can be computed first.** `seal_digest` is a digest of a file that contains `genesis_record_digest`, which is a digest of a record whose `prev_hash` is `seal_digest`. **No generation can be created as specified.** The construction was not merely awkward; it does not exist | **§2.13.5a**, which splits the seal into a **body** and a **binding section** and states a strictly ordered, acyclic construction |
| 6 | the seal is `root:freedomcoord 0440`, so `freedomsheet` "cannot even read it" — while §2.13.6 rows **J-04**, **J-05**, **J-11** and **J-17** required the *writer* to validate the seal at start | **A process cannot validate a file it cannot open.** The permission model and the startup contract described two different designs | **§2.13.3**, which creates the `freedomjournal` group, tightens `…/journal` to `root:freedomjournal 0750` and makes the seal `root:freedomjournal 0440` — read-only for the writer, and *narrower* for every other identity than revision 5 was — and **§2.13.5b**, which states which checks are the writer's and which are the coordinator's |
| 7 | the capability probe is a `root:root 0600` file inside a directory `freedomsheet` cannot write | **Every negative case fails on discretionary permissions before append-only is reached.** The probe would have "passed" identically on a filesystem with no `FS_APPEND_FL` support at all, which makes it evidence of nothing | **§2.13.2a**, a four-stage probe with a **control stage** whose job is to prove that ordinary permissions are *not* the reason for any later refusal |
| 8 | at every writer start "the writer re-runs the unprivileged half of the probe against the live journal" — a non-append write, an `O_TRUNC` open, an `ftruncate` | **If `+a` has disappeared, those operations succeed** and corrupt or destroy the live evidence the check exists to protect. A startup check that can destroy what it is checking is not a check | **§2.13.5b V-W**, whose startup path performs **no** destructive operation against live evidence; the destructive matrix runs only against disposable artifacts (§2.13.2a) |
| 9 | `CHECK (append_only_verified)` makes the probe "enforced by a constraint rather than by a procedure step somebody could skip" | **A `CHECK` constrains a supplied Boolean to `true`.** It proves that the coordinator supplied `true`; it cannot prove a host probe ran, and describing it as proof was exactly the kind of claim stop condition 10b forbids | **§2.13.8a**, which withdraws the column, replaces it with a probe **report digest** bound into the seal, and states line by line what PostgreSQL enforces and what it merely records |

**Revision 6's defects. These are what revision 7 exists to fix, and each is
conceded before its replacement is presented.**

| # | Revision 6 said | The fact | Fixed in |
|---|---|---|---|
| 10 | Algorithm C step **C1** built the probe report from **stages 1–3**, while §3.7, §2.13.8a and the evidence contract said `append_only_probe_digest` covered **four stages**; Stage 4 ran *"once at deployment, not at provisioning"* | **A seal made immutable at revision 6's step C9 cannot acquire a stage that runs afterwards.** The digest was described as covering bytes it did not contain, which is the same class of claim stop condition 10b already forbids | **§2.13.2a**, which moves Stage 4 **before** the report is built, inside the same `verify-capability` invocation, and states the lifecycle choice and the option not taken |
| 11 | falsification row **F-1**: *"any byte of the seal file"* is refused by the writer, *"without any database"* | **Changing only `BND.sealed_at` passed every V-W step.** W3 hashed the body, W5 validated the derived genesis digest, and no writer step authenticated that field. The coordinator caught it through the whole-file `seal_digest`; the writer did not | **§2.13.5a C2/C7/C8** (the field is withdrawn and the binding's structure moves into the chain-authenticated body), **§2.13.5b** (a field-by-field binding authentication table) and **§2.13.5c** (F-1 split by attacker class, four new independent cases) |
| 12 | `JNL-32` re-ran a full writer start with `+a` **absent** and asserted the journal byte-identical *"except for that record"* | **W9 refuses with `SW-J06` before W17 is reached**, so no `startup` record can exist in that branch. The test expected a state the algorithm makes unreachable | **§2.13.8**, `JNL-32a` (successful start, `+a` present, exactly one appended record) and `JNL-32b` (absent flag, refusal at W9, no write-mode open at all, evidence byte-for-byte unchanged) |
| 13 | the R5 handoff document contained merged and truncated verification bullets and ended mid-sentence | a review record that cannot be read is not a review record | **`phase-5-0-remediation-r6-handback.md`**, complete Markdown, `git diff --check` clean; the corrupt text is preserved only in Git history |

**Revision 7's defects. These are what revision 8 exists to fix, and each is
conceded before its replacement is presented.**

| # | Revision 7 said | The fact | Fixed in |
|---|---|---|---|
| 14 | Algorithm C step **C0** refuses unless `verify-capability` *"passed in this invocation, all four stages"*, with a report whose `writer_deployment_digest` equals the supplied one — and step **C1** runs those stages and builds that report | **An ordered algorithm cannot validate an output before producing it.** C0 could not be satisfied on a first pass, so revision 7's Algorithm C had **no executable order at all**; any implementation that appeared to work would have been running the probe twice or reading a report from a previous invocation, neither of which the algorithm authorizes | **§2.13.5a**, which keeps only pre-probe facts in **C0**, leaves **C1** the single creation point, adds **C2** for every result-dependent check before any persistent artifact, renumbers the algorithm **C0 … C13**, and adds a value-dependency table plus `JNL-46`/`JNL-47` |
| 15 | Stage 4 case **S4-2** appends *"to a path **outside** `ReadWritePaths=` but inside `ProtectSystem=strict`'s read-only tree"* and requires `EROFS` | **The path was never named, and it was never proved writable by `freedomsheet` without the sandbox.** Every directory in §2.13.3 except the arena denies that identity, so the refusal would have been attributable to ordinary permissions — **the exact defect Stage 1 exists to prevent, left in the one stage that runs under systemd** | **§2.13.2a**, which names `…/probe-ro/s4-2.target`, gives it a full lifecycle, adds the positive control **S4-0** on that exact file outside any unit, classifies `EACCES` as `inconclusive` and a success as `failed`, and adds `JNL-48` |
| 16 | falsification **class 1** cannot clear `FS_APPEND_FL` yet *"reaches every row below except F-1b"*; **F-2** is assigned class 1 with a note conceding record-0 rewriting needs class 2 | **The class column had drifted into recording which detector catches an injected mutation rather than what an attacker must hold to construct it.** A class that cannot clear `+a` cannot rewrite record 0, replace the journal inode in a root-owned directory, alter a `+i` archive, write the deployment path, rewrite `/etc/machine-id` or touch PostgreSQL | **§2.13.5c**, rewritten: an eight-capability register, a per-row minimum capability with detector reach and residual, F-2 corrected to `K3`, F-7 corrected in the opposite direction, not-constructible pairings named with their controls, and `JNL-49`/`JNL-50` |
| 17 | implementation-plan §20 identified revision 5 / R5 as the active handoff | a controlled document naming an obsolete brief is a governance defect, not a typo: it is what a later reader would act on | **implementation-plan §20**, corrected by the reviewer to revision 7 / R7 and **preserved and extended here** to name revision 8 as the submitted response; and the five registers, which all name **R7** as the active cycle |

**Revision 8's defects. These are what revision 9 exists to fix, and each is
conceded before its replacement is presented.**

| # | Revision 8 said | The fact | Fixed in |
|---|---|---|---|
| 18 | Algorithm C's value table asserts *"In every row, produced < validated ≤ consumed"*, with `writer_deployment_digest` produced before C0, validated at **C0** (presence) and **C2** (equality with `PR`), and first consumed at **C1** | **The first row of the table contradicts the sentence above it.** C1 consumes the value; C2 validates it; `C1 < C2`. And the C2 comparison was not a validation in any case: `PR`'s copy of the digest **came from the supplied value**, so comparing them is a tautology that passes for any string. Nothing in revision 8 ever compared the supplied digest with the **deployed bytes** | **§2.13.2c**, which defines the digest's computor, its exact manifest and when it becomes final; and **§2.13.5a**, where **C0 computes and compares** it against the deployment before C1 consumes it, **C2** keeps a consistency check and adds a second computation, and the universal inequality is replaced by invariants **I-1 … I-5**. `JNL-46` 1 → **5** cases |
| 19 | `JNL-47` asserts that a failure injected in the privileged cleanup leaves *"no `…/probe` or `…/probe-ro` residue"*, while `JNL-48(d)` plants an artifact *"made undeletable"* and asserts it is **named as residue** and makes `init-generation` refuse at **C0** | **One injected failure was required to leave the host in two mutually exclusive states.** Both tests cannot pass against one implementation, so the evidence contract was unsatisfiable. Revision 8 also specified **two** behaviours for the next invocation — `verify-capability` cleaning residue as an explicit first step, and `init-generation` refusing while it exists — which are a self-cleaning path and a refusing path for the same state | **§2.13.2b**, one state machine with three states, in which *"no generation artifact"* is unconditional and *"no transient residue"* is conditional on cleanup success; and a single next-invocation behaviour — **refuse for operator recovery**. The automatic clean-and-reuse step is **withdrawn**. `JNL-47` 5 → **6** cases |
| 20 | the capability register gives **K3** as *"a holder of `CAP_LINUX_IMMUTABLE` — root, or a process granted that capability"* and **K4** as *"root with `CAP_LINUX_IMMUTABLE`"*, with the archive `0750 root:freedomcoord` and its files `0440` | **`CAP_LINUX_IMMUTABLE` permits flag control and confers no discretionary access whatever.** A non-root process holding it can clear `+i` on an archived file and then receive `EACCES` on the `O_WRONLY` open, because the file is `0440` and root-owned inside a directory it may not traverse. The register recorded an **achieved ability** — “archive write” — where it should have recorded the **privileges needed to achieve it**, and the same conflation ran through F-2, F-4, F-5 and the `JNL-49`/`JNL-50` cases | **§2.13.5c**, rewritten into **nine independently constructible authorities** with a per-row minimum **combination**; **F-2 → `A1 + A2`**, **F-4 → `A1 + A4`**, **F-5 → `A1 + A3`**; and `JNL-49`/`JNL-50` at ten cases each, executed under a flag-control-only, non-root capability set |
| 21 | falsification row **F-7** records the host identity as refused by *"the **coordinator**, against the registered row — which is not on the restored tree"*, with `J-16` at **C-d** | **The registered row carries the same `host_machine_id` the seal does.** If **A6** rewrites `/etc/machine-id` to the recorded value, all three copies agree and **neither W10 nor C-d has anything to disagree with**. Storage outside the restored tree creates no mismatch when the value stored there is the forged one. The device and inode differences revision 8 leaned on are **incidental** — they are refused by **F-5**/**F-10**/**F-11** as *inode* findings, and a restore that preserves them produces no refusal at all. This is a **10h** violation: a refusal claimed for an actor whose algorithm contains no step that detects it | **§2.13.5c**, where F-7's outcome becomes a **residual** rather than a refusal, and **R-5.0-13**, which names the independent operational evidence that actually remains. §2.13.5b's verifier table, §2.13.6 **J-23**, `JNL-40` (1 → **2** cases), `JNL-49` case 3 and logical schema §3.7/§3.7.1/§9 follow. Stop condition **10h** is extended so the class is guarded rather than merely corrected |

**Revision 9's defects. These are what revision 10 exists to fix, and each is
conceded before its replacement is presented.**

| # | Revision 9 said | The fact | Fixed in |
|---|---|---|---|
| 22 | the authority register gives **A1** as *"flag control — `FS_IOC_SETFLAGS` setting or clearing `FS_APPEND_FL` / `FS_IMMUTABLE_FL` on an inode the holder can already reach and open under DAC"*, with minimum holder **`CAP_LINUX_IMMUTABLE`**; and every root-owned-inode row is written as **`A1 + A3`** or **`A1 + A4`** | **`FS_IOC_SETFLAGS` has two independent permission requirements and revision 9 recorded one.** The caller's effective UID must equal the inode's owner **or** it must hold **`CAP_FOWNER`**; changing `FS_IMMUTABLE_FL` or `FS_APPEND_FL` requires **`CAP_LINUX_IMMUTABLE`** *in addition*. `CAP_DAC_OVERRIDE` is not a substitute for the owner check, because the owner check is not a discretionary-access check. So **a non-root process holding only `CAP_LINUX_IMMUTABLE` cannot clear `+i` on the root-owned archive at all** — it receives `EPERM` from the ioctl, not `EACCES` from a later open — and every `A1 + A3` / `A1 + A4` combination against a root-owned seal, archive file or `.close` manifest was incomplete. **`A1 + A2` for F-2 was constructible only by accident**, because `freedomsheet` owns its journal file and so satisfies the owner half by ownership; the label did not say so | **§2.13.5c**, redesigned: a *kernel requirements* table stated before the register; **A1** narrowed to the special-bit half alone; **new A10** (owner authorization over the `freedomsheet`-owned journal) and **new A11** (owner authorization over the root-owned seal and archive) as separate rows; and eleven falsification rows re-stated with corrected minimum combinations — F-1a, F-4, F-5, F-8 … F-12 gain **A11**, F-1b gains **A10 and A11**, F-2 and F-5 gain **A10** |
| 23 | *"A1 … A6 confer nothing on each other"*, and, in **F-1a**, *"every real holder of A3 also holds A2"* | **A register cannot assert independence and then reason from implication.** Both sentences were live text in the same subsection, and the falsification matrix's detector-reach column was computed from the first while the qualification under F-1a came from the second | **§2.13.5c**, which separates what an authority **is** from who can **hold** it: the register keeps the independence claim for the *primitives*, a new **holder table** states which identities on this host bundle which rows, and every falsification row is assessed **twice** — against its minimum combination and against the **smallest identity that can actually hold it**. Bounded claim 2 is rewritten: **only F-2, F-3 and F-6 are bounded by the attacker's authority rather than by its choice of alteration**, where revision 9 implied eleven rows were |
| 24 | `JNL-50` case 9 has a **non-root `CAP_LINUX_IMMUTABLE`-only** identity clear `+i` on an archived file *"successfully"* and then receive `EACCES`; `JNL-49` case 10 and `JNL-50` case 9–10 are constructed with `setpriv --ambient-caps=+linux_immutable` | **The case asserts a syscall result the kernel does not produce**, so it could not have passed, and the register's central claim had no executable evidence behind it. **And the `setpriv` shorthand does not build the set it names**: an ambient capability must also be **permitted and inheritable**, and a `setuid` away from 0 clears the permitted set unless `SECBIT_KEEP_CAPS` and `SECBIT_NO_SETUID_FIXUP` are set first | **§2.13.5c**'s **executable-identity table** — eight identities **E1 … E8**, each with its effective UID, GID, supplementary groups and complete permitted/effective/inheritable/ambient/bounding sets as hexadecimal masks, its full `setpriv` invocation including securebits, and a `/proc/self/status` assertion that runs **before** the operation under test; and **§2.13.8**'s rewritten `JNL-49` and `JNL-50`, at **twelve cases each**, in which the flag-refusal cases are executed with every other prerequisite satisfied and each carries a **positive control** that succeeds. **A-5.0-5 is corrected rather than carried forward, and remains unconfirmed** |

**Revision 10's defects. These are what revision 11 exists to fix, and each is
conceded before its replacement is presented.** Defects 25, 27 and 28 were named
by the re-review; **defect 26 was not, and is recorded because the mechanical
recipe-versus-mask comparison R10-B requires found it.**

| # | Revision 10 said | The fact | Fixed in |
|---|---|---|---|
| 25 | identities **E2 … E6** are constructed by a root wrapper running `setpriv --securebits=+keep_caps,+no_setuid_fixup --reuid=… --regid=… --bounding-set=… --inh-caps=… --ambient-caps=…` | **`setpriv(1)` from util-linux 2.39.3 does not accept `keep_caps`.** Its manual lists the valid securebits as *"noroot, noroot\_locked, no\_setuid\_fixup, no\_setuid\_fixup\_locked, and keep\_caps\_locked"* and states that *"keep\_caps is cleared by execve(2) and is therefore not allowed"*. The five commands exit **127** at option parsing and **no identity is produced**, so every `JNL-49`/`JNL-50` case that names E2 … E6 would have been **`inconclusive`** at its own mandatory `/proc/self/status` precondition. The bit was also unnecessary: `capabilities(7)` states that `SECBIT_NO_SETUID_FIXUP` *"provides a superset of the effect of"* `SECBIT_KEEP_CAPS`, and that `keep_caps` *"is always cleared on an execve(2)"* while the securebits *"are inherited by child processes"* and survive `execve` except that one | **§2.13.5c**, which replaces the mechanism with **`capsh(1)`** and states the seven-step construction, the kernel rule each step relies on, and the tool's ownership, mode, absence of file capabilities, lifecycle, cleanup, authority and security-review consequence. **`+keep_caps` is used nowhere**, in any tool |
| 26 | **E2 … E6** request `--bounding-set=+linux_immutable` (and, for E4 … E6, `+dac_override`, `+dac_read_search`, `+fowner` beside it) and declare `CapBnd` values of `0x200`, `0x206`, `0x208` and `0x20E` | **That is an *addition* to the bounding set, which no tool can perform.** The same `setpriv(1)` page states that *"notwithstanding the syntax offered by setpriv, the kernel does not permit capabilities to be added to the bounding set"*, and that the set for `--bounding-set` *"starts out as … the current bounding set"*. Launched from root's full set, the option is at best a no-op and the resulting `CapBnd` would have been **`0x000001ffffffffff`**, not the declared mask. **The re-review named this failure for E8 only; it is present in E2 … E6 as well**, and revision 10 did not notice because it never compared a declared mask with the recipe intended to produce it | **§2.13.5c**'s **mask-versus-recipe comparison table**, which derives every declared cell from the command line; and the mechanism itself, because `capsh` offers **only `--drop`** and therefore cannot express an addition. The prerequisite — that every capability an identity needs is **already** in the launching process's bounding set — is stated, tied to the observed value in §8.1 **H-6**, and asserted by the harness, which reports **`inconclusive`** rather than proceeding if it does not hold |
| 27 | **E8** is `freedomcoord : freedomcoord` with `CapPrm`, `CapEff`, `CapInh`, `CapAmb` **and `CapBnd`** all `0x0`, constructed by `setpriv --reuid=freedomcoord --regid=freedomcoord --init-groups` | **The recipe drops nothing.** With no `--bounding-set`, E8's bounding set would have been the launching process's — the full set — and the declared `CapBnd=0x0` was unproduced. A declared mask that the recipe does not create is exactly the assertion that makes a case `inconclusive` | **§2.13.5c**, where E8 is built by the same seven-step construction as every other identity with an empty capability mask, and its bounding set is dropped explicitly. **E1 had the drop and E8 did not**, which is the shape of an identity table written twice rather than derived once; revision 11 derives all eight from one procedure |
| 28 | **E7** is *"`0` : `0`"* with permitted, effective and bounding given as *"full"* and inheritable and ambient given as **dashes**, under a subsection asserting that every identity specifies complete permitted, effective, inheritable, ambient and bounding masks | **A dash is not a mask, and the subsection's own claim made it a contradiction.** A case whose identity assertion cannot be evaluated is `inconclusive`, and *"full"* is not evaluable either without naming `CAP_LAST_CAP` for the kernel in question | **§2.13.5c**, where E7 carries the values read from this host on 2026-08-31 — `CapPrm`, `CapEff` and `CapBnd` `0x000001ffffffffff`, `CapInh` `0x0`, `CapAmb` `0x0`, securebits `0x0` — with `CAP_LAST_CAP = 40` on kernel **6.8.0-138** named as the derivation, and §8.1 **H-6** recording the read. **E7 is also the one identity whose masks are environment-dependent**, and the harness is required to re-read and re-assert them on the host it actually runs on rather than trusting this document's copy |
| 29 | §2.12.5 says a deployment *"compares the recorded SHA-256 of each deployed file against that reviewed commit"*, and §2.13.2c specifies `deployment_manifest_digest()` as the mechanism: the deploy step records a digest of the **live deployed bytes**, the operator supplies that value back, and **C0** compares it with a fresh digest of **those same live bytes** | **That is consistency after deployment, not provenance from a reviewed commit.** Nothing in the artifact, the registration or the activation precondition ever names a trusted manifest derived from an immutable reviewed Git object, and **no step refuses when the comparison against the commit is omitted** — so an operator who skipped it deployed bytes that H-1 explicitly permits a service identity to have rewritten, computed their digest, created a generation and passed **W11** thereafter, with no refusal and no durable record that the check had not happened. It is Blocking because the deployed program is root-owned and carries authority over the authority plane and the journal evidence. **Security-review finding P5.0-SR1** | **New §2.12.5a**, which replaces the sentence with **Algorithm D** (`D0 … D8`, refusals `DEP-01 … DEP-09`): an out-of-band `root:root 0444` approval record, a trusted manifest computed from **Git object bytes** in a `0700 root:root` bare store addressed by object id and never through a ref, a closed **two-region partition** of the deployed root in which an unaccounted file refuses, and a provenance record written last and outside the deployed root. **§2.13.5a C0** refuses when the provenance record is **absent**; **`SB`** carries the commit, tree and source-manifest values; **W11a** re-checks them; **`V-R`** refuses without an `approved_source_revisions` row and the generation carries a `NOT NULL` foreign key to it, so an unprovenanced deployment cannot reach activation. `JNL-46` 5 → **9** cases and new **`JNL-51`**, eight cases, including the omission test the finding requires |
| 30 | §2.12.2 gives `freedomcoord` and `freedomsheet` the groups *"its own only"* and asserts that *"`freedomcoord` … is in no group any service identity holds"*, while §2.13.3 requires both to be members of `freedomjournal` and §2.13.5c's `E1` and `E2` are constructed with it | **The two contracts cannot both be followed.** Under §2.12.2 the `0750` journal directory and the `0440` seal are unreadable, so the writer cannot perform the startup validation §2.13.5b requires of it, **C-4** cannot pass and the holder table is wrong; under §2.13.3 the identity and isolation inventory §2.12.6 reasons from is wrong. The isolation sentence was false from revision 6 onward and was carried through five revisions. **Security-review finding P5.0-SR2** | **§2.12.2, rewritten as the canonical membership table** — primary and supplementary groups for every identity, a group→members inverse with what each membership grants and does not grant, and a rule that no other passage states a membership. The false sentence is **withdrawn** and replaced by three separately testable claims. §2.13.3, §2.13.5c, §2.12.6, §2.12.7, §2.13.7 and logical schema §4.3.2 cite it; **`E8` gains `freedomjournal`** so it is the identity provisioning creates, and the identity table says which provisioned identity each of `E1 … E8` corresponds to — three correspond to none. New **`JNL-52`**, eight cases of positive and negative `id`, `namei -l` and `open` evidence for `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`. New stop condition **10p** |

Defects 1–3 were one defect with three faces: *the design trusted a file without
specifying what made it trustworthy.* Defects 5–9 are a second, different one:
**the specification asserted properties it had not checked against the mechanism
it named** — a hash order that cannot be evaluated, a permission that contradicts
a duty, a probe whose refusals are not attributable, and a constraint doing work
it cannot do. §2.13.5a, §2.13.3, §2.13.2a and §2.13.8a are the four answers, and
§2.13.5c is the falsification matrix that would have caught all four.

**Defects 10–12 are a third, and it is the narrowest and the most instructive:
the specification described its own artifacts more strongly than it built
them.** A digest was said to cover four stages when it covered three; a refusal
was said to hold for the writer when one field escaped it; a test expected a
record its own algorithm refuses to produce. None of the three is a mechanism
error — each mechanism works — and all three are the kind of claim a
falsification case catches only if the case is written to the exact boundary.
**Stop condition 10h is added for that class**, and §2.13.5c now names the
attacker each claim holds against rather than asserting the claim alone.

**Defects 18–21 are a fifth, and they divide in two.** Defects 18 and 19 are the
fourth class again — a correction reproducing its own defect. The step added to
make the probe report's coverage true was validated after it was consumed, and
by a comparison against a copy of its own input; the state machine added to make
a refusal cost checkable required one failure to leave two states. **Defects 20
and 21 are different, and are the more instructive**: both are claims that a
*mechanism* confers something it does not. `CAP_LINUX_IMMUTABLE` was credited
with discretionary access it has never had, and a comparison between two copies
of one recorded value was credited with detecting a forgery of the fact that
value records. Neither is an ordering error or an unbounded sentence; each is a
**wrong model of the mechanism**, and no ordered-walk harness or positive control
would have caught either. What catches them is executing the case under an
identity that really holds only the capability claimed — which is why `JNL-49`
and `JNL-50` now construct a flag-control-only capability set — and refusing to
call a comparison a detector unless the two sides can differ, which is what stop
condition **10h**'s extension now forbids. **Stop condition 10l is added** for
the defect-19 class: two evidence artifacts may not require mutually exclusive
states of the same host artifact after the same injected failure.

**Defects 14–16 are a fourth, and they are the narrowest yet: each is the
revision-7 correction reproducing, one level down, the defect it corrected.**
The step added to make the probe report's coverage true consumed the report
before creating it. The stage moved to make the sandbox evidence sealed never
proved its target writable without the sandbox. The class column added to bound
the falsification claim recorded which detector fired rather than what an
attacker must hold. **A correction stated in prose is as unbounded as the claim
it replaces**, which is why revision 8 answers all three with executable
artifacts — an ordered-walk harness, a positive control, and a capability
register whose every cell carries a test or a not-constructible assertion — and
why stop conditions **10i**, **10j** and **10k** are added beside **10h**.

**Defects 22–24 are a sixth, and they are defects 20 and 21's class reproduced
one level down: a correction for a wrong model of a mechanism, written from a
model of that mechanism which was itself incomplete.** Revision 9 was right that
`CAP_LINUX_IMMUTABLE` confers no discretionary access. It was wrong about what it
*does* confer, because it read only half of `FS_IOC_SETFLAGS`'s permission check
and never wrote the other half down. The register then propagated the omission
into eleven falsification rows, into a not-constructible table, and into two test
cases that assert an `errno` the kernel does not return — and, because the two
capability-set cases were *specified* rather than run, nothing in the evidence
plan could have caught it. **What catches this class is naming every kernel
prerequisite of an operation before writing any row that depends on it**, which
is why §2.13.5c now states the kernel's checks in a table of their own before the
register that encodes them, and **executing each negative case with all other
prerequisites satisfied and a positive control that succeeds**, which is why
`JNL-49` and `JNL-50` now carry the isolating identities **E4** and **E5** and
their controls **E6** and **E2**. **Stop condition 10m is added** for the class,
and **10k** is extended: no capability may be credited with satisfying a kernel
check it does not satisfy, and no evidence case may assert a syscall result
without stating the syscall, the complete identity that issues it, and the
expected `errno`. Defect 23 has a second lesson of its own: **a register may
assert that its primitives are independent, or reason from the fact that real
holders bundle them, but it must do both explicitly** — which is what the holder
table and the two-column detector-reach assessment now do.

**Defects 25–28 are a seventh, and the pattern is now explicit enough to name
plainly: each correction has been checked against the *model* it replaces and not
against the *tool* that has to execute it.** Revision 10 was right about the
kernel — `FS_IOC_SETFLAGS` really does make both checks, and the eleven corrected
combinations stand. It was wrong about the four commands that were supposed to
put a process in front of that ioctl, and it was wrong in a way that a **single
reading of the installed manual page** would have caught: `keep_caps` is listed
as not allowed, and additions to the bounding set are documented as impossible.
**Neither error is subtle, and neither survived contact with the tool, because
the recipes were never brought into contact with it.** The declared masks were
written from what the identity was *meant* to hold, and the recipes from what the
options were *believed* to do, and the two were never compared — which is why
defect 26 exists at all, and why the re-review found only two of its three
instances.

**What catches this class is a mechanical comparison in the document itself**:
every declared capability mask must be **derived** from the invocation that
produces it, option by option, against the named tool's documented semantics —
not asserted alongside it. §2.13.5c now carries that comparison as a table, and
**stop condition 10n is added** for the class: no executable identity may declare
a set its own recipe does not produce, and no identity may be constructed by a
mechanism whose **ordering** the named tool's documentation does not determine.
That second clause is why the mechanism changes rather than the option list.
Substituting `+no_setuid_fixup` for `+keep_caps` would have made revision 10's
commands *parse*; it would not have made their results **derivable**, because
`setpriv(1)` never says whether it applies securebits before or after the UID
transition, and the entire declared identity turns on that. **A recipe whose
outcome depends on an undocumented internal ordering is not a specification**,
and revision 11 declines to write one and then defend it with a test that has not
been authorized to run. Defect 28 has a lesson of its own, smaller and worth
stating: **an environment-dependent value must name its environment**. *"Full"*
is not a mask; `0x000001ffffffffff` is, and only on a kernel where
`CAP_LAST_CAP = 40`.

#### 2.13.2 The storage decision, and what was rejected

**Unchanged from revision 5 except where it referred to the probe.** The
requirement is a file that (a) survives reboot and unclean shutdown, (b) the
writer can only append to, (c) the writer cannot unlink, rename, replace or
truncate, (d) is on a filesystem whose behaviour has been **verified rather than
assumed**, and (e) whose absence or corruption is distinguishable from emptiness.

| | Candidate | Verdict |
|---|---|---|
| **S-1** | **`/var/lib/freedom-sheet-writer/`** on the root ext4 volume | **Chosen, and retained by revision 6.** `/var/lib` is on `/dev/vda1`, `ext4`, the *same* filesystem as `/opt/freedom-blades` — read with `df -T` and `/proc/mounts` on 2026-08-29 (§8.1 **H-5**), not inferred from a neighbouring path. It is the FHS location for state a service must keep across reboots, and it is where an operator will look. **The R5 handoff requires this direction preserved unless a governed decision changes it, and no governed decision has** |
| **S-2** | `/run/...` — revision 4's choice | **Rejected. This is P5.0-R5.** Volatile by definition, and `noexec,nosuid,nodev` `tmpfs` besides |
| **S-3** | systemd `StateDirectory=freedom-sheet-writer` | **Rejected, and the reason is the point of the whole section.** `StateDirectory=` creates `/var/lib/<name>` **owned by the unit's `User=`**, i.e. by `freedomsheet`, mode `0755`. The writer would then own the directory holding its own evidence and could unlink, rename and replace the journal at will. The convenient mechanism is the one that defeats the requirement, so the directory is created by root at provisioning and merely *made writable through* `ReadWritePaths=` |
| **S-4** | A PostgreSQL table instead of a file | **Rejected, unchanged from revision 4 and for the same reason.** A database write before every Sheet write would give the Freedom bot's legacy mutation path a standing PostgreSQL availability dependency — the exact property that withdrawing the lease bought back, and revision 6 does not give it back. **The generation *registration* is in PostgreSQL; the per-dispatch record is not**, and the writer never opens a database connection at all |
| **S-5** | A separate partition or an `O_DIRECT` raw device | **Rejected as disproportionate.** It adds a mount, a provisioning failure mode and an operational surface, and buys nothing over `fsync` on ext4 that this package can evidence |
| **S-6** | An external append-only service (journald, syslog, a log shipper) | **Rejected.** `journald` rotates, rate-limits and drops under pressure by design; a shipper adds a network dependency to the legacy mutation path. Neither can be made to refuse a dispatch, which is what §2.13.6 needs |

**The filesystem capability is probed, never inferred — and revision 5's probe
did not work.** `chattr +a` on ext4 is a kernel behaviour, not a mount-table
fact, so the design tests it. **How** it tests it is §2.13.2a, which is new and
is remediation R5-C. What this subsection now states is only where the result
goes:

- the probe runs at **provisioning**, inside `freedom-journal-admin
  verify-capability`, against **disposable artifacts in a directory that holds no
  evidence** — never against the live journal;
- its canonical **probe report** is embedded in the generation's seal body
  (§2.13.5a step **C3**, after validation at **C2**), so it is covered by the seal, by the genesis record's
  anchor and by the `chattr +i` attribute, and can be re-derived by any later
  reader;
- the report's digest, its procedure version and its timestamp are carried into
  the registered generation row (logical schema §3.7). **They record an
  attestation bound to a re-derivable artifact. They do not prove the probe
  ran, and §2.13.8a says so where a reader meets them**;
- at every writer start the writer performs the **non-destructive** subset of the
  same checks — `FS_IOC_GETFLAGS`, `fstat`, `statvfs` and a chain read — and
  refuses if any fails (§2.13.5b **V-W**, §2.13.6 row **J-06**). It performs no
  write-mode open, no truncation, no unlink and no rename against live evidence.

**If the capability turns out to be unavailable**, the design degrades in a
stated way rather than collapsing: the directory permissions of §2.13.3 still
prevent unlink, rename and replacement, and the hash chain of §2.13.8 still
detects rewriting after the fact. What is lost is *prevention* of rewriting by
the file's own owner. In that state `verify-capability` **fails**, produces no
passing probe report, and `init-generation` **refuses to create a generation at
all** — a host-side refusal by the privileged tool, before any database is
involved. The operator's choice is then between provisioning a filesystem that
supports the attribute and accepting the weaker variant explicitly under
**D5.0-13 / OD-66 option B**.

#### 2.13.2a The append-only capability probe — valid, attributable, and safe. **New in revision 6; this is remediation R5-C**

Revision 5's probe had two defects and the handoff names both. It ran against a
`root:root 0600` file in a directory `freedomsheet` cannot write, so **every
negative case would have failed on discretionary permissions whether or not
`FS_APPEND_FL` did anything**; and it told the writer to re-run destructive
operations against the live journal at every start, which, in exactly the state
the check exists to detect, would have **succeeded** and destroyed the evidence.

The requirement is therefore: *each expected refusal must be attributable to
`FS_APPEND_FL` and to nothing else, and no destructive operation may ever touch
live evidence.* Four stages, in order, **all four inside a single
`freedom-journal-admin verify-capability` invocation, and the probe report is
built only after all four have run** — which is remediation R6-A. The command
runs as root and drops to the writer's uid with `setpriv --reuid=freedomsheet
--regid=freedomsheet --clear-groups` for every case that is supposed to be
performed *as the writer*.

**That drop is retained unchanged in revision 11, and it is deliberately not
identity `E1`.** It requests **no securebit and no capability option**, so none
of the R10 findings touches it: the invocation is valid under util-linux 2.39.3
as written, and its result is derivable without knowing `setpriv`'s internal
ordering — the UID transition clears the permitted, effective and ambient sets
because no securebit prevents it, and nothing asks for a set to be built. It
differs from **E1** in one respect that is stated rather than glossed: its
**bounding set is the launching process's**, not empty. That is *more* latent
authority than E1, never less, and it cannot manufacture a false pass, because
every §2.13.2a case run under it is a **positive control expected to succeed**,
the permitted set is empty, and a bounding set confers nothing without a file
capability — which the probe targets do not carry. **`verify-capability` is
production tooling and acquires no `capsh` dependency**; `capsh` is used only by
the `JNL-49`/`JNL-50` evidence harness.

**The probe arena.** A transient directory `…/probe`, `root:freedomsheet`, mode
`0770`, created by `verify-capability` and destroyed by it. Inside it, each probe
file is created **owned by `freedomsheet:freedomsheet`, mode `0600`**. The tested
identity therefore has full ordinary file *and directory* permission: it may
create, open for writing, truncate, rename and unlink there by discretionary
access control. **That is the point.** Nothing in the arena is evidence, and the
arena does not exist while the writer unit is active — `verify-capability`
refuses to start while it is, and `init-generation` refuses while the arena
exists.

**New in revision 8: a second transient directory, `…/probe-ro`**, identical in
ownership and mode and on the same mount, holding Stage 4's negative target. It
exists for one reason — the arena must be **inside** the transient unit's
substituted `ReadWritePaths=` and Stage 4's negative target must be **outside**
it — and it carries the same lifecycle, the same cleanup and the same refusals as
the arena. It is specified in full under *Stage 4* below, and it is remediation
**R7-B**.

**Stage 1 — the control stage. Its only job is to prove that ordinary
permissions are not the reason for anything Stage 2 observes.** On a file with
the arena's ownership and mode and **no** `+a`, executed as `freedomsheet`:

| Case | Operation | Required result |
|---|---|---|
| **C-1** | `open(O_WRONLY)`, then `pwrite` at offset 0 | **succeeds**, and the byte at offset 0 changes |
| **C-2** | `open(O_WRONLY\|O_TRUNC)` | **succeeds**, and the file is empty afterwards |
| **C-3** | `ftruncate(fd, 0)` | **succeeds** |
| **C-4** | `rename` within `…/probe` | **succeeds** |
| **C-5** | `unlink` | **succeeds** |
| **C-6** | `open(O_WRONLY\|O_APPEND)`, write, `fsync` | **succeeds** |

**If any control case fails, the probe result is `inconclusive`, never
`passed`.** `verify-capability` exits non-zero naming the failing case and its
`errno`, and no generation may be created. This single rule is what revision 5
was missing: a probe that cannot demonstrate the *positive* first has no standing
to interpret a *negative*.

**Stage 2 — the capability stage.** A freshly created file with the same
ownership and mode, on which **root** sets `FS_APPEND_FL`. Every case is executed
as `freedomsheet`:

| Case | Operation | Required result | Why this errno and not another |
|---|---|---|---|
| **P-1** | `open(O_WRONLY)` without `O_APPEND` | **`EPERM`** | `may_open()` refuses a writable non-append open on an append-only inode. DAC would have given `EACCES`, and Stage 1 proved DAC permits it |
| **P-2** | `open(O_WRONLY\|O_APPEND\|O_TRUNC)` | **`EPERM`** | `O_TRUNC` on an append-only inode is refused even with `O_APPEND` |
| **P-3** | `ftruncate` on an `O_APPEND` fd | **`EPERM`** | `IS_APPEND(inode)` is checked in the truncate path |
| **P-4** | `rename` within `…/probe` | **`EPERM`** | `may_delete()`/`may_create()` refuse on an append-only victim. **Stage 1 C-4 proved the directory permits renames** |
| **P-5** | `unlink` | **`EPERM`** | as above. **Stage 1 C-5 proved the directory permits unlinking** |
| **P-6** | `open(O_WRONLY\|O_APPEND)`, write, `fsync` | **succeeds**, and the bytes are at the old EOF | the capability must permit the one operation the writer needs |
| **P-7** | `pwrite(fd, …, offset 0)` on an `O_APPEND` fd | **succeeds, and the bytes land at EOF, not at offset 0** — asserted by reading the file back | **Deliberately not a refusal.** POSIX requires `O_APPEND` to ignore the offset, so a design expecting `EPERM` here would be wrong. It is asserted because *where the bytes land* is the property the journal depends on |
| **P-8** | `FS_IOC_SETFLAGS` clearing `FS_APPEND_FL` | **`EPERM`**, **and** a subsequent `FS_IOC_GETFLAGS` still reports `FS_APPEND_FL` | needs **both** halves of the ioctl's permission check, and **the arena file is created owned by the writer's uid**, so the owner half (§2.13.5c **A10**) is satisfied and the missing prerequisite is `CAP_LINUX_IMMUTABLE` **alone**, which the writer never holds. *Revision 10 states this explicitly, because a refusal whose cause is ambiguous between two checks proves neither* — it is the same isolation `JNL-50` case 3 makes against the live journal. The read-back is what distinguishes "refused" from "silently ignored" |
| **P-9** | `FS_IOC_GETFLAGS` | reports `FS_APPEND_FL` | `ENOTTY` or `EOPNOTSUPP` here means the filesystem does not implement the flag interface at all, and is a **failed** probe, not a passing one |

**Stage 3 — storage attribution. Its two cases are named in revision 7, because
Algorithm C step C1 hashes them by name and R6-E requires every case a canonical
artifact references to have a definition.** Read-only, as root:

| Case | Observation | Required result |
|---|---|---|
| **M-1** | the `/proc/mounts` entry covering the journal path | it names a **non-`tmpfs`** filesystem backed by a **block device**, and does not carry `ro` |
| **M-2** | `statvfs` on the journal directory | `ST_RDONLY` **clear**. The directory's `st_dev` is recorded in the report as `probe_device` |

`init-generation` later asserts that the journal file it creates has the **same
`st_dev`** (step **C6**), so the report is bound to the filesystem that was
actually tested and not merely to a path string.

**Stage 4 — sandbox attribution. Moved in revision 7 from deployment to
provisioning; given an exact target and a positive DAC control in revision 8,
which is remediation R7-B.** Revision 6 ran this stage *"once at deployment, not
at provisioning"* while Algorithm C built the immutable probe report from stages
1–3, and while logical schema §3.7, §2.13.8a and the evidence contract all said
`append_only_probe_digest` covered **four** stages. **Both statements cannot be
true, and the one that was false is the digest claim**: a report sealed under
`chattr +i` cannot acquire a stage that runs afterwards. Revision 7 conceded that
and moved the stage rather than re-wording the claim.

**Revision 7's remaining defect, conceded before its replacement.** Revision 7's
**S4-2** appended *"to a path **outside** `ReadWritePaths=` but inside
`ProtectSystem=strict`'s read-only tree"* and accepted `EROFS` as evidence of the
sandbox. **It never said which path, and it never proved that path was writable
by `freedomsheet` without the sandbox.** An unspecified path outside the arena is
overwhelmingly likely to be one `freedomsheet` cannot write anyway — every
directory in §2.13.3 except the arena denies it — so the refusal would have been
attributable to ordinary permissions, and a kernel that returns `EACCES` before
it consults the mount would have produced the wrong `errno` for the wrong reason.
**This is the same attribution defect Stage 1 was created to correct**, left
uncorrected in the one stage that runs under systemd. Revision 8 fixes it the way
Stage 1 fixed Stage 2: with a positive control, on the exact target, before the
negative case is interpreted.

Stage 4 runs **inside the same `verify-capability` invocation, after Stage 3 and
before the probe report is built**, so its cases are inside the bytes the digest
covers. It tests systemd rather than the filesystem, so it needs the writer's
unit file **deployed** — which `verify-capability` requires as a precondition and
whose digest it records.

**The exact Stage-4 target, and its whole lifecycle.** `verify-capability`
creates a **second** transient directory beside the arena:

| | The arena | The Stage-4 target directory |
|---|---|---|
| Path | `…/probe` | **`…/probe-ro`** |
| Owner : group, mode | `root:freedomsheet 0770` | `root:freedomsheet 0770` — **identical, deliberately** |
| Contents | the Stage-1/2 probe files, `freedomsheet:freedomsheet 0600` | **`…/probe-ro/s4-2.target`** and **`…/probe-ro/s4-0.unlink`**, both `freedomsheet:freedomsheet 0600`, neither carrying `+a` or `+i` |
| Inside `ProtectSystem=strict`'s read-only tree? | yes — it is under `/var/lib`, and `ProtectSystem=strict` mounts the whole hierarchy read-only except `/dev`, `/proc`, `/sys` and the paths named in `ReadWritePaths=` | **yes, for the same reason and on the same mount** — `…/probe-ro` is a sibling of `…/probe` under the same `/var/lib/freedom-sheet-writer` on the same ext4 device Stage 3 recorded as `probe_device` |
| In the transient unit's substituted `ReadWritePaths=`? | **yes** — the substitution names `…/probe` and nothing else | **no, and that is the entire point.** The substitution is one path, recorded verbatim in the report, and `…/probe-ro` is not it |
| Holds evidence? | no | **no.** Both files are created by this command, contain only probe bytes, and are removed by it |
| Removed by | the `finally` in `verify-capability` | **the same `finally`**, in the same privileged cleanup, with the same non-zero exit and named residue on failure |

The two directories are siblings rather than one directory, because the arena
**must** be inside the substituted `ReadWritePaths=` for **S4-1** and the target
**must** be outside it for **S4-2**, and a path cannot be both.

| Case | Operation | Executed | Required result |
|---|---|---|---|
| **S4-0** | **New in revision 8 — the positive DAC control for S4-2.** On the **exact** `…/probe-ro/s4-2.target`, on the same mount, under the same uid: `open(O_WRONLY\|O_APPEND)`, `write`, `fsync`, `close`; then `rename` `s4-2.target` → `s4-2.target.moved` **within `…/probe-ro`** and `rename` back, so the negative case meets the same path it did; and, on the identically created sibling `…/probe-ro/s4-0.unlink`, `unlink` | as `freedomsheet` through `setpriv`, **outside any unit**, with **no** sandbox | **every operation succeeds.** If any fails, the Stage-4 result is **`inconclusive`**, never `passed`, and `verify-capability` exits non-zero naming the operation and its `errno` |
| **S4-1** | `open(O_WRONLY\|O_APPEND)`, write, `fsync` on an arena file **inside** the substituted `ReadWritePaths=` | inside the transient unit, as `freedomsheet` | **succeeds** |
| **S4-2** | **the same append, to the exact `…/probe-ro/s4-2.target` S4-0 just proved writable**, which is outside the substituted `ReadWritePaths=` and inside `ProtectSystem=strict`'s read-only tree | inside the transient unit, as `freedomsheet` | **`EROFS`, and nothing else.** `EACCES` means discretionary permissions refused it — which S4-0 has just excluded — so `EACCES` is **`inconclusive`**, not a pass. **Success** is a **failed** stage: the sandbox did not deny |
| **S4-3** | `systemctl show` on the transient unit, compared with the deployed unit file **and its drop-ins** under the four conditions below | root | the **applied** property set is captured, normalized and hashed, and must equal the deployed unit's normalized sandbox property set except for the single `ReadWritePaths=` substitution, **which is the canonical probe path and nothing else**; the deployed unit's digest (unit and drop-ins) and the **systemd identity** — `systemd` version and the providing package's name and version — are recorded alongside it. **Any refusal under the four conditions, and any mismatch, is `inconclusive`** |

**S4-3's four conditions — amended 2026-09-23 under C-P5.0-R5-R1, and pending
independent Codex review.** The security review (rev 11, *"Stage 4 remains
conditional"*) made these implementation conditions; the P5.0-R5 reconciliation
(matrix row 15) found them neither stated here nor implemented. They are now
normative, and each is a refusal rather than an interpretation:

1. **A closed allowlist of supported unit directives and drop-ins.** S4-3
   parses the deployed unit in a closed grammar — the sections `[Unit]`,
   `[Service]` and `[Install]`, one `Key=Value` per line, no continuation line,
   no specifier, quote, escape or variable, and no `~` capability inversion —
   and admits only the directives on the allowlist: §2.13.3's hardened sandbox
   directives, `ExecStart=` and `Type=`, and non-authority lifecycle
   directives. **The supported drop-in set is empty**, because this section
   names none: a drop-in beside the writer unit is refused by name, and
   admitting one is a design change. *Maintainer confirmation of the empty set
   is requested in the C-P5.0-R5-R1 handback.*
2. **Duplicate or unknown authority-bearing directives are rejected, including
   in drop-ins.** An unknown directive is refused outright, because a parser that
   does not know a directive cannot know it bears no authority. An
   authority-bearing directive assigned more than once anywhere across the unit
   and its drop-ins — including an empty reset assignment — is refused, so the
   comparison never depends on systemd's reset-and-accumulate rules. Every
   sandbox directive must be assigned exactly once.
3. **The substituted `ReadWritePaths=` is constructed from the internally
   fixed canonical probe path** — `…/probe`, derived from the approved target
   and taken from no caller, argument or report. A report that recorded any
   other substitution is refused, and the deployed unit's own `ReadWritePaths=`
   value never enters the expected set.
4. **The complete normalized applied property set is compared, and a systemd
   or package change invalidates the evidence.** `systemctl show` must report
   every compared property exactly once, with no omitted, duplicated or
   unrequested property, and each value must equal the deployed value after the
   same normalization. The attestation carries the systemd identity it was made
   under; **a different identity invalidates it even when the deployed unit's
   bytes are unchanged**, because what S4-3 attests is systemd's
   *interpretation* of those bytes, and an upgrade can change that without
   changing them. So does a re-read applied set that no longer matches. The
   only way back is a fresh `verify-capability`, which is a rotation.

The harness implements these as typed, fail-closed repository logic in
`tools/phase_5_0_evidence/unit_sandbox.py`. **That is not evidence**: no
deployed writer unit exists yet (reconciliation row 16), and the concrete
plan's S4-3 vector still asks `systemctl show` for two properties, so it cannot
produce a passing S4-3 under condition 4 until the unit exists and the vector
carries the complete set. *Added 2026-09-23 under C-P5.0-R5-R2, pending
review:* the concrete plan declares that gap as its own unresolved conflict,
**C-S4-3** (`STAGE4-S4-3`), which keeps `is_executable` false independently of
Band 7's C-7 until a reviewed producer supplies the deployed unit and drop-in
policy, the complete capture, the canonical substitution and the systemd
identity. *Amended 2026-09-23 under C-P5.0-R5-R3, pending review:* no
review reference, label, path, digest or flag can stand in for that producer.
C-S4-3 is declared unconditionally and has no resolution branch; resolving it
is a separately authorized code and artifact integration pass — the reviewed
deployed unit and drop-in policy, the widened capture, and a reviewed
`SystemdIdentity` producer bound into the attestation — followed by independent
review. S4-3 is a required case (`required_cases.REQUIRED_CASES`), so a plan
that neither produces nor declares it is refused.

**Why S4-0 has to run outside the unit, and why that is not a weaker control.**
The claim S4-2 makes is *"the systemd read-only bind is what refused this
append"*. Falsifying it requires showing the append would have been **permitted**
without that bind — which can only be observed with the bind absent. S4-0 holds
everything else fixed: the same uid, the same absolute path, the same inode, the
same directory, the same mount, the same file mode and the same ownership, with
only the sandbox removed. That is exactly the shape of Stage 1's control for
Stage 2, applied to the one stage revision 7 left without one.

**The order inside Stage 4, stated because it is now load-bearing.** `…/probe-ro`
and its two files are created (root) → **S4-0** runs unsandboxed (as
`freedomsheet`) → the transient unit is started → **S4-1**, **S4-2** and
**S4-3** run → the unit exits → the `finally` removes `…/probe-ro` and `…/probe`.
**S4-0 precedes S4-2 in every execution**, and a Stage-4 report in which S4-2 is
a pass while S4-0 is not present-and-passing is refused at Algorithm C step
**C2** and again by the writer at **W4**.

**What S4-3 buys, stated because it is what makes the other cases mean
anything.** Without it Stage 4 would attest that *some* sandbox behaved as
expected. With it, the report names the exact directive set exercised and the
exact deployed unit it came from, so a later `EROFS` at writer start is
attributable rather than ambiguous: if the running unit's directives still hash
to the recorded value the sandbox is not the explanation, and **M-1**/**M-2**
separate a read-only mount from it.

**The binding to the deployment, which is what keeps the stage true after it has
run — and which revision 9 makes consistent with Algorithm C.** The digest is
**computed**, never merely accepted: `deployment_manifest_digest()` of §2.13.2c
runs over the deployed writer's manifest **including
`freedom-sheet-writer.service` and its drop-ins**, and the run refuses unless the
computed value equals the one the operator supplied. Inside `init-generation`
that comparison is step **C0**, **before C1 consumes the value** — *revision 8
placed the equality check at C2, after C1 had already passed the supplied string
to the probe, and compared it against the probe's copy of that same string*
(§2.13.1 defect 18). `PR` therefore records a **validated** digest, **C2**
recomputes the manifest to detect a deployment changed since C0 and checks
`PR`'s copy for consistency, and the sandbox evidence inside the seal describes
**this** deployment. The rule that already exists — a redeployment requires a
rotation (**J-22**, **F-6**) — is what invalidates it **for a change of
deployed bytes**. *Amended 2026-09-23 under C-P5.0-R5-R1, pending review:*
revision 9 said *"No second invalidation rule is invented, because none is
needed."* **That was not true.** A systemd or package upgrade can change how the
unchanged unit is interpreted, and the deployment digest cannot see it. So
there is a second rule — S4-3 condition 4 — and it has an enforcement point:
**W4** and **C-a** refuse (`SW-J25`/`J-25`) when the systemd identity `PR`
recorded at S4-3 differs from the host's current one.

**The lifecycle choice, made in the open rather than for Peter.** The re-review
named two coherent lifecycles. Revision 7 takes the **first**, and states the
comparison rather than presenting the outcome alone.

| | **Option 1 — taken** | Option 2 — not taken |
|---|---|---|
| Shape | run sandbox attribution **before** seal creation and bind its exact result into the one immutable report | separate filesystem-capability evidence from deployment/sandbox evidence as two typed artifacts, with distinct digests, timestamps, authorities, storage, invalidation rules and writer/coordinator checks |
| Is it feasible? | **Yes.** The stage needs the unit *file*, not a running writer, and the unit file is already deployed before a generation exists — **C0** requires the unit deployed and the digest supplied, both pre-probe facts, and **C2** compares the digest against the report once the report exists | Yes, but it adds a second evidence artifact to a design whose entire integrity argument is that one seal is the anchor |
| How the **writer** authenticates it, with **no PostgreSQL** | it needs no new mechanism: the report is inside the seal body, covered by `seal_body_digest`, anchored by record 0, and checked at **W4** | **this is the difficulty.** A file written at deployment sits outside the `chattr +i` seal, is authored by an actor the writer cannot verify, and the writer has no database to compare it against. Authenticating it honestly means giving it its own seal — which is option 1 with more parts |
| Invalidation | **two conditions, both enforced inside the one sealed report** — *amended 2026-09-23 under C-P5.0-R5-R2, pending review.* (1) A change of **deployed bytes** invalidates through the existing rule: redeployment requires a rotation (**J-22**, **F-6**), which discards the whole generation and its sandbox evidence with it. (2) A change of **systemd or package identity** — which can change how unchanged bytes are interpreted — invalidates the S4-3 attestation at **W4** and **C-a** under **J-25** (§2.13.2a S4-3 condition 4), and it too requires a fresh `verify-capability`, which is a rotation. The second condition introduces **no second evidence artifact and no new refusal-code family**: it is a further refusal cause of the existing `SW-J25`/`J-25`, checked against the report already inside the seal | a **new** rule, plus new absent / stale / mismatched / corrupt refusal paths and a writer-side check for each |
| Cost | one `systemd-run` step, one precondition and — after revision 8's R7-B correction — **four** cases in `verify-capability`, plus one transient sibling directory with two files. **No new artifact, digest, authority, storage location or refusal-code family.** *Amended 2026-09-23 under C-P5.0-R5-R2, pending review:* revision 7 also said *"no new … invalidation rule"*; that is **superseded** by the second invalidation condition above. Its availability cost — a systemd or package upgrade stops Sheet mutations until a rotation — **extends the already identified R-5.0-11 and R-5.0-16 exposure and remains pending review and maintainer disposition** | a new artifact, its digest, its writer, its storage, its own invalidation rules, and at least three new refusal codes |
| Risk it carries | the probe now requires systemd and a deployed unit **at provisioning time**. Recorded in **A-5.0-5**, which grows accordingly | two artifacts that can disagree — a class of defect this package has already met once |

**Why option 1.** Option 2's own stated requirement is what rules it out. The
handoff asks how the writer authenticates deployment evidence **without
PostgreSQL**; for a file written at deployment, outside the seal, the honest
answer is *it cannot*. Option 1 also makes the digest claim true **by
construction** rather than by narration: the report contains four stages and
`append_only_probe_digest` covers four stages, because the report is not built
until all four have run.

**This is a design choice inside an already-open decision, not a new governed
one.** It changes the content of **D5.0-13 / OD-66 option A** — which is open,
and whose content revision 6 already re-stated for the same reason — and it is
recorded there (§5.3) rather than adopted here. **No decision number is added**,
because the alternative was not *whether* to hold sandbox evidence but *where to
put it*, and both placements sit inside option A's cost. **Revision 8's S4-0
control and its `…/probe-ro` target are inside the same option-A cost**, for the
same reason: they add a transient directory to a probe option A already carries,
not a new artifact, authority or rule.

**The attribution table — what each observation means, and what it does not.**
This table is the deliverable the handoff asks for, because a probe that cannot
distinguish these is not a probe.

| Observed | Means | Explicitly does **not** mean |
|---|---|---|
| `EACCES` on open, unlink or rename | **discretionary access control** — the identity lacks permission on the file or its directory | append-only enforcement, and — **new in revision 8** — **not** sandbox enforcement either. **Stage 1** exists so this cannot occur in Stage 2 and **S4-0** so it cannot occur in **S4-2**; where it does, the target is mis-provisioned and the result is `inconclusive` |
| `EROFS` **in S4-2, with S4-0 passing on the same file** | systemd's `ProtectSystem=strict` read-only bind, with the path outside `ReadWritePaths=`. **This is the only observation Stage 4 accepts as a pass for S4-2** | a read-only mount — **M-1**/**M-2** establish the filesystem is writable; and not DAC — **S4-0** establishes the exact target is writable by this uid on this mount with the sandbox removed |
| `EROFS` **in S4-2 with S4-0 failing or absent** | **nothing attributable.** Either the mount, the sandbox or the target's permissions could have produced it | evidence of the sandbox. Result: **`inconclusive`** (revision 7 would have recorded it as a pass — that is the R7-B defect) |
| `EROFS` elsewhere | a **read-only mount**, or the systemd bind | append-only enforcement. **M-1**/**M-2** establish the first is not the case |
| **S4-2 succeeding** | the sandbox did **not** deny a write outside `ReadWritePaths=` | nothing benign. Result: **failed** — the writer's sandbox is not doing what the design relies on |
| a directive set from `systemctl show` that does not match the deployed unit's | the transient unit did **not** exercise the sandbox the writer will run under, so **S4-1** and **S4-2** attest nothing about it | anything about the filesystem. Result: **`inconclusive`** (**S4-3**) |
| `EPERM`, with `FS_IOC_GETFLAGS` reporting `FS_APPEND_FL` | **append-only enforcement.** This is the only observation the probe accepts as a pass for P-1 … P-5 | — |
| `EPERM` from `FS_IOC_SETFLAGS` | `CAP_LINUX_IMMUTABLE` is absent from the caller — the expected state for the writer | that the attribute is set; P-9 establishes that separately |
| `ENOTTY` / `EOPNOTSUPP` from `FS_IOC_GETFLAGS` | the filesystem has **no flag interface** | anything about append-only. It is a **failed** probe |
| any Stage-1 case failing | the arena's permissions are wrong | nothing about the capability. Result: **`inconclusive`** |

**Live evidence is never probed destructively — and this is a standing rule, not
a note.** No startup check, health check, monitoring check or test may perform a
non-append write, an offset write expecting offset semantics, an `O_TRUNC` open,
an `ftruncate`, an `unlink`, a `rename` or an attribute change against a live
journal, seal or archive. The writer's startup path (§2.13.5b **V-W**) is
read-only apart from the single `startup` record it appends. Stop condition
**10f** makes this a stop condition rather than an intention, and `JNL-32a` /
`JNL-32b` assert it by syscall trace rather than by inspection — the second in
the branch where `+a` is **absent**, where V-W refuses at **W9** before it would
have appended anything.

**Privileged cleanup, specified rather than implied — and corrected in revision
9, which is remediation R8-B.** `verify-capability`:

1. **refuses** if `freedom-sheet-writer.service` is active, or if `…/journal`
   contains an unsealed generation whose writer might start;
2. **refuses if `…/probe` or `…/probe-ro` already exists**, reporting every
   residual artifact by absolute path, and **neither cleans nor reuses it**.
   *Revision 8 said it would "report it, clean it as an explicit first step, and
   record that it did", while `init-generation` **C0** refused while either
   existed. Those are a self-cleaning path and a refusing path for the same
   state, and the R8 brief requires exactly one. §2.13.2b takes the refusing one,
   and says why*;
3. creates the arena **and `…/probe-ro` with its two files**, runs stages
   **1–4**, and **returns** the canonical probe report to its caller. Run
   standalone it prints the report and **writes nothing to disk**; run as
   `init-generation`'s step **C1** the report is carried in memory, validated at
   **C2**, and reaches disk only inside the seal body at **C9**;
4. in a `finally` that runs on every exit path, clears `FS_APPEND_FL` (and
   `FS_IMMUTABLE_FL`, if a case set it) from every artifact in **both**
   directories as root, `unlink`s each, and `rmdir`s **`…/probe` and
   `…/probe-ro`**;
5. **exits non-zero if cleanup did not complete**, naming each remaining artifact
   by absolute path with the operation that failed and its `errno`, so a leftover
   writable directory is a loud failure rather than a quiet one.

**Whether that cleanup succeeded is what decides which of three states the host
is left in, and §2.13.2b is that state machine.** `init-generation` refuses at
**C0** while **either** directory exists and at **C2** if C1's own cleanup did
not complete, so a failed cleanup cannot be walked past from either direction —
and, because step 2 no longer cleans, it cannot be walked past by re-running
either.

#### 2.13.2b The transient-directory lifecycle — one failure, one state. **New in revision 9; this is remediation R8-B**

**The defect, conceded before its replacement.** Revision 8 required a single
injected cleanup failure to leave the host in two states at once. `JNL-47`
asserted that a failure injected in the privileged cleanup leaves *"no `…/probe`
or `…/probe-ro` residue"*; `JNL-48(d)` planted an artifact *"made undeletable"*
and asserted that the run **names the residue by path** and that
`init-generation` then refuses at **C0** — which requires the residue to still be
there. **Both tests cannot pass against one implementation.** Revision 8 also
gave the *next* invocation two behaviours: `verify-capability` cleaning residue as
an explicit first step, and `init-generation` refusing while it exists. Revision 9
replaces all of that with one state machine and one next-invocation rule.

**The two claims, separated.** *"No generation or database artifact"* is
**unconditional** and survives every state below, because nothing under
`…/journal` is created before **C5** and no row is inserted before **C13**.
*"No transient residue"* is **conditional on cleanup succeeding**, and revision 8
stated it as though it were unconditional. That is the whole of the correction.

| State | Reached when | Transient residue | Generation artifact — journal file, seal, `current`, `.close` | Database artifact — `sheet_writer_journal_generations` row | Exit | What the operator sees |
|---|---|---|---|---|---|---|
| **S-A** — probe-stage failure, cleanup succeeded | any case in Stage 1, 2, 3 or 4 is `failed` or `inconclusive`, **and** the `finally` removes both directories completely | **none.** `…/probe` and `…/probe-ro` are both absent | **none** | **none** | non-zero, **exit code 2** | the failing case, its expected and observed result, and its `errno`; and an explicit line stating that cleanup completed and no residue remains |
| **S-B** — cleanup failure | the `finally` cannot remove some artifact — an attribute it cannot clear, an I/O error, `ENOSPC`, a directory that will not `rmdir` — **whether or not a probe stage also failed** | **exactly the artifacts it could not remove**, each named by **absolute path**, with the operation attempted and its `errno`. Nothing else is left | **none** | **none** | non-zero, **exit code 3**, distinct from S-A | the failing probe case if there was one, **and** the residue report; and an explicit line stating that the tree now requires operator recovery before another generation can be created |
| **S-C** — probe passed, cleanup succeeded | all four stages pass and both directories are removed | **none** | created by **C5 … C11**, in that order, only after **C2** admitted the report | inserted by the coordinator at **C13**, separately | zero from `init-generation`; the registration is a separate act | the values to pass to `RegisterJournalGeneration` |

**A refusal at C0, C1 or C2 is S-A or S-B and never S-C.** A refusal at **C5**
through **C11** is a different thing entirely — a partially constructed,
**unregistered** generation — and it is covered by the failure-cost paragraph in
§2.13.5a, unchanged.

**The next invocation: one behaviour, and it is refusal.** Both
`verify-capability` and `init-generation` **C0** refuse while `…/probe` or
`…/probe-ro` exists, report every residual artifact by path, and **do not clean
it**. Recovery is a **named operator procedure** in
`docs/operations/migration-cutover-and-rollback.md` (WP-9): read the reported
paths, `lsattr` each, clear `FS_IMMUTABLE_FL` or `FS_APPEND_FL` as root where
that is why removal failed, remove the artifacts and the directories, and re-run.
**No separately named privileged cleanup command is introduced, and the automatic
clean is withdrawn** — the R8 brief permits one of the two and this design takes
the refusal.

**Why refusal rather than an automatic cleanup, stated rather than assumed.**
The residue is, by construction, an artifact that the privileged cleanup already
failed to remove **as root, in a `finally`, with `CAP_LINUX_IMMUTABLE`
available**. A second automatic attempt by the same code with the same authority
has no reason to succeed, and if it did succeed it would mean the first attempt
failed for a reason nobody investigated. Worse, an automatic clean turns a state
that needs a human into one that looks transient, and it would give
`verify-capability` a routine path that deletes a directory the writer's identity
can write — precisely the class of act stop condition **10f** exists to forbid.
The refusal is also the cheaper failure: `…/probe` and `…/probe-ro` hold **no
evidence**, so what is lost is the ability to create a generation until someone
looks, which is **R-5.0-14** and is an availability cost, not an integrity one.

**What the residue is and is not.** Both directories are `root:freedomsheet
0770` and contain only probe bytes this command wrote. They are **not** evidence,
they are **not** referenced by any seal, journal, manifest or database row, and
their presence blocks generation creation rather than corrupting anything. The
one thing they are is a **writer-writable directory persisting in the state
hierarchy**, which is why it is reported loudly, why it blocks, and why it is
raised as a security-review question in §9.2 rather than treated as housekeeping.

**Evidence.** `JNL-47` produces **S-A** four times — one probe stage each, with
cleanup succeeding — and **S-B** twice: once after a probe-stage failure and once
after a **fully passing** probe, because a cleanup can fail on a run in which
nothing else did. `JNL-48(d)` produces **S-B** at the Stage-4 level and asserts
the refusal of the next invocation and the operator recovery that clears it.
`JNL-30` asserts that a planted residue from a crashed run is **reported and
refused**, never cleaned and never reused.

#### 2.13.2c The deployment digest — who computes it, over what bytes, and when it becomes final. **New in revision 9; this is remediation R8-A**

Three artifacts consume `writer_deployment_digest`: Algorithm C seals it into
`SB` (§2.13.5a **C3**), the probe records it in `PR` (**C1**), and the writer
recomputes it at every start (§2.13.5b **W11**). Until revision 9 the value's
**origin** was never specified — it was *"supplied on the command line"* — and
that omission is what made revision 8's validation vacuous.

**Why copying caller-supplied text into `PR` is not independent validation.**
Revision 8's **C2** compared `PR.writer_deployment_digest` with the value the
operator supplied at **C0**. But `PR`'s copy **came from** that supplied value:
C1 passed it to the probe and the probe wrote it into the report. Comparing a
string with a copy of itself succeeds for **every** string, including one that
describes no deployment on this host at all. It establishes exactly one thing —
that the value was carried through the probe unchanged — and it establishes it
*after* C1 has already consumed the value. **A validation must compare an input
against a source that did not come from that input.** For this value the only
such source is the deployed bytes.

**The function, named once and used by three actors.**
`deployment_manifest_digest(root)` is a single specified function, implemented
once, and it is what the deploy step, `init-generation` **C0**/**C2** and the
writer **W11** each run. `JNL-46` asserts that the three call sites produce
identical output for one tree, so a C0-computed value and a W11-computed value
cannot diverge by implementation.

**Its second member, new in revision 12.** `deployed_source_manifest_digest(root)`
is a **different function over overlapping bytes**: the same file set, projected
onto the four facts a Git tree can express — deployed name, source path, entry
class and content digest — so that it is comparable with a manifest computed from
Git objects. **§2.12.5a specifies it, and specifies why the projection is
necessary**: Git records neither uid, gid nor the full permission bits, so a
trusted manifest cannot reproduce them and a comparison that pretended otherwise
would fail on every correct deployment. Those facts are checked separately and
exactly, against the reviewed deployment map, at **D7**. Its call sites are the
deploy step (**D7**), `init-generation` (**C0**) and the writer (**W11a**), and
`JNL-46` asserts the same three-site identity for it that it asserts for
`deployment_manifest_digest()`. **Neither function replaces the other, and neither
is weakened by the other's existence**: `DD` remains exactly what revision 9
specified, and R8-A is preserved unchanged.

**The deployed root is partitioned, and the partition is closed.** Region **S**
is every path the reviewed deployment map names; region **D** is the interpreter
and the hash-pinned distributions under `…/venv`. `deployment_manifest_digest()`
covers **both**, as it always did. `deployed_source_manifest_digest()` covers
**region S only**, because region D is not in the reviewed tree and is bound by
its lock file instead (§2.12.5a). **A file in the deployed root belonging to
neither region is a refusal** — at **D5** when it is deployed, and again at
**C0** — which is the failure a whole-tree digest cannot see: the reviewed files
deployed correctly, *and one more*.

**The exact bytes it covers.** Canonical, typed, length-delimited and
schema-versioned, in the encoding `application/idempotency.py`'s
`canonical_request_hash` already establishes, over a list **sorted by path**:

| Included | Detail |
|---|---|
| every regular file under the deployed writer root `/opt/freedom-blades/sheet-writer/`, recursively | its path **relative to that root**, its mode, its uid, its gid, its size, and SHA-256 over its content bytes |
| the deployed unit file `/etc/systemd/system/freedom-sheet-writer.service` | the same five facts, under the fixed relative name `unit:freedom-sheet-writer.service` |
| every drop-in under `/etc/systemd/system/freedom-sheet-writer.service.d/`, sorted | the same five facts, under `unit.d:<name>` — **included because a drop-in silently changes the directives Stage 4 attests**, which is exactly the escalation §9.2 asks the Security Reviewer about |
| a `manifest_format_version` as the first field | so a later manifest definition is a visible, versioned change and not a silent digest drift |

| Excluded, deliberately | Why |
|---|---|
| symlink targets outside the two roots | they are not the writer's bytes; a symlink's own path, mode and target string **are** covered as content |
| timestamps and inode numbers | they differ across two byte-identical deployments and would force a rotation for nothing |
| the Google credential file, wherever D5.0-12 places it | it is not part of the writer's code, it rotates on its own schedule, and hashing a credential's bytes into a sealed artifact is a disclosure this design will not make |
| anything under `/var/lib/freedom-sheet-writer` | that is state, not deployment; including it would make the digest change every time the writer appended a record |

**When it becomes final.** At the end of the deploy step that installs the
writer's files, its unit and its drop-ins and runs `systemctl daemon-reload`. It
is invariant from that instant until the next deployment, and a redeployment
**requires a rotation** — rows **J-22** and **F-6**, and no second invalidation
rule **for a change of deployed bytes**. It is therefore final **before C0**,
which already requires the unit deployed; the ordering is a property of the
deploy procedure, not an assumption. *Amended 2026-09-23 under C-P5.0-R5-R2,
pending review:* a systemd or package identity change is a separate
invalidation condition the digest cannot see — §2.13.2a S4-3 condition 4,
enforced at **W4**/**C-a** under **J-25**, and it also requires a rotation.

**Who computes it, at each point.**

| Actor | When | What it does with the result |
|---|---|---|
| the deploy step | at deployment, **step D7** | computes it over the live installed bytes and records it in the provenance record `PVR` at **D8**, so the operator has a value to supply and a **root-owned artifact** carries it. *Revision 11 had the deploy step merely "print and record" the value with no artifact of its own; that is half of what P5.0-SR1 found* |
| the **operator** | at `init-generation` | **supplies** it on the command line. It is an assertion of *which deployment they intend to seal*, and it is the only thing C0's comparison can be about |
| **root, at C0** | before any probe stage runs | **computes** it over the live deployed manifest and **refuses unless it equals the supplied value**. From this point the algorithm carries the **computed** value and the supplied string is **discarded** |
| **root, at C2** | after C1 | **recomputes** it and refuses on any change, and separately checks `PR`'s copy — a **consistency** check over an already-validated value |
| the **writer, at W11** | at every start | recomputes it and compares with `SB.writer_deployment_digest`; a mismatch is `SW-J22` |

**Why the operator still supplies it, given that C0 computes it.** Because a
generation must be sealed against a deployment somebody **meant**. Without the
supplied value, `init-generation` would silently seal whatever happened to be on
disk — a half-finished deploy, a rollback in progress, a drop-in added minutes
earlier — and the first evidence of the mistake would be `SW-J22` at the next
writer start. The comparison is what makes the operator's intent and the host's
reality agree **before** anything is created, and it is the one thing the
supplied value is good for.

#### 2.13.3 The hierarchy — every artifact, with its authorities

`__GEN__` is the generation's zero-padded sequence, e.g. `000001`. **Two rows
changed in revision 6** — the seal's mode, and the probe arena — and **one row is
added in revision 8**, `…/probe-ro`. All three are remediation, not preference.

| Path | Owner : group | Mode | Filesystem | Created by | Writer (`freedomsheet`) may | Reader (`freedomcoord`) may | Privileged maintenance |
|---|---|---|---|---|---|---|---|
| `/var/lib/freedom-sheet-writer` | `root:root` | `0755` | ext4, `/dev/vda1` | root, at provisioning | traverse | traverse | root |
| `…/journal` | `root:freedomjournal` *(revision 5 said `root:freedomcoord 0751`)* | **`0750`** | ext4 | root, at provisioning | **read and traverse; no `w`**, so it can neither create, unlink, rename nor link | read and traverse | root, through `freedom-journal-admin` |
| `…/journal/__GEN__.journal` | `freedomsheet:freedomcoord` | `0640`, `chattr +a` | ext4 | root, `init-generation` | **read, and open `O_APPEND` and append; nothing else** | read | root only |
| `…/journal/__GEN__.seal` | `root:freedomjournal` *(revision 5 said `root:freedomcoord`)* | `0440`, `chattr +i` | ext4 | root, `init-generation` | **read** — and modify, replace, unlink or rename **nothing** | read | root only |
| `…/journal/current` | `root:root`, symlink → `__GEN__.journal` | — | ext4 | root, `init-generation` | resolve | resolve | root only |
| `…/archive` | `root:freedomcoord` | `0750` | ext4 | root, at provisioning | **nothing — no traverse, no read** | read and traverse | root |
| `…/archive/__GEN__.{journal,seal,close}` | `root:freedomcoord` | `0440`, `chattr +i` | ext4 | root, `seal` | **nothing** | read | root, `dispose` only |
| `…/probe` *(transient; exists only inside `verify-capability`)* | `root:freedomsheet` | **`0770`** *(revision 5 said `root:root 0600` on a file)* | ext4 | root, `verify-capability` | **create, write, truncate, rename and unlink — deliberately** (§2.13.2a) | — | root; **removed before the command exits**, and `init-generation` refuses while it exists |
| `…/probe-ro` *(transient; **new in revision 8**, remediation R7-B)* | `root:freedomsheet` | `0770` | ext4, **the same mount as `…/probe`** | root, `verify-capability` | **create, write, rename and unlink — deliberately, and proved by S4-0**; it holds Stage 4's negative target and is **excluded from the transient unit's substituted `ReadWritePaths=`** | — | root; removed in the same `finally`, and `init-generation` refuses while it exists |

**Why the seal became readable — this is remediation R5-B.** Revision 5 gave
`freedomsheet` no access to the seal and simultaneously required the writer to
validate the seal at start (rows **J-04**, **J-05**, **J-11**, **J-17**). Those
are two different designs. Of the two coherent contracts the handoff permits,
this design takes the first — **grant the minimum read-only access to a
non-sensitive seal** — because the second would move the genesis, inode,
ownership and mode checks out of the writer, and those are exactly the checks
that must happen *before the writer appends*, in a process that has no database
and cannot wait for a human.

**How the grant is made minimal, and why it is not a world-readable file.** The
obvious edit — leave the directory at `0751` and set the seal to `0444` — would
have made the seal readable by **every local identity on the host**, including
`discordbot` and `freedomweb`, because `0751` grants traverse to *other*. That is
a wider grant than the one R5-B asks for. Instead:

- a **third system group, `freedomjournal`**, is created and used for nothing
  else. **Its membership is stated in §2.12.2 and nowhere else** — revision 12
  moves every membership fact into that one canonical table, because revision 11
  stated this group's membership in three passages and stated the opposite in a
  fourth, which is security-review finding **P5.0-SR2**;
- `…/journal` becomes **`root:freedomjournal 0750`**, so *other* loses even the
  traverse it had under `0751` — `discordbot`, `freedomweb` and every other local
  identity can no longer reach anything inside it at all;
- the seal stays **`0440`** and is owned `root:freedomjournal`, so exactly two
  identities may read it and none may write it.

**The net effect on the boundary is a tightening, not a widening, with one
deliberate exception.** `freedomsheet` gains read on one directory and one file it
is required to validate; every identity that is neither the writer nor the
coordinator **loses** the traverse revision 5 gave it. The one grant R5-B asks
for is made, and nothing else is.

**What the writer gains, and what it does not.** It gains `open(O_RDONLY)` on the
seal and on the journal, and the ability to list `…/journal`. Listing was never a
control — **the write bit is** — and revision 5's *"no `r`"* was incidental to it.
It gains **no** access to `…/archive`, which stays `root:freedomcoord 0750` with
the writer as *other*, and no way to alter the seal: `chattr +i` refuses every
write, and the containing directory is not writable by it, so it cannot unlink,
rename or replace it either. **The seal's integrity was never protected by its
confidentiality**; it is protected by `+i` and by a directory the writer cannot
write, and neither of those weakens by one step.

**The cost, stated where the decision is made.** One more system group is a change
to the accepted host topology, so it is added to **D5.0-12 / OD-65**'s scope
alongside the `freedomsheet` identity, and to **D5.0-13 / OD-66** option A's cost.
It is not adopted here. **And the cost revision 11 did not state is that the
coordinator and one service identity now share a group** — §2.12.2 records that,
withdraws the sentence that denied it, and states the three claims that remain
true; `JNL-52` tests them.

**The disclosure, assessed rather than asserted.** The seal contains the
generation id and sequence, the writer unit name, the writer deployment digest,
`/etc/machine-id`, the journal path, the expected uid/gid/mode, the filesystem
type, the predecessor identifiers and close digest, and the probe report. **None
of it is credential material, and none of it is player data.** The writer already
knows its own unit, its own path, its own deployment (it can hash its own files)
and `/etc/machine-id`, which is world-readable by distribution convention. The
predecessor's close digest names an archive the writer cannot open. So the
disclosure does not enable any row of §2.13.4, and it does not narrow any
guarantee in §2.10.3. It **is** a deliberate widening of the boundary §2.13
draws, so it is listed as security-review surface 11 in §9.2 with a question
attached, rather than settled here by the implementer.

**Three properties of that table are the whole control**, and each is a
permission fact rather than an argument:

1. **`…/journal` is not writable by the writer.** Every one of `unlink(2)`,
   `rename(2)`, `link(2)`, `creat(2)` and `open(O_CREAT)` in that directory
   requires write permission *on the directory*, which mode `0750` with owner
   `root` and group `freedomjournal` denies to `freedomsheet` — the group bits are
   `r-x`, and there is no `w` for anyone but root. This is what makes the journal
   something the writer can read and add to, and not something it owns.
2. **`chattr +a` is a second, independent layer** over the first, not the only
   one. Revision 4 leaned on it alone; revision 6 would still satisfy (c) of
   §2.13.2 without it.
3. **The parent is root-owned too.** `/var/lib/freedom-sheet-writer` is
   `root:root` and `/var/lib` is `drwxr-xr-x root:root` (read 2026-08-29), so the
   `journal` directory itself cannot be renamed or shadowed by any service
   identity. The handoff asks for protection against parent-directory
   manipulation, and this is it.

**And a fourth, new in revision 6:** *reading is not writing.* The writer may
read the journal and the seal and may append to the journal, and that is the
complete list. It cannot modify, replace, rotate, seal, archive or dispose of
anything, and §2.13.4 proves each of those one `errno` at a time.

**The unit is hardened to match.** `freedom-sheet-writer.service` carries
the directives below, each exactly once. *Amended 2026-09-23 under
C-P5.0-R5-R1, pending review:* this said *"at least"*, which S4-3's closed
allowlist (§2.13.2a, condition 1) no longer permits — an authority-bearing
directive not listed here, in the unit or in a drop-in, makes S4-3
`inconclusive`. `ExecStart=`, `Type=` and non-authority lifecycle directives are
on the allowlist beside them. The comment on `TimeoutStopSec=` is this
document's annotation; systemd does not strip a trailing comment, so it is not
part of the deployed line:

```
User=freedomsheet
Group=freedomsheet
NoNewPrivileges=true
CapabilityBoundingSet=
AmbientCapabilities=
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ProtectProc=invisible
RestrictSUIDSGID=true
ReadOnlyPaths=/var/lib/freedom-sheet-writer
ReadWritePaths=/var/lib/freedom-sheet-writer/journal
KillSignal=SIGTERM
TimeoutStopSec=45          # N5.0-17
Restart=on-failure
```

Two of those lines carry weight and should not be read as boilerplate.
`CapabilityBoundingSet=` **empty** removes `CAP_LINUX_IMMUTABLE` from the
process's bounding set, so the writer could not clear `+a` even if it somehow
obtained uid 0 — and `NoNewPrivileges=true` closes the route by which it might.
`ReadWritePaths=` grants **nothing the directory mode does not already grant**;
its only job is to stop `ProtectSystem=strict`'s read-only bind mount from being
the reason the append fails, so that a refusal is always the *journal's* refusal
and never systemd's. **`…/probe` and `…/probe-ro` are deliberately outside the deployed unit's
`ReadWritePaths=`**, so the writer *inside its own unit* cannot reach either
even while they exist; stages 1–3 run the writer's **uid** through `setpriv` from
the root wrapper, outside any unit, which is what makes them a test of the
filesystem rather than of the sandbox.

**Stage 4 is the deliberate exception, and it is not a contradiction of the
previous sentence.** It runs in a **transient** unit `systemd-run` creates, whose
`ReadWritePaths=` is redirected to the arena — **and to the arena only**, which is
what leaves `…/probe-ro` inside `ProtectSystem=strict`'s read-only tree for
**S4-2** — precisely so the sandbox can be exercised **without touching live
evidence** (§2.13.2a). The deployed `freedom-sheet-writer.service` above is
unchanged: it names neither transient directory, and the writer in production
cannot reach either. The evidence for all of this is `TC-5.0-JNL-13`, `JNL-29`
and, for the S4-0/S4-2 pair, `JNL-48`.

#### 2.13.4 What each named manipulation runs into

The handoff requires protection against unlink, rename, replacement, truncation
and parent-directory manipulation — *not merely writes to an open file*. One row
each, with the mechanism and the expected `errno`, because a claim of this shape
is only worth what its test asserts. **Two rows changed in revision 6**, both
about the seal, and **two rows are added in revision 10** — the flag changes
themselves, on the seal and on an archived file, which revision 9's register
described and this table did not contain. **Fifteen rows**, and `JNL-13` asserts
fifteen.

| Attempt, as `freedomsheet` | First mechanism that refuses | Second, independent mechanism | Expected |
|---|---|---|---|
| `unlink("…/journal/__GEN__.journal")` | no write permission on `…/journal` (`0750`, group `r-x`) | `chattr +a` on the file refuses unlinking even with directory write permission | `EACCES` |
| `rename(…)` the journal | as above | as above | `EACCES` |
| `open(…, O_CREAT)` a replacement, then `rename` over it | no write permission on `…/journal` | the coordinator compares `(st_dev, st_ino)` against the registered generation (row **J-11**), and the writer compares it against the seal's binding section at start | `EACCES` |
| `open(…, O_WRONLY)` without `O_APPEND`, then `pwrite` at offset 0 | `chattr +a` refuses a non-append open | the hash chain makes a rewrite detectable after the fact | `EPERM` |
| `open(…, O_TRUNC)` or `ftruncate` | `chattr +a` | the coordinator's chain and sequence check | `EPERM` |
| `chattr -a` the journal | `CAP_LINUX_IMMUTABLE` absent from the process's bounding set | `NoNewPrivileges=true` | `EPERM` |
| **`chattr -i` the seal** — **new in revision 10** | `CAP_LINUX_IMMUTABLE` absent, as above (**A1**) | **and, independently, the seal is `root`-owned, so `FS_IOC_SETFLAGS` requires effective UID 0 or `CAP_FOWNER` (`A11`), which the writer holds by neither route.** *Two independent kernel checks refuse this, and revision 9's register recorded only the first* | `EPERM` |
| **`chattr -i` an archived file** — **new in revision 10** | `…/archive` is `0750 root:freedomcoord` and the writer is *other*, so no file descriptor can be obtained at all | and, were one obtained, **A1** and **A11** are both absent | `EACCES` at the directory; `EPERM` from the ioctl on a descriptor obtained by any other means |
| `rename`/`rmdir` the `…/journal` directory | no write permission on `/var/lib/freedom-sheet-writer` (`root:root`) | `/var/lib` is `root:root 0755` | `EACCES` |
| **read the seal** | — | — | **succeeds, by design — revision 6, §2.13.3.** It is the one row whose answer changed, and it changed because the writer is required to validate the seal |
| **modify, truncate or replace the seal** | `chattr +i` | mode `0440` denies write to every identity including its owner's group; and `…/journal` is not writable by the writer, so it cannot rename over it either | `EPERM` on an `O_WRONLY` open of the seal; `EACCES` on a create-and-rename in `…/journal` |
| **unlink or rename the seal** | no write permission on `…/journal` | `chattr +i` | `EACCES` |
| read, modify or delete anything under `…/archive` | mode `0750 root:freedomcoord`; **the writer is *other* and is not in `freedomcoord`** | `chattr +i` on each archived file | `EACCES` |
| repoint `…/journal/current` | the symlink is `root:root` in a directory the writer cannot write | the writer resolves it and then verifies `(st_dev, st_ino)` and the derived genesis digest against the seal | `EACCES` |
| create, rename or unlink anything in `…/probe` **or `…/probe-ro`** **while a generation is live** | neither directory exists outside `verify-capability` — except as **S-B** residue after a failed cleanup (§2.13.2b) — and `verify-capability` refuses while the writer unit is active | **both** `verify-capability` and `init-generation` **C0** refuse while either exists, and **neither cleans it**; the deployed unit's `ReadWritePaths=` excludes both, so the writer inside its own unit cannot reach either even when S-B residue is present | `ENOENT` normally; `EACCES` from inside the writer's unit against S-B residue |

**The claim this table is making, stated plainly:** *the writer can read the
journal and its seal, can append to the current journal, and can do nothing else
to either — nor to their siblings, their directory or their parent.* That is the
handoff's *"the writer must remain unable to modify, replace, rotate, seal,
archive, or dispose of evidence"*, and it is proved one `errno` at a time by
`TC-5.0-JNL-13` and `JNL-33` rather than argued.

**Two of these rows are refused twice over, and revision 10 says which check
fires first.** The writer's `chattr -a` on its **own** journal file is refused by
the absent capability **alone** — the writer owns that inode, so `FS_IOC_SETFLAGS`'s
owner requirement (**A10**) is satisfied by ownership, and the empty
`CapabilityBoundingSet=` is the whole of the refusal. Its `chattr -i` on the
**seal** is refused by the absent capability **and, independently**, by the
absent owner authorization over a root-owned inode (**A11**). §2.13.5c's register
is written so those two facts are separate rows rather than one label, and
`JNL-50` cases 3 and 4 execute them separately for exactly that reason.

#### 2.13.5 The generation — and why a reset can never look like an empty history

A **journal generation** is the durable identity of one journal file. It is
created only by a privileged act, and it is the mechanism that answers the
handoff's third requirement.

**What a generation carries.** The table below is grouped by *which artifact the
value first exists in*, because that grouping is what makes §2.13.5a's order
checkable — and revision 5's flat list is what hid the cycle.

| Group | Field | Meaning | Bound to |
|---|---|---|---|
| **Seal body** — fixed before the journal file exists | `generation_id` | random UUID, never reused | the generation |
| | `generation_seq` | strictly increasing from 1, one linear chain | its predecessor |
| | `writer_unit` | `freedom-sheet-writer.service` | the deployment |
| | `writer_deployment_digest` | SHA-256 over the deployed writer's file manifest — **`deployment_manifest_digest()` of §2.13.2c**, computed by root at **C0** and compared with the operator's supplied value before anything consumes it. *Revision 8 sealed a value validated only against a copy of itself, at C2, after C1 had consumed it* | **the writer deployment**, as the handoff requires, and to the **deployed bytes** rather than to the operator's assertion about them |
| | `host_machine_id` | `/etc/machine-id` | the host, so a journal restored onto another host is refused **unless `/etc/machine-id` there is rewritten to this value**, which nothing in this design detects — **F-7**, residual **R-5.0-13**. *Revision 8 stated the refusal without that bound* |
| | `journal_path`, `journal_uid`, `journal_gid`, `journal_mode` | the expected identity and permissions of the file | the hierarchy of §2.13.3 |
| | `filesystem_type`, `probe_device` | `ext4`, and the `st_dev` Stage 3 tested | the storage actually probed |
| | `append_only_probe_version`, `append_only_probe_at`, and the **full probe report** | §2.13.2a's four stages and every one of their cases — `C-1 … C-6`, `P-1 … P-9`, `M-1 … M-2`, `S4-0 … S4-3` — with its expected and observed result. **All four stages run before the report is built** (revision 7, R6-A), **and every negative case is preceded by its positive control** — Stage 1 for Stage 2, `S4-0` for `S4-2` (revision 8, R7-B) | the probe, verifiably — the report is *in* the seal, not merely asserted about it |
| | `binding_format_version` | the exact structure and length of the binding section below | **new in revision 7.** It lives in the *body*, which record 0 authenticates, so the binding cannot be re-parsed at another version (**R6-B**) |
| | `predecessor_generation_id`, `predecessor_seq`, `predecessor_close_digest` | the sealed predecessor and its close manifest; all three absent, as typed nulls, for the first generation | the chain |
| | `created_at` | the instant the seal body was fixed; also the genesis record's `at` | — |
| **Derived from the seal body alone** | `seal_body_digest` | SHA-256 over the canonical seal body | everything above |
| | `genesis_record_digest` | the `record_hash` of the journal's record 0, whose whole content is determined by the seal body | the file's first record — **computable before the file exists**, which is what removes the cycle |
| **Seal binding** — fixed after the journal file exists | `genesis_record_digest` | the digest **derived** above, recorded so a reader who has the seal need not read the journal to obtain it | the seal body, and re-derived at **W5** |
| | `journal_device`, `journal_inode` | `st_dev`, `st_ino` of the created journal file | the inode, so a replacement is detected; compared at **W7** |
| | ~~`sealed_at`~~ | ~~when the binding was written~~ | **Withdrawn in revision 7 — remediation R6-B.** No **V-W** step authenticated it and no operative decision read it, so its presence made F-1's whole-seal claim false. The generation's creation instant is `SB.created_at`, which record 0 authenticates; the registration instant is the registered row's `created_at`, which is PostgreSQL's clock; the sealing instant is in the `.close` manifest. **The binding section now holds exactly three fields, and V-W validates every one of them** (§2.13.5b) |
| **Derived from the finished seal file** | `seal_digest` | SHA-256 over the seal file's exact bytes | the seal itself. **Nothing on disk contains it**; it is recomputed by every reader and registered in PostgreSQL |

It lives in three places that must agree: the **immutable seal file**, the
**genesis record inside the journal**, and the **registered row in PostgreSQL**
(logical schema §3.7). The coordinator refuses if any two disagree.

**Why a newly created or reset journal is never indistinguishable from a valid
empty history — three independent reasons, unchanged in substance from revision
5 and now actually constructible.**

1. **A valid journal is never empty.** Record 0 is a `genesis` record whose entire
   content is determined by the seal body, and whose digest is recorded in the
   `chattr +i` seal's binding section. A zero-length file, or a file whose first
   record is not the record the seal body *derives*, is **invalid** — rows
   **J-04** and **J-17** — and invalid is a refusal, not a clean slate.
2. **The generation must be registered, current and unsuperseded.** The
   activation trigger refuses `dispatch_journal_clear` evidence whose
   `journal_generation_id` is not the head of the registered chain, and refuses
   any evidence observed before a later generation was registered. A journal
   nobody registered fences nothing.
3. **Creating a generation requires sealing the one before it.**
   `init-generation` refuses while a predecessor is unsealed, and the new seal
   body's `predecessor_close_digest` is required and comes from the predecessor's
   `.close` manifest. **So "reset the journal so it looks empty" first requires
   sealing and archiving the very history it was meant to erase**, as root,
   audited, into an immutable file the writer cannot read.

**The writer still never touches PostgreSQL.** Registration is performed by the
**coordinator**, at provisioning and at rotation, by a human, through
`RegisterJournalGeneration`. The writer validates against the on-disk seal and
journal alone — which it can now do, because §2.13.3 lets it read the seal. This
is deliberate and is the same property revision 3 won by withdrawing the lease:
**the Freedom bot's legacy mutation path takes no database dependency**, and
revision 6 does not give it back.

#### 2.13.5a The creation order — acyclic, byte-exact, and stated as an algorithm. **New in revision 6; this is remediation R5-A**

Revision 5 said the genesis record's `prev_hash` is `seal_digest` while the seal
contains `genesis_record_digest`. **Neither value can be computed first, so no
generation could be created.** The fix is not a smaller hash: it is to split the
seal into a **body**, fixed before the journal exists, and a **binding section**,
fixed after it exists, and to anchor the genesis record to the **body** rather
than to the whole file.

**Canonical encoding.** Every digest below is SHA-256, rendered lowercase hex,
over the typed, length-delimited, schema-versioned encoding that
`application/idempotency.py`'s `canonical_request_hash` already establishes.
Absent values are encoded as a typed null, never as an empty string, so a first
generation and a successor cannot collide. Every structure carries a
`format_version` as its first field.

**Algorithm C — create a generation.** Executed by `freedom-journal-admin
init-generation`, as root, with the writer unit **inactive** and `…/probe`
**absent**.

| Step | Actor | Action | Bytes hashed, exactly | Already exists | Durability |
|---|---|---|---|---|---|
| **C0** | root | **Corrected again in revision 9; this is remediation R8-A.** Refuse unless every **pre-probe** precondition holds. Each is observable *before* any probe stage runs and **none refers to a probe result**: the writer unit is **inactive**; **its unit file is deployed**, so §2.13.2a Stage 4 has directives to read; `…/journal` and `…/archive` exist with the §2.13.3 owners and modes; **`…/probe` and `…/probe-ro` are absent**, and **neither is cleaned if present** — the run refuses and reports the residue (§2.13.2b); the predecessor generation (if any) is **sealed and archived** and its `.close` manifest verifies; a `writer_deployment_digest` **was supplied** and is well-formed (64 lowercase hex); and — **new in revision 9** — root **computes** `DD` = `deployment_manifest_digest()` over the deployed manifest of §2.13.2c and **refuses unless the supplied value equals `DD`**. **The supplied string is then discarded**: every later step consumes `DD`, the value validated against the deployed bytes. *Revision 8's C0 checked only that a digest "was supplied", and left its equality to **C2** — after **C1** had already passed it to the probe, and against the probe's copy of that same string, which is a tautology (§2.13.1 defect 18)*. **And — new in revision 12, remediation R11-A — the reviewed-source provenance preconditions of §2.12.5a, every one of them fail-closed:** the provenance record `PVR` and the approval record `APR` are **present**, `root:root`, mode `0444`, structurally valid and name this component — **an absent record refuses, and there is no path in which its omission is a default**; `PVR` and `APR` agree on `source_commit`, `source_tree_id` and `source_manifest_digest`; root **recomputes `TM` = `source_manifest_digest()` from the Git object bytes of `APR.source_commit`'s tree in the `0700 root:root` bare store**, by object id and through no ref, and refuses on disagreement; root **recomputes `SM` = `deployed_source_manifest_digest()` over the live deployed bytes** and refuses unless it equals `TM`; the deployed root's file set is exactly regions **S ∪ D** with **no unaccounted file**; `PVR.deployment_manifest_digest` equals `DD`; and the operator's supplied `--source-commit` equals `APR.source_commit`, **that string then being discarded exactly as the supplied digest is**. *Revision 11's C0 read no provenance artifact at all, which is §2.13.1 defect 29* | `DD` = `deployment_manifest_digest()` over §2.13.2c's manifest; `TM` = `source_manifest_digest()` over the reviewed Git tree; `SM` = `deployed_source_manifest_digest()` over the live bytes | the deployed writer and its unit; **`APR`, `PVR` and the reviewed commit in the root-owned object store** | — |
| **C1** | root | Run §2.13.2a **stages 1–4** in this process, in one `verify-capability` invocation; clean up the arena and the Stage-4 target directory; and build the **probe report** `PR` from all four stages. **This is the only invocation of the probe stages anywhere in Algorithm C, and the only creation point of `PR`.** The digest it records is **`DD`**, the value C0 computed and compared — not the operator's string, which no longer exists at this point. If the `finally` cleanup does not complete, the run ends in state **S-B** of §2.13.2b and no later step executes | `PR` = canonical(probe format version, `append_only_probe_version`, `append_only_probe_at`, `filesystem_type`, `probe_device`, mount flags, **`DD`**, the deployed unit file's digest, the applied directive-set digest and the recorded `ReadWritePaths=` substitution, the Stage-4 target path and its `st_dev`, and **every case `C-1 … C-6`, `P-1 … P-9`, `M-1 … M-2`, `S4-0 … S4-3`** with its expected and observed result) | `DD` from C0; the arena and `…/probe-ro`, both created and destroyed within this step | **`PR` is held in memory. It reaches disk only inside the seal body, written at C9** |
| **C2** | root | **New in revision 8; its digest check corrected in revision 9 (R8-A).** Check the **result-dependent** facts — the ones that exist only now that C1 has run — and refuse before any persistent artifact exists: `PR` carries **all four stages** and every one of their cases; every case's observed result equals its expected result, so the overall result is **`passed`** and neither `inconclusive` nor `failed`; **`PR.writer_deployment_digest` equals `DD`**, a **consistency** check over an already-validated value rather than a validation (§2.13.2c); **root recomputes `deployment_manifest_digest()` a second time and refuses unless it still equals `DD`**, which is what detects a deployment changed between C0's comparison and the probe's capture; and C1's privileged cleanup **completed**, so neither `…/probe` nor `…/probe-ro` exists. **Nothing has yet been written under `…/journal`**, so a refusal here leaves **no generation and no database artifact** in every case, and **no transient residue** where cleanup succeeded — §2.13.2b **S-A** and **S-B**, asserted by `JNL-47` | `probe_report_digest` = SHA-256(`PR`), computed **once**, here, after the checks that admit `PR`; and a second `deployment_manifest_digest()` observation, which is compared and then discarded | C1, `DD` | in memory |
| **C3** | root | Build the **seal body** `SB`, carrying **`DD`** as `writer_deployment_digest` | `SB` = canonical(format version, **`binding_format_version`**, `generation_id`, `generation_seq`, `writer_unit`, `writer_deployment_digest` = **`DD`**, **`source_commit`**, **`source_tree_id`**, **`source_manifest_digest` = `TM`**, **`approved_revision_reference`** *(the four provenance fields are new in revision 12; they are fixed before the journal exists, so they belong in the body and introduce no cycle)*, `host_machine_id`, `journal_path`, `journal_uid`, `journal_gid`, `journal_mode`, `filesystem_type`, `probe_device`, `append_only_probe_version`, `append_only_probe_at`, `probe_report_digest`, `PR`, `predecessor_generation_id`, `predecessor_seq`, `predecessor_close_digest`, `created_at`). **Excludes** `genesis_record_digest`, `journal_device`, `journal_inode` and `seal_digest` — and that exclusion *is* remediation R5-A. **`binding_format_version`** fixes the binding section's exact structure and length from **inside** the chain-authenticated body, so the binding cannot be re-parsed at another version (**R6-B**) | C2 | in memory |
| | | `seal_body_digest` = SHA-256(`SB`) | | | |
| **C4** | root | **Derive** the genesis record `G`, whose content is a pure function of `SB` | body = canonical(format version, `generation_id`, `seq = 0`, `kind = 'genesis'`, `at = SB.created_at`, `seal_body_digest`); `prev_hash` = `seal_body_digest`; `record_hash` = SHA-256(`prev_hash` ‖ body) | C3 | in memory |
| | | `genesis_record_digest` = `G.record_hash`. **Any holder of the seal body can recompute this without reading the journal**, which is the property that removes the cycle and the property `JNL-31` asserts | | | |
| **C5** | root | `open("…/journal/__GEN__.journal", O_CREAT\|O_EXCL\|O_WRONLY, 0640)`; `fchown` to `freedomsheet:freedomcoord`; `fchmod 0640`; write `G`; `fsync(file)`; `fsync(dir)`. **This is the first persistent artifact Algorithm C creates**, and every refusal above it creates **no generation and no database artifact** — invariant **I-4**. *Revision 8 said such a refusal "leaves the tree untouched", which is not true of the transient directories when cleanup fails; §2.13.2b states the three states and the failure-cost table above states them per step* | — | C4 | **`fsync` file, then directory.** The file and its name are durable before anything refers to it |
| **C6** | root | `chattr +a` (`FS_IOC_SETFLAGS`, `FS_APPEND_FL`) on the journal; re-read `FS_IOC_GETFLAGS` and refuse if it is not set | — | C5 | attribute change is metadata; `fsync(file)` again |
| **C7** | root | `fstat` the journal → `journal_device`, `journal_inode`. Refuse unless `journal_device` equals `PR.probe_device` | — | C6 | — |
| **C8** | root | Build the **seal binding** `BND` | `BND` = canonical(`genesis_record_digest`, `journal_device`, `journal_inode`), encoded at the `binding_format_version` `SB` declares and carrying **no format field of its own**. **Three fields, and every one of them is recomputed or compared by V-W** (§2.13.5b) | C7 | in memory |
| **C9** | root | Write the seal file to `…/journal/__GEN__.seal.tmp` as `SB` ‖ `BND`, and **nothing else** — its total length is exactly `len(SB) + len(BND)`, so a trailing byte is detectable; `fchown root:freedomjournal`; `fchmod 0440`; `fsync(file)`; `rename` to `…/journal/__GEN__.seal`; `fsync(dir)` | **this is the only step that writes `PR` to disk** | C8 | **`fsync`, then atomic `rename`, then `fsync` the directory.** The seal is never observable half-written |
| **C10** | root | `chattr +i` on the seal; re-read and refuse if not set | — | C9 | `+i` is set **after** the rename, because an immutable file cannot be renamed |
| **C11** | root | Create `…/journal/current.tmp` as a symlink to `__GEN__.journal`; `rename` it over `…/journal/current`; `fsync(dir)` | — | C10 | atomic replacement of the pointer, last |
| **C12** | root | Compute `seal_digest` = SHA-256 over the **exact bytes of the finished seal file**, and print the values the operator must pass to `RegisterJournalGeneration`. **Nothing on disk contains `seal_digest`** | the seal file | C11 | — |
| **C13** | coordinator, **not root** | `migration-authority register-journal-generation` — Algorithm V-R below, then one transaction inserting the row, its receipt and its audit event | — | C12 | PostgreSQL |

**Why the order changed, conceded before the replacement is presented.**
Revision 7's **C0** refused unless `verify-capability` had *"passed in this
invocation, all four stages"*, with a report whose `writer_deployment_digest`
matched the supplied one — and **C1 was the step that ran those stages and built
that report**. An ordered algorithm cannot validate an output before producing
it, so revision 7's Algorithm C had no executable order at all: C0 could never be
satisfied on a first pass, and any implementation that appeared to work would
have been running the probe twice or reading a report from a previous
invocation, neither of which the algorithm authorizes. **Revision 8 takes the
re-review's preferred minimal correction**: C0 keeps only what exists before the
probe, C1 remains the single creation point, and the result-dependent
requirements move to a new **C2** that runs after C1 and before any persistent
artifact. **The probe still runs exactly once**, `PR` still has exactly one
creation point, and no step consumes a value a later step produces.

**Why the order changed again in revision 9, conceded before the replacement is
presented.** Revision 8's correction fixed the *ordering* of the probe report and
left the **deployment digest** wrong in both halves. The value was consumed at
**C1** and its equality checked at **C2**, so `consumed < validated` in the very
first row of the table that asserted the opposite; and the C2 check compared
`PR`'s copy of the digest with the string that copy was **made from**, which
succeeds for any string whatever. **Revision 9 corrects the design rather than
the inequality.** C0 now **computes** the digest from the deployed manifest —
§2.13.2c says who computes it, over exactly which bytes, and when it becomes
final — and refuses unless the supplied value equals it, so the digest C1
consumes has been validated **against an independent source**. C2 keeps a
**post-production consistency check** and adds a **second computation**, which is
the only thing that detects a deployment changed between C0 and the probe's
capture. The probe still runs exactly once and `PR` still has one creation point.

**And the universal inequality is withdrawn, because it was the wrong shape.**
*"produced < validated ≤ consumed"* cannot hold for every value: values produced
**inside** the algorithm are checked **after** the step that produces them and
often after a later step has already used them as an input, and derived values —
pure functions of validated inputs — are not validated at all. Stating one
inequality for all of them either forces a false claim or forces the word
*validated* to mean two different things in one table. Revision 9 states the two
things separately, as five invariants:

| # | Invariant | Applies to | What it forbids |
|---|---|---|---|
| **I-1** | **Production precedes use.** For every value, the step that produces it strictly precedes the step that first consumes it | every value | a step consuming a value a later step produces — the R7-A defect |
| **I-2** | **Pre-consumption validation of external inputs.** Every value entering the algorithm **from outside it** is validated against a source **independent of that value** at or before the step that first consumes it: `produced < validated ≤ first consumed` | `writer_deployment_digest` (supplied), the deployed unit file and its drop-ins, the predecessor `.close` manifest, the absence of `…/probe` and `…/probe-ro` | consuming caller-supplied text before checking it against the host, and “validating” it against a copy of itself — the R8-A defect |
| **I-3** | **Post-production consistency checking of internal values.** Every value **produced inside** the algorithm that has a check is checked after its producing step and **before the first step that makes a persistent artifact depend on it**: `produced < checked ≤ first persistent dependence` | `PR` (checked at C2, first persistent dependence C9), the journal file (C6, C7), the seal file (C10) | sealing a probe result nothing examined, or setting an attribute and not re-reading it |
| **I-4** | **No persistent artifact before the checks.** No step at or before **C4** creates anything under `…/journal` or in PostgreSQL. **C5** is the first persistent artifact and **C13** the first row | the whole algorithm | a refusal that leaves a half-created generation behind at C0 … C4 |
| **I-5** | **Derived values carry no validation row.** A pure function of already-validated inputs is not separately validated; its correctness is its inputs' correctness plus an **independent re-derivation by a later reader** | `probe_report_digest`, `seal_body_digest`, `G`, `genesis_record_digest`, `BND`, `seal_digest` | inventing a validation step for a value nothing could disagree with, which is how a table acquires rows that assert nothing |

**I-2 and I-3 are the distinction the R8 brief asks for**, and the *class* column
of the table below says which one governs each row. `JNL-46` asserts all five.

**The value-dependency table, so the invariants are checkable rather than
asserted.** Every value Algorithm C consumes appears here with its **class**
under I-2 / I-3 / I-5, the step that produces it, the step that validates or
checks it, and the step that first consumes it. **No single inequality is
claimed for all rows**; each row satisfies the invariant its class names, and the
final column says which fact the check establishes.

| Value | Class | Produced at | Validated / checked at | First consumed at | What the check establishes |
|---|---|---|---|---|---|
| `writer_deployment_digest` **as supplied by the operator** | **I-2** external input | before C0, by the operator | **C0** — well-formedness, **and equality with `DD`, computed by root over the deployed manifest** | **nothing consumes it.** It is compared at C0 and **discarded**; every later step consumes `DD` | that the deployment the operator meant to seal is the deployment on disk. *Revision 8 consumed this value at C1 and compared it at C2 against a copy of itself* |
| `DD` = `deployment_manifest_digest()` | **I-3** internal | **C0** | **C0** (against the supplied value); **C2** (recomputed, and compared with `PR`'s copy) | C1 (recorded in `PR`), C3 (into `SB`) | that the sealed digest is computed from the deployed bytes, and that those bytes did not change between C0 and the probe's capture |
| the deployed unit file and its drop-ins | **I-2** external input | before C0, by deployment | **C0** deployed and inside `DD`'s manifest; **C1** S4-3 captures and hashes the applied directive set | C0 (into `DD`), C1 | that Stage 4 exercised the directives the writer will run under, and that a drop-in cannot change them without changing `DD` |
| `APR` — the approved revision **(new in revision 12)** | **I-2** external input | before C0, by root, out of band | **C0** — present, `root:root 0444`, well-formed, this component; and equal to `PVR` on all three provenance values | C0 (its `source_commit` is compared with the operator's supplied value; its three values reach `SB` through `TM`) | that a review approved the revision the deployment claims. **Its integrity is root ownership and mode — R-5.0-15** |
| `PVR` — the provenance record **(new in revision 12)** | **I-2** external input | at deployment, **D8** | **C0** — present, `root:root 0444`, well-formed; equal to `APR`; and `PVR.deployment_manifest_digest` equal to `DD` | C0 | that the deployment on disk is the one the deploy step verified against the reviewed commit, and **that the provenance step was not omitted** |
| `TM` = `source_manifest_digest()` over the reviewed Git tree **(new in revision 12)** | **I-3** internal | **C0**, from the object store | **C0** — against `APR.source_manifest_digest`, and against `SM` computed over the live bytes | C3 (into `SB`) | that the sealed source manifest was produced from an **immutable, content-addressed reviewed object**, not from the bytes being checked. *This is the whole of the P5.0-SR1 remediation in one row* |
| `SM` = `deployed_source_manifest_digest()` **(new in revision 12)** | **I-3** internal | **C0**, over the live deployed bytes | **C0** — against `TM` | **nothing consumes it.** It is compared at C0 and discarded; the writer recomputes its own at **W11a** | that the bytes on disk are the reviewed bytes, and that no unaccounted file was added |
| `…/probe`, `…/probe-ro` absent | **I-2** external input | — | **C0**, and **not cleaned if present** (§2.13.2b) | C1 creates them | that no residue of a crashed run is reused or silently removed |
| predecessor sealed, archived, `.close` verified | **I-2** external input | the predecessor's `seal` | **C0** | C3 (`predecessor_close_digest` into `SB`) | that no history was skipped or erased unsealed |
| `PR` and every case result | **I-3** internal | **C1** | **C2** | C2 (digest), C3 (into `SB`) | that all four stages ran, every case passed, cleanup completed, and `PR` carries `DD` |
| `probe_report_digest` | **I-5** derived | **C2** | — | C3 | — (a pure function of a checked `PR`; re-derived by the writer at **W4**) |
| `SB`, `seal_body_digest` | **I-5** derived | **C3** | — | C4 | — (re-derived by the writer at **W3**, and against record 0 at **W13**) |
| `G`, `genesis_record_digest` | **I-5** derived | **C4** (from `SB` alone) | — | C5 (written to the journal), C8 (recorded in `BND`) | — . **V-W W5** re-derives it from `SB` at every writer start, which is what makes the anchor **derivable rather than merely recorded** and is what removed the revision-5 cycle |
| the journal file | **I-3** internal | **C5** | **C6** (`+a` re-read), **C7** (`st_dev` = `PR.probe_device`) | C7 | that the file is on the filesystem the probe tested and carries the attribute |
| `journal_device`, `journal_inode` | **I-5** derived | **C7** | — | C8 | — (compared by the writer at **W7** against `fstat`) |
| `BND` | **I-5** derived | **C8** | — | C9 | — |
| the seal file | **I-3** internal | **C9** | **C10** (`+i` re-read) | C12 | that the seal is immutable before anything depends on it |
| `seal_digest` | **I-5** derived, and a **leaf** | **C12** | — | C13 | nothing on disk consumes it; it is recomputed by every reader and registered in PostgreSQL |

**Read the table against the invariants, not against a single inequality.** Every
**I-2** row is validated at or before its first consumption, against a source
that is not itself; every **I-3** row is checked after its producing step and
before **C9**/**C5**, the steps that make a persistent artifact depend on it;
every **I-5** row is a pure function whose correctness a later, independent
reader re-derives. **I-1 holds for every row without exception**, and **I-4** is
the property the failure-cost paragraph below states.

**What a refusal costs at each step, corrected in revision 9 so that one
injected failure has one outcome.** Revision 8 said a refusal at C0, C1 or C2
*"leaves the tree exactly as it was … and no `…/probe` or `…/probe-ro` residue"*.
**The second half of that is not unconditional**, and requiring it alongside
`JNL-48(d)`'s planted undeletable residue is what made the evidence contract
unsatisfiable (§2.13.1 defect 19). The two claims are now stated separately:

| Refusal at | Generation artifact — journal, seal, `current`, `.close` | Database row | Transient residue | Recovery |
|---|---|---|---|---|
| **C0** | **none, unconditionally** | none | unchanged — the run creates neither directory, and **refuses rather than cleaning** any it finds | fix the named precondition, or clear reported residue by the §2.13.2b operator procedure, then re-run |
| **C1** or **C2**, **cleanup succeeded** — §2.13.2b **S-A** | **none, unconditionally** | none | **none** | re-run |
| **C1** or **C2**, **cleanup failed** — §2.13.2b **S-B** | **none, unconditionally** | none | **exactly the artifacts named in the residue report**, by absolute path | operator recovery per §2.13.2b, then re-run. **A re-run before that refuses at C0** |
| **C5 … C11** | a **partially constructed, unregistered** generation, whose `current` symlink still points at its predecessor (or at nothing, for a first generation) | none | none — C1's cleanup ran long before | `init-generation` names the partial artifacts and exits non-zero; **`repair`, not a re-run, is the documented recovery**, because `O_EXCL` at C5 refuses to overwrite them |
| **C13** | a complete, sealed, **unregistered** generation | none | none | row **J-16** already refuses it at the coordinator, and no writer may use it |

**“No generation or database artifact” is unconditional in every row above C5;
“no transient residue” is conditional on cleanup success, and is stated that
way.** `JNL-47`'s six cases produce exactly these rows.

**The dependency graph, so acyclicity is checkable rather than claimed.**

```
deployed manifest ──▶ DD (C0) ──▶ [I-2 gate: DD == supplied, C0] ──┐
       │                                                            │
       │  (recomputed at C2, compared with DD and with PR's copy)   │
       ▼                                                            ▼
 probe stages 1-4 (C1) ──▶ PR ──▶ [I-3 gate: checked, C2] ──▶ probe_report_digest ──▶ SB ──┐
                                                                                            │
                                   seal_body_digest ◀────────────────────────────────────────┘
                                          │
                                          ▼
                                   G ──▶ genesis_record_digest ─┐
                                          │                      │
                      journal file (C5) ──┴──▶ (device, inode) ──┤
                                                                 ▼
                                                               BND
                                                                 │
                                            SB ‖ BND ──▶ seal file (C9)
                                                                 │
                                                                 ▼
                                                           seal_digest (C12)
                                                                 │
                                                                 ▼
                                                  registered row (C13)
```

**The provenance edge, new in revision 12.** Upstream of `deployed manifest` sits
one more input path, and it is the one P5.0-SR1 says was missing:

```
approved commit (immutable Git object, 0700 root store) ──▶ TM (C0) ──┐
approval record APR (root:root 0444, out of band) ────────────────────┤
                                                                       ├─▶ [I-2 gate: APR == PVR == TM == SM, C0] ──▶ SB
provenance record PVR (written at D8, outside the deployed root) ─────┤
deployed bytes ──▶ SM (C0) ───────────────────────────────────────────┘
```

**No arrow in that fragment runs from the deployed bytes to the trusted side.**
That is the property revision 11 lacked: its only trusted value came from the
bytes it was checking. The gate refuses on **any** disagreement and on **any**
absence, so omission of the provenance step is a refusal rather than a default —
`JNL-51` case (g).

Every arrow points forward in time and no value appears upstream of itself. **Two
gates sit on the graph, and revision 9 adds the first of them.** The **I-2 gate
at C0** is on the only path from the operator's supplied value into the
algorithm, and what it compares against is the **deployed manifest**, a source
outside the supplied value — so nothing downstream can be constructed from an
unvalidated external input. *Revision 8 had no gate here at all: the supplied
string reached C1 unchecked and was compared at C2 against the copy C1 had made
of it.* The **I-3 gate at C2** is on the only path out of `PR`, so no downstream
value can be constructed from an unchecked probe result; it is retained from
revision 8. `deployment manifest → DD` is drawn as an input edge rather than a
loop: the second computation at C2 is an **observation compared with `DD`**, not
a value anything consumes.
**`seal_digest` is a leaf**: it is consumed by readers and by PostgreSQL and is
never an input to anything on disk. `genesis_record_digest` depends on the seal
**body** only. The journal's inode depends on the file, which depends on the
genesis record, which depends on the seal body — and the seal *file* depends on
all three, which is legal because it is written last.

**How the first generation differs from a successor.**

| | First generation | Successor |
|---|---|---|
| `generation_seq` | `1` | predecessor's `+ 1` |
| `predecessor_generation_id`, `predecessor_seq`, `predecessor_close_digest` | **typed nulls in `SB`** — encoded as absent, so the canonical bytes differ structurally from any successor's | all three present; the close digest comes from the predecessor's `.close` manifest, which exists only after `seal` |
| Step **C0** | requires only that `…/journal` contains no journal file at all | additionally requires the predecessor **sealed, archived, `+i`**, and its `.close` manifest re-verified in this invocation. **Both are pre-probe facts**, which is why they stayed in C0 when the probe-result requirements moved to C2. **The deployment-digest computation and comparison revision 9 adds to C0 is identical for both**, and is likewise a pre-probe fact |
| Registration | `predecessor_generation_id IS NULL`, admitted by the partial unique index that permits exactly **one** such row per fenced writer | composite FK to the predecessor's `(id, generation_seq)`, and the unique predecessor index that permits **one** successor per generation |
| What it proves | that the chain has a root | that no history was skipped, and that erasing history required sealing it first |

**The `.close` manifest, for completeness**, since `predecessor_close_digest`
names it. Written by `seal`: canonical(format version, `generation_id`,
`final_seq`, `final_record_hash`, `record_count`, the **unresolved set at seal
time** as request ids with target-range and payload digests, `sealed_at`,
`seal_body_digest`, `seal_digest`). It may name the predecessor's `seal_digest`
because that seal already exists — no cycle. `close_digest` = SHA-256 over the
manifest's exact bytes.

#### 2.13.5b The verification algorithms — who checks what, and where each refusal lands. **New in revision 6; the binding contract corrected in revision 7 by remediation R6-B**

Three verifiers, deliberately unequal, because they have unequal access. The
split is the second half of remediation R5-B: **the writer validates everything
that can be established from disk, and only the coordinator validates against
PostgreSQL.**

**Algorithm V-W — the writer, at every start and before every dispatch.
Unprivileged, and read-only apart from one appended record.**

| Step | Check | Refusal |
|---|---|---|
| **W1** | `readlink("…/journal/current")`; refuse unless it is a relative name matching `^[0-9]{6}\.journal$` in the same directory | `SW-J03` |
| **W2** | `open("…/journal/__GEN__.seal", O_RDONLY\|O_NOFOLLOW)`; read fully | `SW-J17` |
| **W3** | Parse `SB`; refuse on an unknown `format_version`. **Then parse `BND` at exactly the `binding_format_version` `SB` declares**, refusing an unsupported version, a short binding, or **any byte after it** — the file's length must be exactly `len(SB) + len(BND)`. Recompute `seal_body_digest` over `SB` | `SW-J24` |
| **W4** | Recompute `probe_report_digest` over the embedded `PR` and compare with `SB.probe_report_digest`; refuse if `SB.append_only_probe_version` is not one this writer build supports, if `PR` does not carry **all four stages** and every one of their cases, if any case in `PR` is not a pass, or if `PR.writer_deployment_digest` ≠ `SB.writer_deployment_digest`; **and — amended 2026-09-23 under C-P5.0-R5-R1, pending review — if the systemd identity S4-3 recorded in `PR` differs from the host's current systemd identity** (§2.13.2a S4-3 condition 4) | `SW-J25` |
| **W5** | **Derive** the genesis record from `SB` alone (Algorithm C step **C4**) and compare its `record_hash` with `BND.genesis_record_digest`. **This is the acyclicity check made observable**: the writer computes the digest, it does not accept it | `SW-J24` |
| **W6** | `FS_IOC_GETFLAGS` on the seal fd: `FS_IMMUTABLE_FL` present | `SW-J17` |
| **W7** | `open("…/journal/__GEN__.journal", O_RDONLY\|O_NOFOLLOW)`; `fstat`; compare `(st_dev, st_ino)` with `BND` | `SW-J11` |
| **W8** | Compare `st_uid`, `st_gid` and the permission bits with `SB.journal_uid/gid/mode` | `SW-J05` |
| **W9** | `FS_IOC_GETFLAGS` on the journal fd: `FS_APPEND_FL` present. **`ENOTTY`/`EOPNOTSUPP` is a refusal, not an absence of information** | `SW-J06` |
| **W10** | Compare `SB.host_machine_id` with `/etc/machine-id`. **This detects an *unforged* host change and nothing more**: an actor holding **A6** can write `/etc/machine-id` on the host where the tree is read, and this comparison then passes — **F-7**, residual **R-5.0-13** | `SW-J23` |
| **W11** | Compare `SB.writer_deployment_digest` with **`deployment_manifest_digest()`** (§2.13.2c) computed by this process over its own deployed manifest — **the same named function root runs at C0 and C2**, asserted identical across the three call sites by `JNL-46` | `SW-J22` |
| **W11a** | **New in revision 12; this is remediation R11-A.** Compute `deployed_source_manifest_digest()` (§2.13.2c, §2.12.5a) over this process's own deployed region-S bytes and compare with `SB.source_manifest_digest`; then read `/etc/freedom-blades/sheet-writer.provenance` and refuse unless it is `root:root 0444`, well-formed, and equal to `SB` on `source_commit`, `source_tree_id` and `source_manifest_digest`. **The writer cannot re-derive the trusted manifest** — the object store is `0700 root:root` and it has no read — so this step establishes *these bytes are the sealed reviewed bytes* and **not** *the sealed manifest came from the approved commit*, which is root's check at **C0** and the coordinator's at **V-R**. §2.12.5a's verifier table states the inequality rather than leaving it implied | `SW-J26`, `SW-J27` |
| **W12** | `statvfs`: `ST_RDONLY` clear, and free bytes ≥ **N5.0-21** | `SW-J13` |
| **W13** | Read record 0 and compare it **byte for byte** with the derived genesis record | `SW-J04` |
| **W14** | Walk the chain to EOF: `format_version` known; `generation_id` equal to `SB`'s; `seq` exactly `+1` each time; `prev_hash` equal to the predecessor's `record_hash`; `record_hash` verifying; `at` non-decreasing | `SW-J07`, `SW-J08`, `SW-J09`, `SW-J10`, `SW-J18`, `SW-J21` |
| **W15** | A short or unverifiable tail record is a **torn tail**: the generation is `suspect`, and only `freedom-journal-admin repair` may clear it | `SW-J02` |
| **W16** | The last record's `kind` is not `seal` | `SW-J19` |
| **W17** | `open(O_WRONLY\|O_APPEND\|O_NOFOLLOW)` and append one **`startup`** record naming this writer's deployment digest and the sequence it resumed at; `fsync` | `SW-J14`, `SW-J15` |
| **W18** | Re-read the appended record at its expected sequence and verify its hash | `SW-J09` |

**The binding section, field by field — the enumeration R6-B requires.**
Revision 6 claimed at **F-1** that changing *any* byte of the seal is refused by
the writer without PostgreSQL. **It was not true**: `BND.sealed_at` was
authenticated by no step, so a seal whose only change was that field passed W1 …
W18 unchanged. Revision 7 fixes the design rather than the sentence — the
unauthenticated field is removed — and then states the enumeration so the claim
can be checked instead of believed.

| Field | Where it is fixed | What **V-W** does with it | Step | Semantic or cryptographic |
|---|---|---|---|---|
| `binding_format_version` | in **`SB`**, not in `BND` | the writer parses `BND` only at the version the body declares, and refuses a short binding or a trailing byte. **`SB` is itself authenticated by W13**, so the version cannot be moved without breaking record 0 | **W3**, transitively **W13** | cryptographic, transitively |
| `genesis_record_digest` | `BND`, at **C8** | **recomputed** from `SB` alone by Algorithm C step **C4** and compared; the same derivation is then compared **byte for byte** with record 0 | **W5**, then **W13** | cryptographic |
| `journal_device` | `BND`, at **C8** | compared with `fstat(st_dev)` of the journal the writer actually opened | **W7** | semantic, against the filesystem |
| `journal_inode` | `BND`, at **C8** | compared with `fstat(st_ino)` | **W7** | semantic, against the filesystem |
| ~~`sealed_at`~~ | ~~`BND`~~ | **withdrawn in revision 7.** Nothing recomputed it, nothing compared it, and no refusal read it | — | — |
| ~~a `format version` field inside `BND`~~ | ~~`BND`~~ | **withdrawn in revision 7.** A version the attacker supplies is a version the attacker chooses; it now lives in the chain-authenticated body | — | — |

**And the seal body, in one row, because it does not need one row per field.**
`seal_body_digest` covers **every** byte of `SB`, `prev_hash` of the genesis
record **is** `seal_body_digest`, and **W13** compares record 0 byte for byte
with the record the writer derives. So altering any byte of `SB` changes the
derived record 0 and the comparison fails — against the record actually on disk,
in a file carrying `FS_APPEND_FL`, which the writer's own identity cannot rewrite
(§2.13.4). **There is now no field in the writer-trusted seal that V-W does not
either recompute or compare against an independent source**, and §2.13.5c states
the attacker capability that claim holds against.

**W17 is the only write in the whole startup path, and it is a journal record
rather than a probe.** It demonstrates that appending works without performing
any operation that could damage the file if `+a` were absent, which is precisely
what revision 5's destructive re-probe got wrong. Nothing in V-W opens the
journal for writing without `O_APPEND`, truncates it, unlinks it, renames it or
touches its attributes; `JNL-32a` and `JNL-32b` assert that by syscall trace, in
the successful-start and absent-flag branches respectively.

**Algorithm V-C — the coordinator, at `observe`. Everything V-W checks except
W17/W18, plus the database.**

| Step | Check | Refusal |
|---|---|---|
| **C-a** | W1 … W16 **including W11a**, read-only. The coordinator appends nothing, ever. *W11a is named explicitly because it is new in revision 12 and because "W1 … W16" would otherwise be read as excluding it* | the matching `J-xx` row; **no evidence is recorded** |
| **C-b** | Recompute `seal_digest` over the seal file's exact bytes | `J-17` |
| **C-c** | Read the registered generation for `fenced_writer = 'sheet_writer'` that **nothing names as predecessor**; refuse if there is none | `J-16` |
| **C-d** | Compare that row's `generation_id`, `generation_seq`, `seal_body_digest`, `seal_digest`, `genesis_record_digest`, `journal_device`, `journal_inode`, `host_machine_id`, `writer_unit`, `writer_deployment_digest`, `filesystem_type`, `append_only_probe_version`, `append_only_probe_digest` and — **new in revision 12** — `source_commit`, `source_tree_id` and `source_manifest_digest` with the values just computed from disk. **Any single mismatch refuses.** *Sixteen compared values, up from thirteen* | `J-16` |
| **C-e** | Enumerate the unresolved set: every `dispatch` with no matching `outcome`, plus one synthetic unknown entry if W15 found a torn tail. Refuse if it is non-empty (**N5.0-20 = zero**), printing each entry with its target ranges and payload digest for human adjudication | `J-20` |
| **C-f** | Record the evidence row with `journal_generation_id`, `journal_last_sequence` and `journal_head_digest` | — |

**Algorithm V-R — `RegisterJournalGeneration`.** V-C steps C-a and C-b against
the *new* generation; then, for a successor, re-read the predecessor's archived
`.close` manifest, verify its digest equals the supplied
`predecessor_close_digest`, and re-validate the archived chain against it
(`archive-verify`); **then — new in revision 12 — resolve the approved source
revision: `SELECT` the `approved_source_revisions` row whose
`(component, source_commit, source_tree_id, source_manifest_digest)` equals the
four values the seal body carries, and refuse with `J-28` if there is none**;
then insert the row — carrying that row's id in a **`NOT NULL`** foreign key —
its `idempotency_keys` receipt and its `audit_events` row **in one transaction**.
Every constraint in logical schema §3.7 is a second, independent refusal.

**Why the foreign key is the fail-closed half, and not the `SELECT`.** A check
performed by the coordinator's code is a step somebody could remove; a
`NOT NULL` foreign key is refused by PostgreSQL for every principal, including
the schema owner, and it is checked on the same statement that would create the
row. **A generation with no approved source revision cannot exist**, and
§2.13.5b's **C-c** requires a registered generation before any
`dispatch_journal_clear` evidence is recorded, which the activation trigger in
turn requires. So the chain from *"the provenance step was omitted"* to
*"activation cannot succeed"* is closed by a schema constraint rather than by a
procedure — which is what P5.0-SR1 asks for, and it is a database refusing a
**database** fact, so §2.13.8a's enforce-versus-record division permits the claim.
**`JNL-51` case (g) is the executed proof**, and it asserts both halves:
`init-generation` refuses at **C0** with no artifact created, and a manually
assembled provenance record naming an unapproved commit is refused at
registration.

**What each verifier can and cannot establish.** Stated because the handoff asks
for the actor of every digest, and because unequal verifiers are only safe if the
inequality is written down.

| | Writer (V-W) | Coordinator (V-C / V-R) |
|---|---|---|
| Seal integrity, genesis derivation, inode, ownership, mode, `+a`, `+i`, chain — **against an attacker holding §2.13.5c `A1 + A11 + A3` but not `A10 + A2`** *(revision 9 wrote this pair as `A1 + A3` / `A2`; the owner-authorization rows are added in revision 10)* | **yes** | yes |
| Seal integrity **against `A1 + A2 + A3 + A10 + A11`** — an actor able to write the seal *and* to clear `FS_APPEND_FL` and rewrite record 0 consistently. **Revision 10 adds A10 and A11**, because clearing either flag needs the owner authorization as well as the capability; on this host the smallest identity holding the whole set is §2.13.5c's **E6** or **E7** | **no, and revision 7 states this rather than implying otherwise.** Every artifact and attribute the writer reads is below that privilege | **yes** — the registered digests are the one copy that actor did not write (**F-1b**) |
| Deployment digest and probe report | **yes** | yes |
| **Reviewed-source provenance — that the deployed bytes are the sealed reviewed bytes** *(new in revision 12)* | **yes** (**W11a**) | yes (**C-d**) |
| **Reviewed-source provenance — that the sealed source manifest was produced from the approved commit's Git objects** | **no.** The object store is `0700 root:root` and the writer has no read of it | **no.** The coordinator does not read the store either — this row is established by **root** at **D3** and **C0**, and by no other actor |
| **Reviewed-source provenance — that the revision was approved** | **no** | **yes**, against `approved_source_revisions`, which is the one copy an actor holding only host authority did not write (**F-13**) |
| Host identity — an **unforged** `/etc/machine-id` change | **yes** (W10) | yes (C-d, against the registered `host_machine_id`) |
| Host identity — `/etc/machine-id` **rewritten to the recorded value** on the host where the tree is read | **no** | **no.** The registered row holds the **same** value the seal does, so C-d compares two copies of the forged-to-match fact and finds no disagreement. *Revision 8 recorded a C-d refusal here; that is withdrawn* (**F-7**, **R-5.0-13**) |
| That this generation is the **registered head** | **no — it has no database access, by design** | yes |
| That no later generation was registered after an observation | **no** | yes |
| The unresolved set as *fence evidence* | computes it for its own refusal only; **authors no evidence** | yes, and it is the only thing that records it |
| Predecessor `.close` manifest and archive | **no — it cannot read `…/archive`** | yes |

#### 2.13.5c The capability matrix — the authorities needed to construct each alteration, and what refuses it. **New in revision 6; corrected in revision 7; replaced by a capability register in revision 8; that register corrected in revision 9; the register itself redesigned in revision 10, which is remediation R9-A and R9-B; the launch mechanism rebuilt in revision 11 (R10); `A5` widened, `E8` corrected and `F-13` added in revision 12 (R11)**

**The correction, conceded before the replacement.** Revision 9 withdrew the
eight-capability register and replaced it with nine authorities whose first row,
**A1**, was *"flag control — `FS_IOC_SETFLAGS` setting or clearing `FS_APPEND_FL`
/ `FS_IMMUTABLE_FL` on an inode the holder can already reach and open under
DAC"*, with the minimum holder given as **`CAP_LINUX_IMMUTABLE`**. **That is not
what Linux requires.** `FS_IOC_SETFLAGS` requires that the caller's **effective
UID match the inode's owner, or that the caller hold `CAP_FOWNER`**; changing
`FS_IMMUTABLE_FL` or `FS_APPEND_FL` requires **`CAP_LINUX_IMMUTABLE` in
addition**. The two are independent kernel checks and revision 9 hid one of them
inside a single label. `CAP_DAC_OVERRIDE` does not substitute for the
owner-or-`CAP_FOWNER` check: it is a discretionary-access override and the owner
check is not a discretionary-access check.

Primary contract:
<https://man7.org/linux/man-pages/man2/fs_ioc_setflags.2const.html>

**What that made false, stated as consequences rather than as one sentence.**

- A **non-root process holding only `CAP_LINUX_IMMUTABLE`** cannot clear `+i` on
  the **root-owned** archive at all. Revision 9's `JNL-50` case 9 asserted that it
  *"clears `+i` successfully"* and then receives `EACCES`. **It does not reach the
  `EACCES`**: the `FS_IOC_SETFLAGS` returns **`EPERM`** first, and the case as
  written is not executable.
- Every combination revision 9 wrote as **`A1 + A3`** or **`A1 + A4`** against a
  **root-owned** seal, archive file or `.close` manifest was **incomplete**. DAC
  obtained through `CAP_DAC_OVERRIDE` does not carry the owner authorization the
  flag change needs.
- **`A1 + A2`** for **F-2** happened to be constructible — because `freedomsheet`
  *owns* its journal file and so satisfies the owner half by ownership — but the
  label did not say so, and a label that is right by accident is not a model.
- Revision 9 asserted that **A1 … A6 confer nothing on one another** and then, in
  **F-1a**, that *"every real holder of A3 also holds A2"*. Both cannot be true of
  one register. **This is R9-B**, and it is corrected below by separating what an
  authority **is** from who can **hold** it.

Revision 10 does not repair this with a note. **The register is redesigned**: the
two kernel requirements become **separate rows**, the ownership requirement is
split by *which inode's owner it is* — because `freedomsheet` satisfies it on the
journal and nobody but root or a `CAP_FOWNER` holder satisfies it on the seal and
the archive — and every falsification row states the **minimum constructible
combination** and, separately, the **smallest identity on this host that can
actually hold it**.

---

##### The kernel requirements, before the register that encodes them

Every operation this section reasons about decomposes into these checks, and the
register has one row per check rather than one row per achieved ability.

| Operation | Checks the kernel makes, all of which must pass |
|---|---|
| **traverse to an inode** | `x` on every directory on the path, **or** `CAP_DAC_READ_SEARCH` |
| **open it** (`O_RDONLY` is enough for the ioctl) | `r` under DAC, **or** `CAP_DAC_OVERRIDE` |
| **`FS_IOC_SETFLAGS` at all** | effective UID **equal to the inode's owner**, **or** `CAP_FOWNER` |
| **`FS_IOC_SETFLAGS` changing `FS_IMMUTABLE_FL` or `FS_APPEND_FL`** | **`CAP_LINUX_IMMUTABLE`**, *in addition to the row above* |
| **write the inode's content** | `w` under DAC, **or** `CAP_DAC_OVERRIDE` — **and** the flag must already be clear, because `inode_permission()` refuses `MAY_WRITE` on an immutable inode with **`EPERM`** *before* it evaluates DAC |
| **create, unlink, rename or link in a directory** | `w` **and** `x` on the directory, **or** `CAP_DAC_OVERRIDE`; **and**, for an append-only or immutable victim, the flag must already be clear — `may_delete()` refuses first |

Two orderings in that table are load-bearing and are asserted rather than
assumed. **Immutability is checked before DAC on a write open**, so a
`0440 root:… +i` file returns `EPERM` to a non-owner and returns `EACCES` only
*after* the flag is gone — which is why a test that observes `EACCES` has already
proved the flag was cleared, and a test that observes `EPERM` has proved nothing
about DAC. And **the owner check is evaluated before `CAP_LINUX_IMMUTABLE` is
consulted**, so a caller without owner authorization gets `EPERM` whether or not
it holds the flag capability, which is why every negative flag case below is run
with **all other prerequisites satisfied**.

---

##### The authority register — eleven independently constructible primitives

Each row is independently held or not held, and **no row confers another as a
matter of definition**. **A7** is the exception and is labelled as one: it is a
composite, and it is in the register because it is how the others are acquired in
practice. **A9** is held by nobody in this design. *Which identities actually hold
which rows is a separate question, answered in the holder table below — that
separation is remediation **R9-B**.*

| # | Authority | What it is, concretely | Minimum holder on this host | Confers | Does **not** confer |
|---|---|---|---|---|---|
| **A1** | **Inode-flag special-bit authority** | the `CAP_LINUX_IMMUTABLE` half of an `FS_IOC_SETFLAGS` that changes `FS_IMMUTABLE_FL` or `FS_APPEND_FL` | **`CAP_LINUX_IMMUTABLE`.** Held by root; grantable to a non-root process as an ambient or file capability. **Unreachable from the writer**: `CapabilityBoundingSet=` is empty and `NoNewPrivileges=true` | **nothing on its own.** It is one of *two* prerequisites for a flag change and neither of the others | **the owner authorization the same ioctl requires** — that is **A10**/**A11** — and **any discretionary access at all**. *This row is the whole of remediation R9-A: revision 9 had the second clause and not the first* |
| **A10** | **`FS_IOC_SETFLAGS` owner authorization over the *`freedomsheet`-owned* inode** — the live journal file | effective UID equal to `freedomsheet`'s, **or** `CAP_FOWNER` | **`freedomsheet` itself, by ownership**; also uid 0 and any `CAP_FOWNER` holder | the owner half of a flag change **on the journal file only** | the flag half (**A1**), any DAC, and nothing about the seal or the archive |
| **A11** | **`FS_IOC_SETFLAGS` owner authorization over the *root-owned* inodes** — the seal, and every `…/archive/__GEN__.{journal,seal,close}` | effective UID **0**, **or** `CAP_FOWNER` | **uid 0, or a `CAP_FOWNER` holder. No service identity on this host holds it**, and `CAP_DAC_OVERRIDE` is **not** a substitute | the owner half of a flag change on the seal and the archive | the flag half (**A1**), and any DAC. Clearing a flag opens nothing and writes nothing |
| **A2** | **DAC on the live journal *file*** | `w` on `…/journal/__GEN__.journal`, mode `0640`, owner `freedomsheet`, group `freedomcoord` | **`freedomsheet` itself**, by ownership; also uid 0, or `CAP_DAC_OVERRIDE`. Traversal of `…/journal` comes with membership of `freedomjournal`, which the writer has | the ability to write the journal's bytes **once `+a` is gone** | the ability to write them while `+a` is set — that needs **A1 + A10** — and nothing about the directory, the seal or the archive |
| **A3** | **DAC on `…/journal` the directory, and on the seal within it** | create, unlink, rename or link inside `…/journal` (`0750 root:freedomjournal`, group `r-x`, **no `w` for anyone but root**); and `w` on `…/journal/__GEN__.seal` (`0440 root:freedomjournal` — **not writable by its own group, and not by its owner without a mode change**) | **uid 0, or `CAP_DAC_OVERRIDE`** (with `CAP_DAC_READ_SEARCH` where traversal is also lacking). **No group or other identity holds it** | replacing the journal inode **once `+a` is gone**, and writing the seal **once `+i` is gone** | either flag change — those are **A1 + A10** and **A1 + A11** — the archive (**A4**), or anything in PostgreSQL |
| **A4** | **DAC on `…/archive` and its files** | traverse `…/archive` (`0750 root:freedomcoord`), read and write its `0440 root:freedomcoord` files | traversal and read: membership of `freedomcoord`, uid 0, or `CAP_DAC_READ_SEARCH`. **Write: uid 0 or `CAP_DAC_OVERRIDE` only** — `freedomcoord` membership gives read and traverse and **never** write | altering an archived journal, seal or `.close` manifest **once `+i` is gone** | clearing `+i` — that is **A1 + A11** — and the **registered** `predecessor_close_digest`, which is A9's half of the database |
| **A5** | **DAC on the deployment path — widened in revision 12** | change the deployed writer's files, its unit file or its drop-ins (§2.13.2c's manifest); **and, new in revision 12, write `/opt/freedom-blades/coordinator/source.git`, `/etc/freedom-blades/approved-source-revision` or `/etc/freedom-blades/sheet-writer.provenance`** — the three root-owned artifacts §2.12.5a's provenance rests on | uid 0, or `CAP_DAC_OVERRIDE` on root-owned paths. **H-1 is the qualification, and revision 12 narrows it**: the *repository worktree* is group-writable by `discordbot` and `freedomweb`, so those identities can corrupt what a **future** deploy would copy — except that **no step of Algorithm D reads the worktree** (`JNL-51` case (h)), so what they can corrupt is no longer an input to a deployment. **Neither identity can write the object store, the approval record or the provenance record**: all three are `root:root`, and the store is `0700`. §7.1 row 17 | changing the digest the writer computes about itself at **W11**, and — with the three artifacts — making C0's four-way provenance comparison agree on a tree the holder chose (**F-13**) | the digest recorded in the seal (that is **A1 + A11 + A3**), and **the registered `approved_source_revisions` row**, which needs **A8** to insert and **A9** to alter. *A holder of A5 alone deploys unreviewed bytes and then cannot register the generation they require* |
| **A6** | **Host identity and restoration control** | write `/etc/machine-id`, **or** restore the journal tree onto a host the attacker controls and set `/etc/machine-id` there | **root on whichever host the tree is read on.** `/etc/machine-id` is an ordinary root-owned file | defeating **W10** — and **also C-d**, because the registered row holds the same value | anything in the production PostgreSQL, which is not on the restored tree |
| **A7** | **Full host-root identity** | uid 0 with a full capability set on this host | root, and anything that can become root | **A1, A2, A3, A4, A5, A6, A10 and A11**, and `setuid` to `freedomcoord`, hence **A8**. It is listed as its own row because it is how the others are acquired in practice | **A9.** Root on this host is not a PostgreSQL superuser; the database's own principals are a separate authority |
| **A8** | **Coordinator execution and authentication** | run `migration-authority` as `freedomcoord`, peer-authenticate, and `INSERT` into the generation and evidence tables | the `foundry` account through the `sudoers` rule (§2.12.4); and **A7**, which can `setuid` | inserting a generation row and evidence rows | `UPDATE`, `DELETE` or `TRUNCATE` on any append-only table |
| **A9** | **PostgreSQL mutation authority** | **mutate** an existing append-only row, or alter its datafile | a PostgreSQL **superuser**, or the `postgres` operating-system user's direct datafile access. **Nobody in this design holds it**: `UPDATE`/`DELETE`/`TRUNCATE` are revoked from every principal **including the schema owner** and refused by `reject_history_mutation` | changing a registered digest | any host artifact |

**Why A10 and A11 are two rows and not one.** They are the *same* kernel check
over *different* inodes, and on this host they have **completely different holder
sets**: `freedomsheet` holds A10 for nothing more than owning its own journal
file, and holds A11 not at all. Collapsing them would put the writer's own
ordinary ownership and a root-only authority in one cell, which is the shape of
the defect this section is correcting. **F-2's whole detector separation depends
on the distinction**, and it is the one place in the design where it does real
work.

---

##### Who actually holds what — the holder table, which is remediation R9-B

The register above says what each authority **is**. This table says who can
**hold** it on this host. **The authorities remain independent primitives — none
implies another by definition — and the realistic holders bundle them.** Both
statements are true at once, and revision 9's contradiction came from asserting
only the first while reasoning from the second.

| Identity or capability set | Holds | Notes |
|---|---|---|
| **`freedomsheet` inside its deployed unit** | **A2, A10** | by ownership of the journal file, and nothing else. `CapabilityBoundingSet=` is empty and `NoNewPrivileges=true`, so **A1 is unreachable**, which is why the flag is the whole of what refuses a rewrite |
| **`freedomsheet`'s uid outside any unit, granted an ambient `CAP_LINUX_IMMUTABLE`** | **A1, A2, A10** | the **exact** authority set that constructs **F-2** and nothing else. It reaches no seal and no archive, because it holds neither **A11** nor **A3**/**A4** |
| **`freedomcoord`** | **A8**, and A4's *read and traverse* only | no write bit anywhere under `…/journal`; no flag authority of either kind |
| **`discordbot`, `freedomweb`, `foundry`** | — | `…/journal` is `0750` and they are *other*; `…/archive` likewise |
| **a non-root uid holding `CAP_LINUX_IMMUTABLE` alone** | **A1** | **and can therefore change no flag on any inode in this hierarchy**, because it owns none of them and holds no `CAP_FOWNER`. *This is the identity revision 9 credited with clearing `+i` on the archive* |
| **a non-root uid holding `CAP_LINUX_IMMUTABLE` + `CAP_FOWNER`** | **A1, A10, A11** | can set and clear either flag on any inode it can **open** — and can open almost none of them, holding no DAC |
| **a non-root uid holding `CAP_LINUX_IMMUTABLE` + `CAP_DAC_OVERRIDE` + `CAP_DAC_READ_SEARCH`** | **A1, A2, A3, A4, A5, A6** | **the isolating case for R9-A**: every discretionary right and the flag capability, and **still no flag change**, because it holds neither **A10** nor **A11** |
| **a non-root uid holding `CAP_LINUX_IMMUTABLE` + `CAP_FOWNER` + `CAP_DAC_OVERRIDE` + `CAP_DAC_READ_SEARCH`** | **A1 … A6, A10, A11** | **the practical non-root composite.** Everything on disk; not **A8** without the `sudoers` rule, and not **A9** |
| **uid 0 (`A7`)** | **A1 … A8, A10, A11** | everything except **A9** |
| **a PostgreSQL superuser** | **A9** | and no host authority at all, unless it is also the `postgres` uid |

**The consequence for detector reach, stated because it is the half revision 9
got wrong.** Every falsification row below is assessed **twice**: once against the
**minimum combination** the alteration requires, and once against the **smallest
identity in this table that can hold that combination**. Where the two answers
differ, the row says so, and the honest reading is the second one — **F-1a is
separated from F-1b by what the attacker altered, not by what it could alter.**
Only three rows in the matrix have a *minimum combination whose smallest real
holder still does not reach the detector*, and those three are the ones this
design can claim as bounded rather than merely observed: **F-2**, **F-3** and
**F-6**.

---

##### The executable identities — corrected again, because a recipe that does not parse is not a specification either. **Rewritten in revision 11; this is remediation R10-A and R10-B**

**The correction, conceded before the replacement.** Revision 10 wrote the
identities **E2 … E6** as a root wrapper running
`setpriv --securebits=+keep_caps,+no_setuid_fixup …`. **That command does not
run.** `setpriv(1)` from util-linux **2.39.3** — the version installed on this
host and the version this package names — documents its accepted securebits as
*"noroot, noroot\_locked, no\_setuid\_fixup, no\_setuid\_fixup\_locked, and
keep\_caps\_locked"* and states in the same sentence that *"keep\_caps is cleared
by execve(2) and is therefore not allowed"*. The option is rejected at parsing
and `setpriv` exits **127** before any credential changes, so **five of the eight
identities did not exist**, and every `JNL-49`/`JNL-50` case naming them would
have stopped at its own mandatory `/proc/self/status` precondition as
**`inconclusive`**.

**Three further disagreements between a declared mask and the recipe meant to
produce it**, of which the re-review named two and the mechanical comparison
below found the third:

- **E2 … E6** requested `--bounding-set=+linux_immutable` (and its siblings).
  That is an **addition** to the bounding set. The same manual page states that
  *"notwithstanding the syntax offered by setpriv, the kernel does not permit
  capabilities to be added to the bounding set"*, and that the set for
  `--bounding-set` *"starts out as … the current bounding set"*. From root's full
  set the option changes nothing, and `CapBnd` would have been
  **`0x000001ffffffffff`** rather than the declared `0x200` … `0x20E`.
  **Revision 10 did not notice this because it never derived a declared mask from
  its recipe.**
- **E8** declared `CapBnd = 0x0` and its recipe dropped nothing.
- **E7** wrote **dashes** for inheritable and ambient, in a subsection whose own
  title claimed every identity carried complete masks.

**Revision 11 does not patch the option list. It changes the mechanism**, for a
reason that outlives the parse error and is stated before the replacement so it
can be disagreed with: substituting `+no_setuid_fixup` for `+keep_caps` would
have made those commands *parse*, and would still not have made their results
**derivable**. `setpriv(1)` does not document the order in which it applies
securebits, the UID/GID change, and the inheritable, ambient and bounding sets —
and **every declared mask depends on that order**. A securebit applied after the
UID transition does not prevent the permitted set being cleared; a bounding-set
drop attempted after the UID transition has no `CAP_SETPCAP` to do it with. The
manual's one relevant sentence, *"setting a uid or gid does not change
capabilities"*, is a claim about the tool that the kernel's documented behaviour
does not support on its own, and it names no ordering. **A recipe whose outcome
turns on an undocumented internal ordering is not a specification**, and this
package is not authorized to run the experiment that would settle it.

---

##### The launch mechanism, stated as a host fact and priced

**`capsh(1)`, from libcap.** Its manual page opens with the guarantee the
construction needs: *"capsh takes a number of optional arguments, **acting on
them in the order they are provided**."* Every intermediate credential state is
therefore derivable from the command line together with `capabilities(7)`, which
is the standard R10-A sets.

| Property | Value, and how it is known |
|---|---|
| Path | **`/usr/sbin/capsh`** |
| Package | **`libcap2-bin` 1:2.66-5ubuntu2.4**, `dpkg -S /usr/sbin/capsh` — **already installed**; the harness installs nothing |
| Ownership and mode | **`root:root`, `-rwxr-xr-x` (0755)**, `ls -l` |
| File capabilities | **none.** `getcap /usr/sbin/capsh` prints nothing. **It is not set-user-ID and carries no `security.capability` attribute** |
| Lifecycle | it is a **distribution binary that already exists**, not an artifact this package creates, deploys, modifies or removes. **Its lifecycle is the operating system's** |
| Cleanup | **none is required or performed.** No file is created, no attribute is set, and nothing is left behind by the launcher itself. The disposable `fbprobe` identity and the disposable hierarchy have their own lifecycle, unchanged from revision 10 |
| Authority to invoke it | **the harness's own**, which is root, under **A-5.0-5** and the Operations Owner's authorization. `capsh` is **not** granted authority; it *drops* the authority the harness already has. It is never invoked by `freedomsheet`, `freedomcoord`, `discordbot`, `freedomweb` or `foundry`, and no `sudoers` rule names it |
| Security-review consequence | **it is a harness dependency, not a production one.** `freedom-journal-admin`, `migration-authority`, `verify-capability` and the writer do not invoke `capsh`, and §2.13.3's hierarchy, §2.13.7's lifecycle and §2.12's coordinator boundary are unchanged. What the Security Reviewer gains is one question, added to §9.2: *is a root harness that constructs reduced identities with an unmodified system binary an acceptable evidence mechanism, given that it sets no file capability, creates no set-user-ID artifact and grants nothing that root did not already hold?* **The alternative mechanisms are named and declined below rather than left unstated** |

**The host design is not widened.** No file capability is set on any binary; no
set-user-ID or set-group-ID artifact is created; no helper executable is written,
deployed or left behind; no package is installed; no `sudoers` rule, unit,
drop-in, group or directory is added. The only new host object in the whole
capability harness is the **disposable `fbprobe` account**, which revision 10
already introduced and A-5.0-5 already carries.

**The mechanisms considered and declined, so the choice is a choice.**

| Mechanism | Why not |
|---|---|
| `setpriv(1)` with `+no_setuid_fixup` substituted | parses, but its **ordering is undocumented**, so the declared masks are not derivable from the tool's contract. It would need an empirical ordering determination as a prerequisite — which requires privilege and is **not authorized here** |
| a **file capability** on a purpose-built helper | sets `security.capability` on a real executable, creating a persistent host artifact with its own ownership, mode, deployment, integrity and revocation questions — and doing so **inside the state hierarchy this package is protecting**. It widens the host design for evidence, which stop condition 10c's spirit and §2.13.2's requirement (c) both argue against |
| a **set-user-ID helper** written for the harness | the same objection, worse: a new set-user-ID binary on a host whose set-user-ID inventory §8.1 records as **not audited** |
| a small C or Python program calling `prctl`/`capset` directly | the most precise option, and the one to fall back to if `capsh` is unavailable on the target host. It is **more** code to review than an unmodified system binary, and it is the harness's own artifact rather than the distribution's. Recorded here as the named fallback rather than adopted |

---

##### The prerequisite on the launching process's bounding set

**No tool can add a capability to a bounding set.** `setpriv(1)` says so
explicitly; `capsh(1)` offers **`--drop` and no addition at all**, which is the
strongest available form of the guarantee R10-A asks for — **there is no
invocation in revision 11 that asks for an addition, because the mechanism cannot
express one.**

Therefore **every capability any identity below needs must already be present in
the bounding set of the process that launches the harness.** Stated as a
precondition rather than assumed:

- the harness reads its **own** `CapBnd` from `/proc/self/status` **before**
  constructing anything, and asserts that it contains `CAP_LINUX_IMMUTABLE` (9),
  `CAP_FOWNER` (3), `CAP_DAC_OVERRIDE` (1), `CAP_DAC_READ_SEARCH` (2),
  `CAP_SETPCAP` (8), `CAP_SETUID` (7) and `CAP_SETGID` (6);
- if any is absent — a hardened unit, a container, a reduced login path — the run
  is **`inconclusive`** and **no case is reported as passed or refused**;
- **observed on this host on 2026-08-31** (§8.1 **H-6**, a non-mutating read):
  `/proc/1/status` and an ordinary shell both report
  `CapBnd: 000001ffffffffff`, which `capsh --decode` expands to all forty-one
  capabilities `0 … 40`, `CAP_LAST_CAP` being **40** (`cap_checkpoint_restore`)
  on kernel **6.8.0-138-generic**. **All seven required capabilities are
  present.** This is a reading of the host, not a confirmation of A-5.0-5, and
  the harness re-reads it on whatever host it actually runs on.

---

##### The construction — seven steps, in the order `capsh` documents, with the kernel rule each one relies on

One procedure builds **E1 … E6 and E8**. It is parameterised by the target uid
**U**, primary gid **G**, supplementary-group list **S**, and capability set
**M** — and by nothing else, so two identities that differ only in **M** differ
only in the authority under test. **E7 is the harness's own root identity and is
constructed by not dropping**, which is why it is stated separately below.

Let `ALLCAPS` be the forty-one capability names of this kernel, in index order,
as `capsh --decode=0x000001ffffffffff` prints them:

```text
cap_chown, cap_dac_override, cap_dac_read_search, cap_fowner, cap_fsetid,
cap_kill, cap_setgid, cap_setuid, cap_setpcap, cap_linux_immutable,
cap_net_bind_service, cap_net_broadcast, cap_net_admin, cap_net_raw,
cap_ipc_lock, cap_ipc_owner, cap_sys_module, cap_sys_rawio, cap_sys_chroot,
cap_sys_ptrace, cap_sys_pacct, cap_sys_admin, cap_sys_boot, cap_sys_nice,
cap_sys_resource, cap_sys_time, cap_sys_tty_config, cap_mknod, cap_lease,
cap_audit_write, cap_audit_control, cap_setfcap, cap_mac_override,
cap_mac_admin, cap_syslog, cap_wake_alarm, cap_block_suspend, cap_audit_read,
cap_perfmon, cap_bpf, cap_checkpoint_restore
```

`DROP(M)` is `ALLCAPS` with the members of **M** removed, order preserved. It is
a **total** substitution over an enumerated constant, so it is not shorthand: the
resulting bounding set is `M` whatever order the names appear in, because a
bounding-set operation can only ever remove.

```text
/usr/sbin/capsh \
  --secbits=4 \                      # step 1
  --drop=DROP(M) \                   # step 2
  --inh=M \                          # step 3   (omitted when M is empty)
  --gid=G --groups=S \               # step 4
  --uid=U \                          # step 5
  --addamb=<one per capability in M> \# step 6   (omitted when M is empty)
  --shell=<harness case binary> --    # step 7
```

| Step | What it does | The rule that makes the result derivable | State after it, starting from root |
|---|---|---|---|
| **1** | `--secbits=4` sets **`SECBIT_NO_SETUID_FIXUP`** and clears every other securebit. `4` is `1 << SECURE_NO_SETUID_FIXUP`, and `SECURE_NO_SETUID_FIXUP` is **2** in `/usr/include/linux/securebits.h` on this host | `capabilities(7)`: the bit *"stops the kernel from adjusting the process's permitted, effective, and ambient capability sets when the thread's effective and filesystem UIDs are switched between zero and nonzero values"*, and *"provides a superset of the effect of"* `SECBIT_KEEP_CAPS`. `PR_SET_SECUREBITS` requires **`CAP_SETPCAP`**, which root holds. **`SECBIT_KEEP_CAPS` is not set, is not needed, and is not used** | securebits `0x4`; P, E, I, A, B unchanged |
| **2** | `--drop=DROP(M)` removes every capability outside **M** from the **bounding set** | `capsh(1)`: *"remove the listed capabilities from the prevailing bounding set … requires that capsh is operating with `CAP_SETPCAP` in its effective set"*, which it still is. A bounding-set drop **does not touch permitted or effective** | **B = M**; P, E full |
| **3** | `--inh=M` sets the **inheritable** set to exactly **M** | `capabilities(7)`: the new inheritable set must be a subset of *"the existing inheritable set and the capability bounding set"* — B is now **M** — and, absent `CAP_SETPCAP`, of inheritable ∪ permitted. Both hold; `CAP_SETPCAP` is in effect in any case | **I = M** |
| **4** | `--gid=G` then `--groups=S`: `setgid(2)` and `setgroups(2)` | both require **`CAP_SETGID`**, which is still in the effective set. **They must precede step 5**, because a non-zero uid holds neither | primary gid **G**, supplementary list exactly **S** |
| **5** | `--uid=U`: `setuid(2)`, changing **all** uids to a non-zero value | `capabilities(7)` would clear permitted, effective **and ambient** on this transition — *"if one or more of the real, effective, or saved set user IDs was previously 0, and as a result of the UID changes all of these IDs have a nonzero value"* — **except that step 1 set `SECBIT_NO_SETUID_FIXUP`**, which is exactly the adjustment that bit stops. Requires **`CAP_SETUID`**, still effective | uid **U**; P and E still full; **I = M**; **B = M**; A empty |
| **6** | one `--addamb=` per capability in **M**: `PR_CAP_AMBIENT_RAISE` | `capabilities(7)`: a capability may be raised in the ambient set only if it is *"currently present in both the permitted and inheritable sets"* — permitted is full and **I = M** — and only while `SECBIT_NO_CAP_AMBIENT_RAISE` is clear, which step 1 guarantees. **No `CAP_SETPCAP` is required**, which matters because it is no longer in **M** | **A = M** |
| **7** | `--shell=<binary> --` execs the harness case binary, which is **`root:root 0755` with no file capabilities and not set-user-ID** — asserted by the harness with `getcap` and `stat` before the run | the `execve` transformation for a file carrying no capabilities: `P'(amb) = P(amb)`; `P'(perm) = (I ∧ F_I) ∨ (F_P ∧ B) ∨ P'(amb)` = **A**, since `F_I` and `F_P` are empty; `P'(eff) = P'(amb)`, since `F_E` is clear; `P'(inh) = I`; the bounding set is unchanged; and the securebits survive **except `SECBIT_KEEP_CAPS`**, which was never set | **`CapPrm = CapEff = CapInh = CapAmb = CapBnd = M`**, securebits `0x4` |

**Why the pre-`execve` permitted set does not appear in any declared mask.** Step
7 recomputes the permitted set from scratch. With no file capabilities,
`P'(perm)` reduces to the ambient set, so whatever the process held at step 6 is
irrelevant to what the harness asserts. **That is the whole reason the ambient set
is the carrier**, and it is why revision 10's `--ambient-caps` instinct was right
about the destination and wrong about the route.

**When `M` is empty** — **E1** and **E8** — steps 3 and 6 are omitted and step 2
drops all forty-one capabilities. Step 1 is still executed, so that **E1 and E2
differ in `M` and in nothing else**; with an empty permitted set the securebit
confers nothing, and this is stated rather than left to be noticed.

---

##### The identities — E1 … E8, complete, with securebits and exact supplementary groups

`CAP_DAC_OVERRIDE` is capability **1** (`0x2`), `CAP_DAC_READ_SEARCH` **2**
(`0x4`), `CAP_FOWNER` **3** (`0x8`), `CAP_LINUX_IMMUTABLE` **9** (`0x200`).
Every mask below was recomputed independently from those indices and cross-checked
with `capsh --decode`, which is check 4 of the required non-mutating set.

**`freedomsheet`, `freedomcoord`, `freedomjournal` and `fbprobe` do not exist on
this host** (`getent passwd`/`getent group`, 2026-08-31). Every uid and gid below
is therefore a **name**, and the harness resolves it with `getpwnam`/`getgrnam`
at run time, substitutes the numeric value into `--uid`, `--gid` and `--groups`,
and asserts the resolved numbers against `/proc/self/status`. `capsh`'s `--uid`,
`--gid` and `--groups` take **numeric** values; the resolution step is part of the
harness and is stated because it is the one place a name becomes a number.

| Id | Effective UID : GID | Supplementary groups, exactly | `CapPrm` | `CapEff` | `CapInh` | `CapAmb` | `CapBnd` | Securebits | Authorities |
|---|---|---|---|---|---|---|---|---|---|
| **E1** | `freedomsheet` : `freedomsheet` | `freedomsheet`, `freedomjournal` | `0x0` | `0x0` | `0x0` | `0x0` | `0x0` | `0x4` | **A2, A10** |
| **E2** | `freedomsheet` : `freedomsheet` | `freedomsheet`, `freedomjournal` | `0x200` | `0x200` | `0x200` | `0x200` | `0x200` | `0x4` | **A1, A2, A10** |
| **E3** | `fbprobe` : `fbprobe` | `fbprobe` only | `0x200` | `0x200` | `0x200` | `0x200` | `0x200` | `0x4` | **A1** only |
| **E4** | `fbprobe` : `fbprobe` | `fbprobe` only | `0x206` | `0x206` | `0x206` | `0x206` | `0x206` | `0x4` | **A1, A2, A3, A4, A5, A6** — **no A10, no A11** |
| **E5** | `fbprobe` : `fbprobe` | `fbprobe`, `freedomcoord` | `0x208` | `0x208` | `0x208` | `0x208` | `0x208` | `0x4` | **A1, A10, A11**, and A4's read/traverse half |
| **E6** | `fbprobe` : `fbprobe` | `fbprobe` only | `0x20E` | `0x20E` | `0x20E` | `0x20E` | `0x20E` | `0x4` | **A1 … A6, A10, A11** |
| **E7** | `0` : `0` | `0` (`root`) only | `0x000001ffffffffff` | `0x000001ffffffffff` | `0x0` | `0x0` | `0x000001ffffffffff` | `0x0` | **A7** — A1 … A8, A10, A11 |
| **E8** | `freedomcoord` : `freedomcoord` | **`freedomcoord`, `freedomjournal`** *(corrected in revision 12: revision 11 wrote `freedomcoord` only, which is not the identity §2.12.2 provisions)* | `0x0` | `0x0` | `0x0` | `0x0` | `0x0` | `0x4` | **A8**, A4 read/traverse, and `freedomjournal`'s read/traverse of `…/journal` |

**"No supplementary groups" is not a state `setgroups(2)` reaches usefully here,
so revision 11 stops claiming it.** Revision 10 wrote *"no supplementary
groups"* for E3, E4 and E6; the harness sets the supplementary list to **exactly
the identity's own primary gid**, which is what `--groups=<gid>` produces and what
`/proc/self/status` `Groups:` will show. It confers nothing beyond the primary
group, and **no group named in §2.13.3 appears in it** except where the table says
so — `freedomjournal` for E1, E2 and **E8**, `freedomcoord` for E5 and E8.

**Every group name above is taken from §2.12.2 and from nowhere else — new in
revision 12, and this is remediation R11-B.** Revision 11's `E8` was
`freedomcoord` with its own group only, which is **not** the identity
provisioning creates: §2.12.2 puts `freedomcoord` in `freedomjournal` as well, so
the evidence identity named after the coordinator was not the coordinator. It is
corrected above. **§2.12.2 also records which provisioned identity each of
`E1 … E8` corresponds to**, and says plainly that `E3`, `E4`, `E5` and `E6`
correspond to **none** — `fbprobe` with constructed capability sets, `E5`
additionally carrying a `freedomcoord` membership this design provisions for
nobody. That labelling is deliberate: a synthetic identity is a legitimate way to
isolate a kernel check, and a synthetic identity **mistaken for a real holder
set** is the defect P5.0-SR2 found one level up.

**What the E8 correction does and does not change, checked case by case.** E8
appears in `JNL-49` and `JNL-50` as the coordinator-side identity for **A8** and
for **A4**'s read and traverse. Adding `freedomjournal` grants it `r-x` on
`…/journal` and `r--` on the seal — **access §2.13.3 already says the reader
has** — and grants no write anywhere. **No case asserts that E8 is denied a read
of `…/journal` or of the seal**, so no expected result moves. `JNL-50` case 8,
the one case that turns on *absence* of `freedomjournal`, is executed under **E5**
(`fbprobe`, which is in neither group) and is untouched. The sweep is recorded in
the R11 handback rather than asserted here.

**E7's masks are environment-derived and are labelled as such.**
`0x000001ffffffffff` is every capability from `0` to `CAP_LAST_CAP`, and
`CAP_LAST_CAP` is **40** on kernel **6.8.0-138-generic** — read on 2026-08-31
from `/proc/1/status` and expanded with `capsh --decode` (§8.1 **H-6**). Root's
inheritable and ambient sets are `0x0`, which is the ordinary state of a root
process and is now stated rather than dashed. **On a kernel with a different
`CAP_LAST_CAP` this row is wrong**, so the harness **re-reads `/proc/1/status`
on the host it runs on**, recomputes the expected value, and reports
**`inconclusive`** if the document's copy and the host disagree — it does not
silently prefer either.

---

##### Every invocation, in full

Written out per identity, because R10-B requires a complete construction rather
than *"as E2/E3"* shorthand wherever option ordering or inherited state could
alter the result. `DROP(M)` is the total substitution defined above; `⟨g:name⟩`
is the numeric gid the harness resolves for `name`, and `⟨u:name⟩` the numeric
uid. **Nothing is inherited between rows**: each is a complete command line
executed by the root harness from its own credentials.

| Id | Complete invocation |
|---|---|
| **E1** | `/usr/sbin/capsh --secbits=4 --drop=DROP(∅) --gid=⟨g:freedomsheet⟩ --groups=⟨g:freedomsheet⟩,⟨g:freedomjournal⟩ --uid=⟨u:freedomsheet⟩ --shell=<case> --` |
| **E2** | `/usr/sbin/capsh --secbits=4 --drop=DROP({linux_immutable}) --inh=cap_linux_immutable --gid=⟨g:freedomsheet⟩ --groups=⟨g:freedomsheet⟩,⟨g:freedomjournal⟩ --uid=⟨u:freedomsheet⟩ --addamb=cap_linux_immutable --shell=<case> --` |
| **E3** | `/usr/sbin/capsh --secbits=4 --drop=DROP({linux_immutable}) --inh=cap_linux_immutable --gid=⟨g:fbprobe⟩ --groups=⟨g:fbprobe⟩ --uid=⟨u:fbprobe⟩ --addamb=cap_linux_immutable --shell=<case> --` |
| **E4** | `/usr/sbin/capsh --secbits=4 --drop=DROP({dac_override,dac_read_search,linux_immutable}) --inh=cap_dac_override,cap_dac_read_search,cap_linux_immutable --gid=⟨g:fbprobe⟩ --groups=⟨g:fbprobe⟩ --uid=⟨u:fbprobe⟩ --addamb=cap_dac_override --addamb=cap_dac_read_search --addamb=cap_linux_immutable --shell=<case> --` |
| **E5** | `/usr/sbin/capsh --secbits=4 --drop=DROP({fowner,linux_immutable}) --inh=cap_fowner,cap_linux_immutable --gid=⟨g:fbprobe⟩ --groups=⟨g:fbprobe⟩,⟨g:freedomcoord⟩ --uid=⟨u:fbprobe⟩ --addamb=cap_fowner --addamb=cap_linux_immutable --shell=<case> --` |
| **E6** | `/usr/sbin/capsh --secbits=4 --drop=DROP({dac_override,dac_read_search,fowner,linux_immutable}) --inh=cap_dac_override,cap_dac_read_search,cap_fowner,cap_linux_immutable --gid=⟨g:fbprobe⟩ --groups=⟨g:fbprobe⟩ --uid=⟨u:fbprobe⟩ --addamb=cap_dac_override --addamb=cap_dac_read_search --addamb=cap_fowner --addamb=cap_linux_immutable --shell=<case> --` |
| **E7** | **no invocation.** The harness's own process, root, no securebit set and no drop of any kind. Its masks are read and asserted, not constructed |
| **E8** | `/usr/sbin/capsh --secbits=4 --drop=DROP(∅) --gid=⟨g:freedomcoord⟩ --groups=⟨g:freedomcoord⟩,⟨g:freedomjournal⟩ --uid=⟨u:freedomcoord⟩ --shell=<case> --` *(the second group is the revision-12 correction)* |

**E4 and E6 differ in exactly one option pair** — `cap_fowner` in `--drop`'s
complement, in `--inh` and in one `--addamb` — and in nothing else: same uid, same
gid, same supplementary list, same securebits, same case binary. **E1 and E2
differ in exactly one capability.** That is the property the control pairs below
rest on, and it is now a property of the command lines rather than a claim about
them.

---

##### The mask-versus-recipe comparison, done mechanically

This is check 4 of the required non-mutating set: each declared mask compared
with the recipe intended to produce it, cell by cell. **Revision 10 is assessed
first, so the failures are visible before the replacement is scored.**

| Id | Declared `CapBnd` | Revision 10's recipe would produce | Agrees? |
|---|---|---|---|
| **E1** | `0x0` | `0x0` **if** `setpriv` drops the bounding set while `CAP_SETPCAP` is still effective — **not determinable from `setpriv(1)`** | **undetermined** |
| **E2 … E6** | `0x200`, `0x200`, `0x206`, `0x208`, `0x20E` | **`0x000001ffffffffff`** — `--bounding-set=+…` starts from the current set and cannot add; and in any case the command **exits 127** on `+keep_caps` | **no** |
| **E7** | *"full"* | not evaluable — no mask stated, and no `CAP_LAST_CAP` named | **not evaluable** |
| **E8** | `0x0` | **`0x000001ffffffffff`** — no `--bounding-set` requested | **no** |

| Id | Declared, revision 11 | Derived from the invocation | Agrees? |
|---|---|---|---|
| **E1** | P/E/I/A/B all `0x0`, secbits `0x4` | step 2 drops all 41 → B `0x0`; steps 3 and 6 omitted → I `0x0`, A `0x0`; step 7 → P = E = A = `0x0` | **yes** |
| **E2** | all `0x200`, secbits `0x4` | step 2 → B `0x200`; step 3 → I `0x200`; step 6 → A `0x200`; step 7 → P = E = A = `0x200` | **yes** |
| **E3** | all `0x200`, secbits `0x4` | identical to E2 but for uid, gid and group list | **yes** |
| **E4** | all `0x206`, secbits `0x4` | `0x2 ∣ 0x4 ∣ 0x200 = 0x206`; same derivation | **yes** |
| **E5** | all `0x208`, secbits `0x4` | `0x8 ∣ 0x200 = 0x208`; same derivation | **yes** |
| **E6** | all `0x20E`, secbits `0x4` | `0x2 ∣ 0x4 ∣ 0x8 ∣ 0x200 = 0x20E`; same derivation | **yes** |
| **E7** | P/E/B `0x000001ffffffffff`, I/A `0x0`, secbits `0x0` | **not derived — read.** `/proc/1/status` on this host, 2026-08-31; re-read and re-asserted on the target host | **yes, by measurement** |
| **E8** | P/E/I/A/B all `0x0`, secbits `0x4` | identical to E1 but for uid, gid and group list | **yes** |

**No invocation in revision 11 asks any tool to add a capability to a bounding
set.** `capsh` has no such option, and the prerequisite that every needed
capability is already present in the launching process's bounding set is stated
in its own subsection above and asserted at run time — which is check 3 of the
required non-mutating set, discharged by construction rather than by inspection.

---

##### The assertion contract, and what makes a case `inconclusive`

**Every case asserts its identity before it asserts its result.** Inside the
exec'd process, and **before** the operation under test:

| Asserted | Read from |
|---|---|
| `Uid:` — all four fields equal to the resolved uid | `/proc/self/status` |
| `Gid:` — all four fields equal to the resolved primary gid | `/proc/self/status` |
| `Groups:` — exactly the resolved supplementary list, as a set | `/proc/self/status` |
| `CapPrm`, `CapEff`, `CapInh`, `CapAmb`, `CapBnd` — each equal to the declared mask | `/proc/self/status` |
| securebits — equal to the declared value | **`prctl(PR_GET_SECUREBITS)`**, because `/proc/self/status` does not report them. *Revision 10 declared no securebits value and had nothing to assert* |
| `NoNewPrivs: 0`, and the case binary carrying **no** file capability and **no** set-user-ID bit | `/proc/self/status`; `getcap` and `stat` in the harness before launch |

**A case whose identity assertion fails is `inconclusive`** — never a pass, never
a refusal. The same rule §2.13.2a Stage 1 applies to the probe, applied here, and
it is the rule that would have caught revision 10's five non-existent identities
had the harness ever run.

**`fbprobe` is a disposable identity that exists only for this evidence**, is in
no group that appears in §2.13.3 except where the table says so, and is created
and removed by the harness against a disposable hierarchy. It is carried by
**A-5.0-5**, which remains **unconfirmed**.

---

##### The two control forms, because one of them was wrong

Every negative flag case runs with **all other prerequisites satisfied** and
carries a **positive control that succeeds and differs in exactly the authority
under test**. Revision 11 recognises **two ways** to hold everything else fixed,
and names which one each case uses — revision 10 used the first where only the
second was available, and in two places used neither.

| Form | What is varied | What is held fixed | Where it is used |
|---|---|---|---|
| **C-I — vary one capability** | one capability in **M**, and nothing else: same uid, gid, supplementary list, securebits, case binary, path, inode and mount | everything else | **E4 → E6** for `CAP_FOWNER` (the owner check, on either owner's inode); **E1 → E2** for `CAP_LINUX_IMMUTABLE` (the flag capability, on the writer's own inode) |
| **C-II — vary the inode's owner** | the target inode's owner, and nothing else: same identity, same syscall, same directory, same mode, same mount, two files created identically by the root harness | the whole process identity | **E2** against a root-owned `+i` file (`EPERM`) versus a `freedomsheet`-owned `+i` file (**succeeds**) — the control for `JNL-50` case 4, where **no identity one capability apart from E2 exists in the table** |

**The pair revision 10 got wrong, corrected rather than defended.** `JNL-50`
case 7 and the journal half of `JNL-49` case 11 gave **E2** as the positive
control for an **E4** refusal against the `freedomsheet`-owned journal file. E2
differs from E4 in **uid, supplementary groups and two capabilities**, so an E4
refusal beside an E2 success is consistent with several explanations and isolates
none of them. **The isolating control is E6**, which differs from E4 by
`CAP_FOWNER` alone — and `CAP_FOWNER` is precisely the second way to satisfy A10.
**E2 is retained as a corroborating control** demonstrating the *other* way to
satisfy the same check, ownership, and is labelled as differing in more than one
respect and therefore not the isolating control. The claim is not narrowed,
because C-I with E6 supports it in full.

**Nothing else in this subsection moved.** The eleven-authority register, the
holder table, the two-column reach assessment, the thirteen falsification rows
revision 10 left, the not-constructible table and the six bounded claims are
**preserved unchanged in substance** from revision 10. *(Revision 12 widens `A5`
and adds a fourteenth row, **F-13**; it moves none of the thirteen.)* **No corrected identity produced a conflict with
them**, and none with the R8-A, R8-B or R8-D/F-7 corrections either; had one
appeared, the R10 brief requires this document to stop and report it rather than
expand, and it would have.

---

##### Achieved ability versus the privileges that achieve it, corrected again

| An achieved ability | What revision 8 called it | What revision 9 called it | What it actually requires |
|---|---|---|---|
| “archive write” | `K4`, *"root with `CAP_LINUX_IMMUTABLE`"* | **A1 + A4** | **A1 + A11 + A4.** A1 is the flag capability; **A11** is the owner authorization the same ioctl needs over a **root-owned** inode; **A4** is the discretionary access. A holder of A1 + A4 without A11 receives **`EPERM`** from `FS_IOC_SETFLAGS` and never reaches the open |
| “journal-content rewrite” | `K3`, *"a holder of `CAP_LINUX_IMMUTABLE`"* | **A1 + A2** | **A1 + A10 + A2** — and revision 9's answer was constructible only because **`freedomsheet` holds A10 by owning the file**. The label is corrected so it is right for a reason rather than by accident |
| “replace the journal file” | `K2`, journal-directory write alone | **A1 + A3** | **A1 + A10 + A3.** An `+a` inode cannot be unlinked or renamed over (probe cases **P-4**, **P-5**), and clearing the flag needs the owner half over a **`freedomsheet`-owned** inode |
| “rewrite the seal” | — | **A1 + A3** | **A1 + A11 + A3.** The seal is root-owned, so the owner half is **A11**, which `CAP_DAC_OVERRIDE` does not supply |

**The identity boundary, stated because R7-C asked for it, R8-C sharpened it and
R9-A corrects it.** There are now **four** distinct kinds of authority here and
they are not a ladder. **`CAP_LINUX_IMMUTABLE` alone is A1 and nothing else** — it
is one half of one ioctl's permission check. **Owner authorization is A10/A11**,
and it is the other half; `CAP_DAC_OVERRIDE` is not it. **Discretionary access is
A2 … A5**, and a cleared flag confers none of it. **Full root is A7**, different
in kind, and a **PostgreSQL superuser is A9**. A real compromise may hold any
combination, and the matrix below says which combination each row needs and who
can actually hold it.

---

##### The falsification matrix — **fourteen rows in revision 12**, thirteen of them unchanged

For every row: the **minimum combination** that constructs the alteration; the
**smallest identity in the holder table** that can hold it; whether the *minimum
combination* reaches the expected detector's own prerequisites; whether that
*smallest real holder* does; the **independent actor or artifact** that refuses
it; the **exact step and code**; and the **residual**.

| # | Altered, independently | Minimum **combination** | Smallest real holder | Detector, and its prerequisites | Reach — by combination / by holder | Independent actor or artifact that refuses | Exact step and code | Residual when the attacker holds artifact **and** detector | Test |
|---|---|---|---|---|---|---|---|---|---|
| **F-1a** | any byte of the **seal body** `SB`, the seal alone being altered | **A1 + A11 + A3** *(revision 9 said A1 + A3)* | **E6**, or **E7** | record 0 inside the `+a` journal — **A1 + A10 + A2** | **No / yes.** The combination omits A10 and A2; **E6 and E7 hold both.** So the honest statement is R9-B's: F-1a is separated from F-1b by **what the attacker altered**, not by what it could alter. The writer's refusal is a real refusal of the observable partial alteration and **is not a bound on the attacker** | the **writer**, from disk, with no database | **W13** `SW-J04`; **W5** `SW-J24` where `BND.genesis_record_digest` was left alone; coordinator **C-b/C-d** `J-17`/`J-16` | adding A10 + A2 is **F-1b** | `JNL-34a` |
| **F-1b** | the **seal body and record 0 together**, rewritten consistently | **A1 + A2 + A3 + A10 + A11** *(revision 9 said A1 + A2 + A3)* | **E6**, or **E7** | — the disk agrees with itself | **n/a** — this is the case where nothing on disk disagrees | **the coordinator only**, against the registered row | **C-b/C-d** `J-16`, `J-17` | **that combination + A9**, which needs a PostgreSQL superuser. **Not refused by this design.** What remains is `sudo log_output`, journald, `audit_events` and offline backups — detection, not prevention: **R-5.0-12** | `JNL-34b` |
| **F-2** | the **genesis record** in the journal, the seal left alone | **A1 + A2 + A10** *(revision 9 said A1 + A2; the omission of A10 was invisible only because `freedomsheet` holds it by ownership)* | **E2** — `freedomsheet`'s own uid with an ambient `CAP_LINUX_IMMUTABLE`. It holds **A2 and A10 by owning the inode** and lacks **A1** and nothing else | `SB` in the `+i` seal — **A1 + A11 + A3** | **No / no.** **E2 holds neither A11 nor A3**, so it cannot clear `+i` on the root-owned seal (**`EPERM`**) and cannot write a `0440` root-owned file. **This is the one row where the corrected model makes the separation stronger rather than weaker**, and it is why A10 and A11 are two rows | the **writer**, from disk, with no database | **W13** `SW-J04` | E6/E7 hold everything and the row becomes **F-1b** | `JNL-35`, `JNL-49` case 10 |
| **F-3** | the **registered digests** in PostgreSQL | **A9** for mutation; **A8** for inserting a competing row — no principal in this design holds A9 | a PostgreSQL superuser; **not E7** | the files on disk — **A1 + A10 + A11 + A2 + A3** | **No / no.** Neither A8 nor A9 touches a host artifact, and a superuser is not root on this host | the `reject_history_mutation` trigger and the revoked grants; then coordinator **C-d** | trigger refusal, then `J-16` | A8 + the disk combination constructs a **new** self-consistent generation and inserts it, but the partial unique index and the predecessor foreign key admit only **one** unsuperseded head and **one** successor per generation, so the forged row is visible as a rotation with no `seal`, no `.close` manifest and no archive. **R-5.0-12** | `JNL-36`, `JNL-49` |
| **F-4** | the **predecessor `.close` manifest** | **A1 + A11 + A4** *(revision 9 said A1 + A4)* | **E6**, or **E7**. **E5** reaches the *clear* and stops at the write — that pair is `JNL-49` case 12 | the successor's `predecessor_close_digest`, in `SB` (**A1 + A11 + A3**) and in the registered row (**A9**) | **No / partly.** E6 and E7 hold A3, so the **disk** copy is within reach; **A9 is not**, and that is what the row rests on | coordinator **V-R**, and `archive-verify` at every restore | registration refused | adding A3 falsifies both disk copies; the **registered** `predecessor_close_digest` still disagrees, so this collapses to the F-3 residual | `JNL-37`, `JNL-49` case 8, `JNL-50` case 6 |
| **F-5** | the **inode** — the journal replaced by a new file | **A1 + A10 + A3** *(revision 9 said A1 + A3)* | **E6**, or **E7**. **E4 cannot do it**: it holds A1 and A3 and **not** A10, so the flag clear returns `EPERM` and the `+a` victim cannot be unlinked or renamed over | `BND.journal_inode` in the `+i` seal — **A1 + A11 + A3** | **No / yes.** The minimum combination lacks A11; **E6 and E7 hold it.** What stops the row is therefore not the detector's privilege but that altering the seal too is **F-1b**, a different and larger act. Stated here rather than left implicit | the **writer** **W7**; coordinator **C-a/C-d** | `SW-J11` | adding A11 + A2 rebuilds a consistent generation, which is **F-1b** | `JNL-38`, `JNL-49` case 9 |
| **F-6** | the **writer deployment digest** — the writer redeployed without a rotation | **A5** | **E4**; or, through **H-1**, `discordbot`/`freedomweb` against the *repository* copy a future deploy would read | `SB.writer_deployment_digest` (**A1 + A11 + A3**) and the probe report's copy inside `SB` | **No / no.** E4 holds A3 and **not A11**, so it cannot open the seal for a flag change; the H-1 identities hold neither | the **writer** **W11** and **W4**; coordinator **C-d** | `SW-J22`, `SW-J25` | E6/E7 make it **F-1b** with a redeployment inside it | `JNL-39`, `JNL-49` case 2 |
| **F-7** | the **host identity** — the tree restored onto another host, or `/etc/machine-id` rewritten to match | **A6** | **E7 on the host where the tree is read** — which holds every disk authority there, and it changes nothing, because there is no detector to reach | none exists | **Yes, and completely** — every copy of the fact records the same value | **None for the forged-matching case.** For an **unforged** host change the writer refuses at **W10** and the coordinator at **C-d** | `SW-J23` at **W10** and `J-16` at **C-d** — **only where the machine-id was not forged** | **this row has no “both” case, because there is nothing on either side to disagree.** A forged matching host identity is a **residual**: **R-5.0-13** | `JNL-40` (two cases), `JNL-49` case 3 |
| **F-8** | the **probe report** inside the seal | **A1 + A11 + A3** | **E6**, or **E7** | `probe_report_digest` inside `SB`, and record 0 — the latter **A1 + A10 + A2** | **Partly / yes.** The same combination keeps the seal self-consistent, but `seal_body_digest` then changes and record 0 does not, which needs A10 + A2 — **which E6 and E7 hold** | the **writer** **W4** (report/digest) and **W13** (record 0); coordinator **C-d** against `append_only_probe_digest` | `SW-J25`, `SW-J04` | it becomes **F-1b**; the registered `append_only_probe_digest` is then the only disagreement | `JNL-41` |
| **F-9** | **`BND.genesis_record_digest` alone** | **A1 + A11 + A3** | **E6**, or **E7** | the value the writer **derives** from `SB` by Algorithm C step **C4** — an algorithm, not an artifact | **No / no.** No authority reaches a derivation | the **writer** **W5**; coordinator **C-a/C-d** | `SW-J24` | the combination cannot make the derivation agree without changing `SB`, which is **F-1a** | `JNL-42` |
| **F-10** | **`BND.journal_device` alone** | **A1 + A11 + A3** | **E6**, or **E7** | `fstat(st_dev)` on the opened journal — the kernel, not a file | **No / no** | the **writer** **W7**; coordinator **C-a/C-d** | `SW-J11` | to make `fstat` agree the attacker must move the journal to another device, which is A3 plus a second filesystem | `JNL-43` |
| **F-11** | **`BND.journal_inode` alone** | **A1 + A11 + A3** | **E6**, or **E7** | `fstat(st_ino)` | **No / no** | the **writer** **W7**; coordinator **C-a/C-d** | `SW-J11` | as F-10, and it becomes **F-5** | `JNL-44` |
| **F-12** | a **`sealed_at` field present in the binding** — a revision-6-layout seal, or a field appended to a current one | **A1 + A11 + A3** | **E6**, or **E7** | `binding_format_version` in `SB`, authenticated by record 0 (**A1 + A10 + A2**) | **No / yes** | the **writer** **W3**; coordinator **C-a** | `SW-J24` | it becomes **F-1b** | `JNL-45` |
| **F-13** *(new in revision 12; this is remediation R11-A)* | the **deployed program**, replaced by bytes no review approved — with the approval record, the object store and the provenance record all rewritten to agree | **A5** to construct it; **A5 + A8** for it to survive registration | **E7** for the host half. **`discordbot` and `freedomweb` hold neither half**: they can write the *worktree*, and no step of Algorithm D reads it (`JNL-51` case (h)) | four sources compared at **C0**: `APR`, `TM` from the Git objects, `SM` from the live bytes, and `PVR`; then **W11a**; then `V-R`'s `approved_source_revisions` lookup and `NOT NULL` foreign key. **Their prerequisites are A5 for the three host artifacts and A8 for the database row** | **No / no** — for **A5 alone**. An A5 holder can make every *host* copy agree and **still cannot register the generation**, because the row it needs is in PostgreSQL | the **database**, at registration; and root's four-way comparison at **C0** | `J-28` at **V-R**; `J-26`/`J-27` and `SW-J26`/`SW-J27` on the host side; `DEP-01 … DEP-09` at deploy | **A5 + A8** — an actor who can both substitute the deployment and invoke `register-journal-generation` as the Platform Administrator approves and registers its own revision. **That boundary is operator trust, not a technical control**, and it is **R-5.0-15**, recorded rather than described as a refusal | `JNL-51`, `JNL-53` |

**Every row that changed in revision 10, and by how much.** F-1a, F-4, F-5, F-8,
F-9, F-10, F-11 and F-12 gain **A11**; F-1b gains **A10 and A11**; F-2 and F-5
gain **A10**. **F-3, F-6 and F-7 are unchanged**, because none of them changes an
inode flag. **No row was added, removed or reclassified**, and **no refusal was
strengthened**: every correction adds a prerequisite to what an attacker must
hold, which makes each alteration *harder*, and the design claims nothing new for
it.

**What revision 12 changes here, and what it does not.** **One row is added,
F-13**, and it is a falsification revision 11 had no row for at all: substituting
the deployed program. **No existing row's minimum combination, smallest real
holder, detector, reach, refusing actor, code or residual moves**, because
`A1 … A4` and `A6 … A11` are untouched and `A5`'s **holder set** is unchanged —
only the artifacts it covers grew, and they grew to include three artifacts that
are `root:root` like the deployment path already was. **F-13 is the one row whose
independent refusal is the database rather than the writer**, which puts it
beside **F-1b** rather than beside the on-disk rows, and its residual is stated
as operator trust rather than as a control.

---

##### F-7, in full, because R8-D requires the design to be honest rather than re-worded. **Retained unchanged from revision 9.**

*What the design does.* `SB.host_machine_id` is fixed once at **C3** and sealed
under `+i`. **W10** compares it with `/etc/machine-id`. **C-d** compares the
**registered** `host_machine_id` with the value read from disk — which is
`SB.host_machine_id`. All three copies record the *same fact*, taken at the same
instant, from the same host.

*What that means when the fact is forged.* An actor holding **A6** rewrites
`/etc/machine-id` on the host where the tree is read. `SB.host_machine_id`,
`/etc/machine-id` and the registered row now agree. **W10 passes. C-d passes.**
Storing a copy outside the restored tree creates no mismatch, because the copy
stored there is the same forged-to-match value. **There is no independent
host-bound authenticated value anywhere in this design.**

*Why device and inode are not a substitute, and are withdrawn as one.* Revision 8
leaned on *"changed device/inode values"*. They are **incidental**. A restore that
changes `st_dev`/`st_ino` is refused at **W7** with `SW-J11` and at **C-d** on
`journal_device`/`journal_inode` — which is **F-5**, **F-10** or **F-11**, and the
refusal names *those* fields, not host identity. A restore that **preserves**
them — an image-level restore, or a filesystem laid down to place the inode — is
refused by nothing. **A detector that fires only when a different, named field
happens to differ is not a host-identity detector**, and revision 9 stopped
calling it one. Stop condition **10h** forbids the class.

*The independent operational evidence that remains, named rather than implied.*

| Evidence | What it establishes | What it does not |
|---|---|---|
| the **production PostgreSQL**, which the restored tree does not carry | a forged tree on another host affects nothing until its holder can also record evidence through the coordinator (**A8**) and, to change what is already registered, hold **A9**. A restored tree alone is inert | it does not detect the forgery; it means the forgery has **no effect** unless the attacker also reaches the production database, which is the **F-3** / **R-5.0-12** boundary |
| `sudo`'s `log_output`, journald, and the `audit_events` chain | **where** `init-generation` and `register-journal-generation` actually ran, under whose account, and when | anything, if the attacker also holds A7 on the machine those records live on |
| the **archive** on the production host | a forged head has no `seal` record, no `.close` manifest and no archived predecessor behind it | it does not distinguish two hosts claiming the same identity |
| the production host's own systemd and deployment records | that the real writer unit ran on the real host, with the deployment `DD` names | it is operational evidence for a human, not a refusal any algorithm here makes |

*The alternative, priced and routed rather than adopted.* A genuinely independent
authenticated host-bound value would close this — for example a TPM-sealed or
coordinator-signed host token that the seal carries and that a second host cannot
reproduce. **It changes the design surface**, so under §0.2 it is raised as
**D5.0-13 / OD-66 option A-2** (§5.3), with its authority, provisioning,
rotation, backup/restore behaviour and verification specified there, and it is
**not adopted here**. Revision 10 continues to take the first of R8-D's two
options.

---

##### The pairings that are not constructible, with the control that makes them so

These are the pairings the **stated threat model** — an unprivileged compromise of
the writer, §2.13.2 requirement (c) — is built on. **Revision 10 restates two
rows revision 9 had wrong and adds two that isolate the kernel checks.**

| Identity | Authority sought | Constructible? | The control that refuses it, and the syscall that proves it | Test |
|---|---|---|---|---|
| **E1** `freedomsheet` | **A3** seal write / journal-directory write | **No** | seal `0440` and not writable by its group; `…/journal` `0750` with group `r-x`, so no create-and-rename either. `open(seal, O_WRONLY)` → **`EPERM`** while `+i` is set (immutability is checked before DAC), and **`EACCES`** on a disposable copy without `+i`, which is the assertion that proves the *mode* rather than the flag; `creat`/`unlink`/`rename` in `…/journal` → **`EACCES`** | `JNL-33`, `JNL-50` cases 1–2 |
| **E1** `freedomsheet` | **A2** on the journal file | **Yes — it holds it, by ownership.** *Revision 8 recorded this as “No”, which was wrong: mode `0640` gives the owner `rw`* | **nothing in DAC refuses it.** What refuses a non-append write is **`FS_APPEND_FL`**, i.e. the absence of **A1** | `JNL-13`, `JNL-50` case 12 |
| **E1** `freedomsheet` | **A1** flag control on **its own** journal file | **No** | `CapabilityBoundingSet=` empty and `NoNewPrivileges=true`, so `CAP_LINUX_IMMUTABLE` cannot be acquired → `FS_IOC_SETFLAGS` clearing `FS_APPEND_FL` → **`EPERM`**. **This is the clean isolation of A1**: E1 *owns* the inode, so **A10 is satisfied** and the missing prerequisite is the capability and only the capability | `JNL-13`, `JNL-50` case 3 |
| **E1** `freedomsheet` | **A11** flag control over the **root-owned** seal | **No, and for a second independent reason** | it holds neither uid 0 nor `CAP_FOWNER`, so `FS_IOC_SETFLAGS` on the seal returns **`EPERM`** *even in a hypothetical where it held A1*. **E2 — the same uid with an ambient `CAP_LINUX_IMMUTABLE` — is the executed proof**, and it is what makes F-2's detector separation real rather than assumed. **Its control is form C-II** (§2.13.5c): the identity is held fixed and the *inode's owner* is varied, because no identity in the table differs from E2 by `CAP_FOWNER` alone. E2 receives `EPERM` on the root-owned seal and **succeeds** on a `freedomsheet`-owned `+i` file created identically beside it. *Revision 10 named no control for this case* | `JNL-50` case 4 |
| **E1** `freedomsheet` | **A4** archive write or traversal | **No** | `…/archive` is `0750 root:freedomcoord` and the writer is *other* → **`EACCES`** at the directory, before any file is reached | `JNL-33`, `JNL-50` case 5 |
| **E1** `freedomsheet` | **A8**/**A9** database authority | **No** | the writer opens **no database connection at all** and holds no role; there is nothing to authenticate as | `JNL-50` case 11 |
| **E4** — every discretionary right, **no `CAP_FOWNER`** — **new in revision 10** | **A11** on a root-owned archive file, and **A10** on the journal | **No** | **this is the isolating control R9-A requires.** `CAP_DAC_READ_SEARCH` and `CAP_DAC_OVERRIDE` satisfy traverse and open, so `open(archive_file, O_RDONLY)` **succeeds**; `FS_IOC_SETFLAGS` clearing `FS_IMMUTABLE_FL` then returns **`EPERM`**, because the caller neither owns the inode nor holds `CAP_FOWNER`. **The positive control is the identical call by E6**, which adds `CAP_FOWNER` and **succeeds** on a disposable copy — so the refusal is attributable to the owner check and not to DAC, to path search or to the flag capability. **This is control form C-I** (§2.13.5c): E4 and E6 differ in `CAP_FOWNER` and in no other option. The journal half is the same shape against `FS_APPEND_FL`, and **its isolating control is E6 as well** — **corrected in revision 11**, because revision 10 named **E2**, which differs from E4 in uid, supplementary groups **and two capabilities** and therefore isolates nothing. **E2 is retained as a corroborating control** showing the *other* route to the same check, ownership, and is labelled as such | `JNL-50` cases 6–7 |
| **E5** — `CAP_LINUX_IMMUTABLE` + `CAP_FOWNER`, in `freedomcoord` — **new in revision 10, and it is the corrected form of revision 9's case 9** | **A4** archive **write** | **No** | it holds **A1 + A11**, so `FS_IOC_SETFLAGS` clearing `FS_IMMUTABLE_FL` **succeeds** — that is A1 and A11 doing exactly their job — and the subsequent `open(O_WRONLY)` returns **`EACCES`**, because the file is `0440 root:freedomcoord` and `freedomcoord` membership confers read and traverse and never write. **This is the executed proof that flag authority confers no DAC**, and unlike revision 9's version it is constructible, because it holds the owner half | `JNL-49` case 12 |
| **E5** | **A3** journal-directory write | **No** | `…/journal` is `0750 root:freedomjournal` with no `w` for group or other, and `fbprobe` is not in `freedomjournal` → **`EACCES`**. Clearing a flag changes no directory permission | `JNL-50` case 8 |
| **E8** `freedomcoord` | **A2**/**A3** journal write | **No** | no write bit on `…/journal` or on the `0440` seal; no `CAP_LINUX_IMMUTABLE` and no `CAP_FOWNER`; `freedom-journal-admin` is a *separate* executable in a *separate* `sudoers` drop-in that runs as root, and no rule grants the coordinator root (§2.13.7) | `JNL-50` case 9 |
| **E8** `freedomcoord` | **A4** archive **write** | **No** | membership of `freedomcoord` gives **traverse and read** on `…/archive` and read on its `0440` files. **It confers no write on any of them**, and the coordinator holds neither A1 nor A11: `open(O_WRONLY)` → **`EPERM`** while `+i` is set, **`EACCES`** on a disposable copy without it | `JNL-50` case 10 |
| **E8** `freedomcoord` | **A9** mutation | **No** | `UPDATE`/`DELETE`/`TRUNCATE` revoked, and `reject_history_mutation` refuses them for every principal including the schema owner | `JNL-36`, `JNL-50` case 11 |
| `discordbot`, `freedomweb`, `foundry` | anything under `…/journal` | **No** | `…/journal` moved from `0751` to `0750` in revision 6, so *other* has no traverse at all → **`EACCES`** on the directory itself | `JNL-50` case 11 |

---

##### What this matrix claims, stated to the exact boundary rather than one step past it

Revision 9's five bounded claims are re-stated. **The second is corrected, the
third is narrowed, and a sixth is added.**

1. **Every row whose minimum combination does not also reach its detector is
   refused by an actor that did not author the altered artifact.** That is F-1a,
   F-2, F-3, F-4, F-6 and F-8 … F-12. It is **not** a claim about a class, and
   **not** a claim that one attacker reaches all of them. F-5 is excluded here
   deliberately: its combination reaches its detector's prerequisites once A11 is
   added, and what stops it is that using them is a larger act (F-1b).
2. **Only three rows are bounded by the attacker's authority rather than by its
   choice of alteration** — **F-2**, **F-3** and **F-6** — because for those
   three the *smallest identity that can hold the minimum combination* still
   cannot reach the detector. **Revision 9 implied this held for eleven rows; it
   does not**, and the holder table is why. For every other row the refusal is
   real but the attacker could have chosen the larger alteration instead: the
   writer's refusal tells a responder **what was done**, not **what could have
   been done**. *This is remediation R9-B stated as a bounded claim rather than
   as a qualification buried in F-1a.*
3. **Nine rows are refused by the writer alone, from disk, with no database**:
   F-1a, F-2, F-5, F-6, F-8, F-9, F-10, F-11 and F-12. **F-3 and F-4 are not** —
   F-3 is refused by PostgreSQL and F-4 by the coordinator's archive
   verification, and the writer can read neither.
4. **F-1b is refused only by the coordinator, against PostgreSQL.** An
   **A1 + A2 + A3 + A10 + A11** attacker produces a seal and a journal that agree
   with each other, and no check confined to this host can distinguish that from a
   genuine generation. The registered row is the one copy of those digests the
   attacker did not write.
5. **When an attacker holds both the artifact and its detector, this design
   detects rather than prevents.** That is **A1 + A2 + A3 + A10 + A11 + A9**,
   which needs root on the host *and* a PostgreSQL superuser. It is recorded as
   **R-5.0-12** with what actually remains — `sudo log_output`, journald, the
   `audit_events` chain and offline backups — and it is **not** claimed as a
   refusal anywhere.
6. **One alteration has no detector in this design at all.** A forged matching
   `/etc/machine-id` under **A6** is seen by neither W10 nor C-d, because every
   copy of that fact records the same value. It is **R-5.0-13**, the operational
   evidence that remains is tabulated above, and the design change that would
   close it is routed as OD-66 option A-2 rather than adopted.

**`chattr +i` is not offered as the answer to any row.** It is the attribute A1,
A10 and A11 *together* clear, which is exactly why the register above is written
in authorities and not in attributes — and why the flag rows and the DAC rows are
separate, because clearing an attribute is neither obtaining access nor, on its
own, permitted.

**And the one-directional comparison is preserved.** Nothing on disk depends on a
PostgreSQL value; the coordinator compares disk **to** the registered row and
never the reverse; and the writer still opens no database connection, so the
Freedom bot's legacy mutation path takes no database dependency (§2.13.5,
§2.13.2 S-4).


#### 2.13.6 Every journal condition and its fail-closed outcome

Two actors, two refusals, and they are different refusals. **W** is the writer, at
start and before each dispatch; its refusal is *refuse new Sheet mutations*. **C**
is the coordinator, at `observe`; its refusal is *record no
`dispatch_journal_clear` row*, which makes the activation trigger refuse because a
required method has no evidence.

Every row of the handoff's enumeration is present, and **no row resolves to
"continue"**. **Revision 6 adds four rows — J-22 … J-25 — because remediation
R5-A and R5-B gave the writer four checks it could not previously perform.**
**Revision 12 adds three more — J-26 … J-28 — because remediation R11-A gives the
writer one check and the coordinator two that neither could previously perform.**
The table is now **twenty-eight rows** and the writer's refusal family
**`SW-J01 … SW-J28`**. The deploy step's own `DEP-01 … DEP-09` family
(§2.12.5a) is **not** in this table: the deploy step is neither the writer nor
the coordinator, and it refuses before either exists.

| # | Condition | Detected by | W | C | Net effect |
|---|---|---|---|---|---|
| **J-01** | **Reboot** (clean) | the journal is on durable ext4 and is re-validated at start by **V-W** | validate the seal, chain and inode, then continue appending | reads the surviving journal; a pre-reboot unresolved entry is **still unresolved** | **an unresolved entry survives a reboot.** This is the property `/run` destroyed, and it is the single most important row in the table |
| **J-02** | **Unclean shutdown / power loss** | the tail record is short of its length prefix, or its `record_hash` does not verify (**W15**) | refuse; the generation is `suspect` and only `freedom-journal-admin repair` may seal it | treat the torn tail as **one unresolved dispatch of unknown identity**; refuse | fail closed on both sides |
| **J-03** | **Missing journal file, or a `current` symlink that does not resolve to a well-formed name** | `open` → `ENOENT`, or **W1** | refuse. **The writer cannot create one** — §2.13.3 | refuse. *Missing* is not *empty* | fail closed |
| **J-04** | **Empty file, or a record 0 that is not the genesis record the seal body derives** | size 0, or **W13**'s byte comparison | refuse | refuse | **the P5.0-R5 case, closed** |
| **J-05** | **Wrong owner, group or mode** | **W8**, against the seal body's recorded `uid`/`gid`/`mode` | refuse | refuse | fail closed |
| **J-06** | **Append-only attribute absent or unsupported** | **W9**: `FS_IOC_GETFLAGS` lacks `FS_APPEND_FL`, or returns `ENOTTY`/`EOPNOTSUPP` | refuse | refuse | the capability is verified at runtime **without a destructive test** — the correction R5-C requires; a filesystem type is never accepted as evidence of it |
| **J-07** | **Malformed record** anywhere but the tail | length-prefix, canonical-form or parse failure (**W14**) | refuse | refuse | fail closed |
| **J-08** | **Sequence gap** | `seq[i] ≠ seq[i−1] + 1` | refuse | refuse | a gap means records are missing, which is the unsafe direction |
| **J-09** | **Checksum / chain failure** | `prev_hash` ≠ the predecessor's `record_hash`, or a `record_hash` that does not verify | refuse | refuse | detects rewriting even where `+a` did not prevent it |
| **J-10** | **Duplicate sequence** | two records share a `seq` | refuse | refuse | fail closed |
| **J-11** | **Replaced inode** | **W7**: `(st_dev, st_ino)` ≠ the seal binding's, and — for C — ≠ the registered generation's | refuse | refuse | a replaced journal is not an empty one |
| **J-12** | **Unreadable file or seal** — `EACCES`, `EIO`, a media error | `open`/`read` error | refuse | refuse. ***Unreadable* is never *clear*** | fail closed |
| **J-13** | **Filesystem full or read-only** | **W12**: free space below **N5.0-21**, `ST_RDONLY` set, or `write`/`fsync` → `ENOSPC`/`EROFS` | **refuse before dispatch.** The writer never dispatches a request it could not journal first | if the last durable state is an unrecorded intent it cannot be known, so the integrity failure refuses | **disk-full prevents a dispatch; it never permits an unjournalled one** |
| **J-14** | **`fsync` failure** | `fsync` returns an error | refuse; mark the generation `suspect` for the life of the process; exit non-zero | refuse | Linux may not retry failed writeback, so a failed `fsync` is terminal for the generation rather than retryable |
| **J-15** | **Outcome append fails** after a dispatch | append or `fsync` error on the outcome record | the request stays **unresolved**; refuse further dispatch; exit non-zero | the unresolved entry refuses `dispatch_journal_clear` | over-reporting, which is the safe direction |
| **J-16** | **Generation unregistered, superseded, or disagreeing with the registered row** | **C-c/C-d**: any of **sixteen** compared values differs (*thirteen before revision 12, which adds the three provenance values*), or no unsuperseded head exists | — (the writer does not read PostgreSQL) | refuse | prevents stale, cross-generation and rolled-back evidence |
| **J-17** | **Seal missing, mutable, unreadable, or failing its own structure** | **W2**, **W6**, **C-b**: absent, `+i` not set, or the seal's parts do not verify | refuse | refuse | the seal is what makes generation zero distinguishable from a reset |
| **J-18** | **A record from another generation** | a record whose `generation_id` ≠ the seal body's | refuse | refuse | prevents splicing one journal into another |
| **J-19** | **A dispatch after a `seal` record** | **W16**: the last record's kind is `seal` | refuse — the generation is closed | refuse | prevents appending to a sealed generation |
| **J-20** | **Unresolved set non-empty** | **C-e**: a `dispatch` with no matching `outcome`, or a torn tail | (computed for its own refusal; the writer authors no evidence) | refuse (**N5.0-20 = zero**); enumerate each entry with its ranges and payload digest for human adjudication | the revision-4 control, retained unchanged |
| **J-21** | **Non-monotonic timestamp** | a record's `at` earlier than its predecessor's | refuse | refuse | recorded for completeness; the chain and sequence would already refuse most instances |
| **J-22** | **New in revision 6. Writer deployment digest mismatch** | **W11**: the digest the process computes over its own deployed files ≠ `SB.writer_deployment_digest` | refuse | refuse (**C-d**) | **a writer redeployed without a rotation cannot reuse the old generation's clear evidence.** Revision 5 bound the deployment into the seal and then gave the writer no way to check it |
| **J-23** | **New in revision 6; scope narrowed in revision 9 (R8-D). Host identity mismatch — the *unforged* case, and only that** | **W10**: `/etc/machine-id` ≠ `SB.host_machine_id` | refuse | refuse (**C-d**) | a journal and seal restored onto another host **whose `/etc/machine-id` was left alone** refuse **before** any Sheet mutation, not only at the coordinator. **It detects nothing where `/etc/machine-id` has been rewritten to the recorded value**: `SB`, the file and the registered row then carry the same value and neither W10 nor C-d has anything to compare. That is **F-7** and residual **R-5.0-13**, not a condition this table can add |
| **J-24** | **New in revision 6; widened in revision 7. The seal's internal structure or its genesis derivation fails** | **W3**, **W5**: an unknown body `format_version`, an unsupported or short binding, **any byte after the binding the `binding_format_version` does not permit — including a `sealed_at` field revision 7 withdrew** — or a derived genesis digest ≠ the binding section's | refuse | refuse | **this is the row that makes §2.13.5a checkable at runtime.** A seal whose parts do not derive each other is not a seal; and after **R6-B** a seal carrying a field no **V-W** step authenticates is not a seal either |
| **J-25** | **New in revision 6. The probe report is absent, altered, unsupported, or not a pass** | **W4**: `probe_report_digest` mismatch, an `append_only_probe_version` this build does not support, any case not passing, or — *amended 2026-09-23, pending review* — an S4-3 attestation made under a systemd identity other than the host's current one | refuse | refuse (**C-d**, against the registered `append_only_probe_digest`) | **the probe's result travels with the evidence and is re-checked**, rather than being trusted because a database column said `true` |
| **J-26** | **New in revision 12. The provenance record is absent, wrongly owned or moded, malformed, or disagrees with the seal** | **W11a**: `/etc/freedom-blades/sheet-writer.provenance` missing, not `root:root 0444`, unparseable, or differing from `SB` on `source_commit`, `source_tree_id` or `source_manifest_digest`. **C-a** performs the same check | refuse | refuse | **an omitted or removed provenance step is a refusal, not a default.** This is the condition that closes the *"skipped silently"* half of P5.0-SR1, and it holds at the writer even with no database reachable |
| **J-27** | **New in revision 12. The deployed source manifest does not match the sealed one** | **W11a**: `deployed_source_manifest_digest()` over this process's own region-S bytes ≠ `SB.source_manifest_digest` — including because a file was added to the deployed root that belongs to neither region | refuse | refuse (**C-a**, and **C-d** against the registered `source_manifest_digest`) | **the writer refuses to dispatch under bytes that are not the sealed reviewed bytes**, which `J-22` did not cover: `J-22` compares a digest of the deployment with itself at two times, and this compares the deployment with a **reviewed source** |
| **J-28** | **New in revision 12. The generation's source revision is not an approved revision** | **V-R**: no `approved_source_revisions` row matches `(component, source_commit, source_tree_id, source_manifest_digest)`; and, structurally, the `NOT NULL` foreign key on `sheet_writer_journal_generations` | — (*the writer does not read PostgreSQL*) | **refuse — the generation cannot be registered at all** | **an unprovenanced deployment cannot reach activation**, because **C-c** requires a registered generation and no such row can exist. The refusal is a schema constraint, not a procedure step, so it survives a coordinator whose code was altered |

**The writer's refusal is typed and named, and it is not a crash.** Each row has a
refusal code in the `SW-J01 … SW-J28` family, on the `S-01 … S-15` precedent
(`application/web/config.py`). The Freedom bot stays online: reads, `/info` and
every non-mutating command are unaffected, and an affected mutation is refused
with a typed message carrying **no** exception text, path or `errno` — the
`.agents/AGENTS.md` Discord rule. The operational cost of that is real and is
named as risk **R-5.0-11**, which revision 6 extends to the four conditions it
added and **revision 12 extends again to `J-26` and `J-27`** — a writer whose
provenance record has been removed or whose deployment has drifted refuses every
Sheet mutation until an operator acts, which is the fail-closed direction and an
availability cost (**R-5.0-16**).

#### 2.13.7 The privileged lifecycle — seal, rotate, archive, retain, dispose

`freedom-journal-admin` is a second root-owned wrapper at
`/opt/freedom-blades/coordinator/bin/freedom-journal-admin`, invoked through
`/etc/sudoers.d/freedom-journal-admin`:

```
Cmnd_Alias FREEDOM_JOURNAL_ADMIN = /opt/freedom-blades/coordinator/bin/freedom-journal-admin
Defaults!FREEDOM_JOURNAL_ADMIN env_reset, !setenv, log_output, \
    secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
foundry ALL=(root:root) FREEDOM_JOURNAL_ADMIN
```

**It runs as `root`, not as `freedomcoord`**, because setting and clearing `+a`
and `+i` needs **two** things and root is the only identity here that holds both:
`CAP_LINUX_IMMUTABLE`, **and** the owner authorization `FS_IOC_SETFLAGS` requires
— effective UID 0 or `CAP_FOWNER` — over inodes that are root-owned (the seal and
every archived file) as well as over the `freedomsheet`-owned journal.
*Revision 9's version of this sentence named only the capability; that is
remediation **R9-A** applied here.* An ambient `CAP_LINUX_IMMUTABLE` granted to
the coordinator would therefore **not** be sufficient to run the lifecycle, which
is a second reason beyond authority separation — and that is exactly why it is a **separate
executable in a separate drop-in** from `migration-authority`. The two authorities
are revoked independently, and no rule anywhere grants the coordinator identity
root. `NOPASSWD` is absent, as it is for the coordinator. **It drops privilege
with `setpriv` for every probe case that must be executed as the writer**
(§2.13.2a) — including **S4-0**, the unsandboxed positive control revision 8 adds
— and never runs writer-identity work as root, because a probe run as root would
prove nothing about the writer.

| Event | Command | Preconditions, all checked and all refusing | Record it leaves |
|---|---|---|---|
| **Deploy** | *(not `freedom-journal-admin`; the root deploy step of §2.12.5a)* | **New row in revision 12.** `APR` present, `root:root 0444` and naming this component; the reviewed commit present as a commit object in the `0700 root:root` bare store; its tree matching `APR`; the recomputed trusted manifest equal to `APR.source_manifest_digest`; region **D** matching the pinned lock exactly; the staging tree containing **no unaccounted file**; and, after installation, the deployed source manifest equal to the trusted one and every uid, gid and mode equal to the reviewed deployment map's. **Nine refusals, `DEP-01 … DEP-09`, and a failure at or after installation restores the predecessor** | the provenance record `PVR` at `/etc/freedom-blades/<component>.provenance`, written last and outside the deployed root. **There is no deployed state without it** |
| **Verify capability** | `verify-capability` | the writer unit is **inactive**; **its unit file is deployed and the supplied `writer_deployment_digest` equals the digest this command computes** over §2.13.2c's manifest (revision 9, R8-A — *revision 7 required only that a digest be supplied, and revision 8 deferred the comparison to `init-generation` C2*); `…/journal` and `…/archive` have the §2.13.3 owners and modes; **any `…/probe` or `…/probe-ro` residue is reported and the run refuses — it is never cleaned and never reused** (revision 9, R8-B; *revision 8 cleaned it as an explicit first step*) | the **four-stage** probe report of §2.13.2a — **all four stages run in this one invocation**, before the report is built, with **S4-0** preceding **S4-2** — returned to the caller and, inside `init-generation`, carried into the seal body and, as a digest, a version and a timestamp, into the registered generation. Run standalone it prints the report and **writes nothing**. **Cleanup runs in a `finally` over both transient directories; a failed cleanup is a distinct non-zero exit naming every remaining artifact by path — §2.13.2b state S-B** |
| **Create a generation** | `init-generation` | **Corrected in revision 8 (R7-A) and again in revision 9 (R8-A), and the preconditions are split by when they can be known.** *Before the probe runs* (**C0**): the writer unit is **inactive**; **its unit file is deployed**; `…/probe` and `…/probe-ro` are **absent**, and are **refused rather than cleaned** if present; the predecessor is **sealed and archived** and its `.close` manifest re-verifies; a deployment digest is **supplied, well-formed, and equal to `DD`, which C0 computes over the deployed manifest** — the supplied string is then discarded; and — **new in revision 12** — **the reviewed-source provenance preconditions of §2.12.5a**: `PVR` and `APR` present, `root:root 0444` and well-formed; the two agreeing on commit, tree and source-manifest digest; the trusted manifest **recomputed from the Git object store** and equal to both; the deployed source manifest **recomputed over the live bytes** and equal to it; no unaccounted file in the deployed root; `PVR.deployment_manifest_digest` equal to `DD`; and the supplied `--source-commit` equal to `APR.source_commit`, then discarded. **An absent provenance record refuses here**, which is the omission test `JNL-51` case (g) executes. *After the probe runs* (**C2**): the report carries **all four stages**, every case **passed**, `PR.writer_deployment_digest` equals `DD`, **a second manifest computation still equals `DD`**, and the cleanup **completed**. *Revision 7 required the second set at C0, before C1 had produced it; revision 8 consumed the supplied digest at C1 and compared it at C2 against the probe's copy of that same string* | Algorithm **C** of §2.13.5a, in order: the journal with its genesis record, `+a`, the `root:freedomjournal 0440` `+i` seal, the `current` symlink; and the values the operator must pass to `RegisterJournalGeneration`. **Nothing under `…/journal` is created before C5**, so every refusal at C0, C1 or C2 creates **no generation and no database artifact**; whether it also leaves **no transient residue** depends on cleanup, which is §2.13.2b's three states (`JNL-47`) |
| **Register it** | *(coordinator, not root)* `migration-authority register-journal-generation` | Algorithm **V-R**: the seal parses and derives; the digests match the files on disk; the predecessor row is closed and its archive verifies; **and — new in revision 12 — an `approved_source_revisions` row matches the seal's `(component, source_commit, source_tree_id, source_manifest_digest)`, refusing with `J-28` if there is none** | one `sheet_writer_journal_generations` row — **carrying a `NOT NULL` foreign key to that approved revision** — + receipt + audit, one transaction |
| **Seal** | `seal` | the writer unit is **inactive**; the chain validates | a `seal` record appended and `fsync`-ed; `+a` cleared; the file moved to `…/archive`, set `root:freedomcoord 0440` and `+i`; a `.close` manifest (§2.13.5a) carrying the final `record_hash`, the record count and **the unresolved set at seal time** |
| **Rotate** | `rotate` | `seal`, then `init-generation` — which runs the probe itself at **C1** — as one operator act; refuses while the writer is active. *Revision 7 listed `verify-capability` as a separate preceding step, which under R7-A would have been a second probe invocation with a second report; `init-generation` owns the single invocation* | all of the above; the operator then registers the successor |
| **Repair** | `repair` | only for a `suspect` generation (**J-02**, **J-14**); it **seals**, it never edits | the torn tail is preserved verbatim in the archive and named in the `.close` manifest |
| **Verify an archive** | `archive-verify` | — | re-reads an archived generation, re-derives its genesis record from its seal body, and re-validates its chain against its `.close` manifest. Run in the WP-9 rehearsal, at every registration of a successor, and after any restore |
| **Retain** | *(no command)* | — | **N5.0-23**: an archived generation is retained until plan §15.1's Sheet-retirement gate closes, and in no case less than 365 days |
| **Dispose** | `dispose` | N5.0-23 elapsed **and** §15.1's gate closed **and** a Data Owner approval reference supplied **and** `archive-verify` passed | an `audit_events` row and a change-log entry naming the generation and the approval. It is the only path that deletes evidence, and it clears `+i` as a root act under `log_output` |

**Clearing does not require an undocumented ambient capability — and revision 10
completes the sentence that says so.** Revision 4's sentence — *"clearing it needs
`CAP_LINUX_IMMUTABLE`"* — is withdrawn as a specification, **and it was in any
case incomplete**: `FS_IOC_SETFLAGS` also requires the caller's effective UID to
equal the inode's owner or `CAP_FOWNER` (§2.13.5c **A10**, **A11**), which for the
root-owned seal and archive means uid 0 or `CAP_FOWNER` and for the journal file
means `freedomsheet`'s own uid or `CAP_FOWNER`. **So a granted ambient
`CAP_LINUX_IMMUTABLE` would not even suffice**, which is a second reason beyond
authority separation to keep this a root tool. The capability is real, but the *documented* way to clear a journal
is `seal` followed, much later and under approval, by `dispose`; both are named
commands with named preconditions, a named invoker and three audit trails
(`sudo` `log_output`, journald, `audit_events`). A bare `chattr -a` by a human is
not a procedure this design offers, and the operations document says so.

#### 2.13.8 The record format, and the evidence that falsifies each claim

**One record per line, length-prefixed, canonically encoded**, in the shape
`application/idempotency.py`'s `canonical_request_hash` already establishes:
typed, length-delimited and schema-versioned, so two encoders cannot disagree.

| Field | Every record | Notes |
|---|---|---|
| `format_version` | yes | an integer; an unknown version is **J-07** |
| `generation_id` | yes | ≠ the seal body's is **J-18** |
| `seq` | yes | 0 is `genesis`; a gap is **J-08**, a duplicate is **J-10** |
| `kind` | yes | `genesis` \| `startup` \| `dispatch` \| `outcome` \| `seal` |
| `at` | yes | the writer's clock, **for diagnosis only** — no fencing decision reads it (**J-21** merely refuses when it goes backwards) |
| `prev_hash` | yes | **`genesis` uses `seal_body_digest`** — *revision 5 said `seal_digest`, which was the cycle*; every other record uses its predecessor's `record_hash` |
| `record_hash` | yes | SHA-256 over `prev_hash ‖ canonical body` |
| `seal_body_digest` | `genesis` | the anchor, repeated in the record so the chain root is self-describing |
| `writer_deployment_digest`, `source_manifest_digest`, `resumed_at_seq` | `startup` | **new in revision 6; `source_manifest_digest` added in revision 12.** One record per writer start, appended by **W17**; it is the writer's non-destructive demonstration that appending works, and — from revision 12 — the durable record of **which reviewed source** the process that appended it was running |
| `request_id`, `target_ranges`, `payload_digest` | `dispatch` | **no cell values, ever** — ranges and a digest only, the same rule `observed_detail` follows |
| `request_id`, `outcome`, `status_class` | `outcome` | `applied` \| `refused` \| `error` \| `timeout` |
| `final_record_hash`, `record_count`, `unresolved_set` | `seal` | mirrors the `.close` manifest, so the archive is self-describing |

**The unresolved set** is *every `dispatch` whose `request_id` has no `outcome`
record*, plus **one synthetic unknown entry if the tail is torn** (**J-02**). The
second half is what stops a truncation from reading as a clean set. `startup`
records are never part of it.

**The evidence band, `TC-5.0-JNL-01 … 53`** — **fifty-three identifiers and one
hundred and fourteen cases** after remediation R11. *Revision 11 had fifty and
eighty-eight; the arithmetic of the change is stated after the revision-10
paragraph below rather than left to be recomputed.* `JNL-02`, `JNL-32` and `JNL-34` each carry two; `JNL-40`
carries two, `JNL-46` five, `JNL-47` six, `JNL-48` four, `JNL-49` twelve and
`JNL-50` twelve. Twenty-six identifiers from revision 5, fifteen added by
remediation R5, four by remediation R6 (`JNL-42 … 45`) and five by remediation R7
(`JNL-46 … 50`). **Remediation R8 added no identifier**: its ten added cases sat
under existing ones — `JNL-46` 1 → 5, `JNL-47` 5 → 6, `JNL-49` 8 → 10, `JNL-50`
8 → 10, `JNL-40` 1 → 2. **Remediation R9 adds no identifier either**, and its
arithmetic is `JNL-49` **10 → 12** and `JNL-50` **10 → 12**, a total of
**84 + 4 = 88**: the two added cases per identifier are the isolating
owner-authorization controls **E4**/**E6** and the corrected flag-then-DAC case
**E5**, which revision 9 wrote as one non-constructible case. `JNL-13`,
`JNL-30`, `JNL-35`, `JNL-38` and `JNL-48` change contract without changing case
count — `JNL-13`'s manipulation matrix grows from thirteen rows to **fifteen**
(§2.13.4), which is rows inside one case rather than cases. One test per bullet of
the R4 handoff's falsification plan, plus one per defect the R5, R6, R7, R8 and
R9 handoffs name.

**Remediation R10 adds no identifier and no case, and the arithmetic is
unchanged: fifty identifiers and eighty-eight cases.** This is stated explicitly
rather than recalculated, because R10 corrects **how an identity is constructed**
and **which identity serves as a control** — not which cases exist. `JNL-49`
stays at twelve, `JNL-50` stays at twelve, `JNL-13` stays at fifteen rows inside
one case, and `JNL-40` stays at two. The changes inside those identifiers are:
every identity is built by §2.13.5c's `capsh(1)` procedure instead of the
rejected `setpriv` recipes; every case additionally asserts **securebits**;
`JNL-50` case 7 and the journal half of `JNL-49` case 11 take **E6** as the
isolating control instead of **E2**, retaining E2 as corroborating; and `JNL-50`
case 4 gains the control form **C-II** it previously lacked. **No case changed
its expected syscall, result or `errno`**, which is why no count moves and why
none is invented.

**Remediation R11 adds three identifiers and twenty-six cases, and the arithmetic
is shown.** `JNL-46` **5 → 9**, because the reviewed-source provenance adds four
refusals to Algorithm C's ordered walk that revision 11 had no case for. New
**`JNL-51`** — the deployment contract of §2.12.5a — **eight cases**. New
**`JNL-52`** — the canonical membership table of §2.12.2 — **eight cases**. New
**`JNL-53`** — the three fail-closed conditions `J-26 … J-28` — **six cases**,
one per condition per actor. Total: **88 + 4 + 8 + 8 + 6 = 114**, and
**50 + 3 = 53** identifiers. **No existing case changes its expected syscall,
result or `errno`**, and the one identity correction R11-B makes — `E8` gaining
`freedomjournal` — was checked against every case naming E8 and moves none of
them, because no case asserts E8 is denied a read it now has.

| Requirement | Test | Assertion |
|---|---|---|
| verify the actual filesystem and required append/immutability behaviour at the journal path | `JNL-01` | `/proc/mounts` for the journal path reports a **non-`tmpfs`** filesystem backed by a block device; `+a` set; the §2.13.2a Stage-2 cases each produce their stated `errno` |
| reboot between dispatch and outcome preserves an unresolved entry | `JNL-02a` | **process-level:** the writer is `SIGKILL`ed after a dispatch record, restarted, and the entry is still unresolved |
| — | `JNL-02b` | **boot-level:** a **supervised host reboot** in the WP-9 rehearsal, on a disposable generation. **MD-3, decided 2026-09-23:** this case is mandatory for P5.0-R5 harness-facsimile feasibility closure and may not end as Not Run or an accepted residual. It must run on `oracle-test` under separately reviewed and explicitly authorized operational scope; this requirement is not itself reboot authority |
| service restart cannot reset a non-empty or indeterminate generation | `JNL-03` | after restart the writer **appends** and does not create; `seq` continues; a creation attempt fails `EACCES`; a `suspect` generation refuses to start at all |
| missing, replaced, truncated, corrupt, wrong-owner, wrong-mode, wrong-inode, sequence-gap and checksum-failure states refuse clear evidence | `JNL-04 … 12` | one test per condition **J-03 … J-12**, each asserting the writer's named refusal code **and** the coordinator recording no evidence |
| a compromised `freedomsheet` cannot unlink, rename, replace, truncate, rotate, clear or alter prior records or its parent | `JNL-13` | the **fifteen** rows of §2.13.4, each asserting the expected `errno`, executed under identity **E1** (§2.13.5c). **Revision 10 adds the two flag rows** — `chattr -i` on the seal and on an archived file — and asserts, for the seal, that the refusal survives **both** independent checks: it is `EPERM` under E1, and it is still `EPERM` under **E2**, which holds `CAP_LINUX_IMMUTABLE` and lacks the owner authorization `A11`. *Revision 9 counted thirteen rows and had neither* |
| `SIGKILL` after durable intent and before dispatch safely over-reports | `JNL-14` | the entry exists and is unresolved; the coordinator refuses; **the request was never sent** |
| `SIGKILL` after dispatch and before outcome leaves a durable unresolved entry | `JNL-15` | the entry survives, is unresolved, and names its ranges and payload digest |
| disk-full and `fsync` failure prevent dispatch | `JNL-16`, `JNL-17` | a loopback filesystem filled to `ENOSPC` and an injected `fsync` failure; **the Sheets client is asserted never to have been called** |
| outcome-append failure leaves the request unresolved and prevents activation | `JNL-18` | the entry is unresolved, `dispatch_journal_clear` is refused, the activation trigger refuses |
| privileged rotation and generation change preserve prior evidence and cannot fabricate an empty history | `JNL-19` | `init-generation` refused while unsealed; after `seal`, the archived file is `+i` and unmodifiable; the successor's `predecessor_close_digest` is required; a second unregistered chain head is refused by the partial unique index |
| coordinator observation binds generation, inode/content identity, writer unit, authority revision and observation time | `JNL-20` | the evidence row carries `journal_generation_id`, `journal_last_sequence` and `journal_head_digest`, and the registered generation carries the inode, the unit and the deployment digest |
| reboot, restore or deployment rollback cannot reuse stale clear evidence | `JNL-21` | a successor generation registered **after** the evidence was recorded → the activation trigger refuses; a database restore predating a rotation → `status` refuses before any service starts |
| the activation trigger refuses missing, stale, cross-generation, corrupt or incomplete journal evidence | `JNL-22 … 26` | five trigger-refusal tests, each asserting the named refusal reason |
| **R5-C — the probe's control stage** | **`JNL-27`** | on a file with the arena's ownership and **no** `+a`, cases **C-1 … C-6** all **succeed** as `freedomsheet`; and with any one of them failing, `verify-capability` reports **`inconclusive`** and refuses, rather than `passed` |
| **R5-C — refusal attribution** | **`JNL-28`** | `EACCES` (DAC), `EROFS` (read-only bind) and `EPERM` (append-only, with `FS_IOC_GETFLAGS` confirming the flag) are each produced deliberately and each classified correctly; `ENOTTY` from `FS_IOC_GETFLAGS` is classified as a **failed** probe |
| **R5-C / R6-A — sandbox attribution, at provisioning; extended by R7-B** | **`JNL-29`** | inside a single `verify-capability` invocation, **before the report is built**: the exact `…/probe-ro/s4-2.target` is proved writable, appendable, `fsync`-able, renamable and — on its identically created sibling — unlinkable by `freedomsheet` **outside any unit** (**S4-0**); then, under a `systemd-run` transient unit carrying the deployed unit's hardening verbatim with `ReadWritePaths=` redirected to the arena **and to nothing else**, an append inside it succeeds (**S4-1**) and the same append **to that exact target** fails **`EROFS`** (**S4-2**); `systemctl show` is compared with the deployed unit file and the applied directive set is hashed, with the single substitution recorded (**S4-3**); a directive-set mismatch yields **`inconclusive`**. **S4-0 is asserted to run before S4-2 in every execution**, and a report in which S4-2 passes while S4-0 is absent or failing is asserted to be refused at **C2** and at **W4**. The resulting report is asserted to contain **all four stages**, and `append_only_probe_digest` is asserted to be computed over exactly those bytes |
| **R5-C — privileged cleanup; contract corrected by R8-B** | **`JNL-30`** | after a successful `verify-capability`, `…/probe`, `…/probe-ro` and every artifact in them are gone (§2.13.2b **S-A**/**S-C**); **a planted residue from a crashed run is reported by absolute path and the run refuses — it is asserted *not* to be cleaned and *not* to be reused**, and the residue is asserted to be byte-for-byte unchanged after the refusal (*revision 8 asserted that it was cleaned before re-probing, which contradicted `JNL-48(d)`*); a cleanup failure exits non-zero with the **S-B** exit code, naming every remaining artifact, its failed operation and its `errno`; `verify-capability` refuses while the writer unit is active; `init-generation` refuses at **C0** while either directory exists |
| **R5-A — the construction is acyclic and byte-exact** | **`JNL-31`** | an **independent implementation** of Algorithm C step C3 derives the genesis record from the seal body alone and reproduces it byte for byte; the seal body is asserted to contain **none** of `genesis_record_digest`, `journal_device`, `journal_inode` or `seal_digest`; and a mutation test asserts that adding any of them to the body makes the construction unsatisfiable |
| **R5-C — startup is non-destructive: the successful-start branch, `+a` present** | **`JNL-32a`** | with `FS_APPEND_FL` **set**, a syscall trace of a writer start that reaches **W18** shows, against the journal, seal and archive paths: **no** `O_TRUNC`, no write-mode open without `O_APPEND`, no `ftruncate`, no `unlink`, no `rename`, no `FS_IOC_SETFLAGS`. **W17 is the only write**, and it appends exactly one `startup` record: the journal afterwards is its prior bytes **plus that one record**, and the seal and every archived file are byte-for-byte unchanged |
| **R6-C — startup is non-destructive: the absent-flag branch, `+a` absent** | **`JNL-32b`** | with `FS_APPEND_FL` **cleared by root on a disposable generation**, the start **refuses at W9 with `SW-J06`, before W17 is reached**. The trace shows **no** write-mode open of the journal at all — with or without `O_APPEND` — **no W17, no W18, no journal opened for writing and no `startup` record**; and the journal, the seal and the archive are **byte-for-byte unchanged**. *Revision 6's `JNL-32` expected an appended `startup` record in this branch, which **W9** makes unreachable. The expectation is corrected, not defended* |
| **R5-B — the writer's seal access is exactly read** | **`JNL-33`** | as `freedomsheet`: `open(seal, O_RDONLY)` **succeeds**; `open(seal, O_WRONLY)` → `EPERM`; `unlink`/`rename` of the seal → `EACCES`; a create-and-rename replacement in `…/journal` → `EACCES`; `…/archive` is unreachable → `EACCES`; and the full V-W algorithm completes using only that read |
| **R5-A / R5-D — the falsification cases carried forward; `JNL-40` split by R8-D** | **`JNL-35 … 41`** | §2.13.5c rows **F-2 … F-8**, one test each: genesis, registered digests, predecessor close manifest, inode, deployment digest, host identity, probe report — each altered **independently**, each asserting the named code, and each refused at the boundary the matrix names **where the matrix names one**. `JNL-35` and `JNL-38` additionally assert the corrected minimum combinations of **revision 10** — **F-2 = `A1 + A2 + A10`**, constructed under identity **E2**, `freedomsheet`'s own uid with a complete ambient `CAP_LINUX_IMMUTABLE` set, which holds **A2 and A10 by owning the inode** and is asserted in the same test to receive **`EPERM`** from `FS_IOC_SETFLAGS` against the **root-owned seal**, because it holds no `A11`; **F-5 = `A1 + A10 + A3`**, so `unlink`/`rename` on the `+a` victim is asserted to return `EPERM` **before** the flag is cleared, **and** identity **E4** — every discretionary right, no `CAP_FOWNER` — is asserted to receive `EPERM` from the flag clear itself. *Revision 9 gave these as `A1 + A2` and `A1 + A3`, omitting the owner authorization in both.* **`JNL-40` carries two cases** and is stated separately below |
| **R6-B — the seal, split by attacker class** | **`JNL-34a`** | **F-1a.** Any byte of the **seal body** altered with the journal left alone: the writer refuses at **W13** (and **W5** where applicable) with `SW-J04`/`SW-J24`, **with no database reachable**, and the coordinator refuses at **C-b/C-d** |
| **R6-B — the case the writer does *not* refuse, asserted as such** | **`JNL-34b`** | **F-1b.** The seal body **and record 0** rewritten consistently, `+a` and `+i` cleared and restored by root: **V-W is asserted to complete without refusing** — the test asserts the limit rather than hiding it — and the **coordinator** then refuses at **C-b/C-d** against the registered digests with `J-16`/`J-17`. *This is the case that makes the narrowed F-1 falsifiable: if a future change made the writer refuse it, this test fails and the claim is re-widened deliberately* |
| **R6-B — `BND.genesis_record_digest` alone** | **`JNL-42`** | **F-9.** Only the recorded genesis digest is altered: **W5** refuses with `SW-J24`, before any append |
| **R6-B — `BND.journal_device` alone** | **`JNL-43`** | **F-10.** Only the recorded device is altered: **W7** refuses with `SW-J11` against `fstat` |
| **R6-B — `BND.journal_inode` alone** | **`JNL-44`** | **F-11.** Only the recorded inode is altered: **W7** refuses with `SW-J11` against `fstat` |
| **R6-B — a `sealed_at` field present in the binding** | **`JNL-45`** | **F-12.** A seal built to the **revision-6** binding layout, and separately a current seal with one field appended: **W3** refuses with `SW-J24` in both, because the binding is longer than `SB.binding_format_version` permits. **The same seal is asserted to have passed revision 6's V-W**, which is the regression this case exists to prevent |
| **R7-A — the construction order is executable; R8-A — its validations are against independent sources; R11-A — and the deployment is bound to a reviewed commit** | **`JNL-46`** — **nine cases** | *(a)* An **independent construction-order harness** walks Algorithm C **C0 … C13** in order against a disposable hierarchy and asserts **I-1 … I-5** of §2.13.5a row by row: every value exists when first consumed; every value is **final**, compared at consumption with its value at the end of the run; every **I-2** row is validated against a source that is not itself, at or before first consumption; every **I-3** row is checked before the first persistent artifact depends on it; and no **I-5** row is credited with a validation step. It asserts specifically that **C0 reads no probe result**, that **C1 is the only invocation of the probe stages and the only creation point of `PR`**, that **`probe_report_digest` is computed exactly once at C2**, and that **`deployment_manifest_digest()` returns identical bytes at its three call sites** — the deploy step, C0/C2, and the writer's W11 — for one tree. *(b)* **A malformed supplied digest** — not 64 lowercase hex — is refused at **C0**; the probe is asserted **never to have run**. *(c)* **A well-formed but wrong supplied digest**, naming no deployment on the host, is refused at **C0** by comparison with the computed `DD`; the probe is asserted never to have run. *This is the case revision 8 could not catch, because it consumed the value at C1 and compared it at C2 against the probe's copy of it.* *(d)* **A deployed file changed between C0 and C1** — a byte written into the writer's tree, or a drop-in added under `freedom-sheet-writer.service.d/`, after C0's comparison and before the probe's capture — is refused at **C2** by the second manifest computation. *(e)* **A report whose `writer_deployment_digest` differs from the validated `DD`**, injected into `PR` after C1, is refused at **C2**. **In (b) … (i) the run is asserted to refuse before C5 and to leave no journal file, no seal, no `current` symlink, no `.close` manifest and no row in `sheet_writer_journal_generations`.** *(f)* **New in revision 12: the provenance record `PVR` is absent** — deleted after a deployment, or never written because the deploy step's **D8** was suppressed. `init-generation` is asserted to refuse at **C0** with `J-26`, and **the probe is asserted never to have run**. *This is the omission case revision 11 had no refusal for.* *(g)* **`PVR.source_commit` names a commit `APR` does not** — refused at **C0**; and the mirror case, `APR` absent entirely, likewise refused. *(h)* **A byte is changed in a deployed region-S file after the deployment completed**, so `SM` no longer equals `TM` — refused at **C0** with the field named. *(i)* **A file belonging to neither region is added to the deployed root** — refused at **C0** by the closed partition, which a whole-tree digest comparison against itself could not have seen. **`JNL-46` also asserts that `deployed_source_manifest_digest()` returns identical bytes at its three call sites** — **D7**, **C0** and the writer's **W11a** — for one tree, exactly as it already asserts for `deployment_manifest_digest()` |
| **R7-A / R8-B — a refusal before C5 creates no generation artifact, and cleanup decides the rest** | **`JNL-47`** — **six cases** | **Four probe-stage injections with cleanup succeeding — §2.13.2b state S-A** — one each in Stage 1, Stage 2, Stage 3 and Stage 4: `init-generation` refuses at **C1** or **C2**, exits **non-zero with the S-A code** naming the failing case and its `errno`, and the disposable hierarchy is asserted to contain **no journal file, no seal, no `current` symlink, no `.close` manifest and no `…/probe` or `…/probe-ro` residue**, with **no row in `sheet_writer_journal_generations`**; a re-run is asserted to be admitted at C0. **Two cleanup-failure injections with deterministic residue — state S-B**: one after a probe-stage failure and one after a **fully passing** probe, each planting an artifact the `finally` cannot remove. Both assert the **S-B exit code**, distinct from S-A; **the residue reported by absolute path with its failed operation and `errno`, and no other path named**; **no journal file, no seal, no symlink, no `.close` manifest and no database row**; **the residue still present and byte-for-byte unchanged** after the run; **the next `init-generation` refused at C0** and the next `verify-capability` refused at its own precondition, **neither cleaning it**; and **the documented operator recovery clearing it, after which a re-run is admitted**. *Revision 8's single cleanup case asserted no residue, which `JNL-48(d)` simultaneously required to be present* |
| **R7-B — the S4-2 target's positive control, its lifecycle, and its four distinguishable outcomes** | **`JNL-48`** | **Four cases.** *(a)* **S4-0** succeeds on the exact `…/probe-ro/s4-2.target` under `verify-capability`'s own `setpriv --reuid=freedomsheet --regid=freedomsheet --clear-groups` drop, outside any unit: open, append, `fsync`, `rename` and back, and `unlink` on the identically created sibling. **Revision 11 states explicitly that this drop is *not* identity `E1`** (§2.13.2a): it requests no securebit and no capability option, is valid as written under util-linux 2.39.3, and retains the launching process's bounding set — more latent authority than E1, never less, and immaterial here because every S4-0 case is a positive control expected to succeed with an empty permitted set against a target carrying no file capability. *(b)* With the target deliberately mis-provisioned — `root:root 0600` — the sandboxed append returns **`EACCES`**, and the stage is asserted to record **`inconclusive`**, never `passed`, and `verify-capability` exits non-zero. *(c)* With the target correctly provisioned and S4-0 passing, the sandboxed append returns **`EROFS`** and only then is Stage 4 a pass; a sandboxed append that **succeeds** is asserted to be a **failed** stage. *(d)* A planted cleanup failure — an artifact in `…/probe-ro` made undeletable — is asserted to reach §2.13.2b state **S-B**: a non-zero exit with the **S-B code**, **the residue named by absolute path** with its failed operation and `errno`, **the residue still present** afterwards, **no generation or database artifact**, `init-generation` and `verify-capability` both refusing at their preconditions **without cleaning it**, and the documented operator recovery clearing it so a re-run is admitted. *Revision 8 required this residue to remain while `JNL-47` required a cleanup failure to leave none; §2.13.2b removes the contradiction and both tests now assert the same state* |
| **R7-C / R8-C / R8-D / R9-A / R9-C — one case per feasible authority combination not already covered, and the residuals** | **`JNL-49`** — **twelve cases** | **Against §2.13.5c's eleven-authority register, and every case is executed under one of the named identities `E1 … E8`, whose effective UID, GID, supplementary groups and complete permitted, effective, inheritable, ambient and bounding capability sets are asserted from `/proc/self/status` — and whose **securebits** are asserted from `prctl(PR_GET_SECUREBITS)`, which `/proc/self/status` does not report — *before* the operation under test runs.** A case whose identity assertion fails is **`inconclusive`**, never a pass. **Corrected in revision 11 (R10-A/R10-B):** the identities are constructed by the seven-step **`capsh(1)`** procedure of §2.13.5c, not by revision 10's `setpriv --securebits=+keep_caps,…` recipes, which util-linux 2.39.3 rejects and which declared bounding sets they did not produce. **No case is added, removed or renumbered by that correction.** *(1)* **A1 + A11 + A4** against the archive, under **E6**: `FS_IOC_SETFLAGS` clearing `FS_IMMUTABLE_FL` succeeds, an archived file is altered, `+i` is restored → `archive-verify` fails and a successor registration is refused. *Revision 9 gave this as `A1 + A4`, which is not constructible: the file is root-owned.* *(2)* **A5 without flag or seal authority**, under **E4**: the deployed writer's files changed, the seal untouched → **W11** `SW-J22` and **W4** `SW-J25`; and **E4 is asserted to receive `EPERM` from `FS_IOC_SETFLAGS` on the seal**, so the case proves the alteration was confined to the deployment path. *(3)* **A6 — retained from revision 9**: the tree restored onto a second host whose `/etc/machine-id` has been **rewritten to match**, with the journal's device and inode **preserved** → **W10 is asserted to pass**, **C-d is asserted not to refuse on `host_machine_id`**, and the case asserts that **no check in this design refuses the restored tree at all**. It additionally asserts the operational evidence that does remain: the restored tree carries **no production database**, and a forged head has no `seal` record, no `.close` manifest and no archive. This is **R-5.0-13**. *(4)* **A8 without any disk authority**, under **E8**: a generation row inserted for a journal the coordinator did not create → **V-R** refuses because the seal does not derive its own genesis, and the partial unique index refuses a second unsuperseded head. *(5)* **A1 + A2 + A10 without A3 or A11**, under **E2**: a mid-chain record rewritten in place → **W14** `SW-J09`. *(6)* **A1 + A2 + A3 + A10 + A11 + A8**, under **E6** plus the coordinator: a wholly forged self-consistent generation **inserted** → admitted by the trigger but visible as a head with no `seal` record, no `.close` manifest and no archive, and refused by the predecessor foreign key. *(7)* **A1 + A2 + A3 + A10 + A11 + A9**: asserted **not refused** by any check in this design — the test asserts the limit rather than hiding it — and asserts that `sudo log_output`, journald and `audit_events` still carry the acts, which is **R-5.0-12** and not a refusal. *(8)* **A1 + A11 + A4 + A3** against a `.close` manifest: both disk copies agree and the **registered** `predecessor_close_digest` still disagrees → `J-16`. *(9)* **F-5's corrected minimum, in three steps.** With **A3 alone** (**E4** without its flag capability), `unlink` and `rename` over the journal are asserted to return **`EPERM`**, because the victim carries `FS_APPEND_FL`. With **A1 + A3 and no A10** (**E4**), `FS_IOC_SETFLAGS` clearing `FS_APPEND_FL` is asserted to return **`EPERM`** — the caller neither owns the `freedomsheet`-owned inode nor holds `CAP_FOWNER`. Only with **A1 + A10 + A3** (**E6**) does the clear succeed, the replacement succeed, and the writer refuse at **W7** `SW-J11`. *Revision 9 stated this row as `A1 + A3` and its second step was not executable.* *(10)* **F-2's corrected minimum**, under **E2**: the alteration is constructed **as `freedomsheet`**, with a complete ambient `CAP_LINUX_IMMUTABLE` set and no other privilege, proving that **the writer's own ownership supplies both `A2` and `A10`** and that the empty `CapabilityBoundingSet=` is what actually refuses it in production → **W13** `SW-J04`; and the same identity is asserted to receive **`EPERM`** against the root-owned seal, which is the executed form of F-2's detector separation. *(11)* **new in revision 10 — the owner-authorization boundary, isolated with its positive control.** On one disposable root-owned `+i` file, with every discretionary prerequisite satisfied: **E4** opens it `O_RDONLY` **successfully** and `FS_IOC_SETFLAGS` clearing `FS_IMMUTABLE_FL` returns **`EPERM`**; **E6**, which differs from E4 only by holding `CAP_FOWNER`, issues the identical call and **succeeds**. The pair proves the refusal is the **owner check** and not DAC, path search or the flag capability — **control form C-I** (§2.13.5c), E4 and E6 differing in one option and no other. The same **E4/E6** pair is run against a disposable `freedomsheet`-owned `+a` file against `FS_APPEND_FL`. **Corrected in revision 11**: revision 10 gave **E2** as the positive control for that second half, and E2 differs from E4 in uid, supplementary groups and two capabilities, so it isolates nothing. **E2 is retained as a corroborating control** on that file — the same check satisfied by *ownership* rather than by `CAP_FOWNER` — and is asserted as corroborating rather than isolating. *(12)* **new in revision 10 — flag authority without discretionary access, made constructible.** Under **E5** (`CAP_LINUX_IMMUTABLE` + `CAP_FOWNER`, in `freedomcoord` for traverse and read), `FS_IOC_SETFLAGS` clearing `FS_IMMUTABLE_FL` on an archived file **succeeds**, and the subsequent `open(O_WRONLY)` is asserted to return **`EACCES`**, because the file is `0440 root:freedomcoord`. **This is the executed proof that A1 and A11 confer no DAC.** *Revision 9 asserted this outcome for a `CAP_LINUX_IMMUTABLE`-only identity, which cannot reach the open because the clear itself returns `EPERM`; the case is corrected rather than removed.* |
| **R7-C / R8-C / R9-A — the pairings that are not constructible, asserted rather than assumed** | **`JNL-50`** — **twelve cases** | One per row of §2.13.5c's not-constructible table, each executed under a named identity from `E1 … E8` with its full capability set asserted first, and each asserting the named syscall, result and `errno`. *(1)* **E1** vs the seal: `open(seal, O_WRONLY)` → **`EPERM`** while `+i` is set — immutability is checked before DAC — and **`EACCES`** on a disposable copy without `+i`, which is the sub-assertion that proves the **mode** rather than the flag. *(2)* **E1** vs `…/journal`: `creat`, `unlink` and `rename` → **`EACCES`**. *(3)* **E1** vs **A1** on its **own** journal file: `FS_IOC_SETFLAGS` clearing `FS_APPEND_FL` → **`EPERM`**. **This is the clean isolation of A1**: E1 owns the inode, so `A10` is satisfied by ownership and the capability is the only missing prerequisite; the positive control is **E2**, which differs only by holding `CAP_LINUX_IMMUTABLE` and **succeeds** on a disposable generation. *(4)* **E2** vs **A11** on the **root-owned seal**: `FS_IOC_SETFLAGS` → **`EPERM`**, with the capability held and the owner authorization absent. **This case is what makes F-2's detector separation executable**, and revision 9 contained nothing equivalent. **Its control is form C-II** (§2.13.5c) and is **added in revision 11**, because no identity in the table differs from E2 by `CAP_FOWNER` alone: the identity is held fixed and the **inode's owner** is varied, E2 receiving `EPERM` on the root-owned seal and **succeeding** on a `freedomsheet`-owned `+i` file the root harness created identically beside it, same directory, same mode, same mount. *(5)* **E1** vs the archive: `open` → **`EACCES`** at the directory, before any file is reached. *(6)* **E4** — `CAP_LINUX_IMMUTABLE`, `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, **no `CAP_FOWNER`** — vs **A11** on a root-owned archive file: traverse and `open(O_RDONLY)` **succeed**, and `FS_IOC_SETFLAGS` → **`EPERM`**. Positive control **E6**. **This is the isolating control remediation R9-A requires**, and it is the case that proves the refusal is the owner check rather than an unrelated DAC or path-search denial. *(7)* **E4** vs **A10** on the `freedomsheet`-owned journal file: the same shape against `FS_APPEND_FL` → **`EPERM`**; **isolating positive control `E6`** (control form **C-I**, differing by `CAP_FOWNER` alone), with **E2** retained as a **corroborating** control by the ownership route. *Revision 10 named E2 as the isolating control; it differs from E4 in uid, groups and two capabilities and is corrected here.* *(8)* **E5** vs **A3**: `creat`, `unlink` and `rename` inside `…/journal` → **`EACCES`**; clearing a flag changes no directory permission. *(9)* **E8** `freedomcoord` vs **A2**/**A3**: no write bit on `…/journal` or the `0440` seal, and neither `CAP_LINUX_IMMUTABLE` nor `CAP_FOWNER` → `EACCES` on the directory and `EPERM` on the seal open. *(10)* **E8** vs **A4** archive **write**: traverse and read **succeed**, and `open(O_WRONLY)` → **`EPERM`** while `+i` is set and **`EACCES`** on a disposable copy without it. *(11)* `discordbot`, `freedomweb` and `foundry` against `…/journal` itself → **`EACCES`** at the directory; and **E1** asserted to open **no database connection at all** and to hold no role, so there is nothing to authenticate as (**A8**/**A9**), together with `freedomcoord`'s `UPDATE`/`DELETE` on the generation table refused by `reject_history_mutation` and the revoked grants. *(12)* **`freedomsheet`'s hold on `A2` and `A10` is asserted positively rather than denied**: with `FS_APPEND_FL` cleared by root on a disposable generation, a non-append write by **E1** **succeeds**; and **E2** clears the flag itself and then writes, proving that the writer needs no privilege it does not already own **once the capability is present** — which is why the empty `CapabilityBoundingSet=` and `NoNewPrivileges=true` are the controls and the file mode is not. **Every negative flag case in this identifier is executed with all other prerequisites satisfied and carries a positive control that succeeds**, so no refusal here is attributable to an unrelated DAC or path-search denial. **Revision 11 states which control form each uses** — **C-I**, varying one capability and nothing else (cases 3, 6 and 7, the pairs `E1 → E2` and `E4 → E6`), or **C-II**, holding the identity fixed and varying the inode's owner (case 4) — **and corrects case 7's isolating control from `E2` to `E6`**, `E2` being retained as a corroborating control by the ownership route. Every identity in this identifier is constructed by the seven-step `capsh(1)` procedure of §2.13.5c and asserts its securebits as well as its five capability masks. *Revision 9's cases 9 and 10 asserted a successful `+i` clear by a `CAP_LINUX_IMMUTABLE`-only non-root identity; that is not constructible and both were replaced in revision 10.* |
| **R8-D — a forged matching host identity is a residual, and the test says so** | **`JNL-40`** — **two cases** | *(a)* **Unforged.** The tree is presented on a host whose `/etc/machine-id` differs from `SB.host_machine_id`: the writer refuses at **W10** with `SW-J23` **before W17**, and the coordinator refuses at **C-d** with `J-16`. *(b)* **Forged to match.** `/etc/machine-id` on the second host is rewritten to the recorded value and the journal's device and inode are preserved: **W10 is asserted to pass**, **C-d is asserted to pass on `host_machine_id`**, and the case asserts that **no step in V-W or V-C refuses the tree on host-identity grounds**. Where the harness cannot preserve device and inode, the case asserts that the refusal that does occur is **`SW-J11` at W7 on `journal_inode`/`journal_device`** and **names that field**, so no test claims a host-identity detection it did not make. *Revision 8's `JNL-40` asserted a single refusal and revision 8's `JNL-49` case 3 asserted a C-d refusal; both are corrected, and this case is the standing record of **R-5.0-13*** |
| **R11-A — the deployment is bound to an immutable reviewed Git object, and omitting the binding refuses** | **`JNL-51`** — **eight cases** | *(a)* An **ordered walk of Algorithm D**, `D0 … D8`, against a disposable object store, a disposable approval record and a disposable deployment root: every value is asserted to exist and be final when first consumed, the trusted manifest is asserted to be computed **from Git object bytes** and not from any file in a worktree, and the provenance record is asserted to be written **last** and **outside** the deployed root. *(b)* **`APR` absent** — the deploy refuses at **D0** with `DEP-01`; nothing is staged, nothing is installed, and the predecessor deployment is asserted byte-for-byte unchanged. *(c)* **The approved commit is not in the store** — refused at **D1** with `DEP-02`. The case also asserts that **a ref, branch or tag pointing at a different commit changes nothing**, because no step resolves one. *(d)* **A tree whose extracted content does not reproduce `APR.source_manifest_digest`** — refused at **D3** with `DEP-04`. **This is the case that does not rest on SHA-1**, and it is asserted as such. *(e)* **A region-D distribution whose artifact digest is not the lock's**, plus an extra distribution and a missing one — each refused at **D4** with `DEP-05`. *(f)* **An unaccounted file in the staging tree** — refused at **D5** with `DEP-06`; and the same file added *after* installation is refused at **D7** with `DEP-08`, the deployment then being **rolled back to its predecessor**, which the case asserts. *(g)* **The negative test P5.0-SR1 requires: the provenance step is omitted.** `D8` is suppressed, or `PVR` is deleted after a successful deployment. `init-generation` is then asserted to **refuse at C0** with `J-26`, to leave **no journal file, no seal, no `current` symlink, no `.close` manifest and no row**, and the probe is asserted **never to have run** — so **activation cannot succeed**. The case separately assembles a syntactically valid `PVR` and `APR` naming a commit with **no** `approved_source_revisions` row, drives `init-generation` and `seal` to completion, and asserts that **`V-R` refuses with `J-28`** and that the `NOT NULL` foreign key refuses the same insert **issued directly as SQL**, under the coordinator role and under the schema owner. *(h)* **A syscall trace of a complete deployment asserts that no path under `/opt/freedom-blades/platform` is opened** — the group-writable worktree of **H-1** is not an input to any deployment |
| **R11-B — the membership table is canonical, and every identity's access matches it** | **`JNL-52`** — **eight cases** | **Every case first asserts the canonical table itself**: `getent group` for `freedomjournal`, `freedomcoord`, `freedomsheet`, `discordbot`, `sudo` and `fbprobe` lists **exactly** the members §2.12.2 records, and **an unexpected member fails the case** rather than being noted. Then, per identity, a positive set and a negative set, each with `id`, `namei -l` and `open`, because a denial whose cause could be a path search is not evidence of a permission. *(1)* **`freedomsheet`, positive** — `id` reports its uid, its primary gid and **`freedomjournal` and nothing else**; `namei -l` on `…/journal/__GEN__.seal` resolves every component; `open(seal, O_RDONLY)` and `open(journal, O_RDONLY)` **succeed**, and the full **V-W** algorithm completes. *(2)* **`freedomsheet`, negative** — `open(seal, O_WRONLY)` → `EPERM`; create, unlink or rename inside `…/journal` → `EACCES`; `namei -l` on `…/archive` shows the search denied and `open` → `EACCES`; `id` shows **no** membership of `freedomcoord`. *(3)* **`freedomcoord`, positive** — `id` reports `freedomcoord` **and `freedomjournal`**, matching evidence identity **E8**; `namei -l` resolves both the seal and an archived file; `open(seal, O_RDONLY)`, `open(journal, O_RDONLY)` and `open(archive/*, O_RDONLY)` **succeed**. *(4)* **`freedomcoord`, negative** — `open(seal, O_WRONLY)` → `EACCES`; `open(journal, O_WRONLY\|O_APPEND)` → `EACCES`, the journal file's group bits being `r--`; create inside `…/journal` or `…/archive` → `EACCES`. **The coordinator holds no write bit anywhere in the hierarchy**, which is claim 3 of §2.12.2. *(5)* **`discordbot`, positive control** — it traverses `/var/lib` and `stat`s `/var/lib/freedom-sheet-writer` successfully, so the denials in case 6 are attributable to `…/journal`'s mode and not to a parent. *(6)* **`discordbot`, negative** — `id` shows **no `freedomjournal`**; `namei -l` names `…/journal` as the component where the search is denied; `open(seal)` and every `…/archive` path → `EACCES`. *(7)* **`freedomweb`, positive control** — the same traverse-to-parent success, **plus** a successful write in the repository worktree, which proves its `discordbot` membership is real and therefore that case 8's denials are not an artefact of a broken identity. *(8)* **`freedomweb`, negative** — identical denials at `…/journal` and `…/archive`; `id` shows `freedomweb` and `discordbot` and **no `freedomjournal`**. **Cases 5–8 together are check `C-4`**, which §8.1 records as not run and which this evidence discharges once A-5.0-5 is authorized |
| **R11-A — the three new fail-closed conditions refuse on both sides** | **`JNL-53`** — **six cases** | One case per condition per actor, on the `JNL-04 … 12` precedent. **`J-26`, writer** — `PVR` deleted, then chmod'ed `0644`, then chowned away from root, then corrupted, then edited to name a different commit: the writer refuses at **W11a** with `SW-J26` in each, **appends no `startup` record**, and dispatches nothing, asserted by syscall trace. **`J-26`, coordinator** — the same five mutations at `observe`: **C-a** refuses and **no evidence row is written**. **`J-27`, writer** — one byte changed in a deployed region-S file, and separately a file added to the deployed root belonging to neither region: `SW-J27` at **W11a**, before **W17**. **`J-27`, coordinator** — the same, refused at **C-a**, and refused again at **C-d** against the registered `source_manifest_digest`. **`J-28`, coordinator** — registration attempted for a generation whose seal names an unapproved revision: `V-R` refuses, and the direct `INSERT` is refused by the `NOT NULL` foreign key under **both** the coordinator role and the schema owner. **`J-28`, activation** — with no registered generation, `dispatch_journal_clear` is not recorded and the activation trigger refuses, asserted against real PostgreSQL rather than through the service. **Every case asserts that the Sheets client was not called** |

**Synthetic and disposable artifacts only.** Every one of these runs against a
harness writer, a disposable generation under a path the test creates and removes,
and the disposable `freedom_test` database. **No live Google Sheet, credential,
production database or production service is touched**, and no test writes to the
production journal hierarchy, which does not exist.

#### 2.13.8a What PostgreSQL enforces, and what it merely records. **New in revision 6; this is remediation R5-D**

Revision 5 said that `CHECK (append_only_verified)` made the probe *"enforced by a
constraint rather than by a procedure step somebody could skip"*. **That is
false, and it is withdrawn rather than defended.** A `CHECK` on a Boolean column
constrains a **supplied value** to `true`. It proves that the row's author
supplied `true`. It cannot observe a host, cannot know whether `verify-capability`
ran, and cannot distinguish a probe that passed from a coordinator that typed the
word.

> **Withdrawn.** *"A generation whose capability probe did not pass cannot be
> registered, so the probe is enforced by a constraint rather than by a procedure
> step somebody could skip"* — §2.13.2 and logical schema §3.7, revision 5. The
> **column** `append_only_verified` is withdrawn with it.

**What replaces it.** Three columns that carry an *attestation bound to a
re-derivable artifact*, rather than a Boolean that carries nothing:
`append_only_probe_version` (a closed vocabulary), `append_only_probe_digest`
(SHA-256 of the canonical probe report) and `append_only_probe_at`. The probe
report itself lives **inside the seal body**, so it is covered by
`seal_body_digest`, anchored by the genesis record's `prev_hash`, sealed under
`chattr +i`, and re-derivable by anyone who can read the seal — including the
writer (**W4**) and the coordinator (**C-d**).

**And the digest covers what it is said to cover — corrected in revision 7.**
Revision 6 described `append_only_probe_digest` as covering the probe's four
stages while Algorithm C built the report from three, because Stage 4 ran later
at deployment. §2.13.2a moves Stage 4 **before** the report is built, so the
sentence above is now true by construction rather than by wording. **`JNL-29`
asserts it**: the report is checked to contain all four stages and the digest to
be computed over exactly those bytes. This is the correction R6-A required, and
it is a change to the artifact rather than to the claim about it.

**The authenticated actor, and the immutable fields.** The row is inserted only
by `RegisterJournalGeneration`, connecting as `freedom_migration_coordinator`,
authenticated by PostgreSQL's `peer` method as the dedicated `freedomcoord`
operating-system identity, reached only through the `sudo` wrapper (§2.12,
logical schema §4.3). The row names `registered_by_platform_account_id`, resolved
at execution. Once inserted it is immutable: `UPDATE`, `DELETE` and `TRUNCATE`
are revoked from every principal **and** refused by `reject_history_mutation`,
including for the schema owner. The same act writes an `idempotency_keys` receipt
and an `audit_events` row in the same transaction, and `sudo`'s `log_output` and
journald record the invocation independently.

**Binding to the exact generation, filesystem and probe version.** The probe
report names the probe version, the filesystem type and the `st_dev` Stage 3
tested; `init-generation` refuses unless the journal file it creates has that same
`st_dev` (step **C6**); the report is then inside that generation's seal body,
which is inside that generation's genesis anchor. So a probe report cannot be
moved to another generation, another filesystem or another probe version without
breaking a digest that three different readers recompute.

**The honest division of labour.**

| | PostgreSQL **enforces** | PostgreSQL **merely records** |
|---|---|---|
| Shape | lowercase-hex digests, non-blank text, closed vocabularies for `filesystem_type`, `fenced_writer` and `append_only_probe_version` | that the values describe the files that exist on disk **now** |
| Structure | one linear chain: unique `generation_seq`, unique predecessor, one first generation per writer, `seq = predecessor_seq + 1`, composite FK to the predecessor, one registration per `(device, inode)`, all-or-nothing predecessor triple | that the predecessor was genuinely sealed on disk — the `.close` digest is compared by **V-R** on the host, and the constraint only enforces that a value was supplied |
| History | append-only, against every principal including the schema owner | — |
| Authority | that the inserting principal is the coordinator, authenticated by peer as `freedomcoord`, and names a real `platform_accounts` row | that the human behind that account ran the probe honestly |
| Fencing | that a `dispatch_journal_clear` evidence row names the **current head** and predates no later registration (§3.4 condition 5) | — |
| The probe | **nothing about whether it ran.** It enforces that a well-formed digest, a supported version and a timestamp were supplied | that `verify-capability` produced this report at this time — an attestation whose falsity is **detectable**, because the report is inside the `+i` seal and every reader recomputes its digest |
| The systemd sandbox (**new in revision 7**) | **nothing whatever.** No column names a directive, a unit or a mount | that Stage 4's `S4-0 … S4-3` observed the deployed unit's directives at provisioning, with `S4-0` proving the target writable outside the sandbox first. It is inside the same report, under the same digest. *Amended 2026-09-23 under C-P5.0-R5-R3, pending review:* it is invalidated under **two conditions**, matching §2.13.2a's Option-1 table — (1) a change of **deployed bytes** invalidates through **J-22**/**F-6** and requires a rotation; (2) a change of **systemd or package identity** invalidates the S4-3 attestation at **W4**/**C-a** under **J-25** and requires a fresh `verify-capability`, which is a rotation. The second is a further refusal cause of the existing `SW-J25`/`J-25`, not a new rule family: it needs no column, no second evidence artifact, no second digest authority and no new refusal-code family. Its availability cost extends **R-5.0-11** and **R-5.0-16** and remains pending review and maintainer disposition. *(Revision 7 said "invalidated by the same rule — a redeployment forces a rotation"; that single-rule statement is superseded.)* |

**Why this is stronger than the withdrawn `CHECK`, and why it is still not a
proof.** It is stronger because a false attestation is now *detectable* rather
than merely unprovable: `JNL-41` alters the probe report and both the writer and
the coordinator refuse. It is not a proof because **no database constraint can
observe a host**, and the design no longer says one does. What actually
establishes that the probe ran is the on-disk seal, the `sudo log_output`
transcript, the journald entry, the `audit_events` row and `archive-verify` — four
records, three of them outside PostgreSQL, and the operations document names all
of them.

**The writer remains free of PostgreSQL.** None of this gives the writer a
database dependency: it validates the probe report from the seal it can read
(**W4**), and the database comparison is the coordinator's alone (**C-d**).

#### 2.13.9 What journal completeness is trusted to establish — and the sentence that is withdrawn

The handoff requires this stated exactly, and requires the contradiction removed.
**The contradiction is removed by withdrawing the false statement, not the
control.**

> **Withdrawn.** Revision 4 said, in §2.10.3 W-2 and logical schema §2.4:
> *"nothing in the fence depends on the journal being complete"*. **That is false**
> while `dispatch_journal_clear` is one of the five required fence methods, and it
> is withdrawn rather than defended.

**What completeness is trusted to establish, exactly.** *For a writer that
executed its own dispatch path, the set of requests dispatched without a recorded
outcome is the set the coordinator enumerates.* It is trusted against crash,
`SIGKILL`, power loss, reboot, unclean shutdown, disk-full, `fsync` failure,
partial writes and defects elsewhere in the writer — because each of those is a
row in §2.13.6 that refuses rather than under-reports. It is **not** trusted
against a writer whose dispatch path has itself been replaced.

**The one direction in which activation depends on it.**

| | Statement |
|---|---|
| The journal **can refuse** an activation the other four methods would permit | when the unresolved set is non-empty (**J-20**) or any journal state is unknown (**J-01 … J-19, J-21 … J-25**) |
| The journal **can never permit** an activation the other four would refuse | all five methods are required, so a clear journal is **necessary and not sufficient**. There is no path by which a journal makes a cutover possible that termination, an empty cgroup, a clear host scan and a revoked ACL would not |
| Therefore an **incomplete** journal **removes a refusal that should have occurred** | it never manufactures a permission. That is the direction in which the design is weakened, and it is bounded by durable storage, the directory permissions, the append-only attribute, the hash chain, the sequence, the generation seal, the registered generation and the fail-closed treatment of every unknown state |
| What remains outside all of that | **a writer whose dispatch path was replaced can call Google without journalling at all.** No record it authors can bound that. **R-5.0-10, new in revision 5** |
| What bounds *that* | not the journal. The writer is dead, its cgroup is empty, a host scan found nothing, and Google refuses its access — the four methods the writer does not author. And a writer compromised deeply enough to bypass its own journal could have written the Sheet arbitrarily long before the fence, which is a condition no fence was ever going to repair |

**The alternative the handoff permits, and why it is not taken.** The handoff
allows redesigning activation so the statements are consistent — that is, dropping
`dispatch_journal_clear` from the required set and deleting the journal. It is
rejected, and the reason is worth stating so a reviewer can disagree with it:
**the journal is the only control that refuses a cutover when a request is *known*
to be outstanding.** Without it, the case P5.0-R1 is actually about — the writer
was killed mid-request — produces four clear observations and a permitted
activation. Removing the control to remove the contradiction would trade an
inaccurate sentence for a worse fence. It is offered as **D5.0-13 / OD-66 option
C** so the choice is Peter's rather than the implementer's.

#### 2.13.10 What none of this does for the Google residual

Stated separately, and deliberately at the end, because the failure mode this
whole section exists to prevent is a durable journal being *mistaken* for the
barrier §2.10.2 says does not exist.

- **§2.10.2's conclusion is unchanged.** No accepted-request completion barrier
  exists in the published Sheets v4 / Drive v3 surface. Thirteen candidates were
  searched and the search stands.
- **A durable journal is not a fourteenth candidate.** It records what *this
  client* did. It observes nothing about what Google has applied, and durability,
  a generation, a seal, an acyclic construction, a hash chain, an inode check, a
  probe report and an immutable archive are all properties of *our* record, not of
  Google's state.
- **R-5.0-8 is not narrowed by one case**, and revision 6 narrows it by none
  either. A request Google accepted, whose response never reached the writer, and
  which Google applies after the final import, is exactly as unprevented and
  exactly as unprovable as it was in revision 4. What has changed is that the
  *enumeration* of such requests is now trustworthy across a reboot, so the
  operator adjudicates a set that is real rather than one a `tmpfs` may have
  emptied.
- **Stop condition 10b is extended** to name the journal's durability, its
  generation, its seal, its acyclic construction and its archive as things that
  must never be described as a barrier for I-SHEET-COMPLETE.

#### 2.13.11 The option comparison this section is choosing between

| | Option | What it gives | Cost | Verdict |
|---|---|---|---|---|
| **J-1** | **The full contract above** — durable root-owned hierarchy, an **acyclic** sealed generation registered in PostgreSQL, a **writer-readable** seal whose every binding field V-W authenticates, a **four-stage attributable and non-destructive** capability probe whose four stages all run **before** the report is sealed, hash chain, twenty-five fail-closed states, privileged lifecycle | Every unknown state refuses. A reset cannot look empty. The writer cannot erase what it authored. The enumeration survives a reboot. The construction can actually be built, and every claim in it is falsifiable | a sixth table, a fifth command, a second privileged tool and `sudoers` entry, a root-owned state hierarchy, a transient writer-writable probe arena, a seal the writer can read, and **N5.0-21's refusal cost** — a full or failing filesystem stops Sheet mutations (**R-5.0-11**) | **Recommended.** It is what the handoff asks for. **Revision 6 changes its content in four ways** — the acyclic construction, the readable seal, the safe probe and the withdrawn `CHECK` — so OD-66 option A is re-stated rather than carried forward unread |
| **J-2** | **Durable storage and the seal, without PostgreSQL registration** | Most of the integrity, and no sixth table | the activation trigger cannot refuse stale or cross-generation evidence, so that check exists **only** in the coordinator command — which §3.4 of the schema already argues is not sufficient on its own, for exactly the reason it gave for duplicating the fence test in the database. **Revision 6 made this option slightly less bad and still not good, and revision 7 makes it worse again**: the writer's own **V-W** refuses a wrong deployment, a wrong host and a broken seal from disk alone — but only against an attacker who lacks §2.13.5c's **`A1`**, and nothing then refuses *stale* evidence about a superseded journal **or an `A1 + A2 + A3` self-consistent rewrite of the seal and record 0 (F-1b), which only the registered row refuses**. Dropping the registration drops the only artifact that covers it | **Weaker, and inconsistent with a decision this package already made.** Listed so it is rejected rather than ignored |
| **J-3** | **Drop `dispatch_journal_clear` and the journal** | The contradiction disappears; four fence methods remain; no sixth table, no second tool, no `R-5.0-11` | nothing refuses a cutover when a request is known outstanding; W-2, W-3 and two of the six achievable guarantees are withdrawn; the residual grows from *"a lost response"* to *"a lost response or a killed request"* | **Not recommended**, and it is the honest alternative to the contradiction |
| **J-4** | **Keep revision 4's `/run` journal** | — | a reboot silently reports a clean set | **This is the P5.0-R5 finding.** Listed for completeness |

**Owner: Operations Owner and Data Owner, on the Security Reviewer's review.
Required by: before WP-4b and WP-15.** Raised as **D5.0-13 / OD-66** (§5.3), whose
option A is **re-stated in revision 6** because its content changed.

---

## 3. Work breakdown

Reviewable work packages. Every one names the evidence that closes it; none is
closed by "the code is written". **Numbering is preserved from revisions 1 and 2**
so that existing cross-references stay valid; WP-5 remains withdrawn.

| WP | Work | Closes when |
|---|---|---|
| **WP-0** | This readiness package and the logical schema artifact, including remediations R1, R2, R3, R4 and **R5** | Peter records a readiness decision and the independent schema review recommends acceptance with P5.0-R1, P5.0-R4 and P5.0-R5 closed; P5.0-R2 remains closed. **R4 does not claim any of them closed, and for R1's Sheet half it returns a decision instead of a fence** |
| **WP-1** | The migration-and-cutover **contract** (deliverable 9): preview/apply, the fence protocol, the rollback data path, reconciliation, control totals, the comparison-telemetry contract (§11), the verification-window template, the numeric register | the contract states every threshold as a number and every convention with the package that first implements it. **Blocked by D5.0-10** |
| **WP-2** | Migration `0014` + **two** sequences + grants + coordinator role + **five** append-only triggers *(four before revision 12)* + the activation-fence trigger + the evidence-recording trigger + the authority-fence trigger function + seed derived from the manifest. The `fence_method` vocabulary carries **five** values, including `dispatch_journal_clear`; **revision 5 adds the sixth table `sheet_writer_journal_generations`, the three journal columns on the evidence table, and the activation trigger's fifth condition; revision 6 withdraws `append_only_verified` and its `CHECK` and adds `seal_body_digest`, `append_only_probe_version`, `append_only_probe_digest` and `append_only_probe_at`; revision 12 adds the seventh table `approved_source_revisions` with its append-only trigger and grants, and four columns on the generation table including a `NOT NULL` foreign key** | empty-database apply, upgrade-over-fixtures, round trip, downgrade refusal, restored-backup rerun, seed idempotence, four equal control totals, **and the generation chain's constraints exercised by direct statement**, with §2.13.8a's enforce-versus-record division asserted case by case; **and the `NOT NULL` foreign key to `approved_source_revisions` proved to refuse an unprovenanced generation under the coordinator role *and* under the schema owner** (`JNL-51` case (g), `JNL-53`). **Blocked by D5.0-11 and D5.0-13** |
| **WP-3** | `domain/migration_authority.py` and `application/migration_authority.py` — states, transitions, epochs, dispositions, evidence, **the journal-generation value object and chain arithmetic**, repository protocols, the **five** commands | unit and application tests, plus the PostgreSQL evidence in WP-8 |
| **WP-4** | **The database authority fence and the startup refusal** — the trigger function installed on 5.0's own tables and one synthetic migrating unit; the startup authority read and capability refusal in bot, web and worker; identified refusal codes; the additive typed bot settings boundary | a write to a unit not at `cutover`/`database` is refused *inside its transaction*, proved with a held transaction across an activation; each process refuses to start when it cannot serve a unit's authority, each with its documented code |
| **WP-4b** | **The separately terminable Sheet writer** — the `freedom-sheet-writer` unit template **with the §2.13.3 hardening directives** and its own OS identity, the writer process, the IPC boundary, the bot-side client, the failure semantics, the two call-site migrations in `models/actor.py` and `models/trade.py`, the explicit per-request timeout on the Sheets client (N5.0-19), the `SIGTERM` drain (N5.0-17), and — **rewritten in revision 5** — the **durable journal client**: **Algorithm V-W** of §2.13.5b — seal read and structural verification, the **derived** genesis comparison, inode, ownership, mode, `FS_APPEND_FL`, host identity, deployment digest and probe-report checks, the chain walk, and the single appended `startup` record — plus the hash-chained record writer, the free-space precondition (N5.0-21), and the **twenty-eight** typed refusal codes `SW-J01 … SW-J28` — the last three being **W11a**'s reviewed-source provenance checks, new in revision 12. **Revision 7 changes what V-W parses, not how many steps it has**: the binding section is read at the `binding_format_version` the chain-authenticated body declares, carries exactly three fields, and every one of them is recomputed or compared (§2.13.5b) | the two call sites behave identically to today under characterization tests; a drain is proved to complete outstanding calls and record their outcomes; stopping the unit is proved to terminate a `SIGSTOP`ped writer; a journal entry is proved to exist *before* dispatch, including under `SIGKILL` between the `fsync` and the dispatch; **every row of §2.13.6 is proved to refuse, with its named code**; **a syscall trace shows no destructive operation against the journal, seal or archive in either branch — a successful start appends exactly one `startup` record (`JNL-32a`), and a start with `+a` absent refuses at W9 before W17 and leaves the journal, seal and archive byte-for-byte unchanged (`JNL-32b`)**; the bot stays online and refuses affected mutations with a typed message carrying no exception text. **Blocked by D5.0-9, D5.0-12 and D5.0-13** |
| **WP-5** | ~~`shadow_comparisons` and its write path~~ | **Withdrawn by OD-55.** Package 5.1 owns it |
| **WP-6** | `tools/migration_authority.py` preview / authorize / observe / activate / abandon / status / **diagnostics** / **`register-journal-generation`** — including, from revision 12, **`V-R`'s approved-source-revision resolution and `V-C`'s three added `C-d` comparisons** — connecting as the coordinator principal, including the systemd, cgroup, host-scan, Drive-permission and **dispatch-journal** observations, the **journal seal, derived-genesis, chain, inode, probe-report and registered-generation verification of Algorithm V-C** — which is the **only** verifier that refuses a self-consistent **`A1 + A2 + A3`** rewrite of the seal and record 0 (§2.13.5c **F-1b**) — `archive-verify` after a restore, and the **post-import divergence re-read** | authority, refusal, exit-code, safe-output and non-interactive recovery tests (plan §13.3, CLI surfaces); the refusal to record evidence for a non-clear observation; the refusal to activate without a complete fence; the refusal to record `dispatch_journal_clear` while the unresolved set is non-empty (N5.0-20) **or while any §2.13.6 condition holds**; the refusal to register a generation whose predecessor is unsealed; and `diagnostics` printing an effective `sys.path` no service identity can write |
| **WP-7** | Monitoring: **four** `/healthz` checks and the bounded queries behind them | never-run, healthy, pending, fence-incomplete, writer-down, past-deadline, rolled-back **and no-current-registered-generation** states, with no player data |
| **WP-8** | The PostgreSQL and multi-process evidence suite and falsification: for each invariant, the mutation that breaks it and the assertion that then fails — including the adversarial cases the handoff's evidence plan names and the **`TC-5.0-JNL` band of §2.13.8 — fifty-three identifiers, one hundred and fourteen cases** — including §2.13.5c's **fourteen** falsification rows, of which `JNL-34b` asserts the one case the writer deliberately does **not** refuse and **F-13** is the deployment substitution revision 12 adds, and — **new in revision 8, extended in revision 9** — the construction-order harness with its four deployment-digest cases (`JNL-46`), the six construction failure injections split by cleanup outcome (`JNL-47`), the S4-0/S4-2 lifecycle (`JNL-48`), the capability matrix's feasible combinations, residuals and not-constructible cells executed under real capability sets (`JNL-49`, `JNL-50`), the two-case host-identity residual (`JNL-40`), and — **new in revision 12** — the deployment-provenance contract with its omission test (`JNL-51`), the canonical membership matrix (`JNL-52`) and the three new fail-closed conditions (`JNL-53`) | every row of §6.2 and §6.5 has a named passing test and every falsification is detected; every row of §2.13.6 has a test that refuses; the two checks §2.13.8 cannot produce are recorded as not run rather than claimed |
| **WP-9** | Operations document + **supervised operational rehearsal** on the disposable database: seed → shadow → fence → cutover → verification → rollback → restore, **including — new in revision 12 — the deployment procedure of §2.12.5a end to end, the custody and installation of the approved-revision record, the authenticated refresh of the root-owned object store, the §2.12.2 membership matrix, and the staging-residue recovery procedure**, **plus a `verify-capability` run with its privileged cleanup over both transient directories, its **S4-0** positive control and its Stage-4 `systemd-run` sandbox attribution, a journal rotation, a generation change, an `archive-verify` and — if the Operations Owner authorizes it — a supervised host reboot between a dispatch and its outcome** | the Operations Owner witnesses the rehearsal and accepts the document |
| **WP-10** | Security-focused review preparation and the review itself, covering the coordinator principal, the grant model, the Sheet-writer credential move and the Drive-permission procedure | the Security Reviewer reports; blocking findings closed and re-reviewed |
| **WP-11** | Submission, traceability, RAID, status, change-log, decision register | the gate package is complete |
| **WP-12** | Independent review, remediation cycles and re-review | the Independent Reviewer records a recommendation with no open blocking finding |
| **WP-13** | **Demoted in revision 4.** Google-access feasibility: measure Drive write-permission propagation and restore latency against a **disposable** spreadsheet and a **disposable** service account, and record the observed distribution | N5.0-18 has a measured **operational margin** rather than a proposed one. **It closes nothing**, and the artifact must say so in the same paragraph as the number, so a later reader cannot mistake a distribution for a bound. **No production spreadsheet, credential or access is touched** |
| **WP-14** | The coordinator host boundary (§2.12): the `freedomcoord` and `freedomsheet` OS accounts **and the `freedomjournal` group, provisioned in the order and with the exact memberships §2.12.2 records**, the `pg_hba.conf` ordering and `pg_ident.conf` map, the `sudoers` drop-in, the root-owned `/opt/freedom-blades/coordinator` deployment path **with its bare object store and the approved-revision record**, the wrapper, and the provisioning/audit/revocation/recovery/rotation procedure. **Revision 5 adds the second `sudoers` drop-in for `freedom-journal-admin` and its two denial rows; revision 12 adds the membership matrix, the object store and the approval-record custody** | the per-identity peer-denial matrix passes against real PostgreSQL; the dedicated identity succeeds on the socket and is refused over TCP with and without a password; `sudo -l -U` shows **neither** `Cmnd_Alias` for every service identity; an unauthorized `freedom-journal-admin` invocation is refused; no `sys.path` entry is writable by a service identity; a `pg_ident` rotation is exercised in both intermediate states; **and `JNL-52`'s eight cases pass — `getent group` matching §2.12.2 exactly, and positive and negative `id`/`namei -l`/`open` evidence for `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`, which is check `C-4`**. **Blocked by D5.0-11 and D5.0-12** |
| **WP-16** | **New in revision 12; this is remediation R11-A.** The **deployment contract** of §2.12.5a: the root-owned bare object store and its authenticated refresh; the approved-revision record `APR` and its custody; `source_manifest_digest()` and `deployed_source_manifest_digest()` as specified functions; the reviewed **deployment map** and the hash-pinned dependency lock; **Algorithm D `D0 … D8`** with refusals `DEP-01 … DEP-09`, the closed two-region partition and the rollback at D7/D8; and the provenance record `PVR` | `JNL-51`'s eight cases pass, including **the negative test P5.0-SR1 requires** — the provenance step omitted, `init-generation` refusing at **C0**, no artifact and no row created, and a direct registration refused by the `NOT NULL` foreign key under both the coordinator role and the schema owner; a deployment is proved by syscall trace to read no path under the group-writable worktree; and the three manifest functions are proved identical across their call sites (`JNL-46`). **Blocked by D5.0-12** |
| **WP-15** | **New in revision 5; substantially rewritten by remediation R5; corrected by remediation R6, R7 and R8; extended by remediation R11.** The dispatch journal's durable storage and lifecycle (§2.13): the root-owned `/var/lib/freedom-sheet-writer` hierarchy with its ownership, modes and filesystem requirement, **including the third system group `freedomjournal`, the `0750` journal directory and the `0440` seal the writer may read**; the **four-stage capability probe of §2.13.2a** with its disposable arena, control stage, attribution table, privileged cleanup and — **new in revision 7** — its Stage-4 `systemd-run` sandbox attribution executed **at provisioning, before the report is built**, with the deployed unit's directives captured and hashed, and — **new in revision 8, remediation R7-B** — its **`…/probe-ro` target directory and the S4-0 positive DAC control** that must pass on the exact S4-2 target before any `EROFS` is interpreted; the **acyclic and executably ordered generation construction of §2.13.5a (Algorithm C, C0 … C13)** with its post-probe check step **C2** and — **new in revision 9, remediation R8-A** — **`deployment_manifest_digest()` of §2.13.2c**, computed at **C0** and compared with the operator's supplied value before anything consumes it and **recomputed at C2**; the **transient-directory state machine of §2.13.2b**, in which a failed cleanup is a distinct exit that reports its residue and **refuses rather than cleaning it**; and its PostgreSQL registration; the hash-chained record format; and `freedom-journal-admin` with its `sudoers` drop-in — `verify-capability`, `init-generation`, `seal`, `rotate`, `repair`, `archive-verify`, `dispose` | `verify-capability`'s **control stages pass before any refusal is interpreted** — Stage 1 for Stage 2 and **S4-0 for S4-2** — and report `inconclusive` rather than `passed` when they do not; the four stages distinguish DAC, a read-only mount, the sandbox and `FS_APPEND_FL`, **each with a positive control on its exact target** (`JNL-48`); **the construction-order harness walks C0 … C13 and proves every consumed value exists, is final and has passed its validation before use** and asserts **I-1 … I-5**, including that a malformed or wrong supplied digest is refused at **C0** and a deployment changed between C0 and the probe is refused at **C2** (`JNL-46`, five cases), and six failure injections prove that a refusal before **C5** creates no journal, seal, symlink, `.close` manifest or registration row **in every case**, with residue present or absent exactly as §2.13.2b's state machine says (`JNL-47`); **the report it returns contains all four stages and `append_only_probe_digest` is computed over exactly those bytes** (`JNL-29`); cleanup removes both transient directories, and a failed cleanup exits with its own code, names every remaining artifact by path, leaves it untouched and makes the next run refuse (`JNL-30`, `JNL-47`, `JNL-48`); **an independent implementation re-derives the genesis record from the seal body alone** (`JNL-31`); `init-generation` refuses while a predecessor is unsealed or **either transient directory exists, and cleans neither**; `seal` produces an immutable archive and a `.close` manifest naming the unresolved set; `dispose` refuses without N5.0-23, the §15.1 gate and a Data Owner reference; and the **fifteen** manipulation rows of §2.13.4 each fail with the expected `errno` under the `freedomsheet` uid; **and — new in revision 12 — `init-generation` **C0** refuses when the provenance record is absent, when it disagrees with the approval record, when the deployed source manifest no longer matches the trusted one, or when an unaccounted file is present in the deployed root (`JNL-46` cases (f) … (i))**. **Blocked by D5.0-13** |

---

## 4. Estimate and capacity

Units are focused implementer-days for one implementer, excluding blocked time
and excluding the maintainer's own decision and review time (plan §0.4).

| WP | O | ML | P | Change in revision 12 |
|---|---|---|---|---|
| WP-1 contract | 0.5 | 2.2 | 3.8 | — |
| WP-2 migration, two sequences, triggers, coordinator role, grants, seed, the sixth table, **and the seventh table plus four generation columns with a `NOT NULL` foreign key** | 2.3 | 3.9 | 6.0 | **+0.4 / +0.7 / +1.0** |
| WP-3 domain + application services, **five commands** | 1.6 | 2.7 | 4.8 | — |
| WP-4 database authority fence + startup refusal | 1.0 | 2.0 | 3.5 | — |
| WP-4b Sheet writer + drain + explicit timeout + durable journal client, Algorithm V-W and **twenty-eight** refusal codes, **including W11a** | 2.9 | 5.5 | 8.7 | **+0.2 / +0.4 / +0.6** |
| WP-5 telemetry — **withdrawn (OD-55)** | — | — | — | — |
| WP-6 coordinator command, observations, generation registration and Algorithm V-C/V-R verification **including the approved-source-revision resolution**, divergence re-read | 2.1 | 4.1 | 7.1 | **+0.2 / +0.4 / +0.7** |
| WP-7 monitoring, **four checks** | 0.5 | 1.2 | 2.2 | — |
| WP-8 PostgreSQL, multi-process, host-boundary, journal and adversarial evidence + falsification — **fifty-three identifiers, one hundred and fourteen cases** | 4.9 | 9.6 | 15.1 | **+0.6 / +1.2 / +2.0** |
| WP-9 operations doc + rehearsal, with the capability probe, rotation, generation change, the §2.13.2b residue-recovery procedure **and the §2.12.5a deployment procedure, approval-record custody and object-store refresh** | 2.0 | 4.3 | 7.0 | **+0.3 / +0.6 / +1.0** |
| WP-11 submission and registers | 0.5 | 1.0 | 1.5 | — |
| WP-13 Google-access margin measurement | 0.5 | 1.0 | 2.0 | — |
| WP-14 coordinator host boundary — OS identities **and the canonical membership matrix**, peer map, sudo, deployment path **and the root-owned object store and approval record** | 1.5 | 3.1 | 5.6 | **+0.4 / +0.8 / +1.3** |
| WP-15 journal storage, the acyclic generation construction, the four-stage probe, the deployment-digest computation, the cleanup state machine, `freedom-journal-admin`, **and C0's provenance preconditions and the four sealed provenance fields** | 1.9 | 3.8 | 6.6 | **+0.2 / +0.5 / +0.8** |
| **WP-16 the deployment contract — the object store, `APR`, the two manifest functions, the deployment map, the dependency lock, Algorithm D and `PVR`** | **0.9** | **1.9** | **3.2** | **new** |
| **Total** | **23.1** | **46.3** | **77.1** | **+3.2 / +6.5 / +10.6** |

PERT expectation `(O + 4ML + P) / 6` = `(23.1 + 185.2 + 77.1) / 6` = `285.4 / 6`
= **47.6 implementer-days**, up from **40.9**.

**The increase is decomposed rather than absorbed, and none of it is contingency.**
R11-A creates one new work package and adds real, separately reviewable work to
six existing ones: a seventh table and four columns in the migration; one writer
step and three refusal codes; one coordinator lookup and three comparisons;
twenty-six evidence cases across three new identifiers; a deployment procedure
and a credential-custody procedure in the operations document; and two new host
objects in the boundary work. R11-B adds the membership matrix to WP-14 and its
eight evidence cases to WP-8. **Nothing is netted off against the remediation
allowance**, which is a separate line and is not a place to hide new scope.

**The change from revision 11 to revision 12.** One work package is added and
seven grow. Each movement is a named remediation requirement, not a re-estimate
of work that was already there.

**A delta column rather than a running one**, because a running column on rounded
figures accumulates rounding rather than arithmetic. Each delta is
`(O + 4ML + P) / 6` over that package's own O/ML/P movement in the table above.

| Movement | O / ML / P | PERT delta |
|---|---|---|
| **WP-16 — the deployment contract**, new (R11-A): the root-owned bare object store, the approved-revision record, `source_manifest_digest()` and `deployed_source_manifest_digest()`, the reviewed deployment map, the hash-pinned dependency lock, Algorithm **D** with nine refusals and a rollback, and the provenance record | 0.9 / 1.9 / 3.2 | **+1.95** |
| **WP-8 — the band grows from eighty-eight cases to one hundred and fourteen** across three new identifiers `JNL-51`, `JNL-52` and `JNL-53`, including the omission test and the membership matrix | 0.6 / 1.2 / 2.0 | **+1.23** |
| **WP-14 — the canonical membership matrix, the object store and the approval-record custody** (R11-A, R11-B) | 0.4 / 0.8 / 1.3 | **+0.82** |
| **WP-2 — the seventh table `approved_source_revisions`**, its append-only trigger and grants, and four generation columns including a `NOT NULL` foreign key | 0.4 / 0.7 / 1.0 | **+0.70** |
| **WP-9 — the deployment procedure, credential custody and object-store refresh in the operations document and the rehearsal** | 0.3 / 0.6 / 1.0 | **+0.62** |
| **WP-15 — C0's provenance preconditions and the four sealed provenance fields** | 0.2 / 0.5 / 0.8 | **+0.50** |
| **WP-6 — `V-R`'s approved-source-revision resolution and `V-C`'s three added comparisons** | 0.2 / 0.4 / 0.7 | **+0.42** |
| **WP-4b — W11a and three refusal codes** | 0.2 / 0.4 / 0.6 | **+0.40** |
| **Total** | **3.2 / 6.5 / 10.6** | **+6.63** |

`40.93 + 6.63 = 47.57`, which is the **47.6** the totals row computes directly
from `285.4 / 6`. **The two routes agree**, which is the only reason both are
shown.

**The remediation allowance moves with ML because it is defined as a percentage
of it, and that is arithmetic rather than a judgement.** Nothing is rounded,
absorbed or netted off; the per-package O/ML/P deltas in the estimate table sum
to the totals shown there, and the PERT movements above sum to the PERT total.

**Retained — the change from revision 10 was none, and the reason was stated
rather than asserted.** The R10 brief required an estimate to be recalculated
**only if the corrected contract actually changes it**, and to say so explicitly
otherwise. **It did not change: revision 11's total stayed at PERT 40.9 and every
O/ML/P triple was carried forward unmodified**, for four reasons that are
checkable against the R10 corrections themselves:

- **no case, identifier or test is added or removed** — the band stays at fifty
  identifiers and eighty-eight cases (§2.13.8), so WP-8's executed work is the
  same work;
- **the capability harness was already budgeted** in revision 10, at **WP-8
  +0.40** and **WP-9 +0.08**, and it is that same harness. R10 substitutes one
  already-installed, non-set-user-ID, no-file-capability system binary
  (`/usr/sbin/capsh`) for another (`/usr/bin/setpriv`) **inside** it, and adds a
  single `prctl(PR_GET_SECUREBITS)` assertion beside five `/proc/self/status`
  assertions the harness already made;
- **no host artifact, account, group, unit, `sudoers` rule, package installation,
  privileged command or production code path is added.** `verify-capability`,
  `freedom-journal-admin`, `migration-authority` and the writer are untouched,
  so WP-4b, WP-14 and WP-15 cannot move; and
- **the one redesigned control pair reuses an identity the plan already
  builds.** `JNL-50` case 7 and `JNL-49` case 11 take **E6** instead of **E2** as
  the isolating control; both were already in the identity table and both were
  already constructed for other cases, so the change is which row a case names,
  not how much is built.

**Nothing is rounded, absorbed or netted off to reach that answer**, and no
allowance is drawn down: there is simply no movement to decompose. Were an
increment invented for a documentation-and-design remediation that adds no
executed work, it would be an estimate about a state that does not exist —
which is the class of claim stop condition **10b** forbids.

**The change from revision 9, decomposed rather than announced — retained.** No work
package is added, none is removed, and **no new numeric control, decision,
column, table, trigger, command, refusal code or test identifier is introduced**.
Three packages move, and each movement is a named R9 finding rather than a
re-estimate.

| Movement | PERT effect |
|---|---|
| Revision 9 baseline | 40.4 (40.40 unrounded) |
| **WP-8 — four added cases, eight rewritten ones, and a capability harness that is new machinery rather than more assertions** (R9-A, R9-C): `JNL-49` and `JNL-50` at **twelve cases each**; the executable-identity table's eight identities, each requiring a privilege-dropping invocation with **securebits** — *written as `setpriv` in revision 10 and rebuilt on `capsh(1)` in revision 11, at no change to this figure; see the revision-11 note above* — and a `/proc/self/status` assertion of `CapPrm`, `CapEff`, `CapInh`, `CapAmb` and `CapBnd` **before** the operation under test; a disposable `fbprobe` uid provisioned and removed per run; and a **positive control that succeeds** beside every negative flag case, which doubles the executed work for the eight rows whose minimum combination changed. `JNL-13` also grows from thirteen manipulation rows to fifteen. O 4.1 → 4.3, ML 8.0 → 8.4, P 12.5 → 13.1 | **+0.40** → 40.80 |
| **WP-9 — the rehearsal provisions the capability sets and the operations document records them** (R9-C): `fbprobe`, the four capability-bearing identities and their securebits — *revision 11 rebuilds these on `capsh(1)`; the estimate does not move, see the revision-11 note above* — and the statement that a flag change needs owner authorization as well as `CAP_LINUX_IMMUTABLE`, which is what makes `freedom-journal-admin` a root tool rather than a capability-bearing one. ML 3.6 → 3.7, P 5.9 → 6.0 | **+0.08** → 40.88 |
| **WP-15 — `freedom-journal-admin`'s privileged operations state their kernel prerequisites** (R9-A): each flag change in the lifecycle table names both requirements, and the tool asserts effective UID 0 at entry rather than assuming it. **The code does not change**; what changes is the specification it is written against and the assertion that makes the assumption checkable. P 5.5 → 5.8 | **+0.05** → **40.9** |
| WP-1, WP-2, WP-3, WP-4, **WP-4b**, WP-6, WP-7, WP-14 | **unchanged.** V-W's eighteen steps, the twenty-five refusal codes, every schema object, every command and every health check are untouched. **WP-4b in particular does not move**: R9 corrects the model of a kernel check the writer never invokes, so neither the writer's code nor its contract changes |

**The change from revision 8 to revision 9, retained.** No work
package is added, none is removed, and **no new numeric control, decision,
column, table, trigger, command, refusal code or test identifier is introduced**.
Four packages move, and each movement is a named R8 finding rather than a
re-estimate.

| Movement | PERT effect |
|---|---|
| Revision 8 baseline | 39.5 (39.47 unrounded) |
| **WP-8 — the band grows from seventy-four cases to eighty-four, and three of the additions need capability sets rather than root** (R8-A, R8-B, R8-C, R8-D): `JNL-46`'s four deployment-digest cases, including a deployed file changed between C0 and C1; `JNL-47`'s split into four S-A injections and two S-B injections with deterministic residue, next-run behaviour and recovery; `JNL-49` and `JNL-50` at ten cases each, of which the new ones must be **executed under a non-root `CAP_LINUX_IMMUTABLE`-only ambient capability set** through `setpriv --ambient-caps` rather than simulated as root; and `JNL-40`'s second case, which needs a second host or a disposable host whose `/etc/machine-id` can be rewritten. **The per-case cost is higher than revision 8's**, because a capability-set harness and a second-host restore are new machinery rather than more assertions | **+0.53** → 40.00 |
| **WP-15 — the deployment digest becomes a specified function and the cleanup becomes a state machine** (R8-A, R8-B): `deployment_manifest_digest()` with its manifest, its three call sites and its drop-in coverage; the C0 computation and comparison and the C2 recomputation; three named exit states with a residue report carrying path, operation and `errno`; and the **removal** of the automatic residue clean, which is a subtraction from the code and an addition to the operations procedure | **+0.20** → 40.20 |
| **WP-9 — the operations document gains the residue-recovery procedure and the F-7 disclosure** (R8-B, R8-D): the named operator steps for §2.13.2b state S-B, and the statement that a forged matching host identity is detected by nothing here and what evidence remains instead | **+0.12** → 40.32 |
| **WP-4b — W10 and W11's contracts are narrowed and re-pointed** (R8-A, R8-D): W11 calls the named shared function rather than an unspecified one, and W10's claim is bounded to the unforged case. **The writer's code does not change**; what changes is the contract it is tested against, and the two tests that assert the bound | **+0.08** → **40.4** |
| WP-1, WP-2, WP-3, WP-4, WP-6, WP-7, WP-14 | **unchanged.** V-W's eighteen steps, the twenty-five refusal codes, every schema object, every command and every health check are untouched: R8-A moves a computation into C0, R8-B replaces one cleanup branch with three named states, R8-C replaces a table, and R8-D withdraws a claim |

**The change from revision 7 to revision 8, retained.**

| Movement | PERT effect |
|---|---|
| Revision 7 baseline | 38.2 |
| **WP-8 — the band grows from forty-five identifiers to fifty, and from forty-eight cases to seventy-four** (R7-A, R7-B, R7-C): the construction-order harness and its value-dependency assertions (`JNL-46`); five construction failure injections, each proving nothing persistent was created (`JNL-47`); the S4-0/S4-2 lifecycle with its four distinguishable outcomes (`JNL-48`); eight capability/artifact pairings and residuals, one of which asserts a case this design does **not** refuse (`JNL-49`); and eight not-constructible cells executed under their real identities (`JNL-50`). **This is the largest single movement in the package's history, and it is a consequence of replacing a two-class claim with a matrix that has to be tested cell by cell** | **+0.87** → 39.07 |
| **WP-15 — Stage 4 gains a target directory, a positive control and an ordering constraint** (R7-B), and Algorithm C gains a validation step and a fourteenth step number (R7-A): `…/probe-ro` with its two files, the `setpriv` unsandboxed control, the extension of the `finally` cleanup and the two extra refusals at **C0** and **C2** | **+0.30** → 39.37 |
| **WP-9 — the rehearsal runs S4-0 and the `…/probe-ro` residue path** alongside the existing `verify-capability` run | **+0.10** → **39.5** |
| WP-1, WP-2, WP-3, WP-4, WP-4b, WP-6, WP-7, WP-14 | **unchanged.** V-W's eighteen steps, the twenty-five refusal codes, every schema object, every command and every health check are untouched: R7-A renumbers Algorithm C, R7-B adds a probe case and R7-C replaces a prose claim with a table, and none of the three changes what the writer or the coordinator executes |

**The change from revision 6 to revision 7, retained.**

| Movement | PERT effect |
|---|---|
| Revision 6 baseline | 37.7 |
| **WP-8 — the band grows from forty-one identifiers to forty-five, and from forty-two cases to forty-eight** (R6-A, R6-B, R6-C): `JNL-32` split into a successful-start and an absent-flag branch with opposite expectations; `JNL-34` split by attacker class, including `JNL-34b`, which asserts a case the writer deliberately does not refuse; `JNL-42 … 45` for the four independent binding fields; and `JNL-29` extended to assert the report contains all four stages | **+0.4** → 38.1 |
| **WP-15 — Stage 4 moves into `verify-capability`** (R6-A): a `systemd-run` transient unit, the `ReadWritePaths=` substitution, `systemctl show` capture and directive-set hashing, the deployed-unit precondition and the deployment-digest binding. **It replaces a deployment-time step rather than adding one**, so the net is small | **+0.1** → 38.15 |
| **WP-4b — the binding section changes shape** (R6-B): parsed at the version the chain-authenticated body declares, exactly three fields, length-exact with no trailing byte permitted. It is close to a simplification of V-W; what costs is the exactness of the parse and its four new negative tests | **+0.05** → **38.2** |
| WP-2, WP-3, WP-6, WP-7, WP-9, WP-14 | **unchanged.** No column, constraint, trigger, command, health check or host artifact changes. `sealed_at` was never a database column, so R6-B costs the schema nothing |

**The change from revision 5 to revision 6, retained.** No work package
was added; five grew, and each growth was a named remediation rather than a
re-estimate.

| Movement | PERT effect |
|---|---|
| Revision 5 baseline | 35.5 |
| **WP-15 — the four-stage probe with its arena, control stage, attribution table and privileged cleanup, and Algorithm C's twelve ordered construction steps** (R5-A, R5-C) | **+0.7** → 36.2 |
| **WP-4b — Algorithm V-W**: the seal read, the derived-genesis comparison, the host and deployment checks, the probe-report check, the `startup` record, and four more refusal codes (R5-A, R5-B, R5-C) | **+0.4** → 36.6 |
| **WP-8 — the band grows from twenty-six cases to forty-one**, including the syscall-trace assertion that startup is non-destructive with `+a` absent, and §2.13.5c's eight falsification cases | **+0.5** → 37.1 |
| **WP-6 — Algorithms V-C and V-R**: thirteen compared values instead of four, the probe-digest comparison, and `archive-verify` at every successor registration (R5-A, R5-D) | **+0.3** → 37.4 |
| **WP-2 — the column change**: `append_only_verified` withdrawn, four columns added, and the enforce-versus-record division asserted case by case (R5-D) | **+0.2** → 37.6 |
| **WP-9 — `verify-capability` and its cleanup in the rehearsal**, plus the sandbox-attribution stage at deployment | **+0.1** → **37.7** |

**The change from revision 4 to revision 5, retained.**

| Movement | PERT effect |
|---|---|
| Revision 4 baseline | 29.2 |
| **WP-4b — the durable journal client** (P5.0-R5): seal and generation validation at start, the hash-chained writer, the free-space precondition, and twenty-one typed refusal codes instead of one best-effort append | **+1.0** → 30.2 |
| **WP-2 — the sixth table**, its chain constraints, the three evidence columns and the activation trigger's fifth condition | **+0.5** → 30.7 |
| **WP-3 — the journal-generation value object and the fifth command** | **+0.2** → 30.9 |
| **WP-6 — generation registration, seal/chain/inode verification and `archive-verify`** | **+0.5** → 31.4 |
| **WP-7 — the fourth `/healthz` check** | **+0.2** → 31.6 |
| **WP-8 — the twenty-six-case `TC-5.0-JNL` band**, including the disk-full and `fsync`-failure injections and the ten-row manipulation matrix | **+1.2** → 32.8 |
| **WP-9 — rotation, generation change, `archive-verify` and the supervised reboot in the rehearsal** | **+0.3** → 33.1 |
| **WP-1 — three new numeric controls in the register** | **+0.2** → 33.3 |
| **WP-14 — the second `sudoers` drop-in and its two denial rows** | **+0.2** → 33.5 |
| **WP-15 — the journal storage and lifecycle**, new | **+2.0** → **35.5** |

**The change from revision 3 to revision 4, retained.**

| Movement | PERT effect |
|---|---|
| Revision 3 baseline | 23.7 |
| **WP-4b — drain, explicit request timeout, `fsync`-ed dispatch journal** (R3-A) | **+1.0** → 24.7 |
| **WP-6 — journal reading, ACL readback, the adjudication output and the divergence re-read** | **+0.5** → 25.2 |
| **WP-8 — the host-boundary denial matrix** (R3-B) | **+1.0** → 26.2 |
| **WP-9 — the divergence re-read and the unresolved-set adjudication in the rehearsal** | **+0.4** → 26.6 |
| **WP-1 — two reframed and two new numeric controls in the register** | **+0.4** → 27.0 |
| **WP-14 — the coordinator host boundary** (R3-B), new | **+2.2** → **29.2** |

**The change from revision 2 to revision 3, retained.**

| Movement | PERT effect |
|---|---|
| Revision 2 baseline | 20.8 |
| **Withdraw the lease apparatus** — two tables and their constraints, the lease client, the admission guard, the in-flight drain register, the acknowledgement writer, the `fence_protocol_version` handshake and the whole clock-injection evidence band | **−2.0** → 18.8 |
| **Add the separately terminable Sheet writer** (WP-4b): a fourth unit, an IPC boundary, two call-site migrations and characterization in a live service | **+2.5** → 21.3 |
| **Add the coordinator principal and observed evidence** (P5.0-R4): the role and `pg_hba` design, the evidence table and its triggers, the systemd/cgroup/host-scan/Drive observations in WP-6, and the per-principal denial evidence in WP-8 | **+1.4** → 22.7 |
| **Add the Google-access feasibility measurement** (WP-13) and its rehearsal step in WP-9 | **+1.0** → 23.7 |

**Separately, and deliberately not inside those figures:**

| Item | Estimate | Note |
|---|---|---|
| Independent implementation review (WP-12) | **2.5–3.0 reviewer-days**, unchanged | the boundary now spans a database trigger, a fourth process with a drain and a durable journal, a sixth table, a second privileged root-run tool, an external access change and a host privilege boundary |
| **Independent logical-schema re-review** | 0.5–1.0 reviewer-days | **before** WP-2 begins; it is a readiness precondition, not a gate activity |
| Security-focused review (WP-10) | **4.5–5.5 reviewer-days** | **Raised again in revision 12, and this time because a surface is added rather than because the model grew.** §9.2 goes from **eleven** surfaces to **twelve**: the reviewed-source provenance chain — an approval record whose only integrity is root ownership, a root-owned Git object store, a reviewed deployment map that decides ownership and modes, a hash-pinned dependency region, and a root-run algorithm that installs the program carrying authority over the authority plane. The reviewer must also confirm the **canonical membership table** identity by identity — which is what the previous re-review could not do, because the document contradicted itself — and re-derive **F-13** and the widened **A5**. **The two conditions on the assignment stand**, and the first pass returned P5.0-SR1 and P5.0-SR2 rather than a recommendation. *Revision 10 raised this to 3.5–4.5 for R9-A;* and the reason is R9-A rather than a new surface: the threat model is now **eleven independently constructible authorities** — the register grows by the two owner-authorization rows `A10` and `A11` — whose **combinations** must each be checked against the *two* permission checks `FS_IOC_SETFLAGS` actually makes, and against a **holder table** the reviewer must confirm identity by identity. Eleven of the thirteen falsification rows changed their minimum combination, and there are still **two** unrefused residuals (**R-5.0-12**, **R-5.0-13**). *Revision 10 kept the surface count at eleven and added two reviewer questions; revision 12 adds the twelfth surface and three more questions.* *Revision 9 raised this to 3.0–4.0 for R8-C.* It covers a new database principal, two new OS identities, **two** `sudoers` drop-ins one of which runs **as root**, `pg_hba`/`pg_ident` ordering, a root-owned deployment path, **a root-owned durable state hierarchy with filesystem attributes and an evidence-disposal path**, hardening on two live units and the pre-existing group-writable repository tree (H-1), a credential relocation and a production-access procedure — and, from revision 6, **a seal the writer may read** and **a transient probe arena the writer's identity may write**, from revision 7 a **transient root-started unit**, and from revision 8 the **`…/probe-ro` directory** (§9.2 surface 11) — see §9.2 |
| Remediation allowance | **13.9 days** (30 % of ML, 0.30 × 46.3 = 13.89) — *11.9 in revision 11, on an ML of 39.8* | Phases 2, 3 and 4 each ran two or more remediation cycles, and package 5.0 has now run **nine** before implementation began |
| Operational rehearsal (WP-9), supervised | 1.5–2.0 days of Operations Owner time | witnessed, not self-reported; it now includes a drain proof, a termination proof, an access-revocation step, an unresolved-set adjudication, a post-import divergence re-read, **a `verify-capability` run with its cleanup, a journal rotation, a generation change, an `archive-verify` and — if authorized — a supervised host reboot between a dispatch and its outcome** |
| Maintainer decision time | D5.0-9, D5.0-10, D5.0-11, D5.0-12 and **D5.0-13**, plus the readiness and gate decisions. **D5.0-9 is now a risk acceptance, not only a cost choice**, which is a different kind of decision and may take longer | not estimable by the implementer |
| Contingency | **4.0 days** | **unchanged.** Matched to R-5.0-1, R-5.0-3, R-5.0-5, R-5.0-7, R-5.0-8 and R-5.0-11 in §7. **R-5.0-12, R-5.0-13 and R-5.0-14 do not raise it**, because none of them is work this package can do: two are residuals for the Acceptance Authority and the third is an operator-recovery path already inside WP-9 |

**Against the roadmap.** Plan §12 withdrew Phase 5's numeric target range
deliberately, so there is **no range to compare against** and none is invented
here.

**Confidence: low-to-moderate, and stated with its drivers rather than as a
number alone.**

*Upward:* the fence for database writes is a single trigger reading a single
indexed row, which is the simplest correct thing available and has no timing
behaviour to get wrong; the Sheet write surface is one function with two call
sites, verified in §2.9, so the isolation is bounded; the idempotency, audit,
authorization, unit-of-work, translation, grants and migration mechanisms all
exist and are proven; the schema is purely additive and has no legacy data to
reconcile; the sixth table follows the same chain shape as the revisions table, so
it introduces no new constraint idiom; the revision-6 generation construction is a
strictly ordered sequence of ordinary file operations with a stated dependency
graph rather than novel cryptography, and it is testable by re-derivation
(`JNL-31`); nothing touches a game rule; and the
host-boundary and storage work of §2.12 and §2.13 is configuration, permissions
and packaging rather than distributed-systems reasoning, which is the kind of work
that estimates well.

*Downward:* **(a)** WP-4b changes a live service's process topology *and* now adds
a drain and a durable, generation-validated journal on that service's mutation
path, which is the highest-consequence change in the package; **(b)** **five**
decisions are open and each blocks a work package — D5.0-9 can change WP-4b
wholesale, D5.0-11 blocks WP-2, D5.0-12 blocks WP-4b and WP-14, D5.0-13 blocks
WP-4b and WP-15; **(c)** §2.10 concludes that the Sheet half **cannot** be closed
by design, so the package's completion now depends on a risk-acceptance decision
rather than on implementation quality, and that is not something effort can buy;
**(d)** the bot has no typed settings boundary at all, so one must be built beside
`config.py` without disturbing a live service; **(e)** the activation trigger
duplicates checks the coordinator also makes — now two of them, the fence set and
the generation — and proving the two agree is real work; **(f)** the host-boundary
evidence needs **real OS identities and a real `pg_hba` reload** (A-5.0-4,
unconfirmed) and the journal evidence needs a **root-owned durable hierarchy and a
verified `chattr +a`** (A-5.0-5, unconfirmed), neither of which the disposable
database supplies; **(g)** two of the R4 evidence bullets — a real boot and a real
`fsync` failure — need either a supervised host action or fault injection, and
§2.13.8 names them rather than assuming them; **(h)** the falsification
requirement is where this project's history shows cycles are spent, and the
journal band alone now carries eighty-eight cases across fifty identifiers, of
which every capability case needs a constructed identity as well as an assertion;
**(i)** **nine** design revisions
have now been returned with Blocking findings, which is evidence that a design
pass here is not reliable on its own; **(j)** **from revision 6**: the R5 findings
were not gaps in the design's *coverage* but errors in its *mechanics* — a hash
order that could not be evaluated, a permission that contradicted a duty, a probe
whose refusals were not attributable, and a constraint credited with work it
cannot do. Three of the four were checkable on paper by anyone who traced the
construction once, and revision 6 therefore adds `JNL-31`, `JNL-32a`/`JNL-32b`,
`JNL-27` and §2.13.8a's table specifically so that the same class of error is
caught by a test rather than by a re-review; and **(k)** **new in revision 7, and
the most useful thing this section can now say**: the R6 findings were not errors
in the mechanics either — every mechanism revision 6 specified works — but
**claims stated one step past what the mechanism does**. A digest said to cover
four stages covered three; a refusal said to hold for the writer had one field
outside it; a test expected a record its own algorithm refuses to produce. That
class is invisible to a reader checking whether the design *works* and visible
only to one checking whether each sentence is *bounded*, which is why stop
condition **10h** and `JNL-29`, `JNL-34b` and `JNL-32b` exist; and **(l)** **new
in revision 8, and it narrows (k) rather than repeating it**: the R7 findings were
that class of defect **in the corrections themselves**. The step that was supposed
to make the probe report's coverage true consumed the report before creating it;
the stage that was supposed to attribute a refusal to the sandbox never proved
its target was writable without one; and the matrix that was supposed to name the
attacker's capability recorded which detector caught an injected mutation. **Each
correction reproduced, one level down, the defect it was correcting.** That is why
revision 8 answers all three with **executable artifacts rather than prose** — an
ordered-walk harness (`JNL-46`), a positive control (`S4-0`, `JNL-48`) and a
capability register whose every cell has a test or a not-constructible assertion
(`JNL-49`, `JNL-50`) — and why stop conditions **10i**, **10j** and **10k** are
added.

**Capacity assumptions.**

- One implementing agent working the package serially; no parallel Phase 5
  package. Plan §12.0 permits independent packages in parallel *"only when they
  touch no shared aggregate/cutover"*, and 5.0 is the shared cutover control.
- Peter available for **D5.0-9, D5.0-10, D5.0-11, D5.0-12 and D5.0-13 before the
  work packages they block start**, and for the readiness and gate decisions.
- Codex available for the schema re-review, the implementation review and at
  least one re-review; and a Security Reviewer for a distinct pass. **The
  Security Reviewer is not named.**
- Operations Owner available to witness one rehearsal.
- A disposable Google spreadsheet and a disposable service account available for
  WP-13. **If they are not, WP-13 cannot run and N5.0-18 stays unmeasured.** In
  revision 4 that is a smaller loss than it was in revision 3, because N5.0-18 is
  an operational margin rather than a control; it does not change D5.0-9's answer
  on its own.
- **A disposable operating-system identity, a `pg_hba`/`pg_ident` entry and a
  configuration reload on the disposable cluster**, for WP-14's peer-denial
  evidence. The attacking side of that matrix can use the existing service
  identities read-only; the coordinator side cannot be simulated. **This is a host
  change and needs the Operations Owner's authorization** — assumption A-5.0-4,
  unconfirmed. Without it the R3-B evidence cannot be produced at all, which is
  flagged here rather than discovered at WP-14.
- **New in revision 5, restated in revision 6: a root-owned durable directory
  hierarchy and a verified `chattr +a` capability**, for WP-15 and the
  `TC-5.0-JNL` band. Creating `/var/lib/freedom-sheet-writer`, creating a
  disposable `freedomsheet`-owned probe arena, setting a filesystem attribute and
  running the probe cases **under the writer's uid through `setpriv`** all require
  root — **assumption A-5.0-5, unconfirmed.** A disposable path under the same
  filesystem is sufficient for the evidence; the production hierarchy is
  provisioned at deployment, not here. **Revision 6 corrects what its absence
  costs**: `verify-capability` cannot produce a passing probe report, so
  `init-generation` refuses to create a generation at all — a **host-side**
  refusal by the privileged tool, not a database constraint (§2.13.8a).
  **Two bullets of the R4 evidence plan need more than that**: a real boot
  (`JNL-02b`) needs a supervised host reboot the Operations Owner must authorize,
  and a real `fsync` failure (`JNL-17`) needs fault injection — a loopback device
  with `dm-error`, or a `LD_PRELOAD` interposer in the harness. Both are named
  here rather than discovered at WP-8.
- **No calendar dates are proposed.** Under §0.4 and the governance README,
  effort is not converted into a promised date until reviewer and maintainer
  availability is known.

**Named roles.**

| Role | Assignee |
|---|---|
| Product Sponsor / Acceptance Authority | Peter Duscha |
| Product Owner, Data Owner, Operations Owner, Delivery Lead | Peter Duscha |
| Technical Lead (working) / implementer | Claude — designated, OD-61 |
| Independent Reviewer | Codex — designated, OD-61 |
| Independent schema reviewer | Codex — designated, OD-61 |
| Security Reviewer | Codex — named 2026-08-31, OD-61 closed. **The twelve-surface security design review was delivered 2026-09-02**; P5.0-SR1/SR2 are Closed on design, with no package-readiness recommendation pending operational evidence and decisions |

---

## 5. Dependencies and decisions

### 5.1 Dependencies

| Ref | Item | State |
|---|---|---|
| Phase 4 gate | dependency-direction and domain-correctness | **Approved 2026-08-29** (`C-P4-L`) |
| **D-04** | shared ledger/idempotency/domain foundations | **Closed 2026-08-29** |
| P4-R1 … P4-R5 | Phase 4 review findings | **All Closed 2026-08-29** |
| Phase 3 gate | authentication, authorization, web security | **Approved 2026-08-28** — supplies `platform_accounts`, the authorization port and the operator-command pattern |
| A-02 | disposable PostgreSQL with an assumable restricted runtime role | **Holds** — verified §8.1 |
| A-04 | the legacy Sheet-backed bot remains the rollback implementation until approved cutover | **Holds, and this package depends on it absolutely.** The `cutover → legacy` and `database → legacy` transitions exist only while it does |
| **A-5.0-3** | A disposable Google spreadsheet and disposable service account are available for WP-13 | **Unconfirmed.** Without it F-8 cannot be evidenced and D5.0-9's option set narrows |
| **A-5.0-5** | **New in revision 5; restated in revision 6; widened in revision 11.** A root-owned durable directory hierarchy, a **disposable probe arena owned by the writer's identity**, a **verified** `chattr +a` capability exercised **under the writer's uid**, the eight `E1 … E8` identities of §2.13.5c constructed with **`capsh(1)`** from a launching bounding set that already holds every capability they need, plus fault injection for a `fsync` failure and — if authorized — a supervised host reboot. **Widened again in revision 12:** a disposable **bare Git object store** and a disposable **approved-revision record** for `JNL-51`, and the ability to run `id`, `namei -l` and `open` **as each of `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`** for `JNL-52`, which is host check **C-4** | **Unconfirmed, and it is a host change.** Without it §2.13.2a's capability probe cannot be run, so `init-generation` **refuses to create a generation at all** — a host-side refusal, **not** a database constraint (§2.13.8a) — and the `TC-5.0-JNL` band cannot be produced, so **P5.0-R5 cannot close on evidence** — **and, from revision 12, neither `JNL-51` nor `JNL-52` can run, so the evidence P5.0-SR1 and P5.0-SR2 ask for is specified and unexecuted** |
| D-01b | per-vocabulary readiness | **Not required.** 5.0 introduces no controlled *game* vocabulary. Its four vocabularies — authority states, legal transitions, dispositions and fence methods — are control-plane values defined by this package and reviewed with its schema |
| OD-03/04/05/09/28/39 | rule decisions | **Not required for 5.0.** They stay blocking for their own packages |
| OD-16, OD-17 | `/info` exposure and legacy attribution | **Not required for 5.0**; they gate package 5.1 |
| OD-20 / OD-21 / OD-22 | production and staging topology | **Changed by this package, and this is a correction to revision 3's row.** Their substance stands — same host, loopback, separate roles and environment files, no shared credential, no service moved, no port opened — but the package now proposes **two operating-system identities, two `sudoers` drop-ins, `pg_hba`/`pg_ident` lines, a root-owned deployment path outside `/opt/freedom-blades/platform`, a root-owned durable state hierarchy under `/var/lib/freedom-sheet-writer`, a credential relocation and hardening on a live unit**. That is an accepted-topology change, raised as **D5.0-11 / OD-64 (extended)**, **D5.0-12 / OD-65** and **D5.0-13 / OD-66 (new)** rather than adopted |
| OD-48 | no Phase 4 ledger table; the PostgreSQL evidence reallocated to *"package 5.0 or 5.2"* | **Closed by OD-58** — the ledger table is 5.2's |
| **OD-54 … OD-61** | the eight package-5.0 rulings | **Closed / partly closed 2026-08-29** — traced in §5.2 |
| R-P4-4 | the ledger posting is durable only as far as process memory | **Active.** 5.0 narrows it and does not close it |
| R-03 | Phase 5 scope cannot fit its roadmap range | **Active.** This estimate is one input to it, now **47.6**. *This row read `35.5` in revisions 5 through 11 — the revision-4 figure, left behind by six estimate changes. It is corrected here rather than silently updated, because a stale number in a scope-risk row is exactly the kind of thing the risk exists to catch* |
| R-06 | cutover or rollback loses live-bot availability | **Active, and this package is both its principal mitigation and, through D5.0-9, a contributor** |
| §15.1 stage 7 | *"cut that field group's reads and writes over behind controlled feature flags"* | the flags do not exist; this package supplies them as database-enforced authority rather than as configuration |

### 5.2 Decision-to-document trace — OD-54 … OD-61

Each ruling, and every place in the controlled documents where it is now
realized. Where this revision changed how a ruling is realized, the change is
named.

| Ruling | What it decided | Where it is realized |
|---|---|---|
| **OD-54** / D5.0-1 | Package 5.0 persists its own authority control plane, and an authority revision is the durable effect in the effect/receipt/audit transaction. Conditional on remediating P5.0-R1 and P5.0-R2 | Logical schema §0.2 (the real consumers), §0.3 (the transaction boundary), §3.1–3.5 and **§3.7** (the tables). This plan §1.1, §1.2 deliverables 1–5 and **13**, §2.1 disposition, WP-2/WP-3. **The condition is what revisions 2, 3 and 4 discharge** |
| **OD-55** / D5.0-2 | Package 5.0 defines the comparison-telemetry contract only; package 5.1 owns the table, write path and independently reviewed schema | **Preserved from revision 2.** No telemetry table, column, grant, decision-table row, access pattern or test claim exists in package 5.0. The written contract is §11, which WP-1 folds into the contract document. Risk R-5.0-4 stays re-owned by 5.1 |
| **OD-56** / D5.0-3 | An internal character UUID may be stored when 5.1 implements telemetry, under restricted access and approved retention | §11 states it as a binding constraint on package 5.1. Package 5.0 stores **no player-identifying column at all** (logical schema §5, last row) |
| **OD-57** / D5.0-4 | N5.0-1 … N5.0-8 accepted; below 30 compared operations requires separate advance package-specific approval | §8.3, values unchanged, including revision 2's accepted wording correction to N5.0-4. §11 carries N5.0-2's advance-approval rule into the telemetry contract |
| **OD-58** / D5.0-5 | The durable wallet/ledger table and the account vocabulary belong to package 5.2; 5.0 creates no ledger table and does not close R-P4-4 | Logical schema §0.1 and §8; this plan §1.3, §5.1, §10 and the *Durable ledger posting* row of §12 |
| **OD-59** / D5.0-6 | Authority changes use a host-local operator command run by a named, currently authorized Platform Administrator against a validated database target, with preview/apply fencing, idempotency and safe output. No web or Discord mutation surface | This plan §1.2 deliverable 7, §2.4, WP-6. Logical schema §0.2 and §4.3, which goes further than revision 2: the command now connects as a **distinct database principal**, so *"only the operator may change authority"* is enforced by PostgreSQL rather than by which module opens the connection |
| **OD-60** / D5.0-7 | No new service-principal scope in 5.0; revisit only with a concrete consumer | This plan §1.3, §2.4 disposition. `application/service_principals.py` is untouched. **The coordinator is a database role for a human-run command, not a service principal**, so OD-60 is unaffected — stated explicitly because the two could be confused |
| **OD-61** / D5.0-8 | **Closed 2026-08-31.** Claude is implementer and working Technical Lead; **Codex is Independent Reviewer, logical-schema reviewer and Security Reviewer**, the last named by Peter Duscha on 2026-08-31 | This plan's header, §4 *Named roles*, §9.2, §9.4. RAID row D-5.0-1 no longer turns on an unnamed role but on the **review being delivered**. **Updated in revision 12:** the first §9.2 pass ran on 2026-08-31 and returned **changes requested with no readiness recommendation** — P5.0-SR1 Blocking, P5.0-SR2 Important, `C-1` not completed, `C-3`/`C-4` not run, the residuals unaccepted. Revision 12 remediates the two findings and returns them; §9.4 still concludes `not ready` |

### 5.3 Decisions this revision raises or reframes

Five. None is decided here.

#### D5.0-9 / OD-62 — **Reframed a third time.** Which cutover boundary is adopted, now that no barrier exists? · **material; risk acceptance, production availability, topology and external access; blocks WP-4b**

**Both earlier framings are withdrawn.** Revision 2 asked whether the bot could
take a 25-second PostgreSQL availability dependency; that was priced on a leased
design that did not close P5.0-R1. Revision 3 asked which of three costs was
accepted for an *enforceable* composite; §2.10.2 retracts the enforceability
claim on which that question rested. Neither is revived.

**The real question, now that §2.10 has done the search.** No externally
verifiable barrier proving I-SHEET-COMPLETE exists in the published Google APIs.
So the choice is no longer *which fence*; it is **what is accepted in place of a
fence**, and by whom.

The four options are compared in §2.10.5. In brief:

- **G-A (recommended).** Drain-first boundary with an enumerable unresolved set,
  fail-closed activation, containment and detection (W-1 … W-6). *Costs:* a
  fourth systemd unit and a fifth OS identity; a Sheet-mutation outage per fence
  window; a production Drive-permission change per cutover; an `fsync` on the
  legacy mutation path; an operator adjudication step; **and an explicitly
  accepted residual — an accepted-but-unacknowledged request that Google applies
  after the final import is not prevented and cannot be proved absent.**
- **G-B.** Pre-cutover write-path retirement — deploy a build without the unit's
  Sheet write path, refuse those mutations for an accepted period, then import.
  Stronger in kind, and costs a mutation outage measured in days, roughly forty
  times. **Variant G-B′** does it once for the whole bot.
- **G-C.** Accept a measured quiet period as the boundary. **Not recommended**;
  it is what the re-review rejected, and it is listed so the residual can be
  accepted knowingly rather than relabelled.
- **G-D.** Cut no Sheet-authoritative unit over. Package 5.0 still delivers the
  PostgreSQL fence, the isolated writer, the journal, the access control, the
  detection and the monitoring; the first Sheet-authoritative cutover waits.

**Why an agent cannot decide this, and why the reason has changed.** Revision 3's
reason was that `.agents/AGENTS.md` gates bot degradation and production access
changes, and that still holds. Revision 4 adds a stronger one: **G-A, G-B and G-C
all require someone to accept an unprovable residual on the authoritative store
of a live community's game state.** That is a risk acceptance under plan §0.2 and
§0.3, and it belongs to the Acceptance Authority. An implementer who took it
would be deciding the project's tolerance for silent data loss.

**What revision 6 changes, and what it does not.** The four options, their
owners and their costs are **unchanged**, and this decision is not decided here.
Two impacts are recorded because the R5 handoff requires them recorded:

- **G-A's enumeration control changed in substance.** The R4 handoff required
  that D5.0-9 not be ruled until the Independent Reviewer accepts that G-A's
  enumeration control is itself fail-closed, and the revision-5 statement of that
  control **could not be built** (§2.13.1 defects 5–9). Revision 6 replaces it —
  an acyclic construction, a writer that can actually validate the seal it
  depends on, a probe whose refusals are attributable, and a registration that no
  longer claims more than it does. **That precondition therefore still stands and
  is still not met**: it is the Independent Reviewer's to accept, not the
  implementer's to assert.
- **G-A's failure behaviour is marginally wider, and its topology slightly
  larger.** Four new refusal conditions (**J-22 … J-25**) mean four more states in
  which the writer refuses every Sheet mutation, so **R-5.0-11's** availability
  cost covers more cases than it did; and G-A now also carries a writer-readable
  seal and a transient probe arena, which is a small addition to the host
  topology the Security Reviewer must see. Neither changes G-A's *authority*,
  *retention* or *external access* costs, and neither narrows **R-5.0-8**.

**Owner: Product Owner and Acceptance Authority, with the Operations Owner and
the Security Reviewer. Required by: before WP-4b.**

---

**Decision history.** The revision-2 lease framing and the revision-3
*"which of three costs"* framing are retained in
[`../discovery/open-decisions.md`](../discovery/open-decisions.md) OD-62 so the
record shows what was proposed and why each was not approvable. Neither is to be
revived.

#### D5.0-10 / OD-63 — **Extended to nine.** The fencing numeric controls · **required before WP-1 completes**

Revision 3 reduced seven controls to four; revision 4 raised them to six; revision
5 **adds three** for the journal's storage lifecycle and changes none of the six
(§8.3):

| Ref | State in revision 6 |
|---|---|
| N5.0-14 | **unchanged** — activation deadline after `effective_at`, 24 hours |
| N5.0-16 | **unchanged** — maximum age of a quiescence observation at activation, 15 minutes |
| N5.0-17 | **unchanged from revision 4** — the writer drain timeout, and the unit's `TimeoutStopSec` |
| N5.0-18 | **unchanged from revision 4** — the post-revocation margin, explicitly *risk reduction, not a barrier* |
| N5.0-19 | **unchanged from revision 4** — the Sheets client's explicit per-request timeout |
| N5.0-20 | **unchanged from revision 4** — unresolved dispatch-journal entries permitted at activation, **zero** |
| **N5.0-21** | **new** — the minimum free space on the journal filesystem below which the writer refuses to dispatch. Proposed **1 GiB**. It is what makes §2.13.6 row **J-13** a refusal *before* the call rather than an `ENOSPC` discovered after it |
| **N5.0-22** | **new** — the maximum size of the current journal before a privileged rotation is required. Proposed **64 MiB**. It exists so the file cannot grow without a decision, not because growth is expected |
| **N5.0-23** | **new** — the retention of a sealed, archived generation. Proposed **until plan §15.1's Sheet-retirement gate closes, and in no case less than 365 days**. It is the only number in the register whose owner is the **Data Owner**, because it governs when evidence may be destroyed |

**Owner: Operations Owner and Product Owner; N5.0-23 additionally the Data
Owner.** N5.0-18 should still be ruled after WP-13 measures it, but the coupling
to D5.0-9 is weaker than it was: an unmeasured margin no longer removes a control,
because the margin was never one.

#### D5.0-11 / OD-64 — **Extended.** The authority-plane database principal **and its operating-system identity** · **material; security, credential and host topology; blocks WP-2 and WP-14**

Revision 3 asked only whether `freedom_migration_coordinator` is introduced.
P5.0-R4's re-review is that the question was incomplete: a peer-authenticated
role isolates nothing until the operating-system identity it trusts is named and
bounded. §2.12 supplies that specification. **The decision now covers both
halves**, because approving the role without the host boundary would approve a
control that does not exist.

- **Option A (recommended) — I-1.** Introduce the role *and* the dedicated
  `freedomcoord` OS user and group, the `pg_hba.conf` ordering, the single
  `pg_ident.conf` map line, the `sudoers` drop-in naming `foundry` only, the
  root-owned `/opt/freedom-blades/coordinator` deployment path with digest
  verification, and the wrapper that pins the interpreter and clears the
  environment. *Cost:* one OS account, one `sudoers` file, two PostgreSQL
  configuration lines and a reload, one deployment path. *Benefit:* four
  independent layers must all hold before a connection succeeds (§2.12.3), no
  secret exists to steal, and every claim is testable one runtime identity at a
  time.
- **Option B — I-2.** Introduce the role but map the existing `foundry` operator
  account. *Cost:* no separation between the maintainer's general-purpose account
  and the authority principal; anything `foundry` runs can reach the coordinator.
  *Benefit:* no new OS account. **It still needs the root-owned deployment path**,
  because H-1 lets a service process edit code `foundry` would execute.
- **Option C — Option B of revision 3.** Use the schema-owner credential.
  *Cost:* DDL rights the command does not need, and it inherits every problem of
  Option B. **Not recommended.**
- **Option D — I-3.** Keep one shared principal. **This is the P5.0-R4 finding.**

**Owner: Product Owner and Operations Owner, on the Security Reviewer's review.
Required by: before WP-2 and WP-14.**

#### D5.0-12 / OD-65 — **New.** The host changes the boundary requires outside the coordinator itself · **material; production topology and credential custody; blocks WP-4b and WP-14**

Three changes that §2.12 depends on, that are **not** about the coordinator
principal, and that each touch a live service. They are separated from OD-64
because they have a different owner and a different blast radius, and because two
of them are pre-existing conditions this package would otherwise be silently
relying on.

1. **A dedicated `freedomsheet` OS identity for `freedom-sheet-writer`, and the
   Google service-account credential moved into
   `/etc/freedom-blades/sheet-writer.env` (`root:freedomsheet`, `0640`).** The
   writer must not run as `discordbot`: that identity has a login shell and group
   write access to the whole repository (H-1). *This is a credential relocation
   and needs the Security Reviewer.*
2. **Hardening directives added to `freedom-bot.service.tmpl`** —
   `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`,
   `ProtectHome=true` — closing Phase 0 topology finding **F-3** (H-2). Every
   *"a service cannot gain privileges"* argument in §2.12.6 is weaker for the bot
   than for web and worker until this is done. *It is a change to a live unit and
   needs the Operations Owner.*
3. **A ruling on the group-writable repository tree (H-1).** Today
   `/opt/freedom-blades/platform` is group-writable by `discordbot`, and
   `freedomweb` is in that group, so the bot, web and worker processes can rewrite
   every module including `migrations/` and `.git`. §2.12.5 **works around** this
   with a separate root-owned deployment path rather than fixing it, because
   fixing it is wider than package 5.0 — it would change how the maintainer edits
   and deploys the repository. *The workaround is sufficient for the coordinator
   and does not make the condition acceptable*, and the Security Reviewer should
   see it named rather than infer it. **Revision 12 narrows what the workaround
   rests on**: §2.12.5a's deploy path reads the reviewed bytes out of a root-owned
   bare object store and **reads no path in the worktree at all** (`JNL-51` case
   (h)), so what a compromised service identity can edit is no longer an input to
   any deployment. **The condition itself is unchanged and still needs the
   ruling.**
4. **New in revision 12, from security-review finding P5.0-SR1: the
   reviewed-source provenance objects.** A **bare Git object store** at
   `/opt/freedom-blades/coordinator/source.git` (`root:root 0700`), refreshed only
   by root from an authenticated origin; an **approved-revision record** at
   `/etc/freedom-blades/approved-source-revision` (`root:root 0444`) installed out
   of band and naming the commit a review approved; and a **provenance record**
   at `/etc/freedom-blades/sheet-writer.provenance` (`root:root 0444`) that the
   deploy step writes and without which no generation can be created. **All three
   are new host objects and one of them is a governance artifact with an
   operational custody question** — who installs it, from what, and on whose
   signature. *It needs the Security Reviewer and the Operations Owner.*
5. **New in revision 12, from security-review finding P5.0-SR2: the canonical
   membership table.** §2.12.2 now states the primary and supplementary groups
   for every identity, including the `freedomjournal` membership revision 11's
   own §2.12.2 denied. **Provisioning must create the group and its two members
   in that exact order, and the membership matrix must be re-run after any
   account, group or deployment change.** *It needs the Operations Owner.*

- **Option A (recommended).** All **five**. *Cost:* one OS account, one system
  group with an exactly specified membership, one credential file move, four
  directives on a live unit, three new root-owned provenance objects with a
  custody procedure, and a separate decision on the repository permissions.
  *Benefit:* the §2.12.6 argument holds for every identity rather than for two of
  three, **and the supply-chain control §9.2 surface 7 names fails closed rather
  than silently**.
- **Option B.** Items 1, 2, 4 and 5; item 3 deferred to a separate maintenance
  change. *Cost:* the condition persists and the deployment-path workaround
  carries the whole weight — though revision 12 narrows what that weight is, since
  no deployment reads the worktree. *Benefit:* nothing about the maintainer's own
  workflow changes now.
- **Option C.** Items 1, 2, 3 and 5, without item 4. **The implementer's
  assessment is that this leaves P5.0-SR1 unremediated**: without the object
  store, the approval record and the provenance record there is no trusted side
  to the comparison, and the design returns to a digest of the deployment checked
  against itself. It is listed so the assessment can be disagreed with rather
  than hidden.
- **Option D.** None of them, and the writer runs as `discordbot` on an
  unhardened unit. **The implementer's assessment is that §2.12.6's argument does
  not hold under this option**, and it is listed so that assessment can be
  disagreed with rather than hidden.

**Owner: Operations Owner and Product Owner, on the Security Reviewer's review.
Required by: before WP-4b and WP-14.** If the preferred answer changes the
accepted production topology or credential contract, work stops and Peter's
ruling is requested before it is treated as binding — §9.3 stop condition 2.

#### D5.0-13 / OD-66 — **New.** The dispatch journal's durable storage, generation lifecycle and evidence-disposal authority · **material; production topology, privileged tooling and evidence retention; blocks WP-4b and WP-15**

Revision 4 specified this control in a table row. P5.0-R5 found that the row put
the journal on a volatile filesystem and inferred its append-only property from an
unrelated path, so a reboot could report an empty unresolved set. §2.13 replaces
the row with a contract, and that contract is **not** a design detail: it creates a
root-owned durable state hierarchy, a **sixth** table, a **fifth** application
command, a **second** privileged tool that runs **as root** under its own
`sudoers` drop-in, and a rule about when evidence may be destroyed —
**and, from revision 12, a seventh table and the reviewed-source provenance
objects that make the sixth one's registration refusable at all.**

Four things need a ruling together, because approving some without the others
would approve a control that does not hold:

1. **The storage.** `/var/lib/freedom-sheet-writer` on the verified ext4 root
   volume, root-owned throughout, with the writer holding **no write permission on
   the directory containing its own journal** (§2.13.3). Deliberately not
   systemd's `StateDirectory=`, which would make the writer the directory's owner.
   **Revision 6 adds two permission facts to this half**: a third system group
   `freedomjournal` makes `…/journal` `0750` and the `0440` seal readable by the
   writer — tightening the boundary for every other identity while granting the
   one read R5-B requires — and provisioning creates a transient
   `…/probe` arena the writer's identity may write, which exists only inside
   `verify-capability`, holds no evidence, and is refused while the writer unit is
   active (R5-C). **Revision 7 adds one fact to this half**: `verify-capability`
   starts a **transient `systemd-run` unit as root at provisioning**, carrying
   the deployed writer unit's hardening directives with `ReadWritePaths=`
   redirected to that arena, so Stage 4's sandbox attribution is inside the
   sealed report rather than in a later, separately trusted artifact (R6-A). It
   requires the writer's unit file to be **deployed** before a generation can be
   created.
2. **The generation and its registration.** A `chattr +i` seal on disk *and* a
   registered row in PostgreSQL, so the activation trigger can refuse stale and
   cross-generation evidence (§2.13.5). **The writer still never touches
   PostgreSQL**, so the legacy mutation path gains no database dependency.
   **Revision 6 replaces the construction itself**: the seal is split into a body
   and a binding section, the genesis record is anchored to `seal_body_digest`
   and *derived* rather than trusted, and `seal_digest` is a leaf no on-disk
   artifact contains (§2.13.5a). Revision 5's construction could not be built at
   all, so approving option A as revision 5 stated it would have approved
   something that does not exist. **Revision 7 narrows the seal itself**: the
   binding section loses `sealed_at` and its own format field, keeping exactly
   the three values **V-W** authenticates, and its structure is fixed by a
   `binding_format_version` carried in the chain-authenticated body (R6-B).
   Approving option A as revision 6 stated it would have approved a seal one of
   whose fields no reader validated.
3. **The privileged lifecycle.** `freedom-journal-admin`, run as root, with a
   second `sudoers` drop-in kept separate from the coordinator's so the two
   authorities are revoked independently (§2.13.7). **Revision 6 adds the
   `setpriv` drop to the writer's uid for probe cases, and a specified privileged
   cleanup whose failure is a non-zero exit.**
4. **The retention and disposal rule.** N5.0-23, and a `dispose` that refuses
   without the §15.1 gate and a Data Owner approval reference. *This is the part
   that is genuinely the Data Owner's*: it decides when a record of what the
   platform wrote to a live community's Sheet may be destroyed. **Unchanged in
   revision 6**, in cost, in authority and in retention period.

The options are §2.13.11's **J-1 … J-4**:

- **Option A (recommended) — J-1, and its content changed in revision 6, so it
  is re-stated rather than carried forward unread.** All four. *Cost:* a sixth
  table, a fifth command, a second privileged tool, a root-owned hierarchy, the
  refusal cost of N5.0-21 — a full or failing filesystem stops Sheet mutations
  (**R-5.0-11**) — and, new in revision 6, **a seal the writer may read** and **a
  transient probe arena the writer's identity may write**, both argued
  non-sensitive in §2.13.3 and §2.13.2a and both referred to the Security Reviewer
  as surface 11 (§9.2); **new in revision 7**, a transient `systemd-run`
  unit started **as root at provisioning** under the deployed writer unit's
  directives; and, **new in revision 8**, a **second** transient directory
  `…/probe-ro` the writer's identity may write, holding Stage 4's negative
  target — all three added to the same surface, each with its own reviewer
  question. *Benefit:* every unknown state refuses; a reset cannot look empty;
  the writer cannot erase what it authored; the enumeration survives a reboot;
  **the construction can actually be built**; **new in revision 7, every claim in
  it is bounded to what the artifacts do** — the probe digest covers the four
  stages it names, and every seal field a reader trusts is a field **V-W**
  recomputes or compares; and, **new in revision 8, it can actually be executed
  in the order it states**, every negative case has a positive control on its
  exact target, and the threat model is a capability register with a test or a
  not-constructible assertion per cell (§2.13.5a, §2.13.5b, §2.13.5c, §2.13.8a).
- **Option A-2 — new in revision 9, raised by remediation R8-D and deliberately
  *not* adopted.** Option A **plus an independent authenticated host-bound
  value**, which is the only thing that would close **F-7** / **R-5.0-13**.
  Because it changes the design surface rather than correcting a claim, §0.2
  routes it to the Acceptance Authority on the Security Reviewer's and the
  Operations Owner's advice; **the implementer does not adopt it and revision 9
  takes option A with the residual stated instead.** Specified far enough to be
  decidable:
  - *What it is.* A per-host secret the seal binds to and a second host cannot
    reproduce — either a value sealed to the host's TPM (a PCR-bound key whose
    public half the seal body carries and whose private half never leaves the
    chip), or a coordinator-signed host token issued once per host and held under
    `root:root 0400` outside the journal tree. **The distinguishing property is
    that it is not a copy of a fact the restored tree carries**, which is exactly
    what `/etc/machine-id` is.
  - *Authority.* Provisioned by the Operations Owner as a root act; the signing
    half, in the token variant, belongs to the coordinator's authority plane and
    is **not** reachable from the writer.
  - *Provisioning.* One act per host, before the first `init-generation`; the
    seal body gains one field and `SB` gains a `host_binding_version`; **the
    writer verifies it at a new V-W step**, which is the first V-W change since
    revision 6 and is why this is a surface change rather than a wording one.
  - *Rotation.* A new host binding invalidates every generation sealed against
    the old one, so it **forces a rotation** — the same rule as **J-22** and
    **F-6**, and no second invalidation rule.
  - *Backup and restore.* This is the cost that matters, and it is the reason it
    is not recommended lightly. **A legitimate restore onto replacement hardware
    stops working**: a TPM-sealed value cannot be restored at all, and a token
    must be re-issued by the coordinator, so disaster recovery gains a manual,
    authority-bearing step that must itself be rehearsed. A design whose whole
    purpose is that evidence survives a restore acquires a failure mode in the
    restore.
  - *Verification.* One new **V-W** step, one new coordinator comparison at
    **C-d**, one new refusal code beyond the family's current end, one new
    §2.13.6 condition, and
    at least three new `TC-5.0-JNL` cases — present, absent, and reproduced on a
    second host.
  - *Cost:* a new secret with a custody model, a hardware or credential
    dependency, a restore procedure that can fail closed on legitimate recovery,
    and the first growth of the refusal-code family since revision 6.
    *Benefit:* **F-7 becomes a refusal instead of a residual**, and R-5.0-13 is
    closed by design rather than accepted.
- **Option A-3 — new in revision 12, raised by remediation R11-A and deliberately
  *not* adopted.** Option A **plus a cryptographically signed approved-revision
  record**, which is the only thing that would close the host half of
  **R-5.0-15**. Under option A as taken, `APR`'s integrity is root ownership and
  mode: an actor holding **A5**, which on this host means uid 0 or
  `CAP_DAC_OVERRIDE` on root-owned paths, rewrites it and the deploy step and
  **C0** then agree with it. Specified far enough to be decidable:
  - *What it is.* Either a **signed Git tag or signed commit** on the approved
    revision, verified by the deploy step and by **C0** against a keyring held
    `root:root 0400` outside the object store; or an `APR` carrying a **detached
    signature** over its own canonical bytes, verified the same way.
  - *What it changes, and what it does not.* It moves the trust anchor from *a
    root-owned file* to *a root-held verification key*. **It does not remove
    root from the trust boundary**: an actor holding **A7** replaces the keyring
    as readily as the record. What it does close is the narrower case of an
    actor holding **A5** without **A7** — `CAP_DAC_OVERRIDE` on root-owned paths
    but no ability to install a key the release process would recognise — and it
    makes an unauthorized deployment detectable from an artifact **created off
    this host**.
  - *Authority and custody.* A signing key belonging to the release process, held
    by the Acceptance Authority, with its own generation, storage, rotation and
    revocation procedure — none of which this package has, and all of which
    §0.2 requires before a key is introduced.
  - *Cost:* a signing key with a custody model this project does not yet have; a
    revocation story (a revoked signature must invalidate deployments already
    made, which is a rotation rule and a new refusal); a verification dependency
    in a root-run tool; and a release process that can now **fail closed on a
    legitimate emergency deployment** when the signer is unavailable.
    *Benefit:* **R-5.0-15's A5-only half becomes a refusal instead of a
    residual**, and the provenance chain gains an anchor that is not a file on
    the host it protects.
  - **Not adopted, and stated as a choice rather than an omission.** Revision 12
    takes option A with **R-5.0-15** recorded, on the same reasoning as A-2:
    introducing a signing key is a governance change with its own failure modes,
    and it is the Acceptance Authority's to make, not the implementer's.

- **Option B — J-2.** Durable storage and the seal, without PostgreSQL
  registration and without the sixth table. *Cost:* the stale- and
  cross-generation checks exist only in the coordinator command, contradicting the
  reason this package already gave for duplicating the fence test in the database.
- **Option C — J-3.** Drop `dispatch_journal_clear` and the journal entirely.
  *Cost:* nothing refuses a cutover when a request is **known** outstanding; W-2,
  W-3 and two of the six achievable guarantees are withdrawn; the residual grows.
  **It is the honest alternative to the contradiction and it is Peter's to take,
  not the implementer's** — §2.13.9 says why it is not recommended.
- **Option D — J-4.** Keep revision 4's `/run` journal. **This is the P5.0-R5
  finding.**

**Owner: Operations Owner and Data Owner, on the Security Reviewer's review.
Required by: before WP-4b and WP-15.** The full contract is §2.13; the schema
consequence is logical schema §3.7.

**What revision 10 changes about this decision, stated so it is re-read rather
than assumed unchanged.** **Nothing in the decision itself.** The *authorities*,
*retention rule*, *topology*, *artifacts* and *options* are all untouched, and
options **A-2**, **B**, **C** and **D** are unchanged word for word, and
revision 12 adds **A-3** without touching any of them. Option A's
**content** does not move either: R9 corrects the *description* of a Linux
permission check that option A's design already depended on and never altered.
What changes is the **threat model that prices option A** — §2.13.5c's register
grows from nine authorities to **eleven**, eleven of thirteen falsification rows
gain a prerequisite, and every one of those changes makes the alteration
**harder** to construct, not easier. **No refusal is strengthened and no new
guarantee is claimed.** The consequences for this decision are three, and all
three are inputs to the ruling rather than parts of it: the Security Reviewer's
estimate rises to **3.5–4.5** reviewer-days (§9.2); **A-5.0-5** now requires a
`CAP_FOWNER`-bearing capability set and a disposable uid, and remains
**unconfirmed**; and the PERT estimate rises to **40.9**. **No decision number is
added, no option is added, and nothing here decides the question.**

**What revision 12 changes about this decision.** The *authorities*, *retention
rule* and *topology* are untouched, and options **B**, **C** and **D** are
unchanged word for word. Option A's content grows in three places, all of them
consequences of remediation R11-A: **a seventh table**, `approved_source_revisions`,
with its append-only trigger and grants; **four columns on
`sheet_writer_journal_generations`**, one of them a `NOT NULL` foreign key to it;
and **four provenance fields in the seal body**, with the writer step **W11a** and
the three fail-closed conditions **J-26 … J-28** that read them. A **new option
A-3** is raised above and **not adopted**. The consequences for the ruling are
four, and all four are inputs to it rather than parts of it: the Security
Reviewer's estimate rises to **4.5–5.5** reviewer-days over **twelve** surfaces
(§9.2); **A-5.0-5** now additionally requires a disposable object store, a
disposable approval record and the ability to run `id`, `namei -l` and `open` as
four named identities, and remains **unconfirmed**; the PERT estimate rises to
**47.6**; and a **third unrefused residual**, **R-5.0-15**, joins R-5.0-12 and
R-5.0-13 for the Acceptance Authority. **No decision number is added, and nothing
here decides the question.**

**What revision 9 changed about this decision, retained.** The *authorities*, *retention rule* and *topology* are
untouched, and options **B**, **C** and **D** are unchanged. Two things change.
**First, option A's content moves in two places and no others**: the deployment
digest becomes a value `init-generation` **computes and compares against the
deployed manifest at C0**, before anything consumes it — which adds a
specification (§2.13.2c) and a computation, and **no artifact, authority, column
or refusal code**; and the transient directories acquire an explicit **three-state
cleanup contract** whose failed-cleanup state **refuses and reports rather than
cleaning**, which **removes** a code path revision 8 had and adds an operator
procedure to WP-9. **Second, a new option A-2 is raised above**, because R8-D's
alternative to accepting the forged-host residual is a design-surface change that
§0.2 reserves to the Acceptance Authority. **Nothing here decides the question,
and no decision number is added** — A-2 is an option inside D5.0-13, not a new
decision.

**What revision 8 changed about this decision, retained.** The *options* are still the same four, and the
authorities, retention rule and topology are untouched. What changed is again the
**content of option A**, in three places and no others: **the order in which a
generation is created** — C0 keeps only pre-probe preconditions, C1 is the single
probe invocation, and a new C2 validates the result before any persistent
artifact, which adds a step number and no artifact; **Stage 4's target** — a
second transient directory `…/probe-ro` and a positive DAC control `S4-0`, which
adds a directory the constrained identity may write during provisioning and
nothing else; and **the threat model** — an eight-capability register in place of
two attacker classes, which adds no mechanism at all. Revision 7's own two
movements are retained below.

**What revision 7 changed about this decision, retained.** The
**content of option A** changed in two places: **where the probe's sandbox
stage runs** — at provisioning, inside the sealed report, which adds a root-run
transient unit and a deployed-unit precondition and removes a deployment-time
step — and **what the seal's binding section contains** — three authenticated
fields instead of five, of which two were unauthenticated. Both are corrections
to claims revision 6 made, not new capabilities. **Option B is unchanged by R6**;
options **C** and **D** are unchanged. **No new decision number is raised, and
nothing here decides the question.**

**What revision 6 changed about this decision, retained.** The *options* are the same four and the *authorities*,
*costs of retention* and *topology* are the same. What changed is the **content
of option A**: an acyclic construction in place of one that could not be built, a
readable seal in place of a contradiction, a valid and non-destructive probe in
place of one whose refusals proved nothing, and a registration that **records**
an attestation in place of a `CHECK` that was described as proving one. Two of
those are permission changes, so the security-review scope grows with them.
**Option B is marginally less bad than it was** — the writer's own **V-W** now
refuses a wrong deployment, a wrong host and a broken seal with no database at
all — and is still rejected for the reason §2.13.11 gives. **Option C and option
D are unchanged.** Nothing here decides the question.

### 5.4 What is deliberately **not** decided here

Restated so a reader can confirm none of it was absorbed: account vocabulary
(5.2), service-principal credential scope (OD-60), field authority (each owning
package's gate), the per-unit rollback data path (each owning package, against
the §2.6 contract in the schema), comparison-telemetry schema (5.1), and
production topology (unchanged; OD-20/21/22 stand).

---

## 6. Acceptance traceability

### 6.1 Deliverable → evidence

| # | Deliverable | Planned automated test or supervised check |
|---|---|---|
| 1 | Authority states, legal transitions, epoch arithmetic, fence-method vocabulary, **journal-generation chain arithmetic** | unit tests over every legal and every illegal pair, table-driven; epoch successor and genesis cases; **generation successor, first-generation and unsealed-predecessor cases**; the required-method set asserted equal in the trigger and the command |
| 2 | Migration `0014` | `TC-5.0-MIG-01…08`: empty apply, apply over fixtures, round trip, downgrade refusal after a move, restored-backup rerun, seed idempotence, four equal control totals, **and the generation table's chain, uniqueness and `CHECK` constraints exercised by direct statement** |
| 3 | The **five** commands | `TC-5.0-CMD-01…21`: valid authorize; valid observe; valid activate; valid abandon; **valid register-generation**; unauthenticated, ordinary, Council-only and revoked-administrator refusal at **each** step; stale predecessor; illegal transition; backdating; retry; conflicting key reuse; two concurrent callers; **a generation whose predecessor is unsealed, and a second unregistered chain head**; injected effect/audit/commit failure at each write |
| 4 | **The database authority fence** | `TC-5.0-FEN-01…08`: a write to a `legacy` unit refused; to a `shadow` unit refused; to a `cutover` unit permitted; a transaction opened at `cutover`, held across an activation of `→ legacy`, then committed — **refused**; the same with two connections and a barrier; the runtime role unable to alter a disposition to defeat the trigger; startup refusal in each of the three processes when a unit's authority names an unserved store; the refusal codes asserted |
| 5 | **The separately terminable Sheet writer** | `TC-5.0-SW-01…13`: the two call sites produce byte-identical `batch_update` payloads to today's characterization; the writer terminated mid-operation; a `SIGSTOP`ped writer terminated by the unit stop and the cgroup asserted empty; the bot online and refusing affected mutations with a typed message while the writer is down; the writer's failure surfaced without exception text; an out-of-systemd duplicate detected by the host scan; the credential absent from the bot process's environment; **and six added in revision 4** — an explicit request timeout honoured (N5.0-19); a `SIGTERM` drain refusing new work; a drain completing an outstanding call and recording its outcome; a journal entry present after a `SIGKILL` between the `fsync` and the dispatch; a killed writer leaving an unresolved entry; and the journal proved append-only against the writer's own identity. **The journal's own evidence is deliverable 13's `TC-5.0-JNL` band**, not this one |
| 5b | **The coordinator host boundary** (§2.12) | `TC-5.0-HB-01…10`: a peer connection as the coordinator role attempted and refused under each of `discordbot`, `freedomweb`, `freedomsheet` and `foundry`; the dedicated identity accepted on the socket; the same identity refused over TCP with and without a password; `sudo -l -U` empty for each service identity; a write into the root-owned deployment path refused under each service identity; `PYTHONPATH` supplied through `sudo` absent from the recorded `sys.path`; no `sys.path` entry writable by any service identity; and a `pg_ident` rotation exercised in both intermediate states. **Requires A-5.0-4** |
| 6 | ~~Telemetry~~ | **Withdrawn (OD-55).** Package 5.1's evidence |
| 7 | Coordinator command | `TC-5.0-OPS-01…16`: authority, refusal, exit codes, safe output, non-interactive recovery, preview/authorize agreement, stale preview, `status` output, abandon after deadline, a non-clear observation refused and **not** recorded, activation refused with an incomplete fence, the command's connection asserted to use the coordinator principal, **`dispatch_journal_clear` refused while the unresolved set is non-empty (N5.0-20), the unresolved-set listing naming ranges and digests but no cell values, `diagnostics` output, and both divergence re-reads** |
| 8 | Monitoring | `TC-5.0-MON-01…09`: never-run, healthy, pending, fence-incomplete, writer-down, past-deadline, rolled-back, **no current registered generation, and a generation registered after the pending revision's evidence**; and an assertion that no name, balance or exception text appears |
| 9 | Contract | reviewed document; every threshold a number; the telemetry contract present with 5.1 named as its implementer |
| 10 | Operations document | **supervised rehearsal**, witnessed by the Operations Owner, including a drain proof, a termination proof, an access revocation, an unresolved-set adjudication, both divergence re-reads and a rollback |
| 11 | Google-access margin | WP-13's measured propagation and restore latency against a disposable spreadsheet, recorded with its method, sample count and distribution — **and with the sentence that a measured distribution is not a maximum, in the same paragraph as the number** |
| 12 | Submission | the gate package |
| **13** | **The journal's durable storage and lifecycle** (§2.13) | **`TC-5.0-JNL-01…26`**, mapped one test per bullet of the R4 evidence plan in §2.13.8: the filesystem and attribute probe; the reboot cases; the restart case; the nine condition refusals; the ten-row manipulation matrix under the `freedomsheet` uid; the two `SIGKILL` boundaries; disk-full and `fsync` failure; the outcome-append failure; rotation and generation change; the observation's bindings; stale-evidence refusal after a rotation; and five activation-trigger refusals. **Two of them — a real boot and a real `fsync` failure — need a supervised host action or fault injection and are named as such, never assumed** |
| **14** | **The reviewed-source provenance contract** (§2.12.5a) | **`TC-5.0-JNL-51`**, eight cases: the ordered walk of Algorithm **D**; a missing approval record; a commit absent from the root-owned object store; a tree whose content does not reproduce the approved source-manifest digest — **the check that does not rest on SHA-1**; a dependency-lock mismatch; an unaccounted file, refused at **D5** before installation and at **D7** after it with a rollback; **the omission test — the provenance step skipped, `init-generation` refused at C0, no artifact, no row, activation unreachable, and a direct registration refused by the `NOT NULL` foreign key under both the coordinator role and the schema owner**; and a syscall trace proving the deployment reads no path in the group-writable worktree. Plus **`TC-5.0-JNL-46`** cases (f) … (i) inside Algorithm C, and **`TC-5.0-JNL-53`** for conditions `J-26 … J-28` |
| **15** | **The canonical identity and group membership table** (§2.12.2) | **`TC-5.0-JNL-52`**, eight cases: `getent group` for every group matching the table **exactly**, then positive and negative `id`, `namei -l` and `open` evidence for `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`, with the last two carrying traverse-to-parent controls so their denials are attributable. This is the security review's check **C-4** |

### 6.2 Plan §13.2 mandatory-scenario matrix

Every row is present. A `not applicable` row carries a written rationale for the
Independent Reviewer's acceptance, as §13.2 requires; it is never omitted.

| §13.2 scenario | Disposition |
|---|---|
| insufficient resources | **Not applicable.** This package moves no resource and has no balance. Rationale: the control plane records authority, not quantity; the first resource movement is 5.2's |
| invalid and negative values | **Covered.** Illegal transition, unknown unit key, blank reason, blank gate reference, blank `observed_detail`, over-long fields, `effective_at` before `created_at`, `activation_deadline_at` before `effective_at`, `verification_until` before `effective_at`, negative epoch, a non-`clear` observation |
| duplicate Discord interaction | **Covered by analogy, and stated as such.** There is no Discord surface; the equivalent is a duplicated operator invocation, tested as an identical retry returning the stored receipt, and a duplicated observation refused by `(revision_id, fenced_writer, fence_method)` |
| double approval | **Covered.** Two authorizations against one disposition; one commits, one is refused by `uq_…_previous_disposition`. And two concurrent activations of one revision; one commits, one is refused by `uq_…_revision` |
| stale optimistic version | **Covered.** A preview taken against disposition *D*, another change applied and activated, then the first authorization refused |
| concurrent trade/edit | **Covered.** Two concurrent callers, two connections, one barrier, one durable revision |
| partial external failure | **Covered.** Injected failures at each of the effect, receipt and audit writes, for each of the **five** commands; no partial state, no false success. Plus a Sheet-writer failure mid-fence, a Drive-permission call that errors, and — new in revision 5 — a journal `fsync` failure, a full filesystem and a failed outcome append (§2.13.6 **J-13 … J-15**) |
| authorization denied | **Covered.** Unauthenticated, ordinary member, Council-only, revoked administrator — at authorize, observe **and** activate, each applying nothing and leaking nothing |
| guild role removed | **Covered.** Authority is resolved at execution; an administrator whose capability was withdrawn between steps is refused at the next |
| Actor renamed | **Not applicable.** No character identity is resolved by name anywhere in this package, and no character is referenced at all. Rationale: OD-42's failure mode cannot arise where no name lookup exists |
| Foundry duplicate/missing mapping | **Not applicable.** No Foundry surface. Rationale: this package neither reads nor writes a snapshot |
| malformed or tampered Foundry snapshot | **Not applicable**, same rationale |
| migration failure and recovery | **Covered.** §6.1 row 2, plus the restored-backup rerun and the post-restore `status` step |
| mission settlement affecting multiple characters | **Not applicable.** No mission surface. Rationale: Phase 8 |
| correction after approval | **Covered.** A rollback revision and an abandonment, both appended, neither rewriting a predecessor |
| attendance reconnect and late join | **Not applicable.** No attendance surface |
| unsupported Foundry version | **Not applicable**, as above |
| pinned catalogue snapshot and checksum | **Not applicable.** No catalogue; package 5.6a |
| idempotent catalogue re-import; stale/concurrent preview refusal | **Half applicable.** No catalogue, but stale/concurrent preview refusal **is** tested |
| malformed/duplicate/removed/renamed/ambiguous upstream item records | **Not applicable.** No upstream item source |
| source disablement with retained inventory | **Not applicable.** No inventory |
| unique-item transfer; concurrent consumable use | **Not applicable.** No items |
| stale crafting project | **Not applicable.** No crafting |
| atomic craft completion | **Not applicable.** No crafting |

### 6.3 Plan §13.2 per-package persistent-state matrix

| Required item | Disposition |
|---|---|
| valid preview/apply and deterministic before/after facts | preview renders current authority, proposed authority, epoch, earliest activation instant, activation deadline, verification-window end, whether the transition requires an external-writer fence, which fence methods are outstanding, and the disposition it is fenced against; authorize records exactly those; `status` renders which methods have been observed and which have not |
| unauthenticated, unauthorized, cross-object and revoked-role denial | all four, at authorize, observe and activate, including an attempt to change a unit owned by another package — refused for the same reason, since no caller is scoped to a subset of units |
| invalid, boundary, negative, oversized and unknown input | §6.2 row 2, plus an unknown `unit_key`, an unknown `fence_method`, an activation at exactly `effective_at`, an activation one microsecond before it, and an activation at exactly `activation_deadline_at` |
| duplicate request, retry, stale optimistic version, two concurrent actors | all four, against real PostgreSQL, for authorize, observe and activate separately |
| database uniqueness, FK, check and append-only enforcement **against PostgreSQL** | every constraint in logical schema §3.3, §3.4, §3.5, **§3.7 and — new in revision 12 — §3.8**, exercised by direct statement, not through the service — including the **`NOT NULL` foreign key** to `approved_source_revisions` and the composite provenance foreign key, each refused under the coordinator role **and** the schema owner (`JNL-51` case (g), `JNL-53`), and the fifth append-only trigger; and the activation trigger's four preconditions each falsified individually |
| application and database runtime-role attempts to bypass history or authorization | §6.5's principal matrix in full |
| **fencing, drain and clock** | §6.1 rows 4, 5 and 13, and §6.5. **No clock-injection band exists**, because no fencing decision measures elapsed time in a process — the withdrawal is deliberate and is stated rather than omitted. The journal's own timestamps are diagnostic only, and §2.13.6 row **J-21** refuses rather than reasons about them |
| **durable evidence storage and its lifecycle** | §6.1 row 13 and §6.5 items 12–14. Every one of the fifteen conditions the R4 handoff enumerates is a row of §2.13.6 with a test, and **no row resolves to "continue"** |
| parser/external, mid-transaction, audit-write and commit failure | injected at each write; no partial state and no false success |
| migration dry-run, idempotent rerun, every source row accounted for, unresolved records, rollback, restored-backup rerun | §6.1 row 2. *Unresolved records:* the only source is the controlled manifest, and a manifest entry with no seeded unit fails the suite |
| safe monitoring states and logs without secrets or unrelated player data | §6.1 row 8, plus an assertion that `observed_detail` never carries credential material |
| a synthetic staging end-to-end path plus the named supervised operational checks | the WP-9 rehearsal: seed → shadow → fence → cutover → verification → rollback → restore, on the disposable database, witnessed |

### 6.4 Plan §13.3 review-gate evidence

Committed for the submission: the traceability tables above; unit and application
tests; repository/contract tests proving the same transaction and audit behaviour
for the fake and the PostgreSQL adapter; PostgreSQL integration tests for
migrations, uniqueness, foreign keys, the activation trigger, the authority-fence
trigger, optimistic concurrency, idempotency, rollback and append-only
immutability under every principal; multi-process tests for termination and
duplicate detection; CLI-surface tests for authority, refusal, exit codes, safe
output and non-interactive recovery; deterministic synthetic fixtures with no real
character data; the narrow suite then the full configured suites with exact
commands and results; `compileall` under both interpreters and `git diff --check`;
an explicit statement that no formatter, linter or type checker is configured;
diff review for secrets and unsafe logs; and recovery documentation exercised
against the disposable environment.

**No web surface and no Discord surface exists in this package**, so the §13.3
web and Discord evidence bands are recorded as not applicable with that rationale
rather than omitted.

### 6.5 The handoff's required evidence plan

The nine items the handoff names, each with the test that produces it. These are
additional to §6.2 and §6.3, not a restatement of them. **Twenty-two items in
revision 12**, up from twenty: R10 corrected how an identity is constructed and
which identity is a control and added no item, while **R11 adds two — the
reviewed-source provenance chain, and the canonical membership table** — because
each answers a security-review finding with evidence that did not previously
exist.

| # | Required evidence | Planned test |
|---|---|---|
| 1 | **A process paused after its final admission check and resumed after activation** | Two tests, one per store. *Database:* a transaction opened while the unit is at `cutover`, held by a barrier across an activation of `cutover → legacy`, then committed — the authority-fence trigger refuses it, and the assertion is on the refusal, not on a log line. *Sheet:* a harness writer `SIGSTOP`ped mid-operation, then stopped through its unit; the cgroup asserted empty; the process asserted gone, so no resume is possible. **Added in revision 4:** the same writer with an outstanding call, drained instead of killed, asserted to have recorded the response outcome before exit |
| 2 | **An out-of-systemd duplicate legacy writer** | A second writer started outside systemd; `host_scan_clear` refuses and records nothing; the coordinator refuses to proceed; separately, a revoked-access simulation asserts the duplicate's write is refused at the API boundary |
| 3 | **A request already at the irreversible external-call boundary** | **Rewritten in revision 4, because the revision-3 test asserted a property §2.10.2 says cannot be established.** Four assertions replace it: *(a)* a journal entry exists **before** dispatch, proved by killing the harness writer between the journal `fsync` and the call and finding the entry; *(b)* a drained writer's outstanding call is completed and its outcome recorded; *(c)* a killed writer's outstanding call leaves an **unresolved** entry, the coordinator refuses to record `dispatch_journal_clear`, and the activation is refused (N5.0-20); and *(d)* a call dispatched after revocation is refused at the API boundary. **No test asserts that a dispatched call has completed**, because nothing can |
| 4 | **One runtime process attempting to update, release or fence another process's lease** | **Recorded as unconstructable**, with the grant proof that makes it so: there is no lease table, and `has_table_privilege` asserts the runtime role holds nothing on the evidence table |
| 5 | **One runtime process attempting to acknowledge for another process** | **Recorded as unconstructable**, same proof. No process attests anything, for itself or for another |
| 6 | **Direct SQL attempts under every proposed database principal** | A matrix test: `freedom_runtime_test` × **seven** tables × `INSERT`/`UPDATE`/`DELETE`/`TRUNCATE`; the schema owner × **five** append-only tables × `UPDATE`/`DELETE`; the coordinator × **five** tables × `UPDATE`/`DELETE`/`TRUNCATE`; **and — new in revision 12 — an `INSERT` into `sheet_writer_journal_generations` naming an unapproved source revision, under the coordinator role and under the schema owner, refused by the `NOT NULL` foreign key**. Every cell refused, with the refusing mechanism named. *Six / four / four before revision 12 added the seventh table* |
| 7 | **Activation with forged, missing, stale and cross-instance proof** | *Forged:* unconstructable, with the grant proof. *Missing:* three of four methods → refused. *Stale:* evidence older than N5.0-16 → refused; evidence predating `revision.created_at` → refused. *Cross-revision:* another revision's evidence → refused by foreign key |
| 8 | **Failed shutdown/restart and rollback** | A stop that leaves the cgroup non-empty → coordinator records nothing → activation refused; a writer that fails to restart → outage asserted, authority unchanged, `/healthz` reports it; a complete `cutover → legacy` rehearsal in WP-9 |
| 9 | **Proof that the chosen fence prevents the old writer from acting, rather than that monitoring notices it afterwards** | **For the database path this is met:** item 1's held-transaction test — the write never commits, and the assertion is the absence of the row. **For the Sheet path it is not met, and revision 4 says so rather than substituting a weaker test for it.** What is proved is the absence of the process (item 1), a refusal at the API boundary after revocation (item 2), a refused activation while the unresolved set is non-empty (item 3c), and a detected divergence (item 10). What is *not* proved is that no accepted request applies later — §2.10.2. **No monitoring assertion is offered as fencing evidence anywhere in this matrix**, and `/healthz` is tested as a detector only |
| 10 | **New in revision 4: the post-import divergence re-read** | The fenced ranges are mutated out-of-band after the final import in a harness; both re-reads (import + N5.0-18, and end of the N5.0-4 window) report the divergence; the rollback path refuses to replay until the report has been produced (W-6) |
| 11 | **New in revision 4: the host boundary** (R3-B) | Each of `discordbot`, `freedomweb`, `freedomsheet` and `foundry` attempts a peer connection as the coordinator role and is refused; the dedicated identity succeeds on the socket and is refused over TCP with and without a password; `sudo -l -U <identity>` lists **neither `Cmnd_Alias`** for every service identity **and an unauthorized `freedom-journal-admin` invocation is refused** (the two rows revision 5 adds); a write attempt into the root-owned deployment path fails with `EACCES` under each service identity; `PYTHONPATH` supplied through `sudo` is asserted absent from the recorded `sys.path`; and **no entry on that `sys.path` is writable by any service identity**. Requires assumption A-5.0-4. **Otherwise unchanged from revision 4**, as the R4 handoff requires |
| 12 | **New in revision 5: the journal's storage and integrity** (P5.0-R5 items 1, 2 and 4) | `TC-5.0-JNL-01` proves the journal path is on a **non-`tmpfs`, block-backed** filesystem and that the §2.13.2a Stage-2 cases behave as stated; `JNL-04 … 12` prove that each of the nine named bad states **refuses clear evidence**; `JNL-13` proves the **thirteen-row** manipulation matrix under the `freedomsheet` uid; `JNL-16`, `JNL-17` and `JNL-18` prove that disk-full, an `fsync` failure and an outcome-append failure each **prevent a dispatch or leave an unresolved entry**, with the Sheets client asserted not to have been called |
| 13 | **New in revision 5: the generation lifecycle** (P5.0-R5 items 3 and 5) | `JNL-02a`/`JNL-02b` prove an unresolved entry survives a process kill and — supervised — a host reboot; `JNL-03` proves a restart cannot reset a non-empty or indeterminate generation; `JNL-19` proves rotation preserves prior evidence, that `init-generation` refuses while a predecessor is unsealed, and that **no sequence of privileged commands produces an empty history without first sealing and archiving the one it replaced**; `JNL-20` proves the observation binds generation, inode, content digest, writer unit, deployment digest and time; `JNL-21` proves a rotation, restore or rollback **invalidates prior clear evidence** |
| 14 | **New in revision 5: activation refuses bad journal evidence** (P5.0-R5 items 4 and 6) | `JNL-22 … 26`: activation attempted with **missing**, **stale**, **cross-generation**, **corrupt** and **incomplete** journal evidence, each refused by the activation trigger with its named reason, and each asserted against real PostgreSQL rather than through the service |
| **15** | **New in revision 6: the probe is valid, attributable and safe** (R5-C) | `JNL-27` proves the **control stage** — the same six operations succeed as `freedomsheet` without `+a`, and a failing control case yields **`inconclusive`**, never `passed`; `JNL-28` produces `EACCES`, `EROFS` and `EPERM` deliberately and classifies each, and classifies `ENOTTY` as a **failed** probe; `JNL-29` separates the systemd sandbox from the filesystem; `JNL-30` proves the privileged cleanup, the residue path and the two refusals that guard it; **`JNL-32a` proves by syscall trace that a writer start reaching W18 performs no destructive operation against the journal, seal or archive and appends exactly one `startup` record, and `JNL-32b` proves that with `+a` absent the start refuses at W9 with `SW-J06` before W17, opens the journal for writing not at all, appends nothing, and leaves the journal, seal and archive byte-for-byte unchanged** |
| **16** | **New in revision 6: the construction is acyclic, the permissions match the duties, and the database claim is honest** (R5-A, R5-B, R5-D) | `JNL-31` re-derives the genesis record from the seal body with an **independent implementation**, byte for byte, and asserts the seal body contains none of `genesis_record_digest`, `journal_device`, `journal_inode` or `seal_digest`; `JNL-33` proves the writer's seal access is exactly *read* and that the full **V-W** algorithm completes using only it; `JNL-34a`, `JNL-34b` and `JNL-35 … 45` are §2.13.5c's **thirteen independent falsification rows** — seal body, seal-plus-record-0, genesis, registered digests, predecessor close manifest, inode, deployment digest, host identity, probe report, the three binding fields and a planted `sealed_at` — each refused at the boundary the matrix names. *Revision 7 counted these as twelve while listing thirteen; the count is corrected in revision 8;* and the §2.13.8a division is asserted case by case, including that a row **can** be inserted with a well-formed but false probe digest and that both the writer and the coordinator then refuse it |
| **17** | **New in revision 7: the claims are bounded to what the artifacts do** (R6-A, R6-B, R6-C) | `JNL-29` asserts the probe report contains **all four stages** and that `append_only_probe_digest` is computed over exactly those bytes, so no digest is described as covering bytes it does not contain; `JNL-42 … 45` alter `BND.genesis_record_digest`, `BND.journal_device` and `BND.journal_inode` **independently** and plant a withdrawn `sealed_at` field, each refused by a named **V-W** step; **`JNL-34b` asserts the case the writer does *not* refuse** — an `A1 + A2 + A3` rewrite of the seal body and record 0 together (`K1 + K3` in revision 8's withdrawn register) — and asserts that the coordinator refuses it against the registered digests, so §2.13.5c's narrowed F-1 is falsifiable in both directions; and `JNL-32a`/`JNL-32b` assert the two startup branches with their opposite expectations |
| **18** | **New in revision 8: the order is executable, the negative has a positive control, and the threat model is stated in capabilities** (R7-A, R7-B, R7-C) | `JNL-46` walks Algorithm C **C0 … C13** and asserts, for every value in the dependency table, that it exists, is final and has passed its validation before it is consumed — with **C0 reading no probe result** and **C1 the only creation point of `PR`**; `JNL-47` injects a failure in each of Stage 1 … Stage 4 and cleanup and asserts that **no journal, seal, symlink or registration row is created**; `JNL-48` proves **S4-0** on the exact `…/probe-ro/s4-2.target` and distinguishes the four outcomes the handoff enumerates — positive DAC success outside the sandbox, `EACCES` from DAC, `EROFS` from the systemd bind, and cleanup failure or residue; and `JNL-49` and `JNL-50` give one case per feasible capability/artifact pairing, the three combined-authority residuals including the one this design does **not** refuse, and an executed assertion for every not-constructible cell |
| **19** | **New in revision 9: the validations are against independent sources, one failure has one outcome, the authorities are separated from the flag, and the undetected case is named** (R8-A, R8-B, R8-C, R8-D) | `JNL-46`'s five cases assert **I-1 … I-5** and refuse a malformed digest, a wrong digest and a deployment changed between **C0** and the probe — the first two at **C0**, before anything consumes the value, which is what revision 8 could not do; `JNL-47`'s six cases separate the four probe-stage failures with cleanup succeeding from the **two** cleanup failures with deterministic residue, asserting exit status, safe path reporting, generation and database absence, residue state, next-run refusal and operator recovery for each, so **no two artifacts require mutually exclusive states**; `JNL-49` and `JNL-50` execute the corrected minimum **combinations** under identities and ambient capability sets that really hold them, including a **non-root `CAP_LINUX_IMMUTABLE`-only** identity that clears `+i` and then receives `EACCES`, which is the executed proof that **flag control confers no DAC**; and `JNL-40`'s two cases assert the **unforged** host-identity refusal and the **forged-matching residual** in which neither W10 nor C-d refuses — with the rule that no case may assert a C-d refusal without naming the field whose inherent mismatch this threat proves |
| **20** | **New in revision 10: every kernel prerequisite is named, and every negative capability case is isolated with a positive control** (R9-A, R9-B, R9-C) | §2.13.5c states the checks `FS_IOC_SETFLAGS` actually makes **before** the register that encodes them, splits **A1** from the owner authorizations **A10** and **A11**, and adds a **holder table** so detector reach is assessed against the smallest identity that can really hold each combination as well as against the combination itself. `JNL-50` case 6 is the isolating control: identity **E4** holds `CAP_LINUX_IMMUTABLE`, `CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH`, **opens the root-owned archived file successfully**, and receives **`EPERM`** from the flag clear — with **E6**, which differs only by `CAP_FOWNER`, issuing the identical call and **succeeding**, so the refusal is attributable to the owner check and to nothing else. `JNL-50` case 3 does the same for `A1` against the writer's **own** inode, where the owner half is satisfied by ownership and the capability is the only missing prerequisite, with **E2** as its positive control. `JNL-49` case 12 is the corrected form of revision 9's non-constructible claim: **E5** holds `CAP_LINUX_IMMUTABLE` **and** `CAP_FOWNER`, clears `+i` **successfully**, and is then refused **`EACCES`** on the open — the executed proof that flag authority confers no discretionary access. Every case asserts its identity's `Uid`, `Gid`, `Groups`, `CapPrm`, `CapEff`, `CapInh`, `CapAmb` and `CapBnd` from `/proc/self/status` **before** the operation under test, and a case whose identity assertion fails is **`inconclusive`** rather than a pass or a refusal |
| **21** | **New in revision 12: the deployment is bound to an immutable reviewed Git object, and omitting the binding refuses** (R11-A, security-review finding P5.0-SR1) | `JNL-51`'s eight cases walk Algorithm **D** `D0 … D8` and assert that the trusted manifest is computed **from Git object bytes** in a `0700 root:root` bare store addressed by object id, with **no ref, branch or tag resolved anywhere**; that an absent approval record, a commit absent from the store, a tree whose content does not reproduce `APR.source_manifest_digest` — **the check that does not rest on SHA-1** — a lock-hash mismatch, an unaccounted file and a post-installation mismatch each refuse with their own `DEP-xx` code, the last of them **rolling the deployment back to its predecessor**; and that **a complete deployment opens no path under the group-writable worktree**, by syscall trace. **Case (g) is the negative test the finding requires**: the provenance step is omitted, `init-generation` refuses at **C0** with `J-26`, the probe is asserted never to have run, no journal, seal, symlink, `.close` manifest or registration row exists, and **activation therefore cannot succeed** — and, separately, a generation whose seal names an unapproved revision is refused at **V-R** with `J-28` and by the `NOT NULL` foreign key issued as direct SQL under both the coordinator role and the schema owner. `JNL-46` cases (f) … (i) assert the same four refusals inside Algorithm C's ordered walk, and `JNL-53` asserts `J-26 … J-28` on both sides |
| **22** | **New in revision 12: every identity's group membership is what one table says it is, and its access follows** (R11-B, security-review finding P5.0-SR2) | `JNL-52`'s eight cases assert, first, that `getent group` for every group in §2.12.2 lists **exactly** the members that table records — **an unexpected member fails the case** — and then, per identity, a positive set and a negative set of `id`, `namei -l` and `open` evidence for **`freedomsheet`**, **`freedomcoord`**, **`discordbot`** and **`freedomweb`**. The positive halves for `discordbot` and `freedomweb` are **controls**: each is proved able to traverse to the parent and, for `freedomweb`, to write in the repository worktree, so the denials that follow are attributable to `…/journal`'s mode rather than to a path search or a broken identity. Together they are host check **`C-4`**, which §8.1 records as **not run** and which this evidence discharges once A-5.0-5 is authorized. **The three claims §2.12.2 states in place of the withdrawn isolation sentence are each asserted**: the shared group is read-only over one directory and one file; `freedomcoord` holds no write bit anywhere in the hierarchy; and no mechanism in this design decides who a process **is** from a group |

---

## 7. Risk and rollback plan

### 7.1 Failure modes and controls

| # | Failure mode | Control | Residual |
|---|---|---|---|
| 1 | **Partial commit** — effect without receipt, or effect without audit | one unit of work; three writes; commit or nothing. Injected-failure tests at each write, for each of the **five** commands | none inside one database. A crash between the client's commit request and its acknowledgement leaves the caller unsure; the retry path resolves it from the stored receipt |
| 2 | **Duplicate request** | `(scope, key)` unique plus the schema-versioned canonical digest; retry returns the stored receipt, conflicting reuse fails closed | a caller that generates a fresh key for a genuine retry gets a second attempt, which `uq_…_previous_disposition` then refuses. Two fences, deliberately |
| 3 | **Concurrent or stale authorization** | `previous_disposition_id` UNIQUE: one atomic `INSERT`, no read-then-write window | none. The loser is refused by PostgreSQL, not by a predicate |
| 4 | **Concurrent activation** | `revision_id` UNIQUE on dispositions | none, same shape |
| 5 | **Audit failure** | the audit row is in the same transaction as the effect; a failed audit write rolls the authority change back | none. This is what makes "every authority change is auditable" a property rather than a hope |
| 6 | **A future-dated revision takes effect early** | authority is read only from dispositions; a revision without one is authority for nothing; the activation trigger refuses before `effective_at` (logical schema §2.5) | none by construction. There is no query that could return a pending revision as authority, because the read does not touch that table |
| 7 | **A stale process writes PostgreSQL after authority moves** — *the P5.0-R1 case, database half* | the authority-fence trigger, evaluated inside the writing transaction. A pause of any duration changes nothing, because the check is not in the past | **none.** This is the half of R1 that is fully closed, and it is closed by the database rather than by the application |
| 8 | **A stale process writes the Sheet after authority moves** — *the P5.0-R1 case, legacy half* | the writer is **drained**, then terminated, then its Google write access is revoked; termination is observed at the cgroup level and by host scan; the dispatch journal is validated against its seal and its registered generation and must be clear | **R-5.0-5, unchanged:** the `host_scan_clear` observation is point-in-time, so a writer started between the scan and the activation is not observed, and it leaves no journal entry either |
| 8b | **A request Google accepted before the fence is applied after the final import** — *the P5.0-R1 case, and the one revision 4 concedes* | **None that prevents it.** §2.10.2 concludes no such control exists in the published API. What exists: the drain makes it rare (W-1/W-2), a non-empty unresolved set refuses the cutover (W-3), it cannot reach PostgreSQL (W-4), and the two re-reads find it (W-5/W-6) | **R-5.0-8, new. Not mitigated away.** This is the residual D5.0-9 / OD-62 asks the Acceptance Authority to accept, and the whole of §2.10 exists to describe it accurately |
| 9 | **An old build writes unfenced** — partial deployment | a build predating the fence still connects with the shared runtime role and is therefore refused by the authority-fence trigger for database writes; for Sheet writes, the deployment procedure requires the writer unit on the host before any unit is authorized out of genesis, and the coordinator refuses to authorize a non-genesis revision while the writer unit is absent | a second instance of a role started outside systemd. **R-5.0-5**, with an explicit process check in the cutover procedure |
| 10 | **Accidental dual authority by transition** | the transition reference table has no `legacy → cutover`, `legacy → database`, `shadow → database`, `cutover → shadow` or `database → shadow`; a unit cannot reach database authority without a shadow period and cannot re-enter comparison after it | a *human* can still edit a Sheet by hand. Nothing in software prevents that; OD-36's amendment already rules that it cannot affect PostgreSQL after cutover |
| 11 | **Failed deployment** | migration `0014` is additive and applies before the code that reads it; a process that cannot serve a unit's authority refuses to start rather than serving under the wrong one; the plan §14.2 ten-step gate is unchanged | a half-deployed estate refuses to start rather than running split. That is the intended failure direction and is stated so the Operations Owner expects it |
| 12 | **Database restoration** | `infra/postgresql/backup-restore-drill.sh`, unchanged, exercised in WP-9; restored evidence is stale by the N5.0-16 test and fences nothing; **the operations document requires an authority `status` check as the first step after any restore, before any service starts** | a restore to a point before a cutover, reconciled only by comparing the restored control-plane version against the change log. **R-5.0-3** |
| 13 | **Rollback to the Freedom bot and Sheet path** | `cutover → legacy` and `database → legacy`, the retained Sheet connector, credential and export (plan §15.1 stage 9), A-04, and the §2.6 rollback-data-path precondition that no unit enters `cutover` without an evidenced replay | it works only while the legacy path exists. Once §15.1's final gate closes, the transition rows must be removed by migration; until then **no Freedom-bot behaviour may be weakened, disabled or deleted** |
| 14 | **The fence itself refuses a healthy estate** | every refusal is fail-*closed* and typed; the operations document names the recovery; F-6 is the declared fallback if the writer unit is found defective | **R-5.0-1**, and it is why WP-4 and WP-4b's evidence exercises every process before any deployment |
| 15 | **The Sheet writer cannot be restarted after a cutover** | the fence held, so there is no integrity consequence; monitoring reports the missing writer; the bot stays online and refuses affected mutations with a typed message | **R-5.0-6, restated:** a bounded mutation outage that lasts until a human acts. **This is what D5.0-9 is accepting** |
| 16 | **The Google permission is not restored after a cutover** | the Sheet stays read-only for the service account: a fail-closed state. The cutover checklist's last step is the restore, and `migration_sheet_writer` reports a writer whose writes are failing | **R-5.0-7:** a forgotten restore is a silent mutation outage for every unit still at `legacy`. Detected by monitoring, not prevented |
| 17 | **A compromised service process rewrites the coordinator's code and has it executed with coordinator database authority** | the root-owned `/opt/freedom-blades/coordinator` deployment path, the digest comparison at deploy, `sudo`'s single fixed executable path, `env_reset` and `python -I -P` (§2.12.5, §2.12.6) | **The repository copy remains writable by `discordbot` and `freedomweb` (H-1)**, so a compromised process can still corrupt what a *future* deploy would copy. The digest comparison is what stands between that and execution, and the condition itself is raised as **D5.0-12 / OD-65** item 3 rather than fixed here |
| 18 | **The `pg_ident` map or either `sudoers` drop-in is edited or removed** | every such edit is a root action; all are recorded in the change log and re-verified by the WP-14 matrix after any change | a removal **prevents** cutovers and cannot enable one, so the failure direction is closed. An *addition* of a second system user to the map would widen the boundary silently; the operations document requires the map to be re-read and the matrix re-run after any PostgreSQL or `sudoers` change |
| **19** | **The dispatch journal is lost, replaced, reset or corrupted, and an unknown history reads as an empty unresolved set** — *the P5.0-R5 case* | **§2.13 in full.** Durable ext4 storage instead of `tmpfs`; a directory the writer cannot write, so it cannot unlink, rename or replace the file; `chattr +a` **probed, not inferred**; a `chattr +i` seal whose **derived** genesis digest must match record 0 (§2.13.5a); a registered generation the activation trigger checks; a hash chain and a sequence; and **twenty-five** conditions that all refuse | **R-5.0-10, new.** A writer whose **dispatch path itself** has been replaced can call Google without journalling. Nothing it authors bounds that; what bounds it is that the process is dead, its cgroup is empty and Google refuses its access — the four methods the writer does not author |
| **20** | **The journal filesystem fills, or an `fsync` fails, during normal operation** | the writer refuses to dispatch below **N5.0-21** and refuses for the life of the process after a failed `fsync` (rows **J-13**, **J-14**). It never dispatches a request it could not durably record first | **R-5.0-11, new.** Sheet mutations are unavailable until an operator acts. **This is the cost of fail-closed and it is named rather than discovered**: monitoring reports the writer, the bot stays online, reads and every non-mutating command are unaffected |
| **21** | **A privileged operator seals or disposes of a journal generation to make a history disappear** | `dispose` refuses without N5.0-23, plan §15.1's gate, a Data Owner approval reference and a passing `archive-verify`; `seal` preserves the file immutably in an archive the writer cannot read; every act is in `sudo`'s `log_output`, journald and `audit_events` | **not prevented against root**, and the design says so: root is above every boundary here, exactly as §4.3.5 already records for the coordinator. What exists is that the act is deliberate, gated on an approval reference, and leaves three independent records |
| **22** | **New in revision 6. The journal's own integrity machinery is wrong** — the digests cannot be constructed, the validator cannot read what it must validate, the capability probe measures the wrong thing, or a database constraint is credited with proving a host fact | this is the P5.0-R5 re-review, and the controls against it are **tests, not arguments**: `JNL-31` re-derives the genesis record with an independent implementation and asserts the seal body excludes the four downstream values; `JNL-33` runs the whole of **V-W** using only the read the writer is granted; `JNL-27` refuses to interpret a refusal until the control stage passes; **`JNL-32a` and `JNL-32b` prove startup is non-destructive in both branches — one appended `startup` record with `+a` present, and, with `+a` absent, a refusal at **W9** before **W17** that appends nothing at all**; and §2.13.8a's division is asserted case by case | **not fully prevented.** A design error of this class is caught by a reviewer or by one of those tests, and revision 6 exists because a reviewer caught four of them. What has changed is that each is now a **named falsification case** rather than a property a reader had to re-derive from prose |
| **23** | **New in revision 7. The specification describes its own artifacts more strongly than it builds them** — a digest said to cover bytes it does not contain, a refusal claimed for an actor the algorithm gives no means to detect it, or a test expecting a state its own algorithm refuses to produce. **All three occurred in revision 6** (R6-A, R6-B, R6-C) | **stop condition 10h**, which forbids the claim class outright; §2.13.5c, which now names the **attacker capability** each refusal holds against instead of asserting the refusal alone; §2.13.5b's binding table, which enumerates every field and the step that authenticates it; and three tests written to the exact boundary — `JNL-29` (the digest covers four stages), `JNL-34b` (the case the writer does **not** refuse) and `JNL-32b` (the branch that appends nothing) | **not prevented, and it is the residual this package has actually realised twice.** What bounds it is that each claim now has a falsification case that fails if the claim drifts, and that the ones the writer cannot make are written down as limits rather than omitted |
| **24** | **New in revision 8. An attacker holds both a falsifiable artifact and the artifact that would detect it** — specifically **`A1 + A2 + A3 + A9`** (§2.13.5c; `K1 + K3 + K8`-mutation in revision 8's withdrawn register): root on the host, so the seal and record 0 can be rewritten consistently, **and** a PostgreSQL superuser, so the registered digests can be changed to agree. This is the only combination in the capability register for which no actor in this design holds an independent copy | **None that prevents it, and revision 8 says so rather than describing a refusal that does not exist.** What exists is detection and record: `sudo`'s `log_output`, journald, the `audit_events` chain, the offline backups of the generation table, and the fact that a forged head has no `seal` record, no `.close` manifest and no archive behind it (`JNL-49` cases 6 and 7) | **R-5.0-12, new.** Accepted or rejected as a residual, not closed by implementation. It is the honest edge of a design whose whole integrity argument is *two authorities that must agree*: when one attacker holds both, agreement proves nothing, and the only remaining evidence is external to both |
| **25** | **New in revision 9. A forged matching host identity is invisible to every check in this design** — an actor holding **A6** (§2.13.5c) restores the journal tree onto a host it controls and rewrites `/etc/machine-id` there to the value the seal records. `SB.host_machine_id`, `/etc/machine-id` and the registered row then carry the **same** value, so **W10 passes and C-d has nothing to disagree with** | **None that detects it, and revision 9 says so rather than naming a detector that cannot fire.** *Revision 8 recorded a coordinator refusal here; it is withdrawn.* What bounds the consequence is that the restored tree carries **no production database**, so the forgery has no effect until its holder also reaches the coordinator (**A8**) and, to change what is registered, holds **A9**; and what remains as evidence is `sudo log_output`, journald, the `audit_events` chain, the production host's own systemd and deployment records, and the absence of a `seal` record, `.close` manifest and archive behind a forged head | **R-5.0-13, new.** Accepted or rejected as a residual, not closed by implementation. The design change that would close it — an independent authenticated host-bound value — is routed as **D5.0-13 / OD-66 option A-2** and is deliberately **not adopted**, because it changes the design surface and is the Acceptance Authority's under §0.2 |
| **26** | **New in revision 9. A failed privileged cleanup leaves a writer-writable transient directory in the state hierarchy** — §2.13.2b state **S-B**. `…/probe` or `…/probe-ro`, `root:freedomsheet 0770`, persists until an operator acts, and while it does, **no generation can be created** | the residue is reported by absolute path with its failed operation and `errno`; the exit code is distinct from every other failure; **both `verify-capability` and `init-generation` refuse while it exists, and neither cleans it**; the deployed writer unit's `ReadWritePaths=` names neither directory, so the writer inside its own unit cannot reach the residue even though its identity owns the directory's group; and the operations document names the recovery steps | **R-5.0-14, new.** An **availability** cost, not an integrity one: the directories hold no evidence and are referenced by no seal, manifest or row. It is deliberately preferred to an automatic clean, which would delete a writer-writable directory on a routine path (stop condition **10f**) and would mask a failure nobody investigated |
| **27** | **New in revision 10. The design states a kernel or platform requirement incompletely, and a control is then credited to the wrong mechanism** — the R9-A defect. Revision 9 recorded `CAP_LINUX_IMMUTABLE` as the requirement for an `FS_IOC_SETFLAGS` flag change and omitted the owner-or-`CAP_FOWNER` check the same ioctl makes, so eleven falsification rows named an incomplete combination and two evidence cases asserted an `errno` the kernel does not return | **stop condition 10m**, which requires every operation this package reasons about to name **all** of its kernel prerequisites before any row depends on it — §2.13.5c now states them in a table of their own; **stop condition 10k as extended**, which forbids crediting a capability with a check it does not satisfy; and, executably, the rule that **every negative capability case runs with all other prerequisites satisfied and carries a positive control that succeeds** (`JNL-50` cases 3, 6 and 7 with controls **E2** and **E6**), so a refusal can no longer be attributed to the wrong check | **not prevented, and it is the class this package has now realised three times** — a hash order that could not be evaluated, a capability credited with access it never had, and a capability credited with a check it never satisfied. What bounds it is that a claim of this kind now has to survive an **executed** case under an identity that really holds only what the row claims, and that the identity itself is asserted from `/proc/self/status` before the case runs. **It is not a new residual**: every correction here makes an alteration harder to construct, so no guarantee moves and no risk row is added to §7.4 |
| **28** | **New in revision 11. A specification declares a state its own recipe does not produce, because the recipe was written against a model of the tool rather than against the tool's documentation** — the R10-A/R10-B defect. Revision 10 built five of eight identities with a `setpriv` securebit the installed manual page lists as *not allowed*, asked all five to **add** to a bounding set the same page says cannot be added to, left a sixth identity's bounding set undropped and a seventh's inheritable and ambient sets written as dashes. **Each of those four is a single-sentence contradiction of a manual page present on the host**, and none was caught, because the declared masks and the recipes were written side by side and never compared | **stop condition 10n**, which requires every declared capability mask to be **derived** from the invocation that produces it — option by option, against the named tool's documented semantics — and forbids constructing an identity with a mechanism whose **ordering** that tool's documentation does not determine; §2.13.5c's **mask-versus-recipe comparison table**, which carries that derivation in the document rather than in the reviewer's head; and the harness's **`inconclusive`** rule, which is what would have surfaced the defect at the first execution rather than at the second review | **not prevented, and the honest statement is that this is the fourth realisation of one family.** Defects 20–21, 22–24 and 25–28 are the same shape at three depths: a claim about a *mechanism* written from a model of it. What bounds it is narrow and worth stating narrowly — a derivation table costs nothing to check, and a tool's own manual is the cheapest independent source this package has. **It is not a new residual and no guarantee moves**: an identity that could not be built proved nothing either way, so nothing that revision 10 claimed on its strength was ever claimed as evidence. **A-5.0-5 is unconfirmed and every case remains unrun** |
| 29 | **New in revision 12. An integrity control's trusted side comes from the artifact it is checking** — the P5.0-SR1 defect. Revision 11 verified a deployment against a digest of that same deployment and called it a comparison with the reviewed commit; the reviewed commit appeared nowhere in any artifact, precondition or refusal | **§2.12.5a**: the trusted side is computed from **Git object bytes** for a commit an out-of-band, root-owned approval record names, in a store no service identity can read or write; the deployed side is compared against it at **D7**, at **C0** and at **W11a**; and the database holds a fourth copy the host cannot write. **Omission refuses at C0**, so the control cannot be skipped without a refusal | **The approval record's own integrity is root ownership and mode — R-5.0-15.** An actor holding **A5** rewrites every host copy; an actor holding **A5 + A8** also registers the revision it approved. That boundary is operator trust, and the signed alternative is routed as OD-66 **option A-3** and not adopted |
| 30 | **New in revision 12. The same fact is stated in more than one place and the copies disagree** — the P5.0-SR2 defect. Revision 11 stated `freedomjournal`'s membership in three passages, denied it in a fourth, and carried the contradiction through five revisions and three independent re-reviews without either contract's consumer noticing | **§2.12.2 is the single place a membership is stated**, and §2.13.3, §2.13.5c, §2.12.6, §2.12.7, §2.13.7 and logical schema §4.3.2 cite it rather than restating it. **Stop condition 10p** makes a membership stated elsewhere a defect, and `JNL-52` asserts the table against `getent group` and `id` before any access case runs | **The rule binds memberships, not every duplicated fact.** This package still states digests, modes and paths in more than one place; what makes membership different is that a wrong copy silently changes who can read evidence. A general single-source rule is not proposed here and is not claimed |

### 7.2 The cutover and rollback sequence — the boundary as it actually is

Written here in operational order; WP-9 turns it into
`docs/operations/migration-cutover-and-rollback.md` and rehearses it. The
protocol is identical for a cutover and for a rollback, which is the point: there
is no unfenced emergency path.

**Preconditions, checked and recorded before anything is authorized.**

1. The `freedom-sheet-writer` unit exists on the host and is the only holder of
   the Google write credential. The coordinator command refuses otherwise.
1b. **A journal generation is registered, current and unsuperseded**, its seal
   parses, its `(device, inode)` and genesis digest match the file on disk, and
   its probe report re-derives and matches the registered
   `append_only_probe_digest`. The coordinator command refuses otherwise, and
   `/healthz` `migration_journal_generation` reports it (§2.13.5, §8.4).
2. All services run a build whose database writes pass the authority-fence
   trigger. (A build that does not is refused by the trigger anyway; this
   precondition is about the *startup* refusal being present, not about the fence
   being enforced.)
3. The unit's entry prerequisites for the target state are met (logical schema
   §2.1, last row) — for `shadow → cutover` that is N5.0-1, N5.0-2, N5.0-3, a
   durable write repository, and an evidenced rollback data path.
4. A gate reference exists. No authority change may be recorded without one.
5. A current backup exists and its restore has been evidenced, not merely taken.

**The sequence.**

| Step | Who | What | Evidence it leaves |
|---|---|---|---|
| 1 | operator | `preview` — current authority, proposed authority, epoch, earliest activation instant, deadline, verification-window end, whether the transition is fenced, and which fence methods will be required | terminal output; no state change |
| 2 | operator | `authorize` — one revision row, receipt and audit row in one transaction | the revision; the unit's authority is **unchanged** |
| 3 | operator | **only if the transition is fenced:** `systemctl stop freedom-sheet-writer`. `SIGTERM` puts the writer into refuse-new-work mode; it waits up to N5.0-17 for outstanding calls to return and records each outcome in its journal; `SIGKILL` escalates if it does not. **The drain comes first, and this is the ordering change revision 4 makes** — revoking first would convert *completed and known* into *failed and unknown* (§2.10.4 case 1) | — |
| 4 | operator | revoke the service account's Drive write permission on the spreadsheet, and read the effective role back | `observe external_write_access_revoked` |
| 5 | operator | `observe` — the unit's `ActiveState`/`SubState`, its `cgroup.procs`, a host-wide scan for the writer entry point, and **the dispatch journal**: the seal, the `(device, inode)`, the registered generation, the hash chain, the sequence and the unresolved set. **A non-clear observation records nothing and refuses**, so a failed fence cannot be papered over; **any of the twenty-five conditions in §2.13.6 refuses**, evaluated by Algorithm **V-C** (§2.13.5b); and a non-empty unresolved set (N5.0-20) refuses and is adjudicated entry by entry against the Sheet before anything else happens | `observe unit_inactive`, `cgroup_empty`, `host_scan_clear`, `dispatch_journal_clear` — the last carrying the generation id, the last sequence and the head digest |
| 6 | operator | wait N5.0-18, the post-revocation margin. **This is risk reduction, not a barrier** (§2.10.1 B-13), and the operations document says so at the step | — |
| 7 | owning package | inside the window, with neither store writable by any service: for `shadow → cutover`, the final idempotent import and its control totals; for `→ legacy`, the supervised replay of PostgreSQL's changes back to the Sheet, under the coordinator's own access | the owning package's migration report, under Data Owner approval |
| 8 | operator | `activate` — one disposition row, receipt and audit row in one transaction. The trigger refuses unless every required fence method has a clear observation newer than N5.0-16 and newer than the revision, and unless `effective_at <= now() <= activation_deadline_at`. **The authority changes here and nowhere else** | the disposition; the new control-plane version |
| 9 | operator | start `freedom-sheet-writer` on a build that reads the new authority | the writer online |
| 10 | operator | restore the Drive write permission — **only when no unit the writer touches is at `cutover` or `database` on the Sheet side**; for a `→ legacy` rollback this is immediate, for a `→ cutover` this is when the moved unit no longer needs Sheet writes at all | `/healthz` `migration_sheet_writer` |
| 10b | operator | **the first divergence re-read**: re-read the fenced ranges and compare against the imported snapshot (W-5). Any difference is a late apply or a human edit, and is reported before the verification window is declared open | the divergence report |
| 11 | operator + Operations Owner | monitor the N5.0-4 verification window against the N5.0-5 rollback triggers; **the second divergence re-read** runs at the window's end | `/healthz`, the monitoring queries, the second divergence report |
| 12 | operator | on acceptance, `authorize` + `activate` for `cutover → database` — an unfenced transition, so steps 3–6 and 9–10 do not apply. On any N5.0-5 trigger, decide within N5.0-6 and run the whole sequence again for `→ legacy` | the next disposition |

**If an observation is not clear.** Nothing is recorded and the activation trigger
refuses, because a required method has no row. The operator's `status` says which
method is outstanding, and `/healthz` reports the pending revision. The cutover
does not happen — which is the correct outcome and is what fail-closed means
here.

**If the unresolved set is not empty.** The coordinator records no
`dispatch_journal_clear` row and the activation trigger refuses. Each outstanding
entry names its target ranges and a payload digest, so the operator can read the
Sheet and ask whether that write is present. *Present* resolves it. *Absent* does
**not** resolve it — the honest reading is *"not applied, or not applied yet"* —
and the operator's only sound choices are to abandon the fence and retry later,
or to accept that specific residual explicitly and record it. The operations
document must not offer a third.

**If the journal itself is not in a known-good state.** Any of §2.13.6's
conditions — missing, empty, unsealed, unregistered, superseded, wrong inode,
wrong owner or mode, a broken chain, a sequence gap, a torn tail, an unreadable
file — records **no** evidence and refuses. The operator's choices are to repair
the generation through `freedom-journal-admin repair`, which **seals** rather than
edits and preserves the torn tail verbatim in the archive, and then to rotate and
re-fence; or to abandon. **There is no path that treats an unknown journal as a
clear one**, and that sentence is the whole of the P5.0-R5 remediation compressed
into one line.

**If the operator abandons.** `abandon` writes a disposition recording the
unchanged authority, the chain is free, and nothing was ever authoritative but
the previous state. The writer must still be restarted and the permission
restored; the operations document makes those the abandon path's last two steps.

**If the activation window lapses.** After `activation_deadline_at` the revision
can only be abandoned. A cutover is never applied by a script that woke up a day
late.

### 7.3 Rollback of package 5.0 itself

Distinct from rolling back a cutover.

- **Before any unit has moved:** `alembic downgrade 0013` drops the **six**
  tables, the two sequences and the triggers cleanly. Nothing is lost, because
  nothing has happened. **A registered journal generation is not a unit having
  moved**, so a downgrade after provisioning but before any cutover is still
  clean — and the on-disk journal survives it, which is the correct direction:
  the evidence outlives the schema that indexed it.
- **After any unit has moved:** the downgrade **refuses**, following migration
  `0013`'s accepted precedent and dependency D-09's disposition. Rolling the
  package back then means rolling the *application* back — deploying the previous
  code, which does not read these tables — while the schema and its history
  remain.
- **The Freedom bot is restored exactly by reverting its build**, and the writer
  unit is stopped and removed. Its Sheet behaviour returns to today's, including
  today's absence of any database dependency for legacy mutations.

### 7.4 Proposed RAID rows

To be entered in the register **when this plan is accepted**, not now.

| Proposed | Type | Statement | Owner | Trigger / mitigation |
|---|---|---|---|---|
| R-5.0-1 | Risk | The authority fence is added to a live estate and a defect refuses a healthy process | Technical Lead | Every refusal is fail-*closed* by design, so the failure is a bounded refusal rather than a silent wrong authority. Exercised against all processes before deployment; the operations document names the recovery; F-6 is the declared fallback for the writer |
| R-5.0-2 | Risk | ~~A process already running when authority changes keeps the old authority until it restarts~~ **Superseded twice.** Revision 2 replaced it with a lease; revision 3 replaces the lease with a database-enforced write fence and a lifecycle boundary. The correctness risk is closed for database writes and converted into a bounded availability cost for Sheet writes | Operations Owner | The authority-fence trigger; the terminable writer; the revoked Google access. The availability consequence is D5.0-9 and R-5.0-6 |
| R-5.0-3 | Risk | A database restore silently returns a unit to an earlier authority | Operations Owner | The operations document requires `python -m tools.migration_authority status` as the first post-restore step, before any service is started, and a comparison of the restored control-plane version against the change log |
| R-5.0-4 | Risk | ~~Shadow telemetry grows without bound~~ **Re-owned by package 5.1 under OD-55.** Package 5.0 creates no telemetry table | Product Owner | Carried into §11 as a constraint on 5.1's design |
| **R-5.0-5** | Risk | **Restated and narrowed.** The `host_scan_clear` observation is point-in-time, so a writer started between the scan and the activation is not observed | Technical Lead | The coordinator re-observes immediately before activating, in the same invocation; the N5.0-16 staleness test; and the revoked Google access, which refuses such a writer independently of any host observation. **No longer includes the paused-process case**, which termination closes |
| **R-5.0-6** | Risk | **Restated.** ~~Freedom-bot mutations refuse during a PostgreSQL outage~~ — **withdrawn with the lease.** Replaced by: Sheet mutations are unavailable for the length of each fence window, and remain unavailable if the writer fails to restart | Product Owner | Bounded by the fence window; reads, `/info` and every non-mutating command unaffected; a typed message rather than a crash; `/healthz` reports it. **Accepted or rejected by D5.0-9 / OD-62 as reframed** |
| **R-5.0-7** | Risk | A Drive write permission revoked for a cutover and not restored afterwards is a silent Sheet-mutation outage for every unit still at `legacy` | Operations Owner | The restore is the checklist's last step and is a named line item in the rehearsal; `/healthz` `migration_sheet_writer` reports a writer whose writes are failing; the operations document states the one-line restore |
| **R-5.0-8** | Risk | **New, and it is a residual rather than a mitigation gap.** A `values.batchUpdate` request Google accepted before the fence, whose response never reached the writer, and which Google applies after the final import has read the Sheet, silently diverges the frozen legacy store from the imported snapshot. **No control in the published Google API prevents it or proves it absent** (§2.10.2) | **Acceptance Authority** | Made rare by the drain (W-1); enumerated when the writer worked correctly (W-2); refuses the cutover while outstanding (W-3, N5.0-20); cannot reach PostgreSQL (W-4); detected by two re-reads (W-5); disclosed before any rollback replay (W-6). **Accepted or rejected by D5.0-9 / OD-62 as reframed a third time.** It is not owned by the Technical Lead, because it is not a thing implementation can close |
| **R-5.0-9** | Risk | The coordinator's host boundary depends on host state — group memberships, `sudoers`, `pg_hba` ordering, `pg_ident`, file modes — that can drift after it is established, silently and outside this repository | Operations Owner | The WP-14 matrix is re-run after any PostgreSQL configuration change, any `sudoers` change and any deployment; `diagnostics` asserts no `sys.path` entry is writable by a service identity on every invocation; the operations document lists the host facts to re-verify. **Extended in revision 5** to the journal hierarchy's owners, modes and filesystem attributes, which drift the same way, **in revision 6** to the membership of the new `freedomjournal` group and to any residue of the `…/probe` arena, **in revision 7 to the deployed `freedom-sheet-writer.service` directive set, which Stage 4 records at provisioning and which drifts whenever the unit is edited, in revision 8 to any `…/probe-ro` residue and to the ownership and mode of both transient directories, and in revision 9 to the whole of §2.13.2c's deployment manifest — including `freedom-sheet-writer.service.d/` drop-ins, which change the directives Stage 4 attests without touching the unit file — and to any §2.13.2b state-S-B residue, which is now an operator-recovery condition rather than something a later run clears**. **Detected on re-run, not prevented** |
| **R-5.0-10** | Risk | **Accepted by MD-4 on 2026-09-23; retained as an active residual. New, raised by remediation R4, and it is the honest limit of the dispatch journal.** A writer whose **dispatch path itself** has been replaced can call `values.batchUpdate` without writing a journal record, so the unresolved set reads empty when it is not and a refusal that should have occurred does not | Technical Lead, with the Security Reviewer | Not detected by the journal, and §2.13.9 says so where a reader meets it rather than in a footnote. What bounds it is everything the writer does **not** author: the process is terminated, its cgroup is empty, a host scan found nothing, and Google refuses its access. The unit hardening (`NoNewPrivileges`, an empty `CapabilityBoundingSet`, `ProtectSystem=strict`) and the deployment digest in the registered generation raise the cost of reaching that state. **A writer compromised this deeply could have written the Sheet arbitrarily long before the fence**, which is a condition no fence was ever going to repair |
| **R-5.0-11** | Risk | **New, raised by remediation R4; extended by remediation R5, and it is the price of fail-closed.** The journal filesystem falls below N5.0-21, or an `fsync` fails, or any of §2.13.6's **twenty-five** conditions holds — including the four revision 6 adds, **J-22** (the writer was redeployed without a rotation), **J-23** (the journal was restored onto another host), **J-24** (the seal does not derive its own genesis) and **J-25** (the probe report is altered or unsupported) — and the writer refuses **every** Sheet mutation until an operator acts, for every unit still at `legacy`. **J-22 is the one an operator will meet in normal work**: an ordinary writer redeployment now requires a rotation and a re-registration before Sheet mutations resume | Operations Owner | The refusal is typed, named and carries no exception text; the Freedom bot stays online and reads, `/info` and every non-mutating command are unaffected; `/healthz` `migration_sheet_writer` reports the writer as unreachable and `migration_journal_generation` reports an unregistered or superseded generation; the operations document names the recovery for each condition. **This is a deliberate trade — an outage instead of an unrecorded write — and D5.0-13 is where it is accepted or rejected** |
| **R-5.0-12** | Risk | **New, raised by remediation R7-C; its authority set corrected by remediation R9-A.** An attacker holding **both** the complete on-disk set — `A1 + A2 + A3 + A10 + A11`, which on this host means uid 0 or a non-root identity carrying `CAP_LINUX_IMMUTABLE`, `CAP_FOWNER`, `CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH` (§2.13.5c identity **E6**) — **and** PostgreSQL superuser authority can rewrite the seal, record 0 and the registered digests into mutual agreement. *Revision 9 wrote this set as `A1 + A2 + A3 + A9` and omitted the owner authorizations; the correction makes the set **larger**, not the risk worse.* **No check in this design refuses that**, because every check compares two copies and this attacker writes both | **Acceptance Authority**, with the Security Reviewer | Not prevented. Detected only by artifacts outside both stores: `sudo log_output`, journald, the `audit_events` chain and offline backups; and a forged head still has no `seal` record, no `.close` manifest and no archive. Distinguished in §2.13.5c from `CAP_LINUX_IMMUTABLE` **alone**, which — as revision 10 records — reaches **no row at all** on this hierarchy, because it owns none of these inodes and holds no `CAP_FOWNER`. **Recorded as a residual for D5.0-13 rather than as a control** |
| **R-5.0-13** | Risk | **New, raised by remediation R8-D, and it is an undetected case rather than a mitigated one.** An actor holding **A6** — root on whichever host the tree is read on — restores the journal tree there and rewrites `/etc/machine-id` to the value the seal records. `SB.host_machine_id`, the file and the **registered row** then all carry that value, so **neither W10 nor C-d refuses**. *Revision 8's F-7 recorded a coordinator refusal; the registered row holds the forged value too, and the claim is withdrawn* | **Acceptance Authority**, with the Security Reviewer | **Not detected.** Bounded, not mitigated: the restored tree carries no production database, so the forgery is inert until its holder also reaches the coordinator (**A8**) and, for registered rows, **A9**. Evidence that remains: `sudo log_output`, journald, `audit_events`, the production host's systemd and deployment records, and a forged head with no `seal` record, `.close` manifest or archive. The design change that would close it is **D5.0-13 / OD-66 option A-2**, routed under §0.2 and **not adopted** |
| **R-5.0-14** | Risk | **New, raised by remediation R8-B.** A failed privileged cleanup (§2.13.2b state **S-B**) leaves `…/probe` or `…/probe-ro` — `root:freedomsheet 0770`, holding no evidence — in the state hierarchy until an operator acts, and **blocks generation creation** while it is there | Operations Owner | The residue is reported by absolute path with its failed operation and `errno`; the exit code is distinct; **both privileged commands refuse while it exists and neither cleans it**; the deployed unit's `ReadWritePaths=` names neither directory; and the operations document names the recovery. **An availability cost accepted deliberately in preference to an automatic clean**, which would put a routine deletion of a writer-writable directory on the happy path and mask an uninvestigated failure |
| A-5.0-1 | Assumption | The legacy Freedom bot and Sheet path remain available and undegraded outside the bounded fence windows, throughout readiness, implementation and every verification window | Product Owner | A-04 restated at package scope. Void the moment §15.1's final gate closes |
| A-5.0-2 | Assumption | No staging deployment is required for package 5.0 | Operations Owner | Holds while the package deploys nothing. §8.2 records what staging is and is not on this host |
| **A-5.0-3** | Assumption | A disposable Google spreadsheet and disposable service account are available for WP-13's measurement | Delivery Lead | **Unconfirmed.** Without them N5.0-18 stays unmeasured. **Less consequential than at revision 3**, because N5.0-18 is now an operational margin rather than a control |
| **A-5.0-4** | Assumption | A disposable operating-system identity, a `pg_hba.conf`/`pg_ident.conf` entry and a configuration reload can be made on the disposable cluster, so WP-14's peer-denial matrix can be produced | Operations Owner | **Unconfirmed, and it is a host change.** The attacking side of the matrix can use the existing service identities read-only; the coordinator side cannot be simulated. **Without it the whole R3-B evidence plan is unproducible**, and P5.0-R4 cannot close on evidence |
| **R-5.0-15** | Risk | **New, raised by remediation R11-A, and it is a residual rather than a mitigation gap.** The reviewed-source provenance of §2.12.5a rests on three root-owned host artifacts — the bare object store, the approved-revision record and the provenance record. An actor holding **A5** (uid 0, or `CAP_DAC_OVERRIDE` on root-owned paths) can rewrite all three so that `APR`, `TM`, `SM` and `PVR` agree on a tree it chose. **The database still refuses**: the generation cannot be registered without a matching `approved_source_revisions` row, which needs **A8**. **An actor holding A5 *and* A8 — that is, host root together with the Platform Administrator's `sudo` path — approves and registers its own revision, and no check in this design refuses it.** That boundary is **operator trust, not a technical control** | Acceptance Authority | What remains is external to both stores: `sudo`'s `log_output`, journald, the `audit_events` chain, offline backups, and the fact that the approval record names a `review_reference` a human can check. **The design change that would narrow it — a cryptographically signed approval record verified against a root-held keyring — is priced as D5.0-13 / OD-66 option A-3 and is deliberately not adopted.** Recorded as a residual for the Acceptance Authority, **not described as a refusal** |
| **R-5.0-16** | Risk | **New, raised by remediation R11-A, and it is the availability price of the fence.** A deployment with no approval record, no provenance record or a drifted deployed tree **cannot produce a journal generation at all**, and a running writer whose provenance record has been removed refuses every Sheet mutation at **W11a**. An emergency redeployment therefore fails closed until an approved revision exists and the deploy step has completed | Operations Owner | This is the intended direction, and it is stated rather than discovered: the operations document names the recovery — approve the revision, install the record, re-run Algorithm D, rotate the generation — and the WP-9 rehearsal exercises it. **Bounded by the same window as R-5.0-11**, with which it shares its refusal path, and it never permits an unjournalled or unprovenanced dispatch |
| **A-5.0-5** | Assumption | **New, raised by remediation R4; restated by remediation R5.** A root-owned durable directory hierarchy can be created on the journal filesystem; a **disposable probe arena owned by the writer's identity** can be created inside it; the probe cases can be executed **under the writer's uid** (`setpriv`) with `chattr +a` set and cleared by root; **a transient `systemd-run` unit can be started as root at provisioning time, carrying the deployed writer unit's hardening directives, so §2.13.2a Stage 4 can run before the report is built (new in revision 7, R6-A)**; a **deployed** `freedom-sheet-writer.service` unit file exists to read those directives from; **a second transient directory `…/probe-ro` can be created on the same mount and the S4-0 control executed in it under the writer's uid outside any unit (new in revision 8, R7-B)**; **the eight executable identities of §2.13.5c — `E1 … E8` — can each be constructed and asserted (corrected in revision 10 under R9-A/R9-C, and **corrected again in revision 11 under R10-A/R10-B**, each superseded form being withdrawn rather than carried forward).** **What revision 11 assumes, in place of revision 10's `setpriv` recipes**: that **`capsh(1)` from `libcap2-bin` is present on the target host** — it is on this one, `/usr/sbin/capsh`, `root:root 0755`, no file capabilities, §8.1 **H-6** — or, failing that, that the named fallback (a small `prctl`/`capset` program written for the harness) is acceptable to the Security Reviewer; that the **launching process's bounding set already contains** `CAP_LINUX_IMMUTABLE`, `CAP_FOWNER`, `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, `CAP_SETPCAP`, `CAP_SETUID` and `CAP_SETGID`, since **no tool can add to a bounding set**; that `PR_SET_SECUREBITS` with `SECBIT_NO_SETUID_FIXUP` (`0x4`) and `PR_CAP_AMBIENT_RAISE` behave as `capabilities(7)` documents on kernel 6.8.x; that `prctl(PR_GET_SECUREBITS)` can be read inside each constructed process alongside `/proc/self/status`; and that the harness case binary can be placed `root:root 0755` with **no file capability and no set-user-ID bit**. *Revision 10's own wording is superseded here and is retained only in §2.13.1 defects 25–28.* Revision 9 assumed *"a non-root process can be given an ambient `CAP_LINUX_IMMUTABLE` and nothing else — `setpriv --ambient-caps=+linux_immutable`"* and that such a process could clear `+i` on a **root-owned** archive file. **Both halves were wrong.** An ambient capability must also be **permitted and inheritable**, and a `setuid` away from 0 clears the permitted set unless `SECBIT_KEEP_CAPS` and `SECBIT_NO_SETUID_FIXUP` are set first, so the shorthand does not build the set it names; and `FS_IOC_SETFLAGS` additionally requires effective UID 0 or **`CAP_FOWNER`** over a root-owned inode, so the identity could not have produced the asserted result even if the set had been built. **What is assumed instead**: that a disposable uid `fbprobe` can be created and removed; that the seven-step `capsh(1)` construction of §2.13.5c produces the permitted/effective/inheritable/ambient/bounding sets `0x0`, `0x200`, `0x206`, `0x208` and `0x20E` — nothing at all, `CAP_LINUX_IMMUTABLE` alone, plus `CAP_DAC_OVERRIDE`/`CAP_DAC_READ_SEARCH`, plus `CAP_FOWNER`, and all four together; that `/proc/self/status` can be read inside each dropped process to assert them; and that a disposable second host, or a disposable host whose `/etc/machine-id` may be rewritten, is available for `JNL-40`'s forged-matching case (new in revision 9, R8-D); an `fsync` failure can be injected; and — if the Operations Owner authorizes it — a supervised host reboot can be taken between a dispatch and its outcome | Operations Owner | **Unconfirmed, and it is a host change.** A disposable path on the same filesystem suffices for the evidence; the production hierarchy is provisioned at deployment, not by this package. **None of this is confirmed, and revision 11 explicitly does not treat any earlier wording as evidence** — neither revision 9's impossible capability set nor revision 10's unparseable recipes. The assumption has now been corrected twice and **stays unconfirmed**; §8.1 **H-6** records a non-mutating read of the tool contract and is **not** a confirmation of this assumption, which needs host changes nobody has authorized. **Without it `verify-capability` cannot produce a passing probe report, so `init-generation` refuses to create a generation at all** — a host-side refusal by the privileged tool, **not** a database constraint; revision 5's *"the column is `CHECK (append_only_verified)`"* is withdrawn with the column (§2.13.8a). The `TC-5.0-JNL` band cannot be produced either, so P5.0-R5 cannot close on evidence. The reboot bullet may end as a check not run, and §2.13.8 says so rather than assuming it |
| D-5.0-1 | Dependency | A named Security Reviewer, **and their delivered recommendation** | Delivery Lead | **Half resolved 2026-08-31: Codex is named** (OD-61 closed). **The dependency is not discharged.** *Updated in revision 12:* the §9.2 pass **has now run once** and returned **changes requested with no readiness recommendation** — **P5.0-SR1** Blocking and **P5.0-SR2** Important, with `C-1` not completed, `C-3` and `C-4` not run and the three residuals unaccepted. Revision 12 remediates both findings, **claims neither closed**, and requires a re-review; readiness still blocks on it. Its scope grew at R2, R3 and **again at R4**: a new database principal, two operating-system identities, **two** `sudoers` drop-ins one of which runs **as root**, `pg_hba`/`pg_ident` ordering, a root-owned deployment path, **a root-owned durable state hierarchy with filesystem attributes and an evidence-disposal path**, hardening on two live units, the pre-existing group-writable repository tree, a credential relocation and a production-access procedure — **and, added at R5, a third system group, a seal the writer may read and a transient probe arena the writer's identity may write; added at R6, a transient `systemd-run` unit started as root at provisioning which executes the writer's identity under the deployed unit's hardening; and, added at R7, a **second** transient directory `…/probe-ro` the writer's identity may write, plus the combined-authority residual R-5.0-12; and, added at R8, a threat model of nine independently constructible authorities, a second unrefused residual **R-5.0-13**, and the operator-recovery residue state **R-5.0-14**; and, **added at R9, that threat model corrected to eleven authorities — the two owner-authorization rows `A10` and `A11` separating `FS_IOC_SETFLAGS`'s owner-or-`CAP_FOWNER` check from `CAP_LINUX_IMMUTABLE` — together with a holder table the reviewer must confirm identity by identity, and eleven of thirteen falsification rows whose minimum combination changed****. **And, added at R11, a twelfth surface — the reviewed-source provenance chain, with its out-of-band approval record, root-owned bare Git object store, reviewed deployment map, hash-pinned dependency region and root-run deployment algorithm — the canonical membership table to be confirmed identity by identity, falsification row F-13, the widened A5, and a third unrefused residual R-5.0-15.** Estimate raised to **4.5–5.5** reviewer-days. **Surface count twelve** |
| **D-5.0-2** | Dependency | **Extended again.** Rulings on D5.0-9 (reframed a third time), D5.0-10 (**extended to nine controls**), D5.0-11 (extended to the OS identity and host boundary), D5.0-12 (the two OS identities, the live-unit hardening and the repository permissions) and **D5.0-13** (new at R4; **option A re-stated at R5**, because its construction, its permission model, its probe and its registration semantics all changed; **its content amended again at R6**, because the probe's sandbox stage moves to provisioning and the seal's binding section loses its unauthenticated field, **amended again at R7**, because the probe gains a second transient directory and a positive control and the construction gains a validation step, **amended again at R8**, because the deployment digest becomes a computed and pre-consumption-validated value, the transient-directory cleanup becomes a three-state machine with one next-invocation behaviour, and a **new option A-2** is raised inside it for an independent authenticated host binding, which is **not adopted**; **and, at R9, not amended at all** — R9 corrects the *description* of a kernel check option A already depended on, so the option's content, artifacts, authorities and cost are unchanged and only the threat model that prices it moves) | Delivery Lead | D5.0-9 blocks WP-4b and is now a **risk acceptance**; D5.0-10 blocks WP-1's completion; D5.0-11 blocks WP-2 and WP-14; D5.0-12 blocks WP-4b and WP-14; **D5.0-13 blocks WP-4b and WP-15** |

**Existing rows this package touches:** R-03 (Phase 5 scope) gains a revised
estimate, **47.6** — *and a correction: §5.1's copy of this figure still read
`35.5`, the revision-4 value, through six estimate changes; revision 12 corrects
it rather than updating it silently*; R-06 (cutover or rollback loses live-bot availability) gains
its principal mitigation **and**, through D5.0-9 and now R-5.0-11, two
contributors; R-P4-4 is narrowed and stays open, owned by 5.2; A-02 and A-04 are
confirmed as still holding.

---

## 8. Environment and operations

### 8.1 Verified on 2026-08-29 and, for **H-6** only, on 2026-08-31 — not assumed

**MD-2 disposition, 2026-09-23.** The observations in this section were made
on the development host and remain historical context for the design work that
used them. They do **not** satisfy target-specific P5.0-R5 feasibility
requirements. `oracle-test` is the approved disposable target whose host facts
count; every relevant fact must be freshly observed there during a separately
authorized evidence pass and bound to that pass's reviewed target identity and
artifacts. This disposition authorizes no host access or execution.

| Requirement | State |
|---|---|
| Bot test interpreter | `/opt/discord-bots/venv/bin/python` — pytest 8.4.2, Python 3.12.3, **present** |
| Web test interpreter | `/opt/discord-bots/venv-web/bin/python` — pytest 8.4.2, Python 3.12.3, **present** |
| Node, for the Foundry module suite | v24.19.0, **present** |
| Disposable PostgreSQL | `freedom_test` over the local Unix-domain socket, **reachable**, PostgreSQL **16.15**, 31 tables at head `0013` |
| Restricted runtime role | `freedom_runtime_test` exists and cannot log in, so it can be assumed for denial evidence — assumption **A-02 holds** |
| `TEST_DATABASE_URL` | must be exported as `postgresql+psycopg:///freedom_test`, or every database-marked test skips and the suite still exits 0. The correct web skip count is **80** |
| Backup/restore drill | `infra/postgresql/backup-restore-drill.sh`, present, refuses production outright |
| `reject_history_mutation()` | present since migration 0002, and is the mechanism this package reuses |
| Live services | `freedom-bot`, `freedom-web`, `freedom-worker` all active on this host |
| The Sheet write surface | **one function**, `connectors/sheets.py:31`, called from `models/actor.py:230` and `models/trade.py:66`, with an existing boundary regression test at `tests/test_sheet_bootstrap_boundary.py:28` — verified by repository-wide search on 2026-08-29 |
| `freedom-bot.service.tmpl` stop semantics | `Type=simple`, `Restart=on-failure`, no `KillSignal` or `TimeoutStopSec` override, so `systemctl stop` is `SIGTERM` then a `SIGKILL` escalation at the default timeout — **read from the template**, not assumed |
| Disposable Google spreadsheet and service account for WP-13 | **not verified.** Assumption A-5.0-3, unconfirmed |
| Formatter / linter / type checker | **none configured.** No `pyproject.toml`, `setup.cfg`, `.ruff.toml` or `.flake8`. The submission will state this as "not configured", never as "passed" |
| **H-1 — repository ownership** | `/opt/freedom-blades/platform` is `drwxrwsr-x foundry:discordbot`; its files are `-rwxrwxr-x foundry:discordbot`; `getent group discordbot` → `discordbot:x:997:freedomweb`. **The bot, web and worker OS identities can rewrite every module in this repository, including `tools/`, `migrations/` and `.git`.** Read with `ls -ld`, `ls -l` and `getent` on 2026-08-29 |
| **H-2 — bot unit hardening** | `infra/systemd/freedom-bot.service.tmpl` sets no `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem` or `ProtectHome` — Phase 0 topology finding **F-3**, still open. Read from the template |
| **H-3 — PostgreSQL socket directory** | `/var/run/postgresql` is `drwxrwsr-x postgres:postgres`, so every local identity can reach the socket. The isolation is therefore the `pg_ident` map, not the path. Read with `ls -ld` |
| **Deployed service identities** | `freedom-bot` runs as `discordbot:discordbot`; `freedom-web` and `freedom-worker` both run as `freedomweb:freedomweb`. Read with `systemctl show -p User,Group` on 2026-08-29 — **the templates carry `__SERVICE_USER__` placeholders, so this could not be read from the repository** |
| ~~Filesystem type~~ | **Revision 4's row is withdrawn. This is finding P5.0-R5.** It read *"`/opt/freedom-blades` is on ext4 (`df -T`), so `chattr +a` is available for the dispatch journal"* — a claim about one path used to justify a file on a different one, and a filesystem type used as evidence of a runtime capability. Replaced by **H-4** and **H-5** |
| **H-4 — `/run` is `tmpfs`** | Read from `/proc/mounts` on 2026-08-29: `tmpfs /run tmpfs rw,nosuid,nodev,noexec,relatime,size=806112k,mode=755,inode64`, and `df -T /run` reports `tmpfs`. **It is volatile and is emptied at every boot.** `lsattr -d /run` additionally prints an *empty* attribute field where the ext4 paths print `--------------e-------`. **This is the fact revision 4 did not read**, and it is why the journal moves (§2.13.2) |
| **H-5 — the journal filesystem** | `df -T` and `/proc/mounts` report `/`, `/var`, `/var/lib` and `/opt/freedom-blades` as **one ext4 filesystem on `/dev/vda1`**, mounted `rw,relatime,discard,errors=remount-ro`, 232 GiB with 135 GiB free. So `/var/lib/freedom-sheet-writer` is durable, is on the same device as the repository, and needs **no new mount**. `/var/lib` is `drwxr-xr-x root:root` and `/var/lib/freedom-sheet-writer` **does not exist**. `chattr` and `lsattr` are present at `/usr/bin/`; `tune2fs` and `dumpe2fs` at `/usr/sbin/`. Read with `df -T`, `/proc/mounts`, `ls -ld` and `command -v` |
| **`chattr +a` actually works on that filesystem** | **NOT VERIFIED — a check not run, and it must not be inferred.** Setting the attribute needs `CAP_LINUX_IMMUTABLE`, which the reading account (`uid=1000(foundry)`) does not hold, and setting it would have been an environment change neither this remediation nor its predecessor is authorized to make. It is **assumption A-5.0-5**, and it is discharged by `freedom-journal-admin verify-capability` at provisioning — whose **control stage must pass first**, or the result is `inconclusive` rather than a pass (§2.13.2a). **A generation whose probe did not pass cannot be created**, because `init-generation` refuses; revision 5's *"cannot be registered, because the column is `CHECK`ed"* is **withdrawn** (§2.13.8a) |
| systemd version | **255** (`systemctl --version`), so `StateDirectory=`, `ReadWritePaths=`, `ProtectSystem=strict`, `CapabilityBoundingSet=` and `NoNewPrivileges=` are all available. §2.13.3 uses four of them and **deliberately does not use `StateDirectory=`** |
| `/etc/freedom-blades` | present, `drwxr-x--- root:root`, read with `ls -ld` on 2026-08-29 — so the credential relocation of D5.0-12 has a directory to relocate into, and it is already root-owned |
| **The `freedomjournal` membership of `freedomcoord` and `freedomsheet`** | **not verified, and it cannot be: neither account nor the group exists on this host** (`getent passwd`, `getent group`, 2026-08-31, §8.1 **H-6**). §2.12.2 is a **specification** of what provisioning must create, and `JNL-52` is the evidence that it did. **Nothing here asserts that any membership currently holds**, and the security review's check **C-4** remains outstanding |
| **A Git object store, an approval record or a provenance record for §2.12.5a** | **none exists.** `/opt/freedom-blades/coordinator`, `/opt/freedom-blades/sheet-writer` and every path §2.12.5a names are absent from this host; no bare repository was created, no commit was fetched and no record was written by this remediation. The reviewed-source contract is a **specification**, and `JNL-51` is its evidence |
| `/etc/sudoers.d/` | **not readable without privilege on 2026-08-29 — a check not run.** `getent group sudo` → `sudo:x:27:foundry` was read, so no service identity is in the `sudo` group, but a drop-in granting one cannot be excluded from here. The Security Reviewer must enumerate it |
| Setuid audit | **not run.** A partial listing of `/usr/bin`, `/usr/sbin`, `/bin` and `/sbin` showed the distribution's usual set. That is not a host-wide audit and is not offered as one |
| PostgreSQL `log_connections` | **not verified.** §2.12.7's audit cross-reference assumes it is on; the operations document must set and verify it rather than assume it |
| Disposable OS identity and `pg_hba` reload for WP-14 | **not verified.** Assumption A-5.0-4, unconfirmed |
| Root-owned journal hierarchy, a **writer-owned disposable probe arena**, a verified `+a`, a privilege drop to the writer uid, the `E1 … E8` capability sets, `fsync` fault injection and a supervised reboot for WP-15 | **not verified.** Assumption **A-5.0-5**, unconfirmed. *Revision 10 recorded that `setpriv` had **not** been checked for presence; **H-6 below now records that check**, and it is the only part of this row that has moved. Everything else in it remains unverified.* |
| **H-6 — the capability tooling contract.** Read on **2026-08-31**, non-mutatingly, for remediation R10 | **verified, and it is a read of the host, not a confirmation of A-5.0-5.** `setpriv --version` → **`setpriv from util-linux 2.39.3`**; `dpkg -l util-linux` → **2.39.3-9ubuntu6.5**; `/usr/bin/setpriv` is **`root:root`, `-rwxr-xr-x`**, and `getcap` prints nothing for it. `capsh` is present at **`/usr/sbin/capsh`**, `dpkg -S` → **`libcap2-bin` 1:2.66-5ubuntu2.4**, **`root:root`, `-rwxr-xr-x`**, and `getcap` prints nothing for it either — **neither binary is set-user-ID and neither carries a `security.capability` attribute**. Kernel **6.8.0-138-generic**; `/proc/1/status` and an unprivileged shell both report **`CapBnd: 000001ffffffffff`**, which `capsh --decode` expands to all forty-one capabilities `0 … 40`, so **`CAP_LAST_CAP` is 40** and every capability §2.13.5c needs — `CAP_LINUX_IMMUTABLE`, `CAP_FOWNER`, `CAP_DAC_OVERRIDE`, `CAP_DAC_READ_SEARCH`, `CAP_SETPCAP`, `CAP_SETUID`, `CAP_SETGID` — is present in the launching bounding set. `/usr/include/linux/securebits.h` gives `SECURE_NO_SETUID_FIXUP` as bit **2**, hence securebits value **`0x4`**. `getent passwd` and `getent group` confirm that **`freedomsheet`, `freedomcoord`, `freedomjournal` and `fbprobe` do not exist on this host**. **Every one of these is a read.** No UID, GID, group, capability set, securebit, file, mode or attribute was changed, no privilege was dropped, and no probe, `chattr`, `setpriv` or `capsh` execution that alters a credential was performed |

### 8.2 Staging — what exists, stated precisely

`freedom_staging` exists as a database, OD-22 accepts staging on this host with
hard separation, and `infra/staging/` holds the P3.5 procedures that stand a test
site up and take it down again. **No staging service is running**, and staging is
therefore a procedure rather than a standing environment.

**Package 5.0 requires no staging deployment**, because it deploys nothing
(A-5.0-2). Its database evidence is producible against the disposable
`freedom_test` database. Its **termination evidence needs real processes**, and is
producible with a harness writer process under a disposable transient systemd
unit — a `systemd-run --unit=…` scope on this host, stopped and removed by the
test — rather than against the production `freedom-sheet-writer`. That is stated
here because it is the one place revision 3's evidence needs something revision
2's did not, and it must not be discovered at implementation time. **The packages
that follow will need a standing staging environment**: 5.1's shadow comparison
and 5.2's first mutation are exactly the work plan §14.1 expects a production-like
topology for.

### 8.3 Numeric controls

**Accepted by OD-57 — N5.0-1 … N5.0-8.** Values unchanged, including revision 2's
accepted wording correction to N5.0-4.

| Ref | Threshold | Accepted value | Reasoning |
|---|---|---|---|
| N5.0-1 | Minimum shadow period before a unit may enter `cutover` | **14 consecutive days** | two full weekly cycles, so a weekly accrual is observed twice |
| N5.0-2 | Minimum compared operations before `cutover` | **30 per unit**; a lower numeric threshold requires separate advance package approval | a low-traffic command may not reach 30 in 14 days; any lower threshold must be decided before shadowing rather than waived at the gate |
| N5.0-3 | Mismatch condition permitting `cutover` | **zero unexplained mismatches in the final 7 days, and every earlier mismatch individually explained and closed** | a rate would let a systematic defect hide under a tolerance |
| N5.0-4 | The bounded verification window — the duration of the `cutover` *state*, during which PostgreSQL is authoritative and the Sheet is retained frozen for rollback | **14 days per unit** | plan §15.1 stage 8 requires a numeric period and defines none |
| N5.0-5 | Rollback trigger | **any one of:** one unexplained data-integrity mismatch; three failed commands for one unit within 60 minutes; a `migration_authority` health check failing for more than 15 minutes; or any Freedom-bot degradation attributable to the cutover | a single integrity mismatch is decisive on its own; the others are availability signals |
| N5.0-6 | Time to decide a rollback after a trigger | **60 minutes** | replaces "promptly". It is a decision deadline, not a repair deadline |
| N5.0-7 | Comparison telemetry retention | **30 days** | matches N-24's accepted precedent for terminal reconciliation jobs. **Its lease-retention half is withdrawn with the lease table** |
| N5.0-8 | Shadow comparison overhead budget | **≤ 200 ms added at p95** to any shadowed operation | a comparison that degrades the live bot violates the governing "keep the live Freedom bot reliable" direction |

**Withdrawn by revision 3, and still withdrawn.** N5.0-9 (lease TTL), N5.0-10
(renewal interval), N5.0-11 (clock-skew allowance), N5.0-12 (admitted-operation
budget), N5.0-13 (quiesce acknowledgement expectation) and N5.0-15 (the fence's
share of a cutover window, which was defined against the quiesce protocol). Each
existed only to make a lease work, and there is no lease. **The derived 25-second Freedom-bot
grace period is withdrawn with them**, and with it the standing PostgreSQL
availability dependency for legacy mutations.

**Accepted 2026-09-02 — decision D5.0-10 / OD-63 Option 1.**

Six are carried from revision 4 unchanged — two of which revision 4 reframed
because revision 3 described them as bounds they cannot be — and **three are new
in revision 5**, all of them for the journal's storage lifecycle.

| Ref | Threshold | Proposed value | Reasoning |
|---|---|---|---|
| N5.0-14 | Activation deadline after `effective_at` | **24 hours** — *retained unchanged from revision 2* | a cutover authorized and then forgotten must expire rather than fire unattended a week later |
| **N5.0-16** | Maximum age of a quiescence observation at activation | **15 minutes** — *unchanged from revision 3* | long enough for the owning package's final import to run between the observation and the activation for a small unit; short enough that a stale observation cannot fence a cutover attempted the next morning. If an import needs longer, the observation is retaken — which is a re-observation, not a waiver |
| **N5.0-17** | **Reframed.** The writer's drain timeout: how long `freedom-sheet-writer` is given after `SIGTERM` to refuse new work, finish outstanding calls and record their outcomes, before the `SIGKILL` escalation. This is the unit's `TimeoutStopSec` | **45 seconds**, and it must exceed N5.0-19 with margin | *Revision 3 called this a settle interval that bounded a call already dispatched to Google. It cannot: §2.10.1 B-13.* What it can bound is **our own client's wait for its own response**, which is a real and useful number — it is the difference between W-1 answering and W-2 having to. The margin above N5.0-19 covers connection setup and the response being written to the journal |
| **N5.0-18** | **Reframed.** The post-revocation margin before the final import reads the Sheet | **120 seconds — an operational margin, not a barrier** | Google publishes no propagation guarantee, so **no value of this number bounds anything** and the register must record it with that sentence attached. WP-13 measures a distribution to choose a sensible margin; a measured distribution is not a maximum, and calling it one is the mistake revision 3 made |
| **N5.0-19** | **New.** The Sheets client's explicit per-request timeout | **30 seconds** | `connectors/sheets.py` sets none today (§2.9), so the in-flight window is unbounded by anything this repository states. N5.0-17 cannot be chosen until this exists, and a drain cannot be bounded without it. It is the one number in the register that makes another number meaningful |
| **N5.0-20** | Maximum unresolved dispatch-journal entries permitted at activation — *unchanged from revision 4* | **zero** | a control rather than a tolerance. A single unresolved entry refuses the cutover and is adjudicated by a human (§7.2). Any non-zero value would be a silent decision that some unknown writes are acceptable, which is exactly the decision D5.0-9 puts to the Acceptance Authority explicitly |
| **N5.0-21** | **New.** The minimum free space on the journal filesystem below which the writer refuses to dispatch | **1 GiB** | The filesystem holds 135 GiB free today (§8.1 **H-5**) and a journal record is a few hundred bytes, so 1 GiB costs nothing and is reached only by something else filling the root volume. Its job is to make §2.13.6 row **J-13** a refusal **before** the Google call rather than an `ENOSPC` discovered after it. A value of zero would mean *dispatch first, journal if you can*, which is the failure direction the whole section exists to prevent |
| **N5.0-22** | **New.** The maximum size of the current journal before a privileged rotation is required | **64 MiB** | At roughly 400 bytes per record and two records per Sheet write, that is on the order of 80 000 writes — far beyond this bot's traffic for the whole of Phase 5. The number exists so the file cannot grow without a decision, and so that `archive-verify` and a chain re-read stay bounded operations. Exceeding it is an operational signal, not a refusal to dispatch |
| **N5.0-23** | **New.** Retention of a sealed, archived generation before `dispose` may run | **until plan §15.1's Sheet-retirement gate closes, and in no case less than 365 days** | It is the record of what the platform wrote to a live community's Sheet, and of what was outstanding at each fence. **The Data Owner owns this number**, not the Operations Owner: it decides when evidence may be destroyed, which is a data decision. A shorter period would let a generation be disposed of inside a verification window that might still need it |

**Revision 6 adds no numeric control and changes no value.** The register stays
at nine. The probe's procedure version (`append_only_probe_version`) is a **closed
vocabulary**, not a threshold, and it is governed by the schema and by a review
rather than by the numeric register — stated here so a reader does not go looking
for a tenth number.

These, together with N5.0-1 … N5.0-8, become the numeric register in
`docs/contracts/phase-5-migration-and-cutover-contract.md`, with the same
one-definition-per-number discipline the Phase 3 register uses. **A withdrawn
number is recorded as withdrawn, with its reason, and never silently reused.**

### 8.4 Monitoring

**Four** `/healthz` checks, reporting **pass/fail and names only**, consistent
with VM-16. They report no unit values, no player data, no counts that could
identify a character, no path and no exception text.

| Check | Fails when |
|---|---|
| `migration_authority_capability` | any unit's current authority names a store this process holds no repository for |
| `migration_authority_pending` | a revision has been pending beyond N5.0-16 without a complete fence; or a unit is past its `verification_until` without a decision; or a revision is past its `activation_deadline_at` without a disposition |
| `migration_sheet_writer` | the Sheet writer is not reachable, its writes are being refused at the external boundary — which is what a forgotten permission restore looks like (R-5.0-7) — **or its dispatch journal holds an unresolved entry older than N5.0-17**. **A writer refusing under any §2.13.6 condition becomes unreachable to this check, which is how R-5.0-11 surfaces** |
| **`migration_journal_generation`** | **new in revision 5.** No current registered journal generation exists for `sheet_writer`; or a generation was registered after the current pending revision's `dispatch_journal_clear` evidence was observed; or a pending fenced revision has evidence naming a superseded generation |

**Revision 12 adds no fifth check, and says why rather than leaving it to be
noticed.** The reviewed-source provenance has exactly one failure mode
`/healthz` could report — *no registered generation for `sheet_writer`* — and
**`migration_journal_generation` already reports it**, because a generation
cannot be registered without an approved source revision (logical schema §3.7's
`NOT NULL` foreign key). Every other provenance failure is a **host** fact: the
provenance record's absence, the deployed manifest's drift, the object store's
ownership. Reading any of those would require `freedomweb` to hold access the
next paragraph explains it must not have, and reading them from PostgreSQL would
be a copy of a fact rather than the fact. **A check that reports a copy is the
class of claim stop condition 10h forbids**, so the provenance is checked where
it can be checked — by root at **D7** and **C0**, by the writer at **W11a**, and
by the coordinator at **V-R** — and monitoring reports the one consequence that
reaches the database.

**Why the fourth check does not read the journal, deliberately.** `/healthz` is
served by `freedom-web`, running as `freedomweb`, and §2.13.3 gives that identity
no access to the journal, the seal or the archive — **less than revision 5 gave
it**, because `…/journal` moves from `0751` to `root:freedomjournal 0750` and
`freedomweb` is neither in that group nor able to traverse as *other*. Giving it
any access would widen the boundary the section exists to draw. **And a health
check must never be the thing that probes**: stop condition **10f** forbids a
destructive check against live evidence, and a non-destructive one would still be
a second, un-audited reader of the evidence file. The check is therefore evaluated
**against PostgreSQL alone**, and the journal's own integrity is read by the
coordinator's `status`/`diagnostics` and enforced by the writer's own refusal.
Stating this here is preferable to a reviewer asking why the monitoring does not
verify the chain.

Backlog and mismatch counts are exposed as aggregates on the same principle.
**Revision 2's `migration_authority_lease` check is withdrawn with the lease.**

---

## 9. Review gates and stop conditions

### 9.1 Gates that apply

| Gate | Subject | Required recommendation (governance README) | Approval |
|---|---|---|---|
| **Architecture / schema** | the **six** new tables, the **four** append-only chains, the activation trigger, the authority-fence trigger, the coordinator principal, the grants | Technical Lead, **Data Owner**, **Independent Reviewer** | Acceptance Authority |
| **Security** | the coordinator principal, its **dedicated OS identity**, the `pg_hba`/`pg_ident` ordering, the **two** `sudoers` boundaries, the **root-owned deployment path**, the **root-owned durable journal hierarchy, its filesystem attributes and its evidence-disposal path**, **the third system group `freedomjournal`, the writer-readable seal and the transient probe arena**, the runtime role's loss of every authority-plane write privilege, the Google credential's relocation into `freedom-sheet-writer`, the hardening of two live units, the pre-existing group-writable repository tree, and the production Drive-permission procedure | **Security Reviewer** | Acceptance Authority |
| **First-mutation and cutover control** (plan §12.0) | the harness, the fence, the thresholds, the rollback procedure | Technical Lead, **Security Reviewer**, **Operations Owner** | Acceptance Authority |
| **Deployment / cutover** | the deployment sequence, the writer-unit precondition and the restart order | Technical Lead, Security Reviewer, Operations Owner | Acceptance Authority |

The schema review is not a gate activity — it is a **readiness precondition**
under plan §7.3.1 and the handover, and it must close before WP-2 writes a
migration. This revision is submitted for that re-review.

### 9.2 Security review — required, and larger again

**Package 5.0 adds twelve security-relevant surfaces.** Neither revision 9 nor
revision 10 added one; **revision 12 does**, and it is the direct consequence of
this review's own first pass. Revision 9 raised the estimate to 3.0–4.0
reviewer-days and added two questions; revision 10 raised it to 3.5–4.5 and added
two more, because the threat model became **eleven** authorities whose
combinations each have to be tested against the *two* permission checks
`FS_IOC_SETFLAGS` makes, with a **holder table** to be confirmed identity by
identity; **revision 12 raises it to 4.5–5.5 and adds three more**, for the
twelfth surface, for a canonical membership table the reviewer must confirm
identity by identity because the document previously contradicted itself about
it, and because there are now **three** residuals this design does not refuse:

1. an authorization-bearing operator command that can change which store is
   authoritative;
2. **five** append-only histories whose integrity depends on withheld grants and
   triggers — *four before revision 12 added `approved_source_revisions`, whose
   immutability is what makes the generation table's foreign key mean something*;
3. a database-enforced activation precondition that is the platform's only fence
   against dual write authority;
4. **a new database principal and `pg_hba.conf` entry** (D5.0-11), which changes
   who may write the authority plane at the database level; and
5. **the relocation of the Google service-account credential** out of the Freedom
   bot and into `freedom-sheet-writer`, plus **a procedure that changes a
   production Drive permission** at each cutover (D5.0-9);
6. **two new operating-system identities, a `sudoers` drop-in, `pg_hba.conf`
   ordering and a `pg_ident.conf` map** (D5.0-11, D5.0-12) — a host privilege
   boundary, which is a different discipline from a database grant model and
   should be reviewed as one;
7. **a root-owned deployment path** (§2.12.5). **Revision 11 verified it with a
   digest of the deployment against itself, which is security-review finding
   P5.0-SR1**; surface 12 is what replaces that check, so this surface is now the
   path and its ownership rather than the verification; and
8. **the pre-existing group-writable repository tree (H-1)** and the unhardened
   `freedom-bot` unit (H-2). Neither is created by this package. Both are load
   bearing for §2.12.6's argument, and the review should see them named rather
   than have to find them;
9. **a second privileged tool that runs as `root`** — `freedom-journal-admin`,
   with its own `sudoers` drop-in (§2.13.7). It is the only thing in this package
   that runs as root; it holds `CAP_LINUX_IMMUTABLE` **and, because it is uid 0,
   the owner authorization `FS_IOC_SETFLAGS` also requires over the root-owned
   seal and archive** (§2.13.5c **A1**, **A11**); and it is the only path that
   can destroy evidence. **It should be reviewed as a privileged tool, not as a
   maintenance script**; and
10. **a root-owned durable state hierarchy carrying integrity evidence**
    (§2.13.3–§2.13.4): ownership and mode as the primary control, filesystem
    attributes as the second, an immutable seal, an immutable archive, and a
    disposal path gated on a Data Owner approval. The security question here is
    not *"can the writer append?"* but **"can anything the writer controls make
    history disappear?"**, and §2.13.4 answers it one `errno` at a time; and
11. **new in revision 6 — two deliberate relaxations of the §2.13.3 permission
    model, each made because remediation R5 required it.** First, a **third system
    group `freedomjournal`** holding exactly `freedomcoord` and `freedomsheet`, so
    the writer can read the seal it is required to validate; the net effect is
    argued to be a **tightening**, because `…/journal` moves from `0751` to `0750`
    and every other local identity loses its traverse. Second, a **transient
    `…/probe` arena the writer's identity may fully write**, without which the
    capability probe cannot attribute a refusal to `FS_APPEND_FL` at all; it
    exists only inside `verify-capability`, holds no evidence, is refused while the
    writer unit is active, is outside `ReadWritePaths=` so the unit cannot reach it,
    and is removed in a `finally` whose failure is a non-zero exit. **Both are
    permission grants to the identity the whole section exists to constrain, and
    the implementer's argument that they are safe is exactly the kind of argument
    a security reviewer should test rather than accept.** **Revision 7 adds a
    third relaxation, from remediation R6-A:** `verify-capability` now starts a
    **transient `systemd-run` unit as root at provisioning**, carrying the
    deployed writer unit's hardening directives with `ReadWritePaths=` redirected
    to the arena, and executes the writer's identity inside it. That is a
    root-invoked execution whose directive set is read from a **file on disk**
    — the deployed unit — and altered by one substitution the tool performs
    itself. **Revision 8 adds a fourth, from remediation R7-B:** a **second**
    transient directory `…/probe-ro`, `root:freedomsheet 0770`, holding the
    Stage-4 negative target. It exists because a path cannot be simultaneously
    inside and outside the substituted `ReadWritePaths=`; it is written by the
    writer's identity **outside any unit** for the S4-0 control; and it is
    removed in the same `finally`. **It doubles the number of directories the
    constrained identity may write during provisioning, and that is a fact for
    the reviewer rather than a detail.** **Revision 12 corrects what this surface
    rested on:** the `freedomjournal` relaxation was described here while
    §2.12.2 simultaneously said both identities were in their own groups only,
    which is security-review finding **P5.0-SR2**. §2.12.2 is now the canonical
    membership table, the isolation sentence that denied the group is withdrawn,
    and check **C-4** has evidence specified to discharge it (`JNL-52`); and
12. **new in revision 12 — the reviewed-source provenance chain** (§2.12.5a).
    It is a **supply-chain control**, and it is the one this review's first pass
    found missing. It introduces: an **approved-revision record** whose only
    integrity is root ownership and mode, and which is the single point at which
    a human's approval enters the design; a **root-owned bare Git object store**
    refreshed from an authenticated origin, whose `0700 root:root` ownership is
    the reason no service identity can influence what a deployment trusts; a
    **reviewed deployment map** that decides which files are installed **and with
    what owner and mode**; a **hash-pinned dependency region** whose binding is a
    lock file rather than a review; and **Algorithm D**, a root-run procedure
    that installs the program carrying authority over the authority plane and the
    journal evidence. **Every one of those is something to test rather than
    accept**, and the design's own statement is that **root remains inside the
    trust boundary — R-5.0-15** — with the signed alternative priced as OD-66
    option A-3 and deliberately not adopted.

Items 4 through 12 are exactly the kind of change `.agents/AGENTS.md` requires
approval for. A distinct security-focused pass is required.

**The reviewer is named as of 2026-08-31: Codex** (OD-61, now closed; decision by
Peter Duscha). Codex also holds the Independent Reviewer and independent
logical-schema reviewer roles for this package. **Naming the reviewer does not
shrink this section by one surface, close one finding or confirm one assumption**,
and the design re-reviews Codex has already returned are **not** this pass.
**Nor is the first security pass, returned on 2026-08-31, a discharge of it:** it
raised **P5.0-SR1** and **P5.0-SR2**, made no readiness recommendation, recorded
**C-1** as not completed and **C-3** and **C-4** as not run, and declined to
accept the declared residuals. Revision 12 remediates the two findings and
**changes none of those four facts**. The
4.5–5.5 reviewer-day scope below is outstanding in full. The briefing pack is
`docs/review/phase-5-0-security-review-brief.md`. The estimate rises again, from 3.5–4.5 to **4.5–5.5
reviewer-days** — and this time **because a surface was added**. Revision 9
replaced the threat model with nine authorities and revision 10 corrected those
into eleven, whose combinations must each be checked against the two permission
checks `FS_IOC_SETFLAGS` makes and whose holders must be confirmed identity by
identity; **revision 12 adds surface 12, the reviewed-source provenance chain**,
adds a canonical membership table that has to be confirmed identity by identity
because the document previously contradicted itself about it, adds falsification
row **F-13** and a widened **A5**, and leaves **three** residuals standing
unrefused rather than two.

**The questions the security review should be asked explicitly**, because the
implementer's answers to them are assessments rather than proofs:

- is the §2.12.6 vector table complete, and in particular does
  `/etc/sudoers.d/` — which could not be read on 2026-08-29 — contain any rule
  reaching a service identity?
- is the residual in §2.10.3's closing sentence correctly characterized, and is
  the detection in W-5 adequate compensation for the prevention that does not
  exist?
- **is §2.13.4's manipulation matrix complete**, and does the combination of a
  non-writable parent directory, `chattr +a`, an empty `CapabilityBoundingSet` and
  `NoNewPrivileges=true` actually prevent a compromised `freedomsheet` from
  erasing or replacing the evidence it authored?
- **is R-5.0-10 correctly bounded** — that is, is *"a writer whose dispatch path
  was replaced can dispatch without journalling"* the only way completeness fails,
  and is the compensating argument (the writer is dead, its access revoked, and
  the other four methods are not authored by it) sound?
- **new in revision 6: is the `freedomjournal` grant actually minimal?** The
  writer can now read the seal and list `…/journal`. Does anything in the seal —
  the deployment digest, the machine id, the predecessor identifiers, the probe
  report — help a compromised writer do something §2.13.4 does not already refuse?
  And is moving `…/journal` from `0751` to `0750` genuinely a net tightening for
  every identity on this host?
- **new in revision 7: is Stage 4's transient unit a safe thing for root to
  start?** It reads its directives from the deployed
  `freedom-sheet-writer.service`, substitutes `ReadWritePaths=`, and runs the
  writer's identity under them. Can a writable or attacker-influenced unit file
  turn that into an escalation; is the single substitution genuinely the only
  divergence `systemctl show` can miss; does **S4-3**'s directive-set comparison
  actually detect a directive systemd silently dropped or reinterpreted; and is
  a redeployment forcing a rotation (**J-22**) sufficient invalidation for
  sandbox evidence, or can the sandbox change under a systemd upgrade that the
  deployment digest does not cover?
- **new in revision 8: is §2.13.5c's capability register complete and correctly
  bounded?** **Restated in revision 9 against the nine-authority register that
  replaced it.** It asserts that **A3** is root-only on this host, that **A1** is
  unreachable from the writer's unit, that **A9** is held by no principal in the
  design, and that root can cross into `freedomcoord` but not into a PostgreSQL
  superuser. Is any of those wrong; and is **R-5.0-12** — the combined-authority
  residual this design does **not** refuse — correctly characterized as
  detection-only rather than under-stated?
- **new in revision 8: is `…/probe-ro` genuinely outside every writable
  boundary the transient unit has?** The stage's whole meaning depends on the
  substituted `ReadWritePaths=` naming `…/probe` and nothing else. Can systemd
  reach `…/probe-ro` by any other directive the deployed unit carries —
  `StateDirectory=`, `BindPaths=`, `PrivateTmp=`, a `.d` drop-in — and would
  **S4-3**'s directive-set comparison detect such a directive if one were added?
- **new in revision 9; the answer to its own last question corrected in
  revision 10: is §2.13.5c's authority register complete, and is the separation
  of flag control from DAC now correct everywhere?** Revision 8 treated
  `CAP_LINUX_IMMUTABLE` as if it reached the archive; revision 9 split the
  register into nine authorities; **revision 9's own answer to the question this
  bullet asked — "is there a tenth authority the register omits, `CAP_FOWNER`
  among them?" — was wrong, and R9-A is that answer being corrected by the
  reviewer rather than by the implementer.** The register is now **eleven**
  authorities, with `A10` and `A11` carrying `FS_IOC_SETFLAGS`'s owner-or-
  `CAP_FOWNER` check. So the question stands and is sharper: is there a
  **twelfth** — `CAP_CHOWN` (which could make an attacker the owner and so
  manufacture A10 or A11), `CAP_SYS_ADMIN`, `CAP_MKNOD`, a mount namespace, a
  bind mount over `…/journal`, a `setgid` into `freedomjournal` or
  `freedomcoord`, or a filesystem mounted with different flag semantics — that is
  reachable on this host by something short of full root, and does any of them
  change an F-row's minimum combination or its smallest real holder?
  And is the statement that **`freedomsheet` already holds A2 *and A10* on its
  own journal file**, so that the empty `CapabilityBoundingSet=` and
  `NoNewPrivileges=true` are the *whole* of what refuses a rewrite, correct and
  sufficient?
- **new in revision 10: is the holder table right, identity by identity?**
  §2.13.5c now assesses every falsification row twice — against its minimum
  combination and against the **smallest identity on this host that can hold
  it** — and concludes that **only F-2, F-3 and F-6 are bounded by the
  attacker's authority rather than by its choice of alteration**. That is a
  materially weaker claim than revision 9 made, and it is the honest one only if
  the holder table is accurate. Does any row of it over- or under-state what a
  real identity holds? In particular: does `CAP_DAC_OVERRIDE` reach anything the
  table denies it; does membership of `freedomcoord` confer anything beyond
  traverse and read on `…/archive`; and is there any route by which the
  **deployed writer** reaches `A1` that the empty `CapabilityBoundingSet=` and
  `NoNewPrivileges=true` do not close?
- **new in revision 10, and rewritten in revision 11: are the executable
  identities `E1 … E8` constructible as specified, and do their controls isolate
  the checks they claim to?** Revision 10's answer was **no**: its `setpriv`
  recipes named a securebit the tool rejects and asked for a bounding-set
  addition the kernel forbids, and five of the eight identities did not exist.
  Revision 11 rebuilds them on **`capsh(1)`** with a seven-step construction
  whose every intermediate state is derivable from the command line, and carries
  a **mask-versus-recipe comparison** in §2.13.5c. **A-5.0-5 is unconfirmed and
  none of this has been run.** The questions for the Security Reviewer are now:
  is the seven-step derivation correct step by step against `capabilities(7)` —
  in particular, is it right that with `SECBIT_NO_SETUID_FIXUP` set and no file
  capabilities on the case binary, `execve` leaves `CapPrm = CapEff = CapAmb`
  equal to the ambient set raised before it? Is a **root harness that constructs
  reduced identities with an unmodified distribution binary** the right mechanism
  — it sets no file capability, creates no set-user-ID artifact, installs
  nothing, leaves nothing behind and grants nothing root did not hold — or is one
  of the declined alternatives (a purpose-built helper with a file capability, a
  set-user-ID helper, a small `prctl`/`capset` program) preferable, given that
  §8.1 records the host's set-user-ID inventory as **not audited**? Does the
  **`fbprobe`** disposable account, and its membership of `freedomcoord` in
  **E5**, reach anything §2.13.3 does not intend? And — the question that matters
  most, carried forward unchanged — does the **E4 / E6** pair genuinely isolate
  the owner check, or is there a confound (a mount option, an LSM, an
  `overlayfs` layer) that would make E4's `EPERM` mean something else? A control
  that refuses for the wrong reason is the defect R9-A exists to prevent, one
  level down again. **The reviewer-day estimate does not move for this**: it is
  the same harness reviewed against a better-specified construction, and §4 says
  so rather than inflating the figure.
- **new in revision 9: are the two unrefused residuals correctly characterized,
  and is the forged-host one worth closing?** **R-5.0-13** says a forged matching
  `/etc/machine-id` is detected by nothing here, because every copy of that fact
  records the same value. Is that right, and is the remaining operational
  evidence (§2.13.5c's F-7 table) an honest account of what a responder would
  actually have? And is **D5.0-13 / OD-66 option A-2** — a TPM-sealed or
  coordinator-signed host binding — worth its cost, given that its principal
  price is a **legitimate restore onto replacement hardware that fails closed**
  in a design whose purpose is that evidence survives a restore?
- **new in revision 12: does the reviewed-source provenance chain actually bind
  what it claims to bind?** §2.12.5a asserts that the trusted side of every
  comparison comes from an immutable Git object in a store no service identity
  can reach, and that **omitting the step refuses**. Is that right end to end?
  Specifically: is `0700 root:root` on a bare object store sufficient, or can an
  object be introduced into it by any route short of root — a `git fetch` run by
  the wrong identity, an alternates file, a submodule, a hook, a packed-refs
  edit? **Is the SHA-1 argument sound** — that recomputing
  `source_manifest_digest` from the object bytes and comparing with `APR`'s
  SHA-256 makes a Git object-id collision insufficient — or does the extraction
  path trust an object id somewhere the recomputation does not cover? Is the
  **two-region partition genuinely closed**, and is a hash-pinned dependency lock
  an adequate binding for region D, given that region D is not reviewed and is
  the larger half of the deployed bytes by file count? And does **any** ordering
  of `D0 … D8` leave a window in which the deployed root is live but `PVR` is
  absent or stale — the rollback at D7/D8 is the design's answer, and it should
  be tested rather than accepted.
- **new in revision 12: is R-5.0-15 correctly bounded, and is option A-3 worth
  its cost?** The design concedes that `APR`'s integrity is root ownership and
  mode, so **A5** rewrites it and **A5 + A8** approves and registers a revision
  of the attacker's choosing. Is that the correct boundary, or is there a
  narrower one — is there any identity short of root that can write
  `/etc/freedom-blades/`, and does the `sudo` path to `A8` widen it in a way
  §2.12.4 does not already bound? And is a **signed approval record** (OD-66
  option A-3) worth a signing key this project does not have, given that its
  principal price is a **legitimate emergency deployment that fails closed when
  the signer is unavailable**?
- **new in revision 12: is the canonical membership table right, group by group
  and identity by identity?** This is the question the previous pass could not
  answer, because §2.12.2 and §2.13.3 disagreed. §2.12.2 now states primary and
  supplementary groups for every identity, an inverse listing each group's exact
  members, and three claims in place of the withdrawn isolation sentence.
  **Test all three:** is `freedomjournal` genuinely read-only for both members;
  does `freedomcoord` hold a write bit anywhere in the hierarchy; and is it true
  that **no mechanism in this design decides who a process is from a group** —
  `pg_ident`, `sudo`, `SO_PEERCRED`, systemd's `SupplementaryGroups=`, and any
  `setgid` route included? And does the corrected **E8** now match the
  `freedomcoord` provisioning creates, given that revision 11's did not?
- **new in revision 6, extended in revision 9: is the `…/probe` arena safe for its whole lifetime?** It is
  a directory the writer's identity may create, rename and unlink in. Can its
  existence be forced or extended while a generation is live; can a symlink or
  hardlink planted in it reach anything outside it; is `setpriv` the right
  privilege-drop; and is the `finally` cleanup sufficient against a signal, a
  panic and a full filesystem? **And, from revision 9: is refusing on residue
  the right choice rather than cleaning it?** §2.13.2b argues that a second
  automatic attempt by the same code with the same authority has no reason to
  succeed, and that an automatic clean would put a routine deletion of a
  writer-writable directory on the happy path. The cost is **R-5.0-14** — a
  writer-group-writable directory persisting until an operator acts, blocking
  generation creation while it does. Is that the correct trade, and is there
  anything a compromised `freedomsheet` could do with a `0770 root:freedomsheet`
  directory that outlives the command, given that the deployed unit's
  `ReadWritePaths=` names neither directory?

### 9.3 Stop conditions — objective, and checked at each work package

Work stops and Peter is asked if any of these is reached:

1. **D5.0-9, D5.0-11, D5.0-12 or D5.0-13 is required and unresolved** —
   WP-4b, WP-2/WP-14, WP-4b/WP-14 and WP-4b/WP-15 respectively. D5.0-10 was
   closed on 2026-09-02 and no longer stops WP-1;
2. a material architecture, schema, authority, privacy, credential-scope,
   database-principal, deployment, migration, rollback or release-boundary choice
   appears that this plan does not already record — **including any change to the
   accepted production topology or credential contract, which stops work for
   Peter's ruling before it is treated as binding**;
3. a physical schema is written and the independent logical-schema re-review has
   not closed with P5.0-R1 and P5.0-R4 recorded closed and P5.0-R2 still closed;
4. the Security Reviewer is unnamed at the point of the gate, **or is named and
   has not delivered the §9.2 recommendation, or has delivered it with an open
   Blocking or Important finding** — extended in revision 12, because revision 11
   satisfied this condition by naming alone and the gap it exists to guard was
   the review, not the vacancy;
5. the disposable PostgreSQL database or the restricted runtime role becomes
   unavailable;
6. any design would produce dual writes or two simultaneous authorities, in any
   of the four states;
7. any Sheet-era field would be migrated, or any 5.1+ feature implemented;
8. a permanent Discord character-mutation interface would be created;
9. any Freedom-bot behaviour would be weakened, disabled or deleted **beyond what
   D5.0-9 rules acceptable**;
10. the fence's guarantee would depend on a human step, an unbounded wait, a
    clock, or a process behaving correctly after it has lost authority;
10b. **any document, test or evidence artifact would describe an unproven
    property as proven** — in particular describing N5.0-17, N5.0-18, a `403`, an
    ACL readback, a quiet period, a propagation distribution, **the dispatch
    journal, its durability, its generation, its seal, its acyclic construction or
    its archive** as a barrier for I-SHEET-COMPLETE, which §2.10.2 and §2.13.10 say
    none of them is; **or describing any database constraint as proof that a
    host-side fact occurred**, which §2.13.8a says no constraint can be; **or —
    new in revision 9 — describing a forged matching `/etc/machine-id` as
    detected**, which §2.13.5c's F-7 and **R-5.0-13** say it is not;
10c. **the coordinator would execute code from a path any service identity can
    write**, or either `sudo` rule would be configured with `NOPASSWD`, `setenv`,
    a relative path or a directory rather than a single fixed executable;
10d. **any journal state that is not known-good would be treated as clear** —
    in particular a missing, empty, unsealed, unregistered, superseded, replaced,
    truncated, corrupt or unreadable journal producing a `dispatch_journal_clear`
    row, or the journal being placed on a volatile filesystem, or its append-only
    capability being **inferred** from a filesystem type rather than probed
    (§2.13.2, §2.13.6), **or probed in a way whose refusals are attributable to
    ordinary permissions rather than to `FS_APPEND_FL`** (§2.13.2a Stage 1).
    **This is the standing guard against a repeat of P5.0-R5**;
10e. **the writer would be given ownership of, or write permission on, the
    directory holding its own journal, its seal or its archive** — including by
    adopting systemd's `StateDirectory=`, which does exactly that (§2.13.2 S-3).
    **Read access to the seal is the single exception, granted deliberately by
    remediation R5-B**, and it does not extend to the archive, to write on
    anything, or to the transient probe arena while a generation is live;
10f. **any startup, health, monitoring or routine check would perform a
    destructive operation against live evidence** — a write-mode open without
    `O_APPEND`, an offset write expecting offset semantics, an `O_TRUNC` open, an
    `ftruncate`, an `unlink`, a `rename` or an attribute change on a live journal,
    seal or archive — **or the capability probe would run against anything but a
    disposable artifact in a directory holding no evidence** — which, from
    revision 8, means `…/probe` **and `…/probe-ro`**, both created and destroyed
    inside `verify-capability` (§2.13.2a, §2.13.5b **V-W**, `JNL-32a`, `JNL-32b`,
    `JNL-48`). This is the standing guard against revision 5's destructive
    re-probe. **Extended in revision 9:** residue left by a failed cleanup
    (§2.13.2b state **S-B**) may not be **reused, silently removed, or treated as
    absent**. Both privileged commands refuse while it exists and neither cleans
    it; recovery is a named operator procedure, and **only one of those two
    behaviours may be specified**;
10g. **any digest in the generation construction would depend, directly or
    transitively, on a value derived from it** — the revision-5 defect — so any
    change to §2.13.5a's Algorithm C must be re-checked against its dependency
    graph and re-proved by `JNL-31`; **or the seal body would be made to carry
    `genesis_record_digest`, `journal_device`, `journal_inode` or `seal_digest`**,
    each of which reintroduces the cycle;
11. **any production Google access, service-account key, spreadsheet permission
    or credential would be changed** — WP-13 uses disposable resources only, and
    a production access change is a cutover step under an approved D5.0-9, never
    an implementation step;
12. **any proof of quiescence would be authored by the process being fenced**,
    beyond the single, named, one-direction dependency §2.13.9 states and bounds;
    or
10h. **new in revision 7 — any artifact would be described as covering, proving
    or refusing more than it does.** Specifically: a digest described as covering
    a stage, a field or a byte range that is **not inside the bytes it is
    computed over** (the R6-A defect); a refusal claimed for an actor whose
    algorithm contains **no step that detects it**, or claimed without naming the
    attacker capability it holds against (the R6-B defect); or a test whose
    expected state its **own** algorithm refuses to produce (the R6-C defect).
    Every integrity claim in §2.13 must name the artifact, the step, the actor
    and the capability boundary, **and must carry a falsification case that fails
    if the claim drifts.** This is the standing guard against the class of defect
    revision 6 realised three times. **Extended in revision 9 by R8-D:** a
    comparison may not be described as a **detector** unless its two sides can
    differ under the threat it is claimed to detect. Comparing two copies of one
    recorded value detects a **transcription** error and nothing else; it does not
    detect a forgery of the fact recorded. **No test may assert a refusal without
    naming the field whose inherent mismatch the threat case proves**, and where
    no such field exists the outcome is a **residual**, not a refusal;
10i. **new in revision 8 — any negative capability test would be interpreted
    without a positive control against the exact identity, path, file, inode and
    mount it relies upon.** Stage 1 is that control for Stage 2 and **S4-0** for
    **S4-2**; a refusal observed without its control passing is **`inconclusive`**,
    never `passed`. This is the standing guard against the R7-B defect, and it
    extends 10d from `FS_APPEND_FL` to every mechanism a refusal is attributed
    to;
10j. **new in revision 8; re-stated in revision 9 — any ordered algorithm in this
    package would contain a step that consumes a value a later step produces,
    that validates a result before the step which creates it, or that
    "validates" an input against a value derived from that same input.**
    Algorithm C's value table (§2.13.5a) must satisfy invariants **I-1 … I-5**,
    and `JNL-46` must walk the algorithm in order and prove them. *Revision 8
    stated this as one universal inequality, `produced < validated ≤ consumed`,
    which cannot hold for internally produced or derived values and which its own
    first row violated.* The two halves are now separate: **I-2** requires every
    **external input** to be validated **against an independent source** at or
    before first consumption, and **I-3** requires every **internally produced**
    value to be checked before the first persistent artifact depends on it. This
    is the standing guard against the R7-A and R8-A defects, and it is broader
    than 10g, which covers digest cycles only;
10k. **new in revision 8 — any threat model here would state reach by which
    detector catches an injected mutation rather than by what an attacker must
    hold to construct the alteration**, or would assign a row a capability that
    cannot in fact construct it. Every falsification row must name its **minimum
    capability**, whether that capability also reaches the detector, and the
    residual when it reaches both; and every impossible pairing must be marked
    not constructible **with the control that makes it so**. This is the standing
    guard against the R7-C defect. **Extended in revision 9 by R8-C:** a
    capability may not be credited with an access it does not confer.
    `CAP_LINUX_IMMUTABLE` is flag control and **no discretionary access
    whatever**; every row must state the minimum **combination** of flag control
    and DAC, and every feasible or not-constructible case must be executed under
    an identity and capability set that really holds only what the row claims —
    not simulated as root. **Extended again in revision 10 by R9-A and R9-B:** a
    capability may not be credited with satisfying a kernel check it does not
    satisfy — `CAP_LINUX_IMMUTABLE` is **one of two** requirements for an
    `FS_IOC_SETFLAGS` flag change and `CAP_DAC_OVERRIDE` is not the other; **and
    a register may not assert that its primitives are independent while reasoning
    from the fact that real holders bundle them.** Where both are true they must
    be stated separately — the primitives in the register, the bundling in a
    holder table — and every reach claim must be assessed against the **smallest
    identity that can actually hold the combination**, not against the
    combination alone;
10l. **new in revision 9 — any two evidence artifacts in this package would
    require mutually exclusive states of the same host artifact after the same
    injected failure.** Every failure injection must resolve to exactly **one**
    state of the state machine that owns it (§2.13.2b for the transient
    directories), and every test asserting a post-failure state must **name which
    state it is asserting**. Where a claim holds only in some states, it must be
    written conditionally — *"no generation artifact"* is unconditional,
    *"no transient residue"* is not. This is the standing guard against the R8-B
    defect;
10m. **new in revision 10 — any operation this package reasons about would be
    described by fewer kernel prerequisites than it has, or any negative
    capability case would be run without its other prerequisites satisfied.**
    Every privileged or capability-bearing operation named in §2.13 must state
    **all** of the checks the kernel makes — for `FS_IOC_SETFLAGS` that is path
    traversal, open, **owner-or-`CAP_FOWNER`**, and `CAP_LINUX_IMMUTABLE` for the
    two flags — **before** any register row, matrix cell, risk row or evidence
    case depends on it, and §2.13.5c must carry them in a table of their own.
    Every case asserting a refusal from such an operation must run with **every
    other prerequisite satisfied** and must carry a **positive control that
    succeeds** and differs from it in exactly the one privilege under test, so
    the refusal is attributable to the intended boundary rather than to an
    unrelated DAC or path-search denial. Every executable identity must be
    specified by effective UID, GID, supplementary groups and its complete
    permitted, effective, inheritable, ambient and bounding capability sets —
    **ambient shorthand alone is not a specification**, because an ambient
    capability must also be permitted and inheritable — and must be asserted from
    `/proc/self/status` before the case runs, an unasserted identity yielding
    **`inconclusive`**. This is the standing guard against the R9-A and R9-C
    defects, and it extends **10i** from *a positive control on the exact target*
    to *a positive control on the exact privilege*;
10n. **new in revision 11 — any executable identity would declare a credential
    state that its own launch recipe does not produce, or would be constructed by
    a mechanism whose ordering the named tool's documentation does not
    determine.** Every declared effective UID, GID, supplementary-group list,
    permitted, effective, inheritable, ambient and bounding set and securebits
    value must be **derived** from the invocation that produces it — option by
    option, against the documented semantics of the exact tool and version named
    — and that derivation must appear **in the document**, as §2.13.5c's
    mask-versus-recipe comparison does, not in the author's or the reviewer's
    head. **An option a tool's own manual page refuses, or an operation it
    documents as impossible, is a defect wherever it appears**, including in a
    correction: revision 10 used `setpriv --securebits=+keep_caps`, which that
    page lists as not allowed, and `--bounding-set=+…`, which that page says the
    kernel does not permit. **No tool may be asked to add a capability to a
    bounding set**, and every identity's capabilities must be asserted present in
    the launching process's bounding set before construction, an absence yielding
    **`inconclusive`**. **Where a mask depends on the order in which a tool
    applies securebits, credential changes and capability sets, and the tool does
    not document that order, the mechanism must be changed rather than the mask
    defended** — a recipe whose outcome is not derivable is not a specification,
    and a test that has not been authorized to run cannot stand in for one. An
    environment-dependent value — `CAP_LAST_CAP`, a resolved uid or gid — must
    name the environment it was read from and be **re-read and re-asserted** on
    the host the case actually runs on. This is the standing guard against the
    R10-A and R10-B defects, and it completes **10m**: 10m requires the identity
    to be *specified* completely, 10n requires it to be *constructible* as
    specified;
10o. **new in revision 12 — any integrity or supply-chain control would take its
    trusted side from the artifact it is checking, or would be skippable without
    a refusal.** A digest of a deployment compared with a digest of that same
    deployment establishes **consistency**, never **provenance**, and a
    comparison whose two sides can only ever agree is not a control. Every
    artifact this package deploys that carries authority — the coordinator, the
    writer, their units and their drop-ins — must be bound to an **immutable
    reviewed object** and to an **approval record that arrives out of band**, the
    binding must be recomputed at deployment, at generation creation and at
    writer start, and the **absence** of any provenance input must be a refusal
    rather than a default. **A control described in an operations document but
    absent from an algorithm's preconditions is not a control**, and neither is
    one whose omission leaves no durable trace. Where the trust boundary still
    contains an identity that can write both sides — as root does here — that
    must be recorded as a **residual with its holder named**, never as a refusal.
    This is the standing guard against the P5.0-SR1 defect, and it extends
    **10j**'s I-2 from *"an independent source"* to *"a source outside the host
    the artifact is deployed on"*;
10p. **new in revision 12 — any operating-system identity's group membership
    would be stated anywhere but §2.12.2.** Primary and supplementary groups are
    stated **once**, in that table, with a complete per-identity list and a
    complete per-group member list; every other passage, evidence identity,
    provisioning step and schema artifact **cites** it. A membership asserted,
    denied or implied elsewhere is a defect **whether or not it is correct**,
    because the failure mode is two true-looking statements that cannot both be
    followed — which is what P5.0-SR2 found, held for five revisions and three
    independent re-reviews. **Every evidence identity must additionally say which
    provisioned identity it corresponds to, or say that it corresponds to none**;
    a synthetic identity is legitimate, and a synthetic identity mistaken for a
    real holder set is the same defect one level down;
13. **any journal generation would be disposed of** without N5.0-23, plan
    §15.1's gate, a Data Owner approval reference and a passing `archive-verify`.

### 9.4 Readiness assessment against the governance README

| Readiness criterion | State |
|---|---|
| outcome, included scope and exclusions written | **met** (§1) |
| predecessor gates approved | **met** — Phase 3 and Phase 4 both approved |
| blocking decisions and dependencies closed | **NOT met** — OD-54 … OD-61 and **OD-63** are closed, but D5.0-9, D5.0-11, D5.0-12 and **D5.0-13** remain open and each blocks a work package. **D5.0-9 is now a risk acceptance rather than a design choice** |
| Product Owner, Technical Lead, implementer and required reviewer roles named | **met** — implementer, Technical Lead, Independent Reviewer, schema reviewer and, from 2026-08-31, **Security Reviewer** are all named (OD-61, closed). *Naming closes the criterion; it does not deliver the review, which is the next row* |
| **required security review delivered** | **met on design, 2026-09-02** — Codex's revision-12 re-review closes **P5.0-SR1** and **P5.0-SR2** on design and completes the twelve-surface security design review. **No readiness recommendation follows:** C-1/C-3/C-4, the operational evidence, assumptions, residual dispositions and Blocking P5.0-R5 remain outstanding |
| independent logical-schema review closed | **NOT met** — revisions 1 … 9 were each returned with Blocking findings. **Revision 10 is remediation R9 and claims none closed**: for P5.0-R5 it corrects the authority register's model of `FS_IOC_SETFLAGS`, separating the `CAP_LINUX_IMMUTABLE` half from the owner-or-`CAP_FOWNER` half, adding a holder table and rewriting the executable evidence under identities with complete capability sets — every corrected combination making an alteration **harder** to construct. Revision 9 was remediation R8 and **claimed none closed**: for P5.0-R5 it makes C0 compute and compare the deployment digest against the deployed bytes before anything consumes it and replaces the universal ordering claim with invariants I-1 … I-5, gives the transient directories one three-state cleanup contract with a single next-invocation behaviour, replaces the eight-capability register with nine independently constructible authorities and per-row minimum combinations, and reclassifies F-7's forged-matching host identity as a residual rather than a refusal; for P5.0-R4 it leaves the revision-4 boundary and evidence plan intact and claims no operational evidence passed; for P5.0-R1 it repeats that no barrier exists and returns a decision instead |
| work decomposed small enough to estimate and review | **met** (§3) |
| estimate assumptions, capacity, confidence, contingency recorded | **met** (§4) |
| acceptance criteria objective and traced to tests or supervised checks | **met** (§6) |
| development, disposable database and staging environments available | **partly met** — the database evidence is producible (§8.1); the termination evidence needs transient systemd units, which this host supports; **A-5.0-3, A-5.0-4 and the new A-5.0-5 are all unconfirmed.** Without A-5.0-4 the R3-B evidence cannot be produced at all, and **without A-5.0-5 no journal generation can be registered and the whole `TC-5.0-JNL` band is unproducible** |
| material risks have owners, mitigations and triggers | **met, pending register entry** (§7.4) |

**Conclusion: package 5.0 is `not ready`.** Four criteria are unmet or partly
met. Two are the maintainer's to resolve — the **five** open decisions and the
three unconfirmed environment assumptions — and two are reviews this submission
requests and does not pre-empt: the **security re-review of revision 12**, and
the schema re-review. *Revision 11's version of this paragraph counted the
unnamed Security Reviewer; that criterion is now met and is replaced by the
undelivered review, which is a different and larger gap: a named reviewer who has
returned two findings is further from readiness than a vacancy, not closer.*

**One of them cannot be resolved by any further design pass.** §2.10.2 concludes
that the barrier P5.0-R1's Sheet half asks for does not exist in the published
Google APIs, and §2.13.10 records that making the journal durable does not create
one. A fifth revision of the design would not find it; what closes that half is
Peter's ruling on D5.0-9, or the Independent Reviewer evidencing a published
mechanism §2.10.1 missed. Both outcomes are better than another cycle of the same
search, which is why this revision leaves the conclusion where revision 4 put it
rather than proposing a mechanism.

**What revision 12 claims to have changed.** The first security pass found two
things, and they are different in kind. **P5.0-SR2 is a bookkeeping failure with
a security consequence:** one fact stated in four places, wrong in one of them,
and neither contract's consumer noticed for five revisions and three independent
re-reviews. It is answered by making the fact have **one** place (§2.12.2), by
withdrawing the sentence that was false rather than repairing it, and by stop
condition **10p**, which makes a restatement a defect whether or not it is
correct. **P5.0-SR1 is a control that was never a control:** a comparison whose
two sides came from the same artifact, described in an operations document rather
than in an algorithm's preconditions, with no refusal on omission. It is answered
by §2.12.5a — an approval record that arrives out of band, a trusted manifest
computed from immutable Git objects in a store no service identity can reach, a
closed two-region partition, a provenance record whose **absence refuses at C0**,
and a `NOT NULL` foreign key that stops an unprovenanced generation from being
registered at all — with the negative test the finding demands (`JNL-51` case
(g)). **Neither finding is claimed closed**, and **the honest limit is stated
rather than argued around**: root is still inside the trust boundary
(**R-5.0-15**), and the design change that would narrow that is priced as OD-66
option A-3 and not adopted. **Whether this is sufficient is the Security
Reviewer's to say**, and the most useful disagreements would be: a route into the
object store short of root; a gap in the SHA-1 argument; a window in `D0 … D8`
where the deployed root is live and `PVR` is not; a mechanism that does decide
identity from a group; or a residual — **R-5.0-15** in particular — that is
understated.

**What revision 9 claimed to have changed, retained.** Revision 8 answered R7's three
findings and was returned with four more, and the four divide in two. **Two are
the same class again** — a validation that ran after the step that consumed its
input and compared it against a copy of itself, and a cleanup contract that
required one injected failure to leave two states. **Two are a different and
worse class**: a *mechanism* credited with something it does not do.
`CAP_LINUX_IMMUTABLE` was written into the register as though it bypassed Unix
DAC, and a comparison between two copies of one recorded value was written into
F-7 as though it detected a forgery of the fact recorded. Revision 9 answers the
first pair with a computed digest validated at **C0** against the deployed bytes
and five invariants in place of one inequality (§2.13.2c, §2.13.5a, `JNL-46`), and
with a three-state cleanup machine that gives one failure one outcome
(§2.13.2b, `JNL-47`, `JNL-48`, `JNL-30`). It answers the second pair by
**replacing the register with nine independently constructible authorities and
testing the new cases under capability sets that really hold only what they
claim** (§2.13.5c, `JNL-49`, `JNL-50`), and by **withdrawing F-7's refusal
entirely** and recording the forged-matching host identity as residual
**R-5.0-13**, with the design change that would close it routed as OD-66 option
A-2 rather than adopted. **Whether that is sufficient is the Independent
Reviewer's to say**, and the most useful disagreements would be: an authority in
§2.13.5c that is still wrongly bounded, a tenth the register omits, or an F-row
whose stated minimum **combination** still cannot construct its alteration; a
case in `JNL-49`/`JNL-50` that would in practice be executed as root rather than
under the capability set it names; a state in §2.13.2b that a real failure can
reach and the table does not list; a value in §2.13.5a whose class under
I-2/I-3/I-5 is wrong; or a residual — **R-5.0-13** in particular — that is
understated, or that option A-2 should close rather than the Acceptance Authority
accept.

**What revision 8 claimed to have changed, also retained.** P5.0-R5 is still the one of the
three findings a design pass *can* answer, because it is a defect in this
package's own design rather than a limit of an external service. Revision 5
answered its *shape* and got four of its *mechanics* wrong; revision 6 replaced
those four mechanics and then described three of its own artifacts more strongly
than it built them; **revision 7 corrected those three descriptions and, in each
correction, reproduced the same defect one level down** — a validation placed
before the step that produces its input, a sandbox refusal accepted without a
control on its target, and a class column that recorded which detector fired
rather than what an attacker must hold. Revision 8 answers that class with
artifacts rather than prose: Algorithm C is renumbered **C0 … C13** around a
post-probe validation step and given a value-dependency table and an
ordered-walk harness (§2.13.5a, `JNL-46`, `JNL-47`); Stage 4 is given an exact
target, a full lifecycle and the positive DAC control `S4-0` (§2.13.2a,
`JNL-48`); and the falsification matrix is replaced by a capability register with
a per-row minimum **combination**, detector reach and residual, plus a
not-constructible table with the control for each cell — **eight capabilities in
revision 8, nine authorities in revision 9, and eleven in revision 10**, which is
where the register finally names both of `FS_IOC_SETFLAGS`'s permission checks
(§2.13.5c, `JNL-49`, `JNL-50`). **Whether that is sufficient is the Independent Reviewer's to say**,
and the most useful disagreements would be: a step in Algorithm C that still
consumes a value produced later, or a value the dependency table mis-attributes;
a probe case whose refusal is still attributable to something other than the
mechanism it names; a capability in §2.13.5c's register that is wrongly bounded,
a ninth the register omits, or an F-row whose stated minimum capability cannot
in fact construct its alteration; a pairing marked not constructible that is; or
a residual — **R-5.0-12** in particular — that is understated.

---

## 10. What this package does not claim

- It does **not** claim the Phase 5.0 gate, or any gate.
- It does **not** claim readiness. §9.4 says the opposite.
- **New in revision 12.** It does **not** claim that **P5.0-SR1** or **P5.0-SR2**
  is closed. The Security Reviewer decides, and revision 12 exists to be
  re-reviewed. It does not claim that the §9.2 security pass has been delivered,
  that check **C-1** has been completed, that **C-3** or **C-4** has been run, or
  that **R-5.0-12**, **R-5.0-13**, **R-5.0-14**, **R-5.0-15** or **R-5.0-16** has
  been accepted.
- **New in revision 12.** It does **not** claim that the reviewed-source
  provenance contract removes root from the trust boundary. An actor holding
  **A5** rewrites the approval record, the object store and the provenance
  record; an actor holding **A5 + A8** also registers the revision it approved.
  That is **R-5.0-15**, and it is recorded as a residual with its holder named —
  not described as a refusal, and not narrowed by a control this package builds.
  What the contract does claim is narrower and testable: **the trusted side of
  every comparison comes from an immutable object no service identity can reach,
  and omitting the step refuses.**
- **New in revision 12.** It does **not** claim that a signed approval record,
  a signed tag or a keyring exists or is planned. OD-66 **option A-3** prices one
  and **does not adopt it**, and no signing key, keyring, custody procedure or
  verification step is introduced anywhere in this package.
- **New in revision 12.** It does **not** claim that any group membership in
  §2.12.2 currently holds. `freedomcoord`, `freedomsheet`, `freedomjournal` and
  `fbprobe` **do not exist on this host** (§8.1, **H-6**). §2.12.2 is a
  specification of what provisioning must create; `JNL-52` is the evidence that
  it did; and check **C-4** remains outstanding.
- **New in revision 12.** It does **not** claim that region **D** — the
  hash-pinned dependency half of the deployed root — is reviewed. It is
  **pinned**, by artifact digest against a lock file that is itself reviewed.
  A distribution whose published artifact changes under a fixed version is
  **detected** at **D4**, not prevented, and nothing here claims a reproducible
  build.
- It does **not** claim that P5.0-R1, P5.0-R4 or P5.0-R5 is closed. The
  Independent Reviewer decides. **Revision 9 corrects the four Blocking
  inconsistencies the R8 re-review found, and adds no new claim of closure.**
  **Two of its corrections remove a claim rather than replace it**: F-7's
  coordinator refusal is withdrawn and becomes residual **R-5.0-13**, and the
  universal *produced < validated ≤ consumed* sentence is withdrawn and becomes
  five bounded invariants. The design is smaller in what it asserts after this
  revision than before it, which is the intended direction. For **P5.0-R5** revision
  5 replaced the journal's
  storage, identity, integrity format and lifecycle and resolved the completeness
  contradiction, and **revision 6 replaces the four mechanics the re-review found
  wrong** — the circular construction, the contradictory permission, the invalid
  and unsafe probe, and the overstated database claim. It names the evidence
  bullets it cannot produce without a supervised host action. For **P5.0-R4** it leaves revision 4's boundary and
  denial matrix intact and **claims no operational evidence passed**; OD-64,
  OD-65, the Security Reviewer and the two privileged checks remain open. For
  **P5.0-R1's Sheet half it still does not offer a fence at all**: §2.10.2
  concludes no barrier exists in the published Google APIs, and what is offered
  instead is a stated weaker guarantee and a priced decision.
- It does **not** describe any of N5.0-17, N5.0-18, a `403`, an ACL readback, a
  process death, a quiet period, a measured propagation distribution, **the
  dispatch journal, its durable storage, its generation, its seal, its acyclic
  construction, its hash chain or its immutable archive** as a barrier proving
  that an accepted request has completed. Revision 3 came close to doing so for
  two of them and revision 4 withdrew it; **revisions 5, 6, 7 and 8 each make the
  journal stronger and claim exactly nothing more for it** (§2.13.10). **R-5.0-8
  is narrowed by no case at all.**
- It does **not** claim that the journal establishes completeness against a
  compromised writer. §2.13.9 states the single direction in which activation
  depends on the journal, and **R-5.0-10** names what is left outside it.
- It does **not** claim that `chattr +a` works on this host. That is
  **assumption A-5.0-5**, it could not be tested without privilege and without
  changing the host, and a generation whose probe did not pass **cannot be
  created**, because `init-generation` refuses. Revision 4's inference from a
  filesystem type is exactly the mistake being corrected, and no revision since
  repeats it in a new place. **Revision 8 extends the same discipline to the
  sandbox**: `EROFS` is not accepted as evidence of `ProtectSystem=strict`
  unless `S4-0` first proved the exact target writable without it.
- **New in revision 6.** It does **not** claim that any database constraint
  proves a host-side fact. `CHECK (append_only_verified)` and its column are
  **withdrawn**; §2.13.8a states line by line what PostgreSQL enforces and what it
  merely records, and what actually establishes that the probe ran is the on-disk
  seal, `sudo`'s `log_output`, journald, `audit_events` and `archive-verify`.
- **New in revision 6.** It does **not** claim that the revision-5 generation
  construction was buildable. It was not: §2.13.1 rows 5–9 concede all four
  defects the re-review named, without argument, before §2.13 states the
  replacements.
- **New in revision 8.** It does **not** claim that revision 7's Algorithm C
  could be executed. It could not: **C0** required a probe result **C1** had not
  yet produced, and §2.13.1 row 14 concedes that before §2.13.5a states the
  replacement.
- **New in revision 8.** It does **not** claim that revision 7's **S4-2**
  attributed anything. Without a positive control on its exact target, an
  `EROFS` there was consistent with ordinary permissions, and §2.13.1 row 15
  concedes it.
- **New in revision 8.** It does **not** claim that any single attacker reaches
  every falsification row. The two-class model is withdrawn; §2.13.5c states a
  **minimum capability per row**, and the sentence *"class 1 reaches every row
  except F-1b"* is **withdrawn as false of its own definition**.
- **New in revision 8.** It does **not** claim that a combined-authority attacker
  — root on the host **and** a PostgreSQL superuser — is refused anywhere in this
  design. That is **R-5.0-12**, it is a residual for the Acceptance Authority,
  and `JNL-49` case 7 asserts the limit rather than hiding it.
- **New in revision 8.** It does **not** claim that a `machine-id` cannot be
  forged. Revision 7 said a privileged attacker *"cannot forge another host's
  `machine-id` on this one"*; `/etc/machine-id` is an ordinary root-writable
  file, and §2.13.5c **F-7** now states the boundary as it is.
- **New in revision 10; sharpened in revision 11.** It does **not** claim that
  any privileged case in §2.13.5c, `JNL-49` or `JNL-50` has been **executed**.
  Every one of them depends on **A-5.0-5**, which is unconfirmed. Revision 9's
  two capability-set cases were not merely unrun but **not constructible**, and
  **revision 10's E2 … E6 recipes were not merely unrun but would not have
  parsed** — which is precisely why neither defect could be caught by the
  evidence plan and why both had to be caught by a reader. The identities
  `E1 … E8` are a specification for an authorized environment to run, and until
  it does, §2.13.5c's register is an argument checked against the kernel's
  documented contract, and its construction an argument checked against two
  installed manual pages, and against nothing else. **§8.1 H-6 is a read of the
  host's tool contract; it is not evidence that any identity was built**, and no
  count, estimate or claim in this plan treats it as such.
- **New in revision 10.** It does **not** claim that the writer's refusals bound
  what an attacker holding a given combination *could* have done. §2.13.5c
  bounded claim 2 states the limit: **only F-2, F-3 and F-6** are bounded by the
  attacker's authority rather than by its choice of alteration, because for every
  other row the smallest identity that can hold the minimum combination also
  reaches the detector's prerequisites. **Revision 9 implied this held far more
  widely**, and the correction narrows the claim rather than the design.
- **New in revision 6.** It does **not** claim that giving the writer read access
  to the seal is free. It is a deliberate grant to the identity this section
  exists to constrain, it is argued rather than proved, and it is referred to the
  Security Reviewer as surface 11 with two questions attached (§9.2).
- It does **not** claim that P5.0-R2 has been re-opened or re-decided. That
  finding is closed and its accepted content is preserved verbatim in substance.
- It does **not** close R-P4-4, or any RAID row.
- It does **not** make PostgreSQL authoritative for anything. Every unit stays
  `legacy`.
- It does **not** decide account vocabulary, credential scope, field authority,
  the per-unit rollback data path, comparison-telemetry schema, or production
  topology.
- It does **not** decide D5.0-9, D5.0-10, D5.0-11, D5.0-12 or D5.0-13, and it
  does not begin WP-1, WP-2, WP-4b, WP-14 or WP-15.
- It does **not** claim that the §2.12.6 vector table is exhaustive. Two of its
  rows rest on checks that could not be run on this host without privilege —
  `/etc/sudoers.d/` and a host-wide setuid audit — and both are recorded as not
  run in §8.1 rather than assumed clear.
- It does **not** assert that Google's published APIs definitely contain no
  completion barrier or conditional write. It asserts that **none was found in
  the published surface** across the thirteen candidates of §2.10.1, and invites
  the reviewer to evidence one. A single such citation would overturn the
  conclusion, and that outcome is preferred to the one recorded here.
- It does **not** assert that any test was run. **No test was run for this
  package, because no code exists**; the environment facts in §8.1 are
  observations of this host and each says how it was observed.
- **No implementation or environment change occurred in producing this
  revision.** No production code, migration, table, database role, operating-system
  account, group, `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, credential,
  Google access, configuration, environment variable, deployment path, service
  unit, deployment, service restart, data mutation, Sheet access or authority
  change. **No directory, file, file mode or filesystem attribute was created or
  altered**: `/var/lib/freedom-sheet-writer` does not exist on this host and was
  not created, and no `chattr` was run. **The host was read and never written**:
  the §8.1 observations are the output of `ls`, `getent`, `id`, `df -T`,
  `/proc/mounts`, `lsattr` (read-only), `command -v`, `find`, `uname`,
  `systemctl --version` and `systemctl show`, and `/etc/sudoers.d/` was refused
  rather than read. The changed files are documents and registers.

---

## 11. The comparison-telemetry contract — retained under OD-55

**Unchanged from revision 2.** OD-55 moves the table, write path and schema to
package 5.1. What package 5.0 keeps is the **common contract**, so that 5.1 and
every later package implement one telemetry design rather than each inventing its
own. WP-1 folds this section into
`docs/contracts/phase-5-migration-and-cutover-contract.md` verbatim; nothing here
creates a table, a column or a code path in package 5.0.

**Owner of the implementation: package 5.1**, with its first real shadow
consumer, under its own independently reviewed logical-schema artifact and its
own Security Reviewer confirmation (OD-56).

**What a comparison record must be.**

1. **Bounded.** Every column is a fixed-width scalar or a `CHECK`-constrained
   token. A row must not be able to grow with the size of what it observed.
2. **Value-free by construction.** No `legacy_value`, no `database_value`, no
   `difference_detail`, no `message`, no `exception`, no `payload`, no `JSONB`.
   The guarantee must be structural — there is no column that could receive a
   balance, a name, a raw player value or exception text — rather than a
   redaction rule somebody has to remember. A schema test asserts the column set
   against an allowlist, so a future value column fails the suite.
3. **Incapable of becoming a second authority.** A record with no values cannot
   be read back to reconstruct state, cannot be imported and cannot correct
   anything. A reconciliation that needs values is the owning package's
   supervised migration report, produced under Data Owner approval.
4. **Bound to the authority state it was observed under.** A comparison must
   reference the disposition that was current when it was taken; a mismatch count
   read against the wrong window is not evidence.
5. **Minimal identity.** An internal `character_id` UUID is permitted (OD-56)
   under restricted access and approved retention. No name, no Discord identity,
   no compared value, no exception text, no arbitrary payload. A behavior unit —
   a scheduled job rather than a character operation — records no character at
   all.
6. **Classified vocabularies.** The outcome and the difference class are
   `CHECK`-constrained tokens, not free text.

**What the thresholds require of it.** N5.0-1 … N5.0-3 are counts and rates over
*(unit, disposition, outcome)* in a time window. None of them needs a value, and
that is why (2) costs nothing.

**Operational constraints.**

- **Retention: N5.0-7, 30 days**, swept by an operator command run as the schema
  owner, on the `tools/job_retention.py` pattern. The runtime role gets **no
  `DELETE`**: a process that could delete its own mismatch record could delete
  the evidence that it should be rolled back.
- **Overhead: N5.0-8, ≤ 200 ms added at p95.** A comparison that degrades the
  live Freedom bot violates the governing direction and must be disabled rather
  than tolerated.
- **Growth is the sizing case for 5.1**, whose shadowed command is the highest
  frequency legacy read. Value-free fixed-width rows plus retention are the
  controls; a monitored row count is the signal.
- **Advance approval below the floor.** OD-57's clarification is part of this
  contract: fewer than 30 compared operations before a cutover requires a
  separately approved, package-specific numeric threshold and rationale **before
  shadowing begins**, not a waiver at the gate.

**Where comparison happens at all.** Only in the `shadow` state (logical schema
§2.1). In `cutover` the legacy store is frozen, so a comparison against it would
measure elapsed time rather than correctness; verification in that state is by
invariant checks and the N5.0-5 operational signals. In `legacy` and `database`
there is nothing to compare.

---

## 12. What Phase 4 left, and what is genuinely missing

| Need | Exists | Missing |
|---|---|---|
| Balanced append-only ledger semantics | `domain/ledger.py` | — |
| Idempotent command execution against real PostgreSQL | `application/ledger.py` + `idempotency_keys` | — |
| Typed money and resources in integer smallest units | `domain/money.py`, `domain/quantities.py`, `domain/resources.py` | — |
| Command envelope, receipt, expected version, correlation fence | `application/commands.py` | — |
| Durable ledger posting | — | **the table. R-P4-4, owned by 5.2 (OD-58)** |
| Explicit authority states with a defined read/write matrix | — | **all of it** |
| Cross-process authority agreement | — | **all of it** |
| **A database-enforced write fence** | — | **all of it** |
| **An external-writer boundary as strong as the store allows** | — | **all of it, and it is the largest single item in this package.** Revision 4 also establishes what it *cannot* be: §2.10.2 concludes no accepted-request completion barrier exists in the published Google APIs, so what is missing is the drain, the journal, the fail-closed activation and the detection — not a fence |
| **A host privilege boundary for the authority plane** | — | **all of it. New in revision 4** (§2.12): two OS identities, a peer map, a `sudoers` boundary and a root-owned deployment path. Without it the coordinator principal is a rename rather than a control |
| **Durable, tamper-evident storage for the writer's own dispatch record** | — | **all of it. New in revision 5** (§2.13): a root-owned hierarchy on a verified durable filesystem, a sealed and registered generation, an **acyclic** hash-chained record format, **twenty-five** fail-closed conditions and a privileged lifecycle. Revision 4 assumed a file was enough; **P5.0-R5 is the evidence that it is not** — twice, because revision 5's replacement was itself not implementable — and this is the second control in the package whose absence would have been discovered only in production |
| Comparison telemetry | — | **contract here; implementation is 5.1's (OD-55)** |
| Cutover/rollback procedure and thresholds | — | **all of it** |
