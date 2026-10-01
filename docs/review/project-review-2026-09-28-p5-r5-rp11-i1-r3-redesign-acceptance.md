# Maintainer acceptance — RP-11 I1-R3 publication redesign — 2026-09-28

Decision owner: Peter Duscha, Product Owner and Acceptance Authority

## Decision

Peter Duscha accepts the direction in
`phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md`.

RP-11 publication will be redesigned around:

* an exclusively created named staging inode;
* one descriptor-relative, non-replacing hard link to the final name;
* retention and explicit indexing of both staging and final names; and
* no automatic unlink, rename, repair or alias cleanup.

The `O_TMPFILE` plus `/proc/self/fd/N` publication route and its mutating
pre-admission capability probe are no longer the implementation direction.
The implementation must use the proposal's recommended capability policy: no
separate mutating probe; the first real X-1 publication is the fail-closed
capability test before any host command.

## Effect and limits

This accepts the design direction and authorizes preparation of a bounded
repository implementation assignment. It does **not** itself:

* amend the operational-evidence draft or source;
* assign an implementing agent;
* approve any implementation or manifest digest;
* close RP11-I1-R1-1, RP11-I1-R2-1 or RP11-I1-2;
* satisfy RP-11, C-11 or the launcher-environment requirement;
* set `plan.is_executable=True`, accept either operational pass, close
  P5.0-R5, bind OD-62 G-A or make Package 5.0 ready; or
* authorize SSH, synchronization, network or host inspection, database
  access, `sudo`, provisioning, controlled writes, reboot, verifier, evidence
  bands, harness `--execute`, real participants, capture roots, operational
  probes, protected-artifact access, secrets scans, commits or pushes.

A separately assigned implementer must perform the coherent requirements,
source, tests, manifest and handback slice in proposal §6. A different agent
must then provide the mandatory independent technical, security, operational
and evidence review before Peter decides acceptance.

No host action occurred in recording this decision.
