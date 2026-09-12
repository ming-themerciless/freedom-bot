# Independent design review — proposed VM evidence boundary, 2026-09-10

Reviewer: Claude, assigned by the maintainer in
[Handover information](Handover%20information). Author of the reviewed design:
Codex. Acceptance authority: Peter Duscha.

## Disposition

**Changes requested.** The proposed VM lifecycle boundary is not technically
recommended in its current form, and it is not recommended as the path to
Package 5.0's outstanding evidence.

Two things are true at once and must not be collapsed:

1. **The core architectural claim is sound.** Moving ownership from individual
   guest objects to a whole disposable allocation genuinely removes the outer
   harness's destructive dependence on guest pathnames. No outer cleanup command
   consumes a guest path, so the class of defect behind EH-R16-1 and
   PR-20260910-1 cannot express itself against a guest object. §1, §5 and §6
   state this accurately and refuse to overclaim it.
2. **The proposal reproduces the same defect class one layer up, and its central
   safety premise fails on the only candidate host.** The registry publication
   path re-instantiates PR-20260910-1's staged-write-then-rename mechanism; the
   disposal path deletes by an identity the cited documentation does not
   establish as substitution-proof; and both exemptions rest on an exclusive-
   writer premise that `docs/operations/disposable-test-server.md` contradicts
   for `oracle-test`.

Five findings are Blocking. This disposition is not implementation approval, not
execution approval, and not a rejection of ADR 0011 as a direction. ADR 0011
remains **Proposed**. Package 5.0 remains **not ready**, P5.0-R5 **Blocking**,
OD-62 **Open**, EH-R16-1 **Open**, and the current plan `is_executable=False`.
No execution digest is approved.

**Preferred approach (§F):** complete Package 5.0's evidence on the already
approved disposable target using the bounded descriptor/held-bytes/quiescence
mechanism from C-8 revision 3 §9.2, and hold the VM boundary as the target
architecture for a later, separately funded slice. The reasoning is in §F and it
is about sequencing and authorization distance, not about which architecture is
cleaner.

---

## A. Scope, sources and evidence limits

### A.1 What was reviewed

The complete VM lifecycle design and ADR 0011, against the current working tree,
the authorization in force, and the package requirements the proposal would have
to keep satisfied. This is a design review. It is not a security audit of libvirt
or QEMU, not a feasibility assessment of any host, and not a package-gate
assessment.

### A.2 Documents read completely

* `.agents/AGENTS.md`; `docs/implementation-plan.md` current-status blocks and
  the Package 5.0 entries; `docs/operations/disposable-test-server.md`.
* `docs/adr/0011-disposable-vm-evidence-boundary.md`.
* `docs/review/phase-5-0-evidence-vm-design.md` (the review subject).
* `docs/review/project-review-2026-09-10.md`;
  `docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16-3.md`;
  `docs/review/phase-5-0-evidence-harness-r16-independent-review.md`.
* `docs/review/phase-5-0-evidence-harness-authorization-draft.md`.
* `docs/review/phase-5-0-package-plan.md` §2.12.3, §2.13.2b, §2.13.2c.
* `docs/project-management/status.md`, `decision-register.md`,
  `raid-register.md`, and change-log entries C-P5.0-VM-P and C-P5.0-VM-H.

### A.3 Source inspected

`tools/phase_5_0_evidence/`: `targets.py`, `approved_target.py`, `cleanup.py`,
`case_runtime.py`, `capability.py`, `review_manifest.py`, `records.py`,
`concrete_plan.py` (generated output), `execution/executor.py`,
`execution/case_program.py`, `execution/boundary.py`. Generated artifacts:
`docs/review/phase-5-0-evidence-harness-review-manifest.json` and the concrete
plan built in-process. Tests under `tests/phase_5_0_evidence/` were run, not
rewritten.

### A.4 Primary references consulted

