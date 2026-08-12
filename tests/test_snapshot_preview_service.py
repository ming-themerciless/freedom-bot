"""Council-authorized preview of a pending submitted snapshot.

The properties under test are the ones that make a preview safe to expose:
current authority is resolved per call, nothing is written, and the artifact
comes from the restricted store rather than from anything the caller supplied.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from adapters.artifacts.filesystem import FilesystemArtifactStore
from application.authorization import AuthorizationContext, NotAuthorizedError
from application.foundry.import_service import SnapshotImportService
from application.foundry.preview_service import (
    PreviewUnavailable,
    SnapshotPreviewService,
)
from application.foundry.submission import SnapshotSubmissionService
from application.service_principals import ServicePrincipal, ServicePrincipalScope
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from tests import foundry_fixtures as fx
from tests.fakes import FakeAuthorization, FakeStore, admit, unit_of_work_factory

COUNCIL_USER = 4200000000000000001
ORDINARY_USER = 4200000000000000002
ADMINISTRATOR_USER = 4200000000000000003

SUBMITTER = ServicePrincipal(
    principal_id="foundry-the-guild",
    scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
)


@pytest.fixture()
def wiring(tmp_path: Path):
    store = FakeStore()
    admit(store, SUBMITTER.principal_id)
    artifacts = FilesystemArtifactStore(tmp_path / "artifacts")
    factory = unit_of_work_factory(store)
    authorization = FakeAuthorization.with_council(COUNCIL_USER)
    authorization.grant(
        AuthorizationContext(discord_user_id=ORDINARY_USER, guild_member=True)
    )
    authorization.grant(
        AuthorizationContext(
            discord_user_id=ADMINISTRATOR_USER,
            guild_member=True,
            platform_administrator=True,
        )
    )
    submissions = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=artifacts
    )
    imports = SnapshotImportService(
        factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=authorization,
    )
    preview = SnapshotPreviewService(
        imports, artifacts=artifacts, authorization=authorization
    )
    receipt = submissions.submit(
        fx.encode(fx.bundle()), principal=SUBMITTER, request_key="submitted"
    )
    return preview, store, authorization, receipt


def test_a_council_member_sees_the_bound_preview(wiring):
    preview, _, _, receipt = wiring

    view = preview.preview(
        receipt.checksum, discord_user_id=COUNCIL_USER, request_key="preview-1"
    )

    assert view.checksum == receipt.checksum
    assert view.folder_id == fx.ACTIVE_FOLDER_ID
    assert view.folder_path == "/actors/Characters/Characters (active)"
    assert view.profile_version == PROFILE.version
    assert view.would_create == 1
    assert view.blocked is False
    assert len(view.preview_token) == 64


def test_the_preview_writes_nothing(wiring):
    preview, store, _, receipt = wiring
    before = (
        dict(store.characters),
        list(store.external_actor_mappings),
        list(store.snapshot_imports),
        len(store.audit_events),
    )

    preview.preview(
        receipt.checksum, discord_user_id=COUNCIL_USER, request_key="preview-1"
    )

    assert store.characters == before[0]
    assert store.external_actor_mappings == before[1]
    assert store.snapshot_imports == before[2]
    assert len(store.audit_events) == before[3]


def test_an_ordinary_member_is_refused(wiring):
    preview, _, _, receipt = wiring

    with pytest.raises(NotAuthorizedError) as refusal:
        preview.preview(
            receipt.checksum, discord_user_id=ORDINARY_USER, request_key="preview-1"
        )

    assert refusal.value.code == "not_guild_council"


def test_a_platform_administrator_alone_is_refused(wiring):
    """An operational role does not imply game-policy authority (plan §4.1)."""
    preview, _, _, receipt = wiring

    with pytest.raises(NotAuthorizedError) as refusal:
        preview.preview(
            receipt.checksum,
            discord_user_id=ADMINISTRATOR_USER,
            request_key="preview-1",
        )

    assert refusal.value.code == "not_guild_council"


def test_authority_is_resolved_at_the_moment_of_the_call(wiring):
    preview, _, authorization, receipt = wiring
    preview.preview(
        receipt.checksum, discord_user_id=COUNCIL_USER, request_key="preview-1"
    )

    authorization.revoke(COUNCIL_USER)

    with pytest.raises(NotAuthorizedError):
        preview.preview(
            receipt.checksum, discord_user_id=COUNCIL_USER, request_key="preview-2"
        )


def test_authorization_is_checked_before_the_artifact_is_even_looked_for(wiring):
    """An unauthorized caller cannot learn whether a checksum is held."""
    preview, _, _, _ = wiring

    with pytest.raises(NotAuthorizedError):
        preview.preview(
            "f" * 64, discord_user_id=ORDINARY_USER, request_key="preview-1"
        )


def test_a_checksum_that_was_never_submitted_is_a_typed_refusal(wiring):
    preview, _, _, _ = wiring

    with pytest.raises(PreviewUnavailable) as refusal:
        preview.preview(
            "f" * 64, discord_user_id=COUNCIL_USER, request_key="preview-1"
        )

    assert refusal.value.code == "snapshot_not_held"


def test_a_deleted_artifact_refuses_rather_than_reconciling_nothing(wiring, tmp_path):
    """Retention deletes the document; the checksum and audit record remain."""
    preview, _, _, receipt = wiring
    (tmp_path / "artifacts" / f"{receipt.checksum}.json").unlink()

    with pytest.raises(PreviewUnavailable) as refusal:
        preview.preview(
            receipt.checksum, discord_user_id=COUNCIL_USER, request_key="preview-1"
        )

    assert refusal.value.code == "snapshot_not_held"


def test_a_selectable_folder_can_be_chosen_explicitly(wiring):
    preview, _, _, receipt = wiring

    view = preview.preview(
        receipt.checksum,
        discord_user_id=COUNCIL_USER,
        request_key="preview-1",
        folder_id=fx.ACTIVE_FOLDER_ID,
    )

    assert view.folder_id == fx.ACTIVE_FOLDER_ID
    assert view.selectable_folders == (fx.ACTIVE_FOLDER_ID,)


def test_the_view_payload_is_bounded_and_json_shaped(wiring):
    preview, _, _, receipt = wiring

    payload = preview.preview(
        receipt.checksum, discord_user_id=COUNCIL_USER, request_key="preview-1"
    ).as_payload()

    import json

    rendered = json.dumps(payload)
    assert "Testcharacter" not in rendered
    assert "abilities" not in rendered
    assert set(payload) == {
        "checksum",
        "folder_id",
        "folder_path",
        "profile_version",
        "preview_token",
        "selectable_folders",
        "blocked",
        "would_create",
        "summary",
    }
