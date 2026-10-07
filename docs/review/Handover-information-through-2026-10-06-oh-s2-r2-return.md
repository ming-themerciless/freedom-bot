# Active handover — OH-S2 R2 returned for review — 2026-10-06

Peter Duscha renamed the GitHub repository to `freedom-platform` and made it
public. The canonical public retrieval URL is now
`https://github.com/ming-themerciless/freedom-platform.git`; the controller
`origin` uses `git@github.com:ming-themerciless/freedom-platform.git`.

R4 work ID `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R4-20261006-01` is consumed at
its required anonymous-retrieval `HARD STOP`. Independent review accepts the
substantive stop and records two Important process/reporting findings plus one
Optional retained-wording finding. Its paths remain retained and must not be
reused or inspected.

R5 work ID `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-20261006-02` is consumed.
Independent review accepts its anonymous pinned retrieval, isolated checkout
and retained evidence integrity, but not its reported `H-0 PASS`: HF-15's
capture-root-parent observation and HF-18's named-client-path observation are
missing because the assignment supplied neither path.

No retry, evidence revisit, cleanup, credential access, privilege,
installation, build, test, service/database mutation, H-1/H-2, activation,
commit or push is authorized.

Peter Duscha authorizes repository-only work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR1-20261006-03`. Claude must prepare a
decision-ready cumulative remediation for HF-15, HF-18, the Python 3.12/3.14
mismatch, the Polkit unknown and PO-21(i), then stop for independent Codex
review. This authority grants no host access or later slice. OH-S2 and every
later slice remain unauthorized.

Claude returned the remediation at its terminal state, `REMEDIATION PROPOSAL
READY FOR REVIEW`. It recommends a fixed capture-root parent and template,
withdrawal of HF-18 from H-0 with per-slice client checks, Route 1 (exact
`/usr/bin/python3.14`, with PO-12/PO-19 returned to OH-S2), a privileged
Polkit absence check at H-1, an HF-20 split, and a narrow H-0G successor
that composes with R5. At that return point nothing was accepted or authorized;
the subsequent Codex finding and Peter decisions are recorded below.

Independent Codex review found one blocking command defect: H-0G cannot run
`df` against an expected-absent capture parent. Peter has now decided D-1
through D-7, including the fresh run-specific RP-11 checkout model and the
bounded disposable-Test cleanup/recreation lifecycle. Repository-only work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR2-20261006-04` is authorized to produce
the corrected cumulative R2 proposal and handback. It grants no host access,
cleanup, H-0G or later slice.

Claude returned R2 at its terminal state, `R2 REMEDIATION READY FOR REVIEW`.
The cumulative R2 proposal records D-1 through D-7 and the lifecycle policy,
corrects HF-15 so `findmnt`/`df` run only on the existing ancestor `/var/lib`
while the parent's expected `ENOENT` is observed by `lstat`/`listxattr`,
applies D-7 through a per-slice fresh-checkout contract, and designs gated
exact-path cleanup and workspace recreation without any command or authority.
Nothing is accepted or authorized; it awaits independent Codex review.

