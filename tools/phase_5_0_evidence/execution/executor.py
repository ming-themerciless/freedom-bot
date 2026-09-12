"""The executing runner: a separate implementation from `plan.DryRunRunner`, and
one that cannot be reached by importing anything.

## Six gates, all at construction, all before a process exists

1. **The target is the approved one, field for field.**
   `approved_target.require_approved_target()` refuses an unassigned target, an
   unconfirmed one, and one that differs in any compared field. A near miss is
   refused as hard as a production path.
2. **The plan carries no unresolved conflict.** A plan that can run four bands
   out of six is not four sixths of the evidence: the bands it is missing include
   controls the others depend on, and a refusal beside a control that never ran
   attributes nothing.
3. **The interpreter's two reviewed facts are stated.** Every syscall-level case
   runs through one named interpreter, and the preflight that would establish it
   is the reviewed one has nothing to compare against until a maintainer states
   its SHA-256 and its resolved path and the independent reviewer verifies both
   on the host. Learning either from the run being judged would make the
   preflight a check against itself, so the constructor refuses while either is
   unconfirmed.
4. **`E7`'s ten reviewed facts are stated — R13.** `P-06` observes the harness's
   own root identity by running the `identity` verb in the final interpreted
   process. `E7` constructs nothing, so its uid, gid, complete supplementary
   set, five capability masks, `NoNewPrivs` and final securebits are facts about
   the host rather than values derived from a capability set or read out of a
   bound vector. The constructor refuses while any of them is unconfirmed, for
   the same reason gate 3 exists.
5. **The confirmation token is exact.** It is derived from the target's own
   identity, so it cannot be a stale constant, and it is compared with
   `hmac.compare_digest` so a wrong one is wrong rather than nearly right.
6. **The reviewer's digest matches the manifest recomputed from the live tree.**
   The expected value is supplied from outside; nothing here reads it from a file
   in the same tree and nothing here creates one. Edit any covered source file and
   the recomputed digest changes and the run refuses.

None of the six is a warning and none is skippable. There is no `--force`, no
environment variable and no keyword that bypasses any of them, which is the
property to check when reading this class: the constructor has no branch that
reaches the step loop without all six having held.

## What happens once it runs

Each step is revalidated **immediately before execution** — the whole argument
vector through `plan.validate_argv` against the plan's target, the executable
against the permitted set, the identity against the closed identity set, the
timeout against zero. The plan was validated when it was built; it is validated
again here because the object that reaches this loop is not obliged to be the
object that was reviewed, and one more check costs nothing. **Every cleanup step
is revalidated the same way**, immediately before it runs.

Execution stops on the first step that is not satisfied. Not *"the first
failure"* — satisfaction is what the reviewed plan says the step's exit status
must be, so a `getent` exiting 2 on an absent group is satisfied and one exiting
0 is not.

## Materializations — conflict C-4

Two steps of the reviewed design write file **content**, which no argument vector
expresses. They are `plan.MaterializeStep`s rather than `CommandStep`s, they
carry no `argv`, and they never reach the process boundary: they go to an
injected `FileMaterializer`, whose real implementation is the one place in the
harness that puts bytes on disk. Each runs immediately after the command step it
names, and each is refused unless the **byte-exact pre-change capture step it is
restored from was satisfied** — a check the plan cannot make, because whether a
step did what the plan says is a fact about a run. Responsibility for cleanup
begins before the write for exactly the reason it begins before a command: a
materialization whose outcome is never learned is treated as potentially
reached.

## Late-bound identities — conflict C-5

`capsh --uid=`, `--gid=` and `--groups=` take numbers, and the four disposable
names do not exist until Band 2 creates them. The reviewed vector therefore
carries the **names**, and each step declares its `binding.BindingSite`s. `_bind`
resolves them through the injected NSS boundary immediately before the step,
requires exactly one consistent record per name, validates the numeric form,
substitutes only the declared sites, refuses any change outside one, and then
**revalidates the complete final vector** — Option-B interpreter prefix and
case-program grammar included — before the boundary is called. It runs before
cleanup responsibility is taken on, so a run that cannot resolve an identity has
not yet touched anything for that step.

## Cleanup is guaranteed, and when responsibility begins — EH-R5-2

The previous version called the boundary inside the step loop and reached
cleanup only after the loop had exited normally. There was no `try`/`finally`
around mutation-bearing execution, so an unexpected `OSError`, a capture or
sanitizer failure, an ordinary programming error or an operator's `Ctrl-C` after
a mutation had been reached unwound straight past cleanup and left accounts,
groups, files, PostgreSQL objects, configuration or a transient unit behind. The
class promised the opposite. It now does it:

* **Responsibility begins before the command, not after it.** A step's declared
  mutation ids are recorded **before** the boundary is invoked, so a mutation
  whose launch outcome is unknown — the call raised, the process may or may not
  have started, the operator interrupted — is treated as *potentially reached*
  and the full derived cleanup runs. Nothing decides cleanup from what a command
  reported, because a command that reported nothing is exactly the case that
  matters.
* **Cleanup runs exactly once**, on every path: normal completion, an
  unsatisfied step, a timeout, a safe launch refusal, an ordinary exception and
  an operator interruption. `_conclude` is the single caller and refuses a second
  invocation.
* **The two facts are kept apart.** The execution failure is `RunOutcome.
  stopped_at`/`stop_reason`; the cleanup result is `RunOutcome.cleanup`. A
  cleanup that succeeded never makes a failed run look successful, and a cleanup
  that failed never erases what stopped the run.
* **Unexpected exceptions become a fixed category.** `UNEXPECTED_EXECUTION_
  FAILURE` and `OPERATOR_INTERRUPTION` are constants. No exception text, errno,
  path or account name is serialized from an exception, because the exception may
  carry any of them.
* **An interruption is never suppressed.** `KeyboardInterrupt` and `SystemExit`
  are re-raised — after cleanup has finished. Nothing here catches
  `BaseException` to stay alive.
* **A cleanup that cannot complete is S-B and says so.** If the cleanup
  machinery itself fails, the outcome names only residue the plan **declared**
  and the effective-configuration risk that follows from cleanup not having
  completed. It is never S-C, `artifact_admissible` is never true, and the next
  invocation refuses rather than cleaning it — §2.13.2b.

## What it does not do

It writes nothing. Serializing the evidence artifact is the CLI's step, and only
when `RunOutcome.artifact_admissible` is true — which requires every band's
records to satisfy the existing completeness and provenance rules, and which is
False for every run that stopped early, raised, was interrupted, or could not
prove its cleanup complete.
"""
from __future__ import annotations

import hmac
from dataclasses import dataclass, field
from typing import Sequence

from ..approved_target import CONFIRMATION_TOKEN, require_approved_target
from ..binding import BindingRefused, bind_arguments
from ..capture import CapturePolicy
from .. import capability, case_runtime
from ..case_runtime import CASE_PROGRAM_SOURCE, INTERPRETER_PATH
from ..cleanup import (
    NOT_ATTEMPTED,
    RECOVERY_INPUT_RETAINED,
    CleanupApplicability,
    CleanupOutcome,
    CleanupStep,
    CleanupStepKind,
    ConfigurationRestoration,
    SkippedCleanupStep,
    classify_cleanup,
)
from ..concrete_plan import ConcretePlan
from ..errors import PlanRefused, TargetRefused
from ..expectations import EXPECTATION_NOT_CONSTRUCTED, contract_for
from ..materialization import MAX_MATERIALIZED_BYTES
from ..plan import (
    PERMITTED_EXECUTABLES,
    CommandStep,
    MaterializeStep,
    StepRole,
    validate_argv,
)
from ..review_manifest import ReviewManifest, digests_match
from .boundary import (
    IDENTITY_CONTRACT,
    LAUNCH_BOUNDARY_FAILURE,
    LAUNCH_VALIDATION_REFUSED,
    CommandResult,
    IdentityLookup,
    IdentityRefusal,
    ProcessBoundary,
    SystemIdentityLookup,
    timeout_for,
)
from .materializer import (
    MATERIALIZATION_CAPTURE_INCOMPLETE,
    MATERIALIZATION_VALIDATION_REFUSED,
    FileMaterializer,
    MaterializationResult,
    RecordingMaterializer,
)

