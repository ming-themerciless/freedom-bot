"""Wiring shared by the snapshot preview and import tests.

There is no correction service here any more, and nothing to seed a character's
field values with. After the rejection of ADR 0008 a character has exactly the
state Phase 2 can give it — an identity, a display name and a mapping — so the
harness can only build that much, which is a useful floor: a test cannot set up
a scenario the production code could not have produced.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from application.foundry.artifact import SnapshotArtifact, ingest_bytes
from application.foundry.import_service import SnapshotImportService
from application.snapshots import ExternalActorMapping
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from domain.identity import Character
from tests import foundry_fixtures as fx
from tests.fakes import FakeAuthorization, FakeStore, unit_of_work_factory

COUNCIL_USER = 4200000000000000001
ORDINARY_USER = 4200000000000000002


@dataclass
class Harness:
    store: FakeStore
    authorization: FakeAuthorization
    imports: SnapshotImportService
    factory: object
    correlation_ids: list[UUID] = field(default_factory=list)

    def artifact(self, document=None) -> SnapshotArtifact:
        return ingest_bytes(fx.encode(document or fx.bundle()))

    def add_character(
        self,
        display_name: str,
        *,
        actor_id: str | None = None,
        character_id: UUID | None = None,
        level: int | None = None,
        version: int = 0,
    ) -> Character:
        character = Character(
            id=character_id or uuid4(),
            display_name=display_name,
            level=level,
            version=version,
        )
        self.store.characters[character.id] = character
        if actor_id is not None:
            self.store.external_actor_mappings.append(
                ExternalActorMapping(
                    character_id=character.id,
                    world_id=OBSERVED_DEPLOYMENT.world_id,
                    external_actor_id=actor_id,
                    relink_fingerprint=f"{display_name} / unknown / level unknown",
                    folder_id=fx.ACTIVE_FOLDER_ID,
                )
            )
        return character


def build(*, council_user: int = COUNCIL_USER) -> Harness:
    store = FakeStore()
    factory = unit_of_work_factory(store)
    authorization = FakeAuthorization.with_council(council_user)
    imports = SnapshotImportService(
        factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=authorization,
    )
    return Harness(
        store=store,
        authorization=authorization,
        imports=imports,
        factory=factory,
    )


#: The fixture Actor's display name, which is the only field Phase 2 compares.
FIXTURE_DISPLAY_NAME = "Testcharacter Brightlantern"
