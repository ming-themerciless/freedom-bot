# Package 5.0 — design remediation R6 handback

> **Disposition: SUPERSEDED by
> [`phase-5-0-remediation-r7-handback.md`](phase-5-0-remediation-r7-handback.md),
> 2026-08-30.** This handback was independently re-reviewed on 2026-08-30 and
> returned **changes requested**: revision 7 did not close P5.0-R5. Algorithm C
> checked the probe result before running it, S4-2 lacked a positive DAC control
> for its exact target, and the attacker-class assignments exceeded their defined
> capabilities; implementation-plan §20 also named an obsolete brief. Remediation
> **R7** answers all four in revision 8. This document is **retained as
> submission history and is not current authority**; nothing in it is a closed
> finding, and no result it reports may be carried forward as current evidence.

Date: 2026-08-30 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 remediation R6 —
documentation and design instructions*, which **authorizes documentation and
design remediation only**. No production code, migration `0014`, database or
operating-system change, privileged probe, service change, Google access,
deployment, cutover or Package 5.1+ work is authorized, and none occurred.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here. **P5.0-R5 remains Blocking.**
>
> **The four R6 findings are conceded before any replacement is presented.** Each
> concession is written into the documents themselves — package plan
> **§2.13.1 rows 10–13** — *before* the corrections are stated, so a reader meets
> the defect first.
>
> - **R6-A.** Algorithm C step **C1** built the immutable probe report from
>   **stages 1–3** while §3.7, §2.13.8a and the evidence contract all said
>   `append_only_probe_digest` covered **four** stages. A seal made immutable at
>   **C9** cannot acquire a stage that runs afterwards. **The digest was described
>   as covering bytes it did not contain.**
> - **R6-B.** Falsification row **F-1** claimed the writer refuses *any* seal-byte
>   alteration **without PostgreSQL**. Changing only `BND.sealed_at` passed every
>   **V-W** step: **W3** hashed the body, **W5** validated the derived genesis
>   digest, and **no writer step authenticated that field at all.**
> - **R6-C.** `JNL-32` expected a `startup` record in the branch where
>   `FS_APPEND_FL` is absent. **W9 refuses with `SW-J06` before W17 is reached**,
>   so that record cannot exist. The test expected a state its own algorithm
>   makes unreachable.
> - **R6-D.** The submitted R5 handoff contained merged and truncated
>   verification bullets and ended mid-sentence.
>
> **The preserved states are preserved.** P5.0-R1 and P5.0-R4 remain open;
> **P5.0-R2 remains closed**; P5.0-R5 remains **Blocking**; D5.0-9 through
> D5.0-13 / OD-62 through OD-66 remain **open**; the Security Reviewer remains
> **unnamed**; implementation remains **unauthorized**. The journal remains an
> **enumeration control, not a Google accepted-request completion barrier**, and
> **narrows R-5.0-8 by no case at all**.

---

## 1. Finding-by-finding change table

