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

import array
import fcntl
import hashlib
import hmac
import os
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
    EFFECT_FLAGS,
    EVIDENCE_ROLE,
    PERMITTED_EXECUTABLES,
    ROOT_ROLE,
    CommandStep,
    DescriptorEffect,
    EffectKind,
    MaterializeStep,
    StepRole,
    validate_argv,
)
from ..review_manifest import ReviewManifest, digests_match
from .boundary import (
    IDENTITY_CONTRACT,
    LAUNCH_BOUNDARY_FAILURE,
    LAUNCH_EFFECT_REFUSED,
    LAUNCH_EFFECT_UNAVAILABLE,
    LAUNCH_VALIDATION_REFUSED,
    CommandResult,
    IdentityLookup,
    IdentityRefusal,
    ProcessBoundary,
    SystemIdentityLookup,
    timeout_for,
)
from ..durability_model import DescriptorMode, Quiescence
from .descriptors import (
    DESCRIPTOR_OBJECT_ABSENT,
    DescriptorInventory,
    DescriptorRefused,
    ObjectIdentity,
    PosixFilesystem,
)
from .materializer import (
    MATERIALIZATION_CAPTURE_INCOMPLETE,
    MATERIALIZATION_RECOVERY_BASIS_MISSING,
    MATERIALIZATION_VALIDATION_REFUSED,
    FileMaterializer,
    MaterializationResult,
    RecordingMaterializer,
    RestorationOutcome,
    publication_permits_mutation,
    restore_configuration,
)
from ..lifecycle_storage import Participant
from .participants import (
    EffectPermit,
    HarnessObservations,
    ParticipantIntegration,
    ParticipantRefused,
)
from ..reservation import ResidueObservation
from .recovery_store import (
    ConfigurationCaptureSet,
    RecoveryStore,
    StorePublication,
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
    #: **r6 §1.4, C-P5.0-LAB-I-R1.** How P1, P1b, P2, P4 and L3 are issued.
    #: `None` means no effect issuer was assembled, and then every effect step
    #: refuses: an executor without one does not fall back to a pathname-based
    #: command, because the pathname-based commands are what r6 §6.4 retired.
    effects: "DescriptorBoundEffects | None" = None
    #: **r6 §5.** The participant integration point this run is accounted for
    #: by — the object that holds the cooperative lock, publishes the ledger
    #: entries and concludes the reservation. `None`, or anything that is not a
    #: `ParticipantIntegration`, means the executor was assembled outside the
    #: reservation protocol, which `execute()` refuses before the first step.
    session: ParticipantIntegration | None = None
    #: **PR-20260914-LABI-R1-1 and -R1-2.** The permit the integration point
    #: issued after its durable `participant_started` publication, bound to this
    #: run and this reservation. It is not a flag, not a sentinel and **not a
    #: bearer token**: an equivalent object can be constructed from readable
    #: module attributes, and the previous version of this comment was wrong to
    #: say otherwise. What it is is a reference to a live work invocation, and
    #: `_require_accounted_run` spends it through `EffectPermit.consume` — once,
    #: and only while that invocation is the one running.
    permit: EffectPermit | None = None
    #: The run identifier this executor's recovery publication and ledger entry
    #: are filed under. Bounded before it becomes a filename or a role label.
    run_id: str = ""
    #: The reservation this run belongs to, written into its `participant_started`
    #: entry before the first effect and never derived from a caller afterwards.
    reservation_id: str = ""
    #: The publication the pre-M1 capture produced, kept so `_materialize_after`
    #: can re-check its barrier set immediately before the first mutation.
    _publication: object | None = field(default=None, init=False)
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
    def cleanup_uncertain(self) -> bool:
        """Whether cleanup could not prove what it left behind.

        Read by `run_observations` below, because an uncertain cleanup did not
        complete its residue search — and a search that did not complete
        establishes nothing about the paths it did not reach.
        """
        return self._cleanup_uncertain

    def run_observations(
        self, outcome: RunOutcome, *, observed_by: str, searched_at: str
    ) -> HarnessObservations:
        """What **this** run established, for the reservation's release decision.

        **PR-20260914-LABI-R1-1.** The release used to be handed an evidence
        object a caller built. These two facts are now derived from the run that
        actually happened: the residue search is the cleanup's own result, and
        the configuration restoration is its own configuration risk. Neither is
        supplied, neither defaults to a passing value, and `release()` refuses on
        each of the three unsatisfactory shapes — not observed, observed
        incomplete, and observed with something in it.

        The other two members of `HarnessObservations` stay `None` here. Whether
        every process the run started has exited and every server-side
        transaction has settled are r6 §1.6's external observations: this process
        cannot make them, a parent's exit status is explicitly not one of them,
        and an unmade observation quarantines. They reach the evidence only
        through `HarnessObservations.with_quiescence`, from an observation a
        named observer made.
        """
        if not isinstance(observed_by, str) or not observed_by.strip():
            raise ExecutorRefused(
                "An observation names who made it. A residue search with no "
                "observer is an assertion with no author, and "
                "`ResidueObservation` refuses one."
            )
        cleanup = outcome.cleanup
        uncertain = self._cleanup_uncertain
        paths = tuple(cleanup.residue)
        if uncertain:
            # The search did not finish, so what it did not reach is unknown.
            # `complete=False` is the shape `release()` refuses with the reason
            # *"the residue search did not complete"*, which is the true one.
            # The restoration is `None` rather than `False` for the same reason:
            # an uncertain cleanup did not observe it false, it observed nothing.
            residue = ResidueObservation.found(
                paths,
                observed_by=observed_by,
                searched_at=searched_at,
                complete=False,
            )
            restored: bool | None = None
        elif paths:
            residue = ResidueObservation.found(
                paths, observed_by=observed_by, searched_at=searched_at
            )
            restored = not (
                cleanup.configuration_risk or cleanup.retained_recovery_inputs
            )
        else:
            residue = ResidueObservation.empty(
                observed_by=observed_by, searched_at=searched_at
            )
            restored = not (
                cleanup.configuration_risk or cleanup.retained_recovery_inputs
            )
        return HarnessObservations(
            residue=residue, configuration_restored=restored
        )

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
        if step.is_effect:
            # A descriptor-bound effect names no executable, so there is no
            # vector to revalidate. What replaces the vector check is stricter:
            # the effect's own reviewed shape was checked at construction, the
            # issuer refuses an unarmed instance, and every effect refuses
            # unless the object it reaches is the one the creating step recorded.
            if step.run_as != "root":
                return (
                    "a descriptor-bound effect is issued by the executor itself "
                    "and by no other identity"
                )
            if self.effects is None:
                return (
                    "this executor was assembled with no descriptor-bound effect "
                    "issuer, so the step writes nothing. An executor without one "
                    "refuses the effect rather than falling back to a "
                    "pathname-based command"
                )
            if not isinstance(step.capture, CapturePolicy):
                return "the step does not declare a reviewed capture policy"
            return ""
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
        # **r6 §§2.3.3 and 1.4.4 M1, C-P5.0-LAB-I-R1.** M1's own precondition is
        # that the independent publication reported **every** barrier crossed.
        # The capture step being satisfied is not that fact: it is this run's
        # account of a step, and the publication's barrier set is the account
        # the contract names. It is re-checked here, immediately before the
        # first configuration mutation, rather than trusted from earlier.
        if not publication_permits_mutation(self._publication):
            return (
                "the independent recovery basis does not report every §2.3.3 "
                "barrier crossed, so the first configuration mutation may not "
                "occur. A mutation with no durably published basis is the state "
                "PR-20260911-2 found revision 1 in"
            )
        return ""

    def _issue_cleanup_effect(self, step: CleanupStep) -> CommandResult:
        """One cleanup effect, with the same fixed classification a step gets."""
        issuer = self.effects
        if issuer is None or step.effect is None:
            return CommandResult(
                exit_status=-1,
                timed_out=False,
                launch_failure=LAUNCH_EFFECT_UNAVAILABLE,
            )
        try:
            self._apply_effect(issuer, step.effect, step.step_id)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return CommandResult(
                exit_status=-1, timed_out=False, launch_failure=LAUNCH_EFFECT_REFUSED
            )
        return CommandResult(exit_status=0, timed_out=False)

    def _revalidate_cleanup(self, step: CleanupStep) -> str:
        """The same guards for a cleanup step.

        Cleanup is derived, bounded and non-recursive by construction, and it is
        still revalidated: it runs the destructive half of the plan, and the
        object that reaches this loop is not obliged to be the object that was
        reviewed.
        """
        if step.is_effect:
            if step.run_as != "root":
                return (
                    "a descriptor-bound effect is issued by the executor itself "
                    "and by no other identity"
                )
            if self.effects is None:
                return (
                    "this executor was assembled with no descriptor-bound effect "
                    "issuer, so the cleanup step writes nothing"
                )
            return ""
        return self._revalidate_vector(tuple(step.argv), step.run_as)

    # -- the run -------------------------------------------------------------

    def execute(self) -> RunOutcome:
        """Run the reviewed plan, and clean up whatever it reached.

        The `try` covers every mutation-bearing command. There is no path out of
        this method — return, exception or interruption — that does not pass
        through `_conclude`, and `_conclude` is what invokes cleanup.
        """
        self._require_accounted_run()
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

    def accept_permit(self, permit: EffectPermit) -> None:
        """Take the permit the integration point issued for **this** run.

        **PR-20260914-LABI-R1-1.** This is the hand-off the re-review found
        missing: the CLI constructed a `ParticipantIntegration` and drove the
        executor beside it, so nothing connected the durable start to the run
        that then issued effects. `ParticipantIntegration.run_harness` calls
        this with the permit it issued, and the permit is checked against this
        executor's own run and reservation before it is kept.

        A second hand-off is refused. A permit is evidence about one durable
        start; an executor handed two would be a run accounted for twice, and
        the ledger accounts for one. The refusal is on the **second call**, not
        on the second value: two permits for the same run compare equal, so a
        check on the value alone would be a branch nothing could take.
        """
        if self.permit is not None:
            raise ExecutorRefused(
                "This executor has already been handed its permit. One run has "
                "one durable start and one hand-off, and a second is either a "
                "second start or somebody else's."
            )
        self.permit = self._validate_permit(permit)

    def _validate_permit(self, permit: object) -> EffectPermit:
        """The permit this run may proceed on, or a refusal naming why."""
        if not isinstance(permit, EffectPermit):
            raise ExecutorRefused(
                "An armed run proceeds on an `EffectPermit` issued by the "
                "participant integration point, not on the presence of an "
                "object. The presence check is exactly what PR-20260914-LABI-R1-1 "
                "found: `session=object()` satisfied it."
            )
        if not permit.issued:
            raise ExecutorRefused(
                "The permit was not issued by a durable `participant_started` "
                "publication. r6 §5.11 requires the non-reusable state to reach "
                "durable storage **before** the first relevant effect, and a "
                "permit constructed without one asserts a publication that did "
                "not happen."
            )
        if not permit.binds(
            participant=Participant.HARNESS_CLI,
            run_id=self.run_id,
            reservation_id=self.reservation_id,
        ):
            raise ExecutorRefused(
                "The permit does not bind this run. It must name the harness "
                f"participant, run {self.run_id!r} and reservation "
                f"{self.reservation_id!r} — equality on all three, which is r6 "
                "§5.11.1's binding rule applied to the object that carries the "
                "start's authority. A permit for another run is another run's "
                "accounting."
            )
        return permit

    def _require_accounted_run(self) -> None:
        """**r6 §5.11, LABI-3, LABI-R1-1 and PR-20260914-LABI-R1-2.** An armed
        run is an accounted run, *accounted* is proved rather than asserted, and
        it is proved about **now**.

        An effect issuer that can really `mkdirat`, `ioctl` and `unlinkat` may
        only be driven by a run the participant ledger accounts for. Without the
        integration point there is no `participant_started` entry, so an
        interrupted run would leave effects nothing could attribute — which is
        R3-2 in one sentence, and the reason the reset's exemption was refused.

        The check has three value conjuncts and then the one that matters. The
        `session` must be a real `ParticipantIntegration`; the permit must bind
        this exact participant, run id and reservation; and the integration point
        must hold this executor's reservation. **None of those is sufficient**,
        and PR-20260914-LABI-R1-2 is why it is said out loud: every one of them
        is satisfied by a permit reconstructed from readable module attributes,
        and every one of them is satisfied by a genuine permit a work callback
        retained and replayed after the lock was released.

        So the last step is `EffectPermit.consume`, which asks the protocol
        rather than the object: that this integration point is inside the work
        invocation the authority was issued for, that it owns an open session,
        that the session still holds the cooperative lock, that the stored run is
        this participant's, bound to this reservation and still in progress, that
        the reservation is in r6 §5.7's T8 `running` state, and that the
        authority has not already been spent. **PR-20260914-LABI-R2-1:** the
        spend is the running invocation's own `ISSUED → SPENT` transition, kept
        in a record no attribute reachable from here refers to, so it is good for
        exactly one first effect per invocation. `participants.py` states the
        limit of that claim: it holds against ordinary attribute access and
        method calls, not against code in this interpreter that rebinds this
        method or reaches into frames.

        It is checked here rather than at construction because an unarmed issuer
        is exactly what every test injects: a double that writes nothing needs no
        ledger entry, and requiring one would make the guard a statement about
        the suite rather than about the host. It is checked **here** rather than
        at `accept_permit` because r6 §5.7 places T9 after T8 and inside the
        hold: the only moment worth checking is the moment before the effect.
        Every type is checked rather than an attribute looked up by name — a
        duck-typed object that merely has the right attribute must not be able to
        satisfy or to trip it.
        """
        issuer = self.effects
        if not isinstance(issuer, DescriptorBoundEffects) or not issuer.armed:
            return
        if not isinstance(self.session, ParticipantIntegration) or not self.run_id:
            raise ExecutorRefused(
                "This executor holds an armed descriptor-bound effect issuer and "
                "no participant integration accounts for the run. r6 §5.11 "
                "requires every one of the seven entry points to publish its "
                "non-reusable state before its first relevant effect, and an "
                "unaccounted run is one whose effects nothing can attribute. "
                "The effects are not issued."
            )
        permit = self._validate_permit(self.permit)
        if permit.participant is not self.session.participant:
            raise ExecutorRefused(
                "The permit and the integration point name different "
                "participants, so whatever published the start is not what is "
                "accounting for this run."
            )
        if self.session.reservation_id != self.reservation_id:
            raise ExecutorRefused(
                "The integration point holds a different reservation than this "
                "executor was assembled for. A run's effects belong to the "
                "reservation its start names, and nothing else."
            )
        try:
            permit.consume(integration=self.session)
        except ParticipantRefused as refusal:
            # `from None`, and the message is built from the protocol's own
            # closed vocabulary: an operator is told which rule refused, and a
            # hostile caller is told nothing about paths, stored bytes or the
            # operating system. The refusal happens before `_refuse_when_blocked`
            # and before the first step, so the process boundary, the
            # materializer and the descriptor-bound issuer are never reached.
            raise ExecutorRefused(
                "This run holds no live authority for its first effect. r6 "
                "§§5.6–5.7 place T9 inside the cooperative lock and after the "
                "current T6, T7 and T8 state, so an armed executor must be "
                "running inside the work invocation its authority was issued "
                "for — not merely hold an object that was valid at some earlier "
                f"time. Refused as {refusal.classification}: {refusal.detail}. "
                "The effects are not issued."
            ) from None

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
                if step.is_effect:
                    # **r6 §1.4, C-P5.0-LAB-I-R1.** No process is started at
                    # all: the executor issues the syscall itself, on a
                    # descriptor its own inventory holds. This is where
                    # `/usr/bin/install` and `/usr/bin/chattr` used to be.
                    result: CommandResult = self._issue_effect(step)
                else:
                    result = self.boundary.run(
                        step_id=step.step_id,
                        argv=argv,
                        run_as=step.run_as,
                        capture=step.capture,
                        timeout_seconds=timeout_for(argv[0]),
                        # **R14, EH-R14-1.** The reviewed names a catalog
                        # reading answers about, taken from the plan and never
                        # from the run. `None` for every other policy, and
                        # `capture.sanitize` refuses one supplied to a policy
                        # that answers no question.
                        catalog=step.catalog_question,
                        # **r6 §§1.3.3 and 6.3.** The declared inherited table,
                        # or the empty one. No synchronizable descriptor is ever
                        # in it, and `DIRFD` is an index into it and nothing else.
                        descriptors=self._transfer_for(step),
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

    # -- r6 §1.4: the descriptor-bound effects, issued here ------------------

    def _transfer_for(self, step: CommandStep) -> tuple:
        """The declared inherited descriptor table for one step, or the empty one.

        **r6 §§1.3.3 and 6.3.** Descriptors move by inheritance and by nothing
        else. The table is declared by the inventory — which refuses to put a
        synchronizable descriptor in one — and a step that was declared none
        receives none, so `DIRFD` resolves against a table this run stated
        rather than against whatever happened to be open.
        """
        if self.effects is None:
            return ()
        return tuple(self.effects.declared_transfer())

    def _issue_effect(self, step: CommandStep) -> CommandResult:
        """One reviewed descriptor-bound effect, and a fixed classification.

        Every refusal comes back as `LAUNCH_EFFECT_REFUSED`. The exception the
        issuer raises names the role, the recorded identity and the one found,
        which is what an operator needs and is **not** what an evidence artifact
        may carry, so it stops here exactly as `boundary`'s identity refusals do.
        """
        issuer = self.effects
        effect = step.effect
        if issuer is None or effect is None:  # pragma: no cover - refused above
            return CommandResult(
                exit_status=-1,
                timed_out=False,
                launch_failure=LAUNCH_EFFECT_UNAVAILABLE,
            )
        try:
            self._apply_effect(issuer, effect, step.step_id)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            return CommandResult(
                exit_status=-1, timed_out=False, launch_failure=LAUNCH_EFFECT_REFUSED
            )
        return CommandResult(exit_status=0, timed_out=False)

    def _apply_effect(
        self,
        issuer: "DescriptorBoundEffects",
        effect: DescriptorEffect,
        step_id: str = "",
    ) -> None:
        """Dispatch one effect kind. The closed set, and no default branch."""
        if effect.kind is EffectKind.CREATE_DIRECTORY:
            issuer.create_directory_object(
                parent_role=effect.directory_role,
                name=effect.name,
                mode=effect.mode,
                step_id=step_id,
            )
            return
        if effect.kind is EffectKind.CREATE_OBJECT:
            uid, gid = self._resolved_ownership(effect)
            issuer.create_object(
                directory_role=effect.directory_role,
                name=effect.name,
                uid=uid,
                gid=gid,
                mode=effect.mode,
                step_id=step_id,
            )
            return
        if effect.kind is EffectKind.INSTALL_PAYLOAD:
            content = self.source_bytes.get(effect.payload_source)
            if content is None:
                raise EffectRefused(
                    "the reviewed payload's bytes are not among the covered "
                    "sources this run was handed, so what would be installed is "
                    "not what the manifest digested."
                )
            uid, gid = self._resolved_ownership(effect)
            issuer.install_case_program(
                content=content,
                sha256=hashlib.sha256(content).hexdigest(),
                directory_role=effect.directory_role,
                name=effect.name,
                uid=uid,
                gid=gid,
                mode=effect.mode,
                step_id=step_id,
            )
            return
        if effect.kind is EffectKind.SET_FLAG:
            issuer.set_inode_flags(
                directory_role=effect.directory_role,
                name=effect.name,
                add=_flag_mask(effect.flags),
                step_id=step_id,
            )
            return
        if effect.kind is EffectKind.CLEAR_FLAG:
            issuer.clear_inode_flags(
                directory_role=effect.directory_role,
                name=effect.name,
                remove=_flag_mask(effect.flags),
                step_id=step_id,
            )
            return
        if effect.kind is EffectKind.CAPTURE_CONFIGURATION:
            self._publish_recovery_basis(issuer, effect, step_id)
            return
        if effect.kind is EffectKind.RESTORE_CONFIGURATION:
            self._restore_configuration(issuer, effect, step_id)
            return
        raise EffectRefused(  # pragma: no cover - the vocabulary is closed
            "the effect names a kind this executor does not issue."
        )

    def _resolved_ownership(
        self, effect: DescriptorEffect
    ) -> tuple[int | None, int | None]:
        """The numeric owner and group, through the **injected** NSS boundary.

        The same seam every argument vector's late binding reads, so there is
        one reader of `pwd`/`grp` in this package and a test exercises every
        branch without touching a real account.
        """
        if not effect.owner or not effect.group:
            return (None, None)
        try:
            # `root` is 0, by definition rather than by lookup. The boundary
            # takes the same position for a root step: it requires the launcher
            # to be effective UID and GID 0 rather than resolving the name, so a
            # database that answered something else could not change what root
            # means here either. Every other name is one of the four disposable
            # identities and is resolved through the **injected** NSS boundary,
            # immediately before the effect — conflict C-5's rule, applied to an
            # effect exactly as it is applied to an argument vector.
            uid = (
                0
                if effect.owner == "root"
                else self.identity_lookup.account(effect.owner)[0]
            )
            gid = (
                0
                if effect.group == "root"
                else self.identity_lookup.group_id(effect.group)
            )
        except IdentityRefusal as refusal:
            raise EffectRefused(
                "the owner or group the reviewed effect names does not resolve "
                "on this host, so the object would be created under an identity "
                "nobody reviewed."
            ) from refusal
        return (uid, gid)

    def _publish_recovery_basis(
        self,
        issuer: "DescriptorBoundEffects",
        effect: DescriptorEffect,
        step_id: str = "",
    ) -> None:
        """**§§1.4.3 and 2.3.3.** Capture and publish, before any mutation.

        The publication's own result is retained, because `_materialize_after`
        re-checks its barrier set immediately before M1 rather than trusting
        that this step reported satisfied.
        """
        publication = issuer.publish_recovery_basis(
            run_id=self.run_id,
            reservation_id=self.reservation_id,
            captured_by=EFFECT_ISSUER,
            capture_set=ConfigurationCaptureSet(
                directory=self.plan.target.postgres_config_directory,
                components=tuple(effect.components),
            ),
            configuration_role=effect.configuration_role,
            evidence_role=effect.evidence_role,
            step_id=step_id,
        )
        self._publication = publication
        if not publication_permits_mutation(publication):
            raise EffectRefused(
                "the independent recovery basis was not durably published, so "
                "no configuration mutation may occur. A refusal here leaves "
                "nothing to recover from, which is why it is a refusal rather "
                "than a warning."
            )

    def _restore_configuration(
        self,
        issuer: "DescriptorBoundEffects",
        effect: DescriptorEffect,
        step_id: str = "",
    ) -> None:
        """**§2.4 / L1.** Verify against the store, then write and publish."""
        uid, gid = self._resolved_ownership(effect)
        outcome = issuer.restore_configuration(
            run_id=self.run_id,
            configuration_role=effect.configuration_role,
            destination_directory=self.plan.target.postgres_config_directory,
            owner_uid=uid if uid is not None else 0,
            owner_gid=gid if gid is not None else 0,
            mode=effect.mode or 0o640,
            step_id=step_id,
        )
        if not outcome.durable:
            raise EffectRefused(
                "the restoration is not durable. A rename whose containing-entry "
                "barrier did not return success is visible and not durable, and "
                "the post-reload verification does not run on it."
            )

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
                            MATERIALIZATION_RECOVERY_BASIS_MISSING
                            if "recovery basis" in refusal
                            else MATERIALIZATION_CAPTURE_INCOMPLETE
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
            elif step.is_effect:
                # **r6 §§1.4.5 and 2.4.** L3's flag clear and L1's
                # verify-and-write restoration. No process starts here either:
                # this is what `chattr -ia` and the restoring `install` became.
                result = self._issue_cleanup_effect(step)
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



# ---------------------------------------------------------------------------
# r6 §§1.4 and 1.6 — descriptor issuance, the quiescence gate, pre/post checks
# ---------------------------------------------------------------------------


#: The five directories P1 creates under the disposable root, in the order it
#: creates them. Each becomes a role in the descriptor inventory, held twice for
#: the run: an `O_PATH` traversal descriptor and, where a barrier is needed, a
#: bound `O_RDONLY` synchronizable one.
RUN_DIRECTORIES = ("bin", "before", "journal", "probe", "probe-ro")

#: The roles the disposable root and its parent are registered under. They are
#: `plan.ROOT_ROLE` and `plan.EVIDENCE_ROLE`, imported rather than respelled: a
#: reviewed effect step names the same role this module resolves.

#: What a quiescence-dependent effect costs, stated where its gate is.
QUIESCENCE_COST = (
    "B3 serializes the run: no effect that depends on it may overlap a case "
    "process. Cases that require concurrency keep it inside the case, and the "
    "executor's B3-dependent effects sit between cases and never during one.",
    "Quiescence is a **prerequisite of name-based removal**, not a detector of "
    "its failure. It does not make `unlinkat` inode-bound, because nothing "
    "does.",
)

#: r6 §1.4.5(4), stated where the post-check is issued. It is the sentence the
#: re-review required rather than a claim the code makes for itself.
POST_CHECK_ESTABLISHES = (
    "The post-check observes whether a name exists. It cannot establish which "
    "object the removal took, and it cannot report a replacement's identity, "
    "because the object is gone and the name is all that is left to look at.",
    "A post-check that finds the name still resolving is informative: something "
    "is there that should not be, and the run reaches S-B.",
    "A post-check returning absence is **not** evidence that the intended "
    "object was removed. It is byte-for-byte the observation a substituted "
    "removal produces.",
)


#: **PR-20260913-LABI-2.** The three refusals the mandatory ownership binding
#: adds, each raised **before** an `ioctl`, an `unlinkat` or an `rmdir`.
EFFECT_IDENTITY_NOT_RECORDED = "creating-step-identity-not-recorded"
EFFECT_OBJECT_ABSENT = "object-absent-at-the-pre-check"
EFFECT_IDENTITY_MISMATCH = "object-is-not-the-recorded-object"
#: The effect issuer's closed refusal vocabulary. A classification outside it is
#: refused at construction, for the reason `DescriptorRefused`'s is: an
#: operator-facing refusal must not acquire a new meaning by being raised.
EFFECT_REFUSALS: frozenset[str] = frozenset(
    {
        EFFECT_IDENTITY_NOT_RECORDED,
        EFFECT_OBJECT_ABSENT,
        EFFECT_IDENTITY_MISMATCH,
    }
)

#: **PR-20260913-LABI-2, stated where the effects are.** The reviewer found the
#: contract's prerequisite — *"the file is the object the creating step
#: recorded"* — encoded as an optional comparison, so an object this run neither
#: created nor recorded could be flagged or removed.
OWNERSHIP_BINDING_RULE = (
    "A non-empty creating-step identity for the exact `(directory_role, name)` "
    "is a **mandatory** prerequisite of setting a flag, clearing a flag and "
    "removing an object. It is not a comparison that is skipped when absent.",
    "Three inputs refuse, and all three refuse before `ioctl`, `unlinkat` or "
    "`rmdir`: no recorded identity, no object at the pre-check, and an identity "
    "that is not equal to the recorded one.",
    "Equality with the mandatory record is the **only** admitting branch. There "
    "is no default empty value, no optional truthiness and no comparison that "
    "is skipped for absence.",
    "Every production creation path records the identity at the point r6 "
    "specifies — inside the effect that creates the object — so no caller has "
    "to remember a separate optional call later.",
    "The accepted distinction is preserved: the pre-check detects substitution "
    "before removal; quiescence is the only prevention for the final-component "
    "interval; and the post-check establishes absence and never which inode was "
    "removed.",
)


class EffectRefused(PlanRefused):
    """A descriptor-bound effect was refused before it was issued.

    Before, never during: every refusal below happens ahead of the syscall that
    would have changed something, so a refused effect leaves the host exactly as
    it was and the dependent effects refuse with it.

    `classification` is one of `EFFECT_REFUSALS` for the three ownership-binding
    refusals and empty for the rest, which carry their rule in the message. A
    value outside the closed vocabulary is refused here rather than reaching an
    operator.
    """

    def __init__(self, message: str, *, classification: str = "") -> None:
        if classification and classification not in EFFECT_REFUSALS:
            raise PlanRefused(
                f"{classification!r} is not one of the effect refusals. The "
                "vocabulary is closed."
            )
        self.classification = classification
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class RemovalRecord:
    """One removal's pre-check, its issue and its post-check, kept apart.

    Three separate facts, because collapsing any two of them is how r2 came to
    claim the post-check established something. `detected_substitution` is true
    only where the **pre**-check caught it.
    """

    name: str
    recorded_identity: str
    pre_check_identity: str | None
    removal_issued: bool
    post_check_identity: str | None
    detected_substitution: bool
    establishes: tuple[str, ...] = POST_CHECK_ESTABLISHES

    @property
    def post_check_absent(self) -> bool:
        return self.post_check_identity is None


@dataclass(slots=True)
class DescriptorBoundEffects:
    """The executor's half of r6 §1: P1, P1b, P2, P4 and L3, through the chain.

    Every effect here is issued on a **descriptor** or refuses. The four the
    contract enumerates:

    * **P1/P1b** — `mkdirat` each of the five run directories exclusively, then
      `fsync` the root's containing entry. Exclusive creation is B1: `EEXIST` is
      the refusal and success *is* the ownership proof;
    * **P2** — install the reviewed case program from a **held buffer**:
      `O_CREAT|O_EXCL|O_WRONLY|O_NOFOLLOW`, write, `fchown`, `fchmod`, `fsync`
      the bytes, publish exclusively, `fsync` the containing entry. The bytes
      written are the bytes digested, from one buffer, so there is no second
      read of any pathname between the check and the write;
    * **P4** — set a flag on the inode a descriptor holds, never on a name. The
      residual interval is the lookup itself, and it is covered by the
      quiescence gate or the effect refuses; and
    * **L3** — clear the flag on the descriptor, then remove by name, with the
      pre-check that detects and the post-check that does not.

    **Nothing here is armed by default.** `armed` is False, and an unarmed
    instance refuses every effect, so an executor assembled with one by mistake
    still changes nothing.
    """

    inventory: DescriptorInventory
    filesystem: PosixFilesystem
    #: The three §1.6 observations. The default is `not_observed`, which refuses
    #: every B3-dependent effect — the fail-closed direction.
    quiescence: Quiescence = field(default_factory=Quiescence.not_observed)
    armed: bool = False
    #: **r6 §§2.2–2.5.** The independent recovery store the pre-M1 capture
    #: publishes into and the restoration verifies against. `None` refuses both
    #: configuration effects: a capture with nowhere durable to publish to is a
    #: mutation with no recoverable basis.
    recovery: "RecoveryStore | None" = None
    #: `(st_dev, st_ino)` as recorded when each object was created, keyed by the
    #: `(role, name)` it was created under. It is what a pre-check compares
    #: against, and it is never re-derived from the descriptor that produced it.
    _recorded: dict[tuple[str, str], str] = field(default_factory=dict, init=False)

    # -- the gate -------------------------------------------------------------

    def require_quiescence(self, effect: str) -> None:
        """**B3.** Refuse the effect and every dependent one, or proceed.

        Unobserved, observed false and incomplete are three different inputs and
        all three refuse. None of them defaults to true, which is what makes
        *"not checked"* and *"checked and false"* stay apart.
        """
        missing = self.quiescence.missing()
        if missing:
            raise EffectRefused(
                f"{effect} depends on experimental quiescence and it is not "
                f"established: {list(missing)}. The effect and every dependent "
                "effect refuse, the objects are reported as residue by absolute "
                "path, the §2.13.2b state is S-B, and independent recovery is "
                "preserved because the store is outside the disposable root and "
                "was published before the first mutation."
            )

    def _require_armed(self, effect: str) -> None:
        if not self.armed:
            raise EffectRefused(
                f"{effect} was requested of an unarmed effect issuer, which "
                "writes nothing. Arming is a single explicit act in the CLI's "
                "`--execute` branch, so an executor assembled without one still "
                "cannot change a file."
            )

    # -- P1 and P1b -----------------------------------------------------------

    def create_run_directories(
        self, *, root_role: str = ROOT_ROLE, mode: int = 0o700
    ) -> tuple[str, ...]:
        """**P1 + P1b.** Five exclusive `mkdirat`s, then the root's barrier.

        It replaces `install -d <path>` with the syscall that carries the
        ownership proof: `install` succeeds whether or not the directory was
        already there, and exclusive creation does not.
        """
        self._require_armed("creating the run directories")
        created: list[str] = []
        for name in RUN_DIRECTORIES:
            handle = self.inventory.create_directory(
                parent_role=root_role, name=name, role=name, mode=mode
            )
            self._recorded[(root_role, name)] = handle.identity.object_id
            created.append(name)
        # P1b — the barrier r2 had no equivalent of at all. A failure here
        # refuses P2 and everything after it.
        self.inventory.bind_synchronizable(root_role)
        self.inventory.fsync_entry(root_role)
        return tuple(created)

    def create_directory_object(
        self,
        *,
        parent_role: str,
        name: str,
        role: str = "",
        mode: int = 0o700,
        step_id: str = "",
    ) -> str:
        """**P1 + P1b for one directory.** `mkdirat`, record, then the barrier.

        It is `create_run_directories` for a plan that creates its directories
        one reviewed step at a time. Exclusive creation is the ownership proof
        and `EEXIST` is the refusal, exactly as the batch form; the parent's
        containing-entry barrier follows each creation rather than the set, so a
        failure refuses the step that needed it rather than a later one.

        **The identity is recorded here**, inside the creation, so no caller has
        to remember a separate optional call later — PR-20260913-LABI-2.
        """
        self._require_armed("creating a run directory")
        handle = self.inventory.create_directory(
            parent_role=parent_role, name=name, role=role or name, mode=mode
        )
        self._recorded[(parent_role, name)] = handle.identity.object_id
        self.inventory.bind_synchronizable(parent_role)
        self.inventory.fsync_entry(parent_role)
        return handle.identity.object_id

    def create_object(
        self,
        *,
        directory_role: str,
        name: str,
        content: bytes = b"",
        uid: int | None = None,
        gid: int | None = None,
        mode: int = 0o640,
        step_id: str = "",
    ) -> str:
        """Create one reviewed file exclusively, from a held buffer.

        The replacement for `install -m … /dev/null <path>`: `install` succeeds
        whether or not something was already at the name and re-resolves that
        name for every one of its own effects. Here `O_CREAT|O_EXCL|O_NOFOLLOW`
        proves the name was free, the ownership and the mode land on the
        **descriptor**, the bytes are synchronized before the containing entry,
        and the created object's identity is recorded by the creating step.
        """
        self._require_armed("creating an object")
        traversal = self.inventory.traversal(directory_role)
        descriptor = self.filesystem.create_file(traversal, name)
        try:
            if content:
                self.filesystem.write(descriptor.number, content)
            if uid is not None and gid is not None:
                os.fchown(descriptor.number, uid, gid)
            os.fchmod(descriptor.number, mode)
            self.filesystem.fsync(descriptor.number, barrier="object-data")
            identity = ObjectIdentity.of(descriptor.number)
        finally:
            self.filesystem.close(descriptor.number)
        self.inventory.bind_synchronizable(directory_role)
        self.inventory.fsync_entry(directory_role)
        self._recorded[(directory_role, name)] = identity.object_id
        return identity.object_id

    # -- P2 -------------------------------------------------------------------

    def install_case_program(
        self,
        *,
        content: bytes,
        sha256: str,
        directory_role: str = "bin",
        name: str = "case-program",
        temporary: str = ".case-program.tmp",
        uid: int | None = None,
        gid: int | None = None,
        mode: int = 0o555,
        creation_mode: int = int(case_runtime.CASE_PROGRAM_TEMPORARY_MODE, 8),
        step_id: str = "",
    ) -> ObjectIdentity:
        """**P2.** Install the reviewed bytes from one held buffer.

        The digest is compared against the buffer this call was handed, at the
        last possible moment, and against `materialization.REVIEWED_DIGESTS`
        where the content is one the planning tier pinned. Content that changed
        between the manifest and the write is refused rather than installed.

        **The two modes are different modes — C-P5.0-LAB-I3-R3, 2026-09-20.**
        `creation_mode` is r6 §6.2's `0500`, given to the exclusive `openat`
        that makes the temporary pathname; `mode` is the ruled published
        `0555`, applied to the descriptor that `openat` returned. The sequence
        between them is unchanged and the descriptor is the authority
        throughout: the bytes are written to it, synchronized on it, and its
        ownership and final mode are applied to it, all before the exclusive
        link claims the final name. The temporary's creation mode never becomes
        the published mode.
        """
        self._require_armed("installing the case program")
        digest = hashlib.sha256(content).hexdigest()
        if digest != (sha256 or "").strip().lower():
            raise EffectRefused(
                "the bytes handed to the installation do not hash to the digest "
                "that travelled with them, so what would be installed is not "
                "what was reviewed."
            )
        traversal = self.inventory.traversal(directory_role)
        descriptor = self.filesystem.create_file(
            traversal, temporary, mode=creation_mode
        )
        try:
            self.filesystem.write(descriptor.number, content)
            if uid is not None and gid is not None:
                os.fchown(descriptor.number, uid, gid)
            os.fchmod(descriptor.number, mode)
            self.filesystem.fsync(descriptor.number, barrier="payload-data")
            identity = ObjectIdentity.of(descriptor.number)
        finally:
            self.filesystem.close(descriptor.number)
        self.filesystem.renameat(
            traversal, temporary, traversal, name, noreplace=True
        )
        self.inventory.bind_synchronizable(directory_role)
        self.inventory.fsync_entry(directory_role)
        self._recorded[(directory_role, name)] = identity.object_id
        return identity

    # -- P4 -------------------------------------------------------------------

    def set_inode_flags(
        self, *, directory_role: str, name: str, add: int, step_id: str = ""
    ) -> None:
        """**P4.** `ioctl(FS_IOC_SETFLAGS)` on the inode a descriptor holds.

        The pre-check is the genuine detection: the entry is opened relative to
        the held parent and its `fstat` is compared with the identity the
        creating step recorded. A mismatch refuses **before** the flag change,
        so a replacement of the *name* after the check cannot receive the flag.

        The residual interval is the lookup between `openat` and `fstat`, and it
        is covered by the quiescence gate — or the effect refuses.
        """
        self._require_armed("setting an inode flag")
        self.require_quiescence("setting an inode flag")
        descriptor = self._open_and_verify(directory_role, name)
        try:
            current = _read_inode_flags(descriptor)
            _write_inode_flags(descriptor, current | add)
        finally:
            self.filesystem.close(descriptor)

    def clear_inode_flags(
        self, *, directory_role: str, name: str, remove: int, step_id: str = ""
    ) -> None:
        """**L3's first half.** Clear the flag, on the descriptor. Still B2."""
        self._require_armed("clearing an inode flag")
        self.require_quiescence("clearing an inode flag")
        descriptor = self._open_and_verify(directory_role, name)
        try:
            current = _read_inode_flags(descriptor)
            _write_inode_flags(descriptor, current & ~remove)
        finally:
            self.filesystem.close(descriptor)

    # -- L3 -------------------------------------------------------------------

    def remove_object(
        self,
        *,
        directory_role: str,
        name: str,
        is_directory: bool = False,
        step_id: str = "",
    ) -> RemovalRecord:
        """**L3.** Pre-check, remove by name, post-check — and say what each is.

        There is no `funlink`. `unlinkat` resolves its final component at the
        time of the call and no flag binds that component to a previously
        observed inode, so removal cannot be made inode-bound by any syscall
        available here and this does not claim otherwise.

        1. **Prevention** — the quiescence gate, and it is the only prevention;
        2. **Pre-check** — `openat` + `fstat` against the recorded pair. A
           mismatch refuses **before** the removal and names both identities;
        3. **Removal** — whatever the name resolves to at the moment of the
           call; and
        4. **Post-check** — an absence check, and nothing more.
        """
        self._require_armed("removing an object")
        self.require_quiescence("removing an object")
        # **PR-20260913-LABI-2.** Three refusing inputs, all before `unlinkat`:
        # no recorded identity, no object at the pre-check, and an identity that
        # is not equal to the record. Equality is the only admitting branch.
        recorded = self._require_recorded(directory_role, name, "the removal")
        traversal = self.inventory.traversal(directory_role)
        found = self.filesystem.fstatat(traversal, name)
        if found is None:
            raise EffectRefused(
                "the object this run recorded is not at that name, so the "
                "removal has nothing to take and no basis for taking it. It is "
                "refused before it is issued.",
                classification=EFFECT_OBJECT_ABSENT,
            )
        if found != recorded:
            raise EffectRefused(
                "the object at that name is not the object this run recorded "
                f"when it created it: recorded {recorded!r}, found {found!r}. "
                "The removal is refused before it is issued and the run reports "
                "a detected substitution.",
                classification=EFFECT_IDENTITY_MISMATCH,
            )
        self.filesystem.unlinkat(traversal, name, directory=is_directory)
        after = self.filesystem.fstatat(traversal, name)
        return RemovalRecord(
            name=name,
            recorded_identity=recorded,
            pre_check_identity=found,
            removal_issued=True,
            post_check_identity=after,
            detected_substitution=False,
        )

    # -- the two configuration effects ---------------------------------------

    def declared_transfer(self) -> tuple:
        """The inherited descriptor table this run declared — r6 §§1.3.3, 6.3."""
        return self.inventory.transfer

    def publish_recovery_basis(
        self,
        *,
        run_id: str,
        reservation_id: str,
        captured_by: str,
        capture_set: ConfigurationCaptureSet,
        configuration_role: str,
        evidence_role: str = "",
        step_id: str = "",
    ) -> "StorePublication":
        """**§§1.4.3 and 2.3.3.** Capture and publish, before any mutation.

        The reviewed set is bound here, at the integration boundary, and the
        request is derived from it — so there is no parameter through which a
        caller substitutes a destination of its own. That is
        PR-20260913-LABI-1's binding, applied at the one place the executor
        captures anything.
        """
        self._require_armed("publishing the recovery basis")
        store = self.recovery
        if store is None:
            raise EffectRefused(
                "no independent recovery store was assembled, so a capture "
                "would have nowhere durable to publish to and the first "
                "configuration mutation has no recoverable basis."
            )
        store.bind_capture_set(capture_set)
        publication = store.publish(
            run_id=run_id,
            reservation_id=reservation_id,
            captured_by=captured_by,
            sources=dict(capture_set.destinations()),
            configuration_role=configuration_role,
        )
        if evidence_role and publication.mutation_permitted:
            # **r6 §2.5.** The retained evidence copy, written from the store
            # **after** the basis is durable — so it cannot precede the basis and
            # cannot be mistaken for it. `R/before` is evidence; the basis is
            # `/var/lib/freedom-blades/recovery/<run-id>/`, whose custody is not
            # the custody this run is about.
            for capture in publication.captures:
                self.create_object(
                    directory_role=evidence_role,
                    name=capture.name,
                    content=store.read_copy(run_id, capture.name),
                    mode=0o600,
                    step_id=step_id,
                )
        return publication

    def restore_configuration(
        self,
        *,
        run_id: str,
        configuration_role: str,
        destination_directory: str,
        owner_uid: int,
        owner_gid: int,
        mode: int = 0o640,
        step_id: str = "",
    ) -> "RestorationOutcome":
        """**§2.4 / L1.** Verify against the independent store, then write."""
        self._require_armed("restoring the configuration")
        store = self.recovery
        if store is None:
            raise EffectRefused(
                "no independent recovery store was assembled, so there is "
                "nothing to restore the pre-change configuration from."
            )
        return restore_configuration(
            inventory=self.inventory,
            filesystem=self.filesystem,
            store=store,
            run_id=run_id,
            configuration_role=configuration_role,
            destination_directory=destination_directory,
            owner_uid=owner_uid,
            owner_gid=owner_gid,
            mode=mode,
        )

    # -- internals ------------------------------------------------------------

    def recorded_identity(self, directory_role: str, name: str) -> str:
        """What the creating step recorded for this entry, or `""`.

        Exposed so a reviewer and a negative control can both see that the
        production path never consults it without requiring it.
        """
        return self._recorded.get((directory_role, name), "")

    def _require_recorded(self, directory_role: str, name: str, effect: str) -> str:
        """**PR-20260913-LABI-2.** The mandatory prerequisite, before anything.

        An absent or empty record refuses here, ahead of every lookup and every
        syscall that could change something. The contract's prerequisite is that
        the object *is the one the creating step recorded*; with nothing
        recorded there is no such object, and an effect issued anyway is an
        effect on something this run does not own.
        """
        recorded = self._recorded.get((directory_role, name), "")
        if not recorded:
            raise EffectRefused(
                f"{effect} requires the identity the creating step recorded for "
                f"this entry under role {directory_role!r}, and this run "
                "recorded none. A missing record is not an absent comparison: "
                "it is an object this run neither created nor owns, and the "
                "effect is refused before it is issued.",
                classification=EFFECT_IDENTITY_NOT_RECORDED,
            )
        return recorded

    def _open_and_verify(self, directory_role: str, name: str) -> int:
        """The pre-check for a flag effect: mandatory record, object, equality.

        One lookup, so there is no second interval between two of this run's own
        calls: `openat` resolves the entry and `fstat` of the descriptor it
        returned reports the object the effect will reach. The recorded identity
        is required **before** the lookup, an absent object refuses **before**
        any `ioctl`, and equality is the only admitting branch.
        """
        recorded = self._require_recorded(
            directory_role, name, "the descriptor-bound effect"
        )
        traversal = self.inventory.traversal(directory_role)
        try:
            descriptor = self.filesystem.openat(
                traversal, name, DescriptorMode.O_RDONLY
            )
        except DescriptorRefused as refusal:
            if refusal.classification == DESCRIPTOR_OBJECT_ABSENT:
                raise EffectRefused(
                    "the entry this run recorded does not resolve, so there is "
                    "no object to compare with the record and none to issue the "
                    "effect on. The effect is refused before any ioctl.",
                    classification=EFFECT_OBJECT_ABSENT,
                ) from None
            raise
        found = ObjectIdentity.of(descriptor.number).object_id
        if found != recorded:
            self.filesystem.close(descriptor.number)
            raise EffectRefused(
                "the entry resolved to a different object from the one this run "
                f"recorded: recorded {recorded!r}, found {found!r}. The effect "
                "is refused before it is issued.",
                classification=EFFECT_IDENTITY_MISMATCH,
            )
        return descriptor.number

    def record_identity(self, *, directory_role: str, name: str) -> str:
        """Record what a name resolves to now, so a later pre-check can compare.

        It records the result of a **lookup**, which is the only thing a later
        comparison can be against. Re-`fstat`ing the descriptor that produced it
        would compare a value with itself — r6 §1.1(1), withdrawn.
        """
        traversal = self.inventory.traversal(directory_role)
        found = self.filesystem.fstatat(traversal, name)
        if found is None:
            raise EffectRefused(
                "the name does not resolve, so there is no identity to record "
                "and nothing a later pre-check could compare against."
            )
        self._recorded[(directory_role, name)] = found
        return found


def _read_inode_flags(descriptor: int) -> int:
    """`ioctl(FS_IOC_GETFLAGS)` on a held descriptor.

    It is issued through `fcntl.ioctl` on the descriptor, so the request lands
    on the object the descriptor refers to. There is no argument kind through
    which a caller could name a different request number: both are constants in
    this module's own body.
    """
    buffer = array.array("i", [0])
    fcntl.ioctl(descriptor, FS_IOC_GETFLAGS, buffer, True)
    return int(buffer[0])


def _write_inode_flags(descriptor: int, value: int) -> None:
    buffer = array.array("i", [value])
    fcntl.ioctl(descriptor, FS_IOC_SETFLAGS, buffer, False)


#: The two `ioctl` request numbers, as constants in this module's body. They are
#: the same two the reviewed case program uses, and neither is reachable from a
#: vector.
FS_IOC_GETFLAGS = 0x80086601
FS_IOC_SETFLAGS = 0x40086602
#: The two flags the contract names: the append-only flag the journal carries
#: and the immutable flag the seal carries.
FS_APPEND_FL = 0x00000020
FS_IMMUTABLE_FL = 0x00000010

#: The numeric value of each reviewed flag name. `plan.EFFECT_FLAGS` carries the
#: names a step may write and the `chattr` letter each replaced; the numbers
#: live here, beside the `ioctl` request numbers, and neither is reachable from
#: an argument vector.
FLAG_VALUES: dict[str, int] = {
    "append_only": FS_APPEND_FL,
    "immutable": FS_IMMUTABLE_FL,
}


def _flag_mask(flags: Sequence[str]) -> int:
    """The mask a reviewed flag tuple denotes. An unknown name is a refusal."""
    mask = 0
    for flag in flags:
        if flag not in FLAG_VALUES or flag not in EFFECT_FLAGS:
            raise EffectRefused(
                "the effect names an inode flag outside the reviewed pair."
            )
        mask |= FLAG_VALUES[flag]
    return mask


#: Who a recovery publication records as its capturing identity. Fixed, so a
#: caller cannot write an attribution of its own into a stored record.
EFFECT_ISSUER = "the harness executor, as root"


__all__ = [
    "BEFORE_FIRST_STEP",
    "EFFECT_IDENTITY_MISMATCH",
    "EFFECT_IDENTITY_NOT_RECORDED",
    "EFFECT_OBJECT_ABSENT",
    "EFFECT_REFUSALS",
    "OWNERSHIP_BINDING_RULE",
    "CLEANUP_BOUNDARY_FAILURE",
    "EVIDENCE_ROLE",
    "FS_APPEND_FL",
    "FS_IMMUTABLE_FL",
    "FS_IOC_GETFLAGS",
    "FS_IOC_SETFLAGS",
    "POST_CHECK_ESTABLISHES",
    "QUIESCENCE_COST",
    "ROOT_ROLE",
    "RUN_DIRECTORIES",
    "DescriptorBoundEffects",
    "EffectRefused",
    "ExecutingRunner",
    "ExecutorRefused",
    "RemovalRecord",
    "MATERIALIZATION_NOT_APPLIED",
    "OPERATOR_INTERRUPTION",
    "PERMITTED_RUN_AS",
    "REFUSED_EXIT_CODE",
    "RunOutcome",
    "StepOutcome",
    "UNEXPECTED_EXECUTION_FAILURE",
]
