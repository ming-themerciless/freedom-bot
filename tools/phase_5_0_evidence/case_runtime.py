"""Conflict **C-2**, resolved as Option B: an **explicitly named interpreter** in
every case-program vector, and a closed grammar for what may follow it.

## The ruling this module implements

Peter Duscha accepted Codex's recommendation on 2026-09-06 (package plan §2.12.2,
change-log **C-P5.0-AH**): R10 returned C-2 as a runtime decision between four
shapes, and **Option B is the ruled one**. The reviewed vector names the
interpreter itself, so *the reviewed vector is the vector that runs* — there is no
shebang, no indirection, and no file whose executed program the plan does not
name. The case program's installed bytes are its reviewed source bytes, so its
digest pins in the review manifest, which is the property R10 showed a compiled
program cannot have.

Option B's stated cost was that *"a general-purpose interpreter joins
`PERMITTED_EXECUTABLES`"*. **It does not.** `plan.PERMITTED_EXECUTABLES` is
unchanged, and the interpreter is admitted only through `validate_case_vector()`
below, which accepts one absolute interpreter path, exactly two isolation flags in
one order, one case-program path strictly inside the validated disposable root,
one verb from a closed vocabulary, and that verb's exact arity and argument kinds.
An arbitrary Python command is not expressible: there is no `-c`, no `-m`, no
interactive form, no second script path and no trailing argument.

## The five things the grammar admits, and nothing else

```text
<interpreter> -I -S <root>/bin/case <verb> [<argument> …]
```

* **`<interpreter>`** — `INTERPRETER_PATH`, the one absolute path
  `docs/operations/disposable-test-server.md` documents for `oracle-test`, and no
  other. A relative name, a second interpreter, a wrapper or `env` is refused.
* **`-I -S`** — `INTERPRETER_FLAGS`, in that order and complete. `-I` is
  CPython's isolated mode: it implies `-E` and `-s`, and it removes the script's
  own directory from `sys.path`, so nothing beside the installed program can be
  imported. `-S` additionally skips `site`, so the virtual environment's
  `site-packages` is not on the path at all. **Omitting either, adding a third
  flag, or reordering the two is refused** — by this validator before process
  creation, and again by the case program, which reads `sys.flags` and refuses
  when isolated mode is not actually in effect.
* **`<root>/bin/case`** — `case_program_path(target)`, validated through
  `DisposableTarget.contained_path()`, so it is strictly inside the confirmed
  disposable root. An arbitrary script path is refused.
* **`<verb>`** — one key of `CASE_VERBS`. Unknown verbs are refused.
* **the verb's arguments** — exactly the arity its `VerbSpec` states, each of the
  declared kind. A path argument goes through `contained_path()` too, so a target
  outside the disposable root cannot be named. Trailing arguments are refused.

## The one other program path, and why it exists — conflict **C-8**

```text
<interpreter> -I -S <repository>/…/execution/case_program.py mkroot <root>
```

The third element may **also** be `CASE_PROGRAM_SOURCE_PATH`, the reviewed source
in the repository tree on the disposable host — and then, and only then, the verb
must be one of `BOOTSTRAP_VERBS`. The reason is a dependency rather than a
convenience: **a helper that creates the disposable root cannot first be
installed inside that root**, and every other way of getting one there creates a
host object whose own pre-existence nobody proved.

The repository source is the way out that creates nothing. The run does not
write it, modify it or remove it; it is the same file the review manifest already
pins and the same bytes `install` later copies to `<root>/bin/case`, so one
digest covers both copies. The partition between them is total and enforced
twice: the bootstrap copy runs `mkroot` and `statroot` and nothing else, and the
installed copy runs everything else and neither of those.

## The two reviewed interpreter facts, and what the digest covers

`EXPECTED_INTERPRETER_SHA256` and `EXPECTED_INTERPRETER_REAL_PATH` are both
**reviewed target facts**, in the same sense as
`approved_target.APPROVED_TARGET_FACTS`' kernel, filesystem device and PostgreSQL
instance: values the Operations Owner states and the independent reviewer
verifies on the host, not values this harness learns from the run it is judging.
Both are `UNCONFIRMED` here because establishing either requires reading
`oracle-test`, which no authorization in force grants — see the R11 and R12
handbacks. While either is unconfirmed the executor refuses before it starts
anything; the plan is still fully specified, because a plan whose preflight
cannot pass is a different thing from a plan that cannot be written.

The resolved path is a **separate** fact rather than a derivation, because R12
requires every key of `P-05`'s observation to be compared with an expectation the
observation cannot supply, and `interpreter_real` has no other honest source: a
virtual environment's `bin/python` normally resolves outside the environment, so
neither *"equal to `INTERPRETER_PATH`"* nor *"inside the environment"* is a rule
the reviewed host would satisfy.

The digest covers **the interpreter executable's own bytes and nothing else**. It
does not cover the operating system, the dynamic loader, `libc`, `libpython`, any
other shared library, or the Python standard library on disk. Those are
**disposable-host prerequisites**, exactly as they already are for `capsh`,
`chattr`, `install`, `psql`, `systemd-run` and every other distribution
executable the harness names — none of which is hashed either. Claiming the
interpreter digest covers the runtime would be claiming more for this one
executable than the harness claims for any other, and it would be false.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .errors import PlanRefused, TargetRefused
from .targets import REPOSITORY_ROOT, DisposableTarget

# ---------------------------------------------------------------------------
# The runtime, named once
# ---------------------------------------------------------------------------

#: The Python 3.12 interpreter `docs/operations/disposable-test-server.md`
#: documents for `oracle-test`. One absolute path, stated here and nowhere else.
INTERPRETER_PATH = "/opt/freedom-blades/runtime/venv-web/bin/python"

#: The isolation flags, in the order they must appear. `-I` implies `-E` and
#: `-s` and removes the script directory from `sys.path`; `-S` skips `site`, so
#: the virtual environment's `site-packages` never joins it. Together they are
#: what makes *"imports no third-party distribution"* a property of the vector
#: rather than a hope about the host.
INTERPRETER_FLAGS = ("-I", "-S")

#: The major/minor version preflight requires. Recorded as text because that is
#: how the case program reports it and how the manifest pins it.
INTERPRETER_PYTHON_VERSION = "3.12"

#: The sentinel `EXPECTED_INTERPRETER_SHA256` carries until a maintainer states
#: the fact and the independent reviewer verifies it on the disposable host.
INTERPRETER_DIGEST_UNCONFIRMED = "UNCONFIRMED"

#: The interpreter executable's expected SHA-256 — **a reviewed target fact**.
#: Establishing it requires reading `oracle-test`, which this work is not
#: authorized to do, so it is unconfirmed and the executor refuses while it is.
#: Supplying it changes a covered source, which changes the review-manifest
#: digest, which is exactly the re-review the substitution should trigger.
EXPECTED_INTERPRETER_SHA256 = INTERPRETER_DIGEST_UNCONFIRMED

#: The sentinel `EXPECTED_INTERPRETER_REAL_PATH` carries until the fact is
#: stated and verified, for the same reason and by the same authority.
INTERPRETER_REAL_PATH_UNCONFIRMED = "UNCONFIRMED"

#: The path `INTERPRETER_PATH` resolves to — **a second reviewed target fact**,
#: new in R12.
#:
#: `P-05` reports `interpreter_real` as well as `interpreter`, and R12 requires
#: every value in that observation to be compared with a reviewed expectation.
#: The two are **not** the same fact: `INTERPRETER_PATH` names a virtual
#: environment's `bin/python`, which on a normal CPython venv is a symbolic link
#: to an interpreter outside the environment, so a rule requiring the two to be
#: equal would refuse the reviewed host and a rule deriving the expectation from
#: the observation would be the tautology `P-05` exists to avoid.
#:
#: So the resolved path is stated from outside, exactly as the digest is:
#: establishing it requires reading `oracle-test`, which this work is not
#: authorized to do. It is unconfirmed, and the executor refuses while it is.
EXPECTED_INTERPRETER_REAL_PATH = INTERPRETER_REAL_PATH_UNCONFIRMED

#: The largest value `prctl(PR_GET_SECUREBITS)` can legitimately return: eight
#: defined bits, 0 … 7. The planning tier's copy of
#: `execution/case_program.py`'s `SECUREBITS_MAX`, mirrored here so the shape a
#: capture policy admits and the range the program enforces cannot drift;
#: `tests/phase_5_0_evidence/test_case_program.py` asserts they agree.
SECUREBITS_MAX = 0xFF

#: The reviewed source, relative to the repository root. It is **installed
#: byte-for-byte**: the generated `install` vector copies this exact file to
#: `<root>/bin/case`, so the manifest's digest for this path is simultaneously
#: the source digest and the installation digest. There is no build step, no
#: generated code and no downloaded binary between the two.
CASE_PROGRAM_SOURCE = "tools/phase_5_0_evidence/execution/case_program.py"

#: The same file as an absolute path on the disposable host, which is where the
#: `install` vector names it. `oracle-test`'s repository path is the one
#: `docs/operations/disposable-test-server.md` records.
CASE_PROGRAM_SOURCE_PATH = f"{REPOSITORY_ROOT}/{CASE_PROGRAM_SOURCE}"

#: Where the installed program lives, relative to the disposable root.
CASE_PROGRAM_RELATIVE_PATH = "bin/case"

#: The mode, owner and group `P-04` asserts. Stated here so the install vector
#: and the assertion cannot disagree.
CASE_PROGRAM_MODE = "0755"
CASE_PROGRAM_OWNER = "root"
CASE_PROGRAM_GROUP = "root"


def interpreter_real_path_confirmed() -> bool:
    """Whether the expected resolved interpreter path is a stated reviewed fact.

    An absolute path of the narrow shape `capture`'s `absolute_path` admits is
    confirmed; the sentinel is not. The executor consults this beside the digest,
    so an unconfirmed fact is a refusal to run rather than a preflight key that
    quietly compares against a value nothing can equal.
    """
    value = EXPECTED_INTERPRETER_REAL_PATH
    return (
        isinstance(value, str)
        and value.startswith("/")
        and 2 <= len(value) <= 111
        and ".." not in value.split("/")
        and all(
            character in _REAL_PATH_CHARACTERS for character in value
        )
    )


#: The character class `capture`'s `absolute_path` shape admits, so a reviewed
#: resolved path that the capture boundary could never report is refused here
#: rather than compared against forever.
_REAL_PATH_CHARACTERS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "._-/"
)


def interpreter_digest_confirmed() -> bool:
    """Whether the expected interpreter digest is a stated reviewed fact.

    A 64-character lower-case hexadecimal value is confirmed; the sentinel is
    not. The executor consults this before it starts anything, so an unconfirmed
    fact is a refusal to run rather than a preflight that quietly compares
    nothing.
    """
    value = EXPECTED_INTERPRETER_SHA256
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


# ---------------------------------------------------------------------------
# The closed verb vocabulary
# ---------------------------------------------------------------------------


class ArgumentKind(str, Enum):
    """What one verb argument is allowed to be. Four kinds, and no free text."""

    #: An absolute path strictly inside the validated disposable root.
    TARGET_PATH = "target_path"
    #: One member of `OPEN_MODES` — an exact `open(2)` flag combination.
    OPEN_MODE = "open_mode"
    #: One member of `WRITE_MODES`.
    WRITE_MODE = "write_mode"
    #: The one reviewed relative generation name a symlink may point at.
    LINK_NAME = "link_name"
    #: **Conflict C-8.** The disposable root itself, and no other string. It is
    #: the one path that is not *strictly inside* the root, so it cannot be a
    #: `TARGET_PATH`; and it admits exactly one value, so it is a constant the
    #: vector states rather than a path a caller chooses.
    ROOT_PATH = "root_path"


#: Every `open(2)` flag combination the package-plan cases name, and no other.
#: The names are the vector's; the flags themselves live in the case program, so
#: a combination that is not in this table cannot be requested.
OPEN_MODES = (
    "rdonly",
    "wronly",
    "wronly-trunc",
    "wronly-append",
    "wronly-append-trunc",
    "create-excl",
)

#: The two modes a write-bearing verb may open with.
WRITE_MODES = ("wronly", "wronly-append")

#: §2.13.3's `…/journal/current` points at the current generation, and this run
#: creates exactly one. The link target is this **relative name** — never an
#: absolute path, never a separator, never `..` — so the link cannot be made to
#: reach outside the directory it lives in.
GENERATION_LINK_NAME = "000001.journal"


@dataclass(frozen=True, slots=True)
class VerbSpec:
    """One verb, its exact arity and the kind of each argument."""

    name: str
    arguments: tuple[ArgumentKind, ...]
    purpose: str

    @property
    def arity(self) -> int:
        return len(self.arguments)


def _verb(name: str, arguments: Sequence[ArgumentKind], purpose: str) -> VerbSpec:
    return VerbSpec(name=name, arguments=tuple(arguments), purpose=purpose)


#: The complete operation vocabulary. Every entry is an operation the package
#: plan's own cases already require — §2.13.2a's four stages, §5.2's eight
#: `JNL-52` cases, §2.13.3's `current` link and §2.13.5c's identity assertion —
#: and there is no entry that is not.
CASE_VERBS: Mapping[str, VerbSpec] = {
    spec.name: spec
    for spec in (
        _verb(
            "open",
            (ArgumentKind.OPEN_MODE, ArgumentKind.TARGET_PATH),
            "open(2) with one of the reviewed flag combinations, then close. The "
            "evidence is whether it returned and, when it did not, the exact errno.",
        ),
        _verb(
            "pwrite",
            (ArgumentKind.WRITE_MODE, ArgumentKind.TARGET_PATH),
            "open, pwrite the reviewed byte block at offset 0, and report the "
            "file's size before and after — which is how P-7 asserts that "
            "O_APPEND made the bytes land at EOF rather than at the offset.",
        ),
        _verb(
            "append",
            (ArgumentKind.TARGET_PATH,),
            "open(O_WRONLY|O_APPEND), write the reviewed byte block, fsync, and "
            "report the size before and after.",
        ),
        _verb(
            "ftruncate",
            (ArgumentKind.WRITE_MODE, ArgumentKind.TARGET_PATH),
            "open, then ftruncate(fd, 0).",
        ),
        _verb(
            "rename",
            (ArgumentKind.TARGET_PATH, ArgumentKind.TARGET_PATH),
            "rename(2) between two paths, both strictly inside the disposable root.",
        ),
        _verb(
            "unlink",
            (ArgumentKind.TARGET_PATH,),
            "unlink(2).",
        ),
        _verb(
            "symlink",
            (ArgumentKind.TARGET_PATH, ArgumentKind.LINK_NAME),
            "symlink(2) creating §2.13.3's `…/journal/current`. The link path is "
            "absolute and inside the root; the target is the one reviewed "
            "relative generation name.",
        ),
        _verb(
            "statvfs",
            (ArgumentKind.TARGET_PATH,),
            "statvfs(3) reporting whether ST_RDONLY is set — Stage 3's M-2.",
        ),
        _verb(
            "getflags",
            (ArgumentKind.TARGET_PATH,),
            "FS_IOC_GETFLAGS, reporting whether FS_APPEND_FL is present.",
        ),
        _verb(
            "clearflags",
            (ArgumentKind.TARGET_PATH,),
            "FS_IOC_SETFLAGS clearing FS_APPEND_FL — Stage 2's P-8, which must be "
            "refused with FS_APPEND_FL still reported afterwards.",
        ),
        _verb(
            "getimmutable",
            (ArgumentKind.TARGET_PATH,),
            "FS_IOC_GETFLAGS, reporting whether FS_IMMUTABLE_FL is present. It "
            "establishes each C-6 experiment's initial artifact state separately, "
            "immediately before that experiment, so a clear that already "
            "succeeded cannot make a later case meaningless.",
        ),
        _verb(
            "clearimmutable",
            (ArgumentKind.TARGET_PATH,),
            "FS_IOC_SETFLAGS clearing FS_IMMUTABLE_FL and no other bit — "
            "conflict C-6. It is E4's refusal (EPERM, for want of A10/A11), E6's "
            "positive control and the first half of E5's two-step case.",
        ),
        _verb(
            "mkroot",
            (ArgumentKind.ROOT_PATH,),
            "mkdir(2) creating the disposable root exclusively, then fchmod(2) "
            "and fstat(2) on the descriptor of the directory just created — "
            "conflict C-8. Exit 0 *is* the ownership; EEXIST is the unique, "
            "documented pre-existence status; and the reported device and inode "
            "tie that ownership to the created object rather than to its name. "
            "Bootstrap-only.",
        ),
        _verb(
            "statroot",
            (ArgumentKind.ROOT_PATH,),
            "The disposable root's current device and inode, opened with "
            "O_DIRECTORY|O_NOFOLLOW. It is the revalidation cleanup makes "
            "immediately before the one rmdir that would remove the root. "
            "Bootstrap-only.",
        ),
        _verb(
            "identity",
            (),
            "The bounded identity and status observation §2.13.5c's E1 … E8 are "
            "classified from: uid, gid, the supplementary gids, the five "
            "capability masks, the securebits and no_new_privs.",
        ),
        _verb(
            "runtime",
            (),
            "The interpreter preflight: the interpreter's absolute path, its "
            "resolved path, its major/minor version, the SHA-256 of its "
            "executable bytes, whether isolated mode and no-site are actually in "
            "effect, and whether any third-party distribution is importable.",
        ),
    )
}

#: The case program's exit status when the operation returned.
EXIT_RETURNED = 0
#: Its exit status for a refusal whose errno the reviewed cases do not name.
EXIT_REFUSED = 1
#: Its exit status when **it** refused the vector — a distinct code, so a step
#: satisfied by "the kernel denied this" can never be satisfied by "the vector
#: was wrong" instead.
EXIT_VECTOR_REFUSED = 64
#: Its exit status on an internal failure.
EXIT_INTERNAL = 65
#: Its exit status when a **reviewed observation** could not be made — today,
#: `prctl(PR_GET_SECUREBITS)` failing or returning something that is not a
#: securebits word. Distinct from every refusal code, and in no step's
#: `satisfying_statuses`, so an identity that could not be observed can never be
#: recorded as an identity that was.
EXIT_OBSERVATION_UNAVAILABLE = 66

#: errno name → exit status, mirroring `execution/case_program.py`'s table by
#: **name** rather than by number, because the planning tier states the errno a
#: case expects and the program states the number the host uses for it.
#: `tests/phase_5_0_evidence/test_case_program.py` asserts the two agree.
#:
#: This is what lets a step declare *"satisfied by exit 12, which is EROFS"* in
#: `satisfying_statuses` — reviewed in advance — rather than *"satisfied by any
#: non-zero exit"*, which is all `refusal_required` can say and which a vector
#: refusal would also satisfy.
REFUSAL_EXIT_CODES: Mapping[str, int] = {
    "EPERM": 10,
    "EACCES": 11,
    "EROFS": 12,
    "ENOTTY": 13,
    "EOPNOTSUPP": 14,
    "EEXIST": 15,
    "ENOENT": 16,
}


def refused_with(*errno_names: str) -> tuple[int, ...]:
    """The satisfying exit statuses for a step whose case expects a refusal.

    Takes names rather than numbers so a generated step reads as the case does —
    `refused_with("EROFS")` — and so a name the table does not carry is a
    `PlanRefused` at generation time rather than an exit status nobody assigned.
    """
    statuses: list[int] = []
    for name in errno_names:
        if name not in REFUSAL_EXIT_CODES:
            raise PlanRefused(
                f"{name!r} is not one of the refusals the case program reports "
                f"with its own exit status: {sorted(REFUSAL_EXIT_CODES)}."
            )
        statuses.append(REFUSAL_EXIT_CODES[name])
    if not statuses:
        raise PlanRefused(
            "A step expecting a refusal names at least one errno. 'Any non-zero "
            "exit' would also be satisfied by the case program refusing the "
            "vector, which is not the boundary under test."
        )
    return tuple(sorted(set(statuses)))


#: The verbs that make no filesystem change and take no path. They are the two
#: observation verbs, and they are named so a reviewer can see at a glance which
#: entries of the table can alter anything.
OBSERVATION_VERBS = frozenset({"identity", "runtime"})

#: **Conflict C-8.** The verbs the **bootstrap** copy runs, and the installed
#: copy may not. The partition is total in both directions: `validate_case_vector`
#: refuses a bootstrap verb behind the installed path and every other verb behind
#: the bootstrap path, and `execution/case_program.py` refuses the same pair from
#: its own constants.
#:
#: The bootstrap copy exists for one reason: **a helper required to create the
#: disposable root cannot first be installed inside that root.** The reviewed
#: source in the repository tree is the way out that adds no host object — the
#: run does not create it, does not modify it, does not remove it, and needs no
#: absence baseline for it, because its lifecycle is the repository's. `install`
#: copies those same bytes to `<root>/bin/case` afterwards, so the manifest's one
#: digest for `CASE_PROGRAM_SOURCE` covers both copies.
BOOTSTRAP_VERBS = frozenset({"mkroot", "statroot"})

#: The exit status `mkroot` reports for a path that is already occupied.
#: `mkdir(2)` gives `EEXIST` for a directory, a file, a symbolic link and a
#: dangling symbolic link alike — the unique, documented pre-existence status
#: that no permitted distribution binary offers, and the whole reason conflict
#: C-8 is resolvable by a creation rather than by a probe.
ROOT_PREEXISTING_STATUS = 15

#: The statuses in which `mkroot` **created nothing**: `os.mkdir` either was not
#: reached (the vector was refused) or returned an error. Every other unsatisfied
#: outcome — an internal failure, an unreadable identity, a timeout, a launch
#: that never reported — leaves a directory that may exist and that this run
#: cannot identify, which is bounded residue rather than a clean absence.
ROOT_NOTHING_CREATED_STATUSES = (
    EXIT_REFUSED,
    *sorted(set(REFUSAL_EXIT_CODES.values())),
    EXIT_VECTOR_REFUSED,
)


# ---------------------------------------------------------------------------
# The dedicated validator
# ---------------------------------------------------------------------------


def case_program_path(target: DisposableTarget) -> str:
    """`<root>/bin/case`, validated as strictly inside the disposable root."""
    return target.contained_path(f"{target.root_path}/{CASE_PROGRAM_RELATIVE_PATH}")


def validate_case_vector(
    vector: Sequence[str], *, target: DisposableTarget
) -> tuple[str, ...]:
    """The whole of what makes the interpreter admissible. Returns the vector.

    This is the **only** route by which `INTERPRETER_PATH` may appear in a
    planned or executed argument vector. It is deliberately not a check that the
    vector *contains* the right things: it is a positional match against a fixed
    shape, so anything the shape does not describe — an extra flag, a second
    script, a trailing argument, a reordered prefix — is refused by the same
    comparison that accepts the reviewed form.
    """
    if isinstance(vector, (str, bytes)) or not isinstance(vector, Sequence):
        raise PlanRefused("A case-program vector is a sequence of separate arguments.")
    argv = tuple(vector)
    for argument in argv:
        if not isinstance(argument, str) or not argument:
            raise PlanRefused(
                "Every element of a case-program vector is non-empty text."
            )

    prefix_length = 1 + len(INTERPRETER_FLAGS) + 1
    if len(argv) < prefix_length + 1:
        raise PlanRefused(
            f"A case-program vector is {prefix_length} fixed elements — the "
            "interpreter, its isolation flags and the program — followed by a "
            f"verb; {list(argv)} is shorter than that."
        )
    if argv[0] != INTERPRETER_PATH:
        raise PlanRefused(
            f"{argv[0]!r} is not the approved interpreter. Exactly one absolute "
            f"interpreter path is admissible, {INTERPRETER_PATH!r}, and it is "
            "admitted only in this position and only by this validator — it is "
            "not a member of the general command surface."
        )
    flags = argv[1 : 1 + len(INTERPRETER_FLAGS)]
    if flags != INTERPRETER_FLAGS:
        raise PlanRefused(
            f"The interpreter flags are {list(flags)} and the reviewed vector's "
            f"are {list(INTERPRETER_FLAGS)}, in that order. An omitted isolation "
            "flag, an additional flag, a reordered pair, `-c`, `-m` and an "
            "interactive form are each refused: they change which code the "
            "interpreter runs, which is the whole of what the vector says."
        )

    try:
        expected_program = case_program_path(target)
    except TargetRefused as exc:
        raise PlanRefused(
            f"The case program's path is not admissible for this target: {exc}"
        ) from exc
    program = argv[1 + len(INTERPRETER_FLAGS)]
    if program not in (expected_program, CASE_PROGRAM_SOURCE_PATH):
        raise PlanRefused(
            f"{program!r} is not one of the two reviewed case-program paths. The "
            f"vector runs {expected_program!r} — strictly inside the validated "
            f"disposable root — or, for conflict C-8's bootstrap, "
            f"{CASE_PROGRAM_SOURCE_PATH!r}, the reviewed source the manifest "
            "pins. An arbitrary script path is refused."
        )

    verb = argv[prefix_length]
    spec = CASE_VERBS.get(verb)
    if spec is None:
        raise PlanRefused(
            f"{verb!r} is not one of the case program's operations. The "
            f"vocabulary is closed: {sorted(CASE_VERBS)}."
        )
    # **Conflict C-8's partition.** Which copy runs decides which half of the
    # table it may run, in both directions and with no overlap.
    bootstrap = program == CASE_PROGRAM_SOURCE_PATH
    if bootstrap and verb not in BOOTSTRAP_VERBS:
        raise PlanRefused(
            f"The bootstrap copy at {CASE_PROGRAM_SOURCE_PATH!r} runs only "
            f"{sorted(BOOTSTRAP_VERBS)}. It exists because a helper that creates "
            "the disposable root cannot first be installed inside it, and that is "
            "the whole of what it is for: an experiment run from the repository "
            "tree would be an experiment the installed, digest-asserted program "
            "did not perform."
        )
    if not bootstrap and verb in BOOTSTRAP_VERBS:
        raise PlanRefused(
            f"{verb!r} is a bootstrap verb and this vector runs the installed "
            "copy. The program inside the disposable root does not create or "
            "re-identify the root it lives in — the object it would be asked "
            "about is the one whose existence it depends on."
        )
    arguments = argv[prefix_length + 1 :]
    if len(arguments) != spec.arity:
        raise PlanRefused(
            f"Verb {verb!r} takes exactly {spec.arity} argument(s) and was given "
            f"{len(arguments)}. A trailing argument is refused rather than "
            "ignored, because an ignored argument is one nobody reviewed."
        )
    for index, (kind, argument) in enumerate(zip(spec.arguments, arguments)):
        _validate_argument(verb, index, kind, argument, target=target)
    return argv


def _validate_argument(
    verb: str,
    index: int,
    kind: ArgumentKind,
    argument: str,
    *,
    target: DisposableTarget,
) -> None:
    """One argument, against the kind its position declares."""
    if kind is ArgumentKind.TARGET_PATH:
        try:
            resolved = target.contained_path(argument)
        except TargetRefused as exc:
            raise PlanRefused(
                f"Verb {verb!r} argument {index} names {argument!r}, which is not "
                f"strictly inside the disposable root: {exc}"
            ) from exc
        if resolved != argument:
            raise PlanRefused(
                f"Verb {verb!r} argument {index} is {argument!r}, which is not "
                "already normalized. What a reviewer approved is what runs."
            )
        return
    if kind is ArgumentKind.ROOT_PATH:
        if argument != target.root_path:
            raise PlanRefused(
                f"Verb {verb!r} argument {index} is {argument!r}; the one "
                f"admissible value is the disposable root itself, "
                f"{target.root_path!r}. This kind admits one string and no path "
                "a caller composes."
            )
        return
    if kind is ArgumentKind.OPEN_MODE:
        if argument not in OPEN_MODES:
            raise PlanRefused(
                f"Verb {verb!r} argument {index} is {argument!r}; the reviewed "
                f"open flag combinations are {list(OPEN_MODES)}."
            )
        return
    if kind is ArgumentKind.WRITE_MODE:
        if argument not in WRITE_MODES:
            raise PlanRefused(
                f"Verb {verb!r} argument {index} is {argument!r}; the reviewed "
                f"write modes are {list(WRITE_MODES)}."
            )
        return
    if argument != GENERATION_LINK_NAME:
        raise PlanRefused(
            f"Verb {verb!r} argument {index} is {argument!r}; the one reviewed "
            f"link target is the relative name {GENERATION_LINK_NAME!r}. An "
            "absolute target, a `..` segment, a separator and any other "
            "generation name are refused."
        )


def build_case_vector(
    target: DisposableTarget, verb: str, *arguments: str
) -> tuple[str, ...]:
    """The Option-B vector for one operation, built and then validated.

    Built here rather than at each call site so that no generated step can spell
    the prefix differently, and validated by the same function the planner and
    the executor use, so a vector this returns is a vector both of them accept.
    """
    vector = (
        INTERPRETER_PATH,
        *INTERPRETER_FLAGS,
        case_program_path(target),
        verb,
        *arguments,
    )
    return validate_case_vector(vector, target=target)


def build_bootstrap_vector(
    target: DisposableTarget, verb: str, *arguments: str
) -> tuple[str, ...]:
    """Conflict **C-8**'s bootstrap vector, built and then validated.

    The same interpreter, the same isolation flags and the same reviewed bytes —
    executed from the repository source rather than from the copy inside a root
    that does not exist yet. It goes through `validate_case_vector`, which is
    what confines it to `BOOTSTRAP_VERBS` and confines those to the root itself.
    """
    vector = (
        INTERPRETER_PATH,
        *INTERPRETER_FLAGS,
        CASE_PROGRAM_SOURCE_PATH,
        verb,
        *arguments,
    )
    return validate_case_vector(vector, target=target)


__all__ = [
    "ArgumentKind",
    "BOOTSTRAP_VERBS",
    "CASE_PROGRAM_GROUP",
    "CASE_PROGRAM_MODE",
    "CASE_PROGRAM_OWNER",
    "CASE_PROGRAM_RELATIVE_PATH",
    "CASE_PROGRAM_SOURCE",
    "CASE_PROGRAM_SOURCE_PATH",
    "CASE_VERBS",
    "EXIT_INTERNAL",
    "EXIT_REFUSED",
    "EXIT_RETURNED",
    "EXIT_VECTOR_REFUSED",
    "EXIT_OBSERVATION_UNAVAILABLE",
    "EXPECTED_INTERPRETER_REAL_PATH",
    "EXPECTED_INTERPRETER_SHA256",
    "GENERATION_LINK_NAME",
    "INTERPRETER_DIGEST_UNCONFIRMED",
    "INTERPRETER_REAL_PATH_UNCONFIRMED",
    "INTERPRETER_FLAGS",
    "INTERPRETER_PATH",
    "INTERPRETER_PYTHON_VERSION",
    "OBSERVATION_VERBS",
    "OPEN_MODES",
    "REFUSAL_EXIT_CODES",
    "ROOT_NOTHING_CREATED_STATUSES",
    "ROOT_PREEXISTING_STATUS",
    "SECUREBITS_MAX",
    "VerbSpec",
    "WRITE_MODES",
    "build_bootstrap_vector",
    "build_case_vector",
    "case_program_path",
    "interpreter_digest_confirmed",
    "interpreter_real_path_confirmed",
    "refused_with",
    "validate_case_vector",
]
