"""Shared positive fixtures for the evidence-harness suite.

It is deliberately **not** a `conftest.py`: nothing here is a pytest fixture, a
hook or a plugin, and a module that is imported by name is easier to follow than
one pytest injects. It is imported explicitly by the three modules that drive a
whole run across an injected boundary.

Two things live here. `runnable_plan()` is the plan every module that drives a
whole run needs — the real one, with its declared blockers taken as decided; see
its own docstring for what that suspends and why the harness does not.

`observations_for()` exists because R12 made *"the boundary
answered"* insufficient: a step whose capture policy carries a semantic
expectation is satisfied only when its **observation** matches, so a fake
boundary that scripts an exit status and no observation now scripts a failure.

`observations_for()` produces the observation a compliant case program would
print for one step, from the same reviewed contract the executor compares
against. That is deliberately not a proof that the real program prints it —
`test_case_program.py` asserts the program's own emitted key set against the
policy and the contract, and `test_expectations.py` asserts every mismatch is
refused. This is the *positive* fixture, so that the rest of the suite can go on
exercising cleanup, ordering, interruption and materialization against a run that
gets as far as it should.

**Nothing here reads a host account, starts a process, opens a socket or touches
a file.** `test_no_execution.py` scans every `*.py` in this directory, including
this one — the scan was widened from `test_*.py` to `*.py` for exactly that
reason.
"""
from __future__ import annotations

import hashlib
from dataclasses import replace
from typing import Sequence

from tools.phase_5_0_evidence import capability
from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.binding import bind_arguments
from tools.phase_5_0_evidence.capture import CapturePolicy
from tools.phase_5_0_evidence.case_runtime import (
    CASE_PROGRAM_SOURCE,
    case_program_path,
)
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence.execution.executor import (
    CREATED_IDENTITY_KEYS,
    EFFECT_IDENTITY_NOT_RECORDED,
    EffectRefused,
)
from tools.phase_5_0_evidence.execution.materializer import (
    RESTORATION_BARRIERS,
    RestorationOutcome,
)
from tools.phase_5_0_evidence.execution.recovery_store import (
    BARRIER_ORDER,
    StorePublication,
)
from tools.phase_5_0_evidence.expectations import contract_for

#: The four disposable identities, resolved from a table rather than a host.
#: Every fake lookup in this suite states the same numbers, and they are numbers
#: this file chose: no test here consults `pwd` or `grp`, which
#: `test_no_execution.py` asserts.
DISPOSABLE_ACCOUNTS = {
    "freedomcoord": (5001, 5001),
    "freedomsheet": (5002, 5002),
    "fbprobe": (5003, 5003),
    # `postgres` is **pre-existing**, not disposable. The reviewed restoration
    # `fchown`s the configuration back to it — r6 §2.4 — so the injected NSS
    # boundary has to answer for it. The numbers are this file's.
    "postgres": (900, 900),
}
DISPOSABLE_GROUPS = {
    "freedomcoord": 5001,
    "freedomsheet": 5002,
    "fbprobe": 5003,
    "postgres": 900,
    "freedomjournal": 5004,
}

#: Stand-ins for `E7`'s ten reviewed target facts, which ship `UNCONFIRMED` — the
#: same device `REVIEWED_INTERPRETER_DIGEST` is for the interpreter's.
#:
#: **They are deliberately not §2.13.5c's 2026-08-31 host row.** The capability
#: masks below are an obviously synthetic `0x1234`, and the supplementary set is
#: an obviously synthetic pair, precisely so that a test which passes proves the
#: contract took its expectation from `capability.E7_TARGET_FACTS` and from
#: nowhere else: a contract that had quietly fallen back to `DOCUMENTED_ROOT_MASK`
#: would fail against these. `uid` and `gid` are `0` because `E7` **is** root and
#: no honest fixture makes it anything else.
#:
#: **Nothing here is a fact about `oracle-test`.** No test in this suite reads a
#: host, and supplying the real values remains a maintainer decision that no
#: authorization in force grants.
REVIEWED_E7_FACTS = {
    "uid": "0",
    "gid": "0",
    "groups": "0,4242",
    "cap_inh": "1234",
    "cap_prm": "1234",
    "cap_eff": "1234",
    "cap_bnd": "1234",
    "cap_amb": "1234",
    "no_new_privs": "0",
    "securebits": "2a",
}


def supply_reviewed_e7_facts(monkeypatch) -> None:
    """State `E7`'s ten reviewed target facts for the length of one test.

    `ExecutingRunner` refuses at construction while any of them is unconfirmed —
    gate 4 — so every module that drives a whole run across an injected boundary
    calls this from its autouse fixture, exactly as it monkeypatches the two
    interpreter facts. The patch is applied to the **module attribute**, because
    that is how `expectations.root_identity_contract`, the executor's gate, the
    review manifest and the renderer all read it.
    """
    monkeypatch.setattr(capability, "E7_TARGET_FACTS", REVIEWED_E7_FACTS)


