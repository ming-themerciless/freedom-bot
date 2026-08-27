"""C-5's fixtures must be exactly what they claim, or they misreport a measurement.

The generator's whole value is that its byte totals are trustworthy: TC-PERF-01
compares peak resident memory against N-47 for "a synthetic worst case at the
N-20 bound", and a fixture that is quietly 40 MB rather than 64 MB would produce
a comfortable number and prove nothing.

The 64 MiB profiles are **not materialised here**. Building them costs about two
seconds and 130 MB each, and what needs testing about them is the arithmetic that
decides their Actor counts plus the guard that refuses to write a fixture whose
size contradicts its own claim. Both are tested without allocating the corpus.
"""
from __future__ import annotations

import json

import pytest

from application.foundry.artifact import IngestionLimits, SnapshotRejected, ingest_bytes
from application.foundry.parser import parse_snapshot
from domain.foundry import OBSERVED_DEPLOYMENT
from tests.perf_snapshot_fixtures import (
    MAX_ITEMS_PER_ACTOR,
    N20_MAX_ACTORS,
    N20_MAX_BYTES,
    PROFILES,
    REHEARSAL_B_ACTOR_COUNT,
    REHEARSAL_B_MEAN_ACTOR_BYTES,
    REHEARSAL_B_TOTAL_BYTES,
    FixtureError,
    _WORDS,
    _encoded_length,
    _write,
    build_bundle,
    build_profile,
    sized_actor,
)

#: Small enough to be fast, large enough that the padding path runs.
SMALL_ACTOR_BYTES = 24_000


def test_an_actor_encodes_to_exactly_its_target_size():
    """Exact, not approximate — a fixture one byte the wrong side of N-20 tests
    the limit instead of the parse.

    Measured with the generator's own length function, which is the canonical
    encoding **without** `fx.encode`'s trailing newline; that newline is one
    constant byte on the whole bundle, not on each Actor.
    """
    for target in (12_000, SMALL_ACTOR_BYTES, 61_111):
        actor = sized_actor(1, target)
        assert _encoded_length(actor) == target, target


def test_the_real_mean_is_the_observed_rehearsal_b_figure():
    # The generator is only honest if it is sized from the real observation.
    assert REHEARSAL_B_TOTAL_BYTES // REHEARSAL_B_ACTOR_COUNT == REHEARSAL_B_MEAN_ACTOR_BYTES
    assert REHEARSAL_B_MEAN_ACTOR_BYTES > 500_000


def test_generation_is_deterministic():
    first = build_bundle(2, SMALL_ACTOR_BYTES)
    second = build_bundle(2, SMALL_ACTOR_BYTES)
    assert first == second


def test_the_bytes_are_carried_by_many_documents_rather_than_one_large_string():
    """The shape claim, asserted rather than described.

    A real Actor is large because it carries hundreds of item documents. A
    fixture that reached the same byte count with one enormous string would
    allocate one buffer where a real parse allocates thousands of small objects,
    and peak resident memory is the quantity under measurement.
    """
    actor = sized_actor(1, REHEARSAL_B_MEAN_ACTOR_BYTES)
    items = actor["items"]
    assert len(items) > 100
    assert len(items) <= MAX_ITEMS_PER_ACTOR

    longest = max(
        len(value)
        for value in json.dumps(actor).split('"')
    )
    assert longest < REHEARSAL_B_MEAN_ACTOR_BYTES // 10


def test_a_generated_bundle_is_accepted_and_parsed_by_the_real_pipeline():
    payload = build_bundle(3, SMALL_ACTOR_BYTES)
    artifact = ingest_bytes(payload)
    bundle = parse_snapshot(artifact, deployment=OBSERVED_DEPLOYMENT)
    assert len(bundle.actors) == 3
    assert len({actor.actor_id for actor in bundle.actors}) == 3


def test_every_generated_word_is_from_the_invented_word_list():
    """No real name, place, rules term or player datum can reach a fixture."""
    payload = build_bundle(1, SMALL_ACTOR_BYTES).decode("utf-8")
    document = json.loads(payload)
    filler = document["actors"][0]["items"][-1]["system"]["description"]["value"]
    words = filler.removeprefix("<p>").removesuffix("</p>").split()
    assert words, "the filler description is empty"
    assert set(words) <= set(_WORDS)


def test_the_bound_profile_is_planned_just_under_n20_and_the_refusal_profile_just_over():
    bound = PROFILES["bound"]
    over = PROFILES["over-bound"]

    assert bound.approximate_total_bytes < N20_MAX_BYTES
    assert over.approximate_total_bytes > N20_MAX_BYTES
    # Just over, not far over: a refusal at ten times the limit proves less.
    assert over.approximate_total_bytes - N20_MAX_BYTES < REHEARSAL_B_MEAN_ACTOR_BYTES
    # The byte bound binds long before the Actor-count bound, once Actors are
    # real-sized. Worth asserting because it is counter-intuitive from N-20's
    # "500 Actors" alone.
    assert over.actor_count < N20_MAX_ACTORS


def test_the_folder_32_profile_reproduces_rehearsal_bs_shape():
    profile = PROFILES["folder-32"]
    assert profile.actor_count == REHEARSAL_B_ACTOR_COUNT
    drift = abs(profile.approximate_total_bytes - REHEARSAL_B_TOTAL_BYTES)
    assert drift < 1024, drift


def test_building_a_profile_refuses_when_the_produced_size_contradicts_the_claim(monkeypatch):
    """The guard that stops a fixture misreporting what it is.

    Falsified rather than asserted: a profile that claims to be within N-20
    while producing more than N-20 must refuse, and the only way to know the
    guard runs is to make it fire.
    """
    import tests.perf_snapshot_fixtures as module

    liar = module.FixtureProfile(
        name="liar",
        actor_count=2,
        actor_bytes=SMALL_ACTOR_BYTES,
        accepted_by_n20=False,   # claims to exceed N-20; it plainly does not
        purpose="deliberately wrong, for this test",
    )
    monkeypatch.setitem(module.PROFILES, "liar", liar)

    with pytest.raises(FixtureError, match="the opposite of what the profile claims"):
        build_profile("liar")


def test_an_over_sized_artifact_is_refused_by_ingestion():
    """The refusal path SP-15 observes, proved without allocating 64 MiB.

    `over-bound` exists to be refused at the real limit. Here the same shape is
    refused against a deliberately small limit, which exercises the identical
    code path in `ingest_bytes` for a thousandth of the memory.
    """
    payload = build_bundle(2, SMALL_ACTOR_BYTES)
    with pytest.raises(SnapshotRejected) as refusal:
        ingest_bytes(payload, limits=IngestionLimits(max_bytes=len(payload) - 1))
    assert refusal.value.code == "artifact_too_large"


def test_an_actor_target_below_the_base_document_is_refused():
    with pytest.raises(FixtureError, match="over the .* target"):
        sized_actor(1, 100)


def test_writing_refuses_to_overwrite_and_refuses_the_repository(tmp_path):
    destination = tmp_path / "fixture.json"
    _write(b"{}", destination)
    assert destination.read_bytes() == b"{}"
    assert destination.stat().st_mode & 0o777 == 0o600

    with pytest.raises(FixtureError, match="already exists"):
        _write(b"{}", destination)

    from pathlib import Path as _Path

    inside = _Path(__file__).resolve().parent / "must-not-be-written.json"
    with pytest.raises(FixtureError, match="inside the repository"):
        _write(b"{}", inside)
    assert not inside.exists()
