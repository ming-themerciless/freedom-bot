"""Regression controls for the lost-pin operational reconciliation.

The procedure in §9 is the thing a human follows when a submission's outcome is
unknown, and getting it wrong produces a second pending artifact for one export.
So its load-bearing claims are asserted here rather than left to review.

**This file was rewritten for C-24.** The nine previous versions of §9 settled an
episode by *observing* that nothing was in flight — a probe, Caddy's in-flight
gauge, a stopped endpoint, a terminated ingress, a restart-vector inventory, a
commit watermark, a `pg_locks` queue reading, a drain read. Every one of them was
defeated by the same thing: an observation of a resource cannot exclude work that
has been accepted and has not yet reached it. §9 now closes the submitting
credential's **admission generation**, which is a transaction the application
checks inside every submission, and the withdrawn conditions are gone.

Two kinds of test therefore live here. The first kind asserts what the procedure
now says. The second kind asserts that the withdrawn conditions **stay**
withdrawn: each of them looked like a simplification when it was introduced, and
the cheapest way for this defect to come back is for one of them to be
reintroduced by someone who did not read why it went.
"""

from pathlib import Path


GUIDE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "operations"
    / "foundry-snapshot-submission.md"
)


def _guide() -> str:
    return GUIDE.read_text(encoding="utf-8")


def _lost_pin_procedure() -> str:
    return _guide().split(
        "#### Lost-pin reconciliation after an accidental reload", maxsplit=1
    )[1].split("Downloading is a fallback delivery channel", maxsplit=1)[0]


def _step(name: str) -> str:
    """One step of the procedure, from its heading to the next one."""
    procedure = _lost_pin_procedure()
    body = procedure.split(f"##### {name}", maxsplit=1)[1]
    return body.split("\n##### ", maxsplit=1)[0]


def _normalized(text: str) -> str:
    return " ".join(text.split())


# -- what the procedure now says ----------------------------------------------


def test_lost_pin_reconciliation_spans_the_whole_unresolved_episode():
    """Same-key retries are silent, so the window includes the first attempt."""
    normalized = _normalized(_lost_pin_procedure())

    assert "whole unresolved delivery episode" in normalized
    assert "replays the original receipt without writing a new audit event" in normalized
    assert (
        "The time window applies to the append-only event for the first "
        "submission of these pinned bytes" in normalized
    )
    assert "Do not send Actor data or a credential." in normalized


def test_settlement_is_closing_the_admission_generation():
    """Step 1 is a transaction against the database, not an outage.

    The single most important claim in the procedure: what an operator *does* to
    settle an episode.
    """
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert "tools.submission_admission" in step
    assert "close" in step
    assert "--principal" in step and "--operator" in step and "--reason" in step
    assert "Record the generation, the operator, the reason and the time" in step


def test_step_1_states_why_an_observation_could_never_have_worked():
    """The reason nine remediations failed, kept where the next author will read it."""
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert (
        "An observation of a resource cannot exclude work that has been accepted "
        "and has not yet reached it" in step
    )
    assert "pauses **before its first statement**" in step
    assert "it commits whenever it eventually wakes" in step


def test_step_1_names_the_three_facts_the_closure_rests_on():
    """Each is a property of the schema or of the check, not a claim about timing."""
    step = _normalized(_step("Step 1 — close the admission generation"))

    # The check is in the request's own transaction.
    assert "inside the request's own transaction" in step or (
        "The check is inside the request's own transaction" in step
    )
    assert "last statement before its commit" in step
    # The identity travels in the request's own bytes.
    assert "travels in its own bytes" in step
    assert 'never against "whichever generation is open now"' in step
    # One admission per credential, for all time.
    assert "at most one admission, ever" in step
    assert "unique in `submission_admissions` for all time" in step


def test_step_1_states_that_the_closure_and_an_acceptance_cannot_interleave():
    """Both orderings, because only both together exclude a false miss."""
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert "`KEY SHARE`" in step and "`FOR UPDATE`" in step
    assert "holds the closure off" in step
    assert "a hit, with no miss to record" in step
    assert "waits" in step and "rolls itself back" in step


def test_step_1_cites_the_postgresql_evidence_by_file():
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert "tests/test_submission_admission_postgresql.py" in step
    assert "real submission service and real transaction boundaries" in step


def test_the_endpoint_and_the_proxy_stay_up():
    """The downtime the previous nine versions cost is gone, and says so."""
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert "The endpoint stays up, and so does Caddy" in step
    assert "The fence is a transaction, not an outage" in step


def test_operational_readings_are_marked_as_diagnosis_and_never_as_evidence():
    """They are retained, and their status is stated where they appear.

    Deleting them would invite someone to re-derive them badly; leaving them
    unlabelled would invite someone to settle on one.
    """
    step = _step("Step 1 — close the admission generation")
    normalized = _normalized(step)

    assert "Diagnostic readings" in normalized
    assert "never for settling one" in normalized
    assert (
        "None of the following establishes anything, and no outcome below may "
        "cite one as evidence" in normalized
    )
    # The readings themselves are still here, so an operator investigating an odd
    # episode has them.
    assert "pg_stat_activity" in normalized
    assert "admission_closed" in normalized


