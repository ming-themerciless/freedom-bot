# Disposable Linux Test Server

**Restriction after D2-R2 acceptance and LD-9 decision, 2026-10-01 — design
accepted; no action on this server is authorized.** Peter Duscha accepted the
D2-R2 design and decided LD-9 option (i). `R4-D2-R1-1` is Closed as remediated
at the design level, but XD, T-L11, T-L12 and Codex's D9-2 independent decode
remain unimplemented and unperformed. A separate M-14/I-7 assignment is
required. No synchronization, inspection, build, test, verifier, controlled
write or other host command is authorized. PO-9 and PO-14 remain open; RP-11
remains unwired and unmet; neither pass is executable.
[Acceptance](../review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md).

**Restriction at D2-R2 remediation return, 2026-09-30 — the remediation was
returned documentation-only and issued no command to this server.** Nothing
was compiled, built, decoded, traced, inspected or executed, and no decoder
exists. Codex re-review is pending, and every prohibition below remains in
force. PO-9 and PO-14 remain open; RP-11 remains unwired and unmet, and
neither pass is executable.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md).

**Restriction at D2-R2 assignment, 2026-09-30 — documentation-only; no action
on this server is authorized.** Peter Duscha accepted LD-7's zero-`ret` design
and LD-8's conditional bound-root model. `R4-D2-R1-1` remains Open, Blocking,
and D2-R2 may amend documentation only. No synchronization, inspection, build,
test, verifier, controlled write or other host command is authorized. PO-9 and
PO-14 remain open; RP-11 remains unwired and unmet; neither pass is executable.
[Decision](../review/project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md).

**Restriction at D2-R1 static-launcher remediation return, 2026-09-29 —
the remediation was returned documentation-only and issued no command to this
server.** Nothing was compiled, built, traced, inspected or executed. The
amended hostile-environment experiment would need a disposable `x86_64` host,
unprivileged user and mount namespaces and separate authorization. None is
requested or granted. Codex re-review is pending, and every prohibition below
remains in force. PO-9 and PO-14 remain open; RP-11 remains unwired and unmet,
and neither pass is executable.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md).

**Restriction at LB-2S static-launcher design return, 2026-09-29 — the
design was returned documentation-only and issued no command to this
server.** Nothing was compiled, built, inspected or executed. The proposal's
later hostile-environment experiment would need a disposable `x86_64` host and
separate authorization; none is requested or granted. Codex review is pending,
and every prohibition below remains in force. PO-9 and PO-14 remain open;
RP-11 remains unwired and unmet, and neither pass is executable.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md).

**Restriction during the LB-2S static-launcher design, 2026-09-29 —
documentation-only; no action on this server is authorized.** M-14 authorizes
design only. M-9 conditionally selects LB-2S and M-10 records the threat scope;
they do not authorize compilation, installation, host inspection or a drill.
Every prohibition below remains in force. PO-9 and PO-14 remain open; RP-11
remains unwired and unmet, and neither pass is executable.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md).

**Restriction after R4-D1-R2 independent review, 2026-09-29 — no finding, but
no host authority is created.** The remediation is accepted as internally
reviewable design input only: no recommendation is ready, LB-2S depends on
M-9/M-14/M-10 and PO-9/PO-14, and no implementation is authorized. No command
was issued to this server. Every prohibition below remains in force; RP-11
remains unwired and unmet, and neither pass is executable.
[Review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-system-manager-environment.md).

**Restriction at R4-D1-R2 remediation return, 2026-09-29 — R4-D1-R2 was
returned documentation-only and issued no command to this server.** No SSH,
rsync, loader, interpreter, `systemctl`, `systemd-run`, polkit, `sudo` or hook
probe was made. The amended proposal's corrected boundary (LB-2S) would need a
compiled static image, separately authorized host provisioning on the
repository host, which is not this server, and a later authorized drill. None
is authorized. Codex re-review is pending, and every prohibition below remains
in force. RP-11 remains unwired and unmet; neither pass is executable.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md).

**Restriction during R4-D1-R2 remediation, 2026-09-29 — documentation-only;
no action on this server is authorized.** Claude may correct the LB-2
system-manager environment design and return it for independent review. No
loader, interpreter, systemd, hook, SSH or rsync probe may run. Every
prohibition below remains in force; RP-11 remains unwired and unmet, and
neither pass is executable.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md).

**Restriction after remediation re-review, 2026-09-29 — R4-D1-R1 retains one
Blocking design finding and requires further documentation remediation.** The
recommended LB-2 unit does not yet establish a closed pre-loader environment;
manager-level loader state could act before the entry's diagnostic check. No
command was issued to this server. Every prohibition below remains in force;
RP-11 remains unwired and unmet, and neither pass is executable.
[Review](../review/project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md).

**Restriction at remediation return, 2026-09-29 — R4-D1-R1 was returned
documentation-only and issued no command to this server.** No SSH, rsync, loader,
interpreter-entry, hook, `systemctl`, polkit or `sudo` probe was made. The
amended proposal's launch-boundary options would need separately authorized
host provisioning on the repository host, which is not this server, and none is
authorized. Codex re-review is pending; every prohibition below remains in
force. RP-11 remains unwired and unmet; neither pass is executable.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md).

**Restriction during remediation, 2026-09-29 — R4-D1-R1 is documentation-only.
It authorizes no action on this server and no loader, interpreter, hook, SSH or
rsync probe. R4-D1's two Blocking findings remain open pending independent
re-review. No SSH, rsync, synchronization, network or host inspection, `sudo`,
database access, provisioning, controlled write, reboot, verifier, evidence
band, harness `--execute`, real participant, real capture root, operational
path, protected-artifact access, secrets scan, commit or push is authorized.
RP-11 remains unwired and unmet; neither pass is executable;
`plan.is_executable=False`.**

**Restriction after independent review, 2026-09-29 — R4-D1 has two Blocking
design findings and requires repository-only documentation remediation. O-2
and D-1 are not ready for decision. No SSH, rsync, synchronization, network or
host inspection, `sudo`, database access, provisioning, controlled write,
reboot, verifier, evidence band, harness `--execute`, real participant, real
capture root, operational path, protected-artifact access, secrets scan,
commit or push is authorized. RP-11 remains unwired and unmet; neither pass is
executable; `plan.is_executable=False`.**

**Restriction at review return, 2026-09-29 — R4-D1 was returned
documentation-only and issued no host command.** Claude read repository files
only; no SSH, rsync, host, agent, socket, SSH configuration, known-hosts or
environment inspection was made and no hook was run against a real command.
Codex review is pending; every prohibition below remains in force. RP-11
remains unwired and unmet; neither pass is executable.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md).

**Restriction at assignment, 2026-09-29 — R4-D1 is documentation-only and creates no
host authority.** Claude may prepare the C-11 guard-preserving capture and
pinned launcher-environment proposal and handback, then must stop for Codex
review. No source, hook, manifest, artifact or wiring change is authorized.
**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.** RP-11
remains unwired and unmet; neither pass is executable; P5.0-R5 remains Blocking;
and Package 5.0 remains not ready.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md).

**Current restriction, 2026-09-29 — R3 accepted; no host authority is
created.** Peter Duscha accepted the bounded post-open descriptor-release
remediation after independent review with no finding. Manifest version 26 and
digest `526dd446…` are accepted review inputs only. **No SSH, rsync,
synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.** RP-11
remains unwired and unmet; neither pass is executable; P5.0-R5 remains Blocking;
and Package 5.0 remains not ready.
[Acceptance](../review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release-acceptance.md).

**Current restriction, 2026-09-29 — Codex reviewed R3 with no finding; no host
authority is created.** Independent repository-only verification reproduced 16
focused passes and **3364 passed, 0 skipped** at both the 1024 and default
descriptor limits, plus byte-identical harness dry-run artifacts at manifest
version 26 and digest `526dd446…`. Peter Duscha decides acceptance. **No SSH,
rsync, synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.** RP-11
remains unwired and unmet; neither pass is executable; P5.0-R5 remains Blocking;
and Package 5.0 remains not ready.
[Review](../review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release.md).

**Restriction at review return, 2026-09-29 — C-P5.0-R5-RP11-I1-R3-R3 was returned
repository-only and issued no host command.** Claude ran repository-local tests
only on this repository host, under pytest temporary directories with
`TEST_DATABASE_URL` unset; the soft descriptor limit was only **lowered**, to
1024 inside a subshell; artifacts were regenerated by harness dry run only.
Codex review was pending at that point; every prohibition below remained in force.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md).

**Restriction at assignment, 2026-09-29 — C-P5.0-R5-RP11-I1-R3-R3 is assigned
repository-only and creates no host authority.** Claude may repair the named
post-open descriptor leaks in `PosixFilesystem.create_file` and `openat`, add
focused regressions, advance the review manifest and regenerate artifacts by
harness dry run only. Codex is the independent reviewer. **No SSH, rsync,
synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.** RP-11
remains unwired and unmet; neither pass is executable; P5.0-R5 remains Blocking;
and Package 5.0 remains not ready.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-claude-prompt.md).

**Current restriction, 2026-09-29 — the RP-11 Option-1 alignment review is
accepted and creates no host authority.** Peter Duscha accepted Codex's
repository-only review with no finding and closed `RP11-I1-2`,
`RP11-I1-R2-1` and `RP11-I1-R1-1` as superseded. No SSH, synchronization,
network or host inspection, `sudo`, database access, provisioning, controlled
write, reboot, verifier, evidence band, harness `--execute`, real participant,
real capture root, protected-artifact access, secrets scan, commit or push
occurred or is authorized. RP-11 remains unwired and unmet; neither pass is
executable or authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking;
and Package 5.0 remains not ready.
[Acceptance record](../review/project-review-2026-09-29-p5-r5-rp11-option-1-alignment-acceptance.md).

**Current restriction, 2026-09-28 — the C-P5.0-R5-RP11-I1-R3-D2-DOC1-R1
correction was returned repository-only and issued no host command.** Claude
corrected documentation only, under Peter Duscha's instruction. It ran
repository-local tests only on this repository host, under pytest temporary
directories and with `TEST_DATABASE_URL` unset. The soft descriptor limit was
only **lowered**, to 1024 inside a subshell, and harness artifacts were
regenerated by dry run to scratchpad paths only. None of the actions listed
below occurred, no host authority is created, and every prohibition below
remains in force.
[Handback](../review/phase-5-0-p5-r5-rp11-i1-r3-d2-doc1-r1-alignment-review-remediation-handback.md).

**Restriction unchanged, 2026-09-28 — RP-11 Option 1 is decided; documentation
and exact-byte acceptance remediation remain repository-only.** Peter Duscha
accepted the metadata-only rule for exactly the recorded unadmitted
staging/final pair. Codex independently reviewed the descriptor-release
remediation with no new Blocking or Important finding. Repository-local tests
ran only on this repository host, under pytest temporary directories and with
`TEST_DATABASE_URL` unset; the soft descriptor limit was only **lowered**, to
1024 inside a subshell. **None of the following occurred:**

* SSH, rsync, synchronization, or network or host inspection;
* `sudo`, database access or provisioning;
* a controlled write, reboot, verifier or evidence band;
* harness `--execute` or real participant invocation;
* use of a real capture root or an operational path;
* protected-artifact access or a secrets scan.

No guard refused a call. The mechanism remains unwired and unaccepted. Neither
pass is executable or authorized, RP-11 remains unmet, **no host authority is
created**, and every prohibition below remains in force.
[Decision and review record](../review/project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md).

