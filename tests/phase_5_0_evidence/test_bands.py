"""The evidence bands: identity, capability, filesystem, manifest, provenance and
journal.

Every case here is over supplied observations. Nothing runs a command, opens a
socket, reads `/proc`, or needs root — which is the point: the classification is
what this stage delivers, and it has to be reviewable before a single privileged
step is authorized.
"""
from __future__ import annotations

from dataclasses import replace
from unittest import mock

import pytest

from tools.phase_5_0_evidence.capability import (
    CAP_DAC_OVERRIDE,
    CAP_DAC_READ_SEARCH,
    CAP_FOWNER,
    CAP_LINUX_IMMUTABLE,
    CapabilityCase,
    DOCUMENTED_CAP_LAST_CAP,
    DOCUMENTED_ROOT_MASK,
    EVIDENCE_IDENTITIES,
    REQUIRED_LAUNCHER_CAPABILITIES,
    SECBITS_NO_SETUID_FIXUP,
    classify_capability_case,
    classify_launcher_bounding_set,
    classify_root_masks,
    control_form_for,
    declared_identity,
    documented_root_masks,
    mask_for,
)
from tools.phase_5_0_evidence import identity as identity_module
from tools.phase_5_0_evidence.case_runtime import INTERPRETER_FLAGS, INTERPRETER_PATH
from tools.phase_5_0_evidence.errors import ObservationRefused, PlanRefused
from tools.phase_5_0_evidence.filesystem import (
    ALL_CASES,
    STAGE_1,
    STAGE_2,
    STAGE_3,
    STAGE_4,
    classify_probe_case,
    probe_report_admissible,
    stage_four_ordering_holds,
    stage_status,
)
from tools.phase_5_0_evidence.identity import (
    CANONICAL_ACCOUNTS,
    CANONICAL_GROUPS,
    MEMBERSHIP_CASE_IDS,
    AccessCase,
    CanonicalAccount,
    CanonicalGroup,
    ObservedAccount,
    ObservedGroup,
    account_case_id,
    classify_access,
    classify_account_identity,
    classify_group_membership,
    group_case_id,
    membership_matrix_holds,
)
from tests.phase_5_0_evidence.unit_sandbox_fixtures import classify as classify_s4_3
from tools.phase_5_0_evidence.journal import (
    RECOVERY_PROCEDURE,
    classify_recovery,
)
from tools.phase_5_0_evidence.manifest import (
    DeploymentEntry,
    EntryClass,
    PartitionFacts,
    SourceEntry,
    classify_manifest_equivalence,
    classify_partition,
    deployment_manifest_digest,
    source_manifest_digest,
)
from tools.phase_5_0_evidence.provenance import (
    ApprovedRevision,
    FileFacts,
    ProvenanceRecord,
    classify_missing_provenance,
    classify_provenance_agreement,
    classify_worktree_isolation,
)
from tools.phase_5_0_evidence.records import CaseRole, EvidenceRecord, Outcome, Status

# ---------------------------------------------------------------------------
# identity — C-4 / JNL-52
# ---------------------------------------------------------------------------


def test_the_canonical_membership_is_matched_as_a_set_not_a_containment() -> None:
    exact = classify_group_membership(
        ObservedGroup("freedomjournal", 5000, frozenset({"freedomcoord", "freedomsheet"}))
    )
    assert exact.status is Status.PASSED

    extra = classify_group_membership(
        ObservedGroup("freedomjournal", 5000, frozenset({"freedomcoord", "freedomsheet", "discordbot"}))
    )
    assert extra.status is Status.FAILED
    assert extra.detail["unexpected_members"] == "discordbot"

    short = classify_group_membership(ObservedGroup("freedomjournal", 5000, frozenset({"freedomcoord"})))
    assert short.status is Status.FAILED
    assert short.detail["missing_members"] == "freedomsheet"


def test_a_complete_supplementary_list_means_exhaustive() -> None:
    """An identity whose supplementary list is `—` is asserted to be in **no**
    supplementary group, and `JNL-52` fails the case rather than passing it."""
    clean = classify_account_identity(
        ObservedAccount("discordbot", 997, 997, "discordbot", frozenset())
    )
    assert clean.status is Status.PASSED

    extra = classify_account_identity(
        ObservedAccount("discordbot", 997, 997, "discordbot", frozenset({"freedomjournal"}))
    )
    assert extra.status is Status.FAILED


def test_a_group_or_account_outside_section_2_12_2_cannot_be_classified() -> None:
    with pytest.raises(ObservationRefused):
        classify_group_membership(ObservedGroup("wheel", 10, frozenset()))
    with pytest.raises(ObservationRefused):
        classify_account_identity(ObservedAccount("nobody", 65534, 65534, "nogroup", frozenset()))


def traverse_control(observed: Outcome) -> EvidenceRecord:
    """`JNL-52` case 5: `discordbot` reaching `<TARGET_ROOT>` itself.

    Declared `CONTROL`, because case 6 is read beside it and nothing else in the
    band may be. Its status comes from `observed` and from nothing a caller says.
    """
    return classify_access(
        AccessCase(
            case_id="JNL-52-5",
            identity="discordbot",
            path="/var/lib/fb-evidence-r1",
            operation="stat the parent, to show the denial below is not a path search",
            expected=Outcome.returned(),
            role=CaseRole.CONTROL,
        ),
        observed,
    )


def seal_denial(control_record: EvidenceRecord) -> EvidenceRecord:
    """`JNL-52` case 6, interpreted beside case 5's **record**."""
    return classify_access(
        AccessCase(
            case_id="JNL-52-6",
            identity="discordbot",
            path="/var/lib/fb-evidence-r1/journal/000001.seal",
            operation="open(O_RDONLY)",
            expected=Outcome.refused("EACCES"),
            control_case_id="JNL-52-5",
            role=CaseRole.DEPENDENT,
        ),
        Outcome.refused("EACCES"),
        control=control_record,
    )


def test_an_access_denial_is_not_interpreted_without_its_traverse_control() -> None:
    failed = traverse_control(Outcome.refused("EACCES"))
    assert failed.status is Status.FAILED
    assert seal_denial(failed).status is Status.INCONCLUSIVE


def test_an_access_denial_beside_a_passing_traverse_control_is_a_pass() -> None:
    """The other half: cases 5 and 7 exist so cases 6 and 8 can mean something."""
    passing = traverse_control(Outcome.returned())
    assert passing.status is Status.PASSED
    assert seal_denial(passing).status is Status.PASSED


