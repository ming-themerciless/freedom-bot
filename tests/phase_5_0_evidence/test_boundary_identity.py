"""EH-R5-1, EH-R6-1 and EH-R6-2: the credentials the real boundary constructs.

**No test in this file starts a process, and none reads the host's account or
group database.** The boundary module's process starter is replaced with a
recorder, and its `IdentityLookup` is replaced with a table written here — so
every branch of the credential contract is exercised on any machine, with no
account, no group and no privilege.

Two properties are what make that safe to trust, and `test_no_execution.py`
checks both of them about this file: it never imports the process starter, and
it names it only as the string it hands to `monkeypatch.setattr`.

The assertions are about the **keyword arguments actually passed**, because that
is exactly what the finding was about: a boundary that passes `user=` alone gets
its primary group from the launching process and, with `extra_groups=[]`, throws
away the `freedomjournal` membership the positive traversal and isolation cases
depend on. A fake `ProcessBoundary` cannot show any of that.

The last two sections are R6's, and the second of them injects a fake
**account database** rather than a fake lookup, because EH-R6-2's defect is
inside `SystemIdentityLookup` itself: a fake standing in for that class would
prove nothing about it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest

from tools.phase_5_0_evidence.capture import CapturePolicy
from tools.phase_5_0_evidence.execution import boundary as boundary_module
from tools.phase_5_0_evidence.execution.boundary import (
    IDENTITY_CONTRACT,
    LAUNCH_BLANK_IDENTITY,
    LAUNCH_BOUNDARY_NOT_ARMED,
    LAUNCH_EXECUTABLE_ABSENT,
    LAUNCH_FAILURES,
    LAUNCH_IDENTITY_INCONSISTENT,
    LAUNCH_IDENTITY_MEMBERSHIP,
    LAUNCH_IDENTITY_NOT_IN_CONTRACT,
    LAUNCH_IDENTITY_REFUSED,
    LAUNCH_IDENTITY_UNKNOWN,
    LAUNCH_NOT_ABSOLUTE,
    LAUNCH_NO_TIMEOUT,
    LAUNCH_ROOT_UNAVAILABLE,
    LAUNCH_TIMEOUT,
    IdentityAbsent,
    IdentityInconsistent,
    IdentityLookup,
    MembershipRule,
    RequiredIdentity,
    SubprocessBoundary,
    SystemAccountDatabase,
    SystemIdentityLookup,
    resolve_credential,
)
from tools.phase_5_0_evidence.execution.executor import PERMITTED_RUN_AS
from tools.phase_5_0_evidence.identity import CANONICAL_ACCOUNTS, CANONICAL_GROUPS
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

#: A synthetic account database. Every id is invented for this file; none of it
#: is read from a host, and none of it needs to exist anywhere.
ACCOUNTS = {
    "root": (0, 0),
    "postgres": (114, 120),
    "freedomcoord": (4001, 4001),
    "freedomsheet": (4002, 4002),
    "fbprobe": (4003, 4003),
    "discordbot": (1001, 1001),
    "freedomweb": (1002, 1002),
}
GROUPS = {
    "root": 0,
    "postgres": 120,
    "ssl-cert": 121,
    "freedomcoord": 4001,
    "freedomsheet": 4002,
    "fbprobe": 4003,
    "freedomjournal": 4100,
    "discordbot": 1001,
    "freedomweb": 1002,
}
#: The supplementary memberships §2.12.2 states, as a host would report them.
MEMBERSHIPS = {
    "root": frozenset(),
    "postgres": frozenset({"ssl-cert"}),
    "freedomcoord": frozenset({"freedomjournal"}),
    "freedomsheet": frozenset({"freedomjournal"}),
    "fbprobe": frozenset(),
    "discordbot": frozenset(),
    "freedomweb": frozenset({"discordbot"}),
}


@dataclass
class FakeLookup:
    """An account database written here, and the process's own effective ids.

    `caller_supplementary` is the launching process's own group list. Nothing
    reads it — that is the point of the field: a test can change it and assert
    that the child's credentials do not move.
    """

    accounts: dict[str, tuple[int, int]] = field(
        default_factory=lambda: dict(ACCOUNTS)
    )
    groups: dict[str, int] = field(default_factory=lambda: dict(GROUPS))
    memberships: dict[str, frozenset[str]] = field(
        default_factory=lambda: dict(MEMBERSHIPS)
    )
    effective: tuple[int, int] = (0, 0)
    caller_supplementary: frozenset[str] = frozenset()
    #: name -> exception, for the inconsistency cases.
    account_failures: dict[str, Exception] = field(default_factory=dict)
    group_failures: dict[str, Exception] = field(default_factory=dict)

    def account(self, name: str) -> tuple[int, int]:
        if name in self.account_failures:
            raise self.account_failures[name]
        if name not in self.accounts:
            raise IdentityAbsent(f"no account named {name!r} exists")
        return self.accounts[name]

    def group_id(self, name: str) -> int:
        if name in self.group_failures:
            raise self.group_failures[name]
        if name not in self.groups:
            raise IdentityAbsent(f"no group named {name!r} exists")
        return self.groups[name]

    def supplementary_group_names(self, name: str, primary_gid: int) -> frozenset[str]:
        return self.memberships.get(name, frozenset())

    def effective_ids(self) -> tuple[int, int]:
        return self.effective


@dataclass
class Recorder:
    """Stands in for the boundary module's process starter. Starts nothing."""

    calls: list[dict[str, object]] = field(default_factory=list)
    positional: list[tuple[object, ...]] = field(default_factory=list)
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""
    raises: BaseException | None = None

    DEVNULL = "a stand-in for the null device"

    class TimeoutExpired(Exception):
        """The stand-in's timeout, raised in place of the real one."""

    def run(self, *args: object, **keywords: object) -> SimpleNamespace:
        self.positional.append(args)
        self.calls.append(dict(keywords))
        if self.raises is not None:
            raise self.raises
        return SimpleNamespace(
            returncode=self.returncode, stdout=self.stdout, stderr=self.stderr
        )


