# R1 remediation handback — fresh R-5 independent-rebuild assignment

Work ID: `C-P5.0-R5-RP11-FRESH-A1-R1`

Date: 2026-10-02

Drafting-remediation assignee: Claude, appointed by Peter Duscha, who accepted
this work ID in this session

Controlling prompt:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-claude-prompt.md)
(SHA-256 `2496f14366578213bc3b375410a7f4d7d2c0055bc2ad29a72c51b505f523a29a`)

Corrected output:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)

Historical first-draft record, not amended:
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md)

Status: **Corrected assignment returned for independent Codex re-review. It is
not accepted, not assigned and not executable. No finding is claimed closed.
Claude has stopped.** Claude implemented I-7/I-7-R1 and remains ineligible to
execute R-5, to be its assignee, to select one, or to review or accept the
assignment. R-5 remains stopped, Blocking, unaccepted and unauthorized.

---

## 1. Result

All five findings are remediated in the assignment text, and no stop condition
of R1 prompt §8 arose:

* every mandatory document was read completely (§6);
* every controlling digest matched (§9);
* the documented secret-excluding synchronization was adapted to the fresh
  destination by changing the destination only, and the repository secrets
  guard admits it (§4);
* no implementation or test change was needed;
* no execution-safety or PASS-eligibility ambiguity remains open (§5); and
* no other agent changed either authorized path during the task.

Only the two authorized files were written in the repository.

## 2. Finding dispositions

