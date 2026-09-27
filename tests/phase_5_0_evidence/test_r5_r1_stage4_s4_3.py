"""C-P5.0-R5-R1, part B — §2.13.2a S4-3 and the four security-review conditions.

Security review rev 11, *"Stage 4 remains conditional"*: S4-3 must (1) parse a
closed allowlist of supported unit directives and drop-ins, (2) reject duplicate
or unknown authority-bearing directives including in drop-ins, (3) construct the
substituted `ReadWritePaths=` from the internally fixed canonical probe path,
and (4) compare the complete normalized applied property set, with the evidence
invalidated by a systemd/package upgrade even when deployed bytes are unchanged.

§2.13.2a: *"A mismatch is `inconclusive`"*. So every negative here must be
`INCONCLUSIVE` — never `PASSED`, and not `FAILED` either.
"""
from __future__ import annotations

import dataclasses
import inspect

import pytest

from tools.phase_5_0_evidence import unit_sandbox
from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.errors import ObservationRefused
from tools.phase_5_0_evidence.filesystem import (
    classify_probe_case,
    probe_report_admissible,
)
from tools.phase_5_0_evidence.records import Outcome, Status
from tools.phase_5_0_evidence.unit_sandbox import (
    CANONICAL_PROBE_PATH,
    UnitFile,
    expected_applied_properties,
    revalidate_sandbox_attestation,
)
from tests.phase_5_0_evidence.unit_sandbox_fixtures import (
    APPLIED_LINES,
    DESIGN_UNIT_TEXT,
    PROBE,
    SYSTEMD,
    applied_show,
    classify,
    unit,
)


def with_line(after: str, line: str) -> str:
    return DESIGN_UNIT_TEXT.replace(after + "\n", after + "\n" + line + "\n", 1)


def without_line(line: str) -> str:
    assert line + "\n" in DESIGN_UNIT_TEXT
    return DESIGN_UNIT_TEXT.replace(line + "\n", "", 1)


# ---------------------------------------------------------------------------
# The valid case
# ---------------------------------------------------------------------------


def test_the_design_unit_with_its_substitution_passes_and_is_attested() -> None:
    record, attestation = classify()
    assert record.status is Status.PASSED, record.reason
    assert attestation is not None
    assert attestation.substitution == PROBE
    assert attestation.systemd == SYSTEMD
    assert record.detail["applied_property_digest"] == attestation.applied_property_digest
    assert dict(attestation.applied_properties) == {
        **APPLIED_LINES,
        "NoNewPrivileges": "yes",
    }


def test_normalization_admits_equivalent_spellings_and_any_line_order() -> None:
    text = DESIGN_UNIT_TEXT.replace("NoNewPrivileges=true", "NoNewPrivileges=1").replace(
        "PrivateTmp=true", "PrivateTmp=on"
    )
    show = "\n".join(reversed(applied_show().splitlines()))
    record, _ = classify(unit(text), show=show)
    assert record.status is Status.PASSED, record.reason


def test_a_repeated_lifecycle_directive_is_not_an_authority_duplicate() -> None:
    record, _ = classify(unit(with_line("After=network-online.target", "After=local-fs.target")))
    assert record.status is Status.PASSED, record.reason


# ---------------------------------------------------------------------------
# Every negative is inconclusive
# ---------------------------------------------------------------------------

HOSTILE_DROP_IN = UnitFile("zz-override.conf", "[Service]\nNoNewPrivileges=false\n")

