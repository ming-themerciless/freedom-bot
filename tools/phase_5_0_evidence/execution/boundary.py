"""The one place in the harness that starts a process.

Everything else — the planner, the cleanup generator, the executor — works in
terms of `ProcessBoundary`, which is a protocol with two implementations: this
module's `SubprocessBoundary`, and whatever fake a test injects. That is what
makes the whole executor testable without a privileged host, and it is what makes
*"the harness cannot run what it plans"* still true of every module outside this
one.

## Why raw output does not leave this module

`run()` returns a `CommandResult` whose only textual content is the **sanitized
observations** `capture.sanitize` produced. The bytes a command wrote are read
into a local, passed to the sanitizer and dropped. There is therefore no object
anywhere above this line that holds stdout, so no later code can serialize it by
accident, and a reviewer checking *"can raw output reach an artifact?"* has one
function to read rather than a call graph to trace.

Standard error is treated the same way and more narrowly: only **whether** it was
non-empty is recorded. A refusal's message is exactly the kind of text that
carries a rule, a path, a role name or a hostname, and the evidence a case needs
from a refusal is its exit status and the errno the case names — not the
sentence PostgreSQL or `chattr` chose to print.

## The credential vector, and why it is constructed rather than implied — EH-R5-1

The previous version passed `user=run_as` and `extra_groups=[]` and omitted
`group=`, on the stated belief that `user=` also selects the account's primary
group. It does not. `subprocess` treats the three as separate controls: it calls
`setgroups(extra_groups)`, then `setgid(group)`, then `setuid(user)`, and each
one it is not given is simply not set. The consequence was a child whose primary
group was **the launching process's**, and whose supplementary list was
deliberately **emptied** — including `freedomjournal`, the membership on which
the positive traversal and isolation cases depend. A positive control could then
fail, or a refusal occur, because of how the harness built the identity rather
than because of the authority under test. That is not admissible evidence.

The contract is now explicit and fail-closed, and it is the same one §2.12.2
states for the identities it covers:

* every `run_as` names a row of `IDENTITY_CONTRACT`, a closed table. A name that
  is not a row cannot be launched, and there is no default;
* the account is resolved **before** the process is created — numeric UID,
  numeric primary GID and the numeric GIDs of exactly the supplementary groups
  the reviewed contract states — through an injected `IdentityLookup`, so the
  suite exercises every branch of it without reading the host's account
  database;
* `user=`, `group=` and `extra_groups=` are all three passed explicitly on every
  call. Nothing is inherited from the caller: not its primary group, not its
  supplementary groups, not its UID;
* a row provisioned by the harness (`freedomcoord`, `freedomsheet`, `fbprobe`)
  and a row that is an existing host identity (`postgres`, `discordbot`,
  `freedomweb`) are distinguished by `provisioned_by_harness`, and neither has a
  membership invented for it: both take §2.12.2's list verbatim;
* `MembershipRule.EXACT` means §2.12.2 states that account's **complete**
  supplementary list, so a missing required membership and an unexpected extra
  one are both refusals — the same rule `identity.classify_group_membership`
  applies to the evidence. It is the only rule under which a credential is
  constructed at all, and its permitted set is **read** from
  `identity.CANONICAL_ACCOUNTS` rather than restated here, with
  `RequiredIdentity.__post_init__` refusing a row that disagrees with it;
* **`postgres` is an ordinary row, and this is finding EH-R6-1's disposition.**
  R5 gave it an `AS_CONFIGURED` rule that passed the host's currently configured
  supplementary groups through to the child. Those memberships were fixed by no
  reviewed document, appeared in no covered source and were therefore outside
  the review-manifest digest, so a `usermod` run after Codex approved a digest
  could change the credential vector that executes without changing a reviewed
  byte. R6 deleted the pass-through and refused the row, because §2.12.2 covered
  six accounts and `postgres` was not one of them. **R7 does not restore a
  pass-through and infers nothing**: Peter Duscha ruled the set on 2026-09-06
  (change-log C-P5.0-AE), §2.12.2 carries the row, and this module reads it
  through `_from_canonical` exactly like the others. The permitted set is
  `ssl-cert`; a host that is missing it, or that adds any other group, is
  refused before a process exists. There is now **no rule but `EXACT`**, so
  there is no state a later edit can put a row into in order to avoid stating
  its membership;
* `root` is explicit too. It is never *"whatever identity launched the CLI"*: the
  launching process must already be effective UID and GID 0, the `root` row must
  resolve to UID 0 and GID 0, and the child's credentials are then constructed
  from those resolved numbers like every other row. A non-root launcher cannot
  run a `run_as="root"` step as itself — it is refused before a process exists;
* an absent account or group, an identity whose membership the reviewed design
  has not decided, a missing required membership, an unexpected membership, a
  duplicated record, a name that does not round-trip to the id it claims, a
  non-root row resolving to UID or GID 0, and a supplementary name that resolves
  to no group are each a refusal **before** `subprocess.run`; and
* every refusal is reported as one of `LAUNCH_FAILURES` — a short fixed
  classification. No account database, numeric id, group list or operating-system
  message reaches a `CommandResult`, and therefore none can reach an artifact.

None of this is done with `sudo`, `su`, a shell, `setpriv`, `capsh`, a helper
executable or an environment variable. The reviewed argument vector remains
exactly the vector passed to `subprocess.run`; the credentials are keyword
arguments beside it.

## Resolving one account, and why it must be exactly one record — EH-R6-2

`SystemIdentityLookup` reads the account and group database through an injected
`AccountDatabase`, so every rule below is exercised by the suite without any test
reading a real account. The rules are:

* the direct `getpwnam` / `getgrnam` answer must exist, or the identity is
  **absent**;
* the enumerated records matching that name are **counted, not deduplicated**,
  and there must be exactly one. R5 built a set of `(uid, gid)` pairs and refused
  only when it had more than one member, so two records whose numbers happened to
  match collapsed to one member and were accepted — despite the documented
  contract that a duplicated record is ambiguous and must refuse. That was
  finding **EH-R6-2**, and it applied to group records as well; and
* the direct answer and that single enumerated record must agree **completely** —
  name, and both numbers. A database that answers one thing directly and
  enumerates another is contradicting itself, and this run does not choose
  between them.

Zero records is the *unknown* classification; two records, whether identical or
contradictory, is *inconsistent*. Neither the record, the ids nor the exception
reaches a `CommandResult`.

## Every guard on the call, and why

* **`shell=False`, always, and not passed as a variable.** The literal is written
  at the call site so that no argument, environment value or configuration can
  change it.
* **`argv` is a list of separate arguments** built from a validated
  `CommandStep`, and `argv[0]` is an absolute path. `PATH` is never consulted to
  find it.
* **A fixed environment.** The inherited environment is discarded whole. What is
  passed is `MINIMAL_ENVIRONMENT` plus, for `psql`, the PostgreSQL 16 client
  directory on `PATH` — needed because `psql` looks up its own helpers, not
  because anything here is resolved through it.
* **A bounded timeout, always non-zero.** On expiry the process is killed and the
  result says so; a timed-out step is never satisfied.
* **`stdin` is `/dev/null`.** Nothing can prompt, so nothing can hang waiting for
  an operator who is not there.
* **No `cwd` of the repository.** The working directory is `/`, so a relative
  path nobody wrote cannot resolve against the worktree.
"""
from __future__ import annotations

