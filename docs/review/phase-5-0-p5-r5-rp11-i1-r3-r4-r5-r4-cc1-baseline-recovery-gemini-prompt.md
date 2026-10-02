# Gemini prompt — R-5 R4 `cc1.v` baseline recovery

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R4`

Date: 2026-10-01

Assignee: Gemini

Status: **accepted and authorized by Peter Duscha; recovery only**

## 1. Objective and success condition

Attempt to recover the exact `cc1.v` bytes retained from Claude's accepted
I-7 or I-7-R1 run. The sole accepted digest is:

```text
b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b
```

Success requires recovering an existing historical artifact and independently
computing that exact SHA-256. A digest mention in documentation, reconstructed
text, a newly generated file, or a file with any other digest is not success.

If the exact bytes cannot be recovered within the sources and boundaries below,
stop and report failure. Do not rebuild them, substitute another artifact, or
rerun R-5.

## 2. Required context

Before acting, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §13, §16, §17 and §20;
3. `docs/review/Handover information`;
4. the accepted D2 design §§5.3.2–5.3.8 and §5.12.3;
5. Claude's I-7 and I-7-R1 prompts and handbacks;
6. the R-5 assignment and stopped handback;
7. the R2 and R3 prompts, handbacks, and R3 acceptance decision; and
8. this prompt.

Inspect `git status` and preserve all existing changes.

## 3. Authorized recovery sources

Use read-only inspection first. The search is limited to:

1. the repository worktree, including its existing untracked files but
   excluding `.git` object contents;
2. exact scratch paths or retained artifacts explicitly named in the I-7 or
   I-7-R1 records; and
3. Claude I-7/I-7-R1 session artifacts or attachments directly exposed to
   Gemini by the collaboration client, if any.

Do not broadly crawl `/tmp`, home directories, agent configuration, caches,
logs belonging to other tasks, shell history, credentials, secret files,
process environments, `/proc`, or the full filesystem. If no exact candidate
location is documented or directly exposed, that source is unavailable; this
is not authority to expand the search.

Do not contact Claude or another agent unless Peter separately provides that
coordination mechanism and authority.

## 4. Candidate handling and verification

For each candidate that is specifically attributable to I-7 or I-7-R1:

1. record its precise provenance without changing it;
2. compute SHA-256 using a local read-only operation;
3. compare it with the accepted digest; and
4. reject it as baseline evidence if the digest differs.

Do not print the full candidate contents into logs. It is sufficient to record
the path or artifact identifier, byte length, digest, provenance and verdict.

If and only if a candidate matches exactly:

1. copy its bytes without transformation to
   `infra/rp11-launch/verify/fixtures/cc1.v.baseline`;
2. compute the digest of both source and retained copy and require exact
   equality;
3. run the accepted `cc1check.py` against the source and retained copy and
   require `PASS`;
4. do not normalize line endings, decode/re-encode, edit, regenerate or
   otherwise transform the bytes; and
5. record enough provenance for independent review.

Creating the fixture is authorized only for an exact digest match. If no match
is found, do not create a placeholder or empty fixture.

## 5. Required result branches

### Branch A — exact artifact recovered

Retain the verified fixture and write the handback in §7. State only that the
historical baseline bytes were recovered and authenticated by the previously
recorded digest. Do not claim that the unexplained Gemini difference has been
causally resolved; that requires a later exact comparison and review.

### Branch B — exact artifact not recovered

Write the handback in §7 with every authorized source checked, why it was
available or unavailable, and any candidate digest. State clearly that
baseline recovery failed and that a separate maintainer decision would be
required before any reference reproduction. Stop without creating a fixture.

## 6. Restrictions

No SSH, rsync, `oracle-test`, network access, download, `sudo`, package action,
provisioning, build-root creation, compiler or launcher build, R-5 rerun,
reference-environment reproduction, service or database action, H-1/H-2,
PO-14 discharge, RP-11 wiring, controlled write, reboot, evidence band,
harness `--execute`, operational path, protected-artifact access, secrets scan,
commit or push is authorized.

Do not change any existing source, test, digest, lock, manifest, listing,
governance document, handback or accepted artifact. The only implementation
artifact Gemini may create is the exact-match fixture named in §4. Gemini may
also create the single handback named in §7.

Do not treat Claude's digest alone as recoverable content. Do not guess or
reconstruct `cc1.v` from documentation. Do not use Gemini's stopped-run
`cdc0fe11…45f9` file as the baseline.

## 7. Required handback and stop gate

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-handback.md`

Include:

* the result branch, success or failure;
* every authorized source inspected and the exact bounded commands or client
  operations used;
* candidate provenance, byte length, SHA-256 and disposition;
* fixture source/copy equality and `cc1check.py` result, if Branch A;
* checks not run and why;
* residual trust and unresolved evidence;
* security, configuration, deployment and rollback implications; and
* proposed independent-review focus.

Stop after the handback. Even if recovery succeeds, do not compare it with a
new build, explain Gemini's differing bytes, access a host, or rerun R-5.
