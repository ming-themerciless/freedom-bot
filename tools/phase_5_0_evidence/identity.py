"""Check **C-4** / `JNL-52`: the canonical membership table, and the access each
identity actually has.

§2.12.2 is the **single place a membership is stated** — that is remediation
R11-B, and security-review finding **P5.0-SR2** is what happens when it is not.
This module encodes that table once, compares an observed `getent group` / `id`
against it, and refuses to treat an unexpected member as an incidental
difference: *"an unexpected member is a **failed** `JNL-52` case"*.

The table has two halves and they are two **different relations**, which is
finding **EH-R8-1**: `CANONICAL_ACCOUNTS` states each account's primary group and
its complete supplementary set, observed through `id`; `CANONICAL_GROUPS` states
each group's **explicit** member list, observed through the fourth field of
`getent group`. A primary group is not an explicit membership, so it appears in
the first and never in the second. Finding **EH-R8-2** is the same distinction
applied to the rest of the table: the four rows R8 left alone are corrected here,
and the inverse row the identity half already implied — `users`: `foundry` — is
added, so the two halves now describe exactly one relation between them.

The second half is `JNL-52`'s access matrix, and its shape is the one this whole
harness repeats: **a denial whose cause could be a path search is not evidence of
a permission.** Every negative case therefore carries the positive control the
plan names for it — cases 5 and 7 are the `discordbot` and `freedomweb` traverse
controls that make cases 6 and 8 attributable to `…/journal`'s mode rather than
to a parent directory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .errors import ObservationRefused
from .records import (
    CaseRole,
    CleanupState,
    EvidenceRecord,
    Outcome,
    Status,
)

BAND = "identity"


@dataclass(frozen=True, slots=True)
class CanonicalAccount:
    """One row of §2.12.2's identity table. `supplementary` is **complete**."""

    name: str
    primary_group: str
    supplementary: frozenset[str]
    shell: str
    provisioned_by_package: bool


@dataclass(frozen=True, slots=True)
class CanonicalGroup:
    """One row of §2.12.2's group inverse. `members` is **exact and explicit**.

    *Explicit* is the whole of finding **EH-R8-1**, and it is stated here rather
    than left to be inferred from the row that happens to be read first. This
    field models the **fourth field of `getent group`** — the group's explicit
    member list — and `ObservedGroup.members` is that field, split. An account
    whose *primary* group this is does **not** appear there: primary membership
    lives in the account's passwd record, is stated in `CanonicalAccount.
    primary_group`, and is checked by `classify_account_identity` against `id`.

    So the two halves of §2.12.2 are two different relations over one ruled fact
    set, not one relation written twice:

    * the identity table states, per account, its primary group and its
      **complete** supplementary set; and
    * this inverse states, per group, exactly who is listed in it explicitly —
      which is the supplementary side, and nothing else.

    Writing an account into the inverse row of its own primary group turns the
    ruled fact *"`postgres`'s primary group is `postgres`"* into the different,
    unruled fact *"the `postgres` group explicitly lists `postgres`"*, and a
    correctly configured host then **fails** its `JNL-52` case. That is what R7
    did, what R8 removed from the `postgres` row, and what **EH-R8-2** removes
    from the four rows R8 reported and left standing. No row states it now, and
    `_the_two_halves_of_the_table_agree` refuses at import if one is written
    back.
    """

    name: str
    members: frozenset[str]
    grants: str


