"""`JNL-51` and `JNL-53`: reviewed-source provenance, and the refusal that
security-review finding **P5.0-SR1** says was missing.

§2.12.5a's contract in one sentence: *a deployment is admissible only when three
facts from three different sources agree, and a generation is registrable only
when a fourth, in PostgreSQL, agrees with them.*

| | Fact | Source | Why it is independent |
|---|---|---|---|
| `APR` | the approved revision | `/etc/freedom-blades/approved-source-revision`, `root:root 0444`, installed out of band | not derived from any deployed byte and not from the object store |
| `TM` | the trusted manifest | the bare `…/coordinator/source.git`, `root:root 0700`, addressed **by object id only** | Git objects are content-addressed and the store is unreachable by every non-root identity |
| `SM` | the deployed source manifest | the live installed bytes | it is the reality the writer will actually execute |
| `ASR` | the approved-revision row | PostgreSQL, inserted under **A8**, append-only under **A9** | it is the one copy an actor holding only host authority did not write |

**The case this module exists for is the missing one.** `JNL-51` case (g): the
provenance step is omitted — `D8` suppressed, or `PVR` deleted after a successful
deployment. `init-generation` must then refuse at **C0** with `J-26`, leave no
journal file, no seal, no `current` symlink, no `.close` manifest and no row, and
the probe must never have run. *"An absent or unreadable approval record is a
refusal, never a default — that is the whole of what P5.0-SR1 says was missing."*

`classify_missing_provenance()` is that case. **R16, EH-R16-2:** the absence of
`APR`/`PVR` is the case's *precondition* — the situation the producer arranged —
and the refusal the program reported is a **separate observation** the caller
supplies. The expectation is this module's own `EXPECTED_OMISSION_REFUSAL`
constant and comes from nowhere else, so an observed `DEP-04`, or an observed
admission, is failed evidence rather than a differently expected result.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .errors import ObservationRefused
from .records import CaseRole, CleanupState, EvidenceRecord, Outcome, Status

BAND = "provenance"

#: Algorithm D's refusal family. It belongs to the deploy step alone — it is
#: neither the writer's `SW-Jxx` family nor the coordinator's `J-xx` family,
#: because the deploy step is neither actor.
DEPLOY_REFUSALS: Mapping[str, str] = {
    "DEP-01": "APR absent, unreadable, wrongly owned, wrongly moded, structurally "
              "invalid, or for a different component",
    "DEP-02": "the object store is not bare root:root 0700, or does not hold "
              "APR.source_commit as a commit object",
    "DEP-03": "the commit's root tree id does not equal APR.source_tree_id",
    "DEP-04": "TM recomputed from the object bytes does not equal "
              "APR.source_manifest_digest",
    "DEP-05": "a region-D distribution artifact digest is not the lock's, or a "
              "distribution is extra or missing",
    "DEP-06": "the staging tree's file set is not exactly region S ∪ region D",
    "DEP-07": "the deployment map's owner, group or mode could not be applied",
    "DEP-08": "SM does not equal TM, or a uid, gid or mode does not equal the map's",
    "DEP-09": "PVR could not be written; the deployment is rolled back, because "
              "there is no deployed state without a provenance record",
}

#: The three fail-closed conditions revision 12 adds, one per consumer.
CONSUMER_REFUSALS: Mapping[str, str] = {
    "J-26": "init-generation C0, or the coordinator at observe: PVR or APR absent, "
            "malformed, wrongly owned, wrongly moded, or disagreeing",
    "J-27": "the writer at W11a, or the coordinator at C-a/C-d: the deployed bytes "
            "do not match the sealed source manifest",
    "J-28": "V-R at registration: no approved_source_revisions row matches, and the "
            "NOT NULL foreign key refuses the same insert issued directly as SQL",
    "SW-J26": "the writer's own W11a refusal on PVR",
    "SW-J27": "the writer's own W11a refusal on the deployed bytes",
}


@dataclass(frozen=True, slots=True)
class FileFacts:
    """Ownership and mode, which is the whole of `APR`'s integrity — residual
    **R-5.0-15**, recorded as a residual and not described as a refusal."""

    present: bool
    owner: str = ""
    group: str = ""
    mode: str = ""

    @property
    def is_root_owned_read_only(self) -> bool:
        return self.present and self.owner == "root" and self.group == "root" and self.mode == "0444"


@dataclass(frozen=True, slots=True)
class ApprovedRevision:
    """`APR`: the only place a human's *approval* enters the algorithm."""

    component: str
    source_commit: str
    source_tree_id: str
    source_manifest_digest: str
    review_reference: str
    approved_by: str
    approved_at: str
    facts: FileFacts


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """`PVR`, written at **D8**, and deliberately **outside** the deployed root so
    no digest covers a file containing its own value."""

    component: str
    source_commit: str
    source_tree_id: str
    source_manifest_digest: str
    deployment_manifest_digest: str
    dependency_lock_digest: str
    deployed_at: str
    deployed_by: str
    facts: FileFacts


