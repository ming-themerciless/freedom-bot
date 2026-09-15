"""The reviewed case program — conflict **C-2**'s payload, and the one file the
harness places inside the disposable root for the kernel to run.

## What it is

A single-file Python program with no build step. The generated `install` vector
copies **this file, byte for byte**, to `<root>/bin/case`, so the SHA-256 the
review manifest records for
`tools/phase_5_0_evidence/execution/case_program.py` is simultaneously the source
digest and the installation digest. There is no compiler, no generated code, no
downloaded binary and nothing whose bytes are not in this repository.

It is executed only through the Option-B vector `case_runtime` defines:

```text
<interpreter> -I -S <root>/bin/case <verb> [<argument> …]
```

so the program the kernel runs is named in the reviewed vector, there is no
shebang, and nothing is resolved through `PATH`.

## Why it is in the execution tier

`tests/phase_5_0_evidence/test_no_execution.py` partitions this package into a
planning tier that may not touch a file at all and an execution tier that may act
on the harness's behalf. This program's whole purpose is `open(2)`, `pwrite(2)`,
`ftruncate(2)`, `rename(2)`, `unlink(2)`, `symlink(2)`, `statvfs(3)`, `mkdir(2)`,
`fchmod(2)`, `fstat(2)` and two `ioctl(2)`s, so the planning tier is not where it
can live. It is declared in the execution tier alongside `boundary` and
`materializer`, and the same suite still asserts, of this file, that it starts no
process, reaches no shell, opens no socket and imports nothing outside a fixed
standard-library allowlist.

## The four refusals it performs on itself

The planner and the executor both validate the vector before a process exists.
This program validates it **again**, from its own constants, because a check made
only by the caller is a check an edited caller can skip:

1. **isolated mode is actually in effect.** `sys.flags.isolated` and
   `sys.flags.no_site` must both be set. `-I` removes the script's directory and
   the user site directory from `sys.path` and ignores `PYTHONPATH`; `-S` skips
   `site`, so the virtual environment's `site-packages` never joins it. If either
   is missing the program refuses rather than running with an import path
   somebody else chose.
2. **it is one of the two reviewed copies, and which one decides what it may
   do.** `sys.argv[0]` must be `CASE_PROGRAM_PATH` — the installed copy — or
   `BOOTSTRAP_PROGRAM_PATH`, the reviewed source in the repository tree. A copy
   placed anywhere else refuses. The two are **byte-identical**, because
   `install` copies the second to the first, so one digest covers both.
3. **the verb, its arity and its argument kinds** are the closed table below.
   An unknown verb, a wrong count, a trailing argument, an unreviewed open-flag
   combination and any link target but the reviewed relative generation name are
   each refused.
4. **every path is strictly inside the disposable root**, absolute, normalized,
   free of `..` and drawn from a narrow character class — except the two
   bootstrap verbs, whose one argument must be the disposable root itself and
   nothing else. There is no option that widens the root and no verb that takes
   a path outside it.

## The bootstrap partition — conflict **C-8**

A helper that creates the disposable root cannot first be installed inside it.
So the same reviewed bytes are executed from **two** places, and each place runs
a disjoint half of the verb table:

| Copy | `sys.argv[0]` | Verbs it may run |
|---|---|---|
| **bootstrap** | `BOOTSTRAP_PROGRAM_PATH`, the repository source the manifest pins | `mkroot`, `statroot` — and no other |
| **installed** | `CASE_PROGRAM_PATH`, `<root>/bin/case` | every other verb — and neither of those two |

The partition is total and is enforced here as well as by the planner. The
installed copy cannot create the root it lives in, and the bootstrap copy cannot
perform an experiment: a run that lost its installed program cannot fall back to
the repository and keep going.

`mkroot` is the **only** creation in this program whose success is ownership.
`os.mkdir(2)` reports pre-existence as `EEXIST` and reports it for a directory,
a file, a symbolic link and a dangling symbolic link alike, which is the unique,
documented status no permitted distribution binary has. Exit 0 therefore means
*this call created this directory*, and every other status means *no ownership*.

## What it deliberately cannot do

Invoke a shell, start another program, open a socket, import a database driver,
import any third-party distribution, accept an arbitrary path, write arbitrary
content, read an arbitrary file, or offer a general file-operation interface. The
only bytes it ever writes are `REVIEWED_BYTES`, and the only files it reads are
`/proc/self/status` and the interpreter's own executable — both named as literals,
neither taken from an argument.

It also offers **no general `ioctl` and no mask**: `FS_IOC_GETFLAGS` and
`FS_IOC_SETFLAGS` are the two request numbers in this file, the four flag verbs
name their one bit in their own bodies, and no argument kind carries a flag, a
mask or a request number. It creates exactly one directory — the disposable root,
by the one bootstrap verb, at the one literal path — and it removes nothing at
all: `rmdir` is not a verb here and `unlink` is confined to the root's interior.

## The one native call, and why it is here

`_prctl_get_securebits()` calls `prctl(PR_GET_SECUREBITS)` through `ctypes`, and
it is the **only** foreign call in this repository. §2.13.5c requires every
`E1 … E8` identity's final securebits to be observed inside the exec'd process,
and the kernel exposes securebits through `prctl(2)` and through no file. The
exception is bounded to this one function: the already-loaded C runtime
(`CDLL(None)`), the literal symbol `prctl`, fixed `argtypes`/`restype`, the
literal operation `PR_GET_SECUREBITS` with zero remaining arguments, an errno
read through `ctypes.get_errno()` on `-1`, and a range check before the value can
be emitted. Nothing about the call is reachable from a vector argument, and there
is no reusable arbitrary-FFI helper. `test_no_execution.py` asserts every clause
of that against this file's syntax tree, and asserts that no other module imports
`ctypes` at all.

## What it prints

`key=value` lines of ASCII on standard output, drawn from the closed key set the
matching `capture.CapturePolicy` parses. It prints no path, no message from the
operating system and no exception text: a refusal is `result=refused` plus the
`errno` name, which is the evidence every §2.13.2a and `JNL-52` case is stated
in.

Exit status: `0` when the operation returned; one of `REFUSAL_EXIT_CODES` when the
operating system refused it with an errno the reviewed cases name; `1` for any
other refusal; `64` when **this program** refused the vector; `65` on an internal
failure; and `66` when a reviewed observation could not be made at all. The codes
are distinct so that *"the kernel denied it, and for this reason"*, *"the vector
was wrong"*, *"the harness broke"* and *"the state could not be read"* are never
the same observation — and so that a step which may record only its exit status
still carries the errno its case is stated in.

For `mkroot` the split does a second job, and it is conflict **C-8**'s
conservative half. `0`, `1`, `10 … 16` and `64` are all statuses in which
`os.mkdir` either was not reached or returned an error, so **nothing was
created**; `65` and `66` are statuses in which a directory may exist and this
process cannot say which one. The executor reads the first group as *no
ownership, nothing to remove* and the second as *bounded residue*, and neither
is a clean success.
"""
from __future__ import annotations

