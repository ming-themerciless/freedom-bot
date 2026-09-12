"""Conflict **C-5**, resolved: the four disposable names, the declared sites they
may be substituted at, and the rule that nothing else in a vector may change.

## The problem, stated as R10 left it

`capsh --uid=`, `--gid=` and `--groups=` take **numbers**. `freedomcoord`,
`freedomsheet`, `fbprobe` and `freedomjournal` do not exist until Band 2 creates
them on the disposable host, so the numbers are not knowable when the plan is
written, and a plan carrying numbers nobody has verified is worse than one
carrying none. §2.13.5c already says the harness resolves them *"with
`getpwnam`/`getgrnam` at run time"*; what it did not have was a reviewed rule for
doing that inside the executor.

## The rule

The reviewed vector carries the **symbolic** form — `--uid=freedomsheet`,
`--groups=freedomsheet,freedomjournal` — so the manifest pins names rather than
numbers, and a reviewer reads which identity a step assumes instead of an integer
whose meaning depends on a host. Beside it the step declares its
**`BindingSite`s**: for each, the exact argument index, the exact prefix, the kind
of identifier and the exact names. Substitution is then a **positional** operation
over declared sites, not a search-and-replace over a vector:

* a site whose argument is not exactly `prefix + ",".join(names)` is refused, so
  the declaration and the vector cannot drift;
* a name outside `LATE_BOUND_NAMES` is refused — the four this run creates, and
  no fifth. `root`, `postgres`, `discordbot` and `freedomweb` are **not** late
  bound: they are existing host identities the run neither creates nor names
  numerically, and admitting them here would let a vector be rewritten around an
  account the harness does not own;
* the lookup must return **exactly one** result. That is not re-implemented here:
  the injected `IdentityLookup` is `boundary.SystemIdentityLookup`, which already
  refuses a duplicated record, refuses a direct answer that disagrees with the
  single enumerated one, and refuses an absent name — and a test injects a fake
  in its place rather than reading this machine's accounts;
* a resolved value that is not a plain positive integer below `MAX_IDENTIFIER` is
  refused: a `bool`, a float, a negative number, zero (which is `root`, and no
  late-bound name may resolve to it) and anything large enough to have wrapped;
  and
* after substitution the whole vector is compared with the symbolic one
  element by element, and **any difference outside a declared site is refused**.
  That is the check that makes "substitute only the reviewed uid/gid fields" a
  property rather than an intention.

The executor then revalidates the complete final vector — including the Option-B
interpreter prefix and the case-program grammar of `case_runtime` — immediately
before process creation, so the bound vector is subject to every check the
symbolic one was.

## What this module does not do

It performs no lookup. `resolve_uid` and `resolve_gid` are parameters, so nothing
in the planning tier consults the host's account database, dry-run generation
consults nothing at all, and every branch below is exercised by the suite with
injected results.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence

from .errors import PlanRefused

#: The four names this run creates in the disposable environment, and the only
#: names any binding site may mention. Three are accounts whose primary group
#: carries the same name; the fourth is the shared group §2.12.2 provisions.
LATE_BOUND_NAMES = frozenset({"freedomcoord", "freedomsheet", "fbprobe", "freedomjournal"})

#: The upper bound a resolved identifier must stay under. `uid_t` and `gid_t` are
#: 32-bit unsigned, and a value at or above this is either a wrapped negative
#: number or the `(uid_t) -1` sentinel, neither of which is an identity.
MAX_IDENTIFIER = 2**31 - 1


class BindingRefused(PlanRefused):
    """A late binding could not be performed as the reviewed plan declares it."""


class BindingKind(str, Enum):
    """What one site substitutes. Three kinds, each tied to one prefix."""

    #: A single numeric uid, from `getpwnam`.
    UID = "uid"
    #: A single numeric gid, from `getgrnam`.
    GID = "gid"
    #: A comma-separated list of numeric gids, in the declared order.
    GID_LIST = "gid_list"


#: The one prefix each kind may carry. A site whose prefix does not match its
#: kind is refused, so `--uid=` cannot be given a group's number.
PREFIX_FOR_KIND = {
    BindingKind.UID: "--uid=",
    BindingKind.GID: "--gid=",
    BindingKind.GID_LIST: "--groups=",
}

#: Every prefix a binding site may carry, for a reader who wants the set rather
#: than the mapping.
PERMITTED_BINDING_PREFIXES = frozenset(PREFIX_FOR_KIND.values())


@dataclass(frozen=True, slots=True)
class BindingSite:
    """One declared substitution: where, what prefix, which kind, which names."""

    argument_index: int
    kind: BindingKind
    names: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.kind, BindingKind):
            raise BindingRefused("A binding site names one of the closed kinds.")
        if (
            not isinstance(self.argument_index, int)
            or isinstance(self.argument_index, bool)
            or self.argument_index < 1
        ):
            raise BindingRefused(
                "A binding site's argument index is a positive position in the "
                "vector. Index 0 is the executable, which is never substituted."
            )
        if not self.names:
            raise BindingRefused("A binding site names at least one identity.")
        unknown = sorted(set(self.names) - LATE_BOUND_NAMES)
        if unknown:
            raise BindingRefused(
                f"A binding site names {unknown}, which this run does not create. "
                f"Late binding reaches exactly {sorted(LATE_BOUND_NAMES)} — an "
                "existing host identity is never rewritten into a vector."
            )
        if len(set(self.names)) != len(self.names):
            raise BindingRefused(
                f"A binding site names {list(self.names)}, which repeats a name. "
                "A duplicated member is a group list nobody wrote."
            )
        if self.kind is not BindingKind.GID_LIST and len(self.names) != 1:
            raise BindingRefused(
                f"A {self.kind.value} site names exactly one identity; this one "
                f"names {list(self.names)}."
            )

    @property
    def prefix(self) -> str:
        return PREFIX_FOR_KIND[self.kind]

    @property
    def symbolic_argument(self) -> str:
        """The argument the reviewed vector carries at this index."""
        return self.prefix + ",".join(self.names)


def validate_sites(
    argv: Sequence[str], sites: Sequence[BindingSite]
) -> None:
    """Every site is in range, unique, and matches the vector it annotates.

    Called when a step is constructed, so a declaration that disagrees with its
    own argument vector is a `PlanRefused` at plan time rather than a surprise
    immediately before a privileged process is created.
    """
    seen: set[int] = set()
    for site in sites:
        if site.argument_index >= len(argv):
            raise BindingRefused(
                f"A binding site names argument {site.argument_index}, and the "
                f"vector has {len(argv)} arguments."
            )
        if site.argument_index in seen:
            raise BindingRefused(
                f"Argument {site.argument_index} is declared as a binding site "
                "twice. One site, one substitution."
            )
        seen.add(site.argument_index)
        actual = argv[site.argument_index]
        if actual != site.symbolic_argument:
            raise BindingRefused(
                f"Argument {site.argument_index} is {actual!r} and its declared "
                f"binding site describes {site.symbolic_argument!r}. The "
                "declaration and the vector state the same substitution, or "
                "neither was reviewed."
            )


def _identifier(value: object, *, name: str, what: str) -> int:
    """A resolved number, or a refusal. Nothing in between and no default."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise BindingRefused(
            f"The {what} resolved for {name!r} is not a plain integer, so it is "
            "not an identifier this vector may carry."
        )
    if value <= 0:
        raise BindingRefused(
            f"The {what} resolved for {name!r} is {value}, which is not a usable "
            "identity: zero is the superuser and a negative value is malformed. "
            "No name this run creates may resolve to either."
        )
    if value > MAX_IDENTIFIER:
        raise BindingRefused(
            f"The {what} resolved for {name!r} is {value}, beyond "
            f"{MAX_IDENTIFIER}. A value that large is a wrapped negative number "
            "or the (uid_t) -1 sentinel rather than an account."
        )
    return value