@pytest.fixture()
def recorder(monkeypatch: pytest.MonkeyPatch) -> Recorder:
    """Replace the boundary module's process starter for the whole test.

    The name is passed as a string and never imported here, so this file has no
    path to a real process even if the replacement failed.
    """
    stand_in = Recorder()
    monkeypatch.setattr(boundary_module, "subprocess", stand_in)
    return stand_in


def start(
    run_as: str,
    lookup: IdentityLookup,
    *,
    argv: tuple[str, ...] = ("/usr/bin/id",),
    timeout_seconds: float = 30.0,
) -> boundary_module.CommandResult:
    return SubprocessBoundary(armed=True, lookup=lookup).run(
        step_id="S-01",
        argv=argv,
        run_as=run_as,
        capture=CapturePolicy.EXIT_STATUS_ONLY,
        timeout_seconds=timeout_seconds,
    )


# ---------------------------------------------------------------------------
# The contract itself
# ---------------------------------------------------------------------------


def test_the_contract_covers_exactly_the_identities_a_step_may_name() -> None:
    """One closed set, in one place. The executor's is derived from it."""
    assert PERMITTED_RUN_AS == frozenset(IDENTITY_CONTRACT)
    assert "" not in IDENTITY_CONTRACT


@pytest.mark.parametrize(
    "name", ["freedomcoord", "freedomsheet", "fbprobe", "discordbot", "freedomweb"]
)
def test_every_membership_comes_from_the_canonical_table_and_not_from_here(
    name: str,
) -> None:
    """§2.12.2 is the single place a membership is stated — remediation R11-B.

    The boundary transcribes it rather than restating it, so a correction to the
    canonical table is a correction to the credentials a child receives.
    """
    row = IDENTITY_CONTRACT[name]
    canonical = CANONICAL_ACCOUNTS[name]
    assert row.primary_group == canonical.primary_group
    assert row.supplementary == canonical.supplementary
    assert row.provisioned_by_harness is canonical.provisioned_by_package
    assert row.rule is MembershipRule.EXACT
    assert row.superuser is False


def test_the_two_kinds_of_identity_are_distinguished() -> None:
    """Provisioned by the harness, or already on the host. Neither has a
    membership invented for it; the distinction is recorded, not applied."""
    provisioned = {
        name for name, row in IDENTITY_CONTRACT.items() if row.provisioned_by_harness
    }
    assert provisioned == {"freedomcoord", "freedomsheet", "fbprobe"}
    assert IDENTITY_CONTRACT["root"].superuser is True
    assert not any(
        row.superuser for name, row in IDENTITY_CONTRACT.items() if name != "root"
    )


def test_the_canonical_table_states_the_ruled_postgres_row_exactly_once() -> None:
    """EH-R6-1's disposition, at its source.

    Peter Duscha ruled the set on 2026-09-06 (change-log C-P5.0-AE): primary
    group `postgres`, complete supplementary set exactly `ssl-cert`. The row is
    in §2.12.2 as `identity.py` transcribes it, and it is marked as an existing
    host identity — this package does not provision it.
    """
    rows = [name for name in CANONICAL_ACCOUNTS if name == "postgres"]
    assert rows == ["postgres"]

    account = CANONICAL_ACCOUNTS["postgres"]
    assert account.primary_group == "postgres"
    assert account.supplementary == frozenset({"ssl-cert"})
    assert account.provisioned_by_package is False

    # The inverse half of the same membership, which is what makes it stated
    # rather than half-stated — stop condition 10p. The inverse is the
    # **explicit** `getent group` member relation, so the supplementary group
    # lists the account and the primary group does not — finding EH-R8-1.
    assert CANONICAL_GROUPS["ssl-cert"].members == frozenset({"postgres"})
    assert CANONICAL_GROUPS["postgres"].members == frozenset()


def test_the_contract_row_is_derived_from_the_canonical_row() -> None:
    """`IDENTITY_CONTRACT["postgres"]` restates nothing; it reads §2.12.2."""
    row = IDENTITY_CONTRACT["postgres"]
    account = CANONICAL_ACCOUNTS["postgres"]

    assert row.rule is MembershipRule.EXACT
    assert row.primary_group == account.primary_group
    assert row.supplementary == account.supplementary
    assert row.provisioned_by_harness is account.provisioned_by_package
    assert row.superuser is False


def test_exact_is_the_only_membership_rule_that_exists() -> None:
    """No pass-through, no wildcard, no subset-only rule, and no undecided state.

    R5's `AS_CONFIGURED` passed a host's configuration through — EH-R6-1. R6's
    `UNDECIDED` recorded that §2.12.2 did not describe `postgres`. Both are gone
    rather than unused: an enum value is an authority a later edit can reach for,
    and after the ruling there is nothing to reach for. Every row states
    §2.12.2's set, and there is no second way to write one.
    """
    assert {rule.name for rule in MembershipRule} == {"EXACT"}
    assert not hasattr(MembershipRule, "AS_CONFIGURED")
    assert not hasattr(MembershipRule, "UNDECIDED")
    assert not hasattr(boundary_module, "UNDECIDED_MEMBERSHIP")
    assert not hasattr(boundary_module, "MembershipUndecided")
    assert all(row.rule is MembershipRule.EXACT for row in IDENTITY_CONTRACT.values())


