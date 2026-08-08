"""The filesystem artifact store: naming, containment, atomicity and cleanup.

Every test here uses a per-test temporary directory and synthetic bytes. Nothing
scans, reads or ingests an existing export directory, and no real artifact is
involved at any point.

## The ancestor rule, and why most tests here bound it

`ensure_ready()` walks the directories *above* the artifact root and refuses
unless each is owned by `root` or this account and is not writable by others
without the sticky bit. On a conventional host that is `/tmp` (1777, `root`) and
`/` (0755, `root`), and it passes. The second review of this package ran the
suite on a host where both are owned by `nobody`, and **thirty-two tests failed
at that gate before reaching their own assertions** — tests about publication,
durability, anchoring and descriptor lifetime, none of them about ancestors.
`--basetemp` does not help: every absolute path has host ancestors.

So the store takes the rule as an object, `TrustedAncestors`, and the `store`
fixture below bounds its walk at pytest's own temporary root. Below that
boundary the *real* rule runs against *real* `os.lstat` results on directories
the test itself created; above it, the host's business is the host's. Nothing is
globally monkeypatched, so the root and target checks — which are what these
tests are about — keep testing real filesystem behaviour.

The rule itself is not thereby untested. It is exercised directly, on real
directories with real modes, in "the ancestor rule, tested directly" below, and
against the actual configured pathname with the production unbounded walk in
`test_the_production_walk_checks_the_real_configured_path`.
"""
from __future__ import annotations

import ast
import hashlib
import os
import shutil
import stat
import subprocess
import time
from pathlib import Path

import pytest

from adapters.artifacts.filesystem import (
    ARTIFACT_MODE,
    ROOT_MODE,
    FilesystemArtifactStore,
    TrustedAncestors,
)
from application.artifacts import (
    ArtifactNotStored,
    ArtifactStorageError,
    StorageOutcome,
)
from application.foundry.artifact import ingest_bytes
from tests import foundry_fixtures as fixtures

#: The temporary-file prefix the store publishes through. Named here so that the
#: race tests can recognise the window without importing a private constant.
TEMPORARY_PREFIX = ".incoming-"


@pytest.fixture()
def ancestors(tmp_path_factory) -> TrustedAncestors:
    """The real ancestor rule, bounded at pytest's temporary root.

    See the module docstring. `getbasetemp()` rather than a fixed path so this
    holds under `--basetemp` too.
    """
    return TrustedAncestors(ceiling=tmp_path_factory.getbasetemp())


@pytest.fixture()
def anchored(ancestors):
    """Build a store whose ancestor walk is bounded, at any root."""

    made: list[FilesystemArtifactStore] = []

    def build(root: Path, **keywords) -> FilesystemArtifactStore:
        keywords.setdefault("ancestors", ancestors)
        store = FilesystemArtifactStore(root, **keywords)
        made.append(store)
        return store

    yield build
    for store in made:
        store.close()


@pytest.fixture()
def store(tmp_path: Path, anchored) -> FilesystemArtifactStore:
    return anchored(tmp_path / "artifacts")


def artifact(payload: bytes | None = None):
    return ingest_bytes(payload or fixtures.encode(fixtures.bundle()))


def test_stores_under_the_checksum_and_ignores_any_caller_name(store, tmp_path):
    data = fixtures.encode(fixtures.bundle())
    stored = ingest_bytes(data, source_name="operator-chosen.json")

    reference = store.store(stored)

    checksum = hashlib.sha256(data).hexdigest()
    assert reference == f"snapshot/{checksum}.json"
    assert (store.root / f"{checksum}.json").read_bytes() == data
    # The caller's name influenced nothing.
    assert not (store.root / "operator-chosen.json").exists()


def test_the_reference_is_opaque_and_carries_no_host_path(store):
    reference = store.store(artifact())
    assert not reference.startswith("/")
    assert str(store.root) not in reference


def test_storing_the_same_bytes_twice_is_one_file_and_one_reference(store):
    first = store.store(artifact())
    second = store.store(artifact())

    assert first == second
    assert len(list(store.root.glob("*.json"))) == 1


def test_two_different_documents_are_two_artifacts(store):
    other = fixtures.encode(
        fixtures.bundle(actors=(fixtures.actor(fixtures.SECOND_ACTOR_ID),))
    )
    store.store(artifact())
    store.store(artifact(other))

    assert len(list(store.root.glob("*.json"))) == 2


def test_load_returns_the_exact_bytes_and_re_verifies_them(store):
    data = fixtures.encode(fixtures.bundle())
    checksum = store.store(artifact(data))[len("snapshot/") : -len(".json")]

    loaded = store.load(checksum)

    assert loaded.raw_bytes() == data
    assert loaded.checksum.hex_digest == checksum


def test_a_corrupted_stored_file_is_refused_rather_than_served(store):
    data = fixtures.encode(fixtures.bundle())
    checksum = hashlib.sha256(data).hexdigest()
    store.store(artifact(data))
    (store.root / f"{checksum}.json").write_bytes(b'{"tampered":true}\n')

    with pytest.raises(ArtifactStorageError) as refusal:
        store.load(checksum)
    assert refusal.value.reason == "checksum_mismatch"


def test_an_absent_artifact_is_a_typed_not_stored(store):
    with pytest.raises(ArtifactNotStored):
        store.load("a" * 64)
    assert store.contains("a" * 64) is False


def test_a_checksum_that_is_not_a_digest_cannot_build_a_path(store):
    for candidate in ("../escape", "a" * 63, "A" * 64, "", "x/y", "a" * 64 + "b"):
        with pytest.raises(ArtifactStorageError) as refusal:
            store.load(candidate)
        assert refusal.value.reason == "invalid_checksum"


def test_permissions_are_restrictive_on_the_root_and_on_each_artifact(store):
    reference = store.store(artifact())
    name = reference.removeprefix("snapshot/")

    assert stat.S_IMODE(store.root.stat().st_mode) == ROOT_MODE
    assert stat.S_IMODE((store.root / name).stat().st_mode) == ARTIFACT_MODE


def test_no_temporary_file_survives_a_successful_write(store):
    store.store(artifact())
    assert list(store.root.glob(".incoming-*")) == []


def refuse_publication(monkeypatch, error: OSError) -> None:
    """Make the publication of the checksum entry fail.

    Publication is `os.link` — see "Publication never overwrites" in the
    adapter. It used to be `os.replace`; injecting into the wrong primitive would
    silently inject nothing and let the store succeed, which is why this is one
    helper rather than a call site per test.
    """

    def refuse(source, destination, **keywords):
        raise error

    monkeypatch.setattr(os, "link", refuse)


def test_a_failed_publication_cleans_up_and_publishes_nothing(store, monkeypatch):
    """An injected mid-write failure leaves neither an artifact nor a temporary."""
    refuse_publication(monkeypatch, OSError("injected publication failure"))

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    assert refusal.value.reason == "write_failed"
    assert refusal.value.outcome is StorageOutcome.UNCHANGED
    assert list(store.root.glob("*.json")) == []
    assert list(store.root.glob(".incoming-*")) == []


def test_a_storage_failure_message_carries_no_path_or_os_detail(store, monkeypatch):
    refuse_publication(
        monkeypatch,
        OSError(13, "Permission denied", str(store.root / "secret.json")),
    )
    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    message = str(refusal.value)
    assert "secret.json" not in message
    assert str(store.root) not in message
    assert "Permission denied" not in message
    assert refusal.value.__cause__ is None


def test_the_root_must_be_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="absolute"):
        FilesystemArtifactStore(Path("artifacts"))


