r5_block() {
  date -u '+S4b.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4b.end date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4b.end block exit=0\n'
  exit 0
}
r5_block </dev/null
