"""A content-addressed artifact store on the local filesystem.

Every property below exists because of a specific way a file store goes wrong.

**The name is derived, never supplied.** The file is named for the SHA-256 of
its own contents. A caller cannot influence it at all, so there is no traversal,
no overwrite of an unrelated file, no `.json.exe`, and no way for two different
documents to land on one name. `SnapshotArtifact.source_name` is deliberately
ignored here even though the artifact carries it.

**Containment is structural.** Every operation is performed *relative to a
directory descriptor*, with a name that is a validated hex digest plus a fixed
suffix. Such a name can hold no separator and no `..`, so there is no path for
containment to fail on — see "The anchored root" below.

**The write is atomic, and it never overwrites.** Bytes go to a temporary file
in the *same directory*, are flushed and `fsync`ed and read back, and only then
is the checksum entry created — by `os.link`, which either creates it or fails
`EEXIST`. A crash never leaves a half-written artifact under a name that claims
to be a complete one, and no entry that this process has not validated is ever
removed: see "Publication never overwrites" below. The *directory* is then
`fsync`ed, and a failure to do that is an error rather than a shrug: see "The
durability contract".

**What was written is read back and verified.** A store whose bytes do not hash
to their own name is refused rather than reported as a success, because the
whole platform identifies this document by that hash.

**A failed write cleans up after itself.** The temporary file is removed on
every failure path, so a partial write does not accumulate in a directory the
operator is expected to be able to reason about. Cleanup only ever names the
temporary file, and it is unreachable once the artifact has been published, so a
correctly published artifact is never removed because some *later* step failed.

**Restrictive permissions are enforced, not merely requested.** Security review
S-B-2 found the previous arrangement asserted this rather than checking it:
`mkdir(mode=0o700, exist_ok=True)` sets the mode of a root it creates and says
nothing at all about one that already exists, and an existing checksum-named
target was content-verified but accepted without anyone asking whether it was a
regular, service-owned, unreadable-by-others file. Both are now checked, and an
unsafe state is a refusal rather than a silent repair — see "The storage
policy".

## The anchored root

The second security review of S-B-2 found what the permission checks alone could
not fix: they were made *by pathname*. `_ensure_root()` `lstat`ed the configured
path, and then the temporary file, the artifact reads, the `os.replace` and the
directory `fsync` each named that path again. Between the check and each use,
anyone able to rename entries in a writable parent could replace the directory
that had been approved, and every subsequent operation would follow the
pathname to the replacement. Checking the pathname once more would not fix that;
it would only move the window.

So the root is **opened once, validated through that descriptor, and every
operation afterwards is anchored to it**:

| Operation | How it is anchored |
|---|---|
| creating the temporary file | `os.open(name, …, dir_fd=root)` |
| reading or verifying an artifact | `os.open(name, O_RDONLY \\| O_NOFOLLOW, dir_fd=root)` |
| publishing | `os.link(tmp, name, src_dir_fd=root, dst_dir_fd=root)` |
| removing a temporary | `os.unlink(name, dir_fd=root)` |
| presence | `os.stat(name, dir_fd=root, follow_symlinks=False)` |
| directory `fsync` | `os.fsync(root)` — the descriptor itself |

A name resolved relative to a directory descriptor cannot be redirected by
anything happening to the pathname: the kernel starts from the inode the
descriptor already holds. Replacing `/srv/freedom/snapshots` after the service
started therefore does not move a single one of these operations.

**The descriptor is the trusted object.** Its type, owner and mode are proved by
`os.fstat` on the descriptor — never by `stat` on a path — at startup and again
on every `store()` and every read. `O_DIRECTORY` and `O_NOFOLLOW` mean the open
itself refuses a non-directory and refuses a symlinked root rather than
following it.

**Divergence is reported, not relied on.** Each use additionally compares the
configured pathname's `(st_dev, st_ino)` with the anchored directory's and
refuses with `root_replaced` if they differ. This is *not* the safety mechanism
— the anchoring is — and it is deliberately fail-closed: if an operator moved
the store, the service should say so rather than keep writing into a directory
that is no longer at the configured path.

**Ancestors are checked once, at startup.** A descriptor cannot see what happens
above it, so `ensure_ready()` walks the root's parents and refuses
(`root_ancestor_untrusted`) unless each is a directory owned by `root` or by
this service account, and is not group- or other-writable without the sticky
bit. That is the condition under which no other account could have staged the
replacement in the first place. It is a startup check by design: after startup
the anchored descriptor is what makes a replacement harmless, and re-walking a
pathname on every request would add a check that is itself racy.

The walk is a separate object, `TrustedAncestors`, for one reason given in full
there: it is the only rule in this module whose answer depends on directories
*the deployment does not own* — `/`, `/srv`, a host temporary directory — and a
test about publication or descriptor lifetime should not be deciding whether the
machine it runs on has a conventional `/`. Production constructs it with no
bound and walks to `/`. Nothing reads it from configuration.

**Lifetime is explicit.** The descriptor is opened lazily, held for the life of
the store, and released by `close()` — which the composition root calls from
`Composition.dispose()`, and which `with FilesystemArtifactStore(...)` calls on
exit. `__del__` closes it too, but only as a backstop: nothing here depends on
when the garbage collector runs. Every failure path that opens a descriptor and
then refuses closes it before raising.

## Publication never overwrites

The third security review found that anchoring, having fixed *where* the final
directory entry was created, had left *how* untouched. Publication was:

1. `_holds()` opens the checksum entry, validates it, or finds it absent;
2. a temporary file is written, synced and verified;
3. `os.replace(temporary, name, …)` publishes it.

`os.replace` is atomic about **replacing**. If a checksum-named entry appeared
between 1 and 3 — another writer, an operator, anything — step 3 removed it and
put this process's file in its place, without anybody having looked at it. That
contradicts four things this store claims: that artifacts are immutable, that an
unsafe or mismatched target is refused rather than repaired, that unexpected
evidence is preserved for an operator, and that no artifact is ever implicitly
deleted. Descriptor anchoring does not help: it proves the operation stayed
inside the approved directory, which was never the question.

**So publication is `os.link`.** `linkat(2)` creates the destination entry or
fails `EEXIST`; there is no mode in which it removes what is already under the
name, and the check and the creation are one syscall, so there is no window
between them to lose. Concretely:

- **nobody there** — the link succeeds. Exactly one writer can win, because the
  kernel serialises the entry creation;
- **somebody there** — `EEXIST`. The entry is then opened *through the anchored
  descriptor* with `O_NOFOLLOW` and re-proved from nothing: regular file, owned
  by this account, no group or other permission, and bytes that hash to the name
  it is under. If it passes, the winner is this submission's artifact and is
  reused — two writers of identical bytes converge on one file. If it fails, the
  submission is refused (`checksum_mismatch`, `artifact_untrusted`,
  `artifact_permissive`, `artifact_not_owned`,
  `artifact_not_a_regular_file`) and the entry is left byte-for-byte and
  mode-for-mode as it was found. `StorageOutcome.PRESERVED` is what says so.

Three consequences of using a link rather than a rename, all deliberate:

- **the temporary survives publication and is removed afterwards.** For a moment
  the bytes have two names. Both are inside the anchored root, both are `0600`
  and owned by this account, and the artifact's mode and ownership are the
  *same inode's*, so they cannot drift from what `os.open` created. `_discard`
  removes the temporary, and `_discard` refuses to unlink any name that is not a
  temporary — so no future edit can reach it with a checksum name and delete a
  published artifact.

  **That removal is best effort, and the store does not promise it happened.**
  `_discard` swallows `OSError`, deliberately: a submission that published a
  correct artifact must not be failed a second time because the second name
  could not be unlinked, and a failure path has nothing left to save. So a
  `store()` that returned successfully may have left one `.incoming-*` hard
  link to the published bytes behind, and
  `test_a_failing_cleanup_leaves_the_published_artifact_alone` is the test that
  says so. What such a leftover costs is storage — it is `0600`, owned by this
  account, inside a `0700` root, and no route serves it, because the only name
  any route resolves is the checksum one. What it cannot do is invalidate or
  remove the published artifact. Finding and removing leftovers is operator
  hygiene, under the read-only procedure in
  `docs/operations/foundry-snapshot-submission.md` §5.6 ("Temporary files left
  by a failed cleanup"); nothing in this module deletes an entry it did not
  create in the attempt that is running;
- **the temporary's removal is a publication-related directory-entry change**,
  so it happens *before* the directory `fsync`. One sync makes both the creation
  and the removal durable;
- **hard links must work.** They do on every filesystem this deployment can use,
  and `ensure_ready()` proves it rather than assuming it: it links a probe file,
  links it a second time, and requires the second attempt to fail `EEXIST`. A
  filesystem that cannot publish this way fails startup with `link_unsupported`,
  in front of an operator, instead of failing an upload. `renameat2` with
  `RENAME_NOREPLACE` would give the same guarantee in one syscall, but only
  through a hand-rolled `ctypes` binding — the standard library exposes no
  wrapper — and a raw syscall stub in the path that stores every exported
  Actor's mechanics is a worse trade than one extra `unlink`.

## The storage policy

POSIX, because the deployment is Linux (`docs/operations/topology.md`). Every
rule below is enforced at startup through `ensure_ready()` *and* re-checked on
each `store()` and each read, because a mode or an owner can change between them
and only the later check is on the path that is about to write or serve a
sensitive document.

| Subject | Required |
|---|---|
| the configured root path | contains no symbolic-link component |
| the root's ancestors (startup) | directories owned by `root` or this account, not writable by others without the sticky bit |
| the root | exists (or is created `0700`), is a directory, is owned by this process's effective uid, grants nothing to group or other, and is still the directory the configured path names |
| an artifact being read or accepted | is a regular file, opened without following a symlink, owned by this process's effective uid, granting nothing to group or other, and hashing to its own name |
| a newly written artifact | created `0600` by `os.open`, so it is never briefly world-readable between creation and a `chmod` that has not happened yet |

**Reads re-check the root too.** That is a deliberate decision rather than an
omission: a store whose root has become readable by another account is no longer
restricted storage, and continuing to serve every exported Actor's mechanics out
of it while an operator is unaware would be the wrong direction to fail. The
cost is one `fstat` on a descriptor that is already open.

**Refusal, not repair.** Nothing here calls `chmod` or `chown` on a path it
found in the wrong state. A process that quietly widened or narrowed the
permissions of a directory an operator configured would be exercising an
authority nobody granted it, and the operations policy assigns repair to the
operator (`docs/operations/foundry-snapshot-submission.md` §5.6). The refusal
names a fixed reason and never the path.

**Why a symlinked component is refused rather than resolved.** Resolving it
would mean the store's real location is decided by whoever can write the link,
which may not be the account that owns the configured directory. The operator
configures the real path; that is a one-line change and it removes a redirect
this process cannot audit.

**Time of check to time of use.** The existing-artifact checks are made against
a file *descriptor* — `os.open` with `O_NOFOLLOW`, then `os.fstat` and a read
from that same descriptor — so the file whose type, owner and mode were checked
is exactly the file whose bytes were hashed. Nothing re-opens a name between
deciding it is safe and using it, and the directory that name is resolved
against is the anchored one.

## The durability contract

Publication creates the artifact's directory entry atomically, but that entry is
not durable until the directory itself is `fsync`ed. Implementation review I-2
found that a failure to do that was being swallowed, which allowed the database
transaction to commit against an artifact whose entry might not survive a power
loss — the precise state the store-before-record ordering exists to prevent.

So a directory-`fsync` failure raises
`ArtifactStorageError("durability_unconfirmed")`, the submission is refused, and
no database row, idempotency receipt or accepted audit event is committed. A
failure to *open* the root is now a distinct and earlier event — the store
cannot anchor itself, so it refuses `root_unavailable` before writing anything
at all — which is a more precise statement of the same guarantee rather than a
weaker one: both refuse the submission and both commit nothing.

Two consequences worth stating, because both are deliberate:

- **the published target is left alone.** By the time directory sync runs, the
  checksum entry exists and the bytes under it are correct and complete —
  whether this attempt created it or found and re-proved another writer's.
  Deleting it because the *acknowledgement* failed would turn an unconfirmed
  success into a destroyed one. `durability_unconfirmed` is therefore the one
  failure classified `StorageOutcome.UNRESOLVED`: it says publication may or may
  not have completed and that its durability was not confirmed, which is all it
  can prove;
- **a retry completes the guarantee.** The retry finds the target present,
  re-verifies it, and `fsync`s the directory again — so the durability that was
  not established the first time is established now. This is why the
  already-held branch syncs the directory rather than returning early.

`ensure_ready()` proves at startup that this filesystem supports directory
`fsync` at all, so a platform that cannot support it fails the service's
startup in front of an operator instead of failing an upload that carries every
exported Actor's mechanics.

There is no delete, no listing and no path-returning accessor. Retention is an
operator action against the filesystem; see
`docs/operations/foundry-snapshot-submission.md`.
"""
from __future__ import annotations