Independent Codex review accepts the HF-15 correction but does not accept R2.
It records two Blocking D-7 findings: CK-9 leaves its `.git` contract to be
designed by the reviewer, and CK-3 claims to reject escaping symlinks without
checking their targets or protecting consumed source paths. It also records
one Important finding: manifests and digests do not reproduce retained
evidence bytes. Peter authorizes repository-only R3 work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR3-20261006-05` to remediate those three
findings and return for independent Codex re-review. No host access, cleanup,
H-0G or later slice is authorized.

Claude returned R3 at its terminal state, `R3 REMEDIATION READY FOR REVIEW`.
The cumulative R3 proposal replaces CK-9 with a closed structural `.git`
contract and explicit mechanism rejections, authenticates the tracked `venv`
symlink's link text and makes every symlink non-consumable under a no-follow
source-consumption contract, and withdraws the claim that digests reproduce
retained bytes. Nothing is accepted or authorized; it awaits independent
Codex re-review.

Codex independently re-reviewed R3 with no Blocking, Important or Optional
finding. Peter Duscha accepts that recommendation and the cumulative R3
proposal; `R2-F1`, `R2-F2` and `R2-F3` are closed as remediated. R3 is the
accepted inactive design basis and creates no host or cleanup authority by
itself.

Peter authorizes H-0G R1 work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0G-R1-20261006-06` under the exact 7881-byte
prompt SHA-256 `58ebc8cb07a82d4f2c75df5dc35feb99eaf04802cc9abd1a98ffdb1104caca31`.
Claude may use exactly one forwarding-disabled, non-interactive SSH execution
connection to collect the repository-free, unprivileged H-0G facts into
`/var/tmp/p5-r5-rp11-h0g-20261006-01-h0g-evidence`. It must stop at `H-0G
PASS` or a defined `HARD STOP` and return for independent Codex review and
composition. No cleanup, workspace recreation, OH-S2 or later slice is
authorized.

Claude returned H-0G R1 at its terminal state, `H-0G PASS`, through exactly
one connection. Anchors A-1 through A-10 are equal; `/var/lib/rp11-capture`
is absent (`lstat` and `listxattr` both `ENOENT`); `/var/lib` and its
filesystem facts match R5; the exact-path CPython 3.14 package and runtime
facts are recorded. Evidence closed with `MANIFEST.payload`
`cc0c3f29221c035241efdad71852776258c69e68e530c145925d3f4a74f1da3d`. The
authority and prompt are consumed. Codex independently reviewed H-0G R1 with
no Blocking, Important or Optional finding and accepts its reported `H-0G
PASS`. All ten composition anchors are equal, so the review composes R5 and
H-0G as **`H-0 PASS`** under accepted R3 §10.2. For RD-2, no pending or
foreseeable review or recovery of this composition needs the retained R5 or
H-0G host bytes; their host-byte dependencies are closed by the review. The
paths nevertheless remain retained and untouched pending the separately gated
LC-3 through LC-5 sequence. No cleanup enumeration, cleanup, workspace
recreation, OH-S2 or later work is authorized.

Peter Duscha accepts the composed `H-0 PASS` and restates U-9 for the exact
`/usr/bin/python3.14` target, binding the proof to the accepted glibc version,
the interpreter's dynamic section and drift-triggered re-citation. He
authorizes repository-only OH-S2 R1 work ID
`C-P5.0-R5-RP11-H1-OH-S2-R1-20261006-07` under exact prompt SHA-256
`97ba6c23aa19ee83cb5389eb2860d51806f3fad243afe9aacf76c8e3c7aca92f`
(9254 bytes). Claude must evaluate PO-14 first, may use only primary upstream
sources and exact Ubuntu source-package material, and must return its citation
record for independent Codex review. No host access, implementation, build,
cleanup, OH-S3/OH-S4p or later slice is authorized.

Claude returned OH-S2 R1 at its terminal state, `OH-S2 CITATIONS READY FOR
REVIEW`. PO-14 and AD-7 are established for systemd `259.5-0ubuntu3.4`, so
LB-2S is not withdrawn. Dispositions reported for review: PO-20 (f), PO-21 (c)
and PO-21 (s) are refuted and PO-11 (d) has no citable reload bound, so the
activation design returns to design review; PO-12 and AS-8 are refuted for
CPython 3.14.4 (`PYTHONEXECUTABLE` and `__PYVENV_LAUNCHER__` are honoured
under `-I`), so Route 1 returns to Route 3 design review, with a narrower
PO-12′ offered; PO-19 is not established pending unobserved dynamic-section
and library-ownership facts (MF-1, MF-2); CL-21i is non-empty and disarmed by
`/run/nextroot` being absent; `os` has no `renameat2`, so `ctypes` stays. The
authority and prompt are consumed. Nothing is accepted or authorized; the
record awaits independent Codex review and Peter's decision. No host access,
implementation, build, cleanup, OH-S3/OH-S4p or later slice is authorized.

