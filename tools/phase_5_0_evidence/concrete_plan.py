"""The concrete argument vectors, generated against the approved target.

This module replaces the execution plan's `<TARGET_ROOT>`/`<EVIDENCE_DB>`
template with real paths and real names. It is a **generator**, not a
transcription: every vector below is built from `approved_target.APPROVED_TARGET`
and from the constants in this file, so a target change is one edit and a vector
that disagrees with the target cannot be written.

## Four kinds of thing come out of it

1. **`CommandStep`s** — a complete `execve` argument vector, an identity, a
   purpose, the evidence cases it observes and the mutations it performs. Every
   one of them passes `plan.validate_argv`, so none contains a placeholder, a
   glob, a shell metacharacter, an unresolved variable, a relative path or an
   executable outside `plan.PERMITTED_EXECUTABLES`.
2. **`Mutation`s** — every object the run would create, in provisioning order.
   `cleanup.CleanupPlan.for_mutations()` derives the whole cleanup from this
   list; nobody writes a cleanup command.
3. **`MaterializeStep`s** — the two reviewed configuration files, each with its
   pinned bytes, digest, owner, group and mode, the capture step whose success it
   requires and the command step it runs after. This is conflict **C-4**'s
   bounded resolution: it is not a write-file interface, because there is no way
   to express a destination or a byte sequence the closed table in
   `materialization.py` does not already contain.
4. **`UnresolvedStep`s** — the parts of the reviewed design that **cannot be
   expressed at all with the reviewed mechanisms**, each with the conflict it
   raises. R11's Option-B ruling resolved the last vector-shaped one; what
   remains are missing **producers** — Band 7's three cases under **C-7** (R16)
   and S4-3 under **C-S4-3** (C-P5.0-R5-R2). The section below describes the
   state after R11 and is kept as that history.

## Why the fourth kind exists, and why it is now empty

The reviewed design describes steps that are not commands. Stage 1 and Stage 2 of
the §2.13.2a probe are `open(2)`, `rename(2)`, `unlink(2)` and
`FS_IOC_GETFLAGS` — syscalls with specific flags, made by a program. §2.13.5c's
`E1 … E6` and `E8` are `capsh` invocations that exec that same program, and
whose `--uid=`/`--gid=` are **numeric** for accounts Band 2 has not yet created;
`E7` is the harness's own root process and execs it directly.
§2.13.3's `…/journal/current` is a symbolic link, which nothing permitted
creates.

R10 returned all three as one question — *what program is `…/bin/case`, and what
runtime executes it?* — because that is a decision about the trusted computing
base rather than something to settle by writing a file. **Peter Duscha ruled it
on 2026-09-06** (package plan §2.12.2, change-log **C-P5.0-AH**): Option B, an
explicitly named interpreter in every case-program vector. `case_runtime` is that
ruling, `execution/case_program.py` is the reviewed program, and `binding` is the
late-binding rule the `capsh` construction needed once it had a consumer.

So this generator now emits **no `UnresolvedStep`**. The class and
`ConcretePlan.is_executable` remain, because the next thing the reviewed design
grows that cannot be a vector should be visible in the plan rather than absent
from it — and because `is_executable` being True is a statement about the plan,
not permission to run it. The executor holds five separate gates that say so, one
of which refuses while the interpreter's expected digest is an unsupplied
reviewed target fact.

## What is not here

No production path, no production database, no credential, no address beyond the
loopback the TCP-refusal case must name, and no rule text. The two PostgreSQL
configuration files are the only paths the harness *writes* outside the
disposable root, and they are reached through `DisposableTarget.config_path()`,
which knows two filenames. Three paths outside the root are *read* or *executed*
and never written: `/dev/null` as `install`'s source for an empty file, the
reviewed case-program source `install` copies, and the approved interpreter,
which is an executable rather than an object and is admitted only by
`case_runtime.validate_case_vector`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .approved_target import APPROVED_TARGET, APPROVED_TARGET_FACTS
from .binding import BindingKind, BindingSite
from .capability import ALL_CAPABILITY_NAMES, EVIDENCE_IDENTITIES
from .capture import CapturePolicy, CatalogQuestion
from .case_runtime import (
    CASE_PROGRAM_GROUP,
    CASE_PROGRAM_MODE,
    CASE_PROGRAM_OWNER,
    CASE_PROGRAM_SOURCE,
    CASE_PROGRAM_SOURCE_PATH,
    GENERATION_LINK_NAME,
    INTERPRETER_FLAGS,
    INTERPRETER_PATH,
    INTERPRETER_PYTHON_VERSION,
    BOOTSTRAP_VERBS,
    OBSERVATION_VERBS,
    REFUSAL_EXIT_CODES,
    ROOT_NOTHING_CREATED_STATUSES,
    ROOT_PREEXISTING_STATUS,
    build_bootstrap_vector,
    build_case_vector,
    case_program_path,
    refused_with,
)
from .cleanup import CleanupPlan
from .errors import PlanRefused
from .expectations import EMPTY_SET, Comparison, DeclaredExpectation
from .identity import CANONICAL_ACCOUNTS, CANONICAL_GROUPS
from .materialization import reviewed_configuration
from .observations import BAND_7_SCHEMA
from .required_cases import check_case_coverage
from .plan import (
    CONFIGURATION_ROLE,
    ROOT_IDENTITY_NAME,
    ROOT_ROLE,
    CommandStep,
    DescriptorEffect,
    EffectKind,
    ExecutionPlan,
    MaterializeStep,
    Mutation,
    MutationKind,
    StepRole,
)
from .targets import POSTGRES_CONFIG_FILES, DisposableTarget
from .unit_sandbox import CANONICAL_PROBE_PATH, COMPARED_PROPERTIES

# ---------------------------------------------------------------------------
# The names the run creates. Every one is checked by
# `targets.validate_account_name`, which refuses root, postgres, discordbot,
# freedomweb, foundry and sudo, so none of them can name an existing identity.
# ---------------------------------------------------------------------------

JOURNAL_GROUP = "freedomjournal"
COORD = "freedomcoord"
WRITER = "freedomsheet"
PROBE = "fbprobe"

#: The groups, in provisioning order. §2.12.7: groups, then accounts, then
#: membership.
CREATED_GROUPS = (JOURNAL_GROUP, COORD, WRITER, PROBE)
#: The accounts, each with its primary group.
CREATED_ACCOUNTS = ((COORD, COORD), (WRITER, WRITER), (PROBE, PROBE))
#: §2.12.2's membership matrix, exactly: two members of `freedomjournal` and no
#: third. `identity.classify_group_membership` compares as a set, so an
#: unexpected member is a failed case rather than a noted difference (P5.0-SR2).
CREATED_MEMBERSHIPS = ((COORD, JOURNAL_GROUP), (WRITER, JOURNAL_GROUP))

#: The identities the `JNL-52` assertions read back. The last three are existing
#: host identities the run never creates and never modifies; they are read so
#: that §2.12.2's *complete* supplementary list can be compared, which is what
#: makes "no unexpected member" a checkable claim rather than a hope.
ASSERTED_GROUPS = (JOURNAL_GROUP, COORD, WRITER, PROBE, "discordbot", "sudo")
ASSERTED_ACCOUNTS = (COORD, WRITER, PROBE, "discordbot", "freedomweb", "foundry")

#: §2.12.3's role, created in the disposable instance only.
COORDINATOR_ROLE = "freedom_migration_coordinator"

#: The one temporary authentication mapping Band 6 declares. Both halves are
#: required on the configuration mutation (EH-R3-2) because cleanup's post-reload
#: proof runs **as** the identity and asks for the role.
MAPPED_OS_USER = COORD
MAPPED_POSTGRES_ROLE = COORDINATOR_ROLE

#: The Stage-4 transient unit, named so `systemctl show` can be asked about
#: exactly the thing that ran.
#:
#: **One name, used twice.** `S4-1` starts it with `--collect`, so the unit is
#: removed the moment it exits and the name is free; `S4-2` starts it without,
#: so the failed unit stays loaded and `S4-3` can read the directive set that was
#: actually applied to it. One declared mutation, one `systemctl stop` reversal,
#: and the unit §2.13.2a names.
TRANSIENT_UNIT = "fb-evidence-s4.service"

#: The reviewed configuration capture set, in the order the plan lists it. It is
#: `targets.POSTGRES_CONFIG_FILES`, named here so the capture effect, the
#: restoration effect and the recovery store's bound set are one list rather
#: than three.
CAPTURED_CONFIGURATION: tuple[str, ...] = tuple(sorted(POSTGRES_CONFIG_FILES))

#: Which memberships a group's absence establishes ownership of. A group that
#: does not exist has no members, so the `getent` that proves `freedomjournal`
#: absent proves that every `gpasswd --delete` reversing a membership into it is
#: reversing a membership this run added — R13, EH-R13-1.
_MEMBERSHIPS_INTO: dict[str, tuple[str, ...]] = {}
for _account, _group in CREATED_MEMBERSHIPS:
    _MEMBERSHIPS_INTO.setdefault(_group, ())
    _MEMBERSHIPS_INTO[_group] += (f"group_membership:{_account}",)

#: The `ProtectSystem=` directive every Stage-4 unit is started with, and the
#: value `S4-3` reads back from `systemctl show`. Named once so the vector that
#: sets it and the expectation that compares it are one string — R13.
STAGE_4_PROTECT_SYSTEM = "strict"

#: The loopback address the TCP-refusal case must name. It is a connection
#: parameter, not a recorded observation: nothing derived from it reaches an
#: evidence record.
LOOPBACK = "127.0.0.1"


# ---------------------------------------------------------------------------
# Unresolved steps
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class UnresolvedStep:
    """A reviewed design step that cannot be an argument vector.

    Deliberately **not** a `CommandStep`. It has no `argv`, so it cannot be
    executed, cannot be validated as a vector and cannot be mistaken for one in
    a rendered plan. It carries what the design requires, why a vector cannot
    express it, and what would resolve it — because a blocker with no stated
    resolution is a complaint.
    """

    step_ref: str
    band: str
    conflict_id: str
    design_requires: str
    why_not_a_vector: str
    what_would_resolve_it: str
    evidence_case_ids: tuple[str, ...] = ()
    #: **R14, EH-R14-1.** The declared mutations this blocker leaves **unowned**.
    #: A blocked ownership baseline is not merely a missing observation: it is a
    #: set of objects the executor may not create, because nothing proved them
    #: absent, and whose reversals can therefore never become applicable. Stating
    #: the set here makes that machine-checkable — `test_r14_remediation.py`
    #: asserts every reversal's subjects are owned or blocked and never both —
    #: rather than a claim in prose.
    blocks_mutation_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "step_ref",
            "band",
            "conflict_id",
            "design_requires",
            "why_not_a_vector",
            "what_would_resolve_it",
        ):
            if not getattr(self, name).strip():
                raise PlanRefused(f"An unresolved step needs a {name}.")
        if not isinstance(self.blocks_mutation_ids, tuple):
            raise PlanRefused(
                f"Unresolved step {self.step_ref!r} declares the mutations it "
                "blocks as a tuple, so the plan is immutable."
            )


@dataclass(frozen=True, slots=True)
class ExternalCase:
    """A required evidence case whose producer is **not a step of this plan**.

    **R16, conflict C-7.** R14 declared Band 7's three cases `UnresolvedStep`s,
    which was right about the state of the harness and wrong about the shape of
    the problem: their observations are not vectors this plan failed to express,
    they are observations of the coordinator tooling §2.12.5a and §2.13.5a
    describe — a run of `init-generation` with its provenance record removed, a
    probe with a failure injected at one stage, a cleanup that did not complete.
    No argument vector this harness could write would produce one.

    So they are declared as what they are: cases with a **named external
    producer** and a **named collection procedure**, whose observations enter
    through `observations.py`'s importer, are validated against a closed schema,
    and are classified by the band's own classifiers. `is_executable` does not
    depend on them, because they are not something the run does.

    What that emphatically does not mean is that a record can stand in for an
    experiment. `observations.classify_supplied_observations` refuses to call a
    case covered while the plan still declares it unresolved, and
    `EvidenceResult.complete` is false while any required case or variant has no
    record — so *"the plan ran"* and *"the evidence is complete"* stay two
    different statements, which is the whole of EH-R13-4.
    """

    case_id: str
    band: str
    #: The actor and situation that makes the observation.
    producer: str
    #: How the observation is collected, step by step.
    collection_procedure: str
    #: The variants the importer requires before the case is covered.
    variants: tuple[str, ...]
    #: Why this is not an argument vector.
    why_not_a_step: str
    #: **R16, EH-R16-4.** Whether a **reviewed producer artifact** and a runnable
    #: collection procedure actually exist for this case today.
    #:
    #: R16's finding was that describing future coordinator tooling and calling
    #: the result an external case *"reclassified missing producers as
    #: resolved"*: naming `init-generation` and a table Package 5.0 has not built
    #: is not a producer, and changing the coverage category does not discharge
    #: an evidence dependency. So the field defaults to `False` and every entry
    #: in this plan carries the default: the contract below is **documentation of
    #: the input shape**, and the dependency it describes stays open.
    producer_artifact_reviewed: bool = False
    #: The review that would have to accept the producer artifact before this
    #: case may be counted as externally supplied. Non-empty only when the
    #: producer exists.
    producer_review_reference: str = ""

    @property
    def resolves_coverage(self) -> bool:
        """Whether this contract may occupy `check_case_coverage`'s third column.

        **EH-R16-4.** A documented contract is not a producer. Only a case whose
        producer artifact exists and has been reviewed leaves the unresolved
        column, and nothing in this plan does.
        """
        return self.producer_artifact_reviewed and bool(
            self.producer_review_reference.strip()
        )

    def __post_init__(self) -> None:
        for name in (
            "case_id",
            "band",
            "producer",
            "collection_procedure",
            "why_not_a_step",
        ):
            if not getattr(self, name).strip():
                raise PlanRefused(f"An external case needs a {name}.")
        if self.producer_artifact_reviewed and not self.producer_review_reference.strip():
            raise PlanRefused(
                f"External case {self.case_id!r} claims a reviewed producer "
                "artifact and names no review. A producer nobody reviewed is a "
                "description, which is the substitution EH-R16-4 refuses."
            )
        if self.producer_review_reference.strip() and not self.producer_artifact_reviewed:
            raise PlanRefused(
                f"External case {self.case_id!r} names a producer review and "
                "does not claim the artifact exists."
            )
        if not isinstance(self.variants, tuple) or not self.variants:
            raise PlanRefused(
                f"External case {self.case_id!r} names the variants an importer "
                "requires before it is covered. A case with none could be "
                "covered by nothing."
            )


# ---------------------------------------------------------------------------
# S4-3's producer dependency — C-P5.0-R5-R2, finding P5.0-R5-R1-PLAN-1
# ---------------------------------------------------------------------------

#: The stable identifier of S4-3's producer dependency. **Not C-7**: C-7 is Band
#: 7's three coordinator-tooling producers and may be resolved without touching
#: Stage 4, and this dependency may be resolved without touching Band 7. A
#: separate identifier is what lets `conflicts()` show one open while the other
#: closes.
S4_3_CONFLICT = "C-S4-3"


#: **C-P5.0-R5-R3, finding P5.0-R5-R2-PLAN-1.** The two S4-3 requirements only a
#: concrete, reviewed artifact can discharge, and which **nothing in this
#: repository discharges**. R2 represented them as `SandboxAttestationProducer`,
#: two nonblank review-reference strings, so `SandboxAttestationProducer("x",
#: "y")` cleared both — a description of future work standing in for the work,
#: which is the substitution EH-R16-4 refuses. That class is removed and nothing
#: replaces it: a review reference is provenance metadata, not the reviewed unit,
#: not the reviewed `SystemdIdentity` producer and not the binding between them.
#:
#: So there is no value, flag, path, digest or label a caller can supply to meet
#: these two requirements. Meeting them needs code and artifacts that do not
#: exist yet — the reviewed deployed unit and drop-in policy, and a reviewed
#: `SystemdIdentity` producer integrated into the S4-3 attestation — added by a
#: separately authorized pass and independently reviewed. That pass changes this
#: module; it cannot be done from outside it.
S4_3_UNMET_PRODUCER_REQUIREMENTS: tuple[str, ...] = (
    "no reviewed deployed `freedom-sheet-writer.service` and allowed drop-in "
    "policy exists in this repository (P5.0-R5 reconciliation row 16)",
    "no reviewed producer and binding for `unit_sandbox.SystemdIdentity` exists "
    "in this repository",
)


def s4_3_dependency_gaps(
    *,
    requested_properties: Sequence[str],
    substituted_path: str,
) -> tuple[str, ...]:
    """Every S4-3 requirement not met, in a fixed order. **Never empty.**

    `requested_properties` is what the plan's capture vector asks `systemctl
    show` for, and `substituted_path` is the `ReadWritePaths=` the plan's own
    transient-unit vector applies. Both come from the plan, so no caller can
    satisfy them by assertion. The two producer requirements are always
    reported unmet (`S4_3_UNMET_PRODUCER_REQUIREMENTS`): this function takes no
    argument that could say otherwise.

    The result is the **detail** C-S4-3 renders, not its gate. `_stage_four`
    declares C-S4-3 unconditionally, so an empty result — which only a
    monkeypatch can produce — does not clear it.
    """
    gaps: list[str] = [S4_3_UNMET_PRODUCER_REQUIREMENTS[0]]
    asked = tuple(requested_properties)
    missing = [name for name in COMPARED_PROPERTIES if name not in asked]
    duplicated = sorted({name for name in asked if asked.count(name) > 1})
    unrequested = sorted(set(asked) - set(COMPARED_PROPERTIES))
    if missing or duplicated or unrequested:
        detail = [f"requests {len(set(asked) & set(COMPARED_PROPERTIES))} of "
                  f"{len(COMPARED_PROPERTIES)} compared properties"]
        if missing:
            detail.append("omits " + ", ".join(missing))
        if duplicated:
            detail.append("repeats " + ", ".join(duplicated))
        if unrequested:
            detail.append("adds " + ", ".join(unrequested))
        gaps.append(
            "the capture vector does not request every property in "
            "`unit_sandbox.COMPARED_PROPERTIES` exactly once: it "
            + "; ".join(detail)
        )
    if substituted_path != CANONICAL_PROBE_PATH:
        gaps.append(
            f"the transient unit's `ReadWritePaths=` is {substituted_path!r}, "
            f"not the canonical probe path {CANONICAL_PROBE_PATH!r}"
        )
    gaps.append(S4_3_UNMET_PRODUCER_REQUIREMENTS[1])
    return tuple(gaps)


def _requested_properties(argv: Sequence[str]) -> tuple[str, ...]:
    """The `--property=` names a `systemctl show` vector asks for, in order."""
    return tuple(
        argument.split("=", 1)[1]
        for argument in argv
        if argument.startswith("--property=")
    )


# ---------------------------------------------------------------------------
# Paths, derived from the target and from nowhere else
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _Paths:
    """Every path the plan names, built once from the target's root."""

    root: str

    @property
    def journal(self) -> str:
        return f"{self.root}/journal"

    @property
    def archive(self) -> str:
        return f"{self.root}/archive"

    @property
    def before(self) -> str:
        return f"{self.root}/before"

    @property
    def bin(self) -> str:
        return f"{self.root}/bin"

    @property
    def probe(self) -> str:
        return f"{self.root}/probe"

    @property
    def probe_ro(self) -> str:
        return f"{self.root}/probe-ro"

    @property
    def case_binary(self) -> str:
        """The installed case program. `build_concrete_plan()` asserts this is
        `case_runtime.case_program_path(target)`, so the path the mutation list
        declares and the path the reviewed grammar admits are one string."""
        return f"{self.bin}/case"

    @property
    def stage1_moved(self) -> str:
        """Where Stage 1's `C-4` rename control moves the probe file, and moves
        it back from. Declared as a mutation, so a rename that succeeded and a
        rename-back that did not leaves a named object cleanup removes."""
        return f"{self.probe}/stage1.moved"

    @property
    def stage2_moved(self) -> str:
        """`P-4`'s rename destination. **Not** declared as a mutation: `P-4` is
        expected to be refused, so nothing is created — and if the append-only
        boundary failed to refuse it, the unexpected object makes `rmdir` on the
        arena fail and is reported as residue rather than deleted."""
        return f"{self.probe}/stage2.moved"

    @property
    def s4_1_target(self) -> str:
        """Stage 4's writable target, inside the substituted `ReadWritePaths=`."""
        return f"{self.probe}/s4-1.target"

    @property
    def s4_0_moved(self) -> str:
        """Where `S4-0`'s rename control moves its target, and moves it back."""
        return f"{self.probe_ro}/s4-0.moved"

    def denial_probe(self, directory: str, identity: str) -> str:
        """The path a negative `JNL-52` case tries to create and must not.

        Not a declared mutation, for `stage2_moved`'s reason: the case asserts
        the create is refused, so nothing is created, and an unexpected success
        is visible as residue rather than quietly cleaned up.
        """
        return f"{directory}/{identity}-deny.probe"

    @property
    def journal_file(self) -> str:
        return f"{self.journal}/000001.journal"

    @property
    def journal_seal(self) -> str:
        return f"{self.journal}/000001.seal"

    @property
    def journal_current(self) -> str:
        return f"{self.journal}/current"

    @property
    def archive_journal(self) -> str:
        return f"{self.archive}/000001.journal"

    @property
    def archive_seal(self) -> str:
        return f"{self.archive}/000001.seal"

    @property
    def archive_close(self) -> str:
        return f"{self.archive}/000001.close"

    @property
    def stage1(self) -> str:
        return f"{self.probe}/stage1.target"

    @property
    def stage2(self) -> str:
        return f"{self.probe}/stage2.target"

    @property
    def s4_unlink(self) -> str:
        return f"{self.probe_ro}/s4-0.unlink"

    @property
    def s4_target(self) -> str:
        return f"{self.probe_ro}/s4-2.target"

    def capture(self, filename: str) -> str:
        return f"{self.before}/{filename}"


# ---------------------------------------------------------------------------
# The mutation list, in provisioning order
# ---------------------------------------------------------------------------


def build_mutations(target: DisposableTarget) -> tuple[Mutation, ...]:
    """Every object the run would create, in the order §2.12.7 provisions them.

    The order is load-bearing twice over: it is the order the steps run in, and
    `CleanupPlan.for_mutations()` reverses it, so declaring a file before the
    attribute set on it is what makes cleanup clear the attribute first, and
    declaring a directory before its contents is what makes `rmdir` run last and
    on an empty directory.
    """
    paths = _Paths(target.root_path)
    mutations: list[Mutation] = []

    for group in CREATED_GROUPS:
        mutations.append(
            Mutation(
                MutationKind.OS_GROUP,
                group,
                "§2.12.2 provisions this group in the disposable environment; "
                "JNL-52 asserts its exact membership.",
            )
        )
    for account, _primary in CREATED_ACCOUNTS:
        mutations.append(
            Mutation(
                MutationKind.OS_ACCOUNT,
                account,
                "§2.12.2's identity, created disposable and evidence-only.",
            )
        )
    for account, group in CREATED_MEMBERSHIPS:
        mutations.append(
            Mutation(
                MutationKind.GROUP_MEMBERSHIP,
                account,
                "§2.12.2's membership matrix, and the revision-12 E8 correction.",
                group=group,
            )
        )

    for directory, why in (
        (paths.root, "the disposable facsimile of /var/lib/freedom-sheet-writer"),
        (paths.journal, "§2.13.3's journal directory, root:freedomjournal 0750"),
        (paths.archive, "§2.13.3's archive directory, root:freedomcoord 0750"),
        (paths.before, "the byte-exact pre-change captures cleanup restores from"),
        (paths.bin, "where the Band-5 case binary would live"),
        (paths.probe, "the §2.13.2a probe arena, root:freedomsheet 0770"),
        (paths.probe_ro, "Stage 4's negative target, outside the substituted ReadWritePaths="),
    ):
        mutations.append(Mutation(MutationKind.DIRECTORY, directory, why))

    for file_path, why in (
        (
            paths.case_binary,
            "the reviewed case program, installed byte-for-byte from "
            f"{CASE_PROGRAM_SOURCE} and executed through the Option-B "
            "interpreter vector (conflict C-2)",
        ),
        (paths.journal_file, "the disposable journal, freedomsheet:freedomcoord 0640"),
        (paths.journal_seal, "the disposable seal, root:freedomjournal 0440"),
        (
            paths.journal_current,
            "§2.13.3's current-generation symbolic link, created by the reviewed "
            "case program's symlink verb (conflict C-3)",
        ),
        (paths.archive_journal, "the disposable archive journal, root:freedomcoord 0440"),
        (paths.archive_seal, "the disposable archive seal, root:freedomcoord 0440"),
        (paths.archive_close, "the disposable .close manifest, root:freedomcoord 0440"),
        (paths.stage1, "the Stage-1 probe file, carrying no append attribute"),
        (
            paths.stage1_moved,
            "the name Stage 1's C-4 rename control moves the probe file to and "
            "moves it back from",
        ),
        (paths.stage2, "the Stage-2 probe file, the one FS_APPEND_FL is set on"),
        (paths.s4_1_target, "Stage 4's writable target, inside the substituted ReadWritePaths="),
        (paths.s4_unlink, "Stage 4's outside-the-unit control target"),
        (
            paths.s4_0_moved,
            "the name S4-0's rename control moves its target to and moves it "
            "back from",
        ),
        (paths.s4_target, "Stage 4's inside-the-unit denial target"),
        (paths.capture("pg_hba.conf"), "the byte-exact pre-change capture cleanup restores from"),
        (paths.capture("pg_ident.conf"), "the byte-exact pre-change capture cleanup restores from"),
    ):
        mutations.append(Mutation(MutationKind.FILE, file_path, why))

    for attributed, flag, why in (
        (paths.journal_file, "+a", "§2.13.3's append-only journal"),
        (paths.journal_seal, "+i", "§2.13.3's immutable seal"),
        (paths.archive_journal, "+i", "§2.13.3's immutable archive"),
        (paths.archive_seal, "+i", "§2.13.3's immutable archive"),
        (paths.archive_close, "+i", "§2.13.3's immutable archive"),
        (paths.stage2, "+a", "the FS_APPEND_FL the Stage-2 matrix is about"),
    ):
        mutations.append(
            Mutation(
                MutationKind.FILE_ATTRIBUTE,
                attributed,
                f"{flag} — {why}",
                file_path=attributed,
            )
        )

    mutations.append(
        Mutation(
            MutationKind.POSTGRES_DATABASE,
            target.database_name,
            "the disposable synthetic facsimile; never freedom_test, which the "
            "repository's two suites share (finding F-6).",
        )
    )
    mutations.append(
        Mutation(
            MutationKind.POSTGRES_ROLE,
            COORDINATOR_ROLE,
            "§2.12.3's coordinator role, PASSWORD NULL, in the disposable "
            "instance only.",
        )
    )

    for filename, why in (
        (
            "pg_hba.conf",
            "§2.12.3's five lines, in that order, above any broader local rule",
        ),
        ("pg_ident.conf", "§2.12.3's one freedom_coord identity-map line"),
    ):
        mutations.append(
            Mutation(
                MutationKind.POSTGRES_CONFIG_LINE,
                f"{filename}:{MAPPED_OS_USER}->{MAPPED_POSTGRES_ROLE}",
                why,
                file_path=target.config_path(filename),
                maps_os_user=MAPPED_OS_USER,
                maps_postgres_role=MAPPED_POSTGRES_ROLE,
            )
        )

    mutations.append(
        Mutation(
            MutationKind.TRANSIENT_UNIT,
            TRANSIENT_UNIT,
            "Stage 4's sandbox, started with systemd-run --unit= so systemctl "
            "can be asked about exactly the thing that ran.",
        )
    )
    return tuple(mutations)


# ---------------------------------------------------------------------------
# psql, built once so no two steps can disagree about how a connection is made
# ---------------------------------------------------------------------------


def _psql(
    target: DisposableTarget,
    *,
    dbname: str,
    command: str,
    username: str = "",
    host: str = "",
    port: int = 0,
    tuples_only: bool = False,
) -> tuple[str, ...]:
    """One `psql` vector.

    `--no-password` on every one of them, always: it makes the invocation
    non-interactive, so a step cannot block on a prompt no operator is watching,
    and it means no credential is ever supplied or read. `--no-psqlrc` keeps a
    stray `~/.psqlrc` from changing what runs. `ON_ERROR_STOP=1` makes the exit
    status mean what the plan says it means.

    `tuples_only` adds `--tuples-only --no-align`, and only the two R14 catalog
    baselines use it: one name per line, no header, no row count and no column
    padding, which is the shape `capture._catalog_membership` reads. It changes
    the **format** of a listing and never which rows are listed — the reviewed
    grammar admits no string literal, so no `psql` vector in this plan filters
    anything.
    """
    argv = [
        "/usr/bin/psql",
        "--no-psqlrc",
        "--no-password",
        "--set",
        "ON_ERROR_STOP=1",
        "--host",
        host or target.postgres_socket_directory,
    ]
    if port:
        argv.extend(["--port", str(port)])
    if tuples_only:
        argv.extend(["--tuples-only", "--no-align"])
    argv.extend(["--dbname", dbname])
    if username:
        argv.extend(["--username", username])
    argv.extend(["--command", command])
    return tuple(argv)


# ---------------------------------------------------------------------------
# The declared semantic expectations — R13, Blocking finding EH-R13-3
# ---------------------------------------------------------------------------
#
# Every step that records an observation states, here, what that observation has
# to say for the step to be satisfied. R12 left this to the bands, which classify
# records *after* a run; the execution loop never consulted them, so a `getent`
# reporting a `freedomjournal` with an unexpected member and a `capsh` reporting
# an empty bounding set were both recorded as passes and every dependent step ran
# behind them. `plan.CommandStep` now refuses a step that records an observation
# and declares nothing, and `expectations.declared_contract` refuses a
# declaration that does not cover every key its policy emits — so this section
# cannot be incomplete without the plan failing to build.
#
# Three policies are absent from it on purpose. `EXIT_STATUS_ONLY` records
# nothing. `CASE_RUNTIME`, `CASE_IDENTITY` and `CAPABILITY_MASKS` are compared
# against reviewed constants — the interpreter's target facts, the review
# manifest's covered-source digest, §2.13.5c's derivation and
# `capability.E7_TARGET_FACTS` — and a plan that wrote those down would be
# stating the expectation it is judged against.


def _expect(
    key: str, comparison: Comparison, value: str, uncompared_because: str = ""
) -> DeclaredExpectation:
    return DeclaredExpectation(
        key=key,
        comparison=comparison,
        value=value,
        uncompared_because=uncompared_because,
    )


#: Why a numeric id is recorded and not compared. `groupadd --system` and
#: `useradd --system` allocate from the host's system range, so the number does
#: not exist when the plan is generated and cannot be written into it; the
#: existing host identities' numbers are host facts no reviewed prerequisite
#: states. What §2.12.2 states — and what `JNL-52` asserts — is **names and
#: membership**, and those are compared exactly. The numbers the `capsh`
#: construction needs are resolved independently, immediately before each step,
#: through the executor's injected NSS boundary (conflict C-5).
_ALLOCATED_ID = (
    "a system uid/gid allocated by useradd/groupadd at run time, or an existing "
    "host identity's number; §2.12.2 states names and membership, and the "
    "capsh construction resolves its numbers through the late-binding boundary"
)


def _names(names) -> str:
    """A reviewed name set, in the canonical text form the capture boundary
    produces for one: sorted and comma-joined, or `none` for the empty set."""
    ordered = sorted(names)
    return ",".join(ordered) if ordered else EMPTY_SET


def _group_members_expected(group: str) -> tuple[DeclaredExpectation, ...]:
    """`getent group NAME`, compared against §2.12.2's canonical inverse.

    The member set is compared **as a set and in both directions**, which is
    P5.0-SR2's rule and the reason an unexpected member is a failed case rather
    than a difference to note.
    """
    canonical = CANONICAL_GROUPS.get(group)
    if canonical is None:
        raise PlanRefused(
            f"Group {group!r} is asserted by this plan and is not in §2.12.2's "
            "canonical table, so there is no reviewed membership to compare its "
            "observation with."
        )
    return (
        _expect("group", Comparison.TEXT, group),
        _expect("gid", Comparison.NUMBER_PRESENT, "1000", _ALLOCATED_ID),
        _expect("members", Comparison.TEXT_SET, _names(canonical.members)),
    )


def _account_identity_expected(account: str) -> tuple[DeclaredExpectation, ...]:
    """`id NAME`, compared against §2.12.2's canonical row.

    `id` prints the primary group inside `groups=`, so the expected set is the
    primary group **and** the canonical supplementary set — the one place the two
    halves of §2.12.2's table are combined, and it is combined from the table
    rather than restated.
    """
    canonical = CANONICAL_ACCOUNTS.get(account)
    if canonical is None:
        raise PlanRefused(
            f"Account {account!r} is asserted by this plan and is not in "
            "§2.12.2's canonical table."
        )
    return (
        _expect("uid", Comparison.NUMBER_PRESENT, "1000", _ALLOCATED_ID),
        _expect("uid_name", Comparison.TEXT, account),
        _expect("gid", Comparison.NUMBER_PRESENT, "1000", _ALLOCATED_ID),
        _expect("gid_name", Comparison.TEXT, canonical.primary_group),
        _expect(
            "groups",
            Comparison.TEXT_SET,
            _names({canonical.primary_group, *canonical.supplementary}),
        ),
    )


def _root_identity_expected() -> tuple[DeclaredExpectation, ...]:
    """`R-01`'s `id`, with no operand: the identity the run executes as.

    uid and gid are compared exactly, because *"uid 0, gid 0"* is the whole of
    what this step asserts and every Band 2-6 step assumes it. The complete
    supplementary set is **not** compared here: it is one of `E7`'s ten reviewed
    target facts and `P-06` compares it against that fact, in the final
    interpreted process, through the same code path as the seven constructed
    identities. Comparing it twice from two sources is how two sources come to
    disagree.
    """
    return (
        _expect("uid", Comparison.NUMBER, "0"),
        _expect("uid_name", Comparison.TEXT, "root"),
        _expect("gid", Comparison.NUMBER, "0"),
        _expect("gid_name", Comparison.TEXT, "root"),
        _expect(
            "groups",
            Comparison.TEXT_PRESENT,
            "root",
            "E7's complete supplementary set is a reviewed target fact compared "
            "by P-06 against capability.E7_TARGET_FACTS; a second expectation "
            "here would be a second source for one fact",
        ),
    )


def _attribute_flags_expected(
    *, append_only: bool, immutable: bool
) -> tuple[DeclaredExpectation, ...]:
    """`lsattr`, compared against the flags this plan's own `chattr` set."""
    return (
        _expect("append_only", Comparison.TEXT, "yes" if append_only else "no"),
        _expect("immutable", Comparison.TEXT, "yes" if immutable else "no"),
    )


def _mount_facts_expected() -> tuple[DeclaredExpectation, ...]:
    """`findmnt` on the arena, compared against the **confirmed** target facts.

    The filesystem type and the backing device are `approved_target.
    APPROVED_TARGET_FACTS`' — stated by the Operations Owner on 2026-09-05 and
    part of what `require_approved_target()` already refuses a deviation in — so
    no new unconfirmed fact is needed and the expectation has an independent
    source. `read_only` is the plan's own claim: Stage 3's control asserts a
    writable mount, and an append-only refusal taken on a read-only one
    attributes nothing.
    """
    return (
        _expect("fstype", Comparison.TEXT, APPROVED_TARGET_FACTS.filesystem_type),
        _expect("source", Comparison.TEXT, APPROVED_TARGET_FACTS.filesystem_device),
        _expect("read_only", Comparison.TEXT, "no"),
    )


def _stat_mode(mode: str) -> str:
    """A four-digit `install --mode` argument as `stat --format=%a` prints it.

    The case program is installed `0555` and `stat` prints `555`: `%a` emits the
    octal permission bits with no leading zero unless a set-user-ID,
    set-group-ID or sticky bit is set. Deriving the expected text from the mode
    the plan installs keeps one source for the value; writing `555` beside
    `0555` would be two.
    """
    trimmed = mode.lstrip("0")
    return trimmed if trimmed else "0"


def _file_mode_expected(
    *, uid: str, gid: str, mode: str, file_type: str
) -> tuple[DeclaredExpectation, ...]:
    return (
        _expect("uid", Comparison.NUMBER, uid),
        _expect("gid", Comparison.NUMBER, gid),
        _expect("mode", Comparison.TEXT, mode),
        _expect("file_type", Comparison.TEXT, file_type),
    )


def _no_file_capability_expected() -> tuple[DeclaredExpectation, ...]:
    return (_expect("file_capability_present", Comparison.TEXT, "no"),)


def _unit_directives_expected(
    *, protect_system: str, read_write_paths: str
) -> tuple[DeclaredExpectation, ...]:
    return (
        _expect("ProtectSystem", Comparison.TEXT, protect_system),
        _expect("ReadWritePaths", Comparison.TEXT, read_write_paths),
    )


#: The `errno` a negative access case may report. Both, and for exactly the
#: reason `_ACCESS_DENIAL_STATUSES` admits both exit statuses: §5.2 states the
#: same kernel check as `EPERM` in one sentence and `EACCES` in another, the two
#: cannot both be right, and ruling on it is the package plan's to do and not
#: this generator's. The admitted pair is written in the plan and pinned in the
#: review manifest, so it is as reviewed as a single value would be.
_DENIAL_ERRNOS = "EPERM|EACCES"


def _case_result_expected(
    verb: str,
    *,
    refused: bool,
    errnos: str = _DENIAL_ERRNOS,
    extra: Sequence[DeclaredExpectation] = (),
) -> tuple[DeclaredExpectation, ...]:
    """The case program's own output for one operation.

    The key set is decided by the program rather than described: a refusal emits
    `verb`, `result` and `errno` and nothing else, and a return emits those three
    — with `errno=none` — plus the size or flag facts the verb produces. `extra`
    carries those, and it is refused for a refusal, where the operation did not
    reach the point of producing one.
    """
    if refused:
        if extra:
            raise PlanRefused(
                f"A refused {verb!r} case declares a size or flag observation. "
                "The operation did not return, so the case program emits its "
                "verb, its result and its errno and nothing else."
            )
        return (
            _expect("verb", Comparison.TEXT, verb),
            _expect("result", Comparison.TEXT, "refused"),
            _expect("errno", Comparison.TEXT_ANY_OF, errnos),
        )
    return (
        _expect("verb", Comparison.TEXT, verb),
        _expect("result", Comparison.TEXT, "returned"),
        _expect("errno", Comparison.TEXT, "none"),
        *extra,
    )


#: Why a byte count or file size is recorded and not compared: it depends on what
#: the disposable file holds when the operation runs, which the plan does not fix
#: and which the band's own classifier reads from the record.
_RUNTIME_SIZE = (
    "a size or byte count that depends on the disposable file's state when the "
    "operation runs; the band classifies it from the record"
)

#: **R16, conflict C-8.** Why the created root's device and inode are recorded
#: and not compared: the kernel allocates them, so no reviewed plan can state
#: them in advance. They are not uncompared in the sense that matters, either —
#: `statroot` reads the same two numbers back at cleanup and the executor
#: compares **the two observations with each other** before it removes anything.
_RUNTIME_IDENTITY = (
    "the device and inode the kernel allocated for the directory this step "
    "created; no plan can state them in advance, and cleanup compares them with "
    "the values `statroot` reads back rather than with a declared constant"
)

#: The returned facts whose value is text rather than a decimal number.
_TEXT_FACTS = frozenset({"link_target", "created"})


#: What the case program emits **in addition** to `verb`, `result` and `errno`
#: when an operation returns, per verb. It is a transcription of
#: `execution/case_program.py`'s `_do_*` return values, and
#: `tests/phase_5_0_evidence/test_case_program.py` asserts the two agree — so a
#: verb that grows an observation without a declared expectation fails the suite
#: rather than reaching a run.
_RETURNED_FACTS: dict[str, tuple[str, ...]] = {
    "open": (),
    "pwrite": ("bytes_written", "pre_size", "post_size"),
    "append": ("bytes_written", "pre_size", "post_size"),
    "ftruncate": ("post_size",),
    "rename": (),
    "unlink": (),
    "symlink": ("link_target",),
    "statvfs": ("st_rdonly",),
    "getflags": ("fs_append_fl",),
    "clearflags": ("fs_append_fl",),
    # **Conflict C-6.** The immutable half. Both verbs report the one bit they
    # are about, and the key is `fs_immutable_fl` rather than `fs_append_fl`, so
    # an append-only observation can never satisfy an immutable-flag
    # expectation — which is the substitution the R13/R14 boundary refused to
    # let this band approximate.
    "getimmutable": ("fs_immutable_fl",),
    "clearimmutable": ("fs_immutable_fl",),
    # **Conflict C-8.** `mkroot`'s ownership evidence, and the reading cleanup
    # revalidates it against.
    "mkroot": ("created", "root_device", "root_inode"),
    "statroot": ("root_device", "root_inode"),
}

#: Exit status back to errno name, so a step that declares *"satisfied by exit
#: 12"* declares the matching `errno=EROFS` expectation from the same table
#: rather than from a second one written beside it.
_ERRNO_FOR_STATUS = {status: name for name, status in REFUSAL_EXIT_CODES.items()}


def _case_result_for(
    argv: Sequence[str],
    satisfying_statuses: Sequence[int],
    *,
    known: Mapping[str, str] = {},
) -> tuple[DeclaredExpectation, ...]:
    """The declared expectation for one case-program step, from its own vector.

    Derived rather than written per site, and derived from the two things the
    reviewed step already states: **which verb its vector names** and **which
    exit statuses satisfy it**. A step satisfied by exit 0 expects
    `result=returned`, `errno=none` and exactly the size or flag keys its verb
    produces; a step satisfied by refusal statuses expects `result=refused` and
    an `errno` drawn from the same names those statuses stand for. The two can
    therefore not disagree, which is what writing them out separately would
    allow.

    `known` states the value of a returned fact the plan does fix — `st_rdonly=0`
    for Stage 3's control, `fs_append_fl=1` for the flag read-back — and every
    fact it does not name is recorded and shape-checked rather than compared,
    with `_RUNTIME_SIZE` saying why.
    """
    verb = _case_program_verb_anywhere(argv)
    if verb not in _RETURNED_FACTS:
        raise PlanRefused(
            f"{verb!r} is not an operation verb this generator can state an "
            "expectation for; a case-program step names one of "
            f"{sorted(_RETURNED_FACTS)}."
        )
    statuses = tuple(satisfying_statuses)
    if statuses == (0,):
        extra: list[DeclaredExpectation] = []
        for key in _RETURNED_FACTS[verb]:
            if key in known:
                extra.append(
                    _expect(
                        key,
                        Comparison.TEXT if key in _TEXT_FACTS else Comparison.NUMBER,
                        known[key],
                    )
                )
            elif key in _TEXT_FACTS:
                raise PlanRefused(
                    f"A returned {verb!r} states {key!r}; it is the one fact the "
                    "operation reports about what it did, so leaving it "
                    "uncompared would leave that unchecked."
                )
            elif key in ("root_device", "root_inode"):
                extra.append(
                    _expect(key, Comparison.NUMBER_PRESENT, "0", _RUNTIME_IDENTITY)
                )
            else:
                extra.append(
                    _expect(key, Comparison.NUMBER_PRESENT, "0", _RUNTIME_SIZE)
                )
        return _case_result_expected(verb, refused=False, extra=tuple(extra))
    if 0 in statuses:
        raise PlanRefused(
            "A case-program step is satisfied either by the operation returning "
            "or by its being refused. One that admits both would be satisfied "
            "whatever the boundary under test did."
        )
    names = []
    for status in statuses:
        name = _ERRNO_FOR_STATUS.get(status)
        if name is None:
            raise PlanRefused(
                f"Exit status {status} is not one of the case program's reported "
                "refusals, so no errno expectation can be stated for it."
            )
        names.append(name)
    unique = sorted(set(names))
    if len(unique) == 1:
        # One admitted errno is an exact comparison, and writing it as a
        # one-member list would spell an exact comparison as a choice.
        return (
            _expect("verb", Comparison.TEXT, verb),
            _expect("result", Comparison.TEXT, "refused"),
            _expect("errno", Comparison.TEXT, unique[0]),
        )
    return _case_result_expected(verb, refused=True, errnos="|".join(unique))


def _case_program_verb_anywhere(argv: Sequence[str]) -> str:
    """The verb a case-program vector names, wherever the interpreter appears.

    A direct vector begins with the interpreter; a `capsh` construction names it
    with `--shell=` and a `systemd-run` one puts it after `--`. All three run the
    same program with the same grammar, so the verb is read from the position
    after the program path rather than from a fixed index.

    **R16, conflict C-8.** The bootstrap vector names the reviewed **source**
    rather than the installed copy, so both spellings of the program are matched.
    They are the same bytes, and one manifest digest covers both.
    """
    for index, argument in enumerate(argv):
        if (
            argument.endswith("/bin/case") or argument == CASE_PROGRAM_SOURCE_PATH
        ) and index + 1 < len(argv):
            return argv[index + 1]
    raise PlanRefused(
        "This vector does not name the reviewed case program, so it states no "
        "operation verb."
    )


# ---------------------------------------------------------------------------
# The step list
# ---------------------------------------------------------------------------


class _Steps:
    """Accumulates steps and unresolved items, keeping ids unique and ordered."""

    def __init__(self) -> None:
        self.steps: list[CommandStep] = []
        self.materializations: list[MaterializeStep] = []
        self.unresolved: list[UnresolvedStep] = []
        self.external_cases: list[ExternalCase] = []

    def add(self, step: CommandStep) -> None:
        self.steps.append(step)

    def materialize(self, step: MaterializeStep) -> None:
        self.materializations.append(step)

    def block(self, item: UnresolvedStep) -> None:
        self.unresolved.append(item)

    def external(self, item: ExternalCase) -> None:
        self.external_cases.append(item)


#: The mutation kinds whose subject lives under the disposable root. **R16,
#: conflict C-8**: their ownership follows from the root's exclusive creation
#: rather than from a probe, because `mkdir(2)` returns an empty directory — so
#: at the instant `B3-01` is satisfied there is nothing under that path for a
#: later step to overwrite and nothing this run could later delete that it did
#: not itself put there. `_contained_mutation_ids` checks the containment rather
#: than assuming it, and refuses any declared path that is neither the root nor
#: inside it.
_ROOT_CONTAINED_KINDS = (
    MutationKind.DIRECTORY,
    MutationKind.FILE,
    MutationKind.FILE_ATTRIBUTE,
)


def _contained_mutation_ids(
    mutations: Sequence[Mutation], root: str
) -> tuple[str, ...]:
    """Every declared path mutation whose subject is the root or is inside it.

    A path that is neither is refused rather than silently left unowned: the two
    PostgreSQL configuration files are the only paths this harness writes outside
    the root, they are `POSTGRES_CONFIG_LINE` mutations reversed by a **restore**
    rather than a deletion, and a fourth kind of path appearing here would be a
    path nothing had proved absent and something was about to delete.
    """
    contained: list[str] = []
    for mutation in mutations:
        if mutation.kind not in _ROOT_CONTAINED_KINDS:
            continue
        path = mutation.identifier
        if path != root and not path.startswith(f"{root}/"):
            raise PlanRefused(
                f"Mutation {mutation.mutation_id!r} names a path outside the "
                "disposable root, so the root's absence does not establish that "
                "this run would create it and its reversal would delete "
                "something this run did not make."
            )
        contained.append(mutation.mutation_id)
    return tuple(contained)


#: `psql`'s own exit statuses. **R14, EH-R14-1: neither is an absence result,
#: and no step in this plan treats one as though it were.** They are retained
#: named, and unused as satisfying statuses, because the correction is easier to
#: review beside the thing it replaced: 2 is a **connection** failure, and
#: `pg_database.datallowconn = false` produces it for a database that plainly
#: exists; 3 is **any** statement error under `ON_ERROR_STOP=1`, of which *"the
#: role does not exist"* is one of many. R13 read the first as *"the database is
#: not there"* and the second as *"the role is not there"*, and both baselines
#: then granted ownership that cleanup acted on. Both now read a successful
#: catalog listing instead.
PSQL_CONNECTION_FAILED = 2
PSQL_STATEMENT_FAILED = 3


def _band_0(
    steps: _Steps, target: DisposableTarget, paths: _Paths, mutations: Sequence[Mutation]
) -> None:
    """Discovery, and — **R13** — the ownership baseline.

    ## Why a baseline exists at all: Blocking finding EH-R13-1

    Cleanup deletes accounts, groups, memberships, paths, a database, a role and
    a transient unit. Until R13 the only thing it asked before deleting one was
    whether *some* mutation had been attempted, and the only pre-change
    observation in the whole plan was `R-02`'s single `getent` on
    `freedomjournal`. So a run that stopped on its second `groupadd` went on to
    `groupdel` three groups it had never reached and to `DROP DATABASE IF EXISTS`
    a database no step had created — and if any of those objects had been on the
    host before the run, the harness would have deleted somebody else's.

    A cleanup step may therefore reverse a mutation only when **two** things
    hold, and this band establishes the first:

    1. a baseline step observed the subject **absent before anything changed**,
       which is what makes the object this run's to remove; and
    2. the run **attempted** the mutation, which the executor records before the
       boundary is called so an unknown launch outcome counts as attempted.

    Ownership is additionally **withdrawn** when a creation reports the object
    already existed — `groupadd` and `useradd`'s exit 9 — because an object that
    was already there was not created by the step that found it.

    ## What each baseline step proves, and what it does not — corrected in R14

    **Blocking finding EH-R14-1.** R13 proved absence with a **failure** wherever
    the tool had one, and three of those failures do not mean *absent*:

    | Baseline | R13 read | R14 |
    |---|---|---|
    | `getent group` / `getent passwd` | exit 2 | **kept.** `getent(1)` documents 2 as *"one or more supplied key could not be found in the database"*, distinct from 1 for a missing argument or unknown database and 3 for an unsupported enumeration. It is an absence result, not a generic failure |
    | `stat` on the root | exit 1 | **establishes nothing, and no longer needs to — R16.** Coreutils gives every failure the same 1, so an existing path on a filesystem returning EIO looked absent, and no permitted executable can distinguish them. The root's ownership now comes from `B3-01`'s exclusive `mkdir(2)`, whose EEXIST is unique; this step is retained as a precondition that stops a doomed run early. See `_create_disposable_root` and conflict C-8 |
    | `psql` connecting to the evidence database | exit 2 | **replaced.** Exit 2 is a connection failure, and `datallowconn = false` produces it for a database that exists |
    | `psql` running `SET ROLE` | exit 3 | **replaced.** Exit 3 under `ON_ERROR_STOP=1` is any statement error |
    | `systemctl show` | `LoadState=not-found` | **kept.** A successful command whose compared answer names the state |

    The two replacements read a catalog listing that PostgreSQL **returns**, and
    compare it with two names the plan states: the subject, which must be absent,
    and a control, which must be present. The control is what separates *absent*
    from *unknown*, and it does it inside the same reading rather than from a
    different object — `R-B-PG`'s successful connection to `postgres` proved the
    server was reachable and proved nothing whatever about another database.

    Three states, and only one grants ownership: **absent** (listing read,
    control there, subject not), **present** (subject there, run stops, nothing
    removed) and **unknown** (no listing, no control, an unparsable line, a
    non-zero exit — run stops, no ownership, nothing removed). *Unknown never
    authorizes a deletion.*

    One `stat` was to have covered every declared path. It no longer covers any:
    `_contained_mutation_ids` still refuses a declared path outside the root, and
    still enumerates the paths, but the enumeration is now the **blocked** set on
    conflict C-8 rather than an ownership grant.
    """
    steps.add(
        CommandStep(
            step_id="R-01",
            band="discovery",
            run_as="root",
            argv=("/usr/bin/id",),
            purpose=(
                "Record the identity the run actually executes as, before "
                "anything is constructed."
            ),
            evidence_case_ids=("PREFLIGHT-IDENTITY",),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.ACCOUNT_IDENTITY,
            observation_expectations=_root_identity_expected(),
            expected_result=(
                "uid 0, gid 0 — the executing identity every Band 2-6 step "
                "assumes, and compared rather than recorded (EH-R13-3)."
            ),
            expected_refusal="",
        )
    )
    for group in CREATED_GROUPS:
        steps.add(
            CommandStep(
                step_id=("R-02" if group == JOURNAL_GROUP else f"R-B-G-{group}"),
                band="discovery",
                run_as="root",
                argv=("/usr/bin/getent", "group", group),
                purpose=(
                    f"Prove the {group} group does not already exist on this "
                    "host, so that this run's `groupdel` would remove a group "
                    "this run created — EH-R13-1."
                ),
                evidence_case_ids=(
                    ("JNL-52-PRECONDITION",) if group == JOURNAL_GROUP else ()
                ),
                role=StepRole.PREREQUISITE,
                satisfying_statuses=(2,),
                establishes_ownership_of=(
                    (f"os_group:{group}", *_MEMBERSHIPS_INTO[group])
                    if group in _MEMBERSHIPS_INTO
                    else (f"os_group:{group}",)
                ),
                expected_result=(
                    "exit 2 — absent, the expected pre-implementation state, and "
                    "the ownership this run's cleanup needs."
                ),
                expected_refusal=(
                    "exit 0 means the group already exists. The run stops before "
                    "any mutation, and **nothing is deleted**: a group nobody "
                    "proved absent is not a group this harness may remove."
                ),
            )
        )
    for account, _primary in CREATED_ACCOUNTS:
        steps.add(
            CommandStep(
                step_id=f"R-B-A-{account}",
                band="discovery",
                run_as="root",
                argv=("/usr/bin/getent", "passwd", account),
                purpose=(
                    f"Prove the {account} account does not already exist, so that "
                    "this run's `userdel` would remove an account this run "
                    "created — EH-R13-1."
                ),
                role=StepRole.PREREQUISITE,
                satisfying_statuses=(2,),
                establishes_ownership_of=(f"os_account:{account}",),
                expected_result="exit 2 — absent.",
                expected_refusal=(
                    "exit 0 means the account already exists. The run stops "
                    "before any mutation and nothing is deleted."
                ),
            )
        )
    steps.add(
        CommandStep(
            step_id="R-B-ROOT",
            band="discovery",
            run_as="root",
            argv=("/usr/bin/stat", "--format=%F", paths.root),
            purpose=(
                "Stop the run if the disposable root already resolves. **It "
                "establishes no ownership — R14, EH-R14-1.** `stat` exits 1 for "
                "every failure it has, so its exit 1 does not say *absent*; it "
                "says *did not resolve*, and a path that exists on a filesystem "
                "returning EIO says the same thing. What it does say soundly is "
                "the other direction: exit 0 means something is there, and that "
                "stops the run."
            ),
            role=StepRole.PREREQUISITE,
            # `stat` exits 1 for a path that is not there and prints nothing.
            satisfying_statuses=(1,),
            expected_result=(
                "exit 1 — the root did not resolve. This is a **precondition, "
                "not a proof of absence**, and it establishes ownership of "
                "nothing: `stat` gives every failure the same 1, so ENOENT, "
                "ENOTDIR, ELOOP, ENAMETOOLONG, EACCES and EIO are one number "
                "here. What owns the root is `B3-01`'s exclusive `mkdir(2)`, "
                "whose EEXIST is unique and whose success is the proof — R16, "
                "conflict C-8. This step is retained because it stops a run "
                "early, before a single identity is provisioned, when the root "
                "is plainly already there."
            ),
            expected_refusal=(
                "exit 0 means the root already exists. The run stops before any "
                "mutation, and no path under it is removed: §2.13.2b's operator "
                "recovery clears a previous run's residue, and this harness does "
                "not. A run that reaches `B3-01` regardless — because `stat` "
                "failed for some other reason — is stopped there by EEXIST, "
                "with ownership withdrawn rather than merely unclaimed."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id="R-B-PG",
            band="discovery",
            run_as="postgres",
            argv=_psql(target, dbname="postgres", command="SELECT 1"),
            purpose=(
                "Establish that the disposable instance is reachable as "
                "`postgres` over this socket, and that the `postgres` role and "
                "the `postgres` database — the **control name** both catalog "
                "baselines look for — are there to be found. It returns the "
                "constant 1 and reads nothing. "
                "**R14, EH-R14-1 narrows what this control is for.** R13 called "
                "it the positive control for two baselines that were satisfied "
                "by a non-zero psql exit, and it could not be: connecting to "
                "`postgres` says nothing about whether another database exists, "
                "and an existing one that refuses connections produced the same "
                "exit 2 as an absent one. Separating *absent* from *unknown* is "
                "now done inside each baseline's own reading, by a control name "
                "the same listing must carry. What this step still does is make "
                "that name a fact rather than an assumption, and stop the run "
                "before any mutation when the instance is unreachable."
            ),
            role=StepRole.CONTROL,
            expected_result=(
                "exit 0 — the disposable instance is reachable as postgres, so "
                "the `postgres` role and database both exist."
            ),
            expected_refusal=(
                "any non-zero exit stops the run before any mutation. No "
                "ownership is established, so nothing this plan declares could be "
                "removed even if a later step had reached it."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id="R-B-DB",
            band="discovery",
            run_as="postgres",
            argv=_psql(
                target,
                dbname="postgres",
                command="SELECT datname FROM pg_database",
                tuples_only=True,
            ),
            purpose=(
                f"Prove {target.database_name} does not already exist, so that "
                "this run's DROP DATABASE would drop a database this run created "
                "— EH-R13-1, corrected in R14."
            ),
            role=StepRole.DEPENDENT,
            satisfying_statuses=(0,),
            capture=CapturePolicy.CATALOG_MEMBERSHIP,
            catalog_question=CatalogQuestion(
                subject=target.database_name, control="postgres"
            ),
            observation_expectations=(
                _expect("control_present", Comparison.TEXT, "yes"),
                _expect("subject_present", Comparison.TEXT, "no"),
            ),
            establishes_ownership_of=(f"postgres_database:{target.database_name}",),
            expected_result=(
                "exit 0, and a listing that carries `postgres` and does not carry "
                f"{target.database_name}. **R14, EH-R14-1: absence is what the "
                "catalog returned, not a failure.** Until R13 this step connected "
                f"to {target.database_name} and took psql's exit 2 as proof it "
                "was not there. Exit 2 is a connection failure; "
                "`pg_database.datallowconn = false` refuses a connection to a "
                "database that is plainly there, so a pre-existing evidence "
                "database with connections disabled satisfied the baseline and "
                "handed this run ownership of somebody else's. `R-B-PG` did not "
                "catch it: connecting to `postgres` says nothing about another "
                "database. The control name in the listing now does the work "
                "`R-B-PG` could not — it proves this reading reached the catalog."
            ),
            expected_refusal=(
                "three ways, and each stops the run before any mutation with no "
                "ownership established. `subject_present=yes` means the database "
                "is there and is somebody's — `DROP DATABASE IF EXISTS` is "
                "idempotent, and that is not the question, because idempotence "
                "would make dropping it quiet rather than safe. "
                "`control_present=no`, an unparsable line or a missing question "
                "means the listing was not read, which is *unknown* and never "
                "*absent*. A non-zero exit means psql could not run the query at "
                "all, which is the same."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id="R-B-ROLE",
            band="discovery",
            run_as="postgres",
            # **R14, EH-R14-1.** An unfiltered `pg_roles` listing, because the
            # reviewed vector grammar admits no string literal: `'`, `*` and `>`
            # are all refused as arguments, deliberately, so `SELECT … WHERE
            # rolname = 'x'` cannot be written and must not be. The two names
            # this listing is asked about therefore travel beside the vector, in
            # `catalog_question`, where the manifest pins them.
            argv=_psql(
                target,
                dbname="postgres",
                command="SELECT rolname FROM pg_roles",
                tuples_only=True,
            ),
            purpose=(
                f"Prove the {COORDINATOR_ROLE} role does not already exist — "
                "EH-R13-1, corrected in R14."
            ),
            role=StepRole.DEPENDENT,
            satisfying_statuses=(0,),
            capture=CapturePolicy.CATALOG_MEMBERSHIP,
            catalog_question=CatalogQuestion(
                subject=COORDINATOR_ROLE, control="postgres"
            ),
            observation_expectations=(
                _expect("control_present", Comparison.TEXT, "yes"),
                _expect("subject_present", Comparison.TEXT, "no"),
            ),
            establishes_ownership_of=(f"postgres_role:{COORDINATOR_ROLE}",),
            expected_result=(
                "exit 0, and a listing that carries `postgres` and does not carry "
                f"{COORDINATOR_ROLE}. R13 read this as `SET ROLE` and took psql's "
                "exit 3 as proof of absence. Exit 3 under `ON_ERROR_STOP=1` is "
                "**any** statement error — a permission refusal, a catalog "
                "failure, a syntax rejection by a different server version — so "
                "it identified absence no more uniquely than exit 2 did for the "
                "database. The listing is read once and compared with two names "
                "the plan states."
            ),
            expected_refusal=(
                "`subject_present=yes` means the role already exists and is "
                "somebody's; the run stops before any mutation and leaves it in "
                "place. `control_present=no`, an unparsable line, a missing "
                "question or a non-zero exit is *unknown*, which establishes no "
                "ownership and authorizes no DROP ROLE."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id="R-B-UNIT",
            band="discovery",
            run_as="root",
            argv=(
                "/usr/bin/systemctl",
                "show",
                "--property=LoadState",
                TRANSIENT_UNIT,
            ),
            purpose=(
                f"Prove {TRANSIENT_UNIT} is not already loaded, so that this "
                "run's `systemctl stop` would stop a unit this run started — "
                "EH-R13-1."
            ),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.UNIT_DIRECTIVES,
            observation_expectations=(
                _expect("LoadState", Comparison.TEXT, "not-found"),
            ),
            establishes_ownership_of=(f"transient_unit:{TRANSIENT_UNIT}",),
            expected_result="LoadState=not-found.",
            expected_refusal=(
                "any other load state means a unit of this name is already "
                "known to systemd. The run stops before any mutation and stops "
                "nothing."
            ),
        )
    )
    return None