def test_the_root_must_be_outside_the_repository(tmp_path):
    repository = tmp_path / "repo"
    (repository / "artifacts").mkdir(parents=True)

    with pytest.raises(ValueError, match="outside this repository"):
        FilesystemArtifactStore(
            repository / "artifacts", repository_root=repository
        )


def test_the_real_repository_root_is_refused_by_default():
    """The default guard names *this* repository, not a test fixture's."""
    inside = Path(__file__).resolve().parents[1] / "docs"
    with pytest.raises(ValueError, match="outside this repository"):
        FilesystemArtifactStore(inside)


def test_there_is_no_listing_or_delete_on_the_store(store):
    """The port's surface is the control; a listing is half an exfiltration."""
    for absent in ("list", "delete", "remove", "open", "path_for"):
        assert not hasattr(store, absent)


# -- restricted storage, enforced rather than asserted (S-B-2) ----------------
#
# The previous permission test created a fresh temporary root and could
# therefore only observe what this store had just done. These exercise the cases
# it could not see: a root or a target that was *already there*, in a state
# nobody here chose. Every mode below is set explicitly, so nothing depends on
# what `tmp_path` happens to be created as.


def checksum_name() -> str:
    return f"{hashlib.sha256(fixtures.encode(fixtures.bundle())).hexdigest()}.json"


def test_a_fresh_root_is_created_private_and_usable(tmp_path, anchored):
    store = anchored(tmp_path / "fresh")
    store.ensure_ready()

    assert stat.S_IMODE(store.root.stat().st_mode) == ROOT_MODE
    store.store(artifact())
    assert len(list(store.root.glob("*.json"))) == 1


def test_a_safe_pre_existing_root_is_accepted(tmp_path, anchored):
    root = tmp_path / "existing"
    root.mkdir()
    root.chmod(ROOT_MODE)

    store = anchored(root)
    store.ensure_ready()
    store.store(artifact())

    assert len(list(root.glob("*.json"))) == 1


@pytest.mark.parametrize("mode", [0o755, 0o750, 0o701, 0o770, 0o777])
def test_a_permissive_pre_existing_root_fails_closed(tmp_path, mode, anchored):
    """Any bit granted to group or other. The whole guarantee is that no other
    account on the host can list or read this directory."""
    root = tmp_path / "permissive"
    root.mkdir()
    root.chmod(mode)
    store = anchored(root)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.ensure_ready()
    assert refusal.value.reason == "root_permissive"

    # And on the request path too, not only at startup: a mode can change while
    # the process is running, and only the second check is in front of a write.
    root.chmod(ROOT_MODE)
    store.ensure_ready()
    root.chmod(mode)
    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "root_permissive"


def test_a_root_owned_by_another_account_fails_closed(tmp_path, monkeypatch, anchored):
    """Exercised by moving *this* process's identity rather than by chowning the
    directory, which needs privilege this suite must never require or hold."""
    root = tmp_path / "elsewhere"
    root.mkdir()
    root.chmod(ROOT_MODE)
    store = anchored(root)
    monkeypatch.setattr(os, "geteuid", lambda: os.getuid() + 1)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.ensure_ready()
    assert refusal.value.reason == "root_not_owned"


def test_a_root_that_is_not_a_directory_fails_closed(tmp_path, anchored):
    path = tmp_path / "afile"
    path.write_bytes(b"")
    path.chmod(0o600)
    store = anchored(path)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.ensure_ready()
    assert refusal.value.reason == "root_not_a_directory"


def test_a_symlinked_root_is_refused_at_configuration_time(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    real.chmod(ROOT_MODE)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)

    with pytest.raises(ValueError, match="symbolic link"):
        FilesystemArtifactStore(link)


def test_a_symlinked_parent_of_the_root_is_refused_too(tmp_path):
    """The redirect does not have to be the last component to be a redirect."""
    real = tmp_path / "realparent"
    real.mkdir()
    link = tmp_path / "linkparent"
    link.symlink_to(real, target_is_directory=True)

    with pytest.raises(ValueError, match="symbolic link"):
        FilesystemArtifactStore(link / "artifacts")


def test_a_permissive_existing_target_is_refused_rather_than_served(store):
    """The case the old test could not reach: a pre-existing artifact holding
    every exported Actor's mechanics, readable by another account."""
    store.store(artifact())
    target = store.root / checksum_name()
    target.chmod(0o644)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "artifact_permissive"

    with pytest.raises(ArtifactStorageError) as refusal:
        store.load(target.name.removesuffix(".json"))
    assert refusal.value.reason == "artifact_permissive"


def test_an_existing_target_owned_by_another_account_is_refused(store, monkeypatch):
    store.store(artifact())
    monkeypatch.setattr(os, "geteuid", lambda: os.getuid() + 1)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason in {"root_not_owned", "artifact_not_owned"}


def test_a_non_regular_target_is_refused(store):
    store.ensure_ready()
    (store.root / checksum_name()).mkdir()

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "artifact_not_a_regular_file"


def test_a_symlinked_target_is_refused_and_never_followed(store, tmp_path):
    """`O_NOFOLLOW`: a checksum-named symlink is a name pointing at a file this
    store did not write, whatever it points at."""
    store.ensure_ready()
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_bytes(fixtures.encode(fixtures.bundle()))
    elsewhere.chmod(0o600)
    (store.root / checksum_name()).symlink_to(elsewhere)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "artifact_untrusted"
    # The target of the link was neither read nor replaced.
    assert elsewhere.read_bytes() == fixtures.encode(fixtures.bundle())


def test_an_existing_target_with_the_wrong_content_is_refused(store):
    store.store(artifact())
    target = store.root / checksum_name()
    target.write_bytes(b'{"tampered":true}\n')
    target.chmod(ARTIFACT_MODE)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "checksum_mismatch"


def test_a_safe_existing_target_is_reused_idempotently(store):
    first = store.store(artifact())
    second = store.store(artifact())

    assert first == second
    assert len(list(store.root.glob("*.json"))) == 1
    assert stat.S_IMODE((store.root / checksum_name()).stat().st_mode) == ARTIFACT_MODE


def test_no_unsafe_state_is_repaired_silently(store):
    """Refusal, not repair. Widening or narrowing a directory an operator
    configured is an authority this process was never granted."""
    store.store(artifact())
    target = store.root / checksum_name()
    target.chmod(0o644)

    with pytest.raises(ArtifactStorageError):
        store.store(artifact())

    assert stat.S_IMODE(target.stat().st_mode) == 0o644


def test_a_storage_refusal_names_a_reason_and_never_the_path(store):
    store.ensure_ready()
    (store.root / checksum_name()).mkdir()

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    message = str(refusal.value)
    assert str(store.root) not in message
    assert ".json" not in message
    assert refusal.value.__cause__ is None


def test_contains_does_not_follow_a_symlink(store, tmp_path):
    store.ensure_ready()
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_bytes(b"{}")
    checksum = checksum_name().removesuffix(".json")
    (store.root / checksum_name()).symlink_to(elsewhere)

    assert store.contains(checksum) is False


# -- durability is acknowledged or the submission fails (I-2) -----------------


def _fsync_refusing_directories(monkeypatch):
    """Fail `fsync` for a directory descriptor only, leaving file sync working."""
    real = os.fsync

    def selective(descriptor: int) -> None:
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            raise OSError(5, "injected directory fsync failure")
        real(descriptor)

    monkeypatch.setattr(os, "fsync", selective)


def test_a_directory_fsync_failure_refuses_the_store(store, monkeypatch):
    store.ensure_ready()
    _fsync_refusing_directories(monkeypatch)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "durability_unconfirmed"