#: The refusal `init-generation` must report at **C0** when the provenance step
#: was omitted. It is stated here, from §2.12.5a, and it is the **only** place
#: this case's expectation comes from: no caller supplies it and no observation
#: reaches it.
EXPECTED_OMISSION_REFUSAL = "J-26"

#: What the observed side of the refusal record says when the program did not
#: refuse at all. It is a value the comparison can fail against, rather than an
#: absence the classifier has to interpret.
OBSERVED_ADMITTED = "admitted; no refusal was reported"

#: What it says when the situation the case is about did not obtain — neither
#: `APR` nor `PVR` was absent. The case **is** the omission, so a run in which
#: nothing was omitted is evidence of a different situation and can never be
#: this case passing, whatever the program then did.
OBSERVED_PRECONDITION_UNMET = (
    "the precondition did not hold: neither APR nor PVR was absent"
)


def classify_missing_provenance(
    *,
    apr: ApprovedRevision | None,
    pvr: ProvenanceRecord | None,
    probe_ran: bool,
    generation_artifacts: Sequence[str],
    generation_row_inserted: bool,
    observed_refusal_code: str | None,
) -> tuple[EvidenceRecord, ...]:
    """`JNL-51` case (g) — the negative test P5.0-SR1 requires.

    Four assertions, and every one of them is about something that must **not**
    have happened: `init-generation` refuses at **C0** with `J-26`; no journal
    file, seal, `current` symlink or `.close` manifest exists; no row was
    inserted; and the probe never ran. Only when all four hold has the omission
    been shown to prevent activation rather than merely to be noticed.

    ## Blocking finding EH-R16-1's sibling, **EH-R16-2**

    R16 found the first record constructing its **observed** value from
    `bool(absent)` — that is, from whether `APR` or `PVR` was missing. That is
    the *experimental input*: it is the situation the producer arranged, and it
    says nothing whatever about what `init-generation` then did. A payload that
    reported an observed `DEP-04` was classified `passed` with an observed value
    of `refused J-26`, so the artifact contradicted the evidence it was built
    from.

    `observed_refusal_code` is therefore a **required** keyword with no default:

    * a refusal code — the code the producer observed the program report. It is
      compared with `EXPECTED_OMISSION_REFUSAL`, which comes from this module's
      own constant and from nowhere a caller can reach;
    * `None` — the program did **not** refuse. That is recorded explicitly as
      `OBSERVED_ADMITTED` rather than as a missing value, because *"it admitted"*
      is a result and not an absence of one.

    The absence of `APR`/`PVR` keeps the role it actually has: it is the
    **precondition**. When it does not hold the observed value says so, and the
    record fails — a refusal observed in a run where nothing was omitted is a
    refusal for some other reason.
    """
    absent = [
        name
        for name, record in (("APR", apr), ("PVR", pvr))
        if record is None or not record.facts.present
    ]
    if observed_refusal_code is not None and not str(observed_refusal_code).strip():
        raise ObservationRefused(
            "The observed refusal code is either a code the producer reported or "
            "None, meaning the program did not refuse. Blank is neither, and "
            "reading it as either is how an unmade observation becomes a result."
        )
    if not absent:
        observed_refusal = OBSERVED_PRECONDITION_UNMET
    elif observed_refusal_code is None:
        observed_refusal = OBSERVED_ADMITTED
    else:
        observed_refusal = f"refused {observed_refusal_code}"
    return (
        EvidenceRecord.for_case(
            case_id="JNL-51-g-refusal",
            band=BAND,
            target_identity="root, at init-generation C0",
            operation="read PVR and APR before any persistent artifact exists",
            preconditions=("D8 was suppressed, or PVR was deleted after a "
                           "successful deployment",),
            expected=Outcome.read(f"refused {EXPECTED_OMISSION_REFUSAL}"),
            observed=Outcome.read(observed_refusal),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "absent_records": ",".join(absent) or "—",
                # The expected code, named as such. It is this module's constant.
                "refusal_code": EXPECTED_OMISSION_REFUSAL,
                # **EH-R16-2.** The result the producer actually observed, kept in
                # the persisted record beside the expectation it was compared
                # with. `none` is the program having admitted; it is a value
                # rather than a blank, so a reader cannot mistake it for a field
                # nobody filled in.
                "observed_refusal_code": (
                    "none" if observed_refusal_code is None else observed_refusal_code
                ),
                "precondition_holds": "yes" if absent else "no",
                "note": "An absent or unreadable approval record is a refusal, "
                        "never a default. That is the whole of what P5.0-SR1 says "
                        "was missing. The absence is the precondition; the "
                        "refusal code above is what the program was observed to "
                        "do, and the two are compared rather than conflated.",
            },
        ),
        EvidenceRecord.for_case(
            case_id="JNL-51-g-no-artifact",
            band=BAND,
            target_identity="the journal hierarchy",
            operation="list …/journal after the refusal",
            preconditions=("nothing under …/journal is created before C5",),
            expected=Outcome.read("no journal, seal, current symlink or .close manifest"),
            observed=Outcome.read(
                "no journal, seal, current symlink or .close manifest"
                if not generation_artifacts
                else ",".join(sorted(generation_artifacts))
            ),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.CLEAN if not generation_artifacts else CleanupState.RESIDUE,
            detail={"artifact_count": len(generation_artifacts)},
        ),
        EvidenceRecord.for_case(
            case_id="JNL-51-g-no-row",
            band=BAND,
            target_identity="sheet_writer_journal_generations",
            operation="select for a generation row after the refusal",
            preconditions=("no row is inserted before C13",),
            expected=Outcome.read("no row"),
            observed=Outcome.read("a row exists" if generation_row_inserted else "no row"),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "note": "So an unprovenanced deployment cannot reach activation at "
                        "all, and the refusal is a schema constraint rather than a "
                        "procedure step.",
            },
        ),
        EvidenceRecord.for_case(
            case_id="JNL-51-g-probe-never-ran",
            band=BAND,
            target_identity="verify-capability",
            operation="assert by syscall trace that the probe stages never ran",
            preconditions=("C0 precedes C1, and C0 refused",),
            expected=Outcome.read("not invoked"),
            observed=Outcome.read("invoked" if probe_ran else "not invoked"),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={},
        ),
    )


