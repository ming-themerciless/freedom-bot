# Preparation handback — fresh R-5 independent-rebuild assignment

Work ID: `C-P5.0-R5-RP11-FRESH-A1`

Date: 2026-10-02

Drafting assignee: Claude, appointed by Peter Duscha, who accepted this
preparation task in this session

Controlling prompt:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md)
(SHA-256 `86accd3deacb3adc774db967cabd542ae4c3fc90758bbe8d0cdfab8a19121054`)

Output:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)

Status: **Draft prepared. It is not accepted, not assigned and not
executable. Claude has stopped.** Next: independent Codex review, then Peter
Duscha's decision, which names the executor if the draft is accepted. Claude
implemented I-7/I-7-R1. It is therefore ineligible to execute R-5, to be the
R-5 assignee, to select or appoint one, or to review or accept this draft. It
makes no claim about any future R-5 result.

---

## 1. Result

The proposed assignment covers every element of the prompt:

* §4.1 independence (the assignee is TBD, Claude is ineligible, the executor
  attests independence, and Gemini must use only wholly fresh resources);
* §4.2 pinned inputs, with 28 file digests and the in-memory review-manifest
  reproduction;
* §4.3 the LD-8 variation rules with exact-string comparison;
* §4.4 unique paths and forbidden reuse;
* §4.5 the 12 ordered steps through the accepted same-invocation
  `enter.py build` gate;
* §4.6 PASS, INVALID RUN and HARD STOP;
* §4.7 the minimum host actions, the banner treatment and the forbidden list;
  and
* §4.8 the 16-item handback contract.

No controlling value differed from the prompt's §2 (see §4). No accepted
records were found to conflict materially. The draft creates no new policy:
every gate in it is either an accepted gate or the repository's existing
tooling applied as written. Two places go beyond the earlier assignment and
need reviewer disposition: the `resolve` signature gate (U-2) and the
checkout transport (U-5).

## 2. Sources read

Read completely:

* `CLAUDE.md`; `.agents/AGENTS.md`;
* `docs/review/Handover information`; `docs/project-management/status.md`;
* this prompt;
* the B1-R4 acceptance record;
* the original R-5 assignment; the Antigravity review; the R-5 assignment
  acceptance; the bubblewrap-stop review; the bubblewrap-install authority;
  and the stopped R-5 handback;
* the R3 acceptance; the R4-R1 acceptance and reference-reproduction
  decision;
* the D2-R1 decisions record (LD-7, LD-8); the D2-R2 acceptance (LD-9);
* the I-7 Codex review; the I-7-R1 Codex re-review; the I-7-R1 acceptance;
* the B1 prompt; the B1-R2 handback;
* `infra/rp11-launch/toolchain.lock`, `expected.sha256`, `build.sh`,
  `buildroot/provision.py`, `buildroot/enter.py` and `verify/cc1check.py`;
  and
* `tests/test_rp11_launch_toolchain.py`.

Read by section or in part:

* `docs/implementation-plan.md`: the reading map, §0, §13, §16, §17 and §20;
* `docs/operations/disposable-test-server.md` lines 1–140, including the
  current restriction banner, machine profile, access and sync procedure;
* the D2 proposal: section index; §5.3.2, §5.3.4 (tail), §5.3.5–§5.3.8,
  §5.12.3; and the LD-8 rows located by search;
* the B1 handback, §§1–3;
* the B1-R4 handback, §1 and §2 opening;
* the R2 handback, §§1–2;
* `build-root.manifest`, checked by digest and size only (3,641 lines; not
  read line by line); and
* `tools/phase_5_0_evidence/review_manifest.py` (digest function and
  `RP11_LAUNCH_COVERED`), `tools/phase_5_0_evidence/execution/cli.py`
  (docstring and `main`) and `tools/phase_5_0_evidence/rp11_launch.py`
  (constants only).

Located by search only, not read in full:

* the I-7 and I-7-R1 handbacks (reference HA facts, R-5 mechanism, HA-1 …
  HA-5 statements);
* the B1-R3 handback (manifest/plan digests);
* the R3, R4 and R4-R1 handbacks (`cc1.v` and GGC statements); and
* the B1-R1, B1-R3 and B1-R4 prompts, the I-7 and I-7-R1 prompts, and the R2,
  R3, R4 and R4-R1 prompts, which were sized but not opened.

The prompt's §3 asks for items 7 and 9 to be read. The partial coverage above
is a disclosed shortfall for the reviewer to weigh. The draft's substantive
requirements are taken from the records read in full.

## 3. Read-only commands used

All of these ran on the repository host in `/opt/freedom-blades/platform`.

