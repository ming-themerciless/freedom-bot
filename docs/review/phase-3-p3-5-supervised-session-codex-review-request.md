# P3.5 supervised session — independent review request

**Date:** 2026-08-24
**Requester:** Claude, P3.5 working Technical Lead
**Reviewer:** Codex — one independent pass and one distinct security-focused pass
**Subject:** `docs/review/phase-3-p3-5-supervised-session-evidence-2026-08-24.md`
**Commit:** `0c95e72bc9a3c274b5683161b17ceb0fe53f8902`, working tree clean
**Status requested:** review of the evidence, the SP-21 and SP-22 procedures, and
disposition of eight findings.
**No gate decision is requested and no RAID item is proposed for closure.**

---

## 1. What was executed

The bounded procedure in
`phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md` §4, in full,
plus **SP-21** and the observable part of **SP-22**, added after §4 closed because
§4 did not reach them,
on the deployed staging host `freedom-blades-test.rpgworld.org`, with the
Operations Owner driving Chrome on macOS 26 and his own platform authenticators.
Every §4.2 and §4.3 row is Passed; none Failed; none skipped.

**No repository change was made during the session**, deliberately — a code change
inside an evidence run invalidates the evidence it produced. The six findings below
are recorded unfixed.

## 2. What the session establishes, and what it does not

**Establishes:** a human completed break-glass login in a real browser, twice, on
two distinct enabled credentials, under a Discord outage verified in both
directions; the break-glass session resolved to a continuity shell offering exactly
`Role capabilities` and `My account`, proven by contrast against the same operator's
ordinary session offering all six; sign-out invalidated the session server-side; a
retired credential was refused at verification; cancellation is neutral and
non-disclosing; all seven required views render at 320/768/1280 and 200%; the
no-JavaScript page shows no dead security-key control. **SP-21:** a host-issued
recovery grant was issued, used exactly once, and then refused on replay and refused
again after expiry — the second attempt deliberately delayed 15 minutes so that both
the 10-minute grant ceiling and the N-33 per-address window had passed, making it an
expiry refusal rather than a limiter refusal. **SP-22:** R-20, R-22 and R-40 each
answered the denial page against a live break-glass session.

**Does not establish:** anything about I-06 — no TC-OPS, TC-PERF, TC-LIM-02 or
TC-SEC-07 browser half was performed. Anything about browsers other than Chrome on
macOS 26. A-05 criteria 3, 4, 9 or 10 — criterion 8 is now evidenced by SP-21, but
the `revoke`/`invalidate_all` path was not exercised. The import-apply half of
criterion 6 — see §4.

## 3. Findings for disposition

| # | Finding | Location | Bearing |
|---|---|---|---|
| S-1 | Deployed process served code 8½ hours older than the commit under test; the page under test returned 500 while the suite was green and `/healthz` reported `ok`. Resolved by restart; the deploy/reload gap remains | operational | — |
| S-2 | `freedom-worker.service` inactive while `/healthz` reports `worker_heartbeat: true` | operational | I-06, TC-OPS |
| S-4 | `/healthz` reports `identity_provider: true` unconditionally — a literal, not a probe | `adapters/web/app.py:1212` | I-06 criterion 9, TC-OPS-05 |
| S-5 | Rate-limited break-glass refusals write **no** audit record, while showing a correlation reference that resolves to nothing | `adapters/web/app.py:1092-1113` | **A-05 criterion 7**, SM-03, N-32 |
| S-6 | Every logout audited as `guild_member`, including a break-glass administrator with no guild membership | `application/web/sessions.py:658-661` | **A-05 criterion 7**, SM-03 |
| S-7 | R-07 options and R-08 verify share one limiter bucket: a completed ceremony costs two of five per-address units, a cancelled one costs one | `adapters/web/app.py:1063`, `:1092` | **A-05 criteria 5 and 7**, availability |
| S-8 | Product Owner finds the post-sign-out page unpolished. Cosmetic; that page passes every functional and accessibility check applied | — | Visual baseline is frozen; a scope decision, not a defect |
| S-9 | A replayed recovery grant and an expired one produce **byte-identical** audit payloads (`grant_not_live`), with no grant reference in either | `application/web/breakglass.py:422-423`, `adapters/web/repositories.py` grant `consume` | **A-05 criterion 8**, SM-03, N-14 |

