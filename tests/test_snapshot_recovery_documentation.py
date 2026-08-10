"""Regression controls for the lost-pin operational reconciliation."""

from pathlib import Path


GUIDE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "operations"
    / "foundry-snapshot-submission.md"
)


def _lost_pin_procedure() -> str:
    text = GUIDE.read_text(encoding="utf-8")
    return text.split(
        "#### Lost-pin reconciliation after an accidental reload", maxsplit=1
    )[1].split("Downloading is a fallback delivery channel", maxsplit=1)[0]


def test_lost_pin_reconciliation_spans_the_whole_unresolved_episode():
    """Same-key retries are silent, so the window includes the first attempt."""
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    assert "FROM audit_events AS a" in procedure
    assert "JOIN foundry_snapshots AS s ON s.checksum = a.entity_id" in procedure
    assert "a.action = 'snapshot_submission.accepted'" in procedure
    assert "a.payload->>'world_id' = 'the-guild'" in procedure
    assert "a.occurred_at >=" in procedure
    assert "a.occurred_at <=" in procedure
    assert "s.received_at >=" not in procedure
    assert "s.received_at <=" not in procedure
    assert "a.payload->>'duplicate' AS duplicate" in procedure
    assert "whole unresolved delivery episode" in normalized
    assert "from the first submission" in normalized
    assert "same idempotency key" in normalized
    assert "without writing a new audit event" in normalized
    assert "`duplicate = false`" in normalized


def _miss_rule() -> str:
    procedure = _lost_pin_procedure()
    return " ".join(
        procedure.split("- **Miss**", maxsplit=1)[1]
        .split("- **Ambiguous**", maxsplit=1)[0]
        .split()
    )


def test_lost_pin_miss_requires_the_duplicate_safe_query_to_be_repeated():
    miss_rule = _miss_rule()

    assert "whole-episode audit-event query repeated once" in miss_rule
    assert "accepted pending snapshot during that episode" in miss_rule
    assert "Only then may the operator authorize" in miss_rule


def test_lost_pin_miss_requires_settlement_and_not_merely_a_repeat():
    """B-1: a client timeout does not establish that the server stopped.

    The repeat survives, for operator error. What it may no longer be is the
    thing that makes the miss safe — two queries moments apart are two
    observations of the same still-open transaction.
    """
    miss_rule = _miss_rule()

    assert "settlement established and recorded" in miss_rule
    assert "Two misses without settlement are not a miss." in miss_rule


def test_the_settlement_step_states_a_positive_server_side_condition():
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    # The defect, named, so it cannot be reintroduced as an oversight.
    assert "A client timeout is not evidence that the server stopped" in normalized
    assert "repeating it does not help" in normalized

    # Settlement is established before any result is interpreted…
    assert "Step 1 — establish settlement, before reading any query result" in procedure
    # …by one condition, which is a state of the whole path rather than a sample,
    # and rather than a state of the endpoint alone.
    assert (
        "There is exactly one way to establish it: **nothing on that path is "
        "running, and none of it runs again until the outcome has been "
        "recorded.**" in normalized
    )
    assert "S-A — the endpoint is not running" in normalized
    assert "An exited process commits nothing" in normalized
    # …in two recorded parts for the endpoint: gone, and unserved.
    assert "S-A.1 — the process that served the episode is gone" in normalized
    assert "S-A.2 — nothing is listening now" in normalized
    assert "ss -ltn '( sport = :8757 )'" in procedure
    # A replacement process is not settlement: the proxy can still reach it.
    assert (
        "A *replacement* process is not good enough, and this corrects an "
        "earlier version of this step which accepted one." in normalized
    )
    # …corroborated by the database showing no work in flight.
    assert "pg_stat_activity" in procedure
    assert "idle in transaction" in procedure
    # The argument, stated as what it is: acceptance is required to commit.
    assert (
        "Every commit on this path begins with an accept" in normalized
    )
    assert "Both halves are states rather than samples" in normalized


