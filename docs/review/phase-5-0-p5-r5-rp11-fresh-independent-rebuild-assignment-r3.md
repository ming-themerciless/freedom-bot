# Accepted assignment (R3) — fresh R-5 independent static-launcher rebuild in `/var/tmp`

Execution work ID: `C-P5.0-R5-RP11-FRESH-R5-R3` (confirmed by Peter Duscha)

Prepared under: `C-P5.0-R5-RP11-FRESH-A2`
([preparation prompt](phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md),
[preparation handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md))

Successor to the accepted and consumed procedure
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)
(prepared under `C-P5.0-R5-RP11-FRESH-A1`, revised under `-A1-R1` and `-A1-R2`;
reviewed proposal
[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md),
SHA-256 `f5b4c4e935817e7a68df3c8d1b6f8cc78617e0db6622a86a45ea38c1f0c18f94`).
Its single run `C-P5.0-R5-RP11-FRESH-R5` ended at an accepted Step 5 HARD STOP:
[handback](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md),
[independent review](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop.md),
[decision and cleanup authority](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md),
[cleanup result](phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md).

Prepared: 2026-10-03, by Claude as drafting assignee

Execution assignee: **Gemini**, for one wholly new run, accepted and activated
by Peter Duscha on 2026-10-03.

Status: **Accepted and activated for one bounded run by Gemini on 2026-10-03.**

---

## 0. Decision requested and what this document does not do

Codex independently reviewed this successor with no Blocking, Important or
Optional finding. Peter Duscha accepted it as written, including the strict
S1.3 evidence rule, confirmed the execution work ID and handback path, and
activated Gemini for one bounded run. The controlling acceptance and
activation record is
[`project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md`](project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md).

Only Gemini receives this execution authority, and only for the single run
described here. The authority ends at PASS, INVALID RUN or HARD STOP and the
completed handback and closing record.

Claude prepared this draft from implementation knowledge. Claude implemented
I-7 and I-7-R1, so Claude is **ineligible** to execute R-5, to be the R-5
assignee, to select or appoint the assignee, to review or accept this
draft, or to characterize any R-5 result. This draft says only what a PASS
would require. It does not predict one.

The predecessor's acceptance record is
[`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md),
and its consumed activation record is
[`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md).
Neither authorizes this run. The authority for preparing it is Peter Duscha's
[2026-10-03 decision](project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md),
which permits one wholly new Gemini run only after an exact assignment is
written, reviewed and activated.

### 0.1 What R3 changes, and what it does not

R3 carries over the accepted procedure's pinned inputs, comparisons, ordering,
single-invocation limits and terminal-state rules unchanged, except for
exactly these amendments:

| # | Amendment | Where |
|---|---|---|
| 1 | Every outer-host run resource on `oracle-test` (checkout, index, package cache, provisioned root, work, evidence and pytest tree) is allocated under `/var/tmp/<RUN>-*` instead of `/tmp/<RUN>-*`. The build root's own `/tmp` and `/var/tmp` keep their accepted meaning | §5; §6 steps 4a–11 |
| 2 | Step 2 checks that `oracle-test:/var/tmp` is a real directory, records `df`, filesystem type, mount options, available bytes and inodes for it, requires at least 4 GiB available, and checks the fresh-prefix absence in `/var/tmp` | §5; §6.0 statuses 10, 15, 16; §6 step 2 |
| 3 | Every creation, synchronization, build, evidence, accounting, retention and cleanup-state statement names `/var/tmp` for the outer-host run resources | §4.4, §5, §6, §7, §10 |
| 4 | `FRESH-R5-HS-1`, prospectively: S1.3 prints the complete actual stdout of `git status --short --untracked-files=all`, with its line count and SHA-256, before S1.4 prints and gates the derived repository-state result, and the handback must reproduce it | §6 step 1; §6 step 12b; §10 item 3 |
| 5 | New run identifier, new execution work ID and new handback path; no resume or reuse of the stopped run | header; §2; §5; §10; §12 |
| 6 | No remediation, retry, cleanup, package change, privilege escalation, service or database action, secret access, commit or push; at PASS, INVALID RUN or HARD STOP Gemini writes the complete handback and closing record and stops | unchanged in substance: §6 step 12, §7, §8 |
| 7 | The resolved Gemini `/goal` invocation | §13 |

The closed predecessor handback is not edited. `FRESH-R5-HS-1` stays attached
to it; amendment 4 prevents the same defect in this run only.

## 1. Objective

Perform D2 §5.3.5 R-5 once: an independent rebuild by a party other than the
I-7/I-7-R1 implementer. The run provisions a fresh root from the accepted
`toolchain.lock` and performs R-1 … R-3 through the accepted same-invocation
gate. It compares the diagnostic `cc1.v` exactly with the accepted baseline.
At least one of HA-1 … HA-3 must actually differ from the accepted reference
environment under the qualification rules of §4.2.

This run is wholly new. It is not a resume, retry or partial rerun of
`C-P5.0-R5-RP11-FRESH-R5`, and it inherits nothing from that run except the
governance records that describe it.

This is reproducibility and build-environment evidence (D9-3) only. It is not
decoder evidence. It does not repeat or replace XD-9, XD-11 or D9-2 (LD-8,
LD-9; D2 §5.3.8).

## 2. Independence and assignee

1. The executor is named only by Peter Duscha in the acceptance record.
2. **Claude is ineligible** because Claude implemented I-7 and I-7-R1.
3. Before any host action, the executor writes the following attestation in
   its handback and signs it with its identity:
   * it did not implement, co-author or remediate I-7 or I-7-R1;
   * it has not reused, and will not use, any earlier build root, package
     cache, checkout, work directory, build output, trace, evidence or scratch
     directory; and
   * it has read this assignment and the acceptance record that names it.
4. **Gemini is the intended executor**, so the run must be wholly fresh. It
   must not read, reuse, copy, compare against or inherit any resource or
   artifact from Gemini's earlier R-5 run (`/tmp/r5-*-gemini-f8a1` on
   `oracle-test`), its B1 run (`/tmp/p5-b1-repro-20261001t190454z-*` on the
   repository host) or its stopped fresh R-5 run
   `p5-r5-fresh-20261002T184800Z-7e9b2d41` (formerly
   `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-*` on `oracle-test`, deleted by
   Codex on 2026-10-03; any surviving copy is equally forbidden). That
   includes roots, caches, checkouts, outputs, `cc1.v` bytes, manifests,
   traces, logs and pytest temporary directories. The closed handback of the
   stopped fresh run and its review are governance records: they may be read,
   but no value in them is an input, a comparison value or a substitute for a
   fresh observation. The only exception is the committed repository fixture,
   read as described in §5. Gemini's stopped-run digest `cdc0fe11…45f9` stays
   rejected and is not a comparison input.

## 3. Controlling inputs (pinned; verify before any host or provisioning action)

### 3.1 Accepted state that this assignment must not alter

| Item | Accepted value |
|---|---|
| review-manifest version | `30` |
| aggregate review-manifest digest | `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526` |
| diagnostic baseline path | `infra/rp11-launch/verify/fixtures/cc1.v.baseline` |
| diagnostic baseline length | `5120` bytes |
| diagnostic baseline SHA-256 | `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` |
| normative outputs | the four entries of `infra/rp11-launch/expected.sha256` (§3.3) |
| `cc1.v.baseline` status | diagnostic comparison evidence, **not** a fifth normative output |
| `B1-R3-1`, `B1-R3-2` | Closed as remediated |
| R-5 | stopped, Blocking, unaccepted |
| RP-11 | unwired and unmet |
| `plan.is_executable` | `False` |
| PO-9, PO-14 | open |
| Package 5.0 | not ready |

### 3.2 File digests (SHA-256, calculated read-only at preparation)

Prepared against commit `9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa` on
`docs/platform-plan`, and re-verified read-only at the same commit under
`C-P5.0-R5-RP11-FRESH-A1-R1` and again under `C-P5.0-R5-RP11-FRESH-A2`. The
commit is recorded for orientation only:
**the binding identities are the digests and lengths below**. A later commit
is acceptable only if every listed file still has exactly these bytes and the
repository-state check of §6 step 1 passes.

| File | Bytes | SHA-256 |
|---|---:|---|
| `infra/rp11-launch/toolchain.lock` | 16509 | `f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf` |
| `infra/rp11-launch/build-root.manifest` | 381913 | `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` |
| `infra/rp11-launch/expected.sha256` | 328 | `6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625` |
| `infra/rp11-launch/verify/fixtures/cc1.v.baseline` | 5120 | `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | 376981 | `c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c` |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | 178810 | `f02b7acfa14b1c108ab53942bd3f89a9bd629eccb6c2c685419e07bf729dec3d` |
| `infra/rp11-launch/build.sh` | 2819 | `7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0` |
| `infra/rp11-launch/launch.c` | 6314 | `6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe` |
| `infra/rp11-launch/select.h` | 2187 | `34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b` |
| `infra/rp11-launch/start.s` | 857 | `ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139` |
| `infra/rp11-launch/rp11-launch.ld` | 2321 | `ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326` |
| `infra/rp11-launch/rp11-launch.x86_64.listing` | 21742 | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` |
| `infra/rp11-launch/buildroot/provision.py` | 15106 | `40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300` |
| `infra/rp11-launch/buildroot/enter.py` | 14521 | `cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a` |
| `infra/rp11-launch/verify/cc1check.py` | 6021 | `16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72` |
| `infra/rp11-launch/verify/ic1check.py` | 18546 | `ea7d9dd3d8e141349019cfdeba5e91df7569e28d6818136777f59bf313316917` |
| `infra/rp11-launch/verify/elfcheck.py` | 7695 | `b742552c6d200dd1c0536f29a444dcc4a00405f758788bc82c8b2c4f2df2aceb` |
| `infra/rp11-launch/verify/tl11.py` | 5432 | `cb1b8d835983b625e8e42dda2d46aa2d5e56816cf90fb8c3a397e291c3d0e676` |
| `infra/rp11-launch/verify/ctverify.py` | 35036 | `eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31` |
| `infra/rp11-launch/verify/xdecode.py` | 54170 | `84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97` |
| `infra/rp11-launch/verify/xdecode-spelling.table` | 3806 | `d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66` |
| `infra/rp11-launch/verify/xdecode-corpus.txt` | 14292 | `f0e811a4bd61782789b66f31ab4401797e52b8ac00ffeebb984bfcd71afb4a8a` |
| `infra/rp11-launch/test-harness/select_harness.c` | 2228 | `603099e0f7279e4158023a63b6bc1411c0d9d3ac7c9372c7f77fa9d42f0b0a94` |
| `infra/rp11-launch/test-harness/select_shim.c` | 950 | `8c4ad99c0a1f3452923dab46149e7f4b202060ef5bf981b732ec9e9724dd91fd` |
| `tests/test_rp11_launch_toolchain.py` | 12326 | `ff3d458cabae91512562cca6143542337b1306dc3df791da505c51a9519ab76f` |
| `tests/rp11_launch_support.py` | 8045 | `bc24c0ee7b0c9f58853479adc908c60cf013b9652409e3d5cee0d710074a18b6` |
| `tools/phase_5_0_evidence/rp11_launch.py` | 15849 | `5a2f4694983619d6a3fb7ac3965e4415dd114fb7504003d91abb6071d189c2b1` |
| `tools/phase_5_0_evidence/review_manifest.py` | 73785 | `311f1d0300e3e98f5b3b33ea6c4598bfc744ad8e9ba61bf0d2adb2d62f5c1844` |

