# Fresh R-5 successor R3 independent static-launcher rebuild handback

Execution work ID: `C-P5.0-R5-RP11-FRESH-R5-R3`
Run identifier: `p5-r5-fresh-20261003T191400Z-9c3f71e2`
Executor: Gemini
Controlling assignment: [`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md)
Controlling acceptance and activation: [`docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md`](project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md)

---

## 1. Executor identity and §2 independence attestation

I, Gemini, execute this run under assignment R3 and attest before any host action:

1. I did not implement, co-author or remediate I-7 or I-7-R1;
2. I have not reused, and will not use, any earlier build root, package cache, checkout, work directory, build output, trace, evidence or scratch directory;
3. I have read the controlling assignment (`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md`) and the acceptance record that names me (`docs/review/project-review-2026-10-03-p5-r5-rp11-fresh-assignment-r3-acceptance-and-gemini-activation.md`); and
4. This run is wholly fresh. I have not read, reused, copied, compared against or inherited any resource or artifact from Gemini's earlier R-5 run (`/tmp/r5-*-gemini-f8a1` on `oracle-test`), its B1 run (`/tmp/p5-b1-repro-20261001t190454z-*` on the repository host) or its stopped fresh R-5 run `p5-r5-fresh-20261002T184800Z-7e9b2d41` (formerly `/tmp/p5-r5-fresh-20261002T184800Z-7e9b2d41-*` on `oracle-test`, deleted by Codex on 2026-10-03; any surviving copy is equally forbidden). That includes roots, caches, checkouts, outputs, `cc1.v` bytes, manifests, traces, logs and pytest temporary directories.

---

## 2. Timestamps

| Scope | Producing label | Host | Start UTC | End UTC | Status |
|---|---|---|---|---|---|
| whole run | `RUN.start` / `RUN.end` | repository host | absent | in closing record | absent |
| step 1 | `S1.start` / `S1.end` | repository host | absent | absent | exit=0 (shell exit; no stdout/stderr) |
| step 2 | `S2.start` / `S2.end` | `oracle-test` | not run | not run | not run |
| step 3 | `S3.start` / `S3.end` | `oracle-test` | not run | not run | not run |
| step 4a | `S4a.start` / `S4a.end` | `oracle-test` | not run | not run | not run |
| step 4b | `S4b.start` / `S4b.end` | repository host | not run | not run | not run |
| step 4c | `S4c.start` / `S4c.end` | repository host | not run | not run | not run |
| step 4d | `S4d.start` / `S4d.end` | `oracle-test` | not run | not run | not run |
| step 5 | `S5.start` / `S5.end` | `oracle-test` | not run | not run | not run |
| steps 6/7 combined | `S6-S7.start` / `S6-S7.end` | `oracle-test` | not run | not run | not run |
| step 8 | `S8.start` / `S8.end` | `oracle-test` | not run | not run | not run |
| step 9 | `S9.start` / `S9.end` | `oracle-test` | not run | not run | not run |
| step 10 | `S10.start` / `S10.end` | `oracle-test` | not run | not run | not run |
| step 11 | `S11.start` / `S11.end` | `oracle-test` | not run | not run | not run |
| step 12 | `S12.start` / `S12.end` | repository host | absent | in closing record | absent |

---

## 3. Repository state

Step 1 block failed to execute its internal commands on the repository host environment.
The invoking shell exited with code 0 without executing `r5_block` or emitting output to stdout/stderr.
Consequently, `git rev-parse HEAD`, the S1.3 `git status --short --untracked-files=all` output, `git_status_lines`, `git_status_sha256`, S1.4 `repository_state`, S1.5 `sha256sum`, S1.6 `hashlib-and-tree-check`, S1.7 `lock-facts`, and S1.8 in-memory review manifest were not reached.

---

## 4. Host-assumption variation (HA-1 … HA-5) and diagnostic context

Steps 2 and 3 on `oracle-test` were not reached due to the Step 1 HARD STOP. No remote host observations were made.

---

## 5. Created paths

### Repository host
- `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`: regular file, created for this handback.

### `oracle-test`
No paths were created on `oracle-test`.

---

## 6. Block execution and transcripts

### Step 1 block invocation

Invoked command:
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

Transcript:
The command was executed via background task `c31a5ee1-213a-4442-b6e9-ef53f43f2d31/task-19` starting at `2026-10-03T19:11:41Z`.
The task ran for ~53 minutes in a subshell/terminal without emitting any characters to stdout or stderr.
Upon receiving EOF (`\x04`), the process exited at `2026-10-03T20:05:23Z` with shell exit code 0.
Actual output:
```text
(empty)
```
Exit status: `0` (shell exit).

---

## 7. Synchronization command and cache accounting

Step 4b was not run. Step 5 was not run.

---

## 8. Same-invocation R-1/R-2 evidence

Steps 6 and 7 were not run.

---

## 9. Normative output digests

Step 8 was not run.

---

## 10. Diagnostic `cc1.v` comparison

Step 9 was not run.

---

## 11. Corroborating tests

Step 10 was not run.

---

## 12. Stopped conditions and first failure

First stop condition:
**Step 1 HARD STOP — missing evidence and missing required timestamps (§6.0, §8.3)**.
The Step 1 block process exited with code 0 without executing `r5_block` or emitting output to stdout/stderr. None of the required timestamps (`RUN.start`, `S1.start`, `S1.end`), intermediate exit markers (`S1.1` … `S1.9`, `S1 block exit=0`, `S1 final exit=0`), or repository checks were printed.
Under §8.3, a missing or malformed required timestamp or missing evidence is a HARD STOP.
Under §6 step 12, after a HARD STOP at any step, no later step runs, and the executor writes the handback and stops.

---

## 13. Retained evidence locations and cleanup state

- Handback file on repository host: `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r3-handback.md`.
- No outer-host directories were created on `oracle-test`.
- No changes were made to `oracle-test`.
- Cleanup state: host state preserved as-is pending maintainer review.

---

## 14. Verdict

**HARD STOP** (precedence: HARD STOP over INVALID RUN over PASS, §8).

### Evaluation of §8.1 conditions:
1. Executor independence attestation (§2): complete (Section 1).
2. Every block and synchronization command ran in order, once, each exiting 0 with stated pass output: **FAIL** (Step 1 emitted no output/checks).
3. Every timed scope of §6.0 has start and end values printed with status 0, and exact closing record: **FAIL** (Step 1 timestamps absent; in closing record).
4. HA-1 or HA-2 qualified under §4.2: **NOT REACHED** (Step 3 not run).
5. Same-invocation R-1/R-2 gate passed and manifest byte-equal: **NOT REACHED** (Steps 6/7 not run).
6. Normative outputs match expected.sha256 and listing byte-equal: **NOT REACHED** (Step 8 not run).
7. `cc1.v` byte-identical to baseline (`cc1check.py PASS`): **NOT REACHED** (Step 9 not run).
8. Corroborating tests report 12 tests, 0 failures, 0 errors, 0 skipped: **NOT REACHED** (Step 10 not run).
9. No unexplained difference remains: **FAIL** (Step 1 failed to execute script body).

---

## 15. Operational and governance statements

- RP-11 remains unwired and unmet.
- `plan.is_executable=False`.
- PO-9 and PO-14 remain open.
- Package 5.0 is not ready.
- No installation, operational, harness `--execute`, privileged, commit or push authority was exercised.

---

## 16. Stop condition and handback completion

Execution stopped immediately upon Step 1 HARD STOP.
Handback completed under §10 pending independent review by Codex and decision by Peter Duscha.

## Closing record (written by the S12.end block)

~~~text
S12.end.3 open-record exit=0
S12.end end_utc=2026-10-03T20:08:58Z
RUN.end end_utc=2026-10-03T20:08:58Z
S12.end.4 date exit=0
~~~