NEGATIVES = {
    # Condition 1 — the closed grammar and allowlist.
    "unknown-directive": dict(deployed=unit(with_line("Group=freedomsheet",
                                                       "SupplementaryGroups=freedomjournal"))),
    "unknown-exec-hook": dict(deployed=unit(with_line("Type=simple", "ExecStartPre=+/bin/sh -c id"))),
    "unknown-section": dict(deployed=unit(DESIGN_UNIT_TEXT + "[X-Override]\nUser=root\n")),
    "directive-in-wrong-section": dict(deployed=unit(DESIGN_UNIT_TEXT.replace(
        "[Install]\n", "[Install]\nUser=root\n"))),
    "continuation-line": dict(deployed=unit(DESIGN_UNIT_TEXT.replace(
        "ReadOnlyPaths=/var/lib/freedom-sheet-writer",
        "ReadOnlyPaths=/var/lib/freedom-sheet-writer \\\n  /etc"))),
    "specifier": dict(deployed=unit(DESIGN_UNIT_TEXT.replace(
        "ReadOnlyPaths=/var/lib/freedom-sheet-writer", "ReadOnlyPaths=%S/freedom-sheet-writer"))),
    "capability-inversion": dict(deployed=unit(DESIGN_UNIT_TEXT.replace(
        "CapabilityBoundingSet=\n", "CapabilityBoundingSet=~cap_sys_admin\n"))),
    "missing-sandbox-directive": dict(deployed=unit(without_line("NoNewPrivileges=true"))),
    "wrong-unit-name": dict(deployed=dataclasses.replace(
        unit(), unit=UnitFile("other.service", DESIGN_UNIT_TEXT))),
    # Condition 2 — duplicates, in the unit and through drop-ins.
    "duplicate-in-unit": dict(deployed=unit(with_line("ProtectSystem=strict", "ProtectSystem=full"))),
    "duplicate-exec": dict(deployed=unit(with_line("Type=simple", "ExecStart=/bin/true"))),
    "reset-by-empty-assignment": dict(deployed=unit(with_line(
        "ReadWritePaths=/var/lib/freedom-sheet-writer/journal", "ReadWritePaths="))),
    "hostile-drop-in": dict(deployed=unit(DESIGN_UNIT_TEXT, HOSTILE_DROP_IN)),
    "extra-benign-drop-in": dict(deployed=unit(DESIGN_UNIT_TEXT,
                                               UnitFile("10-doc.conf", "[Unit]\nDescription=x\n"))),
    "drop-in-adds-authority": dict(deployed=unit(DESIGN_UNIT_TEXT,
                                                 UnitFile("50-groups.conf",
                                                          "[Service]\nAmbientCapabilities=cap_fowner\n"))),
    # The supplied text is not the deployed text.
    "text-not-the-recorded-bytes": dict(deployed=unit(DESIGN_UNIT_TEXT.replace(
        "ProtectHome=true", "ProtectHome=false")), recorded_unit_digest=unit().digest()),
    # Condition 3 — the substitution comes from nowhere but the module.
    "recorded-substitution-probe-ro": dict(recorded_substitution=PROBE + "-ro"),
    "recorded-substitution-deployed-path": dict(
        recorded_substitution="/var/lib/freedom-sheet-writer/journal"),
    "applied-substitution-probe-ro": dict(show=applied_show(ReadWritePaths=PROBE + "-ro")),
    "applied-substitution-widened": dict(show=applied_show(ReadWritePaths=f"{PROBE} {PROBE}-ro")),
    "applied-deployed-path-unsubstituted": dict(
        show=applied_show(ReadWritePaths="/var/lib/freedom-sheet-writer/journal")),
    # Condition 4 — the complete normalized applied set.
    "omitted-property": dict(show=applied_show(ProtectProc=None)),
    "duplicated-property": dict(show=applied_show() + "ProtectSystem=strict\n"),
    "unrequested-property": dict(show=applied_show() + "SupplementaryGroups=freedomjournal\n"),
    "interpreted-differently-boolean": dict(show=applied_show(NoNewPrivileges="no")),
    "interpreted-differently-capabilities": dict(
        show=applied_show(CapabilityBoundingSet="cap_linux_immutable")),
    "interpreted-differently-protect-system": dict(show=applied_show(ProtectSystem="full")),
    "malformed-applied-value": dict(show=applied_show(User="free domsheet")),
}


@pytest.mark.parametrize("kwargs", NEGATIVES.values(), ids=NEGATIVES.keys())
def test_every_negative_is_inconclusive_and_never_passed(kwargs) -> None:
    record, attestation = classify(**kwargs)
    assert record.status is Status.INCONCLUSIVE, record.reason
    assert attestation is None
    assert record.detail["refusal_count"] >= 1


@pytest.mark.parametrize(
    "deployed, fragment",
    [
        (NEGATIVES["unknown-directive"]["deployed"], "unknown directive SupplementaryGroups="),
        (NEGATIVES["duplicate-in-unit"]["deployed"], "duplicate authority-bearing ProtectSystem="),
        (NEGATIVES["hostile-drop-in"]["deployed"], "not in the supported drop-in allowlist"),
        (NEGATIVES["hostile-drop-in"]["deployed"], "duplicate authority-bearing NoNewPrivileges="),
        (NEGATIVES["drop-in-adds-authority"]["deployed"],
         "duplicate authority-bearing AmbientCapabilities="),
        (NEGATIVES["missing-sandbox-directive"]["deployed"], "does not assign NoNewPrivileges="),
    ],
    ids=["unknown", "duplicate", "drop-in-name", "drop-in-duplicate", "drop-in-authority",
         "missing"],
)
def test_the_parse_names_each_reason(deployed, fragment) -> None:
    parsed = unit_sandbox.parse_deployed_unit(deployed)
    assert any(fragment in refusal for refusal in parsed.refusals), parsed.refusals


def test_no_drop_in_is_supported_because_the_design_names_none() -> None:
    assert unit_sandbox.SUPPORTED_DROP_INS == frozenset()


# ---------------------------------------------------------------------------
# Condition 3, structurally
# ---------------------------------------------------------------------------


def test_the_canonical_probe_path_is_the_approved_targets_arena() -> None:
    assert CANONICAL_PROBE_PATH == f"{APPROVED_TARGET.root_path}/probe" == PROBE


