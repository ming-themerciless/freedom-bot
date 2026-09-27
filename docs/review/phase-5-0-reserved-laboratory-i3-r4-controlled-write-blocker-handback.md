# Claude operational handback — I3 controlled-write verification refused before the first write — 2026-09-20

Authorization: **C-P5.0-LAB-I3-R4**. Claude acted as the implementing operator
for the bounded operational I3 verification on `oracle-test`.

> ## ERRATUM — evidence precision, correction C-P5.0-LAB-I3-R4-E1, 2026-09-20
>
> **This erratum corrects the wording of this handback. It corrects no
> result.** The C-P5.0-LAB-I3-R4 outcome is unchanged and stands as Peter
> Duscha accepted it: the root invocation refused admission with
> `target-mismatch` at exit `4`, **I3 remains unconfirmed and unperformed**,
> and the `ubuntu` invocation was not run. No host action and no retry is
> authorized by this correction, and nothing here reopens, closes or advances
> anything.
>
> The original text used broad phrases — "nothing was written on the host",
> "the host is exactly as it was", "nothing was created", "the host was not
> mutated". Those phrases are imprecise. What is true, and what this handback
> now says everywhere, is:
>
> 1. **The I3 verifier performed no controlled write and created no verifier
>    object.** It refused in admission, before the first `openat`, `mkdirat`
>    and `linkat`, and before any context was entered. This is the claim the
>    evidence supports, and it is the claim that matters for I3.
> 2. **Synchronization did mutate the target.** The authorized §3.2 `rsync`
>    ran with `--delete` and updated the remote repository worktree at
>    `/opt/freedom-blades/platform` on `oracle-test` (§3). That is an
>    authorized operator mutation of a repository worktree, not a verifier
>    write, and it is outside canonical `R` and the four publication
>    directories.
> 3. **The operator's output redirection created two files.** The shell-level
>    evidence-capture wrapper around the reviewed verifier argv redirected
>    stdout and stderr, creating `/tmp/fb-i3-root.out` and
>    `/tmp/fb-i3-root.err` on the target (§8). They are operator evidence
>    artifacts, owned `ubuntu:ubuntu`, outside canonical `R` and outside the
>    four publication directories. **They are not verifier residue**, and
>    their presence is not a residue finding.
> 4. **The correct general phrasing is "no verifier-controlled mutation
>    occurred."** Every broad claim in this document has been replaced with
>    that wording, with the synchronization and the two `/tmp` files disclosed
>    alongside it rather than implicitly excluded by it.
> 5. **"No wrapper" was wrong** as originally written in §6. The reviewed
>    verifier **argv** was exactly the authorized one — no added flags, no ad
>    hoc script, no substituted probe, no re-implementation. It was invoked
>    through an ordinary shell-level evidence-capture wrapper (`ssh`, `cd`,
>    `date`, redirection, exit-status capture, `cat`). §6 now records the
>    complete executed shell command verbatim and distinguishes the two
>    levels.
>
> What did **not** change: the refusal, the exit status, the safe output, the
> prerequisite observations, the tree identity, the digest, the per-context
> evidence (none exists), the resulting state, or the §10 open decision. The
> two `/tmp` files are **not** deleted by this correction, and no inspection
> of `oracle-test` was performed to produce it — it is a repository
> documentation correction written from the recorded execution evidence.
>
> Correction handback:
> [`phase-5-0-reserved-laboratory-i3-r4-e1-evidence-precision-correction-handback.md`](phase-5-0-reserved-laboratory-i3-r4-e1-evidence-precision-correction-handback.md).

---

**Result: I3 is unconfirmed. The root invocation refused admission with
`target-mismatch` and exit status `4`. No verifier-controlled mutation
occurred: the verifier performed no controlled write and created no verifier
object. The `ubuntu` invocation was not run, because the authorization permits
it only after the root invocation returns `verified` with exit status `0`.**

The pass's two disclosed effects on the target are the authorized §3.2
synchronization, which updated the remote repository worktree (§3), and the
operator's two output-capture files under `/tmp` (§8). Neither is a verifier
object, and both lie outside canonical `R` and the four publication
directories.