| Finding | Severity | Disposition (proposed; for Codex's re-review) | Where |
|---|---|---|---|
| `FRESH-A1-R1-1` — commands can mask a failed build, verifier or test behind `echo` | Blocking | **Remediated in text.** Every executable command was audited, not only the three cited. All commands now run inside blocks in which each status is captured immediately, printed with a step label, and on nonzero becomes the block's exit status before any later check. No block has a pipe, a `;`-chained check, `set -e` or a trailing `echo`. Where a block displays evidence after a checked command, the checked status is captured first and governs. pytest's exit-0-with-skips case is closed by a mechanical count check (status 32) | assignment §6.0; every step; §3 below |
| `FRESH-A1-R1-2` — expected-absence checks return nonzero under an all-nonzero hard stop | Blocking | **Remediated in text.** Each absence or observation is now an explicit conditional that returns 0 only for the accepted condition and a distinct nonzero status for the violation (10–14), with its accepted output stated. No unmatched glob through `ls` and no pipeline is used | assignment §6.0 status table; S2.10, S2.11, S2.25, S7.3, S7.4; §3 below |
| `FRESH-A1-R1-3` — `git archive` transport has no accepted fail-closed secrets boundary | Blocking | **Remediated in text.** The archive transport, its repository-host `/tmp` export directory, digests, paths and handback items are removed. Step 4b is the documented `rsync` with only the destination changed, followed by local and remote exact-digest and exact launcher-tree verification. U-5 is removed | assignment §6 step 4, §7, §10, §12; §4 below |
| `FRESH-A1-R1-4` — HA-3 version-only difference left unresolved | Important | **Remediated in text.** Normative rules: HA-1 only by kernel release; HA-2 only by CPU model name; HA-3 only by a materially different mechanism or configuration accepted in advance by Peter, never by a bubblewrap version alone. HA-3 therefore cannot qualify in this run, and the run must rely on a measured HA-1 or HA-2 difference. Step 3 applies the rules mechanically and exits 20 (INVALID RUN) before any directory is created. U-4 is removed | assignment §4.2, §4.3, §6 step 3, §8.2; §5 below |
| `FRESH-A1-R1-5` — not all mandatory sources were read completely | Important | **Remediated for this task.** Every source that the R1 prompt §2 makes mandatory was read completely, from first byte to last, with the Read tool or `cat`, before editing. No search, excerpt or sizing substituted for a read. The list is §6. The preparation handback's disclosed shortfall stays on record there unchanged | §6 below |

## 3. Exit-status and absence-check corrections: before and after

"Before" quotes the first draft (SHA-256 `37e2673e…48d5`) exactly. "After"
names the assignment's block labels; the block text there is exact.

### 3.1 The four forms the prompt names

**Same-invocation build** — before:

```bash
cd /tmp/<RUN>-checkout && PYTHONDONTWRITEBYTECODE=1 <PY> infra/rp11-launch/buildroot/enter.py build --root /tmp/<RUN>-root --work /tmp/<RUN>-work --variant r2 --manifest-out /tmp/<RUN>-evidence/regenerated.manifest > /tmp/<RUN>-evidence/build.stdout 2> /tmp/<RUN>-evidence/build.stderr; echo "exit=$?"
```

After (S6.1–S6.5, inside the step 6/7 block):

```bash
  cd /tmp/<RUN>-checkout
  status=$?
  printf 'S6.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 <PY> -B infra/rp11-launch/buildroot/enter.py build --root /tmp/<RUN>-root --work /tmp/<RUN>-work --variant r2 --manifest-out /tmp/<RUN>-evidence/regenerated.manifest > /tmp/<RUN>-evidence/build.stdout 2> /tmp/<RUN>-evidence/build.stderr
  build_status=$?
  printf 'S6.2 enter-build exit=%s\n' "$build_status"
  cat /tmp/<RUN>-evidence/build.stdout /tmp/<RUN>-evidence/build.stderr
  display_status=$?
  printf 'S6.3 display exit=%s\n' "$display_status"
  if [ "$build_status" -ne 0 ]; then exit "$build_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
```

followed by S6.4 and S6.5, which require the exact gate line and `exit 0` in
`build.stdout` with `grep -Fxq`.

**`cc1check.py`** — before:

```bash
cd /tmp/<RUN>-checkout && PYTHONDONTWRITEBYTECODE=1 <PY> infra/rp11-launch/verify/cc1check.py infra/rp11-launch/verify/fixtures/cc1.v.baseline /tmp/<RUN>-work/co-r2/build-out/cc1.v > /tmp/<RUN>-evidence/cc1check.out; echo "exit=$?"
```

After (S9.2–S9.4): `cd` is a checked command; `cc1check.py` writes stdout and
stderr to `cc1check.out` and `cc1check.err`; its status is captured as
`check_status` and printed; both files are displayed; `check_status` governs
the block's exit, and the display status is checked only afterwards. Exit 0 is
`PASS`, 1 `HARD_STOP`, 2 unreadable input.

**pytest** — before:

```bash
cd /tmp/<RUN>-checkout && RP11_LAUNCH_BUILD_ROOT=/tmp/<RUN>-root PYTHONDONTWRITEBYTECODE=1 <PY> -m pytest -q -rs -p no:cacheprovider --basetemp=/tmp/<RUN>-pytest tests/test_rp11_launch_toolchain.py > /tmp/<RUN>-evidence/pytest.out 2>&1; echo "exit=$?"
```

After (S10.1–S10.4): `cd` checked; pytest runs under `env -u
TEST_DATABASE_URL` with `--junitxml=/tmp/<RUN>-evidence/pytest.junit.xml`;
its status is captured first and governs; `pytest.out` is displayed; then
S10.4 parses the JUnit counts and exits 32 unless they are exactly
`tests=12 failures=0 errors=0 skipped=0`. pytest itself exits 0 when tests
skip, so this check closes the remaining masking path.

**`ld.so.preload` absence** — before:

```bash
test ! -e /tmp/<RUN>-root/etc/ld.so.preload; echo "preload_absent=$?"
```

After (S7.3):

```bash
  preload=/tmp/<RUN>-root/etc/ld.so.preload
  if [ -e "$preload" ] || [ -L "$preload" ]; then
    printf 'ld_so_preload=present\n'
    status=11
  else
    printf 'ld_so_preload=absent\n'
    status=0
  fi
  printf 'S7.3 ld-so-preload-absent exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
```

Accepted: `ld_so_preload=absent`, exit 0. A dangling link is also a
violation.

### 3.2 The other absence checks the prompt names

| Before (exact) | After | Accepted output and status | Violation |
|---|---|---|---|
| `cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns   # record "absent" if the file does not exist` | S2.11: `if [ -e … ]` then `read -r` (status captured) and print `apparmor_restrict_unprivileged_userns=<value>`, else print `…=absent` with status 0 | the exact value or the literal `absent`; exit 0 (recorded, not a gate) | read failure: the `read` status |
| `ls -d /tmp/<RUN>*   # must report that no such path exists` | S2.25: `<PY> -I -B` lists `/tmp` with `os.listdir` and selects names starting with `<RUN>` | `run_prefix_entries=none`; exit 0 | 10 |
| `find /tmp/<RUN>-root/tmp /tmp/<RUN>-root/var/tmp -mindepth 1   # must print nothing` | S7.4: `<PY> -I -B` checks each is a real directory and lists it | `… entries=none` for both; exit 0 | 12 non-empty; 13 missing, link or not a directory |

### 3.3 The rest of the audit

| Before (draft line, exact or as written) | Defect | After |
|---|---|---|
| Step 1: the unwrapped command list (`git rev-parse HEAD` … the review-manifest program), statuses recorded by prose only | no stated status handling; `grep -c` and the manifest program print values that only a manual comparison judged | S1.1–S1.9 block; mechanical conditions 23 (lock facts), 24 (in-memory manifest), 25–27 (digests, count, launcher tree), 28 (repository state) |
| `uname -srvm; cat /proc/version` | `;` masks the first status | S2.2, S2.3 |
| `/usr/bin/bwrap --version; stat -L -c '%a %U:%G %s %n' /usr/bin/bwrap; sha256sum /usr/bin/bwrap` | `;` masks | S2.6–S2.8 |
| `cat /proc/sys/user/max_user_namespaces` | value unjudged | S2.10a (read status) and S2.10b (positive integer, else 14) |
| `id; hostname; cat /etc/os-release` | `;` masks | S2.12–S2.14 |
| `grep MemTotal /proc/meminfo; ulimit -Sa; ulimit -Ha; df -P /tmp` | `;` masks | S2.15–S2.18 |
| `<PY> -VV; <PY> -c 'import pytest; print(pytest.__version__)'` | `;` masks | S2.19, S2.20 |
| `command -v zstd gpgv; zstd --version; gpgv --version \| head -n 1` | `;` masks; pipe takes `head`'s status | S2.21–S2.23 (no pipe; `rsync` and `lscpu` added to the presence check) |
| `date -u …`, `lscpu`, the `awk` filter, `dpkg-query …`, `sha256sum …keyring.gpg` (single commands) | no stated status handling | S2.1, S2.4, S2.5, S2.9, S2.24 |
| step 3 prose comparison | manual | S3.1, mechanical; 20 INVALID, 21 model name missing or not unique |
| step 4: `mkdir -m 0700 /tmp/<RUN>-export`, `git … archive …`, `sha256sum …checkout.tar`, `stat …`, `mkdir -m 0700 …`, `stat -c '%a %U:%G %n' /tmp/<RUN>-*`, `rsync -a …checkout.tar …`, `sha256sum …`, `tar -x …`, `cd … && sha256sum <every file in §3.2>`, `cd … && … '<the step-1 hashlib loop>' …` | archive transport (finding 3); unwrapped statuses | removed; replaced by S4a.1–S4a.2, the 4b sync command (its own invocation status), S4c.1–S4c.3, S4d.1–S4d.4 |
| step 5: `… resolve … > …/resolve.out`, `grep … > …`, `cmp …`, `… install …`, `ls -1 /tmp/<RUN>-cache \| wc -l; sha256sum /tmp/<RUN>-cache/*.deb > …/cache.sha256`, `… ldconfig …`, `stat …` | pipe takes `wc`'s status; `;` masks; count judged manually | S5.1–S5.8; S5.6 exact cache accounting, 29 |
| `cmp …regenerated.manifest …`, `sha256sum …regenerated.manifest` | no stated status handling | S7.1, S7.2 |
| step 8: `cd … && sha256sum -c …`, `cd … && … '<the step-1 hashlib loop>' …`, `cmp …listing …` | `&&` chains; manual comparison against `build.stdout` | S8.1–S8.4; S8.3 independent check, 30 digests, 31 missing `build.stdout` line |
| `stat -c '%s' …/cc1.v` | no stated status handling | S9.1 |
| step 11: `cd … && sha256sum <every file in §3.2>   # must still equal §3.2`, `sha256sum …/* …/*`, `stat … /tmp/<RUN>-*`, `du -s /tmp/<RUN>-*`, `date …; uname -srvm; awk …; /usr/bin/bwrap --version; sha256sum /usr/bin/bwrap` | `&&` chain; `;` masks four statuses | S11.1–S11.11 with explicit path lists |

## 4. Final synchronization command and its source

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
  /opt/freedom-blades/platform/ oracle-test:/tmp/<RUN>-checkout/
```

* **Source:** [`docs/operations/disposable-test-server.md`](../operations/disposable-test-server.md)
  §3.2, lines 80–91 (identical to §4 item 2, lines 144–155). A `diff` of the
  two, after substituting a sample `<RUN>` and masking the destination, is
  empty (§7). The only change is the destination, from
  `oracle-test:/opt/freedom-blades/platform/` to the fresh
  `oracle-test:/tmp/<RUN>-checkout/`.
* **Retained:** every flag, every exclusion, the single quoting and the order
  `--include='.env.example'` before `--exclude='.env*'`. No
  `--delete-excluded`, exclusions file, substitution, redirection or chained
  command.
* **Guard:** fed a sample-`<RUN>` payload of this command,
  `.claude/hooks/guard-secrets.py` returned 0 (admitted). It admits only one
  plain `rsync`, so the command is the one exception to the block convention
  and its status is the invocation's own (assignment §6.0, step 4b).
* **After the transfer:** S4c re-checks the repository state and digests
  locally. S4d re-verifies all 28 controlling files remotely by `sha256sum
  --strict -c` and by the independent Python check, and requires the remote
  `infra/rp11-launch/` file set to be exactly the 22 pinned files (status 27
  otherwise). This last check exists because `enter.py`'s `prepare_checkout`
  copies that whole directory into the build checkout.
* **Precedent:** the accepted original R-5 assignment §4 authorized exactly
  this canonical procedure for the earlier run.

**Disclosed transfer scope, for the reviewer.** The documented procedure sends
the working tree, including `.git`, untracked files and ignored files its list
does not exclude. On this host, existence-only checks found `venv/`,
`venv-web` and `docs/screenshots/` present. `.gitignore` describes
`docs/screenshots/` as maintainer browser evidence that may show world, folder
or Actor content. No `fvtt-Actor-*.json` or `*.log` file was found. Every
accepted synchronization to `oracle-test` has had this scope. Narrowing it
would be a new policy decision, which R1 prompt §3.3 forbids me to invent. The
assignment therefore keeps the accepted list, discloses the scope, and forbids
the executor to open, list, read, copy or cite that content (step 4b, §7.2).
Whether to add exclusions in future is a question for Peter; it is not a
blocker under the accepted policy.

## 5. Normative HA-1 … HA-3 qualification rules

As written in assignment §4.2:

* **HA-1** qualifies only if `os.uname().release` (= `uname -r`) differs
  from `6.8.0-139-generic`.
* **HA-2** qualifies only if every processor reports one and the same `model
  name` and it is neither `AMD EPYC-Milan Processor` nor `AMD EPYC-Milan`.
  Flags, microcode, stepping or topology differences never qualify. A missing
  or non-unique model name exits 21 (HARD STOP).
* **HA-3** qualifies only through a materially different entry mechanism or
  configuration accepted in advance by Peter. A bubblewrap version-only
  difference does not qualify. No such configuration exists, and none is
  added, so **HA-3 cannot qualify in this run.**
* If neither HA-1 nor HA-2 qualifies, step 3 exits 20: **INVALID RUN**, before
  any directory is created or anything is provisioned.

For the record: under these rules, Gemini's earlier observation of bubblewrap
0.11.1 against 0.9.0 would not have qualified on its own. Its HA-1 and HA-2
observations were separate. This changes no earlier record.

## 6. Mandatory documents read completely

Each was read from first byte to last before editing:

1. `.agents/AGENTS.md`;
2. the original preparation prompt;
3. the proposed assignment (first draft, `37e2673e…48d5`) and the preparation
   handback;
4. `docs/review/Handover information`;
5. `docs/project-management/status.md`;
6. `docs/operations/disposable-test-server.md`;
7. D2/D2-R2: the D2 proposal (all 2,258 lines), the D2 handback, the D2-R1
   handback, the D2-R2 handback, the D2-R1 review and decisions record
   (LD-7, LD-8), and the D2-R2 acceptance (LD-9);
8. the I-7 prompt and handback, Codex's I-7 review, the I-7-R1 prompt and
   handback, Codex's I-7-R1 re-review, and the I-7-R1 acceptance;
9. the original R-5 assignment and its preserved reviewed proposal, the
   Antigravity review, the R-5 acceptance, the stopped R-5 handback, the
   bubblewrap-stop review and the bubblewrap-install authority;
10. the R2 prompt and handback; the R3 prompt, handback and acceptance; the R4
    prompt and handback; and the R4-R1 prompt, handback and acceptance and
    reference-reproduction decision. No separate review records for R2 or R4
    exist in the repository; their reviews are summarized in the next
    prompts, which were read;
11. the B1, B1-R1, B1-R2, B1-R3 and B1-R4 prompts and handbacks, and the B1-R4
    acceptance. No other B1 review record exists in the repository;
12. `infra/rp11-launch/buildroot/provision.py`;
13. `infra/rp11-launch/buildroot/enter.py`;
14. `infra/rp11-launch/verify/cc1check.py`;
15. `tests/test_rp11_launch_toolchain.py`; and
16. the R1 remediation prompt.

From `docs/implementation-plan.md`: the reading map and §0, §13, §16, §17 and
§20, each completely.

Also read completely, beyond the mandatory list, because the corrections rely
on them: `infra/rp11-launch/build.sh`; the non-`package=` lines of
`toolchain.lock`; `expected.sha256`; `.claude/hooks/guard-secrets.py`; and the
first 40 lines of `.gitignore` (the whole of its relevant part).

**I confirm the mandatory complete reading was finished before the first edit.**

## 7. Read-only commands actually run

All on the repository host, in `/opt/freedom-blades/platform`. No command
wrote to the repository except the two authorized files, written with the
Write and Edit tools.

* Reading: the Read tool and `cat` on the documents of §6; `wc -l` on the
  required documents; `ls docs/review | grep … | while read …; wc -l`;
  `grep -nE '^#{1,2} '` on the implementation plan (section offsets only, not
  a substitute for reading); `grep -rl 'FRESH-A1-R1' docs` and a `grep -lE`
  for B1/R2/R4 finding IDs in review files (to find review records; none
  beyond those read); `ls docs/review | grep -E '2026-10-0'`.
* State: `git status --short` (start and end); `git rev-parse HEAD`;
  `git ls-files infra/rp11-launch`; `git status --short --ignored -- infra
  tests tools`; `git ls-files | grep -E …` for root config and `__init__.py`
  names; `ls -a` of the root; `find infra/rp11-launch -name __pycache__ -prune
  -o -type f -print | LC_ALL=C sort`.
* Lock: `grep -v '^package='`; `grep '^package=' … | sort -c` and
  `| LC_ALL=C sort -c`; `grep -c '^package='` (62).
* Digests: `sha256sum` of the first draft, the R1 prompt, the preparation
  handback and the scratch copy; a Python `hashlib` check of all 28 §3.2
  rows (lengths and digests); a Python generation of Appendices A and B from
  the table; a Python cross-check that the new table, Appendix A, Appendix B
  and the tree agree, that §3.1 and §3.3 are byte-identical to the first
  draft, and that removed forms are gone.
* Transfer scope, existence only, no content read: `[ -e ]` tests for
  `venv`, `venv-web`, `node_modules`, `docs/screenshots`, `logs`,
  `.pytest_cache`; `find . -path ./.git -prune -o -name 'fvtt-Actor-*.json'
  -print` and the same for `*.log` (both empty); `du -sh .git`.
* Syntax analysis only: a Python script that extracted the 14 `bash` code
  blocks, substituted sample values (`<RUN>` =
  `p5-r5-fresh-20261003T000000Z-0123abcd`, `<PY>`, the appendices and the
  S1.6 program), ran `bash -n` on each invocation and on each inner script,
  and `ast.parse` on each of the 14 embedded Python programs. All passed; no
  placeholder remained. **No block, program or command of the assignment was
  executed.** The programs' expected outputs (for example
  `launcher_tree files 22 dirs 5`) are derived from the tree listing above,
  not from running them.
* Guard: `python3 .claude/hooks/guard-secrets.py < <payload>` on scratch
  payload files holding the sample sync command (exit 0); then `diff` of the
  sample command against operations-document lines 80–91, and of lines 80–91
  against lines 144–155 (both empty, exit 0).
* Documentation checks: §11.
* One `cp` of the first draft into the session scratchpad, to keep its bytes
  for the before/after record.

Scratch files, outside the repository:
`…/scratchpad/assignment-before.md`, `appendices.txt`, `syntax/*.sh`,
`payload-fresh.json`, `payload-documented.json`.

## 8. Files modified or created

| File | Action | SHA-256 |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md` | rewritten in place (authorized) | before `37e2673e923c8d11db2c471850be55ab22a35381db03e20f26880a58a62748d5`; after `f4f4e1a3e48d6968215596432af6a08218f91dbf9b60c458fd50f969cfa89ff7` (1,464 lines) |
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md` | created (this file) | not self-embeddable |

The preparation handback was not amended (still
`0bb3a67872e058254fb8736d03d3248e766940c739741f5462a40f8b3db86b0b`). No other
repository file was touched.

## 9. Accepted input values unchanged

* §3.2's 28 rows (path, length, digest) are byte-identical to the first
  draft's, and every one still matches the tree at `HEAD`
  `9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa`: 0 mismatches.
* §3.1 (manifest version 30, aggregate `28a4f4c2…a526`, baseline path, 5,120
  bytes, `b77f92dc…905b`, the four normative outputs, diagnostic status,
  `B1-R3-1`/`B1-R3-2` closed, R-5 stopped, RP-11 unwired,
  `plan.is_executable=False`, PO-9/PO-14 open, Package 5.0 not ready) and
  §3.3 (the four `expected.sha256` lines) are byte-identical to the first
  draft.
* `toolchain.lock` still has 62 `package=` lines, snapshot `20261001T000000Z`
  and `build_root_manifest_sha256` `f08ba9de…e76f`.
* No fixture, manifest, concrete plan, launcher source, test, lock,
  build-root manifest or normative digest was changed.

Preserved boundaries: Claude's ineligibility; the TBD executor named only by
Peter; wholly fresh roots, caches, checkouts, work paths and evidence; no
reuse of earlier R-5, B1, I-7 or I-7-R1 artifacts; manifest 30 and all
accepted digests; four normative outputs versus diagnostic `cc1.v.baseline`;
the same-invocation R-1/R-2 gate; exact bytes as the only `cc1check.py` PASS;
12 tests and zero skips; one run, no retry, no remediation; no privilege or
prerequisite repair; HARD STOP over INVALID RUN over PASS; the executor
handback and immediate stop; and Codex review plus Peter's decision after the
run.

## 10. Former U-1 … U-9

| Item | Disposition |
|---|---|
| U-1 | Retained as diagnostic context only (assignment §4.4). An exact `cc1.v` mismatch is a HARD STOP; no GGC-only exception |
| U-2 | Confirmed against `provision.py` as written: `gpgv` runs with `check=True`, a `Packages.xz` mismatch exits, output is one `package=` line per package in name order, matching the lock's format and its byte order (checked with `LC_ALL=C sort -c`). The gate is retained, fail-closed, and stated normatively (step 5) |
| U-3 | Made normative: HA-2 qualifies only on a different model name (§4.2) |
| U-4 | Removed: version-only does not qualify; HA-3 cannot qualify in this run |
| U-5 | Removed: archive transport replaced by the documented `rsync` (§4 above) |
| U-6 | Converted to the explicit evidence-retention rule of assignment §10.1: the handback embeds every block transcript and verdict-relevant evidence file; `/tmp` evidence is retained, unchanged, as a supplement only |
| U-7 | Peter has not decided the identifiers, so they stay clearly marked **pending acceptance** in the header, §5, §10 and §12 |
| U-8 | Kept outside the executor's authority (§7.1, §7.2) |
| U-9 | Kept as historical drafting context in the unamended preparation handback; the assignment binds exact bytes (§3.2, §12) |

## 11. Documentation checks and final state

Checks on the two authorized outputs. Relative links were resolved with a
read-only Python `pathlib` check. Whitespace was checked with
`git diff --no-index --check /dev/null <file>`, because both files are
untracked and plain `git diff --check` would not inspect them; the same
Python check counted trailing-whitespace lines and tabs.

```text
assignment: relative links 6, missing [], trailing-whitespace lines 0, tabs 0
handback:   relative links 4, missing [], trailing-whitespace lines 0, tabs 0
git diff --no-index --check /dev/null <assignment>  -> no output, exit 1
git diff --no-index --check /dev/null <handback>    -> no output, exit 1
```

The checker printed no whitespace finding for either file. Exit 1 comes from
`--no-index` reporting that the file differs from `/dev/null`; it is not a
whitespace finding.

The assignment's final SHA-256 is
`f4f4e1a3e48d6968215596432af6a08218f91dbf9b60c458fd50f969cfa89ff7`.
This handback was edited after its checks only to record these results, so it
cannot carry its own digest.

Final `git status --short`:

```text
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md
```

At the start, the four entries other than this handback were already present
and untracked. The only new entry is this handback, and the assignment is the
only file modified. All unrelated state is preserved.

## 12. Boundary confirmation

* No host inspection beyond repository files and the existence-only checks
  of §7.
* No remote access: no `oracle-test`, SSH, `rsync` or network use.
* No provisioning, build, test or verifier run. No `provision.py`,
  `enter.py`, `cc1check.py`, IC-1, B1 or R-5, and no proposed R-5 command,
  even locally. The guard hook ran once on a text payload; the sync it
  describes was not run.
* No access to retained `/tmp` run evidence.
* No `sudo`, package, service, database or host-configuration change.
* No governance or current-state document edited. No implementation, test,
  fixture, manifest or generated artifact changed.
* No staging, commit or push.
* No executor selected, appointed, reviewed or accepted.

**R-5 remains stopped, Blocking, unaccepted and unauthorized.** RP-11 remains
unwired and unmet; `plan.is_executable=False`; PO-9 and PO-14 remain open;
Package 5.0 is not ready. Next: Codex's independent re-review of the corrected
assignment, then Peter Duscha's decision. Claude has stopped.
