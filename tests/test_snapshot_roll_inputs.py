"""Snapshot-only inputs: readable, provenanced, and never defaulted."""
from __future__ import annotations

from copy import deepcopy
from uuid import uuid4

import pytest

from application.foundry.artifact import ingest_bytes
from application.foundry.parser import parse_snapshot
from application.foundry.roll_inputs import (
    MissingSnapshotInput,
    SnapshotProjection,
)
from application.snapshots import ExternalActorMapping
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from tests import foundry_fixtures as fx

CHARACTER = uuid4()


def projection(actor_document=None, *, character_id=CHARACTER) -> SnapshotProjection:
    document = fx.bundle(actors=(actor_document or fx.actor(),))
    snapshot = parse_snapshot(
        ingest_bytes(fx.encode(document)), deployment=OBSERVED_DEPLOYMENT
    )
    mapping = ExternalActorMapping(
        character_id=character_id,
        world_id="the-guild",
        external_actor_id=fx.FIRST_ACTOR_ID,
        relink_fingerprint="synthetic",
    )
    return SnapshotProjection(snapshot, profile=PROFILE, mappings=(mapping,))


def test_a_roll_input_carries_the_snapshot_and_profile_it_came_from():
    actor = projection().for_character(CHARACTER)

    result = actor.require("skill_proficiencies")

    assert result.value == {"acr": 0, "ath": 1, "prc": 2}
    assert result.provenance.profile_version == PROFILE.version
    assert len(result.provenance.checksum) == 64
    assert result.provenance.exporter == "freedom-blades-export 1.0.0"


def test_provenance_renders_as_facts_a_result_can_record():
    facts = projection().for_character(CHARACTER).provenance.as_facts()

    assert set(facts) == {
        "snapshot_checksum",
        "exporter",
        "exported_at",
        "profile_version",
    }


def test_a_missing_required_input_refuses_rather_than_defaulting():
    stripped = deepcopy(fx.actor())
    stripped["system"].pop("skills")

    with pytest.raises(MissingSnapshotInput) as refusal:
        projection(stripped).for_character(CHARACTER).require("skill_proficiencies")

    assert refusal.value.name == "skill_proficiencies"
    assert "system.skills" in refusal.value.reason


def test_an_optional_input_answers_none_rather_than_a_substituted_value():
    stripped = deepcopy(fx.actor())
    stripped["system"].pop("skills")

    result = projection(stripped).for_character(CHARACTER).optional("skill_proficiencies")

    assert result is None


def test_a_skill_the_snapshot_does_not_record_is_not_no_proficiency():
    actor = projection().for_character(CHARACTER)

    with pytest.raises(MissingSnapshotInput) as refusal:
        actor.skill_proficiency("ste")

    assert "not the same as no proficiency" in refusal.value.reason


def test_a_recorded_skill_returns_its_level():
    actor = projection().for_character(CHARACTER)

    assert actor.skill_proficiency("acr").value == 0
    assert actor.skill_proficiency("ath").value == 1
    assert actor.skill_proficiency("prc").value == 2


def test_a_character_with_no_actor_has_no_projection_rather_than_an_empty_one():
    with pytest.raises(MissingSnapshotInput) as refusal:
        projection().for_character(uuid4())

    assert "has no Actor in snapshot" in str(refusal.value)


def test_an_unknown_input_name_is_refused():
    actor = projection().for_character(CHARACTER)

    with pytest.raises(MissingSnapshotInput) as refusal:
        actor.require("invented_input")

    assert "exposes no roll input" in refusal.value.reason


@pytest.mark.parametrize("name", sorted(PROFILE.roll_inputs()))
def test_every_declared_roll_input_is_reachable_from_the_projection(name):
    actor = projection().for_character(CHARACTER)

    assert name in actor.available()
    assert actor.require(name).value is not None


def test_bastion_facilities_are_observed_not_asserted():
    stripped = deepcopy(fx.actor())
    stripped["items"] = [i for i in stripped["items"] if i["type"] != "facility"]

    result = projection(stripped).for_character(CHARACTER).require("bastion_facilities")

    # An empty observation, carrying its provenance. Absence is not evidence of
    # absence, so nothing here says the character has no Bastion.
    assert result.value == ()
    assert result.provenance.checksum


def test_a_projection_exposes_no_way_to_write_a_snapshot_only_field():
    actor = projection().for_character(CHARACTER)

    public = {name for name in dir(actor) if not name.startswith("_")}

    assert public == {
        "available",
        "optional",
        "provenance",
        "require",
        "skill_proficiency",
    }