import grp
import os
import pwd
import stat
import subprocess  # noqa: S404 - the single, declared process boundary
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Mapping, Protocol, Sequence, TypeVar

from ..capture import CapturePolicy, CatalogQuestion, sanitize
from ..errors import HarnessError
from ..identity import CANONICAL_ACCOUNTS

if TYPE_CHECKING:  # pragma: no cover - the import direction, stated once
    from .descriptors import TransferEntry

#: The environment every command runs in. Small, fixed, and containing no
#: credential, no repository path and nothing inherited from the operator's
#: shell. `LC_ALL=C` is load-bearing: it makes every tool's output the byte
#: sequence the capture policies were written against, so an operator's locale
#: cannot change what a run observes.
MINIMAL_ENVIRONMENT: Mapping[str, str] = {
    "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
    "LC_ALL": "C",
    "LANG": "C",
    "SHELL": "/usr/sbin/nologin",
    "TERM": "dumb",
}

#: The PostgreSQL 16 client directory, prepended for `psql` only. The disposable
#: server documents that there is no global client symlink and that test
#: invocations prepend this explicitly.
POSTGRES_16_BIN = "/usr/lib/postgresql/16/bin"

#: Every step gets one. A step with no timeout is a step that can hang a
#: privileged run on a host nobody is watching.
DEFAULT_TIMEOUT_SECONDS = 60.0

#: Per-executable overrides, both directions. `systemd-run --wait` legitimately
#: takes longer; `psql` should never take a minute against a local socket.
TIMEOUT_SECONDS: Mapping[str, float] = {
    "/usr/bin/psql": 30.0,
    "/usr/bin/systemd-run": 120.0,
    "/usr/bin/systemctl": 30.0,
}


def timeout_for(executable: str) -> float:
    return TIMEOUT_SECONDS.get(executable, DEFAULT_TIMEOUT_SECONDS)


def environment_for(executable: str) -> dict[str, str]:
    """The fixed environment, plus the PostgreSQL 16 client path for `psql`."""
    env = dict(MINIMAL_ENVIRONMENT)
    if executable == "/usr/bin/psql":
        env["PATH"] = f"{POSTGRES_16_BIN}:{env['PATH']}"
        # Bound the connection attempt itself as well as the process. A socket
        # that never answers should fail as a connection error, not as a killed
        # process whose exit status means something else.
        env["PGCONNECT_TIMEOUT"] = "10"
    return env


# ---------------------------------------------------------------------------
# Launch classifications — the complete, fixed vocabulary
# ---------------------------------------------------------------------------

#: A boundary that is not armed refuses to start anything.
LAUNCH_BOUNDARY_NOT_ARMED = "boundary-not-armed"
#: The step named no identity. Blank never means `root` and never means "the
#: caller"; it means nothing, and nothing cannot be launched.
LAUNCH_BLANK_IDENTITY = "blank-identity"
LAUNCH_NO_TIMEOUT = "no-timeout"
LAUNCH_NOT_ABSOLUTE = "not-absolute"
#: The identity is not a row of `IDENTITY_CONTRACT`. The contract does not
#: describe an identity that can be constructed, so there is nothing to build a
#: credential from. The vocabulary value is unchanged from R6; what no longer
#: reaches it is a named row whose membership was undecided, there being no such
#: row after the R7 ruling.
LAUNCH_IDENTITY_NOT_IN_CONTRACT = "identity-not-in-contract"
#: An account or a group the contract names does not exist on the host.
LAUNCH_IDENTITY_UNKNOWN = "identity-unknown"
#: A required membership is missing, or an unexpected one is present where the
#: contract states an exact list.
LAUNCH_IDENTITY_MEMBERSHIP = "identity-membership-mismatch"
#: A duplicated record, a name that does not round-trip to its id, a non-root
#: row resolving to a superuser id, or a group id that resolves to no name.
LAUNCH_IDENTITY_INCONSISTENT = "identity-inconsistent"
#: A `run_as="root"` step from a launcher that is not already effective UID/GID 0.
LAUNCH_ROOT_UNAVAILABLE = "root-identity-unavailable"
#: The operating system refused the credential transition itself.
LAUNCH_IDENTITY_REFUSED = "identity-refused"
LAUNCH_EXECUTABLE_ABSENT = "executable-absent"
LAUNCH_TIMEOUT = "timeout"
#: Recorded by the executor when a boundary call raised. It is declared here so
#: that the classification vocabulary a run can serialize is one closed set in
#: one file.
LAUNCH_BOUNDARY_FAILURE = "boundary-failure"
#: Recorded by the executor when a step failed its immediately-before-execution
#: revalidation and was therefore never started.
LAUNCH_VALIDATION_REFUSED = "validation-refused"