def _root_ownership_note() -> str:
    """**R16, conflict C-8, resolved.** Where the filesystem ownership now comes from.

    R14 blocked this baseline and left the 29 path mutations owned by nothing.
    The repair is not a better probe — no permitted executable has one — it is a
    different shape: `B3-01` creates the root with `mkdir(2)`, whose `EEXIST` is
    unique and documented and whose success **is** the proof that nothing was
    there. See `_create_disposable_root`, which states the mechanism, the
    bootstrap location, the result vocabulary, the ownership evidence and the
    cleanup revalidation in full.

    `R-B-ROOT` is unchanged and still establishes nothing. It is a precondition
    that stops an obviously doomed run before a single identity is provisioned,
    and it is deliberately **not** where ownership was reattached.
    """
    return "conflict C-8: ownership from exclusive creation, not from a probe"


def _band_1(steps: _Steps) -> None:
    steps.add(
        CommandStep(
            step_id="P-01",
            band="capability",
            run_as="root",
            argv=("/usr/sbin/capsh", "--print"),
            purpose=(
                "Read the launching process's bounding set and securebits. capsh "
                "offers --drop and no addition at all, so a capability absent here "
                "cannot be obtained by any later step."
            ),
            evidence_case_ids=("CAP-LAUNCHER-BND",),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.CAPABILITY_MASKS,
            expected_result=(
                "exit 0; the bounding-set mask, the ambient-set mask, the "
                "securebits word and no-new-privs each equal the reviewed target "
                "fact stated for them in `capability.E7_TARGET_FACTS`. **All four "
                "are compared before this step may be satisfied** — R13, "
                "EH-R13-3 — and the seven capabilities every later step needs are "
                "in the bounding set exactly when that mask is the reviewed one."
            ),
            expected_refusal=(
                "a missing, unreadable or unequal value for any of the four makes "
                "this prerequisite unsatisfied and stops the run, so no case is "
                "reported passed or refused. The launching process **is** E7, so "
                "its four values are four of E7's ten reviewed target facts and "
                "are read from that one source; while any is unconfirmed the "
                "executor refuses before it starts any command. R12 compared none "
                "of them: `capsh --print` prints no `CapBnd:` line at all, so the "
                "reader looked for /proc/self/status field names no `capsh` emits "
                "and the step was satisfied by its exit status alone."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id="P-02",
            band="capability",
            run_as="root",
            argv=("/usr/sbin/capsh", "--decode=0x000001ffffffffff"),
            purpose=(
                "Expand the documented E7 mask so it can be compared name-by-name "
                "with the host's PID-1 mask, which is supplied out of band."
            ),
            evidence_case_ids=("CAP-E7-ENVIRONMENT",),
            role=StepRole.PREREQUISITE,
            expected_result="the decode agrees with §8.1 H-6: every capability 0…40, CAP_LAST_CAP 40.",
            expected_refusal=(
                "disagreement is INCONCLUSIVE; the harness prefers neither the "
                "document nor the host."
            ),
        )
    )
    # `P-03`, `P-04` and `P-05` are **not** generated here. Their subject is the
    # case program, which Band 3 installs, and R10 §R10.7 left their position
    # inherited rather than ruled. Resolving conflict C-2 settles it: a
    # prerequisite whose subject does not yet exist is not a prerequisite, so the
    # three are generated in `_band_3` immediately after the install step that
    # creates their subject and before any step that runs it. They keep their
    # `P-` ids and their `capability` band, because what they assert is unchanged
    # — only the point at which they can hold.
    return None


def _band_2(steps: _Steps, mutations_by_id) -> None:
    order = 0

    def next_id() -> str:
        nonlocal order
        order += 1
        return f"B2-{order:02d}"

    for group in CREATED_GROUPS:
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="identity",
                run_as="root",
                argv=("/usr/sbin/groupadd", "--system", group),
                purpose=f"Create the disposable {group} group.",
                mutation_ids=(f"os_group:{group}",),
                preexisting_statuses=(9,),
                expected_result="exit 0; the group exists with a system gid.",
                expected_refusal=(
                    "exit 9 means the group already exists, which stops the run "
                    "**and withdraws this run's ownership of it**: a group this "
                    "run did not create is not a group its cleanup may delete "
                    "(EH-R13-1)."
                ),
            )
        )
    for account, primary in CREATED_ACCOUNTS:
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="identity",
                run_as="root",
                argv=(
                    "/usr/sbin/useradd",
                    "--system",
                    "--no-create-home",
                    "--shell",
                    "/usr/sbin/nologin",
                    "--gid",
                    primary,
                    account,
                ),
                purpose=f"Create the disposable {account} identity, no home and no shell.",
                mutation_ids=(f"os_account:{account}",),
                preexisting_statuses=(9,),
                expected_result="exit 0; the account exists with a system uid.",
                expected_refusal=(
                    "exit 9 means the account already exists, which stops the run "
                    "**and withdraws this run's ownership of it** (EH-R13-1)."
                ),
            )
        )
    for account, group in CREATED_MEMBERSHIPS:
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="identity",
                run_as="root",
                argv=("/usr/sbin/gpasswd", "--add", account, group),
                purpose=f"Add {account} to {group}, as §2.12.2's matrix requires.",
                mutation_ids=(f"group_membership:{account}",),
                expected_result="exit 0.",
                expected_refusal="",
            )
        )
    for group in ASSERTED_GROUPS:
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="identity",
                run_as="root",
                argv=("/usr/bin/getent", "group", group),
                purpose=f"Read {group}'s complete membership back for JNL-52.",
                evidence_case_ids=(f"JNL-52-GROUP-{group}",),
                capture=CapturePolicy.GROUP_MEMBERS,
                observation_expectations=_group_members_expected(group),
                expected_result=(
                    f"{JOURNAL_GROUP} lists exactly {COORD},{WRITER}; every other "
                    "group matches §2.12.2's complete list. **The member set is "
                    "compared as a set, in both directions, before this step may "
                    "be satisfied** — EH-R13-3."
                ),
                expected_refusal=(
                    "an unexpected member is a FAILED case, not a noted difference "
                    "(P5.0-SR2), and it stops the rehearsal."
                ),
            )
        )
    for account in ASSERTED_ACCOUNTS:
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="identity",
                run_as="root",
                argv=("/usr/bin/id", account),
                purpose=f"Read {account}'s complete supplementary list back for JNL-52.",
                evidence_case_ids=(f"JNL-52-ID-{account}",),
                capture=CapturePolicy.ACCOUNT_IDENTITY,
                observation_expectations=_account_identity_expected(account),
                expected_result=(
                    "the account name, its primary group's name and its complete "
                    "group set equal §2.12.2's row, the set compared as a set and "
                    "in both directions, **before this step may be satisfied** — "
                    "EH-R13-3."
                ),
                expected_refusal="a set difference in either direction is a FAILED case.",
            )
        )


