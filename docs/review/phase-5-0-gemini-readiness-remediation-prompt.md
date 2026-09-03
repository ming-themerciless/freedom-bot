# Gemini remediation handover — Package 5.0 readiness artifacts R1

Work in `/opt/freedom-blades/platform`.

## Authority and purpose

Your pre-implementation readiness handback was useful and stayed within its
mutation boundary. Codex, acting as the named Package 5.0 Security Reviewer,
has reviewed it and requires a bounded correction to the three Gemini-authored
artifacts.

This prompt authorizes **documentation remediation only**. It does not authorize
Package 5.0 implementation, migration `0014`, database or host changes,
privileged evidence collection, deployment, cutover, production work, Package
5.1+, owner decisions, risk acceptance, assumption confirmation, finding
closure, or a gate decision.

Codex retains the Security Reviewer, Independent Reviewer and logical-schema
reviewer roles. Peter Duscha retains every approval and accountable-owner role
recorded in the controlled documents. Your corrected artifacts remain advisory
inputs; they do not become controlled rulings or the official security review.

## Required reading

Before editing, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/phase-5-0-gemini-preimplementation-prompt.md`;
4. `docs/review/phase-5-0-gemini-readiness-analysis.md`;
5. `docs/review/phase-5-0-gemini-decision-matrix.md`;
6. `docs/review/phase-5-0-gemini-operational-evidence-runbook.md`;
7. `docs/review/phase-5-0-security-review-brief.md`;
8. `docs/review/phase-5-0-security-review.md`;
9. `docs/review/phase-5-0-remediation-r11-handback.md`;
10. the relevant sections of `docs/review/phase-5-0-package-plan.md`:
    §§2.12.2, 2.12.5a, 2.12.6, 2.13.5a–c, 2.13.8, 8.1, 9.2–9.4;
11. the relevant sections of `docs/review/phase-5-0-logical-schema.md`:
    §§3.7, 3.8, 4.3.2–4.3.8; and
12. OD-62 through OD-66 in `docs/discovery/open-decisions.md`, the corresponding
    decision-register rows, and `docs/review/phase-5-0-od-63-ruling-draft.md`.

Check `git status` before editing. Preserve the intentionally dirty tree. Do not
reset, revert, stage, commit, reformat, or modify any file except the three
Gemini-authored deliverables named below.

## Reviewer disposition you must incorporate

### 1. G-RA-1 is not an Important finding

Withdraw **G-RA-1 — Origin-fetch authentication not specified** as a finding.
Preserve its useful supply-chain question as a clearly labelled
**non-blocking design note**, with the following reasoning represented
accurately:

- The out-of-band approval record carries the independently approved SHA-256
  `source_manifest_digest`.
- Algorithm D recomputes that digest from the selected Git object bytes and
  refuses disagreement before deployment provenance is registered.
- A malicious or unauthenticated origin can withhold the approved object,
  return unrelated objects, advertise excessive objects, or otherwise cause an
  availability/resource failure. It cannot cause different deployed source
  bytes to match the independently approved SHA-256 manifest without breaking
  the SHA-256 binding.
- Fetching broadly rather than narrowly may be an operational efficiency or
  denial-of-service concern, but it does not widen R-5.0-15 from A5 to a
  network-only attacker while the approval digest remains independently fixed.
- Certificate pinning, signed tags, or a new signing-key system would be new
  policy and operational complexity. Do not prescribe one as the smallest
  remediation to P5.0-SR1.

You may recommend that the eventual operations document specify an
authenticated transport and bounded fetch behavior as defense in depth. Do not
call their absence a Blocking or Important defect in revision 12, and do not
invent a sixth residual from it.

### 2. G-RA-2 is outstanding evidence, not an Important finding

Withdraw **G-RA-2 — `pg_hba.conf`/`pg_ident.conf` isolation depends on current
file state not yet confirmed** as a finding. Preserve it as an **operational
evidence prerequisite**.

Represent these distinctions exactly:

- Revision 12 specifies the required first-match ordering, peer map, explicit
  rejects, `PASSWORD NULL`, grants and post-reload positive/negative tests.
- The proposed configuration does not exist yet because implementation is not
  authorized. Failure to possess post-implementation evidence before the
  objects exist is not a design defect.
- Existing-file inspection before change, exact insertion placement, syntax
  validation, reload, and the complete authentication-denial matrix remain
  mandatory gate evidence. No security-readiness recommendation may be treated
  as proof those checks passed.
- **C-4/JNL-52 is the operating-system membership and filesystem-access matrix.**
  Do not describe it as the `pg_hba.conf`/`pg_ident.conf` authentication test.
  The database host-boundary evidence is the package plan/logical schema's
  separate Band 2 matrix. Use the controlled artifact's exact evidence label
  when naming it; if no single `C-*` shorthand exists, do not invent one.
- A pre-existing broad or `trust` rule would be discovered by the required
  configuration inspection and would constrain insertion ordering or stop the
  rehearsal. Record that as a check, not as a confirmed defect.

### 3. G-RA-3 remains an Optional observation

Keep the SIGKILL/cleanup-residue discussion only as an Optional observation or
cross-reference to R-5.0-14. State that the design already specifies fail-closed
next invocation, operator cleanup and the residue availability cost. Do not
request a design remediation and do not imply R-5.0-14 has been accepted.

### 4. Correct the security-review conclusion

Update the advisory analysis to state Codex's disposition accurately:

- P5.0-SR1 is **materially addressed on paper** by revision 12.
- P5.0-SR2 is **materially addressed on paper** by revision 12.
- The Gemini analysis identifies no additional Blocking or Important security
  design finding after the two classifications above are corrected.
- Operational evidence, owner decisions and risk acceptance remain outstanding.
- The advisory document itself does not close P5.0-SR1/P5.0-SR2 or issue the
  official §9.2 recommendation. Codex records those actions separately.
- Package 5.0 remains `not ready`, and implementation remains unauthorized.

Do not rewrite the original `docs/review/phase-5-0-security-review.md`; it is a
received review artifact and must retain its original revision-11 outcome.

### 5. Correct the decision sequence everywhere

The controlled sequence is:

1. **OD-63 is rulable now** and has no Security Reviewer predecessor. Peter may
   review and sign its existing draft now.
2. Codex delivers the revision-12 §9.2 security disposition/recommendation.
3. The accountable owners may then rule **OD-64, OD-65 and OD-66** in their
   documented dependency order. Do not silently assume those three are mutually
   independent; preserve any predecessor relationship their decision records
   state, including OD-65 before an OD-66 option whose subject depends on the
   artifacts OD-65 adopts.
4. The appropriate owner explicitly authorizes the disposable/privileged
   operational evidence. The evidence is then executed and reviewed; an
   authorization is not evidence.
5. **OD-62 is ruled last**, consuming the preceding decisions, evidence and
   explicit residual-risk pricing.

Remove or correct every statement that places OD-63 after OD-64/65/66 or after
the security recommendation. In particular, correct the readiness analysis's
cross-document table and any dependency diagrams or prose in the decision
matrix.

### 6. Correct residual and count wording

Use one vocabulary consistently:

- R-5.0-12 through R-5.0-16 are **five unaccepted residuals**.
- If management records distinguish previously recorded from newly proposed
  rows, say so separately without implying that the first three are accepted.
- There are twelve security surfaces, seven proposed tables, five append-only
  histories/triggers, eleven authorities, 53 evidence identifiers, 114 evidence
  cases, PERT 47.6 implementer-days, 13.9 remediation days and 4.5–5.5
  reviewer-days.
- Confirm package-plan §5.1 directly. If it reads 47.6, replace G-CB-1's
  uncertainty with a verified informational note or remove the note. Do not say
  a fact was unverifiable merely because editing its file was prohibited;
  reading was authorized.

Do a fresh cross-document search rather than changing only the instances named
here.

## File-specific changes

Edit exactly these existing files:

1. `docs/review/phase-5-0-gemini-readiness-analysis.md`
   - revise the executive outcome, review matrix, §4 dispositions, findings,
     residual analysis, consistency table and next-action sequence;
   - retain the useful adversarial reasoning, but clearly distinguish findings,
     defense-in-depth notes and unexecuted evidence;
   - use stable labels such as `G-NOTE-1` and `G-EVIDENCE-1` if renaming
     G-RA-1/G-RA-2 helps prevent stale citations;
   - include a short remediation note saying the original classifications were
     withdrawn following Security Reviewer review.
2. `docs/review/phase-5-0-gemini-decision-matrix.md`
   - correct OD-63's timing and every sequence/dependency statement;
   - ensure no option is selected and no owner recommendation or signature is
     fabricated;
   - remove G-RA-1/G-RA-2 as open Important prerequisites;
   - retain mandatory operational evidence as evidence, not design closure;
   - keep OD-62 last.
3. `docs/review/phase-5-0-gemini-operational-evidence-runbook.md`
   - correct the C-4 versus database Band 2 taxonomy;
   - keep all privileged/mutating commands explicitly marked **do not run
     without authorization**;
   - do not claim absent pre-implementation objects are expected safe results;
     distinguish pre-provisioning discovery, post-provisioning validation and
     production-like evidence;
   - preserve cleanup/recovery instructions and never claim an unrun command
     passed.

Do not create a fourth handback file. Add a concise remediation history section
inside `phase-5-0-gemini-readiness-analysis.md` instead.

## Prohibited changes and actions

Do not modify:

- `.agents/AGENTS.md`;
- `docs/implementation-plan.md`;
- `docs/project-management/**`;
- `docs/discovery/**`;
- `docs/review/Handover information`;
- the Package 5.0 package plan, logical schema, security brief, original
  security review, R11 handback or OD-63 ruling draft;
- any production code, tests, migration, configuration or infrastructure file;
  or
- the Gemini prompt files.

Do not use `sudo`, `su`, `systemd-run`, identity-construction commands,
`chattr`, `setcap`, account/group tools, service commands, database DDL/DML,
network access, or Git-writing commands. Do not read secrets, environment files,
credentials, tokens or private keys.

## Verification

Run only read-only repository checks:

```sh
git status --short
git diff --check -- \
  docs/review/phase-5-0-gemini-readiness-analysis.md \
  docs/review/phase-5-0-gemini-decision-matrix.md \
  docs/review/phase-5-0-gemini-operational-evidence-runbook.md

rg -n "G-RA-1|G-RA-2|Important finding|OD-63|C-4|JNL-52|Band 2|five unaccepted|three unaccepted" \
  docs/review/phase-5-0-gemini-readiness-analysis.md \
  docs/review/phase-5-0-gemini-decision-matrix.md \
  docs/review/phase-5-0-gemini-operational-evidence-runbook.md
```

Inspect every search hit manually. A historical reference to the withdrawn
classification is permitted only inside the remediation-history section and
must say explicitly that it was withdrawn.

## Handback

Return a concise report containing:

- files changed and why;
- exact disposition of former G-RA-1, G-RA-2 and G-RA-3;
- corrected decision sequence;
- corrected C-4/Band 2 taxonomy;
- every stale reference found and corrected;
- commands run and exact results;
- checks not run and why;
- confirmation that only the three authorized files changed; and
- confirmation that Package 5.0 remains `not ready` and implementation remains
  unauthorized.

Stop and report rather than edit if the controlled documents contradict the
reviewer disposition or if a correction would require changing a controlled
artifact.
