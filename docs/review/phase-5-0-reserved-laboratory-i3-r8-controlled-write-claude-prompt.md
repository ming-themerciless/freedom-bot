# Claude prompt — AUTHORIZED — one fresh I3 controlled-write verification pass

> # AUTHORIZED 2026-09-21 — C-P5.0-LAB-I3-R8
>
> Peter Duscha authorizes C-P5.0-LAB-I3-R8 and assigns Claude as implementing
> operator for this exact accepted prompt. Codex remains the independent
> technical, security and evidence reviewer. This authority reaches nothing
> outside the prompt and ends after Claude's handback. It does not close I3.
> C-P5.0-LAB-I3-R7 is consumed and cannot be reused.

## Objective

Use the separately armed, independently reviewed I3 verifier to exercise the
four exclusive-publication contexts against the accepted manifest-version-17
tree on `oracle-test`: root first (T1 under V4, §2.3.3 under V5 and P2 under
temporary canonical `R/bin`), then `ubuntu` (T6 under V9) only after complete
root success. Return complete safe evidence for independent Codex review. The
operator cannot close I3.

## Governing context

Before acting, read completely and obey `.agents/AGENTS.md`; the implementation
plan reading map and §§0, 12 including Package 5.0, 13, 14, 16, 17 and 20; the
active handover; the current disposable-server restriction and §3.2
synchronization procedure; the R5 implementation handback and acceptance; the
R6 handback and its R6-R1 erratum; the R6-R1 and R6-R2 remediation handbacks;
the R7 prompt, stopped-pass handback, R7-R1 and R7-R2 remediation handbacks and
R7-R2 acceptance record; runner contract r6 especially §§1.3.3, 1.4.1–1.4.2,
6.2, 7.4 and 9.2–9.3; the I3 verifier, CLI, descriptor, case-runtime and
provisioning sources and tests; and the current status, RAID, decision and
change registers. Inspect Git status and preserve unrelated changes. Never
read, print, transfer or modify a secret file. Never use historical
`/opt/discord-bots/` paths.

## Every guard, tool or harness refusal ends the pass

**This section controls over every other instruction. There is no retry path.**

The following events each immediately consume the authority and end the entire
pass, whether they occur before or after host contact:

1. refusal by `guard-secrets.py`, `guard-git.py`, another `PreToolUse` guard or
   any repository guard;
2. denial, refusal, rejection or block by the client, execution harness,
   sandbox, permission classifier, policy layer or command tool;
3. a request or indication that elevated, bypass, unsandboxed, dangerous or
   exceptional tool permission is needed; or
4. any uncertainty whether a response is a refusal or whether the exact plain
   command executed.

On any such event, do not request approval, escalation or a permission
exception. Do not remove or add a tool parameter and re-issue. Do not re-quote,
split, unchain, reformulate, wrap, retry or substitute the command. Do not issue
any further host command, even a read-only inspection or cleanup command. Record
the exact attempted call and exact refusal in a repository-only stopped-pass
handback and return for maintainer direction and independent Codex review.

**Tool-call parameters are part of the attempt.** Use the client's ordinary,
default execution path only. Do not attach `dangerouslyDisableSandbox`,
`require_escalated`, an approval request, a sandbox bypass or any equivalent
parameter. If the ordinary path cannot issue the command, the pass stops.

## Exact first synchronization attempt

The first synchronization attempt must be exactly this one plain invocation,
with no preliminary synchronization, chained command, redirection,
substitution, wrapper, trailing comment or tool-level bypass parameter:

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

Do not use `--exclude-from` or alter any option or exclusion. A refusal or
denial before execution still consumes the pass under the preceding section.

## Authorized preparation

This activated pass authorizes only:

1. the exact synchronization above;
2. read-only confirmation that the synchronized tree is manifest version 17
   and reproduces review-input digest
   `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26`;
3. read-only confirmation that V1, V2, V3, V12, V4, V9 and V5 remain
   provisioned; V7 and canonical `/var/lib/fb-evidence-p5-0` remain absent; no
   `.fb-i3-verify-` residue exists; `protected_hardlinks=1`; nodename is `Test`,
   release is `7.0.0-31-generic`, architecture is `x86_64`; and
   `/opt/freedom-blades/runtime/venv-web/bin/python` is available; and
