# Claude prompt — implement the complete I3 controlled-write verifier — 2026-09-19

> **Superseded and consumed.** This pass stopped before implementation. Its
> P2/`CAP_FOWNER` requirement and decision-B restriction were replaced by
> C-P5.0-LAB-I3-D1: P2 is `root:root 0555`, relies on the filesystem-UID owner
> condition, and the armed verifier has narrow authority to create and remove
> temporary canonical `R`/`R/bin` topology. This prompt authorizes no work or
> host action.

Authorization: **C-P5.0-LAB-I3-R1**. Peter Duscha authorizes one bounded,
repository-only pass implementing a dedicated, explicitly armed operator entry
point for the complete current I3 controlled-write verification. Claude is the
implementing Technical Lead. Codex remains the Independent Technical and
Security Reviewer and must review the returned implementation before any I3
invocation on `oracle-test` is authorized.

## Assignment

Specify and implement one production operator entry point that can perform the
complete current I3 verification without initializing V7, invoking a
participant or the evidence harness, running a generated vector, accessing the
database or using `--execute`.

The verifier must cover every dependency currently assigned to I3, including:

1. filesystem support for the reviewed `linkat`/`unlinkat` exclusive-publication
   sequence in every materially distinct target context;
2. the owner-condition path used by T1, T6 and §2.3.3 under their reviewed
   execution identities; and
3. P2's `CAP_FOWNER` path in its contracted `R/bin` location, after reproducing
   P2's reviewed ownership and `0555` mode conditions.

Do not split, narrow or redefine I3. If the existing contract cannot support a
safe, complete verifier without a product, security, authority or topology
decision, stop and return the exact decision needed instead of choosing it.

## Required design

Make the complete procedure explicit in the runner contract and code. Define,
at minimum:

- the exact target directories and execution identity for each check;
- how the verifier obtains or creates the disposable `R` and `R/bin` topology
  required for P2 without entering the normal harness execution path;
- unique temporary and final naming rules that cannot collide with lifecycle,
  ledger, recovery or case-program records;
- one fixed harmless byte payload and its expected digest;
- descriptor acquisition, custody and no-follow requirements;
- exclusive creation, byte write, data barrier, reviewed ownership/mode
  transition, `linkat`, observation while both names exist, `unlinkat`, and
  containing-directory barrier ordering;
- byte equality, `(st_dev, st_ino)` and link-count observations;
- identity-guarded removal of both test names and any verifier-created
  disposable topology;
- fail-closed accounting for every partial state, including cleanup failure;
- a final bounded residue survey; and
- safe, closed-vocabulary operator output and distinct non-success exit codes.

Reuse the reviewed descriptor and filesystem abstractions where their contracts
fit. Do not route through lifecycle initialization, a participant, recovery
capture, case-program installation, the evidence harness or a generated plan
merely to reach the syscall. Do not duplicate a security-sensitive primitive
without documenting why the existing abstraction cannot safely serve it.

The entry point must be non-effecting by default. A deliberate command-line arm
specific to I3 is required, and deleting or bypassing one guard must not be
enough to cause an effect. It must refuse before the first write unless all
targets, identities, capabilities, ownership/mode assumptions, mount facts and
`fs.protected_hardlinks` facts match the reviewed contract.

## Governing context

Before changing anything, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 12 (Package 5.0), 13, 14, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. the active `docs/review/Handover information`;
4. the current restriction banner and relevant procedures in
   `docs/operations/disposable-test-server.md`;
5. runner contract r6, especially §§1.3.3, 1.4.1–1.4.2, 5.10–5.11, 6.2, 7,
   7.1–7.3 and 9.2–9.3;
6. the C-P5.0-LAB-I3 operator prompt and blocker handback;
7. the V6/I12 operational handback and independent closure review;
8. every implementation and test path that performs exclusive publication,
   descriptor-bound removal or containing-directory synchronization; and
9. the current status, RAID, decision and change registers.

Inspect Git status first and preserve all unrelated, prior-pass and
reviewer-authored changes. Do not read or print secret files.

## Required tests and evidence

Add public behavioral tests using temporary directories and controlled identity
or syscall seams. At minimum prove:

- no arm means no filesystem or account-database observation and no effect;
- every precondition mismatch refuses before the first write;
- each materially distinct owner/identity policy branch is exercised;
- P2's changed-owner, mode-`0555` case requires and observes the reviewed
  `CAP_FOWNER` condition rather than accidentally succeeding through ownership
  or write permission;
- the destination is claimed exclusively and an existing name is never
  overwritten;
- both names are observed as the same inode with link count two before removal;
- bytes and their digest remain exact;
- success removes both names, synchronizes the parent and leaves no residue;
- injected failure at every state boundary is accounted for and never reported
  as success;
- foreign/replaced names are not removed;
- cleanup or directory-barrier failure is a non-success with complete safe
  accounting; and
- malformed or unexpected exception text, paths and host data cannot reach
  operator output.

Include single-point reversals for the arm, precondition admission, exclusive
publication, identity comparison and residue/cleanup checks. Trace the new
tests to the applicable r6 §9 evidence rows, adding rows where necessary.

Run the narrow new tests first, then the complete
`tests/phase_5_0_evidence` suite locally and serially with
`TEST_DATABASE_URL` unset. Run the repository guards, `compileall` and
`git diff --check`. Report exact pass, fail, skip and warning counts and every
check not run. Do not claim PostgreSQL evidence from this restricted run.

If covered review artifacts change, regenerate them only through the
non-executing path, prove deterministic regeneration, and label every digest as
review input only. Never pass a digest to `--execute`.

## Restrictions and stop point

This is a repository-only implementation pass. **No host action is
authorized.** Do not SSH, synchronize, inspect or mutate `oracle-test`; invoke
`sudo`; change users, groups, permissions or capabilities; edit `/etc`; create
anything under the real `/run`, `/var/lib` or `/opt/freedom-blades`; initialize
V7; invoke a participant or harness; access a database; execute a generated
vector; use a real boundary/materializer; or use `--execute`.

Local temporary-directory tests may model the required topology and identities
through reviewed seams. They are not I3 operational evidence and confirm no
target fact.

Keep `plan.is_executable` false and
`reservation.REAL_EXECUTION_REFUSAL` unconditional. I3 remains unconfirmed;
V7 remains excluded; V8 and V10 remain unperformed; LAB-SECRETS-1 remains Open,
Low; LAB-V6-P2 remains deferred; and Package 5.0 remains not ready.

Return a dated implementation handback for independent Codex technical and
security review. Include requirements implemented, files changed, the complete
procedure and authority model, failure-state accounting, tests and reversals,
safe-output analysis, rollback of the repository change, checks not run and
reviewer focus areas. Claude closes no finding, confirms no I3 fact, approves no
digest and advances no gate. Stop after the handback. A later operational I3
run requires separate maintainer authorization after Codex accepts the
implementation.
