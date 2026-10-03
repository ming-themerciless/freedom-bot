r5_end() {
  block_status=$?
  date -u '+S10.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S10.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S10 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S10.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S10.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S10.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cd /var/tmp/<RUN>-checkout
  status=$?
  printf 'S10.1 cd exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  env -u TEST_DATABASE_URL RP11_LAUNCH_BUILD_ROOT=/var/tmp/<RUN>-root PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -B -m pytest -q -rs -p no:cacheprovider --basetemp=/var/tmp/<RUN>-pytest --junitxml=/var/tmp/<RUN>-evidence/pytest.junit.xml tests/test_rp11_launch_toolchain.py > /var/tmp/<RUN>-evidence/pytest.out 2>&1
  pytest_status=$?
  printf 'S10.2 pytest exit=%s\n' "$pytest_status"
  cat /var/tmp/<RUN>-evidence/pytest.out
  display_status=$?
  printf 'S10.3 display exit=%s\n' "$display_status"
  if [ "$pytest_status" -ne 0 ]; then exit "$pytest_status"; fi
  if [ "$display_status" -ne 0 ]; then exit "$display_status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
suite=root if root.tag=="testsuite" else root.find("testsuite")
counts={k:int(suite.get(k,"-1")) for k in ("tests","failures","errors","skipped")}
print(" ".join(k+"="+str(v) for k,v in counts.items()))
sys.exit(0 if counts=={"tests":12,"failures":0,"errors":0,"skipped":0} else 32)' /var/tmp/<RUN>-evidence/pytest.junit.xml
  status=$?
  printf 'S10.4 pytest-counts exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S10 block exit=0\n'
  exit 0
}
r5_block </dev/null