def test_the_contract_cannot_drift_from_the_canonical_table() -> None:
    """§2.12.2 and the credential contract are one source, enforced per row.

    Constructing a row that disagrees with `identity.CANONICAL_ACCOUNTS` raises
    while the table is being built, so the two cannot be edited apart — and a
    membership for an account §2.12.2 does not cover cannot be stated here at
    all, which is stop condition 10p applied to code.
    """
    with pytest.raises(IdentityInconsistent):
        RequiredIdentity(
            name="freedomcoord",
            primary_group="freedomcoord",
            supplementary=frozenset({"freedomjournal", "sudo"}),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=True,
        )
    with pytest.raises(IdentityInconsistent):
        RequiredIdentity(
            name="freedomcoord",
            primary_group="wheel",
            supplementary=frozenset({"freedomjournal"}),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=True,
        )
    # An account the canonical table does not cover cannot claim an exact list.
    with pytest.raises(IdentityInconsistent):
        RequiredIdentity(
            name="nobody",
            primary_group="nogroup",
            supplementary=frozenset({"ssl-cert"}),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=False,
        )
    # And the ruled row cannot be widened here either: `postgres` is covered
    # now, so restating its set with anything added is the same drift.
    with pytest.raises(IdentityInconsistent):
        RequiredIdentity(
            name="postgres",
            primary_group="postgres",
            supplementary=frozenset({"ssl-cert", "sudo"}),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=False,
        )
    # Nor narrowed, nor re-labelled as something this package provisions.
    with pytest.raises(IdentityInconsistent):
        RequiredIdentity(
            name="postgres",
            primary_group="postgres",
            supplementary=frozenset(),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=False,
        )
    with pytest.raises(IdentityInconsistent):
        RequiredIdentity(
            name="postgres",
            primary_group="postgres",
            supplementary=frozenset({"ssl-cert"}),
            rule=MembershipRule.EXACT,
            provisioned_by_harness=True,
        )


def test_changing_the_reviewed_postgres_policy_changes_the_manifest_digest() -> None:
    """The policy lives in a covered source, so it is inside the digest.

    That is the property the finding turned on: a membership fixed by the host
    rather than by a reviewed file could change what executes without changing
    any byte Codex approved. A membership fixed *here* cannot.
    """
    from pathlib import Path

    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan

    # The ruled set lives in the canonical table, so that is the file a change
    # to the policy has to move — and it is covered, so the digest moves with it.
    policy_source = "tools/phase_5_0_evidence/identity.py"
    assert policy_source in COVERED_SOURCES
    assert "tools/phase_5_0_evidence/execution/boundary.py" in COVERED_SOURCES

    root = Path(__file__).resolve().parents[2]
    sources = {name: (root / name).read_bytes() for name in COVERED_SOURCES}
    assert b'CanonicalAccount("postgres", "postgres", frozenset({"ssl-cert"})' in (
        sources[policy_source]
    )

    plan = build_concrete_plan()
    baseline = ReviewManifest.build(plan, dict(sources)).digest()
    for widened in (
        b'CanonicalAccount("postgres", "postgres", frozenset({"ssl-cert", "sudo"})',
        b'CanonicalAccount("postgres", "postgres", frozenset()',
    ):
        altered = dict(sources)
        altered[policy_source] = altered[policy_source].replace(
            b'CanonicalAccount("postgres", "postgres", frozenset({"ssl-cert"})',
            widened,
        )
        assert altered[policy_source] != sources[policy_source]
        assert ReviewManifest.build(plan, altered).digest() != baseline

    # EH-R8-1 and EH-R8-2: the corrected inverse rows are in the same covered
    # source, so the representation Codex approved is inside the digest too.
    # Putting the pre-R9 primary-membership claim back moves it, for the row R8
    # corrected and for each of the four the R9 ruling corrected — and so does
    # removing the `users` row that ruling added.
    for corrected, reverted in (
        (b'CanonicalGroup("postgres", frozenset(),',
         b'CanonicalGroup("postgres", frozenset({"postgres"}),'),
        (b'CanonicalGroup("freedomcoord", frozenset(),',
         b'CanonicalGroup("freedomcoord", frozenset({"freedomcoord"}),'),
        (b'CanonicalGroup("freedomsheet", frozenset(),',
         b'CanonicalGroup("freedomsheet", frozenset({"freedomsheet"}),'),
        (b'CanonicalGroup("discordbot", frozenset({"freedomweb"}),',
         b'CanonicalGroup("discordbot", frozenset({"discordbot", "freedomweb"}),'),
        (b'CanonicalGroup("fbprobe", frozenset(),',
         b'CanonicalGroup("fbprobe", frozenset({"fbprobe"}),'),
        (b'CanonicalGroup("users", frozenset({"foundry"}),',
         b'CanonicalGroup("users", frozenset(),'),
    ):
        assert corrected in sources[policy_source]
        reintroduced = dict(sources)
        reintroduced[policy_source] = reintroduced[policy_source].replace(
            corrected, reverted
        )
        assert reintroduced[policy_source] != sources[policy_source]
        assert ReviewManifest.build(plan, reintroduced).digest() != baseline


# ---------------------------------------------------------------------------
# What is passed to the process starter
# ---------------------------------------------------------------------------


def test_a_non_root_account_passes_its_numeric_ids_and_supplementary_groups(
    recorder: Recorder,
) -> None:
    result = start("fbprobe", FakeLookup())

    assert result.launch_failure == ""
    assert len(recorder.calls) == 1
    keywords = recorder.calls[0]
    assert keywords["user"] == 4003
    assert keywords["group"] == 4003
    assert keywords["extra_groups"] == []
    # The reviewed vector is the vector, and the credentials are beside it.
    assert recorder.positional[0][0] == ["/usr/bin/id"]
    assert keywords["shell"] is False
    assert keywords["cwd"] == "/"
    assert keywords["env"] == boundary_module.environment_for("/usr/bin/id")


