# Fresh R-5 independent static-launcher rebuild — handback

Execution work ID: `C-P5.0-R5-RP11-FRESH-R5`
Decision ID: `C-P5.0-R5-RP11-FRESH-R5-A1`
Executor: **Gemini** (named by Peter Duscha on 2026-10-02)
Activation record: [`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md)
Procedure: [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)
Run identifier: `p5-r5-fresh-20261002T184800Z-7e9b2d41`

---

## 1. Independence and freshness attestation (§2)

I, Gemini, as the independent executor named by Peter Duscha under decision `C-P5.0-R5-RP11-FRESH-R5-A1`, hereby attest before any host action:

1. I did not implement, co-author or remediate I-7 or I-7-R1.
2. I have not reused, and will not use, any earlier build root, package cache, checkout, work directory, build output, trace, evidence or scratch directory.
3. I have read the fresh R-5 assignment ([`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md)), the acceptance record ([`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md)), and the activation record ([`project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md`](project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md)).
4. Under the mandatory Gemini clause of §2.4: this run is wholly fresh. I have not read, reused, copied, compared against or inherited, and will not read, reuse, copy, compare against or inherit, any resource or artifact from my earlier R-5 run (`/tmp/r5-*-gemini-f8a1` on `oracle-test`) or my earlier B1 run (`/tmp/p5-b1-repro-20261001t190454z-*` on the repository host). This includes roots, caches, checkouts, outputs, `cc1.v` bytes, manifests, traces, logs and pytest temporary directories. The only exception is the committed repository fixture (`infra/rp11-launch/verify/fixtures/cc1.v.baseline`), read as described in §5. The stopped-run digest `cdc0fe11…45f9` remains rejected and is not a comparison input.

Signed: **Gemini** (2026-10-02)

---

## 2. Timed scopes (§6.0, §10 item 2)

| Scope | Start value (label, producing invocation, status) | End value (label, producing invocation, status) | Host |
|---|---|---|---|
| whole run | `RUN.start start_utc=2026-10-03T11:51:06Z` (label `RUN.start`, step-1 block, `date exit=0`) | in closing record | repository host |
| step 1 | `S1.start start_utc=2026-10-03T11:51:06Z` (label `S1.start`, step-1 block, `date exit=0`) | `S1.end end_utc=2026-10-03T11:51:06Z` (label `S1.end`, `date exit=0`, `S1 final exit=0`) | repository host |
| step 2 | `S2.start start_utc=2026-10-03T12:08:50Z` (label `S2.start`, step-2 block, `date exit=0`) | `S2.end end_utc=2026-10-03T12:08:52Z` (label `S2.end`, `date exit=0`, `S2 final exit=0`) | `oracle-test` |
| step 3 | `S3.start start_utc=2026-10-03T12:09:13Z` (label `S3.start`, step-3 block, `date exit=0`) | `S3.end end_utc=2026-10-03T12:09:13Z` (label `S3.end`, `date exit=0`, `S3 final exit=0`) | `oracle-test` |
| step 4a | `S4a.start start_utc=2026-10-03T12:10:43Z` (label `S4a.start`, step-4a block, `date exit=0`) | `S4a.end end_utc=2026-10-03T12:10:43Z` (label `S4a.end`, `date exit=0`, `S4a final exit=0`) | `oracle-test` |
| step 4b (the `rsync` invocation) | `S4b.start start_utc=2026-10-03T12:10:43Z` (label `S4b.start`, S4b.start block, `date exit=0`, `block exit=0`) | `S4b.end end_utc=2026-10-03T12:10:54Z` (label `S4b.end`, S4b.end block, `date exit=0`, `block exit=0`) | repository host |
| step 4c | `S4c.start start_utc=2026-10-03T12:10:54Z` (label `S4c.start`, step-4c block, `date exit=0`) | `S4c.end end_utc=2026-10-03T12:10:54Z` (label `S4c.end`, `date exit=0`, `S4c final exit=0`) | repository host |
| step 4d | `S4d.start start_utc=2026-10-03T12:10:54Z` (label `S4d.start`, step-4d block, `date exit=0`) | `S4d.end end_utc=2026-10-03T12:10:54Z` (label `S4d.end`, `date exit=0`, `S4d final exit=0`) | `oracle-test` |
| step 5 | `S5.start start_utc=2026-10-03T12:13:10Z` (label `S5.start`, step-5 block, `date exit=0`) | `S5.end end_utc=2026-10-03T12:13:38Z` (label `S5.end`, `date exit=0`, `S5 final exit=1`) | `oracle-test` |
| steps 6 and 7, combined | not run | not run | `oracle-test` |
| step 8 | not run | not run | `oracle-test` |
| step 9 | not run | not run | `oracle-test` |
| step 10 | not run | not run | `oracle-test` |
| step 11 | not run | not run | `oracle-test` |
| step 12 | `S12.start start_utc=2026-10-03T12:14:46Z` (label `S12.start`, S12.start block, `date exit=0`, `block exit=0`) | in closing record | repository host |

---

## 3. Repository state and preflight checks (§10 item 3)

- **Commit:** `9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa`
- **`git status --short`:** All changes isolated to `docs/` review files.
- **S1.4 `repository-state`:** `repository_state=clean` (exit 0)
- **S4c.2 `repository-state`:** `repository_state=clean` (exit 0)
- **S1.5 `sha256sum-check`:** All 28 files OK (exit 0)
- **S1.6 `hashlib-and-tree-check`:** `rows 28 mismatches 0`, `launcher_tree files 22 dirs 5` (exit 0)
- **S4c.3 `sha256sum-check`:** All 28 files OK (exit 0)
- **S4d.3 `sha256sum-check`:** All 28 files OK (exit 0)
- **S4d.4 `hashlib-and-tree-check`:** `rows 28 mismatches 0`, `launcher_tree files 22 dirs 5` (exit 0)
- **S1.8 `in-memory-review-manifest`:** `30 28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526 True c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c False` (exit 0)

---

## 4. Host environment and variation qualification (§10 item 4)

### Observations from Step 2 (`oracle-test`):
- **Date:** `2026-10-03T12:08:50Z`
- **HA-1 Kernel release:** `7.0.0-31-generic` (`Linux 7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug 1 04:26:38 UTC 2026 x86_64`)
- **HA-2 CPU Model name:** `AMD EPYC 7551 32-Core Processor` (family 23, model 1, stepping 2, microcode 0x8001279, 2 vCPUs)
- **HA-3 Bubblewrap:** version `0.11.1`, package `bubblewrap 0.11.1-1ubuntu0.3`, mode `755 root:root 80424`, sha256 `a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361`
- **HA-4 max_user_namespaces:** `3354` (positive integer, exit 0)
- **AppArmor unprivileged userns:** `apparmor_restrict_unprivileged_userns=1`
- **HA-5 Identity:** `uid=1001(ubuntu) gid=1001(ubuntu)`
- **Hostname:** `Test`
- **OS Release:** `Ubuntu 26.04.1 LTS (Resolute Raccoon)`
- **MemTotal:** `973580 kB`
- **Disk space:** `tmpfs 486792 1024-blocks, 4900 used, 481892 available (2%) on /tmp`
- **Python interpreter:** `Python 3.12.14 (main, Sep 1 2026, 14:16:52) [Clang 22.1.3 ]` at `/opt/freedom-blades/runtime/venv-web/bin/python`
- **Pytest:** `8.4.2`
- **Tools:** `zstd` v1.5.7, `gpgv` 2.4.8, `rsync`, `lscpu` present
- **Keyring:** sha256 `80a36b0a6de2f69f49d2df75ef473ccde121e9e190b9ea01d20a4f63778d5c31 /usr/share/keyrings/ubuntu-archive-keyring.gpg`
- **Run prefix check:** `run_prefix_entries=none` (exit 0)

### Variation qualification (Step 3, S3.1):
```text
HA-1 kernel_release=7.0.0-31-generic
HA-2 model_names=AMD EPYC 7551 32-Core Processor
HA-1 qualifies=yes
HA-2 qualifies=yes
HA-3 qualifies=no (version-only differences do not qualify; section 4.2)
S3.1 qualification exit=0
```

### HA-1 … HA-3 difference table against baseline §3.4:
| Axis | Baseline (§3.4) | `oracle-test` (observed) | Qualifies? |
|---|---|---|---|
| **HA-1 (Kernel)** | `6.8.0-139-generic` | `7.0.0-31-generic` | **Yes** (kernel release differs) |
| **HA-2 (CPU model)** | `AMD EPYC-Milan Processor` | `AMD EPYC 7551 32-Core Processor` | **Yes** (CPU model name differs) |
| **HA-3 (Bubblewrap)**| `0.9.0` | `0.11.1` | **No** (version-only difference does not qualify; §4.2) |

---

## 5. Created paths, permissions, and sizes (§10 item 5)

Created in Step 4a on `oracle-test`:
- `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout`: creation mode `700 ubuntu:ubuntu`; after rsync mode `2775 ubuntu:ubuntu`
- `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-index`: creation mode `700 ubuntu:ubuntu`
- `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-cache`: creation mode `700 ubuntu:ubuntu`
- `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-root`: creation mode `700 ubuntu:ubuntu`
- `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-work`: creation mode `700 ubuntu:ubuntu`
- `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-evidence`: creation mode `700 ubuntu:ubuntu`

(Final stat and du accounting from Step 11 was not run due to HARD STOP at Step 5).

---

## 6. Block execution and transcripts (§10 item 6)

### Step 1 block (repository host):
Status: final exit 0
Transcript:
```text
S1.trap exit=0
RUN.start start_utc=2026-10-03T11:51:06Z
S1.start start_utc=2026-10-03T11:51:06Z
S1.start date exit=0
S1.1 cd exit=0
9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa
S1.2 git-rev-parse exit=0
S1.3 git-status exit=0
repository_state=clean
S1.4 repository-state exit=0
infra/rp11-launch/toolchain.lock: OK
infra/rp11-launch/build-root.manifest: OK
infra/rp11-launch/expected.sha256: OK
infra/rp11-launch/verify/fixtures/cc1.v.baseline: OK
docs/review/phase-5-0-evidence-harness-review-manifest.json: OK
docs/review/phase-5-0-evidence-harness-concrete-plan.md: OK
infra/rp11-launch/build.sh: OK
infra/rp11-launch/launch.c: OK
infra/rp11-launch/select.h: OK
infra/rp11-launch/start.s: OK
infra/rp11-launch/rp11-launch.ld: OK
infra/rp11-launch/rp11-launch.x86_64.listing: OK
infra/rp11-launch/buildroot/provision.py: OK
infra/rp11-launch/buildroot/enter.py: OK
infra/rp11-launch/verify/cc1check.py: OK
infra/rp11-launch/verify/ic1check.py: OK
infra/rp11-launch/verify/elfcheck.py: OK
infra/rp11-launch/verify/tl11.py: OK
infra/rp11-launch/verify/ctverify.py: OK
infra/rp11-launch/verify/xdecode.py: OK
infra/rp11-launch/verify/xdecode-spelling.table: OK
infra/rp11-launch/verify/xdecode-corpus.txt: OK
infra/rp11-launch/test-harness/select_harness.c: OK
infra/rp11-launch/test-harness/select_shim.c: OK
tests/test_rp11_launch_toolchain.py: OK
tests/rp11_launch_support.py: OK
tools/phase_5_0_evidence/rp11_launch.py: OK
tools/phase_5_0_evidence/review_manifest.py: OK
S1.5 sha256sum-check exit=0
f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf 16509 infra/rp11-launch/toolchain.lock OK
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f 381913 infra/rp11-launch/build-root.manifest OK
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625 328 infra/rp11-launch/expected.sha256 OK
b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b 5120 infra/rp11-launch/verify/fixtures/cc1.v.baseline OK
c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c 376981 docs/review/phase-5-0-evidence-harness-review-manifest.json OK
f02b7acfa14b1c108ab53942bd3f89a9bd629eccb6c2c685419e07bf729dec3d 178810 docs/review/phase-5-0-evidence-harness-concrete-plan.md OK
7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0 2819 infra/rp11-launch/build.sh OK
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe 6314 infra/rp11-launch/launch.c OK
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b 2187 infra/rp11-launch/select.h OK
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139 857 infra/rp11-launch/start.s OK
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326 2321 infra/rp11-launch/rp11-launch.ld OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 21742 infra/rp11-launch/rp11-launch.x86_64.listing OK
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300 15106 infra/rp11-launch/buildroot/provision.py OK
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a 14521 infra/rp11-launch/buildroot/enter.py OK
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72 6021 infra/rp11-launch/verify/cc1check.py OK
ea7d9dd3d8e141349019cfdeba5e91df7569e28d6818136777f59bf313316917 18546 infra/rp11-launch/verify/ic1check.py OK
b742552c6d200dd1c0536f29a444dcc4a00405f758788bc82c8b2c4f2df2aceb 7695 infra/rp11-launch/verify/elfcheck.py OK
cb1b8d835983b625e8e42dda2d46aa2d5e56816cf90fb8c3a397e291c3d0e676 5432 infra/rp11-launch/verify/tl11.py OK
eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31 35036 infra/rp11-launch/verify/ctverify.py OK
84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97 54170 infra/rp11-launch/verify/xdecode.py OK
d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66 3806 infra/rp11-launch/verify/xdecode-spelling.table OK
f0e811a4bd61782789b66f31ab4401797e52b8ac00ffeebb984bfcd71afb4a8a 14292 infra/rp11-launch/verify/xdecode-corpus.txt OK
603099e0f7279e4158023a63b6bc1411c0d9d3ac7c9372c7f77fa9d42f0b0a94 2228 infra/rp11-launch/test-harness/select_harness.c OK
8c4ad99c0a1f3452923dab46149e7f4b202060ef5bf981b732ec9e9724dd91fd 950 infra/rp11-launch/test-harness/select_shim.c OK
ff3d458cabae91512562cca6143542337b1306dc3df791da505c51a9519ab76f 12326 tests/test_rp11_launch_toolchain.py OK
bc24c0ee7b0c9f58853479adc908c60cf013b9652409e3d5cee0d710074a18b6 8045 tests/rp11_launch_support.py OK
5a2f4694983619d6a3fb7ac3965e4415dd114fb7504003d91abb6071d189c2b1 15849 tools/phase_5_0_evidence/rp11_launch.py OK
311f1d0300e3e98f5b3b33ea6c4598bfc744ad8e9ba61bf0d2adb2d62f5c1844 73785 tools/phase_5_0_evidence/review_manifest.py OK
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S1.6 hashlib-and-tree-check exit=0
package_lines 62
archive_snapshot=20261001T000000Z
build_root_manifest_sha256=f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f
entry_mechanism=bubblewrap 0.9.0 (Ubuntu 24.04 host package, unprivileged user namespace; --unshare-all --die-with-parent --new-session --clearenv, root bound read-only at /); informative, not a pin (HA-3)
S1.7 lock-facts exit=0
30 28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526 True c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c False
S1.8 in-memory-review-manifest exit=0
/usr/bin/rsync
/usr/bin/ssh
S1.9 local-tools exit=0
S1 block exit=0
S1.end end_utc=2026-10-03T11:51:06Z
S1.end date exit=0
S1 final exit=0
```

### Step 2 block (`oracle-test`):
Status: final exit 0
Transcript:
```text
S2.trap exit=0
S2.start start_utc=2026-10-03T12:08:50Z
S2.start date exit=0
2026-10-03T12:08:50Z
S2.1 date exit=0
Linux 7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug  1 04:26:38 UTC 2026 x86_64
S2.2 uname exit=0
Linux version 7.0.0-31-generic (buildd@lcy02-amd64-091) (x86_64-linux-gnu-gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0, GNU ld (GNU Binutils for Ubuntu) 2.46) #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug  1 04:26:38 UTC 2026
S2.3 proc-version exit=0
Architecture:                            x86_64
CPU op-mode(s):                          32-bit, 64-bit
Address sizes:                           40 bits physical, 48 bits virtual
Byte Order:                              Little Endian
CPU(s):                                  2
On-line CPU(s) list:                     0,1
Vendor ID:                               AuthenticAMD
Model name:                              AMD EPYC 7551 32-Core Processor
CPU family:                              23
Model:                                   1
Thread(s) per core:                      2
Core(s) per socket:                      1
Socket(s):                               1
Stepping:                                2
BogoMIPS:                                3992.49
Flags:                                   fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm rep_good nopl xtopology cpuid extd_apicid tsc_known_freq pni pclmulqdq ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm cmp_legacy svm cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw topoext perfctr_core ssbd ibpb vmmcall fsgsbase tsc_adjust bmi1 avx2 smep bmi2 rdseed adx smap clflushopt sha_ni xsaveopt xsavec xgetbv1 clzero xsaveerptr virt_ssbd arat npt nrip_save vgif overflow_recov succor arch_capabilities
Virtualization:                          AMD-V
Hypervisor vendor:                       KVM
Virtualization type:                     full
L1d cache:                               64 KiB (1 instance)
L1i cache:                               64 KiB (1 instance)
L2 cache:                                512 KiB (1 instance)
L3 cache:                                16 MiB (1 instance)
NUMA node(s):                            1
NUMA node0 CPU(s):                       0,1
Vulnerability Gather data sampling:      Not affected
Vulnerability Ghostwrite:                Not affected
Vulnerability Indirect target selection: Not affected
Vulnerability Itlb multihit:             Not affected
Vulnerability L1tf:                      Not affected
Vulnerability Mds:                       Not affected
Vulnerability Meltdown:                  Not affected
Vulnerability Mmio stale data:           Not affected
Vulnerability Old microcode:             Not affected
Vulnerability Reg file data sampling:    Not affected
Vulnerability Retbleed:                  Mitigation; untrained return thunk; SMT vulnerable
Vulnerability Spec rstack overflow:      Vulnerable: Safe RET, no microcode
Vulnerability Spec store bypass:         Mitigation; Speculative Store Bypass disabled via prctl
Vulnerability Spectre v1:                Mitigation; usercopy/swapgs barriers and __user pointer sanitization
Vulnerability Spectre v2:                Mitigation; Retpolines; IBPB conditional; STIBP disabled; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected
Vulnerability Srbds:                     Not affected
Vulnerability Tsa:                       Not affected
Vulnerability Tsx async abort:           Not affected
Vulnerability Vmscape:                   Not affected
S2.4 lscpu exit=0
vendor_id	: AuthenticAMD
cpu family	: 23
model		: 1
model name	: AMD EPYC 7551 32-Core Processor
stepping	: 2
microcode	: 0x8001279
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm rep_good nopl xtopology cpuid extd_apicid tsc_known_freq pni pclmulqdq ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm cmp_legacy svm cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw topoext perfctr_core ssbd ibpb vmmcall fsgsbase tsc_adjust bmi1 avx2 smep bmi2 rdseed adx smap clflushopt sha_ni xsaveopt xsavec xgetbv1 clzero xsaveerptr virt_ssbd arat npt nrip_save vgif overflow_recov succor arch_capabilities
S2.5 cpuinfo-first-processor exit=0
bubblewrap 0.11.1
S2.6 bwrap-version exit=0
755 root:root 80424 /usr/bin/bwrap
S2.7 bwrap-stat exit=0
a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361  /usr/bin/bwrap
S2.8 bwrap-sha256 exit=0
bubblewrap 0.11.1-1ubuntu0.3
S2.9 bwrap-package exit=0
S2.10a max_user_namespaces-read exit=0
max_user_namespaces=3354
S2.10b max_user_namespaces-positive exit=0
apparmor_restrict_unprivileged_userns=1
S2.11 apparmor-userns exit=0
uid=1001(ubuntu) gid=1001(ubuntu) groups=1001(ubuntu),4(adm),24(cdrom),27(sudo),30(dip),102(lxd),986(freedomlab)
S2.12 id exit=0
Test
S2.13 hostname exit=0
PRETTY_NAME="Ubuntu 26.04.1 LTS"
NAME="Ubuntu"
VERSION_ID="26.04"
VERSION="26.04.1 LTS (Resolute Raccoon)"
VERSION_CODENAME=resolute
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=resolute
LOGO=ubuntu-logo
S2.14 os-release exit=0
MemTotal:         973580 kB
S2.15 memtotal exit=0
real-time non-blocking time  (microseconds, -R) unlimited
core file size              (blocks, -c) 0
data seg size               (kbytes, -d) unlimited
scheduling priority                 (-e) 0
file size                   (blocks, -f) unlimited
pending signals                     (-i) 3354
max locked memory           (kbytes, -l) 8192
max memory size             (kbytes, -m) unlimited
open files                          (-n) 1024
pipe size                (512 bytes, -p) 8
POSIX message queues         (bytes, -q) 819200
real-time priority                  (-r) 0
stack size                  (kbytes, -s) 8192
cpu time                   (seconds, -t) unlimited
max user processes                  (-u) 3354
virtual memory              (kbytes, -v) unlimited
file locks                          (-x) unlimited
S2.16 ulimit-soft exit=0
real-time non-blocking time  (microseconds, -R) unlimited
core file size              (blocks, -c) unlimited
data seg size               (kbytes, -d) unlimited
scheduling priority                 (-e) 0
file size                   (blocks, -f) unlimited
pending signals                     (-i) 3354
max locked memory           (kbytes, -l) 8192
max memory size             (kbytes, -m) unlimited
open files                          (-n) 524288
pipe size                (512 bytes, -p) 8
POSIX message queues         (bytes, -q) 819200
real-time priority                  (-r) 0
stack size                  (kbytes, -s) unlimited
cpu time                   (seconds, -t) unlimited
max user processes                  (-u) 3354
virtual memory              (kbytes, -v) unlimited
file locks                          (-x) unlimited
S2.17 ulimit-hard exit=0
Filesystem     1024-blocks  Used Available Capacity Mounted on
tmpfs               486792  4900    481892       2% /tmp
S2.18 df-tmp exit=0
Python 3.12.14 (main, Sep  1 2026, 14:16:52) [Clang 22.1.3 ]
S2.19 python-version exit=0
8.4.2
S2.20 pytest-version exit=0
/usr/bin/zstd
/usr/bin/gpgv
/usr/bin/rsync
/usr/bin/lscpu
S2.21 required-tools exit=0
*** Zstandard CLI (64-bit) v1.5.7, by Yann Collet ***
S2.22 zstd-version exit=0
gpgv (GnuPG) 2.4.8
libgcrypt 1.12.0
Copyright (C) 2025 g10 Code GmbH
License GNU GPL-3.0-or-later <https://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
S2.23 gpgv-version exit=0
80a36b0a6de2f69f49d2df75ef473ccde121e9e190b9ea01d20a4f63778d5c31  /usr/share/keyrings/ubuntu-archive-keyring.gpg
S2.24 keyring-sha256 exit=0
run_prefix_entries=none
S2.25 run-prefix-absent exit=0
S2 block exit=0
S2.end end_utc=2026-10-03T12:08:52Z
S2.end date exit=0
S2 final exit=0
```

### Step 3 block (`oracle-test`):
Status: final exit 0
Transcript:
```text
S3.trap exit=0
S3.start start_utc=2026-10-03T12:09:13Z
S3.start date exit=0
HA-1 kernel_release=7.0.0-31-generic
HA-2 model_names=AMD EPYC 7551 32-Core Processor
HA-1 qualifies=yes
HA-2 qualifies=yes
HA-3 qualifies=no (version-only differences do not qualify; section 4.2)
S3.1 qualification exit=0
S3 block exit=0
S3.end end_utc=2026-10-03T12:09:13Z
S3.end date exit=0
S3 final exit=0
```

### Step 4a block (`oracle-test`):
Status: final exit 0
Transcript:
```text
S4a.trap exit=0
S4a.start start_utc=2026-10-03T12:10:43Z
S4a.start date exit=0
S4a.1 mkdir exit=0
700 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout
700 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-index
700 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-cache
700 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-root
700 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-work
700 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-evidence
S4a.2 stat exit=0
S4a block exit=0
S4a.end end_utc=2026-10-03T12:10:43Z
S4a.end date exit=0
S4a final exit=0
```

### Step 4b — S4b.start timestamp block (repository host):
Status: final exit 0
Transcript:
```text
S4b.start start_utc=2026-10-03T12:10:43Z
S4b.start date exit=0
S4b.start block exit=0
```

### Step 4b — Synchronization command (repository host):
Exit status: `0`
Summary lines:
```text
sent 62,801,705 bytes  received 94,488 bytes  5,990,113.62 bytes/sec
total size is 86,175,864  speedup is 1.37
```

### Step 4b — S4b.end timestamp block (repository host):
Status: final exit 0
Transcript:
```text
S4b.end end_utc=2026-10-03T12:10:54Z
S4b.end date exit=0
S4b.end block exit=0
```

### Step 4c block (repository host):
Status: final exit 0
Transcript:
```text
S4c.trap exit=0
S4c.start start_utc=2026-10-03T12:10:54Z
S4c.start date exit=0
S4c.1 cd exit=0
repository_state=clean
S4c.2 repository-state exit=0
infra/rp11-launch/toolchain.lock: OK
infra/rp11-launch/build-root.manifest: OK
infra/rp11-launch/expected.sha256: OK
infra/rp11-launch/verify/fixtures/cc1.v.baseline: OK
docs/review/phase-5-0-evidence-harness-review-manifest.json: OK
docs/review/phase-5-0-evidence-harness-concrete-plan.md: OK
infra/rp11-launch/build.sh: OK
infra/rp11-launch/launch.c: OK
infra/rp11-launch/select.h: OK
infra/rp11-launch/start.s: OK
infra/rp11-launch/rp11-launch.ld: OK
infra/rp11-launch/rp11-launch.x86_64.listing: OK
infra/rp11-launch/buildroot/provision.py: OK
infra/rp11-launch/buildroot/enter.py: OK
infra/rp11-launch/verify/cc1check.py: OK
infra/rp11-launch/verify/ic1check.py: OK
infra/rp11-launch/verify/elfcheck.py: OK
infra/rp11-launch/verify/tl11.py: OK
infra/rp11-launch/verify/ctverify.py: OK
infra/rp11-launch/verify/xdecode.py: OK
infra/rp11-launch/verify/xdecode-spelling.table: OK
infra/rp11-launch/verify/xdecode-corpus.txt: OK
infra/rp11-launch/test-harness/select_harness.c: OK
infra/rp11-launch/test-harness/select_shim.c: OK
tests/test_rp11_launch_toolchain.py: OK
tests/rp11_launch_support.py: OK
tools/phase_5_0_evidence/rp11_launch.py: OK
tools/phase_5_0_evidence/review_manifest.py: OK
S4c.3 sha256sum-check exit=0
S4c block exit=0
S4c.end end_utc=2026-10-03T12:10:54Z
S4c.end date exit=0
S4c final exit=0
```

### Step 4d block (`oracle-test`):
Status: final exit 0
Transcript:
```text
S4d.trap exit=0
S4d.start start_utc=2026-10-03T12:10:54Z
S4d.start date exit=0
2775 ubuntu:ubuntu /tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout
S4d.1 checkout-stat exit=0
S4d.2 cd exit=0
infra/rp11-launch/toolchain.lock: OK
infra/rp11-launch/build-root.manifest: OK
infra/rp11-launch/expected.sha256: OK
infra/rp11-launch/verify/fixtures/cc1.v.baseline: OK
docs/review/phase-5-0-evidence-harness-review-manifest.json: OK
docs/review/phase-5-0-evidence-harness-concrete-plan.md: OK
infra/rp11-launch/build.sh: OK
infra/rp11-launch/launch.c: OK
infra/rp11-launch/select.h: OK
infra/rp11-launch/start.s: OK
infra/rp11-launch/rp11-launch.ld: OK
infra/rp11-launch/rp11-launch.x86_64.listing: OK
infra/rp11-launch/buildroot/provision.py: OK
infra/rp11-launch/buildroot/enter.py: OK
infra/rp11-launch/verify/cc1check.py: OK
infra/rp11-launch/verify/ic1check.py: OK
infra/rp11-launch/verify/elfcheck.py: OK
infra/rp11-launch/verify/tl11.py: OK
infra/rp11-launch/verify/ctverify.py: OK
infra/rp11-launch/verify/xdecode.py: OK
infra/rp11-launch/verify/xdecode-spelling.table: OK
infra/rp11-launch/verify/xdecode-corpus.txt: OK
infra/rp11-launch/test-harness/select_harness.c: OK
infra/rp11-launch/test-harness/select_shim.c: OK
tests/test_rp11_launch_toolchain.py: OK
tests/rp11_launch_support.py: OK
tools/phase_5_0_evidence/rp11_launch.py: OK
tools/phase_5_0_evidence/review_manifest.py: OK
S4d.3 sha256sum-check exit=0
f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf 16509 infra/rp11-launch/toolchain.lock OK
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f 381913 infra/rp11-launch/build-root.manifest OK
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625 328 infra/rp11-launch/expected.sha256 OK
b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b 5120 infra/rp11-launch/verify/fixtures/cc1.v.baseline OK
c9afaf7cd32a398e9714e39779fef522d6af053ec71cd2c403e0a4c2eaba4b5c 376981 docs/review/phase-5-0-evidence-harness-review-manifest.json OK
f02b7acfa14b1c108ab53942bd3f89a9bd629eccb6c2c685419e07bf729dec3d 178810 docs/review/phase-5-0-evidence-harness-concrete-plan.md OK
7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0 2819 infra/rp11-launch/build.sh OK
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe 6314 infra/rp11-launch/launch.c OK
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b 2187 infra/rp11-launch/select.h OK
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139 857 infra/rp11-launch/start.s OK
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326 2321 infra/rp11-launch/rp11-launch.ld OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 21742 infra/rp11-launch/rp11-launch.x86_64.listing OK
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300 15106 infra/rp11-launch/buildroot/provision.py OK
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a 14521 infra/rp11-launch/buildroot/enter.py OK
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72 6021 infra/rp11-launch/verify/cc1check.py OK
ea7d9dd3d8e141349019cfdeba5e91df7569e28d6818136777f59bf313316917 18546 infra/rp11-launch/verify/ic1check.py OK
b742552c6d200dd1c0536f29a444dcc4a00405f758788bc82c8b2c4f2df2aceb 7695 infra/rp11-launch/verify/elfcheck.py OK
cb1b8d835983b625e8e42dda2d46aa2d5e56816cf90fb8c3a397e291c3d0e676 5432 infra/rp11-launch/verify/tl11.py OK
eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31 35036 infra/rp11-launch/verify/ctverify.py OK
84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97 54170 infra/rp11-launch/verify/xdecode.py OK
d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66 3806 infra/rp11-launch/verify/xdecode-spelling.table OK
f0e811a4bd61782789b66f31ab4401797e52b8ac00ffeebb984bfcd71afb4a8a 14292 infra/rp11-launch/verify/xdecode-corpus.txt OK
603099e0f7279e4158023a63b6bc1411c0d9d3ac7c9372c7f77fa9d42f0b0a94 2228 infra/rp11-launch/test-harness/select_harness.c OK
8c4ad99c0a1f3452923dab46149e7f4b202060ef5bf981b732ec9e9724dd91fd 950 infra/rp11-launch/test-harness/select_shim.c OK
ff3d458cabae91512562cca6143542337b1306dc3df791da505c51a9519ab76f 12326 tests/test_rp11_launch_toolchain.py OK
bc24c0ee7b0c9f58853479adc908c60cf013b9652409e3d5cee0d710074a18b6 8045 tests/rp11_launch_support.py OK
5a2f4694983619d6a3fb7ac3965e4415dd114fb7504003d91abb6071d189c2b1 15849 tools/phase_5_0_evidence/rp11_launch.py OK
311f1d0300e3e98f5b3b33ea6c4598bfc744ad8e9ba61bf0d2adb2d62f5c1844 73785 tools/phase_5_0_evidence/review_manifest.py OK
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S4d.4 hashlib-and-tree-check exit=0
S4d block exit=0
S4d.end end_utc=2026-10-03T12:10:54Z
S4d.end date exit=0
S4d final exit=0
```

### Step 5 block (`oracle-test`):
Status: final exit 1
Transcript:
```text
S5.trap exit=0
S5.start start_utc=2026-10-03T12:13:10Z
S5.start date exit=0
S5.1 cd exit=0
S5.2 resolve exit=0
S5.3 lock-package-lines exit=0
S5.4 resolve-equals-lock exit=0
S5.5 install exit=1
S5.end end_utc=2026-10-03T12:13:38Z
S5.end date exit=0
S5 final exit=1
```

Stderr from `install`:
```text
Traceback (most recent call last):
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 399, in <module>
    sys.exit(main(sys.argv[1:]))
             ^^^^^^^^^^^^^^^^^^
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 394, in main
    install(args.lock, args.root, args.cache)
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 349, in install
    _unpack(_data_tar(data), root)
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 326, in _unpack
    shutil.copyfileobj(src, out)
  File "/home/ubuntu/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu/lib/python3.12/shutil.py", line 204, in copyfileobj
    fdst_write(buf)
OSError: [Errno 122] Disk quota exceeded
```

### Steps 6 through 11:
Not run due to HARD STOP at Step 5.

### Step 12a — S12.start timestamp block (repository host):
Status: final exit 0
Transcript:
```text
S12.start start_utc=2026-10-03T12:14:46Z
S12.start date exit=0
S12.start block exit=0
```

---

## 7. Synchronization and provisioning evidence (§10 item 7)

- **Synchronization exit status:** `0`
- **Synchronization summary:**
  `sent 62,801,705 bytes  received 94,488 bytes  5,990,113.62 bytes/sec`
  `total size is 86,175,864  speedup is 1.37`
- **Download source:** `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z/`
- **`resolve` signature gate:** Exit 0 (InRelease signed by archive keyring verified by `gpgv`, `Packages.xz` digest verified against InRelease, seed set resolved to exactly 62 package lines).
- **`cmp resolve.out lock-packages.txt`:** Exit 0 (byte-identical to committed `toolchain.lock` package lines).
- **`install` result:** Exit 1 (`OSError: [Errno 122] Disk quota exceeded`). Insufficient disk space on `oracle-test:/tmp` (`tmpfs` of 486,792 kB).
- **Cache accounting (S5.6):** Not run.

---

## 8. Same-invocation R-1/R-2 evidence (§10 item 8)

Not run due to HARD STOP at Step 5.

---

## 9. Normative output digests and byte comparisons (§10 item 9)

Not run due to HARD STOP at Step 5.

---

## 10. `cc1.v` comparison and verification (§10 item 10)

Not run due to HARD STOP at Step 5.

---

## 11. Corroborating toolchain test results (§10 item 11)

Not run due to HARD STOP at Step 5.

---

## 12. Stopped, invalid or unexplained conditions (§10 item 12)

**HARD STOP at Step 5 (S5.5 install exit=1, S5 final exit=1):**

Prerequisite failure: Disk space exhausted on `oracle-test:/tmp`.
`/tmp` is mounted as a `tmpfs` with 486,792 kB total capacity (observed in S2.18).
During `provision.py install`, as packages were being downloaded to `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-cache` and unpacked into `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-root`, disk space was exhausted:

```text
Traceback (most recent call last):
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 399, in <module>
    sys.exit(main(sys.argv[1:]))
             ^^^^^^^^^^^^^^^^^^
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 394, in main
    install(args.lock, args.root, args.cache)
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 349, in install
    _unpack(_data_tar(data), root)
  File "/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout/infra/rp11-launch/buildroot/provision.py", line 326, in _unpack
    shutil.copyfileobj(src, out)
  File "/home/ubuntu/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu/lib/python3.12/shutil.py", line 204, in copyfileobj
    fdst_write(buf)
OSError: [Errno 122] Disk quota exceeded
```

Governing assignment rules applied:
- §6.0 Status meanings: "Every other nonzero status, whether from a tool or from a conditional below, is a HARD STOP (§8.3)."
- §7.2: "If a prerequisite such as bubblewrap, unprivileged user namespaces, the pinned Python environment, pytest, rsync, zstd, gpgv, the archive keyring, network reachability of the snapshot or disk space is unavailable, the executor stops and reports. This assignment grants no ambient authority to repair it."
- §8.3: "The executor stops at the first one and does not continue to later steps, apart from the S4b.end block and step 12 (§6 step 12)."

No remediation, retry, cleanup or modification was attempted.

---

## 13. Retained evidence locations and cleanup state (§10 item 13, §10.1)

Retained on `oracle-test`:
- Checkout: `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout`
- Index cache: `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-index`
- Package cache: `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-cache`
- Partial build root: `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-root`
- Work directory: `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-work`
- Evidence directory: `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-evidence`

**Cleanup state:**
Nothing has been deleted; all created directories stay in place on `oracle-test` pending maintainer review and Peter Duscha's direction.
The repository working tree was synchronized into `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-checkout`, directories were created, packages were downloaded into `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-cache`, and `oracle-test`'s `/tmp` changed. The host was not left in its pre-run state.

---

## 14. Verdict (§8, §10 item 14)

Verdict: **HARD STOP**

Precedence (§8): HARD STOP over INVALID RUN over PASS.

Evaluation against §8.1 conditions:
1. **Executor independence attestation complete (§2):** Satisfied (§1).
2. **Every block and synchronization command ran in order, once, each exited 0:** **NOT SATISFIED**. Step 5 exited 1 (`S5.5 install exit=1`, `S5 final exit=1`) due to disk space exhaustion on `/tmp`.
3. **Every one of the 15 timed scopes has its start and end value printed with status 0, handback ends with exact closing record:** Steps 1–5 and 12 recorded; steps 6–11 were not run due to HARD STOP; step-12 end and whole-run end are in closing record.
4. **HA-1 or HA-2 qualified under §4.2:** Satisfied (both HA-1 and HA-2 qualified).
5. **Same-invocation R-1/R-2 gate passed and regenerated manifest byte-equal:** Not run (blocked by HARD STOP at Step 5).
6. **Normative outputs match expected.sha256, listing byte-equal:** Not run (blocked by HARD STOP at Step 5).
7. **`cc1.v` byte-identical to accepted baseline (`cc1check.py PASS`):** Not run (blocked by HARD STOP at Step 5).
8. **Corroborating tests report 12 tests, 0 failures, 0 errors, 0 skipped:** Not run (blocked by HARD STOP at Step 5).
9. **No unexplained difference remains:** Satisfied. The failure is fully explained prerequisite exhaustion (`OSError: [Errno 122] Disk quota exceeded` on `oracle-test:/tmp`).

The verdict of record is **HARD STOP**.

---

## 15. Product and governance status statements (§10 item 15)

- RP-11 remains unwired and unmet.
- `plan.is_executable=False`.
- PO-9 and PO-14 remain open.
- Package 5.0 is not ready.
- No installation, operational, harness `--execute`, privileged, commit or push authority was exercised.

---

## 16. Stop gate and handback disposition (§10 item 16, §11)

Execution stops immediately with this handback.
R-5 is not accepted and D9-3 is not complete.
All actions cease pending independent review by Codex and decision by Peter Duscha.

## Closing record (written by the S12.end block)

~~~text
S12.end.3 open-record exit=0
S12.end end_utc=2026-10-03T12:16:06Z
RUN.end end_utc=2026-10-03T12:16:06Z
S12.end.4 date exit=0
~~~
