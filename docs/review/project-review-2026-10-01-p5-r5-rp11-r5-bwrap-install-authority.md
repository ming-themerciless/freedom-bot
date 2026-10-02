# Gemini R-5 bubblewrap-install authority — 2026-10-01

Decision ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R1-A1`

Peter Duscha authorizes Gemini to remediate the single missing host prerequisite
on the disposable `oracle-test` host and resume the already accepted R-5
assignment.

Gemini may run only these privileged package-management operations:

```bash
ssh oracle-test "sudo apt-get update"
ssh oracle-test "sudo apt-get install -y bubblewrap"
```

The authority includes packages that the Ubuntu package manager necessarily
installs or upgrades as dependencies of that exact transaction, but no other
requested package, upgrade, removal or repository/configuration change. Gemini
must record the complete apt result, installed package version, `/usr/bin/bwrap`
identity, `bwrap --version`, and whether unprivileged user namespaces work. If
apt proposes a broader material system change, fails, or the unprivileged
mechanism remains unavailable, Gemini stops without improvising.

After the prerequisite succeeds, Gemini resumes the active R-5 assignment
using entirely new, unique root, package-cache, checkout, output, trace and
evidence directories. No stopped-run directory or downloaded artifact may be
reused. The original R-1 … R-3 procedure, HA comparison, pass conditions,
hard stops and negative authority boundaries remain unchanged.

Gemini must also remediate review finding `R5-R1-1`: the amended handback must
acknowledge that the repository checkout was synchronized and must not claim
that no ambient file changed or that the whole host remained in its exact
pre-run baseline. It must distinguish repository synchronization, the newly
authorized package/cache changes, and disposable build evidence.

This is not authority for general `sudo`, package upgrades, host configuration,
services, databases, launcher installation, H-1/H-2, PO-14, RP-11 wiring,
controlled writes, reboot, an evidence band, harness `--execute`, an
operational pass, commit or push. Gemini writes the amended prescribed
handback and stops. R-5 remains incomplete until independently reviewed and
accepted afterward.

- [Stopped handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-handback.md)
- [Codex review](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md)
- [Active R-5 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)
