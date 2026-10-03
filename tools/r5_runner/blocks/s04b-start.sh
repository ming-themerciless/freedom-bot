r5_block() {
  date -u '+S4b.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S4b.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S4b.start block exit=0\n'
  exit 0
}
r5_block </dev/null