#: Every identity a step may run as, taken from the process boundary's own
#: credential contract so the two closed sets cannot drift. A typo is a refusal
#: rather than an unexpected transition, and blank is not a member — `""` cannot
#: default to `root` and `root` cannot default to anything.
#:
#: `freedomcoord`, `freedomsheet` and `fbprobe` are identities the run creates in
#: the disposable environment. `postgres` is the identity the database steps name.
#: It is an **existing host identity** the run never creates or modifies, and its
#: permitted membership is §2.12.2's, ruled on 2026-09-06 under change-log
#: C-P5.0-AE and read through `identity.CANONICAL_ACCOUNTS` like every other row
#: — the disposition of EH-R6-1. `discordbot` and `freedomweb` are existing host
#: identities the run **reads as** for the two positive traverse controls and
#: never modifies; `targets.validate_account_name` still refuses `postgres`,
#: `discordbot` and `freedomweb` as mutation subjects, which is the distinction
#: that matters: a step may run *as* them and may not act *on* them.
PERMITTED_RUN_AS: frozenset[str] = frozenset(IDENTITY_CONTRACT)

#: `RunOutcome.exit_code` when a gate refused. Distinct from S-A's 2 and S-B's 3
#: so *"it would not start"* is never mistaken for *"it ran and something
#: failed"*.
REFUSED_EXIT_CODE = 4

#: `stopped_at` when the run failed before it reached its first step. A step id
#: is always non-empty, so this cannot be confused with one, and `completed`
#: stays False — an exception is not a run that finished.
BEFORE_FIRST_STEP = "<before the first step>"

#: The fixed category for any exception the harness did not expect. Deliberately
#: says nothing about the exception: its message may name a path, an account, an
#: errno or a line of operating-system text, and none of those may be serialized.
UNEXPECTED_EXECUTION_FAILURE = (
    "the run stopped on an unexpected failure inside the harness. The exception "
    "is not recorded: its text may name a path, an identity or an operating-"
    "system message, and none of those may reach an artifact. Cleanup ran."
)

#: The fixed category for an operator interruption. Cleanup finishes first, and
#: the interruption then propagates unchanged.
OPERATOR_INTERRUPTION = (
    "the run was interrupted by the operator. The derived cleanup ran to "
    "completion before the interruption was allowed to propagate."
)

#: What a cleanup step records when the boundary call itself raised. The step was
#: attempted, nothing is known about what it achieved, and it is therefore not
#: satisfied — which makes its object residue.
CLEANUP_BOUNDARY_FAILURE = (
    "the cleanup step could not be completed; its object is therefore not proved "
    "removed"
)

#: **R16, conflict C-8.** The two observation keys an exclusive creation reports
#: about the object it made, and that its revalidation reads back. Named once, so
#: the value the executor stores and the value it compares cannot drift.
CREATED_IDENTITY_KEYS = ("root_device", "root_inode")

#: The fixed category a revalidation records when the object at the path is not
#: the object the creation reported. No path, no number and no operating-system
#: message: what is at that path now is exactly what this harness must not
#: describe from an unvalidated reading.
OWNERSHIP_NOT_REVALIDATED = (
    "the object at this path is not the object this run created, or its identity "
    "could not be re-read; the removal was not performed"
)

#: The fixed category the guarded removal records when its revalidation did not
#: succeed. The object is residue — it is at a path this run created and it is
#: not the thing this run created — so it is reported for §2.13.2b's operator
#: recovery and is never deleted.
REMOVAL_NOT_REVALIDATED = (
    "the removal was skipped because the object's identity was not revalidated; "
    "the path is reported as residue rather than deleted"
)

#: The fixed category for a materialization the harness did not carry out. Like
#: every other category here it names no path, no digest and no operating-system
#: message: the classification is in `MATERIALIZATION_FAILURES` and the step's
#: destination is already in the reviewed plan.
MATERIALIZATION_NOT_APPLIED = (
    "the reviewed configuration bytes were not written, so the band's "
    "post-change ordering case cannot be observed and the run stops"
)


@dataclass(frozen=True, slots=True)
class StepOutcome:
    """What one step did. Scalars and sanitized observations, and nothing else."""

    step_id: str
    band: str
    run_as: str
    argv: tuple[str, ...]
    exit_status: int
    satisfied: bool
    timed_out: bool
    observations: tuple[tuple[str, str], ...] = ()
    stderr_present: bool = False
    launch_failure: str = ""
    stop_reason: str = ""


@dataclass(frozen=True, slots=True)
class RunOutcome:
    """The whole run: what ran, what stopped it, and what cleanup left."""

    steps: tuple[StepOutcome, ...]
    cleanup_steps: tuple[StepOutcome, ...]
    cleanup: CleanupOutcome
    stopped_at: str = ""
    stop_reason: str = ""
    mutations_reached: tuple[str, ...] = ()
    #: **R13, EH-R13-1.** Every derived cleanup step this run was **not**
    #: entitled to carry out, with the fixed reason. Reported rather than
    #: omitted: a cleanup that silently ran fewer steps than the plan declares
    #: cannot be told from one that ran them all and found nothing.
    cleanup_skipped: tuple[SkippedCleanupStep, ...] = ()

    @property
    def exit_code(self) -> int:
        return self.cleanup.exit_code

    @property
    def completed(self) -> bool:
        return not self.stopped_at

    @property
    def artifact_admissible(self) -> bool:
        """Whether a final evidence artifact may be written at all.

        Three conditions, and all of them: the run was not stopped, cleanup
        reached S-C, and every step was satisfied. A run that stopped has bands
        with no observations, and `records.deserialize_records` refuses an
        artifact whose dependent cases reference a control that is not there —
        so producing one would give a file that cannot be read back, which is a
        worse outcome than not producing it.

        Every exception path sets `stopped_at`, so none of them can be admissible.
        """
        return (
            self.completed
            and self.cleanup.state == "S-C"
            and all(step.satisfied for step in self.steps)
        )


class ExecutorRefused(PlanRefused):
    """A gate refused. Nothing was executed and nothing was created."""


