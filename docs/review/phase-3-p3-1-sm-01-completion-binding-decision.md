# Decision request — SM-01's session/transaction binding contradicts the no-transaction-across-provider-I/O invariant

**Prepared:** 2026-08-14 · **For:** Peter Duscha (Acceptance Authority,
Security Reviewer) · **Prepared by:** Claude (Working Technical Lead) ·
**Status:** **Option 1 approved by Peter Duscha on 2026-08-14, with the schema
refinement in §7. Implementation and re-review remain required.**

**Raised by:** Codex blocking finding 1 against P3.1, recorded in
`docs/review/Handover information`.

**Blocks:** the remediation of that finding, and therefore P3.G1.

---

## 1. The contradiction, stated precisely

Two accepted statements cannot both hold in this flow.

**Statement A — `docs/contracts/phase-3-state-machines.md`, SM-01 "Forbidden":**

> | A session created without a consumed transaction | Session creation takes the
> transaction row's id and runs **in the same transaction as the consumption** |

**Statement B — the accepted architectural invariant.** `.agents/AGENTS.md`
("Adapters") forbids blocking database work on the event loop; the P3.0 operational
and configuration contracts bound the portal to a five-connection pool with a
five-second pool timeout (N-53); and the P3.1 implementation records the rule in
`adapters/web/app.py` as *no database transaction is held open across a network
call to Discord*. Codex's finding restates it as an accepted invariant and
directs that finding 1 must not be fixed by breaking it.

**Why they collide is not a matter of implementation style.** It follows from a
third accepted statement:

**Statement C — `docs/contracts/phase-3-logical-schema.md` §9.2.1:** the PKCE
verifier's *recovery and erasure are one statement*. The callback obtains the
verifier only by consuming the transaction, and PKCE requires that verifier to be
**presented to Discord** at the token exchange.

The consequence is forced:

1. the verifier is needed **before** the provider call, and can be obtained only
   by consuming (C);
2. the identity that a session attests is known only **after** the provider call;
3. therefore consumption necessarily precedes session creation with a provider
   network round trip **between** them;
4. so "the same transaction as the consumption" (A) is a transaction that spans
   the provider round trip — which is exactly what B forbids.

There is no ordering of the existing mechanism that satisfies A and B together.
The current implementation resolves the collision silently in favour of B, and
that silent choice is what Codex found.

## 2. The security outcome, separated from the prescribed mechanism

The **outcome** SM-01 protects is:

> No web session exists unless it is the unique product of exactly one live,
> browser-bound OAuth transaction that was correctly consumed.

The **mechanism** SM-01 prescribes — one database transaction spanning
consumption and session creation — is one way to obtain that outcome, and it is
the way that is unavailable here.

The distinction matters because the outcome is achievable by a durable
mechanism, and because the current implementation achieves **neither**. Today
`OAuthLoginService.complete()` receives no transaction id at all. It cannot
establish from durable state that the completion it is performing corresponds to
any transaction. The route's ordering makes the forbidden state unlikely; nothing
makes it impossible. An internal call, a future route refactor, or a second
completion path would create a session with no proof of an OAuth transaction
behind it, and no test would fail.

## 3. Options

### Option 1 — Durable one-way completion binding (**recommended**)

Give the transaction row a second, one-way step after `consumed`, and make the
session structurally dependent on it.

- `oauth_transactions` gains `completion_claimed_at TIMESTAMPTZ NULL`.
- `sessions` gains `oauth_transaction_id UUID NULL REFERENCES oauth_transactions(id)`,
  `UNIQUE`, with
  `CHECK ((auth_method = 'discord_oauth') = (oauth_transaction_id IS NOT NULL))`.
- `complete()` takes `transaction_id` and, in **one** transaction containing no
  provider I/O:
  1. claims the completion atomically —
     `UPDATE oauth_transactions SET completion_claimed_at = now() WHERE id = $1
     AND consumed_at IS NOT NULL AND completion_claimed_at IS NULL RETURNING id`;
     zero rows is a refusal, not a warning;
  2. resolves the account, records membership, stores tokens, creates the session
     carrying `oauth_transaction_id`, and writes the success audit event;
  3. commits all of it or none of it.

The forbidden state becomes a **database** property in two independent ways: the
`CHECK` refuses an OAuth session with no transaction, and the `UNIQUE` refuses a
second session for the same transaction. Neither depends on the route.