import errno
import hashlib
import os
import re
import stat
from pathlib import Path
from types import TracebackType

from application.artifacts import (
    ArtifactNotStored,
    ArtifactStorageError,
    StorageOutcome,
)
from application.foundry.artifact import SnapshotArtifact
from domain.foundry import SnapshotChecksum

UNCHANGED = StorageOutcome.UNCHANGED
PRESERVED = StorageOutcome.PRESERVED
UNRESOLVED = StorageOutcome.UNRESOLVED

#: The stored file mode. Readable and writable by the service account only.
ARTIFACT_MODE = 0o600

#: The storage root's mode. No group or other access at all, so a stray
#: world-readable file inside it is still unreachable by another account.
ROOT_MODE = 0o700

#: Any permission bit granted to group or other. A root or an artifact with one
#: of these set is refused: the whole point of the store is that no other
#: account on the host can list or read it.
FORBIDDEN_MODE_BITS = 0o077

#: Write access for anyone but the owner. An ancestor with one of these set, and
#: without the sticky bit, is a directory in which another account can rename the
#: store's root out from under it.
_ANCESTOR_WRITE_BITS = 0o022

#: What a checksum must look like before it is used to build a name. Rejecting
#: the shape is cheaper and more obviously correct than sanitising it.
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")

_SUFFIX = ".json"
_TEMPORARY_PREFIX = ".incoming-"