def _component(path: str) -> tuple[str, str]:
    """The `(directory_role, name)` pair a reviewed absolute path denotes.

    The role is the parent directory's own name, which is the role the
    descriptor inventory registers it under, and the name is one component. The
    absolute path stays in the plan for the reviewer and for the mutation id; it
    is never resolved, because resolving it is exactly what `install` and
    `chattr` did.
    """
    parent, _, name = path.rpartition("/")
    return parent.rpartition("/")[2], name


def _create_directory(
    step_id: str, band: str, path: str, mode: str, owner: str, group: str, why: str
) -> CommandStep:
    """**P1 + P1b**, replacing `install --directory`.

    `install --directory` succeeds whether or not the directory was already
    there, so it establishes no ownership. `mkdirat(parent_traversal, name,
    mode)` with exclusive creation refuses with `EEXIST` instead, and the
    successful creation *is* the ownership proof.
    """
    _parent_role, name = _component(path)
    return CommandStep(
        step_id=step_id,
        band=band,
        run_as="root",
        argv=(),
        effect=DescriptorEffect(
            kind=EffectKind.CREATE_DIRECTORY,
            directory_role=ROOT_ROLE,
            name=name,
            path=path,
            mode=int(mode, 8),
            owner=owner,
            group=group,
        ),
        purpose=why,
        mutation_ids=(f"directory:{path}",),
        expected_result=(
            f"the exclusive `mkdirat` created {path} as {owner}:{group} {mode} "
            "and the root's containing-entry barrier returned success."
        ),
        expected_refusal=(
            "`EEXIST` refuses: an entry already at that name is an object this "
            "run did not create and may not own."
        ),
    )


