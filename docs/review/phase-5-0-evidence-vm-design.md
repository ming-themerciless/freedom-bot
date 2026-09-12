# Package 5.0 evidence — proposed VM lifecycle boundary

Date: 2026-09-10. Author: Codex.

**Current disposition:** reviewed with changes requested; deferred from Package
5.0's critical path by C-P5.0-LAB-1. The active assignment is the
[reserved-laboratory remediation](phase-5-0-reserved-laboratory-claude-prompt.md).
The proposal below is retained, not accepted or implemented, and its findings
remain unresolved. Its recommendation is no longer the current work direction.

**Proposed for independent technical review. Not accepted, implemented or
authorized for execution.** This is a concrete alternative to C-8 revision 3,
not a claim that its current code is repaired. Preparation was authorized by the
maintainer's September 10 instruction to prioritize a simpler, stronger design.

## 1. Recommendation and the requirement being changed

Give each privileged evidence run an entire fresh VM containing synthetic data.
An external controller owns the VM allocation and all its writable storage.
Recovery terminates that allocation and starts a later run from the unchanged
baseline image. Nothing is restored into oracle-test's PostgreSQL instance.

This deliberately changes the **outer harness cleanup contract** from reversing
individual changes on a reusable server to retiring a complete owned execution
environment. It must be accepted as such, rather than disguised as another
implementation of C-8's old per-object guarantee. A replacement object created
inside this guest is still within the disposable allocation. An existing host
object never becomes owned merely because its name matches a prefix.

The package's actual journal/probe cleanup and recovery requirements remain
unchanged. Their producers must still exercise them inside the guest and report
failures. External disposal only protects the laboratory. It supplies no evidence
that the production cleanup algorithm works.

## 2. Proposed topology and trust boundary

```text
Trusted management host (candidate: oracle-test; feasibility unverified)
  reviewed controller + durable run registry + immutable synthetic base image
        | local, restricted libvirt management connection
        | bounded observation channel; no commands supplied by the guest
        v
  QEMU/KVM guest, one run UUID, one private writable raw disk
    Linux + systemd + PostgreSQL 16 + pinned Python 3.12 (-I -S)
    reviewed experiment program and synthetic journal/schema/configuration
    freedomcoord / freedomsheet / fbprobe / postgres identities
```

The guest has no network interface, shared filesystem, host-device passthrough,
host Unix socket, libvirt/QMP endpoint, SSH key or production credential. A
dedicated virtio-serial channel carries bounded protocol records. PostgreSQL
Unix-socket and TCP rejection tests use guest-local sockets and loopback.

