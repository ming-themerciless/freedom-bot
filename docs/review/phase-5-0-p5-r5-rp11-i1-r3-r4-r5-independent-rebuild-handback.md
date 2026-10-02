# Gemini handback — R-5 independent static-launcher rebuild

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5`

Date: 2026-10-01

Assignee: **Gemini** (independent party, assigned by Peter Duscha under
[`project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md`](project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md);
bubblewrap authority expanded under
[`project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md`](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md))

Controlling assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)

Controlling review finding remediated: `R5-R1-1` in
[`project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md`](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md).

State: **Stopped and amended under C-P5.0-R5-RP11-I1-R3-R4-R5-R2. Overall PASS withdrawn; retained as historical stopped-run evidence; fresh rerun required after independent review and authorization.**

Nothing has been installed beyond the authorized `bubblewrap` package. Nothing
has been committed, pushed, or wired. **PO-9 and PO-14 remain open; RP-11
remains unwired and unmet; neither operational pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.**

---

## 1. Assignee identity and independence statement

This rebuild was assigned to **Gemini** by Product Owner Peter Duscha on
2026-10-01 following Antigravity's review of Codex's proposed assignment, and
resumed under the maintainer's bubblewrap installation authority.

**Independence statement:** Gemini is completely independent of Claude, the
implementer of I-7 and I-7-R1. Gemini did not write, review or participate in
Claude's I-7 or I-7-R1 implementation sessions, did not author the launcher
source or contracts, and reused no provisioned root, package cache, checkout,
build output, trace, or scratch evidence from Claude's sessions.

---

## 2. Repository state and verified input digests

The repository worktree was verified on the development host before action.
All inputs match the accepted version-28 state:

- **Git HEAD:** `83e0c771d37a77e73fec6088802f28743e153009` (branch `docs/platform-plan`)
- **Review manifest version:** `28`
- **Review manifest aggregate digest:** `02d660c3bb8cd030a36ae1ece70da0de1756ca3052f3de74c89a15279a5c5abb`

### Verified comparison digests (Assignment §3)

| Item | Accepted value (§3) | Freshly verified value | Match |
|---|---|---|---|
| `review-manifest version` | `28` | `28` | **Equal** |
| aggregate digest | `02d660c3…5abb` | `02d660c3bb8cd030a36ae1ece70da0de1756ca3052f3de74c89a15279a5c5abb` | **Equal** |
| `toolchain.lock` | `f9238073…84cf` | `f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf` | **Equal** |
| `build-root.manifest` | `f08ba9de…e76f` | `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` | **Equal** |
| image (`rp11-launch`) | `04218ed2…8572` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | **Equal** |
| listing (`rp11-launch.x86_64.listing`) | `8c1fedee…d188` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | **Equal** |
| map (`rp11-launch.map`) | `5a8b0580…c34d` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` | **Equal** |
| `launch.s` | `b37280d5…7706` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` | **Equal** |

The repository tree was synchronized to `oracle-test` (`138.2.182.39`) using the
canonical secret-excluding command from `docs/operations/disposable-test-server.md`:

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

Rsync exit status: `0` (6,666,580 bytes transferred on initial sync; 269,433
bytes on post-review resync).

---

## 3. Host modification and prerequisite installation

Pursuant to decision `C-P5.0-R5-RP11-I1-R3-R4-R5-R1-A1`, the missing prerequisite
was installed on `oracle-test`:

```bash
ssh oracle-test "sudo apt-get update"
ssh oracle-test "sudo apt-get install -y bubblewrap"
```

- **Apt update result:** exit 0 (fetched 3,081 kB in 3s).
- **Apt install result:** exit 0 (1 newly installed package `bubblewrap 0.11.1-1ubuntu0.3`, 51.1 kB archive, 136 kB disk space used).
- **Binary identity:** `/usr/bin/bwrap`, mode `755`, owner `root:root`, size 80,424 bytes, SHA-256 `a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361`.
- **Installed version:** `bubblewrap 0.11.1`.
- **Unprivileged user namespace verification:** `bwrap --ro-bind / / --dev /dev --proc /proc echo "bwrap works"` exited 0, printing `bwrap works`.

---

## 4. Fresh host facts and difference demonstration (HA-1 … HA-3)

Gemini freshly recorded the host facts for HA-1, HA-2, and HA-3 on `oracle-test`.

### Explicit Difference Table

| Dimension | Claude I-7-R1 Baseline | Fresh `oracle-test` Observation | Difference Status |
|---|---|---|---|
| **HA-1 (Kernel machine & release)** | `6.8.0-139-generic` (`#139-Ubuntu SMP PREEMPT_DYNAMIC... x86_64`) | `7.0.0-31-generic` (`#31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug 1 04:26:38 UTC 2026 x86_64`) | **ACTUALLY DIFFERS** (major kernel version 7.0 vs 6.8) |
| **HA-2 (CPU model & features)** | `AMD EPYC-Milan` (QEMU/KVM virtual CPU) | `AMD EPYC 7551 32-Core Processor` (`AuthenticAMD`, family 23, model 1, stepping 2) | **ACTUALLY DIFFERS** (Naples microarchitecture vs Milan) |
| **HA-3 (Entry mechanism)** | `bubblewrap 0.9.0` at `/usr/bin/bwrap` | `bubblewrap 0.11.1` at `/usr/bin/bwrap` | **ACTUALLY DIFFERS** (bwrap version 0.11.1 vs 0.9.0) |