def test_an_access_case_whose_role_and_reference_disagree_is_refused() -> None:
    """The role is declared, not inferred from the reference."""
    with pytest.raises(ObservationRefused):
        AccessCase(
            case_id="JNL-52-6",
            identity="discordbot",
            path="/var/lib/fb-evidence-r1/journal/000001.seal",
            operation="open(O_RDONLY)",
            expected=Outcome.refused("EACCES"),
            control_case_id="JNL-52-5",
        )
    with pytest.raises(ObservationRefused):
        AccessCase(
            case_id="JNL-52-5",
            identity="discordbot",
            path="/var/lib/fb-evidence-r1",
            operation="stat the parent",
            expected=Outcome.returned(),
            role=CaseRole.DEPENDENT,
        )


def test_a_dependent_access_case_without_its_control_record_is_refused() -> None:
    """A denial beside a control nobody supplied attributes nothing, so the
    classifier refuses rather than classifying it as an uncontrolled case."""
    with pytest.raises(ObservationRefused):
        classify_access(
            AccessCase(
                case_id="JNL-52-6",
                identity="discordbot",
                path="/var/lib/fb-evidence-r1/journal/000001.seal",
                operation="open(O_RDONLY)",
                expected=Outcome.refused("EACCES"),
                control_case_id="JNL-52-5",
                role=CaseRole.DEPENDENT,
            ),
            Outcome.refused("EACCES"),
        )


def test_the_ruled_postgres_row_is_in_both_halves_of_the_canonical_table() -> None:
    """The R7 amendment, at its source, and its `JNL-52` cases.

    Peter Duscha ruled the set on 2026-09-06 (change-log C-P5.0-AE). The row is
    §2.12.2's, so the membership matrix asserts it like every other: `id
    postgres` must report `postgres` plus `ssl-cert` and nothing else, and
    `getent group ssl-cert` must report exactly `postgres`.
    """
    account = CANONICAL_ACCOUNTS["postgres"]
    assert account.primary_group == "postgres"
    assert account.supplementary == frozenset({"ssl-cert"})
    assert account.provisioned_by_package is False

    # EH-R8-1. The supplementary half is explicit membership and is listed
    # exactly once; the primary half is **not** an explicit `getent group`
    # member and must not be manufactured into one.
    assert CANONICAL_GROUPS["ssl-cert"].members == frozenset({"postgres"})
    assert sorted(CANONICAL_GROUPS["ssl-cert"].members).count("postgres") == 1
    assert CANONICAL_GROUPS["postgres"].members == frozenset()

    assert account_case_id("postgres") in MEMBERSHIP_CASE_IDS
    assert group_case_id("ssl-cert") in MEMBERSHIP_CASE_IDS
    assert group_case_id("postgres") in MEMBERSHIP_CASE_IDS

    passed = classify_account_identity(
        ObservedAccount("postgres", 114, 120, "postgres", frozenset({"ssl-cert"}))
    )
    assert passed.status is Status.PASSED

    # A host that adds one group fails the case rather than noting a difference.
    widened = classify_account_identity(
        ObservedAccount(
            "postgres", 114, 120, "postgres", frozenset({"ssl-cert", "sudo"})
        )
    )
    assert widened.status is Status.FAILED
    assert widened.detail["unexpected_supplementary"] == "sudo"

    missing = classify_account_identity(
        ObservedAccount("postgres", 114, 120, "postgres", frozenset())
    )
    assert missing.status is Status.FAILED


def test_the_two_halves_of_the_canonical_table_agree_in_both_directions() -> None:
    """**EH-R8-2.** Every membership is stated on both sides, over the whole
    table — not one ruled row.

    This is computed from the tables rather than transcribed beside them, so it
    is the relation that is asserted and not a copy of it. A supplementary
    membership missing from either half, or an explicit member no identity row
    states, fails here.
    """
    stated_by_accounts = {
        (account.name, group)
        for account in CANONICAL_ACCOUNTS.values()
        for group in account.supplementary
    }
    stated_by_inverse = {
        (member, group.name)
        for group in CANONICAL_GROUPS.values()
        for member in group.members
    }
    assert stated_by_accounts == stated_by_inverse

    # And it is not vacuous: the relation is the six supplementary memberships
    # §2.12.2 states, named here so a table that silently lost one fails.
    assert stated_by_accounts == {
        ("freedomcoord", "freedomjournal"),
        ("freedomsheet", "freedomjournal"),
        ("freedomweb", "discordbot"),
        ("foundry", "sudo"),
        ("foundry", "users"),
        ("postgres", "ssl-cert"),
    }


def test_the_r9_corrected_inverse_rows_are_exact() -> None:
    """The four ruled sets and the ruled `users` row, at their source.

    Peter Duscha accepted Codex's recommendation on 2026-09-06 (change-log
    **C-P5.0-AF**, package plan §2.12.2's R9 ruling): `freedomcoord`,
    `freedomsheet` and `fbprobe` have **no** explicit members, `discordbot` has
    `freedomweb` **only**, and the inverse row completing the already-recorded
    `foundry -> users` supplementary membership is `users`: `foundry` only.
    """
    assert CANONICAL_GROUPS["freedomcoord"].members == frozenset()
    assert CANONICAL_GROUPS["freedomsheet"].members == frozenset()
    assert CANONICAL_GROUPS["discordbot"].members == frozenset({"freedomweb"})
    assert CANONICAL_GROUPS["fbprobe"].members == frozenset()
    assert CANONICAL_GROUPS["users"].members == frozenset({"foundry"})
    assert group_case_id("users") in MEMBERSHIP_CASE_IDS

    # The ruling was representational: no account's primary group or complete
    # supplementary set moved.
    assert CANONICAL_ACCOUNTS["freedomcoord"].supplementary == frozenset({"freedomjournal"})
    assert CANONICAL_ACCOUNTS["freedomsheet"].supplementary == frozenset({"freedomjournal"})
    assert CANONICAL_ACCOUNTS["discordbot"].supplementary == frozenset()
    assert CANONICAL_ACCOUNTS["freedomweb"].supplementary == frozenset({"discordbot"})
    assert CANONICAL_ACCOUNTS["fbprobe"].supplementary == frozenset()
    assert CANONICAL_ACCOUNTS["foundry"].supplementary == frozenset({"sudo", "users"})
    for name in ("freedomcoord", "freedomsheet", "discordbot", "fbprobe",
                 "freedomweb", "foundry", "postgres"):
        assert CANONICAL_ACCOUNTS[name].primary_group == name


