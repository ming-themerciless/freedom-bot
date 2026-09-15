"""The independent recovery store of runner contract r6 §§2.2–2.5, on disk.

## The finding this answers

Revision 1 §7 said the recovery basis when the disposable root is unsafe is
*"the operator's own out-of-band copy"*, and named `cleanup.RECOVERY_PROCEDURE`
as its procedure. **Neither held.** No operation created, verified or durably
retained such a copy, and nothing made one a prerequisite of the first mutation;
and the named procedure instructed recovery from the captures under the
disposable root's own `before/` directory, whose custody is exactly the custody
in question. That is PR-20260911-2.

Revision 2 introduced a store outside the root and then **published it
non-durably**: it synchronized the captures and the run directory and never
synchronized the **recovery parent**. `fsync(2)` is explicit that a containing
directory must be synchronized separately for a new entry to be durable, so
after a power loss, restart discovery by listing the recovery parent is not
guaranteed to find the advertised basis however carefully its contents were
written. That is PR-20260911-R2-2, and `recovery-parent-entry` is the barrier it
found missing.

## The rule, stated before the sequence

> **No first configuration mutation may occur until both the recoverable bytes
> and all the metadata needed to discover and verify them after a crash are
> durably published.**

Two halves, and revision 2 satisfied only the first. *Recoverable bytes* is the
copy. *Metadata needed to discover them* includes the run directory's **own
entry in the recovery parent**, because discovery is `readdir` of that parent.

## What is not a barrier

`durability_model.NOT_A_BARRIER` names all three, and each appears in this
module as something performed **beside** a barrier rather than instead of one:

* a **read-back and digest comparison**. It establishes that the bytes written
  are the bytes captured, and **nothing** about whether either survives a power
  loss. Step 11 does it, after every barrier, and is labelled a verification;
* a successful **rename**. It changes the namespace; it does not synchronize the
  directory the namespace entry lives in; and
* a successful **write**. Data reaches the page cache, not the device.

A sequence that performed any of these in place of a barrier has performed no
barrier, and `publish()` returns `mutation_permitted=False` whenever a barrier
did not return success — whatever else succeeded.

## Custody

`/var/lib/freedom-blades/recovery` is `0700 root:root`, so **no experimental
identity may traverse it** and no case can reach a capture even by descriptor.
That is provisioning item **V5** and it is unapproved: this module opens the
parent a caller names and refuses when it is absent. It never creates it.

## Retention and disposal

A run's directory is retained until **both** the post-reload verification of
§2.4(6) passed **and** `reservation.release` returned `RELEASED`. A quarantined
run's directory is never removed automatically, and disposal is an explicit
operator step naming the run id — not a command this module offers, for the same
reason §2.13.2b withdrew the automatic clean.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from ..durability_model import (
    NOT_A_BARRIER,
    PUBLICATION_BARRIERS,
    DescriptorMode,
    RecoveryRecord,
)
from ..materialization import MAX_MATERIALIZED_BYTES
from ..provisioning import LABORATORY_LAYOUT
from .descriptors import DescriptorInventory, DescriptorRefused, PosixFilesystem

#: The barrier names, in the order §2.3.3 requires them. Imported rather than
#: respelled: the model and the mechanism name the same five barriers, so a
#: reviewer comparing the two tables compares one list with itself.
BARRIER_ORDER: tuple[str, ...] = tuple(barrier.name for barrier in PUBLICATION_BARRIERS)

#: The refusal a capture publication reports. Fixed and safe.
CAPTURE_SOURCE_UNREADABLE = "capture-source-unreadable"
CAPTURE_SOURCE_CHANGED = "capture-source-changed-during-read"
CAPTURE_TOO_LARGE = "capture-exceeds-reviewed-bound"
CAPTURE_RUN_DIRECTORY_EXISTS = "recovery-run-directory-exists"
CAPTURE_BARRIER_FAILED = "publication-barrier-failed"
CAPTURE_VERIFICATION_FAILED = "stored-copy-does-not-verify"
CAPTURE_PARENT_UNAVAILABLE = "recovery-parent-unavailable"
#: **PR-20260913-LABI-1.** The six refusals the destination binding adds. Each
#: is decided **before** the recovery run directory is created, so a refused
#: request leaves no directory, no temporary, no copy and no record.
CAPTURE_SET_NOT_BOUND = "reviewed-capture-set-not-bound"
CAPTURE_SET_INCOMPLETE = "reviewed-capture-set-incomplete"
CAPTURE_COMPONENT_NOT_REVIEWED = "capture-component-not-reviewed"
CAPTURE_COMPONENT_MALFORMED = "capture-component-malformed"
CAPTURE_DESTINATION_NOT_BOUND = "capture-destination-not-bound"
CAPTURE_DESTINATION_DUPLICATED = "capture-destination-duplicated"
#: The publication verification could not establish the one-to-one
#: record/copy/destination correspondence `restore_configuration()` consumes.
CAPTURE_CORRESPONDENCE_FAILED = "stored-correspondence-does-not-verify"

CAPTURE_REFUSALS: frozenset[str] = frozenset(
    {
        CAPTURE_SOURCE_UNREADABLE,
        CAPTURE_SOURCE_CHANGED,
        CAPTURE_TOO_LARGE,
        CAPTURE_RUN_DIRECTORY_EXISTS,
        CAPTURE_BARRIER_FAILED,
        CAPTURE_VERIFICATION_FAILED,
        CAPTURE_PARENT_UNAVAILABLE,
        CAPTURE_SET_NOT_BOUND,
        CAPTURE_SET_INCOMPLETE,
        CAPTURE_COMPONENT_NOT_REVIEWED,
        CAPTURE_COMPONENT_MALFORMED,
        CAPTURE_DESTINATION_NOT_BOUND,
        CAPTURE_DESTINATION_DUPLICATED,
        CAPTURE_CORRESPONDENCE_FAILED,
    }
)

#: **PR-20260913-LABI-1, stated where the publisher is.** The rule the reviewer
#: found unenforced, in the terms the finding used.
DESTINATION_BINDING_RULE = (
    "The reviewed configuration capture set — the exact components, the exact "
    "destinations and the exact correspondence between a stored copy, its "
    "record and its restoration target — is established at the integration "
    "boundary. A caller supplies a request; it never supplies the set.",
    "The whole requested set is validated before the recovery run directory "
    "exists. Missing, additional, duplicate, malformed, cross-directory and "
    "mismatched entries refuse with no publication and no permitted mutation.",
    "Publication verification establishes the same one-to-one "
    "record/copy/destination correspondence restoration consumes, not merely a "
    "comparison of copy digests.",
    "`mutation_permitted` is true only when the exact reviewed set is durably "
    "published, every barrier returned success and the complete basis verifies. "
    "A record a restoration must refuse is not a recovery basis at mutation "
    "time.",
)

#: The fixed reasons a discovery reports. **None carries stored text.** A record
#: this store failed to bind is named by its run and its rule, never by the
#: bytes or the destination it claimed, because those are attacker-controlled.
DISCOVERY_LEFTOVER_TEMPORARY = (
    "a publication temporary is present, so a capture was being written when "
    "its writer stopped. It is reported and not removed."
)
DISCOVERY_RECORD_UNDECODABLE = (
    "a stored recovery record could not be decoded. A record that cannot be "
    "parsed verifies nothing."
)
DISCOVERY_ORPHAN_RECORD = "a record names a copy the run directory does not hold."
DISCOVERY_ORPHAN_COPY = (
    "a stored copy has no record beside it. Bytes nobody can place are not a "
    "recovery basis."
)
DISCOVERY_DIGEST_MISMATCH = (
    "a stored copy does not digest to the value its record binds, so the basis "
    "is present and not usable."
)
DISCOVERY_WRONG_RUN_ID = (
    "a stored record names a run other than the directory it is filed under. "
    "The directory name is not the binding and neither is the record alone."
)
DISCOVERY_DESTINATION_NOT_BOUND = (
    "a stored record names a destination outside the reviewed capture set, so "
    "restoration would refuse it. A basis restoration refuses is not a basis."
)
DISCOVERY_COPY_NAME_MISMATCH = (
    "a stored record's destination does not correspond to the copy it is filed "
    "beside, so the one-to-one binding does not hold."
)
DISCOVERY_DESTINATION_DUPLICATED = (
    "two stored records name one destination, so the set does not restore each "
    "reviewed file exactly once."
)
DISCOVERY_SET_INCOMPLETE = (
    "the run directory does not hold the complete reviewed capture set, so a "
    "restoration from it would leave a mixed configuration."
)

DISCOVERY_REASONS: frozenset[str] = frozenset(
    {
        DISCOVERY_LEFTOVER_TEMPORARY,
        DISCOVERY_RECORD_UNDECODABLE,
        DISCOVERY_ORPHAN_RECORD,
        DISCOVERY_ORPHAN_COPY,
        DISCOVERY_DIGEST_MISMATCH,
        DISCOVERY_WRONG_RUN_ID,
        DISCOVERY_DESTINATION_NOT_BOUND,
        DISCOVERY_COPY_NAME_MISMATCH,
        DISCOVERY_DESTINATION_DUPLICATED,
        DISCOVERY_SET_INCOMPLETE,
    }
)

#: The mode every stored object carries. Read-only to root; a copy is replaced
#: by replacing the whole directory, never by rewriting a file in place.
STORED_OBJECT_MODE = 0o400
RUN_DIRECTORY_MODE = 0o700

#: The two name suffixes the store uses. A `.record` names the binding between
#: a copy's bytes and where they came from and go; a `.tmp` is a publication
#: temporary, which is reported and **never removed automatically**.
RECORD_SUFFIX = ".record"
TEMPORARY_SUFFIX = ".tmp"


def _barrier_reason(name: str) -> tuple[str, ...]:
    return (
        f"the {name!r} barrier did not return success, so nothing later may "
        "proceed. No configuration mutation is issued, and there is therefore "
        "nothing to recover from.",
    )


def _record_barrier(name: str, crossed: list[str]) -> None:
    if name not in crossed:
        crossed.append(name)


@dataclass(frozen=True, slots=True)
class ConfigurationCaptureSet:
    """The reviewed capture set — **PR-20260913-LABI-1's binding**.

    One directory and the exact component names under it. The destination for a
    component is derived here and nowhere else, so there is no parameter through
    which a caller substitutes an absolute path of its own: a request names
    components and their destinations, and every one is compared with what this
    object derives.

    It is constructed at the integration boundary from the approved target's own
    configuration directory and `targets.POSTGRES_CONFIG_FILES`. A store with no
    set bound publishes nothing.
    """

    directory: str
    components: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.directory.startswith("/") or self.directory.endswith("/"):
            raise DescriptorRefused(
                "descriptor-open-refused",
                "recovery",
                "a reviewed capture set names one absolute configuration "
                "directory with no trailing separator",
            )
        for component in self.components:
            _require_capture_component(component)

    @property
    def duplicated(self) -> tuple[str, ...]:
        """Components named twice. One destination restored twice is not a set."""
        seen: set[str] = set()
        repeated: list[str] = []
        for component in self.components:
            if component in seen and component not in repeated:
                repeated.append(component)
            seen.add(component)
        return tuple(repeated)

    def destination_for(self, component: str) -> str:
        """The one destination this component may bind to."""
        return f"{self.directory}/{component}"

    def destinations(self) -> Mapping[str, str]:
        return {name: self.destination_for(name) for name in self.components}

    def stored_names(self) -> tuple[str, ...]:
        """Every name a complete publication leaves in the run directory."""
        names: list[str] = []
        for component in self.components:
            names.append(component)
            names.append(f"{component}{RECORD_SUFFIX}")
        return tuple(sorted(names))

    def component_for(self, destination: str) -> str:
        """The reviewed component a stored destination names, or `""`."""
        for component in self.components:
            if self.destination_for(component) == destination:
                return component
        return ""


def _require_capture_component(name: str) -> None:
    """One path component, and the refusal names the rule rather than the name."""
    if (
        not name
        or "/" in name
        or name in (".", "..")
        or name.endswith(RECORD_SUFFIX)
        or name.endswith(TEMPORARY_SUFFIX)
    ):
        raise _CaptureRefused(
            CAPTURE_COMPONENT_MALFORMED,
            (
                "a capture component is one path component that is neither `.` "
                "nor `..`, contains no separator, and does not collide with the "
                "store's own record or temporary suffix.",
            ),
        )


@dataclass(frozen=True, slots=True)
class CapturedSource:
    """One configuration file, as the capture read it.

    `identity` is the source's `(st_dev, st_ino, st_size, st_mtim)` at the
    moment of the read, and `digest` is computed **over the buffer** and never
    over a re-read of the pathname. A re-read reads a possibly different file,
    which is PR-20260909-R2-2 and which stays.
    """

    name: str
    destination: str
    identity: str
    digest: str
    byte_length: int


@dataclass(frozen=True, slots=True)
class StorePublication:
    """What one publication concluded, and whether M1 may proceed.

    `mutation_permitted` is the whole point of the object: it is true only when
    every barrier in `BARRIER_ORDER` returned success **and** the stored copies
    verified. A caller that consults anything else before mutating a
    configuration file has performed no barrier check.
    """

    published: bool
    mutation_permitted: bool
    barriers_crossed: tuple[str, ...] = ()
    refusal: str = ""
    reasons: tuple[str, ...] = ()
    run_directory_name: str = ""
    captures: tuple[CapturedSource, ...] = ()
    not_barriers: tuple[str, ...] = NOT_A_BARRIER


@dataclass(frozen=True, slots=True)
class DiscoveredRun:
    """One recovery basis a restart found by listing the recovery parent."""

    run_id: str
    record_names: tuple[str, ...]
    copy_names: tuple[str, ...]
    records: tuple[RecoveryRecord, ...] = ()
    verifiable: bool = False
    reasons: tuple[str, ...] = ()

    @property
    def usable(self) -> bool:
        """Discoverable, complete and verifying. All three, or it is not a basis."""
        return bool(self.records) and self.verifiable and not self.reasons


@dataclass(slots=True)
class RecoveryStore:
    """`/var/lib/freedom-blades/recovery`, and one directory per run inside it.

    The parent is a **provisioned** directory this object opens and never
    creates: creating it would be a provisioning act, and an absent parent means
    the host was not provisioned for independent recovery — which refuses the
    first mutation rather than proceeding without a basis.
    """

    inventory: DescriptorInventory
    filesystem: PosixFilesystem
    parent_role: str = "recovery"
    parent_path: str = LABORATORY_LAYOUT.recovery_directory
    #: **PR-20260913-LABI-1.** The reviewed capture set, established at the
    #: integration boundary. A store with none bound publishes nothing: there is
    #: no set to compare a request against, and a publication that compared a
    #: request with itself is the defect the finding reproduced.
    capture_set: ConfigurationCaptureSet | None = None
    _parent_object_id: str = field(default="", init=False)

    # -- setup ----------------------------------------------------------------

    def bind_capture_set(self, capture_set: ConfigurationCaptureSet) -> None:
        """Establish the reviewed set. The integration boundary's act, not a caller's."""
        self.capture_set = capture_set

    def open_parent(self) -> None:
        """Hold the recovery parent twice, and bind the barrier descriptor.

        The synchronizable descriptor is bound here, before anything is written,
        so a parent whose second lookup reaches a different object refuses
        **before** a capture is taken rather than at the barrier that needed it.
        """
        handle = self.inventory.open_provisioned_root(self.parent_role, self.parent_path)
        self.inventory.bind_synchronizable(self.parent_role)
        self._parent_object_id = handle.identity.object_id

    @property
    def parent_object_id(self) -> str:
        if not self._parent_object_id:
            raise DescriptorRefused(
                "descriptor-not-registered",
                self.parent_role,
                "the recovery parent has not been opened, so there is no store "
                "to publish into and no basis to discover",
            )
        return self._parent_object_id

    # -- §2.3.3's ordered sequence -------------------------------------------

    def publish(
        self,
        *,
        run_id: str,
        reservation_id: str,
        captured_by: str,
        sources: Mapping[str, str],
        configuration_role: str,
        fail_at: str = "",
    ) -> StorePublication:
        """Capture, store and durably publish, in §2.3.3's exact order.

        `sources` maps each configuration file's **component name** to the
        absolute destination the record binds it to. The component is resolved
        under the configuration directory's held traversal descriptor, so no
        pathname is re-resolved between the check and the read.

        Every failure refuses **before M1**, and the refusal says which barrier
        did not return success. `fail_at` injects a failure at one barrier name,
        which is how the model's parametrized failure rows become mechanism
        rows.
        """
        crossed: list[str] = []
        # **Step 0 — PR-20260913-LABI-1.** The whole requested set is validated
        # against the reviewed one *before* the run directory is created, so a
        # request this store will not publish leaves nothing behind at all.
        try:
            bound = self._validate_capture_set(sources)
        except _CaptureRefused as refusal:
            return StorePublication(
                published=False,
                mutation_permitted=False,
                refusal=refusal.classification,
                reasons=refusal.reasons,
                run_directory_name=run_id,
            )
        try:
            run_role = f"runstore:{run_id}"
            self._create_run_directory(run_id, run_role)
            self._entry_barrier(
                "recovery-parent-entry", self.parent_role, crossed, fail_at
            )

            captures: list[CapturedSource] = []
            for name in sorted(bound):
                destination = bound[name]
                capture, buffer = self._capture(
                    name, destination, configuration_role
                )
                self._store_copy(run_role, capture, buffer, crossed, fail_at)
                self._store_record(
                    run_role,
                    run_id=run_id,
                    reservation_id=reservation_id,
                    captured_by=captured_by,
                    capture=capture,
                    crossed=crossed,
                    fail_at=fail_at,
                )
                captures.append(capture)
        except _CaptureRefused as refusal:
            return StorePublication(
                published=False,
                mutation_permitted=False,
                barriers_crossed=tuple(crossed),
                refusal=refusal.classification,
                reasons=refusal.reasons,
                run_directory_name=run_id,
            )
        except DescriptorRefused as refusal:
            return StorePublication(
                published=False,
                mutation_permitted=False,
                barriers_crossed=tuple(crossed),
                refusal=CAPTURE_BARRIER_FAILED,
                reasons=(refusal.classification,),
                run_directory_name=run_id,
            )

        # Step 11 — **a verification, not a barrier.** It establishes that the
        # bytes written are the bytes captured and nothing about durability, so
        # it happens after every barrier and never in place of one.
        unverified = self._verify(run_role, captures)
        if unverified:
            return StorePublication(
                published=False,
                mutation_permitted=False,
                barriers_crossed=tuple(crossed),
                refusal=CAPTURE_VERIFICATION_FAILED,
                reasons=unverified,
                run_directory_name=run_id,
                captures=tuple(captures),
            )
        # **PR-20260913-LABI-1.** The second half of the verification, and the
        # half the finding found missing: the record/copy/destination
        # correspondence restoration consumes, established here rather than
        # discovered at restore time when the mutation has already happened.
        unbound = self._verify_correspondence(run_role, captures, run_id)
        if unbound:
            return StorePublication(
                published=False,
                mutation_permitted=False,
                barriers_crossed=tuple(crossed),
                refusal=CAPTURE_CORRESPONDENCE_FAILED,
                reasons=unbound,
                run_directory_name=run_id,
                captures=tuple(captures),
            )

        complete = all(name in crossed for name in BARRIER_ORDER)
        published_set = tuple(sorted(capture.name for capture in captures))
        exact = published_set == tuple(sorted(self._reviewed().components))
        return StorePublication(
            published=complete and exact,
            mutation_permitted=complete and exact,
            barriers_crossed=tuple(crossed),
            run_directory_name=run_id,
            captures=tuple(captures),
        )

    # -- §2.5's restart discovery --------------------------------------------

    def discover(self) -> tuple[DiscoveredRun, ...]:
        """List the recovery parent. **The listing is the discovery mechanism.**

        No index file is read and none is proposed, because an index is a second
        thing that can be lost or disagree. An entry the parent never
        synchronized is not in the listing, which is exactly why barrier 1
        exists.
        """
        found: list[DiscoveredRun] = []
        for name in self.inventory.listing(self.parent_role):
            found.append(self._discover_one(name))
        return tuple(found)

    def read_record(self, run_id: str, record_name: str) -> RecoveryRecord:
        """One stored record, decoded. A malformed record verifies nothing."""
        role = self._adopt_run_directory(run_id)
        traversal = self.inventory.traversal(role)
        descriptor = self.filesystem.openat(
            traversal, record_name, DescriptorMode.O_RDONLY
        )
        try:
            return RecoveryRecord.decoded(self.filesystem.read(descriptor.number))
        finally:
            self.filesystem.close(descriptor.number)

    def read_copy(self, run_id: str, copy_name: str) -> bytes:
        """One stored copy's bytes, read **once**, into one held buffer."""
        role = self._adopt_run_directory(run_id)
        traversal = self.inventory.traversal(role)
        descriptor = self.filesystem.openat(
            traversal, copy_name, DescriptorMode.O_RDONLY
        )
        try:
            return self.filesystem.read(descriptor.number)
        finally:
            self.filesystem.close(descriptor.number)

    # -- internals ------------------------------------------------------------

    def _reviewed(self) -> ConfigurationCaptureSet:
        """The reviewed set, or a refusal. There is no third answer."""
        if self.capture_set is None:
            raise _CaptureRefused(
                CAPTURE_SET_NOT_BOUND,
                (
                    "no reviewed configuration capture set is bound to this "
                    "store, so there is nothing a request can be compared with. "
                    "The set is established at the integration boundary and a "
                    "caller never supplies it.",
                ),
            )
        return self.capture_set

    def _validate_capture_set(self, sources: Mapping[str, str]) -> dict[str, str]:
        """**PR-20260913-LABI-1.** The whole requested set, before anything exists.

        Every shape the finding names refuses here: an unbound store, a missing
        component, an additional one, a duplicated destination, a malformed
        component, a destination outside the reviewed directory and a
        destination whose basename is not its component. The return value is the
        **derived** mapping, so what is captured afterwards is the reviewed
        destination rather than the requested one even when the two agree.
        """
        reviewed = self._reviewed()
        duplicated = reviewed.duplicated
        if duplicated:
            raise _CaptureRefused(
                CAPTURE_DESTINATION_DUPLICATED,
                (
                    "the reviewed capture set names a component more than once, "
                    "so one destination would be captured and restored twice. "
                    "The set is refused rather than de-duplicated.",
                ),
            )
        requested = dict(sources)
        for component in requested:
            _require_capture_component(component)
        unreviewed = sorted(set(requested) - set(reviewed.components))
        if unreviewed:
            raise _CaptureRefused(
                CAPTURE_COMPONENT_NOT_REVIEWED,
                (
                    "the request names a configuration component the reviewed "
                    "capture set does not, so it would publish a basis for a "
                    "file nobody approved capturing.",
                ),
            )
        missing = sorted(set(reviewed.components) - set(requested))
        if missing:
            raise _CaptureRefused(
                CAPTURE_SET_INCOMPLETE,
                (
                    "the request does not name every reviewed configuration "
                    "component. A partial basis restores a mixed configuration, "
                    "so the publication refuses rather than covering some of "
                    "the files the mutation will change.",
                ),
            )
        seen: set[str] = set()
        for component, destination in requested.items():
            expected = reviewed.destination_for(component)
            if destination != expected:
                raise _CaptureRefused(
                    CAPTURE_DESTINATION_NOT_BOUND,
                    (
                        "a requested destination is not the one the reviewed "
                        "capture set binds this component to. A caller does not "
                        "choose where a record says its bytes go: an arbitrary, "
                        "cross-directory, relative or empty destination is a "
                        "record restoration must refuse, and a record "
                        "restoration must refuse is not a recovery basis.",
                    ),
                )
            if expected in seen:
                raise _CaptureRefused(
                    CAPTURE_DESTINATION_DUPLICATED,
                    (
                        "two requested components name one destination, so the "
                        "set does not bind each reviewed file exactly once.",
                    ),
                )
            seen.add(expected)
        return {name: reviewed.destination_for(name) for name in requested}

    def _verify_correspondence(
        self, run_role: str, captures: Sequence[CapturedSource], run_id: str
    ) -> tuple[str, ...]:
        """Read back every record and establish the binding restoration consumes.

        Four facts per component, and all four: the record decodes; it names
        **this** run; it names the reviewed destination for the copy it is filed
        beside; and its digest and byte length are the capture's. Plus one fact
        about the directory as a whole: it holds exactly the reviewed set's
        names and nothing else, so a leftover temporary or an extra object is a
        refusal rather than something discovery meets later.
        """
        reviewed = self._reviewed()
        reasons: list[str] = []
        held = set(self.inventory.listing(run_role))
        if held != set(reviewed.stored_names()):
            reasons.append(DISCOVERY_SET_INCOMPLETE)
        destinations: set[str] = set()
        for capture in captures:
            name = f"{capture.name}{RECORD_SUFFIX}"
            try:
                record = self.read_record(run_id, name)
            except Exception:
                reasons.append(DISCOVERY_RECORD_UNDECODABLE)
                continue
            if record.run_id != run_id:
                reasons.append(DISCOVERY_WRONG_RUN_ID)
            if record.destination != reviewed.destination_for(capture.name):
                reasons.append(DISCOVERY_DESTINATION_NOT_BOUND)
            elif record.destination in destinations:
                reasons.append(DISCOVERY_DESTINATION_DUPLICATED)
            else:
                destinations.add(record.destination)
            if (
                record.content_digest != capture.digest
                or record.byte_length != capture.byte_length
            ):
                reasons.append(DISCOVERY_DIGEST_MISMATCH)
        return tuple(dict.fromkeys(reasons))

    def _create_run_directory(self, run_id: str, role: str) -> None:
        try:
            self.inventory.create_directory(
                parent_role=self.parent_role,
                name=run_id,
                role=role,
                mode=RUN_DIRECTORY_MODE,
            )
        except DescriptorRefused as refusal:
            if refusal.classification == "object-already-exists":
                raise _CaptureRefused(
                    CAPTURE_RUN_DIRECTORY_EXISTS,
                    (
                        "a run id that already has a directory is a run id that "
                        "was used. Exclusive creation refuses rather than "
                        "publishing a second basis under one name.",
                    ),
                ) from None
            raise _CaptureRefused(
                CAPTURE_PARENT_UNAVAILABLE,
                (
                    "the recovery parent could not be written. It is a "
                    "provisioned directory and this mechanism never creates "
                    "one, so an absent or unwritable parent refuses the first "
                    "mutation rather than proceeding without a basis.",
                ),
            ) from None
        self.inventory.bind_synchronizable(role)

    def _adopt_run_directory(self, run_id: str) -> str:
        role = f"runstore:{run_id}"
        if role in self.inventory.roles():
            return role
        self.inventory.adopt_directory(
            parent_role=self.parent_role, name=run_id, role=role
        )
        return role

    def _capture(
        self, name: str, destination: str, configuration_role: str
    ) -> tuple[CapturedSource, bytes]:
        """§2.3.3 steps 5-8: open, record identity, read once, re-check, digest.

        The buffer is **returned**, not re-read later. Everything downstream —
        the digest, the stored copy and the record — is computed from this one
        buffer, so there is no second read of any pathname between the check and
        the write.
        """
        traversal = self.inventory.traversal(configuration_role)
        try:
            descriptor = self.filesystem.openat(
                traversal, name, DescriptorMode.O_RDONLY
            )
        except DescriptorRefused:
            raise _CaptureRefused(
                CAPTURE_SOURCE_UNREADABLE,
                (
                    "the configuration file this run would mutate could not be "
                    "opened through the held directory descriptor, so no "
                    "recoverable copy exists and the mutation refuses.",
                ),
            ) from None
        try:
            before = os.fstat(descriptor.number)
            if before.st_size > MAX_MATERIALIZED_BYTES:
                raise _CaptureRefused(
                    CAPTURE_TOO_LARGE,
                    (
                        "the source is larger than the reviewed bound. It is "
                        "refused rather than truncated, because a partial copy "
                        "is a recovery basis that restores the wrong file.",
                    ),
                )
            buffer = self.filesystem.read(descriptor.number)
            after = os.fstat(descriptor.number)
            # A consistency check on the read, **not** a substitution check: the
            # descriptor cannot have moved. A short read, a read error or a
            # changed size or mtime refuses and is never retried, because a
            # retry reads a possibly different file.
            if (before.st_size, before.st_mtime_ns) != (
                after.st_size,
                after.st_mtime_ns,
            ) or len(buffer) != before.st_size:
                raise _CaptureRefused(
                    CAPTURE_SOURCE_CHANGED,
                    (
                        "the source's size or modification time changed across "
                        "the read, so the buffer is not a consistent copy of "
                        "any one state of the file.",
                    ),
                )
            identity = (
                f"{before.st_dev}:{before.st_ino}:{before.st_size}:"
                f"{before.st_mtime_ns}"
            )
        finally:
            self.filesystem.close(descriptor.number)
        return (
            CapturedSource(
                name=name,
                destination=destination,
                identity=identity,
                # Computed over **the buffer**, never over a re-read.
                digest=hashlib.sha256(buffer).hexdigest(),
                byte_length=len(buffer),
            ),
            buffer,
        )

    def _store_copy(
        self,
        run_role: str,
        capture: CapturedSource,
        buffer: bytes,
        crossed: list[str],
        fail_at: str,
    ) -> None:
        fd = self._write_object(run_role, capture.name, buffer)
        self._data_barrier("copy-data", fd, crossed, fail_at)
        self._publish_object(run_role, capture.name)
        self._entry_barrier("copy-entry", run_role, crossed, fail_at)

    def _store_record(
        self,
        run_role: str,
        *,
        run_id: str,
        reservation_id: str,
        captured_by: str,
        capture: CapturedSource,
        crossed: list[str],
        fail_at: str,
    ) -> None:
        record = RecoveryRecord(
            run_id=run_id,
            destination=capture.destination,
            source_identity=capture.identity,
            content_digest=capture.digest,
            byte_length=capture.byte_length,
            captured_by=f"{captured_by}@{reservation_id}",
        )
        name = f"{capture.name}{RECORD_SUFFIX}"
        fd = self._write_object(run_role, name, record.encoded())
        self._data_barrier("record-data", fd, crossed, fail_at)
        self._publish_object(run_role, name)
        self._entry_barrier("record-entry", run_role, crossed, fail_at)

    def _write_object(self, run_role: str, name: str, data: bytes) -> int:
        """Write the temporary exclusively and set its mode **on the descriptor**.

        `fchmod` rather than a `chmod` by name: the mode lands on the object the
        descriptor holds, so a replacement of the name after the creation cannot
        receive it. That is B2, applied to the one effect between the write and
        the rename.
        """
        traversal = self.inventory.traversal(run_role)
        descriptor = self.filesystem.create_file(traversal, f"{name}{TEMPORARY_SUFFIX}")
        try:
            self.filesystem.write(descriptor.number, data)
            os.fchmod(descriptor.number, STORED_OBJECT_MODE)
        except (DescriptorRefused, OSError):
            self.filesystem.close(descriptor.number)
            raise
        return descriptor.number

    def _publish_object(self, run_role: str, name: str) -> None:
        traversal = self.inventory.traversal(run_role)
        self.filesystem.renameat(
            traversal, f"{name}{TEMPORARY_SUFFIX}", traversal, name, noreplace=True
        )

    def _data_barrier(
        self, name: str, fd: int, crossed: list[str], fail_at: str
    ) -> None:
        """`fsync` the bytes, on the `O_WRONLY` descriptor that wrote them."""
        if fail_at == name:
            self.filesystem.close(fd)
            raise _CaptureRefused(CAPTURE_BARRIER_FAILED, _barrier_reason(name))
        try:
            self.filesystem.fsync(fd, barrier=name)
        finally:
            self.filesystem.close(fd)
        _record_barrier(name, crossed)

    def _entry_barrier(
        self, name: str, role: str, crossed: list[str], fail_at: str
    ) -> None:
        """`fsync` the containing entry, on the bound `O_RDONLY` descriptor."""
        if fail_at == name:
            raise _CaptureRefused(CAPTURE_BARRIER_FAILED, _barrier_reason(name))
        self.inventory.fsync_entry(role)
        _record_barrier(name, crossed)

    def _verify(
        self, run_role: str, captures: Sequence[CapturedSource]
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        traversal = self.inventory.traversal(run_role)
        for capture in captures:
            descriptor = self.filesystem.openat(
                traversal, capture.name, DescriptorMode.O_RDONLY
            )
            try:
                stored = self.filesystem.read(descriptor.number)
            finally:
                self.filesystem.close(descriptor.number)
            if hashlib.sha256(stored).hexdigest() != capture.digest:
                reasons.append(
                    "the stored copy does not digest to the value the capture "
                    "computed over the buffer it read, so the store does not "
                    "hold the bytes the record binds."
                )
        return tuple(reasons)

    def _discover_one(self, run_id: str) -> DiscoveredRun:
        reasons: list[str] = []
        try:
            role = self._adopt_run_directory(run_id)
            names = self.inventory.listing(role)
        except DescriptorRefused as refusal:
            return DiscoveredRun(
                run_id=run_id,
                record_names=(),
                copy_names=(),
                reasons=(refusal.classification,),
            )
        record_names = tuple(name for name in names if name.endswith(RECORD_SUFFIX))
        copy_names = tuple(
            name
            for name in names
            if not name.endswith(RECORD_SUFFIX) and not name.endswith(TEMPORARY_SUFFIX)
        )
        leftovers = tuple(name for name in names if name.endswith(TEMPORARY_SUFFIX))
        if leftovers:
            reasons.append(DISCOVERY_LEFTOVER_TEMPORARY)
        # **PR-20260913-LABI-1.** Restart discovery applies the same binding the
        # publication does. A basis restoration would refuse is reported as not
        # usable here, rather than found at restore time after the mutation.
        reviewed = self.capture_set
        if reviewed is None:
            reasons.append(CAPTURE_SET_NOT_BOUND)
            return DiscoveredRun(
                run_id=run_id,
                record_names=record_names,
                copy_names=copy_names,
                reasons=tuple(reasons),
            )
        for copy_name in copy_names:
            if f"{copy_name}{RECORD_SUFFIX}" not in record_names:
                reasons.append(DISCOVERY_ORPHAN_COPY)
                break
        if set(names) != set(reviewed.stored_names()):
            reasons.append(DISCOVERY_SET_INCOMPLETE)
        records: list[RecoveryRecord] = []
        destinations: set[str] = set()
        verifiable = bool(record_names)
        for name in record_names:
            try:
                record = self.read_record(run_id, name)
            except Exception:
                reasons.append(DISCOVERY_RECORD_UNDECODABLE)
                verifiable = False
                continue
            records.append(record)
            copy_name = name[: -len(RECORD_SUFFIX)]
            if copy_name not in copy_names:
                reasons.append(DISCOVERY_ORPHAN_RECORD)
                verifiable = False
                continue
            if record.run_id != run_id:
                reasons.append(DISCOVERY_WRONG_RUN_ID)
                verifiable = False
                continue
            component = reviewed.component_for(record.destination)
            if not component:
                reasons.append(DISCOVERY_DESTINATION_NOT_BOUND)
                verifiable = False
                continue
            if component != copy_name:
                reasons.append(DISCOVERY_COPY_NAME_MISMATCH)
                verifiable = False
                continue
            if record.destination in destinations:
                reasons.append(DISCOVERY_DESTINATION_DUPLICATED)
                verifiable = False
                continue
            destinations.add(record.destination)
            stored = self.read_copy(run_id, copy_name)
            if (
                hashlib.sha256(stored).hexdigest() != record.content_digest
                or len(stored) != record.byte_length
            ):
                reasons.append(DISCOVERY_DIGEST_MISMATCH)
                verifiable = False
        reasons = list(dict.fromkeys(reasons))
        return DiscoveredRun(
            run_id=run_id,
            record_names=record_names,
            copy_names=copy_names,
            records=tuple(records),
            verifiable=verifiable and not reasons,
            reasons=tuple(reasons),
        )


class _CaptureRefused(Exception):
    """Internal control flow for a refusal that carries its classification."""

    def __init__(self, classification: str, reasons: tuple[str, ...]) -> None:
        if classification not in CAPTURE_REFUSALS:
            raise ValueError(f"{classification!r} is not a capture refusal.")
        self.classification = classification
        self.reasons = reasons
        super().__init__(classification)


__all__ = [
    "BARRIER_ORDER",
    "CAPTURE_BARRIER_FAILED",
    "CAPTURE_COMPONENT_MALFORMED",
    "CAPTURE_COMPONENT_NOT_REVIEWED",
    "CAPTURE_CORRESPONDENCE_FAILED",
    "CAPTURE_DESTINATION_DUPLICATED",
    "CAPTURE_DESTINATION_NOT_BOUND",
    "CAPTURE_PARENT_UNAVAILABLE",
    "CAPTURE_REFUSALS",
    "CAPTURE_RUN_DIRECTORY_EXISTS",
    "CAPTURE_SET_INCOMPLETE",
    "CAPTURE_SET_NOT_BOUND",
    "CAPTURE_SOURCE_CHANGED",
    "CAPTURE_SOURCE_UNREADABLE",
    "CAPTURE_TOO_LARGE",
    "CAPTURE_VERIFICATION_FAILED",
    "DESTINATION_BINDING_RULE",
    "DISCOVERY_COPY_NAME_MISMATCH",
    "DISCOVERY_DESTINATION_DUPLICATED",
    "DISCOVERY_DESTINATION_NOT_BOUND",
    "DISCOVERY_DIGEST_MISMATCH",
    "DISCOVERY_LEFTOVER_TEMPORARY",
    "DISCOVERY_ORPHAN_COPY",
    "DISCOVERY_ORPHAN_RECORD",
    "DISCOVERY_REASONS",
    "DISCOVERY_RECORD_UNDECODABLE",
    "DISCOVERY_SET_INCOMPLETE",
    "DISCOVERY_WRONG_RUN_ID",
    "RECORD_SUFFIX",
    "RUN_DIRECTORY_MODE",
    "STORED_OBJECT_MODE",
    "TEMPORARY_SUFFIX",
    "CapturedSource",
    "ConfigurationCaptureSet",
    "DiscoveredRun",
    "RecoveryStore",
    "StorePublication",
]
