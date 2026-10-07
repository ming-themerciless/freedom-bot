# Project status

This is the concise current operational-status entry point. Historical states
are indexed under [`status-archive/`](status-archive/README.md).

## Current status — OH-S2 R2 returned for review — 2026-10-06

The canonical public repository is now `ming-themerciless/freedom-platform` at
`https://github.com/ming-themerciless/freedom-platform.git`. This administrative
rename does not rename the Freedom bot application or service.

R5 is consumed. Independent review accepts its anonymous pinned retrieval,
clean detached isolated checkout and retained evidence integrity, but rejects
the reported `H-0 PASS` as incomplete: the accepted HF-15 capture-root-parent
and HF-18 named-client-path observations were not collected because neither
path was supplied. The observed host also has CPython 3.14.4 rather than the
design's required `/usr/bin/python3.12`. No retry or later slice is authorized.

Peter Duscha authorizes repository-only remediation work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR1-20261006-03`. Claude will produce a
decision-ready cumulative amendment and handback, then stop for independent
Codex review. No host access, fresh fact collection or OH-S2 is authorized.

Claude returned the remediation at its terminal state, `REMEDIATION PROPOSAL
READY FOR REVIEW`. It recommends a fixed capture-root parent and template,
withdrawal of HF-18 from H-0 with per-slice client checks, Route 1 (exact
`/usr/bin/python3.14`, with PO-12/PO-19 returned to OH-S2), a privileged
Polkit absence check at H-1, an HF-20 split, and a narrow H-0G successor
that composes with R5. At that return point nothing was accepted or authorized;
the subsequent Codex finding and Peter decisions are recorded below.

Codex found one blocking defect in the proposed H-0G HF-15 commands: `df`
cannot inspect an expected-absent parent path. Peter has decided D-1 through
D-7 and approved a bounded disposable-Test cleanup/recreation lifecycle.
Repository-only R2 work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR2-20261006-04` is authorized to correct
and consolidate the proposal. No host cleanup, H-0G or later slice is
authorized.

Claude returned R2 at `R2 REMEDIATION READY FOR REVIEW`: a cumulative proposal
recording D-1 through D-7, a corrected HF-15 that runs `findmnt`/`df` only on
the existing ancestor `/var/lib`, the D-7 fresh-checkout contract, and a gated
exact-path cleanup and recreation design. Nothing is accepted or authorized;
it awaits independent Codex review.

Independent Codex review accepts R2's HF-15 repair but records two Blocking
D-7 findings and one Important evidence-retention finding. CK-9 is incomplete
because its `.git` rule is left for the reviewer to design; CK-3 does not
enforce its claimed escaping-symlink protection; and manifests/digests do not
reproduce retained bytes. Peter authorizes repository-only R3 work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR3-20261006-05` to remediate the findings
and return for independent Codex re-review. No host access, cleanup, H-0G or
later slice is authorized.

Claude returned R3 at `R3 REMEDIATION READY FOR REVIEW`: a cumulative
proposal with a closed structural CK-9 `.git` contract, link-text
authentication of the tracked `venv` symlink with a no-follow
source-consumption contract that makes every symlink non-consumable, and a
corrected retained-evidence rationale. Nothing is accepted or authorized; it
awaits independent Codex re-review.

Codex independently re-reviewed R3 with no finding, and Peter accepts the
cumulative proposal. `R2-F1`, `R2-F2` and `R2-F3` are closed as remediated.
R3 is now the accepted inactive design basis.

H-0G R1 work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06` is authorized under exact
prompt SHA-256 `58ebc8cb07a82d4f2c75df5dc35feb99eaf04802cc9abd1a98ffdb1104caca31`
(7881 bytes). It permits exactly one forwarding-disabled SSH execution
connection and repository-free, unprivileged observation into the exclusive
path `/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence`. Its return requires
independent review and composition with R5. Cleanup, workspace recreation,
OH-S2 and every later slice remain unauthorized.

Claude returned H-0G R1 at its terminal state, `H-0G PASS`, through exactly
one connection. Anchors A-1 through A-10 are equal; `/var/lib/rp11-capture`
is absent (`lstat` and `listxattr` both `ENOENT`); `/var/lib` and its
filesystem facts match R5; the exact-path CPython 3.14 package and runtime
facts are recorded. Evidence closed with `MANIFEST.payload`
`cc0c3f29221c035241efdad71852776258c69e68e530c145925d3f4a74f1da3d`. The
authority and prompt are consumed. Codex independently reviewed H-0G R1 with
no finding, accepted `H-0G PASS` and composed R5 plus H-0G as **`H-0 PASS`**
under accepted R3 §10.2. The review closes the R5 and H-0G host-byte
dependencies for RD-2 because no pending or foreseeable review or recovery of
the composition needs those bytes. Both paths remain retained and no cleanup
enumeration, cleanup, workspace recreation, OH-S2 or later work is authorized
without its next recorded decision and authority.