| Scenario | Behaviour |
|---|---|
| Provider retry / duplicated callback | The second callback fails at `consume()` (zero rows, unchanged). Even reaching `complete()`, the claim matches zero rows |
| Process death after consumption, before completion | Transaction is consumed, verifier already erased, no claim, **no session**. The row expires under N-04 and is reaped 24 h after expiry. The user signs in again |
| Callback replay | Unchanged at `consume()`; the claim is a second, independent serialization point |
| Concurrent callbacks | One consumes under `FOR UPDATE`; the other is refused. The claim would refuse a second winner even if consumption were bypassed |
| Audit failure during completion | The success audit shares the completion transaction. It rolls back, the claim rolls back with it, no session exists, and the transaction remains consumed-but-unclaimed — the same terminal state as process death |
| Stale or forged completion | An internal caller invoking `complete()` with an unknown, unconsumed or already-claimed id gets zero rows and a typed refusal. This is enforcement, not an API comment |

Cost: one **new** migration (`0009`; revisions 0006–0008 are not edited), one
service signature change, one route change, amendments to SM-01, schema §9.1/§9.2
and the traceability contract, and new tests including a real-PostgreSQL
rendezvous concurrency test and a mutation that removes the binding.

No provider token, authorization code, `state` or PKCE verifier is stored to
bridge the seam. The claim carries timestamps and row ids only.

### Option 2 — Implement SM-01 literally

Hold the consuming transaction open across `exchange()` and `verify()`.

Satisfies A exactly and violates B. On a five-connection pool with a
five-second pool timeout, a slow or unavailable Discord would hold connections
for the provider timeout and convert a provider degradation into a portal-wide
outage — the failure mode N-53 and the operational contract exist to prevent. It
also requires blocking database work on the event loop or an awaited network call
inside a threadpool-held transaction. **Not recommended**, and the handover
explicitly forbids it.

### Option 3 — Consume after provider verification

Recover the verifier without consuming, call the provider, then consume and
create the session in one transaction — literally satisfying A.

This breaks statement C: recovery and erasure would no longer be one statement,
so two concurrent callbacks could both recover the same verifier and both attempt
an exchange. It reopens the replay window TC-AUTH-12 closes, and leaves a live,
replayable transaction behind every provider failure — contradicting SM-01's own
provider-outage row. **Not recommended.**

### Option 4 — Re-read the row in `complete()` without an atomic claim

Pass the transaction id and require `consumed_at IS NOT NULL`.

Cheaper, and insufficient: it proves *a* transaction was consumed, not that
*this* completion is the only one bound to it. Two completions would both pass
the read. Option 1 subsumes it at the cost of one column and one unique index.

## 4. Recommendation

**Option 1.** It is the smallest change that makes the forbidden state
structurally impossible, it preserves every property the current implementation
already has (single-use AAD-bound PKCE recovery, opaque sessions, no transaction
across provider I/O), and it moves the guarantee from route ordering into the
database, which is where SM-01 intended it to live.

This mechanism change required Acceptance Authority approval. That approval is
now recorded in §7; implementation and re-review remain outstanding.

## 5. Artifacts requiring amendment if Option 1 is approved

| Artifact | Amendment |
|---|---|
| `docs/contracts/phase-3-state-machines.md` | SM-01 states/transitions gain `consumed → completed` and `consumed → abandoned`; the "Forbidden" row is rewritten from "same transaction as the consumption" to the durable binding; failure behaviour gains the process-death-after-consumption row |
| `docs/contracts/phase-3-logical-schema.md` | §9.1 `sessions`: new column, FK, `UNIQUE`, `CHECK`. §9.2 `oauth_transactions`: `completion_claimed_at`; no reverse session FK. §11.2 grant bands unchanged (no new table) |
| `docs/contracts/phase-3-test-traceability.md` | TC-AUTH-12 extended or a new TC-AUTH-13 for the binding, the refused unbound completion, the concurrency evidence and the named mutation |
| `docs/contracts/phase-3-threat-model.md` | The forged/duplicated-completion path recorded against its control |
| `migrations/versions/0009_*.py` | New revision. **0006–0008 are not edited** |
| `application/web/oauth.py`, `adapters/web/app.py`, `adapters/web/repositories.py` | The signature, the claim statement, the route wiring |
| `docs/operations/web-portal.md` | Migration stages and the rollback cost of `0009` |
| `docs/project-management/{decision-register,raid-register,change-log,status}.md` | The decision, its RAID effect and a dated controlled entry |

