# Handback — R4 `cc1.v` determinism audit and remediation (`FRESH-R4-HS-1`)

Work ID: `C-P5.0-R5-RP11-FRESH-R5-R4-D1`
Assignee: Claude
Date: 2026-10-04
Prompt: [`phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md)
Authority: [R4 HARD STOP acceptance and remediation authority](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md)

Status: **returned for Codex independent review. Not accepted.** Claude does
not close `FRESH-R4-HS-1`, accept R-5 or approve a successor run.

---

## 1. Outcome

`build.sh` now passes `--param=ggc-min-expand=100 --param=ggc-min-heapsize=131072`
to the compiler driver, once each, and no other `--param`. These were the only
host-resource-selected bytes in `cc1.v`. With them fixed:

* the four normative outputs and the committed listing are **byte-identical**
  to `expected.sha256` and the committed listing (§5);
* the diagnostic fixture was re-derived with already-available, R-1-verified
  local roots: 5,305 bytes, SHA-256
  `e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a`. It
  differs from the B1 fixture (5,120 bytes, `b77f92dc…905b`) by exactly three
  insertions of the two arguments, and a test proves that removing them gives
  back the B1 bytes exactly;
* that `cc1.v` is identical across 2 roots × 4 variants (R-2, R-4(a)/(b)/(c))
  and under lowered `RLIMIT_AS`/`RLIMIT_RSS`. With the same limits and without
  the arguments, the `GGC heuristics:` line moves and nothing else does. That
  reproduces the R4 defect locally;
* `cc1check.py` is **unchanged**: byte equality is still the only PASS. There
  is no regex, ignored range, normalization, alternate hash, caller exception
  or causal label;
* IC-1 now also requires each fixed argument **exactly once**, as its canonical
  token, in the traced driver and `cc1` argument vectors. No other token may
  name either parameter, and no `@file` response file is allowed. The
  compiler-environment contract carries both arguments in
  `COLLECT_GCC_OPTIONS`; and
* a draft successor package is prepared for review: the proposed R5
  assignment, the runner and the 17 resources re-pinned, and the focused test.

No blocker remains within the remediation's authority. §9 lists the
maintainer decisions.

## 2. Governing records read

Read in full: `.agents/AGENTS.md`; plan reading map, §0, §16 and §20; `docs/review/Handover information`;
the prompt; the [R4 HARD STOP review](project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md)
and the acceptance/authority record. Read in the parts this work touches:
the R4 assignment
(`7d472c0a…e8cc`, 137,335 bytes, unchanged) and its runner, blocks and test;
D2 §5.3.3–§5.3.5 (flag vectors, drift table, procedure); `build.sh`,
`enter.py`, `provision.py`, `ic1check.py`, `cc1check.py`, `toolchain.lock`,
`rp11_launch.py`, `review_manifest.py` and their tests. The closed R4 handback
was verified by digest only (`0302ee9d…fdda`, 64,273 bytes, equal to the
reviewed identity) and was not edited.

## 3. GCC semantics: the evidence, all from the pinned toolchain

Every observation below was made with the pinned `gcc-15`/`cc1` inside an
existing local build root. That root was first regenerated with `enter.py
manifest` and compared **byte-equal** with the committed `build-root.manifest`
(`f08ba9de…e76f`). Two roots were used: `root-a` and `root-c`, both provisioned
by I-7 on this host from the lock and left in that session's scratchpad. They
were only read and entered read-only. Nothing was downloaded or provisioned.

| Question | Evidence | Result |
|---|---|---|
| Canonical spelling | `gcc-15 --help=params` | documents `--param=ggc-min-expand=` ("as a percentage of the total size of the heap") and `--param=ggc-min-heapsize=` ("in kilobytes") in the joined form |
| Values selected on this host | `gcc-15 -Q --help=params` | `100` and `131072`, the B1 fixture's values |
| Host resources reach the heuristic | unfixed R-2 build under `RLIMIT_AS` 1.0 GB / 800 MB, and 800 MB plus `RLIMIT_RSS` 2,221,056 | `95/131072`, `82/131072` and `82/4096`; `cc1.v` lengths 5119/5119/5117; **all four normative digests unchanged** |
| An explicit value overrides the heuristic | fixed build, with and without the same limits | `100/131072` in every case; `cc1.v` byte-identical |
| Spelling equivalence | `--param name=v` and `--param=name=v` builds | identical `cc1.v` (`e99cee65…`). The driver canonicalizes both to the joined form |
| Last value wins | a later `--param=ggc-min-expand=94` (and the separate spelling) | `cc1` reports `94` (and `2169`). This is why "exactly once" is enforced |
| Normative outputs | every build above | image, map, listing and `launch.s` equal `expected.sha256`; the listing equals the committed listing |

Disclosed residual: R4 observed `ggc-min-heapsize=2169` on `oracle-test`. Local
limits never produced a value below `4096`, so the precise host mechanism
behind `2169` is **not reproduced here**. It does not affect the remediation.
The explicit value is applied after the heuristic, whatever the heuristic
computed: the override tests show `2169` itself accepted as an explicit value
and the fixed values reported under every tested limit. Confirming this on
`oracle-test` is the successor run's job and was not attempted.

Values chosen: `100` and `131072`, GCC's own upper bounds (selected on any host
with ≥ 1 GiB available). Consequences:

* the `GGC heuristics:` line of the fixture is byte-identical to B1's;
* GC behaviour is what the B1 reference and this host already used; and
* for this ~6 KB translation unit, cc1 never approaches a 128 MiB heap
  threshold.

## 4. Complete `cc1.v` dynamic-field audit

The fixture has 22 lines and ends with a newline. Classes:

* **C** — compiled into the pinned binaries (lock `tool=` digests; R-1
  manifest).
* **V** — derived from `build.sh`'s fixed vector and `BUILD_ARGV` (source pins;
  IC-1 exact `COLLECT_GCC_OPTIONS`; T-L3).
* **E** — affected by the environment, which `env -i` reduces to `build_env`
  and IC-1 compares exactly per process.
* **F** — affected by root filesystem state (R-1 manifest; IC-1 path rules).
* **H** — affected by host resources not pinned by any contract.

| Line | Content | Inputs | Class | Disposition and evidence |
|---|---|---|---|---|
| 1 | `Using built-in specs.` | presence of a `specs` file in the driver's search path; `GCC_EXEC_PREFIX` | F, E | bound: absence is a manifest fact, the failing `access` is checked by IC-1 as manifest-absent, and the variable is cleared. Unchanged in R4 across HA-1/HA-2 variation |
| 2 | `COLLECT_GCC=/usr/bin/gcc-15` | driver `argv[0]` | V | bound by `build.sh` and IC-1 (`COLLECT_GCC`) |
| 3–4 | `OFFLOAD_TARGET_NAMES`, `OFFLOAD_TARGET_DEFAULT` | driver configure string | C | bound; the existing toolchain test reads them from the pinned driver's bytes |
| 5–9 | `Target:`, `Configured with:`, thread model, LTO algorithms, version line (with trailing space) | driver build | C | bound by the driver digest |
| 10 | `COLLECT_GCC_OPTIONS=…'-dumpdir' '../../build-out/'` | the vector after `prune_options`; `-o` from `$out` | V | bound. `$out` is `build-out` (fixed `BUILD_ARGV`) and is relative, so the checkout path (R-4(a)) never appears. **Changed:** it now carries the two arguments once each. Equal to IC-1's `COLLECT_GCC_OPTIONS` (tested) |
| 11 | ` /usr/libexec/…/cc1 -quiet … -Wbidi-chars=any` | the vector, rewritten by built-in specs (`-imultiarch`, `-dumpbase`, Ubuntu's `-Wformat-security -fzero-init-padding-bits=all -Wbidi-chars=any`); `self_spec` empty | V, C | bound; `self_spec` emptiness is checked by the existing toolchain test. **Changed:** it now carries the two arguments once each, after `-o`. Not tied to the host CPU (`-march=x86-64 -mtune=generic`, no `native`) |
| 12 | `GNU C11 (Ubuntu …) version 15.2.0 (x86_64-linux-gnu)` | cc1 build | C | bound |
| 13 | `compiled by GNU C …, GMP 6.3.0, MPFR 4.2.2, MPC 1.3.1, isl isl-0.27-GMP` | build-time headers, and isl's runtime version | C, F | bound: the run-time libraries (`libgmp10`, `libmpfr6`, `libmpc3`, `libisl23`) are manifest files. A header/library mismatch would add a warning line, which exact comparison would catch |
| 14 | empty | format | C | bound |
| 15 | `GGC heuristics: --param ggc-min-expand=… --param ggc-min-heapsize=…` | physical memory and `RLIMIT_AS`/`RLIMIT_DATA`/`RLIMIT_RSS`, unless given explicitly | **H → V** | **remediated.** Fixed by the two arguments. Pinned-toolchain evidence in §3 |
| 16–18 | include search banners, `End of search list.` | `-nostdinc`, no `-I`; `CPATH`, `C_INCLUDE_PATH` | V, E | bound: the list is empty by construction and the variables are cleared, so no "ignoring nonexistent directory" line can appear |
| 19 | `Compiler executable checksum: edd70396…` | compiled into cc1 | C | bound by the cc1 digest |
| 20 | `COMPILER_PATH=…` | configured prefixes, relative to the driver's resolved location (`argv[0]`, `/proc/self/exe`); `GCC_EXEC_PREFIX`, `COMPILER_PATH` | C, F, E | bound: the links are manifest entries, `/proc/self/exe` is IC-1's single recorded `/proc` path (HA-1 provides the mechanism), and the variables are cleared |
| 21 | `LIBRARY_PATH=…` | as line 20, plus multilib/multiarch configuration; `LIBRARY_PATH` | C, F, E | bound as line 20 |
| 22 | `COLLECT_GCC_OPTIONS=…'-dumpdir' '../../build-out/launch.'` | as line 10 | V | bound. **Changed** as line 10 |

**Absent by construction.** The following cannot appear in `cc1.v`, and each
would fail exact comparison if it did:

* timestamps, PIDs, temporary-file names (`-S`; `/tmp` and `/var/tmp` empty
  and read-only), host name, user, uid and the absolute checkout path;
* translated messages (`LC_ALL=C`);
* colour or URL escapes (stderr is a file, not a tty; `GCC_COLORS`,
  `GCC_URLS`, `TERM` and `COLUMNS` are unset);
* timing reports (no `-ftime-report` or `-Q`); and
* compiler diagnostics (`-Werror`, so a diagnostic fails the build).

**Empirical cross-check.** In R4 the host varied in HA-1 (kernel) and HA-2
(CPU). Only line 15 differed. Locally, the four variants on two roots and the
lowered limits changed nothing except line 15 when it was unfixed.

**Normative outputs versus diagnostic provenance.** `rp11-launch`,
`rp11-launch.map`, `rp11-launch.x86_64.listing` and `launch.s` are the
normative outputs (`expected.sha256`, unchanged). `cc1.v` remains diagnostic
provenance: S9 compares it exactly, but it is **not** a fifth normative output,
and `expected.sha256` still has exactly four lines (tested).

## 5. Proof that the normative artifacts are preserved

Final tree, gated `enter.py build` (R-1 gate `f08ba9de…e76f equal` in each
run):

```text
root-a r2 / r4a-path / r4b-time / r4c-user   rc=0  expected.sha256 OK, listing cmp OK, cc1.v == fixture
root-c r2 / r4a-path / r4b-time / r4c-user   rc=0  expected.sha256 OK, listing cmp OK, cc1.v == fixture
```

Each of the 8 builds reproduced all 4 digests and the listing, and its `cc1.v`
was the fixture exactly. `expected.sha256`, the listing, `launch.c`,
`select.h`, `start.s`, the linker script, `build-root.manifest`, XD and its
table are unchanged.

## 6. Changed paths and identities

`→` separates the HEAD identity from the new one. Every path below is
modified; none is committed.

| Path | Bytes | SHA-256 | Change |
|---|---|---|---|
| `infra/rp11-launch/build.sh` | 2819 → 3254 | `7c8fc6da…b1b738e0` → `87e318cd…d333cfd1` | the two arguments, plus an explanatory comment (no backtick, per T-L3) |
| `infra/rp11-launch/verify/fixtures/cc1.v.baseline` | 5120 → 5305 | `b77f92dc…9992905b` → `e99cee65…af6bb13a` | re-derived from the gated R-2 build (§5) |
| `infra/rp11-launch/verify/ic1check.py` | 18546 → 20364 | `ea7d9dd3…13316917` → `167d16ae…af2fceed` | `COLLECT_GCC_OPTIONS`; new `FIXED_PARAMS` and `_check_fixed_params` over the driver and `cc1` argv |
| `infra/rp11-launch/toolchain.lock` | 16509 → 16769 | `f9238073…eef784cf` → `f704c0f4…4b3563d6` | `ic1_env_compiler` gains the two arguments, and a comment; packages, tools and the manifest digest are unchanged |
| `tools/phase_5_0_evidence/rp11_launch.py` | 15849 → 16942 | `5a2f4694…d189c2b1` → `0d4ece45…9f626a08` | `COMPILER_FIXED_PARAMS` (serialized as `build.compiler_fixed_params`); driver environment; fixture length/digest; lock digest |
| `tools/phase_5_0_evidence/review_manifest.py` | 73785 → 75172 | `311f1d03…2f5c1844` → `09983ff7…81007dd7` | `MANIFEST_VERSION` 30 → **31**, with its rationale |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | 376981 → 377250 | `c9afaf7c…eaba4b5c` → `b9f03a47…ed14817a` | regenerated |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | 178810 → 178810 | `f02b7acf…729dec3d` → `2ac6e5e7…2b11c64f` | regenerated; only the digest line moved |
| `tests/test_rp11_launch_source.py` | 47923 → 56363 | `6d2f2820…a711cf5c` → `abbc676d…5578657a` | transcribed vector; fixture pins; trace argv; new FRESH-R4-HS-1 section |
| `tests/test_rp11_launch_cc1_determinism.py` (new) | 6405 | `1d1c3534…e7617254` | real-root determinism tests; skip without a root |
| `tests/phase_5_0_evidence/test_concrete_plan.py` | 54935 → 54935 | `1055fdb2…64fd7e2f` → `8cc4d417…f8ee38a1` | fixture length/digest |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | 35486 → 35795 | `13a3817a…4856441e` → `6d572e01…b326efef` | version 31 |
| `tools/r5_runner/r5run.py` | 58050 → 58905 | `4ef88bd6…a63be015` → `5626a9ec…145a9142` | R5 identifiers; `REVISION`; R4 run consumed; fixture digest and the new `BASELINE_LENGTH`; `PINS` |
| `tools/r5_runner/blocks/s01.sh`, `s04c.sh`, `s04d.sh`, `s11.sh` | unchanged lengths | see the R5 §3.5 table | the 8 moved Appendix A/B values; S1.8's tuple (`s01.sh` only) |
| `tools/r5_runner/blocks/s12-end.sh` | 1283 | `eda40b93…` → `9aaf1069…d59d46db` | handback path `…-r5-handback.md` |
| `tests/test_r5_runner.py` | 30835 → 35674 | `6bc5320c…f26b448f` → `95647bb8…44a3154f` | derivation from R3 with R5's appendices plus one declared amendment; 4 new identity tests |
| `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md` (new, draft) | 140080 | `4073360b0894c212e5b5507249c011d1d4197c09af2094e877829fcb9b00a1e1` | proposed successor assignment (§8) |
| this handback | — | — | new |

**Contract and digest changes:**

* review manifest version 31, aggregate
  `448f280511fc433a9098b8da278e32277cc108a4eb5c7a29071993b39686a0a3`;
* S1.8's expected tuple:
  `(31, 448f2805…a0a3, True, b9f03a47…817a, False)`;
* `TOOLCHAIN_LOCK_SHA256` is `f704c0f4…63d6`; and
* `CC1_V_BASELINE_*` are `5305` and `e99cee65…b13a`.

**Unchanged:**

* `BUILD_ROOT_MANIFEST_SHA256`, the expected-output digests, XD digests and
  the agreed stream;
* `cc1check.py` (`16b78462…4b72`), `enter.py`, `provision.py` and
  `elfcheck.py`; and
* `tests/test_rp11_launch_toolchain.py` (`ff3d458c…b76f`, still 12 tests,
  which S10 counts) and `tests/rp11_launch_support.py`.

**Stale-pin audit.** Within code, tests, runner and resources:

* no reference to `b77f92dc`, `f9238073`, `7c8fc6da`, `ea7d9dd3`, `c9afaf7c`,
  `f02b7acf`, `5a2f4694` or `311f1d03` remains, except four places where it is
  retained deliberately as history:
  * `test_the_fixture_differs_from_b1_only_by_the_fixed_params`, which keeps
    the B1 identity to prove the delta;
  * `R5_AMENDMENTS` in the runner test, which records the R3 text being
    replaced;
  * `rp11_launch.py`, whose comment describes the old fixture; and
  * the version-29/30 history comments in `review_manifest.py` and
    `test_r16_remediation.py`;
* `tests/test_r5_runner.py` now checks mechanically that the R5 assignment's
  §3.2 table, Appendices A, B and C, the §3.5 table and the §13 command and
  `/goal` line equal the files; and
* governance and archive documents still cite the old values historically.
  They were not edited (§9).

## 7. Regression tests added

**Source tests** — `tests/test_rp11_launch_source.py`, toolchain-free:

* **one contract everywhere.** The contract module, IC-1, the lock's compiler
  environment and the manifest section agree. Each token appears once in each
  `COLLECT_GCC_OPTIONS`, and no other `ggc`.
* **`build.sh` supplies each exactly once.** The only tokens containing
  `param`/`ggc` are the two fixed ones. There is no `@file` or `-specs`. The
  caller's one argument reaches the compile line only inside the two quoted
  `$out` paths.
* **9 mutations × 2 vectors** (driver and `cc1`). The mutations are: one or
  both absent, duplicated, changed expand, changed heapsize, later joined
  override, later separate override, earlier separate override, and response
  file. Each is refused by the IC-1 rule.
* **Reordering and moving.** Reordering the two, or moving them to just before
  `-o`, passes the once-only rule. It is still refused, because the derived
  `COLLECT_GCC_OPTIONS` no longer equals the pinned one. That is what IC-1
  and `cc1.v` compare.
* **IC-1 over synthetic traces.** The 9 mutations are applied at both the
  driver and the `cc1` execve (18 cases). Each fails naming the executable.
  There are exact-message tests, and the conforming trace's `cc1` argv is
  taken from the committed fixture's own `cc1` line.
* **Contract mutation.** Changing `IC1.FIXED_PARAMS` makes the conforming trace
  fail.
* **The fixture records each value once per line**; its `GGC` line is derived
  from `COMPILER_FIXED_PARAMS`.
* **The fixture differs from B1 only by the three insertions.** Removing them
  yields the 5,120-byte B1 fixture with B1's digest.
* **`cc1check`.** It still returns `HARD_STOP` for `94/2169` and for a one-unit
  heapsize change, and `PASS` only for identical bytes.

The existing fixture-contract mutation tests (one-byte change, append,
truncate, wrong expectations) now pin 5305/`e99cee65…`.

**Toolchain tests** — `tests/test_rp11_launch_cc1_determinism.py`, which needs
a root:

* the fixed build reproduces the fixture without and with lowered limits;
* the same limits move only the unfixed `GGC` line. The values are not
  asserted, because they are host-specific. All other bytes and all outputs
  are unchanged; and
* the last value given wins, in both spellings.

**Fail-before evidence.** With HEAD's `build.sh` swapped in temporarily, then
restored and re-verified by digest, 18 of the new and affected tests failed.
These included both real-root determinism tests, T-L3's vector test, the IC-1
environment and driver-derivation tests, every driver mutation case, the
reordering cases and the contract-mutation test. A real IC-1 trace with
`--param=ggc-min-expand=94` injected into `cc1`'s argv fails with
`…cc1: ggc-min-expand is also given as ['--param=ggc-min-expand=94']`.

## 8. Proposed successor assignment (draft, for Codex)

[`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md)
is SHA-256 `4073360b…a1e1` and 140,080 bytes.