This is a stop condition named in the authorization — *"refuses admission or
reports a target, account, group, policy, mount, ownership, mode, name or
source mismatch"*. Nothing was retried, repaired, provisioned, removed or
broadened. The blocker requires a maintainer decision; it is not an operator
fix, for the reason given in §6.

---

## 1. The exact blocker

The verifier's admission step 2 (r6 §7.4.2) compares the three values
`os.uname()` reports against the approved target's facts:

```python
host = tuple(self.probe.host())          # (nodename, release, machine)
if host != (
    APPROVED_TARGET_FACTS.host,          # "oracle-test"
    APPROVED_TARGET_FACTS.active_kernel, # "7.0.0-31-generic"
    APPROVED_TARGET_FACTS.architecture,  # "x86_64"
):
    raise _Refusal(TARGET_MISMATCH)
```

`tools/phase_5_0_evidence/execution/i3_verifier.py:1101-1114`;
`ProcHostProbe.host()` at `:504-506`.

Observed on the target, read-only:

| Value | `os.uname()` on the target | `APPROVED_TARGET_FACTS` | Match |
|---|---|---|---|
| nodename / `host` | `Test` | `oracle-test` | **no** |
| release / `active_kernel` | `7.0.0-31-generic` | `7.0.0-31-generic` | yes |
| machine / `architecture` | `x86_64` | `x86_64` | yes |

`/etc/hostname` and `hostnamectl --static` both report `Test`.
`/etc/os-release` reports `Ubuntu 26.04.1 LTS`, matching the recorded facts.

**`oracle-test` is the SSH alias defined in `~/.ssh/config` (runbook §2), not
the target's kernel nodename.** `APPROVED_TARGET_FACTS.host` carries the alias;
admission compares it against the nodename. The two were never equal, so this
refusal is reproducible and is not caused by any state this pass created.

The kernel release and the architecture — the two facts that describe the
rebuilt baseline the target was approved on — match exactly. The single
divergence is the name.

## 2. Why no earlier pass met this

`execution/i3_verifier.py` is the **only** module in
`tools/phase_5_0_evidence/` that reads `uname` at all; a repository-wide search
for `uname` and `nodename` outside it returns nothing. The 2026-09-18
provisioning run and the read-only I12/V6 verification made no such comparison,
so neither could have detected the divergence. It became reachable when r6
§7.4.2 step 2 was added, and this is its first execution.

## 3. Synchronization

The exact accepted inline §3.2 command was used, with its single-quoted
exclusions, no `--exclude-from`, and no alteration to the exclusion set. The
secrets guard admitted it; no guard refusal occurred at any point in this pass.

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

It completed successfully: 52 paths transferred, `sent 372,553 bytes`,
`received 33,273 bytes`, `total size is 73,348,693`.
[*Correction note, C-P5.0-LAB-I3-R4-E1: the "52 paths" figure is not
reproducible from the recorded transfer output, which lists 54 entries — 45
files and 9 directories. The three byte figures reproduce exactly. The figure
is left as accepted rather than rewritten, and the discrepancy is flagged for
the reviewer; it bears on no result.*] No secret-type file
appears in the transfer list. No secret file was read, printed, transferred or
modified in this pass.

**This synchronization mutated the target** (erratum, item 2). It ran with
`--delete` and updated the remote **repository worktree** at
`/opt/freedom-blades/platform` on `oracle-test` — documentation, tests,
`tools/phase_5_0_evidence/` sources and Git metadata under `.git/`. That is
the authorized operator preparation this pass permits, and it is disclosed
here rather than covered by any broad "nothing was written" claim. It is not a
verifier write: it touched no canonical `R` and none of the four publication
directories, which remained absent or unchanged as §5 records.

A UTC timestamp was not captured for the synchronization itself; it was
performed in the same session shortly before the 13:14Z invocation. The
inspection and invocation timestamps below are exact.

## 4. Source identity and the accepted tree

