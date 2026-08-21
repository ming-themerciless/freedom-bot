# P3.4 remediation release-policy clarification

Date: 2026-08-20

Status: **ACCEPTED AND EFFECTIVE**

Acceptance and release authority: Peter Duscha

## Decision

Peter clarified the P3.4 remediation workflow on 2026-08-20:

> Once is enough. Peter does not require or want duplicate, second, or triple
> approval for a bounded remediation prompt.

When Peter instructs Codex to **write a remediation prompt for Gemini to fix
the reviewed issues**, that single instruction has all of these effects unless
Peter expressly says otherwise:

1. it accepts preparation of the bounded remediation prompt;
2. it authorizes the prompt's exact remediation scope;
3. it releases that prompt to Gemini immediately after Codex writes and checks
   it; and
4. it authorizes Gemini to execute that bounded prompt and stop at its stated
   checkpoint.

Codex must document that release as part of the same action. Codex must not mark
such a prompt “prepared but not released,” ask Peter to approve it again, or
require a third confirmation before Gemini acts.

This standing instruction applies to subsequent P3.4 remediation requests with
the same clear “write a prompt ... to fix” direction. It does not release a new
numbered implementation step, expand a remediation beyond reviewed findings,
accept completed work, close P3.G4, or authorize staging, deployment, secrets,
live services, real data, or production use. Those distinct decisions remain
separate when the governing records require them.

## Step 5 clarification

Peter's earlier instructions to update documentation and write remediation
prompts for Gemini to fix Step 5 were intended as single-step authorization and
release of those bounded remediations. Accordingly:

- Step 5 remediation 01 was authorized and released by Peter's instruction to
  write it;
- Step 5 remediation 02 was authorized and released by Peter's instruction to
  write it; and
- Step 5 remediation 03 is authorized and released by Peter's instruction to
  write it and this explicit clarification.

The earlier “not released” labels reflected Codex's mistaken interpretation of
Peter's approval process, not a failure by Peter to authorize the work and not
unauthorized Gemini execution. Historical review findings remain intact; only
their release-status interpretation is corrected.

Step 6 and every later step remain unreleased.