def test_no_function_accepts_a_replacement_substitution_path() -> None:
    assert list(inspect.signature(expected_applied_properties).parameters) == ["parsed"]
    parameters = inspect.signature(unit_sandbox.classify_sandbox_attestation).parameters
    # `recorded_substitution` is compared against the canonical path, never used.
    assert set(parameters) == {
        "deployed", "recorded_unit_digest", "recorded_substitution", "applied_show", "systemd",
    }


def test_the_deployed_read_write_paths_never_reaches_the_expected_set() -> None:
    parsed = unit_sandbox.parse_deployed_unit(unit())
    expected = dict(expected_applied_properties(parsed))
    assert expected["ReadWritePaths"] == CANONICAL_PROBE_PATH
    assert "/var/lib/freedom-sheet-writer/journal" not in expected.values()


# ---------------------------------------------------------------------------
# Condition 4, invalidation
# ---------------------------------------------------------------------------


def test_an_unchanged_host_revalidates() -> None:
    _, attestation = classify()
    status, _ = revalidate_sandbox_attestation(attestation, systemd=SYSTEMD, applied_show=applied_show())
    assert status is Status.PASSED


@pytest.mark.parametrize(
    "field, value",
    [("package_version", "259.2-1ubuntu1"), ("systemd_version", "260"), ("package", "systemd-alt")],
)
def test_a_systemd_identity_change_invalidates_even_with_unchanged_bytes(field, value) -> None:
    _, attestation = classify()
    upgraded = dataclasses.replace(SYSTEMD, **{field: value})
    # Same deployed unit, same applied set: only the interpreter changed.
    status, reason = revalidate_sandbox_attestation(
        attestation, systemd=upgraded, applied_show=applied_show()
    )
    assert status is Status.INCONCLUSIVE
    assert reason.startswith("invalidated")
    assert "unchanged deployed unit does not carry the attestation" in reason


def test_a_changed_interpretation_under_the_same_identity_invalidates() -> None:
    _, attestation = classify()
    status, reason = revalidate_sandbox_attestation(
        attestation, systemd=SYSTEMD, applied_show=applied_show(ProtectHome="read-only")
    )
    assert status is Status.INCONCLUSIVE and "ProtectHome" in reason


def test_a_systemd_identity_is_one_token_per_field() -> None:
    with pytest.raises(ObservationRefused):
        dataclasses.replace(SYSTEMD, package_version="259 1")


# ---------------------------------------------------------------------------
# The old route is closed, and the probe report sees the result
# ---------------------------------------------------------------------------


def test_s4_3_cannot_be_classified_from_a_supplied_outcome() -> None:
    from tools.phase_5_0_evidence.filesystem import ALL_CASES

    with pytest.raises(ObservationRefused):
        classify_probe_case("S4-3", ALL_CASES["S4-3"].expected)
    with pytest.raises(ObservationRefused):
        classify_probe_case("S4-3", Outcome.read("anything"))


def test_an_inconclusive_s4_3_makes_the_probe_report_inadmissible() -> None:
    from tests.phase_5_0_evidence.test_bands import passing_probe

    records = [r for r in passing_probe() if r.case_id != "S4-3"]
    bad, _ = classify(show=applied_show(NoNewPrivileges="no"))
    admissible, reason = probe_report_admissible([*records, bad])
    assert not admissible and "Stage 4 is inconclusive" in reason


def test_the_current_plans_two_property_capture_cannot_pass_s4_3() -> None:
    """The concrete plan's S4-3 vector still asks for two properties. Until it
    carries the complete set, the classifier refuses what it can produce."""
    from tools.phase_5_0_evidence.capture import CapturePolicy
    from tools.phase_5_0_evidence.concrete_plan import (
        TRANSIENT_UNIT,
        build_concrete_plan,
    )

    # C-P5.0-R5-R2: the capture step no longer claims S4-3 (it is declared
    # unresolved under C-S4-3), so it is found by what it runs.
    step = next(
        s
        for s in build_concrete_plan().steps
        if s.capture is CapturePolicy.UNIT_DIRECTIVES
        and s.argv[-1] == TRANSIENT_UNIT
        and "--property=ReadWritePaths" in s.argv
    )
    asked = [arg.split("=", 1)[1] for arg in step.argv if arg.startswith("--property=")]
    assert set(asked) < set(unit_sandbox.COMPARED_PROPERTIES)
    show = "".join(f"{name}={APPLIED_LINES[name]}\n" for name in asked)
    record, _ = classify(show=show)
    assert record.status is Status.INCONCLUSIVE
    # And the substitution the plan applies is the canonical one.
    run = next(s for s in build_concrete_plan().steps if "S4-2" in s.evidence_case_ids)
    assert f"--property=ReadWritePaths={CANONICAL_PROBE_PATH}" in run.argv
