r5_end() {
  block_status=$?
  date -u '+S5.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S5.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S5 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S5.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S5.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S5.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S5.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -B infra/rp11-launch/buildroot/provision.py resolve --snapshot 20261001T000000Z --suite resolute --cache /var/tmp/<RUN>-index > /var/tmp/<RUN>-evidence/resolve.out
  status=$?
  printf 'S5.2 resolve exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  grep '^package=' infra/rp11-launch/toolchain.lock > /var/tmp/<RUN>-evidence/lock-packages.txt
  status=$?
  printf 'S5.3 lock-package-lines exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cmp /var/tmp/<RUN>-evidence/resolve.out /var/tmp/<RUN>-evidence/lock-packages.txt
  status=$?
  printf 'S5.4 resolve-equals-lock exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -B infra/rp11-launch/buildroot/provision.py install --lock infra/rp11-launch/toolchain.lock --root /var/tmp/<RUN>-root --cache /var/tmp/<RUN>-cache
  status=$?
  printf 'S5.5 install exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import hashlib,os,sys
lock=[l.split() for l in open(sys.argv[1],encoding="utf-8") if l.startswith("package=")]
want={os.path.basename(f):s for _n,_v,s,f in lock}
have=sorted(os.listdir(sys.argv[2]))
bad=0
for n in have:
    p=os.path.join(sys.argv[2],n)
    d=hashlib.sha256(open(p,"rb").read()).hexdigest() if os.path.isfile(p) and not os.path.islink(p) else "not-a-regular-file"
    ok=want.get(n)==d
    bad+=not ok
    print(d,n,"OK" if ok else "UNEXPECTED")
missing=sorted(set(want)-set(have))
for n in missing:
    print("missing",n)
print("cache_entries",len(have),"lock_packages",len(want),"unexpected",bad,"missing",len(missing))
sys.exit(29 if (bad or missing or len(have)!=62 or len(want)!=62) else 0)' infra/rp11-launch/toolchain.lock /var/tmp/<RUN>-cache
  status=$?
  printf 'S5.6 cache-accounting exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -B infra/rp11-launch/buildroot/enter.py ldconfig --root /var/tmp/<RUN>-root
  status=$?
  printf 'S5.7 ldconfig exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-root
  status=$?
  printf 'S5.8 root-stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S5 block exit=0\n'
  exit 0
}
r5_block </dev/null
