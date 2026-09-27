# Claude operational handback — C-P5.0-LAB-I3-R8; one unbroken pass, both invocations verified — 2026-09-21

Author: Claude (implementing operator for C-P5.0-LAB-I3-R8).
Authorization: **C-P5.0-LAB-I3-R8**, one fresh I3 controlled-write verification
pass, authorized by Peter Duscha on 2026-09-21 and assigned to Claude. Codex
remains the Independent Technical, Security and Evidence Reviewer and did not
perform this operation.

**State: the pass ran unbroken and both authorized invocations returned run
status `verified`.** No repository guard refused anything. No client, harness,
sandbox, permission-classifier or policy denial occurred. No approval,
escalation or permission exception was requested, and no bypass parameter was
attached to any tool call. All four exclusive-publication contexts verified,
every tracked object was `removed` through its identity guard, no barrier or
descriptor failed, and both final surveys were clean.

**I3 is performed. It is not closed, and the operator does not close it.** This
handback is evidence for independent Codex review and a later maintainer
decision, and nothing more. PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2
remain **Open, Blocking** — this pass does not address, cure or close them. V7
remains excluded and absent; V8 and V10 remain unperformed;
`plan.is_executable=False`; Package 5.0 remains **not ready**; LAB-SECRETS-1
remains Open, Low; LAB-V6-P2 remains deferred. Nothing here approves a digest,
initializes V7, makes the concrete plan executable or authorizes `--execute`.

---

## 1. Refusals, denials and escalation — the express statement R8 requires

Stated first, because the R8 authority turned on it.

| Question | Answer |
|---|---|
| Did `guard-secrets.py` refuse any call? | **No.** |
| Did `guard-git.py` refuse any call? | **No.** |
| Did any other `PreToolUse` hook or repository guard refuse any call? | **No.** |
| Did the client, execution harness, sandbox, permission classifier, policy layer or command tool deny, refuse, reject or block any call? | **No.** |
| Was elevated, bypass, unsandboxed, dangerous or exceptional tool permission requested, indicated as needed, or granted? | **No.** |
| Was `dangerouslyDisableSandbox`, `require_escalated`, an approval request, a sandbox bypass or any equivalent parameter attached to any tool call? | **No.** |
| Was any command re-quoted, split, unchained, reformulated, wrapped, retried or substituted after any response? | **No.** No call was re-issued in any form. |
| Was there any uncertainty whether a response was a refusal, or whether the exact plain command executed? | **No.** Every call returned its ordinary output on the ordinary execution path. |

Every host call in this pass was issued through the client's ordinary, default
execution path, using only the tool's `command` and `description` parameters.

**One nonzero exit status occurred and it was not a refusal.** The read-only
prerequisite call in §4 ended with exit status `1` because its last statement
was `stat` of the canonical root `/var/lib/fb-evidence-p5-0`, which reported
`No such file or directory`. That is the **required absence observation**, not a
denial, not a guard response and not an ambiguity: the command executed, its
output was returned in full, and the nonzero status is the expected result of
observing an absent path. It is disclosed rather than smoothed over, and it is
also the evidence in §6.3 that this harness does surface nonzero exit statuses.

## 2. What was authorized, and what was done

| Authorized | Done |
|---|---|
| the exact plain §3.2 synchronization, as the first synchronization attempt | yes, §3 — one call, executed |
| read-only confirmation of manifest version 17 and review-input digest `c358ea8b…` | yes, §3.3 |
| read-only confirmation of the provisioned items, absences, residue, `protected_hardlinks`, identity facts and interpreter | yes, §4 |
| root verifier invocation — T1 under V4, §2.3.3 under V5, P2 under temporary canonical `R/bin` | yes, §5, §6 — `verified` |
| `ubuntu` verifier invocation — T6 under V9, **only after** complete root success | yes, §5, §6 — `verified`, issued only after the root result was read in full |
| nothing else | **nothing else was done.** §7 states this exhaustively |

No source file, test, hook, manifest, generated artifact, migration, schema or
configuration file was changed by this pass. **No database was invoked and
`TEST_DATABASE_URL` was neither set nor required** — it was verified unset in
the operator environment and no invocation referenced it. No provisioning,
installation, `chmod`, `chown`, group change, capability change or V7
initialization was performed. No participant, evidence-harness run, generated
vector, real boundary, materializer, V8, V10 or `--execute` was invoked. No
historical `/opt/discord-bots/` path was used.

## 3. Synchronization

### 3.1 The exact call, with all tool-call parameters

Issued as the **first** synchronization attempt, with no preliminary
synchronization of any kind, no chained command, no redirection, no
substitution, no wrapper and no trailing comment. Tool: the Claude Code `Bash`
tool. **Parameters passed: `command` and `description` only.** No
`dangerouslyDisableSandbox`, no escalation flag, no approval request, no sandbox
bypass, no equivalent parameter.

The `command` parameter was exactly:

```bash
rsync -avz --delete \
  --include='.env.example' \
  --exclude='.env*' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='yt-cookies.txt' \
  --exclude='*service_account*.json' \
  --exclude='*credentials*.json' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='.pytest_cache/' \
  /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
```

No option or exclusion was altered, added or removed. `--exclude-from` was not
used. No secret was named as a source or destination.

**Did the harness execute it? Yes.** The call was admitted and ran to
completion on the first attempt.

### 3.2 Result