ADR 0010 is **not** affected: it governs provider-neutral identity and emergency
administration, and the binding is an SM-01/schema property that applies to any
provider adapter equally.

## 6. What was done in the meantime

Nothing that pre-empts this decision. Finding 1 is untouched in code. Findings 2
and 4 are authorized without a contract change and were remediated; finding 3 is
a separate decision request. The complete enumeration of OAuth callback exits and
session-creation paths that this note rests on is in
`docs/review/phase-3-p3-1-remediation-submission.md` §3.

## 7. Acceptance Authority ruling — 2026-08-14

Peter Duscha approves **Option 1, durable one-way completion binding**. The
security outcome in §2 is binding: a Discord OAuth session must be the unique
durable product of one consumed OAuth transaction, while no database transaction
may span provider I/O.

One refinement is part of the ruling: do **not** add the proposed reverse
`oauth_transactions.session_id` foreign key. The authoritative relationship is
`sessions.oauth_transaction_id`, which is non-null for `discord_oauth`, unique,
and references `oauth_transactions.id`. `completion_claimed_at` is atomically
claimed in the same provider-I/O-free database transaction that creates that
session and its success audit. A redundant cyclic relationship would add a
second value that could disagree without strengthening the session-side
guarantee.

The implementation must use a new migration (`0009`), must not edit revisions
0006–0008, and must include the real-PostgreSQL concurrency, rollback,
unconsumed/unknown/already-claimed refusal, direct-database constraint and named
mutation evidence described above. This ruling authorizes remediation only; it
does not accept P3.1 or close P3.G1. Codex independent re-review and a distinct
security-focused pass remain required after implementation.

## 8. Acceptance Authority ruling — 2026-08-14, second addition

Added after Codex's independent implementation and security re-reviews of the
implementation recorded in §7. **§1–§7 are unchanged**; this section is an
addition, not a revision.

Peter approves the partial unique index the implementation declared for
confirmation:

```sql
UNIQUE (oauth_transaction_id) WHERE rotated_from_session_id IS NULL
```

This is the authoritative interpretation of OD-44. It preserves one root
completion-created session per OAuth transaction while allowing that login's N-08
rotation chain to carry the same binding forward.

**The approval is conditional.** Rotation integrity must be strengthened so that
neither the database nor the application can create a branching or otherwise
invalid rotation chain. The predicate is only safe if the set of rows permitted to
share a transaction id is exactly one linear chain per login, so the ruling
requires that:

- at most one session row names a given `rotated_from_session_id`;
- a rotation's account, authentication method and OAuth transaction binding equal
  its predecessor's;
- only a live, unrotated predecessor may be rotated;
- the successor's insertion and the predecessor's revocation are atomic;
- two concurrent rotations deterministically produce one successor and one typed
  refusal, never a branch and never two live descendants;
- a caller cannot label an arbitrary session a rotation to evade the root-session
  unique index; and
- WebAuthn and recovery-grant rotations remain unbound to OAuth transactions.

### 8.1 The second blocking finding this addition also covers

Codex's re-review found that the completion claim checked only the transaction id,
`consumed_at` and `completion_claimed_at`, while `OAuthLoginService.complete()`
independently trusted `identity.provider_key`. Those are two facts that nothing
required to agree, so an internal caller could spend a consumed Discord
transaction using a verified identity and tokens belonging to **another
provider**. The existing "mismatched transaction" test did not cover it: it
supplied a second *unconsumed transaction*, not a second *provider*.

The remediation binds the completion to the provider recorded on that exact row —
`AND provider_key = :provider_key` inside the claiming `UPDATE` — and derives the
expected key from the verified provider result rather than from route ordering.
`VerifiedCompletion` makes that derivation trustworthy: it is one indivisible
value whose identity and tokens are required to name the same provider when it is
constructed, and each half carries the key stamped by the adapter that made the
network call. No unverifiable claim is invented: the key is an adapter constant,
never a field of a provider response.

### 8.2 What this ruling does and does not do

It authorizes the remediation and requires it to be recorded by dated addition in
this record, the controlled contracts, the decision, change, status and RAID
registers, the threat model and a **new** submission. Historical submissions are
not rewritten.

It does **not** accept the implementation. Codex independent implementation
re-review and a separately reported security-focused re-review remain required,
and Codex must verify that the conditions in §8 were implemented. P3.G1 remains
open and P3.2 has not started.
