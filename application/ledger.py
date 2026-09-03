"""Posting a ledger transaction: the Phase 4 command-execution path.

This module is both halves of one boundary, kept together because
`.agents/AGENTS.md` requires an interface to be owned by the code that consumes
it: the repository and unit-of-work protocols a ledger needs, and the service
that consumes them. Nothing here is speculative — every method on every protocol
below is called by `LedgerCommandService`.

## What the service guarantees

- **Authority is resolved here, at execution, for every caller.** A human is
  resolved through `AuthorizationPort`; a non-human caller is resolved through
  `LedgerPrincipalPort`. Neither is taken from the request. See *Who may post*
  below.
- **A retry is not a second effect.** The command's idempotency key is spent in
  the same transaction as the posting, and a repeat of the same key with the
  same canonical content returns the *stored* receipt without posting again.
- **Reuse of a key for different content fails closed.** It is refused with
  `idempotency_key_conflict`; the original receipt is never handed back to
  describe an operation it is not.
- **A stale expected version applies nothing.** The book's version is read
  inside the transaction and compared with the version the caller read before
  deciding. A mismatch raises `ConcurrencyConflictError` and the unit of work is
  left without committing.
- **A held balance never goes negative.** The resulting balance of every `HELD`
  account the transaction touches is computed inside the transaction and refused
  with `insufficient_resources` if it would be, which is the rule
  `Resource.deduct` enforces in the live bot today.
- **Nothing is half-applied.** The posting, the idempotency receipt and the audit
  event are written through one unit of work and commit together or not at all.
- **Authority is resolved before anything is read, and once per operation.** A
  correction resolves the caller *before* it looks the target transaction up, so
  no caller can learn whether a transaction exists by comparing refusals, and the
  one attribution it resolved is what the digest, the receipt, the audit row and
  the posting all use. See *One resolution per operation* below.
- **One attempt has one correlation identity.** The envelope and the transaction
  it carries must name the same one, or the command is refused before a unit of
  work opens. See *One correlation identity per attempt* below.

## Where the transaction boundary is, and what OD-48 leaves open

The service owns the transaction: it opens one unit of work per attempt, and the
repositories join it and never commit (ADR 0003). `LedgerUnitOfWork` is that unit
of work plus a ledger — deliberately a *narrower* protocol than
`application.repositories.UnitOfWork`, because a service should depend on the
repositories it uses and not on the ten it does not.

**OD-48 rules that Phase 4 adds no physical ledger table**, so the only ledger
implementation in this repository is the in-memory reference adapter in
`adapters/ledger/`. What that means for the guarantees above, stated plainly
rather than left for a reviewer to discover: the *idempotency receipt* is durable
in PostgreSQL and is what proves the retry, conflicting-reuse and concurrent-
caller behaviour against a real database; the *posting itself* is durable only as
far as its repository is. When package 5.0 or 5.2 gives the ledger a table, the
same service commits both halves in one database transaction and the gap closes.
Nothing here is written in a way that assumes an in-memory ledger. That adapter
does not claim cross-store atomicity; what it does claim, and enforces, is
written in `adapters/ledger/in_memory.py`.

## Who may post — the two authorities, both resolved at execution

**A human caller** is resolved through `AuthorizationPort` and must currently
hold Guild Council authority (`application/authorization.py`, rule 2).

**A non-human caller** is resolved through `LedgerPrincipalPort`, and this is
the change made for review finding **P4-R2**. Before it, any `CommandCaller`
carrying a non-blank `principal_id` was treated as an authorized service
principal: the envelope *named* an identity and the service read that name as a
grant. `CommandCaller.principal_id` is caller-supplied text — an adapter builds
the envelope out of its own request — so a direct caller could manufacture
authority by choosing a string.

The rule now is the one the module docstring of
`application/authorization.py` states for people, applied to machines:

1. the principal is resolved **by the port, at execution**, from the id in the
   request — the request supplies a *lookup*, never an answer;
2. a principal the port does not currently return is refused, whether it is
   unknown, revoked, or deactivated;
3. the principal must currently hold `LedgerScope.POST_TRANSACTION`; and
4. the audit row is attributed to the **resolved** principal, never to the
   request text.

Nothing here infers authority from `AuditSource`, from an id's spelling, from a
claim that an outer adapter checked, or from a boolean in the envelope. There is
no such boolean, and `application/commands.py` explains why.

**Why this port rather than `ServicePrincipalScope`.** That enum is the accepted
authority vocabulary of the Foundry snapshot credential set
(`adapters/http/credentials.py`), whose configured secrets are parsed from
`FREEDOM_SNAPSHOT_PRINCIPALS`. Adding a ledger scope to it would widen what an
operator can grant to a snapshot-submission credential, which is a change to an
accepted authorization decision and is not Phase 4's to make. Phase 4 has no
production caller for this service — no route, no command, no deployment unit —
so the handover's stated alternative applies: a narrow, consumer-owned protocol
with a faithful in-memory fake. **No implementation of `LedgerPrincipalPort`
exists outside the tests, and the fake proves authorization, not
authentication**: proving that a presented credential belongs to a principal is
an adapter's job, and the package that gives this service a caller owns it.

## One resolution per operation — the compensation lookup

Review finding **P4-R4**. `compensate()` used to read `ledger.get()` first and
refuse an unknown id with its own message, while an id that *did* exist went on
to `post()`, which authorized and could refuse with `not_authorized`. Two
different answers to two different questions, both reachable by a caller holding
no authority at all: an ordinary member, a member whose Council role was
withdrawn, an unknown principal, a revoked or deactivated one, or one holding
some other scope could all use the pair of refusals as an existence oracle. No
posting, receipt or audit row was written on either path — the defect was the
*distinction*, not an effect.

The rule now:

1. `compensate()` resolves the caller's current authority **before** the lookup,
   through the same ports `post()` uses and with the same undifferentiated
   `not_authorized` refusal, so an unauthorized caller is answered identically
   whether the transaction exists or not;
2. that resolution happens **once**. The resolved `_Attribution` is carried into
   the private `_post_resolved` path rather than the operation re-entering
   `post()` and asking a port a second time. A second resolution could answer
   differently — a credential revoked between the two readings — and would leave
   the lookup authorized under one identity and the posting recorded under
   another; and
3. the carried attribution is the identity used by the canonical digest, the
   audit row and the posting alike.

`_post_resolved` is private and there is deliberately **no public overload that
accepts an attribution**. An `_Attribution` exists only as a port's answer, and
an entry point that accepted one would let an adapter present a conclusion where
the design requires it to present an identity — the shape of defect P4-R2. No
authorization is cached between requests: every `post()` and every
`compensate()` resolves afresh.

## One correlation identity per attempt

Review finding **P4-R5**. `CommandEnvelope.correlation_id` and
`LedgerTransaction.correlation_id` could differ. The receipt and the audit row
recorded the envelope's; append-only ledger history kept the transaction's. One
attempt therefore had two correlation identities, an operator tracing an audit
row into ledger history found nothing, and neither the digest nor a retry could
detect it, because correlation is attempt metadata and excluded from the digest.

`post()` now refuses a mismatch with `correlation_mismatch` **before** the
expected-version precondition is read, before the digest is computed and before
the unit-of-work factory is called, so a mismatched command writes no posting, no
receipt and no audit row. An accepted command records one id in all three places,
and the fix is a fence rather than an added digest field: making correlation
command-defining would refuse a genuine retry that regenerated one, which is the
opposite of what a retry needs.

## Command identity — what a key is spent on

Review finding **P4-R3**: the canonical digest omitted command-defining facts,
so a reused key could be answered as a retry when the second request would have
recorded materially different history. The rule now, stated field by field.

**Command-defining.** Change any of these and the same key is a *conflict*:

| Field | Why it defines the command |
|---|---|
| digest schema | a stored key means what the schema that produced it says |
| command name and idempotency scope | the operation being performed |
| caller source | recorded in audit; a different surface is a different record |
| authenticated caller identity | the resolved Discord user or service principal |
| book id | which aggregate is changed |
| resource | which of the three quantities moves |
| expected version | the precondition the caller decided against |
| authoritative occurrence time | recorded in append-only history |
| reason | recorded verbatim in append-only history |
| compensation target | which transaction this reverses, or none |
| entry count, and each entry in order | the effect itself: account book, name, kind, unit and signed amount |

**Attempt metadata.** These may differ between attempts under one key, and each
is excluded only because it cannot alter the *accepted* effect:

- **`CommandEnvelope.correlation_id` and `LedgerTransaction.correlation_id` are
  attempt metadata**, stated explicitly because the handover requires the answer
  to be unambiguous. They must be *equal within one attempt* — the fence above —
  and that is a consistency rule, not an identity: what remains excluded from the
  digest is the shared value, because it varies legitimately between attempts of
  one command. A correlation id ties one *attempt*'s receipt, audit row, ledger
  entry and log line together. Only the first attempt's transaction is ever accepted,
  so only its correlation id is ever recorded; a retry is answered from the
  stored receipt and therefore returns the **original** attempt's correlation id
  rather than its own. Retry behaviour, the stored receipt and the audit row all
  agree on that, which is the consistency the rule has to have. Were a
  correlation id command-defining, a genuine retry that generated a fresh one
  would be refused as a conflict — the opposite of what a retry needs.
- **`LedgerTransaction.id`** — a rebuilt true retry generates a fresh one, and
  the accepted id is always returned from stored state (`facts.transaction_id`
  is read back from the receipt, never recomputed).
- **The idempotency key itself**, which is the identity the digest is stored
  under rather than a field within it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Protocol
from uuid import UUID

from application.audit import ActorCapability, AuditEvent
from application.authorization import AuthorizationPort, NotAuthorizedError
from application.commands import (
    CommandCaller,
    CommandEnvelope,
    CommandReceipt,
    StoredReceiptUnreadable,
)
from application.errors import ConcurrencyConflictError, UniquenessConflict
from application.idempotency import (
    CanonicalValue,
    IdempotencyRecord,
    IdempotencyStatus,
    canonical_request_hash,
)
from application.repositories import AuditRepository, IdempotencyRepository
from application.service_principals import validate_principal_id
from domain.ledger import AccountRef, LedgerTransaction, Quantity, ResourceKind, utc

#: The Phase-4-owned idempotency namespace. Keys are unique *within* a scope, so
#: a key spent on a ledger posting cannot collide with one spent on a snapshot
#: submission, and a scope nobody else writes is what lets Phase 4 use the
#: existing `idempotency_keys` table without a migration (OD-48).
LEDGER_SCOPE = "ledger.post_transaction"

#: The command name written into every receipt this service produces.
POST_TRANSACTION = "ledger.post_transaction"

LEDGER_ENTITY = "ledger_transaction"

#: The one audit action this service writes. A refusal writes **nothing**: every
#: refusal path below leaves its unit of work without committing, and that is
#: what makes "nothing was posted" literally true rather than nearly true. The
#: snapshot submission service records refusals because it is an unauthenticated
#: network boundary; this one is reached only through an adapter that has already
#: established its caller.
TRANSACTION_POSTED = "ledger.transaction_posted"

ACTION = "Posting a ledger transaction"

#: The version of the canonical request identity below. It is the first thing
#: hashed, so a stored `idempotency_keys.request_hash` can only ever be compared
#: against the field list that produced it. Changing which fields are
#: command-defining, what they are named, or how they are rendered means a new
#: schema name — never a quiet reinterpretation of keys already stored.
DIGEST_SCHEMA = "ledger.post_transaction.identity/1"

#: Every refusal this service can raise, and nothing else.
#:
#: Closed on purpose: the code is what an adapter branches on and what an
#: operator filters history by, so a value nobody declared would be free text
#: wearing a code's clothes. The same rule the snapshot submission service
#: applies to its own refusals.
REFUSAL_CODES = frozenset(
    {
        #: The caller does not currently hold the required capability. Resolved
        #: now, through the port — never taken from the request.
        "not_authorized",
        #: This key is spent, and it was spent on different content. Refused
        #: rather than answered with the original receipt, which would describe
        #: an operation this request is not.
        "idempotency_key_conflict",
        #: The posting would drive a `HELD` account below zero.
        "insufficient_resources",
        #: A race was lost and its winner could not be identified. Never
        #: resolved into a duplicate: an unresolvable conflict is not a receipt.
        "concurrent_posting",
        #: The stored receipt for an already-spent key could not be read back.
        "original_result_unavailable",
        #: The envelope and the transaction it carries name different
        #: correlation identities, so one attempt could not be recorded under
        #: one identity in ledger history, receipt and audit. Refused before a
        #: unit of work is opened.
        "correlation_mismatch",
    }
)


class LedgerRefused(Exception):
    """A ledger command was refused for a stated, safe reason.

    Carries a code from `REFUSAL_CODES` and a message written here — never
    derived from a driver, an ORM or the failing statement. An adapter turns it
    into a user-facing message; nothing else does.
    """

    def __init__(self, code: str, message: str) -> None:
        if code not in REFUSAL_CODES:
            raise ValueError(
                f"{code!r} is not a declared ledger refusal. Add it to "
                "REFUSAL_CODES with a comment saying what it means, so an "
                "operator filtering history can rely on the set being closed."
            )
        super().__init__(message)
        self.code = code


class LedgerScope(Enum):
    """Every capability a non-human caller may hold over this ledger.

    An enum rather than free-text strings for the reason
    `application/service_principals.py` gives about its own scopes: a typo in a
    string scope is silently a *different* scope, and it fails in the dangerous
    direction — a check against a misspelling passes for whoever was granted the
    same misspelling and fails closed for everyone else, which looks like working
    authorization right up until it does not.

    One entry, because Phase 4 has one ledger command. A second is a decision
    about which credential would hold it and what a leak of that credential would
    then permit, not a convenience.
    """

    #: Post a balanced transaction to a ledger book. Explicitly not: correct
    #: somebody else's posting without holding this scope, read Council data,
    #: read audit history, or reach any other use case.
    POST_TRANSACTION = "ledger:transaction:post"


@dataclass(frozen=True, slots=True)
class LedgerPrincipal:
    """A non-human caller's authority over this ledger, as resolved *now*.

    Constructed by an implementation of `LedgerPrincipalPort`, never by an
    adapter out of request text and never by this service. Holding one of these
    is the evidence that the port answered; there is no other way to obtain the
    authority it represents.
    """

    principal_id: str
    scopes: frozenset[LedgerScope]

    def __post_init__(self) -> None:
        # The same identifier rule the accepted service-principal model applies,
        # called rather than copied: this id is written into append-only audit
        # history and into operator logs, so it is a chosen token and not free
        # text. See `application/service_principals.validate_principal_id`.
        validate_principal_id(self.principal_id)
        if not isinstance(self.scopes, frozenset):
            object.__setattr__(self, "scopes", frozenset(self.scopes))
        for scope in self.scopes:
            if not isinstance(scope, LedgerScope):
                raise ValueError(
                    "A ledger principal holds LedgerScope values, not "
                    f"{type(scope).__name__}. A scope that is merely a string "
                    "cannot be checked for existing."
                )
        if not self.scopes:
            raise ValueError(
                f"Ledger principal {self.principal_id!r} holds no scope, so it "
                "can do nothing. Grant it a scope or do not resolve it; a "
                "principal that resolves and then fails every check is a "
                "confusing way to say 'revoked'."
            )

    def holds(self, scope: LedgerScope) -> bool:
        return scope in self.scopes


class LedgerPrincipalPort(Protocol):
    """Resolves a non-human caller's *current* ledger authority.

    Asked again on every execution, for the reason `AuthorizationPort` is: a
    resolution is a reading, and a reading has a time. A credential revoked
    between two commands must refuse the second one.
    """

    def current_principal(self, principal_id: str) -> LedgerPrincipal | None:
        """The principal as it stands now, or `None`.

        **Unknown, revoked and deactivated are one answer on purpose.** That is
        how the accepted credential mechanism already models revocation — an
        entry removed from the configured set
        (`adapters/http/credentials.ServicePrincipalRegistry`) — and it is what
        keeps the refusal this service returns undifferentiated. Whoever
        presented an id that does not resolve has nothing to do with a more
        specific diagnosis, and an attacker would.

        Implementations must not create, register or widen a principal as a side
        effect of being asked. This is a query.
        """
        ...


class LedgerRepository(Protocol):
    """The append-only book, as its consumer needs it.

    **There is deliberately no `update` and no `delete`.** A correction is a
    compensating transaction (`LedgerTransaction.compensate`), and an interface
    that offered to rewrite an accepted entry would make the append-only
    invariant a convention rather than a property.
    """

    def version_of(self, book_id: UUID) -> int:
        """How many transactions this book has accepted.

        The optimistic-concurrency version of the aggregate. Zero for a book
        that has never been posted to, which is a value and not an absence: a
        caller's first posting legitimately expects version 0.
        """
        ...

    def balance_of(self, account: AccountRef, kind: ResourceKind) -> Quantity:
        """The account's current balance in one resource.

        Read inside the posting transaction, because a balance read outside it
        is a number that was true once. Returns the resource's zero for an
        account with no entries.
        """
        ...

    def append(self, transaction: LedgerTransaction, *, expected_version: int) -> None:
        """Accept one transaction into this unit of work, under a precondition.

        `expected_version` is carried into the *commit*, not merely compared
        here, and that distinction is the whole of the optimistic-concurrency
        guarantee: a version read at the start of a transaction is a reading, and
        two callers who both read version 3 would both pass a comparison made at
        that moment. The precondition has to be re-checked where the write
        becomes visible — the same shape as `CharacterRepository.save`, whose
        conditional `UPDATE … WHERE version = :expected` is one atomic statement
        rather than a read followed by a write.

        Raises `UniquenessConflict("ledger_transaction.id")` if that identity is
        already taken, which is how a repository refuses to accept the same
        posting twice however it arrived, and `ConcurrencyConflictError` at
        commit if the book moved on in between.
        """
        ...

    def get(self, transaction_id: UUID) -> LedgerTransaction | None:
        """The accepted transaction with this id, for a correction to reverse."""
        ...


class LedgerUnitOfWork(Protocol):
    """One command, one transaction, over exactly the repositories used here."""

    ledger: LedgerRepository
    idempotency: IdempotencyRepository
    audit: AuditRepository

    def __enter__(self) -> LedgerUnitOfWork: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


@dataclass(frozen=True, slots=True)
class _Attribution:
    """How one command is recorded: under whose authority, and as whom.

    Built only from what a port answered. Nothing in it is copied out of the
    request, which is what lets the audit row and the canonical command identity
    below both be described as naming the *verified* caller.
    """

    capability: ActorCapability
    discord_user_id: int | None
    #: The resolved principal, for a non-human caller. `None` for a person.
    service_principal_id: str | None = None

    @property
    def identity(self) -> str:
        """The verified caller, as one canonical token.

        Prefixed by kind, so a Discord snowflake and a principal id cannot be
        the same token by coincidence — which matters because this string is a
        command-defining field of the idempotency digest.
        """
        if self.discord_user_id is not None:
            return f"discord-user:{self.discord_user_id}"
        return f"service-principal:{self.service_principal_id}"


class LedgerCommandService:
    """Posts balanced transactions, once each, under a checked precondition.

    One instance per configured application; one unit of work per attempt. The
    unit-of-work factory is injected rather than a session being held, so the
    service never outlives a transaction and never shares one between commands.
    """

    def __init__(
        self,
        unit_of_work_factory,
        *,
        authorization: AuthorizationPort,
        principals: LedgerPrincipalPort,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._authorization = authorization
        # Required rather than defaulted. A default would have to be either
        # "authorize every principal", which is the defect P4-R2 records, or
        # "refuse every principal", which would let a deployment that forgot to
        # wire a port look like one that deliberately has no service callers.
        # Composing this service is the moment to say which it is.
        self._principals = principals

    # -- commands ---------------------------------------------------------- #

    def post(
        self, envelope: CommandEnvelope, transaction: LedgerTransaction
    ) -> CommandReceipt:
        """Post one balanced transaction, or refuse. Never post it twice.

        `transaction` is already valid by construction — an unbalanced one, a
        mixed-resource one or one with a zero entry cannot be built at all
        (`domain/ledger.py`). What is decided here is everything that needs the
        *current* state: authority now, the key's history, the book's version and
        the resulting held balances.

        The envelope and the transaction must name one correlation identity; a
        mismatch is refused before a unit of work opens (`correlation_mismatch`,
        review finding **P4-R5**).
        """
        if not isinstance(transaction, LedgerTransaction):
            raise TypeError(
                "post() takes a LedgerTransaction. Build it in the domain, where "
                "the balance invariant is enforced, rather than passing entries "
                "for this service to assemble."
            )

        # Authority first, and before any of the caller's other input is
        # examined: an unauthorized caller learns nothing about the shape this
        # command should have had.
        attribution = self._attribute(envelope.caller)
        return self._post_resolved(envelope, transaction, attribution=attribution)

    def _post_resolved(
        self,
        envelope: CommandEnvelope,
        transaction: LedgerTransaction,
        *,
        attribution: _Attribution,
    ) -> CommandReceipt:
        """Everything `post()` does after authority has been resolved.

        Private, and deliberately so. It takes an `_Attribution` — the object
        that exists only as the answer of a port — rather than a caller, which
        is what lets `compensate()` resolve authority *before* it looks anything
        up and still perform exactly one resolution for the whole operation
        (review finding **P4-R4**). Exposing this publicly would hand an adapter
        a way to present an attribution instead of an identity, which is the
        shape of defect P4-R2 recorded, so nothing outside this class can reach
        it.
        """
        correlation_id = self._require_one_correlation(envelope, transaction)
        book_id = transaction.book_id
        expected = envelope.require_expected_version("ledger_book", book_id)
        digest = self._digest(
            envelope,
            transaction,
            expected_version=expected.version,
            attribution=attribution,
        )

        try:
            return self._execute(
                envelope,
                transaction,
                expected_version=expected.version,
                attribution=attribution,
                correlation_id=correlation_id,
                digest=digest,
            )
        except UniquenessConflict as conflict:
            # The adapter has already rolled this transaction back, so there is
            # nothing partial to undo. What is left is to find out who won and
            # say so truthfully, in a fresh transaction, rather than assume it
            # from the rule name.
            if conflict.rule == "idempotency_key.scope_key":
                return self._replay(envelope, digest)
            raise LedgerRefused(
                "concurrent_posting",
                "Another command claimed an identity this one needed and could "
                "not be identified. This attempt posted nothing. Retry with the "
                "same idempotency key: a retry cannot post a second transaction.",
            ) from None

    def compensate(
        self,
        envelope: CommandEnvelope,
        *,
        transaction_id: UUID,
        reason: str,
        occurred_at: datetime,
    ) -> CommandReceipt:
        """Correct an accepted transaction by reversing it, never by editing it.

        The original is read back and negated here rather than being rebuilt by
        the caller, so a correction cannot quietly reverse something other than
        what was accepted.

        **Authority is resolved before the lookup, and exactly once**, which is
        review finding **P4-R4**. Before it, the ledger was read first and an
        unknown `transaction_id` returned its own refusal while an existing one
        went on to be authorized by `post()`. The two answers differed, so any
        caller — an ordinary member, a revoked one, an unknown principal, a
        revoked or deactivated one, one holding another scope — could ask this
        method whether a transaction exists and read the answer off which
        refusal came back. Nothing was posted either way; the leak was the
        *distinction*.

        Resolving first is only half of it. Resolving first and then calling
        `post()` would resolve a *second* time, and a resolution is a reading
        with a time: a credential revoked in between would leave the lookup
        authorized under one answer and the posting under another, and the
        digest, the audit row and the posting could then disagree about who
        acted. So one attribution is resolved here and carried through
        `_post_resolved` into the digest, the receipt, the audit row and the
        posting.

        The read happens in its own transaction, which is safe because the
        posting that follows carries the book's version precondition: a book that
        changed between the read and the commit refuses the correction rather
        than reversing a transaction against a state nobody saw.
        """
        attribution = self._attribute(envelope.caller)
        with self._unit_of_work_factory() as unit_of_work:
            original = unit_of_work.ledger.get(transaction_id)
        if original is None:
            raise LedgerRefused(
                "concurrent_posting",
                "The transaction to be corrected is not in the ledger, so there "
                "is nothing to reverse and nothing was posted.",
            )
        return self._post_resolved(
            envelope,
            original.compensate(
                reason=reason,
                occurred_at=occurred_at,
                correlation_id=envelope.correlation_id,
            ),
            attribution=attribution,
        )

    # -- execution --------------------------------------------------------- #

    def _execute(
        self,
        envelope: CommandEnvelope,
        transaction: LedgerTransaction,
        *,
        expected_version: int,
        attribution: _Attribution,
        correlation_id: UUID,
        digest: bytes,
    ) -> CommandReceipt:
        book_id = transaction.book_id
        with self._unit_of_work_factory() as unit_of_work:
            spent = unit_of_work.idempotency.find(
                LEDGER_SCOPE, envelope.idempotency_key
            )
            if spent is not None:
                # Nothing has been written in this unit of work, so leaving the
                # block without committing discards a transaction that only
                # read.
                return _replay_record(spent, digest)

            version = unit_of_work.ledger.version_of(book_id)
            if version != expected_version:
                # Raised *before* anything is written, and the `with` block is
                # left without committing, so a stale caller applies nothing at
                # all — not the posting, not the receipt, not an audit row
                # claiming a change that did not happen.
                #
                # This is the *early* refusal, not the guarantee. Two callers who
                # both read version 3 would both pass here; what separates them
                # is the same precondition re-checked at commit, carried by
                # `append` below.
                raise ConcurrencyConflictError(
                    f"Ledger book {book_id} is at version {version}; this command "
                    f"was decided against version {expected_version}. Nothing was "
                    "posted. Re-read the book and decide again."
                )

            self._require_sufficient_balances(unit_of_work, transaction)

            receipt = CommandReceipt(
                command=POST_TRANSACTION,
                # The one correlation identity of this attempt, fenced above and
                # therefore the same value the transaction carries into ledger
                # history and the audit row records below. Passed in rather than
                # read off the envelope again, so the three cannot drift apart
                # by a later edit to one of them (review finding **P4-R5**).
                correlation_id=correlation_id,
                version=version + 1,
                facts={
                    "transaction_id": str(transaction.id),
                    "book_id": str(book_id),
                    "resource": transaction.kind.value,
                    "entry_count": len(transaction.entries),
                    "compensates": (
                        None
                        if transaction.compensates is None
                        else str(transaction.compensates)
                    ),
                },
            )

            # **The receipt is written before the effect, and the order decides
            # what a concurrent caller is told.** `(scope, key)` is unique in the
            # database, so a second caller carrying the same key blocks on this
            # statement until this transaction ends and then loses it — arriving
            # back in `post()` as a typed `UniquenessConflict` to be resolved by
            # re-reading the winner's receipt.
            #
            # Written *before* `append` deliberately. A duplicate submission of
            # one command is a retry, and a retry must be answered with the
            # original receipt; if the effect's own precondition were reached
            # first, the loser of an identical double-submit would be told its
            # version was stale — which is true of the book and false of the
            # question the caller asked.
            unit_of_work.idempotency.add(
                IdempotencyRecord(
                    scope=LEDGER_SCOPE,
                    key=envelope.idempotency_key,
                    request_hash=digest,
                    status=IdempotencyStatus.COMPLETED,
                    response=receipt.as_payload(),
                )
            )
            unit_of_work.ledger.append(transaction, expected_version=version)
            unit_of_work.audit.record(
                AuditEvent(
                    action=TRANSACTION_POSTED,
                    entity_type=LEDGER_ENTITY,
                    entity_id=str(transaction.id),
                    source=envelope.caller.source,
                    actor_capability=attribution.capability,
                    actor_discord_user_id=attribution.discord_user_id,
                    correlation_id=correlation_id,
                    # The reason and the accounts, never the amounts of another
                    # player's holdings and never the caller's own text beyond
                    # the bounded reason the domain already validated.
                    payload={
                        "book_id": str(book_id),
                        "resource": transaction.kind.value,
                        "reason": transaction.reason,
                        "entry_count": len(transaction.entries),
                        "version": version + 1,
                        # The principal the *port* resolved, never the request's
                        # own text, and `None` for a person — whose attribution
                        # is the audit row's own Discord column. Always present
                        # so an operator filtering history reads one row shape.
                        "service_principal_id": attribution.service_principal_id,
                    },
                )
            )
            unit_of_work.commit()
            return receipt

    def _require_sufficient_balances(
        self, unit_of_work: LedgerUnitOfWork, transaction: LedgerTransaction
    ) -> None:
        """Refuse a posting that would drive a held balance below zero.

        Checked inside the transaction, against the balance as it is *there*.
        A check made before the transaction opened would be a reading from
        before whatever else committed in between, which is exactly the race the
        version precondition exists to catch and this one would not.

        It is the version fence that makes this reading safe against a
        *concurrent* posting rather than a stale one: any transaction that
        changes a balance also advances the book's version, so a caller whose
        balance reading has been overtaken is refused at commit before its own
        posting becomes visible.
        """
        kind = transaction.kind
        for account in transaction.accounts():
            if not account.is_held:
                continue
            effect = transaction.effect_on(account)
            if not effect.is_negative:
                continue
            resulting = unit_of_work.ledger.balance_of(account, kind) + effect
            if resulting.is_negative:
                raise LedgerRefused(
                    "insufficient_resources",
                    f"{account.name} does not hold enough {kind.value} for this "
                    "transaction, so nothing was posted.",
                )

    # -- replay ------------------------------------------------------------ #

    def _replay(self, envelope: CommandEnvelope, digest: bytes) -> CommandReceipt:
        """Answer from the winner's stored receipt, in a fresh transaction."""
        with self._unit_of_work_factory() as unit_of_work:
            spent = unit_of_work.idempotency.find(
                LEDGER_SCOPE, envelope.idempotency_key
            )
        if spent is None:
            raise LedgerRefused(
                "concurrent_posting",
                "Another command claimed this idempotency key and its receipt "
                "could not be read back. This attempt posted nothing. Retry with "
                "the same key: a retry cannot post a second transaction.",
            )
        return _replay_record(spent, digest)

    # -- helpers ----------------------------------------------------------- #

    def _require_one_correlation(
        self, envelope: CommandEnvelope, transaction: LedgerTransaction
    ) -> UUID:
        """One attempt, one correlation identity — or refuse before anything.

        Review finding **P4-R5**. An envelope and the transaction it carries
        each name a correlation id, and nothing previously required them to be
        the same one. When they differed the receipt and the audit row recorded
        the envelope's while append-only ledger history kept the transaction's,
        so the three records of one attempt named two identities and nothing
        detected it — the digest excludes both as attempt metadata, so a retry
        could not notice the contradiction either.

        Refused here, before `require_expected_version`, before the digest and
        before the unit-of-work factory is called, so a mismatch writes no
        posting, no receipt and no audit row. It is a refusal rather than a
        silent preference for one of the two: choosing the envelope's would
        quietly discard the id the domain object was built with, and choosing
        the transaction's would make the caller's own correlation a suggestion.

        **This does not make correlation command-defining.** It stays out of the
        digest, and it stays attempt metadata: a genuine retry may carry a fresh
        correlation id in *both* places and is still the same command, answered
        from the stored receipt — which returns the accepted attempt's id. What
        is fenced is a single attempt's internal disagreement, not variation
        between attempts.
        """
        if envelope.correlation_id != transaction.correlation_id:
            raise LedgerRefused(
                "correlation_mismatch",
                "This command and the transaction it carries name different "
                "correlation identities, so one attempt could not be recorded "
                "under one identity in ledger history, the receipt and the "
                "audit record. Nothing was posted. Build the transaction with "
                "the correlation id of the command that carries it.",
            )
        return envelope.correlation_id

    def _attribute(self, caller: CommandCaller) -> _Attribution:
        """Resolve current authority, or refuse. Never trust the request.

        A port is asked *now*, at the moment the work is about to be done, and
        its answer is used both to permit the command and to record the authority
        it was taken under (`application/authorization.py`, rule 2). Which port
        depends only on which identity the caller carries, and
        `CommandCaller` guarantees it carries exactly one.
        """
        if caller.is_human:
            return self._attribute_person(caller.discord_user_id)
        return self._attribute_principal(caller.principal_id)

    def _attribute_person(self, discord_user_id: int) -> _Attribution:
        context = self._authorization.context_for(discord_user_id)
        try:
            context.require_council(ACTION)
        except NotAuthorizedError as error:
            # Re-raised as this service's own refusal so an adapter has one
            # exception type and one code vocabulary for everything it must turn
            # into a user-facing message. The reason is kept.
            raise LedgerRefused("not_authorized", str(error)) from None
        return _Attribution(context.capability, discord_user_id)

    def _attribute_principal(self, principal_id: str) -> _Attribution:
        """Resolve a non-human caller through the port, or refuse it.

        `principal_id` is a *lookup*, not a grant. It arrives as caller-supplied
        text and the only thing done with it is to ask the port; everything
        afterwards — the scope check, the audit attribution and the canonical
        command identity — uses the principal the port returned.

        **One refusal for four causes**, matching how the accepted credential
        mechanism already answers: an unknown id, a revoked one, a deactivated
        one and one lacking the scope are indistinguishable to the caller. A
        machine holding one configured credential has nothing to do with a more
        specific diagnosis, and an attacker would.
        """
        principal = self._principals.current_principal(principal_id)
        if principal is None or not principal.holds(LedgerScope.POST_TRANSACTION):
            raise LedgerRefused(
                "not_authorized",
                f"{ACTION} requires a currently authorized service principal "
                "holding the ledger posting scope. Nothing was posted.",
            )
        return _Attribution(
            ActorCapability.SERVICE_PRINCIPAL,
            None,
            service_principal_id=principal.principal_id,
        )

    def _digest(
        self,
        envelope: CommandEnvelope,
        transaction: LedgerTransaction,
        *,
        expected_version: int,
        attribution: _Attribution,
    ) -> bytes:
        """The canonical content this key is spent on.

        Every command-defining field and no attempt metadata; the module
        docstring's table is the contract and this is its one implementation.
        Three of these fields were added for review finding **P4-R3** — the
        authoritative occurrence time, the verified caller identity and the
        caller's surface — because without them a key reused for materially
        different history, or by a different principal, hashed identically to the
        original and was answered as a retry.

        `attribution` rather than `envelope.caller`: the identity bound in is the
        one a port resolved. Hashing the request's own `principal_id` would bind
        in a string the caller chose, which is the input P4-R2 records as
        untrustworthy.

        `expected_version` is passed in rather than re-read from the envelope
        because `post()` has already required it to name *this* book; reading it
        again here would allow a `None` that cannot occur and would need a
        rendering for it.
        """
        fields: list[tuple[str, CanonicalValue]] = [
            ("command", POST_TRANSACTION),
            ("scope", LEDGER_SCOPE),
            ("caller.source", envelope.caller.source.value),
            ("caller.identity", attribution.identity),
            ("book", str(transaction.book_id)),
            ("resource", transaction.kind.value),
            ("expected_version", expected_version),
            ("occurred_at.epoch_us", _epoch_microseconds(transaction.occurred_at)),
            ("reason", transaction.reason),
            (
                "compensates",
                None if transaction.compensates is None else str(transaction.compensates),
            ),
            ("entry_count", len(transaction.entries)),
        ]
        # In order, and indexed by position: the entries of a transaction are an
        # ordered tuple that append-only history keeps as given, so two orderings
        # of the same movements are two different recorded histories.
        for index, entry in enumerate(transaction.entries):
            fields.extend(
                (
                    (f"entry.{index}.book", str(entry.account.book_id)),
                    (f"entry.{index}.account", entry.account.name),
                    (f"entry.{index}.account_kind", entry.account.kind.value),
                    (f"entry.{index}.unit", type(entry.amount).__name__),
                    (f"entry.{index}.amount", _amount_units(entry.amount)),
                )
            )
        return canonical_request_hash(DIGEST_SCHEMA, fields)