UTC timestamps were taken in their own separate calls immediately before and
after, so that the transferred command remained one plain invocation: started
after **2026-09-21T00:27:04Z**, completed before **2026-09-21T00:27:34Z**.

Transfer list, counted from the recorded list itself rather than estimated:
**27 entries — 20 files and 7 directory entries** (the leading `./` counted as a
directory). Of those, `.git` accounts for **5** entries (3 files, 2 directories)
and the repository proper for **21** (17 files, 4 directories).

```
sent 303,130 bytes  received 19,208 bytes  92,096.57 bytes/sec
total size is 75,275,591  speedup is 233.53
```

The 17 repository files transferred were the implementation plan, the
disposable-server runbook, the four project-management registers, and eleven
`docs/review/` documents including the active handover and the authorized R8
prompt itself.

**No secret-type file appears in the transfer list.** No `.env`, `*.pem`,
`*.key`, `yt-cookies.txt`, service-account or credentials JSON was transferred.
No secret file was read, printed, transferred or modified at any point in this
pass.

**This synchronization mutated the target.** It ran with `--delete` and updated
the remote **repository worktree** at `/opt/freedom-blades/platform` on
`oracle-test`, including Git metadata under `.git/`. That is the authorized
operator preparation this pass permits, and it is disclosed here rather than
covered by a broad claim. It is not a verifier write: it touched no canonical
`R` and none of the four publication directories.

### 3.3 Source identity, target identity and the reproduced digest

Measured **in-process on each host** from `review_manifest.COVERED_SOURCES`. No
file list, capture file or transferred list was used or created on either host.

| Property | Source workspace | Target after synchronization |
|---|---|---|
| Branch / `HEAD` | `docs/platform-plan` / `2fb1d6f` | — (the worktree is a synchronized copy) |
| `MANIFEST_VERSION` | **17** | **17** |
| `COVERED_SOURCES` count | 47 | 47 |
| Reproduced review-input digest | `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26` | `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26` |

The digest was reproduced by the deterministic non-executing generation path
(`build_concrete_plan()` → `ReviewManifest.build(plan, read_covered_sources())`
→ `.digest()`) on both hosts. **It is the digest accepted for the
C-P5.0-LAB-I3-R5 tree.** No evidence-harness invocation was made on the target;
a dry run is still a run, and this authorization does not permit one.

Artifact and verifier SHA-256, identical on both hosts and identical to the
values recorded under C-P5.0-LAB-I3-R6:

| File | SHA-256 |
|---|---|
| `…-evidence-harness-concrete-plan.md` | `ce275fd3cf48ed26d0b2c0ed1193835c68d0390115bc0ec02066db3163b8d263` |
| `…-evidence-harness-review-manifest.json` | `66855575a17ea08b96775e744fe35a3f344902a4311813524a07d6022d0c495c` |
| `execution/i3_verifier.py` | `e7a4b0fc785b227af081a99d853530d3be9233ad3ffa7f83502e58a87c8566ed` |
| `execution/i3_verifier_cli.py` | `9421331ddb8155e86c78a2995f8bc6f81c9945b7ea110727d6252e149f8fc3bd` |

A 50-file aggregate was also computed on both hosts over the 47
`COVERED_SOURCES` entries, the two generated artifacts and runner contract r6:
**`f4120970ac7615b50944b1a2ab27fd689ab37782c282fe9680f7240cad52df36` on both.**

> **Erratum, 2026-09-21 — C-P5.0-LAB-I3-R8-R1, recording Codex finding
> LAB-I3-R8-AGGREGATE-1 (Open, Important).** As returned, the precision note
> below asserted that the two recorded aggregates "were produced by **different
> line-joining formulas**". That was an *explanation offered without evidence*:
> R6's record does not state a joining formula, so nothing in the record
> supported the claim, and an unproven cause must not stand as if it were a
> finding. The assertion is **withdrawn** and replaced by the measured account
> that follows. **No operational evidence is added or withdrawn by this
> erratum**: the `f4120970…` measurement, its source-to-target equality, the
> reproduced review-input digest, the four individual file digests, the
> timestamps and every other observation of this pass stand exactly as
> returned, and no new target-side measurement was made or claimed.

> **Second erratum, 2026-09-22 — C-P5.0-LAB-I3-R8-R2, recording Codex
> re-review finding LAB-I3-R8-AGGREGATE-1 (still Open, Important).** The first
> erratum's replacement text, immediately below, itself overstated its evidence
> in one respect: it said the divergence between the two records is *accounted
> for by the calculation*. It is not. The reproduced calculation shows a
> **possible** explanation; it does not establish the historical cause and does
> not recover R6's formula. That wording is **corrected below**, and the
> historical cause is now recorded as **unresolved** rather than accounted for.
> The candidate-enumeration count is also restated under **one explicit
> convention** — distinct calculations, with candidate descriptions reported
> separately. *(Corrected 2026-09-22 under C-P5.0-LAB-I3-R8-R3,
> LAB-I3-R8-R2-COUNT-1, Open, Important: as returned this erratum said the
> figures "counted two different things", which read as validating both. The
> first erratum's "exactly one of 960 candidates" **mixed the two units** — a
> distinct-calculation numerator over a candidate-description denominator — and
> was **ambiguous, indeed wrong, as written**. Two **candidate descriptions**
> reproduce `f4120970…`; one **distinct calculation** does, among 612.)*
> **No operational evidence is added or
> withdrawn by this erratum either**: the `f4120970…` measurement, its
> source-to-target equality at its measured 50-file scope, the reproduced
> review-input digest, the four individual file digests, the timestamps and
> every other observation of this pass stand exactly as returned, and no new
> target-side measurement was made or claimed.