import array
import ctypes
import errno
import fcntl
import hashlib
import os
import sys

# ---------------------------------------------------------------------------
# The reviewed constants
# ---------------------------------------------------------------------------

#: The disposable root Peter Duscha confirmed on 2026-09-05. It is repeated here
#: rather than imported because this program runs under `-I`, where nothing but
#: the standard library is importable — that isolation is the point, and it is
#: worth one duplicated constant. `tests/phase_5_0_evidence/test_case_program.py`
#: asserts this value equals `approved_target.APPROVED_TARGET.root_path`, so the
#: two cannot drift.
DISPOSABLE_ROOT = "/var/lib/fb-evidence-p5-0"

#: Where the installed program lives. In installed mode `sys.argv[0]` must be
#: exactly this.
CASE_PROGRAM_PATH = DISPOSABLE_ROOT + "/bin/case"

#: **Conflict C-8's bootstrap location.** The reviewed source in the repository
#: tree on the disposable host, which the run does not create, does not modify
#: and does not remove: its lifecycle is the repository's. It is repeated here
#: rather than imported for `DISPOSABLE_ROOT`'s reason, and
#: `tests/phase_5_0_evidence/test_case_program.py` asserts it equals
#: `case_runtime.CASE_PROGRAM_SOURCE_PATH`, so the two cannot drift.
BOOTSTRAP_PROGRAM_PATH = (
    "/opt/freedom-blades/platform/tools/phase_5_0_evidence/execution/case_program.py"
)

#: §2.13.3's `…/journal/current` points at the current generation by **relative
#: name**. One name, and no other target is accepted.
GENERATION_LINK_NAME = "000001.journal"

#: The only bytes this program ever writes. Seventeen ASCII bytes, fixed, with no
#: substitution: a probe that wrote caller-supplied content would be a general
#: write interface with extra steps.
REVIEWED_BYTES = b"fb-evidence-p5-0\n"

#: `FS_APPEND_FL` and `FS_IMMUTABLE_FL` from `include/uapi/linux/fs.h`, and the
#: two ioctl request numbers for a 64-bit x86 kernel: `FS_IOC_GETFLAGS` is
#: `_IOR('f', 1, long)` and `FS_IOC_SETFLAGS` is `_IOW('f', 2, long)`.
#:
#: **The two flags are separate constants used by separate verbs — conflict
#: C-6.** There is no verb that takes a flag name, a mask or an ioctl request
#: number as an argument: `getflags`/`clearflags` name `FS_APPEND_FL` in their
#: own bodies and `getimmutable`/`clearimmutable` name `FS_IMMUTABLE_FL` in
#: theirs. A caller therefore chooses a **verb**, and the set of bits any verb
#: can reach is fixed in this file rather than supplied to it.
FS_APPEND_FL = 0x00000020
FS_IMMUTABLE_FL = 0x00000010
FS_IOC_GETFLAGS = 0x80086601
FS_IOC_SETFLAGS = 0x40086602

#: The mode `mkroot` creates the disposable root with, applied again with
#: `fchmod(2)` on the descriptor of the directory it just created so the process
#: umask cannot decide it. §2.13.3's facsimile root is `root:root 0755`; the
#: owner and group are the harness's own, because `mkdir(2)` gives the creating
#: process's uid and gid and this program is exec'd by `E7`.
ROOT_DIRECTORY_MODE = 0o755

#: `S_IFMT` and `S_IFDIR` as literals. The `stat` module is not in this
#: program's permitted import set — it runs under `-I -S` and the set is
#: asserted against the source — and widening that set for two constants would
#: be relaxing a guard rather than writing two constants.
_S_IFMT = 0o170000
_S_IFDIR = 0o040000

#: The character class a path argument may contain. Narrow on purpose: every path
#: this program is given was generated from the confirmed target's own root.
_PATH_CHARACTERS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "._-/"
)

EXIT_RETURNED = 0
#: An operating-system refusal whose errno is not one the reviewed cases name.
EXIT_REFUSED = 1
EXIT_VECTOR_REFUSED = 64
EXIT_INTERNAL = 65
#: A reviewed observation this program was required to make and could not.
#: Distinct from every other code so that *"the identity could not be observed"*
#: is never recorded as *"the kernel refused the operation"*, as *"the vector was
#: wrong"* or as a pass. It is not in `satisfying_statuses` for any step.
EXIT_OBSERVATION_UNAVAILABLE = 66

