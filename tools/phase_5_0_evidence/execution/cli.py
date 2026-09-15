"""The only entry point that can reach the executing runner.

    python -m tools.phase_5_0_evidence.execution.cli                 # dry run
    python -m tools.phase_5_0_evidence.execution.cli --manifest      # print it
    python -m tools.phase_5_0_evidence.execution.cli --render PATH   # write plan
    python -m tools.phase_5_0_evidence.execution.cli --execute \\
        --confirm-target '<token>' --reviewed-digest '<hex>'

## A default invocation is a dry run, and that is structural

With no arguments the CLI builds the plan, prints what would run, and constructs
a `RecordingBoundary` and a `RecordingMaterializer` — objects with no path to a
process and no path to a file. The `SubprocessBoundary` and the
`SystemMaterializer` are each constructed on exactly one line, inside the
`--execute` branch, and armed on that same line. There is no configuration,
environment variable or default that arms either, and importing this module arms
nothing: `main` runs only under `__main__`.

## The three things `--execute` needs, and why each is separate

* **`--execute`** — the operator's statement that this is not a rehearsal.
* **`--confirm-target`** — the exact token derived from the approved target's
  identity. It says *which* host, root and database, so a run against a rebuilt
  or re-pointed target refuses instead of proceeding against something that
  merely looks similar.
* **`--reviewed-digest`** — Codex's approval of the exact plan. Supplied from
  outside, never read from the tree and never written by this CLI, so the tree
  cannot approve itself.

Any one of them missing is a refusal, and the refusal names which. They are three
arguments rather than one because they are three different people's statements:
the operator's, the Operations Owner's, and the reviewer's.

## What it reads and what it writes

It reads exactly `review_manifest.COVERED_SOURCES`, relative to the repository
root, to compute the manifest. It writes only where told: `--manifest-out` for
the manifest JSON, `--render` for the human-readable concrete plan. It writes no
evidence artifact unless the run completed and `RunOutcome.artifact_admissible`
is true, and today it cannot: the executor refuses while the interpreter's
expected SHA-256, its expected resolved path or any of `E7`'s ten reviewed target
facts is unsupplied, and it would refuse again without the exact confirmation
token and a reviewer-supplied digest.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Protocol, Sequence

from ..approved_target import APPROVED_TARGET_FACTS, CONFIRMATION_TOKEN
from ..case_runtime import (
    CASE_PROGRAM_SOURCE,
    CASE_PROGRAM_SOURCE_PATH,
    CASE_VERBS,
    EXPECTED_INTERPRETER_SHA256,
    GENERATION_LINK_NAME,
    INTERPRETER_FLAGS,
    INTERPRETER_PATH,
    INTERPRETER_PYTHON_VERSION,
    EXIT_OBSERVATION_UNAVAILABLE,
    EXPECTED_INTERPRETER_REAL_PATH,
    OPEN_MODES,
    REFUSAL_EXIT_CODES,
    WRITE_MODES,
    case_program_path,
    interpreter_digest_confirmed,
    interpreter_real_path_confirmed,
)
from .. import capability
from ..capability import (
    EVIDENCE_IDENTITIES,
    e7_fact_confirmed,
    unconfirmed_e7_facts,
)
from ..capture import CapturePolicy
from ..concrete_plan import ConcretePlan, build_concrete_plan
from ..errors import HarnessError, PlanRefused
from ..expectations import (
    CAPSH_CONSTRUCTED_IDENTITIES,
    ROOT_IDENTITY,
    case_runtime_contract,
)
from ..review_manifest import COVERED_SOURCES, ReviewManifest
from .artifact import (
    NOT_ADMISSIBLE,
    NO_DESTINATION,
    RunRecordRefused,
    write_run_record,
)
from .boundary import RecordingBoundary, SubprocessBoundary
from .descriptors import DescriptorInventory, PosixFilesystem
from .executor import (
    EVIDENCE_ROLE,
    REFUSED_EXIT_CODE,
    ROOT_ROLE,
    DescriptorBoundEffects,
    ExecutingRunner,
    ExecutorRefused,
)
from .materializer import RecordingMaterializer, SystemMaterializer
from .participants import (
    PARTICIPANT_ENTRY_POINTS,
    EffectPermit,
    HarnessObservations,
    HarnessRun,
    ParticipantIntegration,
    ParticipantRefused,
    validate_run_identifier,
)
from .recovery_store import RecoveryStore
from ..durability_model import Quiescence
from ..lifecycle_storage import Participant
from ..reservation import ReservationRequest

#: The repository root, three levels up from this file. Computed rather than
#: configured, so the covered-source read cannot be pointed somewhere else.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def read_covered_sources(root: Path = REPOSITORY_ROOT) -> dict[str, bytes]:
    """The exact bytes of every file the manifest pins.

    Reads only `COVERED_SOURCES` — an enumerated tuple, not a glob — so this
    function cannot be made to read anything else by adding a file to a
    directory. A missing file is an error rather than an omission: a manifest
    over a subset would approve a plan without approving the code that made it.
    """
    contents: dict[str, bytes] = {}
    for relative in COVERED_SOURCES:
        path = root / relative
        if not path.is_file():
            raise HarnessError(
                f"{relative} is covered by the review manifest and is not present. "
                "The manifest pins every source that produces the vectors, so a "
                "missing one is a refusal rather than a shorter manifest."
            )
        contents[relative] = path.read_bytes()
    return contents


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_plan(
    plan: ConcretePlan, manifest_digest: str, manifest_source_digest: str
) -> str:
    """The concrete plan as Markdown, deterministically.

    `manifest_source_digest` is the review manifest's covered-source digest for
    `case_runtime.CASE_PROGRAM_SOURCE`. It is passed in rather than computed here
    for the same reason the executor takes it from the manifest: it is the
    reviewer's own value for the bytes `install` copies, and a document that
    hashed the file for itself would be showing a reviewer something other than
    what the run will compare.

    Same tree, same bytes. There is no timestamp, no host name of the machine
    that rendered it and no ordering that depends on a set, because the document
    is what Codex reviews line by line and a diff that changes on every render is
    a diff nobody reads.
    """
    lines: list[str] = []
    add = lines.append

    add("# NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED")
    add("")
    add("## Package 5.0 evidence harness — generated concrete plan")
    add("")
    add(
        "Generated by `tools/phase_5_0_evidence/concrete_plan.py` against the "
        "disposable target Peter Duscha confirmed on 2026-09-05. **Nothing in "
        "this document has been executed.** It supersedes nothing: the "
        "placeholder template in "
        "`phase-5-0-evidence-harness-execution-plan.md` §§3-6 is retained there "
        "as the reviewed history this was generated from."
    )
    add("")
    add(f"Review-manifest digest: `{manifest_digest}`")
    add("")
    add(f"Target confirmation token: `{CONFIRMATION_TOKEN}`")
    add("")

    add("## 1. The approved target")
    add("")
    add("| Fact | Value |")
    add("|---|---|")
    for name, value in APPROVED_TARGET_FACTS.as_fields():
        add(f"| {name.replace('_', ' ')} | `{value}` |")
    add("")
    add(f"Disposability: {plan.target.disposability_evidence}")
    add("")

    add("## 1.1 The case-program runtime — conflict C-2, Option B")
    add("")
    add(
        "Every syscall-level case runs through one explicitly named interpreter. "
        "The interpreter is **not** a member of `plan.PERMITTED_EXECUTABLES`: it "
        "is admitted only by `case_runtime.validate_case_vector`, which matches "
        "the whole vector against the closed grammar below, before process "
        "creation and again — through `plan.validate_argv` — immediately before "
        "`execve`. The case program validates the same vector a third time from "
        "its own constants."
    )
    add("")
    add("| Fact | Value |")
    add("|---|---|")
    add(f"| interpreter | `{INTERPRETER_PATH}` |")
    add(f"| isolation flags | `{' '.join(INTERPRETER_FLAGS)}` |")
    add(f"| python version | `{INTERPRETER_PYTHON_VERSION}` |")
    add(
        "| expected interpreter SHA-256 | "
        f"`{EXPECTED_INTERPRETER_SHA256}` "
        f"({'confirmed' if interpreter_digest_confirmed() else '**a reviewed target fact that has not been supplied — the executor refuses while it is unconfirmed**'}) |"
    )
    add(
        "| expected resolved interpreter path | "
        f"`{EXPECTED_INTERPRETER_REAL_PATH}` "
        f"({'confirmed' if interpreter_real_path_confirmed() else '**a reviewed target fact that has not been supplied — the executor refuses while it is unconfirmed**'}) |"
    )
    add(f"| reviewed source | `{CASE_PROGRAM_SOURCE}` |")
    add(f"| installed from | `{CASE_PROGRAM_SOURCE_PATH}` |")
    add(f"| installed at | `{case_program_path(plan.target)}` |")
    add(
        "| installation digest | the review manifest's `source_digests` entry "
        f"for `{CASE_PROGRAM_SOURCE}` — `install` copies bytes, so the source "
        "digest **is** the installation digest |"
    )
    add("")
    add(
        "The interpreter digest covers the interpreter executable's own bytes "
        "and nothing else. The operating system, the dynamic loader, the shared "
        "libraries and the standard library on disk are disposable-host "
        "prerequisites, exactly as they already are for `capsh`, `chattr`, "
        "`install`, `psql` and `systemd-run`, none of which is hashed either."
    )
    add("")
    add("| Verb | Arity | Arguments | What it does |")
    add("|---|---|---|---|")
    for name in sorted(CASE_VERBS):
        spec = CASE_VERBS[name]
        arguments = ", ".join(kind.value for kind in spec.arguments) or "—"
        add(f"| `{name}` | {spec.arity} | {arguments} | {spec.purpose} |")
    add("")
    add(
        "`open_mode` is one of "
        + ", ".join(f"`{mode}`" for mode in OPEN_MODES)
        + "; `write_mode` is one of "
        + ", ".join(f"`{mode}`" for mode in WRITE_MODES)
        + f"; `link_name` is the one relative name `{GENERATION_LINK_NAME}`; and "
        "`target_path` is an absolute, normalized path strictly inside the "
        "disposable root."
    )
    add("")
    add(
        "The case program reports a refusal through its **exit status** as well "
        "as its output, from a closed table — "
        + ", ".join(
            f"`{name}` = {REFUSAL_EXIT_CODES[name]}"
            for name in sorted(REFUSAL_EXIT_CODES)
        )
        + " — so a step that may record only its exit status still carries the "
        "errno its case is stated in, and a vector the program itself refused "
        "(64) can never stand in for a denial by the boundary under test."
    )
    add("")

    add("## 2. Declared mutations, in provisioning order")
    add("")
    add("| # | Mutation id | Kind | Object | Why |")
    add("|---|---|---|---|---|")
    for index, mutation in enumerate(plan.mutations, start=1):
        add(
            f"| M-{index:02d} | `{mutation.mutation_id}` | {mutation.kind.value} | "
            f"`{mutation.identifier}` | {mutation.reason} |"
        )
    add("")

    add("## 3. Generated argument vectors")
    add("")
    add("| Step | Band | Runs as | Role | Argument vector | Satisfied by | Mutations | Evidence cases |")
    add("|---|---|---|---|---|---|---|---|")
    for step in plan.steps:
        satisfied = (
            "a non-zero exit (must be refused)"
            if step.refusal_required
            else ", ".join(str(status) for status in step.satisfying_statuses)
        )
        add(
            f"| `{step.step_id}` | {step.band} | `{step.run_as}` | "
            f"{step.role.value} | `{' '.join(step.argv)}` | {satisfied} | "
            f"{', '.join(step.mutation_ids) or '—'} | "
            f"{', '.join(step.evidence_case_ids) or '—'} |"
        )
    add("")
    add("### 3.1 What each step expects")
    add("")
    add("| Step | Purpose | Expected result | Expected refusal | May record |")
    add("|---|---|---|---|---|")
    for step in plan.steps:
        add(
            f"| `{step.step_id}` | {step.purpose} | {step.expected_result or '—'} | "
            f"{step.expected_refusal or '—'} | `{step.capture.value}` |"
        )
    add("")

    add("### 3.1a Late-bound identities — conflict C-5")
    add("")
    bound_steps = [step for step in plan.steps if step.bindings]
    if not bound_steps:
        add("None.")
        add("")
    else:
        add(
            "`capsh --uid=`, `--gid=` and `--groups=` take **numbers**, and the "
            "four names below do not exist until Band 2 creates them. The "
            "reviewed vector therefore carries the names; the executor resolves "
            "each through the injected NSS boundary immediately before the step, "
            "requires exactly one consistent record, validates the numeric form, "
            "substitutes **only** the sites listed here, and revalidates the "
            "complete final vector — Option-B prefix and case-program grammar "
            "included — before process creation. A change anywhere outside a "
            "listed site is refused."
        )
        add("")
        add("| Step | Argument | Kind | Symbolic argument | Names |")
        add("|---|---|---|---|---|")
        for step in bound_steps:
            for site in step.bindings:
                add(
                    f"| `{step.step_id}` | {site.argument_index} | "
                    f"{site.kind.value} | `{site.symbolic_argument}` | "
                    f"{', '.join(site.names)} |"
                )
        add("")

    add("### 3.1b Semantic expectations — what must be observed, not merely exited")
    add("")
    add(
        "Exit status 0 is necessary and **not sufficient** for the two "
        "observation verbs. Immediately after the capture boundary sanitizes a "
        "step's output and **before** its satisfaction is decided, the executor "
        "compares the observation against the closed contract below: every "
        "expected key must be present exactly once, be readable, and equal its "
        "expected value. A missing, duplicated, unreadable, unexpected or "
        "unequal value makes the step unsatisfied, stops the run there, and "
        "leaves every dependent case uninterpreted and unrun. No expected value "
        "is learned from the observation it is compared with."
    )
    add("")
    runtime_steps = [
        step.step_id
        for step in plan.steps
        if step.capture is CapturePolicy.CASE_RUNTIME
    ]
    add(
        "**`case_runtime` — "
        + (", ".join(f"`{step_id}`" for step_id in runtime_steps) or "no step")
        + "**"
    )
    add("")
    add("| Key | Expected value |")
    add("|---|---|")
    for key, value in case_runtime_contract(
        case_program_installed_path=case_program_path(plan.target),
        case_program_sha256=manifest_source_digest,
    ).expected_observations():
        add(f"| `{key}` | `{value}` |")
    add("")
    identity_steps = {
        step.identity_name: step.step_id
        for step in plan.steps
        if step.capture is CapturePolicy.CASE_IDENTITY
    }
    add(
        "**`case_identity` — §2.13.5c's `E1 … E6` and `E8`, the seven `capsh` "
        "constructs.** `uid`, `gid` and `groups` are compared against the "
        "numbers the **bound** vector's `--uid=`, `--gid=` and `--groups=` asked "
        "the kernel for, because the four disposable names do not exist until "
        "Band 2 creates them; `groups` is compared as a set. The masks, "
        "`no_new_privs` and the securebits are §2.13.5c's seven-step derivation. "
        "**The securebits is read by `prctl(PR_GET_SECUREBITS)` inside the "
        "exec'd process**, after `capsh`'s construction and after `execve` — not "
        "inferred from the `--secbits=` option in the vector."
    )
    add("")
    add(
        "| Identity | Step | User | Primary group | Supplementary | CapPrm/Eff/Inh/Amb/Bnd | NoNewPrivs | Securebits |"
    )
    add("|---|---|---|---|---|---|---|---|")
    for name in sorted(CAPSH_CONSTRUCTED_IDENTITIES):
        identity = EVIDENCE_IDENTITIES[name]
        masks = identity.expected_masks()
        add(
            f"| `{name}` | `{identity_steps.get(name, '—')}` | "
            f"`{identity.user}` | `{identity.primary_group}` | "
            f"{', '.join(f'`{group}`' for group in identity.supplementary_groups) or '—'} | "
            f"`{masks['cap_prm']:#x}` / `{masks['cap_eff']:#x}` / "
            f"`{masks['cap_inh']:#x}` / `{masks['cap_amb']:#x}` / "
            f"`{masks['cap_bnd']:#x}` | `0` | `{masks['securebits']:#x}` |"
        )
    add("")
    add(
        "A securebits that cannot be read at all is not a pass and not a "
        f"refusal: the case program exits `{EXIT_OBSERVATION_UNAVAILABLE}`, which "
        "is in no step's satisfying statuses."
    )
    add("")
    add(
        f"**`case_identity` — `{ROOT_IDENTITY}`, at step "
        f"`{identity_steps.get(ROOT_IDENTITY, '—')}`.** `E7` is the harness's own "
        "root identity: §2.13.5c gives it *\"no invocation … no securebit set "
        "and no drop of any kind\"*, so its step is the **direct** Option-B "
        "vector rather than a `capsh` construction, it substitutes nothing, and "
        "it runs as `root`. It observes the same twelve values through the same "
        "`identity` verb in the same final interpreted process, and its "
        "securebits comes from the same `prctl(PR_GET_SECUREBITS)` call. "
        "Because it constructs nothing there is no `M` to derive a mask from and "
        "no bound vector to read a number out of, so **each of the ten "
        "environment values is a reviewed target fact**: stated by the "
        "Operations Owner for this target and verified by an independent "
        "reviewer, never learned from `P-01`, `P-02`, this observation, `/proc`, "
        "`id` or `capsh`. `P-01` and `P-02` are unchanged and remain the separate "
        "preflight evidence they were."
    )
    add("")
    add("| Reviewed E7 target fact | Value | State |")
    add("|---|---|---|")
    for fact in sorted(capability.E7_TARGET_FACTS):
        add(
            f"| `{fact}` | `{capability.E7_TARGET_FACTS[fact]}` | "
            + (
                "confirmed"
                if e7_fact_confirmed(fact)
                else "**not supplied — the executor refuses while it is unconfirmed**"
            )
            + " |"
        )
    add("")

    add("### 3.2 Materialised configuration — conflict C-4")
    add("")
    if not plan.materializations:
        add("None.")
        add("")
    else:
        add(
            "These write file **content**, which no argument vector expresses, so "
            "they are not commands and carry no `argv`. The bytes below are the "
            "whole of what may be written: the destination comes from "
            "`DisposableTarget.config_path()`, the content and its digest come "
            "from the closed table in `materialization.py`, and the executor "
            "refuses each one unless the byte-exact pre-change capture it is "
            "restored from was taken and satisfied."
        )
        add("")
        add(
            "| Step | Runs after | Requires capture | Destination | Owner | Group "
            "| Mode | Bytes | SHA-256 | Reverses |"
        )
        add("|---|---|---|---|---|---|---|---|---|---|")
        for item in plan.materializations:
            add(
                f"| `{item.step_id}` | `{item.after_step_id}` | "
                f"`{item.capture_step_id}` | `{item.destination}` | "
                f"`{item.file.owner}` | `{item.file.group}` | "
                f"`{item.file.mode:04o}` | {item.file.byte_count} | "
                f"`{item.file.sha256}` | {', '.join(item.mutation_ids) or '—'} |"
            )
        add("")
        for item in plan.materializations:
            add(f"#### `{item.step_id}` — `{item.destination}`")
            add("")
            add(f"- **Purpose:** {item.purpose}")
            add(f"- **Expected result:** {item.expected_result or '—'}")
            add(f"- **Expected refusal:** {item.expected_refusal or '—'}")
            add(
                "- **Evidence cases:** " + (", ".join(item.evidence_case_ids) or "—")
            )
            add("")
            add("```")
            for line in item.file.lines:
                add(line)
            add("```")
            add("")

    add("## 4. Derived cleanup")
    add("")
    add("| Step | Kind | Runs as | Argument vector | Satisfied by | Reverses |")
    add("|---|---|---|---|---|---|")
    for step in plan.cleanup_plan.steps:
        satisfied = (
            "a non-zero exit (must be refused)"
            if step.refusal_required
            else ", ".join(str(status) for status in step.satisfying_statuses)
        )
        add(
            f"| `{step.step_id}` | {step.kind.value} | `{step.run_as}` | "
            f"`{' '.join(step.argv)}` | {satisfied} | "
            f"{', '.join(step.mutation_ids) or '—'} |"
        )
    add("")

    add("## 5. Mutation-to-cleanup traceability")
    add("")
    add("| Mutation | Performed by | Reversed by |")
    add("|---|---|---|")
    for mutation_id, performed, reversed_by in plan.traceability():
        add(f"| `{mutation_id}` | {performed} | {reversed_by} |")
    add("")

    add("## 5b. Reviewed observation expectations — R13, EH-R13-3")
    add("")
    add(
        "What each step's **observation** must say for the step to be satisfied. "
        "Exit status 0 is necessary and not sufficient, and this is the half R12 "
        "did not have: nine capture policies recorded an observation and were "
        "decided by their exit status, so a `capsh` reporting an empty bounding "
        "set and a `getent` reporting an unexpected member were both passes."
    )
    add("")
    add("| Step | Policy | Key | Comparison | Expected | Not compared because |")
    add("|---|---|---|---|---|---|")
    for step in plan.steps:
        for item in step.observation_expectations:
            add(
                f"| `{step.step_id}` | `{step.capture.value}` | `{item.key}` | "
                f"`{item.comparison.value}` | `{item.value}` | "
                f"{item.uncompared_because or '—'} |"
            )
    add("")
    add(
        "The three policies absent from this table — `capability_masks`, "
        "`case_runtime` and `case_identity` — are compared against reviewed "
        "constants rather than against anything a step could declare for itself: "
        "the interpreter's two target facts, this manifest's covered-source "
        "digest, §2.13.5c's mask derivation and `capability.E7_TARGET_FACTS`. "
        "Their expected values are in sections 7 and 8."
    )
    add("")

    add("## 5c. Ownership baselines — R13, EH-R13-1")
    add("")
    add(
        "Cleanup removes an object only where a step observed it **absent before "
        "anything changed**. Without that, a reversal deletes whatever happened "
        "to be there: R12 ran the whole declared cleanup once any mutation had "
        "been attempted, so a run that stopped on its second `groupadd` deleted "
        "three groups it never reached and dropped a database no step created."
    )
    add("")
    add(
        "**R14, EH-R14-1 corrects how three of them proved it.** R13 read a "
        "**failure** as absence wherever the tool had one, and `psql` exit 2, "
        "`psql` exit 3 and `stat` exit 1 are not absence results: exit 2 is a "
        "connection failure and `pg_database.datallowconn = false` produces it "
        "for a database that exists, exit 3 is any statement error under "
        "`ON_ERROR_STOP=1`, and coreutils gives every `stat` failure the same 1. "
        "The two PostgreSQL baselines now read a catalog listing the server "
        "**returns**, compared with a subject that must be absent and a control "
        "that must be present. `getent`'s exit 2 is kept: it is documented as "
        "*key not found*, distinct from its 1 and 3."
    )
    add("")
    add(
        "**R16, conflict C-8 resolves the filesystem baseline R14 had to block.** "
        "It is not repaired as a better probe, because no permitted executable "
        "has one: it is replaced by a **creation**. `B3-01` runs `mkdir(2)` on "
        "the disposable root through the reviewed case program's bootstrap copy, "
        "and the successful creation **is** the ownership — there is no "
        "preliminary absence check, so there is no window in which the object "
        "can arrive between the observation and the creation. `mkdir(2)` reports "
        "a path that is already occupied as `EEXIST`, uniquely and documentedly, "
        "and reports it for a directory, a file, a symbolic link and a dangling "
        "symbolic link alike."
    )
    add("")
    add(
        "The bootstrap copy is the reviewed **source** in the repository tree, "
        "because a helper that creates this root cannot first be installed "
        "inside it and installing it anywhere else would create a second object "
        "with the same unprovable pre-existence. That file is not a host object "
        "this run creates, modifies or removes, `install` later copies its exact "
        "bytes to `<root>/bin/case`, and one manifest digest covers both copies."
    )
    add("")
    add("| Creation step | Owns by creating | Owns as contained | Already exists | Nothing created |")
    add("|---|---|---|---|---|")
    for step in plan.steps:
        if step.establishes_ownership_by_creation:
            add(
                f"| `{step.step_id}` | "
                f"{', '.join(f'`{item}`' for item in step.establishes_ownership_by_creation)} | "
                f"{len(step.establishes_ownership_of_contained)} mutations | "
                f"exit {', '.join(str(code) for code in step.preexisting_statuses)} | "
                f"exit {', '.join(str(code) for code in step.nothing_created_statuses)} |"
            )
    add("")
    add(
        "Any other unsatisfied outcome — an internal failure, an identity the "
        "creation could not read, a timeout, a launch that never reported, an "
        "operator interruption — is the **uncertain** case: a directory may "
        "exist and this run cannot identify it, so the path is reported as "
        "bounded residue with the named operator recovery and is never removed. "
        "Cleanup re-reads the root's device and inode immediately before the one "
        "`rmdir` that would remove it and compares them with what the creation "
        "reported, so a path whose object was replaced does not inherit "
        "permission to have its replacement deleted."
    )
    add("")
    add("| Baseline step | Proves absent | How | Mutations it makes removable |")
    add("|---|---|---|---|")
    for step in plan.steps:
        if step.establishes_ownership_of:
            subjects = list(step.establishes_ownership_of)
            shown = ", ".join(f"`{item}`" for item in subjects[:4])
            if len(subjects) > 4:
                shown += f", … ({len(subjects)} in total)"
            if step.catalog_question is not None:
                how = (
                    "successful listing; subject "
                    f"`{step.catalog_question.subject}` absent, control "
                    f"`{step.catalog_question.control}` present"
                )
            elif step.observation_expectations:
                how = "compared observation, section 5b"
            else:
                how = (
                    "exit "
                    + ", ".join(str(code) for code in step.satisfying_statuses)
                )
            add(f"| `{step.step_id}` | `{step.rendered()}` | {how} | {shown} |")
    add("")
    blocked = [item for item in plan.unresolved if item.blocks_mutation_ids]
    if blocked:
        add(
            "**Blocked baselines — R14.** These objects are proved absent by "
            "nothing, so the executor refuses the step that would create the "
            "first of them and their reversals can never become applicable. The "
            "harness leaves them to the operator recovery in §2.13.2b rather "
            "than removing what it could not prove it made."
        )
        add("")
        add("| Blocked baseline | Conflict | Mutations left unowned |")
        add("|---|---|---|")
        for item in blocked:
            add(
                f"| `{item.step_ref}` | {item.conflict_id} | "
                f"{len(item.blocks_mutation_ids)} |"
            )
        add("")
    add(
        "The two `postgres_config_line` mutations appear in no row, and that is "
        "the contract rather than a gap: their reversal is a **restore** of a "
        "byte-exact pre-change capture, not a removal, and the executor already "
        "refuses to write the configuration at all unless that capture step was "
        "satisfied."
    )
    add("")

    add(
        "## 5d. Externally produced evidence — the input contract, and the "
        "producers that do not exist (R16, C-7 and EH-R16-4)"
    )
    add("")
    add(
        "Band 7's cases observe nothing this plan does. Each is a comparison "
        "over what happened when `init-generation` ran with its provenance "
        "record removed, when a probe stage was made to fail, or when cleanup "
        "did not complete — situations an operator arranges on the disposable "
        "host and that no argument vector here produces."
    )
    add("")
    add(
        "**None of them is resolved.** R16's first submission declared these as "
        "externally supplied cases on the strength of a description of the "
        "coordinator tooling that would produce them; the review returned that "
        "as EH-R16-4, because *naming `init-generation` and a future table does "
        "not resolve the evidence dependency*. The three cases are therefore "
        "declared **unresolved** under conflict C-7 in section 6, and "
        "`executable` is `False` while they are."
    )
    add("")
    add(
        "What the table below is, then, is the **input contract**: the shape a "
        "reviewed observation would have to have, and who would have to make "
        "it. Observations enter through `observations.py` — a separate "
        "non-executing importer with a strict, versioned, bounded schema and no "
        "free-text field, reached by `execution/evidence_cli.py`, which imports "
        "no boundary, no executor and no materializer. A supplied record can "
        "select no command, no executable, no identity, no path, no approval "
        "token and no expected value, and it cannot close a case the plan "
        "declares unresolved. The `resolves` column is what says so: a contract "
        "resolves a required case only when a reviewed producer artifact exists, "
        "and none does."
    )
    add("")
    if not plan.external_cases:
        add("None.")
    else:
        add("| Case | Band | Variants required | Resolves the case? | Producer |")
        add("|---|---|---|---|---|")
        for item in plan.external_cases:
            add(
                f"| `{item.case_id}` | {item.band} | "
                f"{', '.join(item.variants)} | "
                + (
                    f"yes — {item.producer_review_reference}"
                    if item.resolves_coverage
                    else "**no** — no reviewed producer artifact exists"
                )
                + f" | {item.producer} |"
            )
    add("")

    add("## 6. Unresolved — what could not be generated, and why")
    add("")
    if not plan.unresolved:
        add(
            "**None.** **`is_executable` would then be a statement about the "
            "plan and not permission to run it**: the executor still refuses "
            "while any reviewed target fact is unsupplied, without the exact "
            "confirmation token, and without a reviewer-supplied digest for this "
            "exact tree."
        )
    else:
        add(
            f"**{len(plan.unresolved)} items across conflicts "
            f"{', '.join(plan.conflicts())}.** The executor refuses a plan that "
            "carries any of them, so none of this is a partial run waiting to "
            "happen."
        )
        add("")
        for item in plan.unresolved:
            add(f"### `{item.step_ref}` — {item.conflict_id} ({item.band})")
            add("")
            add(f"- **The design requires:** {item.design_requires}")
            add(f"- **Why it is not a vector:** {item.why_not_a_vector}")
            add(f"- **What would resolve it:** {item.what_would_resolve_it}")
            add(
                "- **Evidence cases affected:** "
                + (", ".join(item.evidence_case_ids) or "—")
            )
            add("")
    add("# NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED")
    add("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The command line
# ---------------------------------------------------------------------------


def _unconfirmed_target_facts() -> tuple[str, ...]:
    """Every reviewed target fact still unsupplied, named rather than counted.

    They are constant names this package declares, not values and not host
    facts, so printing them says which decision is outstanding without saying
    anything about `oracle-test`. Each one refuses `ExecutingRunner` at
    construction, before any command starts.
    """
    names: list[str] = []
    if not interpreter_digest_confirmed():
        names.append("interpreter_sha256")
    if not interpreter_real_path_confirmed():
        names.append("interpreter_real_path")
    names.extend(f"E7.{fact}" for fact in unconfirmed_e7_facts())
    return tuple(names)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase-5-0-evidence",
        description=(
            "Package 5.0 evidence harness. A default invocation is a dry run: it "
            "prints the plan and executes nothing."
        ),
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Actually run the reviewed plan. Requires --confirm-target and "
            "--reviewed-digest. Without it nothing is executed."
        ),
    )
    parser.add_argument(
        "--confirm-target",
        default="",
        help="The exact confirmation token derived from the approved target's identity.",
    )
    parser.add_argument(
        "--reviewed-digest",
        default="",
        help=(
            "The review-manifest digest Codex approved. Supplied by the reviewer; "
            "never read from this tree."
        ),
    )
    parser.add_argument(
        "--manifest",
        action="store_true",
        help="Print the review manifest JSON to standard output and exit.",
    )
    parser.add_argument(
        "--manifest-out",
        default="",
        help="Write the review manifest JSON to this path.",
    )
    parser.add_argument(
        "--render",
        default="",
        help="Write the human-readable concrete plan Markdown to this path.",
    )
    # **r6 §5, PR-20260913-LABI-3.** The four values the reservation protocol
    # needs from the operator. They are arguments rather than derived values
    # because each is a *claim* the stored record checks: the run id binds this
    # run's ledger entry and its recovery directory, the reservation binds the
    # start the completion must name, and the author and time are attribution.
    parser.add_argument(
        "--run-id",
        default="",
        help=(
            "This run's identifier. It becomes a ledger filename, a recovery "
            "directory name and a role in a refusal, so it is bounded before "
            "any of the three — letters, digits, dot, dash and underscore, at "
            "most 64 characters."
        ),
    )
    parser.add_argument(
        "--reservation",
        default="",
        help=(
            "The reservation this run belongs to. It is written into the run's "
            "durable `participant_started` entry before the first effect, and "
            "the completion's evidence must name exactly that reservation — "
            "equality, both ways."
        ),
    )
    parser.add_argument(
        "--author",
        default="",
        help="Who is running this. Recorded in the ledger, never inferred.",
    )
    parser.add_argument(
        "--at",
        default="",
        help="The run's timestamp, in the record schema's own format.",
    )
    # **r6 §5.12, PR-20260914-LABI-R1-1.** The reservation the terminal
    # publication concludes. `ReservationRequest` refuses a blank owner,
    # deadline or recovery owner, so there is no default reservation and no
    # reservation nobody is accountable for.
    parser.add_argument(
        "--reservation-owner",
        default="",
        help="Who holds the reservation. There is no default owner.",
    )
    parser.add_argument(
        "--requested-at",
        default="",
        help="When the reservation was requested, in the record schema's format.",
    )
    parser.add_argument(
        "--deadline",
        default="",
        help=(
            "The reservation deadline. Reaching it moves the run to RECOVERING "
            "and authorizes nobody to take the host."
        ),
    )
    parser.add_argument(
        "--recovery-owner",
        default="",
        help="Who recovers this reservation if it is interrupted or quarantined.",
    )
    # **r6 §1.6.** The three external observations no process in this package
    # can make. Each is a tri-state on purpose: unsupplied is *not observed*,
    # which quarantines, and is never the same as an observed false.
    parser.add_argument(
        "--observed-by",
        default="",
        help=(
            "Who made the external observations below, and who is named as "
            "having searched for residue. An observation with no author is an "
            "assertion with no author."
        ),
    )
    for option, condition in (
        ("--processes-ended", "every process the run started has exited"),
        (
            "--transactions-settled",
            "every server-side transaction the run opened has settled",
        ),
        (
            "--transient-units-inactive",
            "no transient unit the run created is still active",
        ),
    ):
        parser.add_argument(
            option,
            choices=("true", "false"),
            default=None,
            help=(
                f"Whether {condition}, as observed rather than inferred. "
                "Omitting it is *not observed*, which gates every B3-dependent "
                "effect and quarantines the reservation at release."
            ),
        )
    parser.add_argument(
        "--run-record-out",
        default="",
        help=(
            "Where to write the run record after an --execute. It is written "
            "only when the run is admissible, it is read back and validated "
            "before the path is reported, and without this option nothing is "
            "written and nothing is claimed. It is the **run record** — what "
            "ran and what was observed — and not the classified evidence "
            "artifact. That is written by a different program — "
            "`execution.evidence_cli`, which imports no boundary, no executor "
            "and no materializer — from observations supplied for the cases "
            "Band 7 produces outside this plan."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    plan = build_concrete_plan()
    sources = read_covered_sources()
    manifest = ReviewManifest.build(plan, sources)
    digest = manifest.digest()

    if args.manifest:
        sys.stdout.write(manifest.serialize().decode("utf-8"))
        return 0
    if args.manifest_out:
        Path(args.manifest_out).write_bytes(manifest.serialize())
    if args.render:
        Path(args.render).write_text(
            render_plan(plan, digest, manifest.digest_for(CASE_PROGRAM_SOURCE)),
            encoding="utf-8",
        )

    if not args.execute:
        boundary = RecordingBoundary()
        for step in plan.steps:
            boundary.calls.append((step.run_as, tuple(step.argv)))
        materializer = RecordingMaterializer()
        for item in plan.materializations:
            materializer.requests.append(
                (item.step_id, item.destination, item.file.sha256)
            )
        sys.stdout.write(
            f"DRY RUN — nothing was executed.\n"
            f"  target                : {plan.target.identity}\n"
            f"  steps planned         : {len(plan.steps)}\n"
            f"  materializations      : {len(materializer.requests)} "
            f"(written by nothing; this boundary is not armed)\n"
            f"  binding sites declared: "
            f"{sum(len(step.bindings) for step in plan.steps)} "
            f"(resolved by nothing; no account database was read)\n"
            f"  expectation contracts : "
            f"{sum(1 for step in plan.steps if step.capture is not CapturePolicy.EXIT_STATUS_ONLY)} "
            f"(compared by nothing; no observation was made)\n"
            f"  ownership baselines   : "
            f"{sum(1 for step in plan.steps if step.establishes_ownership_of)} "
            f"steps covering "
            f"{len({m for step in plan.steps for m in step.establishes_ownership_of})} "
            f"of {len(plan.mutations)} declared mutations "
            "(the two configuration lines are restored, not removed)\n"
            f"  blocked baselines     : "
            f"{len({m for item in plan.unresolved for m in item.blocks_mutation_ids})} "
            "mutations proved absent by nothing, so nothing may create or "
            "remove them (R14, EH-R14-1)\n"
            f"  creation ownership    : "
            f"{sum(1 for step in plan.steps if step.establishes_ownership_by_creation)} "
            f"step(s) owning "
            f"{len({m for step in plan.steps for m in (*step.establishes_ownership_by_creation, *step.establishes_ownership_of_contained)})} "
            "mutations by exclusive creation rather than by a probe "
            "(R16, C-8)\n"
            f"  external contracts    : {len(plan.external_cases)} "
            "documented input contract(s) for observations produced outside "
            "this plan, of which "
            f"{sum(1 for item in plan.external_cases if item.resolves_coverage)} "
            "have a reviewed producer artifact and therefore resolve a required "
            "case. A contract without one documents an input shape and closes "
            "nothing (R16, EH-R16-4)\n"
            f"  mutations declared    : {len(plan.mutations)}\n"
            f"  cleanup steps derived : {len(plan.cleanup_plan.steps)}\n"
            f"  unresolved conflicts  : {len(plan.unresolved)} "
            f"({', '.join(plan.conflicts()) or 'none'})\n"
            f"  unconfirmed facts     : "
            f"{', '.join(_unconfirmed_target_facts()) or 'none'} "
            f"(each one refuses the executor before any command starts)\n"
            f"  review manifest digest: {digest}\n"
            f"  executable            : {plan.is_executable}\n"
        )
        return 0

    # **r6 §5, PR-20260913-LABI-3 and PR-20260914-LABI-R1-1.** The harness is one
    # of seven participants, and this is where it joins the protocol. It does not
    # merely construct the integration point beside the executor — the re-review
    # found that constructing the objects without calling their protocol enforces
    # nothing. `ParticipantIntegration.run_harness` **owns** the call: it takes
    # the cooperative lock, re-seals, reads, validates, surveys, admits,
    # publishes the durable `participant_started`, issues the permit the armed
    # executor requires, runs the work below, derives the release evidence from
    # what that work observed, publishes §5.12's two terminal entries and only
    # then releases the lock.
    #
    # **Every operational gate above stays closed.** `plan.is_executable` is
    # False and the twelve target facts are unconfirmed, so
    # `ExecutingRunner.__post_init__` refuses this construction today — before
    # the lock is taken and before anything durable is written, which is why a
    # standing refusal publishes no run entry. `reservation.REAL_EXECUTION_REFUSAL`
    # stands independently at admission. The wiring below is wiring, not
    # permission.
    integration = ParticipantIntegration(
        participant=Participant.HARNESS_CLI,
        host=plan.target.host,
        target_identity=plan.target.identity,
        author=args.author,
        at=args.at,
        reservation_id=args.reservation,
        # The harness takes the lock **for the reservation** and refuses rather
        # than waiting behind another participant: waiting would hold a
        # reservation open behind a suite.
        wait_for_lock=False,
    )
    inventory = DescriptorInventory()
    filesystem = PosixFilesystem(inventory)
    recovery = RecoveryStore(inventory=inventory, filesystem=filesystem)
    try:
        run_id = validate_run_identifier(args.run_id)
        # **r6 §1.6.** One observation, read once. It gates every B3-dependent
        # effect *and* supplies two of the release's conditions; a second copy
        # supplied separately to the release would be the two-readers drift.
        quiescence = _quiescence(args)
        request = ReservationRequest(
            reservation_id=args.reservation,
            owner=args.reservation_owner,
            host=plan.target.host,
            target_identity=plan.target.identity,
            requested_at=args.requested_at,
            deadline=args.deadline,
            recovery_owner=args.recovery_owner,
            real_execution=True,
        )
        runner = ExecutingRunner(
            plan=plan,
            # The one place a boundary that can start a process is constructed,
            # and it is armed on the same line, inside the --execute branch.
            boundary=SubprocessBoundary(armed=True),
            # The one place a materializer that can write a file is constructed,
            # and it is armed on the same line, in the same branch.
            materializer=SystemMaterializer(armed=True),
            # The one place an effect issuer that can `mkdirat`, `ioctl` and
            # `unlinkat` is constructed, armed on the same line, in the same
            # branch. It replaced `/usr/bin/install` and `/usr/bin/chattr`.
            effects=DescriptorBoundEffects(
                inventory=inventory,
                filesystem=filesystem,
                recovery=recovery,
                armed=True,
                quiescence=quiescence,
            ),
            session=integration,
            run_id=run_id,
            reservation_id=args.reservation,
            reviewed_digest=args.reviewed_digest,
            confirmation_token=args.confirm_target,
            source_bytes=sources,
        )
    except (ExecutorRefused, HarnessError, ParticipantRefused, PlanRefused) as exc:
        inventory.close()
        sys.stderr.write(f"REFUSED — nothing was executed.\n{exc}\n")
        return REFUSED_EXIT_CODE

    try:
        harness = execute_under_reservation(
            integration=integration,
            runner=runner,
            request=request,
            run_id=run_id,
            quiescence=quiescence,
            observed_by=args.observed_by,
            searched_at=args.at,
        )
    except ParticipantRefused as exc:
        inventory.close()
        sys.stderr.write(f"REFUSED — the reservation protocol refused.\n{exc}\n")
        return REFUSED_EXIT_CODE
    finally:
        inventory.close()

    outcome = runner.last_outcome
    if outcome is None:
        # The work never returned an outcome, so the run is unsettled and the
        # ledger says so. Nothing is claimed about what it left behind.
        sys.stderr.write(
            "REFUSED — the harness did not reach its executor.\n"
            f"  refusal          : {harness.run.refusal or '—'}\n"
            f"  reasons          : {', '.join(harness.run.reasons) or '—'}\n"
            f"  durable start    : {harness.run.started}\n"
            f"  unsettled        : {harness.run.unsettled}\n"
        )
        return REFUSED_EXIT_CODE
    # **R13, EH-R13-5.** Eligibility and persistence are two lines, because they
    # are two facts. The previous version printed the first under the second's
    # label and wrote no file at all, so a successful run reported an artifact
    # that did not exist and kept neither its observations nor its band records.
    written = _write_run_record(outcome, args.run_record_out, runner)
    sys.stdout.write(
        f"state {outcome.cleanup.state}, exit {outcome.exit_code}\n"
        f"  steps run        : {len(outcome.steps)}\n"
        f"  stopped at       : {outcome.stopped_at or '—'}\n"
        f"  stop reason      : {outcome.stop_reason or '—'}\n"
        f"  residue          : {', '.join(outcome.cleanup.residue) or 'none'}\n"
        f"  configuration    : "
        f"{', '.join(outcome.cleanup.configuration_risk) or 'no unresolved risk'}\n"
        f"  preserved        : "
        f"{', '.join(outcome.cleanup.preserved) or 'none'}\n"
        f"  retained inputs  : "
        f"{', '.join(outcome.cleanup.retained_recovery_inputs) or 'none'}\n"
        f"  cleanup skipped  : {len(outcome.cleanup_skipped)}\n"
        f"  artifact eligible: {outcome.artifact_admissible}\n"
        f"  run record       : {written}\n"
        # **§5.12.** The reservation's own conclusion, reported beside the run's.
        # `released` is both halves or neither: between steps 2 and 3 the record
        # says released and the run is still in progress, and an unsettled run
        # refuses every successor including the environment reset.
        f"  reservation      : "
        f"{harness.terminal.decision.value if harness.terminal is not None else '—'}\n"
        f"  release durable  : {harness.released}\n"
        f"  run completed    : {harness.run.completed}\n"
        f"  run unsettled    : {harness.run.unsettled}\n"
    )
    return outcome.exit_code


def _quiescence(args) -> Quiescence:
    """r6 §1.6's three observations, exactly as the operator stated them.

    `None` stays `None`. An option nobody passed is an observation nobody made,
    and `Quiescence.missing()` reports it as such — it never becomes `False`,
    because *"not checked"* and *"checked and false"* are different things to
    tell an operator, and it never becomes `True`.
    """
    def stated(value: str | None) -> bool | None:
        return None if value is None else value == "true"

    return Quiescence(
        observed=any(
            value is not None
            for value in (
                args.processes_ended,
                args.transactions_settled,
                args.transient_units_inactive,
            )
        ),
        processes_ended=stated(args.processes_ended),
        transactions_settled=stated(args.transactions_settled),
        transient_units_inactive=stated(args.transient_units_inactive),
        observed_by=args.observed_by,
    )


class HarnessRunner(Protocol):
    """What the orchestration path needs of the thing it drives — three methods.

    A small protocol owned by its consumer, so the one function that sequences
    the harness states what it requires instead of naming a concrete class it
    happens to be handed. `ExecutingRunner` satisfies it; so does the recording
    double the composition test observes the ordering with, which is the point:
    the ordering is a property of this function, not of the executor.
    """

    def accept_permit(self, permit: EffectPermit) -> None: ...

    def execute(self): ...

    def run_observations(
        self, outcome, *, observed_by: str, searched_at: str
    ) -> HarnessObservations: ...


def execute_under_reservation(
    *,
    integration: ParticipantIntegration,
    runner: HarnessRunner,
    request: ReservationRequest,
    run_id: str,
    quiescence: Quiescence,
    observed_by: str,
    searched_at: str,
) -> HarnessRun:
    """The executable harness call, as one orchestration path — §5.6 and §5.12.

    **PR-20260914-LABI-R1-1.** It is a function rather than four statements
    inside `main` so that the composition can be driven, and observed, by a test
    over a laboratory under `tmp_path`: the ordering this enforces is a property
    of the call graph, and a test that asserted the construction of the objects
    would be asserting the very thing the re-review found insufficient.

    Everything below the `work` closure happens **inside** the lock, after the
    admission and after the durable start. The closure is handed the permit, it
    hands it to the executor — which refuses unless it is genuinely issued and
    bound to this run and this reservation — and it returns what the run
    established. It returns nothing about its own completion: r6 §5.12 derives
    the harness's two conditions from the release decision and the release
    publication, and an injected one is refused at the writer.
    """

    def work(permit: EffectPermit) -> HarnessObservations:
        runner.accept_permit(permit)
        outcome = runner.execute()
        return runner.run_observations(
            outcome, observed_by=observed_by, searched_at=searched_at
        ).with_quiescence(quiescence)

    return integration.run_harness(
        run_id=run_id, work=work, request=request, observed_by=observed_by
    )


def _write_run_record(outcome, destination: str, runner) -> str:
    """The run record's path, or the fixed reason there is none.

    It never returns a path it did not write: `write_run_record` serializes,
    writes, **reads the bytes back** and validates them against the run before
    returning, and every failure comes back here as a refusal rather than as a
    path.
    """
    if not outcome.artifact_admissible:
        return NOT_ADMISSIBLE
    if not destination:
        return NO_DESTINATION
    try:
        path = write_run_record(
            outcome,
            Path(destination),
            target_identity=runner.plan.target.identity,
            manifest_digest=runner.manifest_digest,
        )
    except RunRecordRefused as refusal:
        return f"no — {refusal}"
    return str(path)


if __name__ == "__main__":  # pragma: no cover - the entry point itself
    raise SystemExit(main())