#: Every value `CommandResult.launch_failure` may take. Fixed, safe, and short:
#: a reviewer reads this set and knows the complete vocabulary a run can put in
#: an artifact. Nothing derived from the host or from an exception is in it.
#: **r6 §1.4, C-P5.0-LAB-I-R1.** A descriptor-bound effect was refused before it
#: was issued, or no effect issuer was assembled at all. It is a member of this
#: set because a step's outcome carries one classification whether the step was
#: a command or an effect, and because the refusals an effect raises carry a
#: path and an identity that must not reach an artifact.
LAUNCH_EFFECT_REFUSED = "effect-refused"
#: **r6 §§1.3.3 and 6.3.** The five descriptor-transfer refusals, each decided
#: before any process exists.
LAUNCH_DESCRIPTOR_UNDECLARED = "descriptor-not-in-the-declared-table"
LAUNCH_DESCRIPTOR_SYNCHRONIZABLE = "synchronizable-descriptor-not-transferable"
LAUNCH_DESCRIPTOR_CLOSED = "descriptor-closed"
LAUNCH_DESCRIPTOR_NOT_A_DIRECTORY = "descriptor-not-a-directory"
#: No armed effect issuer was assembled, so the step writes nothing. The
#: fail-closed direction: an executor built without one refuses the effect
#: rather than falling back to a pathname-based command.
LAUNCH_EFFECT_UNAVAILABLE = "effect-issuer-unavailable"

LAUNCH_FAILURES: frozenset[str] = frozenset(
    {
        LAUNCH_DESCRIPTOR_CLOSED,
        LAUNCH_DESCRIPTOR_NOT_A_DIRECTORY,
        LAUNCH_DESCRIPTOR_SYNCHRONIZABLE,
        LAUNCH_DESCRIPTOR_UNDECLARED,
        LAUNCH_EFFECT_REFUSED,
        LAUNCH_EFFECT_UNAVAILABLE,
        LAUNCH_BOUNDARY_NOT_ARMED,
        LAUNCH_BLANK_IDENTITY,
        LAUNCH_NO_TIMEOUT,
        LAUNCH_NOT_ABSOLUTE,
        LAUNCH_IDENTITY_NOT_IN_CONTRACT,
        LAUNCH_IDENTITY_UNKNOWN,
        LAUNCH_IDENTITY_MEMBERSHIP,
        LAUNCH_IDENTITY_INCONSISTENT,
        LAUNCH_ROOT_UNAVAILABLE,
        LAUNCH_IDENTITY_REFUSED,
        LAUNCH_EXECUTABLE_ABSENT,
        LAUNCH_TIMEOUT,
        LAUNCH_BOUNDARY_FAILURE,
        LAUNCH_VALIDATION_REFUSED,
    }
)


# ---------------------------------------------------------------------------
# The identity contract
# ---------------------------------------------------------------------------


class MembershipRule(str, Enum):
    """How an account's permitted groups are decided. **There is one rule.**

    R5 had a second value, `AS_CONFIGURED`, which passed the host's currently
    configured supplementary groups through to the child — finding EH-R6-1, and
    it is gone rather than unused. R6 had a third, `UNDECIDED`, recording that
    §2.12.2 did not describe `postgres`; the R7 ruling describes it, so that
    value is gone too rather than left as an escape hatch a later edit could
    reach for. What remains is a single rule under which the only permitted set
    is §2.12.2's, and adding a second is a maintainer ruling recorded in a
    reviewed source — not a code change.
    """

    #: §2.12.2 states this account's **complete** supplementary list. A missing
    #: required membership and an unexpected extra one are both refusals, which
    #: is the same rule the `JNL-52` membership cases are classified under.
    EXACT = "exact"


class IdentityRefusal(HarnessError):
    """The identity a step names cannot be constructed as the contract states.

    These carry a readable message for an operator reading a traceback. **No
    message from this hierarchy reaches a `CommandResult`**: `run()` maps each
    class to one of `LAUNCH_FAILURES` precisely so that an account name, a
    numeric id or a group list cannot travel into an evidence artifact.
    """


class IdentityAbsent(IdentityRefusal):
    """An account or group the contract names does not exist."""


class IdentityInconsistent(IdentityRefusal):
    """The account database contradicts itself, or contradicts the contract."""


class MembershipRefused(IdentityRefusal):
    """The resolved memberships are not the ones the contract requires."""


class PrivilegeUnavailable(IdentityRefusal):
    """A root step was reached from a launcher that is not root."""