4. the two conditional verifier invocations below.

No database may be invoked and `TEST_DATABASE_URL` must not be set or required.
If any prerequisite is missing, changed, ambiguous or refused, stop before the
first controlled write. Do not repair, install, provision, chmod, chown, change
groups or capabilities, or initialize V7.

## No auxiliary host-side artifacts

Do not use `scp`, `sftp` or any second `rsync`. Do not create a file list,
capture file, output redirection, wrapper, script, scratch file or `/tmp`
object. Any comparison file set must be derived in-process on each host from
`review_manifest.COVERED_SOURCES`. Capture output only in the client transcript.

The only permitted host objects beyond the synchronized worktree are those
created and removed solely inside the reviewed verifier: the unique staged and
linked `.fb-i3-verify-<nonce>-*` objects in V4, V5, temporary canonical `R/bin`
and V9, plus temporary canonical `/var/lib/fb-evidence-p5-0` and `R/bin` for P2.
The operator must never manually inspect beyond the authorized surveys, create,
edit, move, repair or remove those objects. Residue ends the pass and must be
reported, not cleaned up.

The historical `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
`/tmp/fb-i3-r6-filelist.txt` are protected evidence. Do not read their contents,
stat, delete, truncate, overwrite, move, modify or reuse them.

## Exact verifier invocations

From `/opt/freedom-blades/platform` on `oracle-test`, run as root exactly:

```bash
sudo /opt/freedom-blades/runtime/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.i3_verifier_cli \
  --arm-i3-controlled-write --identity root
```

Proceed only if exit status is `0`, run status is `verified`, all three root
contexts are verified, every tracked object is removed, every barrier and
descriptor succeeds and the final survey is clean. Then, as the already
logged-in `ubuntu` identity and without `sudo`, run exactly:

```bash
/opt/freedom-blades/runtime/venv-web/bin/python \
  -m tools.phase_5_0_evidence.execution.i3_verifier_cli \
  --arm-i3-controlled-write --identity ubuntu
```

Do not add flags, use a wrapper or invoke a verifier object directly. Each
process must already have the identity named by its argument.

## Other stop conditions

Stop immediately without retry on any admission refusal, nonzero exit,
non-`verified` status, unattempted context, unexpected value, write, barrier,
link, cleanup, survey or descriptor failure, residue, operator-attention result
or output outside the reviewed safe vocabulary. Never manually repair or remove
residue, repeat an invocation, or run `ubuntu` after incomplete root success.

## Required handback

Write a dated repository handback under `docs/review/`, then reconcile the
active handover, implementation-plan §20 and current status, RAID, decision and
change registers only to what actually happened. Include:

* the exact synchronization call and result, including all tool-call parameters
  and whether the harness executed it;
* an explicit statement whether any repository guard, tool, harness, sandbox,
  classifier or policy refusal occurred, and whether any approval or escalation
  was requested;
* source identity, manifest version, artifact hashes, reproduced digest and all
  prerequisite observations;
* exact verifier argv, identities, UTC timestamps, exit statuses and complete
  safe stdout/stderr;
* all per-context status, nonce, stages, object identity, mode, owner condition,
  link counts, payload result, operation-time capabilities, tracked-object
  fates, barrier and descriptor counts, and final survey/residue;
* whether any host-side object outside the verifier-controlled exemption was
  created and whether the operator manually touched a verifier object;
* checks not run and why, and the precise resulting state.

Only an unbroken pass in which both invocations verify may be described as I3
performed; I3 still remains unclosed pending independent Codex review and
Peter's later decision. A stopped or partial pass leaves I3 unconfirmed.

## Exclusions and stop point

This authorization permits only the actions stated above. It authorizes no
source change, dependency installation, provisioning or permission change, V7,
participant or evidence-harness run, generated vector, database or service
action, real boundary or materializer, V8, V10, `--execute` or production
action. Success approves no digest and does not make the plan executable or
Package 5.0 ready. Stop after the handback for independent Codex review.

---

**Authorization reminder:** C-P5.0-LAB-I3-R8 is authorized once, for Claude as
implementing operator, and only for the exact actions in this prompt. Every
guard or tool/harness refusal immediately consumes the authority. Stop after
the handback for independent Codex review.