Independent Codex review does not accept R1. It records two Blocking findings:
R1-F1, the disclosed repository-root recursive search read prohibited
secret-bearing paths and contradicts the later no-secret-read claim; and R1-F2,
the `bolt`, `fwupd` and `packagekit` source-package retrievals exceeded R1's
named source authority. Peter authorizes repository-only OH-S2 R2 remediation
work ID `C-P5.0-R5-RP11-H1-OH-S2-R2-20261006-08` under exact prompt SHA-256
`ca6dd02ff3400573413f77c3067366bd86259a599ba2107c963322f68bb0d05f`
(11759 bytes). R2 may re-retrieve only the three exact named Ubuntu source
packages, produce a cumulative corrected citation record and return for
independent Codex re-review. No host, retained-evidence, secret, implementation,
build, application-test, cleanup, later-slice, commit or push authority exists.

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

- [Rename and publication decision](project-review-2026-10-06-repository-rename-and-publication.md)
- [R4 independent review](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-hard-stop.md)
- [R4 handback](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-handback.md)
- [Consumed R4 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-authority.md)
- [Consumed R4 prompt](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r4-claude-prompt.md)
- [R5 independent review](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-incomplete.md)
- [R5 handback](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-handback.md)
- [Consumed R5 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-authority.md)
- [Consumed R5 prompt](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-claude-prompt.md)
- [Active remediation authority](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-authority.md)
- [Consumed remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r5-remediation-claude-prompt.md)
- [Remediation proposal](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md)
- [Remediation handback](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-handback.md)
- [R2 authority](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-authority.md)
- [Consumed R2 Claude prompt](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-claude-prompt.md)
- [R2 proposal](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md)
- [R2 handback](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-handback.md)
- [R2 independent review](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md)
- [R3 authority](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md)
- [Consumed R3 Claude prompt](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md)
- [R3 proposal](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md)
- [R3 handback](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-handback.md)
- [R3 acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-acceptance.md)
- [Consumed H-0G R1 authority](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-authority.md)
- [Consumed H-0G R1 Claude prompt](phase-5-0-p5-r5-rp11-h1-h0g-r1-claude-prompt.md)
- [H-0G R1 handback](phase-5-0-p5-r5-rp11-h1-h0g-r1-handback.md)
- [H-0G R1 independent review and composed H-0](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-composed-h0-pass.md)
- [H-0 and U-9 acceptance](project-review-2026-10-06-p5-r5-rp11-h1-h0g-r1-acceptance-and-u9.md)
- [Consumed OH-S2 R1 authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r1-authority.md)
- [Consumed OH-S2 R1 Claude prompt](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-claude-prompt.md)
- [OH-S2 R1 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-citations.md)
- [OH-S2 R1 handback](phase-5-0-p5-r5-rp11-h1-oh-s2-r1-handback.md)
- [Consumed OH-S2 R2 remediation authority](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md)
- [Consumed OH-S2 R2 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md)
- [OH-S2 R2 citation record](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md)
- [OH-S2 R2 handback](phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md)

## Consumed R3 H-0

Claude returned a Phase 1 `HARD STOP` for work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R3-20261005-06`: the fixed checkout on
`oracle-test` had tracked and untracked changes, so the program correctly
stopped before fetch, checkout or HF-03 through HF-20 collection. The single
SSH authority and evidence path are consumed.

Independent review accepts the substantive stop but not the pasted text as a
complete literal handback: multiple commands and SHA-256 fields were visibly
truncated or malformed. No evidence revisit, repair, cleanup or retry is
authorized. A successor requires Peter's separate choice between preserving or
cleaning the existing checkout and using a fresh checkout path, plus a new work
ID and evidence path. OH-S2 and every later slice remain unauthorized.

- [Independent review](project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-hard-stop.md)
- [Consumed authority](project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-authority.md)
- [Consumed Claude prompt](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-claude-prompt.md)

## Consumed R3 assignment detail

Peter Duscha authorizes the production-workspace Claude process to execute the
replacement OH-S0b/OH-S1 assignment through exactly one forwarding-disabled,
non-interactive SSH connection under work ID
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R3-20261005-06`. Claude remains here and sends
one self-contained H-0 program on stdin; no nested Claude client is used. The
program is retained as evidence, then runs locally as `ubuntu` on
`oracle-test`. It verifies kernel nodename
`Test`, anonymously retrieves pinned commit
`46d1c35a029ca8287779ae87d08a370ba0a0f2ef` from the fixed canonical public
HTTPS repository, and collects HF-01 through HF-20 into the exclusive evidence
directory `/var/tmp/p5-r5-rp11-h0-20261005-04-h0-evidence`.