class RecordingEffects:
    """A descriptor-bound effect issuer that **records and writes nothing**.

    The injected seam for r6 §1.4's effects, and the reason it exists is the
    reason `Boundary` exists: the object that can really `mkdirat`, `ioctl` and
    `unlinkat` is `executor.DescriptorBoundEffects` over a real inventory, and
    no test in this suite may hold one — `test_no_execution.py` asserts that
    this directory constructs no armed real writer.

    It is **not** a default. `ExecutingRunner.effects` defaults to `None`, and
    an executor assembled without an issuer refuses every effect step rather
    than falling back to a pathname-based command. A test that wants a run to
    get past `B3-03` says so by passing one of these.

    `refuse` names the effects this issuer refuses, keyed by the step's
    `(kind, name)`, so a test can make exactly one effect fail.
    """

    def __init__(self, *, refuse: Sequence[str] = (), publication=None) -> None:
        self.issued: list[tuple[str, str, str]] = []
        #: The reviewed step id each effect came from, in order. `ProcessBoundary`
        #: takes `step_id` for the same reason: two steps legitimately issue the
        #: same effect — the capability band resets a flag Band 3 set — and a
        #: double that could not tell them apart could not report which one ran.
        self.steps: list[str] = []
        self.refuse = set(refuse)
        self.transfer: tuple = ()
        self._publication = publication
        self._recorded: set[tuple[str, str]] = set()

    # -- what the executor calls ---------------------------------------------

    def declared_transfer(self) -> tuple:
        return self.transfer

    def create_directory_object(
        self, *, parent_role, name, role="", mode=0o700, step_id=""
    ):
        return self._record("create_directory", parent_role, name, step_id)

    def create_object(
        self,
        *,
        directory_role,
        name,
        content=b"",
        uid=None,
        gid=None,
        mode=0o640,
        step_id="",
    ):
        return self._record("create_object", directory_role, name, step_id)

    def install_case_program(
        self,
        *,
        content,
        sha256,
        directory_role="bin",
        name="case-program",
        temporary=".case-program.tmp",
        uid=None,
        gid=None,
        mode=0o555,
        step_id="",
    ):
        if hashlib.sha256(content).hexdigest() != sha256:
            raise AssertionError("the fake issuer still checks the digest")
        return self._record("install_payload", directory_role, name, step_id)

    def set_inode_flags(self, *, directory_role, name, add, step_id=""):
        self._require_recorded(directory_role, name)
        self._record("set_flag", directory_role, name, step_id)

    def clear_inode_flags(self, *, directory_role, name, remove, step_id=""):
        self._require_recorded(directory_role, name)
        self._record("clear_flag", directory_role, name, step_id)

    def remove_object(
        self, *, directory_role, name, is_directory=False, step_id=""
    ):
        self._require_recorded(directory_role, name)
        return self._record("remove_object", directory_role, name, step_id)

    def publish_recovery_basis(
        self,
        *,
        run_id,
        reservation_id,
        captured_by,
        capture_set,
        configuration_role,
        evidence_role="",
        step_id="",
    ):
        self._record("capture_configuration", configuration_role, run_id, step_id)
        if self._publication is not None:
            return self._publication
        return StorePublication(
            published=True,
            mutation_permitted=True,
            barriers_crossed=BARRIER_ORDER,
            run_directory_name=run_id,
        )

    def restore_configuration(
        self,
        *,
        run_id,
        configuration_role,
        destination_directory,
        owner_uid,
        owner_gid,
        mode=0o640,
        step_id="",
    ):
        self._record("restore_configuration", configuration_role, run_id, step_id)
        return RestorationOutcome(
            renamed=(run_id,), durable=True, barriers_crossed=RESTORATION_BARRIERS
        )

    # -- internals ------------------------------------------------------------

    def _record(self, kind: str, role: str, name: str, step_id: str = "") -> str:
        keys = {
            kind,
            name,
            step_id,
            f"{role}/{name}",
            f"{kind}:{name}",
            f"{kind}:{role}/{name}",
        }
        keys.discard("")
        if keys & self.refuse:
            raise EffectRefused(f"the fake issuer was asked to refuse {kind}.")
        self.issued.append((kind, role, name))
        self.steps.append(step_id)
        if kind in ("create_directory", "create_object", "install_payload"):
            self._recorded.add((role, name))
        return f"{role}/{name}"

    def _require_recorded(self, role: str, name: str) -> None:
        """**PR-20260913-LABI-2, mirrored in the double.**

        The fake refuses an unrecorded object for the same reason the real
        issuer does, so a plan that ordered a flag or a removal before the
        creation that records it fails here rather than passing on a double that
        was more permissive than the thing it stands for.
        """
        if (role, name) not in self._recorded:
            raise EffectRefused(
                "no creating-step identity was recorded for this entry.",
                classification=EFFECT_IDENTITY_NOT_RECORDED,
            )


