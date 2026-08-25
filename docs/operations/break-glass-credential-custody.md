# Break-glass credential custody, replacement, loss and recovery

**A-05 criterion 9.** Written 2026-08-25 for the Operations Owner's acceptance.

This document contains **no credential material** and never will: no credential
id, no public key, no COSE bytes, no PIN, no biometric, no recovery token and no
token hash. It names people, counts, timings and procedures only.

It covers the protected Server Administrator account — the account that exists so
the platform can be administered when Discord cannot be reached. Ordinary Discord
sign-in is not in scope.

---

## 1. What is being kept safe, and why it is unusual

The protected account is not a normal login. It is the only way into the platform
when the identity provider is unavailable, and it is deliberately built so that
**no part of the running system can grant it back to you**. There is no password
reset, no "email me a link", no support desk. Authority to restore it comes from
host access, not from the application.

That is the right design, and it has one consequence the whole of this document
follows from: **losing these credentials is not an inconvenience, it is an
outage of the administrative surface**, recoverable only by someone with shell
access to the host and, in the worst case, database-owner rights.

Two rules follow, and they are enforced by the software rather than left to
memory:

- **At least two enabled credentials at all times** (N-13). The tool refuses to
  retire the second-to-last one, and refuses before it writes anything.
- **Two independent authenticators**, not two records for one device. Two passkeys
  on the same phone are one hardware failure, not two.

## 2. Custody

| Question | Answer |
|---|---|
| Who holds them | The Operations Owner (Peter Duscha) |
| How many | Two enabled, minimum, at all times |
| Independence | Two separate physical authenticators, kept in different places |
| What is written down | Nicknames, record UUIDs, enrollment dates. **Never** credential material |
| Where the account lives | The portal's database on the target host |
| Who else can enroll | Anyone with host shell access and sudo — that is the trust boundary |

**Host access is the real perimeter.** Every command in this document requires it,
and none of them is reachable over HTTP by design (route contract §1, §8). Anyone
who can run commands on the host as an operator can enroll a new credential for
the protected account. Protect host access with the same seriousness as the
passkeys themselves; they are not two separate controls.

### 2.1 The check nothing will do for you

**The system does not tell you when you are down to one credential.** This was
observed on 2026-08-25 and recorded as finding F6: outside production the shortfall
is detected at startup, a warning describing it exactly is produced — and then
nothing publishes it. It is not logged, not printed, and not visible in `/healthz`,
which reports `status: ok` with every check green and is **byte-identical** to a
healthy two-credential account.

So the count is a **manual** check. Run it on a schedule you actually keep —
monthly, and after any device change:

```bash
sudo bash /opt/discord-bots/freedom-bot/infra/staging/portal-run.sh \
  -m tools.webauthn_enrollment list --operator "<your name>"
```

It prints the account id, the enabled count against the minimum, and one line per
credential. Two is the floor, not the target.

## 3. Replacement and rotation

**Always enroll the new one before retiring the old one.** The tool enforces this
— retiring below two is refused — but the ordering matters for a reason beyond the
refusal: between the retire and the enroll you would be at one, and at one you are
one failure away from §5.

1. Enroll the replacement (§3.1 of `web-portal.md` has the exact command).
2. Verify the count is now three with `list`.
3. **Sign in with the new credential once**, to prove it works before you rely on
   it. An enrolled credential that has never authenticated is an assumption.
4. Retire the old one, with a reason that will mean something to a reader in a
   year:

```bash
sudo bash /opt/discord-bots/freedom-bot/infra/staging/portal-run.sh \
  -m tools.webauthn_enrollment retire --operator "<your name>" \
  --credential <record UUID from list> --reason "<why>"
```

Retirement is not deletion. The record stays, disabled, and presenting it at login
is refused — observed on 2026-08-24. That is deliberate: an audit trail of which
credential was used when survives the credential.

### 3.1 A usability problem you will meet, and how to work around it

**The nicknames the portal holds are not what your passkey UI shows you.** The
portal knows a credential as `puppetmaster`; your device offers you a list of
passkeys labelled however the platform labels them. There is no reliable way to
match one to the other by looking, and this is a real problem rather than a
cosmetic one: on 2026-08-24 the operator selected a **retired** credential in a
genuine emergency rehearsal, because his authenticator listed the dead ones
alongside the live ones and nothing distinguished them.