@dataclass(frozen=True, slots=True)
class RequiredIdentity:
    """One row of the closed identity contract.

    `supplementary` is the set of group **names** beyond the primary group. For
    the six rows §2.12.2 covers it is that table's own list, transcribed by
    `_from_canonical` rather than restated here, so the membership is stated in
    exactly one place in the repository. `root` is the only row that is not one
    of them, and it states no supplementary group at all.
    """

    name: str
    primary_group: str
    supplementary: frozenset[str]
    rule: MembershipRule
    #: True for the identities this run creates on the disposable target, False
    #: for identities that already exist on the host. It changes nothing about
    #: how the credentials are built — it is the distinction a reviewer needs in
    #: order to see that no membership was invented for an existing account.
    provisioned_by_harness: bool
    #: True for `root` alone. It is a member of the closed set like any other
    #: row, not a default and not a fallback.
    superuser: bool = False

    def __post_init__(self) -> None:
        """The row and §2.12.2 agree, or this module does not import — EH-R6-1.

        The requirement is that the permitted identity cannot drift from the
        reviewed source it is supposed to come from. It is enforced here, per
        row, rather than by a comparison somebody has to remember to run: a
        canonical row edited in `identity.py` and not here, or a supplementary
        set written here for an account §2.12.2 does not cover, raises while the
        table is being built rather than at the moment a credential is applied.
        """
        canonical = CANONICAL_ACCOUNTS.get(self.name)
        if self.rule is not MembershipRule.EXACT:
            raise IdentityInconsistent(
                f"{self.name!r} states a membership rule this contract does not "
                "have. §2.12.2's set is the only permitted set, and a second rule "
                "is a maintainer ruling rather than a code change"
            )
        if canonical is not None:
            if (
                self.primary_group != canonical.primary_group
                or self.supplementary != canonical.supplementary
                or self.provisioned_by_harness is not canonical.provisioned_by_package
            ):
                raise IdentityInconsistent(
                    f"the contract's row for {self.name!r} does not match §2.12.2, "
                    "which is the single place a membership is stated"
                )
            return
        if not self.superuser:
            raise IdentityInconsistent(
                f"{self.name!r} is not in §2.12.2 and is not the superuser row, so "
                "an exact supplementary list for it would be a membership stated "
                "outside the canonical table — stop condition 10p"
            )
        if self.supplementary:
            raise IdentityInconsistent(
                "the superuser row states no supplementary group"
            )


def _from_canonical(name: str) -> RequiredIdentity:
    """§2.12.2's row for `name`, as a credential requirement."""
    account = CANONICAL_ACCOUNTS[name]
    return RequiredIdentity(
        name=account.name,
        primary_group=account.primary_group,
        supplementary=account.supplementary,
        rule=MembershipRule.EXACT,
        provisioned_by_harness=account.provisioned_by_package,
    )


#: Every identity a step may run as, and the exact credentials each one means.
#: Closed: `run()` refuses a name that is not a key, so a typo is a refusal
#: rather than an unexpected transition.
#:
#: `postgres` was the one row §2.12.2 did not describe — EH-R6-1. Peter Duscha
#: ruled it on 2026-09-06 (change-log C-P5.0-AE): §2.12.2 now carries the row, and
#: this table reads it through `_from_canonical` like every other. There is no row
#: here whose membership is stated anywhere but §2.12.2, and no rule under which
#: one could be.
IDENTITY_CONTRACT: Mapping[str, RequiredIdentity] = {
    identity.name: identity
    for identity in (
        RequiredIdentity(
            name="root",
            primary_group="root",
            supplementary=frozenset(),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=False,
            superuser=True,
        ),
        _from_canonical("postgres"),
        _from_canonical("freedomcoord"),
        _from_canonical("freedomsheet"),
        _from_canonical("fbprobe"),
        _from_canonical("discordbot"),
        _from_canonical("freedomweb"),
    )
}



@dataclass(frozen=True, slots=True)
class ResolvedCredential:
    """The numeric identity a child will be given. Three explicit values."""

    uid: int
    gid: int
    supplementary_gids: tuple[int, ...]

    def as_keywords(self) -> dict[str, object]:
        """Exactly what is passed to `subprocess.run`, and nothing implied.

        `extra_groups` carries the supplementary groups only; the primary group
        is `group=`, which `setgid` establishes. Passing all three means the
        child's credentials are a function of the contract and of the host's
        account database — never of the process that launched the harness.
        """
        return {
            "user": self.uid,
            "group": self.gid,
            "extra_groups": list(self.supplementary_gids),
        }


class IdentityLookup(Protocol):
    """The seam the credential tests inject across.

    It exists so that the account database is read in exactly one class, which a
    test replaces wholesale. No test in this repository reads the host's real
    accounts or groups, and none needs to.
    """

    def account(self, name: str) -> tuple[int, int]:
        """`(uid, primary gid)` for an account, or an `IdentityRefusal`."""

    def group_id(self, name: str) -> int:
        """The gid of a group, or an `IdentityRefusal`."""

    def supplementary_group_names(
        self, name: str, primary_gid: int
    ) -> frozenset[str]:
        """The account's configured supplementary groups, excluding its primary."""

    def effective_ids(self) -> tuple[int, int]:
        """`(euid, egid)` of the harness process itself."""


class AccountDatabase(Protocol):
    """The operating system's account and group database, as six reads.

    `SystemIdentityLookup` is written against this rather than against `pwd`,
    `grp` and `os` directly, so its own resolution rules — exactly one record,
    and the direct answer agreeing with it — are exercised by the suite without a
    test reading a real account. `SystemAccountDatabase` is the only
    implementation that touches the host.

    Every method reports absence the way the standard library does, with
    `KeyError`. Deciding what an absence or a duplicate *means* is the lookup's
    job, not this seam's.
    """

    def account(self, name: str) -> tuple[str, int, int]:
        """`(name, uid, primary gid)` from a direct lookup."""

    def accounts(self) -> Sequence[tuple[str, int, int]]:
        """Every account record, as the database enumerates them."""

    def group(self, name: str) -> tuple[str, int]:
        """`(name, gid)` from a direct lookup."""

    def groups(self) -> Sequence[tuple[str, int]]:
        """Every group record, as the database enumerates them."""

    def group_name(self, gid: int) -> str:
        """The name a gid carries."""

    def group_ids(self, name: str, primary_gid: int) -> Sequence[int]:
        """The gids this account's initial group list would contain."""

    def effective_ids(self) -> tuple[int, int]:
        """`(euid, egid)` of the harness process itself."""