#: How much is pulled per read when verifying a stored artifact.
_READ_CHUNK = 256 * 1024

#: POSIX open flags, looked up rather than named directly so that importing this
#: module cannot fail on a platform that lacks one. The deployment is Linux and
#: has both; a platform without them would lose the symlink refusal and the
#: anchoring, so `ensure_ready()` refuses to start there rather than pretending
#: otherwise.
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIRECTORY = getattr(os, "O_DIRECTORY", 0)

#: Whether this platform can resolve a name relative to a directory descriptor
#: for every operation this store performs. `os.link` is publication; without
#: `dir_fd` on it the final directory entry would be the one operation resolved
#: through a pathname, which is the whole defect S-B-2 was about.
_ANCHORING_SUPPORTED = all(
    function in os.supports_dir_fd
    for function in (os.open, os.stat, os.unlink, os.link)
)

#: How many times publication may see `EEXIST` and then find the entry gone
#: again before refusing. Nothing in this store ever removes an artifact, so even
#: a second pass is unreachable in production; the bound exists so that a
#: filesystem behaving in a way nobody predicted produces a refusal rather than a
#: spin inside a request.
_PUBLICATION_ATTEMPTS = 3

_CLOSED = -1


class TrustedAncestors:
    """No account but `root` or this one may rename entries above the store.

    That is the condition under which the root-replacement attack S-B-2 is about
    could be staged at all, so it is checked once, at startup, before the first
    submission. A directory descriptor cannot observe its own ancestors, which is
    why this is the one rule in this module made by pathname; re-walking it per
    request would add exactly the check-then-use window the anchoring removes.

    **Why this is an object.** Every other rule here is about directories the
    deployment owns and this process can therefore reason about. This one is
    about `/`, `/srv`, and whatever stands between them — directories a *test*
    neither owns nor created. The second review of this package ran the suite on
    a host whose `/` and temporary directory are owned by `nobody`, and every
    test that called `ensure_ready()` was refused `root_ancestor_untrusted`
    before it reached the publication, durability or descriptor-lifetime
    assertion it was actually written to make. Thirty-two of them, none of them
    about ancestors.

    So `ceiling` bounds the walk, and the automated suite bounds it at pytest's
    own temporary root: the directories a test creates are checked by this exact
    code against real `lstat` results, and the host's are not that test's
    business. `ceiling` is **not configuration** — `build_application` exposes it
    only as a keyword a test can pass, there is no environment variable for it,
    and production constructs this class with no arguments and walks to `/`.
    `docs/operations/foundry-snapshot-submission.md` §5.6 states the deployment
    requirement that walk enforces, and how it is tested.
    """

    __slots__ = ("_ceiling",)

    def __init__(self, *, ceiling: Path | None = None) -> None:
        self._ceiling = ceiling

    @property
    def ceiling(self) -> Path | None:
        """Where the walk stops, or `None` for the production walk to `/`."""
        return self._ceiling

    def require(self, root: Path) -> None:
        """Refuse unless every directory above `root` is trustworthy.

        A `ceiling` that is not actually an ancestor of `root` bounds nothing and
        the walk reaches `/`, which is the safe direction for a mistake to fail
        in: it can only check more than was asked, never less.
        """
        for ancestor in root.parents:
            if self._ceiling is not None and ancestor == self._ceiling:
                return
            self._require_trusted(ancestor)

    def _require_trusted(self, ancestor: Path) -> None:
        try:
            info = os.lstat(ancestor)
        except OSError as error:
            raise ArtifactStorageError(
                "root_ancestor_untrusted", UNCHANGED
            ) from _dropped(error)
        if not stat.S_ISDIR(info.st_mode):
            raise ArtifactStorageError("root_ancestor_untrusted", UNCHANGED)
        if info.st_uid not in (0, os.geteuid()):
            raise ArtifactStorageError("root_ancestor_untrusted", UNCHANGED)
        mode = stat.S_IMODE(info.st_mode)
        # The sticky bit is what makes a shared directory such as `/tmp`
        # acceptable: it restricts renaming an entry to that entry's owner.
        if mode & _ANCESTOR_WRITE_BITS and not mode & stat.S_ISVTX:
            raise ArtifactStorageError("root_ancestor_untrusted", UNCHANGED)