def test_a_directory_open_failure_refuses_the_store(store, monkeypatch):
    """The root descriptor is now opened *before* anything is written, so a
    failure to open it is a distinct and earlier refusal than it used to be. The
    guarantee I-2 asked for is unchanged and stated more precisely: the store
    refuses, so the submission is refused and no row commits — and here nothing
    was written either, which `root_unavailable` may say and
    `durability_unconfirmed` may not."""
    real_open = os.open
    root = str(store.root)

    def selective(path, flags, *args, **kwargs):
        if str(path) == root:
            raise OSError(24, "injected directory open failure")
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", selective)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "root_unavailable"
    assert refusal.value.outcome is StorageOutcome.UNCHANGED


def test_an_unacknowledged_durability_failure_does_not_destroy_a_correct_target(
    store, monkeypatch
):
    """The rename already happened and the bytes under the checksum name are
    right. Deleting them because the *acknowledgement* failed would turn an
    unconfirmed success into a destroyed one."""
    store.ensure_ready()
    data = fixtures.encode(fixtures.bundle())
    _fsync_refusing_directories(monkeypatch)

    with pytest.raises(ArtifactStorageError):
        store.store(artifact())

    target = store.root / checksum_name()
    assert target.read_bytes() == data
    assert stat.S_IMODE(target.stat().st_mode) == ARTIFACT_MODE
    # And no temporary accumulated.
    assert list(store.root.glob(".incoming-*")) == []


def test_a_retry_after_a_durability_failure_completes_the_guarantee(
    store, monkeypatch
):
    """Content addressing is what makes the retry a retry: it finds the target,
    re-verifies it, and syncs the directory that could not be synced before."""
    store.ensure_ready()
    _fsync_refusing_directories(monkeypatch)
    with pytest.raises(ArtifactStorageError):
        store.store(artifact())

    monkeypatch.undo()
    synced: list[int] = []
    real = os.fsync

    def recording(descriptor: int) -> None:
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            synced.append(descriptor)
        real(descriptor)

    monkeypatch.setattr(os, "fsync", recording)

    reference = store.store(artifact())

    assert reference.endswith(".json")
    assert len(list(store.root.glob("*.json"))) == 1
    assert synced, "the retry must sync the directory it could not sync before"


# -- publication never overwrites an unvalidated entry (third review) ---------
#
# `_holds()` decides whether the checksum entry is already this artifact. The
# previous implementation then wrote a temporary and called
# `os.replace(temporary, name, …)`, which is atomic about *replacing*: anything
# that appeared under the checksum name in between was removed and overwritten
# without ever being looked at. That contradicted immutability, refusal-not-
# repair, evidence preservation and "no artifact is implicitly deleted", all at
# once.
#
# Publication is now `os.link`, which creates the entry or fails `EEXIST`.
# `EEXIST` sends the winner through the same full revalidation `_holds()` does.
#
# The tests below plant into the window *without naming the publication
# primitive* — the hook is the verification read of the temporary file, which is
# the last thing that happens before the entry is created in any implementation.
# That is deliberate: run these against the superseded `os.replace` publication
# and they fail, which is what makes them regression tests rather than a
# description of the current code.


def plant_before_publication(monkeypatch, action) -> None:
    """Run `action` in the window between `_holds()` and the entry's creation.

    Hooked on the verification re-read of the temporary file — `O_RDONLY` on a
    `.incoming-*` name, as opposed to the `O_CREAT` that made it. Fires once,
    after that open has returned, so the action lands strictly between the last
    look at the checksum name and the attempt to publish under it.
    """
    real_open = os.open
    fired: list[bool] = []

    def opening(path, flags, *args, **kwargs):
        descriptor = real_open(path, flags, *args, **kwargs)
        if (
            not fired
            and isinstance(path, str)
            and path.startswith(TEMPORARY_PREFIX)
            and not flags & os.O_CREAT
        ):
            fired.append(True)
            action()
        return descriptor

    monkeypatch.setattr(os, "open", opening)
    return fired


def identity_of(path: Path) -> tuple[int, int]:
    """Device and inode: what proves a file is the *same* file, not equal bytes."""
    info = os.lstat(path)
    return (info.st_dev, info.st_ino)


def plant(store, payload: bytes, *, mode: int = ARTIFACT_MODE) -> Path:
    """Put a file under the checksum name, as another writer would have."""
    target = store.root / checksum_name()
    target.write_bytes(payload)
    target.chmod(mode)
    return target


def test_a_valid_target_appearing_before_publication_is_reused_not_overwritten(
    store, monkeypatch
):
    """The blocking finding, in its benign form. Another writer publishes the
    identical artifact in the window. The correct outcome is to reuse *their*
    file: the bytes are right, and replacing them would be an unnecessary
    deletion of an artifact this store promises never to delete implicitly.

    `os.replace` publication passes the byte assertion and fails the inode one,
    which is why the inode is what is asserted."""
    data = fixtures.encode(fixtures.bundle())
    planted: list[tuple[int, int]] = []

    plant_before_publication(
        monkeypatch, lambda: planted.append(identity_of(plant(store, data)))
    )
    reference = store.store(artifact())

    target = store.root / checksum_name()
    assert reference == f"snapshot/{checksum_name()}"
    assert identity_of(target) == planted[0], (
        "the entry another writer published was removed and replaced; "
        "publication must not overwrite an entry it did not validate"
    )
    assert target.read_bytes() == data
    assert stat.S_IMODE(target.stat().st_mode) == ARTIFACT_MODE
    assert list(store.root.glob(".incoming-*")) == []
    assert len(list(store.root.glob("*.json"))) == 1


def test_a_mismatched_target_appearing_before_publication_is_refused_intact(
    store, monkeypatch
):
    """The dangerous form. Something is under the checksum name whose bytes are
    not that checksum — a corruption, a partial restore, an intrusion. It is
    evidence, and the submission must refuse rather than quietly destroy it."""
    wrong = b'{"tampered":true}\n'
    planted: list[Path] = []

    plant_before_publication(
        monkeypatch, lambda: planted.append(plant(store, wrong, mode=0o600))
    )
    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    target = planted[0]
    assert refusal.value.reason == "checksum_mismatch"
    assert refusal.value.outcome is StorageOutcome.PRESERVED
    # Exact bytes, exact mode, exact inode: nothing was repaired or replaced.
    assert target.read_bytes() == wrong
    assert stat.S_IMODE(target.stat().st_mode) == 0o600
    assert identity_of(target) == identity_of(store.root / checksum_name())
    assert list(store.root.glob(".incoming-*")) == []


def test_a_symlinked_target_appearing_before_publication_is_never_followed(
    store, tmp_path, monkeypatch
):
    """A symlink under the checksum name is a redirect, and `os.replace` would
    have removed it — losing the evidence and, worse, teaching nobody that
    somebody could put it there. `O_NOFOLLOW` on the anchored revalidation is
    what refuses it, and nothing writes through it."""
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_bytes(b"{}")
    elsewhere.chmod(0o600)

    def link_it() -> None:
        (store.root / checksum_name()).symlink_to(elsewhere)

    plant_before_publication(monkeypatch, link_it)
    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    target = store.root / checksum_name()
    assert refusal.value.reason == "artifact_untrusted"
    assert refusal.value.outcome is StorageOutcome.PRESERVED
    assert target.is_symlink(), "the link itself was removed or replaced"
    assert elsewhere.read_bytes() == b"{}", "the link was written through"
    assert list(store.root.glob(".incoming-*")) == []


def test_a_non_regular_target_appearing_before_publication_is_refused(
    store, monkeypatch
):
    """A directory under the checksum name. Not a file this store wrote,
    therefore not a file this store may remove."""
    plant_before_publication(
        monkeypatch, lambda: (store.root / checksum_name()).mkdir()
    )
    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    assert refusal.value.reason == "artifact_not_a_regular_file"
    assert refusal.value.outcome is StorageOutcome.PRESERVED
    assert (store.root / checksum_name()).is_dir()
    assert list(store.root.glob(".incoming-*")) == []


