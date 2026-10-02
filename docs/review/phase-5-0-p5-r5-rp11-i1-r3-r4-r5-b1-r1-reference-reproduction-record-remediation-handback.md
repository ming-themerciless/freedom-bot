# Handback — `cc1.v` Reference-Reproduction Record Remediation (B1-R1)

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R1`

Date: 2026-10-01

Assignee: **Gemini** (independent rebuilder)

Controlling Prompt:
[`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r1-reference-reproduction-record-remediation-gemini-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r1-reference-reproduction-record-remediation-gemini-prompt.md)

Amended Document:
[`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md)

Status: **Documentation-only correction completed; substantive Branch A result unchanged; preflight procedural evidence noted as incomplete. Gemini has stopped. R-5 is not performed or claimed.**

---

## 1. Objective and Summary of Changes

In accordance with prompt `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R1`, three documentation defects in Gemini's B1 reference-reproduction handback (`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md`) were corrected without changing the substantive Branch A result:

1. **Defect 1: Incomplete preflight CPU-feature evidence and procedural-completeness narrowing.**
   - Retained preflight evidence in `execution.log` recorded CPU architecture (`x86_64`), model name (`AMD EPYC-Milan Processor`), family (25), model (1), and topology (2 threads/core, 3 cores/socket, 1 socket), but did **not** record CPU flags/features from `lscpu`. This was an evidence omission from the preflight record.
   - In accordance with Prompt §3, CPU flags/features are **not** reconstructed, inferred, quoted from later observations, or claimed as pre-provisioning evidence; they remain absent from the retained preflight log.
   - The verified exact CPU model name (`AMD EPYC-Milan Processor`) required by the B1 proceed/stop gate is explicitly distinguished from the omitted additional feature-detail record.
   - Any statement indicating that B1 satisfied every procedural requirement is narrowed: the substantive Branch A reproduction result remains verified, but the preflight procedural evidence record is incomplete.

2. **Defect 2: Wrong snapshot transport URL.**
   - Corrected the snapshot archive URL in §7 from `http://snapshot.ubuntu.com/ubuntu/20261001T000000Z` to `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z`, conforming with `infra/rp11-launch/buildroot/provision.py` line 58 (`SNAPSHOT_BASE = "https://snapshot.ubuntu.com/ubuntu"`) and `infra/rp11-launch/toolchain.lock` line 9 (`archive_base=https://snapshot.ubuntu.com/ubuntu`).

3. **Defect 3: Overgeneralized directory modes.**
   - Corrected the directory-mode description in §3: the package cache, work, and retained evidence directories were created with mode `0700`, while the build-root directory has mode `0755` because `provision.py` deliberately sets the root to mode `0755` during accepted post-install processing (`os.chmod(root, 0o755)` in `infra/rp11-launch/buildroot/provision.py` line 373).

4. **Correction Note:** Added a dated B1-R1 correction note to the B1 handback documenting all three defects.

---

## 2. Exact Before and After Statements for All Three Corrections

### Defect 1: CPU Feature Evidence and Procedural Narrowing

* **Status Line and Added Correction Note (lines 14–27):**
  - *Before:*
    ```markdown
    Status: **Reference reproduction completed successfully; baseline fixture created and verified. Gemini has stopped. R-5 is not performed or claimed.**

    ---
    ```
  - *After:*
    ```markdown
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
    ```

* **Section 1 Opening Sentence (lines 29–31):**
  - *Before:*
    ```markdown
    In accordance with prompt `C-P5.0-R5-RP11-I1-R3-R4-R5-B1`, Gemini executed the authorized reference reproduction procedure on the repository host using a wholly fresh build root provisioned from the accepted `toolchain.lock`, without reusing any previous root, cache, checkout, work directory, or artifact.
    ```
  - *After:*
    ```markdown
    In accordance with prompt `C-P5.0-R5-RP11-I1-R3-R4-R5-B1`, Gemini executed the authorized reference reproduction procedure on the repository host using a wholly fresh build root provisioned from the accepted `toolchain.lock`, without reusing any previous root, cache, checkout, work directory, or artifact. (While the core Branch A build and fixture results are verified, the preflight procedural evidence record is incomplete due to the omission of CPU flags/features from the pre-provisioning log.)
    ```

* **Section 2 Preflight Host Confirmation (lines 53–76):**
  - *Before:*
    ```markdown
    ### Preflight Host Confirmation

    Preflight inspection confirmed exact compatibility with Claude's reference environment prior to provisioning:

    | Item | Claude Reference Specification | Freshly Recorded Host Fact | Status |
    |---|---|---|---|
    | **Kernel** (`uname -r`) | `6.8.0-139-generic` | `6.8.0-139-generic` | **Compatible** |
    | **CPU Architecture** | `x86_64` | `x86_64` | **Compatible** |
    | **CPU Model Name** | `AMD EPYC-Milan Processor` | `AMD EPYC-Milan Processor` | **Compatible** |
    | **CPU Details** | Family 25, Model 1 | Family 25, Model 1, 2 threads/core, 3 cores/socket, 1 socket | **Compatible** |
    | **Bubblewrap Version** | `0.9.0` | `bubblewrap 0.9.0` | **Compatible** |
    | **Bubblewrap Identity** | `/usr/bin/bwrap` | `-rwxr-xr-x 1 root root 72160 Sep 17 20:12 /usr/bin/bwrap` | **Compatible** |
    | **Bubblewrap SHA-256** | — | `e318903862396f96de3df57264e0158682b952fd3fb53ac23d876413e7b30f71` | Recorded |
    ```
  - *After:*
    ```markdown
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
    ```

* **Section 8 Stop Gate (lines 240–241):**
  - *Before:*
    ```markdown
    - **Stop Gate:** Gemini has completed reference reproduction, established the verified `cc1.v` baseline fixture under Branch A, documented all evidence, and stopped.
    ```
  - *After:*
    ```markdown
    - **Stop Gate:** Gemini has established the verified `cc1.v` baseline fixture under Branch A, documented all available evidence (with the preflight CPU-feature record noted as incomplete), and stopped.
    ```

---

### Defect 2: Snapshot Transport URL

* **Section 7 Item 1 (line 227):**
  - *Before:*
    ```markdown
    1. **Network Boundary:** Network traffic was strictly bounded to `provision.py` downloading the 62 package archives specified in `toolchain.lock` from the signed Ubuntu snapshot server (`http://snapshot.ubuntu.com/ubuntu/20261001T000000Z`). No other network access occurred.
    ```
  - *After:*
    ```markdown
    1. **Network Boundary:** Network traffic was strictly bounded to `provision.py` downloading the 62 package archives specified in `toolchain.lock` from the signed Ubuntu snapshot server (`https://snapshot.ubuntu.com/ubuntu/20261001T000000Z`). No other network access occurred.
    ```

---

### Defect 3: Directory-Mode Specification

* **Section 3 Unique Directories (lines 98–110):**
  - *Before:*
    ```markdown
    ### Unique Directories

    All provisioning and execution took place in freshly created, dedicated directories under `/tmp` with mode `0700`:

    * **Run ID:** `p5-b1-repro-20261001t190454z`
    * **Root Directory:** `/tmp/p5-b1-repro-20261001t190454z-root`
    * **Package Cache:** `/tmp/p5-b1-repro-20261001t190454z-cache`
    * **Work Directory:** `/tmp/p5-b1-repro-20261001t190454z-work`
    * **Retained Evidence Directory:** `/tmp/p5-b1-repro-20261001t190454z-evidence`
    * **Execution Log:** `/tmp/p5-b1-repro-20261001t190454z-evidence/execution.log`

    No earlier root, cache, checkout, or intermediate outputs were reused.
    ```
  - *After:*
    ```markdown
    ### Unique Directories

    Provisioning and execution took place in freshly created, dedicated directories under `/tmp`. The package cache, work, and retained evidence directories have mode `0700`. The build-root directory has mode `0755` because `provision.py` deliberately sets the root to `0755` during accepted post-install processing (`os.chmod(root, 0o755)` in `infra/rp11-launch/buildroot/provision.py` line 373):

    * **Run ID:** `p5-b1-repro-20261001t190454z`
    * **Root Directory:** `/tmp/p5-b1-repro-20261001t190454z-root` (mode `0755`, post-install)
    * **Package Cache:** `/tmp/p5-b1-repro-20261001t190454z-cache` (mode `0700`)
    * **Work Directory:** `/tmp/p5-b1-repro-20261001t190454z-work` (mode `0700`)
    * **Retained Evidence Directory:** `/tmp/p5-b1-repro-20261001t190454z-evidence` (mode `0700`)
    * **Execution Log:** `/tmp/p5-b1-repro-20261001t190454z-evidence/execution.log`

    No earlier root, cache, checkout, or intermediate outputs were reused.
    ```

---

## 3. Before and After SHA-256 for Amended B1 Handback

Target File:
`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md`

* **Before SHA-256:**
  `18a86a113527c748be08c2483ca4bad78605ed273c561dc49e2086c67beca113`
* **After SHA-256:**
  `3cde1285501b834a9a63685f88a15d35f2e15bd9c4cc3c73ffe7ee7ee92ab1a2`

---

## 4. Confirmations of Restraint

1. **No repeated command, inspection, test, build, or provisioning:**
   - No rerun of `provision.py`, `enter.py`, `build.sh`, `cc1check.py`, or pytest test suites was performed.
   - No fresh host facts or `lscpu` features were queried or inspected.
   - CPU flags/features remain absent from the retained preflight evidence.
   - No network access, snapshot download, SSH, rsync, `oracle-test`, `sudo`, package operations, services, databases, or harness `--execute` was invoked.

2. **No touched fixture or `/tmp` evidence:**
   - Fixture file `infra/rp11-launch/verify/fixtures/cc1.v.baseline` was completely untouched (SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`, length 5,120 bytes).
   - Retained `/tmp` directories (`/tmp/p5-b1-repro-20261001t190454z-*`) remain untouched for independent inspection.
   - No code, lock, manifest, expected digests, listing, governance documents, or other handbacks were modified.
   - Only the two authorized documentation files were touched:
     - `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md` (remediated)
     - `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r1-reference-reproduction-record-remediation-handback.md` (this handback)