Peter accepts the composed `H-0 PASS` and the recommended U-9 restatement for
`/usr/bin/python3.14`. Repository-only OH-S2 R1 work ID
`C-P5.0-R5-RP11-H1-OH-S2-R1-20261006-07` is now authorized under exact prompt
SHA-256 `97ba6c23aa19ee83cb5389eb2860d51806f3fad243afe9aacf76c8e3c7aca92f`
(9254 bytes). PO-14 is the first, fail-closed citation gate. No host access,
implementation, build, cleanup or later slice is authorized.

Claude returned OH-S2 R1 at its terminal state, `OH-S2 CITATIONS READY FOR
REVIEW`. PO-14 and AD-7 are established for systemd `259.5-0ubuntu3.4`, so
LB-2S is not withdrawn. The record reports these dispositions for review:
PO-20 (f), PO-21 (c) and PO-21 (s) are refuted and PO-11 (d) has no citable
reload bound, so the activation design returns to design review; PO-12 and
AS-8 are refuted for CPython 3.14.4 (`PYTHONEXECUTABLE` and
`__PYVENV_LAUNCHER__` are honoured under `-I`), so Route 1 returns to Route 3
design review, with a narrower PO-12′ offered; PO-19 is not established
pending unobserved dynamic-section and library-ownership facts; CL-21i is a
non-empty list disarmed by `/run/nextroot` being absent; and `os` has no
`renameat2`, so `ctypes` stays. The authority and prompt are consumed.
Nothing is accepted or authorized; the record awaits independent Codex review
and Peter's decision. No host access, implementation, cleanup or later slice
is authorized.

Independent Codex review does not accept R1. R1-F1 records that the disclosed
repository-root recursive search read prohibited secret-bearing paths and
contradicts R1's later no-secret-read claim. R1-F2 records that retrieval of
the `bolt`, `fwupd` and `packagekit` source packages exceeded R1's named source
authority. Peter authorizes repository-only OH-S2 R2 remediation work ID
`C-P5.0-R5-RP11-H1-OH-S2-R2-20261006-08` under exact prompt SHA-256
`ca6dd02ff3400573413f77c3067366bd86259a599ba2107c963322f68bb0d05f`
(11759 bytes). R2 may re-retrieve only the three exact named Ubuntu source
packages and must return a cumulative corrected record for independent Codex
re-review. It grants no host, retained-evidence, secret, implementation,
build, application-test, cleanup, later-slice, commit or push authority.

Claude returned OH-S2 R2 at its terminal state, `OH-S2 R2 REMEDIATION
READY FOR REVIEW`. The cumulative R2 citation record states plainly that
R1's repository-root recursive search read prohibited secret-bearing paths,
that R1 was nonconforming for that reason, and that any incident-response or
rotation decision is Peter's; R2 makes no no-secret-read claim. R1's
`bolt`/`fwupd`/`packagekit` evidence is marked non-authoritative; R2
re-retrieved only those three authorized packages, validated every `.dsc`
checksum, and derived the three installed rule byte streams, each equal to
its durable R5 digest. No verdict or disposition changes, and
`/etc/polkit-1/rules.d` remains MF-3. The authority is not retroactive. The
R2 authority and prompt are consumed. Nothing is accepted or authorized;
neither R1 nor R2 is accepted because R2 is complete. The record awaits
independent Codex re-review and Peter's decision. No host, retained-evidence,
secret, implementation, build, cleanup, OH-S3/OH-S4p or later-slice authority
exists.

