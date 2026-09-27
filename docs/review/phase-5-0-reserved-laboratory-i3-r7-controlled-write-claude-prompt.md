# Claude prompt — AUTHORIZED — one clean I3 controlled-write verification pass

> # AUTHORIZED 2026-09-20 — C-P5.0-LAB-I3-R7
>
> **Peter Duscha authorizes this bounded operational pass and assigns Claude as
> implementing operator.** The prompt was prepared under C-P5.0-LAB-I3-R6-R1;
> its host-side-artifact rule corrected 2026-09-20 under C-P5.0-LAB-I3-R6-R2.
> Both remediations have received independent Codex review and maintainer
> acceptance. This authorization is effective only with the matching entries in
> the active handover, implementation-plan §20, disposable-server restriction
> and registers, and only for the exact scope below.
>
> This authorization does not close, mitigate or discharge
> PR-20260920-LAB-I3-R6-1 or PR-20260920-LAB-I3-R6-2. Both remain **Open,
> Blocking**. I3 remains **unconfirmed and not closed**.

## Why this pass exists

C-P5.0-LAB-I3-R6 is consumed and cannot be retried under its authority. Its
verifier runs occurred and returned internally coherent `verified` results, but
the pass continued past a mandatory guard stop condition and performed an
unauthorized host write, so it is not acceptable gate evidence. This
authorization releases **one clean operational pass** so that the operational
question can be settled by a pass whose authority was never
in doubt. It deliberately retains the accepted R6 verifier order, prerequisites,
evidence requirements and stop conditions, and tightens exactly the two points
the findings identified.

## Objective

Use the separately armed, independently reviewed I3 verifier to exercise all
four exclusive-publication contexts against the accepted manifest-version-17
tree on `oracle-test`: run the root invocation (T1 under V4, §2.3.3 under V5 and
P2 under temporary canonical `R/bin`, in that order), then only after it returns
`verified` with exit status `0`, run the `ubuntu` invocation (T6 under V9).
Return complete safe evidence for independent Codex review. Do not declare I3
closed; Peter decides closure after that review.

## Governing context

Before acting, read completely and obey `.agents/AGENTS.md`; the implementation
plan reading map and §§0, 12 (Package 5.0), 13, 14, 16, 17 and 20; the active
handover; the current disposable-server restriction and §3.2 synchronization
procedure; the R5 implementation handback and acceptance; the R6 handback
**including its R6-R1 erratum** and the R6-R1 remediation handback **including
its R6-R2 erratum**, and the R6-R2 remediation handback; runner contract r6
especially §§1.3.3, 1.4.1–1.4.2, 6.2, 7.4 and 9.2–9.3; the I3 verifier, CLI,
descriptor, case-runtime and provisioning sources and tests; and
current status, RAID, decision and change registers. Inspect Git status and
preserve unrelated, earlier-pass and reviewer-authored changes. Never read,
print, transfer or modify a secret file. Do not use historical
`/opt/discord-bots/` paths.

## Guard refusals end the pass — no exceptions

**This section overrides any contrary reading of anything else in this prompt.**

1. Any refusal by `.claude/hooks/guard-secrets.py`, `.claude/hooks/guard-git.py`
   or any other `PreToolUse` guard, at any point and for any reason,
   **immediately ends the entire pass.**
2. On such a refusal: issue no further command of any kind against the host, do
   not re-issue the refused command in any form, do not reformulate, re-shape,
   unchain, split, re-quote, retry or otherwise adjust it, and do not proceed to
   synchronization or to either verifier invocation. **Removing the offending
   construct and re-issuing does not cure the stop.**
3. Record the exact refused call and the exact refusal, write the handback
   stating that the pass ended at a mandatory stop condition with no
   synchronization and no invocation performed, and return it for maintainer
   direction. The authority is then consumed.
4. A guard refusal is **never** to be described as a defect in the guard, as a
   stylistic matter, or as an obstacle that was "resolved". It is a stop.

