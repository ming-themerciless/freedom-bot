# Claude prompt — retry the accepted I3 controlled-write verification

**Status: authorized 2026-09-20.** Peter Duscha authorizes
**C-P5.0-LAB-I3-R6** and assigns Claude as implementing operator for the bounded
operational I3 verification described here. Codex remains the Independent
Technical, Security and Evidence Reviewer and does not perform the operation.

## Authorization statement supplied by Peter

> I authorize C-P5.0-LAB-I3-R6 and assign Claude as implementing operator for
> the bounded operational I3 verification described in the prompt.

## Objective

Use the separately armed, independently reviewed I3 verifier to exercise all
four exclusive-publication contexts against the accepted manifest-version-17
tree on `oracle-test`: run the root invocation (T1 under V4, §2.3.3 under V5
and P2 under temporary canonical `R/bin`, in that order), then only after it
returns `verified` with exit status `0`, run the `ubuntu` invocation (T6 under
V9). Return complete safe evidence for independent Codex review. Do not declare
I3 closed; Peter decides closure after that review.

## Governing context

Before acting, read completely and obey `.agents/AGENTS.md`; the implementation
plan reading map and §§0, 12 (Package 5.0), 13, 14, 16, 17 and 20; the active
handover; the current disposable-server restriction and §3.2 synchronization
procedure; the R5 implementation handback and acceptance; runner contract r6
especially §§1.3.3, 1.4.1–1.4.2, 6.2, 7.4 and 9.2–9.3; the I3 verifier, CLI,
descriptor, case-runtime and provisioning sources and tests; and current status,
RAID, decision and change registers. Inspect Git status and preserve unrelated,
earlier-pass and reviewer-authored changes. Never read, print, transfer or
modify a secret file. Do not use historical `/opt/discord-bots/` paths.

## Authorized preparation

This pass authorizes only:

1. synchronize the workspace to `/opt/freedom-blades/platform` on `oracle-test`
   using the **exact accepted inline §3.2 `rsync` command** with its
   single-quoted exclusions; do not use `--exclude-from`, alter the exclusions
   or work around a guard refusal;
2. establish read-only that the synchronized tree is manifest version 17 and
   reproduces review-input digest
   `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26`;
3. establish that V1, V2, V3, V12, V4, V9 and V5 remain provisioned; V7 and
   canonical `/var/lib/fb-evidence-p5-0` remain absent; no
   `.fb-i3-verify-` residue exists; `protected_hardlinks=1`; the target reports
   nodename `Test`, release `7.0.0-31-generic` and architecture `x86_64`; and
   `/opt/freedom-blades/runtime/venv-web/bin/python` is available; and
4. invoke no database and set or require no `TEST_DATABASE_URL`.

The prior `/tmp/fb-i3-root.out` and `/tmp/fb-i3-root.err` files are historical
evidence. Do not delete, truncate, overwrite or reuse them. Capture output in
the client/tool transcript; do not create an unreviewed shell wrapper or new
host-side capture file.

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

Stop immediately and do not retry on any admission refusal, nonzero exit,
non-`verified` status, unattempted context, unrecognized value, write/barrier/
link/cleanup/survey/descriptor failure, residue, operator-attention result or
output outside the reviewed safe vocabulary. Do not manually repair or remove
residue, repeat an invocation, or run `ubuntu` after a non-successful root run.

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
checks not run and why; and the precise resulting state. I3 is **performed but
not closed** only if both invocations verify; otherwise it remains unconfirmed.

Do not claim behavior beyond the four contexts or capability causation.
Successful verification does not approve a digest, initialize V7, make the plan
executable or make Package 5.0 ready.

## Restrictions and stop point

This authorization permits only the exact §3.2 synchronization,
necessary read-only prerequisite inspection and the two armed verifier
invocations above. It does not authorize source changes, dependency installation,
provisioning or permission changes, V7, a participant or evidence-harness run,
a generated vector, database access, service changes, a real boundary or
materializer, V8, V10, `--execute`, or production action. Stop after the
handback for fresh independent review. I3 is not closed by the operator. V7
remains excluded; `plan.is_executable=False`; Package 5.0 remains not ready;
LAB-SECRETS-1 remains Open, Low; LAB-V6-P2 remains deferred.