def test_settlement_terminates_the_ingress_and_not_only_the_endpoint():
    """B-1, fourth remediation: the proxy is terminated too.

    A request the proxy has accepted and not yet dialled upstream for is the one
    an unserved port does not dispose of. S-I is what ends it, and it is a state
    of the same kind as S-A — a process that does not exist — rather than an
    observation of what a running proxy is holding.
    """
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    assert "S-I — the ingress in front of it is terminated, not drained" in normalized
    assert "S-I.1 — no Caddy process exists" in normalized
    assert "S-I.2 — nothing is listening on the public ports" in normalized
    assert "S-I.3 — nothing will bring either of them back" in normalized
    assert "S-I.4 — confirmed from off the host" in normalized

    # Terminated, not reloaded and not drained.
    assert "sudo systemctl stop caddy" in procedure
    assert "ps -o pid,lstart,args -C caddy" in procedure
    assert "systemctl is-active caddy" in procedure
    # Both protocols: HTTP/3 is a UDP listener.
    assert "ss -ltn '( sport = :80 or sport = :443 )'" in procedure
    assert "ss -lun '( sport = :443 )'" in procedure
    assert "**Being asked to shut down is not having shut down.**" in normalized
    # Measured, not cautioned: the two checks do not come true in written order,
    # and both measurements are carried because either one alone misleads.
    assert "**S-I.2 passing is not evidence for S-I.1**" in normalized
    assert "| production | nothing in flight | 4 ms | 4 ms |" in procedure
    assert (
        "| **production** | **one request, accepted and unrouted** | **0.5 ms** "
        "| **4.3 s** |" in procedure
    )
    assert (
        "| isolated rig | one request, accepted and unrouted | immediate | 5.4 s |"
        in procedure
    )
    assert (
        "**The delay is a function of what the proxy is holding, not a fixed "
        "cost of stopping it**" in normalized
    )
    # …and the reason that matters here specifically.
    assert (
        "**A rehearsal on an idle host teaches the wrong expectation.**"
        in normalized
    )
    assert (
        "So read `ps` until it is empty, and read it last." in normalized
    )
    assert "they come apart by seconds" in normalized
    # The other half of S-I, observed rather than argued.
    assert (
        "**the connection closed with nothing delivered.**" in normalized
    )

    # The 502 confirmation is not merely withdrawn, it is inverted.
    assert "**A `502` or `503` is now a failure of this check**" in normalized
    assert "receiving one means Caddy is running" in normalized

    # The cost is stated where the operator meets it, not only in the record.
    assert (
        "**This is host-wide downtime, and it is the maintainer's to authorize.**"
        in normalized
    )

    # Duration covers both, and hands the restart to step 4.
    assert "S-D — all of it stays down until the outcome is recorded" in normalized


def test_the_withdrawn_settlement_conditions_are_named_with_their_defects():
    """B-1, third remediation: neither a probe nor Caddy's gauge is a drain.

    Both tried to settle the question against a running endpoint, and neither
    could establish that nothing would arrive later. They are named here so that
    neither returns as an apparent simplification.
    """
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    assert "Why there is only one condition" in procedure
    assert (
        "a running endpoint can still be handed a request the operator cannot see"
        in normalized
    )

    # The probe: it settles only what was already accepted.
    assert "**A probe is not a drain.**" in normalized
    assert (
        "Issuing the probe late does not make the endpoint accept it late."
        in normalized
    )

    # The gauge: Caddy's documented meaning, and what it therefore excludes.
    assert "**Caddy's in-flight gauge is not a drain either.**" in normalized
    assert "caddy_http_requests_in_flight" in procedure
    assert "requests *currently being handled*" in normalized
    assert (
        "That excludes a connection Caddy has accepted whose request has not "
        "entered the instrumented handler" in normalized
    )
    assert (
        "body bytes still arriving over an established HTTP/1.1, HTTP/2 or "
        "HTTP/3 connection" in normalized
    )
    assert "two samples, not one atomic drain" in normalized
    assert (
        "Closing or reloading the Foundry page does not establish that "
        "everything the browser already transmitted has been consumed" in normalized
    )

    # …and why the database check cannot stand in for either of them.
    assert (
        "A request that has not reached the application has no backend to be "
        "`active` or `idle in transaction`." in normalized
    )

    # Withdrawn, not merely discouraged.
    assert (
        "a settlement recorded from either is not a settlement" in normalized
    )

    # And the third: a state, but scoped to the endpoint alone.
    assert "**Stopping the endpoint is not terminating the path.**" in normalized
    assert (
        "one the proxy has accepted, or is still reading, and has **not yet "
        "dialled upstream for**" in normalized
    )
    assert (
        "that rule is about a *retry* after a refused dial, and this is a "
        "**first** dial that has not happened yet" in normalized
    )
    assert "Detecting it is not preventing it" in normalized
    assert (
        "Stopping the endpoint alone is not that, and the version of this step "
        "before this one thought it was." in normalized
    )