## The first synchronization attempt must be the exact plain command

The **first** command issued for synchronization must be the exact accepted
inline runbook §3.2 `rsync` command, as **one plain `rsync` invocation** with
its single-quoted exclusions — with **no preliminary chained form**, no `date`
or any other command chained before or after it, no `&&`, `;` or `|`, no
substitution, no redirection and no trailing comment:

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

Do not use `--exclude-from`, do not alter, add or remove an exclusion or option,
and do not work around a guard refusal. If timestamps are wanted, take them in
their own separate calls **before** and **after** this one; they are never part
of it.

## No host-side artifacts beyond the reviewed verifier-controlled objects

**Prohibited outright: `scp`, `sftp`, `rsync` of any file other than the
synchronization above, operator-created remote temporary files, and every other
auxiliary host-side artifact.** Specifically, do not create, copy or write any
file or directory on the target other than (a) what the authorized
synchronization writes into `/opt/freedom-blades/platform` and (b) the reviewed
verifier-controlled objects defined immediately below; and do not create a file
list, a capture file, an output redirection, a shell wrapper, a script, a
scratch file or a `/tmp` object of any kind.

### The one narrow exemption — the reviewed verifier-controlled objects

The two exact verifier invocations authorized below necessarily create, publish,
observe and remove filesystem objects of their own. That is the behavior under
verification, it is what the separately armed and independently reviewed
verifier implementation does, and an operator cannot both issue those two
commands and prevent those objects from existing. The prohibition above
therefore does not reach, **and reaches nothing beyond**:

* the temporary exclusively-created payload file `.fb-i3-verify-<nonce>-staged`
  and the published hard link `.fb-i3-verify-<nonce>-linked`, in each of the
  four reviewed publication directories — V4 for T1, V5 for §2.3.3, temporary
  canonical `R/bin` for P2, and V9 for T6; and
* in the P2 context only, the temporary canonical root
  `/var/lib/fb-evidence-p5-0` and its `bin` subdirectory, created and removed
  within that context.

Nothing else on the host is exempt, and the exemption is not an operational
authority. In particular it:

1. **confers no operator permission over these objects.** It does not permit an
   operator to create, rename, replace, edit, move, copy, preserve, repair or
   remove any verifier object manually, by any command, before, during or after
   either invocation. **All verifier-object creation and cleanup must occur
   solely inside the reviewed verifier implementation, under the two exact
   invocations below.** The operator issues those two commands and touches
   nothing they create or leave behind;
2. **does not widen either invocation.** No flag may be added, no ad hoc wrapper
   used and no verifier object invoked directly, exactly as stated below; and
3. **does not excuse residue or a cleanup failure.** A cleanup failure, a
   surviving verifier name or a non-clean final survey remains a stop condition
   to be recorded and reported, never tidied up, repaired or retried.

Any file set needed for a digest comparison must be derived **in-process** on
each host from `review_manifest.COVERED_SOURCES`, never transferred. Capture all
output in the client/tool transcript.

The following files are **historical evidence and must be preserved exactly**:

* `/tmp/fb-i3-root.out`
* `/tmp/fb-i3-root.err`
* `/tmp/fb-i3-r6-filelist.txt`

Do not delete, truncate, overwrite, move, modify or reuse any of them, and do
not read their contents; `stat` metadata only. `/tmp/fb-i3-r6-filelist.txt` is
the subject of an Open, Blocking finding and its disposition is the maintainer's
alone — **tidying it up is not permitted and would be a further unauthorized
write.**

## Authorized preparation

This pass authorizes only:

1. synchronize the workspace to `/opt/freedom-blades/platform` on `oracle-test`
   using the exact plain command above, as the first synchronization attempt;
2. establish read-only that the synchronized tree is manifest version 17 and
   reproduces review-input digest
   `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26`;
