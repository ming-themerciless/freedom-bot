# P3.5 staging re-observation procedure

**Written 2026-08-25** for the Operations Owner, to be executed in **one sitting**
against the identity-verified deployed process (PID 3785672, commit `0bef692`).

Four re-observations remain from the handover's Step 5. Each confirms that a
repository remediation accepted by review behaves as intended on the deployed
build — the same standard SP-25 met for S-4.

| # | What it proves | Finding |
|---|---|---|
| 1 | Challenge and assertion budgets are separate | S-7 |
| 2 | A limiter refusal writes an audit row that resolves by the correlation shown | S-5 |
| 3 | Logout is attributed to the authority the session actually held | S-6 |
| 4 | A replayed and an expired grant are classified differently in the audit | S-9 |

---

## Before you start

**This deliberately spends limiter budget**, which is why it is one sitting rather
than four. The budgets, and what this procedure spends:

| Control | Budget | Window | Spent here |
|---|---|---|---|
| Challenge issuance per IP (N-32a) | 10 | 10 min | 4 in Phase 1 |
| Assertion verification per IP (N-32) | 5 | 10 min | 1 in Phase 1, then 5–6 in Phase 4 |
| Assertion verification per account (N-32) | 10 | 60 min | ~7 total |
| Recovery redemption per IP (N-33) | 3 | 10 min | 3 across Phases 2–3 |

Two consequences to plan around:

- **Phase 4 deliberately locks the assertion path for ten minutes.** Do it last.
- **Wait ten minutes between Phase 1 and Phase 4**, or Phase 1's assertion will
  count against Phase 4's five and the refusal will arrive a step early. That is
  not a failure, but it makes the count harder to read.

**Record only** route or action, UTC time, HTTP status, and the coarse refusal
code or audit reason. Never record a cookie, token, token hash, assertion,
challenge, CSRF value, public key or raw address.

---

## Phase 1 — the budgets are separate (S-7)

The finding: before 2026-08-24, issuance and verification shared one five-unit
bucket, so a completed ceremony cost two and a cancelled prompt cost one. Three
fumbles during an outage could exhaust the path that exists for outages.

1. Go to `https://freedom-blades-test.rpgworld.org/v1/auth/emergency`.
2. Start the passkey ceremony and **cancel it at the authenticator**. Do this
   **three times**. Each spends one *challenge*, and — if the fix works — no
   verification budget at all.
3. Now sign in properly with a live passkey.

**Pass:** the sign-in succeeds. Under the old shared bucket, three cancellations
plus a ceremony would have spent five of five and this would have been refused
`rate_limited`.

**Record:** that three cancellations occurred, and that the fourth attempt
authenticated. Note the UTC time — Phase 4 needs to be at least ten minutes later.

4. Confirm the session is live by reaching `/v1/admin/role-capabilities`.
5. **Sign out** using the control in the header.

## Phase 2 — logout attribution and grant replay (S-6, S-9)

6. Issue a recovery grant host-locally:

```bash
sudo bash /opt/discord-bots/freedom-bot/infra/staging/portal-run.sh \
  -m tools.emergency_recovery issue --operator "Peter Duscha" \
  --reason "P3.5 staging re-observation, 2026-08-25"
```

7. Redeem it at the emergency page. You should land on
   `/v1/admin/role-capabilities`.
8. **Sign out.**
9. **Submit the same token again.** It must be refused with the neutral message
   and a correlation reference. Note that reference — it is not a secret; it is
   what the audit row will carry.

## Phase 3 — expiry classification (S-9)

10. Issue a **second** grant. Note the UTC time. Issuing invalidates the first.
11. **Wait more than ten minutes.** Use the wait to run the audit checks in
    Phase 5, which need no budget at all.
12. Submit the expired token. It must be refused, with a reference — and the
    refusal must look **identical** to Phase 2's replay refusal from the browser.
    That indistinguishability is the security property; the difference belongs in
    the audit and nowhere else.

## Phase 4 — a limiter refusal is audited and resolves (S-5)

**At least ten minutes after Phase 1.** This is the one that locks you out
temporarily; the recovery path stays available.

13. Attempt a passkey sign-in and let it **fail verification** five times — use a
    retired credential if you still have one on the device, or any attempt that
    reaches verification and is refused.
14. The **sixth** attempt must answer `rate_limited` with a `Retry-After` header
    and a correlation reference. **Note that reference.**

**Pass:** the refusal is `429 rate_limited`, and — the actual finding — a row
exists for it. Before the fix, this refusal wrote nothing at all, so the reference
shown to the operator resolved to no row.

## Phase 5 — resolve every reference in the audit (S-5, S-6, S-9)

These are reads. They cost no budget and can be done during Phase 3's wait, from a
break-glass session — audit search is one of the two surfaces N-65 permits.

15. Sign in (or use the session you have) and open the audit search.
16. Look up **each correlation reference** you noted. For every one, a row must
    exist. A reference that resolves to nothing is a failure of S-5's remediation.

What each should show:

| Event | Expected |
|---|---|
| Phase 1 sign-out | `auth.logout`, capability **`platform_administrator`**, `auth_method: webauthn` |
| Phase 2 sign-out | `auth.logout`, capability **`platform_administrator`**, `auth_method: recovery_grant` |
| Phase 2 replay | `auth.emergency.refused`, reason **`consumed`**, with a grant record id |
| Phase 3 expiry | `auth.emergency.refused`, reason **`expired`**, with a grant record id |
| Phase 4 limiter | `auth.emergency.refused`, reason **`assertion_rate_limited_ip`** |

**The two logout rows are S-6.** Before the fix, *every* logout was audited as
`guild_member` — including a break-glass administrator holding no proven guild
membership at all. If either row says `guild_member`, the remediation is not
working on the deployed build.

**The replay and expiry rows are S-9.** They must differ from each other, and
**neither may contain a token or token hash** — only the non-secret grant record
id. If they read identically, the classification is not reaching the audit.

## Afterwards

- Confirm no grant is left live: issuing a third invalidates any earlier one, or
  use `tools.emergency_recovery revoke`.
- The assertion budget clears ten minutes after Phase 4's last attempt.
- Send the recorded lines back. Nothing here closes A-05, I-06 or any gate; these
  are observations for the record and for the Security Reviewer.

## If something does not match

Stop and report it rather than re-running. A limiter refusal that resolves to no
row, a logout audited as `guild_member`, or a replay and an expiry that read
identically each mean a remediation accepted in the repository is not behaving as
accepted on the deployed build — which is exactly the class of gap S-1 existed to
catch, and worth more than finishing the checklist.