def test_the_ingress_must_be_terminable_and_hold_no_retry_window():
    """§9 depends on both, and §5.4 is where they are recorded.

    S-I stops the proxy, so the path has to be one the operator can stop. The
    retry-window requirement survives, but §5.4 now says what it does *not* buy:
    an earlier §9 leaned on it to cover a request that had never dialled upstream
    at all. The in-flight gauge is still disclaimed here, in the section that
    used to require it.
    """
    proxy = (
        GUIDE.read_text(encoding="utf-8")
        .split("### 5.4", maxsplit=1)[1]
        .split("\n#### ", maxsplit=1)[0]
    )
    normalized = " ".join(proxy.split())

    # The requirement S-I introduces: a path that can be terminated from here.
    assert (
        "**The ingress must be terminable, and §9 depends on that.**" in normalized
    )
    assert (
        "one proxy, on this host, under a supervisor the operator can stop"
        in normalized
    )
    assert (
        "§9's step 1 must be revisited with it before the next reconciliation"
        in normalized
    )

    # The retry window, kept, and bounded to what it actually governs.
    assert "**No upstream retry window.**" in normalized
    assert "lb_try_duration" in proxy
    assert (
        "It governs a **retry after a refused attempt**. It says nothing about a "
        "request the proxy has accepted and has **not yet dialled upstream for "
        "at all**" in normalized
    )
    assert (
        "Only terminating the proxy disposes of that request" in normalized
    )

    # …and the route retirement step 4 performs is pointed at from here.
    assert "**§9's recovery route.**" in normalized
    assert "Restore this block when the episode closes" in normalized

    # The gauge is no longer required, and no longer evidence.
    assert "**Metrics are not required by anything in this document.**" in normalized
    assert "requests *currently being handled*" in normalized
    assert "Do not reintroduce it as settlement evidence." in normalized

    # …and the snippet that remains is the current, non-deprecated form.
    assert "servers {\n" not in proxy
    assert "```caddyfile\n{\n    metrics\n}\n```" in proxy
    assert "removed in the next major version" in normalized


def test_an_unsettled_episode_is_an_incident_rather_than_a_miss():
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    unsettled = " ".join(
        procedure.split("- **Unsettled**", maxsplit=1)[1]
        .split("No fresh submission is permitted", maxsplit=1)[0]
        .split()
    )
    assert "This is **not** a miss and not a hit." in unsettled
    assert "Do not authorize a fresh export." in unsettled
    assert "escalate to the maintainer" in unsettled

    # An endpoint that cannot be taken down is one of the ways step 1 fails…
    assert (
        "The endpoint is still serving and the maintainer has not authorized "
        "stopping it" in unsettled
    )
    assert "something is still listening on the port" in unsettled
    # …and so is a proxy that is still up, or still going down.
    assert (
        "**Caddy is still running, or is still shutting down, or something "
        "would restart it**" in unsettled
    )
    assert (
        "the public name is answered by Caddy or by the application rather than "
        "by no origin at all" in unsettled
    )
    assert (
        "**a hop in front of this host cannot be terminated and its route has "
        "not been retired**" in unsettled
    )
    assert (
        "the endpoint or Caddy was restarted before the outcome was recorded"
        in unsettled
    )
    # …and the way out is to make S-A and S-I true, not to record an unproven miss.
    assert (
        "stop the endpoint, terminate the ingress in front of it, and satisfy "
        "S-A and S-I" in unsettled
    )

    assert (
        "No fresh submission is permitted from the reload until a settled hit "
        "or a settled miss has been established" in normalized
    )