def test_a_permissive_target_appearing_before_publication_is_refused_intact(
    store, monkeypatch
):
    """Group- or other-readable: every exported Actor's mechanics, readable by
    another account. Refused, and left for the operator with its mode intact."""
    data = fixtures.encode(fixtures.bundle())
    planted: list[Path] = []

    plant_before_publication(
        monkeypatch, lambda: planted.append(plant(store, data, mode=0o644))
    )
    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    assert refusal.value.reason == "artifact_permissive"
    assert refusal.value.outcome is StorageOutcome.PRESERVED
    assert stat.S_IMODE(planted[0].stat().st_mode) == 0o644


def test_two_writers_of_identical_bytes_converge_on_one_artifact(
    store, anchored, tmp_path, monkeypatch
):
    """Concurrency, made deterministic: the second writer runs *inside* the
    first's publication window, on the same root, through its own store object
    and its own descriptor. Exactly one of them creates the entry; the other
    finds it, re-proves it, and reuses it."""
    other = anchored(tmp_path / "artifacts")
    other.ensure_ready()
    won: list[str] = []
    winners: list[tuple[int, int]] = []

    def race() -> None:
        won.append(other.store(artifact()))
        winners.append(identity_of(store.root / checksum_name()))

    plant_before_publication(monkeypatch, race)
    reference = store.store(artifact())

    assert won == [reference]
    assert len(list(store.root.glob("*.json"))) == 1
    assert identity_of(store.root / checksum_name()) == winners[0], (
        "the writer that lost the race replaced the winner's artifact instead "
        "of reusing it"
    )
    # Both cleanups are allowed to succeed here, and that precondition is the
    # whole reason this assertion is allowed to be absolute: `_discard` swallows
    # `OSError`, so nothing may claim in general that a store leaves no
    # temporary. See the operator-hygiene group below.
    assert list(store.root.glob(".incoming-*")) == [], (
        "with cleanup working, the writer that lost the race still left its "
        "temporary behind"
    )
    assert (store.root / checksum_name()).read_bytes() == fixtures.encode(
        fixtures.bundle()
    )
    assert store.load(checksum_name().removesuffix(".json")).raw_bytes() == (
        fixtures.encode(fixtures.bundle())
    )


def test_publication_stays_anchored_when_the_root_name_is_taken_over(
    store, tmp_path, monkeypatch
):
    """The two findings meet: the configured pathname is replaced inside the
    publication window. The entry must be created in the directory that was
    validated, and nothing at all may appear in the replacement."""
    moved: list[Path] = []

    plant_before_publication(
        monkeypatch,
        lambda: moved.append(replacement_directory(tmp_path, store.root)),
    )
    store.store(artifact())

    (trusted,) = moved
    assert (trusted / checksum_name()).read_bytes() == fixtures.encode(
        fixtures.bundle()
    )
    assert list(trusted.glob(".incoming-*")) == []
    assert list(store.root.iterdir()) == []


def test_cleanup_can_only_ever_remove_a_temporary(store, monkeypatch):
    """The structural half of "a cleanup failure cannot delete the published
    target": the unlink is never reached with a checksum name at all, on the
    success path or on a refusal."""
    removed: list[str] = []
    real_unlink = os.unlink

    def recording(path, *args, **kwargs):
        if isinstance(path, str):
            removed.append(path)
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", recording)
    store.store(artifact())

    other = fixtures.encode(
        fixtures.bundle(actors=(fixtures.actor(fixtures.SECOND_ACTOR_ID),))
    )
    refuse_publication(monkeypatch, OSError("injected publication failure"))
    with pytest.raises(ArtifactStorageError):
        store.store(artifact(other))

    assert removed, "nothing was cleaned up at all, so this proved nothing"
    assert all(name.startswith(TEMPORARY_PREFIX) for name in removed), removed


def test_a_failing_cleanup_leaves_the_published_artifact_alone(store, monkeypatch):
    """And the behavioural half. The temporary's removal is best effort; the
    artifact it published is not conditional on it."""
    data = fixtures.encode(fixtures.bundle())
    real_unlink = os.unlink

    def refuse(path, *args, **kwargs):
        if isinstance(path, str) and path.startswith(TEMPORARY_PREFIX):
            raise OSError(13, "injected cleanup failure")
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", refuse)
    reference = store.store(artifact())

    assert reference == f"snapshot/{checksum_name()}"
    assert (store.root / checksum_name()).read_bytes() == data
    # The temporary survived, which is the point: it is a leftover, not a
    # failure, and it is removed by the operator's ordinary hygiene. This is
    # also why no document may say a successful store leaves no temporary —
    # `test_the_hygiene_rule_finds_a_leftover_a_successful_store_left` below is
    # the procedure that has to find this file.
    assert len(list(store.root.glob(".incoming-*"))) == 1


# -- operator hygiene: finding what a failed cleanup left ---------------------
#
# `_discard` swallows `OSError` deliberately, so the removal of the temporary is
# best effort and the store never learns whether it worked. A `store()` that
# returned a reference may therefore have left one `.incoming-*` hard link to
# the published bytes, and a refusal may have left one to bytes that were never
# published. Neither is reachable through any route, and neither can touch the
# checksum entry — but both consume storage, so an operator has to be able to
# find them.
#
# The service is given no listing and no deletion capability for that: detection
# is a read-only filesystem procedure in
# `docs/operations/foundry-snapshot-submission.md` §5.6, "Temporary files left
# by a failed cleanup". These tests run that procedure's actual rule, through
# the real `find`, against synthetic files this test wrote. They add nothing to
# the application.

FIND = shutil.which("find")

#: The age bound in the documented rule. A `.incoming-*` file younger than this
#: is more likely a submission in flight than a leftover.
_LEFTOVER_AGE_MINUTES = 60


