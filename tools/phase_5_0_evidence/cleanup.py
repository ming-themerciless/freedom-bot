"""Cleanup planning: bounded, reverse-order, idempotent, and structurally unable
to express a recursive deletion.

## Derived, not written

A cleanup step is **generated from a declared `Mutation`**, one per mutation,
through a closed table. Nobody writes a cleanup command in this package, so
nobody can write `rm -rf`. The table has one entry per `MutationKind`, and a kind
with no entry cannot exist — `plan.MutationKind` and `_REVERSALS` are checked
against each other by `tests/phase_5_0_evidence/test_cleanup.py`, so a future
mutation kind fails the suite on the day it is added rather than the day it
leaves residue.

## Reverse dependency order

Mutations are reversed in the exact reverse of the order they were declared. The
provisioning order §2.12.7 gives is group, then accounts, then membership, then
paths, then database objects, then configuration; reversing the declaration order
therefore removes a membership before the group it names and a file before the
directory that holds it, without this module knowing anything about the
dependencies — the plan's ordering already encodes them.

## Idempotent, and what that means here — stated precisely, because the loose
## version would be false

Idempotence here is **"no step performs a destructive act when its object is
absent"**, not *"every step exits 0"*. The two are different and only the first
is true of `rmdir`: it exits non-zero on a directory that is already gone, and
also on one that still holds something. Re-running a complete plan against an
already clean host is therefore safe, and the §2.13.2b recovery procedure is
re-runnable, without any step having to be silent about failing.

Each step additionally records which exit statuses mean *"gone"* — `rm --force`
exits 0 on a missing file, `userdel` and `groupdel` exit 6, `gpasswd --delete`
exits 3, `DROP … IF EXISTS` exits 0, `systemctl stop` exits 5. **Residue is
decided by a presence check, never by an exit status**, and that check is what
feeds `classify_cleanup`: a `rmdir` that failed because the directory still holds
an artifact the plan did not declare leaves the path present, and the path is
reported.

## Restoring files is not restoring configuration — EH-R2-2

Reinstalling `pg_hba.conf` and `pg_ident.conf` puts the recorded bytes back on
disk. It does **not** put the recorded rules back into the running server:
PostgreSQL parses those files at startup and on `SIGHUP`, and until it is told to
re-read them it keeps authenticating with the harness's temporary rules in
memory. The previous version restored both files and continued, and a run that
had finished "cleanly" could leave the temporary peer rule and identity map
effective for as long as the postmaster lived.

Cleanup therefore has an ordered configuration phase, generated whenever the plan
declares a configuration-line mutation and placed **before every other step**:

1. **restore** every captured configuration file, one `install` of the byte-exact
   pre-change capture each — both of them when both were captured, and the one
   that was reached when a partial setup only reached one;
2. **reload**, exactly once, with `SELECT pg_reload_conf()`; and
3. **verify**, with a bounded post-reload observation that the temporary mapping
   is no longer effective.

The verification is two steps, in this order, because a refusal on its own
attributes nothing — the same rule the evidence bands live by:

* a **control**: an ordinary local connection as `postgres` must still succeed,
  which excludes "the server is down" and "the socket moved" as explanations; and
* the **proof**: a connection as the temporary OS identity asking for the
  temporary role must be **refused**. It runs while that role still exists —
  before `DROP ROLE`, which is why the drop steps come after — so the refusal is
  attributable to the removed mapping and not to a missing role.

Neither observation reads, prints or returns any configuration, rule text,
address, authentication method or credential: one is `SELECT 1`, the other is
whether `SELECT 1` was refused.

## The mapping the proof needs must exist before the plan is built — EH-R3-2

The refusal proof runs **as** the mapped OS identity and asks for the mapped
PostgreSQL role. Both come from the configuration mutation, and R2 let a
configuration mutation omit them: `Mutation` required the pair only in
`validate_against()`, which `CleanupPlan.for_mutations()` never called, so an
incomplete mutation travelled all the way into `_verification_refusal_step()` and
was caught there as a blank `run_as`. The plan then refused — with a message
about a step, after part of the plan had been assembled, and before the restore,
reload and verification ordering could be inspected at all.

The contract is now stated in one place and enforced three times, earliest first:

1. `plan.Mutation.__post_init__` refuses a `POSTGRES_CONFIG_LINE` that declares
   no mapping, half a mapping, or a malformed identity or role;
2. `CleanupPlan.for_mutations()` validates **every** declared mutation against
   the target before it builds a single step; and
3. `_require_complete_mapping()` refuses a blank half at the last point before it
   would become a `CleanupStep`'s `run_as` or `--username`.

No half is ever defaulted. There is no fallback identity and no fallback role:
the mapping the run created is the only mapping this plan can prove gone, so a
plan that does not know it refuses rather than substituting `postgres`,
`freedomcoord`, `freedomsheet` or any other identity that exists on some host.

**A zero exit from the reload is not evidence.** `pg_reload_conf()` returns as
soon as the signal is sent; it reports neither that the files parsed nor that the
new rules are in force. `ConfigurationRestoration.problems()` therefore treats a
successful reload with no post-reload observation as an unresolved
effective-configuration risk, and `classify_cleanup()` makes any restore, reload
or verification failure state **S-B** — the same state as filesystem residue, and
for the same reason: something the run created is still in effect.

## What cleanup deliberately cannot do

* **No recursion.** No generated argv contains `-r`, `-R`, `--recursive`,
  `--one-file-system` or `rm` on a directory. Directories are removed with
  `rmdir`, which refuses a non-empty directory — so a directory holding an
  artifact the plan did not declare stays, and is reported as residue.
* **No path outside the target.** Every path passes `DisposableTarget.
  contained_path`, except the two PostgreSQL configuration files, which pass
  `config_path`.
* **No cleaning of residue.** §2.13.2b is explicit: a failed cleanup is state
  **S-B**, the residue is reported by absolute path, and the next invocation
  *refuses* rather than cleaning it. `CleanupOutcome` records that refusal; it
  does not offer a second attempt.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping, NamedTuple, Sequence

from .capture import CapturePolicy
from .case_runtime import INTERPRETER_PATH, build_bootstrap_vector
from .errors import PlanRefused
from .journal import RECOVERY_PROCEDURE as RESIDUE_RECOVERY_PROCEDURE
from .journal import RecoveryStep
from .plan import (
    CONFIGURATION_ROLE,
    DescriptorEffect,
    EffectKind,
    Mutation,
    MutationKind,
)
from .records import CleanupState
from .targets import DisposableTarget

#: Tokens that would make a removal unbounded. Checked on every generated argv,
#: so the table and the guard have to agree rather than the table being trusted.
FORBIDDEN_CLEANUP_TOKENS = frozenset(
    {"-r", "-R", "-rf", "-fr", "--recursive", "--no-preserve-root", "*", "-a"}
)

#: Every executable a reversal may name. Each is non-destructive when its object
#: is absent, which is what makes a re-run of the whole plan safe. The set is
#: closed so that adding a reversal that is *not* safe to re-run fails the suite.
NON_DESTRUCTIVE_WHEN_ABSENT = frozenset(
    {
        "/usr/bin/rm",
        "/usr/bin/rmdir",
        # `/usr/bin/chattr` and `/usr/bin/install` are **gone** — r6 §6.4,
        # applied in C-P5.0-LAB-I-R1. The flag clear and the configuration
        # restoration are descriptor-bound effects now, and `is_safe_to_rerun`
        # states separately why each is re-runnable.
        "/usr/bin/psql",
        "/usr/bin/systemctl",
        "/usr/sbin/userdel",
        "/usr/sbin/groupdel",
        "/usr/sbin/gpasswd",
        # **R16, conflict C-8.** The approved interpreter, admitted here for the
        # one bootstrap vector cleanup runs: `statroot`, which opens the
        # disposable root with `O_DIRECTORY|O_NOFOLLOW`, reports its device and
        # inode and changes nothing. On an already-absent root it exits with
        # `ENOENT` and destroys nothing, which is the property this set is about.
        INTERPRETER_PATH,
    }
)


class CleanupStepKind(str, Enum):
    """What a cleanup step is for.

    The kind is what lets the ordering rules be checked rather than described: a
    restore must precede the reload, the reload must precede every step whose
    safety depends on the restored authentication, and cleanup is not complete
    until the verification has been made.
    """

    #: Reinstall a captured PostgreSQL configuration file over the live one.
    RESTORE = "restore"
    #: `SELECT pg_reload_conf()` — the one step that makes a restored file the
    #: server's effective configuration.
    RELOAD = "reload"
    #: The bounded post-reload observation. Exactly two shapes: the control that
    #: must connect, and the mapping that must be refused.
    VERIFY = "verify"
    #: **R16, conflict C-8.** Re-read the identity of an exclusively created
    #: object immediately before the step that would remove it, so the executor
    #: can compare it with the identity the creation reported. It removes
    #: nothing, restores nothing and reloads nothing: it is the check that stops
    #: a **replaced** path from inheriting permission to have its replacement
    #: deleted.
    REVALIDATE = "revalidate"
    #: Remove one declared object.
    REVERSAL = "reversal"


@dataclass(frozen=True, slots=True)
class CleanupStep:
    """One cleanup command, and what its exit status has to be to satisfy it."""

    step_id: str
    kind: CleanupStepKind
    #: The identity the step runs as. Recorded, never composed — this package
    #: emits no privilege transition.
    run_as: str
    argv: tuple[str, ...]
    #: The object this step removes or restores, by absolute path or bare name.
    #: Empty for a reload or a verification, which remove nothing.
    removes: str = ""
    #: The declared mutations this step reverses. Empty for a reload or a
    #: verification, which reverse nothing on their own — they are what make the
    #: restores that precede them effective, and what proves that they are.
    mutation_ids: tuple[str, ...] = ()
    #: Exit statuses that satisfy the step. For a reversal these are the ones
    #: meaning *"absent"*, including the one meaning *"removed just now"*.
    #: Anything else is a cleanup failure and therefore state S-B.
    satisfying_statuses: tuple[int, ...] = (0,)
    #: True for the one step whose *satisfaction* is a **non-zero** exit: the
    #: post-reload connection as the temporary identity, which must be refused.
    #: Exit 0 there means the temporary mapping is still effective.
    refusal_required: bool = False
    #: **R13, Blocking finding EH-R13-2.** Cleanup step ids that must have been
    #: **satisfied** before this step may run. Empty for every step but the ones
    #: that delete a recovery input: the two byte-exact pre-change configuration
    #: captures, and the directories that hold them.
    #:
    #: R12's cleanup loop ran every reversal whatever had happened before it, on
    #: the stated ground that *"no step's safety depends on an earlier one's
    #: success"*. That was true of the reversals and false of these: when the
    #: `install` restoring `pg_hba.conf` failed, the loop went on to `rm` the
    #: capture it would have been restored from, reported S-B, and left the host
    #: with the harness's authentication rules on disk and nothing to put back.
    #: A step named here is **skipped** rather than failed when its requirement
    #: is unmet, and the object it would have removed is reported as a retained
    #: recovery input with the operator procedure that uses it.
    requires_satisfied: tuple[str, ...] = ()
    #: **R16, conflict C-8.** The `REVALIDATE` step whose observation must have
    #: matched the creation's before this step may run. Empty for every step but
    #: the one reversal that removes an exclusively created object.
    #:
    #: It is separate from `requires_satisfied` because the two failures are
    #: different states. An unmet `requires_satisfied` **retains** a recovery
    #: input: the object is deliberately kept and the operator is told why, and
    #: cleanup has not failed. An unmet `requires_revalidated` is **residue**:
    #: something is at a path this run created and it is not the object this run
    #: created, so it is neither removable nor ignorable, and the run is S-B.
    requires_revalidated: str = ""
    #: **R16, conflict C-8.** The declared mutations whose applicability decides
    #: this step's, for a step that reverses nothing. Empty for every step but
    #: `REVALIDATE`, which applies exactly when the reversal it guards applies —
    #: otherwise a run that created nothing would re-read a root it never made.
    applies_with: tuple[str, ...] = ()
    #: **R16, conflict C-8.** What the executor may record from this step.
    #: `EXIT_STATUS_ONLY` for every step that removes or restores something, for
    #: the reason `plan.CommandStep` states: a step whose purpose is a side
    #: effect has no observation to make. The one exception is `REVALIDATE`,
    #: whose whole purpose **is** the observation.
    capture: CapturePolicy = CapturePolicy.EXIT_STATUS_ONLY
    #: **r6 §§1.4.5 and 2.4, C-P5.0-LAB-I-R1.** The descriptor-bound effect this
    #: step is, instead of a command. The two cleanup steps that used to be
    #: `install` and `chattr` vectors carry one and **no argument vector at
    #: all**: the executor issues the syscall itself, on a descriptor it holds.
    effect: "DescriptorEffect | None" = None
    note: str = ""

    @property
    def is_effect(self) -> bool:
        """True for a descriptor-bound cleanup step. It has no argument vector."""
        return self.effect is not None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, CleanupStepKind):
            raise PlanRefused("A cleanup step names one of the closed step kinds.")
        if not self.run_as.strip():
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} does not say which identity runs it."
            )
        if self.effect is not None:
            if not isinstance(self.effect, DescriptorEffect):
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} names an effect that is not "
                    "one of the reviewed descriptor-bound effects."
                )
            if self.argv:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} is a descriptor-bound "
                    "effect and carries an argument vector. An effect names no "
                    "executable at all."
                )
            if self.run_as != "root":
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} issues a descriptor-bound "
                    f"effect as {self.run_as!r}. The executor holds the "
                    "descriptors and issues every effect itself, as root."
                )
        elif not self.argv:
            raise PlanRefused("A cleanup step needs a command or an effect.")
        offending = sorted(set(self.argv) & FORBIDDEN_CLEANUP_TOKENS)
        if offending:
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} contains {offending}. Cleanup in "
                "this harness removes named objects one at a time; a recursive or "
                "wildcard removal cannot be expressed."
            )
        if self.refusal_required:
            if self.kind is not CleanupStepKind.VERIFY:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} is a {self.kind.value} and "
                    "requires a refusal. Only the post-reload proof is satisfied "
                    "by being refused; a restore, a reload or a removal that is "
                    "refused has failed."
                )
            if self.satisfying_statuses:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} both requires a refusal and "
                    "lists satisfying exit statuses. A step that must be refused "
                    "is satisfied by any non-zero exit and by no zero one."
                )
        elif 0 not in self.satisfying_statuses:
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} does not treat exit 0 as success."
            )
        if self.kind is CleanupStepKind.REVALIDATE:
            if self.mutation_ids or self.removes:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} is a revalidation and claims "
                    "to reverse a mutation. It reads two numbers and removes "
                    "nothing; the removal is the step it guards."
                )
            if not self.applies_with:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} is a revalidation and names "
                    "no mutation whose applicability decides its own. A "
                    "revalidation that ran unconditionally would re-read a path "
                    "this run may never have created."
                )
            if self.capture is CapturePolicy.EXIT_STATUS_ONLY:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} is a revalidation that "
                    "records only its exit status. Its whole purpose is the "
                    "identity it reads back, and an exit status does not carry "
                    "one."
                )
        elif self.capture is not CapturePolicy.EXIT_STATUS_ONLY:
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} is a {self.kind.value} and would "
                "record more than its exit status. A step whose purpose is a "
                "side effect has no observation to make."
            )
        if self.applies_with and self.kind is not CleanupStepKind.REVALIDATE:
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} is a {self.kind.value} and names "
                "the mutations whose applicability decides its own. Every other "
                "kind decides that from the mutations it reverses."
            )
        if self.requires_revalidated and self.kind is not CleanupStepKind.REVERSAL:
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} is a {self.kind.value} and "
                "requires a revalidation. Only a removal has to prove it is "
                "removing the object this run created."
            )
        if self.kind in (
            CleanupStepKind.RELOAD,
            CleanupStepKind.VERIFY,
            CleanupStepKind.REVALIDATE,
        ):
            if self.mutation_ids or self.removes:
                raise PlanRefused(
                    f"Cleanup step {self.step_id!r} is a {self.kind.value} and "
                    "claims to reverse a mutation. It removes nothing: it makes "
                    "the restores that precede it effective, and proves that it "
                    "did — or, for a revalidation, it proves that the object the "
                    "next step removes is the object this run created."
                )
        elif not self.mutation_ids:
            raise PlanRefused(
                f"Cleanup step {self.step_id!r} reverses no declared mutation. "
                "Every cleanup command in this harness is generated from one."
            )

    @property
    def is_recovery_input(self) -> bool:
        """Whether this step deletes something an operator recovery would need."""
        return bool(self.requires_satisfied)

    def is_satisfied_by(self, exit_status: int) -> bool:
        """Whether this exit status means the step did what it had to.

        Deliberately not *"exited zero"*: `rmdir` on an absent directory and a
        post-reload connection that was correctly refused are both non-zero, and
        one of them is the only evidence that the temporary mapping is gone.
        """
        if self.refusal_required:
            return exit_status != 0
        return exit_status in self.satisfying_statuses


def _rm_file(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    path = target.contained_path(mutation.identifier)
    return (
        ("/usr/bin/rm", "--force", "--", path),
        path,
        (0,),
        "`--force` exits 0 on an absent file, which is what makes the step re-runnable.",
    )


def _rmdir(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    # `root_or_contained_path` rather than `contained_path`: the run creates its
    # own root, so cleanup has to be able to remove it. One extra path, and
    # `rmdir` still removes only an empty directory (conflict C-1).
    path = target.root_or_contained_path(mutation.identifier)
    return (
        ("/usr/bin/rmdir", "--", path),
        path,
        (0,),
        "`rmdir` removes only an empty directory, so an artifact the plan did not "
        "declare is left in place and reported as residue rather than deleted. Its "
        "non-zero exit on an already-absent directory destroys nothing, which is "
        "the sense in which this step is re-runnable.",
    )


def _revalidate_root(
    target: DisposableTarget, step_id: str, mutation: Mutation
) -> "CleanupStep":
    """**R16, conflict C-8.** Read the created root's identity back before removal.

    `mkroot` reported the device and inode of the directory its `mkdir(2)`
    created. This reads them again, through the same reviewed bytes run from the
    same bootstrap location, with `O_DIRECTORY|O_NOFOLLOW` so a symbolic link or
    a non-directory at the path is a refusal rather than a redirection. The
    executor compares the two observations and runs the `rmdir` only when they
    agree.

    That is what makes ownership a property of the **object** rather than of the
    name. A path that was replaced between the creation and the cleanup — the
    directory removed and a different one, or a symbolic link, put there — does
    not inherit permission to have its replacement deleted: the comparison fails,
    the removal is skipped, and the path is reported as residue for §2.13.2b's
    operator recovery.

    The residual window is stated rather than glossed. `rmdir(2)` takes a path
    and not a descriptor, so a replacement performed between this reading and the
    removal is not detectable by this design; what is closed is the far larger
    window between the creation and the cleanup, which is the whole of the run.
    """
    return CleanupStep(
        step_id=step_id,
        kind=CleanupStepKind.REVALIDATE,
        run_as="root",
        argv=build_bootstrap_vector(target, "statroot", target.root_path),
        applies_with=(mutation.mutation_id,),
        capture=CapturePolicy.CASE_RESULT,
        satisfying_statuses=(0,),
        note=(
            "Reads the disposable root's device and inode through the reviewed "
            "case program's bootstrap copy. The executor compares them with the "
            "values `mkroot` reported; a disagreement, an unreadable observation "
            "or any non-zero exit skips the removal and reports the path as "
            "residue rather than deleting an object this run did not create."
        ),
    )


def _clear_attributes(target: DisposableTarget, mutation: Mutation) -> "_Reversed":
    """**L3's first half**, replacing `chattr -ia`.

    `chattr -ia` resolved the pathname inside a tool this design does not own,
    so the flags were cleared on whatever the name meant at that instant. The
    effect clears them on the inode a held descriptor refers to, after a
    pre-check that requires the identity the creating step recorded and refuses
    on anything but equality — PR-20260913-LABI-2.

    Both flags are cleared in one effect before the file is removed, as
    §2.13.2a's `finally` does, and that is why a removal failure is a *reported*
    residue rather than a silent one.
    """
    path = target.contained_path(mutation.identifier)
    parent, _, name = path.rpartition("/")
    return _Reversed(
        argv=(),
        removes=path,
        satisfying=(0,),
        note=(
            "Both inode flags are cleared on the held descriptor before the "
            "file is removed — §2.13.2a's `finally` does the same, and it is "
            "why a removal failure is a *reported* residue rather than a "
            "silent one."
        ),
        effect=DescriptorEffect(
            kind=EffectKind.CLEAR_FLAG,
            directory_role=parent.rpartition("/")[2],
            name=name,
            path=path,
            flags=("immutable", "append_only"),
        ),
    )


def _userdel(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    return (
        ("/usr/sbin/userdel", mutation.identifier),
        mutation.identifier,
        (0, 6),
        "`userdel` exits 6 when the account does not exist.",
    )


def _groupdel(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    return (
        ("/usr/sbin/groupdel", mutation.identifier),
        mutation.identifier,
        (0, 6),
        "`groupdel` exits 6 when the group does not exist.",
    )


def _remove_membership(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    return (
        ("/usr/sbin/gpasswd", "--delete", mutation.identifier, mutation.group),
        f"{mutation.identifier}@{mutation.group}",
        (0, 3),
        "`gpasswd --delete` exits 3 when the member is already absent.",
    )


def _drop_role(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    return (
        (
            "/usr/bin/psql",
            "--no-psqlrc",
            # `--no-password` on every psql vector in this package: a cleanup step
            # that prompts is a cleanup step that hangs, and a hung cleanup is
            # state S-B for a reason that has nothing to do with the host.
            "--no-password",
            "--set",
            "ON_ERROR_STOP=1",
            "--host",
            target.postgres_socket_directory,
            "--dbname",
            target.database_name,
            "--command",
            f"DROP ROLE IF EXISTS {mutation.identifier}",
        ),
        mutation.identifier,
        (0,),
        "`IF EXISTS` is the idempotence, and it is in the statement rather than in "
        "a wrapper that would have to parse an error message.",
    )


def _drop_database(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    return (
        (
            "/usr/bin/psql",
            "--no-psqlrc",
            "--no-password",
            "--set",
            "ON_ERROR_STOP=1",
            "--host",
            target.postgres_socket_directory,
            "--dbname",
            "postgres",
            "--command",
            f"DROP DATABASE IF EXISTS {mutation.identifier}",
        ),
        mutation.identifier,
        (0,),
        "Dropped from `postgres`, because a session connected to the database "
        "being dropped refuses.",
    )


def _restore_config(target: DisposableTarget, mutation: Mutation) -> "_Reversed":
    """**L1**, replacing `install <capture> <live>` — r6 §2.4's verify-and-write.

    The `install` this replaces read the capture under the disposable root,
    whose custody is the custody in question, and reported a restoration from a
    successful copy. The effect reads the **independent** store instead,
    verifies the stored bytes against the record that binds them to *this*
    destination, writes every temporary and synchronizes it before any rename,
    and reports `renamed` and `durable` as two separate facts — so a rename
    whose directory barrier failed is not a durable restoration and the reload
    verification does not run on it.
    """
    filename = mutation.file_path.rsplit("/", 1)[-1]
    live = target.config_path(filename)
    return _Reversed(
        argv=(),
        removes=live,
        satisfying=(0,),
        note=(
            "Restoration verifies the byte-exact pre-change capture in the "
            "independent recovery store against the record binding it to this "
            "destination, then writes and publishes it durably. It restores the "
            "file and nothing else: the running server keeps the harness's "
            "rules in memory until the reload step that follows every restore."
        ),
        effect=DescriptorEffect(
            kind=EffectKind.RESTORE_CONFIGURATION,
            configuration_role=CONFIGURATION_ROLE,
            components=(filename,),
            path=live,
            mode=0o640,
            owner="postgres",
            group="postgres",
        ),
    )


def _stop_unit(target: DisposableTarget, mutation: Mutation) -> tuple[tuple[str, ...], str, tuple[int, ...], str]:
    return (
        ("/usr/bin/systemctl", "stop", mutation.identifier),
        mutation.identifier,
        (0, 5),
        "A transient unit is gone once it exits; `stop` on an absent unit exits 5.",
    )


class _Reversed(NamedTuple):
    """What one reversal is: a command, or a descriptor-bound effect.

    The eight command reversals return four values and `effect` defaults to
    `None`; the two that r6 §6.4 moved off `install` and `chattr` return an
    effect and an **empty** argument vector. One shape, so the derivation below
    reads one thing.
    """

    argv: tuple[str, ...]
    removes: str
    satisfying: tuple[int, ...]
    note: str
    effect: DescriptorEffect | None = None


_Reversal = Callable[
    [DisposableTarget, Mutation],
    tuple[tuple[str, ...], str, tuple[int, ...], str] | _Reversed,
]

#: One reversal per mutation kind, and no kind without one.
_REVERSALS: Mapping[MutationKind, _Reversal] = {
    MutationKind.FILE: _rm_file,
    MutationKind.DIRECTORY: _rmdir,
    MutationKind.FILE_ATTRIBUTE: _clear_attributes,
    MutationKind.OS_ACCOUNT: _userdel,
    MutationKind.OS_GROUP: _groupdel,
    MutationKind.GROUP_MEMBERSHIP: _remove_membership,
    MutationKind.POSTGRES_ROLE: _drop_role,
    MutationKind.POSTGRES_DATABASE: _drop_database,
    MutationKind.POSTGRES_CONFIG_LINE: _restore_config,
    MutationKind.TRANSIENT_UNIT: _stop_unit,
}


def _require_complete_mapping(mutation: Mutation) -> tuple[str, str]:
    """The declared `(identity, role)` pair, or a refusal naming what is missing.

    EH-R3-2. `Mutation.__post_init__` already refuses an incomplete pair, so this
    cannot fire for a mutation constructed through the public API — and it is here
    anyway, because it is the last point before a value becomes a `CleanupStep`'s
    `run_as` and `--username`. R2's failure was exactly that the missing half was
    discovered *inside* `CleanupStep.__post_init__`, as a blank identity, after
    part of the plan had been built and with a message about the step rather than
    about the mutation. Nothing blank reaches a step from here.
    """
    user, role = mutation.maps_os_user, mutation.maps_postgres_role
    if not user or not role:
        raise PlanRefused(
            f"Configuration mutation {mutation.identifier!r} reached cleanup "
            f"planning with maps_os_user={user!r} and maps_postgres_role={role!r}. "
            "The post-reload proof runs as that identity and asks for that role; "
            "neither half is defaulted, and no production identity stands in for a "
            "mapping the run did not declare."
        )
    return user, role


def _mapping_id(mutation: Mutation) -> str:
    """How a temporary authentication mapping is named in a plan and a report.

    An identity and a role, and nothing else — no rule text, no address, no
    method, no credential.
    """
    user, role = _require_complete_mapping(mutation)
    return f"{user}->{role}"


def _reload_step(target: DisposableTarget, step_id: str) -> CleanupStep:
    return CleanupStep(
        step_id=step_id,
        kind=CleanupStepKind.RELOAD,
        run_as="postgres",
        argv=(
            "/usr/bin/psql",
            "--no-psqlrc",
            "--no-password",
            "--set",
            "ON_ERROR_STOP=1",
            "--host",
            target.postgres_socket_directory,
            "--dbname",
            "postgres",
            "--command",
            "SELECT pg_reload_conf()",
        ),
        note=(
            "The step that makes the restored files the server's effective "
            "configuration. It is a reload, never a restart, and it follows every "
            "restore so that one reload activates all of them. Its exit status "
            "says the signal was sent and nothing more, which is why the two "
            "verification steps below exist."
        ),
    )


def _verification_control_step(target: DisposableTarget, step_id: str) -> CleanupStep:
    return CleanupStep(
        step_id=step_id,
        kind=CleanupStepKind.VERIFY,
        run_as="postgres",
        argv=(
            "/usr/bin/psql",
            "--no-psqlrc",
            "--no-password",
            "--set",
            "ON_ERROR_STOP=1",
            "--host",
            target.postgres_socket_directory,
            "--dbname",
            "postgres",
            "--command",
            "SELECT 1",
        ),
        note=(
            "The positive control for the proof that follows. An ordinary local "
            "connection must still succeed after the reload, which excludes a "
            "stopped server, a moved socket and a configuration that failed to "
            "parse as explanations for the refusal below. It returns the constant "
            "1 and reads nothing."
        ),
    )


def _verification_refusal_step(
    target: DisposableTarget, step_id: str, mutation: Mutation
) -> CleanupStep:
    user, role = _require_complete_mapping(mutation)
    return CleanupStep(
        step_id=step_id,
        kind=CleanupStepKind.VERIFY,
        run_as=user,
        argv=(
            "/usr/bin/psql",
            "--no-psqlrc",
            "--no-password",
            "--set",
            "ON_ERROR_STOP=1",
            "--host",
            target.postgres_socket_directory,
            "--dbname",
            target.database_name,
            "--username",
            role,
            "--command",
            "SELECT 1",
        ),
        #: Empty, and required to be: this is the one step whose satisfaction is a
        #: **non-zero** exit, so listing a satisfying status would be listing a
        #: zero one. `CleanupStep.__post_init__` refuses the combination, and R2
        #: left the default `(0,)` in place here — a second way the configuration
        #: phase could not be planned, reached only once the missing mapping
        #: identity stopped refusing first (EH-R3-2).
        satisfying_statuses=(),
        refusal_required=True,
        note=(
            f"The proof that the temporary mapping {_mapping_id(mutation)} is no "
            "longer effective. It runs as that OS identity, asks for that role, "
            "and must be refused; a zero exit means the restored files have not "
            "taken effect. `--no-password` is what keeps it bounded and "
            "non-interactive: it never prompts, so it cannot hang and no "
            "credential is supplied or read. It runs **before** the role is "
            "dropped, so the refusal is attributable to the removed mapping "
            "rather than to a role that no longer exists."
        ),
    )


#: Why a derived cleanup step was **not** run. A closed vocabulary: each entry
#: is a complete explanation on its own, and none interpolates a host value.
#: **R13, EH-R13-1 and EH-R13-2.**
NOT_ATTEMPTED = (
    "the run did not reach the mutation this step reverses, so there is nothing "
    "of this run's for it to remove"
)
NOT_OWNED = (
    "no baseline observation proved this object absent before the run changed "
    "anything, so it is not this run's to remove"
)
OWNERSHIP_WITHDRAWN = (
    "the step that would have created this object reported that it already "
    "existed, so this run did not create it and may not delete it"
)
CONFIGURATION_NOT_REACHED = (
    "no configuration restore applies to this run, so there is nothing for this "
    "step to make effective or to prove"
)
RECOVERY_INPUT_RETAINED = (
    "this object is a recovery input for a configuration restoration that was "
    "not proved complete, so it is retained rather than removed"
)


@dataclass(frozen=True, slots=True)
class SkippedCleanupStep:
    """One derived cleanup step that was deliberately not run, and why.

    It is reported rather than merely omitted. A cleanup that quietly ran fewer
    steps than the plan declares is indistinguishable from one that ran them all
    and found nothing, and the two mean opposite things about what is on the
    host.
    """

    step_id: str
    #: The object the step would have removed or restored, by absolute path or
    #: bare name. Empty for a reload or a verification.
    subject: str
    reason: str

    def __post_init__(self) -> None:
        if not self.step_id.strip() or not self.reason.strip():
            raise PlanRefused("A skipped cleanup step names itself and its reason.")


@dataclass(frozen=True, slots=True)
class CleanupApplicability:
    """Which derived cleanup steps this run may run, and which it may not.

    **Blocking finding EH-R13-1.** R12 ran the entire declared cleanup once any
    mutation had been attempted, so a run that stopped on its second `groupadd`
    deleted three groups it never reached and dropped a database no step had
    created. The reached-mutation list existed and was recorded; nothing read it.

    Filtering to the attempted mutations is necessary and is not sufficient, and
    that is the other half of the finding: a `groupadd` that exits 9 **did**
    attempt its mutation and reported that the object was already there. So a
    step runs only when its mutation was attempted **and** a baseline step
    proved the object absent beforehand **and** no creation reported it
    pre-existing.
    """

    steps: tuple[CleanupStep, ...]
    skipped: tuple[SkippedCleanupStep, ...]

    @property
    def restores_configuration(self) -> bool:
        return any(step.kind is CleanupStepKind.RESTORE for step in self.steps)

    def declared_files(self) -> tuple[str, ...]:
        return tuple(
            step.removes
            for step in self.steps
            if step.kind is CleanupStepKind.RESTORE
        )

    def declared_mappings(self) -> tuple[str, ...]:
        return tuple(
            f"{step.run_as}->{step.argv[step.argv.index('--username') + 1]}"
            for step in self.steps
            if step.kind is CleanupStepKind.VERIFY and step.refusal_required
        )


@dataclass(frozen=True, slots=True)
class CleanupPlan:
    """Every declared mutation's reversal, plus the configuration phase.

    Order: every configuration restore, then the single reload, then the bounded
    post-reload verification, then every other reversal in the exact reverse of
    the order the mutations were declared. Hoisting the configuration phase to
    the front is what puts the drop steps — and every other step that talks to
    PostgreSQL — under the *restored* authentication rules rather than under the
    harness's temporary ones.
    """

    target: DisposableTarget
    steps: tuple[CleanupStep, ...]

    @classmethod
    def for_mutations(
        cls, target: DisposableTarget, mutations: Sequence[Mutation]
    ) -> "CleanupPlan":
        """Every declared mutation's reversal, validated before any step exists.

        The whole declaration is checked against the target **first** — EH-R3-2.
        A mutation this target does not admit, or a configuration mutation whose
        authentication mapping is incomplete, is refused before one step is built,
        so a refusal names the mutation that is wrong rather than the step that
        could not be assembled out of it. Half a plan is not a smaller plan; it is
        a plan whose ordering, restores and verification nobody can inspect.
        """
        target.require_mutable()
        declared = tuple(mutations)
        for mutation in declared:
            mutation.validate_against(target)
        config = [m for m in declared if m.kind is MutationKind.POSTGRES_CONFIG_LINE]
        others = [m for m in declared if m.kind is not MutationKind.POSTGRES_CONFIG_LINE]

        steps: list[CleanupStep] = []

        def add(step_factory) -> None:
            steps.append(step_factory(f"CL-{len(steps) + 1:02d}"))

        # 1. Restore every captured configuration file, one step per file. Two
        #    lines written into the same file share one restore: the capture is
        #    byte-exact and whole-file, so reinstalling it twice would restore
        #    the same bytes twice.
        by_file: dict[str, list[Mutation]] = {}
        for mutation in reversed(config):
            by_file.setdefault(mutation.file_path, []).append(mutation)
        for file_path, group in by_file.items():
            argv, removes, satisfying, note, effect = _restore_config(
                target, group[0]
            )
            add(lambda step_id, argv=argv, removes=removes, satisfying=satisfying,
                note=note, group=group, effect=effect: CleanupStep(
                    step_id=step_id,
                    kind=CleanupStepKind.RESTORE,
                    run_as="root",
                    argv=argv,
                    effect=effect,
                    removes=removes,
                    mutation_ids=tuple(m.mutation_id for m in group),
                    satisfying_statuses=satisfying,
                    note=note,
                ))

        # 2 and 3. One reload after every restore, then the control and the proof.
        if config:
            add(lambda step_id: _reload_step(target, step_id))
            add(lambda step_id: _verification_control_step(target, step_id))
            seen: set[str] = set()
            for mutation in config:
                mapping = _mapping_id(mutation)
                if mapping in seen:
                    continue
                seen.add(mapping)
                add(lambda step_id, mutation=mutation: _verification_refusal_step(
                    target, step_id, mutation
                ))

        # **R13, EH-R13-2.** Everything the configuration phase produced, in
        # order. A step that deletes one of the byte-exact captures those
        # restores read from may not run until every one of these has been
        # observed satisfied: the restore that reinstalls the file, the single
        # reload that makes it the server's effective configuration, and the two
        # post-reload observations that prove it is. Until then the capture is
        # the only thing an operator could recover the original configuration
        # from, and deleting it is not cleanup.
        configuration_phase = tuple(step.step_id for step in steps)
        capture_paths = {
            target.contained_path(
                f"{target.root_path}/before/{m.file_path.rsplit('/', 1)[-1]}"
            )
            for m in config
        }

        def recovery_requirement(path: str) -> tuple[str, ...]:
            """`configuration_phase` when this path is a capture or holds one."""
            if not configuration_phase:
                return ()
            if path in capture_paths:
                return configuration_phase
            if any(capture.startswith(f"{path}/") for capture in capture_paths):
                # A directory that still holds a retained capture. `rmdir` would
                # fail on it anyway and be reported as residue; skipping it
                # deliberately says *why* it is still there, which is the
                # difference between a reported retention and an unexplained one.
                return configuration_phase
            return ()

        # 4. Everything else, in reverse declaration order.
        for mutation in reversed(others):
            reversal = _REVERSALS.get(mutation.kind)
            if reversal is None:  # pragma: no cover - the table is exhaustive
                raise PlanRefused(
                    f"Mutation kind {mutation.kind.value!r} has no reversal, so it "
                    "cannot be declared."
                )
            argv, removes, satisfying, note, effect = _Reversed(
                *reversal(target, mutation)
            )
            # **R16, conflict C-8.** The one object this run creates
            # **exclusively** is the disposable root, and it is the one whose
            # removal has to prove it is removing what the run made. The
            # revalidation is generated immediately before it — which is the end
            # of the plan, because the root is declared first and reversals run
            # in reverse declaration order, so every path under it has already
            # been removed by the time this runs.
            revalidation_id = ""
            if (
                mutation.kind is MutationKind.DIRECTORY
                and mutation.identifier == target.root_path
            ):
                revalidation_id = f"CL-{len(steps) + 1:02d}"
                add(
                    lambda step_id, mutation=mutation: _revalidate_root(
                        target, step_id, mutation
                    )
                )
            # **EH-R4-2.** A `psql` reversal runs as `postgres`, not as `root`.
            # Every reversal used to be attributed to `root`, and a `psql`
            # invocation as `root` over the local socket asks peer authentication
            # for a PostgreSQL role called `root`, which the disposable instance
            # does not have — so `DROP ROLE` and `DROP DATABASE` would have been
            # refused for an authentication reason, cleanup would not have
            # completed, and the run would have reported S-B for a defect in its
            # own plan. The identity is derived from the executable rather than
            # written per entry, so a reversal added later cannot forget it.
            run_as = (
                "postgres" if argv and argv[0] == "/usr/bin/psql" else "root"
            )
            requires = recovery_requirement(removes)
            kind = (
                CleanupStepKind.RESTORE
                if effect is not None
                and effect.kind is EffectKind.RESTORE_CONFIGURATION
                else CleanupStepKind.REVERSAL
            )
            add(lambda step_id, argv=argv, removes=removes, satisfying=satisfying,
                note=note, mutation=mutation, run_as=run_as,
                requires=requires, effect=effect, kind=kind,
                revalidation_id=revalidation_id: CleanupStep(
                    step_id=step_id,
                    kind=kind,
                    run_as=run_as,
                    argv=argv,
                    effect=effect,
                    removes=removes,
                    mutation_ids=(mutation.mutation_id,),
                    satisfying_statuses=satisfying,
                    requires_satisfied=requires,
                    requires_revalidated=revalidation_id,
                    note=(
                        note
                        + (
                            " **R13, EH-R13-2:** this object is a recovery input "
                            "for the configuration restoration, so the step is "
                            "skipped — and the object retained and reported — "
                            "unless the restore, the reload and both post-reload "
                            "observations were satisfied."
                            if requires
                            else ""
                        )
                    ),
                ))

        plan = cls(target=target, steps=tuple(steps))
        if not plan.ordering_holds():  # pragma: no cover - built in this order
            raise PlanRefused(
                "The generated cleanup does not restore, reload and verify before "
                "the steps whose safety depends on the restored configuration."
            )
        return plan

    # -- the phases, named so the ordering rules can be checked ---------------

    def applicable(
        self,
        *,
        attempted: Sequence[str],
        owned: Sequence[str],
        withdrawn: Sequence[str] = (),
    ) -> CleanupApplicability:
        """The subset of this plan a run may actually carry out — **EH-R13-1**.

        A **reversal or restore** applies when every mutation it reverses was
        attempted, was proved absent by a baseline before anything changed, and
        had no creation report it already there. All three, and in that order of
        reading: attempted without ownership is *"somebody else's object"*, and
        ownership without an attempt is *"an object this run never made"*.

        The **reload** and the two **verifications** remove nothing; they make
        the restores that precede them effective and prove that they are. They
        therefore apply exactly when a restore applies, which is the other half
        of the finding: R12 reloaded PostgreSQL's configuration and ran the
        post-reload proof because an OS-group creation had been attempted.
        """
        attempted_set = set(attempted)
        owned_set = set(owned)
        withdrawn_set = set(withdrawn)
        keep: list[CleanupStep] = []
        skipped: list[SkippedCleanupStep] = []
        restores_apply = False
        for step in self.steps:
            if step.kind in (CleanupStepKind.RELOAD, CleanupStepKind.VERIFY):
                continue
            reason = ""
            # **R16, conflict C-8.** A revalidation reverses nothing, so its
            # applicability is decided by the mutations it names in
            # `applies_with` — the removal it guards. Deciding it from its own
            # (empty) mutation set would run it on a host where nothing was
            # created.
            subjects = set(step.mutation_ids) | set(step.applies_with)
            if not subjects <= attempted_set:
                reason = NOT_ATTEMPTED
            elif subjects & withdrawn_set:
                reason = OWNERSHIP_WITHDRAWN
            elif step.kind in (
                CleanupStepKind.REVERSAL,
                CleanupStepKind.REVALIDATE,
            ) and not (subjects <= owned_set):
                # A **restore** needs no absence baseline: it reinstalls a
                # byte-exact capture over a file that was there before the run,
                # which is the opposite claim, and the executor already refuses
                # to write the file at all unless that capture step was
                # satisfied.
                reason = NOT_OWNED
            if reason:
                skipped.append(
                    SkippedCleanupStep(step.step_id, step.removes, reason)
                )
                continue
            keep.append(step)
            if step.kind is CleanupStepKind.RESTORE:
                restores_apply = True

        ordered: list[CleanupStep] = []
        for step in self.steps:
            if step.kind in (CleanupStepKind.RELOAD, CleanupStepKind.VERIFY):
                if restores_apply:
                    ordered.append(step)
                else:
                    skipped.append(
                        SkippedCleanupStep(
                            step.step_id, step.removes, CONFIGURATION_NOT_REACHED
                        )
                    )
            elif step in keep:
                ordered.append(step)
        return CleanupApplicability(
            steps=tuple(ordered),
            skipped=tuple(
                sorted(skipped, key=lambda item: item.step_id)
            ),
        )

    def steps_of_kind(self, kind: CleanupStepKind) -> tuple[CleanupStep, ...]:
        return tuple(step for step in self.steps if step.kind is kind)

    @property
    def restore_steps(self) -> tuple[CleanupStep, ...]:
        return self.steps_of_kind(CleanupStepKind.RESTORE)

    @property
    def reload_steps(self) -> tuple[CleanupStep, ...]:
        return self.steps_of_kind(CleanupStepKind.RELOAD)

    @property
    def verification_steps(self) -> tuple[CleanupStep, ...]:
        return self.steps_of_kind(CleanupStepKind.VERIFY)

    def restored_config_files(self) -> tuple[str, ...]:
        return tuple(step.removes for step in self.restore_steps)

    def verified_mappings(self) -> tuple[str, ...]:
        """The mappings the plan would prove ineffective, `identity->role`."""
        return tuple(
            f"{step.run_as}->{step.argv[step.argv.index('--username') + 1]}"
            for step in self.verification_steps
            if step.refusal_required
        )

    def ordering_holds(self) -> bool:
        """Restore, then reload, then everything whose safety depends on it.

        Three claims, checked rather than described:

        1. every configuration restore precedes the reload;
        2. the reload precedes every verification; and
        3. the reload precedes every other step that talks to PostgreSQL — the
           `DROP ROLE` and `DROP DATABASE` reversals — so those connect under the
           restored authentication rules and not under the harness's.

        A plan with no configuration mutation has no reload, and the rules are
        vacuously satisfied because there is nothing whose safety depends on one.
        """
        reloads = [i for i, step in enumerate(self.steps)
                   if step.kind is CleanupStepKind.RELOAD]
        if len(reloads) > 1:
            return False
        if not reloads:
            return not self.restore_steps and not self.verification_steps
        reload_at = reloads[0]
        for index, step in enumerate(self.steps):
            if step.kind is CleanupStepKind.RESTORE and index > reload_at:
                return False
            if step.kind is CleanupStepKind.VERIFY and index < reload_at:
                return False
            if (
                step.kind is CleanupStepKind.REVERSAL
                and step.argv[:1] == ("/usr/bin/psql",)
                and index < reload_at
            ):
                return False
        return True

    def is_safe_to_rerun(self) -> bool:
        """No step performs a destructive act when its object is absent.

        True by construction, and asserted rather than assumed: the property is
        what makes the §2.13.2b operator recovery re-runnable, and a table entry
        that lost it would otherwise be invisible. A `psql` **reversal** has
        additionally to carry `IF EXISTS`, because that is where its idempotence
        lives; the reload and the two verification steps are re-runnable for a
        different reason — they create and remove nothing at all.
        """
        for step in self.steps:
            if step.is_effect:
                # A descriptor-bound effect is re-runnable for the reason the
                # reload is: every one of them refuses when its object is absent
                # rather than acting. The flag clear refuses at the pre-check
                # with `object-absent-at-the-pre-check`, and the restoration
                # refuses when the independent store holds no usable basis.
                continue
            if step.argv[0] not in NON_DESTRUCTIVE_WHEN_ABSENT:
                return False
            if (
                step.kind is CleanupStepKind.REVERSAL
                and step.argv[0] == "/usr/bin/psql"
                and not any("IF EXISTS" in argument for argument in step.argv)
            ):
                return False
        return True

    def removes(self) -> tuple[str, ...]:
        return tuple(step.removes for step in self.steps if step.removes)


@dataclass(frozen=True, slots=True)
class ConfigurationRestoration:
    """What cleanup achieved for the **running server's** configuration.

    EH-R2-2: filesystem restoration is not restoration of effective
    configuration, so "cleanup completed" cannot be decided from the reversal
    steps alone. This value carries the four facts that decide it — which files
    the plan declared and which were actually restored, whether the reload was
    attempted and succeeded, whether the post-reload control connected, and which
    of the declared mappings were actually observed to be refused.

    Every unknown is `None` rather than `False`, and every `None` is a problem:
    an unmade observation is not a passed one. `nothing_to_restore` is the one
    case with no problems at all, and it is the honest one — a run that declared
    no configuration mutation changed no configuration and needs no reload.
    """

    #: The configuration files the plan declared a mutation against.
    declared_files: tuple[str, ...] = ()
    #: The files observed reinstalled from their byte-exact pre-change capture.
    restored_files: tuple[str, ...] = ()
    #: `identity->role` for every temporary mapping the plan declared.
    declared_mappings: tuple[str, ...] = ()
    #: `identity->role` for every mapping observed refused after the reload.
    mappings_proven_ineffective: tuple[str, ...] = ()
    #: `None` when no reload was attempted.
    reload_succeeded: bool | None = None
    #: `None` when no post-reload control connection was attempted.
    verification_control_succeeded: bool | None = None

    @classmethod
    def declared_by(cls, plan: CleanupPlan) -> "ConfigurationRestoration":
        """The declared half, taken from the plan, with nothing observed yet.

        A run that reports its result starts from this and fills in what it saw,
        so the two halves cannot drift: what has to be restored comes from the
        plan, and what was restored comes from the run.
        """
        return cls(
            declared_files=plan.restored_config_files(),
            declared_mappings=plan.verified_mappings(),
        )

    @property
    def nothing_to_restore(self) -> bool:
        return not self.declared_files and not self.declared_mappings

    def problems(self) -> tuple[str, ...]:
        """Every unresolved effective-configuration risk, in a fixed order."""
        if self.nothing_to_restore:
            return ()
        problems: list[str] = []
        unrestored = [f for f in self.declared_files if f not in self.restored_files]
        for path in unrestored:
            problems.append(
                f"{path} was not restored from its pre-change capture, so the "
                "harness's authentication rules are still on disk."
            )
        if self.reload_succeeded is None:
            problems.append(
                "No reload was attempted. PostgreSQL parses pg_hba.conf and "
                "pg_ident.conf at startup and on SIGHUP, so restoring the files "
                "without reloading leaves the harness's rules effective in the "
                "running server."
            )
        elif not self.reload_succeeded:
            problems.append(
                "SELECT pg_reload_conf() did not succeed, so the restored files "
                "are not the server's effective configuration."
            )
        if self.verification_control_succeeded is None:
            problems.append(
                "No post-reload observation was made. A zero exit from the reload "
                "says the signal was sent; it does not say PostgreSQL accepted the "
                "restored configuration or that it is in force."
            )
        elif not self.verification_control_succeeded:
            problems.append(
                "The post-reload control connection did not succeed, so nothing "
                "observed after the reload attributes anything: a refusal beside a "
                "failed control is consistent with a stopped server."
            )
        for mapping in self.declared_mappings:
            if mapping not in self.mappings_proven_ineffective:
                problems.append(
                    f"The temporary mapping {mapping} was not observed to be "
                    "refused after the reload, so it may still be effective."
                )
        return tuple(problems)

    @property
    def is_complete(self) -> bool:
        return not self.problems()


@dataclass(frozen=True, slots=True)
class CleanupOutcome:
    """Which of §2.13.2b's three states the run left the host in.

    `S-A` — a probe-stage failure with cleanup complete. `S-B` — cleanup could not
    complete; the residue is named by absolute path, the effective-configuration
    risk is named in full, and **the next invocation refuses rather than cleaning
    it**. `S-C` — everything passed and cleanup completed.
    """

    state: str
    exit_code: int
    residue: tuple[str, ...]
    message: str
    #: Every unresolved effective-configuration risk. Non-empty only in S-B, and
    #: sufficient on its own to produce S-B: a temporary authentication rule that
    #: may still be in force is residue that has no path.
    configuration_risk: tuple[str, ...] = ()
    #: **R13, EH-R13-1.** Objects the derived cleanup deliberately did **not**
    #: remove because they are not this run's: a subject no baseline proved
    #: absent, or one whose creation reported it already there. They are not
    #: residue — this run did not make them — and they are reported because an
    #: operator reading *"cleanup complete"* beside an object of that name on the
    #: host needs to know which of the two it is.
    preserved: tuple[str, ...] = ()
    #: **R13, EH-R13-2.** Objects retained because a configuration restoration
    #: was not proved complete and they are what an operator would restore from.
    #: Always accompanied by `configuration_risk`, and by the procedure below.
    retained_recovery_inputs: tuple[str, ...] = ()
    #: The bounded operator procedure for the retained inputs above, or empty.
    recovery_procedure: tuple[str, ...] = ()
    #: The operator procedure for residue left by failed removal, or empty.
    #: Kept separate from configuration recovery because the two procedures
    #: address different states and must not be merged.
    residue_recovery_procedure: tuple[RecoveryStep, ...] = ()

    @property
    def cleanup_state(self) -> CleanupState:
        if self.residue or self.configuration_risk:
            return CleanupState.RESIDUE
        return CleanupState.CLEAN


#: The bounded procedure an operator follows when a configuration restoration
#: could not be proved complete and its byte-exact captures were therefore
#: retained. Four steps, in order, each naming an object the plan already
#: declares — **R13, EH-R13-2**. It states what to do and does not do it: §2.13.2b
#: is explicit that residue is never automatically cleaned, and a harness that
#: offered to finish its own failed restoration would be offering a second pass
#: over the step that just failed.
RECOVERY_PROCEDURE = (
    "1. Do not re-run the harness. The next invocation refuses while this is "
    "unresolved, and that refusal is the point.",
    "2. The byte-exact pre-change captures are retained **outside the "
    "disposable root**, under `/var/lib/freedom-blades/recovery/<run-id>/`, "
    "root-owned 0400, with a record binding each copy's SHA-256 to its "
    "destination and to the source identity it was taken from. The run "
    "directory's entry in the recovery parent is durable, so listing that "
    "parent finds it after a restart. Read the record, verify the copy against "
    "it, and compare with the live file before doing anything else. Do not use "
    "the copies under the disposable root's `before/` directory: their custody "
    "depends on the root whose safety is in question. If the independent store "
    "holds no usable basis for this run, keep the host blocked and obtain "
    "operator direction rather than continuing automatically.",
    "3. Write each verified copy over its live file as root, mode 0640, owner "
    "and group `postgres`, through the reviewed verify-and-write path — one "
    "held buffer to a temporary, synchronized, renamed, then the destination "
    "directory's entry synchronized — and only then reload with `SELECT "
    "pg_reload_conf()` as `postgres`. A rename whose directory barrier did not "
    "return success is not a durable restoration and the reload does not "
    "follow it.",
    "4. Confirm the temporary mapping is gone: an ordinary local connection as "
    "`postgres` must still succeed, and a connection as the temporary OS "
    "identity asking for the temporary role must be refused. Only then remove "
    "the run's directory under `/var/lib/freedom-blades/recovery/`, and only "
    "after the reservation has released without quarantine. A quarantined "
    "run's directory is never removed automatically.",
)


def _named_procedures(
    residue_procedure: tuple[RecoveryStep, ...],
    configuration_procedure: tuple[str, ...],
) -> list[str]:
    """Name the recovery each present cause calls for, in the operator's text.

    §2.13.2b requires an S-B run to **report** the named operator recovery, and
    the reader of that report is an operator looking at a non-zero exit rather
    than at `CleanupOutcome`'s fields. Carrying the procedures in the structured
    result and naming neither in the message would satisfy the field and not the
    requirement — the same gap LAB-1 named, one surface further out.

    Each procedure is named only when its own cause is present, and the two are
    listed separately because they are different procedures for different
    states. Runner contract r6 §8.1.
    """
    named: list[str] = []
    if residue_procedure:
        named.append(
            "The named operator recovery for the residue is the "
            f"{len(residue_procedure)}-step procedure in "
            "`journal.RECOVERY_PROCEDURE`, carried on this result as "
            "`residue_recovery_procedure`: "
            + " ".join(f"({step.order}) {step.action}." for step in residue_procedure)
        )
    if configuration_procedure:
        named.append(
            "The named operator recovery for the configuration is the separate "
            f"{len(configuration_procedure)}-step procedure in "
            "`cleanup.RECOVERY_PROCEDURE`, carried on this result as "
            "`recovery_procedure`. It is not a substitute for the residue "
            "procedure and neither answers for the other."
        )
    return named


def classify_cleanup(
    *,
    probe_passed: bool,
    unremoved: Sequence[str],
    configuration: ConfigurationRestoration,
    preserved: Sequence[str] = (),
    retained_recovery_inputs: Sequence[str] = (),
) -> CleanupOutcome:
    """The §2.13.2b state machine, with its claims kept separate.

    *"No generation or database artifact"* is unconditional. *"No transient
    residue"* is conditional on cleanup succeeding, and revision 8 stated it as
    though it were unconditional — which is the defect §2.13.2b exists to correct.

    EH-R2-2 adds the third claim, which the previous version made silently and
    without evidence: *"the temporary authentication configuration is no longer
    effective"*. It is conditional on the restore, the reload **and** the
    post-reload observation, and any of the three failing or not being made is
    state **S-B** — the same state as filesystem residue, because it is the same
    thing: something this run created is still in force on the host.

    `configuration` is required rather than defaulted. A default would let a run
    that mutated `pg_hba.conf` report S-C by saying nothing about it, which is
    the shape of the finding.
    """
    residue = tuple(sorted(unremoved))
    risks = configuration.problems()
    kept = tuple(sorted(set(preserved)))
    retained = tuple(sorted(set(retained_recovery_inputs)))
    procedure = RECOVERY_PROCEDURE if retained else ()
    residue_procedure = RESIDUE_RECOVERY_PROCEDURE if residue else ()
    preserved_note = (
        " These objects were left in place deliberately: this run did not "
        "create them and does not remove them — " + ", ".join(kept) + "."
        if kept
        else ""
    )
    if residue or risks:
        parts = []
        if retained:
            parts.append(
                "The byte-exact pre-change configuration captures were retained "
                "rather than removed, because the restoration they would be used "
                "for was not proved complete: " + ", ".join(retained)
            )
        if residue:
            parts.append(
                "The next invocation refuses while these paths exist rather than "
                "cleaning them: " + ", ".join(residue)
            )
        if risks:
            parts.append(
                "The disposable PostgreSQL instance's effective configuration is "
                "not proved restored: " + " ".join(risks)
            )
        return CleanupOutcome(
            state="S-B",
            exit_code=3,
            residue=residue,
            configuration_risk=risks,
            preserved=kept,
            retained_recovery_inputs=retained,
            recovery_procedure=procedure,
            residue_recovery_procedure=residue_procedure,
            message=(
                "Cleanup did not complete. The host now requires operator recovery "
                "before another generation can be created. "
                + " ".join(parts + _named_procedures(residue_procedure, procedure))
                + preserved_note
            ),
        )
    if not probe_passed:
        return CleanupOutcome(
            state="S-A",
            exit_code=2,
            residue=(),
            preserved=kept,
            message=(
                "A probe stage failed or was inconclusive. Cleanup completed and "
                "no residue this run created remains; no generation artifact and "
                "no database row was created at any point." + preserved_note
            ),
        )
    return CleanupOutcome(
        state="S-C",
        exit_code=0,
        residue=(),
        preserved=kept,
        message=(
            "All stages passed, both transient directories were removed, and the "
            "restored PostgreSQL configuration was reloaded and observed to be in "
            "force."
            if not configuration.nothing_to_restore
            else "All stages passed and both transient directories were removed. "
                 "No configuration mutation was declared, so none had to be "
                 "restored or reloaded."
        ),
    )


__all__ = [
    "CONFIGURATION_NOT_REACHED",
    "CleanupApplicability",
    "CleanupOutcome",
    "CleanupPlan",
    "CleanupStep",
    "CleanupStepKind",
    "ConfigurationRestoration",
    "FORBIDDEN_CLEANUP_TOKENS",
    "NON_DESTRUCTIVE_WHEN_ABSENT",
    "NOT_ATTEMPTED",
    "NOT_OWNED",
    "OWNERSHIP_WITHDRAWN",
    "RECOVERY_INPUT_RETAINED",
    "RECOVERY_PROCEDURE",
    "RESIDUE_RECOVERY_PROCEDURE",
    "SkippedCleanupStep",
    "classify_cleanup",
]