def test_a_freedomjournal_member_keeps_the_membership_the_cases_depend_on(
    recorder: Recorder,
) -> None:
    """The defect, directly.

    `extra_groups=[]` cleared `freedomjournal` from `freedomcoord` and
    `freedomsheet`, so `JNL-52`'s positive traversal and the isolation cases
    would have been decided by the harness's credential construction rather than
    by the authority under test.
    """
    for name in ("freedomcoord", "freedomsheet"):
        recorder.calls.clear()
        result = start(name, FakeLookup())
        assert result.launch_failure == ""
        keywords = recorder.calls[0]
        assert keywords["user"] == ACCOUNTS[name][0]
        assert keywords["group"] == ACCOUNTS[name][1]
        assert keywords["extra_groups"] == [GROUPS["freedomjournal"]]


def test_a_non_member_receives_no_inherited_supplementary_group(
    recorder: Recorder,
) -> None:
    """`discordbot` is in no supplementary group, and gets none — not the
    caller's, and not another contract row's."""
    lookup = FakeLookup(caller_supplementary=frozenset({"freedomjournal", "sudo"}))
    result = start("discordbot", lookup)

    assert result.launch_failure == ""
    keywords = recorder.calls[0]
    assert keywords["user"] == 1001
    assert keywords["group"] == 1001
    assert keywords["extra_groups"] == []


def test_the_one_supplementary_group_an_existing_host_identity_has_is_kept(
    recorder: Recorder,
) -> None:
    """`freedomweb` is in `discordbot` — observation H-1's group-write fact — and
    that membership is passed rather than cleared."""
    result = start("freedomweb", FakeLookup())

    assert result.launch_failure == ""
    assert recorder.calls[0]["extra_groups"] == [GROUPS["discordbot"]]


def test_changing_the_parent_processs_groups_cannot_change_the_child_keywords(
    recorder: Recorder,
) -> None:
    """The credentials are a function of the contract and the account database.

    Nothing about the launching process contributes to them, so two runs whose
    caller differs in every way that could be inherited produce the identical
    keyword set.
    """
    first = FakeLookup(effective=(0, 0), caller_supplementary=frozenset())
    second = FakeLookup(
        effective=(0, 0),
        caller_supplementary=frozenset({"sudo", "adm", "freedomjournal"}),
    )

    start("freedomcoord", first)
    start("freedomcoord", second)

    assert recorder.calls[0] == recorder.calls[1]
    assert recorder.calls[0]["extra_groups"] == [GROUPS["freedomjournal"]]


def test_the_ruled_postgres_set_reaches_the_child_as_its_numeric_gid(
    recorder: Recorder,
) -> None:
    """EH-R6-1's disposition, at the keyword arguments.

    R5 passed the host's *configured* groups through, so a `usermod` after the
    digest was approved changed the credential vector without changing a
    reviewed byte. What reaches the child now is the **ruled** set resolved to
    numbers — and it is the reviewed set that decides, not the host's: the two
    agree here, and the tests below are the cases where they do not.
    """
    lookup = FakeLookup()
    result = start("postgres", lookup)

    assert result.launch_failure == ""
    keywords = recorder.calls[0]
    assert keywords["user"] == ACCOUNTS["postgres"][0]
    assert keywords["group"] == ACCOUNTS["postgres"][1]
    assert keywords["extra_groups"] == [GROUPS["ssl-cert"]]
    assert all(isinstance(gid, int) for gid in keywords["extra_groups"])


def test_the_postgres_credential_does_not_move_with_the_launchers_groups(
    recorder: Recorder,
) -> None:
    """The ruled row is a function of §2.12.2 and the account database alone.

    `test_changing_the_parent_processs_groups_cannot_change_the_child_keywords`
    asserts this for `freedomcoord`; the ruled row gets it too, because the row
    R5 got wrong is the row a reviewer will look at.
    """
    first = FakeLookup(effective=(0, 0), caller_supplementary=frozenset())
    second = FakeLookup(
        effective=(0, 0),
        caller_supplementary=frozenset({"sudo", "adm", "ssl-cert", "freedomjournal"}),
    )

    start("postgres", first)
    start("postgres", second)

    assert recorder.calls[0] == recorder.calls[1]
    assert recorder.calls[0]["extra_groups"] == [GROUPS["ssl-cert"]]


def test_extra_groups_is_a_sorted_list_of_numbers_and_does_not_vary(
    recorder: Recorder,
) -> None:
    """Deterministic order, so two runs of one reviewed tree pass one vector.

    The credential is built from a `frozenset`, whose iteration order is not a
    contract, and `extra_groups=` is an ordered argument. `_resolve` sorts twice
    — the names before they are resolved and the numbers after — and this asserts
    the observable half: every row's list is numerically sorted, and rebuilding
    the same row from an account database whose insertion order differs produces
    the identical list.
    """
    for name, row in sorted(IDENTITY_CONTRACT.items()):
        if row.name == "root":
            continue
        recorder.calls.clear()
        assert start(name, FakeLookup(effective=(0, 0))).launch_failure == "", name
        gids = recorder.calls[0]["extra_groups"]
        assert gids == sorted(gids), name
        assert all(isinstance(gid, int) and not isinstance(gid, bool) for gid in gids)

        # The same row, from a group table built in the opposite order.
        recorder.calls.clear()
        reversed_groups = dict(reversed(list(GROUPS.items())))
        shuffled = FakeLookup(effective=(0, 0), groups=reversed_groups)
        assert start(name, shuffled).launch_failure == "", name
        assert recorder.calls[0]["extra_groups"] == gids, name


