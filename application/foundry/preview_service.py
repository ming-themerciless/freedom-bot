"""Reconcile a pending submitted snapshot, for one currently authorized Council member.

This is the join between a submission and the existing import path, and it is
deliberately thin. It resolves current authority, fetches the exact artifact the
submission stored, and hands it to `SnapshotImportService.preview`, which is the
service that already knows how to reconcile and — crucially — to bind what it
reconciled so that a later apply can detect that anything moved.

**Nothing is duplicated from the import service.** No authorization rule, no
reconciliation logic and no binding is re-implemented here. The plan requires the
web adapter to "reuse the existing application authorization and reconciliation
services; do not duplicate their rules", and a second copy of a rule is a second
place for it to be wrong.

**Preview permission is not apply permission.** This service resolves the
Council role *now*, and `SnapshotImportService.apply` resolves it again when it
commits. A role revoked in between refuses the apply, whatever this preview
said.

**Nothing is written.** The underlying preview opens a transaction, reads and
rolls back. A pending snapshot stays pending; no character, mapping, import row
or audit event is created by looking at one.

**The view is bounded.** It carries the reconciliation *summary* — counts, issue
codes, folder identity, checksum, profile version — and not the narrative
per-Actor report. Council members are entitled to see Actor detail, but deciding
how much of it a web response should carry, and to whom, is Phase 3's
authorization and rendering work. Until that exists, this returns the same
bounded facts the platform already stores in `snapshot_imports.summary`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from application.artifacts import ArtifactNotStored, ArtifactStorageError, ArtifactStore
from application.authorization import AuthorizationPort
from application.foundry.import_service import SnapshotImportService

ACTION = "Previewing a submitted Foundry snapshot"


class PreviewUnavailable(RuntimeError):
    """The preview could not be produced. Nothing was read into the platform."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class SnapshotPreviewView:
    """What a Council member is shown before deciding to apply anything."""

    checksum: str
    folder_id: str
    folder_path: str
    profile_version: str
    #: The digest of everything an apply must find unchanged. Presenting it back
    #: is what lets a later confirmation refer to *this* preview rather than to
    #: whatever the database looks like when the button is pressed.
    preview_token: str
    selectable_folders: tuple[str, ...]
    blocked: bool
    would_create: int
    summary: dict[str, Any]

    def as_payload(self) -> dict[str, Any]:
        return {
            "checksum": self.checksum,
            "folder_id": self.folder_id,
            "folder_path": self.folder_path,
            "profile_version": self.profile_version,
            "preview_token": self.preview_token,
            "selectable_folders": list(self.selectable_folders),
            "blocked": self.blocked,
            "would_create": self.would_create,
            "summary": self.summary,
        }


class SnapshotPreviewService:
    def __init__(
        self,
        imports: SnapshotImportService,
        *,
        artifacts: ArtifactStore,
        authorization: AuthorizationPort,
    ) -> None:
        self._imports = imports
        self._artifacts = artifacts
        self._authorization = authorization

    def preview(
        self,
        checksum: str,
        *,
        discord_user_id: int,
        request_key: str,
        folder_id: str | None = None,
    ) -> SnapshotPreviewView:
        """Reconcile the stored artifact `checksum`, or refuse.

        Authorization is resolved first, before the artifact is even fetched: a
        caller who may not preview should not be able to learn from a timing or
        an error code whether a given checksum is held.
        """
        context = self._authorization.context_for(discord_user_id)
        context.require_council(ACTION)

        try:
            artifact = self._artifacts.load(checksum)
        except ArtifactNotStored:
            raise PreviewUnavailable(
                "snapshot_not_held",
                "No artifact is held for that checksum. It was never submitted, "
                "or it was deleted under the documented retention rule — in "
                "which case its checksum and audit record remain, but the "
                "document to reconcile does not.",
            ) from None
        except ArtifactStorageError as error:
            raise PreviewUnavailable(
                "artifact_unreadable",
                "The stored artifact could not be read back "
                f"({error.reason}). Nothing was reconciled.",
            ) from None

        preview = self._imports.preview(
            artifact, request_key=request_key, folder_id=folder_id
        )
        binding = preview.binding
        return SnapshotPreviewView(
            checksum=binding.snapshot_checksum,
            folder_id=binding.folder_id,
            folder_path=binding.folder_path,
            profile_version=binding.profile_version,
            preview_token=binding.token(),
            selectable_folders=preview.selectable_folders,
            blocked=preview.blocked,
            would_create=preview.would_create,
            summary=preview.report.summary(),
        )
