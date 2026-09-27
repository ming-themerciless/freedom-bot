# Claude prompt — draft the P5.0-R5 operational-evidence authorization prompt

**Assigned repository-only drafting task. This prompt authorizes Claude to
draft a later operational prompt; it does not authorize that later prompt,
host access, synchronization, evidence execution, database access or reboot.**

Codex remains the Independent Reviewer. Claude must not perform or represent
Codex's independent pre-execution review.

## Objective

Produce one bounded, technically executable **draft authorization prompt** for
the P5.0-R5 harness-facsimile feasibility-evidence pass on the approved
disposable target, `oracle-test`. The draft must be suitable for later Codex
independent technical, security and evidence review and later explicit Peter
Duscha authorization. Do not execute any part of the drafted pass.

Write the draft to:

`docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`

Also return a dated repository-only handback at:

`docs/review/phase-5-0-p5-r5-operational-evidence-prompt-drafting-handback.md`

## Governing context

Before drafting, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 12, 13, 15.1, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the current restriction banner and applicable operational rules in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-evidence-reconciliation-handback.md`;
6. the MD-1 through MD-6 decision records dated 2026-09-23 and 2026-09-24;
7. the complete C-P5.0-R5-R1 through R4 remediation, review and acceptance
   chain;
8. `docs/review/phase-5-0-package-plan.md`, especially §§2.12, 2.13, 6, 7.4,
   8, 9.2 and 9.4;
9. the current concrete plan, review manifest, generated artifact contract,
   implementation modules and focused P5.0 evidence tests;
10. the status, RAID, decision and change registers and OD-62/OD-66; and
11. the accepted disposable-laboratory operational-prompt precedents, using
    them for safety structure only rather than importing their authority or
    scope.

Inspect `git status` first. Preserve all pre-existing and unrelated work. An
uncommitted file is not absent merely because it is not in `HEAD`.

## Binding decisions the draft must preserve

- **MD-1:** independently reviewed harness-facsimile evidence from the
  approved disposable target may close P5.0-R5 feasibility; evidence from
  actual production journal code remains mandatory at the later
  implementation/release gate. Label the evidence classes separately.
- **MD-2:** only freshly observed `oracle-test` facts count as target facts.
  Package-plan §8.1 development-host observations are historical context.
- **MD-3:** the supervised reboot durability case is mandatory for P5.0-R5
  feasibility closure. It may not be Not Run or converted into a residual.
- **MD-4:** `R-5.0-10` through `R-5.0-16` are accepted active residual risks.
  Recovery rehearsals for `R-5.0-11`, `R-5.0-14` and `R-5.0-16` remain
  mandatory evidence.
- **MD-5:** the classifier corrections must have passed independent review
  before execution. The draft must include a preflight that proves the
  accepted corrected classifier and pinned artifacts are the ones deployed.
- **MD-6:** JNL-40(b)'s second-host or `/etc/machine-id` rewrite is not
  mandatory for P5.0-R5 closure. Do not execute it merely because it remains
  in historical catalogues.

## Required draft structure

The operational draft must contain:

1. an unmistakable **draft/not-authorized** banner;
2. the named target, operator, Independent Reviewer and authorization owner;
3. exact admission prerequisites and artifact/digest bindings;
4. one explicit synchronization method, source and destination, with no
   alternate or retry path;
5. exact commands in execution order, including the documented Python
   environment `/opt/freedom-blades/runtime/venv-web`;
6. a case-to-requirement matrix covering every P5.0-R5 feasibility proposition
   still required after MD-1 through MD-6;
7. separate bands for read-only preflight, provisioning, controlled mutation,
   database evidence where authorized, recovery rehearsal and reboot;
8. the mandatory supervised-reboot sequence, including pre-reboot durable
   state, operator confirmation, restart/identity checks and post-reboot
   verification;
9. mandatory recovery rehearsals for `R-5.0-11`, `R-5.0-14` and `R-5.0-16`;
10. precise expected outputs, artifact locations, ownership/modes, evidence
    manifest fields and independent-review inputs;
11. rollback and cleanup steps that preserve evidence and never use Git history
    rewrites or broad/destructive deletion;
12. per-band stop conditions, a global stop-on-refusal rule and an explicit
    no-retry rule unless a later authorization says otherwise;
13. rules for secrets, credentials and protected historical `/tmp` artifacts;
14. a final clean-state survey and a list of intended target-side changes;
15. a handback template that distinguishes measured facts from inference and
    records commands, return codes, pass/fail/skip counts, warnings, deviations,
    residue, rollback and checks not run; and
16. an explicit statement that successful feasibility evidence is not
    production-code evidence and does not authorize implementation or release.

Every command must be copyable, deterministic and scoped to the named target
and reviewed disposable paths. Resolve placeholders that can be resolved from
the repository. For values that require later observation or maintainer input,
declare typed preconditions and stop rather than inventing values.

## Safety and authority requirements

The drafted operational prompt must require all of the following before its
first host command:

- Codex independent pre-execution acceptance of the exact draft and pinned
  repository state;
- explicit Peter Duscha authorization of host access, synchronization,
  controlled mutation, database work and the supervised reboot;
- confirmation that no newer handover or restriction supersedes the prompt;
- confirmation of the approved target identity; and
- confirmation that the target contains no production data or credentials.

The draft must prohibit production-host access, production credentials,
production Google Sheets, production databases, migration `0014` outside an
explicitly authorized disposable database, and any change to the live Freedom
bot. It must not touch or inspect protected historical `/tmp` artifacts.

Do not weaken a guard, bypass a refusal, silently substitute a command, broaden
a path, use `git reset --hard`/`git checkout --`, or construct a retry after a
stop condition. A guard or permission refusal consumes the later operational
pass unless fresh authorization explicitly says otherwise.

## Work authorized now

This assignment authorizes only repository reads, drafting the two documents
named above, and safe repository-only consistency checks. Focused local tests
may be run only if they access no database, network, credential, service or
protected artifact and directly validate text or command construction in the
draft. Keep `TEST_DATABASE_URL` unset.

Do **not** SSH, synchronize, inspect `oracle-test`, use `sudo`, access any
database, invoke a verifier or evidence band, provision anything, create an
identity, change permissions, perform a controlled write, reboot a host, or
access protected `/tmp` artifacts. Do not run a secrets scan or a command
expected to engage a secrets guard. If any guard or tool refuses a call, stop
without reformulation or retry and report it.

Do not change application source, tests, hooks, manifests, generated evidence
artifacts, migrations, schema or configuration. Do not set
`plan.is_executable=True`, close P5.0-R5, make OD-62 G-A binding, declare
Package 5.0 ready, approve a digest or authorize the drafted prompt.

## Handback

The handback must list:

- files read and changed;
- decisions and restrictions carried into the draft;
- the exact evidence scope included and excluded;
- every unresolved placeholder or prerequisite;
- security, data-authority, rollback and reboot implications;
- checks run and checks not run; and
- a proposed Codex independent-review checklist.

Run `git diff --check`. Stop after returning the draft and handback for Codex
independent review.
