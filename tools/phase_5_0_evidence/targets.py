"""The disposable target, and every guard that keeps the harness away from
anything that is not one.

Nothing in this package plans a mutation without a `DisposableTarget`, and a
target is admissible only when it is **explicitly named, explicitly marked
disposable, and structurally incapable of naming a production object**. The rule
the authorization draft sets is that the executor *"cannot prove the target
disposable"* is a stop condition, so this module's default answer is refusal and
its exceptions are enumerated.

## What is refused, and why each one is here rather than in a reviewer's head

* **`UNASSIGNED`.** The implementation prompt is explicit that inventing a target
  is worse than not having one. `DisposableTarget.unassigned()` is a real value
  that plans and records can carry; it refuses every mutation-bearing use.
* **The root, the repository worktree, and the system hierarchy.** `/`,
  `/opt/freedom-blades/platform`, `/var/lib`, `/etc`, `/usr`, `/boot`, `/home`,
  `/root` and the kernel filesystems. A target equal to any of them, or an
  **ancestor** of any of them, is refused — an ancestor because a cleanup bounded
  to "inside the target" would then be bounded to nothing.
* **`tmpfs` roots.** `/run` and `/tmp`. §2.13.1 defect 1 is precisely this: the
  revision-4 journal lived on `/run`, and the `chattr +a` claim had been inferred
  from a different filesystem. A C-3 result from a `tmpfs` root would repeat that
  error rather than detect it.
* **Production database names**, and anything that is not explicitly an evidence
  database. `freedom_test` is refused as well: it is the repository's shared
  disposable test database (AGENTS.md, finding F-6), and a harness that mutated
  roles and HBA lines in it would be mutating the suite's environment.
* **Unresolved variables, globs, shell metacharacters, relative segments and
  `~`.** A path the harness cannot resolve is a path a reviewer cannot check, and
  a metacharacter in an argument vector is a metacharacter that means nothing —
  which is worse than one that means something, because it is silently literal.

## The naming rule, stated rather than assumed

A disposable root's **last path component** must begin with `fb-evidence-`, and a
disposable database's name must begin with `fb_evidence_`. This is a convention
and it is doing real work: it is what makes "is this the production journal
hierarchy?" a question the harness can answer without knowing the host. A target
that cannot be given such a name is a target the Operations Owner has not made
disposable, and that is a stop condition rather than a naming inconvenience.
"""
from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass

from .errors import TargetRefused

#: The sentinel the execution plan carries when the Operations Owner has not
#: named a target. It is a value, not `None`, so a plan can be assembled,
#: reviewed and published while still refusing to run.
UNASSIGNED = "UNASSIGNED"

#: The repository worktree. Observation **H-1**: it is group-writable by
#: `discordbot` and `freedomweb`, which is the condition OD-65 defers and the
#: reason §2.12.5a's deploy path reads nothing inside it.
REPOSITORY_ROOT = "/opt/freedom-blades/platform"

#: Absolute paths that may never be a mutation root, nor contain one as a direct
#: identity. Each is either the system's own hierarchy or a path the package plan
#: names as production.
FORBIDDEN_ROOTS = frozenset(
    {
        "/",
        "/bin",
        "/boot",
        "/dev",
        "/etc",
        "/home",
        "/lib",
        "/lib64",
        "/opt",
        "/proc",
        "/root",
        "/run",
        "/sbin",
        "/srv",
        "/sys",
        "/tmp",
        "/usr",
        "/var",
        "/var/lib",
        "/var/log",
        "/var/run",
        REPOSITORY_ROOT,
        "/opt/freedom-blades",
        "/opt/freedom-blades/coordinator",
        "/opt/freedom-blades/sheet-writer",
        "/var/lib/freedom-sheet-writer",
        "/var/lib/freedom-coordinator",
        "/etc/freedom-blades",
        "/etc/sudoers.d",
    }
)

#: Roots that are `tmpfs` on this host (§8.1 **H-4**) or shared scratch. An
#: append-only or immutability result taken here would be a result about a
#: different filesystem, which is §2.13.1's first defect.
VOLATILE_ROOTS = ("/run", "/tmp", "/dev/shm")