def test_no_inverse_row_treats_a_primary_membership_as_an_explicit_one() -> None:
    """**EH-R8-2**, as the property rather than as a list of four names.

    R8 pinned the four offending rows in a constant and left them standing. The
    hold is gone: the assertion is now that *no* row has the shape, so a fifth
    one cannot be added either.
    """
    conflating = {
        name
        for name, group in CANONICAL_GROUPS.items()
        if any(
            account.name in group.members
            for account in CANONICAL_ACCOUNTS.values()
            if account.primary_group == name
        )
    }
    assert conflating == set()
    assert not hasattr(identity_module, "PRE_EXISTING_PRIMARY_IN_INVERSE")

    # And the case now passes for the host §2.13.3 provisions: `useradd` puts an
    # account in no explicit list, so `getent group` reports an empty fourth
    # field for every group that is only somebody's primary group.
    only_primary = sorted(
        name
        for name in CANONICAL_GROUPS
        if name in CANONICAL_ACCOUNTS and not CANONICAL_GROUPS[name].members
    )
    assert only_primary == ["fbprobe", "freedomcoord", "freedomsheet", "postgres"]
    observed = [
        classify_group_membership(ObservedGroup(name, 5000 + index, frozenset()))
        for index, name in enumerate(only_primary)
    ]
    assert all(record.status is Status.PASSED for record in observed)
    assert membership_matrix_holds(observed)

    # `discordbot` is the mixed case: one real supplementary member, and the
    # account's own name no longer beside it.
    discordbot = classify_group_membership(
        ObservedGroup("discordbot", 5100, frozenset({"freedomweb"}))
    )
    assert discordbot.status is Status.PASSED
    assert discordbot.detail["missing_members"] == ""


def test_the_table_cannot_be_edited_into_disagreement() -> None:
    """`identity.py`'s import-time guard, exercised rather than trusted.

    A membership in one half and not the other is stop condition **10p** — the
    shape of P5.0-SR2. The guard now covers the whole table, so each of the
    four ways the halves can disagree is a refusal at import.
    """
    guard = identity_module._the_two_halves_of_the_table_agree
    guard()  # the tree as it stands

    # 1. A supplementary group with no inverse row at all — the defect the
    #    missing `users` row was.
    without_inverse = {
        name: group for name, group in CANONICAL_GROUPS.items() if name != "users"
    }
    with mock.patch.object(identity_module, "CANONICAL_GROUPS", without_inverse):
        with pytest.raises(ObservationRefused) as excinfo:
            guard()
    assert "stop condition 10p" in str(excinfo.value)

    # 2. An inverse row that omits an account the identity half puts in it.
    emptied = dict(CANONICAL_GROUPS)
    emptied["ssl-cert"] = CanonicalGroup("ssl-cert", frozenset(), "emptied")
    with mock.patch.object(identity_module, "CANONICAL_GROUPS", emptied):
        with pytest.raises(ObservationRefused):
            guard()

    # 3. An explicit member no identity row states as supplementary.
    disagreeing = dict(CANONICAL_GROUPS)
    disagreeing["ssl-cert"] = CanonicalGroup(
        "ssl-cert", frozenset({"fbprobe"}), "a members list that disagrees"
    )
    with mock.patch.object(identity_module, "CANONICAL_GROUPS", disagreeing):
        with pytest.raises(ObservationRefused):
            guard()

    # 4. **The EH-R8-1 / EH-R8-2 representation, written back.** Putting an
    #    account into its own primary group's row refuses by name, for the row
    #    R8 corrected and for each of the four R9 corrected.
    for name in ("postgres", "freedomcoord", "freedomsheet", "discordbot", "fbprobe"):
        reintroduced = dict(CANONICAL_GROUPS)
        reintroduced[name] = CanonicalGroup(
            name,
            CANONICAL_GROUPS[name].members | {name},
            "the pre-R9 representation, restored",
        )
        with mock.patch.object(identity_module, "CANONICAL_GROUPS", reintroduced):
            with pytest.raises(ObservationRefused) as excinfo:
                guard()
        assert "EH-R8-2" in str(excinfo.value), name

    # 5. An explicit member that is not an account this table covers is refused
    #    rather than inferred — the R9 prompt's bar on drawing a member from the
    #    host or from outside the controlled identity table.
    outsider = dict(CANONICAL_GROUPS)
    outsider["users"] = CanonicalGroup(
        "users", frozenset({"foundry", "ubuntu"}), "an outsider beside the ruled row"
    )
    with mock.patch.object(identity_module, "CANONICAL_GROUPS", outsider):
        with pytest.raises(ObservationRefused) as excinfo:
            guard()
    assert "never" in str(excinfo.value)

    # 6. And from the identity side: a primary group also written as
    #    supplementary claims one membership in two senses.
    doubled = dict(CANONICAL_ACCOUNTS)
    doubled["fbprobe"] = CanonicalAccount(
        "fbprobe", "fbprobe", frozenset({"fbprobe"}), "/usr/sbin/nologin", True
    )
    with mock.patch.object(identity_module, "CANONICAL_ACCOUNTS", doubled):
        with pytest.raises(ObservationRefused):
            guard()


def test_a_primary_group_is_not_an_explicit_getent_group_member() -> None:
    """**EH-R8-1**, at the point the case is decided.

    `ObservedGroup.members` is the fourth field of `getent group`, which is the
    group's *explicit* member list. An account's primary membership comes from
    its passwd record and does not appear there, so a correctly configured host
    reports `postgres:x:114:` — an empty field — and that must **pass**. R7
    required the account to be listed and would have failed the case for a host
    that matches the ruling exactly.
    """
    empty = classify_group_membership(ObservedGroup("postgres", 114, frozenset()))
    assert empty.status is Status.PASSED
    assert empty.detail["missing_members"] == ""
    assert empty.detail["unexpected_members"] == ""

    # It is still an exact assertion: an account that really is listed there
    # would hold the cluster's data directory through the group, and that is a
    # finding rather than a difference to note.
    widened = classify_group_membership(
        ObservedGroup("postgres", 114, frozenset({"discordbot"}))
    )
    assert widened.status is Status.FAILED
    assert widened.detail["unexpected_members"] == "discordbot"

    # The supplementary half is unchanged, and exact in both directions.
    assert classify_group_membership(
        ObservedGroup("ssl-cert", 121, frozenset({"postgres"}))
    ).status is Status.PASSED
    assert classify_group_membership(
        ObservedGroup("ssl-cert", 121, frozenset())
    ).status is Status.FAILED
    assert classify_group_membership(
        ObservedGroup("ssl-cert", 121, frozenset({"postgres", "someone-else"}))
    ).status is Status.FAILED