@dataclass(frozen=True, slots=True)
class SystemAccountDatabase:
    """`pwd`, `grp` and the process's own effective ids. Deliberately thin.

    It converts records to tuples and lets `KeyError` and `OSError` out
    unchanged. Nothing here decides how many records there may be or whether
    they agree — those are `SystemIdentityLookup`'s rules, so that there is one
    place to read them and one place to test them.
    """

    def account(self, name: str) -> tuple[str, int, int]:
        entry = pwd.getpwnam(name)
        return entry.pw_name, int(entry.pw_uid), int(entry.pw_gid)

    def accounts(self) -> Sequence[tuple[str, int, int]]:
        return [
            (entry.pw_name, int(entry.pw_uid), int(entry.pw_gid))
            for entry in pwd.getpwall()
        ]

    def group(self, name: str) -> tuple[str, int]:
        entry = grp.getgrnam(name)
        return entry.gr_name, int(entry.gr_gid)

    def groups(self) -> Sequence[tuple[str, int]]:
        return [(entry.gr_name, int(entry.gr_gid)) for entry in grp.getgrall()]

    def group_name(self, gid: int) -> str:
        return grp.getgrgid(gid).gr_name

    def group_ids(self, name: str, primary_gid: int) -> Sequence[int]:
        return list(os.getgrouplist(name, primary_gid))

    def effective_ids(self) -> tuple[int, int]:
        return os.geteuid(), os.getegid()


_Record = TypeVar("_Record", bound=tuple)


def _the_one_record(
    records: Sequence[_Record], *, name: str, what: str
) -> _Record:
    """Exactly one record, **counted** rather than deduplicated — EH-R6-2.

    Two records are two records even when their numbers are identical. R5 built a
    set of the values and refused only when the set had more than one member, so
    a duplicate whose uid and gid happened to match collapsed into a single
    member and was accepted. Which identity a step would assume is not a question
    this harness answers by noticing that today's answers agree.
    """
    if not records:
        raise IdentityAbsent(f"no {what} named {name!r} exists")
    if len(records) > 1:
        raise IdentityInconsistent(
            f"{name!r} has {len(records)} {what} records, so which identity a "
            "step would assume is not decidable"
        )
    return records[0]


@dataclass(frozen=True, slots=True)
class SystemIdentityLookup:
    """The default lookup: one account record, one group record, and agreement.

    Construction reads nothing — every method is called at the moment a step is
    about to run, and never at import or at plan time. That is what keeps the
    planning tier free of host reads while the credential decision stays here,
    beside the call it protects.

    The database is injected so that this class — which is where R5's collapsing
    set was — is the thing the suite exercises, rather than a fake standing in
    for it.
    """

    database: AccountDatabase = field(default_factory=SystemAccountDatabase)

    def account(self, name: str) -> tuple[int, int]:
        try:
            direct = self.database.account(name)
        except KeyError as exc:
            raise IdentityAbsent(f"no account named {name!r} exists") from exc
        record = _the_one_record(
            [entry for entry in self.database.accounts() if entry[0] == name],
            name=name,
            what="account",
        )
        if tuple(direct) != tuple(record):
            raise IdentityInconsistent(
                f"the account database's direct answer for {name!r} is not the "
                "one record it enumerates under that name"
            )
        return record[1], record[2]

    def group_id(self, name: str) -> int:
        try:
            direct = self.database.group(name)
        except KeyError as exc:
            raise IdentityAbsent(f"no group named {name!r} exists") from exc
        record = _the_one_record(
            [entry for entry in self.database.groups() if entry[0] == name],
            name=name,
            what="group",
        )
        if tuple(direct) != tuple(record):
            raise IdentityInconsistent(
                f"the group database's direct answer for {name!r} is not the one "
                "record it enumerates under that name"
            )
        return record[1]

    def supplementary_group_names(
        self, name: str, primary_gid: int
    ) -> frozenset[str]:
        """The configured supplementary groups, by name.

        A name that comes back from here is resolved again through `group_id`
        before it becomes a credential, so a reverse mapping that does not
        round-trip to exactly one named record is refused there.
        """
        try:
            gids = self.database.group_ids(name, primary_gid)
        except KeyError as exc:
            raise IdentityAbsent(f"no account named {name!r} exists") from exc
        except OSError as exc:
            raise IdentityInconsistent(
                f"the group list for {name!r} could not be resolved"
            ) from exc
        names: set[str] = set()
        for gid in gids:
            if gid == primary_gid:
                continue
            try:
                names.add(self.database.group_name(gid))
            except KeyError as exc:
                raise IdentityInconsistent(
                    f"{name!r} is in a group with no name in the group database"
                ) from exc
        return frozenset(names)

    def effective_ids(self) -> tuple[int, int]:
        return self.database.effective_ids()


