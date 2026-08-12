# B-1 and I-1 remediation record — independent Phase 2 gate review

Date: 2026-08-10
Findings addressed: **B-1** (Blocking), **I-1** (Important), **RA-4** (procedure
note, carried)
Source review:
[`phase-2-gate-independent-review-2026-08-09.md`](phase-2-gate-independent-review-2026-08-09.md)
— Codex, Independent Reviewer, 2026-08-09. (It was delivered through
`Handover information`, which is a two-way working channel and has since been
overwritten with the handoff; the review itself is preserved at the path above.)
Implemented by: Claude

This record closes two findings raised by the independent gate reviewer. **It is
not a gate decision, not an acceptance of I-03, and not evidence that any
rehearsal was performed.** No gate decision is recorded anywhere in this change,
as the handover required.

Both changes carry **no independent review**: they were implemented after the
independent review and have not been back through one. That is what the package
is being returned for.

**Read this first.** B-1 has been remediated **ten** times and **is not closed** —
the independent reviewer holds it open, and closing it is the reviewer's to do.

**The current rule is the tenth remediation, and it withdraws the other nine.**
Go straight to
[§ B-1, tenth remediation](#b-1-tenth-remediation--the-fence-and-the-end-of-settlement-by-observation).
Every section above it describes a mechanism that no longer exists: S-A, S-I
(including the S-I.3a–d inventory), S-D.2's commit watermark, S-D.3's
`LOCK TABLE … IN SHARE MODE` and S-D.4's queue and drain readings are all gone
from §9. They are retained here as the record of **why**, and that record has one
sentence: every one of them tried to infer quiescence from a point-in-time
observation, and an observation of a resource cannot exclude work that has been
accepted but has not yet reached it.

Settlement is now `tools.submission_admission close` — closing the submitting
credential's admission generation, which every submission checks inside its own
transaction. Nothing is stopped, and a reconciliation costs no downtime.

In order:

| Re-review | Verdict | What was wrong | Where the rule went |
|---|---|---|---|
| 2026-08-10 (first) | I-1 closed, **B-1 open** | S-B inferred the endpoint's *accept* order from the client's *issuance* order | second remediation: S-B.1 + S-B.2 |
| 2026-08-10 (second) | **B-1 open** | S-B.1 read `caddy_http_requests_in_flight` as a drain; Caddy documents it as the requests *currently being handled* | third remediation: **the probe and the gauge are withdrawn**; settlement is a stopped endpoint |
| 2026-08-10 (third) | **B-1 open** | stopping the *upstream* leaves a request the proxy holds and has not yet dialled upstream for; it connects after the restart, and step 4 detects the duplicate rather than preventing it | fourth remediation: **the endpoint-only stop is withdrawn**; settlement terminates the whole ingress path, and step 4 retires the route |
| 2026-08-11 (fourth) | **B-1 open** | S-I.3 was required and evidenced only by `Restart=no`, which proves far less; the claimed test mutation could not have been run as described; and only a settled *miss* had a way to bring the host back up | fifth remediation: **the rule stands** — S-I.3 gains four executable checks and an explicit Unsettled rule, the pair is rebuilt on one shared scenario and the mutation executed, and step 4 gains a restoration branch for every outcome |
| 2026-08-11 (fifth) | **B-1 open** | S-I.3d judged cron jobs and containers by their names — the same overclaim S-I.3b names one check earlier — and the unresolved branch assumed a stopped host, so `systemctl start` would silently no-op on two of its three entries | sixth remediation: S-I.3d becomes a bounded inventory read by contents; **S-D gains S-D.2**, a both-ends comparison; the unresolved branch reads its entry state and picks its verb from it |
| 2026-08-11 (sixth) | **B-1 open** | S-D.2's persistent readings all belonged to `caddy.service`, so a transient ingress that is not Caddy could serve and commit inside the window and leave every one of them unchanged; and the executable inventory printed a conclusion the operator had not read | seventh remediation: **the "still mints a new `InvocationID`" claim is withdrawn**; S-D.2 gains the **commit watermark** over the append-only tables, the counterexample is executed, and both presence checks report per name |
| 2026-08-11 (seventh) | **B-1 open** | the watermark is still an instant, and the miss is recorded after it: an unenumerated ingress that starts *after* the closing reading commits before the record, so the miss is false and every reading matches. The discovery-command correction was accepted | eighth remediation: **S-D gains S-D.3** — the decisive reading is taken inside a transaction holding a `SHARE` lock on the two append-only tables, and the lock is held until the outcome has been written down |
| 2026-08-11 (ninth) | **B-1 open** | S-D.4 **moved** the race into the drain transaction rather than closing it: a request paused before its first conflicting statement is queued behind nothing, appears in no `pg_locks` reading, and commits after the drain read has matched and the miss has authorized a fresh export. Route retirement cannot reach a transaction already inside PostgreSQL | tenth remediation: **every observation-based condition is withdrawn.** Settlement closes a durable **admission generation** the submitting credential writes under; the check is inside each submission's own transaction, against the principal id in its own bytes, and a closure and an acceptance cannot interleave |
| 2026-08-11 (eighth) | **B-1 open** | the lock **delays** the race rather than closing it: a writer that arrives while it is held waits inside PostgreSQL and commits the instant it is released, before step 4 retires anything — and the control test read that as the successful case. Plus one Important: `idle_in_transaction_session_timeout = 0` left the platform-wide pause unbounded | ninth remediation: **S-D gains S-D.4** — the queue behind the lock is read and any waiter is Unsettled, the miss is confirmed by a drain read taken after the lock is released, the idle timeout is bounded, and the whole mechanism is tested against a real PostgreSQL |

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
  episode with the proxy terminated as well as the endpoint. Its thread ends
  without ever dialling, the client's connection dies where it stood, and the
  restart brings back an endpoint that nothing arrives at.

> **Superseded, and the claim that stood here was false.** This section originally
> said the two tests differed in **one line**, and that deleting `proxy.terminate()`
> from the second made it fail on `assert not proxy.dialled`. Neither held. The two
> tests were hand-written copies whose sequences diverged after the stop, and the
> deletion blocked at the `proxy.join()` immediately following the terminate call —
> the assertion the claim named was never reached, so the mutation had never been
> run as described. The pair is rebuilt on one shared scenario in the
> [fifth remediation](#b-1-fifth-remediation--the-evidence-for-s-i3-the-mutation-that-was-never-run-and-the-outcomes-that-never-came-back-up),
> where the mutation is executed and its output recorded.

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
| 8 | `systemctl show caddy -p Restart` is **`no`** | ~~S-I.3 on the real unit: nothing brings Caddy back on its own~~ — **withdrawn as an overclaim.** It settles what the unit does when the process exits on its own, and nothing about socket activation, timers, path units, units that pull Caddy in, supervisors outside systemd, or a second route to the endpoint's port. S-I.3 is established by rows 13–16 |
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

## B-1, fifth remediation — the evidence for S-I.3, the mutation that was never run, and the outcomes that never came back up

Date: 2026-08-11. Findings from the fourth re-review: one Blocking and two
Important. The fourth remediation's **rule** survives all three — nothing here
withdraws S-A, S-I, S-D or step 4's retirement. What the reviewer found was that
two of the rule's parts were asserted rather than established, and that a third
part of the procedure had no exit.

### What was still wrong

**1. S-I.3 was required and not established (Blocking).** S-I.3 claims that no
unit, timer, path unit, watchdog, supervisor, tunnel or second proxy can restore
ingress before the outcome is recorded. It was three sentences of prose with no
command to run and no recorded evidence, and the one row offered for it —
`systemctl show caddy -p Restart` returning `no` — proves substantially less than
the claim. `Restart=no` governs what the unit does when the process exits on its
own. It is silent on socket activation, on a timer or path unit, on another unit
pulling Caddy in, on a supervisor that is not systemd, and on a second listener
reaching the endpoint's port without Caddy at all. An operator could satisfy the
recorded evidence in full and still have ingress restored underneath them.

**2. The claimed mutation was not what the package contained (Important).** The
fourth remediation said the two `_a_request_held_by_the_proxy_` tests differed in
one line, and that deleting `proxy.terminate()` from the second made it fail on
`assert not proxy.dialled` where the proxy forwards across the restart. The tests
were two hand-written copies whose sequences diverged immediately after the
endpoint stop: the S-I copy called `proxy.join()` on the next line, the other
waited on `forwarded` after the restart. Deleting the terminate call therefore
blocked that `join()` until it timed out and failed with "the proxy thread never
finished". Release and restart came later; the named assertion was never reached.
**The mutation had not been run as described** — the fifth overclaim of this
package's kind, and the reason a negative control has to be executed rather than
narrated.

**3. Only one of four outcomes could bring the service back (Important).** S-D
takes the whole host down and holds it there until step 3's outcome is recorded.
Step 4 was "only for a settled miss". A **hit** ended step 3 by recording the row
and continuing Council review; **Ambiguous** and **Unsettled** ended it by
escalating. None of the three had an executable restoration sequence, so on three
of the four outcomes the procedure's last instruction left Caddy stopped and every
service on the host — all three Foundry instances among them — with it, for an
unbounded time.

### The corrected rule

**S-I.3 is now four checks with commands, and no partial pass.** S-I.3a reads the
unit's own restart surface (`Restart`, `RestartSec`, `TriggeredBy`, `BindsTo`,
`WatchdogUSec`, `OnFailure`, `DropInPaths`, `UnitFileState`) and the reverse
dependency tree; S-I.3b reads timers and path units, **and the unit behind
anything the listing shows**, because a timer's name does not say what its service
does; S-I.3c looks for a second way to `127.0.0.1:8757` — competing listeners with
process names, proxy and tunnel processes, and Caddy's admin endpoint on 2019,
which is both a configuration-replacement vector and a third witness that Caddy is
gone; S-I.3d looks for a supervisor that is not systemd — containers, supervisord,
monit, cron, `at`.

Two consequences are stated where the operator meets them. **Any of the four that
cannot be read is Unsettled**, as is any that comes back positive; there is no
weaker fallback, because S-I.3 is a claim about what cannot happen and an unread
check is not evidence that nothing will. And two of the commands need privilege —
`ss -p` to name another user's socket, root's crontab — so **an operator without
`sudo` on this host cannot establish S-I.3c or S-I.3d, and must record Unsettled
and escalate.** That is a concrete, reachable **Unsettled**, which the fourth
remediation listed as an open question about the procedure; it is now an example
in it. Step 3's Unsettled branch names the same trigger, so the two cannot drift.

**One vector is named as not closable.** `UnitFileState=enabled` is expected on
this host and is not a failure of S-I.3a, but it means a **reboot** restores Caddy.
Nothing in S-A, S-I or S-D survives a reboot, and §9 now says so: a reboot before
the outcome is recorded voids settlement exactly as an operator restart would.

**The test pair is rebuilt on one shared scenario.**
`_held_request_episode(artifacts, *, terminate_the_proxy)` holds the whole
sequence — the held-and-undialled request, the endpoint stop, the two missing
queries, the restart on the same port and path, the release, and the wait for the
proxy thread — and `terminate_the_proxy` guards exactly one statement,
`proxy.terminate()`. The wait is what lets both runs share the line: a terminated
proxy's thread returns without dialling, a live one dials, forwards, and then
returns. The two tests are now assertions over a common episode rather than two
copies of it, so "the termination call is the only behavioural variable" is a
property of the code instead of a claim about it.

**Step 4 becomes "bring the path back, on the route the outcome chooses",** with
three branches and a table. Every episode reaches it; what step 3 decides is what
answers the submission path afterwards, not whether the service returns.

| Step 3 said | Submission path afterwards | Fresh export |
|---|---|---|
| **Miss** | `410`; the fresh export goes through a single-use recovery route | authorized |
| **Hit** | the §5.4 route, unchanged | forbidden |
| **Ambiguous** or **Unsettled** | `410`, with no recovery route | forbidden |

The asymmetry is argued from the checksum rather than chosen. Retirement matters
exactly when a **fresh export with a different checksum** has been authorized,
because only then can the stranded request become a *second* artifact. After a hit
none is authorized, so the most a stranded request can carry is the episode's own
bytes: the uniqueness constraint refuses a second row for them and a same-key
retry writes no event. The hit branch therefore restarts on the unmodified §5.4
configuration, verifies from off the host that the path answers `401` — the
application's own answer, the only one that proves it is reachable through Caddy —
confirms the three Foundry sites, and re-runs step 2's query across the restart.
One specific second row is expected rather than alarming there: **same checksum,
`duplicate = true`** is the stranded request absorbed, one artifact and two
acceptance events. A second row with a **different** checksum is Ambiguous.

The unresolved branch takes the combination that gives up nothing: the site comes
back and the submission path does not. Retire the path with `respond 410`, add no
recovery route, restart, verify the `410` and the Foundry sites, and hold the
episode open with the host up. Retirement costs nothing there, because no
submission is permitted during an unresolved episode in any case — it removes an
option the operator did not have, and with it the one way an unresolved episode
could quietly become a second artifact.

### Evidence

**Read-only checks against this host, 2026-08-11**, with Caddy **running**. These
establish restart *vectors*, which is what S-I.3 is about, and every one of them is
readable in that state. **No service was stopped, started, reloaded or
reconfigured, and this is not a settlement rehearsal.**

| | Observed | What it settles |
|---|---|---|
| 13 | `Restart=no`, `TriggeredBy=`, `BindsTo=`, `OnFailure=` and `DropInPaths=` all empty, `WatchdogUSec=0`, `UnitFileState=enabled`; `systemctl list-dependencies --reverse caddy.service` shows only `multi-user.target` → `graphical.target` | S-I.3a on the real unit. **No socket activation and no watchdog** — which `Restart=no` never said — and nothing pulls Caddy in but its own enablement. The `enabled` state is the reboot vector, now written into §9 as not closable |
| 14 | 14 timers and 6 path units on the host; **none** whose service references Caddy or the endpoint | S-I.3b. The check is the listing *plus* reading the units behind it, which is how this was established |
| 15 | no `nginx`, `haproxy`, `apache2`, `traefik`, `envoy`, `cloudflared`, `ngrok`, `frpc`, `socat`, `stunnel` or forwarding `ssh` process; no Docker and no Podman installed; no supervisord, monit or runit; no user crontab; `/etc/cron.d` holds `e2scrub_all` and `sysstat` only; `at` not installed | S-I.3c's process half and S-I.3d. Nothing outside systemd owns either process on this host today |
| 16 | a loopback listener on **`127.0.0.1:2019`** — Caddy's documented default admin endpoint — while Caddy runs, alongside `127.0.0.1:5432` for PostgreSQL and the two TCP and one UDP `:443` listeners | S-I.3c's port half, and the reason 2019 is in the check: an admin API that answers can be handed a whole new configuration without `systemctl`, and it dies with the process, so a row on it during a down window contradicts S-I.1 |

**What these checks did *not* establish, and it matters more than what they did.**
This session had **no passwordless `sudo`**. `ss -ltnup` therefore could not name
the processes behind the root-owned listeners (`:80`, `:443`, `:22`, `:5432`), and
root's crontab was not read. Under the rule written above that is not a partial
pass — **it is Unsettled**, and it is the first worked example of an operator
reaching that outcome for a reason other than a running process. Row 16's listener
is identified as Caddy's admin endpoint by port and documentation, **not** by
process attribution.

**The mutation, executed this time.** With the pair rebuilt on the shared
scenario, `proxy.terminate()` was replaced by `pass` inside the one guarded
statement and the pair was run:

```text
tests/test_snapshot_recovery_settlement.py::…_commits_after_the_endpoint_restarts PASSED
tests/test_snapshot_recovery_settlement.py::…_dies_when_the_proxy_is_terminated  FAILED

>           assert not episode.proxy.dialled
E           AssertionError: assert not True
E            +  where True = <…_HoldingProxy object at 0x…>.dialled

1 failed, 1 passed, 5 deselected
```

The control test still passes with the mutation in place, which is the point: with
S-I deleted the two tests execute identical code, so the one that expects the
request to have died is the only one that can fail. The mutation was then reverted
and the file restored from a copy taken before it, and the suite re-run.

### What remains open in this remediation

- **B-1 itself.** It is remediated a fifth time, not closed, and this record still
  carries no independent review.
- **S-I.3 is established for this host on this date, not for all time.** Rows
  13–16 are a snapshot of what exists now. Installing a container runtime, a
  second proxy, a socket unit or a monitoring agent invalidates them, which is why
  §9 makes the operator run the four checks during the episode rather than cite
  this table.
- **The privileged half of S-I.3c and S-I.3d is unread.** An operator with `sudo`
  should run both once outside an episode and record the result, so the first time
  they are read is not under time pressure.
- Everything the fourth remediation left open: the Phase 3 improvement, whether
  host-wide downtime is acceptable beyond Phase 2, and the unexecuted public-site
  half of step 4's validation.
- The hit and unresolved restoration branches are **written and tested as
  documentation, not rehearsed.** No operator has followed either, and the hit
  branch's `401` check and the unresolved branch's `410` check have not been run in
  the configurations those branches describe — though step 4 phase 1 (row 12)
  exercised the same `410` and `401` pair on the production config and reload path.

## B-1, sixth remediation — the inventory states its bound, and the window is closed from its far end

Raised by the re-review of the fifth remediation on 2026-08-11, which held B-1
Blocking on two findings. **Nothing in C-18 or C-19 is withdrawn.** S-A, S-I, S-D,
the route retirement and the three restoration branches all stand. Change-log
**C-20**.

### What was still wrong

**1 — S-I.3d listed names where it needed to read jobs.** The check claimed that
no supervisor outside systemd owns either process, and ran `docker ps -a`,
`podman ps -a`, `supervisorctl status`, `monit summary`, `crontab -l`,
`sudo crontab -l`, `ls -la /etc/cron.d/` and `atq`. None of that establishes the
claim:

- `ls -la /etc/cron.d/` produces **filenames**. It never opens a cron file, so what
  the jobs behind those names actually do was never read;
- `/etc/crontab` was not read at all, nor `/etc/cron.{hourly,daily,weekly,monthly}`,
  nor the crontabs of any user other than the operator and root;
- `docker ps -a` lists containers. A **restart policy** and an **entrypoint** are
  what make a container a restart vector, and neither appears in a listing.

The reviewer's characterisation is exact and is the part worth keeping: this is
**the same overclaim C-19 itself identified for timer names one check earlier**.
S-I.3b says in so many words that a timer's name does not say what its service
does, and then S-I.3d judged cron jobs and containers by their names.

The consequence is not theoretical. A scheduled or supervised start that fires
**after the four checks pass and before the outcome is written down** brings Caddy
back on the **§5.4 configuration** — the live submission route, because nothing has
amended it yet — and a request held upstream can be delivered while the operator is
concluding the episode was a miss.

**2 — the unresolved branch assumed a host that was down.** It opened "the host is
down now" and instructed the maintainer to amend the Caddyfile, restart the
endpoint and `start` Caddy. Only one of its three entries has that property:

| Entered from | Caddy | Endpoint |
|---|---|---|
| **Ambiguous** at step 3 | down, under S-D | down |
| **Unsettled** | **may be running** — that is what Unsettled means | **may be serving** |
| the **hit** branch's step (5) | **running** — this branch started it | **running** |

`systemctl start` against a running unit is a **no-op that reports success**. On
two of the three entries the amended Caddyfile would therefore never load, and
§5.4's live submission route would survive the branch whose entire purpose is to
retire it — with the `410` check at the end the only thing standing between that
and an unnoticed live route. Restarting the foreground endpoint against a running
one is worse than a no-op: it has no unit, and nothing makes starting it twice safe.

### The corrected rule

**S-I.3d is bounded, and says so.** It no longer claims that no supervisor exists
on this host; nothing an operator can run establishes that. It claims that **every
start mechanism the topology record documents was read in full, and none of them
starts either process** — container runtimes by presence and then by restart policy
and entrypoint, `/etc/crontab` and `/etc/cron.d/*` by **contents**, `run-parts
--list` per directory, `/var/spool/cron/crontabs/` for who actually has a crontab,
the crontabs of `root`, `foundry` and `discordbot`, `at`, and the per-user systemd
managers — closed by a `grep` over the job *contents* for `caddy`, `snapshot_api`
and `systemctl start|restart`. The users are the ones
[topology §1](../operations/topology.md)'s component table names, plus `root`, and
**a user in the spool or in `loginctl` that the table does not name is Unsettled**:
not because that user is suspect, but because the bound has broken.

**S-D gains S-D.2, and it is what actually closes the reviewer's window.** No check
run in advance forbids a start after it. So the same readings are taken at both
ends of the down window and compared: `InvocationID`, `ActiveEnterTimestampMonotonic`,
the listener list, and the journal for the window. **Any difference is Unsettled,
not a miss**, and **a miss may not be recorded without the comparison.** A start
from a mechanism nobody enumerated still mints a new `InvocationID` — which is
precisely why a retrospective comparison can close a gap a prospective inventory
cannot. S-I.3 is thereby demoted to what it can support: it makes a mid-episode
restart rare, and S-D.2 establishes that none happened this time.

**The unresolved branch reads its entry state.** `systemctl is-active caddy`, the
listeners, and `pgrep -af 'snapshot_api'`, recorded before anything is changed.
Then the rollback copy is taken **before** the edit, `caddy validate` runs before
anything loads, and Caddy is brought to the amended configuration by the verb its
actual state allows — `start` when inactive, **`reload` when active** — with the
copy restored on any failure. The endpoint is started only if it is not running,
and is otherwise left alone with that recorded. `activating`/`deactivating` is
neither state and is waited out. The miss branch, which amends the same file, gets
the same copy-and-validate discipline.

### Evidence

The bounded inventory was run **read-only against this host on 2026-08-11**, and it
found something the old check could not — rows **17–19** of
[`phase-2-b-1-settlement-observations-2026-08-10.md`](phase-2-b-1-settlement-observations-2026-08-10.md).

**LXD is installed on this host.** `snap.lxd.daemon.unix.socket` is listening,
`snap.lxd.daemon.service` is socket-activated — the same vector S-I.3a names for
`caddy.socket` — and `snap.lxd.activate.service` starts `boot.autostart` instances
at boot. C-19's row 15 ran `docker ps -a` and `podman ps -a`, got "not installed"
from both, and recorded *"no Docker, Podman, supervisord, monit or runit"*. Every
word of that is true, and it is silent about **the one container runtime that is
here**, because the check was a list of names somebody thought of rather than an
inventory bounded by anything. Whether LXD holds an instance is **unread** —
`lxc list` needs `root` or the `lxd` group, which has no members — and under the
corrected rule that is **Unsettled, not a pass**.

Cron was read in full: `/etc/crontab`'s four `run-parts` lines, `e2scrub_all` and
`sysstat` in `/etc/cron.d`, six `cron.daily` jobs and one `cron.weekly` job, and no
job's **contents** reference `caddy`, `snapshot_api` or `systemctl start|restart`.
The names were in fact benign — but that is now a fact established by reading them.

**Nothing was stopped, started, reloaded or reconfigured. No maintainer-authorized
window was used or needed.**

### Three more things this package claimed and got wrong, all self-reported

All three were found the same way as the earlier ones — by running the commands
rather than re-reading them.

Writing S-D.2 produced the load-bearing one. The first draft offered **`NRestarts`** as
one of the readings that catches a mid-episode restart. It does not. It counts
restarts performed by the unit's own `Restart=` logic, and this unit is
`Restart=no`. The host says so directly: `NRestarts=0` sitting beside a **non-zero**
`ActiveExitTimestampMonotonic`, which is the 2026-08-10 authorized stop and the
start after it — a real stop and a real start, and the counter did not move.

A `systemctl start` from cron, from a supervisor or from a second operator has
exactly that shape, so `NRestarts` would have been **silent for the case S-D.2
exists to catch**. §9 now says this inside the check and rests on `InvocationID`,
which is minted fresh on every start regardless of who asked for it. Two other
first-draft commands were wrong until they were run: `run-parts --list` takes one
directory per call and fails with `missing operand` when given four, and the
container check had to name `lxc`/`lxd` before it found anything on this host.

### What remains open in this remediation

- **B-1 itself.** Remediated a sixth time, not closed, and this record still
  carries no independent review.
- **S-D.2 has never been run.** Taking it needs a real down window at both ends,
  and no episode has been run since it was written. What rows 19 establish is only
  that its readings exist, are stable when nothing happens, and that one of the four
  is weaker than it looks. **That the comparison catches a restart is not claimed.**
- **LXD's instance list is unread**, and it is now the only unread item known to
  exist rather than merely possible. An operator with `sudo` should read it and
  each instance's `boot.autostart` before the next review.
- **The privileged half of S-I.3c and S-I.3d is still unread**, and S-I.3d's
  privileged half is now larger: the other users' crontabs,
  `/var/spool/cron/crontabs/`, the per-user managers, and LXD.
- The unresolved branch's entry read and its `reload` path are **written and tested
  as documentation, not rehearsed** — as are the hit branch's, unchanged from the
  fifth remediation.
- Everything the fourth and fifth remediations left open.

## B-1, seventh remediation — S-D.2 reads the destination, not only the route

Raised by the re-review of the sixth remediation on 2026-08-11, which held B-1
Blocking on one finding and raised one Important. **Nothing in C-18, C-19 or C-20
is withdrawn** except the one sentence named below. Change-log **C-21**.

### What was still wrong

**1 — S-D.2 detected Caddy restarts, and a miss does not depend only on Caddy.**
Every persistent reading the comparison rested on — `InvocationID`, the two
timestamps, the journal — belongs to `caddy.service`. The listener list is not
persistent at all: it is sampled at the two ends of the window, and a process
that starts and exits between the samples is in neither of them. So this stayed
reachable, and it is the reviewer's sequence:

1. both opening readings are clean, and the query returns no row;
2. an unenumerated mechanism transiently starts the endpoint and another
   listener or proxy on the public port;
3. a request held upstream is delivered and commits;
4. those transient processes exit;
5. the closing socket list is empty again, and Caddy's identity, timestamps and
   journal are unchanged;
6. the procedure permits recording a miss.

The sixth remediation asserted the opposite in one sentence — *"a start mechanism
nobody enumerated still mints a new `InvocationID`"* — and **that sentence is
withdrawn as false.** It is true of a mechanism that starts *Caddy*. It is not
true of one that does not go near `caddy.service`, and that is exactly the class
S-I.3d's bound admits it cannot enumerate. The claim that S-D.2 closed S-I.3's
residual therefore did not hold: the two checks had the same blind spot, and
pairing them did not remove it.

The sixth remediation's new test made the same mistake at the other end. It
asserted that §9 *contains* the proposed Caddy readings. Nothing in it exercised
the transient alternate ingress, so nothing in it could have failed on the case
above.

**2 — the executable inventory printed a conclusion the operator had not read.**
S-I.3d passed six names to one `command -v` and hung `|| echo 'no container
runtime'` off its exit status; the supervisor check did the same with five.

The reviewer's stated mechanism — that `command -v` fails when *any* name is
absent, so an installed `lxc` could be followed by "no container runtime" — is
**not what these shells do**, and the record should say so rather than accept a
diagnosis it can check. Measured on this host, `bash` 5.2.21 and `dash` both exit
`0` when *at least one* name is found, so on this host the old line printed two
LXD paths and no false conclusion. The finding's *substance* stands anyway, on
two grounds the check cannot argue with:

- the multi-operand form is an extension. POSIX defines `command -v` for **one**
  `command_name`, so the exit status the conclusion hangs on is shell-dependent,
  and §9 does not control the shell an operator pastes into;
- and in every shell the output is six names' worth of question answered by
  however many paths, leaving the reader to match them up. **C-20 exists because
  precisely that reading missed LXD**, so this check of all checks may not emit a
  summary line the operator has to trust.

### The corrected rule

**S-D.2 takes three readings at each end, and the third is what a miss rests on.**
The Caddy readings stay, scoped to what they can support — `InvocationID` remains
load-bearing **for that unit**. The listener list stays, named as two samples
rather than a state. Added to them is the **commit watermark**:

```sql
SELECT count(*) AS snapshots, max(received_at) AS newest FROM foundry_snapshots;
SELECT count(*) AS snapshot_events, max(occurred_at) AS newest
  FROM audit_events WHERE entity_type = 'foundry_snapshot';
```

It closes the class because **it reads the destination rather than the route**. An
accepted submission commits, in one transaction, one
`snapshot_submission.accepted` audit event on the `foundry_snapshot` entity and —
unless those exact bytes were already stored — one `foundry_snapshots` row; a
refusal taken after authentication commits a `snapshot_submission.refused` event
on the same entity, so a transient ingress that served a request and declined it
is caught as well. Both tables are in `APPEND_ONLY_TABLES`, the runtime role holds
only `SELECT, INSERT`, and a trigger rejects `UPDATE`/`DELETE` even for the schema
owner — so the counts are monotone and cannot be walked back by whatever moved
them. A commit inside the window moves them whether it arrived through Caddy or
around it, from a mechanism in the topology table or from one that is not in it,
and whether or not the process that accepted it still exists when the closing
reading is taken. **Any difference in any of the three is Unsettled, not a miss.**

What the watermark does **not** do is stated in §9 rather than left for the next
review: it compares two instants like the others, so it says nothing about a
commit landing after the closing reading — which is why that reading is the last
act before the outcome is written, why S-D holds both processes down until it is,
and why step 4 retires the route and re-queries afterwards. It also moves for a
write this episode did not cause, such as a Council import applied on this host
during the window, and that is Unsettled too and correctly so.

The journal is now read for the manager as well as for the unit
(`journalctl … _PID=1 + _COMM=sudo`), because a unit started under some other name
is still a start this episode has to know about. It is supporting, not
load-bearing: a transient process started outside systemd writes nothing there,
which is the whole reason the watermark exists.

**The inventory states its result per name.** Both presence checks became a loop
over one name per call, printing `present <name> <path>` or `absent  <name>`, with
the conclusion drawn only after all of them have been read.

### Evidence

Run on this host on 2026-08-11, read-only. **Nothing was stopped, started,
reloaded or reconfigured, and no maintainer-authorized window was used or needed.**

- **the shell measurement above.** `command -v bash nope` exits `0` in `bash`
  5.2.21 and in `dash`; `command -v nope1 nope2` exits `1`. That is what makes the
  reviewer's stated mechanism wrong and the reviewer's remedy right anyway;
- **the corrected loop, run.** It prints `present lxc /usr/sbin/lxc` and
  `present lxd /usr/sbin/lxd` beside four `absent` lines, and five `absent` lines
  for the supervisors — the C-20 finding stated by the command instead of by a
  reader who happened to look;
- **the watermark's columns exist.** The two statements were compiled against the
  real `adapters/database/tables.py` metadata for the PostgreSQL dialect. **They
  were not executed**: no database was contacted in this session, and the
  PostgreSQL-backed tests remain skipped.

**The counterexample is now executed, not asserted.**
`test_a_transient_alternate_ingress_is_caught_only_by_the_commit_watermark` runs a
real endpoint and a real proxy that exist only between the two readings, delivers
a request held by a hop the operator cannot terminate, and commits a submission
through them. It then asserts that the Caddy readings and both listener samples
are identical across the window, and that the watermark is not. Its control,
`test_the_commit_watermark_is_unchanged_when_the_window_was_actually_quiet`, is
the same episode with the transient ingress never started.

The `caddy.service` stand-in mints its `InvocationID` from a `start()` and from
nothing else, so the equality assertion is a fact about the episode rather than
about a constant. **Mutation run:** adding `caddy.start()` to the transient block
fails the test on `'caddy.service-invocation-2' != 'caddy.service-invocation-1'`;
reverted and re-run.

### What remains open in this remediation

- **B-1 itself.** Remediated a seventh time, not closed, and this record still
  carries no independent review.
- **S-D.2 has still never been run against a real down window**, and the
  watermark's two statements have never been executed against a real database.
  What is established is that the columns exist, that the entity type and both
  action names match the service's, and that the counterexample the readings must
  survive is reproduced in the suite.
- **The watermark's completeness rests on the submission service being the only
  writer of these two tables on the accepted path**, which is read from
  `application/foundry/submission.py` and guarded by a test that fails if the
  entity type or either action name is renamed. It is not established by a
  database-level audit of every writer.
- Everything the fourth, fifth and sixth remediations left open, including LXD's
  unread instance list and the privileged half of S-I.3c and S-I.3d.

## B-1, eighth remediation — the decisive reading is held through the recording

Raised by the re-review of the seventh remediation on 2026-08-11, which held B-1
Blocking on one finding and confirmed the discovery-command correction. **Nothing
in C-18, C-19, C-20 or C-21 is withdrawn.** Change-log **C-22**.

### What was still wrong

**S-D.2 closed the interval between its two readings and left the one after them
open.** The document said as much — the watermark "is a comparison of two instants
like the others, so it says nothing about a commit that lands *after* the closing
reading" — and then answered it with **ordering**: the reading was made the last
thing done before the outcome was written. The outcome is still written by hand,
afterwards, from figures already taken, and the mechanism the watermark exists for
runs in that gap:

1. the opening watermark is read;
2. both step-2 queries miss;
3. the closing Caddy, listener, journal and watermark readings all match;
4. **after** that closing read, an unenumerated endpoint and proxy start;
5. the held request commits and both transient processes exit;
6. the operator records the miss from the already-obsolete readings.

That is a false settled miss. Holding the known Caddy and endpoint processes down
does not prevent it, because the counterexample uses processes outside that
inventory — the same class S-I.3d's bound admits it cannot enumerate. Step 4's
later retirement and query may discover the mistake afterwards; they cannot make
an already-recorded miss true, and the miss is what authorized the fresh export.

**The seventh remediation's test could not have caught it.** It stops the
transient ingress before taking the closing reading, so what it proves is that the
watermark catches a commit landing between its two samples. It says nothing about
the interval that runs from the closing sample through to the recording.

### The corrected rule

**S-D.3 — the decisive reading is held rather than sampled, and the hold outlives
the recording.** The closing watermark and step 3's repeated acceptance-event query
are taken inside a transaction that first does:

```sql
SET lock_timeout = '15s';
SET idle_in_transaction_session_timeout = 0;
BEGIN;
LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE;
```

`SHARE` conflicts with the `ROW EXCLUSIVE` an `INSERT` takes, so for as long as
that transaction is open nothing can commit an acceptance **or** a refusal to
either table, whatever is serving and whether or not it was ever enumerated. The
session is left open while the rest of the closing comparison is taken and while
the outcome is written down; only then does the operator confirm the lock in
`pg_locks` and `COMMIT`. The reading a miss rests on is therefore a state that
spans the recording rather than an instant preceding it.

Three things are stated in §9 rather than left to be worked out:

- **the privilege.** `SELECT` does not carry this lock mode, so S-D.3 runs as the
  **schema owner** and not as step 2's read-only account. Not being able to take
  the lock is Unsettled, not a miss;
- **every failure mode is Unsettled.** A `lock_timeout` expiry means something was
  inserting at the moment the window was supposed to be shut, which is the
  discovery rather than an obstacle to it. A deadlock, a lost session, an aborted
  transaction, a `held` count other than 2, or a `COMMIT` that does not succeed all
  mean the reading was not held through the recording — so it is a sample again,
  and a miss may not rest on it;
- **what it costs.** The lock pauses inserts into `audit_events` platform-wide, so
  an unrelated Discord command waits for the transaction to end. That is why the
  transaction contains the readings and nothing else.

**The boundary with step 4 is now explicit.** S-D.3 covers everything up to and
including the instant the miss is written down; step 4's route retirement prevents
a later delivery and its post-recovery query detects a failure of the prevention.
A commit landing after the `COMMIT` is a later commit, not a miss that was never
true.

### What was considered and not done

- **retiring the §5.4 route before the decisive read** — the reviewer's first
  suggestion. It closes the interval only for requests arriving through Caddy, and
  the counterexample is an endpoint and a proxy that are not Caddy at all. The
  retirement stays where it is, answering a different question: what a hop in front
  of this host can still deliver afterwards;
- **a third watermark sample immediately before the record** — rejected, and named
  in §9 so it cannot come back as a simplification. It moves the interval;
- **recording the miss into the database in the same transaction as the check** —
  the reviewer's second suggestion. Rejected because the operational record is not
  a domain table and `audit_events` is not where an operator's conclusion belongs;
  the lock gives the same guarantee without inventing a schema for it;
- **revoking the runtime role's `INSERT` for the duration** — rejected as a durable
  privilege change made under incident conditions, with a restore step that must
  not be forgotten. A transaction-scoped lock releases itself.

### Evidence

**The counterexample is executed, not asserted.**
`test_a_commit_after_the_closing_reading_is_a_false_miss_without_the_settlement_lock`
runs the same transient ingress the seventh remediation added — a real endpoint and
a real proxy, delivering a request held by a hop the operator cannot terminate —
but starts it **after** the closing reading. All three of S-D.2's readings are
identical at both ends, and the state the miss is recorded from is not the state
that was read: the watermark is `(1, 1)` and the query returns a row. Its control,
`test_the_settlement_lock_holds_the_window_shut_until_the_outcome_is_recorded`,
is the same episode with the lock taken before the closing reading: the ingress
still receives the request and still reaches its commit, the commit cannot
complete, the miss is recorded against the watermark that was read, and the commit
lands only once the lock is released.

The two are one episode function differing in one flag, which is what makes the
control checkable rather than asserted. **Mutation run:** replacing the guard on
`lock.acquire()` with `False` fails the control on *"the commit did not wait for
the settlement lock"*; reverted and re-run.

`tests/test_snapshot_recovery_documentation.py` gains
`test_the_decisive_reading_is_held_through_the_recording_of_the_outcome`, which
binds the procedure to the mechanism, the privilege, the two session settings, the
`pg_locks` confirmation, every Unsettled failure mode, the rejected route-retirement
alternative, the platform-wide cost, and the boundary with step 4.

**No database was contacted.** The lock mode's conflict with `ROW EXCLUSIVE`, the
privilege it requires and the `pg_locks` predicate are taken from PostgreSQL's
documented behaviour. The settlement test models the lock at the commit boundary
of the unit of work, which is where a test without PostgreSQL can observe it; the
acquire side — a real `LOCK TABLE` waiting for an insert already in flight — is
deliberately not modelled, because that path ends the episode as Unsettled and
cannot produce a recorded miss at all.

### What remains open in this remediation

- **B-1 itself.** Remediated an eighth time, not closed, and this record still
  carries no independent review.
- **S-D.3 has never been run.** No `LOCK TABLE` was executed, no `pg_locks` row was
  read, and the platform-wide pause it causes has not been observed against the
  running bot. S-D.2 remains unrehearsed for the same reason.
- **The lock's completeness rests on the same claim the watermark does** — that
  every acceptance and every post-authentication refusal on this path commits to
  one of these two tables — which is read from `application/foundry/submission.py`
  and guarded by a test, not established by a database-level audit of every writer.
- Everything the fourth to seventh remediations left open, including LXD's unread
  instance list and the privileged half of S-I.3c and S-I.3d.

## B-1, ninth remediation — the queue behind the lock, and the miss confirmed after it opens

Raised by the re-review of the eighth remediation on 2026-08-11, which held B-1
Blocking on one finding and raised one Important. **Both are accepted in full.**
Nothing in C-18 to C-21 is withdrawn; **one sentence of C-22's is withdrawn as
false**, and one of its session settings is replaced. Change-log **C-23**.

### What was still wrong

**S-D.3 delayed the race and the document said it had closed it.** `SHARE`
conflicts with `ROW EXCLUSIVE`, which is why nothing can *commit* while the lock is
held — but a conflicting `INSERT` that arrives in that window does not fail and does
not go away. It **waits**, inside PostgreSQL, and it is granted its lock the instant
the settlement transaction ends:

1. the lock is taken and the decisive reading says nothing has committed;
2. the episode's stranded request is delivered by something in front of this host,
   reaches its `INSERT`, and queues behind the lock;
3. the operator records the miss — truthfully, of the state that was read — and
   authorizes a fresh export;
4. the `COMMIT` releases the lock and the queued submission commits **at once**,
   before step 4 has retired anything;
5. the fresh export lands beside it under a different checksum, which uniqueness
   cannot merge.

**Step 4's retirement cannot answer it**, and the eighth remediation's claim that
the two "divide the timeline between them and leave no gap" was therefore false.
The retirement takes an address away; a transaction waiting on a lock has already
been accepted, is already inside the application, and is past every hop the
retirement acts on.

**The eighth remediation's own control test demonstrated the defect and read it as
the successful case.** `test_the_settlement_lock_holds_the_window_shut_until_the_
outcome_is_recorded` established a blocked writer, recorded zero hits, released the
lock and then *required* the original acceptance to commit — the reviewer's exact
sequence, asserted as correct behaviour.

**The Important finding, and it is unrelated to the race.**
`SET idle_in_transaction_session_timeout = 0` disabled the only bound on a
transaction that blocks every audit insert on the platform. An operator who is
called away mid-recording holds the Discord bot's audit writes indefinitely.

### The corrected rule

**S-D.4 — a shut door is not an empty one, so the queue is read too, and the miss
is confirmed after the lock is released.** Two readings, and one separation:

- **the queue is read inside the lock** — ungranted relation-lock requests by any
  other backend on either table — taken with the decisive reading and again as the
  last statement before the `COMMIT`. **Any row is Unsettled.** A waiting
  `RowExclusiveLock` is a commit the procedure has postponed, not one it has
  prevented, and an episode with one is exactly as unresolved as an episode whose
  watermark moved;
- **the miss is confirmed by a drain read** taken immediately after the `COMMIT`,
  in the same session: the same lock again, which PostgreSQL grants only behind the
  requests already queued, with the watermark read inside it. A figure that has
  moved **retracts the miss**, and the episode becomes Unsettled;
- **recording the miss and authorizing the fresh export become two steps.** The
  record is written under the lock, where S-D.3 makes it true of the window; the
  authorization comes after the drain read, where S-D.4 makes it safe to act on.
  Collapsing them is the defect.

The Important finding is taken by bounding the setting rather than removing it:
`idle_in_transaction_session_timeout` is `'10min'`, which exceeds the recording
window, and an expiry aborts the transaction — Unsettled, never a miss. `0` is named
in §9 as what must not be used, with the reason.

**A third correction, which only running it could have found.** The queue reading is
over **`pg_locks` alone**. The obvious form joins `pg_stat_activity` to name the
waiting session, and inside S-D.3's long-lived transaction that form silently loses
the case it exists for: `pg_locks` is read live from the lock manager, but a
backend-status snapshot is taken at the first `pg_stat_activity` read in a
transaction and reused for the rest of it — so the second queue reading is answered
from the state at the first, and the writer that matters connected after it. §9 now
decides on `pg_locks` and keeps the join only as a follow-up that names the
sessions, after `pg_stat_clear_snapshot()`.

### What was considered and not done

- **cancelling or terminating the queued writers** — `pg_terminate_backend()` on
  anything waiting behind the lock. Rejected: it destroys a submission the platform
  may have accepted legitimately, on the operator's judgement, under incident
  conditions — and it does not remove the interval, because another writer can
  queue after the last termination and before the `COMMIT`;
- **holding the lock until after step 4's retirement** — it would extend a
  platform-wide pause across a Caddyfile edit, a `caddy validate` and two restarts,
  and the retirement still cannot reach a transaction that is already inside the
  database. The drain read obtains the same guarantee in seconds;
- **treating the queue reading as advisory** — an advisory reading of a delayed
  commit is the defect itself;
- **leaving the idle timeout disabled and relying on the operator not to walk
  away** — that is the Important finding, restated as a mitigation.

### Evidence

**The counterexample is executed twice, once against a model and once against the
database.**
`test_a_writer_queued_behind_the_settlement_lock_is_a_false_miss_without_the_drain_read`
is the eighth remediation's control, renamed and inverted: everything S-D.3 claims
still holds — the ingress reaches its commit, the door is shut, the miss is recorded
against a watermark that could not move — and the miss is false anyway, because the
queue is non-empty at the record and the drain read has moved by the time the lock
is released. `test_an_empty_queue_and_an_unmoved_drain_read_are_what_a_true_miss_rests_on`
is its control, the same episode with nothing delivered, and the two differ in one
flag.

**A real PostgreSQL concurrency test now exists**, which is what the reviewer asked
for: `tests/test_snapshot_settlement_postgresql.py`, five tests in the declared
database-backed set, against the disposable `freedom_test` database over the
Unix-domain socket. They establish, against the database rather than a model:

1. the settlement lock **blocks the real `SnapshotSubmissionService`** rather than
   refusing it, the blocked backend appears as an ungranted `RowExclusiveLock` in
   §9's own query, the decisive reading cannot move while it waits, and the
   submission commits the instant the transaction commits — the reviewer's sequence,
   executed;
2. the **drain read is granted only behind the queued writer**: with that writer
   holding its transaction open after its `INSERT`, the second `LOCK TABLE` is
   observed **ungranted** from a third session, and the watermark it reads once
   granted includes that writer's commit;
3. the **joined form of the queue reading misses the waiter entirely** when the
   waiting backend connected after the transaction's first statistics read, while
   `pg_locks` alone sees it — the correction above, found here and not by reading;
4. the control: an empty queue, a drain read granted without waiting, and figures
   identical to the decisive reading;
5. a **bounded idle timeout** releases the platform-wide pause — the waiting writer
   commits — and terminates the settlement session, so its `COMMIT` cannot succeed.

**Mutations run:** removing the queue registration from the modelled lock fails the
queued-writer test; restoring the `pg_stat_activity` join to the decisive reading
fails two of the PostgreSQL tests; deleting `pg_stat_clear_snapshot()` fails the
staleness test. Each was reverted and re-run.

`tests/test_snapshot_recovery_documentation.py` gains
`test_a_writer_queued_behind_the_lock_is_unsettled_rather_than_a_miss`, which binds
the procedure to S-D.4's heading, the defect as a sequence, why the retirement
cannot reach it, both readings and the `pg_locks`-only rule, the retraction, the
separation of recording from authorizing, step 3's Miss and Unsettled branches, and
the fifth thing settlement now rests on. Four assertions in the S-D.3 test are
updated to text this remediation rewrote, including the two the eighth remediation
got wrong, and none is removed.

### What remains open in this remediation

- **B-1 itself.** Remediated a ninth time, not closed, and this record still carries
  no independent review.
- **S-D.3 and S-D.4 have never been run as an operator procedure.** What is now
  established is the PostgreSQL behaviour they rest on, against a disposable test
  database. No `LOCK TABLE` was executed against `freedom`, the platform-wide pause
  has not been observed against the running bot, and S-D.2 remains unrehearsed.
- **The residual S-D.4 states rather than closes:** a request accepted somewhere in
  front of the destination that has not reached its first conflicting statement when
  the drain read is granted. It is not in the queue, so neither reading sees it.
  S-A, S-I, step 1's `pg_stat_activity` check and step 4's retirement are what stand
  against it, and step 4's post-recovery query is what would find it.
- **The lock's completeness still rests on the claim the watermark does** — that
  every acceptance and every post-authentication refusal on this path commits to one
  of these two tables.
- Everything the fourth to eighth remediations left open, including LXD's unread
  instance list and the privileged half of S-I.3c and S-I.3d.

## B-1, tenth remediation — the fence, and the end of settlement by observation

**This remediation withdraws the previous nine rather than adding to them.**
Everything from S-A through S-D.4 is gone from §9. Read this section before any
of the nine above it: each of those describes a mechanism that no longer exists,
and they are retained only as the record of why.

### What was still wrong

C-23's S-D.4 moved the race into the drain transaction. It did not close it. The
uncovered sequence, as the reviewer gave it:

1. the old request is accepted and pauses **before its first `INSERT`** or other
   statement conflicting with the settlement lock;
2. S-D.3 takes its lock; both queue readings are empty, the decisive watermark is
   unchanged, and the miss is recorded;
3. S-D.3 commits;
4. S-D.4 immediately takes the drain lock;
5. while the drain lock is held, the paused old request reaches its first
   conflicting `INSERT` and queues **behind the drain**;
6. the drain watermark is read before that writer can commit, so it still matches
   the decisive watermark;
7. the drain commits; the old writer commits immediately afterwards;
8. the matching drain has already authorized a fresh export with a different
   checksum. Route retirement cannot reach the old transaction, and the later
   post-recovery query merely detects the duplicate after authorization.

### The defect all nine share, stated once

Every one of the nine tried to infer quiescence from a **point-in-time
observation**: a probe's answer, Caddy's in-flight gauge, a stopped endpoint, a
terminated ingress, a restart-vector inventory, `pg_stat_activity`, a commit
watermark, a `pg_locks` queue reading, a drain read.

**An observation of a resource cannot exclude work that has been accepted but has
not yet reached that resource.** That is not a defect in any particular reading —
each was sound about what it measured — and it is why no reading can work. A
request paused before its first statement is invisible to all of them, and it
commits whenever it wakes. Each remediation moved the window; none removed it.

### The corrected rule

Settlement stops observing and **revokes**.

`submission_admissions` holds one row per submitting credential: a generation, a
state that moves `open` → `closed` once, and the operator, reason and time of each
transition. Settlement is `tools.submission_admission close`. Nothing is stopped
— not the endpoint, not Caddy, not the three Foundry sites behind it.

The invariant:

> Once settlement closes the admission generation a credential writes under, no
> request presenting that credential can create or reuse an accepted snapshot,
> return a successful receipt, or write an acceptance audit event — regardless of
> where that request was paused. A fresh export is accepted only under a newly
> authorized generation belonging to a credential the old request was never sent
> with.

Four properties carry it, and each is load-bearing:

1. **The check is inside the request's own transaction**, as the last statement
   before its commit. A request paused anywhere makes that check when it wakes.
   This is the one thing no observation could do: it asks the request rather than
   the resource.
2. **The identity it is checked against travels in the request's own bytes** — the
   principal id in its own `Authorization` header, fixed when the client sent it.
   Nothing resolves "which generation is open now", which would silently upgrade a
   request paused before that lookup and would be the same defect in a new place.
3. **A credential holds at most one admission, ever.** `principal_id` is unique
   for all time and the state transition is monotone, enforced by a trigger that
   also refuses `DELETE`, for the schema owner too. Recovery issues a **new**
   credential and opens a generation naming it.
4. **Closure and acceptance cannot interleave.** The acceptance's
   `idempotency_keys.admission_id` foreign key takes a `KEY SHARE` lock on the
   admission row; the closure takes `FOR UPDATE`, plus the exclusive side of an
   advisory lock the submission holds shared. An acceptance in flight holds the
   closure off and is then visible to the query — a hit, not a miss. An acceptance
   arriving during the closure waits, then reads `closed` and rolls back.

`idempotency_keys` is the choke point rather than `foundry_snapshots` because
every successful submission writes exactly one row there, on the new-bytes path
**and** on the duplicate-bytes path where no snapshot row is created.

### What was considered and not done

- **Another lock.** A lock delays a request; it does not revoke its authority.
  Any lock-and-read scheme recreates the same last-read-to-commit interval
  somewhere else. A lock is used *inside* this answer, to serialize a closure
  against an acceptance — but it carries state, and the state is what refuses.
- **A composite foreign key on `(admission_id, state)`.** `ON UPDATE RESTRICT`
  makes closure fail forever against historical rows; `ON UPDATE CASCADE` rewrites
  history and fences nothing.
- **A `SECURITY DEFINER` trigger taking `SELECT … FOR KEY SHARE`.** Workable and
  heavier than the foreign key already present for provenance, which takes the
  same lock for free and cannot be forgotten by a new write path.
- **An in-flight record written before processing and cleared after it** — the
  shape the previous §9 named as its Phase 3 obligation. It settles without a
  stop, and it is still an observation: a request that has not begun has written
  no in-flight record. Same defect.

### Evidence

`tests/test_submission_admission_postgresql.py`, 17 tests against a real
PostgreSQL over the Unix-domain socket, using the real `SnapshotSubmissionService`
over `SqlAlchemyUnitOfWork` and `threading.Event` rendezvous rather than sleeps:

1. **the regression the review asked for** — the old request paused **before its
   first statement**, the generation closed while it sleeps, and the refusal when
   it wakes, with no snapshot row, no receipt and no acceptance event;
2. the same at the two other boundaries — after the admission read, and at the
   final commit boundary with everything already written;
3. both lock orderings: a closure blocked by a live acceptance and then reading a
   database that contains it, and a submission blocked by a live closure and then
   refusing itself;
4. same-key retries on both sides of a closure, and a key that cannot cross into
   a new generation;
5. the recovery generation succeeding while the old credential cannot use it, and
   cannot be given a second admission;
6. a deployment with no generation at all; duplicate settlement; a closed
   generation that cannot be reopened or deleted; migration 0005's generation 0;
   audit-write failure rolling the whole acceptance back; process restart;
7. the measured PostgreSQL behaviour, including the trap that a plain `UPDATE`
   takes `FOR NO KEY UPDATE` and does **not** conflict with the foreign key's
   `KEY SHARE` — which is why `tools.submission_admission` takes `FOR UPDATE`
   first, and which reads exactly like a working fence if got wrong.

`tests/test_runtime_grants_live.py` holds the least-privilege evidence against the
real restricted role: `SELECT` on `submission_admissions` and nothing else, with
`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE` and `FOR UPDATE` each refused with
SQLSTATE 42501, while `pg_advisory_xact_lock_shared` needs no grant at all.

Four mutations were run, each reverted and re-run green; see the C-24 change-log
entry for the named failures. The first — removing the transactional admission
check, which is the C-23 design — fails the paused-before-first-statement
regression along with eight others.

### What remains open in this remediation

- **B-1 itself.** Remediated a tenth time, not closed, and this record still
  carries no independent review. Closing it is the reviewer's to do.
- **No operator has followed the new procedure end to end**, and no real Foundry
  client has met a `403 admission_closed`. The automated evidence is real
  PostgreSQL with the real submission service; the operational rehearsal is
  Rehearsal A step 10 against this version and has not been run.
- **Three maintainer decisions**, named in the C-24 change-log entry rather than
  buried in documentation wording: the fail-closed deployment state, the
  requirement to issue a new credential after every closure, and the removal of
  the downtime requirement from §9.
- **The completeness claim the watermark rested on is no longer needed**, and one
  narrower claim replaces it: that every acceptance writes exactly one
  `idempotency_keys` row in the submission scope. That is enforced by a check
  constraint requiring such a row to name an admission, and by the foreign key.
- Everything the fourth to eighth remediations left open that is not about S-A,
  S-I or S-D — those are withdrawn with the procedure that required them, and the
  unread LXD instance list and the privileged half of S-I.3c/S-I.3d are withdrawn
  with S-I.

## Records corrected

First remediation, unless a row says otherwise.

| Record | Correction |
|---|---|
| `docs/operations/foundry-snapshot-submission.md` | §9 settlement steps; §6 step 10 (late-commit disclaimer, RA-4). **Second remediation:** §9 S-B split into S-B.1/S-B.2 with the restated chain, the unsettled trigger and the S-A escape; §5.4 requires Caddy's per-server metrics. **Third remediation:** §9 step 1 rewritten to the single stopped-endpoint condition with S-A.1–S-A.4 and the withdrawn conditions named; step 3's unsettled triggers; new step 4; the "what settlement rests on" section; §5.4 drops the metrics requirement, disclaims the gauge, shows the global `{ metrics }` form and requires no upstream retry window; §6 step 10's settlement note. **Fourth remediation:** §9 step 1 widened to the whole path — the endpoint-only stop named as the third withdrawn condition, S-A reduced to S-A.1/S-A.2, **S-A.3 withdrawn and inverted**, new S-I.1–S-I.4, S-A.4 becomes S-D, "why this settles the question" and "what settlement rests on" rewritten; step 3's unsettled triggers gain the proxy's; step 4 gains route retirement, its verification and its ordering; §5.4 requires a terminable ingress, bounds what the retry window buys and points at the recovery route; §6 step 10 stops Caddy too. **Fifth remediation:** §9 S-I.3 expanded into S-I.3a–S-I.3d with commands, the `Restart=no` disclaimer, the reboot vector and the no-partial-pass/privilege rule; step 3's Unsettled trigger gains S-I.3, and its Hit, Ambiguous and Unsettled branches each point at a restoration branch; step 4 becomes "bring the path back, on the route the outcome chooses" with the outcome table and two new branches; S-D states that every episode reaches step 4. **Sixth remediation:** §9 S-I.3d rewritten as a bounded inventory with its bound stated, its sources read by contents, the LXD worked example and the topology tie; **S-D gains S-D.2**, the both-ends comparison, with the `NRestarts` caveat; step 3's Miss requires the comparison and its Unsettled trigger gains it; step 4 states which branches may assume a stopped process; the unresolved branch gains an entry read, per-state `start`/`reload` verbs, a rollback copy and `caddy validate`, and its heading changes; the miss branch gains the same copy-and-validate; the hit branch's reclassification names the running state it hands over. **Seventh remediation:** §9 S-D.2 restructured into three readings taken at both ends — the Caddy figures scoped to that unit, the listener list named as two samples, and the new **commit watermark** over `foundry_snapshots` and `audit_events` — with the counterexample that defeats the first two stated as a sequence, the withdrawn `InvocationID` claim named, the watermark's limits stated, and the journal read for the manager as well as the unit; step 3's Miss and Unsettled both name the watermark; S-I.3d's two `command -v` presence checks become per-name loops. **Eighth remediation:** §9 S-D.2's closing pass named as held rather than merely late, its "what the watermark does not establish" paragraph replaced by the interval the ordering left open, and **new S-D.3** — the `SHARE` lock over `foundry_snapshots` and `audit_events`, its privilege, its session settings, its `pg_locks` confirmation, every failure mode as Unsettled, the rejected route-retirement alternative, the platform-wide cost and the boundary with step 4; step 3's Miss states the ordering as load-bearing and its Unsettled trigger gains S-D.3's failures; step 4's miss branch records that the lock is released before it begins, and its "detection is not prevention" paragraph divides the timeline with S-D.3; "what settlement rests on" becomes four things. **Ninth remediation:** S-D.3's `idle_in_transaction_session_timeout` becomes `'10min'` with `0` named as forbidden, its block gains the `pg_locks` queue reading at both of its points with the `pg_stat_activity` join demoted to a follow-up after `pg_stat_clear_snapshot()`, and its failure list gains the idle expiry and a non-empty queue; **new S-D.4** — the queue reading's rule, why route retirement cannot reach a queued writer, the drain read, the retraction, and the separation of recording a miss from authorizing an export; step 3's Miss gains both readings and the retraction, and its Unsettled trigger gains S-D.4's failures; **step 4's "no gap" claim is withdrawn as false** and its miss branch records the drain read as a precondition; "what settlement rests on" becomes five things |
| this record | **Second remediation:** the section on S-B.1/S-B.2. **Third remediation:** the table at the top, the third-remediation section, and this table; **every S-B paragraph in the first two halves is withdrawn**. **Fourth remediation:** the table at the top, a superseding banner on the third remediation, the fourth-remediation section, and this table. **Fifth remediation:** the table at the top, the "read this first" paragraph, **the fourth remediation's one-line/mutation claim withdrawn as false** and its evidence row 8 withdrawn as an overclaim, the fifth-remediation section, and this table |
| `tests/test_snapshot_recovery_settlement.py` | **Tenth remediation:** retained and reframed as the record of every false miss a withdrawn condition permitted. **Fifth remediation:** the two `_a_request_held_by_the_proxy_` tests rebuilt on the shared `_held_request_episode` scenario; the module docstring's "differ in one line" claim corrected. **Seventh remediation:** the transient-alternate-ingress episode added with its control, `commit_watermark` and the `_SupervisedUnit` model; `_HoldingProxy` gains a late-bound upstream so a hop can hold a request for an address that does not answer yet. **Eighth remediation:** the post-closing-reading episode added with its control, plus the `_SettlementLock` and `_LockAwareUnitOfWork` models; the module docstring gains the fifth withdrawn rule. **Ninth remediation:** `_SettlementLock` gains the queue and the drain — `queued_writers()`, `writer_finished()` and `drain()` — the post-closing-reading episode gains `deliver_the_held_request` and reports the queue at the record and the drain read, its lock control is renamed and inverted into `test_a_writer_queued_behind_the_settlement_lock_is_a_false_miss_without_the_drain_read`, `test_an_empty_queue_and_an_unmoved_drain_read_are_what_a_true_miss_rests_on` is added as its control, and the module docstring gains the sixth withdrawn rule |
| `tests/test_snapshot_recovery_documentation.py` | **Tenth remediation: rewritten.** It now asserts the fence-based procedure and asserts that each withdrawn condition stays withdrawn — including that no fenced command block in the settling portion runs one. **Fifth remediation:** two tests added for S-I.3's four checks and for the three restoration branches; the step 4 anchors and the S-D assertion updated. **Sixth remediation:** two tests added for S-D.2's comparison and for the unresolved branch's entry states; the S-I.3d, restoration-branch and miss-branch assertions updated. **Seventh remediation:** two tests added — S-D.2's coverage of an ingress that is not Caddy, and the watermark's columns, entity type and action names checked against the real schema and audit policy; the S-D.2 and `command -v` assertions updated. **Eighth remediation:** one test added for S-D.3, and the two S-D.2 assertions the rewrite moved updated. **Ninth remediation:** one test added for S-D.4, and five assertions updated to the rewritten session setting, failure list, miss-branch gate and step-4 boundary |
| `tests/test_snapshot_settlement_postgresql.py` | **Tenth remediation:** retained and reframed as the record of a withdrawn condition, not a test of the live procedure. **Ninth remediation:** added. Five tests in the declared database-backed set establishing S-D.3's and S-D.4's PostgreSQL behaviour against the disposable `freedom_test` database: the lock blocks the real submission service, the blocked backend is an ungranted `RowExclusiveLock` in §9's own query, it commits on release, the drain read is granted only behind it, the `pg_stat_activity` join misses it, and a bounded idle timeout ends both the pause and the episode |
| `docs/review/phase-2-b-1-settlement-observations-2026-08-10.md` | **Fifth remediation:** the "one line of difference" note corrected, and rows 13–16 added for the S-I.3 checks read on 2026-08-11. **Sixth remediation:** rows 17–19 added for the bounded inventory, the LXD finding and S-D.2's readings; the unread list extended with LXD, the cron spool and S-D.2 itself |
| `docs/rules/foundry-export-contract.md` | §1 row and §1.0 boundary, with the reproduction and the module-comment deferral |
| `docs/review/phase-2-i-03-cl3-remediation.md` | CL3-B-1 reopened; scoped to the window correction |
| `docs/review/phase-2-supervised-rehearsal-2026-08-09.md` | step 10 no longer claims to have closed CL3-B-1 or exercised the late commit |
| `docs/project-management/change-log.md` | **Tenth remediation:** C-24 added, and C-23's closure claims struck in place. C-12 and C-13 added; C-10 given a superseding banner. **Second remediation:** C-14 added, C-13 given a superseding banner. **Third remediation:** C-15 added, C-14 given a superseding banner. **Fourth remediation:** C-18 added, C-15 given a superseding banner. **Fifth remediation:** C-19 added, C-18's mutation claim struck. **Sixth remediation:** C-20 added, C-19's S-I.3d decision struck. **Seventh remediation:** C-21 added, C-20's `InvocationID` claim struck. **Eighth remediation:** C-22 added, C-21's account of what the watermark leaves to step 4 corrected |
| `docs/project-management/status.md` | Phase 2 rows corrected. **Tenth remediation:** the B-1 row rewritten for the admission fence |
| `adapters/database/tables.py`, `migrations/versions/0005_submission_admission_fence.py` | **Tenth remediation:** added — `submission_admissions` with its monotone trigger, and `idempotency_keys.admission_id` with its `RESTRICT` foreign key and check constraint |
| `application/admissions.py`, `application/repositories.py`, `application/idempotency.py`, `application/foundry/submission.py`, `application/foundry/audit_policy.py` | **Tenth remediation:** the fence in the application — the admission types and the lock key, the repository protocol, `IdempotencyRecord.admission_id`, the check inside the acceptance transaction with the `admission_closed` refusal, and the two admission audit actions with `admission_generation` |
| `adapters/database/repositories.py`, `adapters/database/unit_of_work.py`, `adapters/database/translation.py`, `adapters/http/wsgi.py`, `infra/postgresql/runtime-grants.sql.tmpl`, `foundry-module/scripts/transport.js` | **Tenth remediation:** the read-only admission repository and its wiring, the new constraint rule names, `admission_closed` → `403`, `SELECT`-only grants with the writes explicitly revoked, and the module's refusal vocabulary |
| `tools/submission_admission.py` | **Tenth remediation:** added — `show`, `open` and `close`, with the `FOR UPDATE`-before-`UPDATE` ordering and one append-only audit row per transition |
| `tests/test_submission_admission_postgresql.py` | **Tenth remediation:** added. The paused-before-first-statement regression and sixteen more, against a real PostgreSQL with the real submission service |

## Checks

Ninth remediation, 2026-08-11:

```text
./venv/bin/python -m pytest -q                → 1899 passed, 213 skipped,
                                                 1 warning, 0 failed
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/python -m pytest -q              → 2112 passed, 0 skipped,
                                                 1 warning, 0 failed
./venv/bin/python -m pytest -q \
  tests/test_snapshot_recovery_settlement.py \
  tests/test_snapshot_recovery_documentation.py
                                              → 32 passed, 0 failed
TEST_DATABASE_URL=… ./venv/bin/python -m pytest -q \
  tests/test_snapshot_settlement_postgresql.py
                                              → 5 passed, 0 failed (run three
                                                 times for stability)
mutation: `self._queued += 1` removed from
  the modelled lock                           → 1 failed on the queued-writer
                                                 test; reverted and re-run
mutation: `JOIN pg_stat_activity` restored
  to the decisive queue reading               → 2 failed of the PostgreSQL five;
                                                 reverted and re-run
mutation: `pg_stat_clear_snapshot()` removed  → 1 failed on the staleness test;
                                                 reverted and re-run
git diff --check                              → clean
```

Seven tests more than the eighth remediation's package: five in the new
`tests/test_snapshot_settlement_postgresql.py`, one in
`tests/test_snapshot_recovery_settlement.py` (with one renamed and inverted), and
one in `tests/test_snapshot_recovery_documentation.py`, with five assertions in the
latter updated to text this remediation rewrote and none removed. No JavaScript
changed and no JavaScript check was re-run for that reason. No code under
`application/`, `adapters/`, `domain/`, `tools/` or `foundry-module/` changed: this
remediation is documentation, plus tests.

**The declared PostgreSQL-backed set was run for the first time in these
remediations**, against the disposable `freedom_test` database over the
Unix-domain socket, through the existing `tests/conftest.py` fixtures and their
two-layer disposability guard. The previous eight remediations recorded those 208
tests as skipped; all 213 now pass. **Nothing on production was contacted**: no
`LOCK TABLE` was run against `freedom`, no service was stopped, started, reloaded
or reconfigured, no configuration file was edited, and no maintainer-authorized
window was used or needed. **S-D.2, S-D.3 and S-D.4 remain unrehearsed as an
operator procedure**; what these checks establish is the database behaviour they
rest on.

Eighth remediation, 2026-08-11:

```text
./venv/bin/python -m pytest -q                → 1897 passed, 208 skipped,
                                                 1 warning, 0 failed
./venv/bin/python -m pytest -q \
  tests/test_snapshot_recovery_settlement.py \
  tests/test_snapshot_recovery_documentation.py
                                              → 30 passed, 0 failed
mutation: the guard on lock.acquire()
  replaced with False                         → 1 failed on "the commit did not
                                                 wait for the settlement lock";
                                                 reverted and re-run
git diff --check                              → clean
```

Three tests more than the seventh remediation's package: two in
`tests/test_snapshot_recovery_settlement.py` and one in
`tests/test_snapshot_recovery_documentation.py`, with two assertions in the latter
updated to text this remediation rewrote and none removed. No JavaScript changed
and no JavaScript check was re-run for that reason. No code under `application/`,
`adapters/`, `domain/`, `tools/` or `foundry-module/` changed: this remediation is
documentation, plus tests.

The 208 skips are the declared PostgreSQL-backed set, skipped without
`TEST_DATABASE_URL`. **No database was contacted, no `LOCK TABLE` was executed,
and S-D.2 and S-D.3 both remain unrehearsed.** No host command was run for this
remediation, so no new observation row is added to
[`phase-2-b-1-settlement-observations-2026-08-10.md`](phase-2-b-1-settlement-observations-2026-08-10.md);
nothing was stopped, started, reloaded or reconfigured.

Seventh remediation, 2026-08-11:

```text
./venv/bin/python -m pytest -q                → 1894 passed, 208 skipped,
                                                 1 warning, 0 failed
./venv/bin/python -m pytest -q \
  tests/test_snapshot_recovery_settlement.py \
  tests/test_snapshot_recovery_documentation.py
                                              → 27 passed, 0 failed
mutation: caddy.start() in the transient
  block                                       → 1 failed on
                                                 'invocation-2' != 'invocation-1';
                                                 reverted and re-run
```

Four tests more than the sixth remediation's package: two in
`tests/test_snapshot_recovery_settlement.py` — the first added to that file since
the fifth remediation — and two in
`tests/test_snapshot_recovery_documentation.py`. No JavaScript changed and no
JavaScript check was re-run for that reason. No code under `application/`,
`adapters/`, `domain/`, `tools/` or `foundry-module/` changed: this remediation is
documentation, plus tests.

The 208 skips are the declared PostgreSQL-backed set, skipped without
`TEST_DATABASE_URL`. **That set was not run, and no database was contacted.** The
watermark's two statements were compiled against `adapters/database/tables.py`'s
metadata for the PostgreSQL dialect to establish that the columns exist; they were
not executed against any database, and **S-D.2 as a whole remains unrehearsed.**

Fifth remediation, 2026-08-11:

```text
./venv/bin/python -m pytest -q                → 1888 passed, 208 skipped,
                                                 0 failed
./venv/bin/python -m pytest -q \
  tests/test_snapshot_recovery_settlement.py
  tests/test_snapshot_recovery_documentation.py
                                              → 21 passed, 0 failed
mutation: proxy.terminate() → pass            → 1 failed, 1 passed, as recorded
                                                 above; reverted and re-run
```

Two tests more than the fourth remediation's package, both in
`tests/test_snapshot_recovery_documentation.py`; the settlement file keeps its
seven, with two of them rebuilt onto a shared scenario rather than added to. No
JavaScript changed and no JavaScript check was re-run for that reason. No code
under `application/`, `adapters/`, `domain/`, `tools/` or `foundry-module/`
changed: this remediation is documentation, plus tests.

The read-only host checks behind rows 13–16 were run against this host on
2026-08-11 with Caddy running. **No service was stopped, started, reloaded or
reconfigured; no configuration file was edited; no maintainer-authorized window was
used or needed.** Two of the S-I.3 commands need privilege this session did not
have, and are recorded as unread rather than as passed.

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

- **finding B-1 itself**, which is remediated ten times and closed zero times.
  The reviewer holds it open, and closing it is the reviewer's to do;
- the independent re-review of these remediations, which is what the package is
  being returned for — including the fourth B-1 remediation above, which has had
  no review of any kind;
- the maintainer's ruling on change-log C-12 to C-15 and C-18 to C-24, none of
  which is ruled. **The maintainer did rule on the route** C-18 takes, between the
  two the reviewer offered, and that is not a ruling on the entry;
- ~~the Phase 3 improvement that would let recovery settle an episode without
  stopping the endpoint~~ — **delivered by the tenth remediation.** §9 no longer
  stops anything, so the question of whether a host-wide stop is acceptable for a
  running Phase 3 service does not arise;
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