#: §2.12.2, transcribed once. Nothing else in this package states a membership,
#: and `tests/phase_5_0_evidence/test_identity.py` asserts that E1 … E8's group
#: lists in `capability.py` are drawn from here.
CANONICAL_ACCOUNTS: Mapping[str, CanonicalAccount] = {
    account.name: account
    for account in (
        CanonicalAccount("freedomcoord", "freedomcoord", frozenset({"freedomjournal"}),
                         "/usr/sbin/nologin", True),
        CanonicalAccount("freedomsheet", "freedomsheet", frozenset({"freedomjournal"}),
                         "/usr/sbin/nologin", True),
        CanonicalAccount("discordbot", "discordbot", frozenset(), "/bin/bash", False),
        CanonicalAccount("freedomweb", "freedomweb", frozenset({"discordbot"}),
                         "/usr/sbin/nologin", False),
        CanonicalAccount("foundry", "foundry", frozenset({"sudo", "users"}),
                         "/bin/bash", False),
        # Ruled by Peter Duscha on 2026-09-06 as §2.12.2's R7 amendment, change-log
        # C-P5.0-AE, closing the blocked half of EH-R6-1. An **existing host
        # identity**: this package neither creates it nor changes its memberships,
        # which is what `provisioned_by_package=False` records. The set is exactly
        # `ssl-cert`, and it is exact in both directions like every other row, so a
        # host that differs is a refusal rather than a pass-through. The shell is
        # `not asserted`: the ruling covered the membership alone, nothing in this
        # package reads the column, and inventing a plausible value for it would be
        # the membership-stated-outside-the-table defect in another column.
        CanonicalAccount("postgres", "postgres", frozenset({"ssl-cert"}),
                         "not asserted", False),
        CanonicalAccount("fbprobe", "fbprobe", frozenset(), "/usr/sbin/nologin", True),
    )
}

#: The `getent group` fourth field, per group. **Every row states explicit
#: members only** — the R8 definition of the relation, applied to the whole table
#: by the R9 ruling that closes **EH-R8-2** (change-log **C-P5.0-AF**, package
#: plan §2.12.2). No account's primary group is written here, and the four rows
#: that used to do so are corrected below in place, with the row `users:
#: foundry` added because the identity half already states that supplementary
#: membership and a membership stated in one half only is stop condition **10p**.
#:
#: **This changed no account's memberships.** Primary groups and complete
#: supplementary sets in `CANONICAL_ACCOUNTS` are exactly as ruled; what changed
#: is how the same facts are represented on this side of the table.
CANONICAL_GROUPS: Mapping[str, CanonicalGroup] = {
    group.name: group
    for group in (
        CanonicalGroup("freedomjournal", frozenset({"freedomcoord", "freedomsheet"}),
                       "r-x on …/journal and r-- on the seal; no w anywhere"),
        # `freedomcoord`, `freedomsheet` and `fbprobe` are each some account's
        # *primary* group and nobody's supplementary one, so `useradd` adds no
        # explicit member and `getent group` reports an empty fourth field. Each
        # row is **kept** with the empty set rather than deleted, for the reason
        # the `postgres` row is: the empty list is a claim worth failing on, and
        # a deleted row would make its `JNL-52-GROUP-*` case unclassifiable
        # instead of failed.
        CanonicalGroup("freedomcoord", frozenset(),
                       "r-x on …/archive and r-- on its 0440 files"),
        CanonicalGroup("freedomsheet", frozenset(),
                       "nothing by itself; the writer's access is ownership"),
        # `freedomweb` alone: that is the one real supplementary membership the
        # identity half states into this group. `discordbot`'s own account is
        # not an explicit member of its own primary group.
        CanonicalGroup("discordbot", frozenset({"freedomweb"}),
                       "group write on the repository worktree — observation H-1"),
        CanonicalGroup("sudo", frozenset({"foundry"}),
                       "the two Cmnd_Alias entries, each with a fixed absolute path"),
        # Added by the R9 ruling. `foundry`'s identity row has named `users` as a
        # supplementary group throughout, and the inverse carried no row for it —
        # a membership stated half-way, which is the P5.0-SR2 shape. The row
        # grants nothing new: it states the relation that was already
        # authoritative on the identity side.
        CanonicalGroup("users", frozenset({"foundry"}),
                       "the existing supplementary membership the foundry "
                       "identity row already states; no Package 5.0 filesystem, "
                       "database or identity-transition authority"),
        CanonicalGroup("fbprobe", frozenset(),
                       "nothing; that is what makes JNL-50 case 8 attributable"),
        # The R7 amendment's two inverse rows, corrected by **EH-R8-1**.
        #
        # `postgres` is the account's **primary** group, so its explicit member
        # list — the fourth field of `getent group postgres` — is empty. R7 wrote
        # `{"postgres"}` here, which asserted that the account is listed in its
        # own primary group explicitly; on a correctly configured host it is not,
        # and `JNL-52-GROUP-postgres` would have failed for a host that matches
        # the ruling exactly. The ruled facts are unchanged: primary group
        # `postgres`, supplementary set exactly `ssl-cert`. The primary half is
        # asserted against `id` by `classify_account_identity`, which is where a
        # primary group is observable at all.
        #
        # The row is kept rather than dropped because the empty set is a claim
        # worth failing on: a host that adds an explicit member to `postgres`
        # — an account that would then hold the cluster's data directory through
        # a group — is a finding, and dropping the row would make that case
        # unclassifiable instead. Emptiness is not a new ruling: §2.12.2's
        # identity half is complete, and no identity row names `postgres` as a
        # supplementary group, so the explicit member set the controlled table
        # implies is exactly the empty one.
        CanonicalGroup("postgres", frozenset(),
                       "ownership of the cluster's data directory and of "
                       "/var/run/postgresql — observation H-3"),
        # `ssl-cert` is the supplementary half, so it does list the account
        # explicitly, exactly once. A missing or unexpected member here is still
        # a refusal before any process is created.
        CanonicalGroup("ssl-cert", frozenset({"postgres"}),
                       "read of the server's TLS private key; nothing in this "
                       "package's hierarchy and no database privilege"),
    )
}


