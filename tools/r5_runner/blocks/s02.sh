r5_end() {
  block_status=$?
  date -u '+S2.end end_utc=%Y-%m-%dT%H:%M:%SZ'
  end_status=$?
  printf 'S2.end date exit=%s\n' "$end_status"
  final_status=$block_status
  if [ "$block_status" -eq 0 ]; then final_status=$end_status; fi
  printf 'S2 final exit=%s\n' "$final_status"
  exit "$final_status"
}
r5_block() {
  trap r5_end EXIT
  status=$?
  printf 'S2.trap exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u '+S2.start start_utc=%Y-%m-%dT%H:%M:%SZ'
  status=$?
  printf 'S2.start date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  date -u +%Y-%m-%dT%H:%M:%SZ
  status=$?
  printf 'S2.1 date exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  uname -srvm
  status=$?
  printf 'S2.2 uname exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cat /proc/version
  status=$?
  printf 'S2.3 proc-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  lscpu
  status=$?
  printf 'S2.4 lscpu exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  awk '/^processor/{n++} n==1 && /^(vendor_id|cpu family|model|model name|stepping|microcode|flags)[[:space:]]*:/' /proc/cpuinfo
  status=$?
  printf 'S2.5 cpuinfo-first-processor exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /usr/bin/bwrap --version
  status=$?
  printf 'S2.6 bwrap-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  stat -L -c '%a %U:%G %s %n' /usr/bin/bwrap
  status=$?
  printf 'S2.7 bwrap-stat exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /usr/bin/bwrap
  status=$?
  printf 'S2.8 bwrap-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  dpkg-query -W -f='${Package} ${Version}\n' bubblewrap
  status=$?
  printf 'S2.9 bwrap-package exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  read -r userns_max < /proc/sys/user/max_user_namespaces
  status=$?
  printf 'S2.10a max_user_namespaces-read exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'max_user_namespaces=%s\n' "$userns_max"
  case "$userns_max" in
    ''|*[!0-9]*|0) status=14 ;;
    *) status=0 ;;
  esac
  printf 'S2.10b max_user_namespaces-positive exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  apparmor_userns=/proc/sys/kernel/apparmor_restrict_unprivileged_userns
  if [ -e "$apparmor_userns" ]; then
    read -r apparmor_value < "$apparmor_userns"
    status=$?
    if [ "$status" -eq 0 ]; then
      printf 'apparmor_restrict_unprivileged_userns=%s\n' "$apparmor_value"
    fi
  else
    printf 'apparmor_restrict_unprivileged_userns=absent\n'
    status=0
  fi
  printf 'S2.11 apparmor-userns exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  id
  status=$?
  printf 'S2.12 id exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  hostname
  status=$?
  printf 'S2.13 hostname exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  cat /etc/os-release
  status=$?
  printf 'S2.14 os-release exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  grep MemTotal /proc/meminfo
  status=$?
  printf 'S2.15 memtotal exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  ulimit -Sa
  status=$?
  printf 'S2.16 ulimit-soft exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  ulimit -Ha
  status=$?
  printf 'S2.17 ulimit-hard exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import os,stat,sys
p="/var/tmp"
try:
    st=os.lstat(p)
except FileNotFoundError:
    print("var_tmp=missing")
    sys.exit(15)
if stat.S_ISLNK(st.st_mode):
    print("var_tmp=link")
    sys.exit(15)
if not stat.S_ISDIR(st.st_mode):
    print("var_tmp=not-a-directory")
    sys.exit(15)
real=os.path.realpath(p)
if real!=p:
    print("var_tmp=resolves-elsewhere realpath="+real)
    sys.exit(15)
print("var_tmp=directory mode=%04o uid=%d gid=%d" % (stat.S_IMODE(st.st_mode),st.st_uid,st.st_gid))
sys.exit(0)'
  status=$?
  printf 'S2.18a var-tmp-directory exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  df -P -T /var/tmp
  status=$?
  printf 'S2.18b df-var-tmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  df -P -i /var/tmp
  status=$?
  printf 'S2.18c df-inodes-var-tmp exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import os,sys
p="/var/tmp"
best=None
for line in open("/proc/self/mountinfo",encoding="utf-8",errors="replace"):
    f=line.split()
    sep=f.index("-")
    mnt=f[4]
    if p==mnt or p.startswith(mnt.rstrip("/")+"/"):
        if best is None or len(mnt)>=len(best[0]):
            best=(mnt,f[5],f[sep+1],f[sep+2],f[sep+3])
mnt,opts,fstype,source,superopts=best
print("var_tmp_mount="+mnt+" fstype="+fstype+" source="+source)
print("var_tmp_mount_options="+opts)
print("var_tmp_super_options="+superopts)
s=os.statvfs(p)
avail=s.f_bavail*s.f_frsize
floor=4*1024**3
print("var_tmp_bytes_total=%d bytes_available=%d floor=%d" % (s.f_blocks*s.f_frsize,avail,floor))
print("var_tmp_inodes_total=%d inodes_free=%d inodes_available=%d" % (s.f_files,s.f_ffree,s.f_favail))
print("var_tmp_capacity="+("sufficient" if avail>=floor else "insufficient"))
sys.exit(0 if avail>=floor else 16)'
  status=$?
  printf 'S2.18d var-tmp-capacity exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -VV
  status=$?
  printf 'S2.19 python-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import pytest; print(pytest.__version__)'
  status=$?
  printf 'S2.20 pytest-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  command -v zstd gpgv rsync lscpu
  status=$?
  printf 'S2.21 required-tools exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  zstd --version
  status=$?
  printf 'S2.22 zstd-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  gpgv --version
  status=$?
  printf 'S2.23 gpgv-version exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  sha256sum /usr/share/keyrings/ubuntu-archive-keyring.gpg
  status=$?
  printf 'S2.24 keyring-sha256 exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  /opt/freedom-blades/runtime/venv-web/bin/python -I -B -c 'import os,sys
hits=sorted(n for n in os.listdir("/var/tmp") if n.startswith(sys.argv[1]))
print("run_prefix_entries="+(",".join(hits) if hits else "none"))
sys.exit(10 if hits else 0)' '<RUN>'
  status=$?
  printf 'S2.25 run-prefix-absent exit=%s\n' "$status"
  if [ "$status" -ne 0 ]; then exit "$status"; fi
  printf 'S2 block exit=0\n'
  exit 0
}
r5_block </dev/null
