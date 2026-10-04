# Fresh R-5 successor R5 independent static-launcher rebuild handback

Execution work ID: `C-P5.0-R5-RP11-FRESH-R5-R5`
Run identifier: `p5-r5-fresh-20261004T110421Z-b9e8f92d`
Executor: Gemini
Controlling assignment: [`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md)
Written by: `tools/r5_runner/r5run.py` on the executor's single invocation (assignment R5 §13)

---

## 0. Runner identity, verified before any host action

The runner verified these files before writing this file and before step 1.
Every block that follows was sent from the verified in-memory bytes.

| File | Bytes | SHA-256 | Result |
|---|---:|---|---|
| `tools/r5_runner/r5run.py` | 58905 | `5626a9ecfa8486b058cfe9ab1c45f163671827d77a7f4adb34a1e8b9145a9142` | OK |
| `tests/test_r5_runner.py` | 35674 | `95647bb82646550ffd09e4a693136a6ff1dac20bbfd137cde017ed4544a3154f` | OK |
| `tools/r5_runner/blocks/s01.sh` | 11516 | `119e3d924fe4020588311df6404f927fdf356f47d4cc709bf8e74d13a23c81fd` | OK |
| `tools/r5_runner/blocks/s02.sh` | 7000 | `a0cda6026583275d45c1a8b88cc0ed77ba97a9973408d66990469901ef78d264` | OK |
| `tools/r5_runner/blocks/s03.sh` | 1560 | `2d4c39b8ccf9d84afc4a439b08611ce3f5bca32a3b97021bb6caca8d8759676b` | OK |
| `tools/r5_runner/blocks/s04a.sh` | 1172 | `1a948d6758f6ece09dbafc8f250a5682ec2b096cbed814eb25a8ed57657ef0a1` | OK |
| `tools/r5_runner/blocks/s04b-end.sh` | 232 | `a77be397cf2b9a00737f25a5c4d4e17dc706e2d5478353f9afc2dbdbb95c261e` | OK |
| `tools/r5_runner/blocks/s04b-start.sh` | 240 | `55ab56d97581e442bf24c3ebe6ab9e6b6714a1aaac04f0f0d620e3d45d4aff85` | OK |
| `tools/r5_runner/blocks/s04b-sync.argv` | 313 | `7dddbaef33807f4158792c7270d5a6d7e38049938a87953c7c905c44c8738050` | OK |
| `tools/r5_runner/blocks/s04c.sh` | 4420 | `4110a1c52f28f8996fde2d674716749c3be79dba572c193839279a79c2c814b7` | OK |
| `tools/r5_runner/blocks/s04d.sh` | 8708 | `1cbd8aca86b11d0405f657b42ca36a14898ddca2694f7e5912cb6aae69ab06ea` | OK |
| `tools/r5_runner/blocks/s05.sh` | 3231 | `7750e2502d7ecea05350d3d596b15d59b0b7243789502cc954592862ff4cb64b` | OK |
| `tools/r5_runner/blocks/s06-s07.sh` | 3193 | `58a63f9cefb8323b339e92dd3f799e2570291803792c705a4face97eacc49868` | OK |
| `tools/r5_runner/blocks/s08.sh` | 2440 | `c55ada18c1cd607189e7f6ef4d99de4e4589ee1d78208a643006caf900464878` | OK |
| `tools/r5_runner/blocks/s09.sh` | 1588 | `46bbcd1f6eee93531d08350699b83f71897e3c40cea35c2eedde54c517d02dc6` | OK |
| `tools/r5_runner/blocks/s10.sh` | 2029 | `6502636bf63a5194574ca553e3ca8c2ac3889e2d2bfe97c76e890f60731828f7` | OK |
| `tools/r5_runner/blocks/s11.sh` | 10066 | `1a0004523890ce3d19be1fd87353bbc5ea692d9a65e07a431045f819290e8bc2` | OK |
| `tools/r5_runner/blocks/s12-end.sh` | 1283 | `9aaf1069e4637e3b342712cb33817c4282c1fa8efef8296f54974c6dd59d46db` | OK |
| `tools/r5_runner/blocks/s12-start.sh` | 240 | `bf495fd370a236b04295e955ce083e63fd4ead1fa8e2fabe4ca788a21f1f2aa3` | OK |

Interpreter: `/usr/bin/python3 3.12.3`; flags: isolated=1, dont_write_bytecode=1.

---

## 1. Executor identity and §2 independence attestation

I, Gemini, execute this run under assignment R5 and make this attestation
by invoking the runner with `--executor Gemini --attest-independence`,
before step 1 and before any host action:

1. I did not implement, co-author or remediate I-7 or I-7-R1;
2. I have not reused, and will not use, any earlier build root, package cache,
   checkout, work directory, build output, trace, evidence or scratch
   directory;
3. I have read the controlling assignment (`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md`) and the acceptance
   record that names me; and
4. this run is wholly fresh. I have not read, reused, copied, compared against
   or inherited any resource or artifact from my earlier R-5 run
   (`/tmp/r5-*-gemini-f8a1` on `oracle-test`), my B1 run
   (`/tmp/p5-b1-repro-20261001t190454z-*` on the repository host), my stopped
   fresh R-5 run `p5-r5-fresh-20261002T184800Z-7e9b2d41` (formerly
   `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-*` on `oracle-test`, deleted by
   Codex on 2026-10-03; any surviving copy is equally forbidden), my consumed
   R3 run `p5-r5-fresh-20261003T191400Z-9c3f71e2`, which created no
   `oracle-test` path, or my consumed R4 run
   `p5-r5-fresh-20261003T234834Z-4fc93046` (its retained
   `/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` paths on `oracle-test`).
   That includes roots, caches, checkouts, outputs, `cc1.v` bytes, manifests,
   traces, logs and pytest temporary directories.

---

## 2. Timestamps

Copied by the runner from the transcripts of §6; no value comes from any other source.

| Scope | Producing label | Host | Start | End | Status |
|---|---|---|---|---|---|
| whole run | `RUN.start` / `RUN.end` | repository host | `RUN.start start_utc=2026-10-04T11:04:21Z` | in closing record | invoking status 0 |
| step 1 | `S1.start` / `S1.end` | repository host | `S1.start start_utc=2026-10-04T11:04:21Z` | `S1.end end_utc=2026-10-04T11:04:21Z` | invoking status 0; `S1 final exit=0` |
| step 2 | `S2.start` / `S2.end` | oracle-test | `S2.start start_utc=2026-10-04T11:04:24Z` | `S2.end end_utc=2026-10-04T11:04:25Z` | invoking status 0; `S2 final exit=0` |
| step 3 | `S3.start` / `S3.end` | oracle-test | `S3.start start_utc=2026-10-04T11:04:26Z` | `S3.end end_utc=2026-10-04T11:04:26Z` | invoking status 0; `S3 final exit=0` |
| step 4a | `S4a.start` / `S4a.end` | oracle-test | `S4a.start start_utc=2026-10-04T11:04:26Z` | `S4a.end end_utc=2026-10-04T11:04:26Z` | invoking status 0; `S4a final exit=0` |
| step 4b | `S4b.start` / `S4b.end` | repository host | `S4b.start start_utc=2026-10-04T11:04:26Z` | `S4b.end end_utc=2026-10-04T11:04:37Z` | S4b.start: invoking status 0; S4b.sync: invoking status 0; S4b.end: invoking status 0 |
| step 4c | `S4c.start` / `S4c.end` | repository host | `S4c.start start_utc=2026-10-04T11:04:37Z` | `S4c.end end_utc=2026-10-04T11:04:37Z` | invoking status 0; `S4c final exit=0` |
| step 4d | `S4d.start` / `S4d.end` | oracle-test | `S4d.start start_utc=2026-10-04T11:04:38Z` | `S4d.end end_utc=2026-10-04T11:04:38Z` | invoking status 0; `S4d final exit=0` |
| step 5 | `S5.start` / `S5.end` | oracle-test | `S5.start start_utc=2026-10-04T11:04:38Z` | `S5.end end_utc=2026-10-04T11:05:16Z` | invoking status 0; `S5 final exit=0` |
| steps 6/7 combined | `S6-S7.start` / `S6-S7.end` | oracle-test | `S6-S7.start start_utc=2026-10-04T11:05:17Z` | `S6-S7.end end_utc=2026-10-04T11:05:20Z` | invoking status 0; `S6-S7 final exit=0` |
| step 8 | `S8.start` / `S8.end` | oracle-test | `S8.start start_utc=2026-10-04T11:05:21Z` | `S8.end end_utc=2026-10-04T11:05:21Z` | invoking status 0; `S8 final exit=0` |
| step 9 | `S9.start` / `S9.end` | oracle-test | `S9.start start_utc=2026-10-04T11:05:22Z` | `S9.end end_utc=2026-10-04T11:05:22Z` | invoking status 0; `S9 final exit=0` |
| step 10 | `S10.start` / `S10.end` | oracle-test | `S10.start start_utc=2026-10-04T11:05:22Z` | `S10.end end_utc=2026-10-04T11:05:37Z` | invoking status 0; `S10 final exit=0` |
| step 11 | `S11.start` / `S11.end` | oracle-test | `S11.start start_utc=2026-10-04T11:05:39Z` | `S11.end end_utc=2026-10-04T11:05:40Z` | invoking status 0; `S11 final exit=0` |
| step 12 | `S12.start` / `S12.end` | repository host | `S12.start start_utc=2026-10-04T11:05:40Z` | in closing record | S12.start: invoking status 0; S12.end: in closing record |

## 3. Repository state

Commit (S1.2): `4cbdf0b6ecabad7484e64ff0485587a17f55dcaf`

Complete S1.3 output, every line of `git status --short --untracked-files=all` followed by `git_status_lines` and `git_status_sha256`, extracted from the step-1 transcript:

```text
 M .agents/AGENTS.md
 M docs/implementation-plan-archive/README.md
 M docs/implementation-plan.md
 M docs/operations/disposable-test-server-archive/README.md
 M docs/operations/disposable-test-server.md
 M docs/project-management/change-log.md
 M docs/project-management/decision-register.md
 M docs/project-management/status-archive/README.md
 M docs/project-management/status.md
 M "docs/review/Handover information"
 M docs/review/handover-archive/README.md
 M docs/review/phase-5-0-evidence-harness-concrete-plan.md
 M docs/review/phase-5-0-evidence-harness-review-manifest.json
 M docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md
?? docs/implementation-plan-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/implementation-plan-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/operations/disposable-test-server-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/operations/disposable-test-server-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/project-management/status-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/project-management/status-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/review/Handover-information-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/review/Handover-information-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop-acceptance.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign-r1.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-cc1-determinism-remediation.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-acceptance-and-gemini-activation.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-r4-r1-acceptance-and-gemini-activation.md
git_status_lines=63
git_status_sha256=ba8d3192e171dd34503ab991d30bd531a29827a7ed2892cdb9ce24a0287f86ee
```

Runner check of line count and digest: equal.

S1.4, S1.5, S1.6, S1.7, S1.8, S4c.2, S4c.3, S4d.3 and S4d.4 result lines:

```text
[S1]
repository_state=clean
S1.4 repository-state exit=0
S1.5 sha256sum-check exit=0
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S1.6 hashlib-and-tree-check exit=0
package_lines 62
archive_snapshot=20261001T000000Z
build_root_manifest_sha256=f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f
entry_mechanism=bubblewrap 0.9.0 (Ubuntu 24.04 host package, unprivileged user namespace; --unshare-all --die-with-parent --new-session --clearenv, root bound read-only at /); informative, not a pin (HA-3)
S1.7 lock-facts exit=0
S1.8 in-memory-review-manifest exit=0
[S4c]
repository_state=clean
S4c.2 repository-state exit=0
S4c.3 sha256sum-check exit=0
[S4d]
S4d.1 checkout-stat exit=0
S4d.3 sha256sum-check exit=0
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S4d.4 hashlib-and-tree-check exit=0
```


## 4. Host-assumption variation and diagnostic context

S3.1 output:

```text
HA-1 kernel_release=7.0.0-31-generic
HA-2 model_names=AMD EPYC 7551 32-Core Processor
HA-1 qualifies=yes
HA-2 qualifies=yes
HA-3 qualifies=no (version-only differences do not qualify; section 4.2)
```

| HA | Reference (§3.4) | Observed (S3.1) | Qualifies (S3.1) |
|---|---|---|---|
| HA-1 | `6.8.0-139-generic` | `7.0.0-31-generic` | yes |
| HA-2 | `AMD EPYC-Milan Processor` | `AMD EPYC 7551 32-Core Processor` | yes |
| HA-3 | bubblewrap `0.9.0`, fixed `enter.py` vector | see S2.6–S2.9 in §6 | no (version-only differences do not qualify; section 4.2) |

Step-2 observations (S2.1–S2.25), including the S2.15–S2.18d diagnostic context and the `/var/tmp` preflight, are in the step-2 transcript in §6.

End-of-run observations against step 2 (byte equality of the printed lines):

* S11.8 uname = S2.2 uname: equal
* S11.9 cpuinfo-first-processor = S2.5 cpuinfo-first-processor: equal
* S11.10 bwrap-version = S2.6 bwrap-version: equal
* S11.11 bwrap-sha256 = S2.8 bwrap-sha256: equal


## 5. Created paths

* repository host: `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md`, regular file, created by the runner for this handback.
* `oracle-test` modes, owners and groups at creation (S4a.2), checkout after synchronization (S4d.1), root (S5.8), at the end (S11.5) and sizes (S11.6), copied from §6:

```text
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-index
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-cache
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence
2775 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
755 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/build.stderr
586fdfd646ebab0de102f3033056803f93bdd36d0827fdf61b0ba15123543084  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/build.stdout
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/cc1check.err
4171ff346c7a0a863fd502ec8e132eb1c1e00b3ce1a278be8316d2fed330d558  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/cc1check.out
23a4e88bf07608fda8a5ff3f187297bfe0eb03b0b5a6ac20d79cd3b8ea571da7  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/lock-packages.txt
eab7e76ed59d0f044f6f19abf70c848497963dfb23a577130e940cb70795c19c  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/pytest.junit.xml
09865af4cecfcfe2bb8bc57aa6afd1459ca0c856072121809bd715bdc6eea66f  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/pytest.out
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/regenerated.manifest
23a4e88bf07608fda8a5ff3f187297bfe0eb03b0b5a6ac20d79cd3b8ea571da7  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/resolve.out
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/cc1.v
bfe7b3e7c0132f7f316d6704aecc087e453334c6bb1d65579c8ba252eb8c1f0c  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/launch.o
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/launch.s
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch.map
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch.x86_64.listing
154771200e4c7515d583f84911a9e124acb94e9dacca56f477935690b08618a5  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/start.o
2775 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-index
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-cache
755 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-pytest
98516	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
140	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-index
71612	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-cache
252612	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
748	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work
420	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence
5288	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-pytest
```


## 6. Invocation transcripts

Every invocation, exactly as run and in order, with its true status and both streams. The S12.end block is evidenced by its closing record.

### S1 — step block, repository host

* argv: `/bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s01.sh`
* standard input: the resource with `<RUN>` substituted, 11516 bytes, SHA-256 `119e3d924fe4020588311df6404f927fdf356f47d4cc709bf8e74d13a23c81fd`; then closed
* invoking status: `0`
* stdout: 10399 bytes, SHA-256 `6c6eaa933af67141cbe2df94dfcda4237e0e6a8929ad8e59b638a30c719eaa74`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S1.trap exit=0
RUN.start start_utc=2026-10-04T11:04:21Z
S1.start start_utc=2026-10-04T11:04:21Z
S1.start date exit=0
S1.1 cd exit=0
4cbdf0b6ecabad7484e64ff0485587a17f55dcaf
S1.2 git-rev-parse exit=0
 M .agents/AGENTS.md
 M docs/implementation-plan-archive/README.md
 M docs/implementation-plan.md
 M docs/operations/disposable-test-server-archive/README.md
 M docs/operations/disposable-test-server.md
 M docs/project-management/change-log.md
 M docs/project-management/decision-register.md
 M docs/project-management/status-archive/README.md
 M docs/project-management/status.md
 M "docs/review/Handover information"
 M docs/review/handover-archive/README.md
 M docs/review/phase-5-0-evidence-harness-concrete-plan.md
 M docs/review/phase-5-0-evidence-harness-review-manifest.json
 M docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md
?? docs/implementation-plan-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/implementation-plan-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/operations/disposable-test-server-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/operations/disposable-test-server-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/project-management/status-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/project-management/status-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/review/Handover-information-through-2026-10-02-fresh-r5-assignment-r2-acceptance.md
?? docs/review/Handover-information-through-2026-10-02-fresh-r5-procedure-acceptance.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-r1-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r5.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-reviewed-proposal.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-claude-prompt.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r4-cc1-determinism-remediation-handback.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r5-cleanup-result.md
?? docs/review/phase-5-0-p5-r5-rp11-fresh-r5-new-run-assignment-preparation-claude-prompt.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-gemini-activation.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2-acceptance.md
?? docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r2.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop-acceptance.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r3-hard-stop.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop-acceptance-and-cleanup-authority.md
?? docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-r5-hard-stop.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign-r1.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-antigravity-delivery-redesign.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-cc1-determinism-remediation.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop-acceptance-and-remediation-authority.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r4-hard-stop.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-fresh-r5-acceptance-and-gemini-activation.md
?? docs/review/project-review-2026-10-04-p5-r5-rp11-r4-r1-acceptance-and-gemini-activation.md
git_status_lines=63
git_status_sha256=ba8d3192e171dd34503ab991d30bd531a29827a7ed2892cdb9ce24a0287f86ee
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
f704c0f4f0ddbe9de92da9812dde6929f681ba778263746a603bde8b4b3563d6 16769 infra/rp11-launch/toolchain.lock OK
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f 381913 infra/rp11-launch/build-root.manifest OK
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625 328 infra/rp11-launch/expected.sha256 OK
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a 5305 infra/rp11-launch/verify/fixtures/cc1.v.baseline OK
b9f03a4791448c029b9a1eccc50416818893294357fa9f6182f85610ed14817a 377250 docs/review/phase-5-0-evidence-harness-review-manifest.json OK
2ac6e5e7721bf73347ffcc73281152f6cbec40fd2ff7167ff554ad9b2b11c64f 178810 docs/review/phase-5-0-evidence-harness-concrete-plan.md OK
87e318cdd77f1fae0a354f707d9fe32d163ba48b708bb455c670f6d4d333cfd1 3254 infra/rp11-launch/build.sh OK
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe 6314 infra/rp11-launch/launch.c OK
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b 2187 infra/rp11-launch/select.h OK
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139 857 infra/rp11-launch/start.s OK
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326 2321 infra/rp11-launch/rp11-launch.ld OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 21742 infra/rp11-launch/rp11-launch.x86_64.listing OK
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300 15106 infra/rp11-launch/buildroot/provision.py OK
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a 14521 infra/rp11-launch/buildroot/enter.py OK
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72 6021 infra/rp11-launch/verify/cc1check.py OK
167d16ae0b1cf6e82a5099b5e5b5c6b571b1f0273f8bdde7b79c55b9af2fceed 20364 infra/rp11-launch/verify/ic1check.py OK
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
0d4ece459dbffac790e3a1f7d61e0c83efe270825e0d874cded48e759f626a08 16942 tools/phase_5_0_evidence/rp11_launch.py OK
09983ff782eef3be420994f165e3168eee9682f6da8481e0427a31a481007dd7 75172 tools/phase_5_0_evidence/review_manifest.py OK
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S1.6 hashlib-and-tree-check exit=0
package_lines 62
archive_snapshot=20261001T000000Z
build_root_manifest_sha256=f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f
entry_mechanism=bubblewrap 0.9.0 (Ubuntu 24.04 host package, unprivileged user namespace; --unshare-all --die-with-parent --new-session --clearenv, root bound read-only at /); informative, not a pin (HA-3)
S1.7 lock-facts exit=0
31 448f280511fc433a9098b8da278e32277cc108a4eb5c7a29071993b39686a0a3 True b9f03a4791448c029b9a1eccc50416818893294357fa9f6182f85610ed14817a False
S1.8 in-memory-review-manifest exit=0
/usr/bin/rsync
/usr/bin/ssh
S1.9 local-tools exit=0
S1 block exit=0
S1.end end_utc=2026-10-04T11:04:21Z
S1.end date exit=0
S1 final exit=0
```

stderr:

```text
(empty)
```

### S2 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s02.sh`
* standard input: the resource with `<RUN>` substituted, 7032 bytes, SHA-256 `6a3b38d072e3b8ea24067eb089456b541762e783732a50323ecf1f37926f439e`; then closed
* invoking status: `0`
* stdout: 8796 bytes, SHA-256 `280eafa29e0188c96c3c9a7b59272e0be27714d43b9498c33d04cb24e345c466`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S2.trap exit=0
S2.start start_utc=2026-10-04T11:04:24Z
S2.start date exit=0
2026-10-04T11:04:24Z
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
var_tmp=directory mode=1777 uid=0 gid=0
S2.18a var-tmp-directory exit=0
Filesystem     Type 1024-blocks    Used Available Capacity Mounted on
/dev/sda1      ext4    46167704 6519124  39632196      15% /
S2.18b df-var-tmp exit=0
Filesystem      Inodes  IUsed   IFree IUse% Mounted on
/dev/sda1      5707520 237306 5470214    5% /
S2.18c df-inodes-var-tmp exit=0
var_tmp_mount=/ fstype=ext4 source=/dev/sda1
var_tmp_mount_options=rw,relatime
var_tmp_super_options=rw,discard,errors=remount-ro,commit=30
var_tmp_bytes_total=47275728896 bytes_available=40583368704 floor=4294967296
var_tmp_inodes_total=5707520 inodes_free=5470214 inodes_available=5470214
var_tmp_capacity=sufficient
S2.18d var-tmp-capacity exit=0
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
S2.end end_utc=2026-10-04T11:04:25Z
S2.end date exit=0
S2 final exit=0
```

stderr:

```text
(empty)
```

### S3 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s03.sh`
* standard input: the resource with `<RUN>` substituted, 1560 bytes, SHA-256 `2d4c39b8ccf9d84afc4a439b08611ce3f5bca32a3b97021bb6caca8d8759676b`; then closed
* invoking status: `0`
* stdout: 386 bytes, SHA-256 `5c8deef3d4da86ed4b412e5b8bd7eb42fb8f64b63ff1e623fcc680a5ae13c32c`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S3.trap exit=0
S3.start start_utc=2026-10-04T11:04:26Z
S3.start date exit=0
HA-1 kernel_release=7.0.0-31-generic
HA-2 model_names=AMD EPYC 7551 32-Core Processor
HA-1 qualifies=yes
HA-2 qualifies=yes
HA-3 qualifies=no (version-only differences do not qualify; section 4.2)
S3.1 qualification exit=0
S3 block exit=0
S3.end end_utc=2026-10-04T11:04:26Z
S3.end date exit=0
S3 final exit=0
```

stderr:

```text
(empty)
```

### S4a — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s04a.sh`
* standard input: the resource with `<RUN>` substituted, 1556 bytes, SHA-256 `6a5d925b962c4f1fb576d3093f75efe9b546152d80e5054f00aadeaf092a9ffd`; then closed
* invoking status: `0`
* stdout: 637 bytes, SHA-256 `0384ee4f99a0f0a9c6e2ae204adccd8dcdf9551fba9001b66c28543b1385299a`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S4a.trap exit=0
S4a.start start_utc=2026-10-04T11:04:26Z
S4a.start date exit=0
S4a.1 mkdir exit=0
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-index
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-cache
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence
S4a.2 stat exit=0
S4a block exit=0
S4a.end end_utc=2026-10-04T11:04:26Z
S4a.end date exit=0
S4a final exit=0
```

stderr:

```text
(empty)
```

### S4b.start — timestamp block, repository host

* argv: `/bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s04b-start.sh`
* standard input: the resource with `<RUN>` substituted, 240 bytes, SHA-256 `55ab56d97581e442bf24c3ebe6ab9e6b6714a1aaac04f0f0d620e3d45d4aff85`; then closed
* invoking status: `0`
* stdout: 86 bytes, SHA-256 `c8f4d0d035f822465dbe3de0f61e40ecf78d507a67e8e5ed1be8d0e557e7edda`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S4b.start start_utc=2026-10-04T11:04:26Z
S4b.start date exit=0
S4b.start block exit=0
```

stderr:

```text
(empty)
```

### S4b.sync — synchronization command, repository host

* argv: `rsync -avz --delete --include=.env.example --exclude=.env* --exclude=*.pem --exclude=*.key --exclude=yt-cookies.txt --exclude=*service_account*.json --exclude=*credentials*.json --exclude=__pycache__/ --exclude=*.py[cod] --exclude=.pytest_cache/ /opt/freedom-blades/platform/ oracle-test:/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout/`
* resource: `tools/r5_runner/blocks/s04b-sync.argv`
* standard input: `/dev/null`
* invoking status: `0`
* stdout: 272751 bytes, SHA-256 `275db60a71fb1b315614cb87d2190ae2bec4892f980fe594aad0f6f5a063018f`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

Per R5 §10.1 only the exit status and rsync's closing summary lines are embedded; the per-file list and standard error are withheld and are identified only by the digests above.

```text
sent 63,168,587 bytes  received 96,526 bytes  5,501,314.17 bytes/sec
total size is 87,264,928  speedup is 1.38
```

### S4b.end — timestamp block, repository host

* argv: `/bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s04b-end.sh`
* standard input: the resource with `<RUN>` substituted, 232 bytes, SHA-256 `a77be397cf2b9a00737f25a5c4d4e17dc706e2d5478353f9afc2dbdbb95c261e`; then closed
* invoking status: `0`
* stdout: 78 bytes, SHA-256 `c0a105aeb69839f97bf967d5bf4830c750a83fdbc7c470f0ac4f58673f551751`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S4b.end end_utc=2026-10-04T11:04:37Z
S4b.end date exit=0
S4b.end block exit=0
```

stderr:

```text
(empty)
```

### S4c — step block, repository host

* argv: `/bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s04c.sh`
* standard input: the resource with `<RUN>` substituted, 4420 bytes, SHA-256 `4110a1c52f28f8996fde2d674716749c3be79dba572c193839279a79c2c814b7`; then closed
* invoking status: `0`
* stdout: 1464 bytes, SHA-256 `faa31474de624601a9869c253b15449ae97c59ba4af4adf617b139355de9caff`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S4c.trap exit=0
S4c.start start_utc=2026-10-04T11:04:37Z
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
S4c.end end_utc=2026-10-04T11:04:37Z
S4c.end date exit=0
S4c final exit=0
```

stderr:

```text
(empty)
```

### S4d — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s04d.sh`
* standard input: the resource with `<RUN>` substituted, 8772 bytes, SHA-256 `181ca29818259bafa9909887a2826da0c6de1d22906982781601472164650071`; then closed
* invoking status: `0`
* stdout: 4742 bytes, SHA-256 `3ef30072b5c684ed0eb6a2dcd47a4b149551608053c9030d7f84b6eb43ea6203`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S4d.trap exit=0
S4d.start start_utc=2026-10-04T11:04:38Z
S4d.start date exit=0
2775 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
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
f704c0f4f0ddbe9de92da9812dde6929f681ba778263746a603bde8b4b3563d6 16769 infra/rp11-launch/toolchain.lock OK
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f 381913 infra/rp11-launch/build-root.manifest OK
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625 328 infra/rp11-launch/expected.sha256 OK
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a 5305 infra/rp11-launch/verify/fixtures/cc1.v.baseline OK
b9f03a4791448c029b9a1eccc50416818893294357fa9f6182f85610ed14817a 377250 docs/review/phase-5-0-evidence-harness-review-manifest.json OK
2ac6e5e7721bf73347ffcc73281152f6cbec40fd2ff7167ff554ad9b2b11c64f 178810 docs/review/phase-5-0-evidence-harness-concrete-plan.md OK
87e318cdd77f1fae0a354f707d9fe32d163ba48b708bb455c670f6d4d333cfd1 3254 infra/rp11-launch/build.sh OK
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe 6314 infra/rp11-launch/launch.c OK
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b 2187 infra/rp11-launch/select.h OK
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139 857 infra/rp11-launch/start.s OK
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326 2321 infra/rp11-launch/rp11-launch.ld OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 21742 infra/rp11-launch/rp11-launch.x86_64.listing OK
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300 15106 infra/rp11-launch/buildroot/provision.py OK
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a 14521 infra/rp11-launch/buildroot/enter.py OK
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72 6021 infra/rp11-launch/verify/cc1check.py OK
167d16ae0b1cf6e82a5099b5e5b5c6b571b1f0273f8bdde7b79c55b9af2fceed 20364 infra/rp11-launch/verify/ic1check.py OK
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
0d4ece459dbffac790e3a1f7d61e0c83efe270825e0d874cded48e759f626a08 16942 tools/phase_5_0_evidence/rp11_launch.py OK
09983ff782eef3be420994f165e3168eee9682f6da8481e0427a31a481007dd7 75172 tools/phase_5_0_evidence/review_manifest.py OK
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S4d.4 hashlib-and-tree-check exit=0
S4d block exit=0
S4d.end end_utc=2026-10-04T11:04:38Z
S4d.end date exit=0
S4d final exit=0
```

stderr:

```text
(empty)
```

### S5 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s05.sh`
* standard input: the resource with `<RUN>` substituted, 3583 bytes, SHA-256 `6055f91cef895539db68d76a6cb493f5ad81bde610b26a9e84833f70b8d05b28`; then closed
* invoking status: `0`
* stdout: 6994 bytes, SHA-256 `28e6c461341b74f71575b46630ce6a09d4c987e09af918a61a49453bbaf033b1`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S5.trap exit=0
S5.start start_utc=2026-10-04T11:04:38Z
S5.start date exit=0
S5.1 cd exit=0
S5.2 resolve exit=0
S5.3 lock-package-lines exit=0
S5.4 resolve-equals-lock exit=0
S5.5 install exit=0
b766d8381fadc5e22249ba34632798dab333f9d896108092ce0f2d220b1b0537 base-files_14ubuntu6_amd64.deb OK
226c75127e46de2bbd8a329ac7e55781ede395ab8a9be0f269250b24c81b9c36 base-passwd_3.6.8_amd64.deb OK
3c846f001d87b16e5038a3919ca975276808a2db17459308a9d0f965c1cddac5 binutils-common_2.46-3ubuntu2_amd64.deb OK
91fa094c31783f7ccf0f0df8ed06447655c40476ba61fc95dbd245a313f8171e binutils-x86-64-linux-gnu_2.46-3ubuntu2_amd64.deb OK
d14fc7bf644b495083f77c99ff168f1a2215c8b3b7ad5202e0345dc1092002b0 binutils_2.46-3ubuntu2_amd64.deb OK
862be75c7dd5d92815f2b80149bbcf819d11d21b1dba734f62b545bc5acb0eb7 coreutils-from-gnu_0.0.0~ubuntu25_all.deb OK
1649aa71c45b047feda5b9ca303c94799bdba5befa5c9de9735cbfc59c3ef93f cpp-15-x86-64-linux-gnu_15.2.0-16ubuntu1_amd64.deb OK
baacc9086e17c8cadc3603365e660f907bca483de4446e56e6f1bc25da4c02be cpp-15_15.2.0-16ubuntu1_amd64.deb OK
563091a9b615a5a59951c2cc4478163d099df366a051113e8ce5bb2baab7f0c8 dash_0.5.12-12ubuntu3_amd64.deb OK
eb155f0a9531b5f3b1c06e0e415c4cd7e01777e7714cf51ac094fa6afa01638f debianutils_5.23.2build1_amd64.deb OK
546d6b0c2b2f5c61494ee5d11aa1b49476213af27a66edd9e05bb3ef00940557 findutils_4.10.0-3build2_amd64.deb OK
5a302d705d562fb7e150415b00651c00fed58b633faadff0b332eac1b73fadb3 gcc-15-base_15.2.0-16ubuntu1_amd64.deb OK
df0e5375c9e981b18e396c2e9ec1e359f226576a9b94a311bf07603f3ca6023a gcc-15-x86-64-linux-gnu_15.2.0-16ubuntu1_amd64.deb OK
28da225c111d3ce9d230209cca24db46ec645f631f593f188bef718d8a1e4711 gcc-15_15.2.0-16ubuntu1_amd64.deb OK
281b3188840a7abdca85a02eb2609b0efad852e8994b3804a0e4227ec4ec3f90 gcc-16-base_16-20260322-1ubuntu1_amd64.deb OK
6b5b60a5c372b6e9d1dcfa1507317aae59bf809d4f4d6d363d3ef0a58a189137 gnu-coreutils_9.7-3ubuntu2_amd64.deb OK
77f8d49c031182bbd6c4fe4ec9ad49edb5d4607f2dac795fc6932dce0e8f541e libacl1_2.3.2-2_amd64.deb OK
d59b3a851c0b58759e9f940fa407f68a6ef46401381e5389c74e5ded5419262d libasan8_16-20260322-1ubuntu1_amd64.deb OK
82fa61135e7154d7958feaa91ec1808a688eb1e0e06822ab35e99e2480feb148 libatomic1_16-20260322-1ubuntu1_amd64.deb OK
195ca7b0ca6c91c4b4b9e17baf98b98143e3a14a0571f1613f04b318b9799510 libattr1_2.5.2-4_amd64.deb OK
1376a5e49c8dc2ba938fadc15fce40dd01c7fbf1adf2d506a2a7cf7148e347c8 libbinutils_2.46-3ubuntu2_amd64.deb OK
c34230e6892fa95e498e51640f7131946120b83eb672f586e341fa53bf504359 libc-bin_2.43-2ubuntu2_amd64.deb OK
85ffc97dcc6c63c80693b07a984128b9e267992482f12e1c0dd87c65f014c769 libc-dev-bin_2.43-2ubuntu2_amd64.deb OK
eb5ba6fd4ec1a68801e757f4492c6c6b30119ff277ac9d99629a011559c963f0 libc-gconv-modules-extra_2.43-2ubuntu2_amd64.deb OK
6c8def1cafec89468fef8bd0d7a4eb66192a7850bf17c9decf7bca8fcf3dd5fa libc6-dev_2.43-2ubuntu2_amd64.deb OK
c13775dc0c984403f3fcad229d14507a9f387763bd07ace1e5f93897ee6b8434 libc6_2.43-2ubuntu2_amd64.deb OK
484ac5fd30a19bfade8db336fe70f3c046beccd1c9a9ac327fcd89d29dd5a125 libcc1-0_16-20260322-1ubuntu1_amd64.deb OK
57ab343c3dd28ce7101dc4e23de4e9d5bd3e58c6cb0ecd5ba0c42a877fc8868a libcrypt1_4.5.1-1_amd64.deb OK
5ca038ae110ddf65e190b9fe88822592abd45cecba5001f3e4ce7692ca1f31be libctf-nobfd0_2.46-3ubuntu2_amd64.deb OK
34b1757ce619720541c7e1e8d8f3aa506cb327731374e284ffb6ec872a2c566f libctf0_2.46-3ubuntu2_amd64.deb OK
21f699abaaa7624b0206573f69bf4f7a902d92863f2c9dfba497662c5713456b libdebconfclient0_0.280ubuntu1_amd64.deb OK
32fa5bde1891f46fd4f422e466c863fb78e834b634e1aa08211c8eea68870af5 libgcc-15-dev_15.2.0-16ubuntu1_amd64.deb OK
2fb4d81c14fdf34251639ae82f5181f9f98480ea16125d535571ac1be9db3065 libgcc-s1_16-20260322-1ubuntu1_amd64.deb OK
a9bbe9d4a4bcd5875bbd0f53e67c379bc881d1c1a80522d51dfb4b107cc31819 libgmp10_6.3.0+dfsg-5ubuntu2_amd64.deb OK
add19738c63794d2aa9ac529d3b8aebe2e88980faecb6c1c59f07aefd6c3c314 libgomp1_16-20260322-1ubuntu1_amd64.deb OK
6b066ab912300b2c6a965a9a8045da45c237a52b76c2c11d8f2ceaf7aabfacbb libgprofng0_2.46-3ubuntu2_amd64.deb OK
6bd25c936289463c6472290d3b4377edf8dd4f5e3a07f356fb0adf2de04a8055 libhwasan0_16-20260322-1ubuntu1_amd64.deb OK
02ea5de2ab6ddba978606ad58647bf6371ea68c0ed63aa5d6d0d3b8c1fe77ea3 libisl23_0.27-1build1_amd64.deb OK
ef841c269b5e9f324e38b1069f712a13c29237051f037847d1de79441dc3a9a2 libitm1_16-20260322-1ubuntu1_amd64.deb OK
1dc986ac3cf112384919d1a339a952e8a86bede9890a4489c016fdc266a036ca libjansson4_2.14-2build4_amd64.deb OK
c90895d3b6cd164fcb54def68c7dff74419f869c837fa607e3f54c1a0e742263 liblsan0_16-20260322-1ubuntu1_amd64.deb OK
38ad8500817a9159db210fecfb8c50fa82d7a8829730fcdf8ae60e3523676d41 liblzma5_5.8.3-1_amd64.deb OK
a95c75b486f26fe8b140a632fd9e2883b7e2efc21f7586e155d27d2d2ff0ddc0 libmpc3_1.3.1-3_amd64.deb OK
74defa71b7f81d66b103afccfce750ad356976696b40c96c846ddc956fcfe937 libmpfr6_4.2.2-3_amd64.deb OK
3e116766f1a7b149994d4745556023d993d26401223d1595520a991d4ba737fb libpcre2-8-0_10.46-1build1_amd64.deb OK
420e777fef436f397a85ddedde53fbb44f92c7ca8e87d581f9d86573859e1aa4 libquadmath0_16-20260322-1ubuntu1_amd64.deb OK
3ce3aea44b2ec00780c48b1b8e1f7e672166ec3ccac14b0eae8890e55983061e libselinux1_3.9-4build1_amd64.deb OK
05541ea1edb19e54bea297a21a9c33d0b99ca2cfe2e86d4a67335e6640667cfc libsframe3_2.46-3ubuntu2_amd64.deb OK
fe78b8124fb6c8c0d7efc8f2bd8d5e0d3f217351f520a3b4652ee0afe24143c2 libssl3t64_3.5.5-1ubuntu3_amd64.deb OK
a32b9ad585e39bdc7bd15d1eae6293461e6d466859a1dd2f7862d1e40f89b9d8 libstdc++6_16-20260322-1ubuntu1_amd64.deb OK
a93b416fd58067a14061763bfc9a23d18b0d4e0914b9a678ff7795e02f71d532 libsystemd0_259.5-0ubuntu3_amd64.deb OK
42705a701a98d84c203c6f96f08c6fd6a29a1ef978683e1ffbf0e27535b20ddb libtinfo6_6.6+20251231-1_amd64.deb OK
95b7a9b63096840cb960562d190a802a541055366eb4bc756c763d7de6e174d8 libtsan2_16-20260322-1ubuntu1_amd64.deb OK
cde09806b1b60d0ab8ab96033177cb21a0290333a946f25572de8f72b4403695 libubsan1_16-20260322-1ubuntu1_amd64.deb OK
7a9978fadf0940f45500ced0fba219cb5954f322a31068b7b32ad04f3ddc5c3f libunwind8_1.8.3-0ubuntu1_amd64.deb OK
34365d611ccf1f717f90a92fbe52ed96ae1829ab9be363c68a83563322797f8f libzstd1_1.5.7+dfsg-3_amd64.deb OK
14bf36d574df2cacf2e50fa8c1f28b4b6b574b63e9561924cc942e4c9186e57e linux-libc-dev_7.0.0-14.14_amd64.deb OK
9b071ec8637a7d87e152eee7952df8f3374e432bafecd3bcc30948feb3acb3e9 mawk_1.3.4.20260129-1_amd64.deb OK
05c9ab6be49c5177b366b21fc1b96e042d69e2c119de898d539e55a3a778f8f7 openssl-provider-legacy_3.5.5-1ubuntu3_amd64.deb OK
d7102b9d3fd35fd7a66d94ba0765a9c8e87b2b80e3633ef4af401dd0c952bafd rpcsvc-proto_1.4.3-1build1_amd64.deb OK
aa530bb652e46beaf92d5c916403182a5ac6b2ba79a94f18e5b9da45d1799ee5 strace_6.19+ds-0ubuntu5_amd64.deb OK
c45bbbf9c87457d90b8ba38720c5f01b9388c380d40f303c26f5c4953932da26 zlib1g_1.3.dfsg+really1.3.1-1ubuntu3_amd64.deb OK
cache_entries 62 lock_packages 62 unexpected 0 missing 0
S5.6 cache-accounting exit=0
S5.7 ldconfig exit=0
755 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
S5.8 root-stat exit=0
S5 block exit=0
S5.end end_utc=2026-10-04T11:05:16Z
S5.end date exit=0
S5 final exit=0
```

stderr:

```text
(empty)
```

### S6-S7 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s06-s07.sh`
* standard input: the resource with `<RUN>` substituted, 3705 bytes, SHA-256 `a89474a088895cac9a410fcf90ce6ca6309b27b20f564616bef038088f43f464`; then closed
* invoking status: `0`
* stdout: 1215 bytes, SHA-256 `be4940bdf356dfdeb733f37476a97f8c76abbdb04452221cefb888b03fd8de2f`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S6-S7.trap exit=0
S6-S7.start start_utc=2026-10-04T11:05:17Z
S6-S7.start date exit=0
S6.1 cd exit=0
S6.2 enter-build exit=0
r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal
exit 0
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  rp11-launch
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d  rp11-launch.map
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  rp11-launch.x86_64.listing
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706  launch.s
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a  cc1.v
S6.3 display exit=0
S6.4 gate-line-present exit=0
S6.5 r2-exit-line-present exit=0
S7.1 manifest-cmp exit=0
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/regenerated.manifest
S7.2 manifest-sha256 exit=0
ld_so_preload=absent
S7.3 ld-so-preload-absent exit=0
/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root/tmp entries=none
/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root/var/tmp entries=none
S7.4 root-tmp-empty exit=0
S6-S7 block exit=0
S6-S7.end end_utc=2026-10-04T11:05:20Z
S6-S7.end date exit=0
S6-S7 final exit=0
```

stderr:

```text
(empty)
```

### S8 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s08.sh`
* standard input: the resource with `<RUN>` substituted, 2600 bytes, SHA-256 `b727928a648f73c02e1c579d81ef6054bb565d11d2e5eec3a8c14a825a8dcb14`; then closed
* invoking status: `0`
* stdout: 794 bytes, SHA-256 `6e3704b58cbe0d0c53e1dc2c76c3be77030e0c977045735698a78305d1bf2814`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S8.trap exit=0
S8.start start_utc=2026-10-04T11:05:21Z
S8.start date exit=0
S8.1 cd exit=0
rp11-launch: OK
rp11-launch.x86_64.listing: OK
rp11-launch.map: OK
launch.s: OK
S8.2 expected-sha256-check exit=0
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572 rp11-launch OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 rp11-launch.x86_64.listing OK
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d rp11-launch.map OK
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706 launch.s OK
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a 5305 cc1.v diagnostic, judged in step 9
S8.3 independent-output-check exit=0
S8.4 listing-cmp exit=0
S8 block exit=0
S8.end end_utc=2026-10-04T11:05:21Z
S8.end date exit=0
S8 final exit=0
```

stderr:

```text
(empty)
```

### S9 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s09.sh`
* standard input: the resource with `<RUN>` substituted, 1812 bytes, SHA-256 `b4d9ddfcbf568fa4e8bc87985842ff065dff5a95589560458c7f57086d21e62a`; then closed
* invoking status: `0`
* stdout: 475 bytes, SHA-256 `01d482a5c71e70ccd9ec5313c66ea985b02bb259f6e683f463787095ed24ea77`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S9.trap exit=0
S9.start start_utc=2026-10-04T11:05:22Z
S9.start date exit=0
5305
S9.1 cc1v-length exit=0
S9.2 cd exit=0
S9.3 cc1check exit=0
baseline_sha256: e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a
actual_sha256:   e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a
is_identical:    True
total_diffs:     0
verdict:         PASS
S9.4 display exit=0
S9 block exit=0
S9.end end_utc=2026-10-04T11:05:22Z
S9.end date exit=0
S9 final exit=0
```

stderr:

```text
(empty)
```

### S10 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s10.sh`
* standard input: the resource with `<RUN>` substituted, 2253 bytes, SHA-256 `e2109d1d672a017557215500d19e4c527e8e1fdc3032acba398d5370b02d6951`; then closed
* invoking status: `0`
* stdout: 490 bytes, SHA-256 `d3ba10f1df8fc1ba2e37967ba31c089eeba80cdb08111661c812e56b82608f4b`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S10.trap exit=0
S10.start start_utc=2026-10-04T11:05:22Z
S10.start date exit=0
S10.1 cd exit=0
S10.2 pytest exit=0
............                                                             [100%]
- generated xml file: /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/pytest.junit.xml -
12 passed in 11.78s
S10.3 display exit=0
tests=12 failures=0 errors=0 skipped=0
S10.4 pytest-counts exit=0
S10 block exit=0
S10.end end_utc=2026-10-04T11:05:37Z
S10.end date exit=0
S10 final exit=0
```

stderr:

```text
(empty)
```

### S11 — step block, oracle-test

* argv: `ssh oracle-test /bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s11.sh`
* standard input: the resource with `<RUN>` substituted, 10610 bytes, SHA-256 `a99719dbbc838f84c311786a7f35f8de8eb99ec6979f6c36c9e39092e4215bbb`; then closed
* invoking status: `0`
* stdout: 8978 bytes, SHA-256 `551717a28e5486f55740866645b4696d002c748e5e9e4d073a0cd1ffa684d4a5`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S11.trap exit=0
S11.start start_utc=2026-10-04T11:05:39Z
S11.start date exit=0
S11.1 cd exit=0
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
S11.2 sha256sum-check exit=0
f704c0f4f0ddbe9de92da9812dde6929f681ba778263746a603bde8b4b3563d6 16769 infra/rp11-launch/toolchain.lock OK
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f 381913 infra/rp11-launch/build-root.manifest OK
6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625 328 infra/rp11-launch/expected.sha256 OK
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a 5305 infra/rp11-launch/verify/fixtures/cc1.v.baseline OK
b9f03a4791448c029b9a1eccc50416818893294357fa9f6182f85610ed14817a 377250 docs/review/phase-5-0-evidence-harness-review-manifest.json OK
2ac6e5e7721bf73347ffcc73281152f6cbec40fd2ff7167ff554ad9b2b11c64f 178810 docs/review/phase-5-0-evidence-harness-concrete-plan.md OK
87e318cdd77f1fae0a354f707d9fe32d163ba48b708bb455c670f6d4d333cfd1 3254 infra/rp11-launch/build.sh OK
6810bcd0dd9567c9ee49a2b7f0dd7bfe2d69148eaba3d3d5caea3aa0983fa6fe 6314 infra/rp11-launch/launch.c OK
34b56cfc1adb4f14f2e09c740e5e25915194778ebf73c74c1d24502121425c4b 2187 infra/rp11-launch/select.h OK
ca631f087ad09c16d5e45d2088c7be81593f2fb8efb805b66ed65aff0a1a5139 857 infra/rp11-launch/start.s OK
ed5519ef1994d4b32eb92f754f008a5aeb88e08d5194ede92491ddda1ac95326 2321 infra/rp11-launch/rp11-launch.ld OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 21742 infra/rp11-launch/rp11-launch.x86_64.listing OK
40496661f5d7e251b557b6d4f9f13a1d76e59619a608c39e576424352d0c0300 15106 infra/rp11-launch/buildroot/provision.py OK
cf467c17df4135cc5f431a3ffe5c86afef930df3b880ae4425ad6209e397807a 14521 infra/rp11-launch/buildroot/enter.py OK
16b784622d46150dee768e399d3e89ddb8a996111af5264928761a5bc08a4b72 6021 infra/rp11-launch/verify/cc1check.py OK
167d16ae0b1cf6e82a5099b5e5b5c6b571b1f0273f8bdde7b79c55b9af2fceed 20364 infra/rp11-launch/verify/ic1check.py OK
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
0d4ece459dbffac790e3a1f7d61e0c83efe270825e0d874cded48e759f626a08 16942 tools/phase_5_0_evidence/rp11_launch.py OK
09983ff782eef3be420994f165e3168eee9682f6da8481e0427a31a481007dd7 75172 tools/phase_5_0_evidence/review_manifest.py OK
rows 28 mismatches 0
launcher_tree files 22 dirs 5
S11.3 hashlib-and-tree-check exit=0
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/build.stderr
586fdfd646ebab0de102f3033056803f93bdd36d0827fdf61b0ba15123543084  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/build.stdout
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/cc1check.err
4171ff346c7a0a863fd502ec8e132eb1c1e00b3ce1a278be8316d2fed330d558  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/cc1check.out
23a4e88bf07608fda8a5ff3f187297bfe0eb03b0b5a6ac20d79cd3b8ea571da7  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/lock-packages.txt
eab7e76ed59d0f044f6f19abf70c848497963dfb23a577130e940cb70795c19c  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/pytest.junit.xml
09865af4cecfcfe2bb8bc57aa6afd1459ca0c856072121809bd715bdc6eea66f  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/pytest.out
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/regenerated.manifest
23a4e88bf07608fda8a5ff3f187297bfe0eb03b0b5a6ac20d79cd3b8ea571da7  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/resolve.out
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/cc1.v
bfe7b3e7c0132f7f316d6704aecc087e453334c6bb1d65579c8ba252eb8c1f0c  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/launch.o
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/launch.s
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch.map
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch.x86_64.listing
154771200e4c7515d583f84911a9e124acb94e9dacca56f477935690b08618a5  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/start.o
S11.4 evidence-sha256 exit=0
2775 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-index
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-cache
755 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence
700 ubuntu:ubuntu /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-pytest
S11.5 stat exit=0
98516	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout
140	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-index
71612	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-cache
252612	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root
748	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work
420	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence
5288	/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-pytest
S11.6 du exit=0
2026-10-04T11:05:40Z
S11.7 date exit=0
Linux 7.0.0-31-generic #31-Ubuntu SMP PREEMPT_DYNAMIC Sat Aug  1 04:26:38 UTC 2026 x86_64
S11.8 uname exit=0
vendor_id	: AuthenticAMD
cpu family	: 23
model		: 1
model name	: AMD EPYC 7551 32-Core Processor
stepping	: 2
microcode	: 0x8001279
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm rep_good nopl xtopology cpuid extd_apicid tsc_known_freq pni pclmulqdq ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm cmp_legacy svm cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw topoext perfctr_core ssbd ibpb vmmcall fsgsbase tsc_adjust bmi1 avx2 smep bmi2 rdseed adx smap clflushopt sha_ni xsaveopt xsavec xgetbv1 clzero xsaveerptr virt_ssbd arat npt nrip_save vgif overflow_recov succor arch_capabilities
S11.9 cpuinfo-first-processor exit=0
bubblewrap 0.11.1
S11.10 bwrap-version exit=0
a85b0ff8664c52ab923e0daf7e20cbc394272cd3831cc492ab144105d8091361  /usr/bin/bwrap
S11.11 bwrap-sha256 exit=0
S11 block exit=0
S11.end end_utc=2026-10-04T11:05:40Z
S11.end date exit=0
S11 final exit=0
```

stderr:

```text
(empty)
```

### S12.start — timestamp block, repository host

* argv: `/bin/bash --noprofile --norc -s`
* resource: `tools/r5_runner/blocks/s12-start.sh`
* standard input: the resource with `<RUN>` substituted, 240 bytes, SHA-256 `bf495fd370a236b04295e955ce083e63fd4ead1fa8e2fabe4ca788a21f1f2aa3`; then closed
* invoking status: `0`
* stdout: 86 bytes, SHA-256 `1eae07332e00cbfe92b55ac3ab0ad372d5380e3d20afeb12f6999504debf5501`, valid UTF-8
* stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, valid UTF-8

stdout:

```text
S12.start start_utc=2026-10-04T11:05:40Z
S12.start date exit=0
S12.start block exit=0
```

stderr:

```text
(empty)
```


## 7. Synchronization, download source, resolve and cache accounting

* synchronization: invoking status 0; summary lines in §6 (`S4b.sync`).
* download source: `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z/`, fixed by the pinned `provision.py` and the `--snapshot` argument of S5.2.
* resolve and cache accounting (S5.2–S5.6):

```text
[S5]
S5.2 resolve exit=0
S5.4 resolve-equals-lock exit=0
S5.5 install exit=0
cache_entries 62 lock_packages 62 unexpected 0 missing 0
S5.6 cache-accounting exit=0
S5.7 ldconfig exit=0
S5.8 root-stat exit=0
```


## 8. Same-invocation R-1/R-2 evidence

`build.stdout` and `build.stderr` are displayed verbatim by S6.3 in the steps-6/7 transcript (§6). Result lines:

```text
[S6-S7]
S6.2 enter-build exit=0
r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal
S6.3 display exit=0
S6.4 gate-line-present exit=0
S6.5 r2-exit-line-present exit=0
S7.1 manifest-cmp exit=0
f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f  /var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-evidence/regenerated.manifest
S7.2 manifest-sha256 exit=0
ld_so_preload=absent
S7.3 ld-so-preload-absent exit=0
/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root/tmp entries=none
/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-root/var/tmp entries=none
S7.4 root-tmp-empty exit=0
```


## 9. Normative output digests

```text
[S8]
rp11-launch: OK
rp11-launch.x86_64.listing: OK
rp11-launch.map: OK
launch.s: OK
S8.2 expected-sha256-check exit=0
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572 rp11-launch OK
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188 rp11-launch.x86_64.listing OK
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d rp11-launch.map OK
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706 launch.s OK
e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a 5305 cc1.v diagnostic, judged in step 9
S8.3 independent-output-check exit=0
S8.4 listing-cmp exit=0
```


## 10. Diagnostic `cc1.v` comparison

The complete `cc1check.py` output is displayed by S9.4 in the step-9 transcript (§6). Result lines:

```text
[S9.1] cc1.v length: 5305
[S9]
S9.1 cc1v-length exit=0
S9.3 cc1check exit=0
baseline_sha256: e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a
actual_sha256:   e99cee65a228339e304d4e578643de409961539a8240230d4e41bb1baf6bb13a
is_identical:    True
total_diffs:     0
verdict:         PASS
S9.4 display exit=0
```


## 11. Corroborating tests

The complete pytest output, every warning and the summary line are displayed by S10.3 in the step-10 transcript (§6). The runner does not classify warnings: under §6 step 10 the two known pytest-asyncio configuration warnings are expected and every other warning is for the reviewer.

```text
[S10]
S10.2 pytest exit=0
S10.3 display exit=0
tests=12 failures=0 errors=0 skipped=0
S10.4 pytest-counts exit=0
```


## 12. Stopped, invalid or unexplained conditions

None.


## 13. Retained evidence and cleanup state

* the handback `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md` is the evidence of record (R5 §10.1).
* step 4a ran: directories were created under `oracle-test:/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-*`, and `oracle-test`'s `/var/tmp` changed.
* the synchronization ran: the repository working tree was sent to `oracle-test:/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-checkout/`.
* S11.4 evidence digests: in the step-11 transcript (§6).
* cleanup state: nothing was deleted. Everything stays in place pending review and Peter Duscha's direction. The host is not claimed to be in its pre-run state.


## 14. Verdict

**PASS** (precedence: HARD STOP over INVALID RUN over PASS, §8). The verdict of record is HARD STOP if this handback does not end with the exact closing record of §6 step 12.

| §8.1 condition | Answer |
|---|---|
| 1. independence attestation | complete (§1, written before step 1) |
| 2. every invocation ran in order, once, exit 0, with its pass output | yes |
| 3. every timed scope has its start and end values | yes; step-12 end, whole-run end and closing record: in closing record |
| 4. HA-1 or HA-2 qualified; start and end observations agree | yes |
| 5. same-invocation R-1/R-2 gate and manifest equality | yes |
| 6. four normative outputs and listing | yes |
| 7. `cc1.v` byte-identical (`cc1check.py` PASS) | yes |
| 8. 12 tests, 0 failures, 0 errors, 0 skipped | yes |
| 9. no unexplained difference remains | no mechanical difference found; pytest warnings (§11) are for reviewer determination |


## 15. Operational and governance statements

* RP-11 remains unwired and unmet.
* `plan.is_executable=False`.
* PO-9 and PO-14 remain open.
* Package 5.0 is not ready.
* No installation, operational, harness `--execute`, privileged, commit or push authority was exercised.


## 16. Stop

The runner hands this file to the S12.end block, which appends the closing record. Nothing edits this file afterwards. The run stops pending Codex's independent review and Peter Duscha's decision.

## Closing record (written by the S12.end block)

~~~text
S12.end.3 open-record exit=0
S12.end end_utc=2026-10-04T11:05:40Z
RUN.end end_utc=2026-10-04T11:05:40Z
S12.end.4 date exit=0
~~~