R2 is withdrawn unused and superseded. The assignment ends at its first
`H-0 PASS` or `HARD STOP`. No second SSH connection or retry,
credential access or forwarding, privilege, package operation, build, test,
service/database mutation, H-1/H-2, activation, rollback, cleanup, commit or
push is authorized. OH-S2 and every later slice remain unauthorized pending
independent Codex review and a further recorded decision.

- [Authority](project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-authority.md)
- [Consumed Claude prompt](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-r3-claude-prompt.md)

## Consumed evidence-repair assignment

Claude returned `EVIDENCE REPAIR COMPLETE` for work ID
`C-P5.0-ORACLE-AGENT-CLIENT-BOOTSTRAP-R1-20261005-03`. The one-shot authority
is consumed. The reported retained bytes support the disposition `substantive
remediation facts verified; original evidence procedure was nonconforming` and
resolve the apparent inode collision as a damaged earlier table.

The returned chat text is not a complete literal corrected handback: numerous
command strings and fields remain visibly truncated or malformed, including a
40-character value presented as the new `MANIFEST.payload` SHA-256. The repair
is therefore recorded without clean acceptance of its reporting requirement.
Its authority ended at the terminal return, so no further evidence access or
retry is authorized.

- [Evidence-repair authority](project-review-2026-10-05-agent-client-bootstrap-evidence-repair-authority.md)
- [Claude prompt](phase-5-0-agent-clients-bootstrap-remediation-evidence-repair-claude-prompt.md)
- [Return review](project-review-2026-10-05-agent-client-bootstrap-evidence-repair-return.md)

The first OH-S0b/OH-S1 work ID ended in `HARD STOP` before retrieval because
its prompt incorrectly compared the kernel nodename with the SSH alias. That
authority, R1, R3 and R4 are consumed; R2 was withdrawn unused. No H-0
authority is currently active.

The intended assignment remains:

1. retrieve pinned commit `46d1c35a029ca8287779ae87d08a370ba0a0f2ef`
   directly and anonymously from the canonical public GitHub repository; then
2. collect the accepted unprivileged, read-only H-0 facts HF-01 through HF-20.

A future successor must provide a fresh work ID, evidence path and explicit
authority using the new canonical repository URL.

Identity clarification, 2026-10-05: `oracle-test` is the SSH alias; the same
machine's approved kernel nodename is `Test`. Future assignments must compare
`uname -n` with `Test`, not with the alias. The consumed H-0 prompt is retained
as execution evidence and is not retroactively rewritten. See the
[nodename correction](project-review-2026-10-05-oracle-test-nodename-correction.md).

Outside R3's direct controller authority, the evidence-repair authority
recorded above or another separately recorded authority, the production
workspace host must not be a source, controller, relay, destination, fallback
or rollback target. No SSH Git transport, credential,
`sudo`, package operation, installation, build, test suite, service/database
mutation, H-1/H-2, activation, evidence pass, rollback, cleanup, commit or push
is authorized. H-0 may write only its exclusive retained evidence directory.

- [Authority](project-review-2026-10-05-p5-r5-rp11-h1-oh-s0b-oh-s1-authority.md)
- [Claude prompt](phase-5-0-p5-r5-rp11-h1-oh-s0b-oh-s1-h0-claude-prompt.md)
- [Accepted design](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md)
- [Archived predecessor handover](Handover-information-through-2026-10-04-d3-r6-acceptance.md)