def _set_flag(
    step_id: str,
    band: str,
    path: str,
    flag: str,
    *,
    why: str = "",
    refusal: str = "",
) -> CommandStep:
    """**P4**, replacing `chattr +a` and `chattr +i`.

    `chattr` resolves the pathname itself, inside a tool this design does not
    own, so the flag landed on whatever the name meant at that instant. Here the
    entry is opened relative to the held parent descriptor, its identity is
    compared with the one the creating step recorded, and
    `ioctl(FS_IOC_SETFLAGS)` is issued **on that descriptor** — so a replacement
    of the name after the check cannot receive the flag.
    """
    directory_role, name = _component(path)
    letter = "a" if flag == "append_only" else "i"
    return CommandStep(
        step_id=step_id,
        band=band,
        run_as="root",
        argv=(),
        effect=DescriptorEffect(
            kind=EffectKind.SET_FLAG,
            directory_role=directory_role,
            name=name,
            path=path,
            flags=(flag,),
        ),
        purpose=why or f"Set the {flag} inode flag on {path}, as §2.13.3 specifies.",
        mutation_ids=(f"file_attribute:{path}",),
        expected_result=(
            f"the flag is set on the inode the descriptor holds; `lsattr` "
            f"reports `{letter}` on {path}."
        ),
        expected_refusal=refusal
        or (
            "a missing creating-step record, an absent object or an identity "
            "that is not the recorded one refuses before the ioctl, and an "
            "unestablished quiescence refuses the effect and every dependent "
            "one."
        ),
    )


def _create_empty_file(
    step_id: str, band: str, path: str, mode: str, owner: str, group: str, why: str
) -> CommandStep:
    """One reviewed empty subject, created exclusively on a held descriptor.

    Replaces `install --mode … /dev/null <path>`: `O_CREAT|O_EXCL|O_NOFOLLOW`
    proves the name was free, `fchown`/`fchmod` land on the descriptor rather
    than on a name resolved again, and the creating step records the identity a
    later flag or removal pre-check compares against.
    """
    directory_role, name = _component(path)
    return CommandStep(
        step_id=step_id,
        band=band,
        run_as="root",
        argv=(),
        effect=DescriptorEffect(
            kind=EffectKind.CREATE_OBJECT,
            directory_role=directory_role,
            name=name,
            path=path,
            mode=int(mode, 8),
            owner=owner,
            group=group,
        ),
        purpose=why,
        mutation_ids=(f"file:{path}",),
        expected_result=(
            f"{path} exists, empty, as {owner}:{group} {mode}, created "
            "exclusively and synchronized with its containing entry."
        ),
        expected_refusal=(
            "`EEXIST` refuses: something is already at that name and this run "
            "did not put it there."
        ),
    )


def _create_disposable_root(
    steps: _Steps,
    target: DisposableTarget,
    paths: _Paths,
    mutations: Sequence[Mutation],
    next_id,
) -> None:
    """Conflict **C-8**: the disposable root, created exclusively — R16.

    ## What R14 could not do, and why a probe was the wrong shape

    R13 proved the root absent with `stat --format=%F` exiting 1 and made that
    one observation the ownership of every path under it. Coreutils gives every
    failure the same 1 — `ENOENT`, `ENOTDIR`, `ELOOP`, `ENAMETOOLONG`, `EACCES`
    and `EIO` are one number — so a directory that existed on a filesystem
    returning `EIO` satisfied the baseline and cleanup's `rmdir` was entitled to
    it. R14 conceded that and **blocked** the baseline: the 29 path mutations
    were owned by nothing, the executor refused the first `install`, and this
    plan created no file at all.

    Repairing it as a *better probe* was never available. `stat`, `lsattr`,
    `getcap` and `namei` report absence only as a generic failure or as message
    text this harness does not parse, and no permitted creation reports
    pre-existence the way `groupadd` and `useradd` report exit 9: `install -d`
    succeeds on a directory that is already there and `install` overwrites a file
    that is. And a probe is the wrong shape regardless — between *"it was not
    there"* and *"create it"* there is a window in which it can arrive.

    ## The mechanism the maintainer approved on 2026-09-09

    **`mkdir(2)`, and the successful creation is the ownership.** There is no
    preliminary absence check, so there is no window. `mkdir(2)` reports a path
    that is already occupied as **`EEXIST`**, uniquely and documentedly, and it
    reports it for a directory, a regular file, a symbolic link and a **dangling**
    symbolic link alike — which is the whole of what R14 said the filesystem did
    not have.

    | Outcome | Exit | What it establishes |
    |---|---|---|
    | the call returned | `0` | **ownership.** This call created this directory, and `created=yes` with the device and inode it read back are the evidence |
    | something is already at the path | `15` (`EEXIST`) | nothing. The run stops, ownership is *withdrawn* rather than merely unclaimed, and **no path under the root is removed** |
    | the parent does not resolve to a directory | `16`/`1` (`ENOENT`, `ENOTDIR`) | nothing. Unexpected parent resolution stops the run |
    | any other refusal | `10`–`14`, `1` | nothing. `EACCES`, `EROFS`, `ELOOP`, `EIO` — none of them is *absent* and none of them is a creation |
    | it was created and could not be identified | `66` | **residue.** `mkdir` returned and the `open`/`fstat` did not; a directory exists and this run cannot say which one, so it is reported and never removed |
    | it was interrupted, timed out, or never reported | — | the same as `66`, by `nothing_created_statuses` not admitting them |

    ## The bootstrap location, because the dependency is real

    A helper that creates the disposable root cannot first be installed inside
    that root, and installing it anywhere else would create a second host object
    whose own pre-existence nobody proved — the same problem one directory up.

    So the creation runs **the reviewed source in the repository tree**:
    `case_runtime.CASE_PROGRAM_SOURCE_PATH`, executed by the same named
    interpreter with the same two isolation flags. That file is not a host object
    this run creates, modifies or removes; its lifecycle is the repository's, it
    is already covered by the review manifest, and `install` later copies those
    exact bytes to `<root>/bin/case` — so one digest covers both copies and the
    program that creates the root is the program that runs the experiments.
    `case_runtime.BOOTSTRAP_VERBS` confines the bootstrap copy to `mkroot` and
    `statroot`, and confines the installed copy out of both.

    ## What the ownership reaches, and the one inference this rests on

    `mkdir(2)` returns a directory containing nothing but `.` and `..`. At the
    instant this step is satisfied there is therefore no object under that path
    for a later step to overwrite, and no object this run could later delete that
    it did not itself put there. Ownership of the container is ownership of what
    the plan declares inside it, and `establishes_ownership_of_contained`
    enumerates exactly that set so a reviewer approves it and the manifest pins
    it. **That inference is stated rather than assumed**: it is the one step in
    C-8's argument that is not a direct observation, and it is sound precisely
    because the container was created empty by this run rather than found.

    The two PostgreSQL configuration files stay outside it, as they always have:
    they are `postgres_config_line` mutations whose reversal is a **restore** of
    a byte-exact pre-change capture, not a removal, and `_contained_mutation_ids`
    refuses any other path that is neither the root nor inside it.

    ## Cleanup, and what a replaced path does not inherit

    `CL-37` re-reads the root's device and inode through the same bootstrap copy
    immediately before `CL-38`'s `rmdir`, and the executor compares the two
    readings. A path whose object was replaced after this run created it does not
    inherit permission to have its replacement deleted: the comparison fails, the
    removal is skipped, and the path is reported as residue for §2.13.2b's
    operator recovery. The byte-exact configuration captures are retained until
    the restore, the reload and both post-reload observations have succeeded,
    exactly as R13's EH-R13-2 requires — and the capture directory sits inside
    this root, so it is retained by the same rule whether or not the root is
    removable.

    ## The mode

    `mkdir(2)` is given `0700` and `fchmod(2)` applies it again to the descriptor
    of the directory just created, so the process umask does not decide it and no
    path is resolved a second time. Owner and group are `root:root` by
    construction: `mkdir` takes the creating process's uid and gid, and this
    vector runs as `E7`. `B3-02` reads all four back with `stat` rather than
    assuming them.

    **`0700`, not `0755` — C-P5.0-LAB-I3-R3, 2026-09-20.** The mode is
    `case_program.ROOT_DIRECTORY_MODE`, and it is the value r6 §1.4.1's C1 row
    and §7.2's derivation always gave canonical `R`. This root holds
    security-sensitive execution evidence and nothing traverses it but the one
    root identity that created it; every object beneath it is reached by an
    inherited descriptor, so no group or other bit has a consumer. `R/bin`
    remains `0755`, which is a separate item below.
    """
    contained = tuple(
        mutation_id
        for mutation_id in _contained_mutation_ids(mutations, paths.root)
        if mutation_id != f"directory:{paths.root}"
    )
    argv = build_bootstrap_vector(target, "mkroot", target.root_path)
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="identity",
            run_as="root",
            argv=argv,
            purpose=(
                "Create the disposable root **exclusively**, through the reviewed "
                "case program's bootstrap copy — conflict C-8. `mkdir(2)` "
                "returns or reports EEXIST, so the successful creation is itself "
                "the proof that nothing was there, with no preliminary absence "
                "check and therefore no window between the observation and the "
                "creation. The bootstrap copy is the reviewed source in the "
                "repository tree, because a helper that creates this root cannot "
                "first be installed inside it."
            ),
            evidence_case_ids=("ROOT-EXCLUSIVE-CREATION",),
            mutation_ids=(f"directory:{paths.root}",),
            # **STANDALONE, not PREREQUISITE.** A prerequisite is asserted
            # *before anything is constructed*, and this step is the
            # construction: it is interpreted on its own observation, which is
            # `mkdir(2)` having returned. Its failure stops the run either way —
            # the executor stops on the first unsatisfied step whatever its role
            # — and calling it a prerequisite would put a mutation among the
            # steps `test_concrete_plan` requires to precede every mutation.
            role=StepRole.STANDALONE,
            capture=CapturePolicy.CASE_RESULT,
            observation_expectations=_case_result_for(
                argv, (0,), known={"created": "yes"}
            ),
            satisfying_statuses=(0,),
            preexisting_statuses=(ROOT_PREEXISTING_STATUS,),
            nothing_created_statuses=ROOT_NOTHING_CREATED_STATUSES,
            establishes_ownership_by_creation=(f"directory:{paths.root}",),
            establishes_ownership_of_contained=contained,
            expected_result=(
                f"exit 0; result=returned, created=yes, and the device and inode "
                f"of the directory this call made. **That is the ownership** — of "
                f"{paths.root} and, because mkdir returns an empty directory, of "
                f"the {len(contained)} declared mutations inside it. The two "
                "numbers are recorded rather than compared, because the kernel "
                "allocates them; cleanup compares them with the reading it takes "
                "immediately before the one rmdir that would remove the root."
            ),
            expected_refusal=(
                "exit 15 is EEXIST — a directory, a file, a symbolic link or a "
                "dangling symbolic link is already at that path. The run stops "
                "before any other mutation, ownership is withdrawn, and nothing "
                "under the root is removed: §2.13.2b's operator recovery clears "
                "a previous run's residue and this harness does not. Exit 16 or "
                "1 is a parent that does not resolve to a directory, and 10-14 "
                "are the other refusals; none of them is absence and none "
                "establishes anything. **Exit 66 is the uncertain case** — mkdir "
                "returned and the identity could not be read — and it is not a "
                "refusal: a directory may exist, so the path is reported as "
                "bounded residue with the operator recovery and is never "
                "deleted. An interruption, a timeout and a launch that never "
                "reported are the same, because they are outside "
                "nothing_created_statuses."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="identity",
            run_as="root",
            argv=("/usr/bin/stat", "--format=%u %g %a %F", paths.root),
            purpose=(
                "Read the created root's owner, group, mode and type back rather "
                "than assuming mkdir and fchmod produced them. mkdir takes the "
                "creating process's uid and gid, and this vector runs as E7, so "
                "root:root is a consequence rather than an option — and a "
                "consequence is still read back."
            ),
            evidence_case_ids=("ROOT-EXCLUSIVE-CREATION",),
            role=StepRole.CONTROL,
            capture=CapturePolicy.FILE_MODE,
            observation_expectations=_file_mode_expected(
                uid="0", gid="0", mode=_stat_mode("0700"), file_type="directory"
            ),
            expected_result=(
                "uid 0, gid 0, mode 700, type directory — all four compared."
            ),
            expected_refusal=(
                "any disagreement stops the run. A root that is not the object "
                "this plan describes is not a root the rest of the band may "
                "build inside."
            ),
        )
    )


def _band_3(
    steps: _Steps,
    target: DisposableTarget,
    paths: _Paths,
    mutations: Sequence[Mutation],
) -> None:
    order = 0

    def next_id() -> str:
        nonlocal order
        order += 1
        return f"B3-{order:02d}"

    _create_disposable_root(steps, target, paths, mutations, next_id)

    for path, mode, owner, group, why in (
        (paths.journal, "0750", "root", JOURNAL_GROUP, "§2.13.3's journal directory."),
        (paths.archive, "0750", "root", COORD, "§2.13.3's archive directory."),
        (paths.before, "0700", "root", "root", "Where the pre-change captures live."),
        (paths.bin, "0755", "root", "root", "Where the Band-5 case binary would live."),
    ):
        steps.add(_create_directory(next_id(), "identity", path, mode, owner, group, why))

    # ---- conflict C-2: the reviewed case program, installed and asserted -----
    #
    # `install` copies bytes; it does not generate them. The source is the exact
    # repository file the review manifest covers, so **the installed bytes are
    # the reviewed source bytes** and the manifest's digest for
    # `tools/phase_5_0_evidence/execution/case_program.py` is simultaneously the
    # source digest and the installation digest. No compiler runs, nothing is
    # downloaded, and no opaque binary exists anywhere in this plan.
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="identity",
            run_as="root",
            argv=(),
            effect=DescriptorEffect(
                kind=EffectKind.INSTALL_PAYLOAD,
                directory_role="bin",
                name="case",
                path=paths.case_binary,
                mode=int(CASE_PROGRAM_MODE, 8),
                owner=CASE_PROGRAM_OWNER,
                group=CASE_PROGRAM_GROUP,
                payload_source=CASE_PROGRAM_SOURCE,
            ),
            purpose=(
                "**P2.** Install the reviewed case program from one held "
                f"buffer. The bytes are {CASE_PROGRAM_SOURCE}'s, which the "
                "review manifest covers, and they are digested against the "
                "manifest's value at the last possible moment — so the "
                "installed bytes are the reviewed bytes, and no second read of "
                "any pathname happens between the check and the write. "
                "`install` was removed here: it re-resolved the destination for "
                "each of its own effects and succeeded whether or not something "
                "was already at the name."
            ),
            mutation_ids=(f"file:{paths.case_binary}",),
            expected_result=(
                f"{paths.case_binary} exists as "
                f"{CASE_PROGRAM_OWNER}:{CASE_PROGRAM_GROUP} {CASE_PROGRAM_MODE}, "
                "byte-identical to the reviewed source, published exclusively "
                "and synchronized with its containing entry."
            ),
            expected_refusal=(
                "content whose digest is not the manifest's is refused rather "
                "than installed, and an occupied final name is `EEXIST`."
            ),
        )
    )
    _case_program_prerequisites(steps, paths)

    for path, mode, owner, group, why in (
        (paths.journal_file, "0640", WRITER, COORD, "The disposable journal file."),
        (paths.journal_seal, "0440", "root", JOURNAL_GROUP, "The disposable seal."),
        (paths.archive_journal, "0440", "root", COORD, "The disposable archived journal."),
        (paths.archive_seal, "0440", "root", COORD, "The disposable archived seal."),
        (paths.archive_close, "0440", "root", COORD, "The disposable .close manifest."),
    ):
        steps.add(_create_empty_file(next_id(), "identity", path, mode, owner, group, why))

    # ---- conflict C-3: §2.13.3's current-generation link --------------------
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="identity",
            run_as="root",
            argv=build_case_vector(
                target, "symlink", paths.journal_current, GENERATION_LINK_NAME
            ),
            purpose=(
                "Create §2.13.3's `…/journal/current` through the reviewed case "
                "program's `symlink` verb. The link path is absolute and inside "
                "the disposable root; the target is the one reviewed relative "
                f"generation name {GENERATION_LINK_NAME!r}. No `ln` and no other "
                "general filesystem executable is admitted to obtain it."
            ),
            mutation_ids=(f"file:{paths.journal_current}",),
            expected_result=(
                f"exit 0; {paths.journal_current} is a symbolic link to "
                f"{GENERATION_LINK_NAME}."
            ),
            expected_refusal=(
                "an absolute target, a `..` segment, a separator or any other "
                "generation name is refused before the process is created and "
                "again by the case program."
            ),
        )
    )

    for path, flag, case in (
        (paths.journal_file, "append_only", "JNL-52-APPEND"),
        (paths.journal_seal, "immutable", "JNL-52-IMMUTABLE"),
        (paths.archive_journal, "immutable", "JNL-52-ARCHIVE-IMMUTABLE"),
        (paths.archive_seal, "immutable", "JNL-52-ARCHIVE-IMMUTABLE"),
        (paths.archive_close, "immutable", "JNL-52-ARCHIVE-IMMUTABLE"),
    ):
        steps.add(_set_flag(next_id(), "identity", path, flag))

    steps.add(
        CommandStep(
            step_id=next_id(),
            band="identity",
            run_as="root",
            argv=("/usr/bin/lsattr", "--", paths.journal_file),
            purpose="Read the append attribute back rather than assuming chattr set it.",
            evidence_case_ids=("JNL-52-APPEND-CONFIRMED",),
            role=StepRole.CONTROL,
            capture=CapturePolicy.ATTRIBUTE_FLAGS,
            observation_expectations=_attribute_flags_expected(
                append_only=True, immutable=False
            ),
            expected_result="append_only=yes and immutable=no, both compared.",
            expected_refusal=(
                "an absent append flag makes every Stage-2 case inconclusive, and "
                "it now does so by making **this step** unsatisfied rather than by "
                "being recorded and read later — EH-R13-3."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="identity",
            run_as="root",
            argv=("/usr/bin/lsattr", "--", paths.journal_seal),
            purpose="Read the immutable attribute back.",
            evidence_case_ids=("JNL-52-IMMUTABLE-CONFIRMED",),
            role=StepRole.CONTROL,
            capture=CapturePolicy.ATTRIBUTE_FLAGS,
            observation_expectations=_attribute_flags_expected(
                append_only=False, immutable=True
            ),
            expected_result="immutable=yes and append_only=no, both compared.",
            expected_refusal=(
                "an absent immutable flag makes the seal cases inconclusive, and "
                "it now does so by making **this step** unsatisfied — EH-R13-3."
            ),
        )
    )

    # The two positive traverse controls, and only them. Cases 1-8's open(2)
    # calls with specific flags are conflict C-2.
    for identity, case_id in (("discordbot", "JNL-52-CASE-5"), ("freedomweb", "JNL-52-CASE-7")):
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="identity",
                run_as=identity,
                argv=("/usr/bin/namei", "-l", paths.root),
                purpose=(
                    f"The positive traverse control for {identity}. Cases 6 and 8 "
                    "are not interpreted without it, because a denial whose cause "
                    "could be a path search is not evidence of a permission."
                ),
                evidence_case_ids=(case_id,),
                role=StepRole.CONTROL,
                expected_result="the traverse succeeds — this is the control.",
                expected_refusal=(
                    "a failure here makes the matching denial case inconclusive "
                    "rather than a pass."
                ),
            )
        )

    _access_matrix(steps, target, paths, next_id)


