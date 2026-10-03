r5_block() {
  date -u '+S12.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S12.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S12.start block exit=0\n'
  exit 0
}
r5_block </dev/null