**Restriction unchanged, 2026-09-28 — C-P5.0-R5-RP11-I1-R3-R2 is assigned
repository-only and creates no host authority.** Claude may repair the local
`DurableRecordStore` descriptor-release defect, add synthetic regressions,
regenerate review artifacts by harness dry run only and run repository-local
tests with `TEST_DATABASE_URL` unset. **No SSH, rsync, synchronization, network
or host inspection, `sudo`, database access, provisioning, controlled write,
reboot, verifier, evidence band, harness `--execute`, real participant, real
capture root, operational path, protected-artifact access or secrets scan is
authorized.** The mechanism remains unwired; neither pass is executable or
authorized; RP-11 remains unmet; and every prohibition below remains in force.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-claude-prompt.md).

**Current restriction, 2026-09-28 — C-P5.0-R5-RP11-I1-R3-R1 was returned
repository-only and issued no host command.** Claude diagnosed the
whole-package descriptor-exhaustion discrepancy with local synthetic tests on
this repository host only, under pytest temporary directories and with
`TEST_DATABASE_URL` unset. The soft descriptor limit was only **lowered**, to
1024 inside a subshell, to reproduce the review. Claude also corrected the
proposed draft's state wording and prepared the unadmitted-pair decision
proposal. **None of the following occurred:**

* SSH, rsync, synchronization, or network or host inspection;
* `sudo`, database access or provisioning;
* a controlled write, reboot, verifier or evidence band;
* harness `--execute` or real participant invocation;
* use of a real capture root, a probe path or an operational path;
* protected-artifact access or a secrets scan.

No guard refused a call. The mechanism remains unwired. Independent Codex
re-review is mandatory. Neither pass is executable or authorized, RP-11
remains unmet, **no host authority is created**, and every prohibition below
remains in force.
[I1-R3-R1 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-handback.md).

**Restriction unchanged, 2026-09-28 — C-P5.0-R5-RP11-I1-R3-R1 is assigned
repository-only and creates no host authority.** Claude may diagnose the local
whole-package descriptor-exhaustion discrepancy, correct proposed-draft state
wording, prepare the unadmitted-pair decision proposal, make only narrowly
authorized repository remediations and run local synthetic tests with
`TEST_DATABASE_URL` unset. **No SSH, rsync, synchronization, network or host
inspection, `sudo`, database access, provisioning, controlled write, reboot,
verifier, evidence band, harness `--execute`, real participant, real capture
root, operational path, protected-artifact access or secrets scan is
authorized.** The mechanism remains unwired; neither pass is executable or
authorized; RP-11 remains unmet; and every prohibition below remains in force.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md).

**Current restriction, 2026-09-28 — C-P5.0-R5-RP11-I1-R3-I1 was repository-only
and issued no host command.** Claude returned the retained-alias amendment of
the proposed operational requirements and the unwired RP-11 source for
independent Codex review. It ran only under pytest temporary directories on
this repository host, with `TEST_DATABASE_URL` unset. **None of the following
occurred:**

* SSH, rsync, synchronization, or network or host inspection;
* `sudo`, database access or provisioning;
* a controlled write, reboot, verifier or evidence band;
* harness `--execute` or real participant invocation;
* use of a real capture root, a probe path or an operational path;
* protected-artifact access or a secrets scan.

No guard refused a call. The mechanism remains unwired, and the new review-input
manifest digest (`264674da…`) is not an approval. Neither pass is executable or
authorized, RP-11 remains unmet, **no host authority is created**, and every
prohibition below remains in force.
[I1-R3 handback](../review/phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-handback.md).

**Restriction unchanged, 2026-09-28 — C-P5.0-R5-RP11-I1-R3-I1 is assigned
repository-only and creates no host authority.** Claude may amend the proposed
operational requirements and unwired RP-11 source for retained staging/final
aliases, update focused tests and regenerate repository review artifacts. The
mechanism must remain unwired. **No SSH, rsync, synchronization, network or host
inspection, `sudo`, database access, provisioning, controlled write, reboot,
verifier, evidence band, harness `--execute`, real participant, real capture
root, operational path, protected-artifact access or secrets scan is
authorized.** Neither pass is executable or authorized, RP-11 remains unmet,
and every prohibition below remains in force.
[Assignment](../review/phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md).

**Current restriction, 2026-09-28 — the accepted RP-11 I1-R3 approach change
is repository-only and creates no host authority.** Peter Duscha accepted the
[publication redesign](../review/phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md)
that replaces the unreliable unnamed-inode/procfs route with named staging,
non-replacing hard-link publication and retained indexed aliases. No production
source, manifest or operational draft was changed. No test, SSH,
synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, capture root, operational probe,
protected-artifact access or secrets scan occurred. Neither pass is executable
or authorized, RP-11 remains unmet, and every prohibition below remains in
force. [Acceptance record](../review/project-review-2026-09-28-p5-r5-rp11-i1-r3-redesign-acceptance.md).

**Current restriction, 2026-09-28 — C-P5.0-R5-RP11-I1-R2 was repository-only
and issued no host command.** Claude corrected the test-only §9.5.4 capability
prototype and its evidence for the Important finding RP11-I1-R1-1. It ran only
under pytest temporary directories on this repository host. **None of the
following occurred:**

* SSH, rsync, synchronization, or network or host inspection;
* `sudo`, database access or provisioning;
* a controlled write, reboot, verifier or evidence band;
* harness `--execute` or real participant invocation;
* use of a real capture root, a probe path or an operational path;
* protected-artifact access.

No secrets scan was run, and no guard refused a call. The corrected
diagnostic now awaits independent Codex review. Neither pass is executable or
authorized, RP-11 remains unmet, and **no host authority is created**. Every
prohibition below remains in force.
[I1-R2 handback](../review/phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-handback.md).

**Restriction unchanged, 2026-09-28 — C-P5.0-R5-RP11-I1-R1 was repository-only
and issued no host command.** Claude returned the amended operational-evidence
draft (`186ff546…`, unaccepted) and a local portability diagnosis for
independent Codex review. The diagnosis ran only under pytest temporary
directories on this repository host. **No SSH, rsync, synchronization, network
or host inspection, `sudo`, database access, provisioning, controlled write,
reboot, verifier, evidence band, harness `--execute`, real participant
invocation, real capture root, operational path or protected-artifact access
occurred**, no secrets scan was run, and no guard refused a call. The proposed
§9.5.4 capability check chooses no operational location. Neither pass is
executable or authorized, RP-11 remains unmet, and **no host authority is
created**. Every prohibition below remains in force.
[I1-R1 handback](../review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md).

**Restriction unchanged, 2026-09-28 — C-P5.0-R5-RP11-I1-R1 is repository-only.**
Peter Duscha assigns the bounded
[publication-contract and portability remediation](../review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md).
Claude may amend the operational-evidence requirements, add narrowly necessary
repository-local diagnostic tests, create the handback and update current-state
pointers. It must not change RP-11 production source. Codex's
[review](../review/project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md)
found two Blocking issues and reproduced **991 passed, 179 failed, 0 skipped**
locally because `/proc/self/fd/N` publication returned `ENOENT` before genesis.
The remediation's capability check is bounded, disposable and cleanup-verified
and occurs before any real capture root or host command.

**No SSH, rsync, synchronization, network or host inspection, `sudo`, database
access, provisioning, controlled write, reboot, verifier, evidence band,
harness `--execute`, real participant invocation, real capture root,
protected-artifact access or secrets scan is authorized.** Neither pass is
executable or authorized, RP-11 remains unmet, and no host authority is
created. Every prohibition below remains in force.