---

## 5. Whitespace and Format Verification (`git diff --check`)

Verification commands executed for the authorized documentation files:

```bash
git --no-pager diff --check --no-index /dev/null docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md
git --no-pager diff --check --no-index /dev/null docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r1-reference-reproduction-record-remediation-handback.md
```

* **Result:** Zero trailing whitespace or formatting warnings emitted on both files.
* Repository-wide tracked file check `git diff --check`: Clean exit code 0.

---

## 6. Unchanged Branch A Digest Result and R-5 Stop State

* **Substantive Branch A Result:**
  - Regenerated Manifest SHA-256: `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` (exact byte equality with `build-root.manifest`).
  - All four normative outputs match `infra/rp11-launch/expected.sha256`:
    - `rp11-launch`: `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`
    - `rp11-launch.x86_64.listing`: `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188`
    - `rp11-launch.map`: `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d`
    - `launch.s`: `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706`
  - Intermediate compiler diagnostic `build-out/cc1.v` byte length: `5,120` bytes.
  - `cc1.v` SHA-256: `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` (exact byte equality with fixture `cc1.v.baseline`).
  - `cc1check.py`: `PASS` (0 differences).
  - Reported test suite results: 15 passed in focused gate tests, 634 passed in launcher source tests, 12 passed against fresh root in toolchain tests (12 cleanly skipped with unset root).

* **Incomplete Procedural-Evidence Note:**
  - The core Branch A result is verified, but the preflight evidence is incomplete due to omitted CPU flags/features from `lscpu`.

* **R-5 Stop State:**
  - R-5 remains unperformed, stopped, Blocking, and unaccepted.
  - Baseline reference reproduction and fixture establishment do not constitute R-5.
  - Gemini has completed the B1-R1 remediation and stopped.