**How it was made.** It was generated from R4 by a counted substitution
script: every old value had to occur exactly the expected number of times, and
none may remain. The header, §0/§0.1, §1, §2, §3.1, §3.2, §3.5, §4.4, §5 and
§12 were then edited by hand. §0.1 lists its five amendments.

**What it proposes:**

* work ID `C-P5.0-R5-RP11-FRESH-R5-R5`;
* handback `…-fresh-independent-rebuild-r5-handback.md`;
* R4's run `p5-r5-fresh-20261003T234834Z-4fc93046` added as consumed and
  refused, with its retained paths forbidden; and
* runner `5626a9ec…9142` (58,905 bytes) in the §13 command.

**What it leaves unchanged.** Every step, status code, comparison and the
R4-R1 waiting contract are unchanged. In the resources, only the pinned values
of §6 move.

**Mechanical checks.** `tests/test_r5_runner.py` (79 tests) derives all 17
resources from R3, which is pinned by digest. The derivation applies R5's
appendices and the one declared S1.8 amendment, which must apply exactly once.
The test requires byte equality, and that R5's §6 displays every resource
exactly.

**Not done here:** an activation record, and any Gemini invocation authority.

## 9. Unresolved maintainer decisions and dependencies

1. **Review and closure.** Codex reviews the remediation, then Peter Duscha
   decides whether `FRESH-R4-HS-1` is closed. Claude makes no closure claim.