def test_the_account_side_still_decides_the_primary_group() -> None:
    """The primary group is checked where it is observable — EH-R8-1 point 4.

    Removing it from the inverse relation removes nothing from the evidence:
    `id` reports the primary group, and `classify_account_identity` compares it
    against §2.12.2's identity row. A host whose `postgres` account has some
    other primary group still fails.
    """
    assert classify_account_identity(
        ObservedAccount("postgres", 114, 120, "postgres", frozenset({"ssl-cert"}))
    ).status is Status.PASSED

    for wrong in ("ssl-cert", "sudo", "discordbot"):
        moved = classify_account_identity(
            ObservedAccount("postgres", 114, 999, wrong, frozenset({"ssl-cert"}))
        )
        assert moved.status is Status.FAILED, wrong


def test_the_membership_matrix_gates_the_access_cases() -> None:
    passing = [
        classify_group_membership(ObservedGroup(name, 5000 + index, group.members))
        for index, (name, group) in enumerate(CANONICAL_GROUPS.items())
    ]
    assert membership_matrix_holds(passing)
    assert not membership_matrix_holds([])


# ---------------------------------------------------------------------------
# capability — JNL-49 / JNL-50
# ---------------------------------------------------------------------------

DECLARED_MASKS = {
    "E1": 0x0,
    "E2": 0x200,
    "E3": 0x200,
    "E4": 0x206,
    "E5": 0x208,
    "E6": 0x20E,
    "E8": 0x0,
}


@pytest.mark.parametrize("name, expected", sorted(DECLARED_MASKS.items()))
def test_every_declared_mask_is_reproduced_by_the_derivation(name: str, expected: int) -> None:
    """The revision-11 mask-versus-recipe comparison, done mechanically.

    `§2.13.5c` declares `0x0`, `0x200`, `0x200`, `0x206`, `0x208`, `0x20E`, `0x0`.
    These are the same numbers, derived from the capability sets rather than
    transcribed beside them — which is the property revision 10 lacked.
    """
    masks = EVIDENCE_IDENTITIES[name].expected_masks()
    assert set(masks.values()) == {expected, SECBITS_NO_SETUID_FIXUP} or expected == 0
    for field in ("cap_prm", "cap_eff", "cap_inh", "cap_amb", "cap_bnd"):
        assert masks[field] == expected
    assert masks["securebits"] == SECBITS_NO_SETUID_FIXUP


def test_e7s_masks_are_read_rather_than_derived() -> None:
    """And `expected_masks()` refuses to pretend otherwise — R13.

    Revision 12 returned the 2026-08-31 `/proc/1/status` reading from the same
    method that derives the other seven identities' masks from `M`, which made a
    **documented host value** indistinguishable from a derivation and available
    to anything that asked for an expectation. It is now `documented_root_masks()`
    — review material for `CAP-E7-ENVIRONMENT` — and the executor's expectation
    is `E7_TARGET_FACTS`, which ships unconfirmed.
    """
    with pytest.raises(PlanRefused):
        EVIDENCE_IDENTITIES["E7"].expected_masks()
    masks = documented_root_masks()
    assert masks["cap_prm"] == masks["cap_eff"] == masks["cap_bnd"] == DOCUMENTED_ROOT_MASK
    assert masks["cap_inh"] == masks["cap_amb"] == 0
    assert masks["securebits"] == 0

    agrees = classify_root_masks(DOCUMENTED_ROOT_MASK, DOCUMENTED_CAP_LAST_CAP)
    assert agrees.status is Status.PASSED

    other_kernel = classify_root_masks(mask_for(range(39)), 38)
    assert other_kernel.status is Status.FAILED


def test_every_evidence_identitys_groups_come_from_section_2_12_2() -> None:
    """Remediation R11-B: every group name is taken from §2.12.2 and nowhere else."""
    for identity in EVIDENCE_IDENTITIES.values():
        for group in identity.supplementary_groups:
            assert group in CANONICAL_GROUPS
        assert identity.user in CANONICAL_ACCOUNTS or identity.user == "root"


def test_e8_carries_freedomjournal_because_that_is_what_provisioning_creates() -> None:
    """Revision 11 gave `E8` `freedomcoord` only, which is not the identity
    §2.12.2 provisions."""
    assert EVIDENCE_IDENTITIES["E8"].supplementary_groups == ("freedomjournal",)
    assert CANONICAL_ACCOUNTS["freedomcoord"].supplementary == frozenset({"freedomjournal"})


def test_e1_and_e2_differ_in_exactly_one_capability_and_nothing_else() -> None:
    e1, e2 = EVIDENCE_IDENTITIES["E1"], EVIDENCE_IDENTITIES["E2"]
    assert (e1.user, e1.primary_group, e1.supplementary_groups) == (
        e2.user,
        e2.primary_group,
        e2.supplementary_groups,
    )
    assert set(e2.capability_set) - set(e1.capability_set) == {CAP_LINUX_IMMUTABLE}


def test_e4_and_e6_differ_in_exactly_cap_fowner() -> None:
    e4, e6 = EVIDENCE_IDENTITIES["E4"], EVIDENCE_IDENTITIES["E6"]
    assert set(e6.capability_set) - set(e4.capability_set) == {CAP_FOWNER}
    assert set(e4.capability_set) == {CAP_DAC_OVERRIDE, CAP_DAC_READ_SEARCH, CAP_LINUX_IMMUTABLE}


def test_the_two_control_forms_are_named_and_a_third_is_refused() -> None:
    assert control_form_for("E4", "E6") == "C-I"
    assert control_form_for("E1", "E2") == "C-I"
    assert control_form_for("E2", "E2") == "C-II"

    with pytest.raises(PlanRefused) as refusal:
        control_form_for("E4", "E2")
    assert "isolates none of them" in str(refusal.value)


#: The Option-B case-program vector the capsh construction execs — the
#: interpreter, its two isolation flags, the installed program and one verb. It
#: is written out here rather than built from the approved target because these
#: tests are about `capsh_argv`'s own arithmetic and use a different root.
CASE_PROGRAM_ARGV = (
    INTERPRETER_PATH,
    *INTERPRETER_FLAGS,
    "/var/lib/fb-evidence-r1/bin/case",
    "identity",
)