def _documented_leftover_rule(root: Path) -> list[tuple[str, str]]:
    """Operations §5.6's detection command — its **selection** exactly.

    `-maxdepth 1 -type f -name '.incoming-*' -mmin +60` is character for
    character what the procedure tells an operator to run, and it is the part
    that decides what gets deleted. Only `-printf` differs: the document prints
    size, timestamp and link count for a human, and this prints name and link
    count so the test can compare them. Nothing about *which files match*
    changes, and the link count — the thing the procedure's table is read from
    — is taken from the same `%n`.
    """
    completed = subprocess.run(
        [
            FIND,
            str(root),
            "-maxdepth",
            "1",
            "-type",
            "f",
            "-name",
            ".incoming-*",
            "-mmin",
            f"+{_LEFTOVER_AGE_MINUTES}",
            "-printf",
            "%f\t%n\n",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        (name, links)
        for name, _, links in (
            line.partition("\t") for line in completed.stdout.splitlines() if line
        )
    ]


def _age(path: Path, minutes: int) -> None:
    """Backdate a file so the rule's `-mmin` bound can be exercised at all."""
    when = time.time() - minutes * 60
    os.utime(path, (when, when))


def _refuse_temporary_unlinks(monkeypatch) -> None:
    """Make `_discard`'s `unlink` fail, exactly as an `EACCES` or `EROFS` would."""
    real_unlink = os.unlink

    def refuse(path, *args, **kwargs):
        if isinstance(path, str) and path.startswith(TEMPORARY_PREFIX):
            raise OSError(13, "injected cleanup failure")
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", refuse)


@pytest.mark.skipif(FIND is None, reason="`find` is not installed on this host")
def test_the_hygiene_rule_finds_a_leftover_a_successful_store_left(
    store, monkeypatch
):
    """The success-path case, which is the one the third re-review found the
    evidence had denied could happen. The store returns a reference, the
    artifact is published and correct, and one temporary survives — so the
    operator procedure must find it and must report **two** links, which is
    what tells the operator that removing it frees an inode and no bytes."""
    _refuse_temporary_unlinks(monkeypatch)
    reference = store.store(artifact())

    (leftover,) = store.root.glob(".incoming-*")
    _age(leftover, _LEFTOVER_AGE_MINUTES + 5)

    assert _documented_leftover_rule(store.root) == [(leftover.name, "2")]
    # And the published artifact is neither matched by the rule nor affected by
    # it: the procedure is read-only and names only temporaries.
    assert reference == f"snapshot/{checksum_name()}"
    assert (store.root / checksum_name()).read_bytes() == fixtures.encode(
        fixtures.bundle()
    )


@pytest.mark.skipif(FIND is None, reason="`find` is not installed on this host")
def test_the_hygiene_rule_reports_one_link_for_an_unpublished_leftover(
    store, monkeypatch
):
    """The failure-path case. Publication is refused and the cleanup then fails
    too, so the surviving temporary is the only name for those bytes. One link
    is what tells the operator that removing it frees the bytes themselves."""
    refuse_publication(monkeypatch, OSError("injected publication failure"))
    _refuse_temporary_unlinks(monkeypatch)
    with pytest.raises(ArtifactStorageError):
        store.store(artifact())

    (leftover,) = store.root.glob(".incoming-*")
    _age(leftover, _LEFTOVER_AGE_MINUTES + 5)

    assert _documented_leftover_rule(store.root) == [(leftover.name, "1")]
    assert list(store.root.glob("*.json")) == [], (
        "a refused publication must not have published anything"
    )


@pytest.mark.skipif(FIND is None, reason="`find` is not installed on this host")
def test_the_hygiene_rule_does_not_match_an_artifact_or_a_submission_in_flight(
    store, monkeypatch
):
    """The two false positives the rule has to avoid, because the operator's
    next step after it is deletion.

    A published artifact must never be matched — the procedure would otherwise
    talk an operator into deleting the thing the store exists to keep. And a
    `.incoming-*` file that is seconds old is more likely a submission in
    flight than a leftover, which is what the age bound is for: removing it
    would break a live upload.
    """
    store.store(artifact())
    assert list(store.root.glob("*.json")), "nothing was published, so this proved nothing"

    # An aged artifact under its checksum name: matched by neither the name
    # pattern nor anything else in the rule.
    _age(store.root / checksum_name(), _LEFTOVER_AGE_MINUTES + 5)
    assert _documented_leftover_rule(store.root) == []

    # A brand-new temporary, standing in for a submission currently writing.
    in_flight = store.root / f"{TEMPORARY_PREFIX}{os.getpid()}-inflight"
    in_flight.write_bytes(b"{}")
    in_flight.chmod(ARTIFACT_MODE)

    assert _documented_leftover_rule(store.root) == []

    _age(in_flight, _LEFTOVER_AGE_MINUTES + 5)
    assert _documented_leftover_rule(store.root) == [(in_flight.name, "1")]


def test_a_startup_probe_proves_publication_refuses_to_overwrite(
    tmp_path, anchored, monkeypatch
):
    """A filesystem without hard links, or one whose link silently replaces,
    cannot give this store its guarantee. Startup says so, in front of an
    operator, rather than an upload discovering it."""
    store = anchored(tmp_path / "artifacts")

    def replacing(source, destination, **keywords):
        return None  # succeeds a second time: no `EEXIST`, so no guarantee

    monkeypatch.setattr(os, "link", replacing)
    with pytest.raises(ArtifactStorageError) as refusal:
        store.ensure_ready()
    assert refusal.value.reason == "link_unsupported"

    def unsupported(source, destination, **keywords):
        raise OSError(95, "injected: hard links unsupported")

    monkeypatch.setattr(os, "link", unsupported)
    with pytest.raises(ArtifactStorageError) as refusal:
        store.ensure_ready()
    assert refusal.value.reason == "link_unsupported"


def test_the_startup_probe_leaves_nothing_behind(tmp_path, anchored):
    """With its two `unlink`s succeeding, which is the ordinary case. The
    probe's cleanup goes through the same best-effort `_discard` as
    publication's, so this asserts what happens when it works, not a guarantee
    that it always does — a probe whose cleanup fails leaves a `.incoming-*`
    file for the operator-hygiene procedure and does not fail startup."""
    store = anchored(tmp_path / "artifacts")
    store.ensure_ready()

    assert list(store.root.iterdir()) == []


def test_ensure_ready_proves_directory_fsync_before_any_upload(
    tmp_path, anchored, monkeypatch
):
    """A platform that cannot support the guarantee fails startup, in front of
    an operator, rather than failing an upload of every exported Actor's
    mechanics."""
    store = anchored(tmp_path / "artifacts")
    _fsync_refusing_directories(monkeypatch)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.ensure_ready()
    assert refusal.value.reason == "durability_unconfirmed"


# -- the root is a descriptor, not a pathname (S-B-2, second review) ----------
#
# The permission checks in the section above are all made *by pathname*, which
# the second security review found is a check-then-use race: between `lstat` on
# the configured path and each later `os.open`/`os.replace`/`fsync` naming that
# same path, anyone able to rename entries in a writable parent can substitute a
# different directory, and every operation follows the name to the replacement.
#
# These exercise the substitution directly. None of them needs privilege or a
# second POSIX account: a rename this process performs is the same event, seen
# from the store's side, as a rename another account performs.


def replacement_directory(tmp_path: Path, at: Path) -> Path:
    """Move `at` aside and stand a *different* directory in its place.

    This is the attacker's move, performed with ordinary permissions. The
    replacement is created 0700 and owned by this account precisely so that the
    owner/mode checks cannot be what refuses it — the question is whether the
    anchoring keeps the operations off it.
    """
    moved = tmp_path / "moved-aside"
    at.rename(moved)
    at.mkdir(mode=ROOT_MODE)
    return moved


def swap_on_first(monkeypatch, action, *, when) -> None:
    """Run `action` the first time `os.open` is called with a matching argument.

    This is what makes the race deterministic. `when` receives the first
    positional argument of `os.open`; the swap therefore happens *after* the
    root has been validated and *before* the operation that uses it, which is
    the exact window a pathname check leaves open.
    """
    real_open = os.open
    fired: list[bool] = []

    def swapping(path, *args, **kwargs):
        if not fired and when(path):
            fired.append(True)
            action()
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", swapping)


def test_a_store_cannot_be_redirected_by_replacing_the_root_pathname(
    store, tmp_path
):
    """The configured name now points at a directory nobody validated. The store
    must not write every exported Actor's mechanics into it."""
    store.ensure_ready()
    trusted = replacement_directory(tmp_path, store.root)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())

    assert refusal.value.reason == "root_replaced"
    assert refusal.value.outcome is StorageOutcome.UNCHANGED
    # The decisive assertion: nothing at all landed in the replacement.
    assert list(store.root.iterdir()) == []
    assert list(trusted.iterdir()) == []