2. **U-7 identifiers** in the R5 draft need confirmation. A different handback
   path means re-pinning `s12-end.sh`, the runner and the §3.5/§13 values.
3. **Commit before activation.** S1.4 binds `infra`, `tests`, `tools` and
   `pytest.ini` to `HEAD`. The changed and new files here are uncommitted, as
   are the earlier untracked review records. No commit was made (none
   authorized).
4. **U-19, the retained R4 paths.** The R4 run's
   `oracle-test:/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` paths remain
   and their size is unknown here. They are forbidden inputs and do not trip
   the freshness check. S2.18d's 4 GiB floor is measured with them present.
   Whether to authorize inspection or cleanup first is the maintainer's
   decision.
5. **U-20, the D2 design text.** D2 §5.3.3's transcribed vector and §5.3.4's
   drift table predate the two arguments. I did not edit the accepted design.
   The binding sources (`build.sh`, the contract module, IC-1, the lock and
   the manifest) agree and are tested. A dated D2 amendment note is a
   documentation decision.
6. **Governance documents.** `status.md`, `Handover information`, plan §20,
   the change-log and the decision register are not updated by me. These are
   current-state records for the maintainer or Codex, and they already carry
   other uncommitted edits that I preserved.
7. **Optional, S10 coverage.** The new real-root determinism tests are outside
   `tests/test_rp11_launch_toolchain.py`, so S10's accepted 12-test contract
   is unchanged. Running them on `oracle-test` in a later run would need a
   separately reviewed S10 change. Their lowered-limit build sets rlimits only
   for its own child processes.

