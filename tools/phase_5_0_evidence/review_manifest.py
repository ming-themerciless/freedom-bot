"""The deterministic pre-execution review manifest, and the digest the executor
demands before it runs anything.

## What the manifest is for

Codex reviews a concrete plan. The executor then runs one. Those are only the
same thing if something binds them, and a banner in a Markdown file does not: the
document can be re-rendered, the generator can be edited, and the plan the
executor builds at run time comes from the live tree either way.

The manifest is the binding. It is a canonical, byte-deterministic serialization
of **everything a reviewer approves** — the target's identity and confirmed
facts, the harness and schema versions, every argument vector, every declared
mutation, every derived cleanup vector, the exit classifications, the unresolved
conflicts, and the SHA-256 of every source file that produced them. Its digest is
one hex string.

## Why the reviewer's digest is a separate input, and must be

The executor recomputes the manifest from the live tree and compares it with a
digest **supplied on the command line**. It does not read an expected digest out
of a file in the same tree, and it does not write one. If it did, editing the
generator would edit the expectation in the same commit and the tree would
approve itself — the exact failure the prompt names. The approved value comes
from outside: Codex reads the manifest, decides, and hands back the digest as the
thing the operator must type. Any later edit to any covered source file changes
the recomputed digest, and the run refuses.

The digest covers the source files as well as the vectors, because two different
generators can emit the same vectors today and different ones tomorrow. Pinning
only the output would approve the output; pinning both approves the output *and*
the thing that produced it.

## What is deliberately not in it

No file content beyond digests, no host state, no credential, no observation and
no result. The manifest describes what **would** run. It is produced before
anything runs and it says nothing about a run, so it cannot be confused with
evidence.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping, Sequence

from application.idempotency import canonical_request_hash

from . import EVIDENCE_SCHEMA_VERSION, HARNESS_NAME, HARNESS_VERSION
from .approved_target import (
    APPROVED_TARGET_FACTS,
    CONFIRMATION_TOKEN,
    TARGET_IDENTITY_DIGEST,
)
from . import capability
from .capability import (
    EVIDENCE_IDENTITIES,
    e7_fact_confirmed,
    e7_target_facts_confirmed,
)
from .case_runtime import (
    CASE_PROGRAM_SOURCE,
    CASE_PROGRAM_SOURCE_PATH,
    CASE_VERBS,
    EXIT_OBSERVATION_UNAVAILABLE,
    EXPECTED_INTERPRETER_REAL_PATH,
    EXPECTED_INTERPRETER_SHA256,
    GENERATION_LINK_NAME,
    INTERPRETER_FLAGS,
    INTERPRETER_PATH,
    INTERPRETER_PYTHON_VERSION,
    OPEN_MODES,
    REFUSAL_EXIT_CODES,
    SECUREBITS_MAX,
    WRITE_MODES,
    case_program_path,
    interpreter_digest_confirmed,
    interpreter_real_path_confirmed,
)
from .concrete_plan import ConcretePlan
from .errors import PlanRefused
from .observations import (
    BAND_7_SCHEMA,
    COMPLETENESS_WITHHELD,
    IMPORTER_SCOPE,
    MAX_PAYLOAD_BYTES,
    MAX_RECORDS,
    OBSERVATION_SCHEMA,
    OBSERVATION_SCHEMA_VERSION,
    SYNTHETIC_TARGET_IDENTITY,
    Custody,
)
from .expectations import (
    CAPSH_CONSTRUCTED_IDENTITIES,
    ROOT_IDENTITY,
    case_runtime_contract,
    launcher_capability_contract,
)
from .required_cases import REQUIRED_CASES

#: The schema name the aggregate digest is computed under. Changing what the
#: manifest *means* changes this string, so a digest approved under an older
#: meaning stops matching rather than being silently reinterpreted.
MANIFEST_SCHEMA = "phase-5-0-evidence-review-manifest"

#: Bumped when the manifest's field set changes.
#:
#: **2** added `materializations` — conflict C-4's resolution: the reviewed
#: bytes, their digest, their destination, owner, group and mode, and the two
#: orderings each one declares.
#:
#: **3** adds `case_runtime` and per-step `bindings` — conflicts C-2 and C-5. A
#: digest approved under version 2 covered a plan that could run no case program
#: and substituted no identity, and it stops matching rather than being
#: reinterpreted as one that does both.
#:
#: **4** adds `expectations` and per-step `identity_name` — R12's disposition of
#: EH-R11-1 and EH-R11-2. A digest approved under version 3 covered a plan whose
#: `P-05` and `E1 … E8` observations were **recorded and never compared**, and
#: whose securebits was asserted from the presence of a `capsh` option rather
#: than observed. That is a different plan, not a differently rendered one, so it
#: stops matching rather than being reinterpreted.
#:
#: **5** replaces `expectations.case_identity`'s seven-identity list with one
#: covering `E1 … E6` and `E8` beside a new `expectations.root_identity` block —
#: R13's disposition of EH-R12-1. A digest approved under version 4 covered a
#: plan in which `E7` had **no identity step and no compared observation at
#: all**, and in which `P-01`/`P-02` were said to classify it. That is a
#: different plan, and the ten reviewed `E7` target facts it now depends on are
#: pinned here so a reviewer approves each value and its confirmed state rather
#: than discovering them from a run.
#: **7** adds per-step `catalog_question` and per-unresolved-item
#: `blocks_mutation_ids` — R14's disposition of EH-R14-1. A digest approved under
#: version 6 covered a plan whose database and role baselines proved absence with
#: a `psql` **failure** — exit 2 and exit 3 — and whose filesystem baseline proved
#: it with `stat`'s exit 1. Under all three, an object that was there could
#: satisfy the baseline and be deleted by cleanup. This is a different plan, not a
#: differently rendered one: two baselines now read a catalog listing whose
#: subject and control are pinned above, and the third establishes no ownership at
#: all. It stops matching rather than being reinterpreted.
#:
#: **8** is R16's resolution of C-6, C-7 and C-8, and it changes all three of the
#: things a digest is supposed to bind. The plan now carries the **three
#: immutable-flag experiments** rather than declaring them unresolved, so `E4`,
#: `E5` and `E6` reach the kernel with two verbs version 7's case program did not
#: have. It creates the disposable root by an **exclusive `mkdir(2)`** run from a
#: bootstrap location outside that root, so ownership comes from a creation
#: rather than from a probe and the 29 path mutations version 7 blocked are owned
#: again — by a different claim, pinned here as
#: `establishes_ownership_by_creation` and `establishes_ownership_of_contained`.
#: And it declares Band 7's cases as **externally produced**, with their producer,
#: their collection procedure and the closed importer schema their observations
#: must satisfy. A digest approved under version 7 covered a plan that ran none of
#: the experiments, created no file at all and had no ingestion stage. That is a
#: different plan, not a differently rendered one.
#:
#: **9** is R16's disposition of **EH-R16-2**, **EH-R16-3** and **EH-R16-4**, and
#: it changes what a Band-7 record *means*, what the plan *claims*, and what the
#: importer's result *is a result about*.
#:
#: * The supplied-observation schema is **version 2**: `JNL-51-PROVENANCE-OMITTED`
#:   carries `refused` and a `refusal_code` that may be `none`, and the observed
#:   result is passed through to the classifier and compared with the fixed
#:   expected `J-26`. Under version 8 the classifier constructed an observed
#:   `refused J-26` from APR/PVR absence alone, so a record reporting `DEP-04`
#:   was stored as a passing `refused J-26`.
#: * Band 7's three cases are **unresolved** again, under conflict C-7, and
#:   `is_executable` is `False`. Version 8 declared them externally supplied on
#:   the strength of a description of tooling that does not exist. Each case now
#:   carries both an unresolved entry and a documented input contract whose
#:   `producer_artifact_reviewed` is `False`, and a contract in that state
#:   occupies no coverage column.
#: * The importer declares its **scope** and withholds overall completeness and
#:   operational eligibility, which version 8 computed from Band 7 alone.
#:
#: A digest approved under version 8 covered a plan that reported itself
#: executable with three producers missing, and an importer that could report a
#: complete result with no capability evidence in it. That is a different plan.
#:
#: **10** is the LAB-1 repair — runner contract r6 §8.1, accepted 2026-09-12.
#: The supplied-observation schema is **version 3**: `JNL-47-RECOVERY-STATE`
#: records the two recovery causes and the two recovery procedures separately,
#: replacing the single `recovery_procedure_named`. Under version 9 the evidence
#: clause was one boolean over both procedures, so a run that left residue and
#: named only the *configuration* recovery satisfied *"the named operator
#: recovery is reported"*. That is the reporting gap LAB-1 named, relocated from
#: the outcome into the record that judges it. A digest approved under version 9
#: covered a plan whose recovery clause could be answered by the wrong
#: procedure, so it stops matching rather than being reinterpreted.
#:
#: **11** is the C-P5.0-LAB-I implementation of runner contract r6's
#: reserved-laboratory mechanism, 2026-09-13. It moves for two reasons and both
#: are changes in what a digest covers rather than in how a plan is rendered.
#:
#: * **The covered set grows by five files.** `execution/descriptors.py`,
#:   `execution/host_lock.py`, `execution/lifecycle_record.py`,
#:   `execution/recovery_store.py` and `execution/run_ledger.py` are the
#:   mechanism, and `provisioning.py` carries the r6 §7 definitions. A digest
#:   approved under version 10 covered a tree in which none of them existed, so
#:   it is not a digest for this one.
#: * **The reviewed verb table grows from 16 to 20.** r6 §6.2's four
#:   descriptor-relative verbs — `openat`, `unlinkat`, `renameat`, `fstatat` —
#:   and their two new argument kinds change what an admissible vector *is*. A
#:   digest approved under version 10 covered a grammar in which no vector could
#:   name a descriptor at all.
#:
#: What does **not** move: the supplied-observation schema stays at **3**, the
#: run-record schema at **3**, and `is_executable` stays `False` with C-7's
#: three cases declared unresolved. Implementation is not resolution, and a
#: digest is review input rather than execution approval in either version.
#: **12** is the C-P5.0-LAB-I-R1 remediation of Codex findings
#: PR-20260913-LABI-1, -2 and -3, 2026-09-14. It moves for three reasons, and
#: each is a change in what a digest covers rather than in how a plan is
#: rendered.
#:
#: * **The covered set grows by one file.** `execution/participants.py` is the
#:   repository-owned integration point for all seven entries of
#:   `reservation.PARTICIPATING_ENTRY_POINTS`. A digest approved under version
#:   11 covered a tree in which the protocol was enforced by nothing.
#: * **`plan.PERMITTED_EXECUTABLES` falls from 22 to 20.** r6 §6.4's retirement
#:   of `/usr/bin/install` and `/usr/bin/chattr` changes what an admissible
#:   vector *is*: a version-11 digest covered a grammar in which both were
#:   permitted and 27 reviewed steps named one of them.
#: * **Those 27 steps are no longer argument vectors.** They are
#:   descriptor-bound effects, reviewed as `plan.DescriptorEffect` rows, so the
#:   manifest pins an effect's kind, role, component, mode and ownership where
#:   it used to pin a command line.
#:
#: What does **not** move: the supplied-observation schema stays at **3**, the
#: run-record schema at **3**, and `is_executable` stays `False` with C-7's
#: three cases declared unresolved. Integration is repository wiring, not
#: permission to invoke it, and a digest is review input rather than execution
#: approval in either version.
MANIFEST_VERSION = 12

#: The source files whose exact bytes the manifest pins, relative to the
#: repository root. Enumerated rather than globbed: a file added to the package
#: without a decision about whether it belongs in the reviewed set should fail
#: the suite, not be swept in.
COVERED_SOURCES = (
    "tools/phase_5_0_evidence/__init__.py",
    "tools/phase_5_0_evidence/approved_target.py",
    "tools/phase_5_0_evidence/binding.py",
    "tools/phase_5_0_evidence/capability.py",
    "tools/phase_5_0_evidence/capture.py",
    "tools/phase_5_0_evidence/case_runtime.py",
    "tools/phase_5_0_evidence/cleanup.py",
    "tools/phase_5_0_evidence/concrete_plan.py",
    "tools/phase_5_0_evidence/durability_model.py",
    "tools/phase_5_0_evidence/errors.py",
    "tools/phase_5_0_evidence/execution/__init__.py",
    "tools/phase_5_0_evidence/execution/artifact.py",
    "tools/phase_5_0_evidence/execution/boundary.py",
    "tools/phase_5_0_evidence/execution/case_program.py",
    "tools/phase_5_0_evidence/execution/cli.py",
    "tools/phase_5_0_evidence/execution/descriptors.py",
    "tools/phase_5_0_evidence/execution/evidence_cli.py",
    "tools/phase_5_0_evidence/execution/executor.py",
    "tools/phase_5_0_evidence/execution/host_lock.py",
    "tools/phase_5_0_evidence/execution/lifecycle_record.py",
    "tools/phase_5_0_evidence/execution/materializer.py",
    "tools/phase_5_0_evidence/execution/participants.py",
    "tools/phase_5_0_evidence/execution/recovery_store.py",
    "tools/phase_5_0_evidence/execution/run_ledger.py",
    "tools/phase_5_0_evidence/expectations.py",
    "tools/phase_5_0_evidence/feasibility.py",
    "tools/phase_5_0_evidence/filesystem.py",
    "tools/phase_5_0_evidence/hba.py",
    "tools/phase_5_0_evidence/identity.py",
    "tools/phase_5_0_evidence/journal.py",
    "tools/phase_5_0_evidence/lifecycle_storage.py",
    "tools/phase_5_0_evidence/manifest.py",
    "tools/phase_5_0_evidence/materialization.py",
    "tools/phase_5_0_evidence/observations.py",
    "tools/phase_5_0_evidence/plan.py",
    "tools/phase_5_0_evidence/provenance.py",
    "tools/phase_5_0_evidence/provisioning.py",
    "tools/phase_5_0_evidence/records.py",
    "tools/phase_5_0_evidence/required_cases.py",
    "tools/phase_5_0_evidence/reservation.py",
    "tools/phase_5_0_evidence/review_manifest.py",
    "tools/phase_5_0_evidence/sudoers.py",
    "tools/phase_5_0_evidence/targets.py",
)

#: §2.13.2b's three exit classifications, pinned so a reviewer approves what each
#: exit code will mean rather than discovering it from a run.
EXIT_CLASSIFICATIONS = (
    (
        "S-C",
        0,
        "Every stage passed, every transient object was removed, and the restored "
        "PostgreSQL configuration was reloaded and observed to be in force.",
    ),
    (
        "S-A",
        2,
        "A stage failed or was inconclusive and cleanup completed. No residue, no "
        "generation artifact and no database row at any point.",
    ),
    (
        "S-B",
        3,
        "Cleanup could not remove an artifact, or could not prove the temporary "
        "authentication configuration gone. Each remaining artifact is named by "
        "absolute path; every unresolved effective-configuration risk is named in "
        "full; the next invocation refuses while they exist and does not clean "
        "them.",
    ),
    (
        "REFUSED",
        4,
        "The run never started: the target was not the approved one, the reviewed "
        "digest was absent or differed, the confirmation token was wrong, or the "
        "plan still carries an unresolved conflict.",
    ),
)


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _effect_row(effect) -> dict | None:
    """**r6 §1.4, C-P5.0-LAB-I-R1.** One descriptor-bound effect, pinned.

    This is what the manifest pins where it used to pin an `install` or a
    `chattr` command line. Every field is a name or a number a reviewer
    approves, and none of them is a pathname the executor resolves: the role
    selects a descriptor the inventory already holds and the component is one
    path component under it. `path` is documentation — the absolute path the
    object has — and nothing resolves it.

    `None` for a command step, so a reviewer reading the manifest sees which
    steps are effects and which are vectors without inferring it from an empty
    `argv`.
    """
    if effect is None:
        return None
    return {
        "kind": effect.kind.value,
        "directory_role": effect.directory_role,
        "name": effect.name,
        "path": effect.path,
        "mode": f"{effect.mode:04o}" if effect.mode else "",
        "owner": effect.owner,
        "group": effect.group,
        "flags": list(effect.flags),
        "payload_source": effect.payload_source,
        "configuration_role": effect.configuration_role,
        "components": list(effect.components),
        "evidence_role": effect.evidence_role,
    }


@dataclass(frozen=True, slots=True)
class ReviewManifest:
    """The reviewed object. Built from a plan and from supplied source bytes.

    Source bytes are **supplied**, not read: this module keeps the planning
    tier's rule that nothing here opens a file, so the reviewer and the executor
    both hand it the same thing and neither can be surprised by a read it did not
    make. The CLI does the reading, and it reads only `COVERED_SOURCES`.
    """

    plan: ConcretePlan
    source_digests: tuple[tuple[str, str], ...]

    @classmethod
    def build(
        cls, plan: ConcretePlan, source_bytes: Mapping[str, bytes]
    ) -> "ReviewManifest":
        missing = [name for name in COVERED_SOURCES if name not in source_bytes]
        if missing:
            raise PlanRefused(
                "The review manifest covers every source file that produces the "
                f"vectors, and these were not supplied: {missing}. A manifest over "
                "a subset would approve a plan without approving the code that "
                "generates it."
            )
        extra = sorted(set(source_bytes) - set(COVERED_SOURCES))
        if extra:
            raise PlanRefused(
                f"{extra} were supplied but are not in COVERED_SOURCES. The covered "
                "set is enumerated so that adding a file to the package is a "
                "decision rather than a side effect."
            )
        digests = tuple(
            (name, _sha256_hex(source_bytes[name])) for name in COVERED_SOURCES
        )
        return cls(plan=plan, source_digests=digests)

    def digest_for(self, path: str) -> str:
        """The covered-source digest for one pinned path.

        It exists so the executor can bind `P-05`'s expected `case_program_sha256`
        to **the bytes the reviewer approved** rather than to a hash it computes
        for itself or reads back from the installed file. `install` copies bytes,
        so the source digest is the installation digest.
        """
        for name, digest in self.source_digests:
            if name == path:
                return digest
        raise PlanRefused(
            f"{path!r} is not one of the manifest's covered sources, so it has no "
            "reviewed digest to compare anything against."
        )

    # -- the canonical body -------------------------------------------------

    def as_mapping(self) -> dict[str, object]:
        """Everything a reviewer approves, in a shape `json.dumps` can sort.

        Every value is a scalar or a list of scalars. No object identity, no
        timestamp, no path relative to the machine it ran on, and nothing that
        differs between two runs over the same tree — that is what makes the
        digest a statement about the plan rather than about the run that produced
        it.
        """
        plan = self.plan
        return {
            "manifest_schema": MANIFEST_SCHEMA,
            "manifest_version": MANIFEST_VERSION,
            "harness_name": HARNESS_NAME,
            "harness_version": HARNESS_VERSION,
            "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
            "target_identity": plan.target.identity,
            "target_identity_digest": TARGET_IDENTITY_DIGEST,
            "confirmation_token": CONFIRMATION_TOKEN,
            "target_facts": [
                {"name": name, "value": value}
                for name, value in APPROVED_TARGET_FACTS.as_fields()
            ],
            "target_fields": {
                "host": plan.target.host,
                "root_path": plan.target.root_path,
                "database_name": plan.target.database_name,
                "postgres_socket_directory": plan.target.postgres_socket_directory,
                "postgres_config_directory": plan.target.postgres_config_directory,
                "confirmed_disposable": plan.target.confirmed_disposable,
                "disposability_evidence": plan.target.disposability_evidence,
            },
            "mutations": [
                {
                    "mutation_id": mutation.mutation_id,
                    "kind": mutation.kind.value,
                    "identifier": mutation.identifier,
                    "file_path": mutation.file_path,
                    "group": mutation.group,
                    "maps_os_user": mutation.maps_os_user,
                    "maps_postgres_role": mutation.maps_postgres_role,
                    "reason": mutation.reason,
                }
                for mutation in plan.mutations
            ],
            "steps": [
                {
                    "step_id": step.step_id,
                    "band": step.band,
                    "run_as": step.run_as,
                    "argv": list(step.argv),
                    # **r6 §6.4, C-P5.0-LAB-I-R1.** The descriptor-bound effect
                    # this step is instead of a command, or `null`.
                    "effect": _effect_row(step.effect),
                    "purpose": step.purpose,
                    "evidence_case_ids": list(step.evidence_case_ids),
                    "mutation_ids": list(step.mutation_ids),
                    "role": step.role.value,
                    "capture": step.capture.value,
                    # **R12.** Which reviewed identity contract this step's
                    # observation is compared against, or empty for a step that
                    # observes no constructed identity. A reviewer approves the
                    # pairing rather than the executor inferring it.
                    "identity_name": step.identity_name,
                    "satisfying_statuses": list(step.satisfying_statuses),
                    "refusal_required": step.refusal_required,
                    "expected_result": step.expected_result,
                    "expected_refusal": step.expected_refusal,
                    # **Conflict C-5.** The permitted binding sites, pinned per
                    # step: which argument index, which prefix, which kind, which
                    # names, and the exact symbolic argument the reviewed vector
                    # carries there. A reviewer approves the substitution set,
                    # not merely the vector it applies to, and the executor may
                    # change nothing outside it.
                    "bindings": [
                        {
                            "argument_index": site.argument_index,
                            "kind": site.kind.value,
                            "prefix": site.prefix,
                            "names": list(site.names),
                            "symbolic_argument": site.symbolic_argument,
                        }
                        for site in step.bindings
                    ],
                    # **R13, EH-R13-3.** The reviewed semantic expectation for
                    # the observation this step records, pinned per step. What a
                    # prerequisite *means* is reviewed beside what it runs, and
                    # the digest changes when either does. Empty for the three
                    # policies whose contract is derived from reviewed constants
                    # and for `exit_status_only`, which records nothing.
                    "observation_expectations": [
                        {
                            "key": item.key,
                            "comparison": item.comparison.value,
                            "expected": item.value,
                            "uncompared_because": item.uncompared_because,
                        }
                        for item in step.observation_expectations
                    ],
                    # **R13, EH-R13-1.** The declared mutations this step proves
                    # **absent** before anything changes, and the exit statuses
                    # with which its executable reports that its object already
                    # existed. Together they decide which objects this run's
                    # cleanup is entitled to remove.
                    "establishes_ownership_of": list(step.establishes_ownership_of),
                    "preexisting_statuses": list(step.preexisting_statuses),
                    # **R14, EH-R14-1.** The two names a catalog reading answers
                    # about. They are pinned here because the vector cannot carry
                    # them: the reviewed grammar admits no string literal, so the
                    # listing is unfiltered and *which name this baseline is
                    # about* exists only in the plan. A reviewer approves the
                    # subject and the control, and the digest changes when either
                    # does. `null` for every step that reads no catalog.
                    "catalog_question": (
                        {
                            "subject": step.catalog_question.subject,
                            "control": step.catalog_question.control,
                        }
                        if step.catalog_question is not None
                        else None
                    ),
                    # **R16, conflict C-8.** The other way ownership is
                    # established, pinned beside the probe-based one so a
                    # reviewer sees which claim each object's deletion rests on.
                    # `establishes_ownership_by_creation` is the object this step
                    # created exclusively; `establishes_ownership_of_contained`
                    # is what that empty directory then contains; and
                    # `nothing_created_statuses` is the set that separates *"the
                    # creation was refused, so the host is untouched"* from *"it
                    # may exist and cannot be identified"*.
                    "establishes_ownership_by_creation": list(
                        step.establishes_ownership_by_creation
                    ),
                    "establishes_ownership_of_contained": list(
                        step.establishes_ownership_of_contained
                    ),
                    "nothing_created_statuses": list(step.nothing_created_statuses),
                }
                for step in plan.steps
            ],
            "cleanup_steps": [
                {
                    "step_id": step.step_id,
                    "kind": step.kind.value,
                    "run_as": step.run_as,
                    "argv": list(step.argv),
                    # **r6 §6.4, C-P5.0-LAB-I-R1.** The descriptor-bound effect
                    # this step is instead of a command, or `null`.
                    "effect": _effect_row(step.effect),
                    "removes": step.removes,
                    "mutation_ids": list(step.mutation_ids),
                    "satisfying_statuses": list(step.satisfying_statuses),
                    "refusal_required": step.refusal_required,
                    # **R13, EH-R13-2 and R16, conflict C-8.** What a cleanup step
                    # waits for, and what it may record. `requires_satisfied` is
                    # the configuration phase a step that deletes a recovery input
                    # waits for; `requires_revalidated` is the identity reading the
                    # one exclusively created object's removal waits for;
                    # `applies_with` is what decides a revalidation's applicability,
                    # since it reverses nothing; and `capture` is `exit_status_only`
                    # for every step but that one.
                    "requires_satisfied": list(step.requires_satisfied),
                    "requires_revalidated": step.requires_revalidated,
                    "applies_with": list(step.applies_with),
                    "capture": step.capture.value,
                }
                for step in plan.cleanup_plan.steps
            ],
            "materializations": [
                {
                    "step_id": item.step_id,
                    "band": item.band,
                    "run_as": item.run_as,
                    "destination": item.destination,
                    "filename": item.file.filename,
                    "lines": list(item.file.lines),
                    "byte_count": item.file.byte_count,
                    "sha256": item.file.sha256,
                    "owner": item.file.owner,
                    "group": item.file.group,
                    "mode": f"{item.file.mode:04o}",
                    "capture_step_id": item.capture_step_id,
                    "after_step_id": item.after_step_id,
                    "mutation_ids": list(item.mutation_ids),
                    "evidence_case_ids": list(item.evidence_case_ids),
                    "role": item.role.value,
                    "purpose": item.purpose,
                    "expected_result": item.expected_result,
                    "expected_refusal": item.expected_refusal,
                }
                for item in plan.materializations
            ],
            # **Conflict C-2.** The runtime every case-program vector names, and
            # the closed grammar it may be followed by. Pinned here so a reviewer
            # approves the interpreter, its isolation flags, the program path,
            # the verb vocabulary and each verb's arity — and so any later edit
            # to any of them changes the digest and the run refuses.
            "case_runtime": {
                "interpreter_path": INTERPRETER_PATH,
                "interpreter_flags": list(INTERPRETER_FLAGS),
                "interpreter_python_version": INTERPRETER_PYTHON_VERSION,
                "expected_interpreter_sha256": EXPECTED_INTERPRETER_SHA256,
                "expected_interpreter_sha256_confirmed": interpreter_digest_confirmed(),
                "expected_interpreter_real_path": EXPECTED_INTERPRETER_REAL_PATH,
                "expected_interpreter_real_path_confirmed": (
                    interpreter_real_path_confirmed()
                ),
                "securebits_max": SECUREBITS_MAX,
                "exit_observation_unavailable": EXIT_OBSERVATION_UNAVAILABLE,
                "case_program_source": CASE_PROGRAM_SOURCE,
                "case_program_source_path": CASE_PROGRAM_SOURCE_PATH,
                "case_program_installed_path": case_program_path(plan.target),
                "generation_link_name": GENERATION_LINK_NAME,
                "open_modes": list(OPEN_MODES),
                "write_modes": list(WRITE_MODES),
                "refusal_exit_codes": [
                    {"errno": name, "exit_code": REFUSAL_EXIT_CODES[name]}
                    for name in sorted(REFUSAL_EXIT_CODES)
                ],
                "verbs": [
                    {
                        "verb": name,
                        "arity": CASE_VERBS[name].arity,
                        "arguments": [
                            kind.value for kind in CASE_VERBS[name].arguments
                        ],
                        "purpose": CASE_VERBS[name].purpose,
                    }
                    for name in sorted(CASE_VERBS)
                ],
            },
            # **R12 — the semantic expectations, pinned.** What each observation
            # verb's output must equal before its step may be satisfied. Exit
            # status 0 is necessary and not sufficient, and this is the part a
            # reviewer approves: the values are all derived from reviewed
            # constants, from §2.13.5c's seven-step mask derivation, and — for
            # the case program's own digest — from this manifest's covered-source
            # entry, which `install` copies byte for byte. None of them is
            # learned from the observation being judged.
            #
            # The three numeric identity values `--uid=`, `--gid=` and
            # `--groups=` carry are **not** here for the seven constructed
            # identities: the four disposable names do not exist until Band 2
            # creates them, so the reviewed vector pins the names (see
            # `steps[].bindings`) and the executor compares the observation
            # against the numbers the bound vector asked the kernel for. `E7`
            # is the exception and its three are pinned below, because it
            # assumes nobody: it has no `--uid=` to resolve, and its uid is a
            # fact about the host like its masks are.
            # **R13, EH-R13-4.** The required evidence cases, and for each one
            # the step that produces it or the conflict that blocks it. A
            # required case in neither column cannot exist: `build_concrete_plan`
            # refuses, which is what makes `is_executable` a statement about
            # completeness rather than about what the generator happened to try.
            "required_cases": [
                {
                    "case_id": case.case_id,
                    "band": case.band,
                    "asserts": case.asserts,
                    "source": case.source,
                    "produced_by": sorted(
                        step.step_id
                        for step in plan.steps
                        if case.case_id in step.evidence_case_ids
                    ),
                    "blocked_by": sorted(
                        item.conflict_id
                        for item in plan.unresolved
                        if case.case_id in item.evidence_case_ids
                    ),
                    # **R16, conflict C-7.** The third column. A required case is
                    # produced by a step, declared unresolved, or externally
                    # produced with a named producer — and in exactly one of the
                    # three, which `required_cases.check_case_coverage` refuses a
                    # plan for violating.
                    "supplied_externally": any(
                        item.case_id == case.case_id for item in plan.external_cases
                    ),
                }
                for case in REQUIRED_CASES
            ],
            # **R16, conflict C-7.** Every required case whose producer is not a
            # step of this plan, with the actor that makes the observation, the
            # procedure that collects it, and the variants an importer requires
            # before it is covered. A reviewer approves *who* produces the
            # evidence and *how*, and the digest changes when either does.
            "external_cases": [
                {
                    "case_id": item.case_id,
                    "band": item.band,
                    "producer": item.producer,
                    "collection_procedure": item.collection_procedure,
                    "variants": list(item.variants),
                    "why_not_a_step": item.why_not_a_step,
                    # **R16, EH-R16-4.** Whether a reviewed producer artifact
                    # exists, and therefore whether this contract discharges the
                    # evidence dependency or merely documents its input shape.
                    # Pinned, so a change from documentation to resolution is a
                    # digest change and a re-review.
                    "producer_artifact_reviewed": item.producer_artifact_reviewed,
                    "producer_review_reference": item.producer_review_reference,
                    "resolves_coverage": item.resolves_coverage,
                }
                for item in plan.external_cases
            ],
            # **R16, conflict C-7.** The importer's contract, pinned: the schema a
            # supplied payload is written under, its version, the bound in bytes
            # and records, the closed custody vocabulary, the synthetic marker,
            # and — per case — the exact field names and value shapes a record
            # may carry. There is no free-text field in it, so a supplied record
            # cannot name a command, an executable, an identity, a path, a token
            # or an expected value.
            "supplied_observations": {
                "schema": OBSERVATION_SCHEMA,
                "schema_version": OBSERVATION_SCHEMA_VERSION,
                # **R16, EH-R16-3.** What an importer result is a result about,
                # and the two judgements it withholds. Pinned so the scope a
                # reviewer reads in an artifact is the scope the reviewed tree
                # declares.
                "importer_scope": IMPORTER_SCOPE,
                "withheld": list(COMPLETENESS_WITHHELD),
                "synthetic_target_identity": SYNTHETIC_TARGET_IDENTITY,
                "max_records": MAX_RECORDS,
                "max_payload_bytes": MAX_PAYLOAD_BYTES,
                "custody_levels": [member.value for member in Custody],
                "cases": [
                    {
                        "case_id": schema.case_id,
                        "band": schema.band,
                        "in_harness_producer": schema.in_harness_producer,
                        "variants": list(schema.variants),
                        "fields": [
                            {"name": spec.name, "shape": spec.shape}
                            for spec in schema.fields
                        ],
                    }
                    for schema in [
                        BAND_7_SCHEMA[name] for name in sorted(BAND_7_SCHEMA)
                    ]
                ],
            },
            "expectations": {
                "launcher_capabilities": (
                    [
                        {"key": key, "expected": value}
                        for key, value in launcher_capability_contract()
                        .expected_observations()
                    ]
                    if capability.e7_target_facts_confirmed()
                    else "unconfirmed — E7's reviewed target facts are not stated"
                ),
                "case_runtime": [
                    {"key": key, "expected": value}
                    for key, value in case_runtime_contract(
                        case_program_installed_path=case_program_path(plan.target),
                        case_program_sha256=self.digest_for(CASE_PROGRAM_SOURCE),
                    ).expected_observations()
                ],
                "case_identity": [
                    {
                        "identity": name,
                        "user": identity.user,
                        "primary_group": identity.primary_group,
                        "supplementary_groups": list(identity.supplementary_groups),
                        "cap_inh": f"{identity.expected_masks()['cap_inh']:#x}",
                        "cap_prm": f"{identity.expected_masks()['cap_prm']:#x}",
                        "cap_eff": f"{identity.expected_masks()['cap_eff']:#x}",
                        "cap_bnd": f"{identity.expected_masks()['cap_bnd']:#x}",
                        "cap_amb": f"{identity.expected_masks()['cap_amb']:#x}",
                        "securebits": f"{identity.expected_masks()['securebits']:#x}",
                        "no_new_privs": 0,
                    }
                    for name, identity in sorted(EVIDENCE_IDENTITIES.items())
                    if name in CAPSH_CONSTRUCTED_IDENTITIES
                ],
                # **R13 — `E7`, the eighth identity, pinned as reviewed target
                # facts.** R12's `case_identity` list above stopped at seven and
                # said `P-01`/`P-02` classified the eighth. They do not: neither
                # runs the case program, and `capsh --print` reports the
                # securebits of `capsh`'s own process rather than of the final
                # interpreted one. `E7` now has a step of its own, and because it
                # constructs nothing it has no derivation and no bound vector to
                # take a value from — so each of the ten is a fact about the host
                # that the Operations Owner states and an independent reviewer
                # verifies. They are pinned with their **confirmed state**, so
                # supplying one changes this manifest's digest and triggers the
                # re-review it should, and so a reviewer can see at a glance that
                # the plan is fully specified and operationally blocked.
                "root_identity": {
                    "identity": ROOT_IDENTITY,
                    "user": EVIDENCE_IDENTITIES[ROOT_IDENTITY].user,
                    # Read through the module, exactly as `case_runtime`'s
                    # reviewed facts are read where they are used: supplying a
                    # fact must take effect where it is supplied, or the manifest
                    # would pin one value while the contract compared another.
                    "facts": [
                        {
                            "name": name,
                            "value": capability.E7_TARGET_FACTS[name],
                            "confirmed": e7_fact_confirmed(name),
                        }
                        for name in sorted(capability.E7_TARGET_FACTS)
                    ],
                    "confirmed": e7_target_facts_confirmed(),
                },
            },
            "cleanup_traceability": [
                {"mutation_id": row[0], "performed_by": row[1], "reversed_by": row[2]}
                for row in plan.traceability()
            ],
            "unresolved": [
                {
                    "step_ref": item.step_ref,
                    "band": item.band,
                    "conflict_id": item.conflict_id,
                    "design_requires": item.design_requires,
                    "why_not_a_vector": item.why_not_a_vector,
                    "what_would_resolve_it": item.what_would_resolve_it,
                    "evidence_case_ids": list(item.evidence_case_ids),
                    # **R14, EH-R14-1.** The declared mutations a blocked
                    # ownership baseline leaves unowned. Pinned so a reviewer sees
                    # which objects this run may not create, and therefore which
                    # reversals can never run.
                    "blocks_mutation_ids": list(item.blocks_mutation_ids),
                }
                for item in plan.unresolved
            ],
            "exit_classifications": [
                {"state": state, "exit_code": code, "meaning": meaning}
                for state, code, meaning in EXIT_CLASSIFICATIONS
            ],
            "source_digests": [
                {"path": path, "sha256": digest} for path, digest in self.source_digests
            ],
        }

    def serialize(self) -> bytes:
        """Byte-deterministic JSON: sorted keys, fixed separators, one newline.

        Two runs over the same tree produce identical bytes, which is the only
        reason a digest over them means anything.
        """
        text = json.dumps(
            self.as_mapping(), sort_keys=True, indent=2, separators=(",", ": ")
        )
        return (text + "\n").encode("utf-8")

    def digest(self) -> str:
        """The aggregate the executor requires, in the package's canonical
        typed encoding rather than as a bare hash of bytes."""
        body = self.serialize()
        return canonical_request_hash(
            MANIFEST_SCHEMA,
            (
                ("manifest_version", MANIFEST_VERSION),
                ("harness_version", HARNESS_VERSION),
                ("target_identity_digest", TARGET_IDENTITY_DIGEST),
                ("step_count", len(self.plan.steps)),
                ("mutation_count", len(self.plan.mutations)),
                ("cleanup_step_count", len(self.plan.cleanup_plan.steps)),
                ("materialization_count", len(self.plan.materializations)),
                ("binding_site_count", sum(len(step.bindings) for step in self.plan.steps)),
                (
                    "expectation_step_count",
                    sum(
                        1
                        for step in self.plan.steps
                        if step.capture.value in ("case_runtime", "case_identity")
                    ),
                ),
                ("unresolved_count", len(self.plan.unresolved)),
                # **R14, EH-R14-1.** How many steps establish ownership from a
                # catalog reading, in the digest alongside the counts above, so a
                # plan that quietly went back to proving absence with an exit
                # status cannot present the same aggregate.
                (
                    "catalog_baseline_count",
                    sum(
                        1
                        for step in self.plan.steps
                        if step.catalog_question is not None
                    ),
                ),
                # **R16, conflict C-8.** How many steps establish ownership by
                # creating their object rather than by probing for it, in the
                # digest alongside the counts above, so a plan that quietly went
                # back to a probe cannot present the same aggregate.
                (
                    "creation_ownership_count",
                    sum(
                        1
                        for step in self.plan.steps
                        if step.establishes_ownership_by_creation
                    ),
                ),
                # **R16, conflict C-7.** How many required cases are externally
                # produced. A plan that moved a case out of the run and into a
                # supplied record without saying so changes this number.
                ("external_case_count", len(self.plan.external_cases)),
                ("body_sha256", _sha256_hex(body)),
            ),
        ).hex()


def digests_match(reviewed: str, recomputed: str) -> bool:
    """Case-insensitive, whitespace-tolerant, and length-checked.

    A reviewer pastes a digest. Being strict about a trailing newline would turn
    a correct approval into a refusal, and being loose about a prefix would turn
    a wrong one into an approval — so the comparison normalises exactly
    surrounding whitespace and case, and nothing else.
    """
    left = (reviewed or "").strip().lower()
    right = (recomputed or "").strip().lower()
    return bool(left) and len(left) == len(right) and left == right


__all__ = [
    "COVERED_SOURCES",
    "EXIT_CLASSIFICATIONS",
    "MANIFEST_SCHEMA",
    "MANIFEST_VERSION",
    "ReviewManifest",
    "digests_match",
]