class FilesystemArtifactStore:
    """Immutable artifacts under one configured root directory.

    The root must be an absolute path, outside the repository, with no symbolic
    link in it. That is checked here rather than trusted, because a store that
    landed inside the working tree would put every exported Actor's mechanics
    one `git add -A` away from being committed, and a store reached through a
    symlink would sit wherever whoever owns that link decided.

    Holds one file descriptor once it has been used. Call `close()`, or use it
    as a context manager, when the composition that owns it is disposed.
    """

    __slots__ = ("_ancestors", "_root", "_root_fd", "_root_identity")

    def __init__(
        self,
        root: Path,
        *,
        repository_root: Path | None = None,
        ancestors: TrustedAncestors | None = None,
    ) -> None:
        # First, so that `__del__` has something to read even if the validation
        # below refuses this configuration.
        self._root_fd = _CLOSED
        self._root_identity: tuple[int, int] | None = None
        # The production walk, to `/`, unless a caller supplies a bounded one.
        # See `TrustedAncestors` for why that seam exists and why it is not
        # reachable from configuration.
        self._ancestors = ancestors if ancestors is not None else TrustedAncestors()
        if not root.is_absolute():
            raise ValueError(
                "The snapshot artifact root must be an absolute path. A relative "
                "root resolves against the process working directory, which is "
                "not a property the operator configured."
            )
        resolved = root.resolve()
        forbidden = (
            repository_root
            if repository_root is not None
            else Path(__file__).resolve().parents[2]
        ).resolve()
        if resolved == forbidden or forbidden in resolved.parents:
            raise ValueError(
                "The snapshot artifact root must be outside this repository. An "
                "artifact holds every exported Actor's mechanics and must never "
                "be reachable by a commit."
            )
        # `normpath` collapses `.` and `..` without touching the filesystem;
        # `realpath` additionally follows every symbolic link. They agree only
        # when no component of the configured path is a link. Comparing them is
        # what detects a symlinked root — `resolve()` alone cannot, because it
        # has already followed the link by the time anything looks.
        if os.path.normpath(str(root)) != os.path.realpath(str(root)):
            raise ValueError(
                "The snapshot artifact root must not be reached through a "
                "symbolic link. Configure the real directory: a link makes the "
                "store's true location a property of whoever can write the "
                "link, which this service cannot audit."
            )
        self._root = resolved

    @property
    def root(self) -> Path:
        """The configured root. For composition and operations, not for callers."""
        return self._root

    # -- lifecycle ------------------------------------------------------------

    def close(self) -> None:
        """Release the anchored root descriptor. Idempotent.

        Composition owns this: `Composition.dispose()` calls it. A store that is
        closed and then used again simply anchors itself afresh, which is what
        makes this safe to call without knowing whether anything is in flight.
        """
        descriptor, self._root_fd = self._root_fd, _CLOSED
        self._root_identity = None
        if descriptor != _CLOSED:
            try:
                os.close(descriptor)
            except OSError:
                # The descriptor is gone either way, and a failure to close one
                # is not something a caller can act on.
                pass

    def __enter__(self) -> FilesystemArtifactStore:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def __del__(self) -> None:
        """A backstop, never the mechanism.

        Explicit `close()` is what the composition root and the tests rely on;
        this only stops a descriptor surviving an object that was dropped
        without one. Interpreter shutdown can have taken `os` apart already, so
        every failure here is ignored.
        """
        try:
            self.close()
        except BaseException:  # noqa: BLE001 - a finalizer may not raise
            pass

    def ensure_ready(self) -> None:
        """Prove the store is usable **before** the first submission, or refuse.

        Called once from the composition root. A permissive root, a root owned
        by another account, a root standing in a directory another account can
        rename entries in, a filesystem on which publication cannot refuse to
        overwrite, and a filesystem that cannot `fsync` a directory are all
        deployment faults, and all of them are better discovered by an operator
        watching a service start than by the first upload of every active
        character's mechanics.

        It is not a substitute for the per-operation checks: a mode can change
        while the process runs, so `store()` and the reads check again. The
        ancestor walk is the one check that happens only here — see the module
        docstring.
        """
        if not _NOFOLLOW or not _DIRECTORY:
            raise ArtifactStorageError("nofollow_unsupported", UNCHANGED)
        if not _ANCHORING_SUPPORTED:
            raise ArtifactStorageError("dir_fd_unsupported", UNCHANGED)
        # The root's own state first, then what stands above it: an operator
        # whose directory is world-readable should be told that, rather than
        # being told about its parent because the walk happened to run earlier.
        root_fd = self._anchored_root(create=True)
        self._ancestors.require(self._root)
        self._prove_publication_refuses_to_overwrite(root_fd)
        self._fsync_root(root_fd)

    def _prove_publication_refuses_to_overwrite(self, root_fd: int) -> None:
        """Prove `os.link` behaves here the way publication depends on it to.

        Two facts, on this root's actual filesystem: a hard link can be created
        at all, and creating one over an existing name fails rather than
        replacing it. A filesystem that cannot do the first (FAT, some network
        mounts) or does not do the second cannot give this store the guarantee
        that no unvalidated entry is ever removed, and it should say so at
        startup rather than during an upload.

        Both probe names carry the temporary prefix, so they are removed by the
        same `_discard` that can only ever remove a temporary, and neither can
        collide with a checksum name. That removal is best effort in the same
        way `store()`'s is: a probe whose cleanup fails leaves a `.incoming-*`
        file the operator hygiene procedure finds, and startup is not failed
        over it.
        """
        stem = f"{_TEMPORARY_PREFIX}probe-{os.getpid()}-{os.urandom(8).hex()}"
        source, target = stem, f"{stem}-published"
        try:
            os.close(
                os.open(
                    source,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                    ARTIFACT_MODE,
                    dir_fd=root_fd,
                )
            )
        except OSError as error:
            raise ArtifactStorageError("root_unavailable", UNCHANGED) from _dropped(
                error
            )
        try:
            self._link(source, target, root_fd)
            try:
                self._link(source, target, root_fd)
            except FileExistsError:
                pass  # Exactly the refusal publication is built on.
            else:
                raise ArtifactStorageError("link_unsupported", UNCHANGED)
        except OSError as error:
            raise ArtifactStorageError("link_unsupported", UNCHANGED) from _dropped(
                error
            )
        finally:
            self._discard(target, root_fd)
            self._discard(source, root_fd)

    # -- the port -------------------------------------------------------------

    def store(self, artifact: SnapshotArtifact) -> str:
        """Write `artifact` under its own checksum, or return the existing one.

        Idempotent on content. Two submissions of identical bytes — under
        different request keys, from different principals, concurrently, or a
        retry of one interrupted submission — produce one file and one reference.

        The `_holds()` check below is an optimisation and a retry path, **not**
        the decision about whether to publish. That decision is `os.link`'s, in
        one syscall, inside `_publish` — see "Publication never overwrites" in
        the module docstring. Anything that appears under the checksum name after
        this check is handled there, by revalidating it, never by replacing it.
        """
        artifact.verify()
        checksum = artifact.checksum.hex_digest
        name = _name_for(checksum)
        root_fd = self._anchored_root(create=True)

        if self._holds(name, root_fd, checksum):
            # Already held, and proven to be a regular, service-owned, private
            # file whose bytes hash to their own name — re-verifying rather than
            # trusting the name is what makes "the same bytes" a fact.
            #
            # The directory is synced again because a previous attempt may have
            # published exactly these bytes and then failed to make the entry
            # durable. That attempt was refused; this retry is what completes
            # the guarantee it could not.
            self._fsync_root(root_fd)
            return _reference(checksum)

        temporary = f"{_TEMPORARY_PREFIX}{os.getpid()}-{os.urandom(8).hex()}"
        try:
            # `O_EXCL` with a random name, and the mode passed to `os.open`, so
            # the file is never briefly world-readable between creation and a
            # later `chmod`. `dir_fd` anchors it to the validated directory.
            descriptor = os.open(
                temporary,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                ARTIFACT_MODE,
                dir_fd=root_fd,
            )
            try:
                handle = os.fdopen(descriptor, "wb")
            except BaseException:
                # `os.fdopen` takes ownership only once it succeeds; closing
                # here is what stops a failure leaking the descriptor.
                os.close(descriptor)
                raise
            with handle:
                handle.write(artifact.raw_bytes())
                handle.flush()
                os.fsync(handle.fileno())
            # Verify *before* publishing: a corrupt temporary file that never
            # becomes an artifact is a failed submission, while a corrupt file
            # under the checksum name is a permanently wrong answer.
            self._verify_written(temporary, root_fd, checksum)
            self._publish(temporary, name, root_fd, checksum)
        except ArtifactStorageError:
            self._discard(temporary, root_fd)
            raise
        except OSError as error:
            self._discard(temporary, root_fd)
            raise ArtifactStorageError("write_failed", UNCHANGED) from _dropped(error)

        # Everything below is deliberately outside the block above, and the
        # order of the two statements is the durability contract.
        #
        # The checksum entry now exists: this attempt linked it, or another
        # writer did and it has been re-proved byte for byte. The temporary is a
        # second name for those same bytes, and removing it is the last
        # directory-entry change publication makes — so it happens *before* the
        # sync that makes every one of those changes durable, and it cannot
        # raise: `_discard` swallows, and it structurally cannot name anything
        # but a temporary.
        #
        # Swallowing means the removal is best effort rather than guaranteed. If
        # it fails, this call still returns the reference — the artifact is
        # published and correct — and one `.incoming-*` link to the same bytes
        # remains until an operator removes it (operations §5.6, "Temporary
        # files left by a failed cleanup"). That is a storage cost, not a
        # correctness one.
        #
        # `write_failed` — the one refusal here that claims nothing was
        # published — is therefore unreachable once publication has succeeded,
        # and a durability failure refuses the submission without destroying
        # bytes that are right.
        self._discard(temporary, root_fd)
        self._fsync_root(root_fd)
        return _reference(checksum)

    def load(self, checksum: str) -> SnapshotArtifact:
        name = _name_for(checksum)
        root_fd = self._anchored_root_for_reading()
        if root_fd is None:
            raise ArtifactNotStored()
        data = self._read_trusted(
            name,
            root_fd,
            missing=ArtifactNotStored,
            reason="read_failed",
            # A read refuses an entry that is under the checksum name and leaves
            # it there, which is what `PRESERVED` says. `ArtifactNotStored` keeps
            # its own `UNCHANGED`: there was nothing to preserve.
            outcome=PRESERVED,
        )
        if data is None:  # unreachable: `missing` is a type, so absence raises
            raise ArtifactNotStored()
        if hashlib.sha256(data).hexdigest() != checksum:
            raise ArtifactStorageError("checksum_mismatch", PRESERVED)
        return SnapshotArtifact(data, SnapshotChecksum(checksum))

    def contains(self, checksum: str) -> bool:
        """Whether a regular file is held under that name.

        Deliberately does not follow symbolic links: a dangling or redirecting
        symlink named for a checksum is not an artifact this store holds. It
        answers a question about presence only — `load` is what decides whether
        the file may be read, and it re-checks type, owner and mode there.
        """
        name = _name_for(checksum)
        root_fd = self._anchored_root_for_reading()
        if root_fd is None:
            return False
        try:
            info = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            return False
        except OSError as error:
            raise ArtifactStorageError("read_failed", UNCHANGED) from _dropped(error)
        return stat.S_ISREG(info.st_mode)

    # -- the anchored root ----------------------------------------------------

    def _anchored_root(self, *, create: bool) -> int:
        """The validated directory descriptor every operation is resolved against.

        Opened once and re-proved on every call: `os.fstat` on the descriptor
        itself, so the directory being checked is necessarily the directory
        being used. The pathname comparison afterwards detects a replacement; it
        does not grant anything.
        """
        if self._root_fd == _CLOSED:
            descriptor = self._open_trusted_root(create=create)
            try:
                self._root_identity = _identity(os.fstat(descriptor))
            except BaseException:
                os.close(descriptor)
                raise
            self._root_fd = descriptor
        else:
            _require_trusted_root(os.fstat(self._root_fd))
        self._require_configured_path_unchanged()
        return self._root_fd

    def _anchored_root_for_reading(self) -> int | None:
        """The anchored root for a read, or `None` when there is no store yet.

        A read never creates the directory: a `load` that found nothing is an
        ordinary outcome, and answering it by making a directory would be a
        mutation performed by a query.
        """
        try:
            return self._anchored_root(create=False)
        except _RootAbsent:
            return None

    def _open_trusted_root(self, *, create: bool) -> int:
        try:
            descriptor = self._open_root_descriptor()
        except FileNotFoundError:
            if not create:
                raise _RootAbsent() from None
            self._create_root()
            try:
                descriptor = self._open_root_descriptor()
            except OSError as error:
                raise ArtifactStorageError(
                    "root_unavailable", UNCHANGED
                ) from _dropped(error)
        try:
            _require_trusted_root(os.fstat(descriptor))
        except BaseException:
            os.close(descriptor)
            raise
        return descriptor

    def _open_root_descriptor(self) -> int:
        """`O_DIRECTORY | O_NOFOLLOW`, so the open itself does the refusing."""
        try:
            return os.open(self._root, os.O_RDONLY | _DIRECTORY | _NOFOLLOW)
        except FileNotFoundError:
            raise
        except NotADirectoryError as error:
            # `O_DIRECTORY` against a regular file, a device or a socket.
            raise ArtifactStorageError(
                "root_not_a_directory", UNCHANGED
            ) from _dropped(error)
        except OSError as error:
            # `ELOOP` lands here: `O_NOFOLLOW` refused a symlinked root rather
            # than following it to wherever its owner pointed it.
            if error.errno == errno.ELOOP:
                raise ArtifactStorageError(
                    "root_untrusted", UNCHANGED
                ) from _dropped(error)
            raise ArtifactStorageError("root_unavailable", UNCHANGED) from _dropped(
                error
            )

    def _create_root(self) -> None:
        try:
            self._root.mkdir(mode=ROOT_MODE, parents=True, exist_ok=True)
        except OSError as error:
            raise ArtifactStorageError("root_unavailable", UNCHANGED) from _dropped(
                error
            )

    def _require_configured_path_unchanged(self) -> None:
        """Refuse if the configured pathname no longer names the anchored root.

        Not a security control — the anchoring is. This exists so that an
        operator who moved or replaced the directory is told, instead of the
        service quietly continuing to write into an inode that no longer has a
        name they know.
        """
        try:
            info = os.stat(self._root, follow_symlinks=False)
        except OSError as error:
            raise ArtifactStorageError("root_replaced", UNCHANGED) from _dropped(error)
        if _identity(info) != self._root_identity:
            raise ArtifactStorageError("root_replaced", UNCHANGED)

    @property
    def ancestors(self) -> TrustedAncestors:
        """The ancestor rule this store walks at startup. For tests and review."""
        return self._ancestors

    def _fsync_root(self, root_fd: int) -> None:
        """Make the publication's directory entries durable, or refuse.

        A failure here used to be swallowed (review finding I-2). It is now a
        typed storage failure, so the caller refuses the submission rather than
        committing a database row against an artifact whose directory entry may
        not survive a power loss. It is the anchored descriptor that is synced,
        so this cannot end up syncing some other directory that acquired the
        configured name.
        """
        try:
            os.fsync(root_fd)
        except OSError as error:
            raise ArtifactStorageError(
                "durability_unconfirmed", UNRESOLVED
            ) from _dropped(error)

    # -- artifacts ------------------------------------------------------------

    def _holds(self, name: str, root_fd: int, checksum: str) -> bool:
        """Whether `name` is already this artifact, refusing anything unsafe.

        Called twice, for two different reasons: once before writing anything, as
        the retry and idempotency path, and once from `_publish` when the link
        reported that another writer got there first. Both need the same answer,
        established the same way — through the anchored descriptor, `O_NOFOLLOW`,
        `fstat` and the bytes — which is why it is one method and not a cheaper
        check in the second position.
        """
        data = self._read_trusted(
            name, root_fd, missing=None, reason="verify_failed", outcome=PRESERVED
        )
        if data is None:
            return False
        if hashlib.sha256(data).hexdigest() != checksum:
            # A file under this name whose content is wrong. It is refused and
            # deliberately left exactly as it is: overwriting it would destroy
            # whatever an operator needs in order to explain it.
            raise ArtifactStorageError("checksum_mismatch", PRESERVED)
        return True

    def _verify_written(self, name: str, root_fd: int, checksum: str) -> None:
        """Re-read this attempt's own temporary file before it is published.

        `UNCHANGED`, not `PRESERVED`: the file being refused here is the
        temporary this call created a moment ago and is about to discard, not an
        entry found under the checksum name.
        """
        written = self._read_trusted(
            name, root_fd, missing=None, reason="verify_failed", outcome=UNCHANGED
        )
        if written is None or hashlib.sha256(written).hexdigest() != checksum:
            raise ArtifactStorageError("checksum_mismatch", UNCHANGED)

    def _publish(
        self, temporary: str, name: str, root_fd: int, checksum: str
    ) -> None:
        """Create the checksum entry, or prove the entry that is already there.

        The whole mechanism is `os.link`: `linkat(2)` either creates the
        destination entry or fails `EEXIST`, and it has no mode in which it
        removes what is already under the name. Test and creation are one
        syscall, so — unlike a pathname check followed by `os.replace`, which is
        the same race in a different shape — there is no window between them for
        an entry to appear in.

        Returning normally means the checksum entry exists *and* has been proved
        to be this artifact, whether this call created it or another writer did.
        """
        for _ in range(_PUBLICATION_ATTEMPTS):
            try:
                self._link(temporary, name, root_fd)
                return
            except FileExistsError:
                pass
            # Somebody else published under this name. Open it through the
            # anchored descriptor and re-prove it from nothing: type, owner,
            # mode and content. Anything that fails raises out of here with the
            # entry untouched, and the caller discards only the temporary.
            if self._holds(name, root_fd, checksum):
                return
            # Present for `EEXIST` and absent by the open. Nothing in this store
            # ever removes an artifact, so production cannot reach this; the loop
            # is bounded so that a filesystem that reaches it anyway refuses.
        raise ArtifactStorageError("publication_unsettled", UNCHANGED)

    @staticmethod
    def _link(source: str, destination: str, root_fd: int) -> None:
        """One anchored, non-following, create-only directory-entry creation.

        `follow_symlinks=False` states the intent rather than changing the
        outcome — the source is a file this process created with `O_EXCL` and
        cannot be a symlink — and `linkat(2)` never follows the *destination*,
        so a checksum name currently holding a symlink is an `EEXIST` to
        revalidate, not something to write through.
        """
        os.link(
            source,
            destination,
            src_dir_fd=root_fd,
            dst_dir_fd=root_fd,
            follow_symlinks=False,
        )

    def _read_trusted(
        self,
        name: str,
        root_fd: int,
        *,
        missing: type[ArtifactStorageError] | None,
        reason: str,
        outcome: StorageOutcome,
    ) -> bytes | None:
        """Read `name`, having proved it is a private, service-owned regular file.

        The proof and the read share one descriptor, so nothing can be swapped
        between the two, and the name is resolved against the anchored root, so
        nothing can redirect which directory it came from. `missing=None`
        reports an absent file as `None`; otherwise the given error is raised.

        `outcome` is what a refusal here may claim, and it differs by caller
        rather than by reason: refusing an entry found under the checksum name
        leaves that entry in place (`PRESERVED`), while refusing this attempt's
        own temporary file leaves the store as it was (`UNCHANGED`). Nothing on
        either path repairs, replaces or removes what it refused.
        """
        try:
            descriptor = os.open(
                name, os.O_RDONLY | _NOFOLLOW, dir_fd=root_fd
            )
        except FileNotFoundError:
            if missing is None:
                return None
            raise missing() from None
        except OSError as error:
            # `ELOOP` lands here: `O_NOFOLLOW` refused to open a symlink, which
            # is a name pointing at a file this store did not write. The link
            # itself is left exactly where it is, and its target is not touched.
            raise ArtifactStorageError("artifact_untrusted", outcome) from _dropped(
                error
            )
        try:
            _require_trusted_artifact(os.fstat(descriptor), outcome)
            return _read_all(descriptor)
        except OSError as error:
            raise ArtifactStorageError(reason, outcome) from _dropped(error)
        finally:
            os.close(descriptor)

    def _discard(self, name: str, root_fd: int) -> None:
        """Remove a temporary entry, and structurally nothing else.

        The prefix is checked *before* the `unlink`. That is not defensive
        decoration: publication now leaves the bytes under two names for a
        moment, so this function runs on the success path as well as the failure
        paths, and the one thing it must never be able to do — however this
        module is edited later — is remove a published checksum entry because a
        cleanup step went wrong.

        Everything after the check is best effort, and the caller is told
        nothing about whether it worked: the `OSError` is swallowed rather than
        raised or reported. On a failure path a leftover `.incoming-*` file
        holds bytes that were never published under a checksum name; on the
        success path it holds a second link to bytes that were. Neither is
        reachable through any route — the only name a route resolves is the
        checksum one — and failing an otherwise correct submission over an
        unlink would help nobody.

        What a leftover does cost is storage, and an operator has to be able to
        find it. `docs/operations/foundry-snapshot-submission.md` §5.6,
        "Temporary files left by a failed cleanup", is the read-only procedure
        for that. This module deliberately provides no listing and no deletion
        of its own.
        """
        if not name.startswith(_TEMPORARY_PREFIX):
            return
        try:
            os.unlink(name, dir_fd=root_fd)
        except OSError:
            pass