#: `PR_GET_SECUREBITS` from `include/uapi/linux/prctl.h`. One literal operation
#: number, used in one call, and the only one this program ever passes to
#: `prctl(2)`.
PR_GET_SECUREBITS = 27

#: The largest value `PR_GET_SECUREBITS` can legitimately return. `securebits.h`
#: defines eight bits — `SECURE_NOROOT`, `SECURE_NO_SETUID_FIXUP`,
#: `SECURE_KEEP_CAPS` and `SECURE_NO_CAP_AMBIENT_RAISE`, each with its `_LOCKED`
#: companion — occupying bits 0 … 7. A value outside `0 … 0xff` is not a
#: securebits word, and it is refused rather than emitted.
#:
#: `case_runtime.SECUREBITS_MAX` is the planning tier's copy, and
#: `tests/phase_5_0_evidence/test_case_program.py` asserts the two agree.
SECUREBITS_MAX = 0xFF

#: **The errno reaches the exit status, from a closed table.** §2.13.2a states
#: each case's expected refusal as a specific errno — `EPERM` for append-only
#: enforcement, `EROFS` for the sandbox bind, `EACCES` for discretionary access —
#: and the difference between them is the whole of the attribution. A step whose
#: purpose is a side effect may record only its exit status (`plan.CommandStep`
#: enforces that), so an errno that lived only in the output would be unavailable
#: to exactly the Stage-4 cases that need it. Mapping it to a distinct exit code
#: puts the expected errno into the reviewed plan's `satisfying_statuses`, where a
#: reviewer approves it in advance, instead of leaving *"it exited non-zero"* to
#: stand in for *"the kernel refused it for this reason"*.
#:
#: `case_runtime.REFUSAL_EXIT_CODES` is the planning tier's copy, and
#: `tests/phase_5_0_evidence/test_case_program.py` asserts the two agree.
REFUSAL_EXIT_CODES = {
    errno.EPERM: 10,
    errno.EACCES: 11,
    errno.EROFS: 12,
    errno.ENOTTY: 13,
    errno.EOPNOTSUPP: 14,
    errno.EEXIST: 15,
    errno.ENOENT: 16,
}

#: `open(2)` flag combinations, by the name the vector carries. Closed: a
#: combination that is not a value here cannot be requested.
OPEN_FLAGS = {
    "rdonly": os.O_RDONLY,
    "wronly": os.O_WRONLY,
    "wronly-trunc": os.O_WRONLY | os.O_TRUNC,
    "wronly-append": os.O_WRONLY | os.O_APPEND,
    "wronly-append-trunc": os.O_WRONLY | os.O_APPEND | os.O_TRUNC,
    "create-excl": os.O_WRONLY | os.O_CREAT | os.O_EXCL,
}

#: The two modes a write-bearing verb may open with.
WRITE_FLAGS = {
    "wronly": os.O_WRONLY,
    "wronly-append": os.O_WRONLY | os.O_APPEND,
}

#: Argument kinds, matching `case_runtime.ArgumentKind` one for one — by the
#: same strings, so the two verb tables compare directly and
#: `tests/phase_5_0_evidence/test_case_program.py` asserts they are equal.
PATH = "target_path"
OPEN_MODE = "open_mode"
WRITE_MODE = "write_mode"
LINK_NAME = "link_name"
#: **Conflict C-8.** The one argument kind whose only admissible value is the
#: disposable root itself. It exists because the root is the one path that is not
#: *strictly inside* the root, and it admits exactly one string — so it is a
#: constant the vector states rather than a path the caller chooses.
ROOT_PATH = "root_path"
#: **r6 §6.2.** An index into the descriptor table this step inherited, and into
#: nothing else. It is never a number a vector author chooses freely: the
#: executor clears `FD_CLOEXEC` on a declared set starting at descriptor 3 and
#: passes the step a table naming each entry, and an index outside that range —
#: or one that is not open, or one that is open on something that is not a
#: directory — refuses. A step that needs a descriptor it was not given refuses;
#: it does not open a path to obtain one.
DIRFD = "dirfd"
#: **r6 §6.2.** Exactly one path component. Not a path: no separator, no `.`,
#: no `..`, no empty string. The prefix is bound by the descriptor the `DIRFD`
#: argument names, exactly as `unlink(2)` describes the prefix being bound, and
#: a component that could carry a separator would be a pathname that binding
#: does not cover.
COMPONENT = "component"

#: The highest `DIRFD` index a vector may name. The declared table starts at
#: descriptor 3 and r6 §1.3.3's inventory is ten directories at its widest, so
#: the bound is generous and finite — and an input surface with no bound is an
#: input surface whose worst case nobody reviewed.
FIRST_DIRFD = 3
MAX_DIRFD = 31

#: The longest one path component may be, which is what `NAME_MAX` is on every
#: filesystem this design contemplates.
MAX_COMPONENT_BYTES = 255

#: The closed verb table: verb → the kind of each argument, in order.
VERBS = {
    "open": (OPEN_MODE, PATH),
    "pwrite": (WRITE_MODE, PATH),
    "append": (PATH,),
    "ftruncate": (WRITE_MODE, PATH),
    "rename": (PATH, PATH),
    "unlink": (PATH,),
    "symlink": (PATH, LINK_NAME),
    "statvfs": (PATH,),
    "getflags": (PATH,),
    "clearflags": (PATH,),
    # **Conflict C-6.** The immutable half of §2.13.5c, as two verbs that name
    # `FS_IMMUTABLE_FL` in their own bodies. Neither takes a flag argument.
    "getimmutable": (PATH,),
    "clearimmutable": (PATH,),
    # **r6 §6.2.** The four descriptor-relative verbs. Each resolves **one
    # component** relative to a descriptor the step inherited, so no operation
    # below resolves a pathname from the root. They are what replaces the
    # withdrawn comparison of revision 1 §9.2(b): the prefix is bound by a held
    # descriptor rather than checked after the fact.
    "openat": (DIRFD, OPEN_MODE, COMPONENT),
    "unlinkat": (DIRFD, COMPONENT),
    "renameat": (DIRFD, COMPONENT, DIRFD, COMPONENT),
    "fstatat": (DIRFD, COMPONENT),
    # **Conflict C-8.** The two bootstrap verbs.
    "mkroot": (ROOT_PATH,),
    "statroot": (ROOT_PATH,),
    "identity": (),
    "runtime": (),
}

