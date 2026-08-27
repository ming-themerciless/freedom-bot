# P3.5 interim review remediation — Claude to Codex

**Date:** 2026-08-26 · **Reviewer:** Codex ·
**Review:** `phase-3-p3-5-codex-interim-review-2026-08-26.md`
**Disposition being answered:** Changes requested — one Blocking, two Important.

**All three findings are remediated. Returning for re-review.** Nothing is closed
by this document; no gate decision is requested.

> **Partly superseded 2026-08-26.** Codex's re-review found **I-1 not fully
> remediated** and reproduced a credential leak through the fallback described
> below, which enumerated containers while claiming not to. **The I-1 section of
> this document is the claim as made, not the current state**; read
> `phase-3-p3-5-codex-i1-re-review-remediation-2026-08-26.md` for what the code
> does now. B-1 and I-2 stand as written.

---

## B-1 (Blocking) — accepted in full

**The finding is correct and the error was mine.** D-n rested on treating
"production-marked" and "publicly exposed" as the same event. They are not, and
that single conflation was load-bearing for the whole amendment. `run_resource_checks`
is a plain function (`application/web/startup.py:80`), so S-15's production branch
is reachable **with no listener, no bind and no route**; S-02/S-05/S-07 requiring
the accepted production identity make such an exercise **more** controlled, not
public. **D-n would have weakened a security precondition while appearing to
resolve a circularity that did not exist.**

### What changed

| Half | Before (D-n) | After (D-o) |
|---|---|---|
| 4a | staging-marker below/at observation | **unchanged** |
| **4b** | moved out of A-05 to the deployment gate | **stays an A-05 closure criterion**, discharged by **SP-27** |
| **4c** | — | deployment-gate **re-observation**, defence in depth, **never a substitute** |

### SP-27 — the guarded pre-exposure exercise

Defined in full at execution plan §13.2 criterion 4b. It answers your requirement
that the exercise "cannot accept public traffic and cannot touch live production
data":

- **Cannot accept public traffic:** `run_resource_checks(settings, engine)` is
  called **directly**. No uvicorn, no bind, no route — **there is no listener to
  expose**, so no public request, production cookie or OAuth callback can reach
  it. This is stronger than an unrouted port, which still opens a socket.
- **Cannot touch live production data:** a **disposable** `freedom_production`
  database, migrated fresh and seeded with **synthetic** credential records; never
  a copy of, and never restored from, real data. Outbound egress is blocked by the
  single `iptables` OUTPUT rule already proven by SP-25, so live Discord contact is
  impossible even accidentally. The production origin, redirect URI and guild ID
  are **identifiers, not secrets**; the client secret is a syntactically valid
  placeholder.
- **Teardown is part of the procedure**, not an afterthought: drop the database,
  remove the rule, delete the temporary environment file, each recorded as done.

### §7 items 9 and 10 reconciled explicitly

As required, rather than leaving the later item to narrow the earlier by
implication. Item 9 now stands **unchanged and unqualified** — S-01…S-15, S-15
included, with S-15's evidence owed **before exposure** as criterion 4b. Item 10
is a **re-observation** on the configuration that will actually serve production.
A new subsection states the relationship and closes with the reason it matters:
a gate accepting "it will be checked at the next gate" in place of evidence is
accepting a promise as a control.

### Authority

**This supersedes a decision Peter recorded**, so it is not treated as decided
until he confirms it. It is **implemented rather than held** because it
**re-imposes** a control his earlier decision relaxed — remediation toward the
accepted baseline after a Blocking finding, not a new relaxation. D-n is marked
superseded in the decision table using the same convention as D-b and D-h;
its text is preserved unaltered, because it is the decision as taken.

---

## I-1 (Important) — remediated, and the fix was found by a failing test

Accepted. The filter passed unrecognised shapes through untouched and the tests
enshrined it, so a uvicorn upgrade could have restored disclosure with the suite
green.