class _RootAbsent(Exception):
    """Internal: the configured root does not exist and was not to be created."""


def _name_for(checksum: str) -> str:
    """The artifact's name *within* the anchored root, never a path.

    A validated hex digest plus a fixed suffix can hold no separator and no
    `..`, and it is resolved relative to a directory descriptor, so containment
    is a property of the name's shape rather than of a comparison somebody has
    to remember to make. The shape is still asserted, so that it stays true if
    the naming rule is ever changed.
    """
    if not _SHA256_HEX.fullmatch(checksum):
        raise ArtifactStorageError("invalid_checksum", UNCHANGED)
    name = f"{checksum}{_SUFFIX}"
    if os.sep in name or (os.altsep and os.altsep in name) or name in (".", ".."):
        raise ArtifactStorageError("containment_violation", UNCHANGED)
    return name


def _reference(checksum: str) -> str:
    """The opaque reference stored in `foundry_snapshots.artifact_location`.

    Deliberately not an absolute path: the column is readable by anyone who can
    read import history, and a host path is infrastructure detail that such a
    reader has no use for. The operator resolves it against the configured root,
    which they already know.
    """
    return f"snapshot/{checksum}{_SUFFIX}"


def _identity(info: os.stat_result) -> tuple[int, int]:
    """What makes two names the same directory: device plus inode."""
    return (info.st_dev, info.st_ino)