#: Database names that are production, shared, or the server's own.
FORBIDDEN_DATABASES = frozenset(
    {
        "postgres",
        "template0",
        "template1",
        "freedom",
        "freedom_prod",
        "freedom_production",
        "freedom_platform",
        "freedom_live",
        # The repository's shared disposable test database. Not production, and
        # still not this harness's to mutate: the two suites share it (F-6), so a
        # role or HBA change here would change what the suites measure.
        "freedom_test",
    }
)

#: The evidence naming convention. Both are anchored and both are checked.
_ROOT_PREFIX = "fb-evidence-"
_DATABASE_PREFIX = "fb_evidence_"

_DATABASE_NAME = re.compile(r"\A[a-z][a-z0-9_]{0,62}\Z")
_ACCOUNT_NAME = re.compile(r"\A[a-z_][a-z0-9_-]{0,31}\Z")

#: Characters that make an argument mean something to a shell. The harness emits
#: argument vectors and never a shell string, so any of these in a path is either
#: a mistake or an attempt to construct a command by concatenation.
_SHELL_METACHARACTERS = set(";|&$`<>()!#\n\r\t\\\"'*?[]{}")

_VARIABLE = re.compile(r"\$\{?[A-Za-z_]|%[A-Za-z_]+%")


def validate_absolute_path(path: str, *, what: str = "path") -> str:
    """Refuse anything that is not a plain, absolute, resolvable path.

    Returns the normalized path. Normalization is `posixpath.normpath` **after**
    the relative-segment check, not instead of it: a path containing `..` is
    refused rather than collapsed, because the reviewer approves the string the
    plan shows and collapsing it silently changes what was approved.
    """
    if not isinstance(path, str):
        raise TargetRefused(f"A {what} is text, not {type(path).__name__}.")
    if not path.strip():
        raise TargetRefused(f"A {what} cannot be blank.")
    if path != path.strip():
        raise TargetRefused(
            f"The {what} {path!r} carries surrounding whitespace, which a reviewer "
            "reading the plan cannot see."
        )
    if _VARIABLE.search(path):
        raise TargetRefused(
            f"The {what} {path!r} contains an unresolved variable. The harness "
            "emits argument vectors, which no shell expands, so the variable would "
            "be taken literally and the command would name a path nobody chose."
        )
    if path.startswith("~"):
        raise TargetRefused(
            f"The {what} {path!r} begins with `~`, which depends on who runs it."
        )
    bad = sorted(set(path) & _SHELL_METACHARACTERS)
    if bad:
        raise TargetRefused(
            f"The {what} {path!r} contains {bad}. A glob or shell metacharacter in "
            "an argument vector is silently literal, and in a shell string it is "
            "silently not — neither is a path a reviewer approved."
        )
    if not path.startswith("/"):
        raise TargetRefused(f"The {what} {path!r} is not absolute.")
    segments = [segment for segment in path.split("/") if segment]
    if any(segment in (".", "..") for segment in segments):
        raise TargetRefused(
            f"The {what} {path!r} contains a relative segment. It is refused rather "
            "than normalized, so what a reviewer approved is what runs."
        )
    normalized = posixpath.normpath(path)
    return normalized


def _is_within(path: str, ancestor: str) -> bool:
    if ancestor == "/":
        return path != "/"
    return path == ancestor or path.startswith(ancestor + "/")


