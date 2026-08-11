# B-1 and I-1 remediation record — independent Phase 2 gate review

Date: 2026-08-10
Findings addressed: **B-1** (Blocking), **I-1** (Important), **RA-4** (procedure
note, carried)
Source review: [`Handover information`](Handover%20information) — Codex,
Independent Reviewer, 2026-08-09
Implemented by: Claude

This record closes two findings raised by the independent gate reviewer. **It is
not a gate decision, not an acceptance of I-03, and not evidence that any
rehearsal was performed.** No gate decision is recorded anywhere in this change,
as the handover required.

Both changes carry **no independent review**: they were implemented after the
independent review and have not been back through one. That is what the package
is being returned for.

**Read this first.** B-1 has been remediated four times and **is not closed** —
the independent reviewer holds it open, and closing it is the reviewer's to do.
The current rule is the fourth remediation,
[§ B-1, fourth remediation](#b-1-fourth-remediation--settlement-terminates-the-whole-ingress-path),
and **everything about S-B in the first two halves of this document is
withdrawn**, as is the third remediation's endpoint-only stop. In order:

| Re-review | Verdict | What was wrong | Where the rule went |
|---|---|---|---|
| 2026-08-10 (first) | I-1 closed, **B-1 open** | S-B inferred the endpoint's *accept* order from the client's *issuance* order | second remediation: S-B.1 + S-B.2 |
| 2026-08-10 (second) | **B-1 open** | S-B.1 read `caddy_http_requests_in_flight` as a drain; Caddy documents it as the requests *currently being handled* | third remediation: **the probe and the gauge are withdrawn**; settlement is a stopped endpoint |
| 2026-08-10 (third) | **B-1 open** | stopping the *upstream* leaves a request the proxy holds and has not yet dialled upstream for; it connects after the restart, and step 4 detects the duplicate rather than preventing it | fourth remediation: **the endpoint-only stop is withdrawn**; settlement terminates the whole ingress path, and step 4 retires the route |

## B-1 — lost-pin reconciliation could still produce a false miss — first remediation

### What was wrong

The §9 procedure told the operator to wait until the final "request/timeout has
finished", run the acceptance-event query, repeat it once, and — on a miss —
authorize a fresh export.

A client timeout proves only that the browser stopped waiting. It says nothing
about the server, and reloading the Foundry page does not cancel anything:
`wsgiref.simple_server` reads a request into its handler and runs it to
completion whether or not a client is still listening. So this sequence was
reachable, and the previous whole-episode window correction did not touch it:

1. the POST reaches the server and keeps processing;
2. the client times out; the page is reloaded; the in-memory pin and its derived
   idempotency key are lost;
3. both reconciliation queries run before the transaction commits;
4. both miss, so the procedure authorizes a fresh export;
5. the original request commits.

Two queries moments apart are two observations of one still-open transaction.
Repeating the query was never capable of detecting this.

The harm is specific. A same-key retry is safe because identical bytes hit the
checksum uniqueness constraint. A **fresh export is not identical bytes** — it
is re-serialised from the world at a later moment and carries its own checksum —
so it lands beside the original rather than merging with it. One real submission
becomes two pending artifacts, which is the outcome this whole procedure exists
to prevent.

### The corrected rule

> **S-B in this section is withdrawn**, and S-A is stricter than written here: a
> replacement process no longer settles anything. See the third remediation.

§9's lost-pin reconciliation is now three explicit steps, and the query result
may not be interpreted at all until the first has been recorded.

**Step 1 — settlement.** A positive statement about the server, established as
one of:

| | Condition | Why it settles the question |
|---|---|---|
| **S-A** | the process that served the episode has exited — no such PID, or the running one started after the episode's last attempt | an exited process commits nothing; PostgreSQL rolls back whatever its connection held, and a commit whose record was already written is already durable and already visible to the query |
| **S-B** | the same process (same PID, same start time) has answered a later probe | the Phase 2 endpoint is `wsgiref.simple_server`, which serves one connection at a time in accept order, so an answer to a probe issued after the episode means every earlier handler already returned — and a submission handler returns only after committing or rolling back |

Both additionally require `pg_stat_activity` to show no backend `active` or
`idle in transaction`. It is cheap, read-only, and independent of the argument
above, so it is not skipped.

The probe is a deliberately **unauthenticated** POST to the submission route,
sent to the service on loopback rather than through Caddy. The endpoint refuses
it `401` before it reads a body, establishes a principal or touches the
database, so it writes no audit event, no snapshot row and no artifact —
recovery must not write. Any answer settles the question; the status only
confirms the service is what replied. **A probe that does not return is not a
settlement**: wait and repeat it rather than shortening the timeout into a
second false negative.

**Step 2 — the whole-episode acceptance-event query**, unchanged. The window
correction from CL3-B-1 is preserved exactly: the window spans the first
submission of the pinned bytes through the last attempt before the reload, the
checksum join to the snapshot row is retained, there is still no
`foundry_snapshots.received_at` filter, and a same-key retry still writes no new
event.

**Step 3 — interpretation**, now four outcomes rather than three:

- **Hit** — unchanged.
- **Miss** — requires step 1's settlement, established and recorded with its
  evidence. The repeat-once rule survives for operator error (a mistyped world
  id, a window set from the wrong clock) and is explicitly **no longer what
  makes the miss safe**. "Two misses without settlement are not a miss."
- **Ambiguous** — unchanged: more than one row, or an unattributable row. Stop.
- **Unsettled** — new. Step 1 could not be completed: the probe never returned,
  the process identity cannot be established, `pg_stat_activity` shows
  unattributable work, or the endpoint is served by something other than the
  single-threaded rehearsal server. This is **not a miss and not a hit**. Do not
  authorize a fresh export; escalate. An unresolved episode costs a delay; a
  wrong miss costs a second pending artifact.

Hit, miss, ambiguous and unsettled are all fail-safe: only a settled hit or a
settled miss permits anything to happen.

### What S-B rests on, stated rather than assumed

S-B is an argument about `wsgiref.simple_server` specifically. It does **not**
survive Phase 3's concurrent `freedom-web` process, where one worker can answer
a probe while another is still committing. §9 records this as a **Phase 3
obligation**: before the endpoint runs under a concurrent server, S-B must be
replaced by a condition that holds for one — an in-flight record committed
before processing and cleared after, a drain/quiesce step with an enforced
request deadline, or an equivalent. S-A remains valid under any server.

A settlement *deadline* derived from Caddy's `read_timeout`/`write_timeout` was
considered and rejected: those bound Caddy's patience, not the upstream handler,
and `wsgiref.simple_server` enforces no request deadline of its own. The
deadline would have been a guess wearing a number's clothes.

Persisting the pin so that recovery needs no server-side evidence was also
rejected: the standing confidentiality constraint forbids Actor data or a
credential in browser-readable Foundry settings, and the handover restated it.

### Evidence — what is automated, what was rehearsed, what is inferred

**Automated** — `tests/test_snapshot_recovery_settlement.py`, three tests:

- the late-commit sequence, reproduced deterministically against the real
  `SnapshotSubmissionService` with a gated `commit`: the query misses twice
  while the transaction is open, and the commit lands afterwards. This is the
  regression test for the finding;
- the settlement probe against a **real** `wsgiref.simple_server` running the
  **real** WSGI application: the probe's answer cannot arrive until the earlier
  submission commits, and the probe records nothing. This is S-B's load-bearing
  claim, tested rather than argued.
- that a fresh export is different bytes under a different checksum, so
  uniqueness cannot merge it with the original. Deliberately sequential: two
  overlapping transactions each committing their own row is PostgreSQL's
  isolation, and `FakeUnitOfWork` commits by copying pending state over the
  store, so a concurrent version of that assertion would be measuring the fake.

The probe test was checked against a threaded server as a **negative control**
and fails there with the message the Phase 3 obligation predicts, so it
discriminates the property rather than passing for an unrelated reason. The
negative control is not committed; it was a temporary monkeypatch.

`tests/test_snapshot_recovery_documentation.py` gains four tests pinning the
settlement step, the miss rule, the unsettled outcome and the Phase 3 note.

**Rehearsed** — nothing new. No rehearsal was run for this change.

**Inferred, and not claimed as observed** — that an operator following the three
steps reaches the right conclusion. Nothing automated establishes that, and
§9 step 10 now says so.

### Rehearsal A's step 10 no longer claims what it did not do

Two records are corrected:

- `docs/review/phase-2-supervised-rehearsal-2026-08-09.md` said "This is the
  CL3-B-1 closure by observation." It was not. The injected fault dropped the
  *response* of a request the service had already served (`upstream=200`, the
  replay path), so the acceptance event was committed before the operator
  queried — the hit branch. Nothing observed on 2026-08-09 is withdrawn; the
  claim that observing it closed the finding is.
- `docs/review/phase-2-i-03-cl3-remediation.md` recorded CL3-B-1 as closed on
  2026-08-09 and pointed at this record instead. It is now the record of the
  *window* correction only.

§6 step 10 itself now states that it does not exercise the late-commit case and
that inducing it against a live supervised rehearsal — which would mean holding
a real transaction open by hand — is deliberately not attempted.

### RA-4, carried in the same edit

§6 step 10 now says the rehearsal-only injector must fault the **POST**, not the
CORS preflight. A fault on the `OPTIONS` preflight stops the browser sending the
POST at all, so nothing reaches the service and the rehearsal can only reach the
miss branch while appearing to have exercised a lost response.

## I-1 — C-10's ECMAScript key boundary was wrong — **Closed**

### What was wrong

C-10 adopted ECMAScript own-property order — correctly — and then wrote the
boundary as "integer index … `[0, 2**53 - 1]`". Ordinary object enumeration
hoists **array indices**: `ToString(ToUint32(P))` is `P`, and `ToUint32(P)` is
not `2**32 - 1`. That range ends at `4294967294`. An *integer index* is a
`String.prototype`/typed-array concept that `OrdinaryOwnPropertyKeys` never
consults.

This was an observed cross-language disagreement, reproduced exactly as the
handover reported it:

```text
JavaScript: {"10000000000":"ten","5000000000":"five"}
Python:     {"5000000000":"five","10000000000":"ten"}
```

Both keys are ordinary string keys to the exporter, so code point decides;
the verifier sorted them numerically. Any real artifact carrying a canonical
decimal key of ten or more digits would have been reported non-canonical against
a conforming exporter. The committed fixture could not see it — its
integer-looking keys are dnd5e class levels, array indices under either rule.

### The corrected rule, and why only two of the three things changed

Contract §1/§1.0 and `application/foundry/parser.py` now say array index,
`[0, 2**32 - 2]`. **The Foundry module is unchanged, byte for byte, and keeps
version `1.0.5`.**

That is sufficient because the exporter never implemented the wrong rule.
`canonical.js` sorts the key array by code point and rebuilds an object; the
engine then hoists exactly the array indices on insertion. What it emits is what
the corrected contract describes. The verifier and the prose were the two things
describing something else, and they are the two things that changed.

Verified rather than argued: every boundary document below was encoded by the
shipped module and by the corrected verifier, and the bytes are identical.

`canonical.js`'s header comment still says "keys sorted by code point at every
depth", which describes the sort it performs rather than the order it emits. It
is **deliberately not edited**: changing the bytes of an installed and rehearsed
build under the same version is exactly what the version identity control
(CL3-I-2) exists to prevent. It is carried against the next version bump, and
`docs/rules/foundry-export-contract.md` §1.0 records it so it is not rediscovered
as a contradiction.

### Coverage

`foundry-module/tests/emit-canonical.mjs` is new: it runs caller-chosen
documents through the shipped `canonicalBytes`, which is what makes this
boundary reachable from a cross-language test at all (the existing emitter
produces one fixed bundle). It is test material and is not part of the module
build — `module.json` ships `scripts/main.js` and its imports.

`tests/test_exporter_contract.py` asserts eight boundary documents three ways —
the exporter's bytes, the verifier's bytes, and that the two are equal — against
written-out expectations, so a change to both implementations at once still has
to argue with a third statement of the rule. Covered:

| Case | Covered by |
|---|---|
| `"0"` | the smallest array index |
| `"4294967294"` | largest array index, hoisted |
| `"4294967295"` | not an array index, sorts as text |
| `"5000000000"` vs `"10000000000"` | numeric and code-point order disagree — the finding's own pair, both orderings of the input |
| `"01"`, `"-1"`, `"1.0"`, `" 1"`, `"+1"`, `"1e2"` | noncanonical forms are ordinary string keys |
| `"9007199254740991"`, `"9007199254740992"` | the old bound's own values, now string keys |
| nested objects and arrays | the rule recurses |

Mirrored in `foundry-module/tests/canonical.test.mjs` (seven new tests) and
pinned for the verifier alone in `tests/test_snapshot_parser.py`.

### What is not disproved

**Rehearsal B's recorded `canonical_encoding = yes` stands.** The real artifact
evidently contained no key at this boundary. What is corrected is the claim that
C-10 was correct and complete — recorded as change-log **C-12**, with a
superseding banner on C-10 itself.

## B-1, second remediation — S-B needs proof the path has drained

> **Withdrawn by the third remediation.** S-B.1's in-flight gauge does not mean
> what this section needed it to mean, so S-B.1 and S-B.2 are both gone. Kept as
> the record of what was attempted and why it failed. The current rule is
> [§ B-1, third remediation](#b-1-third-remediation--settlement-is-a-stopped-endpoint).

Date: 2026-08-10. Source: the independent re-review of this record, which closed
I-1 and held B-1 open. Change-log **C-14**, which supersedes C-13 in part.
Implemented by Claude, and it too **carries no independent review**.

### What was still wrong

S-B's justification above reads: *"A probe issued after the episode's last
attempt is therefore handled after every request of that episode."* That is an
inference from **issuance** order to **accept** order, and the server does not
supply it. `wsgiref.simple_server` guarantees serial handling in the order it
*accepts* connections. Nothing makes accept order follow the order a client
issued requests in — least of all here, where the submission travels
browser → Caddy → loopback and the probe is sent straight to loopback.

So this sequence survived the first remediation:

1. the POST reaches Caddy and is still there — buffered, or accepted but not yet
   forwarded upstream;
2. the operator, seeing an unchanged PID and start time, sends the probe on
   loopback; the endpoint accepts it, refuses it `401`, and answers;
3. the operator records S-B as established and runs the query, which misses,
   twice;
4. Caddy forwards the submission; the endpoint accepts it, and it commits.

One real submission, two pending artifacts — the same harm C-13 set out to
remove, reached by a different route. The `pg_stat_activity` corroboration
cannot see it either: a request that has not reached the application has no
backend to be `active` or `idle in transaction`.

### The corrected rule

S-B is now two conditions, and the probe is worthless without the first.

**S-B.1 — nothing can still be delivered.** Established and recorded before the
probe is sent, as all three of:

| | Evidence | What it rules out |
|---|---|---|
| 1 | the page was reloaded or closed, and the GM confirms no attempt since the episode's last | a client still sending |
| 2 | `caddy_http_requests_in_flight` reads `0` for every series of the server fronting this endpoint, read from Caddy's loopback admin API | a request the proxy holds but has not yet forwarded |
| 3 | the endpoint's current connections, recorded from `ss` | nothing — it is the observation the ordering argument then refers to |

**S-B.2 — the probe**, unchanged: unauthenticated, on loopback, refused `401`
before a body is read, a principal exists or the database is touched.

The justification is restated as the chain it is: after S-B.1 nothing new can be
delivered; every episode request that did arrive therefore already holds a
connection established before the probe's; a listening socket hands completed
connections to the application first-in, first-out and `wsgiref.simple_server`
takes them one at a time; so each of those handlers returns before the probe is
served, and a submission handler returns only after committing or rolling back.
Only the first link concerns issuance order, and S-B.1 observes it instead of
assuming it.

The counter's limits are written into §9 rather than argued past: it is labelled
by server and handler, not by route, so it cannot isolate this endpoint's
traffic, and on a host busy with anything else it will not read `0`. That is a
real "cannot establish", and the procedure says so.

An unreadable or non-zero in-flight counter is an **unsettled** episode, not a
miss. §9 also now records the way out of one, which is the maintainer's to
authorize rather than the operator's: **stopping the endpoint process converts
the episode into S-A.** An exited process commits nothing. It aborts an
in-flight submission deliberately, which is why it is authorized — and it is
always better than recording a miss that was never established.

§5.4 gains the configuration this depends on: Caddy's per-server metrics must be
enabled, or the counter S-B.1 reads does not exist and every episode can be
settled only by S-A.

### What was considered and not done

Replacing S-B with an **application-level in-flight or quiescence mechanism** —
the reviewer's own alternative — is the better answer, and it is deliberately
not done here. It is a code change to the submission path during a gate
re-review; §9 already carries it as the Phase 3 obligation; and it would have to
be designed against the concurrent server rather than retrofitted to this one.
S-B.1 is obtainable today from configuration and two read-only observations. §9
now records that such a mechanism would retire S-B.1 along with S-B.

### Evidence

**Automated** — two tests added to `tests/test_snapshot_recovery_settlement.py`:

- `test_a_probe_can_be_answered_before_an_earlier_submission_is_accepted`
  reproduces the false miss above against the real WSGI application on a real
  `wsgiref.simple_server`. The probe is accepted, answered `401`, and both
  queries miss, all before the submission's connection to the endpoint is made
  at all — which is exactly what "still inside Caddy" means at the endpoint's
  listening socket. This is the regression test for the re-review finding.
- `test_the_probe_cannot_overtake_a_submission_already_queued_at_the_endpoint`
  establishes what S-B.1 buys, at the point the earlier test did not reach. The
  submission is connected and fully sent but **not yet accepted, read or
  handled** — asserted, not assumed — when the probe connects; the server only
  then begins serving. The probe still cannot be answered until that submission
  commits. The C-13 test waited until the submission was already inside its
  commit, which presumes the ordering that needed proving.

Both were run against a threaded server as a **negative control**, by copying
the file and substituting a `ThreadingMixIn` server class. The ordering test
fails there with the message the Phase 3 obligation predicts; the false-miss
reproduction passes there, as it must, since it does not depend on serial
handling. The control is not committed.

`tests/test_snapshot_recovery_documentation.py` gains three tests: S-B.1 and the
named inference it replaces, the §5.4 metrics requirement, and the unsettled
outcome's new trigger and its S-A escape.

**Rehearsed** — nothing. No rehearsal was run for this change either, and none
of the operator-side evidence in S-B.1 has been collected against a live Caddy:
the `curl`, the metric name and the `ss` filter are written from Caddy's
documented admin API and standard tooling, and are **not** claimed as observed
here. The first operator to run §9 should expect to confirm them.

### Checks

```text
./venv/bin/python -m pytest -q                → 1813 passed, 208 skipped,
                                                 1 xfailed, 0 failed
node --test foundry-module/tests/*.test.mjs   → 150 passed, 0 failed, 1 todo
git diff --check                              → clean
```

The five new Python tests are the ones named above; the JavaScript totals are
unchanged, because no JavaScript changed. The 208 skips are the declared
PostgreSQL-backed set, skipped without `TEST_DATABASE_URL`, which is not
configured in this session. The `xfail` and the node `todo` are the open NFC key
collision, unchanged and still tracked.

No code under `application/`, `adapters/`, `domain/`, `tools/` or
`foundry-module/` changed: this remediation is documentation, plus tests. No
rehearsal was run, no Foundry instance, real export, real Actor data,
credential, database or external endpoint was read or modified, and **no Phase 2
gate decision is recorded.**

## B-1, third remediation — settlement is a stopped endpoint

> **Superseded by the fourth remediation.** The stop is right and its scope was
> wrong: it covered the endpoint and not the path in front of it, so a request the
> proxy held and had not yet dialled upstream for survived the down window and
> committed after the restart. S-A.1 and S-A.2 survive unchanged; **S-A.3 is
> withdrawn and inverted**, and S-A.4 becomes S-D. Kept as the record of what was
> attempted and why it was not enough. The current rule is
> [§ B-1, fourth remediation](#b-1-fourth-remediation--settlement-terminates-the-whole-ingress-path).

Date: 2026-08-10. Source: the independent re-review of the second remediation,
which held **B-1 open** and recommended not closing the Phase 2 gate. Change-log
**C-15**, which supersedes C-14 and narrows C-13. Implemented by Claude, and it
too **carries no independent review**. **B-1 is not recorded as closed here.**

### What was still wrong

S-B.1's second condition read: *"Caddy counts every request it is handling,
including one it has accepted but not yet forwarded upstream."* Caddy does not
document that. It documents `caddy_http_requests_in_flight` as the requests
**currently being handled** ([metrics](https://caddyserver.com/docs/metrics)),
which is narrower in exactly the place S-B.1 needed it to be wide:

- a connection Caddy has accepted whose request has not entered the instrumented
  handler is not counted;
- body bytes still arriving over an established HTTP/1.1, HTTP/2 or HTTP/3
  connection are not counted;
- closing or reloading the Foundry page does not establish that everything the
  browser already transmitted has been consumed; and
- sampling the gauge and then the socket table is two observations, not one
  atomic drain.

So the false miss survived the second remediation:

1. the submission has been sent, but its request has not entered Caddy's
   instrumented handler;
2. the GM confirms no new attempt;
3. the gauge reads zero, and the endpoint has no connection for it yet;
4. the probe is answered on loopback and both queries miss;
5. Caddy begins handling, forwards the request, and it commits.

The reviewer also identified the deprecated Caddyfile form §5.4 had adopted:
nested `servers { metrics }` still adapts on the installed Caddy 2.10.2, but
`caddy adapt` warns it is removed in the next major version.

Reading the argument again in that light exposed a smaller version of the same
hole in **C-13's S-A**, which the reviewer did not raise: it accepted "the process
running started after the episode's last attempt". A replacement process is
reachable by the proxy, and it will commit the episode's stranded request as
readily as the original would have.

### The corrected rule

Settlement stops being an observation of what is in flight and becomes a
**state**. The probe and the gauge are both withdrawn, and §9 says so by name so
that neither returns as an apparent simplification. There is one condition:

**S-A — the endpoint is not running, and does not run again until the outcome has
been recorded.** Four recorded parts:

| | Evidence | What it establishes |
|---|---|---|
| **S-A.1** | the process that served the episode is gone (`ps`/`ss`, identified by start time, not PID) | an exited process commits nothing; PostgreSQL rolls back what its connection held, and a commit already written is durable and visible. If it is still running, the maintainer stops it — there is no second condition to fall back on |
| **S-A.2** | nothing is listening on the port | a *replacement* process is explicitly not enough; while anything listens, the proxy can hand it the stranded request |
| **S-A.3** | a request through Caddy is answered `502`/`503` by Caddy itself | the path from a client is dead, confirmed rather than assumed. An answer only the application could give means S-A is not established |
| **S-A.4** | it stays down through steps 2, 3 and 4, with nothing to restart it | a restart mid-procedure voids settlement |

`pg_stat_activity` corroboration is unchanged. The argument is one sentence:
**every commit on this path begins with an accept, and an unserved port accepts
nothing** — not a request in a client's socket, not one Caddy is still reading,
not one Caddy has accepted but not forwarded, not one already waiting in the
endpoint's own accept queue. It is a state rather than a sample, so it does not
depend on the proxy's internals, on what a gauge counts, on two observations
being atomic, or on the endpoint's concurrency model.

**Step 4 is new**, and it is where the residual goes rather than being argued
away. After a settled miss authorizes a fresh export, the endpoint is restarted,
the fresh export is submitted, and step 2's query is re-run over a window widened
to span the recovery. A second acceptance event whose checksum is not the fresh
submission's means the original committed across the down window after all: that
is **ambiguous**, it is escalated as a defect in this procedure rather than as an
ordinary incident, and the Council supersedes one artifact through the documented
correction flow instead of reviewing both. Two pending artifacts are recoverable
when they are found; this step is what finds them.

§5.4 changes in two ways. Caddy's per-server metrics are **no longer required** —
nothing in the document reads them — and the gauge is disclaimed in the section
that used to require it. What §5.4 now requires instead is what S-A actually
depends on: **no upstream retry window** (`lb_try_duration` unset, no second proxy
or queue), so that a dial refused by a stopped endpoint is a final `502` rather
than a request held for later. Where metrics are kept for monitoring, the snippet
is the current global `{ metrics }` form.

§6 step 10 now says that settlement there means stopping the endpoint after the
faulted duplicate delivery and before the query — which is a different thing from
"stopping the service before submission", the case that step deliberately is not.

### What this costs, and the Phase 3 improvement

S-A settles an episode by taking the endpoint down. That is acceptable for a
hand-started rehearsal process and poor for a running service, and it is the
honest cost of not having an application-level mechanism. What was a Phase 3
*obligation to repair a broken argument* is therefore now a Phase 3
**improvement**: before `freedom-web` carries real traffic, add what lets recovery
settle an episode **without** a stop — an in-flight record committed before
processing and cleared after it, an explicit quiesce that stops new intake and
waits for accepted requests to finish, or an equivalent. That is the reviewer's
own preferred answer, and it stays deferred rather than rejected: it is a code
change to the submission path during a gate re-review, and it should be designed
against the concurrent server rather than retrofitted to this one.

An *actual proxy drain* — stopping Caddy, or removing the route and reloading —
was considered and not chosen. It stops new intake, but it takes down every other
service on the host to reconcile one snapshot, where stopping the endpoint alone
is both narrower and strictly stronger.

### Evidence

**Automated** — `tests/test_snapshot_recovery_settlement.py` retains the
late-commit reproduction, the fresh-export/uniqueness test, and the false miss the
withdrawn probe rule permitted (kept as the record of why that rule is gone). The
two probe-ordering tests are replaced by the two that establish S-A, both against
a real `wsgiref.simple_server` over the real WSGI application:

- `test_a_submission_queued_at_the_endpoint_commits_nothing_once_it_stops` takes
  the hardest case, and the one no probe and no gauge can distinguish from an
  empty system: a submission **connected, fully sent, and waiting unaccepted** at
  the endpoint — where a request Caddy forwarded an instant before the stop sits.
  The endpoint stops without serving it. Nothing is accepted, the commit gate is
  never reached, no audit event and no snapshot row exist, and a later delivery
  attempt is refused at the socket. Checked against a **negative control** that
  serves the queue instead of stopping: it fails there, so it discriminates the
  stop rather than passing for an unrelated reason. The control is not committed —
  it is the same file with `server.server_close()` replaced by a `serve_forever`
  thread.
- `test_nothing_can_be_delivered_to_the_endpoint_once_it_has_stopped` establishes
  the other half: an acceptance that committed before the stop is still visible to
  the query, and a delivery attempted after the stop is refused. The second
  delivery is deliberately different bytes under a different idempotency key, so a
  still-running endpoint would produce a second row and fail the test.

`tests/test_snapshot_recovery_documentation.py` now pins the single condition and
its four parts, both withdrawn conditions **with their defects named**, §5.4's
retry-window requirement and its non-deprecated metrics form, the unsettled
triggers, and step 4.

**Rehearsed** — nothing. No rehearsal was run for this change either. In
particular, **no part of S-A has been observed against a live Caddy**: that a
stopped upstream produces `502`/`503` rather than a held request is read from the
§5.4 configuration and Caddy's documented behaviour, and the `ss` and `ps`
invocations are written from standard tooling. The first operator to run §9 should
expect to confirm them.

**Inferred, not claimed as observed** — that an operator following the four steps
reaches the right conclusion.

### What remains open in this remediation

- **B-1 itself.** It is remediated, not closed.
- The Phase 3 improvement, which is now the only route to settling without a stop.
- Whether "the endpoint stays down until the outcome is recorded" is operationally
  acceptable for Phase 3's service. §9 states the requirement; it does not claim
  the service can afford it, which is part of why the improvement is recorded.
- That Caddy fails rather than holds a refused request is a documented-behaviour
  claim plus a configuration requirement, not an observation. §5.4 records the
  requirement so that a change to it cannot pass unnoticed; step 4 is what detects
  it if the claim is wrong anyway.

## B-1, fourth remediation — settlement terminates the whole ingress path

Date: 2026-08-10. Source: the independent re-review of the third remediation,
which held **B-1 open** for the fourth time. Change-log **C-18**, which supersedes
C-15 in part. Implemented by Claude, on the maintainer's ruling between the two
routes the reviewer offered, and it too **carries no independent review**. **B-1 is
not recorded as closed here.**

### What was still wrong

The reviewer's finding, in full:

> Stopping only the upstream endpoint does not settle requests still held by Caddy
> that have not made their first upstream connection. Such a request can connect
> after restart; "no retry window" only addresses retries after a failed attempt.
> Step 4 detects the duplicate but does not prevent the false miss from authorizing
> it.

It is correct, and the defect is one of **scope** rather than of kind. C-15's
argument — every commit on this path begins with an accept, and an unserved port
accepts nothing — is sound about every request that had reached the endpoint. A
request the proxy has accepted, or is still reading, and has not yet dialled
upstream for is not one of those. It is not in the endpoint's accept queue, so
stopping the endpoint does not reach it; and it has made no upstream attempt, so
§5.4's "no upstream retry window" does not govern it either — that rule is about
what happens after a *refused* dial, and this request's dial has not happened. It
happens whenever the proxy gets to it, which under C-15's own step 4 can be after
the endpoint has been restarted:

1. the submission is inside Caddy, accepted and unforwarded;
2. the endpoint is stopped; S-A.1 to S-A.4 are established exactly as written;
3. both queries miss, and the miss is recorded with its settlement evidence;
4. step 4 restarts the endpoint and the GM submits a fresh export;
5. Caddy makes its first dial, and the episode's original request commits.

Two pending artifacts for one export, which is the harm this procedure exists to
prevent, reached for the third time by a different route. C-15's step 4 sees it
afterwards — that is what it is for — and the reviewer's second sentence is the
one that matters: **detection is not prevention**, and the miss recorded at step 3
had already authorized the second artifact.

The same reading condemns C-15's **S-A.3**, which nobody had questioned. It told
the operator to confirm settlement by receiving a `502`/`503` from Caddy. Under the
corrected rule a `502` is Caddy's own answer, so receiving one establishes that
Caddy is *running* — the opposite of what settlement now requires. It is withdrawn
and inverted rather than deleted, because an operator who has run the old step will
otherwise carry the expectation forward.

### The corrected rule

The reviewer offered two routes: terminate or positively drain the complete
ingress path, or add an application-level mechanism that rejects pre-settlement
requests after restart. **The maintainer ruled for the first**, on 2026-08-10, and
the second stays where §9 already had it, as the Phase 3 improvement. The reasons
recorded with the ruling: the procedural route adds no unreviewed code to the
submission path during a gate re-review; it removes the class of claim the last two
remediations died on rather than adding a new one; and the application-level
mechanism should be designed against Phase 3's concurrent server rather than
retrofitted to `wsgiref.simple_server`.

Settlement is still a state rather than an observation. It is now a state of the
**whole path**, in three parts:

| | Condition | What it establishes |
|---|---|---|
| **S-A** | the endpoint is not running — S-A.1 the process that served the episode is gone, S-A.2 nothing is listening on its port | disposes of every request that had reached the endpoint. Unchanged from C-15, minus the withdrawn S-A.3 |
| **S-I** | the ingress in front of it is **terminated, not drained** — S-I.1 no Caddy process exists, S-I.2 nothing is listening on `:80`/`:443`, TCP *and* UDP, S-I.3 nothing will bring either back, S-I.4 confirmed from off the host that the name answers from no origin | disposes of everything that had *not* reached the endpoint. A process that does not exist holds nothing and dials nothing |
| **S-D** | all of it stays down through steps 2 and 3, until the outcome is recorded | was S-A.4, widened to both processes |

Three properties of that rule are worth stating because they are what the previous
versions lacked:

- **it is terminated, not reloaded or drained.** A reload leaves a running process
  deciding what to do with what it already holds, and that decision is exactly what
  no observation available to the operator can establish. Caddy's grace period is
  not relied upon either: S-I.1 reads the *absence of the process*, and the record
  says in as many words that being asked to shut down is not having shut down;
- **it removes dependencies rather than adding one.** Settlement no longer rests on
  whether Caddy fails or holds a request whose dial is refused — the claim that
  killed the second and third remediations — nor on what the Cloudflare edge does
  with a request it is holding. §5.4 keeps the no-retry-window requirement because
  a retry crossing the down window is a real failure mode and the requirement costs
  nothing, but it is explicitly **no longer what makes a miss safe**;
- **what it does newly require is that the ingress be terminable**: one proxy, on
  this host, under a supervisor the operator can stop. §5.4 records that as a
  requirement so that a hop added in front of Caddy cannot appear unnoticed.

**Step 4 gains the prevention half.** S-A and S-I account for this host and cannot
account for a hop in front of it. Rather than reason about what such a hop does,
the procedure makes the question irrelevant: after a settled miss the §5.4 `handle`
block is **removed** and the endpoint comes back behind a single-use
`/recovery/<nonce>/…` path, the retirement is verified from off the host before the
GM submits anything, and the GM re-points the module's `submissionEndpoint` (§4).
A request held anywhere upstream then carries an address that no longer reaches the
application, whenever it arrives and whatever held it. The confirming query stays
exactly as it was, and is now described as what it is: the detector behind the
preventer.

### What this costs

**Host-wide downtime for the duration of a reconciliation.** Caddy fronts every
service on this host, all three Foundry instances among them, so settling a
lost-pin episode now takes the site down through steps 2 and 3. C-15 considered
this and rejected it — "it takes down every other service on the host to reconcile
one snapshot" — and that judgement is reversed here on the reviewer's finding and
the maintainer's ruling: the narrower stop it preferred does not settle the
question, so the comparison was never between two settlements. §9 states the cost
where the operator meets it rather than only in this record, and notes the one way
it is narrower than it sounds: while the path is down the GM cannot submit anything
either.

It is also an operator-procedure cost. Step 1 is now seven recorded conditions
across two processes plus the database check, in order and under time pressure —
which makes the standing
question of whether **Unsettled** is reachable in practice harder rather than
easier, not something this remediation improves.

The Phase 3 improvement is unchanged in substance and sharper in motivation:
before `freedom-web` carries real traffic, add what lets recovery settle an episode
without a stop — an in-flight record committed before processing and cleared after,
an explicit quiesce, a pre-settlement barrier the restarted application refuses
requests against, or an equivalent. That is the reviewer's second route, and it is
the only known way to stop paying for a reconciliation in downtime.

### Evidence

**Automated** — `tests/test_snapshot_recovery_settlement.py` gains two tests, and
they are **each other's control**:

- `test_a_request_held_by_the_proxy_commits_after_the_endpoint_restarts`
  reproduces the finding. A real proxy — a real listening socket, a real client
  connection, the whole request read off it, no upstream dial — holds the
  episode's submission while S-A is satisfied in full against a real
  `wsgiref.simple_server`: the endpoint's process is stopped, its port unserved,
  both queries miss. Step 4 restarts the endpoint on the same port, the proxy makes
  its first dial, and the submission commits. This is the regression test for the
  endpoint-only stop, kept for the same reason the probe's false miss is kept.
- `test_a_request_held_by_the_proxy_dies_when_the_proxy_is_terminated` is the same
  episode with **one line different**: the proxy is terminated as well as the
  endpoint. Its thread ends without ever dialling, the client's connection dies
  where it stood, and the restart brings back an endpoint that nothing arrives at.

Because the pair differs in exactly the terminate call, the negative control is
committed rather than described — which the first three remediations could not
say. It was checked: deleting `proxy.terminate()` from the second test makes it
fail on `assert not proxy.dialled`, at the point where the proxy forwards across
the restart. One assertion had to be strengthened to get there, and it is recorded
because it is the kind of mistake this package keeps finding: asserting
`not forwarded` immediately after releasing the proxy passed whether or not the
proxy went on to dial, so the test waits for the proxy to finish before asserting.

`tests/test_snapshot_recovery_documentation.py` gains two tests — S-I's four parts
with the inverted `502` check, the stated cost and S-D; and step 4's retirement,
its verification, its ordering before the GM submits, and its "detection is not
prevention" statement — and six existing tests are updated to the new rule,
including the third withdrawn condition named with its defect.

**Observed against a real Caddy 2.10.2, 2026-08-10** — on an isolated rig, on high
ports, with `admin off` so the production admin API was never touched, a stub
upstream standing in for the endpoint because every claim under test is about the
proxy and the route rather than about the application. The production instance was
not stopped, reconfigured or reloaded, and was verified still serving its three
Foundry sites afterwards. Six results:

| | Observed | What it settles |
|---|---|---|
| 1 | a request the proxy had accepted with **no upstream connection made** survived the endpoint stop and was delivered and answered `201` after the restart | **the finding itself, reproduced.** It was until now an argument about what Caddy might be holding; it is now a thing that happened |
| 2 | the same episode with the proxy terminated between the stop and the restart delivered **nothing**, and the client's connection was closed | S-I does what it claims, against a real proxy rather than a modelled one |
| 3 | `uri strip_prefix /recovery/<nonce>` presented `/api/v1/foundry/snapshots` upstream; `caddy adapt` ordered `request_body` → `strip_path_prefix` → `reverse_proxy` without an `order` directive | step 4's recovery route works as written |
| 4 | with the block **deleted**, the retired path answered an empty **`200`** — not the `404` this record first claimed | a defect in step 4, corrected below |
| 5 | with the block **replaced by `respond 410`**, the retired path answered `410` with the endpoint up and with it down | the corrected retirement, verified both ways |
| 6 | endpoint down, proxy up, live route → **`502`** | the inverted S-A.3, confirmed: a `502` proves Caddy is running |

**Two corrections came out of running it**, and both are now in §9:

- **step 4 told the operator to expect a `404` from the retired path, and that was
  wrong.** Removing a `handle` block does not produce a refusal; it produces
  whatever the rest of the site does with an unmatched path, which was an empty
  `200` on the rig and would be *Foundry's* answer on these hostnames, each of
  which ends in a `reverse_proxy`. An empty `200` on the submission path is the
  least readable answer available. The retirement is now **explicit** — `handle
  /api/v1/foundry/snapshots { respond 410 }` — and step 4 checks for `410`, naming
  the empty `200` as the symptom of a deleted rather than replaced block.
- **S-I.2 can pass while S-I.1 fails.** Measured with one request held open at the
  moment of the stop: the **listener closed immediately, and the process lived a
  further 5.4 seconds.** An operator reading the socket table first sees an
  unserved port while the process that holds the episode's request is still
  running. §9 now records the measurement, says the two checks do not come true in
  the order they are written, and tells the operator to read `ps` last and until it
  is empty. The warning was already there; it was a caution, and it is now a
  number.

**Observed against the production Caddy, 2026-08-10, in a maintainer-authorized
window** — with the service stopped, three things:

| | Observed | What it settles |
|---|---|---|
| 7 | the public name answered **`521`** through Cloudflare, on the submission path and the site root alike | S-I.4's expectation, confirmed against the real edge: with the origin down the edge answers by itself, and the answer is neither Caddy's `502` nor anything the application could give |
| 8 | `systemctl show caddy -p Restart` is **`no`** | S-I.3 on the real unit: nothing brings Caddy back on its own |
| 9 | production carries a **UDP `:443` listener** as well as two TCP ones | S-I.2's UDP check is necessary on this host rather than a precaution; a socket table filtered to TCP would have missed a live listener |
| 10 | with **no connection in flight**, the production process and both listeners were gone within **4 ms** of the stop | on its own, misleading — see below |
| 11 | with **one request held open** on the origin's own listener, accepted over TLS 1.3 and unrouted: listeners gone in **0.5 ms**, process gone at **4.3 s**, and the held connection **closed with nothing delivered** | S-I's core claim, on the production instance rather than a model: terminating the proxy ends the request it was holding |
| 12 | **step 4 phase 1, on the production Caddy**: with the block added to the real configuration file, `caddy validate` passing and a real reload, the retired path answered **`410`** and the recovery path **`401`**; all three Foundry sites were unaffected across the reload and the revert | step 4's two claims, on the production instance's own config, validate and reload path. Loopback-only: no public site block was edited and no internet-reachable route added |

Every command, script and log behind rows 1–12 is reproduced in full in
[`phase-2-b-1-settlement-observations-2026-08-10.md`](phase-2-b-1-settlement-observations-2026-08-10.md),
so that question 4 can be acted on rather than taken on this record's word.

**The first attempt at this window measured nothing**, and the correction is worth
recording because it is the shape of defect this package keeps finding. The script
ran against an already-stopped service, so every interval it recorded read as zero
— which looks like a result. A script whose purpose is to measure a stop now
refuses to run unless the service is active, and the window was taken again.

**What the three timings mean together, which none says alone.** Production with
nothing in flight was gone in 4 ms; production with one request held open took
**4.3 s**, and the rig took 5.4 s under the same condition. **The delay tracks what
the proxy is holding rather than being a fixed cost of stopping it**, and that is
now established on the production instance and not merely on a rig. The
uncomfortable reading: a lost-pin episode *is* the held-request case — the operator
is there precisely because a request may be in flight — so the 4 ms stop is the one
they will not get, and **a rehearsal on an idle host would show it and teach the
wrong expectation**. The gap between S-I.2 reading clean and S-I.1 coming true was
**4.3 seconds on the machine this procedure runs on**. §9 carries all three
numbers, the interpretation, and the instruction to read `ps` last and until it is
empty.

**Still not observed** — step 4's retirement inside a **public** site block, and an
operator following the four steps.
[`phase-2-step-4-retirement-validation-plan.md`](phase-2-step-4-retirement-validation-plan.md)
scopes both halves; **phase 1 was executed on 2026-08-10 and is row 12 above**.
Phase 2 — the retirement inside the `foundry1` site, where the fall-through would
reach Foundry rather than the rig's empty `200` — is **not run**: it re-creates the
public exposure reverted on 2026-08-09 and is therefore a decision rather than a
next step. §6 step 10 is where it belongs if it is taken.

**Inferred, not claimed as observed** — that an operator following the four steps
reaches the right conclusion.

### What remains open in this remediation

- **B-1 itself.** It is remediated, not closed.
- The Phase 3 improvement, still the only route to settling without a stop, and now
  also the only route to settling without taking the site down.
- Whether host-wide downtime is an acceptable price for a Phase 3 service. It is
  ruled acceptable for Phase 2's hand-started rehearsal; nothing here claims more.
- Whether **Unsettled** is reachable in practice, which this change makes harder.
- **S-I against the production Caddy**, and with it everything about the Cloudflare
  hop. The rig establishes the mechanism; it does not establish this host. The
  window needs maintainer authorization because it disconnects live Foundry
  sessions — three were connected when this was written.

## Records corrected

First remediation, unless a row says otherwise.

| Record | Correction |
|---|---|
| `docs/operations/foundry-snapshot-submission.md` | §9 settlement steps; §6 step 10 (late-commit disclaimer, RA-4). **Second remediation:** §9 S-B split into S-B.1/S-B.2 with the restated chain, the unsettled trigger and the S-A escape; §5.4 requires Caddy's per-server metrics. **Third remediation:** §9 step 1 rewritten to the single stopped-endpoint condition with S-A.1–S-A.4 and the withdrawn conditions named; step 3's unsettled triggers; new step 4; the "what settlement rests on" section; §5.4 drops the metrics requirement, disclaims the gauge, shows the global `{ metrics }` form and requires no upstream retry window; §6 step 10's settlement note. **Fourth remediation:** §9 step 1 widened to the whole path — the endpoint-only stop named as the third withdrawn condition, S-A reduced to S-A.1/S-A.2, **S-A.3 withdrawn and inverted**, new S-I.1–S-I.4, S-A.4 becomes S-D, "why this settles the question" and "what settlement rests on" rewritten; step 3's unsettled triggers gain the proxy's; step 4 gains route retirement, its verification and its ordering; §5.4 requires a terminable ingress, bounds what the retry window buys and points at the recovery route; §6 step 10 stops Caddy too |
| this record | **Second remediation:** the section on S-B.1/S-B.2. **Third remediation:** the table at the top, the third-remediation section, and this table; **every S-B paragraph in the first two halves is withdrawn**. **Fourth remediation:** the table at the top, a superseding banner on the third remediation, the fourth-remediation section, and this table |
| `docs/rules/foundry-export-contract.md` | §1 row and §1.0 boundary, with the reproduction and the module-comment deferral |
| `docs/review/phase-2-i-03-cl3-remediation.md` | CL3-B-1 reopened; scoped to the window correction |
| `docs/review/phase-2-supervised-rehearsal-2026-08-09.md` | step 10 no longer claims to have closed CL3-B-1 or exercised the late commit |
| `docs/project-management/change-log.md` | C-12 and C-13 added; C-10 given a superseding banner. **Second remediation:** C-14 added, C-13 given a superseding banner. **Third remediation:** C-15 added, C-14 given a superseding banner. **Fourth remediation:** C-18 added, C-15 given a superseding banner |
| `docs/project-management/status.md` | Phase 2 rows corrected |

## Checks

Fourth remediation, 2026-08-10:

```text
./venv/bin/python -m pytest -q                → 1886 passed, 208 skipped,
                                                 0 failed
(cd foundry-module && npm test)               → 155 passed, 0 failed, 0 todo
node --check foundry-module/scripts/*.js      → 8 files, all pass
git diff --check                              → clean
```

Four tests more than the package this change was applied to: two in
`tests/test_snapshot_recovery_settlement.py` and two in
`tests/test_snapshot_recovery_documentation.py`, with six existing documentation
tests rewritten to the new rule and none removed. The JavaScript totals are
unchanged, because no JavaScript changed. No code under `application/`,
`adapters/`, `domain/`, `tools/` or `foundry-module/` changed: this remediation is
documentation, plus tests.

Third remediation, 2026-08-10:

```text
./venv/bin/python -m pytest -q                → 1814 passed, 208 skipped,
                                                 1 xfailed, 0 failed
node --test foundry-module/tests/*.test.mjs   → 150 passed, 0 failed, 1 todo
node --check foundry-module/scripts/*.js      → 8 files, all pass
git diff --check                              → clean
```

First remediation: 1809 passed / 208 skipped. Second: 1813 passed / 208 skipped /
1 xfailed. The independent review's baseline was 1,784 passed / 208 skipped and
143 node tests. The third remediation nets one test — two probe-ordering tests
removed, two S-A tests and one documentation test added. The JavaScript totals are
unchanged in both later remediations, because no JavaScript changed. The 208 skips
are unchanged throughout: they are the declared PostgreSQL-backed set, skipped
without `TEST_DATABASE_URL`, which is not configured in this session. The `xfail`
and the node `todo` are the open NFC key collision.

`git status` shows **no change under `foundry-module/scripts/`**, and none to
`module.json` or `package.json`. The only files added under `foundry-module/` are
in `tests/`, which the manifest does not ship.

No rehearsal was run. No Foundry instance, real export, real Actor data,
credential, database, external endpoint or `docs/screenshots/` was read or
modified. The signed attestation's real identifiers are untouched. **No Phase 2
gate decision is recorded.**

## What this does not close

- **finding B-1 itself**, which is remediated four times and closed zero times.
  The reviewer holds it open, and closing it is the reviewer's to do;
- the independent re-review of these remediations, which is what the package is
  being returned for — including the fourth B-1 remediation above, which has had
  no review of any kind;
- the maintainer's ruling on change-log C-12, C-13, C-14, C-15 and C-18, none of
  which is ruled. **The maintainer did rule on the route** C-18 takes, between the
  two the reviewer offered, and that is not a ruling on the entry;
- the Phase 3 improvement that would let recovery settle an episode without
  stopping the endpoint — the reviewer's preferred answer, an application-level
  in-flight or quiescence mechanism — and with it the question of whether §9's
  stop, which now takes the site down with it, is acceptable for a running Phase 3
  service;
- any observation of S-A's or S-I's evidence against a live Caddy: that stopping
  Caddy leaves no process and no listener, that the public name then answers from
  no origin, that `uri strip_prefix` retires the old path as described, and the
  `ps`/`ss` invocations, are written from standard tooling and documented
  configuration, not from a run. The `502`/`503` expectation that used to sit here
  is **withdrawn and inverted**, not merely unobserved;
> **Both of the first two items below were closed later the same day**, on the
> re-review of C-15 and on maintainer instruction: change-log **C-16** fixes the
> NFC key collision in both implementations, corrects the header comment, and
> bumps the exporter to **`1.0.6`**. The list is left as written, as the record
> of what was open when this remediation was submitted.

- `canonical.js`'s stale header comment, carried to the next version bump;
- **a new open defect found while remediating I-1**, and deliberately not fixed
  here: `normalise` sorts keys by their pre-NFC form and inserts them under their
  post-NFC form, so two distinct keys sharing an NFC form collapse and one value
  is **silently dropped**; the verifier meanwhile does not normalise keys at all
  and emits the same key twice. Reproduced and recorded in
  [`phase-2-canonical-nfc-key-collision.md`](phase-2-canonical-nfc-key-collision.md),
  held open by a `{ todo: true }` node test and a strict `xfail` Python test.
  Not fixed because the exporter half changes the rehearsed `1.0.5` build's
  bytes, and fixing only the verifier would trade one cross-language
  disagreement for another;
- everything `phase-2-i-03-cl3-remediation.md` already lists as open.