def test_a_fresh_submission_is_followed_by_a_confirming_query():
    """Step 4: the residual is detected rather than assumed away.

    If the episode's original request ever did commit across the down window,
    the procedure has to find it instead of leaving the Council with two pending
    artifacts for one export.
    """
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    assert (
        "Step 4 — restart on a retired route, then confirm the episode produced "
        "one artifact" in procedure
    )
    assert "Only for a settled miss, and neither half is optional." in normalized
    assert "Expect exactly one acceptance event" in normalized
    assert (
        "Treat it as **ambiguous** — stop, do not let the Council review both "
        "rows" in normalized
    )
    assert "superseded through the documented correction flow" in normalized


def test_step_4_retires_the_route_before_anything_is_brought_back():
    """The prevention half of step 4, added with S-I.

    S-A and S-I account for this host. Neither accounts for a hop in front of
    it, and the procedure stops depending on what such a hop does with a request
    it holds: what comes back is a different address, so the address a stranded
    request carries no longer reaches the application.
    """
    procedure = _lost_pin_procedure()
    step_four = " ".join(
        procedure.split(
            "##### Step 4 — restart on a retired route", maxsplit=1
        )[1]
        .split("##### What settlement rests on", maxsplit=1)[0]
        .split()
    )

    assert (
        "**Retire the route the episode used before bringing anything back.**"
        in step_four
    )
    assert "They cannot account for a hop in front of it" in step_four
    assert (
        "what comes back is a **different address**, and the address the "
        "episode's stranded request carries no longer reaches the application"
        in step_four
    )
    # The old block is *replaced*, not deleted: observed on Caddy 2.10.2, a
    # deleted block falls through to an empty 200, or to Foundry on these hosts.
    assert "handle /api/v1/foundry/snapshots {\n    respond 410\n}" in procedure
    assert "Deleting the §5.4 block is *not* enough on its own" in step_four
    assert (
        "An empty `200`, or anything Foundry would say, means the block was "
        "deleted rather than replaced" in step_four
    )
    # The recovery block is single-use and strips its prefix.
    assert "handle /recovery/<nonce>/api/v1/foundry/snapshots {" in procedure
    assert "uri strip_prefix /recovery/<nonce>" in procedure
    # The retirement is verified rather than assumed, before the GM submits.
    assert "confirm the **retired** path cannot reach the application" in step_four
    assert "must now answer **`410`** — the refusal above, and nothing else" in step_four
    assert (
        "A `401` means the old path still reaches the endpoint" in step_four
    )
    assert "re-point the module's `submissionEndpoint`" in step_four
    # Ordering: retire and verify, then submit.
    assert step_four.index("confirm the **retired** path") < step_four.index(
        "let the GM prepare and submit the fresh export"
    )
    # And the reason the query alone was not enough.
    assert (
        "**Detection is not prevention, and this step is both.**" in step_four
    )
    assert (
        "a query that finds the duplicate afterwards does not stop the miss "
        "from having authorized it" in step_four
    )
    assert "Restore the §5.4 route and remove the recovery route" in step_four