Appendix A restates these 28 digests in `sha256sum --check` format and
Appendix B restates digest, length and path for the independent Python check.
Both appendices were generated from this table and verified against the tree.
The 22 `infra/rp11-launch/` entries above are the **complete** file set of that
directory, apart from ignored `__pycache__` directories; §6 checks this.

Cross-checks the executor makes mechanically in §6:

* `toolchain.lock` has exactly 62 `package=` lines, its `archive_snapshot` is
  `20261001T000000Z`, and its `build_root_manifest_sha256` equals the
  `build-root.manifest` digest above;
* the committed listing's digest equals the listing entry of
  `expected.sha256` (both appear in the table);
* the review manifest rebuilt in memory serializes byte-equal to the checked-in
  JSON, reports `MANIFEST_VERSION = 30` and aggregate `28a4f4c2…a526`, and the
  plan reports `is_executable=False`; and
* `tools/phase_5_0_evidence/rp11_launch.py`, which holds the image, listing,
  map, `launch.s`, lock and manifest digests, `CC1_V_BASELINE_PATH` and
  `CC1_V_BASELINE_LENGTH = 5120`, has exactly the bytes above.

### 3.3 Normative outputs (`expected.sha256`, unchanged)

```text
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  rp11-launch
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  rp11-launch.x86_64.listing
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d  rp11-launch.map
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706  launch.s
```

### 3.4 Accepted reference environment (first party; do not rewrite)

These are the recorded facts of Claude's accepted I-7/I-7-R1 builds, as later
confirmed for B1 and in Peter's B1 decision. They are comparison values, not
observations of the run.

| HA | Reference value | Source |
|---|---|---|
| HA-1 kernel release | `6.8.0-139-generic` (x86_64; Ubuntu 24.04.4 host) | I-7 and I-7-R1 handbacks; B1 handback |
| HA-2 CPU model | `AMD EPYC-Milan Processor` (family 25, model 1). I-7 records it as "AMD EPYC-Milan". **No reference CPU feature-flag list was ever recorded** (B1-R1) | I-7 and I-7-R1 handbacks; B1/B1-R1 handbacks |
| HA-3 entry mechanism | bubblewrap `0.9.0`, `/usr/bin/bwrap`, unprivileged user namespace, the fixed vector of `enter.py` (`--unshare-all --die-with-parent --new-session --clearenv`, root bound read-only at `/`) | `toolchain.lock` `entry_mechanism`; I-7 handback; `enter.py` `_bwrap` |
| HA-4 time | recorded; SOURCE_DATE_EPOCH=0; varied by R-4(b) | D2 §5.3.8 |
| HA-5 identity | build user `rp11build` uid/gid 1000, sandbox host name `rp11-build`; R-4(c) uses 1001 / `rp11-variant` | `enter.py` `VARIANTS`; D2 §5.3.8 |

## 4. Host-assumption variation (LD-8, implemented conservatively)

### 4.1 Recording

1. The executor records HA-1 … HA-5 **freshly on the execution host, before
   provisioning** (§6 step 2), and again at the end (§6 step 11).
2. The record gives the exact kernel release and version string; the CPU
   vendor, model name, family, model, stepping and complete `flags` line, and
   the full `lscpu` output; and the entry mechanism's name, version, package
   version, executable identity (mode, owner, size, SHA-256). The bubblewrap
   vector is fixed by the digest-verified `enter.py` and is not re-derived.
3. HA-4 is recorded as the UTC times printed by S2.1 and S11.7 on
   `oracle-test`. These are HA observations. They are separate from, and do
   not replace, the timed-scope values of §6.0. HA-5 is recorded as the outer
   user (`id`), the outer host name, and the in-sandbox identities set by
   `enter.py`. Neither varies the pass condition. R-4(b) and R-4(c) reach them
   through the corroborating tests (§6 step 10).

### 4.2 Qualification rules (normative)

LD-8 and D2 §5.3.5 require R-5 to use at least one of a different kernel
release (HA-1), a different machine or CPU model (HA-2), or a different entry
mechanism (HA-3). For this assignment:

* **HA-1 qualifies only through a different kernel release:** the exact
  string `os.uname().release` (equal to `uname -r`) differs from
  `6.8.0-139-generic`.
* **HA-2 qualifies only through a different CPU model:** every processor in
  `/proc/cpuinfo` reports one and the same `model name`, and that exact string
  is neither `AMD EPYC-Milan Processor` nor `AMD EPYC-Milan`. Because no
  accepted reference feature list exists, **a feature-flag, microcode,
  stepping or topology difference does not qualify**, alone or in combination.
  Flags are still recorded.
* **HA-3 qualifies only through a materially different entry mechanism, or a
  materially different entry configuration, accepted in advance by Peter
  Duscha.** A bubblewrap **version-only** difference does **not**, by itself,
  qualify as the "different entry mechanism" that D2 and LD-8 require: it is a
  different version of the same `/usr/bin/bwrap` mechanism using the same
  vector. `enter.py` supports only that mechanism and vector, and this
  assignment adds no mechanism and changes no source. **HA-3 therefore cannot
  qualify in this run** unless Peter separately accepts a materially different
  HA-3 configuration before execution, which would be a new reviewed
  assignment, not an executor choice.

Consequently **the run must rely on an actually measured HA-1 or HA-2
difference.** §6 step 3 applies these rules mechanically.

### 4.3 INVALID RUN and unexplained differences

1. **If neither HA-1 nor HA-2 qualifies, the run is INVALID.** The executor
   stops at §6 step 3, before creating any directory or provisioning. A run
   later found to have had no qualifying difference is INVALID even if every
   byte matched.
2. **Every unexplained difference is a hard stop.** The only differences this
   assignment explains in advance are: the qualifying HA-1 or HA-2 difference
   itself; a different bubblewrap version (recorded, not qualifying); the
   diagnostic context of §4.4; the checkout-directory mode change named in
   §6 step 4; and the timestamp values of §6.0, which are recorded, not
   compared. Any other difference between the start and end observations,
   between the planned and the observed environment, or in any output, is
   unexplained.

### 4.4 Diagnostic context (not HA facts, not a route to PASS)

`MemTotal`, soft and hard `ulimit -a`, and `/var/tmp`'s filesystem, mount
options, capacity and inodes (S2.18a–S2.18d) are recorded as diagnostic
context only. The `/var/tmp` facts also gate the preflight of §5; they are not
HA facts and are not a route to PASS. `cc1.v` contains a `GGC heuristics:` line, which the
GCC documentation says is derived from host memory and from `RLIMIT_DATA`,
`RLIMIT_AS` and `RLIMIT_RSS`. That is context for review only: **an exact
`cc1.v` mismatch remains a HARD STOP, and no GGC-line or other partial
exception is authorized** (§6 step 9, §8.3).

The intended disposable target is `oracle-test` (`138.2.182.39`). **None of
its documented or historical facts are assumed**: not the kernel
`7.0.0-31-generic`, CPU `AMD EPYC 7551`, bubblewrap `0.11.1`, interpreter, or
the presence of `rsync`, `zstd`, `gpgv` or the archive keyring; nor any value
recorded by the stopped fresh run or by Codex's 2026-10-03 cleanup
inspection, including the `/tmp` and `/var/tmp` capacity figures. Every fact
is observed afresh, and only after Codex has reviewed this assignment and Peter
has explicitly accepted it.

## 5. Freshness and isolation

`<RUN>` is a new run identifier of the form
`p5-r5-fresh-<UTC YYYYMMDDTHHMMSSZ>-<8 lowercase hex>`, generated by the
executor for this run. It must differ from the stopped run's
`p5-r5-fresh-20261002T184800Z-7e9b2d41`. Before anything is created, §6
step 2 proves that `oracle-test:/var/tmp` is a directory and not a link,
records its filesystem, mount options, capacity and inodes, requires the
capacity floor below, and proves that no entry of `oracle-test:/var/tmp`
begins with `<RUN>`. Nothing is created under `/tmp` or `/var/tmp` on the
repository host.

**Location.** Every outer-host run resource on `oracle-test` lives under
`/var/tmp/<RUN>-*`. Nothing of the run is created under `oracle-test:/tmp`.
Codex's 2026-10-03 inspection found that `/tmp` is a separate, fixed 475.4 MiB
tmpfs, which the stopped run exhausted at S5.5 (`Errno 122`), and that
`/var/tmp` was then on the root ext4 filesystem with 39 GiB available
([cleanup result](phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md)). Those
figures are context only. S2.18a–S2.18d observe `/var/tmp` afresh.

**Capacity floor (preflight only).** S2.18d requires at least 4 GiB
(4,294,967,296 bytes) available in `/var/tmp` to the unprivileged executor,
computed as `statvfs` `f_bavail × f_frsize`. Less than that is a **HARD STOP**
before any directory is created. The floor is a stop condition, not an
allowance: the run writes only what the blocks of §6 write and never consumes
space deliberately. S11.6 records what the run used. Per-user quota headroom
is not separately observable without privilege; the mount options are
recorded, and a write failure during the run remains a **HARD STOP**.

**The build root's own `/tmp` and `/var/tmp` are different directories.** The
provisioned root contains its own `/tmp` and `/var/tmp`, which are
`/var/tmp/<RUN>-root/tmp` and `/var/tmp/<RUN>-root/var/tmp` on the outer host
and appear at `/tmp` and `/var/tmp` inside the sandbox. `provision.py` creates
them empty with mode 1777, S7.4 checks them and IC-1 forbids creating
anything under them. Every reference to "the build root's `/tmp` or
`/var/tmp`" keeps that accepted meaning.

| Purpose | Host | Path | Mode |
|---|---|---|---|
| controlled checkout | `oracle-test` | `/var/tmp/<RUN>-checkout/` | created `0700`; the synchronization then applies the source directory's mode (§6 step 4); both recorded |
| signed-index check cache | `oracle-test` | `/var/tmp/<RUN>-index/` | `0700` |
| package cache | `oracle-test` | `/var/tmp/<RUN>-cache/` | `0700` |
| provisioned build root | `oracle-test` | `/var/tmp/<RUN>-root/` | created `0700`; `provision.py` sets `0755` (both recorded) |
| build work and outputs | `oracle-test` | `/var/tmp/<RUN>-work/` (`co-r2/build-out/` inside) | `0700` |
| trace, comparison and run evidence | `oracle-test` | `/var/tmp/<RUN>-evidence/` | `0700` |
| pytest temporary tree | `oracle-test` | `/var/tmp/<RUN>-pytest/` (created by pytest `--basetemp`) | recorded |
| handback | repository | `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md` *(confirmed; §12)* | — |

The executor records every path's mode, owner and group at creation and at the
end. These are **forbidden** as inputs, work locations or comparison sources:

* every earlier R-5, B1, I-7 or I-7-R1 root, cache, checkout, output, trace,
  log and scratch directory, including `/tmp/r5-*`, `/tmp/p5-b1-repro-*`,
  any `/tmp/pytest-of-*`, and any agent scratchpad;
* every resource of the stopped fresh run, including
  `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-*` and any copy of it;
* any location under `oracle-test:/tmp` as a run resource;
* `oracle-test:/opt/freedom-blades/platform`, a synchronized tree of
  unrecorded provenance, which must not be read, used or modified; and
* any `cc1.v`, manifest or output bytes not produced by this run.

The fixture `infra/rp11-launch/verify/fixtures/cc1.v.baseline` is read **only**
from the controlled checkout, and only as `cc1check.py`'s baseline argument.
It must never be copied into `build-out/`, into the work tree or into an
evidence location as if it were generated output.

Every Python invocation sets `PYTHONDONTWRITEBYTECODE=1` or runs with `-B`.
pytest runs with `-p no:cacheprovider`, so the controlled checkout is not
written to.

## 6. Required ordered procedure