Proposed backend: libvirt's QEMU/KVM driver on x86_64 with a version-pinned q35
machine type. Require KVM and fail closed if it is unavailable. Do not silently
substitute TCG, a privileged container or execution directly on oracle-test.
QEMU explicitly distinguishes supported virtualization from TCG isolation.
[QEMU security requirements](https://www.qemu.org/docs/master/system/security.html)

The controller, libvirt daemon, host kernel, hypervisor isolation and host
administrator are trusted. Guest root and capability-bearing guest identities
do not have management authority. A malicious host administrator or a VM escape
is outside the claimed boundary; that boundary requires security acceptance,
not an assertion that root-owned directories defeat unrestricted root.

QEMU runs unprivileged with libvirt MAC confinement and enforced CPU, memory,
disk and process limits. The controller's registry and release source are not
accessible to QEMU. This must be verified on the selected backend; a default
configuration is not evidence. No guest-exec or arbitrary monitor-command API
is exposed by the controller.

## 3. Ownership outside the experiment

Use a dedicated libvirt storage pool and a controller-owned registry outside
the repository and guest. Proposed paths, **not allocated or approved**:

* `/var/lib/fb-evidence-controller/registry`: durable allocation records.
* `/var/lib/fb-evidence-controller/images`: read-only reviewed baseline images.
* `/var/lib/fb-evidence-controller/runs`: private per-run volumes and transcripts.

The trusted provisioning step establishes the parent chain, ownership and MAC
policy before any experiment. The controller opens and validates that chain
component by component without following symlinks, retains directory references
for registry writes, and refuses writable ancestors outside the trusted boundary.
Parent acquisition is an actual new operation, not fstat on a child descriptor.

Only the controller and trusted storage manager may change allocation-directory
entries. The QEMU process may write its attached disk bytes but cannot rename
volume entries, edit the registry or attach other disks. Other management clients
must be excluded from this pool and its domains during runs. This exclusion is
an operational prerequisite enforced by host access policy and one controller
instance, not a naming convention or an advisory lock alone.

Before allocation, durably record a random run UUID, intended domain UUID,
reserved volume name, approved pool identity, image digest, plan digest and
template digest. Record intent before calling libvirt. Record the returned volume
key and full domain definition before execution. Registry updates use private
staging, fsync and atomic publication under the retained parent reference; fsync
the directory. This staging has an explicitly excluded writer population, unlike
the proposed staging in postgres's guest directory.

After a controller crash, reconcile only registry-owned IDs with that dedicated
pool. An object from an uncertain create outcome may be adopted only when its
reserved identity, pool, domain definition and exclusive-controller history all
match. Otherwise quarantine and request operational investigation. Never search
for a matching prefix and destroy the result. Missing or corrupt registry data
permits no destructive adoption. Guest-provided UUIDs and paths grant no rights.

## 4. Baseline and resource contract

Build a fresh synthetic baseline in a separately reviewed build job; do not clone
the existing oracle-test disk. Record the image hash and package provenance.
It contains the OS, PostgreSQL 16, Python 3.12, systemd and required utilities,
but no runtime secrets or community data. The exact kernel, filesystem features,
mount options, utility builds and interpreter hash must be pinned in the final
manifest. Existing interpreter and E7 target facts cannot be copied across hosts.

The separately authorized image-build job includes a characterization boot to
establish these expected facts, followed by external disposal. It cannot run
the experiment plan or supply passing package evidence. Its outputs are reviewed
before the evidence manifest is approved. This avoids requiring an evidence run
to approve its own expected observations; the evidence run compares its early
observations with the already reviewed build contract. Host-only feasibility
inspection does not authorize this image-build boot.

Proposed initial capacity, to validate before adoption: one concurrent VM,
2 vCPUs, 4 GiB guest RAM, 6 GiB enforced host process-memory ceiling, one 20 GiB
raw writable volume, 30-minute run deadline, 120-second disposal deadline and
64 MiB transcript ceiling. A bound exceeded produces incomplete evidence and
teardown, never an implicit limit increase. Capacity is a proposed budget, not
a measurement of available oracle-test resources or a schedule commitment.

Clone the reviewed base to a private full raw volume; verify its content before
boot. No writable base attachment, external backing chain, guest-supplied image,
NVRAM, managed save or snapshot is admitted. A minimal BIOS guest avoids extra
persistent firmware artifacts. Disable automatic restart and autostart.
Record every generated host artifact, including channel sockets and libvirt
logs, for explicit retention/disposal. Unexpected disks or attachments refuse
execution. Do not mount an experimental guest disk on the host to inspect it.

## 5. Operation-by-operation contract

| Phase | Object and resolution | Prerequisite before effect | Failure behavior |
|---|---|---|---|
| Admit | external registry and reviewed release | exact approval/manifest; all producers and target facts resolved; capacity; no unresolved prior allocation | no VM starts |
| Allocate | dedicated pool via recorded identity; domain UUID generated by controller | durable intent; no existing allocation at reserved identity; exclusive manager | reconcile uncertainty, otherwise quarantine |
| Populate | private raw volume from reviewed baseline | source provenance and digest; destination belongs to allocation | no boot on mismatch |
| Define/boot | fixed libvirt domain template and its recorded UUID | validate entire device list, isolation policy and resource limits; persist identifiers first | stop/delete owned allocation independently of guest |
| Observe baseline | bounded guest channel tied to domain/run IDs | image and plan match; kernel, filesystem, capabilities, interpreter and positive controls observed | run inconclusive; dispose |
| Provision | guest-only accounts, database, directories and config | exact approved guest steps and target; no host routes/sockets | stop experiments; preserve failure record; dispose |
| Experiment | guest program executes pinned vectors under specified identities | producer exists; full capability/securebit contract; positive control; input state | stop on unexpected result; do not fabricate evidence |
| Record | host receives structured records, not files or shell text | run ID, sequence, step ID, schema and byte limits | reject invalid output; evidence incomplete |
| Finish/abort | external lifecycle controller addresses recorded domain UUID | registry authority; not guest root identity or guest cooperation | terminate guest; never invoke its recovery writer |
| Dispose | inactive domain and exact recorded volume key | confirm stopped, no attachment elsewhere, metadata matches registry | preserve/quarantine ambiguity; block next run |
| Verify | external domain/pool inventory and retained transcript | absence of domain, volume and unretained artifacts | no clean-laboratory claim unless verified |

Guest path replacement can invalidate an experimental result, but it cannot
redirect an outer cleanup command onto another host object: no outer cleanup
command consumes a guest path. Case programs used to measure behavior are loaded
from the reviewed image rather than the group-writable repository at execution
time. Guest compromise still invalidates their trustworthiness (§8).

## 6. Recovery is external disposal

State sequence:

`RESERVED → ALLOCATED → RUNNING → STOPPING → STOPPED → DISPOSED`

Any uncertain transition enters `QUARANTINED`; new execution is blocked until
the allocation is independently reconciled. The controller records each intent
before its external effect and each observed result afterwards. Guest runner
death, channel failure or timeout cannot suppress the outer transition to
STOPPING. Controller restart processes unfinished records before admitting work.

On normal completion, request guest shutdown for at most 30 seconds. On failure
or deadline, use the recorded domain's force-stop operation. Independently verify
it is inactive. Undefine it only after this verification; then delete only its
recorded unattached writable volume and verify absence. An API success response
alone is not disposal evidence. If libvirt is unavailable or stopping fails,
retain QUARANTINED and retry only through registry-based recovery after service
availability returns. No claim of bounded successful teardown during host failure.

The corresponding libvirt operations are `virDomainShutdown`,
`virDomainDestroyFlags`, `virDomainIsActive`, `virDomainUndefine`, and
`virStorageVolDelete` plus lookup/inventory. Undefining a running domain does not
stop it, and stopping a VM does not establish deletion of its disk. Those are
separate checked stages.
[Domain API](https://libvirt.org/html/libvirt-libvirt-domain.html),
[storage API](https://libvirt.org/html/libvirt-libvirt-storage.html)

No PostgreSQL configuration is restored onto the management host. If a run dies
after modifying guest authentication, the guest is terminated and discarded.
A later run boots a new clone of the verified baseline. Thus neither a surviving
guest buffer nor a trustworthy guest capture is required for laboratory recovery.

The current test subject may still need a **production recovery algorithm** to
be exercised inside the VM. That algorithm is a distinct producer and must use
its own accepted custody and verification design. Whole-VM disposal must never
be cited as passing the package's backup/restore or journal cleanup criteria.

## 7. Exact scope and interface changes proposed

| Component | Proposed change |
|---|---|
| Target model | New `VmEvidenceTarget`: management connection identity, pool identity, image/template digests, guest contract and limits. Existing `DisposableTarget` cannot activate it. |
| External lifecycle port | Closed methods `reserve`, `allocate`, `start`, `observe`, `stop`, `dispose`, `reconcile`, each keyed by registry-owned run ID. Callers supply no arbitrary XML, path, shell command or monitor command. |
| Backend | New isolated libvirt adapter; domain/volume creation, inspection and deletion restricted to the reviewed pool/template through the controller. Exact installed API versions remain to be pinned. |
| Guest protocol | Version 1; controller sends one manifest-bound plan identifier; guest emits sequence/step/status/typed-observation records. No guest request can allocate, attach, delete or select host objects. Maximum frame 64 KiB; cumulative output 64 MiB; unknown keys or duplicate step completions refuse. |
| Executor | Separate outer lifecycle runner. Guest retains exact case vectors and current stop-on-unsatisfied behavior. No fallback into the current host-mutating executor. |
| Materializer | Host HBA capture/restore operations absent in this mode. Configuration writes are inside the owned guest; experimental recovery remains separately tested. |
| Manifest | New version covering controller, backend, guest code, protocol, registry schema, template, baseline digest and all changed guest step contracts. Two non-executing regenerations must match; old digest approves nothing new. |
| Outcomes | Separate `experiment_outcome`, `guest_cleanup_outcome`, `lab_disposal_outcome`, and `evidence_eligibility`. Preserve existing distinctions and missing-producer rules. |
| Deployment | Dedicated host controller policy/pool and synthetic image build. No platform migration, bot/web deployment, production credential or configuration change. |

The controller's narrow API does not make the underlying libvirt privilege
small automatically. Host policy must constrain the service; its actual
permissions and attack surface require separate review. Installing a hypervisor,
provisioning a pool or performing a feasibility SSH probe is not authorized by
this proposal.

## 8. What the evidence would and would not prove

The VM must demonstrate the intended filesystem's append/immutable behavior,
full E1–E8 identities, securebits, systemd controls and PostgreSQL authentication.
Peer authentication obtains the client identity from the OS, so both client and
server must run inside the same guest; a forwarded host connection would test a
different boundary. [PostgreSQL 16 peer authentication](https://www.postgresql.org/docs/16/auth-peer.html)

Require an explicit equivalence table for every band: OS/kernel build,
filesystem and mount features, utilities, identity construction, PostgreSQL
version/configuration, expected observations and limitations. The guest kernel
does not inherit oracle-test's version just because it runs there. Filesystem
behavior and actual storage power-loss durability are distinct; an injected
fsync error proves the failure path, not hardware persistence. Host-specific
C-1/sudoers facts remain separate authorized read-only observations and cannot
be inferred from the guest.

A guest-root compromise may forge observations. The external transcript proves
what was received from that run, not the truth of arbitrary guest assertions.
The evidence claim assumes reviewed bounded case programs and no unrelated
hostile guest software; deliberately adversarial cases need independent controls
and explicit measurement scope. Tamper the measuring program or lose observation
integrity and mark the affected evidence inconclusive. VM isolation alone cannot
solve that problem or justify closing P5.0-R5.

The three unresolved C-7 producers and twelve unconfirmed current target facts
remain unresolved. A new target needs its own facts. No manifest or user-supplied
observation can substitute for a missing producer.

## 9. Finding disposition under this proposal

| Finding/risk | Proposed response; no closure claimed |
|---|---|
| PR-20260910-1, substituted staged restoration | Outer restoration is removed. The base is read-only outside guest reach; future runs use new clones. Any experimental restore remains subject to this finding until its own producer is repaired. |
| PR-20260910-2, root guard blocks recovery | Stop/disposal depends only on external allocation identity, never on the guest root or capture. |
| PR-20260910-3, nonexistent parent descriptor | External registry acquisition explicitly opens and validates its real parent chain before allocation; guest mkroot is no longer the laboratory ownership primitive. |
| EH-R16-1 and C-8 per-entry substitution | Address through a proposed ownership-scope change to the whole guest. Old executor remains defective and disabled; no retroactive claim of per-entry safety. |
| R-C8 create/guard intervals, descendants and buffer loss | No acceptance of those risks on a shared test host is requested. Their guest effects are contained within the allocation; experimental validity remains separately checked. |
| Host virtualization and management compromise | New trusted boundary and residual; requires security review and maintainer acceptance. |
| Host outage / undeletable allocation | QUARANTINED; no new run, no clean claim. Explicit registered residue survives restart. |

## 10. Required verification matrix

First implement pure planning/state/protocol tests with injected ports. These
are model evidence only. Operational checks occur later on an approved VM host.

| Injection / check | Required observable result |
|---|---|
| Pre-existing domain/volume at reserved identity | No adoption, start, overwrite or deletion; refusal before experiments. |
| Controller crash before/after each create response | Durable intent resolves only the exact owned allocation; uncertainty quarantines; no duplicate live run. |
| Changed template, base digest, extra disk/shared filesystem/NIC | Refused before boot; no fallback. |
| Replaced guest root before provisioning, experiment or cleanup | Host paths and volumes of other allocations untouched; affected evidence not silently passed; owned VM disposed. |
| Replaced capture, staged source or destination after configuration write | No host restore issued; guest may fail; external disposal works without capture/buffer. |
| Guest root forks persistent processes or ignores shutdown | External stop ends the whole guest; host verifies inactivity before volume deletion. |
| Controller restart after guest config mutation | Registry recovery completes independent of guest protocol and PostgreSQL authentication. |
| Fake guest UUID/path/XML or oversized/malformed record | Rejected; no management operation follows the payload. |
| Guest tampers with measuring program | Affected evidence inconclusive; laboratory disposal does not upgrade it. |
| Domain stopped but disk remains / deletion response lost | Not DISPOSED until inventory confirms absence; quarantine unresolved residue. |
| Unrecognized attachment or registry corruption | No destructive recovery by name guessing; block and report. |
| Host memory/disk/time limit exceeded | Incomplete evidence, bounded output and teardown; other host services remain available in supervised resource drill. |
| Positive controls fail / producer absent / E7 mismatch | Existing evidence refusal semantics retained. |
| Intentional package S-B and next-invocation refusal | Observe both before disposal; report laboratory cleanup independently. |
| Clean complete run followed by a new run | New UUID/new disk, same approved baseline; no inherited accounts/configuration; full producer evidence required. |
| Guest attempts host socket/filesystem/network access | No such attachment/route; supervised negative checks plus independent domain-policy inspection. |

Every model case needs a successful control. The implementation handback must
map each operational claim to actual target evidence and label unrun cases.

## 11. Feasibility, effort and decisions

Do **not** begin a general VM platform. One backend, one template, one concurrent
run, no UI, network orchestration, snapshots, migration or reusable guest pool.

Bounded next work:

1. Independent design review by **Claude**, assigned in
   [Handover information](Handover%20information), including whether
   complete-guest ownership satisfies the harness authorization and keeps package
   evidence honest. Return one consolidated list against this design.
2. Once the design direction and exact read-only inspection scope are accepted,
   verify KVM/libvirt availability, host capacity and confinement on a candidate
   host. **Not performed here.** Existing preflight permission does not silently
   include these new virtualization facts. If KVM is unavailable, stop and price
   a separate approved VM host; do not install dependencies or buy capacity.
3. After feasibility, pin image/tool/template values and submit the precise
   implementation and host-provisioning permission diff. No repeated request
   for already authorized design work.
4. Implement only after the applicable scope decision, review the implementation,
   approve an exact execution digest, then run the synthetic operational matrix.

Rough planning estimate for the new harness slice: O 4 / ML 7 / P 12 focused
implementer-days (PERT 7.3), plus 1–2 independent reviewer-days and 2 remediation
days. Low confidence until feasibility; excludes obtaining a host, image build
delays, C-7 producer implementation and package evidence review. This is not a
promised schedule or an assertion of savings over an unestimated alternative.

Decisions for Peter **after independent recommendation**: accept the whole-guest
outer cleanup contract; approve the bounded VM management surface and target;
accept the external trust boundary and measured resource/retention limits.
Proposed retention: sanitized transcripts 30 days; experimental disks deleted
after transcript completion and shutdown, with failed deletion quarantined and
blocking admission. Keeping a failed guest disk for investigation needs an
explicit recorded exception; never mount it on the management host.

Because Codex authored this alternative, Codex cannot provide its independent
design acceptance. Claude's review assignment is specific to this authored
design; it does not silently reassign existing project roles or approvals.

## 12. Submission evidence and current state

Prepared from the canonical agreement/roadmap, disposable-server contract,
evidence authorization, current executor/cleanup/materializer/target contracts,
package plan §§2.12.3, 2.13.2–2.13.2b, C-8 revision 3 and the September 10 review.
Primary documentation above supports API semantics; the isolation and recovery
argument is a proposed design inference, not tested host behavior. Online
documentation is not a substitute for pinning installed versions.

Documentation-only submission. No tools source, test, generated plan, manifest,
environment or operational state changed. No VM, host preflight, privilege,
database, SSH, service or generated-vector execution occurred. No tests are
claimed for the proposed mechanism. Submission checks passed: local links and
Markdown fence/whitespace checks for the two new artifacts, all 32 manifest
source hashes matching, and `git diff --check`. Earlier suite counts remain
evidence of their earlier tree only; no runtime suite was rerun for this
documentation-only proposal.

Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**,
EH-R16-1 **Open** and the current plan `is_executable=False`. Migration 0014,
production deployment/cutover and Package 5.1+ remain unauthorized.