def test_a_swap_after_validation_still_writes_to_the_anchored_directory(
    store, tmp_path
):
    """The race itself, won. The substitution happens *after* every check has
    passed and before the temporary file is created, which is precisely when a
    pathname-based store would have been redirected. Anchoring means the write
    lands in the directory that was validated, wherever its name went."""
    store.ensure_ready()
    moved: list[Path] = []

    with pytest.MonkeyPatch.context() as patch:
        swap_on_first(
            patch,
            lambda: moved.append(replacement_directory(tmp_path, store.root)),
            # The temporary file is opened by a bare name against the root
            # descriptor, so a relative argument is the operation to race.
            when=lambda path: isinstance(path, str)
            and path.startswith(".incoming-"),
        )
        store.store(artifact())

    (trusted,) = moved
    assert (trusted / checksum_name()).read_bytes() == fixtures.encode(
        fixtures.bundle()
    )
    # Nothing was created in the directory that took over the name.
    assert list(store.root.iterdir()) == []


def test_a_load_cannot_read_an_artifact_from_a_replacement_directory(
    store, tmp_path
):
    """A read is not exempt. If the pathname can be swapped between validation
    and the open, a preview can be served bytes from a directory that was never
    approved. The planted decoy hashes to the name it is under, so content
    verification alone would have accepted it."""
    store.ensure_ready()
    checksum = store.store(artifact()).removeprefix("snapshot/").removesuffix(".json")
    replacement_directory(tmp_path, store.root)
    decoy = store.root / checksum_name()
    decoy.write_bytes(fixtures.encode(fixtures.bundle()))
    decoy.chmod(ARTIFACT_MODE)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.load(checksum)

    assert refusal.value.reason == "root_replaced"
    # And presence answers the same way rather than reporting the decoy.
    with pytest.raises(ArtifactStorageError) as presence:
        store.contains(checksum)
    assert presence.value.reason == "root_replaced"


def test_an_artifact_read_is_anchored_even_when_the_root_name_is_swapped(
    store, tmp_path
):
    """The bytes returned come from the validated directory, not from whatever
    holds the configured name at the moment of the read. The two directories
    hold *different* content under the same checksum name, so a redirected read
    is observable as a `checksum_mismatch` rather than being invisible."""
    store.ensure_ready()
    data = fixtures.encode(fixtures.bundle())
    checksum = store.store(artifact()).removeprefix("snapshot/").removesuffix(".json")
    moved: list[Path] = []

    def plant() -> None:
        trusted = replacement_directory(tmp_path, store.root)
        moved.append(trusted)
        decoy = store.root / checksum_name()
        decoy.write_bytes(b'{"planted":true}\n')
        decoy.chmod(ARTIFACT_MODE)

    with pytest.MonkeyPatch.context() as patch:
        swap_on_first(
            patch, plant, when=lambda path: isinstance(path, str)
            and path == checksum_name()
        )
        loaded = store.load(checksum)

    assert loaded.raw_bytes() == data
    assert (moved[0] / checksum_name()).read_bytes() == data


def test_an_existing_target_cannot_be_swapped_for_a_symlink_before_the_read(
    store, tmp_path
):
    """The other half of the same race, one level down: the checksum-named entry
    itself is replaced with a symlink between the root's validation and the
    open. `O_NOFOLLOW` on the anchored open is what refuses it."""
    store.ensure_ready()
    store.store(artifact())
    elsewhere = tmp_path / "elsewhere.json"
    elsewhere.write_bytes(fixtures.encode(fixtures.bundle()))
    elsewhere.chmod(0o600)

    def swap() -> None:
        target = store.root / checksum_name()
        target.unlink()
        target.symlink_to(elsewhere)

    with pytest.MonkeyPatch.context() as patch:
        swap_on_first(
            patch, swap, when=lambda path: isinstance(path, str)
            and path == checksum_name()
        )
        with pytest.raises(ArtifactStorageError) as refusal:
            store.store(artifact())

    assert refusal.value.reason == "artifact_untrusted"
    # The link's target was neither read as an artifact nor replaced.
    assert elsewhere.read_bytes() == fixtures.encode(fixtures.bundle())


def test_publication_and_directory_fsync_use_the_anchored_directory(
    store, tmp_path, monkeypatch
):
    """Publication and the durability `fsync` are the two operations that decide
    where the artifact ends up and whether it survives. Both must name the
    anchored descriptor, and that descriptor must still be the directory that was
    validated even after the pathname has been taken over."""
    store.ensure_ready()
    anchor = os.stat(store.root)
    synced: list[tuple[int, int]] = []
    published: list[tuple[int, int]] = []

    real_fsync = os.fsync
    real_link = os.link

    def recording_fsync(descriptor: int) -> None:
        info = os.fstat(descriptor)
        if stat.S_ISDIR(info.st_mode):
            synced.append((info.st_dev, info.st_ino))
        real_fsync(descriptor)

    def recording_link(source, destination, **keywords):
        assert keywords.get("src_dir_fd") is not None, (
            "publication must be anchored to a directory descriptor, not "
            "resolved through the configured pathname"
        )
        assert keywords.get("dst_dir_fd") is not None, (
            "the *destination* is the entry that decides where the artifact "
            "lands; resolving it through the pathname is the S-B-2 defect"
        )
        info = os.fstat(keywords["dst_dir_fd"])
        published.append((info.st_dev, info.st_ino))
        return real_link(source, destination, **keywords)

    monkeypatch.setattr(os, "fsync", recording_fsync)
    monkeypatch.setattr(os, "link", recording_link)

    store.store(artifact())

    identity = (anchor.st_dev, anchor.st_ino)
    assert published == [identity]
    assert synced == [identity]


def test_the_root_state_is_rechecked_through_the_descriptor_on_every_store(store):
    """Not through the pathname. The mode is changed on the anchored directory
    itself, so only a check made on the descriptor can see it."""
    store.ensure_ready()
    store.store(artifact())
    os.chmod(store.root, 0o750)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "root_permissive"

    # Refusal, not repair: the mode the operator left is the mode still there.
    assert stat.S_IMODE(store.root.stat().st_mode) == 0o750


def test_a_read_rechecks_the_root_too(store):
    """A deliberate decision, documented in the adapter: a root that has become
    readable by another account is no longer restricted storage, and continuing
    to serve every exported Actor's mechanics out of it is the wrong way to
    fail."""
    store.ensure_ready()
    checksum = store.store(artifact()).removeprefix("snapshot/").removesuffix(".json")
    os.chmod(store.root, 0o755)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.load(checksum)
    assert refusal.value.reason == "root_permissive"


# -- the ancestor rule, tested directly ---------------------------------------
#
# Every test in this section walks *real* directories with *real* modes, set by
# the test, and reads them with the real `os.lstat`. What is bounded is only how
# far up the walk goes: `ceiling=tmp_path` means the directories the test created
# are checked and the host's `/tmp` and `/` are not, so the assertion that fails
# is the one the test is about. Review finding 3.
#
# Ownership is the one property a test cannot create: chowning a directory to
# another account needs privilege this suite must never require. It is exercised
# from the other side instead, by moving *this process's* idea of who it is,
# which leaves the real `st_uid` comparison doing the real work.


def rule(root: Path) -> TrustedAncestors:
    """The production rule, walking only what a test made below `root`."""
    return TrustedAncestors(ceiling=root)


def test_a_trusted_ancestor_chain_is_accepted(tmp_path):
    chain = tmp_path / "srv" / "freedom"
    chain.mkdir(parents=True)
    (tmp_path / "srv").chmod(0o755)
    chain.chmod(0o755)

    rule(tmp_path).require(chain / "snapshots")


@pytest.mark.parametrize("mode", [0o777, 0o733, 0o757, 0o775, 0o707])
def test_an_ancestor_another_account_can_rename_entries_in_is_refused(tmp_path, mode):
    """The condition under which the root replacement could be staged at all.
    Group- or other-writable and not sticky: another account can rename the
    store's root out from under a validated pathname."""
    parent = tmp_path / "shared"
    parent.mkdir()
    parent.chmod(mode)

    with pytest.raises(ArtifactStorageError) as refusal:
        rule(tmp_path).require(parent / "artifacts")
    assert refusal.value.reason == "root_ancestor_untrusted"
    assert refusal.value.outcome is StorageOutcome.UNCHANGED