def _require_identifier(value: object, what: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise IdentityInconsistent(f"{what} is not a numeric identifier")
    return int(value)


def resolve_credential(
    required: RequiredIdentity, lookup: IdentityLookup
) -> ResolvedCredential:
    """The contract, resolved to numbers, or a refusal. Nothing in between.

    Every check here happens before a process exists. There is no path through
    this function that returns a credential the contract does not describe, and
    no path that substitutes a default for something it could not resolve.
    """
    uid, gid = lookup.account(required.name)
    return _resolve(
        required,
        lookup,
        _require_identifier(uid, "the uid"),
        _require_identifier(gid, "the primary gid"),
    )


def _resolve(
    required: RequiredIdentity,
    lookup: IdentityLookup,
    uid: int,
    gid: int,
) -> ResolvedCredential:
    primary_gid = _require_identifier(
        lookup.group_id(required.primary_group), "the primary group's gid"
    )
    if primary_gid != gid:
        raise IdentityInconsistent(
            f"{required.name!r} has primary gid {gid} while the contract's "
            f"primary group {required.primary_group!r} is {primary_gid}"
        )
    if required.superuser:
        if uid != 0 or gid != 0:
            raise IdentityInconsistent(
                f"{required.name!r} is the superuser row and does not resolve to 0/0"
            )
    elif uid == 0 or gid == 0:
        raise IdentityInconsistent(
            f"{required.name!r} is not the superuser row and resolves to a "
            "superuser id, which is a malformed identity rather than a step that "
            "may run"
        )

    observed = lookup.supplementary_group_names(required.name, gid)
    if not isinstance(observed, (set, frozenset)):
        raise IdentityInconsistent("the supplementary group list is not a set")
    # Set **equality**, in both directions and unconditionally. There is no rule
    # under which an observed group the contract does not name is carried into
    # the credential, so a rule added later without a decision about its
    # membership gets this treatment rather than a pass-through — EH-R6-1.
    missing = sorted(required.supplementary - observed)
    if missing:
        raise MembershipRefused(
            f"{required.name!r} is not in {missing}, which the reviewed contract "
            "requires. A case that depends on that membership would be refused "
            "for the harness's identity rather than for the authority under test"
        )
    unexpected = sorted(observed - required.supplementary)
    if unexpected:
        raise MembershipRefused(
            f"{required.name!r} is additionally in {unexpected}, and the "
            "reviewed contract states its complete supplementary list. An "
            "unexpected membership is a failed case, not a difference to note"
        )
    effective = frozenset(required.supplementary)

    gids: list[int] = []
    for group_name in sorted(effective):
        group_gid = _require_identifier(
            lookup.group_id(group_name), f"the gid of {group_name!r}"
        )
        if not required.superuser and group_gid == 0:
            raise IdentityInconsistent(
                f"supplementary group {group_name!r} resolves to gid 0"
            )
        gids.append(group_gid)
    if len(set(gids)) != len(gids):
        raise IdentityInconsistent(
            "two of the contract's supplementary groups resolve to the same gid"
        )
    return ResolvedCredential(uid=uid, gid=gid, supplementary_gids=tuple(sorted(gids)))


@dataclass(frozen=True, slots=True)
class CommandResult:
    """What a boundary reports. Scalars and sanitized observations only."""

    exit_status: int
    timed_out: bool
    #: `capture.sanitize`'s output. Never raw text.
    observations: tuple[tuple[str, str], ...] = ()
    #: Whether the command wrote anything to standard error. Not *what*.
    stderr_present: bool = False
    #: Set when the process could not be started at all — a missing executable, a
    #: refused identity transition, an identity that does not match the reviewed
    #: contract. Always one of `LAUNCH_FAILURES`: a short, fixed classification,
    #: never the operating system's message and never an account fact.
    launch_failure: str = ""


class ProcessBoundary(Protocol):
    """The seam every test injects across.

    `step_id` is passed so a boundary can attribute a call to the reviewed step
    it came from — two steps in the plan legitimately share an argument vector
    (`getent group freedomjournal` asserts the group is *absent* before
    provisioning and asserts its *membership* after), and a boundary that could
    not tell them apart could not report which one it ran.

    `run_as` is passed through rather than composed into the argument vector:
    the harness emits no privilege transition and `sudo`, `su` and every shell
    are refused by `plan.validate_argv`. How an identity is assumed is this
    boundary's business and nothing else's.

    `catalog` is the reviewed question a `catalog_membership` reading answers —
    **R14, EH-R14-1**. The vector lists a whole PostgreSQL catalog, because the
    reviewed grammar admits no string literal to filter it with, so the two names
    the reading compares travel beside it rather than inside it. It is `None` for
    every other policy.

    `descriptors` is the **declared inherited table** of r6 §§1.3.3 and 6.3:
    the descriptors this step may use, in the order they are remapped, starting
    at descriptor 3. A step that was declared none receives none and opens no
    path to obtain one; the case program's `DIRFD` argument kind is an index
    into this table and into nothing else. **No synchronizable descriptor is
    ever in it** — `DescriptorInventory.declare_transfer` enforces that where
    the table is built, and `_transferable` enforces it again here, because a
    step that could `fsync` could make a durability claim the executor did not
    make.
    """

    def run(
        self,
        *,
        step_id: str,
        argv: Sequence[str],
        run_as: str,
        capture: CapturePolicy,
        timeout_seconds: float,
        catalog: CatalogQuestion | None = None,
        descriptors: Sequence["TransferEntry"] = (),
    ) -> CommandResult: ...


@dataclass(frozen=True, slots=True)
class SubprocessBoundary:
    """The real one. Not reachable from the planning tier, and not the default
    anywhere: the CLI constructs it only on the `--execute` path.

    The identity transition uses `subprocess`'s own `user=`, `group=` and
    `extra_groups=` parameters, all three passed on every call, from credentials
    resolved against `IDENTITY_CONTRACT` before the process is created. That is
    deliberately **not** a wrapper binary: `setpriv` or `su` in the argument
    vector would mean the reviewed vector is not the vector that runs, and the
    whole point of an argument vector is that those are the same thing.
    """

    #: Set by the CLI from `--dry-run`/`--execute`. A boundary that is not armed
    #: refuses to start anything, so an executor constructed with a real boundary
    #: by mistake still cannot run a command.
    armed: bool = False
    #: How the account database is read. Injected so the credential contract is
    #: exercised by the suite without any test reading a real account.
    lookup: IdentityLookup = field(default_factory=SystemIdentityLookup)

    def run(
        self,
        *,
        step_id: str,
        argv: Sequence[str],
        run_as: str,
        capture: CapturePolicy,
        timeout_seconds: float,
        catalog: CatalogQuestion | None = None,
        descriptors: Sequence["TransferEntry"] = (),
    ) -> CommandResult:
        if not self.armed:
            return _refusal(LAUNCH_BOUNDARY_NOT_ARMED)
        if not run_as or not run_as.strip():
            return _refusal(LAUNCH_BLANK_IDENTITY)
        if timeout_seconds <= 0:
            return _refusal(LAUNCH_NO_TIMEOUT)
        vector = list(argv)
        if not vector or not vector[0].startswith("/"):
            return _refusal(LAUNCH_NOT_ABSOLUTE)

        required = IDENTITY_CONTRACT.get(run_as)
        if required is None:
            return _refusal(LAUNCH_IDENTITY_NOT_IN_CONTRACT)

        try:
            credential = self._credential_for(required)
        except PrivilegeUnavailable:
            return _refusal(LAUNCH_ROOT_UNAVAILABLE)
        except IdentityAbsent:
            return _refusal(LAUNCH_IDENTITY_UNKNOWN)
        except MembershipRefused:
            return _refusal(LAUNCH_IDENTITY_MEMBERSHIP)
        except IdentityInconsistent:
            return _refusal(LAUNCH_IDENTITY_INCONSISTENT)

        # **r6 §§1.3.3 and 6.3.** The declared inherited table, validated here
        # and not merely passed on. Every failure refuses the launch with a
        # fixed classification, before any process exists.
        try:
            inherited = _transferable(descriptors)
        except _TransferRefused as refusal:
            return _refusal(refusal.classification)

        try:
            completed = subprocess.run(  # noqa: S603 - argv only, shell=False
                vector,
                shell=False,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=environment_for(vector[0]),
                cwd="/",
                stdin=subprocess.DEVNULL,
                check=False,
                # The descriptors the step inherits, and no others.
                # `subprocess` closes every descriptor this does not name.
                pass_fds=tuple(number for number, _index in inherited),
                # The remap into the declared order, performed in the child
                # between `fork` and `execve`. `dup2` with `inheritable=True`
                # clears `FD_CLOEXEC` on the duplicate, and it is cleared for
                # **exactly** these descriptors and no others, because every
                # other descriptor `subprocess` inherits is closed by
                # `pass_fds`.
                preexec_fn=_remap(inherited) if inherited else None,
                **credential.as_keywords(),
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                exit_status=-1, timed_out=True, launch_failure=LAUNCH_TIMEOUT
            )
        except FileNotFoundError:
            return _refusal(LAUNCH_EXECUTABLE_ABSENT)
        except PermissionError:
            # The credentials resolved, and the operating system still refused
            # the transition — an unprivileged launcher, or a restriction the
            # account database does not describe. Reported as a classification
            # rather than as the message, which would name the identity.
            return _refusal(LAUNCH_IDENTITY_REFUSED)
        except (KeyError, LookupError):
            # A credential the child could not apply. Everything this boundary
            # resolves is checked above, so reaching here means the account
            # database changed under the run; it is a stop either way.
            return _refusal(LAUNCH_IDENTITY_UNKNOWN)

        # The raw text lives exactly here and nowhere else.
        observations = sanitize(capture, completed.stdout or "", catalog=catalog)
        return CommandResult(
            exit_status=completed.returncode,
            timed_out=False,
            observations=observations,
            stderr_present=bool((completed.stderr or "").strip()),
        )

    def _credential_for(self, required: RequiredIdentity) -> ResolvedCredential:
        """Resolve the contract's row, with root's launcher precondition first.

        `run_as="root"` never means *"whatever identity launched the CLI"*. The
        launcher must already be effective UID and GID 0 — which is checked here,
        before anything is resolved — and the child's credentials are then
        constructed from the `root` row's own resolved numbers, so the vector the
        child receives is stated by the contract rather than inherited.
        """
        if required.superuser:
            euid, egid = self.lookup.effective_ids()
            if euid != 0 or egid != 0:
                raise PrivilegeUnavailable(
                    "a root step was reached from a launcher that is not "
                    "effective UID and GID 0; it will not be run as the launching "
                    "identity instead"
                )
        return resolve_credential(required, self.lookup)


class _TransferRefused(Exception):
    """A declared descriptor this boundary will not transfer."""

    def __init__(self, classification: str) -> None:
        self.classification = classification
        super().__init__(classification)


def _transferable(
    descriptors: Sequence["TransferEntry"],
) -> tuple[tuple[int, int], ...]:
    """Validate the declared table and return `(source fd, declared index)`.

    Five refusing inputs, each before any process exists:

    * an **undeclared** index — the table must start at
      `FIRST_TRANSFERRED_DESCRIPTOR` and run consecutively, so an entry claiming
      an arbitrary number is not an index into a table this run declared;
    * a **synchronizable** descriptor, refused for the reason
      `DescriptorInventory.declare_transfer` refuses it: a step that can `fsync`
      can make a durability claim the executor did not make;
    * a **closed** descriptor;
    * a descriptor that is **not a directory**, which is what every entry in
      this table is; and
    * a **duplicated** index, which would make `DIRFD` ambiguous.
    """
    from .descriptors import FIRST_TRANSFERRED_DESCRIPTOR, DescriptorMode

    resolved: list[tuple[int, int]] = []
    seen: set[int] = set()
    for offset, entry in enumerate(descriptors):
        expected = FIRST_TRANSFERRED_DESCRIPTOR + offset
        if entry.index != expected or entry.index in seen:
            raise _TransferRefused(LAUNCH_DESCRIPTOR_UNDECLARED)
        seen.add(entry.index)
        if entry.mode is not DescriptorMode.O_PATH:
            raise _TransferRefused(LAUNCH_DESCRIPTOR_SYNCHRONIZABLE)
        number = entry.number
        if number is None or number < 0:
            raise _TransferRefused(LAUNCH_DESCRIPTOR_UNDECLARED)
        try:
            status = os.fstat(number)
        except OSError:
            raise _TransferRefused(LAUNCH_DESCRIPTOR_CLOSED) from None
        if not stat.S_ISDIR(status.st_mode):
            raise _TransferRefused(LAUNCH_DESCRIPTOR_NOT_A_DIRECTORY)
        resolved.append((number, entry.index))
    return tuple(resolved)


def _remap(inherited: Sequence[tuple[int, int]]):
    """The child-side remap into the declared order, as a callable.

    It runs in the forked child before `execve`, which is the only place a
    descriptor can be moved to a number the parent may be using itself. Nothing
    else happens in it: no allocation that could deadlock, no logging, no
    import.
    """

    pairs = tuple(inherited)

    def remap() -> None:  # pragma: no cover - runs in the forked child
        for number, index in pairs:
            os.dup2(number, index, inheritable=True)

    return remap


def _refusal(classification: str) -> CommandResult:
    """A launch refusal, with the fixed classification and nothing else."""
    return CommandResult(
        exit_status=-1, timed_out=False, launch_failure=classification
    )


@dataclass(slots=True)
class RecordingBoundary:
    """A boundary that starts nothing and records what it was asked to start.

    This is what a `--dry-run` invocation uses, and it is what makes *"the
    default invocation executes nothing"* a property of the object graph rather
    than of a branch somebody has to keep taking. It is in this module, beside
    the real one, so the two are read together.
    """

    calls: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)
    #: The declared inherited table each call was handed. A dry run transfers
    #: nothing, so every entry is empty — and it is recorded rather than
    #: discarded so that a test can assert it.
    descriptors: list[tuple] = field(default_factory=list)
    #: What every call reports. A dry run has no observations to report, so a
    #: step's satisfaction is not decided by it: `ExecutingRunner` never asks a
    #: recording boundary to decide anything, because `--execute` is what admits
    #: it to the executor at all.
    exit_status: int = 0

    def run(
        self,
        *,
        step_id: str,
        argv: Sequence[str],
        run_as: str,
        capture: CapturePolicy,
        timeout_seconds: float,
        catalog: CatalogQuestion | None = None,
        descriptors: Sequence["TransferEntry"] = (),
    ) -> CommandResult:
        self.calls.append((run_as, tuple(argv)))
        self.descriptors.append(tuple(descriptors))
        return CommandResult(exit_status=self.exit_status, timed_out=False)