**A precision note the reviewer should weigh rather than skip.** That aggregate
is **not** the `4d829dc6…` value recorded under R6 and re-recorded under R7, and
this handback does not claim the two measurements were made the same way.

The two recorded values, and the formula each record actually documents:

| Record | Aggregate | Formula as documented in that record |
|---|---|---|
| C-P5.0-LAB-I3-R6 (and re-recorded by C-P5.0-LAB-I3-R7) | `4d829dc6b2f3279cd2f660b0c02b5ee17bf40d8982dffa4fa46c82b6e1cfa12d` | "aggregate SHA-256 over the sorted `<digest>  <path>` lines" — **line format only**. The ordering key, the join separator and the trailing-newline rule are **not stated** |
| C-P5.0-LAB-I3-R8 (this pass) | `f4120970ac7615b50944b1a2ab27fd689ab37782c282fe9680f7240cad52df36` | sorted `<digest>  <path>` lines, sorted **by the whole line**, joined by newline, with **no trailing newline** |

**The limit of the comparison, stated plainly.** Because R6's record does not
document its ordering or trailing-newline rule, the two numbers are **not
comparable as returned**, and neither may be silently discarded or treated as
confirming the other. What this pass measured is the **source-to-target
equality** of the 50-file set under R8's own fully stated formula, together with
the separately reproduced review-input digest `c358ea8b…` and the individually
matching file digests, which **do** equal their R6-recorded values.

**A common-formula calculation, reproduced entirely from local repository
files.** Performed on 2026-09-21 under C-P5.0-LAB-I3-R8-R1 in the repository
workspace only. **No host command was issued and no target-side value was
measured or re-measured.**

* **Input set** — the same 50 files: the 47 `COVERED_SOURCES` entries derived
  in-process from `tools/phase_5_0_evidence/review_manifest.py`, plus
  `docs/review/phase-5-0-evidence-harness-concrete-plan.md`,
  `docs/review/phase-5-0-evidence-harness-review-manifest.json` and
  `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md`.
* **Line format** — `<sha256-hex>` + two spaces + `<path>`, the path spelled
  relative to the repository root, exactly as `COVERED_SOURCES` spells it.
* **Join** — a single `\n` between lines; the joined text encoded UTF-8 (the
  input is ASCII) and hashed with SHA-256.
* **The two varied rules** — the ordering key (the whole line, or the path) and
  the trailing newline (present, or absent).

| Ordering | Trailing newline | Aggregate over the 50 local files | |
|---|---|---|---|
| sorted by path | present | `4d829dc6b2f3279cd2f660b0c02b5ee17bf40d8982dffa4fa46c82b6e1cfa12d` | **equals the R6/R7-recorded value** |
| sorted by path | absent | `1e9f7f5a4444d602b98bcec292360b7bdba93420eff6347b1cbba01b8808ed53` | — |
| sorted by whole line | present | `f88f2ac6321a8f6c8bc3df278f317703c90e40802bdd1f9c6dde4f4a9a168743` | — |
| sorted by whole line | absent | `f4120970ac7615b50944b1a2ab27fd689ab37782c282fe9680f7240cad52df36` | **equals the R8-recorded value** |

**Search breadth, under one explicit counting convention.** Two units are
counted here and they are not the same. The figure first recorded in this
section — "exactly one of 960 candidates" — **mixed them**, and is **ambiguous,
indeed wrong, as written**: 960 counts candidate descriptions, while "one"
counts distinct calculations. The R8-R1 handback's "two candidate descriptions"
was right in its own unit. *(Characterization corrected 2026-09-22 under
C-P5.0-LAB-I3-R8-R3, LAB-I3-R8-R2-COUNT-1, Open, Important; the R8-R2 wording
that both figures "counted two different things" validated a statement that was
not correct as written.)* The two units:

* a **candidate description** is one point in the enumerated parameter space;
* a **distinct calculation** is one distinct byte string actually hashed. Two
  descriptions that produce the same byte string are the same calculation.

**960 candidate descriptions** were enumerated — four path spellings
(repository-relative, `./`-prefixed, basename only, absolute) × eight line
formats (digest-first and path-first, each with two spaces, one space, a tab or
no separator between the fields) × three ordering keys (whole line, path,
digest) × five separators (`\n`, none, space, `\r\n`, NUL) × trailing separator
present or absent. They denote **612 distinct calculations**, which produced
612 distinct aggregate values.

**Exactly one distinct calculation reproduced each recorded value**, and both
are in the table above:

| Recorded value | Candidate descriptions matching | Distinct calculations matching |
|---|---|---|
| `4d829dc6…` (R6/R7) | 1 | 1 |
| `f4120970…` (R8) | 2 | 1 |

The two descriptions reproducing `f4120970…` are the **same** calculation:
under the digest-first line format, ordering by the whole line and ordering by
the digest are the same ordering, because all 50 digests are distinct. Under
that same line format ordering by the path is a different ordering, so
`4d829dc6…` is reproduced by one description only.