| Property | Value |
|---|---|
| Branch / `HEAD` | `docs/platform-plan` / `2fb1d6f` |
| Working tree | 69 modified or untracked paths, unchanged by this pass |
| `MANIFEST_VERSION` on the target | **16** |

Artifact SHA-256, identical on both hosts and equal to the accepted values:

| Artifact | SHA-256 |
|---|---|
| `…-concrete-plan.md` | `122f0b9a4eddebfa5a998a376adbc51da3ec9d7fb066a1c8c3709b00b2d31720` |
| `…-review-manifest.json` | `65ef078d99273c52f64cd707021e9479d43c80bfcc58f419070c3e08f8f25239` |

**Reproduced review-input digest:
`be9e110f9cc8828ba79aaeec7342fd23182dad54eb261852d68654bf8332762b`** — equal to
the accepted C-P5.0-LAB-I3-R3 digest. It was reproduced in the repository
workspace by the deterministic non-executing generation path, whose output was
byte-identical to both checked-in artifacts.

The digest was deliberately **not** reproduced by invoking the harness on the
target: the authorization does not permit an evidence-harness invocation there,
and a dry run is still one. Target identity was established instead by hashing
the file set the digest covers. All 47 `COVERED_SOURCES` files plus both
generated artifacts and runner contract r6 were hashed on both hosts; the
aggregate SHA-256 over that sorted list is
`9806b548ce86b55d0a3e3574245a4b121f161f4ba5b61da0c209c8fa90c46349` on both.
The synchronized tree is therefore byte-for-byte the accepted
manifest-version-16 tree that reproduces the digest.

Spot digests on the target:

| File | SHA-256 |
|---|---|
| `execution/i3_verifier.py` | `e7b6b869c7fdbca3b6a5c56c5f957bbd89807cdc0b8d9bc90b6938fd143ba35c` |
| `execution/i3_verifier_cli.py` | `9421331ddb8155e86c78a2995f8bc6f81c9945b7ea110727d6252e149f8fc3bd` |

**The digest is review input. It is not approval and is never authority for
`--execute`.**

## 5. Read-only prerequisite observations, before the first invocation

All taken on `oracle-test` at 2026-09-20T13:1xZ, before any invocation. Every
reviewed prerequisite was found exactly as recorded on 2026-09-18.

| Item | Expected | Observed | Result |
|---|---|---|---|
| V1 | group `freedomlab` | `freedomlab:x:986:ubuntu` | matches |
| V2 | `ubuntu` in `freedomlab` | `…,102(lxd),986(freedomlab)`; the five prior groups retained | matches |
| V3 | `/etc/tmpfiles.d/freedom-blades-laboratory.conf` `root:root 0644` | `root:root 644`, regular file | matches |
| V12 | `/var/lib/freedom-blades` `root:root 0755` | `root:root 755`, `dev=2049 ino=1275049` | matches |
| V4 | `/var/lib/freedom-blades/laboratory` `root:freedomlab 0750` | `root:freedomlab 750`, `ino=1275050` | matches |
| V9 | `…/laboratory/runs` `root:freedomlab 03770` | `root:freedomlab 3770`, `ino=1275051` | matches |
| V5 | `/var/lib/freedom-blades/recovery` `root:root 0700` | `root:root 700`, `ino=1275052` | matches |
| V7 | **absent** | `laboratory` holds only `runs`; no `lifecycle.json`, no `.tmp` | absent, as required |
| canonical `R` | **absent** | `/var/lib/fb-evidence-p5-0`: No such file or directory | absent, as required |
| residue | none | `find … -name '.fb-i3-verify-*'` returned nothing | none |
| `R`'s parent | `/var/lib` `root:root 0755` | `root:root 755`, `dev=2049 ino=97831` | matches |
| hard-link policy | `1` | `fs.protected_hardlinks = 1` | matches |
| mount | ext4, read-write | `ext4 /dev/sda1 rw,relatime,discard,…` | matches |
| interpreter | `/opt/freedom-blades/runtime/venv-web/bin/python` | present, Python 3.12.14 | matches |
| `/run` objects | lock present | `/run/freedom-blades` `root:freedomlab 750`; `laboratory.lock` `root:freedomlab 660` | matches |

