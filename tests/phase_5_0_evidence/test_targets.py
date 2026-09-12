"""The disposable-target guards, proved against synthetic paths.

Every path below is synthetic — none is a target this harness has been given — so
these tests fail the same way on a clean checkout as on a dirty one. That is the
N-30 property the repository's own scope guard learned: a guard demonstrated only
by *"the current input happens to pass"* has been shown to run, not to be capable
of failing.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.errors import TargetRefused
from tools.phase_5_0_evidence.targets import (
    DisposableTarget,
    FORBIDDEN_DATABASES,
    REPOSITORY_ROOT,
    UNASSIGNED,
    validate_absolute_path,
    validate_account_name,
    validate_database_name,
    validate_mutation_root,
    validate_postgres_config_directory,
)


def target(**overrides) -> DisposableTarget:
    base = dict(
        host="fb-evidence-host-1",
        root_path="/var/lib/fb-evidence-r1",
        database_name="fb_evidence_r1",
        postgres_socket_directory="/var/run/postgresql",
        confirmed_disposable=True,
        disposability_evidence="Named by the Operations Owner on 2026-09-02.",
        postgres_config_directory="/etc/postgresql/17/fbevidence",
    )
    base.update(overrides)
    return DisposableTarget(**base)


REFUSED_ROOTS = [
    ("the filesystem root", "/"),
    ("a one-level system path", "/etc"),
    ("the /var/lib parent", "/var/lib"),
    ("an ancestor of a forbidden path", "/opt/freedom-blades"),
    ("the repository worktree", REPOSITORY_ROOT),
    ("inside the repository worktree", f"{REPOSITORY_ROOT}/tools/fb-evidence-x"),
    ("the production journal hierarchy", "/var/lib/freedom-sheet-writer"),
    ("the coordinator deployment root", "/opt/freedom-blades/coordinator"),
    ("a tmpfs root", "/run/fb-evidence-x"),
    ("shared scratch", "/tmp/fb-evidence-x"),
    ("a relative path", "var/lib/fb-evidence-x"),
    ("a path with a relative segment", "/var/lib/../lib/fb-evidence-x"),
    ("an unresolved variable", "/var/lib/$EVIDENCE_ROOT"),
    ("a braced variable", "/var/lib/${EVIDENCE_ROOT}"),
    ("a glob", "/var/lib/fb-evidence-*"),
    ("a shell metacharacter", "/var/lib/fb-evidence-a;rm"),
    ("a newline", "/var/lib/fb-evidence-a\nb"),
    ("a home reference", "~/fb-evidence-x"),
    ("a shallow path", "/fb-evidence-x"),
    ("a leaf without the evidence prefix", "/var/lib/journal-probe"),
    ("surrounding whitespace", " /var/lib/fb-evidence-x "),
]


@pytest.mark.parametrize("label, path", REFUSED_ROOTS, ids=[r[0] for r in REFUSED_ROOTS])
def test_a_mutation_root_that_is_not_disposable_is_refused(label: str, path: str) -> None:
    with pytest.raises(TargetRefused):
        validate_mutation_root(path)


def test_an_admissible_mutation_root_is_accepted() -> None:
    assert validate_mutation_root("/var/lib/fb-evidence-r1") == "/var/lib/fb-evidence-r1"
    assert validate_mutation_root("/srv/data/fb-evidence-2026-09-02") == (
        "/srv/data/fb-evidence-2026-09-02"
    )


@pytest.mark.parametrize("name", sorted(FORBIDDEN_DATABASES))
def test_a_production_or_shared_database_name_is_refused(name: str) -> None:
    with pytest.raises(TargetRefused):
        validate_database_name(name)


@pytest.mark.parametrize(
    "name", ["evidence", "FBEvidence", "fb-evidence-1", "fb_evidence_1; drop", ""]
)
def test_a_database_name_outside_the_evidence_convention_is_refused(name: str) -> None:
    with pytest.raises(TargetRefused):
        validate_database_name(name)


def test_an_evidence_database_name_is_accepted() -> None:
    assert validate_database_name("fb_evidence_r1") == "fb_evidence_r1"


@pytest.mark.parametrize(
    "name", ["root", "postgres", "discordbot", "freedomweb", "foundry", "sudo"]
)
def test_an_existing_host_identity_cannot_be_named_as_a_harness_account(name: str) -> None:
    with pytest.raises(TargetRefused):
        validate_account_name(name)


@pytest.mark.parametrize("name", ["freedomcoord", "freedomsheet", "fbprobe", "freedomjournal"])
def test_the_four_provisioned_identities_are_accepted(name: str) -> None:
    assert validate_account_name(name) == name


def test_an_unassigned_target_refuses_every_mutation_bearing_use() -> None:
    unassigned = DisposableTarget.unassigned()
    assert unassigned.is_unassigned
    assert unassigned.identity == UNASSIGNED
    with pytest.raises(TargetRefused) as refusal:
        unassigned.require_mutable()
    assert "inventing a target is a stop condition" in str(refusal.value)


def test_a_named_but_unconfirmed_target_still_refuses() -> None:
    named = target(confirmed_disposable=False, disposability_evidence="")
    assert not named.is_unassigned
    with pytest.raises(TargetRefused) as refusal:
        named.require_mutable()
    assert "not confirmed disposable" in str(refusal.value)


def test_confirming_a_target_without_stating_why_is_refused() -> None:
    with pytest.raises(TargetRefused) as refusal:
        target(disposability_evidence="")
    assert "the shape of an assumption" in str(refusal.value)


def test_a_contained_path_must_be_strictly_inside_the_root() -> None:
    subject = target()
    assert subject.contained_path("/var/lib/fb-evidence-r1/journal") == (
        "/var/lib/fb-evidence-r1/journal"
    )
    for outside in (
        "/var/lib/fb-evidence-r1",
        "/var/lib/fb-evidence-r2/journal",
        "/var/lib/freedom-sheet-writer/journal",
        "/etc/passwd",
    ):
        with pytest.raises(TargetRefused):
            subject.contained_path(outside)


def test_only_the_two_postgresql_configuration_files_can_be_written() -> None:
    subject = target()
    assert subject.config_path("pg_hba.conf").endswith("/pg_hba.conf")
    assert subject.config_path("pg_ident.conf").endswith("/pg_ident.conf")
    for other in ("postgresql.conf", "pg_hba.conf.bak", "../../passwd"):
        with pytest.raises(TargetRefused):
            subject.config_path(other)


def test_a_configuration_directory_that_is_not_postgresqls_is_refused() -> None:
    for path in ("/etc/cron.d", "/etc", "/opt/freedom-blades/platform/etc", "/var/lib"):
        with pytest.raises(TargetRefused):
            validate_postgres_config_directory(path)


def test_a_configuration_directory_is_unassigned_until_it_is_named() -> None:
    subject = target(postgres_config_directory=UNASSIGNED)
    with pytest.raises(TargetRefused) as refusal:
        subject.config_path("pg_hba.conf")
    assert "has not been named" in str(refusal.value)


# ---------------------------------------------------------------------------
# C-1 — the ruled target-root boundary
#
# Peter Duscha accepted Codex's recommendation on 2026-09-06 (package plan
# §2.12.2, change-log C-P5.0-AG): the harness may create and later remove the
# exact disposable root it owns, and its descendants, after all existing
# validation has succeeded. These tests are the boundary of that exception —
# what it admits, and everything it still refuses.
# ---------------------------------------------------------------------------


def test_the_root_exception_admits_the_targets_own_root_and_its_descendants() -> None:
    subject = target()
    assert subject.root_or_contained_path("/var/lib/fb-evidence-r1") == (
        "/var/lib/fb-evidence-r1"
    )
    assert subject.root_or_contained_path("/var/lib/fb-evidence-r1/journal") == (
        "/var/lib/fb-evidence-r1/journal"
    )
    assert subject.root_or_contained_path(
        "/var/lib/fb-evidence-r1/journal/000001.seal"
    ) == "/var/lib/fb-evidence-r1/journal/000001.seal"


C1_STILL_REFUSED = [
    ("the filesystem root", "/"),
    ("the /var/lib parent", "/var/lib"),
    ("a system hierarchy", "/etc"),
    ("the repository worktree", REPOSITORY_ROOT),
    ("inside the repository worktree", f"{REPOSITORY_ROOT}/tools"),
    ("the production journal hierarchy", "/var/lib/freedom-sheet-writer"),
    ("a production journal file", "/var/lib/freedom-sheet-writer/journal/1.journal"),
    ("the coordinator deployment root", "/opt/freedom-blades/coordinator"),
    ("a shallow path", "/fb-evidence-r1"),
    ("an unresolved variable", "/var/lib/$EVIDENCE_ROOT"),
    ("a braced variable", "/var/lib/${EVIDENCE_ROOT}"),
    ("a glob", "/var/lib/fb-evidence-r1/*"),
    ("a shell metacharacter", "/var/lib/fb-evidence-r1;rm"),
    ("a sibling evidence root", "/var/lib/fb-evidence-r2"),
    ("a path inside a sibling root", "/var/lib/fb-evidence-r2/journal"),
    ("a prefix-sharing sibling", "/var/lib/fb-evidence-r1x/journal"),
    ("a parent escape", "/var/lib/fb-evidence-r1/../fb-evidence-r2"),
    ("an escape to the parent itself", "/var/lib/fb-evidence-r1/.."),
    ("a home reference", "~/fb-evidence-r1"),
    ("surrounding whitespace", " /var/lib/fb-evidence-r1 "),
    ("the account database", "/etc/passwd"),
    ("the sudoers drop-in directory", "/etc/sudoers.d"),
]


@pytest.mark.parametrize(
    "label, path", C1_STILL_REFUSED, ids=[row[0] for row in C1_STILL_REFUSED]
)
def test_the_root_exception_refuses_everything_it_did_before(
    label: str, path: str
) -> None:
    """The exception is one path, and it is this target's own root.

    Every one of these was refused before the ruling and is refused after it.
    A `..` escape is refused rather than normalized, so the string a reviewer
    approved is the string that would run.
    """
    with pytest.raises(TargetRefused):
        target().root_or_contained_path(path)


def test_an_ordinary_mutation_path_still_requires_strict_containment() -> None:
    """The exception did not widen `contained_path()`.

    Every file, attribute and configuration capture in the package goes through
    `contained_path()`, which still refuses the root itself — so the ruling
    reaches the root's own directory mutation and the `rmdir` derived from it,
    and nothing else.
    """
    subject = target()
    with pytest.raises(TargetRefused) as refusal:
        subject.contained_path("/var/lib/fb-evidence-r1")
    assert "not strictly inside the disposable root" in str(refusal.value)


def test_the_root_exception_still_refuses_an_unconfirmed_or_unassigned_target() -> None:
    """The ruling is about *which path*, never about *whether a target is
    admissible at all*."""
    with pytest.raises(TargetRefused):
        DisposableTarget.unassigned().root_or_contained_path("/var/lib/fb-evidence-r1")
    unconfirmed = target(confirmed_disposable=False, disposability_evidence="")
    with pytest.raises(TargetRefused):
        unconfirmed.root_or_contained_path(unconfirmed.root_path)


def test_validate_absolute_path_reports_which_thing_it_refused() -> None:
    with pytest.raises(TargetRefused) as refusal:
        validate_absolute_path("relative/path", what="socket directory")
    assert "socket directory" in str(refusal.value)