* `wc -l` on the required documents; `git status --short`;
  `git status --short --ignored -- infra`; `git log --oneline`;
  `git rev-parse HEAD`; `git rev-parse --abbrev-ref HEAD`; `git remote -v`;
  `git cat-file -p HEAD | head`; `git diff --quiet HEAD`;
  `git ls-files -s -- <§3.2 files>`.
* `sed -n`, `cat`, `grep -n`, `ls` and `find infra/rp11-launch -type f` on
  the documents and sources above; `cat -A … | cut -c1-300` on the fixture.
* `sha256sum <28 files + acceptance record + prompt>`, writing its list to
  the session scratchpad (`…/scratchpad/sums.txt`, outside the repository).
  Python `hashlib` then recomputed every digest independently and compared it.
* An in-memory review-manifest reproduction, with no file writes:
  `python3 -B -c` importing `build_concrete_plan`, `read_covered_sources`
  and `ReviewManifest`. It printed version `30`, aggregate `28a4f4c2…a526`,
  serialization byte-equal to the checked-in JSON (SHA-256 `c9afaf7c…4b5c`),
  and `is_executable False`. This imports repository modules. It is not the
  harness CLI and not `--execute`.
* `grep -c '^package='` (62) and `grep -c '^def test_'` (9 functions, which
  parametrize to 12 tests).
* A syntax check of the draft's step-1 `hashlib` snippet on
  `expected.sha256`, and of its `awk` filter on a **synthetic**
  `cpuinfo.sample` file written to the scratchpad. No host `/proc` was read.

**Guard refusal.** I ran one `git ls-files | grep -E -i …` to list tracked
filenames resembling secret-bearing patterns. Its text named `.env`, and
`guard-secrets.py` refused it. I treated the refusal as a stop for that check:
it was not retried or rephrased, and the question is carried as U-5.

## 4. Digests independently calculated

Every value below was calculated twice, once with `sha256sum` and once with
Python `hashlib`, and both agreed. The tree was clean against `HEAD`
`9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa`. The assignment's §3.2 lists all
28 controlling file digests with byte lengths. The values that the prompt's §2
fixes, and their results:

| Item | Required | Calculated | Result |
|---|---|---|---|
| manifest version | `30` | `30` | equal |
| aggregate digest | `28a4f4c2…a526` | `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526` | equal |
| fixture path | `infra/rp11-launch/verify/fixtures/cc1.v.baseline` | present, tracked | equal |
| fixture length | 5120 | 5120 | equal |
| fixture SHA-256 | `b77f92dc…905b` | `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` | equal |
| `expected.sha256` entries | four entries | the four of assignment §3.3; the file is `6e87a542…3625` | unchanged |
| `plan.is_executable` | `False` | `False` | equal |

Other values: the review-manifest JSON is `c9afaf7c…4b5c` and the concrete
plan is `f02b7acf…ec3d`. Both match the B1-R3 record. `toolchain.lock`
(`f9238073…84cf`), `build-root.manifest` (`f08ba9de…e76f`), `enter.py`
(`cf467c17…807a`), `provision.py` (`40496661…0300`), `build.sh`
(`7c8fc6da…38e0`) and `cc1check.py` (`16b78462…4b72`) all match the values in
the B1 and earlier records. The acceptance record is `6302570a…c89d`. **No
mismatch occurred, so no stop condition arose.**

## 5. Files created or modified

| File | Action | SHA-256 at stop |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md` | created | recorded in §7 |
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md` | created (this file) | not self-embeddable |

Only these two repository files were written, and no existing file was edited.
Both output paths were confirmed absent before writing. Two transient files
were written outside the repository, in the session scratchpad: `sums.txt` and
`cpuinfo.sample`.

## 6. Unresolved assumptions for reviewer or Product Owner disposition

* **U-1 — the `cc1.v` byte-equality contract carries a known host input.** The
  fixture contains
  `GGC heuristics: --param ggc-min-expand=100 --param ggc-min-heapsize=131072`.
  The GCC documentation says these defaults derive from physical memory and
  from `RLIMIT_DATA`, `RLIMIT_AS` and `RLIMIT_RSS`. The values here are their
  documented upper bounds, which a host with at least about 1 GiB of usable
  memory and no restrictive limits would normally reach. A host or session
  with lower memory or tighter rlimits would change this line and so produce
  a HARD STOP, which the accepted contract (R3, B1-R4) gives no route past.
  The earlier stopped run's `cdc0fe11…45f9` difference remains unexplained:
  this handback does not attribute it, and Claude must not. The draft keeps
  byte equality as the only PASS and records `MemTotal` and `ulimit` as
  context. Reviewer decision: is that enough, or should Peter decide in
  advance how a GGC-line-only difference would be handled? Any change to the
  contract would need a separate decision and is outside this draft.