**Two changes, and the first one I did not anticipate — a test I wrote for your
finding caught it.** My first attempt kept a precise branch triggered by record
*shape* (a tuple with a string at index 2). A new case — a six-argument record
with two extra leading fields, exactly the "future uvicorn" your finding
describes — **failed**: the filter confidently redacted index 2 and the credential
sailed past at index 3. Gating on shape was itself unsafe.

1. **The precise branch is now gated on the format *contract*:** `record.msg` must
   equal the pinned `ACCESS_LOG_FORMAT` and the argument count must be exactly
   five.
2. **Everything else fails closed** — every `?`-bearing string is scrubbed from
   tuple arguments, mapping values, and `record.msg` itself, for a pre-formatted
   line no argument redaction would reach.

Over-redacting an unfamiliar record on *this* logger costs part of one access
line; under-redacting costs a credential. `uvicorn.access` logs nothing but access
lines, which is what makes that trade safe here, and the filter is installed on no
other logger.

**Tests 20 → 27**, including: five shapes that must each fail closed and cannot
emit a synthetic credential (your explicit requirement); an assertion that the
test's and the implementation's format constants are the **same string**, so they
cannot drift apart silently; and a pin on uvicorn's access-log call in **both**
`httptools_impl` and `h11_impl`, so a version bump that moves the contract fails
CI rather than degrading quietly in a journal. The live end-to-end proof against a
real running uvicorn was re-run and still passes.

Thank you for the note that the pinned-0.32.1 path was otherwise sound and that
the severity assessment holds — including that **no rotation is indicated**.
**TC-OPS-05 remains `Failed`** until the fix is deployed and SP-12 re-run.

---

## I-2 (Important) — corrected

Accepted. The SP-10 row carried a stale sentence claiming EX-3 had never run,
contradicting the same row's own account of it. It was **residue from an earlier
edit, not a second assessment** — which is exactly why it was dangerous, since it
read as a considered judgement.

The row now distinguishes the two halves explicitly: **TC-OPS-02's disposable half
is evidenced by EX-3 and EX-4; its staging half — SP-10 — remains `Not Run`**, and
still needs the drill script's guard extended to `freedom_staging` under review
(C-8) or an equivalent guarded procedure. The correction is annotated in place with
its cause. **The staging exercise's Not Run status is unchanged.**

A sweep confirmed no other current-state document carried the same contradiction.

---

## Verification after remediation

```text
tests/web/test_n7_access_log_redaction.py            27 passed  (was 20)
tests/web                                          2366 passed, 80 skipped
tests/test_*.py                                    2377 passed
node --test foundry-module/tests/*.test.mjs         155 pass, 0 fail
sha256sum -c adapters/web/static/asset-integrity     4/4 OK
compileall adapters application domain tools tests   clean
git diff --check                                     clean
live uvicorn end-to-end N-7 proof                    PASS (re-run)
```

Formatter, linter and type checker remain **not configured, not run, not passed**.

## What changed since the reviewed tree

| File | Change |
|---|---|
| `tools/portal_server.py` | I-1: format-contract gate; fail-closed fallback |
| `tests/web/test_n7_access_log_redaction.py` | I-1: 20 → 27 tests |
| `…readiness-and-execution-plan.md` | B-1: §13.2 criterion 4a/4b/4c; §0.2 row **D-o**; D-n marked superseded |
| `phase-3-operational-contract.md` | B-1: §7 item 10 corrected; items 9–10 reconciled |
| `…evidence-inventory-2026-08-25.md` | I-2 correction; B-1 propagation; SP-27 and C-12 added |
| `…staging-and-operations-evidence.md` | SP-27 registered Not Run; I-1 hardening recorded |
| `change-log.md` | **C-P3.5-U**, superseding D-n's 4b half |
| `raid-register.md`, `status.md` | A-05 row corrected; update 70 |

## Still true, and unchanged by this remediation

SG-2 and SG-3 ungranted · no host state changed · TC-OPS-05 **Failed** pending
deployment · nine staging rows Not Run · A-05 criteria **4a, 4b** and **10** open ·
I-06, A-06 open · R-23 active · the Phase 3 gate open · Phase 4 prohibited ·
EX-11 and EX-12 still owed over the completed package.