#: The instant integer microseconds are counted from. Named rather than inlined,
#: because it is part of what `DIGEST_SCHEMA` version 1 means.
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _epoch_microseconds(moment: datetime) -> int:
    """An authoritative occurrence time as an exact whole number of microseconds.

    An integer rather than a rendered timestamp, so one instant has exactly one
    canonical form: `12:00+00:00` and `13:00+01:00` are the same moment and must
    hash the same, while two different instants must not. Integer arithmetic on
    `timedelta` rather than `timestamp()`, because that returns a binary float
    and a digest is the last place a float should decide an identity.

    `utc()` refuses a naive datetime; the domain refuses one at construction too,
    so this is a second fence rather than the only one.
    """
    return (utc(moment) - _EPOCH) // timedelta(microseconds=1)


def _amount_units(amount: Quantity) -> int:
    """An amount as its whole count of smallest units.

    Read off the value object's single field rather than `str(amount)`, so a
    change to a diagnostic rendering cannot silently change what a stored
    idempotency digest covers. Returned as an integer and hashed as one, so five
    copper and the text "5" are different fields.
    """
    (field_name,) = type(amount).__dataclass_fields__
    return getattr(amount, field_name)


def _replay_record(record: IdempotencyRecord, digest: bytes) -> CommandReceipt:
    """The stored receipt for a spent key, or a refusal. Never a re-execution."""
    if not record.matches(digest):
        raise LedgerRefused(
            "idempotency_key_conflict",
            "This idempotency key has already been spent on a different "
            "command. Nothing was posted. Use a new key: answering with the "
            "original receipt would describe an operation this request is not.",
        )
    if record.status is not IdempotencyStatus.COMPLETED or record.response is None:
        raise LedgerRefused(
            "original_result_unavailable",
            "This idempotency key is spent but its result could not be read "
            "back, so this attempt posted nothing and confirmed nothing.",
        )
    try:
        return CommandReceipt.from_payload(record.response, duplicate=True)
    except StoredReceiptUnreadable:
        raise LedgerRefused(
            "original_result_unavailable",
            "This idempotency key is spent and the stored receipt could not be "
            "read back. Nothing was posted, and no receipt is invented for it.",
        ) from None


__all__ = [
    "ACTION",
    "DIGEST_SCHEMA",
    "LEDGER_ENTITY",
    "LEDGER_SCOPE",
    "POST_TRANSACTION",
    "REFUSAL_CODES",
    "TRANSACTION_POSTED",
    "LedgerCommandService",
    "LedgerPrincipal",
    "LedgerPrincipalPort",
    "LedgerRefused",
    "LedgerRepository",
    "LedgerScope",
    "LedgerUnitOfWork",
]