def _case_program_prerequisites(steps: _Steps, paths: _Paths) -> None:
    """`P-03`, `P-04` and `P-05`, generated where their subject exists.

    R10 §R10.7 flagged `P-03`/`P-04`'s position as inherited rather than ruled:
    the reviewed design lists them among the Band-1 prerequisites *"asserted
    before anything is constructed"*, and their subject is a file Band 3 creates.
    Resolving conflict C-2 settles it. They are generated **immediately after the
    install that creates the case program and before any step that runs it**,
    which is the earliest point at which each can hold and the latest at which it
    is still a prerequisite. Their ids, their band and what they assert are
    unchanged.

    `P-05` is new in R12, and it is the interpreter preflight R11 requires: it
    runs the case program through the complete Option-B vector, so a run that
    reaches any dependent case has already established the interpreter's path,
    version, executable digest and effective isolation — by running exactly the
    vector every later case runs.

    `P-06` is new in R13, and it is here for the same reason `P-03`, `P-04` and
    `P-05` are: its subject is a process the case program has to exist to
    produce. It observes **`E7`**, the harness's own root identity, and it is the
    **first** step in this plan that runs the case program, so every case-program
    operation this plan attributes to `E7` is downstream of it. That is
    EH-R12-1's ordering requirement, and `_validate_root_identity_ordering()`
    asserts it over the generated plan rather than leaving it to this comment.
    """
    steps.add(
        CommandStep(
            step_id="P-03",
            band="capability",
            run_as="root",
            argv=("/usr/bin/getcap", paths.case_binary),
            purpose=(
                "Prove the installed case program carries no file capability. "
                "The execve derivation in §2.13.5c step 7 assumes an empty "
                "F_P/F_I/F_E. It is asserted here, immediately after the install "
                "that creates its subject and before any step that runs it — the "
                "ordering R10 §R10.7 left unresolved and conflict C-2's "
                "resolution settles."
            ),
            evidence_case_ids=("CAP-CASE-BINARY-FILECAPS",),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.FILE_CAPABILITIES,
            observation_expectations=_no_file_capability_expected(),
            expected_result=(
                "no output — no file capability is set, and the recorded "
                "file_capability_present=no is compared before the step may be "
                "satisfied (EH-R13-3)."
            ),
            expected_refusal="any capability reported stops the band.",
        )
    )
    steps.add(
        CommandStep(
            step_id="P-04",
            band="capability",
            run_as="root",
            argv=("/usr/bin/stat", "--format=%u %g %a %F", paths.case_binary),
            purpose=(
                "Prove the installed case program is "
                f"{CASE_PROGRAM_OWNER}:{CASE_PROGRAM_GROUP} {CASE_PROGRAM_MODE} "
                "and not set-user-ID."
            ),
            evidence_case_ids=("CAP-CASE-BINARY-MODE",),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.FILE_MODE,
            observation_expectations=_file_mode_expected(
                uid="0",
                gid="0",
                mode=_stat_mode(CASE_PROGRAM_MODE),
                file_type="regular file",
            ),
            expected_result=(
                f"0 0 {_stat_mode(CASE_PROGRAM_MODE)} regular file — all four compared before "
                "the step may be satisfied (EH-R13-3)."
            ),
            expected_refusal="a set-user-ID bit or a non-root owner stops the band.",
        )
    )
    steps.add(
        CommandStep(
            step_id="P-05",
            band="capability",
            run_as="root",
            argv=build_case_vector(APPROVED_TARGET, "runtime"),
            purpose=(
                "The interpreter preflight — conflict C-2's Option-B boundary, "
                "asserted by running the reviewed vector itself. It records the "
                "interpreter's absolute path, its resolved path, its major/minor "
                f"version, the SHA-256 of its executable bytes, whether `-I` and "
                "`-S` are actually in effect, whether any third-party "
                "distribution is importable, and the installed case program's "
                "own digest."
            ),
            evidence_case_ids=("CASE-RUNTIME-PREFLIGHT",),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.CASE_RUNTIME,
            expected_result=(
                f"exit 0; verb=runtime, result=returned, interpreter "
                f"{INTERPRETER_PATH}, interpreter_real equal to the reviewed "
                "target fact `case_runtime.EXPECTED_INTERPRETER_REAL_PATH`, "
                f"python_version {INTERPRETER_PYTHON_VERSION}, interpreter_sha256 "
                "equal to the reviewed target fact "
                "`case_runtime.EXPECTED_INTERPRETER_SHA256`, isolated=yes, "
                "no_site=yes, third_party_importable=no, case_program equal to "
                "the installed path this plan names, and case_program_sha256 "
                "equal to the review manifest's covered-source digest for "
                f"{CASE_PROGRAM_SOURCE}. **All eleven are compared before this "
                "step may be satisfied**, and exit 0 alone does not satisfy it."
            ),
            expected_refusal=(
                "a missing, duplicated, unreadable or unequal value for any of "
                "the eleven keys makes this prerequisite unsatisfied, stops the "
                "run before any dependent case, and makes every dependent case "
                "INCONCLUSIVE. Both interpreter facts are reviewed target facts "
                "supplied from outside; neither is ever learned from this run, "
                "and the expected case-program digest comes from the review "
                "manifest's covered source rather than from the installed file or "
                "from this observation. **The digest covers the interpreter "
                "executable's own bytes only** — not the operating system, the "
                "dynamic loader, the shared libraries or the standard library, "
                "which are disposable-host prerequisites exactly as they are for "
                "every other distribution executable this plan names."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id="P-06",
            band="capability",
            run_as="root",
            argv=build_case_vector(APPROVED_TARGET, "identity"),
            purpose=(
                "§2.13.5c's **E7**, observed rather than assumed — R13's "
                "disposition of EH-R12-1. E7 is the harness's own root identity, "
                "constructed by not dropping: there is no `capsh`, no securebit "
                "set, no drop, no `--uid=` and no `--groups=`. It is therefore "
                "run as the **direct** Option-B vector, and the `identity` verb "
                "executes in the final interpreted process after `execve`, "
                "reading the five masks and `NoNewPrivs` from "
                "/proc/self/status and the final securebits from "
                "prctl(PR_GET_SECUREBITS) — the same code path, in the same kind "
                "of process, as the seven constructed identities. It is a "
                "prerequisite because every later operation this plan attributes "
                "to E7 depends on E7 being what §2.13.5c says it is."
            ),
            evidence_case_ids=("CAP-E7-IDENTITY", "CAP-E7-ENVIRONMENT"),
            role=StepRole.PREREQUISITE,
            capture=CapturePolicy.CASE_IDENTITY,
            identity_name="E7",
            # No `bindings`: E7 assumes nobody, so there is no symbolic account
            # or group in this vector for the executor to substitute, and
            # `CommandStep` refuses an E7 step that declares one.
            expected_result=(
                "exit 0; verb=identity, result=returned, and the effective uid, "
                "effective gid, complete supplementary gid **set**, cap_inh, "
                "cap_prm, cap_eff, cap_bnd, cap_amb, no_new_privs and final "
                "securebits each equal to the reviewed target fact stated for it "
                "in `capability.E7_TARGET_FACTS`. **All twelve are compared "
                "before this step may be satisfied**, and exit 0 alone does not "
                "satisfy it."
            ),
            expected_refusal=(
                "a missing, duplicated, unreadable, malformed, unexpected or "
                "unequal value for any of the twelve makes this prerequisite "
                "unsatisfied, stops the run here, and makes every operation this "
                "plan attributes to E7 INCONCLUSIVE — none of them is executed "
                "and none is interpreted. Every expected value is a **reviewed "
                "target fact** about the host, supplied from outside and verified "
                "by an independent reviewer: none is derived from `M` (E7 has "
                "no `M`), none is read from the bound vector (E7 has no bound "
                "vector), and none is learned from P-01, P-02, this observation, "
                "/proc, id or capsh. While any of them is unconfirmed the "
                "executor refuses before it starts any command. **P-01 and P-02 "
                "are retained and unchanged**: they read the launcher's bounding "
                "set and expand the documented §8.1 H-6 mask, which is separate "
                "preflight evidence and is not this observation."
            ),
        )
    )


#: The two `open(2)` refusals the negative `JNL-52` cases may be satisfied by.
#:
#: §5.2 states case 2's `open(seal, O_WRONLY)` as `EPERM` and case 4's — the same
#: operation on the same immutable inode, as a different identity — as `EACCES`.
#: On Linux `inode_permission()` checks `IS_IMMUTABLE` **before** the
#: discretionary check, so both would be `EPERM`; the two sentences cannot both
#: be right. That is a package-plan inconsistency and not this generator's to
#: rule on, so every negative access case is satisfied by **either** refusal and
#: the exact errno is recorded for the classifier. Neither exit 0 nor the case
#: program's own vector refusal satisfies one.
_ACCESS_DENIAL_STATUSES = refused_with("EPERM", "EACCES")


def _access_case(
    step_id: str,
    *,
    run_as: str,
    argv: tuple[str, ...],
    purpose: str,
    case_id: str,
    permitted: bool,
    role: StepRole = StepRole.STANDALONE,
) -> CommandStep:
    """One `JNL-52` access assertion, as a case-program vector.

    `permitted` decides the satisfaction rule rather than a caller writing exit
    statuses out: a positive case is satisfied by exit 0 and by nothing else, and
    a negative case by one of the two refusal codes above.
    """
    return CommandStep(
        step_id=step_id,
        band="identity",
        run_as=run_as,
        argv=argv,
        purpose=purpose,
        evidence_case_ids=(case_id,),
        role=role,
        capture=CapturePolicy.CASE_RESULT,
        # **EH-R13-3.** Derived from this step's own verb and satisfying
        # statuses, so the exit status and the observation cannot say different
        # things about what the boundary under test did.
        observation_expectations=_case_result_for(
            argv, (0,) if permitted else _ACCESS_DENIAL_STATUSES
        ),
        satisfying_statuses=(0,) if permitted else _ACCESS_DENIAL_STATUSES,
        expected_result=(
            "exit 0 — the operation returned, and result=returned is recorded."
            if permitted
            else ""
        ),
        expected_refusal=(
            ""
            if permitted
            else "the operation is refused, and the exact errno is recorded. The "
            "satisfying statuses are the case program's EPERM and EACCES codes, "
            "so a vector the program itself refused (64) does not stand in for a "
            "denial by the boundary under test."
        ),
    )


def _access_matrix(
    steps: _Steps, target: DisposableTarget, paths: _Paths, next_id
) -> None:
    """§5.2's `JNL-52` cases 1, 2, 3, 4, 6 and 8 — conflict **C-2** resolved.

    Cases 5 and 7 are the `namei -l` traverse controls generated above; these six
    are the `open(2)` evidence the design states, each run **as** the named
    identity through the process boundary's credential contract and each
    recording the exact errno.

    The negative cases assert a **create** rather than an unlink or a rename.
    All three are refusals the design admits, and only the create leaves nothing
    behind when it is wrongly permitted — an unexpected file in `…/journal` makes
    the derived non-recursive `rmdir` fail and is reported as residue, whereas an
    unexpected unlink would have destroyed a declared object before anyone read
    the result. It is a narrowing, and it is stated rather than assumed.
    """

    def vector(verb: str, *arguments: str) -> tuple[str, ...]:
        return build_case_vector(target, verb, *arguments)

    # (1) freedomsheet, positive.
    steps.add(
        _access_case(
            next_id(),
            run_as=WRITER,
            argv=vector("open", "rdonly", paths.journal_seal),
            purpose=(
                "JNL-52 case 1: freedomsheet reads the seal. Its freedomjournal "
                "membership is what permits it, and §2.12.2 claim 1 is that the "
                "membership grants exactly this and no write."
            ),
            case_id="JNL-52-CASE-1",
            permitted=True,
        )
    )
    steps.add(
        _access_case(
            next_id(),
            run_as=WRITER,
            argv=vector("open", "rdonly", paths.journal_file),
            purpose="JNL-52 case 1: freedomsheet reads the journal it owns.",
            case_id="JNL-52-CASE-1",
            permitted=True,
        )
    )
    # (2) freedomsheet, negative.
    steps.add(
        _access_case(
            next_id(),
            run_as=WRITER,
            argv=vector("open", "wronly", paths.journal_seal),
            purpose=(
                "JNL-52 case 2: freedomsheet must not open the seal for writing. "
                "The inode is chattr +i, so the kernel refuses in "
                "inode_permission() before the discretionary check."
            ),
            case_id="JNL-52-CASE-2",
            permitted=False,
        )
    )
    steps.add(
        _access_case(
            next_id(),
            run_as=WRITER,
            argv=vector(
                "open", "create-excl", paths.denial_probe(paths.journal, WRITER)
            ),
            purpose=(
                "JNL-52 case 2: freedomsheet must not create inside …/journal. "
                "The directory is root:freedomjournal 0750 — r-x for the group "
                "and no write bit, which is §2.12.2 claim 1."
            ),
            case_id="JNL-52-CASE-2",
            permitted=False,
        )
    )
    steps.add(
        _access_case(
            next_id(),
            run_as=WRITER,
            argv=vector("open", "rdonly", paths.archive_journal),
            purpose=(
                "JNL-52 case 2: freedomsheet must not reach …/archive at all. It "
                "holds no freedomcoord membership, and the directory is "
                "root:freedomcoord 0750."
            ),
            case_id="JNL-52-CASE-2",
            permitted=False,
        )
    )
    # (3) freedomcoord, positive.
    for path, what in (
        (paths.journal_seal, "the seal"),
        (paths.journal_file, "the journal"),
        (paths.archive_journal, "an archived journal"),
    ):
        steps.add(
            _access_case(
                next_id(),
                run_as=COORD,
                argv=vector("open", "rdonly", path),
                purpose=(
                    f"JNL-52 case 3: freedomcoord reads {what}. This is evidence "
                    "identity E8's access, and §2.12.2 states the memberships "
                    "that permit it."
                ),
                case_id="JNL-52-CASE-3",
                permitted=True,
            )
        )
    # (4) freedomcoord, negative — the coordinator holds no write bit anywhere.
    for argv_, why in (
        (
            vector("open", "wronly", paths.journal_seal),
            "must not open the seal for writing",
        ),
        (
            vector("open", "wronly-append", paths.journal_file),
            "must not open the journal for appending; the file's group bits are r--",
        ),
        (
            vector("open", "create-excl", paths.denial_probe(paths.journal, COORD)),
            "must not create inside …/journal",
        ),
        (
            vector("open", "create-excl", paths.denial_probe(paths.archive, COORD)),
            "must not create inside …/archive",
        ),
    ):
        steps.add(
            _access_case(
                next_id(),
                run_as=COORD,
                argv=argv_,
                purpose=(
                    f"JNL-52 case 4: freedomcoord {why}. §2.12.2 claim 2 is that "
                    "the coordinator holds no write bit anywhere in the hierarchy."
                ),
                case_id="JNL-52-CASE-4",
                permitted=False,
            )
        )
    # (6) and (8) — the two identities whose denials the namei controls above
    # make attributable. Both are DEPENDENT: a denial beside a traverse control
    # that did not pass is consistent with a path search and isolates nothing.
    for identity, case_id in (("discordbot", "JNL-52-CASE-6"), ("freedomweb", "JNL-52-CASE-8")):
        for path, what in (
            (paths.journal_seal, "the seal"),
            (paths.archive_journal, "an archived journal"),
        ):
            steps.add(
                _access_case(
                    next_id(),
                    run_as=identity,
                    argv=vector("open", "rdonly", path),
                    purpose=(
                        f"{case_id}: {identity} must not read {what}. It holds no "
                        "freedomjournal and no freedomcoord membership, and the "
                        f"matching traverse control has already proved the parent "
                        "reachable — so this denial is attributable to the "
                        "directory's mode rather than to a path search."
                    ),
                    case_id=case_id,
                    permitted=False,
                    role=StepRole.DEPENDENT,
                )
            )


def _band_4(steps: _Steps, target: DisposableTarget, paths: _Paths) -> None:
    order = 0

    def next_id() -> str:
        nonlocal order
        order += 1
        return f"B4-{order:02d}"

    for path, why in (
        (paths.probe, "§2.13.2a's probe arena."),
        (paths.probe_ro, "Stage 4's negative target, outside the substituted ReadWritePaths=."),
    ):
        steps.add(_create_directory(next_id(), "filesystem", path, "0770", "root", WRITER, why))

    for path, why in (
        (paths.stage1, "The Stage-1 probe file, deliberately carrying no append attribute."),
        (paths.stage2, "The Stage-2 probe file, the one FS_APPEND_FL is set on."),
        (paths.s4_1_target, "Stage 4's writable target, inside the substituted ReadWritePaths=."),
        (paths.s4_unlink, "Stage 4's outside-the-unit control target."),
        (paths.s4_target, "Stage 4's inside-the-unit denial target."),
    ):
        steps.add(_create_empty_file(next_id(), "filesystem", path, "0660", WRITER, WRITER, why))

    steps.add(
        _set_flag(
            next_id(),
            "filesystem",
            paths.stage2,
            "append_only",
            why="Set FS_APPEND_FL on the Stage-2 target — the flag Stage 2 is about.",
            refusal=(
                "EOPNOTSUPP means the filesystem has no flag interface and A-5.0-5 "
                "is unconfirmable on it; the probe is failed, not inconclusive."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="filesystem",
            run_as="root",
            argv=("/usr/bin/lsattr", "--", paths.stage2),
            purpose="Read FS_APPEND_FL back before any Stage-2 case is interpreted.",
            evidence_case_ids=("P-9",),
            role=StepRole.CONTROL,
            capture=CapturePolicy.ATTRIBUTE_FLAGS,
            observation_expectations=_attribute_flags_expected(
                append_only=True, immutable=False
            ),
            expected_result="append_only=yes and immutable=no, both compared.",
            expected_refusal=(
                "an absent append flag makes this control unsatisfied and stops "
                "the run before any Stage-2 case — EH-R13-3."
            ),
        )
    )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="filesystem",
            run_as="root",
            argv=(
                "/usr/bin/findmnt",
                "--noheadings",
                "--output",
                "FSTYPE,SOURCE,OPTIONS",
                "--target",
                paths.root,
            ),
            purpose=(
                "Stage 3: the mount the evidence is taken on. §2.13.1 defect 1 is "
                "exactly an append-only result inferred from a different filesystem."
            ),
            evidence_case_ids=("M-1",),
            role=StepRole.CONTROL,
            capture=CapturePolicy.MOUNT_FACTS,
            observation_expectations=_mount_facts_expected(),
            expected_result=(
                f"{APPROVED_TARGET_FACTS.filesystem_type} on "
                f"{APPROVED_TARGET_FACTS.filesystem_device}, block-backed, not "
                "tmpfs, not ro — **all three compared against the confirmed "
                "target facts before this control may be satisfied** (EH-R13-3)."
            ),
            expected_refusal=(
                "a tmpfs, a different device or a read-only mount makes this "
                "control unsatisfied and stops the run, so every attribute case "
                "is inconclusive rather than interpreted beside a control nobody "
                "checked."
            ),
        )
    )

    steps.add(
        CommandStep(
            step_id=next_id(),
            band="filesystem",
            run_as="root",
            argv=build_case_vector(target, "statvfs", paths.journal),
            purpose=(
                "Stage 3's M-2: statvfs on …/journal, asserting ST_RDONLY clear. "
                "`findmnt` above answers the mount half of Stage 3; this answers "
                "ST_RDONLY as the case states it, which is a syscall and not an "
                "option string."
            ),
            evidence_case_ids=("M-2",),
            role=StepRole.CONTROL,
            capture=CapturePolicy.CASE_RESULT,
            observation_expectations=_case_result_for(
                build_case_vector(target, "statvfs", paths.journal),
                (0,),
                known={"st_rdonly": "0"},
            ),
            expected_result=(
                "exit 0 with st_rdonly=0, **compared** before this control may be "
                "satisfied — EH-R13-3."
            ),
            expected_refusal=(
                "st_rdonly=1 makes every attribute case inconclusive: an EPERM "
                "taken on a read-only filesystem attributes nothing to "
                "FS_APPEND_FL."
            ),
        )
    )

    _stage_one(steps, target, paths, next_id)
    _stage_two(steps, target, paths, next_id)
    _stage_four(steps, target, paths, next_id)