**What the reproduction does and does not establish.**

* It **does** establish that the 50 files carry the **same, unmodified local
  bytes** the R6, R7 and R8 records describe. That is independently evidenced:
  the review-input digest reproduces as
  `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26` over the
  47 covered sources (local `python3` 3.12.3, via `build_concrete_plan()` →
  `ReviewManifest.build(plan, execution.cli.read_covered_sources())` →
  `.digest()`), and the three remaining files hash to their individually
  recorded `ce275fd3…`, `66855575…` and `206e40b2…`. So **no byte of the
  measured 50-file set differs between the records**, and the divergence cannot
  be explained by a change in those bytes.
* It **does** establish that both recorded values are reproducible from exactly
  those bytes by two calculations differing only in the ordering key and the
  trailing-newline rule. That is a demonstration of **possibility**: it shows
  the two records *can* diverge with no byte differing.
* It **does not** establish that this is what happened. A calculation that
  reproduces a value is **a possible explanation, not the historical cause**.
  The cause of the divergence is therefore **unresolved**, not accounted for,
  and this handback does not claim otherwise.
* It **does not** establish what calculation R6 executed, and **does not
  recover R6's formula**. R6's record documents no ordering key and no
  trailing-newline rule, so a matching value is not a retrieval of its formula,
  and **no such inference is drawn here**. It is equally not asserted that R6
  and R8 "used different formulas" as a fact about what either operator ran;
  what is asserted is only that the two *records* document different
  calculations, one of them incompletely.
* It is a **repository-workspace** result. It makes no statement about the
  target, adds no target-side measurement, and changes nothing this pass
  observed on `oracle-test`.

**Residual uncertainty, left open deliberately.** Both the **cause of the
mismatch** and the **specific calculation R6 performed** remain **unrecorded
and unresolved**. Only a record from that pass — not a matching value — could
resolve either. **LAB-I3-R8-AGGREGATE-1 remains Open for independent Codex
re-review.**

**Scope of this identity claim, per the closed PR-20260920-LAB-I3-R7-R1-2.** The
measurement covers exactly those 50 files. It does **not** cover the complete
workspace and does not cover every path the repository-wide §3.2 synchronization
transferred. No whole-tree byte-for-byte claim is made.

**The digest is review input. It is not approval, it is not an I3 confirmation,
and it is never authority for `--execute`.**

## 4. Read-only prerequisite observations, before the first controlled write

All taken on `oracle-test` after synchronization and before either verifier
invocation, between **00:27:34Z** and **00:29:26Z**. Every reviewed prerequisite
was found exactly as the R6 record describes.

| Item | Expected | Observed | Result |
|---|---|---|---|
| kernel nodename | `Test` | `Test` | **matches** |
| kernel release | `7.0.0-31-generic` | `7.0.0-31-generic` | matches |
| architecture | `x86_64` | `x86_64` | matches |
| V1 | group `freedomlab` | `freedomlab:x:986:ubuntu` | matches |
| V2 | `ubuntu` in `freedomlab` | `1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd),986(freedomlab)` — the five prior groups retained | matches |
| V3 | `/etc/tmpfiles.d/freedom-blades-laboratory.conf` `root:root 0644` | regular file, `root:root 0644`, `2049:1898` | matches |
| V12 | `/var/lib/freedom-blades` `root:root 0755` | directory, `root:root 0755`, `2049:1275049` | matches |
| V4 | `…/laboratory` `root:freedomlab 0750` | directory, `root:freedomlab 0750`, `2049:1275050` | matches |
| V9 | `…/laboratory/runs` `root:freedomlab 03770` | directory, `root:freedomlab 3770`, `2049:1275051` | matches |
| V5 | `…/recovery` `root:root 0700` | directory, `root:root 0700`, `2049:1275052` | matches |
| V7 | **absent** | `laboratory` holds only `runs`; no `lifecycle.json`, no `.tmp` | absent, as required |
| canonical `R` | **absent** | `/var/lib/fb-evidence-p5-0`: `No such file or directory` | absent, as required |
| `.fb-i3-verify-` residue | none | `find /var/lib/freedom-blades -name '.fb-i3-verify-*'` returned **0** entries | none |
| whole laboratory tree | only the three provisioned directories | `laboratory`, `laboratory/runs`, `recovery` and nothing else | matches |
| `fs.protected_hardlinks` | `1` | `1` | matches |
| interpreter | `/opt/freedom-blades/runtime/venv-web/bin/python` available | present, Python `3.12.14` | available |
| `/run` objects (V3-created) | `/run/freedom-blades` `root:freedomlab 0750`; `laboratory.lock` `0660` | `root:freedomlab 0750`, `29:11451`; lock `root:freedomlab 0660`, `29:11452` | matches |
| mount for `/var/lib` | `ext4` on `/dev/sda1`, read-write | `/dev/sda1 ext4 rw,relatime,discard,errors=remount-ro,commit=30` | matches |

The residue and whole-tree checks used `sudo` for read access only, because V5
is `root:root 0700` and `ubuntu` cannot traverse it. **Nothing was written,
repaired, installed, provisioned, `chmod`ed, `chown`ed, group- or
capability-changed, or initialized.**

**The protected `/tmp` evidence artifacts were not touched.**
`/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt`
were **not read, not `stat`ed, not deleted, not truncated, not overwritten, not
moved, not modified and not reused.** No command in this pass named any of them.
This is stricter than the R6 pass, which took `stat` metadata; R8 forbids that
and it was not done.

