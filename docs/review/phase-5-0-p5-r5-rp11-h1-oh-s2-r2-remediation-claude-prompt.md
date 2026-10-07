# Claude prompt — OH-S2 R1 review-findings remediation (R2)

Status: **authorized by Peter Duscha on 2026-10-06**

Work ID: `C-P5.0-R5-RP11-H1-OH-S2-R2-20261006-08`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only assignment in docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-remediation-claude-prompt.md. Remediate both Blocking findings from independent review of OH-S2 R1, produce a self-contained cumulative R2 citation record and durable handback, update only the four authorized current-state pointers, and stop for independent Codex re-review. Do not access any secret-bearing file, oracle-test, any retained evidence path, credential, or player data; do not perform implementation, build, application-test, service/database, cleanup, commit, or push work.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation and narrowly bounded authoritative-source
research assignment. Its authority record is
[`project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-remediation-authority.md).

R1 remains unaccepted. This assignment may repair its citation record but may
not accept its conclusions. It authorizes no SSH or other host connection, no
`oracle-test`, production, staging, Foundry or database access, no retained
evidence access, no secret, credential or player-data access, no package
operation or installation, no downloaded-code execution, no build or
application test, no implementation or configuration edit, no service or
database mutation, no cleanup of repository or host evidence, no workspace
recreation, no launcher work, no OH-S3/OH-S4p or later slice, no H-1/H-2, no
activation or rollback, and no commit or push.

The assignment ends at `OH-S2 R2 REMEDIATION READY FOR REVIEW` or its first
defined `HARD STOP`. Independent Codex re-review and Peter's later recorded
decision remain mandatory.

## Required reading and initial checks

Before research or editing, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 14, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in
   `docs/operations/disposable-test-server.md`;
5. the OH-S2 R1 authority, consumed prompt, complete citation record and
   complete handback;
6. the accepted one-host design and cumulative R3 sections cited by R1;
7. the composed H-0 review and Peter's H-0/U-9 acceptance; and
8. the R5 and H-0G handbacks only as durable repository evidence.

Inspect `git status` and preserve every unrelated and pre-existing change.
Verify this prompt's exact byte count and SHA-256 against its authority before
any research or edit. A mismatch is
`HARD STOP: remediation prompt identity mismatch`.

Do not use a recursive search whose root is the repository, a workspace root,
the user's home, `/opt`, `/var`, `/tmp` or `/`. Searches must name an exact
known-safe repository document or an exact fresh public-source extraction
directory. Do not read `.env`, `yt-cookies.txt`, service-account JSON, tokens,
credentials, database URLs, Foundry credentials, or any other secret-bearing
path for any purpose, including existence tests, content searches, hashing,
link checking or verification. If a command would traverse an unknown file
set, do not run it.

## Independent-review findings to remediate

### R1-F1 — prohibited secret-file read and contradictory reporting

R1 handback §8 reports that two recursive `grep` commands were accidentally
run from the repository root and read files while testing for `slibdir`,
potentially including the listed `yt-cookies.txt`. This violated both
`.agents/AGENTS.md` and the R1 prompt's absolute secret-access prohibition.
The later statement that no secret was read is therefore false even though no
secret contents were reported as printed or retained.

Remediate this finding without concealing or rewriting history:

1. preserve the R1 prompt, record and handback unchanged;
2. state plainly in R2 that the prohibited read occurred and that R1 was
   nonconforming for that reason;
3. record that Peter was notified through independent review;
4. do not inspect the secret-bearing files, shell history, Claude session
   scratchpad or external logs to investigate further;
5. do not claim that no secret was read; distinguish instead between the
   admitted read and the reported absence of printed or retained content;
6. do not independently decide that credential rotation is unnecessary.
   State that the available R1 disclosure reports no printed or retained
   secret content, while any incident-response or rotation decision belongs
   to Peter; and
7. make every R2 command and verification target explicit and bounded so the
   mistake cannot recur.

This finding is a process and security-compliance defect. It does not by
itself make a source proposition true or false, but it prevents clean
acceptance of R1 as an authority-conforming execution.

### R1-F2 — three Ubuntu source packages were outside R1's source authority

R1 downloaded and used exact Ubuntu source packages for `bolt`, `fwupd` and
`packagekit` to identify installed Polkit rule files. The R1 authority limited
network research to source material named in its prompt, and those packages
were not named. Their R1 retrieval and any conclusions uniquely dependent on
it must not be treated as authorized evidence.

This R2 authority explicitly adds only the following exact Ubuntu source
packages to the permitted research set:

- `bolt` `0.9.10-1`;
- `fwupd` `2.1.1-1ubuntu3.1`; and
- `packagekit` `1.3.4-3ubuntu1.2`.

For those packages, use only official Ubuntu archive or Launchpad source
material. Re-retrieve the exact `.dsc` and every file named by it into one
fresh mode-`0700` directory under `/tmp`; verify every `Checksums-Sha256`
entry before use; statically inspect only the files needed to derive the
installed Polkit rule bytes; and record URLs, retrieval time, sizes and
SHA-256 values. Do not execute downloaded code, invoke its build system,
install anything, or rely on R1's unauthorized retrieval as evidence.

If an exact package or required source file cannot be retrieved or its hashes
do not validate, stop at
`HARD STOP: authorized Polkit-rule source not established`.

All other network retrieval is prohibited. In particular, do not re-download
systemd, Linux, glibc, CPython, polkit itself, or any upstream comparison
artifact. For unaffected conclusions, use R1's durable citations and reasoning
as proposed material, independently check their internal traceability against
the repository records, and clearly state that R2 is a remediation of the two
review findings rather than a claim to have repeated all R1 research.

## Required cumulative R2 treatment

Create a self-contained cumulative R2 citation record. It must:

1. carry forward every R1 requirement and limb with an explicit
   `established`, `refuted` or `not established` verdict;
2. preserve R1's source/H-0/mechanical/reasoned fact separation, complete
   property tables, CL-21i table, U-9 wording and drift gate, PO-17/OH-S4p
   boundary, missing-fact list, contradictions and design-return dispositions;
3. mark R1's three-package evidence as non-authoritative and replace every
   dependency on it with the newly authorized R2 retrieval evidence;
4. identify precisely which PO-11 limbs or supporting rows the three packages
   affect and whether the R2 evidence changes any verdict;
5. preserve the finding that `/etc/polkit-1/rules.d` remains MF-3 and is not
   inferred from distribution packages;
6. retain every R1 technical correction unless R2 discovers a concrete
   internal contradiction while composing the cumulative record; any such
   contradiction must be reported, not silently repaired;
7. state that neither R1 nor R2 is accepted merely because R2 is complete;
8. contain a dedicated compliance-remediation section mapping R1-F1 and R1-F2
   to the exact R2 evidence and wording that closes them; and
9. never use the new authorization retroactively: it authorizes the R2
   retrieval only and does not make the R1 retrieval conforming.

Do not edit the R1 citation record, handback, prompt, authority, any accepted
historical record, or any implementation file.

## Deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md` — the
   self-contained cumulative R2 citation record;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-handback.md` — the complete
   durable handback.

Update only these current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`;
- §20 of `docs/implementation-plan.md`; and
- the restriction banner in `docs/operations/disposable-test-server.md`.

The handback must report the prompt identity, terminal state, files changed,
sources consulted, exact commands and results, checks not run, temporary-path
disposition, security implications, unresolved questions and proposed
independent-review focus. It must distinguish pre-existing worktree changes
and explicitly confirm that R2 did not access a secret-bearing file, any host,
or any retained evidence path.

Mark this R2 authority and prompt consumed in the four pointers. Do not claim
Codex or Peter acceptance and do not propose or authorize a successor slice.

## Safe research and temporary-directory rules

- Use a new literal task-specific path created by `mktemp -d` under `/tmp`.
- Before deletion, resolve and verify that the path is beneath `/tmp`, is not
  `/tmp` itself, is owned by the current user, and is the directory created by
  this run.
- Delete only that verified R2 temporary directory after all durable citation
  data has been written. This local temporary-source disposition is required
  by this prompt and is not authority to clean any repository, host workspace,
  retained evidence or pre-existing path.
- Do not preserve helper scripts or derived artifacts in an external
  scratchpad. Put any helper script needed for this run inside the verified
  temporary directory and delete it with that directory.
- Never point `grep`, `find`, `rg`, a link checker, a hashing loop or another
  recursive tool at the repository root or an unknown directory. Repository
  verification must operate from an explicit allowlist containing only the
  six files this assignment may create or update.

## Verification

Run only bounded local documentation and static-source checks:

- recompute this prompt's byte count and SHA-256 before work;
- validate the three exact Ubuntu `.dsc` checksum sets;
- compare each derived Polkit rule byte stream with the applicable durable R5
  digest without accessing the retained host evidence path;
- check repository-relative links by parsing only the six allowed files and
  testing their named repository-relative targets;
- run whitespace/trailing-space checks only on the six allowed files;
- run `git diff --check` for tracked documentation changes;
- scan the two new R2 files for the exact finding IDs `R1-F1` and `R1-F2`, the
  R1 nonconformance, Peter-notified status, non-retroactivity rule and the
  three exact newly authorized package versions; and
- review the six-file diff for accidental host, implementation, successor,
  cleanup, credential, secret, commit or push authority.

Do not run application tests, hook tests, formatters, builds, package tools,
remote-host checks or any unbounded repository scan.

End the handback exactly:

`OH-S2 R2 remediation awaits independent Codex review; no host, implementation, cleanup, OH-S3/OH-S4p or later slice is authorized.`