#: The verbs the **bootstrap** copy may run, and the installed copy may not.
#: The complement is every other key of `VERBS`, and the partition is total:
#: `main()` refuses a bootstrap verb from the installed path and every other verb
#: from the bootstrap path.
BOOTSTRAP_VERBS = frozenset({"mkroot", "statroot"})


class VectorRefused(Exception):
    """This program will not run the vector it was given."""


class ObservationUnavailable(Exception):
    """A reviewed observation could not be made, so no result may be reported.

    It carries an errno **name** from `errno.errorcode` — or `"none"` when the
    call returned a value that is not a securebits word — and nothing else. No
    message from the operating system, no address, no value.
    """

    def __init__(self, errno_name: str) -> None:
        super().__init__(errno_name)
        self.errno_name = errno_name


# ---------------------------------------------------------------------------
# Vector validation, performed again here
# ---------------------------------------------------------------------------


def validate_path(candidate: str) -> str:
    """An absolute, normalized path strictly inside the disposable root."""
    if not isinstance(candidate, str) or not candidate:
        raise VectorRefused("a path argument is non-empty text")
    if not set(candidate) <= _PATH_CHARACTERS:
        raise VectorRefused("a path argument is drawn from a narrow character class")
    if not candidate.startswith("/"):
        raise VectorRefused("a path argument is absolute")
    segments = candidate.split("/")
    if any(segment in ("", ".", "..") for segment in segments[1:]):
        raise VectorRefused("a path argument carries no empty or relative segment")
    root = DISPOSABLE_ROOT
    if not candidate.startswith(root + "/") or candidate == root:
        raise VectorRefused("a path argument is strictly inside the disposable root")
    return candidate


def validate_root(candidate: str) -> str:
    """The disposable root itself, and no other string — conflict **C-8**.

    Not a path check: an equality check against one literal. `mkroot` creates the
    root and `statroot` reads the identity of the object at it, and neither has
    any other subject.
    """
    if candidate != DISPOSABLE_ROOT:
        raise VectorRefused("a root argument is the confirmed disposable root itself")
    return candidate


def validate_dirfd(candidate: str) -> str:
    """An index into the inherited table, in the declared range.

    The **semantic** check — that index 4 is the journal directory and not some
    other one — is the executor's, because the table is the executor's. What
    this program can establish is that the index is in the declared range and
    that the descriptor is open on a directory, and `_require_directory_fd`
    below does the second half immediately before the call. An index that is not
    open fails with `EBADF`, which is the kernel refusing an unregistered
    descriptor rather than this program permitting one.
    """
    if not isinstance(candidate, str) or not candidate.isdigit():
        raise VectorRefused("a descriptor argument is a non-negative decimal index")
    index = int(candidate)
    if index < FIRST_DIRFD or index > MAX_DIRFD:
        raise VectorRefused(
            "a descriptor argument is an index into the table this step "
            "inherited, which starts at descriptor 3 and is bounded"
        )
    return candidate


def validate_component(candidate: str) -> str:
    """Exactly one path component, drawn from the same narrow character class."""
    if not isinstance(candidate, str) or not candidate:
        raise VectorRefused("a component argument is non-empty text")
    if not set(candidate) <= _PATH_CHARACTERS:
        raise VectorRefused(
            "a component argument is drawn from a narrow character class"
        )
    if len(candidate.encode("utf-8")) > MAX_COMPONENT_BYTES:
        raise VectorRefused("a component argument is within NAME_MAX")
    if "/" in candidate or candidate in (".", ".."):
        raise VectorRefused(
            "a component argument is exactly one path component, so it cannot "
            "reach past the descriptor that binds its prefix"
        )
    return candidate


def validate_arguments(verb: str, arguments: list[str]) -> tuple[str, ...]:
    """The verb's exact arity and each argument's declared kind."""
    kinds = VERBS.get(verb)
    if kinds is None:
        raise VectorRefused("the verb is not one of the reviewed operations")
    if len(arguments) != len(kinds):
        raise VectorRefused("the verb was given the wrong number of arguments")
    checked = []
    for kind, argument in zip(kinds, arguments):
        if kind == PATH:
            checked.append(validate_path(argument))
        elif kind == ROOT_PATH:
            checked.append(validate_root(argument))
        elif kind == OPEN_MODE:
            if argument not in OPEN_FLAGS:
                raise VectorRefused("the open flag combination is not a reviewed one")
            checked.append(argument)
        elif kind == WRITE_MODE:
            if argument not in WRITE_FLAGS:
                raise VectorRefused("the write mode is not a reviewed one")
            checked.append(argument)
        elif kind == DIRFD:
            checked.append(validate_dirfd(argument))
        elif kind == COMPONENT:
            checked.append(validate_component(argument))
        else:
            if argument != GENERATION_LINK_NAME:
                raise VectorRefused("the link target is not the reviewed generation name")
            checked.append(argument)
    return tuple(checked)


# ---------------------------------------------------------------------------
# The operations
# ---------------------------------------------------------------------------


def _size(descriptor: int) -> int:
    return int(os.fstat(descriptor).st_size)