__all__ = [
    "AccountDatabase",
    "CommandResult",
    "DEFAULT_TIMEOUT_SECONDS",
    "IDENTITY_CONTRACT",
    "IdentityAbsent",
    "IdentityInconsistent",
    "IdentityLookup",
    "IdentityRefusal",
    "LAUNCH_BLANK_IDENTITY",
    "LAUNCH_BOUNDARY_FAILURE",
    "LAUNCH_BOUNDARY_NOT_ARMED",
    "LAUNCH_DESCRIPTOR_CLOSED",
    "LAUNCH_DESCRIPTOR_NOT_A_DIRECTORY",
    "LAUNCH_DESCRIPTOR_SYNCHRONIZABLE",
    "LAUNCH_DESCRIPTOR_UNDECLARED",
    "LAUNCH_EFFECT_REFUSED",
    "LAUNCH_EFFECT_UNAVAILABLE",
    "LAUNCH_EXECUTABLE_ABSENT",
    "LAUNCH_FAILURES",
    "LAUNCH_IDENTITY_INCONSISTENT",
    "LAUNCH_IDENTITY_MEMBERSHIP",
    "LAUNCH_IDENTITY_NOT_IN_CONTRACT",
    "LAUNCH_IDENTITY_REFUSED",
    "LAUNCH_IDENTITY_UNKNOWN",
    "LAUNCH_NOT_ABSOLUTE",
    "LAUNCH_NO_TIMEOUT",
    "LAUNCH_ROOT_UNAVAILABLE",
    "LAUNCH_TIMEOUT",
    "LAUNCH_VALIDATION_REFUSED",
    "MINIMAL_ENVIRONMENT",
    "MembershipRefused",
    "MembershipRule",
    "POSTGRES_16_BIN",
    "PrivilegeUnavailable",
    "ProcessBoundary",
    "RecordingBoundary",
    "RequiredIdentity",
    "ResolvedCredential",
    "SubprocessBoundary",
    "SystemAccountDatabase",
    "SystemIdentityLookup",
    "TIMEOUT_SECONDS",
    "environment_for",
    "resolve_credential",
    "timeout_for",
]
