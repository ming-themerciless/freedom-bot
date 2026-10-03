r5_end() {
  block_status=$?
  date -u '+S8.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S8.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S8 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S8.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S8.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S8.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-work/co-r2/build-out
  status=$?
  printf 'S8.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum --strict -c /var/tmp/<RUN>-checkout/infra/rp11-launch/expected.sha256
  status=$?
  printf 'S8.2 expected-sha256-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import hashlib,sys
rows=[l.split("  ",1) for l in sys.stdin.read().splitlines()]
bad=0
for want,name in rows:
    got=hashlib.sha256(open(name,"rb").read()).hexdigest()
    ok=got==want
    bad+=not ok
    print(got,name,"OK" if ok else "MISMATCH")
c=open("cc1.v","rb").read()
print(hashlib.sha256(c).hexdigest(),len(c),"cc1.v diagnostic, judged in step 9")
if bad or len(rows)!=4:
    sys.exit(30)
out=open(sys.argv[1],encoding="utf-8",errors="replace").read().splitlines()
missing=[w+"  "+n for w,n in rows if w+"  "+n not in out]
for m in missing:
    print("missing_from_build_stdout",m)
sys.exit(31 if missing else 0)' /var/tmp/<RUN>-evidence/build.stdout <<'OUTPUTS'
04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572  rp11-launch
8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188  rp11-launch.x86_64.listing
5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d  rp11-launch.map
b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706  launch.s
OUTPUTS
  status=$?
  printf 'S8.3 independent-output-check exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cmp /var/tmp/<RUN>-work/co-r2/build-out/rp11-launch.x86_64.listing /var/tmp/<RUN>-checkout/infra/rp11-launch/rp11-launch.x86_64.listing
  status=$?
  printf 'S8.4 listing-cmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S8 block exit=0\n'
  exit 0
}
r5_block </dev/null