No prerequisite was missing, changed, ambiguous or refused, so the pass
continued to the first controlled write.

## 5. The invocations actually run

Both were run from `/opt/freedom-blades/platform` on `oracle-test`, each as the
identity it names, with **no added flag, no ad hoc wrapper, no substituted probe
and no direct invocation of a verifier object**. Output was captured **only in
the client transcript**: no host-side capture file was created and no output
redirection was used.

### 5.1 Root invocation

Executed shell command, verbatim:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && sudo /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.i3_verifier_cli --arm-i3-controlled-write --identity root"
```

The reviewed verifier **argv** inside it is exactly the authorized one:

```
/opt/freedom-blades/runtime/venv-web/bin/python
  -m tools.phase_5_0_evidence.execution.i3_verifier_cli
  --arm-i3-controlled-write --identity root
```

`ssh` and `cd` are the transport and the working directory; they are stated
rather than implied away, following the C-P5.0-LAB-I3-R4-E1 precision rule. No
`date`, no redirection, no `cat`, no exit-status capture command, no script and
no wrapper were interposed.

| | |
|---|---|
| Identity | `root`, via `sudo`; the process already was root at admission |
| Started after | 2026-09-21T00:29:26Z |
| Completed before | 2026-09-21T00:29:36Z |
| Run status | **`verified`** |
| Exit status | **`0`** — see §6.3 |
| stderr | **empty** |

### 5.2 `ubuntu` invocation

Issued **only after** the root result above was read in full and found to be
`verified` with all three contexts verified, every tracked object `removed`,
every barrier and descriptor successful and a clean survey. Executed shell
command, verbatim:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.i3_verifier_cli --arm-i3-controlled-write --identity ubuntu"
```

No `sudo`. The session is the already logged-in `ubuntu` identity
(`uid=1001 gid=1001`), which is what the argument names.

| | |
|---|---|
| Identity | `ubuntu`, no privilege change |
| Started after | 2026-09-21T00:29:36Z |
| Completed before | 2026-09-21T00:29:57Z |
| Run status | **`verified`** |
| Exit status | **`0`** — see §6.3 |
| stderr | **empty** |

## 6. Complete safe output

Reproduced verbatim from the client transcript. Every field is a member of the
reviewed closed vocabulary; no path, host account name or number, listing,
environment value or exception text appears, which is the contract
`i3_verifier_cli` states.

### 6.1 Root invocation

```
I3 CONTROLLED-WRITE VERIFICATION — VERIFIED
  invocation           : root
  refusal              : none
  hard-link policy     : 1
  identity             : proven before the first write — real, effective, saved and filesystem uid and gid
  capability at admission:
      CapInh 0000000000000000  CapPrm 000001ffffffffff  CapEff 000001ffffffffff
      CapBnd 000001ffffffffff  CapAmb 0000000000000000  NoNewPrivs 0
      cap_dac_override     permitted yes effective yes bounding yes inheritable no  ambient no
      cap_dac_read_search  permitted yes effective yes bounding yes inheritable no  ambient no
      cap_fowner           permitted yes effective yes bounding yes inheritable no  ambient no
  context T1           : verified
      nonce              : e0a68b1b6647347c2e1c53a204ac74b7
      object identity    : 2049:1275058
      file mode          : 0600
      owner condition    : observed — the linking process's filesystem uid owns the file
      link count         : 2 with both names, 1 after the temporary was removed
      payload            : matched through both names
      capability at link :
          CapInh 0000000000000000  CapPrm 000001ffffffffff  CapEff 000001ffffffffff
          CapBnd 000001ffffffffff  CapAmb 0000000000000000  NoNewPrivs 0
          cap_dac_override     permitted yes effective yes bounding yes inheritable no  ambient no
          cap_dac_read_search  permitted yes effective yes bounding yes inheritable no  ambient no
          cap_fowner           permitted yes effective yes bounding yes inheritable no  ambient no
      stages completed   : temporary-exclusive-create, payload-write, payload-data-barrier, ownership-and-mode, temporary-read-back, write-descriptor-release, operation-time-process-state, exclusive-link, two-name-observation, temporary-guarded-removal, published-single-name-observation, published-guarded-removal, containing-entry-barrier, absence-observation
      object             : temporary-name removed [2049:1275058]
      object             : published-name removed [2049:1275058]
      cleanup barriers   : 0 failed; descriptors not released: 0
  context S2.3.3       : verified
      nonce              : 2ebd0379f4ade084e8c8e4729862afee
      object identity    : 2049:1275058
      file mode          : 0400
      owner condition    : observed — the linking process's filesystem uid owns the file
      link count         : 2 with both names, 1 after the temporary was removed
      payload            : matched through both names
      capability at link :
          CapInh 0000000000000000  CapPrm 000001ffffffffff  CapEff 000001ffffffffff
          CapBnd 000001ffffffffff  CapAmb 0000000000000000  NoNewPrivs 0
          cap_dac_override     permitted yes effective yes bounding yes inheritable no  ambient no
          cap_dac_read_search  permitted yes effective yes bounding yes inheritable no  ambient no
          cap_fowner           permitted yes effective yes bounding yes inheritable no  ambient no
      stages completed   : temporary-exclusive-create, payload-write, payload-data-barrier, ownership-and-mode, temporary-read-back, write-descriptor-release, operation-time-process-state, exclusive-link, two-name-observation, temporary-guarded-removal, published-single-name-observation, published-guarded-removal, containing-entry-barrier, absence-observation
      object             : temporary-name removed [2049:1275058]
      object             : published-name removed [2049:1275058]
      cleanup barriers   : 0 failed; descriptors not released: 0
  context P2           : verified
      nonce              : a973ac88b1726b4483d1345048bddd39
      object identity    : 2049:1275060
      file mode          : 0555 (ownership applied on the descriptor)
      owner condition    : observed — the linking process's filesystem uid owns the file
      link count         : 2 with both names, 1 after the temporary was removed
      payload            : matched through both names
      capability at link :
          CapInh 0000000000000000  CapPrm 000001ffffffffff  CapEff 000001ffffffffff
          CapBnd 000001ffffffffff  CapAmb 0000000000000000  NoNewPrivs 0
          cap_dac_override     permitted yes effective yes bounding yes inheritable no  ambient no
          cap_dac_read_search  permitted yes effective yes bounding yes inheritable no  ambient no
          cap_fowner           permitted yes effective yes bounding yes inheritable no  ambient no
      stages completed   : canonical-root-create, canonical-root-ownership-and-mode, canonical-root-entry-barrier, canonical-bin-create, canonical-bin-ownership-and-mode, canonical-bin-entry-barrier, canonical-mount-observation, temporary-exclusive-create, payload-write, payload-data-barrier, ownership-and-mode, temporary-read-back, write-descriptor-release, operation-time-process-state, exclusive-link, two-name-observation, temporary-guarded-removal, published-single-name-observation, published-guarded-removal, containing-entry-barrier, absence-observation, canonical-bin-guarded-removal, canonical-bin-removal-barrier, canonical-root-guarded-removal, canonical-root-removal-barrier, canonical-root-absence-observation
      object             : canonical-root removed [2049:1275058]
      object             : canonical-bin removed [2049:1275059]
      object             : temporary-name removed [2049:1275060]
      object             : published-name removed [2049:1275060]
      cleanup barriers   : 0 failed; descriptors not released: 0
  residue survey       : 0 verifier names found; canonical root absent
  descriptors          : 0 directory roles not released
  statement            : Capability masks are recorded as evidence and are never attribution. This verifier does not isolate, require or prove CAP_FOWNER, and it never reads CapBnd as CapEff. Each publication relies on the protected-hardlink filesystem-UID owner condition, which is observed; a root link that succeeds cannot show which permitted branch the kernel took.
  not observed         : securebits is not observed: the kernel exposes it only through prctl(2), and the one ctypes exception in this package belongs to the case program.
```