@pytest.mark.parametrize("mode", [0o1777, 0o1733, 0o1775])
def test_a_sticky_shared_ancestor_is_accepted(tmp_path, mode):
    """`/tmp` is 1777 and is not a finding: the sticky bit restricts renaming an
    entry to that entry's owner, which is exactly the property being required."""
    parent = tmp_path / "sticky"
    parent.mkdir()
    parent.chmod(mode)

    rule(tmp_path).require(parent / "artifacts")


def test_an_ancestor_owned_by_a_third_account_is_refused(tmp_path, monkeypatch):
    """`root` and this service account are the two acceptable owners. Exercised
    by moving this process's identity rather than by chowning a directory, which
    would need privilege; the `st_uid` read and the comparison are both real."""
    parent = tmp_path / "elsewhere"
    parent.mkdir()
    parent.chmod(0o755)
    monkeypatch.setattr(os, "geteuid", lambda: os.getuid() + 1)

    with pytest.raises(ArtifactStorageError) as refusal:
        rule(tmp_path).require(parent / "artifacts")
    assert refusal.value.reason == "root_ancestor_untrusted"


def test_the_rule_treats_root_ownership_of_slash_as_the_requirement_states():
    """The *other* acceptable owner, and the only one a test can point at: `/` is
    owned by an account this process is not.

    Written as agreement with an independent reading of `os.lstat` rather than as
    a flat expectation, so that it is a real check of the `root`-owned branch on
    a conventional host and still a correct test on the review host whose `/` is
    owned by `nobody` — where the requirement says to refuse, and it must.
    """
    if _independently_trusted(Path("/")):
        TrustedAncestors().require(Path("/") / "anything")
    else:
        with pytest.raises(ArtifactStorageError) as refusal:
            TrustedAncestors().require(Path("/") / "anything")
        assert refusal.value.reason == "root_ancestor_untrusted"


def test_a_non_directory_ancestor_is_refused(tmp_path):
    """`/srv/freedom` being a file is not a permission problem; it is a
    configuration the walk must not step over."""
    parent = tmp_path / "afile"
    parent.write_bytes(b"")
    parent.chmod(0o600)

    with pytest.raises(ArtifactStorageError) as refusal:
        rule(tmp_path).require(parent / "artifacts")
    assert refusal.value.reason == "root_ancestor_untrusted"


def test_a_symlinked_ancestor_is_refused_rather_than_followed(tmp_path):
    """`os.lstat`, not `os.stat`: the walk must judge the link, not whatever the
    link currently points at, because the link's owner decides that."""
    real = tmp_path / "real"
    real.mkdir()
    real.chmod(0o755)
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)

    with pytest.raises(ArtifactStorageError) as refusal:
        rule(tmp_path).require(link / "artifacts")
    assert refusal.value.reason == "root_ancestor_untrusted"


def test_an_absent_ancestor_is_refused(tmp_path):
    with pytest.raises(ArtifactStorageError) as refusal:
        rule(tmp_path).require(tmp_path / "absent" / "artifacts")
    assert refusal.value.reason == "root_ancestor_untrusted"


def test_the_walk_stops_at_the_ceiling_and_not_before(tmp_path, monkeypatch):
    """The bound is what makes these tests hermetic, so what it excludes is
    asserted rather than assumed: everything below the ceiling is visited, in
    order, and nothing at or above it is."""
    chain = tmp_path / "a" / "b" / "c"
    chain.mkdir(parents=True)
    for directory in (tmp_path / "a", tmp_path / "a" / "b", chain):
        directory.chmod(0o755)
    visited: list[Path] = []
    real_lstat = os.lstat

    def recording(path, *args, **kwargs):
        visited.append(Path(path))
        return real_lstat(path, *args, **kwargs)

    monkeypatch.setattr(os, "lstat", recording)
    rule(tmp_path).require(chain / "artifacts")

    assert visited == [chain, tmp_path / "a" / "b", tmp_path / "a"]
    assert tmp_path not in visited


def test_an_unbounded_rule_is_the_production_default(tmp_path):
    """No ceiling unless one is passed, and no way to pass one from
    configuration: `TrustedAncestors()` is what a store built without arguments
    gets, and it walks to `/`."""
    assert TrustedAncestors().ceiling is None
    assert FilesystemArtifactStore(tmp_path / "artifacts").ancestors.ceiling is None


def test_the_production_walk_checks_the_real_configured_path(tmp_path):
    """The integration case the bounded walks deliberately do not cover: the
    real configured path, checked against its real ancestors, all the way to `/`.

    The verdict is computed here from `os.lstat` independently of the adapter and
    the store is required to agree, so this holds on a host whose `/tmp` is
    owned by `nobody` — where it asserts the refusal — as well as on one where it
    is owned by `root`. What it proves either way is that nothing about the
    production path is being skipped.
    """
    root = tmp_path / "artifacts"
    expected = [
        ancestor
        for ancestor in root.parents
        if not _independently_trusted(ancestor)
    ]
    store = FilesystemArtifactStore(root)
    try:
        if expected:
            with pytest.raises(ArtifactStorageError) as refusal:
                store.ensure_ready()
            assert refusal.value.reason == "root_ancestor_untrusted"
        else:
            store.ensure_ready()
    finally:
        store.close()


def _independently_trusted(ancestor: Path) -> bool:
    """The ancestor rule, restated from the deployment requirement.

    Deliberately a second implementation rather than a call into the adapter: a
    test that asks the code under test what it thinks proves only that it is
    consistent with itself.
    """
    try:
        info = os.lstat(ancestor)
    except OSError:
        return False
    if not stat.S_ISDIR(info.st_mode):
        return False
    if info.st_uid not in (0, os.geteuid()):
        return False
    mode = stat.S_IMODE(info.st_mode)
    return not (mode & 0o022) or bool(mode & stat.S_ISVTX)


# -- descriptor ownership and lifetime ----------------------------------------


def descriptors_under(root: Path) -> list[str]:
    """Every descriptor this process holds on `root` or anything inside it.

    A whole-process descriptor count would be counting pytest's capture files
    and whatever another test happened to finalise a moment earlier. This asks
    the only question that matters: is *this store* holding descriptors, and how
    many. Linux-only, like the store itself.
    """
    held: list[str] = []
    for number in os.listdir("/proc/self/fd"):
        try:
            target = os.readlink(f"/proc/self/fd/{number}")
        except OSError:
            # The descriptor was closed between the listing and the read, which
            # by definition is not one that is being held open.
            continue
        if target == str(root) or target.startswith(f"{root}/"):
            held.append(target)
    return held


def test_the_store_holds_exactly_one_descriptor_however_many_operations_run(
    tmp_path, anchored
):
    """A per-request leak would exhaust the service under exactly the load it is
    meant to survive, so the count is asserted rather than assumed."""
    store = anchored(tmp_path / "artifacts")
    store.ensure_ready()

    for _ in range(5):
        store.store(artifact())
        store.load(checksum_name().removesuffix(".json"))
        store.contains(checksum_name().removesuffix(".json"))

    # One: the anchored root. No artifact descriptor and no second root.
    assert descriptors_under(store.root) == [str(store.root)]
    store.close()
    assert descriptors_under(store.root) == []


