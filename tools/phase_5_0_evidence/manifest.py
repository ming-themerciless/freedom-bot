"""`JNL-46`: the two manifest functions, and the equivalence a deployment has to
prove.

§2.12.5a is explicit that these are **different functions over overlapping
bytes**, and says why: *"Git records none of uid, gid or the full permission
bits, so a manifest computed from a Git tree cannot reproduce them, and a
comparison that pretended otherwise would fail on every correct deployment."*

| | `source_manifest_digest()` | `deployment_manifest_digest()` |
|---|---|---|
| Covers | `deployed_name`, `source_path`, `entry_class`, `content_digest` | path, mode, uid, gid, size, content |
| Computed over | the reviewed Git tree's object bytes (`TM`), and the live deployed bytes projected onto what Git can express (`SM`) | the live deployed bytes (`DD`) |
| Compared with | `APR.source_manifest_digest` at **D3**, and `SM` at **D7** | the operator's supplied value at **C0**, recomputed at **C2** |

Both are SHA-256 over the canonical, typed, length-delimited, schema-versioned
encoding `application/idempotency.py`'s `canonical_request_hash` establishes, over
a list **sorted by deployed relative name**. Neither is re-implemented here: this
module composes that function, which is what stops two encoders disagreeing.

## Why the SHA-256 and not only the commit id

A Git object id is a SHA-1 digest, and SHA-1 is no longer collision-resistant.
`APR` therefore carries `source_manifest_digest` as well as `source_commit` and
`source_tree_id`, and **D3** refuses unless the manifest recomputed from the
store's object bytes equals it. A substituted object that collided under SHA-1
would have different content bytes and therefore a different SHA-256.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from application.idempotency import canonical_request_hash

from .errors import ObservationRefused
from .records import CaseRole, CleanupState, EvidenceRecord, Outcome

BAND = "manifest"

#: Bumped when the field list changes, so a later definition is a visible,
#: versioned change rather than silent drift.
SOURCE_MANIFEST_FORMAT_VERSION = 1
DEPLOYMENT_MANIFEST_FORMAT_VERSION = 1


class EntryClass(str, Enum):
    """The three states a Git tree distinguishes, and the only mode facts both
    sides can produce."""

    REGULAR = "regular"
    EXECUTABLE = "executable"
    SYMLINK = "symlink"


class Region(str, Enum):
    """The closed partition of §2.12.5a. **There is no third region.**"""

    #: Every path the deployment map names, including the unit file and drop-ins.
    SOURCE = "S"
    #: The interpreter and third-party distributions under `…/venv`.
    DEPENDENCY = "D"


@dataclass(frozen=True, slots=True)
class SourceEntry:
    """One entry of the source manifest, on either side of the comparison."""

    deployed_name: str
    source_path: str
    entry_class: EntryClass
    content_digest: str

    def __post_init__(self) -> None:
        if not self.deployed_name.strip():
            raise ObservationRefused("A manifest entry needs its deployed name.")
        if not isinstance(self.entry_class, EntryClass):
            raise ObservationRefused(
                f"{self.entry_class!r} is not one of the three entry classes a Git "
                "tree distinguishes."
            )
        if len(self.content_digest) != 64 or not all(
            character in "0123456789abcdef" for character in self.content_digest
        ):
            raise ObservationRefused(
                "A content digest is a lower-case SHA-256 hex digest."
            )


@dataclass(frozen=True, slots=True)
class DeploymentEntry:
    """One entry of the deployment manifest — the facts a *deployment* has and a
    Git tree does not."""

    deployed_path: str
    mode: int
    uid: int
    gid: int
    size: int
    content_digest: str

    def __post_init__(self) -> None:
        if not self.deployed_path.startswith("/") and not self.deployed_path.startswith("unit"):
            raise ObservationRefused(
                "A deployment entry names an absolute path, or a `unit:` / `unit.d:` "
                "fixed relative name."
            )
        for name in ("mode", "uid", "gid", "size"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ObservationRefused(f"Deployment entry field {name!r} is a whole number.")


def source_manifest_digest(entries: Sequence[SourceEntry]) -> str:
    """`TM` and `SM`, over a list sorted by deployed relative name.

    Deliberately excluded, and why: uid, gid and the numeric mode — Git does not
    record them, and they are checked separately and exactly against the
    deployment map at **D7**; timestamps and inode numbers — they differ between
    two byte-identical deployments; and everything in region **D**, which has its
    own binding.
    """
    ordered = sorted(entries, key=lambda entry: entry.deployed_name)
    _refuse_duplicates(entry.deployed_name for entry in ordered)
    fields: list[tuple[str, str | int]] = [
        ("source_manifest_format_version", SOURCE_MANIFEST_FORMAT_VERSION),
        ("entry_count", len(ordered)),
    ]
    for index, entry in enumerate(ordered):
        fields.extend(
            (
                (f"{index}.deployed_name", entry.deployed_name),
                (f"{index}.source_path", entry.source_path),
                (f"{index}.entry_class", entry.entry_class.value),
                (f"{index}.content_digest", entry.content_digest),
            )
        )
    return canonical_request_hash("phase-5-0-source-manifest", tuple(fields)).hex()


def deployment_manifest_digest(entries: Sequence[DeploymentEntry]) -> str:
    """`DD` — path, mode, uid, gid, size and content, over the deployed bytes."""
    ordered = sorted(entries, key=lambda entry: entry.deployed_path)
    _refuse_duplicates(entry.deployed_path for entry in ordered)
    fields: list[tuple[str, str | int]] = [
        ("deployment_manifest_format_version", DEPLOYMENT_MANIFEST_FORMAT_VERSION),
        ("entry_count", len(ordered)),
    ]
    for index, entry in enumerate(ordered):
        fields.extend(
            (
                (f"{index}.deployed_path", entry.deployed_path),
                (f"{index}.mode", entry.mode),
                (f"{index}.uid", entry.uid),
                (f"{index}.gid", entry.gid),
                (f"{index}.size", entry.size),
                (f"{index}.content_digest", entry.content_digest),
            )
        )
    return canonical_request_hash("phase-5-0-deployment-manifest", tuple(fields)).hex()


def _refuse_duplicates(names) -> None:
    seen: set[str] = set()
    for name in names:
        if name in seen:
            raise ObservationRefused(
                f"{name!r} appears twice in a manifest. Two entries for one deployed "
                "name make the digest depend on which one a reader took."
            )
        seen.add(name)


@dataclass(frozen=True, slots=True)
class PartitionFacts:
    """What the deployed root actually holds, against the closed partition."""

    region_s: frozenset[str]
    region_d: frozenset[str]
    deployed_files: frozenset[str]

    @property
    def unaccounted(self) -> tuple[str, ...]:
        return tuple(sorted(self.deployed_files - self.region_s - self.region_d))

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(sorted((self.region_s | self.region_d) - self.deployed_files))


def classify_manifest_equivalence(
    *,
    trusted: Sequence[SourceEntry],
    deployed: Sequence[SourceEntry],
    approved_digest: str,
) -> tuple[EvidenceRecord, ...]:
    """`JNL-46`'s equivalence: `APR` = `TM` = `SM`, in that order.

    Two records, because they are two comparisons against two different sources
    and collapsing them would hide which one disagreed. **D3** compares the
    manifest recomputed from the store's object bytes with the approval record;
    **D7** compares the manifest over the live deployed bytes with it.
    """
    trusted_digest = source_manifest_digest(trusted)
    deployed_digest = source_manifest_digest(deployed)
    return (
        EvidenceRecord.for_case(
            case_id="JNL-46-D3",
            band=BAND,
            target_identity="root",
            operation="source_manifest_digest() over the reviewed tree's Git object bytes",
            preconditions=(
                "the object store is bare, root:root 0700, and holds APR.source_commit",
                "no ref, branch, tag, HEAD or @{…} expression is resolved at any point",
            ),
            expected=Outcome.read(approved_digest),
            observed=Outcome.read(trusted_digest),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "refusal_code": "DEP-04",
                "note": "This is the check that does not rest on SHA-1: a substituted "
                        "object colliding under SHA-1 has different content bytes and "
                        "therefore a different SHA-256.",
            },
        ),
        EvidenceRecord.for_case(
            case_id="JNL-46-D7",
            band=BAND,
            target_identity="root",
            operation="deployed_source_manifest_digest() over the live installed bytes",
            preconditions=("D3 admitted the trusted manifest",),
            expected=Outcome.read(trusted_digest),
            observed=Outcome.read(deployed_digest),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "refusal_code": "DEP-08",
                "note": "A refusal here removes the deployed tree and restores its "
                        "predecessor, so a deployment that cannot prove its "
                        "provenance does not survive the command that made it.",
            },
        ),
    )


def classify_partition(facts: PartitionFacts) -> EvidenceRecord:
    """**D5**: the staging tree's file set is exactly region S ∪ region D.

    *"There is no third region. A file in the deployed root belonging to neither
    is a refusal at D5 and again at C0. This is what stops the failure that a
    whole-tree digest cannot see: deploying the reviewed files correctly and
    adding one more."*
    """
    unaccounted = facts.unaccounted
    missing = facts.missing
    observed = "exactly S ∪ D"
    if unaccounted or missing:
        observed = f"{len(unaccounted)} unaccounted, {len(missing)} missing"
    return EvidenceRecord.for_case(
        case_id="JNL-46-D5",
        band=BAND,
        target_identity="root",
        operation="compare the deployed file set with region S ∪ region D",
        preconditions=("the deployment map is an entry in the source manifest",),
        expected=Outcome.read("exactly S ∪ D"),
        observed=Outcome.read(observed),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail={
            "refusal_code": "DEP-06",
            "unaccounted_count": len(unaccounted),
            "missing_count": len(missing),
            "first_unaccounted": unaccounted[0] if unaccounted else None,
        },
    )


__all__ = [
    "BAND",
    "DEPLOYMENT_MANIFEST_FORMAT_VERSION",
    "DeploymentEntry",
    "EntryClass",
    "PartitionFacts",
    "Region",
    "SOURCE_MANIFEST_FORMAT_VERSION",
    "SourceEntry",
    "classify_manifest_equivalence",
    "classify_partition",
    "deployment_manifest_digest",
    "source_manifest_digest",
]