def classify_provenance_agreement(
    *,
    apr: ApprovedRevision,
    pvr: ProvenanceRecord,
    trusted_manifest_digest: str,
    deployed_manifest_digest: str,
    deployment_digest: str,
    approved_source_revision_row: bool,
) -> tuple[EvidenceRecord, ...]:
    """**C0**'s four-way comparison, one record per source.

    `APR`, `TM` and `SM` must be equal at deployment and again at every
    `init-generation`; `ASR` must exist and agree at registration. **Any
    disagreement, and any absence, is a refusal.**
    """
    records = [
        EvidenceRecord.for_case(
            case_id="JNL-53-J26-apr-facts",
            band=BAND,
            target_identity="root, at C0",
            operation="stat /etc/freedom-blades/approved-source-revision",
            preconditions=("APR is installed out of band by root",),
            expected=Outcome.read("root:root 0444"),
            observed=Outcome.read(
                "root:root 0444"
                if apr.facts.is_root_owned_read_only
                else f"{apr.facts.owner}:{apr.facts.group} {apr.facts.mode or 'absent'}"
            ),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "refusal_code": "DEP-01",
                "residual": "R-5.0-15 — APR's integrity is root ownership and mode, "
                            "not a signature. Recorded as a residual, not described "
                            "as a refusal.",
            },
        ),
        EvidenceRecord.for_case(
            case_id="JNL-53-J26-pvr-agrees",
            band=BAND,
            target_identity="root, at C0",
            operation="compare PVR's three provenance values with APR's",
            preconditions=("both records are present and root-owned",),
            expected=Outcome.read(
                f"{apr.source_commit}/{apr.source_tree_id}/{apr.source_manifest_digest}"
            ),
            observed=Outcome.read(
                f"{pvr.source_commit}/{pvr.source_tree_id}/{pvr.source_manifest_digest}"
            ),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={"refusal_code": "J-26"},
        ),
        EvidenceRecord.for_case(
            case_id="JNL-53-J26-tm-recomputed",
            band=BAND,
            target_identity="root, at C0",
            operation="recompute TM from the object store",
            preconditions=("the store is bare, root:root 0700, addressed by object id",),
            expected=Outcome.read(apr.source_manifest_digest),
            observed=Outcome.read(trusted_manifest_digest),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={"refusal_code": "DEP-04"},
        ),
        EvidenceRecord.for_case(
            case_id="JNL-53-J27-sm-recomputed",
            band=BAND,
            target_identity="the writer, at W11a",
            operation="recompute SM over the live deployed bytes",
            preconditions=("the writer cannot read the object store: it is 0700",),
            expected=Outcome.read(apr.source_manifest_digest),
            observed=Outcome.read(deployed_manifest_digest),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "refusal_code": "SW-J27",
                "note": "The writer establishes that its own deployed bytes match "
                        "the sealed source manifest, and cannot establish that the "
                        "manifest came from the approved commit's Git objects.",
            },
        ),
        EvidenceRecord.for_case(
            case_id="JNL-53-J26-dd-agrees",
            band=BAND,
            target_identity="root, at C0",
            operation="compare PVR.deployment_manifest_digest with the DD C0 computes",
            preconditions=("PVR lives outside the deployed root, so no digest covers "
                           "a file containing its own value",),
            expected=Outcome.read(deployment_digest),
            observed=Outcome.read(pvr.deployment_manifest_digest),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={"refusal_code": "J-26"},
        ),
        EvidenceRecord.for_case(
            case_id="JNL-53-J28-registration",
            band=BAND,
            target_identity="the coordinator, at V-R",
            operation=(
                "look up (component, source_commit, source_tree_id, "
                "source_manifest_digest) in approved_source_revisions"
            ),
            preconditions=(
                "the generation row carries a NOT NULL foreign key to that row",
                "the same INSERT is issued directly as SQL under both the "
                "coordinator role and the schema owner",
            ),
            expected=Outcome.read("a matching row exists"),
            observed=Outcome.read(
                "a matching row exists" if approved_source_revision_row else "no matching row"
            ),
            case_role=CaseRole.STANDALONE,
            cleanup_state=CleanupState.NOT_APPLICABLE,
            detail={
                "refusal_code": "J-28",
                "note": "An A5 holder can make every host copy agree and still "
                        "cannot register the generation, because the row it needs "
                        "is in PostgreSQL. A5 + A8 together is R-5.0-15, which is "
                        "operator trust rather than a technical control.",
            },
        ),
    ]
    return tuple(records)