def _probe_case(
    step_id: str,
    *,
    run_as: str,
    argv: tuple[str, ...],
    purpose: str,
    case_id: str,
    satisfying_statuses: tuple[int, ...],
    expected_result: str = "",
    expected_refusal: str = "",
    role: StepRole = StepRole.STANDALONE,
    mutation_ids: tuple[str, ...] = (),
    known_facts: Mapping[str, str] = {},
) -> CommandStep:
    """One §2.13.2a probe case, as a case-program vector.

    `satisfying_statuses` is stated per case rather than derived, because the
    section states each case's expected errno by name and the case program's exit
    status carries exactly that — so *"satisfied by exit 10, which is EPERM"* is
    something Codex approves in the manifest instead of something a run decides.

    A case that declares a mutation records only its exit status, which
    `plan.CommandStep` enforces and which the errno-bearing exit codes are what
    make sufficient: the errno is in the status, not only in the output.
    """
    return CommandStep(
        step_id=step_id,
        band="filesystem",
        run_as=run_as,
        argv=argv,
        purpose=purpose,
        evidence_case_ids=(case_id,),
        role=role,
        mutation_ids=mutation_ids,
        capture=(
            CapturePolicy.EXIT_STATUS_ONLY
            if mutation_ids
            else CapturePolicy.CASE_RESULT
        ),
        observation_expectations=(
            ()
            if mutation_ids
            else _case_result_for(argv, satisfying_statuses, known=dict(known_facts))
        ),
        satisfying_statuses=satisfying_statuses,
        expected_result=expected_result,
        expected_refusal=expected_refusal,
    )


def _stage_one(
    steps: _Steps, target: DisposableTarget, paths: _Paths, next_id
) -> None:
    """§2.13.2a Stage 1 — the six controls, every one of which must succeed.

    The order is the section's cases reordered by **what each leaves behind**:
    the two renames bracket each other so the file is back where the next case
    expects it, and the unlink is last because it removes the subject. `C-6`
    runs before `C-4` for the same reason — a rename that has not yet happened
    cannot move the file out from under it.

    If any of these fails the probe is inconclusive and no generation is
    created; the executor stops on the first unsatisfied step, which is that rule.
    """

    def vector(verb: str, *arguments: str) -> tuple[str, ...]:
        return build_case_vector(target, verb, *arguments)

    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("pwrite", "wronly", paths.stage1),
            purpose=(
                "C-1: open(O_WRONLY) then pwrite at offset 0 on a file with the "
                "arena's ownership and mode and no append attribute. It proves "
                "ordinary permissions are not the reason for anything Stage 2 "
                "observes."
            ),
            case_id="C-1",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0; the byte at offset 0 changes.",
            expected_refusal="a failure here makes every Stage-2 case inconclusive.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("open", "wronly-trunc", paths.stage1),
            purpose="C-2: open(O_WRONLY|O_TRUNC).",
            case_id="C-2",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0; the file is empty afterwards.",
            expected_refusal="a failure here makes P-2 inconclusive.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("ftruncate", "wronly", paths.stage1),
            purpose="C-3: ftruncate(fd, 0) on a writable descriptor.",
            case_id="C-3",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0.",
            expected_refusal="a failure here makes P-3 inconclusive.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("append", paths.stage1),
            purpose=(
                "C-6: open(O_WRONLY|O_APPEND), write, fsync. It is generated "
                "before the two renames so the file is still at the path it names."
            ),
            case_id="C-6",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0; post_size exceeds pre_size by the reviewed byte count.",
            expected_refusal="a failure here makes P-6 and P-7 inconclusive.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("rename", paths.stage1, paths.stage1_moved),
            purpose=(
                "C-4: rename within …/probe, proving the directory permits one. "
                "The destination is a declared mutation, so a rename that "
                "succeeded and a rename-back that did not leaves a named object "
                "the derived cleanup removes rather than unnamed residue."
            ),
            case_id="C-4",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            mutation_ids=(f"file:{paths.stage1_moved}",),
            expected_result=f"exit 0; the file is at {paths.stage1_moved}.",
            expected_refusal="a failure here makes P-4 inconclusive.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("rename", paths.stage1_moved, paths.stage1),
            purpose=(
                "C-4, reversed. The subject returns to the path C-5 names, and "
                "the intermediate object stops existing."
            ),
            case_id="C-4",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            mutation_ids=(f"file:{paths.stage1}",),
            expected_result=f"exit 0; the file is back at {paths.stage1}.",
            expected_refusal="",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("unlink", paths.stage1),
            purpose=(
                "C-5: unlink, proving the directory permits one. It is last, "
                "because it removes the subject the other five cases share."
            ),
            case_id="C-5",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0; the Stage-1 file is gone.",
            expected_refusal="a failure here makes P-5 inconclusive.",
        )
    )


def _stage_two(
    steps: _Steps, target: DisposableTarget, paths: _Paths, next_id
) -> None:
    """§2.13.2a Stage 2 — nine cases on the identical file root gave `+a`.

    Each expected errno is stated by the section and is carried by the case
    program's exit status, so `EACCES` where `EPERM` is expected does not satisfy
    the step: the run stops, which is the section's rule that `EACCES` in Stage 2
    means the target is mis-provisioned and the result is inconclusive rather
    than a pass.
    """

    def vector(verb: str, *arguments: str) -> tuple[str, ...]:
        return build_case_vector(target, verb, *arguments)

    refusals = (
        (
            "P-1",
            vector("open", "wronly", paths.stage2),
            "open(O_WRONLY) without O_APPEND. may_open() refuses a writable "
            "non-append open on an append-only inode; DAC would have given "
            "EACCES, and C-1 proved DAC permits it.",
        ),
        (
            "P-2",
            vector("open", "wronly-append-trunc", paths.stage2),
            "open(O_WRONLY|O_APPEND|O_TRUNC). O_TRUNC on an append-only inode is "
            "refused even with O_APPEND.",
        ),
        (
            "P-3",
            vector("ftruncate", "wronly-append", paths.stage2),
            "ftruncate on an O_APPEND descriptor. IS_APPEND(inode) is checked in "
            "the truncate path.",
        ),
        (
            "P-4",
            vector("rename", paths.stage2, paths.stage2_moved),
            "rename within …/probe. may_delete()/may_create() refuse on an "
            "append-only victim, and C-4 proved the directory permits renames.",
        ),
        (
            "P-5",
            vector("unlink", paths.stage2),
            "unlink. As P-4, and C-5 proved the directory permits unlinking.",
        ),
    )
    for case_id, argv, why in refusals:
        steps.add(
            _probe_case(
                next_id(),
                run_as=WRITER,
                argv=argv,
                purpose=f"{case_id}: {why}",
                case_id=case_id,
                satisfying_statuses=refused_with("EPERM"),
                expected_refusal=(
                    "EPERM, and EPERM only. The satisfying status is the case "
                    "program's EPERM code, so an EACCES — which would mean "
                    "discretionary access control refused it, and Stage 1 has "
                    "already excluded that — stops the run instead of passing."
                ),
            )
        )

    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("append", paths.stage2),
            purpose=(
                "P-6: open(O_WRONLY|O_APPEND), write, fsync. The capability must "
                "permit the one operation the writer needs."
            ),
            case_id="P-6",
            satisfying_statuses=(0,),
            role=StepRole.DEPENDENT,
            expected_result=(
                "exit 0; post_size exceeds pre_size by the reviewed byte count, "
                "so the bytes are at the old EOF."
            ),
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("pwrite", "wronly-append", paths.stage2),
            purpose=(
                "P-7: pwrite at offset 0 on an O_APPEND descriptor. Deliberately "
                "not a refusal — POSIX requires O_APPEND to ignore the offset, so "
                "a design expecting EPERM here would be wrong. What is asserted "
                "is that the bytes landed at EOF."
            ),
            case_id="P-7",
            satisfying_statuses=(0,),
            role=StepRole.DEPENDENT,
            expected_result=(
                "exit 0; post_size exceeds pre_size by the reviewed byte count "
                "and the file was not overwritten at offset 0."
            ),
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("clearflags", paths.stage2),
            purpose=(
                "P-8: FS_IOC_SETFLAGS clearing FS_APPEND_FL. The arena file is "
                "owned by the writer's uid, so the owner half (A10) is satisfied "
                "and the missing prerequisite is CAP_LINUX_IMMUTABLE alone."
            ),
            case_id="P-8",
            satisfying_statuses=refused_with("EPERM"),
            expected_refusal=(
                "EPERM. ENOTTY or EOPNOTSUPP would mean the filesystem has no "
                "flag interface at all, which is a failed probe and not a passing "
                "one, and neither satisfies this step."
            ),
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("getflags", paths.stage2),
            purpose=(
                "P-8's other half, and P-9 as a syscall: FS_IOC_GETFLAGS after "
                "the refused clear. It is what distinguishes 'refused' from "
                "'silently ignored'."
            ),
            case_id="P-9",
            satisfying_statuses=(0,),
            # **EH-R13-3.** The plan states this value, so it is compared rather
            # than recorded: `fs_append_fl=0` here means the clear the previous
            # step reported refused was not refused, which is precisely the
            # observation this case exists to make and precisely the one exit
            # status 0 does not carry.
            known_facts={"fs_append_fl": "1"},
            expected_result=(
                "exit 0 with fs_append_fl=1 — the flag is still set, and the "
                "value is compared before the step may be satisfied."
            ),
            expected_refusal=(
                "fs_append_fl=0 means the clear was not refused after all, and "
                "ENOTTY or EOPNOTSUPP means the filesystem has no flag interface; "
                "each is a failed probe."
            ),
        )
    )


def _systemd_run(
    *, unit_options: tuple[str, ...], case_argv: tuple[str, ...], read_write_path: str
) -> tuple[str, ...]:
    """One transient-unit invocation, built once so no two can disagree.

    `--uid=`/`--gid=` here take the account **name**: `systemd-run` resolves it
    itself, so these are not late-binding sites and no number appears. That is
    deliberately different from `capsh`, which takes numbers and therefore does
    need `binding.BindingSite`s — the difference is in the tools, and pretending
    otherwise would add a substitution with nothing to substitute.

    `--wait` propagates the service's exit status, which is how the case
    program's errno-bearing code reaches the harness; `--pipe` forwards its
    standard output, which is how the observation does.
    """
    return (
        "/usr/bin/systemd-run",
        f"--unit={TRANSIENT_UNIT}",
        *unit_options,
        "--wait",
        "--pipe",
        "--quiet",
        f"--uid={WRITER}",
        f"--gid={WRITER}",
        f"--property=ProtectSystem={STAGE_4_PROTECT_SYSTEM}",
        f"--property=ReadWritePaths={read_write_path}",
        "--",
        *case_argv,
    )


def _stage_four(
    steps: _Steps, target: DisposableTarget, paths: _Paths, next_id
) -> None:
    """§2.13.2a Stage 4 — the sandbox, and the control that makes it attributable.

    `S4-0` runs the same operations on the same inodes as the same uid on the
    same mount with **only the sandbox removed**, and it runs first in every
    execution. `S4-2`'s EROFS is interpreted beside it and not otherwise: that is
    the R7-B correction, and `S4-2` is declared `DEPENDENT` so the executor stops
    rather than interpreting it if the control did not pass.
    """

    def vector(verb: str, *arguments: str) -> tuple[str, ...]:
        return build_case_vector(target, verb, *arguments)

    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("append", paths.s4_target),
            purpose=(
                "S4-0: append to the exact target S4-2 will be refused on, as "
                "the same identity, outside any unit. Same uid, absolute path, "
                "inode, directory, mount, mode and ownership; only the sandbox "
                "differs."
            ),
            case_id="S4-0",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0 — the target is writable with the sandbox removed.",
            expected_refusal=(
                "a failure here makes S4-2 inconclusive: an EROFS with no passing "
                "S4-0 beside it attributes nothing."
            ),
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("rename", paths.s4_unlink, paths.s4_0_moved),
            purpose="S4-0: rename on the …/probe-ro target, outside any unit.",
            case_id="S4-0",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            mutation_ids=(f"file:{paths.s4_0_moved}",),
            expected_result=f"exit 0; the file is at {paths.s4_0_moved}.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("rename", paths.s4_0_moved, paths.s4_unlink),
            purpose="S4-0: the rename reversed, so the unlink below names a file that exists.",
            case_id="S4-0",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            mutation_ids=(f"file:{paths.s4_unlink}",),
            expected_result=f"exit 0; the file is back at {paths.s4_unlink}.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as=WRITER,
            argv=vector("unlink", paths.s4_unlink),
            purpose="S4-0: unlink on the …/probe-ro target, outside any unit.",
            case_id="S4-0",
            satisfying_statuses=(0,),
            role=StepRole.CONTROL,
            expected_result="exit 0 — the directory permits an unlink with the sandbox removed.",
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as="root",
            argv=_systemd_run(
                unit_options=("--collect",),
                case_argv=vector("append", paths.s4_1_target),
                read_write_path=paths.probe,
            ),
            purpose=(
                "S4-1: the same append inside the transient unit, on a path "
                "**inside** the substituted ReadWritePaths=. `--collect` removes "
                "the unit the moment it exits, so S4-2 can start under the same "
                "reviewed name."
            ),
            case_id="S4-1",
            satisfying_statuses=(0,),
            mutation_ids=(f"transient_unit:{TRANSIENT_UNIT}",),
            expected_result="exit 0 — ProtectSystem=strict permits the substituted path.",
            expected_refusal=(
                "a refusal here means the substitution did not apply, and S4-2's "
                "refusal would then attribute nothing to the path being outside it."
            ),
        )
    )
    steps.add(
        _probe_case(
            next_id(),
            run_as="root",
            argv=_systemd_run(
                unit_options=(),
                case_argv=vector("append", paths.s4_target),
                read_write_path=paths.probe,
            ),
            purpose=(
                "S4-2: the same append to a path **outside** the substituted "
                "ReadWritePaths= and inside ProtectSystem=strict's read-only "
                "tree. No `--collect`, so the failed unit stays loaded and S4-3 "
                "can read the directive set that was actually applied."
            ),
            case_id="S4-2",
            satisfying_statuses=refused_with("EROFS"),
            role=StepRole.DEPENDENT,
            mutation_ids=(f"transient_unit:{TRANSIENT_UNIT}",),
            expected_refusal=(
                "EROFS, and EROFS only. Success is a failed stage — the sandbox "
                "did not deny — and EACCES would mean discretionary permissions "
                "refused it, which S4-0 has just excluded; neither satisfies this "
                "step."
            ),
        )
    )
    capture_argv = (
        "/usr/bin/systemctl",
        "show",
        "--property=ProtectSystem",
        "--property=ReadWritePaths",
        TRANSIENT_UNIT,
    )
    # **C-P5.0-R5-R2/R3, PLAN-1.** The vector is unchanged and cannot pass S4-3
    # under condition 4, and no reviewed producer exists, so S4-3 is declared
    # unresolved under its own conflict **unconditionally**. There is no branch
    # in which this step produces S4-3: adding one is the separately authorized,
    # independently reviewed producer-integration pass, not a value to supply.
    gaps = s4_3_dependency_gaps(
        requested_properties=_requested_properties(capture_argv),
        substituted_path=paths.probe,
    )
    steps.block(
        UnresolvedStep(
            step_ref="STAGE4-S4-3",
            band="filesystem",
            conflict_id=S4_3_CONFLICT,
            design_requires=(
                "S4-3 — §2.13.2a: the transient unit's applied property set, "
                "captured by `systemctl show`, normalized and compared under "
                "the four conditions with the deployed unit and its drop-ins, "
                "and bound to the systemd identity it was made under. "
                "Resolution requires **all** of: (1) the reviewed deployed "
                "`freedom-sheet-writer.service` and its allowed drop-in "
                "policy; (2) a capture vector requesting every property in "
                "`unit_sandbox.COMPARED_PROPERTIES` exactly once; (3) the "
                "canonical `ReadWritePaths=` substitution, "
                "`unit_sandbox.CANONICAL_PROBE_PATH`; and (4) a reviewed "
                "producer and binding for `unit_sandbox.SystemdIdentity`."
            ),
            why_not_a_vector=(
                "the step that runs `systemctl show` on the transient unit "
                "exists, but it cannot produce a passing S4-3: "
                + "; ".join(gaps)
                + ". Widening the vector needs the deployed writer unit, and "
                "capturing the systemd identity needs a producer outside "
                "`plan.PERMITTED_EXECUTABLES`; both are gated work this plan "
                "does not perform."
            ),
            what_would_resolve_it=(
                "a separately authorized, independently reviewed pass that adds "
                "the reviewed deployed unit and drop-in policy, widens the "
                "capture vector, and implements and integrates the reviewed "
                "`SystemdIdentity` producer — code and artifacts that change "
                "this generator. No review reference, label, path, digest or "
                "flag resolves it, and neither does a supplied observation, an "
                "`ExternalCase` or a PASSED record from `unit_sandbox`. "
                "Independent of C-7: resolving Band 7's producers leaves "
                "this open, and resolving this leaves C-7 open."
            ),
            evidence_case_ids=("S4-3",),
        )
    )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="filesystem",
            run_as="root",
            argv=capture_argv,
            purpose=(
                "A partial capture of the directive set systemd applied to "
                "the unit S4-2 ran in. **It is not S4-3 evidence**: S4-3 is "
                f"declared unresolved under {S4_3_CONFLICT} (`STAGE4-S4-3`), "
                "because two properties cannot satisfy condition 4's complete "
                "comparison."
            ),
            evidence_case_ids=(),
            capture=CapturePolicy.UNIT_DIRECTIVES,
            observation_expectations=_unit_directives_expected(
                protect_system=STAGE_4_PROTECT_SYSTEM,
                read_write_paths=paths.probe,
            ),
            expected_result=(
                f"ProtectSystem=strict and ReadWritePaths={paths.probe} — the "
                "deployed unit's directive set, with the single recorded "
                "ReadWritePaths= substitution."
            ),
            expected_refusal=(
                "any other directive set is INCONCLUSIVE rather than a failure: "
                "it says the sandbox under test was not the one the design "
                "describes."
            ),
        )
    )


def _binding_sites(argv: tuple[str, ...], identity) -> tuple[BindingSite, ...]:
    """The three sites in one `capsh` vector, located by scanning the vector.

    Located rather than counted: `capsh_argv()` omits `--inh=` and every
    `--addamb=` when `M` is empty, so the index of `--uid=` differs between `E1`
    and `E4`. Scanning for the prefix and then asserting the argument is exactly
    the symbolic form the site declares — which `binding.validate_sites()` does,
    at `CommandStep` construction — is what makes the position a fact about this
    vector rather than an arithmetic guess about the shape of one.
    """
    wanted = {
        "--gid=": (BindingKind.GID, (identity.primary_group,)),
        "--groups=": (
            BindingKind.GID_LIST,
            (identity.primary_group, *identity.supplementary_groups),
        ),
        "--uid=": (BindingKind.UID, (identity.user,)),
    }
    sites: list[BindingSite] = []
    for prefix, (kind, names) in wanted.items():
        matches = [
            index
            for index, argument in enumerate(argv)
            if argument.startswith(prefix)
        ]
        if len(matches) != 1:
            raise PlanRefused(
                f"{identity.name}'s capsh vector carries {len(matches)} "
                f"{prefix!r} arguments; the construction emits exactly one."
            )
        sites.append(
            BindingSite(argument_index=matches[0], kind=kind, names=names)
        )
    return tuple(sorted(sites, key=lambda site: site.argument_index))


