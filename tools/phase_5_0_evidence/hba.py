"""`pg_hba.conf` and `pg_ident.conf` analysis: ordering, breadth, and the one
mapping line the design permits.

PostgreSQL uses the **first** matching rule, so ordering is the control and not a
formatting preference (§2.12.3). Two questions follow, and this module answers
both from text an authorized reader supplies — it opens no file, and the
pre-change read that produces the text is an explicitly authorized privileged
step performed by somebody else.

1. **Pre-change discovery.** Is there an existing `trust`, `md5`, `password` or
   wildcard line that would match the coordinator role *before* the Package 5.0
   lines could reject it? The runbook's Part 3a says such a line is *"not a
   confirmed defect; it is a constraint on how the Package 5.0 lines must be
   ordered"*, and that the rehearsal stops until it is resolved.
2. **Post-change ordering.** Once the five lines of §2.12.3 are inserted, is the
   `peer` line first among the lines matching the role, and does every other
   transport reach a `reject`?

## What reaches an evidence record

Line **index**, **method**, **match class** and the verdict. Not the address, not
the option string, not the file's other lines and never its bytes. The file is
read by an authorized human; what this harness records is the structural fact the
design's claim rests on, plus a SHA-256 of the supplied text so the analysis can
be tied to exactly the bytes that were read.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from .errors import ObservationRefused

#: The role §2.12.3 creates, and the only one this analysis cares about.
COORDINATOR_ROLE = "freedom_migration_coordinator"

#: The system user `pg_ident` maps to it, and the only one the map may name.
COORDINATOR_SYSTEM_USER = "freedomcoord"

#: The map name §2.12.3 fixes.
COORDINATOR_MAP = "freedom_coord"

#: Methods that authenticate on something a leaked file can supply, or on nothing
#: at all. A line carrying one of these that matches the coordinator role defeats
#: `PASSWORD NULL` before it is reached.
WEAK_METHODS = frozenset({"trust", "md5", "password", "ident", "gss", "sspi"})

_LOCAL_TYPES = frozenset({"local"})
_HOST_TYPES = frozenset({"host", "hostssl", "hostnossl", "hostgssenc", "hostnogssenc"})


class Breadth(str, Enum):
    """How widely a line matches, in the vocabulary §2.12.3 argues in."""

    #: Names the coordinator role explicitly.
    SPECIFIC = "specific"
    #: `all` in the user column, or a `+group`/`@file` reference that this
    #: analysis cannot resolve and therefore will not assume excludes the role.
    BROAD = "broad"
    #: Names some other principal explicitly.
    UNRELATED = "unrelated"


@dataclass(frozen=True, slots=True)
class HbaLine:
    """One parsed rule. `index` is its position among the non-comment lines."""

    index: int
    connection_type: str
    databases: tuple[str, ...]
    users: tuple[str, ...]
    address: str | None
    method: str
    has_options: bool
    map_name: str | None

    @property
    def breadth(self) -> Breadth:
        if any(user == "all" for user in self.users):
            return Breadth.BROAD
        if any(user.startswith(("+", "@")) for user in self.users):
            return Breadth.BROAD
        if COORDINATOR_ROLE in self.users:
            return Breadth.SPECIFIC
        return Breadth.UNRELATED

    @property
    def matches_coordinator(self) -> bool:
        return self.breadth in (Breadth.BROAD, Breadth.SPECIFIC)

    @property
    def is_weak(self) -> bool:
        return self.method in WEAK_METHODS

    @property
    def match_class(self) -> str:
        """The one string an evidence record carries about this line.

        Deliberately not the line: `local all all` is the design's own vocabulary
        for the breadth being asserted, and the address, options and any other
        principal on the line are not this analysis's business.
        """
        databases = "all" if "all" in self.databases else "named"
        users = "all" if self.breadth is Breadth.BROAD else (
            "coordinator" if self.breadth is Breadth.SPECIFIC else "other"
        )
        return f"{self.connection_type} {databases} {users} {self.method}"


@dataclass(frozen=True, slots=True)
class IdentLine:
    """One identity-map entry."""

    index: int
    map_name: str
    system_user: str
    postgres_user: str

    @property
    def is_regular_expression(self) -> bool:
        return self.system_user.startswith("/")

    @property
    def is_wildcard(self) -> bool:
        return self.system_user in ("all", "*") or any(
            token in self.system_user for token in (".*", ".+", "[")
        )


def _significant_lines(text: str) -> list[tuple[int, list[str]]]:
    lines: list[tuple[int, list[str]]] = []
    index = 0
    for raw in text.splitlines():
        stripped = raw.split("#", 1)[0].strip()
        if not stripped:
            continue
        lines.append((index, stripped.split()))
        index += 1
    return lines


def parse_hba(text: str) -> tuple[HbaLine, ...]:
    """Parse supplied `pg_hba.conf` text. Refuses a line it cannot classify.

    A line this parser cannot read is an `ObservationRefused` rather than a
    skipped line: an ordering analysis that silently ignored a rule would report
    a clean order for a file that has one it could not see, which is the exact
    shape of a guard that runs and cannot fail.
    """
    if not isinstance(text, str):
        raise ObservationRefused("HBA content is supplied as text.")
    parsed: list[HbaLine] = []
    for index, tokens in _significant_lines(text):
        if tokens[0] == "include" or tokens[0].startswith("include_"):
            raise ObservationRefused(
                f"HBA line {index} is an `{tokens[0]}` directive. The rules it "
                "pulls in are not in the supplied text, so no ordering conclusion "
                "can be drawn from this file alone. Supply the included files."
            )
        if len(tokens) < 4:
            raise ObservationRefused(f"HBA line {index} has too few fields to classify.")
        connection_type = tokens[0]
        databases = tuple(tokens[1].split(","))
        users = tuple(tokens[2].split(","))
        if connection_type in _LOCAL_TYPES:
            address = None
            method = tokens[3]
            options = tokens[4:]
        elif connection_type in _HOST_TYPES:
            if len(tokens) < 5:
                raise ObservationRefused(
                    f"HBA line {index} is a host rule with no method."
                )
            address = tokens[3]
            method = tokens[4]
            options = tokens[5:]
        else:
            raise ObservationRefused(
                f"HBA line {index} has connection type {connection_type!r}, which "
                "this analysis does not recognise. It refuses rather than skipping."
            )
        map_name = None
        for option in options:
            if option.startswith("map="):
                map_name = option.split("=", 1)[1]
        parsed.append(
            HbaLine(
                index=index,
                connection_type=connection_type,
                databases=databases,
                users=users,
                address=address,
                method=method,
                has_options=bool(options),
                map_name=map_name,
            )
        )
    return tuple(parsed)


def parse_ident(text: str) -> tuple[IdentLine, ...]:
    if not isinstance(text, str):
        raise ObservationRefused("Identity-map content is supplied as text.")
    parsed: list[IdentLine] = []
    for index, tokens in _significant_lines(text):
        if len(tokens) != 3:
            raise ObservationRefused(
                f"Identity-map line {index} does not have three fields."
            )
        parsed.append(
            IdentLine(
                index=index,
                map_name=tokens[0],
                system_user=tokens[1],
                postgres_user=tokens[2],
            )
        )
    return tuple(parsed)


@dataclass(frozen=True, slots=True)
class HbaFinding:
    """One structural fact about the ordering. Carries no file content."""

    code: str
    line_index: int | None
    match_class: str
    detail: str


@dataclass(frozen=True, slots=True)
class HbaAnalysis:
    """The verdict, plus the digest of the bytes it was taken from."""

    content_sha256: str
    line_count: int
    findings: tuple[HbaFinding, ...]
    coordinator_peer_index: int | None
    first_matching_index: int | None

    @property
    def ordering_holds(self) -> bool:
        """The peer line is the first rule that matches the coordinator role."""
        return (
            self.coordinator_peer_index is not None
            and self.first_matching_index == self.coordinator_peer_index
        )

    @property
    def blocking_findings(self) -> tuple[HbaFinding, ...]:
        return tuple(f for f in self.findings if f.code.startswith("HBA-B"))


def analyse_hba(text: str, *, production_database: str) -> HbaAnalysis:
    """Ordering and breadth analysis for the coordinator role.

    `production_database` is the name §2.12.3 writes as `__PROD_DB__`. It is a
    parameter rather than a constant because the pre-change discovery runs against
    whatever instance the reader read, and the post-change analysis runs against
    the disposable facsimile.
    """
    lines = parse_hba(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    findings: list[HbaFinding] = []

    matching = [line for line in lines if line.matches_coordinator]
    first_matching_index = matching[0].index if matching else None

    peer_index: int | None = None
    for line in lines:
        is_intended_peer = (
            line.connection_type == "local"
            and line.method == "peer"
            and line.breadth is Breadth.SPECIFIC
            and production_database in line.databases
            and line.map_name == COORDINATOR_MAP
        )
        if is_intended_peer and peer_index is None:
            peer_index = line.index
            continue
        if not line.matches_coordinator:
            continue
        if peer_index is None:
            findings.append(
                HbaFinding(
                    code="HBA-B1",
                    line_index=line.index,
                    match_class=line.match_class,
                    detail=(
                        "A rule matching the coordinator role appears before the "
                        "peer line. PostgreSQL uses the first match, so this rule "
                        "decides the role's authentication and §2.12.3's ordering "
                        "control does not hold."
                    ),
                )
            )
        if line.is_weak:
            findings.append(
                HbaFinding(
                    code="HBA-B2" if peer_index is None else "HBA-W1",
                    line_index=line.index,
                    match_class=line.match_class,
                    detail=(
                        f"Method {line.method!r} authenticates on something other "
                        "than the peer credential. `PASSWORD NULL` makes it "
                        "unusable for this role, but the rule's presence above the "
                        "reject lines is a constraint on insertion ordering and is "
                        "reported rather than assumed harmless."
                    ),
                )
            )

    if peer_index is None:
        findings.append(
            HbaFinding(
                code="HBA-B3",
                line_index=None,
                match_class="—",
                detail=(
                    "No `local` `peer` rule naming the coordinator role, the "
                    f"production database {production_database!r} and "
                    f"`map={COORDINATOR_MAP}` is present. Pre-change this is the "
                    "expected state; post-change it is a failed provisioning."
                ),
            )
        )
    else:
        for transport in ("host", "hostssl", "hostnossl"):
            rejected = any(
                line.connection_type == transport
                and line.method == "reject"
                and line.breadth is Breadth.SPECIFIC
                for line in lines
            )
            if not rejected:
                findings.append(
                    HbaFinding(
                        code="HBA-B4",
                        line_index=None,
                        match_class=f"{transport} all coordinator reject",
                        detail=(
                            f"No explicit `{transport}` `reject` for the coordinator "
                            "role. §2.12.3 writes the TCP rejects out precisely so a "
                            "later broad `host all all scram-sha-256` cannot silently "
                            "make the role reachable over the network."
                        ),
                    )
                )
        local_reject = any(
            line.connection_type == "local"
            and line.method == "reject"
            and line.breadth is Breadth.SPECIFIC
            for line in lines
        )
        if not local_reject:
            findings.append(
                HbaFinding(
                    code="HBA-B4",
                    line_index=None,
                    match_class="local all coordinator reject",
                    detail=(
                        "No `local all <coordinator> reject` beneath the peer line, "
                        "so a connection to any other database falls through to "
                        "whatever broad rule follows."
                    ),
                )
            )

    return HbaAnalysis(
        content_sha256=digest,
        line_count=len(lines),
        findings=tuple(findings),
        coordinator_peer_index=peer_index,
        first_matching_index=first_matching_index,
    )


@dataclass(frozen=True, slots=True)
class IdentAnalysis:
    content_sha256: str
    line_count: int
    findings: tuple[HbaFinding, ...]
    coordinator_lines: int

    @property
    def mapping_is_exact(self) -> bool:
        return self.coordinator_lines == 1 and not self.blocking_findings

    @property
    def blocking_findings(self) -> tuple[HbaFinding, ...]:
        return tuple(f for f in self.findings if f.code.startswith("IDENT-B"))


def analyse_ident(text: str) -> IdentAnalysis:
    """The map must have exactly one line, no regular expression, no wildcard."""
    lines = parse_ident(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    findings: list[HbaFinding] = []
    coordinator_lines = 0

    for line in lines:
        if line.map_name != COORDINATOR_MAP:
            if line.postgres_user == COORDINATOR_ROLE:
                findings.append(
                    HbaFinding(
                        code="IDENT-B1",
                        line_index=line.index,
                        match_class=f"{line.map_name} -> coordinator",
                        detail=(
                            "A second map also resolves to the coordinator role. "
                            "The design's claim is that exactly one system user "
                            "reaches it, and a second map is a second route."
                        ),
                    )
                )
            continue
        coordinator_lines += 1
        if line.is_regular_expression or line.is_wildcard:
            findings.append(
                HbaFinding(
                    code="IDENT-B2",
                    line_index=line.index,
                    match_class=f"{COORDINATOR_MAP} regex",
                    detail=(
                        "The map's system-user field is a regular expression or a "
                        "wildcard. §2.12.3 requires one literal system user, "
                        "because the isolation is the map."
                    ),
                )
            )
        if line.system_user != COORDINATOR_SYSTEM_USER:
            findings.append(
                HbaFinding(
                    code="IDENT-B3",
                    line_index=line.index,
                    match_class=f"{COORDINATOR_MAP} -> {line.postgres_user}",
                    detail=(
                        "The map names a system user other than "
                        f"{COORDINATOR_SYSTEM_USER!r}."
                    ),
                )
            )
        if line.postgres_user != COORDINATOR_ROLE:
            findings.append(
                HbaFinding(
                    code="IDENT-B4",
                    line_index=line.index,
                    match_class=f"{COORDINATOR_MAP} -> {line.postgres_user}",
                    detail="The map resolves to a role other than the coordinator.",
                )
            )

    if coordinator_lines > 1:
        findings.append(
            HbaFinding(
                code="IDENT-B5",
                line_index=None,
                match_class=COORDINATOR_MAP,
                detail=(
                    f"The map has {coordinator_lines} lines. §2.12.3 permits exactly "
                    "one, and a second is a second system user that authenticates as "
                    "the coordinator."
                ),
            )
        )
    return IdentAnalysis(
        content_sha256=digest,
        line_count=len(lines),
        findings=tuple(findings),
        coordinator_lines=coordinator_lines,
    )


__all__ = [
    "Breadth",
    "COORDINATOR_MAP",
    "COORDINATOR_ROLE",
    "COORDINATOR_SYSTEM_USER",
    "HbaAnalysis",
    "HbaFinding",
    "HbaLine",
    "IdentAnalysis",
    "IdentLine",
    "WEAK_METHODS",
    "analyse_hba",
    "analyse_ident",
    "parse_hba",
    "parse_ident",
]