def test_the_query_projects_the_admission_generation():
    """Which makes step 1 checkable afterwards rather than taken on trust."""
    step = _normalized(_step("Step 2 — the whole-episode acceptance-event query"))

    assert "admission_generation" in step
    assert (
        "no row here may name the generation step 1 closed with a timestamp "
        "after that closure committed" in step
    )


def test_a_miss_rests_on_the_closure_and_on_nothing_else():
    """The whole of the miss condition, and the absence of a second reading."""
    step = _normalized(_step("Step 3 — interpret the result"))

    assert "**Miss** — no row, **with step 1's closure committed and recorded**" in step
    assert "cannot come to record one afterwards" in step
    assert "There is no second reading to take, and no order to get right" in step
    assert "The closure is a state" in step


def test_a_repeated_query_is_for_operator_error_and_not_for_safety():
    step = _normalized(_step("Step 3 — interpret the result"))

    assert "only for **operator error**" in step
    assert "It is not what makes the miss safe. The closure is." in step


def test_an_unsettled_episode_is_an_incident_rather_than_a_miss():
    step = _normalized(_step("Step 3 — interpret the result"))

    assert "This is **not** a miss and not a hit" in step
    assert "Do not authorize a fresh export" in step
    assert "Escalate to the maintainer" in step
    # The specific ways step 1 can fail, each named.
    assert "`lock_timeout`" in step
    assert "could not reach the database" in step
    assert "holds **no** admission at all" in step


def test_a_lock_timeout_is_explained_as_a_probable_hit():
    """An operator meeting this needs to know it is good news, not a fault."""
    step = _normalized(_step("Step 3 — interpret the result"))

    assert "A `lock_timeout` is the good case" in step
    assert "resolve as a **hit**" in step


def test_every_outcome_reopens_submission_deliberately_or_leaves_it_closed():
    """Step 1 closes submission for every episode, so step 4 must address it."""
    step = _normalized(_step("Step 4 — reopen submission, on the terms the outcome chooses"))

    assert "`403 admission_closed`" in step
    for outcome in ("**Miss**", "**Hit**", "**Ambiguous**"):
        assert outcome in step, outcome
    assert "a new credential and a new generation, given to the GM" in step
    assert "nothing; submission stays closed" in step


def test_recovery_issues_a_new_credential_rather_than_reopening_the_old_one():
    """The control that stops an old request being silently readmitted."""
    step = _normalized(_step("Step 4 — reopen submission, on the terms the outcome chooses"))

    assert "It cannot reopen it" in step
    assert "a trigger refuses the reverse and refuses `DELETE`" in step
    assert "unique for all time" in step
    assert "`foundry-the-guild-r1`" in step


def test_the_miss_branch_still_confirms_what_happened_next():
    """Detection did not stop being worth having when prevention improved."""
    step = _normalized(_step("Step 4 — reopen submission, on the terms the outcome chooses"))

    assert "Run step 2's query again with the window widened" in step
    assert "Expect exactly one acceptance event" in step
    assert "escalate to the maintainer as a **defect in the fence**" in step


def test_route_retirement_is_demoted_to_hygiene_and_says_so():
    """It used to be the only control. It no longer is, and the change is stated."""
    step = _normalized(_step("Step 4 — reopen submission, on the terms the outcome chooses"))

    assert "Retiring the route is no longer required" in step
    assert "this is a change from the previous version" in step
    assert "**hygiene, not a control**" in step


def test_no_branch_of_step_4_stops_or_restarts_anything():
    """The downtime window is gone, not merely shortened."""
    step = _step("Step 4 — reopen submission, on the terms the outcome chooses")
    normalized = _normalized(step)

    assert "No episode takes the site down" in normalized
    for withdrawn in ("systemctl stop", "systemctl start caddy", "restart the endpoint"):
        assert withdrawn not in step, withdrawn


# -- what the settlement argument claims --------------------------------------


def test_the_settlement_argument_states_what_it_does_and_does_not_depend_on():
    rests = _guide().split("##### What settlement rests on", maxsplit=1)[1]
    normalized = _normalized(rests)

    assert "Settlement rests on four things" in normalized
    assert "What settlement no longer rests on" in normalized
    # The dependencies that are gone, named individually so none creeps back in
    # as an unstated assumption.
    for gone in (
        "whether the endpoint is running",
        "whether Caddy is running",
        "what `pg_stat_activity` shows",
        "whether a commit watermark moved",
        "whether a lock queue was empty",
        "whether a drain read matched",
    ):
        assert gone in normalized, gone


def test_the_settlement_argument_states_how_it_could_stop_holding():
    """Three named ways, each a code or schema change with a regression test."""
    rests = _normalized(_guide().split("##### What settlement rests on", maxsplit=1)[1])

    assert "When it stops holding" in rests
    assert "foreign key on `idempotency_keys.admission_id` is removed" in rests
    assert "moved out of the acceptance transaction" in rests
    assert "Each has a named regression test" in rests