def _the_two_halves_of_the_table_agree() -> None:
    """§2.12.2's two halves state exactly one relation between them.

    A supplementary membership is stated **twice** on purpose — once per account
    in `CANONICAL_ACCOUNTS.supplementary`, once per group in
    `CANONICAL_GROUPS.members` — and a membership stated in one half only is
    stated half-way: stop condition **10p**, and the shape of security-review
    finding **P5.0-SR2**. The check runs while this module is imported rather
    than in a comparison somebody has to remember to run, so the two halves
    cannot be edited apart: the import fails closed instead, and every consumer
    fails with it.

    **The relation is the supplementary one, and only that — findings EH-R8-1
    and EH-R8-2.** The inverse models the explicit `getent group` member list
    (see `CanonicalGroup`), and an account is not an explicit member of its own
    primary group. A primary group is verified where a host actually reports it:
    `CanonicalAccount.primary_group` against `id`, in
    `classify_account_identity`.

    Three properties are enforced over the **whole** table, not one ruled row:

    1. no account's primary group is also one of its supplementary groups, so
       the two columns of the identity half cannot claim the same membership in
       two different senses;
    2. every supplementary group an identity row names has an inverse row, and
       that row lists the account; and
    3. every explicit member of an inverse row is an account this table covers,
       is **not** the account whose primary group that row is, and names the
       group as supplementary.

    Property 3 is what makes R7's representation an import failure rather than a
    silent regression, and what keeps the four rows EH-R8-2 corrected from being
    written back: putting an account into its own primary group's row now
    refuses by name.
    """
    for account in CANONICAL_ACCOUNTS.values():
        if account.primary_group in account.supplementary:
            raise ObservationRefused(
                f"§2.12.2 gives {account.name!r} the primary group "
                f"{account.primary_group!r} and also lists it as supplementary. "
                "A primary membership is stated in the primary-group column and "
                "nowhere else — findings EH-R8-1 and EH-R8-2."
            )
        for group_name in sorted(account.supplementary):
            group = CANONICAL_GROUPS.get(group_name)
            if group is None:
                raise ObservationRefused(
                    f"§2.12.2 gives {account.name!r} the supplementary group "
                    f"{group_name!r}, which has no row in the group-to-members "
                    "inverse. A membership stated in one table and not the other "
                    "is stop condition 10p."
                )
            if account.name not in group.members:
                raise ObservationRefused(
                    f"§2.12.2's inverse row for {group_name!r} does not list "
                    f"{account.name!r}, which the identity table puts in it. The "
                    "two halves of one membership must agree."
                )

    for group in CANONICAL_GROUPS.values():
        for member in sorted(group.members):
            account = CANONICAL_ACCOUNTS.get(member)
            if account is None:
                raise ObservationRefused(
                    f"§2.12.2's inverse row for {group.name!r} lists {member!r}, "
                    "which is not an account in the identity half. An explicit "
                    "member is drawn from the controlled identity table and never "
                    "inferred from a host."
                )
            if account.primary_group == group.name:
                raise ObservationRefused(
                    f"§2.12.2's inverse row for {group.name!r} lists {member!r}, "
                    f"whose *primary* group it is. The inverse is the explicit "
                    "`getent group` member relation, and a primary group is not "
                    "an explicit membership — findings EH-R8-1 and EH-R8-2."
                )
            if group.name not in account.supplementary:
                raise ObservationRefused(
                    f"§2.12.2's inverse lists {member!r} as an explicit member of "
                    f"{group.name!r}, which the identity row does not give it as a "
                    "supplementary group. The two halves of one membership must "
                    "agree."
                )