def _band_5(steps: _Steps, target: DisposableTarget, paths: _Paths) -> None:
    """§2.13.5c's `E1 … E6` and `E8` — conflicts **C-2** and **C-5**, together.

    Each vector is `capsh`'s seven-step construction with the Option-B
    case-program vector as its step 7: `--shell=` names the **interpreter**, and
    the arguments after `--` are `-I -S <root>/bin/case identity`. `capsh` execs
    the named shell with those as its `argv[1:]`, so the program the kernel runs
    is written in the reviewed vector rather than hidden behind a shebang, and
    `plan.validate_argv` validates that tail by the same closed grammar a direct
    case-program vector goes through.

    `--gid=`, `--groups=` and `--uid=` carry the **symbolic names** — the four
    §2.12.2 provisions and no fifth — and each is a declared
    `binding.BindingSite`. The review manifest therefore pins names, the executor
    resolves them through the injected NSS boundary immediately before the
    process is created, and it revalidates the whole substituted vector before
    `execve`. Nothing outside a declared site may change.

    **`E7` is not in this band, and it is not unobserved either.** It is the
    harness's own root identity, produced by not dropping anything, so there is
    no `capsh` construction for this band to emit — and R12 wrongly concluded
    from that that there was nothing to observe. There is: `P-06` runs the same
    `identity` verb through the **direct** Option-B vector, in the same kind of
    final interpreted process, and compares the same twelve values. It is
    generated with the other case-program prerequisites, because it has to
    precede every operation attributed to `E7` and this band does not.

    **R16, conflict C-6.** The identity observations come first, and the three
    immutable-flag experiments follow in `_band_5_immutable_experiments`. That
    order is the §2.13.5c assertion contract made structural: *"Every case
    asserts its identity before it asserts its result … A case whose identity
    assertion fails is `inconclusive` — never a pass, never a refusal."*
    `_validate_capability_experiment_ordering` asserts it over the generated
    plan, so an experiment that ran before the identity it is attributed to was
    observed is a `PlanRefused` rather than a run.
    """
    case_argv = build_case_vector(target, "identity")
    for name, identity in EVIDENCE_IDENTITIES.items():
        if name == "E7":
            # No capsh vector exists for E7 — see `P-06`, which observes it.
            continue
        argv = identity.capsh_argv(
            case_program_argv=case_argv,
            all_capability_names=ALL_CAPABILITY_NAMES,
            # The planner substitutes **nothing**: it passes the name straight
            # through, so the generated vector is the symbolic one the manifest
            # pins and the numbers exist only inside the executor.
            resolve_uid=lambda account: account,
            resolve_gid=lambda group: group,
        )
        masks = identity.expected_masks()
        steps.add(
            CommandStep(
                step_id=f"B5-{name}",
                band="capability",
                run_as="root",
                argv=argv,
                purpose=(
                    f"§2.13.5c's seven-step construction of {name}: user "
                    f"{identity.user}, primary group {identity.primary_group}, "
                    f"supplementary {list(identity.supplementary_groups)}, "
                    f"capability set mask {identity.mask:#x}, final securebits "
                    f"{masks['securebits']:#x} observed inside the process, "
                    f"exec'ing the reviewed case "
                    f"program at {paths.case_binary} through the named "
                    "interpreter."
                ),
                # **R13, EH-R13-4.** `CAP-IDENTITY-<name>`, not
                # `JNL-49-<name>`/`JNL-50-<name>`. This step observes an
                # identity; it performs no capability-matrix operation, and
                # §2.13.8's cases are one per capability/artifact **pairing**.
                # Attributing them here made the matrix look present in a plan
                # that contained none of it — a case id counted, an experiment
                # missing.
                evidence_case_ids=(f"CAP-IDENTITY-{name}",),
                capture=CapturePolicy.CASE_IDENTITY,
                identity_name=name,
                bindings=_binding_sites(argv, identity),
                expected_result=(
                    f"exit 0; uid and gid equal the numbers the bound vector's "
                    f"--uid= and --gid= asked for ({identity.user} and "
                    f"{identity.primary_group}), the supplementary gid **set** "
                    f"equals the one --groups= asked for "
                    f"{list((identity.primary_group, *identity.supplementary_groups))}, "
                    f"the five masks are cap_prm={masks['cap_prm']:#x}, "
                    f"cap_eff={masks['cap_eff']:#x}, cap_inh={masks['cap_inh']:#x}, "
                    f"cap_amb={masks['cap_amb']:#x}, cap_bnd={masks['cap_bnd']:#x}, "
                    f"no_new_privs=0, and the final securebits read by "
                    f"prctl(PR_GET_SECUREBITS) inside the exec'd process is "
                    f"{masks['securebits']:#x}. **Every one of those twelve values "
                    "is compared before this step may be satisfied**, and exit 0 "
                    "alone does not satisfy it."
                ),
                expected_refusal=(
                    "any value disagreeing with the derivation makes every case "
                    f"run under {name} INCONCLUSIVE, and the run stops here so no "
                    "dependent operation is executed or interpreted. **Securebits "
                    "is observed rather than assumed** — R12's disposition of "
                    "EH-R11-2: the kernel reports it through "
                    "prctl(PR_GET_SECUREBITS) and through no file, the case "
                    "program reads it there after capsh's construction and after "
                    "execve, and a securebits that cannot be read exits 66, which "
                    "satisfies no step. The `--secbits=` option in the vector is "
                    "an intent; this is the state."
                ),
            )
        )
    _band_5_immutable_experiments(steps, target, paths)


def _capability_experiment(
    steps: _Steps,
    *,
    step_id: str,
    run_as: str,
    argv: tuple[str, ...],
    purpose: str,
    case_id: str,
    role: StepRole,
    satisfying: tuple[int, ...],
    known: Mapping[str, str] = {},
    identity=None,
    expected_result: str = "",
    expected_refusal: str = "",
) -> None:
    """One `JNL-49`/`JNL-50` operation, as a case-program vector — conflict **C-6**.

    It is `_access_case`'s shape with two differences the immutable-flag cases
    need. The satisfying statuses are **given** rather than derived from a
    `permitted` flag, because §2.13.5c states one exact errno per case — `EPERM`
    for the owner check and `EACCES` for the discretionary one — and admitting
    both would be admitting the wrong refusal for either. And a step run under a
    constructed identity carries that identity's binding sites, because the four
    disposable names do not exist when the plan is generated.
    """
    steps.add(
        CommandStep(
            step_id=step_id,
            band="capability",
            run_as=run_as,
            argv=argv,
            purpose=purpose,
            evidence_case_ids=(case_id,),
            role=role,
            capture=CapturePolicy.CASE_RESULT,
            observation_expectations=_case_result_for(argv, satisfying, known=known),
            satisfying_statuses=satisfying,
            bindings=_binding_sites(argv, identity) if identity is not None else (),
            expected_result=expected_result,
            expected_refusal=expected_refusal,
        )
    )


def _band_5_immutable_experiments(
    steps: _Steps, target: DisposableTarget, paths: _Paths
) -> None:
    """§2.13.8's three capability-matrix **operations** — conflict **C-6**, resolved.

    ## What was missing, and what makes these not an approximation

    R13's Blocking finding EH-R13-4 was that Band 5 emitted seven `capsh`
    vectors ending in the `identity` verb and stopped. An identity observation is
    a *prerequisite* for `JNL-49` and `JNL-50`; it is not their result. R14 left
    the three operations declared unresolved because the reviewed case program
    could read and clear `FS_APPEND_FL` and nothing else, and running an
    append-only experiment under `E4`, `E5` and `E6` would have produced a
    passing record for a case about `+i` — evidence for a claim nobody made.

    The maintainer approved the narrowly scoped immutable-flag extension on
    2026-09-09. `getimmutable` and `clearimmutable` name `FS_IMMUTABLE_FL` in
    their own bodies in `execution/case_program.py`; **no verb takes a flag, a
    mask or an ioctl request number as an argument**, so what these steps widen
    is the closed verb table by two entries and nothing else.

    ## The three cases, and the kernel checks they separate

    §2.13.5c decomposes `FS_IOC_SETFLAGS` into two independent checks: the
    caller's effective uid must equal the inode's owner **or** it must hold
    `CAP_FOWNER` — authority **A10** over the writer's own inode, **A11** over a
    root-owned one — and changing `FS_IMMUTABLE_FL` additionally requires
    `CAP_LINUX_IMMUTABLE`, authority **A1**. The owner check is evaluated first.

    | Case | Identity | Holds | Expected |
    |---|---|---|---|
    | `JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE` | `E4` | A1 and every discretionary right; **not** A10, **not** A11 | the `open(O_RDONLY)` succeeds — that is `CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH` doing their job — and `FS_IOC_SETFLAGS` returns **`EPERM`** |
    | `JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE` | `E6` | `E4` **plus `CAP_FOWNER`**, and identical in every other option | the same call **returns**, and the flag is gone |
    | `JNL-50-E5-CLEAR-THEN-DENIED-OPEN` | `E5` | A1, A10, A11 and `freedomcoord`'s read/traverse | the clear **returns**; the separately ordered `open(O_WRONLY)` is then refused with **`EACCES`**, because the file is `0440 root:freedomcoord` |

    **The expected outcomes are the approved package design's, not the run's.**
    They are written here from §2.13.5c's falsification matrix and its
    not-constructible table; a case that returns something else is a finding for
    Codex, and there is no path by which an observation edits an expectation.

    ## Why `E6` runs second, and why that is the strongest available control

    §2.13.5c's control form **C-I** requires the control to vary one capability
    and hold *"same uid, gid, supplementary list, securebits, case binary, path,
    inode and mount"*. `E4` and `E6` differ in `cap_fowner` in `--drop`'s
    complement, in `--inh` and in one `--addamb`, and in nothing else. Holding
    the **inode** fixed as well is only possible in one order: `E4`'s attempt is
    expected to be refused, so it leaves the flag set and `E6` can then perform
    the identical call on the identical inode. Running the control first would
    clear the flag `E4`'s case is about.

    So the control is ordered second, and the step between them is what makes
    that sound: `B5-C6-03` reads the flag back **as root** after `E4`'s refusal
    and requires it still to be set. Without it, `E6`'s success would be
    consistent with `E4` having quietly succeeded.

    ## Initial state, established separately for every experiment

    Each experiment is preceded by its own `getimmutable` reading under `E7`
    requiring `fs_immutable_fl=1` on **its own** subject: `B5-C6-01` for `E4`,
    `B5-C6-03` for `E6` and `B5-C6-05` for `E5`. `E5`'s subject is a different
    archive file from `E4`/`E6`'s, so `E6`'s successful clear cannot make `E5`'s
    case meaningless — and the reading proves it rather than the ordering
    implying it.

    ## Reset, and what the failure path leaves

    `B5-C6-08` … `B5-C6-11` set `+i` back on both files and read it back, so the
    hierarchy the rest of the plan documents is the hierarchy the rest of the
    plan runs against. The two `chattr` steps declare the `file_attribute`
    mutations they perform, which are the same two Band 3 declared: cleanup
    already clears both flags before removing either file, and it does so whether
    or not this band was reached.

    Every step here is satisfied by exactly the statuses its case states, so the
    failure path is the executor's ordinary one: the first unsatisfied step stops
    the run, its role says what that invalidates, and the full derived cleanup
    runs. A refused clear leaves the flag set, and a clear that unexpectedly
    succeeded leaves it cleared — which cleanup reverses either way.
    """
    identities = EVIDENCE_IDENTITIES

    def constructed(name: str, verb: str, *arguments: str) -> tuple[str, ...]:
        """The `capsh` construction for `name`, exec'ing one operation verb."""
        return identities[name].capsh_argv(
            case_program_argv=build_case_vector(target, verb, *arguments),
            all_capability_names=ALL_CAPABILITY_NAMES,
            resolve_uid=lambda account: account,
            resolve_gid=lambda group: group,
        )

    def root_flag_reading(step_id: str, path: str, why: str, case_id: str) -> None:
        """`E7` reads `FS_IMMUTABLE_FL` on one artifact and requires it set."""
        argv = build_case_vector(target, "getimmutable", path)
        steps.add(
            CommandStep(
                step_id=step_id,
                band="capability",
                run_as="root",
                argv=argv,
                purpose=why,
                evidence_case_ids=(case_id,),
                # **A positive control, and not a prerequisite.** A prerequisite
                # is asserted before anything is constructed; this is asserted
                # immediately before one experiment, about the inode that
                # experiment is about. Its failure is exactly what `CONTROL`
                # means: a refusal beside a flag that was not set attributes
                # nothing, so the dependent case is inconclusive rather than
                # passed.
                role=StepRole.CONTROL,
                capture=CapturePolicy.CASE_RESULT,
                observation_expectations=_case_result_for(
                    argv, (0,), known={"fs_immutable_fl": "1"}
                ),
                expected_result=(
                    "exit 0 and fs_immutable_fl=1 — the artifact carries the "
                    "immutable flag, which is the state the experiment that "
                    "follows is about."
                ),
                expected_refusal=(
                    "fs_immutable_fl=0, an unreadable observation or any non-zero "
                    "exit stops the run. A flag-clearing experiment against an "
                    "inode whose flag is already gone asserts nothing, and it is "
                    "refused here rather than recorded and interpreted later."
                ),
            )
        )

    # ---- JNL-49: E4 is refused, E6 is not ----------------------------------
    root_flag_reading(
        "B5-C6-01",
        paths.archive_journal,
        "The initial artifact state for E4's experiment, established separately "
        "and immediately before it: the root-owned archived journal carries "
        "FS_IMMUTABLE_FL.",
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
    )
    _capability_experiment(
        steps,
        step_id="B5-C6-02",
        run_as="root",
        argv=constructed("E4", "clearimmutable", paths.archive_journal),
        purpose=(
            "JNL-49: E4 attempts FS_IOC_SETFLAGS clearing FS_IMMUTABLE_FL on "
            f"{paths.archive_journal} — root-owned, 0440, +i. E4 holds "
            "CAP_DAC_OVERRIDE, CAP_DAC_READ_SEARCH and CAP_LINUX_IMMUTABLE, so "
            "it reaches and opens the inode; it holds neither A10 nor A11, so "
            "the ioctl's owner check refuses it. This is the isolating case for "
            "R9-A: every discretionary right and the flag capability, and still "
            "no flag change."
        ),
        case_id="JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        role=StepRole.DEPENDENT,
        satisfying=refused_with("EPERM"),
        identity=identities["E4"],
        expected_refusal=(
            "exit 10 — result=refused, errno=EPERM. **EPERM and not EACCES**: "
            "the owner check is evaluated before CAP_LINUX_IMMUTABLE is "
            "consulted, so a caller without owner authorization is refused "
            "whether or not it holds the flag capability. An EACCES here would "
            "be a different kernel path and is not this case; exit 0 would mean "
            "the boundary §2.13.5c rests on is not there."
        ),
    )
    root_flag_reading(
        "B5-C6-03",
        paths.archive_journal,
        "The flag is read back as root after E4's refusal, and must still be "
        "set. It is E6's separately established initial state, and it is what "
        "makes E6's success attributable: without it, E6 returning would be "
        "consistent with E4 having quietly succeeded.",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
    )
    _capability_experiment(
        steps,
        step_id="B5-C6-04",
        run_as="root",
        argv=constructed("E6", "clearimmutable", paths.archive_journal),
        purpose=(
            "JNL-49: E6 performs the identical call on the identical inode and "
            "succeeds. E6 is E4 plus CAP_FOWNER — one capability in --drop's "
            "complement, in --inh and in one --addamb, and nothing else: same "
            "uid, gid, supplementary list, securebits, case program, path, inode "
            "and mount. That is control form C-I, and it is what makes E4's "
            "EPERM attributable to the owner check rather than to discretionary "
            "access, to path search or to the flag capability."
        ),
        case_id="JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        role=StepRole.CONTROL,
        satisfying=(0,),
        known={"fs_immutable_fl": "0"},
        identity=identities["E6"],
        expected_result=(
            "exit 0; result=returned, errno=none and fs_immutable_fl=0 — the "
            "flag is gone, read back by the same ioctl inside the same process."
        ),
        expected_refusal=(
            "a refusal here makes JNL-49's E4 case **inconclusive** rather than "
            "passed: a denial beside a control that did not succeed attributes "
            "nothing. The run stops, and no dependent case is interpreted."
        ),
    )

    # ---- JNL-50: E5 clears, and is then denied the write open ---------------
    root_flag_reading(
        "B5-C6-05",
        paths.archive_seal,
        "The initial artifact state for E5's experiment, on a **different** "
        "archive file from E4's and E6's, established separately: the flag E6 "
        "cleared was on another inode, so this case cannot inherit its result.",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
    )
    _capability_experiment(
        steps,
        step_id="B5-C6-06",
        run_as="root",
        argv=constructed("E5", "clearimmutable", paths.archive_seal),
        purpose=(
            "JNL-50, first half: E5 clears FS_IMMUTABLE_FL on "
            f"{paths.archive_seal}. E5 is fbprobe with CAP_FOWNER and "
            "CAP_LINUX_IMMUTABLE and a freedomcoord membership, so it holds A1 "
            "and A11 and reaches …/archive by group traverse. The clear is "
            "expected to **succeed** — that is A1 and A11 doing exactly their "
            "job — and its success is the prerequisite that gives the next "
            "step's refusal its meaning."
        ),
        case_id="JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
        role=StepRole.CONTROL,
        satisfying=(0,),
        known={"fs_immutable_fl": "0"},
        identity=identities["E5"],
        expected_result=(
            "exit 0; result=returned, errno=none and fs_immutable_fl=0. The two "
            "halves are **separately ordered steps** rather than one vector, "
            "because the second is interpretable only if the first returned, and "
            "a single step reporting one exit status could not say which of the "
            "two the status belonged to."
        ),
        expected_refusal=(
            "any refusal stops the run and makes the second half inconclusive. "
            "An EPERM here would mean E5 does not hold the owner half after all, "
            "and the EACCES the next step expects would then prove nothing about "
            "discretionary access — it would be the immutability refusal wearing "
            "another name."
        ),
    )
    _capability_experiment(
        steps,
        step_id="B5-C6-07",
        run_as="root",
        argv=constructed("E5", "open", "wronly", paths.archive_seal),
        purpose=(
            "JNL-50, second half: E5 opens the same file O_WRONLY and is "
            "refused. The file is 0440 root:freedomcoord, and freedomcoord "
            "membership confers read and traverse and never write. **This is the "
            "executed proof that flag authority confers no discretionary "
            "access**, and its interpretation requires the clear to have "
            "succeeded: inode_permission() refuses MAY_WRITE on an immutable "
            "inode with EPERM *before* it evaluates DAC, so an EACCES observed "
            "here has already proved the flag was gone."
        ),
        case_id="JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
        role=StepRole.DEPENDENT,
        satisfying=refused_with("EACCES"),
        identity=identities["E5"],
        expected_refusal=(
            "exit 11 — result=refused, errno=EACCES. **EACCES and not EPERM**: "
            "EPERM would mean the immutable flag was still set and the "
            "discretionary check was never reached, which is the previous step "
            "having failed rather than this one having passed. Exit 0 would mean "
            "CAP_LINUX_IMMUTABLE plus CAP_FOWNER had obtained a write this "
            "design says they cannot."
        ),
    )

    # ---- The reset, and its read-back --------------------------------------
    for index, (path, case_id) in enumerate(
        (
            (paths.archive_journal, "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE"),
            (paths.archive_seal, "JNL-50-E5-CLEAR-THEN-DENIED-OPEN"),
        ),
        start=8,
    ):
        steps.add(
            _set_flag(
                f"B5-C6-{index:02d}",
                "capability",
                path,
                "immutable",
                why=(
                    f"Reset: set FS_IMMUTABLE_FL back on {path}, which this "
                    "band's successful clear removed. It restores the state "
                    "§2.13.3 describes and the rest of the plan documents, and "
                    "it declares the same file_attribute mutation Band 3 "
                    "declared — one mutation, one reversal, performed twice."
                ),
                refusal=(
                    "a failure stops the run. Cleanup clears both flags before "
                    "removing either file, so a flag this step could not set is "
                    "a flag cleanup does not need — but a flag effect that "
                    "fails here is evidence the harness's own authority is not "
                    "what the rest of the band assumed."
                ),
            )
        )
    for index, (path, case_id) in enumerate(
        (
            (paths.archive_journal, "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE"),
            (paths.archive_seal, "JNL-50-E5-CLEAR-THEN-DENIED-OPEN"),
        ),
        start=10,
    ):
        root_flag_reading(
            f"B5-C6-{index:02d}",
            path,
            f"Read the reset flag back on {path} rather than assuming chattr "
            "set it — the same rule Band 3 applies to the flags it sets.",
            case_id,
        )



