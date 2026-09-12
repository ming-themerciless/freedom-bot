"""The reviewed bytes the run would write, and nothing else it could write.

## What this module is for — conflict C-4

§2.12.3 specifies five `pg_hba.conf` lines and one `pg_ident.conf` line, and the
generator could not emit either as an argument vector: they are file *content*,
and no permitted executable writes content. `install` copies a file that must
already exist, and there is no `tee`, no `sed -i`, no heredoc and no shell
redirection anywhere in this package. That was concrete-plan conflict **C-4**.

Peter Duscha authorized a bounded resolution on 2026-09-06 (package plan
§2.12.2, change-log **C-P5.0-AG**). This module is the bounded half: it is the
**closed table of every byte sequence the harness may ever put on disk**, and it
is in the planning tier, so it is covered by the review manifest and it cannot
write anything. `execution/materializer.py` is the half that writes, and it can
only write what is described here.

## Why this is not a write-file interface

There is no function here that takes a path and some bytes. There are two
`MaterializedFile` values, each with:

* a **filename** that must be one of `targets.POSTGRES_CONFIG_FILES` — two names,
  and no third; `postgresql.conf` is not one of them;
* the **exact lines**, ASCII, no tab, no NUL, no embedded newline, bounded in
  total length;
* a **content digest declared as a constant and verified on construction**. An
  edit to a line that is not accompanied by a deliberate edit to the digest is a
  `PlanRefused` at import, not a quietly different file; and
* the **owner, group and mode**, each pinned to the single permitted value, so a
  materialization cannot install a configuration file owned by anything but the
  PostgreSQL account or readable more widely than the file it replaces.

`reviewed_configuration()` derives the content from the target — the disposable
database name is the one substitution §2.12.3's `__PROD_DB__` has — and then
checks the result against the pinned digest. So the bytes are a function of the
approved target and of this file, and a target whose database name is not the
approved one produces different bytes and is **refused** rather than written.

## Why the file is written whole rather than prepended to

§2.12.3's ordering claim is *"above any broader `local all all` rule"*, which
sounds like an insertion. It is not implemented as one, and the reason is
C-4's own constraint: prepending requires **reading the live host file first**,
and a host-file read is exactly what the authorization refuses. The synthetic
file therefore carries the five lines and then one broader `local all all peer`
rule beneath them, which is the ordering relation the case asserts, and the
byte-exact pre-change capture in `…/before/` is what the reviewed cleanup
reinstalls. `hba.analyse_hba()` over these bytes reports `ordering_holds` and no
finding, and the suite asserts that rather than describing it.

The trailing `local all all peer` is load-bearing rather than decorative: the
reload, the post-reload control and every `psql` cleanup step connect over the
local socket as `postgres`, and a synthetic file without it would lock the
harness out of its own cleanup.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Mapping

from .errors import PlanRefused
from .targets import POSTGRES_CONFIG_FILES, DisposableTarget

#: The only owner, group and mode a materialized configuration file may carry.
#: They are the values the reviewed cleanup restore reinstalls with, so a
#: materialization cannot leave the file in a state the restore would change.
MATERIALIZED_OWNER = "postgres"
MATERIALIZED_GROUP = "postgres"
MATERIALIZED_MODE = 0o640

#: A bound on the whole file. These are six lines and one line; anything an order
#: of magnitude larger is not the reviewed content and is refused before a digest
#: is even compared.
MAX_MATERIALIZED_BYTES = 4096

#: The role and map names §2.12.3 fixes. Repeated from `hba.py` rather than
#: imported, because that module is the *analysis* of a supplied file and this one
#: is the *content*, and a single constant shared between them would make the
#: analysis agree with the content by construction instead of by observation.
COORDINATOR_ROLE = "freedom_migration_coordinator"
COORDINATOR_SYSTEM_USER = "freedomcoord"
COORDINATOR_MAP = "freedom_coord"

#: Column widths for the rendered rules. Fixed, so the bytes are a function of
#: the field values and of nothing else — not of the longest value in the table,
#: which would make an unrelated edit change every line.
_HBA_WIDTHS = (12, 18, 32, 9, 8)
_IDENT_WIDTHS = (16, 19)

_ALLOWED_CHARACTERS = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    " #_-.,:/=+"
)


def _row(fields: tuple[str, ...], widths: tuple[int, ...]) -> str:
    """One rule line: every field but the last padded to a fixed width.

    A field longer than its column gets a single separating space rather than a
    negative pad, so the line stays parseable and the rendering stays total.
    """
    rendered: list[str] = []
    for index, field_value in enumerate(fields):
        if index == len(fields) - 1:
            rendered.append(field_value)
            continue
        width = widths[index] if index < len(widths) else 0
        rendered.append(field_value.ljust(width) if len(field_value) < width else field_value + " ")
    return "".join(rendered).rstrip()


@dataclass(frozen=True, slots=True)
class MaterializedFile:
    """One reviewed byte sequence and the metadata it is installed with.

    Construction is the check. A value of this class that exists has already had
    its filename, character set, length, ownership, mode and **content digest**
    validated, so nothing downstream has to re-derive what "the reviewed bytes"
    means — there is one definition and it is this object.
    """

    filename: str
    lines: tuple[str, ...]
    owner: str
    group: str
    mode: int
    #: Declared as a constant and compared with the content on construction. It
    #: is not computed from the content and stored: a digest derived from
    #: whatever the lines happen to say would agree with any edit, which is the
    #: opposite of pinning them.
    sha256: str

    def __post_init__(self) -> None:
        if self.filename not in POSTGRES_CONFIG_FILES:
            raise PlanRefused(
                f"{self.filename!r} is not a configuration file this harness "
                f"materializes. It writes {sorted(POSTGRES_CONFIG_FILES)} and "
                "nothing else — not `postgresql.conf`, which carries settings "
                "unrelated to the authentication boundary under test."
            )
        if not self.lines:
            raise PlanRefused(
                f"The reviewed content for {self.filename!r} is empty. An empty "
                "authentication configuration is not a smaller change than a "
                "wrong one."
            )
        for line in self.lines:
            if not set(line) <= _ALLOWED_CHARACTERS:
                raise PlanRefused(
                    f"A reviewed line for {self.filename!r} contains a character "
                    "outside the permitted set. A tab, a NUL, a newline or a "
                    "non-ASCII byte in an authentication rule is either a "
                    "mistake or a way to write a second rule on one line."
                )
        if self.owner != MATERIALIZED_OWNER or self.group != MATERIALIZED_GROUP:
            raise PlanRefused(
                f"A materialized configuration file is installed "
                f"{MATERIALIZED_OWNER}:{MATERIALIZED_GROUP}; "
                f"{self.filename!r} names {self.owner}:{self.group}."
            )
        if self.mode != MATERIALIZED_MODE:
            raise PlanRefused(
                f"A materialized configuration file is installed "
                f"{MATERIALIZED_MODE:#o}; {self.filename!r} names {self.mode:#o}."
            )
        content = self.content
        if len(content) > MAX_MATERIALIZED_BYTES:
            raise PlanRefused(
                f"The reviewed content for {self.filename!r} is "
                f"{len(content)} bytes, beyond the {MAX_MATERIALIZED_BYTES}-byte "
                "bound. The reviewed content is six lines and one line."
            )
        computed = hashlib.sha256(content).hexdigest()
        if computed != self.sha256:
            raise PlanRefused(
                f"The reviewed content for {self.filename!r} hashes to "
                f"{computed}, and the pinned digest is {self.sha256}. The digest "
                "is a constant so that editing a rule without deciding to edit "
                "the digest is a refusal rather than a different file."
            )

    @property
    def content(self) -> bytes:
        """The exact bytes. One trailing newline, and no other trailing space."""
        return ("\n".join(self.lines) + "\n").encode("ascii")

    @property
    def byte_count(self) -> int:
        return len(self.content)


def _hba_lines(database_name: str) -> tuple[str, ...]:
    """§2.12.3's five rules, then the one broader rule they must precede."""
    return (
        "# Package 5.0 evidence harness: synthetic pg_hba.conf, disposable "
        "instance only.",
        "# Generated from package-plan 2.12.3. The pre-change file is captured "
        "byte-exactly",
        "# beneath the disposable root and reinstalled by the reviewed cleanup.",
        _row(("# TYPE", "DATABASE", "USER", "ADDRESS", "METHOD", "OPTIONS"), _HBA_WIDTHS),
        _row(("local", database_name, COORDINATOR_ROLE, "", "peer", f"map={COORDINATOR_MAP}"), _HBA_WIDTHS),
        _row(("local", "all", COORDINATOR_ROLE, "", "reject"), _HBA_WIDTHS),
        _row(("host", "all", COORDINATOR_ROLE, "all", "reject"), _HBA_WIDTHS),
        _row(("hostssl", "all", COORDINATOR_ROLE, "all", "reject"), _HBA_WIDTHS),
        _row(("hostnossl", "all", COORDINATOR_ROLE, "all", "reject"), _HBA_WIDTHS),
        "# The one broader rule the five above are asserted to precede. It is "
        "also what keeps",
        "# the reload, the post-reload control and every psql cleanup step able "
        "to connect.",
        _row(("local", "all", "all", "", "peer"), _HBA_WIDTHS),
    )