_the_two_halves_of_the_table_agree()


@dataclass(frozen=True, slots=True)
class ObservedGroup:
    """What `getent group <name>` reported. `members` is the fourth field, split."""

    name: str
    gid: int
    members: frozenset[str]


@dataclass(frozen=True, slots=True)
class ObservedAccount:
    """What `id <name>` reported."""

    name: str
    uid: int
    gid: int
    primary_group: str
    supplementary: frozenset[str]


def group_case_id(name: str) -> str:
    """The case id for a group's membership assertion."""
    return f"JNL-52-GROUP-{name}"


def account_case_id(name: str) -> str:
    """The case id for an account's identity assertion."""
    return f"JNL-52-ID-{name}"


#: The complete set of `JNL-52` membership case ids, derived from §2.12.2's own
#: tables. `membership_matrix_holds()` reads this rather than testing case ids for
#: a name prefix: a prefix is a convention, and a convention is not a contract.
MEMBERSHIP_CASE_IDS: frozenset[str] = frozenset(
    [group_case_id(name) for name in CANONICAL_GROUPS]
    + [account_case_id(name) for name in CANONICAL_ACCOUNTS]
)


def classify_group_membership(observed: ObservedGroup) -> EvidenceRecord:
    """`JNL-52`'s standing precondition: `getent group` lists **exactly** §2.12.2.

    An unexpected member fails the case. The comparison is a set equality rather
    than a containment, which is the whole of the correction: revision 11 asserted
    that `freedomcoord` was *"in no group any service identity holds"* while its
    own §2.13.3 put both in `freedomjournal`, and a containment check would have
    agreed with the false sentence.
    """
    canonical = CANONICAL_GROUPS.get(observed.name)
    if canonical is None:
        raise ObservationRefused(
            f"Group {observed.name!r} is not in §2.12.2. A group this harness has "
            "no canonical row for cannot be compared with one."
        )
    expected = Outcome.read(_render_members(canonical.members))
    actual = Outcome.read(_render_members(observed.members))
    unexpected = sorted(observed.members - canonical.members)
    missing = sorted(canonical.members - observed.members)
    return EvidenceRecord.for_case(
        case_id=group_case_id(observed.name),
        band=BAND,
        target_identity=observed.name,
        operation=f"getent group {observed.name}",
        preconditions=("§2.12.2 is the canonical membership table",),
        expected=expected,
        observed=actual,
        case_role=CaseRole.STANDALONE,
        detail={
            "gid": observed.gid,
            "unexpected_members": ",".join(unexpected),
            "missing_members": ",".join(missing),
            "grants": canonical.grants,
        },
    )