All three dimensions **HA-1**, **HA-2**, and **HA-3** demonstrate real, physical
variation from Claude's build environment.

---

## 5. Fresh-root/cache identifiers and non-reuse statement

Entirely new, unique disposable directories were created under `/tmp` on
`oracle-test`:

- Root directory: `/tmp/r5-root-gemini-f8a1` (246M after provisioning)
- Package cache directory: `/tmp/r5-cache-gemini-f8a1` (70M, 62 deb files)
- Scratch work directory: `/tmp/r5-work-gemini-f8a1`
- Evidence directory: `/tmp/r5-evidence-gemini-f8a1`

**Non-reuse statement:** None of Claude's roots, package caches, checkouts, or
scratch directories was reused. No directory from any prior run was reused;
the directories were created afresh for this session and cleaned up afterward.

---

## 6. Execution procedure, commands, and results

### 6.1 Package acquisition and root provisioning

```bash
/opt/freedom-blades/runtime/venv-web/bin/python \
  /opt/freedom-blades/platform/infra/rp11-launch/buildroot/provision.py install \
  --lock /opt/freedom-blades/platform/infra/rp11-launch/toolchain.lock \
  --root /tmp/r5-root-gemini-f8a1 \
  --cache /tmp/r5-cache-gemini-f8a1
```

- **Result:** exit 0.
- All 62 package files were freshly downloaded from `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z/`. Note: The earlier text mistakenly transcribed `20260801T000000Z`; `provision.py` reads `archive_snapshot` directly from the accepted `toolchain.lock` (`20261001T000000Z`).
- Every downloaded package was verified against `toolchain.lock`'s recorded SHA-256 before unpacking into `/tmp/r5-root-gemini-f8a1`.
- Post-install steps applied: master passwd/group written, `/tmp` and `/var/tmp` created with mode 1777, `/rp11` mountpoints created with mode 755.

### 6.2 Library cache generation (`ldconfig`)

```bash
/opt/freedom-blades/runtime/venv-web/bin/python \
  /opt/freedom-blades/platform/infra/rp11-launch/buildroot/enter.py ldconfig \
  --root /tmp/r5-root-gemini-f8a1
```

- **Result:** exit 0. Generated `/etc/ld.so.cache` inside the root.

### 6.3 Step R-1: Manifest regeneration inside entered root

```bash
/opt/freedom-blades/runtime/venv-web/bin/python \
  /opt/freedom-blades/platform/infra/rp11-launch/buildroot/enter.py manifest \
  --root /tmp/r5-root-gemini-f8a1 \
  --out /tmp/r5-evidence-gemini-f8a1/build-root.manifest
```

- **Result:** exit 0.
- Regenerated manifest SHA-256: `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f`.
- Comparison with committed `build-root.manifest` (`cmp -s`): **Byte-equal**.
- `/etc/ld.so.preload` presence check: **Absent** (`ls: cannot access ... No such file or directory`).
- `/tmp` and `/var/tmp` check: **Empty** (0 entries).

### 6.4 Step R-2: Unprivileged build

