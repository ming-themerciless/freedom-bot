# Claude handover — Phase 2 final-review findings

Prepared: 2026-08-09
From: Codex, Independent Reviewer
To: Claude, implementer
Repository: `/opt/discord-bots/freedom-bot`, branch `docs/platform-plan`

## Outcome of the independent review

Codex recommends that the Acceptance Authority **not close the Phase 2 gate
yet**. One Blocking recovery finding and one Important contract finding remain.

Do not record a gate decision. Remediate the findings, update the controlled
records accurately, run the relevant verification, and return the package for
independent re-review.

## B-1 — lost-pin reconciliation can still produce a false miss

Severity: **Blocking**

Affected material:

- `docs/operations/foundry-snapshot-submission.md`, especially §9 lines
  describing lost-pin reconciliation;
- `docs/review/phase-2-i-03-cl3-remediation.md`;
- any tests or code needed to establish the corrected recovery contract.

### Defect

The procedure says that the operator waits until the final "request/timeout has
finished", runs the acceptance-event query, repeats it once after a miss, and
may then authorize a fresh export.

A client timeout proves only that the client stopped waiting. It does not prove
that the server stopped processing the POST. This reachable sequence remains:

1. The POST reaches the server and continues processing.
2. The client times out and the Foundry page is reloaded, losing the in-memory
   pin and its checksum/idempotency key.
3. Both reconciliation queries run before the server transaction commits.
4. Both return no row, so the procedure authorizes a fresh export.
5. The original request subsequently commits.

Expanding the query window to cover the complete unresolved episode fixed the
previous window-boundary false miss, but it does not close this in-flight-request
race. Rehearsal A observed the hit branch after a response was lost; that does
not exercise a query performed before a late server commit.

### Required closure

Design a recovery rule that cannot authorize a fresh export while a timed-out
request can still commit. The evidence must establish a positive server-side
termination/settlement condition or an equally safe conservative incident rule;
two immediate query misses alone are insufficient.

The remediation must:

- state exactly what establishes that every relevant POST has finished on the
  server, not merely timed out at the client;
- preserve the whole-episode audit-event window correction;
- keep a hit, miss and ambiguous result fail-safe;
- cover the late-commit sequence with a focused automated test where practical,
  or a deterministic supervised/operational proof if the boundary cannot be
  exercised automatically;
- correct every record that currently says CL3-B-1 is closed;
- avoid claiming that Rehearsal A exercised the late-commit case.

Do not solve this by retaining Actor data or credentials in browser-readable
Foundry settings. The existing confidentiality constraint remains binding.

## I-1 — C-10's ECMAScript key boundary is wrong

Severity: **Important**

Affected material:

- `docs/rules/foundry-export-contract.md` §1/§1.0;
- `application/foundry/parser.py` canonical key ordering;
- `foundry-module/scripts/canonical.js` if the chosen corrected contract
  requires a module change;
- cross-language and boundary tests;
- change-log C-10 and any review/status record that describes it as complete.

### Defect

C-10 calls canonical decimal keys in `[0, 2**53 - 1]` ECMAScript integer
indices and makes Python sort all of them numerically. Ordinary JavaScript
object enumeration gives numeric precedence to **array-index** keys only,
ending at `2**32 - 2`. Larger canonical numeric strings are ordinary string
keys for ordinary objects.

This is an observed cross-language disagreement, not just terminology. From the
repository root:

```bash
node --input-type=module -e "import {canonicalBytes} from './foundry-module/scripts/canonical.js'; process.stdout.write(new TextDecoder().decode(canonicalBytes({'5000000000':'five','10000000000':'ten'})))"

./venv/bin/python -c "from application.foundry.parser import canonical_bytes; print(canonical_bytes({'5000000000':'five','10000000000':'ten'}).decode(), end='')"
```

Observed:

```text
JavaScript: {"10000000000":"ten","5000000000":"five"}
Python:     {"5000000000":"five","10000000000":"ten"}
```

The current fixture misses the disagreement because its integer-looking keys
are small class-level keys.

### Required closure

Choose and document one achievable canonical rule, then make the supported
JavaScript exporter and Python verifier agree for the complete boundary. At a
minimum, cross-language tests must cover:

- `"0"`;
- `"4294967294"` (largest ECMAScript array index);
- `"4294967295"` (not an array index);
- two or more larger numeric-looking strings whose numeric and code-point order
  differ, such as `"5000000000"` and `"10000000000"`;
- noncanonical forms such as `"01"`, `"-1"` and `"1.0"`;
- recursive nested objects.

Do not silently edit the already installed/rehearsed module build while keeping
version `1.0.5`. If module bytes change, follow the existing version/build
identity control and describe honestly what the prior rehearsals exercised. If
only the Python verifier and contract change because the shipped module already
has the intended behavior, show why that is sufficient.

The Rehearsal B artifact's recorded `canonical_encoding = yes` is not disproved:
the real artifact evidently contained no key exposing this boundary. The claim
that C-10 was correct and complete is what must be corrected.

## Conclusions that do not need remediation

Codex accepted the following parts of the package:

- RA-1's `SNAPSHOT_ONLY` classification of `system.favorites*` and Actor-level
  `system.source.*`;
- field profile `2026-08-09.1` and the maintainer review, when considered with
  fail-closed behavior, automated coverage and the two real-folder observations;
- C-11's Phase 2 throughput criterion of at most 1,200 ms/MB measured from the
  slowest sample; it is conservative and is not a production capacity promise;
- the signed active-folder attestation. The plan explicitly permits Actors to
  be create-candidates, so a populated-database reconciliation would add
  evidence but is not a stated gate requirement;
- the declared Phase 3 disposition of RA-3.

RA-4 remains a documentation improvement: the operations instructions should
say that a step 10 injector must fault the POST rather than the CORS preflight.
It did not independently block this Phase 2 recommendation because the recorded
rehearsal ultimately exercised the intended POST path.

## Verification baseline

Codex ran, read-only:

```text
./venv/bin/python -m pytest -q                1784 passed, 208 skipped
node --test foundry-module/tests/*.test.mjs   143 passed
git diff --check                             clean
```

The 208 skipped tests remain the declared PostgreSQL-backed set skipped without
`TEST_DATABASE_URL`.

## Constraints

- Do not access Foundry, real exports, real Actor data, credentials, databases
  or external endpoints merely to implement these corrections.
- Do not modify or regenerate the signed attestation's real identifiers.
- Do not record the Phase 2 gate decision.
- Keep implementation and evidence claims aligned: identify which cases are
  automated, which were rehearsed, and which remain inferred.
- Return the complete diff and test results for independent re-review.