def test_a_host_configured_group_outside_the_ruled_set_never_reaches_the_child(
    recorder: Recorder,
) -> None:
    """The ruling states a **complete** set, so one extra group is a refusal.

    This is the property R5 lacked. A `usermod -aG sudo postgres` run after the
    digest was approved does not widen the credential — it stops the step, before
    a process exists, and the refusal names no group.
    """
    widened = FakeLookup()
    widened.memberships["postgres"] = frozenset({"ssl-cert", "sudo"})
    widened.groups["sudo"] = 27

    result = start("postgres", widened)

    assert result.launch_failure == LAUNCH_IDENTITY_MEMBERSHIP
    assert result.exit_status == -1
    assert "sudo" not in repr(result)
    assert "ssl-cert" not in repr(result)
    assert recorder.calls == []


def test_the_ruled_membership_missing_on_the_host_refuses(
    recorder: Recorder,
) -> None:
    """Equality is required in both directions, so a *missing* group refuses too.

    A `psql` step that ran without `ssl-cert` would produce a result attributable
    to the harness's credential construction rather than to the authority under
    test — the class of outcome EH-R5-1 exists to prevent.
    """
    stripped = FakeLookup()
    stripped.memberships["postgres"] = frozenset()

    result = start("postgres", stripped)

    assert result.launch_failure == LAUNCH_IDENTITY_MEMBERSHIP
    assert recorder.calls == []


def test_an_identity_outside_the_contract_is_refused_before_the_account_is_read(
    recorder: Recorder,
) -> None:
    """No host read contributes to a name the contract does not describe.

    A lookup that raises on every call still produces the same refusal, which is
    only possible if the refusal happens before the lookup is consulted. R6
    asserted this of the undecided `postgres` row; after the ruling there is no
    such row, so the property is asserted where it still lives — a name that is
    not in the closed table at all.
    """

    @dataclass
    class RefusingLookup:
        consulted: list[str] = field(default_factory=list)

        def account(self, name: str) -> tuple[int, int]:
            self.consulted.append(name)
            raise AssertionError("the account database must not be read")

        def group_id(self, name: str) -> int:
            raise AssertionError("the group database must not be read")

        def supplementary_group_names(
            self, name: str, primary_gid: int
        ) -> frozenset[str]:
            raise AssertionError("the group list must not be read")

        def effective_ids(self) -> tuple[int, int]:
            return (0, 0)

    lookup = RefusingLookup()
    result = SubprocessBoundary(armed=True, lookup=lookup).run(
        step_id="S-01",
        argv=("/usr/bin/psql",),
        run_as="postgres-16",
        capture=CapturePolicy.EXIT_STATUS_ONLY,
        timeout_seconds=30.0,
    )

    assert result.launch_failure == LAUNCH_IDENTITY_NOT_IN_CONTRACT
    assert lookup.consulted == []
    assert recorder.calls == []


def test_an_empty_ruled_set_passes_no_group_and_still_rejects_every_extra(
    recorder: Recorder,
) -> None:
    """The shape the ruling would have had if the set had been ruled empty.

    `postgres` was ruled `ssl-cert`, so the empty-set behaviour is asserted on
    the rows §2.12.2 does state as empty. `extra_groups=[]` is passed explicitly
    — not omitted, which is what made the child inherit the launcher's list in
    R5 — and any group the host adds is still a refusal rather than a widening.
    """
    for name in ("fbprobe", "discordbot"):
        assert CANONICAL_ACCOUNTS[name].supplementary == frozenset()

        recorder.calls.clear()
        assert start(name, FakeLookup()).launch_failure == ""
        assert recorder.calls[0]["extra_groups"] == []

        recorder.calls.clear()
        widened = FakeLookup()
        widened.memberships[name] = frozenset({"ssl-cert"})
        assert start(name, widened).launch_failure == LAUNCH_IDENTITY_MEMBERSHIP
        assert recorder.calls == []


def test_every_exact_row_reaches_extra_groups_as_numeric_gids(
    recorder: Recorder,
) -> None:
    """The permitted set, and nothing else, as numbers — for every row that runs.

    The host in `FakeLookup` is well-formed, so this is the positive half of the
    equality: each child receives exactly the gids of §2.12.2's list for its
    identity, sorted, and no other.
    """
    for name, row in sorted(IDENTITY_CONTRACT.items()):
        if row.rule is not MembershipRule.EXACT:
            continue
        recorder.calls.clear()
        result = start(name, FakeLookup(effective=(0, 0)))
        assert result.launch_failure == "", name
        keywords = recorder.calls[0]
        assert keywords["extra_groups"] == sorted(
            GROUPS[group] for group in row.supplementary
        ), name
        assert all(isinstance(gid, int) for gid in keywords["extra_groups"]), name


def test_root_is_constructed_explicitly_rather_than_inherited(
    recorder: Recorder,
) -> None:
    result = start("root", FakeLookup(effective=(0, 0)))

    assert result.launch_failure == ""
    keywords = recorder.calls[0]
    assert keywords["user"] == 0
    assert keywords["group"] == 0
    assert keywords["extra_groups"] == []


# ---------------------------------------------------------------------------
# Refusals, all of them before a process exists
# ---------------------------------------------------------------------------


def test_a_non_root_launcher_cannot_run_a_root_step_as_itself(
    recorder: Recorder,
) -> None:
    """`run_as="root"` never means *"whatever identity launched the CLI"*."""
    for effective in ((1000, 1000), (0, 1000), (1000, 0)):
        result = start("root", FakeLookup(effective=effective))
        assert result.launch_failure == LAUNCH_ROOT_UNAVAILABLE
        assert result.exit_status == -1
    assert recorder.calls == []