def _band_6(steps: _Steps, target: DisposableTarget, paths: _Paths) -> None:
    order = 0

    def next_id() -> str:
        nonlocal order
        order += 1
        return f"B6-{order:02d}"

    # ---- §1.4.3 and §2.3.3: the capture, into the **independent** store -----
    #
    # This was two `install` vectors copying the live configuration into
    # `R/before`. Both are gone, and PR-20260911-2 is why: the captures under
    # the disposable root are in the custody the run is about, so they are not a
    # recovery basis. One effect now publishes the reviewed capture set into
    # `/var/lib/freedom-blades/recovery/<run-id>/`, crossing all five §2.3.3
    # barriers in order, and **M1 may not run until it reports every one
    # crossed**. `R/before` is retained as evidence and is not a basis.
    captured_by: dict[str, str] = {}
    capture_step = next_id()
    for filename in CAPTURED_CONFIGURATION:
        captured_by[filename] = capture_step
    steps.add(
        CommandStep(
            step_id=capture_step,
            band="postgresql",
            run_as="root",
            argv=(),
            effect=DescriptorEffect(
                kind=EffectKind.CAPTURE_CONFIGURATION,
                configuration_role=CONFIGURATION_ROLE,
                components=CAPTURED_CONFIGURATION,
                path=target.postgres_config_directory,
                evidence_role="before",
            ),
            purpose=(
                "Capture both reviewed configuration files byte-exactly, into "
                "the independent recovery store outside the disposable root, "
                "and publish them durably. The digest is computed over the one "
                "held buffer the read produced, never over a re-read of a "
                "pathname, and each record binds its bytes to exactly the "
                "destination the restoration will write."
            ),
            mutation_ids=tuple(
                f"file:{paths.capture(filename)}"
                for filename in CAPTURED_CONFIGURATION
            ),
            expected_result=(
                "every §2.3.3 barrier returned success, the stored copies and "
                "records verify against the reviewed capture set, and the "
                "publication reports `mutation_permitted`."
            ),
            expected_refusal=(
                "a failure at any barrier, a source that changed across the "
                "read, or a requested set that is not the reviewed one refuses "
                "**before** the first configuration mutation — so there is "
                "nothing to recover from."
            ),
        )
    )

    steps.add(
        CommandStep(
            step_id=next_id(),
            band="postgresql",
            run_as="postgres",
            argv=_psql(
                target,
                dbname="postgres",
                command=f"CREATE DATABASE {target.database_name}",
            ),
            purpose="Create the disposable evidence database.",
            mutation_ids=(f"postgres_database:{target.database_name}",),
            expected_result="exit 0.",
            expected_refusal="",
        )
    )
    role_step_id = f"B6-{order + 1:02d}"
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="postgresql",
            run_as="postgres",
            argv=_psql(
                target,
                dbname="postgres",
                command=(
                    f"CREATE ROLE {COORDINATOR_ROLE} LOGIN NOSUPERUSER NOCREATEDB "
                    "NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD NULL "
                    "CONNECTION LIMIT 2"
                ),
            ),
            purpose="Create §2.12.3's coordinator role in the disposable instance.",
            mutation_ids=(f"postgres_role:{COORDINATOR_ROLE}",),
            expected_result="exit 0; the role exists with PASSWORD NULL and no attribute beyond LOGIN.",
            expected_refusal="",
        )
    )

    # Conflict **C-4**, resolved. These write file *content*, which no permitted
    # executable does, so they are `MaterializeStep`s rather than `CommandStep`s:
    # no argument vector, no shell redirection, no `tee`, no heredoc, and no
    # general write-file interface — the bytes come from the closed two-file
    # table in `materialization.py` and the destination from `config_path()`.
    reviewed = reviewed_configuration(target)
    for index, filename in enumerate(("pg_hba.conf", "pg_ident.conf"), start=1):
        steps.materialize(
            MaterializeStep(
                step_id=f"B6-M{index}",
                band="postgresql",
                run_as="root",
                destination=target.config_path(filename),
                file=reviewed[filename],
                purpose=(
                    "Install §2.12.3's five HBA rules, in that order, above the "
                    "one broader `local all all` rule beneath them."
                    if filename == "pg_hba.conf"
                    else "Install §2.12.3's single "
                    f"`freedom_coord freedomcoord {COORDINATOR_ROLE}` "
                    "identity-map line, with no regular expression and no wildcard."
                ),
                capture_step_id=captured_by[filename],
                after_step_id=role_step_id,
                mutation_ids=(
                    f"postgres_config_line:{filename}:{MAPPED_OS_USER}->"
                    f"{MAPPED_POSTGRES_ROLE}",
                ),
                evidence_case_ids=("HBA-POST-CHANGE-ORDERING",),
                expected_result=(
                    f"the destination holds exactly the {reviewed[filename].byte_count} "
                    f"reviewed bytes, postgres:postgres 0640, digest "
                    f"{reviewed[filename].sha256}."
                ),
                expected_refusal=(
                    "a content or digest mismatch, an unreviewed destination, a "
                    "destination that is not an existing regular file, or a "
                    "pre-change capture that was not taken — each stops the band "
                    "before the file is touched."
                ),
            )
        )

    steps.add(
        CommandStep(
            step_id=next_id(),
            band="postgresql",
            run_as="postgres",
            argv=_psql(target, dbname="postgres", command="SELECT pg_reload_conf()"),
            purpose=(
                "Make the changed authentication configuration effective. A reload, "
                "never a restart: PostgreSQL is not stopped at any point."
            ),
            evidence_case_ids=("HBA-RELOAD",),
            expected_result="exit 0 — the signal was sent. That is all a zero exit means.",
            expected_refusal="",
        )
    )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="postgresql",
            run_as=MAPPED_OS_USER,
            argv=_psql(
                target,
                dbname=target.database_name,
                username=COORDINATOR_ROLE,
                command="SELECT 1",
            ),
            purpose=(
                "The positive control of the peer/HBA boundary: the mapped identity "
                "asking for the mapped role over the local socket must authenticate."
            ),
            evidence_case_ids=("HBA-POSITIVE-CONTROL",),
            role=StepRole.CONTROL,
            expected_result="exit 0.",
            expected_refusal=(
                "a refusal here makes every denial below inconclusive — a denial "
                "beside a failed control attributes nothing."
            ),
        )
    )
    for identity in (WRITER, PROBE):
        steps.add(
            CommandStep(
                step_id=next_id(),
                band="postgresql",
                run_as=identity,
                argv=_psql(
                    target,
                    dbname=target.database_name,
                    username=COORDINATOR_ROLE,
                    command="SELECT 1",
                ),
                purpose=(
                    f"{identity} must not reach the coordinator role. The identity "
                    "map names one system user and no other."
                ),
                evidence_case_ids=(f"HBA-DENY-{identity}",),
                role=StepRole.DEPENDENT,
                satisfying_statuses=(),
                refusal_required=True,
                expected_result="",
                expected_refusal=(
                    "non-zero — peer authentication fails because the map admits "
                    "only the mapped identity."
                ),
            )
        )
    steps.add(
        CommandStep(
            step_id=next_id(),
            band="postgresql",
            run_as=MAPPED_OS_USER,
            argv=_psql(
                target,
                dbname=target.database_name,
                username=COORDINATOR_ROLE,
                command="SELECT 1",
                host=LOOPBACK,
                port=APPROVED_TARGET_FACTS.postgres_port,
            ),
            purpose=(
                "The same identity and role over TCP rather than the local socket. "
                "§2.12.3's reject line is what makes this fail."
            ),
            evidence_case_ids=("HBA-DENY-TCP",),
            role=StepRole.DEPENDENT,
            satisfying_statuses=(),
            refusal_required=True,
            expected_result="",
            expected_refusal=(
                "non-zero. A missing reject line (HBA-B4) would let a later broad "
                "`host all all scram-sha-256` make the role reachable, and that "
                "stops the band."
            ),
        )
    )


def _band_7(steps: _Steps) -> None:
    """Provenance, manifests and the journal lifecycle — **producers missing**.

    ## Where this band stands

    R12's version of this function returned `None` with a comment saying the band
    *"creates no host object"* and that every case is *"a pure function over
    supplied observations"*. Both sentences are true, and together they were read
    as *"nothing to generate"* — a different claim and a false one: a pure
    function over supplied observations still needs the observations, and nothing
    in this harness supplied any. R13's **EH-R13-4** found the band emitting no
    step and declaring nothing unresolved while `is_executable` was `True`.

    R14 declared the three cases unresolved under conflict **C-7**. R16's first
    submission moved them to `ExternalCase`s and, in doing so, removed every
    unresolved entry from the band. R16's review returned that as Important
    finding **EH-R16-4**:

    > Band 7 now declares external producers by descriptions of future
    > coordinator tooling, removing all unresolved entries. The handback
    > expressly says their existence is not established. … Naming
    > `init-generation` and a future table does not resolve the evidence
    > dependency that blocked pre-implementation readiness.

    That is conceded in full. **The three cases are `UnresolvedStep`s again**,
    under conflict C-7, and `ConcretePlan.is_executable` is `False` while they
    are — so the executor's second gate refuses and no complete-harness success
    can be produced with the band missing.

    ## What survives, and why it is not a resolution

    The ingestion stage itself is real and is kept: `observations.py` validates a
    payload against a closed, versioned schema and classifies it through the
    band's own classifiers, and `execution/evidence_cli.py` reads a file while
    importing no boundary, no executor and no materializer. What R16 found is
    that a *route in* is not a *producer*.

    So each case additionally declares an `ExternalCase` — the **input contract**
    — with `producer_artifact_reviewed=False`. The contract is documentation:
    it records the shape an observation would have to have and who would have to
    make it, the review manifest pins it so a reviewer approves that shape, and
    `resolves_coverage` is `False` for every entry, so **no entry occupies
    `check_case_coverage`'s external column**. A case is in the unresolved column
    and in no other.

    Three separate mechanisms keep a supplied record from closing a missing
    producer, and each of them is sufficient on its own:

    1. `check_case_coverage` receives an empty external list, so the case is
       declared unresolved and `is_executable` is `False`;
    2. `observations.classify_supplied_observations` reports a case whose plan
       step is declared unresolved in `unresolved_cases` and **never** in
       `covered`, however many well-formed records arrive for it; and
    3. `EvidenceResult.eligible_for_operational_acceptance` is `False`
       unconditionally — EH-R16-3.

    ## What would resolve it, and what this submission does not do

    Each entry's `what_would_resolve_it` names a **bounded evidence-only
    producer**: a reviewed artifact that arranges the situation on the disposable
    host and records the observation. That is not built here. Building it, or
    building the gated Package 5.0 product tooling whose absence is the
    dependency, is outside this remediation's authority, and EH-R16-4 says so
    directly: *"Do not implement gated Package 5.0 product tooling merely to
    satisfy this finding."* The scope and the authority such work would need are
    described in the handback for a later decision; the dependency stays open.
    """
    for schema in BAND_7_SCHEMA.values():
        steps.block(
            UnresolvedStep(
                step_ref=f"BAND7-{schema.case_id}",
                band=schema.band,
                conflict_id="C-7",
                design_requires=(
                    f"{schema.case_id} — {schema.collection_procedure}."
                ),
                why_not_a_vector=(
                    "this band observes nothing this plan does. Its cases are "
                    "comparisons over what happened when `init-generation` ran "
                    "with its provenance record removed, when a probe stage was "
                    "made to fail, and when cleanup did not complete — "
                    "situations an operator arranges on the disposable host and "
                    "that no argument vector in this plan produces. The "
                    "coordinator tooling that would produce them is Package "
                    "5.0's gated product work and does not exist."
                ),
                what_would_resolve_it=(
                    "a reviewed, bounded, evidence-only producer that arranges "
                    f"the situation this case is about — {schema.producer} — and "
                    "records the observation, together with the authorization to "
                    "run it on the disposable host. The importer's schema is "
                    "already reviewed and pinned, so what is missing is the "
                    "artifact that makes the observation, not the route by which "
                    "it would enter. A well-formed record is not that artifact."
                ),
                evidence_case_ids=(schema.case_id,),
            )
        )
        steps.external(
            ExternalCase(
                case_id=schema.case_id,
                band=schema.band,
                producer=schema.producer,
                collection_procedure=schema.collection_procedure,
                variants=schema.variants,
                why_not_a_step=(
                    "this band observes nothing this plan does; see the "
                    "unresolved entry of the same case id. This contract records "
                    "the shape a reviewed observation would have to have and who "
                    "would have to make it. **It resolves nothing**: "
                    "`producer_artifact_reviewed` is False, so it occupies no "
                    "coverage column, and the case is declared unresolved."
                ),
            )
        )


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

#: Every band the concrete plan covers, in run order.
BANDS = ("discovery", "identity", "filesystem", "capability", "postgresql", "journal")


@dataclass(frozen=True, slots=True)
class ConcretePlan:
    """The generated plan, its derived cleanup, and what could not be generated."""

    execution_plan: ExecutionPlan
    cleanup_plan: CleanupPlan
    unresolved: tuple[UnresolvedStep, ...]
    #: **R16, conflict C-7.** The required evidence cases whose producer is not a
    #: step of this plan, each with the actor that makes the observation and the
    #: procedure that collects it. They do not make the plan inexecutable — they
    #: are not something the run does — and they are not covered by anything
    #: until `observations.py` validates a record for every one of their
    #: variants.
    external_cases: tuple[ExternalCase, ...] = ()

    @property
    def target(self) -> DisposableTarget:
        return self.execution_plan.target

    @property
    def steps(self) -> tuple[CommandStep, ...]:
        return self.execution_plan.steps

    @property
    def mutations(self) -> tuple[Mutation, ...]:
        return self.execution_plan.mutations

    @property
    def materializations(self) -> tuple[MaterializeStep, ...]:
        return self.execution_plan.materializations

    @property
    def is_executable(self) -> bool:
        """False while any part of the reviewed design is unresolved.

        The executor consults this. A plan that can run four bands out of six is
        not four-sixths of the evidence: the bands that are missing include every
        positive control Stage 2 and the capability matrix depend on, and running
        the rest would produce refusals nothing attributes.
        """
        return not self.unresolved

    def unresolved_by_band(self, band: str) -> tuple[UnresolvedStep, ...]:
        return tuple(item for item in self.unresolved if item.band == band)

    def conflicts(self) -> tuple[str, ...]:
        return tuple(sorted({item.conflict_id for item in self.unresolved}))

    def traceability(self) -> tuple[tuple[str, str, str], ...]:
        """`(mutation id, the steps that perform it, the cleanup steps that
        reverse it)`, for every declared mutation.

        Generated from the two plans rather than maintained beside them, so a
        mutation with no reversal or a reversal with no mutation is visible in
        the table instead of being a claim about it.
        """
        rows: list[tuple[str, str, str]] = []
        for mutation in self.mutations:
            performed = [
                step.step_id
                for step in (*self.steps, *self.materializations)
                if mutation.mutation_id in step.mutation_ids
            ]
            reversed_by = [
                step.step_id
                for step in self.cleanup_plan.steps
                if mutation.mutation_id in step.mutation_ids
            ]
            rows.append(
                (
                    mutation.mutation_id,
                    ", ".join(performed) or "— not reached by any generated step",
                    ", ".join(reversed_by) or "— NO REVERSAL",
                )
            )
        return tuple(rows)


def _validate_root_identity_ordering(steps: Sequence[CommandStep]) -> None:
    """**EH-R12-1's ordering requirement, asserted over the generated plan.**

    The finding is that `E7` had no semantic identity observation. Adding one is
    half the remediation; the other half is that it has to come **first**, or a
    run could attribute an operation to `E7` and only afterwards discover that
    `E7` was not what §2.13.5c says it is.

    ## What "an operation this plan attributes to `E7`" is

    Exactly one step observes `E7`, so there is no ambiguity about which
    observation applies. The operations whose attribution depends on it are the
    **case-program operations the root harness performs**: §2.13.5c's assertion
    contract governs the case program's processes — *"every case asserts its
    identity before it asserts its result"* — and a root case-program step is a
    case run as `E7`. This function requires every one of them to appear after
    the `E7` observation, and requires there to be exactly one such observation.

    ## The two exclusions, stated rather than assumed

    **The two observation verbs are not operations.** `case_runtime.
    OBSERVATION_VERBS` — `runtime` and `identity` — *"make no filesystem change
    and take no path"*, and neither reports anything whose meaning depends on
    which identity ran it: `P-05` reports the interpreter's path, resolved path,
    version, digest and isolation, and `P-06` is the `E7` observation itself.
    `P-05` deliberately stays **before** `P-06`, so the identity is observed
    through an interpreter that has already been established as the reviewed one
    rather than the other way round.

    **The earlier root steps are not cases.** They are Band 0's discovery, Band
    2's provisioning, Band 3's `install`/`chattr` construction of the hierarchy
    and `P-01` … `P-04`: they establish the target and the case program rather
    than asserting what an identity could or could not do, and the plan
    attributes no evidence case to `E7` among them. Nor could an observation
    precede them — the case program does not exist until Band 3 installs it,
    which is the same reason `P-03`, `P-04` and `P-05` sit where they do rather
    than in Band 1. That is a judgement about scope; it is stated here and in the
    R13 handback rather than hidden behind the check.

    **The two bootstrap verbs are excluded, and the reason is a dependency, not a
    convenience — R16, conflict C-8.** `mkroot` creates the disposable root and
    `statroot` re-reads it at cleanup, and `P-06` runs `<root>/bin/case`, which
    does not exist until the root does. No ordering can put the observation
    first. What stands in its place is not an assumption:

    * `R-01` asserts uid 0 and gid 0 through `id`, as a Band 0 prerequisite,
      **before anything is constructed** — so the harness's identity is compared
      rather than assumed by the time this runs; and
    * `B3-02` reads the created directory's owner, group, mode and type back with
      `stat`. `mkdir(2)` gives the directory the creating process's uid and gid,
      so a root that comes back `0 0 755 directory` is evidence about the process
      that made it, taken from the object rather than from the process's own
      account of itself.

    Neither bootstrap verb asserts what an identity could or could not do, which
    is what the assertion contract governs: `mkroot`'s claim is that `mkdir`
    returned, and that claim is not a function of a capability set.
    """
    observations = [
        index
        for index, step in enumerate(steps)
        if step.capture is CapturePolicy.CASE_IDENTITY
        and step.identity_name == ROOT_IDENTITY_NAME
    ]
    if len(observations) != 1:
        raise PlanRefused(
            f"The plan carries {len(observations)} E7 identity observations. It "
            "carries exactly one: none would leave every root case attributed to "
            "an identity nothing checked — Blocking finding EH-R12-1 — and two "
            "would leave which of them a dependent operation depends on "
            "undecided."
        )
    first = observations[0]
    late = [
        step.step_id
        for index, step in enumerate(steps)
        if index < first
        and step.run_as == "root"
        and _case_program_verb(step.argv)
        not in ("", *OBSERVATION_VERBS, *BOOTSTRAP_VERBS)
    ]
    if late:
        raise PlanRefused(
            f"{late} run a case-program operation as root before the E7 identity "
            f"observation {steps[first].step_id!r}. An operation attributed to "
            "E7 that reaches the boundary before E7 has been observed is an "
            "operation whose attribution nothing established, which is exactly "
            "what EH-R12-1 found."
        )


def _validate_capability_experiment_ordering(steps: Sequence[CommandStep]) -> None:
    """**R16, conflict C-6.** Every constructed identity is observed first.

    §2.13.5c's assertion contract: *"Every case asserts its identity before it
    asserts its result … A case whose identity assertion fails is
    `inconclusive` — never a pass, never a refusal."* `_validate_root_identity_
    ordering` above asserts it for `E7`, whose observation is `P-06`. This
    asserts it for the identities `capsh` constructs, whose observations are Band
    5's `B5-E1 … B5-E8`.

    A step is *"run under"* a constructed identity when its vector is that
    identity's `capsh` construction. The band emits one identity observation per
    identity and then the experiments, so the check is an index comparison — and
    it is a check rather than a comment because the ordering is the whole reason
    an unexpected mask makes a case inconclusive instead of failed.
    """
    observed_at: dict[str, int] = {}
    for index, step in enumerate(steps):
        if step.capture is CapturePolicy.CASE_IDENTITY and step.identity_name:
            observed_at.setdefault(step.identity_name, index)
    for index, step in enumerate(steps):
        if step.capture is not CapturePolicy.CASE_RESULT:
            continue
        name = _constructed_identity_of(step.argv)
        if not name:
            continue
        first = observed_at.get(name)
        if first is None:
            raise PlanRefused(
                f"Step {step.step_id!r} runs an operation under {name}, and the "
                "plan carries no identity observation for it. An operation "
                "attributed to a constructed identity nothing observed is an "
                "operation whose attribution nothing established."
            )
        if index < first:
            raise PlanRefused(
                f"Step {step.step_id!r} runs an operation under {name} before "
                f"{steps[first].step_id!r} observed it. §2.13.5c requires the "
                "identity assertion to precede the result, so that an identity "
                "that is not what the plan says makes the case inconclusive "
                "rather than being discovered afterwards."
            )


def _constructed_identity_of(argv: Sequence[str]) -> str:
    """Which §2.13.5c identity a `capsh` construction builds, or the empty string.

    Read from the vector's own `--uid=`/`--groups=` options rather than from a
    field a step could fill in differently: the identity a step runs under is
    what its argument vector asks the kernel for.
    """
    if not argv or argv[0] != "/usr/sbin/capsh":
        return ""
    options = {
        argument.split("=", 1)[0]: argument.split("=", 1)[1]
        for argument in argv
        if argument.startswith("--") and "=" in argument
    }
    for name, identity in EVIDENCE_IDENTITIES.items():
        if name == ROOT_IDENTITY_NAME:
            continue
        wanted = ",".join((identity.primary_group, *identity.supplementary_groups))
        if (
            options.get("--uid") == identity.user
            and options.get("--gid") == identity.primary_group
            and options.get("--groups") == wanted
            and options.get("--inh", "")
            == ",".join(
                sorted(ALL_CAPABILITY_NAMES[bit] for bit in identity.capability_set)
            )
        ):
            return name
    return ""


def _case_program_verb(argv: Sequence[str]) -> str:
    """The verb a **direct** Option-B vector names, or the empty string.

    Positional, exactly as `case_runtime.validate_case_vector` reads it: the
    interpreter, its two isolation flags, the program, then the verb. A vector
    that is not a direct case-program vector — a distribution binary, or a
    `capsh` construction that execs one — has no verb of its own here, and the
    empty string says so. `capsh` vectors are not `E7`'s in any event: they
    assume another identity, which is the whole of what they are for.
    """
    verb_index = 1 + len(INTERPRETER_FLAGS) + 1
    if len(argv) <= verb_index or argv[0] != INTERPRETER_PATH:
        return ""
    return argv[verb_index]


def build_concrete_plan(target: DisposableTarget = APPROVED_TARGET) -> ConcretePlan:
    """Generate the whole thing against `target`, defaulting to the approved one.

    The parameter exists so the suite can prove a one-field deviation is refused
    downstream; it is not a way to point the harness at another host. The
    executor calls `approved_target.require_approved_target()` on whatever plan
    it is handed, so a plan built against anything else cannot be executed.
    """
    paths = _Paths(target.root_path)
    if paths.case_binary != case_program_path(target):
        raise PlanRefused(
            "The mutation list's case-program path and the path the reviewed "
            "case-program grammar admits are not the same string, so the plan "
            "would declare one object and run another."
        )
    mutations = build_mutations(target)

    steps = _Steps()
    _band_0(steps, target, paths, mutations)
    _band_1(steps)
    _band_2(steps, {m.mutation_id: m for m in mutations})
    _band_3(steps, target, paths, mutations)
    _band_4(steps, target, paths)
    _band_5(steps, target, paths)
    _band_6(steps, target, paths)
    _band_7(steps)
    _validate_root_identity_ordering(steps.steps)
    _validate_capability_experiment_ordering(steps.steps)
    # **R13, EH-R13-4.** Every required evidence case is produced by a step or
    # declared unresolved. A case that is in neither list is invisible to
    # `is_executable`, which is how two whole groups of required evidence came to
    # be absent from a plan that reported itself executable.
    check_case_coverage(
        produced=[
            case_id for step in steps.steps for case_id in step.evidence_case_ids
        ],
        declared_unresolved=[
            case_id for item in steps.unresolved for case_id in item.evidence_case_ids
        ],
        # **R16, EH-R16-4.** Only a contract whose producer artifact exists and
        # has been reviewed occupies the third column. Every Band-7 contract in
        # this plan is documentation of an input shape, so this list is empty and
        # the three cases stay in `declared_unresolved` where R16 requires them.
        supplied_externally=[
            item.case_id for item in steps.external_cases if item.resolves_coverage
        ],
    )

    execution_plan = ExecutionPlan(
        target=target,
        steps=tuple(steps.steps),
        mutations=mutations,
        materializations=tuple(steps.materializations),
    )
    cleanup_plan = CleanupPlan.for_mutations(target, mutations)
    return ConcretePlan(
        execution_plan=execution_plan,
        cleanup_plan=cleanup_plan,
        unresolved=tuple(steps.unresolved),
        external_cases=tuple(steps.external_cases),
    )


__all__ = [
    "BANDS",
    "COORDINATOR_ROLE",
    "CREATED_ACCOUNTS",
    "CREATED_GROUPS",
    "CREATED_MEMBERSHIPS",
    "ConcretePlan",
    "CAPTURED_CONFIGURATION",
    "CONFIGURATION_ROLE",
    "ExternalCase",
    "MAPPED_OS_USER",
    "MAPPED_POSTGRES_ROLE",
    "S4_3_CONFLICT",
    "S4_3_UNMET_PRODUCER_REQUIREMENTS",
    "TRANSIENT_UNIT",
    "UnresolvedStep",
    "build_concrete_plan",
    "build_mutations",
    "s4_3_dependency_gaps",
]