standard error: **empty**.

### 6.2 `ubuntu` invocation

```
I3 CONTROLLED-WRITE VERIFICATION — VERIFIED
  invocation           : ubuntu
  refusal              : none
  hard-link policy     : 1
  identity             : proven before the first write — real, effective, saved and filesystem uid and gid
  capability at admission:
      CapInh 0000000000000000  CapPrm 0000000000000000  CapEff 0000000000000000
      CapBnd 000001ffffffffff  CapAmb 0000000000000000  NoNewPrivs 0
      cap_dac_override     permitted no  effective no  bounding yes inheritable no  ambient no
      cap_dac_read_search  permitted no  effective no  bounding yes inheritable no  ambient no
      cap_fowner           permitted no  effective no  bounding yes inheritable no  ambient no
  context T6           : verified
      nonce              : a9cf4e38d249fa8f2fd9eadda28a6f24
      object identity    : 2049:1275058
      file mode          : 0600
      owner condition    : observed — the linking process's filesystem uid owns the file
      link count         : 2 with both names, 1 after the temporary was removed
      payload            : matched through both names
      capability at link :
          CapInh 0000000000000000  CapPrm 0000000000000000  CapEff 0000000000000000
          CapBnd 000001ffffffffff  CapAmb 0000000000000000  NoNewPrivs 0
          cap_dac_override     permitted no  effective no  bounding yes inheritable no  ambient no
          cap_dac_read_search  permitted no  effective no  bounding yes inheritable no  ambient no
          cap_fowner           permitted no  effective no  bounding yes inheritable no  ambient no
      stages completed   : temporary-exclusive-create, payload-write, payload-data-barrier, ownership-and-mode, temporary-read-back, write-descriptor-release, operation-time-process-state, exclusive-link, two-name-observation, temporary-guarded-removal, published-single-name-observation, published-guarded-removal, containing-entry-barrier, absence-observation
      object             : temporary-name removed [2049:1275058]
      object             : published-name removed [2049:1275058]
      cleanup barriers   : 0 failed; descriptors not released: 0
  residue survey       : 0 verifier names found; canonical root absent
  descriptors          : 0 directory roles not released
  statement            : Capability masks are recorded as evidence and are never attribution. This verifier does not isolate, require or prove CAP_FOWNER, and it never reads CapBnd as CapEff. Each publication relies on the protected-hardlink filesystem-UID owner condition, which is observed; a root link that succeeds cannot show which permitted branch the kernel took.
  not observed         : securebits is not observed: the kernel exposes it only through prctl(2), and the one ctypes exception in this package belongs to the case program.
```

standard error: **empty**.