def refusing_effects(step, **keywords) -> RecordingEffects:
    """A `RecordingEffects` that refuses exactly one reviewed effect step.

    The counterpart of scripting a `CommandResult` for a command step: an effect
    starts no process, so a test that wants one to fail says so here.
    """
    return RecordingEffects(refuse=(step.step_id,), **keywords)


def runnable_plan() -> ConcretePlan:
    """The real plan, as it would be once its declared blockers were decided.

    The submitted plan is **not** executable and the executor's second gate
    refuses it. What makes that true is **conflict C-7**, and three unresolved
    items carry it:

    * Band 7's three evidence cases observe nothing this plan does, and the
      producers that would make those observations do not exist — R16's
      **EH-R16-4**. An importer is a route in, not a producer, so the cases are
      declared unresolved and a supplied record cannot close one. The run this
      fixture drives does not carry them, and the unresolved items are dropped
      here, exactly as every module's own copy of this helper did before R14.

    Dropping them is a **fixture's** licence and not a claim: it lets the tests
    below exercise provisioning, execution and cleanup, which is what they are
    about. `test_r16_remediation.py` asserts the gate against the shipped plan.

    **C-6 and C-8 are no longer suspended, because they are no longer blocked.**
    R16 implements both: the three immutable-flag experiments are generated
    steps, and the disposable root is created by an exclusive `mkdir(2)` whose
    success is its own ownership. Nothing in this fixture reattaches an ownership
    the harness refuses — the previous version had to, and the fact that it no
    longer does is the difference C-8's resolution makes.
    """
    real = build_concrete_plan()
    return ConcretePlan(
        execution_plan=real.execution_plan,
        cleanup_plan=real.cleanup_plan,
        unresolved=(),
    )


def creation_step(plan: ConcretePlan):
    """The one step that establishes ownership by exclusive creation, or `None`."""
    for step in plan.steps:
        if step.establishes_ownership_by_creation:
            return step
    return None


def revalidation_observations(
    plan: ConcretePlan, source_bytes: dict[str, bytes]
) -> tuple[tuple[str, str], ...]:
    """What `statroot` must report for cleanup to remove the root it created.

    **Conflict C-8.** The executor compares the revalidation's observation with
    the one the creation made; this returns the creation's two identity keys, so
    a positive fixture's cleanup agrees with its own run. A test that wants the
    replaced-path case scripts different numbers instead.
    """
    step = creation_step(plan)
    if step is None:
        return ()
    made = observations_for(step, bound_argv(step), source_bytes)
    return tuple((key, value) for key, value in made if key in CREATED_IDENTITY_KEYS)


def cleanup_observations_for(
    step, plan: ConcretePlan, source_bytes: dict[str, bytes]
) -> tuple[tuple[str, str], ...]:
    """What a compliant boundary reports for one **cleanup** step.

    Empty for every step but the one revalidation — conflict **C-8** — which
    reads the created root's device and inode back so the executor can compare
    them with what the creation reported. A fake that scripted an exit status and
    no observation would script a mismatch, and the `rmdir` it guards would be
    skipped and the run reported S-B.
    """
    if step.capture is CapturePolicy.EXIT_STATUS_ONLY:
        return ()
    return revalidation_observations(plan, source_bytes)


def bound_argv(step, *, accounts=None, groups=None) -> tuple[str, ...]:
    """The vector the executor would hand the boundary for this step.

    A step with no declared binding site is its own vector; §2.13.5c's `capsh`
    steps have their three sites substituted, exactly as `ExecutingRunner._bind`
    does it and through the same function.
    """
    if not step.bindings:
        return tuple(step.argv)
    accounts = DISPOSABLE_ACCOUNTS if accounts is None else accounts
    groups = DISPOSABLE_GROUPS if groups is None else groups
    return bind_arguments(
        step.argv,
        step.bindings,
        resolve_uid=lambda name: accounts[name][0],
        resolve_gid=lambda name: groups[name],
    )


def observations_for(
    step, argv: Sequence[str], source_bytes: dict[str, bytes]
) -> tuple[tuple[str, str], ...]:
    """The complete observation that satisfies this step's reviewed contract.

    Empty only for an `EXIT_STATUS_ONLY` step, which records nothing. Since R13
    every other policy carries a contract — the three derived from reviewed
    constants and the rest declared on the step — so a fake boundary that scripts
    an exit status and no observation now scripts a failure for **every**
    observation-bearing step rather than for nine of them.
    """
    contract = contract_for(
        capture=step.capture,
        identity_name=step.identity_name,
        argv=tuple(argv),
        case_program_installed_path=case_program_path(APPROVED_TARGET),
        case_program_sha256=hashlib.sha256(
            source_bytes[CASE_PROGRAM_SOURCE]
        ).hexdigest(),
        declared=step.observation_expectations,
        subject=step.step_id,
    )
    return () if contract is None else contract.satisfying_observations()
