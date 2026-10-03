r5_end() {
  block_status=$?
  date -u '+S9.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S9.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S9 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S9.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S9.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S9.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%s' /var/tmp/<RUN>-work/co-r2/build-out/cc1.v
  status=$?
  printf 'S9.1 cc1v-length exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S9.2 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -B infra/rp11-launch/verify/cc1check.py infra/rp11-launch/verify/fixtures/cc1.v.baseline /var/tmp/<RUN>-work/co-r2/build-out/cc1.v > /var/tmp/<RUN>-evidence/cc1check.out 2> /var/tmp/<RUN>-evidence/cc1check.err
  check_status=$?
  printf 'S9.3 cc1check exit=%s\n' "$check_status"
  cat /var/tmp/<RUN>-evidence/cc1check.out /var/tmp/<RUN>-evidence/cc1check.err
  display_status=$?
  printf 'S9.4 display exit=%s\n' "$display_status"
  if [ "$check_status" -ne 0 ]; then exit "$check_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
  printf 'S9 block exit=0\n'
  exit 0
}
r5_block </dev/null