@pytest.mark.parametrize(
    "break_it",
    [
        pytest.param(lambda root: root.chmod(0o755), id="permissive_root"),
        pytest.param(
            lambda root: (root / checksum_name()).mkdir(), id="non_regular_target"
        ),
    ],
)
def test_no_descriptor_survives_a_refused_operation(tmp_path, anchored, break_it):
    store = anchored(tmp_path / "artifacts")
    store.ensure_ready()
    break_it(store.root)

    for _ in range(3):
        with pytest.raises(ArtifactStorageError):
            store.store(artifact())

    assert descriptors_under(store.root) == [str(store.root)]
    store.close()
    assert descriptors_under(store.root) == []


def test_a_refused_startup_leaves_no_descriptor_open(tmp_path, anchored):
    """The failure an operator sees most often is a misconfigured root. It must
    not also be the failure that leaks a descriptor per restart attempt."""
    root = tmp_path / "permissive"
    root.mkdir()
    root.chmod(0o755)

    for _ in range(3):
        store = anchored(root)
        with pytest.raises(ArtifactStorageError):
            store.ensure_ready()
        # Not even before `close()`: the validation failure closes the
        # descriptor it opened, so a restart loop cannot accumulate them.
        assert descriptors_under(root) == []
        store.close()

    assert descriptors_under(root) == []


def test_close_releases_the_descriptor_and_is_idempotent(tmp_path, anchored):
    store = anchored(tmp_path / "artifacts")
    store.ensure_ready()

    assert descriptors_under(store.root) == [str(store.root)]
    store.close()
    store.close()

    assert descriptors_under(store.root) == []
    # And a closed store simply anchors itself again rather than breaking.
    store.store(artifact())
    assert descriptors_under(store.root) == [str(store.root)]
    store.close()
    assert descriptors_under(store.root) == []


def test_the_store_is_a_context_manager(tmp_path, ancestors):
    with FilesystemArtifactStore(tmp_path / "artifacts", ancestors=ancestors) as store:
        store.ensure_ready()
        store.store(artifact())
        assert descriptors_under(store.root) == [str(store.root)]
    assert descriptors_under(store.root) == []


def test_a_dropped_store_does_not_hold_its_descriptor_forever(tmp_path, ancestors):
    """The backstop, stated as what it is: `close()` is the contract, and this
    only proves that forgetting it is not permanent."""
    import gc

    root = tmp_path / "artifacts"
    # Constructed directly rather than through `anchored`, which would keep a
    # reference and make the collection this test is about impossible.
    store = FilesystemArtifactStore(root, ancestors=ancestors)
    store.ensure_ready()
    assert descriptors_under(root) == [str(root)]
    del store
    gc.collect()

    assert descriptors_under(root) == []


def test_a_retry_after_durability_unconfirmed_neither_duplicates_nor_destroys(
    store, monkeypatch
):
    """S-B-2's hardening must not have cost I-2's behaviour. The refused attempt
    leaves the correct target alone, and the retry completes the guarantee
    against that same file rather than writing a second one."""
    store.ensure_ready()
    data = fixtures.encode(fixtures.bundle())
    _fsync_refusing_directories(monkeypatch)

    with pytest.raises(ArtifactStorageError) as refusal:
        store.store(artifact())
    assert refusal.value.reason == "durability_unconfirmed"
    assert refusal.value.outcome is StorageOutcome.UNRESOLVED
    assert (store.root / checksum_name()).read_bytes() == data

    monkeypatch.undo()
    reference = store.store(artifact())

    assert reference == f"snapshot/{checksum_name()}"
    assert len(list(store.root.glob("*.json"))) == 1
    assert list(store.root.glob(".incoming-*")) == []
    assert (store.root / checksum_name()).read_bytes() == data


# -- what a storage failure is allowed to claim (I-1) -------------------------


def test_durability_unconfirmed_makes_no_claim_about_the_filesystem():
    """The finding, at its source. Every `ArtifactStorageError` used to carry
    "Nothing was stored or served", which is false for exactly this reason
    code — a correct target may already be published and must be kept."""
    refusal = ArtifactStorageError("durability_unconfirmed", StorageOutcome.UNRESOLVED)

    message = str(refusal).lower()
    assert "nothing was stored" not in message
    assert "may or may not have completed" in message
    assert "durability was not confirmed" in message
    assert "retrying the same content is safe" in message


def test_the_conservative_default_claims_nothing_about_durable_state():
    """The second I-1 finding. `UNRESOLVED` is what an unclassified reason
    inherits, so it is attached to paths nobody has examined — and it used to
    assert "nothing already held was changed or removed", which the publication
    race made false. A default may say what is structurally true of the store;
    it may not make a positive claim about what is on the filesystem."""
    message = StorageOutcome.UNRESOLVED.sentence.lower()

    assert "nothing already held" not in message
    assert "unchanged" not in message
    assert "changed or removed" not in message


def test_a_pre_publication_failure_may_say_it_published_nothing():
    refusal = ArtifactStorageError("root_permissive", StorageOutcome.UNCHANGED)

    assert "No artifact was published" in str(refusal)
    assert "nothing was stored" not in str(refusal).lower()


def test_a_preserved_entry_is_distinguished_from_having_found_nothing():
    """The two ways a store declines are operationally different: "there was
    nothing there" sends an operator nowhere, and "there was something there,
    it was refused, and it is still there" sends them to §5.6."""
    preserved = str(ArtifactStorageError("checksum_mismatch", StorageOutcome.PRESERVED))
    absent = str(ArtifactStorageError("root_permissive", StorageOutcome.UNCHANGED))

    assert "left exactly as it was found" in preserved
    assert "left exactly as it was found" not in absent
    assert preserved != absent
    for message in (preserved, absent):
        assert "No artifact was published" in message


def test_an_unclassified_reason_defaults_to_claiming_nothing():
    """The safety net. A reason somebody forgot to classify produces a vaguer
    true statement, never a stronger false one."""
    assert (
        ArtifactStorageError("something_new").outcome is StorageOutcome.UNRESOLVED
    )


def test_every_storage_refusal_declares_what_it_establishes():
    """And the net is not the normal path: each raise names its outcome.

    Walked from the syntax tree rather than asserted per call site, so a refusal
    added later cannot quietly inherit the conservative default and go
    unnoticed.
    """
    source = Path("adapters/artifacts/filesystem.py").resolve()
    tree = ast.parse(source.read_text(encoding="utf-8"))
    undeclared: list[str] = []
    reasons: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        # `_read_trusted(..., reason="verify_failed")` decides a reason without
        # constructing the error itself, so both forms are collected.
        for keyword in node.keywords:
            if keyword.arg == "reason" and isinstance(keyword.value, ast.Constant):
                reasons.add(keyword.value.value)
        name = node.func.id if isinstance(node.func, ast.Name) else None
        if name != "ArtifactStorageError":
            continue
        if len(node.args) < 2:
            undeclared.append(ast.unparse(node))
            continue
        if isinstance(node.args[0], ast.Constant):
            reasons.add(node.args[0].value)

    assert not undeclared, (
        "every ArtifactStorageError in the adapter must name its StorageOutcome, "
        "so that what it claims about the store is a decision rather than an "
        f"inheritance: {undeclared}"
    )
    # The reason vocabulary the operations document has to describe.
    assert reasons == {
        "artifact_not_a_regular_file",
        "artifact_not_owned",
        "artifact_permissive",
        "artifact_untrusted",
        "checksum_mismatch",
        "containment_violation",
        "dir_fd_unsupported",
        "durability_unconfirmed",
        "invalid_checksum",
        "link_unsupported",
        "nofollow_unsupported",
        "publication_unsettled",
        "read_failed",
        "root_ancestor_untrusted",
        "root_not_a_directory",
        "root_not_owned",
        "root_permissive",
        "root_replaced",
        "root_unavailable",
        "root_untrusted",
        "verify_failed",
        "write_failed",
    }