def validate_mutation_root(path: str) -> str:
    """The strongest guard in the package: what may be created, written, or
    removed under."""
    normalized = validate_absolute_path(path, what="mutation root")

    if normalized in FORBIDDEN_ROOTS:
        raise TargetRefused(
            f"{normalized!r} is a system or production path. The harness mutates a "
            "disposable hierarchy and nothing else."
        )
    for forbidden in FORBIDDEN_ROOTS:
        if forbidden == "/":
            continue
        if _is_within(forbidden, normalized):
            raise TargetRefused(
                f"{normalized!r} is an ancestor of {forbidden!r}. A cleanup bounded "
                "to 'inside the target' would then be bounded to a production path."
            )
    if _is_within(normalized, REPOSITORY_ROOT):
        raise TargetRefused(
            f"{normalized!r} is inside the repository worktree. Observation H-1 "
            "makes that tree group-writable by two service identities, so evidence "
            "taken there is evidence about the wrong filesystem and the wrong "
            "permission model."
        )
    for volatile in VOLATILE_ROOTS:
        if _is_within(normalized, volatile):
            raise TargetRefused(
                f"{normalized!r} is under {volatile!r}, which is tmpfs or shared "
                "scratch on this host (§8.1 H-4). An append-only or immutability "
                "result taken there is a result about a different filesystem — the "
                "exact inference §2.13.1 defect 1 records."
            )
    depth = len([segment for segment in normalized.split("/") if segment])
    if depth < 3:
        raise TargetRefused(
            f"{normalized!r} is too shallow to be a disposable evidence root. The "
            "hierarchy it stands in for is three levels deep, and a two-level path "
            "is far more likely to be a system directory than an evidence one."
        )
    leaf = normalized.rsplit("/", 1)[1]
    if not leaf.startswith(_ROOT_PREFIX):
        raise TargetRefused(
            f"A disposable evidence root's last component begins with "
            f"{_ROOT_PREFIX!r}; {leaf!r} does not. The convention is what lets this "
            "harness tell a disposable hierarchy from the production one without "
            "knowing the host."
        )
    return normalized


def validate_database_name(name: str) -> str:
    """A disposable evidence database, and provably not a production one."""
    if not isinstance(name, str) or not name.strip():
        raise TargetRefused("A database name is non-blank text.")
    if not _DATABASE_NAME.match(name):
        raise TargetRefused(
            f"{name!r} is not a plain PostgreSQL identifier. A quoted or mixed-case "
            "name would have to be escaped to be used, and this harness builds no "
            "SQL by concatenation."
        )
    if name in FORBIDDEN_DATABASES:
        raise TargetRefused(
            f"{name!r} is a production, shared or server-owned database. The "
            "authorization covers a disposable facsimile and nothing else."
        )
    if not name.startswith(_DATABASE_PREFIX):
        raise TargetRefused(
            f"A disposable evidence database's name begins with {_DATABASE_PREFIX!r}; "
            f"{name!r} does not."
        )
    return name


def validate_account_name(name: str) -> str:
    """An OS account or group name the harness may create in the disposable
    environment. Production identities are refused here rather than at the point
    a `userdel` is emitted."""
    if not isinstance(name, str) or not _ACCOUNT_NAME.match(name or ""):
        raise TargetRefused(f"{name!r} is not a usable OS account or group name.")
    if name in {"root", "postgres", "discordbot", "freedomweb", "foundry", "sudo"}:
        raise TargetRefused(
            f"{name!r} is an existing identity on this host. The harness creates "
            "`freedomcoord`, `freedomsheet`, `fbprobe` and `freedomjournal` in a "
            "disposable environment and touches no existing account or group."
        )
    return name


#: The only two files the harness would ever write outside its own root, and the
#: reason the exception exists at all: PostgreSQL reads its authentication
#: configuration from its own data or configuration directory, so an ordering
#: result taken from a copy under the evidence root would be a result about a
#: file no server consults.
POSTGRES_CONFIG_FILES = frozenset({"pg_hba.conf", "pg_ident.conf"})


