# Codex re-review — I-7-R1 IC-1 exact-environment remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-I7-R1`

Date: 2026-10-01

Implementer: Claude

Independent reviewer: Codex

Disposition: **no Blocking, Important or Optional finding. Recommend accepting
`I7-R1-1` as remediated and D-2 as implemented.** Peter Duscha remains the
acceptance authority.

The remediation defines the ten ordered successful `execve` calls and the
complete environment for each process class. `ic1check.py` parses the complete
environment array and compares exact mappings: missing, changed, extra,
duplicate and malformed entries fail. `PWD` and `OLDPWD` are bound to the
selected controlled checkout. The compiler-driver values are fixed outside the
trace and checked against a separate derivation from `build.sh` and the pinned
driver. The lock, planning contract and serialized manifest agree.

The focused negative matrix covers every required variable at every process
position under both controlled checkout paths, including each of the four
driver additions. It also covers extra, duplicate and malformed entries,
incorrect `PWD`/`OLDPWD`, malformed or abbreviated records and changed process
order. The accepted R1-D-1 derivation is consistent with the returned fresh
trace: GCC's `prune_options` removes the earlier `-fno-pic` when the later
`-fno-pie` cancels it through the relevant `Negative()` cycle.

## Independent checks

Codex ran on the repository host:

* focused IC-1 selection: **368 passed**, 266 deselected;
* `tests/test_rp11_launch_source.py` plus `tests/phase_5_0_evidence`:
  **4,004 passed**;
* Python compilation of the changed Python surface: clean;
* `git diff --check`: clean; and
* submitted lock, checker, contract, manifest and generated-artifact digests:
  equal to the handback.

The two pre-existing unknown pytest-asyncio configuration warnings appeared.
`tests/test_rp11_launch_toolchain.py` reported **12 explicit skips** because no
`RP11_LAUNCH_BUILD_ROOT` was named in Codex's review session. Those skips are
not passes. Claude's handback records the fresh isolated-root R-1, R-2, both
IC-1 variants and T-L11/T-L10 runs; Codex did not repeat that fresh-root run.

No SSH, `oracle-test`, database, protected-artifact, installation, service,
controlled-write, evidence-band, harness `--execute`, R-5, H-1/H-2, commit or
push action was performed.

This review closes no broader gate. R-5 remains independently performed only
under a later explicit authorization and must vary and record at least one of
HA-1 … HA-3. RP-11 remains unwired and unmet; `plan.is_executable=False`;
P5.0-R5 remains Blocking; and Package 5.0 remains not ready.