It cost him a failed attempt, and failed attempts are not free (§4).

Mitigations, none of them perfect:

- **Delete retired passkeys from the device** when you retire them in the portal.
  The portal keeps the record; your device does not need to. This is the single
  most effective step and it is the one most often skipped.
- **Keep a private note** — outside the portal, outside this repository — mapping
  each device to its portal nickname. A nickname and a device name is not
  credential material.
- **Name new credentials after the device**, not the person or the role, so
  `iphone-15-personal` beats `puppetphone`.

## 4. What a mistake costs: the budgets

Wrong selections consume limiter budget, so an emergency handled clumsily can lock
you out of the emergency path. The numbers, as accepted:

| Control | Budget | Window |
|---|---|---|
| Challenge issuance, per source IP (N-32a) | 10 | 10 minutes |
| Assertion verification, per source IP (N-32) | 5 | 10 minutes |
| Assertion verification, per account (N-32) | 10 | 60 minutes |
| Recovery redemption, per source IP (N-33) | 3 | 10 minutes |
| Attempts per recovery grant (N-33) | 5 | — |

**A cancelled authenticator prompt no longer costs you a verification attempt.**
Issuance and verification held one shared budget until 2026-08-24 (finding S-7); a
completed sign-in spent two of five and a cancelled prompt spent one, so three
fumbles during an outage could exhaust the path that exists for outages. They are
separate now: cancelling costs an issuance, not a guess.

Practical consequence: **you get five real attempts per ten minutes from one
location.** If you burn them, wait the window out rather than continuing — further
attempts are refused and the refusals are audited. If you are on a phone hotspot
and a laptop, those are different source addresses.

## 5. Loss

### 5.1 One credential lost, one still working

Not an emergency. You are at one, and **nothing will remind you** (§2.1).

1. Enroll a replacement **today**, not this month.
2. Retire the lost one, with the reason.
3. Verify the count is two.

### 5.2 A credential possibly compromised

Treat "left unlocked in a hotel room" as compromised.

1. Enroll a replacement from a device you trust.
2. Retire the suspect credential immediately.
3. Read the audit trail for its record id — every emergency login and refusal is
   recorded with a correlation reference — and look for logins you cannot account
   for.
4. If you find one, treat it as an incident: the session may have created
   role-capability mappings, which survive the session.

### 5.3 Every credential lost

This is what recovery grants exist for, and they require host access:

```bash
sudo bash /opt/discord-bots/freedom-bot/infra/staging/portal-run.sh \
  -m tools.emergency_recovery issue --operator "<your name>" --reason "<why>"
```

The token prints **once**. It is stored only as a hash, appears in no row, no log
and no audit payload, and cannot be recovered if you lose the output — issue
another, which invalidates the first.

It is single use, purpose-bound, and **valid for ten minutes**. Exercised on
2026-08-24: it was redeemed once, a replay was refused, and an expired one was
refused — both refusals identical to the caller by design.

**The residual, stated plainly:** for those ten minutes the token is a bearer
credential. Anyone who sees your terminal or clipboard in that window can use it.
Do not paste it anywhere, do not read it aloud, and use it immediately.

**The moment you are back in, enroll two credentials and verify the count.** A
recovery grant is a way back in, not a way to stay in.

### 5.4 Host access lost as well

There is no application-level answer, and that is by design rather than an
oversight. Restoring the account then requires database-owner action on the host —
someone with PostgreSQL superuser or the database owner role, acting outside the
application. Make sure that is not the same single person as the Operations Owner,
and that whoever it is can be reached.

## 6. Emergency sessions expire quickly — plan for it

An emergency session is **15 minutes idle, 60 minutes absolute** — deliberately
tighter than an ordinary session. A break-glass session left alone for a quarter
of an hour is gone, and no session survives an hour from login regardless of
activity.

Plan emergency work in that unit. Know what you intend to do before you sign in.

## 7. Acceptance

| Field | Value |
|---|---|
| Author | Claude (working Technical Lead), 2026-08-25 |
| Accepted by | **Pending** — Operations Owner |
| Date accepted | **Pending** |
| Review | Contains no credential material; A-05 criterion 9 |

This document closes A-05 criterion 9 **only when the Operations Owner records
acceptance above**. It closes no other criterion and no gate.