## 10. Commands, results, skips and checks not run

**Interpreter.** Repository-host `/opt/freedom-blades/platform/venv-web/bin/python`
(Python 3.12.3, pytest 9.1.1). `TEST_DATABASE_URL` was **unset**, so every
database test skipped. That is an unverified assertion, not PostgreSQL
evidence. `RP11_LAUNCH_BUILD_ROOT` pointed at the R-1-verified `root-a` (and
`root-c` where stated). The suites ran serially.

| # | Command (abridged) | Result |
|---|---|---|
| 1 | `enter.py manifest --root root-a` / `root-c`, `cmp` with the committed manifest | both byte-equal (`f08ba9de…e76f`) |
| 2 | baseline before any change: focused launcher, runner and evidence suites | 738 passed and 3,383 passed, 0 skipped |
| 3 | pinned `gcc-15 --help=params`, `-Q --help=params` in root-a | §3 |
| 4 | scratch experiment builds (`exp.py`): unfixed, separate, joined, other values, override, each with and without limits | §3 |
| 5 | gated `enter.py build`, 2 roots × 4 variants, initially and again on the final tree; `sha256sum -c expected.sha256`; `cmp` of the listing and `cc1.v` | all rc 0, all identical (§5) |
| 6 | `enter.py ic1` (root-a, `/rp11/co`) + `ic1check.py` on the real trace | `verdict: pass`, `failures: []`; `cc1` argv carries both tokens once |
| 7 | the same trace with an injected later override | rc 1, the named failure (§7) |
| 8 | HEAD `build.sh` swapped in, selected tests, then restored (digest re-checked `87e318cd…`) | 18 failed, 40 passed (fail-before) |
| 9 | `python -m tools.phase_5_0_evidence.execution.cli --manifest-out … --render …` (**never `--execute`**): twice to scratch, once to the checked-in paths, once more at the end | each rc 0, `DRY RUN — nothing was executed.`; 138 steps, 43 mutations, 47 cleanup steps, 4 unresolved (C-7, C-S4-3), `executable: False`, digest `448f2805…a0a3`; **every manifest, render and stdout byte-identical** |
| 10 | S1.8's tuple computed by import (not by running a block) under `/usr/bin/python3` and venv-web | both `31 448f2805… True b9f03a47… False` |
| 11 | `gen_r5_stage1.py`, then `gen_r5_stage2.py` (scratch) | 8 moved pins, all counts exact; 5 resources rewritten |
| 12 | final focused run: `pytest -q -rs -p no:cacheprovider` over the four launcher modules, `tests/test_r5_runner.py` and `tests/phase_5_0_evidence` | **4,175 passed, 0 skipped, 0 failed**. Per module: source 682, gate 15, toolchain 12, determinism 4, runner 79, evidence 3,383 |
| 13 | `tests/test_rp11_launch_toolchain.py` + the determinism module with root-c | 16 passed |
| 14 | the determinism module without `RP11_LAUNCH_BUILD_ROOT` | 4 skipped, with the explicit reason |
| 15 | `pytest -q -rs --continue-on-collection-errors tests/test_*.py tests/phase_5_0_evidence` | 6,960 passed, 337 skipped, 1 failed, 32 errors. Every skip names `TEST_DATABASE_URL` or the missing `google` module. **The failure and all 32 errors are `ModuleNotFoundError: discord` or `google`** in this interpreter: 7 collection errors, 25 setup errors, and `test_sheet_bootstrap_boundary`. This is an environment limit (no bot code touched), not a pass |
| 16 | `py_compile` of the 10 changed or new Python files; `sh -n build.sh`; `bash -n` on every block | all clean |
| 17 | `git diff --check`; trailing-whitespace scan of the two new text files | clean |
| 18 | `python3 .claude/hooks/test_guards.py` | all guard cases passed (hooks unchanged) |
| 19 | digests of the R4 handback, assignment and review | unchanged (`0302ee9d…`, `7d472c0a…`, `7a4666cb…`) |