def validate_postgres_config_directory(path: str) -> str:
    """The disposable instance's configuration directory.

    It is not under the evidence root and cannot be, so it gets the same refusals
    as a mutation root minus the naming convention — and one extra: it must name a
    PostgreSQL configuration directory rather than an arbitrary place under
    `/etc`, so that a mistyped path refuses instead of writing a file somewhere a
    reviewer did not expect.
    """
    normalized = validate_absolute_path(path, what="PostgreSQL configuration directory")
    if normalized in FORBIDDEN_ROOTS:
        raise TargetRefused(
            f"{normalized!r} is a system path, not a PostgreSQL instance's "
            "configuration directory."
        )
    for forbidden in FORBIDDEN_ROOTS:
        if forbidden != "/" and _is_within(forbidden, normalized):
            raise TargetRefused(
                f"{normalized!r} is an ancestor of {forbidden!r}."
            )
    if _is_within(normalized, REPOSITORY_ROOT):
        raise TargetRefused(f"{normalized!r} is inside the repository worktree.")
    segments = [segment for segment in normalized.split("/") if segment]
    if "postgresql" not in segments and "pgsql" not in segments:
        raise TargetRefused(
            f"{normalized!r} does not look like a PostgreSQL configuration "
            "directory. The harness writes `pg_hba.conf` and `pg_ident.conf` for a "
            "disposable instance and must not write them anywhere else."
        )
    return normalized