def test_the_downtime_window_ends_where_step_4_begins():
    """S-D and step 4 must be jointly satisfiable.

    An earlier version required steps 2, 3 *and 4* to run with the endpoint
    down, while step 4 began by restarting it. No operator could obey both. The
    boundary is now explicit and is asserted from both sides here, because the
    two concepts were previously asserted separately and their contradiction
    went unnoticed. Since the fourth remediation the window covers Caddy too, so
    the downtime it describes is the site's.
    """
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    settlement = " ".join(
        procedure.split(
            "###### S-D — all of it stays down until the outcome is recorded",
            maxsplit=1,
        )[1]
        .split("###### Why this settles the question", maxsplit=1)[0]
        .split()
    )
    step_four = " ".join(
        procedure.split(
            "##### Step 4 — restart on a retired route", maxsplit=1
        )[1]
        .split("##### What settlement rests on", maxsplit=1)[0]
        .split()
    )

    # S-D claims downtime over steps 2 and 3 only, for both processes…
    assert (
        "Steps 2 and 3 below are run with the endpoint and Caddy both down"
        in settlement
    )
    assert "Steps 2, 3 and 4" not in normalized
    assert (
        "both stay down until step 3's outcome — a settled hit or a settled "
        "miss — has been recorded" in settlement
    )
    assert "A restart of either before that voids settlement" in settlement
    # …and hands the restart to step 4 rather than forbidding it there.
    assert "**Step 4 is outside settlement**" in settlement
    assert (
        "it may begin only after a settled miss has been recorded" in settlement
    )

    # Step 4 agrees, from its own side, and says why that is not a loophole.
    assert "This step runs **outside settlement**" in step_four
    assert "that is not a loophole in S-D" in step_four
    assert (
        "Restarting now cannot void an outcome that is already written down."
        in step_four
    )
    # The forbidden ordering is still forbidden, and named as such.
    assert (
        "Restarting *before* the miss is recorded is the thing S-D forbids"
        in step_four
    )
    # The restart is ordered after the recorded miss, not before it.
    assert "confirm the settled miss is recorded;" in step_four
    assert step_four.index("confirm the settled miss is recorded;") < step_four.index(
        "restart the endpoint and start Caddy on the amended configuration"
    )

    # The stop times are recorded under S-D; the restart times under step 4.
    assert "Record the stop times." in settlement
    assert "Record the restart times there." in settlement
    assert "record both times" in step_four


def test_the_settlement_argument_states_what_it_does_and_does_not_depend_on():
    """Settlement rests on two absent processes and a dead address.

    None of the three is a claim about anyone's documented behaviour, which is
    what the two remediations before this one died on. That is also what makes
    it survive Phase 3's concurrent server, and why the Phase 3 obligation is an
    improvement — settling without a stop — rather than a repair of an argument
    that breaks.
    """
    normalized = " ".join(_lost_pin_procedure().split())

    assert "**an unserved port cannot accept anything.**" in normalized
    assert (
        "a property of the socket API rather than of `wsgiref.simple_server`"
        in normalized
    )
    assert (
        "**a process that does not exist holds nothing and dials nothing.**"
        in normalized
    )
    assert (
        "it is why S-I terminates Caddy rather than reloading or draining it"
        in normalized
    )
    assert (
        "**a request cannot commit through an address that no longer reaches "
        "the application.**" in normalized
    )

    # What it no longer rests on, said in the document rather than only here.
    assert "**What settlement no longer rests on**" in normalized
    assert (
        "whether Caddy fails or holds a request whose upstream dial is refused"
        in normalized
    )
    assert (
        "whether the edge in front of it queues, retries or discards a request"
        in normalized
    )
    assert "it is **no longer what makes a miss safe**" in normalized
    # …and the one new requirement it does add.
    assert "the ingress be **terminable**" in normalized

    assert (
        "Three earlier conditions are withdrawn rather than weakened" in normalized
    )
    assert "The `502`/`503` confirmation that accompanied the third" in normalized

    assert "Phase 3 obligation" in normalized
    assert (
        "add the mechanism that lets recovery settle an episode **without** a "
        "stop" in normalized
    )
    assert "stops new intake and waits for accepted requests to finish" in normalized
    assert "tests/test_snapshot_recovery_settlement.py" in normalized