| Finding | Classification | Conceded at | Replaced by | What a reviewer should check |
|---|---|---|---|---|
| **R6-A** — reconcile the probe report lifecycle | Blocking — integrity and production reliability | package plan **§2.13.1 row 10** | **§2.13.2a** Stage 3 (cases `M-1 … M-2`), Stage 4 (cases `S4-1 … S4-3`, moved to **provisioning**), *The lifecycle choice, made in the open*; **§2.13.5a** **C0**, **C1**, **C8**; **§2.13.7** `verify-capability` and `init-generation` preconditions; **§2.13.8** `JNL-29`; **§2.13.8a**; logical schema **§3.7** `append_only_probe_digest`, **§3.7.1** (new sandbox row), **§4.3.8** Band 3, **§9** | that the report is built **after** all four stages run, so the digest covers what it names; that no second artifact, digest, authority, storage location, invalidation rule, column or refusal code was introduced; that the option not taken is priced rather than omitted |
| **R6-B** — make the whole-seal claim true or narrow it | Blocking — integrity and production reliability | package plan **§2.13.1 row 11**, and again at the head of **§2.13.5c** | **§2.13.5a** **C2** (`binding_format_version` added to the body), **C7** (`sealed_at` and `BND`'s own format field withdrawn), **C8** (exact file length); **§2.13.5b** *The binding section, field by field*; **§2.13.5c** rewritten with two attacker classes, **F-1** split into **F-1a**/**F-1b**, and **F-9 … F-12** added; **§2.13.6** **J-24** widened; **§2.13.8** `JNL-34a`, `JNL-34b`, `JNL-42 … 45`; logical schema **§3.7** (`seal_digest`, *What this table uniquely can do*), **§3.7.1**, **§9** | that every binding field is named with the V-W step that recomputes or compares it; that the narrowed claim states the **attacker capability** rather than asserting a refusal; that `chattr +i` is **not** offered as the answer; that `JNL-34b` asserts the case the writer does **not** refuse |
| **R6-C** — correct `JNL-32` everywhere | Important — testability and documentation correctness | package plan **§2.13.1 row 12** | **§2.13.8** `JNL-32a` and `JNL-32b`; **§2.13.2a** (*Live evidence is never probed destructively*); **§2.13.5b** (the W17 paragraph); **§3** WP-4b; **§6.5** item 15; **§9.3** stop condition 10f; logical schema **§4.3.8** Band 3 and **§9** | that the absent-flag branch expects `SW-J06`, **no W17/W18**, **no write-mode journal open**, and byte-for-byte unchanged journal, seal and archive; and that a separate successful-start branch expects **exactly one** appended `startup` record |
| **R6-D** — preserve a valid review record | Important — governance and review evidence | — | **this file**, complete Markdown, `git diff --check` clean. `phase-5-0-remediation-r5-handback.md` carries a superseded-disposition note and is retained as review history; the corrupt text is preserved **only in Git history** | that this document is complete, ends in a finished sentence, and passes `git diff --check` |
| **R6-E** — correct cross-reference defects | Important — specification precision | package plan **§2.13.1 row 10** (same lifecycle defect) | **§2.13.5a** **C1** — *"written in C4"* corrected to *the report reaches disk only inside the seal body, written at **C8***, with C4 writing the genesis record and nothing else; **§2.13.2a** — **`M-1`** and **`M-2`** defined as Stage 3's two named cases and **`S4-1 … S4-3`** as Stage 4's | that every case identifier a canonical artifact references has exactly one definition |

**No finding is claimed closed by this table.** It records what changed and where,
so the re-review can check the change rather than the claim.

---

## 2. The probe-evidence lifecycle that was selected, and the one that was not

**The selection: option 1 — run sandbox attribution before seal creation and bind
its exact result into the immutable report.** It is stated in full at package
plan **§2.13.2a**, *Stage 4 — sandbox attribution*, and the comparison is in the
table immediately below it. It is **not** chosen silently: both options are
priced side by side, the reason for the rejection is given, and the choice is
recorded as a change to **D5.0-13 / OD-66 option A's content** — an already-open
decision — rather than adopted here.

**The lifecycle, exactly.**

| Step | Actor | What happens | Where |
|---|---|---|---|
| 1 | root, `verify-capability` | refuses unless the writer unit is **inactive**, **its unit file is deployed**, the `writer_deployment_digest` is supplied and matches the digest computed over the deployed writer's file manifest **including `freedom-sheet-writer.service`**, `…/journal` and `…/archive` carry the §2.13.3 owners and modes, and any `…/probe` residue is reported and cleaned first | §2.13.2a, §2.13.7 |
| 2 | root → `freedomsheet` via `setpriv` | Stage 1 control cases `C-1 … C-6` **must succeed**, or the result is `inconclusive` | §2.13.2a |
| 3 | root → `freedomsheet` | Stage 2 capability cases `P-1 … P-9` | §2.13.2a |
| 4 | root | Stage 3 storage attribution `M-1 … M-2`; `probe_device` recorded | §2.13.2a |
| 5 | root, then `freedomsheet` inside a transient unit | **Stage 4** sandbox attribution `S4-1 … S4-3`: `systemd-run --wait --pipe` with **every hardening directive of the deployed unit verbatim**, one recorded substitution — `ReadWritePaths=` redirected to the **arena**, so no live evidence is touched — and `systemctl show` compared with the deployed unit file, the applied directive set hashed | §2.13.2a |
| 6 | root | the arena is destroyed in a `finally`; a failed cleanup is a **non-zero exit** naming the residue | §2.13.2a |
| 7 | root, Algorithm C **C1** | the probe report `PR` is **built now, from all four stages**, and held in memory | §2.13.5a |
| 8 | root, **C2** | `PR` and `probe_report_digest` go **inside the seal body**, so they are covered by `seal_body_digest` | §2.13.5a |
| 9 | root, **C3–C4** | the genesis record is derived from the body and written; **C4 writes the genesis record and nothing else** | §2.13.5a |
| 10 | root, **C8** | the seal — body ‖ binding — is written. **This is the only step that writes `PR` to disk** | §2.13.5a |
| 11 | root, **C9** | `chattr +i`. The report is now immutable **and complete**, because nothing further is added to it | §2.13.5a |
| 12 | writer, **W4** | at every start: `probe_report_digest` recomputed; all four stages present; every case a pass; `PR.writer_deployment_digest` = `SB.writer_deployment_digest`; refusal `SW-J25` | §2.13.5b |
| 13 | coordinator, **C-d** | the registered `append_only_probe_digest` compared with the value recomputed from disk; refusal `J-16` | §2.13.5b |

**Invalidation, stated because option 2's requirement made it the hard question.**
There is **no new invalidation rule**. Sandbox evidence is invalidated by exactly
what invalidates the rest of the generation: a writer redeployment changes
`writer_deployment_digest`, so **J-22** refuses at **W11**, **F-6** falsifies it,
and a rotation and a fresh `verify-capability` are required before Sheet
mutations resume. **`init-generation` refuses to create a generation whose report
carries a deployment digest other than the one it was given** (**C0**).

**Why option 2 was rejected.** Option 2's own stated requirement is the reason:
the handoff asks how the writer authenticates deployment evidence **without
PostgreSQL**. For a typed artifact written at deployment, outside the `chattr +i`
seal, by an actor the writer cannot verify, with no database available to it, the
honest answer is *it cannot* — not without giving that artifact its own seal,
its own anchor and its own writer check, which is option 1 with more moving
parts and a second artifact that can disagree with the first. Option 1 also makes
the digest claim true **by construction** rather than by narration. The full
comparison — shape, feasibility, writer authentication, invalidation, cost and
risk carried — is package plan §2.13.2a.

**What option 1 costs, stated rather than absorbed.** `verify-capability` now
requires **systemd** and a **deployed unit file** at provisioning time. That is
recorded in **A-5.0-5**, which is widened accordingly and remains **unconfirmed**,
and in the security-review surface and question added at §9.2.

**Falsification cases for the sandbox evidence.** The handoff asks for missing,
stale, altered and wrong-deployment cases, each naming actor, boundary, refusal
code, and what PostgreSQL enforces versus records.

| Case | Actor and boundary | Refusal | PostgreSQL enforces | PostgreSQL records |
|---|---|---|---|---|
| **Missing** — the report carries no Stage 4 | writer **W4**, before any append; coordinator **C-d** | `SW-J25` / `J-16` | nothing about stages; the shape of a digest, a supported version and a non-future timestamp | that *this* report was attested at *this* time |
| **Stale** — a report from a previous deployment | `init-generation` **C0** refuses at creation; writer **W11**/**W4** refuse at start; **J-22** | refuses creation; `SW-J22`, `SW-J25` | nothing | the digest that no longer matches |
| **Altered** — any Stage-4 case result edited inside the seal | writer **W4** (`probe_report_digest` mismatch); coordinator **C-d** | `SW-J25` / `J-16` | nothing | the registered digest the altered report no longer produces |
| **Wrong deployment** — the report describes another unit's directives | `verify-capability` refuses at step 1 (digest mismatch); **C0** refuses; **S4-3** yields `inconclusive` if the applied set differs from the deployed file | non-zero exit; creation refused | nothing | — |
| **Wrong sandbox** — the transient unit did not carry the deployed directives | **S4-3**, inside the probe | **`inconclusive`**, never `passed`; no generation may be created | nothing | — |
| **Corrupt** — the report will not parse | writer **W3**/**W4**; coordinator **C-a** | `SW-J24`, `SW-J25` | nothing | — |

**What PostgreSQL enforces about any of this: nothing whatever.** It enforces
that a well-formed lowercase-hex digest, a value from the closed vocabulary
`append_only_probe_version`, and a timestamp not later than `created_at` were
supplied. It records an attestation whose falsity is **detectable**, because the
report is inside the `+i` seal and three readers recompute its digest. That is
logical schema §3.7.1, which gains a row for the sandbox saying exactly this.

---

## 3. The complete binding-field authentication table

Package plan §2.13.5b carries this table; it is reproduced here because the
handoff requires it in the handback.

**The seal file is `SB ‖ BND` and nothing else.** Its length is exactly
`len(SB) + len(BND)`, so a trailing byte is a refusal.

**The binding section, after remediation R6-B.**

| Field | Where fixed | What **V-W** does with it | Step | Semantic or cryptographic |
|---|---|---|---|---|
| `binding_format_version` | in **`SB`**, not in `BND` | fixes `BND`'s exact structure and length; the writer refuses an unsupported version, a short binding or any trailing byte. `SB` is authenticated by **W13**, so the version cannot be moved | **W3**, transitively **W13** | cryptographic, transitively |
| `genesis_record_digest` | `BND`, at **C7** | **recomputed** from `SB` alone by Algorithm C step **C3** and compared; the same derivation is then compared **byte for byte** with record 0 | **W5**, then **W13** | cryptographic |
| `journal_device` | `BND`, at **C7** | compared with `fstat(st_dev)` of the journal the writer opened | **W7** | semantic, against the filesystem |
| `journal_inode` | `BND`, at **C7** | compared with `fstat(st_ino)` | **W7** | semantic, against the filesystem |
| ~~`sealed_at`~~ | ~~`BND`~~ | **withdrawn.** Nothing recomputed it, nothing compared it, no refusal read it. Its removal is the substantive half of R6-B | — | — |
| ~~a `format version` inside `BND`~~ | ~~`BND`~~ | **withdrawn.** A version the attacker supplies is a version the attacker chooses; it now lives in the chain-authenticated body | — | — |

**Where the withdrawn instant went.** The generation's creation instant is
`SB.created_at`, which record 0 authenticates. The registration instant is the
registered row's `created_at`, which is PostgreSQL's clock and is what the
activation trigger's condition 5 compares against. The sealing instant remains in
the `.close` manifest, written by `seal`. **No timestamp was lost; one that no
verifier read was removed from the artifact the writer trusts.**

**The seal body, in one row rather than thirty.** `seal_body_digest` covers every
byte of `SB`; the genesis record's `prev_hash` **is** `seal_body_digest`; and
**W13** compares record 0 byte for byte with the record the writer derives from
`SB`. Altering any byte of `SB` therefore changes the derived record 0 and fails
that comparison — against the record actually on disk, in a file carrying
`FS_APPEND_FL`.

**The claim this supports, bounded.** *There is no field in the writer-trusted
seal that V-W does not either recompute or compare against an independent
source.* That is a statement about **coverage**, not about **omnipotence**, and
§2.13.5c states the attacker capability it holds against:

- **Class 1** — can write the seal file, cannot clear `FS_APPEND_FL` (no
  `CAP_LINUX_IMMUTABLE`). Every falsification row is refused **by the writer,
  with no database**.
- **Class 2** — holds `CAP_LINUX_IMMUTABLE`, so it can clear `+i` and `+a`,
  rewrite the seal **and** record 0 consistently, and restore both. **The writer
  does not refuse this**, and no check confined to that host could: every
  artifact and attribute it reads is below the privilege that produced it. It is
  refused by the **coordinator**, against the registered row.

**`chattr +i` is not offered as the answer.** It is the attribute class 2 clears
by definition, which is why the classes are stated by capability. **The two new
falsification cases that carry this are `JNL-34a` and `JNL-34b`**, and `JNL-34b`
asserts the **negative** — that V-W completes without refusing — so that if a
future change made the writer refuse F-1b, the test fails and the claim is
re-widened deliberately rather than by drift.

**How *"each half fails closed alone"* is reconciled.**

| Half | Fails closed alone against | Does **not** cover |
|---|---|---|
| the writer, on disk, with no database | **class 1** — every falsification row but **F-1b** | **F-1b**, which is self-consistent on disk |
| PostgreSQL, with no host access | **F-3** — a forged or mutated registration | anything about the bytes on disk |
| the two together, at `observe` | class 1 **and** class 2 | **I-SHEET-COMPLETE**, which no part of this design addresses (§2.13.10) |

---

## 4. The corrected successful-start and absent-`+a` branches

`JNL-32` is replaced by two cases with **opposite** expectations. Package plan
§2.13.8.

| | **`JNL-32a` — successful start** | **`JNL-32b` — absent flag** |
|---|---|---|
| Precondition | `FS_APPEND_FL` **present** on the journal | `FS_APPEND_FL` **cleared by root** on a **disposable** generation |
| How far V-W runs | to **W18** | refuses at **W9** |
| Refusal | none | **`SW-J06`** |
| `W17` / `W18` | **W17 executes; it is the only write** | **neither executes** |
| Journal opened for writing | once, `O_WRONLY\|O_APPEND\|O_NOFOLLOW` | **not at all** — with or without `O_APPEND` |
| `startup` record | **exactly one**, appended | **none** |
| Journal afterwards | its prior bytes **plus that one record** | **byte-for-byte unchanged** |
| Seal afterwards | **byte-for-byte unchanged** | **byte-for-byte unchanged** |
| Archive afterwards | **byte-for-byte unchanged** | **byte-for-byte unchanged** |
| Syscall trace asserts absent | `O_TRUNC`, write-mode open without `O_APPEND`, `ftruncate`, `unlink`, `rename`, `FS_IOC_SETFLAGS` | all of those, **and every write-mode open** |

**Why revision 6 was wrong.** **W9** reads `FS_IOC_GETFLAGS` on the journal and
refuses when `FS_APPEND_FL` is absent — and `ENOTTY`/`EOPNOTSUPP` is a refusal,
not an absence of information. **W17** is nine steps later. A start with `+a`
absent therefore cannot reach the append, so *"the file is byte-identical
afterwards except for that record"* described a state the algorithm makes
unreachable. The correct assertion for that branch is that **nothing was
written**, and it is now the stronger of the two.

**Every repeated form is corrected**, not only the test row: package plan §2.13.2a
(*Live evidence is never probed destructively*), §2.13.5b (the W17 paragraph),
§3 WP-4b, §4's revision-6 movement row is left as history while §6.5 item 15,
§7.1 row 22 and §9.3 stop condition 10f are corrected, and logical schema §4.3.8
Band 3 and §9's traceability row are corrected. The forms that survive a search
are **quotations of the withdrawn wording inside a correction**, and §9 of this
handback lists each one.

---

## 5. Schema impacts

**None to the schema objects.** Revision 7 adds, removes and alters **no** column,
constraint, index, trigger, sequence, closed vocabulary, table or command.
`sealed_at` was never a database column, and the probe's stage placement is a
host-side lifecycle question.

| Artifact | Change |
|---|---|
| `sheet_writer_journal_generations` — columns | **none.** `append_only_probe_digest`'s **note** now names four stages and their cases `C-1 … C-6`, `P-1 … P-9`, `M-1 … M-2`, `S4-1 … S4-3`; `seal_digest`'s note records its second job — it is the only artifact that refuses **F-1b**; `append_only_probe_version`'s note records that `jnl-probe-1` now **denotes** a four-stage procedure, which is a change to the procedure the vocabulary names and not to the vocabulary |
| Constraints, triggers, indexes, FKs | **none** |
| The activation trigger's five conditions | **none** |
| `migration_quiescence_evidence`'s three journal columns | **none** |
| The five commands, the six tables, the `fence_method` vocabulary | **none** |
| Migration `0014` | **not written, and still not authorized** |
| §3.7 prose | new closing paragraph *What this table uniquely can do*, which is the schema half of R6-B |
| §3.7.1 | two new rows in the enforce-versus-record division — the systemd sandbox, and seal integrity against a privileged rewrite — and an added reviewer check for R6-A's claim class |
| §3.0 ER diagram | two annotations, no structure change |
| §4.3.8 Band 3 | case counts, the four new cases, and A-5.0-5 widened |
| §9 traceability | three rows added, two corrected |

---

## 6. Evidence impacts

| | Revision 6 | Revision 7 |
|---|---|---|
| `TC-5.0-JNL` identifiers | 41 | **45** |
| `TC-5.0-JNL` cases | 42 (`JNL-02a/b`) | **48** (`JNL-02a/b`, `JNL-32a/b`, `JNL-34a/b`) |
| §2.13.5c falsification rows | 8 | **12** |
| §6.5 required-evidence items | 16 | **17** |
| §2.13.6 fail-closed conditions | 25 | **25 — unchanged** |
| Refusal codes | `SW-J01 … SW-J25` | **unchanged** |

**The new and changed cases.**

| Case | What it asserts |
|---|---|
| `JNL-29` *(extended)* | Stage 4 runs inside `verify-capability` before the report is built; `S4-1` succeeds inside the substituted `ReadWritePaths=`, `S4-2` fails `EROFS` outside it, `S4-3` compares `systemctl show` with the deployed unit and hashes the applied directive set; a directive-set mismatch yields **`inconclusive`**; **the report contains all four stages and `append_only_probe_digest` is computed over exactly those bytes** |
| `JNL-32a` *(new branch)* | successful start: no destructive operation, **exactly one** appended `startup` record, seal and archive unchanged |
| `JNL-32b` *(corrected branch)* | `+a` absent: refusal at **W9** with `SW-J06` before **W17**, **no write-mode journal open at all**, nothing appended, journal, seal and archive **byte-for-byte unchanged** |
| `JNL-34a` *(new branch)* | **F-1a** — an altered seal body alone is refused by the writer at **W13**, **with no database reachable** |
| `JNL-34b` *(new branch)* | **F-1b** — seal body **and** record 0 rewritten consistently under `CAP_LINUX_IMMUTABLE`: **V-W is asserted to complete without refusing**, and the coordinator refuses at **C-b/C-d** against the registered digests |
| `JNL-42` *(new)* | **F-9** — `BND.genesis_record_digest` altered alone: **W5**, `SW-J24` |
| `JNL-43` *(new)* | **F-10** — `BND.journal_device` altered alone: **W7**, `SW-J11` |
| `JNL-44` *(new)* | **F-11** — `BND.journal_inode` altered alone: **W7**, `SW-J11` |
| `JNL-45` *(new)* | **F-12** — a `sealed_at` field present in the binding, both as a revision-6-layout seal and as a field appended to a current one: **W3**, `SW-J24`; **and the same seal is asserted to have passed revision 6's V-W** |

---

## 7. Estimate, RAID and decision impacts

**Estimate.** PERT **38.2** implementer-days, up from **37.7**. Decomposed at
package plan §4:

| Movement | Effect |
|---|---|
| Revision 6 baseline | 37.7 |
| **WP-8** — four new identifiers, three new branch cases, and `JNL-29`'s added assertions | **+0.4** → 38.1 |
| **WP-15** — Stage 4 moves into `verify-capability`: `systemd-run`, the `ReadWritePaths=` substitution, `systemctl show` capture and hashing, the deployed-unit precondition. **It replaces a deployment-time step rather than adding one** | **+0.1** → 38.15 |
| **WP-4b** — the binding section's exact parse and its four negative tests | **+0.05** → **38.2** |
| WP-1, WP-2, WP-3, WP-4, WP-6, WP-7, WP-9, WP-11, WP-13, WP-14 | **unchanged** |

**Allowances.** Remediation allowance **11.1** days (30 % of ML 37.1), from 11.0.
Contingency **4.0**, unchanged. Independent implementation review **2.5–3.0**
reviewer-days, unchanged. Independent logical-schema re-review **0.5–1.0**,
unchanged. Security-focused review **2.5–3.5** reviewer-days, **unchanged in
figure**, with **one added surface element** and **one added question**.

**Case, control and surface counts.**

| Count | Revision 6 | Revision 7 |
|---|---|---|
| Numeric controls | nine (N5.0-14 … N5.0-23) | **nine — unchanged. No numeric control is added** |
| Security-review surfaces | eleven | **eleven — unchanged in number**; surface 11 gains the transient `systemd-run` unit as a third relaxation |
| Security-review questions | six | **seven** |
| Stop conditions | 1 … 13 with 10b … 10g | **10h added** |
| Fail-closed conditions | 25 | **25** |
| Work packages | fourteen active, WP-5 withdrawn | **unchanged** |

**RAID impacts.**

| Row | Change |
|---|---|
| **A-5.0-5** | **Widened.** It now also requires a transient `systemd-run` unit startable as root at provisioning and a **deployed** `freedom-sheet-writer.service` to read directives from. **Still unconfirmed**, and without it `verify-capability` cannot produce a passing report, so `init-generation` refuses to create a generation at all |
| **R-5.0-9** | **Extended** to the deployed unit's directive set, which Stage 4 records at provisioning and which drifts whenever the unit is edited |
| **D-5.0-1** | **Extended** — the Security Reviewer's scope gains a transient root-started unit that executes the writer's identity under the deployed unit's hardening. Estimate unchanged at 2.5–3.5 reviewer-days |
| **D-5.0-2** | **Extended** — D5.0-13's option A content is amended again |
| **R-03** (existing) | revised estimate **38.2** |
| **New §7.1 row 23** | *the specification describes its own artifacts more strongly than it builds them* — the R6 class, with stop condition **10h** and three boundary tests as its controls, and **not fully prevented** as its residual |
| **R-5.0-8**, **R-5.0-10**, **R-5.0-11** | **unchanged.** R-5.0-8 is narrowed by **no case at all** |
| All other rows | unchanged |

**Decision impacts.** **No decision number is added.** No genuinely new governed
choice exists: the lifecycle question was *where* sandbox evidence lives, and both
placements sit inside **D5.0-13 / OD-66 option A**'s cost, which is open.

| Decision | State |
|---|---|
| **D5.0-9 / OD-62** | **Open, unchanged.** No new impact from R6 |
| **D5.0-10 / OD-63** | **Open, unchanged.** Nine controls; **no new numeric control** |
| **D5.0-11 / OD-64** | **Open, unchanged** |
| **D5.0-12 / OD-65** | **Open, unchanged** |
| **D5.0-13 / OD-66** | **Open. Option A's content is amended in two places and re-stated**: where the probe's sandbox stage runs, and what the seal's binding section contains. Options B, C and D are unchanged, as are the owners, the authorities and the retention rule N5.0-23. **Nothing is decided or recommended into effect** |
| **D5.0-1 … D5.0-8 / OD-54 … OD-61** | **Preserved.** OD-61 remains partly closed: the Security Reviewer is unnamed |

---

## 8. Exact commands run, and their results

Every command was run in `/opt/freedom-blades/platform` on 2026-08-30. **All are
read-only or act on tracked documentation files in the working tree.** No test
suite was run, and none is required for a documentation-only remediation; no
result from an earlier tree is carried forward as current evidence.

| # | Command | Result |
|---|---|---|
| 1 | `cat "docs/review/Handover information"` | the R6 instructions, read in full |
| 2 | `cat .agents/AGENTS.md` (in two ranges) | read in full, as `CLAUDE.md` requires |
| 3 | `wc -l .agents/AGENTS.md docs/implementation-plan.md` | 603 and 2522 lines |
| 4 | `wc -l docs/review/phase-5-0-*.md`, `ls -la docs/review/` | revision-6 artifacts located |
| 5 | `grep -n '^#\{1,4\} ' docs/review/phase-5-0-package-plan.md`, and the same for the logical schema | section inventories |
| 6 | `sed -n` reads of §§1.2, 2.13–2.13.11, 3, 4, 5.3, 6.5, 7.1, 7.4, 8, 9.2–9.4, 10 of the package plan and §§0–4.3.8, 9, 10 of the logical schema | the revision-6 text under remediation |
| 7 | the ten stale-form searches the handoff names, across `docs/` | recorded in §9 below |
| 8 | `git diff --check` | **exit 0, no output.** Re-run after the final edit |
| 8b | `git diff --no-index --check /dev/null <file>` for each of the package plan, the logical schema, this handback and the R5 handback | **clean for all four.** Stated because the two revised artifacts and both handbacks are **untracked** in this worktree, so `git diff --check` alone does not inspect them; this is the equivalent check that does |
| 9 | `git status --porcelain` | only the intended documentation files, plus the pre-existing unrelated worktree changes, which were **preserved** |

**Checks not run, and their owners.** Stated because the handoff requires it and
because §9.3 stop condition 10b forbids describing an unproven property as proven.

| Check | Why not run | Owner |
|---|---|---|
| The `TC-5.0-JNL` band, all forty-eight cases | **the code does not exist and is not authorized.** Every case is a planned assertion, not a result | Technical Lead, after D5.0-13 and the implementation authority |
| `verify-capability` and its four stages, including the new Stage 4 | **no probe was run and no arena was created.** It requires root, `chattr`, `setpriv`, `systemd-run` and a durable hierarchy that does not exist on this host | Operations Owner — **A-5.0-5, unconfirmed** |
| The Band 2 host and authentication matrix | needs real OS identities and a `pg_hba` reload | Operations Owner — **A-5.0-4, unconfirmed** |
| The supervised host reboot (`JNL-02b`) | needs an authorized reboot | Operations Owner |
| The bot, web and Foundry test suites | **not run.** No production or test code changed in this remediation, so a suite result would evidence nothing about it, and a figure from an earlier tree would be an assertion about a state that no longer exists | Technical Lead |
| Formatter, linter, type checker | **not run**, for the same reason: no Python file was touched | Technical Lead |
| The Google-access margin (WP-13) | disposable spreadsheet and service account unavailable | Delivery Lead — **A-5.0-3, unconfirmed** |
| Security review | **the Security Reviewer is unnamed** | Delivery Lead — **D-5.0-1** |

---

## 9. Search results for the stale forms

Run over `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, `docs/project-management/` and
`docs/discovery/open-decisions.md`. **Every surviving hit is one of three kinds:**
a **definition** (the form is now a defined identifier), a **corrected use** (the
form is now true of the artifact), or a **marked quotation** of the withdrawn
wording inside the correction that withdraws it. **No hit is a stale claim.**

| Form | Surviving hits | Disposition |
|---|---|---|
| `written in C4` | package plan **3**; status **1**; change log **1** | **1 corrected use** — Algorithm C **C1** now reads *"`PR` is held in memory and reaches disk only inside the seal body, written at C8"*; the rest are **marked quotations** in the revision-7 status block, the R6-E change row and the two register entries, each naming it as the corrected defect |
| `four stages` | package plan **19**; logical schema **5**; open decisions **4**; status **2**; RAID **1**; change log **1** | **corrected uses throughout.** All four stages now run inside one `verify-capability` invocation **before** the report is built, so the form is true wherever it stands as a claim. The exceptions are **marked quotations** of the false form at package plan §2.13.1 row 10, logical schema's R6-A change row, RAID's superseded re-review note, status's superseded re-review note and open decisions §1792 and §2345 |
| `M-1`, `M-2` | package plan **8** / **7**; logical schema **3** / **3** | **defined.** §2.13.2a Stage 3 now names them as its two cases, and every use points at that definition. One package-plan hit for `M-1` is the substring `VM-16`. The register hits — status **20** / **8**, change log **21** / **10**, RAID **8** / **1**, decision register **1** — are, with one exception, the unrelated **Phase 3 identity-migration** identifiers `M-1 … M-2`, a different identifier space this remediation did not touch; the exception is change log entry `C-P5.0-M`, which names the new definitions |
| `any byte of the seal` | package plan **2** | **marked quotations only**, at §2.13.1 row 11 and at the head of §2.13.5c, both introducing the withdrawal of the claim. **No live claim of this form survives anywhere** |
| `without any database` | package plan **2** | **marked quotations only**, both quoting the withdrawn F-1 wording. §2.13.11 option **J-2** previously carried a live use of this form; it is **rewritten** to bound the claim to §2.13.5c class 1 and to name **F-1b** as what dropping the registration gives up |
| ``with `+a` absent`` | package plan **5**; logical schema **2**; status **1** | **2 corrected uses** — WP-4b and §6.5 item 15, both now naming `JNL-32b`'s no-append expectation; **2 retained-history rows** in the revision-6 change tables at package plan §§156 and 2167, which are the record of what revision 6 said and are labelled as retained; **the rest are marked quotations** in the R6-C concessions and in the status register's record of the finding |
| `except for that record` | package plan **1** | **marked quotation**, §2.13.1 row 12, naming the defect |
| `except for the startup record` | package plan **1**; logical schema **1** | **marked quotations**, in the revision-7 status block and logical schema §9's corrected traceability row |
| `full writer start` | package plan **1**; logical schema **1** | **marked quotations**, both in the R6-C concession rows |

**Counts exclude this handback**, which quotes every one of the ten forms by
design in §§1, 2, 4 and 9. **No surviving hit anywhere is a stale claim**: each is
a definition, a use that the revised artifacts make true, a labelled
retained-history row, or a quotation inside the correction that withdraws it.

**`git diff --check`: run, exit 0, no output.**

---

## 10. Confirmation that no implementation or environment mutation occurred

**No production code, no migration `0014`, no table, no database role, no
database object, no grant, no operating-system account, no group, no
`pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no Google
access change, no configuration or environment change, no directory, no file
outside `docs/`, no file mode, no **filesystem attribute**, no deployment, no
service start, stop or restart, no `systemd-run`, no `chattr`, no `setpriv`, no
`sudo`, no data mutation, no Sheet access, no authority cutover and no Package
5.1+ work.**

- `/var/lib/freedom-sheet-writer` **does not exist on this host and was not
  created**. Neither did `…/journal`, `…/archive`, `…/probe`, any seal, any
  journal, any archive or any generation.
- **No probe was executed**, no arena was created, and no transient unit was
  started. Stage 4 is a specification, not a result.
- **The host was neither read nor written for this remediation.** No
  `/proc/mounts`, `df`, `statvfs`, `systemctl`, `stat` or `chattr` observation was
  taken; every host fact in the documents is the one recorded on 2026-08-29 at
  package plan §8.1, carried forward as previously recorded evidence and labelled
  as such.
- **No test suite, formatter, linter or type checker was run**, because no code
  changed. §8 lists this as a check not run rather than implying a pass.
- **Unrelated worktree changes were preserved.** `git status` before and after
  shows the same pre-existing modified and untracked files outside `docs/`, and
  none was edited, staged, reverted or committed by this remediation.

The only changes are to documents: `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, this file,
`docs/review/phase-5-0-remediation-r5-handback.md` (disposition note only), and
the status, RAID, decision-register, open-decisions and change-log entries, which
**record impacts and approve nothing**.

---

## 11. What P5.0-R1, P5.0-R2 and P5.0-R4 look like after this remediation

| Finding | State | What revision 7 did to it |
|---|---|---|
| **P5.0-R1** | **Open.** Its database half is met by the authority-fence trigger; its Sheet half is not | **Nothing.** §2.10's barrier search is unchanged, its conclusion is unchanged, and **R-5.0-8 is narrowed by no case at all**. §2.13.10 is unchanged: the journal is an enumeration control and **is not** a Google accepted-request completion barrier. It is not offered as one anywhere, and stop condition 10b forbids describing it as one |
| **P5.0-R2** | **Closed, and preserved** | **Nothing.** §2.1's matrix, §2.5's effective-time model and §11's telemetry contract are untouched, and the regression guard remains |
| **P5.0-R4** | **Open** | **Nothing.** §2.12's host boundary, §4.3's grant and authentication matrices and the revision-4 denial evidence plan are unchanged, and **no operational evidence is claimed passed**. The one addition is to the Security Reviewer's scope, which widens the finding's cost rather than closing it |
| **P5.0-R5** | **Blocking** | The three overclaims are corrected and the fourth defect is the handback itself. **No closure is claimed** |
| **OD-55**, **OD-58** | **Closed, and preserved** | No telemetry table and no ledger table exists in this package |

---

## 12. What is requested next

**An independent re-review of revision 7**, on `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md` and this handback.

**This submission claims no finding closed.** It asks the Independent Reviewer to
decide whether the R6 findings are answered, and it does not ask for readiness,
for a gate, or for implementation authority.

**The most useful disagreements would be:**

1. a field in the seal — body or binding — that **V-W** still does not
   authenticate, or one whose stated step does not in fact validate it;
2. a row in §2.13.5c whose stated **attacker class** is wrong in either
   direction, and in particular any class-1 case the writer would not actually
   refuse, or any class-2 case the writer would;
3. a Stage-4 case that does not distinguish the systemd sandbox from the
   filesystem, or a way the transient unit can diverge from the deployed one that
   **S4-3** would not detect;
4. a `TC-5.0-JNL` case whose expected state its own algorithm refuses to
   produce — the R6-C class, which stop condition **10h** now forbids and which a
   second instance would show the guard has not worked;
5. a digest, seal or manifest still described anywhere as covering an artifact, a
   stage or a byte range outside the bytes it is computed over; or
6. a claim that the probe's move to provisioning has quietly created a second
   trust root, a second invalidation rule or a dependency this handback has not
   named.

**Package 5.0 remains `not ready`, and implementation remains unauthorized**
until all Blocking findings are closed, the Security Reviewer is named and
completes review, Peter records D5.0-9 through D5.0-13, and the package
definition of ready is satisfied.