### 6.3 How the exit status is evidenced — stated precisely

No `$?` value was captured in a separate variable, because doing so would have
required either chaining a capture command onto the authorized invocation or
creating a host-side capture file. R8 forbids the auxiliary artifact and
requires the invocation to be exact, and the R4-E1 correction criticised the
chained form's opacity. The exit status is evidenced instead by four facts, and
a reviewer should weigh it as such rather than as a directly printed integer:

1. `ssh` propagates the remote command's exit status as its own, and the client
   tool reported **no command failure** for either call;
2. **this harness demonstrably surfaces a nonzero status**, shown in this same
   pass by the §4 prerequisite call, which was reported as `Exit code 1` for its
   trailing `stat` of the absent canonical root. A nonzero status from either
   invocation would have been surfaced the same way and was not;
3. the rendered run status is `verified` for both, and
   `i3_verifier_cli.EXIT_CODES` maps `Status.VERIFIED` to `0` and to no other
   value; and
4. `main()` writes `NOT VERIFIED — <status>.` to **standard error** for every
   code other than `0`. **Both stderr streams were empty**, which is
   inconsistent with any nonzero exit.

If the reviewer wants a directly captured integer, that requires a further
authorized invocation. This pass does not repeat one.

## 7. Per-context evidence, consolidated

### 7.1 Root invocation — three contexts

| | T1 (V4) | §2.3.3 (V5) | P2 (canonical `R/bin`) |
|---|---|---|---|
| status | `verified` | `verified` | `verified` |
| nonce | `e0a68b1b6647347c2e1c53a204ac74b7` | `2ebd0379f4ade084e8c8e4729862afee` | `a973ac88b1726b4483d1345048bddd39` |
| published object identity | `2049:1275058` | `2049:1275058` | `2049:1275060` |
| file mode | `0600` | `0400` | `0555`, ownership applied on the descriptor |
| owner condition | observed | observed | observed |
| link count | 2 with both names, 1 after the temporary was removed | same | same |
| payload | matched through both names | matched through both names | matched through both names |
| stages completed | 14 | 14 | 26 |
| tracked-object fates | temporary-name `removed`; published-name `removed` | same | canonical-root `removed` `[2049:1275058]`; canonical-bin `removed` `[2049:1275059]`; temporary-name `removed`; published-name `removed` |
| cleanup barriers failed | 0 | 0 | 0 |
| descriptors not released | 0 | 0 | 0 |

Capability evidence, identical at admission and at every link:
`CapInh 0000000000000000`, `CapPrm 000001ffffffffff`, `CapEff 000001ffffffffff`,
`CapBnd 000001ffffffffff`, `CapAmb 0000000000000000`, `NoNewPrivs 0`.
`cap_dac_override`, `cap_dac_read_search` and `cap_fowner` were each permitted,
effective and bounding, and neither inheritable nor ambient. `CapBnd` was never
read as `CapEff`. Hard-link policy read `1`.

### 7.2 `ubuntu` invocation — one context

| | T6 (V9) |
|---|---|
| status | `verified` |
| nonce | `a9cf4e38d249fa8f2fd9eadda28a6f24` |
| published object identity | `2049:1275058` |
| file mode | `0600` |
| owner condition | observed |
| link count | 2 with both names, 1 after the temporary was removed |
| payload | matched through both names |
| stages completed | 14 |
| tracked-object fates | temporary-name `removed`; published-name `removed` |
| cleanup barriers failed | 0 |
| descriptors not released | 0 |

Capability evidence, identical at admission and at the link:
`CapInh 0000000000000000`, `CapPrm 0000000000000000`, `CapEff 0000000000000000`,
`CapBnd 000001ffffffffff`, `CapAmb 0000000000000000`, `NoNewPrivs 0`. All three
named capabilities were **bounding only** — not permitted, not effective, not
inheritable, not ambient. **This is the sharper half of the evidence:** T6's
`linkat` succeeded under a process holding no effective `CAP_FOWNER` and no
effective `CAP_DAC_OVERRIDE`, so for that publication the
`protected_hardlinks=1` owner condition is the only branch that can have
permitted it.

### 7.3 A reader's note on repeated inode numbers

`2049:1275058` appears as the published identity of T1, §2.3.3, T6 and, as the
canonical root, in P2. These are **different objects at different times**: each
context creates its object, observes it, removes it and observes its absence
before the next begins, and ext4 reuses a freed inode number. The identities
that must be distinct within one live moment — P2's canonical root
`1275058`, its `R/bin` `1275059` and its published file `1275060` — are
distinct. Nothing here indicates a collision, and no context observed a foreign
or replacement object.

## 8. Final survey, residue and the resulting state

Both invocations' own final surveys — the mechanism's authoritative residue
check under runner contract r6 §7.4.5 — reported **0 `.fb-i3-verify-` names
found** in every held publication directory and **canonical root absent**, with
**0 directory roles not released**. Every tracked object in every context has
fate `removed`, which the contract defines as removed after a matching identity
comparison with absence then observed. No object has any residue fate. No
foreign object was met, no name was found occupied, and no removal barrier
failed.

**The resulting state, stated precisely.** On the evidence of those two clean
surveys and the four all-`removed` context inventories, the target's laboratory
topology is exactly what §4 observed before the first write: V1, V2, V3, V12,
V4, V9 and V5 provisioned as reviewed; V7 absent; canonical
`/var/lib/fb-evidence-p5-0` absent; no `.fb-i3-verify-` residue. The one
operator-caused change to the target in this pass is the synchronized repository
worktree of §3.2.

