"""The supervised bootstrap command: flags, refusals and safe output."""
from __future__ import annotations

from pathlib import Path

import pytest

from application.authorization import SupervisedBootstrap
from tests import foundry_fixtures as fx
from tools import bootstrap_manager as cli


def write_snapshot(tmp_path: Path, document=None, name: str = "the-guild.json") -> Path:
    path = tmp_path / name
    path.write_bytes(fx.encode(document or fx.bundle()))
    return path


# -- arguments -----------------------------------------------------------------


def test_the_default_run_is_a_rehearsal():
    arguments = cli.parse_arguments(["--snapshot", "x.json"])

    assert arguments.bootstrap is False
    assert arguments.supervisor is None


def test_the_snapshot_is_required():
    with pytest.raises(SystemExit):
        cli.parse_arguments([])


def test_bootstrap_requires_a_named_supervisor(tmp_path, capsys):
    exit_code = cli.main(["--snapshot", str(write_snapshot(tmp_path)), "--bootstrap"])

    assert exit_code == cli.EXIT_MISCONFIGURED
    assert "--supervisor" in capsys.readouterr().err


def test_a_supervisor_without_the_flag_is_a_rehearsal_and_says_so(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    cli.main(
        [
            "--snapshot",
            str(write_snapshot(tmp_path)),
            "--supervisor",
            "Peter Duscha",
        ]
    )

    assert "rehearsal" in capsys.readouterr().err


def test_a_blank_supervisor_is_refused_by_the_value_object():
    with pytest.raises(ValueError):
        SupervisedBootstrap("   ")


# -- artifact refusals happen before the database ------------------------------


def test_a_missing_snapshot_is_refused_without_a_path_in_the_message(tmp_path, capsys):
    exit_code = cli.main(["--snapshot", str(tmp_path / "absent.json")])

    assert exit_code == cli.EXIT_MISCONFIGURED
    error = capsys.readouterr().err
    assert "artifact_unreadable" in error
    assert str(tmp_path) not in error


def test_a_path_bearing_snapshot_name_is_refused(tmp_path, capsys):
    path = write_snapshot(tmp_path, name="snapshot.json.exe")

    exit_code = cli.main(["--snapshot", str(path)])

    assert exit_code == cli.EXIT_MISCONFIGURED
    assert "unsafe_artifact_name" in capsys.readouterr().err


def test_an_archive_is_refused_unopened(tmp_path, capsys):
    path = tmp_path / "snapshot.json"
    path.write_bytes(b"PK\x03\x04 not really a bundle")

    exit_code = cli.main(["--snapshot", str(path)])

    assert exit_code == cli.EXIT_MISCONFIGURED
    assert "unsupported_container" in capsys.readouterr().err


def test_a_misconfigured_database_is_refused_after_the_artifact(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_ENVIRONMENT", raising=False)

    exit_code = cli.main(["--snapshot", str(write_snapshot(tmp_path))])

    assert exit_code == cli.EXIT_MISCONFIGURED
    assert "Database configuration refused" in capsys.readouterr().err


# -- rendering is safe ---------------------------------------------------------


def test_the_report_names_the_snapshot_the_folder_and_the_profile():
    from application.bootstrap import BootstrapGate
    from application.foundry.artifact import ingest_bytes
    from application.foundry.import_service import SnapshotImportService
    from domain.foundry import OBSERVED_DEPLOYMENT
    from domain.foundry_profile import PROFILE
    from tests.fakes import FakeAuthorization, FakeStore, unit_of_work_factory

    store = FakeStore()
    factory = unit_of_work_factory(store)
    authorization = FakeAuthorization.with_council(1)
    service = SnapshotImportService(
        factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=authorization,
        bootstrap_gate=BootstrapGate(factory, profile=PROFILE),
    )
    preview = service.preview(
        ingest_bytes(fx.encode(fx.bundle())), request_key="req-1"
    )

    rendered = cli.render(preview)

    assert PROFILE.version in rendered
    assert "/actors/Characters/Characters (active)" in rendered
    assert "Rehearsal" in rendered
    assert "would create  1" in rendered
    # No Actor field values leak into an operator's terminal.
    assert "Synthetic Human" not in rendered


def test_a_duplicate_prints_the_original_imports_own_record():
    """Not a fresh reconciliation of the database under an "already applied" line.

    The duplicate outcome has no report of its own (finding B-1R): it reconciled
    nothing. Printing the preview's report beside "already applied" would show
    the operator today's database under a heading claiming to describe an import
    from some earlier moment — and today's says the Actor is already mapped,
    where the original said it was a create candidate.
    """
    from application.foundry.artifact import ingest_bytes
    from application.foundry.import_service import SnapshotImportService
    from domain.foundry import OBSERVED_DEPLOYMENT
    from domain.foundry_profile import PROFILE
    from tests.fakes import FakeAuthorization, FakeStore, unit_of_work_factory

    store = FakeStore()
    factory = unit_of_work_factory(store)
    service = SnapshotImportService(
        factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=FakeAuthorization.with_council(1),
    )
    artifact = ingest_bytes(fx.encode(fx.bundle()))
    service.apply(
        artifact, service.preview(artifact, request_key="req-1"), discord_user_id=1
    )
    retry_preview = service.preview(artifact, request_key="req-1")
    duplicate = service.apply(artifact, retry_preview, discord_user_id=1)

    rendered = cli.render(retry_preview, duplicate)

    assert "Already applied" in rendered
    # The original's counts: one Actor, created by that import.
    assert "created       1" in rendered
    assert "already mapped  0" in rendered
    # …which is precisely what a reconciliation run now would *not* say.
    assert retry_preview.report.facts().mapped == 1
    assert "Synthetic Human" not in rendered
