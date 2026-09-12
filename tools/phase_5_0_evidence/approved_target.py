"""The one canonical construction of the approved disposable target.

Peter Duscha, Operations Owner and Acceptance Authority, named and confirmed this
exact target on **2026-09-05**, after `oracle-test` was rebuilt onto the future
production baseline. Codex independently verified the host prerequisites and
accepted the assignment.

## Why this module exists at all

Before it, the target was a value each caller built for itself. That is fine
while the target is `UNASSIGNED` — the harness's default answer — and it stops
being fine the moment a real host is named, because then *"which target?"* has an
answer and every place that answers it separately is a place the answer can be
wrong. This module is the single answer. Nothing else in the package spells a
target fact, the execution plan's §1 table is compared against this module by the
suite rather than maintained beside it, and the executor refuses any plan whose
target is not field-for-field this one.

## What is here, and what deliberately is not

`APPROVED_TARGET` is the `DisposableTarget` the planner and cleanup generator
consume: the five fields those two need, and no more. `APPROVED_TARGET_FACTS`
carries the rest of the confirmed environment — the address, the distribution,
the booted kernel, the filesystem and its device, the PostgreSQL major/instance
and port. Those are review facts rather than planning inputs: no argument vector
is derived from them, and a `DisposableTarget` that carried them would invite one
to be.

`CONFIRMATION_TOKEN` is derived from the target's own identity, so it cannot
drift from it and cannot be memorised as a constant that outlives a target
change. Typing it is the operator's statement *"this host, this root, this
database"*; it is not a secret and gives no authority on its own — execution
additionally needs the explicit flag and the reviewer-supplied plan digest.

## What confirmation does **not** mean

Target assignment closed the first item of the authorization draft's required
sequence and nothing else. It is not authority to execute, it is not approval of
the concrete vectors, and it does not make the R-03/R-04 production-host reads
authorized: those remain a separate decision Peter has not been asked for here.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from .errors import TargetRefused
from .targets import DisposableTarget

#: The decision that made the target admissible, recorded as the target's own
#: `disposability_evidence` so the claim travels with the value rather than
#: living in a document beside it.
DISPOSABILITY_STATEMENT = (
    "Peter Duscha, Operations Owner and Acceptance Authority, named and "
    "confirmed this exact disposable target on 2026-09-05. oracle-test is a "
    "dedicated, explicitly disposable test host rebuilt onto the future "
    "production baseline (Ubuntu 26.04.1 LTS, generic 7.0.0-31 kernel); it is "
    "isolated from production and staging, holds no production credential and "
    "no player data, and its whole purpose is destructive drills. Codex "
    "independently verified the booted generic kernel, PostgreSQL 16 online "
    "with PostgreSQL 18 down and disabled, ext4 append-attribute support, the "
    "root capability bounding set, the required system tools, pristine "
    "template ownership and ACLs, the restricted test role, the absence of any "
    "P5 evidence object, and a metadata-only scan finding no secret-shaped "
    "file, and accepted the assignment."
)

#: The approved disposable target. **One construction, and no other in the
#: package.** Every value below is Peter's, quoted exactly; none is defaulted,
#: inferred from the host this code runs on, or read from the environment.
APPROVED_TARGET = DisposableTarget(
    host="oracle-test",
    root_path="/var/lib/fb-evidence-p5-0",
    database_name="fb_evidence_p5_0",
    postgres_socket_directory="/var/run/postgresql",
    confirmed_disposable=True,
    disposability_evidence=DISPOSABILITY_STATEMENT,
    postgres_config_directory="/etc/postgresql/16/main",
)


@dataclass(frozen=True, slots=True)
class ApprovedTargetFacts:
    """The confirmed environment around the target, for review rather than for
    planning.

    Every field is a fact Peter named or Codex verified on 2026-09-05. No
    argument vector is derived from any of them: they exist so that a reviewer
    reading the manifest can tell *which host, in which state* the vectors were
    approved against, and so that a later run on a rebuilt host produces a
    different manifest digest instead of a silently different meaning.
    """

    host: str
    ipv4: str
    operating_system: str
    architecture: str
    active_kernel: str
    filesystem_root: str
    filesystem_type: str
    filesystem_device: str
    postgres_instance: str
    postgres_port: int
    postgres_socket_directory: str
    postgres_config_directory: str
    evidence_database: str
    confirmed_by: str
    confirmed_on: str

    def as_fields(self) -> tuple[tuple[str, str], ...]:
        """The facts in a fixed order, every value rendered as text.

        Fixed because the review manifest hashes them, and a mapping iterated in
        insertion order is a promise about a dictionary rather than about this
        value.
        """
        return (
            ("host", self.host),
            ("ipv4", self.ipv4),
            ("operating_system", self.operating_system),
            ("architecture", self.architecture),
            ("active_kernel", self.active_kernel),
            ("filesystem_root", self.filesystem_root),
            ("filesystem_type", self.filesystem_type),
            ("filesystem_device", self.filesystem_device),
            ("postgres_instance", self.postgres_instance),
            ("postgres_port", str(self.postgres_port)),
            ("postgres_socket_directory", self.postgres_socket_directory),
            ("postgres_config_directory", self.postgres_config_directory),
            ("evidence_database", self.evidence_database),
            ("confirmed_by", self.confirmed_by),
            ("confirmed_on", self.confirmed_on),
        )


APPROVED_TARGET_FACTS = ApprovedTargetFacts(
    host="oracle-test",
    ipv4="138.2.182.39",
    operating_system="Ubuntu 26.04.1 LTS",
    architecture="x86_64",
    active_kernel="7.0.0-31-generic",
    filesystem_root="/var/lib/fb-evidence-p5-0",
    filesystem_type="ext4",
    filesystem_device="/dev/sda1",
    postgres_instance="16/main",
    postgres_port=5432,
    postgres_socket_directory="/var/run/postgresql",
    postgres_config_directory="/etc/postgresql/16/main",
    evidence_database="fb_evidence_p5_0",
    confirmed_by="Peter Duscha, Operations Owner",
    confirmed_on="2026-09-05",
)

#: The fields a plan's target must match, one by one. Named here rather than
#: taken from `dataclasses.fields()` so that a field added to `DisposableTarget`
#: without a decision about whether a deviation in it is admissible fails the
#: suite instead of being compared by accident or missed by accident.
COMPARED_TARGET_FIELDS = (
    "host",
    "root_path",
    "database_name",
    "postgres_socket_directory",
    "postgres_config_directory",
    "confirmed_disposable",
    "disposability_evidence",
)


def _identity_bytes() -> bytes:
    parts = [f"{name}={getattr(APPROVED_TARGET, name)!r}" for name in COMPARED_TARGET_FIELDS]
    parts.extend(f"{name}={value}" for name, value in APPROVED_TARGET_FACTS.as_fields())
    return "\n".join(parts).encode("utf-8")


#: The full SHA-256 over the canonical identity, for the manifest.
TARGET_IDENTITY_DIGEST = hashlib.sha256(_identity_bytes()).hexdigest()

#: What the operator must type to execute. Derived from the target's identity,
#: so changing any confirmed fact changes the token and the previously approved
#: one stops working — which is the point. It is not a secret and not an
#: authority: execution also needs `--execute` and the reviewer-supplied digest.
CONFIRMATION_TOKEN = (
    f"{APPROVED_TARGET.host}:{APPROVED_TARGET.root_path}:"
    f"{APPROVED_TARGET.database_name}#{TARGET_IDENTITY_DIGEST[:16]}"
)


def target_deviations(candidate: DisposableTarget) -> tuple[str, ...]:
    """Every field in which `candidate` differs from the approved target.

    Returns the differences rather than a boolean, because *"the target is
    wrong"* is not a usable refusal and *"root_path is /var/lib/fb-evidence-p5-1
    and the approved root is /var/lib/fb-evidence-p5-0"* is. A candidate that is
    `UNASSIGNED`, or that was never confirmed, deviates in exactly the fields
    that say so.
    """
    if not isinstance(candidate, DisposableTarget):
        return (
            f"The plan's target is {type(candidate).__name__}, not a "
            "DisposableTarget.",
        )
    deviations: list[str] = []
    for name in COMPARED_TARGET_FIELDS:
        mine = getattr(APPROVED_TARGET, name)
        theirs = getattr(candidate, name, None)
        if theirs != mine:
            deviations.append(f"{name}: plan has {theirs!r}, approved is {mine!r}")
    return tuple(deviations)


def require_approved_target(candidate: DisposableTarget) -> DisposableTarget:
    """Raise `TargetRefused` unless `candidate` is the approved target exactly.

    The executor's first gate. A near-miss is refused as hard as a production
    path is: the authorization names one host, one root, one database and one
    configuration directory, and *"almost that"* is a target nobody confirmed.
    """
    deviations = target_deviations(candidate)
    if deviations:
        raise TargetRefused(
            "This is not the disposable target Peter Duscha confirmed on "
            "2026-09-05. "
            + "; ".join(deviations)
            + ". A target the Operations Owner did not name is a stop condition, "
            "not a parameter."
        )
    return candidate


__all__ = [
    "APPROVED_TARGET",
    "APPROVED_TARGET_FACTS",
    "ApprovedTargetFacts",
    "COMPARED_TARGET_FIELDS",
    "CONFIRMATION_TOKEN",
    "DISPOSABILITY_STATEMENT",
    "TARGET_IDENTITY_DIGEST",
    "require_approved_target",
    "target_deviations",
]