No database was invoked and `TEST_DATABASE_URL` was neither set nor required at
any point.

## 6. The invocation actually run

Two levels must be distinguished, and the original text of this section
wrongly collapsed them by saying "no wrapper" (erratum, item 5).

**Level 1 — the reviewed verifier argv**, run from
`/opt/freedom-blades/platform` on `oracle-test`, as root via `sudo`, using the
documented interpreter. It is exactly the authorized invocation: no added
flags, no ad hoc script, no re-implementation, no substituted
shell/Python/`ctypes` probe, and the verifier object was not invoked directly.

```bash
sudo /opt/freedom-blades/runtime/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.i3_verifier_cli \
  --arm-i3-controlled-write --identity root
```

**Level 2 — the shell-level evidence-capture wrapper** that carried that argv
to the target. It is an ordinary operator wrapper — `ssh`, `cd`, UTC
timestamps, stdout/stderr redirection, exit-status capture and `cat` — and it
is what created the two `/tmp` files recorded in §8. It adds nothing to the
verifier's own behaviour and changes none of its arguments.

Recovered verbatim from this operator's execution transcript, not
reconstructed, this is the complete shell command that was executed, with all
SSH quoting, redirection and exit-status capture exactly as issued:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && date -u +'START %Y-%m-%dT%H:%M:%SZ' && sudo /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.i3_verifier_cli --arm-i3-controlled-write --identity root > /tmp/fb-i3-root.out 2>/tmp/fb-i3-root.err; echo \"EXIT=\$?\"; date -u +'END %Y-%m-%dT%H:%M:%SZ'; echo '=== STDOUT ==='; cat /tmp/fb-i3-root.out; echo '=== STDERR ==='; cat /tmp/fb-i3-root.err"
```

Read as a single line of 434 characters. The escaped `\"EXIT=\$?\"` defers
`$?` to the remote shell, so the exit status reported is the verifier's own.
Its captured transcript output was:

```
START 2026-09-20T13:14:44Z
EXIT=4
END 2026-09-20T13:14:45Z
```

followed by the `=== STDOUT ===` and `=== STDERR ===` sections quoted below.

| Property | Value |
|---|---|
| Execution identity | `root` (via `sudo`; the program changes no identity) |
| Start | `2026-09-20T13:14:44Z` |
| End | `2026-09-20T13:14:45Z` |
| **Exit status** | **`4`** — refused before the first write |

Complete safe stdout, verbatim:

```
I3 CONTROLLED-WRITE VERIFICATION — REFUSED-BEFORE-WRITE
  invocation           : root
  refusal              : target-mismatch
  written              : nothing
  descriptors          : 0 directory roles not released
  statement            : Capability masks are recorded as evidence and are never attribution. This verifier does not isolate, require or prove CAP_FOWNER, and it never reads CapBnd as CapEff. Each publication relies on the protected-hardlink filesystem-UID owner condition, which is observed; a root link that succeeds cannot show which permitted branch the kernel took.
  not observed         : securebits is not observed: the kernel exposes it only through prctl(2), and the one ctypes exception in this package belongs to the case program.
```

Complete safe stderr, verbatim:

```
NOT VERIFIED — refused-before-write.
```

The output is entirely within the reviewed safe vocabulary: `target-mismatch`
is a member of `ADMISSION_REFUSALS`, and the two fixed statements are
`NOT_ATTRIBUTION` and `SECUREBITS_NOT_OBSERVED`. No path, account name or
number, listing, environment value or exception text appears.

**The `ubuntu` invocation was not run.** The authorization permits it only
after the root invocation returns `verified` with exit status `0`.

## 7. Per-context evidence

**None exists, and none can.** The refusal occurred in admission, before any
context was entered — before the first `openat`, the first `mkdirat` and the
first `linkat`. The run therefore has:

