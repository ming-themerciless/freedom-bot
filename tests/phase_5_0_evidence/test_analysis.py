"""C-1's `sudoers` analysis and the `pg_hba` / `pg_ident` ordering analysis.

Both work on text an authorized reader supplies. Neither opens a file, and both
are asserted here against synthetic content, so nothing in this suite depends on
`/etc/sudoers.d` or a PostgreSQL configuration being readable — which they are
not, and which is the whole reason C-1 is still open.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.errors import ObservationRefused
from tools.phase_5_0_evidence.hba import (
    COORDINATOR_ROLE,
    analyse_hba,
    analyse_ident,
    parse_hba,
    parse_ident,
)
from tools.phase_5_0_evidence.sudoers import (
    SudoersFileFacts,
    analyse_sudoers_drop_in,
    summarize_c1,
)

PRODUCTION_DB = "fb_evidence_r1"

CORRECT_HBA = f"""
# TYPE       DATABASE        USER                            ADDRESS  METHOD  OPTIONS
local        {PRODUCTION_DB}  {COORDINATOR_ROLE}                       peer    map=freedom_coord
local        all             {COORDINATOR_ROLE}                        reject
host         all             {COORDINATOR_ROLE}              all      reject
hostssl      all             {COORDINATOR_ROLE}              all      reject
hostnossl    all             {COORDINATOR_ROLE}              all      reject
local        all             all                                      peer
"""

CORRECT_IDENT = """
# MAPNAME        SYSTEM-USERNAME    PG-USERNAME
freedom_coord    freedomcoord       freedom_migration_coordinator
"""


def test_the_specified_ordering_holds_and_reports_nothing() -> None:
    analysis = analyse_hba(CORRECT_HBA, production_database=PRODUCTION_DB)
    assert analysis.ordering_holds
    assert analysis.findings == ()
    assert analysis.coordinator_peer_index == 0
    assert len(analysis.content_sha256) == 64


def test_a_broad_rule_above_the_peer_line_defeats_the_ordering_control() -> None:
    analysis = analyse_hba(
        "local all all trust\n" + CORRECT_HBA, production_database=PRODUCTION_DB
    )
    assert not analysis.ordering_holds
    codes = {finding.code for finding in analysis.findings}
    assert "HBA-B1" in codes and "HBA-B2" in codes
    offending = next(f for f in analysis.findings if f.code == "HBA-B1")
    assert offending.line_index == 0
    assert offending.match_class == "local all all trust"


def test_a_broad_rule_below_the_peer_line_is_reported_but_not_blocking_ordering() -> None:
    analysis = analyse_hba(
        CORRECT_HBA + "local all all md5\n", production_database=PRODUCTION_DB
    )
    assert analysis.ordering_holds
    assert {finding.code for finding in analysis.findings} == {"HBA-W1"}


def test_the_absent_peer_line_is_the_expected_pre_change_state() -> None:
    analysis = analyse_hba("local all all peer\n", production_database=PRODUCTION_DB)
    assert analysis.coordinator_peer_index is None
    assert {finding.code for finding in analysis.findings} == {"HBA-B1", "HBA-B3"}


@pytest.mark.parametrize("missing", ["host", "hostssl", "hostnossl", "local"])
def test_a_missing_reject_line_is_reported(missing: str) -> None:
    text = "\n".join(
        line
        for line in CORRECT_HBA.splitlines()
        if not (line.startswith(missing + " ") and "reject" in line)
    )
    analysis = analyse_hba(text, production_database=PRODUCTION_DB)
    assert any(finding.code == "HBA-B4" for finding in analysis.findings)


def test_an_include_directive_refuses_rather_than_reporting_a_clean_order() -> None:
    with pytest.raises(ObservationRefused) as refusal:
        parse_hba("include_dir conf.d\n" + CORRECT_HBA)
    assert "no ordering conclusion" in str(refusal.value)


def test_an_unclassifiable_line_refuses_rather_than_being_skipped() -> None:
    with pytest.raises(ObservationRefused):
        parse_hba("weird all all peer\n")
    with pytest.raises(ObservationRefused):
        parse_hba("local all\n")


def test_no_evidence_finding_carries_an_address_or_an_option_string() -> None:
    analysis = analyse_hba(
        "host all all 10.0.0.0/8 md5 clientcert=verify-full\n" + CORRECT_HBA,
        production_database=PRODUCTION_DB,
    )
    rendered = " ".join(
        f"{finding.code} {finding.match_class} {finding.detail}"
        for finding in analysis.findings
    )
    assert "10.0.0.0" not in rendered
    assert "clientcert" not in rendered


def test_the_identity_map_must_be_one_literal_line() -> None:
    assert analyse_ident(CORRECT_IDENT).mapping_is_exact

    regex = analyse_ident("freedom_coord /^(.*)$ freedom_migration_coordinator")
    assert {f.code for f in regex.findings} == {"IDENT-B2", "IDENT-B3"}

    two = analyse_ident(CORRECT_IDENT + "freedom_coord otheruser freedom_migration_coordinator\n")
    assert {f.code for f in two.findings} >= {"IDENT-B3", "IDENT-B5"}

    second_map = analyse_ident(
        CORRECT_IDENT + "other_map someone freedom_migration_coordinator\n"
    )
    assert "IDENT-B1" in {f.code for f in second_map.findings}


def test_an_identity_map_line_without_three_fields_refuses() -> None:
    with pytest.raises(ObservationRefused):
        parse_ident("freedom_coord freedomcoord\n")


# ---------------------------------------------------------------------------
# C-1
# ---------------------------------------------------------------------------

PACKAGE_FACTS = SudoersFileFacts(
    name="freedom-migration-coordinator",
    owner="root",
    group="root",
    mode="0440",
    byte_count=320,
)

CORRECT_DROP_IN = """
Cmnd_Alias FREEDOM_MIGRATION_AUTHORITY = /opt/freedom-blades/coordinator/bin/migration-authority
Defaults!FREEDOM_MIGRATION_AUTHORITY env_reset, !setenv, log_output, \\
    secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