def test_the_measured_postgresql_trap_is_recorded_rather_than_assumed():
    """A plain UPDATE does not conflict, and a closure written that way fences nothing."""
    rests = _normalized(_guide().split("##### What settlement rests on", maxsplit=1)[1])

    assert "`FOR NO KEY UPDATE`" in rests
    assert "does *not* conflict with `KEY SHARE`" in rests
    assert "takes `FOR UPDATE` first" in rests


def test_the_phase_3_obligation_is_discharged_rather_than_carried():
    """The previous version promised this mechanism for Phase 3. It is here."""
    rests = _normalized(_guide().split("##### What settlement rests on", maxsplit=1)[1])

    assert "Phase 3 obligation" in rests
    assert "discharged by this one" in rests
    assert "no downtime" in rests


def test_what_remains_unobserved_is_stated():
    """No operator has followed this version yet, and the document says so."""
    rests = _normalized(_guide().split("##### What settlement rests on", maxsplit=1)[1])

    assert "What remains unobserved" in rests
    assert "No operator has yet followed this procedure end to end on production" in rests


# -- the withdrawn conditions stay withdrawn ----------------------------------


def test_no_withdrawn_observation_is_used_as_a_settlement_condition():
    """The nine defeated conditions, each absent from the procedure as evidence.

    They are still *named* in prose — step 1 explains why each went, and that
    explanation is what stops one coming back. What none of them may be is
    something an operator **runs**. So this reads the commands rather than the
    words: every fenced block in the procedure, minus the one explicitly headed
    as diagnostic.
    """
    procedure = _lost_pin_procedure()
    settling = procedure.split("###### Diagnostic readings", maxsplit=1)[0]
    commands = "\n".join(settling.split("```")[1::2])

    for withdrawn in (
        "LOCK TABLE",
        "pg_locks",
        "pg_stat_clear_snapshot",
        "systemctl stop",
        "systemctl start",
        "caddy_http_requests_in_flight",
        "lstart",
        "pg_stat_activity",
    ):
        assert withdrawn not in commands, withdrawn

    # And the one command that does settle an episode is there.
    assert "tools.submission_admission" in commands


def test_the_withdrawn_conditions_are_named_with_the_reason_they_failed():
    """Named, so that none of them returns as an apparent simplification."""
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert "What settlement no longer requires" in step
    for withdrawn in (
        "S-A's endpoint stop",
        "S-I's ingress termination",
        "S-D.2's commit watermark",
        "S-D.3's",
        "S-D.4's",
    ):
        assert withdrawn in step, withdrawn
    assert "They are not weakened here — they are **replaced**" in step
    assert "not one of them could exclude a request that had not yet arrived" in step


def test_the_c_23_drain_sequence_is_recorded_as_the_defect_it_was():
    """The exact sequence the reviewer gave, kept as the reason for the rewrite."""
    step = _normalized(_step("Step 1 — close the admission generation"))

    assert "queues behind the drain" in step
    assert "the drain reading is taken before that writer can commit, so it matches" in step
    assert "the miss has already authorized a fresh export with a different checksum" in step


def test_the_ingress_no_longer_has_to_be_terminable():
    """§5.4's requirement is demoted, explicitly, where it was stated."""
    normalized = _normalized(_guide())

    assert "The ingress no longer has to be terminable" in normalized
    assert "§9 no longer depends on it" in normalized
    assert (
        "a hop that cannot be stopped from here is no longer a reason to revisit it"
        in normalized
    )


def test_the_no_upstream_retry_window_requirement_survives_without_being_load_bearing():
    normalized = _normalized(_guide())

    assert "No upstream retry window" in normalized
    assert "it is not what makes one safe now" in normalized
    assert "refused by the fence" in normalized


# -- the deployment and rotation consequences ---------------------------------


def test_a_credential_is_documented_as_needing_a_generation_too():
    """The state between running the migration and opening a generation."""
    normalized = _normalized(_guide())

    assert "A credential is not enough on its own" in normalized
    assert (
        "A credential with no generation authenticates and is then refused "
        "`403 admission_closed`" in normalized
    )
    assert "tools.submission_admission open" in normalized


def test_a_principal_id_is_documented_as_spent_once_its_generation_closes():
    normalized = _normalized(_guide())

    assert "A principal id may hold at most one generation, ever" in normalized
    assert "every reissue takes a new one" in normalized


def test_revocation_is_documented_as_reaching_only_unauthenticated_requests():
    """The reason closing the generation is the decisive half of a revocation."""
    normalized = _normalized(_guide())

    assert "Rotation opens a new generation; revocation should close the old one" in normalized
    assert (
        "A request that authenticated before the reload and is paused somewhere"
        in normalized
    )
    assert "Closing is the decisive half" in normalized


def test_the_rehearsal_no_longer_expects_host_wide_downtime():
    """Rehearsal A's step 10 followed the withdrawn procedure."""
    normalized = _normalized(_guide())

    assert "Nothing is stopped: the endpoint keeps serving" in normalized
    assert (
        "An earlier version of this rehearsal stopped the endpoint and terminated "
        "Caddy here" in normalized
    )