def _ident_lines() -> tuple[str, ...]:
    return (
        "# Package 5.0 evidence harness: synthetic pg_ident.conf, disposable "
        "instance only.",
        "# Exactly one map line, no regular expression and no wildcard.",
        _row(("# MAPNAME", "SYSTEM-USERNAME", "PG-USERNAME"), _IDENT_WIDTHS),
        _row((COORDINATOR_MAP, COORDINATOR_SYSTEM_USER, COORDINATOR_ROLE), _IDENT_WIDTHS),
    )


#: The pinned digests, one per file, over the content produced for the **approved
#: target**. They are written here rather than computed, so a change to a rule, to
#: a column width or to the disposable database name changes the content, fails
#: this comparison, and has to be re-reviewed instead of silently installed.
REVIEWED_DIGESTS: Mapping[str, str] = {
    "pg_hba.conf": "446d8d1fc64d8d680c6963857472a543ab57962c7ca7a5519442dc678b058909",
    "pg_ident.conf": "ca39dd7b636f6383647c44030f4c63645c8835003c2cf51d4f9bc86692d0388e",
}


def reviewed_configuration(target: DisposableTarget) -> Mapping[str, MaterializedFile]:
    """The two reviewed files, derived from the target and pinned by digest.

    `target.database_name` is the single substitution §2.12.3's `__PROD_DB__`
    has. It is read from the target rather than written here so that the content
    and the vectors cannot disagree about which database the rule names — and the
    pinned digest is what makes a target whose database is not the approved one a
    refusal rather than a different file quietly installed.
    """
    target.require_mutable()
    files = {
        "pg_hba.conf": MaterializedFile(
            filename="pg_hba.conf",
            lines=_hba_lines(target.database_name),
            owner=MATERIALIZED_OWNER,
            group=MATERIALIZED_GROUP,
            mode=MATERIALIZED_MODE,
            sha256=REVIEWED_DIGESTS["pg_hba.conf"],
        ),
        "pg_ident.conf": MaterializedFile(
            filename="pg_ident.conf",
            lines=_ident_lines(),
            owner=MATERIALIZED_OWNER,
            group=MATERIALIZED_GROUP,
            mode=MATERIALIZED_MODE,
            sha256=REVIEWED_DIGESTS["pg_ident.conf"],
        ),
    }
    return files


__all__ = [
    "COORDINATOR_MAP",
    "COORDINATOR_ROLE",
    "COORDINATOR_SYSTEM_USER",
    "MATERIALIZED_GROUP",
    "MATERIALIZED_MODE",
    "MATERIALIZED_OWNER",
    "MAX_MATERIALIZED_BYTES",
    "MaterializedFile",
    "REVIEWED_DIGESTS",
    "reviewed_configuration",
]
