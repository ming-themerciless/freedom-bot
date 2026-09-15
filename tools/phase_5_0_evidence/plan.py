"""Command planning as **argument vectors**, mutation declaration, and the only
runner this package ships — the one that runs nothing.

## Why a vector and not a string

Every privileged step in the authorized bands is modelled as `CommandStep.argv`:
a tuple whose first element is an absolute executable path and whose remaining
elements are literal arguments. There is no quoting question, no word splitting,
no glob expansion and no variable substitution, so what a reviewer reads in
`docs/review/phase-5-0-evidence-harness-execution-plan.md` is exactly what would
be passed to `execve`. The implementation prompt asks for this directly: *"Do not
use shell-string construction for privileged commands where an argument-vector
representation can be emitted and reviewed."*

The corollary is enforced rather than intended: an argument containing a shell
metacharacter, a glob or an unresolved variable is refused, because in a vector
it would be silently literal and in a string it would be silently not.

## Why a mutation is declared before it is planned

A `CommandStep` that would change host state carries the ids of the `Mutation`
rows it performs, and `ExecutionPlan` refuses to hold a step whose mutations it
does not declare. That is the implementation prompt's *"refuse to run
mutation-bearing cases unless a generated plan names the disposable target and
every intended mutation"*, made structural: the declaration is the plan's, the
performance is the step's, and the two are compared before anything is written
out. It is also what makes cleanup derivable — `cleanup.py` reads the declared
mutations, not the steps, so a mutation nobody declared has no cleanup and the
plan refuses before that can happen.

## The runner

`Runner` is a protocol with one implementation, `DryRunRunner`, which records the
argument vector it was given and executes nothing. **No module in this package
imports `subprocess`, `os.system`, `os.exec*`, `os.popen`, `socket`, `http`,
`urllib`, `ssl` or a database driver**, and `tests/phase_5_0_evidence/
test_no_execution.py` asserts that by reading the source of every module.

Adding an executing runner is a separate, separately reviewed change that may be
made only after Codex's pre-execution approval of the named target, the exact
commands and the cleanup.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Protocol, Sequence

from .binding import BindingSite, validate_sites
from .capture import CapturePolicy, CatalogQuestion
from .expectations import (
    DERIVED_CONTRACT_POLICIES,
    DeclaredExpectation,
    declared_contract,
)
from .case_runtime import INTERPRETER_PATH, validate_case_vector
from .errors import PlanRefused
from .materialization import MaterializedFile
from .targets import (
    DisposableTarget,
    validate_absolute_path,
    validate_account_name,
    validate_database_name,
)

#: Executables a step may name. Every one is a distribution binary already
#: present on this host (§8.1 and the preflight), so the harness installs
#: nothing, and the list is closed so that a step naming an unexpected program is
#: a refusal rather than a line a reviewer has to notice.
#:
#: `sudo` and `su` are **deliberately absent**. How the executor comes to be root
#: is the operations document's business and the `sudoers` drop-ins' business; it
#: is not a command this harness composes, and composing one here would put a
#: privilege transition inside an artifact whose whole purpose is to describe what
#: runs *after* that transition. `CommandStep.run_as` records the identity
#: instead.
#: **r6 §6.4, applied in C-P5.0-LAB-I-R1.** `/usr/bin/install` and
#: `/usr/bin/chattr` are **gone**, taking the set from 22 to 20. They were the
#: two pathname-based programs whose effects §1.4 replaces with syscalls issued
#: on a held descriptor: `install` succeeds whether or not something was already
#: at the name and re-resolves that name for each of its own effects, and
#: `chattr` sets a flag on whatever a fresh lookup finds. `EffectKind` below
#: names what replaced them, `executor.DescriptorBoundEffects` issues it, and
#: no step in this package may name either binary again.
PERMITTED_EXECUTABLES = frozenset(
    {
        "/usr/bin/lsattr",
        "/usr/bin/getent",
        "/usr/bin/id",
        "/usr/bin/namei",
        "/usr/bin/stat",
        "/usr/bin/findmnt",
        "/usr/bin/rm",
        "/usr/bin/rmdir",
        "/usr/bin/psql",
        "/usr/bin/systemd-run",
        "/usr/bin/systemctl",
        "/usr/bin/getcap",
        "/usr/bin/setpriv",
        "/usr/sbin/capsh",
        "/usr/sbin/useradd",
        "/usr/sbin/userdel",
        "/usr/sbin/groupadd",
        "/usr/sbin/groupdel",
        "/usr/sbin/gpasswd",
        "/usr/sbin/visudo",
    }
)

#: The two executables r6 §6.4 retires, named once so a structural test can
#: assert their absence from the allowlist, from every generated vector and from
#: the executable call graph without respelling them in three places.
RETIRED_EXECUTABLES: frozenset[str] = frozenset(
    {"/usr/bin/install", "/usr/bin/chattr"}
)

_FORBIDDEN_IN_ARGUMENT = set(";|&$`<>\n\r\\\"'*?")
#: A plain PostgreSQL role identifier. Same shape as a database name: unquoted,
#: lower case, so no statement in this package is built by escaping.
_POSTGRES_ROLE_NAME = re.compile(r"\A[a-z][a-z0-9_]{0,62}\Z")
#: An OS account name, in the shape `targets.validate_account_name` accepts. It is
#: repeated here rather than imported so that a *shape* failure in a declared
#: authentication mapping is a `PlanRefused` at mutation validation, while
#: `validate_account_name`'s separate question — *is this an existing production
#: identity?* — stays a `TargetRefused` raised against a named target.
_OS_ACCOUNT_NAME = re.compile(r"\A[a-z_][a-z0-9_-]{0,31}\Z")
_FORBIDDEN_EXECUTABLE_NAMES = frozenset({"sudo", "su", "sh", "bash", "env", "nohup", "setarch"})

#: The two permitted executables that can be asked to `execve` **another**
#: program: `capsh` names it with `--shell=` and runs it with the arguments after
#: `--`, and `systemd-run` runs the whole vector after `--` inside a transient
#: unit. For both, the program that actually runs is the tail rather than
#: `argv[0]`, so the tail is validated as a case-program vector — which is the
#: only way the interpreter may appear behind one of them.
#:
#: Every other permitted executable takes `--` as an end-of-options marker
#: followed by its own operands (`chattr +a -- PATH`, `rm --force -- PATH`), so
#: the rule is applied to these two by name and to nothing else.
_EXEC_DELEGATING_EXECUTABLES = frozenset({"/usr/sbin/capsh", "/usr/bin/systemd-run"})

#: The option `capsh` names the program to exec with.
_CAPSH_SHELL_OPTION = "--shell="

#: The shape `CommandStep.identity_name` may take: one of §2.13.5c's eight
#: identities. **`E7` is included — that is EH-R12-1's correction.** R12 wrote
#: this shape as `E[1-6]|E8` on the ground that `E7` is *"constructed by no
#: vector"*, which is true and is not a reason to leave it unobserved: it is
#: observed by running the same `identity` verb in the same final interpreted
#: process, directly rather than behind `capsh`.
#:
#: Written as a shape here rather than imported from `capability`, so the planner
#: keeps its existing import direction; `expectations.OBSERVED_IDENTITIES` is the
#: derived set and `tests/phase_5_0_evidence/test_expectations.py` asserts the two
#: agree.
OBSERVED_IDENTITY = re.compile(r"\AE[1-8]\Z")

#: The one identity that is **not** produced by a `capsh` construction: the
#: harness's own root process. A step observing it therefore substitutes nothing
#: and assumes no credential, and both are enforced below rather than described.
#: `expectations.ROOT_IDENTITY` is the same name, and the suite asserts it.
ROOT_IDENTITY_NAME = "E7"


class StepRole(str, Enum):
    """What a step's failure means for the rest of the run.

    The executor stops on the first unsatisfied step whatever its role, so the
    role does not decide *whether* to stop — it decides what the stop is
    **called**, and a stop nobody can name is a stop nobody can act on. It also
    makes the reviewed plan state, per step, which failures invalidate other
    steps' interpretation rather than leaving that to a reader.
    """

    #: Asserted before anything is constructed. Its failure makes the whole run
    #: inconclusive: no case is reported passed or refused.
    PREREQUISITE = "prerequisite"
    #: A positive control. Its failure makes every dependent case inconclusive —
    #: a refusal beside a failed control attributes nothing.
    CONTROL = "control"
    #: Interpreted only beside a control that passed.
    DEPENDENT = "dependent"
    #: Interpreted on its own observations.
    STANDALONE = "standalone"


class MutationKind(str, Enum):
    """The kinds of host state the authorized bands would create.

    The list is closed because `cleanup.py` maps each kind to exactly one
    reversal. A kind with no reversal cannot exist, which is how "cleanup is
    bounded" stops being a promise.
    """

    OS_GROUP = "os_group"
    OS_ACCOUNT = "os_account"
    GROUP_MEMBERSHIP = "group_membership"
    DIRECTORY = "directory"
    FILE = "file"
    FILE_ATTRIBUTE = "file_attribute"
    POSTGRES_ROLE = "postgres_role"
    POSTGRES_DATABASE = "postgres_database"
    POSTGRES_CONFIG_LINE = "postgres_config_line"
    TRANSIENT_UNIT = "transient_unit"


@dataclass(frozen=True, slots=True)
class Mutation:
    """One thing the run would create, and the one thing cleanup would remove.

    `identifier` is an absolute path for the filesystem kinds and a bare name for
    the identity and database kinds. It is validated against the target on
    construction, so a mutation naming a production path or a pre-existing
    account cannot be declared at all — the refusal happens where the object is
    named rather than where a command is emitted.
    """

    kind: MutationKind
    identifier: str
    reason: str
    #: For `POSTGRES_CONFIG_LINE` and `FILE_ATTRIBUTE`: the file the mutation is
    #: against. Empty for every other kind.
    file_path: str = ""
    #: For `GROUP_MEMBERSHIP`: the group the account is added to.
    group: str = ""
    #: For `POSTGRES_CONFIG_LINE`: **what the temporary authentication mutation
    #: makes possible** — the OS identity that would connect over the local
    #: socket, and the PostgreSQL role the HBA rule and identity map would admit
    #: it as. **Both are required for that kind** and both are empty for every
    #: other.
    #:
    #: EH-R2-2 is why they are declared, and EH-R3-2 is why they are required
    #: *here*. Restoring the two files is not restoring the running server's
    #: effective configuration, so cleanup has to *prove* the temporary mapping is
    #: no longer effective — and the proof step runs **as** `maps_os_user` and asks
    #: for `maps_postgres_role`. A configuration mutation that omits either half
    #: therefore describes a post-reload proof that cannot be constructed, and R2
    #: discovered that only inside `CleanupStep.__post_init__`, as a blank
    #: `run_as`, after the plan had already been half built. It is an invalid
    #: mutation, so it is refused where the mutation is declared.
    #:
    #: The pair names an identity and a role; it carries no rule text, no address,
    #: no authentication method and no credential.
    maps_os_user: str = ""
    maps_postgres_role: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.kind, MutationKind):
            raise PlanRefused("A mutation names one of the closed mutation kinds.")
        if not self.reason.strip():
            raise PlanRefused(
                f"Mutation {self.identifier!r} does not say why it exists. A "
                "mutation nobody can justify is one nobody reviewed."
            )
        if self.kind is MutationKind.POSTGRES_CONFIG_LINE:
            self._validate_authentication_mapping()
        elif self.maps_os_user or self.maps_postgres_role:
            raise PlanRefused(
                f"Mutation {self.identifier!r} is a {self.kind.value} and names an "
                "authentication mapping. Only a configuration-line mutation grants "
                "one, and only that mutation's cleanup has to prove one gone."
            )

    def _validate_authentication_mapping(self) -> None:
        """EH-R3-2: a configuration mutation carries a **complete** mapping pair.

        The two halves are validated together rather than separately, because
        half a mapping is not a smaller fact than a whole one — it is a
        post-reload proof that names either an identity with no role to ask for or
        a role with no identity to ask as. Neither can be run, and neither can be
        reported as *"the temporary mapping is gone"*.

        No half is ever defaulted. There is no fallback identity, no fallback role
        and no production identity to fall back to: the mapping the run created is
        the only mapping whose removal this plan can prove, so the plan either
        knows it or refuses.
        """
        if not self.file_path.strip():
            raise PlanRefused(
                f"Configuration mutation {self.identifier!r} names no file. A "
                "configuration line exists in a file, and cleanup restores files."
            )
        user, role = self.maps_os_user, self.maps_postgres_role
        if not (user or role):
            raise PlanRefused(
                f"Configuration mutation {self.identifier!r} declares no "
                "authentication mapping. Restoring pg_hba.conf and pg_ident.conf "
                "puts bytes back on disk; it does not prove the running server has "
                "stopped honouring the temporary rule. The proof connects **as** "
                "the mapped OS identity and asks for the mapped role, so a "
                "configuration mutation that does not say which pair it created "
                "describes a proof that cannot be constructed."
            )
        if not user or not role:
            missing = "maps_os_user" if not user else "maps_postgres_role"
            supplied = "maps_postgres_role" if not user else "maps_os_user"
            raise PlanRefused(
                f"Configuration mutation {self.identifier!r} supplies {supplied} "
                f"and not {missing}. A mapping is a pair; half of one names "
                "neither a connection that can be attempted nor a refusal that "
                "attributes anything, and the missing half is never defaulted."
            )
        if not _OS_ACCOUNT_NAME.match(user):
            raise PlanRefused(
                f"Configuration mutation {self.identifier!r} maps OS identity "
                f"{user!r}, which is not a usable account name. The post-reload "
                "proof runs as that identity, so a name no host can resolve is a "
                "proof that cannot be run."
            )
        if not _POSTGRES_ROLE_NAME.match(role):
            raise PlanRefused(
                f"Configuration mutation {self.identifier!r} maps to PostgreSQL "
                f"role {role!r}, which is not a plain unquoted identifier. The "
                "proof passes it as `--username`, and this harness quotes and "
                "escapes nothing."
            )

    @property
    def mutation_id(self) -> str:
        return f"{self.kind.value}:{self.identifier}"

    def validate_against(self, target: DisposableTarget) -> None:
        """Refuse a mutation this target does not admit.

        Called by `ExecutionPlan`, not by `__post_init__`, because a `Mutation` is
        also the vocabulary in which the *plan document* is written and a reviewer
        should be able to read one before a target exists.
        """
        target.require_mutable()
        if self.kind is MutationKind.DIRECTORY:
            # The root itself is a directory the run creates, so a directory
            # mutation may name it. Every other path — including every file and
            # every attribute — stays strictly inside. See
            # `DisposableTarget.root_or_contained_path` and handback conflict C-1.
            target.root_or_contained_path(self.identifier)
        elif self.kind is MutationKind.FILE:
            target.contained_path(self.identifier)
        elif self.kind is MutationKind.FILE_ATTRIBUTE:
            target.contained_path(self.identifier)
        elif self.kind in (MutationKind.OS_ACCOUNT, MutationKind.OS_GROUP):
            validate_account_name(self.identifier)
        elif self.kind is MutationKind.GROUP_MEMBERSHIP:
            validate_account_name(self.identifier)
            validate_account_name(self.group)
        elif self.kind is MutationKind.POSTGRES_ROLE:
            if not self.identifier.strip():
                raise PlanRefused("A PostgreSQL role mutation names a role.")
        elif self.kind is MutationKind.POSTGRES_DATABASE:
            validate_database_name(self.identifier)
            if self.identifier != target.database_name:
                raise PlanRefused(
                    f"The plan would create database {self.identifier!r}, which is "
                    f"not the target's {target.database_name!r}. One target, one "
                    "disposable database."
                )
        elif self.kind is MutationKind.POSTGRES_CONFIG_LINE:
            filename = self.file_path.rsplit("/", 1)[-1]
            expected = target.config_path(filename)
            if self.file_path != expected:
                raise PlanRefused(
                    f"{self.file_path!r} is not inside the disposable instance's "
                    f"configuration directory ({expected!r})."
                )
            validate_account_name(self.maps_os_user)
            if not _POSTGRES_ROLE_NAME.match(self.maps_postgres_role or ""):
                raise PlanRefused(
                    f"Configuration mutation {self.identifier!r} does not name the "
                    "PostgreSQL role its temporary rule admits. Cleanup has to "
                    "prove that mapping no longer effective after it reloads, and "
                    "it cannot name a mapping the mutation never declared."
                )
        elif self.kind is MutationKind.TRANSIENT_UNIT:
            if not self.identifier.endswith(".service") and not self.identifier.endswith(".scope"):
                raise PlanRefused(
                    "A transient unit is named as a unit, so `systemctl` can be "
                    "asked about exactly the thing that ran."
                )


def validate_argv(argv: Sequence[str], *, target: DisposableTarget) -> tuple[str, ...]:
    """Refuse an argument vector a reviewer could not check by reading it."""
    if not isinstance(argv, Sequence) or isinstance(argv, (str, bytes)):
        raise PlanRefused("An argument vector is a sequence of separate arguments.")
    vector = tuple(argv)
    if not vector:
        raise PlanRefused("An argument vector cannot be empty.")
    for argument in vector:
        if not isinstance(argument, str):
            raise PlanRefused(
                f"Argument {argument!r} is {type(argument).__name__}. Every argument "
                "is rendered as text at the point it is chosen, not by the runner."
            )
        if argument == "":
            raise PlanRefused("An empty argument is almost always a lost variable.")
        bad = sorted(set(argument) & _FORBIDDEN_IN_ARGUMENT)
        if bad:
            raise PlanRefused(
                f"Argument {argument!r} contains {bad}. In a vector these are "
                "silently literal and in a shell string they are silently not; "
                "neither is what the plan says the command does."
            )
        if "${" in argument or argument.startswith("$"):
            raise PlanRefused(
                f"Argument {argument!r} carries an unresolved variable. The harness "
                "resolves names to values when it plans, so the plan a reviewer "
                "approves is the plan that runs."
            )

    executable = vector[0]
    if executable.rsplit("/", 1)[-1] in _FORBIDDEN_EXECUTABLE_NAMES:
        raise PlanRefused(
            f"{executable!r} is a shell or a privilege-transition helper. The plan "
            "records the identity a step runs as in `run_as`; it does not compose "
            "the transition, and it never composes a shell."
        )
    if executable == INTERPRETER_PATH:
        # **Conflict C-2, Option B.** The interpreter is not a member of
        # `PERMITTED_EXECUTABLES` and is not admitted as a general command: it is
        # admitted here, and only when the whole vector matches the closed
        # case-program grammar — the two isolation flags in order, the one
        # program path inside the validated disposable root, one verb from the
        # closed vocabulary, and that verb's exact arity and argument kinds.
        validate_case_vector(vector, target=target)
        return vector
    if executable not in PERMITTED_EXECUTABLES:
        raise PlanRefused(
            f"{executable!r} is not a permitted distribution binary and is not the "
            "approved interpreter. An arbitrary program inside the disposable "
            "root is no longer admissible as an executable: conflict C-2's "
            "resolution names the interpreter in the vector, so the case program "
            "is an argument to it and never `argv[0]`."
        )
    _validate_delegated_vector(vector, target=target)
    return vector


def _validate_delegated_vector(
    vector: tuple[str, ...], *, target: DisposableTarget
) -> None:
    """`capsh` and `systemd-run` exec a program named inside their own vector.

    For both, the thing the kernel eventually runs is not `argv[0]` — it is the
    tail after `--`, with `capsh` additionally taking `argv[0]` of that tail from
    `--shell=`. So a vector that hid an unreviewed program behind one of them
    would defeat the whole argument-vector discipline, and the tail is therefore
    validated by exactly the grammar a direct case-program vector is.
    """
    executable = vector[0]
    if executable not in _EXEC_DELEGATING_EXECUTABLES or "--" not in vector:
        return
    tail = vector[vector.index("--") + 1 :]
    shells = [
        argument[len(_CAPSH_SHELL_OPTION) :]
        for argument in vector
        if argument.startswith(_CAPSH_SHELL_OPTION)
    ]
    if executable == "/usr/sbin/capsh":
        if not tail:
            # `capsh … --` with no tail execs the named shell with no arguments,
            # which is not an operation this plan expresses.
            raise PlanRefused(
                "A capsh step that reaches `--` names the program it execs and "
                "the arguments it gives it. An empty tail is an interactive "
                "shell, which this harness never runs."
            )
        if len(shells) != 1:
            raise PlanRefused(
                f"A capsh step that execs names exactly one {_CAPSH_SHELL_OPTION!r} "
                f"program; this one names {len(shells)}."
            )
        validate_case_vector((shells[0], *tail), target=target)
        return
    if shells:
        raise PlanRefused(
            f"{executable!r} does not take {_CAPSH_SHELL_OPTION!r}."
        )
    validate_case_vector(tail, target=target)


class EffectKind(str, Enum):
    """What a descriptor-bound step does, from the closed set r6 §1.4 names.

    **These are the effects that used to be `install` and `chattr` vectors.**
    An effect step carries no argument vector and no executable at all: the
    executor issues the syscall itself, on a descriptor the inventory holds, so
    there is no pathname re-resolved between the ownership check and the effect
    and no program in between that could resolve one.
    """

    #: **P1 + P1b.** `mkdirat` one run directory exclusively, then the parent's
    #: containing-entry barrier. Replaces `install --directory`.
    CREATE_DIRECTORY = "create_directory"
    #: Create one reviewed file exclusively from a held buffer, with the mode and
    #: ownership set on the descriptor. Replaces `install <src> <dst>` for the
    #: empty subjects.
    CREATE_OBJECT = "create_object"
    #: **P2.** Install the reviewed case program from the one held buffer.
    #: Replaces `install -m 0555 <source> <destination>`.
    INSTALL_PAYLOAD = "install_payload"
    #: **P4.** `ioctl(FS_IOC_SETFLAGS)` on the inode a descriptor holds.
    #: Replaces `chattr +a` / `chattr +i`.
    SET_FLAG = "set_flag"
    #: **L3's first half.** Clear the flag, on the descriptor. Replaces
    #: `chattr -ia`.
    CLEAR_FLAG = "clear_flag"
    #: **§1.4.3 / §2.3.3.** Capture the reviewed configuration set into the
    #: independent recovery store, crossing all five publication barriers.
    #: Replaces the two `install <config> <root>/before/<config>` vectors.
    CAPTURE_CONFIGURATION = "capture_configuration"
    #: **§2.4 / L1.** Verify against the independent store, then write and
    #: publish. Replaces the two `install <root>/before/<config> <config>`
    #: cleanup vectors.
    RESTORE_CONFIGURATION = "restore_configuration"


#: The inventory role the disposable root `R` is registered under, and the role
#: its parent is registered under. They are named in the planning tier because a
#: reviewed effect step names one of them, and `executor` imports them rather
#: than spelling a second copy.
ROOT_ROLE = "root"
EVIDENCE_ROLE = "evidence"
#: The role `/etc/postgresql/16/main` is held under — r6 §1.3.3's D9/D10 pair.
#: The two configuration effects resolve their components relative to that held
#: traversal descriptor, so no pathname under it is re-resolved between the
#: ownership check and the effect.
CONFIGURATION_ROLE = "pgconf"

#: The two inode flags r6 §1.4.2 P4 names, by the symbol the plan writes and the
#: `chattr` letter it replaces. The numeric values live in `executor`, beside
#: the `ioctl` request numbers, and neither is reachable from a vector.
EFFECT_FLAGS: Mapping[str, str] = {
    "append_only": "a",
    "immutable": "i",
}


@dataclass(frozen=True, slots=True)
class DescriptorEffect:
    """One descriptor-bound effect, reviewed exactly as an argument vector is.

    Every field is a name or a number a reviewer approves, and none of them is a
    pathname the executor resolves: `directory_role` selects a descriptor the
    inventory already holds and `name` is one path component under it. The
    absolute path the plan documents is derived from the two and is carried for
    the reviewer and the mutation id, never used to reach the object.
    """

    kind: EffectKind
    #: The inventory role whose **traversal** descriptor the effect is issued
    #: relative to. Empty only for the two configuration effects, which name the
    #: configuration role instead.
    directory_role: str = ""
    #: One path component under that role. Empty for the configuration effects.
    name: str = ""
    #: The absolute path this effect's object has, for the reviewer and for the
    #: declared mutation. It is documentation: nothing resolves it.
    path: str = ""
    mode: int = 0
    owner: str = ""
    group: str = ""
    #: One of `EFFECT_FLAGS` for `SET_FLAG`; for `CLEAR_FLAG` the flags cleared,
    #: in the order `chattr -ia` named them.
    flags: tuple[str, ...] = ()
    #: The covered source whose reviewed bytes `INSTALL_PAYLOAD` installs.
    payload_source: str = ""
    #: The inventory role the two configuration effects resolve their components
    #: under — the held `/etc/postgresql/16/main` traversal descriptor.
    configuration_role: str = ""
    #: The reviewed configuration components the capture and the restoration
    #: bind, in the order the plan lists them.
    components: tuple[str, ...] = ()
    #: **r6 §2.5.** Where a capture's **evidence** copy is retained under the
    #: disposable root. It is written from the independent store *after* the
    #: basis is durably published, so it can neither precede the basis nor be
    #: mistaken for it: "`R/before` may be retained for evidence, but it is not
    #: a recovery basis". Empty for every effect but the capture.
    evidence_role: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EffectKind):
            raise PlanRefused("A descriptor effect names one of the closed kinds.")
        if self.kind in _CONFIGURATION_EFFECTS:
            if not self.configuration_role or not self.components:
                raise PlanRefused(
                    f"A {self.kind.value} effect names the configuration role "
                    "it holds and the reviewed components it binds."
                )
            if self.directory_role or self.name:
                raise PlanRefused(
                    f"A {self.kind.value} effect binds a reviewed capture set, "
                    "not one named object under a run directory."
                )
            return
        if not self.directory_role.strip():
            raise PlanRefused(
                f"A {self.kind.value} effect names the directory role whose "
                "held descriptor it is issued relative to."
            )
        if not self.name or "/" in self.name or self.name in (".", ".."):
            raise PlanRefused(
                f"A {self.kind.value} effect names one path component. A "
                "separator, `.` or `..` would be a pathname, and a pathname is "
                "what the descriptor chain exists to remove."
            )
        if self.kind in (EffectKind.SET_FLAG, EffectKind.CLEAR_FLAG):
            if not self.flags or any(
                flag not in EFFECT_FLAGS for flag in self.flags
            ):
                raise PlanRefused(
                    f"A {self.kind.value} effect names one or more of "
                    f"{sorted(EFFECT_FLAGS)}."
                )
            if self.kind is EffectKind.SET_FLAG and len(self.flags) != 1:
                raise PlanRefused(
                    "A set_flag effect sets exactly one flag, as `chattr +a` "
                    "and `chattr +i` each did."
                )
        elif self.flags:
            raise PlanRefused(
                f"A {self.kind.value} effect sets no inode flag and names none."
            )
        if self.kind is EffectKind.INSTALL_PAYLOAD and not self.payload_source:
            raise PlanRefused(
                "An install_payload effect names the covered source whose "
                "reviewed bytes it installs, so the digest it is checked "
                "against is the manifest's rather than the file's."
            )

    @property
    def summary(self) -> str:
        """One reviewed line, for the rendered plan and the dry-run listing."""
        if self.kind in _CONFIGURATION_EFFECTS:
            return f"{self.kind.value}({', '.join(self.components)})"
        detail = f"{self.directory_role}/{self.name}"
        if self.flags:
            detail = f"{detail} {''.join(EFFECT_FLAGS[f] for f in self.flags)}"
        elif self.mode:
            detail = f"{detail} {self.mode:04o}"
        return f"{self.kind.value}({detail})"


_CONFIGURATION_EFFECTS = frozenset(
    {EffectKind.CAPTURE_CONFIGURATION, EffectKind.RESTORE_CONFIGURATION}
)


@dataclass(frozen=True, slots=True)
class CommandStep:
    """One command, with everything needed to review it before it is run."""

    step_id: str
    band: str
    #: The identity the step runs as: `root`, `freedomsheet`, `E4`, `postgres`.
    #: Recorded rather than composed — see `PERMITTED_EXECUTABLES`.
    run_as: str
    argv: tuple[str, ...]
    purpose: str
    #: Which evidence cases this step produces an observation for.
    evidence_case_ids: tuple[str, ...] = ()
    #: The ids of the `Mutation` rows this step performs. Empty means read-only,
    #: and a read-only step is admissible against an `UNASSIGNED` target.
    mutation_ids: tuple[str, ...] = ()
    #: What the plan expects to observe if the boundary holds, in prose. The
    #: machine-checkable form is `satisfying_statuses` / `refusal_required`
    #: below, and the band's `Outcome` for the classified case.
    expected_result: str = ""
    expected_refusal: str = ""
    #: What this step's failure invalidates. See `StepRole`.
    role: StepRole = StepRole.STANDALONE
    #: Exit statuses that mean the step observed what the plan says it would.
    #: Not always `(0,)`: `getent group` on an **absent** group exits 2, and
    #: absence is exactly what the JNL-52 precondition asserts.
    satisfying_statuses: tuple[int, ...] = (0,)
    #: True for a step whose satisfaction is a **non-zero** exit — a connection
    #: the authentication boundary must refuse. Exit 0 there is the failure.
    refusal_required: bool = False
    #: What a run may record from this step's output. Declared in the plan, so it
    #: is reviewed and digested rather than chosen at run time. The default
    #: records the exit status and nothing else, which is what every
    #: mutation-bearing step wants.
    capture: CapturePolicy = CapturePolicy.EXIT_STATUS_ONLY
    #: **Conflict C-5.** The declared late-binding sites: which argument indices
    #: carry a symbolic identity the executor resolves through the injected NSS
    #: boundary immediately before the process is created. The reviewed vector —
    #: the one the review manifest pins — carries the **names**; the numbers
    #: exist only in the bound vector, for the length of one `execve`. A step
    #: with no sites is substituted nowhere, which is every step but §2.13.5c's.
    bindings: tuple[BindingSite, ...] = ()
    #: **R12, corrected in R13.** Which of §2.13.5c's identities this step
    #: observes. Empty for every step but the **eight** `CASE_IDENTITY` ones, and
    #: required for those: it is what selects the typed semantic expectation the
    #: executor compares the observation against — the uid, gid, complete
    #: supplementary group set, five capability masks, `NoNewPrivs` and final
    #: securebits — and a step that observed an identity without saying which one
    #: would have no expectation to be compared with. It is pinned in the review
    #: manifest, so which contract applies to which step is reviewed rather than
    #: inferred.
    identity_name: str = ""
    #: **R13, EH-R13-3.** The reviewed semantic expectation for the observation
    #: this step records, in the closed comparison vocabulary of
    #: `expectations.DeclaredExpectation`. Required for every capture policy that
    #: records an observation and whose contract is not derived from reviewed
    #: constants, refused for the three that do not — `EXIT_STATUS_ONLY`, which
    #: records nothing, and the two case-program observation verbs, whose
    #: expectations come from `case_runtime`, the review manifest and
    #: `capability` rather than from a plan a step could write for itself.
    #:
    #: It is pinned in the review manifest, so what a prerequisite *means* is
    #: reviewed beside what it runs.
    observation_expectations: tuple["DeclaredExpectation", ...] = ()
    #: **R13, EH-R13-1.** The mutation ids whose subject this step proves
    #: **absent** before anything is created. Cleanup may remove an object only
    #: when a baseline step established that the run's own provisioning is what
    #: would have created it; without that, a reversal deletes whatever was
    #: already there. A baseline step performs no mutation and is refused if it
    #: declares one.
    establishes_ownership_of: tuple[str, ...] = ()
    #: **R13, EH-R13-1.** The exit statuses with which this step's executable
    #: reports *"the object already exists"* — `groupadd` and `useradd`'s 9. Such
    #: an exit satisfies nothing, stops the run, and additionally **withdraws
    #: ownership** of the declared mutation: the object was not created by this
    #: step, so this run may not delete it.
    preexisting_statuses: tuple[int, ...] = ()
    #: **R14, EH-R14-1.** The two names a `catalog_membership` reading answers
    #: about: the subject whose absence this baseline needs, and the control that
    #: proves the catalog was read at all. Required for that policy and refused
    #: for every other, and pinned in the review manifest — the vector alone does
    #: not carry them, because the reviewed grammar admits no string literal and
    #: the listing is therefore unfiltered.
    catalog_question: CatalogQuestion | None = None
    #: **R16, conflict C-8.** The mutation ids whose ownership this step
    #: establishes **by creating them exclusively**, rather than by having
    #: observed them absent beforehand.
    #:
    #: The distinction is the whole of C-8. `establishes_ownership_of` above is a
    #: *probe*: a separate observation, made earlier, that the subject was not
    #: there — and between that observation and the creation there is a window in
    #: which the object can arrive, which is why `install -d` over a directory
    #: somebody else made was the defect R14 could not repair for the filesystem.
    #: A step named here makes no probe. It performs a creation whose failure
    #: mode for *"something is already at this path"* is unique and documented —
    #: `mkdir(2)`'s `EEXIST`, for a directory, a file, a symbolic link and a
    #: dangling symbolic link alike — so **the successful creation is itself the
    #: proof that nothing was there**, with no window at all.
    #:
    #: The executor therefore grants this ownership **after** the step is
    #: satisfied rather than requiring it before the step runs, and only then.
    #: Every other outcome grants nothing.
    establishes_ownership_by_creation: tuple[str, ...] = ()
    #: **R16, conflict C-8.** The exit statuses with which this step's program
    #: reports that it created **nothing at all**.
    #:
    #: Required for a step that establishes ownership by creation, refused for
    #: every other. It is what separates the two unsatisfied outcomes that must
    #: never be confused: *the creation was refused, so there is nothing on the
    #: host and nothing to remove* — and *the creation may have happened and this
    #: run cannot identify what it made*, which is bounded residue and an
    #: operator recovery. A status outside this tuple, a timeout, a launch that
    #: never reported and an interruption are all the second case.
    nothing_created_statuses: tuple[int, ...] = ()
    #: **R16, conflict C-8.** The declared mutations whose subjects lie **inside**
    #: the object this step exclusively created, and whose ownership therefore
    #: follows from it.
    #:
    #: The argument is stated because it is the one inference in this design that
    #: is not a direct observation: `mkdir(2)` returns a directory that contains
    #: nothing but `.` and `..`, so at the instant the creation succeeded there
    #: was no object under that path for a later step to overwrite and no object
    #: this run could later delete that it had not itself put there. Ownership of
    #: the container is therefore ownership of everything the plan declares
    #: inside it — and the container is the whole of what R14 could not prove,
    #: because R13's `stat` could not tell an absent root from an unreadable one.
    #:
    #: It is enumerated rather than derived at run time, so a reviewer approves
    #: the exact set and the manifest pins it. `__post_init__` requires every id
    #: to name a path strictly inside a directory this same step creates
    #: exclusively; a mutation that is not is refused rather than swept in.
    establishes_ownership_of_contained: tuple[str, ...] = ()
    #: **r6 §1.4, C-P5.0-LAB-I-R1.** The descriptor-bound effect this step is,
    #: instead of a command. A step with one carries **no argument vector and no
    #: executable**: the executor issues the syscall itself through
    #: `executor.DescriptorBoundEffects`, on a descriptor the inventory holds.
    #:
    #: This is what replaced `/usr/bin/install` and `/usr/bin/chattr`. The two
    #: are no longer in `PERMITTED_EXECUTABLES`, so a step that tried to name
    #: one is refused by `validate_argv` rather than merely discouraged.
    effect: DescriptorEffect | None = None

    @property
    def is_effect(self) -> bool:
        """True for a descriptor-bound effect step. It has no argument vector."""
        return self.effect is not None

    def __post_init__(self) -> None:
        for name in ("step_id", "band", "run_as", "purpose"):
            if not getattr(self, name).strip():
                raise PlanRefused(f"A command step needs a {name}.")
        if not isinstance(self.bindings, tuple):
            raise PlanRefused(
                f"Step {self.step_id!r} declares its binding sites as a tuple, so "
                "the reviewed substitution set is immutable."
            )
        if not isinstance(self.argv, tuple):
            raise PlanRefused("A step's argv is a tuple, so the plan is immutable.")
        if self.effect is not None:
            if not isinstance(self.effect, DescriptorEffect):
                raise PlanRefused(
                    f"Step {self.step_id!r} names an effect that is not one of "
                    "the reviewed descriptor-bound effects."
                )
            if self.argv:
                raise PlanRefused(
                    f"Step {self.step_id!r} is a descriptor-bound effect and "
                    "carries an argument vector. An effect names no executable "
                    "at all — that is the whole of what replacing `install` and "
                    "`chattr` means."
                )
            if self.run_as != "root":
                raise PlanRefused(
                    f"Step {self.step_id!r} issues a descriptor-bound effect as "
                    f"{self.run_as!r}. The executor holds the descriptors and "
                    "issues every effect itself, as root; there is no process "
                    "for another identity to be assumed in."
                )
            if self.bindings:
                raise PlanRefused(
                    f"Step {self.step_id!r} is a descriptor-bound effect and "
                    "declares late-binding sites. There is no vector to "
                    "substitute a name into."
                )
            if self.capture is not CapturePolicy.EXIT_STATUS_ONLY:
                raise PlanRefused(
                    f"Step {self.step_id!r} is a descriptor-bound effect and "
                    "would record more than its outcome. An effect's purpose is "
                    "a side effect; it has no observation to make."
                )
        elif not self.argv:
            raise PlanRefused(
                f"Step {self.step_id!r} has neither an argument vector nor a "
                "descriptor-bound effect, so there is nothing for it to do."
            )
        if self.bindings:
            validate_sites(self.argv, self.bindings)
        if not isinstance(self.role, StepRole):
            raise PlanRefused(f"Step {self.step_id!r} names one of the closed step roles.")
        if not isinstance(self.capture, CapturePolicy):
            raise PlanRefused(
                f"Step {self.step_id!r} names one of the closed capture policies. "
                "What a run may record from a command is reviewed in advance."
            )
        if self.capture is CapturePolicy.CASE_IDENTITY:
            if not OBSERVED_IDENTITY.match(self.identity_name):
                raise PlanRefused(
                    f"Step {self.step_id!r} observes an identity and names "
                    f"{self.identity_name!r}. It names exactly one of §2.13.5c's "
                    "eight identities E1 … E8 — E7 included — because that name "
                    "is what selects the reviewed expectation its observation is "
                    "compared against."
                )
            if self.identity_name == ROOT_IDENTITY_NAME:
                # `E7` is the harness's own root identity: §2.13.5c gives it *"no
                # invocation … no securebit set and no drop of any kind"*. A step
                # claiming to observe it while substituting a disposable account
                # into its vector, or while assuming some other identity, would
                # be observing something else and calling it E7.
                if self.bindings:
                    raise PlanRefused(
                        f"Step {self.step_id!r} observes E7 and declares "
                        f"{len(self.bindings)} late-binding site(s). E7 drops "
                        "nothing and assumes nobody, so its vector carries no "
                        "symbolic account or group for the executor to "
                        "substitute; a vector with one is not E7's."
                    )
                if self.run_as != "root":
                    raise PlanRefused(
                        f"Step {self.step_id!r} observes E7 and runs as "
                        f"{self.run_as!r}. E7 **is** the harness's own root "
                        "process; observed from any other identity it is not the "
                        "thing §2.13.5c names."
                    )
        elif self.identity_name:
            raise PlanRefused(
                f"Step {self.step_id!r} names identity {self.identity_name!r} and "
                "does not observe one. The name selects a semantic expectation "
                "for a `case_identity` observation and means nothing beside any "
                "other capture policy."
            )
        self._validate_observation_expectations()
        self._validate_catalog_question()
        self._validate_ownership_declaration()
        self._validate_exclusive_creation()
        if (
            self.is_mutation_bearing
            and self.capture is not CapturePolicy.EXIT_STATUS_ONLY
            and not self.establishes_ownership_by_creation
        ):
            raise PlanRefused(
                f"Step {self.step_id!r} performs a mutation and would record more "
                "than its exit status. A step whose purpose is a side effect has "
                "no observation to make, and reading one from it is how something "
                "nobody reviewed reaches an artifact."
            )
        if self.refusal_required:
            if self.satisfying_statuses:
                raise PlanRefused(
                    f"Step {self.step_id!r} both requires a refusal and lists "
                    "satisfying exit statuses. A step that must be refused is "
                    "satisfied by any non-zero exit and by no zero one."
                )
            if self.is_mutation_bearing:
                raise PlanRefused(
                    f"Step {self.step_id!r} performs a mutation and requires a "
                    "refusal. A step that must be refused must not be the step "
                    "that creates something, because a refusal proves nothing "
                    "about what a partly-completed mutation left behind."
                )
        elif not self.satisfying_statuses:
            raise PlanRefused(
                f"Step {self.step_id!r} lists no satisfying exit status and does "
                "not require a refusal, so nothing decides whether it did what the "
                "plan says."
            )
        elif any(
            not isinstance(status, int) or isinstance(status, bool)
            for status in self.satisfying_statuses
        ):
            raise PlanRefused(
                f"Step {self.step_id!r} lists a satisfying status that is not an "
                "exit status."
            )

    def _validate_observation_expectations(self) -> None:
        """**EH-R13-3.** A step that records an observation states what it means.

        Three rules, checked when the plan is built rather than when a run stops:

        * a policy that records nothing declares nothing;
        * a policy whose contract is derived from reviewed constants declares
          nothing, because those expectations are not a plan's to write; and
        * **every other policy declares one**, and `expectations.
          declared_contract` additionally requires the declared keys to be the
          keys the policy emits, so a declaration cannot quietly leave one out.
        """
        if not isinstance(self.observation_expectations, tuple):
            raise PlanRefused(
                f"Step {self.step_id!r} declares its reviewed expectation as a "
                "tuple, so the plan is immutable."
            )
        if self.capture is CapturePolicy.EXIT_STATUS_ONLY:
            if self.observation_expectations:
                raise PlanRefused(
                    f"Step {self.step_id!r} records only its exit status and "
                    "declares an expectation for an observation it does not make."
                )
            return
        if self.capture in DERIVED_CONTRACT_POLICIES:
            if self.observation_expectations:
                raise PlanRefused(
                    f"Step {self.step_id!r} declares an expectation for a "
                    f"{self.capture.value} observation. That contract is built "
                    "from reviewed constants — the interpreter's target facts, "
                    "the review manifest's covered-source digest, §2.13.5c's "
                    "derivation and `capability.E7_TARGET_FACTS` — and a step "
                    "that supplied its own would be stating the expectation it "
                    "is judged against."
                )
            return
        if not self.observation_expectations:
            raise PlanRefused(
                f"Step {self.step_id!r} records a {self.capture.value} "
                "observation and declares no reviewed expectation for it. An "
                "observation nobody compares is not evidence — Blocking finding "
                "EH-R13-3 — and exit status alone does not decide a step that "
                "makes one."
            )
        # Built here, so a declaration that cannot become a contract is a refusal
        # while the plan is being generated.
        declared_contract(
            policy=self.capture,
            subject=self.step_id,
            declared=self.observation_expectations,
        )

    def _validate_catalog_question(self) -> None:
        """**EH-R14-1.** A catalog reading states which names it answers about.

        Three rules:

        * the policy that answers a question **has** one, because a reading with
          no question is the *unknown* state and would refuse every run;
        * no other policy carries one, because it would name something the
          reading never looks at; and
        * a baseline that establishes ownership from a catalog reading owns
          **only its subject**. Proving one name absent and claiming another is
          exactly the substitution EH-R14-1 is about, one level up.
        """
        if self.capture is CapturePolicy.CATALOG_MEMBERSHIP:
            if not isinstance(self.catalog_question, CatalogQuestion):
                raise PlanRefused(
                    f"Step {self.step_id!r} reads a catalog and states no "
                    "question. The reviewed vector lists the whole catalog — "
                    "the grammar admits no string literal to filter it with — so "
                    "the names it is asked about are the plan's to declare and "
                    "the manifest's to pin."
                )
            for mutation_id in self.establishes_ownership_of:
                if not mutation_id.endswith(f":{self.catalog_question.subject}"):
                    raise PlanRefused(
                        f"Step {self.step_id!r} proves "
                        f"{self.catalog_question.subject!r} absent and claims "
                        f"ownership of {mutation_id!r}. A baseline establishes "
                        "ownership of the object it looked for and of no other."
                    )
            return
        if self.catalog_question is not None:
            raise PlanRefused(
                f"Step {self.step_id!r} states a catalog question and does not "
                f"read a catalog: its policy is {self.capture.value}."
            )

    def _validate_ownership_declaration(self) -> None:
        """**EH-R13-1.** A baseline step proves absence and creates nothing."""
        if not isinstance(self.establishes_ownership_of, tuple):
            raise PlanRefused(
                f"Step {self.step_id!r} declares the mutations it establishes "
                "ownership of as a tuple."
            )
        if self.establishes_ownership_of and self.is_mutation_bearing:
            raise PlanRefused(
                f"Step {self.step_id!r} both creates an object and proves one "
                "absent. A baseline observation that runs after a change "
                "establishes nothing about what was there before it."
            )
        if not isinstance(self.preexisting_statuses, tuple) or any(
            not isinstance(status, int) or isinstance(status, bool)
            for status in self.preexisting_statuses
        ):
            raise PlanRefused(
                f"Step {self.step_id!r} lists an already-exists status that is "
                "not an exit status."
            )
        if self.preexisting_statuses and not self.is_mutation_bearing:
            raise PlanRefused(
                f"Step {self.step_id!r} reports an already-exists status and "
                "declares no mutation, so there is no ownership to withdraw."
            )
        overlap = sorted(set(self.preexisting_statuses) & set(self.satisfying_statuses))
        if overlap:
            raise PlanRefused(
                f"Step {self.step_id!r} treats {overlap} as both satisfying and "
                "as evidence the object already existed. A creation that found "
                "its object already there did not create it."
            )

    def _validate_exclusive_creation(self) -> None:
        """**R16, conflict C-8.** An exclusive creation is its own ownership.

        Six rules, all checked when the plan is built:

        * the declaration is a tuple, so the plan stays immutable;
        * every id it names is one this step actually performs. Ownership by
          creation is ownership of *the thing this step created*, and claiming
          another object is the substitution EH-R14-1 is about;
        * it does not also probe. A step cannot both observe its subject absent
          beforehand and be the creation that proves it, and declaring both would
          leave a reader unable to say which claim the ownership rests on;
        * exit 0 and only exit 0 satisfies it, and it does not require a refusal.
          A creation satisfied by a non-zero status would be granting ownership
          from a failure, which is the whole family of defects R14 corrected;
        * it names the unique pre-existence status its program reports, so
          *"something was already there"* withdraws ownership rather than merely
          failing to claim it; and
        * it names the statuses in which nothing was created, and none of them is
          a satisfying one.
        """
        for name in (
            "establishes_ownership_by_creation",
            "nothing_created_statuses",
            "establishes_ownership_of_contained",
        ):
            if not isinstance(getattr(self, name), tuple):
                raise PlanRefused(
                    f"Step {self.step_id!r} declares {name} as a tuple, so the "
                    "plan is immutable."
                )
        if not self.establishes_ownership_by_creation:
            if self.nothing_created_statuses:
                raise PlanRefused(
                    f"Step {self.step_id!r} names the statuses in which it "
                    "created nothing and does not establish ownership by "
                    "creation. The distinction has nothing to separate."
                )
            if self.establishes_ownership_of_contained:
                raise PlanRefused(
                    f"Step {self.step_id!r} claims ownership of what is inside "
                    "an object it does not create exclusively. Contained "
                    "ownership follows from a creation that returned an empty "
                    "directory, and from nothing else."
                )
            return
        outside = sorted(
            set(self.establishes_ownership_by_creation) - set(self.mutation_ids)
        )
        if outside:
            raise PlanRefused(
                f"Step {self.step_id!r} claims ownership by creation of "
                f"{outside}, which it does not perform. A creation establishes "
                "ownership of the object it created and of no other."
            )
        if self.establishes_ownership_of:
            raise PlanRefused(
                f"Step {self.step_id!r} both probes for absence and claims "
                "ownership by creation. Those are two different claims about two "
                "different moments, and a step that made both would leave a "
                "reader unable to say which one the deletion rests on."
            )
        if self.refusal_required or self.satisfying_statuses != (0,):
            raise PlanRefused(
                f"Step {self.step_id!r} establishes ownership by creation and is "
                f"satisfied by {list(self.satisfying_statuses)}. Exclusive "
                "creation grants ownership because the call **returned**; a "
                "satisfying non-zero status would be ownership derived from a "
                "failure, which is the defect EH-R14-1 named three times."
            )
        if not self.preexisting_statuses:
            raise PlanRefused(
                f"Step {self.step_id!r} establishes ownership by creation and "
                "names no status for *'something is already at this path'*. That "
                "status is the reason a creation can replace a probe at all, and "
                "a step that cannot report it is a probe with extra steps."
            )
        if not self.nothing_created_statuses:
            raise PlanRefused(
                f"Step {self.step_id!r} establishes ownership by creation and "
                "does not say in which statuses it created nothing. Without it a "
                "run cannot separate *'refused, so the host is untouched'* from "
                "*'it may have been created and cannot be identified'*, and the "
                "second is residue an operator has to be told about."
            )
        overlap = sorted(
            set(self.nothing_created_statuses) & set(self.satisfying_statuses)
        )
        if overlap:
            raise PlanRefused(
                f"Step {self.step_id!r} treats {overlap} as both satisfying and "
                "as evidence that nothing was created."
            )
        containers = tuple(
            mutation_id.split(":", 1)[1]
            for mutation_id in self.establishes_ownership_by_creation
            if mutation_id.startswith(f"{MutationKind.DIRECTORY.value}:")
        )
        for mutation_id in self.establishes_ownership_of_contained:
            subject = mutation_id.split(":", 1)[1] if ":" in mutation_id else ""
            if not any(
                subject.startswith(f"{container}/") for container in containers
            ):
                raise PlanRefused(
                    f"Step {self.step_id!r} claims ownership of {mutation_id!r} "
                    f"as contained by {list(containers)}, and its subject is not "
                    "strictly inside any of them. Contained ownership reaches "
                    "exactly what the created directory contains."
                )
            if mutation_id in self.establishes_ownership_by_creation:
                raise PlanRefused(
                    f"Step {self.step_id!r} claims {mutation_id!r} both as its "
                    "own exclusive creation and as something contained by it."
                )

    def created_nothing(self, exit_status: int) -> bool:
        """Whether this unsatisfied status means the host is untouched.

        `False` is the conservative answer, and it is the answer for every status
        a step did not enumerate — including the ones no program produces, such
        as the executor's own `-1` for a launch that never reported.
        """
        return exit_status in self.nothing_created_statuses

    def reports_preexisting(self, exit_status: int) -> bool:
        """Whether this exit status says the object was already there.

        **EH-R13-1.** Filtering cleanup to the mutations a run attempted does not
        cover this case on its own: the attempt was made, and it is precisely the
        attempt that reported the object was somebody else's. Ownership is
        therefore withdrawn rather than merely unclaimed.
        """
        return exit_status in self.preexisting_statuses

    def is_satisfied_by(self, exit_status: int) -> bool:
        """Whether this exit status is the one the reviewed plan expects.

        Deliberately not *"exited zero"*: the JNL-52 precondition is satisfied by
        `getent`'s exit 2, and every authentication-boundary denial is satisfied
        only by a non-zero exit.
        """
        if self.refusal_required:
            return exit_status != 0
        return exit_status in self.satisfying_statuses

    @property
    def is_mutation_bearing(self) -> bool:
        return bool(self.mutation_ids)

    def rendered(self) -> str:
        """The vector, one argument per token, for the plan document.

        Deliberately **not** shell-quoted: this is a rendering of a vector, and
        presenting it as a copy-pasteable shell line would invite exactly the
        string construction the vector exists to avoid.
        """
        return " ".join(self.argv)


@dataclass(frozen=True, slots=True)
class MaterializeStep:
    """One reviewed byte sequence, written to one pinned destination.

    **Deliberately not a `CommandStep`.** It has no `argv`, so it cannot reach
    `validate_argv`, cannot be handed to the process boundary and cannot be
    mistaken for a command in a rendered plan — the same separation
    `concrete_plan.UnresolvedStep` has, for the same reason. It is the resolution
    of conflict **C-4**, and it is as narrow as that conflict: the content comes
    from `materialization.MaterializedFile`, which is a closed table of two
    files, and the destination comes from `DisposableTarget.config_path()`, which
    knows two filenames and no third.

    Two orderings are declared rather than implied, because both are what makes
    the mutation reversible:

    * `capture_step_id` names the step that took the **byte-exact pre-change
      capture** this destination is restored from. The executor refuses to
      materialize when that step was not satisfied, so a configuration mutation
      whose restore has nothing to reinstall is never made; and
    * `after_step_id` names the command step this runs immediately after, so a
      reviewer reads the run order out of the plan rather than reconstructing it
      from two lists.
    """

    step_id: str
    band: str
    #: The identity that performs the write. It is `root`, and it is the
    #: harness's **own** process rather than a child: there is no argument vector
    #: here for a child to be given. The materializer re-checks that the process
    #: is effective UID and GID 0 before it writes anything.
    run_as: str
    #: The absolute path, which must be exactly `target.config_path(filename)`.
    destination: str
    file: MaterializedFile
    purpose: str
    capture_step_id: str
    after_step_id: str
    mutation_ids: tuple[str, ...] = ()
    evidence_case_ids: tuple[str, ...] = ()
    role: StepRole = StepRole.STANDALONE
    expected_result: str = ""
    expected_refusal: str = ""

    def __post_init__(self) -> None:
        for name in (
            "step_id",
            "band",
            "run_as",
            "destination",
            "purpose",
            "capture_step_id",
            "after_step_id",
        ):
            if not getattr(self, name).strip():
                raise PlanRefused(f"A materialization step needs a {name}.")
        if not isinstance(self.file, MaterializedFile):
            raise PlanRefused(
                f"Materialization step {self.step_id!r} does not carry a reviewed "
                "file. The bytes come from the closed table in "
                "`materialization.py` and from nowhere else."
            )
        if not isinstance(self.role, StepRole):
            raise PlanRefused(
                f"Materialization step {self.step_id!r} names one of the closed "
                "step roles."
            )
        if self.run_as != "root":
            raise PlanRefused(
                f"Materialization step {self.step_id!r} runs as {self.run_as!r}. "
                "The write is performed by the root harness process itself; there "
                "is no argument vector here, so there is no child to give another "
                "identity to."
            )
        if not self.mutation_ids:
            raise PlanRefused(
                f"Materialization step {self.step_id!r} declares no mutation. It "
                "replaces a live configuration file, which is the most reversible "
                "thing in the plan only because the restore is derived from a "
                "declared mutation."
            )
        normalized = validate_absolute_path(self.destination, what="materialization destination")
        if normalized != self.destination:
            raise PlanRefused(
                f"Materialization destination {self.destination!r} is not already "
                "normalized, so what a reviewer approved is not what would be "
                "written."
            )
        if self.destination.rsplit("/", 1)[-1] != self.file.filename:
            raise PlanRefused(
                f"Materialization step {self.step_id!r} would write "
                f"{self.file.filename!r} to {self.destination!r}. The reviewed "
                "content and the destination name the same file, or neither was "
                "reviewed."
            )

    @property
    def is_mutation_bearing(self) -> bool:
        return bool(self.mutation_ids)

    def validate_against(self, target: DisposableTarget) -> None:
        """Refuse a destination this target does not admit.

        `config_path()` is the guard, not a string comparison written here: it
        requires the filename to be one of two, requires the disposable
        instance's configuration directory to have been named, and refuses a
        production path, a system path and the repository worktree before it
        returns anything.
        """
        expected = target.config_path(self.file.filename)
        if self.destination != expected:
            raise PlanRefused(
                f"Materialization step {self.step_id!r} names destination "
                f"{self.destination!r}, and this target's configuration path for "
                f"{self.file.filename!r} is {expected!r}. A materialization "
                "reaches exactly the disposable instance's own configuration "
                "directory."
            )


@dataclass(frozen=True, slots=True)
class PlannedInvocation:
    """What `DryRunRunner` records. `executed` is a constant, and it is False."""

    step_id: str
    run_as: str
    argv: tuple[str, ...]
    executed: bool = False


class Runner(Protocol):
    """The interface an executing runner would have to implement.

    It is declared so that the pre-execution and execution stages have a shared
    vocabulary, and so that the *absence* of an executing implementation in this
    package is visible rather than incidental.
    """

    def run(self, step: CommandStep) -> PlannedInvocation: ...


class DryRunRunner:
    """Records intent. Executes nothing, ever.

    There is no code path in this class, or anywhere else in this package, that
    reaches a process, a socket or a database. The class exists so that the
    planning side can be exercised end to end by the tests without any part of
    the harness acquiring the ability to run what it plans.
    """

    def __init__(self) -> None:
        self._invocations: list[PlannedInvocation] = []

    def run(self, step: CommandStep) -> PlannedInvocation:
        invocation = PlannedInvocation(
            step_id=step.step_id, run_as=step.run_as, argv=step.argv
        )
        self._invocations.append(invocation)
        return invocation

    def run_all(self, steps: Iterable[CommandStep]) -> tuple[PlannedInvocation, ...]:
        return tuple(self.run(step) for step in steps)

    @property
    def invocations(self) -> tuple[PlannedInvocation, ...]:
        return tuple(self._invocations)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """The target, every mutation it declares, and every step that performs one.

    Construction is the check. A plan that holds a mutation-bearing step against
    an unassigned or unconfirmed target does not exist, and neither does one whose
    steps perform a mutation the plan did not declare.
    """

    target: DisposableTarget
    steps: tuple[CommandStep, ...]
    mutations: tuple[Mutation, ...] = ()
    #: The reviewed byte sequences the run would write, each anchored to the
    #: command step it follows. Held beside `steps` rather than inside it,
    #: because a materialization has no argument vector and a list whose members
    #: sometimes have one is a list every reader has to check.
    materializations: tuple[MaterializeStep, ...] = ()
    #: The banner the execution-plan document carries until Codex approves it.
    #: It is a field rather than a constant so that a plan object rendered into a
    #: document cannot lose it.
    review_state: str = "NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED"

    def __post_init__(self) -> None:
        declared: dict[str, Mutation] = {}
        for mutation in self.mutations:
            if mutation.mutation_id in declared:
                raise PlanRefused(
                    f"Mutation {mutation.mutation_id!r} is declared twice. One "
                    "declaration, one cleanup step."
                )
            declared[mutation.mutation_id] = mutation

        seen_steps: set[str] = set()
        step_order: dict[str, int] = {}
        for step in self.steps:
            if step.step_id in seen_steps:
                raise PlanRefused(f"Step id {step.step_id!r} is used twice.")
            seen_steps.add(step.step_id)
            step_order[step.step_id] = len(step_order)
            if not step.is_effect:
                validate_argv(step.argv, target=self.target)
            if not step.is_mutation_bearing:
                continue
            self.target.require_mutable()
            for mutation_id in step.mutation_ids:
                if mutation_id not in declared:
                    raise PlanRefused(
                        f"Step {step.step_id!r} performs mutation {mutation_id!r}, "
                        "which the plan does not declare. A mutation the plan does "
                        "not name has no cleanup step and no reviewer approval."
                    )

        for materialization in self.materializations:
            if materialization.step_id in seen_steps:
                raise PlanRefused(
                    f"Step id {materialization.step_id!r} is used twice. Command "
                    "steps and materializations share one id space, so a run's "
                    "outcome can always be attributed to exactly one of them."
                )
            seen_steps.add(materialization.step_id)
            self.target.require_mutable()
            materialization.validate_against(self.target)
            for mutation_id in materialization.mutation_ids:
                if mutation_id not in declared:
                    raise PlanRefused(
                        f"Materialization {materialization.step_id!r} performs "
                        f"mutation {mutation_id!r}, which the plan does not "
                        "declare. A configuration file written under a mutation "
                        "nobody declared has no restore step."
                    )
            for name, referenced in (
                ("capture_step_id", materialization.capture_step_id),
                ("after_step_id", materialization.after_step_id),
            ):
                if referenced not in step_order:
                    raise PlanRefused(
                        f"Materialization {materialization.step_id!r} names "
                        f"{name} {referenced!r}, which is not a step in this plan."
                    )
            if (
                step_order[materialization.capture_step_id]
                > step_order[materialization.after_step_id]
            ):
                raise PlanRefused(
                    f"Materialization {materialization.step_id!r} would run after "
                    f"{materialization.after_step_id!r} and depends on a capture "
                    f"taken by {materialization.capture_step_id!r}, which the plan "
                    "orders later. The byte-exact capture is taken before the file "
                    "is replaced, or there is nothing for cleanup to reinstall."
                )

        for mutation in self.mutations:
            mutation.validate_against(self.target)

    @property
    def mutation_bearing_steps(self) -> tuple[CommandStep, ...]:
        return tuple(step for step in self.steps if step.is_mutation_bearing)

    @property
    def read_only_steps(self) -> tuple[CommandStep, ...]:
        return tuple(step for step in self.steps if not step.is_mutation_bearing)

    def mutations_by_id(self) -> Mapping[str, Mutation]:
        return {mutation.mutation_id: mutation for mutation in self.mutations}

    def materializations_after(self, step_id: str) -> tuple[MaterializeStep, ...]:
        """The materializations anchored to `step_id`, in declaration order."""
        return tuple(
            item for item in self.materializations if item.after_step_id == step_id
        )

    def dry_run(self) -> tuple[PlannedInvocation, ...]:
        """Walk every step through the only runner there is."""
        return DryRunRunner().run_all(self.steps)


def read_only_plan(steps: Sequence[CommandStep]) -> ExecutionPlan:
    """A plan of reads, admissible before a target has been named.

    This is the shape the C-1 and pre-change HBA discovery bands take: an
    authorized reader performs them and supplies the result, and the harness
    plans, records and classifies without a disposable target existing at all.
    """
    plan = ExecutionPlan(target=DisposableTarget.unassigned(), steps=tuple(steps))
    for step in plan.steps:
        if step.is_mutation_bearing:  # pragma: no cover - refused above
            raise PlanRefused("A read-only plan holds no mutation-bearing step.")
    return plan


__all__ = [
    "CommandStep",
    "DescriptorEffect",
    "EFFECT_FLAGS",
    "CONFIGURATION_ROLE",
    "EVIDENCE_ROLE",
    "EffectKind",
    "ROOT_ROLE",
    "RETIRED_EXECUTABLES",
    "StepRole",
    "DryRunRunner",
    "ExecutionPlan",
    "MaterializeStep",
    "Mutation",
    "MutationKind",
    "OBSERVED_IDENTITY",
    "PERMITTED_EXECUTABLES",
    "PlannedInvocation",
    "ROOT_IDENTITY_NAME",
    "Runner",
    "read_only_plan",
    "validate_argv",
]