def _do_open(mode: str, path: str) -> dict:
    descriptor = os.open(path, OPEN_FLAGS[mode], 0o600)
    os.close(descriptor)
    return {}


def _do_pwrite(mode: str, path: str) -> dict:
    descriptor = os.open(path, WRITE_FLAGS[mode])
    try:
        before = _size(descriptor)
        written = os.pwrite(descriptor, REVIEWED_BYTES, 0)
        after = _size(descriptor)
    finally:
        os.close(descriptor)
    return {"bytes_written": written, "pre_size": before, "post_size": after}


def _do_append(path: str) -> dict:
    descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
    try:
        before = _size(descriptor)
        written = os.write(descriptor, REVIEWED_BYTES)
        os.fsync(descriptor)
        after = _size(descriptor)
    finally:
        os.close(descriptor)
    return {"bytes_written": written, "pre_size": before, "post_size": after}


def _do_ftruncate(mode: str, path: str) -> dict:
    descriptor = os.open(path, WRITE_FLAGS[mode])
    try:
        os.ftruncate(descriptor, 0)
        after = _size(descriptor)
    finally:
        os.close(descriptor)
    return {"post_size": after}


def _do_rename(source: str, destination: str) -> dict:
    os.rename(source, destination)
    return {}


def _do_unlink(path: str) -> dict:
    os.unlink(path)
    return {}


def _do_symlink(link_path: str, target_name: str) -> dict:
    os.symlink(target_name, link_path)
    return {"link_target": target_name}


def _require_directory_fd(index: str) -> int:
    """The inherited descriptor, or a refusal. **This is the unregistered check.**

    Two things are established immediately before every descriptor-relative
    call, and neither can be established by reading the vector:

    1. the descriptor is **open** in this process. One that is not raises
       `EBADF`, which is the kernel refusing a descriptor the step was not
       given; and
    2. it refers to a **directory**. A descriptor open on a file is not one an
       `*at()` call may traverse, and using it would be reaching an object the
       executor's table did not name.

    A step that fails either does not fall back to a path. There is no path to
    fall back to: the whole point of the argument kind is that the prefix is the
    descriptor.
    """
    descriptor = int(index)
    try:
        facts = os.fstat(descriptor)
    except OSError as failure:
        raise ObservationUnavailable(
            errno.errorcode.get(failure.errno, "UNKNOWN")
        ) from None
    if facts.st_mode & _S_IFMT != _S_IFDIR:
        raise VectorRefused(
            "the descriptor this step inherited at that index is not a "
            "directory, so it is not one an *at() call may traverse"
        )
    return descriptor


def _do_openat(index: str, mode: str, component: str) -> dict:
    """`openat(dirfd, component, <reviewed flags>|O_NOFOLLOW)`, then close.

    `O_NOFOLLOW` is added to every reviewed combination here rather than left to
    the combination's own definition, because the whole value of resolving one
    component under a held descriptor is lost if that component may be a
    symbolic link to somewhere else.
    """
    dirfd = _require_directory_fd(index)
    descriptor = os.open(
        component, OPEN_FLAGS[mode] | os.O_NOFOLLOW, 0o600, dir_fd=dirfd
    )
    try:
        facts = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    return {"st_dev": facts.st_dev, "st_ino": facts.st_ino}


def _do_unlinkat(index: str, component: str) -> dict:
    """`unlinkat(dirfd, component, 0)`. **Not bindable, and this says so.**

    `unlink(2)` interprets a relative pathname relative to the directory the
    descriptor refers to: the *prefix* is bound, the final component is not. So
    this removes whatever `component` resolves to **now**, and no flag available
    here binds it to a previously observed inode. r6 §1.4.5 is the whole of what
    stands in for that: quiescence is the prevention, the pre-check is the only
    genuine detection, and the post-check is an absence check and nothing more.
    """
    dirfd = _require_directory_fd(index)
    os.unlink(component, dir_fd=dirfd)
    return {}


def _do_renameat(
    source_index: str, source: str, destination_index: str, destination: str
) -> dict:
    """`renameat(sdirfd, source, ddirfd, destination)`, both prefixes bound."""
    source_fd = _require_directory_fd(source_index)
    destination_fd = _require_directory_fd(destination_index)
    os.rename(source, destination, src_dir_fd=source_fd, dst_dir_fd=destination_fd)
    return {}


def _do_fstatat(index: str, component: str) -> dict:
    """`fstatat(dirfd, component, AT_SYMLINK_NOFOLLOW)`.

    It reports what the name resolves to **now**, or that it resolves to
    nothing. It cannot report which object a previous removal took, and nothing
    here gives it a way to — PR-20260911-R2-3.
    """
    dirfd = _require_directory_fd(index)
    try:
        facts = os.stat(component, dir_fd=dirfd, follow_symlinks=False)
    except FileNotFoundError:
        return {"resolves": 0, "st_dev": 0, "st_ino": 0}
    return {"resolves": 1, "st_dev": facts.st_dev, "st_ino": facts.st_ino}


def _do_statvfs(path: str) -> dict:
    facts = os.statvfs(path)
    return {"st_rdonly": 1 if facts.f_flag & os.ST_RDONLY else 0}


def _read_flags(descriptor: int) -> int:
    buffer = array.array("i", [0])
    fcntl.ioctl(descriptor, FS_IOC_GETFLAGS, buffer, True)
    return int(buffer[0])


def _do_getflags(path: str) -> dict:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        flags = _read_flags(descriptor)
    finally:
        os.close(descriptor)
    return {"fs_append_fl": 1 if flags & FS_APPEND_FL else 0}