**Not run, and why:**

* anything on `oracle-test`, R-5, S1–S12 or any runner block: forbidden by the
  task;
* `tests/web` and the Foundry `node --test` suite: they are unrelated, and
  `tests/web` cannot be collected by this interpreter;
* database-backed tests: `TEST_DATABASE_URL` was unset, so those tests
  skipped; and
* formatter, linter and type checker: none is configured or installed (no
  ruff/mypy). This is unavailable tooling, not a pass.

## 11. Security, configuration and rollback

**Security.**

* No secret was read or written.
* No network access, download, package installation, privilege, service or
  database action occurred.
* bubblewrap ran unprivileged, with the root bound read-only.
* The rlimit experiments only lowered limits for child processes.

**Configuration and deployment.** None. Nothing is installed, wired or
deployed. `plan.is_executable` remains `False`.

**Rollback.** Restore the files of §6 to `HEAD` and delete the three new files
(the determinism test, the R5 draft and this handback). The R4-era pins then
hold again, because `HEAD` is the reviewed R4 state.

## 12. Proposed reviewer focus

1. **The §3 evidence.** Check that it establishes the override and last-wins
   semantics from the pinned toolchain. Check the disclosed `2169` residual.
2. **The §4 audit's completeness.** In particular, check the claims for lines
   1, 13, 20 and 21 (classes F and E).
3. **IC-1's new rule.** Does checking argv tokens leave any spelling or
   channel open? Candidates: `-param`, response files, `specs`, environment.
4. **Is "exactly once" overconstrained?** The reordering refusal relies on
   exact `COLLECT_GCC_OPTIONS` comparison, not on the once-only rule.
5. **The R5 draft.** Check that only §0.1's amendments differ from R4. A
   normalized diff of R4 and R5 shows the hand-edited prose; the 17 resources
   are proved by test.

## 13. Statement

No remote host was accessed. No `oracle-test` command, synchronization, SSH or
inspection took place. The retained R4 paths were not inspected, changed or
deleted. No cleanup, retry or R-5 execution occurred, and the evidence harness
never ran with `--execute`. No commit or push was made.

The closed R4 handback, the R4 assignment and Codex's review are unchanged.
`FRESH-R4-HS-1` is not closed by this handback. R-5 remains Blocking and
unaccepted; RP-11 remains unwired and unmet; `plan.is_executable=False`; PO-9
and PO-14 remain open; and Package 5.0 remains not ready.

Claude stops here.
