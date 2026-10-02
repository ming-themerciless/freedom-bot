# Claude handback — I-7-R1 IC-1 exact-environment remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-I7-R1`

Date: 2026-10-01

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md)

Controlling finding: `I7-R1-1` in
[`project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md`](project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md).

State: **returned for independent Codex re-review. Claude has stopped.**
Nothing is committed, pushed, installed or wired. **PO-9 and PO-14 remain open;
RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; Package 5.0 remains not ready.** R-5 is not performed or claimed.
D-2 is not claimed accepted: under the maintainer decision it can be accepted
only after Codex accepts this remediation.

## 1. Summary

IC-1 now proves the **exact** environment of every class-B and class-E
process in the traced build. It no longer only permits a set of extra names.

* The successful `execve` calls must be exactly the ten that `build_argv` and
  `build.sh` define, in order. Each must receive **exactly** its class's
  complete name/value mapping, with `{co}` set to the run's controlled
  checkout. Missing variables, extra variables, changed values, duplicated
  names, malformed entries and malformed or abbreviated `execve` records each
  fail.
* The four driver-added values are **specified, not observed**:
  * derived from `build.sh`'s driver vector and the pinned driver's
    configuration;
  * pinned in the checker, the contract module and the lock; and
  * re-derived by a test from `build.sh`.
* All three are cross-checked by tests.
* A fresh root was provisioned from the committed lock alone, with a fresh
  download.
  * R-1 is byte-equal.
  * R-2 reproduced all five outputs.
  * IC-1 passes at R-2's checkout `/rp11/co` and at R-4(a)'s
    `/rp11/alt/checkout`, with outputs byte-identical to R-2.
* **Every frozen digest of prompt §2 is unchanged**, and so are all other
  launcher inputs (§6).
* Review manifest **27 → 28**: the lock and the serialized `rp11_launch`
  section gain the exact contract. The digest is `02d660c3…5abb`.

One derivation step needed correction during the work. It is reported in full
as R1-D-1 (§8): my first derivation of `COLLECT_GCC_OPTIONS` omitted GCC's
`prune_options` rule.

## 2. The exact environment contract

`build_env` = `LC_ALL=C`, `PATH=/usr/bin`, `SOURCE_DATE_EPOCH=0`, `TZ=UTC0`.
`{co}` is the run's checkout mount point. It must be one of the controlled
checkouts `/rp11/co` (R-2, R-4(b), R-4(c)) or `/rp11/alt/checkout` (R-4(a)).
Any other checkout fails IC-1.

| # | Successful `execve` | Class | Exact environment (complete; order ignored) |
|---|---|---|---|
| 1 | `/usr/bin/env` | entry | `build_env` + `PWD={co}` |
| 2 | `/bin/sh` | shell | `build_env` only |
| 3 | `/usr/bin/gcc-15` | source | `build_env` + `OLDPWD={co}` + `PWD={co}/infra/rp11-launch` |
| 4 | `/usr/libexec/gcc/x86_64-linux-gnu/15/cc1` | compiler | source + the four driver variables below |
| 5 | `/usr/bin/as` (`start.s`) | source | as #3 |
| 6 | `/usr/bin/as` (`launch.s`) | output | `build_env` + `OLDPWD={co}/infra/rp11-launch` + `PWD={co}/build-out` |
| 7 | `/usr/bin/ld.bfd` | output | as #6 |
| 8 | `/usr/bin/readelf` | output | as #6 |
| 9 | `/usr/bin/objdump` (`-d`) | output | as #6 |
| 10 | `/usr/bin/objdump` (`-s -j .rodata`) | output | as #6 |

Where each value comes from:

* **Entry `PWD`.** bubblewrap's `--chdir` sets it for the first process. This
  is HA-3's entry mechanism, as D-2 named.
* **Shell's `PWD` and `OLDPWD`.** The pinned dash exports both on `cd`. Their
  values are the two directories `build.sh` changes into (`cd
  infra/rp11-launch`, then `cd ../../build-out`), each resolved against `{co}`.