def _do_clearflags(path: str) -> dict:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        flags = _read_flags(descriptor)
        fcntl.ioctl(
            descriptor,
            FS_IOC_SETFLAGS,
            array.array("i", [flags & ~FS_APPEND_FL]),
        )
        remaining = _read_flags(descriptor)
    finally:
        os.close(descriptor)
    return {"fs_append_fl": 1 if remaining & FS_APPEND_FL else 0}


def _do_getimmutable(path: str) -> dict:
    """`FS_IOC_GETFLAGS`, reporting `FS_IMMUTABLE_FL` — conflict **C-6**.

    It is what establishes each immutable-flag experiment's **initial artifact
    state**, separately, immediately before the experiment: §2.13.5c's E4 refusal
    and E6 success are claims about clearing a flag that was set, and a case run
    against an inode whose flag an earlier case already cleared asserts nothing.
    """
    descriptor = os.open(path, os.O_RDONLY)
    try:
        flags = _read_flags(descriptor)
    finally:
        os.close(descriptor)
    return {"fs_immutable_fl": 1 if flags & FS_IMMUTABLE_FL else 0}


def _do_clearimmutable(path: str) -> dict:
    """`FS_IOC_SETFLAGS` clearing `FS_IMMUTABLE_FL` and nothing else.

    The kernel makes two independent checks here and §2.13.5c is written on the
    difference between them: the caller's effective uid must equal the inode's
    owner **or** it must hold `CAP_FOWNER` (authority **A10**/**A11**), and the
    change of this particular bit additionally requires `CAP_LINUX_IMMUTABLE`
    (authority **A1**). The owner check is evaluated first, which is why `E4` —
    every discretionary right and the flag capability, and neither A10 nor A11 —
    receives **`EPERM`** rather than reaching the flag check at all.

    The mask is `flags & ~FS_IMMUTABLE_FL`, so every other attribute on the inode
    is written back unchanged; this verb cannot set a bit and cannot clear
    `FS_APPEND_FL`.
    """
    descriptor = os.open(path, os.O_RDONLY)
    try:
        flags = _read_flags(descriptor)
        fcntl.ioctl(
            descriptor,
            FS_IOC_SETFLAGS,
            array.array("i", [flags & ~FS_IMMUTABLE_FL]),
        )
        remaining = _read_flags(descriptor)
    finally:
        os.close(descriptor)
    return {"fs_immutable_fl": 1 if remaining & FS_IMMUTABLE_FL else 0}


def _directory_identity(path: str) -> dict:
    """The device and inode of the directory at `path`, opened without following.

    `O_DIRECTORY` refuses anything that is not a directory and `O_NOFOLLOW`
    refuses a symbolic link at the final component, so the identity reported is
    the identity of a real directory reached without a redirection.
    """
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        facts = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    return {"root_device": int(facts.st_dev), "root_inode": int(facts.st_ino)}


def _do_mkroot(path: str) -> dict:
    """Exclusive creation of the disposable root — conflict **C-8**.

    **This call is the ownership.** `mkdir(2)` creates the directory or fails;
    there is no preliminary absence check and no overwriting creation, so the
    window R14 found — observe absent, then create over whatever arrived — does
    not exist. `EEXIST` is returned for a directory, a file, a symbolic link and
    a dangling symbolic link alike, and it is the unique documented status no
    permitted distribution binary offers: `install -d` succeeds on a directory
    that is already there and `install` overwrites a file that is.

    Three outcomes, and only the first grants anything:

    * it returned — the directory at `path` was created by this call, and its
      device and inode are read back and reported as the evidence that ties the
      ownership to **that object** rather than to that name;
    * it was refused — `EEXIST`, `ENOENT`/`ENOTDIR` for a parent that does not
      resolve to a directory, or any other errno. No directory was created and
      nothing is owned; and
    * it returned and the identity could not be read — an
      `ObservationUnavailable`, whose distinct exit status satisfies no step. A
      directory may exist and this run cannot prove which one, so the path is
      reported as residue and never removed.

    `fchmod(2)` is applied to the descriptor of the directory this call just
    created, so the process umask cannot decide the mode and no path is resolved
    a second time to set it.
    """
    os.mkdir(path, ROOT_DIRECTORY_MODE)
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fchmod(descriptor, ROOT_DIRECTORY_MODE)
            facts = os.fstat(descriptor)
        finally:
            os.close(descriptor)
    except OSError as failure:
        # The directory was created and this process cannot say what it is. That
        # is not a refusal — a refusal would say nothing was created — so it is
        # reported through the one status that satisfies nothing.
        raise ObservationUnavailable(
            errno.errorcode.get(failure.errno, "UNKNOWN")
        ) from failure
    return {
        "created": "yes",
        "root_device": int(facts.st_dev),
        "root_inode": int(facts.st_ino),
    }


def _do_statroot(path: str) -> dict:
    """The disposable root's current device and inode — conflict **C-8**.

    It is the revalidation the cleanup plan runs immediately before the one
    `rmdir` that would remove the root: the executor compares what this reports
    with what `mkroot` reported, and a path whose object has been replaced since
    the run created it does not inherit permission to have its replacement
    deleted. It creates nothing, changes nothing and reports two numbers.
    """
    return _directory_identity(path)


# ---------------------------------------------------------------------------
# The two observation verbs
# ---------------------------------------------------------------------------

#: The `/proc/self/status` fields the identity observation reports. The five
#: capability masks and `NoNewPrivs`, and nothing else on the file's forty-odd
#: other lines.
_STATUS_FIELDS = {
    "CapInh:": "cap_inh",
    "CapPrm:": "cap_prm",
    "CapEff:": "cap_eff",
    "CapBnd:": "cap_bnd",
    "CapAmb:": "cap_amb",
    "NoNewPrivs:": "no_new_privs",
}


