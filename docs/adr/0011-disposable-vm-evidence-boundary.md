# ADR 0011 — One disposable VM per privileged evidence run

Date: 2026-09-10

Status: **Proposed; not accepted or implemented**

**2026-09-10 disposition:** independent review returned changes requested.
C-P5.0-LAB-1 defers this alternative from Package 5.0's critical path in favour
of the [reserved disposable laboratory](../review/phase-5-0-reserved-laboratory-direction.md).
No further VM expansion is the active assignment. The proposal and its unresolved
review findings are retained for history; deferral is not technical acceptance.

Author: Codex, acting as design author for this proposal. Claude is assigned the
independent design review in [Handover information](../review/Handover%20information).
Peter Duscha retains acceptance authority. The delivered review is
[the VM independent review](../review/phase-5-0-evidence-vm-independent-review.md).

## Context

The Package 5.0 evidence harness repeatedly encounters the same problem: it
creates deliberately writable experimental objects, then relies on their
pathnames to protect later privileged operations and restore PostgreSQL
authentication configuration. C-8 revision 3 still has the three findings in
[the September 10 review](../review/project-review-2026-09-10.md).

The maintainer authorized preparation of a simpler alternative in the September
10 conversation, including reconsidering the process-per-step structure. That
instruction authorizes this proposal, not its new operational surface.

## Proposed decision

Use a fresh, synthetic, single-use **QEMU/KVM virtual machine**, managed through
libvirt from a controller outside the guest, for each privileged evidence run.
Own and dispose of the VM and its complete writable disk as a unit. Never mount
a host filesystem or expose a host PostgreSQL socket inside the guest.

Retain exact reviewed case vectors where they are useful. Replace the harness's
outer per-file restoration and deletion mechanism with externally recorded VM
allocation, execution, power-off, disk disposal and absence verification.
Experimental cleanup being measured remains inside the guest and retains its
actual S-A/S-B/S-C result; destroying the VM does not turn it into a pass.

Do not retrofit this mode into the existing armed executor behind a fallback.
It requires a distinct target type, manifest version and review. The existing
target remains unexecutable. The detailed proposal is
[the VM lifecycle design](../review/phase-5-0-evidence-vm-design.md).

## Consequences

Ownership and recovery no longer depend on mutable guest directory entries.
Replacement of a guest root or capture cannot redirect host cleanup, and guest
PostgreSQL configuration is discarded rather than copied back onto a shared
server. Host credentials and existing databases are never recovery inputs.

This adds a virtualization management boundary, image provenance, resource
limits and an external durable allocation record. It needs available KVM,
representative guest storage/kernel behavior and independent security review.
Those conditions are unverified. Software emulation is not an approved fallback:
QEMU's [security policy](https://www.qemu.org/docs/master/system/security.html)
does not give TCG the virtualization isolation guarantee this proposal needs.

VM isolation protects the host; it does not make observations from a compromised
guest trustworthy. Missing producers, failed controls and incomplete evidence
still block the gate. No package requirement, production recovery algorithm,
OD-62 disposition or existing finding closes through this ADR.

## Alternatives considered

| Alternative | Assessment |
|---|---|
| Add 128 root guards and retain in-place recovery | Rejected recommendation: still depends on mutable descendants and publication names, while adding many process boundaries. |
| Persistent supervisor with descriptor chains on the shared test host | Viable but not preferred: improves object binding, yet still needs writer exclusion, protected recovery storage and process containment for capability-bearing actors. |
| Container or mount namespace around the same host | Not selected: capability, systemd and peer-authentication evidence needs a carefully justified namespace topology; a shared writable mount does not prevent substitutions. |
| Fresh VM with external teardown | Recommended, conditional on feasibility and evidence equivalence. Larger infrastructure boundary, much simpler recovery obligation. |

No baseline amendment takes effect until independently reviewed and accepted.