* **The driver's four variables for `cc1`:**

| Variable | Exact value | Derivation (pinned inputs only) |
|---|---|---|
| `COLLECT_GCC` | `/usr/bin/gcc-15` | the driver's `argv[0]` in `build.sh` |
| `COLLECT_GCC_OPTIONS` | `'-S' '-v' '-std=c11' '-ffreestanding' '-nostdinc' '-fno-builtin' '-fno-pie' '-fno-stack-protector' … '-Os' '-g0' '-U' '_FORTIFY_SOURCE' '-Wall' '-Wextra' '-Wvla' '-Werror' '-o' '../../build-out/launch.s' '-dumpdir' '../../build-out/'` (full text in `ic1check.COLLECT_GCC_OPTIONS`, `rp11_launch.DRIVER_ADDED_ENV_VALUES` and the lock's `ic1_env_compiler`) | GCC 15 `set_collect_gcc_options` over `build.sh`'s driver vector, in this order: (1) `prune_options` drops a switch that a later switch cancels through the `Negative()` cycle `fpic → fPIC → fpie → fPIE → fpic`, so `-fno-pie` removes the earlier `-fno-pic`; (2) each remaining switch is single-quoted; (3) `-U` and `-o` take their separate canonical form; (4) `-dumpdir` is appended last, set to the `-o` directory, as for one compile-only input. The pinned driver's `*self_spec` is empty, and its configured defaults add no switch to a vector that names `-march` and `-mtune` and not `-m32` |
| `OFFLOAD_TARGET_NAMES` | `nvptx-none:amdgcn-amdhsa` | the pinned driver's configuration string `--enable-offload-targets=nvptx-none=…,amdgcn-amdhsa=…`: names kept, joined by `:` (`handle_foffload_option`) |
| `OFFLOAD_TARGET_DEFAULT` | `1` | the pinned driver's `--enable-offload-defaulted` |

Each `PWD` must also equal the process's traced working directory. This
secondary consistency check was kept from I-7.

## 3. Files and serialized contracts changed

Only these files changed. Every other file of I-7's returned set is byte-equal
to its I-7 handback digest (§6).

| File | I-7 SHA-256 | Now | Change |
|---|---|---|---|
| `infra/rp11-launch/verify/ic1check.py` | `2e35bed7…a89769` | `ea7d9dd3d8e141349019cfdeba5e91df7569e28d6818136777f59bf313316917` (421 lines) | exact contract constants; `expected_environment`; strict strace string/array/`execve` parser (`parse_execve`); exact mapping comparison; ordered `execve` sequence; controlled-checkout check; output gains `checkout`, `exec_sequence` and per-record `class` |
| `infra/rp11-launch/toolchain.lock` | `ea4c5872…72411d` | `f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf` (107 lines) | 11 lines appended after `driver_added_env`: a 4-line comment, `ic1_controlled_checkouts`, `ic1_exec_sequence` and `ic1_env_{entry,shell,source,compiler,output}`. Existing lines unchanged; `build_root_manifest_sha256` unchanged |
| `tools/phase_5_0_evidence/rp11_launch.py` | `37d3e8db…2d8` | `9cf5668c87bc1aace1eacdafa3c1a5759ea4cec747fb9dcfaa0d529d77ac3c57` (302 lines) | `IC1_CONTROLLED_CHECKOUTS`, `IC1_CHECKOUT_TOKEN`, `DRIVER_ADDED_ENV_VALUES`, `IC1_ENV_CLASSES`, `IC1_EXEC_SEQUENCE`, `ic1_environment()`; `TOOLCHAIN_LOCK_SHA256` → `f9238073…`; `manifest_section()["build"]["ic1_environment"]`; the "only the names are contract" comment replaced |
| `tools/phase_5_0_evidence/review_manifest.py` | `aa32e57c…11a4` | `4aa68e7e73249a5c17e28c1af48ed0b20d1b72ac2d4d36cd1d58df55302bb510` | `MANIFEST_VERSION` 27 → 28, with its history entry. Nothing else |
| `tests/rp11_launch_support.py` | `5985491e…c9bcc9a` | `bc24c0ee7b0c9f58853479adc908c60cf013b9652409e3d5cee0d710074a18b6` (201 lines) | `build_driver_vector()` and `collect_gcc_options()`: the test-side derivation from `build.sh` |
| `tests/test_rp11_launch_source.py` | `8767ff31…26d9` | `77e05fc6c3c3b95da7391971ca61ab7e0a683c1e33eba85e3290b52614c63ba6` (940 lines) | IC-1 section replaced: realistic trace generator for both checkouts and 368 IC-1 tests (§4); T-L3 required lock fields extended |
| `tests/test_rp11_launch_toolchain.py` | `a54795bb…e480` | `ff3d458cabae91512562cca6143542337b1306dc3df791da505c51a9519ab76f` (254 lines) | IC-1 parametrized over `r2` and `r4a-path` with an exact per-record comparison; new driver-configuration test; `_in_root` gains a `chdir` parameter; IC-1 trace directory per variant |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | `4f3bdf25…2830` | `304acf5ef4c75fa7d23ea8a817ba6eeaf787c584a24b25842761e9402b3fe168` | version pin 27 → 28, with its history comment |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | `8b2c4481…a464` | `74a7424518673d3aa8fbaa82cdb7ee1d3952e93ef22df605ff538da4d58f8518` | regenerated (dry run) |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | `eca1da83…263a` | `1f843cbd2656527134003b516f57135948a1ca13071e79fdede7d6354b556a40` | regenerated (dry run); only its digest line changes |

**Review manifest 27 → 28.** The serialized contract changed, so the existing
versioning rule applies. The structural JSON diff against regenerated v27 is
exactly:

* `manifest_version` 27 → 28;
* **added** `rp11_launch.build.ic1_environment`, which holds:
  * `controlled_checkouts`;
  * `checkout_token`;
  * `classes`: the five complete environments;
  * `exec_sequence`; and
  * `comparison: "exact"`;
* `rp11_launch.expected_sha256.toolchain_lock` `ea4c5872…` → `f9238073…`; and
* `source_digests` for exactly three paths: `toolchain.lock`, `rp11_launch.py`
  and `review_manifest.py`.

Nothing else changed:

* the covered set (62 paths);
* every vector, step and mutation;
* `executable: False`; and
* the unresolved entries C-7 and C-S4-3.

The digest moves `87507cc7…e0d0` → `02d660c3bb8cd030a36ae1ece70da0de1756ca3052f3de74c89a15279a5c5abb`.

The old name-only fields (`shell_added_env`, `entry_added_env`,
`driver_added_env`) are kept in the lock, the contract and the section. A test
asserts that they are exactly the names each class adds to `build_env`.

Current-state pointers: §11.

## 4. Finding-to-test trace (prompt §4.5)

All tests are in `tests/test_rp11_launch_source.py` unless stated. Counts are
collected test IDs. "Both paths" means R-2 `/rp11/co` and R-4(a)
`/rp11/alt/checkout`.

| §4.5 item | Tests | Count |
|---|---|---|
| each required addition missing individually | `test_ic1_refuses_each_required_variable_missing`: every variable of every one of the ten `execve` environments, both paths. It covers every `build_env` variable, the entry `PWD`, the shell's `PWD`/`OLDPWD` in all eight children, and the four driver variables. Needle: `<path>: required environment variable <NAME> is missing` | 122 |
| each required addition with a changed value | `test_ic1_refuses_each_required_variable_changed`: the same 122 positions, value + `x`. Needle: `<path>: <NAME> is '<got>', not '<want>'` | 122 |
| an extra variable | `test_ic1_refuses_an_extra_variable` (`LD_PRELOAD` in each of the ten processes, both paths); `test_ic1_refuses_driver_variables_outside_cc1` (`COLLECT_GCC` in each of the nine non-`cc1` processes) | 20 + 9 |
| duplicate variables | `test_ic1_refuses_a_duplicated_variable`: same and different second value, entry/`cc1`/last `objdump`, both paths | 12 |
| malformed variables | `test_ic1_refuses_a_malformed_variable`: `NOEQUALS`, `=value`, `1BAD=x`, empty, `A B=c` in four processes | 20 |
| malformed records | `test_ic1_refuses_a_malformed_or_abbreviated_execve_record`: truncated string `"…"...`, `...` element, `/* 6 vars */`, missing separator, unknown escape, unterminated array, non-array; `test_ic1_decodes_strace_escapes_before_comparing` (octal/hex/quote/backslash decoding; an escaped spelling of a required value still passes) | 7 + 1 |
| incorrect `PWD`/`OLDPWD` under both the R-2 path and R-4(a) path | `test_ic1_refuses_wrong_pwd_and_oldpwd_at_each_checkout` (seven processes × both paths: the other run's directories, and `PWD`/`OLDPWD` exchanged); `test_ic1_a_run_is_checked_against_its_own_checkout` (a conforming trace checked against the other checkout fails on `PWD` and `OLDPWD`); plus the 2 × 2 × 9 `PWD`/`OLDPWD` positions inside the 244 above | 14 + 2 |
| each of the four driver-added variables missing individually | `test_ic1_refuses_each_driver_variable_missing`, both paths | 8 |
| each of the four driver-added variables changed individually | `test_ic1_refuses_each_driver_variable_changed`, both paths. Realistic wrong values: `gcc-15`, `/usr/bin/x86_64-linux-gnu-gcc-15`, options + `'-O2'`, options with `'-fno-pic'` restored, empty options, `nvptx-none`, reversed targets, `0`, empty | 18 |

Supporting tests:

* `test_ic1_checker_passes_a_conforming_trace` (both paths: exact sequence,
  classes, `/proc` paths and PCH probe);
* `test_ic1_the_exact_environments_are_these`: all five classes written out by
  hand for both paths and compared with the contract module and with the
  checker;
* `test_ic1_the_driver_values_are_derived_from_build_sh_not_observed`;
* `test_ic1_refuses_a_different_execve_sequence` (an extra, a missing and a
  reordered `execve`);
* `test_ic1_refuses_an_uncontrolled_checkout`;
* `test_ic1_the_checker_contract_and_lock_agree`, which covers the lock, the
  contract, the checker, `enter.VARIANTS`, the serialized section and the
  executable set;
* the retained non-environment refusals (5) and the every-tool test; and
* T-L3's extended required-field list.

IC-1 total: **368**.

Toolchain file (pinned root):

* `test_ic1_the_traced_build_opens_nothing_outside_the_bound_root[r2]` and
  `[r4a-path]`: a real trace; outputs equal to R-2; verdict pass; every record
  equal to its class's exact environment.
* `test_ic1_the_driver_values_follow_from_the_pinned_driver`:
  * reads the pinned driver's bytes and checks their digest against the lock;
  * derives the offload pair from its configuration string; and
  * runs `gcc-15 -dumpspecs` in the root to show `*self_spec` is empty.

**The tests demonstrate the finding.** The same mutations were run against the
**I-7** checker (`2e35bed7…`, kept in scratch) through the new trace generator:

* it passed both conforming traces;
* it **passed 42 of the 122 missing-variable mutations and 24 of the 122
  changed-value mutations**; and
* in particular, it passed every one of the four driver variables missing, and
  every one set to an arbitrary value.

The new checker refuses all 244. Only the extra-variable mutations (20/20) were
already refused by I-7. That matches Codex's description of the finding.

## 5. Fresh R-1, R-2 and IC-1 evidence

All runs were on the repository host (Linux `6.8.0-139-generic`, AMD
EPYC-Milan, bubblewrap 0.9.0), in this session's scratchpad.

**Provisioning (fresh).**

* `provision.py install`: an empty root, a new package cache, and **62
  packages downloaded from the snapshot**, each verified against the lock.
* Then `enter.py ldconfig`.
* No earlier root or cache was used.

| Step | Result |
|---|---|
| R-1 (once after provisioning, again before the recorded run) | regenerated inside the root; **byte-equal** to `build-root.manifest`, SHA-256 `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` |
| R-2 `enter.py build` | exit 0; all five outputs in the table below |
| IC-1 `enter.py ic1 --variant r2`, checked at `/rp11/co` | exit 0; outputs **byte-identical** to R-2's (`cmp`, five files); checker verdict **pass**, no failure. Trace `81c34340ba9309477d910ce952919369f2422cc4d84ce535c091814e33d22108`, checker JSON `ee35ec2571f487e0d15310622b46048db30cbdc673c2f37c7c0b607b29d9cddb` |
| IC-1 `enter.py ic1 --variant r4a-path`, checked at `/rp11/alt/checkout` | exit 0; outputs **byte-identical** to R-2's; verdict **pass**. Trace `b30a537b1f9b4bf6481adc59142ad48fe178d1a52a113766d17db93e84379535`, checker JSON `600d8846038630db7284e4ad10dd24915466d654ec8a725d703b0f291438462a` |
| R-4 (a) path, (b) time, (c) user/host | T-L6 against the fresh root: all five outputs identical to R-2 |

| Output | R-2 and both IC-1 runs |
|---|---|
| `rp11-launch` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` |
| `rp11-launch.map` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` |
| `rp11-launch.x86_64.listing` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` (= committed listing, `cmp`) |
| `launch.s` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` |
| `cc1.v` | `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` (= I-7's) |

IC-1 also found:

* the executed sequence exactly as in §2's table;
* `/proc/self/exe` as the only kernel path;
* the two PCH probes as in I-7; and
* nothing created under `/tmp` or `/var/tmp`.

The traces are not committed. They are reproducible with the commands in §7.

**T-L11 and its T-L10 gate** (`verify/tl11.py` on the fresh R-2 image and the
committed listing):

* `tl11_verdict pass`, `tl10_verdict pass`, `tl10_evidence true`, 332
  instructions;
* `image_is_expected true`;
* T-L10 tables `25779797d8a69b0ae6094292367413379e510a37cfa841ac10949d12f790e341`
  (= Codex's figure); and
* interpreter CPython 3.12.3.

## 6. The frozen digests are unchanged

| Prompt §2 item | Required | Fresh value | Source of the fresh value |
|---|---|---|---|
| image | `04218ed2…8572` | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | R-2 and both IC-1 builds; T-L5; T-L11 `image_sha256` |
| listing | `8c1fedee…d188` | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` | committed file, R-2 output, T-L9, T-L11 |
| `launch.s` | `b37280d5…7706` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` | R-2 and IC-1 outputs |
| map | `5a8b0580…c34d` | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` | R-2 and IC-1 outputs |
| XD source | `84598d06…7c97` | `84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97` | committed file; T-L11 `xdecode_py_sha256` |
| XD spelling table | `d2040648…7b66` | `d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66` | committed file; T-L11 |
| agreed stream | `e1354c29…f8e0` | `e1354c29e4abddd115fad9b1f83fd69b3b93aae2971db6a448964baa8edbf8e0` | T-L11 `agreed_stream_sha256` |

Also unchanged against the I-7 handback's table:

* `start.s`, `launch.c`, `select.h`, `rp11-launch.ld` and `build.sh`;
* `build-root.manifest` and `expected.sha256`;
* `xdecode-corpus.txt`, `ctverify.py`, `elfcheck.py` and `tl11.py`; and
* `enter.py`, `provision.py` and both T-L8 harness files.

No build input changed. The lock is not a `build.sh` input. Its new bytes
changed nothing in the root (R-1 equal) or the build (outputs equal), and
IC-1 has been rerun after the lock change, as §5.3.7 requires.

## 7. Commands and results

All runs were serial on the repository host. Pytest ran as `env -u
TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p
no:cacheprovider` (CPython 3.12.3). Every run printed only pytest's two
pre-existing `Unknown config option` asyncio warnings. `<root>` is the fresh
root in the session scratchpad.

| # | Command / selection | Result |
|---|---|---|
| 1 | baseline before editing: `tests/test_rp11_launch_source.py` | 275 passed |
| 2 | `python3 infra/rp11-launch/buildroot/provision.py install --root <root> --cache <new cache>`; `enter.py ldconfig`; `enter.py manifest --out …`; `cmp` | exit 0; 62 packages; **R-1 equal** |
| 3 | focused: `tests/test_rp11_launch_source.py -k ic1` | **368 passed** |
| 4 | `tests/test_rp11_launch_source.py` | **634 passed, 0 skipped** (275 − 9 replaced IC-1 tests + 368) |
| 5 | `RP11_LAUNCH_BUILD_ROOT=<root> … tests/test_rp11_launch_toolchain.py -v` | **12 passed, 0 skipped**: R-1, T-L5, T-L6 ×3, T-L7, T-L9, T-L11, IC-1 `[r2]`, IC-1 `[r4a-path]`, driver configuration, T-L8 |
| 6 | the same, `RP11_LAUNCH_BUILD_ROOT` unset | 12 skipped, each with the explicit "not set" reason. A skip is not a pass |
| 7 | `tests/phase_5_0_evidence` (one process) | **3370 passed, 0 failed, 0 skipped** |
| 8 | `RP11_LAUNCH_BUILD_ROOT=<root> … --continue-on-collection-errors tests/test_*.py` | 3424 passed, 337 skipped, 1 failed, 32 errors (detail below) |
| 9 | `python3 .claude/hooks/test_guards.py` | 41 cases (27 refused, 14 allowed): all passed |
| 10 | `py_compile` of the 7 changed Python files (cfiles in scratch) | clean |
| 11 | `git diff --check` (tracked); `git diff --no-index --check /dev/null <f>` for the six changed untracked files | no output: clean |
| 12 | dry-run CLI: `-m tools.phase_5_0_evidence.execution.cli --manifest-out <x> --render <y>`, **never `--execute`**. Twice to scratch, then once to the checked-in paths | all exit 0; `DRY RUN — nothing was executed.`; 138 steps, 43 mutations, 47 cleanup steps, 4 unresolved (C-7, C-S4-3), `executable: False`; digest `02d660c3…5abb`; **all three outputs byte-identical** (`cmp`) |
| 13 | v27 reproduction: the three covered files temporarily restored to their I-7 bytes in place (`review_manifest.py` by deleting only the 28 entry, which reproduced `aa32e57c…` exactly); dry run to scratch; v28 files restored and re-verified by digest | v27 JSON `8b2c4481…`, plan `eca1da83…`, digest `87507cc7…` reproduced exactly. Structural diff as in §3 |
| 14 | the I-7 checker over the new mutations (§4) | passed 42/122 missing and 24/122 changed |
| 15 | `enter.py build`; `enter.py ic1 --variant r2` and `--variant r4a-path`; `verify/ic1check.py --trace … --manifest … --checkout …`; `verify/tl11.py --image … --listing … --tables-out …`; `cmp` of all outputs | as §5 and §6 |

**Row 8 detail.** The run has the same profile as I-7's, with the counts
moving only by this change: +359 source tests, and the 12 toolchain tests now
run instead of skipping.

* **Skips (337):** 263 database-marked tests (no `TEST_DATABASE_URL`) and 11
  for the missing `google` module. These are unverified, not PostgreSQL
  evidence.
* **The failure and all 32 errors** are `ModuleNotFoundError` for `discord`
  (32) or `google` (1), from `ext/commands/` and `connectors/sheets.py`, which
  this change does not touch.
* **Seven modules** could not be collected for the same reason.

**Not run, and why.**

* `oracle-test`, SSH and synchronization: prohibited. The documented
  test-server suite, `tests/web` and the Foundry `node --test` suite were
  therefore not run. All are untouched by this change.
* Database-marked tests: database access is prohibited.
* No formatter, linter or type checker is configured in the repository.
* R-5, H-1/H-2 and any operational step: not authorized and not performed.
* A bulk copy of the working tree into scratch, for the v27 reproduction, was
  **refused by the secrets guard**. The command matched a `.env` pattern, even
  though that pattern was there to exclude the file. I did not route around
  the guard and copied no tree. Row 13's in-place swap of my own three covered
  files replaced it.

## 8. Discrepancies and interpretations

None was silently chosen.

| # | Item | What I did | Status |
|---|---|---|---|
| R1-D-1 | **My first `COLLECT_GCC_OPTIONS` derivation was incomplete.** Before any I-7-R1 trace existed, I wrote the derived values to scratch (`derived-expectations.txt`, SHA-256 `bd2131bc…3f51`, 08:40 UTC). It kept `'-fno-pic'`. The first fresh IC-1 under the new checker failed on exactly that one value; every other value of all ten environments matched | Identified the missing rule: GCC's driver `prune_options` drops a switch a later one cancels through the `Negative()` chain `fpic → fPIC → fpie → fPIE → fpic`, so `-fno-pie` cancels `-fno-pic`. I implemented the rule in the test-side derivation over `build.sh`, not as a special case, and corrected the pinned literal. It is corroborated by the driver's own `-v` report in `cc1.v`, whose digest `b77f92dc…` was recorded in the I-7 handback before this work. The correction was **prompted by** the trace, but its value is **derived from** the cited rule over pinned inputs. Codex should judge whether that satisfies "not learned from the trace" | **review** |
| R1-D-2 | Exact per-process expectations need each `execve`'s identity, and `as` runs in both directories | IC-1 now requires the exact ordered sequence of ten `execve` calls. This is stricter than I-7's "each tool at least once" | review |
| R1-D-3 | `PWD` is still also compared with the traced working directory. That comparison holds only because strace completes the child's `execve` after the parent's `vfork` returns | Kept as a secondary check. The primary check is now the specified value, which does not depend on the interleaving | note |
| R1-D-4 | The `COLLECT_GCC_OPTIONS` derivation function models only what this vector needs: quoting, `-U`/`-o` separate canonical forms, the PIC/PIE `Negative()` cycle and the compile-only `-dumpdir` | It is not a general GCC model. A `build.sh` change would need its rules re-checked. `build.sh` is frozen here | note |
| R1-D-5 | The lock gained IC-1 lines, so its digest and `TOOLCHAIN_LOCK_SHA256` move | Not a build input. R-1 and the build were unchanged, and IC-1 was rerun after the change | note |
| R1-D-6 | `-dumpspecs` runs the pinned driver once in the root, in the new toolchain test | It reads compiled-in specs and writes nothing. It is evidence for the derivation, not a build step | note |
| R1-D-7 | IC-1 at R-4(a) is not required by §5.3.7, which names one R-2 run | Added under prompt §4.4, so that the R-4(a) path is exercised on a real trace as well as synthetically | note |
| R1-D-8 | Trace inspection | No I-7 trace was opened. After the derivation was recorded, the fresh trace's `execve`/`vfork`/`chdir` lines were read for syntax (the `<unfinished ...>` structure), and the checker output was read for R1-D-1 | note |

## 9. Security implications and remaining trust

* **The comparison only got stricter.**
  * No variable was removed from any traced process.
  * No value is wildcarded.
  * Nothing in the trace becomes an expectation.
  * An uncontrolled checkout fails.
  * A malformed, truncated or abbreviated record fails rather than being
    parsed leniently.
* **No behaviour reaches any host.**
  * Nothing executes on any host from this change.
  * The section still records `installed: false` and `wired: false`.
  * `plan.is_executable` stays `False`.
  * No vector, mutation or authority changes.
* **HA-1 … HA-5 are recorded, not eliminated, as in I-7.**
  * HA-1: kernel `6.8.0-139-generic` and `/proc/self/exe`.
  * HA-2: AMD EPYC-Milan.
  * HA-3: bubblewrap 0.9.0. It also supplies the entry `PWD` now required
    exactly, and the interval between R-1 and R-2 stays trusted (D-1).
  * HA-4 and HA-5: varied by R-4(b) and R-4(c).
  * This remediation varies none of HA-1 … HA-3 and **is not R-5**.
* **TD-1 … TD-4 are unchanged.**
  * TD-1 and TD-2: unchanged; XD was not touched.
  * TD-3: unchanged; I am still a model whose prior knowledge may include
    binutils.
  * TD-4: unchanged; the interpreter is CPython 3.12.3.
* **Added trust:** my reading of GCC 15's driver behavior for the four values.
  It is cross-checked two ways: by the traced values, and by the driver's own
  `-v` report in R-2's untraced `cc1.v`.

## 10. Rollback and recovery

* **Repository only.**
  * Restore the eight changed source and test files to their I-7 bytes (§3
    table).
  * For `review_manifest.py`, delete the version-28 history entry and set
    `MANIFEST_VERSION = 27`. This reproduces `aa32e57c…` exactly.
  * Regenerate both artifacts through the dry-run CLI. This was exercised in
    §7 row 13 and reproduces `8b2c4481…` / `eca1da83…` / digest `87507cc7…`.
* **Nothing to undo on any host.**
  * No package was installed and no configuration changed.
  * Nothing was installed, wired, committed or pushed.
  * The fresh root, package cache, traces and evidence live only in the
    session scratchpad.
* **A future change to the lock, manifest, `build.sh` or toolchain:**
  * re-derive the driver values (R1-D-4);
  * rerun IC-1 at both checkouts; and
  * never set an expected value from an unexplained trace.

## 11. Current-state pointers

The following were updated to record this return:

* `docs/review/Handover information`;
* `docs/project-management/status.md`;
* `docs/implementation-plan.md` §20; and
* the restriction banner of `docs/operations/disposable-test-server.md`.

No prior assignment, handback, review, decision, snapshot or archive was
edited. The change-log is left for the acceptance step.

## 12. Focused questions for Codex

1. **Derivation independence (R1-D-1).**
   * Is deriving `COLLECT_GCC_OPTIONS` from `build.sh` plus GCC's
     `set_collect_gcc_options`/`prune_options`/`-dumpdir` rules acceptable as
     "deterministically derived from pinned inputs"?
   * Is the correction acceptable, given that the trace prompted it, it is
     corroborated by `cc1.v`, and it is implemented as a general rule?
   * If you prefer, you can re-derive the value from the GCC 15 sources (the
     relevant code is `gcc/gcc.cc` and `gcc/opts-common.cc` `prune_options`/
     `cancel_option`). The pinned driver's `-v` output in `cc1.v` gives a
     second channel.
2. **Exactness.**
   * Does `ic1check._check_env` plus `parse_execve` now establish equality of
     complete mappings?
   * Is any accepted spelling still lenient? Order is deliberately ignored;
     strace escapes are decoded first.
   * Is refusing truncated strings, abbreviated arrays and `/* N vars */`
     correct and sufficient?
3. **Sequence (R1-D-2).** Is requiring the exact ordered ten-`execve`
   sequence acceptable?
4. **Checkout binding.** Is the controlled-checkout restriction, with
   `{co}`-relative `PWD`/`OLDPWD` exercised for R-2 and R-4(a) on real
   traces, what prompt §4.4 intended?
5. **D-2.** With this remediation, can the named additions be accepted as the
   bounded clarification the maintainer decision describes?

Codex re-reviews the exact returned bytes. Peter Duscha alone accepts the
remediation or authorizes R-5, H-1, H-2 or any later host or operational work.