def _prctl_get_securebits() -> int:
    """`prctl(PR_GET_SECUREBITS)` — **the one native call in this repository.**

    ## Why it exists

    §2.13.5c's assertion contract requires every `E1 … E8` identity's **final**
    securebits to be observed inside the exec'd process, before the operation
    whose attribution depends on that identity. The kernel exposes securebits
    through `prctl(2)` and through no file: `/proc/self/status` does not report
    it, which is exactly what the package plan's assertion table says. R11 had no
    mechanism for it and therefore asserted the value from *intent* — the
    presence of a `capsh --secbits=` option in the vector — which is not evidence
    of the state after `execve`. That was Blocking finding **EH-R11-2**.

    ## Why it is allowed to use `ctypes` when nothing else is

    Python 3.12 exposes no `prctl` in `os`, so the smallest mechanism that can
    read the value at all is a foreign call. This is a **narrow exception**,
    justified solely by the already-approved `PR_GET_SECUREBITS` evidence
    contract, and it is bounded mechanically rather than by convention:

    * the library is the process's **already-loaded** C runtime, `CDLL(None)` —
      no library name is loaded, and no name comes from the vector;
    * the symbol is the literal `prctl` and no other; there is no lookup by a
      computed name, no `getattr`, and no reusable arbitrary-FFI helper for
      anything else to call;
    * `argtypes` and `restype` are fixed, so the call cannot be made with a
      different signature;
    * the operation is the literal `PR_GET_SECUREBITS` with its four remaining
      arguments zero — the vector supplies none of them, and there is no verb
      through which it could;
    * the errno is cleared before the call and read immediately after it, so a
      `-1` return carries the reason the kernel gave and not a stale one; and
    * the call **decides nothing**: it returns the raw pair, and
      `_securebits_text()` below applies the failure and range rules. That split
      is what lets the suite drive every failure branch across a fixed injected
      boundary without needing a kernel that fails on demand.

    `tests/phase_5_0_evidence/test_no_execution.py` asserts all of that against
    this file's syntax tree, and asserts that no other module in the package —
    planning tier or execution tier — imports `ctypes` or performs a native call
    at all.

    Returns `(return value, errno)`.
    """
    library = ctypes.CDLL(None, use_errno=True)
    entry = library.prctl
    entry.argtypes = (
        ctypes.c_int,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
    )
    entry.restype = ctypes.c_int
    ctypes.set_errno(0)
    value = entry(PR_GET_SECUREBITS, 0, 0, 0, 0)
    return int(value), int(ctypes.get_errno())


def _securebits_text(read=None) -> str:
    """The final securebits as bounded lower-case hexadecimal.

    Three refusals, all of them `ObservationUnavailable` and all of them naming
    at most an errno **name** from a closed table:

    1. the call returned `-1`, which is the failure convention — the errno read
       beside it is reported;
    2. the call returned something that is not an integer, or a boolean; or
    3. the value is outside `0 … SECUREBITS_MAX`, so it is not a securebits word.

    `read` exists so the suite can drive every one of those across a fixed
    injected native boundary. **No test changes this process's securebits**, and
    none could: setting them needs `CAP_SETPCAP`, no test in this repository runs
    as root, and this program contains no setter to call.
    """
    reader = _prctl_get_securebits if read is None else read
    answer = reader()
    if not isinstance(answer, tuple) or len(answer) != 2:
        raise ObservationUnavailable("none")
    value, failure = answer
    if isinstance(value, bool) or not isinstance(value, int):
        raise ObservationUnavailable("none")
    if value < 0:
        raise ObservationUnavailable(errno.errorcode.get(failure, "UNKNOWN"))
    if value > SECUREBITS_MAX:
        raise ObservationUnavailable("none")
    return format(value, "x")


def _proc_status() -> dict:
    """The six fields above, read from a literal path and nothing else.

    **Securebits is not among them, and is not missing either.** The kernel
    reports it through `prctl(PR_GET_SECUREBITS)` and through no file, so it is
    read by `_prctl_get_securebits()` above and joined to these six by
    `_do_identity()`.
    """
    found = {}
    with open("/proc/self/status", "r", encoding="ascii", errors="replace") as handle:
        for line in handle:
            for label, key in _STATUS_FIELDS.items():
                if line.startswith(label):
                    found[key] = line[len(label):].strip()
    return found


def _do_identity() -> dict:
    """The complete final identity, observed inside this process.

    The securebits is read **here**, after `capsh` applied the credential and
    capability construction and after `execve`, and before the operation whose
    attribution depends on this identity — which is a later step, because this
    verb performs no operation at all. A securebits that cannot be read raises
    `ObservationUnavailable`, and `main()` reports that through its own fixed
    exit status rather than emitting an identity with a field missing.
    """
    observations = {
        "uid": os.getuid(),
        "gid": os.getgid(),
        "groups": ",".join(str(gid) for gid in sorted(set(os.getgroups()))),
        "securebits": _securebits_text(),
    }
    observations.update(_proc_status())
    return observations


def _digest_of(path: str) -> str:
    """SHA-256 of a file named by a literal or by `sys.executable`.

    It is not reachable from a vector argument: the two callers pass
    `sys.executable` and this program's own path, and no verb takes a path this
    function is given.
    """
    digest = hashlib.sha256()
    descriptor = os.open(path, os.O_RDONLY)
    try:
        while True:
            block = os.read(descriptor, 1 << 16)
            if not block:
                break
            digest.update(block)
    finally:
        os.close(descriptor)
    return digest.hexdigest()


def _third_party_importable() -> str:
    """Whether any `site-packages`/`dist-packages` directory is on `sys.path`.

    Under `-I -S` there should be none: `-S` skips `site`, so the virtual
    environment's is never added, and `-I` removes the script directory and the
    user site directory. A `yes` here means the isolation the vector asks for did
    not take effect, which makes every dependent case inconclusive.
    """
    for entry in sys.path:
        name = str(entry)
        if "site-packages" in name or "dist-packages" in name:
            return "yes"
    return "no"


