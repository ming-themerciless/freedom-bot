# Claude handback — I-7 zero-`ret` static launcher and independent decoder

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-I7`

Date: 2026-10-01

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)

Controlling design (normative, read unchanged):
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md),
with LD-7, LD-8 and LD-9 as decided in
[`project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md`](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
and [`project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md`](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md).

State: **returned for independent Codex review. Claude has stopped.** Nothing
is committed, pushed, installed or wired. **PO-9 and PO-14 remain open; RP-11
remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; Package 5.0 remains not ready.** R-5, XD-9, XD-11, D9-1 … D9-4,
PO-9, PO-14, PO-17 and PO-18 are **not** claimed.

## 1. Summary

The accepted D-S1 design is implemented as repository text, and its first
build passes every mechanical check **without any fail-closed alternative**:
FA-1 and FA-3 were not needed.

* **Image.** `rp11-launch`, 2 368 bytes, SHA-256
  `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`.
  `.text` is 1 295 bytes, 332 instructions: `_start` (27 bytes, 7
  instructions) and `rp11_main` (1 268 bytes), which tile `.text` exactly.
  **No `call`, no `ret`, no indirect transfer; one direct entry `jmp`.**
* **XD** decodes the image bytes under a closed 116-row table written from the
  Intel SDM (325383-093US) and AMD APM (24594 r3.20), and agrees exactly with
  the committed listing on all 332 instructions (T-L11). Its 208-vector T-L12
  corpus covers every row, every forbidden form named by XD-10 and every XD-5
  class.
* **T-L10** passes over the agreed stream, and gives byte-identical tables
  over XD's own stream. The 200-byte frame and 223-byte maximum stack depth
  are within the 512 and 1 024 bounds. All 55 stores map to named frame
  objects. All 29 system-call sites resolve to the §5.4 inventory with NULL
  output pointers. Every refusal writes its exact line, then calls
  `exit_group(status)`, then `ud2`.
* **Build boundary.** A 62-package Ubuntu 26.04 root, pinned at snapshot
  `20261001T000000Z`, is bound file by file (3 641-line manifest).
  * Three independent provisionings reproduced the committed manifest byte
    for byte, the last from the committed lock alone with a fresh download.
  * R-2 and the three R-4 variations reproduce all outputs byte for byte.
  * **IC-1 passes, with two environment additions the design text did not
    foresee** (§6, D-2), named for your decision.
* **Manifest** 26 → **27**: the contract module and nine launcher files are
  covered, and an `rp11_launch` section is serialised. The checked-in JSON
  and concrete plan were regenerated through the dry-run path, and the
  digest is
  `87507cc7a26e3b87ad4f19880c3a4ae93faa0fc022fbd9d8b09210aab987e0d0`.

One decision was taken during the work, by Peter Duscha (AskUserQuestion,
2026-10-01): `entry_environment.py` does not exist (R2 slice I-6 is
unimplemented). So T-L2 compares the C literals with the new contract module,
transcribed from R2, and the `entry_environment` half remains owed by I-6.

## 2. Requirements implemented → files

| Prompt §3 item | Implemented in |
|---|---|
| 1. source and build inputs (§5.2) | `infra/rp11-launch/start.s`, `launch.c`, `select.h`, `rp11-launch.ld`, `build.sh`, `toolchain.lock`, `build-root.manifest`, `expected.sha256`, `rp11-launch.x86_64.listing` |
| 2. zero-`ret` form from the first build | the same; verified by XD, T-L11, T-L10 (§4) |
| 3. state machine, literals, statuses, bounds, signals, syscalls, stack and input discipline (§§5.4–5.10, §5.14) | `launch.c`, `select.h`, `start.s`; contract data in `tools/phase_5_0_evidence/rp11_launch.py` |
| 4. pinned build root and reproducibility (§§5.3.1–5.3.8), IC-1, HA-1 … HA-5 | `infra/rp11-launch/buildroot/provision.py` (X-1/X-2), `buildroot/enter.py` (X-3), `verify/ic1check.py`; lock and manifest |
| 5. T-L1 … T-L10, listing-based control-transfer verifier | `tests/test_rp11_launch_source.py` (T-L1 … T-L4, T-L10), `tests/test_rp11_launch_toolchain.py` (T-L5 … T-L9), `verify/ctverify.py` (T-L10), `verify/elfcheck.py` (T-L7) |
| 6. XD and its spelling table (§5.15) | `verify/xdecode.py`, `verify/xdecode-spelling.table` |
| 7. T-L11 and T-L12 | `verify/tl11.py`, `verify/xdecode-corpus.txt`; tests in both test files |
| 8. tests, manifest coverage, deterministic artifacts | `tools/phase_5_0_evidence/review_manifest.py` (v27), `tests/phase_5_0_evidence/test_no_execution.py`, `test_concrete_plan.py`, `test_r16_remediation.py`; regenerated `docs/review/phase-5-0-evidence-harness-review-manifest.json` and `…-concrete-plan.md` |
| T-L8 shim and harness | `infra/rp11-launch/test-harness/select_shim.c`, `select_harness.c`; `tests/rp11_launch_support.py` (reference model) |

### 2.1 Exact files changed

New (SHA-256, lines):

| File | SHA-256 | Lines |
|---|---|---|
| `infra/rp11-launch/start.s` | `ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139` | 23 |
| `infra/rp11-launch/launch.c` | `6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe` | 224 |
| `infra/rp11-launch/select.h` | `34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b` | 75 |
| `infra/rp11-launch/rp11-launch.ld` | `ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326` | 58 |
| `infra/rp11-launch/build.sh` | `7c8fc6da367e9fa9a8bb639ace7aa19da41db306fd62757ab86f0716b1b738e0` | 58 |
| `infra/rp11-launch/toolchain.lock` | `ea4c5872b79f4ac033a1a99e67fd8160bf160d8d654ee8196b39c164072d411d` | 96 |
| `infra/rp11-launch/build-root.manifest` | `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` | 3 641 |
| `infra/rp11-launch/expected.sha256` | `6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625` | 4 |
| `infra/rp11-launch/rp11-launch.x86_64.listing` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | 421 |
| `infra/rp11-launch/test-harness/select_shim.c` | `8c4ad99c0a1f3452923dab46149e7f4b202060ef5bf981b732ec9e9724dd91fd` | 27 |
| `infra/rp11-launch/test-harness/select_harness.c` | `603099e0f7279e4158023a63b6bc1411c0d9d3ac7c9372c7f77fa9d42f0b0a94` | 86 |
| `infra/rp11-launch/verify/xdecode.py` | `84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97` | 1 292 |
| `infra/rp11-launch/verify/xdecode-spelling.table` | `d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66` | 173 |
| `infra/rp11-launch/verify/xdecode-corpus.txt` | `f0e811a4bd61782789b66f31ab4401797e52b8ac00ffeebb984bfcd71afb4a8a` | 259 |
| `infra/rp11-launch/verify/ctverify.py` | `eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31` | 849 |
| `infra/rp11-launch/verify/elfcheck.py` | `b742552c6d200dd1c0536f29a444dcc4a00405f758788bc82c8b2c4f2df2aceb` | 179 |
| `infra/rp11-launch/verify/ic1check.py` | `2e35bed7de0905c373514ae60048983718d15082cf1dabf11237dbba85a89769` | 258 |
| `infra/rp11-launch/verify/tl11.py` | `cb1b8d835983b625e8e42dda2d46aa2d5e56816cf90fb8c3a397e291c3d0e676` | 115 |
| `infra/rp11-launch/buildroot/provision.py` | `40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300` | 399 |
| `infra/rp11-launch/buildroot/enter.py` | `66c8f5b11a50d2b20eac3c29cb29de7f1cb3b27997e74669967e12e74acade10` | 266 |
| `tools/phase_5_0_evidence/rp11_launch.py` | `37d3e8dbd25fbff1f350583a0093b9c0cb1d0a6d3687d785b3f57b6567ead2d8` | 232 |
| `tests/rp11_launch_support.py` | `5985491ebc6d79846486c00f7115721e7bdf337aeecfd0cc72707170391bcc9a` | 140 |
| `tests/test_rp11_launch_source.py` | `8767ff315d578f7c0c30305850192ec712f151331cc28f38a3b13836ffdf26d9` | 656 |
| `tests/test_rp11_launch_toolchain.py` | `a54795bbeb9e87036a938270a7f59ab13252b7305e4df92306ab97aa81f2e480` | 223 |

Modified:

| File | After SHA-256 | Change |
|---|---|---|
| `tools/phase_5_0_evidence/review_manifest.py` | `aa32e57c82d9f8d90cd718a8fbb2601f9ab7559c81bb280207793fe4011311a4` | `MANIFEST_VERSION` 26 → 27 and its history entry; `RP11_LAUNCH_COVERED` (nine files) appended to `COVERED_SOURCES`, plus `rp11_launch.py`; `rp11_launch` body section |
| `tests/phase_5_0_evidence/test_no_execution.py` | `f2acbd0766f3af9745601769414e68f2953ef7467a4f7d07e6d3a3af246852eb` | declares `rp11_launch` in the planning tier, with its reason. Every planning-tier guard now applies to it, and none was relaxed |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | `05682fcac9528da83e749ce12075dae81864d923d38db12cc22e85b069a4bb1f` | covered set = the package exactly ∪ the enumerated launcher files, disjoint, without duplicates (D-6) |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | `4f3bdf25d8c0b9ee9faf29ab6e3bb90377cd84cb2963b9e60c84094d867c2830` | version pin 26 → 27, with its history comment |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | `add5524b…` → `8b2c448114da651687974636b5559e38507311f6c5e7a8502fdd0b26acdda464` | regenerated (dry run) |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | `c3591e65…` → `eca1da8354d63cac6507c3c1dcd618d87bfe1a3884a023f29c2665e969c3263a` | regenerated (dry run); only its digest line changes |

Current-state pointers: §11.

## 3. Toolchain and build-root provenance

| Item | Value |
|---|---|
| distribution | Ubuntu 26.04 `resolute`, `main`, `amd64`, release pocket only |
| archive snapshot | `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z` |
| archive signature | `InRelease` verified by host `gpgv` against the host Ubuntu archive keyring: "Good signature … Ubuntu Archive Automatic Signing Key (2018)", key `F6ECB376…991BC93C`. `Packages.xz` digest checked against `InRelease`, and every package digest against the index and the lock |
| packages | 62, all recorded with version, package-file SHA-256 and pool path in the lock. Seeds: `base-files base-passwd dash coreutils-from-gnu findutils libc-bin gcc-15 binutils libc6-dev strace`; the rest is the Pre-Depends/Depends closure |
| compiler | `gcc-15` 15.2.0-16ubuntu1 (driver `b5f1b773…`, `cc1` `30510b34…`) |
| binutils | 2.46-3ubuntu2 (`as` `4e5fcaa3…`, `ld.bfd` `97f48d93…`, `objdump` `44f07f8d…`, `readelf` `c8573396…`) |
| `/bin/sh` | dash 0.5.12-12ubuntu3 (`c6262295…`); `/usr/bin/env`, `sha256sum` from GNU coreutils 9.7; `find` 4.10.0; `strace` 6.19 |
| tree manifest | `rp11-build-root/1`, 3 641 lines, SHA-256 `f08ba9de…c38e76f`, which is also `build_root_manifest_sha256` in the lock |
| maintainer scripts | **not run.** Fixed provisioning steps replace them (`provision.py` docstring): `passwd`/`group` from base-passwd's masters plus `rp11build` (1000) and `rp11alt` (1001); `/tmp` and `/var/tmp` empty at 1777; three empty mount points under `/rp11`; `ld.so.cache` from the root's own `ldconfig -X -i` (aux cache removed) |
| entry mechanism (X-3) | `bubblewrap 0.9.0` (host package), unprivileged user namespace, `--unshare-all --die-with-parent --new-session --clearenv`, root bound **read-only** at `/`. Informative, not a pin (HA-3) |
| build host (HA-1, HA-2) | kernel `6.8.0-139-generic` (Ubuntu 24.04.4 host); CPU AMD EPYC-Milan |
| XD sources | Intel SDM Vol. 2, **325383-093US**, fetched from `cdrdv2.intel.com` (getContent 671110), SHA-256 `d137a788…cca1516`. AMD APM Vol. 3, **24594 r3.20 (May 2013)**, a copy hosted at `socsvn.freebsd.org` (AMD's portal was not reachable non-interactively), SHA-256 `0157e483…c818240`. Text read with `pdftotext` unpacked into scratch. Neither manual is committed |

No host package was installed or replaced, and no system configuration was
changed. Downloads and roots live in the session scratchpad.

## 4. Build outputs and T-L1 … T-L12

`expected.sha256` (R-3):

| Output | SHA-256 |
|---|---|
| `rp11-launch` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` |
| `rp11-launch.x86_64.listing` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` |
| `rp11-launch.map` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` |
| `launch.s` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` |
| `cc1.v` (compared, not expected; D-16) | `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` |

| Test | Result | Where |
|---|---|---|
| T-L1 source structure (SR-1 … SR-8) | **pass** (7 tests) | source file |
| T-L2 literal drift | **pass** (4 tests), **partial** by decision: against `rp11_launch.py`, not `entry_environment` (owed by I-6) | source file |
| T-L3 build definition, lock, manifest | **pass** (7 tests) | source file |
| T-L4 coarse listing screen | **pass** (3 tests), narrowed as D-4 | source file |
| T-L5 one build → expected digests | **pass** | toolchain file |
| T-L6 R-4(a) path, (b) time and mtimes, (c) user and host | **pass**: all five outputs identical | toolchain file |
| T-L7 BI-1 … BI-5, BI-8, BI-9, listing bytes = `.text` | **pass** | toolchain file |
| T-L8 compiled `select.h` vs reference model | **pass**: 4 029 cases (§5.6 table, §5.5 refusals and 4 000 seeded cases), of which 102 envp and 48 argv acceptances. Narrow as LD-7 accepts | toolchain file |
| T-L9 regenerated listing = committed listing | **pass** | toolchain file |
| T-L10 over the committed listing | **pass**; 13 injected violations each refused | source file (not evidence on its own, XD-7) |
| T-L11 XD agreement + T-L10 gate | **pass**: 332/332 instructions; three-way facts agree; T-L10 over XD's stream identical (tables `25779797…`); `tl10_evidence: true` | toolchain file; `verify/tl11.py` |
| T-L12 XD self-test | **pass**: 116 rows; 134 positive, 65 negative and 9 whole-`.text` vectors (208); ambiguous tables fail to load; spelling injectivity enforced | source file |

T-L11 record, over the built image and the committed listing:

```
image_sha256          04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  (= expected)
listing_sha256        8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188
xdecode_py_sha256     84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97
spelling_table_sha256 d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66
xd_table_sha256       e4aedd940b8935ae3684790beace7fc8ad75b430a3f39decf9126d8cf638ee86
ctverify_py_sha256    eea9f843ef87cabff7baafbd21a05e60742c1219741f6a56571ce152bd342a31
agreed_stream_sha256  e1354c29e4abddd115fad9b1f83fd69b3b93aae2971db6a448964baa8edbf8e0
interpreter           CPython 3.12.3 (/usr/bin/python3; venv-web python for pytest)
instructions 332; tl11 pass; tl10 pass; tl10_evidence true
```

**First-build XD verdict.** XD was run on the image bytes alone before the
listing was read. It passed: complete sweep, every instruction reached,
exactly one CT-4 `jmp`, and no instruction outside the table. The only T-L11
disagreement on first comparison was the listing's spelling `movabs` for MOV
r64, imm64 (`REX.W B8+rd io`), at the same boundary and with the same bytes.
It was resolved by a `form` entry in the spelling table, which is
presentation only and recorded in the file. No decoding change was made in
response to the listing.

## 5. HR-1 … HR-6: instruction, system-call, function and stack summary

**Functions.** `_start` `0x4000b0`+27 and `rp11_main` `0x4000cb`+1268, both
FUNC GLOBAL; `.text` `0x4000b0`+`0x50f`. The only other symbols are a FILE
symbol `launch.c` and the null symbol.

**Instruction list (the contract's permitted list, fixed from this build).**

* Non-transfer: `add and cmp cmpb dec inc lea mov movabs movb movl movq movw
  push shr sub test xor`.
* Transfer: `ja jbe je jne jmp syscall ud2`.
* Counts: mov 174, cmp 32, syscall 29, jne 28, xor 13, ud2 10, lea 10, je 8,
  test 7, inc 4, jbe 4, jmp 3, sub 2, push 2, and 2, add/dec/shr/ja 1 each.
* Of the three `jmp`s, one is CT-4 and two are intra-`rp11_main`.

**`_start`** — `xor %ebp,%ebp`; `mov (%rsp),%rdi`; `lea 0x8(%rsp),%rsi`;
`lea 0x10(%rsp,%rdi,8),%rdx`; `and $-16,%rsp`; `push $0`; `jmp rp11_main`.

* HR-6: it loads only `argc` at `0(%rsp)` (T-L10 load table: one frame load).
* It stores only the pushed zero, and reads nothing above `envp`'s
  terminator, so not the auxiliary vector.

**System calls** (T-L10 constant propagation with a zero-flag edge
refinement; HR-5). All 29 sites are in `rp11_main`:

| Site(s) | Call | Arguments resolved |
|---|---|---|
| `0x400214`, `0x40024a`, `0x400282` | fcntl (72) | fd 0, 1, 2; `F_GETFD` |
| `0x4002ba` | close_range (436) | 3, `0xffffffff`, 0 |
| `0x400326` | rt_sigaction (13) | `%rdi` the loop's signal (1 … 64 except 9 and 19, by the `0x40100` bitmask); `%rsi` → `sa`, 32 zero bytes; old action **NULL** (proved on the not-taken edge of `and $1,%edx; jne`); size 8 |
| `0x400378` | rt_sigprocmask (14) | `SIG_SETMASK`, `%rsi` → `mask` (8 zero bytes), old set **NULL**, size 8 |
| `0x4003a8` | umask (95) | `0077` |
| `0x4003b4` | chdir (80) | `"/"` |
| `0x400599` | execve (59) | `"/usr/bin/python3.12"`, `argv_out` (7 `.rodata` literals in order, then NULL), `envp_out` (`LC_ALL=C`, `PATH=/usr/bin`, `idbuf`, NULL) |
| 10 × write (1) | — | descriptor 2, `.rodata` line equal to the class line, length equal to §5.9's |
| 10 × exit_group (231) | — | 111, 112, 113 ×3, 114, 115 ×2, 116, 117. **Each is preceded immediately by its write and followed immediately by `ud2`**. There is no shared exit tail |

**Frame and stack (RI-4 … RI-6, HR-1 … HR-3).**

* `o(i)` in `rp11_main` takes only the values 0, 8 (`push %rbx`) and 200
  (`sub $0xc0,%rsp`). It is consistent at every join and never negative.
* Maximum depth is 223: 15 alignment + 8 + 200. The frame bound is 512 and
  the stack bound 1 024.
* All 55 stores map to frame objects (offsets from `rp11_main`'s entry
  `%rsp`). None is unexplained:

| Object | Bytes | Stores |
|---|---|---|
| `mask` | −192 … −185 | 1 (zero) |
| `envp_out[4]` | −184 … −153 | 4: `LC_ALL=C`, `PATH=/usr/bin`, frame −120 (`idbuf`), 0 |
| `sa` | −152 … −121 | 4 zero quadwords |
| `idbuf` | −120 … −74 | 36: `movabs` "INVOCATI", `movl` "ON_I", `movw` "D=", **32 byte stores of input-derived bytes at −106 … −75 (HR-2)**, `movb $0` |
| `argv_out[8]` | −72 … −9 | 8: seven literals and 0 |
| saved `%rbx` | −8 | 1 (`push`) |

* The `INVOCATION_ID` copy is reached only on the path where S-2 succeeded
  and S-3 … S-8 returned 0.

**Loads (HR-4).** `rp11_main` makes 60 loads, all through input-derived
pointers and none from its own frame:

* 11 in the argv check;
* 15 in the envp scan, at most 14 bytes per non-matching entry;
* 2 in the hex validation (`(%r8,%rax,1)` for 0 … 31, and `0x20(%r8)`); and
* the 32 copy loads `0x0 … 0x1f(%r8)`.

Total per matching entry: 47 bytes (§5.6). No load lies at or above
`rp11_main`'s entry slot.

The reviewer's independent HR-1 … HR-6 over the raw listing remains the
second layer (§5.14.4).

## 6. IC-1 and R-1 … R-5

**IC-1** traced R-2 under the pinned `strace`
(`-f -qq -v -y -s 65536 -e trace=%file,%process,fchdir`). The outputs were
identical to R-2's. The checker `verify/ic1check.py` canonicalises every path
through the manifest's own symbolic links.

* **Executed:** `env`, `sh`, `gcc-15`, `cc1`, `as` ×2, `ld.bfd`, `readelf`,
  `objdump` ×2. There were no failed `execve` calls.
* **Opened or looked up.**
  * Within the root: only manifest entries (loader cache, libraries, `cc1`),
    or paths the manifest binds as absent (four `specs` probes, the gcc
    library directories).
  * In the checkout: the five inputs and `build-out/`. The checkout's own
    directories were reached only by stat-family calls.
  * Two PCH probes (`launch.c.gch`, `select.h.gch`, both ENOENT); see D-3.
  * `/proc/self/exe`, listed under HA-1.
  * Nothing under `/tmp` or `/var/tmp`.
* **Environments.** `env` received `build_env` + `PWD`; `/bin/sh` exactly
  `build_env`; every later tool `build_env` + `PWD` + `OLDPWD`; `cc1` also
  `COLLECT_GCC`, `COLLECT_GCC_OPTIONS`, `OFFLOAD_TARGET_NAMES` and
  `OFFLOAD_TARGET_DEFAULT`.
* **Verdict:** pass under the named additions (D-2). A mutated manifest
  missing `libc.so.6` made it fail with 10 findings.

| Step | Status |
|---|---|
| R-1 | **done**: manifest regenerated inside root A before R-2 and before each R-4 run; inside root B; inside root C (provisioned from the committed lock alone, fresh download). All byte-equal to the committed manifest. `/etc/ld.so.preload` absent; `/tmp` and `/var/tmp` empty and read-only |
| R-2 | **done**: exit 0; outputs as §4 |
| R-3 | **done**: digests equal `expected.sha256`; listing equal to the committed listing |
| R-4 | **done**: (a) `/rp11/alt/checkout`; (b) a later run with every source mtime moved +400 days; (c) uid/gid 1001 `rp11alt`, host name `rp11-variant`. All five outputs identical, including `cc1.v` |
| R-5 | **not performed and not claimable by Claude.** The mechanism is `provision.py install` → `enter.py ldconfig` → `enter.py manifest` → `enter.py build`, or `RP11_LAUNCH_BUILD_ROOT=<root> pytest tests/test_rp11_launch_toolchain.py`. Root C (same host, same kernel, CPU and mechanism) shows the lock reproduces the root; **it varies none of HA-1 … HA-3 and is not R-5**. My values to vary against: kernel `6.8.0-139-generic`, AMD EPYC-Milan, bubblewrap 0.9.0 |

**HA-1 … HA-5 are recorded, not eliminated.** HA-1 is the kernel above and
`/proc/self/exe`. HA-2 is the CPU above (the loader's `glibc-hwcaps` choice).
HA-3 is bubblewrap, trusted between R-1 and R-2. HA-4 and HA-5 are varied by
R-4(b) and R-4(c).

## 7. Discrepancies, interpretations and their dispositions

None silently chosen. The ones that need your or Peter Duscha's acceptance are
marked **decide**.

| # | Item | What I did | Status |
|---|---|---|---|
| D-1 | §5.3.5 asks R-1 to run "in the same session that will run R-2" and R-2 to be "the first process in the build root". bwrap runs one command per entry | R-1's two `find` vectors and R-2 are three consecutive bwrap entries from one `enter.py` run, over the same read-only root bind. The interval is HA-3's stated trust | **decide** |
| D-2 | IC-1 condition 3 (every class-B environment = `build_env` + `shell_added_env`) cannot hold literally: bubblewrap always sets `PWD` for its first process (`--unsetenv` and `--clearenv` do not stop it); and the GCC driver passes four variables to `cc1` | Named and recorded as `entry_added_env` and `driver_added_env` in the lock, the contract and the manifest. Any other variable fails IC-1. `env -i` discards the entry `PWD`; the driver's variables are products of the pinned driver and its argv | **decide**: LD-8's "IC-1 passes" depends on accepting this |
| D-3 | `cc1` probes for `launch.c.gch` and `select.h.gch` in the checkout; their absence is an input outside the bound root | `build.sh` refuses (exit 3) if either exists; IC-1 records the probes by name; T-L3 checks the guard. This adds one check to `build.sh` beyond §5.2's text | review |
| D-4 | T-L4's "every `syscall` is preceded in its basic block by a load of `%eax` from the inventory" fails as text: four write sites load `%rax` by `mov %r9,%rax` | T-L4 checks for a write to `%eax`/`%rax` in the block; T-L10's constant propagation proves the inventory value at every site | review |
| D-5 | IC-1 "every executed path is an X-5 … X-11 executable", but `build.sh` (per §5.2) runs `objdump` and `readelf` (X-12, X-13) to write the listing | X-12 and X-13 are admitted to IC-1's executed set | review |
| D-6 | `test_the_covered_sources_are_exactly_the_package` asserted the covered set equals the package; §5.11 puts launcher files in `COVERED_SOURCES` | Enumerated `RP11_LAUNCH_COVERED` appended; the test now asserts package ∪ that tuple, disjoint and without duplicates. No glob, and a new package module still fails it | review |
| D-7 | R2 §9 puts the contract "beside `entry_environment.py`" in `execution/` | `rp11_launch.py` is in the stricter planning tier (pure data), declared in `test_no_execution` | review |
| D-8 | T-L2 needs `entry_environment` (I-6, unimplemented) | Peter Duscha's decision (§1); the half against `entry_environment` is owed by I-6 (T-B14) | decided |
| D-9 | X-15 says the tracer is "present only for IC-1" | `strace` is part of the bound root and listed in the manifest, so one manifest serves R-2 and IC-1; IC-1 shows R-2 does not execute it | review |
| D-10 | §5.3.2 excludes `/tmp` and `/var/tmp` | They are **listed** (empty, 1777), which is stricter: emptiness is bound by R-1 | note |
| D-11 | `coreutils` in 26.04 may resolve to Rust uutils | GNU coreutils 9.7 pinned via `coreutils-from-gnu`; recorded as a seed | note |
| D-12 | AMD APM revision | A 2013 r3.20 mirror copy, provenance recorded; the Intel 2026 edition is primary | note |
| D-13 | XD-5 lists classes (a) … (g) | XD adds a non-XD-5 structural refusal, `x-image-structure`, for a function set other than `_start`/`rp11_main`, a non-function symbol or non-`ET_EXEC` | note |
| D-14 | SETcc's ModR/M.reg | XD requires reg = 0 (`0F 9x /0`), stricter than the SDM's table text | note |
| D-15 | R-1's owner/group fields | The manifest is generated as namespace uid/gid 0; R-2 runs as 1000 (R-4(c): 1001). Ownership is the entry mechanism's mapping (HA-3); a root-owned real provisioning would show the same 0/0 | note |
| D-16 | `cc1.v` contains `GGC heuristics` computed from host memory | Compared across R-4 (identical) but, as §5.2 specifies, not in `expected.sha256`; may differ at R-5 without consequence | note |
| D-17 | Release pocket only | Updates and security pockets were not used; the root is offline build tooling | note |

## 8. Security implications and remaining trust

* **Nothing executes on any host from this change.** The image is not
  installed or wired. The harness manifest gains review data with
  `installed: false` and `wired: false`, `plan.is_executable` stays `False`,
  and no vector, mutation or authority changes.
* The launcher reads only `argc`, `argv[1..2]` and envp entries within §5.6's
  bounds. It writes only its own frame. It makes only the nine inventory
  calls, and its `execve` vector and environment are literals plus the 32
  validated bytes. Refusal output is fixed text, with no `errno`, path or
  value.
* **TD-1 … TD-4 remain trusted.**
  * TD-1: the manuals' encodings and the CPU's conformance to them (AD-14).
  * TD-2: no misreading common to XD and Codex's D9-2 decoding.
  * TD-3: XD's provenance independence from binutils. I wrote XD and its
    corpus from the manuals before the first build existed and did not read
    binutils source, tables or output, or the listing, while writing them.
    But **I am a language model whose prior knowledge may include binutils**.
    That cannot be shown here and is exactly what XD-9 and XD-11 exist for.
  * TD-4: the interpreters (CPython 3.12.3 here).
* D9-1's kernel citations (AD-3, AD-4, AD-6, AD-8, AD-11, AD-12) were not
  made.
* Class-P tools (`provision.py`, `enter.py`, host `gpgv`, `zstd`, bubblewrap)
  are not pinned; the root they produce is.

## 9. Commands and results

All on the repository host (Linux 6.8.0-139-generic). Every pytest run was
serial, `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p
no:cacheprovider` (CPython 3.12.3). Each run printed only pytest's two
`Unknown config option` warnings.

| # | Selection | Result |
|---|---|---|
| 1 | `tests/test_rp11_launch_source.py` | **275 passed, 0 skipped** |
| 2 | `tests/test_rp11_launch_toolchain.py`, `RP11_LAUNCH_BUILD_ROOT` = root A | **10 passed** |
| 3 | the same, root C (from the committed lock) | **10 passed** |
| 4 | the same, variable unset | **10 skipped**, each "RP11_LAUNCH_BUILD_ROOT is not set: no pinned rp11-launch build root is provisioned here …" |
| 5 | `test_no_execution`, `test_concrete_plan`, `test_r16_remediation` | **397 passed** |
| 6 | `tests/phase_5_0_evidence`, one process | **3370 passed, 0 failed, 0 skipped** (3364 before; +6 parametrized structural cases over the new module) |
| 7 | the same, `ulimit -Sn 1024` in a subshell | **3370 passed, 0 skipped** |
| 8 | `tests/test_*.py --continue-on-collection-errors` | **3053 passed, 347 skipped, 1 failed, 32 errors**. Skips: 326 database, 11 `google`, 10 rp11 toolchain. The failure and every error are `ModuleNotFoundError` for `discord` (32) or `google` (1), from `ext/commands/` and `connectors/sheets.py`, which this change does not touch. Seven modules could not be collected for the same reason |
| 9 | `python3 .claude/hooks/test_guards.py` | **41 cases (27 refused, 14 allowed): all passed** |
| 10 | `py_compile` over all 15 new or changed Python files; `dash -n build.sh` with the pinned `dash` | clean |
| 11 | harness dry run `-m tools.phase_5_0_evidence.execution.cli --manifest-out … --render …`, **never `--execute`**, four times: three to scratch, one to the checked-in paths | all exit 0; `DRY RUN — nothing was executed.`; 138 steps, 43 mutations, 47 cleanup steps, 4 unresolved (C-7, C-S4-3), `executable: False`, digest `87507cc7…e0d0`; **all outputs byte-identical** (`cmp`) |
| 12 | `xdecode.py`, `ctverify.py`, `elfcheck.py`, `tl11.py`, `ic1check.py`, `enter.py` R-1/R-2/R-4/IC-1 by hand | as §4 and §6 |
| 13 | `git diff --check`; `--no-index --check` on new files | see §11 |

**Manifest JSON diff** 26 → 27: `manifest_version`; the added `rp11_launch`
section; and `source_digests` changed or added for `review_manifest.py`,
`rp11_launch.py` and the nine launcher files. Nothing else.

**Not run, and why.**

* `oracle-test`, SSH and synchronization: prohibited.
* The DB-marked tests: no `TEST_DATABASE_URL`, because database access is
  prohibited. The 326 skips are unverified assertions, not PostgreSQL
  evidence.
* `tests/web`: 8 collection errors (`bs4` missing from this interpreter), so
  it was not exercised. It is untouched by this change.
* The Foundry `node --test` suite: untouched, not run.
* R-5, XD-9, XD-11, D9-1 … D9-4 and D9-5: not mine to perform, or not
  authorized.
* No formatter, linter or type checker is configured in the repository
  (no `pyproject`/`setup.cfg`/`mypy`/`ruff` config; neither tool is in
  `venv-web`).

## 10. Rollback and recovery

* Repository only. Delete `infra/rp11-launch/`,
  `tools/phase_5_0_evidence/rp11_launch.py` and the three new test files.
  Revert `review_manifest.py` and the three edited evidence tests. Then
  regenerate the manifest JSON and concrete plan through the dry-run CLI,
  which reproduces the version-26 bytes `add5524b…` and `c3591e65…`.
* Nothing to undo on any host: no package was installed, no configuration was
  changed, and nothing was installed or wired. The build roots and downloads
  live only in the session scratchpad.
* A future toolchain or source change follows §5.13: rebuild through R-1 …
  R-4, rerun XD, T-L11, T-L12 and T-L10, review the listing diff, update
  `expected.sha256` and the contract constants, and bump the manifest. The
  expected digest is **never** updated to match an unexplained output.

## 11. Current-state pointers and `git diff --check`

Updated to record this return: `docs/review/Handover information`,
`docs/project-management/status.md`, `docs/implementation-plan.md` §20, and
the first restriction banner of `docs/operations/disposable-test-server.md`.

The change-log's I-7 row is an append-only approval record and is left for
the acceptance step. No prior assignment, handback, review, decision,
snapshot or archive was edited.

`git diff --check` over the tracked changes: clean. Over the new files
(`git diff --no-index --check /dev/null <file>`): clean except
`rp11-launch.x86_64.listing`, whose 5 trailing-whitespace lines are `readelf`
and `objdump` output. They must stay: T-L9 and R-3 require the committed
listing to be byte-equal to the regenerated one.

## 12. Focused questions for Codex

1. **XD-9.**
   * Please check each of the 116 table rows (`xdecode.py` `_rows()`) and the
     ModR/M, SIB, REX and RIP-relative logic (`decode_one`,
     `_decode_memory`, `_row_width`) against the SDM sections cited per row.
   * Please review the T-L12 corpus, and the spelling table's `form` entry
     and injectivity check.
   * Are the strictness choices D-13 and D-14 acceptable?
2. **XD-11 (LD-9 (i)).**
   * Please decode the actual `.text` (1 295 bytes, `0x4000b0`) with your own
     decoder or by hand, without reading XD's table, and compare instruction
     starts, lengths, mnemonics, operands and targets with XD's agreed stream
     (`e1354c29…`) and the listing.
   * The `.text` bytes are the listing's byte fields (T-L7 ties them to the
     image). The image is reproducible from the lock with `provision.py` and
     `enter.py`.
3. **T-L11 → T-L10 binding.**
   * Does `tl11.py` gate T-L10 as XD-7 requires: same image and listing
     digests, image = expected, three-way facts, and identical T-L10 over
     both streams?
   * Is T-L10's zero-flag edge refinement — `%rdx` = 0 on the not-taken edge
     of `and $1,%edx; jne`, which proves `rt_sigaction`'s NULL old action —
     sound?
   * Is joining "input-derived" with NULL to "input-derived" sound?
4. **Zero-`ret` completeness.** Is there any reachable transfer or
   fault/signal path that CT-1 … CT-9 and RI-1 … RI-7 as implemented do not
   cover? Note that `rp11_main` saves `%rbx` with a `push` it never pops,
   which is harmless because nothing returns.
5. **LD-8 and R-5.**
   * Do you accept D-2's named environment additions as satisfying "IC-1
     passes"?
   * Do you accept D-1's reading of "same session"?
   * Who performs R-5, and which of HA-1 (kernel ≠ `6.8.0-139-generic`),
     HA-2 (CPU ≠ AMD EPYC-Milan) and HA-3 (a mechanism other than
     bubblewrap 0.9.0) will it vary?
6. D-3 … D-7 and D-9: accept or direct changes.

Codex reviews the exact returned bytes. Peter Duscha alone accepts the
implementation or authorizes R-5, H-1, H-2 or any later host or operational
work.