**Restriction unchanged, 2026-09-28 — C-P5.0-R5-RP11-I1 was repository-only
and issued no host command.** Claude returned the RP-11 capture mechanism and
B0-RA retention check, implemented and tested locally under pytest temporary
directories only. **No SSH, rsync, synchronization, network or host inspection,
`sudo`, database access, provisioning, controlled write, reboot, verifier,
evidence band, harness `--execute`, real capture root or protected-artifact
access occurred**, no secrets scan was run, and no guard refused a call. The
mechanism is wired to no command. RP-11 remains unmet pending independent Codex
review. Neither pass is executable or authorized, and **no host authority is
created**. Every prohibition below remains in force.
[Implementation handback](../review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-RP11-I1 is repository-only.**
Claude may implement and locally test RP-11's client-side capture and B0-RA
retention mechanisms within the repository. **No SSH, rsync, synchronization,
network or host inspection, `sudo`, database access, provisioning, controlled
write, reboot, verifier, evidence band, harness `--execute`, real participant
invocation or protected-artifact access is authorized.** No real capture root
may be created, inspected or reused. The assignment does not mark RP-11
satisfied or authorize either operational pass; every host prohibition below
remains in force.
[Claude prompt](../review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-claude-prompt.md).

**Restriction unchanged, 2026-09-27 — R5 requirements remediation accepted;
no host authority.** Codex reviewed the exact R5-amended draft with no findings,
and Peter Duscha accepted C-P5.0-R5-OP1-R5 and closed OP1-R4-1 as remediated.
The acceptance is requirements-only. RP-11 remains absent and unmet, neither
pass is executable or authorized, and no RP-11 implementation has been
assigned. **No SSH, synchronization, inspection, provisioning, verifier,
suite, database access, controlled write, reboot, `--execute` or
protected-artifact access is authorized.** Every prohibition below remains in
force.
[Codex R5 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5.md);
[maintainer acceptance](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5-acceptance.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R5 was repository-only
and issued no host command.** Claude returned the R5-amended operational-evidence
draft and its handback for Codex review. The correction requires B0-RA, on the
**repository host**, to compare one complete recursive enumeration of Pass A's
retained capture root with the names Pass A's final state accounts for, in
both directions and with object types. Any absent, unexpected, mistyped,
duplicate, aliased or escaping name, or an incomplete comparison, stops Pass B
before it creates its own root or issues any host command. For unadmitted files
it verifies presence, name and type only, not content. It implements nothing,
tests nothing and inspects no capture root. **No SSH, synchronization,
inspection, provisioning, verifier, suite, database access, controlled write,
reboot or protected-artifact access occurred.** No secrets scan was run and no
guard refused a call. Neither pass is executable or authorized, and **no new
host authority is created**. Every prohibition below remains in force.
[R5-amended draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R5 handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-handback.md);
[Codex R4 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R5 is repository-only
unadmitted-retention remediation.** Claude may amend documentation only so
B0-RA checks retained names bidirectionally and fails closed when a name
recorded by Pass A's final state—including an unadmitted name—is absent or has
the wrong object type. Claude must not implement the check, SSH, synchronize,
inspect a host capture root, provision, invoke a verifier or suite, access a
database, perform a controlled write, reboot or access a protected historical
`/tmp` artifact. Neither pass is executable or authorized, and this assignment
creates no host authority.
[R5 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md);
[Codex R4 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R4 was repository-only
and issued no host command.** Claude returned the R4-amended operational-evidence
draft and its handback for Codex review. The correction adds a Pass B
admission step, B0-RA, on the **repository host**. Before Pass B creates its
own capture root or issues any host command, B0-RA verifies read-only that
Pass A's retained capture root and final index state still match the Pass A
handback. Any failure stops Pass B fail-closed. It implements nothing, tests
nothing and inspects no capture root. **No SSH, synchronization, inspection,
provisioning, verifier, suite, database access, controlled write, reboot or
protected-artifact access occurred.** No secrets scan was run and no guard
refused a call. Neither pass is executable or authorized, and **no new host
authority is created**. Every prohibition below remains in force.
[R4-amended draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R4 handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md);
[Codex R3 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R4 is repository-only
retention-verification remediation.** Claude may amend documentation only so
Pass B admission verifies, without mutation, that Pass A's retained capture
root and durable final index still match the Pass A handback. Claude must not
implement the check, SSH, synchronize, inspect a host capture root, provision,
invoke a verifier or suite, access a database, perform a controlled write,
reboot or access a protected historical `/tmp` artifact. Neither pass is
executable or authorized, and this assignment creates no host authority.
[R4 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md);
[Codex R3 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R3 was repository-only
and issued no host command.** Claude returned the R3-amended operational-evidence
draft and its handback for Codex review. The correction gives Pass A and Pass B
distinct, retained capture roots on the repository host and defines one ordered
stop transition, in which one local X-3 finalization attempt is the only write
before the capture root becomes read-only. It implements nothing, tests nothing
and creates no capture root or record. **No SSH, synchronization, inspection,
provisioning, verifier, suite, database access, controlled write, reboot or
protected-artifact access occurred.** No secrets scan was run and no guard
refused a call. Neither pass is executable or authorized, and **no new host
authority is created**. Every prohibition below remains in force.
[R3-amended draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R3 handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md);
[Codex R2 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R3 is repository-only
contract-consistency remediation.** Claude may amend documentation only to
give the two passes distinct retained capture roots and reconcile stop with
X-3 finalization and the read-only transition. Claude must not implement the
capture mechanism, SSH, synchronize, inspect, provision, invoke a verifier or
suite, access a database, perform a controlled write, reboot or access a
protected historical `/tmp` artifact. This assignment creates no host
authority.
[R3 assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md);
[Codex R2 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md).

**Restriction unchanged, 2026-09-27 — Codex R2 review requests two
repository-only contract corrections.** The review confirms the original
capture-durability omission is resolved in substance but finds that the two
passes need distinct retained capture roots and that stop/finalization ordering
must be made internally consistent. Neither pass is executable or authorized.
**No SSH, synchronization, inspection, provisioning, verifier, suite, database
access, controlled write, reboot or protected-artifact access is authorized.**
No new host authority is created.
[R2 review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R2 was repository-only
and issued no host command.** Claude returned the R2-amended operational-evidence
draft and its handback for Codex review. The correction states RP-11's
crash-consistent capture requirements only. It implements nothing, tests
nothing and creates no capture record. **No SSH, synchronization, inspection,
provisioning, verifier, suite, database access, controlled write, reboot or
protected-artifact access occurred.** No secrets scan was run and no guard
refused a call. Neither pass is executable or authorized, and **no new host
authority is created**. Every prohibition below remains in force.
[R2-amended draft](../review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md);
[R2 handback](../review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md);
[Codex R1 re-review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R2 is repository-only
capture-durability prompt remediation.** Codex found one remaining Blocking
requirements defect in RP-11. Claude may amend documentation only and must not
implement the capture mechanism, SSH, synchronize, inspect, provision, invoke
a verifier or suite, access a database, perform a controlled write, reboot or
access a protected historical `/tmp` artifact. This assignment creates no host
authority.
[Codex R1 re-review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md);
[R2 remediation assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md).

**Restriction unchanged, 2026-09-27 — C-P5.0-R5-OP1-R1 is repository-only
prompt remediation.** Codex requested changes to both passes of the returned
operational-evidence draft. Neither pass is authorized. Claude may amend
documentation only and must not SSH, synchronize, inspect, provision, invoke a
verifier or suite, access a database, perform a controlled write, reboot or
access a protected historical `/tmp` artifact. This assignment creates no host
authority.
[Codex review](../review/project-review-2026-09-27-p5-r5-operational-evidence-prompt.md);
[remediation assignment](../review/phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md).

**Restriction unchanged, 2026-09-22 — C-P5.0-R5-E1 was repository-only and
issued no host command.** No SSH, synchronization, inspection, verifier,
suite, database access or protected-artifact access occurred; no guard refused
a call. The reconciliation recommends, but does not authorize, future
disposable-host evidence (harness bands, a supervised reboot) and creates **no
new host authority**. Every prohibition below remains in force.
[Reconciliation handback](../review/phase-5-0-p5-r5-evidence-reconciliation-handback.md).

**Restriction unchanged, 2026-09-22 — C-P5.0-R5-E1 is a draft repository-only
evidence-reconciliation prompt.** It is not accepted, assigned or authorized and
creates no host authority. Do not SSH, synchronize, inspect, provision, invoke a
verifier or suite, access a database, perform a controlled write or access any
protected `/tmp` artifact.
[Draft prompt](../review/phase-5-0-p5-r5-evidence-reconciliation-claude-prompt.md).

**Restriction unchanged, 2026-09-22 — R6 findings disposed and I3 closed on R8
evidence.** R6 remains retained but inadmissible as gate evidence. The historical
`/tmp/fb-i3-r6-filelist.txt` remains protected and preserved; no cleanup, read,
inspection, `stat`, modification, move or reuse is authorized. This decision
creates no SSH, synchronization, inspection, verifier, suite, database or other
host authority.
[Decision record](../review/project-review-2026-09-22-r6-findings-and-i3-disposition.md).

**Restriction unchanged, 2026-09-22 — R8-R6 accepted and
LAB-I3-R8-D1-TABLE-1 closed.** This documentation decision creates no host
authority. The two R6 Blocking findings remain Open and I3 remains unconfirmed.
No SSH, synchronization, inspection, verifier invocation, suite, database
access or protected-artifact access is authorized.
[Acceptance record](../review/project-review-2026-09-22-reserved-laboratory-i3-r8-r6-acceptance.md).

**Restriction unchanged, 2026-09-22 — C-P5.0-LAB-I3-R8-R6 was repository-only
and issued no host command.** The repair and its follow-up changed only the
change-log table's Markdown structure and added two register rows. **No SSH, synchronization, inspection, verifier invocation,
suite or database access occurred.** The three protected `/tmp` artifacts were
not accessed. No secrets scan was run and no guard refused a call. R8-R5 is
accepted, so any lower note saying it awaits review records its historical
state only. **No new host authority is created.** Every prohibition below
remains in force.
[R8-R6 repair handback](../review/phase-5-0-reserved-laboratory-i3-r8-r6-change-log-table-structure-handback.md).

**Restriction unchanged, 2026-09-22 — R8-R5 accepted; R8-R6 remains draft.**
Peter Duscha closed LAB-I3-R8-R2-ROLLBACK-1 as remediated and wants no R8-R2
rollback. The draft R8-R6 change-log table repair creates no host authority.
Every prohibition below remains in force.

*Current-state note, 2026-09-22:* R8-R5 has returned and is consumed, awaiting
independent Codex review. Any lower banner saying R8-R5 is active, or naming one
of the five maintainer-disposed R8 findings as Open, records its historical
state only. No action on this host is authorized.

**Restriction unchanged, 2026-09-22 — C-P5.0-LAB-I3-R8-R5 was repository-only
and issued no host command.** The bounded remediation withdrew the R8-R2
handback's `git checkout --` rollback instruction as **unsafe** and its
exact-restoration claim as **unsupported** (**LAB-I3-R8-R2-ROLLBACK-1, Open,
Important**). **No SSH, synchronization, inspection, verifier invocation, suite
or database access occurred.** The three protected `/tmp` artifacts were **not
read, inspected, `stat`ed, written, moved, modified or reused**; this record
*refers* to them and to this restriction, which is not access to what it
protects. **No secrets scan was run and no command expected to engage a secrets
guard was issued**; **no guard or tool refused any call**; **no guard, hook or
rule was altered**; and the withdrawn command was **not executed** — no file was
reverted, deleted or restored. **No new host authority is created.** Every
prohibition below remains in force.
[R8-R5 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r5-r8-r2-rollback-safety-remediation-handback.md).

**Historical restriction, 2026-09-22 — R8-R4 review accepted; R8-R5 assigned
repository-only.** Peter Duscha closed five remediated R8 documentation and
evidence findings on their recorded terms and wants no R8-R3 rollback. This
decision issued no host command and creates no host authority.
**LAB-I3-R8-R2-ROLLBACK-1 remains Open, Important** under the active R8-R5
documentation remediation. Every prohibition below remains in force.
[Decision record](../review/project-review-2026-09-22-r8-r4-acceptance-and-r8-dispositions.md).

**Restriction unchanged, 2026-09-22 — C-P5.0-LAB-I3-R8-R4 was repository-only
and issued no host command.** The bounded remediation of Codex's re-review of
R8-R3 withdrew that handback's `git checkout --` rollback instruction as
**unsafe** and its exact-restoration claim as **unsupported**
(**LAB-I3-R8-R3-ROLLBACK-1, Open, Important**), and corrected its absolute "or
referenced" protected-artifact wording (**LAB-I3-R8-R3-WORDING-1, Open,
Optional**). **No SSH, synchronization, inspection, verifier invocation, suite
or database access occurred.** The three protected `/tmp` artifacts were **not
read, inspected, `stat`ed, written, moved, modified or reused**, and no artifact
content was added or inferred; this record *refers* to them and to this
restriction, which is not access to what it protects. **No new host authority is
created.** The withdrawn rollback command was **not executed**, no file was
reverted, deleted or restored, and no reverse patch was manufactured. **No
secrets scan was run and no command expected to engage a secrets guard was
issued**; **no guard or tool refused any call**; and **no guard, hook or rule was
altered**. It made **no measurement of any kind**: the R8, R8-R2 and R8-R3
recorded values stand exactly as recorded. Every prohibition in the restriction
that follows remains in force.
[R8-R4 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r4-rollback-safety-and-protected-artifact-wording-remediation-handback.md).

**Restriction unchanged, 2026-09-22 — C-P5.0-LAB-I3-R8-R3 was repository-only
and issued no host command.** The bounded remediation of Codex's re-review of
R8-R2 recorded the R8-R2 secrets-guard refusal as a **procedural violation**
(**LAB-I3-R8-R2-GUARD-1, Open, Blocking**, pending Peter Duscha's disposition)
and restated the candidate count in its actual units
(**LAB-I3-R8-R2-COUNT-1, Open, Important**). **No SSH, synchronization,
inspection, verifier invocation, suite or database access occurred**, the three
protected `/tmp` artifacts were not read, `stat`ed or changed, and **no new host
authority is created**. **No secrets scan was run and no command expected to
engage a secrets guard was issued**; the refused R8-R2 check was **not rerun or
reproduced through another tool**, and **no guard, hook or rule was altered**.
It made **no measurement of any kind**: the R8 and R8-R2 recorded values stand
exactly as recorded. Every prohibition in the restriction that follows remains
in force.
[R8-R3 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md).

**Restriction unchanged, 2026-09-22 — C-P5.0-LAB-I3-R8-R2 was repository-only
and issued no host command.** The bounded aggregate-precision remediation
withdrew the "accounted for by the calculation" overclaim from the R8 erratum,
the R8-R1 handback and the registers, recorded the historical cause
**unresolved**, and reconciled the candidate count under one explicit
convention. **No SSH, synchronization, inspection, verifier invocation, suite or
database access occurred**, the three protected `/tmp` artifacts were not read,
`stat`ed or changed, and **no new host authority is created**. Its
re-enumeration and digest reproduction were performed in the repository
workspace only; **no target-side value was measured or re-measured**, and the R8
target-side observations below stand exactly as recorded. Every prohibition in
the restriction that follows remains in force.
[R8-R2 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md).

**Restriction unchanged, 2026-09-21 — C-P5.0-LAB-I3-R8-R1 was repository-only
and issued no host command.** The bounded aggregate-explanation remediation
corrected R8 handback §3.3 in the repository and nothing else. **No SSH,
synchronization, inspection, verifier invocation, suite or database access
occurred**, the three protected `/tmp` artifacts were not read, `stat`ed or
changed, and **no new host authority is created**. Its common-formula
calculation was performed in the repository workspace only; **no target-side
value was measured or re-measured**, and the R8 target-side observations below
stand exactly as recorded. Every prohibition in the restriction that follows
remains in force.
[R8-R1 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r1-aggregate-remediation-handback.md).

**Current restriction, 2026-09-21 — the R8 pass is complete and consumed; NO
further action on this host is authorized.** The assigned C-P5.0-LAB-I3-R8 pass
ran **unbroken**: the exact plain §3.2 synchronization executed on its first
attempt, the read-only prerequisites were confirmed, and both verifier
invocations returned run status `verified` — root (T1 under V4, §2.3.3 under V5,
P2 under temporary canonical `R/bin`), then `ubuntu` (T6 under V9). All four
contexts verified, every tracked object `removed`, 0 barrier and 0 descriptor
failures, and both final surveys reported 0 `.fb-i3-verify-` names with
canonical `/var/lib/fb-evidence-p5-0` absent.

**No refusal or denial occurred**, no escalation or bypass parameter was
requested or used, and **no unauthorized host action or auxiliary artifact was
created**: no `scp`, `sftp` or second `rsync`; no file list, capture file,
redirection, wrapper, script or `/tmp` object; and no manual operator contact
with any verifier object. **The host's one operator-caused change is the
authorized synchronized repository worktree.**

**This host's state on the evidence of both clean surveys:** V1, V2, V3, V12,
V4, V9 and V5 provisioned as reviewed; V7 absent; canonical `R` absent; no
residue. The historical `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` remain **protected** — they were not read, `stat`ed
or changed by this pass and must not be read, deleted, truncated, overwritten,
moved, modified or reused.

**C-P5.0-LAB-I3-R8 is consumed.** Until fresh, explicitly bounded maintainer
authorization and assignment are recorded: **no SSH, synchronization,
inspection, `sudo`, controlled write, verifier invocation or retry.** I3 is
performed but remains unconfirmed and not closed; the two R6 Blocking findings
remain Open.
[R8 operational handback](../review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md).

**Superseded authorization, 2026-09-21 — C-P5.0-LAB-I3-R8 assigned to
Claude.** *Superseded by the banner above: the pass was performed and returned.
Its scope is retained as the authority the pass ran under.* Peter Duscha
authorizes only the exact accepted R8 prompt and assigns
Claude as implementing operator. The release is limited to the exact plain
§3.2 synchronization, necessary read-only prerequisite inspection, the exact
root verifier and—only after complete root success—the exact `ubuntu` verifier.
Any repository-guard or tool/harness permission denial consumes the pass; no
escalation, bypass, altered re-issuance or retry is permitted. No action outside
the prompt is authorized. Stop after handback for independent Codex review.
[Authorized R8 prompt](../review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

**Superseded restriction, 2026-09-21 — R8 prompt accepted but inactive; NO action
on this host is authorized.** Peter Duscha accepts the C-P5.0-LAB-I3-R8 prompt,
but has not authorized the pass or assigned Claude. Both are required in a
later explicit instruction before host action. Every existing prohibition and
protected `/tmp` evidence rule remains in force.
[Prompt acceptance](../review/project-review-2026-09-21-reserved-laboratory-i3-r8-prompt-acceptance.md).

**Superseded restriction, 2026-09-20 — R8 is draft and inactive; NO action on this
host is authorized.** A fresh C-P5.0-LAB-I3-R8 prompt is prepared by Codex for
maintainer acceptance. Prompt preparation is not operational authority.
Peter must later accept the prompt, explicitly authorize R8 and assign
Claude before any host action. R7 remains consumed. Every existing prohibition
and protected `/tmp` evidence rule remains in force.
[Draft R8 prompt](../review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

**Superseded restriction, 2026-09-20 — R7 is consumed; NO action on this host is
authorized.** Peter Duscha accepts Codex's independent R7-R2 review, closes the
three R7-R1/R2 documentation findings and accepts the recommendation that
**C-P5.0-LAB-I3-R7 is consumed**. This creates no host authority. Any future
operational pass requires fresh, explicitly bounded maintainer authorization
and assignment. Until then: no SSH, synchronization, inspection, `sudo`,
controlled write, verifier invocation or retry. The historical
`/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` remain protected and must not be accessed or
changed. I3 remains unconfirmed, and the two R6 Blocking findings remain Open.
[Acceptance record](../review/project-review-2026-09-20-reserved-laboratory-i3-r7-r2-acceptance.md).

**Superseded restriction, 2026-09-20 — a repository bookkeeping count was
corrected; NO action on this host is authorized.** The bounded,
repository-documentation-only C-P5.0-LAB-I3-R7-R2 remediation **issued no
command of any kind to this host**, and neither did the R7-R1 remediation or
the R7 pass before it. **This host was not contacted and is in exactly the
state the R6 record describes.**

That remediation corrected one figure in the R7-R1 handback and recorded
**PR-20260920-LAB-I3-R7-R2-1 — the R7-R1 handback understates its completed
working-tree count — Open, Important**, raised by Codex's independent
re-review. The corrected progression is **84 → 85 → 86 paths**, the completed
R7-R1 state being **86 paths (34 modified, 52 untracked)**. **This is a count of
paths in the repository checkout. It is not an execution digest, it says
nothing about this host, and it adds no evidence about it.** Every substantive
R7-R1 result stands: the §12 omission remains an uncured operational-process
deviation, the identity claim remains limited to the measured **50-file
review-input set**, the withdrawn claims stay withdrawn and every recorded hash
and the statement that **no target-side comparison exists** stay retained.

**Until Peter decides whether the R7 stop consumes C-P5.0-LAB-I3-R7 — a
decision he has not made, and which Codex's recommendation to treat it as
consumed does not make for him — every prohibition below stays in force: no
SSH, synchronization, inspection, `sudo`, controlled write, verifier invocation
or retry.** The historical `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` remain protected. PR-20260920-LAB-I3-R7-R1-1,
PR-20260920-LAB-I3-R7-R1-2 and PR-20260920-LAB-I3-R7-R2-1 remain Open,
Important; PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain Open,
Blocking; I3 remains unconfirmed.
[R7-R2 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r7-r2-count-remediation-handback.md).

**Superseded restriction, 2026-09-20 — documentation remediation returned; NO
action on this host is authorized.** *Superseded as the current banner by the
entry above; **its prohibitions are unchanged and remain fully in force**.* The
bounded, repository-documentation-only
C-P5.0-LAB-I3-R7-R1 remediation **issued no command of any kind to this host**,
and neither did the R7 pass it corrects. **This host was not contacted and is in
exactly the state the R6 record describes.**

The remediation added a dated erratum to the R7 stopped-pass handback recording
two Codex findings as **Open, Important**: **PR-20260920-LAB-I3-R7-R1-1**,
required implementation-plan §12 (Package 5.0) context was skipped on the
operational pass — an operator process deviation that later documentation work
does **not** cure; and **PR-20260920-LAB-I3-R7-R1-2**, the workspace identity
claim exceeded its measurement — the recorded aggregate covers the **50-file
review-input set** only, not the complete workspace and not every path the
repository-wide §3.2 synchronization would have transferred, so the "would have
carried" and whole-tree byte-for-byte claims are **withdrawn**. Every recorded
hash and the explicit statement that **no target-side comparison exists** are
retained. Neither finding is closed; only independent Codex re-review may close
them.

**Until Peter decides whether the R7 stop consumes C-P5.0-LAB-I3-R7 — a
decision he has not made, and which Codex's recommendation to treat it as
consumed does not make for him — every prohibition below stays in force: no
SSH, synchronization, inspection, `sudo`, controlled write, verifier invocation
or retry.** The historical `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` remain protected. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain Open, Blocking; I3 remains unconfirmed.
[Remediation handback](../review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md).

**Superseded restriction, 2026-09-20 — the R7 pass stopped before
synchronization; NO action on this host is authorized.** *Superseded as the
current banner by the entry above; its prohibitions are unchanged and remain
fully in force.* The assigned C-P5.0-LAB-I3-R7 pass
issued **no command of any kind** to this host. Its first synchronization
attempt was denied before execution by the Claude Code auto-mode permission
classifier over a tool-level `dangerouslyDisableSandbox` parameter the
authorization never named; **no repository guard refused it**, and the operator
stopped rather than re-issue it. **This host was not contacted and is in exactly
the state the R6 record describes.**

Until Peter decides whether that stop consumes R7: **no SSH, synchronization,
inspection, `sudo`, controlled write, verifier invocation or retry.** The
historical `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` remain protected — they must not be read, deleted,
truncated, overwritten, moved, modified or reused. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain Open, Blocking; I3 remains unconfirmed.
[Stopped-pass handback](../review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md).

**Superseded authorization, 2026-09-20 — C-P5.0-LAB-I3-R7 assigned to
Claude.** *Superseded by the banner above: the pass was attempted and stopped
before synchronization; whether this authority survives is Peter's decision.*
Peter Duscha authorizes Claude to perform exactly the R7 prompt: the
exact plain §3.2 synchronization as the first synchronization attempt,
necessary read-only prerequisite inspection, the exact root verifier and—only
after complete root success—the exact `ubuntu` verifier. Any guard refusal ends
the entire pass and consumes the authority. No auxiliary host-side artifact or
manual action on a verifier object is permitted. The historical
`/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` must not be read, deleted, truncated, overwritten,
moved, modified or reused. Stop after the handback for independent review.
[Authorized R7 prompt](../review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md).

**Superseded restriction, 2026-09-20 — R6-R2 accepted; R7 still NOT authorized;
NO action on this host is authorized.** Peter Duscha accepts the independently
reviewed R6-R2 documentation remediation and closes
PR-20260920-LAB-I3-R6-R1-1. That acceptance corrects a draft prompt only and
confers no host authority. C-P5.0-LAB-I3-R7 remains draft and inactive pending
a separate explicit authorization and operator assignment.

The restriction below remains fully in force: no SSH, synchronization,
inspection, `sudo`, controlled write, verifier invocation, retry or change to
any protected `/tmp` evidence artifact. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain Open, Blocking; I3 remains unconfirmed.

**Standing R6 state, 2026-09-20 — C-P5.0-LAB-I3-R6 not accepted; two Blocking
findings Open.** *Its blanket host prohibition is superseded only by the exact
bounded R7 authorization above; every action outside R7 remains prohibited.*
Independent
Codex review of the C-P5.0-LAB-I3-R6 pass does **not** recommend closing I3 and
raises two Blocking findings against how that pass was conducted on this host:
**PR-20260920-LAB-I3-R6-1**, execution continued after a mandatory guard stop —
the secrets-guard refusal of the first synchronization attempt ended the pass's
authority, and synchronization and both verifier invocations should never have
been issued; and **PR-20260920-LAB-I3-R6-2**, an unauthorized host write — the
`scp` that created `/tmp/fb-i3-r6-filelist.txt` was outside the R6 authority.
Both are **Open**.

**Standing restriction, except for the exact R7 actions above.** No other SSH
action, synchronization, inspection, `sudo`, creation under `/var/lib`,
capability change, controlled write, verifier invocation or retry.
**No `/tmp` evidence artifact may be deleted, truncated,
overwritten, moved or modified** — this now covers
`/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` **and
`/tmp/fb-i3-r6-filelist.txt`**, whose disposition is the maintainer's alone;
tidying it up would be a further unauthorized write. Do not read their contents.

**The host's physical state is as the R6 handback records it** and is not
disputed: canonical `/var/lib/fb-evidence-p5-0` absent, V7 absent, no
`.fb-i3-verify-` residue, and V1, V2, V3, V12, V4, V9 and V5 unchanged in
ownership, mode and inode (`1275049`–`1275052`). The R6 verifier runs **did
occur** and returned internally coherent `verified` results; **occurrence is not
acceptable gate evidence**, so I3 is **unconfirmed and not closed**.

**C-P5.0-LAB-I3-R6 is consumed and cannot be retried under its authority.** A
**draft, inactive** C-P5.0-LAB-I3-R7 prompt exists for one clean operational
pass; it is **not authorized** and confers no permission. A new pass requires
Peter Duscha's later explicit authorization and assignment after independent
Codex review of the C-P5.0-LAB-I3-R6-R1 remediation. V7 remains excluded;
V8/V10 unperformed; `plan.is_executable=False`; Package 5.0 not ready.
[R6-R1 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r6-r1-remediation-handback.md);
[draft R7 prompt — not authorized](../review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md).

**Superseded state and restriction, 2026-09-20 — C-P5.0-LAB-I3-R6 performed; no
further action authorized.** *Superseded by the banner above: the pass was not
accepted, two Blocking findings are Open, and `/tmp/fb-i3-r6-filelist.txt` is
now explicitly protected from deletion. Retained unaltered as the historical
record.* Claude executed the bounded I3 retry on this host.
Both authorized verifier invocations returned run status `verified` — root (T1
under V4, §2.3.3 under V5, P2 under temporary canonical `R/bin`) and then
`ubuntu` (T6 under V9). Each of the four contexts published one object, observed
it under both names with link count two and the pinned payload, and removed both
names under identity guards; every tracked object is `removed`, every barrier
and descriptor succeeded, and both surveys found **0** verifier names with
canonical `R` absent.

**This host is left provisioned and clean.** Canonical `/var/lib/fb-evidence-p5-0`
is absent, V7 is absent, no `.fb-i3-verify-` residue exists, and V1, V2, V3, V12,
V4, V9 and V5 are unchanged in ownership, mode and inode (`1275049`–`1275052`).
The directory mtimes of `laboratory`, `laboratory/runs` and `recovery` moved to
2026-09-20 18:53Z because entries were created and removed inside them; contents
are empty. The historical `/tmp/fb-i3-root.out` and `/tmp/fb-i3-root.err` are
unchanged, were not read, and **must still not be deleted, truncated,
overwritten or reused**. One operator artifact, `/tmp/fb-i3-r6-filelist.txt`
(2,210 bytes, `ubuntu:ubuntu`), was created unnecessarily, was never used and is
left for the maintainer; it is not verifier residue.

**C-P5.0-LAB-I3-R6 is consumed.** Until independent Codex review and a fresh
maintainer authorization: no SSH action, synchronization, inspection, creation
under `/var/lib`, capability change, controlled write, verifier invocation or
retry. I3 is **performed but not closed**; V7 remains excluded; V8/V10
unperformed; `plan.is_executable=False`; Package 5.0 not ready.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-verification-handback.md).

**Superseded authorization, 2026-09-20 — C-P5.0-LAB-I3-R6.**
Peter Duscha authorizes Claude as implementing operator for the bounded I3
retry. Claude may use only the exact accepted inline §3.2 synchronization,
necessary read-only prerequisite inspection, the reviewed root verifier
invocation and—only after complete root success—the reviewed `ubuntu`
invocation. The historical `/tmp/fb-i3-root.out` and
`/tmp/fb-i3-root.err` files must not be deleted, truncated, overwritten or
reused. Stop on every mismatch, refusal, residue, nonzero exit, incomplete
context or unexpected output; do not repair or retry. No database, V7,
participant, harness, generated vector, service change, provisioning,
permission change, V8, V10, real boundary/materializer, `--execute` or
production action is authorized. I3 remains unconfirmed until evidence is
independently reviewed; `plan.is_executable=False`; Package 5.0 not ready.
[Authorized prompt](../review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-retry-claude-prompt.md).

**Superseded restriction, 2026-09-20 — R5 accepted; R6 prompt prepared but not
authorized.** Peter accepted the repository reconciliation, but operational
authority had not yet been issued at this point.

**Superseded restriction, 2026-09-20 — target identity Option A implemented;
still repository-only.** C-P5.0-LAB-I3-R5 reconciled the approved target facts,
I3 admission, runner contract r6, the review manifest (version 17) and both
generated artifacts in the repository, and has returned for independent Codex
technical and security review. **Nothing was done on this host, and no action on
it is authorized:** no SSH, synchronization, inspection, deletion of
`/tmp/fb-i3-root.out` or `/tmp/fb-i3-root.err`, creation under `/var/lib`,
capability change, controlled write, verifier invocation or retry. The two
`/tmp` files remain in place as evidence artifacts and must not be deleted. The
review-input digest for the reconciled tree is `c358ea8b…`; the previously
accepted `be9e110f…` does not describe it, and neither is authority. I3 remains
unconfirmed and unperformed, V7 excluded, V8/V10 unperformed,
`plan.is_executable=False`, and Package 5.0 not ready.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r5-target-identity-handback.md).

**Superseded restriction, 2026-09-20 — target identity Option A decided;
repository reconciliation only.** Peter Duscha has chosen to keep
`oracle-test` as the operational SSH alias and separately approve kernel
nodename `Test`. C-P5.0-LAB-I3-R5 authorizes repository reconciliation and
independent review only. **No action on this host is authorized:** no SSH,
synchronization, inspection, deletion of `/tmp/fb-i3-root.out` or
`/tmp/fb-i3-root.err`, verifier invocation, controlled write or retry. I3
remains unconfirmed, V7 excluded, V8/V10 unperformed,
`plan.is_executable=False`, and Package 5.0 not ready.
[Decision](../review/project-review-2026-09-20-reserved-laboratory-i3-target-identity-decision.md).

**Superseded restriction, 2026-09-20 — I3 verification refused before the first
controlled write; no verifier-controlled mutation, and no authority in force.**
Under C-P5.0-LAB-I3-R4 Claude synchronized this host with the exact accepted
inline §3.2 command, performed read-only prerequisite inspection, and ran the
armed I3 verifier's root invocation. **It refused admission with
`target-mismatch` at exit `4`; the verifier performed no controlled write and
created no verifier object**, and the `ubuntu` invocation was not run. The
cause is a naming divergence: this host's kernel nodename is `Test`, while
`APPROVED_TARGET_FACTS.host` is the SSH alias `oracle-test`. Kernel release
`7.0.0-31-generic` and architecture `x86_64` matched. Every prerequisite was
observed unchanged — V1, V2, V3, V12, V4, V9 and V5 provisioned; V7 absent;
canonical `R` absent; no `.fb-i3-verify-` residue; `protected_hardlinks=1` —
and no reviewed object was created, removed or altered. The pass's two
disclosed effects on this host are the authorized synchronization, which
updated the repository worktree at `/opt/freedom-blades/platform`, and the
operator's output redirection, which created `/tmp/fb-i3-root.out` and
`/tmp/fb-i3-root.err`. Those two files remain in place as evidence artifacts
outside canonical `R` and the four publication directories; they are **not
verifier residue** and must not be deleted under the current restriction.
C-P5.0-LAB-I3-R4 is **consumed**. Wording corrected by C-P5.0-LAB-I3-R4-E1;
the result and this restriction are unchanged. Until a maintainer decides the target-identity
question (RAID LAB-I3-TARGET-1) and issues a new authorization: no SSH,
synchronization, inspection, creation under `/var/lib`, capability change,
controlled write or verifier invocation. I3 remains unconfirmed, V7 excluded,
V8/V10 unperformed, `plan.is_executable=False`, and Package 5.0 not ready.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r4-controlled-write-blocker-handback.md).

**Superseded restriction, 2026-09-20 — mode reconciliation accepted; fresh
operational authority pending.** Peter accepts the independent review of
C-P5.0-LAB-I3-R3 with no finding. This acceptance closes the repository review
but releases no host action. The single next step is a fresh, explicit,
bounded authorization for Claude to run the separately armed I3 verifier in
the reviewed root and `ubuntu` invocations; the superseded 2026-09-19 authority
is consumed and cannot be reused. Until that release: no SSH, synchronization,
inspection, creation under `/var/lib`, capability change, controlled write or
verifier invocation. I3 remains unconfirmed, V7 excluded, V8/V10 unperformed,
`plan.is_executable=False`, and Package 5.0 not ready. [Acceptance](../review/project-review-2026-09-20-reserved-laboratory-i3-r3-mode-reconciliation-acceptance.md).

**Superseded restriction, 2026-09-20 — mode reconciliation implemented; still
repository-only.** C-P5.0-LAB-I3-R3 reconciled the two accepted mode rulings
in the repository — canonical `R` created `root:root 0700`, P2's temporary
`0500` through an explicit creation-mode input whose default remains `0600` for
T1, T6 and §2.3.3, and P2 still `root:root 0555` before publication — and has
returned for fresh independent Codex technical and security review. **Nothing
was done on this host, and no action on it is authorized:** no SSH,
synchronization, inspection, creation under `/var/lib`, capability change,
controlled write or verifier invocation. I3 remains unconfirmed, V7 excluded,
V8/V10 unperformed, `plan.is_executable=False`, and Package 5.0 not ready.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r3-mode-reconciliation-handback.md).

**Superseded restriction, 2026-09-19 — P2/I3 decision made; repository
remediation only.** Peter Duscha has ruled P2 `root:root 0555`, using the
protected-hardlink filesystem-UID owner condition rather than `CAP_FOWNER`, and
has narrowly allowed the future armed verifier to create temporary canonical
`R`/`R/bin` topology. The contract, implementation, tests and generated
artifacts have not yet been reconciled or independently reviewed. Therefore no
action on `oracle-test` is authorized: no SSH, synchronization, inspection,
creation under `/var/lib`, capability change, controlled write or verifier
invocation. I3 remains unconfirmed, V7 excluded, V8/V10 unperformed,
`plan.is_executable=False`, and Package 5.0 not ready. [Decision
review](../review/project-review-2026-09-19-reserved-laboratory-i3-r1-decision-handback.md).

**Consumed authorization, 2026-09-19 — bounded I3 verification assigned to
Claude.** The earlier assignment stopped before implementation under its stop
clause. Its P2/`CAP_FOWNER` premise is superseded by the ruling above and it
authorizes no further host action.

**Current state, 2026-09-18 — prerequisite subset applied; host provisioned and
fail-closed.** All seven released items — V1, V2, V3, V12, V4, V9, V5 — were applied on `oracle-test` in exact order on 2026-09-18 (22:06–22:07Z), and the read-only I12/V6 verification observed every object matching its reviewed definition. `freedomlab` is gid 986 with `ubuntu` appended (five prior groups retained); the V3 fragment is byte-exact and `systemd-tmpfiles` created `/run/freedom-blades` `0750` and the lock `0660`, both `root:freedomlab`; the provisioning CLI exited 0 with V12, V4, V9, V5 `created` at `2049:1275049`–`1275052`, no refusal, nothing unattempted and no residue. `lifecycle.json` and `.tmp` are absent. LAB-V6-P3 and V6 were closed on 2026-09-19, and the one-time `--exclude-from` deviation was accepted retrospectively for R4 only. Future synchronization must use the accepted inline runbook command. I3 remains unconfirmed; V8 and V10 are unperformed; V7 is excluded and absent; `is_executable=False`; LAB-V6-P2 is deferred; Package 5.0 is **not ready**. [Operational handback](../review/phase-5-0-reserved-laboratory-v6-p-r4-operational-provisioning-handback.md).

Objects now present: group `freedomlab` (gid 986, member `ubuntu`); `/etc/tmpfiles.d/freedom-blades-laboratory.conf`; `/run/freedom-blades` and `laboratory.lock`; `/var/lib/freedom-blades` with `laboratory`, `laboratory/runs` and `recovery`. The C-P5.0-LAB-V6-P-R4 authorization below is **consumed**; no further host action is authorized until review and maintainer direction.

**Consumed authorization, 2026-09-18 — reviewed prerequisite-provisioning retry
released.** Peter accepts Codex's R3 independent review with no finding, closes
PR-20260918-LAB-V6P-R2-1 and LAB-V6-P1, and authorizes
**C-P5.0-LAB-V6-P-R4**. Claude is the implementing operator and may safely
synchronize and inspect `oracle-test`, then apply **V1, V2, V3, V12, V4, V9
and V5 in that exact order**, using the reviewed provisioning CLI for the four
directory items, followed only by read-only I12/V6 verification. Stop on any
refusal, discrepancy, unexpected precondition, unclassified result or residue
and return evidence for independent Codex review.

This does not authorize V7, I3, V8, V10, database access, participant wiring or
invocation, generated-vector execution, the evidence harness, a real boundary
or materializer, or `--execute`. `plan.is_executable` remains false,
`reservation.REAL_EXECUTION_REFUSAL` remains unconditional, LAB-V6-P2 remains
Open and deferred, and Package 5.0 remains not ready. This banner supersedes
the repository-only 2026-09-18 restriction immediately below.

**Superseded restriction, 2026-09-18 — provisioning entry-point implementation
only; this host remains untouched.** Peter authorizes
**C-P5.0-LAB-V6-P-R1**, a bounded repository-local Claude pass adding the
missing dedicated operator CLI over the reviewed directory provisioner. This
does **not** release any action on `oracle-test`: no SSH, synchronization,
inspection, provisioning, permission/group change, `systemd-tmpfiles`,
database operation, controlled write verification, generated-vector execution,
participant, real boundary/materializer or `--execute`. The implementation
must receive independent Codex technical and security review before Peter may
separately release an operational retry. LAB-V6-P1 remains Open; LAB-V6-P2 is
deferred; V6 remains performed-but-not-closed, I3 unconfirmed, V7 excluded,
V8/V10/I12 unperformed, `is_executable=False`, and Package 5.0 not ready.

**Prior state, 2026-09-17 — provisioning pass stopped before mutation; this
host is still untouched.** Claude performed the **C-P5.0-LAB-V6-P** pass under
the authorization below and **applied nothing**. No group, no membership, no
edit under `/etc`, nothing created under `/run`, `/var/lib` or
`/opt/freedom-blades`, no `systemd-tmpfiles`, no link, no controlled write
verification, no database operation, no generated vector, no real participant,
no boundary or materializer and no `--execute`. No synchronization was
performed. The
[handback](../review/phase-5-0-reserved-laboratory-v6-p-provisioning-blocker-handback.md)
is returned for independent Codex technical and security review.

**Why it stopped.** The repository has **no already reviewed operator
invocation** that can drive the directory provisioner as approved — no `main`
or `__main__` in `tools/phase_5_0_evidence/execution/provisioner.py`, no
provisioning subcommand in the harness CLI, and no reference to it outside the
module except the test suite's armed construction over a temporary directory
with a fake account lookup. The assignment's application rules require a stop
rather than adding source or inventing an entry point. RAID item **LAB-V6-P1**.

**Observed read-only, and recorded as pre-application facts only.** All seven
released items **absent**: `freedomlab` resolves to zero records,
`/etc/tmpfiles.d/freedom-blades-laboratory.conf` and both `/run` objects are
absent, and `/var/lib/freedom-blades` and all three of its children are absent.
`ubuntu` still holds exactly the five supplementary groups V6 observed —
`adm`, `cdrom`, `sudo`, `dip`, `lxd`. `/var/lib` is a real directory,
`root:root 0755`, `dev=2049 ino=97831`, on the ext4 root mount, with no group-
or other-write bit. Both `lifecycle.json` and `lifecycle.json.tmp` are absent.
`/opt/freedom-blades` is unchanged at `1001:1001 0755` and
`/opt/freedom-blades/evidence` is absent. Canonical
`R = /var/lib/fb-evidence-p5-0` is absent. **The repository tree on this host
is stale (5 September) and does not contain the applier**, so the pass that
does apply must synchronize under §3.2 first.

**The I12/V6 verification was not performed**; its rows need the provisioned
objects. `protected_hardlinks=1` and the observing `ubuntu` identity and
capability masks were read as ambient context and are **not** verification
rows. **I3 remains unconfirmed — no link was created.** V6 remains performed
2026-09-16 and not closed; V7 excluded; V8, V10 and I12 unperformed;
`is_executable=False`; Package 5.0 not ready.

**Note on the banners below.** The 2026-09-17 authorization banner and the
2026-09-17 restriction banner that follows it are both labelled *current* and
disagree about SSH, synchronization and provisioning. The authorization is the
later maintainer act and is what this pass worked under, performing only
read-only inspection within it. The overlap is a documentation defect for a
maintainer to reconcile; it was not resolved by an implementer.

**Consumed authorization, 2026-09-17 — Claude assigned reviewed prerequisite
provisioning and read-only verification.** Peter assigns **Claude as
implementing operator** and authorizes the necessary safe synchronization,
inspection and administrative application on this host of **V1, V2, V3, V12,
V4, V9 and V5, in that order**, followed only by the read-only I12/V6
verification. **Codex remains the Independent Reviewer and does not perform the
operation. V7, the I3 controlled-write test, participant wiring, database
access, generated-vector execution, a real participant, the evidence harness,
a real boundary/materializer and `--execute` remain unauthorized.** Stop after
returning evidence for independent Codex review.

**Prior restriction, 2026-09-17 — r6 topology-contract correction accepted;
host still untouched.** Peter accepted Codex's independent
[re-review](../review/project-review-2026-09-17-reserved-laboratory-v6-d-r1-contract-correction.md)
with no finding and closed PR-20260917-LAB-V6D-R1-1. This acceptance grants no
host authority. Repository-local work with `TEST_DATABASE_URL` unset only
remains authorized; **no SSH, synchronization, inspection, provisioning,
permission change, database operation, controlled write verification,
generated-vector execution, real participant or `--execute`**. V6 remains
performed-but-not-closed, I3 unconfirmed, V7 excluded, V8/V10/I12 unperformed,
`is_executable=False`, and Package 5.0 not ready.

**Prior restriction, 2026-09-17 — r6 contract topology correction; this host
is still untouched.** Claude completed **C-P5.0-LAB-V6-D-R1**, one bounded
repository-local documentation correction of Codex Blocking
PR-20260917-LAB-V6D-R1-1, and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-d-r1-contract-correction-handback.md)
for independent Codex re-review. Runner contract r6 §1.3.3 now defines
`R = /var/lib/fb-evidence-p5-0` with D1 on its parent `/var/lib`, and §7's V6
row observes only the canonical locations and records V6 as **performed
2026-09-16 and not closed**. **No source file changed and no artifact was
regenerated.** The restriction below is unchanged and still in force: repository
changes and local tests with `TEST_DATABASE_URL` unset only, and **no SSH,
synchronization, inspection, provisioning, permission change, database
operation, controlled write verification, generated-vector execution, real
participant or `--execute`.**

**Prior restriction, 2026-09-17 — topology decisions approved; repository
remediation only.** Peter accepted R4 and decided LAB-V6-1 through LAB-V6-3:
V11 and `/opt/freedom-blades/evidence` are withdrawn,
`/var/lib/fb-evidence-p5-0` is canonical `R`, and V12 defines persistent
`/var/lib/freedom-blades` as `root:root 0755`. Production `EVIDENCE_ROLE`
registration remains deferred. This authorizes repository changes and local
tests with `TEST_DATABASE_URL` unset only. **This host remains untouched:** no
SSH, synchronization, inspection, provisioning, permission change, database
operation, controlled write verification, generated-vector execution, real
participant or `--execute`.

This document defines the operational profile, access method, and execution instructions for the dedicated disposable Linux test environment.

**Prior restriction, 2026-09-16 — verification and reversal finalization
repaired in the repository; this host is still untouched.** Claude completed
**C-P5.0-LAB-V6-R4**, one bounded repository-local remediation of Codex Blocking
finding PR-20260916-LAB-V6R3-1, and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-r4-verification-rollback-handback.md)
for independent Codex technical and security re-review.

The four bare `os.close` calls the R3 pass reported and left are gone. **No
release anywhere in `tools/phase_5_0_evidence/execution/provisioner.py` is a bare
close any more**: `_release` is the one function that calls `os.close` at all, it
calls it once, and it reports instead of raising.

`verify()` — the read-only V6 re-observation — now returns **one observation for
every target** even when a descriptor will not release; the release is an
appended `descriptor-not-released` discrepancy that never displaces what was
observed about the object, and the later targets are still observed. The same
condition through an idempotent `ensure()` is a closed refusal carrying the
`already-provisioned` item exactly once, with `created` empty and nothing
written. Guarded rollback refuses **before** an effect: a descriptor that will
not release before the `rmdir` means nothing is removed and the object is still
this application's to reverse. Where `rmdir` succeeded and the parent descriptor
then failed, the removal is reported as real, the object leaves the live created
account exactly once, and a second reversal cannot aim at it.

**Nothing was applied to this host and nothing may be applied yet.** No SSH, no
synchronization, no inspection, no `sudo`, no user or group creation, no edit
under `/etc`, nothing created under `/run` or `/var/lib` or
`/opt/freedom-blades`, no `systemd-tmpfiles`, no link, no controlled write
verification, no database operation, no generated-vector execution, no real
participant, no boundary or materializer and no `--execute`.

**LAB-V6-1, LAB-V6-2 and LAB-V6-3 are unchanged and remain maintainer stop
conditions**, so **V11 must remain unapplied**. **V7 remains excluded** and a
provisioned host with no lifecycle record refuses all seven participants. V6
remains **performed but not closed**, I3 unconfirmed, V8 and V10 unperformed,
`is_executable` False, Package 5.0 not ready.

**Prior restriction, 2026-09-16 — descriptor finalization repaired in the
repository; this host is still untouched.** Claude completed
**C-P5.0-LAB-V6-R3**, one bounded repository-local remediation of Codex Blocking
finding PR-20260916-LAB-V6R2-1, and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-r3-descriptor-finalization-handback.md)
for independent Codex technical and security re-review.

`tools/phase_5_0_evidence/execution/provisioner.py` no longer lets a failing
`close()` out of the application path, and no longer lets one **replace** the
refusal it was unwinding. All three descriptors it holds — the created object's
and the parent's synchronizable and traversal descriptors — are released through
one helper that reports instead of raising. A release failure with nothing else
in flight is the closed refusal `descriptor-not-released`, carrying the object
**exactly once** with the identity its read-back established, so guarded
rollback survives; a release failure while an ownership, mode, read-back,
barrier or parent refusal is unwinding leaves that refusal exactly as it was.
An ambiguous `close()` is treated as ambiguous: the descriptor is neither reused
nor closed again, and **no leak is claimed either way**.

**Two release sites are reported and deliberately unchanged** — `_verify_one`,
used by `verify()` and the already-provisioned path, and `_remove`, used by
guarded rollback. Both sit outside the window the finding governs and both can
still raise; scoping them is a maintainer's decision, not an implementer's.

**Nothing was applied to this host and nothing may be applied yet.** No SSH, no
synchronization, no inspection, no `sudo`, no user or group creation, no edit
under `/etc`, nothing created under `/run` or `/var/lib` or
`/opt/freedom-blades`, no `systemd-tmpfiles`, no link, no controlled write
verification, no database operation, no generated-vector execution, no real
participant, no boundary or materializer and no `--execute`. Peter's approval of
the prerequisite subset applies only after independent review accepts the
returned contract and code.

**LAB-V6-1, LAB-V6-2 and LAB-V6-3 are unchanged and remain maintainer stop
conditions**, so **V11 must remain unapplied**: `/opt/freedom-blades` is
`1001:1001 0755`, `/var/lib/freedom-blades` is absent with no item defining it,
and r6's `R` is unreconciled with the approved target root. **V7 remains
excluded** and a provisioned host with no lifecycle record refuses all seven
participants, which is the intended fail-closed state.

V6 remains **performed but not closed**, I3 unconfirmed, V8 and V10 unperformed,
`is_executable` False, Package 5.0 not ready.

**Prior restriction, 2026-09-16 — post-creation accounting repaired in the
repository; this host is still untouched.** Claude completed
**C-P5.0-LAB-V6-R2**, one bounded repository-local remediation of Codex Blocking
finding PR-20260916-LAB-V6R1-1, and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-r2-partial-state-handback.md)
for independent Codex technical and security re-review.

`tools/phase_5_0_evidence/execution/provisioner.py` no longer lets an ordinary
`OSError` out of the window between a successful `mkdirat` and the parent's
barrier, and no longer reports that nothing was created while a directory it
created sits at the target. Each of the six post-creation failure points is a
closed refusal that carries the object it left; an object whose identity could
never be established is reported as residue and **guarded rollback refuses the
whole reversal** while one is present.

**Nothing was applied to this host and nothing may be applied yet.** No SSH, no
synchronization, no inspection, no `sudo`, no user or group creation, no edit
under `/etc`, nothing created under `/run` or `/var/lib` or
`/opt/freedom-blades`, no `systemd-tmpfiles`, no link, no controlled write
verification, no database operation, no generated-vector execution, no real
participant, no boundary or materializer and no `--execute`. Peter's approval of
the prerequisite subset applies only after independent review accepts the
returned contract and code.

**LAB-V6-1, LAB-V6-2 and LAB-V6-3 are unchanged and remain maintainer stop
conditions**, so **V11 must remain unapplied**: `/opt/freedom-blades` is
`1001:1001 0755`, `/var/lib/freedom-blades` is absent with no item defining it,
and r6's `R` is unreconciled with the approved target root. **V7 remains
excluded** and a provisioned host with no lifecycle record refuses all seven
participants, which is the intended fail-closed state.

V6 remains **performed but not closed**, I3 unconfirmed, V8 and V10 unperformed,
`is_executable` False, Package 5.0 not ready.

**Prior restriction, 2026-09-16 — V6 provisioning contract completed in the
repository; this host is still untouched.** Claude completed
**C-P5.0-LAB-V6-R1**, one bounded repository-local remediation, and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-provisioning-remediation-handback.md)
for independent Codex technical and security review.

The r6 §7 delta is now **eleven items**: `/opt/freedom-blades/evidence`, which
V6 found absent and which r6 described only as "root-only [A]", is stated
exactly as **V11, `0700 root:root`**, with its creation mechanism, persistence,
verification and rollback. `tools/phase_5_0_evidence/execution/provisioner.py`
is the applier for the four directory items, and
`provisioning.VERIFICATION_PROCEDURE` is the read-only post-provision V6
re-observation.

**Nothing was applied to this host and nothing may be applied yet.** No SSH, no
synchronization, no inspection, no `sudo`, no user or group creation, no edit
under `/etc`, nothing created under `/run` or `/var/lib` or
`/opt/freedom-blades`, no `systemd-tmpfiles`, no link, no controlled write
verification, no database operation, no generated-vector execution, no real
participant, no boundary or materializer and no `--execute`. Peter's approval of
the prerequisite subset applies only after that independent review accepts the
returned contract and code.

**Two things a reader of the new delta must not miss.** **V7 is excluded**: the
lifecycle record is not initialized, because its `linkat` is the first real
exclusive publication here and **I3** is unconfirmed — a provisioned host with
no record refuses all seven participants, and that is the intended fail-closed
state. And **`/opt/freedom-blades` was observed `1001:1001 0755`**, so `ubuntu`
can rename or unlink the `evidence` entry whatever mode V11 sets; the applier
refuses to provision under it, and resolving that is a maintainer decision.
`/var/lib/freedom-blades` is absent and no item defines it, which refuses V4 and
V5 the same way.

V6 remains **performed but not closed**, I3 unconfirmed, V8 and V10 unperformed,
`is_executable` False, Package 5.0 not ready.

**Prior restriction, 2026-09-16 — V6 survey complete; no execution release.**
Peter accepted the independent D12-R1 re-review, closed
PR-20260915-LAB-D12-1 and released the queued V6 read-only prerequisite survey.
The [dated record](../review/project-review-2026-09-16-reserved-laboratory-d12-r1-acceptance-and-v6-preflight.md)
reports its result. V6 was performed but does not close: the exact publication
paths and proposed `freedomlab` group are absent, so their target ownership/mode
assumptions cannot be confirmed. It does not prove real `linkat` viability and
I3 remains unconfirmed. No synchronization, provisioning, permission/group
change, link creation, database operation, generated-vector execution, real
participant, boundary/materializer or `--execute` is authorized. V8 and V10
remain unperformed. Further host mutation or controlled write verification
requires separate maintainer authorization.

**Prior restriction, 2026-09-15 — preflight authorized but not yet released.**
Peter authorizes V6 as a read-only prerequisite survey, but the preflight
remains queued behind remediation and independent re-review of Blocking
PR-20260915-LAB-D12-1. It does not prove `linkat` viability or close I3. Until
that review accepts the remediation, SSH, synchronization and host inspection
remain out of scope. Provisioning, permission or group changes,
`systemd-tmpfiles`, database operations, generated-vector execution, real
participant invocation, real boundary/materializer use and `--execute` remain
unauthorized in every case. No item of the r6 §7 delta is provisioned, no
reservation is claimed and this host must remain untouched until the document
checkpoint closes. See
the active [handover](../review/Handover%20information) and
[Codex re-review](../review/project-review-2026-09-15-reserved-laboratory-one-shot-authority.md).

**Prior state, 2026-09-14 — the mechanism is wired in the repository; this
host is still untouched.** The C-P5.0-LAB-I-R1 remediation is
[returned for independent re-review](../review/phase-5-0-reserved-laboratory-implementation-remediation-handback.md).
Reservation enforcement now has a repository-owned integration point for all
seven participants — `tools/phase_5_0_evidence/execution/participants.py` — and
the harness CLI's `--execute` branch assembles it. **Nothing here is enforced by
any of that**, for two separate reasons, and both matter:

* **the six non-harness participants are not wired to it.** The bot suite, the
  web suite, the Foundry tests, §3.2 synchronization, §3.5 dependency updates
  and §4 environment reset run exactly as they do today. Connecting them is a
  follow-up authorization, and RAID item **LAB-R6** records why it must not
  precede provisioning: an integration point refuses on an absent lock, so
  wiring it on an unprovisioned host would stop every suite; and
* **every r6 §7 item this host would need remains unapproved and
  unprovisioned** — the `freedomlab` group, `ubuntu`'s membership, the
  `systemd-tmpfiles` fragment, the laboratory and recovery directories, the
  ledger directory and the initialized `lifecycle.json`. The mechanism refuses
  on an absent lock or record rather than creating either.

**No reservation is claimed by this document.** Nothing was run, synchronized,
inspected or changed on this host, and V6, V8 and V10 remain unperformed.

**Prior authorization boundary, 2026-09-14.** C-P5.0-LAB-I-R1 authorizes
repository changes and local tests with `TEST_DATABASE_URL` unset only. It does
**not** authorize SSH, synchronization, inspection, preflight, provisioning,
permission changes, database operations, generated-vector execution or execution
on this server, and it does not authorize invoking any of the seven integration
points against a real participant. Claude stops after its remediation handback
for independent Codex re-review.

**Prior state, 2026-09-13 — the mechanism exists; this host is untouched.**
The C-P5.0-LAB-I implementation is
[returned for independent review](../review/phase-5-0-reserved-laboratory-implementation-handback.md).
Reservation enforcement is now **implemented in the repository** and is still
**enforced by nothing here**: every one of the r6 §7 items this host would need
— the `freedomlab` group, `ubuntu`'s membership, the `systemd-tmpfiles`
fragment, the laboratory and recovery directories, the ledger directory and the
initialized `lifecycle.json` — remains **unapproved and unprovisioned**, and the
mechanism refuses on an absent lock or record rather than creating either. **No
reservation is claimed by this document.** Nothing was run, synchronized,
inspected or changed on this host, and V6, V8 and V10 remain unperformed.

**Prior authorization boundary, 2026-09-13.** C-P5.0-LAB-I authorizes
repository implementation and local tests only. It does **not** authorize SSH,
synchronization, inspection, preflight, provisioning, permission changes,
database operations or execution on this server. Provisioning definitions may
be prepared in the repository for review but may not be applied. Claude must
stop after its implementation handback for independent Codex review.

**Prior review state, 2026-09-13.** The independent
[LAB-1 R3 re-review](../review/project-review-2026-09-13-lab1-rereview-r3.md)
accepts the local raw-byte remediation with no residual finding. This does not
authorize use of this host: reservation enforcement and the r6 provisioning
delta remain unimplemented, C-7 and EH-R16-1 remain unresolved, the twelve
target facts remain unconfirmed, and `is_executable` remains `False`. The next
action is maintainer direction on those blockers, followed only by separately
authorized implementation review, read-only preflight and execution decisions.

**Current laboratory direction and restriction, 2026-09-10.** C-P5.0-LAB-1
uses exclusive whole-host reservation, trusted administrators and scoped
adversarial cases; see the [direction and impact assessment](../review/phase-5-0-reserved-laboratory-direction.md).
During a reservation all other project work, including tests, synchronization
and dependency updates, must wait for verified release. A lock expiry or crashed
executor does not authorize takeover. Reservation enforcement is not implemented
or verified yet, and no reservation is claimed by this document.

**Maintainer design choice, 2026-09-12.** All seven participants are intended to
use the shared `ubuntu` identity; no separate identities are wanted. The
maintainer accepts the exact ten-item r6 §7 delta as the design basis. This is
not a provisioning or host-operation authorization. The choice records the
trusted-operator assumption and the disposable host's isolation rationale; it
does not make the shared UID a security boundary between participants or
confirm the target's actual entry-point identities. The current handover remains
local-only: no SSH, synchronization, preflight, permission changes, provisioning
or real execution. See the [decision and remediation note](../review/project-review-2026-09-12-lab1-disposition.md).

**Reservation contract, 2026-09-11.** The decision half is now written down:
`tools/phase_5_0_evidence/reservation.py` carries the six reservation states, the
owner/target/release record, fail-closed admission and the release and quarantine
conditions, and it enumerates the seven project entry points that must serialize
on one cooperative lock at `/run/freedom-blades/laboratory.lock` — the bot suite,
the web suite, the Foundry tests, the §3.2 synchronization, the §3.5 dependency
update, the §4 environment reset and the harness CLI. The rule for all seven is
*wait or refuse*, never proceed. **The adapter that actually takes the lock is
proposed and not built**, so no reservation is enforced by anything today and none
is claimed. The lock is advisory: it revokes no permission, and manual root access
to this host remains a trusted operational premise rather than something the lock
constrains. Holding it is not evidence the host is quiet, and releasing it is not
evidence a run ended.

**Errata, 2026-09-11.** Two statements in the paragraph above were corrected by
the [September 11 review](../review/project-review-2026-09-11.md) and the
remediation that answered it. First, the decision half now also requires
**explicit durable lifecycle evidence** to admit: a free process lock, a complete
service inventory, an elapsed deadline and an absent quarantine argument are each
refused as substitutes for a verified predecessor release, and release now
distinguishes an unobserved residue check from an observed empty one. Second, the
lock's proposed `O_CREAT|O_EXCL` adapter is **withdrawn** — ordinary participants
cannot create or unlink an entry in a root-owned directory. The replacement in
[runner contract r2](../review/phase-5-0-reserved-laboratory-runner-contract-r2.md)
§5 is a **provisioned persistent lock inode** plus a separately protected
lifecycle record, and it carries a **non-zero** provisioning and permission delta
(a `freedomlab` system group, a group membership, a `systemd-tmpfiles` fragment
and four provisioned paths). **None of that is approved or provisioned**, the
adapter is still not built, no reservation is enforced by anything today and none
is claimed by this document.

**Second erratum, 2026-09-11.** The
[September 11 re-review](../review/project-review-2026-09-11-r2.md) found four
further defects, and the paragraph above needs two corrections. First, the
decision half admitted a **contradictory** record: a release record beside a
`RUNNING` or `QUARANTINED` predecessor state was resolved in favour of reuse, and
an unrecognised disposition value fell through to admission with no refusal at
all. Both are repaired — `reservation.validate_lifecycle()` now validates the
record as a coherent whole before choosing an admitting branch, and it is the
**same** function all seven participants apply, so an ordinary participant has no
weaker rule than the executor. **`ADMITTED` is an active predecessor and refuses
reuse even when the process lock is free.** Second, the replacement design in
[runner contract r2](../review/phase-5-0-reserved-laboratory-runner-contract-r2.md)
§5 is **superseded by
[r3](../review/phase-5-0-reserved-laboratory-runner-contract-r3.md)**: r2 assigned
`O_PATH` to descriptors it then required `fsync` on, omitted the recovery
parent's durability barrier, overclaimed what a post-unlink check establishes,
and never initialized the verified-first-use record its own fresh-install path
needed. r3's provisioning and permission delta is **eight items** — the
`freedomlab` group, a group membership, a `systemd-tmpfiles` fragment, four
provisioned paths, the initial lifecycle record, and one preflight fact about the
directory barrier. **None of that is approved or provisioned**, the adapter is
still not built, no reservation is enforced by anything today and none is claimed
by this document.

**Third erratum, 2026-09-11.** The
[R3 re-review](../review/project-review-2026-09-11-r3.md) found three further
defects, and the paragraphs above need three corrections. First, the reservation
record's publication renames the record before synchronizing its containing
directory, so between those two points the record is **readable and not
durable**, and a process restart leaves a successor no way to learn that the
publication never completed. The replacement in
[runner contract r4](../review/phase-5-0-reserved-laboratory-runner-contract-r4.md)
§5.6 is that **every participant re-establishes that durability under the lock,
or refuses** — a barrier needing read permission and no write permission at all.
Second, r3's statement that a crashed test suite leaves no lifecycle record and
the next suite may proceed is **withdrawn**: all seven participants now publish
durable in-progress and completion state, an interrupted run of **any** of them
blocks every successor including the harness and the environment reset, and a
free lock or a clean wrapper exit is never evidence that a run's effects ended.
Third, a first-use or operator-recovery record carried no **approved target
identity**, so a history for this hostname admitted against a different approved
target; the binding, the first-use attester and basis, and the recovery's author
now travel from the stored bytes through a bounded versioned schema into the one
shared validator. r4's provisioning and permission delta is **ten items** — r3's
eight, plus a group-writable `runs` directory and a preflight confirmation of the
seven participants' identities. **None of that is approved or provisioned**, the
adapter is still not built, no reservation is enforced by anything today and none
is claimed by this document.

The active [Claude handover](../review/Handover%20information) permits
repository-only prompt drafting. Do not run the SSH, synchronization,
provisioning or test-server commands below for that task. VM work is deferred;
the general server profile does not override the existing pre-execution review
and task-specific gates. Consumed handovers are retained under
[`handover-archive/`](../review/handover-archive/) as history only.

Agents that support skills should use the `run-suites` skill, which carries
this document's synchronization and execution procedure together with the
skip-count and serial-execution traps from `.agents/AGENTS.md`. The skill
checks the restriction banner above first and cites both documents rather
than replacing either.

The server exists so that **Codex, Claude Code, Antigravity, and maintainers have full administrative (root) access** to execute end-to-end tests, destructive PostgreSQL migration drills, dependency builds, and system-level experiments in complete isolation from the production/staging host.

---

## 1. Machine Profile

| Property | Value |
|---|---|
| **Public IPv4** | `138.2.182.39` |
| **SSH Host Alias** | `oracle-test` (and direct IP `138.2.182.39`) |
| **User** | `ubuntu` |
| **Privilege Level** | Full passwordless `sudo` (`sudo ALL=(ALL) NOPASSWD:ALL`) |
| **SSH Authentication** | Key-based via `~/.ssh/id_ed25519` from this host |
| **Operating System** | Ubuntu 26.04 LTS (x86_64) |
| **Kernel** | `7.0.0-31-generic` (future production 7.x generic-kernel baseline) |
| **Node.js** | v22 LTS (`/usr/bin/node`, npm 10) |
| **Python Virtualenv** | `/opt/freedom-blades/runtime/venv-web` (Python 3.12.14) |
| **Python Manager** | `uv` (`/usr/local/bin/uv`) |
| **Database Server** | PostgreSQL 16 (active systemd service `postgresql@16-main`, port 5432, Unix socket `/var/run/postgresql`); PostgreSQL 18 disabled via `/etc/postgresql/18/main/start.conf` (`manual`, port 5433) |
| **PostgreSQL Roles** | `ubuntu` (superuser, local peer auth), `freedom_runtime_test` (restricted role: `NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`, granted to `ubuntu`) |
| **Databases** | `freedom_test` (test lane), `freedom_dev` (development lane) |
| **Client Utilities** | `/usr/lib/postgresql/16/bin` explicitly prepended to `PATH` in test invocations (no global `/usr/local/bin` client symlinks) |
| **Repository Path** | `/opt/freedom-blades/platform` (owned by `ubuntu:ubuntu`) |

---

## 2. Access Configuration

The host configuration is established in `~/.ssh/config` on the primary development/staging server:

```ssh-config
Host oracle-test 138.2.182.39
    HostName 138.2.182.39
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
```

Any agent running in this workspace can reach the remote environment without prompts or interactive passwords.

---

## 3. Agent Usage Instructions (Codex & Claude Code)

### 3.1 Running Administrative (Root) Commands

The `ubuntu` user has unrestricted, passwordless `sudo` rights. To run any administrative or system-level command:

```bash
ssh oracle-test "sudo <command>"
```

Examples:
- Restarting or inspecting PostgreSQL: `ssh oracle-test "sudo systemctl status postgresql"`
- Installing system packages: `ssh oracle-test "sudo apt-get install -y <package>"`
- Managing files or services: `ssh oracle-test "sudo systemctl restart <service>"`

### 3.2 Synchronizing Code to the Disposable Server

Before executing tests or scripts on the disposable server, sync the latest workspace state. Note that `--include='.env.example'` must precede `--exclude='.env*'` to ensure tracked example configuration is transferred while secrets remain excluded. Do not use broad `--delete-excluded`:

```bash
rsync -avz --delete \
  --include='.env.example' \
  --exclude='.env*' \
  --exclude='*.pem' \
  --exclude='*.key' \
  --exclude='yt-cookies.txt' \
  --exclude='*service_account*.json' \
  --exclude='*credentials*.json' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='.pytest_cache/' \
  /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
```

**Secrets guard (LAB-V6-P3 remediation r1, accepted 2026-09-19).** The repository secrets guard admits this command only in the documented shape: one plain `rsync` invocation whose exclusion values are **single-quoted**. It still refuses double-quoted or unquoted exclusion values, `--exclude-from`, a secret named as a source or destination, and any command that chains, substitutes, redirects or comments. Do not rewrite the command to get past a refusal; a refusal is a stop condition. [Independent review](../review/project-review-2026-09-19-lab-v6-p3-secrets-guard-remediation.md).

### 3.3 Running Test Suites Against PostgreSQL

The test database `freedom_test` is created on the authoritative PostgreSQL 16 cluster and owned by `ubuntu`. Run pytest directly using the remote Python 3.12 virtual environment with explicit PostgreSQL 16 `PATH`:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && \
  PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin' \
  TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/freedom-blades/runtime/venv-web/bin/pytest -q -rs tests/web"
```

To run a single test module:
```bash
ssh oracle-test "cd /opt/freedom-blades/platform && \
  PATH='/usr/lib/postgresql/16/bin:/usr/bin:/bin' \
  TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  /opt/freedom-blades/runtime/venv-web/bin/pytest -q tests/web/test_structural_guards.py"
```

### 3.4 Running Frontend / Node.js Tests

Node.js v22 LTS is installed and supports the Node built-in test runner:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && node --test 'foundry-module/tests/'*.test.mjs"
```

### 3.5 Updating Python Dependencies

To add or update dependencies inside the remote virtualenv using `uv`:

```bash
ssh oracle-test "cd /opt/freedom-blades/platform && \
  uv pip install --python /opt/freedom-blades/runtime/venv-web -r requirements-dev.txt -r requirements-web-dev.txt"
```

---

## 4. Resetting the Disposable Environment

If a test corrupted the database or filesystem:

1. **Re-create the PostgreSQL 16 test database:**
   ```bash
   ssh oracle-test "dropdb -U ubuntu --if-exists freedom_test && createdb -U ubuntu freedom_test"
   ```
2. **Re-sync the repository tree safely:**
   ```bash
   rsync -avz --delete \
     --include='.env.example' \
     --exclude='.env*' \
     --exclude='*.pem' \
     --exclude='*.key' \
     --exclude='yt-cookies.txt' \
     --exclude='*service_account*.json' \
     --exclude='*credentials*.json' \
     --exclude='__pycache__/' \
     --exclude='*.py[cod]' \
     --exclude='.pytest_cache/' \
     /opt/freedom-blades/platform/ oracle-test:/opt/freedom-blades/platform/
   ```