def test_the_capsh_invocation_never_asks_to_add_to_a_bounding_set() -> None:
    all_names = [f"cap_{index}" for index in range(41)]
    all_names[CAP_DAC_OVERRIDE] = "cap_dac_override"
    all_names[CAP_DAC_READ_SEARCH] = "cap_dac_read_search"
    all_names[CAP_FOWNER] = "cap_fowner"
    all_names[CAP_LINUX_IMMUTABLE] = "cap_linux_immutable"

    for name in ("E1", "E2", "E4", "E6", "E8"):
        argv = EVIDENCE_IDENTITIES[name].capsh_argv(
            case_program_argv=CASE_PROGRAM_ARGV,
            all_capability_names=all_names,
            resolve_uid=lambda user: 5001,
            resolve_gid=lambda group: 5002,
        )
        assert argv[0] == "/usr/sbin/capsh"
        assert argv[1] == f"--secbits={SECBITS_NO_SETUID_FIXUP}"
        assert any(argument.startswith("--drop=") for argument in argv)
        assert not any("--bounding-set" in argument for argument in argv)
        assert not any("keep_caps" in argument for argument in argv)
        # Conflict C-2, Option B: step 7 names the **interpreter** as the
        # program capsh execs, and the case program is an argument to it. The
        # reviewed vector is therefore the vector that runs, which is exactly
        # what a shebang would have hidden.
        assert argv[-len(CASE_PROGRAM_ARGV) - 1] == f"--shell={CASE_PROGRAM_ARGV[0]}"
        assert argv[-len(CASE_PROGRAM_ARGV)] == "--"
        assert argv[-len(CASE_PROGRAM_ARGV) + 1 :] == CASE_PROGRAM_ARGV[1:]


def test_e1_and_e8_omit_the_inheritable_and_ambient_steps() -> None:
    argv = EVIDENCE_IDENTITIES["E1"].capsh_argv(
        case_program_argv=CASE_PROGRAM_ARGV,
        all_capability_names=["cap_a", "cap_b"],
        resolve_uid=lambda user: 5001,
        resolve_gid=lambda group: 5002,
    )
    assert not any(argument.startswith("--inh=") for argument in argv)
    assert not any(argument.startswith("--addamb=") for argument in argv)


def test_e7_has_no_invocation() -> None:
    with pytest.raises(PlanRefused):
        EVIDENCE_IDENTITIES["E7"].capsh_argv(
            case_program_argv=CASE_PROGRAM_ARGV,
            all_capability_names=[],
            resolve_uid=lambda u: 0,
            resolve_gid=lambda g: 0,
        )


def test_a_capsh_construction_needs_the_whole_case_program_vector() -> None:
    """Step 7 is a vector, not a path.

    Handing `capsh_argv` a bare program path would produce `--shell=<path>` with
    an empty tail — an interactive shell, and the one thing the whole
    argument-vector discipline exists to prevent.
    """
    with pytest.raises(PlanRefused):
        EVIDENCE_IDENTITIES["E1"].capsh_argv(
            case_program_argv=("/var/lib/fb-evidence-r1/bin/case",),
            all_capability_names=["cap_a"],
            resolve_uid=lambda u: 5001,
            resolve_gid=lambda g: 5002,
        )


def test_a_short_launcher_bounding_set_makes_the_run_inconclusive() -> None:
    full = classify_launcher_bounding_set(DOCUMENTED_ROOT_MASK)
    assert full.status is Status.PASSED

    short = classify_launcher_bounding_set(
        mask_for([c for c in REQUIRED_LAUNCHER_CAPABILITIES if c != CAP_LINUX_IMMUTABLE])
    )
    assert short.status is Status.FAILED
    assert "cap_linux_immutable" in (short.observed.value or "")


def test_a_case_whose_identity_assertion_fails_is_inconclusive() -> None:
    expected = declared_identity("E2", uid=5001, gid=5001, group_ids=[5001, 5000])
    wrong = declared_identity("E1", uid=5001, gid=5001, group_ids=[5001, 5000])
    case = CapabilityCase(
        case_id="JNL-50-4",
        identity_name="E2",
        operation="FS_IOC_SETFLAGS clearing FS_IMMUTABLE_FL on the root-owned seal",
        target_path="/var/lib/fb-evidence-r1/journal/000001.seal",
        expected=Outcome.refused("EPERM"),
        inode_owner="root",
    )
    record = classify_capability_case(
        case, observed_identity=wrong, expected_identity=expected, observed=Outcome.refused("EPERM")
    )
    assert record.status is Status.INCONCLUSIVE
    assert "cap_prm" in record.reason


E4_IDENTITY = declared_identity("E4", uid=5003, gid=5003, group_ids=[5003])
E6_IDENTITY = declared_identity("E6", uid=5003, gid=5003, group_ids=[5003])


def e6_control(case_id: str = "JNL-50-7-control", *, observed: Outcome | None = None) -> EvidenceRecord:
    """The isolating control for an `E4` refusal: the same process identity plus
    `CAP_FOWNER`, clearing the flag it must be able to clear.

    Declared `CONTROL`, and its status is whatever its observation makes it. The
    default observation is the expected success, so a test that wants a failing
    control has to supply one rather than assert one.
    """
    return classify_capability_case(
        CapabilityCase(
            case_id=case_id,
            identity_name="E6",
            operation="FS_IOC_SETFLAGS clearing FS_APPEND_FL on the freedomsheet-owned journal",
            target_path="/var/lib/fb-evidence-r1/journal/000001.journal",
            expected=Outcome.returned(),
            inode_owner="freedomsheet",
            role=CaseRole.CONTROL,
        ),
        observed_identity=E6_IDENTITY,
        expected_identity=E6_IDENTITY,
        observed=Outcome.returned() if observed is None else observed,
    )