@dataclass(slots=True)
class _RunState:
    """What the step loop has established so far.

    It exists so that the exception handlers in `execute()` can conclude a run
    they did not finish: the outcomes recorded, the mutations that became this
    run's responsibility, and where it stopped are all here rather than in
    locals that an exception would discard.
    """

    outcomes: list[StepOutcome] = field(default_factory=list)
    mutations_reached: list[str] = field(default_factory=list)
    #: **R13, EH-R13-1.** The mutations a satisfied baseline step proved absent
    #: **before anything changed**. A cleanup step may remove an object only when
    #: its mutation is in here, because that is what makes the object this run's.
    owned: set[str] = field(default_factory=set)
    #: **R13, EH-R13-1.** The mutations whose creation reported the object was
    #: already there. Ownership is withdrawn rather than merely unclaimed: the
    #: attempt was made, so filtering by attempt alone would still delete it.
    withdrawn: set[str] = field(default_factory=set)
    #: **R16, conflict C-8.** The mutations whose exclusive creation was reached
    #: and whose outcome does not prove the host untouched: the program reported
    #: a status outside `nothing_created_statuses`, or it timed out, or it never
    #: reported at all. Something may exist at the path and this run cannot say
    #: what, so it is neither owned — nothing may remove it — nor absent. It is
    #: reported as bounded residue with the operator recovery, which is S-B.
    uncertain_creations: set[str] = field(default_factory=set)
    #: **R16, conflict C-8.** The ownership evidence an exclusive creation
    #: reported about the object it made: `root_device` and `root_inode` as
    #: `fstat(2)` gave them. Cleanup's revalidation is compared against this and
    #: against nothing else — never against a value read from the same reading it
    #: is judging.
    created_identity: dict[str, str] = field(default_factory=dict)
    failed_controls: set[str] = field(default_factory=set)
    #: The command steps that have been observed satisfied, so a materialization
    #: can require the byte-exact capture it is restored from rather than assume
    #: it. A step id, never an outcome, because the question is *"did that exact
    #: reviewed step do what the plan says?"*.
    satisfied_steps: set[str] = field(default_factory=set)
    current_step_id: str = ""
    stopped_at: str = ""
    stop_reason: str = ""

    def stop(self, step_id: str, reason: str) -> None:
        """Record the first stop only. A later cleanup failure or an exception
        raised while unwinding must not overwrite what actually stopped the run."""
        if not self.stopped_at:
            self.stopped_at = step_id or BEFORE_FIRST_STEP
            self.stop_reason = reason

    @property
    def probe_passed(self) -> bool:
        return (
            not self.stopped_at
            and bool(self.outcomes)
            and all(outcome.satisfied for outcome in self.outcomes)
        )


