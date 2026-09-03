# Gemini prompt — Package 5.0 security evidence preflight

Status: **AUTHORIZED SUPPORTING ANALYSIS ONLY — CODEX REMAINS SECURITY REVIEWER**
Date: 2026-09-02

Copy this entire document into Gemini as one prompt.

---

You are Gemini, a supporting security-analysis agent for Freedom Blades Package
5.0. Codex remains the formally named Package 5.0 Security Reviewer and owns all
finding closure and recommendations. You are not an Independent Reviewer,
Acceptance Authority, decision owner or implementer for this task.

Work in `/opt/freedom-blades/platform`. Before planning or inspecting anything,
read `.agents/AGENTS.md` and `docs/implementation-plan.md` completely. Then read:

1. `docs/review/phase-5-0-security-rereview-revision-12.md`;
2. `docs/review/phase-5-0-security-review-brief.md`;
3. `docs/review/phase-5-0-package-plan.md`;
4. `docs/review/phase-5-0-logical-schema.md`;
5. `docs/review/phase-5-0-remediation-r11-handback.md`; and
6. the current status, RAID, decision register and active handover.

## Objective

Prepare an adversarial **preflight package** for the operational evidence still
needed before Package 5.0 can become ready. Do not run privileged cases and do
not implement Package 5.0.

Deliver one new document:

`docs/review/phase-5-0-gemini-security-evidence-preflight.md`

It must contain:

1. a requirement-to-evidence matrix for C-1, C-3, C-4, peer authentication,
   HBA ordering, capability masks/securebits, sandbox properties, journal
   lifecycle, provenance, append-only constraints, recovery and negative cases;
2. for every case, its exact prerequisite, identity, command or observation,
   expected positive control, expected refusal, safe output, cleanup owner and
   the decision/finding it can inform;
3. an inconsistency scan across package plan, logical schema, security brief,
   operations requirements and decision records, reporting duplicate authority
   statements, mismatched counts, stale option names and evidence that cannot
   construct the identity it claims;
4. a minimal ordering for executing the evidence without allowing a later case
   to invalidate an earlier result;
5. a list of steps requiring Peter's explicit authorization because they mutate
   host, database, accounts, groups, filesystem attributes, `sudoers`, HBA,
   services or credentials; and
6. residual questions for Codex, clearly labelled as questions rather than
   findings or recommendations.

## Restrictions

- Do not close or reclassify P5.0-SR1, P5.0-SR2, P5.0-R1, P5.0-R4 or P5.0-R5.
- Do not recommend Package 5.0 readiness or rule OD-62/64/65/66.
- Do not create migration `0014`, production code, accounts, groups,
  credentials, directories, object stores, approval/provenance records,
  database objects, systemd units or `sudoers`/HBA changes.
- Do not run `sudo`, privileged capability probes, Google operations, service
  restarts, deployments or cutovers.
- Do not read or print secrets, `.env` files, service-account JSON or tokens.
- Do not edit any controlled project record besides the one supporting preflight
  document named above.
- Treat every existing change in the dirty working tree as user-owned.

Use read-only host inspection only where already permitted. Mark everything not
actually observed as `Not Run` or `Unconfirmed`; never infer a pass from a
written procedure. Run `git diff --check` on your one-file change and return
`READY FOR CODEX EVIDENCE-PREFLIGHT REVIEW` or `BLOCKED`, with exact reasons.
