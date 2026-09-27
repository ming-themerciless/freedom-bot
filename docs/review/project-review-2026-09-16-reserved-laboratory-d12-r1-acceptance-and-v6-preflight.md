# D12-R1 accepted; released V6 read-only preflight performed — 2026-09-16

Peter Duscha accepted Codex's independent technical and security re-review of
[C-P5.0-LAB-D12-R1](phase-5-0-reserved-laboratory-d12-r1-remediation-handback.md)
and explicitly released the queued **V6 read-only prerequisite survey**.

## D12-R1 disposition

**PR-20260915-LAB-D12-1 is closed.** The remediation puts the lifecycle
publication-temporary comparison on the one authoritative admission path,
between re-seal and parse, and all seven participants refuse before their work
is called. T1 and T6 use the same guarded operator-recovery implementation.
The independent local evidence was 9 focused regressions passed, the complete
Phase 5.0 evidence suite **2,239 passed, zero skipped**, guards **31/31**,
`compileall` successful and `git diff --check` clean, all with
`TEST_DATABASE_URL` unset.

This acceptance approves no digest and advances no package gate. The review
manifest digest remains review input only and must not be passed to
`--execute`.

## V6 authorization boundary

Peter's release authorized SSH and read-only target inspection for V6 only:
filesystem and mount type, `fs.protected_hardlinks`, execution identity,
relevant ownership/mode assumptions and capability state. It did not authorize
synchronization, creating a link, provisioning, permission or group changes,
`systemd-tmpfiles`, database access, generated-vector execution, a participant,
a boundary/materializer or `--execute`.

## Observations on `oracle-test`

The survey used non-elevated, non-mutating commands (`id`, `uname`, `cat` on the
sysctl, `findmnt`, `df`, `stat`, `/proc/self/status`, `capsh`, `getcap`,
`readlink` and `getent`). No repository synchronization was performed.

| Observation | Result |
|---|---|
| Host/kernel | `Test`, Linux `7.0.0-31-generic`, x86-64 |
| Execution identity | `uid=1001(ubuntu)`, `gid=1001(ubuntu)`; supplementary groups `adm`, `cdrom`, `sudo`, `dip`, `lxd` |
| `/opt/freedom-blades` parent mount | `/dev/sda1`, ext4, mounted at `/`, `rw,relatime,discard,errors=remount-ro,commit=30` |
| `/var/lib` parent mount | the same `/dev/sda1` ext4 root mount |
| `fs.protected_hardlinks` | `1` |
| Process capabilities | inheritable, permitted, effective and ambient sets all zero; bounding set non-empty; `NoNewPrivs=0` |
| `capsh` confirmation | current and ambient capability sets empty; securebits unlocked; uid/euid and gid are `1001` |
| Runtime interpreter | resolves to `/home/ubuntu/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu/bin/python3.12`, owned `1001:1001`, mode `0775`, with no file capability reported |
| Existing parents | `/opt/freedom-blades` is `1001:1001 0755`; `/var/lib` is `0:0 0755` |
| Exact publication paths | `/opt/freedom-blades/evidence`, `/var/lib/freedom-blades`, `laboratory`, `laboratory/runs` and `recovery` are absent |
| Proposed group | `freedomlab` is absent (`getent group freedomlab` returned no entry) |

## Disposition

**V6 was performed, but it does not pass or close.** The filesystem and policy
prerequisites were observed: both future location families resolve through
existing parents to ext4, and the hard-link policy is `1`. The exact publication
directories and the proposed group do not exist, so their required ownership
and mode assumptions cannot be confirmed on the target. The zero effective
capability state also means the design may not rely on `CAP_FOWNER`; its
protected-hardlink owner/read-write conditions must hold for the actual
publication object and execution identity.

As V6's approved contract already states, these observations do not demonstrate
that the real `linkat` succeeds. **I3 remains unconfirmed.** A controlled write
verification remains separately gated and was not performed or authorized.
V8 and V10 were not performed.

`plan.is_executable` remains `False`; C-7, EH-R16-1, LAB-R6, LAB-X1, P5.0-R5
and OD-62 remain Open; Package 5.0 remains not ready. The next action is
maintainer direction on provisioning/design readiness and, independently, a
separate decision whether to authorize the controlled I3 write verification.