3. establish that V1, V2, V3, V12, V4, V9 and V5 remain provisioned; V7 and
   canonical `/var/lib/fb-evidence-p5-0` remain absent; no `.fb-i3-verify-`
   residue exists; `protected_hardlinks=1`; the target reports nodename `Test`,
   release `7.0.0-31-generic` and architecture `x86_64`; and
   `/opt/freedom-blades/runtime/venv-web/bin/python` is available; and
4. invoke no database and set or require no `TEST_DATABASE_URL`.

If any prerequisite is missing, changed, ambiguous or refused, stop before the
first controlled write. Do not repair, provision, install, chmod, chown, create
a group, change a capability or initialize V7.

## Authorized verifier invocations

From `/opt/freedom-blades/platform` on `oracle-test`, run as root using exactly:

```bash
sudo /opt/freedom-blades/runtime/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.i3_verifier_cli \
  --arm-i3-controlled-write --identity root
```

Proceed only if exit status is `0`, run status is `verified`, all three root
contexts are verified, every tracked object is removed, every barrier and
descriptor succeeds, and the final survey is clean. Then run as the already
logged-in `ubuntu` identity, without `sudo`:

```bash
/opt/freedom-blades/runtime/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.i3_verifier_cli \
  --arm-i3-controlled-write --identity ubuntu
```

Do not add flags, use an ad hoc wrapper or invoke the verifier object directly.
Each process must already be the identity named by its argument.

## Stop conditions

Stop immediately and do not retry on: **any guard refusal** (see above); any
admission refusal, nonzero exit, non-`verified` status, unattempted context,
unrecognized value, write/barrier/link/cleanup/survey/descriptor failure,
residue, operator-attention result or output outside the reviewed safe
vocabulary; and any need that would be met only by a prohibited host-side
artifact. Do not manually repair or remove residue, repeat an invocation, or run
`ubuntu` after a non-successful root run.

## Required handback

Write a dated operational handback under `docs/review/`, place its state banner
and pointer at the top of the active handover, and update §20 and the status,
RAID, decision and change registers only with what actually occurred. Include
the exact synchronization command/result; source identity, manifest version,
artifact hashes and reproduced digest; all prerequisite observations; exact
verifier argv, identities, UTC timestamps, exit statuses and complete safe
stdout/stderr; all per-context status, nonce, stages, object identity, mode,
owner condition, link counts, payload result, operation-time capabilities,
tracked-object fates, barrier and descriptor counts; final survey/residue;
**an explicit statement of whether any guard refusal occurred and whether any
host-side artifact outside the reviewed verifier-controlled exemption was
created**, with confirmation that every verifier object was created and removed
solely inside the verifier under the two exact invocations and that the operator
touched none of them; checks not run and why; and the precise
resulting state. I3 is **performed but not closed** only if both invocations
verify under an unbroken authority; otherwise it remains unconfirmed.

Do not claim behavior beyond the four contexts or capability causation.
Successful verification does not approve a digest, initialize V7, make the plan
executable or make Package 5.0 ready.

## Restrictions and stop point

This authorization permits only the exact §3.2 synchronization, necessary
read-only prerequisite inspection and the two armed verifier invocations above.
It would not authorize source changes, dependency installation, provisioning or
permission changes, V7, a participant or evidence-harness run, a generated
vector, database access, service changes, a real boundary or materializer, V8,
V10, `--execute`, or production action. Stop after the handback for fresh
independent review. I3 is not closed by the operator. V7 remains excluded;
`plan.is_executable=False`; Package 5.0 remains not ready; LAB-SECRETS-1 remains
Open, Low; LAB-V6-P2 remains deferred.

---

**Authorization reminder: `C-P5.0-LAB-I3-R7` is authorized once, for Claude as
implementing operator, and only for the exact synchronization, read-only
prerequisite inspection and two conditional verifier invocations above. Any
guard refusal immediately consumes this authority. Stop after the handback for
fresh independent review.**