def test_an_identity_that_is_not_a_contract_row_is_refused(
    recorder: Recorder,
) -> None:
    for unknown in ("nobody", "mallory", "Root", "postgres-16", "foundry"):
        result = start(unknown, FakeLookup())
        assert result.launch_failure == LAUNCH_IDENTITY_NOT_IN_CONTRACT
    assert recorder.calls == []


def test_an_absent_account_or_group_refuses_before_process_creation(
    recorder: Recorder,
) -> None:
    without_account = FakeLookup()
    del without_account.accounts["freedomcoord"]
    assert start("freedomcoord", without_account).launch_failure == (
        LAUNCH_IDENTITY_UNKNOWN
    )

    without_group = FakeLookup()
    del without_group.groups["freedomjournal"]
    assert start("freedomcoord", without_group).launch_failure == (
        LAUNCH_IDENTITY_UNKNOWN
    )

    without_primary = FakeLookup()
    del without_primary.groups["fbprobe"]
    assert start("fbprobe", without_primary).launch_failure == LAUNCH_IDENTITY_UNKNOWN

    assert recorder.calls == []


def test_a_duplicated_account_or_group_refuses(recorder: Recorder) -> None:
    """Which identity a step would assume is not decidable, so it does not run."""
    duplicated_account = FakeLookup(
        account_failures={
            "fbprobe": IdentityInconsistent("more than one account record")
        }
    )
    assert start("fbprobe", duplicated_account).launch_failure == (
        LAUNCH_IDENTITY_INCONSISTENT
    )

    duplicated_group = FakeLookup(
        group_failures={
            "freedomjournal": IdentityInconsistent("more than one group record")
        }
    )
    assert start("freedomcoord", duplicated_group).launch_failure == (
        LAUNCH_IDENTITY_INCONSISTENT
    )
    assert recorder.calls == []


def test_an_account_whose_primary_group_does_not_round_trip_refuses(
    recorder: Recorder,
) -> None:
    """`fbprobe`'s passwd gid and the gid of the group the contract names must be
    the same number. A host where they differ is a host this run does not use."""
    inconsistent = FakeLookup()
    inconsistent.groups["fbprobe"] = 9999
    assert start("fbprobe", inconsistent).launch_failure == (
        LAUNCH_IDENTITY_INCONSISTENT
    )
    assert recorder.calls == []


def test_a_non_root_row_that_resolves_to_a_superuser_id_refuses(
    recorder: Recorder,
) -> None:
    """A `fbprobe` with uid 0 is a malformed identity, not a step that may run."""
    as_uid_zero = FakeLookup()
    as_uid_zero.accounts["fbprobe"] = (0, 4003)
    assert start("fbprobe", as_uid_zero).launch_failure == LAUNCH_IDENTITY_INCONSISTENT

    as_gid_zero = FakeLookup()
    as_gid_zero.accounts["fbprobe"] = (4003, 0)
    as_gid_zero.groups["fbprobe"] = 0
    assert start("fbprobe", as_gid_zero).launch_failure == LAUNCH_IDENTITY_INCONSISTENT

    with_root_supplementary = FakeLookup()
    with_root_supplementary.groups["freedomjournal"] = 0
    assert start("freedomcoord", with_root_supplementary).launch_failure == (
        LAUNCH_IDENTITY_INCONSISTENT
    )
    assert recorder.calls == []


def test_a_required_membership_missing_at_execution_time_refuses(
    recorder: Recorder,
) -> None:
    """The membership may exist when the plan is reviewed and not when it runs.

    Refusing here is what keeps a later refusal attributable: a case that needs
    `freedomjournal` and runs without it produces a denial that says nothing
    about the authority it was meant to test.
    """
    lookup = FakeLookup()
    lookup.memberships["freedomcoord"] = frozenset()
    assert start("freedomcoord", lookup).launch_failure == LAUNCH_IDENTITY_MEMBERSHIP
    assert recorder.calls == []


def test_an_unexpected_membership_refuses_where_the_list_is_exact(
    recorder: Recorder,
) -> None:
    """§2.12.2's supplementary lists are complete, so an extra group is a failed
    case rather than a difference to note — `classify_group_membership`'s rule,
    applied to the credentials as well as to the evidence."""
    lookup = FakeLookup()
    lookup.memberships["freedomcoord"] = frozenset({"freedomjournal", "sudo"})
    lookup.groups["sudo"] = 27
    assert start("freedomcoord", lookup).launch_failure == LAUNCH_IDENTITY_MEMBERSHIP

    extra_on_a_row_with_none = FakeLookup()
    extra_on_a_row_with_none.memberships["fbprobe"] = frozenset({"freedomjournal"})
    assert start("fbprobe", extra_on_a_row_with_none).launch_failure == (
        LAUNCH_IDENTITY_MEMBERSHIP
    )
    assert recorder.calls == []


def test_the_unarmed_blank_timeout_and_relative_refusals_still_start_nothing(
    recorder: Recorder,
) -> None:
    unarmed = SubprocessBoundary(lookup=FakeLookup()).run(
        step_id="S-01",
        argv=("/usr/bin/id",),
        run_as="root",
        capture=CapturePolicy.EXIT_STATUS_ONLY,
        timeout_seconds=30.0,
    )
    assert unarmed.launch_failure == LAUNCH_BOUNDARY_NOT_ARMED

    assert start("", FakeLookup()).launch_failure == LAUNCH_BLANK_IDENTITY
    assert start("   ", FakeLookup()).launch_failure == LAUNCH_BLANK_IDENTITY
    assert start("root", FakeLookup(), timeout_seconds=0).launch_failure == (
        LAUNCH_NO_TIMEOUT
    )
    assert start("root", FakeLookup(), argv=("id",)).launch_failure == (
        LAUNCH_NOT_ABSOLUTE
    )
    assert recorder.calls == []