def classify_account_identity(observed: ObservedAccount) -> EvidenceRecord:
    """`id <name>` against §2.12.2's complete supplementary list.

    *Complete* means exhaustive: an identity whose supplementary list is `—` is
    asserted to be in **no** supplementary group, and this fails the case rather
    than noting it if `id` reports one.
    """
    canonical = CANONICAL_ACCOUNTS.get(observed.name)
    if canonical is None:
        raise ObservationRefused(
            f"Account {observed.name!r} is not in §2.12.2."
        )
    expected = Outcome.read(
        f"{canonical.primary_group}+{_render_members(canonical.supplementary)}"
    )
    actual = Outcome.read(
        f"{observed.primary_group}+{_render_members(observed.supplementary)}"
    )
    return EvidenceRecord.for_case(
        case_id=account_case_id(observed.name),
        band=BAND,
        target_identity=observed.name,
        operation=f"id {observed.name}",
        preconditions=("§2.12.2 is the canonical membership table",),
        expected=expected,
        observed=actual,
        case_role=CaseRole.STANDALONE,
        detail={
            "uid": observed.uid,
            "gid": observed.gid,
            "unexpected_supplementary": ",".join(
                sorted(observed.supplementary - canonical.supplementary)
            ),
            "provisioned_by_package": canonical.provisioned_by_package,
        },
    )


@dataclass(frozen=True, slots=True)
class AccessCase:
    """One `JNL-52` access assertion.

    `control_case_id` names the positive control, and the classifier will not
    interpret this case's result without that control having passed — which is why
    cases 5 and 7 of `JNL-52` exist at all.

    `role` says which side of that relationship this case is on. It is declared
    and validated rather than inferred from the reference alone, because the two
    facts a reviewer needs are *"this case needs a control"* and *"this case may
    be used as one"*, and only the first is implied by naming a reference.
    """

    case_id: str
    identity: str
    path: str
    operation: str
    expected: Outcome
    control_case_id: str | None = None
    namei_resolved: bool | None = None
    role: CaseRole = CaseRole.STANDALONE

    def __post_init__(self) -> None:
        names_control = self.control_case_id is not None
        if (self.role is CaseRole.DEPENDENT) != names_control:
            raise ObservationRefused(
                f"Access case {self.case_id!r} declares role {self.role.value!r} "
                f"and {'names' if names_control else 'names no'} control. A "
                "dependent case names exactly one; a control or a read names none."
            )


def classify_access(
    case: AccessCase,
    observed: Outcome | None,
    *,
    control: EvidenceRecord | None = None,
) -> EvidenceRecord:
    """One access case, interpreted only beside its control's **record**.

    The control's status is read off that record (EH-R2-1), so a denial cannot be
    made attributable by a caller stating that the traverse control passed.
    """
    if case.control_case_id is not None and control is None:
        raise ObservationRefused(
            f"Access case {case.case_id!r} names control {case.control_case_id!r}; "
            "that control's record must be supplied, because a denial beside a "
            "control that did not pass attributes nothing."
        )
    detail: dict[str, str | int | bool | None] = {"path": case.path}
    if case.namei_resolved is not None:
        detail["namei_every_component_resolved"] = case.namei_resolved
    return EvidenceRecord.for_case(
        case_id=case.case_id,
        band=BAND,
        target_identity=case.identity,
        operation=case.operation,
        preconditions=(
            "the membership matrix passed for this identity",
            "namei -l resolved the path so a denial is not a path search",
        ),
        expected=case.expected,
        observed=observed,
        case_role=case.role,
        positive_control_case_id=case.control_case_id,
        positive_control=control,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail=detail,
    )


def _render_members(members: frozenset[str]) -> str:
    return ",".join(sorted(members)) if members else "—"


def membership_matrix_holds(records: Sequence[EvidenceRecord]) -> bool:
    """Every membership case passed. Used as the precondition for the access
    cases, because `JNL-52` asserts the table itself before every access."""
    membership = [r for r in records if r.case_id in MEMBERSHIP_CASE_IDS]
    return bool(membership) and all(r.status is Status.PASSED for r in membership)


__all__ = [
    "BAND",
    "MEMBERSHIP_CASE_IDS",
    "AccessCase",
    "CANONICAL_ACCOUNTS",
    "CANONICAL_GROUPS",
    "CanonicalAccount",
    "CanonicalGroup",
    "ObservedAccount",
    "ObservedGroup",
    "classify_access",
    "classify_account_identity",
    "classify_group_membership",
    "account_case_id",
    "group_case_id",
    "membership_matrix_holds",
]