foundry ALL=(freedomcoord:freedomcoord) FREEDOM_MIGRATION_AUTHORITY
"""


def test_the_specified_drop_in_is_safe() -> None:
    analysis = analyse_sudoers_drop_in(PACKAGE_FACTS, CORRECT_DROP_IN, is_package_drop_in=True)
    assert analysis.is_safe
    assert analysis.rule_count == 1
    assert len(analysis.content_sha256) == 64


def test_nopasswd_is_refused_because_an_authority_cutover_reauthenticates() -> None:
    analysis = analyse_sudoers_drop_in(
        PACKAGE_FACTS,
        CORRECT_DROP_IN.replace(") FREEDOM", ") NOPASSWD: FREEDOM"),
        is_package_drop_in=True,
    )
    assert {finding.code for finding in analysis.findings} == {"SUDO-B4"}


def test_a_wildcard_in_the_permitted_command_is_refused() -> None:
    analysis = analyse_sudoers_drop_in(
        PACKAGE_FACTS,
        CORRECT_DROP_IN.replace("migration-authority", "migration-*"),
        is_package_drop_in=True,
    )
    assert "SUDO-B6" in {finding.code for finding in analysis.findings}


@pytest.mark.parametrize("default", ["env_reset", "!setenv", "log_output", "secure_path="])
def test_a_missing_required_default_is_reported(default: str) -> None:
    analysis = analyse_sudoers_drop_in(
        PACKAGE_FACTS, CORRECT_DROP_IN.replace(default, ""), is_package_drop_in=True
    )
    assert "SUDO-B9" in {finding.code for finding in analysis.findings}


def test_a_wrongly_owned_or_moded_drop_in_is_reported() -> None:
    analysis = analyse_sudoers_drop_in(
        SudoersFileFacts(name="d", owner="foundry", group="foundry", mode="0644", byte_count=1),
        CORRECT_DROP_IN,
        is_package_drop_in=True,
    )
    assert {"SUDO-B1", "SUDO-B2"} <= {finding.code for finding in analysis.findings}


def test_c1_finds_an_unrelated_drop_in_that_widens_the_authority() -> None:
    """§2.12.6: *"Whether some other rule in `/etc/sudoers.d/` widens it is check
    C-1, still not run."* This is that check, over content it is handed."""
    unrelated = analyse_sudoers_drop_in(
        SudoersFileFacts(name="90-ops", owner="root", group="root", mode="0440", byte_count=40),
        "discordbot ALL=(ALL) NOPASSWD: ALL\n",
        is_package_drop_in=False,
    )
    assert unrelated.grants_to_service_identity
    assert unrelated.permits_unrestricted_command
    codes = {finding.code for finding in unrelated.findings}
    assert {"SUDO-B3", "SUDO-B4", "SUDO-B5"} <= codes

    assert len(summarize_c1([unrelated])) == len(unrelated.blocking_findings)


def test_no_c1_finding_reproduces_a_rule_from_the_file() -> None:
    """The finding names the drop-in and the class of the rule. The reviewer who
    can read the file reads the file; nothing under `docs/review/` copies it."""
    unrelated = analyse_sudoers_drop_in(
        SudoersFileFacts(name="90-ops", owner="root", group="root", mode="0440", byte_count=40),
        "operator ALL=(ALL) NOPASSWD: /usr/bin/secret-tool --token abc123\n",
        is_package_drop_in=False,
    )
    rendered = " ".join(f"{f.code} {f.drop_in} {f.detail}" for f in unrelated.findings)
    assert "abc123" not in rendered
    assert "secret-tool" not in rendered
    assert "operator" not in rendered


def test_a_mode_that_is_not_octal_is_refused() -> None:
    with pytest.raises(ObservationRefused):
        SudoersFileFacts(name="d", owner="root", group="root", mode="rw-r-----", byte_count=1)
