r5_end() {
  block_status=$?
  date -u '+S6-S7.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S6-S7.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S6-S7 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S6-S7.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S6-S7.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S6-S7.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S6.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -B infra/rp11-launch/buildroot/enter.py build --root /var/tmp/<RUN>-root --work /var/tmp/<RUN>-work --variant r2 --manifest-out /var/tmp/<RUN>-evidence/regenerated.manifest > /var/tmp/<RUN>-evidence/build.stdout 2> /var/tmp/<RUN>-evidence/build.stderr
  build_status=$?
  printf 'S6.2 enter-build exit=%s\n' "$build_status"
  cat /var/tmp/<RUN>-evidence/build.stdout /var/tmp/<RUN>-evidence/build.stderr
  display_status=$?
  printf 'S6.3 display exit=%s\n' "$display_status"
  if [ "$build_status" -ne 0 ]; then exit "$build_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
  grep -Fxq 'r1-manifest f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f equal' /var/tmp/<RUN>-evidence/build.stdout
  status=$?
  printf 'S6.4 gate-line-present exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  grep -Fxq 'exit 0' /var/tmp/<RUN>-evidence/build.stdout
  status=$?
  printf 'S6.5 r2-exit-line-present exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cmp /var/tmp/<RUN>-evidence/regenerated.manifest /var/tmp/<RUN>-checkout/infra/rp11-launch/build-root.manifest
  status=$?
  printf 'S7.1 manifest-cmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /var/tmp/<RUN>-evidence/regenerated.manifest
  status=$?
  printf 'S7.2 manifest-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  preload=/var/tmp/<RUN>-root/etc/ld.so.preload
  if [ -e "$preload" ] || [ -L "$preload" ]; then
    printf 'ld_so_preload=present\n'
    status=11
  else
    printf 'ld_so_preload=absent\n'
    status=0
  fi
  printf 'S7.3 ld-so-preload-absent exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import os,sys
nonempty=False
for d in sys.argv[1:]:
    if os.path.islink(d) or not os.path.isdir(d):
        print("missing_or_not_directory="+d)
        sys.exit(13)
    entries=sorted(os.listdir(d))
    print(d+" entries="+(",".join(entries) if entries else "none"))
    nonempty=nonempty or bool(entries)
sys.exit(12 if nonempty else 0)' /var/tmp/<RUN>-root/tmp /var/tmp/<RUN>-root/var/tmp
  status=$?
  printf 'S7.4 root-tmp-empty exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S6-S7 block exit=0\n'
  exit 0
}
r5_block </dev/null