@dataclass(slots=True)
class ExecutingRunner:
    """Drives a reviewed `ConcretePlan` across an injected `ProcessBoundary`.

    Every dependency is injected — the boundary above all — so the entire class
    is exercised by the suite without a privileged host, and so the object that
    can actually start a process is constructed in exactly one place: the CLI's
    `--execute` branch.
    """

    plan: ConcretePlan
    boundary: ProcessBoundary
    reviewed_digest: str
    confirmation_token: str
    source_bytes: dict[str, bytes]
    #: How the two reviewed configuration files are written. It defaults to the
    #: recording implementation, which writes nothing and reports
    #: `materializer-not-armed`, so an executor assembled without one refuses the
    #: materialization, stops the run and cleans up — rather than performing it.
    materializer: FileMaterializer = field(default_factory=RecordingMaterializer)
    #: **Conflict C-5.** How the four disposable names are resolved to numbers,
    #: immediately before the step that needs them. It is the same injected seam
    #: the process boundary reads its credentials through, so there is one reader
    #: of `pwd`/`grp` in this package, one place that refuses a duplicated or
    #: self-contradicting record, and one object a test replaces to exercise every
    #: branch without touching a real account. Constructing it reads nothing.
    identity_lookup: IdentityLookup = field(default_factory=SystemIdentityLookup)
    #: Set once the run has produced residue, or once cleanup could not be proved
    #: complete. A second `execute()` on the same object refuses, because
    #: §2.13.2b's next invocation refuses while residue exists rather than
    #: cleaning it.
    _blocked_by_residue: tuple[str, ...] = field(default_factory=tuple, init=False)
    #: The derived cleanup this run was entitled to carry out, kept so the
    #: conclusion can name what it deliberately did not do — R13, EH-R13-1.
    _last_applicability: CleanupApplicability | None = field(default=None, init=False)
    #: Set when the cleanup machinery failed or was interrupted, so that what it
    #: left behind is unknown rather than merely non-empty.
    _cleanup_uncertain: bool = field(default=False, init=False)
    #: Cleanup is invoked exactly once per run, and `_conclude` is its only
    #: caller. This makes a second invocation a refusal rather than a second
    #: pass over the same destructive plan.
    _cleanup_invoked: bool = field(default=False, init=False)
    _last_outcome: RunOutcome | None = field(default=None, init=False)
    _manifest_digest: str = field(default="", init=False)
    #: The review manifest's covered-source digest for the case program, bound
    #: once the reviewer's digest has been matched. It is `P-05`'s expected
    #: `case_program_sha256`, and it is the only place that expectation comes
    #: from.
    _case_program_sha256: str = field(default="", init=False)

    def __post_init__(self) -> None:
        require_approved_target(self.plan.target)

        if not self.plan.is_executable:
            raise ExecutorRefused(
                "The plan still carries unresolved conflicts "
                f"{list(self.plan.conflicts())} across "
                f"{len(self.plan.unresolved)} steps. Running the resolved part "
                "would produce refusals with no controls beside them, which is "
                "not weaker evidence — it is evidence of nothing."
            )

        if not case_runtime.interpreter_real_path_confirmed():
            raise ExecutorRefused(
                "The expected resolved interpreter path is not a confirmed "
                "reviewed target fact: "
                "`case_runtime.EXPECTED_INTERPRETER_REAL_PATH` is "
                f"{case_runtime.EXPECTED_INTERPRETER_REAL_PATH!r}. `P-05` reports "
                "`interpreter_real`, and R12 requires every key of that "
                "observation to be compared with an expectation the observation "
                "cannot supply. A virtual environment's `bin/python` normally "
                "resolves outside the environment, so there is no rule that "
                "derives this value without either refusing the reviewed host or "
                "learning the expectation from the run being judged. Establishing "
                "it requires reading the disposable host, which is a maintainer "
                "decision and not this harness's to take."
            )

        if not case_runtime.interpreter_digest_confirmed():
            raise ExecutorRefused(
                "The expected interpreter digest is not a confirmed reviewed "
                f"target fact: `case_runtime.EXPECTED_INTERPRETER_SHA256` is "
                f"{case_runtime.EXPECTED_INTERPRETER_SHA256!r}. Every case in "
                "identity and capability bands runs through "
                f"{INTERPRETER_PATH}, and the preflight that would establish that "
                "the interpreter is the reviewed one has nothing to compare "
                "against. Establishing the digest requires reading the "
                "disposable host, which is a maintainer decision and not this "
                "harness's to take, and learning it from the run being judged "
                "would make the preflight a check against itself. The plan is "
                "fully specified; it is not runnable until the fact is stated "
                "and independently verified."
            )

        unconfirmed_e7 = capability.unconfirmed_e7_facts()
        if unconfirmed_e7:
            raise ExecutorRefused(
                "E7's reviewed target facts are not all stated for this target: "
                f"{list(unconfirmed_e7)}. `P-06` observes E7 — the harness's own "
                "root identity — by running the `identity` verb in the final "
                "interpreted process, and R13 requires every key of that "
                "observation to be compared with an expectation the observation "
                "cannot supply. E7 constructs nothing, so there is no `M` to "
                "derive a mask from and no bound vector to read a uid, gid or "
                "group list out of: each of the ten is a fact about the host, "
                "and establishing one requires reading the disposable host, "
                "which is a maintainer decision and not this harness's to take. "
                "Learning any of them from `P-01`, `P-02` or from E7's own "
                "observation would make the comparison a check against itself. "
                "The plan is fully specified; it is not runnable until the facts "
                "are stated and independently verified."
            )

        if not isinstance(self.confirmation_token, str) or not hmac.compare_digest(
            self.confirmation_token.strip(), CONFIRMATION_TOKEN
        ):
            raise ExecutorRefused(
                "The target confirmation token does not match the approved "
                "target's. The token is derived from the target's own identity, "
                "so a token that does not match names a target nobody confirmed."
            )

        manifest = ReviewManifest.build(self.plan, self.source_bytes)
        self._manifest_digest = manifest.digest()
        # **The expected case-program digest, and where it comes from.** The
        # bytes are the ones the reviewer approved: `ReviewManifest.build` hashes
        # exactly `COVERED_SOURCES` from the mapping supplied here, and the digest
        # gate below refuses unless the aggregate over them matches the value the
        # reviewer typed. So this is the manifest's own covered-source digest for
        # the reviewed source — not a hash of the installed file, and not
        # anything `P-05` reports. `install` copies bytes, so it is simultaneously
        # the installation digest, which is what makes the comparison meaningful
        # without a second reviewed fact.
        self._case_program_sha256 = manifest.digest_for(CASE_PROGRAM_SOURCE)
        if not self.reviewed_digest or not self.reviewed_digest.strip():
            raise ExecutorRefused(
                "No reviewed plan digest was supplied. The executor will not "
                "compute its own approval: the expected value is a reviewer's "
                "input, and a tree that produced its own expectation would "
                "approve itself. The digest of the plan in this tree is "
                f"{self._manifest_digest}; it is a value to submit for review, "
                "not authority to run."
            )
        if not digests_match(self.reviewed_digest, self._manifest_digest):
            raise ExecutorRefused(
                "The reviewed plan digest does not match the plan in this tree. "
                f"Reviewed {self.reviewed_digest.strip()!r}; this tree computes "
                f"{self._manifest_digest!r}. Some covered source file, argument "
                "vector, mutation, cleanup step or target fact has changed since "
                "the review, and what would run is not what was approved."
            )

    @property
    def manifest_digest(self) -> str:
        return self._manifest_digest

    @property
    def last_outcome(self) -> RunOutcome | None:
        """The outcome of the run that has finished concluding.

        It exists for the interruption path: `execute()` re-raises there, so the
        caller gets no return value, and the record of what ran and what cleanup
        left would otherwise be lost with the frame.
        """
        return self._last_outcome

    # -- per-step validation, repeated immediately before execution ----------

    def _revalidate_vector(self, argv: tuple[str, ...], run_as: str) -> str:
        """The guards every command shares, at the last possible moment. Returns
        a stop reason, empty when the command is admissible."""
        try:
            vector = validate_argv(argv, target=self.plan.target)
        except (PlanRefused, TargetRefused) as exc:
            return f"argument vector refused at execution time: {exc}"
        if vector != tuple(argv):
            return "the validated vector is not the step's vector"
        executable = vector[0]
        if not executable.startswith("/"):
            return "the executable is not an absolute path, so it would resolve through PATH"
        if executable not in PERMITTED_EXECUTABLES and executable != INTERPRETER_PATH:
            # The interpreter is the one non-distribution executable a vector may
            # name, and `validate_argv` above has already required the whole
            # vector to match the closed case-program grammar before it could get
            # here. An arbitrary program inside the disposable root is **not**
            # admissible: conflict C-2's resolution names the interpreter, so the
            # case program is an argument to it and never `argv[0]`.
            return f"{executable} is not a permitted executable"
        if run_as not in PERMITTED_RUN_AS:
            return (
                f"run_as {run_as!r} is not one of the identities this plan "
                "may assume; there is no default and blank is not a member"
            )
        if timeout_for(executable) <= 0:
            return "the step has no bounded timeout"
        return ""

    def _revalidate(self, step: CommandStep) -> str:
        """Every guard again, immediately before this step is executed."""
        refusal = self._revalidate_vector(tuple(step.argv), step.run_as)
        if refusal:
            return refusal
        if not isinstance(step.capture, CapturePolicy):
            return "the step does not declare a reviewed capture policy"
        return ""

    # -- R12: the semantic expectation, immediately after capture ------------

    def _expectation_refusal(
        self, step: CommandStep, argv: tuple[str, ...], result: CommandResult
    ) -> str:
        """Whether this step's **observation** satisfies its reviewed contract.

        This is EH-R11-1 and EH-R11-2's enforcement point, and its position is
        the finding's substance: it operates on the `CommandResult` the executor
        actually received, immediately after `capture.sanitize` and **before**
        `StepOutcome.satisfied`, `state.satisfied_steps` or any dependent
        execution decision exists. Exit status 0 is necessary and not sufficient.

        **R13, Blocking finding EH-R13-3.** *Every* policy that records an
        observation now carries a contract, and a missing, duplicated,
        unreadable, malformed, unexpected or unequal value is a refusal with a
        fixed classification that names no observed value. Only
        `EXIT_STATUS_ONLY` returns the empty string, because it records nothing.

        R12 gated two policies and left the other nine to *"the bands, which
        classify the recorded observations"* — and the execution loop never
        called a band classifier, so a `capsh` reporting an empty bounding set
        and a `getent` reporting a `freedomjournal` with an unexpected member
        were both satisfied by their exit status and every dependent step ran
        behind them. Describing a classification that happens later did not make
        it a prerequisite; calling it here does.

        A contract that cannot be **built** is also a refusal. There is no path
        through this method that reaches "satisfied" without a comparison having
        been made.
        """
        try:
            contract = contract_for(
                capture=step.capture,
                identity_name=step.identity_name,
                argv=argv,
                case_program_installed_path=case_runtime.case_program_path(
                    self.plan.target
                ),
                case_program_sha256=self._case_program_sha256,
                # **R13, EH-R13-3.** The step's own reviewed declaration, for
                # every policy whose expectation is not derived from a reviewed
                # constant. It is read from the plan the digest gate has already
                # matched, so it is the declaration Codex approved and not one
                # this run composed.
                declared=step.observation_expectations,
                subject=step.step_id,
            )
        except (PlanRefused, TargetRefused):
            # The message may name a path or an identity; the classification is
            # fixed and names neither.
            return EXPECTATION_NOT_CONSTRUCTED
        if contract is None:
            return ""
        return contract.check(result.observations)

    # -- conflict C-5: late binding, immediately before the process ----------

    def _bind(self, step: CommandStep) -> tuple[tuple[str, ...], str]:
        """The vector that will actually be executed, and any refusal.

        Four things happen here and nowhere else, in this order:

        1. the four disposable names are resolved through the **injected** NSS
           boundary, which is what refuses a missing name, a duplicated record
           and a database whose direct answer disagrees with its enumeration;
        2. `binding.bind_arguments` validates every resolved number's form and
           substitutes **only** the declared sites, refusing any change outside
           one;
        3. the complete final vector is revalidated — `plan.validate_argv`
           against the plan's target, which for a `capsh` step re-checks the
           Option-B interpreter prefix and the case-program grammar of the tail,
           plus the executable, the identity and the timeout; and
        4. only then is the vector handed to the process boundary.

        A step with no declared sites returns its own vector unchanged, which is
        every step outside §2.13.5c. Nothing is resolved for it and no lookup is
        performed, so a dry run and every test that does not exercise binding
        consult no account database at all.
        """
        if not step.bindings:
            return tuple(step.argv), ""
        try:
            bound = bind_arguments(
                step.argv,
                step.bindings,
                resolve_uid=lambda name: self.identity_lookup.account(name)[0],
                resolve_gid=self.identity_lookup.group_id,
            )
        except BindingRefused as exc:
            return (), f"late binding refused: {exc}"
        except IdentityRefusal:
            # The message may name an account, a numeric id or a group list, and
            # none of those may reach a run outcome.
            return (), (
                "late binding refused: one of the four disposable identities "
                "could not be resolved to exactly one consistent record"
            )
        refusal = self._revalidate_vector(bound, step.run_as)
        if refusal:
            return (), f"the substituted vector was refused: {refusal}"
        return bound, ""

    def _revalidate_materialization(self, step: MaterializeStep, state: _RunState) -> str:
        """Every guard again, immediately before the reviewed bytes are written.

        The plan validated this step when it was built; it is validated again
        here for the reason every other step is — the object that reaches this
        loop is not obliged to be the object that was reviewed — and with one
        check the plan cannot make: whether the byte-exact pre-change capture
        this destination is restored from was actually taken by a step that was
        satisfied.
        """
        try:
            step.validate_against(self.plan.target)
        except (PlanRefused, TargetRefused) as exc:
            return f"materialization refused at execution time: {exc}"
        if step.run_as not in PERMITTED_RUN_AS:
            return (
                f"run_as {step.run_as!r} is not one of the identities this plan "
                "may assume; there is no default and blank is not a member"
            )
        content = step.file.content
        if not content or len(content) > MAX_MATERIALIZED_BYTES:
            return "the reviewed content is empty or beyond the reviewed bound"
        if step.capture_step_id not in state.satisfied_steps:
            return (
                f"the byte-exact pre-change capture step "
                f"{step.capture_step_id!r} was not satisfied, so cleanup would "
                "have nothing to reinstall over this destination"
            )
        return ""

    def _revalidate_cleanup(self, step: CleanupStep) -> str:
        """The same guards for a cleanup step.

        Cleanup is derived, bounded and non-recursive by construction, and it is
        still revalidated: it runs the destructive half of the plan, and the
        object that reaches this loop is not obliged to be the object that was
        reviewed.
        """
        return self._revalidate_vector(tuple(step.argv), step.run_as)

    # -- the run -------------------------------------------------------------

    def execute(self) -> RunOutcome:
        """Run the reviewed plan, and clean up whatever it reached.

        The `try` covers every mutation-bearing command. There is no path out of
        this method — return, exception or interruption — that does not pass
        through `_conclude`, and `_conclude` is what invokes cleanup.
        """
        self._refuse_when_blocked()

        state = _RunState()
        try:
            self._run_steps(state)
        except (KeyboardInterrupt, SystemExit):
            # Not suppressed: cleanup finishes, and the interruption then
            # continues to the operator who asked for it.
            state.stop(state.current_step_id, OPERATOR_INTERRUPTION)
            self._conclude(state)
            raise
        except Exception:
            state.stop(state.current_step_id, UNEXPECTED_EXECUTION_FAILURE)
        return self._conclude(state)

    def _refuse_when_blocked(self) -> None:
        if self._cleanup_uncertain:
            raise ExecutorRefused(
                "A previous run could not prove its cleanup complete, so what it "
                f"left behind is unknown: {list(self._blocked_by_residue)}. "
                "§2.13.2b is explicit that the next invocation refuses while it "
                "exists and does not clean it, and an uncertain cleanup is a "
                "stronger reason to refuse than a known residue, not a weaker one."
            )
        if self._blocked_by_residue:
            raise ExecutorRefused(
                "A previous run left residue that has not been cleared by the "
                "named operator recovery procedure: "
                f"{list(self._blocked_by_residue)}. §2.13.2b is explicit that the "
                "next invocation refuses while it exists and does not clean it."
            )

    def _run_steps(self, state: _RunState) -> None:
        """The reviewed steps, in order, until one is not satisfied.

        Every exception this raises is handled by `execute()`, which concludes
        the run and therefore cleans up whatever `state.mutations_reached` says
        this run became responsible for.
        """
        for step in self.plan.steps:
            state.current_step_id = step.step_id

            refusal = self._revalidate(step)
            if refusal:
                state.stop(step.step_id, refusal)
                state.outcomes.append(
                    StepOutcome(
                        step_id=step.step_id,
                        band=step.band,
                        run_as=step.run_as,
                        argv=tuple(step.argv),
                        exit_status=-1,
                        satisfied=False,
                        timed_out=False,
                        launch_failure=LAUNCH_VALIDATION_REFUSED,
                        stop_reason=refusal,
                    )
                )
                return

            if step.role is StepRole.DEPENDENT and state.failed_controls:
                reason = (
                    "a positive control in this band did not pass, so this "
                    "dependent case is not interpreted: a refusal beside a failed "
                    "control attributes nothing"
                )
                state.stop(step.step_id, reason)
                state.outcomes.append(
                    StepOutcome(
                        step_id=step.step_id,
                        band=step.band,
                        run_as=step.run_as,
                        argv=tuple(step.argv),
                        exit_status=-1,
                        satisfied=False,
                        timed_out=False,
                        stop_reason=reason,
                    )
                )
                return

            # Conflict C-5. The declared sites are substituted here — after the
            # reviewed vector has been revalidated and **before** cleanup
            # responsibility is taken on, so a run that cannot resolve one of the
            # four disposable identities has not yet touched anything.
            argv, binding_refusal = self._bind(step)
            if binding_refusal:
                state.stop(step.step_id, binding_refusal)
                state.outcomes.append(
                    StepOutcome(
                        step_id=step.step_id,
                        band=step.band,
                        run_as=step.run_as,
                        argv=tuple(step.argv),
                        exit_status=-1,
                        satisfied=False,
                        timed_out=False,
                        launch_failure=LAUNCH_VALIDATION_REFUSED,
                        stop_reason=binding_refusal,
                    )
                )
                return

            # **R13, EH-R13-1.** Ownership is checked **before** the mutation is
            # attempted, not before it is reversed. A run that reaches a creation
            # whose subject no baseline proved absent stops here, having changed
            # nothing, rather than creating something it would later have to
            # decide whether it may delete.
            # **R16, conflict C-8.** A mutation this step owns *by creating it*
            # cannot have been owned beforehand — that is the point: there is no
            # preliminary absence check, so there is nothing to have satisfied
            # this gate. Its ownership is granted below, after the creation is
            # observed to have returned, and only then.
            unowned = [
                mutation_id
                for mutation_id in step.mutation_ids
                if mutation_id not in state.owned
                and mutation_id not in step.establishes_ownership_by_creation
            ]
            if unowned:
                reason = (
                    "no baseline observation proved this step's subject absent "
                    "before the run changed anything, so creating it would "
                    "produce an object cleanup could not tell from one that was "
                    f"already there: {sorted(unowned)}"
                )
                state.stop(step.step_id, reason)
                state.outcomes.append(
                    StepOutcome(
                        step_id=step.step_id,
                        band=step.band,
                        run_as=step.run_as,
                        argv=tuple(step.argv),
                        exit_status=-1,
                        satisfied=False,
                        timed_out=False,
                        launch_failure=LAUNCH_VALIDATION_REFUSED,
                        stop_reason=reason,
                    )
                )
                return

            # Responsibility for cleanup begins here, before the command exists.
            # A mutation whose launch outcome is never learned — the call raised,
            # the operator interrupted, the process may or may not have started —
            # is treated as potentially reached.
            if step.is_mutation_bearing:
                state.mutations_reached.extend(step.mutation_ids)

            try:
                result: CommandResult = self.boundary.run(
                    step_id=step.step_id,
                    argv=argv,
                    run_as=step.run_as,
                    capture=step.capture,
                    timeout_seconds=timeout_for(argv[0]),
                    # **R14, EH-R14-1.** The reviewed names a catalog reading
                    # answers about, taken from the plan and never from the run.
                    # `None` for every other policy, and `capture.sanitize`
                    # refuses one supplied to a policy that answers no question.
                    catalog=step.catalog_question,
                )
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                # The boundary or its sanitizer failed. The exception carries
                # host text and is dropped; the step is recorded as not started,
                # which is what a fixed classification is for.
                result = CommandResult(
                    exit_status=-1,
                    timed_out=False,
                    launch_failure=LAUNCH_BOUNDARY_FAILURE,
                )

            # **R12.** The observation is compared here, before satisfaction is
            # decided and before anything is added to `state.satisfied_steps`.
            expectation_refusal = ""
            if not result.timed_out and not result.launch_failure:
                expectation_refusal = self._expectation_refusal(step, argv, result)
            satisfied = (
                not result.timed_out
                and not result.launch_failure
                and step.is_satisfied_by(result.exit_status)
                and not expectation_refusal
            )
            reason = ""
            if result.timed_out:
                reason = "the step exceeded its bounded timeout and was killed"
            elif result.launch_failure:
                reason = f"the step could not be started: {result.launch_failure}"
            elif not step.is_satisfied_by(result.exit_status):
                reason = self._unsatisfied_reason(step, result.exit_status)
            elif expectation_refusal:
                reason = (
                    "the step exited as the reviewed plan requires and its "
                    f"observation does not satisfy the reviewed expectation: "
                    f"{expectation_refusal}"
                )

            state.outcomes.append(
                StepOutcome(
                    step_id=step.step_id,
                    band=step.band,
                    run_as=step.run_as,
                    # The vector that actually ran. For a step with declared
                    # binding sites that is the substituted one, because
                    # recording the symbolic form would report something other
                    # than what was executed.
                    argv=argv,
                    exit_status=result.exit_status,
                    satisfied=satisfied,
                    timed_out=result.timed_out,
                    observations=result.observations,
                    stderr_present=result.stderr_present,
                    launch_failure=result.launch_failure,
                    stop_reason=reason,
                )
            )
            if not satisfied:
                # **R13, EH-R13-1.** A creation that reported its object already
                # existed did not create it, so this run's ownership of it is
                # withdrawn and its reversal will not run. The attempt was made,
                # which is exactly why filtering cleanup by attempt alone does
                # not cover this case.
                if step.reports_preexisting(result.exit_status):
                    state.withdrawn.update(step.mutation_ids)
                # **R16, conflict C-8.** An exclusive creation that did not
                # return has two very different outcomes, and conflating them is
                # how a harness either deletes somebody else's directory or
                # reports a clean run over one it left behind. The step
                # enumerates the statuses in which its program created nothing;
                # everything else — an internal failure, an identity it could not
                # read, a timeout, a launch that never reported — leaves an
                # object that may exist and that this run cannot identify.
                if step.establishes_ownership_by_creation and not (
                    not result.timed_out
                    and not result.launch_failure
                    and step.created_nothing(result.exit_status)
                ):
                    state.uncertain_creations.update(
                        step.establishes_ownership_by_creation
                    )
                if step.role is StepRole.CONTROL:
                    state.failed_controls.add(step.band)
                state.stop(step.step_id, reason)
                return
            state.satisfied_steps.add(step.step_id)
            # A baseline step that was satisfied observed its subjects absent
            # before anything changed.
            state.owned.update(step.establishes_ownership_of)
            # **R16, conflict C-8.** A satisfied exclusive creation is the other
            # way ownership is established, and the only other way. `mkdir(2)`
            # returned, so nothing was at that path; and it returns an empty
            # directory, so nothing was under it either — which is what the
            # reviewed, manifest-pinned contained set rests on. The two ownership
            # routes are the whole of what adds to `owned`.
            state.owned.update(step.establishes_ownership_by_creation)
            state.owned.update(step.establishes_ownership_of_contained)
            if step.establishes_ownership_by_creation:
                state.created_identity.update(
                    {
                        key: value
                        for key, value in result.observations
                        if key in CREATED_IDENTITY_KEYS
                    }
                )

            if not self._materialize_after(step.step_id, state):
                return

    def _materialize_after(self, step_id: str, state: _RunState) -> bool:
        """Write the reviewed bytes anchored to `step_id`. False stops the run.

        Responsibility begins exactly where it does for a command: the declared
        mutation is recorded **before** the write is attempted, so a
        materialization whose outcome is never learned is treated as potentially
        reached and the full derived cleanup — restore, one reload, control,
        proof — runs for it.
        """
        for materialization in self.plan.execution_plan.materializations_after(step_id):
            state.current_step_id = materialization.step_id

            refusal = self._revalidate_materialization(materialization, state)
            if refusal:
                state.stop(materialization.step_id, refusal)
                state.outcomes.append(
                    self._materialization_outcome(
                        materialization,
                        applied=False,
                        failure=(
                            MATERIALIZATION_CAPTURE_INCOMPLETE
                            if "pre-change capture" in refusal
                            else MATERIALIZATION_VALIDATION_REFUSED
                        ),
                        reason=refusal,
                    )
                )
                return False

            state.mutations_reached.extend(materialization.mutation_ids)

            try:
                result: MaterializationResult = self.materializer.materialize(
                    step_id=materialization.step_id,
                    destination=materialization.destination,
                    content=materialization.file.content,
                    sha256=materialization.file.sha256,
                    owner=materialization.file.owner,
                    group=materialization.file.group,
                    mode=materialization.file.mode,
                )
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:
                # The materializer failed. The exception may name the path, the
                # account or an operating-system message, and none of those may
                # be serialized, so it is dropped for the fixed classification.
                result = MaterializationResult(
                    applied=False, failure=LAUNCH_BOUNDARY_FAILURE
                )

            state.outcomes.append(
                self._materialization_outcome(
                    materialization,
                    applied=result.applied,
                    failure=result.failure,
                    reason="" if result.applied else MATERIALIZATION_NOT_APPLIED,
                )
            )
            if not result.applied:
                state.stop(materialization.step_id, MATERIALIZATION_NOT_APPLIED)
                return False
            state.satisfied_steps.add(materialization.step_id)
        return True

    @staticmethod
    def _materialization_outcome(
        step: MaterializeStep, *, applied: bool, failure: str, reason: str
    ) -> StepOutcome:
        """One materialization's outcome, in the same shape as a command's.

        `argv` is empty and stays empty: a materialization has no argument
        vector, and giving it one that merely looked like a command is how a
        reader stops being able to tell the two apart.
        """
        return StepOutcome(
            step_id=step.step_id,
            band=step.band,
            run_as=step.run_as,
            argv=(),
            exit_status=0 if applied else -1,
            satisfied=applied,
            timed_out=False,
            launch_failure="" if applied else failure,
            stop_reason=reason,
        )

    def _conclude(self, state: _RunState) -> RunOutcome:
        """Clean up once, then assemble the outcome from both halves.

        The execution failure and the cleanup result are separate fields of the
        returned value. Neither is allowed to stand in for the other.
        """
        if self._cleanup_invoked:
            raise ExecutorRefused(
                "Cleanup has already been invoked for this run. It runs exactly "
                "once: a second pass over a destructive plan is not a retry, and "
                "§2.13.2b does not offer one."
            )
        self._cleanup_invoked = True

        cleanup_outcomes: list[StepOutcome] = []
        finished = False
        try:
            cleanup = self._clean_up(state, cleanup_outcomes)
            finished = True
        finally:
            if not finished:
                # Cleanup was interrupted rather than completed. Nothing is
                # suppressed — the interruption is on its way out — but the
                # runner records that what it left behind is unknown, so the
                # next invocation refuses.
                self._cleanup_uncertain = True
                self._blocked_by_residue = self._declared_residue(cleanup_outcomes) or (
                    "effective-configuration",
                )

        outcome = RunOutcome(
            steps=tuple(state.outcomes),
            cleanup_steps=tuple(cleanup_outcomes),
            cleanup=cleanup,
            stopped_at=state.stopped_at,
            stop_reason=state.stop_reason,
            mutations_reached=tuple(state.mutations_reached),
            cleanup_skipped=(
                self._last_applicability.skipped
                if self._last_applicability is not None
                else ()
            ),
        )
        if cleanup.residue or cleanup.configuration_risk:
            self._blocked_by_residue = tuple(cleanup.residue) or (
                "effective-configuration",
            )
        self._last_outcome = outcome
        return outcome

    @staticmethod
    def _unsatisfied_reason(step: CommandStep, exit_status: int) -> str:
        if step.refusal_required:
            return (
                "the step exited 0 where the plan requires a refusal; the "
                "authentication boundary did not deny"
            )
        return (
            f"exit {exit_status} is not one of the statuses the reviewed plan "
            f"expects {list(step.satisfying_statuses)}"
        )

    # -- cleanup -------------------------------------------------------------

    def _clean_up(
        self, state: _RunState, outcomes: list[StepOutcome]
    ) -> CleanupOutcome:
        """Derived cleanup, entered after the first reached mutation.

        The prefix that ran does not choose the cleanup: the **declared**
        mutations do. Every reversal is idempotent in the sense this package
        means — no step performs a destructive act when its object is absent —
        so running the whole derived cleanup after a run that reached three
        mutations removes those three and reports the rest as already gone,
        rather than leaving the executor to reason about which prefix it was in.

        `outcomes` is the caller's list rather than a local, so a failure of the
        cleanup machinery itself still leaves the steps that did run visible in
        the returned outcome.
        """
        applicability = self.plan.cleanup_plan.applicable(
            attempted=state.mutations_reached,
            owned=sorted(state.owned),
            withdrawn=sorted(state.withdrawn),
        )
        self._last_applicability = applicability
        # **R16, conflict C-8.** An exclusive creation whose outcome does not
        # prove the host untouched leaves an object this run can neither remove
        # nor disown. It is residue in every path below, including the one where
        # no cleanup step applies at all — which is exactly the path a run that
        # stopped on its own root creation takes.
        uncertain = self._uncertain_residue(state)
        if not applicability.steps:
            return classify_cleanup(
                probe_passed=state.probe_passed,
                unremoved=uncertain,
                configuration=ConfigurationRestoration(),
                preserved=self._preserved(applicability, uncertain),
            )
        try:
            return self._run_cleanup_plan(state, outcomes, applicability)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            # The cleanup machinery failed, not one of its steps. What the run
            # created is therefore not proved removed, and that is S-B — named
            # from the plan's own declarations, never from the exception.
            self._cleanup_uncertain = True
            return self._cleanup_did_not_complete(outcomes)

    @staticmethod
    def _uncertain_residue(state: _RunState) -> tuple[str, ...]:
        """**R16, conflict C-8.** The subjects of creations whose outcome is unknown.

        Named from the **plan's** own mutation ids, never from the host and never
        from an exception: a mutation id is `kind:identifier`, and the identifier
        is the absolute path the reviewed plan declared.
        """
        return tuple(
            sorted(
                {
                    mutation_id.split(":", 1)[1]
                    for mutation_id in state.uncertain_creations
                    if ":" in mutation_id
                }
            )
        )

    @staticmethod
    def _preserved(
        applicability: CleanupApplicability, uncertain: Sequence[str] = ()
    ) -> tuple[str, ...]:
        """Every object cleanup left alone because it is not this run's.

        Named from the **plan's** declarations, never from the host: a skipped
        step's `subject` is the string the reviewed cleanup plan carries.

        **R16, conflict C-8.** A subject whose creation outcome is unknown is
        excluded. *Preserved* says *"this run did not create this and does not
        remove it"*, and that is a claim an uncertain creation cannot support:
        the run may well have created it. Those subjects are residue instead,
        which is the state that requires operator recovery rather than the one
        that reads as a deliberate courtesy.
        """
        withheld = set(uncertain)
        return tuple(
            sorted(
                {
                    item.subject
                    for item in applicability.skipped
                    if item.subject
                    and item.reason != NOT_ATTEMPTED
                    and item.subject not in withheld
                }
            )
        )

    def _run_cleanup_plan(
        self,
        state: _RunState,
        outcomes: list[StepOutcome],
        applicability: CleanupApplicability,
    ) -> CleanupOutcome:
        """Every derived cleanup step, in the generated order.

        A step that fails does not stop the rest. The derived plan has no step
        whose safety depends on an earlier one having succeeded — the ordering
        is a dependency order for *effectiveness*, and every step is
        non-destructive when its object is absent — so stopping would leave more
        behind than continuing. What a failed step does is make its object
        residue, which is state S-B.
        """
        restored: list[str] = []
        proven: list[str] = []
        reload_succeeded: bool | None = None
        control_succeeded: bool | None = None
        uncertain = self._uncertain_residue(state)
        unremoved: list[str] = list(uncertain)
        satisfied_cleanup: set[str] = set()
        retained: list[str] = []

        applicable_ids = {item.step_id for item in applicability.steps}
        for step in applicability.steps:
            # **R13, EH-R13-2.** A step that deletes a recovery input runs only
            # when everything the recovery would need has already succeeded. The
            # object is retained and reported otherwise; it is not a failure,
            # and it is emphatically not a deletion.
            #
            # The requirement is read against the **applicable** configuration
            # phase, not the declared one. A run that never changed a
            # configuration file has nothing to recover and its captures are
            # ordinary objects: retaining them there would report a recovery
            # input for a restoration that was never owed, and would leave a
            # directory behind for a reason that did not exist.
            required = set(step.requires_satisfied) & applicable_ids
            if required and not required <= satisfied_cleanup:
                retained.append(step.removes)
                outcomes.append(
                    StepOutcome(
                        step_id=step.step_id,
                        band="cleanup",
                        run_as=step.run_as,
                        argv=tuple(step.argv),
                        exit_status=-1,
                        satisfied=False,
                        timed_out=False,
                        stop_reason=RECOVERY_INPUT_RETAINED,
                    )
                )
                continue
            # **R16, conflict C-8.** A removal that names a revalidation runs
            # only when that revalidation both ran and **matched**. Otherwise the
            # object at the path is not the object this run created — or its
            # identity could not be re-read — and it becomes residue rather than
            # a deletion. Replacing a path does not confer permission to delete
            # its replacement.
            if step.requires_revalidated and (
                step.requires_revalidated in applicable_ids
                and step.requires_revalidated not in satisfied_cleanup
                or step.requires_revalidated not in applicable_ids
            ):
                unremoved.append(step.removes)
                outcomes.append(
                    StepOutcome(
                        step_id=step.step_id,
                        band="cleanup",
                        run_as=step.run_as,
                        argv=tuple(step.argv),
                        exit_status=-1,
                        satisfied=False,
                        timed_out=False,
                        stop_reason=REMOVAL_NOT_REVALIDATED,
                    )
                )
                continue
            refusal = self._revalidate_cleanup(step)
            if refusal:
                result = CommandResult(
                    exit_status=-1,
                    timed_out=False,
                    launch_failure=LAUNCH_VALIDATION_REFUSED,
                )
            else:
                try:
                    result = self.boundary.run(
                        step_id=step.step_id,
                        argv=tuple(step.argv),
                        run_as=step.run_as,
                        # **R16, conflict C-8.** Every cleanup step but one
                        # records its exit status and nothing else, for the
                        # reason a mutation-bearing command step does: a step
                        # whose purpose is a side effect has no observation to
                        # make. The revalidation's purpose *is* the observation,
                        # and its policy is declared in the reviewed plan and
                        # pinned in the manifest like every other.
                        capture=step.capture,
                        timeout_seconds=timeout_for(step.argv[0]),
                    )
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception:
                    result = CommandResult(
                        exit_status=-1,
                        timed_out=False,
                        launch_failure=LAUNCH_BOUNDARY_FAILURE,
                    )
            identity_refusal = ""
            if step.kind is CleanupStepKind.REVALIDATE:
                identity_refusal = self._revalidation_refusal(state, result)
            satisfied = (
                not result.timed_out
                and not result.launch_failure
                and step.is_satisfied_by(result.exit_status)
                and not identity_refusal
            )
            outcomes.append(
                StepOutcome(
                    step_id=step.step_id,
                    band="cleanup",
                    run_as=step.run_as,
                    argv=tuple(step.argv),
                    exit_status=result.exit_status,
                    satisfied=satisfied,
                    timed_out=result.timed_out,
                    stderr_present=result.stderr_present,
                    launch_failure=result.launch_failure,
                    stop_reason=(
                        refusal
                        if refusal
                        else CLEANUP_BOUNDARY_FAILURE
                        if result.launch_failure == LAUNCH_BOUNDARY_FAILURE
                        else identity_refusal
                    ),
                )
            )
            if satisfied:
                satisfied_cleanup.add(step.step_id)
            self._record_cleanup_observation(
                step,
                satisfied,
                restored=restored,
                proven=proven,
                unremoved=unremoved,
            )
            if step.kind is CleanupStepKind.RELOAD:
                reload_succeeded = satisfied
            elif step.kind is CleanupStepKind.VERIFY and not step.refusal_required:
                control_succeeded = satisfied

        configuration = ConfigurationRestoration(
            # **R13, EH-R13-1.** The *applicable* declarations, not the whole
            # plan's. A run that never reached a configuration mutation has no
            # configuration to restore, and reporting the plan's declared files
            # as unrestored would turn *"we did not go there"* into a risk we
            # had created.
            declared_files=applicability.declared_files(),
            restored_files=tuple(restored),
            declared_mappings=applicability.declared_mappings(),
            mappings_proven_ineffective=tuple(proven),
            reload_succeeded=reload_succeeded,
            verification_control_succeeded=control_succeeded,
        )
        return classify_cleanup(
            probe_passed=state.probe_passed,
            unremoved=tuple(unremoved),
            configuration=configuration,
            preserved=self._preserved(applicability, uncertain),
            retained_recovery_inputs=tuple(sorted(set(retained))),
        )

    @staticmethod
    def _revalidation_refusal(state: _RunState, result: "CommandResult") -> str:
        """**R16, conflict C-8.** Does the object at the path have the identity
        the creation reported?

        Three ways to answer no, and all three are the same refusal:

        * the creation recorded no identity — there was no exclusive creation in
          this run, or its observation did not survive the capture boundary;
        * the revalidation reported neither key, or reported one of them
          `unreadable`, which is what `capture.sanitize` emits for a value that
          is not the shape its field can have; or
        * the two disagree.

        The comparison is between **two observations**, and the expected one is
        the earlier of them: the identity is never learned from the reading it is
        judging, and there is no path by which a revalidation supplies its own
        expectation.
        """
        expected = state.created_identity
        if not expected or sorted(expected) != sorted(CREATED_IDENTITY_KEYS):
            return OWNERSHIP_NOT_REVALIDATED
        observed = {
            key: value for key, value in result.observations if key in expected
        }
        if sorted(observed) != sorted(expected):
            return OWNERSHIP_NOT_REVALIDATED
        if any(observed[key] != expected[key] for key in expected):
            return OWNERSHIP_NOT_REVALIDATED
        return ""

    def _declared_residue(self, outcomes: Sequence[StepOutcome]) -> tuple[str, ...]:
        """Every object the **applicable** cleanup removes that no cleanup step
        has been observed to remove.

        Bounded by construction: the names come from the reviewed plan, not from
        the host and not from an exception.

        **R13, EH-R13-1.** *Applicable*, not *declared*. A run that never reached
        the database has no unremoved database, and naming one here would report
        as residue an object this run neither created nor was entitled to touch.
        Before an applicability has been derived — an exception on the way to
        cleanup — the whole declared plan is used, because at that point nothing
        is known about what was reached and the conservative answer is the wide
        one.
        """
        removed = {outcome.step_id for outcome in outcomes if outcome.satisfied}
        applicable = (
            self._last_applicability.steps
            if self._last_applicability is not None
            else self.plan.cleanup_plan.steps
        )
        return tuple(
            sorted(
                {
                    step.removes
                    for step in applicable
                    if step.kind is CleanupStepKind.REVERSAL
                    and step.removes
                    and step.step_id not in removed
                }
            )
        )

    def _cleanup_did_not_complete(
        self, outcomes: Sequence[StepOutcome]
    ) -> CleanupOutcome:
        """State S-B for a cleanup that could not be carried out.

        Constructed rather than classified, because `classify_cleanup` answers
        *"what did cleanup observe?"* and the answer here is *"it did not get to
        observe"*. It is S-B for exactly the reason §2.13.2b gives: something
        this run created may still be in effect, the residue is named by the
        plan's own declarations, and the next invocation refuses.
        """
        residue = self._declared_residue(outcomes)
        risks = (
            "The derived cleanup did not complete, so nothing this run created "
            "is proved removed and any temporary PostgreSQL authentication "
            "configuration is not proved restored or reloaded.",
        )
        return CleanupOutcome(
            state="S-B",
            exit_code=3,
            residue=residue,
            configuration_risk=risks,
            message=(
                "Cleanup did not complete. The host now requires operator "
                "recovery before another generation can be created. The next "
                "invocation refuses while this is unresolved rather than "
                "cleaning it."
            ),
        )

    @staticmethod
    def _record_cleanup_observation(
        step: CleanupStep,
        satisfied: bool,
        *,
        restored: list[str],
        proven: list[str],
        unremoved: list[str],
    ) -> None:
        """Turn one cleanup step's satisfaction into the facts `classify_cleanup`
        needs. Residue is decided by the step that was meant to remove the object
        not being satisfied — never by an exit status alone, which is why
        `CleanupStep.is_satisfied_by` already knows that `rmdir` on an absent
        directory and a correctly refused connection are both non-zero."""
        if step.kind is CleanupStepKind.RESTORE:
            if satisfied:
                restored.append(step.removes)
        elif step.kind is CleanupStepKind.VERIFY and step.refusal_required:
            if satisfied:
                username = step.argv[step.argv.index("--username") + 1]
                proven.append(f"{step.run_as}->{username}")
        elif step.kind is CleanupStepKind.REVERSAL:
            if not satisfied and step.removes:
                unremoved.append(step.removes)


__all__ = [
    "BEFORE_FIRST_STEP",
    "CLEANUP_BOUNDARY_FAILURE",
    "ExecutingRunner",
    "ExecutorRefused",
    "MATERIALIZATION_NOT_APPLIED",
    "OPERATOR_INTERRUPTION",
    "PERMITTED_RUN_AS",
    "REFUSED_EXIT_CODE",
    "RunOutcome",
    "StepOutcome",
    "UNEXPECTED_EXECUTION_FAILURE",
]