### 6.0 Execution conventions (normative)

**Substitutions.** Each block runs exactly as written, with only these
substitutions: `<RUN>` (§5); `<PY>`, which is
`/opt/freedom-blades/runtime/venv-web/bin/python` on `oracle-test`; the
placeholder lines `<APPENDIX A>` and `<APPENDIX B>`, each replaced by the
28 lines of the named appendix, verbatim, with no blank line added; in
S4d.4 and S11.3 only, `'<the S1.6 program, verbatim>'`, replaced by the
single-quoted Python program of S1.6, byte for byte, including its quotes;
and, in the S12.end block only, `<HANDBACK>`, replaced by the
repository-relative path of the handback file that the acceptance record
names (§10, §12). That path consists only of characters in `[a-z0-9./-]`, so
it is safe inside the block's single quotes.

**Blocks.** Every command except the synchronization command of step 4b runs
inside a **block**: one shell process that receives the block's text on its
standard input. A repository-host block is invoked as
`/bin/bash --noprofile --norc -s <<'R5BLOCK'` … `R5BLOCK`; an `oracle-test`
block as `ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'` …
`R5BLOCK`. The quoted delimiter prevents any expansion by the invoking shell.
Each block's last line calls its function `r5_block` with standard input from
`/dev/null`, so no command inside the block can consume the block's own text.
The twelve **step blocks** (steps 1, 2, 3, 4a, 4c, 4d, 5, 6/7, 8, 9, 10 and 11)
also define the end-timestamp handler `r5_end` described under "Timestamps"
below. The four **timestamp blocks** (S4b.start, S4b.end, S12.start and
S12.end) are written out in step 4b and step 12; S12.end also defines
`r5_close`.

**Status handling.** Inside a block, every command is followed immediately by:

```bash
status=$?
printf '<label> exit=%s\n' "$status"
if [ "$status" -ne 0 ]; then exit "$status"; fi
```

so the exact status is captured before anything else runs, printed with its
step label, and, if nonzero, becomes the block's own exit status at once,
before any later check. A block that completes ends with
`printf '<step> block exit=0\n'` and `exit 0`. No block contains a pipe, a
`;`-chained check, `set -e`, or an `echo` after a checked command. Where a
block also displays an evidence file after a checked command, the checked
command's status is captured first and governs; the display status is checked
only afterwards (stated in each such block). `ssh` returns the remote block's
status, or 255 if `ssh` itself fails; no block uses 255.

**The executor records every block's complete transcript and its final exit
status as reported by the invoking shell.** It issues nothing after a block in
the same command line.

**Timestamps (normative).** Every timestamp is produced by `date -u` with a
format that prints the label and the value together, so the value is
`%Y-%m-%dT%H:%M:%SZ` (for example `2026-10-03T09:15:02Z`) and each line has
the form `<label> start_utc=<value>` or `<label> end_utc=<value>`. Each `date`
invocation's status is captured immediately, printed and enforced exactly as
any other command. Only POSIX `date` conversions are used (`%Y %m %d %H %M %S
%n`).

In a **step block**:

1. The first two commands of `r5_block` are `trap r5_end EXIT` (label
   `<step>.trap`) and the start timestamp (label `<step>.start`). Nothing
   precedes them. In step 1 the same single `date` invocation prints two lines
   from one clock reading: `RUN.start start_utc=…` and `S1.start start_utc=…`.
2. The end timestamp is taken by `r5_end`, which the shell runs on **every**
   exit from the block: after `exit 0`, after an `exit <status>` from any
   check, and after step 3's `exit 20`. On entry `r5_end` captures the block's
   exit status as `block_status` before doing anything else (POSIX: `$?` on
   entry to an `EXIT` trap is the status the shell is exiting with). It then
   prints `<step>.end end_utc=…`, captures and prints that `date` status as
   `<step>.end date exit=…`, and exits with the **governing status**, printed
   as `<step> final exit=…`: `block_status` if it is nonzero, otherwise the
   end-`date` status. A failed check therefore keeps its own status, and a
   failed end timestamp after an otherwise passing block is itself nonzero.
3. The `final exit` line equals the status that the invoking shell reports
   for the block. "Block exit 0" in this assignment means that status is 0,
   which requires `<step> block exit=0`, `<step>.end date exit=0` and
   `<step> final exit=0` all to be printed.

The four timestamp blocks are single-purpose: S4b.start and S4b.end bracket the
synchronization command (step 4b), and S12.start and S12.end bracket the
handback (step 12). S12.end also prints `RUN.end end_utc=…` from the same clock
reading as its `S12.end end_utc=…`, and writes both lines into the handback
itself (step 12). No timestamp is taken in any other way.

**Timed scopes.** "Each step" in §10 item 2 means each separately invoked
scope in this table, and nothing finer. Numbered checks inside a block (for
example S5.2) and prose actions are not separately timed.

| Scope | Start value (label, producing invocation) | End value (label, producing invocation) | Host |
|---|---|---|---|
| whole run | `RUN.start`, from the S1.start `date` in the step-1 block | `RUN.end`, from the S12.end `date` in the S12.end block | repository host |
| step 1 | `S1.start`, step-1 block | `S1.end`, step-1 block (`r5_end`) | repository host |
| step 2 | `S2.start`, step-2 block | `S2.end`, step-2 block (`r5_end`) | `oracle-test` |
| step 3 | `S3.start`, step-3 block | `S3.end`, step-3 block (`r5_end`) | `oracle-test` |
| step 4a | `S4a.start`, step-4a block | `S4a.end`, step-4a block (`r5_end`) | `oracle-test` |
| step 4b (the `rsync` invocation) | `S4b.start`, S4b.start block | `S4b.end`, S4b.end block | repository host |
| step 4c | `S4c.start`, step-4c block | `S4c.end`, step-4c block (`r5_end`) | repository host |
| step 4d | `S4d.start`, step-4d block | `S4d.end`, step-4d block (`r5_end`) | `oracle-test` |
| step 5 | `S5.start`, step-5 block | `S5.end`, step-5 block (`r5_end`) | `oracle-test` |
| steps 6 and 7, **combined** | `S6-S7.start`, steps-6/7 block | `S6-S7.end`, steps-6/7 block (`r5_end`) | `oracle-test` |
| step 8 | `S8.start`, step-8 block | `S8.end`, step-8 block (`r5_end`) | `oracle-test` |
| step 9 | `S9.start`, step-9 block | `S9.end`, step-9 block (`r5_end`) | `oracle-test` |
| step 10 | `S10.start`, step-10 block | `S10.end`, step-10 block (`r5_end`) | `oracle-test` |
| step 11 | `S11.start`, step-11 block | `S11.end`, step-11 block (`r5_end`) | `oracle-test` |
| step 12 (handback and immediate stop) | `S12.start`, S12.start block | `S12.end`, S12.end block | repository host |

Steps 6 and 7 run in one block, so they have **one** pair covering both steps
together: R-1 gate, R-2 build, manifest comparison and the root checks. There
is no separate step-6 or step-7 pair.

Rules for the timed scopes:

* A scope that did not start, because an earlier invocation stopped the run,
  has no timestamps and is recorded as `not run`.
* An end value that was not printed, for example because `ssh` failed with
  255 or the process was killed, is recorded as `absent` together with the
  invoking shell's status. **No required timestamp is ever reconstructed or
  supplied from an operator's clock, terminal or SSH-client metadata, shell
  history, file times or any wrapper not written here.**
* A missing, failed or malformed required timestamp is a **HARD STOP** for
  missing evidence (§8.3).
* Values come from two hosts' clocks and are recorded, not compared. A clock
  difference between the repository host and `oracle-test` is not a verdict
  input. The executor's independence attestation (§2), written before step 1,
  is not timed.

**Status meanings.** `0` is the accepted condition. `20` from step 3 is
**INVALID RUN** (§8.2). Every other nonzero status, whether from a tool or
from a conditional below, is a **HARD STOP** (§8.3). The conditionals return
these distinct statuses:

| Status | Condition |
|---:|---|
| 10 | an entry of `/var/tmp` on `oracle-test` begins with `<RUN>` |
| 11 | `/etc/ld.so.preload` exists in the build root (including a dangling link) |
| 12 | the build root's `/tmp` or `/var/tmp` has an entry |
| 13 | the build root's `/tmp` or `/var/tmp` is missing, a link or not a directory |
| 14 | `/proc/sys/user/max_user_namespaces` is not a positive integer |
| 15 | `/var/tmp` on `oracle-test` is missing, a link, not a directory, or not its own real path |
| 16 | `/var/tmp` on `oracle-test` has less than 4 GiB (4,294,967,296 bytes) available |
| 20 | neither HA-1 nor HA-2 qualifies (INVALID RUN) |
| 21 | `/proc/cpuinfo` has no `model name`, or more than one distinct one |
| 23 | lock facts differ (62 package lines, snapshot, manifest digest) |
| 24 | the in-memory review manifest differs from §3.1/§3.2 |
| 25 | a §3.2 digest or length differs |
| 26 | the digest list is not exactly 28 lines |
| 27 | `infra/rp11-launch/` has an extra, missing or non-regular entry |
| 28 | `infra`, `tests`, `tools` or `pytest.ini` differs from `HEAD` or has untracked files on the repository host |
| 29 | the package cache is not exactly the lock's 62 package files |
| 30 | a normative output digest differs (independent check) |
| 31 | `build.stdout` lacks a normative output digest line |
| 32 | the pytest result is not exactly 12 tests, 0 failures, 0 errors, 0 skipped |
| 33 | the handback file is missing, is a link or is not a regular file when the S12.end block runs |

### Step 1 — preflight repository identity and digests (repository host, read-only)