def test_a_case_naming_a_control_without_its_identity_is_refused() -> None:
    """Reaches the rule it is named for.

    The case is a complete, admissible dependent case in every other respect —
    role declared, control record supplied — so the refusal is about the missing
    `control_identity_name` and not about a second omission on the way to it.
    Without the control's identity the control *form* cannot be checked, and an
    unchecked form is how `E2` came to be named as the control for an `E4`
    refusal.
    """
    case = CapabilityCase(
        case_id="JNL-50-6",
        identity_name="E4",
        operation="FS_IOC_SETFLAGS clearing FS_IMMUTABLE_FL",
        target_path="/var/lib/fb-evidence-r1/archive/000001.journal",
        expected=Outcome.refused("EPERM"),
        control_case_id="JNL-50-6-control",
        role=CaseRole.DEPENDENT,
    )
    with pytest.raises(PlanRefused) as refusal:
        classify_capability_case(
            case,
            observed_identity=E4_IDENTITY,
            expected_identity=E4_IDENTITY,
            observed=Outcome.refused("EPERM"),
            control=e6_control("JNL-50-6-control"),
        )
    assert "the control form cannot be checked" in str(refusal.value)


def test_a_capability_case_whose_role_and_reference_disagree_is_refused() -> None:
    with pytest.raises(PlanRefused):
        CapabilityCase(
            case_id="JNL-50-7",
            identity_name="E4",
            operation="FS_IOC_SETFLAGS clearing FS_APPEND_FL",
            target_path="/var/lib/fb-evidence-r1/journal/000001.journal",
            expected=Outcome.refused("EPERM"),
            control_case_id="JNL-50-7-control",
            control_identity_name="E6",
        )
    with pytest.raises(PlanRefused):
        CapabilityCase(
            case_id="JNL-50-7-control",
            identity_name="E6",
            operation="FS_IOC_SETFLAGS clearing FS_APPEND_FL",
            target_path="/var/lib/fb-evidence-r1/journal/000001.journal",
            expected=Outcome.returned(),
            role=CaseRole.DEPENDENT,
        )


def test_the_isolating_control_for_an_e4_refusal_is_e6_and_not_e2() -> None:
    good = CapabilityCase(
        case_id="JNL-50-7",
        identity_name="E4",
        operation="FS_IOC_SETFLAGS clearing FS_APPEND_FL on the freedomsheet-owned journal",
        target_path="/var/lib/fb-evidence-r1/journal/000001.journal",
        expected=Outcome.refused("EPERM"),
        control_case_id="JNL-50-7-control",
        control_identity_name="E6",
        control_form="C-I",
        inode_owner="freedomsheet",
        role=CaseRole.DEPENDENT,
    )
    record = classify_capability_case(
        good,
        observed_identity=E4_IDENTITY,
        expected_identity=E4_IDENTITY,
        observed=Outcome.refused("EPERM"),
        control=e6_control(),
    )
    assert record.status is Status.PASSED
    assert record.detail["control_form"] == "C-I"

    bad = replace(good, control_identity_name="E2")
    with pytest.raises(PlanRefused):
        classify_capability_case(
            bad,
            observed_identity=E4_IDENTITY,
            expected_identity=E4_IDENTITY,
            observed=Outcome.refused("EPERM"),
            control=e6_control(),
        )


def test_an_e4_refusal_beside_a_control_that_did_not_clear_the_flag_is_inconclusive() -> None:
    """`E6` failing means the flag could not be cleared by an identity that holds
    every authority for it, so `E4`'s `EPERM` is not attributable to `CAP_FOWNER`.

    The control's status is read off its record, so this cannot be overridden by
    the caller of the dependent case.
    """
    failing = e6_control(observed=Outcome.refused("EPERM"))
    assert failing.status is Status.FAILED

    record = classify_capability_case(
        CapabilityCase(
            case_id="JNL-50-7",
            identity_name="E4",
            operation="FS_IOC_SETFLAGS clearing FS_APPEND_FL on the freedomsheet-owned journal",
            target_path="/var/lib/fb-evidence-r1/journal/000001.journal",
            expected=Outcome.refused("EPERM"),
            control_case_id="JNL-50-7-control",
            control_identity_name="E6",
            control_form="C-I",
            inode_owner="freedomsheet",
            role=CaseRole.DEPENDENT,
        ),
        observed_identity=E4_IDENTITY,
        expected_identity=E4_IDENTITY,
        observed=Outcome.refused("EPERM"),
        control=failing,
    )
    assert record.status is Status.INCONCLUSIVE


# ---------------------------------------------------------------------------
# filesystem — C-3 / §2.13.2a
# ---------------------------------------------------------------------------


def test_the_four_stages_carry_the_case_counts_the_section_specifies() -> None:
    assert len(STAGE_1) == 6
    assert len(STAGE_2) == 9
    assert len(STAGE_3) == 2
    assert len(STAGE_4) == 4
    assert len(ALL_CASES) == 21


def test_the_case_table_declares_a_role_for_every_case_and_checks_it() -> None:
    """The band's own contract, asserted rather than trusted.

    `filesystem` and `identity` both have a case called `C-1`, so *"it starts with
    C"* says nothing about what a case is. Every dependent case declares
    `DEPENDENT` and names exactly one control; every control declares `CONTROL`;
    every read declares `STANDALONE` and names none.
    """
    for case in ALL_CASES.values():
        names_control = case.control_case_id is not None
        assert (case.role is CaseRole.DEPENDENT) == names_control, case.case_id
        if names_control:
            assert ALL_CASES[case.control_case_id].role is CaseRole.CONTROL, case.case_id
    assert {case.case_id for case in STAGE_1} == {
        case.case_id for case in STAGE_1 if case.role is CaseRole.CONTROL
    }
    assert ALL_CASES["S4-0"].role is CaseRole.CONTROL
    assert ALL_CASES["S4-2"].control_case_id == "S4-0"


def test_a_failing_stage_one_control_makes_every_stage_two_case_inconclusive() -> None:
    """*"A probe that cannot demonstrate the positive first has no standing to
    interpret a negative."*"""
    control = classify_probe_case("C-1", Outcome.refused("EACCES"))
    assert control.status is Status.FAILED

    refused = classify_probe_case("P-1", Outcome.refused("EPERM"), control=control)
    assert refused.status is Status.INCONCLUSIVE


def test_a_stage_two_refusal_beside_its_passing_control_is_a_pass() -> None:
    control = classify_probe_case("C-1", Outcome.returned())
    assert control.status is Status.PASSED
    assert classify_probe_case("P-1", Outcome.refused("EPERM"), control=control).status is Status.PASSED


def test_eaccess_in_stage_two_is_inconclusive_and_not_a_failed_capability() -> None:
    control = classify_probe_case("C-1", Outcome.returned())
    record = classify_probe_case("P-1", Outcome.refused("EACCES"), control=control)
    assert record.status is Status.INCONCLUSIVE
    assert "mis-provisioned" in record.reason
    assert record.detail["attribution"].startswith("discretionary access control")