def _do_runtime(program_path: str) -> dict:
    executable = sys.executable or ""
    return {
        "interpreter": executable,
        "interpreter_real": os.path.realpath(executable) if executable else "",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "interpreter_sha256": _digest_of(executable) if executable else "",
        "isolated": "yes" if sys.flags.isolated else "no",
        "no_site": "yes" if sys.flags.no_site else "no",
        "third_party_importable": _third_party_importable(),
        "case_program": program_path,
        "case_program_sha256": _digest_of(program_path),
    }


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def _perform(verb: str, arguments: tuple[str, ...], program_path: str) -> dict:
    if verb == "open":
        return _do_open(arguments[0], arguments[1])
    if verb == "pwrite":
        return _do_pwrite(arguments[0], arguments[1])
    if verb == "append":
        return _do_append(arguments[0])
    if verb == "ftruncate":
        return _do_ftruncate(arguments[0], arguments[1])
    if verb == "rename":
        return _do_rename(arguments[0], arguments[1])
    if verb == "unlink":
        return _do_unlink(arguments[0])
    if verb == "symlink":
        return _do_symlink(arguments[0], arguments[1])
    if verb == "openat":
        return _do_openat(arguments[0], arguments[1], arguments[2])
    if verb == "unlinkat":
        return _do_unlinkat(arguments[0], arguments[1])
    if verb == "renameat":
        return _do_renameat(
            arguments[0], arguments[1], arguments[2], arguments[3]
        )
    if verb == "fstatat":
        return _do_fstatat(arguments[0], arguments[1])
    if verb == "statvfs":
        return _do_statvfs(arguments[0])
    if verb == "getflags":
        return _do_getflags(arguments[0])
    if verb == "clearflags":
        return _do_clearflags(arguments[0])
    if verb == "getimmutable":
        return _do_getimmutable(arguments[0])
    if verb == "clearimmutable":
        return _do_clearimmutable(arguments[0])
    if verb == "mkroot":
        return _do_mkroot(arguments[0])
    if verb == "statroot":
        return _do_statroot(arguments[0])
    if verb == "identity":
        return _do_identity()
    return _do_runtime(program_path)


def _emit(observations: dict, stream) -> None:
    """`key=value` lines, in a fixed order, ASCII only.

    Sorted so two runs of the same verb produce the same line order, and filtered
    so a value that somehow acquired a newline or a non-ASCII byte is reported as
    `unreadable` rather than written through.
    """
    for key in sorted(observations):
        value = str(observations[key])
        if not value.isascii() or any(character in value for character in "\r\n"):
            value = "unreadable"
        stream.write(f"{key}={value}\n")


def main(
    arguments: list[str],
    *,
    program_path: str,
    isolated: bool,
    no_site: bool,
    stream=None,
) -> int:
    """One operation, or a refusal. Never more than one operation."""
    output = sys.stdout if stream is None else stream
    try:
        if not isolated or not no_site:
            raise VectorRefused(
                "isolated mode and no-site must both be in effect; the reviewed "
                "vector passes -I and -S"
            )
        if program_path not in (CASE_PROGRAM_PATH, BOOTSTRAP_PROGRAM_PATH):
            raise VectorRefused("this is not one of the two reviewed program paths")
        if not arguments:
            raise VectorRefused("no verb was given")
        verb = arguments[0]
        # **Conflict C-8's partition, enforced here as well as by the planner.**
        # The bootstrap copy exists to create the root the installed copy lives
        # in, and that is the whole of what it may do; the installed copy may not
        # create the root it lives in. Neither half can stand in for the other.
        bootstrap = program_path == BOOTSTRAP_PROGRAM_PATH
        if bootstrap and verb not in BOOTSTRAP_VERBS:
            raise VectorRefused(
                "the bootstrap copy runs only the disposable root's creation and "
                "its identity reading"
            )
        if not bootstrap and verb in BOOTSTRAP_VERBS:
            raise VectorRefused(
                "the installed copy does not create or re-identify the disposable "
                "root it lives inside"
            )
        checked = validate_arguments(verb, list(arguments[1:]))
    except VectorRefused as refusal:
        _emit({"result": "vector-refused", "reason": str(refusal)}, output)
        return EXIT_VECTOR_REFUSED

    try:
        observations = _perform(verb, checked, program_path)
    except ObservationUnavailable as unavailable:
        # A reviewed observation could not be made. Nothing is reported as a
        # result, and the distinct exit status means no step's
        # `satisfying_statuses` can be met by it.
        _emit(
            {
                "verb": verb,
                "result": "unobserved",
                "errno": unavailable.errno_name,
            },
            output,
        )
        return EXIT_OBSERVATION_UNAVAILABLE
    except OSError as failure:
        _emit(
            {
                "verb": verb,
                "result": "refused",
                "errno": errno.errorcode.get(failure.errno, "UNKNOWN"),
            },
            output,
        )
        return REFUSAL_EXIT_CODES.get(failure.errno, EXIT_REFUSED)
    except Exception:  # pragma: no cover - defensive; nothing below raises
        _emit({"verb": verb, "result": "internal-failure"}, output)
        return EXIT_INTERNAL

    observations["verb"] = verb
    observations["result"] = "returned"
    observations["errno"] = "none"
    _emit(observations, output)
    return EXIT_RETURNED


if __name__ == "__main__":  # pragma: no cover - the entry point itself
    raise SystemExit(
        main(
            sys.argv[1:],
            program_path=sys.argv[0],
            isolated=bool(sys.flags.isolated),
            no_site=bool(sys.flags.no_site),
        )
    )