* **U-2 — archive-signature verification.** `provision.py install` verifies
  package digests against the lock but does not check `InRelease`. Only
  `resolve` runs `gpgv`. To honour "signed snapshot", the draft adds `resolve`
  into a separate fresh index directory and requires its output to be
  byte-equal to the lock's 62 package lines. This adds a dependency on the
  host's `gpgv` and keyring, and assumes that the lock's package lines are
  exactly `resolve`'s output. The lock header says its values were "recorded";
  this draft did not verify that they came from `resolve`. If they did not,
  the step would stop the run. Reviewer: confirm, amend or drop.
* **U-3 — no HA-2 reference feature list.** No accepted record holds CPU flags
  for the reference build (see B1-R1). HA-2 can therefore qualify only on a
  different model name.
* **U-4 — HA-3 by version only.** `enter.py` hard-codes `/usr/bin/bwrap`. A
  different bubblewrap version is the only HA-3 variation possible without a
  source change. Does a version-only difference satisfy LD-8's "different
  entry mechanism"? The draft counts it, but the reviewer should rule. On the
  intended target, HA-1 is expected to differ; that is not assumed.
* **U-5 — controlled-checkout transport.** The canonical procedure rsyncs the
  working tree into `oracle-test:/opt/freedom-blades/platform`, a shared,
  non-fresh path. The draft instead uses `git archive` of the verified commit
  (tracked files only), one single-file `rsync` into a fresh `/tmp` directory,
  remote digest re-verification and extraction. The reviewer should confirm
  three things: that this transport is acceptable; that the secrets guard
  admits the command (it names no secret pattern); and that no tracked file
  is secret-bearing. Claude's own check of that last point was refused by the
  guard and not retried (§3).
* **U-6 — evidence retention.** All run evidence stays in `/tmp` on
  `oracle-test` pending review. Reboot is forbidden, but `/tmp` may still be
  volatile. The draft authorizes no evidence bundle in the repository beyond
  the handback. Should a bounded bundle (for example, `cc1.v`, the regenerated
  manifest and the logs) be retained elsewhere?
* **U-7 — identifiers.** The execution work ID `C-P5.0-R5-RP11-FRESH-R5` and
  the handback filename are placeholders for Peter to confirm.
* **U-8 — the banner and current-state documents.** On acceptance, someone
  must update the disposable-test-server banner, the Handover, status and
  §20. The draft gives the executor no authority to edit them, so the
  maintainer or a separately assigned agent records that.
* **U-9 — tree movement during preparation.** At session start the reported
  status was `HEAD 83e0c77` with many modified files. By the time digests were
  calculated, `HEAD` was `9cad3de` and the tree was clean apart from the
  prompt. Every controlling value matched, so the change is only noted. The
  draft binds digests, not the commit.

## 7. Documentation checks and final state

Checks on the two output documents:

* relative-link resolution: run with a read-only Python check; result below;
* whitespace: `git diff --no-index --check /dev/null <file>`, because both
  files are untracked and plain `git diff --check` would not inspect them;
  result below; and
* final `git status --short`: below.

Results:

```text
assignment: relative links 3, missing []
handback:   relative links 2, missing []
git diff --no-index --check /dev/null <assignment>  -> no output, exit 1
git diff --no-index --check /dev/null <handback>    -> no output, exit 1
```

The checker printed no whitespace finding for either file. Exit status 1 comes
from `--no-index` reporting that a file differs from `/dev/null`; it is not a
whitespace finding.

The assignment's SHA-256 at stop is
`37e2673e923c8d11db2c471850be55ab22a35381db03e20f26880a58a62748d5`.
This handback was last edited after its checks, which add only this results
text, so it cannot carry its own digest.

Final `git status --short`:

```text
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md
```

The prompt file was already untracked before this task. The other two entries
are this task's outputs, and nothing else changed.

## 8. Boundary confirmation

* No host inspection beyond repository files.
* No remote access, `oracle-test`, SSH, rsync or network use.
* No provisioning, build or test run.
* No launcher or verifier run: no `provision.py`, `enter.py`, `cc1check.py`,
  IC-1, B1 or R-5.
* No `sudo`, package or host-state change.
* No access to retained `/tmp` run evidence.
* No staging, commit or push.
* No executor named, appointed, reviewed or accepted.

RP-11 remains unwired and unmet; `plan.is_executable=False`; PO-9 and PO-14
remain open; R-5 remains stopped, Blocking and unaccepted; and Package 5.0 is
not ready. Claude has stopped.
