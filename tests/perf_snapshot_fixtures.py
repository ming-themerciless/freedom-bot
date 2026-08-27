"""C-5: bounded synthetic snapshot fixtures shaped to the **real** size distribution.

Built for TC-PERF-01 and TC-PERF-02 (execution plan §11.4, evidence inventory §7
item C-5). Generated at run time and **never committed**: a 16 MB fixture in Git
is a fixture nobody reads and a repository nobody can clone quickly, and the
traceability contract §20 forbids committing snapshot corpora as fixtures.

## The defect this exists to correct

`tests/benchmark_snapshot_500.py` generates 500 Actors of **2,182 bytes** each.
Phase 2's Rehearsal B then previewed a real folder of **32 Actors totalling
16,287,185 bytes** — 508,974 bytes per Actor, **233× larger**. A measurement
taken against the synthetic corpus therefore measures the corpus, not the code:
peak resident memory and per-Actor parse cost both scale with Actor *bytes*, and
the synthetic Actors have almost none.

So these fixtures are sized from the real observation, and the shape is copied
from what makes a real Actor large: **hundreds of embedded item documents with
prose in them**, not one enormous string. A single 500 KB string would produce
the right byte count and the wrong allocation profile — one large buffer instead
of the thousands of small objects a real parse actually creates, which is exactly
what N-47's memory ceiling is a guard against.

## What is honest about this corpus, and what is not

**Honest:** the byte total, the Actor count, the per-Actor byte distribution, the
item-count-per-Actor order of magnitude, the document schema, and the depth.

**Not the real thing, and stated so wherever these fixtures are cited:** the
filler prose is lexically repetitive, so anything that measures *compression* —
a proxy's gzip, a `pg_dump` of stored bytes — will be optimistic against real
data. Nothing in TC-PERF-01/02 measures compression; parse time, peak RSS and
apply duration all work on decoded objects. Recorded here so a reviewer can
challenge it rather than discover it.

**No real Actor, name, payload, biography or warning text appears here or can.**
Every string is generated from the word list below.

## The profiles

| Profile | Actors | Target bytes | Purpose |
|---|---|---|---|
| `folder-32` | 32 | ≈16.3 MB | Rehearsal B's real shape, as the synthetic control for the real-folder run (D-m's synthetic pair) |
| `bound` | 131 | just under 64 MiB | TC-PERF-01's "synthetic worst-case at the N-20 bound" |
| `over-bound` | 132 | just over 64 MiB | SP-15's 64 MiB **refusal** observation |

`bound` is 131 Actors because 64 MiB ÷ 508,974 bytes is 131.9: the N-20 byte
bound binds long before N-20's 500-Actor bound does, once Actors are real-sized.
That is worth knowing before the measurement rather than after it.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from application.foundry.artifact import DEFAULT_MAX_BYTES, SnapshotArtifact, ingest_bytes
from application.foundry.parser import BundleLimits
from domain.foundry import SnapshotChecksum
from tests import foundry_fixtures as fx

# ---------------------------------------------------------------------------
# The real observation these fixtures are sized from
# ---------------------------------------------------------------------------

#: Phase 2 Rehearsal B, 2026-08-09. The only real measurement that exists.
REHEARSAL_B_ACTOR_COUNT = 32
REHEARSAL_B_TOTAL_BYTES = 16_287_185
REHEARSAL_B_MEAN_ACTOR_BYTES = REHEARSAL_B_TOTAL_BYTES // REHEARSAL_B_ACTOR_COUNT

#: N-20, read from the code that enforces it rather than restated as a literal.
N20_MAX_BYTES = DEFAULT_MAX_BYTES
N20_MAX_ACTORS = BundleLimits().max_actors
MAX_ITEMS_PER_ACTOR = BundleLimits().max_items_per_actor

#: How far under the bound the `bound` profile aims. Not arbitrary: the whole
#: point of that fixture is to be accepted, and a fixture that lands one byte
#: the wrong side of a limit tests the limit instead of the parse.
BOUND_HEADROOM_BYTES = 64 * 1024


class FixtureError(RuntimeError):
    """A fixture could not be generated within its stated bounds."""


# ---------------------------------------------------------------------------
# Deterministic synthetic prose
# ---------------------------------------------------------------------------

#: Invented words only. Nothing here is a rules term, a place, a person or a
#: quotation, so no copyrighted text and no player datum can reach a fixture.
_WORDS = (
    "lantern", "vellum", "quartz", "harrow", "sable", "kindled", "meridian",
    "brambling", "verdigris", "tallow", "cistern", "gyre", "hollow", "keening",
    "pallid", "rookery", "sallow", "thrum", "umber", "wending", "yarrow",
    "clarion", "dolmen", "ember", "fathom", "gambit", "hearth", "ingot",
)


def _filler_words(seed: int, count: int) -> str:
    """A deterministic ASCII sentence. ASCII so byte length equals character length."""
    return " ".join(_WORDS[(seed + step) % len(_WORDS)] for step in range(count))


def _encoded_length(document: Any) -> int:
    """The canonical encoded byte length of one object.

    `fx.encode` appends a trailing newline to a *bundle*; this does not, because
    it is used to size the objects inside one. The newline is a single constant
    byte on the finished artifact, and the profile totals below account for it.
    """
    return len(
        json.dumps(
            document, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    )


def _filler_item(actor_index: int, item_index: int, words: int) -> dict[str, Any]:
    """One embedded spell document, shaped like the ones that make a real Actor large."""
    seed = actor_index * 7919 + item_index
    return {
        "type": "spell",
        "name": f"Invented Cantrip {actor_index:04d}-{item_index:04d}",
        "system": {
            "level": item_index % 10,
            "school": _WORDS[seed % len(_WORDS)],
            "description": {
                "value": f"<p>{_filler_words(seed, words)}</p>",
                "chat": "",
            },
            "activation": {"type": "action", "cost": 1},
            "duration": {"value": 1, "units": "minute"},
            "target": {"value": 1, "type": "creature"},
            "range": {"value": 30, "units": "ft"},
        },
    }


# ---------------------------------------------------------------------------
# Actor sizing
# ---------------------------------------------------------------------------

#: Words per filler item. Chosen so one item is roughly 1.2 KB — the order of
#: magnitude of a real `dnd5e` spell or feature document with its description.
_WORDS_PER_ITEM = 150


def sized_actor(actor_index: int, target_bytes: int) -> dict[str, Any]:
    """One Actor whose encoded length is exactly `target_bytes`.

    Built by adding whole item documents until one more would overshoot, then
    padding the **last** item's description to land on the target exactly. Exact
    rather than approximate because the refusal fixture has to sit a known
    distance past a hard limit, and "about 64 MiB" cannot demonstrate that.
    """
    actor = fx.actor(
        actor_id=f"perf{actor_index:012d}"[:16],
        name=f"Synthetic Actor {actor_index:04d}",
        folder_id=fx.ACTIVE_FOLDER_ID,
    )
    base_length = _encoded_length(actor)
    if base_length > target_bytes:
        raise FixtureError(
            f"The base Actor is {base_length} bytes, over the {target_bytes}-byte "
            "target. Raise the target; the shape is not negotiable."
        )

    items: list[dict[str, Any]] = actor["items"]

    # Appending to a JSON array adds exactly the element's own encoding plus one
    # separator byte, so the running total is arithmetic rather than a re-encode
    # of the whole Actor. A probe-and-multiply estimate is *not* safe here: the
    # filler words differ in length between items, so every item has a different
    # exact cost and an average would overshoot for some Actors and undershoot
    # for others.
    length = base_length
    item_index = 0
    while True:
        candidate = _filler_item(actor_index, item_index, _WORDS_PER_ITEM)
        cost = _encoded_length(candidate) + 1
        # Leave room for the padded tail item, which cannot be smaller than its
        # own unpadded encoding.
        if length + cost + cost > target_bytes:
            break
        if len(items) >= MAX_ITEMS_PER_ACTOR - 1:
            raise FixtureError(
                f"Actor {actor_index} reached the {MAX_ITEMS_PER_ACTOR}-item "
                "parser bound before its byte target. Use more Actors, not "
                "larger ones."
            )
        items.append(candidate)
        length += cost
        item_index += 1

    # One final item, its description padded character by character onto the
    # target. Padding is appended as plain ASCII, so one character is one byte.
    tail = _filler_item(actor_index, item_index, _WORDS_PER_ITEM)
    items.append(tail)
    shortfall = target_bytes - _encoded_length(actor)
    if shortfall < 0:
        raise FixtureError(
            f"Actor {actor_index} overshot its {target_bytes}-byte target by "
            f"{-shortfall} bytes before padding. This is a generator defect."
        )
    description = tail["system"]["description"]
    description["chat"] = "x" * shortfall

    produced = _encoded_length(actor)
    if produced != target_bytes:
        raise FixtureError(
            f"Actor {actor_index} encoded to {produced} bytes, not the requested "
            f"{target_bytes}. This is a generator defect."
        )
    return actor


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FixtureProfile:
    """A named corpus, with the reason it is that size."""

    name: str
    actor_count: int
    actor_bytes: int
    accepted_by_n20: bool
    purpose: str

    @property
    def approximate_total_bytes(self) -> int:
        return self.actor_count * self.actor_bytes


def _actors_that_fit(budget_bytes: int, actor_bytes: int) -> int:
    return budget_bytes // actor_bytes


#: 131 at the real mean; computed rather than written down so the arithmetic is
#: checkable and moves if the observed mean is ever re-measured.
_BOUND_ACTOR_COUNT = _actors_that_fit(
    N20_MAX_BYTES - BOUND_HEADROOM_BYTES, REHEARSAL_B_MEAN_ACTOR_BYTES
)

PROFILES: dict[str, FixtureProfile] = {
    "folder-32": FixtureProfile(
        name="folder-32",
        actor_count=REHEARSAL_B_ACTOR_COUNT,
        actor_bytes=REHEARSAL_B_MEAN_ACTOR_BYTES,
        accepted_by_n20=True,
        purpose=(
            "Rehearsal B's observed shape: 32 Actors at the real mean. The "
            "synthetic control for the single real-folder run (D-m)."
        ),
    ),
    "bound": FixtureProfile(
        name="bound",
        actor_count=_BOUND_ACTOR_COUNT,
        actor_bytes=REHEARSAL_B_MEAN_ACTOR_BYTES,
        accepted_by_n20=True,
        purpose=(
            "TC-PERF-01's synthetic worst case: as close under N-20's 64 MiB as "
            "real-sized Actors reach. The byte bound binds first; the 500-Actor "
            "bound is never approached."
        ),
    ),
    "over-bound": FixtureProfile(
        name="over-bound",
        actor_count=_BOUND_ACTOR_COUNT + 1,
        actor_bytes=REHEARSAL_B_MEAN_ACTOR_BYTES,
        accepted_by_n20=False,
        purpose=(
            "SP-15's refusal observation: past 64 MiB by roughly one Actor, so "
            "the refusal is demonstrated at the boundary rather than at 10× it."
        ),
    ),
}


def build_bundle(actor_count: int, actor_bytes: int) -> bytes:
    """Encode a complete, contract-valid bundle of `actor_count` sized Actors."""
    if actor_count > N20_MAX_ACTORS:
        raise FixtureError(
            f"{actor_count} Actors is over N-20's {N20_MAX_ACTORS}-Actor bound."
        )
    actors = tuple(
        sized_actor(index, actor_bytes) for index in range(1, actor_count + 1)
    )
    return fx.encode(
        fx.bundle(actors=actors, selected_folder_ids=(fx.ACTIVE_FOLDER_ID,))
    )


def build_profile(name: str) -> bytes:
    try:
        profile = PROFILES[name]
    except KeyError:
        raise FixtureError(
            f"Unknown profile {name!r}. Known: {', '.join(sorted(PROFILES))}."
        ) from None
    payload = build_bundle(profile.actor_count, profile.actor_bytes)
    over_bound = len(payload) > N20_MAX_BYTES
    if over_bound != (not profile.accepted_by_n20):
        raise FixtureError(
            f"Profile {name!r} produced {len(payload)} bytes, which is "
            f"{'over' if over_bound else 'under'} N-20's {N20_MAX_BYTES}-byte "
            "bound — the opposite of what the profile claims. Refusing to write "
            "a fixture that would misreport what it is."
        )
    return payload


def artifact_of(payload: bytes) -> SnapshotArtifact:
    """Ingest, so the measurement runs against bytes the application accepted."""
    return ingest_bytes(payload)


# ---------------------------------------------------------------------------
# Operator entry point
# ---------------------------------------------------------------------------


def _write(payload: bytes, destination: Path) -> None:
    if destination.exists():
        raise FixtureError(
            f"{destination} already exists. Fixtures are written once and "
            "shredded at teardown; refusing to overwrite one."
        )
    repository_root = Path(__file__).resolve().parents[1]
    try:
        destination.resolve().relative_to(repository_root)
    except ValueError:
        pass
    else:
        raise FixtureError(
            f"{destination} is inside the repository. These fixtures are never "
            "committed; write them under the artifact root or a scratch path."
        )
    destination.write_bytes(payload)
    destination.chmod(0o600)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tests.perf_snapshot_fixtures",
        description=(
            "Generate a bounded synthetic snapshot fixture shaped to the real "
            "size distribution. Never writes inside the repository."
        ),
    )
    parser.add_argument("--profile", required=True, choices=sorted(PROFILES))
    parser.add_argument("--out", type=Path, help="Where to write. Omit to report only.")
    arguments = parser.parse_args(argv)

    try:
        payload = build_profile(arguments.profile)
        checksum = SnapshotChecksum.of(payload)
        if arguments.out is not None:
            _write(payload, arguments.out)
    except FixtureError as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 1

    profile = PROFILES[arguments.profile]
    print(f"profile          {profile.name}")
    print(f"purpose          {profile.purpose}")
    print(f"actors           {profile.actor_count}")
    print(f"bytes            {len(payload)}")
    print(f"bytes per actor  {profile.actor_bytes}")
    print(f"N-20 bound       {N20_MAX_BYTES}")
    print(f"within N-20      {len(payload) <= N20_MAX_BYTES}")
    print(f"sha256           {checksum.hex_digest}")
    if arguments.out is not None:
        print(f"written          {arguments.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover - operator entry point
    raise SystemExit(main())
