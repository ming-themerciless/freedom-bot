r5_end() {
  block_status=$?
  date -u '+S11.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S11.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S11 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S11.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S11.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S11.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S11.1 cd exit=%s\n' "$status"
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
  printf 'S11.2 sha256sum-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import hashlib,os,sys
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
  printf 'S11.3 hashlib-and-tree-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /var/tmp/<RUN>-evidence/* /var/tmp/<RUN>-work/co-r2/build-out/*
  status=$?
  printf 'S11.4 evidence-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence /var/tmp/<RUN>-pytest
  status=$?
  printf 'S11.5 stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  du -s /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence /var/tmp/<RUN>-pytest
  status=$?
  printf 'S11.6 du exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u +%Y-%m-%dT%H:%M:%SZ
  status=$?
  printf 'S11.7 date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  uname -srvm
  status=$?
  printf 'S11.8 uname exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  awk '/^processor/{n++} n==1 && /^(vendor_id|cpu family|model|model name|stepping|microcode|flags)[[:space:]]*:/' /proc/cpuinfo
  status=$?
  printf 'S11.9 cpuinfo-first-processor exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /usr/bin/bwrap --version
  status=$?
  printf 'S11.10 bwrap-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /usr/bin/bwrap
  status=$?
  printf 'S11.11 bwrap-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S11 block exit=0\n'
  exit 0
}
r5_block </dev/null