Full reasoning, mechanism and reproduction for each is in §6 of the evidence
document.

## 4. The gap this session did not close, and should have

A-05 criterion 6 requires break-glass to grant **Platform Administrator only** —
"never Council, character ownership or import-apply authority, **by implication or
by route**". The session evidenced the **presentation** half thoroughly: the
continuity shell withholds `Characters`, `Council characters` and `Snapshots`, and
the same operator's ordinary session offers all three minutes later.

**This gap was closed after the §4 procedure completed**, by holding a live
break-glass session and requesting each withheld destination directly by URL:

| Route | Path | Result |
|---|---|---|
| R-20 | `/v1/characters` | **Refused** — `denied.html`, "Not available" |
| R-22 | `/v1/council/characters` | **Refused** — same |
| R-40 | `/v1/council/snapshots` | **Refused** — same |

**One half of criterion 6 remains suite-only.** R-46
(`POST /v1/council/jobs/{job_id}/apply`) and R-41
(`POST /v1/admin/snapshots/{snapshot_id}/folder`) are POST routes needing an
identifier; they cannot be driven from a browser address bar, and driving them
otherwise would mean handling the operator's session cookie, which A-8 forbids
recording. R-40's refusal does establish that the emergency administrator cannot
reach the import surface through the application at all.

**A near-miss worth the reviewer's attention.** The first run of this check
returned the Discord **sign-in page** for all three URLs — the signature of *no
session*, not of a refused break-glass session, because
`adapters/web/portal_routes.py:415-423` answers a sessionless GET navigation with
`303` to `/v1/login`. Recorded uncritically, it would have entered this package as a
pass for a test performed signed-out. It was caught by comparing the observation
against the two code paths rather than against expectation. The evidence document
records the near-miss alongside the result.

## 5. Independent verification available to the reviewer

Three findings — S-5, S-6, S-9 — concern what the audit trail does and does not
record, and all three were found by reading rows the ceremony actually wrote rather
than by reading code first. The reviewer may wish to treat audit completeness as a
theme rather than three separate items.

Repository-scoped, re-runnable without the staging host:

```
node --test tests/web/webauthn_client.test.mjs                       # 50 passed
pytest -q tests/web/test_p3_5_webauthn_and_shell_presentation.py     # 9 passed
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  pytest -q tests/web/test_break_glass_login.py                      # 17 passed
sha256sum -c adapters/web/static/asset-integrity.sha256              # 4/4 OK
git diff --check                                                     # clean
```

The staging observations cannot be re-run without the host and the Operations
Owner's authenticators. Where a claim rests only on operator report rather than on
machine output, the evidence document says so explicitly.

## 6. Questions for the reviewer

1. Does S-5 block A-05? The working view is that it should: criterion 7 requires
   limiter, audit and correlation to be verified, and an audit trail that goes
   silent precisely under sustained attack does not satisfy it.
2. Is S-6 a defect or an accepted simplification? Nothing in the code defends the
   hardcoded capability, and migration `0006` widened the attribution constraint
   specifically for the actor it mislabels.
3. Should S-7's shared bucket be split, or the budget resized? Does five per ten
   minutes remain right when each attempt costs two, and should challenge issuance
   and assertion verification share a budget at all?
4. Is S-4 a monitoring defect to fix, or should `identity_provider` be removed from
   the VM-16 vocabulary rather than reported as a constant?
4a. Does S-9 warrant recording the specific cause after a failed grant redemption?
   The single-statement `consume` is correct and should stand; the question is
   whether a second, read-only lookup should follow a zero-row result so the audit
   can say *why*, and whether the grant record id belongs in the refusal payload as
   `credential_record_id` already does for credentials.
5. Is the import-apply half of criterion 6 (§4) acceptable at suite level, or must
   R-41/R-46 be observed against a live break-glass session before A-05 closes?
6. Does any finding here reopen a closed gate?
7. Is the evidence document's separation of observed fact from operator report, and
   of Passed from Not Run, honest enough to rest a gate decision on later?

## 7. What is explicitly not claimed

A-05, I-06, A-06, R-23, TC-BG-02, TC-UI-01/02 and the Phase 3 gate all remain open.
Public exposure and Phase 4 remain unauthorized. The session occurring is not
evidence for any of them; only recorded successful evidence and the required
authority's dated acceptance moves their state.