@dataclass(frozen=True, slots=True)
class DisposableTarget:
    """The one place a plan says what it would touch.

    `confirmed_disposable` is not a convenience flag. It records that the
    Operations Owner named this host, this filesystem and this PostgreSQL
    instance as disposable — the first item of the authorization draft's required
    sequence. Without it every mutation-bearing use refuses, which is how
    `UNASSIGNED` and "named but not yet confirmed" stay distinguishable.
    """

    host: str
    root_path: str
    database_name: str
    postgres_socket_directory: str
    confirmed_disposable: bool
    #: Why the Operations Owner considers it disposable, recorded in the plan so
    #: the claim is reviewable rather than asserted.
    disposability_evidence: str = ""
    #: The disposable PostgreSQL instance's configuration directory — the one
    #: place `pg_hba.conf` and `pg_ident.conf` may be written. It is deliberately
    #: **not** under `root_path`: a PostgreSQL instance keeps its configuration
    #: where the distribution puts it, and pretending otherwise would produce an
    #: HBA ordering result about a file no server reads. It is therefore guarded
    #: by its own rule (`config_path`) rather than by the root containment rule.
    postgres_config_directory: str = UNASSIGNED

    def __post_init__(self) -> None:
        if self.is_unassigned:
            return
        if not isinstance(self.host, str) or not self.host.strip():
            raise TargetRefused("A named target has a host.")
        object.__setattr__(self, "root_path", validate_mutation_root(self.root_path))
        object.__setattr__(self, "database_name", validate_database_name(self.database_name))
        object.__setattr__(
            self,
            "postgres_socket_directory",
            validate_absolute_path(self.postgres_socket_directory, what="socket directory"),
        )
        if self.postgres_config_directory != UNASSIGNED:
            object.__setattr__(
                self,
                "postgres_config_directory",
                validate_postgres_config_directory(self.postgres_config_directory),
            )
        if self.confirmed_disposable and not self.disposability_evidence.strip():
            raise TargetRefused(
                "A target confirmed disposable records why. 'Confirmed' with no "
                "stated evidence is the shape of an assumption, and the "
                "authorization draft's first stop condition is exactly that the "
                "target cannot be proved disposable."
            )

    @classmethod
    def unassigned(cls) -> "DisposableTarget":
        """No target has been named. Every mutation-bearing use refuses."""
        return cls(
            host=UNASSIGNED,
            root_path=UNASSIGNED,
            database_name=UNASSIGNED,
            postgres_socket_directory=UNASSIGNED,
            confirmed_disposable=False,
            disposability_evidence="",
            postgres_config_directory=UNASSIGNED,
        )

    @property
    def is_unassigned(self) -> bool:
        return self.host == UNASSIGNED and self.root_path == UNASSIGNED

    @property
    def identity(self) -> str:
        """How a record names this target. Never a credential, never an address."""
        if self.is_unassigned:
            return UNASSIGNED
        return f"{self.host}:{self.root_path}"

    def require_mutable(self) -> None:
        """Raise unless this target may be mutated at all."""
        if self.is_unassigned:
            raise TargetRefused(
                "No disposable target has been named. `UNASSIGNED` is the correct "
                "state until the Operations Owner names one, and inventing a "
                "target is a stop condition rather than a default."
            )
        if not self.confirmed_disposable:
            raise TargetRefused(
                f"{self.identity} is named but not confirmed disposable. The "
                "harness defaults to refusal, not to dry-run-and-hope."
            )

    def contained_path(self, path: str) -> str:
        """A path this target may create, write or remove. Refuses anything
        outside its own root, so no step and no cleanup can reach past it."""
        self.require_mutable()
        normalized = validate_absolute_path(path, what="target path")
        if not _is_within(normalized, self.root_path) or normalized == self.root_path:
            raise TargetRefused(
                f"{normalized!r} is not strictly inside the disposable root "
                f"{self.root_path!r}. Every artifact the harness creates lives "
                "under that root, so anything else is a path it did not create and "
                "must not remove."
            )
        return normalized


    def root_or_contained_path(self, path: str) -> str:
        """The disposable root **itself**, or any path strictly inside it.

        **Ruled and accepted.** Peter Duscha accepted Codex's recommendation on
        2026-09-06, recorded in package plan §2.12.2 and change-log
        **C-P5.0-AG**: the harness may create and later remove the exact
        disposable target root it owns, as well as its descendants, and it may do
        so only after all existing `DisposableTarget` validation has succeeded.
        This method is that ruling and the whole of it.

        It is deliberately a **separate method** rather than a relaxation of
        `contained_path()`. The run creates its own root — `install --directory
        <root>` is the first provisioning step — so the root is an object the run
        makes and cleanup must remove. Every other path in the package continues
        to go through `contained_path()`, which still refuses the root, so the
        exception reaches exactly one path and exactly the two places that need
        it: the root's own `DIRECTORY` mutation and the `rmdir` derived from it.

        The root is not less validated than the paths under it; it is more.
        `validate_mutation_root()` has already refused `/`, every entry of
        `FORBIDDEN_ROOTS` and every ancestor of one, the repository worktree,
        every `tmpfs` root, anything shallower than three levels and anything
        whose last component is not `fb-evidence-`-prefixed — and, through
        `validate_absolute_path()`, every relative segment, unresolved variable,
        glob, shell metacharacter and `~`. A sibling root is refused because it
        is not this target's, and a `..` escape is refused rather than collapsed.

        **The only root cleanup vector is a non-recursive `rmdir`**, which
        removes an empty directory and nothing else, so a root still holding an
        artifact the plan did not declare is reported as residue rather than
        deleted. `cleanup.FORBIDDEN_CLEANUP_TOKENS` additionally makes a
        recursive or wildcard removal unexpressible, so the exception cannot be
        combined with one.
        """
        self.require_mutable()
        normalized = validate_absolute_path(path, what="target path")
        if normalized == self.root_path:
            return normalized
        return self.contained_path(normalized)

    def config_path(self, filename: str) -> str:
        """`pg_hba.conf` or `pg_ident.conf` inside the disposable instance's own
        configuration directory. Two names, and no third."""
        self.require_mutable()
        if filename not in POSTGRES_CONFIG_FILES:
            raise TargetRefused(
                f"{filename!r} is not a PostgreSQL configuration file this harness "
                f"writes. It writes {sorted(POSTGRES_CONFIG_FILES)} and nothing else "
                "— not `postgresql.conf`, which carries settings unrelated to the "
                "authentication boundary under test."
            )
        if self.postgres_config_directory == UNASSIGNED:
            raise TargetRefused(
                "The disposable PostgreSQL instance's configuration directory has "
                "not been named, so no HBA or identity-map line can be planned."
            )
        return f"{self.postgres_config_directory}/{filename}"


__all__ = [
    "DisposableTarget",
    "FORBIDDEN_DATABASES",
    "FORBIDDEN_ROOTS",
    "REPOSITORY_ROOT",
    "UNASSIGNED",
    "VOLATILE_ROOTS",
    "validate_absolute_path",
    "validate_account_name",
    "validate_database_name",
    "validate_mutation_root",
    "validate_postgres_config_directory",
    "POSTGRES_CONFIG_FILES",
]