def bind_arguments(
    argv: Sequence[str],
    sites: Sequence[BindingSite],
    *,
    resolve_uid: Callable[[str], object],
    resolve_gid: Callable[[str], object],
) -> tuple[str, ...]:
    """The final vector, with exactly the declared sites substituted.

    The lookups happen here, immediately before the caller creates the process,
    and their results are validated before any of them reaches a vector: a
    partially substituted vector is never constructed, because a refusal on the
    third site raises before the first is applied.
    """
    validate_sites(argv, sites)

    replacements: dict[int, str] = {}
    for site in sites:
        numbers: list[int] = []
        for name in site.names:
            if site.kind is BindingKind.UID:
                numbers.append(_identifier(resolve_uid(name), name=name, what="uid"))
            else:
                numbers.append(_identifier(resolve_gid(name), name=name, what="gid"))
        if len(set(numbers)) != len(numbers):
            raise BindingRefused(
                f"The names {list(site.names)} resolved to the same identifier "
                "more than once, so the group list this vector would carry names "
                "fewer identities than the reviewed one."
            )
        replacements[site.argument_index] = site.prefix + ",".join(
            str(number) for number in numbers
        )

    bound = tuple(
        replacements.get(index, argument) for index, argument in enumerate(argv)
    )
    _refuse_change_outside_sites(tuple(argv), bound, replacements)
    return bound


def _refuse_change_outside_sites(
    symbolic: tuple[str, ...],
    bound: tuple[str, ...],
    replacements: dict[int, str],
) -> None:
    """The bound vector differs from the reviewed one **only** at declared sites.

    Computed by comparison rather than asserted by construction: the substitution
    above builds the vector, and this reads the result back, so a future edit that
    rewrote something else would be caught by the check rather than by the reader
    of the code that did it.
    """
    if len(symbolic) != len(bound):
        raise BindingRefused(
            "Late binding changed the length of the argument vector. A "
            "substitution replaces an argument; it never adds or removes one."
        )
    for index, (before, after) in enumerate(zip(symbolic, bound)):
        if before == after:
            continue
        if index not in replacements:
            raise BindingRefused(
                f"Argument {index} changed from {before!r} to {after!r} and is "
                "not a declared binding site. Only the reviewed uid and gid "
                "fields are substituted."
            )


__all__ = [
    "BindingKind",
    "BindingRefused",
    "BindingSite",
    "LATE_BOUND_NAMES",
    "MAX_IDENTIFIER",
    "PERMITTED_BINDING_PREFIXES",
    "PREFIX_FOR_KIND",
    "bind_arguments",
    "validate_sites",
]