def _require_trusted_root(info: os.stat_result) -> None:
    """The root must be a directory this account owns and nobody else can enter.

    `info` always comes from `os.fstat` on the anchored descriptor, so this is a
    statement about the directory that is about to be used, not about whatever a
    pathname currently resolves to.
    """
    if not stat.S_ISDIR(info.st_mode):
        raise ArtifactStorageError("root_not_a_directory", UNCHANGED)
    if info.st_uid != os.geteuid():
        raise ArtifactStorageError("root_not_owned", UNCHANGED)
    if stat.S_IMODE(info.st_mode) & FORBIDDEN_MODE_BITS:
        raise ArtifactStorageError("root_permissive", UNCHANGED)


def _require_trusted_artifact(info: os.stat_result, outcome: StorageOutcome) -> None:
    """An artifact must be a regular file this account owns and nobody else reads.

    `outcome` comes from the caller because the same three refusals mean
    different things about the filesystem depending on what was being examined —
    see `_read_trusted`. Nothing here repairs or removes what it refuses, on
    either path.
    """
    if not stat.S_ISREG(info.st_mode):
        raise ArtifactStorageError("artifact_not_a_regular_file", outcome)
    if info.st_uid != os.geteuid():
        raise ArtifactStorageError("artifact_not_owned", outcome)
    if stat.S_IMODE(info.st_mode) & FORBIDDEN_MODE_BITS:
        raise ArtifactStorageError("artifact_permissive", outcome)


def _read_all(descriptor: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        chunk = os.read(descriptor, _READ_CHUNK)
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def _dropped(error: BaseException) -> None:
    """Discard the causing exception rather than chaining it.

    An `OSError` renders the path it failed on, and this store's paths are
    infrastructure detail. Chaining would put them into any traceback that is
    rendered or logged. Returning `None` makes `raise ... from _dropped(error)`
    read as the deliberate act it is.
    """
    return None
