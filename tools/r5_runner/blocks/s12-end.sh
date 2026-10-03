r5_close() {
  printf '\n## Closing record (written by the S12.end block)\n\n~~~text\n'
  status=$?
  printf 'S12.end.3 open-record exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then return "$status"; fi
  date -u '+S12.end end_utc=%Y-%m-%dT%H:%M:%SZ%nRUN.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S12.end.4 date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then return "$status"; fi
  printf '~~~\n'
  status=$?
  return "$status"
}
r5_block() {
  cd /opt/freedom-blades/platform
  status=$?
  printf 'S12.end.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  if [ -f 'docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md' ] && [ ! -L 'docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md' ]; then
    printf 'handback_body=present\n'
    status=0
  else
    printf 'handback_body=missing\n'
    status=33
  fi
  printf 'S12.end.2 handback-body-present exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  r5_close >> 'docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r4-handback.md'
  status=$?
  printf 'S12.end.5 closing-record exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S12.end block exit=0\n'
  exit 0
}
r5_block </dev/null
