"""R-48 and R-49: bounded, cursor-paginated, disclosure-safe audit search.

Three properties, and each is a control rather than a feature.

## Append-only, with no exception anywhere in the surface

There is deliberately **no** audit export route, **no** audit mutation route and
**no** audit deletion route, and this module exposes no use case for one. That is
the application half of a rule the database already holds: the restricted runtime
role has only `SELECT, INSERT` on `audit_events`, and migration 0002's trigger
refuses `UPDATE` and `DELETE` **even for the schema owner**. Corrections are
compensating entries, which is the plan's rule for the whole platform.

## Bounded, because the table grows forever

N-21 forbids an unbounded offset scan and N-63 bounds the filters: a free-text
filter is at most 120 characters, at most five filters may be combined, and a
time range is at most 366 days. `total_is_unbounded` is `true` permanently, and
that is not a placeholder — a `COUNT(*)` over an append-only log **is** the
unbounded scan N-21 forbids, so the view says there is no total rather than
computing one.

The action filter is a **prefix**, not a substring: `reconciliation.` is an index
range and `%council%` is a scan of every row that has ever been written.

## Safe, by projecting rather than by filtering

`AuditRow.facts` is a flattened, bounded, structured projection of the payload —
**not** the payload. `application/audit.py` already restricts payloads to JSON
scalars, mappings and sequences and rejects bytes; this narrows further to
key/before/after triples with per-value bounds.

The direction of that rule matters. A projection that rendered every key and
redacted a denylist would be safe only for the keys somebody remembered; this one
renders a key **only** if the projection recognizes it, and shows an unrecognized
key as a redacted marker. So a future writer that puts a new key in a payload
widens the audit table and does not widen the response, which is the difference
between a control and a habit.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from uuid import UUID

from application.audit import ActorCapability
from application.web.errors import RefusalCode, WebRefusal
from application.web.pagination import Page, decode
from application.web.view_models import (
    AUDIT_FACT_BOUND,
    AUDIT_VALUE_BOUND,
    DISCORD_NAME_BOUND,
    Actor,
    AuditFact,
    AuditFilters,
    AuditRow,
    AuditSearchView,
    Correlation,
    Instant,
    SafeText,
    bounded_tuple,
)

#: N-63. A free-text filter value is at most 120 characters, at most five filters
#: may be combined in one query, and a time range spans at most 366 days.
FILTER_VALUE_BOUND = 120
MAX_SIMULTANEOUS_FILTERS = 5
MAX_RANGE_DAYS = 366

AUDIT_CURSOR_SCOPE = "p3.3:audit"

#: The payload keys the projection renders, and the **only** ones. Everything
#: else is shown as a redacted key.
#:
#: Every entry here is an identifier, a count, a closed-vocabulary code or a
#: timestamp. None of them can carry Actor content, artifact bytes, a token, a
#: credential, an exception message, SQL or a filesystem path — because a key is
#: on this list only if the writer that sets it is one of the services in this
#: repository and the value it sets is one of those things.
#:
#: A *before*/*after* pair is recognised by suffix, so `folder_id_before` and
#: `folder_id_after` fold into one fact rather than becoming two rows a reader
#: has to pair up by eye.
#: Completeness is **checked**, not remembered: a regression parses every
#: `AuditEvent(payload={...})` literal in this repository and requires each key
#: to be here or in a stated exclusion set. Rendering already fails closed, so a
#: missing entry is not a disclosure — it is a silent loss, where a Council
#: member reading history sees `(not rendered)` where the platform meant to show
#: them a fact, and nobody finds out until an incident.
RENDERED_PAYLOAD_KEYS = frozenset(
    {
        "access_id",
        "access_kind",
        "actor_count",
        "attempts",
        #: P3.1 authentication facts. `capabilities` is the resolved capability
        #: **set** a login produced, which is the fact an incident review needs;
        #: the code, the tokens, the state and the verifier appear in no audit
        #: payload, ever.
        "auth_method",
        "capabilities",
        "capability",
        "character_id",
        "checksum",
        "created_count",
        "duplicate_of",
        "absent",
        "blocked",
        "duplicate",
        "errors",
        "failure_code",
        "folder_id",
        "import_id",
        "invalidated_jobs",
        "issue_codes",
        "job_id",
        "kind",
        "lease_owner",
        #: The session-concurrency bound (N-66) an automatic revocation cites.
        "limit",
        "mapped",
        "mapping_id",
        "mode",
        "observed_state",
        #: The named operator of a host-local command (C-07). A person's name,
        #: bounded like any other external text, and never the secret they
        #: handled.
        "operator",
        "outcome",
        "previous_session_id",
        "provider_key",
        "preview_job_id",
        "profile_version",
        "proposal_id",
        "provenance",
        "reaped_by",
        #: Council-supplied text on a grant, a revocation or an identity
        #: decision, and a closed refusal code on an authentication event. It is
        #: **not** artifact-derived — §3.3's rule is about reconciliation
        #: warnings, which never reach a payload at all — so it is rendered under
        #: §3.2's 200-character per-value bound like any other external text, and
        #: only to Council and administrators.
        "reason",
        "request_key_digest",
        "resolution",
        "revoked",
        "role_id",
        "session_id",
        "snapshot_id",
        "stale_reason",
        "state",
        "status",
        "unmapped",
        "updated_count",
        "warning_count",
        "warnings",
        "would_create",
        "would_update",
    }
)

_BEFORE = "_before"
_AFTER = "_after"


class FilterBounds(WebRefusal):
    """N-63 exceeded. `422`, because the caller can narrow it and try again."""

    def __init__(self) -> None:
        super().__init__(RefusalCode.FILTER_BOUNDS, status=422)


class AuditSearchService:
    """The one read path over `audit_events`, and there is no write path at all."""

    __slots__ = ("_audit", "_accounts", "_bounds", "_cursor_key")

    def __init__(self, *, audit, accounts, bounds, cursor_key) -> None:
        self._audit = audit
        self._accounts = accounts
        self._bounds = bounds
        self._cursor_key = cursor_key

    def search(
        self,
        *,
        context,
        query,
        cursor_token: str | None,
        size: int,
    ) -> AuditSearchView:
        """VM-18. Council, administrator and break-glass; nobody else.

        Break-glass reaches this — it is the one P3.3 surface N-65 permits,
        because reading history is how an administrator restoring continuity
        finds out what happened, and reading changes nothing.
        """
        if not (context.guild_council or context.platform_administrator):
            raise WebRefusal(RefusalCode.INSUFFICIENT_CAPABILITY, status=403)
        filters = self._filters(query)
        position = decode(
            self._cursor_key, cursor_token, scope=AUDIT_CURSOR_SCOPE, arity=2
        )
        rows = self._audit.search(filters=filters, position=position, size=size)
        page = Page.of(
            rows,
            size=size,
            key=self._cursor_key,
            scope=AUDIT_CURSOR_SCOPE,
            # `(occurred_at DESC, id DESC)` — the stable total order the accepted
            # index serves. The trailing id is what makes it total: two events in
            # the same microsecond would otherwise tie at a page boundary and one
            # of them would never be shown.
            position=lambda row: (row["occurred_at"].isoformat(), str(row["id"])),
        )
        account_ids = [row["actor_platform_account_id"] for row in page.rows]
        labels = self._accounts.labels_for(account_ids)
        legacy = self._audit.labels_for_discord_actors(
            [row["actor_discord_user_id"] for row in page.rows]
        )
        rendered, _ = bounded_tuple(
            (self._row(row, labels, legacy) for row in page.rows), size
        )
        return AuditSearchView(
            state="ready" if rendered else "empty",
            filters=filters,
            rows=rendered,
            cursor=page.cursor,
            page_size=size,
        )

    # -- filters -----------------------------------------------------------
    def _filters(self, query) -> AuditFilters:
        """Parse and bound the query string. Refuses rather than silently drops.

        A filter the platform quietly ignored would answer a different question
        from the one asked, and an operator reading an audit result has to be
        able to trust that the rows shown are the rows that match.
        """
        supplied = {
            key: value
            for key, value in {
                "action_prefix": _text(query.get("action")),
                "entity_type": _text(query.get("entity_type")),
                "entity_id": _text(query.get("entity_id")),
                "capability": _text(query.get("capability")),
                "source": _text(query.get("source")),
                "occurred_from": _text(query.get("from")),
                "occurred_to": _text(query.get("to")),
                "correlation_id": _text(query.get("correlation_id")),
            }.items()
            if value
        }
        if len(supplied) > MAX_SIMULTANEOUS_FILTERS:
            raise FilterBounds()
        for value in supplied.values():
            if len(value) > FILTER_VALUE_BOUND:
                raise FilterBounds()

        capability = None
        if "capability" in supplied:
            try:
                capability = ActorCapability(supplied["capability"])
            except ValueError:
                raise FilterBounds() from None
        source = supplied.get("source")
        if source is not None and source not in _SOURCES:
            raise FilterBounds()
        correlation_id = None
        if "correlation_id" in supplied:
            try:
                correlation_id = UUID(supplied["correlation_id"])
            except ValueError:
                raise FilterBounds() from None
        occurred_from = _instant(supplied.get("occurred_from"))
        occurred_to = _instant(supplied.get("occurred_to"))
        if occurred_from and occurred_to:
            if occurred_to < occurred_from:
                raise FilterBounds()
            if occurred_to - occurred_from > timedelta(days=MAX_RANGE_DAYS):
                raise FilterBounds()
        return AuditFilters(
            action_prefix=(
                SafeText.bounded(supplied["action_prefix"], FILTER_VALUE_BOUND)
                if "action_prefix" in supplied
                else None
            ),
            entity_type=supplied.get("entity_type"),
            entity_id=(
                SafeText.bounded(supplied["entity_id"], FILTER_VALUE_BOUND)
                if "entity_id" in supplied
                else None
            ),
            capability=capability,
            source=source,
            occurred_from=Instant.of(occurred_from) if occurred_from else None,
            occurred_to=Instant.of(occurred_to) if occurred_to else None,
            correlation_id=correlation_id,
        )

    # -- rendering ---------------------------------------------------------
    def _row(self, row, labels, legacy) -> AuditRow:
        account_id = row["actor_platform_account_id"]
        actor = None
        if account_id is not None:
            actor = Actor(
                account_id=account_id,
                label=SafeText.bounded(
                    labels.get(account_id) or f"Account {str(account_id)[:8]}",
                    DISCORD_NAME_BOUND,
                ),
                capability=ActorCapability(row["actor_capability"]),
            )
        elif row["actor_discord_user_id"] is not None:
            # A row written before the migration. It keeps its Discord column and
            # is never rewritten, so the actor is resolved through
            # `external_identities` — including after that identity is retired,
            # which is why an identity is retired rather than deleted.
            resolved = legacy.get(row["actor_discord_user_id"])
            if resolved is not None:
                actor = Actor(
                    account_id=resolved["account_id"],
                    label=SafeText.bounded(resolved["label"], DISCORD_NAME_BOUND),
                    capability=ActorCapability(row["actor_capability"]),
                )
        facts, truncated = self._facts(row["payload"])
        return AuditRow(
            event_id=row["id"],
            occurred_at=Instant.of(row["occurred_at"]),
            actor=actor,
            actor_capability=ActorCapability(row["actor_capability"]),
            action=row["action"],
            entity_type=row["entity_type"],
            entity_id=SafeText.bounded(row["entity_id"], FILTER_VALUE_BOUND),
            source=row["source"],
            correlation=Correlation(row["correlation_id"]),
            facts=facts,
            payload_truncated=truncated,
        )

    def _facts(self, payload) -> tuple[tuple[AuditFact, ...], bool]:
        """The payload as at most 40 bounded key/before/after triples.

        An unrecognized key renders as a key with `redacted = True` and **no
        value at all** — not a truncated one, not a type name, not a length.
        """
        if not isinstance(payload, Mapping):
            return (), False
        pairs: dict[str, dict[str, object]] = {}
        order: list[str] = []
        for key, value in payload.items():
            name, slot = _classify(str(key))
            if name not in pairs:
                pairs[name] = {}
                order.append(name)
            pairs[name][slot] = value

        facts = []
        for name in order:
            if name not in RENDERED_PAYLOAD_KEYS:
                facts.append(AuditFact(key=name, before=None, after=None, redacted=True))
                continue
            slots = pairs[name]
            facts.append(
                AuditFact(
                    key=name,
                    before=_value(slots.get("before")),
                    after=_value(slots.get("after") if "after" in slots else slots.get("value")),
                )
            )
        bounded, dropped = bounded_tuple(facts, AUDIT_FACT_BOUND)
        # `payload_truncated` is true when a *value* was cut as well as when the
        # record held more facts than the bound: both are the response carrying
        # less than the row does, and a reader needs to know either way.
        cut = any(
            (fact.before is not None and fact.before.truncated)
            or (fact.after is not None and fact.after.truncated)
            for fact in bounded
        )
        return bounded, dropped or cut


def _classify(key: str) -> tuple[str, str]:
    if key.endswith(_BEFORE):
        return key[: -len(_BEFORE)], "before"
    if key.endswith(_AFTER):
        return key[: -len(_AFTER)], "after"
    return key, "value"


def _value(raw) -> SafeText | None:
    """One payload value, rendered as bounded text or not at all.

    A sequence is joined into a bounded comma list because the two sequence-valued
    keys the platform writes — `issue_codes` and `warnings` — are closed
    vocabularies. Anything nested is not rendered: an audit fact is a scalar
    comparison, and a mapping inside one would be a structure with no bound.
    """
    if raw is None:
        return None
    if isinstance(raw, bool):
        return SafeText.bounded("true" if raw else "false", AUDIT_VALUE_BOUND)
    if isinstance(raw, (int, float, str)):
        return SafeText.bounded(str(raw), AUDIT_VALUE_BOUND)
    if isinstance(raw, Sequence):
        return SafeText.bounded(
            ", ".join(str(item) for item in raw if isinstance(item, (str, int, float))),
            AUDIT_VALUE_BOUND,
        )
    return None


def _text(value) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    return stripped or None


def _instant(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        raise FilterBounds() from None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


_SOURCES = frozenset({"discord", "web", "foundry", "import", "system"})


__all__ = [
    "AUDIT_CURSOR_SCOPE",
    "FILTER_VALUE_BOUND",
    "MAX_RANGE_DAYS",
    "MAX_SIMULTANEOUS_FILTERS",
    "RENDERED_PAYLOAD_KEYS",
    "AuditSearchService",
    "FilterBounds",
]