def test_enotty_from_getflags_is_a_failed_probe_and_not_a_passing_one() -> None:
    record = classify_probe_case("P-9", Outcome.refused("ENOTTY"))
    assert record.status is Status.FAILED
    assert "no flag interface" in record.detail["attribution"]


def test_s4_2_succeeding_is_a_failed_stage() -> None:
    control = classify_probe_case("S4-0", Outcome.returned())
    record = classify_probe_case("S4-2", Outcome.returned(), control=control)
    assert record.status is Status.FAILED
    assert "nothing benign" in record.detail["does_not_mean"]


def test_erofs_in_s4_2_without_a_passing_s4_0_attributes_nothing() -> None:
    control = classify_probe_case("S4-0", Outcome.refused("EROFS"))
    record = classify_probe_case("S4-2", Outcome.refused("EROFS"), control=control)
    assert record.status is Status.INCONCLUSIVE


def test_a_case_that_names_a_control_refuses_when_its_record_is_not_supplied() -> None:
    with pytest.raises(ObservationRefused):
        classify_probe_case("P-1", Outcome.refused("EPERM"))


def test_a_probe_case_classified_beside_the_wrong_control_is_refused() -> None:
    """`P-1`'s control is `C-1`, the case that proved the same operation permitted
    without the flag. Any other control holds different variables fixed."""
    wrong = classify_probe_case("C-2", Outcome.returned())
    with pytest.raises(ObservationRefused) as refusal:
        classify_probe_case("P-1", Outcome.refused("EPERM"), control=wrong)
    assert "was given case 'C-2'" in str(refusal.value)


def passing_probe() -> list:
    """Every case observed exactly as the section expects, classified in order.

    Controls first, then everything that is read beside one — and each dependent
    case is given the **record** its control produced, resolved out of what has
    already been classified. Nothing here selects a control status.
    """
    records: list[EvidenceRecord] = []
    by_id: dict[str, EvidenceRecord] = {}
    ordered = sorted(
        ALL_CASES.values(), key=lambda case: case.role is not CaseRole.CONTROL
    )
    for case in ordered:
        if case.case_id == "S4-3":
            # C-P5.0-R5-R1: S4-3 is a typed comparison, not a supplied outcome.
            record, _ = classify_s4_3()
        else:
            control = by_id[case.control_case_id] if case.control_case_id else None
            record = classify_probe_case(case.case_id, case.expected, control=control)
        by_id[case.case_id] = record
        records.append(record)
    return records


def test_a_fully_passing_probe_is_admissible_at_c2() -> None:
    records = passing_probe()
    assert all(stage_status(records, stage) is Status.PASSED for stage in (1, 2, 3, 4))
    admissible, reason = probe_report_admissible(records)
    assert admissible, reason


def test_a_report_missing_a_stage_is_not_admissible() -> None:
    records = [record for record in passing_probe() if ALL_CASES[record.case_id].stage != 4]
    admissible, reason = probe_report_admissible(records)
    assert not admissible
    assert "Stage 4 is not_run" in reason


def test_s4_2_cannot_pass_without_a_present_and_passing_s4_0() -> None:
    records = [
        record for record in passing_probe() if record.case_id != "S4-0"
    ]
    assert not stage_four_ordering_holds(records)
    admissible, reason = probe_report_admissible(records)
    assert not admissible


# ---------------------------------------------------------------------------
# manifest — JNL-46
# ---------------------------------------------------------------------------

ENTRIES = (
    SourceEntry("bin/migration-authority", "coordinator/bin/x", EntryClass.EXECUTABLE, "a" * 64),
    SourceEntry("unit:freedom-sheet-writer.service", "infra/systemd/x", EntryClass.REGULAR, "b" * 64),
)


def test_the_source_manifest_digest_is_order_independent_and_content_bound() -> None:
    assert source_manifest_digest(ENTRIES) == source_manifest_digest(tuple(reversed(ENTRIES)))
    changed = (ENTRIES[0], SourceEntry(ENTRIES[1].deployed_name, ENTRIES[1].source_path,
                                       ENTRIES[1].entry_class, "c" * 64))
    assert source_manifest_digest(ENTRIES) != source_manifest_digest(changed)


def test_the_two_manifest_functions_are_different_functions() -> None:
    """§2.12.5a: Git records none of uid, gid or the full permission bits, so a
    manifest computed from a Git tree cannot reproduce them."""
    deployment = (
        DeploymentEntry("/opt/freedom-blades/sheet-writer/bin/x", 0o755, 0, 0, 10, "a" * 64),
    )
    assert deployment_manifest_digest(deployment) != source_manifest_digest(ENTRIES[:1])


def test_a_duplicate_deployed_name_is_refused() -> None:
    with pytest.raises(ObservationRefused):
        source_manifest_digest((ENTRIES[0], ENTRIES[0]))


def test_an_entry_class_git_cannot_express_is_refused() -> None:
    with pytest.raises(ObservationRefused):
        SourceEntry("x", "y", "directory", "a" * 64)  # type: ignore[arg-type]
    with pytest.raises(ObservationRefused):
        SourceEntry("x", "y", EntryClass.REGULAR, "not-a-digest")


def test_the_equivalence_names_which_comparison_disagreed() -> None:
    digest = source_manifest_digest(ENTRIES)
    ok = classify_manifest_equivalence(trusted=ENTRIES, deployed=ENTRIES, approved_digest=digest)
    assert [record.status for record in ok] == [Status.PASSED, Status.PASSED]

    drifted = classify_manifest_equivalence(
        trusted=ENTRIES, deployed=ENTRIES[:1], approved_digest=digest
    )
    assert drifted[0].status is Status.PASSED
    assert drifted[1].status is Status.FAILED
    assert drifted[1].detail["refusal_code"] == "DEP-08"

    unapproved = classify_manifest_equivalence(
        trusted=ENTRIES, deployed=ENTRIES, approved_digest="f" * 64
    )
    assert unapproved[0].status is Status.FAILED
    assert unapproved[0].detail["refusal_code"] == "DEP-04"