def test_the_operating_systems_own_refusals_are_classifications_too(
    recorder: Recorder,
) -> None:
    """A refused transition, a missing executable and a timeout each become one
    fixed word. The exception is dropped where it is raised."""
    recorder.raises = PermissionError("Operation not permitted: setgroups")
    assert start("fbprobe", FakeLookup()).launch_failure == LAUNCH_IDENTITY_REFUSED

    recorder.raises = FileNotFoundError("/usr/bin/id")
    assert start("fbprobe", FakeLookup()).launch_failure == LAUNCH_EXECUTABLE_ABSENT

    recorder.raises = Recorder.TimeoutExpired("timed out")
    timed_out = start("fbprobe", FakeLookup())
    assert timed_out.launch_failure == LAUNCH_TIMEOUT
    assert timed_out.timed_out is True


def test_no_classification_carries_lookup_or_operating_system_text(
    recorder: Recorder,
) -> None:
    """The whole point of a fixed vocabulary.

    A sentinel is planted in every message the lookup and the process starter
    can raise, and it appears in no field of any result. Neither does an account
    name, a numeric id or a group name.
    """
    sentinel = "SENTINEL-uid-4001-gid-4100-freedomjournal-EACCES"
    lookups = [
        FakeLookup(account_failures={"freedomcoord": IdentityAbsent(sentinel)}),
        FakeLookup(account_failures={"freedomcoord": IdentityInconsistent(sentinel)}),
        FakeLookup(group_failures={"freedomjournal": IdentityAbsent(sentinel)}),
    ]
    results = [start("freedomcoord", lookup) for lookup in lookups]

    recorder.raises = PermissionError(sentinel)
    results.append(start("fbprobe", FakeLookup()))

    for result in results:
        assert result.launch_failure in LAUNCH_FAILURES
        rendered = repr(result)
        assert sentinel not in rendered
        assert "4001" not in rendered and "4100" not in rendered
        assert "freedomjournal" not in rendered
    # Only the last case reached the process starter at all; the three lookup
    # refusals were decided before it.
    assert len(recorder.calls) == 1


def test_every_classification_the_boundary_can_return_is_in_the_fixed_set() -> None:
    """Read as text, so a classification added on a branch a test does not take
    still has to be declared."""
    from pathlib import Path
    import ast

    source = (
        Path(__file__).resolve().parents[2]
        / "tools"
        / "phase_5_0_evidence"
        / "execution"
        / "boundary.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    declared = {
        node.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
        and any(
            isinstance(target, ast.Name) and target.id.startswith("LAUNCH_")
            for target in node.targets
        )
    }
    assert declared == LAUNCH_FAILURES
    for classification in LAUNCH_FAILURES:
        assert classification.replace("-", "").isalpha()
        assert classification.islower()


# ---------------------------------------------------------------------------
# EH-R6-2: one account record, one group record, and they must agree
# ---------------------------------------------------------------------------


@dataclass
class FakeAccountDatabase:
    """The account and group database `SystemIdentityLookup` reads.

    This is the seam R6 needs, and it is deliberately **below** the lookup: the
    defect was inside `SystemIdentityLookup`, so a fake standing in for that
    class would prove nothing about it. Every record here is written in this
    file; none is read from a host.

    `direct_account` and `direct_group` are what the direct lookups answer when
    a test needs them to disagree with the enumeration — the one contradiction
    an enumeration alone cannot express.
    """

    account_records: list[tuple[str, int, int]] = field(default_factory=list)
    group_records: list[tuple[str, int]] = field(default_factory=list)
    direct_account: dict[str, tuple[str, int, int]] = field(default_factory=dict)
    direct_group: dict[str, tuple[str, int]] = field(default_factory=dict)
    initial_group_ids: dict[str, tuple[int, ...]] = field(default_factory=dict)
    effective: tuple[int, int] = (0, 0)

    def account(self, name: str) -> tuple[str, int, int]:
        if name in self.direct_account:
            return self.direct_account[name]
        for record in self.account_records:
            if record[0] == name:
                return record
        raise KeyError(name)

    def accounts(self) -> list[tuple[str, int, int]]:
        return list(self.account_records)

    def group(self, name: str) -> tuple[str, int]:
        if name in self.direct_group:
            return self.direct_group[name]
        for record in self.group_records:
            if record[0] == name:
                return record
        raise KeyError(name)

    def groups(self) -> list[tuple[str, int]]:
        return list(self.group_records)

    def group_name(self, gid: int) -> str:
        for record in self.group_records:
            if record[1] == gid:
                return record[0]
        raise KeyError(gid)

    def group_ids(self, name: str, primary_gid: int) -> list[int]:
        return list(self.initial_group_ids.get(name, (primary_gid,)))

    def effective_ids(self) -> tuple[int, int]:
        return self.effective


def one_of_each() -> FakeAccountDatabase:
    """A well-formed database: exactly one record per name, all consistent."""
    return FakeAccountDatabase(
        account_records=[("root", 0, 0), ("fbprobe", 4003, 4003)],
        group_records=[("root", 0), ("fbprobe", 4003), ("freedomjournal", 4100)],
        initial_group_ids={"fbprobe": (4003,)},
    )


def test_the_lookups_default_database_is_the_system_one() -> None:
    """The injection is a seam, not a substitute: production reads `pwd`/`grp`.

    Constructing it reads nothing, which is why this assertion is safe to make
    in a suite that must not touch the host's accounts.
    """
    assert isinstance(SystemIdentityLookup().database, SystemAccountDatabase)