- no context status, nonce, stage, object identity, final mode,
  owner-condition observation, link count, payload result or operation-time
  capability evidence, for any of T1, §2.3.3, P2 or T6;
- no capability evidence at admission either: the target comparison precedes
  the identity and mask observations, so the masks were never read;
- no tracked objects, and therefore no fates;
- `0` cleanup-barrier failures and `0` unreleased descriptor roles, as printed.

A refusal at admission establishes **nothing about target behaviour**. It is
not a negative result for I3.

## 8. Residue and final survey

The verifier performed no residue survey — a survey belongs to a run that
wrote. An independent read-only check after the invocation found every
reviewed object exactly as recorded before the pass:

- `/var/lib/fb-evidence-p5-0` — absent;
- no `.fb-i3-verify-` name anywhere under `/var/lib/freedom-blades`;
- `laboratory` holds only `runs`; `runs` and `recovery` are empty;
- V7 still absent.

**No verifier-controlled mutation occurred in this pass.** Nothing was
created, removed, chmoded, chowned, provisioned or repaired *by the verifier*,
and no reviewed object — canonical `R`, the four publication directories, V1,
V2, V3, V12, V4, V9, V5 or V7 — was created, removed or altered by anything in
this pass. The pass's two disclosed effects on the target are the authorized
§3.2 synchronization of the repository worktree (§3) and the two operator
capture files below.

Two files this operator created for output capture remain on the target at
`/tmp/fb-i3-root.out` and `/tmp/fb-i3-root.err` (`ubuntu:ubuntu`, 761 and 39
bytes, 13:14:45Z). They hold exactly the text quoted in §6. They were created
by the shell-level evidence-capture wrapper's redirection (§6, level 2), not
by the verifier: they are **operator evidence artifacts, not verifier
residue**, and they lie outside canonical `R` and outside the four publication
directories. Their presence is therefore not a residue finding and does not
bear on the verifier's cleanup contract. They were left in place rather than
deleted so the raw output can be inspected independently, and correction
C-P5.0-LAB-I3-R4-E1 does not delete them or authorize their deletion.

## 9. Checks not run, and why

| Check | Why not |
|---|---|
| The `ubuntu` invocation (T6 under V9) | Authorized only after a `verified` root invocation with exit `0`. The root invocation exited `4` |
| T1, §2.3.3, P2, T6 publication, observation and removal | Never reached; admission refused first |
| Capability masks at admission and at each link | Never read; the target comparison precedes them |
| Harness invocation on the target, including a dry run, to reproduce the digest | Not authorized by this pass. Tree identity was established by hashing the covered file set on both hosts instead |
| Test suites on the target | Not authorized and not required by this pass; no database was used and `TEST_DATABASE_URL` was never set |
| Any repair, provisioning, `chmod`, `chown`, group change, capability change or V7 initialization | Explicitly excluded, and a stop condition was in force |
| Any source-code change to resolve the mismatch | Not authorized; and it is a maintainer decision — see §10 |

## 10. Why this is not an operator fix

The divergent value is not incidental. `APPROVED_TARGET_FACTS.host` and
`APPROVED_TARGET.host` are both hashed into `TARGET_IDENTITY_DIGEST`
(`approved_target.py:169-176`), which the review manifest carries
(`review_manifest.py:515`, `:954`) and which also derives `CONFIRMATION_TOKEN`.

Changing either value — or changing what admission compares — would:

1. change `TARGET_IDENTITY_DIGEST` and `CONFIRMATION_TOKEN`;
2. change the review manifest and therefore the review-input digest, which is
   currently the accepted `be9e110f…`; and
3. invalidate the accepted manifest-version-16 tree this authorization names,
   requiring fresh independent review before any operational retry.

Renaming the host instead would change the target's identity as observed, and
the target was named and confirmed by the Operations Owner on 2026-09-05.

Either route is a maintainer decision about target identity, and it is exactly
the kind of change this authorization withholds. The options are recorded here
without a recommendation being acted on:

- **A.** Rule that admission compares the kernel nodename against a separately
  recorded nodename fact, keeping `host` as the alias it is. This adds a fact
  and moves the digest.
- **B.** Rule that `APPROVED_TARGET_FACTS.host` is the nodename `Test`, and
  that the alias lives only in the runbook. This moves the digest and the
  confirmation token.
- **C.** Set the target's nodename to `oracle-test`. This is a host change,
  mutating a confirmed target fact, and is not authorized here.

A maintainer decision is required before any operational retry. Nothing in this
handback chooses one.

## 11. Resulting state

**I3 is unconfirmed.** It was not performed: no controlled write occurred, and
the four publication contexts were not exercised.

Unchanged by this pass, and stated for the record:

- V7 remains excluded and absent;
- `plan.is_executable = False`, untouched;
- V8 and V10 remain unperformed;
- Package 5.0 remains **not ready**;
- LAB-SECRETS-1 remains Open, Low;
- LAB-V6-P2 remains deferred;
- the review-input digest remains `be9e110f…`, which is not an approval and is
  not authority for `--execute`;
- no repository source, test or generated artifact was changed. The only
  repository changes in this pass are this handback and the factual pointer,
  register and §20 updates it requires.

No claim is made that target behaviour is confirmed beyond the four I3
contexts, and no claim is made that a capability caused any link — no link was
attempted. The authorization C-P5.0-LAB-I3-R4 is **consumed**: its two
invocations were attempted to the point the stop conditions allow, and it
cannot be reused for a retry.

## 12. Files changed, rollback, and reviewer focus

**Files changed in this pass — documentation only:** this handback (new); the
pointer and state banner at the top of `docs/review/Handover information`; the
restriction banner in `docs/operations/disposable-test-server.md`; §20 of
`docs/implementation-plan.md`; and the status, RAID, decision and change
registers. No source file, test, migration, configuration or generated artifact
was changed. `git diff --check` is clean, and the 62 earlier-pass and
reviewer-authored working-tree changes were preserved untouched.

**No test suite was run**, and none is claimed. This pass authorized
synchronization, read-only inspection and two verifier invocations only; the
accepted `tests/phase_5_0_evidence` figures belong to C-P5.0-LAB-I3-R3 and are
evidence about that pass, not this one. No formatter, linter or type checker
was run, for the same reason. Both artifacts were re-hashed after the
documentation edits and are unchanged, so the accepted digest still holds.

**Rollback:** none is required. No verifier-controlled mutation occurred, so
no reviewed object needs reversing. The two effects that do exist are benign
and disclosed: the authorized §3.2 synchronization left the remote repository
worktree matching this workspace, which is its intended state and is re-made
by the next authorized synchronization; and the two `/tmp` capture files may
be deleted at any time without affecting any reviewed object — though not
under this correction, which authorizes no host action. The repository changes
are documentation and are revertible by reverting this pass's edits.

**Security implications:** none introduced. No secret file was read, printed,
transferred or modified; the synchronization used the accepted secret-excluding
command in its admitted shape and no guard refusal occurred. The verifier's
safe-output contract held — the refusal printed one closed-vocabulary
classification and no host detail.

**Proposed reviewer focus areas:**

1. whether the §1 root cause is complete — that admission compares the nodename
   and that nothing else in the refusal path contributed;
2. whether §4's file-set hashing is accepted as establishing target tree
   identity in place of a dry-run harness invocation on the target, which this
   authorization does not permit;
3. the §10 reasoning that resolution moves `TARGET_IDENTITY_DIGEST` and the
   review-input digest, and therefore needs fresh review before a retry; and
4. whether leaving the two `/tmp` capture files in place is the preferred
   disposition, or whether they should be removed.

**Unresolved question:** the §10 target-identity decision. It is stated as an
open decision with three unchosen options, not as a recommendation, and not as
a finding closed by this pass.

Returned for fresh independent Codex technical, security and evidence review,
and for the maintainer decision in §10. **I3 is not closed, and is not closable
on this evidence.** Nothing in this handback closes a finding, accepts a risk,
approves a digest or advances a gate.