def test_an_unaccounted_file_is_refused_by_the_closed_partition() -> None:
    """*"There is no third region … This is what stops the failure that a
    whole-tree digest cannot see: deploying the reviewed files correctly and
    adding one more."*"""
    clean = classify_partition(
        PartitionFacts(frozenset({"a"}), frozenset({"b"}), frozenset({"a", "b"}))
    )
    assert clean.status is Status.PASSED

    extra = classify_partition(
        PartitionFacts(frozenset({"a"}), frozenset({"b"}), frozenset({"a", "b", "c"}))
    )
    assert extra.status is Status.FAILED
    assert extra.detail["first_unaccounted"] == "c"

    missing = classify_partition(
        PartitionFacts(frozenset({"a"}), frozenset({"b"}), frozenset({"a"}))
    )
    assert missing.status is Status.FAILED


# ---------------------------------------------------------------------------
# provenance — JNL-51 / JNL-53
# ---------------------------------------------------------------------------

APR = ApprovedRevision(
    component="sheet_writer",
    source_commit="c" * 40,
    source_tree_id="t" * 40,
    source_manifest_digest="d" * 64,
    review_reference="phase-5-0-security-rereview-revision-12",
    approved_by="Peter Duscha",
    approved_at="2026-09-02T00:00:00Z",
    facts=FileFacts(True, "root", "root", "0444"),
)

PVR = ProvenanceRecord(
    component="sheet_writer",
    source_commit="c" * 40,
    source_tree_id="t" * 40,
    source_manifest_digest="d" * 64,
    deployment_manifest_digest="e" * 64,
    dependency_lock_digest="f" * 64,
    deployed_at="2026-09-02T01:00:00Z",
    deployed_by="root",
    facts=FileFacts(True, "root", "root", "0444"),
)


def test_the_missing_provenance_case_refuses_and_creates_nothing() -> None:
    """`JNL-51` case (g): the negative test P5.0-SR1 requires."""
    records = classify_missing_provenance(
        apr=None,
        pvr=None,
        probe_ran=False,
        generation_artifacts=(),
        generation_row_inserted=False,
        observed_refusal_code="J-26",
    )
    assert [record.status for record in records] == [Status.PASSED] * 4
    assert records[0].detail["refusal_code"] == "J-26"
    assert records[0].detail["observed_refusal_code"] == "J-26"


def test_a_present_provenance_record_makes_the_omission_case_fail() -> None:
    """The case asserts an omission. If nothing was omitted it must not pass, or
    the test would report a refusal nobody triggered.

    **R16, EH-R16-2.** The observed refusal is the expected one here, and the
    record still fails: the precondition is what did not hold, and a refusal
    observed in a run where nothing was omitted is a refusal for another reason.
    """
    records = classify_missing_provenance(
        apr=APR,
        pvr=PVR,
        probe_ran=False,
        generation_artifacts=(),
        generation_row_inserted=False,
        observed_refusal_code="J-26",
    )
    assert records[0].status is Status.FAILED
    assert records[0].detail["precondition_holds"] == "no"


def test_a_generation_artifact_surviving_the_refusal_fails_the_case() -> None:
    records = classify_missing_provenance(
        apr=None,
        pvr=None,
        probe_ran=True,
        generation_artifacts=("/var/lib/fb-evidence-r1/journal/000001.journal",),
        generation_row_inserted=True,
        observed_refusal_code="J-26",
    )
    assert records[1].status is Status.FAILED
    assert records[2].status is Status.FAILED
    assert records[3].status is Status.FAILED


def test_the_four_way_provenance_comparison_names_the_source_that_disagreed() -> None:
    agreeing = classify_provenance_agreement(
        apr=APR,
        pvr=PVR,
        trusted_manifest_digest="d" * 64,
        deployed_manifest_digest="d" * 64,
        deployment_digest="e" * 64,
        approved_source_revision_row=True,
    )
    assert all(record.status is Status.PASSED for record in agreeing)

    no_row = classify_provenance_agreement(
        apr=APR,
        pvr=PVR,
        trusted_manifest_digest="d" * 64,
        deployed_manifest_digest="d" * 64,
        deployment_digest="e" * 64,
        approved_source_revision_row=False,
    )
    failed = [record for record in no_row if record.status is Status.FAILED]
    assert [record.detail["refusal_code"] for record in failed] == ["J-28"]

    drifted = classify_provenance_agreement(
        apr=APR,
        pvr=PVR,
        trusted_manifest_digest="d" * 64,
        deployed_manifest_digest="9" * 64,
        deployment_digest="e" * 64,
        approved_source_revision_row=True,
    )
    failed = [record for record in drifted if record.status is Status.FAILED]
    assert [record.detail["refusal_code"] for record in failed] == ["SW-J27"]


def test_an_apr_that_is_not_root_owned_read_only_is_reported() -> None:
    loose = replace(APR, facts=FileFacts(True, "foundry", "foundry", "0644"))
    records = classify_provenance_agreement(
        apr=loose,
        pvr=PVR,
        trusted_manifest_digest="d" * 64,
        deployed_manifest_digest="d" * 64,
        deployment_digest="e" * 64,
        approved_source_revision_row=True,
    )
    assert records[0].status is Status.FAILED
    assert "R-5.0-15" in records[0].detail["residual"]


def test_the_deploy_path_reads_no_file_in_the_group_writable_worktree() -> None:
    clean = classify_worktree_isolation(
        (
            "/opt/freedom-blades/coordinator/source.git/objects/xx",
            "/etc/freedom-blades/approved-source-revision",
        )
    )
    assert clean.status is Status.PASSED

    dirty = classify_worktree_isolation(("/opt/freedom-blades/platform/tools/x.py",))
    assert dirty.status is Status.FAILED
    assert dirty.detail["first_offending_path"] == "/opt/freedom-blades/platform/tools/x.py"


# ---------------------------------------------------------------------------
# journal — P5.0-R5
# ---------------------------------------------------------------------------

#: The generation classifier's tests moved to `test_r5_r1_journal_classifier.py`
#: under C-P5.0-R5-R1. The ones that stood here encoded the harness's own
#: five-condition table rather than §2.13.6, which is how the four contradictions
#: in the P5.0-R5 reconciliation handback §3.13 passed.


def test_the_recovery_procedure_is_operator_run_and_leaves_no_residue() -> None:
    done = classify_recovery([step.order for step in RECOVERY_PROCEDURE], residue_after=())
    assert done.status is Status.PASSED

    incomplete = classify_recovery([1, 2], residue_after=("/var/lib/fb-evidence-r1/probe",))
    assert incomplete.status is Status.FAILED
    assert incomplete.detail["first_remaining"] == "/var/lib/fb-evidence-r1/probe"
