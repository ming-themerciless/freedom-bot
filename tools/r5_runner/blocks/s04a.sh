r5_end() {
  block_status=$?
  date -u '+S4a.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S4a.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S4a final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S4a.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S4a.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4a.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  mkdir -m 0700 /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence
  status=$?
  printf 'S4a.1 mkdir exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -c '%a %U:%G %n' /var/tmp/<RUN>-checkout /var/tmp/<RUN>-index /var/tmp/<RUN>-cache /var/tmp/<RUN>-root /var/tmp/<RUN>-work /var/tmp/<RUN>-evidence
  status=$?
  printf 'S4a.2 stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4a block exit=0\n'
  exit 0
}
r5_block </dev/null