```bash
/bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S1.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S1.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S1 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S1.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+RUN.start start_utc=%Y-%m-%dT%H:%M:%SZ%nS1.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S1.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /opt/freedom-blades/platform
  status=$?
  printf 'S1.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  git rev-parse HEAD
  status=$?
  printf 'S1.2 git-rev-parse exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 python3 -I -B -c 'import hashlib,subprocess,sys
r=subprocess.run(["git","status","--short","--untracked-files=all"],capture_output=True)
sys.stdout.buffer.write(r.stdout)
sys.stdout.buffer.flush()
sys.stderr.buffer.write(r.stderr)
sys.stderr.buffer.flush()
sys.stdout.buffer.write(("git_status_lines=%d\ngit_status_sha256=%s\n" % (r.stdout.count(b"\n"),hashlib.sha256(r.stdout).hexdigest())).encode())
sys.stdout.buffer.flush()
sys.exit(r.returncode)'
  status=$?
  printf 'S1.3 git-status exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 python3 -I -B -c 'import subprocess,sys
paths=["infra","tests","tools","pytest.ini"]
r=subprocess.run(["git","status","--porcelain","--untracked-files=all","--"]+paths,capture_output=True,text=True)
sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
if r.returncode:
    sys.exit(r.returncode)
print("repository_state="+("drift" if r.stdout else "clean"))
sys.exit(28 if r.stdout else 0)'
  status=$?
  printf 'S1.4 repository-state exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum --strict -c <<'SUMS'
<APPENDIX A>
SUMS
  status=$?
  printf 'S1.5 sha256sum-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 python3 -I -B -c 'import hashlib,os,sys
rows=[l.split(" ",2) for l in sys.stdin.read().splitlines()]
bad=0
for want,size,path in rows:
    data=open(path,"rb").read()
    got=hashlib.sha256(data).hexdigest()
    ok=got==want and len(data)==int(size)
    bad+=not ok
    print(got,len(data),path,"OK" if ok else "MISMATCH")
print("rows",len(rows),"mismatches",bad)
if bad:
    sys.exit(25)
if len(rows)!=28:
    sys.exit(26)
top="infra/rp11-launch"
want_files={p for _w,_s,p in rows if p.startswith(top+"/")}
want_dirs={top}
for p in want_files:
    d=os.path.dirname(p)
    while d!=top:
        want_dirs.add(d)
        d=os.path.dirname(d)
got_files=set()
got_dirs=set()
odd=[]
for d,ds,fs in os.walk(top):
    ds[:]=[x for x in ds if x!="__pycache__"]
    got_dirs.add(d)
    for x in ds:
        if os.path.islink(os.path.join(d,x)):
            odd.append(os.path.join(d,x))
    for x in fs:
        p=os.path.join(d,x)
        if os.path.islink(p) or not os.path.isfile(p):
            odd.append(p)
        got_files.add(p)
for p in sorted(got_files-want_files):
    print("extra_file",p)
for p in sorted(want_files-got_files):
    print("missing_file",p)
for p in sorted(got_dirs^want_dirs):
    print("directory_set_difference",p)
for p in sorted(odd):
    print("not_regular",p)
print("launcher_tree files",len(got_files),"dirs",len(got_dirs))
sys.exit(27 if (got_files!=want_files or got_dirs!=want_dirs or odd) else 0)' <<'LIST'
<APPENDIX B>
LIST
  status=$?
  printf 'S1.6 hashlib-and-tree-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 python3 -I -B -c 'import sys
lines=open("infra/rp11-launch/toolchain.lock",encoding="utf-8").read().splitlines()
packages=[l for l in lines if l.startswith("package=")]
facts=dict(l.split("=",1) for l in lines if l.startswith(("archive_snapshot=","build_root_manifest_sha256=","entry_mechanism=")))
print("package_lines",len(packages))
for k in sorted(facts):
    print(k+"="+facts[k])
ok=len(packages)==62 and facts.get("archive_snapshot")=="20261001T000000Z" and facts.get("build_root_manifest_sha256")=="f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f"
sys.exit(0 if ok else 23)'
  status=$?
  printf 'S1.7 lock-facts exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import hashlib,sys
from tools.phase_5_0_evidence.execution.cli import build_concrete_plan, read_covered_sources
from tools.phase_5_0_evidence.review_manifest import ReviewManifest, MANIFEST_VERSION
p=build_concrete_plan()
m=ReviewManifest.build(p, read_covered_sources())
b=m.serialize()
f=open("docs/review/phase-5-0-evidence-harness-review-manifest.json","rb").read()
r=(MANIFEST_VERSION, m.digest(), b==f, hashlib.sha256(b).hexdigest(), p.is_executable)
print(*r)
want=(30,"28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526",True,"c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c",False)
sys.exit(0 if r==want else 24)'
  status=$?
  printf 'S1.8 in-memory-review-manifest exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  command -v rsync ssh
  status=$?
  printf 'S1.9 local-tools exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S1 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

Pass: block exit 0, which includes the timing lines `RUN.start start_utc=…`,
`S1.start start_utc=…`, `S1.end end_utc=…` and `S1 final exit=0` (§6.0).
S1.3 prints the complete stdout of one
`git status --short --untracked-files=all` invocation, every line of it,
followed by `git_status_lines=<N>` and `git_status_sha256=<digest>`, which are
computed from exactly those bytes; S1.4 prints `repository_state=clean`; S1.5
prints `OK` for all 28 files; S1.6 prints `OK` for all 28, `rows 28 mismatches 0` and
`launcher_tree files 22 dirs 5`; S1.7 prints `package_lines 62` and the
snapshot and manifest-digest values of §3.2; and S1.8 prints
`30 28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526 True c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c False`.
S1.3 is evidence, not a gate: documentation changes outside the controlled
paths are expected, and only git's own failure stops it. It runs before S1.4,
which derives and gates the repository state of the controlled paths. The
executor must reproduce every S1.3 line verbatim; a summary is not a
transcript (lesson of `FRESH-R5-HS-1`).
S1.8 only builds the review manifest in memory. It is not the harness and does
not use `--execute`. S1.4 binds the unpinned support files that step 10
imports (for example `tests/conftest.py` and the package `__init__.py` files)
to `HEAD`, because the synchronization of step 4 sends the working tree.

### Step 2 — fresh HA-1 … HA-5 observation (`oracle-test`, read-only)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S2.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S2.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S2 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S2.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S2.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S2.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u +%Y-%m-%dT%H:%M:%SZ
  status=$?
  printf 'S2.1 date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  uname -srvm
  status=$?
  printf 'S2.2 uname exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cat /proc/version
  status=$?
  printf 'S2.3 proc-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  lscpu
  status=$?
  printf 'S2.4 lscpu exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  awk '/^processor/{n++} n==1 && /^(vendor_id|cpu family|model|model name|stepping|microcode|flags)[[:space:]]*:/' /proc/cpuinfo
  status=$?
  printf 'S2.5 cpuinfo-first-processor exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /usr/bin/bwrap --version
  status=$?
  printf 'S2.6 bwrap-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -L -c '%a %U:%G %s %n' /usr/bin/bwrap
  status=$?
  printf 'S2.7 bwrap-stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /usr/bin/bwrap
  status=$?
  printf 'S2.8 bwrap-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  dpkg-query -W -f='${Package} ${Version}\n' bubblewrap
  status=$?
  printf 'S2.9 bwrap-package exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  read -r userns_max < /proc/sys/user/max_user_namespaces
  status=$?
  printf 'S2.10a max_user_namespaces-read exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'max_user_namespaces=%s\n' "$userns_max"
  case "$userns_max" in
    ''|*[!0-9]*|0) status=14 ;;
    *) status=0 ;;
  esac
  printf 'S2.10b max_user_namespaces-positive exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  apparmor_userns=/proc/sys/kernel/apparmor_restrict_unprivileged_userns
  if [ -e "$apparmor_userns" ]; then
    read -r apparmor_value < "$apparmor_userns"
    status=$?
    if [ "$status" -eq 0 ]; then
      printf 'apparmor_restrict_unprivileged_userns=%s\n' "$apparmor_value"
    fi
  else
    printf 'apparmor_restrict_unprivileged_userns=absent\n'
    status=0
  fi
  printf 'S2.11 apparmor-userns exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  id
  status=$?
  printf 'S2.12 id exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  hostname
  status=$?
  printf 'S2.13 hostname exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cat /etc/os-release
  status=$?
  printf 'S2.14 os-release exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  grep MemTotal /proc/meminfo
  status=$?
  printf 'S2.15 memtotal exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  ulimit -Sa
  status=$?
  printf 'S2.16 ulimit-soft exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  ulimit -Ha
  status=$?
  printf 'S2.17 ulimit-hard exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import os,stat,sys
p="/var/tmp"
try:
    st=os.lstat(p)
except FileNotFoundError:
    print("var_tmp=missing")
    sys.exit(15)
if stat.S_ISLNK(st.st_mode):
    print("var_tmp=link")
    sys.exit(15)
if not stat.S_ISDIR(st.st_mode):
    print("var_tmp=not-a-directory")
    sys.exit(15)
real=os.path.realpath(p)
if real!=p:
    print("var_tmp=resolves-elsewhere realpath="+real)
    sys.exit(15)
print("var_tmp=directory mode=%04o uid=%d gid=%d" % (stat.S_IMODE(st.st_mode),st.st_uid,st.st_gid))
sys.exit(0)'
  status=$?
  printf 'S2.18a var-tmp-directory exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  df -P -T /var/tmp
  status=$?
  printf 'S2.18b df-var-tmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  df -P -i /var/tmp
  status=$?
  printf 'S2.18c df-inodes-var-tmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import os,sys
p="/var/tmp"
best=None
for line in open("/proc/self/mountinfo",encoding="utf-8",errors="replace"):
    f=line.split()
    sep=f.index("-")
    mnt=f[4]
    if p==mnt or p.startswith(mnt.rstrip("/")+"/"):
        if best is None or len(mnt)>=len(best[0]):
            best=(mnt,f[5],f[sep+1],f[sep+2],f[sep+3])
mnt,opts,fstype,source,superopts=best
print("var_tmp_mount="+mnt+" fstype="+fstype+" source="+source)
print("var_tmp_mount_options="+opts)
print("var_tmp_super_options="+superopts)
s=os.statvfs(p)
avail=s.f_bavail*s.f_frsize
floor=4*1024**3
print("var_tmp_bytes_total=%d bytes_available=%d floor=%d" % (s.f_blocks*s.f_frsize,avail,floor))
print("var_tmp_inodes_total=%d inodes_free=%d inodes_available=%d" % (s.f_files,s.f_ffree,s.f_favail))
print("var_tmp_capacity="+("sufficient" if avail>=floor else "insufficient"))
sys.exit(0 if avail>=floor else 16)'
  status=$?
  printf 'S2.18d var-tmp-capacity exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -VV
  status=$?
  printf 'S2.19 python-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import pytest; print(pytest.__version__)'
  status=$?
  printf 'S2.20 pytest-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  command -v zstd gpgv rsync lscpu
  status=$?
  printf 'S2.21 required-tools exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  zstd --version
  status=$?
  printf 'S2.22 zstd-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  gpgv --version
  status=$?
  printf 'S2.23 gpgv-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /usr/share/keyrings/ubuntu-archive-keyring.gpg
  status=$?
  printf 'S2.24 keyring-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import os,sys
hits=sorted(n for n in os.listdir("/var/tmp") if n.startswith(sys.argv[1]))
print("run_prefix_entries="+(",".join(hits) if hits else "none"))
sys.exit(10 if hits else 0)' '<RUN>'
  status=$?
  printf 'S2.25 run-prefix-absent exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S2 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

Pass: block exit 0, with `S2.start`, `S2.end` and `S2 final exit=0` (§6.0);
S2.10 prints a positive `max_user_namespaces`; S2.11
prints the exact AppArmor value or the literal `absent` (recorded, not a gate;
a restriction that later prevents bubblewrap is a HARD STOP at step 5);
S2.18a prints `var_tmp=directory` with its mode, owner and group; S2.18b and
S2.18c print the `df` capacity and inode rows for `/var/tmp`; S2.18d prints
the mount point, filesystem type, source, mount and superblock options, the
byte and inode figures and `var_tmp_capacity=sufficient`; and S2.25 prints
`run_prefix_entries=none` for `/var/tmp`. Exit 15 (`/var/tmp` missing, a
link, not a directory or not its own real path) and exit 16 (less than 4 GiB
available) are each a **HARD STOP** before anything is created. If
`/usr/bin/bwrap`, `<PY>` with pytest, `zstd`, `gpgv`, `rsync`, `lscpu` or the
keyring is missing or fails, the block stops with that status: **HARD STOP** (§8.3). The executor must not
install, repair or substitute anything.

### Step 3 — confirm a qualifying variation (`oracle-test`, read-only)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S3.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S3.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S3 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S3.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S3.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S3.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import os,sys
release=os.uname().release
names=set()
for line in open("/proc/cpuinfo",encoding="utf-8",errors="replace"):
    key,sep,value=line.partition(":")
    if sep and key.strip()=="model name":
        names.add(value.strip())
print("HA-1 kernel_release="+release)
print("HA-2 model_names="+" | ".join(sorted(names)))
if len(names)!=1:
    print("HA-2 model name missing or not unique")
    sys.exit(21)
ha1=release!="6.8.0-139-generic"
ha2=names.isdisjoint({"AMD EPYC-Milan Processor","AMD EPYC-Milan"})
print("HA-1 qualifies="+("yes" if ha1 else "no"))
print("HA-2 qualifies="+("yes" if ha2 else "no"))
print("HA-3 qualifies=no (version-only differences do not qualify; section 4.2)")
sys.exit(0 if (ha1 or ha2) else 20)'
  status=$?
  printf 'S3.1 qualification exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S3 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

The executor also writes the HA-1 … HA-3 difference table against §3.4,
copying the S3.1 lines. Exit `20` is **INVALID RUN**: stop now, write the
handback (step 12), and create or provision nothing. Exit `21` or any other
nonzero status is a **HARD STOP**. On every exit, `r5_end` prints
`S3.end end_utc=…` and `S3 final exit=…` with the governing status, so an
INVALID RUN shows `S3 final exit=20` (§6.0). Pass: block exit 0, with
`S3.start`, `S3.end` and `S3 final exit=0`.

### Step 4 — unique directories, synchronization and controlled-checkout verification

**4a (`oracle-test`).** Create the directories:

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S4a.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S4a.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S4a final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S4a.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S4a.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4a.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  mkdir -m 0700 /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence
  status=$?
  printf 'S4a.1 mkdir exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence
  status=$?
  printf 'S4a.2 stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4a block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

`mkdir` without `-p` fails if any path already exists, which is a further
freshness proof.

**4b (repository host) — synchronization.** Step 4b is exactly three
invocations, in this order, with nothing issued between them: the S4b.start
timestamp block, the synchronization command, and the S4b.end timestamp block.

First, the S4b.start timestamp block:

```bash
/bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_block() {
  date -u '+S4b.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4b.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4b.start block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

If the S4b.start block exits nonzero, that is a **HARD STOP**: the
synchronization command and the S4b.end block are not run, and step 4b's end
is recorded as `not run`.

Only if it exits 0, run this one command, alone, exactly as written apart from
`<RUN>`:

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
  /opt/freedom-blades/platform/ oracle-test:/var/tmp/<RUN>-checkout/
```

This is the canonical secret-excluding procedure of
[`docs/operations/disposable-test-server.md`](../operations/disposable-test-server.md)
§3.2 (repeated in §4 item 2 there), with **one change only**: the destination
is the run's fresh path instead of the shared
`oracle-test:/opt/freedom-blades/platform/`. Every documented flag, every
exclusion, their single quoting and their order are unchanged, including
`--include='.env.example'` before `--exclude='.env*'`. It uses no
`--delete-excluded`, no exclusions file, no shell substitution, no redirection
and no chained command. It is one plain `rsync` invocation, the only shape the
repository secrets guard admits (operations document §3.2); `<RUN>` adds no
character outside `[a-z0-9-]`. `--delete` removes nothing, because the
destination was created empty in 4a. Any refusal by a guard is a stop
condition, not an obstacle: the executor must not rephrase the command.

This command is the one exception to the block convention, because the
admitted shape cannot be wrapped. Its exit status is the status of the
invocation itself, which the executor records directly, appending nothing to
the command line. Nonzero is a **HARD STOP**. The executor records the exit
status and rsync's two closing summary lines; the per-file list is not
evidence. With `-a`, rsync sets the destination directory's mode to that of
the source directory; this change is expected and recorded in 4d.

The two timestamp blocks are separate invocations. They do not prepend,
append, wrap, redirect or chain anything to the synchronization command, whose
bytes are exactly those above. The synchronization command's status remains
directly observable and governs step 4b.

Then, immediately after the synchronization command returns, **whatever its
status**, run the S4b.end timestamp block:

```bash
/bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_block() {
  date -u '+S4b.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4b.end date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4b.end block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

The S4b.end block is the only invocation permitted after a nonzero
synchronization status, and only so that step 4b's end is recorded. After it,
a nonzero synchronization status is a **HARD STOP** reported first and
governing, and a nonzero S4b.end status is also a **HARD STOP**. Step 4c runs
only if all three invocations exited 0.

**Transfer scope (disclosed).** The documented procedure transfers the working
tree, including `.git`, untracked files and ignored files that its list does
not exclude. On the preparation host those include `venv/`, `venv-web` and
`docs/screenshots/`, which `.gitignore` describes as maintainer browser
evidence that may show world, folder or Actor content. Every accepted
synchronization to `oracle-test` has had this scope; this assignment does not
change it. The executor must not open, list, read, copy or cite any of that
content; only the files named in §3.2 and the support files imported in step
10 are used. Narrowing the exclusion list would be a new policy decision that
this assignment does not make.

**4c (repository host) — repository state unchanged after the transfer.**

```bash
/bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S4c.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S4c.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S4c final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S4c.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S4c.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4c.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /opt/freedom-blades/platform
  status=$?
  printf 'S4c.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 python3 -I -B -c 'import subprocess,sys
paths=["infra","tests","tools","pytest.ini"]
r=subprocess.run(["git","status","--porcelain","--untracked-files=all","--"]+paths,capture_output=True,text=True)
sys.stdout.write(r.stdout)
sys.stderr.write(r.stderr)
if r.returncode:
    sys.exit(r.returncode)
print("repository_state="+("drift" if r.stdout else "clean"))
sys.exit(28 if r.stdout else 0)'
  status=$?
  printf 'S4c.2 repository-state exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum --strict -c <<'SUMS'
<APPENDIX A>
SUMS
  status=$?
  printf 'S4c.3 sha256sum-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4c block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

**4d (`oracle-test`) — exact-digest verification of the controlled checkout.**

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S4d.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S4d.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S4d final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S4d.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S4d.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4d.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-checkout
  status=$?
  printf 'S4d.1 checkout-stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S4d.2 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum --strict -c <<'SUMS'
<APPENDIX A>
SUMS
  status=$?
  printf 'S4d.3 sha256sum-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c '<the S1.6 program, verbatim>' <<'LIST'
<APPENDIX B>
LIST
  status=$?
  printf 'S4d.4 hashlib-and-tree-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4d block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

Pass (4a–4d): every block and the rsync command exit 0, which for the step
blocks includes `S4a`, `S4c` and `S4d` `.start`, `.end` and `final exit=0`,
and for 4b includes `S4b.start block exit=0` and `S4b.end block exit=0`
(§6.0); S4c.2 prints
`repository_state=clean`; S4d.3 prints `OK` for all 28 files; and S4d.4
prints `OK` for all 28, `rows 28 mismatches 0` and
`launcher_tree files 22 dirs 5`. S4d.1 shows the checkout directory with the
source directory's mode. `prepare_checkout` copies the whole of
`infra/rp11-launch/` except `__pycache__`, so S4d.4's exact tree check is what
proves that the build sees only the pinned launcher files.

### Step 5 — fresh provisioning from the signed snapshot and accepted lock only (`oracle-test`)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S5.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S5.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S5 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S5.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S5.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S5.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S5.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 <PY> -B infra/rp11-launch/buildroot/provision.py resolve --snapshot 20261001T000000Z --suite resolute --cache /var/tmp/<RUN>-index > /var/tmp/<RUN>-evidence/resolve.out
  status=$?
  printf 'S5.2 resolve exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  grep '^package=' infra/rp11-launch/toolchain.lock > /var/tmp/<RUN>-evidence/lock-packages.txt
  status=$?
  printf 'S5.3 lock-package-lines exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cmp /var/tmp/<RUN>-evidence/resolve.out /var/tmp/<RUN>-evidence/lock-packages.txt
  status=$?
  printf 'S5.4 resolve-equals-lock exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 <PY> -B infra/rp11-launch/buildroot/provision.py install --lock infra/rp11-launch/toolchain.lock --root /var/tmp/<RUN>-root --cache /var/tmp/<RUN>-cache
  status=$?
  printf 'S5.5 install exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import hashlib,os,sys
lock=[l.split() for l in open(sys.argv[1],encoding="utf-8") if l.startswith("package=")]
want={os.path.basename(f):s for _n,_v,s,f in lock}
have=sorted(os.listdir(sys.argv[2]))
bad=0
for n in have:
    p=os.path.join(sys.argv[2],n)
    d=hashlib.sha256(open(p,"rb").read()).hexdigest() if os.path.isfile(p) and not os.path.islink(p) else "not-a-regular-file"
    ok=want.get(n)==d
    bad+=not ok
    print(d,n,"OK" if ok else "UNEXPECTED")
missing=sorted(set(want)-set(have))
for n in missing:
    print("missing",n)
print("cache_entries",len(have),"lock_packages",len(want),"unexpected",bad,"missing",len(missing))
sys.exit(29 if (bad or missing or len(have)!=62 or len(want)!=62) else 0)' infra/rp11-launch/toolchain.lock /var/tmp/<RUN>-cache
  status=$?
  printf 'S5.6 cache-accounting exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 <PY> -B infra/rp11-launch/buildroot/enter.py ldconfig --root /var/tmp/<RUN>-root
  status=$?
  printf 'S5.7 ldconfig exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-root
  status=$?
  printf 'S5.8 root-stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S5 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

**The `resolve` signature gate (normative).** `provision.py resolve` is the
repository's only implemented archive-signature check. Its contract, as
written: it fetches `InRelease` into `/var/tmp/<RUN>-index`, runs the host's
`gpgv` against the host's Ubuntu archive keyring with `check=True` (a bad or
missing signature, keyring or `gpgv` raises and exits nonzero), checks
`Packages.xz` against the signed `InRelease` digest (a mismatch exits
nonzero), computes the closure of the fixed seed set, and prints one
`package=<name> <version> <SHA-256> <pool path>` line per package in name
order. The lock's 62 `package=` lines have exactly that format and order. The
gate is therefore fail-closed: any signature, index or closure failure stops
S5.2, and S5.4 requires the signed closure to be byte-equal to the lock's
lines, so every package digest that `install` then enforces is one the signed
index lists. `install` verifies each package file against the lock's SHA-256
before unpacking it and does not recheck the signature.

Pass: block exit 0, with `S5.start`, `S5.end` and `S5 final exit=0` (§6.0);
S5.6 prints `cache_entries 62 lock_packages 62 unexpected 0
missing 0`; S5.8 shows mode `755`. The only network traffic is HTTPS to
`https://snapshot.ubuntu.com/ubuntu/20261001T000000Z/`.

### Steps 6 and 7 — same-invocation R-1 gate, unprivileged R-2, and root checks (`oracle-test`, one block)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S6-S7.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S6-S7.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S6-S7 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S6-S7.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S6-S7.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S6-S7.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S6.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 <PY> -B infra/rp11-launch/buildroot/enter.py build --root /var/tmp/<RUN>-root --work /var/tmp/<RUN>-work --variant r2 --manifest-out /var/tmp/<RUN>-evidence/regenerated.manifest > /var/tmp/<RUN>-evidence/build.stdout 2> /var/tmp/<RUN>-evidence/build.stderr
  build_status=$?
  printf 'S6.2 enter-build exit=%s\n' "$build_status"
  cat /var/tmp/<RUN>-evidence/build.stdout /var/tmp/<RUN>-evidence/build.stderr
  display_status=$?
  printf 'S6.3 display exit=%s\n' "$display_status"
  if [ "$build_status" -ne 0 ]; then exit "$build_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
  grep -Fxq 'r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal' /var/tmp/<RUN>-evidence/build.stdout
  status=$?
  printf 'S6.4 gate-line-present exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  grep -Fxq 'exit 0' /var/tmp/<RUN>-evidence/build.stdout
  status=$?
  printf 'S6.5 r2-exit-line-present exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cmp /var/tmp/<RUN>-evidence/regenerated.manifest /var/tmp/<RUN>-checkout/infra/rp11-launch/build-root.manifest
  status=$?
  printf 'S7.1 manifest-cmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /var/tmp/<RUN>-evidence/regenerated.manifest
  status=$?
  printf 'S7.2 manifest-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  preload=/var/tmp/<RUN>-root/etc/ld.so.preload
  if [ -e "$preload" ] || [ -L "$preload" ]; then
    printf 'ld_so_preload=present\n'
    status=11
  else
    printf 'ld_so_preload=absent\n'
    status=0
  fi
  printf 'S7.3 ld-so-preload-absent exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import os,sys
nonempty=False
for d in sys.argv[1:]:
    if os.path.islink(d) or not os.path.isdir(d):
        print("missing_or_not_directory="+d)
        sys.exit(13)
    entries=sorted(os.listdir(d))
    print(d+" entries="+(",".join(entries) if entries else "none"))
    nonempty=nonempty or bool(entries)
sys.exit(12 if nonempty else 0)' /var/tmp/<RUN>-root/tmp /var/tmp/<RUN>-root/var/tmp
  status=$?
  printf 'S7.4 root-tmp-empty exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S6-S7 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

In S6.2 and S6.3 the `enter.py build` status governs: it is captured first,
and the display status is checked only if the build status is 0.

One `enter.py build` invocation runs `run_gated_build`. It regenerates the
manifest inside the read-only entered root with the pinned `find` and
`sha256sum`, and requires byte equality with the checkout's committed
`build-root.manifest`; on any difference it exits 1 before preparing a
checkout. Only on equality does it prepare `co-r2` and start the R-2 vector as
the first process in the root, as sandbox uid/gid 1000, from an unprivileged
outer user, without `sudo`. Its exit status is R-2's. The original run's split
orchestration (`enter.py manifest`, then a separate `enter.py build`) is
**forbidden**. `enter.py manifest` and `enter.py ic1` are not run as separate
steps.

Pass: block exit 0, with `S6-S7.start`, `S6-S7.end` and `S6-S7 final exit=0`
(§6.0); S6.4 and S6.5 find the gate line
`r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal`
and `exit 0`; S7.1 is silent; S7.3 prints `ld_so_preload=absent`; S7.4 prints
`entries=none` for both directories.

### Step 8 — R-3 exact comparison of the four normative outputs (`oracle-test`)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S8.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S8.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S8 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S8.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S8.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S8.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-work/co-r2/build-out
  status=$?
  printf 'S8.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum --strict -c /var/tmp/<RUN>-checkout/infra/rp11-launch/expected.sha256
  status=$?
  printf 'S8.2 expected-sha256-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c 'import hashlib,sys
rows=[l.split("  ",1) for l in sys.stdin.read().splitlines()]
bad=0
for want,name in rows:
    got=hashlib.sha256(open(name,"rb").read()).hexdigest()
    ok=got==want
    bad+=not ok
    print(got,name,"OK" if ok else "MISMATCH")
c=open("cc1.v","rb").read()
print(hashlib.sha256(c).hexdigest(),len(c),"cc1.v diagnostic, judged in step 9")
if bad or len(rows)!=4:
    sys.exit(30)
out=open(sys.argv[1],encoding="utf-8",errors="replace").read().splitlines()
missing=[w+"  "+n for w,n in rows if w+"  "+n not in out]
for m in missing:
    print("missing_from_build_stdout",m)
sys.exit(31 if missing else 0)' /var/tmp/<RUN>-evidence/build.stdout <<'OUTPUTS'
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  rp11-launch
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  rp11-launch.x86_64.listing
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d  rp11-launch.map
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706  launch.s
OUTPUTS
  status=$?
  printf 'S8.3 independent-output-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cmp /var/tmp/<RUN>-work/co-r2/build-out/rp11-launch.x86_64.listing /var/tmp/<RUN>-checkout/infra/rp11-launch/rp11-launch.x86_64.listing
  status=$?
  printf 'S8.4 listing-cmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S8 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

Pass: block exit 0, with `S8.start`, `S8.end` and `S8 final exit=0` (§6.0);
S8.2 reports all four `OK`; S8.3 reports all four `OK`
and finds each digest line in `build.stdout`; S8.4 is silent.

### Step 9 — exact `cc1.v` comparison (`oracle-test`)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S9.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S9.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S9 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S9.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S9.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S9.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%s' /var/tmp/<RUN>-work/co-r2/build-out/cc1.v
  status=$?
  printf 'S9.1 cc1v-length exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S9.2 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 <PY> -B infra/rp11-launch/verify/cc1check.py infra/rp11-launch/verify/fixtures/cc1.v.baseline /var/tmp/<RUN>-work/co-r2/build-out/cc1.v > /var/tmp/<RUN>-evidence/cc1check.out 2> /var/tmp/<RUN>-evidence/cc1check.err
  check_status=$?
  printf 'S9.3 cc1check exit=%s\n' "$check_status"
  cat /var/tmp/<RUN>-evidence/cc1check.out /var/tmp/<RUN>-evidence/cc1check.err
  display_status=$?
  printf 'S9.4 display exit=%s\n' "$display_status"
  if [ "$check_status" -ne 0 ]; then exit "$check_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
  printf 'S9 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

`cc1check.py` exits 0 only for byte-identical inputs (`PASS`), 1 for any
difference (`HARD_STOP`) and 2 for a missing or unreadable input. Its status
governs; the display status is checked only after it.

Pass, and the **only** route to PASS: block exit 0, with `S9.start`, `S9.end`
and `S9 final exit=0` (§6.0); S9.1 prints `5120`; and
the output shows `verdict:         PASS`, `is_identical:    True` and actual
SHA-256 `b77f92dc…905b`. Any other result is a **HARD STOP**. The executor
reports the whole `cc1check.out`, including every differing offset, length
and byte value. It does not explain a difference away, label it, or rerun to
get a different result.

### Step 10 — accepted corroborating toolchain tests against the fresh root (`oracle-test`)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S10.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S10.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S10 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S10.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S10.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S10.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S10.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  env -u TEST_DATABASE_URL RP11_LAUNCH_BUILD_ROOT=/var/tmp/<RUN>-root PYTHONDONTWRITEBYTECODE=1 <PY> -B -m pytest -q -rs -p no:cacheprovider --basetemp=/var/tmp/<RUN>-pytest --junitxml=/var/tmp/<RUN>-evidence/pytest.junit.xml tests/test_rp11_launch_toolchain.py > /var/tmp/<RUN>-evidence/pytest.out 2>&1
  pytest_status=$?
  printf 'S10.2 pytest exit=%s\n' "$pytest_status"
  cat /var/tmp/<RUN>-evidence/pytest.out
  display_status=$?
  printf 'S10.3 display exit=%s\n' "$display_status"
  if [ "$pytest_status" -ne 0 ]; then exit "$pytest_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
  <PY> -I -B -c 'import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
suite=root if root.tag=="testsuite" else root.find("testsuite")
counts={k:int(suite.get(k,"-1")) for k in ("tests","failures","errors","skipped")}
print(" ".join(k+"="+str(v) for k,v in counts.items()))
sys.exit(0 if counts=={"tests":12,"failures":0,"errors":0,"skipped":0} else 32)' /var/tmp/<RUN>-evidence/pytest.junit.xml
  status=$?
  printf 'S10.4 pytest-counts exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S10 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

Pass: block exit 0, with `S10.start`, `S10.end` and `S10 final exit=0`
(§6.0), and S10.4 as below.

pytest exits 0 even when tests skip, so S10.4 checks the counts mechanically:
`tests=12 failures=0 errors=0 skipped=0`. The 12 are R-1, T-L5, T-L6 × 3
(R-4(a)/(b)/(c)), T-L7, T-L9, T-L11, IC-1 × 2 (`r2`, `r4a-path`), the IC-1
driver derivation and T-L8. A skip is not a pass. `TEST_DATABASE_URL` is
explicitly unset: this module has no database dependency, and AGENTS.md's
80-skip figure applies to the web suite, not here. The executor reports every
warning verbatim. The two known pytest-asyncio configuration warnings are
expected. Any other warning goes to review, and a warning reporting a
skipped, failed or unrun check is a HARD STOP. These tests corroborate the
current tree. They do not change the R-1 … R-3 pass condition.

### Step 11 — evidence capture and digest accounting (`oracle-test`, read-only)

```bash
ssh oracle-test /bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_end() {
  block_status=$?
  date -u '+S11.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S11.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S11 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S11.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S11.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S11.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S11.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum --strict -c <<'SUMS'
<APPENDIX A>
SUMS
  status=$?
  printf 'S11.2 sha256sum-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  <PY> -I -B -c '<the S1.6 program, verbatim>' <<'LIST'
<APPENDIX B>
LIST
  status=$?
  printf 'S11.3 hashlib-and-tree-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /var/tmp/<RUN>-evidence/* /var/tmp/<RUN>-work/co-r2/build-out/*
  status=$?
  printf 'S11.4 evidence-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence /var/tmp/<RUN>-pytest
  status=$?
  printf 'S11.5 stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  du -s /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence /var/tmp/<RUN>-pytest
  status=$?
  printf 'S11.6 du exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u +%Y-%m-%dT%H:%M:%SZ
  status=$?
  printf 'S11.7 date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  uname -srvm
  status=$?
  printf 'S11.8 uname exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  awk '/^processor/{n++} n==1 && /^(vendor_id|cpu family|model|model name|stepping|microcode|flags)[[:space:]]*:/' /proc/cpuinfo
  status=$?
  printf 'S11.9 cpuinfo-first-processor exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /usr/bin/bwrap --version
  status=$?
  printf 'S11.10 bwrap-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /usr/bin/bwrap
  status=$?
  printf 'S11.11 bwrap-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S11 block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

Pass: block exit 0, with `S11.start`, `S11.end` and `S11 final exit=0`
(§6.0); S11.2 and S11.3 show the checkout unchanged; and the
lines printed by S11.8, S11.9, S11.10 and S11.11 are byte-equal to those of
S2.2, S2.5, S2.6 and S2.8. Any difference is an unexplained environmental
difference and a **HARD STOP**.

### Step 12 — handback, then immediate stop

Write the handback (§10) and stop. Do not clean up, rerun, remediate, commit,
push or start any follow-on step. After a HARD STOP or an INVALID RUN at any
step, no later step runs, step 11 included, with two exceptions only: the
S4b.end block where step 4b's synchronization command was invoked (step 4b),
and step 12 itself. The handback is written from the transcripts already
recorded.

Step 12 is exactly three actions, in this order, on the repository host, with
nothing issued between them.

**12a — the S12.start timestamp block.** Run it immediately after the last
invocation of the run: step 11's block on a complete run; otherwise the
invocation that stopped the run, or the S4b.end block where that applies.

```bash
/bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_block() {
  date -u '+S12.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S12.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S12.start block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

A nonzero S12.start status is a **HARD STOP**. It is recorded in the
handback, and 12b and 12c still follow, so that the handback exists and is
closed.

**12b — the handback body.** Complete the handback file, which already holds
the §2 attestation, with items 1–16 of §10. The body embeds every transcript
through the S12.start block. It must not contain a heading named
`Closing record`. Where §10 item 2 needs the step-12 end and whole-run end
values, the body writes the literal text `in closing record`. Before 12c begins, the executor
confirms by reading the body that it reproduces every S1.3 line and that
their number equals `git_status_lines` (§10 item 3); this is a reading, not a
command. Once 12c begins, the body is final: neither the executor nor anyone
else edits any earlier transcript or line of the handback.

**12c — the S12.end block, which closes the handback.** It checks that the
handback body exists, then appends a closing record to it. From one clock
reading the closing record holds the step-12 end value and the whole-run end
value. The executor therefore never copies a timestamp into the handback by
hand, and nothing is edited after the final timestamp is taken.

```bash
/bin/bash --noprofile --norc -s <<'R5BLOCK'
r5_close() {
  printf '\n## Closing record (written by the S12.end block)\n\n~~~text\n'
  status=$?
  printf 'S12.end.3 open-record exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then return "$status"; fi
  date -u '+S12.end end_utc=%Y-%m-%dT%H:%M:%SZ%nRUN.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S12.end.4 date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then return "$status"; fi
  printf '~~~\n'
  status=$?
  return "$status"
}
r5_block() {
  cd /opt/freedom-blades/platform
  status=$?
  printf 'S12.end.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  if [ -f '<HANDBACK>' ] && [ ! -L '<HANDBACK>' ]; then
    printf 'handback_body=present\n'
    status=0
  else
    printf 'handback_body=missing\n'
    status=33
  fi
  printf 'S12.end.2 handback-body-present exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  r5_close >> '<HANDBACK>'
  status=$?
  printf 'S12.end.5 closing-record exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S12.end block exit=0\n'
  exit 0
}
r5_block </dev/null
R5BLOCK
```

All output of `r5_close` goes only into the handback. S12.end.1, S12.end.2,
S12.end.5 and the block line go to the terminal. On success the handback ends
with exactly this closing record, where each `<UTC>` is one value in the §6.0
format and the two values are equal:

```text

## Closing record (written by the S12.end block)

~~~text
S12.end.3 open-record exit=0
S12.end end_utc=<UTC>
RUN.end end_utc=<UTC>
S12.end.4 date exit=0
~~~
```

After the one `date` reading that gives `S12.end` and `RUN.end`, the only
things that happen are this block's own status lines, the closing fence and
`exit`. **The executor then stops at once.** It issues no further command and
makes no further edit to the handback, whatever the S12.end status. It may
quote the block's terminal transcript in its reply to the maintainer, but
never in the handback.

Pass: S12.start and S12.end each exit 0, printing `S12.start block exit=0`,
`S12.end.5 closing-record exit=0` and `S12.end block exit=0`, and the handback
ends with the closing record exactly as shown. A handback that does not end
with that exact record is a **HARD STOP** for missing evidence (§8.3),
whatever its body says. The reviewer checks this from the file. Exit 33 means
the body was missing.

## 7. Minimum host actions authorized after acceptance (named executor only)

Only the twelve step blocks, the four timestamp blocks and the single
synchronization command in §6 are authorized. Each runs once, in the order of
§6, together with the `ssh oracle-test` transport that delivers the
`oracle-test` blocks. In summary:

* **Repository host:** the read-only step blocks of steps 1 and 4c (Git
  state, digests, the in-memory review manifest, tool presence); the S4b.start
  and S4b.end timestamp blocks; one `rsync` invocation of step 4b; the
  S12.start timestamp block; writing the single handback file (the §2
  attestation before step 1 and the body in step 12b); and the S12.end block,
  whose only write is to append the closing record to that file. Nothing is
  created under the repository host's `/tmp` or `/var/tmp`.
* **`oracle-test`:** the read-only observation blocks of steps 2, 3 and 11,
  including the `/var/tmp` preflight of S2.18a–S2.18d;
  creation of the `/var/tmp/<RUN>-*` directories (step 4a); receipt of the
  synchronized tree (step 4b); `provision.py resolve` and `install`, and
  `enter.py ldconfig` and `build`, with unprivileged bubblewrap and HTTPS to
  the pinned snapshot only; the `cmp`, `grep`, `sha256sum`, `stat`, `cat`,
  `du`, `df` and Python checks written in the blocks; `cc1check.py`; and one pytest
  invocation of `tests/test_rp11_launch_toolchain.py`.
* **Timestamps, on both hosts:** only the `date -u` commands written in the
  blocks. These are the `trap r5_end EXIT`, start `date` and `r5_end` end
  `date` of each step block, and the `date` of each timestamp block (§6.0,
  "Timestamps"). They are the only authorized source of every required
  timestamp.

Any other command, or any change to a block's text beyond §6.0's
substitutions, is an **unexpected command** and a HARD STOP. That includes
any additional or substitute timestamp command, any wrapper or prefix around
the synchronization command, and any edit to the handback after the S12.end
block begins.

### 7.1 The active one-run banner

Peter Duscha accepted this assignment after independent review and activated
Gemini for the single run described here. The corresponding restriction banner
in `docs/operations/disposable-test-server.md` grants no ambient access or
repair authority and expires when the run stops for PASS, INVALID RUN or HARD
STOP and its handback is closed. The executor edits no authority, governance
or current-state document.

### 7.2 Forbidden unless separately justified and accepted

* installation, upgrade, removal or downgrade of any host package, including
  `bubblewrap`, `rsync`, `zstd`, `gpgv`, keyrings, Python or pytest;
* any `sudo` or privileged command;
* persistent host configuration, sysctl, AppArmor or user changes;
* service, PostgreSQL or database actions, or the platform bot/web suites;
* access to production or staging hosts or data, Discord, Sheets or Foundry;
* installation of `rp11-launch`, RP-11 wiring, or pass-configuration changes;
* H-1, H-2, D9-4, D9-5, PO-14, PO-17 or PO-18 discharge, or any evidence band;
* the evidence harness with `--execute`, a controlled write or an operational
  path;
* reboot;
* reading, scanning or copying secrets or protected artifacts, or opening any
  non-controlled content that the synchronization carries (§6 step 4b);
* use of or changes to `oracle-test:/opt/freedom-blades/platform`;
* commit, push, staging or any Git-history modification;
* edits to any repository file other than the single handback; and
* **any second run, partial rerun, retry or remediation after a stop.**

If a prerequisite such as `bubblewrap`, unprivileged user namespaces, the
pinned Python environment, pytest, `rsync`, `zstd`, `gpgv`, the archive
keyring, network reachability of the snapshot or disk space is unavailable,
the executor **stops and reports**. This assignment grants no ambient
authority to repair it. The 2026-10-01 `bubblewrap` installation authority was
consumed by the earlier run and is not inherited. The 2026-10-03 inspection
and cleanup authority was Codex's, was exhausted by the recorded cleanup and
is not inherited: the executor deletes, cleans or frees nothing, on `/tmp`,
`/var/tmp` or anywhere else.

## 8. Verdicts

The verdict is exactly one of the following. Precedence: HARD STOP over
INVALID RUN over PASS.

### 8.1 PASS

All of these hold:

1. the named executor's independence attestation (§2) is complete;
2. every block and the synchronization command of §6 ran in order, once, and
   each exited 0 with its stated pass output;
3. every one of the fifteen timed scopes of §6.0 has its start and end value,
   each printed by its authorized command with status 0, and the handback ends
   with the exact closing record of §6 step 12;
4. HA-1 or HA-2 qualified under §4.2 (HA-3 cannot qualify in this run), and
   the start and end observations agree (step 11);
5. the same-invocation R-1/R-2 gate passed, and the regenerated manifest is
   byte-equal to the committed one;
6. all four normative outputs match `expected.sha256`, and the listing is
   byte-equal to the committed listing;
7. `cc1.v` is byte-identical to the accepted baseline (`cc1check.py`
   `PASS`);
8. the corroborating tests report 12 tests, 0 failures, 0 errors and 0
   skipped; and
9. no unexplained difference remains.

A PASS is a recommendation input for Codex and Peter. It is not R-5
acceptance.

### 8.2 INVALID RUN

Step 3 exits `20`: neither HA-1 nor HA-2 qualified, even if every byte would
have matched. The run is not R-5 and does not pass.

### 8.3 HARD STOP

Any nonzero status other than step 3's `20`, from a block or from the
synchronization command, and in particular: an input digest, count or tree
mismatch; repository-state drift; a missing or failed prerequisite, including a
`/var/tmp` preflight failure (status 15 or 16) or a write failure for lack of
space or quota; a
provisioning, signature, package or cache discrepancy; a failed or reordered
gate; a manifest, output, listing, `cc1.v` or test difference; a skip,
failure or error; missing evidence, including a failed, missing or malformed
required timestamp or a missing or malformed closing record (§6.0, §6 step
12); an unexpected command; any need for
privilege; a guard refusal; or any unexplained environmental difference. The
executor stops at the first one and does not continue to later steps, apart
from the S4b.end block and step 12 (§6 step 12).

**Manual adjustment is forbidden.** No one may edit, regenerate, substitute or
normalize the fixture, `expected.sha256`, `toolchain.lock`,
`build-root.manifest`, launcher source, the listing, a verifier, a test or any
generated output to obtain a PASS. No one may compare against any other
baseline or relabel a difference.

## 9. What a result does and does not show

R-5 can show only that the pinned root produced the same bytes on the variants
tested (D2 §5.3.8). It does not eliminate HA-1 … HA-5 or TD-1 … TD-4. It does
not test a different toolchain or show decoder correctness, and it does not
discharge PO-9 as a whole, PO-14, D9-3 by itself, H-1 or RP-11 readiness.

## 10. Handback contract

Write exactly one new file,
`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`
*(path confirmed or replaced in the acceptance record; §12)*, containing:

1. the executor's identity and the §2 independence attestation, including the
   Gemini clause where it applies;
2. start and end UTC timestamps for the whole run and for each step, where
   "each step" means each timed scope of §6.0 and nothing finer: a table with
   one row per scope (whole run; steps 1, 2, 3, 4a, 4b, 4c, 4d, 5, 6/7
   combined, 8, 9, 10, 11 and 12), giving the producing label, the host and
   the exact `start_utc`/`end_utc` line and status line copied from the
   transcript. The rows for the step-12 end and the whole-run end say
   `in closing record`, because the S12.end block writes those values into the
   handback itself (§6 step 12). A scope that did not start says `not run`,
   and an end value that was not printed says `absent`, with the invoking
   shell's status. No value is supplied from any other source;
3. repository state: the commit; the **complete** S1.3 output, every line of
   `git status --short --untracked-files=all` reproduced verbatim and in
   order, followed by its `git_status_lines` and `git_status_sha256` lines;
   the S1.4 and S4c.2 results; the S1.5, S1.6, S4c.3, S4d.3 and S4d.4
   results; and the in-memory review-manifest result. The S1.3 lines are
   never summarized or abbreviated. The number of reproduced lines must equal
   `git_status_lines`, and the SHA-256 of those lines, each followed by one
   newline, must equal `git_status_sha256`; the reviewer recomputes both from
   the handback. A handback that fails either check is **missing evidence**
   (§8.3);
4. the step-2 HA-1 … HA-5 observations, the end-of-run observations, the
   diagnostic context of §4.4 including the S2.18a–S2.18d `/var/tmp`
   preflight, the S3.1 output and the HA-1 … HA-3 difference
   table naming the qualifying variation;
5. every created path with its mode, owner and group at creation and at the
   end, and its size;
6. every block, including the S4b.start, S4b.end and S12.start timestamp
   blocks, and the synchronization command, exactly as run and in order, with
   each block's final exit status. The S12.end block is evidenced by its
   closing record;
7. the synchronization command's exit status and summary lines; the download
   source; the `resolve` result; and the S5.6 cache accounting;
8. same-invocation R-1/R-2 evidence: `build.stdout` and `build.stderr`
   verbatim, the gate line, the regenerated manifest digest, the `cmp`
   result, `ld.so.preload` absence, and the emptiness of the build root's own
   `/tmp` and `/var/tmp` (S7.4);
9. all normative output digests and byte-comparison results;
10. the `cc1.v` length, both SHA-256 values, the complete `cc1check.py`
    output and its verdict;
11. the complete pytest output, the S10.4 counts, every warning and the
    summary line;
12. every stopped, invalid or unexplained condition, quoting the first one
    exactly, with its status;
13. retained evidence locations and their digests, under §10.1. **Cleanup
    state:** nothing is deleted; everything stays in place pending review and
    Peter's direction. The handback must state honestly that the repository
    working tree was synchronized into `/var/tmp/<RUN>-checkout`, that
    directories were created under `/var/tmp`, and that `oracle-test`'s
    `/var/tmp` changed. It must not say the host was left in its pre-run state
    (lesson of `R5-R1-1`);
14. the verdict (PASS, INVALID RUN or HARD STOP), with each §8.1 condition
    answered separately. For condition 3, the step-12 end, the whole-run end
    and the closing record are answered `in closing record`. The verdict of
    record is HARD STOP if the handback does not end with the exact closing
    record (§6 step 12);
15. an explicit statement that RP-11 remains unwired and unmet, that
    `plan.is_executable=False`, that PO-9 and PO-14 remain open, that Package
    5.0 is not ready, and that no installation, operational, harness
    `--execute`, privileged, commit or push authority was exercised; and
16. an immediate stop pending Codex's independent review and Peter's
    decision, which follows the S12.end block (§6 step 12).

### 10.1 Evidence retention (normative)

Review must not depend on `oracle-test:/var/tmp` surviving. Therefore:

1. **The handback is the evidence of record.** It embeds verbatim every block
   transcript, including every `exit=` line and every `start_utc=`,
   `end_utc=` and `final exit=` line, with two exceptions. For the
   synchronization command, only the exit status and rsync's closing summary
   lines are embedded, not the per-file list. For the S12.end block, the
   closing record that the block appends is the evidence; its terminal lines
   are not copied in, because the body is final before the block runs (§6
   step 12).
2. Every evidence file whose content a verdict depends on is embedded
   verbatim: `build.stdout`, `build.stderr`, `cc1check.out`, `cc1check.err`
   and `pytest.out`. The S5.6 output is embedded as printed. Files whose
   content is fully determined by a passing byte comparison or count
   (`resolve.out`, `lock-packages.txt`, `regenerated.manifest`,
   `pytest.junit.xml`) are recorded by SHA-256 from S11.4 together with that
   comparison's result.
3. The run's `/var/tmp/<RUN>-*` directories on `oracle-test` are **retained
   unchanged** as supplementary evidence until Peter directs otherwise. The
   executor deletes nothing and promises no retention period. Loss of those
   directories after the handback does not change a verdict recorded under
   items 1 and 2.
4. No evidence is copied back to the repository host or committed, and no
   other evidence bundle is created.

## 11. Stop gate

After the handback, the executor stops. R-5 is accepted, or D9-3 treated as
complete, only after Codex independently reviews the handback and Peter
Duscha records an explicit decision. This assignment authorizes neither in
advance.

## 12. Disposition of preparation-time open items

No item below is open for the executor, and none affects execution safety,
independence, admissibility, PASS eligibility, transport security or evidence
availability.

| Former item | Disposition in this assignment |
|---|---|
| U-1 `cc1.v` GGC host input | diagnostic context only (§4.4); exact mismatch is a HARD STOP; no GGC-only exception |
| U-2 `resolve` signature gate | confirmed against `provision.py` as written and fail-closed; retained (§6 step 5) |
| U-3 no reference CPU feature list | normative: HA-2 qualifies only on a different `model name` (§4.2) |
| U-4 HA-3 version-only | resolved: does not qualify; HA-3 cannot qualify in this run (§4.2) |
| U-5 checkout transport | resolved: `git archive` transport removed; the documented secret-excluding `rsync` with only the destination changed (§6 step 4b) |
| U-6 evidence retention | resolved by the explicit rule of §10.1 |
| U-7 identifiers | **confirmed:** execution work ID `C-P5.0-R5-RP11-FRESH-R5-R3`; handback and `<HANDBACK>` path `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`. The predecessor's identifiers `C-P5.0-R5-RP11-FRESH-R5` and `…-rebuild-handback.md` are consumed and must not be reused |
| U-8 governance documents | outside the executor's authority; recorded by the maintainer or a separately assigned agent (§7.1) |
| U-9 tree movement during preparation | historical drafting context only (preparation handback §6); this assignment binds exact bytes (§3.2), not the preparation-time commit |
| U-10 run-resource location | resolved: outer-host run resources under `/var/tmp/<RUN>-*`, with the S2.18a–S2.18d preflight and a 4 GiB floor; the build root's own `/tmp` and `/var/tmp` are unchanged (§5) |
| U-11 `FRESH-R5-HS-1` | closed prospectively for this run only: S1.3 prints the complete `git status --short --untracked-files=all` output with its line count and digest, and the handback must reproduce it (§6 step 1, §10 item 3). The finding stays open and attached to the closed predecessor handback, which is not edited |
| U-12 per-user quota | disclosed residual: per-user quota headroom on `/var/tmp` is not observable without privilege, and no `quota` tool is installed. Mount options are recorded (S2.18d); a write failure remains a HARD STOP (§5) |

## 13. Resolved Gemini invocation

Under `.agents/AGENTS.md` ("Gemini assignment invocation"), the activator hands
this assignment to Gemini with exactly this invocation. It is resolved here so
that it can be copied without interpretation:

```text
/goal Execute the active assignment in docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md. Proceed autonomously through every authorized step in order until the defined terminal state (PASS, INVALID RUN, or HARD STOP). Do not post intermediate progress updates, do not yield turns for user confirmation on background tasks, and do not stop until the final handback and closing record are fully written.
```

The acceptance record activates this invocation for Gemini's one run. It
prevents conversational pauses only. It does not broaden the assignment,
authorize an omitted command, suppress a genuine tool-permission prompt, or
permit a retry, remediation or cleanup, and it overrides no HARD STOP. At the
first terminal state (PASS, INVALID RUN or HARD STOP) Gemini writes the
complete handback and closing record (§6 step 12, §10) and stops.

## Appendix A — §3.2 digests in `sha256sum --check` format (28 lines)

```text
f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf  infra/rp11-launch/toolchain.lock
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f  infra/rp11-launch/build-root.manifest
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625  infra/rp11-launch/expected.sha256
b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b  infra/rp11-launch/verify/fixtures/cc1.v.baseline
c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c  docs/review/phase-5-0-evidence-harness-review-manifest.json
f02b7acfa14b1c108ab53942bd3f89a9bd629eccb6c2c685419e07bf729dec3d  docs/review/phase-5-0-evidence-harness-concrete-plan.md
7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0  infra/rp11-launch/build.sh
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe  infra/rp11-launch/launch.c
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b  infra/rp11-launch/select.h
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139  infra/rp11-launch/start.s
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326  infra/rp11-launch/rp11-launch.ld
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  infra/rp11-launch/rp11-launch.x86_64.listing
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300  infra/rp11-launch/buildroot/provision.py
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a  infra/rp11-launch/buildroot/enter.py
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72  infra/rp11-launch/verify/cc1check.py
ea7d9dd3d8e141349019cfdeba5e91df7569e28d6818136777f59bf313316917  infra/rp11-launch/verify/ic1check.py
b742552c6d200dd1c0536f29a444dcc4a00405f758788bc82c8b2c4f2df2aceb  infra/rp11-launch/verify/elfcheck.py
cb1b8d835983b625e8e42dda2d46aa2d5e56816cf90fb8c3a397e291c3d0e676  infra/rp11-launch/verify/tl11.py
eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31  infra/rp11-launch/verify/ctverify.py
84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97  infra/rp11-launch/verify/xdecode.py
d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66  infra/rp11-launch/verify/xdecode-spelling.table
f0e811a4bd61782789b66f31ab4401797e52b8ac00ffeebb984bfcd71afb4a8a  infra/rp11-launch/verify/xdecode-corpus.txt
603099e0f7279e4158023a63b6bc1411c0d9d3ac7c9372c7f77fa9d42f0b0a94  infra/rp11-launch/test-harness/select_harness.c
8c4ad99c0a1f3452923dab46149e7f4b202060ef5bf981b732ec9e9724dd91fd  infra/rp11-launch/test-harness/select_shim.c
ff3d458cabae91512562cca6143542337b1306dc3df791da505c51a9519ab76f  tests/test_rp11_launch_toolchain.py
bc24c0ee7b0c9f58853479adc908c60cf013b9652409e3d5cee0d710074a18b6  tests/rp11_launch_support.py
5a2f4694983619d6a3fb7ac3965e4415dd114fb7504003d91abb6071d189c2b1  tools/phase_5_0_evidence/rp11_launch.py
311f1d0300e3e98f5b3b33ea6c4598bfc744ad8e9ba61bf0d2adb2d62f5c1844  tools/phase_5_0_evidence/review_manifest.py
```

## Appendix B — §3.2 digest, length and path (28 lines)

```text
f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf 16509 infra/rp11-launch/toolchain.lock
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f 381913 infra/rp11-launch/build-root.manifest
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625 328 infra/rp11-launch/expected.sha256
b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b 5120 infra/rp11-launch/verify/fixtures/cc1.v.baseline
c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c 376981 docs/review/phase-5-0-evidence-harness-review-manifest.json
f02b7acfa14b1c108ab53942bd3f89a9bd629eccb6c2c685419e07bf729dec3d 178810 docs/review/phase-5-0-evidence-harness-concrete-plan.md
7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0 2819 infra/rp11-launch/build.sh
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe 6314 infra/rp11-launch/launch.c
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b 2187 infra/rp11-launch/select.h
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139 857 infra/rp11-launch/start.s
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326 2321 infra/rp11-launch/rp11-launch.ld
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 21742 infra/rp11-launch/rp11-launch.x86_64.listing
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300 15106 infra/rp11-launch/buildroot/provision.py
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a 14521 infra/rp11-launch/buildroot/enter.py
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72 6021 infra/rp11-launch/verify/cc1check.py
ea7d9dd3d8e141349019cfdeba5e91df7569e28d6818136777f59bf313316917 18546 infra/rp11-launch/verify/ic1check.py
b742552c6d200dd1c0536f29a444dcc4a00405f758788bc82c8b2c4f2df2aceb 7695 infra/rp11-launch/verify/elfcheck.py
cb1b8d835983b625e8e42dda2d46aa2d5e56816cf90fb8c3a397e291c3d0e676 5432 infra/rp11-launch/verify/tl11.py
eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31 35036 infra/rp11-launch/verify/ctverify.py
84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97 54170 infra/rp11-launch/verify/xdecode.py
d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66 3806 infra/rp11-launch/verify/xdecode-spelling.table
f0e811a4bd61782789b66f31ab4401797e52b8ac00ffeebb984bfcd71afb4a8a 14292 infra/rp11-launch/verify/xdecode-corpus.txt
603099e0f7279e4158023a63b6bc1411c0d9d3ac7c9372c7f77fa9d42f0b0a94 2228 infra/rp11-launch/test-harness/select_harness.c
8c4ad99c0a1f3452923dab46149e7f4b202060ef5bf981b732ec9e9724dd91fd 950 infra/rp11-launch/test-harness/select_shim.c
ff3d458cabae91512562cca6143542337b1306dc3df791da505c51a9519ab76f 12326 tests/test_rp11_launch_toolchain.py
bc24c0ee7b0c9f58853479adc908c60cf013b9652409e3d5cee0d710074a18b6 8045 tests/rp11_launch_support.py
5a2f4694983619d6a3fb7ac3965e4415dd114fb7504003d91abb6071d189c2b1 15849 tools/phase_5_0_evidence/rp11_launch.py
311f1d0300e3e98f5b3b33ea6c4598bfc744ad8e9ba61bf0d2adb2d62f5c1844 73785 tools/phase_5_0_evidence/review_manifest.py
```