| Reference | What it was used for | What it did **not** settle |
|---|---|---|
| [QEMU security policy](https://www.qemu.org/docs/master/system/security.html) | Confirms the design's TCG position. The page states the non-virtualization use case covers TCG, that bugs affecting it "are not considered security bugs at this time", that coverage requires "a virtualization accelerator like KVM or HVF", that the guest is untrusted, and that "QEMU processes must run as unprivileged users" | Nothing about the installed version on any host |
| [libvirt storage API](https://libvirt.org/html/libvirt-libvirt-storage.html) | `virStorageVolGetKey` documents the key as "globally unique, so the same volume will have the same key no matter what host it is accessed from"; `virStorageVolLookupByPath` documents a path as "locally (host) unique" | **What the key actually is for a directory-backed pool.** The API page does not say |
| [libvirt storage format](https://libvirt.org/formatstorage.html) | The key "cannot be set when creating a volume: it is always generated". Warns that "Any modification of the storage pool outside of libvirt … may not update the cached volume or pool metadata" | Same gap; also no documented directory-scanning contract for `dir`/`fs` pools |
| [libvirt domain API](https://libvirt.org/html/libvirt-libvirt-domain.html) | Cited by the design for the stop/undefine/delete separation | Not independently re-fetched; the design's ordering claim is assessed as design reasoning in VM-17 |
| [PostgreSQL 16 peer authentication](https://www.postgresql.org/docs/16/auth-peer.html) | Cited by the design; its argument that client and server must share the guest is correct as documented | — |

### A.5 Evidence limits — read these before citing anything below

* **No runtime proof of anything in the proposal exists, and none is claimed.**
  Nothing in the VM design is implemented. No test in this repository exercises
  a controller, a registry, a libvirt adapter or a guest protocol, because none
  of those exists.
* **No operational check was performed.** No SSH, no `oracle-test`
  synchronization, no host inspection, no KVM or libvirt probe, no VM
  allocation, no image build or characterization boot, no dependency
  installation, no database operation, no destructive drill, no service change,
  no credential access, no generated-vector execution, no `--execute`, no armed
  boundary or materializer. No stage, commit, push, reset or history rewrite.
* **The libvirt findings are design inferences against primary documentation,
  not host behavior.** Where the documentation is silent — notably the volume
  key's construction for a directory-backed pool — this review says so and asks
  the design to pin it, rather than asserting the implementation detail.
* **Local test figures are from the fallback interpreters, not the canonical
  `oracle-test` environment.** `TEST_DATABASE_URL` was unset throughout, so every
  database-marked skip is an unverified assertion and not PostgreSQL evidence.
* **Existing user changes were preserved.** `git status` was checked at the start
  and the tree is unchanged apart from this review artifact and the pointer
  updates in §I.

---

## B. Findings

Numbered consecutively. Locations are given as file and section or line.
Classification is against the roadmap: **Blocking** prevents accepting the design
as a technical direction to implement; **Important** must be corrected before an
implementation permission diff is submitted; **Optional** improves the artifact.

---

### VM-1 — Blocking: the exclusive-controller premise is contradicted by the only named candidate host

**Location.** `phase-5-0-evidence-vm-design.md` §2 (trust boundary), §3
(paragraphs beginning "Only the controller and trusted storage manager…" and
"After a controller crash…"), §5 Allocate row; ADR 0011 "Consequences".

**What the design relies on.** Three separate load-bearing statements: "The
controller, libvirt daemon, host kernel, hypervisor isolation and host
administrator are trusted"; "Other management clients must be excluded from this
pool and its domains during runs. This exclusion is an operational prerequisite
enforced by host access policy and one controller instance"; and "The
controller's registry and release source are not accessible to QEMU."

**What the repository records about the candidate.**
`docs/operations/disposable-test-server.md` §1 and §3.1 state that `oracle-test`
"exists so that **Codex, Claude Code, Antigravity, and maintainers have full
administrative (root) access** to execute end-to-end tests, destructive
PostgreSQL migration drills, dependency builds, and system-level experiments",
with `sudo ALL=(ALL) NOPASSWD:ALL` and key-based SSH from this workspace, and
that "Any agent running in this workspace can reach the remote environment
without prompts or interactive passwords."

**Counterexample.** Run R is `RUNNING`. A second agent, doing unrelated
authorized work on the disposable host, runs
`ssh oracle-test "sudo virsh destroy <domain>"` — or, equally, `sudo rm` on a
file under `/var/lib/fb-evidence-controller/registry`. The controller's next
observation finds the domain inactive or the record gone. Its reconciler cannot
distinguish this from its own crash, because the only inputs it has are the
registry and the pool inventory, and one of those is the thing that was changed.

**Consequence.** The proposal's central promise — that ownership no longer
depends on mutable directory entries an adversary can change — is not delivered.
It is re-expressed as dependence on an access policy that the candidate host is
documented not to have. Every downstream claim in §3, §5 and §6 that begins
"only the controller may…" is unenforced on `oracle-test`.

**Second-order consequence the design does not state.** Adopting `oracle-test`
as the management host converts the *disposable* target into a *trusted*
component. That contradicts `approved_target.py`'s `DISPOSABILITY_STATEMENT`,
which is the basis on which Peter confirmed the target on 2026-09-05, and it
would need an explicit Operations Owner decision rather than a feasibility check.

**Required correction.** Either (a) name a management host on which the
controller is the sole administrative principal, and state the mechanism that
makes it so — a dedicated host, or a separate account whose libvirt access is
constrained by policy and whose registry directory the drill accounts cannot
write; or (b) withdraw the exclusivity premise and re-derive §3 and §6 without
it, which means the registry and the pool must be treated as objects a
privileged host actor can change. Do not carry the premise as an "operational
prerequisite" while naming a candidate whose documented profile denies it.

**Verification cases.** *Success:* a second administrative principal attempting
`virsh destroy` on the run's domain, or a write under the registry directory, is
refused by host policy, and the run completes and reports DISPOSED. *Failure:*
the same attempt succeeds, and the controller must classify the allocation
`QUARANTINED` and report the external interference — never report a clean
disposal.

---

### VM-2 — Blocking: the registry publication path re-instantiates PR-20260910-1

**Location.** `phase-5-0-evidence-vm-design.md` §3, the paragraph beginning
"Before allocation, durably record…", specifically: "Registry updates use private
staging, fsync and atomic publication under the retained parent reference; fsync
the directory. This staging has an explicitly excluded writer population, unlike
the proposed staging in postgres's guest directory."

**What is wrong.** This is the same mechanism PR-20260910-1 found defective:
write to an exclusively created temporary name, fsync, publish by `rename`. The
finding was never about the destination; it was that a writer to the containing
directory can unlink the staged name and put another file there after the
write/fsync and before the rename, at which point the held descriptor is
irrelevant and `rename` consumes the replacement. The design's only defence is
the writer-population exclusion, which VM-1 shows is unestablished.

**Counterexample.** The controller stages
`…/registry/.tmp-<run>` , writes the intent record, fsyncs it, and is about to
rename it to `…/registry/<run>.json`. A principal with write access to
`…/registry` unlinks `.tmp-<run>` and creates a file of its own at that name.
The rename publishes that file. The controller's own held descriptor still refers
to the bytes it wrote; the durable record that later governs adoption, stopping
and deletion is the other file.

**Consequence.** The record that authorizes destruction can be forged by the
same actor class that VM-1 shows is present. Because §6 makes the registry "the
registry authority" for the Finish/abort and Dispose phases, a forged record is a
forged authorization for a destructive libvirt operation. PR-20260910-1 is not
resolved by this proposal; it is relocated from the guest to the host, into the
one write path whose integrity the whole design depends on.

**Required correction.** State the excluded writer population as an enumerated
set of principals together with the mechanism that enforces it, and specify what
the controller does when it cannot verify the exclusion — refuse to admit work,
not proceed on an assumption. Do not present PR-20260910-1 as "removed" in §9
while the identical publication mechanism governs the allocation record. If the
exclusion cannot be enforced, the registry needs an integrity binding that does
not rest on directory entries, such as an authenticated record the controller can
verify after reading it back.

**Verification cases.** *Success:* an uninterrupted publication under a directory
only the controller can write produces a record whose read-back matches the bytes
staged. *Failure:* an injected unlink-and-replace between the fsync and the rename
must produce a refusal and `QUARANTINED`, and must not publish a record; assert
the exact bytes, not merely that a file exists.

---

### VM-3 — Blocking: disposal deletes by an identity the documentation does not establish as substitution-proof

**Location.** `phase-5-0-evidence-vm-design.md` §5 Dispose row ("inactive domain
and exact recorded volume key"), §6 ("delete only its recorded unattached
writable volume and verify absence"), §3 ("Record the returned volume key").

**What the documentation actually says.** `virStorageVolGetKey` documents the key
as globally unique across hosts, and `virStorageVolLookupByPath` documents a path
as merely host-unique — which is what the design leans on. But neither the API
page nor `formatstorage.html` states **what the key is for a directory-backed
pool**; the format page says only that it "is always generated". Separately, the
format documentation warns that "Any modification of the storage pool outside of
libvirt … may not update the cached volume or pool metadata."

**Why that gap is load-bearing.** For file-backed pools the key is derived from
the volume's location, and a pool refresh re-discovers volumes by scanning the
target directory. If that holds for the selected backend, then "delete by
recorded volume key" is delete by pathname, and the design's outer boundary
performs exactly the operation it claims to have eliminated. This review cannot
resolve it from the cited documentation and does not assert the implementation
detail; the design must pin it against the installed version.

**Counterexample, stated on the assumption the design must now exclude.** The
recorded volume for run R is the file `<pool>/<run-uuid>.raw`. Between the
verified-inactive check and the delete, a principal with pool-directory write
access unlinks that name and creates another file there — or replaces it with a
symbolic link. A pool refresh rediscovers the replacement under the same name and
therefore the same key. `virStorageVolDelete` deletes the replacement. The
controller's absence check succeeds, and the run is recorded `DISPOSED`. The
outer harness has issued a destructive operation keyed on a mutable directory
entry, which is the defect class of EH-R16-1 and PR-20260910-1.

**Consequence.** §5's claim that "no outer cleanup command consumes a guest path"
is true and is not the whole claim being made. The outer boundary still consumes
a *host* path, and the design's own §1 frames the change as "retiring a complete
owned execution environment" — which is only stronger than per-object cleanup if
the environment's identity is stronger than a name.

**Required correction.** Pin what the volume key is for the selected backend and
libvirt version, in the manifest, with the observation that established it. If it
is derived from the path, add an identity binding that is not a pathname — for
example, open the volume before the domain is stopped, hold the descriptor
through disposal, and compare device and inode at deletion — or record the
residual explicitly with its actor, prerequisite, interval and consequence, in
the form §8 of C-8 revision 3 already uses. Do not claim the outer boundary is
free of pathname-keyed destruction until this is settled.

**Verification cases.** *Success:* a normal disposal deletes the recorded object,
and an independent pool and domain inventory confirms absence. *Failure:* an
injected replacement of the volume's path between the inactivity check and the
delete must refuse and quarantine, and the test must assert that the replacement
object still exists afterwards.

---

### VM-4 — Blocking: §10's "affected evidence not silently passed" is unsatisfiable by anything the design proposes

**Location.** `phase-5-0-evidence-vm-design.md` §10, row *"Replaced guest root
before provisioning, experiment or cleanup"*, required result *"Host paths and
volumes of other allocations untouched; affected evidence not silently passed;
owned VM disposed."* Supporting statements: §5 Experiment and Record rows; §7
Executor row ("Guest retains exact case vectors and current stop-on-unsatisfied
behavior"); §9 row 4.

**The mechanism gap.** The design proposes no in-guest ownership guard. It states
that the guest keeps the current vectors and stop-on-unsatisfied behavior, which
is the behavior EH-R16-1 found defective. Verified against source:
`execution/case_program.py:562-608` (`_do_mkroot`) records device and inode at
creation; `_do_statroot` at `:609-620` is consumed only by the `REVALIDATE`
cleanup step (`cleanup.py`, `CleanupStepKind.REVALIDATE`) that runs immediately
before the single root `rmdir`. The R16 review reproduced 30 cleanup commands
referencing the root before that check.

**The substitution actor exists inside the guest by construction, and this was
verified rather than assumed.** The generated plan's step `B5-E4` is
`capsh … --uid=fbprobe --addamb=cap_dac_override --addamb=cap_dac_read_search
--addamb=cap_linux_immutable …`, and the manifest's expected identity for `E4`
carries `cap_amb 0x206`. `B5-E6` is the same shape with `cap_amb 0x20e`. The plan
therefore constructs, deliberately, a non-root identity holding ambient
`CAP_DAC_OVERRIDE`, which can create, rename and unlink entries anywhere in the
hierarchy regardless of mode.

**Counterexample.** Inside the guest, after `B6-M1` has written the synthetic
`pg_hba.conf`, the root is renamed and a replacement directory is created at the
same path, populated with a `before/` subtree. The in-guest runner restores
PostgreSQL configuration from the replacement's captures, clears flags and
removes paths inside the replacement, and classifies the run S-A or S-C. The
external transcript records a passing cleanup classification for a hierarchy the
run did not create. External disposal then destroys the VM, and the transcript
survives as the evidence.

**Consequence.** The design's most valuable honest claim — §1's "destroying the
VM does not turn it into a pass", and §9's refusal to close findings — is true of
`lab_disposal_outcome` and false of `guest_cleanup_outcome`, because nothing
detects the substitution before the classification is made. §8 concedes that a
guest-root compromise "may forge observations", but §10's row promises a stronger
observable than §8 supports, and the two must be reconciled.

**Required correction.** Choose one and state it: (a) the guest runner carries an
accepted in-guest ownership guard — which re-imports C-8's whole mechanism
decision, its cost and its authorization impact into a proposal that presents
itself as replacing that decision; or (b) §10's row is downgraded to "the
affected bands are marked inconclusive", and the design names the mechanism that
marks them. Option (b) is coherent and cheap, but it must be written, because as
drafted the row reads as a property the design delivers.

**Verification cases.** *Success:* an unsubstituted run reports S-C with every
positive control satisfied. *Failure:* an injected root substitution after the
configuration write must produce a non-S-C classification and an explicitly
inconclusive band for every case whose attribution depended on that root — not a
pass, and not a silent S-A.

---

### VM-5 — Blocking: "the old executor remains defective and disabled" is not true of this tree

**Location.** `phase-5-0-evidence-vm-design.md` §9, row *"EH-R16-1 and C-8
per-entry substitution"*: "Old executor remains defective and disabled". ADR 0011
"Proposed decision": "The existing target remains unexecutable."

**What was verified.** `execution/executor.py:440-510`. `ExecutingRunner.__post_
init__` refuses on four conditions, and every one of them is data-conditional:
`plan.is_executable` being False; `EXPECTED_INTERPRETER_REAL_PATH` being
`UNCONFIRMED`; `EXPECTED_INTERPRETER_SHA256` being `UNCONFIRMED`; and any of the
ten entries of `capability.E7_TARGET_FACTS` being `UNCONFIRMED`. Nothing refuses
because EH-R16-1 is open. The twelve unconfirmed facts are exactly the ones the
**already authorized** read-only target preflight would supply — C-8 revision 3
§13.1 records that preflight as "authorized and **assigned to Codex**", and the
implementation plan's 2026-09-09 block repeats it.

**Counterexample.** Codex performs the authorized preflight. The two interpreter
facts and the ten E7 facts are stated and independently verified. A C-7 producer
is later supplied and `is_executable` becomes True. The defective executor is now
runnable, with EH-R16-1 unfixed, and no decision about ADR 0011 was required for
that sequence to occur. The proposal's assertion that the old path is "disabled"
would have contributed to the belief that it was safe.

**Required correction.** Add an unconditional refusal keyed to EH-R16-1 rather
than to target facts — the existing target must refuse execution while the
finding is open, independently of how many facts are confirmed — or fix EH-R16-1
before the preflight facts are supplied. Until one of those is done, restate §9's
row as "the old executor remains defective and is currently refused for unrelated
reasons", which is what the code says.

**Verification cases.** *Success:* with all twelve facts supplied and the three
C-7 cases resolved in a fixture, `ExecutingRunner` still refuses, naming
EH-R16-1. *Failure:* the same fixture constructing a runner successfully is the
defect.

---

### VM-6 — Important: the management credential is named as a problem and given no constraint

**Location.** §2 ("QEMU runs unprivileged with libvirt MAC confinement and
enforced CPU, memory, disk and process limits"), §7 final paragraph ("The
controller's narrow API does not make the underlying libvirt privilege small
automatically. Host policy must constrain the service").

**What is missing.** The design states the problem correctly and then names no
mechanism. A client holding a `qemu:///system` connection can define a domain
whose disk element is any path on the host, and with libvirt's default dynamic
ownership behavior, starting such a domain changes the ownership of that host
file. The controller's closed API constrains the controller; it does not
constrain the credential the controller holds, and any other holder of that
credential — see VM-1 — is unconstrained.

**Required correction.** Name the concrete controls and make each one a
verification target rather than a property of a default configuration:

* the account the controller runs as, and that membership in a group conferring
  broad libvirt access is **not** an acceptable credential;
* the libvirt access-control policy rules, with the attributes they key on —
  domain UUID and pool name — and the actions they permit;
* the QEMU driver settings that are load-bearing: the unprivileged user and
  group, dynamic ownership, namespaces, seccomp, and which mandatory access
  control driver is in force;
* what the controller does when any of these cannot be confirmed at start-up.

**Verification cases.** *Success:* the controller defines and starts the reviewed
template. *Failure:* the same credential attempting to define a domain with a
disk outside the reviewed pool is refused by policy — demonstrated by
independent inspection of the policy, not by the controller declining to try,
which proves nothing about the credential.

---

### VM-7 — Important: the resource contract omits the two limits that protect the management host

**Location.** §4, paragraph beginning "Proposed initial capacity"; §3's three
proposed paths.

**Two gaps.** "6 GiB enforced host process-memory ceiling" names no enforcement
mechanism. "One 20 GiB raw writable volume" names no allocation policy, so a
sparsely allocated volume lets guest writes consume host free space up to its
capacity. §3 places `registry`, `images` and `runs` under one parent, which on a
default installation means one filesystem.

**Counterexample.** The guest writes until its volume is full. The host
filesystem reaches `ENOSPC`. The controller's next durable registry write fails —
and §6's entire recovery argument rests on "The controller records each intent
before its external effect". The one write the design cannot afford to lose is
the one the guest can cause to fail.

**Required correction.** Preallocate the volume, or place `runs` on a separate
filesystem or under a quota from `registry`; name the mechanism enforcing the
memory ceiling; add disk I/O throttling and a process-count limit to the template
and to the manifest. State the controller's behavior when a registry write fails
for space.

**Verification cases.** *Success:* a run at the full capacity budget completes
and every registry write succeeds. *Failure:* a guest filling its volume must
leave the registry writable, must produce bounded incomplete evidence and
teardown, and must not silently raise a limit.

---

### VM-8 — Important: the guest channel contract is under-specified in three ways that matter

**Location.** §2 ("A dedicated virtio-serial channel carries bounded protocol
records"), §7 Guest protocol row, §5 Record row, §10 row 8.

**Three gaps.**

1. **No serialization or framing is named.** "Maximum frame 64 KiB; cumulative
   output 64 MiB" bounds sizes without saying what a frame is or how it is
   delimited. A parser for untrusted input is the design's only guest-facing
   attack surface and it is specified only by its limits.
2. **No per-frame or idle deadline.** The 30-minute run deadline is the only
   time bound. A guest that opens a frame and stalls consumes the whole run
   budget before the outer deadline fires.
3. **Attribution is ambiguous.** §5 requires records to carry "run ID, sequence,
   step ID"; §7 says the controller "sends one manifest-bound plan identifier".
   If the guest is told the run ID, a record's run ID field proves nothing about
   which run produced it. If it is not, the design must say attribution comes
   from the channel the controller opened.

**Required correction.** State the format and framing; state a per-frame and idle
deadline; and state that attribution derives from the channel endpoint the
controller created, never from a field inside a record. Records are guest-
supplied data and must be treated as such throughout.

**Verification cases.** *Success:* a well-formed transcript for a complete run is
accepted and its records are attributed to the correct run. *Failure:* each of —
a record naming a different run's identifier, a record completing a step already
completed, a record arriving after its step's deadline, an oversized frame, and a
half-frame followed by silence — must be rejected, and no management operation
may follow any of them.

---

### VM-9 — Important: single-controller enforcement is asserted and its available mechanisms are ruled out

**Location.** §3: "This exclusion is an operational prerequisite enforced by host
access policy and one controller instance, not a naming convention or an advisory
lock alone." §6: "Controller restart processes unfinished records before
admitting work."

**What is wrong.** The design rejects the two mechanisms that would implement the
property and supplies neither replacement. "One controller instance" is the
requirement restated, not a mechanism.

**Counterexample.** Two controller processes start — a stale one that was
believed dead and a new one after an operator restart. Both read the same
`RESERVED` record and both call allocate. One receives a definite success, the
other an uncertain response. On reconciliation each finds an object whose
reserved identity, pool and domain definition match its own record, so §3's
adoption test admits it for both. The result is either two live runs against one
allocation, or one live run whose disposal is issued by a process that does not
know it is running.

**Required correction.** Name the mechanism and its failure behavior: a service
manager constraint that permits one instance, an exclusive lock file created with
`O_EXCL` under the retained parent reference and carrying the holder's identity,
or a libvirt-side reservation. State what happens when the mechanism cannot be
established — refuse to admit work. Also define "exclusive-controller history",
which §3 makes an adoption prerequisite and never specifies.

**Verification cases.** *Success:* a second controller instance refuses to admit
work while the first holds the allocation. *Failure:* a simulated concurrent
start must not produce two live allocations, two adoptions, or a disposal issued
against a running allocation.

---

### VM-10 — Important: `QUARANTINED` has no release path, owner or evidence standard

**Location.** §6 ("Any uncertain transition enters `QUARANTINED`; new execution
is blocked until the allocation is independently reconciled"), §10 rows 2, 10 and
11, §11's retention paragraph.

**What is missing.** Quarantine blocks all future admission. No procedure, owner,
evidence standard or record is defined for leaving it. "Independently reconciled"
is the requirement, not the procedure.

**The package already has the right pattern.** §2.13.2b refuses, reports residue
by absolute path, does not clean it, and names an operator recovery procedure in
`docs/operations/migration-cutover-and-rollback.md`. The reasoning there applies
here verbatim: an automatic second attempt by the same code with the same
authority has no reason to succeed, and turning a state that needs a human into
one that looks transient is the failure mode.

**Counterexample.** A delete response is lost. One volume may or may not remain.
Every subsequent evidence run is blocked. The pressure is then to clear the
registry by hand, which is the unrecorded destructive act §3 forbids — and the
design gives an operator no sanctioned alternative.

**Required correction.** Define the release procedure, its owner, the independent
absence check it requires — an inventory read that does not come from the
controller's own cached state — and the durable record it writes. State that
release without the independent check is refused.

**Verification cases.** *Success:* a quarantine raised by an injected lost delete
response is released by the named procedure, and the release is recorded with the
evidence that justified it. *Failure:* a release attempted without the
independent absence check must be refused, and the quarantine must persist across
a controller restart.

---

### VM-11 — Important: retention and sanitization of host artifacts is named but not contracted

**Location.** §4 ("Record every generated host artifact, including channel
sockets and libvirt logs, for explicit retention/disposal"), §11 ("Proposed
retention: sanitized transcripts 30 days").

**The requirement it must meet.** The evidence authorization permits retaining
"sanitized evidence artifacts under `docs/review/` that contain no secrets,
credential contents, player data or unrelated host configuration".

**What is missing.** Who sanitizes, against what rule, and which artifacts may be
retained at all. Domain XML, libvirt logs and QEMU logs carry host paths, the
pool location, device topology and the management account's identity. Those are
unrelated host configuration under the authorization's own words.

**Counterexample.** A retained libvirt log naming the management host's storage
layout and the QEMU user is committed under `docs/review/` as run evidence.

**Required correction.** State the sanitization rule and its owner; state which
artifact classes may be retained and which must be disposed rather than
sanitized; and state explicitly that domain XML and libvirt/QEMU logs are host
configuration under the authorization's exclusion unless redacted against a named
rule. Note that the existing harness already solves the analogous problem —
`execution/boundary.py` reads command output into a local, passes it to the
sanitizer and drops it, so no object above that line holds raw output — and the
controller should adopt the same shape rather than a retention period.

**Verification cases.** *Success:* a retained transcript passes the stated rule
and contains no host path outside the reviewed pool. *Failure:* an artifact
containing a host path outside the reviewed pool, or the management account's
identity, must be refused for retention.

---

### VM-12 — Important: durability equivalence omits the one setting that decides whether guest `fsync` reaches host storage

**Location.** §8, paragraph beginning "Require an explicit equivalence table";
§4, "Clone the reviewed base to a private full raw volume".

**What is right.** The design correctly separates an injected `fsync` error,
which proves the failure path, from hardware persistence, which it does not
claim. That distinction is the one §2.13.1 defect 1 exists to enforce and it is
kept.

**What is missing.** The disk cache and I/O mode are not pinned. Whether a guest
`fsync` results in a host flush is decided by that setting, and it is not part of
the template contract, the manifest, or the equivalence table §8 requires.

**Counterexample.** The template is defined with a cache mode that does not honor
guest flushes. Every durability observation the guest makes becomes a statement
about the emulator's page cache, and the band reports a pass. This is §2.13.1
defect 1 in a new form: a result taken on a different substrate than the one it
claims to describe.

**Required correction.** Pin the disk cache and I/O settings in the template;
include them in the manifest and in the per-band equivalence table; and state
explicitly which durability claim the chosen mode supports and which it does not.
§10 row 3 already refuses a changed template, so this becomes enforced once cache
mode is part of what "template" means.

**Verification cases.** *Success:* the booted domain's effective disk settings
match the reviewed template. *Failure:* a template deviating in cache or I/O mode
must refuse before boot.

---

### VM-13 — Important: the feasibility sequence understates what the candidate host's answer is likely to cost

**Location.** §2 ("Trusted management host (candidate: oracle-test; feasibility
unverified)"), §11 step 2, RAID row VM-A1.

**The facts in the repository.** `oracle-test` is reached at a public IPv4
address (`docs/operations/disposable-test-server.md` §1), which makes it a hosted
instance rather than hardware this project controls. Hardware-accelerated
virtualization inside a hosted instance requires the provider to expose nested
virtualization, which general-purpose instance shapes commonly do not. The
design's own rule is correct and fail-closed: "Require KVM and fail closed if it
is unavailable… Do not silently substitute TCG."

**Consequence the design does not draw.** If KVM is unavailable, §11 step 2 says
"stop and price a separate approved VM host" — and §11's estimate explicitly
excludes "obtaining a host". The probability-weighted cost of the proposal is
therefore dominated by the single item the estimate leaves out, and the decision
Peter is being asked to prepare for (VM-D1/D2/D3) is being framed before the fact
that most affects it is known.

**Required correction.** This is a correction to the decision framing, not to the
mechanism. State the KVM availability check as the gate whose likely negative
result changes the recommendation, and price the alternative host — acquisition,
ongoing cost, and who administers it — before the architecture decision rather
than after. Note that the alternative host also resolves VM-1, since a
purpose-provisioned host need not be the multi-agent drill host.

---

### VM-14 — Important: the scope table omits the guest runner, and the estimate is not supportable

**Location.** §7 (scope and interface changes), §11 ("Rough planning estimate…
O 4 / ML 7 / P 12 focused implementer-days (PERT 7.3)").

**What §7 introduces.** A new target model; a new isolated libvirt adapter; a
controller implementing a six-state machine plus quarantine, crash reconciliation
and adoption; a durable registry with its own schema and integrity contract; a
versioned bidirectional protocol requiring two implementations; a new four-field
outcome model; a new manifest version covering all of it; and §10's seventeen
verification rows, each needing an injected port and a success control.

**What §7 omits.** Who writes the in-guest runner. The Executor row says "Guest
retains exact case vectors and current stop-on-unsatisfied behavior", which
describes what the guest must do without saying what code does it. If it is the
current executor, VM-4 applies in full. If it is new code, it is the largest
single item in the slice and it is not in the table.

**Measured comparison.** The current harness — narrower in scope than the above,
with no external lifecycle, no registry and no protocol — is 23,903 lines under
`tools/phase_5_0_evidence/` and 18,124 lines under `tests/phase_5_0_evidence/`,
and it has been through sixteen review rounds. A PERT figure of 7.3
implementer-days for the list above is not consistent with that body of work.

**Required correction.** Re-estimate after feasibility, with the guest runner,
the registry and reconciliation state machine, and the image build pipeline as
separate line items, and state the estimate's basis. Do not carry a
low-confidence figure into a decision table beside an alternative whose cost is
described qualitatively as "high", because that comparison reads as quantitative
and is not.

---

### VM-15 — Important: the proposal increases the authorization distance to the twelve unconfirmed target facts

**Location.** §4 ("Existing interpreter and E7 target facts cannot be copied
across hosts"; the characterization-boot paragraph), §8 final paragraph, §11.

**What the twelve facts are, verified.** `case_runtime.EXPECTED_INTERPRETER_REAL_
PATH` and `EXPECTED_INTERPRETER_SHA256`, plus the ten entries of
`capability.E7_TARGET_FACTS` (`uid`, `gid`, `groups`, `cap_inh`, `cap_prm`,
`cap_eff`, `cap_bnd`, `cap_amb`, `no_new_privs`, `securebits`). All are
`UNCONFIRMED` and each independently makes `ExecutingRunner` refuse.

**Where they stand today.** They are obtainable by a read-only preflight that is
already authorized and already assigned to Codex, and that has simply not been
performed.

**Where the proposal puts them.** Into a synthetic image whose build job and
characterization boot are explicitly **not** authorized, on a host that does not
yet exist and whose feasibility is unverified. The design states this honestly in
§4 — "Host-only feasibility inspection does not authorize this image-build boot"
— but neither §11's sequence nor ADR 0011's consequences record it as a cost.

**A related covered-source consequence.** `case_runtime.py:113` hard-codes
`INTERPRETER_PATH = "/opt/freedom-blades/runtime/venv-web/bin/python"`, which is
`oracle-test`'s path. A guest interpreter lives elsewhere, so this constant
becomes a per-target value; that changes a covered source, which changes the
manifest digest, which is a re-review. Correct behavior, and it belongs in the
scope table.

**Required correction.** Record in ADR 0011's consequences and in §11's sequence
that the proposal converts twelve facts obtainable by an authorized, unperformed
read-only preflight into facts requiring a new authorization, a new host and a
new build job. This is a genuine argument *against* the proposal on sequencing,
and the ADR should carry it rather than leaving it to a reviewer to derive.

---

### VM-16 — Optional: state which of the existing target refusals carry into the new target model

`targets.py` refuses `/var/lib` as a mutation root, refuses `tmpfs` roots
(§2.13.1 defect 1), refuses production database names, and requires the
`fb-evidence-` and `fb_evidence_` naming rule. §3's proposed controller paths sit
under `/var/lib`, beside the approved evidence root
`/var/lib/fb-evidence-p5-0`. That is not a defect, because the controller tree is
not a `DisposableTarget`. But §7's `VmEvidenceTarget` row should state which of
those refusals apply to the new target and which deliberately do not, so a reader
does not infer that the existing guards carry over.

---

### VM-17 — Optional: make the disposal ordering argument complete

§6's ordering is correct and worth keeping explicit: verify inactive, then
undefine, then delete the volume, then verify absence. Undefining first would
remove the persistent definition while the domain still ran; deleting first would
remove a disk still attached. The design should also state that the plain
undefine call is sufficient *because* §4 already forbids NVRAM, managed save and
snapshots, so a reader can see why no flag variant is needed. Without that
sentence the two sections are correct separately and their dependency is
invisible.

---

### VM-18 — Optional: four missing rows in §10

Add, each with a success control: two concurrent controller instances (VM-9);
registry filesystem exhaustion during a run (VM-7); libvirt daemon restart
between the domain's start and its stop; and host reboot between `STOPPED` and
`DISPOSED`. §10 covers controller crash and host limits but not the management
service's own restart, which is the case §6 depends on when it says "retry only
through registry-based recovery after service availability returns".

---

## C. Traceability

### C.1 Against PR-20260910-1/2/3 and EH-R16-1

| Item | Design's claim (§9) | This review's disposition |
|---|---|---|
| **PR-20260910-1** — substituted staged restoration | "Outer restoration is removed. The base is read-only outside guest reach" | **Partly accurate, not resolved.** The outer *configuration* restoration is genuinely removed and that is a real gain. The finding's mechanism — staged write, fsync, publish by rename, with a writer able to substitute at the name — is re-instantiated in the registry write path (§3) and exempted only by an exclusion premise VM-1 shows is unestablished. See **VM-2**. Remains **Open** |
| **PR-20260910-2** — root guards suppress independently available recovery | "Stop/disposal depends only on external allocation identity, never on the guest root or capture" | **Resolved for the laboratory recovery obligation, and correctly so.** The finding's requirement that independently safe restoration proceed no longer applies, because no restoration is attempted: the guest is destroyed. The finding's *other* half — that a production recovery algorithm needs its own custody design — is correctly carried forward in §6 rather than claimed closed. **Open** against its production-recovery producer; **not applicable** to the outer harness under this design |
| **PR-20260910-3** — G-0 relies on a nonexistent parent descriptor | "External registry acquisition explicitly opens and validates its real parent chain before allocation; guest mkroot is no longer the laboratory ownership primitive" | **Accurate as a scope statement and correctly labelled as one.** §3's "Parent acquisition is an actual new operation, not fstat on a child descriptor" answers the finding for the new component. The defect in `_do_mkroot` (`execution/case_program.py:562-608`) is unrepaired and remains present in the guest, where it now bears on evidence integrity rather than host safety. See **VM-4**. Remains **Open** against the existing source |
| **EH-R16-1** | "Address through a proposed ownership-scope change to the whole guest. Old executor remains defective and disabled; no retroactive claim of per-entry safety" | **The scope change is real; the disablement claim is false.** The distinction the handover asked to preserve — a scope replacement is not a repair — is preserved correctly and deserves credit. But nothing disables the old executor; it is refused by unrelated data conditions that an already-authorized preflight would clear. See **VM-5**. Remains **Open** |

### C.2 Against design §10's verification matrix

| §10 row | Disposition |
|---|---|
| Pre-existing domain/volume at reserved identity | Adequate as stated |
| Controller crash before/after each create response | **Incomplete** — "exclusive-controller history" is an unspecified adoption prerequisite, and concurrent controllers are not covered. VM-9 |
| Changed template, base digest, extra disk/NIC | Adequate, and strengthened once cache and I/O mode are part of the template. VM-12 |
| Replaced guest root before provisioning, experiment or cleanup | **Unsatisfiable as written.** VM-4 |
| Replaced capture, staged source or destination after configuration write | Adequate for the outer boundary; the guest half inherits VM-4 |
| Guest root forks persistent processes or ignores shutdown | Adequate |
| Controller restart after guest config mutation | Adequate; add libvirt daemon restart. VM-18 |
| Fake guest UUID/path/XML or oversized/malformed record | **Incomplete** — no framing, no idle deadline, no attribution rule. VM-8 |
| Guest tampers with measuring program | Adequate and correctly limited by §8 |
| Domain stopped but disk remains / deletion response lost | **Incomplete** — no quarantine release path. VM-10. Volume identity unpinned. VM-3 |
| Unrecognized attachment or registry corruption | Adequate in intent; depends on VM-2 |
| Host memory/disk/time limit exceeded | **Incomplete** — registry and run volumes share a filesystem. VM-7 |
| Positive controls fail / producer absent / E7 mismatch | Adequate; correctly preserves existing refusal semantics |
| Intentional package S-B and next-invocation refusal | Adequate **provided** the design states that both invocations occur in the same guest. A fresh guest must never be used to satisfy §2.13.2b's next-invocation refusal, because a clean baseline trivially has no residue |
| Clean complete run followed by a new run | Adequate |
| Guest attempts host socket/filesystem/network access | Adequate in intent; the independent domain-policy inspection is the load-bearing half and depends on VM-6 |
| *(missing)* concurrent controllers; registry ENOSPC; libvirt restart; host reboot between STOPPED and DISPOSED | VM-18 |

### C.3 Package requirements checked for silent waiver

Question 1 of the assignment asks whether whole-guest ownership waives a package
requirement. Checked, with the result:

* **§2.13.2b S-A/S-B/S-C and the next-invocation refusal.** Preserved by §10's
  row, subject to the same-guest condition in C.2. **Not waived.**
* **§2.12.3 peer authentication and the HBA ordering control.** Preserved and
  strengthened: §8's argument that client and server must share the guest is
  correct, and a guest-local instance is a better substrate for this than a
  shared server whose configuration must be restored. **Not waived.**
* **C-1 sudoers and the pre-change HBA/identity-map inspection.** §8 correctly
  keeps these as separate authorized host observations that cannot be inferred
  from a guest. **Not waived.**
* **The authorization's "filesystem representative of the intended production
  journal filesystem".** §8 requires a per-band equivalence table and does not
  supply one. Not a waiver, but the requirement is deferred to an artifact that
  does not exist, and VM-12 shows one input to it is currently unpinned.
  **At risk, not waived.**
* **The authorization's "destroy or explicitly inventory every temporary object
  after evidence collection, with cleanup failure treated as a stop condition".**
  Satisfied for guest objects by construction. A **new** class of temporary host
  object appears — registry records, transcripts, channel sockets, libvirt logs,
  the pool itself — and §4 requires them recorded but §11 gives them a retention
  period rather than an inventory-and-disposal contract. **Partly waived by
  omission.** VM-11.
* **The authorization's stop condition "the target cannot be proved disposable or
  isolated".** A new target needs a new Operations Owner disposability
  confirmation. §7 and the decision register route this to VM-D2 correctly.
  **Not waived**, and see VM-1 for why the management host cannot inherit the
  existing confirmation.
* **Three unresolved C-7 producers.** Verified in-process: the built plan carries
  `is_executable=False` with three `UnresolvedStep` entries —
  `BAND7-JNL-51-PROVENANCE-OMITTED`, `BAND7-JNL-47-NO-GENERATION-ON-FAILURE`,
  `BAND7-JNL-47-RECOVERY-STATE` — each stating that the producing tooling "is
  Package 5.0's gated product work and does not exist". §8 concedes this
  correctly. **Not waived, and not improved.** This is the substance of §F.

---

## D. What the design gets right, stated so it is not lost in remediation

These are not concessions; they are the parts a corrected design must keep.

1. **The scope change is named as a scope change.** §1's refusal to disguise the
   new contract "as another implementation of C-8's old per-object guarantee" is
   exactly the distinction the assignment asked to preserve, and §9 sustains it
   row by row.
2. **Disposal is separated from evidence.** Four distinct outcome fields, §1's
   "External disposal only protects the laboratory. It supplies no evidence that
   the production cleanup algorithm works", and §6's insistence that whole-VM
   disposal "must never be cited as passing the package's backup/restore or
   journal cleanup criteria". This is the single most important property of the
   proposal and it is stated repeatedly and without hedging.
3. **The TCG position is correct and correctly sourced.** Verified against
   QEMU's security policy, which excludes TCG from security support and requires
   an accelerator. Failing closed rather than substituting emulation is right.
4. **The stop/undefine/delete separation is correct**, including the observations
   that undefining a running domain does not stop it and that an API success is
   not disposal evidence.
5. **Observation integrity is not overclaimed.** §8's statement that "The
   external transcript proves what was received from that run, not the truth of
   arbitrary guest assertions", and that VM isolation "cannot solve that problem
   or justify closing P5.0-R5", is the correct limit and it is the reason the
   proposal cannot be sold as a route to closing the gate.
6. **No finding is claimed closed and no residual is claimed accepted.** §9's
   table, §11's decision list and §12's status paragraph are accurate against the
   registers as they stand.

---

## E. Answers to the assignment's seven questions, in short

1. **Does whole-guest ownership remove the outer dependence without waiving a
   requirement?** It removes the dependence for destructive effects — genuinely,
   and §5's "no outer cleanup command consumes a guest path" is true. It does not
   remove it for evidence classification (VM-4), it relocates the same defect
   class to the host (VM-2, VM-3), and it partly waives the temporary-object
   inventory requirement by omission (VM-11). PR-20260910-1 and EH-R16-1 remain
   Open; PR-20260910-2 is resolved in the laboratory scope; PR-20260910-3 is
   answered for the new component and unrepaired in the old one.
2. **Allocation through crash and uncertain-response windows.** Intent durability
   is specified and its write path is defective (VM-2). Volume and domain binding
   is specified and its identity is unpinned (VM-3). The exclusive-controller
   assumption has no mechanism (VM-9). Adoption depends on an unspecified
   "exclusive-controller history" (VM-9). Stopping and the detach/undefine/delete
   ordering are correct (§D.4). Independent absence checks are required and their
   quarantine outcome has no exit (VM-10). **A destructive operation can reach an
   unowned host resource: `virStorageVolDelete` against a replaced volume path
   (VM-3), and any operation authorized by a forged registry record (VM-2).**
3. **The privilege boundary.** The design states the credential problem and
   constrains nothing (VM-6). QEMU confinement is named as a default rather than
   a verified setting. The channel parser is specified by size limits alone
   (VM-8). Resource limits omit host protection (VM-7). Forbidden attachments are
   handled well and are refused before boot.
4. **Image provenance and unauthorized prerequisites.** The build-job and
   characterization-boot separation is the right shape and correctly unauthorized.
   Interpreter and E7 facts are correctly not copied across hosts, and the
   proposal increases the authorization distance to them (VM-15). No TCG fallback
   is correct (§D.3). Prerequisites needing new authorization: hypervisor and
   libvirt installation, access-control policy, pool provisioning, the controller
   tree, the image build, the characterization boot, and possibly a new host
   (VM-13). None was performed and none is populated here.
5. **Evidence equivalence.** Capabilities, systemd and filesystem flags are
   plausible in a guest and require the per-band table §8 asks for and does not
   supply. Peer authentication is correctly argued. Durability separates the
   failure path from persistence correctly and omits the setting that decides it
   (VM-12). External isolation, guest observation integrity and production
   recovery evidence are kept separate throughout, and **VM disposal cannot
   promote a failed experiment or a missing producer into a pass** — that is
   sound for `lab_disposal_outcome` and unproven for `guest_cleanup_outcome`
   (VM-4).
6. **Scope, estimate and the alternative.** §F.
7. **Tests, restart, quarantine, deadlines, retention.** VM-8, VM-9, VM-10,
   VM-11, VM-18, and the §10 table in C.2.

---

## F. Preferred approach, with supported tradeoffs

### F.1 The recommendation

**Complete Package 5.0's evidence on the already approved disposable target,
using the bounded mechanism C-8 revision 3 already priced — candidates 5, 7 and a
narrowed 2 from its §9.2 — and hold ADR 0011 as the target architecture for a
later slice that is not on Package 5.0's critical path.**

Concretely, and without requiring speculative infrastructure or a generic VM
management product:

* **Candidate 5 (`G-1`, held-bytes recovery)** — the materializer retains the
  verified original bytes and restores from the buffer it verified, with the
  source and destination prerequisites PR-20260910-2 required stated separately.
  Maintainer decision, already routed, cost moderate.
* **Candidate 7 (`G-4`, quiescence)** — the seven probe subjects are removed only
  on a passing quiescence check and otherwise reported preserved. Low cost, no
  new verb or privilege.
* **Candidate 2, narrowed** — a held root descriptor and an `openat` chain
  applied **only** to the operations that consume ownership before a destructive
  or configuration-bearing effect, rather than to every guarded effect. C-8 §9.3
  establishes correctly, from `rename(2)`, that a held directory descriptor
  survives its name being renamed away and that a pathname identity comparison
  cannot reproduce that. Narrowing it to the ownership-consuming operations is
  what keeps the privileged-interface widening bounded, and it is the part of
  §9.2's "high" cost estimate that is actually load-bearing.
* **Class F stays open and is accepted as a laboratory residual**, with its
  actor, prerequisite, interval and consequence stated. C-8 §9.4 is right that
  Linux has no descriptor-only unlink primitive, and that limitation is real.

### F.2 Why this rather than the VM, given that the VM is architecturally cleaner

The VM design is cleaner for the recovery obligation. That is not the deciding
question. The deciding question is what stands between the project and Package
5.0's evidence, and the answer was verified in-process rather than assumed:

* **The binding constraint is missing producers, not ownership.** The built plan
  reports `is_executable=False` with three unresolved C-7 steps, each of which
  states that the tooling that would produce the observation "is Package 5.0's
  gated product work and does not exist". No ownership design — neither C-8's nor
  this one — moves that. §8 concedes it.
* **The second constraint is twelve facts that an already-authorized preflight
  would supply.** Under the VM proposal those same facts require a new
  authorization, a new host and an unauthorized characterization boot (VM-15).
  The proposal moves the project *further* from executable evidence, not closer.
* **The VM's safety benefit protects a host that is defined as disposable.**
  `oracle-test` exists for destructive drills with full root for multiple agents.
  Spending a new trusted component, a hypervisor, an image pipeline and a
  management credential to protect it inverts the reason it exists — and, per
  VM-1, doing it *on* that host does not work anyway.
* **The VM's central premise fails on the only named candidate, and the
  alternative is a host nobody has priced** (VM-1, VM-13).
* **The estimate that makes the VM look comparable is not supportable** (VM-14).
  Against a corrected estimate, the comparison is not close.

### F.3 What this recommendation does not say

It does not say ADR 0011 is wrong. The whole-allocation ownership model is the
better architecture, and if this project ever needs privileged evidence on a host
that is not disposable, it is the right answer. It should stay **Proposed**, with
VM-1, VM-2 and VM-3 corrected, so that it is ready when a purpose-provisioned
host exists. It also does not say the VM must never be built; it says it must not
be built *as the route to closing Package 5.0*, because it is not one.

It does not reopen decisions Peter has made, and it accepts nothing on his
behalf.

### F.4 Residuals under the recommended approach

| Residual | Actor and prerequisite | Interval | Consequence | Status |
|---|---|---|---|---|
| Class F, final-entry replacement | uid 0, `CAP_DAC_OVERRIDE`, or the `freedomsheet` account this run constructs, on the disposable host | between the guard and the `unlink`/`rmdir` | a replacement object at a final path component is removed | **Unaccepted.** Requires a recorded maintainer decision |
| Class C, in-place content mutation | same | between digest and consumption | verified bytes are not the consumed bytes, except where `G-1`'s held buffer applies | **Unaccepted** |
| `R-C8-1` create-to-identify interval | same | between `mkdir` return and `fstat` | ownership attributed to an object created in that window | **Unaccepted** |
| `G-4` premise 2 — whether `useradd --system` leaves the password field locked | not established anywhere in this repository | — | `G-4` remains a boundary, not an observation | **Proof obligation**, C-8 §13.1-2 |
| Evidence integrity under an in-guest privileged adversary | any holder of uid 0 or ambient `CAP_DAC_OVERRIDE` | whole run | observations may be forged; affected bands inconclusive | **Unaccepted, and unchanged by either design** |

---

## G. Remaining decision requests

None of these is decided by this review, and this review recommends no
acceptance. They are stated so Peter is asked once, with the right information.

| Id | Request | Owner | What this review recommends |
|---|---|---|---|
| **VM-D1** — whole-guest outer cleanup contract | Accept or defer the ownership-scope change | Peter | **Defer.** Sound as architecture; not the route to Package 5.0 evidence (§F) |
| **VM-D2** — management surface, candidate host, feasibility scope | Approve or refuse a bounded read-only KVM/libvirt/capacity/confinement inspection | Peter, Operations Owner | If ADR 0011 is pursued at all, authorize **only** the read-only inspection, and treat VM-1 as its first question: whether any candidate host can be the sole-controller host. Nothing else |
| **VM-D3** — external trust boundary, capacity, retention | Accept the new trusted component and its budgets | Peter, with independent security recommendation | **Not ready to decide.** VM-1, VM-2, VM-3 and VM-6 must be corrected first |
| **`G-1`** — materializer capture/restore, a read of a live file and a write of observed bytes | Widens a privileged interface | Peter | Recommended under §F.1. Already routed by C-8 §14; unchanged by this review |
| **`G-0`** — five parent target facts | Obtaining them is the authorized read-only preflight | Peter, on Codex's recommendation | Unchanged; the preflight is already authorized and unperformed |
| **Class F / Class C / `R-C8-1` residuals** | Explicit acceptance as laboratory residuals on a disposable host | Peter, via Codex | Recommended for explicit acceptance under §F.1, with the actor and interval in §F.4 recorded. **Not accepted here** |
| **New** — EH-R16-1 unconditional refusal | Whether the existing executor refuses on the open finding rather than on target facts | Codex technical acceptance | Recommended. See VM-5 |

**New material items recorded, not accepted.** VM-1's host-role conflict, VM-2's
registry publication defect and VM-3's disposal-identity gap are new risks against
the proposal. They are recorded in the RAID register beside the existing VM-R1,
VM-R2, VM-R3 and VM-A1 rows; none is accepted, and none changes ADR 0011's
**Proposed** status or any package gate.

---

## H. Commands run, results, and checks not run

Every command was run locally in `/opt/freedom-blades/platform` with
`TEST_DATABASE_URL` explicitly unset, using the task-specific fallback
interpreters. Both were verified before use: `/opt/discord-bots/venv-web/bin/
python` and `/opt/discord-bots/venv/bin/python` are both Python 3.12.3. **These
are not the canonical environment**, which is `/opt/freedom-blades/runtime/
venv-web/bin/python` on `oracle-test`.

| Check | Command | Result |
|---|---|---|
| Structural guards | `env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py` | **193 passed** |
| Full harness suite | `env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence` | **1391 passed** |
| Manifest source hashes | independent SHA-256 of all 32 `source_digests` entries | **32 entries, zero mismatches** |
| Plan executability | `build_concrete_plan()` in-process | **`is_executable=False`; 3 unresolved C-7 steps; 139 steps** |
| Manifest version | file and module compared | **both 9** |
| Local links | every relative Markdown link in the design, ADR 0011, the handover and the disposable-server document resolved | **no broken links** |
| Whitespace | `git diff --check` | **clean** |
| Harness size, for VM-14 | line count over `tools/` and `tests/phase_5_0_evidence` | **23,903 / 18,124** |

The harness figure of 1391 matches the September 10 independent baseline, and the
32 hashes match, so this review was performed against the same tree that review
saw. **Passing defect reproductions confirm the defect is open; they are not a
passed safety invariant.**

### H.1 Checks deliberately not run

* Bot, web and Foundry suites were not rerun. This review changed no product or
  harness source, so the September 10 figures — bot 2990 passed / 326 skipped;
  web 1610 passed / 1362 skipped; Foundry 171 passed — remain evidence of that
  tree, which is byte-identical to this one for every manifest-covered source.
  They are cited as history, not as results for this pass.
* No formatter, linter, type checker or `compileall` was run: no Python file
  changed in this pass.
* No manifest regeneration. No covered source changed, so no version increment
  applies and no digest was recomputed. The review-input digest
  `ec1e3e70b5d24aca911df9e4dcd394361ebffdb04b9587434cb74386756f2839` remains
  review input and **must not be passed to `--execute`**.

### H.2 Operational checks not performed, and not authorized

No SSH; no `oracle-test` synchronization; no host inspection or provisioning; no
KVM, libvirt, capacity or confinement probe; no VM allocation; no image build or
characterization boot; no dependency installation; no database operation; no
destructive drill; no service change; no credential access; no generated-vector
execution; no `--execute`; no armed real boundary or materializer. No stage,
commit, push, reset or history rewrite. **No test of the unimplemented VM design
exists, and none is claimed to pass.** Every libvirt statement in §B is a design
inference against primary documentation, not observed host behavior.

---

## I. Next bounded action, owner and checkpoint

**Next action.** Codex, as the proposal's author, prepares a revision of
`phase-5-0-evidence-vm-design.md` and ADR 0011 that answers VM-1 through VM-5
before any host question is put to Peter — specifically: name a management host
on which the controller can be the sole administrative principal, or withdraw the
exclusivity premise; re-derive the registry write path without it; pin the volume
key against the selected backend; reconcile §10's guest-root row with §8; and
correct the "disabled" claim in §9. Documentation only. No implementation, no
host inspection, no VM.

**Owner.** Codex. **Acceptance authority.** Peter Duscha.

**Checkpoint.** That revision returns for maintainer direction on §G, together
with this review's §F recommendation. Whether ADR 0011 is pursued at all is
Peter's decision, and §F recommends that Package 5.0's evidence work does not
wait for it.

**Stop point.** This handback ends the assignment. Neither this technical
recommendation nor a green local suite authorizes VM implementation,
provisioning or execution. ADR 0011 remains **Proposed** and is not accepted.
Package 5.0 remains **not ready**, P5.0-R5 **Blocking**, OD-62 **Open**,
EH-R16-1 **Open**, PR-20260910-1/2/3 **Open**, and the current plan
`is_executable=False`. No execution digest is approved. Migration `0014`,
production deployment, cutover and Package 5.1+ remain unauthorized.
