# Package 5.0 security review — revision 11

Date: 2026-08-31
Reviewer: Codex, Package 5.0 Security Reviewer and Independent Reviewer
Outcome: **changes requested; no readiness recommendation**

## Scope and authority

This is the distinct security-focused pass required by package-plan §9.2. It
reviews the eleven named surfaces in revision 11 and does not substitute for
P5.0-R5 operational evidence. It does not rule OD-62 through OD-66, accept
R-5.0-12 through R-5.0-14, confirm A-5.0-3 through A-5.0-5, approve the package
gate, or authorize implementation, migration, host mutation, deployment,
cutover, or Package 5.1+.

The reviewer also performed the earlier design and logical-schema reviews.
Conclusions below that accept those designs are therefore one reviewer's
judgement, not independent design-and-security judgements.

## Findings

### P5.0-SR1 — Blocking — the deployment integrity check can be skipped silently

Package-plan §2.12.5 says deployment compares every copied file with the
reviewed commit and refuses a mismatch. Section 9.2 correctly calls this a
supply-chain control that fails silently if skipped. The specified
`deployment_manifest_digest()` does not close that gap: the deploy step computes
and records a digest of the live deployed bytes, the operator supplies that
same value, and C0 compares it with a fresh digest of those same live bytes.
That proves consistency after deployment, not provenance from the reviewed
commit. Nothing in the specified artifact, journal-generation registration,
or activation precondition requires a trusted reviewed-commit manifest or
attestation. An operator who accidentally omits the separate comparison can
therefore deploy bytes modified through H-1, compute their digest, create a
generation, and pass W11 thereafter without any refusal or durable indication
that the reviewed-commit comparison was omitted.

This is Blocking because H-1 explicitly permits service identities to rewrite
the source tree, while the root-owned deployed program carries authority to
change the authority plane and administer journal evidence. The missing binding
is the control claimed to separate those identities from that authority.

Required remediation: make reviewed-source provenance a fail-closed input to
deployment and generation activation. At minimum, define a trusted manifest
derived from the reviewed immutable Git object (not the mutable worktree), bind
its commit/object identity and digest into the deployment record and generation
registration, and refuse deployment/registration when the trusted manifest,
deployed manifest, and approved revision do not agree. Add a negative test that
omits the provenance step and proves activation cannot succeed; testing only a
wrong caller-supplied live-tree digest is insufficient.

### P5.0-SR2 — Important — the OS identity contract contradicts the journal group contract

Package-plan §2.12.2 says `freedomcoord` and `freedomsheet` are members of their
own groups only. Section 2.13.3 instead requires both identities to be members
of `freedomjournal`, and the E1/E2 evidence identities include that supplementary
group. Following the former contract makes the `0750` directory and `0440` seal
unreadable and invalidates C-4, writer startup verification, and the stated
holder table. Following the latter contradicts the identity and isolation
inventory used by §2.12.6.

Required remediation: make one canonical membership table cover primary and
supplementary groups for every identity, use it consistently in provisioning,
the holder table, and E1–E8, and add positive and negative `id`/`namei`/open
evidence for `freedomsheet`, `freedomcoord`, `discordbot`, and `freedomweb`.

## Host checks

- **C-1 — not completed.** Direct enumeration of `/etc/sudoers.d` was denied.
  The approved non-interactive `sudo` attempt required a password, which this
  review could not supply. This remains a required pre-readiness condition; no
  absence of colliding or broader rules is claimed.
- **C-2 — completed as an inventory.** A host-wide, same-filesystem search for
  set-user-ID and set-group-ID regular files found the standard Ubuntu helpers:
  `ssh-keysign`, `polkit-agent-helper-1`, `dbus-daemon-launch-helper`,
  `utempter`, `crontab`, `umount`, `fusermount3`, `su`, `ssh-agent`, `expiry`,
  `passwd`, `mount`, `chfn`, `sudo`, `chage`, `gpasswd`, `newgrp`, `chsh`,
  `unix_chkpwd`, and `pam_extrausers_chkpwd`. No project-specific helper or
  direct service-identity-to-`freedomcoord` path was identified. This is an
  inventory, not a claim that every listed binary is vulnerability-free.
- **C-3 — not run by design.** It requires an authorized host mutation and
  remains part of A-5.0-5/P5.0-R5 operational evidence.
- **C-4 — not run by design.** The hierarchy and identities do not exist. It
  remains operational evidence and is also blocked on resolving P5.0-SR2.

## Security assessment by surface

Subject to P5.0-SR1 and P5.0-SR2, no additional Blocking or Important design
finding was identified in the database role/HBA ordering, append-only database
histories and activation trigger, credential separation, journal manipulation
matrix, capability register, root journal lifecycle, transient probe cleanup,
or the `freedomjournal` disclosure itself. In particular, the A1/A10/A11 split
matches the two `FS_IOC_SETFLAGS` authorization requirements; the corrected
E1–E8 recipes are suitable as an evidence specification only if their asserted
runtime masks and securebits pass; and the writer-readable seal discloses no
credential or player data.

Stage 4 remains conditional operational evidence, not a confirmed control. Its
implementation must parse a closed allowlist of supported unit directives,
reject duplicate or unknown authority-bearing directives (including drop-ins),
construct `ReadWritePaths=` from the internally fixed canonical probe path, and
compare the complete normalized applied property set. A systemd/package upgrade
that changes the interpreted property set must invalidate the evidence even
when deployed bytes did not change.

The three declared unrefused residuals are correctly described, but this review
does not accept them. P5.0-R5 remains Blocking; P5.0-R1 and P5.0-R4 remain open;
OD-62 through OD-66 remain open; Package 5.0 remains not ready.

## Recommendation

Do not recommend Package 5.0 readiness. Remediate P5.0-SR1 and P5.0-SR2 and
return them for re-review. Separately obtain privileged C-1 evidence and the
authorized C-3/C-4, peer-authentication, HBA-ordering, capability, sandbox,
journal, and recovery evidence required by the package plan. No package gate
may close on this document alone.