## 9. Host-side objects, and what the operator did not touch

**No host-side object outside the verifier-controlled exemption was created.**

* No `scp`, `sftp` or second `rsync` was used. The only transfer was the single
  authorized `rsync` of §3.
* No file list, capture file, output redirection, wrapper, script, scratch file
  or `/tmp` object was created on either host. All output was captured only in
  the client transcript.
* The comparison file set of §3.3 was derived **in-process on each host** from
  `review_manifest.COVERED_SOURCES`, never from a transferred or written list.
* **The operator never manually inspected, created, edited, moved, repaired or
  removed a verifier object.** The `.fb-i3-verify-<nonce>-*` objects, the
  temporary canonical `R` and `R/bin` existed only inside the reviewed verifier,
  which created and removed them itself. No operator command named any of them.
* The three protected `/tmp` evidence artifacts were not read, `stat`ed,
  deleted, truncated, overwritten, moved, modified or reused, and no command
  named them.

This pass therefore repeats neither of the two R6 faults: there was no stop
condition to continue past, and there was no unauthorized host write.

## 10. Checks not run, and why

* **No post-run host inspection was performed.** R8's authorized-preparation
  list is exhaustive — the exact synchronization, the read-only prerequisite
  confirmations, and the two invocations — and a post-run survey is not on it.
  The operator did not issue one rather than widen the authority by its own
  reading. **What this means for the evidence:** the resulting state in §8 rests
  on the verifier's own final surveys and tracked-object inventories, which are
  the reviewed mechanism's residue check, and **not** on an independent
  operator-issued re-observation after the runs. A reviewer wanting that
  independent confirmation must authorize it separately.
* **No exit-status integer was captured directly**, for the reasons in §6.3.
* **No test suite was run**, and **no suite figure is cited or claimed.** This
  pass is operational verification on the target, not a repository change; no
  source, test or artifact was modified, so there is nothing for a suite to
  characterize. `TEST_DATABASE_URL` was verified unset and no database was
  invoked, as required.
* **No evidence-harness invocation, dry run or generated vector on the target.**
  The digest was reproduced by the non-executing generation path, on both hosts.
* **V8 and V10 were not performed**, and nothing here bears on them. The
  barriers this pass issued were issued, not verified, so I2 is untouched.
* **The concrete plan's own P2 was not run.** The verifier does not run it.

## 11. What this evidence supports, stated narrowly

Exactly this: **in the approved target's real filesystem, each of the four
reviewed contexts created its temporary by exclusive `openat`, wrote and
`fsync`ed the fixed payload, applied the reviewed ownership and mode on the
descriptor, read the object back through the descriptor, published it with
`linkat`, observed it under both names with link count two and the pinned
payload digest, removed both names under identity guards, barriered the
containing directory and observed both names absent — with the
protected-hardlink filesystem-UID owner condition observed at each
publication, under `fs.protected_hardlinks=1`.**

What it does **not** support, restated from runner contract r6 §7.4.6:

* nothing about V8 or I2 — the barriers are issued, not verified;
* nothing about V10;
* nothing about the concrete plan's own P2, which this verifier does not run;
* **no capability causation.** The verifier does not isolate, require or prove
  `CAP_FOWNER`. For the root invocation, a process with effective
  `CAP_DAC_OVERRIDE` also satisfies the read-and-write branch, so a root link
  that succeeds cannot show which branch the kernel took. `CapBnd` was never
  read as `CapEff`. What is shown is that the owner condition held. The
  `ubuntu` invocation is the narrower case described in §7.2;
* nothing beyond the four contexts actually exercised.

## 12. Repository state

| | |
|---|---|
| Branch / `HEAD` | `docs/platform-plan` / `2fb1d6f` |
| Working tree before this pass | **90 paths — 34 modified, 56 untracked** |
| Working tree after the operational steps, before this handback was written | **90 paths — 34 modified, 56 untracked** — unchanged; the operational steps modified nothing locally |
| Working tree after this handback and the documentation reconciliation | **91 paths — 34 modified, 57 untracked**; the one added path is this handback |
| `git diff --check` | clean, before and after |

Unrelated and earlier-pass working-tree changes were inspected before acting and
**preserved**; none was touched, reclassified or reverted. No commit, push,
rebase, amend, reset or history rewrite was performed or attempted.

The seven controlled documents reconciled to what actually happened are the
active handover, implementation-plan §20, the disposable-server restriction
banner, and the status, RAID, decision and change registers.

## 13. Disposition

**C-P5.0-LAB-I3-R8 is consumed by this completed pass.** The authority ends
here.

This was an unbroken pass in which both invocations verified, so **I3 is
performed**. **I3 remains unconfirmed and not closed**, pending independent
Codex technical, security and evidence review and Peter Duscha's later decision.
The operator closes nothing, approves no digest, accepts no risk and advances no
gate.

PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**;
V7 remains excluded and absent; V8 and V10 remain unperformed;
`plan.is_executable=False`; Package 5.0 remains **not ready**; LAB-SECRETS-1
remains Open, Low; LAB-V6-P2 remains deferred.

**Next step: independent Codex technical, security and evidence review.**
No further host command will be issued under this authority.