[Rename decision](../review/project-review-2026-10-06-repository-rename-and-publication.md)
· [R4 review](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-hard-stop.md)
· [R4 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-handback.md)
· [R5 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-authority.md)
· [R5 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md)
· [R5 review](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-incomplete.md)
· [Remediation authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md)
· [Consumed remediation prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md)
· [Remediation proposal](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md)
· [Remediation handback](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md)
· [R2 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-authority.md)
· [Consumed R2 prompt](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-claude-prompt.md)
· [R2 proposal](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md)
· [R2 handback](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-handback.md)
· [R2 independent review](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md)
· [R3 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md)
· [Consumed R3 prompt](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md)
· [R3 proposal](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md)
· [R3 handback](../review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-handback.md).
· [R3 acceptance](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-acceptance.md)
· [H-0G R1 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-authority.md)
· [Consumed H-0G R1 prompt](../review/phase-5-0-p5-r5-rp11-h1-h0g-r1-claude-prompt.md)
· [H-0G R1 handback](../review/phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md).
· [H-0G R1 review and composed H-0](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-composed-h0-pass.md).
· [H-0 and U-9 acceptance](../review/project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md)
· [Consumed OH-S2 R1 authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r1-authority.md)
· [Consumed OH-S2 R1 prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-claude-prompt.md)
· [OH-S2 R1 citation record](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md)
· [OH-S2 R1 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r1-handback.md).
· [Consumed OH-S2 R2 remediation authority](../review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md)
· [Consumed OH-S2 R2 remediation prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md)
· [OH-S2 R2 citation record](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md)
· [OH-S2 R2 handback](../review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md).

### Consumed R3 H-0

R3 reached a valid Phase 1 `HARD STOP` because the fixed `oracle-test`
checkout contained tracked and untracked changes. No fetch, checkout or
HF-03 through HF-20 collection ran. The single SSH authority and evidence path
are consumed. Independent review accepts the substantive stop but records a
blocking evidence defect: the supplied terminal handback contains truncated
commands and malformed SHA-256 fields and is not a complete literal record.

No retry, evidence revisit, repository cleanup or fresh checkout is authorized.
Peter must separately select and authorize the successor route. OH-S2 and every
later slice remain unauthorized.

[Independent review](../review/project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-hard-stop.md).

### Consumed R3 authority

Peter Duscha authorized replacement work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R3-20261005-06`. Workspace Claude remains on
the controller and sends one self-contained H-0 program through exactly one
forwarding-disabled, non-interactive SSH connection. No nested Claude is used.
The retained program runs as `ubuntu`, compares `uname -n` with `Test`, and retrieves
the pinned commit from the fixed canonical public HTTPS repository, and collects
HF-01 through HF-20 into the new exclusive evidence directory. The assignment
is one-shot and ends at `H-0 PASS` or `HARD STOP`.

[Authority](../review/project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-authority.md)
· [Consumed prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-claude-prompt.md).

OH-S2 and every later slice remain unauthorized pending independent Codex
review and a further recorded decision. No new authentication or credential access,
privilege, package operation, build, test, service/database mutation, H-1/H-2,
activation, rollback, cleanup, commit or push is authorized.

### Consumed evidence-repair assignment

Claude returned `EVIDENCE REPAIR COMPLETE` for the one-shot retained-evidence
repair. The authority is consumed. The return supports the substantive
disposition that the remediation facts are verified while the original
evidence procedure was nonconforming, but the transmitted handback still has
truncated command text and fields and therefore is not accepted as the complete
literal record the prompt required.

That repair does not authorize further evidence access or retry. Its reporting
defect is preserved independently of the later, now-consumed H-0 assignments.
[Authority](../review/project-review-2026-10-05-agent-client-bootstrap-evidence-repair-authority.md)
· [Prompt](../review/phase-5-0-agent-clients-bootstrap-remediation-evidence-repair-claude-prompt.md).
· [Return review](../review/project-review-2026-10-05-agent-client-bootstrap-evidence-repair-return.md).

The first, corrected, R3, R4 and R5 OH-S0b/OH-S1 attempts are all consumed. R2
was withdrawn unused. No H-0 authority is currently active.

`oracle-test` is the operational SSH alias; the approved kernel nodename is
`Test`. The consumed prompt used the alias as the expected nodename. Future
host checks use `Test` and require a fresh assignment and evidence path.
[Correction](../review/project-review-2026-10-05-oracle-test-nodename-correction.md).

The cumulative D3-R6 design remains accepted and its remediation findings
closed. Package RAID item `P5.0-R5`, PO-9, PO-14, D9-4, H-1, RP-11 wiring,
`plan.is_executable` and Package 5.0 readiness remain open. OH-S2 and every
later slice remain unauthorized pending Peter's decision on the R5 review.

[Authority](../review/project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-authority.md)
· [Claude prompt](../review/phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-claude-prompt.md)
· [Archived predecessor status](status-through-2026-10-04-d3-r6-acceptance.md).
