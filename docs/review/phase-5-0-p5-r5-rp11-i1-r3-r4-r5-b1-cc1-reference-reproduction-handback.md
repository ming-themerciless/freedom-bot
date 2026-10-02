# Handback — `cc1.v` Reference Reproduction

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-B1`

Date: 2026-10-01

Assignee: **Gemini** (independent rebuilder)

Controlling Prompt:
[`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-gemini-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-gemini-prompt.md)

Result Branch: **Branch A — exact digest reproduced**

Status: **Branch A reference reproduction verified; baseline fixture created and verified; preflight CPU-feature record incomplete. Gemini has stopped. R-5 is not performed or claimed.**

> [!NOTE]
> **B1-R1 Correction Note (2026-10-01, Work ID `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R1`):**
> This handback was corrected under maintainer direction to remediate three documentation defects:
> 1. **Incomplete preflight CPU-feature record:** Retained preflight evidence in `execution.log` recorded architecture, model name, family, model, and topology, but did **not** include CPU flags/features. This is an evidence omission from the preflight record. CPU flags/features are not retroactively reconstructed, inferred, or quoted from later host observations, nor claimed as pre-provisioning evidence. The verified exact CPU model required by the B1 proceed/stop condition (`AMD EPYC-Milan Processor`) is distinguished from this omitted feature-detail record. Any statement that B1 satisfied every procedural requirement is narrowed accordingly: the core Branch A reproduction result remains verified, but the preflight procedural evidence record is incomplete.
> 2. **Corrected snapshot transport URL:** Handback §7 erroneously cited an `http://...` URL for the snapshot archive; the actual transport URL defined in `infra/rp11-launch/buildroot/provision.py` and `infra/rp11-launch/toolchain.lock` is `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z`.
> 3. **Corrected directory-mode specification:** Handback §3 overgeneralized all fresh run directories as mode `0700`. The package cache, work, and retained evidence directories were created with mode `0700`, but `provision.py` deliberately sets the build root directory to mode `0755` during accepted post-install processing (`os.chmod(root, 0o755)` in `provision.py` line 373).
>
> The substantive Branch A disposition (fixture byte-identical, length 5,120 bytes, SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`, R-1 manifest equality, normative output digests, `cc1check.py` PASS, R-5 unperformed) remains verified and unchanged.

---

## 1. Executive Summary and Result Disposition

In accordance with prompt `C-P5.0-R5-RP11-I1-R3-R4-R5-B1`, Gemini executed the authorized reference reproduction procedure on the repository host using a wholly fresh build root provisioned from the accepted `toolchain.lock`, without reusing any previous root, cache, checkout, work directory, or artifact. (While the core Branch A build and fixture results are verified, the preflight procedural evidence record is incomplete due to the omission of CPU flags/features from the pre-provisioning log.)

The fresh invocation executed the accepted same-invocation R-1 manifest gate immediately before R-2 within a single `enter.py build` run:
1. The R-1 manifest gate regenerated the build root manifest using the root's pinned `find` and `sha256sum`, proving byte equality with `build-root.manifest` (SHA-256 `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f`) and emitting `r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal`.
2. The R-2 build completed with exit code 0, and all four normative outputs matched `infra/rp11-launch/expected.sha256` exactly.
3. The intermediate compiler diagnostic stream `build-out/cc1.v` yielded an exact length of **5,120 bytes** and SHA-256:
   ```text
   b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b
   ```
   This matches Claude's reference `cc1.v` digest exactly.

**Result Branch:** Under Prompt §5, this result satisfies **Branch A (exact digest reproduced)**.
The fresh `cc1.v` bytes were retained without transformation, decoding, or normalization at:
`infra/rp11-launch/verify/fixtures/cc1.v.baseline`
Exact byte equality between the build output and the fixture was confirmed via `cmp`, SHA-256 was re-verified, and `cc1check.py` returned verdict `PASS` with 0 differences.

All fresh run directories under `/tmp` have been retained intact for independent review. Gemini has stopped and has not initiated R-5.

---

## 2. Fresh Preflight Host Facts and Input Hashes

### Preflight Host Confirmation

Preflight inspection confirmed compatibility of the mandatory proceed/stop host facts (kernel, CPU model name, and bubblewrap version) with Claude's reference environment prior to provisioning, though the CPU-feature preflight record is incomplete:

| Item | Claude Reference Specification | Freshly Recorded Host Fact | Status |
|---|---|---|---|
| **Kernel** (`uname -r`) | `6.8.0-139-generic` | `6.8.0-139-generic` | **Compatible** (satisfied proceed/stop gate) |
| **CPU Architecture** | `x86_64` | `x86_64` | **Compatible** |
| **CPU Model Name** | `AMD EPYC-Milan Processor` | `AMD EPYC-Milan Processor` | **Compatible** (satisfied proceed/stop gate) |
| **CPU Details** | Family 25, Model 1 | Family 25, Model 1, 2 threads/core, 3 cores/socket, 1 socket | **Compatible** |
| **CPU Flags / Features** | Relevant feature output from `lscpu` | *Omitted from retained preflight log* | **Incomplete preflight record** |
| **Bubblewrap Version** | `0.9.0` | `bubblewrap 0.9.0` | **Compatible** (satisfied proceed/stop gate) |
| **Bubblewrap Identity** | `/usr/bin/bwrap` | `-rwxr-xr-x 1 root root 72160 Sep 17 20:12 /usr/bin/bwrap` | **Compatible** |
| **Bubblewrap SHA-256** | — | `e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71` | Recorded |

*Note on CPU Features / Flags:*
The B1 prompt §3 required recording the complete CPU model and relevant feature output from `lscpu`. The verified exact CPU model name (`AMD EPYC-Milan Processor`) required by the B1 proceed/stop condition was verified and matched Claude's reference specification. However, the retained preflight evidence in `execution.log` did **not** include CPU flags/features, although it did record the architecture, model name, family, model, and topology shown above. CPU flags/features remain absent from the retained preflight record; they are not reconstructed, inferred, or quoted from a later observation, nor claimed as pre-provisioning evidence.

### Input Hashes Before Provisioning

All five controlling files specified in Prompt §3 were verified by SHA-256:

| File | SHA-256 |
|---|---|
| `infra/rp11-launch/toolchain.lock` | `f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf` |
| `infra/rp11-launch/build-root.manifest` | `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` |
| `infra/rp11-launch/buildroot/enter.py` | `cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a` |
| `infra/rp11-launch/build.sh` | `7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0` |
| `infra/rp11-launch/verify/cc1check.py` | `16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72` |

Additionally recorded:
* `infra/rp11-launch/buildroot/provision.py`: `40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300`

---

## 3. Unique Run Directories and Authorized Procedure

### Unique Directories

Provisioning and execution took place in freshly created, dedicated directories under `/tmp`. The package cache, work, and retained evidence directories have mode `0700`. The build-root directory has mode `0755` because `provision.py` deliberately sets the root to `0755` during accepted post-install processing (`os.chmod(root, 0o755)` in `infra/rp11-launch/buildroot/provision.py` line 373):

* **Run ID:** `p5-b1-repro-20261001t190454z`
* **Root Directory:** `/tmp/p5-b1-repro-20261001t190454z-root` (mode `0755`, post-install)
* **Package Cache:** `/tmp/p5-b1-repro-20261001t190454z-cache` (mode `0700`)
* **Work Directory:** `/tmp/p5-b1-repro-20261001t190454z-work` (mode `0700`)
* **Retained Evidence Directory:** `/tmp/p5-b1-repro-20261001t190454z-evidence` (mode `0700`)
* **Execution Log:** `/tmp/p5-b1-repro-20261001t190454z-evidence/execution.log`

No earlier root, cache, checkout, or intermediate outputs were reused.

### Exact Commands Executed

```bash
# 1. Provision fresh build root from accepted lock and signed snapshot:
python3 infra/rp11-launch/buildroot/provision.py install \
  --lock infra/rp11-launch/toolchain.lock \
  --root /tmp/p5-b1-repro-20261001t190454z-root \
  --cache /tmp/p5-b1-repro-20261001t190454z-cache

# 2. Run ldconfig inside root once:
python3 infra/rp11-launch/buildroot/enter.py ldconfig \
  --root /tmp/p5-b1-repro-20261001t190454z-root

# 3. Execute same-invocation R-1 manifest gate + R-2 build:
python3 infra/rp11-launch/buildroot/enter.py build \
  --root /tmp/p5-b1-repro-20261001t190454z-root \
  --work /tmp/p5-b1-repro-20261001t190454z-work \
  --variant r2 \
  --manifest-out /tmp/p5-b1-repro-20261001t190454z-evidence/regenerated.manifest
```

---

## 4. Gate Evidence and Output Verification

### R-1 Manifest Gate

* Verdict emitted by `enter.py build`:
  ```text
  r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal
  exit 0
  ```
* Written regenerated manifest: `/tmp/p5-b1-repro-20261001t190454z-evidence/regenerated.manifest`
* Manifest SHA-256: `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f`
* Verification with `cmp`:
  `cmp infra/rp11-launch/build-root.manifest /tmp/p5-b1-repro-20261001t190454z-evidence/regenerated.manifest` (exit 0; byte-identical)

### Normative Output Hashes

Outputs produced in `/tmp/p5-b1-repro-20261001t190454z-work/co-r2/build-out/`:

| Output File | Fresh SHA-256 Digest | Expected (`expected.sha256`) | Verdict |
|---|---|---|---|
| `rp11-launch` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | **OK** |
| `rp11-launch.x86_64.listing` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | **OK** |
| `rp11-launch.map` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` | **OK** |
| `launch.s` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` | **OK** |

Verification via `sha256sum --check infra/rp11-launch/expected.sha256`:
```text
rp11-launch: OK
rp11-launch.x86_64.listing: OK
rp11-launch.map: OK
launch.s: OK
```

---

## 5. `cc1.v` Measurement and Branch A Fixture Retain

### Measurement of Fresh `cc1.v`

* **Source File:** `/tmp/p5-b1-repro-20261001t190454z-work/co-r2/build-out/cc1.v`
* **Byte Length:** `5,120` bytes (`wc -c`)
* **SHA-256 Digest:**
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`
* **Comparison to Reference Digest:** Exact match with Claude's reference digest `b77f92dc…`.

### Fixture Installation and Invariant Verification

As mandated by Branch A:
1. Created directory `infra/rp11-launch/verify/fixtures/`.
2. Copied raw bytes without transformation to `infra/rp11-launch/verify/fixtures/cc1.v.baseline`.
3. Verified source and copy byte equality:
   `cmp /tmp/p5-b1-repro-20261001t190454z-work/co-r2/build-out/cc1.v infra/rp11-launch/verify/fixtures/cc1.v.baseline` (exit 0)
4. Verified fixture SHA-256 and byte length:
   - Length: `5,120` bytes
   - SHA-256: `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`
5. Verified via `cc1check.py`:
   ```bash
   python3 infra/rp11-launch/verify/cc1check.py \
     infra/rp11-launch/verify/fixtures/cc1.v.baseline \
     /tmp/p5-b1-repro-20261001t190454z-work/co-r2/build-out/cc1.v
   ```
   **Output:**
   ```text
   baseline_sha256: b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b
   actual_sha256:   b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b
   is_identical:    True
   total_diffs:     0
   verdict:         PASS
   ```
   (exit code 0)

---

## 6. Verification Test Suites

All tests were executed on the repository host using Python 3.12.3 under `/opt/freedom-blades/runtime/venv-web/bin/python`:

| Suite | Command | Result |
|---|---|---|
| **Focused `cc1check` & Gate Tests** | `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 python -m pytest -v tests/test_rp11_launch_gate.py` | **15 passed, 0 failed, 0 skipped** (0.44s) |
| **Launcher Source Suite** | `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_rp11_launch_source.py` | **634 passed, 0 failed, 0 skipped** (1.84s) |
| **Toolchain-Dependent Suite (against fresh root)** | `env -u TEST_DATABASE_URL RP11_LAUNCH_BUILD_ROOT=/tmp/p5-b1-repro-20261001t190454z-root PYTHONDONTWRITEBYTECODE=1 python -m pytest -v tests/test_rp11_launch_toolchain.py` | **12 passed, 0 failed, 0 skipped** (1.38s) |
| **Toolchain-Dependent Suite (unset root)** | `env -u TEST_DATABASE_URL -u RP11_LAUNCH_BUILD_ROOT PYTHONDONTWRITEBYTECODE=1 python -m pytest -rs tests/test_rp11_launch_toolchain.py` | **12 skipped, 0 passed, 0 failed** (0.05s, clean skip with explicit reason) |
| **Python Bytecode Compilation** | `python3 -m py_compile infra/rp11-launch/buildroot/enter.py infra/rp11-launch/verify/cc1check.py` | Clean (exit 0) |
| **Git Whitespace & Format Check** | `git diff --check` | Clean (exit 0, no output) |

*Note: Database suites and evidence harness with `--execute` were strictly excluded in accordance with Prompt §6.*

---

## 7. Residual Trust and Safety Boundaries

1. **Network Boundary:** Network traffic was strictly bounded to `provision.py` downloading the 62 package archives specified in `toolchain.lock` from the signed Ubuntu snapshot server (`https://snapshot.ubuntu.com/ubuntu/20261001T000000Z`). No other network access occurred.
2. **Authority and Invariants:**
   - No `sudo`, host configuration change, or host package change was performed.
   - No database, service, daemon, SSH, or rsync operations were performed.
   - `oracle-test` was not contacted.
   - R-5 rebuild was not performed or claimed.
   - Launcher source files, toolchain lock, manifest, and expected digests were not modified.
   - Writes were strictly confined to `/tmp` directories, the new fixture `infra/rp11-launch/verify/fixtures/cc1.v.baseline`, and this handback.
3. **Evidence Retention:** In compliance with Branch A, all run artifacts and intermediate checkouts remain intact in `/tmp/p5-b1-repro-20261001t190454z-*` for independent inspection and review.

---

## 8. Stop Gate and Next Actions

- **Stop Gate:** Gemini has established the verified `cc1.v` baseline fixture under Branch A, documented all available evidence (with the preflight CPU-feature record noted as incomplete), and stopped.
- **R-5 State:** R-5 remains stopped, unaccepted, and not executed. Achieving Branch A fulfills the prerequisite for future comparative diagnostic work under LD-8, but does not constitute an independent rebuild.
