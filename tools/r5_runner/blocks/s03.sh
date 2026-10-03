r5_end() {
  block_status=$?
  date -u '+S3.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S3.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S3 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S3.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S3.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S3.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import os,sys
release=os.uname().release
names=set()
for line in open("/proc/cpuinfo",encoding="utf-8",errors="replace"):
    key,sep,value=line.partition(":")
    if sep and key.strip()=="model name":
        names.add(value.strip())
print("HA-1 kernel_release="+release)
print("HA-2 model_names="+" | ".join(sorted(names)))
if len(names)!=1:
    print("HA-2 model name missing or not unique")
    sys.exit(21)
ha1=release!="6.8.0-139-generic"
ha2=names.isdisjoint({"AMD EPYC-Milan Processor","AMD EPYC-Milan"})
print("HA-1 qualifies="+("yes" if ha1 else "no"))
print("HA-2 qualifies="+("yes" if ha2 else "no"))
print("HA-3 qualifies=no (version-only differences do not qualify; section 4.2)")
sys.exit(0 if (ha1 or ha2) else 20)'
  status=$?
  printf 'S3.1 qualification exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S3 block exit=0\n'
  exit 0
}
r5_block </dev/null