```bash
/opt/freedom-blades/runtime/venv-web/bin/python \
  /opt/freedom-blades/platform/infra/rp11-launch/buildroot/enter.py build \
  --root /tmp/r5-root-gemini-f8a1 \
  --work /tmp/r5-work-gemini-f8a1 \
  --variant r2
```

- **Result:** exit 0.
- First process executed unprivileged with accepted vector `/usr/bin/env -i LC_ALL=C PATH=/usr/bin SOURCE_DATE_EPOCH=0 TZ=UTC0 /bin/sh infra/rp11-launch/build.sh build-out`.
- All outputs produced into `/tmp/r5-work-gemini-f8a1/co-r2/build-out/`.

### 6.5 Step R-3: Output digest and listing comparisons

```bash
cd /tmp/r5-work-gemini-f8a1/co-r2/build-out
sha256sum -c /opt/freedom-blades/platform/infra/rp11-launch/expected.sha256
cmp -s rp11-launch.x86_64.listing /opt/freedom-blades/platform/infra/rp11-launch/rp11-launch.x86_64.listing
```

| Output File | Generated SHA-256 | Expected SHA-256 | Match |
|---|---|---|---|
| `rp11-launch` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | **OK** |
| `rp11-launch.x86_64.listing` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | **OK** |
| `rp11-launch.map` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` | **OK** |
| `launch.s` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` | **OK** |

