# Baseline and change log

This is the approval record for material project-plan changes. Entries are
append-only; a correction adds a new entry that supersedes an earlier one.

| Version / change | Date | Requester | Summary | Scope / schedule / risk effect | Reviews | Approval |
|---|---|---|---|---|---|---|
| **C-P5.0-AD** | 2026-09-02 | Codex / Security Reviewer | Reconcile the operational runbook and issue Claude's evidence-harness implementation prompt | Corrects the runbook's A-5.0-3/A-5.0-4 inversion; replaces the circular package-gate prerequisite with the approved evidence-only exception; separates synthetic facsimiles from migration `0014` and production objects; and requires Claude to stop for Codex pre-execution review after implementing and testing the isolated harness and exact cleanup plan. No assumption, finding, residual or package gate closes | Documentation consistency and `git diff --check`; privileged evidence not run | **Implements C-P5.0-AC's already-approved authorization; grants no additional authority** |
| **C-P5.0-AC** | 2026-09-02 | Peter Duscha / Operations Owner and Acceptance Authority | Authorize bounded Package 5.0 pre-implementation evidence harness | Resolves the readiness/evidence sequencing circularity through a narrow exception: synthetic disposable scaffolding and privileged evidence collection only, executed by Claude after Codex pre-execution review. All draft exclusions and stop conditions bind. Does not authorize migration `0014`, product implementation, production mutation, deployment, cutover, OD-62 or Package 5.1+ | Codex read-only preflight and authorization draft; independent evidence review still required | **Approved by Peter Duscha 2026-09-02** |
| **C-P5.0-AB** | 2026-09-02 | Peter Duscha / accountable package roles | Approve OD-64 A, OD-65 B and OD-66 A/J-1; record provisional OD-62 G-A direction | Adopts the dedicated coordinator boundary; Sheet-writer isolation, credential relocation, bot hardening, canonical membership and provenance controls; and the full durable sealed/registered journal contract. The group-writable worktree correction is deferred to a separate maintenance change and may not supply deployment inputs. OD-62 remains Open pending P5.0-R5 operational evidence and independent review. Residuals R-5.0-12 through R-5.0-16 are not silently accepted. No implementation, migration, host/database mutation, deployment or cutover is authorized | Revision-12 security design review already delivered; operational and P5.0-R5 review evidence remains outstanding | **OD-64/65/66 approved by Peter Duscha 2026-09-02; OD-62 not ruled** |
| **C-P5.0-AA** | 2026-09-02 | Codex / Security Reviewer | Package 5.0 revision-12 independent security re-review | P5.0-SR1 and P5.0-SR2 Closed on design; twelve-surface security design review delivered. No scope, schema or implementation change. C-1/C-3/C-4, assumptions, operational evidence, P5.0-R1/R4/R5 and residual dispositions remain outstanding. OD-64/65/66 become rulable; OD-62 stays last. Package remains `not ready` and implementation unauthorized | `docs/review/phase-5-0-security-rereview-revision-12.md`; no new Blocking or Important design finding | **Reviewer disposition only; no package/gate approval** |
| **C-P5.0-Z** | 2026-09-02 | Peter Duscha / Acceptance Authority | Accept Phase 4 post-gate R3 disposition and OD-63 Option 1 | **P4-PG4 and P4-PG5 Closed; Phase 4 remains approved and closed.** OD-63's nine values are accepted, including N5.0-18 at **120 seconds — an operational margin, not a barrier**. No scope, architecture, schema, authority, privacy, estimate, migration or release-boundary change. A-5.0-3 remains unconfirmed; no RAID row closes or narrows. OD-62 and OD-64 through OD-66 remain Open; Package 5.0 remains `not ready`; implementation, migration `0014`, host/database mutation, deployment, cutover and Package 5.1+ remain unauthorized | Codex independent R3 review: bot 3103, web 2824/80 expected skips, Foundry 171; no new Blocking or Important Phase 4 finding. OD-63 change-control package signed in all accountable roles | **Accepted by Peter Duscha 2026-09-02** |
| **C-P4-N** | 2026-08-31 | Peter Duscha / Codex Independent Reviewer | Records the two bounded Phase 4 post-gate constructor remediations and the R2 independent disposition | **P4-PG1, P4-PG2 and P4-PG3 Closed.** Discord-user ID, aggregate-type and service-principal-ID boundaries establish type before value operations and preserve their typed errors without coercion. **P4-PG4 and P4-PG5 Open, Important:** malformed idempotency keys escape `invalid_request_key`, and malformed stored receipt command names can escape `StoredReceiptUnreadable` on replay. Phase 4 remains approved; no architecture, authority, schema, migration, deployment, data ownership, phase order or release-boundary change. Per maintainer direction, Package 5.0 preparation pauses for one final bounded correction; Package 5.0's own `not ready` state and implementation prohibition are unchanged | Codex independently ran 121 command tests, the 62-case PG1–PG3 selection, both prescribed `compileall` checks and a scoped whitespace check. Claude's submitted full evidence: bot 2989, web 2824/80 expected skips, Foundry 171. Durable review: `../review/phase-4-post-gate-r2-independent-review.md` | **P4-PG1–PG3 closed by Independent Reviewer. P4-PG4/PG5 remediation authorized by maintainer request; Codex re-review required before Phase 5 preparation resumes** |
| **C-P5.0-Y** | 2026-08-31 | Working Technical Lead (implementer) | Package 5.0 **security remediation R11** — revision 12 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r11-handback.md` and an updated security-review briefing pack | **Scope:** the design grows. **P5.0-SR1** is answered by a new package-plan **§2.12.5a**, a fail-closed reviewed-source provenance contract: an out-of-band `root:root 0444` approved-revision record; a **bare `root:root 0700` Git object store** addressed **by object id**, with no ref, branch or tag resolved anywhere; a trusted manifest computed from **Git object bytes** and compared against a **SHA-256** the approval record carries, so the binding does not rest on Git's SHA-1; a **closed two-region partition** of the deployed root in which an unaccounted file refuses; **Algorithm D `D0 … D8`** with refusals `DEP-01 … DEP-09` and a rollback; and a provenance record written last, outside the deployed root. `init-generation` **C0 refuses when it is absent**; the seal carries the commit, tree and source-manifest values; the writer re-checks them at new step **W11a**; and a **`NOT NULL` foreign key** to the new `approved_source_revisions` table means **an unprovenanced generation cannot be registered, so activation cannot be reached**. `JNL-51` case (g) is the negative test the finding required. **P5.0-SR2** is answered by making **§2.12.2 the single canonical primary/supplementary membership table** with a group→members inverse and a rule that no other passage states a membership; the false isolation sentence is **withdrawn**, `E8` gains `freedomjournal`, and `JNL-52`'s eight cases are the review's check **C-4**. **Schema:** seven tables instead of six, four columns on `sheet_writer_journal_generations`, two foreign keys, a fifth append-only trigger, one new closed vocabulary. **Schedule:** PERT **40.9 → 47.6** implementer-days, remediation allowance 11.9 → 13.9, security review **3.5–4.5 → 4.5–5.5** reviewer-days over **twelve** surfaces — all decomposed in §4 and §9.2. **Risk:** two residuals proposed and unaccepted — **R-5.0-15** (the approval record's integrity is root ownership; an actor holding host root *and* the coordinator's `sudo` path approves and registers its own revision — operator trust, not a technical control) and **R-5.0-16** (an unprovenanced deployment cannot produce a generation, which is fail-closed and an availability cost). §7.1 gains rows 29–30; stop conditions **10o** and **10p** are added and **condition 4 is extended** so a named-but-undelivered security review stops the gate. One pre-existing stale figure is corrected and reported: §5.1's R-03 estimate still read 35.5. **No baseline, implementation or environment change.** No host object was created — no account, group, directory, Git repository, object store, approval record or provenance record — and **no `git` write was performed** | **Claims no finding closed.** P5.0-SR1 and P5.0-SR2 are the Security Reviewer's; P5.0-R5 remains Blocking; P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed. `git diff --check` clean; counts and estimates re-derived by two independent routes that agree | **Requires an independent security re-review of revision 12.** Not approved; **OD-62 … OD-66 must not be ruled from it**; Package 5.0 remains `not ready` |
| **C-P5.0-X** | 2026-08-31 | Security Reviewer (Codex) | Package 5.0 **security review of revision 11** — the distinct §9.2 pass, first run | **Outcome: changes requested; no readiness recommendation.** **P5.0-SR1 — Blocking:** the deployment integrity check can be skipped silently; `deployment_manifest_digest()` proves consistency after deployment, not provenance from the reviewed commit, and nothing refuses when the comparison against the commit is omitted. **P5.0-SR2 — Important:** §2.12.2's *"own groups only"* contradicted §2.13.3's `freedomjournal` requirement and the E1–E8 identities. Host check **C-1 not completed** (`/etc/sudoers.d` not readable); **C-2 completed as an inventory**; **C-3 and C-4 not run by design**. The three declared residuals are **not accepted**. No baseline, implementation or environment change | Reviewer also holds Independent Reviewer and logical-schema reviewer, so the design and security judgements are not independent of each other — recorded, and accepted knowingly under OD-61 | Rules nothing; approves no gate. P5.0-R5 remains Blocking; OD-62 … OD-66 remain Open; Package 5.0 remains `not ready` |
| **C-P5.0-W** | 2026-08-31 | Acceptance Authority / Product Owner (Peter Duscha) | Package 5.0 Security Reviewer named — **Codex** — closing OD-61 / D5.0-8 | **Scope:** none. No requirement, option, schema object, numeric control, risk, assumption or finding changes. The §9.2 security surface stays at eleven and the estimate at 3.5–4.5 reviewer-days. **Schedule:** the readiness path unblocks in one place only — OD-64, OD-65 and OD-66 are owned *on the Security Reviewer's review* and become rulable once the recommendation exists; OD-63 was never gated on it and is rulable now; OD-62 stays last. **Risk:** Codex now holds the Independent Reviewer, logical-schema reviewer and Security Reviewer roles for this package, so the design and security judgements are no longer independent of each other. That concentration is accepted knowingly by the Acceptance Authority and recorded in the OD-61 trace; it is compatible with §0.3, which bars approving one's own implementation, because Codex did not implement Package 5.0. **No new baseline version**: this is a role assignment, not a change to roadmap or release boundary | Cross-document consistency scan of all eight controlled documents found no contradiction; `git diff --check` clean. **No security review was performed** — the revision-11 design re-review is not the §9.2 pass and is not cited as one | **Assignment approved and effective. It approves no option, closes no finding and confirms no assumption.** P5.0-R5 remains Blocking; P5.0-R1 and P5.0-R4 open; OD-62 … OD-66 Open; A-5.0-3/4/5 unconfirmed; Package 5.0 `not ready`; implementation, migration, deployment, cutover and Package 5.1+ unauthorized |
| **C-P5.0-V** | 2026-08-31 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 11 / remediation R10 | No new Blocking or Important design finding. R10-A through R10-C are materially addressed on paper: the `capsh(1)` construction has documented ordering, declares the launching bounding-set prerequisite, derives E1–E8 P/E/I/A/B masks and corrects the isolating controls. This closes the remediation request only; no schema object, option, risk, decision, package finding or gate closes. P5.0-R5 remains Blocking pending authorized operational evidence; P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed; OD-62 through OD-66 remain Open; Security Reviewer unnamed; Package 5.0 not ready; implementation unauthorized | Complete governing-document and revision-11 design/schema review; installed `setpriv`/`capsh` contracts and capability-mask decoding checked non-mutatingly; `git diff --check` clean. No implementation or privileged suites: documentation/design-only and A-5.0-5 unconfirmed | **R10 remediation request closed by the Independent Reviewer. No package/gate approval requested; readiness and authorization work remains** |
| **C-P5.0-U** | 2026-08-31 | Technical Lead (implementer) | Package 5.0 design remediation **R10** — revision 11 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r10-handback.md`; **claims no Blocking finding closed** | No baseline, implementation or environment change. R10-A replaces the E2–E6 launch recipes: `setpriv(1)` 2.39.3 documents `keep_caps` as not allowed, so those commands exited 127; the mechanism becomes `capsh(1)` (already installed, `root:root 0755`, no file capabilities), because `setpriv(1)` does not document the option ordering every declared mask depends on. R10-B gives `E1 … E8` exact UID, GID, supplementary groups, P/E/I/A/B **and securebits** with complete invocations and a mask-versus-recipe comparison; a **third** recipe/mask disagreement not named by the review is recorded — E2–E6 asked to **add** to a bounding set, which the kernel forbids. R10-C revalidates dependent evidence: `JNL-50` case 7 and `JNL-49` case 11 take **E6** rather than **E2** as the isolating control, `JNL-50` case 4 gains a second control form, and two stale copies of superseded wording in the logical schema are corrected. **Evidence band (50 identifiers, 88 cases), estimate (PERT 40.9), remediation allowance (11.9) and security review (3.5–4.5 reviewer-days) are unchanged, with the reason stated rather than recalculated.** New stop condition **10n** and §7.1 risk row **28**; **A-5.0-5 widened and still unconfirmed**; no risk, decision, option or schema object added or closed | Self-review against `.agents/AGENTS.md`, the implementation plan and the R10 brief; **non-mutating** checks only — `setpriv --version`, `capsh --decode`, `dpkg`, `ls`, `getcap`, `getent`, `/proc/*/status` and installed `setpriv(1)`, `capsh(1)`, `capabilities(7)` and `linux/securebits.h`; independent recomputation of every capability mask; mechanical mask-versus-recipe comparison; Markdown whitespace, table-shape, heading-order, link and stale-wording checks; `git diff --check` clean. **Implementation and privileged suites not run** — the submission is documentation/design-only, A-5.0-5 is unconfirmed and host changes are unauthorized | **Not requested and not granted. Independent re-review of revision 11 required.** P5.0-R5 remains Blocking; P5.0-R1 and P5.0-R4 open; P5.0-R2 closed; D5.0-9 … D5.0-13 / OD-62 … OD-66 Open; Security Reviewer unnamed; Package 5.0 `not ready`; implementation unauthorized |
| **C-P5.0-T** | 2026-08-31 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 10; remediation R10 requested | No baseline, implementation or environment change. R9-A and R9-B are materially improved. R9-C remains Blocking because E2–E6 use a `setpriv` securebit rejected by util-linux 2.39.3, E8's recipe does not produce its declared empty bounding set, and E7 omits complete masks. No risk, decision, option, schema object or estimate changes | Complete governing-document and artifact review; installed `setpriv` 2.39.3 manual and Linux capability definitions checked; `git diff --check` clean. No implementation or privileged suite run because the submission is documentation/design-only and host changes are unauthorized | **Changes requested. P5.0-R5 remains Blocking; Package 5.0 remains not ready; implementation unauthorized; remediation R10 and independent re-review required** |
| **C-P5.0-S** | 2026-08-30 | Technical Lead (implementer) | Package 5.0 design remediation **R9** — revision 10 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r9-handback.md`; **claims no Blocking finding closed** | No baseline change and **no implementation**: no production code, no migration `0014`, no database, host, service, credential, Google-access or deployment change, no directory, file, file mode or filesystem attribute, no `systemd-run`, no `chattr`, no `setpriv`, no privileged probe, no reboot, no data mutation, no Sheet access, no authority cutover and no Package 5.1+ work; the host was neither read nor written. **R9-A:** `FS_IOC_SETFLAGS` requires the caller's effective UID to equal the inode's owner **or** `CAP_FOWNER`, in addition to `CAP_LINUX_IMMUTABLE` for the immutable and append flags, and `CAP_DAC_OVERRIDE` is not a substitute; package plan §2.13.5c is redesigned from nine authorities to **eleven**, with **A1** narrowed to the capability half and **A10**/**A11** carrying the owner authorization over the `freedomsheet`-owned journal and the root-owned seal and archive. **Eleven of the thirteen falsification rows gain a prerequisite**, every such change making the alteration **harder** to construct; §2.13.4 grows from thirteen manipulation rows to **fifteen**; §2.13.5b and §2.13.7 are restated. **R9-B:** the register keeps its independence claim for the primitives, a new **holder table** carries the bundling of real identities, and detector reach is assessed against the smallest identity that can hold each combination — **narrowing** the bounded claim to F-2, F-3 and F-6. **R9-C:** eight executable identities `E1 … E8` with complete permitted, effective, inheritable, ambient and bounding capability sets and securebits, and `JNL-49`/`JNL-50` rewritten at **twelve cases each** with a positive control beside every negative flag case; **A-5.0-5 is corrected and remains unconfirmed**, and **no privileged case is claimed to have run**. **Preserved unchanged in substance:** the R8-A deployment-digest lifecycle, the R8-B cleanup state machine and the R8-D withdrawal of F-7's detector. Evidence band **84 → 88 cases**, **no identifier added** (50); §6.5 items **19 → 20**; new stop condition **10m**, **10k** extended; new §7.1 risk row **27**; **no RAID row added or closed** — R-5.0-12's authority set corrected to a larger one; **no schema object changes**. Estimate **PERT 40.4 → 40.9** implementer-days; remediation allowance **11.9**; security review **3.5–4.5** reviewer-days. **No decision number and no option is added; OD-62 … OD-66 remain Open and must not be ruled from revision 10; OD-66 option A's content does not move.** | Independent re-review by Codex **requested, not yet performed**. Security Reviewer **unnamed**. | **Not approved.** Package 5.0 remains `not ready`; P5.0-R5 remains **Blocking**; implementation remains unauthorized |
| **C-P5.0-R** | 2026-08-30 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 9; remediation R9 requested | No baseline, implementation or environment change. R8-A, R8-B and R8-D are materially addressed. R8-C remains Blocking: Linux `FS_IOC_SETFLAGS` requires inode ownership or `CAP_FOWNER` in addition to `CAP_LINUX_IMMUTABLE` for immutable/append flags, so the non-root capability-only archive case and several stated minimum combinations are not executable. The A1–A6 independence assertion also contradicts F-1a's A3-implies-A2 qualification. No finding, risk or decision closes | Complete governing-document, design/schema, authority-model, evidence-contract and cross-document review; primary Linux `FS_IOC_SETFLAGS` semantics checked; whitespace checks clean. No implementation or privileged checks because the submission is documentation/design-only | **Changes requested. P5.0-R5 remains Blocking; Package 5.0 remains not ready; implementation unauthorized; remediation R9 and revision-10 independent re-review required** |
| **C-P5.0-Q** | 2026-08-30 | Technical Lead (implementer) | Package 5.0 design remediation **R8** — revision 9 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r8-handback.md`; **claims no Blocking finding closed** | No baseline change and **no implementation**: no production code, no migration `0014`, no database, host, service, credential, Google-access or deployment change, no directory, file, file mode or filesystem attribute, no `systemd-run`, no `chattr`, no `setpriv`, no probe and no probe arena. All four Blocking inconsistencies are conceded and corrected. **R8-A:** new **§2.13.2c** defines `deployment_manifest_digest()` — its computor, its exact manifest (every deployed file with path, mode, uid, gid and content digest, plus the unit file **and its `.service.d/` drop-ins**) and when it becomes final — and Algorithm C **`C0` computes it and refuses unless the operator's supplied value equals it**, discarding the supplied string, so `C1` consumes a value validated against the **deployed bytes** and not against a copy of itself; **`C2`** keeps a consistency check against the report **and recomputes the manifest** to detect a deployment changed between `C0` and the probe's capture. The universal *produced < validated ≤ consumed* claim is **withdrawn** for five invariants **I-1 … I-5** separating **pre-consumption validation of external inputs** from **post-production consistency checking of internally produced values**; the value table gains a class column and the dependency graph a `[computed & compared, C0]` gate. `JNL-46` grows from one case to **five** — the ordered walk plus a malformed digest, a wrong digest, a deployment changed between `C0` and `C1`, and a report whose field differs from the validated input, each refusing before `C5` and creating no generation artifact. **R8-B:** new **§2.13.2b** replaces the contradictory cleanup evidence with one state machine of three states — probe-stage failure with cleanup succeeding (no residue, no artifact), cleanup failure (no artifact, exact residue reported by absolute path with its failed operation and `errno`), and success — in which **“no generation artifact” is unconditional and “no transient residue” is conditional on cleanup success**. For the next invocation the design specifies **one** behaviour and not two: `verify-capability` and `C0` **refuse for operator recovery**, and revision 8's *"reports it, cleans it as an explicit first step"* is **withdrawn**; recovery is a named operator procedure in the WP-9 operations document. `JNL-30`, `JNL-47` (5 → **6** cases), `JNL-48(d)`, the failure-cost table, §2.13.4, §2.13.7, WP-8/WP-9/WP-15 and logical-schema §4.3.8/§9 are reconciled. **R8-C:** the eight-capability register is **withdrawn**, because it credited `CAP_LINUX_IMMUTABLE` with discretionary access it does not confer — a non-root holder clears `+i` on a `0440 root:freedomcoord` archive file and still receives `EACCES` on the open. In its place, **nine independently constructible authorities** (`A1` flag control, `A2` DAC on the journal file, `A3` DAC on `…/journal` and its seal, `A4` DAC on `…/archive`, `A5` DAC on the deployment path, `A6` host identity/restoration, `A7` full host-root identity, `A8` coordinator authentication/insertion, `A9` PostgreSQL mutation), with every falsification row stating its minimum **combination**, detector reach, refusing actor, exact step and code, and residual. **F-2 → `A1 + A2`** (the writer already owns its journal file, so the flag is the whole of what refuses it), **F-4 → `A1 + A4`**, **F-5 → `A1 + A3`** (an `+a` victim cannot be unlinked or renamed over). An *achieved ability* is separated throughout from the privileges that achieve it; `JNL-49` and `JNL-50` grow to **ten cases each** and their new cases are executed under a **non-root `CAP_LINUX_IMMUTABLE`-only ambient capability set** rather than simulated as root. **R8-D:** **F-7's refusal is withdrawn.** When **`A6`** rewrites `/etc/machine-id` to the recorded value, `SB.host_machine_id`, the file and the registered row all carry it, so **W10 passes and C-d has nothing to disagree with**; the changed-device/inode reasoning is withdrawn as incidental, since those are refused as **F-5**/**F-10**/**F-11** by a *named* field and a restore that preserves them is refused by nothing. The case becomes residual **R-5.0-13** with the independent operational evidence that remains named; `JNL-40` grows to **two** cases, `JNL-49` case 3 is rewritten to assert the non-refusal, and logical-schema §3.7's `host_machine_id` rule, §3.7.1 and §9 are corrected — **two of the four corrections remove a claim rather than replace it**. **Schedule effect:** estimate PERT **39.5 → 40.4** implementer-days (WP-8 +0.53, WP-15 +0.20, WP-9 +0.12, WP-4b +0.08; all other packages unchanged); remediation allowance 11.5 → **11.9**; contingency and independent review **unchanged**; security review **2.5–3.5 → 3.0–4.0** reviewer-days with **no added surface** — the cost is a nine-authority threat model whose combinations must each be checked against real Unix DAC, plus a second unrefused residual — and **two added questions**. **Risk effect:** the evidence band grows from seventy-four cases to **eighty-four** across the **same fifty identifiers**, **no identifier being added**; §6.5 items 18 → **19**; new stop condition **10l**, with **10b**, **10f** and **10h** extended and **10j** re-worded; new §7.1 risk rows **25** and **26** and RAID rows **R-5.0-13** (a forged matching `/etc/machine-id` is detected by nothing in this design — an acceptance question, not a control) and **R-5.0-14** (a failed privileged cleanup leaves a writer-writable transient directory and blocks generation creation until an operator acts); **A-5.0-5 widened again** — a non-root ambient `CAP_LINUX_IMMUTABLE` set, and a second host or a host whose `/etc/machine-id` may be rewritten — and **remains unconfirmed**; R-5.0-9, D-5.0-1 and D-5.0-2 extended; **R-5.0-12 retained unchanged and relabelled** to the new authority names. **Falsification rows stay at thirteen, fail-closed conditions stay at twenty-five, refusal codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps, numeric controls stay at nine, security-review surfaces stay at eleven, and no schema object changes at all** — no column, constraint, index, trigger, sequence, vocabulary, table or command. **No new decision number and no new numeric control**; **OD-66 records an amended option-A content in two places and gains a new option A-2** — option A plus an independent authenticated host-bound value, which would make F-7 a refusal but whose principal price is a legitimate restore onto replacement hardware that fails closed — **routed under §0.2 and explicitly not adopted**; OD-62 … OD-65 are unchanged. P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed | Self-review of the design, schema and controlled registers against the R8 remediation brief. **`git diff --check` clean, exit 0, no output**; and, because the design artifacts are untracked, `git diff --no-index --check /dev/null <file>` run for the package plan, the logical schema, this remediation's handback and the superseded R7 handback — **no whitespace error reported for any of them**, verified against a control file that does report one. A programmatic Markdown table-integrity check was run over both design artifacts, ignoring escaped pipes, and reported **no column-count mismatch**. The stale-form searches the brief requires were run across the package plan, the logical schema, the implementation plan, `docs/project-management/` and `docs/discovery/open-decisions.md`, and every surviving hit is recorded in the handback §9 as a definition, a corrected use, a labelled retained-history row or a marked quotation; **one live stale claim was found and fixed** — Algorithm C step `C5` still said every refusal above it *"leaves the tree untouched"*. Edited Markdown inspected for corruption, missing words, duplicated fragments and table column consistency. **No implementation suite was run, because no code exists for this package and none changed**; every privileged, reboot, filesystem-fault, `systemd-run`, capability-set, second-host and security check is named as not run, with its owner | **Submitted for independent re-review. Not approved. Package 5.0 remains `not ready` and implementation remains unauthorized** |
| **C-P5.0-P** | 2026-08-30 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 8; remediation R8 requested | No baseline, implementation or environment change. Four Blocking findings: Algorithm C consumes the deployment digest before its stated validation; cleanup-failure evidence requires mutually exclusive residue outcomes; the K3/K4 boundary treats `CAP_LINUX_IMMUTABLE` as bypassing archive DAC; and F-7 names no independent detector for a forged matching `/etc/machine-id`. R7-B's exact S4-2 positive control is retained subject to cleanup correction. No risk or decision closes; OD-62 through OD-66 remain open | Complete governing-document, design/schema, threat-model, lifecycle and cross-document review; `git diff --check` and untracked-artifact whitespace checks clean. No implementation or privileged checks because the submission is documentation/design-only | **Changes requested. P5.0-R5 remains Blocking; Package 5.0 remains not ready; implementation unauthorized; remediation R8 and revision-9 independent re-review required** |
| **C-P5.0-O** | 2026-08-30 | Technical Lead (implementer) | Package 5.0 design remediation **R7** — revision 8 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r7-handback.md`; **claims no Blocking finding closed** | No baseline change and **no implementation**: no production code, no migration `0014`, no database, host, service, credential, Google-access or deployment change, no directory, file, file mode or filesystem attribute, no `systemd-run`, no `chattr`, no `setpriv`, no probe and no probe arena. All three Blocking defects and the one Important governance defect are conceded and corrected. **R7-A:** Algorithm C is renumbered **`C0 … C13`** — `C0` checks only pre-probe preconditions and reads no probe result, `C1` remains the single invocation of the probe stages and the single creation point of the report, and a new **`C2`** validates pass state, report completeness, deployment-digest equality and cleanup success **before any persistent artifact exists** — with a **value-dependency table** proving *produced < validated ≤ consumed* per value, the dependency graph carrying a `[validated, C2]` gate, `verify-capability`/`init-generation` preconditions split by when they can be known, and new tests `JNL-46` (ordered walk) and `JNL-47` (five failure injections proving no journal, seal, symlink or registration row is created). **R7-B:** Stage 4 gains an exact target and a positive DAC control — `…/probe-ro/s4-2.target` in a second transient directory `root:freedomsheet 0770` on the same mount, inside `ProtectSystem=strict`'s read-only tree and outside the substituted `ReadWritePaths=`; new case **`S4-0`** proves open, append, `fsync`, `rename` and `unlink` permitted by DAC on that exact file under the writer's uid **outside any unit**; only then is `EROFS` accepted, `EACCES` is **`inconclusive`** and a sandboxed success is a **failed** stage. Stage 4's cases become **`S4-0 … S4-3`**, the canonical probe bytes, the hierarchy, the manipulation matrix, the cleanup `finally` and the `C0` refusal all follow, and `JNL-48` distinguishes the four required outcomes. **R7-C:** the two-class attacker model and every *“reaches every row except”* claim are **withdrawn** for an **eight-capability register** (`K1 … K8`), with each falsification row stating its **minimum capability**, whether that capability **also reaches the detector**, the **independent actor or artifact** that refuses it, the **exact step and code**, and the **residual when it reaches both**; **F-2 corrected to `K3`**, **F-7 corrected in the opposite direction** because `/etc/machine-id` is root-writable, F-3 … F-12 re-evaluated, the identity boundary between `CAP_LINUX_IMMUTABLE` alone, full root and a PostgreSQL superuser stated, not-constructible pairings marked **with the control that makes them so**, and `JNL-49`/`JNL-50` added. **R7-D:** implementation-plan §20's correction to revision 7 / R7 is **preserved** and extended to name revision 8 as the submitted response; status, RAID, decisions, open decisions and this log all name **R7** as the active cycle. **Correction:** the falsification-row count is corrected from a stated **twelve** to the **thirteen** actually listed. **Schedule effect:** estimate PERT **38.2 → 39.5** implementer-days (WP-8 +0.87, WP-15 +0.30, WP-9 +0.10; all other packages unchanged); remediation allowance 11.1 → **11.5**; contingency, independent review and security review **unchanged**, security review staying at 2.5–3.5 reviewer-days with one added surface element (`…/probe-ro`) and two added questions. **Risk effect:** the evidence band grows from forty-five identifiers / forty-eight cases to **fifty / seventy-four**; new stop conditions **10i**, **10j** and **10k**; new §7.1 risk row **24** and RAID row **R-5.0-12** — the combined-authority residual (host root **and** PostgreSQL superuser) that **no check in this design refuses**, recorded for the Acceptance Authority rather than mitigated; **A-5.0-5 widened again** to a second transient directory and the `S4-0` control and **remains unconfirmed**; R-5.0-9, D-5.0-1 and D-5.0-2 extended. **Fail-closed conditions stay at twenty-five, refusal codes stay `SW-J01 … SW-J25`, and V-W stays at eighteen steps.** **No schema object changes at all** — no column, constraint, index, trigger, sequence, vocabulary, table or command. **No new decision number and no new numeric control**; OD-66 records an amended option-A content in three places and is **not decided**; OD-62 … OD-65 are unchanged. P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed | Self-review of the design, schema and controlled registers against the R7 remediation brief. **`git diff --check` clean, exit 0, no output**; and, because the design artifacts are untracked, `git diff --no-index --check /dev/null <file>` run for the package plan, the logical schema, this remediation's handback and the superseded R6 handback — **no whitespace error reported for any of them**, verified against a control file that does report one. The thirteen stale-form searches the brief names were run across the package plan, the logical schema, the implementation plan, `docs/project-management/` and `docs/discovery/open-decisions.md`, and every surviving hit is recorded in the handback §9 as a definition, a corrected use, a labelled retained-history row or a marked quotation. Edited Markdown inspected for corruption, missing words, duplicated fragments and table column consistency; one pre-existing duplicated line in the logical schema's revision-5 re-review paragraph was removed. **No implementation suite was run, because no code exists for this package and none changed**; every privileged, reboot, filesystem-fault, `systemd-run` and security check is named as not run, with its owner | **Submitted for independent re-review. Not approved. Package 5.0 remains `not ready` and implementation remains unauthorized** |
| **C-P5.0-N** | 2026-08-30 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 7; remediation R7 requested | No baseline, implementation or environment change. Three Blocking findings: C0 consumes the probe result before C1 creates it; S4-2 attributes `EROFS` without a positive DAC control on its exact target; and the falsification attacker classes exceed their defined capabilities. One Important finding: implementation-plan §20 still identified the obsolete R5 brief as active | Complete governing-document read; design/schema, handback, threat-model and cross-reference review; `git diff --check` clean. No implementation or privileged checks because the submission is design-only | **Changes requested. P5.0-R5 remains Blocking; Package 5.0 remains not ready; implementation unauthorized; remediation R7 and independent re-review required** |
| **C-P5.0-M** | 2026-08-30 | Technical Lead (implementer) | Package 5.0 design remediation **R6** — revision 7 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r6-handback.md`; **claims no Blocking finding closed** | No baseline change and **no implementation**: no production code, no migration `0014`, no database, host, service, credential, Google-access or deployment change, no directory, file, file mode or filesystem attribute, no `systemd-run`, no `chattr`, no `setpriv` and no probe. All four revision-6 defects are conceded and corrected. **R6-A:** the capability probe's **stage 4 moves from deployment to provisioning**, inside the same `verify-capability` invocation and **before** the probe report is built, with named cases `S4-1 … S4-3`, the deployed unit's directive set captured and hashed, and invalidation reusing the existing rotation rule — so `append_only_probe_digest` covers the four stages it names. The re-review's option 2 is priced and rejected in the same table, and **no second artifact, digest, authority, storage location, invalidation rule, column or refusal code is introduced**. **R6-B:** the seal's binding section loses `sealed_at` and its own format field, keeping exactly the three values V-W recomputes or compares, with its structure fixed by a `binding_format_version` carried in the chain-authenticated seal body; a complete binding-field authentication table is added; **F-1 is split** into **F-1a** (refused by the writer with no database) and **F-1b** (a `CAP_LINUX_IMMUTABLE` rewrite of seal **and** record 0, refused **only** by the coordinator against PostgreSQL), two attacker classes are stated, and **F-9 … F-12** are added. **R6-C:** `JNL-32` becomes `JNL-32a` (successful start, exactly one appended `startup` record) and `JNL-32b` (`+a` absent: refusal at **W9** with `SW-J06` before **W17**, no write-mode journal open, nothing appended, evidence byte-for-byte unchanged), corrected in every dependent statement. **R6-D/E:** a complete handback, and C1's *“written in C4”* corrected with `M-1`, `M-2` and `S4-1 … S4-3` defined. **Schedule effect:** estimate PERT **37.7 → 38.2** implementer-days; remediation allowance 11.0 → **11.1**; contingency, independent review and security review **unchanged**, security review staying at 2.5–3.5 reviewer-days with one added surface element and one added question. **Risk effect:** the evidence band grows from forty-one identifiers / forty-two cases to **forty-five / forty-eight**; falsification rows eight → **twelve**; new stop condition **10h**; new risk row §7.1 **23**; **A-5.0-5 widened** to require `systemd-run` and a deployed writer unit at provisioning and **remains unconfirmed**; R-5.0-9, D-5.0-1 and D-5.0-2 extended. **Fail-closed conditions stay at twenty-five and refusal codes stay `SW-J01 … SW-J25`.** **No schema object changes at all** — no column, constraint, index, trigger, sequence, vocabulary, table or command; `sealed_at` was never a database column. **No new decision number and no new numeric control**; OD-66 records an amended option-A content and is **not decided**; OD-62 … OD-65 are unchanged. P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed | Self-review of the design, schema and controlled registers against the R6 remediation brief. **`git diff --check` clean.** The ten stale-form searches the brief names were run across the package plan, the logical schema, `docs/project-management/` and `docs/discovery/open-decisions.md`, and every surviving hit is recorded in the handback §9 as a definition, a corrected use or a marked quotation. Edited Markdown inspected for corruption, missing words, duplicated fragments and table column consistency. **No implementation suite was run, because no code exists for this package and none changed**; every privileged, reboot, filesystem-fault, `systemd-run` and security check is named as not run, with its owner | **Submitted for independent re-review. Not approved. Package 5.0 remains `not ready` and implementation remains unauthorized** |
| **C-P5.0-L** | 2026-08-30 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 6; remediation R6 requested | No baseline, implementation or environment change. Two Blocking findings: the sealed probe report cannot contain deployment-time stage 4 under Algorithm C's stated order, and F-1 overclaims writer-only detection because V-W does not authenticate `BND.sealed_at`. Two Important findings: `JNL-32` contradicts W9/W17, and the active handoff is corrupted/truncated | Complete governing-document read; design/schema and cross-reference review; `git diff --check` clean. No implementation or privileged checks because the submission is design-only | **Changes requested. P5.0-R5 remains Blocking; Package 5.0 remains not ready; implementation unauthorized; remediation R6 and independent re-review required** |
| **C-P5.0-K** | 2026-08-30 | Technical Lead (implementer) | Package 5.0 design remediation **R5** — revision 6 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r5-handback.md`; **claims no Blocking finding closed** | No baseline change and **no implementation**: no production code, no migration `0014`, no database, host, service, credential, Google-access or deployment change, no directory, file, file mode or filesystem attribute. All four revision-5 defects are conceded and corrected — an **acyclic** seal-body/genesis/seal-digest construction with numbered creation (C0–C12) and verification (V-W, V-C, V-R) algorithms and falsification cases F-1 … F-8; a **minimum read-only** seal grant through a new system group `freedomjournal`, with `…/journal` tightened from `0751` to `0750` so the net grant is narrower than revision 5's; a **four-stage, disposable-arena** capability probe with control cases, expected `errno` attribution, non-destructive startup checks and privileged cleanup; and the **withdrawal** of `CHECK (append_only_verified)` in favour of an attested, re-derivable probe report with an explicit enforces-versus-records division. **Schedule effect:** estimate PERT **35.5 → 37.7** implementer-days; security review **2.0–3.0 → 2.5–3.5** reviewer-days over an eleven-element surface. **Risk effect:** R-5.0-11's bounded-outage surface grows with the fail-closed conditions, twenty-one → **twenty-five**; the evidence band grows twenty-six → **forty-one** cases and still needs unconfirmed **A-5.0-5**. **No new decision number**; OD-62 and OD-66 record impacts and are **not decided**; OD-65 gains a fourth item. P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed | Self-review of the design, schema and controlled registers against the R5 remediation brief. **`git diff --check` clean.** Edited Markdown inspected for corruption, missing words, duplicated fragments and table column consistency. **No implementation suite was run, because no code exists for this package**; every privileged, reboot, filesystem-fault and security check is named as not run | **Submitted for independent re-review. Not approved. Package 5.0 remains `not ready` and implementation remains unauthorized** |
| **C-P5.0-J** | 2026-08-29 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 5; keeps P5.0-R5 Blocking and requests remediation R5 | No baseline or implementation change. The durable path correction is retained, but the generation design is not implementable: seal and genesis hashes are circular; the writer cannot read the seal it must validate; the capability probe is masked by ordinary permissions and is unsafe against the live journal when `+a` is absent; and the Boolean check cannot prove a probe ran. P5.0-R1 and P5.0-R4 remain open; P5.0-R2 remains closed | Complete design/schema and controlled-register review. `git diff --check` failed because the submitted handoff contained trailing whitespace and corrupted text. No implementation tests were run because Package 5.0 remains design-only | **Changes requested. Remediation R5 and independent re-review required; Package 5.0 remains not ready and implementation unauthorized** |
| **C-P5.0-I** | 2026-08-29 | Technical Lead / implementer (Claude) | Package 5.0 **design remediation R4** — revision 5 of the package plan and the logical schema, plus `docs/review/phase-5-0-remediation-r4-handback.md`. **Claims no finding closed** | No baseline, phase-order, authority, privacy or data-ownership change, and no implementation. **P5.0-R5:** the dispatch journal moves from volatile `/run` to a root-owned durable hierarchy at `/var/lib/freedom-sheet-writer/journal/` on the ext4 root volume — established by **reading** `/proc/mounts` and `df -T`, not inferred — in a directory the writer cannot write, so it can neither unlink, rename, replace nor create there; `chattr +a` becomes a second layer and is **probed at provisioning and at every writer start**, with a generation whose probe failed unable to be registered (`CHECK (append_only_verified)`); a `chattr +i` seal, a genesis record and a **registered generation** in a new sixth table must agree, so a reset journal is never a valid empty history; **twenty-one conditions all fail closed**; and a privileged root-run `freedom-journal-admin` owns seal, rotate, repair, archive-verify and a `dispose` gated on retention, the §15.1 gate and a Data Owner approval. **The completeness contradiction is resolved by withdrawing the false statement and keeping the control**, with the remainder named as **R-5.0-10**. **P5.0-R1 unchanged and not claimed closed — a durable journal is not a barrier and R-5.0-8 is not narrowed.** **P5.0-R4 unchanged apart from two denial rows; no operational evidence claimed passed.** P5.0-R2, OD-55 and OD-58 preserved. **Schedule/risk:** PERT **29.2 → 35.5** implementer-days; remediation allowance 8.4 → 10.3; contingency 3.5 → 4.0; security review 1.5–2.5 → **2.0–3.0** reviewer-days; new work package **WP-15**; numeric controls six → **nine**; new decision **OD-66**; new risks **R-5.0-10**, **R-5.0-11**; new assumption **A-5.0-5**; R-5.0-3 and R-5.0-9 extended | Design and documentation only. Host read and never written: `df -T`, `/proc/mounts`, `ls -ld`, `lsattr` (read-only), `getent`, `id`, `command -v`, `uname -r`, `systemctl --version`, `systemctl list-units`. **`git diff --check` clean.** **No test was run because no code exists for this package**; no executable control is claimed to have passed. Checks not run and named: whether `chattr +a` is honoured at the journal path (needs `CAP_LINUX_IMMUTABLE`; **A-5.0-5**), a supervised host reboot, an injected `fsync` failure, `/etc/sudoers.d/` enumeration, a host-wide setuid audit, `log_connections`, and the live `pg_hba.conf`/`pg_ident.conf` | **Returned for independent re-review. Claude claims no finding closed; Package 5.0 remains `not ready` and implementation remains unauthorized.** OD-62 must not be ruled until the Independent Reviewer accepts that the enumeration control is fail closed |
| **C-P5.0-H** | 2026-08-29 | Independent Reviewer (Codex) | Independent re-review of Package 5.0 revision 4; raises P5.0-R5 and requests remediation R4 | No baseline or implementation change. P5.0-R1 remains Blocking. The journal path under `/run` is on volatile `tmpfs`, not the ext4 filesystem used to justify `chattr +a`; missing/replaced/rebooted state can falsely appear clear, and the plan contradicts itself about whether activation depends on completeness. P5.0-R4's identity design substantially answers the design finding but still requires operational/security evidence and OD-64/OD-65. P5.0-R2 remains closed | Repository design/schema review; `findmnt -T /run`; cross-reference and lifecycle search; `git diff --check` exposed corruption in the previous handover. No implementation tests because the submission is design-only | **Changes requested. Remediation R4 and independent re-review required; Package 5.0 remains not ready and implementation unauthorized** |
| v1.0 | 2026-08-02 | Peter Duscha | Adds document control, accountable roles, gate governance, success measures, dependency map, RAID/decision/status controls and decomposes oversized roadmap work | Technical product scope preserved; schedule ranges become non-commitment planning inputs; exposes existing Phase 2 and Phase 5 risks | Reviewed for internal consistency and local-link validity by Codex | **Accepted by Peter Duscha on 2026-08-02** |
| v1.1 | 2026-08-02 | Peter Duscha | Rejects ADR 0008; removes Phase 2 migration of Sheet-era state; assigns each field group’s one-time migration to its typed domain package | Removes interim state/bootstrap/correction scope from Phase 2; adds package-level reconciliation, recovery and cutover evidence later; reduces double-migration and weak-constraint risk; Phase 2 implementation/remediation must be re-estimated | Plan and acceptance-criteria review by Codex; technical implementation re-review still required after remediation | **Accepted by Peter Duscha on 2026-08-02 in this review conversation** |
| v1.2 | 2026-08-02 | Peter Duscha | Closes the v1.1 management-review findings: deferred legacy comparisons, read-only Phase 3, exhaustive migration allocation, universal mutation-test matrix, boundary-specific gate evidence, superseded Phase 2 plan and executable next actions | Removes contradictory Phase 2/3 scope; adds one accountable package for every known legacy field; increases planning/evidence work before later mutation packages but reduces omission, double-authority and unverifiable-gate risk | Best-practice project-management review and consistency amendments by Codex; implementation and replacement package-plan review remain pending | **Accepted by Peter Duscha through the instruction to amend the plan on 2026-08-02** |
| v1.3 | 2026-08-02 | Peter Duscha | Requires every multi-valued Google Sheet source to migrate into normalized relational reference/child/junction tables with foreign keys | Prohibits delimited, JSON/JSONB, PostgreSQL-array and generic key/value list storage; adds schema-design, migration-control-total and PostgreSQL constraint evidence to each owning package | Architecture/project-control amendment by Codex; package schemas remain subject to independent review | **Accepted by Peter Duscha through the explicit relational-table direction on 2026-08-02** |
| v1.4 | 2026-08-02 | Peter Duscha | Clarifies that relational normalization applies to authoritative multi-valued operational domain facts, using typed owned child rows when no shared definition identity exists | Retains strict migration integrity while exempting bounded immutable evidence, audit context, diagnostics, preserved external payloads and disposable presentation caches from artificial decomposition; exceptions cannot become operational authority | Architecture clarification by Codex; no implementation gate is bypassed | **Accepted by Peter Duscha through explicit confirmation on 2026-08-02** |
| v1.5 | 2026-08-02 | Peter Duscha | Closes the v1.4 management-review findings: preserves scalar aggregates as opening facts, governs vocabularies, makes source allocation machine-readable, adds schema readiness and correction gates, fixes dependencies and separates Phase 5 cutover from Sheet retirement | Prevents invented history and vocabulary identities; adds manifest/register/schema review work before packages; strengthens traceability, referential integrity and retirement controls without adding committed dates | Best-practice project-management amendment by Codex; replacement Phase 2 and future package plans remain subject to readiness/review | **Accepted by Peter Duscha through the instruction to amend the plan on 2026-08-02** |
| v1.6 | 2026-08-27 | Peter Duscha | Supersedes OD-14's exact Foundry deployment tuple with scoped compatibility ranges: exact world/system identities, Foundry generation `14.x`, dnd5e major/minor `5.3.x`, and fail-closed parsing of malformed or unsupported versions | Removes the mandatory stop for an in-range build/patch update while retaining refusal across Foundry generations, dnd5e minor/major changes, identity changes and malformed versions. Does not authorize Phase 4 or bypass Phase 3 implementation/security re-review. Future in-range upgrades still require the deployment checks and evidence stated in the amended ADR and operations contract | Codex EX-11 identified the conflict between C-P3.5-Z and canonical OD-14; implementation and security recommendations remain withheld pending remediation, deployment evidence and re-review | **Explicitly authorized by Peter Duscha on 2026-08-27: “Yes, it was my recommendation in the first place. I authorise the change.”** |
| v1.7 | 2026-08-28 | Peter Duscha | Records that the Freedom bot is retired and deleted at the end of the migration, once the platform provides every player-facing behavior it provides | Amends `.agents/AGENTS.md` product direction and its non-deletion rule; retitles plan §15 to *Legacy runtime retirement*, adds §15.2 and a terminal dependency-map row. Moves the release boundary by adding a terminal retirement gate after §15.1. No phase order, package scope, authority, privacy or data-ownership change; Phase 4 is unaffected | Product Owner decision recorded as OD-53; Technical Lead impact assessment in this entry; Independent Reviewer not involved, none required for a direction record | **Authorized by Peter Duscha on 2026-08-28**: *"in the end, yes, the bot will be deleted because it's not needed anymore."* |
| C-P4-E | 2026-08-28 | Peter Duscha | `/info` is not rewired in Phase 4 or reproduced as a platform command; linked-character pages replace its underlying user need | Initially replaced real-command wiring with a temporary Sheet adapter/query; that adapter-only portion is superseded by C-P4-F. No schema, authority, phase-order or release-boundary change | OD-52 and Phase 4 impact assessment updated; independent implementation review remains required | **Authorized 2026-08-28; partly superseded by C-P4-F** |
| C-P4-F | 2026-08-29 | Peter Duscha | Removes the adapter-only Phase 4 compromise; package 5.2 introduces the wallet query and production adapter with the character page as their real consumer | Removes WP-5 and the temporary Sheet query/adapter. Phase 4 boundaries are exercised through ledger/idempotent command execution. Estimate becomes 5.0/9.0/16.5, PERT 9.6. No schema, authority, phase-order or release-boundary change | Best-practice recommendation by Codex accepted by Peter; independent Phase 4 implementation review remains required | **Authorized by Peter Duscha on 2026-08-29** |
| C-P4-G | 2026-08-29 | Working Technical Lead (Claude) | Records the Phase 4 WP-2, WP-3 and WP-4 implementation: the command envelope and typed results, the balanced append-only ledger, its concrete command-execution service, and durable idempotent execution on the existing `idempotency_keys` table | **No baseline change, and none is required.** No scope, authority, privacy, architecture, data-ownership, release-criterion, phase-order or target-range change; no migration, no table, no configuration, no deployment. Recorded here so the gate has a dated pointer to the delivery, and because one design correction is worth a reviewer's attention: the optimistic-concurrency precondition is decided **at commit** rather than at read, after the first draft's read-time comparison let two concurrent callers against one version both commit. Adds RAID rows R-P4-1…R-P4-4, A-P4-1 and A-P4-2, and R-P4-4 records that a posted ledger transaction is durable only as far as process memory while OD-48 defers the table | Evidence in `docs/review/phase-4-submission.md`, including 16 falsification mutations with no survivors. **Independent implementation review by Codex is required and has not happened** | **Not decided. Recorded for the Independent Reviewer and the Acceptance Authority; no gate is claimed** |
| C-P4-H | 2026-08-29 | Independent Reviewer (Codex) | Records the first independent Phase 4 implementation review: two Blocking findings (unsafe concurrent retraction; unverified service-principal authority) and one Important finding (incomplete idempotency identity) | **No baseline change.** Phase 4 remains within its approved scope, but its gate is deferred and the remediation allowance is activated. D-04 stays Open and Phase 5 mutations remain blocked. No schema, migration, deployment, data-authority or production-behavior change is authorized. The handover is replaced with a remediation-only brief requiring concurrency, authorization and digest corrections plus regression evidence | Focused independent run: 326 Phase 4 tests passed in 2.81 s and `git diff --check` was clean; those results do not cover the counterexamples. Re-review is required after remediation | **Changes requested by Codex. No gate decision requested until both Blocking findings and the Important finding are remediated and re-reviewed** |
| C-P4-I | 2026-08-29 | Working Technical Lead (Claude) | Records Phase 4 remediation R1: the three Codex findings P4-R1, P4-R2 and P4-R3 are remediated and resubmitted for independent re-review | **No baseline change, and none is required.** No scope, authority, privacy, phase-order, release-criterion or target-range change; no migration, no table, no route, no command, no deployment unit, no environment variable, no credential and no configuration change. OD-48 is untouched. Three contracts change and are called out: `LedgerCommandService` now requires a `LedgerPrincipalPort`; `LedgerBook.publish`/`retract` are replaced by `LedgerBook.committing`, which holds the book across the durable commit and appends only after it returns; and the idempotency digest binds occurrence time, verified caller identity and caller surface under a versioned, length-delimited encoding, making digests non-comparable across the change — which costs nothing, because no digest has ever been stored outside the disposable test database. The Foundry credential vocabulary `ServicePrincipalScope` is deliberately **not** widened; the ledger scope is consumer-owned, and whether it should eventually be shared is left open for the maintainer | Evidence in `docs/review/phase-4-submission.md`, *Remediation R1*: the handover's six falsification mutations, all detected, all restored byte-exactly with `sha256sum -c`. Complete serial verification re-run against the submitted tree. **Independent re-review by Codex is required and has not happened** | **Not decided. No finding is closed, D-04 remains Open, the Phase 4 gate remains deferred and no Phase 5 work is released. Recorded for the Independent Reviewer and the Acceptance Authority** |
| C-P4-J | 2026-08-29 | Independent Reviewer (Codex) | Re-review of Remediation R1: P4-R1 and P4-R2 are materially remediated and P4-R3's requested digest correction is present; raises P4-R4 Blocking for correction lookup before authorization and P4-R5 Important for inconsistent envelope/transaction correlation IDs | **No baseline change.** Both are implementation defects inside approved Phase 4 scope and require no maintainer policy, architecture, authority, privacy, schema, migration, deployment or release-boundary decision. Gate deferred; D-04 Open; Phase 5 blocked. Handover replaced with a Remediation-R2-only brief | Focused 376 passed; web 2824/80; Foundry 171; compileall and diff check clean. Bot 2887/2/1 because backup/restore found missing disposable-test-database grants; restore and rerun required | **Changes requested. Claude may remediate directly; Codex re-review required before a gate decision** |
| C-P4-K | 2026-08-29 | Working Technical Lead (Claude) | Records Phase 4 remediation R2: the two Codex re-review findings P4-R4 and P4-R5 are remediated and resubmitted for independent re-review | **No baseline change, and none is required.** No scope, authority, privacy, phase-order, release-criterion or target-range change; no migration, no table, no route, no command, no deployment unit, no environment variable, no credential and no configuration change. OD-48 is untouched and `ServicePrincipalScope` is again deliberately not widened. Two contracts change and are called out: `LedgerCommandService.compensate()` now resolves current authority **before** it reads the ledger and carries that one resolved attribution through a private execution path, so an unauthorized caller receives `not_authorized` where it could previously receive `concurrent_posting` and can no longer use the pair of refusals as an existence oracle; and `REFUSAL_CODES` gains `correlation_mismatch`, because an envelope and the transaction it carries must now name one correlation identity or the command is refused before a unit of work opens. `post()`'s behaviour is unchanged by design. One production file changed, `application/ledger.py`, already declared in the P3.4 scope guard; no tracked production module changed | Evidence in `docs/review/phase-4-submission.md`, *Remediation R2*: four falsification mutations plus one weaker variant, all detected, `application/ledger.py` restored byte-exactly and verified with `sha256sum -c`. Complete serial verification re-run against the submitted tree: narrow 415, bot **2929 passed, 0 skipped**, web 2824/80, Foundry 171, `compileall` and `git diff --check` clean. The re-review's 2887/2/1 backup-restore drill failure **could not be reproduced** — the drill passes here, no grant was altered, and this is reported rather than claimed fixed. **Independent re-review by Codex is required and has not happened** | **Not decided. No finding is closed, D-04 remains Open, the Phase 4 gate remains deferred and no Phase 5 work is released. Recorded for the Independent Reviewer and the Acceptance Authority** |
| C-P4-L | 2026-08-29 | Independent Reviewer (Codex) / Peter Duscha, Acceptance Authority | Records the second independent re-review and Peter's approval of the Phase 4 dependency-direction and domain-correctness gate | **No controlled-baseline amendment.** P4-R4 and P4-R5 are Closed; the earlier P4-R1, P4-R2 and P4-R3 remediations remain closed review history; D-04 is Closed. Phase 5 package planning is released subject to every package's own definition of ready, predecessor decisions, independent review and cutover gate. No migration, data-authority change, deployment, Sheet retirement or permanent Discord character-mutation surface is authorized | Independent verification against the accepted tree: focused Phase 4 **415 passed**; bot **2929 passed, 0 skipped**; web **2824 passed, 80 expected skips**; Foundry **171 passed**; `compileall` under both interpreters and `git diff --check` clean. No formatter, linter or type checker is configured | **Approved by Peter Duscha on 2026-08-29. Phase 4 gate closed** |
| C-P4-M | 2026-08-29 | Peter Duscha / Delivery Lead documentation update | Selects package 5.0 as the next Phase 5 readiness-planning package and replaces the completed Phase 4 remediation handover with a Phase 5.0 readiness/design brief | **No baseline or production-scope change.** Package 5.0 is the existing common predecessor in plan §12.0. Planning is authorized; implementation, migrations, production mutations, data-authority cutover, deployment and Sheet retirement remain unauthorized until readiness and required independent schema review close | Documentation consistency and `git diff --check`; no production code or environment changed | **Recorded. Readiness package requested; no implementation gate decided** |
| C-P5.0-A | 2026-08-29 | Working Technical Lead (Claude), on Peter Duscha's Phase 5.0 readiness handover | Records the package 5.0 readiness and design submission: the package plan, the mandatory logical schema artifact, eight raised decisions and the finding that the package is **`not ready`** | **No baseline change, and none is required.** No scope, authority, privacy, architecture, data-ownership, release-criterion, phase-order or target-range change; no production file, migration, table, route, command, deployment unit, environment variable, credential or configuration change. Package 5.0's scope is the existing common-predecessor scope plan §12.0 already gives it. Three proposals are recorded here because they would each be a material change if accepted, and none is decided: **(1)** package 5.0 persists its own control plane — a manifest-seeded migration-unit vocabulary, an append-only authority chain, a legal-transition reference table and value-free comparison telemetry — so that its own authority revision is the durable domain effect the transaction-boundary deliverable needs (D5.0-1); **(2)** the durable ledger table is recommended to stay with package **5.2**, closing OD-48's *"package 5.0 or 5.2"* ambiguity, because a 5.0 ledger table would persist a free-text account name with no foreign key to `characters` (D5.0-5); and **(3)** the handover's requirement for comparison telemetry contradicts its own ban on abstractions without a package-5.0 consumer, since 5.0 has no shadowed field — raised as D5.0-2 rather than resolved by the implementer. **R-P4-4 is narrowed, not closed**: 5.0 would make it impossible to deploy a process treating the in-memory ledger as production authority, and claims nothing further. Estimate O 7.0 / ML 14.0 / P 25.0 implementer-days, PERT **14.3**, plus 4.2 days remediation allowance and 2.0 contingency, with review, security review, rehearsal and maintainer decision time outside those figures; Phase 5's roadmap range was withdrawn deliberately, so no range comparison is offered | Evidence: `../review/phase-5-0-package-plan.md` and `../review/phase-5-0-logical-schema.md`. **No test was run for this package, because no code exists for it**; the environment facts in package plan §8.1 are dated observations of this host and each says how it was observed. **The mandatory independent logical-schema review has not happened**, and under plan §7.3.1 and the handover it must close before any migration or production code. A distinct security-focused review is required and its reviewer is unnamed | **Not decided. Package 5.0 is `not ready`.** Two governance-README readiness criteria are unmet: eight decisions are Open (four of them readiness-blocking), and the Independent Reviewer, schema reviewer and Security Reviewer are unnamed. Recorded for the Independent Reviewer and the Acceptance Authority; no gate is claimed and nothing is closed |
| C-P5.0-B | 2026-08-29 | Peter Duscha, on Codex's independent recommendation | Rules D5.0-1 through D5.0-7 and partially resolves D5.0-8; accepts Codex findings P5.0-R1 through R3 and requests design remediation | Package 5.0 persists its authority control plane; telemetry implementation moves to 5.1; internal character UUID telemetry is permitted under restricted value-free controls; numeric thresholds are accepted with advance approval required below 30 comparisons; the ledger belongs to 5.2; authority changes use a host-local Platform-Administrator command; no service-principal scope is added in 5.0. Claude is designated implementer/working Technical Lead and Codex Independent Reviewer/schema reviewer. Security Reviewer remains unnamed. No implementation, migration, deployment, mutation or cutover is authorized | Independent review found that startup checks do not prevent overlapping old/new writers and that cutover/effective-time semantics are incoherent. Claude must revise both design artifacts and obtain Codex re-review; a separate security-focused review remains required | **Changes requested. Package 5.0 remains not ready; implementation unauthorized** |
| C-P5.0-C | 2026-08-29 | Working Technical Lead (Claude), on Peter Duscha's Package 5.0 design remediation handoff | Records design remediation **R1**: the revised package plan and logical schema answering Codex Blocking findings P5.0-R1 and P5.0-R2 and applying OD-55, submitted for independent schema re-review | **No baseline change, and none is required.** No scope, authority, privacy, architecture, data-ownership, release-criterion, phase-order or target-range change; no production file, migration, table, route, command, deployment unit, environment variable, credential or configuration change. Package 5.0's scope is the common-predecessor scope plan §12.0 already gives it. **Design changes within that scope:** authority is removed from process configuration and leased from the database, with request-time admission, a two-phase quiesce carrying a positive drain acknowledgement, and a database trigger that refuses activation without either every live lease's acknowledgement or a passed lease horizon — chosen after comparing five feasible fencing designs and their failure modes (plan §2.10), as the handoff required rather than selected silently; an authority change is split into **authorize** and **activate**, and authority is read only from an activated disposition, so a pending or future-dated revision is authority for nothing; the complete authority-state read/write matrix is schema §2.1 and resolves the revision-1 contradiction by ruling that **authority transfers at `shadow → cutover`** while `cutover → database` closes the verification window; no state dual-writes in any direction; the runtime role loses even `INSERT` on the authority tables, so no application process can change authority at all. **Withdrawn:** revision 1's claim that a database chain head makes two operational write authorities impossible, replaced by schema §2.4 stating what the database guarantees and what process-level control completes it. **Removed under OD-55:** `shadow_comparisons` and its write path, from the schema, ER diagram, grants, decision table, work breakdown, estimate and every Package 5.0 test claim; the common telemetry contract is retained as prose in plan §11 with Package 5.1 recorded as implementation and schema owner. Four tables become six. Estimate becomes O 10.0 / ML 20.0 / P 35.0, PERT **20.8** (was 14.3), with 6.0 days remediation allowance and 2.5 contingency; the movement decomposes as −1.1 for the removed telemetry work package and +7.6 for request-time fencing. **Two decisions are raised, not taken:** D5.0-9 / OD-62, whether Freedom-bot *mutations* may take a bounded (~25 s) availability dependency on PostgreSQL as the price of fencing, with three priced options and WP-4 blocked until it is ruled; and D5.0-10 / OD-63, the seven fencing numeric controls N5.0-9 … N5.0-15. New risks R-5.0-5 and R-5.0-6; R-5.0-2 superseded; R-5.0-4 re-owned by Package 5.1; new dependency D-5.0-2. N5.0-4's wording is corrected to name the `cutover` state, changing no accepted number | Evidence: `../review/phase-5-0-package-plan.md` and `../review/phase-5-0-logical-schema.md`, both revision 2. **No test was run for this remediation, because no code exists for this package**; the environment facts in plan §8.1 are dated observations of this host and each says how it was observed. **The independent logical-schema re-review has not happened**, and under plan §7.3.1 and the handoff it must close with P5.0-R1 and P5.0-R2 recorded closed before any migration or production code. A distinct security-focused review is still required and its reviewer is still unnamed | **Not decided. Package 5.0 remains `not ready` and implementation remains unauthorized.** Claude claims **no finding closed** — the Independent Reviewer decides. Three governance-README readiness criteria are unmet: the schema re-review is open, D5.0-9 and D5.0-10 are open and each blocks a work package, and the Security Reviewer is unnamed. Recorded for the Independent Reviewer and the Acceptance Authority; no gate is claimed and nothing is closed |
| C-P5.0-D | 2026-08-29 | Independent Reviewer (Codex) | Re-review of Package 5.0 remediation R1 | Closes P5.0-R2. Keeps P5.0-R1 Blocking because a paused process may resume after the lease horizon and write Sheets. Raises P5.0-R4 Blocking because the shared runtime role can mutate other instances' leases or forge acknowledgements, defeating the activation proof. No baseline, production code, migration, configuration, credential, deployment or authority change | Design/schema review and `git diff --check`; no tests because Package 5.0 has no implementation | **Changes requested. Remediation R2 and re-review required; implementation remains unauthorized** |
| C-P5.0-E | 2026-08-29 | Working Technical Lead (Claude), on Peter Duscha's Package 5.0 design remediation R2 handoff | Records design remediation **R2**: revision 3 of the package plan and logical schema answering Codex Blocking findings P5.0-R1 and P5.0-R4, with P5.0-R2 and OD-55 preserved, plus a handback document; submitted for independent re-review | **No baseline change, and none is required.** No scope, authority, privacy, architecture, data-ownership, release-criterion, phase-order or target-range change; no production file, migration, table, database role, credential, Google access, deployment unit, environment variable or configuration change. Package 5.0's scope is the common-predecessor scope plan §12.0 already gives it. **Design changes within that scope:** the fence a store gets becomes the fence that store can enforce. Every PostgreSQL-authoritative write is refused by a trigger evaluated **inside the writing transaction**, so a process paused for any duration and resumed after activation commits nothing — the check is not in the past. The Google Sheet, which has no conditional-write mechanism in its published API, is fenced instead by **termination of a separately terminable writer process** — a `SIGKILL` escalation kills a `SIGSTOP`ped process and a killed process cannot resume — with **Google-side write-access revocation** as an independent second control whose residual is disjoint from the first's. Four options were compared against nine failure cases (plan §2.10) as the handoff required. For P5.0-R4, both runtime-written tables are **withdrawn rather than secured**: no application process authors any authority proof for any instance including its own, because a compromised process's claim about itself is worthless at any privilege level; quiescence evidence is *observed* by a supervisor and recorded by a distinct peer-authenticated coordinator principal, and the shared runtime role ends with **no write privilege anywhere on the authority plane**. Per-role RLS was compared and rejected as the primary control (plan §2.11). **Withdrawn:** the lease, the renewal interval, the clock-skew allowance, the admitted-operation budget, the headroom rule, the drain acknowledgement, the `fence_protocol_version` handshake, the monotonic-clock model, numeric controls N5.0-9 … N5.0-13 and N5.0-15, the derived 25-second grace period and the standing PostgreSQL availability dependency for Freedom-bot mutations. **Preserved:** P5.0-R2's accepted state matrix and effective-time model, restated in full so nothing can have drifted; OD-55's telemetry placement; OD-58's ledger ownership. Six tables become **five**. Estimate becomes O 12.5 / ML 22.5 / P 39.5, PERT **23.7** (was 20.8), with 6.8 days remediation allowance and 3.0 contingency; the movement decomposes as −2.0 for the withdrawn lease apparatus, +2.5 for the separately terminable writer, +1.4 for the coordinator principal and observed evidence, and +1.0 for the Google-access feasibility measurement. **One decision reframed, one reduced, one new, none taken:** D5.0-9 / OD-62 is reframed around which enforceable boundary and which of its outage, topology and production-access costs is accepted, its revision-2 options withdrawn as priced on a design that does not close the finding; D5.0-10 / OD-63 is reduced from seven numeric controls to four, with N5.0-18 a placeholder pending measurement; and **D5.0-11 / OD-64** asks whether a distinct peer-authenticated `freedom_migration_coordinator` principal is introduced. New work package WP-13 measures Drive permission propagation against a **disposable** spreadsheet and service account. Risks R-5.0-5 and R-5.0-6 restated, R-5.0-7 and assumption A-5.0-3 new, dependency D-5.0-2 extended to three rulings, and the security review grows to 1.0–1.5 reviewer-days | Evidence: `../review/phase-5-0-package-plan.md` and `../review/phase-5-0-logical-schema.md`, both revision 3, and `../review/phase-5-0-remediation-r2-handback.md`. **No test was run for this remediation, because no code exists for this package**; the environment facts in plan §8.1 are dated observations of this host and each says how it was observed, and the Sheet-write-surface facts in §2.9 are the result of a repository-wide search on 2026-08-29. **The independent logical-schema re-review has not happened**, and under plan §7.3.1 and the handoff it must close with P5.0-R1, P5.0-R2 and P5.0-R4 recorded closed before any migration or production code. A distinct security-focused review is still required and its reviewer is still unnamed | **Not decided. Package 5.0 remains `not ready` and implementation remains unauthorized.** Claude claims **no finding closed** — the Independent Reviewer decides. Four governance-README readiness criteria are unmet or partly met: the schema re-review is open; D5.0-9, D5.0-10 and D5.0-11 are open and each blocks a work package; the Security Reviewer is unnamed; and assumption A-5.0-3 is unconfirmed. Recorded for the Independent Reviewer and the Acceptance Authority; no gate is claimed and nothing is closed |
| C-P5.0-F | 2026-08-29 | Independent Reviewer (Codex) | Re-review of Package 5.0 design remediation R2 | **No baseline or implementation change.** P5.0-R1 remains Blocking: the PostgreSQL transaction trigger is sufficient for database writes, but measured Drive-permission propagation and a fixed settle interval do not prove that a request accepted before revocation has completed before the final Sheet read. P5.0-R4 remains Blocking: removing runtime-authored proof is sound, but the peer-authenticated coordinator is not bound to a named dedicated OS identity, exact peer mapping and host privilege boundary that prove no service process can authenticate as it. P5.0-R2 remains closed and OD-55 remains preserved | Independent design/schema review against the repository and official Google Drive/Sheets API documentation; `git diff --check` clean; no tests because Package 5.0 has no implementation | **Changes requested. Remediation R3 and independent re-review required; Package 5.0 remains not ready and implementation remains unauthorized** |
| C-P5.0-G | 2026-08-29 | Working Technical Lead (Claude), on Peter Duscha's Package 5.0 design remediation R3 handoff | Records design remediation **R3**: revision 4 of the package plan and the logical schema answering Codex Blocking findings P5.0-R1 and P5.0-R4, with P5.0-R2, OD-55 and OD-58 preserved, plus a new handback document; submitted for independent re-review | **No baseline change, and none is required.** No scope, authority, privacy, architecture, data-ownership, release-criterion, phase-order or target-range change; no production file, migration, table, database role, operating-system account or group, `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, credential, Google access, deployment unit, environment variable or configuration change. **The host was read and never written.** Package 5.0's scope is the common-predecessor scope plan §12.0 already gives it. **Design changes within that scope, and the two findings are answered differently.** For **P5.0-R1** the remediation takes the second route the handoff permits: thirteen candidate barriers were traced against the published Sheets v4 and Drive v3 surface — the `batchUpdate` response, an operation identifier, an idempotency token, a conditional write, `files.version`, `revisions.list`, the Drive Activity API, push notifications, a marker write, protected ranges, a file copy, Apps Script `flush()` and waiting — and each reduces to a quiet period, rests on an unpublished implementation property, is documented as unreliable, or does not exist. **The conclusion is that the published Google APIs cannot supply a barrier proving that a request accepted before the fence is reflected before the final import reads**, and revision 3's enforceability claim is **withdrawn**, as is its assertion that such a call *"is captured by the final import"*. What replaces it is stated as a weaker guarantee rather than a fence: the writer is **drained before it is killed** (ordering changed — drain, then terminate, then revoke); an explicit per-request timeout is added because none is set today, so the in-flight window is currently unbounded; a `fsync`-ed, append-only, **host-local** dispatch journal makes the unresolved set enumerable; `dispatch_journal_clear` becomes a fifth required fence method and a non-empty set **refuses the activation**; a late apply cannot reach PostgreSQL; and two post-import divergence re-reads detect it. The journal is deliberately a host file and not a table, so the legacy mutation path still takes **no** database dependency. For **P5.0-R4** the remediation supplies the missing boundary in full: a dedicated **`freedomcoord`** operating-system user and group distinct from `discordbot`, `freedomweb`, the proposed `freedomsheet` and `foundry` and in no group any of them holds; exact `pg_hba.conf` ordering with the `peer`/`map` line above three written-out TCP rejects; one `pg_ident.conf` line with no wildcard; the role created `PASSWORD NULL`; a `sudoers` drop-in naming `foundry` only, without `NOPASSWD`, invoking one fixed root-owned wrapper that clears the environment and runs `python -I -P`; ownership and modes for every artifact; a per-vector argument; provisioning, audit, revocation, recovery and rotation; and a ten-case host-boundary evidence band. **Three host observations are recorded rather than assumed away**, and one of them changed the design: `/opt/freedom-blades/platform` is group-writable by `discordbot` and `freedomweb` is a member of that group, so all three service processes can today rewrite every module including `tools/` and `migrations/` — hence a **root-owned deployment path outside the repository** with digest verification at deploy. **No table is added**; five tables, as in revision 3. Estimate becomes O 14.5 / ML 28.0 / P 48.5, PERT **29.2** (was 23.7), with 8.4 days remediation allowance and 3.5 contingency; the movement decomposes as +1.0 for the drain, timeout and journal, +0.5 for the journal check and divergence re-read, +1.0 for the host-boundary denial matrix, +0.4 for the rehearsal additions, +0.4 for the contract numbers and +2.2 for the new WP-14. **One decision reframed a third time, one extended, one extended, one new, none taken:** D5.0-9 / OD-62 is no longer *which fence* but **what is accepted in place of one**, and is now a **risk acceptance** owned by the Acceptance Authority; D5.0-10 / OD-63 grows from four numeric controls to six, with N5.0-17 and N5.0-18 reframed because they were described as bounds they cannot be and N5.0-19 and N5.0-20 new; D5.0-11 / OD-64 is extended to cover the operating-system identity and host boundary as well as the database role, because approving the role alone would approve a control that does not exist; and **D5.0-12 / OD-65** asks for the `freedomsheet` identity and Google-credential relocation, hardening on the live `freedom-bot` unit (Phase 0 finding F-3) and a ruling on the group-writable repository tree. New work package **WP-14** for the host boundary; **WP-13 demoted** to informing an operational margin. New risks **R-5.0-8** (the accepted, unprovable Sheet residual, owned by the **Acceptance Authority** rather than the Technical Lead) and **R-5.0-9** (host-boundary drift); new assumption **A-5.0-4** (a disposable OS identity and `pg_hba` reload, without which the entire R3-B evidence plan is unproducible); dependency D-5.0-2 extended to four rulings; and the security review grows to 1.5–2.5 reviewer-days | Evidence: `../review/phase-5-0-package-plan.md` and `../review/phase-5-0-logical-schema.md`, both revision 4, and `../review/phase-5-0-remediation-r3-handback.md`. **No test was run for this remediation, because no code exists for this package**, and **no executable control is claimed to have passed**; formatter, linter and type checker are **not configured** in this repository and that is recorded as *not configured*, never as *passed*. `git diff --check` is clean. The host facts in plan §8.1 are dated observations made with `ls`, `getent`, `id`, `df`, `find` and `systemctl show`. **Four checks could not be run and are named rather than omitted**: `/etc/sudoers.d/` could not be enumerated without privilege; no host-wide setuid audit was performed; and neither PostgreSQL `log_connections` nor the live `pg_hba.conf`/`pg_ident.conf` could be read. **No Google API was called**, including for the barrier search, which is a reading of published documentation and not a probe. **The independent logical-schema re-review has not happened**, and under plan §7.3.1 and the handoff it must close with P5.0-R1, P5.0-R2 and P5.0-R4 recorded closed before any migration or production code. A distinct security-focused review is still required and its reviewer is still unnamed | **Not decided. Package 5.0 remains `not ready` and implementation remains unauthorized.** Claude claims **no finding closed** — the Independent Reviewer decides, and for P5.0-R1's Sheet half the remediation explicitly offers a conclusion and a decision rather than a fence. Five governance-README readiness criteria are unmet or partly met: the schema re-review is open; D5.0-9, D5.0-10, D5.0-11 and D5.0-12 are open and each blocks a work package; the Security Reviewer is unnamed; and assumptions A-5.0-3 and A-5.0-4 are unconfirmed. Recorded for the Independent Reviewer and the Acceptance Authority; no gate is claimed and nothing is closed |
| v1.5 clarification C-1 | 2026-08-02 | Peter Duscha | Splits RAID dependency D-01 into D-01a/D-01b, registers the I-05 identity ruling as proposed decision OD-42, corrects A-02/A-03 and the Phase 2 critical path for the now-existing restricted role and available example exports, and tightens the Independent Reviewer wording at mandatory checkpoints | No roadmap, phase order, release boundary, scope, authority, privacy, architecture, data-ownership or release criterion changes. Dependency granularity, evidence status and reviewer wording only; the reviewer change strengthens an existing control and weakens none | Prepared with the replacement Phase 2 remediation plan; independent review of that plan pending | **Accepted by Peter Duscha on 2026-08-02** |
| v1.5 clarification C-2 | 2026-08-02 | Peter Duscha | Records four rulings taken with the acceptance of the replacement Phase 2 remediation plan: OD-42 (display-name identity policy, closing I-05); the disposition of `tools/import_sheet_characters.py`; the security-review assignment; and the timing of the §9.4 operational windows | No roadmap, phase order or release-boundary change. OD-42 confirms and completes an existing identity policy without adding a schema constraint; the CLI ruling reverts an uncommitted modification and allocates the tool's disposition to package 5.1, which the migration register already owns; the review and window rulings are delivery controls. Releases packages R1–R3 to start; R4 remains blocked on the §9.4 values | Recommendations from the working Technical Lead (Claude); independent review of the remediated implementation still required | **Accepted by Peter Duscha on 2026-08-02** |
| v1.5 clarification C-3 | 2026-08-04 | Peter Duscha | Records the Phase 2 I-03 snapshot submission package: a Foundry v14 module, a scoped-service-principal HTTPS submission endpoint, restricted artifact storage and a Council preview contract | No roadmap, phase order or release-boundary change. Brings forward the **read-only submission half** of the Phase 7 module and its scoped credential, and introduces one non-browser HTTP route ahead of Phase 3 without creating any portal, session, OAuth or CSRF surface. Adds one additive, reversible migration (`0004`) and one proposed ADR (`0009`). Submission applies nothing; apply authority, field ownership and the Phase 2 gate evidence are unchanged | Package plan and impact assessment by the working Technical Lead (Claude), `docs/review/phase-2-i-03-package-plan.md`; **independent implementation review and separate security-focused review still required** | **Not yet decided.** Recorded for the Acceptance Authority |
| v1.5 clarification C-4 | 2026-08-04 | Peter Duscha | Accepts ADR 0009: the snapshot submission endpoint is a stdlib WSGI application, and FastAPI is not introduced by the Phase 2 I-03 package | No roadmap, phase order or release-boundary change. ADR 0002 is unchanged — FastAPI remains the recorded choice for the Phase 3 web application, and the WSGI application mounts inside it unchanged. Adds no dependency. Accepts the architectural decision **only**: the I-03 implementation still requires independent implementation review and a separate security-focused review, and no further HTTP surface is authorized | Proposed by the working Technical Lead (Claude) in `docs/adr/0009-snapshot-submission-http-boundary.md`, with alternatives recorded | **Accepted by Peter Duscha on 2026-08-04** |
| v1.5 clarification C-8 | 2026-08-05 | Peter Duscha | Accepts retention decision D-c for database-unclaimed raw Foundry snapshot artifacts | No scope, authority, architecture, phase-order or release-boundary change. Raw artifacts are retained at most 30 days and deleted sooner after their rehearsal, retry or incident closes; checksum, provenance and sanitized audit remain permanent | Operations procedure and I-03 package-plan amendment; independent implementation review remains required for the complete Phase 2 gate | **Accepted by Peter Duscha on 2026-08-05** |
| v1.5 clarification C-9 | 2026-08-05 | Peter Duscha | Sets Phase 2 R4 observation and synthetic 500-Actor runtime thresholds | No scope, authority, architecture, phase-order or release-boundary change. Rehearsal observation is immediate verification followed by shutdown/cleanup; acceptance thresholds are 5 seconds preview and 5 seconds fresh apply on the named host | Synthetic PostgreSQL benchmark and Codex independent reproduction; real-export rehearsal remains pending | **Accepted by Peter Duscha on 2026-08-05** |

## v1.5 clarification C-2 — rulings recorded with the plan acceptance

- **Replacement plan (D-1):** `docs/review/phase-2-v1.5-remediation-plan.md` is
  **accepted** as the executable Phase 2 remediation plan. The superseded
  `phase-2-package-plan.md` remains non-executable.
- **OD-42 / I-05 (D-2):** ruled as recommended. Display names are not unique
  identities; multiple characters may share one; stable character IDs and
  external Actor IDs provide identity; any legacy name-based candidate lookup
  fails closed when more than one candidate exists. **No unique display-name
  constraint is added.** I-05 is closed; R-01's residual narrows accordingly.
- **`tools/import_sheet_characters.py` (D-3):** the I-02 modifications are
  reverted to the committed state and the tool is recorded as **dormant**, with
  its disposition owned by package **5.1**. It is not a Phase 2 write path, which
  is what allows threshold T-6 to be asserted cleanly. This removes no accepted
  I-01 work.
- **Security review (D-5):** Codex performs both the independent review and a
  **distinct, separately reported** security-focused pass covering
  authorization, artifact handling, audit content and runtime grants. The
  implementer never reviews their own work.
- **Windows (D-4):** the §9.4 values — rehearsal window, observation period and
  preview/apply runtime budget — are required **before package R4** rather than
  before any work. R1–R3 are released to start; R4 is not ready until they are
  set.

**Classification: clarification, not a new baseline version.** As with C-1, no
§0.2 trigger for a new baseline is met: OD-42 completes an identity policy the
accepted record already established in three of its four clauses and adds no
schema object; the CLI ruling reverts uncommitted work within scope that
baseline v1.1 already removed; and the review and window rulings are delivery
controls. Scope, phase order, release criteria and target ranges are unchanged.

## v1.5 clarification C-1 — baseline classification

**Classification: clarification under §0.2, not a new baseline version.** §0.2
requires a new baseline version only *"when the roadmap or release boundary
changes"*. Assessed against the five §0.2 triggers:

- **scope** — unchanged. No requirement, deliverable, package or acceptance
  criterion is added, removed or reallocated. D-01a/D-01b restate the same
  satisfaction conditions at the granularity they actually apply to.
- **authority** — unchanged in substance. The Independent Reviewer wording
  removes an ambiguity (*"where practical"* read as optional at mandatory
  checkpoints) by stating the control that §16.4 and the gate-authority table
  already impose. It tightens; a tightening of a review control cannot weaken a
  gate invariant, and the deferral outcome it names is an existing gate state.
- **privacy, architecture, data ownership** — untouched. OD-42 is *recorded as
  proposed*; it takes effect only when the Acceptance Authority rules it, and
  recording a proposal is not a decision.
- **release criteria, phase order, target range** — untouched. The corrected
  critical path re-sequences nothing that was previously approved; it replaces a
  five-step summary that omitted plan approval, implementation and
  implementation re-review with the eight steps those documents already require.

A dated entry is therefore required and given; a new baseline version is not.
**If** the Acceptance Authority rules OD-42, that ruling is a data-ownership
decision and receives its own dated entry — still without a new baseline, since
it changes no roadmap or release boundary.

## v1.5 impact assessment

- **Affected requirements:** §§7.3, 12 Phase 5, 13, 15 and 20; migration and
  vocabulary registers; Phase 2 readiness/status.
- **Reason:** scalar counters/dates cannot support reconstructed event history;
  reference tables require governed identity sources; prose-only coverage was
  insufficient evidence of exhaustive allocation.
- **Scope/schedule:** owning packages add opening-baseline models, vocabulary
  decisions, reviewed ER/schema tables, correction workflows and manifest
  checks. Estimates are updated at package readiness; no unbaselined target is
  converted into a calendar commitment.
- **Risk:** eliminates synthetic-history and accidental-vocabulary risks and
  reduces omitted/duplicate source risk. Unresolved Campaign Counter semantics
  remain explicit and block its Phase 8 migration behavior.
- **Testing/operations:** machine-readable manifest checks exact profile/player/
  linkage coverage and package validity; package gates require schema,
  correction, migration and PostgreSQL evidence; Sheet retirement remains
  blocked by every later legacy row.

## v1.4 impact assessment

- **Affected requirements:** §7.3.1, §15 and the migration register.
- **Reason:** preserve the intended relational integrity without inventing
  meaningless global reference entities or decomposing immutable evidence and
  audit/provenance context into operational tables.
- **Scope/schedule:** no authoritative migration scope is removed. Free-form
  owned collections use typed child rows; shared vocabularies use definition
  plus junction tables. Evidence/metadata exceptions require bounded storage,
  access and retention review rather than domain normalization.
- **Risk/control:** prevents both serialized operational state and dogmatic
  over-normalization. An exception cannot drive authoritative calculation,
  satisfy a migration or become editable state; crossing that boundary requires
  normalization and a package gate.

## v1.3 impact assessment

- **Affected requirements:** §§7.3, 13 and 15; every package owning a
  multi-valued legacy field; the controlled migration register.
- **Reason:** use relational identity, referential integrity, uniqueness and
  typed constraints rather than preserving spreadsheet list encodings.
- **Scope/schedule:** package schema and migration work increases for vocabulary
  definitions, child/junction tables and unresolved-value workflows. Estimates
  must include that work before readiness; no existing calendar commitment is
  changed because those packages are not baselined.
- **Risk:** lowers orphan, typo, duplicate, inconsistent-vocabulary and opaque-
  query risks; raises up-front mapping effort and explicit unresolved-data work.
- **Testing/operations:** adds real PostgreSQL foreign-key, uniqueness, delete-
  behavior, control-total and idempotent migration tests. Serialized collection
  storage is a blocking schema-review finding unless separately approved by ADR.

## v1.2 impact assessment

- **Affected requirements:** §§6, 12 Phases 2, 3 and 5, 13, 15 and 20;
  Phase 2 package planning; project status; legacy migration controls.
- **Reason:** baseline v1.1 left impossible legacy comparisons, premature Phase
  3 correction tests, an executable stale package plan and no exhaustive
  field-to-package allocation.
- **Scope:** Phase 3 is explicitly read-only for game state; correction UI moves
  to typed migration packages. Phase 2 reports `legacy_authority_deferred` when
  no accepted database value exists. Every known character/player field has one
  accountable migration package.
- **Schedule/capacity:** Phase 2 remains not ready pending a replacement estimate
  and named capacity. Later package estimates must include their allocated
  migrations and the universal persistent-mutation evidence matrix.
- **Risk:** reduces fabricated comparison, orphan-field, duplicate-authority and
  premature-web-mutation risks; adds register maintenance controlled by Data
  Owner review and change control.
- **Testing/operations:** adds a mandatory matrix for authorization, boundaries,
  concurrency, constraints, injected failures, migration/rerun, recovery,
  runtime-role bypass, monitoring and staging; gate evidence is selected by the
  actual web, Discord, CLI and database surfaces.
- **Approval/evidence:** defines the Phase 2 Data Owner attestation contents and
  durable storage without committing real Actor data.

## v1.1 impact assessment

- **Affected requirements:** §§6.1, 6.2, 6.5, 7.3, 12 Phase 2 and 15.
- **Reason:** avoid creating a weakly constrained generic store that would be
  migrated again before the owning domain rules and schemas exist.
- **Alternative rejected:** ADR 0008's temporary profile-driven state and
  balance tables.
- **Removed scope:** Phase 2 Sheet bootstrap, generic character-state storage,
  and Foundry-to-database corrections for unmigrated fields.
- **Added/deferred scope:** every typed domain package owns one deterministic
  migration, reconciliation, correction workflow, rollback and cutover gate.
- **Schedule/capacity:** Phase 2 must be re-estimated after removal of rejected
  implementation; later package estimates must include migration and Data Owner
  review. No calendar commitment is inferred.
- **Risk:** lowers weak-constraint and double-migration risk; extends the period
  in which the legacy Sheet path remains operational and therefore increases
  dependency/cutover exposure managed by R-06 and package feature flags.
- **Testing/operations:** Phase 2 retains parser, identity, mapping,
  authorization, PostgreSQL concurrency, role-denial, backup/restore and real
  rehearsal evidence. Later packages receive explicit migration, injected
  failure, reconciliation, authorization, audit, restore and rollback criteria.
- **Security/data authority:** no dual writes; legacy authority continues per
  field until an approved typed-package cutover. Existing production writes are
  not frozen prematurely.

## v1.5 clarification C-3 — Phase 2 I-03 snapshot submission package

Recorded 2026-08-04 by the working Technical Lead. **The Acceptance Authority
has not decided it.** The full package plan and impact assessment is
[`../review/phase-2-i-03-package-plan.md`](../review/phase-2-i-03-package-plan.md);
this entry is the change-control summary the required-fields list below asks for.

- **Affected requirements:** §6.3 and §6.4 (the artifact and its provenance),
  §12 Phase 2 (import and reconciliation), §12 Phase 7 (the Foundry module and
  its scoped credential), §12.0 (the Phase 3 gate releases production portal
  integration), §7.1 (`service_principals`) and §9.2–9.3 (web and infrastructure
  security).
- **Reason:** the maintainer requires snapshot submission without SSH, without
  locating a Foundry database and without manually placing a file on the server.
- **Added scope:** `foundry-module/`; the submission application service;
  restricted, content-addressed artifact storage; one WSGI route; a Council
  preview contract; migration `0004`; ADR `0009`.
- **Removed scope:** none. The file-based operator path remains, as a documented
  fallback.
- **Phase-boundary effect:** brings forward the **read-only submission half** of
  Phase 7's module and scoped authentication. Live sync, retries, diagnostics,
  Council shared-field proposals and every write-back remain unstarted, and no
  Phase 7 gate criterion is claimed. Introduces one HTTP route ahead of Phase 3
  that authenticates a bearer service credential rather than a browser session,
  so no cookie, CSRF, OAuth, session or template surface is created. The Council
  preview route is inert without a Phase 3 authentication composition and
  answers `503`.
- **Dependency and critical-path effect:** none claimed. Phase 2's gate still
  requires the supervised active-folder rehearsal and the Data Owner
  attestation, neither of which this package performs.
- **Estimate and capacity:** not re-baselined here; the Delivery Lead owns the
  forecast.
- **New risks:** a persisted artifact class at rest (Actor mechanics), and a
  credential held on Foundry clients. Both are assessed in the package plan §5
  and controlled by restricted storage with documented retention, and by a
  submit-only scope whose worst case is an unwanted **pending** artifact.
- **Testing:** exporter canonicalisation and contract tests under `node --test`;
  storage atomicity, containment and cleanup; HTTP authentication, limits,
  checksum, idempotency and concurrency; preview authorization; PostgreSQL
  constraint, concurrency and append-only evidence; and one cross-language
  contract test binding the exporter's real output to the real parser.
- **Migration:** `0004_snapshot_submission_provenance`, additive and reversible;
  upgrade/downgrade/upgrade rehearsed against the disposable database. No
  applied migration edited; no runtime grant changed.
- **Security and data authority:** unchanged. Submission is not import. Apply
  still requires a currently authorized Guild Council member and still re-checks
  every bound input at commit. No field changes owner and none moves from
  `legacy`.
- **Operational effect:** a new artifact root with its own permissions,
  retention and backup treatment; proxy body and timeout limits that must match
  the 64 MiB artifact ceiling; credential issue, rotation and revocation
  procedures. All in
  [`../operations/foundry-snapshot-submission.md`](../operations/foundry-snapshot-submission.md).
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending.

## v1.5 clarification C-4 — Phase 2 I-03 independent-review remediation

Recorded 2026-08-04 by the working Technical Lead. **The Acceptance Authority
has not decided it, and no finding is closed on the implementer's authority.**
Full record:
[`../review/phase-2-i-03-remediation-submission.md`](../review/phase-2-i-03-remediation-submission.md);
re-review request:
[`../review/phase-2-i-03-remediation-review-request.md`](../review/phase-2-i-03-remediation-review-request.md).

- **Affected requirements:** §9.2 (web security — CORS, credential handling),
  §6.4 (restricted artifact storage), §12 Phase 2 and Phase 7 as amended by C-3.
  No requirement changes ownership, authority or scope.
- **Reason:** the two independent reviews of the I-03 package returned three
  Blocking findings (B-1, S-B-1, S-B-2) and three others (I-1, I-2, S-I-1).
  `../review/phase-2-i-03-codex-review.md` and
  `../review/phase-2-i-03-codex-security-review.md`.
- **Added scope:** `adapters/http/cors.py`; a per-submission credential prompt in
  the Foundry module dialog; enforced artifact-storage preconditions with a
  startup check; a truthful durability contract. One new configuration variable,
  `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS`.
- **Removed scope:** the `submissionCredential` Foundry world setting. Foundry
  14.365 delivers every world-scoped setting value to every connecting client
  (`dist/packages/world.mjs`, an unfiltered `Setting.dump()`), and offers no
  setting option that is a read boundary, so no setting can hold a secret.
- **Alternatives considered and rejected:** a short-lived token exchange (a
  second HTTP route, reserved to Peter under ADR 0009 — carried forward as
  decision D-a); `scope: "client"` browser storage (leaves a reusable bearer at
  rest in a browser profile for no benefit over a password manager).
- **Phase-boundary effect:** none. No new route, no new capability, no new
  caller, no Phase 3 surface. ADR 0009 carries a dated clarification that a CORS
  preflight is the same route's contract rather than a second route.
- **Dependency and critical-path effect:** none added. Phase 2 I-03 remains
  behind independent implementation re-review and a separate security re-review,
  and now also behind two maintainer-supervised checks (operations §8.1, §8.2).
- **Estimate/forecast and capacity effect:** none recorded; this is remediation
  inside an already-planned package.
- **New or changed risks:** **R7 — the browser workflow is still unverified from
  a real browser.** Recorded in the RAID register and in the package plan
  amendment. Risks R1 and R2 of the package plan are strengthened rather than
  changed.
- **Testing effect:** module tests 78 (was 72); the six named narrow suites 220;
  full Python suite 1788, zero skips. No formatter, linter or type checker was
  run, because none is configured in this repository and none is installed.
- **Migration effect:** none. No schema change, no new migration, no edited
  migration; `alembic check` reports no new upgrade operations.
- **Security effect:** removes a reusable bearer from state readable by every
  client of the Foundry world; enforces restricted artifact storage against
  pre-existing paths; adds a bounded, allowlisted browser-origin policy with no
  cookie authority.
- **Operational effect:** one new required configuration variable for the
  browser workflow; **a deployment whose artifact root is permissive,
  wrongly-owned, symlinked or on a filesystem that cannot `fsync` a directory
  will now refuse to start**; credential rotation no longer touches Foundry; a
  documented read-only procedure for identifying database-unclaimed artifacts.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending. Decisions D-a (short-lived token
  exchange), D-b (whether this process may repair storage permissions) and D-c
  (retention for database-unclaimed artifacts) are reserved to Peter.
- **Superseded in part by C-5.** Two of the findings this entry described as
  remediated were reopened by the second independent re-review. Read C-5 with
  it; nothing in this entry closed a finding, and its I-1 and S-B-2 statements
  are no longer the current position.

## v1.5 clarification C-5 — Phase 2 I-03 second remediation (I-1, S-B-2)

Recorded 2026-08-04 by the working Technical Lead, after the second independent
implementation and security re-review of the I-03 remediation. **No finding is
closed, no gate is claimed, and the Acceptance Authority has not decided it.**
Full record: the same
[`../review/phase-2-i-03-remediation-submission.md`](../review/phase-2-i-03-remediation-submission.md)
and
[`../review/phase-2-i-03-remediation-review-request.md`](../review/phase-2-i-03-remediation-review-request.md),
both amended.

- **Affected requirements:** §6.4 (restricted artifact storage), §12 Phase 2
  operational evidence. No requirement changes ownership, authority or scope.
- **Reason:** the re-review found two of the six findings still open. **I-1**:
  the first remediation corrected the named messages and left the equivalent
  claims in the unresolved-concurrency and replay refusal paths and in every
  `ArtifactStorageError`, all of which can run after the artifact store has
  already published bytes. **S-B-2**: the enforced storage checks were made by
  pathname, so the validated root could be replaced between the check and each
  later create, open, publish or directory `fsync`.
- **Added scope:** a declared `StorageOutcome` on every storage failure, so what
  a refusal claims about the store is a decision rather than an inherited
  sentence; a root **directory descriptor** to which every filesystem operation
  is anchored, with an explicit lifecycle owned by the composition root; a
  startup check that no untrusted account can rename entries above the root; a
  repository-wide regression check on the prohibited claim.
- **Removed scope:** none.
- **Alternatives considered and rejected:** another pathname re-check before each
  use (moves the race window rather than removing it); repairing an unsafe root
  (D-b remains Peter's and is unchanged); relying on `__del__` alone for the
  descriptor's lifetime (explicit `close()` plus a context manager instead, with
  finalization as a backstop only).
- **Phase-boundary effect:** none. No new route, no new capability, no new
  caller, no Phase 3 surface, no schema change.
- **Dependency and critical-path effect:** none added. I-03 remains behind an
  independent implementation re-review (I-1, and preservation of I-2), a
  separate security re-review (S-B-2, and preservation of S-B-1/S-I-1) and the
  two maintainer-supervised checks (operations §8.1, §8.2).
- **Estimate/forecast and capacity effect:** none recorded; remediation inside
  an already-planned package.
- **New or changed risks:** R1 and R2 of the package plan are strengthened. The
  residual is now stated precisely: the anchoring is proven against pathname
  substitution and against type, owner and mode as this process observes them,
  **not** by a cross-account experiment, and no automated test creates a second
  POSIX account.
- **Testing effect:** module tests 81 (was 78); the six named narrow suites 232;
  full Python suite 1912, zero skips. Still no formatter, linter or type checker
  configured or installed, and none was added.
- **Migration effect:** none. No schema change, no new migration, no edited
  migration; `alembic check` reports no new upgrade operations.
- **Security effect:** a pathname replacement of the artifact root can no longer
  redirect a create, open, publication, read or directory `fsync`; the
  precondition that made such a replacement stageable is refused at startup; no
  failure message asserts a filesystem state it did not establish.
- **Operational effect:** **moving or replacing the artifact root now requires a
  service restart** — the running service refuses `root_replaced` rather than
  following the name. A deployment whose root has an ancestor writable by
  another account, without the sticky bit, **will refuse to start**
  (`root_ancestor_untrusted`). Both are documented in operations §5.6 and
  `.env.example`.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending. D-a, D-b and D-c are unchanged and
  remain reserved to Peter.
- **Superseded in part by C-6.** The third re-review found the S-B-2 remediation
  described here materially correct about *where* operations resolve, and found a
  separate defect in *how* the final entry was published. C-6 also reopens the
  I-1 statement above. Nothing in this entry closed a finding.

## v1.5 clarification C-6 — Phase 2 I-03 third remediation (publication, I-1, test evidence)

Recorded 2026-08-05 by the working Technical Lead, after the third independent
implementation and security re-review. **No finding is closed, no gate is
claimed, and the Acceptance Authority has not decided it.** Full record: the same
[`../review/phase-2-i-03-remediation-submission.md`](../review/phase-2-i-03-remediation-submission.md)
and
[`../review/phase-2-i-03-remediation-review-request.md`](../review/phase-2-i-03-remediation-review-request.md),
both amended again.

- **Affected requirements:** §6.4 (immutable, content-addressed, restricted
  artifact storage), §6.5 (atomicity), §12 Phase 2 operational evidence. No
  requirement changes ownership, authority or scope.
- **Reason:** three findings.
  1. **Blocking — publication could overwrite an unvalidated entry.** The
     anchoring accepted in C-5 fixed which directory the final entry was created
     in. Publication itself remained `os.replace`, which is atomic about
     *replacing*: a checksum-named entry appearing between the `_holds()` check
     and the rename was removed and overwritten without being examined,
     contradicting immutability, refusal-not-repair, evidence preservation and
     "no artifact is implicitly deleted".
  2. **Important — `StorageOutcome.UNRESOLVED` made an unproven claim.** The
     conservative *default* asserted that nothing already held had been changed
     or removed, which finding 1 made false.
  3. **Important — the storage tests were not reproducible.** On the review host,
     `/` and `/tmp` are owned by uid 65534, and the startup ancestor rule refused
     32 tests before they reached their own assertions. The submitted count of
     1912 could not be independently reproduced.
- **Added scope:** publication by `os.link`, which creates the checksum entry or
  fails `EEXIST` and never removes what is already there; full revalidation of a
  concurrent winner through the anchored descriptor; a third `StorageOutcome`
  (`PRESERVED`) distinguishing "an entry was refused and left as found" from
  "there was nothing there"; a startup probe proving the filesystem supports
  hard links *and* refuses a link over an existing name (`link_unsupported`);
  `TrustedAncestors` as an injectable policy object so automated evidence is
  hermetic; a structural guard making cleanup unable to name anything but a
  temporary.
- **Removed scope:** none. No route, no capability, no retention decision.
- **Alternatives considered and rejected:** a pathname existence check followed
  by `os.replace` (the same race in a different shape, and explicitly refused by
  the review); `renameat2(RENAME_NOREPLACE)` (equivalent guarantee in one
  syscall, but the standard library exposes no wrapper and a hand-rolled `ctypes`
  syscall stub in the path holding every exported Actor's mechanics is a worse
  trade than one extra `unlink` — recorded in operations §5.6 and the adapter
  docstring); relaxing the production ancestor-ownership rule to make the tests
  pass (treated as a security-policy change reserved to Peter, and **not made**);
  broadly monkeypatching `os.stat`/`os.lstat` in the suite (would have stopped
  the root and target checks testing real behaviour).
- **Phase-boundary effect:** none. No new route, no new capability, no new
  caller, no Phase 3 surface, no schema change.
- **Dependency and critical-path effect:** none added. I-03 remains behind an
  independent implementation re-review, a separate security re-review and the two
  maintainer-supervised checks (operations §8.1, §8.2).
- **Estimate/forecast and capacity effect:** none recorded.
- **New or changed risks:** R-15 restated; new **R-16** (the artifact root's
  filesystem must support hard links) and **R-17** (the ancestor rule is a
  statement about the host and is a genuine deployment prerequisite that no test
  seam removes). See the RAID register.
- **Testing effect:** module tests 81, unchanged; the named narrow suites 372;
  full Python suite **1941**, zero skips. The suite was additionally run under a
  throwaway harness reporting `/` and `/tmp` as owned by uid 65534 — the review
  host's condition — and passed there too, which is the evidence finding 3 asked
  for. Still no formatter, linter or type checker configured or installed, and
  none was added.
- **Migration effect:** none. No schema change, no new migration, no edited
  migration; `alembic check` reports no new upgrade operations.
- **Security effect:** an entry under a checksum name that this service did not
  write and has not validated can no longer be destroyed by a submission. A
  concurrent writer of identical bytes converges rather than overwriting. No
  failure message, including the conservative default, asserts a filesystem state
  it did not establish.
- **Operational effect:** **the artifact root must be on a filesystem supporting
  hard links** (ext4, XFS, Btrfs, ZFS, tmpfs; not FAT/exFAT or some network
  mounts). The service proves this at startup and refuses `link_unsupported`
  otherwise. A new recovery procedure covers an unexpected entry found under a
  checksum name — preserve it, do not delete it. Both are documented in
  operations §5.6, §9 and `.env.example`.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** **both required and neither performed.**
- **Acceptance Authority decision:** pending. D-a, D-b and D-c are unchanged and
  remain reserved to Peter.

## v1.5 clarification C-7 — Phase 2 I-03 fourth remediation (evidence accuracy, I-3R-1)

Recorded 2026-08-05 by the working Technical Lead, after the third independent
implementation and security re-review returned its reports. At submission no
finding was closed and no gate was claimed. **The later independent re-review
and Acceptance Authority decision closing I-3R-1 are recorded below; no I-03 or
Phase 2 gate decision is implied.**
Full record:
[`../review/phase-2-i-03-fourth-remediation-submission.md`](../review/phase-2-i-03-fourth-remediation-submission.md),
with the re-review request at
[`../review/Handover information`](../review/Handover%20information).

- **Affected requirements:** §6.4 (immutable, content-addressed, restricted
  artifact storage) and §13.3 (review-gate evidence). No requirement changes
  ownership, authority or scope, and no acceptance criterion is reinterpreted.
- **Reason:** one Important **evidence-accuracy** finding, I-3R-1. The third
  re-review accepted the publication mechanism, I-1, I-2, root anchoring, S-B-1
  and S-I-1, and found that the third-remediation review request claimed "no
  temporary survives success or an ordinary failure" on the grounds that
  `_discard` runs on every path. Running `_discard` is not removal: it swallows
  `OSError` by design, and
  `test_a_failing_cleanup_leaves_the_published_artifact_alone` had already
  proved that a *successful* store can leave one private `.incoming-*` hard
  link. The implementation, the operations document and the test were right;
  the review evidence was not, and a false structural-guarantee table could
  have misled a storage-capacity or hygiene assessment.
- **What is superseded:** the temporary-cleanup row of the third-remediation
  structural-guarantee table, marked as superseded in place rather than
  rewritten. **C-6 is not otherwise superseded** — it did not repeat the claim,
  and the publication mechanism it records is unchanged and was not reopened.
- **Added scope:** none in the service. The corrected contract is stated
  consistently across the adapter docstring, the operations document,
  `.env.example`, the review record and the controlled records; operations §5.6
  gains "Temporary files left by a failed cleanup", a read-only, age-bounded,
  link-count-aware detection procedure; three tests in
  `tests/test_artifact_store.py` prove that procedure's rule against synthetic
  files.
- **Removed scope:** none.
- **Alternatives considered and rejected:** making the old sentence true by
  changing publication — rejected outright. The `os.link` design and the
  test-only bounded ancestor walk were both accepted by the third re-review and
  were not reopened, and no contradictory evidence was found. Making cleanup
  failure fail the submission — rejected: it would turn a correctly published
  artifact into a refusal over an `unlink`, which is the failure direction I-2
  exists to prevent. Adding a listing or deletion capability to the service so
  it could clean up after itself — rejected: it would broaden the service's
  filesystem authority beyond "create a temporary, and unlink one created in
  the attempt that is running", which is the property that makes a cleanup
  failure structurally unable to delete an artifact.
- **Dependency and critical-path effect:** none. The independent re-review was
  completed on 2026-08-05; the remaining critical path is the supervised and
  owner-controlled evidence followed by the Acceptance Authority's gate
  decision.
- **Estimate/forecast and capacity effect:** none.
- **New or changed risks:** **R-18 added** — leftover temporaries accumulate
  unnoticed and consume storage (Low/Low, Operations Owner). **R-9 in the
  package plan sharpened**: "a failed cleanup cannot delete a published
  artifact" was true and incomplete; what it can do is leave storage behind
  that nobody is told about. **D-11 added** to the package plan: detection is an
  operator procedure, deliberately not an application capability.
- **Testing effect:** three new tests (94 in `tests/test_artifact_store.py`, was
  91), all synthetic and read-only, exercising the documented `find` rule
  through the real `find`. No test was deleted or weakened, and the existing
  cleanup-failure test is preserved unchanged.
- **Migration effect:** none. No schema, no migration, no data.
- **Security effect:** none claimed. No security-relevant code or contract
  changed — publication, anchoring, the credential boundary and the CORS policy
  are untouched — so no new security re-review is requested. The security
  reviewer's own third report had already described the best-effort cleanup
  correctly.
- **Operational effect:** operators gain a documented way to find leftover
  temporaries and a rule for reading the link count before removing one; whoever
  sizes the artifact filesystem is told that leftovers are possible after a
  successful store. **How often the procedure should be run has not been
  decided**, and nothing automates it.
- **Product Owner recommendation:** pending.
- **Technical Lead review:** the implementing agent is the working Technical
  Lead and cannot approve its own recommendation.
- **Independent and security review:** the narrow independent implementation
  re-review was completed by Codex on 2026-08-05 and returned no Blocking,
  Important or Optional finding; it confirms I-3R-1 is resolved and the final
  traceability claims are truthful. Recorded in
  `docs/review/phase-2-i-03-fourth-remediation-codex-re-review.md`. No further
  security re-review was required, for the reason above.
- **Acceptance Authority decision:** Peter Duscha accepted the independent
  recommendation and closed I-3R-1 on 2026-08-05. This closes that finding only;
  it does not accept I-03 or close the Phase 2 gate. D-a, D-b and D-c are
  unchanged and remain reserved to Peter, and the retention question D-c also
  covers how often leftover-temporary hygiene should run.

## v1.5 clarification C-8 — database-unclaimed artifact retention D-c

Recorded and accepted by Peter Duscha on 2026-08-05.

- **Affected requirements:** Phase 2 rollback/recovery and snapshot-retention
  acceptance criterion; I-03 restricted artifact operations.
- **Reason:** database-unclaimed raw snapshots can be necessary for retry or
  incident investigation but contain sensitive Actor mechanics and must not be
  retained indefinitely.
- **Added/removed scope:** none. This decides the lifetime of an existing
  artifact class; it adds no route, mutation or automatic deletion.
- **Decision:** retain a database-unclaimed raw snapshot for at most 30 days and
  delete it sooner when its rehearsal, retry or incident closes. Preserve its
  checksum, provenance and sanitized audit record permanently. Investigate and
  report before deletion; the maximum does not authorize erasing evidence for
  an open incident.
- **Dependency and critical-path effect:** closes retention decision D-c. Other
  Phase 2 supervised evidence, performance thresholds, owner recommendations
  and the gate decision remain pending.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** narrows indefinite sensitive-artifact retention without
  weakening incident evidence handling.
- **Testing and migration effect:** none; policy/documentation only, no schema
  or executable-code change.
- **Security and operational effect:** bounds raw Actor-payload retention;
  operations §5.6 carries the investigation and deletion procedure.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision only.
- **Technical and independent review:** no implementation was introduced by the
  decision. The complete Phase 2 package still requires its final independent
  gate recommendation.
- **Acceptance Authority decision:** **accepted by Peter Duscha on 2026-08-05.**
  This accepts D-c only and does not accept I-03 or close Phase 2.

## v1.5 clarification C-9 — Phase 2 R4 observation and runtime thresholds

Recorded and accepted by Peter Duscha on 2026-08-05.

- **Affected requirements:** Phase 2 remediation plan §9.4 items 3 and 4.
- **Reason:** package R4 requires numeric observation and 500-Actor performance
  thresholds rather than subjective terms.
- **Decision:** use a zero-hour observation period with immediate post-run
  verification, endpoint shutdown and disposable-state cleanup. Accept 5
  seconds for preview and 5 seconds for fresh apply as Phase 2 rehearsal
  thresholds on this named host.
- **Evidence:** `docs/review/phase-2-r4-500-actor-benchmark.md`; Codex also ran
  the exact benchmark from a verified-empty `freedom_test` database and
  reproduced the 793.866 ms preview maximum, 1,313.291 ms fresh-apply maximum,
  5-second recommendations and clean return to Alembic `0004`.
- **Added/removed scope:** none. These are gate/rehearsal acceptance thresholds,
  not production capacity promises, application timeouts or new monitoring.
- **Dependency and critical-path effect:** closes §9.4 items 3 and 4. Items 1
  and 2—the bounded maintainer/gate availability and real-export rehearsal
  window—remain open and continue to block R4 readiness.
- **Estimate/forecast and capacity effect:** no calendar forecast is created.
- **Risk effect:** gives the rehearsal an objective performance refusal point;
  host-specific synthetic evidence does not predict production capacity.
- **Testing and migration effect:** 500-Actor harness and regression evidence;
  no schema or migration change. Full suite reported 1,954 passed with one
  dependency warning.
- **Security and operational effect:** benchmark used synthetic data and the
  local Unix-socket `freedom_test` database. Immediate cleanup retains no
  rehearsal service or raw state for continuing observation.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision only.
- **Technical and independent review:** Gemini produced the benchmark; Codex
  reviewed its safety corrections and independently reproduced the threshold
  inputs.
- **Acceptance Authority decision:** **accepted by Peter Duscha on 2026-08-05.**
  This closes only §9.4 items 3 and 4 and does not accept I-03 or Phase 2.

## v1.5 correction C-10 — canonical key order in the Foundry export contract

Recorded 2026-08-09. Ruled by Peter Duscha the same day, on finding RA-2 from
Rehearsal A.

> **Partly superseded by [C-12](#v15-correction-c-12--the-canonical-key-boundary-is-232--2-corrects-c-10),
> 2026-08-10.** The direction below — ECMAScript own-property order rather than
> plain code-point order — stands, and closing RA-2 stands. **The boundary
> stated below is wrong**: `[0, 2**53-1]` is the *integer index*, and ordinary
> object enumeration hoists only *array indices*, which end at `2**32 - 2`. The
> "Decision" and "Testing effect" bullets below should be read as corrected by
> C-12. This entry is left otherwise intact as the record of what was ruled on
> 2026-08-09.

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1
  ("Object keys"), new §1.0; `application/foundry/parser.py:canonical_bytes`;
  the `non_canonical_encoding` warning text in
  `application/foundry/reconciliation.py`.
- **Reason:** the contract required object keys "sorted by Unicode code point,
  at every depth", and **no conforming exporter could satisfy it**. dnd5e keys
  scale-value advancements by class level, so real Actors carry `{"1":…,"4":…,
  "10":…}`; ECMAScript places integer-index keys first in ascending numeric
  order, so a browser exporter emits `"1","4","10"` however it sorts. Verified
  against the shipped module rather than assumed: `canonical.js` sorts the key
  array to `["1","10","4"]` correctly, then rebuilds an object and the engine
  reorders it on insertion. `canonical_encoding` was therefore false for every
  real world and true only for synthetic fixtures — a flag structurally unable
  to carry information.
- **Decision:** adopt ECMAScript own-property order as the contract's canonical
  order — integer-index keys (canonical decimal integers in `[0, 2**53-1]`)
  first in ascending numeric order, then all other keys by Unicode code point.
- **Alternatives considered:** require such maps to be emitted as JSON arrays,
  which changes the wire shape and every consumer of it; or drop the
  canonical-encoding claim entirely, which discards a genuine
  cross-exporter comparability property. Both were rejected as larger than the
  defect.
- **Added/removed scope:** none. No field, aggregate, route or migration is
  affected, and nothing became writable or comparable that was not before.
- **Dependency and critical-path effect:** closes RA-2. **The Foundry module is
  unchanged and requires no version bump** — the exporter always conformed to
  the new rule; the contract had described something else. Module `1.0.5`
  remains the installed, rehearsed build of record.
- **Estimate/forecast and capacity effect:** none; no calendar forecast exists.
- **Risk effect:** removes a permanently-false report that would have trained
  operators to ignore a warning. The second half of the rule — string keys by
  code point — is this contract's own, not ECMAScript's, because the language
  would use insertion order there and a canonical form may not depend on that.
- **Testing effect:** four new parser tests pin numeric-before-string ordering,
  the array-index definition (`"01"`, `"-1"`, `"1.0"` are string keys), and
  recursion through nested lists and objects. Full suite 1,781 passed, 208
  skipped (database-dependent, no `TEST_DATABASE_URL` in this session).
- **Migration effect:** none. Artifact identity is the SHA-256 of the original
  bytes and is untouched; the Manager still never re-serialises an artifact.
  Duplicate detection never depended on canonicalisation.
- **Security and operational effect:** none. The warning text was also
  corrected: it claimed "two exports of an unchanged world will not compare
  equal", which was false — an exporter's own output is deterministic.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision.
- **Technical Lead and specialist reviews:** implemented by Claude, who also
  raised RA-2. **It carries no independent review**; it is part of the set going
  to the Independent Reviewer with the Phase 2 gate evidence.
- **Acceptance Authority decision:** **ruled by Peter Duscha on 2026-08-09.**
  This closes RA-2 and accepts no implementation beyond it; it does not close
  the Phase 2 gate.

## v1.5 correction C-11 — performance threshold restated per megabyte (amends C-9)

Recorded 2026-08-09. Ruled by Peter Duscha the same day, on finding RA-5 from
Rehearsal B.

- **Affected requirements:** change-log **C-9** (Phase 2 remediation plan §9.4
  items 3 and 4); `tests/benchmark_snapshot_500.py`;
  `docs/review/phase-2-r4-500-actor-benchmark.md` as the evidence C-9 rests on.
- **Reason:** C-9 accepted "5 seconds for preview and 5 seconds for fresh apply"
  measured in wall-clock seconds against an **Actor count**, using synthetic
  Actors of 2,182 bytes. Rehearsal B previewed real Actors of 508,975 bytes —
  **233× larger** — and took 9.566 s, breaching the threshold while producing 0
  errors, 0 warnings and a complete reconciliation. Throughput was **587 ms/MB
  against the benchmark's 728 ms/MB**: the real run is *faster* per megabyte. A
  count-based threshold measures the corpus, not the code. Discovery finding
  F-F5 had already recorded that "an actor is 1.1–3.3 MB of JSON" before the
  benchmark was written, so the corpus was known to be unrepresentative.
- **Decision:** three parts.
  1. The Phase 2 gate criterion is **throughput: ≤ 1,200 ms per megabyte**,
     measured from the slowest sample. Observed 587 (real) and 728 (synthetic).
  2. C-9's 5-second figures are **retained as synthetic smoke-test context and
     are no longer gate criteria.** They are not deleted: they remain the record
     of what was measured on that corpus.
  3. The absolute 9.566 s is recorded as a **Phase 3 architecture input**, not a
     Phase 2 pass/fail — see below.
- **Alternatives considered:** re-baselining the wall-clock number against a
  real-sized corpus, which keeps a figure that must be re-derived whenever the
  folder grows; and dropping the threshold, which was explicitly rejected — it
  is the only control that would catch an N+1 query or a quadratic parse.
- **Added/removed scope:** none.
- **Dependency and critical-path effect:** closes RA-5. Removes a breach that
  would otherwise have had to be argued or waived at the gate.
- **Estimate/forecast and capacity effect:** none. This is still not a
  production capacity promise, exactly as C-9 said of itself.
- **Risk effect:** replaces a criterion that could pass a bad implementation on
  a small corpus, and fail a good one on a real corpus, with one that does
  neither. **Phase 3 consequence:** at 9.566 s for 32 Actors and growing, the
  Council preview cannot be a synchronous HTTP handler; it needs a background
  job or progressive response. That constraint is now recorded in the plan's
  Phase 3 section rather than waiting to be rediscovered during implementation.
- **Testing effect:** `THROUGHPUT_LIMIT_MS_PER_MB` and a `throughput_gate`
  block are in the benchmark harness, reported whether or not they pass. Three
  new tests pin the unit, the breach reporting, and that the gate measures the
  slowest sample rather than the median — a median would let one pathological
  run hide behind six good ones. Suite: 1,784 passed, 208 skipped.
- **Migration effect:** none.
- **Security and operational effect:** none.
- **Product/Data/Operations Owner recommendation:** accepted by Peter Duscha in
  those roles for this decision.
- **Technical Lead and specialist reviews:** proposed and implemented by Claude,
  who also raised RA-5. **No independent review**; it goes to the Independent
  Reviewer with the Phase 2 gate evidence.
- **Acceptance Authority decision:** **ruled by Peter Duscha on 2026-08-09.**
  Closes RA-5. Closes no gate.

## v1.5 correction C-12 — the canonical key boundary is `2**32 - 2` (corrects C-10)

Recorded 2026-08-10 on **finding I-1** of the independent Phase 2 gate review
(`docs/review/Handover information`). **Proposed; not yet ruled.**

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1 and
  §1.0; `application/foundry/parser.py` (`_MAX_ARRAY_INDEX`,
  `_canonical_key_order`, `canonical_bytes`); change-log **C-10**, which this
  entry corrects.
- **Reason:** C-10 adopted ECMAScript own-property order but wrote the boundary
  as "integer index … `[0, 2**53 - 1]`". `OrdinaryOwnPropertyKeys` hoists
  **array indices** — `ToString(ToUint32(P))` is `P`, and `ToUint32(P) ≠
  2**32 - 1` — which end at `4294967294`. An *integer index* is a
  `String.prototype`/typed-array concept ordinary object enumeration never
  consults. This was an **observed cross-language disagreement**, not a wording
  slip: for `{"5000000000":…,"10000000000":…}` the shipped exporter emitted
  `{"10000000000":…,"5000000000":…}` (both are ordinary string keys to it, so
  code point decides) while the Python verifier sorted them numerically and
  emitted the other order. Every artifact carrying a canonical decimal key of
  ten or more digits would have been reported non-canonical against a
  conforming exporter. The committed fixture could not see it: its
  integer-looking keys are dnd5e class levels, which are array indices under
  either rule.
- **Decision:** the canonical order is array-index keys — canonical decimals in
  `[0, 2**32 - 2]` — first in ascending numeric order, then every other key by
  Unicode code point. The second half remains this contract's own, as C-10 said.
- **Alternatives considered:** changing the exporter to sort all numeric-looking
  keys numerically, which is impossible — the engine's hoisting is not
  something a script can opt out of for an ordinary object; and emitting such
  maps as arrays, rejected by C-10 already as larger than the defect.
- **Added/removed scope:** none.
- **Dependency and critical-path effect:** **the Foundry module is unchanged,
  byte for byte, and keeps version `1.0.5`.** The exporter always implemented
  the corrected rule — `canonical.js` sorts the key array by code point, rebuilds
  an object, and the engine hoists exactly the array indices — so only the
  verifier and the contract described something else. `1.0.5` remains the
  installed, rehearsed build of record, and the rehearsals' evidence is
  unaffected. `canonical.js`'s header comment still describes the *sort* rather
  than the emitted order; it is deliberately not edited, because editing an
  installed and rehearsed build's bytes under the same version is what the
  version identity control (CL3-I-2) exists to prevent. Carried to the next
  version bump.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes a false `canonical_encoding = false` for conforming
  real exports — the same class of permanently-wrong report C-10 removed, one
  boundary further out. **Rehearsal B's recorded `canonical_encoding = yes` is
  not disproved**: the real artifact evidently held no key at this boundary. It
  is the claim that C-10 was correct and complete that is corrected here.
- **Testing effect:** a new `foundry-module/tests/emit-canonical.mjs` runs
  caller-chosen documents through the shipped `canonicalBytes`, which is what
  makes the boundary reachable from a cross-language test at all. Eight boundary
  documents are asserted three ways in `tests/test_exporter_contract.py` — the
  exporter's bytes, the verifier's bytes, and that they are equal — covering
  `"0"`, `"4294967294"`, `"4294967295"`, `"5000000000"`/`"10000000000"`, the old
  bound's own values, the noncanonical forms `"01"`, `"-1"`, `"1.0"`, `" 1"`,
  `"+1"`, `"1e2"`, and recursion through nested objects and arrays. Mirrored in
  `foundry-module/tests/canonical.test.mjs` and pinned for the verifier alone in
  `tests/test_snapshot_parser.py`.
- **Migration effect:** none. Artifact identity is still the SHA-256 of the
  original bytes; no stored row changes.
- **Security and operational effect:** none.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex as independent
  review finding I-1; implemented by Claude. Returns to the Independent Reviewer
  with the corrected package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.

## v1.5 correction C-13 — lost-pin recovery requires settlement, not a timeout

Recorded 2026-08-10 on **finding B-1** of the independent Phase 2 gate review.
**Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  and §6 step 10; `docs/review/phase-2-i-03-cl3-remediation.md` and
  `docs/review/phase-2-supervised-rehearsal-2026-08-09.md`, both of which
  recorded CL3-B-1 as closed.
- **Reason:** the procedure told the operator to wait until the final
  "request/timeout has finished", query, repeat once, and then authorize a fresh
  export on a miss. **A client timeout establishes only that the browser stopped
  waiting.** The reload does not cancel the POST — `wsgiref.simple_server` runs
  a handler to completion whether or not anyone is listening — so both queries
  can run before the server transaction commits, both miss, a fresh export is
  authorized, and the original commits afterwards. The fresh export carries its
  own checksum, so the uniqueness constraint cannot merge them: one real
  submission becomes two pending artifacts. The whole-episode window correction
  (CL3-B-1) fixed a different false miss and left this one.
- **Decision:** a miss may not be recorded until **settlement** is positively
  established and recorded — either **S-A**, the process that served the episode
  has exited (an exited process commits nothing), or **S-B**, that same process
  has answered a later probe, which on a single-threaded server proves every
  earlier handler already returned. Both are corroborated by `pg_stat_activity`
  showing no transaction in flight. A fourth outcome, **Unsettled**, is added
  beside hit/miss/ambiguous and is an incident, not a miss. The repeat-once rule
  survives for operator error but is explicitly no longer what makes a miss safe.
- **Alternatives considered:** a settlement *deadline* derived from the proxy's
  `read_timeout`/`write_timeout`, rejected because those bound Caddy's patience
  and not the upstream handler — `wsgiref.simple_server` enforces no request
  deadline of its own, so the deadline would have been a guess wearing a
  number's clothes. Also considered and rejected: persisting the pin so recovery
  needs no server evidence, which the standing confidentiality constraint
  forbids (no Actor data or credential in browser-readable Foundry settings).
- **Added/removed scope:** none. No code path, route, schema or credential
  changes; the endpoint behaves exactly as before.
- **Dependency and critical-path effect:** reopens and then re-closes CL3-B-1.
  **S-B is a property of `wsgiref.simple_server` and does not survive Phase 3's
  concurrent `freedom-web` process**; replacing it is recorded as a Phase 3
  obligation in §9. S-A holds under any server.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the last reachable path from one real submission to
  two pending artifacts. Costs a delay when settlement cannot be established,
  which is the intended direction to fail in.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` reproduces
  the late-commit sequence deterministically against the real submission service
  (a gated `commit`, two misses while the transaction is open, the commit
  landing afterwards), and exercises the settlement probe against a real
  `wsgiref.simple_server` over the real WSGI application. That second test was
  checked against a threaded server as a negative control and **fails** there
  with the message the Phase 3 obligation predicts, so it is not vacuous.
  `tests/test_snapshot_recovery_documentation.py` gains four tests pinning the
  settlement step, the unsettled outcome and the Phase 3 note.
- **Migration effect:** none.
- **Security and operational effect:** operational only, and it is the point.
  The probe is unauthenticated by design so that it is refused `401` before a
  principal exists, writing no audit event, no snapshot row and no artifact —
  recovery must not write. §6 step 10 also now states that the injector must
  fault the POST rather than the CORS preflight (finding RA-4), and that step 10
  does **not** exercise the late-commit case.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex as independent
  review finding B-1; implemented by Claude. Returns to the Independent Reviewer
  with the corrected package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
- **Superseded in part by C-14.** The re-review of this entry found S-B as
  written still inferring accept order from issuance order. S-B is now two
  conditions, S-B.1 and S-B.2; read C-14 with this entry. Nothing else here
  changes, and S-A is untouched.

## v1.5 correction C-14 — S-B needs proof the delivery path has drained

Recorded 2026-08-10 on the **re-review of C-13**, which held finding B-1 open.
**Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-B) and §5.4 (proxy configuration).
- **Reason:** C-13's S-B argued that because the settlement probe is *issued*
  after the episode's last attempt, a single-threaded server must *accept* it
  after that attempt. That does not follow. `wsgiref.simple_server` guarantees
  serial handling in **accept** order, and the submission reaches it through
  Caddy while the probe is sent straight to loopback. A submission Caddy is
  still holding has not reached the endpoint at all, so the endpoint can answer
  the later probe first, the query can then miss, and the submission can be
  accepted and commit afterwards — the same false miss C-13 set out to remove,
  reached by a different route. `pg_stat_activity` cannot cover it either: a
  request that has not reached the application has no backend to observe.
- **Decision:** S-B becomes two conditions, and the second is worthless without
  the first. **S-B.1** requires positive, recorded evidence that nothing can
  still be delivered: the client is gone and the submitting GM confirms no
  attempt since the episode's last; Caddy's `caddy_http_requests_in_flight`
  gauge reads zero for every series of the server fronting this endpoint; and
  the endpoint's current connections are recorded, each of them necessarily
  established before the probe's. The gauge is labelled by server and handler
  and not by route, so a host busy with unrelated traffic cannot satisfy it —
  §9 states that as an honest "cannot establish" rather than working around it. **S-B.2**
  is the probe, unchanged. The settlement argument is restated as an explicit
  chain whose only claim about issuance order is the one S-B.1 observes. An
  unreadable or non-zero in-flight counter is an **unsettled** episode, and §9
  now states the maintainer-authorized way out of one: stopping the endpoint
  process converts it into S-A.
- **Alternatives considered:** a settlement deadline (rejected in C-13, and the
  reasoning is unchanged). Replacing S-B outright with an application-level
  in-flight or quiescence mechanism was considered and **deferred, not
  rejected**: it is the better answer and it is already the recorded Phase 3
  obligation, but it is a code change to the submission path during a gate
  re-review, and S-B.1 is obtainable today from configuration and read-only
  observation. §9 records that such a mechanism would retire S-B.1 as well.
- **Added/removed scope:** §5.4 now requires Caddy's per-server metrics to be
  enabled, so the counter S-B.1 reads exists. No code path, route, schema or
  credential changes; the endpoint behaves exactly as before.
- **Dependency and critical-path effect:** none beyond C-13's. S-B.1 depends on
  Caddy being the only path to the endpoint and on it reporting what it holds;
  §9 records both, and records that another hop in front of the endpoint
  reopens the same gap.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** closes the remaining path from one real submission to two
  pending artifacts. Costs a delay whenever drain cannot be evidenced, which is
  the intended direction to fail in.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` gains two
  tests. One reproduces the false miss S-B.1 exists to prevent — the probe's
  connection accepted and answered, and both queries run, before the
  submission's connection is made at all. The other establishes what S-B.1
  buys: with the submission connected and sent but **not yet accepted, read or
  handled**, the probe still cannot be answered first. That second test is the
  case the C-13 test did not reach, because it waited until the submission was
  already inside its commit. Both were checked against a threaded server as a
  negative control; the ordering test fails there with the message the Phase 3
  obligation predicts, and the false-miss reproduction passes there as it
  should, since it does not depend on serial handling.
  `tests/test_snapshot_recovery_documentation.py` gains three tests pinning
  S-B.1, the §5.4 metrics requirement and the unsettled outcome's new trigger.
- **Migration effect:** none.
- **Security and operational effect:** operational. The added evidence is two
  read-only observations on loopback — Caddy's admin metrics and the socket
  table — and the probe is unchanged and still writes nothing. Caddy's admin
  API stays loopback-only.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex when re-reviewing
  C-13's remediation of B-1; implemented by Claude. **Carries no independent
  review** and returns to the Independent Reviewer with the package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
- **Superseded by C-15.** The re-review of this entry found that
  `caddy_http_requests_in_flight` does not mean what S-B.1 needed it to mean.
  S-B.1 and S-B.2 are both **withdrawn**; read C-15 instead. S-A survives, in a
  corrected and stricter form.

## v1.5 correction C-15 — settlement is a stopped endpoint, not an observed drain

Recorded 2026-08-10 on the **re-review of C-14**, which held finding B-1 open for
the third time. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1, step 3, a new step 4, and §5.4 (proxy configuration); §6 step 10's
  settlement note.
- **Reason:** C-14's S-B.1 rested on Caddy's `caddy_http_requests_in_flight`
  reading zero as evidence that the proxy held nothing. Caddy documents that
  gauge more narrowly, as the requests **currently being handled**
  ([metrics](https://caddyserver.com/docs/metrics)). It does not cover a
  connection Caddy has accepted whose request has not entered the instrumented
  handler, nor body bytes still arriving over an established HTTP/1.1, HTTP/2 or
  HTTP/3 connection; closing or reloading the Foundry page does not establish
  that what the browser already transmitted has been consumed; and sampling the
  gauge and then the socket table is two observations rather than one atomic
  drain. So the false miss survived C-14: the submission has been sent but has
  not entered the handler, the gauge reads zero, the query misses twice, and the
  request is then handled and commits. C-13's S-A had a smaller version of the
  same hole — it accepted "a process that started after the episode", and the
  proxy can hand the episode's stranded request to a replacement process as
  readily as to the original.
- **Decision:** settlement stops being an observation of what is in flight and
  becomes a **state**: the endpoint is not running, and does not run again until
  the outcome has been recorded. The probe (S-B.2) and the gauge (S-B.1) are
  **withdrawn**, and a settlement recorded from either is not a settlement. S-A
  is now four recorded parts: the process that served the episode is gone
  (`ps`/`ss`, by start time); **nothing is listening on the port**, a replacement
  process being explicitly insufficient; the path through Caddy is confirmed dead
  by a `502`/`503` from Caddy itself; and the endpoint stays down through the
  query and the recording. `pg_stat_activity` corroboration is unchanged. The
  argument is that every commit on this path begins with an accept, and an
  unserved port accepts nothing — wherever the request happens to be. A new
  **step 4** then covers the residual after the restart: following a fresh
  submission, the step-2 query is re-run over the widened window, and a second
  acceptance event whose checksum is not the fresh submission's is an
  **ambiguous** outcome and a defect in this procedure, resolved by superseding
  one artifact through the documented correction flow rather than by the Council
  reviewing both.
- **Alternatives considered:** an *actual* proxy drain — stopping Caddy or
  removing the route — which stops new intake but takes down every other service
  on the host to reconcile one snapshot, where stopping the endpoint alone is
  both narrower and strictly stronger. An **application-level in-flight or
  quiescence mechanism**, the reviewer's preferred answer, remains
  **deferred, not rejected**: it is what §9 now records as the Phase 3
  improvement, and it is the only way to settle an episode without a stop. A
  settlement deadline stays rejected for C-13's reasons. Persisting the pin stays
  rejected under the confidentiality constraint.
- **Added/removed scope:** §5.4 no longer requires Caddy's per-server metrics —
  nothing in the document reads them now — and instead requires that **no
  upstream retry window** stand in front of the endpoint (`lb_try_duration` unset,
  no second proxy or queue), because a hop that holds a refused request would let
  a stranded submission arrive after the endpoint returns. Where metrics are kept
  for monitoring, §5.4 now shows the current global `{ metrics }` form; the nested
  `servers { metrics }` form still adapts on the installed Caddy 2.10.2 but
  `caddy adapt` warns it is removed in the next major version. Step 4 is added
  scope for the operator. No code path, route, schema or credential changes.
- **Dependency and critical-path effect:** S-A no longer depends on the
  endpoint's concurrency model, so it holds unchanged for Phase 3's `freedom-web`;
  what was a Phase 3 *obligation to repair* becomes a Phase 3 *improvement*,
  namely settling without taking the service down. It does depend on Caddy being
  the single path and on that path failing a refused request, which §5.4 records.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the reachable false miss that survived C-13 and C-14,
  at the cost of a deliberate endpoint stop during recovery — acceptable for a
  hand-started rehearsal process, and the reason the Phase 3 improvement is
  recorded. Step 4 makes the remaining residual detectable rather than assumed
  away.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` replaces the
  two probe-ordering tests with the two that establish S-A against a real
  `wsgiref.simple_server` over the real WSGI application: a submission
  **connected, fully sent and waiting unaccepted** at the endpoint commits
  nothing when the endpoint stops without serving it, and a delivery attempted
  after the stop is refused at the socket while what committed before the stop
  stays visible to the query. The first was checked against a negative control
  that serves the queue instead of stopping — it fails there, so it discriminates
  the stop. The late-commit reproduction and the withdrawn probe's false miss are
  both retained. `tests/test_snapshot_recovery_documentation.py` pins the single
  condition and its four parts, the named defects of both withdrawn conditions,
  §5.4's retry-window requirement and non-deprecated metrics form, the unsettled
  triggers, and step 4.
- **Migration effect:** none.
- **Security and operational effect:** operational. Recovery still writes
  nothing: the two remaining observations are read-only, and the confirming
  request through Caddy cannot reach the application because the endpoint is
  down. Stopping the endpoint is maintainer-authorized because it deliberately
  aborts in-flight work — a rollback, not a loss.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex when re-reviewing
  C-14's remediation of B-1; implemented by Claude. **Carries no independent
  review.** B-1 is **not** recorded as closed: the reviewer holds it open, and
  closing it is the reviewer's to do.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
- **Superseded in part by C-18.** The re-review of this entry found the stop
  correct and its **scope** wrong: it covers the endpoint and not the path in
  front of it, so a request the proxy holds and has not yet dialled upstream for
  survives the down window and commits after the restart. S-A.1 and S-A.2 survive;
  **S-A.3 is withdrawn and inverted** — a `502` from Caddy now means Caddy is
  running — and S-A.4 becomes S-D. Read C-18 instead.

## v1.5 correction C-16 — an NFC key collision is a refusal, and both halves normalise keys

Recorded 2026-08-10, on the open defect
`docs/review/phase-2-canonical-nfc-key-collision.md` (found while remediating
finding I-1) and on the maintainer instruction to fix both implementations
together, add the refusal code and bump the exporter version before Phase 2
closes. **Proposed; not yet ruled.**

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1
  ("Unicode") and a new §1.2; `foundry-module/scripts/canonical.js` (`normalise`,
  header comment) and both module manifests, now **`1.0.6`**;
  `foundry-module/scripts/transport.js` (`SERVER_ARTIFACT_CODES`);
  `application/foundry/parser.py` (`_ordered`, new `_nfc_keys`, `canonical_bytes`,
  `parse_snapshot`); `application/foundry/submission.py`
  (`ARTIFACT_REFUSAL_CODES`); the review record above, which is closed by this
  entry.
- **Reason:** the encoder sorted an object's keys by their **pre**-NFC form and
  inserted them under their **post**-NFC form. Two distinct keys sharing an NFC
  form — `é` as U+00E9 and as U+0065 U+0301 — therefore wrote to the same
  property of the result, the second write won, and **the first value was
  silently dropped**, with no refusal, warning or record. That is precisely the
  outcome `canonical.js`'s own header says the contract exists to make
  impossible, and the one path in the encoder that lost data instead of refusing
  (§1.1 refuses an `undefined` value and an `undefined` array element). The
  Python verifier meanwhile did not normalise keys at all, so for the same input
  it emitted a document carrying **the same key twice** — a canonical form of
  nothing — and disagreed with the exporter for every non-NFC key. A third
  cross-language disagreement after RA-2 and I-1, in the same family.
- **Decision:** normalise before sorting, and **refuse a collision** in both
  implementations under one new code, `nfc_key_collision`. A merge is not
  available: the two keys are different properties of a Foundry document and no
  rule in this repository says which one an operator meant. The Manager refuses
  the artifact for the same reason, which makes this the one place
  canonicalisation is enforced rather than reported — a colliding document has no
  canonical form and cannot have come from a conforming exporter, where a merely
  non-canonical one is a conforming exporter's bytes in another order and stays a
  warning. The operator remedy is to rename one property in Foundry and export
  again. A **single** non-NFC key is not a collision and is normalised, not
  refused.
- **Alternatives considered:** resolving the collision by keeping the first or
  last key, rejected because the survivor would be chosen by the code-point order
  of the pre-NFC forms — a property of neither the data nor the operator's
  intent — and because it is data loss either way; refusing in the exporter only,
  which would leave the verifier emitting an invalid duplicate-key form and
  replace one cross-language disagreement with another; and normalising keys
  without refusing in the Manager, rejected because a document with no canonical
  form has nothing for `canonical_encoding` to report truthfully.
- **Added/removed scope:** the verifier now also normalises **string values** to
  NFC, which §1 always required and it never did. Without it the two
  implementations still disagreed over the boundary this entry claims to close:
  a decomposed value was reproduced verbatim and the artifact reported
  canonical, when the exporter would have emitted the composed form and
  different bytes. No field, route, schema or migration changes.
- **Dependency and critical-path effect:** **the module changes, so it is
  `1.0.6`**, and `1.0.5` is superseded. `exporter.version` reaches
  `foundry_snapshots.exporter_version` and checksum-bearing audit history, so
  two behaviourally different builds may not share a version string (CL3-I-2);
  this is the version bump the C-12 comment correction was carried against, and
  that correction is made here. **Rehearsals A and B were performed on `1.0.5`**
  and remain the evidence of record for that build; before any further rehearsal
  or supervised submission, `1.0.6` must be the build those instances actually
  serve. It was installed on `foundry1` and `foundry3` on 2026-08-10 and recorded
  in `docs/review/phase-2-module-1.0.6-install-2026-08-10.md`; **neither instance
  has been restarted**, so until they are, an export could still stamp `1.0.5`. For every document whose keys are already NFC — which is every ASCII
  key, and so every artifact either rehearsal produced — `1.0.6` emits **the same
  bytes** as `1.0.5`: normalisation is the identity there, so sorting before or
  after it cannot differ.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the only path by which an Actor value could disappear
  from an export without a refusal. **Reachability against real data was never
  demonstrated and is still not claimed** — Foundry document keys are
  predominantly ASCII schema names and ids, and neither rehearsal artifact was
  examined for non-NFC keys; the candidates are `flags` namespaces and
  user-supplied map keys. The fix is worth making regardless, because the
  contract's claim is that data cannot vanish from an export without a refusal.
  The new refusal is reachable by an artifact no conforming exporter produces,
  so it cannot refuse a submission that would previously have been accepted and
  correct.
- **Testing effect:** the two tests that held the defect open are converted to
  the fixed behaviour and now run — the node `todo` is a real test and the strict
  `xfail` in `tests/test_snapshot_parser.py` is gone. `foundry-module/tests/canonical.test.mjs`
  covers both insertion orders, a nested collision whose message names the path
  and no value, a lone non-NFC key, and that normalisation precedes the sort.
  `tests/test_snapshot_parser.py` mirrors all four for the verifier, pins NFC
  normalisation of string values, and asserts `parse_snapshot` refuses a
  colliding artifact **with its checksum attached**.
  `tests/test_exporter_contract.py` adds an NFC boundary in the shape C-12
  established: five documents asserted three ways — the shipped exporter's bytes,
  the verifier's bytes, and that they are equal — plus one document both
  implementations must refuse with the same code.
  `foundry-module/tests/emit-canonical.mjs` reports a refusal as
  `{"code":…,"index":…}` on stderr with exit 1, so the cross-language test can
  assert *which* refusal rather than pattern-matching a stack trace.
  `tests/test_snapshot_submission.py` already walks both modules' syntax trees
  and holds `ARTIFACT_REFUSAL_CODES` and the module's `SERVER_ARTIFACT_CODES` to
  exactly the parser's codes, so the new code had to be declared in all three
  places to pass.
- **Migration effect:** none. Artifact identity is still the SHA-256 of the
  original bytes, no stored row changes, and no artifact previously accepted
  becomes invalid.
- **Security and operational effect:** operational only, and one deployment step:
  install `1.0.6` before the next supervised export. Refusal messages name the
  path and never a key's value, as every refusal in both files already does.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** the defect was found and recorded by
  Claude on 2026-08-10 and confirmed by the independent reviewer, who ruled that
  leaving the regression tests as `todo`/`xfail` left the release vulnerable and
  directed that both implementations be fixed together. Implemented by Claude.
  **Carries no independent review**, and goes to the Independent Reviewer with
  the rest of the returned package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.
  This closes the defect record; it closes no gate.

## v1.5 correction C-17 — canonical numbers are ECMAScript's, not `json.dumps`'s

Recorded 2026-08-10 on the **Blocking finding** of the independent review of the
C-16 package. **Proposed; not yet ruled.**

- **Affected requirements:** `docs/rules/foundry-export-contract.md` §1
  ("Numbers") and a new §1.3; `application/foundry/parser.py` (new `_double`,
  `_shortest_decimal`, `_ecmascript_number`, `_serialise`; `_ordered` renamed
  `_normalised`; `canonical_bytes`); `application/foundry/submission.py`
  (`ARTIFACT_REFUSAL_CODES`); `foundry-module/scripts/transport.js`
  (`SERVER_ARTIFACT_CODES`) and both module manifests, now **`1.0.7`**.
- **Reason:** the verifier encoded numbers with `json.dumps`, whose float
  formatting is a **different function** from `JSON.stringify`'s. Python
  switches to exponent notation at `1e16` and below `1e-4` and zero-pads the
  exponent; ECMAScript switches at `1e21` and below `1e-6` and does not. So the
  exporter emits `100000000000000000000` and `1e-7` where the verifier emitted
  `1e+20` and `1e-07`, and a conforming artifact containing either was reported
  `canonical_encoding = false`. This is the third instance of one defect — after
  C-12's key boundary and C-16's NFC boundary — in which both implementations
  were self-consistent and disagreed with each other, and it is the same
  consequence each time: the flag reports a defect in a conforming exporter, so
  the canonical-contract remediation and the stable-export diagnostic it feeds
  are not trustworthy. The earlier boundary tables could not see it: every
  number in the golden bundle and in both of them is a small integer, which the
  two languages format identically. `json.dumps` also wrote a Python `float`
  `9.0` as `9.0`, which the exporter — having one number type — writes as `9`.
- **Decision:** a contract number is an IEEE-754 double written as
  `Number::toString` writes it, stated as a rule table in §1.3 rather than by
  naming a library function. An integer literal is read as the double a browser
  would have read it as, so an artifact carrying `9007199254740993` is reported
  non-canonical against `9007199254740992`. A literal outside the double range
  has no canonical form and is a **refusal** under the exporter's own code,
  `non_finite_number`; `-0` does have one (`0`) and is reported, not refused,
  which is a deliberate asymmetry with the exporter and is written down as one.
- **Alternatives considered:** constraining the exporter to a number domain both
  languages format alike — rejected, because the domain would exclude ordinary
  dnd5e values and the exporter cannot control what Foundry holds; and matching
  Python's formatting in the exporter, which is impossible for the same reason
  C-12 gave for key order: `JSON.stringify` is `Number::toString` and a script
  cannot opt an ordinary number out of it.
- **Added/removed scope:** none.
- **Dependency and critical-path effect:** **the exporter's output is unchanged,
  byte for byte.** `canonical.js` has always delegated numbers to
  `JSON.stringify`, so, as with C-12, only the verifier and the contract
  described something else. The module bytes change for one reason only — the
  new refusal code is added to the client's bounded `SERVER_ARTIFACT_CODES`
  list — and that is a version bump to **`1.0.7`** under the version identity
  control (CL3-I-2), not a change to what is exported. **`1.0.7` was installed on
  `foundry1` and `foundry3` on 2026-08-10 23:24:18 UTC**
  ([record](../review/phase-2-module-1.0.7-install-2026-08-10.md)), replacing
  `1.0.6`, and both worlds were launched at 23:40, which is what reloads the
  package registry `exporter.version` is read from. No supervised export has been
  taken with it, and both rehearsals remain evidence for `1.0.5`, the build they
  exercised.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes a false `canonical_encoding = false` for conforming
  real exports, one boundary further out again — and this one is reachable by
  ordinary data, not only by a contrived key: dnd5e carries fractional values
  (encumbrance multipliers, spell scaling, currency weight), and any of them
  outside `[1e-4, 1e16)` produced the wrong flag. **Rehearsal B's recorded
  `canonical_encoding = yes` is not disproved**; the real artifact evidently held
  no number at these thresholds. The new refusal is reachable only by an artifact
  no conforming exporter produces, so it cannot refuse a submission that would
  previously have been accepted and correct — it replaces an uncaught
  `ValueError` from `json.dumps(allow_nan=False)`, which was not a refusal at
  all. Encoding is now a pure-Python pass rather than a C one: measured at
  **+100 ms** on a 1.2 MB, 500-Actor bundle against the 5-second preview
  threshold set by C-9 and the ~740 ms preview measured in
  `docs/review/phase-2-r4-500-actor-benchmark.md`.
- **Testing effect:** eleven number-boundary documents are asserted three ways in
  `tests/test_exporter_contract.py` in the shape C-12 established — the shipped
  exporter's bytes, the verifier's bytes, and that they are equal — covering both
  notation thresholds from both sides, multi-digit exponents, both ends of the
  double range, integer literals past `2**53`, negatives, decimal-point
  placement, and recursion. A fortieth-value `PRECISION_SPREAD` asserts the two
  languages compute the same shortest round-tripping digits, which is the half of
  `Number::toString` neither implementation writes itself. Two further
  cross-language tests pin the refusal both must raise and the one asymmetry.
  `tests/test_snapshot_parser.py` pins the verifier's half as a twenty-row table
  that also records what `json.dumps` used to write, and asserts the refusal
  reaches `parse_snapshot` **with its checksum attached** and the end-to-end flag
  for `1e-7` against `1e-07`. `foundry-module/tests/canonical.test.mjs` pins that
  `serialise` delegates numbers to `JSON.stringify`. The syntax-tree tests in
  `tests/test_snapshot_submission.py` again forced the new code to be declared in
  all three places.
- **Migration effect:** none. Artifact identity is still the SHA-256 of the
  original bytes, no stored row changes, and no artifact previously accepted
  becomes invalid.
- **Security and operational effect:** operational. The deployment step this
  entry called for — install `1.0.7` in place of `1.0.6` before the next
  supervised export — was **carried out on 2026-08-10**, and carrying it out
  corrected a claim this entry made: `exporter.version` is read from the server's
  package registry, which reloads at **world launch** rather than at process
  start, so "neither instance has been restarted" never preserved `1.0.5`. Both
  instances launched worlds at 20:55 that day, six minutes after `1.0.6` went in.
  The refusal message names the path and never a value, as every refusal in both
  files already does.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the independent reviewer
  as the Blocking finding on the C-16 package; implemented by Claude. **Carries
  no independent review**, and returns to the Independent Reviewer with the rest
  of the package.
- **Acceptance Authority decision:** **none recorded.** Awaiting the maintainer.

## v1.5 correction C-18 — settlement terminates the whole ingress path, and step 4 retires the route

Recorded 2026-08-10 on the **re-review of C-15**, which held finding B-1 open for
the fourth time, and on the maintainer's ruling of 2026-08-10 between the two
routes the reviewer offered. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1, step 3 and step 4, and §5.4 (proxy configuration); §6 step 10's
  settlement note.
- **Reason:** C-15 settled an episode by stopping the **upstream endpoint**. That
  disposes of every request that had reached the endpoint, and not of a request the
  proxy has accepted, or is still reading, and has **not yet dialled upstream
  for**. Such a request is not in the endpoint's accept queue, so the stop does not
  reach it, and it has made no upstream attempt, so §5.4's "no upstream retry
  window" does not govern it either — that rule addresses a retry after a *refused*
  dial, and this request's **first** dial has not happened. It happens whenever the
  proxy gets to it, which under C-15's own step 4 can be after the endpoint has been
  restarted; the episode then commits behind a settled miss that has already
  authorized a fresh export. C-15's step 4 detects that afterwards, and **detection
  is not prevention**. The same reading condemns C-15's **S-A.3**, which nobody had
  questioned: it confirmed settlement by receiving a `502`/`503` from Caddy, and a
  `502` is Caddy's own answer, so receiving one establishes that Caddy is running.
- **Decision:** settlement remains a **state** rather than an observation, and
  becomes a state of the whole path in three parts. **S-A** — the endpoint is not
  running: S-A.1 the process that served the episode is gone, S-A.2 nothing is
  listening on its port. **S-I** — the ingress in front of it is **terminated, not
  drained**: S-I.1 no Caddy process exists, S-I.2 nothing is listening on `:80` or
  `:443`, TCP and UDP, S-I.3 nothing will bring either back, S-I.4 confirmed from
  off the host that the public name answers from no origin. **S-D** — all of it
  stays down through steps 2 and 3 until the outcome is recorded. Termination
  rather than a reload or a drain is the point: a reload leaves a running process
  deciding what to do with what it already holds, which is what no observation
  available to the operator can establish, and Caddy's grace period is not relied
  upon because S-I.1 reads the absence of the process. **Step 4 gains the
  prevention half**: after a settled miss the §5.4 `handle` block is removed and
  the endpoint returns behind a single-use `/recovery/<nonce>/…` path, the
  retirement is verified from off the host before the GM submits, and the GM
  re-points the module's `submissionEndpoint`. A request held by a hop this host
  cannot terminate then carries an address that no longer reaches the application.
  The confirming query is unchanged and is now described as the detector behind the
  preventer.
- **Alternatives considered:** the reviewer offered two routes, and the maintainer
  ruled for this one. The other — an **application-level mechanism that rejects
  pre-settlement requests after restart**, such as a submission epoch or one-time
  recovery token the endpoint requires — is deterministic and covers hops that
  cannot be terminated, and it stays **deferred, not rejected**, as the Phase 3
  improvement §9 already records. The reasons recorded with the ruling: it adds no
  unreviewed code to the submission path during a gate re-review, where the
  procedural route removes the class of claim the previous two remediations died on
  rather than adding a new one; and it should be designed against Phase 3's
  concurrent server rather than retrofitted to `wsgiref.simple_server`. Stopping
  Caddy was considered and **rejected** by C-15 as too costly; that judgement is
  reversed here, because the narrower stop it preferred does not settle the
  question, so the comparison was never between two settlements. An *actual proxy
  drain* — a reload, or removing the route and reloading — is rejected for the
  reason above: it leaves the process running.
- **Added/removed scope:** §5.4 requires a **terminable ingress** — one proxy, on
  this host, under a supervisor the operator can stop — so that a hop added in
  front of Caddy cannot appear unnoticed. The no-upstream-retry-window requirement
  is **kept and bounded**: it is worth requiring, and it is explicitly no longer
  what makes a miss safe. Route retirement and its verification are added scope for
  the operator, as is stopping and restarting Caddy. No code path, schema or
  credential changes; the recovery route is a temporary Caddyfile change restored
  when the episode closes.
- **Dependency and critical-path effect:** settlement no longer depends on whether
  Caddy fails or holds a request whose dial is refused, nor on what the Cloudflare
  edge does with a request it holds. It newly depends on the ingress being
  terminable from this host. S-A, S-I and S-D are all independent of the endpoint's
  concurrency model, so they hold unchanged for Phase 3's `freedom-web`.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** removes the reachable false miss that survived C-13, C-14 and
  C-15, at the cost of **host-wide downtime** for the duration of a reconciliation:
  Caddy fronts every service on this host, all three Foundry instances among them.
  That is acceptable for a hand-started Phase 2 rehearsal and is the reason the
  Phase 3 improvement is recorded. It also lengthens step 1 to seven recorded
  conditions across two processes plus the database check, which makes the standing
  question of whether **Unsettled** is reachable in practice harder rather than
  easier.
- **Observation, and two corrections it forced.** Caddy's half was exercised on
  2026-08-10 against a real Caddy 2.10.2, on an isolated rig with `admin off` and a
  stub upstream; the production instance was not stopped, reconfigured or reloaded.
  The finding itself was **reproduced**: a request the proxy had accepted with no
  upstream connection made survived the endpoint stop and was answered `201` after
  the restart, and the same episode with the proxy terminated delivered nothing.
  `uri strip_prefix` and the `502` inversion behaved as written. Two things did
  not. **Step 4 expected a `404` from the retired path and gets an empty `200`**:
  deleting a `handle` block produces whatever the rest of the site does with an
  unmatched path, which on these hostnames would be Foundry's answer, so the
  retirement is now the explicit `handle /api/v1/foundry/snapshots { respond 410 }`
  and step 4 checks for `410`. And **S-I.2 can pass while S-I.1 fails**, which §9
  now records with three timings rather than a caution.
- **S-I exercised against the production Caddy, 2026-08-10**, in
  maintainer-authorized windows. With one request held open on the origin's own
  listener — accepted over TLS 1.3, unrouted, the state a lost-pin episode is
  defined by — the listeners closed in **0.5 ms**, the process ended **4.3 s**
  later, and the held connection **closed with nothing delivered**: S-I's core
  claim, on the instance this procedure runs on rather than on a model. With
  nothing in flight the same stop completed in **4 ms**, so **the delay tracks what
  the proxy is holding rather than being a fixed cost**, and a rehearsal on an idle
  host would show the fast case and teach the wrong expectation. The public name
  answered `521` from Cloudflare throughout, on the submission path and the site
  root alike — the edge's own answer, neither Caddy's `502` nor anything the
  application could give — and the unit's `Restart=` is `no`. Production also
  carries a **UDP `:443`** listener, which is what makes S-I.2's UDP check
  necessary here rather than precautionary. Step 4's retirement against production
  remains unobserved: it needs a route that does not currently exist there.
- **Testing effect:** `tests/test_snapshot_recovery_settlement.py` gains two tests
  that are **each other's control**: a real proxy holding a complete request it has
  not dialled upstream for commits it across the restart when only the endpoint is
  stopped — the regression test for the finding — and the same episode with the
  proxy terminated as well ends with the request gone and nothing arriving after
  the restart. ~~Deleting the terminate call from the second makes it fail where
  the proxy forwards, so the control is committed rather than described, which the
  first three remediations could not say.~~ **Corrected by C-19: that mutation had
  not been run and could not have failed as described** — the two tests were
  hand-written copies whose sequences diverged, so the deletion blocked on a
  `join()` before reaching the named assertion. C-19 rebuilds the pair on one
  shared scenario and executes the mutation.
  `tests/test_snapshot_recovery_documentation.py` gains two tests and updates six,
  pinning S-I's four parts, the inverted `502` check, the stated cost, S-D, the
  third withdrawn condition with its defect, §5.4's terminable-ingress requirement
  and bounded retry window, and step 4's retirement, verification and ordering.
- **Migration effect:** none.
- **Security and operational effect:** operational. Recovery still writes nothing:
  every added observation is read-only, and the two requests made through the
  public name are unauthenticated and empty and reach no application. The recovery
  route is a second way in and is therefore single-use, verified, and removed when
  the episode closes; §5.4 says so. Stopping Caddy is maintainer-authorized because
  it takes the site down deliberately.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by Codex when re-reviewing
  C-15's remediation of B-1; the route chosen by the maintainer; implemented by
  Claude. **Carries no independent review**, and returns to the Independent
  Reviewer with the package. B-1 is **not** recorded as closed: the reviewer holds
  it open, and closing it is the reviewer's to do.
- **Acceptance Authority decision:** **none recorded.** The maintainer ruled on the
  route this entry takes; that is not a decision on the entry.

## v1.5 correction C-19 — S-I.3 becomes four checks, the negative control is executed, and every outcome brings the host back

Recorded 2026-08-11 on the **re-review of C-18**, which held finding B-1 open for
the fifth time on one Blocking and two Important findings. **C-18's rule is not
withdrawn** — S-A, S-I, S-D and step 4's route retirement all stand. C-19 supplies
what two of its parts asserted without establishing, and the exit three of its four
outcomes lacked. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-I.3 and S-D), step 3 (the Hit, Ambiguous and Unsettled branches) and
  step 4 (restructured).
- **Reason:** three findings. **(1, Blocking)** S-I.3 — nothing will bring the
  ingress back — was required by the procedure, written as prose with no command to
  run, and evidenced by `systemctl show caddy -p Restart` returning `no`. That
  governs only what the unit does when the process exits on its own; it is silent
  on socket activation, timers, path units, units that pull Caddy in, supervisors
  outside systemd, and a second listener reaching the endpoint's port. The recorded
  evidence could be satisfied in full while ingress was restored underneath the
  operator. **(2, Important)** C-18 claimed its two settlement tests differed in one
  line and that deleting `proxy.terminate()` made the second fail on
  `assert not proxy.dialled`. The tests were hand-written copies whose sequences
  diverged immediately after the endpoint stop, so the deletion blocked at the
  following `proxy.join()` and the named assertion was never reached: **the mutation
  had not been run as described.** **(3, Important)** S-D holds the whole host down
  until step 3's outcome is recorded, and step 4 was "only for a settled miss" — so
  a hit, an ambiguous result and an unsettled episode each ended with no executable
  way to bring Caddy and the endpoint back, and therefore with unbounded downtime
  for every service on the host.
- **Decision:** **S-I.3 becomes four checks with commands.** S-I.3a reads the
  unit's restart surface (`Restart`, `RestartSec`, `TriggeredBy`, `BindsTo`,
  `WatchdogUSec`, `OnFailure`, `DropInPaths`, `UnitFileState`) and the reverse
  dependency tree; S-I.3b reads timers and path units **and the unit behind
  anything listed**; S-I.3c looks for a second way to `127.0.0.1:8757` — listeners
  with process names, proxy and tunnel processes, and Caddy's admin endpoint on
  2019; ~~S-I.3d looks for a supervisor that is not systemd.~~ **Corrected by
  C-20: S-I.3d as written listed names instead of reading jobs** — `ls -la
  /etc/cron.d/` never opened a cron file, `/etc/crontab` and the other users'
  crontabs were not read, and `docker ps -a` said nothing about restart policies.
  It also missed the one container runtime installed on this host. C-20 replaces it
  with a bounded inventory and adds S-D.2, which detects a restart during the window
  rather than arguing that none can happen. **Any of the four that
  comes back positive or cannot be read is Unsettled**, with no weaker fallback, and
  the procedure states that two of the commands need privilege — so an operator
  without `sudo` cannot establish S-I.3c or S-I.3d and must escalate. A reboot is
  named as the one vector that cannot be closed: `UnitFileState=enabled` is expected
  here, and a reboot before the outcome is recorded voids settlement. **The test
  pair is rebuilt on one shared scenario**, `_held_request_episode(…, *,
  terminate_the_proxy)`, in which the flag guards exactly one statement, so the
  claim that termination is the only behavioural variable is a property of the code.
  **Step 4 becomes "bring the path back, on the route the outcome chooses"**, with a
  branch for every outcome: after a miss, the retired route and single-use recovery
  route C-18 introduced; after a hit, a restart on the **unmodified** §5.4
  configuration; after an ambiguous or unsettled episode, a restart with the
  submission path retired and no recovery route. What the outcome decides is what
  answers the submission path afterwards, not whether the service returns.
- **Alternatives considered:** retiring the route on **every** outcome, which is
  simpler to state and was rejected because it is unnecessary after a hit and costs
  the GM the documented endpoint. The asymmetry is argued from the checksum:
  retirement matters only once a fresh export with a **different** checksum has been
  authorized, since only then can a stranded request become a *second* artifact.
  After a hit none is authorized, so the most a stranded request can carry is the
  episode's own bytes, and the uniqueness constraint refuses a second row for them.
  Leaving the hit and unresolved branches to operator judgement was rejected
  outright: an unbounded outage is not a judgement call, and the third finding
  exists because it had been left as one.
- **Added/removed scope:** four recorded checks are added to step 1 and two
  restoration branches to step 4. No code path, schema, credential or Caddyfile
  requirement changes. §5.4 is untouched.
- **Dependency and critical-path effect:** none beyond C-18's. Settlement newly
  depends on the operator being able to *read* four checks, two of which need
  privilege on this host — which is a genuine new way for an episode to end
  Unsettled, and is recorded as such rather than assumed away.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** **reduces** two risks C-18 carried. Ingress can no longer be
  restored by a vector the recorded evidence never looked at, and no outcome leaves
  the host down indefinitely — the maximum downtime becomes the time to reach a
  recorded outcome plus a restart, on every branch rather than one. It **raises**
  the rate at which episodes end Unsettled, which is the intended direction: the
  reviewer's standing question was whether Unsettled is reachable in practice, and
  an operator without `sudo` now reaches it for a readable reason.
- **Observation:** the four S-I.3 checks were run **read-only against this host on
  2026-08-11 with Caddy running**, and are rows 13–16 of
  `docs/review/phase-2-b-1-settlement-observations-2026-08-10.md`. No socket unit,
  no watchdog, no drop-in, no timer or path unit, no second proxy or tunnel, no
  container runtime, and no supervisor outside systemd. **Nothing was stopped,
  started, reloaded or reconfigured; no maintainer-authorized window was used or
  needed.** Two of the commands need privilege that session did not have — root's
  crontab and process attribution for root-owned listeners — and are recorded as
  **unread rather than passed**, which is the first worked example of the Unsettled
  rule this entry adds.
- **Testing effect:** the two `_a_request_held_by_the_proxy_` tests are rebuilt on
  the shared scenario rather than added to, and **the mutation was executed**:
  replacing `proxy.terminate()` with `pass` makes the S-I test fail on
  `assert not episode.proxy.dialled` while its control still passes, and the change
  was then reverted and the suite re-run.
  `tests/test_snapshot_recovery_documentation.py` gains two tests — S-I.3's four
  checks with their commands, the reboot vector and the Unsettled/privilege rule;
  and the three restoration branches with the outcome table, the checksum argument
  and step 3's pointers into them. Full suite: **1888 passed, 208 skipped, 0
  failed.** No JavaScript changed.
- **Migration effect:** none.
- **Security and operational effect:** operational. Every command added to §9 is
  read-only, and the observation behind rows 13–16 changed nothing on the host. The
  hit branch restores the **documented** configuration rather than adding a route;
  the unresolved branch adds a `respond 410` and **no** recovery route, so neither
  creates a new way in. The unresolved branch narrows exposure relative to C-18,
  under which an unresolved episode had no defined configuration to come back on.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer when
  re-reviewing C-18's remediation of B-1; implemented by Claude. **Carries no
  independent review**, and returns to the Independent Reviewer with the package.
  B-1 is **not** recorded as closed: the reviewer holds it open, and closing it is
  the reviewer's to do.
- **Acceptance Authority decision:** **none recorded.**

## v1.5 correction C-20 — S-I.3d becomes a bounded inventory, S-D.2 closes the window from its far end, and the unresolved branch reads the state it is entered in

Recorded 2026-08-11 on the **re-review of C-19**, which held finding B-1 open for
the sixth time on two Blocking findings. **Neither C-18's nor C-19's rule is
withdrawn** — S-A, S-I, S-D, step 4's route retirement and its three restoration
branches all stand. C-20 fixes what two of C-19's parts could not do as written.
**Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-I.3d, and S-D gains S-D.2), step 3 (the Miss and Unsettled
  definitions) and step 4 (the miss and unresolved branches).
- **Reason:** two Blocking findings. **(1)** C-19's S-I.3d claimed to establish
  that no supervisor outside systemd owns either process, and its commands could
  not: `ls -la /etc/cron.d/` lists names and never reads the jobs, `/etc/crontab`
  and the other users' crontabs were not read at all, and `docker ps -a` says
  nothing about restart policies or entrypoints. The reviewer's point was that
  this is the same overclaim C-19 correctly identified for **timer names** one
  check earlier, committed again — and that a scheduled or supervised start after
  the checks but before the outcome is recorded restores §5.4's live route and can
  let an accepted request commit after a miss is declared. **(2)** C-19's
  unresolved branch opened "the host is down now" and told the maintainer to
  restart the endpoint and `start` Caddy. *Unsettled* expressly includes an
  endpoint still serving and a Caddy still running, and the hit branch reclassifies
  to Ambiguous **after** both are already up. Against a running unit
  `systemctl start` is a no-op that reports success, so the amended Caddyfile need
  never load and the live submission route survives the branch that exists to
  retire it; restarting the foreground endpoint against a running one is worse.
- **Decision:** **S-I.3d is rewritten as a bounded inventory that states its
  bound.** It no longer claims a universal negative. It claims that every start
  mechanism [topology §1](../operations/topology.md)'s component table documents was
  **read in full** and starts neither process: container runtimes by presence and
  then by restart policy and entrypoint, `/etc/crontab` and `/etc/cron.d/*` by
  contents, `run-parts --list` per directory, `/var/spool/cron/crontabs/` for who
  actually has one, the crontabs of `root`, `foundry` and `discordbot`, `at`, and
  the per-user systemd managers — followed by a `grep` over the job *contents* for
  `caddy`, `snapshot_api` and `systemctl start|restart`. A user present in the
  spool or in `loginctl` but absent from the topology table is **Unsettled**,
  because the bound has broken. **S-D gains S-D.2**, which is what actually closes
  the reviewer's window: the same readings are taken at both ends of the down
  window and compared — `InvocationID`, `ActiveEnterTimestampMonotonic`, the socket
  list and the journal — and **any difference is Unsettled, not a miss**.
  ~~A start from a mechanism nobody enumerated still mints a new `InvocationID`, so
  the comparison catches what no advance check can.~~ **Corrected by C-21: that is
  true only of a mechanism that starts `caddy.service`.** All four of these
  readings belong to that unit, and the socket list is two samples rather than a
  state, so an ingress that is not Caddy could serve a held request, commit, and
  exit between the two readings leaving every one of them unchanged — the class
  S-I.3d's bound admits it cannot enumerate. C-21 adds the **commit watermark** and
  makes it the reading a miss rests on. **A miss may not be recorded
  without it.** **The unresolved branch reads its entry state**: `systemctl
  is-active caddy`, the listeners and `pgrep`, then `start` when inactive and
  **`reload` when active**, with the rollback copy taken before the edit and
  `caddy validate` before anything loads; the foreground endpoint is left running
  if it is running. The miss branch gets the same copy-and-validate discipline.
- **Alternatives considered:** enumerating more supervisors and calling S-I.3d
  complete, which is what C-19 attempted and is unbounded by construction — there
  is always one more name. Making the inability to enumerate every mechanism an
  Unsettled result *on its own* was rejected as unusable: it makes every episode
  Unsettled, since no operator can enumerate exhaustively. The pairing is what
  works — a bounded inventory to make a mid-episode start rare, and a
  retrospective comparison to establish it did not happen this time.
- **Added/removed scope:** one new settlement condition (S-D.2), one rewritten
  check, and state-reading entry procedures on two step-4 branches. No code path,
  schema, credential or Caddyfile requirement changes. §5.4 is untouched.
- **Dependency and critical-path effect:** none. Settlement newly requires a
  reading taken **before** step 2 and repeated **before** the outcome is written
  down, which is an ordering constraint inside step 1–3 and adds no dependency
  outside §9.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** **reduces** the risk C-19's S-I.3d only appeared to address —
  a restart during the window is now detected rather than argued against. It
  **raises** the Unsettled rate again, and for a newly concrete reason: LXD is
  installed on this host and reading its instances needs privilege this repository's
  sessions do not have.
- **Observation:** the bounded inventory was run **read-only against this host on
  2026-08-11**, rows 17–19 of
  [`../review/phase-2-b-1-settlement-observations-2026-08-10.md`](../review/phase-2-b-1-settlement-observations-2026-08-10.md).
  It immediately found what the old check could not. **LXD is installed** as a
  snap, with `snap.lxd.daemon.unix.socket` listening and
  `snap.lxd.daemon.service` socket-activated; C-19's row 15 ran `docker ps -a` and
  `podman ps -a`, reported "no container runtime" truthfully, and never looked at
  the one runtime that is here. Whether it holds an instance is **unread** —
  `lxc list` needs `root` or the `lxd` group, which has no members — and under §9's
  rule that is Unsettled rather than a pass. Cron was read in full and no job's
  contents reference either process. **Nothing was stopped, started, reloaded or
  reconfigured, and no maintainer-authorized window was used or needed.**
- **Testing effect:** `tests/test_snapshot_recovery_documentation.py` gains two
  tests — S-D.2's comparison with the `NRestarts` caveat, and the unresolved
  branch's entry states with the `start`-is-a-no-op defect — and updates three.
  Full suite re-run below. No JavaScript changed, and no settlement test changed:
  C-19's rebuilt pair is untouched by this entry.
- **Migration effect:** none.
- **Security and operational effect:** operational. Every command added to §9 is
  read-only except the two that were already there — the Caddyfile edit and the
  reload — and both now take a rollback copy first and validate before loading.
  The unresolved branch narrows exposure relative to C-19: under C-19 a running
  Caddy could come out of that branch still serving §5.4's live submission route.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer
  when re-reviewing C-19; implemented by Claude. **Carries no independent review**,
  and returns to the Independent Reviewer with the package. B-1 is **not** recorded
  as closed.
- **Acceptance Authority decision:** **none recorded.**

## v1.5 correction C-21 — S-D.2 reads what a submission commits, not only what `caddy.service` did

Recorded 2026-08-11 on the **re-review of C-20**, which held finding B-1 open for
the seventh time on one Blocking and one Important finding. **No rule in C-18,
C-19 or C-20 is withdrawn** except one sentence of C-20's, struck above. C-21
supplies the reading S-D.2 was missing. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-I.3d's two presence checks, and S-D.2 restructured) and step 3 (the
  Miss and Unsettled definitions).
- **Reason:** two findings. **(1, Blocking)** C-20's S-D.2 claimed to close the
  residual left by S-I.3d's bounded inventory, and detected only Caddy restarts.
  Its persistent readings — `InvocationID`, both timestamps, the journal — belong
  exclusively to `caddy.service`; the listener list is sampled at the two ends of
  the window and is not persistent at all. An unenumerated mechanism that
  transiently starts the endpoint and another listener on the public port, receives
  a request held upstream, commits it, and exits leaves every one of those readings
  unchanged, and the procedure then permitted a miss. C-20's contrary sentence —
  that such a mechanism "still mints a new `InvocationID`" — is **withdrawn as
  false**: it holds only for a mechanism that starts Caddy. C-20's new test
  asserted only that §9 contained the proposed readings, so it could not have
  failed on this case. **(2, Important)** S-I.3d's two presence checks passed
  several names to one `command -v` and derived "no container runtime" / "none
  installed" from its exit status.
- **Decision:** **S-D.2 takes three readings at each end of the down window, and
  the third is what a miss rests on.** The Caddy readings stay, scoped in the text
  to that unit; the listener list stays, named as two samples rather than a state
  and explicitly load-bearing for nothing. Added is the **commit watermark** — row
  counts and newest timestamps over `foundry_snapshots`, and over `audit_events`
  for the `foundry_snapshot` entity — taken at both ends. It reads the
  **destination rather than the route**: an accepted submission commits one
  `snapshot_submission.accepted` event on that entity in the same transaction as
  its snapshot row, a post-authentication refusal commits a
  `snapshot_submission.refused` event on the same entity, and both tables are in
  `APPEND_ONLY_TABLES` with a trigger rejecting `UPDATE`/`DELETE`, so the counts are
  monotone. They move for any acceptance inside the window regardless of which
  process served it, by what route, or whether it still exists at the closing
  reading. **Any difference in any of the three is Unsettled, not a miss**, and
  step 3's Miss and Unsettled branches both name the watermark. ~~§9 also states what
  the watermark cannot do — it says nothing about a commit landing after the closing
  reading, which is what step 4's route retirement and post-recovery query are for~~
  — **corrected by C-22: step 4 covers a commit landing after the *outcome is
  recorded*, and C-21 left the interval between the closing reading and the
  recording closed by ordering alone, which is not closed at all** — and that a
  Council import applied during the window moves it too, correctly. The
  journal is additionally read for the manager (`_PID=1 + _COMM=sudo`), as a
  supporting reading. **Both presence checks become per-name loops** printing
  `present`/`absent` for each candidate, with the conclusion drawn only after all
  are read.
- **Alternatives considered:** extending the enumerated readings to every other
  listener and to the foreground endpoint — rejected, because those are samples by
  construction and the counterexample is precisely a process that exists only
  between two samples. Requiring continuous monitoring of the port for the duration
  of the window — rejected as unrunnable by an operator following a written
  procedure, and it would still not observe an ingress on a port nobody predicted.
  Reading `pg_stat_database`'s commit counter instead of the two tables — rejected
  as too noisy: the Discord bot stays up during the window and commits routinely,
  so every episode would be Unsettled.
- **Added/removed scope:** one new reading inside an existing settlement condition,
  and two rewritten shell checks. No code path, schema, migration, credential,
  Caddyfile or database grant changes; the watermark uses the same read-only access
  step 2's query already requires.
- **Dependency and critical-path effect:** none. The watermark is taken at the two
  points S-D.2 already defined.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** **reduces** the residual C-20 claimed to have closed and had not
  — a false miss caused by an ingress this host was never documented to have. It
  raises the Unsettled rate slightly: any write to the two tables during the window,
  including a legitimate Council import, is now Unsettled.
- **Observation:** run read-only on this host on 2026-08-11. The reviewer's stated
  mechanism for finding (2) does not hold — `bash` 5.2.21 and `dash` both exit `0`
  from `command -v` when **at least one** name is found, so the old line printed
  both LXD paths and no false "no container runtime" — but the finding stands on
  the two grounds recorded in the remediation: POSIX defines `command -v` for one
  operand, so the exit status is shell-dependent, and the aggregated output is what
  let C-20's finding go unnoticed in the first place. The corrected loop names
  `lxc` and `lxd` explicitly. **Nothing was stopped, started, reloaded or
  reconfigured, and no maintainer-authorized window was used or needed.** No
  database was contacted: the watermark's two statements were compiled against the
  real table metadata, not executed.
- **Testing effect:** four tests added. `tests/test_snapshot_recovery_settlement.py`
  gains the **executed counterexample** — a real endpoint and proxy that exist only
  between the two readings, committing a real submission through a request held by
  a hop the operator cannot terminate — and its control, in which the transient
  ingress is never started. The `caddy.service` stand-in mints its `InvocationID`
  from a start, and adding `caddy.start()` to the transient block fails the test,
  which was run and reverted. `tests/test_snapshot_recovery_documentation.py` gains
  a test for S-D.2's coverage of an ingress that is not Caddy, and one binding the
  watermark's columns, entity type and action names to the real schema and audit
  policy so a rename fails rather than silently emptying the query. Full suite:
  **1894 passed, 208 skipped**. No JavaScript changed.
- **Migration effect:** none.
- **Security and operational effect:** operational. Every command C-21 adds is
  read-only, and the watermark needs no privilege step 2's query does not already
  need.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer
  when re-reviewing C-20; implemented by Claude. **Carries no independent review**,
  and returns to the Independent Reviewer with the package. B-1 is **not** recorded
  as closed.
- **Acceptance Authority decision:** **none recorded.**

## v1.5 correction C-22 — S-D.3 holds the decisive reading through the recording of the outcome

Recorded 2026-08-11 on the **re-review of C-21**, which held finding B-1 open for
the eighth time on one Blocking finding and confirmed C-21's discovery-command
correction. **No rule in C-18, C-19, C-20 or C-21 is withdrawn**; C-22 adds the
mechanism C-21's watermark comparison still needed. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-D.2's closing pass, and the new S-D.3), step 3 (the Miss and Unsettled
  definitions) and step 4's settled-miss branch.
- **Reason:** one Blocking finding. C-21's watermark is a comparison of two
  instants, and the outcome is written down **after** the second of them, by hand.
  C-21 answered the interval by ordering — the closing reading was made the last
  act before the record — and that leaves it reachable by exactly the mechanism the
  watermark exists for: every closing reading matches, an unenumerated endpoint and
  proxy start *after* it, a request held in front of this host is delivered and
  commits, both processes exit, and the operator records a miss from figures that
  are already obsolete. That is a **false settled miss**, and it authorizes a fresh
  export whose different checksum uniqueness cannot merge. Holding Caddy and the
  endpoint down does not prevent it, because no part of the sequence is either of
  them. C-21's test stopped the transient ingress **before** taking the closing
  reading, so it established that the watermark catches a commit between its two
  samples and not that the full interval through recording is closed.
- **Decision:** **S-D.3 — the decisive reading is held rather than sampled.** The
  closing watermark and the repeated acceptance-event query are taken inside a
  transaction holding `LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE`,
  and the transaction stays open until the outcome has been written down. `SHARE`
  conflicts with the `ROW EXCLUSIVE` an `INSERT` takes, so while it is held **no
  acceptance and no refusal can commit** — through Caddy or around it, from an
  enumerated mechanism or from one that is not. The reading is therefore a state
  spanning the recording rather than an instant preceding it. §9 states the
  privilege it needs (the schema owner; `SELECT` alone cannot take this lock mode,
  and being unable to take it is Unsettled), sets `lock_timeout` and
  `idle_in_transaction_session_timeout` for the session, requires a `pg_locks`
  confirmation that the lock was still held plus a successful `COMMIT` **after** the
  record, and makes every failure mode — timeout, deadlock, lost session, aborted
  transaction, `held` other than 2 — **Unsettled, not a miss**. Step 3's Miss states
  the ordering as load-bearing and its Unsettled branch names S-D.3's failures.
  What S-D.3 does not cover is stated: a commit landing after the `COMMIT` is a
  later commit, not a false miss, and that is the residual step 4's route
  retirement prevents and its post-recovery query detects. ~~The two divide the
  timeline with no gap.~~ — **struck by C-23 as false.** They do not: a writer
  that arrived while the lock was held is *queued*, not absent, and it commits the
  instant the lock is released — before step 4 runs, and past every address the
  retirement can take away. C-23's S-D.4 is what closes it.
- **Alternatives considered:** **retiring the §5.4 submission route before the
  decisive read** — the reviewer's first suggestion, and rejected as the mechanism
  because it closes the interval only for requests arriving through Caddy, while
  the counterexample is specifically an endpoint and a proxy that are not Caddy at
  all; the retirement stays where it is, answering what a hop in front of this host
  can deliver afterwards. **A third watermark sample taken immediately before the
  record** — rejected explicitly, and named in §9 so it cannot return as a
  simplification: it moves the interval and leaves it there. **Revoking the runtime
  role's `INSERT` on the two tables for the duration** — rejected as a durable
  privilege change made under incident conditions, with a restore step that must not
  be forgotten, where a transaction-scoped lock releases itself. **Writing the miss
  into the database in the same transaction as the check** — the reviewer's second
  suggestion, and rejected because the operational record is not a domain table and
  `audit_events` is not the place to record an operator's conclusion; the lock
  obtains the same guarantee without inventing a schema for it.
- **Added/removed scope:** one new settlement condition (S-D.3) inside step 1's
  S-D, with ordering requirements in step 3 and one clarifying sentence in step 4's
  miss branch. No code path, schema, migration, credential or Caddyfile change.
- **Dependency and critical-path effect:** none.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** **reduces** the residual C-21 left — a miss recorded from a
  reading that was already obsolete. It adds one **operational** cost, stated in
  §9: while the lock is held, every insert into `audit_events` platform-wide waits,
  including the Discord bot's, which is why the transaction contains the readings
  and nothing else. It raises the Unsettled rate slightly again: a write in flight
  against either table when the lock is requested now ends the episode as Unsettled
  rather than being read past.
- **Observation:** **no database was contacted.** The lock mode's conflict with
  `ROW EXCLUSIVE`, the privilege this lock mode requires, and the `pg_locks`
  predicate are taken from PostgreSQL's documented behaviour, not from a run
  against this host. **S-D.2 and S-D.3 as a whole remain unrehearsed**, and nothing
  was stopped, started, reloaded or reconfigured.
- **Testing effect:** two tests added to
  `tests/test_snapshot_recovery_settlement.py` and one to
  `tests/test_snapshot_recovery_documentation.py`, with two documentation
  assertions updated to the rewritten text.
  `test_a_commit_after_the_closing_reading_is_a_false_miss_without_the_settlement_lock`
  is the **executed counterexample**: the same transient ingress as C-21's, run
  after the closing reading, leaving all three readings identical at both ends and
  the recorded miss false anyway.
  `test_the_settlement_lock_holds_the_window_shut_until_the_outcome_is_recorded` is
  its control, and the two are one episode differing in one flag (**C-23 renames
  that control to
  `test_a_writer_queued_behind_the_settlement_lock_is_a_false_miss_without_the_drain_read`
  and inverts what it establishes**). **Mutation run:**
  removing the `acquire()` fails the control on "the commit did not wait for the
  settlement lock"; reverted and re-run. Full suite: **1897 passed, 208 skipped.**
  No JavaScript changed.
- **Migration effect:** none.
- **Security and operational effect:** operational, and larger than C-21's. S-D.3
  needs the **schema owner** rather than the read-only account step 2 uses, and it
  briefly blocks inserts into two tables platform-wide. Both are stated in the
  procedure with the reason and the bound.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer
  when re-reviewing C-21; implemented by Claude. **Carries no independent review**,
  and returns to the Independent Reviewer with the package. B-1 is **not** recorded
  as closed.
- **Acceptance Authority decision:** **none recorded.**

## v1.5 correction C-23 — S-D.4 reads the queue behind the lock, and confirms the miss after it is released

Recorded 2026-08-11 on the **re-review of C-22**, which held finding B-1 open for
the ninth time on one Blocking finding and raised one Important. **Both are
accepted in full.** No rule in C-18 to C-21 is withdrawn; **one sentence of C-22's
is struck as false** (the "no gap" claim, struck in place above), and one of its
session settings is replaced. **Proposed; not yet ruled.**

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §9 "Lost-pin reconciliation"
  step 1 (S-D.3's session settings and queue reading, and the new S-D.4), step 3
  (the Miss and Unsettled definitions), step 4's settled-miss branch (the
  "detection is not prevention" paragraph), and "what settlement rests on".
- **Reason, Blocking:** **C-22's lock delays the race; it does not close it.**
  `SHARE` conflicts with `ROW EXCLUSIVE`, so a conflicting `INSERT` arriving while
  the lock is held does not fail and does not disappear — it **waits**, inside
  PostgreSQL. The procedure recorded the miss and authorized a fresh export while
  that writer was queued, and on `COMMIT` the waiting submission committed at once,
  **before** step 4 retired the route. Route retirement cannot reach a transaction
  that has already been accepted and is inside the database: there is no address
  left to take away from it. C-22's own control test demonstrated the defect and
  read it as the successful case.
- **Reason, Important:** **`SET idle_in_transaction_session_timeout = 0` removed
  the only bound on a platform-wide pause.** The settlement transaction blocks every
  audit insert on the platform; an operator called away mid-recording could hold
  them indefinitely.
- **Decision:** **S-D.4 — a shut door is not an empty one.** Two readings are
  added, and the authorization of a fresh export is separated from the recording of
  the miss. (a) **The queue is read inside the lock** — ungranted relation-lock
  requests by another backend on either table — with the decisive reading and again
  as the last statement before the `COMMIT`; **any row is Unsettled**, because a
  waiting `RowExclusiveLock` is a postponed commit and not an absent one. (b) **The
  miss is confirmed by a drain read after the lock is released**: the same lock is
  taken a second time in the same session, which PostgreSQL grants only behind the
  requests already queued, and the watermark is read inside it. A figure that has
  moved **retracts the miss** and the episode becomes Unsettled; only a matching
  drain read authorizes a fresh export. The Important finding is taken by setting
  `idle_in_transaction_session_timeout` to **`'10min'`** — a bound exceeding the
  recording window, with expiry classified as Unsettled — and `0` is named in §9 as
  what must not be used.
- **A correction found by running it.** The queue reading is over **`pg_locks`
  alone**. The obvious form joins `pg_stat_activity` to name the waiting session,
  and inside S-D.3's long-lived transaction that form is wrong: `pg_locks` is read
  live from the lock manager, but a backend-status snapshot is taken at the first
  `pg_stat_activity` read in a transaction and reused for the rest of it, so the
  second queue reading answers from the state at the first — and the writer that
  matters connected after it. §9 keeps the join only as a follow-up that names the
  sessions, preceded by `pg_stat_clear_snapshot()`. **This was found by executing
  the procedure against a real PostgreSQL, not by reading it**, and it is the
  reason the reviewer's request for a real concurrency test is taken as written.
- **Alternatives considered:** **cancelling or terminating queued writers**
  (`pg_terminate_backend`) before the `COMMIT` — rejected: it destroys a submission
  the platform may have accepted legitimately, under incident conditions, on the
  operator's judgement, and it does not remove the interval either. **Holding the
  lock until after step 4's retirement** — rejected: it extends a platform-wide
  pause across a Caddy edit, a validate and two restarts, and the retirement still
  cannot reach a transaction already inside the database. **Reading the queue and
  treating it as advisory** — rejected: an advisory reading of a delayed commit is
  the defect. **Leaving `idle_in_transaction_session_timeout` at `0` and relying on
  the operator** — rejected as the safeguard the finding is about.
- **Added/removed scope:** one new settlement condition (S-D.4) inside step 1's
  S-D, two session-setting and query corrections inside S-D.3, ordering
  requirements in step 3, and a corrected paragraph in step 4's miss branch. **No
  code path, schema, migration, credential, Caddyfile or database grant changes.**
- **Dependency and critical-path effect:** none.
- **Estimate/forecast and capacity effect:** none.
- **Risk effect:** **reduces** the residual C-22 left open and had claimed to have
  closed — a miss that was true when recorded and false by the time it was acted
  on. It **reduces** an operational risk as well: the platform-wide pause is now
  bounded rather than unbounded. It raises the Unsettled rate again: an episode
  with any writer queued behind the lock now reaches no conclusion.
- **Observation:** **a database was contacted for the first time in these
  remediations** — the disposable `freedom_test` database over the Unix-domain
  socket, through the existing declared fixtures. Nothing on production was read,
  stopped, started, reloaded or reconfigured; no `LOCK TABLE` was run against
  `freedom`. **S-D.2, S-D.3 and S-D.4 remain unrehearsed as an operator procedure**;
  what is now established is the PostgreSQL behaviour they rest on.
- **Testing effect:** one test added and one renamed and inverted in
  `tests/test_snapshot_recovery_settlement.py`; one test added to
  `tests/test_snapshot_recovery_documentation.py` with five assertions updated to
  rewritten text; and a new file,
  `tests/test_snapshot_settlement_postgresql.py`, of **five tests against real
  PostgreSQL**, in the declared database-backed set. Together they establish that
  the lock blocks the real submission service rather than refusing it, that the
  blocked backend appears as an ungranted `RowExclusiveLock` in §9's own query,
  that it commits the instant the lock is released, that a second `LOCK TABLE` is
  granted only behind it, that the joined form of the queue reading misses it, and
  that a bounded idle timeout ends the pause and the episode. **Mutations run:**
  removing the queue registration in the fake lock fails the queued-writer test;
  restoring the `pg_stat_activity` join to the decisive reading fails two of the
  PostgreSQL tests; removing `pg_stat_clear_snapshot()` fails the staleness test.
  Each was reverted and re-run. Full suite: **1899 passed, 213 skipped**, and
  **2112 passed, 0 skipped** with `TEST_DATABASE_URL` configured. No JavaScript
  changed.
- **Migration effect:** none.
- **Security and operational effect:** operational. The platform-wide pause S-D.3
  introduced is now bounded by `idle_in_transaction_session_timeout`, and the extra
  readings are two `pg_locks` queries and one additional short lock acquisition.
  No privilege change: S-D.4 runs in the same schema-owner session as S-D.3.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer
  when re-reviewing C-22; implemented by Claude. **Carries no independent review**,
  and returns to the Independent Reviewer with the package. B-1 is **not** recorded
  as closed.
- **Acceptance Authority decision:** **none recorded.**
- **Struck by C-24 on 2026-08-12.** S-D.4 did not close the window; it moved the
  race into the drain transaction. A request that had been accepted and had not
  yet issued its first conflicting statement was queued behind nothing, appeared
  in no `pg_locks` reading, and committed after the drain read matched and the
  miss had authorized a fresh export. The claims that "a shut door is not an
  empty one, and what is queued behind it is visible" settles the question, and
  that S-D.3 and S-D.4 together cover "what was already through the door and
  waiting", are **false as closure claims** and are struck. The mechanism behaves
  as C-23 described; the description of what that mechanism established does not
  hold. S-D.3 and S-D.4 are withdrawn entirely by C-24.

## v1.5 correction C-24 — the admission fence replaces settlement-by-observation

Recorded 2026-08-12 on the **re-review of C-23**, which held finding B-1 open for
the tenth time on one Blocking finding. **It is accepted in full.**

**This entry withdraws C-23's closure claim rather than adding to it.** C-23
recorded that S-D.4 "closes" the window S-D.3 left, that "a shut door is not an
empty one, and what is queued behind it is visible", and that S-D.3 and S-D.4
together "cover everything up to the instant the miss is written down" and "what
was already through the door and waiting". **Those claims are false and are
struck.** They are true of the mechanism and false of the problem: a request that
had been accepted and had not yet issued its first conflicting statement was
queued behind nothing, appeared in no `pg_locks` reading, moved no watermark, and
committed when it woke. C-23 moved the race into the drain transaction; it did
not close it. The same is now recorded of every earlier condition — C-13 through
C-22 — not as a further weakening but because **all of them share one defect**,
stated below.

- **Affected requirements:**
  `docs/operations/foundry-snapshot-submission.md` §5.2 (a credential also needs
  an admission generation), §5.3 (revocation reaches only unauthenticated
  requests), §5.4 (the ingress no longer has to be terminable), §7 Rehearsal A
  step 10 (no host-wide downtime), and §9 "Lost-pin reconciliation" steps 1 to 4
  and "what settlement rests on" — rewritten rather than amended. Plan §12 Phase 2
  package 2.4 (PostgreSQL concurrency/recovery evidence). New schema:
  `submission_admissions` and `idempotency_keys.admission_id`, migration 0005.
- **Reason, Blocking:** **no observation can settle this question, and nine
  remediations were nine observations.** A process table, a listening socket,
  `pg_stat_activity`, a restart-vector inventory, a commit watermark, a `pg_locks`
  queue reading and a drain read are all observations of a *resource*, and an
  observation of a resource cannot exclude work that has been **accepted** and has
  not yet reached it. The defeating sequence is the same every time: the old
  request pauses before its first statement, settlement reads clean, the miss is
  recorded, a fresh export with a new checksum is authorized, and the old request
  then wakes and commits. Route retirement cannot reach it — it is already inside
  PostgreSQL, past every address that could be taken away — and the post-recovery
  query detects the duplicate only after the Council has two pending artifacts.
- **Alternatives considered and rejected:**
  - *Another lock.* A lock delays a request; it does not revoke its authority. Any
    lock-and-read scheme recreates the same last-read-to-commit interval
    somewhere. Rejected as the whole answer, though a lock is used *inside* the
    answer to serialize a closure against an acceptance.
  - *A composite foreign key on `(admission_id, state)`.* `ON UPDATE
    RESTRICT`/`NO ACTION` makes closure fail forever, because every historical
    accepted row still references `(id, 'open')`; `ON UPDATE CASCADE` rewrites
    history and fences nothing. Rejected.
  - *A `SECURITY DEFINER` trigger taking `SELECT … FOR KEY SHARE`.* Workable, and
    heavier than the foreign key already present for provenance, which takes the
    same lock for free and cannot be forgotten by a new write path. Rejected as
    redundant.
  - *An in-flight record written before processing and cleared after it.* The
    shape the previous version of §9 named as a Phase 3 obligation. It settles an
    episode without a stop, but it is still an observation — a request that has
    not begun has written no in-flight record — so it has the same defect.
    Rejected.
- **Decision:** **a durable admission fence at the acceptance boundary.**
  `submission_admissions` holds one row per submitting credential: a generation, a
  state that moves `open` → `closed` **once**, and the operator, reason and time of
  each transition. `principal_id` is unique **for all time**, so a closed
  generation can never be succeeded by an open one for the same credential;
  `open` → `closed` is enforced by a trigger that also refuses `DELETE`, for the
  schema owner too. Every submission transaction resolves the admission of **the
  principal id in its own `Authorization` header** — never "whichever generation is
  open now", which would silently upgrade a request paused before that lookup —
  and re-reads its state as the last statement before the commit. The acceptance's
  `idempotency_keys.admission_id` foreign key takes a `KEY SHARE` lock on the
  admission row, which conflicts with the `FOR UPDATE` a closure takes, so a
  closure and an acceptance can never interleave in either direction. A shared
  advisory lock covers the paths that write nothing, so a same-key replay cannot
  return a successful receipt across a closure either.

  Settlement is then `tools.submission_admission close`. **Nothing is stopped.**
  Recovery issues a new credential under a new principal id (§5.2) and opens a new
  generation naming it; the old request cannot present it.
- **Added scope:** one table, one column, one migration (0005) with a data
  backfill; one operator tool (`tools/submission_admission.py`); one application
  module (`application/admissions.py`); one repository on the unit of work; one
  refusal code (`admission_closed`, HTTP `403`); two audit actions
  (`snapshot_submission.admission_opened` / `.admission_closed`) and one new key
  (`admission_generation`) on the accepted and refused payloads.
- **Removed scope:** the whole of S-A, S-I (including S-I.1 to S-I.4 and the
  S-I.3a–d restart-vector inventory), S-D.2's watermark comparison, S-D.3's
  `LOCK TABLE … IN SHARE MODE` and its session settings, and S-D.4's queue and
  drain readings. The mandatory route retirement in step 4 is demoted to optional
  hygiene. §5.4's "the ingress must be terminable" requirement is demoted to good
  practice. **Host-wide downtime during a reconciliation is removed entirely.**
- **Dependency and critical-path effect:** the Phase 3 obligation the previous
  §9 recorded — "add the mechanism that lets recovery settle an episode without a
  stop … a pre-settlement barrier the restarted application refuses requests
  against" — is **discharged by this correction** rather than carried into Phase 3.
  B-1 and the Phase 2 gate remain open pending independent re-review.
- **Estimate/forecast and capacity effect:** no change to the Phase 2 forecast,
  which §12 already records as requiring re-estimation. This is the tenth
  remediation of one finding and the first to change the mechanism rather than the
  reading.
- **New or changed risks:**
  - **R-new-1 — a deployment that opens no generation accepts nothing.** After
    migration 0005 the endpoint answers `403 admission_closed` until an operator
    runs `tools.submission_admission open`. Fail-closed by design; it is a
    deployment step with a documented command (§5.2), and it is named as a
    maintainer decision below.
  - **R-new-2 — a closure blocks all submissions until a new generation is
    opened.** Deliberate: an unresolved episode should leave submission closed.
    The cost is that an operator who closes a generation and walks away leaves an
    endpoint that accepts nothing, with no automatic recovery.
  - **R-new-3 — a closure written without `FOR UPDATE` would fence nothing.** A
    plain `UPDATE` of a non-key column takes `FOR NO KEY UPDATE`, which does not
    conflict with the foreign key's `KEY SHARE`. Measured on this host and held by
    a named regression test, because it reads exactly like a working fence.
  - **R-retired:** every risk arising from host-wide downtime during a
    reconciliation, and every risk arising from a hop in front of Caddy that
    cannot be terminated.
- **Testing effect:** new `tests/test_submission_admission_postgresql.py` — 17
  tests against a real PostgreSQL using the real `SnapshotSubmissionService` over
  `SqlAlchemyUnitOfWork`, with `threading.Event` rendezvous and no sleeps. It
  holds the **paused-before-first-statement regression** the review asked for, the
  two other pause boundaries (after the admission read, and at the final commit
  boundary), both lock orderings, same-key retries on both sides of a closure, the
  recovery generation, a deployment with no generation at all, duplicate and
  abandoned settlement, audit-write failure, process restart, and the measured
  PostgreSQL lock behaviour including the `FOR NO KEY UPDATE` trap.
  `tests/test_runtime_grants_live.py` gains the least-privilege evidence: the
  runtime role holds `SELECT` on `submission_admissions` and is refused `INSERT`,
  `UPDATE`, `DELETE`, `TRUNCATE` and `FOR UPDATE` with SQLSTATE 42501, while
  `pg_advisory_xact_lock_shared` needs no grant.
  `tests/test_snapshot_recovery_documentation.py` is rewritten to assert the new
  procedure and to assert that each withdrawn condition stays withdrawn.
  `tests/test_snapshot_recovery_settlement.py` and
  `tests/test_snapshot_settlement_postgresql.py` are retained and reframed as the
  record of **why** the withdrawn conditions failed, not as tests of a live
  procedure.

  **Mutations run**, each reverted and re-run green (baseline 17 passed):
  removing the transactional admission check fails **9** tests including
  `test_a_request_paused_before_its_first_statement_is_refused_once_the_generation_closes`;
  letting an old request inherit whichever generation is open fails
  `test_the_old_credential_cannot_use_the_new_generation`; moving the check into
  its own transaction before the acceptance fails the two pause-boundary tests;
  removing the foreign key fails
  `test_a_foreign_key_insert_and_a_for_update_closure_cannot_interleave`; removing
  the lock that serializes closure against acceptance fails
  `test_a_closure_cannot_commit_while_a_submission_transaction_is_open`.

  Full suite: **1917 passed, 232 skipped**, and **2149 passed, 0 skipped** with
  `TEST_DATABASE_URL` configured. `foundry-module` JavaScript: one line, adding
  `admission_closed` to `SERVER_REFUSAL_CODES`; its `403` already routes to
  `DEFINITIVE_REFUSAL`, so no retry logic changed.
- **Migration effect:** **migration 0005**, additive and reversible.
  `upgrade → downgrade → upgrade` exercised against the disposable `freedom_test`
  database. It creates `submission_admissions` with its trigger, adds
  `idempotency_keys.admission_id` with a `RESTRICT` foreign key, backfills
  pre-fence receipts to a **closed** generation 0 under the reserved principal
  `<pre-admission-fence>` (not a legal `ServicePrincipal` id, so nothing can ever
  authenticate as it), and then adds the check constraint requiring a submission
  receipt to name an admission. The backfill is two SQL statements that read
  nothing in Python, so `alembic upgrade --sql` still emits a complete script.
  **Downgrade discards which generation each acceptance was written under, and
  removes the fence**; a deployment left downgraded is in the pre-C-24 state that
  B-1 is open against. Take a backup first, and re-upgrade before serving.
  Backup/restore: the new table is ordinary data captured by the existing
  `pg_dump` drill; a restore to a point before the closure restores an **open**
  generation, so an operator restoring across an episode must re-close it and
  record that they did.
- **Security and operational effect:** the runtime role gains `SELECT` on one new
  table and gains nothing else; it cannot open, close, reopen or delete an
  admission, which is what keeps the fence enforced rather than advisory. No new
  credential material and no change to authentication. A refusal is typed, carries
  no exception text, and is rendered as `403 admission_closed`; `403` rather than
  `409` or `503` deliberately, so no client treats it as retryable. Operationally
  this is a large **reduction**: a reconciliation costs one transaction instead of
  a host-wide outage that also took the three Foundry sites down.
- **Product/Data/Operations Owner recommendation:** **not yet given.**
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer
  when re-reviewing C-23; designed and implemented by Claude. **Carries no
  independent review**, and returns to the Independent Reviewer with the package.
  **B-1 is not recorded as closed and the Phase 2 gate remains open.**
- **Maintainer decisions required, stated here rather than left in documentation
  wording:**
  1. **Fail-closed deployment.** Migration 0005 leaves the endpoint refusing every
     submission until `tools.submission_admission open` is run. Confirm that is
     the wanted behaviour, or direct that the migration open a generation for the
     currently configured principal.
  2. **Closure blocks all submission until a new credential is issued.** Confirm
     that recovery may require issuing a new credential to the submitting GM, and
     that a principal id is spent once its generation closes.
  3. **Removal of the downtime requirement from §9.** Confirm that settling a
     lost-pin episode no longer stops the endpoint or Caddy, and that the
     terminable-ingress requirement in §5.4 is demoted to good practice.
- **Acceptance Authority decision:** **none recorded.**

### C-24 finishing pass — bounded implementation and operational corrections

Recorded 2026-08-12, after C-24's implementation was reviewed. **The admission
design above is retained in full and nothing in it is withdrawn.** Four defects
were found in the implementation and its operator surface, none of them in the
fence itself, and each is corrected here. This is an amendment to C-24, not a new
correction of the settlement rule.

1. **The documented operator commands could not run.** The runbook showed
   `DATABASE_URL='postgresql+psycopg:///freedom'`, while `DatabaseSettings`
   validates the database name against `APP_ENVIRONMENT` and defaults that to
   `development` — so the settlement command, copied from the page, refused with
   exit code 2 before settlement began. Every documented invocation now names
   `APP_ENVIRONMENT` and the environment's real database
   (`freedom_production`/`freedom_staging`/`freedom_dev`), and connects as the
   **schema owner** placeholder `__OWNER_ROLE__` rather than the restricted
   runtime login role, which by design cannot open or close a generation. No real
   role name, password or connection string is written into documentation or
   tests. `DatabaseSettings` is unchanged: the refusal was correct and was not
   weakened to make an example pass. `tests/test_submission_admission_tool.py`
   parses the runbook itself and drives every documented invocation through
   `build_engine`, which is the whole configuration path the tool takes before
   connecting.
2. **The admission row's correlation columns identified nothing.** The row took
   `gen_random_uuid()` for `correlation_id` and `closed_correlation_id` while
   `_audit()` minted a separate UUID, so the columns could not find the
   append-only events they exist to name. One identifier is now minted per
   *transition* and written to both records in the same transaction. A second
   close of an already-closed generation still writes no event and no second
   identifier, because it is not a transition. Proved by PostgreSQL-backed tests
   that join `submission_admissions` to `audit_events` on each column.
3. **Expected operator-tool failures escaped as tracebacks.** A `lock_timeout` is
   a documented **Unsettled** outcome, and it — along with connection failure,
   insufficient privilege and other database errors — reached the operator as a
   stack trace. The CLI now has seven documented exit codes (0 success, 1 refused,
   2 unusable target, 3 unreachable, 4 privilege, 5 `lock_timeout`/Unsettled,
   6 other database failure). No failure message carries a traceback, a
   connection string, a credential or SQL — `str()` of a SQLAlchemy `DBAPIError`
   appends the statement and its parameters, so no message is built from it — and
   **no non-zero exit can accompany a claim that a generation was closed**, since
   every branch is reached with the transaction rolled back. The handler catches
   `DBAPIError`, not `Exception`, so a defect in the tool keeps its traceback
   instead of being dressed up as an operational refusal.
4. **The transaction-isolation assumption is now enforced rather than assumed.**
   The submission's re-read before its commit is a *fresh* reading only under
   `READ COMMITTED`; the unit of work inherited whatever
   `default_transaction_isolation` the database or login role carried. **Measured
   before changing anything**, on this host's PostgreSQL 16.14, using the
   decisive interleaving — a closure holding the exclusive advisory lock while the
   submission's first statement takes its snapshot and then blocks, with the
   closure committing before it wakes:

   | Isolation level | Outcome | SQLSTATE |
   |---|---|---|
   | `READ COMMITTED` | typed `admission_closed` refusal | — |
   | `REPEATABLE READ` | PostgreSQL aborts the transaction at the foreign key's `KEY SHARE` lock | **40001** |
   | `SERIALIZABLE` | same | **40001** |

   **No level produced a durable post-closure acceptance**, so the non-default
   levels fail closed. This is recorded as **hardening evidence, not a new B-1
   failure.** What they lose is the *typed* refusal the runbook tells operators to
   expect: the caller gets a generic `PersistenceError` that an operator cannot
   tell from a database fault. `SqlAlchemyUnitOfWork` therefore pins
   `READ COMMITTED` on its own transaction — the local contract, not the cluster,
   the database or the role, and PostgreSQL's own default, so nothing changes on a
   cluster nobody has reconfigured.

- **Added scope:** `tests/test_submission_admission_tool.py` (45 tests: the
  documented-command shape, failure classification, correlation joins and the CLI
  outcomes against a real PostgreSQL); five isolation regressions in
  `tests/test_submission_admission_postgresql.py`, including one against a
  genuine `ALTER DATABASE … SET default_transaction_isolation` with a control
  proving the hostile default was established;
  `TranslatingSession.begin_at_isolation_level`;
  `UNIT_OF_WORK_ISOLATION_LEVEL`; the tool's exit codes and
  `classify_database_failure`. **Removed scope: none.**
- **Migration effect: none.** Migration 0005 is unchanged and was already
  unapplied outside the disposable database. `upgrade 0005 → downgrade 0004 →
  upgrade head` was re-rehearsed against `freedom_test`.
- **Security and operational effect:** operator output is now audited for
  credential, URL and SQL leakage by test rather than by reading. The runtime
  role's inability to settle an episode is now demonstrated at the CLI, using the
  real grants template, rather than only as a table-privilege assertion. No new
  credential material, no new privilege, no change to authentication.
- **Testing effect:** full suite **1952 passed, 247 skipped**, and **2199 passed,
  0 skipped** with `TEST_DATABASE_URL` configured (1917/232 and 2149 before this
  pass). `foundry-module` JavaScript unchanged: 155 pass. `upgrade 0005 →
  downgrade 0004 → upgrade head` re-rehearsed against the disposable database,
  and `alembic check` reports no new upgrade operations. Mutations run and
  reverted, each failing a named regression: restoring the old runbook URL fails
  the documented-invocation tests; returning the correlation columns to
  `gen_random_uuid()` fails the three join tests; removing the CLI's `DBAPIError`
  handler fails all four CLI outcome tests; removing the isolation pin fails
  every isolation test, the interleaving ones with the recorded SQLSTATE 40001.
- **Product/Data/Operations Owner recommendation:** **not yet given.** C-24's
  three maintainer decisions are unchanged and still outstanding.
- **Technical Lead and specialist reviews:** implemented by Claude. **Carries no
  independent review.** **B-1 is not closed and the Phase 2 gate remains open**;
  this pass returns the existing design for independent re-review and approves
  nothing.
- **Acceptance Authority decision:** **none recorded.**

### C-24-R — independent-review remediation of the admission fence

Recorded 2026-08-12, after the C-24 submission-admission fence was independently
reviewed. **The durable admission design above is retained in full and nothing in
it is withdrawn.** Two findings were returned — one Blocking, one Important —
and both are corrected here. This is an amendment to C-24, not a new correction
of the settlement rule.

1. **Blocking — a uniqueness-conflict replay bypassed the fence.** The ordinary
   same-key replay inside `_store_and_record()` was fenced: shared advisory lock
   first, then the admission of the authenticated principal, then a requirement
   that it be open, then a requirement that the stored receipt's `admission_id`
   match it. The **uniqueness-conflict recovery path was not.** When
   `_store_and_record()` lost an `idempotency_key.scope_key` race, `_persist()`
   called `_replay_stored()`, which opened a fresh transaction, read the winning
   receipt and returned it — taking no advisory lock, resolving no admission,
   requiring no open generation, and never checking which generation had earned
   the receipt.

   The counterexample: two requests authenticated as principal P enter with the
   same key and bytes while P's generation N is open; the winner commits its
   accepted receipt under N; the loser meets the uniqueness violation and its
   transaction is rolled back, **releasing the shared lock**; settlement closes N
   and commits, delayed by nothing; and the loser then returns the winner's
   successful receipt after the closure. **No post-closure write is needed for
   this to violate the invariant** — returning or reusing a successful receipt is
   forbidden as squarely as writing a row, because the module treats it as a
   submission that succeeded while the operator has already recorded the episode
   as settled and may have authorized a fresh export.

   **The remediation is consolidation, not a second check.** A local `if closed`
   in the recovery branch would have left every successful-receipt path
   independently responsible for remembering the invariant, which is the shape
   that produced the defect. Instead `_replay_stored()` is deleted, and both ways
   of discovering that a key is already spent — the ordinary retry, which finds
   the row before the store runs, and the race, which finds out after — reach one
   principal-bound operation, `SnapshotSubmissionService._fenced_replay`. In one
   transaction it takes the shared side of the fence lock **before reading any
   receipt**, resolves the admission of the principal id the request itself
   authenticated as, requires that admission to remain open, requires the stored
   record's `admission_id` to equal it, and only then applies the request-digest
   check `_replay()` has always made. `_store_and_record()` no longer replays at
   all: it raises a private `_RequestKeyAlreadySpent` signal that never leaves
   `_persist()`. The authenticated `ServicePrincipal` is passed through recovery;
   no authorization is recovered from the stored record, from a globally current
   generation, or from caller-controlled data.

   `_persist()`'s nested `try` is replaced by one bounded loop with a single
   `_store_and_record` call site, so each conflict rule is examined in one arm
   rather than two. Semantics are otherwise unchanged: same key and same bytes
   under the earning generation returns the original receipt; same key and
   different bytes is `request_key_conflict`; a key earned by another admission
   refuses; no admission or a closed one is `admission_closed`; an unreadable or
   missing race winner fails closed as `concurrent_submission`. The cost is one
   extra read-only transaction on the ordinary retry path.

2. **Important — an absent SQLSTATE does not prove no commit.**
   `tools/submission_admission.py` classified every `DBAPIError` without a
   SQLSTATE as an inability to connect, and said, for `close`, that no generation
   was closed and the fence was unchanged. **That conclusion is not sound.** A
   connection can be lost while PostgreSQL is processing or acknowledging
   `COMMIT`; the server may have committed while the client receives only a
   driver error, and client observation alone cannot distinguish the two — the
   same lesson the fence itself rests on, arriving at the operator surface.

   The phase is now **recorded rather than inferred**. `CommandProgress` is
   marked inside the `with engine.begin()` block of `open` and `close`, and a
   SQLSTATE-less failure is classified by that mark: unmarked is exit 3 and it is
   sound to say nothing was written; marked is **exit 7 — Outcome unknown /
   Unsettled**, which claims nothing in either direction, never says the fence is
   unchanged or that the transition did not commit, directs the operator to
   reconnect and run `show` and to confirm the transition through the admission
   row's correlation columns against its append-only audit event, and states that
   `close` is idempotent once verified while an ambiguous `open` must be verified
   before another principal or generation is attempted. It carries no traceback,
   URL, credential, parameter or SQL. Failures during an ordinary statement, where
   no `COMMIT` was ever sent, are deliberately reported as unknown as well:
   separating them would mean trusting the client's own account of how far it got,
   which is precisely what a lost connection makes unreliable. False uncertainty
   costs one `show`; a false assertion that settlement did not occur costs a
   duplicate accepted export. The `DBAPIError`-only handler is unchanged, so a
   defect in the tool still keeps its traceback.

- **Affected requirements:** `docs/operations/foundry-snapshot-submission.md`
  §5.2's exit-code table, new §5.2.1 (the ambiguous outcome and its verification),
  and §9's Unsettled rule, whose claim that "if it is not 0, nothing was closed"
  is corrected. No change to the settlement rule, the invariant, or the schema.
- **Added scope:** `SnapshotSubmissionService._fenced_replay` and the private
  `_RequestKeyAlreadySpent` signal; `CommandProgress`, `EXIT_OUTCOME_UNKNOWN`,
  `TRANSITIONS` and `_outcome_unknown` in the operator tool. **Removed scope:**
  `SnapshotSubmissionService._replay_stored`, and the duplicated admission check
  that lived inside `_store_and_record`'s replay branch.
- **Reason and alternatives considered:**
  - *A local `if closed` in the recovery branch.* Rejected by the finding itself:
    it leaves each returning path responsible for the invariant, and the next
    branch will forget it exactly as this one did.
  - *Removing the spent-key pre-check from `_store_and_record` and letting every
    retry fall through the uniqueness race.* One boundary, and simpler — but a
    same-key retry with different bytes would then write its artifact to disk
    before being refused, which today it never does. Rejected as a behaviour
    change the finding did not ask for.
  - *A three-state commit-phase model in the CLI* (`before` / `in a statement` /
    `at the commit`), claiming "did not commit" for the middle state. Available
    in principle, since statements run inside the block and the commit runs as it
    exits. Rejected: the claim would rest on the client's account of its own
    progress, and the conservative direction was directed by the finding.
- **Dependency and critical-path effect:** none. B-1 and the Phase 2 gate remain
  open, and this package returns to the Independent Reviewer.
- **Estimate/forecast and capacity effect:** no change.
- **New or changed risks:**
  - **R-new-4 — exit code 7 is a new operator outcome that must be verified
    rather than acted on.** An operator who treats it as "closed" may authorize a
    fresh export against an open generation; one who treats it as "not closed"
    may re-close harmlessly but must not conclude the episode is unsettled
    without looking. §5.2.1 is the procedure, and the message itself carries it.
  - **R-retired:** the false assurance that a SQLSTATE-less failure proved the
    fence unchanged, and the unfenced successful-receipt path.
- **Testing effect:** 21 new tests. `tests/test_submission_admission_postgresql.py`
  gains the five-step race reproduced against a real PostgreSQL using the real
  service over `SqlAlchemyUnitOfWork`, with `threading.Event` rendezvous and no
  sleeps, plus its control without the closure; the harness gains a gate after
  the idempotency lookup and a gate at unit-of-work creation, the latter chosen
  so that a mutant which replays without taking the lock still stops there and
  can be shown to answer successfully after a closure rather than merely hanging.
  `tests/test_snapshot_submission.py` gains five application tests covering both
  callers of the consolidated boundary and two syntax-tree tests: a
  `SubmissionReceipt` is constructed in exactly two production places
  (`_store_and_record` and `_replay`), `SubmissionReceipt.from_payload` is called
  only from `_replay`, `_replay` is called only from `_fenced_replay`, and that
  boundary's first statement is the fence lock.
  `tests/test_submission_admission_tool.py` gains eight classification tests and
  four injected-fault tests covering the four points the review named — before
  the connection is established (through the real driver, an unreachable socket
  directory), during a statement before commit, at the commit acknowledgement,
  and after a genuinely committed close with the documented verification run end
  to end. The acknowledgement fault uses a narrow double at the transaction
  boundary: **the transaction commits for real against the real database** and
  the error replaces the reply the client never hears. What is simulated is the
  loss of the reply, not any behaviour of PostgreSQL, and nothing here is offered
  as evidence about PostgreSQL internals.

  **Mutations run**, each reverted and re-run green: restoring the unfenced
  `_replay_stored()` fails **four** tests, decisively
  `test_a_request_that_loses_the_key_race_cannot_replay_across_a_closure`, which
  then receives a successful receipt after the closure instead of a typed
  refusal, and `test_no_stored_receipt_is_returned_outside_the_one_fenced_boundary`,
  which names the reintroduced caller; restoring `sqlstate is None => definitely
  nothing committed` fails **nine** CLI tests, decisively
  `test_a_lost_commit_acknowledgement_never_claims_the_fence_is_unchanged`.

  Full suite: **1967 passed, 253 skipped**, and **2220 passed, 0 skipped** with
  `TEST_DATABASE_URL` configured (1952/247 and 2199 before this pass).
  `foundry-module` JavaScript unchanged: 155 pass. `alembic check` reports no new
  upgrade operations.
- **Migration effect: none.** Migration 0005 is unchanged and its schema contract
  is untouched, so no rehearsal was required or performed for this pass.
- **Security and operational effect:** the fence now covers every path that can
  return a successful submission receipt, which is a strengthening rather than a
  relaxation; no privilege, credential, authentication or audit-policy change.
  Operationally there is one new documented exit code and one new verification
  procedure. Deployment carries no new step: the change is application and
  operator-tool code, and a deployment that skipped it would be in the reviewed
  state the Blocking finding is open against.
- **Product/Data/Operations Owner recommendation:** **not yet given.** C-24's
  three maintainer decisions are unchanged and still outstanding.
- **Technical Lead and specialist reviews:** raised by the Independent Reviewer
  when reviewing C-24; remediated by Claude. **Carries no independent review.**
  **C-24 is not closed, B-1 is not closed, and the Phase 2 gate remains open**;
  this pass returns the design and its evidence for independent re-review and
  approves nothing.
- **Acceptance Authority decision:** **none recorded.**

### C-24-R independent re-review and Phase 2 gate decision

Recorded 2026-08-12. Codex independently re-reviewed the two C-24-R findings
and returned **no findings**, recommending that C-24 and B-1 close and that the
Phase 2 data-integrity, identity and migration-safety gate be accepted. Review
record: `docs/review/phase-2-c-24-independent-re-review-2026-08-12.md`.

- **Product/Data/Operations Owner recommendation and Acceptance Authority
  decision:** **accepted by Peter Duscha on 2026-08-12**, through the instruction
  "I accept. Let's commit and go on to Phase 3."
- **Gate effect:** C-24 and B-1 are closed. Phase 2 is accepted. Phase 3
  readiness planning is released.
- **Scope effect:** no implementation, schema, authority or release scope is
  changed by this record. Phase 3 remains subject to its separate
  definition-of-ready inputs, including OD-16, OD-17, accepted visual direction,
  named owners, accepted frontend contracts and security-review capacity.
- **Evidence:** focused PostgreSQL suite 146 passed; full suite 1967 passed and
  253 skipped; `git diff --check` clean; `compileall` passed.

### Phase 3 §12.1 visual acceptance and project reconciliation

Recorded 2026-08-13. After staged Gemini implementation and repeated Codex
source review, Peter Duscha accepted visual-refinement Step 5 and directed Codex
to reconcile the project before any further implementation.

- **Affected requirement and milestone:** implementation-plan §12.1 visual
  direction and the readiness inputs for numbered Phase 3. This closes the
  separate visual/accessibility gate only; it does not accept or begin numbered
  Phase 3 production implementation.
- **Reason and alternatives:** the accepted visual source was frozen, while the
  status/RAID records still described Phase 2 and visual acceptance as open and
  the proposed Claude document authorized only contrast tooling. Proceeding
  directly to backend implementation was rejected in favour of a clean,
  reviewable baseline and accurate controlled records.
- **Scope:** commits the static seven-page prototype, local synthetic portraits,
  small dependency-free portrait-preview JavaScript, documentation and a
  14-file SHA-256 freeze manifest. It reconciles current status and dependencies.
  It adds no FastAPI, OAuth, session, authorization, production Jinja, database,
  Caddy, Foundry, Sheet or deployment implementation.
- **Dependency and critical-path effect:** closes the visual half of D-03.
  Stable accepted backend route/view-model contracts remain open and block
  Gemini production integration. Phase 3 remains not ready until its separately
  estimated packages satisfy the management definition of ready.
- **Estimate, forecast and capacity effect:** no calendar forecast is committed.
  Claude remains proposed backend implementer, Gemini frontend implementer and
  Codex independent/security-focused reviewer resource; accountable human roles,
  environment availability, three-point estimates and review/remediation
  contingency must be recorded in the Phase 3 delivery plan.
- **Risk effect:** R-04 remains active until server-side authorization is
  implemented and reviewed. No production security boundary changes here.
  Static-source contrast evidence does not replace browser, screen-reader or
  production accessibility testing.
- **Testing and evidence:** Peter visually accepted desktop and real-mobile
  behaviour. On 2026-08-13 Codex ran `check_css_tokens.py` (71 defined, 62
  referenced, zero undefined), `calc_contrast.py --test` (11 passed), the
  complete contrast matrix (49 pairs: 48 pass, one disabled-state exemption,
  zero failures), the 14-file freeze manifest (all OK), JavaScript syntax check
  and `git diff --check` (both clean). Reconciliation removed one trailing
  blank from the new portrait-preview JavaScript, with no token or rendered
  behaviour change, and updated its manifest hash before the final verification.
  These checks are accurately classified as repository-local/static evidence.
- **Migration, deployment and rollback:** no migration or deployment. Git is the
  baseline and rollback mechanism; the freeze manifest detects visual-source
  drift. The public static preview is not the production portal.
- **Review and acceptance:** Gemini implemented the visual work; Codex performed
  independent source reviews and this reconciliation. Peter Duscha is the
  Product Owner and visual gate authority and accepted Step 5 on 2026-08-13.
  Authentication/security work still requires the separate reviews and
  Acceptance Authority decision defined by the plan.
- **Superseded handoff:**
  `docs/review/phase-3-contrast-evidence-remediation-claude-prompt.md` is retained
  as planning history but was superseded without execution after current tooling
  passed. It must not be used as a production backend prompt.

### Phase 3 delivery-plan readiness submission

Recorded 2026-08-13. Codex prepared
`docs/review/phase-3-delivery-plan.md` at Peter Duscha's instruction. This is a
readiness submission, not an accepted baseline and not implementation.

- **Affected milestone:** numbered Phase 3 only. Phases 0–2 and the §12.1
  visual gate remain unchanged.
- **Scope and decomposition:** proposes P3.0 contract/security design, P3.1
  authentication foundation, P3.2 member reads/identity reconciliation/access
  administration, P3.3 Council import/durable jobs/audit, P3.4 Gemini production
  integration and P3.5 gate evidence, with a stop gate after each package.
- **Estimate and capacity effect:** initially re-estimated focused effort at
  22/38/60 days, then revised to **26/44/70 days** after Peter required
  Discord-independent administrator recovery and future provider portability.
  optimistic/likely/pessimistic, medium-low overall confidence, including
  explicit review/remediation contingency. It withdraws reliance on the early
  10–18-day rough-order range for forecasting; no calendar commitment is made.
- **Migration effect:** explicitly includes Phase 3's controlled migration-
  register allocation for `Characters C` and `Players A/B/D` as identity
  evidence. It requires Council-reviewed snowflake links, control totals,
  unresolved records, idempotency and recovery; no mutable name or Sheet flag
  grants authorization and Google Sheets is not mutated.
- **Identity and recovery clarification:** Peter requires Server Administrator
  access when Discord is unavailable and a credible route to a replacement
  login provider if Discord is retired. The proposed plan therefore introduces
  stable internal platform accounts, external provider identities, narrow
  WebAuthn/passkey break-glass authentication and a host-local single-use
  recovery grant. It deliberately does not add a permanent local password or
  pre-approve an ordinary-member replacement provider. P3.G0 must accept the
  ADR/schema/migration and privilege boundaries before implementation.
- **Security and operational effect:** proposes numeric session, role-cache,
  OAuth, CSRF, rate-limit, request, pagination, polling, job-lease, retention and
  CSP contracts. None becomes authoritative before Peter accepts it. It requires
  disposable PostgreSQL before P3.1 and deployed staging before P3.5.
- **Risk effect:** adds proposed Phase 3 risks R-19–R-27 for the web security
  boundary, Discord availability, durable jobs, contract drift, accessibility,
  co-located-host capacity, environment separation, emergency-access backdoors
  and provider-migration account takeover/lockout.
- **Implementation/deployment/migration effect:** none. Plan acceptance releases
  P3.0 design/contract work only; P3.1 remains behind P3.G0, Gemini remains
  behind accepted backend contracts, and production deployment remains behind
  Phase 3 and deployment gates.
- **Review:** prepared by Codex as planning work. The future Codex implementation
  and security reviews remain independent because Codex implements no production
  package here. Peter reviewed the plan and clarified that authentication must
  remain modular while the provider-independent security core protects the
  internet-exposed host.
- **Acceptance Authority decision:** **Accepted by Peter Duscha on 2026-08-13.**
  This accepts the P3.0–P3.5 boundaries, roles, 26/44/70-day estimate, numeric
  security policies, provider-neutral/break-glass contract and environment
  rules. Authentication providers are replaceable adapters; authorization,
  sessions, CSRF, host/origin checks, rate limits, request/concurrency bounds,
  audit and safe failure remain provider-independent controls. Acceptance
  releases P3.0 design work only. P3.1 remains blocked behind P3.G0.

### Phase 3 P3.0 contract and security design submission

Recorded 2026-08-13. Claude, as working Technical Lead, produced the P3.0
package under `docs/contracts/` plus proposed ADR 0010. This is a design
submission, not an accepted contract and not implementation.

- **Affected milestone:** numbered Phase 3, package P3.0 only. Phases 0–2 and the
  §12.1 visual gate are unchanged.
- **Scope delivered:** route/authorization contract with a closed route set and
  seven-role matrices; versioned view-model contract `vm-1`; logical schema and
  schema decision table; staged identity-migration contract; six state machines;
  threat model with 53 threats and 12 residual risks; dependency, configuration
  and operational contracts; expanded acceptance/test traceability; and a single
  numeric-policy register.
- **Implementation effect: none.** No route, dependency, migration, framework
  scaffold, service, template or runtime module was added. No service was started,
  no deployment performed, no production data or secret accessed.
- **Material proposals requiring the Acceptance Authority's decision at P3.G0:**
  (1) a separate `freedom-worker` systemd service, because the measured
  9.566-second preview is GIL-holding work that would stall `freedom-web`;
  (2) route-level restriction of break-glass sessions to identity/capability
  administration and audit reads (N-65), tighter than the accepted §7 boundary;
  (3) treating the Council **apply** as a durable job for the same measured reason
  as the preview; (4) the P3.0-proposed numeric values N-30…N-66; and
  (5) proposed ADR 0010.
- **Migration effect:** designs, but does not write, a four-stage reversible
  migration off Discord-keyed authorization. It establishes that append-only
  history is **never rewritten** — historical attribution resolves through
  `external_identities` — because rewriting it would require suspending the
  migration-0005 trigger the Phase 2 gate accepted.
- **Security effect:** validates the accepted CSP against the Discord redirect and
  concludes it can stand **unweakened**; settles the cross-process rate-limiter
  storage §7 left open; and records break-glass, provider-portability and
  co-located-host residual risks with named owners.
- **Risk effect:** substantiates proposed risks R-19–R-27 with design and tests;
  adds R-28 (unmeasured real-folder apply duration and worker peak memory).
- **Evidence honesty:** two quantities remain unmeasured and are labelled as such
  (real-folder apply duration; worker peak memory). Staging does not exist, the
  OD-25 firewall question is open, and assistive-technology evidence is not yet
  scheduled. None is claimed as satisfied.
- **Review:** prepared by Claude. **Codex independent architecture/security review
  is requested and has not occurred.**
- **Acceptance Authority decision:** **Not yet decided.** Recorded for Peter
  Duscha at stop gate P3.G0. P3.1 remains blocked; Gemini production integration
  remains blocked.

### Phase 3 P3.G0 remediation decision

Recorded and accepted by Peter Duscha on 2026-08-13 after Codex independent
architecture/security review.

- **D-1 approved:** add the separate `freedom-worker` process in the later P3.3
  implementation package.
- **D-2 approved:** Council apply is a durable job; its retry machine remains a
  blocking remediation item.
- **D-3 conditionally approved:** keep the tighter break-glass route boundary,
  but prevent a break-glass session from creating any mapping that can confer
  Council, character or import authority after ordinary-provider login.
- **D-4 partly/provisionally approved:** N-30–N-42 and N-44–N-66 are accepted as
  proposed starting values subject to their named later evidence. N-43 is
  withheld pending a coherent atomic attempt-exhaustion transition and re-review.
- **D-5 conditionally approved:** ADR 0010's direction is accepted. Final ADR
  acceptance requires account-aware audit attribution and correction of the
  break-glass escalation path.
- **Review disposition:** remediation required. The four findings are account
  attribution versus the legacy audit constraint; indirect Council escalation
  through role mappings; the stranded third job attempt; and contradictory PKCE
  verifier storage. P3.G0 remains open and P3.1/Gemini production integration
  remain unauthorized until remediation and independent re-review.

### Phase 3 P3.0 remediation submitted for re-review

Prepared by Claude on 2026-08-13 from
`docs/review/phase-3-p3-0-remediation-claude-prompt.md`, after Peter Duscha's
P3.G0 remediation decision of the same date. **Submitted, not accepted.**

- **Affected requirement/milestone/release:** implementation plan §12 Phase 3;
  delivery plan §7, §8, §9; milestone P3.0; gate P3.G0. No release effect.
- **Reason:** the four findings recorded in the P3.G0 remediation decision —
  account attribution versus the legacy audit constraint, indirect Council
  escalation from break-glass, unreachable job attempt exhaustion, and the PKCE
  verifier contradiction.
- **Scope added:** one route (R-38, ratification of an emergency-created
  role-capability mapping); one numeric policy (N-67, the administrator-continuity
  allowlist); one state machine (SM-07, mapping provenance); one caller state
  (`AC`, bound to the `BG` matrix column by rule and by test); mapping provenance,
  scope and ratification columns on `role_capability_mappings`; and the
  `audit_events` constraint swap. Scope removed: none. Test TC-BG-05 is
  **withdrawn** as wrong and replaced by five tests.
- **Alternatives considered and rejected:** giving the emergency administrator a
  placeholder Discord id to satisfy the legacy constraint (it would put a lie in
  the audit trail); a bare capability allowlist without provenance (a
  break-glass session would still reach Council through two hops); raising the job
  attempt cap instead of moving the terminal transition (the stranding is a state
  machine defect, not a budget defect).
- **Implementation effect: none.** No route, dependency, migration, framework
  scaffold, service, template or runtime module was added. Nothing was deployed or
  started; no production data or secret was accessed.
- **Migration effect:** stage A of the identity migration now **replaces**
  `ck_audit_events_human_action_has_an_actor` with an account-aware constraint by
  explicit DDL, adding the wider rule `NOT VALID` before dropping the narrower one.
  History is still never rewritten, and no row is read, updated or deleted:
  `ADD COLUMN`, `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are catalogue
  operations for which row triggers never fire. `snapshot_imports` gains a new
  `NOT VALID` attribution check; `foundry_snapshots` gains none, because a
  supervised-bootstrap row that names no human is legitimate. Two new control
  totals (T7, T8) and nine named PostgreSQL tests cover it. A correction of record:
  the append-only trigger is from **migration 0002**, not 0005, as the earlier P3.0
  documents said.
- **Security effect:** the break-glass boundary is closed against a two-session
  escalation it did not previously cover, by three independent controls — an
  application allowlist, a check constraint that depends on what is written rather
  than on who is writing, and the N-65 route surface — plus provenance, so the
  restriction cannot be shed by logging in through Discord. Threat T-10b is new.
  PKCE verifier storage is stated identically in every contract.
- **Estimate/forecast and capacity effect:** none. The remediation is documentation
  and design within P3.0's existing allowance; P3.1's likely range is unchanged.
- **New or changed risks:** R-26 widened; R-29 added (a design defect found only at
  implementation); residual risks RR-13 (emergency persistence) and RR-14 (terminal
  verdict written by the reaper) added to the threat model.
- **Testing effect:** TC-BG-05 withdrawn; TC-BG-05a…05e, TC-BG-15, TC-AUTH-12,
  TC-AUD-09…14, TC-MIG-14…16, TC-CAP-08…11, TC-JOB-15 and TC-JOB-16 added;
  TC-JOB-05 and TC-JOB-13 rewritten against the corrected N-43. **No test in the
  package has been written or run**; they remain a specification.
- **Operational effect:** three monitoring signals added (oldest expired lease,
  unratified emergency mappings, mapping refusals by code) with matching recovery
  procedures. No topology, perimeter or worker conclusion changed.
- **Numeric policy effect:** N-43 corrected and no longer withheld-as-defined;
  N-65's **subject widened** from a break-glass session to any continuity-scoped
  session, with its value and surface unchanged; N-67 new. Every other
  provisionally accepted value is preserved unchanged.
- **Review:** prepared by Claude. **Codex independent architecture and distinct
  security re-review is requested and has not occurred.**
- **Acceptance Authority decision:** **Not yet decided.** P3.G0 remains open, ADR
  0010 remains conditionally accepted, and P3.1 and Gemini production integration
  remain unauthorized.

### Phase 3 P3.G0 final acceptance and P3.1 authorization

Recorded by Peter Duscha on 2026-08-13 after Codex independent architecture and
distinct security-focused re-review of the P3.0 remediation.

- **Decision:** accept the complete remediated P3.0 route/view-model, schema,
  state-machine, numeric, migration, configuration, operational, threat and test
  contracts; accept ADR 0010; close P3.G0.
- **Additional accepted items:** corrected N-43, widened N-65, new N-67, mapping
  provenance and ratification route R-38. N-43's 225-second figure is explicitly
  a live-reaper lease-expiry-recovery bound, excluding queue wait, successful
  execution time and N-45's separate runtime cap.
- **Scope and authority effect:** no product scope or release boundary changes.
  The accepted contracts define implementation authority; they do not claim that
  prospective migrations, routes or PostgreSQL tests already exist.
- **Risk decision:** accept RR-13, the deliberate persistence of
  continuity-scoped administrator authority needed for recovery. It cannot reach
  Council, character or import authority before full-scope ratification.
- **Evidence decision:** P3.0's documentation checks remain valid only as design
  evidence. No database evidence is inherited. P3.1 must implement and execute
  its named tests against guarded disposable PostgreSQL.
- **Authorization:** Claude may begin P3.1 after confirming the delivery plan's
  disposable-PostgreSQL prerequisite. Gemini production integration remains
  blocked behind its later contract/freeze gate. P3.G1 remains the next stop
  gate and requires Codex independent review plus a distinct security pass.
- **Approval:** **Accepted by Peter Duscha on 2026-08-13.**

## C-P3.1 — Phase 3 P3.1 authentication and security foundation implemented

**Date:** 2026-08-14 · **Recorded by:** Claude (Working Technical Lead) ·
**Status:** *Submitted for review. Not accepted. P3.G1 is open.*

- **Affected requirement, milestone and release:** implementation plan §12
  Phase 3; delivery plan §5 package P3.1. No release boundary moves.
- **Reason:** execution of `docs/review/phase-3-p3-1-claude-prompt.md`, under the
  authority Peter Duscha recorded when he closed P3.G0 on 2026-08-13.
- **Environment prerequisite:** confirmed 2026-08-14 before any migration ran.
  `freedom_test` was proven through the repository's own guards — statically by
  `assert_disposable_target` under `UNIX_SOCKET_ONLY`, and live by
  `verify_connected_unix_socket_target`, which reported
  `current_database() = 'freedom_test'` with both `inet_server_addr()` and
  `inet_client_addr()` null. No credential was recorded.
- **Added scope:** a separate `freedom-web` virtualenv and an eleven-package
  bounded dependency set; typed web configuration with the fifteen startup
  refusals; Alembic revisions `0006`, `0007` and `0008` (identity stages A, B and
  C, including the `audit_events` constraint swap and the protected
  role-capability mapping); the OAuth, session, break-glass, capability and
  role-mapping services; the web security middleware and ten routes; four
  host-local operator commands; minimal contract templates; and
  `docs/operations/web-portal.md`.
- **Removed scope:** none.
- **Deliberately not delivered:** P3.2's administration UI and its routes
  (R-20…R-38), P3.3's worker, job system and audit views, Gemini production
  integration, any deployment, Caddy change, OAuth-provider registration or
  production database access. Migration stage D is not in this package and
  remains a separate later decision.
- **Dependency and critical-path effect:** P3.G1 replaces the environment
  prerequisite as the critical-path item. P3.2 remains blocked behind it.
- **Estimate and capacity effect:** none recorded; the P3.1 range in delivery
  plan §6 is not rebaselined by this entry.
- **New or changed risks:** A-02 re-confirmed; A-05 gains its mechanism but
  remains unvalidated because no credential has been enrolled on any host; A-07
  and I-06 are new — the three declared contract deviations, and the
  staging-class evidence that cannot be produced because staging does not exist.
- **Testing effect:** 2250 tests pass under the bot virtualenv and 197 under the
  web virtualenv, both against guarded disposable PostgreSQL with **no skips**.
  Every staging-, browser-, real-device- and assistive-technology-class check in
  the traceability contract is reported as unrun rather than as passing.
- **Migration effect:** three reversible revisions, each round-tripped against
  real PostgreSQL. Stage A checks control totals T1–T8 inside its own
  transaction and aborts on disagreement. **No historical row is read, updated or
  deleted**, and the migration-0002 append-only trigger is neither dropped,
  disabled nor evaded. A downgrade of `0006` discards the attribution of audit
  events written by a break-glass session after the upgrade; that consequence is
  stated in the revision docstring and in the operations document.
- **Security effect:** the `audit_events` attribution rule is **replaced**, not
  relaxed — its subject widened from *a Discord user* to *an identified person* —
  which is what makes an emergency login recordable, and therefore possible, during
  a Discord outage. `application/audit.py`'s copy of the rule moved in the same
  revision. The N-67 allowlist is enforced by three independent controls, one of
  which does not depend on the session at all.
- **Operational effect:** a second systemd-managed process will be required at
  deployment; none is created here. The kill switch, session revocation,
  credential enrolment and recovery-grant commands are host-local and documented.
- **Product Owner recommendation:** proceed to P3.G1 review.
- **Technical Lead and specialist reviews:** **not yet performed.** Codex
  independent implementation review and a separately reported security-focused
  pass are requested.
- **Acceptance Authority decision:** **not recorded. P3.G1 remains open.**

## C-P3.1-R — Phase 3 P3.1 remediation after Codex independent and security review

**Date:** 2026-08-14 · **Recorded by:** Claude (Working Technical Lead) ·
**Status:** *Submitted for re-review. Not accepted. P3.G1 is open. Two findings
are blocked on maintainer decisions.*

This entry **supersedes two claims** in entry C-P3.1 above. That entry is not
edited; it remains the record of what was submitted on 2026-08-14 before review.

- **Affected requirement, milestone and release:** implementation plan §12
  Phase 3; delivery plan §5 package P3.1. No release boundary moves.
- **Reason:** execution of `docs/review/Handover information` — Codex's
  independent implementation review and distinct security-focused review of P3.1,
  which returned three blocking findings and one important finding.
- **Alternatives considered:** for finding 1, implementing SM-01 literally by
  holding a transaction open across the Discord call, and consuming the
  transaction after provider verification — both rejected in the decision note,
  the first because it violates the accepted no-transaction-across-provider-I/O
  invariant and would convert a Discord slowdown into a portal outage on the
  five-connection pool, the second because it breaks schema §9.2.1's single-
  statement recovery-and-erasure and reopens the replay window TC-AUTH-12 closes.
  For finding 3, a P3.1 contract-test route harness and a package/gate reordering
  — both rejected as, respectively, evidence about a harness rather than the
  platform, and a larger restructuring than the finding warrants.
- **Corrections to entry C-P3.1:**
  1. *"**No historical row is read, updated or deleted**"* is **false as
     written**. Migration 0006 **reads** `discord_users` for the backfill and
     **updates** `character_access` with account attribution. The append-only
     half of the claim is correct: `audit_events`, `snapshot_imports` and
     `foundry_snapshots` are not rewritten, the catalogue-only DDL does not fire
     the migration-0002 row trigger, and the `xmin` evidence proves the
     specifically seeded append-only rows were not rewritten — not that the
     migration read or wrote no historical data anywhere. **Migration 0006 was
     not altered**; the prose was corrected to match it.
  2. *"197 [portal tests] … with **no skips**"* stands, but the traceability it
     supported overstated two rows: TC-AUTH-11 was claimed complete while five
     terminal OAuth callback refusals wrote no audit event, and TC-BG-05a…05e
     were claimed collectively "implemented, passing" while the direct-HTTP
     portions of 05b, 05c and 05e are unrun.
- **Added scope:** `application/web/refusals.py`, a single refusal-recording
  boundary that writes exactly one `auth.login.refused` event per terminal
  callback refusal with the caller's correlation id, a closed non-secret reason
  vocabulary and no secret or attacker-controlled value; guarded provider payload
  readers in `adapters/web/discord_provider.py` so malformed provider data
  becomes a classified refusal rather than an unhandled `500`; and 72 new tests.
- **Removed scope:** none.
- **Deliberately not delivered:** the fix for finding 1, and the contract change
  for finding 3. Both change accepted contracts, no approval exists in the
  repository record, and both are returned as decision notes rather than chosen
  silently. **No P3.2 route was added, no migration was added or edited, and no
  document under `docs/contracts/` or `docs/adr/` was edited.**
- **Dependency and critical-path effect:** P3.G1 remains the critical-path item
  and now additionally depends on two maintainer decisions, registered as RAID
  issues **I-07** and **I-08**. P3.2 remains blocked.
- **Estimate and capacity effect:** none recorded.
- **New or changed risks:** I-07 and I-08 are new and blocking. A-05, A-07 and
  I-06 are unchanged.
- **Testing effect:** the portal suite rises from 197 to **269 tests**, all
  passing with no skips against guarded disposable PostgreSQL; the bot suite from
  2251 to **2252**, the single addition being an existing repository-wide guard
  automatically covering the new module. Three mutations were run and reverted,
  restoring the pre-remediation early return for the provider-outage,
  missing-cookie and rate-limited branches; each was killed by named tests.
- **Migration effect:** **none.** No migration was added, edited or removed;
  `alembic check` reports no new upgrade operations. The `upgrade → downgrade →
  upgrade` round trip was re-run against `freedom_test` and reaches head `0008`.
- **Security effect:** every terminal login refusal is now recorded. Previously an
  attacker probing the callback with a forged cookie, a spent transaction or
  during a provider outage left no trace distinguishable from an attempt that
  never happened. A refusal that cannot be audited fails closed to a safe error
  and never to a session. No blanket exception handler was introduced.
- **Operational effect:** refusal audit volume rises, bounded by the same N-18
  limit that already bounded the attempts. `docs/operations/web-portal.md` gains
  §3.2a, naming exactly which existing rows migration 0006 reads and writes.
- **Product Owner recommendation:** decide I-07 and I-08, then complete the
  finding-1 implementation and the finding-3 contract update before P3.G1.
- **Technical Lead and specialist reviews:** **not yet performed.** Codex
  independent implementation review and a separately reported security-focused
  pass are requested over
  `docs/review/phase-3-p3-1-remediation-submission.md` §13.
- **Acceptance Authority decision:** **not recorded. P3.G1 remains open.**

## C-P3.1-D — Phase 3 P3.1 findings I-07 and I-08 ruled

**Date:** 2026-08-14 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Accepted decisions; P3.G1
remains open.*

- **Affected requirement, milestone and release:** SM-01, logical schema
  §9.1–§9.2, threat/test traceability, Phase 3 delivery-plan gates P3.G1/P3.G2.
  No release boundary changes.
- **Reason:** the accepted same-transaction completion mechanism contradicted
  the no-transaction-across-provider-I/O invariant, and three TC-BG-05 HTTP
  portions targeted P3.2 routes that do not exist before P3.G1.
- **Decision I-07 / OD-44:** approve durable one-way OAuth completion binding.
  `sessions.oauth_transaction_id` is the sole authoritative, unique relationship;
  it is required for Discord OAuth. `completion_claimed_at`, session creation and
  success audit commit atomically after provider I/O. No reverse transaction-to-
  session FK is added. Migration 0009 and named PostgreSQL/re-review evidence are
  required.
- **Decision I-08 / OD-45:** retain service and constraint evidence at P3.G1;
  allocate the direct-HTTP portions of TC-BG-05b/c/e to P3.2 as mandatory P3.G2
  evidence against real routes. No test-only route or early P3.2 work is
  authorized, and no evidence is waived.
- **Alternatives rejected:** a database transaction spanning Discord I/O;
  consume-after-provider verification; an unclaimed re-read; a redundant cyclic
  reverse FK; a test-only HTTP harness; and package/gate merger.
- **Scope effect:** one P3.1 migration and focused OAuth/service/repository/tests
  are authorized. No P3.2 implementation is added to P3.1.
- **Dependency/critical-path effect:** I-08 no longer blocks P3.G1. OD-44
  implementation and independent plus distinct security re-review still block
  P3.G1. The HTTP portions become explicit P3.G2 blockers.
- **Estimate/capacity effect:** no forecast change is recorded; the Technical
  Lead must report actual remediation effect in the next submission.
- **Risk, testing, migration, security and operations effect:** the completion
  binding becomes database-enforced without consuming a pool connection during
  provider I/O. Revision 0009 must be reversible and must document rollback;
  PostgreSQL constraint, concurrency, failure and mutation evidence is required.
  HTTP authorization evidence is delayed only until its production handlers
  exist and remains mandatory before their gate closes.
- **Recommendations:** Technical Lead recommendation accepted with the single-FK
  refinement; Security Reviewer accepts that refinement. Independent re-review
  remains prospective after implementation.
- **Approval:** **Accepted by Peter Duscha on 2026-08-14. P3.G1 is not closed.**

## C-P3.1-E — Phase 3 P3.1 OD-44 completion binding implemented and resubmitted

**Date:** 2026-08-14 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for Codex independent
implementation re-review and a distinct security-focused pass. Not accepted.
P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** the OD-44 ruling recorded in
  C-P3.1-D; SM-01; logical schema §9.1–§9.2; the threat model; the test
  traceability contract; `docs/operations/web-portal.md`. Phase 3 P3.1 only. No
  release boundary changes.
- **Reason:** C-P3.1-D authorized the remediation and required implementation
  plus evidence before P3.G1 could be considered again.
- **What was implemented:** new reversible Alembic revision `0009`; revisions
  0006–0008 were **not** edited. `oauth_transactions.completion_claimed_at` and
  `sessions.oauth_transaction_id` with a `RESTRICT` foreign key, a unique index
  and the `discord_oauth`-equivalence check constraint.
  `OAuthLoginService.complete()` now takes the transaction id and atomically
  claims the completion as the first statement of the provider-I/O-free
  transaction that also creates the bound session and writes the success audit;
  zero matched rows is a typed, safely audited refusal
  (`completion_not_claimable`) and never a session. R-04 remains orchestration
  only.
- **One declared reading of the ruling:** the unique index is scoped
  `WHERE rotated_from_session_id IS NULL`. Transcribed literally, the ruled
  table-wide `UNIQUE` and the ruled check constraint are jointly unsatisfiable
  with N-08 privilege rotation, which mints a second session row for the same
  login. Both stated purposes of the ruling survive the scoping; the alternative
  would have silently disabled rotation for the platform's main authentication
  method. Recorded for the Acceptance Authority's confirmation.
- **Alternatives rejected:** relaxing the check constraint for rotated rows
  (would permit an unbound `discord_oauth` session); bounding the claim by
  `expires_at` (would refuse a legitimate login whose provider round trip
  crossed N-04); and a reverse `oauth_transactions.session_id`, which the ruling
  had already rejected.
- **Scope effect:** none beyond the authorized remediation. No P3.2 route was
  added, no HTTP evidence was waived, and OD-45's allocation is unchanged.
- **Dependency/critical-path effect:** OD-44 implementation no longer blocks
  P3.G1; the Codex independent implementation re-review and the distinct
  security-focused pass do.
- **Estimate/capacity effect:** the remediation was completed within the same
  working day as the ruling. No forecast change is recorded.
- **Risk, testing, migration, security and operations effect:** 30 new portal
  tests (TC-AUTH-13) and 4 new migration tests (TC-AUTH-14) were added and run
  against real PostgreSQL, including two barrier-rendezvous concurrency tests
  with no timing sleeps, six injected write failures, a commit failure, the
  direct internal completion call and every constraint with the application
  bypassed. Four mutations were run and reverted, each killed. Revision 0009
  **refuses** to apply while unbindable `discord_oauth` sessions exist and states
  the remedy; a rollback past it ends every Discord OAuth login and loses no
  history. Runtime grants are unchanged. Two residual risks are newly recorded,
  RR-05a and RR-15, both bounded and neither reachable through a route in P3.1.
- **Recommendations:** the Technical Lead requests confirmation of the scoped
  unique index and of the two residual risks alongside the independent reviews.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-remediation-submission.md`.

## C-P3.1-F — Phase 3 P3.1 OD-44 provider binding and rotation integrity

**Date:** 2026-08-14 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for Codex independent
implementation re-review and a distinct security-focused pass. Not accepted.
P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** Codex's two blocking findings
  against the C-P3.1-E package, and Peter's 2026-08-14 conditional approval of the
  scoped unique index (decision record §8). SM-01 and SM-02; logical schema
  §9.1–§9.2; the threat model; the test traceability contract;
  `docs/operations/web-portal.md`; migration 0009, which is uncommitted and not
  accepted and was therefore updated rather than superseded. Phase 3 P3.1 only. No
  release boundary changes.
- **Reason:** the completion claim bound the transaction but not the **provider**,
  so an internal caller holding another provider's verified identity and tokens
  could spend a consumed Discord transaction; and the scoped unique index, which
  Peter approved, is only safe if a rotation chain cannot branch or cross.
- **What was implemented:** (1) the claim gained
  `AND provider_key = :provider_key`, and the expected key is derived from
  `VerifiedCompletion` — one indivisible verified result whose identity and tokens
  must name the same provider, each stamped by the adapter that made the network
  call from its own constant. `ProviderTokens` gained `provider_key`;
  `IdentityProvider.verify()` must refuse another provider's tokens, and the
  Discord adapter does. (2) `sessions` gained a unique index on
  `rotated_from_session_id` where not null and two composite foreign keys making a
  successor's account, authentication method and OAuth binding its predecessor's
  own; rotation became one locked transactional repository operation that requires
  a live, unrotated predecessor, inserts the successor from the locked row and
  revokes the predecessor atomically, refusing anything else with the typed
  `SessionRotationRefused`. No creation path accepts a rotation label any more.
- **Alternatives rejected:** a database trigger (the locked operation plus
  declarative keys is smaller and needs no new mechanism); `MATCH FULL` foreign
  keys (would make break-glass rotation impossible); a route-level provider check
  (route ordering is exactly what the finding says must not be relied on); and
  distinguishing the provider-mismatch refusal from the other claim refusals in
  the caller-visible code (would confirm to a prober that a transaction exists and
  which provider it belongs to).
- **Scope effect:** none beyond the authorized remediation. No P3.2 route was
  added, no HTTP evidence was waived, OD-45's allocation is unchanged, and
  revisions 0006–0008 were not edited. One behavioural consequence is recorded
  deliberately: rotation no longer re-runs the N-66 session limit, because a
  rotation replaces a session rather than adding one and the limit could otherwise
  revoke the very predecessor being rotated.
- **Dependency/critical-path effect:** unchanged. The Codex independent
  implementation re-review and the distinct security-focused pass block P3.G1.
- **Estimate/capacity effect:** completed within the same working day as the
  ruling. No forecast change is recorded.
- **Risk, testing, migration, security and operations effect:** 24 new portal
  tests (TC-AUTH-15, TC-AUTH-16) and 3 new migration tests (TC-AUTH-17) were added
  and run against real PostgreSQL, including a barrier-rendezvous rotation race
  with no timing sleep and every new constraint exercised with the application
  bypassed. Six mutations were run and reverted, each killed. Migration 0009 gained
  a second precondition that refuses a pre-existing branched or crossing rotation
  chain with a count and a remedy. Runtime grants are unchanged. RR-15 is recorded
  **closed**; T-05b and T-05c are new threat entries.
- **Recommendations:** the Technical Lead requests that the re-reviews verify the
  conditions in decision record §8 specifically, rather than the package as a
  whole being re-read for the first time.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md`.

## C-P3.1-G — Phase 3 P3.1 OD-44 session lifetime (rotation and idle refresh)

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for Codex independent
implementation re-review and a distinct security-focused pass. Not accepted.
P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** Codex's two blocking
  session-lifetime findings against the C-P3.1-F package, plus the documentation
  the rotation-lifetime correction of 2026-08-14 left outstanding. SM-02; logical
  schema §9.1; the numeric policy register (N-07, N-08, N-15 clarified, **no value
  changed**); the threat model (T-05d); the test traceability contract (TC-AUTH-18,
  TC-AUTH-19); `docs/operations/web-portal.md` §4.3/§4.3a; RAID I-09. Phase 3 P3.1
  only. **No migration was changed** — 0006–0008 were not edited and 0009 needed no
  schema or metadata change, because the defect and its fix are both in the
  repository and application boundary. No release boundary changes.
- **Reason:** `SessionRepository.touch()` updated a row on
  `id = :id AND revoked_at IS NULL` alone. An expired session stays unrevoked
  until something observes it, so a caller holding a `SessionRecord` resolved
  while the session was valid could refresh it after its idle bound and push that
  bound into the future — an expired session revived and kept live to its absolute
  bound. Separately, `SessionService.touch()` always passed
  `SessionSettings.idle_minutes`, so WebAuthn and recovery-grant sessions received
  N-06's 60-minute idle window instead of N-15's 15-minute one, leaving that
  accepted value inoperative for the life of an emergency session. A third defect
  found while fixing them: the repository returned nothing, so a zero-row update —
  a refused refresh — was reported to the caller as success.
- **What was implemented:** the refresh became **one conditional `UPDATE`** that
  matches only while the row is unrevoked and strictly inside both bounds
  (`idle_expires_at > :now`, `absolute_expires_at > :now`; equality at either is
  expired), verifies the expected `auth_method` in the same statement, sets
  `idle_expires_at = LEAST(:now + :idle, absolute_expires_at)` and **never writes
  `absolute_expires_at`**. It `RETURNING`s the persisted bounds as the typed
  immutable `TouchedSession`. `SessionService.touch()` now takes the trusted
  `SessionRecord` rather than a bare id, selects the idle duration from the
  record's persisted authentication method through the existing `bounds_for`, and
  raises the new typed `SessionTouchRefused` when no row matched. The rotation
  correction present at review time was preserved unchanged.
- **Alternatives rejected:** calling `resolve()` before the write (time advances
  after resolution, and the write is the serialization boundary — this is the
  control the finding explicitly rejects); a check constraint (it can relate the
  two bounds to each other but not either to `now()`, which is not immutable); a
  database trigger (a second mechanism where one statement suffices); deriving the
  idle duration inside the repository (would move an accepted numeric policy into
  the adapter layer, away from `bounds_for`); and keeping the `touch(session_id)`
  signature with an added method argument (a caller-supplied method is exactly the
  input that must not be trusted).
- **Scope effect:** none beyond the authorized remediation. No P3.2 route was
  added, no HTTP evidence was waived, OD-45 is unchanged, no dependency was added,
  and no migration was edited. One deliberate interface change: `touch()` takes a
  record, and both of its callers — which are tests, since no P3.1 route calls it —
  were updated.
- **Dependency/critical-path effect:** unchanged. A new Codex independent
  implementation re-review and a distinct security-focused pass block P3.G1.
- **Estimate/capacity effect:** completed within one working session. No forecast
  change is recorded.
- **Risk, testing, migration, security and operations effect:** TC-AUTH-19 is new
  (17 portal tests) and TC-AUTH-18 is recorded in the traceability contract for the
  first time. The whole portal suite is 354 passed / 0 failed / 0 skipped against
  guarded `freedom_test`, and the bot suite 2260 passed. **Nine mutations** were run
  and reverted, each killed, with byte-identical restoration verified by SHA-256;
  two of them are observable only inside a rolled-back `ck_sessions_idle_within_absolute`
  drop, and the first harness run was corrected after it was found to be mutating
  `rotate()`'s identically-shaped predicate instead of `touch()`'s. No migration,
  deployment or runtime-grant change; rollback is unaffected. Operationally,
  §4.3a now states that a refused continuation means *end the session, do not
  retry*, and §4.3 states that a break-glass idle window is fifteen minutes in
  practice and not only at creation. New issue **I-09**; new threat entry **T-05d**.
- **Recommendations:** the Technical Lead requests that the re-reviews test the
  stale-record path specifically — resolve while valid, advance only the injected
  `now`, then continue the session without re-resolving — and check the two
  boundary comparisons for strictness, since an inclusive absolute comparison is an
  equivalent mutant for every row the check constraint permits.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md`.

## C-P3.1-H — Phase 3 P3.1 OD-44 session-touch policy composition

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for Codex independent
implementation re-review and a distinct security-focused pass. Not accepted.
P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** the single blocking finding
  from Codex's 2026-08-15 independent implementation and security re-reviews of
  the C-P3.1-G package. SM-02; logical schema §9.1; the threat model (T-05d); the
  test traceability contract (TC-AUTH-19); `docs/operations/web-portal.md`
  §4.3/§4.3a; RAID I-09. N-06 and N-15 are **clarified, not changed** — no accepted
  numeric value moved and configuration remains their source. Phase 3 P3.1 only.
  **No migration was changed:** 0006–0008 were not edited and 0009 needed no
  schema or metadata change, because the defect and its correction are entirely in
  interface and policy composition. No release boundary changes.
- **Reason:** the C-P3.1-G remediation corrected the break-glass idle window in
  `SessionService` only. `SessionRepository.touch()` still took `idle` and
  `expected_auth_method` as independent arguments, and its SQL verified only that
  the supplied method equalled the row's. A caller supplying a break-glass row's
  **correct** method together with N-06's 60-minute duration therefore matched the
  row and extended its idle window to the emergency absolute bound: N-15's fifteen
  minutes bypassed for a session that resolves to `platform_administrator`, with
  every predicate in the statement satisfied. The method predicate refuses a false
  *method*; it has no view of the duration standing beside it. The repository test
  offered as evidence supplied a mismatched `discord_oauth` method, which exercises
  the predicate and not the bypass, so TC-AUTH-19(h), SM-02, logical schema §9.1,
  T-05d and the C-P3.1-G submission each asserted a property no test established.
- **What was implemented:** `SessionIdlePolicy`, an immutable validated
  method-to-idle mapping built from `SessionSettings` and injected once at the
  composition root. `SessionRepository` requires one at construction; its
  `touch(session_id, *, now)` takes no duration, deadline or authentication-method
  argument, and the single conditional `UPDATE` chooses the window with
  `CASE auth_method` over bind parameters generated from that policy, guarded by an
  `auth_method IN (…)` predicate so an ungoverned method is refused rather than
  silently given its absolute bound through a `NULL` interval. The statement is
  otherwise unchanged: same liveness predicates, strict at both bounds, same clamp,
  `absolute_expires_at` in no `SET` clause, zero rows still `SessionTouchRefused`.
  `SessionService.touch(record, *, now)` keeps its signature and now selects
  nothing. Every construction site was reviewed and updated: the composition root,
  `tools/session_revoke.py`, and the test helper.
- **Alternatives rejected:** adding a second predicate that compares the supplied
  duration against the row's method (keeps the pairing expressible and makes the
  API's safety depend on the caller getting two arguments consistent); naming,
  comments or underscore privacy on the existing signature (the finding explicitly
  refuses this, and the supported API is what P3.2 will call); hard-coding N-06 and
  N-15 in the adapter or the SQL (moves accepted numeric policy out of
  configuration); a check constraint or trigger (neither can express "this
  duration belongs to this method" for a value that is not in the row); and making
  the policy an optional constructor argument with a default (a default is the
  adapter owning the numbers, and it lets a future construction site acquire a
  window nobody configured).
- **Reversal recorded:** C-P3.1-G listed "deriving the idle duration inside the
  repository" as a rejected alternative, on the ground that it would move accepted
  numeric policy into the adapter. That objection stands against adapter-owned
  *constants* and is respected — the adapter still contains no duration. It does
  not stand against the adapter *consuming* configured policy injected through
  composition, which is what is implemented, and the earlier framing is what left
  the duration as a caller-supplied argument.
- **Scope effect:** none beyond the authorized remediation. No P3.2 route was
  added, no HTTP evidence was waived, OD-45 is unchanged, no dependency was added,
  no migration was edited, and no frozen visual asset changed.
- **Dependency/critical-path effect:** unchanged. A new Codex independent
  implementation re-review and a separately reported security-focused re-review
  remain the gating items for P3.G1.
- **Estimate/forecast and capacity effect:** none beyond the remediation itself.
- **New or changed risks:** the finding is a corrected implementation defect
  rather than a new risk. I-09 is amended to record that its first remediation was
  incomplete and that resolution additionally requires no supported API to admit a
  caller-selected refresh duration. T-05d's mitigation text is corrected: an
  authentication-method equality predicate does not validate a caller-supplied
  duration, and no check constraint establishes liveness.
- **Testing, migration, security and operational effect:** TC-AUTH-19(h) is
  rewritten and its inadequate mismatched-method test replaced. The new evidence is
  behavioural through the repository alone — N-06 applied to a Discord OAuth row,
  N-15 to WebAuthn and recovery-grant rows — plus a narrow signature assertion, a
  `TypeError` proof that the former pairing is unexpressible under any spelling,
  policy-validation cases, and a rolled-back `ck_sessions_auth_method` drop that
  makes the governed-method predicate observable. Thirteen mutants were applied and
  reverted, each killed, with byte-identical restoration verified by SHA-256 and
  the focused suite rerun after restoration. No migration, deployment or
  runtime-grant change; rollback is unaffected. Operationally, §4.3 now records
  that the fifteen-minute rule holds at both layers and not only in the service.
- **Recommendations:** the Technical Lead requests that the re-reviews attempt the
  bypass directly — construct a break-glass session, then try to obtain N-06's
  window through the repository by any route including the policy object — and
  check that no construction site defaults the policy.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md`.

## C-P3.1-I — Phase 3 P3.1 OD-44 session idle-policy construction

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for Codex independent
implementation re-review and a distinct security-focused pass. Not accepted.
P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** the single blocking finding
  from Codex's 2026-08-15 independent re-review of the C-P3.1-H package, plus the
  related composition defect reported with it. SM-02; logical schema §9.1; the
  threat model (T-05d); the test traceability contract (TC-AUTH-19);
  `docs/operations/web-portal.md` §4.3; RAID I-09; the OD-44 addendum. N-06 and
  N-15 are **unchanged** — no accepted numeric value moved, `SessionSettings`
  remains their source, and the configuration contract's accepted ranges are
  untouched. Phase 3 P3.1 only. **No migration was changed:** 0006–0009 were not
  edited and none needed editing, because the defect and its correction are
  entirely in interface and composition. No release boundary changes.
- **Reason:** C-P3.1-H removed `idle` and `expected_auth_method` from
  `SessionRepository.touch()` but moved the same authority into a publicly
  constructible `SessionIdlePolicy`. It was a frozen dataclass whose generated
  constructor took `tuple[tuple[AuthMethod, timedelta], ...]`, and the mapping
  that assigns N-06's 60-minute window to *every* method is complete,
  duplicate-free and positive — so the constructor accepted it, the generated
  `CASE` selected 60 minutes for a persisted WebAuthn or recovery-grant row, and
  N-15's 15-minute idle limit was bypassed up to the 60-minute emergency absolute
  bound. The existing policy tests asserted completeness, uniqueness and
  positivity and never attempted a complete but semantically false mapping.
  C-P3.1-H's statements that no supported API could pair a method with another
  policy's duration, and that policy was built once and injected, were therefore
  both false. The second was false of the composition independently:
  `WebComposition.services()` constructed a policy for the repository while
  `SessionService.__init__()` constructed another from settings — equivalent under
  production inputs, but two derivations that an alternate construction site could
  make disagree, leaving creation/rotation bounds at odds with refresh policy.
- **What was implemented:** `SessionIdlePolicy` has **no public constructor**.
  `__init__` refuses every call; the only supported factory is
  `from_settings(SessionSettings)`; and which methods receive the emergency window
  is classification derived inside the class from `AuthMethod.is_break_glass`
  rather than a mapping any caller supplies. The object is immutable
  (`__setattr__`/`__delattr__` refuse) and defines no `__eq__`, so "the same
  policy instance" is a property a test can assert with `is` and cannot be
  weakened into a value comparison. `WebComposition` builds **one** policy at
  construction and injects that same object into `SessionRepository` and into
  `SessionService`, whose `idle_policy` is now a required constructor argument
  instead of a second derivation; `tools/session_revoke.py` follows the same
  pattern. Both layers expose a read-only `idle_policy` property so the wiring is
  assertable without reaching into a private attribute. `for_method` refuses
  anything that is not an `AuthMethod` rather than defaulting it. The conditional
  `UPDATE` is **unchanged**: same generated `CASE`/`IN` over bind parameters, same
  liveness predicates strict at both bounds, same clamp, `absolute_expires_at` in
  no `SET` clause, zero rows still `SessionTouchRefused`, transactions still owned
  by the caller.
- **Alternatives rejected:** keeping the dataclass constructor and adding a
  validator that the break-glass durations equal the configured emergency value
  (re-derives the settings the caller was allowed to contradict, so the pairing
  stays expressible and the class becomes a second numeric authority);
  an `emergency < ordinary` invariant (the configuration contract permits
  `WEB_SESSION_IDLE_MINUTES` down to 1 against a `WEB_EMERGENCY_SESSION_IDLE_MINUTES`
  ceiling of 15, so this would refuse accepted configurations, and the finding
  explicitly rules it out); underscore-privacy, naming or a documented convention
  to use `from_settings()` (the finding explicitly refuses all four);
  a constructor taking two bare durations rather than `SessionSettings` (narrower
  than the mapping, but still a second numeric entry point beside the validated
  configuration object); passing the policy to `SessionService` as an optional
  argument defaulting to a derivation (a default is exactly how the second
  derivation survived); and hard-coding 60/15 in the adapter or the SQL (moves
  accepted numeric policy out of configuration).
- **Scope effect:** none beyond the authorized remediation. No P3.2 route was
  added, no HTTP evidence was waived, OD-45 is unchanged, no dependency was added,
  no migration was edited, and no frozen visual asset changed.
- **Dependency/critical-path effect:** unchanged. A new Codex independent
  implementation re-review and a separately reported security-focused re-review
  remain the gating items for P3.G1.
- **Estimate/forecast and capacity effect:** none beyond the remediation itself.
- **New or changed risks:** a corrected implementation defect rather than a new
  risk. I-09 is amended to record that the second remediation was also incomplete
  and that resolution additionally requires no supported API to admit a
  caller-*constructed* method-to-duration mapping, and requires the repository and
  service to demonstrably hold the same policy instance. T-05d, SM-02 and logical
  schema §9.1 are corrected where they concluded from the absence of call
  arguments that the pairing was unrepresentable.
- **Testing, migration, security and operational effect:** TC-AUTH-19 gains (j),
  which attempts the finding's exact all-ordinary mapping and the subtler
  single-method variant against the new construction boundary, runs the finding's
  full four-line sequence and shows it halting before any database work, asserts
  the class's public surface and the absence of dataclass machinery, proves
  classification against real PostgreSQL for a configuration whose ordinary window
  is **shorter** than its emergency one, and asserts single-instance injection
  with `is` across two `services()` calls. Sixteen mutants were applied and
  reverted, each killed, with byte-identical restoration verified by SHA-256 and
  the focused suite rerun after restoration. No migration, deployment,
  configuration or runtime-grant change; rollback is unaffected. Operationally,
  §4.3 records that the fifteen-minute rule now holds against how the policy is
  built and not only against how it is called.
- **Recommendations:** the Technical Lead requests that the re-reviews attempt to
  obtain N-06's window for a break-glass row by **any** route — the repository
  API, the service API, the policy factory, and construction of a policy by any
  means the module exposes — and that they check every `SessionRepository` and
  `SessionService` construction site for a second derivation.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-session-idle-policy-construction-remediation-submission.md`.

## C-P3.1-J — Phase 3 P3.1 OD-44 session settings/bounds construction model

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for a fresh
independent implementation re-review and a distinct security-focused pass. Not
accepted. P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** the three blocking
  counterexamples from Codex's 2026-08-15 independent re-review of the C-P3.1-I
  package. SM-02; logical schema §9.1; the threat model (T-05d); the numeric
  policy register (enforcement location); the test traceability contract
  (TC-AUTH-19); `docs/operations/web-portal.md` §4.3; RAID I-09. **No accepted
  numeric value moved, no configuration variable was renamed and no deployment
  value changed**; configuration remains the source of N-04, N-06, N-07, N-15 and
  N-66. Phase 3 P3.1 only. **No migration was changed:** 0006–0009 were not
  edited, because the defect and its correction are entirely in construction and
  composition. No release boundary changes.
- **Reason:** C-P3.1-I closed `SessionIdlePolicy`'s constructor, and three
  counterexamples survived it. **F1:** `from_settings()` validated only
  positivity, and `SessionSettings` was a public frozen dataclass with no
  construction-time validation, so `SessionSettings(..., emergency_idle_minutes=60,
  ...)` was an accepted object and the derived policy returned sixty minutes for
  both break-glass methods. Environment-reader validation cannot make invalid
  instances of a public settings type impossible, and the removed factory's own
  docstring named tests and operator tools as supported builders. **F2:** the
  refresh statement was generated by iterating the policy's public, overridable
  `__iter__`, so a subclass inheriting the supported factory replaced the mapping
  the database used while `for_method()` reported fifteen minutes; the recorded
  reproduction bound `idle_seconds = 3600.0` for all three methods. This is
  ordinary Python subclassing, and C-P3.1-I was wrong to treat it as process-memory
  forgery. **F3:** `SessionService.__init__()` accepted a repository and an
  independently supplied policy and required no relationship between them, so a
  supported caller could build a graph creating sessions under one idle window and
  refreshing them under another; correct wiring at the two production sites was
  true and was not an invariant.
- **What was implemented:** the construction model was **simplified**, not
  guarded further. `SessionIdlePolicy` is **deleted**. `SessionSettings` validates
  the accepted register in `__post_init__` against `SESSION_CEILINGS`, a single
  table also read by the environment reader, so an out-of-register instance cannot
  exist however it was built (F1). `SessionRepository(connection, settings=…)`
  **derives** a `SessionPolicy` — five numbers with fixed roles, no mapping and no
  `__iter__` — reading each configured value exactly once, and accepts no policy
  object; the `CASE` branches are generated by walking `AuthMethod` and asking
  `session_class_of()`, so there is nothing to iterate and nothing a subclass can
  replace (F2). `SessionService(sessions=…, token_grants=…, audit=…)` reads its
  bounds from that repository and has **no** settings or policy argument, so two
  independently configured bounds sources are not constructible (F3);
  `WebComposition` no longer holds a policy of its own, and
  `tools/session_revoke.py` follows the same shape. `AuthMethod.is_break_glass`
  stopped being `not is_ordinary_provider`: classification is now the explicit
  `_SESSION_CLASSES` table, and a method absent from it raises
  `UnclassifiedAuthMethod` at module import and again at repository construction.
  The conditional `UPDATE` is **unchanged**: same generated `CASE`/`IN` over bind
  parameters, same liveness predicates strict at both bounds, same
  `LEAST(..., absolute_expires_at)` clamp, `absolute_expires_at` in no `SET`
  clause, zero rows still `SessionTouchRefused`, transactions still owned by the
  caller.
- **Alternatives rejected:** adding a validator to `from_settings()` that
  re-derived the emergency value (a third guard on the same extensible object,
  which the finding explicitly rules out); custom immutability machinery,
  reflection guards or interface-inspection assertions (same); making
  `SessionSettings` private (it is the configuration contract's public type and
  tests and tools legitimately build it); keeping `is_break_glass` as
  `not is_ordinary_provider` (silently classifies a future method, which the
  finding explicitly forbids); carrying the classification in `AuthMethod`'s member
  values (would change the persisted `.value` used as the `auth_method` column);
  giving `SessionService` an optional `settings` argument defaulting to the
  repository's (a default is exactly how the second derivation survived twice);
  and hard-coding 60/15 in the adapter or the SQL (moves accepted numeric policy
  out of configuration).
- **Scope effect:** none beyond the authorized remediation. No P3.2 route was
  added, no HTTP evidence was waived, OD-45 is unchanged, no dependency was added,
  no migration was edited, and no frozen visual asset changed. One collateral
  correction was required and is called out rather than folded in:
  `_Reader.integer` and `_read_session` now follow a recorded problem with an
  **in-range** fallback, because the settings constructor runs inside the reader
  and would otherwise abort the collection and report one problem where there are
  several. `test_every_out_of_range_session_bound_is_reported_in_one_pass` is the
  regression test for that.
- **Dependency/critical-path effect:** unchanged. A fresh independent
  implementation re-review and a separately reported security-focused re-review
  remain the gating items for P3.G1.
- **Estimate/forecast and capacity effect:** none beyond the remediation itself.
- **New or changed risks:** a corrected implementation defect rather than a new
  risk. I-09 is amended to record that the third remediation was also incomplete
  and that resolution additionally requires the type carrying the accepted bounds
  to be unconstructible outside the register, no object consumed by the refresh
  SQL to be caller-supplied or overridable, and a service/repository graph to
  admit only one bounds source. T-05d, SM-02, logical schema §9.1 and the numeric
  register are corrected where they concluded a property from a closed constructor
  or from correct production wiring.
- **Testing, migration, security and operational effect:** TC-AUTH-19 gains (k):
  every register bound refused at `SessionSettings` construction in both
  directions with the ceiling and 1 accepted and N-15's 15/16 boundary named; F1's
  sequence run in order against PostgreSQL and shown to halt before any write with
  the row byte-identical; the bind parameters of the conditional write asserted to
  classify rather than repeat one window; a genuinely forged `SessionPolicy`
  subclass shown to have no keyword through which to reach a repository, with the
  persisted break-glass row still receiving N-15 from PostgreSQL; a
  `SessionSettings` subclass whose field answers 15 then 60 shown to be read
  exactly once; F3's mismatch sequence executed with two different valid
  configurations; every construction site exercised; and an unclassified
  authentication method proved to refuse twice — through the real guard given a
  synthetic enum, and by removing an entry from the production table and observing
  `SessionRepository` construction raise, with restoration asserted afterwards.
  The portal suite rose from 381 to 392 collected tests; no test was removed, and
  the superseded policy-construction tests were **replaced** by stronger ones.
  **Mutation testing was not run for this remediation** and is not claimed: the
  three direct counterexamples are closed and demonstrated by recorded before/after
  reproductions, and the prompt makes mutation useful only afterwards. No
  migration, deployment, configuration or runtime-grant change; rollback is
  unaffected.
- **Recommendations:** the Technical Lead requests that the re-reviews attempt to
  obtain N-06's window for a break-glass row by **any** route — the settings
  constructor, `SessionPolicy.derive`, subclassing either type, the repository
  constructor, the service constructor, and every construction site — and that
  they specifically probe whether `SessionPolicy` being a public frozen dataclass
  leaves a residual worth closing, since it is derived and never accepted but is
  still nameable.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`.

## C-P3.1-K — Phase 3 P3.1 OD-44 session-policy numeric validation

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for a fresh
independent implementation re-review and a distinct security-focused pass. Not
accepted. P3.G1 remains open. P3.2 has not started.*

- **Affected requirement, milestone and release:** the single blocking finding
  from Codex's 2026-08-15 independent re-review of the C-P3.1-J package, reported
  from two perspectives — **F1** in the implementation review and **S1** in the
  distinct security-focused pass. They are **one defect**, not two. N-66; the
  numeric policy register (the *type* half of the accepted fields); the test
  traceability contract (TC-AUTH-19(l), new TC-SESS-08b); RAID I-09. **No accepted
  numeric value moved, no configuration variable was added, renamed or removed,
  and no deployment value changed**; configuration remains the source of N-04,
  N-06, N-07, N-15 and N-66. Phase 3 P3.1 only. **No migration was changed:**
  0006–0009 were not edited, because the defect and its correction are entirely
  in runtime validation. No release boundary changes.
- **Reason:** C-P3.1-J gave both enforcement gates the same *bounds* and left each
  to state independently what a value of these fields may **be**.
  `SessionSettings.__post_init__` said "an actual `int`, never a `bool`, positive,
  within its ceiling". The derived-policy gate restated the rule as the two
  ordering comparisons `value < 1` and `value > ceiling` and dropped the type
  half. Two ordering comparisons are not a whole-number rule: `float("nan")` makes
  both of them false. A non-finite `max_sessions_per_account` therefore survived
  `SessionPolicy.derive()`, and `len(live) >= maximum` in `_enforce_session_limit`
  was false for **every** live-session count — the accepted per-account
  live-session bound revoked nothing. It was reachable through the supported
  repository constructor with no `object.__new__`, no mutation of a frozen
  instance, no forged `SessionPolicy` and no private helper, because `derive()`
  deliberately accepts `SessionSettings` subclasses and a subclass whose inherited
  `__post_init__` observes the valid stored integer may answer differently on the
  single later derivation read.
- **Alternatives considered:** patching NaN specifically (rejected — it names one
  value of a class of values, and `10.0`, `2.5` and `True` would still pass);
  relying on the `int` annotations (rejected — annotations are not enforcement);
  forbidding subclassing of `SessionSettings` (rejected — `derive()` accepts
  subclasses deliberately, and the honest fix is to validate what it reads);
  reflection or source inspection of the caller (rejected outright); and adding a
  third type check inside `SessionPolicy` (rejected — a third restatement is the
  mechanism that produced this defect twice).
- **Added/removed scope:** none. One shared validator, called by both gates, and
  regression tests. No feature, route, variable or dependency added.
- **Dependency and critical-path effect:** none beyond the re-review already
  blocking P3.G1. P3.2 remains unstarted.
- **Estimate/forecast and capacity effect:** within the P3.1 remediation
  allowance; no forecast change.
- **New or changed risks:** RAID I-09 amended a fifth time. The residual recorded
  for reviewers is that `SessionPolicy` remains a public, nameable frozen
  dataclass — derived and never accepted — and that the other `WebSettings`
  sub-dataclasses have **not** been audited for the same shape.
- **Testing, migration, security and operational effect:** the correction is
  strictly a tightening; no control was relaxed. `application/web/config.py` now
  holds `session_policy_problem`/`session_policy_problems` beside
  `SESSION_CEILINGS` as the single runtime definition of the accepted type and
  range, and both `SessionSettings.__post_init__` and `_validate_policy_values` in
  `application/web/sessions.py` call it. Evidence is the new
  `tests/web/test_session_policy_numeric_validation.py` (28 cases), mapped
  one-to-one to the eight prompt requirements and recorded as TC-AUTH-19(l) and
  TC-SESS-08b. **A falsification run is recorded rather than asserted:** with the
  reviewed two-comparison validator restored in memory, nine of the new cases fail
  while the entire pre-existing 54-test session-lifetime suite stays green —
  direct evidence that the earlier suite contained no counterexample. Fresh
  results: 420 portal tests and 2260 bot tests, 0 failed and **0 skipped**;
  `alembic check` reports no new upgrade operations; `git diff --check` clean; the
  14-entry visual-freeze manifest verified. **Mutation testing was not run for
  this remediation and is not claimed.** No migration, deployment, configuration
  or runtime-grant change; rollback is unaffected, because nothing persisted
  changed shape or meaning.
- **Recommendations:** the Technical Lead requests that the re-reviews attempt to
  reach `_enforce_session_limit` with a `max_sessions_per_account` that is not an
  `int` by **any** route, and then check whether any *other* accepted numeric
  policy in `WebSettings` has the same shape — a settings dataclass whose bounds
  or types only one of its gates enforces. This remediation fixed the session
  register; it did not audit the others, and that is a stated gap rather than an
  oversight reported as complete.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md`.

## C-P3.1-L — Phase 3 P3.1 settings-construction validation (exact `int`; RAID I-10)

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for a fresh
independent implementation review, a distinct security-focused pass and an
availability review of the pool and worker bounds. Not accepted. P3.G1 remains
open. P3.2 and P3.3 have not started.*

- **Affected requirement, milestone and release:** two connected deliverables in
  one package. (1) The still-open comparison-overriding `int`-subclass bypass in
  the shared session-policy validator — N-66, RAID I-09, TC-AUTH-19(m). (2) RAID
  I-10: `RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`,
  `DatabasePoolSettings` and `WorkerSettings` made valid by construction —
  N-09, N-10, N-14, N-18, N-19, N-21, N-22, N-23, N-30…N-34, N-41…N-45, N-53,
  N-60; the numeric policy register (the *type* half and the enforcement points);
  the configuration and dependency contract (§2.2's bounds, where they hold); the
  test traceability contract (TC-AUTH-19(m), new TC-STRUCT-07, new TC-LIM-06).
  **No accepted numeric value moved, no environment variable was added, renamed
  or removed, no deployment value changed, and no migration was touched** —
  0006–0009 were not edited, because both defects and both corrections are
  entirely in runtime validation. No release boundary changes. Phase 3 P3.1 only.
- **Reason.** (1) C-P3.1-K gave both session gates one definition of the accepted
  type and left that definition stating it as `isinstance(value, int) and not
  isinstance(value, bool)`. That refuses `bool` and every float and admits every
  **other** subclass of `int`. An `int` subclass may override `__lt__`, `__gt__`,
  `__le__` and `__ge__`, and Python gives the right-hand subclass's reflected
  comparison priority, so `len(live) >= maximum` is answered by the subclass:
  `dataclasses.replace(settings, max_sessions_per_account=LyingInt(10))` survived
  settings construction **and** `SessionPolicy.derive()`, and
  `_enforce_session_limit` saw false for every live-session count — N-66
  inoperative for the third time, through the supported public constructor with
  no `object.__new__`, no frozen-object mutation, no private helper, no forged
  policy and no skipped `__post_init__`. (2) The five settings types had no
  construction-time validation at all; `WebSettings.from_environment()` validated
  the strings it parsed, which protects the ordinary path and is not an invariant
  of a public value object. This is **not** an environment-string bypass and none
  is claimed; it is the same authority-boundary shape the session work found five
  times.
- **Alternatives considered:** excluding known `int` subclasses by name (rejected
  — it names members of a class of values, exactly as patching NaN did); relying
  on the `int` annotations (rejected — annotations are not enforcement); checking
  one comparison result to detect a lying value (rejected — it asks the value
  under test to grade itself); coercing with `int(value)` (rejected — a coercion
  accepts the input and then changes it, which is how a refusal becomes a silent
  reinterpretation); a single generic validator taking arbitrary field names
  (rejected — it cannot prove a type's cross-field rules); five copies of the
  same primitive integer rule (rejected — that is the drift mechanism this whole
  line of remediation is about); independently injectable policy objects
  (rejected — a second bounds source, which OD-44's F3 already demonstrated);
  and enforcing a worker heartbeat/lease ordering (rejected — no accepted
  document states one, and choosing policy in a constructor is not the accepted
  route for new policy; it is raised as an open maintainer question instead).
- **Added/removed scope:** none. One shared `PolicyBound`/`policy_number_problem`
  definition, six register tables citing it, `__post_init__` on the five types,
  read-once canonicalisation at five composition seams, and regression tests. No
  feature, route, environment variable or dependency added.
- **Dependency and critical-path effect:** none beyond the re-review already
  blocking P3.G1. P3.2 and P3.3 remain unstarted.
- **Estimate/forecast and capacity effect:** within the P3.1 remediation
  allowance; no forecast change.
- **New or changed risks:** RAID I-09 amended a sixth time; RAID I-10 amended
  with implementation and evidence state and **left open**. Residuals recorded
  for reviewers: N-09/N-10 have no P3.1 route consumer and N-21/N-22 have no
  consumer at all; `WEB_WEBAUTHN_USER_VERIFICATION` and
  `WEB_RECOVERY_GRANT_MINUTES` are validated but read by no runtime consumer;
  the worker's lease, heartbeat, attempt, timeout and queue consumers belong to
  P3.3; and the relational rules (S-02, S-05, S-09) necessarily remain at the
  environment boundary, because no sub-dataclass carries both sides of them.
- **Testing, migration, security and operational effect:** the correction is
  strictly a tightening; no control was relaxed and no accepted value was
  replaced by a default — a stricter configured value is proved to survive
  unchanged. Evidence is `tests/web/test_session_exact_integer_policy.py` (22
  cases, TC-AUTH-19(m)) and `tests/web/test_settings_construction_validation.py`
  (145 cases, TC-STRUCT-07 and TC-LIM-06). **Two falsification runs are recorded
  rather than asserted:** with the reviewed `isinstance` predicate restored in
  memory, 16 of the 22 new session cases fail while the entire pre-existing
  28-case numeric-validation module stays green; with `__post_init__` removed
  from the five types in memory, 81 of the 145 new cases fail while all 442
  pre-existing portal tests stay green. Neither existing suite contained a
  counterexample. Neither run edited a tracked file, proved by an identical
  `git status --short` before and after. Fresh results: **587 portal tests and
  2260 bot tests, 0 failed and 0 skipped**; compilation under both configured
  interpreters; `alembic check` reports no new upgrade operations; `git diff
  --check` clean; the 14-entry visual-freeze manifest verified. **Mutation
  testing was not run and is not claimed**; no mutation tool is configured. No
  formatter, linter or type checker is configured in this repository — verified
  by inspection, not assumed. No migration, deployment, configuration or
  runtime-grant change; rollback is unaffected, because nothing persisted changed
  shape or meaning.
- **Recommendations:** the Technical Lead requests that the re-reviews attempt to
  reach any enforcement comparison — the session limit, a rate-limit budget, the
  body bound — with a value that is not an exact built-in `int`, by any route
  including a subclass that lies only on a later read; and that the availability
  review consider whether the pool and worker bounds should additionally carry a
  relationship rule, which this package deliberately did **not** invent.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-settings-construction-validation-remediation-submission.md`.

## C-P3.1-M — Phase 3 P3.1 N-23 worker lease corrected to an exact 60 seconds (corrects C-P3.1-L)

**Date:** 2026-08-15 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for review. Not
accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have not started.*

- **Affected requirement, milestone and release:** N-23's worker job lease, as
  implemented by C-P3.1-L. One runtime definition in `application/web/config.py`
  (`WORKER_BOUNDS["lease_seconds"]`), the tests that exercise it, and the
  descriptions C-P3.1-L introduced in the numeric policy register, the
  configuration and dependency contract, the test traceability contract
  (TC-STRUCT-07, TC-LIM-06), the RAID register, status and its own submission.
  **The accepted N-23 row is unchanged and remains the authority: the lease is 60
  seconds.** No accepted numeric value moved, no environment variable was added,
  renamed or removed, `.env.example` is unchanged (it already shipped
  `WORKER_LEASE_SECONDS=60`), and no state machine, logical schema, migration,
  route, service, worker behaviour, runtime grant or deployment value changed.
  No release boundary changes. Phase 3 P3.1 only.
- **Reason.** Independent review found C-P3.1-L's N-23 entry wrong. It defined
  `"lease_seconds": PolicyBound(minimum=1, maximum=60, policy="N-23")`, treating
  the accepted "60 seconds" as a ceiling and accepting every exact integer from 1
  to 60 as a lease. The accepted row reads `Job lease | 60 seconds, heartbeat at
  most every 20 seconds`: one sentence stating a lease **value** and a heartbeat
  **maximum**, and the distinction is deliberate. SM-05 renews with
  `lease_expires_at = now() + 60s`; the logical schema's claim and lease-renewal
  statements write the same 60; the operational contract's reaper liveness signal,
  wedged-worker procedure and `N-23 + N-44` recovery bound are all calculated from
  a 60-second lease. A one-second lease was therefore a contradiction of the
  accepted documents rather than a permitted tightening, and would have lost a
  live claim to ordinary heartbeat scheduling. The entry is now
  `PolicyBound(minimum=60, maximum=60, policy="N-23")` — the same exact-value
  shape N-41's concurrency and N-34's proxy hop count already had.
  `heartbeat_seconds` is **unchanged** at a ceiling of 20 with a floor of 1.
- **Alternatives considered:** rewriting the accepted N-23 row to match the
  delivered code (rejected — the accepted row, state machine, schema and
  operational calculations are the authority, and a register edited to agree with
  its implementation is not a register); leaving `1…60` and adding a
  heartbeat-less-than-lease ordering rule (rejected — it would make new policy in
  a constructor to compensate for a bound that was simply wrong, and would still
  accept a two-second lease); adding an N-45 relationship (rejected — no accepted
  document states one, and one may not be added without a separately accepted
  policy decision); restating 60 in a second validator, constructor branch,
  environment reader, consumer or test helper (rejected — a second authority is
  the drift this structure exists to prevent, so the tests parameterise from
  `WORKER_BOUNDS`, with a single deliberate exception that binds the register to
  the accepted row).
- **Added/removed scope:** none. One `PolicyBound`, its comment, twenty test
  cases and the descriptions that were inaccurate. No feature, route, environment
  variable, dependency or worker behaviour added; **no worker execution was
  implemented to test this setting** — the runtime consumers remain P3.3's.
- **Dependency and critical-path effect:** none beyond the re-review already
  blocking P3.G1. **The "lease/heartbeat ordering" item C-P3.1-L raised as a
  P3.3 prerequisite is withdrawn**, not answered: `lease_seconds=1,
  heartbeat_seconds=20` was never inside the accepted register, so it was never
  evidence that an ordering rule was missing. With the lease exactly 60 every
  accepted heartbeat is already far inside it, no ordering rule was added, none
  is needed, and nothing about N-23 blocks P3.3. P3.2 and P3.3 remain unstarted.
- **Estimate/forecast and capacity effect:** within the P3.1 remediation
  allowance; no forecast change.
- **New or changed risks:** RAID **I-10 amended and left open**; I-09 unchanged.
  C-P3.1-L's residuals still stand and are unchanged by this correction:
  N-09/N-10 have no P3.1 route consumer and N-21/N-22 have no consumer at all;
  `WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated
  but read by no runtime consumer; the worker's lease, heartbeat, attempt,
  timeout and queue **consumers** belong to P3.3; and the relational rules (S-02,
  S-05, S-09) remain at the environment boundary. **No new risk is introduced**:
  the change refuses more configurations than before and refuses them at startup.
- **Testing, migration, security and operational effect:** strictly a tightening
  of a configuration bound. Availability is improved rather than reduced — a
  lease shorter than the accepted 60 could have expired mid-attempt and let the
  reaper requeue live work — and the failure mode is a startup refusal naming
  `WORKER_LEASE_SECONDS` without echoing its value, not a request-time
  degradation. Evidence is TC-STRUCT-07 and TC-LIM-06 as corrected: twenty new
  cases in `tests/web/test_settings_construction_validation.py` (165 total, up
  from 145) covering direct construction, `dataclasses.replace()`, the exact-type
  rule, canonicalisation of a lying subclass, the environment reader unset and
  explicit, S-10 refusal of 59 and 61 with the variable named and the value
  absent, aggregation with other settings types, the unchanged heartbeat
  boundaries, and the withdrawn counterexample proved to halt at construction
  **for its lease**. **One falsification run is recorded rather than asserted:**
  with only the `minimum=1, maximum=60` entry restored in memory by a plugin held
  outside the worktree, 10 of the new cases fail and every other portal test stays
  green; `git status --short` is byte-identical before and after. **Mutation
  testing was not run and is not claimed**; no mutation tool is configured. Fresh
  results: **607 portal tests and 2260 bot tests, 0 failed and 0 skipped**;
  compilation under both configured interpreters; `alembic check` reports no new
  upgrade operations; `git diff --check` clean; the 14-entry visual-freeze
  manifest verified. No formatter, linter or type checker is configured — verified
  by inspection, not assumed. No migration, deployment, configuration-variable or
  runtime-grant change; rollback is unaffected, because nothing persisted changed
  shape or meaning.
- **Recommendations:** the Technical Lead requests that the availability review
  confirm the exact 60-second lease against SM-05, the schema's claim and renewal
  statements and the `N-23 + N-44` recovery calculation, and that reviewers treat
  the withdrawal of the ordering question as a correction of a false premise
  rather than as a policy decision. Any relationship involving N-45 remains
  unaccepted and must not be introduced without a separate decision.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md`.

## C-P3.1-N — Phase 3 P3.1 one canonical settings graph per web process (RAID I-09/I-10)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for review. Not
accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have not started.*

- **Affected requirement, milestone and release:** the configuration boundary of
  the web process — `application/web/config.py` (the descending
  `canonical_settings`, the declared `CANONICAL_SETTINGS_GRAPH`,
  `canonical_web_settings`, `require_canonical`, `require_canonical_web_settings`
  and the typed `SettingsAuthorityError`), `adapters/web/composition.py` (one
  canonical graph, and the Discord adapter built here rather than injected),
  `adapters/web/app.py` (exactly one configuration authority, and the provider
  required to hold it), `adapters/web/discord_provider.py`,
  `application/web/oauth.py` and `application/web/breakglass.py`, with
  `tests/web/test_canonical_settings_graph.py` as the evidence and the
  configuration/dependency and test-traceability contracts amended by addition.
  **No accepted numeric value moved, no environment variable was added, renamed
  or removed, `.env.example` is unchanged, and no state machine, logical schema,
  migration, route, service, worker behaviour, runtime grant, deployment value or
  visual asset changed.** No release boundary changes. Phase 3 P3.1 only.
- **Reason.** C-P3.1-K and C-P3.1-L made each settings *type* valid by
  construction. That is a property of an object, not of a process, and a process
  could still hold two individually valid graphs and use each in different
  places: `WebComposition` retained the caller's `WebSettings`;
  `create_app(settings_a, composition=composition_b)` installed middleware,
  cookies, digests and startup checks from A while every service used B;
  `OAuthLoginService` and `BreakGlassService` re-read
  `session.oauth_transaction_minutes` and `encryption.active_version` from
  whatever they were handed; and the composition accepted a **ready-made identity
  provider**, so a genuine `DiscordIdentityProvider` built from a valid graph B
  could serve R-03's authorization URL and R-04's token exchange for an
  application that had validated graph A — putting S-05's redirect-origin check
  and the redirect URI actually used on two different objects. Two further
  defects were found in the evidence offered for the first correction and are
  fixed here: ten adversarial cases engaged their lie *before* the genuine
  constructor ran, so they proved a settings constructor refuses rather than that
  the canonicalisation boundary does; and the graph-completeness test iterated
  the declaration it was meant to verify, so an omitted nested field removed both
  the obligation and the check.
- **Alternatives considered:** comparing the composition's graph with the
  injected provider's, or with `create_app`'s second `settings` argument
  (rejected — two authorities that agree today are still two authorities, and a
  field comparison of provider settings is a comparison of the client secret);
  inspecting the provider's private `_settings` from the composition (rejected —
  private-attribute introspection in production, and it would still admit a
  second graph that happened to match); accepting a provider *factory* closure
  (rejected — a closure can capture graph B as easily as an object can hold it);
  deleting provider injection outright (rejected — the portal's suite needs a
  double that is not a Discord provider at all, and deterministic HTTP tests need
  a transport seam); inferring the graph's shape from annotations at runtime
  (rejected — reflection guessing security policy from arbitrary objects is
  exactly what the declared graph exists to avoid; the annotations are used by
  the **test**, and the declaration remains the runtime authority); and adjusting
  the ten failing assertions until they passed (rejected — they were failing
  because they never reached the boundary they described).
- **Added/removed scope:** none. One descending canonicalisation, one declared
  graph, one typed refusal, a provider built where it was previously injected, a
  renamed and narrowed test-adapter seam (`provider_double`, plus
  `provider_client` for transport), and a rewritten 46-case evidence module. No
  feature, route, environment variable, dependency or worker behaviour added.
- **Dependency and critical-path effect:** none beyond the re-review already
  blocking P3.G1. P3.2 and P3.3 remain unstarted.
- **Estimate/forecast and capacity effect:** within the P3.1 remediation
  allowance; no forecast change.
- **New or changed risks:** RAID **I-09 and I-10 amended and both left open**.
  The residuals recorded by C-P3.1-L and C-P3.1-M are unchanged. One new
  obligation is recorded rather than silently taken: a settings type added to the
  graph in future must be declared in `CANONICAL_SETTINGS_GRAPH`, and an
  undeclared one now refuses at runtime instead of being canonicalised as a leaf.
- **Testing, migration, security and operational effect:** strictly a tightening,
  applied at startup rather than per request. A misconfigured or two-authority
  composition refuses to start with a typed error naming a type or a field path
  and **never a configured value**; no control was relaxed, no authority widened,
  no secret rendered, compared or decoded, and the environment boundary still
  aggregates every problem into one redacted `ConfigurationError`. Evidence is
  TC-STRUCT-08 (46 cases in `tests/web/test_canonical_settings_graph.py`), **653
  portal and 2260 bot tests with 0 failed and 0 skipped**, compilation under both
  configured interpreters, `alembic check` reporting no new upgrade operations,
  `git diff --check` clean and the 14-entry visual-freeze manifest verified. **No
  formatter, linter or type checker is configured** — verified by inspection, not
  assumed. **Four falsification runs are recorded rather than asserted**, each
  reverted with a byte-for-byte checksum comparison: restoring the
  mismatched-provider path fails three provider-authority cases; restoring the
  premature-engagement harness fails 25 of the 46; deleting one nested
  classification fails the independent completeness test **while the old
  self-referential assertion still passes**; and restoring the unrecognised
  environment-variable name fails the aggregation case. **Mutation testing was
  not run and is not claimed**; no mutation tool is configured. No migration,
  deployment, configuration-variable or runtime-grant change; rollback is
  unaffected, because nothing persisted changed shape or meaning.
- **Recommendations:** the Technical Lead asks the implementation review to
  confirm that the provider seam admits no supported route back to two
  authorities, and asks the security review to confirm the redaction of every new
  refusal and the treatment of the injected `httpx` client as transport-only. The
  SQLAlchemy engine seam is **deliberately** left as a supplied infrastructure
  dependency, with the reasoning stated in the submission §5 — reviewers are
  asked to accept or reject that reasoning explicitly rather than by silence.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md`.

## C-P3.1-O — Phase 3 P3.G1 provider and engine authority (corrects C-P3.1-N)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** the composition root and
  application factory of the web process — `adapters/web/composition.py` (no
  `engine`, `provider` or `provider_double` parameter; the engine and the
  identity provider derived from the composition's own canonical graph through
  two protected hooks; `settings`, `engine` and `provider` write-once behind
  read-only properties; explicit engine ownership in a new `EngineHandle`) and
  `adapters/web/app.py` (`_require_provider_from()` removed; the routes closed
  over the composition the factory accepted rather than dereferencing
  `app.state` per request), with `tests/web/composition_harness.py` as the
  suite's single substitution path and `tests/web/test_canonical_settings_graph.py`
  as the evidence. The configuration/dependency and test-traceability contracts
  are amended by addition. **No accepted numeric value moved, no environment
  variable was added, renamed or removed, `.env.example` is unchanged, and no
  state machine, logical schema, migration, route, service, worker behaviour,
  runtime grant, deployment value or visual asset changed.** No release boundary
  changes. Phase 3 P3.1 only.
- **Reason.** The independent re-review of C-P3.1-N found three blocking defects,
  all of the same shape: a rule stated where it could be described rather than
  where it could be enforced.
  1. `provider_double: IdentityProvider` refused only a concrete
     `DiscordIdentityProvider`. `IdentityProvider` is a **structural protocol**,
     so a wrapper, a delegating adapter or an alternate implementation holding a
     second graph's client id, secret, redirect URI, scopes, guild and endpoints
     passed that exclusion and then served R-03's authorization URL and R-04's
     token exchange. Naming a parameter "double" is not a type.
  2. `create_app()` called `_require_provider_from()` **once**, while
     `WebComposition.provider` stayed publicly assignable and both routes
     dereferenced it per request. A caller could build the application, replace
     the provider, and make requests through a graph nothing validated; the
     regression offered as proof replaced the provider and called `create_app`
     *again*, so it never tested the actual bypass. Reproduced before the fix:
     an already-built application answered R-03 through a provider assigned
     after startup.
  3. `WebComposition(settings=A, engine=B)` accepted any SQLAlchemy engine.
     C-P3.1-N's recorded reasoning — that `settings.database.url` has one reader,
     so an injected engine cannot disagree with a second consumer — proved the
     wrong thing: with one reader and an injected engine, the configured database
     selection is simply *ignored*, and running S-14/S-15 against B shows B is
     usable, not that B is the database A names. Reproduced before the fix: a
     composition built from a graph naming `freedom_test` served from an engine
     naming another database. That reasoning was explicitly offered for reviewer
     acceptance in C-P3.1-N's recommendations and is **rejected**.
- **Alternatives considered:** keeping the parameter and widening the refusal to
  wrappers (rejected — a structural protocol makes classifying a delegating
  adapter undecidable, and each new exclusion is a blacklist); an environment or
  "test mode" flag selecting the seam (rejected — a magic mode is a production
  code path by another name); a constructor capability token held by test
  infrastructure (considered, and a sound shape; the protected-hook subclass was
  chosen as the smaller design, because reaching it already requires writing a
  subclass and nothing needs to be threaded through the entry point); comparing
  rendered database URLs (rejected — equality still admits two authorities, the
  string may carry credentials, and dialect spellings make the comparison
  unreliable); keeping `_require_provider_from()` as defence in depth (rejected —
  with the provider derived and write-once it detects nothing a supported caller
  can produce, and keeping it would describe a startup comparison as a boundary);
  and leaving the engine parameter with documentation (rejected — the finding is
  precisely that documentation is not a construction rule).
- **Added/removed scope:** none. Two constructor parameters removed, two
  protected construction hooks added, one ownership value object added, one
  startup comparison removed, one test-infrastructure module added, one route
  binding narrowed. No feature, route, environment variable, dependency or worker
  behaviour added.
- **Dependency and critical-path effect:** none beyond the re-review already
  blocking P3.G1. P3.2 and P3.3 remain unstarted.
- **Estimate/forecast and capacity effect:** within the P3.1 remediation
  allowance; no forecast change.
- **New or changed risks:** RAID **I-09 and I-10 amended and both left open**.
  One obligation is recorded rather than silently taken: any future dependency a
  composition needs must be *derived* from the canonical graph or arrive through
  a declared protected hook with stated ownership — a new constructor parameter
  accepting a whole infrastructure object would reintroduce this finding.
- **Testing, migration, security and operational effect:** strictly a tightening,
  applied at construction rather than at startup or per request. Evidence is
  **TC-STRUCT-09** and the amended TC-STRUCT-08 (56 cases in
  `tests/web/test_canonical_settings_graph.py`), **663 portal and 2260 bot tests
  with 0 failed and 0 skipped**, compilation under both configured interpreters,
  `alembic check` reporting no new upgrade operations, `git diff --check` clean
  and the 14-entry visual-freeze manifest verified. **No formatter, linter or
  type checker is configured** — verified by inspection, not assumed. **Four
  falsification runs and two before/after reproductions are recorded rather than
  asserted**, each reverted with a byte-for-byte checksum comparison. **Mutation
  testing was not run and is not claimed**; no mutation tool is configured. No
  migration, deployment, configuration-variable or runtime-grant change; rollback
  is unaffected, because nothing persisted changed shape or meaning.
- **Recommendations:** the Technical Lead asks the implementation review to
  confirm that no supported production construction can supply or replace a
  provider or an engine, and that the protected-hook seam is the smallest design
  that keeps the portal suite runnable; and asks the security review to confirm
  the redaction of every new refusal, that the harness's engine guard is the
  suite's existing contract rather than a second copy of it, and that closing the
  routes over the composition removes the `app.state` route without creating a
  reporting/behaviour divergence that could mislead an operator.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md`.

## C-P3.1-P — Phase 3 P3.G1 request authority and lifecycle (corrects C-P3.1-O)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** the application factory and
  composition root of the web process — `adapters/web/app.py` (a frozen
  `RequestAuthority` built once from the accepted canonical graph and passed into
  route registration and the exception handler; `_settings(request)`,
  `_client_digest`, `_user_agent_digest`, `_origin_is_ours` and `_render` removed;
  `run_resource_checks()` moved out of the factory and into the ASGI lifespan that
  owns the accepted composition) and `adapters/web/composition.py` (`aclose()`
  documented and exercised as the cleanup for a refused startup as well as a normal
  shutdown; the constructor disposes an owned engine when a later construction step
  raises), with `tests/web/lifespan.py`, `tests/web/test_request_authority_and_lifecycle.py`
  and `tests/web/test_canonical_settings_graph.py` as the evidence. The
  configuration/dependency and test-traceability contracts are amended by addition.
  **No accepted numeric value moved, no environment variable was added, renamed or
  removed, `.env.example` is unchanged, no dependency changed, and no state
  machine, logical schema, migration, route, service, worker behaviour, runtime
  grant, deployment value or visual asset changed.** No release boundary changes.
  Phase 3 P3.1 only.
- **Reason.** The independent re-review of C-P3.1-O found two blocking defects and
  one was still outstanding when this work began. Both are the shape RAID I-09 and
  I-10 track — validate one thing, then use another — and both were, additionally,
  claims that had been *described* as general while being established only for one
  object or one path.
  1. **The settings graph was still resolved per request.** C-P3.1-O bound the
     *composition* to the routes and recorded `app.state.settings` as a diagnostic
     reference whose replacement could not affect behaviour. The code disagreed: a
     `_settings(request)` helper read `request.app.state.settings` on every call,
     and the request paths used it for the client and user-agent digests,
     mutation-origin validation, the session and login cookie names and attributes,
     CSRF key selection and the health view. Starlette's `State` is an ordinary
     mutable namespace, so one assignment gave an already-validated application a
     second complete settings graph to serve from — a different accepted `Origin`,
     a different CSRF key, a different cookie contract and different keyed audit
     and rate-limit identities. No private mutation and no unsupported API.
  2. **A refused startup leaked both process-lifetime resources.** `create_app()`
     constructed or accepted the composition, called `run_resource_checks()`, and
     only afterwards built the `FastAPI` object the lifespan is installed on. On
     the production construction path the provider's `httpx.AsyncClient` and the
     owned SQLAlchemy engine and its N-53 pool already existed when that call ran,
     and a refusal raised out of the factory: no application was returned, so no
     lifespan could execute, so `aclose()` had no caller on the one path where the
     process was being told not to run. The lifecycle-ownership claim held for a
     normal shutdown and not for the refusal an operator meets first.
- **Correction.** The authority a handler reads is now an object it **holds**: one
  frozen `RequestAuthority` carrying the accepted graph, the address policy whose
  hop count is fixed at construction, and the Jinja environment whose `autoescape`
  is set once. The four `app.state` references remain as diagnostics and are proved
  inert against a second **independently valid** settings graph, with the structural
  half asserted over the AST rather than reviewed. The resource checks now run
  inside the lifespan, before `lifespan.startup.complete`, closing over the exact
  accepted composition and the same graph object every route reads — so a refusal
  is an ASGI startup failure that never serves a request and still releases what the
  composition holds, and the original typed `ConfigurationError` is what surfaces
  even when releasing the provider also fails. They cross the sync/async seam
  through `run_in_threadpool`, as every other database unit of work in that module
  does. Separately, `WebComposition.__init__` disposes an engine it built if a later
  step raises; a provider constructed and then rejected is deliberately not closed
  there, because a synchronous constructor has no loop to await its `aclose()` on,
  and that limit is recorded rather than papered over.
- **Scope, schedule and risk effect.** No scope, authority, privacy, data-ownership
  or migration change. `create_app()` returning is no longer a statement that the
  resource checks passed — entering the returned application's lifespan is — which
  is a contract change for any future non-serving caller and is recorded in the
  configuration/dependency contract rather than left to be discovered. Risk is
  reduced: a refused portal no longer leaves an HTTP client and a SQLAlchemy pool
  open on a host co-located with three Foundry instances, the live bot and
  PostgreSQL, and no production request or startup path resolves a process-lifetime
  authority through a mutable namespace.
- **Evidence and verification.** TC-STRUCT-10 and TC-STRUCT-11 are added to the
  test-traceability contract by addition; TC-STRUCT-11's stated coverage explicitly
  includes failed-startup cleanup and partial construction, not merely normal
  shutdown. 694 portal tests and 2260 bot tests pass with **no skips and no
  failures** against the guarded disposable PostgreSQL database, run serially
  because both suites share it; `alembic check` reports `No new upgrade operations
  detected.` with the one pre-existing unrelated `SAWarning`; `compileall` passes
  under both required interpreters; `git diff --check` is clean and the 14-entry
  visual-freeze manifest verifies. **No formatter, linter or type checker is
  configured** — re-verified by inspection, not assumed. **Six falsification runs
  are recorded rather than asserted**, each reverted with a byte-for-byte checksum
  comparison. **Mutation testing was not run and is not claimed.** No migration,
  deployment, configuration-variable or runtime-grant change; rollback is
  unaffected, because nothing persisted changed shape or meaning.
- **Defect found in the work being verified.** While running the sweep,
  `tests/web/test_canonical_settings_graph.py` — C-P3.1-N/O's own uncommitted
  evidence — was found to pin its injected clock to a literal
  `datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)`. The repositories stamp
  `created_at` from the real clock, and `ck_oauth_transactions_expiry_after_creation`
  and `ck_webauthn_challenges_expiry_after_creation` refuse a row that expires
  before it was created, so five database cases began failing at 12:00 UTC on the
  day they were written. The constant is now anchored to the run's own clock,
  truncated to the second; **no assertion and no accepted value changed**. Recorded
  here because a suite that expires silently is a control that stops working
  without reporting it.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that no production request or startup path resolves an authority through
  `app.state`, that running the resource checks inside the lifespan preserves every
  property §2.3 promises of them, and that the constructor's engine disposal is the
  smallest correct fix rather than the start of a redesign; and asks the security
  review to confirm that a refused startup transmits no configured secret through
  the surfaced exception, its chained context, the `lifespan.startup.failed`
  traceback or the logs, and that keeping the refusal at the head of the exception
  while attaching a cleanup failure beneath it hides neither failure.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md`.

## C-P3.1-Q — Phase 3 P3.G1 test clock authority (corrects C-P3.1-P's §"Defect found in the work being verified")

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** one test module,
  `tests/web/test_canonical_settings_graph.py` — TC-STRUCT-08's evidence. **No
  production file changed.** The test-traceability contract is amended by
  addition. **No accepted numeric value moved, no environment variable was added,
  renamed or removed, `.env.example` is unchanged, no dependency changed, and no
  state machine, logical schema, migration, route, service, worker behaviour,
  runtime grant, deployment value, provider/engine authority, lifecycle behaviour
  or visual asset changed.** No release boundary changes. Phase 3 P3.G1 only.
- **Reason.** C-P3.1-P recorded a defect found in C-P3.1-N/O's own uncommitted
  evidence — a literal `datetime(2026, 8, 16, 12, 0)` that made five database
  cases start failing at noon — and replaced it with
  `datetime.now(timezone.utc)`. Independent re-review found the replacement was
  not a correction. That instant is captured at **module import**, while
  `created_at` is stamped later by two other authorities:
  `adapters.web.repositories.utcnow()` for `oauth_transactions` (the repository
  supplies the column) and PostgreSQL's `server_default = now()` for
  `webauthn_challenges` (it does not). `expires_at` is derived by the service from
  the injected instant, and `ck_oauth_transactions_expiry_after_creation` and
  `ck_webauthn_challenges_expiry_after_creation` compare the two. The module
  therefore still had **two clock authorities** and a result that depended on
  elapsed wall time; the failure was postponed from a calendar time to "more than
  N-04's ten minutes between import and execution", which collection, an earlier
  case, a debugger pause or a slow CI worker each produce. This is the same shape
  RAID I-09/I-10 track — validate against one thing, use another — appearing in
  the evidence rather than in the code.
- **Change.** The constant is removed. A function-scoped `OperationClock` fixture
  reads the instant from **inside the operation's own transaction** — PostgreSQL's
  `now()` is the transaction timestamp, so the value read *is* what the database
  will stamp `created_at` with — and binds the repository's `utcnow` to that same
  reading for the test, so the application-stamped row shares it too. Every
  original assertion is preserved with `NOW` replaced by the operation's instant,
  including N-04's accepted lifetime, the derived N-06 bound, the relying-party
  scoping, the single-snapshot identity assertions and the encryption-version
  round trip. Nothing sleeps, no lifetime is extended, no constraint is relaxed or
  mocked, PostgreSQL still stamps the WebAuthn row itself, and no timestamp is
  captured at module or session scope — after the change the module has no
  module-level datetime at all, asserted over the AST rather than by reading.
- **Scope, schedule and risk effect.** No scope, authority, privacy,
  data-ownership or migration change. Risk is reduced in one specific way: a
  control that would silently stop working after an unpredictable amount of
  elapsed time is replaced by one whose result does not depend on elapsed time,
  and the two expiry check constraints are now positively exercised rather than
  merely not violated.
- **A production observation, declared and not acted on.**
  `OAuthTransactionRepository.create()` re-reads the clock (`created_at=utcnow()`)
  instead of deriving `created_at` from the `now` the service already used for
  `expires_at`. It is **not** observable as a production defect — every production
  caller injects the same process clock microseconds earlier, so `expires_at` is
  always `created_at` plus the lifetime to within one statement — but it is the
  same "two readings, one operation" shape, and `.agents/AGENTS.md` asks for
  injected clocks. Recorded for the reviewer rather than fixed, because changing it
  would broaden a task scoped to tests. The same paragraph records that
  `oauth_transactions.created_at` comes from the application clock while
  `webauthn_challenges.created_at` comes from the database clock; harmless on one
  host, a question if the database is ever moved off it.
- **Evidence and verification.** TC-STRUCT-08 is amended **by addition** with the
  one-clock requirement and the two regressions it now owns. 696 portal tests and
  2260 bot tests pass with **no skips and no failures** against the guarded
  disposable PostgreSQL database, run serially because both suites share it;
  `alembic check` reports `No new upgrade operations detected.` with the one
  pre-existing unrelated `SAWarning`; `compileall` passes under both required
  interpreters; `git diff --check` is clean and the 14-entry visual-freeze manifest
  verifies 14/14. **No formatter, linter or type checker is configured** —
  re-verified by inspection, not assumed. **Two falsification runs are recorded
  rather than asserted**: restoring the import-time model fails the new
  discriminator on a 1.996-second import-to-execution gap, and the same model with
  the operation clock advanced 11 minutes reproduces the original
  `ck_oauth_transactions_expiry_after_creation` violation across all five formerly
  affected cases; the module was restored byte-for-byte and verified by digest and
  by `cmp`. **Mutation testing beyond those two runs was not run and is not
  claimed.** No migration, deployment, configuration-variable or runtime-grant
  change; rollback is unaffected, because nothing persisted changed shape or
  meaning.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that the timestamp-ownership trace is complete, that binding the transaction's
  own timestamp is the smallest honest correction rather than a broadening, and
  that no assertion's policy meaning changed; and asks the security review to
  confirm that no lifetime, window, constraint or accepted value was relaxed to
  make these cases pass, that both expiry constraints remain exercised against real
  PostgreSQL, and that nothing recorded a secret or a real player datum.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`.

## C-P3.1-S — Phase 3 P3.G1 test-clock AST evidence (corrects C-P3.1-Q's §"Change" claim)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** the same one test module,
  `tests/web/test_canonical_settings_graph.py` — TC-STRUCT-08's evidence. **No
  production file changed.** The test-traceability contract is amended by
  addition for the second time. **No accepted numeric value moved, no environment
  variable was added, renamed or removed, `.env.example` is unchanged, no
  dependency changed** — the guard uses the standard library's `ast` — **and no
  state machine, logical schema, migration, route, service, worker behaviour,
  runtime grant, deployment value, provider/engine authority, lifecycle behaviour
  or visual asset changed.** No release boundary changes. Phase 3 P3.G1 only.
- **Reason.** C-P3.1-Q's §"Change" ended with the words "after the change the
  module has no module-level datetime at all, **asserted over the AST rather than
  by reading**", and the submission it records said the same in §3.1. Fresh
  independent implementation re-review found that **no such assertion existed**:
  the module did not import `ast`, no case in it parsed the module or inspected
  module-scope statements, and a module-import clock could therefore have been
  reintroduced without failing anything. The absence itself was real and
  `OperationClock` was and is technically coherent — the defect was in the
  evidence, not in the fix. It is nevertheless the same shape RAID I-09/I-10
  track, appearing this time in a claim about a check rather than in a check: a
  property established by reading, then described as established by a control.
- **Change.** The claim is made true rather than withdrawn, because a robust
  invariant could be stated. Two cases are added to the module in a new §0.1:
  `test_this_module_captures_no_instant_while_it_is_imported` parses the module
  and fails if any code that runs **at import** reads or constructs an instant,
  and `test_the_import_time_clock_guard_reports_both_forms_and_no_others`
  falsifies the detector against synthetic sources on every run. Import-time is
  taken to mean module-level statements, class bodies, decorator expressions and
  the default arguments of declared functions and lambdas; function, method and
  lambda **bodies**, imports and annotations are deliberately outside it, being
  respectively the operation's own clock, not a clock at all, and unevaluated
  under `from __future__ import annotations`. `timedelta` and `timezone` are not
  findings — a duration and a fixed offset are not instants, and rejecting them
  would have been the brittle detector the alternative resolution warns about.
  Nothing else changed: `OperationClock`, the two clock regressions, N-04's
  accepted lifetime and both live expiry check constraints are untouched.
- **Scope, schedule and risk effect.** No scope, authority, privacy,
  data-ownership or migration change. Risk is reduced narrowly: the two constants
  this module has already carried were each removed by hand, and a third
  reintroduction now fails a case instead of relying on a reviewer's memory.
- **Evidence and verification.** TC-STRUCT-08 is amended **by addition** with the
  AST clause. **Three falsification mutations of the real module are recorded
  rather than asserted**: reintroducing `NOW = datetime.now(timezone.utc)` after
  `pytestmark`, replacing it with the fixed constructor
  `datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)`, and hiding a capture in a
  default argument (`_at=datetime.now(timezone.utc)`) each produced **1 failed, 1
  passed** with the offending line reported; the module was restored from a
  digested copy after each and verified byte-for-byte by `sha256sum -c` **and** by
  `cmp`. The detector inspects AST semantics rather than text, which the clean
  module's **seven** literal occurrences of `datetime.now(timezone.utc)` in
  comments, docstrings and synthetic test inputs make necessary rather than
  stylistic. **698 portal tests and 2260 bot tests pass with no failures and — every
  run executed with `-rs` — no skips**, against the guarded disposable PostgreSQL
  database over its Unix-domain socket, run serially because both suites share it;
  the whole module is 60 passed, the TC-STRUCT-08/10/11 selection 91 passed, and
  the OAuth/WebAuthn/clock selection 575 passed. `git diff --check` is clean,
  `compileall` passes under both required interpreters, the 14-entry visual-freeze
  manifest verifies 14/14, and `git status` lists exactly the entries it listed
  before this correction. **`alembic check` was not re-run and is not re-claimed**
  — no schema, migration, table or model was touched; C-P3.1-Q records its result
  for the work this corrects. **Mutation testing beyond the three recorded runs was
  not performed and is not claimed.** **No formatter, linter or type checker is
  configured**; C-P3.1-Q's inspection stands and was not repeated. No migration,
  deployment, configuration-variable or runtime-grant change; rollback is
  unaffected.
- **An honest limit, declared.** The detector is name-based. A capture reached
  through indirection — `NOW = _read_the_clock()`, where the helper is named
  outside the fifteen-name set — is not seen. Both forms that have actually
  occurred in this module, and the alias form one step from them, are caught.
  Closing the general case would need whole-name resolution or a blanket ban on
  every module-level binding; the latter was considered and rejected as brittle,
  because it would reject a future harmless constant and would state a broader
  invariant than the one claimed.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that the invariant is the one §3.1 now claims and no more, that the
  walked/not-walked boundary is right for "import-time", that excluding
  `timedelta`, `timezone` and annotations is correct rather than convenient, and
  that the three mutations prove the detector rather than merely exercise it; and
  asks the security review to confirm that no lifetime, window, constraint or
  accepted value was relaxed by this correction, that both expiry constraints
  remain exercised against real PostgreSQL, and that nothing in the new code or the
  falsification recorded a secret, a credential or a real player datum.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  §10 of
  `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`.

## C-P3.1-T — Phase 3 P3.G1 import-time clock detector completeness (corrects C-P3.1-S's §"Change" lambda-body claim)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** the same one test module,
  `tests/web/test_canonical_settings_graph.py` — TC-STRUCT-08's evidence. **No
  production file changed.** The test-traceability contract is amended by
  addition for the third time. **No accepted numeric value moved, no environment
  variable was added, renamed or removed, `.env.example` is unchanged, no
  dependency changed** — the guard still uses only the standard library's `ast` —
  **and no state machine, logical schema, migration, route, service, worker
  behaviour, runtime grant, deployment value, provider/engine authority,
  lifecycle behaviour or visual asset changed.** No release boundary changes.
  Phase 3 P3.G1 only.
- **Reason.** C-P3.1-S recorded that the new regression "fails if any code that
  runs **at import** reads or constructs an instant", and listed lambda **bodies**
  among the positions deliberately outside it because "they run when a case calls
  them". Fresh independent implementation re-review read the detector and found
  the two statements incompatible: `visit_Lambda()` always skipped the body, so
  `NOW = (lambda: datetime.now(timezone.utc))()` — a lambda invoked where it is
  written, whose body executes during the import — produced **no finding**. The
  reason given is true of a stored lambda and false of an invoked one. Nothing was
  wrong with `OperationClock`, N-04 or the module's actual state; what was wrong is
  that the control's declared scope exceeded its real scope, which is RAID I-10's
  shape appearing this time inside the check rather than in a claim about it.
- **Change.** The detector is corrected to its stated invariant rather than the
  invariant narrowed to the detector — the handover's preferred resolution, chosen
  because the missed construct is recognisable directly from the AST. A lambda is
  now decided by **when its body runs**: walked where the source shows it invoked
  in place (the callable of an import-time call, including the curried
  `(lambda: lambda: ...)()()`, since parentheses leave no trace in the AST and an
  immediately invoked lambda is simply a `Call` whose callable is the `Lambda`);
  excluded where it is stored, returned or passed, because that body runs when its
  holder calls it; and its defaults walked in both cases, as before. Function and
  method bodies, decorators, class bodies, imports, annotations, `timedelta` and
  `timezone` are unchanged, and no interprocedural or call-graph analysis was
  introduced. A third case,
  `test_the_import_time_clock_guard_reads_an_invoked_lambda_body`, carries the
  reproducer, the curried form, the stored-lambda and passed-lambda negative
  controls, the defaults, and an ordinary call's unchanged walk.
- **Scope, schedule and risk effect.** No scope, authority, privacy,
  data-ownership or migration change. Risk is reduced narrowly and precisely: the
  guard now covers a construct it claimed to cover and did not, and the negative
  controls record where its boundary genuinely is.
- **Evidence and verification.** TC-STRUCT-08 is amended **by addition**, with the
  new clause explicitly **superseding** the earlier lambda-body wording rather than
  editing it. **Before and after are both recorded:** the pre-correction detector
  (reconstructed by disabling only the new `visit_Call`) reports nothing for the
  reproducer, the corrected detector reports `datetime.now` at its source line, and
  the clean module reports nothing under either. **Three falsification mutations of
  the real module** were run after `pytestmark`: the invoked lambda and the curried
  invoked lambda each produced **1 failed, 2 passed** naming
  `test_canonical_settings_graph.py:119 datetime.now`, and a **stored** lambda
  reading the same clock produced **3 passed** — the negative control proving the
  fix did not simply widen the net. The module was restored from a digested copy
  after each and verified byte-for-byte by `sha256sum -c` **and** by `cmp`.
  **699 portal tests and 2260 bot tests pass with no failures and — every run
  executed with `-rs` — no skips**, against the guarded disposable PostgreSQL
  database over its Unix-domain socket, run serially because both suites share it;
  the whole module is 61 passed and the TC-STRUCT-08/10/11 selection 92 passed.
  `git diff --check` is clean, `compileall` passes under both required
  interpreters, the 14-entry visual-freeze manifest verifies 14/14, and
  `git status` lists exactly the entries it listed before this correction.
  **`alembic check` was not re-run and is not re-claimed** — no schema, migration,
  table or model was touched. **Mutation testing beyond the three recorded runs was
  not performed and is not claimed.** **No formatter, linter or type checker is
  configured**; C-P3.1-Q's inspection stands and was not repeated. No migration,
  deployment, configuration-variable or runtime-grant change; rollback is
  unaffected.
- **Honest limits, declared.** The detector remains **name-based**: a capture
  reached through a helper named outside the fifteen-name set is still unseen, as
  C-P3.1-S declared. It is also **syntactic** about invocation: a lambda bound to a
  name and called on the next line (`f = lambda: datetime.now(...)`, then `f()`) is
  not resolved, because doing so is the interprocedural analysis the handover
  excludes. Both are limits of the guard, not of the invariant, and are stated
  rather than implied.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that "invoked where it is written" is the right boundary for a lambda, that the
  curried form is included for the same reason and not by accident, that the
  stored/passed negative controls are the correct other side of that line, and that
  no previously accepted example became a finding; and asks the security review to
  confirm that no lifetime, window, constraint or accepted value was relaxed, that
  both expiry constraints remain exercised against real PostgreSQL, and that neither
  the new case nor the falsification recorded a secret, a credential or a real
  player datum.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  §12 of
  `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`.

## C-P3.1-U — Phase 3 P3.G1 import-time clock detector: named-expression recognition (corrects C-P3.1-T's §"Change" claim that the invoked-lambda rule was fully recognised)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** the same one test module,
  `tests/web/test_canonical_settings_graph.py` — TC-STRUCT-08's evidence. **No
  production file changed.** The test-traceability contract is amended by
  addition for the fourth time. **No accepted numeric value moved, no environment
  variable was added, renamed or removed, `.env.example` is unchanged, no
  dependency changed** — the guard still uses only the standard library's `ast`,
  and `ast.NamedExpr` has existed since Python 3.8 — **and no state machine,
  logical schema, migration, route, service, worker behaviour, runtime grant,
  deployment value, provider/engine authority, lifecycle behaviour or visual asset
  changed.** No release boundary changes. Phase 3 P3.G1 only.
- **Reason.** C-P3.1-T recorded that a lambda is now decided by **when its body
  runs**, walked "where the source shows it invoked in place", and that the
  construct is decidable from the AST with no name resolution. Fresh independent
  implementation re-review read the detector against that claim and found the rule
  right and its recognition incomplete: `_invoked_lambda()` knew only `ast.Lambda`
  and a chain of `ast.Call`, so `NOW = (reader := lambda: datetime.now(timezone
  .utc))()` and the curried `NOW = (factory := lambda: lambda: datetime.now(
  timezone.utc))()()` were reported clean although both bodies execute during the
  import and neither requires a separately stored name to be resolved. Nothing was
  wrong with `OperationClock`, N-04 or the module's actual state; what was wrong is
  that a claim about the control's *reach* was verified against the constructs
  already raised rather than the constructs it claimed to cover — RAID I-10's shape
  one turn further in.
- **Change.** Three lines in the pure helper: a callable position is now read
  **through** an `ast.NamedExpr`, recursively, so a walrus around a direct lambda,
  around a curried lambda, or nested in another walrus is answered by the same
  rule. `(reader := L)` evaluates `L`, binds it as a side effect and answers that
  same object to the call standing beside it in the same expression, so the lambda
  is still invoked where it is written. The unwrapping decides **only whether the
  body runs**: the named expression's target is still walked as import-time code (a
  target that is itself an instant name remains a finding, reported first), the
  bound lambda still reaches `visit_Lambda` for its defaults, and no position is
  reported twice or in a different order. The boundary is stated and closed: a
  **selection** (`(f if flag else g)()` or `(f or g)()`) is not unwrapped because
  the source does not say which body runs, and a name, attribute, subscript,
  container element or argument is not unwrapped because that is the
  interprocedural resolution the handover excludes. Function and method bodies,
  decorators, class bodies, imports, annotations, `timedelta` and `timezone` are
  unchanged. A fourth case,
  `test_the_import_time_clock_guard_sees_through_a_named_expression`, carries both
  reproducers, the preserved target and defaults, the ordinary walrus call, the
  bound-but-not-called and applied-once silences, and the two declared limits as
  explicit controls.
- **Scope, schedule and risk effect.** No scope, authority, privacy,
  data-ownership or migration change. Risk is reduced narrowly and precisely: the
  guard now covers a construct it claimed to cover and did not, and two limits that
  were previously implicit are now asserted as cases and declared in writing.
- **Evidence and verification.** TC-STRUCT-08 is amended **by addition**, with the
  new clause explicitly **superseding in part** the earlier recognition wording
  rather than editing it. **The new case was proved to fail first:** with only the
  three-line branch removed it reports `{'direct': [], 'curried': []}` against the
  expected `datetime.now` findings — the false negative reproduced, not some other
  failure standing in for it. **Before and after are both recorded** over seven
  inputs, the pre-correction detector reconstructed by rebinding only the helper:
  both reproducers `[]` → `datetime.now` at their source line, the real module
  mutated with either reproducer `[]` → line 119, and the clean real module `[]`
  under both. **Three falsification mutations of the real module** were run after
  `pytestmark`: the direct and curried named-expression forms each produced **1
  failed, 3 passed** naming `test_canonical_settings_graph.py:119 datetime.now`,
  and the stored-then-called-by-name control produced **4 passed** — a real
  import-time capture the guard does not see, run as evidence that the fix did not
  widen the net and that the declared limit is real. The module was restored from a
  digested copy after each and verified byte-for-byte by `sha256sum -c` **and** by
  `cmp`. **700 portal tests and 2260 bot tests pass with no failures and — every
  run executed with `-rs` — no skips**, against the guarded disposable PostgreSQL
  database over its Unix-domain socket, run serially because both suites share it;
  the whole module is 62 passed and the TC-STRUCT-08/10/11 selection 93 passed.
  `git diff --check` is clean, `compileall` passes under both required
  interpreters (CPython 3.12.3), the 14-entry visual-freeze manifest verifies
  14/14, and `git status` lists exactly the 17 modified and 8 untracked entries it
  listed before this correction. **`alembic check` was not re-run and is not
  re-claimed** — no schema, migration, table or model was touched. **Mutation
  testing beyond the three recorded runs and the before/after table was not
  performed and is not claimed.** **No formatter, linter or type checker is
  configured**; C-P3.1-Q's inspection stands and was not repeated. No migration,
  deployment, configuration-variable or runtime-grant change; rollback is
  unaffected.
- **Honest limits, declared.** The detector remains **name-based** (C-P3.1-S's
  declaration, unchanged). It remains **syntactic** about invocation, and the true
  edge is now stated: a lambda bound in one statement and called through its name
  in another is a live false negative, asserted as a case so it cannot be mistaken
  for coverage. **New, and disclosed rather than left to be found:** a lambda
  reached through a **selection** in a callable position is not reported either,
  because the source does not say which of the two bodies runs; closing it needs a
  set-valued analysis and belongs to a separately scoped task. The guard is still
  scoped to this one module.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that an `ast.NamedExpr` is a directly evaluated wrapper rather than the excluded
  separately stored name, that the wrapper set is closed rather than opened, that
  the unwrapping removed nothing from the ordinary walk (target and defaults still
  reported, once each, in source order), and that the two declared limits are
  honestly placed; and asks the security review to confirm that no lifetime,
  window, constraint or accepted value was relaxed, that both expiry constraints
  remain exercised against real PostgreSQL, and that neither the new case nor the
  falsification recorded a secret, a credential or a real player datum.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  §14 of
  `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`.

## C-P3.1-V — Phase 3 P3.G1 import-time clock detector: literal conditional selection (corrects C-P3.1-U's §"Change" claim that no selection can be unwrapped)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** the same one test module,
  `tests/web/test_canonical_settings_graph.py` — TC-STRUCT-08's evidence. **No
  production file changed.** The test-traceability contract is amended by addition
  for the fifth time. **No accepted numeric value moved, no environment variable
  was added, renamed or removed, `.env.example` is unchanged, no dependency
  changed** — the guard still uses only the standard library's `ast` — **and no
  state machine, logical schema, migration, route, service, worker behaviour,
  runtime grant, deployment value, provider/engine authority, lifecycle behaviour
  or visual asset changed.** No release boundary changes. Phase 3 P3.G1 only.
- **Reason.** C-P3.1-U recorded that the boundary beside the named-expression
  unwrapping was "stated and closed", with a selection excluded because "the source
  does not say which body runs". Fresh independent implementation re-review found
  that claim false for an AST literal: `NOW = ((lambda: datetime.now(timezone.utc))
  if True else (lambda: None))()` captures an instant at import and the AST names
  the branch that runs, so neither data flow nor a set of possible bodies is
  involved — yet the detector reported it clean, because `_invoked_lambda()` did
  not handle `ast.IfExp` at all. The existing control used `PREFER_UTC`, a **name**,
  as its test, so it exercised only the decidable half of a claim made for every
  selection. Nothing was wrong with `OperationClock`, N-04 or the module's actual
  state; what was wrong is that the guard did not enforce its stated import-time
  invariant and an open boundary was presented as an exact one — RAID I-10's shape
  one turn further in.
- **Change.** Two local, AST-syntactic behaviours. A pure `_literal_selection()`
  answers the conditional's `body` for `ast.Constant` `value is True`, its `orelse`
  for `value is False`, and `None` otherwise; `_invoked_lambda()` recurses through
  it, so a literal selection composes with the lambda, call and named-expression
  chain already supported rather than being special-cased beside it. The helper
  still answers **one** body or none — its contract is unchanged and no set-valued
  analysis was introduced. A `visit_IfExp` preserves ordinary evaluation: the test
  always runs and is always walked; the branches are walked as Python evaluates
  them, both when the test is not a literal and the selected one alone when it is,
  because the unselected expression is never evaluated and so builds no lambda and
  runs none of its defaults. The boundary is **identity, not truthiness**: `1`,
  `1.0`, `'yes'`, `(0,)`, `None`, a comparison, a `not`, a name and `ast.BoolOp`
  are all left exactly where they were. Function and method bodies, decorators,
  class bodies, imports, annotations, `timedelta` and `timezone` are unchanged. A
  fifth case,
  `test_the_import_time_clock_guard_selects_a_literal_conditional_branch`, carries
  both reproducers, a clock in each selectable branch, the dead branch proved dead
  at a lambda default with its live counterpart beside it, a clock in the
  condition, the curried and walrus compositions, and eight non-literal tests as
  explicit limits. The preserved name-conditioned control is unchanged in behaviour
  and its comment corrected.
- **Scope, schedule and risk effect.** No scope, authority, privacy,
  data-ownership or migration change. Risk is reduced narrowly: the guard now
  covers a construct its own boundary statement wrongly excluded, and the limit
  that genuinely remains is stated where the earlier over-claim stood.
- **Evidence and verification.** TC-STRUCT-08 is amended **by addition**, with the
  new clause explicitly **superseding in part** the earlier conditional-expression
  wording rather than editing it. **The new case was proved to fail first:** with
  only the helper branch removed it reports `{'true': [], 'false': []}` against the
  expected findings — the false negative reproduced, not some other failure
  standing in for it. **Before and after are both recorded** over six inputs, the
  pre-correction detector loaded from the previous module's own definitions: both
  reproducers `[]` → `datetime.now` / `datetime.utcnow`, the name-conditioned and
  truthy-constant controls `[]` under both, and the clean real module `[]` under
  both. **One row reports less and is disclosed rather than left to be found:** a
  capture written in a branch the source proves dead is no longer reported, because
  Python never evaluates that expression. **Three falsification mutations of the
  real module** were run after `pytestmark`: the literal-`True` and literal-`False`
  positives each produced **1 failed, 4 passed** naming
  `test_canonical_settings_graph.py:119`, and the name-conditioned control produced
  **5 passed** — a real import-time capture the guard does not see, run as evidence
  that the fix did not widen the net. The literal-`False` run carries independent
  corroboration that the mutated module executed a clock during its import: CPython
  itself emitted `DeprecationWarning: datetime.datetime.utcnow() is deprecated` at
  line 119 during collection. The module was restored from a digested copy after
  each and verified byte-for-byte by `sha256sum -c` **and** by `cmp`. **701 portal
  tests and 2260 bot tests pass with no failures and — every run executed with
  `-rs` — no skips**, against the guarded disposable PostgreSQL database over its
  Unix-domain socket, run serially because both suites share it; the whole module
  is 63 passed and the TC-STRUCT-08/10/11 selection 94 passed. `git diff --check`
  is clean, `compileall` passes under both required interpreters (CPython 3.12.3),
  the 14-entry visual-freeze manifest verifies 14/14, and `git status` lists exactly
  the 17 modified and 8 untracked entries it listed before this correction.
  **`alembic check` was not re-run and is not re-claimed** — no schema, migration,
  table or model was touched. **Mutation testing beyond the three recorded runs and
  the before/after table was not performed and is not claimed.** **No formatter,
  linter or type checker is configured**; C-P3.1-Q's inspection stands and was not
  repeated. No migration, deployment, configuration-variable or runtime-grant
  change; rollback is unaffected.
- **Honest limits, declared.** The detector remains **name-based** and remains
  **syntactic** about invocation; a lambda bound in one statement and called
  through its name in another is still a live false negative, asserted as a case.
  **Narrowed, not removed:** a selection is unwrapped only when its test is an
  exact boolean literal, so `((lambda: datetime.now(...)) if flag else (lambda:
  None))()` still executes one of two bodies at import and is still not reported.
  Closing *that* needs the data-flow or set-valued analysis this task excludes;
  closing the literal case did not. The guard is still scoped to this one module.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that an exact boolean literal makes the selected branch decidable from the one
  node, that identity rather than truthiness is the right boundary, that walking
  the test always and the dead branch never is correct and that the resulting
  single behaviour removal is a false-positive removal rather than a narrowed
  invariant, and that the preserved control is now described accurately; and asks
  the security review to confirm that no lifetime, window, constraint or accepted
  value was relaxed, that both expiry constraints remain exercised against real
  PostgreSQL, and that neither the new case nor the falsification recorded a
  secret, a credential or a real player datum.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  §16 of
  `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`.

## C-P3.1-W — Phase 3 P3.G1 composition lifecycle claimed once (corrects C-P3.1-P's lifecycle contract, which guarded only the way out)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and P3.3 have
not started.*

- **Affected requirement, milestone and release:** `adapters/web/composition.py`,
  `adapters/web/app.py` and `tests/web/test_request_authority_and_lifecycle.py` —
  TC-STRUCT-11's subject and evidence. The test-traceability contract is amended by
  addition. **No accepted numeric value moved, no environment variable was added,
  renamed or removed, `.env.example` is unchanged, no dependency changed, and no
  logical schema, migration, route, view model, service, repository, worker
  behaviour, runtime grant, deployment value, provider/engine authority or visual
  asset changed.** No release boundary changes. Phase 3 P3.G1 only.
- **Reason.** C-P3.1-P wired `WebComposition.aclose()` to the ASGI lifecycle and
  recorded the lifecycle contract as complete. Fresh independent implementation
  re-review (`docs/review/Handover information`, 2026-08-16) found it complete in
  one direction only. `aclose()` is **permanent** — it closes the provider's HTTP
  client and disposes an owned engine — and the lifespan performed no
  live-or-closed check on the way *in*. A composition passed to two applications,
  or one application whose lifespan was entered again, answered
  `lifespan.startup.complete` and began serving with a closed Discord client
  behind R-03 and R-04; the first failure would have been an OAuth request, not a
  startup. The resource checks were no defence and could not become one: they never
  receive the provider, and `Engine.dispose()` does not invalidate an engine but
  discards its pool, so S-14 opens a connection through the replacement and reports
  a healthy database. **The suite had codified the unsafe outcome**: the
  repeated-shutdown case entered a second lifespan over a closed composition and
  *required* `lifespan.startup.complete` from it, reading as repeated-shutdown
  idempotency while asserting a new startup after shutdown. This is RAID I-09's
  shape in its lifecycle form — release one way, admit the other — and getting the
  exit right is precisely what made the entry look already handled.
- **Change.** An explicit, one-way lifecycle on the composition root.
  `CompositionLifecycle` is `NEW -> STARTED -> CLOSING -> CLOSED`; `_lifecycle`
  replaces the `_cleanup_started` boolean, which could say whether cleanup had
  begun but not whether a startup was permitted, so one attribute now answers both
  and the two cannot disagree. `claim_for_startup()` is the only transition out of
  `NEW` and raises the new `CompositionLifecycleError` — a `RuntimeError`, because
  nothing is wrong with the configuration, only with *when* — from every other
  state. `__setattr__` refuses any non-forward write to `_lifecycle`, the analogue
  of the write-once rule for an attribute that has to move: a spent composition
  cannot be reset to `NEW` and re-claimed with its provider closed. The lifespan
  calls the claim as its **first** statement, before the resource checks (which
  cannot detect the condition) and **outside** the cleanup `try` — a composition
  this application was refused is not this application's to close, and cleaning up
  underneath a claimant that is still serving would turn a caller's mistake into an
  outage. `aclose()`'s contract is otherwise unchanged: at most once, guard moved
  before the first `await`, owned engine disposed in a `finally` even when the
  provider raises, lent engine untouched, failure re-raised. `create_app()` still
  builds two applications from one composition without complaint, because the
  factory opens and closes nothing; only one of them can start.
- **Scope, schedule and risk effect.** No scope, authority, privacy,
  data-ownership or migration change. Risk is reduced: a portal can no longer
  report a completed startup and then serve OAuth against a closed transport, and
  the refusal is visible to the server as `lifespan.startup.failed` rather than to
  a caller of the factory.
- **Evidence and verification.** TC-STRUCT-11 is amended **by addition**. The
  case that codified the defect is corrected to two shutdown paths and carries a
  note saying why the third was removed; six new cases assert the opposite outcome —
  a second application over a closed composition, a second entry of the *same*
  application's lifespan, a startup attempted while the first is still serving
  (with R-03 then driven through the live provider to show it was left alone), the
  claim proved to run before any resource check, the refusal proved to name no
  configured value across the exception, its context chain and the
  `lifespan.startup.failed` traceback, and `NEW -> CLOSING -> CLOSED` for a
  composition discarded before it served. Every case drives the real ASGI lifespan
  protocol. **Five falsification mutations** of the real production files: removing
  the claim call **7 failed**, moving it after the checks **2 failed**, moving it
  inside the cleanup `try` **1 failed** (the live claimant's provider closed by a
  second application's failed startup — the outage case), removing the forward-only
  `__setattr__` guard **1 failed**, and a pure no-op `claim_for_startup()` **7
  failed**. **A sixth mutation killed nothing and is disclosed rather than
  omitted:** neutralising only the refusal while leaving the `STARTED` write in
  place produced **37 passed**, because the monotonic `__setattr__` guard refuses
  the second `STARTED -> STARTED` write from the other direction; the two mechanisms
  cover each other, which is why the fifth mutation removes both. Every mutation was
  reverted and both files verified by `sha256sum -c` **and** `cmp`. **707 portal
  tests and 2260 bot tests pass with no failures and — every run executed with
  `-rs` — no skips**, against the guarded disposable PostgreSQL database over its
  Unix-domain socket, run serially because both suites share it; the lifecycle
  module alone is 37 passed. `git diff --check` is clean and `compileall` passes.
  **`alembic check` was not re-run and is not re-claimed** — no schema, migration,
  table or model was touched. **Mutation testing beyond the six recorded runs was
  not performed and is not claimed.** **No formatter, linter or type checker is
  configured**; C-P3.1-Q's inspection stands and was not repeated. No migration,
  deployment, configuration-variable or runtime-grant change; rollback is
  unaffected.
- **Honest limits, declared.** The claim is a **single-process** rule: two uvicorn
  workers each build their own composition, which is correct and unchanged, and
  N-53's pool arithmetic remains per-process. It is a check-and-set with no `await`
  between test and write, so it is safe against concurrent lifespans on one event
  loop — the only concurrency this application has — and is **not** thread-safe and
  not claimed to be. `CLOSING` is not asserted directly by any case, because there
  is no suspension point one could reliably observe it from without instrumenting
  the provider; the states either side of it are asserted.
- **Recommendations:** the Technical Lead asks the implementation review to confirm
  that a state transition on the way in is the right correction rather than a check
  inside `run_resource_checks`, that the claim belongs outside the cleanup `try`,
  that a monotonic `_lifecycle` is the right analogue of the write-once rule for an
  attribute that must move, and that closing an unclaimed composition
  (`NEW -> CLOSING`) is correct rather than an omission; and asks the security
  review to confirm that no lifetime, window, constraint or accepted value was
  relaxed, that a refused claim releases nothing belonging to a serving
  application, that neither `CompositionLifecycleError` nor the
  `lifespan.startup.failed` traceback carries a configured value, and that a
  refused startup remains incapable of serving a request.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see
  §8 of
  `docs/review/phase-3-p3-g1-composition-lifecycle-claim-remediation-submission-2026-08-16.md`.

## C-P3.1-X — Phase 3 P3.G1 break-glass attempt budgets survive the refusals they count (corrects the N-32 per-account budget, which had no production caller, and the N-33 per-grant counter, which rolled back with every refused matched grant)

**Date:** 2026-08-16 · **Recorded for:** Peter Duscha (Product Owner, Security
Reviewer and Acceptance Authority) · **Status:** *Submitted for fresh independent
security re-review. Not accepted. P3.G1 and RAID I-09/I-10 remain open. P3.2 and
P3.3 have not started.*

- **Affected requirement, milestone and release:** `application/web/rate_limit.py`,
  `application/web/breakglass.py`, `adapters/web/app.py` (R-08, R-09),
  `adapters/web/repositories.py` (`RecoveryGrantRepository.note_attempt`),
  `tests/web/test_break_glass_login.py` and
  `tests/web/test_settings_construction_validation.py` — N-32 and N-33 as the
  numeric register already accepts them. The test-traceability contract is amended
  by addition (TC-BG-16, TC-BG-17). **No accepted numeric value moved, no
  environment variable was added, renamed or removed, `.env.example` is unchanged,
  no dependency changed, and no logical schema, migration, route, view model,
  worker behaviour, runtime grant, deployment value, provider/engine authority or
  visual asset changed.** No release boundary changes. Phase 3 P3.G1 only.
- **Reason.** The distinct security-focused review
  (`docs/review/phase-3-p3-g1-security-review-2026-08-16.md`, 2026-08-16) returned
  two `[Blocking]` findings, both accepted without qualification. **N-32's second
  budget had no production caller**: `RateLimiter.check_account()` was implemented,
  validated and unit-tested, and no HTTP request ever reached it, so WebAuthn
  assertion attempts distributed over fresh source addresses were bounded only by
  the five-per-address budget and the accepted ten-per-account, sixty-minute budget
  was inoperative. **N-33's per-grant counter was inside the transaction it was
  bounding**: `redeem_recovery_grant()` incremented `recovery_grants.attempt_count`
  and R-09 ran the whole call inside `_in_transaction()`, so an attempt matching a
  real but expired, invalidated or already-consumed grant updated the row, failed
  `consume()`, and rolled the update back — the cap could be walked past from new
  addresses while only the per-IP counter advanced. This is RAID I-09's shape
  twice: the control exists and the path does not reach it, masked in both cases by
  a per-address budget that does work.
- **Alternatives considered.** (a) Leaving the account budget to a later package —
  refused: N-32 is an accepted P3.1 number and an unenforced one is worse than an
  absent one, because the register reads as satisfied. (b) Charging the account
  budget inside `complete_assertion()` — refused: that transaction is rolled back
  by every refusal, which is the same defect in a new place. (c) Spending nothing
  for a credential that resolves to no account — refused: it makes the eleventh
  attempt against an enrolled credential distinguishable from the eleventh against
  an invented one, which is the account-existence oracle `begin_assertion()` exists
  to avoid; an equivalent keyed per-credential budget was added instead. (d)
  Keeping the per-grant increment in the service and raising as before — refused
  for the reason the finding gives; the service method now **returns** its refusal
  so the caller's transaction commits the increment.
- **Change.** `RateLimiter.check_credential()` added, spending the same configured
  N-32 limit and window in a keyed per-credential bucket.
  `BreakGlassService.assertion_subject()` added: one row read, nothing verified,
  nothing written, nothing raised. `BreakGlassService.note_recovery_attempt()`
  added, returning `AuthenticationFailure | None`. R-08 and R-09 each call one new
  `adapters/web/app.py` helper that runs the consumption in **its own** transaction,
  beside the existing `_consume_rate_limit()` and for the identical reason.
  `redeem_recovery_grant()`'s increment becomes a read-only fail-closed check.
  `note_attempt()` becomes one `UPDATE … RETURNING attempt_count` statement, so the
  increment and the reading of it are the same operation. `complete_assertion()`
  and `assertion_subject()` share one credential-id reader; a non-`dict` JSON body
  now takes the ordinary `403 invalid` path instead of the generic 500 handler.
- **Added/removed scope.** Added: two limiter/service consumption paths, one
  limiter method, one repository return value, five test cases, two traceability
  rows. Removed: nothing. **No route, capability, lifetime, window, constraint or
  accepted value was relaxed**, and every refusal a caller can see keeps the code
  it had.
- **Dependency and critical-path effect.** None. P3.G1 remains the gate; P3.2 is
  still not authorized.
- **Testing, migration, security and operational effect.** TC-BG-16 and TC-BG-17
  are new, both **direct HTTP against real PostgreSQL**, both spending their budget
  from several source addresses because that is the attack the per-address halves
  do not bound. The overstated per-grant case is renamed
  `test_a_token_matching_no_grant_counts_against_no_grant_record` and re-scoped to
  the property it actually held. **712 portal and 2260 bot tests pass with no
  failures and no skips**, run serially against the guarded disposable PostgreSQL
  database over its Unix-domain socket. Four falsification mutations were killed —
  including one that reintroduces the original rollback mechanism at the new
  boundary — and every mutation was reverted and verified byte-for-byte.
  `git diff --check` is clean. **`alembic check` was not re-run and is not
  re-claimed**: no schema, migration, table or model was touched, and
  `recovery_grants.attempt_count` is unchanged. **Mutation testing beyond the four
  recorded runs was not performed and is not claimed.** **No formatter, linter or
  type checker is configured**; C-P3.1-Q's inspection stands and was not repeated.
  No migration, deployment, configuration-variable or runtime-grant change;
  rollback is unaffected.
- **New or changed risks.** RR-03's fixed-window 2× boundary burst now applies to
  the per-account budget as well as the per-address ones; that is the accepted cost
  of N-30's algorithm rather than a new decision, and it is disclosed rather than
  smoothed over. The per-credential bucket is genuinely new storage in
  `auth_rate_limits`, bounded by the per-address budget that runs before it and
  swept by N-31.
- **Honest limits, declared.** R-08 now reads the credential row twice — once to
  charge the budget in a committed transaction, once inside the verification
  transaction that authorizes — and that is deliberate rather than an oversight.
  `redeem_recovery_grant()` no longer counts, so direct service callers do not
  advance the per-grant counter; the route is its only production caller and the
  read-only cap check keeps the service fail-closed. No concurrency case was added
  for either counter.
- **Recommendations:** the Technical Lead asks the security review to confirm that
  consuming the account budget after credential resolution and before verification
  is the right boundary; that the per-credential fallback removes the oracle rather
  than moving it; that returning a refusal instead of raising it is the right way
  to keep an increment committed; that no refusal code, audit payload or response
  shape now discloses more than it did; and that the read-only per-grant check left
  in the service is a safeguard rather than a second authority.
- **Approval:** **Not yet decided.** Recorded for the Acceptance Authority; see §9
  of
  `docs/review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md`.

## C-P3.1-Y — P3.1 and stop gate P3.G1 accepted after complete independent and security re-review

**Date:** 2026-08-16 · **Decision:** Peter Duscha, Acceptance Authority and
accountable Security Reviewer · **Status:** **Accepted; P3.G1 closed; P3.2
authorized.**

- **Affected requirement, milestone and release:** the complete P3.1
  authentication/security foundation and P3.G1 gate, including migrations
  0006–0009, OD-44, session lifetime and numeric policy, canonical settings and
  dependency authority, startup/lifecycle ownership, N-32 and N-33. No product
  scope, accepted numeric value, route, schema, dependency or release boundary
  changes in this decision.
- **Reason and review:** Codex completed the independent implementation re-review
  and distinct security-focused pass recorded in
  `docs/review/phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md`.
  No remaining blocking or important implementation or security finding was
  identified. Peter accepted the recommendation.
- **Evidence:** 712 portal tests and 2260 bot tests passed with no skips against
  the guarded disposable PostgreSQL database; changed Python modules compiled;
  `git diff --check` was clean. Historical mutation evidence was inspected but
  not all mutation runs were repeated. No formatter, linter or type checker is
  configured.
- **Evidence correction:** TC-BG-16 proves the same externally meaningful
  outcomes for enrolled and invented credential IDs: status and coarse error
  code at the same attempt under the same configured window. Literal response
  bodies are not identical because correlation identifiers are intentionally
  unique, and literal `Retry-After` equality is timing-dependent and not claimed.
- **Dependency and critical-path effect:** P3.G1 is closed and P3.2 may begin.
  P3.3 remains behind P3.G2; this decision does not bypass any later stop gate.
- **RAID effect:** I-07, I-09 and I-10 are closed by the completed evidence,
  review and acceptance. **I-06 remains open:** staging, browser and real-device
  evidence is still unavailable and is required before staging/production
  exposure and final Phase 3 production-readiness acceptance. **A-05 remains
  open:** the implementation is accepted, but two real WebAuthn credentials must
  be validated on the deployment host before public staging/production exposure.
- **Approval:** Peter Duscha accepted P3.1 and closed P3.G1 on 2026-08-16.

## C-P3.2-A — P3.2 identity-link confirmation activates immediately; C-05 withdrawn; Google is legacy migration input only

**Date:** 2026-08-17 · **Requester and Decision:** Peter Duscha, Maintainer,
Product Sponsor and Acceptance Authority · **Status:** **Decision effective; P3.G2
remains open.**

- **Affected requirement, milestone and release:** P3.2 and stop gate P3.G2.
  `docs/contracts/phase-3-identity-migration-contract.md` §7.2, §7.3, §7.4, §7.5
  and new §7.7; `docs/contracts/phase-3-route-authorization-contract.md` §5.1
  (R-28–R-30) and §8 (command register); `docs/contracts/phase-3-test-traceability.md`
  TC-MIG-09, TC-MIG-11, TC-MIG-13 and new TC-MIG-17/TC-MIG-18;
  `docs/contracts/phase-3-view-model-contract.md` VM-10. No route is added or
  removed, no capability changes, no phase order changes and no release boundary
  moves.

- **Reason and alternatives considered.** Three accepted documents disagreed about
  where the `character_access` row is written. §7.2 of the migration contract put
  it in a third pipeline step, `C-05 --apply`; §7.5 of the same document, §5.1 of
  the route contract and TC-MIG-09/11/13 all put it at the Council confirmation.
  The P3.2 implementation followed §7.2, and the previous submission raised the
  contradiction rather than resolving it, which was correct. The maintainer has now
  resolved it in favour of **immediate activation**: a Guild Council confirmation
  at R-29 creates the link. The alternative — keeping the deferred apply — was
  rejected because it makes an authorization depend on an operator remembering to
  run a second command, leaves confirmed-but-inactive links visible to Council as
  though they were decisions already carried out, and adds an apply state, an apply
  vocabulary and a superseded-run rule that exist only to manage that gap.

- **Added scope.** Nothing. R-29 gains the write it already had in three of the
  four controlled passages.

- **Removed scope.** Command **C-05** (`python -m tools.identity_migration
  --apply`) is withdrawn; its identifier is retired, not reused. The deferred-apply
  architecture is removed with it: the apply service, the recorded-decision
  authority object and the migration-only grant-authority protocol, the
  `--apply`/`--run-id` command surface and its report, and the apply-state columns,
  constraints, repository methods, view-model fields and template states. Migration
  0010 is uncommitted in the P3.2 worktree and is rewritten to describe the final
  approved schema; **no applied migration (0001–0009) is edited**.

- **Further decisions recorded in the same ruling.**
  1. Google Sheets is **legacy migration input**, not an ongoing platform
     component, operational database or portal dependency. Nothing in this
     workflow writes to Google.
  2. C-04 remains a **temporary** migration/import utility, run from a separate
     operator environment provisioned with the Google client libraries and a
     read-only credential. The Google packages stay out of `requirements-web.txt`
     and its lock file; the portal and the normal PostgreSQL-backed runtime must
     not need them.
  3. Imported data is verified in PostgreSQL; the legacy Google access is retained
     only for the approved verification/rollback window and is then retired.
  4. C-04 must accept the real player-tab name explicitly. `--player-tab` becomes a
     **required** argument: `docs/discovery/sheet-inventory.md` §2.1 records the
     tab's columns but not its name, and an unverified default presented as
     operational truth is how a run reads the wrong range.
  5. The policy question of multiple active Discord identities for one platform
     account (submission D6) remains **deferred**; the current fail-closed
     behaviour is retained.

- **Blocking defect fixed under this entry.** The independent review reproduced an
  identity-integrity defect in `application/web/identity_evidence.py`: the player
  join was a dict comprehension keyed by normalized player name, so two Sheet rows
  such as `Ada` and `ADA` collided silently and the later row decided the
  confirmable Discord identity. That is not a product decision and is not
  resolvable by choosing a row. Migration contract §7.3.1 now requires the whole
  C-04 run to be **refused** when two player-tab rows share one normalized key, so
  no partial run is written and no control total can hide the duplicate.

- **Dependency and critical-path effect.** None outside P3.2. P3.3 remains behind
  P3.G2 and this decision bypasses no stop gate.

- **Estimate/forecast and capacity effect.** One remediation cycle inside the P3.2
  package, plus the independent and security-focused re-review P3.G2 already
  required. No phase target range changes.

- **New or changed risks.** *Reduced:* an authorization can no longer sit in a
  confirmed-but-unwritten state, and an identity can no longer be decided by Sheet
  row order. *Retained:* R-29 now writes an authorization on a request path, so its
  request-boundary controls, live capability resolution, optimistic concurrency and
  atomic audit are the controls that matter and must be evidenced at P3.G2.
  *Operational:* C-04 cannot be run from `venv-web`, by design; §7.7's separate
  operator environment is a documented prerequisite of running the migration at
  all.

- **Testing, migration, security and operational effect.** The F6 test material
  around `C-04 → R-28 → R-29/R-30 → C-05` is rewritten around
  `C-04 → R-28 → R-29/R-30`. Migration 0010 describes the final schema and is kept
  exactly aligned with `adapters/database/tables.py`. The guarded backup/restore
  drill and its disposable-target guard are unchanged and unweakened.

- **Product Owner recommendation.** Peter Duscha, as Product Owner, directed the
  remediation in `docs/review/Handover information` (2026-08-17).

- **Technical Lead and specialist reviews.** Implemented by the working Technical
  Lead (Claude) and recorded in `docs/review/phase-3-p3-2-submission.md`.
  **Independent implementation review and a distinct security-focused review are
  still required**, by a reviewer that did not implement the work.

- **Approval:** the workflow, dependency and defect rulings above are **accepted by
  Peter Duscha on 2026-08-17** and are effective. **P3.G2 is not approved by this
  entry** and remains open pending the re-reviews and an explicit maintainer
  acceptance.

## C-P3.2-B — Confirm the one-time C-04 player-tab input as `Players`

**Date:** 2026-08-17 · **Requester and Decision:** Peter Duscha, Maintainer,
Product Sponsor and Acceptance Authority · **Status:** **Operational input
confirmed; P3.G2 remains open.**

- **Affected requirement, milestone and release:** P3.2 C-04 only. The command,
  identity-migration contract §7.7, route-contract command register, Sheet
  inventory, operator runbook and P3.2 submission now name `Players` as the
  confirmed one-time legacy input tab. No route, schema, capability, phase order,
  release boundary or production behavior changes.
- **Reason and alternatives considered:** C-P3.2-A correctly removed an
  unverified hard-coded `Players` default and required the operator to supply the
  real tab name. Peter has now supplied that fact: **`Players`**. Restoring a code
  default was rejected because it would turn temporary migration input into
  enduring runtime configuration and weaken the explicit wrong-tab guard.
- **Added/removed scope:** no product scope is added. One unresolved operator
  input is closed. `--player-tab Players` remains mandatory. C-04 remains
  temporary and read-only; C-05 remains withdrawn.
- **Dependency and critical-path effect:** the missing tab-name prerequisite is
  removed. The separate Google-enabled operator environment, PostgreSQL
  verification, rollback window and Google retirement remain controls. P3.3
  remains behind P3.G2.
- **Estimate/forecast and capacity effect:** documentation-only clarification; no
  estimate or target-range change.
- **New or changed risks:** wrong-tab risk is reduced by recording the exact name
  while retaining the explicit argument and operator verification. No Google
  dependency is added to the portal or bot.
- **Testing, migration, security and operational effect:** no migration or code
  behavior changes. Documentation checks and existing C-04 parser tests are
  sufficient for this record; a live Sheet run remains prohibited until
  separately authorized and must follow the runbook.
- **Product Owner recommendation and approval:** Peter Duscha supplied and
  approved `Players` as the exact one-time C-04 source tab on 2026-08-17.
- **Technical Lead and specialist reviews:** this documentation correction remains
  part of the P3.2 worktree subject to independent implementation and distinct
  security-focused re-review.
- **Gate effect:** this entry **does not approve P3.G2**. Only explicit maintainer
  acceptance after the required re-reviews can close that gate.

## C-P3.2-C — R-28 reports current linkage; a decided proposal must state its reason

**Date:** 2026-08-17 · **Requester:** Independent Reviewer, P3.2 implementation
review (findings 1 and 2) · **Decision:** Peter Duscha, Maintainer, Product Owner
and Acceptance Authority · **Status:** **Decision effective; P3.G2 remains open.**

- **Affected requirement, milestone and release:** P3.2 and stop gate P3.G2.
  `docs/contracts/phase-3-identity-migration-contract.md` §7.4 and §7.5;
  `docs/contracts/phase-3-view-model-contract.md` VM-10;
  `docs/contracts/phase-3-route-authorization-contract.md` §5.1 (R-28);
  `docs/contracts/phase-3-test-traceability.md` new TC-MIG-19 and TC-MIG-20;
  uncommitted migration 0010 and `adapters/database/tables.py`. **No route is
  added or removed, no capability changes, no authority moves, no phase order
  changes and no release boundary moves.** The `resolution` vocabulary is
  unchanged and gains no value.

- **Reason and alternatives considered.** The independent review reproduced two
  defects.

  *Finding 1 (blocking).* R-28 read a proposal's historical `confirmed`
  resolution as proof that its link was still active. §7.5 has always made R-26
  revocation a supported compensating action, so after a revocation the page told
  a Council member that a link *"is active now"* when the `character_access` row
  it named was inactive, and counted it in the total §7.4 defines as **active
  links**. The controlled language could not express the resulting state: §7.4
  defined `confirmed` as active links, VM-10 said *"four states and no fifth"*,
  and a confirmed-then-revoked proposal is neither an active link nor a
  rejection — so it also fell out of the second balance. Two resolutions were
  considered. The one adopted keeps §7.4's *"`confirmed` counts active links"*
  sentence intact and adds a balanced `confirmed_revoked` bucket beside it, so the
  headline total a Council member reads is the number of links that exist. The one
  rejected made `confirmed` the historical decision count and demoted
  active/revoked to non-balancing sub-totals; it changes less arithmetic but
  leaves the most prominent number on the screen unable to answer *"how many links
  did this run produce?"* without reading a sub-total, which is the same class of
  misreading the finding is about.

  *Finding 2 (important).* Migration 0010 enforced only
  `decision_reason IS NULL OR length(trim(decision_reason)) > 0`, so `confirmed`
  and `rejected` rows with a null reason were storable. R-29 and R-30 both require
  a reason and the service validates one, but the restricted runtime role holds
  `UPDATE` on `identity_link_proposals`, so a rule held only in the service was one
  direct statement away from a half-decided authorization record. Relying on
  service validation, or narrowing the runtime grant, were both rejected: the first
  is the gap, and the second would break C-04's own retention `DELETE` and the
  decision transitions the application must make.

- **Added scope.** `MigrationTotals.confirmed_revoked` and
  `LinkProposal.link_state` in VM-10; a `confirmed-and-revoked` rendering on R-28;
  two bounded repository queries; one check constraint,
  `ck_identity_link_proposals_a_decision_states_its_reason`; TC-MIG-19 and
  TC-MIG-20. No new route, form, control, capability or column.

- **Removed scope.** Nothing.

- **What is explicitly preserved.** A revoked confirmation is **counted, not
  re-decided**: `resolution` stays `confirmed`, is never rewritten to `rejected`,
  never returned to `outstanding`, and keeps its `decided_at`,
  `decided_by_account_id`, `decision_reason`, `granted_access_id` and both audit
  events. Activation is read from that exact `granted_access_id` joined to
  `character_access.active` and is never inferred from another active link on the
  same character or account. VM-10's *"no fifth state"* rule is preserved in the
  sense it was written for — there is still no `confirmed but not applied` state,
  no apply outcome and no apply total — and the heading is clarified to say *four
  **decision** states*, because the new field reports the current state of an
  access row rather than a sixth decision.

- **Dependency and critical-path effect.** None outside P3.2. P3.3 remains behind
  P3.G2 and this decision bypasses no stop gate.

- **Estimate/forecast and capacity effect.** One remediation cycle inside the
  existing P3.2 review/remediation allowance, plus the independent and
  security-focused re-review P3.G2 already required. No phase target range
  changes.

- **New or changed risks.** *Reduced:* R-28 can no longer report a revoked
  authorization as active, which was a misreading with direct authorization
  consequences for a Council member deciding whether someone still has access; and
  the database can no longer hold a decision without the reason the audit trail
  depends on. *Retained:* R-28's totals are now derived from two queries rather
  than one, so `MigrationTotals.balances()` is the control that keeps them
  consistent and is asserted on every new case.

- **Testing, migration, security and operational effect.** TC-MIG-19 and TC-MIG-20
  are new and both were shown to **fail before the fix and pass after it**.
  Migration 0010 is still uncommitted in the P3.2 worktree and is corrected in
  place; **no applied migration (0001–0009) is edited**, and the revision's
  `upgrade → downgrade → upgrade` round trip and migration/metadata parity checks
  still pass. No runtime grant is weakened or widened. No operational or
  deployment step changes.

- **Product Owner recommendation.** Peter Duscha, as Product Owner, directed the
  remediation in `docs/review/Handover information` (2026-08-17) and selected the
  adopted representation over the alternative on the same date.

- **Technical Lead and specialist reviews.** Implemented by the working Technical
  Lead (Claude) and recorded in `docs/review/phase-3-p3-2-submission.md`.
  **Independent implementation review and a distinct security-focused review are
  still required**, by a reviewer that did not implement the work.

- **Approval:** the representation ruling above is **accepted by Peter Duscha on
  2026-08-17** and is effective. **P3.G2 is not approved by this entry** and
  remains open pending the re-reviews and an explicit maintainer acceptance.

## C-P3.2-D — Close P3.G2 after independent implementation and security review

**Date:** 2026-08-18 · **Requester and Decision:** Maintainer and Acceptance
Authority · **Status:** **P3.G2 accepted; P3.3 may begin.**

- **Affected requirement, milestone and release:** P3.2 and stop gate P3.G2.
  This closes the authentication, authorization and web-security package gate;
  it does not accept P3.3 or any later package.
- **Reason and alternatives considered:** The maintainer requested a complete
  review before committing or advancing. Committing only the four-file C-04
  remediation, or accepting the package on its existing green tests, were
  rejected because neither satisfied the distinct security-review requirement.
- **Added/removed scope:** Two security remediations inside existing routes:
  account-wide serialization of R-37's last-identity decision, and refusal of
  R-29/R-30 decisions from superseded C-04 runs. No route, capability, provider,
  data-authority boundary or production integration is added.
- **Dependency and critical-path effect:** P3.G2 no longer blocks P3.3. All later
  package gates remain in force.
- **Estimate/forecast and capacity effect:** The two fixes consumed one review
  and remediation cycle; no phase estimate is otherwise changed.
- **New or changed risks:** Account lockout from concurrent different-row unlink
  and stale-evidence authorization are closed. Older migration evidence remains
  durable but is no longer actionable after a newer run. The accepted Google
  credential fallback and the recorded I-06/A-05/OD-17 residuals are unchanged.
- **Testing, migration, security and operational effect:** Both defects were
  reproduced by new failing PostgreSQL tests before remediation. Afterward the
  191-test security slice, the complete portal suite (1103 passed, 54 intentional
  skips) and the complete bot/database suite (2272 passed) were green. Migration
  0010 remains the only new revision; no applied revision was edited. No live
  service or production data was contacted.
- **Product Owner recommendation:** Accept P3.2 and proceed to the P3.3 planning
  and implementation gate.
- **Technical Lead and specialist reviews:** Claude implemented the package.
  Codex independently reviewed the full package and performed the distinct
  security-focused review on 2026-08-18; findings and evidence are recorded in
  `docs/review/phase-3-p3-2-submission.md` §11.
- **Approval:** The maintainer's instruction to complete the outstanding review,
  accept and commit when ready is recorded as the Acceptance Authority decision.
  With both blocking findings remediated and re-verified, **P3.G2 is accepted on
  2026-08-18.**

## C-P3.3-A — Represent the snapshot folder selection, and make S-11 symmetric

**Date:** 2026-08-18 · **Requester:** Technical Lead (P3.3 implementation) ·
**Status:** **Proposed; not accepted.** P3.3 is submitted for independent
implementation and distinct security-focused review, and P3.G3 is open.

- **Affected requirement, milestone and release:** P3.3 and stop gate P3.G3.
  Three implementation findings that could not be resolved inside the accepted
  contracts without either a silent choice or a contradiction, recorded here so a
  reviewer meets them as decisions rather than discovering them as diffs.
- **Reason and alternatives considered:**
  1. **A table for the folder selection (RAID I-11).** R-41 sets a *changeable*
     Actor folder per snapshot and R-40 renders it, but `foundry_snapshots` is
     append-only — schema §11.2 grants the runtime role `SELECT, INSERT`, and
     migration 0002's trigger refuses `UPDATE`/`DELETE` for the schema owner too.
     Schema §10 defines only the two job tables and §11 names no table for the
     selection. Alternatives rejected: storing it on `foundry_snapshots` (the
     trigger refuses, and weakening the trigger would weaken append-only
     history); deriving the current selection by folding the append-only
     `snapshot.folder_selected` audit events (operational state read out of an
     audit log, which the plan's own separation forbids in spirit). Chosen:
     `snapshot_folder_selections`, one live row per snapshot, mutable and
     versioned, whose *history* remains the append-only audit event the route
     contract already requires. This follows the precedent P3.2 set and the gate
     accepted when migration 0010 added two tables §11 does not name.
  2. **S-11 in both directions (RAID I-12).** `WebSettings.from_environment`
     refused `WORKER_ENABLED=true` unconditionally, which was correct while there
     was one process and made the worker unable to read its own configuration the
     moment there were two. Alternatives rejected: a second environment reader
     for the worker (two readers, two chances to drift); reading `WORKER_*`
     directly in the worker (a second settings authority, which the canonical
     graph exists to prevent). Chosen: `from_environment(..., process=...)`,
     defaulting to `WEB`, with the worker refused under the same `S-11` when the
     value is false.
  3. **Account attribution on an applied import (RAID I-13).** Schema §11 and ADR
     0010 D1 require new rows to carry the stable platform account, and the
     Phase 2 apply service set only `actor_discord_user_id`. Alternative
     rejected: resolving the account from the snowflake at render time in R-47 (a
     second resolution path, and a receipt whose attribution is computed rather
     than recorded). Chosen: a keyword-only `actor_account_id` on
     `SnapshotImportService.apply`, defaulting to `None`.
- **Added/removed scope:** one table beyond the accepted schema decision table,
  one optional parameter on an accepted application service, one optional
  parameter on the accepted settings reader, and one additive optional field on
  the accepted `FolderChoice` view model (`path_observed`, permitted by
  view-model contract §1 rule 5). **Removed:** the inert Phase 2 preview
  endpoint, as route contract §1.1 requires.
- **Dependency and critical-path effect:** none. No later package's inputs move.
- **Estimate/forecast and capacity effect:** absorbed within the P3.3
  implementation; no phase estimate changes.
- **New or changed risks:** none introduced. The folder-selection table is not
  authorization-bearing, holds no personal data beyond the administrator's
  account id, and is covered by the runtime-grant band schema §11.2 gives every
  table whose row is changed in place. The `actor_account_id` parameter is
  *recorded* and never *trusted*: authority is still re-resolved through the
  `AuthorizationPort` at the moment of the commit.
- **Testing, migration, security and operational effect:** migration `0011` is
  reversible and round-trip tested against real PostgreSQL, including that
  append-only history seeded before it is unchanged by both directions (compared
  by `xmin`, not merely by value). Runtime grants extend the accepted bands and
  are asserted as *effective* privileges. Operational documentation gains the
  worker runbook, the retention procedure and the two health signals P3.1 left
  as placeholders.
- **Product Owner recommendation:** accept the three decisions with P3.3, or
  direct a different representation for the folder selection before P3.G3.
- **Technical Lead and specialist reviews:** Claude implemented the package.
  Independent implementation review and a distinct security-focused review are
  **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-B — Fence the import effect, and rebuild the N-24 retention sweep

**Date:** 2026-08-18 · **Requester:** Technical Lead (P3.3 remediation) ·
**Status:** **Proposed; not accepted.** P3.G3 is open and both re-reviews are
outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, SM-05
  and schema §10.1. Raised by the independent implementation review of the P3.3
  submission, which found two blocking defects. Both are corrected here.
- **Reason and alternatives considered:**
  1. **The import effect was fenced by nothing (blocking).** SM-05's
     forbidden-transition table said a committed apply cannot be cancelled and
     named its mechanism as *"the apply's commit sets `state='completed'`; the
     cancel statement filters `state IN ('queued','running')"*. That mechanism did
     not exist. `SnapshotImportService.apply` committed the effect in one
     transaction and `WorkerRuntime` published the job's terminal state in a
     second; in the window between them the job was still `running`, so a
     cancellation matched and cancelled a job whose import had already committed.
     The same window let a timeout self-abandon, a kill-switch self-abandon and a
     reaper requeue leave a job saying `queued`, `stale`, `failed` or `cancelled`
     while its abandoned execution thread committed afterwards.

     Alternatives rejected, each because it leaves the window open:
     **uniqueness alone** (`uq_snapshot_imports_applied_input`, the request key)
     prevents a *second* effect and not the *first* effect from a cancelled
     attempt; **a Python cancellation event** cannot be checked at a commit
     boundary inside another module's transaction; **joining the worker thread
     with a timeout** proves nothing about a thread that is still running when
     the timeout elapses; **a check after `apply` returns** is a third
     transaction and a third window; **disabling cancellation** or weakening
     N-45 removes a control rather than fixing one. Chosen: one nullable
     `TIMESTAMPTZ` column, `reconciliation_jobs.effect_committed_at`, written by
     the transaction that commits the effect and by nothing else, with
     `AND effect_committed_at IS NULL` added to the cancellation request, to the
     worker's self-abandon, and to R-41's and R-46's invalidation statements —
     the fourth writer in the same window, found while building the race suite
     and not named in the review's finding. PostgreSQL's row lock is the serialization; the
     reaper needs no predicate because its `FOR UPDATE SKIP LOCKED` already
     skips a locked row.
  2. **The N-24 retention command could not run (blocking).** It executed
     `UPDATE reconciliation_jobs SET result_id = NULL` before deleting, which
     `CHECK ((state = 'completed') = (result_id IS NOT NULL))` refuses for every
     completed job; and it selected expired previews without regard to the
     `parent_job_id … ON DELETE RESTRICT` graph, so a sweep could abort where the
     correct answer was "that graph is not eligible yet". It also joined results
     inner, so `failed` and `cancelled` jobs that never produced one were
     invisible to every sweep and accumulated indefinitely.

     Alternatives rejected: **deferring or dropping the check constraint** (the
     constraint is delivery plan §8.7 expressed as a constraint); **catching the
     integrity error and reporting success**; **a widening `CASCADE`** that would
     delete ineligible children. Chosen: no schema change at all — the pointer
     never needs nulling, because deleting the job cascades to its result and the
     `RESTRICT` on `result_id` is satisfied by the job's own deletion — plus a
     candidate set locked with `FOR UPDATE … SKIP LOCKED` and a recursive
     fixed-point rule that removes a candidate only when every job naming it as a
     parent is being removed with it.
- **Added/removed scope:** one nullable column and one check constraint on
  `reconciliation_jobs` (migration `0012`, a **successor** to `0011` rather than
  an edit of it, because `0011` has been applied); one keyword-only
  `commit_fence` parameter on `SnapshotImportService.apply`, defaulting to
  `None` so the Phase 2 operator path and the supervised bootstrap are
  unchanged; one repository on the unit of work; `tools/job_retention.py`
  rewritten around a `RetentionSweep` object. **Removed:** nothing.
- **Dependency and critical-path effect:** none. No later package's inputs move.
- **Estimate/forecast and capacity effect:** absorbed within the P3.3
  remediation; no phase estimate changes.
- **New or changed risks:** two, both recorded rather than argued away.
  **RR-16** — a job whose effect committed and whose *third* lease then expires
  is failed by the reaper with `attempts_exhausted` while a valid import exists;
  the receipt and its audit event stand and only the presentation record is
  wrong, and closing it would need a fourth claim, which N-43 forbids.
  **RR-17** — the fence holds the job row's write lock for the duration of the
  import's `COMMIT`, so the worker's own heartbeat and a concurrent cancellation
  block for that interval. It is the last statement before the commit, so the
  interval is the commit and not the apply.
- **Two new derived constants, neither an accepted register number**, both
  listed for ratification rather than introduced as policy:
  `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` (how long the runtime keeps a job
  alive waiting for a thread whose effect has already committed — bounded, and on
  expiry the job is left for the reaper) and `MAX_LIMIT = 10 000` on
  `--limit` (so one sweep cannot become one long transaction).
- **Testing, migration, security and operational effect:** migration `0012` is
  reversible and round-trip tested against real PostgreSQL with append-only
  history compared by `xmin`. Forty-four new real-PostgreSQL regression cases
  (TC-JOB-17…26, TC-MIG-22, TC-OPS-06…17 and their parameterisations), every one of which was first run
  against the pre-remediation implementation and failed there. No grant changes:
  the runtime role already holds `UPDATE` on `reconciliation_jobs` and still
  holds no `DELETE`. Operational documentation gains the corrected retention
  behaviour and three new troubleshooting rows.
- **Contract amendment sought:** SM-05's "cancelling a committed apply"
  mechanism cell is corrected to name the fence, and two forbidden-transition
  rows are added. No state, transition or accepted numeric value changes. This is
  a *mechanism* correction of the kind SM-05 has recorded four times before,
  and it is proposed here rather than self-approved.
- **Product Owner recommendation:** accept the two remediations and the SM-05
  mechanism correction with P3.3, and rule separately on the two decisions the
  remediation deliberately left open — **RAID I-11**
  (`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled
  amendment for the completed-unconfirmed-preview → `stale` exception.
- **Technical Lead and specialist reviews:** Claude implemented the
  remediation. An independent implementation re-review and a distinct
  security-focused re-review are **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-C — Publish the effect, never deny it

**Date:** 2026-08-18 · **Requester:** Technical Lead (P3.3 effect-publication
remediation) · **Status:** **Proposed; not accepted.** P3.G3 is open and both
re-reviews are outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, SM-05,
  schema §10.1 and R-45. Raised by the independent implementation and security
  re-review of `C-P3.3-B`, which found two blocking defects in that remediation.
  Both are corrected here, and **RR-16 is withdrawn rather than carried**: the
  reviewer refused it as a residual risk, correctly.
- **Reason and alternatives considered:**
  1. **A committed effect could be cancelled after reaping (blocking).** The
     `queued` branch of `request_cancel` matched `id = :job_id AND state =
     'queued'` and nothing else, while the reaper deliberately requeued a job
     whose effect had committed but whose result had not been published. So this
     interleaving existed: the apply commits its import, characters, mapping,
     applied audit event and `effect_committed_at`; the process dies before
     publishing; the lease expires and the reaper writes `queued`; R-45 cancels a
     job over a durable import. Fixed **at the write boundary**, not with a
     preceding Python read: both branches carry `AND effect_committed_at IS NULL`,
     and so now do `fail`, `cancel_under_lease` and `mark_stale_under_lease`.
     Migration `0013` adds `CHECK (effect_committed_at IS NULL OR state NOT IN
     ('failed','cancelled','stale'))`, so the row is refused whatever statement
     writes it — including direct runtime-role SQL. The route answers the
     truthful `409` with VM-19's `already_applied`, taken from a typed
     `Cancellation` rather than guessed from a state that reads `running`, and it
     **writes no audit event claiming a cancellation was requested**.
  2. **A committed effect could become `failed` on attempt three (blocking).**
     The reaper chose its branch from `attempts` alone. Neither branch can
     describe a committed effect — one retries an attempt that already succeeded,
     the other declares it exhausted — so the reaper now takes only expiries with
     `effect_committed_at IS NULL`, and an explicit **effect-publication
     recovery** takes the rest.

     *Alternatives considered and rejected:* a fourth claim (N-43 forbids it, and
     the accepted cap is not this remediation's to widen); relaxing
     `queued_can_be_claimed` so a committed effect could be requeued at the cap (a
     job that could never be claimed, counted against N-42's queue bound
     forever); clearing `effect_committed_at` (erases the only durable record
     that the effect exists); a seventh state `recovering` (the publication is one
     transaction under the row lock, so no distinguishable state is observable,
     and N-27's six states are an accepted register value an internal convenience
     must not spend); and reconstructing the summary by re-previewing at recovery
     time (it would describe the database *after* the effect, which is exactly the
     mistake Phase 2 finding B-1R corrected).
- **Added scope:** migration `0013` — one column, `reconciliation_jobs.effect_result`,
  and two check constraints. `application/worker/recovery.py`. Two repository
  statements, `lock_unpublished_effect` and `complete_recovered_effect`.
  `WorkerRuntime.recover()` and `Tick.recovered`. `PendingEffectResult`, which the
  commit fence writes **in the same statement as `effect_committed_at`**, so the
  bounded result a run produced becomes durable if and only if its effect does.
  Typed `Cancellation` and `CancellationRefused`. **Removed:** nothing.
- **Dependency and critical-path effect:** none. No later package's inputs move.
- **Estimate/forecast and capacity effect:** absorbed within the P3.3
  remediation; no phase estimate changes.
- **New or changed risks:** **RR-16 is closed** (as RAID I-17). **RR-17 is
  unchanged** — the fence still holds the row's write lock across the import's
  `COMMIT`, and now writes one bounded JSONB value in the same statement, which
  adds no round trip and no additional lock. **One new residual, RR-18:** a
  recovery publication that cannot succeed leaves the job `running` with a lapsed
  lease rather than writing `failed`, so `expired_lease_age_seconds` climbs until
  an operator intervenes. That is the design — a durable import is never denied —
  and both causes are rows migration 0013's constraints make unrepresentable. The
  runbook names the symptom and the response.
- **One new derived constant, not an accepted register number**, listed for
  ratification: `EFFECT_RECOVERY_LIMIT = 20` (how many committed effects one pass
  publishes, matching the reaper's own `limit`, so a backlog cannot turn one tick
  into an unbounded series of transactions).
- **Testing, migration, security and operational effect:** migration `0013` is
  reversible and round-trip tested against real PostgreSQL with append-only
  history compared by `xmin`, and its `upgrade()` refuses — before it adds
  anything — a database holding a pre-0013 committed effect, naming the count and
  the remedy. Twenty-one new real-PostgreSQL regression cases in
  `tests/web/test_p3_3_effect_recovery.py` plus four migration cases, every one of
  which was first run against the pre-remediation statements and failed there. No
  grant changes: the runtime role already holds `SELECT`, `INSERT` and `UPDATE`
  on the two job tables and still holds no `DELETE`. Operational documentation
  gains the recovered-publication row, the never-denied guarantee and the stalled-
  recovery symptom.
- **Contract amendment sought:** SM-05 gains **one transition** — `running →
  completed`, performed by the recovery pass when the lease has expired and the
  effect has committed — three forbidden transitions, and the column and
  constraints above. **No state is added and no accepted numeric value changes.**
  This is larger than `C-P3.3-B`'s mechanism correction and is proposed here
  rather than self-approved.
- **Product Owner recommendation:** accept this remediation and the SM-05
  amendment with P3.3; note that RR-16, recorded for acceptance in `C-P3.3-B`,
  should be **withdrawn** rather than accepted. The two decisions `C-P3.3-B` left
  open are untouched and still Peter's: **RAID I-11**
  (`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled
  amendment.
- **Technical Lead and specialist reviews:** Claude implemented the remediation.
  An independent implementation re-review and a distinct security-focused
  re-review are **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-D — The rollback boundary of migration 0013

**Date:** 2026-08-18 · **Requester:** Technical Lead (P3.3 migration-rollback
remediation) · **Status:** **Proposed; not accepted.** P3.G3 is open and both
re-reviews are outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, schema
  §10.1, and the deployment/rollback contract in `docs/operations/web-portal.md`.
  Raised by the independent implementation review of `C-P3.3-C`, which found one
  blocking defect in that remediation's migration.
- **Reason and alternatives considered:** `C-P3.3-C` claimed migration `0013` had
  a general data-bearing round trip, on evidence that only ever exercised an
  **empty** schema. It does not. The commit fence writes `effect_result` inside
  the transaction that commits the import effect;
  `ck_…_effect_result_accompanies_the_fence` makes the pair inseparable;
  `downgrade 0012` drops `effect_result` and correctly keeps `effect_committed_at`
  (it is 0012's column); and `upgrade 0013` then refuses on **every truthfully
  completed apply**, because the payload its constraint requires was destroyed.
  The database is stranded one revision below head, and every remedy that would
  clear the refusal — deleting committed job or import history, clearing the
  fence, manufacturing a result — is forbidden. The submission also understated
  the loss: `snapshot_imports` is the import's receipt and does not hold the run's
  blocked create-candidate list, `{code, severity, count}` issue counts,
  `would_create`/`would_update` or `selected_folder_path`.

  *Alternatives considered and rejected:* weakening
  `effect_result_accompanies_the_fence` so a `completed` job need not carry a
  payload (it is the constraint that makes an unpublishable effect
  unrepresentable, and the effect-publication invariant is not this remediation's
  to change); narrowing the upgrade guard (same reason, and it would leave rows
  violating the constraint it guards); reconstructing `effect_result` on
  re-upgrade from `reconciliation_job_results` (available only for the completed
  population; the result row is a superset written by the publication rather than
  the fence's own write, so the migration would be recording a durable fact it did
  not witness, answering for the instant it ran rather than the instant the effect
  committed — Phase 2 finding B-1R's mistake); and a **sidecar table or stash**
  carrying the payload across the downgrade, which is the one design that would
  make a data-bearing downgrade genuinely reversible and is a **material new
  schema object with new ownership and retention rules** — presented for approval
  in submission §14.2 and deliberately **not built**.
- **Added scope:** one guard function in migration `0013`
  (`_refuse_a_downgrade_that_cannot_be_undone`), called by `downgrade()` before
  its first `DROP`; an executable `DO … RAISE EXCEPTION` guard for offline
  (`--sql`) downgrade scripts, because `DROP CONSTRAINT`/`DROP COLUMN` succeed
  against any data and a comment would be no protection; a corrected upgrade-guard
  message distinguishing a database that never reached `0013` from one taken below
  it; and a disposable-database reset in the test session fixture, because the
  refusal is deliberately unconditional and `downgrade base` is a downgrade.
  **Removed:** nothing. **No schema object, constraint, grant, application
  statement, worker statement or contract value changed.**
- **Dependency and critical-path effect:** none. No later package's inputs move.
- **Estimate/forecast and capacity effect:** absorbed within the P3.3
  remediation; no phase estimate changes.
- **New or changed risks:** **RR-19 new** — while any reconciliation job
  retaining a committed effect exists there
  is no supported schema rollback and no supported application version below the
  remediated one, so a defect found after the first production apply must be
  fixed by roll-forward. The mitigation is that revision `0013` is small (one
  nullable column, two check constraints) and that `0013` + pre-0013 code fails
  *safe* rather than corrupting: the old fence writes no payload, so the
  constraint aborts the import transaction and nothing commits. RR-16 remains
  withdrawn; RR-17 and RR-18 are unchanged.
- **Testing, migration, security and operational effect:** seven new
  real-PostgreSQL cases (TC-MIG-24…TC-MIG-30) in
  `tests/web/test_migration_0013_rollback_boundary.py`, every committed effect
  produced by the production apply path rather than seeded. All were first run
  against the pre-remediation migration and failed there — **8 failed, 1 passed**
  — for the intended reason. `tests/web/test_migration_0013_round_trip.py` is
  retained unchanged and **relabelled** as empty-schema evidence. No grant
  changed; `alembic check` still reports no metadata difference. Security effect
  is a strengthening: a destructive `DDL` path that previously ran silently now
  refuses, and the refusal reports counts rather than rows.
- **Contract amendment sought:** the **operational rollback contract**. While any
  **retained** reconciliation job records a committed apply effect, rolling P3.3
  back is application rollback or roll-forward rather than schema downgrade; the
  boundary reopens once no such job survives (`docs/operations/web-portal.md`
  §3.6). *(Predicate corrected 2026-08-19 by `C-P3.3-F`. As originally written
  this bullet read "past the first committed apply effect", which describes a
  historical event the guard does not record and this schema does not hold. See
  `C-P3.3-E` and `C-P3.3-F`; retention is not a rollback technique.)* The refusal itself is implemented
  because it is correct under either policy — it declines to destroy a payload
  nothing may truthfully reconstruct — but the **consequence** for the operational
  contract is proposed here and **not self-approved**. Tracked as RAID **D-09**.
- **Product Owner recommendation:** ratify the rollback boundary as stated, and
  keep the sidecar design closed unless a concrete need for data-bearing rollback
  after go-live is identified — it would add a second writer for a value whose
  single-writer property is what makes effect-publication recovery trustworthy.
- **Technical Lead and specialist reviews:** Claude implemented the remediation.
  An independent implementation re-review and a distinct security-focused
  re-review are **outstanding**.

## C-P3.3-E — Migration 0013's downgrade guard is atomic, and its boundary is retention-aware

**Date:** 2026-08-18 · **Requester:** Technical Lead (second P3.3
migration-rollback remediation) · **Status:** **Proposed; not accepted.** P3.G3
is open and both re-reviews are outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, schema
  §10.1, N-24 retention, and `docs/operations/web-portal.md` §3.6. Raised by the
  second independent re-review of `C-P3.3-D`, which found one blocking
  concurrency defect and two major contract/evidence defects.
- **Reason and alternatives considered:** (F1) the downgrade precondition counted
  under an ordinary MVCC snapshot and only then let the first `ALTER TABLE` queue
  for its DDL lock, so a worker committing its fence in that window was counted by
  nobody and had `effect_result` dropped — the exact state the guard exists to
  prevent. The guard now takes `LOCK TABLE reconciliation_jobs IN ACCESS
  EXCLUSIVE MODE` before the count and holds it to the end of the migration
  transaction, online and in the generated `--sql` script. `ACCESS EXCLUSIVE` was
  chosen over a narrower mode because it conflicts with every mode, and because
  the three `ALTER TABLE` statements need it anyway — so there is one lock, taken
  once, and no lock upgrade to deadlock on. Advisory locks were rejected: workers
  take none. (F2) the documented boundary said downgrade was refused *forever*
  after the first committed apply; the guard counts **retained** jobs, and N-24
  retention legitimately removes a completed committed-effect job and its result
  while preserving the immutable receipt and audit history. The alternative —
  adding a permanent marker, sidecar or tombstone to make the old wording true —
  was **not** taken: it is a material schema/ownership/retention decision
  requiring maintainer approval. (F3) the P3.3 artifact-store fixtures used the
  production unbounded ancestor walk, so seven realistic cases failed during
  setup on the review host; they now use the existing `TrustedAncestors(ceiling=…)`
  constructor seam bounded at pytest's temporary root.
- **Scope, schedule and cost effect:** none beyond the remediation slice. No
  schema object is added, changed or removed by this change; the migration's DDL
  is byte-for-byte what it was.
- **Dependency and critical-path effect:** none.
- **New or changed risks:** **RR-19 restated** — the supported-rollback window is
  the retention-aware predicate above, not "before the first apply, forever".
  **RR-24 new** — the downgrade now takes `ACCESS EXCLUSIVE` on
  `reconciliation_jobs` and waits for a draining worker rather than failing fast;
  the mitigation is the unchanged operational requirement to stop workers first,
  and that a migration blocked on a lock is visible in `pg_locks` and
  `pg_stat_activity`.
- **Product Owner recommendation:** ratify the retention-aware predicate as the
  operational rollback boundary (D-09), and keep the marker/sidecar design closed.
- **Technical Lead and specialist reviews:** Claude implemented the remediation.
  An independent implementation re-review and a distinct security-focused
  re-review are **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-F — The retention-aware rollback predicate is stated consistently, and the held-lock exclusion is proved

**Date:** 2026-08-19 · **Requester:** Technical Lead (third P3.3
migration-rollback correction) · **Status:** **Proposed; not accepted.** P3.G3 is
open and both re-reviews are outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3,
  `docs/operations/web-portal.md` §3.6, the logical-schema and state-machine
  contracts, the test-traceability register, RAID `I-18`/`RR-19`/`D-09` and the
  status record. Raised by the independent review of `C-P3.3-E`, which found
  three major defects and no new blocking concurrency defect.
- **Reason and alternatives considered:**
  - **(F1) The controlled documents still stated the superseded boundary.**
    `C-P3.3-E` corrected the predicate in the migration and the runbook headline
    but left "the first committed apply closes rollback" standing in the
    submission's answers, the logical-schema constraint note, the state-machine
    subsection, the status record, RAID `I-18` and `RR-19`, the `C-P3.3-D`
    amendment bullet and the rollback-boundary test module. A superseded block in
    one section does not cure contradictory present-tense prose elsewhere, and a
    reader must not have to infer that a later section silently overrides an
    earlier one. Every normative and present-tense claim now states the
    retained-row predicate and distinguishes the four database states; the
    historical wording survives only where it is labelled superseded and paired
    with the corrected rule in the same place. *The alternative* — deleting the
    historical wording — was not taken: the register is append-only and a reader
    meeting the old phrasing elsewhere needs to be told it is dead.
  - **(F2) The mandatory concurrency regression proved the wrong condition.**
    `…a_fence_writer_arriving_after_the_lock_cannot_commit_until_it_finishes`
    held the migration's `ACCESS EXCLUSIVE` request **ungranted** behind an
    ordinary reader, so what it established was PostgreSQL lock-queue fairness —
    a later writer cannot overtake a pending conflicting request — and not the
    named condition, that a writer starting after the lock is *granted* cannot
    commit until the migration transaction ends. It is renamed
    `…arriving_behind_a_pending_lock_request_cannot_overtake_it`, kept as
    coverage of the property it does prove, and a new case proves the held-lock
    condition from a granted lock. *Alternatives rejected:* a production pause
    hook in the revision (forbidden, and a revision carrying one is not the
    program a deployment runs); a `pg_sleep` or timing window (asserts about the
    scheduler); an event trigger (`CREATE EVENT TRIGGER` requires superuser,
    which the test role deliberately is not).
  - **(F3) The completion report contained impossible counts.** §15.4 reported
    17 passed for the rollback module alone and 15 passed for that module plus
    `test_migration_0013_round_trip.py`. Both cannot describe one tree. Historical
    results had been combined with later additions and presented as current
    evidence. Every required command is rerun against the final tree and reported
    with its literal invocation and exact count; pre-fix results are kept and
    labelled historical rather than rewritten.
- **Added/removed scope:** none. **No production code, schema object, constraint,
  grant, application statement or worker statement changed.** The migration's DDL
  and emitted SQL are byte-for-byte what `C-P3.3-E` left. The diff is one new
  test case, one renamed and re-scoped test case, two test-cleanup corrections,
  and controlled-document wording.
- **Dependency and critical-path effect:** none.
- **Estimate/forecast and capacity effect:** none.
- **New or changed risks:** none new. **RR-19 restated** to the retained-row
  predicate. `RR-24` is unchanged.
- **Testing, migration, security and operational effect:** the held-lock
  regression drives the production Alembic revision and the production
  `hold_for_effect` fence against disposable PostgreSQL and reads every step from
  `pg_locks`/`pg_stat_activity`. The migration is held after its lock is granted
  by locking Alembic's own `alembic_version` row **from the test**, which changes
  no production module and no emitted statement. No marker, sidecar, tombstone,
  retention-policy change, production pause hook or hidden schema object was
  added. Security, integrity, availability, runtime-role and deployment-order
  effects are unchanged from `C-P3.3-E`.
- **Product Owner recommendation:** ratify the retention-aware predicate as the
  operational rollback boundary (D-09), unchanged from `C-P3.3-E`.
- **Technical Lead and specialist reviews:** Claude implemented the correction. An
  independent implementation re-review and a distinct security-focused re-review
  are **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-G — The held-lock regression identifies its own fence writer

**Date:** 2026-08-19 · **Requester:** Technical Lead (fourth P3.3
migration-rollback correction) · **Status:** **Proposed; not accepted.** P3.G3 is
open and both re-reviews are outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, the
  test-traceability register (TC-MIG-37) and RAID `I-19`. Raised by the
  independent review of `C-P3.3-F`, which confirmed the controlled-document
  correction and the exact rollback-module count and found one major defect.
- **Reason and alternatives considered:** TC-MIG-37 called
  `_ungranted(engine, "RowExclusiveLock")`, which returns **every** ungranted
  request of that mode on `reconciliation_jobs`, accepted the first non-empty
  result, and asserted only that the migration lock-holder's pid was absent. It
  never proved that any returned row belonged to the writer thread's connection
  or transaction, so an unrelated queued session satisfied the poll while the
  intended writer might still be awaiting scheduling, opening its connection,
  inside `seed_import()`, or anywhere before the production fence statement. The
  surviving `writer.is_alive()` and `fence == {}` assertions are all true of a
  thread that has not reached the fence. **Recorded as a defective assertion, not
  a timing flake**: it passed because the disposable database is quiet enough
  that the intended writer normally wins the race, which is why a passing run was
  not closing evidence, and it contradicted the mandatory requirement that
  `pg_locks` / `pg_stat_activity` polling be scoped to the relation **and** to the
  process/transaction. §16.3's instrumented transcript showed the intended
  identity; the committed regression did not enforce it. *Alternatives rejected:*
  adding a PID filter to the shared `_ungranted()` (it is used by the
  queue-fairness case, whose property is ordering rather than identity and whose
  deliberately broader observation must not be narrowed — a narrowly named helper
  was added instead); inferring identity from thread liveness (the defect itself);
  a fixed sleep or an unbounded wait (asserts about the scheduler, or hangs the
  suite); and a production pause hook or any change to the revision or its emitted
  SQL (forbidden, and a revision carrying one is not the program a deployment
  runs).
- **Added/removed scope:** none. **No production code, schema object, constraint,
  grant, retention rule, application statement or worker statement changed.** The
  migration's DDL and emitted SQL are byte-for-byte what `C-P3.3-F` left, and
  `alembic check` reports no metadata difference. `0011`, `0012` and `0013` were
  not edited. The diff is one test case's identity assertions and helpers, plus
  controlled-document wording.
- **Dependency and critical-path effect:** none.
- **Estimate/forecast and capacity effect:** none.
- **New or changed risks:** none new. `RR-19` and `RR-24` are unchanged, and
  §16.8's stated limitation of TC-MIG-37 — that it does not bind the granted lock
  to the guard's own `LOCK TABLE` — is unchanged and is not narrowed here.
- **Testing, migration, security and operational effect:** the writer announces
  its PostgreSQL backend pid over a bounded `queue.Queue`, from inside its own
  transaction and before any production statement. The poll is scoped
  `AND l.pid = :pid` and additionally requires `pg_stat_activity.query` for that
  pid to be the production `hold_for_effect` fence — matched by a stable statement
  shape rather than by driver placeholder spelling — so `seed_import`, connection
  setup and any unrelated statement are excluded. The transaction identity
  observed while the request is queued (`pid`, `virtualtransaction`,
  `backend_xid`, `xact_start`) is re-observed, still open and uncommitted, on the
  transaction that then commits the fence, so the queued request and the
  committing transaction are proved to be one. The migration holder and the fence
  writer are named separately throughout, in the docstring and in every assertion
  message. Both new waits are bounded events in this test module's own thread, not
  production hooks. Falsified deterministically: with the writer held before its
  fence and only an unrelated session queued for the same mode on the same
  relation, the old predicate is satisfied — and its one identity assertion still
  holds — while the corrected predicate cannot be and the case fails; the mutation
  was restored by checksum and is not in the final tree. Cleanup releases every
  connection, transaction, thread and process on every assertion-failure path. **No
  marker, sidecar, tombstone, retention-policy change, production pause hook or
  hidden schema object was added.** Security, integrity, availability,
  runtime-role and deployment-order effects are unchanged from `C-P3.3-F`.
- **Product Owner recommendation:** ratify the retention-aware predicate as the
  operational rollback boundary (D-09), unchanged from `C-P3.3-E` and `C-P3.3-F`.
- **Technical Lead and specialist reviews:** Claude implemented the correction. An
  independent implementation re-review and a distinct security-focused re-review
  are **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-H — The held-lock regression's failure cleanup is bounded

**Date:** 2026-08-19 · **Requester:** Technical Lead (fifth P3.3
migration-rollback correction) · **Status:** **Proposed; not accepted.** P3.G3 is
open and both re-reviews are outstanding.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, the
  test-traceability register (TC-MIG-38…TC-MIG-41, and TC-MIG-37 unchanged) and
  RAID `I-20`. Raised by the independent review of `C-P3.3-G`, which accepted the
  writer-identity remediation as sound and reran the module against disposable
  PostgreSQL, and found one major defect in the same case's cleanup.
- **Reason and alternatives considered:** TC-MIG-37's `finally` block killed a
  surviving migration subprocess and then called `migration.communicate()` **with
  no timeout**. If process termination or pipe collection stalled, cleanup could
  hang indefinitely before it rolled back the externally held `alembic_version`
  row lock, closed the holder connection, or joined the fence writer — leaving a
  live migration child, a writer blocked behind the migration lock and an open
  writer transaction behind it. That contradicts the mandatory requirement that
  cleanup remain bounded and release every connection, transaction, thread and
  process on **every** assertion-failure path, and contradicts the case's own
  claim that its waits are bounded. **Recorded as an unbounded failure-path
  cleanup defect, not a flake**: the passing case never executes the defective
  path, which is exactly why the reviewer's passing runs did not close it.
  *Alternatives rejected:* reusing `_reap()` unchanged (its own post-kill
  collection was an unbounded `communicate()`, so it moved the defect rather than
  removing it — it is bounded here too); a fixed sleep before collecting (asserts
  about the scheduler); a second unbounded wait; letting the cleanup helper raise
  out of `finally` (it would substitute a report about the cleanup for the
  assertion under diagnosis); a production pause hook, a production-code change or
  a migration change (forbidden, and none is implicated — this is a test defect);
  and a regression that hangs for the full 60-second production-test ceiling
  (a bounded fake process proves the timeout branch deterministically instead).
- **Added/removed scope:** none. **No production code, schema object, constraint,
  grant, retention rule, application statement or worker statement changed.** The
  migration's DDL and emitted SQL are byte-for-byte what `C-P3.3-G` left, and
  `alembic check` reports no metadata difference. `0011`, `0012`, `0013` and
  `migrations/env.py` were not edited. The diff is one test module's cleanup
  helpers and four new deterministic cases, plus controlled-document wording.
- **Dependency and critical-path effect:** none.
- **Estimate/forecast and capacity effect:** none.
- **New or changed risks:** none new. `RR-19` and `RR-24` are unchanged, and
  §16.8's stated limitation of TC-MIG-37 — that it does not bind the granted lock
  to the guard's own `LOCK TABLE` — is unchanged and is not narrowed here.
- **Testing, migration, security and operational effect:** every resource
  TC-MIG-37 holds is now owned by one test-local object whose single `release()`
  runs on every exit path, in a fixed order: release the writer's commit event
  first; end and boundedly reap a surviving migration child **before** the
  `alembic_version` row lock is released, so a migration that is *released* rather
  than *ended* cannot commit its drops and a writer queued behind its table lock
  is freed; roll back the row lock; close the holder; then join the writer,
  bounded, and only if it was started and is still alive. The reap kills and then
  collects with an explicit timeout, twice, and never waits without one; a child
  that survives both is **reported and stepped over**, so one stuck process cannot
  strand the connection, transaction and thread that are still releasable.
  `release()` never raises: it returns problem descriptions, which are attached to
  the failing assertion with `add_note()` rather than replacing it, so the primary
  failure stays diagnosable while cleanup failures are still reported. The same
  bounded reap replaces the identical unbounded shape in the three sibling
  concurrency cases in the module. Four new cases (TC-MIG-38…TC-MIG-41) prove the
  release is bounded and total from a **controlled** assertion failure driven
  against real PostgreSQL with the production revision and the production fence
  statement live, and prove the timeout, pre-start and error-preservation branches
  deterministically. Falsified deterministically: against the pre-fix
  `kill(); communicate()` shape four of the five fail — **both** real-PostgreSQL
  parameters, on the surviving child collected with `timeout=None` and on the
  already-exited child not collected at all, plus the fake-process case on the
  same recorded absence of a timeout, the elapsed bound and the problem that was
  not reported, and the error-preservation case on the note that was never
  attached. The bound is asserted at the *call* rather than through elapsed time,
  because `SIGKILL` collects a real Alembic child immediately. The mutation was
  restored by checksum and is not in the final tree. **No marker,
  sidecar, tombstone, retention-policy change, production pause hook or hidden
  schema object was added.** Security, integrity, availability, runtime-role and
  deployment-order effects are unchanged from `C-P3.3-G`.
- **Product Owner recommendation:** ratify the retention-aware predicate as the
  operational rollback boundary (D-09), unchanged from `C-P3.3-E`, `C-P3.3-F` and
  `C-P3.3-G`.
- **Technical Lead and specialist reviews:** Claude implemented the correction. The
  maintainer reviewed and **concurred on 2026-08-19** with one evidence-technique
  decision inside the slice — asserting the bounded collection at the call
  (`_RecordingChild`, submission §18.3), which is what lets the real PostgreSQL
  case falsify the defect at all. That is a design concurrence on one technique
  and is **not** an approval of this entry. Whether to formalise it — as a
  numbered RAID decision or its own change-log decision entry — is **deliberately
  deferred until after the reviews**, which are asked to say whether they consider
  it precedent-setting for how P3.3's concurrency and cleanup evidence is written.
  An independent implementation re-review and a distinct security-focused
  re-review are **outstanding**.
- **Approval:** **none yet.** Nothing in this entry is accepted, and P3.3 is not
  accepted by recording it.

## C-P3.3-I — The held-lock regression's database cleanup is bounded too

**Date:** 2026-08-19 · **Requester:** Technical Lead (sixth P3.3
migration-rollback correction) · **Status:** **Accepted 2026-08-19 by
Peter/Acceptance Authority after distinct implementation and security-focused
re-reviews.** P3.G3 remains open for its explicit gate decision.

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3, the
  test-traceability register (TC-MIG-42…TC-MIG-44; TC-MIG-37…TC-MIG-41 unchanged)
  and RAID `I-21`. Raised by the independent review of `C-P3.3-H`, which **did not
  accept** that entry.
- **Reason and alternatives considered:** `C-P3.3-H` bounded the subprocess reap
  and the writer join and then claimed `_HeldLockCleanup.release()` was bounded on
  **every** path. It was not. `release()` also called `holding.rollback()` and
  `holder.close()` synchronously, and neither SQLAlchemy nor psycopg offers an
  enforceable timeout for either; `seconds_ceiling` counted neither, so the
  documented 25 seconds described a release that could not be shown to end. A
  blocked rollback prevented the close, and a blocked close prevented the writer
  join. The resource at stake is the externally taken `alembic_version` row lock
  in the **shared** disposable `freedom_test` database, so a stuck cleanup could
  contaminate every later case's evidence. **Recorded as an unbounded
  failure-path cleanup defect, not a flake**: neither branch is reachable from
  healthy PostgreSQL, which is why the fifth correction's real-database case and
  its instant fake transaction and connection falsified neither.
  *Alternatives rejected:* another elapsed-time assertion around healthy
  PostgreSQL (it cannot see a call that is unbounded but fast); a socket or
  statement timeout (not active for `rollback()` or `close()`, so presenting one
  as a bound would be a disguised failure); running the synchronous cleanup in a
  thread and declaring success while the thread and its database resources may
  still be live (the failure the handover names explicitly — hence the orphan
  accounting below); closing the connection from the release while another thread
  may still be inside it (an ownership violation, and on a pooled connection worse
  than the leak); a production timeout policy, pause hook, schema object, marker,
  sidecar, tombstone, retention change or runtime grant (forbidden, and none is
  implicated — this is a test defect); and a regression that blocks for real
  (it would hang the suite instead of reporting).
- **Added/removed scope:** none. **No production code, schema object, constraint,
  grant, retention rule, application statement or worker statement changed.**
  `0011`, `0012`, `0013` and `migrations/env.py` are byte-for-byte what
  `C-P3.3-H` left, verified by SHA-256, and `alembic check` reports no metadata
  difference. `docs/operations/web-portal.md` is unchanged. The diff is one test
  module's cleanup helpers and four new deterministic cases, plus
  controlled-document wording.
- **Dependency and critical-path effect:** none.
- **Estimate/forecast and capacity effect:** none.
- **New or changed risks:** none new. `RR-19` and `RR-24` are unchanged, and
  §16.8's stated limitation of TC-MIG-37 is unchanged and is not narrowed here.
  The one new mechanism with a security surface — a test-scoped
  `pg_terminate_backend()` on the test's **own** backend, matched on pid *and*
  `backend_start` — is put to the security reviewer explicitly rather than
  assumed acceptable.
- **Testing, migration, security and operational effect:** each database cleanup
  call is now made by a daemon thread of its own and it is the **wait** that is
  bounded, because that is the only part a test can control. The consequence is
  stated rather than hidden: a call that never returns leaves that thread alive,
  so the thread is recorded on the cleanup, reported as a problem, and never
  followed by anything that touches what it owns; and the holder connection is
  **detached from its pool at construction**, while only the calling thread can be
  inside it, so no orphaned thread can ever leave a usable pooled connection for a
  later case. Because a stuck connection object is off limits, the close step
  alone cannot satisfy "a blocked rollback must not prevent an independent
  close/disposal attempt", so a new step disposes of the **backend** from a
  different connection — releasing the `alembic_version` row lock into the shared
  database and letting the stuck call return. `release()` now runs six steps,
  records each in `attempted` before entering it, and runs every later one
  regardless of what an earlier one did; `seconds_ceiling` counts **all six
  waits** — `2 × 5 + 2 × 5 + 5 + 15 = 40 s`, against the 60-second
  production-test ceiling — and the calculation, the documentation and the tests
  agree. Three new cases (TC-MIG-42…TC-MIG-44) drive the rollback-blocked and
  close-blocked paths with deterministic stand-ins that block exactly where the
  real calls would and record the thread they were called on, and prove the
  release returns inside its complete ceiling, reports the blocked step, attempts
  every later step, releases and joins the writer, preserves the assertion under
  diagnosis, and fails a passing case that leaves a cleanup problem. Falsified
  deterministically by three mutation runs: an unbounded direct `rollback()` fails
  exactly the two rollback cases; an unbounded direct `close()` fails exactly the
  two close cases; and `C-P3.3-H`'s own `communicate()` falsification is retained
  and reproduces the same four failures. None hung. The mutations were restored by
  checksum and are not in the final tree. **No marker, sidecar, tombstone,
  retention-policy change, production pause hook or hidden schema object was
  added.** Availability, runtime-role and deployment-order effects are unchanged
  from `C-P3.3-H`.
- **Product Owner recommendation:** ratify the retention-aware predicate as the
  operational rollback boundary (D-09), unchanged from `C-P3.3-E` … `C-P3.3-H`.
- **Technical Lead and specialist reviews:** Claude implemented the correction.
  **Peter's direction on `_RecordingChild` is recorded and applied**: it remains an
  **informal technical concurrence**, is **not** given a numbered RAID decision or
  its own change-log decision entry, and its existing localized documentation is
  sufficient. The question `C-P3.3-H` left open for the reviewers on whether to
  formalise it is therefore closed as a concurrence; reviewers remain free to
  disagree on its merits. An independent implementation re-review and a distinct
  security-focused re-review are **outstanding**, and the resource-ownership model
  and the new test-scoped `pg_terminate_backend()` path are offered to them for
  judgement rather than presented as settled.
- **Approval:** **Accepted by Peter/Acceptance Authority on 2026-08-19.** The
  independent implementation review found no blocking or major defect. The
  distinct security-focused review found no blocking or major security finding
  and recorded 120 passing rollback, structural and rejected-scope tests in
  `docs/review/phase-3-p3-3-sixth-correction-security-review.md`. This accepts
  `C-P3.3-I`, not defective `C-P3.3-H`; P3.G3 still requires its explicit gate
  decision.

## C-P3.3-J — Acceptance Authority ratification of outstanding P3.3 decisions

**Date:** 2026-08-19 · **Requester:** Peter / Acceptance Authority ·
**Status:** **Accepted.** This is a contract and operational decision; it is not
acceptance of `C-P3.3-I` and does not close P3.G3.

- **Affected requirement, milestone and release:** P3.3 and stop gate P3.G3;
  RAID D-09 and I-11; R-41; SM-05; and submission §13.
- **Decision:** accept D-09's retention-aware rollback boundary; accept
  `snapshot_folder_selections`; accept the narrow completed-unconfirmed-preview
  → `stale` exception; and accept effect-publication recovery.
- **Accepted derived limits:** `EFFECT_RECOVERY_LIMIT = 20`,
  `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3`, and retention `MAX_LIMIT = 10 000`.
- **Added/removed scope:** none; no production code, migration, grant, route,
  retention rule, deployment, or live-service action is authorized.
- **Dependency and critical-path effect:** the named maintainer decisions are
  resolved. P3.G3 remains blocked on the distinct security-focused review.
- **Estimate/forecast and capacity effect:** none beyond the accepted bounds.
- **New or changed risks:** RR-17, RR-18, RR-19 and RR-24 remain recorded.
- **Testing, migration, security and operational effect:** existing evidence and
  the migration refusal are unchanged; the separate security review remains.
- **Product Owner recommendation:** accepted as proposed.
- **Technical Lead and specialist reviews:** the implementation review found no
  blocking or major defect; the distinct security-focused review is outstanding.
- **Acceptance Authority decision:** **Accepted by Peter on 2026-08-19.**

## C-P3.3-K — P3.G3 gate acceptance and P3.4 authorization

**Date:** 2026-08-19 · **Requester:** Peter / Acceptance Authority ·
**Status:** **Accepted; P3.G3 closed; P3.4 authorized.**

- **Affected requirement, milestone and release:** P3.3, stop gate P3.G3 and
  authorization to begin P3.4.
- **Reason and decision:** the outstanding P3.3 contract decisions were accepted
  in `C-P3.3-J`; the sixth cleanup correction passed independent implementation
  and distinct security-focused reviews; and `C-P3.3-I` was accepted. Peter
  therefore accepts P3.3, closes P3.G3 and authorizes P3.4.
- **Added/removed scope:** P3.4 development may begin under the approved roadmap.
  No deployment, public exposure, live-service contact or live-data use is
  authorized by this decision.
- **Dependency and critical-path effect:** the P3.G3 stop gate is removed. Later
  package gates and D-03 remain in force.
- **Estimate/forecast and capacity effect:** P3.4 may now enter planning and
  implementation; no estimate is changed by this administrative decision.
- **New or changed risks:** none. RR-17, RR-18, RR-19 and RR-24 remain recorded.
- **Testing, migration, security and operational effect:** no code, schema,
  migration, grant or runtime behavior changes. I-06 staging evidence and A-05
  protected-administrator/WebAuthn readiness remain required before public
  staging or production exposure.
- **Product Owner recommendation:** proceed to P3.4 within the accepted scope.
- **Technical Lead and specialist reviews:** independent implementation and
  distinct security-focused P3.3 reviews completed with no blocking or major
  finding in the accepted sixth correction.
- **Acceptance Authority decision:** **Peter closed P3.G3 and authorized P3.4 on
  2026-08-19.**

## C-P3.3-L — Post-P3.G3 development and exposure sequence

**Date:** 2026-08-19 · **Requester:** Peter / Acceptance Authority ·
**Status:** **Accepted.**

- **Affected requirement, milestone and release:** P3.4 authorization; I-06;
  A-05; D-03; and the later deployment/exposure decision.
- **Reason and decision:** accept the recommended sequence: begin P3.4
  development, keep deployment and public exposure disabled, establish isolated
  staging for I-06, complete A-05's protected administrator and two independent
  WebAuthn credentials, and close D-03 before Gemini production integration.
- **Added/removed scope:** no feature or deployment scope is added. P3.4 may
  proceed only within the approved implementation plan.
- **Dependency and critical-path effect:** I-06 and A-05 continue to block public
  exposure; D-03 continues to block Gemini production integration.
- **Estimate/forecast and capacity effect:** staging provisioning and operational
  WebAuthn enrollment must be scheduled separately; no estimate is accepted here.
- **New or changed risks:** none. Environment separation and credential-loss
  risks remain governed by the existing controls.
- **Testing, migration, security and operational effect:** staging evidence must
  be real and isolated; local simulations do not close I-06. No production or
  live-service action is authorized.
- **Product Owner recommendation:** proceed in the recorded order.
- **Technical Lead and specialist reviews:** no additional review is required to
  record the sequence; each later package and exposure gate retains its own
  required reviews.
- **Acceptance Authority decision:** **Accepted by Peter on 2026-08-19.** See
  `docs/review/phase-3-p3-4-authorisation-and-conditions.md`.

## C-P3.4-A — D-03 backend route/view-model approval: evidence and decision request

**Date:** 2026-08-19 · **Requester:** Claude / backend contract owner and working
Technical Lead · **Status:** **Accepted by Peter / Acceptance Authority on
2026-08-19 as the bounded D-03 correction authorization.** This decision does
not itself close D-03 or P3.G4 and does not release Gemini's implementation
prompt. D-03 closes only after the authorized corrections pass an independent
Codex implementation review and a distinct security-focused review and Peter
accepts the corrected contract.

- **Affected requirement, milestone and release:** RAID `D-03` (backend
  route/view-model approval half); package P3.4 and stop gate P3.G4; the accepted
  route-authorization and view-model contracts; `C-P3.3-K` and `C-P3.3-L`.

- **Reason and alternatives considered:** `C-P3.3-L` requires D-03 to close
  before Gemini production integration. The preparation task asked whether the
  closed P3.G2 and P3.G3 records already supply that approval. Two answers were
  considered.

  *Treat D-03 as closed by inference from P3.G2/P3.G3* — rejected. Both
  `C-P3.3-K` and `C-P3.3-L` were decided on 2026-08-19, after P3.G2 closed on
  2026-08-18 and alongside the P3.G3 closure, and both restate D-03 as in force.
  Reading the same gates as having silently closed it would overturn a dated
  decision by inference.

  *Present the evidence and the remaining items for an explicit decision* —
  recommended, and taken here. The contract freeze is in excellent condition:
  the accepted implementation matches the accepted contracts on everything a
  static comparison can decide. Six specific items nevertheless remain, and two
  of them would stop a faithful P3.4 implementation on its first file.

- **Evidence of no drift** (read-only comparisons, current tree, 2026-08-19;
  literal output in
  `docs/review/phase-3-p3-4-gemini-readiness-report.md` §A9):

  | Check | Result |
  |---|---|
  | Registered route inventory vs. the parsed route contract | 39 = 39; no extra, no missing, no method or path difference |
  | `DEFERRED_ROUTES` | `{}` — the accepted inventory is complete |
  | Implemented view models vs. the documented `vm-1` set | 21 = 21; `DEFERRED_VIEW_MODELS == {}` |
  | `VIEW_MODEL_VERSION` | `vm-1` |
  | Field-level comparison, all 21 view models | no field missing, renamed or removed; one additive implementation-only field and one ordering difference |
  | Absence controls | no character-game-state route or form; `MigrationDeferred` cannot carry a value; `SafeErrorView` carries a correlation id and one code |
  | Template corpus (24 files) | zero `\|safe`, zero `hx-on:`, zero `<script>`, zero `design-prototype/` references, zero remote origins |

- **The six items requiring the decision** (detail in readiness report §A6):

  | # | Item | Blocking? |
  |---|---|---|
  | D-03-1 | **No accepted static-asset surface.** N-26 requires same-origin CSS, HTMX and images; the route contract's set is closed and defines no static path; the operational contract's Caddy table defines no static handler; and `TC-STRUCT-01` cannot see a Starlette `Mount`, so the machine check protecting the closed set is blind here | **Yes** |
  | D-03-2 | **`ConfirmScope` is referenced by VM-15 and never defined in `vm-1`.** *Council confirmation exact scope* is a mandatory delivery-plan §11 row owned jointly by P3.3 and P3.4 | **Yes** |
  | D-03-3 | **`CharacterFilters` is referenced by VM-07 and never defined in `vm-1`** | No — additive definition |
  | D-03-4 | **VM-13 carries an implemented `csrf_token` absent from the frozen block.** Permitted as additive by view-model contract §1 rule 5 and genuinely required by N-17 for R-37, but its docstring's claim to have been *"Recorded in the P3.2 submission"* cannot be located there | No — record correction |
  | D-03-5 | **R-36's route-contract table cell (`303` to provider) contradicts the same contract's §5.1 prose and the accepted implementation** (`200` HTML · VM-13 `denied`) | No — record correction |
  | D-03-6 | **The safe denial body has no view model of its own.** `denied.html` renders a VM-02-shaped object with three deliberately inert placeholder fields, and printing any of them would break route contract §2.3's byte-identical `404` requirement | No — record correction, and a constraint on P3.4 |

- **Accepted correction scope:** the backend contract owner is authorized to
  implement only D-03-1 through D-03-6 as follows:

  1. application-served static assets under `/static/`, supporting `GET` and
     `HEAD`, requiring no authentication, remaining subject to trusted-host
     controls, remaining available during the portal kill switch, and using
     fingerprint-aware cache headers; structural tests must inventory mounts as
     well as routes;
  2. define `ConfirmScope` with `preview_token`, `checksum_full`, `folder`,
     `profile_version`, `expires_at`, `would_create`, `would_update` and
     `blocked`;
  3. define `CharacterFilters` with `query` and `include_inactive`;
  4. record VM-13's additive `csrf_token` and correct its inaccurate P3.2
     provenance statement;
  5. record R-36 as `200` HTML rendering VM-13 in the denied state, not a `303`
     redirect; and
  6. introduce a dedicated typed `DeniedView` containing only `state` and a
     closed-vocabulary `reason`, while preserving the existing byte-identical
     object-denial and absent-object `404` behaviour.

  No capability, authentication, persistence, migration, grant, dependency,
  character-state mutation, prototype or production-frontend scope is added.

- **Dependency and critical-path effect:** D-03 continues to block Gemini's
  production frontend integration. P3.4 development authorization under
  `C-P3.3-K` is unaffected; the prepared implementation prompt
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` is written and held,
  and is released only by an explicit decision. I-06 and A-05 are untouched and
  continue to block public exposure.

- **Estimate/forecast and capacity effect:** none accepted here. D-03-2 through
  D-03-6 are additive definitions and record corrections; D-03-1 needs a route
  and operational decision, an inventory update and an extension of
  `TC-STRUCT-01` to assert over mounts. All six return through Claude/backend
  with independent Codex review before P3.4 consumes them.

- **New or changed risks:** the delivery plan's recorded *frontend contract
  drift* risk is the one this entry addresses. Leaving D-03-1 undecided would
  invite exactly that: a static surface invented inside a frontend package,
  outside the closed inventory, and invisible to the structural guard. RR-17,
  RR-18, RR-19 and RR-24 are unchanged.

- **Testing, migration, security and operational effect:** none. No test,
  migration, grant, header, policy or service behaviour changes. The visual
  freeze verified 14/14 before and after; `git diff --check` is clean. No
  migration, live service, network call, browser, package installation or
  production/real-player data was used, and no `.env`, credential or secret file
  was read.

- **Product Owner disposition:** accepted as specified above. The implementation
  prompt remains held until the correction package passes both required reviews,
  Peter accepts the corrected contract and Peter explicitly releases the prompt.

- **Technical Lead and specialist reviews:** prepared by Claude as backend
  contract owner. **No independent review has been performed on this entry.**
  Codex's independent implementation pass and distinct security-focused pass are
  required on any contract change the decision authorizes.

- **Acceptance Authority decision:** **Accepted as written by Peter on
  2026-08-19.** D-03 remains **partly closed** — visual half accepted 2026-08-13,
  bounded backend correction authorized 2026-08-19, correction implementation
  and both reviews still pending. Gemini may not change a production frontend
  file until Peter accepts the reviewed corrected contract and explicitly
  releases the implementation prompt. This decision does not authorize staging
  exposure, deployment, production use, live-service contact or real-player
  data.

## C-P3.4-B — D-03 backend-contract correction: implementation submitted for review

**Date:** 2026-08-19 · **Requester:** Claude / backend contract owner and working
Technical Lead · **Status:** **Submitted for review. Not accepted.** This entry
records that the correction `C-P3.4-A` authorized has been implemented and handed
off. It closes nothing.

- **Affected requirement, milestone and release:** RAID `D-03` (backend
  route/view-model approval half); the accepted route-authorization, view-model,
  operational, threat-model and test-traceability contracts; package P3.4's
  readiness. P3.G4, I-06 and A-05 are untouched.

- **Reason and alternatives considered:** `C-P3.4-A` was accepted as written on
  2026-08-19 and authorized exactly six corrections, D-03-1 through D-03-6. This
  entry records their implementation. No alternative disposition was open: the
  decisions were accepted as specified, and the only judgement left inside the
  package was *where* the static surface is served from. Two options were
  considered. *A Caddy `file_server`* — rejected, because operational contract
  §4.1 gives Caddy exactly two jobs and assigns every other header to the
  application so each header has one authority; a proxy-served asset would take
  the CSP and `nosniff` off the application for exactly the responses N-26 cares
  about most, and would sit outside any inventory a test can assert.
  *Application-served from `freedom-web`* — taken, and its cost recorded honestly
  in the new operational contract §4.4.

- **Added/removed scope:** one URL surface (`/static/`, mount identifier M-01) and
  one view model (VM-22 `DeniedView`). Nothing removed. No capability,
  authentication, persistence, migration, runtime grant, dependency,
  character-state, prototype or production-frontend scope is added, and no
  production visual template, CSS, HTMX file, image or asset was created or
  modified. `adapters/web/templates/denied.html` is byte-identical before and
  after.

- **Dependency and critical-path effect:** none changed. D-03 **remains open** and
  continues to block Gemini's production frontend integration.
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` **remains held** and
  is not marked released. I-06 and A-05 continue to block public exposure.

- **Estimate/forecast and capacity effect:** none accepted here. The package
  awaits an independent Codex implementation review and a distinct Codex
  security-focused review, then Peter's decision.

- **New or changed risks:** two threats added to the model by addition — **T-54**
  (path traversal or directory disclosure through the static surface) and **T-55**
  (session or authorization state leaking through a cached asset) — each with its
  controls and residual stated. Eight residual risks are recorded in the
  submission, of which the two worth naming here are that the static root is
  **empty**, so every asset-shaped rule is exercised against probe files rather
  than production assets, and that serving assets from `freedom-web` is an
  accepted design trade recorded as a judgement, not as a measurement. RR-17,
  RR-18, RR-19 and RR-24 are unchanged.

- **Testing, migration, security and operational effect:** 82 new automated cases
  (TC-STATIC-01…07, TC-SEC-14, TC-VM-06, TC-STRUCT-01's mount half, and the
  D-03-2…D-03-6 record cases). The complete portal suite is **1524 passed, 80
  skipped** and the complete bot suite **2294 passed**, both exit 0, run serially
  against the approved disposable `freedom_test` database. `compileall` and
  `git diff --check` are clean. The prototype freeze verified **14/14** before and
  after. Falsification evidence is recorded for the mount inventory guard and the
  denial leakage guard, with the tree restored and verified by SHA-256. **No
  migration was added, edited or run outside the disposable test database**; no
  dependency was added; no browser, network call, live service or real-player data
  was used; no `.env`, credential or secret file was read; the pre-existing stash
  was not inspected or touched. Operationally: `/static/*` needs no Caddy handler,
  no configuration, no backup and no monitoring signal, and joins `/healthz` as
  the second prefix the kill switch leaves serving.

- **Version effect:** **`VIEW_MODEL_VERSION` remains `vm-1`.** Every view-model
  change is additive under contract §1 rule 5 — a view model added, none removed,
  renamed or narrowed, and no enum narrowed. No conflict with the accepted
  versioning rules arose, so nothing was returned to Peter on that ground.

- **Product Owner recommendation:** proceed to the two required reviews.

- **Technical Lead and specialist reviews:** **none performed.** Prepared by
  Claude, who is the author and cannot review it. An independent Codex
  implementation review and a distinct Codex security-focused review are
  **requested** and are recorded as pending in
  `docs/review/phase-3-d-03-backend-contract-correction-submission.md` §12.

- **Acceptance Authority decision:** **none.** D-03 stays **partly closed**. After
  both reviews pass, the decision Peter must make is: *accept the corrected D-03
  backend route/view-model contract, and explicitly release
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`.* That decision would
  not close P3.G4 and would authorize no staging exposure, deployment, production
  use, live-service contact or real-player-data use.

## C-P3.4-C — D-03 corrected contract accepted; Gemini prompt released

**Date:** 2026-08-20 · **Requester:** Peter / Acceptance Authority · **Status:**
**Accepted.**

- **Affected requirement, milestone and release:** closes RAID D-03's backend
  route/view-model approval half and releases the bounded P3.4 production
  frontend integration prompt. P3.G4 remains open; I-06 and A-05 remain open.
- **Reason and alternatives considered:** the correction authorized by
  `C-P3.4-A` and submitted as `C-P3.4-B` passed the independent Codex
  implementation review and the distinct security-focused review with no
  blocking findings. Continuing to hold the prompt was rejected because the
  explicit gate conditions are now met. Widening the decision into P3.G4 or a
  deployment authorization was rejected because neither has its required
  evidence.
- **Added/removed scope:** no implementation scope is added beyond the already
  prepared P3.4 prompt. D-03 is closed and the prompt is released. No route,
  view model, capability, persistence, migration, dependency or backend behavior
  changes through this decision.
- **Dependency and critical-path effect:** Gemini may begin the bounded P3.4
  production frontend integration. P3.G4 still blocks acceptance of that work;
  I-06 and A-05 and a separate exposure/deployment decision remain mandatory.
- **Estimate/forecast and capacity effect:** none recorded.
- **New or changed risks:** none. The D-03 submission's residual risks remain
  visible to P3.4 and must be re-evaluated against the real asset corpus. R-22
  and R-23 continue to be controlled by the frontend contract and P3.G4 review.
- **Testing, migration, security and operational effect:** no new runtime or
  migration effect. Reviewer checks were `git diff --check` exit 0, visual freeze
  14/14, and a focused D-03/structural/security selection of 76 passed / 110
  skipped because `TEST_DATABASE_URL` was not exposed. The author submission's
  approved-disposable-database evidence remains 1524 passed / 80 skipped for the
  portal and 2294 passed for the bot. No secret, live service, network endpoint,
  staging system or real-player data was accessed in the review.
- **Product Owner recommendation:** accept the corrected contract and release
  the prepared prompt.
- **Technical Lead and specialist reviews:** independent Codex implementation
  review **PASS**; distinct Codex security-focused review **PASS**; no blocking
  findings. Full record:
  `docs/review/phase-3-d-03-codex-reviews-and-acceptance.md`.
- **Acceptance Authority decision:** **Accepted by Peter on 2026-08-20.** The
  corrected D-03 backend route/view-model contract is accepted, D-03 is closed,
  and `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` is explicitly
  released. This does not close P3.G4 and does not authorize staging exposure,
  deployment, production use, live-service contact or real-player-data use.

## C-P3.4-D — P3.4 Step 12 accepted; Step 13 verification & remediation submitted

**Date:** 2026-08-23 · **Requester:** Peter / Acceptance Authority & Gemini · **Status:**
**Submitted for Review.**

- **Affected requirement, milestone and release:** Milestone P3.4 (Production Frontend
  Integration). Gate P3.G4 remains open; RAID I-06 and A-05 remain open; Milestone P3.5
  remains held.
- **Reason and alternatives considered:** Peter Duscha accepted Step 12 and authorized
  Step 13 verification and submission under `docs/review/Handover information`. Initial
  submission was reviewed by Codex, identifying findings R13-01..09 followed by R13-10..13.
  Peter authorized bounded documentation remediation. Gemini remediated all findings: rebuilt
  screen matrix (26 templates/fragments), rebuilt route and view-model traceability with exact
  handler symbols (R13-06) and valid top-level test symbols (R13-07, R13-10), provided material behavioral
  evidence for R-01 and R-10 (R13-11), individually listed all falsification probes F-SEC-01 through F-SEC-11
  without range shorthand (R13-12), refined candidate inventory under a narrow presentation inclusion rule
  (53 live candidate artifacts plus 1 rename-provenance row = 54 evidence rows, R13-08), restored authoritative
  RAID definitions (R-22, R-23, RR-17..19, R13-04), implemented a reproducible AST-aware evidence validator
  with three negative falsification demonstrations (R13-13), and narrowed the Codex focused check statement (R13-09).
  Self-acceptance was rejected; advancing to P3.5 or closing P3.G4 was rejected
  because independent Codex implementation and distinct security-focused reviews plus
  Acceptance Authority decision are mandatory.
- **Added/removed scope:** Documentation-only remediation across `docs/review/phase-3-p3-4-submission.md`,
  `docs/project-management/status.md`, `docs/project-management/change-log.md`, and the external
  walkthrough. Zero production code, test, fixture, template, CSS, image, vendored script,
  manifest, migration, or dependency changes.
- **Dependency and critical-path effect:** Milestone P3.4 frontend integration candidate
  is frozen and submitted for independent Codex implementation and distinct security-focused
  reviews. Gate P3.G4 still blocks acceptance; P3.5 remains held.
- **Estimate/forecast and capacity effect:** none recorded.
- **New or changed risks:** none. Authoritative RAID definitions derive solely from
  `docs/project-management/raid-register.md`: R-22 (contract drift during integration),
  R-23 (accessibility regression on production adaptation), RR-17 (commit fence row write
  lock duration), RR-18 (recovery publication failure effect), and RR-19 (roll-forward-only
  schema boundary). Character name 120-char display bounding, the single-provider linking
  constraint, and direct static asset delivery are recorded as factual implementation bounds
  without assigning RAID risk identifiers.
- **Testing, migration, security and operational effect:**
  - Codex review evidence: Codex bounded focused check (174 passed, 94 warnings in 8.75s, manifests OK) found no new implementation or focused-security blocker in the exercised surfaces; complete implementation and distinct security reviews remain pending.
  - Complete historical web suite (`tests/web`): 2168 passed, 80 intentional matrix skips, 1063 warnings in 127.20s against disposable `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test`.
  - Bot / domain suite (`tests/test_*.py`): 2294 passed, 1 warning in 136.38s.
  - Foundry VTT module suite (`foundry-module/tests/*.test.mjs`): 155 passed in 212.38ms.
  - Asset integrity manifest: 3/3 OK (`adapters/web/static/asset-integrity.sha256`).
  - Visual prototype freeze manifest: 14/14 OK (`docs/review/phase-3-visual-freeze-manifest.sha256`).
  - Bytecode compilation: clean (0 errors) in both `venv-web` and `venv`.
  - Whitespace / conflict markers: `git diff --check` clean (0 errors).
  - Tooling discovery: 0 undefined CSS tokens in `check_css_tokens.py`; 48/48 evaluated pairs pass AA/AAA in `calc_contrast.py` (1 disabled exempt).
  - Standalone documentation validator: verified 26 template matrix rows, 49 route/mount rows, 22 view models, exact handler symbols, 193 quoted and unquoted test references across 105 unique top-level test node IDs, 53 live candidate paths matching SHA-256, 1 rename row, direct verification of all 3 asset integrity manifest entries and 14 visual freeze manifest entries, and zero forbidden changes; verified 3 negative in-memory falsification demonstrations (false test path, false test symbol, prohibited shorthand) and unquoted reference coverage.
  - Honest Not Run status recorded for TC-UI-01/02 (uninstalled browser binaries), TC-UI-08 (Peter/maintainer real-device acceptance), and TC-UI-09 (screen-reader review).
  - Zero live services, secrets, staging systems, or production PostgreSQL touched.
- **Product Owner recommendation:** proceed to independent Codex implementation review and distinct security-focused review of the remediated candidate.
- **Technical Lead and specialist reviews:** independent Codex implementation review and distinct security-focused review are **requested and pending**.
- **Acceptance Authority decision:** **none yet.** Stop gate P3.G4 remains open and Milestone P3.5 remains held.

## C-P3.4-E — P3.4 and Step 13 accepted; P3.G4 closed; P3.5 released

**Date:** 2026-08-23 · **Requester:** Peter / Acceptance Authority ·
**Status:** **Accepted; P3.G4 closed; P3.5 released.**

- **Affected requirement, milestone and release:** Milestone P3.4 production
  frontend integration, Step 13 final verification, stop gate P3.G4, and the
  authorization boundary for P3.5.
- **Reason and decision:** after iterative remediation of R13-01 through R13-13,
  Codex completed the independent implementation review and a distinct security-
  focused review. Both found no remaining blocking or important issue. Peter
  therefore accepts P3.4 in full, including Step 13, and closes P3.G4.
- **Added/removed scope:** P3.5 planning and approved gate-evidence work may begin.
  No feature scope is added, and this decision does not authorize staging,
  deployment, public exposure, live-service contact, production PostgreSQL,
  secrets access or real-player-data use.
- **Dependency and critical-path effect:** P3.G4 no longer blocks P3.5. I-06 and
  A-05 remain open and continue to block staging/public exposure and the later
  production-readiness decision. P3.5 retains its own definition of ready,
  evidence requirements and review gate.
- **Estimate/forecast and capacity effect:** P3.5 may enter planning; no calendar
  estimate or capacity commitment is created by this acceptance decision.
- **New or changed risks:** R-23 becomes an explicitly accepted active residual
  after P3.G4 closure. TC-UI-01/02, TC-UI-08 and TC-UI-09 remain Not Run and
  move forward as P3.5/staging evidence rather than being treated as passed.
  I-06 and A-05 are unchanged.
- **Testing, migration, security and operational effect:** no code, schema,
  migration, runtime, deployment or data change is made by this record. The
  accepted evidence includes 2,168 web tests passed with 80 intentional matrix
  skips; 2,294 bot/domain tests passed; 155 Foundry tests passed; 3/3 production
  asset hashes and 14/14 visual-freeze hashes verified; clean bytecode compilation
  and `git diff --check`; and a final Codex focused security/accessibility/auth
  run of 228 passed with 99 non-blocking HTTPX deprecation warnings. The five
  literal Step 13 validator demonstrations reproduced exactly: positive and
  unquoted-extraction runs exited 0; the false-path, false-symbol and prohibited-
  shorthand falsifications exited 1 with the recorded complete tracebacks.
- **Product Owner recommendation:** accept P3.4, close P3.G4 and proceed to P3.5
  within the approved plan while retaining all exposure prerequisites.
- **Technical Lead and specialist reviews:** independent Codex implementation
  review **PASS**; distinct Codex security-focused review **PASS**; no blocking
  or important findings remain. The self-referential placeholder-search transcript
  artifact was assessed as non-blocking because all five literal commands were
  independently extracted and reproduced exactly.
- **Acceptance Authority decision:** **Peter accepted P3.4, including Step 13,
  closed P3.G4 and released P3.5 on 2026-08-23.** Formal evidence:
  `docs/review/phase-3-p3-4-step-13-final-independent-reviews-and-acceptance.md`.

## C-P3.5-A — P3.5 planning opened; readiness audit complete; execution plan submitted for approval

**Date:** 2026-08-23 · **Requester:** Claude / working Technical Lead ·
**Status:** **Proposed. Awaiting the Acceptance Authority's approval.**

- **Affected requirement, milestone and release:** Milestone P3.5 phase integration
  and authentication/security gate package; the Phase 3 gate; RAID I-06, A-05, A-06
  and R-23.
- **Reason and alternatives considered:** the P3.5 handover requires a read-only
  readiness audit and an execution plan **before** any deployment or credential work.
  The alternative — beginning staging or enrollment first — was rejected because it
  would spend Peter's authority before the gaps were known, and because both actions
  are outside the authority this package holds. A second alternative, treating the
  green local suite as P3.5 evidence, was rejected because the rows that close I-06,
  A-05, A-06 and R-23 require evidence levels no automated suite can supply.
- **Added/removed scope:** none. One planning artifact is added:
  `docs/review/phase-3-p3-5-readiness-and-execution-plan.md`. No code, schema,
  migration, configuration, contract or accepted numeric policy is changed, and no
  application behavior is affected.
- **Dependency and critical-path effect:** P3.5's critical path is now explicit and
  it is **not** implementation. Six of eleven deliverables depend on a staging
  environment, a browser engine, an authenticator and a protected administrator
  account that do not exist on any host, and on actions only Peter can perform.
  Three stop gates are proposed: SG-1 plan approval releases repository-scoped work
  only; SG-2 authorizes the staging build; SG-3 authorizes the credential ceremony.
- **Estimate/forecast and capacity effect:** the accepted **3/5/8 focused-day** P3.5
  range is **retained unchanged** for the implementer stream and decomposed to
  3.0/5.0/8.0 across four streams. The 30% review/remediation contingency — 1.5
  focused days — is held explicitly. Peter's accountable effort (staging build, A-05
  ceremony, real-device check, screen-reader capacity, gate decision) and Codex's two
  review passes are estimated **separately**, because the accepted range never
  contained them. Confidence: Medium-low for the implementer stream, **Low for
  end-to-end P3.5 completion**. No calendar date is committed; availability windows
  remain unrecorded.
- **New or changed risks:** no RAID disposition is changed. I-06, A-05 and A-06 remain
  **Open**; R-23 remains an **active accepted residual**. Four planning-level findings
  are raised: **F-1** (important, traceability) the P3.4 submission's accessibility
  matrix renumbers the TC-UI rows against the accepted traceability contract, leaving
  TC-UI-03 and TC-UI-05 without a citation under their own IDs — the tests themselves
  are named for the contract's numbering and pass, so nothing is broken and no accepted
  row is weakened; **F-2** no `freedom-web` systemd unit template exists in the
  repository, which TC-OPS-04 needs; **F-3** no repository artifact defines the portal's
  proxy site block or its body limits, which TC-LIM-02's parity assertion needs; **F-4**
  no browser engine or browser automation exists on this host, which blocks TC-UI-01/02,
  TC-SEC-07's browser half and the WebAuthn registration ceremony until Peter decides
  how a browser is supplied.
- **Testing, migration, security and operational effect:** none is made by this record.
  The audit re-ran every available check: `tests/web` 2,168 passed with 80 intentional
  matrix skips; bot/domain 2,294 passed (run **sequentially**, since both suites share
  the one disposable `freedom_test` database); Foundry module 155 passed; asset integrity
  3/3; visual freeze 14/14; bytecode compilation clean in both virtualenvs;
  `git diff --check` clean; a single linear Alembic head `0013` with no branches;
  `git status` clean before and after. **No formatter, linter or type checker is
  configured in this repository** — recorded as unavailable, never as passed. The
  migration upgrade/downgrade/upgrade rehearsal was deliberately **not** run in a
  read-only audit and is the first approved execution step.
- **Product Owner recommendation:** approve the plan (SG-1) and decide the browser
  question, releasing only the repository-scoped step — final traceability, the F-1
  reconciliation, and the migration and backup/restore rehearsals against the guarded
  disposable database. Hold SG-2 and SG-3 until the plan has been read.
- **Technical Lead and specialist reviews:** the readiness audit found **no blocking
  security, authorization, identity, atomicity, data-integrity, recovery or reliability
  issue**, scoped to what a read-only audit and the local suites can show. That is not a
  substitute for the two Codex passes, which P3.5 will request at SG-4.
- **Acceptance Authority decision:** **none yet.** No staging exists, no credential is
  enrolled, no RAID item is closed, the Phase 3 gate remains open and Phase 4 remains
  unstarted. Formal record:
  `docs/review/phase-3-p3-5-readiness-and-execution-plan.md`.

## C-P3.5-B — SG-1 approved; browser decision taken; two ceremony findings raised

**Date:** 2026-08-23 · **Requester:** Peter Duscha / Acceptance Authority ·
**Status:** **Approved (SG-1 and P-2 only). SG-2 and SG-3 remain unapproved.**

- **Affected requirement, milestone and release:** Milestone P3.5; RAID A-05 and R-23.
- **Reason and decision:** Peter approved the P3.5 readiness and execution plan
  (stop gate SG-1) and decided the browser question (P-2) in favour of the
  recommended option — his own workstation browser against the staging loopback.
- **Added/removed scope:** repository-scoped execution EX-1…EX-9 is released.
  **No headless browser, driver or other frontend toolchain dependency is added**,
  preserving delivery-plan §4's exclusion. EX-5 gains one artifact: the WebAuthn
  registration reference page described in F-7. No staging, deployment, exposure,
  credential or production action is authorized.
- **Dependency and critical-path effect:** SG-2 (staging build) and SG-3 (credential
  ceremony) remain the critical path and remain unapproved. I-06, A-05, A-06 and
  R-23 remain open.
- **Estimate/forecast and capacity effect:** none. The accepted 3/5/8 focused-day
  implementer range is unchanged; no calendar date is committed.
- **New or changed risks:** two findings raised while preparing the ceremony's
  prerequisites. **F-7 (important):** `tools/webauthn_enrollment.py` directs the
  operator to a registration reference page in `docs/operations/` that **does not
  exist**, so the A-05 ceremony currently has no supported starting point; EX-5
  authors it. **F-8 (important, operator safety):** `enroll` stores a credential
  without recording or validating the relying-party identifier its browser ceremony
  used, while authentication checks `expected_rp_id` against the running service's
  `WEB_WEBAUTHN_RP_ID`, which configuration requires to equal the public origin's
  own host — so a credential enrolled at a loopback staging origin is accepted and
  **can never authenticate** against the production hostname, and nothing says so
  until somebody is locked out. Neither is exploitable and neither weakens an
  accepted control; the strictness behind F-8 is a control worth keeping.
- **Testing, migration, security and operational effect:** no code, schema, migration,
  runtime or configuration change is made by this record. A-05's closure criteria are
  **tightened**, not weakened: criterion 2a now requires each credential to have been
  created under the intended target host's relying-party identifier and requires one
  successful authentication against a service running that same RP ID before A-05 can
  close. A staging-loopback enrollment is explicitly recorded as a rehearsal of the
  mechanism rather than as satisfaction of the assumption.
- **Product Owner recommendation:** proceed with EX-1…EX-5 only; hold SG-2 and SG-3
  until the staging inputs and the two authenticators are in hand.
- **Technical Lead and specialist reviews:** F-8 is referred to Codex's independent
  and security-focused passes as a structural question — the ceremony's RP ID is
  knowable at enrollment and could be recorded and checked. **No behavior change is
  made under this plan**, because it would touch an accepted P3.1 contract surface
  and is Peter's decision after review.
- **Acceptance Authority decision:** **Peter approved SG-1 and the P-2 browser
  decision on 2026-08-23.** SG-2, SG-3, the Phase 3 gate and Phase 4 remain
  unapproved. Formal record:
  `docs/review/phase-3-p3-5-readiness-and-execution-plan.md` §0.2.

## C-P3.5-C — First deployed run: one blocking defect fixed, one routed to Gemini

**Date:** 2026-08-23 · **Requester:** Claude / working Technical Lead ·
**Status:** **Interim. No gate decision requested; no RAID item closed.**

- **Affected requirement, milestone and release:** Milestone P3.5; RAID I-06, A-05;
  the P3.1 break-glass deliverable; the Phase 3 gate.
- **Reason and decision:** Peter approved SG-1, authorized the host build and
  performed it. The portal ran under its restricted service account for the first
  time in the project's history, on `freedom-blades-test.rpgworld.org` with a
  separate database, a separate test Discord application, no real data and a
  password gate at the proxy. Four defects appeared within the first hour. **Every
  suite was green before and after; none of them was caught by a test.**
- **Added/removed scope:** no product scope. Deployment artifacts that did not
  exist were authored: the `freedom-web` unit template (F-2), the proxy site block
  (F-3), the WebAuthn registration page and its host-local conversion tool (F-7),
  the ASGI entry point, and three operator scripts. One blocking defect was fixed
  in `infra/postgresql/runtime-grants.sql.tmpl`; one was routed to Gemini.
- **Dependency and critical-path effect:** **F-15 blocks A-05 and therefore blocks
  exposure.** The passkey break-glass login cannot be completed in a browser: the
  page has no control and the site ships no application JavaScript, so R-07/R-08
  are unreachable. It is a scope gap — P3.4 Step 4 was explicitly instructed not to
  write passkey JavaScript, and no later package was commissioned to. Routed to
  Gemini as frontend owner per delivery plan §2 and §5 P3.5.
- **Estimate/forecast and capacity effect:** the accepted 3/5/8-day implementer
  range is unchanged; the F-15 remediation falls inside the 30% review/remediation
  contingency, which is what it was reserved for. No calendar date is committed.
- **New or changed risks:** **F-14 (blocking, fixed):** the restricted runtime role
  had no `SELECT` on `alembic_version`, which S-14 must read, so the documented
  restricted-role deployment could never have started — in staging or production.
  Fixed, regression-tested and falsified. **F-15 (blocking, routed).** **F-16
  (important):** nothing in the suite asserts a human can complete break-glass
  login, which is how F-15 survived two gates. **F-13 (minor):** `/healthz` raises
  rather than reporting when the kill-switch directory is unreadable; not fixed,
  as it is accepted P3.1/P3.3 surface. **F-11 (host):** the Cloudflare origin
  private key was world-readable; reported and corrected by the Operations Owner,
  never read. **F-10:** the origin certificate is Cloudflare-issued and trusted
  only by Cloudflare, so proxied DNS is mandatory and the true visitor address must
  be rewritten or the authentication limiter would treat the whole internet as one
  source.
- **Testing, migration, security and operational effect:** migrations `0001`–`0013`
  applied cleanly to `freedom_staging`; the protected administrator mapping landed
  with the correct guild and role snowflakes; restricted grants applied and verified
  in their three documented bands, with `audit_events` holding `SELECT, INSERT` and
  neither `UPDATE` nor `DELETE`. `tests/test_runtime_grants.py` and
  `test_runtime_grants_live.py`: **57 passed**, including the new regression test,
  which was falsified by removing the fix and restored. `/healthz` reports `ok` on
  every check with `environment: staging`. All four pre-existing sites verified
  still serving after every proxy change.
- **Product Owner recommendation:** accept the F-14 fix as remediation, release the
  F-15 prompt to Gemini, and retain every exposure prerequisite. A-05 has its first
  real enrollment — two credentials on a deployed host — and that is a rehearsal,
  not closure: the credentials are bound to the test address and no passkey login
  has yet succeeded.
- **Technical Lead and specialist reviews:** requested from Codex in
  `phase-3-p3-5-interim-findings-and-review-request.md` — an independent pass and a
  distinct security-focused pass, with six named questions including whether any
  finding should reopen a closed gate.
- **Acceptance Authority decision:** **none requested.** I-06, A-05 and A-06 remain
  open, R-23 remains active, the Phase 3 gate remains open, and Phase 4 remains
  unstarted.

## C-P3.5-D — Codex withheld the Gemini prompt; C35 remediation partial

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Partial remediation submitted for re-review. Gemini remains unreleased.**

- **Affected requirement, milestone and release:** Milestone P3.5; findings F-15, F-17,
  F-13, F-14; RAID I-06, A-05; the Phase 3 gate.
- **Reason and decision:** Codex's independent review of the P3.5 interim package raised
  C35-01…C35-07 and withheld release of the Gemini prompt. C35-01, C35-02, C35-03, C35-04
  and C35-06 are implemented and verified. **C35-05 is not started**, and C35-07 depends
  on it, so the prompt stays unreleased.
- **Added/removed scope:** no product scope. One repository artifact stopped carrying
  credential material; one perimeter defect was closed in the repository artifact; three
  test modules were added or extended; the registration ceremony was corrected.
- **Dependency and critical-path effect:** the server-owned shell contract (C35-05) is now
  the critical path for F-17 and for any further Gemini work. Rotation of the staging gate
  and re-enrollment of both emergency credentials are required Operations Owner actions.
- **Estimate/forecast and capacity effect:** consumed within the 30% review/remediation
  contingency. C35-05 is a further backend package not separately estimated. No calendar
  commitment.
- **New or changed risks:** **F-18** — a password verifier authored by this package was
  committed and reached Git history through a harness checkpoint ref; on no branch and no
  remote-tracking ref, not pushed, but read during review, so the password is spent and
  rotation is mandatory. **F-19** — `/healthz` was publishable through the proxy against
  the accepted operational contract. Both are recorded in the readiness plan.
- **Testing, migration, security and operational effect:** no schema, migration or runtime
  data change. `tests/test_deployment_artifacts.py` (7 cases) and six new live
  runtime-grant cases were added and **falsified**; `tests/web/test_health_kill_switch_robustness.py`
  (6 cases) added with its falsification retained as a test. The deployed host is
  **unchanged** — it still proxies `/healthz` and still holds the inline verifier.
- **Product Owner recommendation:** authorize the three host actions (rotate, reinstall and
  reload, re-enroll), then commission C35-05 as the next backend package.
- **Technical Lead and specialist reviews:** Codex independent and distinct
  security-focused re-review requested in
  `docs/review/phase-3-p3-5-c35-remediation-handoff.md`.
- **Acceptance Authority decision:** **none requested.** No RAID item is closed, Gemini is
  not released, the Phase 3 gate remains open and Phase 4 remains unstarted.

## C-P3.5-E — R35 remediation partial; rotation script repaired

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Partial. Submitted for another independent and security-focused review.**

- **Affected requirement, milestone and release:** Milestone P3.5; findings F-13, F-17, F-18;
  RAID A-05; the Phase 3 gate.
- **Reason and decision:** Codex's re-review found the C35 remediation incomplete and the
  operator script defective. R35-08, R35-09 and R35-10 are complete and falsified; R35-11 is
  not started; the Gemini prompt stays unreleased.
- **Added/removed scope:** no product scope. One operator script rewritten; two test modules
  added or extended.
- **Dependency and critical-path effect:** R35-11 (the server-owned shell contract) is the
  critical path for F-17 and any further Gemini work. Gate rotation and credential
  re-enrollment remain Operations Owner actions, both still outstanding.
- **Estimate/forecast and capacity effect:** within the review/remediation contingency.
  R35-11 is a further backend package, not separately estimated. No calendar commitment.
- **New or changed risks:** the rotation procedure previously handed over **could not run at
  all** — a SIGPIPE defect under `pipefail` — so the compromised gate password has never been
  rotated and remains active. The plaintext also passed through child-process argv. Both are
  fixed and falsified; neither password nor verifier appears in any artifact.
- **Testing, migration, security and operational effect:** no schema, migration or runtime data
  change. New: 11 hermetic script tests, 3 ASGI health cases. The stdin hashing interface was
  verified functionally against a real Caddy rather than assumed. The deployed host remains
  unchanged.
- **Product Owner recommendation:** authorize the host actions, then commission R35-11.
- **Technical Lead and specialist reviews:** requested in
  `docs/review/phase-3-p3-5-c35-remediation-handoff.md` (canonical; the R35 handoff now redirects there).
- **Acceptance Authority decision:** **none requested.** No RAID item closed, Gemini not
  released, Phase 3 gate open, Phase 4 unstarted.

## C-P3.5-F — Rotation transaction safety completed; shell contract still outstanding

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Partial. Submitted for another independent and security-focused review.**

- **Affected requirement, milestone and release:** Milestone P3.5; findings F-13, F-17, F-18;
  RAID A-05; the Phase 3 gate.
- **Reason and decision:** Codex's third review found the rotation helper not transaction-safe
  under interruption, its failure-path coverage incomplete, the handoff ambiguous, and
  C35-05 still unstarted. R35-13, R35-14, R35-15, R35-16 and R35-18 are complete; **R35-17
  is not**, and Gemini stays unreleased.
- **Added/removed scope:** no product scope. One operator script rewritten as a transaction;
  one test module extended from 11 to 24 cases; two handoffs consolidated into one canonical
  document.
- **Dependency and critical-path effect:** R35-17 is the sole remaining blocker for F-17 and
  any Gemini work. Four Peter-only host actions remain outstanding.
- **Estimate/forecast and capacity effect:** within the review/remediation contingency.
  R35-17 is scoped but not estimated. No calendar commitment.
- **New or changed risks:** an interrupted rotation could previously leave an unknown active
  password on disk — an availability and access-control risk in the recovery path itself.
  Fixed and falsified. No new risk is introduced.
- **Testing, migration, security and operational effect:** no schema, migration or runtime data
  change. 24 script tests, 7 deployment-artifact tests, 10 health tests (0 skipped with the
  guarded disposable database), 57 + 53 runtime-grant tests, web 2178, bot 2323, Foundry 155,
  manifests OK, compilation clean, `git diff --check` clean. The deployed host is unchanged.
- **Product Owner recommendation:** authorize the four host actions, then commission R35-17.
- **Technical Lead and specialist reviews:** requested in the canonical handoff
  `docs/review/phase-3-p3-5-c35-remediation-handoff.md`.
- **Acceptance Authority decision:** **none requested.** No RAID item closed, Gemini not
  released, Phase 3 gate open, Phase 4 unstarted.

## C-P3.5-G — The server-owned shell contract is implemented

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Submitted for independent and security-focused re-review.**

- **Affected requirement, milestone and release:** Milestone P3.5; findings F-17, C35-05,
  R35-11, R35-17; the view-model and traceability contracts; the Phase 3 gate.
- **Reason and decision:** the shell contract was the sole remaining blocker for F-17 and for
  any Gemini work. It is implemented, tested across every accepted caller state, and recorded
  in the contracts by addition.
- **Added/removed scope:** one new application module and a typed view model (VM-23); two
  wiring points; the shared header; eleven traceability rows. No route, no view-model change
  to any existing page, no persistence, no migration.
- **Dependency and critical-path effect:** F-17's backend half is complete. The Gemini prompt
  is revised and narrowed to styling; it stays unreleased pending Codex. Four Peter-only host
  actions were completed during this session except the Cloudflare ingress restriction.
- **Estimate/forecast and capacity effect:** within the review/remediation contingency.
- **New or changed risks:** none introduced. Two pre-existing defects were found and fixed —
  a capability-only navigation rule would have offered a break-glass caller a route R-40
  refuses, and the P3.4 scope guard never caught modifications to tracked files.
- **Testing, migration, security and operational effect:** no schema, migration or runtime
  data change. Web 2199 passed, bot 2337 passed, Foundry 155, shell contract 21, manifests
  verified, compilation clean, `git diff --check` clean. Accepted P3.4 evidence was updated
  deliberately in three places, each recorded with its prior value or prior intent.
- **Product Owner recommendation:** submit for Codex review; do not release Gemini until it
  accepts both the backend contract and the revised prompt.
- **Technical Lead and specialist reviews:** requested in the canonical handoff.
- **Acceptance Authority decision:** **none requested.** No RAID item closed, Gemini not
  released, Phase 3 gate open, Phase 4 unstarted.

## C-P3.5-H — Shell boundary defects and the rotation commit window closed

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Submitted for another independent and security-focused review.**

- **Affected requirement, milestone and release:** Milestone P3.5; findings F-17, F-18,
  C35-05; VM-23; the Phase 3 gate.
- **Reason and decision:** Codex's fourth review found the rotation helper unsafe after a
  successful reload and the shell derived at the wrong lifecycle point from stale authority.
  R35-19 through R35-25 are implemented; Gemini stays unreleased.
- **Added/removed scope:** no product scope. One operator script resequenced; the shell's
  derivation point, source context and home destination corrected; one new request-boundary
  test module.
- **Dependency and critical-path effect:** the backend half of F-17 is complete and now has
  request-boundary evidence. Only the Cloudflare ingress restriction remains of the host
  actions.
- **Estimate/forecast and capacity effect:** within the review/remediation contingency.
- **New or changed risks:** three defects removed, each of which would have mattered
  operationally — a rotation that could leave an unknown active password; navigation that
  outlived revoked authority; and a denial page that told a signed-in caller they were logged
  out. No new risk introduced.
- **Testing, migration, security and operational effect:** no schema, migration or runtime
  data change. Web 2238, bot 2346, Foundry 155, shell unit 30, request boundary 28, rotation
  33, ASGI health 10 with zero skips. Every fix falsified with the mutation asserted before
  the result was read. Eleven pieces of accepted P3.4 evidence updated deliberately, each
  recorded with its prior value or intent.
- **Product Owner recommendation:** submit for Codex review; authorize the Cloudflare ingress
  restriction at the deployment gate.
- **Technical Lead and specialist reviews:** requested in the canonical handoff.
- **Acceptance Authority decision:** **none requested.** No RAID item closed, Gemini not
  released, Phase 3 gate open, Phase 4 unstarted.

## C-P3.5-I — Shell lifecycle completed on public and failure pages

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Submitted for another independent and security-focused review.**

- **Affected requirement, milestone and release:** Milestone P3.5; findings F-17, F-18,
  C35-05; VM-23; TC-SHELL; the Phase 3 gate.
- **Reason and decision:** Codex's fifth review found authenticated callers still receiving
  the anonymous frame on public full pages and on refresh-failure pages, and post-commit
  housekeeping failures being swallowed. R35-26 through R35-31 are implemented.
- **Added/removed scope:** no product scope. One public-page shell attachment; one refusal-path
  shell; one conservative typed shell state; the rotation script's housekeeping made
  attributable; twenty further request-boundary cases.
- **Dependency and critical-path effect:** the backend half of F-17 is complete across every
  full-page render. Gemini remains blocked pending Codex. Only the Cloudflare ingress
  restriction remains of the host actions.
- **Estimate/forecast and capacity effect:** within the review/remediation contingency.
- **New or changed risks:** three defects removed, each operationally material — a portal that
  told signed-in people they were signed out on its two most-visited public pages; an outage
  page that did the same; and a rotation that hid its own cleanup failures while verifier
  material accumulated. No new risk introduced.
- **Testing, migration, security and operational effect:** no schema, migration or runtime data
  change. Web 2258, bot 2346, Foundry 155, request boundary 48, focused packages 90 and 104,
  ASGI health 10 with zero skips. Every fix falsified with the mutation asserted first. VM-23
  and TC-SHELL-17…20 updated by addition.
- **Product Owner recommendation:** submit for Codex review; authorize the Cloudflare ingress
  restriction at the deployment gate.
- **Technical Lead and specialist reviews:** requested in `docs/review/Handover information`
  and the canonical handoff.
- **Acceptance Authority decision:** **none requested.** No RAID item closed, Gemini not
  released, Phase 3 gate open, Phase 4 unstarted.

## C-P3.5-J — Public-shell failure boundary made typed

**Date:** 2026-08-23 · **Requester:** Codex, via the Acceptance Authority ·
**Status:** **Submitted for another independent and security-focused review.**

- **Affected requirement, milestone and release:** Milestone P3.5; finding F-17; VM-23;
  TC-SHELL; the Phase 3 gate.
- **Reason and decision:** Codex's sixth review ran the focused database-backed suite at 194
  passed and found one remaining defect: the public-shell helper caught every `Exception` and
  treated it as "no session". R35-32 through R35-36 are implemented.
- **Added/removed scope:** no product scope. One typed exception policy; one app-level
  `ServiceDegraded` handler mirroring the existing protected-route response; nineteen further
  request-boundary cases.
- **Dependency and critical-path effect:** none changed. Gemini remains blocked pending Codex.
  Only the Cloudflare ingress restriction remains of the host actions.
- **Estimate/forecast and capacity effect:** within the review/remediation contingency.
- **New or changed risks:** one defect removed, and it was the quiet kind — a portal that
  looked healthy while it could not resolve anybody, logging out the operator best placed to
  notice. No new risk introduced.
- **Testing, migration, security and operational effect:** no schema, migration or runtime data
  change. Web 2277, bot 2346, Foundry 155, boundary 67, focused packages 157 and 104, ASGI
  health 10 with zero skips. Falsified with the mutation verified by AST in both directions.
  VM-23 and TC-SHELL-21…27 updated by addition.
- **Product Owner recommendation:** submit for Codex review; authorize the Cloudflare ingress
  restriction at the deployment gate.
- **Technical Lead and specialist reviews:** requested in `docs/review/Handover information`
  and the canonical handoff. Live-host actions H-1…H-3 are recorded as Peter/Claude
  attestations, not independently reviewed evidence.
- **Acceptance Authority decision:** **none requested.** No RAID item closed, Gemini not
  released, Phase 3 gate open, Phase 4 unstarted.

## C-P3.5-K — Frontend repository remediation accepted; supervised evidence retained

**Date:** 2026-08-24 · **Requester:** Peter / Acceptance Authority ·
**Status:** **Repository implementation accepted; operational evidence pending.**

- **Affected requirement, milestone and release:** P3.5; F-15/F-17; A-05;
  TC-BG-02; TC-UI-01/02; R-23; the Phase 3 gate.
- **Reason and alternatives considered:** after Gemini's frontend implementation,
  Codex twice reviewed the actual diff and withheld acceptance for a dead no-JS
  action, CSP-incompatible style mutation, unexecuted ceremony paths, an
  unenforced refusal vocabulary, permissive Base64URL padding and overclaimed
  evidence. Each was remediated. Treating green mocks as real-browser evidence
  was rejected; the physical session remains a separate gate activity.
- **Added/removed scope:** no product scope added. The repository now contains a
  fingerprinted same-origin WebAuthn client, truthful progressive enhancement,
  VM-23 shell presentation, strict client validation, durable tests and a
  supervised-session plan. No production deployment is authorized here.
- **Dependency and critical-path effect:** the frontend-code blocker is removed.
  The critical path moves to the supervised staging browser/authenticator
  session and the remaining P3.5 operational evidence.
- **Estimate/forecast and capacity effect:** Peter expects the supervised session
  within a few hours on 2026-08-24. This is an availability statement, not a
  guaranteed completion date; failures return to remediation.
- **New or changed risks:** no new implementation risk. The residual is explicit:
  automated and mocked success may still differ from a real browser, RP ID,
  authenticator, proxy and deployed session lifecycle. R-23 remains active.
- **Testing, migration, security and operational effect:** Codex independently
  ran 50 Node tests, 9 structural tests, 10,240 randomized Base64URL vectors,
  refusal probes, asset verification and whitespace checks. Gemini reported the
  full sequential suites green. No schema/migration change is part of the final
  frontend remediation. Real browser/authenticator tests remain Not Run.
- **Product Owner recommendation:** commit the coherent P3.5 repository package,
  execute the bounded supervised procedure in isolated staging, and update the
  evidence record before requesting any gate decision.
- **Technical Lead and specialist reviews:** Codex frontend implementation and
  security-focused review accepted with no remaining repository-code findings.
  Formal record:
  `docs/review/phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md`.
- **Acceptance Authority decision:** Peter authorized documentation consolidation
  and a sensible repository commit. Peter has **not** accepted A-05, R-23, the
  outstanding test rows or the Phase 3 gate, and has not authorized public
  exposure or Phase 4.

## C-P3.5-L — Supervised browser and authenticator session executed; SP-21 and SP-22 added; eight findings raised

**Date:** 2026-08-24 · **Requester:** Peter Duscha / Operations Owner, under SG-3 ·
**Status:** **§4 procedure complete. No RAID item closed; no gate decision requested.**

- **Affected requirement, milestone and release:** Milestone P3.5; RAID A-05, I-06,
  R-23; TC-BG-02, TC-UI-01, TC-UI-02; findings F-15 and F-17; the Phase 3 gate.
- **Reason and alternatives considered:** the frontend repository implementation was
  accepted by Codex on 2026-08-24 with the explicit caveat that no real browser or
  authenticator had completed the workflow. Treating the green Node and pytest
  suites as sufficient was rejected then and is rejected here. The bounded procedure
  in `phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md` §4 was
  executed instead, in two sittings, with the Operations Owner driving his own
  browser and physical authenticators.
- **Added/removed scope:** **no repository change of any kind.** No code, template,
  asset, migration or configuration was modified during the session; the working
  tree stayed clean at `0c95e72`. One evidence document was authored:
  `docs/review/phase-3-p3-5-supervised-session-evidence-2026-08-24.md`.
- **Dependency and critical-path effect:** F-15's operational half is discharged — a
  human completed break-glass login in a real browser, twice, on two credentials,
  under a verified Discord outage. TC-UI-01/02 are satisfied for one browser on one
  platform. The critical path moves to SP-21/SP-22, the disposition of the six
  findings below, and the untouched I-06 procedures.
- **Estimate/forecast and capacity effect:** the session cost roughly 90 minutes of
  Operations Owner time across two sittings, inside decision D-g's ~30-minute units.
  No calendar date is committed.
- **New or changed risks:** **eight findings, none caught by any test suite.**
  **S-1 (resolved):** the deployed process was serving code 8½ hours older than the
  commit under test; the page under test returned HTTP 500 while the full suite was
  green and `/healthz` reported `ok`. Fixed by restart; the deploy/reload gap
  remains. **S-4 (important):** `/healthz` reports `identity_provider: true`
  unconditionally — a hardcoded literal, not a probe, so the portal cannot report a
  Discord outage. **S-5 (important, security):** rate-limited break-glass refusals
  write no audit record while showing the user a correlation reference that resolves
  to nothing; the refusals that stop being recorded are the ones that indicate an
  attack. **S-6 (important):** every logout is audited as `guild_member`, including a
  break-glass administrator holding no guild membership. **S-7 (important,
  operational):** the R-07 options call and the R-08 verify call share one limiter
  bucket, so a completed ceremony costs two of five per-address units and a cancelled
  one costs one. **S-9 (important, security):** a replayed recovery grant and an expired one produce
  byte-identical audit payloads (`grant_not_live`) with no grant reference, so an
  investigator cannot distinguish a possibly-leaked token from a slow operator; the
  single-statement `consume` that causes it is itself correct and should stand.
  **S-8 (cosmetic):** the Product Owner finds the post-sign-out page unpolished; it
  passes every functional and accessibility check applied, and the visual baseline is
  frozen, so any change is a scope decision. **S-2 (observation):**
  `freedom-worker.service` is inactive while `/healthz` reports
  `worker_heartbeat: true`. A usability risk is also recorded: the
  operator cannot distinguish live from retired credentials in his authenticator,
  which with S-7 is a genuine break-glass availability concern.
- **Testing, migration, security and operational effect:** all seven required views
  observed at 320/768/1280 CSS pixels and 200% zoom; keyboard-only traversal
  including a keyboard-actuated POST sign-out; the no-JavaScript branch observed in a
  scriptless browser with no dead control. Two ceremonies on two distinct enabled
  credentials, both under an `iptables` provider outage scoped to the portal's service
  account and verified in both directions (`000` after 1 ms blocked, `405` restored)
  with the live bot unaffected (`200` throughout). A retired credential was presented
  and refused as `unknown_credential`. Break-glass sign-out invalidated the session
  server-side. No schema, migration or configuration change.
- **Product Owner recommendation:** submit to Codex now. The one gap identified at
  drafting — that the session had evidenced the continuity *navigation* withholding
  Council, character and snapshot destinations but never the *routes* refusing them —
  was closed immediately afterwards: R-20, R-22 and R-40 each answered the denial page
  against a live break-glass session. The import-apply POST routes (R-41, R-46) remain
  suite-level only, because driving them would require handling the operator's session
  cookie. **SP-21 was also executed**: a recovery grant was issued host-locally, used
  exactly once, then refused on replay and refused again after a deliberate 15-minute
  wait that cleared both the 10-minute ceiling and the N-33 window, so the expiry
  refusal could not be a limiter refusal in disguise. The token was never transmitted,
  never recorded and never entered a shell history. **A false pass was avoided in the
  process**: the first run of that check was
  performed signed-out and returned the sign-in page, which is the sessionless `303`
  path and not a refusal; it was caught by comparing the observation against the two
  code paths rather than against expectation.
- **Technical Lead and specialist reviews:** not yet requested. The findings are
  recorded undispositioned and deliberately unfixed — no repository change belongs
  inside an evidence session.
- **Acceptance Authority decision:** **none requested.** A-05, I-06, A-06, R-23,
  TC-BG-02, TC-UI-01/02 and the Phase 3 gate all remain open. Public exposure and
  Phase 4 remain unauthorized.

## C-P3.5-M — Codex review findings remediated: emergency refusal audit, logout attribution, limiter split, grant classification, provider probe

**Date:** 2026-08-24 · **Requester:** Claude, P3.5 working Technical Lead ·
**Status:** **Repository remediation accepted by independent and security
re-review. N-32a accepted by the Acceptance Authority. No RAID item or gate
closed.**

- **Affected requirement, milestone and release:** Milestone P3.5; RAID A-05
  (criteria 6, 7, 8), I-06 (criterion 9, TC-OPS-05); SM-03; N-14, N-32, N-33,
  VM-16; the Phase 3 gate. Answers
  `docs/review/phase-3-p3-5-supervised-session-codex-review.md` and
  `docs/review/phase-3-p3-5-supervised-session-codex-security-review.md`.
- **Reason and alternatives considered:** the independent review held S-5 and S-6
  **blocking** for A-05 criterion 7 and the security review made the Security
  Reviewer's criterion-10 confirmation conditional on both being remediated and
  re-reviewed, with S-3/S-4 (its numbering) requiring accepted dispositions.
  Deferring them to a later package was rejected: they are defects in the audit
  trail of the emergency path itself, and every day they stand is a day of
  incident evidence that cannot be reconstructed. For S-7 the review explicitly
  rejected raising the coupled limiter number in favour of splitting the buckets,
  and that is what was implemented.
- **Added/removed scope:** six code changes and their tests, each tied to one
  named finding, plus the F4 reconciliation of the evidence record. No new route,
  no new dependency, no migration, and no schema change — the audit table already
  expressed everything these corrections needed, which is why none of them needs
  one. Full detail in
  `docs/review/phase-3-p3-5-supervised-session-remediation-submission.md`.
- **Dependency and critical-path effect:** A-05 criterion 7's two blocking
  findings are answered and were accepted by independent and security re-review
  on 2026-08-24. Criterion 6's remaining half (F3:
  R-41 and R-46 observed on the deployed build) is **not** discharged — it needs
  the Operations Owner and a live session, and cannot be done from the
  repository. I-06's TC-OPS-05 gains a real provider check. S-1 and S-2 remain
  open operational items with no repository change proposed for either.
- **Estimate/forecast and capacity effect:** repository work only. The two
  outstanding items that need the Operations Owner — F3's two POST observations
  and F4's exact session-end timestamp plus the SP-21 grant record ids — are
  small and are listed explicitly rather than absorbed.
- **New or changed risks:** one accepted numeric policy gains an entry. **N-32a**
  bounds WebAuthn challenge issuance at 10 per source address per 10 minutes,
  separating it from N-32's assertion budget, which is unchanged. The residual
  risk it accepts is a slightly larger bound on short-lived challenge rows, which
  N-31's sweep already governs; the risk it removes is emergency lockout from an
  ordinary operator mistake during the outage break-glass exists to survive. This
  required §5 change control and was accepted by Peter Duscha, Acceptance
  Authority, on 2026-08-24 after the independent and security re-reviews found
  the implementation coherent and no new Important or Blocking code defect.
- **Testing, migration, security and operational effect:** 44 new tests across
  five new traceability rows (TC-BG-18…21, TC-OPS-18). Full portal suite 2330
  passed / 80 skipped, bot suite 2079 passed / 267 skipped, `node --test` 50
  passed, asset integrity 4/4 OK. No migration. Operationally, `/healthz` now
  makes one bounded unauthenticated outbound request per poll, and an unreachable
  Discord makes the endpoint report `degraded` with `503` — which is the intended
  behaviour and a change monitors will see.
- **Product Owner recommendation:** none sought; this is remediation of accepted
  findings rather than a scope proposal.
- **Technical Lead and specialist reviews:** Codex independent and distinct
  security re-reviews accepted the repository remediation on 2026-08-24. The
  remaining evidence and operational conditions are recorded in those reviews.
- **Acceptance Authority decision:** **Peter Duscha accepted N-32a on
  2026-08-24:** 10 WebAuthn challenge issuances per source IP per 10 minutes,
  separate from unchanged N-32 assertion budgets. This accepts only the numeric
  addition. A-05, I-06, R-23 and the Phase 3 gate all remain open; public exposure
  and Phase 4 remain unauthorized.

## C-P3.5-N — Handover executed: deployment identity, criterion 6 and 3 observed, worker root-caused, S-4 closed end to end

**Date:** 2026-08-25 · **Requester:** Claude, P3.5 working Technical Lead ·
**Status:** **Handover steps 1, 2, 3 and 6 complete; steps 4 and 5 partial. Two
new findings raised (F5, F6), one fixed. No RAID item and no gate closed.**

Executes `docs/review/Handover information` (Codex, Independent Reviewer,
2026-08-24). Full operational record:
`docs/review/phase-3-p3-5-post-remediation-operational-addendum-2026-08-24.md`.

- **Affected requirement, milestone and release:** Milestone P3.5; RAID A-05
  (criteria 3, 4, 6, 9), I-06 (worker prerequisite), S-1, S-2; N-13, N-65, S-11,
  S-15, VM-16; the Phase 3 gate.
- **Reason and alternatives considered:** the handover named six ordered steps,
  each blocked on the one before it. Deployment identity had to be proved before
  any browser observation could be trusted (S-1's original failure was a process
  serving code older than the commit under test while every suite was green), so
  no evidence was gathered until the restarted process was shown to postdate the
  deployed commit by a mechanism argument rather than a favourable timestamp.
- **Added/removed scope:** the reviewed remediation package was committed intact
  as `0bef692`. Two repository fixes were added that the handover did not
  anticipate, both for F5: `infra/systemd/freedom-worker.service.tmpl` and the
  worker section of `docs/operations/web-portal.md`. One new operations document,
  `docs/operations/break-glass-credential-custody.md`, answers A-05 criterion 9.
  No route, no view model, no migration and no schema change.
- **Dependency and critical-path effect:** **A-05 criterion 6 is now evidenced in
  full** — R-41 and R-46 both refused `403 emergency_surface_refused` from N-65's
  continuity-surface check before any handler object lookup, which answers F3.
  **Criterion 3 is evidenced** (SP-23): retiring below two enabled credentials is
  refused before any write, exit status 1. **Criterion 9 is drafted and accepted.**
  Criterion 4 is half-observed (SP-24) and blocked on one decision. **S-1 is
  satisfied for this deployment** and **S-2 is resolved.** I-06's worker
  prerequisite is met; its named procedures are untouched.
- **Estimate/forecast and capacity effect:** no forecast change. The remaining
  A-05 work is four staging re-observations in one planned sitting, criterion 4's
  deferred decision, and the Security Reviewer's criterion-10 confirmation.
- **New or changed risks:** two findings, neither previously known.
  **F5** — `freedom-worker.service` could never have started: the unit set
  `Environment=WORKER_ENABLED=true` while reading the shared portal
  `EnvironmentFile`, and `systemd.exec(5)` gives the file precedence, so the
  shared file's `WORKER_ENABLED=false` (required there by S-11 in the other
  direction) silently won and the worker refused itself on every start. The
  arrangement came from this repository's own operations guide, which offered it
  explicitly; the guide was wrong and is corrected. Fixed, installed and verified
  running.
  **F6** — a below-threshold credential count is detected and then reported to
  nobody outside production. `run_resource_checks` produces a warning naming the
  shortfall exactly; the lifespan assigns it to `composition.startup_warnings`,
  which no route, service, repository or control reads; it is never logged and
  never reaches VM-16, and S-15 is a refusal only in production. A staging account
  down to one credential answers `/healthz` byte-identically to a healthy one.
  **No fix is proposed** — the route surface is frozen and VM-16 is an accepted
  closed vocabulary, so adding a check is a contract change needing its own
  decision. Raised for the Security Reviewer.
- **Testing, migration, security and operational effect:** full portal suite 2330
  passed / 80 skipped, bot suite 2079 passed / 267 skipped, `node --test` 50
  passed, asset integrity 4/4 OK, `git diff --check` clean. No migration.
  Operationally: the portal was restarted onto the reviewed commit, the worker was
  fixed and started for the first time, and one `iptables` outage rule was applied
  and removed within a single sitting to run S-4's acceptance test. **S-4 is now
  closed end to end** — under a real provider outage isolated to the portal's
  service account, `/healthz` reported `identity_provider: false`, `degraded` and
  `503`, where the same rule on the same host had reported `ok`/`200` on
  2026-08-24. One incident is recorded in full: `freedom_test`, the disposable
  suite database, was dropped and could not be recreated by the working account
  (`rolcreatedb = false`); the Operations Owner restored it and the full
  verification set was re-run, reproducing 2330 / 80 exactly.
- **Product Owner recommendation:** none sought; this executes an accepted
  handover rather than proposing scope.
- **Technical Lead and specialist reviews:** none yet for this package. The
  observations, the two new findings and the criterion 9 document are submitted
  for independent review, and criterion 10 remains explicitly outstanding.
- **Acceptance Authority decision:** **none requested, and none recorded.** Peter
  Duscha accepted the criterion 9 custody documentation on 2026-08-25 and
  authorised the criterion 4 disposable-database observation; neither closes a
  RAID item. A-05, I-06, A-06, R-23 and the Phase 3 gate all remain open. Public
  exposure and Phase 4 remain unauthorized.

## C-P3.5-O — Codex C1/C2 remediation: the staging installer reproduces the F5 repair, and `/healthz` reports the credential shortfall

**Date:** 2026-08-25 · **Requester:** Claude, P3.5 working Technical Lead ·
**Status:** **Both High findings answered in the repository. C2 carries a contract
correction that is proposed, not approved. No RAID item closed and no gate moved.**

Answers `docs/review/Handover information` (Codex, Independent Reviewer,
2026-08-25, *changes requested*). Return package:
`docs/review/phase-3-p3-5-codex-c1-c2-remediation-2026-08-25.md`.

- **Affected requirement, milestone and release:** Milestone P3.5; RAID A-05
  (criterion 4), S-2, findings F5 and F6; N-13, S-11, S-15, VM-16; the view-model
  contract (`C2-1`) and the operational contract §5; the Phase 3 gate.
- **Reason and alternatives considered:** Codex raised two High findings. **C1**:
  the F5 repair reached the unit template and the operations guide but not
  `infra/staging/setup-portal-host.sh`, the template's only executable consumer, so
  the supported provisioning path would have produced a worker unit carrying a
  literal `EnvironmentFile=__WORKER_ENVIRONMENT_FILE__` and the same losing
  `Environment=WORKER_ENABLED=true`. No alternative was considered: the finding is
  correct. **C2**: F6 is nonconformance with the written A-05 A-4 step, and Codex
  named two permitted paths — implement an approved reporting-contract change, or
  formally amend A-4. **The first was chosen.** Amending A-4 would accept a manual
  credential count as the only channel for the condition on exactly the hosts where
  S-15 is deliberately a warning rather than a refusal, and would close the third
  instance of one pattern (S-4, `worker_heartbeat`, F6) by lowering the question
  rather than answering it.
- **Added/removed scope:** the installer gains a worker environment-file step, the
  `__WORKER_ENVIRONMENT_FILE__` substitution, a refusal to install a unit whose
  directives still carry a placeholder, and an effective-configuration check against
  systemd; it loses the appended `Environment=WORKER_ENABLED=true` and the
  `install_unit` parameter that carried it. `/healthz` gains one check name; the
  lifespan gains a log line for the warnings it already held. Thirteen new tests in
  two modules, one existing test seeded. **No route, no view-model field, no status
  code, no template, no migration, no schema change, no new dependency.**
- **Dependency and critical-path effect:** **nothing closes.** F5/S-2 are
  repository-remediated and wait on Codex's re-review plus one root-held step — the
  supported installer re-run on the staging host, with `systemctl`/`journalctl` as
  the liveness evidence rather than `/healthz`'s `worker_heartbeat`. A-05 criterion
  4 stays open on both halves: the production refusal is unobservable before an
  authorized production deployment, and the `/healthz` half now exists in the
  repository but has been observed on no host and its contract change is unapproved.
  Criterion 10 is untouched.
- **Estimate/forecast and capacity effect:** no forecast change. The added work is
  one authorized root sitting on the staging host, and two review decisions.
- **New or changed risks:** **the contract correction `C2-1` is the material one.**
  `VIEW_MODEL_VERSION` stays `vm-1` — a name is added to a closed vocabulary,
  nothing is removed, renamed or narrowed, which is additive under the view-model
  contract §1 rule 5 and follows the `expired_leases` precedent. Two consequences
  are stated rather than left to be discovered. **Disclosure:** a reader of
  `/healthz` learns that the protected administrator holds fewer than two enabled
  credentials. The endpoint is loopback-bound (N-50), refused by the Caddy site
  before its catch-all proxy (C35-02) and unpublished, and it already discloses
  environment, version and kill-switch state; the assessment is that a boolean
  readable only from the loopback port is a smaller risk than the condition being
  invisible, but that judgment is the Security Reviewer's. **Availability:** any
  host without enrolment now answers `degraded` and `503`, staging included until
  A-05's ceremony happens.
- **Testing, migration, security and operational effect:** portal suite 2338 passed
  / 80 skipped (baseline 2330/80), bot suite 2085 passed / 267 skipped (baseline
  2080/267) and 2352 passed with the disposable database configured, `node --test`
  50 passed, asset integrity 4/4 OK, `git diff --check` clean. Both suites were run
  serially against the one shared disposable database. Both regression sets were
  falsified against the reviewed code: C1's four fail against the installer as
  reviewed, C2's seven of eight fail against the pre-change modules. No migration.
  Operationally, nothing on the staging host was changed by this package: the
  installer was **not** re-run, no unit was rewritten, and no service was restarted.
  The generated worker unit was compared against the running one and is identical in
  every directive.
- **Product Owner recommendation:** none sought; this is remediation of an
  independent reviewer's findings rather than a scope proposal.
- **Technical Lead and specialist reviews:** **outstanding.** Codex's re-review of
  C1 and C2 is requested. The Security Reviewer's review of the `C2-1` reporting
  contract change — its disclosure and availability effects — is required before
  A-05 criterion 4 or criterion 10 can move.
- **Acceptance Authority decision:** **none requested and none taken.** The `C2-1`
  contract correction is **proposed** and awaits Peter Duscha's decision. A-05,
  I-06, A-06, R-23 and the Phase 3 gate all remain open; public exposure and Phase 4
  remain unauthorized.

## C-P3.5-P — Codex C3/C4 remediation: an existing worker file is confirmed completely, and readiness stops being described as usability

**Date:** 2026-08-25 · **Requester:** Claude, P3.5 working Technical Lead ·
**Status:** **Both re-review findings answered. Codex recommends approving the C2
health-contract change; that approval is still outstanding. No RAID item closed and
no gate moved.**

Answers `docs/review/Handover information` (Codex, Independent Reviewer,
2026-08-25, re-review of `020f455..78dfb67`, *changes requested*). Return package:
`docs/review/phase-3-p3-5-codex-c3-c4-remediation-2026-08-25.md`.

- **Affected requirement, milestone and release:** Milestone P3.5; RAID A-05
  (criterion 4), S-2, findings F5/F6; S-11, S-15, N-13, VM-16; the configuration
  and dependency contract's S-15 rationale row; the Phase 3 gate.
- **Reason and alternatives considered:** **C3** — the existing-file branch
  confirmed only the value of `WORKER_ENABLED`, and for this file that is the wrong
  shape of check. The worker unit reads it after the shared portal file, so every
  assignment in it overrides the portal's; a file carrying `WEB_DATABASE_URL` and
  `WORKER_ARTIFACT_ROOT` above a conforming last line was accepted, and ownership,
  mode and symlink shape were not examined at all. The alternative — repairing a
  nonconforming file — was rejected: this script's promise is that it never
  overwrites an environment file, and a script that silently corrects one is a
  script that can silently destroy one. It refuses and names the fault instead.
  **C4** — the description of the below-two state was wrong in a way that matters
  during an incident, and the correct statement is narrower than the one it
  replaces.
- **Added/removed scope:** one new file, `infra/staging/lib/worker-env-file.sh`,
  holding the validation as a sourceable function; the installer sources it during
  preflight and calls it on an existing file. 21 new tests in
  `tests/test_worker_env_file.py` that **execute** that function, plus one in
  `tests/web/test_break_glass_health_reporting.py` over the corrected wording. No
  application-code behaviour changes: C4 is entirely documentation, comments and
  docstrings. No route, view model, migration or schema change.
- **Dependency and critical-path effect:** none moved. F5/S-2 stay pending the
  authorized installer re-run on the staging host; A-05 criterion 4 stays open on
  both halves; criterion 10 is untouched.
- **Estimate/forecast and capacity effect:** no forecast change.
- **New or changed risks:** the C3 finding retires a real one — a `worker.env`
  left behind by any earlier process could have reconfigured the worker's database
  and artifact store through a file the installer reported as confirmed. The
  remaining risk is unchanged and stated: the installer has still not been run on
  the staging host, so its behaviour there is inferred from the repository and from
  the deployed unit's directives, not observed.
- **Testing, migration, security and operational effect:** portal suite 2339
  passed / 80 skipped, bot suite 2106 passed / 267 skipped and 2373 passed with the
  disposable database configured, `node --test` 50 passed, asset integrity 4/4 OK,
  `git diff --check` clean; both suites run serially against the one shared
  disposable database. The C3 validation is falsified against its predecessor:
  Codex's own example file is accepted by the old check and refused by the new one.
  No migration. Nothing on the staging host was changed by this package.
- **Product Owner recommendation:** none sought; this is remediation of an
  independent reviewer's findings.
- **Technical Lead and specialist reviews:** Codex accepted the C1 and C2 core
  mechanisms on 2026-08-25 and **recommended approving the additive C2
  health-contract change** after C4's correction — recorded as a specialist
  recommendation, not an approval. Codex's re-review of C3 and C4 is requested.
- **Acceptance Authority decision:** **none requested and none taken.** The `C2-1`
  contract correction remains proposed and awaits Peter Duscha's decision. A-05,
  I-06, A-06, R-23 and the Phase 3 gate all remain open; public exposure and Phase 4
  remain unauthorized.

## C-P3.5-P1 — Acceptance Authority decision on C2-1

**Date:** 2026-08-25 · **Requester / Acceptance Authority:** Peter Duscha ·
**Status:** **Accepted.**

- **Decision:** Peter Duscha accepted the additive C2-1 health-contract
  correction: VM-16 includes the boolean `break_glass_credentials` check,
  `/healthz` asks it afresh and fails closed, and the lifespan logs the existing
  S-15 startup warning.
- **Review basis:** Codex accepted the mechanism and separately assessed its
  disclosure and availability effects, recommending approval after C4's wording
  correction. C3/C4 were subsequently accepted with no blocking finding, and the
  Low read-diagnostic issue was corrected and regression-tested.
- **Scope and version effect:** no route, view-model field, status code,
  migration, schema or dependency changes. One name is added to VM-16's closed
  check vocabulary; `VIEW_MODEL_VERSION` remains `vm-1` under its additive-change
  rule. The signal remains boolean-only and does not disclose credential count or
  material.
- **Operational effect:** a host below N-13's two-credential redundancy floor
  reports `degraded`/`503`; exactly one credential may still authenticate but is
  not ready for exposure. The endpoint remains loopback-bound and unpublished.
- **Boundary:** this accepts C2-1 only. A-05 criterion 4 still requires its
  remaining deployed observation/production-refusal evidence, and criterion 10
  remains the Security Reviewer's confirmation. A-05, the Phase 3 gate and public
  exposure remain open; Phase 4 remains unauthorized.

## C-P3.5-Q — prepare the product-owned filesystem layout

**Date:** 2026-08-25 · **Requester / Product Owner:** Peter Duscha ·
**Status:** preparation implemented; privileged cutover not executed

- **Affected requirement, milestone and release:** administrative repository
  strategy in implementation-plan §2.1; P3.5 operations. No product scope,
  authorization, schema or release criterion changes.
- **Reason:** `/opt/discord-bots/freedom-bot` describes the platform as its
  original Discord adapter and adds a parent layer that owns no unrelated
  product. Peter requested one Freedom Blades root with explicit subdirectories.
- **Scope:** active paths move to `/opt/freedom-blades` (`platform`, `runtime`,
  `reference`, `workspace`), `/srv/freedom-blades`, and
  `/etc/freedom-blades`. Service names, databases, roles, accounts, DNS and Git
  remote names remain unchanged. Historical evidence retains historical paths.
- **Dependencies and critical path:** feature work pauses until preparation,
  host cutover and direct verification finish. Root access and a short service
  maintenance window are required.
- **Estimate/capacity:** one preparation change and one supervised host sitting;
  rollback remains available until an observation period is released.
- **Risks:** stale hard-coded paths, moved Python-environment shebangs, partial
  service configuration, accidental directory merges, and premature deletion of
  rollback material. Controls are active-path regression tests, fresh virtual
  environments, absent-target preconditions, systemd/Caddy validation, direct
  journals/endpoints, and delayed cleanup.
- **Testing/migration/security/operations:** no data-format migration and no
  secret-content change. `docs/operations/filesystem-layout-migration.md` is the
  cutover and rollback procedure. Persistent artifacts remain under `/srv` and
  secrets under `/etc` with their existing ownership contracts.
- **Product Owner recommendation:** proceed with the prepared layout before more
  feature work.
- **Technical/specialist review:** repository preparation and verification are
  performed by Codex; operational results remain to be observed.
- **Acceptance Authority decision:** Peter explicitly requested preparation and
  migration on 2026-08-25. This authorizes the administrative work, not closure
  of F5/S-2, A-05, or the Phase 3 gate.

## C-P3.5-R — product-owned filesystem cutover executed and verified

**Date:** 2026-08-25 · **Requester / Operations Owner:** Peter Duscha ·
**Status:** executed and verified; rollback observation hold remains.

- **Scope:** the repository, runtimes, reference exports, service data and
  configuration moved to the accepted `/opt/freedom-blades`,
  `/srv/freedom-blades` and `/etc/freedom-blades` layout. Service names,
  databases, roles, accounts, DNS and Git remote are unchanged.
- **Evidence:** status update 59 records the directory inventory, effective
  systemd/Caddy paths, active bot/portal/worker processes, PostgreSQL, endpoints,
  durable queue and asset-integrity checks. The supported portal-host installer
  regenerated the units during the cutover.
- **Review effect:** Codex subsequently observed the worker active with the
  shared environment file followed by the strictly validated worker file and
  recommends closing F5/S-2. Review record:
  `docs/review/phase-3-p3-5-f5-s2-operational-re-review-2026-08-25.md`.
- **Recovery:** obsolete environments and review trees remain under the rollback
  hold; cleanup requires a deliberate Operations Owner release.
- **Gate boundary:** the administrative cutover supplies a deployed staging
  environment but does not execute or close I-06's named P3.5 procedures, A-05,
  A-06, R-23 or the Phase 3 gate.

## C-P3.5-S — Phase 3 closure request audited; gate remains open

**Date:** 2026-08-25 · **Requester / Acceptance Authority:** Peter Duscha ·
**Status:** closure not supportable on current evidence; Phase 4 implementation
not started.

- **Request:** update all documentation, commit the package, close Phase 3 and
  start Phase 4 if possible.
- **Assessment:** P3.G0 through P3.G4 are accepted, C2-1 is accepted, and Codex
  recommends closing F5/S-2. P3.5's accepted gate contract nevertheless requires
  evidence that is still absent or incomplete: TC-LIM-02, TC-SEC-07's browser
  half, TC-OPS-01…05, TC-PERF-01…03, A-05 criteria 4 and 10, final A-06/R-23
  dispositions, complete traceability and the final two review passes over the
  completed gate package.
- **Decision support:** written procedures, automated tests, an active staging
  service and the filesystem cutover cannot be treated as execution of those
  supervised procedures. In particular, real-folder apply time and worker peak
  RSS remain unmeasured.
- **Dependency effect:** the overall Phase 3 gate remains open. Implementation-
  plan §12 and the accepted Phase 3 delivery plan prohibit Phase 4 implementation
  before Peter records that gate after its mandatory evidence and reviews.
- **Next work:** complete the P3.5 staging evidence package. Phase 4 planning may
  occur only within the roadmap's explicit planning allowance; no Phase 4 code,
  schema, migration, behavior or cutover work is authorized here.
- **Evidence:**
  `docs/review/phase-3-gate-disposition-2026-08-25.md`.

## C-P3.5-T — Three P3.5 decisions recorded: real Foundry data in staging, the TC-PERF-02 repeat-run method, and the A-05 criterion 4 split

**Date:** 2026-08-25 · **Requester / Acceptance Authority / Data Owner / Security
Reviewer:** Peter Duscha · **Prepared by:** Claude, working Technical Lead ·
**Status:** all three decided and recorded. **Nothing is closed, no RAID
disposition moved, and no host action is authorized by this entry.**

### Affected requirement, milestone and release

P3.5 gate-evidence package. RAID **I-06** (staging/browser/device evidence),
**A-05** (protected administrator and credentials) and **A-06** (PostgreSQL as
job-queue and limiter substrate). Traceability contract §17 rows **TC-PERF-01**,
**TC-PERF-02** and **TC-OPS-03**. Execution-plan §§8.2, 11.2, 11.4 and 13.2. No
release boundary, phase order or roadmap item changes.

### The three decisions

| ID | Decision | Deciding role |
|---|---|---|
| **D-l** | A real `the-guild` Actor folder may be submitted to `freedom_staging` as a **supervised operational input** for TC-PERF-01/02 and TC-OPS-03 | **Data Owner** |
| **D-m** | TC-PERF-02's apply is measured as **one real run reported as n = 1**, plus two bounded-synthetic runs | **Acceptance Authority** |
| **D-n** | A-05 criterion 4 splits into **4a** (observable, retained) and **4b** (production refusal, **moved to the deployment gate**) | **Security Reviewer** |

### Reason, and alternatives considered

- **D-l.** The traceability contract §17 requires a **real** 32-Actor folder for
  TC-PERF-01 and a **real**-folder apply for TC-PERF-02, while execution-plan §8.2
  said "synthetic snapshot artifacts only" and §11.4 said "never a real Actor
  payload". The two cannot both hold. *Alternative considered and rejected:*
  satisfy the rows synthetically. Rejected because the accepted contract and the
  P3.5 handover both state that a synthetic Actor apply **is not evidence**, and
  because the known weakness of the existing synthetic benchmark — Actors ~233×
  smaller than real ones (RA-5) — is precisely what makes a synthetic measurement
  untrustworthy here.
- **D-m.** §11.2 asked for three apply runs. `uq_snapshot_imports_applied_input`
  and `snapshot_imports.request_key` make runs 2 and 3 against one input return
  the already-committed effect as a **duplicate** — the commit fence working as
  designed. *Alternatives considered:* (a) three distinct real folder
  submissions — rejected as three times the data exposure and operator time for
  variance on a figure whose value is its realism, not its precision; (c)
  truncating staging import tables between runs — rejected as a privileged
  mutation repeated mid-measurement, which changes the conditions it is meant to
  hold constant.
- **D-n.** Criterion 4's production half cannot be observed before production
  exists, and A-05 gates the exposure that would create production. *Alternative
  considered and rejected:* hold criterion 4 open until production configuration
  exists — rejected because it makes A-05 permanently unclosable and therefore
  makes the gate it guards unreachable, which is not what the criterion was
  written to do.

### Added and removed scope

**Added:** a supervised snapshot-transport step before TC-OPS-03 and TC-PERF-01/02
(inventory finding N-3 — the deployed portal exposes no submission route); one
throwaway disposable-database observation for criterion 4a; a named go-live check
at the deployment gate for 4b. **Removed:** nothing. **Superseded:** §8.2's
synthetic-only Foundry rule, **for TC-PERF-01/02 and TC-OPS-03 only** — it stands
unchanged for every other procedure and artifact.

### Dependency and critical-path effect

**SP-11, SP-15, SP-16 and A-06's input rule move from `Blocked` to `Not Run`** —
roughly two of the four-and-a-half attended hours are released. A-05 moves from
**two** criteria outstanding to **one** open criterion (4a, executable) plus
criterion 10 (the Security Reviewer's final confirmation, which by its own terms
comes last). **SG-2 is now the only thing gating execution of every remaining
I-06 procedure.** The Phase 3 gate remains open and the critical path is unchanged
in shape.

### Estimate, forecast and capacity effect

No change to the accepted 3/5/8-day implementer range. D-m **reduces** attended
time by avoiding two extra real submissions. D-n **adds** roughly fifteen attended
minutes (criterion 4a) and moves an unbounded, currently unsatisfiable obligation
off the P3.5 critical path onto the deployment gate. No calendar date is committed;
availability windows (P-7) are still not recorded.

### New or changed risks

- **Real character-sheet data now enters `freedom_staging`.** Mitigated by the
  Rehearsal A/B discipline, binding here: never committed; no Actor name, payload
  or warning text in any artifact; artifact shredded and import tables truncated
  at teardown; screenshots synthetic-only. The Data Owner authorized this
  explicitly and noted the payload is character-sheet data.
- **TC-PERF-02's real figure is single-sample and must be reported as such.** The
  risk is a reader treating n = 1 as a median. Mitigated by requiring the
  submission to state it as single-sample, with variance carried by the synthetic
  pair and the shaping method recorded alongside (§11.4).
- **4b becomes an obligation owed elsewhere.** The risk is that it is forgotten at
  go-live. **Mitigated concretely rather than by intention:** it is landed as
  `docs/contracts/phase-3-operational-contract.md` §7 **item 10**, added by
  addition, carrying its provenance (D-n / C-P3.5-T) and the reason it cannot be
  observed earlier. Item 9 already required S-01…S-15 to be demonstrated failing;
  item 10 names S-15's production branch separately because it is the one member of
  that set no staging process can produce.
- **Unchanged:** N-13 still requires two enabled credentials and still refuses
  retirement below two. No control is weakened by any of the three decisions.

### Testing, migration, security and operational effect

No schema, migration, route, view-model or numeric-policy change. No application
code changes. `VIEW_MODEL_VERSION` is unaffected. Criterion 4a runs a **second,
throwaway** process against the disposable `freedom_dev` with **synthetic**
credential records; the deployed staging portal is untouched and the protected
account's real credentials are never manipulated. The transport step for D-l is
supervised, targets staging only, and adds no route to the deployed proxy without
SG-2.

### Product Owner recommendation

Recommended by Claude, working Technical Lead, in
`docs/review/phase-3-p3-5-evidence-inventory-2026-08-25.md` §§6 (findings N-2,
N-4) and 3.1 (criterion 4). The folder choice within D-l — `Characters (active)`
as primary, the inactive folder additionally only if it holds more than 32
Actors — was taken by the Technical Lead under the execution plan's §2 audience
rule after the Data Owner expressed no preference, and is recorded in §0.2 D-l
rather than referred back.

### Technical Lead and specialist reviews

D-n's premise was **verified in code on 2026-08-25**, not carried forward on
trust: `WebEnvironment.is_production` is `PRODUCTION` alone
(`application/web/config.py:431`); S-15 appends a `ConfigurationProblem` only
`if settings.environment.is_production` and otherwise a `StartupWarning`
(`application/web/startup.py:205-212`). This confirms the 2026-08-24 addendum
§5.2.1 analysis. **Neither Codex review pass has seen these three decisions.**
Both required P3.5 passes — the independent implementation/evidence review and the
distinct security-focused review — remain outstanding and will see them.

### Dated Acceptance Authority decision

- **D-l — accepted by Peter Duscha, Data Owner, 2026-08-25.**
- **D-m — accepted by Peter Duscha, Acceptance Authority, 2026-08-25.**
- **D-n — accepted by Peter Duscha, accountable Security Reviewer, 2026-08-25.**

**Explicitly not granted by this entry:** SG-2, SG-3, any privileged or host
action, public exposure, closure of I-06, A-05, A-06 or R-23, the Phase 3 gate,
or any Phase 4 work.

### How each decision is reversed

Peter's stated requirement is that these remain changeable later. Each is
reversible on its own, and none silently invalidates evidence already collected:

| Decision | Reversal | What it costs |
|---|---|---|
| **D-l** | Restore §8.2's synthetic-only rule to cover all procedures. | TC-PERF-01/02 and TC-OPS-03 return to **Blocked** and I-06 cannot close. Any real-folder measurement already taken remains **true and citable as an observation**, but stops being admissible evidence for those rows. The teardown obligations — shredding, truncation — are unaffected and still apply. |
| **D-m** | Require three real runs. | Needs three distinct real folder submissions and three operator sittings. A single-sample figure already recorded stays valid as one of the three. |
| **D-n** | Delete 4a/4b and restore the struck-through criterion-4 wording (kept in place for exactly this purpose, execution plan §13.2). | A-05 returns to Open on criterion 4 until a production deployment exists, reinstating the circularity. **No 4a evidence is invalidated:** a below/at observation under the staging marker remains true whatever the criterion is named. |

### Evidence

`docs/review/phase-3-p3-5-evidence-inventory-2026-08-25.md` §§3.1, 6, 8, 10 ·
`docs/review/phase-3-p3-5-readiness-and-execution-plan.md` §0.2 rows **D-l**,
**D-m**, **D-n** and §13.2 criterion 4 (amended by addition) ·
`docs/project-management/raid-register.md` A-05 row ·
`docs/project-management/status.md` updates sixty-three to sixty-five.

## C-P3.5-U — D-n corrected after Codex finding B-1: S-15's pre-exposure observation stays inside A-05

**Date:** 2026-08-26 · **Prepared by:** Claude, working Technical Lead ·
**Reviewer whose finding forced it:** Codex, interim review 2026-08-26, finding
**B-1 (Blocking)** · **Status:** implemented; **requires Peter Duscha's
confirmation as accountable Security Reviewer**, because it supersedes a decision
he recorded.

**This entry supersedes the 4b half of D-n (C-P3.5-T). D-l, D-m and 4a are
unaffected.**

### Affected requirement, milestone and release

RAID **A-05** closure criterion 4. `phase-3-p3-5-readiness-and-execution-plan.md`
§13.2 and §0.2. `phase-3-operational-contract.md` §7 items 9 and 10. No release
boundary, phase order or roadmap change.

### What was wrong

D-n moved S-15's production-refusal evidence out of A-05 to the deployment gate,
arguing that the refusal requires `WEB_ENVIRONMENT=production` while A-05 gates
public exposure, so the criterion could never close.

**The argument treated "production-marked" and "publicly exposed" as the same
event. They are not**, and the whole amendment rested on that conflation. A
production-marked process can be exercised with **no listener at all**:
`run_resource_checks` is a plain function (`application/web/startup.py:80`), so
S-15's production branch is reachable without uvicorn, without a bind and without
a route. S-02, S-05 and S-07 requiring the accepted production identity make such
an exercise **more** controlled, not public.

**The consequence, stated plainly: D-n weakened a security precondition while
appearing to resolve a circularity that did not exist.** It also left operational
contract §7 internally inconsistent — item 9 required S-01…S-15 to be
demonstrated failing while item 10 asserted S-15 could not be observed before
that gate.

### The correction

| Half | Before (D-n) | After (D-o) |
|---|---|---|
| **4a** | Staging-marker below/at threshold observation | **Unchanged** |
| **4b** | Moved to the deployment gate; **not** an A-05 criterion | **Stays an A-05 closure criterion**, discharged by the new guarded exercise **SP-27** |
| **4c** | — | Deployment-gate re-observation retained as **defence in depth**, explicitly *additional* to 4b and never a substitute |
| §7 items 9/10 | Item 10 implicitly narrowed item 9 | **Reconciled explicitly**: item 9 stands unqualified; item 10 is a re-observation; neither substitutes for 4b |

**SP-27, the guarded exercise**, is defined in full at §13.2 criterion 4b:
a disposable `freedom_production` database seeded with **synthetic** credential
records and never restored from real data; outbound egress blocked by the
`iptables` rule already proven by SP-25; `run_resource_checks` called **directly**
so no socket is ever opened; the literal S-15 refusal recorded; the at-threshold
pass recorded; then database dropped, rule removed, environment file deleted.
**No credential material, no real client secret and no value from a live
production system is recorded.** Owner: Peter authorizes and supervises, ~20
minutes.

### Reason and alternatives considered

*Alternative rejected:* hold the original D-n. Rejected because a Blocking review
finding identified a false premise, and the amendment's only justification was
that premise. *Alternative rejected:* revert to the unamended criterion 4 and stop
there. Rejected because it would leave the criterion's wording unchanged while
the practical question — *how* is the production branch observed safely — stayed
unanswered, which is what produced the bad amendment in the first place.

### Dependency, estimate and risk effect

**A-05 gains one executable criterion rather than losing one.** Attended time
rises by roughly 20 minutes (SP-27); nothing else in the run sheet moves. **Risk
is reduced**, not added: the pre-exposure S-15 evidence is restored, and the
deployment gate keeps a re-observation it would not otherwise have had. The new
risk introduced is the exercise itself — a production-identity configuration
existing briefly on this host — and it is controlled by the no-listener design,
the synthetic-only database, the egress block and the recorded teardown.

### Testing, migration, security and operational effect

No schema, migration, route, view-model, numeric-policy or application-code
change. `VIEW_MODEL_VERSION` unaffected. **N-13 is unchanged** and retirement
below two is still refused. SP-27 touches no production service and no real data.

### Technical Lead and specialist reviews

Raised by **Codex** as Blocking finding B-1 in the 2026-08-26 interim review.
Remediated by Claude the same day. **Returns to Codex for re-review.**

### Dated Acceptance Authority decision

**Outstanding.** D-n was approved by Peter Duscha as accountable Security Reviewer
on 2026-08-25; this correction **supersedes the half of it that he approved** and
therefore requires his confirmation. It is implemented rather than held because it
**re-imposes** a control he had agreed to relax — remediation toward the accepted
baseline after a Blocking finding, not a new relaxation — but it is not treated as
decided until he records it.

### How to reverse

Restore D-n's wording, and 4b returns to the deployment gate. **This reversal
should not be taken without disposing of B-1**, because it reinstates the finding.

### Evidence

`phase-3-p3-5-readiness-and-execution-plan.md` §13.2 criterion 4a/4b/4c and §0.2
row **D-o** · `phase-3-operational-contract.md` §7 items 9–10 and the reconciliation
that follows them · `phase-3-p3-5-codex-interim-review-2026-08-26.md` finding B-1.

## C-P3.5-V — the P3.5 authority decisions of 2026-08-26, and the two criteria they had to repair first

**Date:** 2026-08-26 · **Requested by:** Claude, working Technical Lead, in
`docs/review/phase-3-p3-5-authority-request-2026-08-26.md` · **Decided by:**
Peter Duscha, in the roles named against each item · **Status:** decided and
recorded; the repository changes it authorizes are applied.

### What was decided

| # | Item | Role | Decision |
|---|---|---|---|
| 1 | **D-o** and change-log **C-P3.5-U** — S-15's pre-exposure observation returns to A-05 | Security Reviewer | **Confirmed** |
| 2 | **SG-2** — the staging build and its named procedures | Operations Owner | **Granted** |
| 3 | **SG-3 extension** — M-1b and M-1c only, with his presence at every assigned step | Operations Owner | **Granted** |
| 4 | Deploy the reviewed **N-7** fix by service restart, and re-run **SP-12** over a fresh journal interval | Operations Owner | **Authorized** |
| 5 | **SP-27** exactly as specified | Operations Owner and Security Reviewer | **Authorized** |
| 6 | Window | Delivery Lead | **Today, 2026-08-26**, excluding 20:30–22:30 MET |
| 7 | **D-p** — A-05 criterion 4a's disposition | Security Reviewer | **Option 1** |
| 8 | **D-q** — SP-10's instrument | Operations Owner | **Route A** |

Items 2–5 are **authorizations**, not baseline amendments, and are recorded in
the execution plan's §0.2 checkpoint table. Items 1, 7 and 8 change accepted
material and are the substance of this entry.

### Affected requirement, milestone and release

RAID **A-05** closure criterion 4a · `phase-3-p3-5-readiness-and-execution-plan.md`
§0.2 and §13.2 · `infra/postgresql/backup-restore-drill.sh` and its stated
refusal · RAID **I-06** procedure SP-10. **No release boundary, phase order or
roadmap change**, and no change to any authentication, authorization,
persistence, route or view-model contract.

### D-p — A-05 criterion 4a was not executable as written

**The defect.** Criterion 4a required the threshold observation "under
`WEB_ENVIRONMENT=staging`" **and** "on a **disposable** database with
**synthetic** credential records". Those cannot both hold.
`DatabaseSettings.from_mapping` binds each environment to exactly one database
name (`adapters/database/config.py:66`), so a staging-marked process must target
`freedom_staging` — on this host the **deployed** staging database, holding the
protected account's two **real** credentials, which the same criterion forbids
manipulating. **Established by observing the refusal (S-01), not by reading the
rule.**

This is the same shape as Codex finding B-1: two halves of one criterion that
cannot both be satisfied. It was found while building the harness *for* the
criterion, which is the argument for building harnesses before sittings rather
than during them.

**The decision.** Option 1: take the observation under the **`development`**
marker against the disposable `freedom_dev`, with synthetic credential records.

**Why this weakens nothing.** S-15 branches on `settings.environment.is_production`
alone (`application/web/startup.py:205-212`), and `WebEnvironment.is_production`
is `PRODUCTION` alone (`config.py:431`). `development` and `staging` therefore
take the **identical** branch — the warning path — and the observation is the
same observation. The live `environment: staging` marker is separately evidenced
on the deployed portal by `/healthz` (inventory O-2).

**What it gives up, recorded rather than glossed:** no observation of the
threshold *under the staging marker itself*, and no running portal process
answering `/healthz` with `break_glass_credentials:false`. The false state is
evidenced by the S-15 warning instead.

**Declined:** option 2, a throwaway second PostgreSQL cluster carrying a
disposable `freedom_staging` — satisfies the wording literally, costs a cluster
and a new moving part on the host; option 3, temporarily disabling one real
credential on deployed staging — **excluded by the criterion's own text**, and
not recommended.

**How to reverse.** Restore criterion 4a's `staging` wording and adopt option 2;
no evidence collected under option 1 is invalidated, because the branch observed
is the same one.

### D-q — the backup/restore drill had no staging target

**The defect.** SP-10 is TC-OPS-02's **staging half**, and
`infra/postgresql/backup-restore-drill.sh` refused any target but `freedom_dev`
and `freedom_test` **by design**, stating that refusal in its own header. The
procedure had no instrument.

**The decision.** Route A: the script accepts `freedom_staging` behind **two
independent, non-default signals** — `FREEDOM_DRILL_ALLOW_STAGING=1` **and**
`FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging` — with a loud banner when the
path is taken. **Production keeps no override at all.**

**This is a real weakening of a stated invariant**, and is recorded as one. It
was taken because plan §14.3 requires "restore tests, not merely backup success
messages": route A keeps the automatic table-and-row inventory comparison that
makes TC-OPS-02 a *verified* restore, where route B — a hand-run procedure with
no falsifying test — would not.

**Fencing, and a defect fixed while the file was open.** The permitted-database
list was previously written twice, once for the requested name and once for the
**connected** name; the second is the security-relevant copy. It is now computed
once and used by both gates. Every connection proof — the libpq-configuration
refusals, the `PGHOSTADDR` refusal, the loopback-TCP refusal, the Unix-socket
requirement and the landed-database comparison — is untouched and still runs
before anything is dumped or dropped.

**Applied 2026-08-26** with three falsifying tests in
`tests/test_database_backup_restore.py`: staging refused without **both**
signals; production refused **with** them; and the staging name gate shown to
**open** — proved without ever drilling staging, by supplying both signals plus a
hostile `PGHOSTADDR` and asserting exit `3` (connection refused, nothing touched)
rather than exit `2` (name refused). Suite: **33 passed**.

**How to reverse.** Restore the two `case` statements and delete the three tests;
SP-10 then returns to route B and its evidence is correspondingly weaker.

### Impact

- **Scope:** unchanged. **Estimate:** unchanged; the two repairs cost about an
  hour of preparation already spent.
- **Risk:** D-q is a deliberate reduction in one script's refusal surface,
  bounded by two signals, a banner, an unchanged production refusal and three
  tests. D-p removes no observation and changes no threshold.
- **Testing:** three tests added; bot suite **2420 passed** after the change.
- **Migration and operations:** none. No schema, no service, no configuration.

### Evidence

`phase-3-p3-5-authority-request-2026-08-26.md` §§0, 5a, 5b ·
`phase-3-p3-5-readiness-and-execution-plan.md` §0.2 rows **D-o**, **P-3**,
**P-4**, **D-p**, **D-q** · `phase-3-p3-5-c8-staging-drill-guard-proposal.md` ·
`phase-3-p3-5-supervised-run-sheets.md` §13 findings **N-10** and **N-11** ·
`infra/postgresql/backup-restore-drill.sh` · `tests/test_database_backup_restore.py`.

## C-P3.5-W — the 2026-08-26 evening decisions: the gate-off window and the performance bounds

**Date:** 2026-08-26 · **Requested by:** Claude, working Technical Lead ·
**Decided by:** Peter Duscha · **Status:** decided, recorded, and executed the
same evening.

### What was decided

| # | Item | Role | Decision |
|---|---|---|---|
| 1 | **D-r** — how the staging proxy gate is handled for the browser evidence run | Operations Owner | **Option 1: a tightly bounded gate-off window** |
| 2 | **D-s** — the two performance latency bounds that had no accepted figure | Acceptance Authority | **Accepted as proposed** |

### Affected requirement, milestone and release

RAID **I-06** procedures SP-14 and SP-23 · **A-06** criterion 2 and TC-PERF-03 ·
`phase-3-p3-5-readiness-and-execution-plan.md` §0.2 and §11.3 ·
`tools/snapshot_perf_harness.py`. **No release boundary, phase order or roadmap
change**, and no change to any authentication, authorization, persistence, route
or view-model contract.

### D-r — the bounded gate-off window

**The problem.** The staging site sits behind a Caddy `basic_auth` gate. The
deployed site file states that the gate "must be gone before the final
security-header evidence run", because a `401` in front of the application is not
the response the accepted contract describes and TC-SEC-07 must observe the
application's own answers. Without removing it, M-5's early-response case would
have recorded **Caddy's** answer as the application's — evidence that looked
complete and was wrong.

**The decision.** A tightly bounded window covering the browser evidence, gate
restored immediately afterwards, **both times recorded**. Written up as procedure
**SP-29**.

**What was accepted:** for the window's duration an unreviewed build is reachable
by anyone who knows the hostname, which Certificate Transparency published at
issuance. **What still protected it:** the application's own controls — Discord
OAuth, guild and role verification, CSRF, origin and host checks, the
authentication limiter and the kill switch — which are the controls under test.

**Resequencing this forced, on safety grounds:** M-2, the kill-switch sitting, was
moved **ahead** of the window, because the kill switch is that window's emergency
stop and proving it works before removing the outer protection is the right order
rather than the convenient one.

**Executed 2026-08-26: open `21:24:46Z`, closed `22:01:01Z` — 36 minutes.** Gate
removed with `caddy validate` reporting valid, public routes answering `303` with
no `401`; gate restored, valid, `401` back. A stop condition was written in and
not needed: had the window threatened to outlast the session, it would have been
closed and reopened another day.

**Declined:** an address allowlist (rejected originally because the responsive
checks need a laptop **and** a phone on mobile data), and keeping the gate while
recording TC-SEC-07's browser half `Not Run`.

### D-s — the two latency bounds

**The problem.** Execution plan §11.3 requires every bound to be stated before the
run it judges. Three of the five performance bounds are accepted policy — N-47,
N-45 and change-log C-11's throughput criterion — and were cited. **Two had no
accepted figure anywhere in the numeric register**: `/healthz` latency and the
Council job-status poll latency, both measured while a preview is running.

**The decision.** Accepted as proposed:

| Bound | Limit |
|---|---|
| **TC-PERF-03a** | `/healthz` p95 ≤ 500 ms, max ≤ 2000 ms |
| **TC-PERF-03b** | job-status poll p95 ≤ 1000 ms, max ≤ 3000 ms |

**The rationale, and the framing that made it decidable.** These are **not speed
targets**. The worker is a separate process at N-41's concurrency of 1, so a
preview should barely touch the portal; the bound is a **tripwire for that design
assumption**. A miss would mean the worker *is* blocking the portal, which is an
architectural problem rather than a performance one. It also matters
operationally: a monitor that sees health time out may alert, or an operator may
restart the portal mid-job. 2000 ms sits well inside N-51's 30-second read
timeout, and a health check slower than that is useless to the monitor it exists
for.

**Explicitly accepted with the decision: a miss is investigated, never relaxed** —
the execution plan's standing stop rule.

**Applied to `tools/snapshot_perf_harness.py`** the same evening: both bounds now
print as `ACCEPTED` citing this decision. The test that asserted they were
`proposed` was rewritten rather than deleted, so the mechanism that flags an
**unaccepted** bound is still exercised — accepting these did not quietly remove
the guard.

**Measured against them the same evening:** 984 samples across four job windows,
zero non-200 responses, every p95 ≤ 51 ms. One 1,561 ms maximum during a
27-second apply is recorded as a signal within bound, not as a pass to be
forgotten.

### Impact

- **Scope:** unchanged. **Estimate:** unchanged.
- **Risk:** D-r accepted a bounded, supervised exposure of an unreviewed build and
  closed it in the same session. D-s set two numbers where none existed, framed so
  that a miss is a finding.
- **Testing:** the harness's bounds test rewritten; 12 passing.
- **Migration and operations:** none.

### Evidence

`phase-3-p3-5-readiness-and-execution-plan.md` §0.2 rows **D-r** and **D-s** ·
`phase-3-p3-5-supervised-run-sheets.md` §12A (SP-29) ·
`phase-3-p3-5-staging-and-operations-evidence.md` §§5I, 5J ·
`tools/snapshot_perf_harness.py` · `tests/test_snapshot_perf_harness.py`.

## C-P3.5-X — the supported Foundry core version moves 14.365 → 14.367

**Date:** 2026-08-27 · **Prepared by:** Claude, working Technical Lead ·
**Authorized by:** Peter Duscha — *"Fully documented update and review after"* ·
**Status:** applied in the repository; **the deployed Foundry module has not yet
been updated** (see *What is still owed*). **Independent review is owed and was
made a condition of the authorization.**

### What forced it

The Operations Owner upgraded Foundry between sessions. The module refused to
export (finding **N-25**):

> `Freedom Blades [unsupported_deployment]: This deployment is not the one the
> Freedom Blades platform is configured for: Foundry 14.367 (expected 14.365).
> Nothing was exported.`

**That refusal is the control working**, and it is simultaneously a live
observation of implementation-plan §13.2's mandatory scenario *"unsupported
Foundry version"* — on a real deployment, upgraded by its owner, refusing in
actual use rather than against a fixture. **It is recorded as a pass for that
scenario in the staging evidence §5K.**

It also blocks named gate evidence: **D-m's real n = 1 apply**, and with it
TC-PERF-01's real 32-Actor half and TC-PERF-02's real-folder apply — the
measurement RR-06 records as never taken.

### Affected requirement, milestone and release

`.agents/AGENTS.md` observed baseline · `docs/implementation-plan.md` §Phase 7
deployment facts · `docs/operations/topology.md` · `docs/operations/foundry-snapshot-submission.md`
· `domain/foundry.py` `OBSERVED_DEPLOYMENT` · the Foundry module and its own
check. **No release boundary, phase order or roadmap change**, and no change to
any authentication, authorization, persistence, route or view-model contract.

### What changed

| Location | Change |
|---|---|
| `domain/foundry.py` | `OBSERVED_DEPLOYMENT.core_version` → `"14.367"` |
| `foundry-module/scripts/settings.js` | `DEFAULT_SUPPORTED.coreVersion` → `"14.367"` — the check that actually fired |
| `foundry-module/module.json` **and** `package.json` | `"verified": "14.367"`; **module version 1.0.7 → 1.0.8 in both manifests**. The pair is pinned equal by `test_both_module_manifests_declare_one_version`, because `exporter.version` reaches checksum-bearing audit history and two manifests disagreeing would leave that history unable to say which build produced a row. **I bumped only `module.json` at first and that test caught it** |
| Module tests | `fixtures.mjs`, `projection.test.mjs` fixture worlds |
| Python tests | `test_snapshot_api`, `test_foundry_identity`, `test_submission_database`, `test_snapshot_database`, `fixtures/foundry_actor_sample.json`, `fixtures/foundry_actor_anomalies.json` |
| Documents | AGENTS.md, implementation plan, topology, snapshot-submission operations |

**`system_version` is unchanged at `5.3.3`**, and that is evidenced rather than
assumed: `mismatches()` reports *every* differing field, and the module's refusal
named the core version alone. A system upgrade would have appeared in the same
message.

### What was deliberately **not** changed, and why it matters most

**Three provenance comments still say 14.365, and must.**

```text
foundry-module/scripts/main.js:11        The APIs used, verified against Foundry 14.365.0 on this host
foundry-module/scripts/world-source.js:11  Verified against the installed Foundry 14.365.0 application source
foundry-module/scripts/settings.js:9     What Foundry 14.365 actually does with a setting
```

Those are **records of what was actually read**, not pins. Rewriting them to
14.367 would fabricate verification nobody performed. The same applies to the one
narrative line in the operations document, which is annotated in place instead.

**So the honest statement of this change is:** the pin moved on the strength of
the server-side parser, **not** on a re-reading of Foundry's source. Nobody has
re-verified the module's API usage against 14.367.

### Risk assessment, stated for the reviewer to challenge

**Bounded, and here is the argument.** The pin gates whether an export is
*attempted*; it does not replace validation. On submission the server still
checks schema version, canonical encoding, exporter identity and version, the
folder graph, Actor identity uniqueness, per-Actor item structure and every N-20
limit. **A genuine schema change in 14.367 would surface as a parse refusal, not
as silent corruption.**

**What the argument does not cover:** a change that is schema-valid but
semantically different — a field that keeps its shape and changes its meaning.
No amount of parser validation catches that, and only reading the 14.367 source
or diffing a real export would. **Neither has been done.** The first real export
under 14.367 is therefore also the first evidence, and its preview output —
Actor counts, mapped/unmapped split, and the `legacy_authority_deferred` warning
count — should be compared against the 32-Actor baseline before it is applied.

### A design question raised and deliberately **not** decided here

`SupportedDeployment.mismatches` compares **exact strings**. Every Foundry patch
release therefore stops submission until a human decides — which is what happened
here, and it worked. The alternative is a range or a minimum.

**This change does not touch that**, because moving from exact-match to a range is
a substantive decision about how much version drift may pass unreviewed, and it
would be wrong to smuggle it into a version bump. **Raised for the Independent
Reviewer and the Acceptance Authority as its own question.**

### What is still owed

1. **The deployed module is still 1.0.7.** The check that refuses lives in the
   module, so the Foundry host needs module **1.0.8** installed before any export
   can succeed. That is an Operations Owner action on the Foundry side.
2. **Independent review**, which the Acceptance Authority made a condition when
   authorizing this.
3. The real-folder run itself, once (1) is done.

### Impact

- **Scope:** unchanged. **Estimate:** unchanged.
- **Risk:** as assessed above — bounded by parser validation, with a named
  residual (schema-valid semantic change) that the first real export must check.
- **Testing:** module suite **155 pass**; the Python tests carrying the version
  all pass. One assertion was **improved rather than merely updated**:
  `test_anomaly_fixture_holds_an_unsupported_version_tuple` hard-coded the
  supported tuple and now derives it from `OBSERVED_DEPLOYMENT`, so a future pin
  change cannot silently turn the anomaly fixture into a supported one.
- **Migration and operations:** no schema change. One module re-install.

### How to reverse

Restore `"14.365"` in the four live locations, revert the module version to
1.0.7, and reinstall it. No data is affected, because nothing has been exported
under 14.367.

### Evidence

`phase-3-p3-5-staging-and-operations-evidence.md` §5K (finding N-25) ·
`domain/foundry.py` · `foundry-module/module.json` ·
`foundry-module/scripts/settings.js` · the module and Python test suites.

## C-P3.5-Y — HSTS added to the proxy configuration (finding N-22)

**Date:** 2026-08-27 · **Prepared by:** Claude, working Technical Lead ·
**Authorized by:** Peter Duscha — *"Fine with me. Most important: full
documentation for review"* · **Status:** applied in the repository; **not yet
deployed**; independent review owed.

### What was wrong

Operational contract §4.1 gives Caddy **exactly two jobs**:

> `| TLS | Existing Cloudflare origin certificates … |`
> `| HSTS | max-age at least one year, includeSubDomains only after the Operations Owner confirms no sibling host would break |`
> `| Headers | Adds HSTS; the application owns CSP and the rest … so there is one authority per header |`

**One of the two was not implemented.** Neither `infra/caddy/freedom-blades-test.caddy`
nor the production template `freedom-blades-portal.caddy.tmpl` set HSTS, and no
response carried `strict-transport-security` — observed on the wire during the
SP-29 gate-off window on 2026-08-26.

**The near-miss is instructive.** The production template's comment read
*"Security headers: none here, deliberately … the application owns every one of
them"* and then listed five — CSP, Referrer-Policy, X-Content-Type-Options, COOP,
CORP. That reasoning is **correct for those five** and silently omits the one the
application does not own. A confident, well-argued comment is exactly the kind of
thing a reviewer stops reading.

### Affected requirement, milestone and release

`docs/contracts/phase-3-operational-contract.md` §4.1 (satisfied, not changed) ·
`infra/caddy/freedom-blades-portal.caddy.tmpl` · `infra/caddy/freedom-blades-test.caddy`
· TC-SEC-07 · deployment-gate input §7 item 2. **No release boundary, phase order
or roadmap change.**

### What changed

```caddy
header Strict-Transport-Security "max-age=31536000"
```

added to **both** files, with the template's heading corrected from *"none here"*
to *"one here, and only one"*.

| Choice | Reason |
|---|---|
| `max-age=31536000` | One year — the contract's floor, not a number invented here |
| **No `includeSubDomains`** | Reserved by the contract until the Operations Owner confirms no sibling breaks; **the Foundry hosts are siblings** under `rpgworld.org` |
| **No `preload`** | A submission to a browser-vendor list, close to irreversible |
| At the proxy, not the application | HSTS describes the TLS connection, and TLS terminates at Caddy. The application answers on plain HTTP over loopback and cannot know the visitor's transport was secure — a header it set would be a guess |

### What is accepted by doing this

**On the test hostname it is a real commitment:** every browser that visits will
refuse plain HTTP to `freedom-blades-test.rpgworld.org` for a year. Acceptable
because nothing is served there over HTTP, and it is the posture production will
carry — but it is a commitment, not a no-op, and is recorded as one.

### Testing

**Five tests** in `tests/test_deployment_artifacts.py`, covering **both files by
name**. That matters: the existing parametrised Caddy checks glob `*.caddy` and
`*.example`, so the production `.tmpl` sat **outside every existing check** — part
of why this went unnoticed.

- HSTS present, with `max-age` at or above the one-year floor;
- **no `includeSubDomains`** and **no `preload`** without a decision;
- **the application still owns every other header** — so this remains an
  exception rather than becoming a habit. Two `Content-Security-Policy` headers
  would silently intersect, which is the failure the "one authority per header"
  rule exists to prevent.

**Falsified, not assumed:** the header was removed from one file and the test
observed failing with *"sets no Strict-Transport-Security header (N-22)"*, then
restored.

### What is still owed

1. **Deployment.** `/etc/caddy` is root-owned; the same change and a reload are an
   Operations Owner action.
2. **Re-observation.** TC-SEC-07's header capture should be re-run afterwards to
   see HSTS on the wire, which is the evidence that closes the finding.
3. **Independent review**, as the authorization required.

### How to reverse

Remove the two `header Strict-Transport-Security` lines and the five tests. Note
that browsers which already received the header will keep enforcing it for the
remaining `max-age` — **removal is not immediately effective**, which is itself a
reason the value was kept at the floor rather than longer.

### Evidence

`phase-3-p3-5-staging-and-operations-evidence.md` §5I finding **N-22** ·
`infra/caddy/*` · `tests/test_deployment_artifacts.py`.

## C-P3.5-Z — version compatibility ranges, N-47 raised, and N-45's soft warning built

**Date:** 2026-08-27 · **Prepared by:** Claude, working Technical Lead ·
**Decided by:** Peter Duscha, Acceptance Authority · **Status:** applied in the
repository; the module and the systemd unit are **not yet deployed**;
**independent review is owed and was made a condition.**

### What was decided, and on what evidence

Three numeric-policy changes, all taken **after** the measurements that justify
them rather than before:

| # | Change | Decided |
|---|---|---|
| 1 | Version comparison from **exact equality** to **scoped ranges** | *"I'd accept a version range … I pretty much doubt that Foundry would change fundamental elements like character values in between minor changes."* |
| 2 | **N-47: 1G → 2G** | *"I don't mind to raise the Memory level to 2 GB … the server has 4GB and half of it is OK."* |
| 3 | **N-45 soft warning: 30 → 60 s, and implemented** | *"Times can also go up a bit."* |

**The framing that governs all three**, in the Acceptance Authority's words:
*"The limits are only for breaking a loop or something, not to restrain normal
work."* That is what N-45 and N-47 are, and this entry treats them accordingly.

### 1. Version compatibility ranges

**Before:** `SupportedDeployment.mismatches` compared all four fields by exact
string. Every Foundry build stopped submission until a human decided — which is
exactly what happened on 14.365 → 14.367 (**N-25**), and the refusal worked. It
also means a bug-fix release costs a controlled change, a module re-release and
a maintainer's evening.

**After — ranges scoped to where each product's breaking changes land**, rather
than opened uniformly:

| Field | Rule | Why |
|---|---|---|
| `world_id`, `system_id` | **exact** | Identities, not versions |
| Foundry core | **generation** (`14.x`) | Builds within a generation are fixes to the *application*. `module.json` already declared `"minimum": "14", "maximum": "14"` — this aligns the module's own check with a statement it was already making |
| Game system | **major.minor** (`5.3.x`) | The system defines the **Actor schema**. `5.3.4` is accepted; `5.4.0` still stops for a decision. This is the half where a real change would hurt, and the Acceptance Authority chose to open it only to patch level |

**Fail closed on anything unreadable.** Every component is validated, not only
the compared prefix — an earlier draft checked the head alone and accepted
`14.x` and `5.3.3-beta` because their tails were never read. **A prerelease game
system is precisely the case that should stop and ask**, since a beta is where an
Actor schema is most likely to move.

**Both sides changed together.** The module refuses before assembling a bundle;
the server refuses on submission. Two different rules would mean an export the
module allowed and the server rejected — or, worse, one the module allowed and
the server accepted when it should not have. `versionSeries` in
`foundry-module/scripts/bundle.js` and `SupportedDeployment._series` in
`domain/foundry.py` are deliberately identical, and each says so.

**A 14-row compatibility table is duplicated in both test suites** —
`tests/test_foundry_identity.py` and
`foundry-module/tests/deployment-range.test.mjs` — with each noting that the two
must agree. Boundaries covered: older and newer builds in-generation, the next
and previous generation, a system patch, the next system minor and major, a
version with too few components, a non-numeric component and a prerelease.

**Refusal messages now name the accepted *series*** — "expected the 14.x series"
rather than "expected 14.367" — so an operator learns what would be accepted, not
only what failed.

**Module bumped 1.0.8 → 1.0.9** in both manifests: the comparison behaviour
changed, and `exporter.version` reaches checksum-bearing audit history.

### 2. N-47 raised from 1 GiB to 2 GiB

**RR-05 is closed by measurement**, which is what made this decidable. A real
32-Actor folder peaked at **302 MiB**. The same-sized synthetic fixture peaked at
185 MiB, and real Actor data costs **~13–15× its input size** where the fixture
cost ~7.5× (**N-26**) — so extrapolating to N-20's 64 MiB ceiling reaches
**~1 GiB, at the old bound**.

**The host is 7,872 MiB, not the 4 GB the Acceptance Authority assumed** when
offering "half of it". 2G is therefore **a quarter of the host** and roughly
**twice the worst realistic case** — better justified than when it was offered.

**The trade, stated:** `MemoryMax` is a kill threshold, not a reservation.
Raising it protects the *job* slightly more and the *shared host* slightly less,
and the host carries the live Discord bot, three Foundry instances and
PostgreSQL (R-24). At 7.7 GB total that is acceptable.

### 3. N-45's soft warning — raised, and built

**It did not exist.** The register has said "soft warning at 30 seconds" since
P3.3 and **nothing in the worker, the runtime or the adapters ever emitted one**.
The only other place the number appeared was a constant in the performance
harness, which had copied it *from the register*.

**This is the same shape as finding F6**, where S-15's warning was computed,
returned and read by nothing. A documented control that is not a control reads
as protection and is not.

**Implemented** in `application/worker/runtime.py`: a latched `LOGGER.warning`
when an attempt first crosses the threshold.

- **60 rather than 30**, decided with the measurement in hand: a real preview at
  the N-20 ceiling extrapolates to ~39 s, so 30 would fire on legitimate work at
  the top of the accepted input range, and a warning that cries wolf is one an
  operator learns to scroll past.
- **Latched**, because the loop runs once per heartbeat and an attempt near the
  300 s cap would otherwise log a dozen times and bury the journal.
- **Carries an opaque job UUID and two numbers.** No snapshot, Actor, character
  or identity value — TC-OPS-05 checks monitoring output for exactly that.
- **A module constant, not a configurable bound.** This is a log threshold, not a
  control; making it configurable would mean a new environment variable, a
  `WORKER_BOUNDS` entry and an S-10 ceiling — more than a journal line warrants.
- The harness constant is now **pinned equal** to the shipped one by a test, so
  the two cannot drift. Before today there was nothing to drift from.

**A test-quality note, recorded because it was nearly shipped.** The first
version of the latch test **reimplemented the latch inline and asserted against
the copy** — it would have passed with the real latch deleted, while its module
docstring claimed to "drive the real `_run` loop". It is replaced by a source
assertion that fails if the latch is removed, and **the module docstring now
states plainly that the latch is covered by reading rather than execution**, with
the integration test that would cover it properly named as a follow-up.

### Impact

- **Scope:** unchanged. **Risk:** the version widening is the substantive one; it
  is bounded by the parser, by identity fields staying exact, by the system range
  stopping at minor, and by fail-closed parsing.
- **Testing:** module **171 pass** (+16); Python compatibility table 14 rows;
  N-45 4 tests; harness pin 1 test.
- **Deployment owed:** module **1.0.9** to the Foundry hosts, and
  `MemoryMax=2G` to the deployed unit — the running worker still has 1G.

### A control gap this change exposed, and closed — N-27

The scope guard `test_no_unrelated_production_files_modified` stopped the
`application/worker/runtime.py` edit until it was declared, which is exactly its
job. It did **not** stop the `domain/foundry.py` edit — the version comparison
that is the substance of this entry — because it watched `adapters/`,
`application/` and templates and **not `domain/`**.

`domain/` holds the rules. An undeclared change there matters most, not least.

**Closed in the same commit:** `domain/` is a fourth watched prefix and
`domain/foundry.py` is declared against this entry. The guard was **falsified** —
an undeclared `domain/` change was made, observed failing, and reverted.

**The pattern is worth naming.** This package has now found four controls that
were described somewhere and implemented nowhere: **N-22** (HSTS required by the
operational contract, configured in neither Caddy file), **N-45** (a soft warning
in the numeric register, emitted by nothing), **F6** (S-15's warning, computed
and read by nothing) and **N-27** (a scope guard blind to a whole layer). Each
was found by looking, none by a check designed to find them.

### How to reverse

Restore exact comparison in both `mismatches` and `assertSupportedDeployment`,
revert `MemoryMax` to `1G`, delete `SOFT_WARNING_SECONDS` and its use. No data is
affected by any of the three.

### Evidence

`domain/foundry.py` · `foundry-module/scripts/bundle.js` ·
`application/worker/runtime.py` · `infra/systemd/freedom-worker.service.tmpl` ·
`docs/contracts/phase-3-numeric-policy-register.md` N-45 and N-47 ·
`phase-3-p3-5-staging-and-operations-evidence.md` §5L finding **N-26**.

## C-P3.5-AA — N-47's raise carried into the harness that measures against it (finding N-28)

**Date:** 2026-08-27 · **Prepared by:** Claude, working Technical Lead ·
**Status:** applied in the repository; **repository-only, nothing deployed**;
**independent review is owed** as part of EX-11.

*The alphabet is exhausted at Z; entries continue `AA`, `AB`, ….*

### What changed, and why it is a correction rather than a decision

C-P3.5-Z raised N-47 from 1 GiB to 2 GiB. **This entry decides nothing new.** It
carries that already-accepted raise into the one place it had not reached:
`tools/snapshot_perf_harness.py`, which reports a measured peak *as a fraction of
N-47* and warns above 75% of it.

| File | Change |
|---|---|
| `tools/snapshot_perf_harness.py` | `N47_MEMORY_MAX_BYTES` 1 GiB → **2 GiB**, with the raise and its reason in the comment; the bound's printed limit and the two prose statements of the ceiling follow it |
| `tests/test_snapshot_perf_harness.py` | the literal pin `assert N47_MEMORY_MAX_BYTES == 1024**3` is **removed** and replaced by `test_the_memory_ceiling_matches_the_shipped_worker_unit`, which parses `MemoryMax=` from `infra/systemd/freedom-worker.service.tmpl` and converts the suffix |

### Why the old test did not prevent this

It pinned the constant to a **literal**, so it asserted only that the harness
agreed with itself. The sibling pins in the same test do it properly — throughput
against `tests/benchmark_snapshot_500`, the soft warning against the shipped
worker constant — which is why those two did not drift and this one did. The
replacement makes the systemd unit the single source of the figure.

### Effect

**No measurement in P3.5 changes.** TC-PERF-01 recorded **302.4 MiB**, inside
both the old and the new ceiling. The defect was forward-looking: against the
stale divisor the harness would have overstated every later reading by 2x and
warned at 768 MiB, reporting a compliant 1.1 GiB peak as over the ceiling — a
failure in the safe direction, and therefore one that could have persisted.

### Verification

Falsified before it was trusted: with the unit set to `MemoryMax=1G` the new test
**fails**; restored to `2G` the file's **14 tests pass**. Full suites re-run
after the change — see the submission §6.

### Rollback

Revert the two files. Nothing is deployed and no configuration changed, so
rollback carries no operational step.

### Review status

**Not independently reviewed.** Submitted as part of the P3.5 package for EX-11,
and named in the submission's §5 as the fourth instance of the pattern it
records.

## C-P3.5-AB — EX-11 implementation tasks, and the deployment of three remediations

**Date:** 2026-08-27 · **Prepared by:** Claude, working Technical Lead ·
**Status:** applied in the repository **and deployed**; **independent review is
owed** as EX-11 and EX-12.

**Authority.** Peter Duscha authorized the Codex EX-11 handoff's three
implementation tasks, and then, separately and explicitly the same evening,
each deployment below. This entry records what was done. **It decides nothing,
closes no finding, closes no residual and confers no Phase 4 authority.**

### 1. Implementation — the access-log client pseudonym (Codex EX-11 finding)

`tools/portal_server.py::_pseudonymise_client()` hashed uvicorn's **whole** client
field. uvicorn 0.32.1 builds that field as `"%s:%d" % client`
(`protocols/utils.py::get_client_addr`), so it is `address:ephemeral-port` and
changes on every connection. **The confidentiality property always held; the
correlation property the comments claimed never held at all.**

The address is now extracted and validated before anything is hashed, in every
form uvicorn and a proxy in front of it produce — IPv4 with port, uvicorn's
**unbracketed** IPv6 with port, bracketed IPv6, bare hosts, and the empty
no-client case — and hashed in `ipaddress`' canonical form. The keyed per-process
digest is unchanged and the key is neither logged nor persisted. A value that
cannot be read as an address is still hashed whole, under a distinct
`client-unknown-` prefix that tells a reader the line carries **no** correlation
guarantee.

**A second, pre-existing defect was found by the new tests and fixed.** An IPv6
address *with* a port survived the traceback scrubber **in plaintext** — the
port's colon falls inside the IPv6 candidate's character class, so the token
matched whole, failed to parse, and was returned untouched. IPv4 was protected
there and IPv6 was not. `_scrub_addresses` now falls back to the `host:port`
reading, and the IPv4 branch swallows a trailing port so the families behave
alike. **This strengthens the fallback path and weakens nothing.**

### 2. Implementation — two stale claims corrected

| Claim | Where | Correction |
|---|---|---|
| `MemoryMax=1G`, peak memory "unmeasured" | `application/worker/__init__.py`, `infra/systemd/freedom-worker.service.tmpl` header | 2G, with **measured** (302 MiB, TC-PERF-01) separated explicitly from **extrapolated** (~1 GiB at N-20's ceiling, N-26) |
| `mismatches()` "compares exact strings"; "every patch stops submission" | `domain/foundry.py` (constant comment **and** class docstring), `foundry-module/scripts/settings.js`, `bundle.js` | Restated as the OD-14 v1.6 ranges; the constant names the observed **reference**, not the boundary |
| N-47's 1 GiB as the active ceiling | `docs/contracts/phase-3-threat-model.md` RR-05 | Amended; original text kept for the record; residual narrowed, **not closed** |

An orphaned JSDoc block in `bundle.js` — detached from `assertSupportedDeployment`
when C-P3.5-Z inserted `versionSeries` between them — was reattached.

### 3. Deployment, on explicit authorization

| Item | Result | Rollback |
|---|---|---|
| **HSTS** (N-22) | `/etc/caddy/freedom-blades-test.caddy`, **22:06 UTC**. `max-age=31536000`, no `includeSubDomains`, no `preload`. Captured at the **Cloudflare edge and again at the Caddy origin** — the second proves this platform emits it rather than the edge | `…caddy.before-hsts-20260827T220639Z` |
| **Module 1.0.9** | foundry1, **foundry2** and foundry3; six manifests; content and modes verified against the repository | 1.0.8 snapshotted on foundry1/3; foundry2's is directory removal |
| **`MemoryMax=2G`** (N-47) | **22:43 UTC**. Kernel cgroup `memory.max` = `2147483648` | `…freedom-worker.service.before-n47-2g-20260827T224337Z` |

**Scope change, recorded rather than absorbed.** The handoff named foundry1 and
foundry3; **Peter directed all three**. foundry2 had **never carried this module**
— 57 modules against 58 — so that was a first installation. It matters because one
world is bind-mounted into all three and only one may host it at a time (ADR
0006): an instance without the module cannot export the world it may be asked to
serve.

**Every confirmation was of effect, not of exit code** (N-18). The memory ceiling
was read at three levels, ending at the kernel cgroup. The Caddy reload was
confirmed by the header on the wire with `NRestarts=0` and an unchanged
`ExecMainStartTimestamp`. The worker restart was confirmed by a moved
`ExecMainStartTimestamp`, a new PID, and `/healthz` reporting
`worker_heartbeat: true` — the platform seeing the *new* process.

### 4. The `includeSubDomains` rationale was wrong

Both Caddy files and `test_hsts_does_not_claim_subdomains_or_preload` said the
directive was reserved because it "would cover the sibling Foundry hosts". **It
would not.** `includeSubDomains` binds the sending host and names *beneath* it
(RFC 6797 §6.1.2); `foundry1.rpgworld.org` and its peers are siblings of the
portal names, not subdomains, and are unaffected either way. No block serves the
apex `rpgworld.org`, the only place the reasoning could have applied.

**The omission stands**, on a reason that holds: no name exists beneath either
portal host, so the directive buys nothing today while committing every future
name under it to HTTPS-only for the whole `max-age`. **No assertion and no
directive changed.**

### Effect and what is *not* claimed

**Deployment task 4 — the real Foundry export/preview compatibility check — is
not done.** 1.0.9 is installed on all three instances and **loaded by none**: the
running Foundry processes were deliberately not restarted, because that would
interrupt live sessions. Nothing in this entry demonstrates the v1.6 version
policy behaving on real data.

No migration was added; the schema is unchanged at `0013`. No Foundry world data
was read, exported or mutated. No secret was read, printed or committed.

### Verification

`2447` bot · `2452 passed / 80 skipped` web · `171` module · assets 4/4 · freeze
14/14 · `compileall` clean in both venvs · `alembic` single head `0013`, no
branches · `git diff --check` clean. Formatter, linter and type checker remain
unconfigured (E-9) and are **not** claimed as passed.

The pseudonym correction was **falsified before it was trusted**: reinstating the
defect fails 13 tests; reverting the scrubber fix alone fails 2. Both were
restored and the file re-run green.

### Rollback

Repository changes revert by `git checkout --`. Each deployment has a timestamped
backup or snapshot named above. The one behavioural repository change,
`tools/portal_server.py`, is **not deployed**: the running portal does not contain
it, so reverting it needs no service action.

### Review status

**Not independently reviewed.** This entry is submitted for **EX-11** and
**EX-12**. Peter alone decides the Phase 3 gate.

## C-P3.5-AC — EX-11/EX-12 re-review raises N-29 and N-30

**Date:** 2026-08-28 · **Reviewer:** Codex, Independent Reviewer and separate
security-focused reviewer · **Status:** two open findings; EX-11 and EX-12
recommendations withheld; remediation and re-review required.

### Review outcome

The implementation corrections in C-P3.5-AB were reviewed read-only and the
full configured verification set was independently reproduced. The scoped
Foundry v1.6 behavior, pinned Uvicorn client correlation, HSTS staging capture,
module installation and `MemoryMax=2G` deployment evidence are acceptable as
presented. Two findings prevent either recommendation:

| Finding | Class | Result |
|---|---|---|
| **N-29** | **Blocking** | `tools.portal_server._scrub_addresses()` is explicitly best-effort and does not isolate an address adjacent to word characters. Synthetic input `peer=203.0.113.7suffix` survives unchanged, contrary to operational contract §5's prohibition on plaintext IP addresses in every log line and the unfamiliar-record fallback's fail-closed purpose |
| **N-30** | **Important** | `test_no_unrelated_production_files_modified` watches `adapters/`, `application/` and `domain/`, but not `tools/`. The behavioral access-log change in `tools/portal_server.py` therefore passed undeclared, reproducing N-27's failure class |

### Required remediation

For N-29, an unfamiliar access-log record must fail closed as a whole. It must
not preserve arbitrary rendered input while attempting to discover every IP
literal within it. Retain only bounded, repository-owned metadata known not to
contain caller input, and add regression cases for adjacency, delimiters,
brackets, zones, ports and arbitrary container rendering. The pinned Uvicorn
format may retain its precise redaction path.

For N-30, add `tools/` to the watched prefixes, explicitly allow only the
reviewed P3.5 entry points, and falsify the guard with an undeclared synthetic
`tools/` change before trusting it.

### Remaining operational evidence

The real Foundry export/preview against a process that has loaded module 1.0.9
remains outstanding. The final operational pass must also correct the stale
deployed worker-unit header comment and recheck the Caddy `Server` header when
the gate is removed and a normal response is observable. None of these facts
authorizes interrupting a live Foundry session without Peter's explicit
operational direction.

### Verification independently reproduced

- bot: **2447 passed**, one warning;
- web: **2452 passed, 80 skipped**, 1137 warnings;
- Foundry module: **171 passed**;
- asset integrity: **4/4**;
- visual freeze: **14/14**; and
- `git diff --check`: clean.

No implementation or deployment was changed by the review. Peter alone decides
the Phase 3 gate; Phase 4 remains unauthorized.

## C-P3.5-AD — N-29 and N-30 remediated, and the scope guard completed

**Date:** 2026-08-28 · **Prepared by:** Claude, working Technical Lead ·
**Status:** applied in the repository, **not deployed**; independent review is
owed as **EX-11** and **EX-12**.

**Authority.** The 2026-08-28 Codex handoff authorizes repository remediation,
verification, evidence updates and preparation of the remaining operational
procedure — and nothing else. This entry records what was done. **It decides
nothing, closes no finding, closes no residual and confers no Phase 4
authority.** No Foundry restart, no live-session interruption, no gate removal
and no production deployment occurred.

### 1. N-29 (Blocking) — the unfamiliar access-log record fails closed as a whole

**Reason.** `tools.portal_server._scrub_addresses()` anchored its candidate
pattern on `\b`, so `peer=203.0.113.7suffix` survived unchanged. Operational
contract §5 prohibits a plaintext IP address in **every** metric, log line and
dashboard, and a best-effort control cannot satisfy a requirement with no
exceptions.

**Alternatives considered, and rejected.** A better pattern — rejected because
the defect is the instrument, not its edges: no rule over arbitrary rendered
objects can be shown complete, and this is the third pattern in this file's
history to be found incomplete. Dropping the access log entirely
(`--no-access-log`) — rejected on the same grounds it was rejected for N-7: it
trades a disclosure for an operational blindness.

**What changed.** The filter has two paths and the second emits nothing that came
from the record. The pinned uvicorn 0.32.1 access line keeps its precise
redaction, with **every retained field bounded and validated** and the retained
**request path** scrubbed by a rule closed over its input. Every other record —
including one carrying an exception, a pre-rendered `exc_text` or a stack — is
replaced by `<uvicorn.access record withheld: <reason>>`, with `args`,
`exc_info`, `exc_text` and `stack_info` cleared. The reason is one of six
literals owned by this repository and derived from no value, type, length or
count.

**Found while correcting it, not by the review:** the retained request path is
caller-controlled, so `GET /x203.0.113.7y` disclosed an address through the
branch the handoff keeps. It is scrubbed now.

**Behaviour changed.** Yes — deliberately, and the cost is stated in
`phase-3-p3-5-staging-and-operations-evidence.md` §5Q.1: an unfamiliar record
keeps only the reason it was unfamiliar. On this logger that is close to no cost,
because `uvicorn.access` emits the pinned line and nothing else.

**Falsified before it was trusted.** The tests were written and run against the
submitted implementation first: **68 failed, 73 passed** of the 141 new cases. After the correction,
reinstating each element of it one at a time fails **3, 52, 5, 19 and 8** tests
respectively; restored, the file's **238 tests pass**. Fifteen existing tests
were rewritten, none deleted, each saying in its docstring what it used to assert
and why that is no longer the property to hold.

### 2. N-30 (Important) — `tools/` watched, and the guard completed

**Reason.** `test_no_unrelated_production_files_modified` watched `adapters/`,
`application/` and `domain/` but not `tools/`, so the N-29 behavioural change to
the deployed portal entry point passed undeclared. That is N-27's class exactly:
a guard that does not watch a layer cannot report that it is not watching.

**What changed.**

- `tools/` is watched, and the two entry points genuinely changed are declared
  with their reasons. `tools/breakglass_observation.py` and
  `tools/startup_refusal_probe.py` were assessed and are **not** declared: both
  are committed at `HEAD` and neither is modified in the working tree this guard
  reads. No directory is allowed by prefix.
- The decision became a pure function, `scope_violation(path)`, so an undeclared
  synthetic path is rejected in a test that never reads the working tree. Until
  now the only available demonstration was "everything currently passes", which
  shows the guard ran, not that it can fail — and N-27 and N-30 are both cases
  where it ran and could not fail.
- The porcelain parser was extracted as `status_paths()` and is asserted against
  the forms git actually emits, including a rename and a quoted path with a
  space.
- **Every production layer is watched**, rather than one added per finding. Every
  top-level directory is now either watched or named non-production, and a test
  fails on a directory in neither.

**Added scope, raised rather than absorbed.** The completion pulls in `infra/`
and `foundry-module/`, which carry accepted deployed P3.5 changes (C-P3.5-Y,
C-P3.5-X/Z). Seven files are declared there, file by file. **This is a deliberate
expansion beyond the handoff's `tools/` and a reviewer should confirm it rather
than inherit it.** It grants no new permission: every declared file is an
already-reviewed change. `PERMITTED_P3_5_BACKEND` was renamed
`PERMITTED_P3_5_PRODUCTION` because it no longer describes only backend files;
`phase-3-p3-5-supervised-session-remediation-submission.md` cites the old name
and is left as the historical record it is.

**Falsified four ways**, including the one the working tree cannot give on its
own: an undeclared synthetic change written into a real `tools/` file is caught
by name. Full table in §5Q.2.

### 3. Files changed

| File | Behaviour changed |
|---|---|
| `tools/portal_server.py` | **Yes.** The unfamiliar-record path, the pinned-path field bounds, and the request-path scrub |
| `tests/web/test_n7_access_log_redaction.py` | Tests only. 97 → 238; nine functions (fifteen cases) rewritten, none deleted |
| `tests/web/test_p3_4_static_assets.py` | Tests only. 11 → 43; the guard refactored into `scope_violation()` and `status_paths()` |
| `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` | §5Q and §5R added; the §5.4 bullet that described best-effort as the remediation carries a dated superseding note and is otherwise left as written |
| `docs/project-management/change-log.md` | This entry |
| `docs/project-management/status.md` | Ninety-fifth update |

No migration was added; the schema is unchanged at `0013`. No dependency was
added. No secret, raw snapshot, cookie, token, gate credential or player datum
was read, printed or committed. No live service was touched.

### 4. Verification

Serial, database enabled, on the deployed host, against the submitted tree:
**2447** bot · **2625 passed / 80 skipped** web · **171** module · assets 4/4 ·
freeze 14/14 · `compileall` clean in both venvs · `alembic` single head `0013`,
no branches · `git diff --check` clean. The web figure moves 2452 → 2625 because
173 tests were added. Formatter, linter and type checker remain unconfigured
(E-9) and are **not** claimed as passed.

### 5. Risk, rollback and recovery

**New risk.** If a future uvicorn changes its access-log format, the portal's
access log degrades to a stream of withheld markers until the pin is updated.
That is the intended direction of failure, and
`test_the_pinned_uvicorn_access_contract_still_holds` is what should say so in CI
before anyone reads it in a journal.

**Rollback** is `git checkout -- tools/portal_server.py tests/web/...` and carries
**no operational step**: the corrected file is not deployed, so the running
portal does not contain it. Reverting restores the N-29 behaviour, which is why
the revert is a rollback of a fix and not a remedy.

### 6. What is not done

The four operational items — the running process proven to have loaded module
1.0.9, the real export/preview compatibility check, the stale deployed
worker-unit header comment, and the post-gate `Server` header with TC-SEC-07 —
are **not** run. Each needs Peter's authorization and, for three of them, a
supervised window. They are listed with their reasons in §5R.

### Review status

**Not independently reviewed.** Submitted for **EX-11** (implementation
re-review of N-29, N-30 and all prior Blocking and Important findings) and
**EX-12** (security re-review of the full formatted-log boundary, the pinned
pseudonym behaviour, the unfamiliar-record fail-closed behaviour, HSTS evidence,
loaded-1.0.9 compatibility evidence and the final `Server` header observation if
then available). No finding, residual or gate closes on implementation or green
tests alone. Peter alone records the Phase 3 gate decision; Phase 4 remains
unauthorized.

## C-P3.5-AE — Remediation re-review raises N-31 on the pinned method field

**Date:** 2026-08-28 · **Requester:** Independent Reviewer · **Status:** review
finding recorded; **not accepted, not deployed, EX-11 and EX-12 withheld.**

- **Affected requirement, milestone and release:** Phase 3 P3.5, EX-11 and
  EX-12, operational contract §5's prohibition of plaintext IP addresses in
  every metric, log line and dashboard, and the Phase 3 authentication/security
  gate. Phase 4 remains unauthorized.
- **Reason and alternatives considered:** C-P3.5-AD correctly replaced every
  unfamiliar access-log record as a whole and correctly scrubbed the retained
  request path, but it preserved the retained HTTP method unchanged. The method
  is caller-controlled and the accepted RFC-token expression permits dots and
  digits. A synthetic pinned record with method `203.0.113.7` therefore passes
  the exact-contract checks and emits that plaintext address. Treating method
  syntax validation as confidentiality validation is rejected: those are
  different properties. Restricting the method to a casual list of common verbs
  is also rejected unless the HTTP contract is deliberately changed and
  reviewed; extension methods are valid. The scoped implementation choice is to
  scrub address material from the bounded method or withhold the record when the
  method carries it.
- **Added/removed scope:** one Blocking finding, **N-31**, and its regression and
  evidence. N-30's remediation is satisfactory. The unfamiliar-record half of
  N-29 is satisfactory, but N-31 keeps the overall confidentiality boundary
  open. No implementation, schema, dependency, configuration or deployment was
  changed by this review.
- **Dependency and critical-path effect:** EX-11 and EX-12 remain withheld; the
  Phase 3 gate remains open and Phase 4 cannot start. The four supervised
  operational items in evidence §5R remain outstanding and unchanged.
- **Estimate/forecast and capacity effect:** a narrow code-and-test remediation
  plus two renewed review passes; no calendar forecast is inferred.
- **New or changed risks:** a caller can place an IPv4 literal in a syntactically
  valid method and disclose it through the retained access-log branch. The
  remediation must not regress query removal, per-address pseudonym correlation,
  unfamiliar-record whole withholding, field bounds, installation scope or
  idempotency.
- **Testing, migration, security and operational effect:** reproduced with a
  fully formatted synthetic pinned record. Current-tree verification: focused
  tests **289 passed**; bot **2447 passed**; web **2625 passed, 80 skipped**;
  Foundry module **171 passed**; assets 4/4; visual freeze 14/14; both
  `compileall` checks clean; Alembic single head `0013`, no branches; clean
  `git diff --check`. Formatter, linter and type checker remain unconfigured.
  No migration or operational action occurred.
- **Product Owner recommendation:** none recorded. Peter alone decides the gate.
- **Technical Lead and specialist reviews:** Codex performed the independent
  implementation/security remediation re-review and raised N-31. After
  implementation, request distinct EX-11 and EX-12 passes again.
- **Approval:** **none.** Recording the finding closes neither the finding nor
  the gate.

## C-P3.5-AF — N-31 remediated: an address-bearing method withholds the record

**Date:** 2026-08-28 · **Prepared by:** Claude, working Technical Lead ·
**Status:** applied in the repository, **not deployed**; independent review is
owed again as **EX-11** and **EX-12**.

**Authority.** The 2026-08-28 Codex handoff authorizes repository remediation,
tests, verification and evidence updates only. It does not authorize deployment,
a Foundry restart or world reload, interruption of a live session, removal of the
staging gate, access to secrets or real snapshots, or a gate decision. **This
entry decides nothing, closes no finding and confers no Phase 4 authority.**

- **Affected requirement, milestone and release:** Phase 3 P3.5, EX-11 and
  EX-12, operational contract §5's prohibition of plaintext IP addresses in every
  metric, log line and dashboard, and the Phase 3 authentication/security gate.
  Phase 4 remains unauthorized.
- **Reason and alternatives considered:** C-P3.5-AD bounded every field the
  pinned uvicorn branch retains and scrubbed the retained request path, but it
  examined the method's *syntax* only. An HTTP method is an RFC 9110 token, the
  token alphabet includes digits and `.`, and the method is caller-controlled, so
  `("198.51.100.9:1", "203.0.113.7", "/healthz", "1.1", 200)` passed every check
  and formatted as `client-… - "203.0.113.7 /healthz HTTP/1.1" 200`. Syntactic
  validity is not confidentiality.
  **Rejected:** restricting the method to a list of common verbs — extension
  methods are valid and the handoff forbids that without a reviewed contract
  change; `_HTTP_METHOD` is unchanged. **Rejected:** scrubbing the method in
  place — it leaves `X<pseudonym>Y`, caller-chosen characters around a removed
  span in a field with no operational meaning left. The request path is scrubbed
  rather than withheld because a path with an address removed is still a route an
  operator can read; a method is not. **Chosen:** the handoff's preferred option,
  withhold the whole record, which is the fail-closed shape the unfamiliar path
  already has.
- **Added/removed scope:** one check, one helper (`_carries_address_material`)
  and a seventh withheld reason (`address-bearing-method`) in
  `tools/portal_server.py`; 172 tests in `tests/web/test_n7_access_log_redaction.py`
  (238 → 410); one declaration comment in `tests/web/test_p3_4_static_assets.py`.
  No route, view model, schema, migration, dependency, configuration or
  deployment artefact changed.
- **Dependency and critical-path effect:** none beyond the two re-reviews it
  requests. The four supervised operational items in evidence §5R remain
  outstanding and were not attempted.
- **Estimate/forecast and capacity effect:** a narrow code-and-test remediation
  within the existing package. No calendar forecast is inferred.
- **New or changed risks:** the access log loses a record whose method carries an
  IP literal, rather than logging a redacted version of it. No standard verb,
  WebDAV method or vendor extension can contain a dotted quad, so this reaches no
  real traffic; a withheld line naming `address-bearing-method` is itself the
  signal that a caller tried. **The completeness claim is bounded and stated:**
  the method alphabet contains no `:`, so no IPv6 literal is expressible in a
  method at all, and the remaining IPv4 dotted quad is found by the rule N-29
  already accepted for the request path — the detector asks whether that rule
  would change the method, so it cannot drift from it. A method spelling an
  address in another encoding is not a plaintext address and is not detected;
  that is the same boundary the accepted request-path rule has.
- **Testing, migration, security and operational effect:** the regression was
  written first and run against the reviewed tree: **68 failed, 342 passed**, and
  **no pre-existing test failed**, which is the evidence that it isolates N-31.
  After the correction the file passes **410**. Reinstating each element one at a
  time fails **67** (the method passed through unchanged again), **2** (detection
  by one greedy unvalidated scan, caught as over-refusal on
  `999.999.999.999`) and **46** (the method scrubbed instead of the record
  withheld). The scope guard was falsified against this edit: with
  `tools/portal_server.py` undeclared it reports the file, 2 failed; restored, 43
  passed. Full serial verification with the database enabled: bot **2447
  passed**; web **2797 passed, 80 skipped**; Foundry module **171 passed**;
  focused **453 passed**; assets 4/4; visual freeze 14/14; both `compileall`
  checks clean; Alembic single head `0013`, no branches; clean `git diff --check`.
  Formatter, linter and type checker remain unconfigured (E-9) and are not
  claimed. **No migration, no deployment and no operational action occurred**;
  the corrected entry point is not on the running portal, so reverting needs no
  service action.
- **Product Owner recommendation:** none recorded. Peter alone decides the gate.
- **Technical Lead and specialist reviews:** requested again as two distinct
  passes — **EX-11**, implementation re-review of N-31 and preservation of all
  prior Blocking and Important remediations; **EX-12**, security-focused
  re-review of the fully formatted pinned and unfamiliar log boundaries, client
  correlation, HSTS evidence, loaded-module compatibility evidence and the final
  `Server` header observation if available.
- **Approval:** **none.** No finding or gate closes on implementation or green
  tests alone.

Evidence: `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` §5T.

## C-P3.5-AG — N-31 accepted in code; N-32 raises probabilistic test evidence

**Date:** 2026-08-28 · **Requester:** Independent Reviewer · **Status:** review
finding recorded; **not accepted, not deployed, EX-11 and EX-12 withheld.**

- **Affected requirement, milestone and release:** Phase 3 P3.5, EX-11 and
  EX-12, operational contract §5's access-log confidentiality evidence and the
  Phase 3 authentication/security gate. Phase 4 remains unauthorized.
- **Reason and alternatives considered:** C-P3.5-AF's N-31 production correction
  is satisfactory. A fresh-process rerun exposed two older assertions that split
  an unfamiliar client value into fragments and require every fragment of three
  or more characters to be absent from an eight-hex-character keyed pseudonym.
  For `203.0.113.999:54321`, the random process-local digest happened to be
  `59990025`; the source fragment `999` therefore appeared by coincidence. This
  is not source preservation and the output contains no complete client or
  dotted plaintext address. Changing production hashing, enlarging the digest,
  or suppressing values until the tests happen to pass are rejected: the
  assertion is probabilistic and must be corrected. Removing disclosure checks
  entirely is also rejected; deterministic complete-value and complete-address
  assertions replace them.
- **Added/removed scope:** one Important finding, **N-32**, confined to two test
  assertions plus their deterministic falsification and evidence. N-31 is
  recommended resolved at the repository implementation boundary. No production
  code, schema, migration, dependency, configuration or deployment is implicated.
- **Dependency and critical-path effect:** the repository re-review needs one
  narrow test correction and rerun. The four supervised operational items remain
  the separate gate dependency. Phase 4 remains blocked.
- **Estimate/forecast and capacity effect:** minimal test-only remediation; no
  calendar forecast is inferred.
- **New or changed risks:** current focused verification can pass or fail solely
  with a new process key, weakening reproducibility and confidence in the
  evidence. Production confidentiality is unchanged.
- **Testing, migration, security and operational effect:** bot **2447 passed**;
  web **2797 passed, 80 skipped**; module **171 passed**; the initial expanded
  focused run passed **461**, then the exact access-log/scope pair in a fresh
  process failed **2 of 453** on the coincidental `999` substring. Assets and
  visual freeze passed; both `compileall` checks were clean; Alembic has single
  head `0013` and no branches; `git diff --check` was clean. No migration,
  deployment or service action occurred.
- **Product Owner recommendation:** none recorded. Peter alone decides the gate.
- **Technical Lead and specialist reviews:** Codex recommends the N-31
  production correction as satisfactory and raises N-32 as Important evidence
  reliability. Renew EX-11 and EX-12 after the deterministic test correction.
- **Approval:** **none.** Recording this entry closes neither the finding nor the
  gate.

## C-P3.5-AH — N-32 corrected: deterministic complete-value assertions replace a probabilistic fragment rule

**Date:** 2026-08-28 · **Prepared by:** Claude, working Technical Lead ·
**Status:** applied in the repository, **test-only, nothing deployed**;
independent review is owed again as **EX-11** and **EX-12**.

**Authority.** The 2026-08-28 Codex handoff authorizes the N-32 test correction,
its falsification, verification and the corresponding evidence updates, and
nothing else. It expressly does not authorize changes to production
pseudonymization, access-log policy, routes, configuration or deployment
artifacts, nor execution of the four outstanding operational procedures. **This
entry decides nothing, closes no finding and confers no Phase 4 authority.**

- **Affected requirement, milestone and release:** Phase 3 P3.5, EX-11 and
  EX-12, operational contract §5's access-log confidentiality evidence, and the
  Phase 3 authentication/security gate. Phase 4 remains unauthorized.
- **Reason and alternatives considered:** C-P3.5-AG recorded N-32. Two
  assertions split an unfamiliar client value on `.`, `:` and `/` and required
  every fragment of three characters or more to be absent from the eight
  hexadecimal characters of the keyed pseudonym. `_CLIENT_PSEUDONYM_KEY` is
  generated per process, and a digest may contain any short hex string, so the
  result depended on the key: for `203.0.113.999:54321` the rerun's digest was
  `59990025`, whose `999` is the source's `999` by coincidence rather than by
  preservation. Enlarging the digest, changing the key derivation, altering the
  prefixes or the client parsing, or suppressing the value until the tests
  happen to pass were all rejected — the production behaviour is correct and the
  assertion is the defect. Deleting the confidentiality checks was also
  rejected. What replaced them is a per-case table of the **complete**
  representations that must not survive: the whole client field, and the
  punctuation-bearing host or credential inside it. Every one of those carries a
  character outside the pseudonym's own alphabet, so its absence follows from
  the contract rather than from the key — and that property is itself asserted,
  rather than assumed, by a test over the table.
- **Added/removed scope:** exactly one file changed,
  `tests/web/test_n7_access_log_redaction.py`. The two tests were rewritten in
  place, each saying in its docstring what it used to assert and why that is no
  longer the property to hold; a new N-32 section was appended carrying the
  deterministic reproduction, the mutation tests and the table guards. Nothing
  was deleted. The module goes from **410 to 437 collected tests**. No
  production code, schema, migration, dependency, configuration, deployment
  artifact or operational procedure is touched, and **no production injection
  seam was added** — the falsification monkeypatches `_digest` from the test
  module and `monkeypatch` restores it.
- **Dependency and critical-path effect:** the narrow test correction the
  repository re-review was waiting on is done. The four supervised operational
  items remain the separate gate dependency. Phase 4 remains blocked.
- **Estimate/forecast and capacity effect:** test-only remediation, completed
  the same day. No calendar forecast is inferred.
- **New or changed risks:** the risk C-P3.5-AG recorded — that focused
  verification could pass or fail solely on a new process key — is removed. A
  one-off measurement over 20,000 random keys × 7 cases put the old rule's
  failure rate at **199 of 140,000 case-runs (0.142%)** and the corrected rule's
  at **0**. That measurement is evidence, not a test: nothing randomized was
  added to the suite. Production confidentiality is unchanged, because nothing
  in production changed.
- **Testing, migration, security and operational effect:** the focused
  access-log and scope-guard pair passed **480** in each of three separate fresh
  Python processes, where the pre-correction tree failed 2 of 453 in one such
  process. Serial database-enabled suites: bot **2447 passed**, 1 warning; web
  **2824 passed, 80 skipped**, 1137 warnings; module **171 pass**. Assets 4/4
  and visual freeze 14/14; both `compileall` checks clean; Alembic single head
  `0013`, no branches; `git diff --check` clean. Formatter, linter and type
  checker remain unconfigured (standing condition E-9) and are **not** claimed.
  No migration, deployment, restart or service action occurred. Rollback is
  `git checkout -- tests/web/test_n7_access_log_redaction.py`, which restores
  the probabilistic assertions and nothing else.
- **Product Owner recommendation:** none recorded. Peter alone decides the gate.
- **Technical Lead and specialist reviews:** **EX-11** is requested to confirm
  that N-32's reproduction is deterministic and that N-31 and N-30 remain
  preserved. **EX-12** is requested to confirm that the corrected tests still
  detect complete plaintext client or address disclosure and that no production
  confidentiality behaviour changed.
- **Approval:** **none.** No finding or gate closes on implementation or green
  tests alone.

Evidence: `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` §5V.

## C-P3.5-AI — deployed worker parity and final TC-SEC-07 capture

**Date:** 2026-08-28 · **Authorized and supervised by:** Peter Duscha,
Operations Owner and Acceptance Authority · **Status:** operational procedures
completed; no gate decision recorded.

- **Affected requirement, milestone and release:** Phase 3 P3.5, I-06,
  TC-SEC-07, N-22, N-47, N-29/N-31 deployment evidence and §5R items 3–4.
- **Reason and alternatives considered:** repository state was not deployment
  evidence. Peter authorized the deployed corrections and bounded staging
  exposure. Keeping Basic Auth enabled was rejected because it would measure
  Caddy's 401 instead of the application's accepted boundary.
- **Added/removed scope:** no new repository behavior. The worker unit was
  rendered from its reviewed template; the current portal tree was loaded by
  restart; existing reviewed HSTS was validated; and the gate import was
  removed for 92 seconds and restored automatically.
- **Dependency and critical-path effect:** §5R items 3–4 now have operational
  evidence. Running-process proof for Foundry 1.0.9 and the dependent real
  export/preview remain outstanding. Phase 4 remains blocked.
- **Estimate/forecast and capacity effect:** none inferred.
- **New or changed risks:** bounded exposure ran 20:21:43Z–20:23:15Z. The
  application's controls remained active. The gate was restored and public 401
  observed. No cookie, redirect location, credential or Actor payload was
  captured.
- **Testing, migration, security and operational effect:** focused preflight
  **458 passed** with `TEST_DATABASE_URL`. The worker matched its template,
  validated, remained active without restart and enforced 2 GiB. The portal
  restarted and passed Host-aware health. Normal/error edge responses carried
  identical CSP and HSTS; origin normal carried HSTS and no `Server`; edge
  `Server` was Cloudflare; early refusal carried the required safe headers.
  Peter acknowledged the browser check without reporting CSP/form-action or
  HTMX indicator-style violations. Caddy validated before reloads and the
  restored gate returned 401. No schema, migration or data mutation occurred.
- **Product Owner recommendation:** none recorded.
- **Technical Lead and specialist reviews:** final combined gate-package review
  remains required where assigned by the plan.
- **Approval:** Peter authorized and supervised these operations. This is not
  the Phase 3 gate decision and does not release Phase 4.

Evidence: `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` §5W.

## C-P3.5-AJ — Foundry 1.0.9 running-load and real preview compatibility

**Date:** 2026-08-28 · **Supervised by:** Peter Duscha · **Status:** preview
complete, no apply and no gate decision.

- **Affected requirement, milestone and release:** Phase 3 P3.5, Foundry
  compatibility residual N-25/R-07 and §5R items 1–2.
- **Reason and scope:** installation metadata alone did not prove a running
  module loaded 1.0.9, and structural tests alone could not exclude a
  schema-valid semantic projection change. Peter observed the module-owned
  snapshot control in running worlds and supplied a fresh active-folder export.
- **Evidence:** the 1.0.9 artifact reported Foundry 14.367, dnd5e 5.3.3,
  `/actors/Characters (active)`, 32 Actors and checksum `fb14adf0a36c…`. Its
  stable Actor-ID set equalled the 1.0.8 baseline. Content was identical after
  excluding only export time and exporter version. The staging preview under
  profile 2026-08-09.1 returned 32 create-candidates, zero mapped/blocked/absent,
  zero errors and warnings, exit 0, and explicitly wrote nothing.
- **Security, privacy and operations:** comparison output retained no Actor
  names or mechanics. The raw artifacts remained outside the repository. No
  credential was read, issued or stored; no apply, schema, service or Foundry
  mutation occurred.
- **Dependency effect:** §5R items 1–2 are satisfied at the operational-evidence
  level. Accountable RAID and Phase 3 gate decisions remain deferred.
- **Approval:** none. Peter decides the final gate separately; Phase 4 remains
  unauthorized.

Evidence: `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` §5X.

## C-P3.5-AK — Phase 3 gate approval and Phase 4 authorization

**Date:** 2026-08-28 · **Decided by:** Peter Duscha, acting in the accountable
Security Reviewer, Technical Lead, Operations Owner, Product Owner and
Acceptance Authority roles · **Status:** accepted; Phase 3 closed and Phase 4
implementation authorized.

- **Affected requirement, milestone and release:** closes A-05, A-06 and I-06;
  approves the Phase 3 authentication, authorization and web-security gate; and
  releases Phase 4 implementation.
- **Reason and evidence:** the complete P3.5 package received independent
  implementation and distinct security-focused review, the final deployed
  worker and TC-SEC-07 evidence was captured, and Foundry module 1.0.9 was
  observed running and produced a compatible real active-folder export and
  clean read-only staging preview.
- **Added/removed scope:** this entry changes governance state only. It adds no
  production behavior, schema, migration, deployment or data mutation.
- **Dependency and critical-path effect:** the Phase 3 gate no longer blocks
  Phase 4 implementation. Ordinary review and deployment gates still apply.
- **Estimate/forecast and capacity effect:** no schedule or capacity claim is
  inferred from authorization.
- **New or changed risks:** R-23 remains an **active accepted accessibility
  residual**. Screen-reader traversal remains Not Run for Phase 3 and is not
  classified as passed.
- **Testing, migration, security and operational effect:** the accepted evidence
  is recorded in the P3.5 submission and staging/operations evidence. This
  decision performs no additional runtime action.
- **Product Owner decision:** retain R-23 as stated above.
- **Technical Lead and specialist decisions:** accept the PostgreSQL
  queue/limiter and staging evidence; confirm final break-glass readiness.
- **Acceptance Authority decision:** **accepted by Peter Duscha on 2026-08-28.**
  Phase 3 is approved and Phase 4 implementation is explicitly authorized.

Decision record: `docs/review/phase-3-gate-disposition-2026-08-25.md`.

## C-P4-A — Phase 4 documentation alignment and implementation handover

**Date:** 2026-08-28 · **Requested by:** Peter Duscha · **Status:** documented;
no implementation or gate decision made by this entry.

- **Affected requirement, milestone and release:** Phase 4 shared application
  services and the documentation state following C-P3.5-AK.
- **Reason:** current roadmap actions and the implementation handover still
  directed agents into completed Phase 2/3 work even though Phase 4 had been
  explicitly authorized.
- **Added/removed scope:** current-state roadmap, governance, decision, status
  and RAID summaries now point to Phase 4. Dated evidence remains historical.
  `docs/review/Handover information` is replaced with a bounded Phase 4 brief.
- **Dependency and critical-path effect:** Phase 4 readiness and implementation
  become the current critical path. D-04 and the Phase 4 gate continue to block
  Phase 5 mutations.
- **Estimate/forecast and capacity effect:** the handover requires a three-point
  estimate and named implementer/reviewer before code; no calendar forecast is
  created here.
- **New or changed risks:** no risk is closed or newly accepted. R-23 remains an
  active accepted residual. The handover reduces premature Phase 5/schema risk
  through explicit stops.
- **Testing, migration, security and operational effect:** documentation only.
  No code, migration, service, host state or live data is changed.
- **Product Owner recommendation:** proceed with the Phase 4 readiness package
  and bounded implementation brief.
- **Technical Lead and specialist reviews:** the implementation still requires
  an Independent Reviewer; material schema work requires its prior logical
  schema review.
- **Acceptance Authority decision:** C-P3.5-AK already authorizes Phase 4.
  C-P4-A adds no new authority and does not approve the Phase 4 gate.

## C-P4-B — Phase 4 readiness package plan (proposed, not decided)

**Date:** 2026-08-28 · **Requested by:** Peter Duscha, through the instruction
to execute `docs/review/Handover information` · **Status:** **recorded for the
Acceptance Authority; not accepted; no production code written.**

- **Affected requirement, milestone and release:** Phase 4 shared application
  services; the management definition of ready in
  `docs/project-management/README.md`; implementation-plan §12 Phase 4 and §20
  action 1.
- **Reason:** the handover forbids production-code edits until a Phase 4 package
  plan exists under `docs/review/`. `docs/review/phase-4-package-plan.md` is
  that plan. It also records the pre-implementation characterization inventory
  of every money and resource concept in the live bot, with file and line
  references, because the scope and estimate depend on it.
- **Alternatives considered:** beginning implementation on the roadmap's Phase 4
  bullet list alone. Rejected: it would leave the persistence boundary, the
  downtime unit and the denomination representation to be decided inside
  implementation, which §0.2 and `.agents/AGENTS.md` both forbid.
- **Added/removed scope:** none. The plan proposes exactly the Phase 4 outcome
  already approved in §12, and restates the handover's exclusions as binding.
- **Dependency and critical-path effect:** Phase 4 readiness remains the current
  critical path. D-04 stays Open and is unchanged by this entry. Readiness is
  **not** met until Peter rules the six decisions in the plan's §5, designates
  the implementer and names an Independent Reviewer.
- **Estimate/forecast and capacity effect:** first three-point estimate for
  Phase 4 — optimistic 5.5, most-likely 10.0, pessimistic 18.5 focused
  implementer-days, PERT expectation 10.7, plus a 3.0-day remediation allowance
  and 2.0-day contingency, and independent review separately. **This exceeds the
  §12 roadmap range of 5–10 days**, which is reported under §0.4 rather than
  absorbed. No calendar date is created; reviewer and maintainer availability
  are not yet known.
- **New or changed risks:** proposed R-P4-1 (a ledger with no physical table may
  be judged insufficient at the gate), R-P4-2 (characterization tests freezing
  the legacy float-money behaviour of `/sale` and `/lc`), R-P4-3 (`/info`
  exposes any character's wallet to any guild member, and Phase 4 is forbidden
  from changing it), assumptions A-P4-1 (no staging required) and A-P4-2 (the
  established database-enabled web skip count of 80 still holds). These are
  **not** entered in the RAID register by this entry; they are entered when the
  plan is accepted.
- **Testing, migration, security and operational effect:** documentation only.
  No code, migration, schema, service, host state, configuration or live data is
  changed. Environment availability was **verified rather than assumed** on
  2026-08-28: both test interpreters present with pytest 8.4.2, the disposable
  `freedom_test` database reachable over the Unix-domain socket on PostgreSQL
  16.15, Node v24.19.0 present, and **no formatter, linter or type checker
  configured** in this repository.
- **Product Owner recommendation:** rule the plan's §5 decisions — in particular
  P4-D1, whether Phase 4 adds a physical ledger table — before implementation
  starts. The plan recommends **no new migration in Phase 4**, because the
  migration register assigns every money and resource field to packages 5.2, 5.3
  and 5.5 and forbids a second write-authoritative target.
- **Technical Lead and specialist reviews:** the plan is the working Technical
  Lead's readiness recommendation. It is not independently reviewed. An
  Independent Reviewer who does not implement the package is required at the
  Phase 4 gate; none is named yet.
- **Acceptance Authority decision:** **not yet decided.** Recorded for the
  Acceptance Authority. This entry approves no gate, closes no dependency and
  authorizes no code.

## C-P4-C — Phase 4 blocking decisions ruled (OD-48, OD-49, OD-50)

**Date:** 2026-08-28 · **Requested by:** Peter Duscha · **Status:** **ruled.**
These three decisions released the first Phase 4 production-code edit. They do
not make the package ready and they approve no gate.

- **Affected requirement, milestone and release:** Phase 4 deliverables
  "transaction ledger" and "money and resource value objects"; the acceptance
  criterion "money uses integer copper"; the characterization requirement that
  the migrated command's visible output is unchanged.
- **Reason:** each decision changes *what is built*, not how long it takes, and
  `.agents/AGENTS.md` requires a maintainer ruling where architecture, data
  authority or migration strategy is at stake.
- **Rulings.** **OD-48** — Phase 4 adds no migration and no physical ledger
  table; the ledger is domain plus a consumer-owned protocol with an in-memory
  reference adapter, and durable idempotency reuses the existing
  `idempotency_keys` table under a Phase-4 scope. **OD-49** — the domain
  `Downtime` value object holds integer thousandth-days and refuses anything
  else; an unrepresentable Sheet cell becomes an explicit invalid-value marker
  and `/info` renders exactly what it renders today. **OD-50** — `domain/`
  models money as integer copper only; the Sheet's four denomination counters
  remain a labelled legacy representation with no domain meaning, and nothing
  normalizes a character's coins on read.
- **Alternatives considered and rejected:** adding a ledger table now (would
  pre-empt package 5.2's schema ownership and stop code work for the mandatory
  logical-schema artifact); rounding an out-of-unit downtime value (the
  `safe_number` coercion defect carried into the new layer); normalizing coins
  on read (silently changes `/info` output for many characters, failing a gate
  criterion).
- **Added/removed scope:** none. OD-48 confirms that no schema addition is in
  Phase 4's scope, which removes the conditional migration, ER-artifact and
  runtime-role-evidence work from the estimate rather than from the requirement:
  that evidence is now explicitly owed by package 5.0 or 5.2.
- **Dependency and critical-path effect:** D-04 unchanged and Open. The critical
  path moves from "rule the blocking decisions" to "designate the implementer
  and name an Independent Reviewer", which readiness still requires.
- **Estimate/forecast and capacity effect:** the §7 figures already assumed
  Option A for OD-48, so the estimate is unchanged: 5.5 / 10.0 / 18.5
  implementer-days, PERT 10.7, plus 3.0 days remediation allowance and 2.0 days
  contingency. Under the rejected Option B they would have risen by roughly 3–5
  days plus a review cycle.
- **New or changed risks:** proposed **R-P4-1** narrows but does not close — a
  ledger with no physical table may still be questioned at the gate, and OD-48
  is now the written answer. Proposed **A-P4-1** (no staging required) is
  confirmed, because Option B was the only thing that would have voided it.
- **Testing, migration, security and operational effect:** no migration, no
  schema change, no service, host, configuration or live-data effect. The
  conditional PostgreSQL constraint/append-only/runtime-role evidence for a
  ledger table is **not** produced by Phase 4 and is reallocated to package 5.0
  or 5.2.
- **Product Owner and Data Owner recommendation:** as recorded in
  `docs/review/phase-4-package-plan.md` §5; all three rulings follow the
  recommendation.
- **Technical Lead and specialist reviews:** none of these rulings is
  independently reviewed. The Independent Reviewer examines them as part of the
  Phase 4 gate package.
- **Acceptance Authority decision:** **ruled by Peter Duscha on 2026-08-28.**
  Canonical records: OD-48, OD-49 and OD-50 in
  `docs/discovery/open-decisions.md`. No gate is approved and D-04 is not closed.

## C-P4-D — Remaining Phase 4 decisions ruled; Independent Reviewer named (OD-51, OD-52)

**Date:** 2026-08-28 · **Requested by:** Peter Duscha · **Status:** **ruled.**
With C-P4-C these complete the Phase 4 management definition of ready. They
approve no gate.

- **Affected requirement, milestone and release:** Phase 4 deliverables
  "characterization tests for Sheet-era behavior" and "first read-only bot
  command using the new application layer"; the gate-authority assignment for
  the Phase 4 domain/dependency gate.
- **Rulings.** **OD-51** — the binary-float money defects in `Resource.sale`
  and `Lifestyle.pay_for_weeks` are **characterized, not corrected**; the fix is
  owed by packages 5.7 and 5.3, which must reproduce the PDF worked examples in
  integer copper. **OD-52** — `/info` calls **one** application query, and only
  the money and resource block is typed; name, level, badge, lifestyle and
  Bastion pass through as labelled presentation values owned by 5.1, 5.3 and
  5.9. **P4-D6** — **Codex** is the Independent Reviewer, performing the
  implementation review; **no separate security-focused review is required**,
  because the package adds no authentication, authorization, session, network or
  privacy surface.
- **Reason, and the correction it records:** the package plan originally
  recommended a full typed character-summary read model. The Product Owner
  observed that `/info` is a Discord command that has no meaning on the
  platform. That is decisive on inspection: the portal's `CharacterDetailView`
  renders every money field as `MigrationDeferred`, a type with **no value
  field**, under a mandatory Phase 3 test — so the platform has no wallet to
  show and cannot acquire one before package 5.2. A full summary read model
  would have had exactly one consumer, been shaped by Discord's rendering, and
  cut across four packages' typed ownership. The recommendation was withdrawn.
- **Alternatives considered and rejected:** routing only `/info`'s resource
  block through the new query, leaving its profile fields on the legacy path.
  Rejected because `Actor.load_from_sheet` performs a single
  `Characters!A3:AL150` read, so the split would either double that API call or
  share mutable state between two paths — and preserved response timing is a
  Phase 4 characterization requirement.
- **Added/removed scope:** none. Deliverable 8 in the package plan narrows from
  a character-summary query to a money/resource query with labelled
  pass-through fields. Nothing is added.
- **Dependency and critical-path effect:** D-04 unchanged and Open. With the
  reviewer named, the package is no longer `deferred` for want of a reviewer.
  The critical path becomes implementation and verification.
- **Estimate/forecast and capacity effect:** unchanged — 5.5 / 10.0 / 18.5
  implementer-days, PERT 10.7, plus 3.0 days remediation allowance and 2.0 days
  contingency, and reviewer capacity of 0.5–1.0 day plus at least one
  re-review. No calendar date is created.
- **New or changed risks:** **R-P4-2** (characterization tests mistaken for
  accepted policy) is the reason OD-51 requires each such test to name its
  defect and owning package. **R-P4-3** is confirmed and raised against package
  **5.1**: `/info` performs no authorization beyond guild membership, so any
  guild member can read any character's wallet, and Phase 4 preserves that
  exactly because changing authorization is an explicit exclusion.
- **Testing, migration, security and operational effect:** no migration, schema,
  service, host, configuration or live-data effect. No authorization,
  authentication, session or privacy behaviour changes.
- **Product Owner recommendation:** as ruled.
- **Technical Lead and specialist reviews:** none of these rulings is
  independently reviewed. Codex examines them as part of the Phase 4 gate
  package.
- **Acceptance Authority decision:** **ruled by Peter Duscha on 2026-08-28.**
  Canonical records OD-51 and OD-52. No gate is approved and D-04 is not closed.

## C-P4-E — `/info` replaced by platform character pages; Phase 4 evidence amended

**Date:** 2026-08-28 · **Requester and Acceptance Authority:** Peter Duscha ·
**Status:** **authorized; supersedes C-P4-D only where that entry requires
Phase 4 to rewire `/info`.**

- **Decision:** `/info` is not a platform feature and is not rewired in Phase
  4. Authenticated players satisfy the underlying need through linked-character
  pages as each typed package migrates its fields.
- **Criterion amendment:** the production-shaped temporary Sheet adapter and
  its money/resource query contract tests replace real-command wiring as Phase
  4 dependency-boundary evidence.
- **Implementation boundary:** `ext/commands/info.py` and
  `helpers/renderers.py` remain unchanged. Existing characterization tests are
  retained. Package 5.2 owns the typed wallet and portal wallet view; package
  5.1 owns any later transitional command migration and its authorization.
- **Impact assessment:** no schema, migration, authority, privacy, production
  behavior, deployment, phase order or release-boundary change. WP-5 changes
  from 0.5/1.0/2.0 to 0.5/0.75/1.5 implementer-days; total becomes
  5.5/9.75/18.0 with PERT 10.4. No new baseline version is required.
- **Working-agreement reconciliation:** the query and production-shaped adapter
  are accepted as each other's concrete boundary implementation for this one
  criterion. The general prohibition on unused abstractions remains; no later
  package inherits an adapter-only exception.
- **Safety and rollback:** the live Freedom bot is unchanged and remains
  supported. The documentation amendment is reverted through a compensating
  change-log entry; no runtime or data rollback exists.
- **Acceptance Authority decision:** directed and authorized by Peter Duscha on
  2026-08-28. Phase 5 order is unchanged and no Phase 4 gate is approved.

## C-P4-F — Remove the unconsumed wallet query/adapter from Phase 4

**Date:** 2026-08-29 · **Requester and Acceptance Authority:** Peter Duscha ·
**Status:** **authorized; supersedes C-P4-E only where it retains a temporary
Sheet-backed wallet query/adapter.**

- **Decision:** Phase 4 creates neither an `/info` rewrite nor an adapter-only
  wallet query. Package 5.2 introduces the wallet query, production repository
  adapter and character-page view together so the abstraction has a real
  production consumer.
- **Reason:** the adapter-only compromise required a special exception to the
  repository's real-consumer rule and created transitional code likely to be
  discarded. Deferring the read boundary to its owning migration package is
  simpler and preserves dependency ownership.
- **Phase 4 evidence:** application envelopes, consumer-owned repository and
  transaction protocols, optimistic concurrency and durable idempotency are
  exercised through the concrete Phase 4 ledger command-execution path.
- **Scope and estimate:** WP-5 is removed. The package changes from
  5.5/9.75/18.0 to **5.0/9.0/16.5** implementer-days; PERT changes from 10.4 to
  **9.6** and remediation allowance from 3.0 to **2.7** days.
- **Impact:** no schema, migration, authority, privacy, production behavior,
  deployment, Phase 5 order or release-boundary change. WP-0 and WP-1 remain
  accepted work-in-progress evidence. No Phase 5 work or gate is authorized.
- **Acceptance Authority decision:** Peter accepted Codex's best-practice
  recommendation on 2026-08-29. OD-52, the plan, package plan and executable
  handover are finally amended.

## v1.7 — Freedom bot retirement (OD-53)

**Date:** 2026-08-28 · **Requester:** Peter Duscha · **Status:** **authorized;
baseline v1.7 effective.**

- **Affected requirement, milestone and release:** `.agents/AGENTS.md` product
  direction items 8–9 and the non-deletion rule; implementation-plan §12.0
  dependency map and §15, retitled *Legacy runtime retirement* with the existing
  Sheets content preserved as §15.1 and a new §15.2. Adds a terminal
  bot-retirement gate, which moves the release boundary and is why this is a new
  baseline version rather than a clarification.
- **Reason:** the platform exists to remove the Google Sheet and the manual
  steps the bot imposes. A bot that duplicates platform behavior preserves those
  steps. **This was stated by the Product Owner before it was recorded, and the
  controlled documents said the opposite** — AGENTS.md read "must not be
  deleted" and retained Discord for "optional lightweight commands". That gap is
  the failure the governance rule about durable written records exists to
  prevent, and it is closed by this entry and OD-53.
- **Alternatives considered:** retaining the bot for "optional lightweight
  commands", which was the prior baseline. Rejected: after every command's
  behavior exists on the platform and the Sheet is retired, a retained bot has no
  remaining purpose, and the rollback justification that protected it during
  migration has expired by construction.
- **Added/removed scope:** adds the §15.2 staged retirement contract and its
  gate. Removes nothing. **No phase is added, reordered or rescoped**, because
  most of the intent was already approved — §15.1 retires Sheets, Phase 5.1–5.9
  migrates every command's automation with 5.10 cutting over, Phase 6 supplies
  Council approvals, and Phases 8–11 automate the rest.
- **Dependency and critical-path effect:** the retirement gate is terminal and
  depends on every migrated command's package gate, Phase 6, the Phase 8–11
  behaviors the bot touches, and §15.1's final Sheet retirement gate. It is not
  on the current critical path and releases no successor work.
- **Estimate/forecast and capacity effect:** none now. The retirement package is
  estimated when it meets the definition of ready. **No Phase 4 estimate changes.**
- **New or changed risks:** the adoption threshold in §15.2 stage 4 must be a
  number accepted in advance — "everyone has moved over" is a gate criterion and
  cannot be assessed by impression. Recorded consequence for **Phase 8**:
  voice-state join/leave requires a live gateway connection, so "no bot" must
  not be read as "no gateway process" until the attendance package decides how
  attendance evidence is collected. This is an impact to size, not an objection.
- **Testing, migration, security and operational effect:** none today. No code,
  schema, migration, service, host, configuration or live-data change. Discord
  OAuth authentication, guild and role verification are explicitly unaffected.
- **Product Owner recommendation:** as decided.
- **Technical Lead review:** the decision is consistent with the approved
  architecture and strengthens Phase 4. A command cannot be retired until its
  logic lives elsewhere, which is exactly what Phase 4 extracts; and OD-52's
  money/resource query gains a genuine second consumer when package 5.2 gives
  the portal a wallet view.
- **Acceptance Authority decision:** **authorized by Peter Duscha on 2026-08-28.**
  Canonical record OD-53. No gate is approved by this entry and D-04 is unchanged.

## v1.7 correction C-1 — the retirement condition is the platform's functionality

**Date:** 2026-08-28 · **Requester:** Peter Duscha · **Status:** **authorized;
corrects the wording of v1.7, not its decision.**

- **What was wrong:** v1.7 recorded the prohibition as *"must not be deleted as
  part of the website or database migration"*. The Product Owner's condition is
  narrower and clearer: *"the bot are not to be deleted…as long as the platform
  is not fully functional."* Anchoring to "as part of the migration" describes
  an activity, and an activity can be declared over; anchoring to the platform's
  functionality describes a state that has to be demonstrated. The v1.7 gate
  criteria already encoded the right substance, but the sentence a future
  implementer reads first did not.
- **Correction:** `.agents/AGENTS.md` and plan §15.2 now bind the prohibition to
  the platform being fully functional. The prohibition is extended from
  *deleted* to **deleted, disabled or degraded**, so the bot cannot be hollowed
  out by degrees while the condition is unmet. *Fully functional* is defined
  explicitly as all of: every player-facing bot behavior existing on the
  platform with its owning package gate approved; §19 platform completion met
  for those behaviors; §15.1's final Sheet retirement gate closed; and measured
  adoption meeting a pre-accepted threshold. §15.2 adds that an agent's belief
  that the platform is finished is not evidence that it is.
- **Affected requirement, milestone and release:** `.agents/AGENTS.md` product
  direction; plan §15.2; OD-53. The v1.7 decision, phase order, package scope
  and release boundary are unchanged.
- **Dependency, estimate and risk effect:** none. D-10 is unchanged. No estimate
  changes. The correction strengthens an existing control and weakens none.
- **Testing, migration, security and operational effect:** none. Documentation
  only; no code, schema, service, host or live-data change.
- **Acceptance Authority decision:** **authorized by Peter Duscha on
  2026-08-28** in the correction quoted above.

## v1.7 correction C-2 — Discord and the Freedom bot are named apart

**Date:** 2026-08-28 · **Requester:** Peter Duscha · **Status:** **authorized;
terminology correction, no decision changed.**

- **What prompted it:** *"Discord and the Freedom Bot (discord bot) are two very
  different things. The discord server is the basis for the whole project."*
- **What was wrong:** the controlled documents used "Discord bot" and "the bot"
  interchangeably for this repository's Python/Pycord application, in the same
  paragraphs that discuss Discord the service. With a retirement decision now on
  the record, that ambiguity is dangerous in both directions: a reader could
  take v1.7 as licence to unwind Discord integration, or could take Discord's
  permanence as a reason to refuse the bot's retirement.
- **Correction:** `.agents/AGENTS.md` opens its product direction with a
  terminology block — Discord is the community's server and the **basis of the
  whole project**, never retired, and any instruction that appears to propose
  retiring it is refused and referred to a maintainer; the Freedom bot is this
  repository's application, a **client** of Discord, retired under §15.2 once
  the platform is fully functional. Retiring the client removes nothing from
  Discord. Five loose uses of "Discord bot" in the working agreement and the
  implementation plan, including the architecture diagram, now read "Freedom
  bot"; §15.2 and OD-53 carry the distinction explicitly. No conflated use
  remains in either document.
- **Affected requirement, milestone and release:** naming only, in
  `.agents/AGENTS.md`, plan §1, §2, §5.1, §12 Phase 2 narrative, §15.2 and
  OD-53. **No decision, phase order, package scope, authority or release
  boundary changes.**
- **Dependency, estimate and risk effect:** none. The correction removes a
  misreading risk and adds no work.
- **Testing, migration, security and operational effect:** none. Documentation
  only; no code, schema, service, host or live-data change.
- **Acceptance Authority decision:** **authorized by Peter Duscha on 2026-08-28**
  in the statement quoted above.

## C-P4-L — Phase 4 gate approved

**Date:** 2026-08-29 · **Requester:** Peter Duscha · **Status:** **approved.**

- **Affected requirement, milestone and release:** closes the Phase 4 shared-
  application-services dependency-direction/domain-correctness gate and D-04.
  It releases Phase 5 package planning under the existing §12 controls; it does
  not approve a Phase 5 package or production release.
- **Reason and alternatives considered:** Codex's second independent re-review
  found no remaining Blocking or Important defect after Remediation R2. Deferral
  was the alternative and is no longer supported by an open review finding.
- **Added/removed scope:** none. The accepted scope remains framework-free
  quantities, command boundaries, typed errors, ledger, idempotency,
  concurrency, authority resolution, audit/correlation and characterization.
- **Dependency and critical-path effect:** P4-R1 through P4-R5 and D-04 are
  Closed. Phase 4 no longer blocks Phase 5 package planning. Every package-
  specific predecessor, readiness review and gate remains effective.
- **Estimate/forecast and capacity effect:** no Phase 5 estimate or calendar
  forecast is approved. Each package is estimated when it meets definition of
  ready.
- **New or changed risks:** no new risk. R-P4-1 through R-P4-4 remain active and
  owned by the stated later packages; the in-memory reference ledger is not
  production authority.
- **Testing, migration, security and operational effect:** independent evidence
  is focused Phase 4 415 passed; bot 2929 passed with zero skips; web 2824
  passed with 80 expected skips; Foundry 171 passed; both `compileall` checks
  and `git diff --check` clean. No formatter, linter or type checker is
  configured. No migration, schema, deployment, configuration, credential,
  live-data or authority-cutover action is authorized.
- **Product Owner recommendation:** approve the gate and proceed to controlled
  Phase 5 package planning.
- **Technical Lead and specialist reviews:** Claude supplied Remediation R2;
  Codex independently re-reviewed it and recommended gate approval with no
  remaining Blocking or Important findings. No separate new security decision
  was required because the authorization defect was corrected within the
  already approved Phase 4 policy.
- **Acceptance Authority decision:** **approved by Peter Duscha on 2026-08-29.**
  This does not authorize permanent character-data mutation through Discord;
  after separately gated Freedom-bot retirement, Discord remains an identity,
  membership, role, event, notification and attendance integration.

## C-P4-M — Phase 5.0 selected for readiness planning

**Date:** 2026-08-29 · **Requester:** Peter Duscha · **Status:** **recorded;
planning only.**

- **Affected requirement, milestone and release:** plan §12.0 and package 5.0.
  Package 5.0 is selected as the next readiness package because it precedes the
  Phase 5 migrations and mutations. No release or cutover is approved.
- **Reason and alternatives considered:** beginning with 5.1 or 5.2 would bypass
  their listed 5.0 predecessor. The accepted alternative is to baseline 5.0
  first under the management definition of ready.
- **Added/removed scope:** none. The handover requests only the package plan,
  current-path inventory, work breakdown, estimate/capacity, traceability,
  risks, operations plan and any mandatory logical schema artifact.
- **Dependency and critical-path effect:** Phase 5.0 readiness is now the
  critical-path activity. Phase 5.1+ remain not ready and retain every package-
  specific predecessor and gate.
- **Estimate/forecast and capacity effect:** none yet; the readiness plan must
  produce the three-point estimate and name implementer/reviewer availability
  before a forecast exists.
- **New or changed risks:** R-P4-1 is Closed because Phase 4 accepted the
  in-memory reference ledger; R-P4-4 remains Active until a later package
  supplies a durable atomic adapter. No new risk is accepted by this entry.
- **Testing, migration, security and operational effect:** documentation only.
  No code, migration, database, configuration, credential, host or live service
  is changed. The readiness brief requires PostgreSQL, security, recovery and
  independent-review evidence to be planned before implementation.
- **Product Owner recommendation:** prepare the Phase 5.0 readiness package and
  stop for approval.
- **Technical Lead and specialist reviews:** not yet assigned for package 5.0;
  the readiness plan must name the working Technical Lead and a different
  Independent Reviewer. A durable ledger schema triggers the mandatory logical
  schema review before code.
- **Acceptance Authority decision:** no implementation decision requested or
  granted. Peter's request authorizes documentation/readiness work only.

## C-P5.0-P — revision 8 independently re-reviewed; remediation R8 required

**Date:** 2026-08-30 · **Requester:** Codex independent review · **Status:**
**changes requested; documentation/design remediation only.**

- **Affected requirement, milestone and release:** Package 5.0 readiness and
  P5.0-R5. No implementation or release boundary changes.
- **Reason:** revision 8 retains four Blocking inconsistencies: deployment-
  digest consumption precedes its stated validation; cleanup-failure evidence
  requires mutually exclusive residue outcomes; the K3/K4 capability boundary
  incorrectly treats `CAP_LINUX_IMMUTABLE` as bypassing DAC; and F-7 identifies
  no independent detector for a forged matching `/etc/machine-id`.
- **Scope:** prepare revision 9 of the package plan and logical schema plus an
  R8 handback. Preserve R7-B's exact S4-2 positive control while reconciling its
  cleanup behavior. No production code, migration or environment change.
- **Dependency and critical-path effect:** P5.0-R5 remains Blocking; Package 5.0
  remains not ready; Phase 5.1+ remains blocked by its predecessor.
- **Estimate/forecast effect:** revision 8's estimate is not accepted as a new
  baseline. Revision 9 must recalculate any affected evidence and effort counts.
- **Risks and decisions:** no risk or decision is closed. R-5.0-12 remains
  active; D5.0-9 through D5.0-13 / OD-62 through OD-66 remain open; the Security
  Reviewer remains unnamed.
- **Testing, migration, security and operations:** documentation review only.
  No suite was run; `git diff --check` and per-artifact whitespace checks were
  clean. Revision 9 must define executable, capability-accurate evidence before
  implementation can be considered.
- **Recommendation:** changes requested; complete R8 and return revision 9 for
  independent re-review.
- **Acceptance Authority decision:** not yet requested or granted.

## C-P5.0-R — revision 9 independently re-reviewed; remediation R9 required

**Date:** 2026-08-30 · **Requester:** Codex independent review · **Status:**
**changes requested; documentation/design remediation only.**

- **Affected requirement, milestone and release:** Package 5.0 readiness and P5.0-R5. No implementation or release boundary changes.
- **Reason:** revision 9 materially addresses R8-A, R8-B and R8-D, but its R8-C authority model omits the owner-or-`CAP_FOWNER` prerequisite Linux applies to `FS_IOC_SETFLAGS`. `CAP_LINUX_IMMUTABLE` alone therefore cannot clear `+i` on the root-owned archive, invalidating the claimed case and several minimum combinations. The model also calls A1–A6 independent while F-1a says every real A3 holder has A2.
- **Scope:** prepare revision 10 of the package plan and logical schema plus an R9 handback. Correct authority primitives, falsification combinations and `JNL-49`/`JNL-50` evidence. Preserve the materially addressed R8-A, R8-B and R8-D corrections. No code, migration, privileged probe or environment change.
- **Dependency and critical-path effect:** P5.0-R5 remains Blocking; Package 5.0 remains not ready; Phase 5.1+ remains blocked by its predecessor.
- **Estimate/forecast effect:** revision 9's estimate is not accepted as a new baseline. Revision 10 must recalculate affected cases and effort.
- **Risks and decisions:** no risk or decision closes. D5.0-9 through D5.0-13 / OD-62 through OD-66 remain Open; the Security Reviewer remains unnamed.
- **Testing, migration, security and operations:** documentation review only. No implementation or privileged suite ran. The design was checked against primary Linux `FS_IOC_SETFLAGS` semantics and whitespace checks were clean.
- **Recommendation:** changes requested; complete R9 and return revision 10 for independent re-review.
- **Acceptance Authority decision:** not yet requested or granted.

## C-P5.0-U — Package 5.0 design remediation R10 (revision 11)

**Date:** 2026-08-31 · **Requester:** Technical Lead (implementer) · **Status:**
**submitted for independent re-review; claims no Blocking finding closed.**

- **Affected requirement, milestone and release:** Package 5.0 readiness and
  P5.0-R5. No implementation or release-boundary change. Package 5.0 remains
  `not ready`.
- **Reason and alternatives considered:** revision 10's executable-identity
  recipes did not construct the identities they declared. `setpriv(1)` from
  util-linux 2.39.3 documents `keep_caps` as *"not allowed"*, so E2–E6 exited
  127; E8 declared an empty bounding set and dropped nothing; E7 wrote dashes
  where complete masks were required; and — found by the mechanical comparison
  the brief requires, not by the review — E2–E6 also asked `--bounding-set=+…`
  to **add** to a bounding set, which the same page says the kernel forbids.
  **Alternatives considered and declined**, each recorded in package plan
  §2.13.5c: keeping `setpriv` with `+no_setuid_fixup` substituted (parses, but
  the tool documents no option ordering, and every declared mask depends on it);
  a file capability on a purpose-built helper (a persistent host artifact inside
  the hierarchy being protected); a set-user-ID helper (worse, on a host whose
  set-user-ID inventory is recorded as not audited); a small `prctl`/`capset`
  program (retained as the named fallback). **Chosen:** `capsh(1)`, whose manual
  documents that it acts on its arguments in the order given.
- **Added/removed scope:** none. No work package, case, identifier, schema
  object, numeric control, command, refusal code, decision or RAID row is added
  or removed. **Added only**: stop condition **10n**, §7.1 risk row **28**, and
  §8.1 host row **H-6** recording the non-mutating tool-contract read.
- **Dependency and critical-path effect:** none. P5.0-R5 remains Blocking;
  Phase 5.1+ remains blocked by its predecessor.
- **Estimate/forecast and capacity effect:** **none.** PERT stays at **40.9**
  implementer-days and the security review at **3.5–4.5** reviewer-days. The
  brief requires recalculation only if the corrected contract changes them; it
  does not, because the harness was already budgeted, no case is added, and one
  already-built identity replaces another as a control. §4 states the four
  reasons rather than inventing an increment.
- **New or changed risks:** §7.1 row **28** records the recurrence class — a
  specification declaring a state its own recipe does not produce. **No RAID row
  is added or closed**; R-5.0-12, R-5.0-13 and R-5.0-14 are unchanged.
  **A-5.0-5 is widened** to name `capsh(1)`, `libcap2-bin` on the target host and
  the launching bounding set as prerequisites, and **remains unconfirmed**.
- **Testing, migration, security and operational effect:** no migration, no
  schema object, no production tool and no host change. `verify-capability`,
  `freedom-journal-admin`, `migration-authority` and the writer are untouched;
  `verify-capability` keeps its `setpriv` privilege drop, which requests no
  securebit and no capability option and is explicitly **not** identity E1.
  **Checks run, all non-mutating:** `setpriv --version` (2.39.3); the installed
  `setpriv(1)`, `capsh(1)`, `capabilities(7)` manual pages and
  `/usr/include/linux/securebits.h`; `dpkg -l`/`dpkg -S`, `ls -l` and `getcap`
  on both binaries; `getent passwd`/`getent group`; `/proc/self/status` and
  `/proc/1/status`; `capsh --decode` on every declared mask; an independent
  recomputation of each mask from capability indices; a mechanical
  mask-versus-recipe comparison for revision 10 and revision 11; and Markdown
  whitespace, table-shape, heading-order, link and stale-wording checks with
  `git diff --check` clean. Those checks also found **fourteen pre-existing stray
  blank lines that split a Markdown table in two** — three in the package plan,
  five in the RAID register, one in the decision register and five in this log —
  and they are removed. **The fix is whitespace only; no cell, figure or claim
  changes, and none of the fourteen was introduced by R10.** **No UID, GID,
  group, capability set, securebit, file, mode or attribute was changed, and no
  privileged helper was executed.**
  **Implementation and privileged suites: not run** — the submission is
  documentation/design-only, A-5.0-5 is unconfirmed, and host changes are
  unauthorized.
- **Product Owner recommendation:** not sought; this is a remediation
  submission, not a decision request.
- **Technical Lead and specialist reviews:** self-review by the implementer
  against `.agents/AGENTS.md`, the implementation plan and the R10 brief.
  **Independent re-review of revision 11 by Codex is required.** The Security
  Reviewer remains **unnamed**, and package plan §9.2 carries the new questions
  the mechanism raises.
- **Acceptance Authority decision:** **not requested and not granted.** Nothing
  is adopted, ruled or closed. D5.0-9 through D5.0-13 / OD-62 through OD-66
  remain Open.

## C-P5.0-T — revision 10 independently re-reviewed; remediation R10 required

**Date:** 2026-08-31 · **Requester:** Codex independent review · **Status:**
**changes requested; documentation/design remediation only.**

- **Affected requirement, milestone and release:** Package 5.0 readiness and
  P5.0-R5. No implementation or release-boundary change.
- **Reason:** R9-A and R9-B are materially improved, but R9-C's executable
  identity contract is internally inconsistent with util-linux 2.39.3. E2–E6
  use `--securebits=+keep_caps,+no_setuid_fixup`, although `setpriv` rejects
  `keep_caps`; E8 declares `CapBnd=0x0` without `--bounding-set=-all`; and E7
  uses unspecified inheritable and ambient masks despite the complete-mask
  requirement. The mandatory `/proc/self/status` assertion would therefore
  make affected cases inconclusive.
- **Scope:** prepare revision 11 of the package plan and logical schema plus an
  R10 handback. Correct only the E1–E8 launch recipes, complete P/E/I/A/B masks,
  directly dependent `JNL-49`/`JNL-50` wording, A-5.0-5 and associated counts or
  estimates if they genuinely change. Preserve R9-A, R9-B and the accepted R8
  movements. No code, migration, privileged probe or environment change.
- **Dependency and critical-path effect:** P5.0-R5 remains Blocking; Package
  5.0 remains not ready; Phase 5.1+ remains blocked by its predecessor.
- **Estimate/forecast effect:** revision 10's estimate is not changed by this
  review. Revision 11 must recalculate only if its corrected evidence contract
  changes work or review effort.
- **Risks and decisions:** no risk or decision closes or is added. D5.0-9
  through D5.0-13 / OD-62 through OD-66 remain Open; the Security Reviewer
  remains unnamed.
- **Testing, migration, security and operations:** documentation review only.
  The installed `setpriv` 2.39.3 manual and Linux capability definitions were
  checked; no privileged or implementation suite ran. Remediation R10 must
  perform a non-mutating syntax/contract check against the named tool and report
  privileged execution as not run.
- **Recommendation:** changes requested; complete R10 and return revision 11
  for independent re-review.
- **Acceptance Authority decision:** not requested or granted.

## Required fields for later entries

Every material entry must identify:

- affected requirement, milestone and release;
- reason and alternatives considered;
- added/removed scope;
- dependency and critical-path effect;
- estimate/forecast and capacity effect;
- new or changed risks;
- testing, migration, security and operational effect;
- Product Owner recommendation;
- Technical Lead and specialist reviews; and
- dated Acceptance Authority decision.