def classify_worktree_isolation(opened_paths: Sequence[str]) -> EvidenceRecord:
    """`JNL-51` case (h): the deploy path opens no file under the worktree.

    §2.12.5a does not fix **H-1** and says so: *"The worktree stays
    group-writable; what changes is that nothing in the deploy path reads it."*
    This asserts that by syscall trace rather than by inspection.
    """
    from .targets import REPOSITORY_ROOT

    offending = tuple(
        sorted(path for path in opened_paths if path.startswith(REPOSITORY_ROOT))
    )
    return EvidenceRecord.for_case(
        case_id="JNL-51-h",
        band=BAND,
        target_identity="root, running Algorithm D",
        operation="syscall trace of a complete deployment, filtered to open()",
        preconditions=("H-1: the worktree is group-writable by discordbot and "
                       "freedomweb",),
        expected=Outcome.read(f"no path under {REPOSITORY_ROOT} opened"),
        observed=Outcome.read(
            f"no path under {REPOSITORY_ROOT} opened"
            if not offending
            else f"{len(offending)} worktree paths opened"
        ),
        case_role=CaseRole.STANDALONE,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail={
            "first_offending_path": offending[0] if offending else None,
            "note": "What discordbot and freedomweb can corrupt is no longer an "
                    "input to a deployment. That the repository is writable by a "
                    "service identity at all remains D5.0-12 / OD-65.",
        },
    )


def provenance_holds(records: Sequence[EvidenceRecord]) -> bool:
    """Every provenance record passed. Used where the design says activation is
    unreachable without it."""
    band = [record for record in records if record.band == BAND]
    return bool(band) and all(record.status is Status.PASSED for record in band)


__all__ = [
    "BAND",
    "CONSUMER_REFUSALS",
    "DEPLOY_REFUSALS",
    "EXPECTED_OMISSION_REFUSAL",
    "OBSERVED_ADMITTED",
    "OBSERVED_PRECONDITION_UNMET",
    "ApprovedRevision",
    "FileFacts",
    "ProvenanceRecord",
    "classify_missing_provenance",
    "classify_provenance_agreement",
    "classify_worktree_isolation",
    "provenance_holds",
]