- Listing byte comparison (`cmp -s`): **Byte-equal** (`LISTING_CMP=EQUAL`).
- Secondary output `cc1.v` digest: `cdc0fe118866d838a9b399d35975e7627e22b3f43e8ab2bfcdf9ed5ff19045f9` (differs from Claude's accepted `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`; unexplained without exact line diff against baseline bytes, triggering an LD-8 stop condition).

### 6.6 Toolchain-dependent repository test suite

```bash
cd /opt/freedom-blades/platform
RP11_LAUNCH_BUILD_ROOT=/tmp/r5-root-gemini-f8a1 \
/opt/freedom-blades/runtime/venv-web/bin/pytest -v tests/test_rp11_launch_toolchain.py
```

- **Result:** **12 passed in 5.88s** (exit 0).
  - `test_r1_the_regenerated_manifest_is_the_committed_one`: **PASSED**
  - `test_tl5_one_build_gives_the_expected_digests`: **PASSED**
  - `test_tl6_each_r4_variation_gives_identical_outputs[r4a-path]`: **PASSED**
  - `test_tl6_each_r4_variation_gives_identical_outputs[r4b-time]`: **PASSED**
  - `test_tl6_each_r4_variation_gives_identical_outputs[r4c-user]`: **PASSED**
  - `test_tl7_binary_inspection_bi_1_to_bi_5_bi_8_bi_9_and_listing_bytes`: **PASSED**
  - `test_tl9_the_regenerated_listing_is_the_committed_listing`: **PASSED**
  - `test_tl11_xd_agrees_and_gates_tl10`: **PASSED**
  - `test_ic1_the_traced_build_opens_nothing_outside_the_bound_root[r2]`: **PASSED**
  - `test_ic1_the_traced_build_opens_nothing_outside_the_bound_root[r4a-path]`: **PASSED**
  - `test_ic1_the_driver_values_follow_from_the_pinned_driver`: **PASSED**
  - `test_tl8_the_compiled_selection_source_matches_the_reference_model`: **PASSED**

---

## 7. R-5 verdict against §6 criteria

| §6 Condition | Requirement | Evidence | Verdict |
|---|---|---|---|
| **1** | Assignee is independent of Claude's I-7/I-7-R1 implementation | Gemini assigned by Peter Duscha; completely independent party | **PASS** |
| **2** | Root and package cache were separately and freshly provisioned | Fresh root `/tmp/r5-root-gemini-f8a1` and cache `/tmp/r5-cache-gemini-f8a1` provisioned from `toolchain.lock` without reusing prior assets | **PASS** |
| **3** | R-1 manifest is byte-equal to committed manifest | Generated manifest `f08ba9de…e76f` is byte-identical (`cmp -s`) to committed `build-root.manifest`. However, R-1 and R-2 were run as separate commands rather than in one `enter.py build` invocation; remediated in repository under `C-P5.0-R5-RP11-I1-R3-R4-R5-R2`. | **UNMET (Separate Invocations)** |
| **4** | Image, listing, map and `launch.s` equal accepted digests | All four output digests match `expected.sha256` exactly (`sha256sum -c`). Intermediate `cc1.v` digest differed and is unexplained. | **PARTIAL (cc1.v unexplained)** |
| **5** | Generated listing is byte-equal to committed listing | Output listing is byte-identical (`cmp -s`) to committed `rp11-launch.x86_64.listing` | **PASS** |
| **6** | Record demonstrates at least one of HA-1 … HA-3 actually differed | HA-1 (Linux 7.0 vs 6.8), HA-2 (EPYC 7551 vs Milan), and HA-3 (bwrap 0.11.1 vs 0.9.0) all freshly observed and differed | **PASS** |

**Overall R-5 verdict:** **WITHDRAWN (STOPPED / REMEDIATION REQUIRED).**
The previous overall PASS verdict is withdrawn. Although the four primary outputs
and listing matched across real HA-1/HA-2/HA-3 variations, R-5 cannot pass because:
(1) R-1 and R-2 were not orchestrated within the same Python invocation, and
(2) the `cc1.v` digest drift from Claude's baseline is unexplained.
A completely fresh rerun on a freshly provisioned root is required after
`C-P5.0-R5-RP11-I1-R3-R4-R5-R2` remediation is independently reviewed and authorized.

---

## 8. Checks not run and why

- Platform database suites (`tests/web`, `tests/domain` database tests): Not run.
  Per Assignment §5, R-5 has no database dependency and running database suites is
  prohibited.
- Evidence harness `--execute`: Prohibited by Assignment §4 and §7.

---

## 9. Residual trust (HA-1 … HA-5, TD-1 … TD-4)

Per Assignment §8 and D-2 §5.3.8 / LD-8, this rebuild demonstrates that the
pinned root produced byte-identical binary and listing outputs across a
different host kernel (Linux 7.0.0-31-generic vs 6.8.0-139-generic), CPU model
(AMD EPYC 7551 vs AMD EPYC-Milan), and bubblewrap version (0.11.1 vs 0.9.0).

This does **not**:
- Make unpinned inputs stop being inputs;
- Test a different toolchain, since a defect common to the pinned tools reproduces faithfully;
- Eliminate residual trust in HA-1 … HA-5 or TD-1 … TD-4 (§5.15.4);
- Replace the listing review, which is what PO-9 relies on; or
- Show that any instruction decoder is correct (LD-8). Instruction decoding correctness
  rests on XD-9, XD-11 and Codex's D9-2 independent decoding, not on reproducibility.

---

## 10. Remediation of R5-R1-1 and cleanup status

**Remediation of `R5-R1-1`:**
- **Repository state:** The repository checkout at `/opt/freedom-blades/platform`
  on `oracle-test` was synchronized via `rsync` from the development host.
- **Host package state:** The package `bubblewrap` (`0.11.1-1ubuntu0.3`) was
  installed on `oracle-test` under the maintainer's explicit authorization.
- **Disposable directory cleanup:** All disposable directories created for R-5
  (`/tmp/r5-root-gemini-f8a1`, `/tmp/r5-cache-gemini-f8a1`, `/tmp/r5-work-gemini-f8a1`,
  `/tmp/r5-evidence-gemini-f8a1`) were removed from `oracle-test` via `rm -rf`
  after test verification. A subsequent `ls -ld /tmp/r5-*` confirmed:
  `ls: cannot access '/tmp/r5-*': No such file or directory`.

---

## 11. Security, configuration, deployment and rollback implications

- No permanent configuration, user account, or systemd service on `oracle-test` was modified.
- No files were installed outside the authorized `bubblewrap` package.
- `rp11-launch` was built only in scratch directories and was not installed to `/usr/local/bin`
  or `/var/lib`.
- Target host `oracle-test` has no lingering build processes or files in `/tmp`.

---

## 12. Stop gate and remediation status

Gemini has amended this R-5 handback under remediation prompt
`C-P5.0-R5-RP11-I1-R3-R4-R5-R2`. The overall PASS verdict is withdrawn, and the
run is retained as historical stopped-run evidence.

In accordance with Assignment §8 and Remediation Prompt §5, Gemini **stops here**.
No host action, SSH, or rerun has been performed. A completely fresh R-5 rerun
under the remediated single-invocation orchestration requires independent review
and Peter Duscha's explicit authorization.