def test_exactly_one_account_and_group_record_resolves() -> None:
    lookup = SystemIdentityLookup(database=one_of_each())

    assert lookup.account("fbprobe") == (4003, 4003)
    assert lookup.group_id("freedomjournal") == 4100
    assert lookup.supplementary_group_names("fbprobe", 4003) == frozenset()
    assert lookup.effective_ids() == (0, 0)


@pytest.mark.parametrize(
    "second",
    [("fbprobe", 4003, 4003), ("fbprobe", 5000, 5000)],
    ids=["identical", "contradictory"],
)
def test_two_account_records_refuse_however_they_are_numbered(
    second: tuple[str, int, int],
) -> None:
    """The defect, directly.

    R5 collected `(uid, gid)` pairs into a set and refused only when the set had
    more than one member, so the identical pair collapsed to one member and was
    accepted — while the contract it documented says a duplicated record is
    ambiguous and must refuse. Records are counted now, not deduplicated.
    """
    database = one_of_each()
    database.account_records.append(second)

    with pytest.raises(IdentityInconsistent):
        SystemIdentityLookup(database=database).account("fbprobe")


@pytest.mark.parametrize(
    "second",
    [("freedomjournal", 4100), ("freedomjournal", 4200)],
    ids=["identical", "contradictory"],
)
def test_two_group_records_refuse_however_they_are_numbered(
    second: tuple[str, int],
) -> None:
    """The same rule for named group records, which R5 collapsed the same way."""
    database = one_of_each()
    database.group_records.append(second)

    with pytest.raises(IdentityInconsistent):
        SystemIdentityLookup(database=database).group_id("freedomjournal")


def test_a_direct_answer_that_contradicts_the_one_record_refuses() -> None:
    """A database that answers one thing and enumerates another contradicts
    itself, and this run does not choose between the two."""
    for direct in (
        ("fbprobe", 4003, 9999),
        ("fbprobe", 9999, 4003),
        ("fbprobe-old", 4003, 4003),
    ):
        database = one_of_each()
        database.direct_account["fbprobe"] = direct
        with pytest.raises(IdentityInconsistent):
            SystemIdentityLookup(database=database).account("fbprobe")

    for direct_group in (("freedomjournal", 9999), ("freedomjournal-old", 4100)):
        database = one_of_each()
        database.direct_group["freedomjournal"] = direct_group
        with pytest.raises(IdentityInconsistent):
            SystemIdentityLookup(database=database).group_id("freedomjournal")


def test_zero_matching_records_are_absent_rather_than_inconsistent() -> None:
    """Both ways a name can have no record: no direct answer, or none enumerated."""
    with pytest.raises(IdentityAbsent):
        SystemIdentityLookup(database=one_of_each()).account("nobody")
    with pytest.raises(IdentityAbsent):
        SystemIdentityLookup(database=one_of_each()).group_id("nogroup")

    enumerates_nothing = one_of_each()
    enumerates_nothing.direct_account["ghost"] = ("ghost", 7000, 7000)
    with pytest.raises(IdentityAbsent):
        SystemIdentityLookup(database=enumerates_nothing).account("ghost")

    no_group_record = one_of_each()
    no_group_record.direct_group["ghosts"] = ("ghosts", 7000)
    with pytest.raises(IdentityAbsent):
        SystemIdentityLookup(database=no_group_record).group_id("ghosts")


def test_a_supplementary_group_with_no_name_refuses() -> None:
    database = one_of_each()
    database.initial_group_ids["fbprobe"] = (4003, 6001)

    with pytest.raises(IdentityInconsistent):
        SystemIdentityLookup(database=database).supplementary_group_names(
            "fbprobe", 4003
        )


def test_the_real_lookup_builds_the_exact_credential_from_one_record_each(
    recorder: Recorder,
) -> None:
    """EH-R6-1 and EH-R6-2 meeting: one record each, resolved to the exact set."""
    database = FakeAccountDatabase(
        account_records=[("freedomcoord", 4001, 4001)],
        group_records=[("freedomcoord", 4001), ("freedomjournal", 4100)],
        initial_group_ids={"freedomcoord": (4001, 4100)},
    )

    result = start("freedomcoord", SystemIdentityLookup(database=database))

    assert result.launch_failure == ""
    keywords = recorder.calls[0]
    assert keywords["user"] == 4001
    assert keywords["group"] == 4001
    assert keywords["extra_groups"] == [4100]


def test_the_real_lookups_refusals_reach_the_boundary_as_fixed_classifications(
    recorder: Recorder,
) -> None:
    """Counted through the boundary, and carrying no record, id or group name."""
    duplicated = FakeAccountDatabase(
        account_records=[("fbprobe", 4003, 4003), ("fbprobe", 4003, 4003)],
        group_records=[("fbprobe", 4003)],
        initial_group_ids={"fbprobe": (4003,)},
    )
    inconsistent = start("fbprobe", SystemIdentityLookup(database=duplicated))
    assert inconsistent.launch_failure == LAUNCH_IDENTITY_INCONSISTENT
    assert "4003" not in repr(inconsistent)

    absent = start("fbprobe", SystemIdentityLookup(database=FakeAccountDatabase()))
    assert absent.launch_failure == LAUNCH_IDENTITY_UNKNOWN
    assert "fbprobe" not in repr(absent)

    assert recorder.calls == []


# ---------------------------------------------------------------------------
# What this file does not do
# ---------------------------------------------------------------------------


def test_this_file_reads_no_account_and_starts_no_process() -> None:
    """Source-level, about this module itself.

    The real `SystemIdentityLookup` is imported for the assertion below and is
    never constructed with a name to look up; every test above injects
    `FakeLookup`.
    """
    from pathlib import Path
    import ast

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])
    assert not (imported & {"pwd", "grp", "os"}), (
        "this file writes its own account table; it does not read the host's"
    )
    assert SystemIdentityLookup is not None
