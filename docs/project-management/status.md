# Project status

Status date: 2026-08-28 (one-hundred-second update: **Phase 3 approved and
Phase 4 implementation authorized.** Peter Duscha accepted the final accountable
statement as Security Reviewer, Technical Lead, Operations Owner, Product Owner
and Acceptance Authority. A-05 is closed by his final break-glass-readiness
confirmation. A-06 and I-06 are closed by his acceptance of the PostgreSQL
queue/limiter and staging evidence. R-23 remains an **active accepted
accessibility residual**; screen-reader traversal is honestly **Not Run for
Phase 3** and is not represented as passed. On the completed P3.5 evidence and
the independent implementation and security recommendations, Peter approved the
Phase 3 authentication, authorization and web-security gate and explicitly
authorized Phase 4 implementation. Decision record:
`phase-3-gate-disposition-2026-08-25.md`; change-log C-P3.5-AK.)

Status date: 2026-08-28 (one-hundred-first update: **Foundry module 1.0.9
running-load and real active-folder compatibility are evidenced.** Peter Duscha
observed the module-owned `Submit Freedom Blades Snapshot` control in the
running Foundry worlds. A fresh 1.0.9 export from `The Guild` selected
`/actors/Characters (active)`, carried Foundry 14.367/dnd5e 5.3.3 and 32 Actors,
and produced checksum `fb14adf0a36c…`. Its stable Actor-ID set exactly matched
the prior 1.0.8 active-folder baseline. After removing only `exportedAt` and the
exporter-version field, the two documents had the same canonical content hash,
proving 1.0.9 changed neither Actor projection nor encoded content. A staging
reconciliation preview under profile 2026-08-09.1 returned 32 Actors, 32
create-candidates, zero mapped, blocked or absent, **0 errors and 0 warnings**,
exit code 0, and wrote nothing. The older active and inactive files remained
identifiable as 1.0.8 baselines and were not misrepresented as new exports.
Evidence is §5X and change-log C-P3.5-AJ. No apply was invoked. The remaining
accountable A-05, A-06, I-06, R-23 and Phase 3 gate decisions are deferred as
Peter directed; Phase 4 remains unauthorized.)

Status date: 2026-08-28 (one-hundredth update: **worker-unit parity and the
final TC-SEC-07 staging capture are complete.** Peter Duscha authorized the
deployed-artifact work and visually confirmed Foundry module 1.0.9 installed on
all three instances. The deployed worker unit matches the reviewed rendered
template; `systemd-analyze verify` returned 0, the worker remained active
without restart, and effective `MemoryMax` is 2147483648 bytes. The current
portal tree, including accepted N-29/N-31 controls, was deployed by restart and
passed its Host-aware health check. A database-enabled focused preflight passed
**458 tests**. The staging gate was removed from **20:21:43Z to 20:23:15Z**, a
92-second window. Public unauthenticated `/` and `/v1/characters` returned the
application's 303/303 boundary. Normal and 404 edge responses carried identical
CSP plus one-year HSTS; origin normal carried HSTS and no `Server`, while the
edge identified only Cloudflare. The origin early refusal returned 400 with the
required safe headers. Peter completed and acknowledged the browser check with
no reported CSP/form-action or HTMX indicator-style violation. The procedure
restored the gate and proved the public route returned 401. Evidence is §5W and
change-log C-P3.5-AI. Operational items 3 and 4 from §5R are complete at the
evidence level. Installed 1.0.9 is not yet proof that every running Foundry
process loaded it, and the real export/preview remains dependent on that proof.
A-05, A-06, I-06, R-23 and the Phase 3 gate remain open; Phase 4 remains
unauthorized.)

Status date: 2026-08-28 (ninety-ninth update: **N-32 corrected — test-only, and
the correction is now deterministic.** The two probabilistic assertions in
`tests/web/test_n7_access_log_redaction.py` no longer forbid arbitrary
three-character source fragments inside an eight-hex-character keyed pseudonym.
Each unfamiliar client value now carries an explicit table of the **complete**
representations that must not survive it — the whole client field, and the
punctuation-bearing host or credential inside it — and the tests assert the
bounded `client-unknown-` plus eight lowercase hexadecimal form, the absence of
those complete values from both the pseudonym and the fully formatted line, and
that the line is still an access line with method, path, protocol and status
intact. A mechanical brute-force check additionally offers every substring of
each source to `ipaddress.IPv4Address` and asserts every complete dotted-quad
literal absent, so a value added to the table later cannot silently skip the
address check. **Deterministic falsification.** `_digest` is monkeypatched at its
boundary to return `59990025`, reproducing the reviewer's exact pseudonym
`client-unknown-59990025` for source `203.0.113.999:54321` while parsing, prefix
selection, the filter and the formatter all run as shipped; against that value
the old fragment rule fails on `999` for both the pseudonym and the formatted
line, and the corrected assertions pass. **Mutation.** Three mutations —
returning the raw client field, the raw host address, and the raw host address
wearing the pseudonym's prefix — each fail the corrected *confidentiality*
assertion, not merely the form check, so a real disclosure is still caught. Why
the correction is deterministic where the old rule was not is itself asserted:
every forbidden value carries a character outside the pseudonym's own alphabet,
whereas the old rule forbade fragments drawn from `[0-9]` alone, every one of
which is inside it. A one-off measurement over **20,000 random keys x 7 cases**
put the old rule's failure rate at **199 of 140,000 case-runs (0.142%)** and the
corrected rule's at **0**. **Verification.** The focused access-log and
scope-guard pair passed **480** in each of three separate fresh Python
processes; serial database-enabled suites are bot **2447 passed**, web **2824
passed, 80 skipped**, module **171 pass**; assets 4/4 and visual freeze 14/14;
both `compileall` checks clean; Alembic single head `0013` with no branches;
`git diff --check` clean. Formatter, linter and type checker remain unconfigured
and are not claimed. **Exactly one file changed:**
`tests/web/test_n7_access_log_redaction.py`. No production pseudonymization,
access-log policy, route, configuration or deployment artifact was touched, no
production injection seam was added, and no service was deployed or restarted.
N-31 remains satisfactory and is not reopened; N-29 and N-30 are not reopened.
Recorded as change-log **C-P3.5-AH** and evidence §5V. EX-11 and EX-12 are
requested again; the four outstanding supervised operational items remain
outstanding and unexecuted. Peter alone decides the Phase 3 gate; Phase 4 remains
unauthorized.)

Status date: 2026-08-28 (ninety-eighth update: **N-31's production remediation
is satisfactory; Important N-32 is a probabilistic test-evidence defect, not a
new disclosure.** Independent review reproduced the full configured suites
green — **2447 / 2797+80 / 171** — and then reran the exact focused access-log
and scope-guard pair in a fresh process. That run failed **2 of 453** because the
new process-local keyed digest happened to be `client-unknown-59990025` for
synthetic client `203.0.113.999:54321`. Two older assertions prohibit every
three-character source fragment, including `999`, from appearing anywhere in
the eight hexadecimal digest. A random digest can contain `999` by coincidence;
that is not the source fragment surviving, and the output contains no dotted IP
literal or original client field. The assertions therefore confuse coincidental
substring equality with disclosure and make the security evidence depend on the
random process key. This is **N-32, Important**. Replace only those probabilistic
fragment assertions with deterministic properties: bounded pseudonym form,
absence of the complete client value and complete plaintext IP literal, and
fully formatted output safety. Do not change production pseudonymization or the
accepted N-31 method policy to satisfy a defective test. Reproduce the failure
deterministically with an injected or monkeypatched digest whose hex contains
`999`, then prove the corrected assertions pass that case and still fail if the
raw client or address is returned. N-31 is recommended resolved at the
repository implementation boundary; EX-11 and EX-12 remain withheld for N-32's
evidence correction and the four outstanding supervised operational items. No
file was changed during review and no service was touched. Recorded as
change-log **C-P3.5-AG** and evidence §5U. Peter alone decides the Phase 3 gate;
Phase 4 remains unauthorized.)

Status date: 2026-08-28 (ninety-seventh update: **N-31 remediated in the
repository; both re-reviews requested again.** The retained pinned Uvicorn branch
examined the method's *syntax* and nothing else, so a caller could send
`203.0.113.7` as an HTTP method — a valid RFC 9110 token, because the token
alphabet includes digits and `.` — and have it formatted into the access log in
clear text. **Syntactic validity is not confidentiality.** A pinned record whose
method carries an IP literal is now **withheld whole**, under a seventh
repository-owned reason, `address-bearing-method`; the five reproductions that
disclosed an address now emit the marker and nothing else. Scrubbing the method
was the other option the handoff allowed and was rejected: it leaves
`X<pseudonym>Y`, caller-chosen characters around a removed span in a field with
no operational meaning left once it carries an address — the request path is
scrubbed instead of withheld because a path with an address removed is still a
route an operator can read. **The method rule is not a second rule.** Detection
asks whether `_scrub_addresses` — the rule N-29's re-review accepted for the
request path — would change the method, so the detector cannot drift from the
scrubber. Its completeness over the accepted input rests on two checked facts:
the method alphabet contains **no `:`**, and every textual IPv6 literal contains
at least two, so no IPv6 literal is expressible in a method at all; and the
remaining IPv4 dotted quad is enumerated by start position and length within the
32-character bound rather than scanned once. 2,000 seeded pseudo-random
token-valid methods are checked against an independent brute force **in both
directions**, so over-refusal fails as loudly as disclosure. `_HTTP_METHOD` is
unchanged and no extension method was sacrificed: `VERSION-CONTROL`, `M-SEARCH`,
`MKCALENDAR`, `PROPFIND`, `QUERY`, `REPORT.V2`, `DEAD.BEEF`, `1.2.3`,
`203.0.113` and `999.999.999.999` all still reach the log. **The boundary is
stated rather than widened:** the rule finds IP *literals*, so an address spelled
in another encoding is not detected — the same boundary the accepted
request-path rule has. **Falsified before it was trusted:** the regression was
written first and fails **68** against the reviewed tree with **no pre-existing
test failing**, which is what shows it isolates N-31; reinstating each element
afterwards fails **67**, **2** and **46**, the last proving the tests pin the
*choice* between the handoff's two options rather than merely the absence of the
address. The scope guard was falsified against this very edit — with
`tools/portal_server.py` undeclared it names the file — so N-30's remediation is
shown to be watching this change, not merely present; no new production file was
opened, and the declaration comment now names N-31 as a distinct change.
Verification serial and database-enabled: **2447 / 2797+80 / 171**, focused
**453**, assets 4/4, freeze 14/14, `compileall` clean in both venvs, single
alembic head `0013`, clean `git diff --check`. Formatter, linter and type checker
remain unconfigured and are not claimed. **Nothing was deployed** — the corrected
portal entry point is not on the running service, which still carries both the
N-29 and the N-31 behaviour — and the four operational items (loaded module 1.0.9
and the real export/preview, the stale worker-unit header comment, the post-gate
`Server` header and TC-SEC-07) are **not run**, each awaiting Peter's
authorization and, for three, a supervised window. Recorded as change-log
**C-P3.5-AF**; evidence in `phase-3-p3-5-staging-and-operations-evidence.md`
§5T. No finding closes on green tests. EX-11 and EX-12 remain withheld; Peter
alone decides the Phase 3 gate; Phase 4 remains unauthorized.)

Status date: 2026-08-28 (ninety-sixth update: **EX-11/EX-12 remediation
re-review found Blocking N-31; both recommendations remain withheld.** The
unfamiliar-record half of N-29 now fails closed as designed, and N-30's
production-scope guard is accepted as satisfactory. The retained pinned Uvicorn
path is still not closed over every caller-controlled field, however: HTTP
methods are RFC tokens, the accepted token syntax permits dots and digits, and
the filter preserves the method unchanged. A synthetic pinned record with method
`203.0.113.7` therefore formats as
`client-… - "203.0.113.7 /healthz HTTP/1.1" 200`, disclosing a plaintext address
contrary to operational contract §5's every-log-line prohibition. This is
**N-31, Blocking**. The remediation must scrub or refuse address-bearing method
values without weakening query removal, client pseudonym correlation,
whole-record withholding, bounded-field validation or filter idempotency, and
must add a fully formatted pinned-record regression that is first falsified
against the current tree. Independent verification of the current tree was
serial and database-enabled: **2447 / 2625+80 / 171**; focused remediation tests
**289 passed**; assets and visual freeze clean; both `compileall` checks clean;
single Alembic head `0013`; `git diff --check` clean. Formatter, linter and type
checker remain unconfigured and are not claimed. No file was changed during the
review and no service was touched. The four outstanding supervised operational
items remain not run. Recorded as change-log **C-P3.5-AE** and evidence §5S.
Peter alone decides the Phase 3 gate; Phase 4 remains unauthorized.)

Status date: 2026-08-28 (ninety-fifth update: **N-29 and N-30 remediated in the
repository; both re-reviews requested.** N-29's fallback no longer redacts text
at all — an access-log record outside the pinned uvicorn 0.32.1 contract is now
**withheld whole**, replaced by a marker naming one of six repository-owned
reasons, with `args`, `exc_info`, `exc_text` and `stack_info` cleared. The
correction is a narrower contract rather than a better pattern, because the
defect was the instrument: no rule over arbitrary rendered objects can be shown
complete, and this was the third pattern in that file's history to be found
incomplete. The retained pinned path now **bounds every field it keeps**, and a
second instance of the same finding was closed on it — the request path is
caller-controlled, so `GET /x203.0.113.7y` disclosed an address through the
branch the handoff keeps; it is scrubbed by a rule closed over its input.
**Found while correcting, not by the review.** N-30's guard watches `tools/`,
declares the two entry points genuinely changed, and became a **pure function of
a path**, so an undeclared synthetic path is rejected without reading the working
tree — the demonstration N-27 and N-30 both lacked. Every production layer is now
watched rather than one added per finding; the widening to `infra/` and
`foundry-module/` goes beyond the handoff and is **raised for the reviewer, not
absorbed**. Both corrections were **falsified before they were trusted**: the new
N-29 tests fail 68 against the submitted build, and reinstating each element of
the fix afterwards fails 3, 52, 5, 19 and 8; the guard is falsified four ways
including an undeclared synthetic change written into a real `tools/` file.
Verification serial and database-enabled: **2447 / 2625+80 / 171**, assets 4/4,
freeze 14/14, `compileall` clean in both venvs, single alembic head `0013`, clean
`git diff --check`. Formatter, linter and type checker remain unconfigured and
are not claimed. **Nothing was deployed** — the corrected portal entry point is
not on the running service — and the four operational items (loaded module 1.0.9
and the real export/preview, the stale worker-unit header comment, the post-gate
`Server` header and TC-SEC-07) are **not run**, each awaiting Peter's
authorization and, for three, a supervised window. Recorded as change-log
**C-P3.5-AD**; evidence in `phase-3-p3-5-staging-and-operations-evidence.md`
§§5Q–5R. No finding closes on green tests. EX-11 and EX-12 remain withheld; Peter
alone decides the Phase 3 gate; Phase 4 remains unauthorized.)

Status date: 2026-08-28 (ninety-fourth update: **EX-11 and EX-12 re-review
completed; both recommendations withheld.** Codex independently reproduced
Blocking finding **N-29**: the unfamiliar-record access-log fallback emits a
plaintext IPv4 address when it is embedded next to word characters, conflicting
with operational contract §5's prohibition in every log line. Important finding
**N-30**: the P3.4 scope guard watches `adapters/`, `application/` and `domain/`
but not `tools/`, so the behavioral change to the production portal entry point
passed undeclared—the same class as N-27. The real Foundry export/preview against
loaded module 1.0.9 also remains outstanding. Full verification was independently
reproduced: **2447 / 2452+80 / 171**, assets 4/4, visual freeze 14/14 and clean
`git diff --check`. Remediation instructions are in the overwritten reviewer
handoff. Phase 4 remains unauthorized.)

Status date: 2026-08-27 (ninety-third update: **EX-11 implementation tasks
completed and the three undeployed remediations deployed.** The client-pseudonym
defect is confirmed and corrected — uvicorn 0.32.1 builds its client field as
`address:ephemeral-port`, so the digest was taken over a value that changed every
connection and the documented correlation property never held; the address is now
extracted and validated before hashing, and an unreadable value fails safe under
a distinct, explicitly uncorrelatable prefix. The new tests found and closed a
second, pre-existing gap: an IPv6 address *with* a port survived the traceback
scrubber in plaintext where the IPv4 form did not. Stale worker documentation and
the stale exact-comparison claim corrected in code, in the module and in the
threat model's RR-05. **Deployed 2026-08-27:** HSTS (22:06 UTC, captured at both
the Cloudflare edge and the Caddy origin), Foundry module **1.0.9** to
**foundry1, foundry2 and foundry3** — foundry2 on Peter's explicit instruction,
where the module had never been installed at all — and `MemoryMax=2G` (22:43 UTC,
confirmed at the unit, at systemd and in the kernel cgroup). Verification set
re-run green: **2447 / 2452+80 / 171**. **Deployment task 4 — the real
export/preview compatibility check — is not done** and is blocked until an
instance loads 1.0.9. The `includeSubDomains` rationale in both Caddy files, the
test that enforces it and operational contract §4.1 was **factually wrong** and
is corrected — the directive binds names beneath the sending host, not siblings,
so the Foundry hosts were never at risk from it; the omission stands on a reason
that holds. RR-06 amended alongside RR-05: both measured, **neither closed
here**. Recorded as change-log **C-P3.5-AB**. EX-11 and EX-12 recommendations
remain withheld; Phase 4 remains unauthorized.)

Status date before this update: 2026-08-27 (ninety-second update: **EX-11/EX-12 review response and
baseline v1.6 authorization**. Peter Duscha explicitly authorized superseding
OD-14's exact deployed tuple with scoped compatibility: exact world/system
identities, numeric Foundry `14.x`, numeric dnd5e `5.3.x`, and fail-closed
handling outside those ranges. Current governance, ADR, discovery, export
contract and operations documents now agree. EX-11 and EX-12 recommendations
remain withheld pending implementation of the client-pseudonym normalization,
stale worker-documentation correction, deployment of module 1.0.9,
`MemoryMax=2G` and HSTS, operational capture, and re-review. Phase 4 remains
unauthorized.)

Status date: 2026-08-27 (ninety-first update: **EX-10 written** — the P3.5
submission, `docs/review/phase-3-p3-5-submission.md`, requesting the Phase 3 gate
decision and, before it, EX-11 and EX-12. Full verification set re-run green
against the submitted tree: **2447 / 2423+80 / 171**. One further finding while
writing it, **N-28**: C-P3.5-Z's N-47 raise reached the register and the systemd
unit but not the harness that measures against N-47, and the test meant to catch
that pinned the constant to a literal. Fixed and falsified as C-P3.5-AA. The
pattern named in the ninetieth update now has a fifth instance — and this one was
found *after* the pattern was written down. The submission's finding index was
also rebuilt: **23 findings, N-6 … N-28**, where a first draft indexed 15 — and
**N-15 stands as a deviation**, only its severity having been withdrawn.)

Status date before this update: 2026-08-27 (ninetieth update: the real-folder run closed RR-06 and
D-m's n=1. Three numeric-policy decisions implemented — version ranges, N-47 to
2 GiB, N-45's soft warning raised and *built*. Four findings, and a pattern
worth naming: four controls described somewhere and implemented nowhere.)

Status date before this update: 2026-08-26 (eighty-ninth update: documentation brought current across
every register and evidence artifact; full verification set re-run green.)

Status date before this update: 2026-08-26 (eighty-eighth update: the synthetic performance and
recovery run. Worker peak memory measured for the first time — 17.9% of N-47 at
realistic size, 47.1% at the N-20 ceiling. SP-15 synthetic halves, SP-16 and SP-17
all pass. D-m's real n=1 apply still owed.)

Status date before this update: 2026-08-26 (eighty-seventh update: S-12 passed at the seventh attempt.
The SP-29 gate-off window ran 36 bounded minutes and the browser evidence found two
things automated tests could not — HSTS missing against the accepted contract, and
a live CSP violation from HTMX.)

Status date before this update: 2026-08-26 (eighty-sixth update: SP-10 re-run on staging — the N-20
fix verified where the defect was reachable. Same drill, same database: services
now start clean instead of crash-looping. S-12 recorded Not Run after six
attempts, every failure the observer's.)

Status date before this update: 2026-08-26 (eighty-fifth update: SP-27 executed. A-05 criterion 4b is
Met — S-15's production refusal observed before exposure, with no listener, inside
a verified network namespace. A-05 is down to criterion 10 alone.)

Status date before this update: 2026-08-26 (eighty-fourth update: A-05 criterion 4a met. And this
package's own procedure caused an operator-visible outage — N-21 — by reusing a
uid-scoped firewall rule under an account that runs far more than the thing under
test. SP-27 not executed; criterion 4b still Open.)

Status date before this update: 2026-08-26 (eighty-third update: N-20 remediated as options 2+3 —
the drill now re-applies the runtime grants and fails when a privilege present
before is missing after. The first version of the fix was itself wrong and was
caught by an unrelated test failing.)

Status date before this update: 2026-08-26 (eighty-second update: M-4 executed. SP-10 passed as a
procedure and found N-20 — the documented restore silently drops the runtime
role's privileges, and both units crash-looped until the grants were re-applied.
S-14 observed on the deployed unit; S-12 remains Not Run after three setup errors.)

Status date before this update: 2026-08-26 (eighty-first update: M-3 executed. SP-13 / TC-LIM-02
passes with exact parity; SP-08 stands at 11 of 15 refusals, one of them proved on
the deployed unit. Two run-sheet defects found by executing it, one of which would
have recorded a refusal as a non-refusal.)

Status date before this update: 2026-08-26 (eightieth update: M-2 executed. SP-09 / TC-OPS-01 passes,
including the half that matters — the bot and Foundry stayed up while the web
perimeter was closed. Two run-sheet instructions were wrong and are corrected; the
portal was not.)

Status date before this update: 2026-08-26 (seventy-ninth update: M-1 executed. SP-02 and SP-03 pass;
the Discord snowflakes corroborate the separation attestation independently. One
minor deviation recorded: the environment files are 0640 where the procedure
specifies 0600.)

Status date before this update: 2026-08-26 (seventy-eighth update: the gate-off window is approved as
decision D-r and written up as procedure SP-29, bounded by two recorded
timestamps. The kill-switch sitting is resequenced before it, so the emergency
stop is proved before the outer protection comes off.)

Status date before this update: 2026-08-26 (seventy-seventh update: the logout 415s are explained —
the proxy gate, not the application — and chasing them found N-14: the same gate
would have invalidated TC-SEC-07's evidence run, which the deployed site file
already said it would.)

Status date before this update: 2026-08-26 (seventy-sixth update: the N-13 fix is deployed and
TC-OPS-05 **passes** — the first of the nine outstanding rows to close. A separate
open question is raised: the deployed portal answered POST /v1/auth/logout with
415 twice, which the shipped sign-out control cannot produce.)

Status date before this update: 2026-08-26 (seventy-fifth update: the N-7 fix is deployed and
verified on the running portal — the credential class is clean. SP-12's re-run
found a second prohibited class: the access log records the client IP address in
plaintext, which operational contract §5 forbids. TC-OPS-05 stays Failed.
Remediated in the repository; not deployed.)

Status date before this update: 2026-08-26 (seventy-fourth update: Peter Duscha answered all eight
authority questions. SG-2 and an SG-3 extension are granted, D-o is confirmed,
and the two defects found yesterday are decided as D-p and D-q. D-q is applied.
No procedure has run; no RAID disposition moves.)

Status date before this update: 2026-08-26 (seventy-third update: the SG-1-released preparation
C-5…C-12 is complete — three harnesses, 38 new tests, the run sheets and the C-8
proposal. It found two defects: A-05 criterion 4a is not executable as written,
and SP-10 has no instrument. Full suites green. Nothing executed, nothing closed.)

Status date before this update: 2026-08-26 (seventy-second update: the single P3.5 authority request
is issued to Peter Duscha, covering D-o confirmation, SG-2, an SG-3 extension for
the two remaining credential procedures, the N-7 deployment and SP-12 re-run, and
SP-27. Nothing is executed and no disposition moves.)

Status date before this update: 2026-08-26 (seventy-first update: Codex re-reviewed the interim
remediation and reproduced a credential leak through the N-7 fallback. Corrected:
the fallback no longer inspects argument structure at all. Tests 27 → 59. No gate
status changes; TC-OPS-05 remains Failed.)

Status date before this update: 2026-08-26 (seventieth update: the Codex interim review returned one
Blocking and two Important findings; all three are remediated. The A-05 criterion-4
amendment is corrected — S-15 pre-exposure evidence returns to A-05 — and the N-7
redaction now fails closed on any unrecognised record shape. **That last claim was
false when written**; Codex reproduced a leak through it and it is corrected in the
seventy-first update.)

Status date before this update: 2026-08-26 (sixty-ninth update: an interim Codex review is requested
over the three decisions, the A-05 criterion-4 amendment, the N-7 security finding
and its fix, and the four new artifacts. It is not either mandatory gate pass.)

Status date before this update: 2026-08-26 (sixty-eighth update: the N-7 access-log fix is implemented
and proved against a real uvicorn, and all four missing P3.5 artifacts now exist.
Traceability resolves 294 of 318 contract rows to real tests; the 5 unresolved are
citation gaps, not coverage gaps.)

Status date before this update: 2026-08-26 (sixty-seventh update: SP-12 ran and TC-OPS-05 failed on a
real credential disclosure in the access log. Remediated in the repository the
same night, with the leak reproduced before it was fixed; not yet deployed, so
the row stays Failed until re-observed.)

Status date before this update: 2026-08-26 (sixty-sixth update: the EX-3 migration-rollback and EX-4
backup/restore rehearsals are executed against the disposable database, with the
0013 boundary observed refusing and failing closed. A stale-bytecode defect left
by the filesystem cutover was found and corrected. Full verification set green.)

Status date before this update: 2026-08-25 (sixty-fifth update: A-05 criterion 4 is split into 4a
(retained, executable) and 4b (moved to the deployment gate). All three P3.5
decisions are formally recorded, with reversal procedures, as change-log
C-P3.5-T. SG-2 remains ungranted.)

Status date before this update: 2026-08-25 (sixty-fourth update: the Data Owner approved real Foundry
data in staging and the Acceptance Authority chose the TC-PERF-02 repeat-run
method. Four procedures are unblocked. SG-2 is now the only thing gating
execution of the remaining I-06 procedures.)

Status date before this update: 2026-08-25 (sixty-third update: the P3.5 evidence inventory and
session run sheet are complete. Nine of thirteen staging-only rows remain Not
Run, A-05 stands at eight of ten criteria, and four of the five required P3.5
artifacts do not yet exist. Two Data Owner / Acceptance Authority decisions block
roughly two hours of the remaining supervised work.)

Update 2026-08-27 (ninetieth) — the real folder, three policy decisions, and a
pattern.

- **RR-06 closed.** The real-folder apply the threat model has recorded as never
  measured since Phase 2 now has a number: preview **9,854 ms (602 ms/MB)**,
  apply **19,927 ms**, peak **302.4 MiB**, one attempt, one durable effect.
  **D-m's n = 1 is discharged.**
- **The version bump validated on real data.** 602 ms/MB against Rehearsal B's
  587 — within **2.5%** across 18 days and a Foundry version change, with the
  same Actor count and no warnings. C-P3.5-X's named residual, a schema-valid
  semantic change, is answered by measurement rather than argument.
- **A second real sample** (the inactive folder, 34 Actors, 282 KB/Actor against
  the active folder's 512 KB) put throughput within 8% and the memory ratio in a
  stable **13–15×** band — **roughly double the synthetic fixture's 7.5×**
  (**N-26**).
- **`absent_from_snapshot` observed on real data:** 32 warnings, and applying
  touched none of the 32 characters. A reconciliation reading "absent from this
  folder" as "delete" would have destroyed live characters the moment somebody
  imported a different folder — which is what we did, by accident of sequencing.
- **Three numeric-policy decisions, all taken after the measurements**
  (C-P3.5-Z): version comparison widened to scoped ranges (Foundry generation,
  system major.minor, identities exact, fail-closed parsing); **N-47 1G → 2G**
  on a host that turned out to be 7.7 GB rather than the assumed 4; **N-45's
  soft warning 30 → 60 s and implemented** — it had never existed outside the
  register.
- **N-27 raised and closed.** The P3.4 scope guard watched `adapters/` and
  `application/` but **not `domain/`** — so the version comparison, the substance
  of the day's change, passed it unnoticed. `domain/` is now watched, the change
  is declared with its reason, and the guard was **falsified** before being
  trusted.
- **The pattern worth a reviewer's attention:** four controls in this package
  were described somewhere and implemented nowhere — **N-22** (HSTS in the
  contract, in neither Caddy file), **N-45** (a register soft warning nothing
  emitted), **F6** (S-15's warning read by nothing) and **N-27** (a guard blind
  to a layer). **Each was found by looking; none by a check designed to find
  them.**
- **Two of my own tests were wrong and both were caught**: one reimplemented the
  latch it claimed to test and would have passed with the real latch deleted;
  another matched a bare word and went red on `base.html`'s own comment.
- **Verification:** bot **2446 passed**, web **2423 passed / 80 skipped**, module
  **171 pass**, assets 4/4, freeze 14/14, `git diff --check` clean.
- **Deployment owed:** module **1.0.9** to the Foundry hosts, **`MemoryMax=2G`**
  to the worker unit, and the **HSTS** Caddy change. All three are
  repository-only.
- **Position:** **A-05 Open on criterion 10 alone.** I-06 and A-06 Open but
  substantially evidenced. R-23 an active accepted residual. **EX-11 and EX-12
  owed. Phase 4 has not begun and remains unauthorized.**

Update 2026-08-26 (eighty-ninth) — documentation brought current; verification green.

- **Every register and evidence artifact now reflects the day's execution:**
  change-log **C-P3.5-W** records decisions **D-r** (the bounded gate-off window)
  and **D-s** (the two performance latency bounds); the execution plan's §0.2
  checkpoint table carries both; the accessibility evidence carries the second
  browser session, the exact Chrome build, the skip-link pass, the reduced-motion
  verification and finding **N-23**; the RAID register carries a close-of-day
  position for I-06, A-06, A-05 and R-23.
- **The 2026-08-25 evidence inventory is left as written** and now opens with a
  superseded-by-execution note, so a reader is not misled by its `Not Run` tables.
  The authoritative record is the staging/operations evidence §§5A–5J.
- **Verification set re-run serially:** bot **2424 passed**, web **2415 passed /
  80 skipped**, asset integrity **4/4**, visual freeze **14/14**, `compileall`
  clean in both environments, `git diff --check` clean, single Alembic head
  `0013`. Formatter, linter and type checker remain **not configured**.
- **The visual freeze still verifies**, which matters because N-23 proposes a
  `base.html` change and nothing has been applied to the frozen assets.
- **Position unchanged by this update:** **A-05 Open on criterion 10 alone**;
  **I-06 and A-06 Open** with most of A-06's evidence now in hand; **R-23** an
  active accepted residual. **EX-11 and EX-12 are owed. Phase 4 has not begun and
  remains unauthorized.**

Update 2026-08-26 (eighty-eighth) — the quantity that had never been measured,
measured.

- **TC-PERF-01: worker peak resident memory.** **184.5 MiB (17.9% of N-47)** at
  the realistic 16.3 MB corpus; **482.3 MiB (47.1%)** at the 66.7 MB N-20 ceiling.
  Both inside the 1 GiB guard, the ceiling case with better than 2× headroom.
  Peak scales at roughly **7× input size** — the ratio worth extrapolating from.
- **The Operations Owner's framing, adopted:** the real folder holds **32**
  Actors, so the 131-Actor run answers *"where is the wall?"* rather than
  predicting load. It would need to roughly quadruple before memory mattered.
- **TC-PERF-02:** applies of **6.2 s** and **27.0 s**, at 384 and 405 ms/MB across
  a 4× size difference — **D-m's repeatability pair**, scaling linearly. The
  second exercised updates against records a previous import created, not only
  creates. Durable effects matched the preview exactly.
- **One figure explicitly disqualified:** the 66.7 MB preview's 1179 ms/MB sits
  just under the bound but is **not a throughput measurement** — it is the run
  deliberately SIGKILLed, and most of its 79 s is lease-expiry wait. A clean
  preview at the bound is still owed.
- **TC-PERF-03 passes** against bounds accepted beforehand (**D-s**): 984 samples,
  **zero non-200**, every p95 ≤ 51 ms — including through a worker being killed
  and restarted. **One 1,561 ms maximum recorded as a signal**, 30× the previous
  max, during a 27-second transaction: portal and worker contending on the
  database. Within bound, and the number that moves first under a larger apply.
- **SP-17 passes.** SIGKILL mid-parse, `attempts` 1→2, systemd restart, 60 s lease
  expiry, reaper requeue, retry completed — **exactly one outcome and no partial
  state**, with the portal unaffected throughout.
- **Four refusals observed that were not planned for**, each firing before the
  next stage could run: idempotency key (1 ms, before the body), size (0.96 ms,
  *"It was not read"*), admission, and the duplicate-content fence. Nothing was
  stored by any of them.
- **N-24 (minor):** the lost-pin runbook tells the operator to run the
  acceptance-event query after closing an admission — but that query joins
  `foundry_snapshots`, which teardown had already truncated. Harmless here; in a
  real recovery it would destroy the query's ability to resolve an acceptance.
  **The query must run before teardown**, and both the runbook and this package's
  teardown order should say so.
- **An accessibility observation from the operator, unprompted:** the
  reconciliation page's text is too large and overflows at his window width.
  Recorded for R-23 — feedback from the person who will operate the screen.
- **Still owed: D-m's real 32-Actor apply, reported as n = 1.** Synthetic Actors
  parse about **3× faster** than real ones (587 ms/MB in Rehearsal B against
  192 ms/MB tonight, near-identical byte counts), so tonight's timings are
  optimistic and are cited as synthetic throughout.
- **Everything torn down**: import tables truncated, artifacts and fixtures
  shredded, admission closed, endpoint stopped, audit history retained.
- **A-06 now has most of its evidence. I-06 advances. A-05 remains Open on
  criterion 10. Phase 4 remains unauthorized.**

Update 2026-08-26 (eighty-seventh) — S-12 closes; the browser window earns its keep.

- **S-12 Passed at the seventh attempt.** The worker's entry point, run **as
  `freedomweb`** with the deployed environment files and a permissive artifact
  root, refused with `ArtifactStorageError: root_not_owned` — the correct branch
  for that account, the mode branch having already been observed from the owner's.
  **Both branches of `_require_trusted_root` are now evidenced**, each from the
  account that makes it fire. **SP-08 stands at 14 of 15**; TC-OPS-04's only
  remaining gap is **S-13**, which is test-enforced and not observable on a live
  host.
- **The six earlier failures diagnosed cleanly, and none was the portal's.**
  Attempt 6 confirmed the value in `/proc/<pid>/environ` but read `is-active`;
  attempt 7 read `NRestarts` but never re-confirmed the value had landed.
  **Neither held both confirmations at once** — which is how a working refusal was
  mistaken first for a setup error and then for an anomaly.
- **SP-29 executed: window open `21:24:46Z`, closed `22:01:01Z` — 36 minutes**,
  bounded at both ends by an observation. Gate removed, `caddy validate` valid,
  public routes `303` with no `401`; gate restored, valid, `401` back. The kill
  switch was confirmed available first, which is why M-2 was resequenced ahead.
- **SP-14 Passed in part.** The N-26 CSP is **byte-identical on normal and error
  responses**; the early refusal (`400 Unknown host.`) carries the same CSP,
  `nosniff` and `no-store`, observed **at the origin** because the public path
  returns Cloudflare's `530` and never reaches our boundary. **TC-SEC-07's
  specific assertion is evidenced:** a Discord login completed in Chrome
  **151.0.7922.172** with no `form-action` violation.
- **N-22 — Important.** The accepted contract gives Caddy **exactly two jobs, TLS
  and HSTS**, and **HSTS is configured in neither the deployed staging file nor
  the production template**. Observed on the wire: no `strict-transport-security`
  on any response. Without it, a first-time visitor typing `http://` can be
  intercepted before the redirect — the attack HSTS exists to prevent, which the
  contract already decided to prevent. **Not remediated:** it touches the proxy
  and the production template, and the `includeSubDomains` question is expressly
  the Operations Owner's.
- **N-23 — Minor.** HTMX 2.0.10 injects an inline `<style>` for `.htmx-indicator`
  and `style-src 'self'` blocks it, on every HTMX page load. **No functional
  impact** — no template uses `hx-indicator` — but a violation on every load is
  noise that would **mask a genuine one**. One-line fix proposed, not applied.
- **Both findings came from running a real engine.** Parsed-DOM automation cannot
  execute HTMX under an enforcing CSP, and cannot see a header that is absent.
- **plan-SP-23 partly evidenced:** skip link **Passed** (markup verified,
  activation observed); `prefers-reduced-motion` **mechanism verified** and its
  imperceptibility explained — the only motion in the stylesheet is 10 short hover
  transitions. HTMX-enhanced path and real-engine contrast remain **Not Run**.
- **TC-UI-08 partly evidenced:** iPhone 15 / iOS 26.6, every view, zoom exercised,
  no defect — **but 768 and 1280 are not covered**, because a phone offers only its
  own width. An iPad would cover both bands on real hardware and is queued.
- **I-06 and A-06 remain Open; A-05 remains Open on criterion 10. Phase 4 remains
  unauthorized.**

Update 2026-08-26 (eighty-sixth) — N-20's fix verified on staging; S-12 recorded
honestly.

- **The re-run was owed because `freedom_test` could not prove it.** Only the
  owner connects there, so nothing depends on a second role's privileges and the
  original defect was never reachable. `freedom_staging` is the one target with a
  restricted runtime role.
- **The result is the contrast.** Same drill, same database, same data — differing
  only in the remediation:

  | | M-4 | This run |
  |---|---|---|
  | `freedomweb` privilege rows after restore | **0** | **99** |
  | Services | crash-looped to `NRestarts` **35 / 36** | **`NRestarts=0`, running** |
  | Manual intervention | grants re-applied by hand | **none** |

- **The restored posture is the restricted one, not a widened one:**
  `INSERT,SELECT,UPDATE` on `sessions` and **`TRUNCATE` still denied**. Data,
  31 tables, 6/6 guard functions and the append-only refusal all unchanged.
- **The runtime role was detected rather than configured**, so no per-database
  mapping exists to fall out of step.
- **Teardown:** all seven artefacts shredded; they held real credential public
  keys and identity, none of which is quoted in the evidence.
- **S-12: Not Run after six attempts, and recorded as such** — not as passed, and
  not as the finding attempt 6 briefly resembled. Every failure was the observer's:
  a non-existent path (which `ensure_ready` legitimately creates), five `sed`s
  against a file where the variable has never existed, and finally reading
  `is-active` instead of `NRestarts` — **the exact error recorded as N-18 earlier
  the same day by the same author.** The code path demonstrably refuses that root,
  in two independent reproductions, so S-12 is probably firing and was
  mis-observed. **SP-08 stands at 13 of 15; TC-OPS-04 is not complete.**
- **I-06 and A-06 remain Open. A-05 remains Open on criterion 10 alone. Phase 4
  remains unauthorized.**

Update 2026-08-26 (eighty-fifth) — SP-27 executed; A-05 criterion 4b closes.

- **The evidence D-o exists for is now an observation rather than an argument.**
  Codex finding B-1 established that a production-*marked* process is not a
  publicly *exposed* one. Under the production marker, with **no listener, no
  bind and no route**, `run_resource_checks` **refused**, naming **S-15** and the
  N-13 credential floor.
- **And it passed at two credentials** — the falsification, and the reason the
  refusal means something. Had it refused at both counts, the refusal would have
  been about production-marking and would have evidenced nothing about N-13.
- **The corrected isolation was verified inside the namespace that ran the
  exercise**, not merely beforehand: `egress: 000` and a working Unix socket.
  Blast radius one process, and **no firewall rule existed to leave behind** —
  which is the whole point of the N-21 correction.
- **The guard was fired deliberately before anything was seeded:** the harness
  refused the production target outright without `--acknowledge-disposable`. A
  guard that has never fired is untested.
- **Preconditions checked, not assumed:** the disposable database was proved
  **empty of real data** first, and revision 0006's required Discord identifiers
  were supplied as **synthetic** values — nothing in the exercise reads them, so
  real production identifiers were deliberately kept out of a throwaway database.
- **Teardown verified independently:** no `freedom_production` remains, egress
  outside the namespace was never affected, and no credential material, real
  account or live-system value was recorded anywhere.
- **One observation, not a finding:** the harness exits `0` on a refused outcome,
  because a refusal is the *expected* result below the threshold. Recorded so a
  reader skimming exit codes does not misread it.
- **A-05: criteria 1, 2, 2a, 3, 4a, 4b, 5, 6, 7, 8, 9 Met. Only criterion 10
  remains** — the Security Reviewer's confirmation, which comes last by its own
  terms. **Criterion 4c stays owed at the deployment gate** as defence in depth.
- **I-06 and A-06 remain Open. Phase 4 remains unauthorized.**

Update 2026-08-26 (eighty-fourth) — criterion 4a met, and a self-inflicted outage.

- **A-05 criterion 4a: Met.** Executed as M-1b under decision D-p on the
  disposable `freedom_dev`: below the N-13 threshold S-15 **warns**, at it the
  same call is **clean**, and the deployed portal's live `/healthz` carries
  `break_glass_credentials: true` under the accepted C2-1 contract. Both limits
  are recorded rather than glossed — no observation under the `staging` marker
  itself, and no portal observed answering `break_glass_credentials: false`.
- **A minor thing learned by cleaning down:** the protected account **cannot** be
  deleted while audit history references it. Not a defect — history that could
  lose its actor to a later delete would not be history.
- **N-21 — this package's procedure caused an operator-visible outage.** SP-27's
  egress step reused SP-25's `iptables` rule but retargeted it from `freedomweb`
  to `foundry`. **`freedomweb` runs the portal and nothing else; `foundry` is the
  maintainer's login**, running PM2 services, tooling and browser automation. The
  rule took every one of them off TCP/443 until the Operations Owner diagnosed it
  and removed it. **He wrote the incident report before this entry existed.**
- **The reasoning failure, named:** SP-25's rule was safe because of the *account
  it named*, not its form. The control was reused and the premise that made it
  safe was discarded without being re-checked. One `ps -u foundry` beforehand
  would have shown it; it was run afterwards.
- **No platform service and no data was affected** — the portal and the bot run
  under different uids and were untouched, and the rule altered no database,
  credential, artifact or configuration.
- **Correction:** the uid rule is withdrawn from SP-27 and replaced by per-process
  **network namespace** isolation, which affects one process and cannot outlive
  it. **It is not yet verified on this host** — unprivileged user namespaces are
  disabled and the check needs root — so the revised SP-27 **verifies the
  isolation as its first step** and stops if either half fails. A control that has
  not been observed working is an assumption, which is what this finding is about.
- **SP-27 was not executed. A-05 criterion 4b remains Open**, alongside criterion
  10. **No residue:** the disposable `freedom_production` database created during
  the attempt was dropped by the Operations Owner in his own cleanup, verified
  independently — none of that name remains.

Update 2026-08-26 (eighty-third) — N-20 remediated, and the remediation needed
remediating.

- **Options 2 + 3, approved by the Operations Owner.** The restore flags are
  **unchanged** — reverting `--no-privileges` would trade a recoverable state for
  a restore that aborts mid-incident on a `GRANT` naming an absent role. Instead
  the drill records the privilege state before the destroy (**3b**), re-applies
  `runtime-grants.sql.tmpl` after the restore (**5b**), and **fails** when an
  entry present before is absent after (**6b**).
- **The runtime role is derived, not configured** — the non-owner, non-`PUBLIC`
  grantee holding table grants — so no per-database mapping can fall out of step.
  More than one such role is refused outright rather than guessed at. Schema ACLs
  are in the inventory too, because the staging failure left `public` with no ACL
  and a table-only check would have missed it.
- **The first version of the fix was wrong, and an unrelated test caught it.**
  Step 6b originally demanded the inventories be *identical*. But 5b re-applies
  the canonical template to every table, so a database whose grants had drifted
  ends with **more** entries than it started with — and exact equality fails the
  drill for having repaired something. **The check now asserts loss, not
  difference**, which is the property N-20 is about.
- **Both directions tested.** The falsification copies the drill beside its own
  template with 5b removed — exactly the pre-N-20 behaviour — and requires it to
  fail. **That test earned its place twice:** an earlier attempt passed
  *vacuously*, because a previous broken run had already stripped the grants and
  left nothing to lose. It now asserts its own precondition instead of trusting
  the database to be as expected.
- **Verified live as well as in tests:** with 5b removed the drill exits 1 with
  the new message; with it, `freedom_test`'s 99 runtime privilege rows survive the
  round trip. **Suites: bot 2423 passed** (+3), drill file 35 passed.
- **Owed:** SP-10 should be re-run **once on `freedom_staging`**, the only target
  with a genuinely restricted runtime role and therefore the only one where the
  original defect was reachable. Until then the fix is proved on the disposable
  database only.
- **Nothing else moved.** I-06, A-05 and A-06 remain Open; **Phase 4 remains
  unauthorized.**

Update 2026-08-26 (eighty-second) — M-4 executed; SP-10 passed, and found the
most consequential defect of the day.

- **The backup was checked, not assumed.** `pg_dump` produced 143,986 bytes at
  mode `0600`, and **`pg_restore -l` listed 241 archive entries** before anything
  depended on it — plan §14.3's "restore-tested, not reported successful", applied
  to the backup itself.
- **The consequence was put to the Operations Owner before the destructive step:**
  `freedom_staging` holds his only enrolled passkeys, so a failed restore would
  cost A-05 criteria 1, 2, 2a, 3, 5, 6, 7 and 8 and a fresh SG-3 ceremony. He
  accepted it against three mitigations.
- **S-14 observed on the deployed unit** — the portal refused a schema it was not
  built for, naming both revisions. The `0013 → 0012 → 0013` round trip left the
  census **identical**.
- **SP-10 Passed as a procedure.** Backup, destroy, restore, inventory. Verified
  independently rather than on the script's verdict: 31 tables, census identical,
  **6/6 guard functions**, 10 triggers, and the append-only trigger observed
  **still refusing** a DELETE — inside a rolled-back transaction, so the answer
  cost nothing.
- **N-20 — Blocking.** After that successful restore, **both units crash-looped
  to `NRestarts=35`/`36`**. The row inventory was perfect and the platform could
  not read its own database: the restore dropped `freedomweb`'s privileges
  entirely and left the `public` schema with no ACL. **A row count cannot see a
  missing GRANT**, so the drill printed `Restore verified`. In production this is
  an outage *after* a recovery, at the worst possible moment.
- **Why the disposable rehearsal missed it:** EX-3 re-applied the runtime grants
  as a separate later step, so the gap was covered by the next thing in the
  sequence instead of exposed by it. Two procedures in the right order hid a
  defect either alone would have shown.
- **Recovered within the granted authority and verified:** grants re-applied,
  `freedomweb=INSERT,SELECT,UPDATE` restored, **TRUNCATE still denied**, both
  units `running`, `/healthz` ok at `17:29:18Z`.
- **Remediation recommended, not applied:** the drill should re-apply the grants
  as its final step **and** assert the runtime role's privileges in its
  comparison. A documented step an operator must remember is exactly what failed
  here — in a rehearsal, with two people watching.
- **S-12 Not Run after three attempts**, every failure a setup error and none the
  portal's: the first was invalidated by N-20 underneath it, the second read a
  stale journal window, the third failed because `/etc/freedom-blades` is
  `750 root:root` so the service account cannot even reach its own environment
  files. **The check is proven to work at code level (`root_permissive`), which is
  not the deployed evidence TC-OPS-04 asks for, and it is recorded as Not Run.**
- **N-15 downgraded on that same evidence.** The recommendation to tighten the
  environment files to `0600` is **withdrawn**: the directory denies the service
  account traversal, so the group-read bit is unreachable. The original assessment
  is left in place and corrected rather than silently revised.
- **SP-08 stands at 12 of 15. TC-OPS-04 is not complete.**
- **Six rows closed today:** TC-OPS-05, SP-02, SP-03, SP-09/TC-OPS-01, SP-13/
  TC-LIM-02, SP-10. **I-06, A-05 and A-06 remain Open; Phase 4 remains
  unauthorized.**
- **Teardown owed:** `/tmp/sp10-2026-08-26/` holds dumps containing real
  credential public keys, Discord identity and audit history. Mode `0600`, outside
  the repository, retained as the rollback of last resort and **to be shredded
  when today's sittings end.**

Update 2026-08-26 (eighty-first) — M-3 executed; TC-LIM-02 closes, TC-OPS-04 does not.

- **Method changed before execution, with the Operations Owner's agreement.** The
  sheet's twelve edit-restart cycles would have meant twelve outages against a
  single backup. Instead: **one** real restart-to-failure for the systemd chain,
  and the rest through a new reviewable tool, `tools.startup_refusal_probe`, which
  calls the same function the deployed process calls at startup, against the same
  environment file, with one variable overridden. **The evidence level is recorded
  rather than implied:** the probe is configuration-layer evidence and does not
  claim to cover systemd.
- **SP-08: eleven of fifteen refusals observed.** S-02, S-05 and S-11 in **both**
  directions. **S-08 was exercised with the real key values** — the deployed CSRF
  key set as the cursor key — and the refusal names both variables while printing
  neither. **S-12 outstanding** (needs the artifact filesystem; scheduled with
  M-4), S-13 test-enforced, S-14 deferred to M-4, S-15 to SP-27. **TC-OPS-04 is
  not complete and is not recorded as complete.**
- **S-11 proved on the deployed unit**, with the refusal text, `Failed with result
  'exit-code'` and systemd's restart counter climbing to **8** before the file was
  restored. Recovery verified at `16:31:22Z`.
- **N-18, and it is the more serious of the two.** `systemctl restart` returned
  **0** and `systemctl status` showed `active (running)` — 8 ms after start, before
  the process had evaluated its configuration. **Following this package's own run
  sheet literally would have recorded a refusal as a non-refusal**, on a service
  that was crash-looping. Corrected: check `NRestarts` or the journal, seconds
  later.
- **N-19 (minor):** the deployed environment file is not shell-sourceable — an
  unquoted multi-word `WEB_WEBAUTHN_RP_NAME` makes `.` drop the variable silently.
  It changed nothing here, because no *required* variable was lost and every probe
  would have said so. Recorded because any procedure that sources the file has the
  same hole.
- **SP-13 / TC-LIM-02 Passed, exactly.** `WEB_MAX_REQUEST_BYTES=1048576` against
  Caddy's `max_size 1MiB`. **The snapshot half is not a gap:** neither side mounts
  a submission route, which is the accepted design (route contract §1.2), and the
  production template already fences the future change. Flagged for Codex, because
  the accepted row names two routes and only one exists.
- **Five rows closed today:** TC-OPS-05, SP-02, SP-03, SP-09/TC-OPS-01, SP-13/
  TC-LIM-02. **I-06, A-05 and A-06 remain Open; Phase 4 remains unauthorized.**

Update 2026-08-26 (eightieth) — M-2 executed; TC-OPS-01 closes.

- **SP-09 / TC-OPS-01 Passed.** Every portal route answered **503** while the
  switch was engaged — **including a mutation route**, so the switch closes writes
  and not merely reads — with the full N-26 security header set, `Retry-After`,
  `Cache-Control: no-store` and a maintenance body carrying **no exception detail,
  no internal path and no identity**. `/static/` served normally. Full recovery
  verified at `15:47:33Z`.
- **The half the criterion exists for:** the Operations Owner confirmed the
  **Discord bot still answered a command** and **Foundry still loaded** while the
  web perimeter was closed. Loopback observations could never have shown that. A
  switch that took the community's bot down with the portal would be an outage,
  not a kill switch.
- **Two of this package's own instructions were wrong, and the portal was not.**
  (1) The sheet said to engage as `freedomweb`; the switch directory is
  `root:freedomweb` with no group write, so it must be **root** — caught before
  the sitting rather than during it. (2) The sheet expected `/healthz` to answer
  `200`; it answers **503**, because it carries a `kill_switch` check of its own.
- **That second one is better behaviour than the criterion asks for.** The
  accepted rule is only that the switch must not *refuse* `/healthz`, and it does
  not: the response is health's own verdict, `status: degraded` with
  `kill_switch: false` and every other check `true`, told apart from the
  middleware's refusal by its content type and its absence of `Retry-After`. A
  monitor is therefore told *"deliberately in maintenance"* rather than *"host is
  gone"*. **I nearly recorded this as a defect and caught it by reading the body
  rather than the status code.**
- **N-16 (minor):** the tool's success message names only `/healthz` as staying
  up, omitting `/static/`, which the accepted D-03 correction added. During an
  incident that would make correct behaviour look like a second fault. One-line
  fix offered, **not taken unilaterally**.
- **N-17 (minor):** the exact engage time was not captured, because the tool
  writes it into the switch file and the release deletes it. The window is bounded
  by its recorded start and verified recovery, which satisfies the criterion but
  is looser than every other timestamp here. The run sheet now takes `date -u`
  either side of both actions.
- **Four rows closed today:** TC-OPS-05, SP-02, SP-03, SP-09/TC-OPS-01. **I-06,
  A-05 and A-06 remain Open; Phase 4 remains unauthorized.**

Update 2026-08-26 (seventy-ninth) — M-1 executed; SP-02 and SP-03 close.

- **SP-02 Passed.** Both environment files are root-owned, not world-readable and
  outside the repository. The Operations Owner attests the staging secrets share
  **no value** with production and were generated independently — a statement that
  cannot be established by inspection and must not be. **Neither file was
  opened**; only metadata was read, plus four identifier lines by an expression
  anchored to exact variable names that cannot match the client secret.
- **N-15, minor deviation.** The files are `0640 root:freedomweb`; SP-02 specifies
  `0600`. The properties that matter hold. The group bit is unnecessary — systemd
  reads `EnvironmentFile` as root before dropping to `User=freedomweb` — and close
  to harmless, because an account already running as `freedomweb` can read the
  same values from its own `/proc/self/environ`. **Recorded, not repaired**;
  tightening is the Operations Owner's call and is not urgent.
- **SP-03 Passed, and the attestation is corroborated rather than merely
  recorded.** The staging guild is provably not `PRODUCTION_GUILD_ID`, and the
  redirect URI is the staging origin. **Discord snowflakes carry their own
  creation time**, so the identifiers date themselves: the staging application,
  guild and admin role were created **within 48 minutes of one another on
  2026-08-23** — the day the staging-address decisions were taken — and **3 years
  8 months after** the production guild. Consistent with a purpose-built test
  server, inconsistent with a reused production object.
- **One half rests on attestation and is recorded as doing so:** the *application*
  cannot be checked against a recorded production value, because the repository
  records none — there is no `PRODUCTION_CLIENT_ID` constant.
- **I-06 remains Open.** Criterion 1 still needs the proxy-boundary parity half,
  SP-13 / TC-LIM-02, which is **Not Run**. Three of the nine outstanding staging
  rows have now closed today: TC-OPS-05, SP-02 and SP-03.

Update 2026-08-26 (seventy-eighth) — the gate-off window is decided and bounded.

- **D-r: option 1.** A tightly bounded window covering M-5, M-6 and the M-7
  block, gate restored immediately afterwards, **both times recorded**. Written up
  as procedure **SP-29** with explicit open and close steps.
- **What is accepted, stated rather than implied:** for the window's duration an
  unreviewed build is reachable by anyone who knows the hostname, which
  Certificate Transparency published at issuance. **What still protects it** are
  the application's own controls — Discord OAuth, guild and role verification,
  CSRF, origin and host checks, the authentication limiter and the kill switch —
  which are the controls under test.
- **Resequenced on safety grounds: M-2 comes before the window.** The kill switch
  is the emergency stop for it, and proving it works *before* the outer
  protection is removed is the right order rather than the convenient one.
- **A closing stop condition is written in:** if the window would have to stay
  open past the end of a session, it is closed first and reopened next time. An
  unbounded window is a different decision from the one approved.
- **Nothing executed by this update.** No RAID disposition moves; TC-OPS-05
  stays Passed; **Phase 4 remains unauthorized.**

Update 2026-08-26 (seventy-seventh) — the 415s explained, and the sitting they
would have spoiled.

- **The password prompt was the proxy gate.** The staging site imports a Caddy
  `basic_auth` fragment whose username is literally `peter`. **The platform has
  no password authentication at all** — N-13 forbids a permanent local password
  — so the prompt could only have come from in front of the application.
- **Mechanism, offered as a hypothesis rather than a conclusion:** a challenge
  arriving mid-flight interrupts the form `POST`; the browser's retry keeps the
  cookies and origin, which is why it reaches the content-type check rather than
  the authentication one, but arrives **without the body**, so nothing declares a
  content type and the handler answers `415`. Two retries, two `415`s; the single
  `401` is a later `POST` after the complete reload.
- **The sign-out control is not implicated** — it is a plain form with a hidden
  CSRF field and nothing enhances it — **but nothing here positively proves
  sign-out works on this build either.** A deliberate one-click check is added to
  SP-11/M-7b as step 2a. **A-05 criterion 7 is left as it stands**, on the
  2026-08-24 evidence.
- **N-14, and it was found by chasing the anomaly rather than by reading the
  plan.** The deployed site file already says the gate "must be gone before the
  final security-header evidence run", because a `401` in front of the
  application is not the response the accepted contract describes. **M-5 as
  scheduled would have observed Caddy's answer for the early-response case and
  recorded it as the application's** — evidence that would have looked complete
  and been wrong.
- **The higher-stakes consequence:** the same interruption can hit the Council
  import **apply** in M-7b and the measured apply in M-7c, where it would corrupt
  a measurement or make a success look like a failure. Both sheets now carry the
  warning.
- **A decision is owed** on how the gate-off window is handled; three options are
  set out in the staging evidence, with a tightly bounded window recommended.
  `infra/staging/rotate-test-gate.sh` prints a fresh password once if the current
  one is not to hand.
- **Nothing else moved.** TC-OPS-05 stays **Passed**; I-06, A-05 and A-06 stay
  Open; **Phase 4 remains unauthorized.**

Update 2026-08-26 (seventy-sixth) — TC-OPS-05 closes, at the third observation.

- **Deployed under P-5** (a decision distinct from the morning's, because this
  code is unreviewed by Codex). New PID 328111, observed working at
  `2026-08-26T14:17:47Z`.
- **The line that carried both defects now carries neither:**
  `client-34b16d41 - "GET /auth/discord/callback?<redacted> HTTP/1.1" 303`.
  22 lines, counts summing back to 22 — complete coverage of the interval. No
  name, no Discord identity, no character identifier, no token, no plaintext
  address.
- **The pseudonym earned its keep:** every access line in the window carries the
  **same** `client-…` value, so an operator can still see it was one client
  throughout. That is why the field was pseudonymised rather than deleted.
- **TC-OPS-05: Failed → Passed.** The first of the nine outstanding staging rows
  to close, and the only row that was outright failing.
- **Coverage limit recorded rather than left implicit:** no worker job ran in the
  observed interval, so worker output during a real preview and apply is still
  unobserved. SP-12 should be re-observed once after M-7c/M-7d before submission.
- **A new open question, not a conclusion.** `POST /v1/auth/logout` answered
  **415 twice** and **401 once**. Reaching 415 means the request carried a
  session cookie and a valid origin but the wrong content type — which the
  shipped sign-out control **cannot** produce: it is a plain HTML form with a
  hidden CSRF field, no JavaScript touches the route, and it carries no
  `hx-boost`. A stale tab or a hand-made request explains the counts equally
  well. **If a real sign-out click returns 415, session revocation is broken on
  the deployed build** — security-relevant, and A-05 criterion 7 currently reads
  **Met**. Referred to the Operations Owner and to SP-11/M-7b.
- **Everything else unchanged.** I-06, A-05 and A-06 stay Open; R-23 stays an
  active accepted residual; **Phase 4 remains unauthorized.**

Update 2026-08-26 (seventy-fifth) — M-1a executed. N-7 is fixed on the deployed
system, and the same procedure found N-13.

- **The deployment worked and is verified on the running system.** Restart at
  `2026-08-26T12:26:49Z`, new PID 296069; all three units active; `/healthz` ok
  with all eight checks true and `environment: staging`; the rollback trigger did
  not fire. The rollback copy was taken **before** the restart and confirmed to
  contain no filter, so it really was the pre-fix code.
- **N-7 is closed on the deployed build.** The callback line now reads
  `"GET /auth/discord/callback?<redacted> HTTP/1.1" 303 See Other`. The defect
  SP-12 found on its first run is gone from the running portal, which is what the
  repository fix alone could not say.
- **N-13 — and TC-OPS-05 still fails.** The same 21-line journal window (counts
  summing back to 21, so complete coverage) shows **the client IP address in
  plaintext** on every access line. **This is not a judgement call:** operational
  contract §5 prohibits "IP addresses in plaintext" in every metric, log line and
  dashboard. `--proxy-headers` means it is the **true visitor's** address, on the
  same line as the OAuth callback.
- **The cause was mine.** The N-7 filter deliberately preserved the client field
  and its docstring called that a virtue — written without checking it against
  §5. One prohibited class was fixed and another left in place while the result
  was described as safe to read.
- **Remediated, not deployed.** The client field becomes a **keyed** pseudonym,
  `client-<8 hex>`. Keyed because an unkeyed digest of an IPv4 address is not
  pseudonymisation — 2^32 candidates is seconds of compute. The key is per
  process and never persisted, so correlation holds within one process lifetime
  and nothing joins across restarts. **This is the pattern the contract already
  accepts** for rate-limit trips, recorded as a bucket hash.
- **Tests 59 → 68**, each falsified first, plus a live proof against a real
  running uvicorn showing the address and the credential both absent while
  method, path, version and status survive. **Two existing tests were amended**
  — both asserted the client field was untouched, which is what N-13 changes;
  they now assert exactly two fields redacted and three provably unchanged.
- **Suites:** web **2407 passed / 80 skipped** (+9, all this finding's), bot
  **2420 passed**.
- **What it needs, and it is not covered by this morning's authorization.**
  Decision 4 authorized deploying **the reviewed N-7 fix**. This is new code
  Codex has not seen, so a second restart is a separate decision for the
  Operations Owner. **TC-OPS-05 stays `Failed`** until it is deployed and SP-12
  re-runs over a second fresh interval.
- **Nothing else moved.** I-06, A-05 and A-06 stay Open; R-23 stays an active
  accepted residual; the Phase 3 gate stays open; **Phase 4 remains
  unauthorized.**

Update 2026-08-26 (seventy-fourth) — every authority is granted; execution now
waits only on the operator being at his console.

- **All eight answered** (change-log **C-P3.5-V**): **D-o confirmed** as Security
  Reviewer; **SG-2 granted**; an **SG-3 extension granted** for M-1b and M-1c with
  his presence at each; the **N-7 deployment and SP-12 re-run authorized**;
  **SP-27 authorized** as written; window **today, excluding 20:30–22:30 MET**;
  criterion 4a **option 1** (**D-p**); SP-10's instrument **route A** (**D-q**).
- **A grant is not evidence.** Nothing has been executed. **TC-OPS-05 stays
  Failed**; I-06, A-05 and A-06 stay **Open**; R-23 stays an active accepted
  residual; the Phase 3 gate stays open; **Phase 4 has not begun and remains
  unauthorized.**
- **D-q applied the same day.** `backup-restore-drill.sh` now accepts
  `freedom_staging` behind **two independent, non-default signals**, with a loud
  banner and **no override for production at all**. A defect was fixed while the
  file was open: the permitted-database list was written twice, and the copy that
  matters for safety is the second one — the one checking where libpq actually
  landed. It is now computed once and used by both gates. Every existing
  connection proof is untouched.
- **Three falsifying tests, and the third is the one that matters:** the staging
  name gate is shown to **open** without ever drilling staging, by supplying both
  signals plus a hostile `PGHOSTADDR` and asserting exit **3** (connection
  refused, nothing touched) rather than exit **2** (name refused). Bot suite:
  **2420 passed**.
- **D-p removes no observation.** S-15 branches on `is_production` alone, so the
  `development` marker takes the identical path a staging-marked process would.
  What it gives up is recorded rather than glossed: no observation under the
  staging marker itself, and no portal answering `/healthz` with
  `break_glass_credentials:false`.
- **The remaining blocker is physical presence, not authority.** This account is
  in the `sudo` group but has no password, and is not in `adm`/`systemd-journal`,
  so it can neither restart a unit nor read the system journal. Every root-level
  sitting — the N-7 deployment, SP-12, the kill switch, the deliberate-refusal
  restarts, the staging drill and SP-27's `createdb`/`iptables` — needs the
  Operations Owner at the console.

Update 2026-08-26 (seventy-third) — the supervised-session preparation is done,
and preparing it found two defects.

- **Everything in inventory §7 that SG-1 released is now built**, so no sitting is
  spent on preparation: **C-5** `tests/perf_snapshot_fixtures.py`, **C-6**
  `tools/snapshot_perf_harness.py`, **C-11/C-12** `tools/breakglass_observation.py`,
  **C-7/C-9** `phase-3-p3-5-supervised-run-sheets.md`, **C-8**
  `phase-3-p3-5-c8-staging-drill-guard-proposal.md`. **C-10 stays last.**
- **N-10 — A-05 criterion 4a is not executable as written.** It asks for the
  observation "under `WEB_ENVIRONMENT=staging`" **and** "on a **disposable**
  database". Each environment is bound to exactly one database name
  (`adapters/database/config.py:66`), so a staging-marked process must target
  `freedom_staging` — the deployed database holding the protected account's two
  **real** credentials, which the same criterion forbids manipulating. **Observed
  refusing (S-01), not inferred from the rule.** The same shape as Codex finding
  B-1: two halves of one criterion that cannot both hold. **Not resolved here** —
  three options are recorded and the choice is the Security Reviewer's. The
  harness refuses `staging` outright until it is taken.
- **N-11 — SP-10 has no instrument.** `backup-restore-drill.sh` refuses any target
  but `freedom_dev`/`freedom_test` **by design**, and says so in its header. The
  C-8 proposal offers a two-signal guard extension with three falsifying tests,
  **not applied**; route A or route B is Peter's decision with Codex's review.
- **N-12 — two unexplained tests and four files the tree cannot agree about.** The
  65 pre-existing bot-suite files collect **2379** today against a recorded
  **2377**, with no tracked test file modified since. Separately and certainly,
  four tracked test files are `0600` in the working tree while Git records
  `100644`. Minor; reported rather than silently repaired, and neither figure is
  asserted to be the wrong one.
- **The fixtures are sized from the real observation, not from convenience.**
  `folder-32` encodes to **16,287,681 bytes** against Rehearsal B's real
  **16,287,185** — a drift of 496 bytes. The `bound` profile reaches **99.4%** of
  N-20 at **131 Actors**, which records something worth knowing before the
  sitting: once Actors are real-sized, **the byte bound binds long before N-20's
  500-Actor bound**.
- **Two of the five performance bounds have no accepted figure anywhere** and are
  printed as `PROPOSED`. They need acceptance **before** the run they judge; the
  other three are N-47, N-45 and C-11's throughput criterion, cited rather than
  invented.
- **Guards falsified, not asserted.** Every refusal in the credential harness is
  made to fire in a test: no acknowledgement, a non-empty database, a credential
  it did not create, a database it did not prepare. The production branch is shown
  refusing with **S-15** below the threshold and passing at it — the second half
  being the falsification that the refusal is the threshold and not
  production-marking itself.
- **Verification:** bot **2417 passed** (38 of the 40 new tests are this
  package's), web **2398 passed / 80 skipped** unchanged, Foundry module **155
  pass**, both `compileall` clean, `git diff --check` clean, single Alembic head
  `0013`, asset and visual-freeze manifests **4/4** and **14/14** OK. Suites run
  serially (F-6). Formatter, linter and type checker remain **not configured**.
- **Nothing moved.** No staging procedure ran, no host state or service was
  changed, no credential was touched, no database outside disposable
  `freedom_test`/`freedom_dev` was contacted. TC-OPS-05 stays **Failed**; I-06,
  A-05 and A-06 stay **Open**; R-23 stays an active accepted residual; SG-2 and
  the SG-3 extension remain ungranted; **Phase 4 has not begun and remains
  unauthorized**.

Update 2026-08-26 (seventy-second) — the P3.5 authority request is issued; every
remaining procedure waits on it.

- **One request, six decisions.** `docs/review/phase-3-p3-5-authority-request-2026-08-26.md`
  asks Peter Duscha, in the roles he holds, to: confirm or reject **D-o** and
  change-log **C-P3.5-U** as Security Reviewer; grant **SG-2** for the staging
  build and its named procedures; grant an **SG-3 extension** for the two
  remaining credential-touching procedures; authorize **deploying the reviewed
  N-7 fix by service restart** and a **fresh-interval SP-12 re-run**; authorize
  **SP-27** as written; and confirm the proposed window.
- **Every procedure carries its owner, duration, rollback trigger and evidence
  destination**, decomposed into twelve sittings of 15–30 minutes each per D-g,
  totalling roughly five attended hours.
- **The N-7 deployment is a service restart and nothing else**, established from
  the deployed unit: `WorkingDirectory=/opt/freedom-blades/platform`, so the fixed
  source is already on disk; the unit file is unchanged by the fix; the running
  process started `2026-08-25T22:46:33Z` while the fix was written
  `2026-08-26T09:36:51Z`. Rollback is `git show HEAD:tools/portal_server.py` plus
  a restart — the state running today.
- **N-9 raised, not silently corrected.** This document says in several places
  that "SG-3 remains ungranted", while the 2026-08-24 supervised-session evidence
  §7 records SG-3 **approved that day** and its procedures SP-07, SP-20, SP-21 and
  SP-22 executed and Passed. **Minor — record accuracy; no evidence is affected**
  and no procedure ran without authority. The request therefore asks for an SG-3
  *extension*, not a fresh grant. The historical entries are left as written.
- **Verified while preparing the request, not asserted:**
  `tests/web/test_n7_access_log_redaction.py` **59 passed**; `git diff --check`
  clean; `run_resource_checks` confirmed at `application/web/startup.py:80`;
  `EXPECTED_DATABASES["production"] == "freedom_production"` confirmed at
  `adapters/database/config.py:18`.
- **Nothing moved.** TC-OPS-05 stays **Failed**; I-06, A-05 and A-06 stay **Open**;
  R-23 stays an **active accepted residual**; SP-27 stays **Not Run**; EX-11 and
  EX-12 are still owed; the Phase 3 gate stays open; **Phase 4 has not begun and
  remains unauthorized**. No host state, service, database or credential was
  touched.

Update 2026-08-26 (seventy-first) — Codex re-review reproduced the N-7 leak;
I-1 corrected properly, and the earlier remediation's claim was false.

- **The finding is correct.** Codex ran the filter over `record.args` set to a
  **list** containing the callback target and the credential rendered intact. The
  previous remediation traversed tuples and mapping values, handed everything else
  to `_redact` as a scalar, and `_redact` changed only strings — **while its
  docstring claimed every unrecognised record failed closed.** A false claim in a
  security control's own documentation is worse than the gap it described.
- **Not fixed by adding `list` beside `tuple`.** Two further shapes were
  reproduced beyond the one Codex named: a `set`, and **an object carrying the
  target only in its `__str__`**. The set of objects that can render a query string
  is not enumerable, so any enumeration is a claim that becomes false later — the
  same failure mode, one container along.
- **The fallback no longer looks at structure.** An unrecognised record is
  rendered by the filter and the rendered **text** is redacted, then stored with
  `args = None`. The guarantee is now a property of the output and states in one
  line: **no character after the first `?` survives.** A record that cannot render
  becomes a placeholder carrying the exception's *type name* and nothing else —
  which also closes a second defect, since a malformed record previously carried
  its `TypeError` into whichever handler formatted it. Attached tracebacks and
  stacks are redacted the same way.
- **The pinned path is untouched.** Uvicorn 0.32.1's five-argument access line
  still loses only its request target, so every ordinary access record keeps its
  client, method, HTTP version and status code. That is what makes the aggressive
  fallback affordable.
- **Tests 27 → 59**, each leaking shape asserted twice — unfiltered to reproduce,
  filtered to prevent — and every assertion made against the fully rendered
  `LogRecord.getMessage()` rather than against mutated arguments.
- **Stale evidence counts corrected** in the inventory's N-7 row and in the
  sixty-seventh update above, annotated in place with their cause. Historical
  statements describing the earlier review runs are left as they were.
- **Suites green:** web **2398** passed / 80 skipped, bot **2377** passed, Foundry
  module 155 pass. Live uvicorn end-to-end N-7 proof re-run: **PASS**.
- **Nothing else moved.** TC-OPS-05 remains **Failed** pending deployment and an
  SP-12 re-run; SP-27 remains Not Run; SG-2 and SG-3 remain ungranted; D-o still
  awaits Peter's confirmation; the Phase 3 gate remains open; no host state or live
  service was changed. **Returns to Codex for focused re-review.**

Update 2026-08-26 (seventieth) — Codex interim review returned Changes Requested;
all three findings remediated.

- **B-1 (Blocking) — accepted, and the reviewer was right.** The D-n amendment
  rested on treating "production-marked" and "publicly exposed" as the same event.
  They are not: `run_resource_checks` is a plain function, so S-15's production
  branch is reachable with **no listener, no bind and no route**. **D-n would have
  weakened a security precondition while appearing to resolve a circularity that
  did not exist.**
- **Corrected as D-o (change-log C-P3.5-U).** **4b returns to A-05** as a closure
  criterion, discharged by a new guarded exercise **SP-27** — disposable
  `freedom_production` with synthetic credentials, outbound egress blocked,
  `run_resource_checks` called directly so no socket is ever opened, then full
  teardown. **4c** keeps a deployment-gate re-observation as defence in depth,
  never a substitute. Operational contract §7 items 9 and 10 are now reconciled
  **explicitly** instead of item 10 narrowing item 9 by implication.
  **This awaits Peter's confirmation as Security Reviewer**, because it supersedes
  a decision he recorded — it is implemented rather than held because it
  **re-imposes** a control the earlier decision relaxed.
- **I-1 (Important) — remediated, and the fix was found by a failing test.** The
  N-7 filter passed unrecognised record shapes through untouched and its tests
  enshrined that, so a uvicorn upgrade could have restored disclosure with the
  suite green. The precise branch is now gated on the pinned **format contract**
  rather than the record **shape** — gating on shape was itself unsafe, and the
  new test proved it by catching a six-argument record whose credential sailed
  past the redaction. Everything else now **fails closed**. Tests 20 → 27,
  including a pin on uvicorn's access-log call in both protocol implementations.
  *(Superseded 2026-08-26: "everything else fails closed" was **not true** — the
  fallback still enumerated containers and Codex reproduced a leak through a list.
  Corrected in the seventy-first update; this bullet is left as the claim that was
  made.)*
- **I-2 (Important) — corrected.** The inventory's SP-10 row carried a stale
  sentence claiming EX-3 had never run, contradicting the same row. It was residue
  from an earlier edit, not a second assessment; the row now distinguishes
  TC-OPS-02's evidenced disposable half from its Not Run staging half.
- **Codex confirmed the remaining credits:** D-l's scoping, D-m, SP-04, TC-UI-01/02
  as satisfying the literal responsive rows without closing R-23, and all five N-8
  citations. The N-7 severity assessment — including that **no rotation is
  indicated** — was independently reviewed and upheld.
- **Suites green:** web **2366** passed / 80 skipped, bot **2377** passed.
- **Returns to Codex for re-review.** Nothing is closed; TC-OPS-05 remains Failed
  pending deployment, SG-2 remains ungranted, the Phase 3 gate remains open.

Update 2026-08-26 (sixty-ninth) — interim Codex review requested.

- **Requested, and deliberately scoped.** `phase-3-p3-5-codex-review-request-2026-08-26.md`
  asks for an independent implementation review plus a distinct security-focused
  view of N-7. **It is not EX-11 or EX-12 and does not consume them** — both
  mandatory gate passes remain owed over the completed package, which does not yet
  exist.
- **Why now rather than at completion.** Three decisions, an amendment to an
  accepted A-05 closure criterion, a security finding with its fix, and four new
  artifacts are the foundation everything subsequent cites. Rework is cheap now.
- **The request names where the author expects to be wrong**, rather than leaving
  the reviewer to find it: D-n's criterion amendment; the N-7 severity conclusion
  that no rotation is indicated; the crediting of SP-04 and TC-UI-01/02 from
  existing observations; the claim that all five N-8 rows are covered; and the
  traceability method itself, which produced a wrong figure once and was corrected.
- **Nothing is committed.** The review request says so and offers to commit
  unchanged if Codex prefers a fixed revision.
- **No gate decision is requested or implied.** SG-2 and SG-3 remain ungranted,
  TC-OPS-05 remains Failed pending deployment, and Phase 4 remains prohibited.

Update 2026-08-26 (sixty-eighth) — the N-7 fix is implemented and proved; all four
missing P3.5 artifacts now exist.

- **N-7 remediated and proved.** `tools/portal_server.py` installs a
  `uvicorn.access` filter replacing the query string with `?<redacted>`. **20
  regression tests**, including a falsification asserting the leak is real without
  the filter, and an **end-to-end proof against a real running uvicorn**: the
  credential is present without the filter and absent with it, path preserved.
  **The unit file is unchanged**, so deployment is a service restart. TC-OPS-05
  stays **Failed** until deployed and re-observed.
- **Artifact 2 created** — the final requirements-to-evidence traceability. All
  **318** accepted contract rows were resolved **mechanically and in both
  directions**: **294** resolve to a real existing test, **19** are staging,
  browser or device rows Not Run or partial by evidence level, and **5** have no
  resolvable citation.
- **A wrong intermediate figure was checked rather than published.** A first pass
  searching only for tests naming their contract ID reported **99 uncited rows**.
  For a large family the contract names the test rather than the reverse, so the
  figure was wrong in the alarming direction. The corrected bidirectional result
  is what the artifact reports, and the correction is recorded in it.
- **Finding N-8, and it is good news.** The five rows with no resolvable citation
  — TC-AUTH-17, TC-BG-19, TC-MIG-19, TC-MIG-21, TC-MIG-28 — were each chased
  individually. **Every one has a passing test.** They are **citation gaps, not
  coverage gaps**; the citations are supplied in the artifact and the accepted
  contract is left unedited.
- **Artifact 4 created** — accessibility and browser evidence, with F-1's TC-UI
  renumbering reconciled against the accepted numbering, TC-UI-03 and TC-UI-05
  given the citations F-1 showed they lacked, and every row not met at its
  accepted level recorded as not met.
- **N-1 resolved without renumbering.** `plan-SP-23` and `evidence-SP-23` are
  distinguished by name throughout; renumbering timestamped evidence would edit
  history to tidy a label.
- **All four previously missing artifacts now exist.** Only the final submission
  remains unwritten, and it must not be written until the evidence it would
  summarise exists.
- **Suites green:** web **2359** passed / 80 skipped, bot **2377** passed.
- **Still nothing closed.** SG-2 ungranted, nine staging rows Not Run, TC-OPS-05
  Failed pending deployment, the Phase 3 gate open.

Update 2026-08-26 (sixty-seventh) — SP-12 executed; TC-OPS-05 fails on a real
credential disclosure, remediated in the repository the same night.

- **SP-12 executed and TC-OPS-05 FAILED.** The Operations Owner reviewed 5535
  journal lines, reduced to distinct message shapes whose counts sum back to 5535
  so nothing was sampled. **No name, character or Discord identity appears
  anywhere.** But the OAuth authorization code and state were being written to the
  journal in clear text on every successful login — **finding N-7**.
- **The application was not the leak.** Uvicorn is started with no
  `--no-access-log` and no log configuration, so its default access logger writes
  the whole request line including the query string, and R-04
  `/auth/discord/callback` is the one route that receives credentials as query
  parameters because that is how the provider redirects.
- **Severity, stated both ways.** Not an emergency: the observed codes are spent,
  the flow is PKCE-bound so a code alone cannot be exchanged, and the journal is
  readable only by root and `adm`/`systemd-journal`. **No client secret, cookie,
  CSRF token, recovery grant or WebAuthn material appears; no rotation is
  indicated.** But the criterion is that monitoring carries **no** token data, and
  the same configuration would behave identically in production.
- **Remediated in the repository, not yet deployed.** `tools/portal_server.py`
  installs a `uvicorn.access` filter that replaces the query string with
  `?<redacted>`, keeping the route identifiable. **The unit file is unchanged**, so
  deployment is a service restart rather than unit surgery.
- **The leak was reproduced before it was fixed.** ~~20~~ **59** regression tests
  including falsifications asserting each leak is real without the filter, plus an
  end-to-end proof against a real running uvicorn showing the credential present
  without it and `?<redacted>` with it.
  *(Count corrected in place 2026-08-26 on Codex's instruction: this row is a
  current-state record, and the module grew 20 → 27 → 59 across two rounds of
  finding I-1. The rest of the row stood as written.)*
- **TC-OPS-05 stays Failed** until the fix is deployed and SP-12 re-run against a
  fresh journal. That is a result rather than a gap, which is progress.
- **Why it survived four gates:** P3.1 proved the OAuth flow and P3.4 proved the
  rendering; neither looked at what the running process writes. Same shape as
  F-15 and F-16.
- **Suites green:** web 2359 passed / 80 skipped, bot 2377 passed.

Update 2026-08-26 (sixty-sixth) — the two disposable-database rehearsals are
executed; one cutover defect found and corrected.

- **EX-3 executed.** `upgrade head → downgrade 0010 → upgrade head` against
  `freedom_test`, after a pre-migration backup, with the documented rollback costs
  read **before** the run. The schema round trip is **exact**: 986 lines, zero
  differences.
- **The 0013 rollback boundary was observed refusing on a real database**, not
  only in a unit test. A synthetic committed-but-unpublished apply job was seeded,
  the downgrade refused with exit status 1 and the documented message, and the
  database was left **at head, complete and usable** — the guard fails closed.
  Removing the job reopened the boundary, as the operations document states.
  Runtime grants were re-applied and re-verified (11 passed).
- **EX-4 executed.** Backup, checksum, destroy, restore and a table-and-row
  inventory comparison, over **seeded synthetic rows** so the comparison could
  fail. Identical across all 31 tables. The restored append-only trigger was then
  verified **still refusing** a DELETE — a restore that returns rows but not
  guards would pass a row count and still be a failure.
- **TC-OPS-02's disposable half is now evidenced. Its staging half (SP-10)
  remains Not Run.**
- **Finding N-6, raised and corrected.** The filesystem cutover moved the
  repository by rename, and `mv` preserves the mtime and size CPython uses to
  validate cached bytecode — so **163 `.pyc` files still named
  `/opt/discord-bots/freedom-bot`**, a directory that no longer exists. Six web
  tests failed with `OSError: could not get source code` and every displayed path
  named the vanished tree. The caches were cleared; the suite then ran **2339
  passed, 0 failed**. No source, test or document changed. **The six failures were
  not product defects**, and file paths quoted from any post-cutover run on this
  host should be read as naming the pre-cutover tree.
- **Full verification set green:** web 2339 passed / 80 skipped; bot 2377 passed;
  Foundry module 155 passed; asset integrity 4/4; visual freeze 14/14; compile
  clean in both environments; `git diff --check` clean; single linear head `0013`.
  Formatter, linter and type checker remain **not configured, not run, not
  passed**.
- **Artifact 3 of five created** — `phase-3-p3-5-staging-and-operations-evidence.md`,
  with the staging procedures listed and their result columns **empty**.
- **Nothing closed.** SG-2 is still ungranted, no staging procedure has run, and
  the Phase 3 gate remains open.

Update 2026-08-25 (sixty-fifth) — A-05 criterion 4 split; all three P3.5 decisions
formally recorded as C-P3.5-T.

- **D-n — A-05 criterion 4 split: approved by Peter Duscha as accountable Security
  Reviewer.** **4a** — startup and `/healthz` observed below and at the N-13
  threshold under `WEB_ENVIRONMENT=staging`, on a disposable database with
  synthetic credential records — remains an A-05 closure criterion and is Open and
  executable. **4b** — S-15's production refusal — moves to the **deployment gate**
  as a named go-live check. It is owed there, not waived.
- **The premise was verified in code, not assumed.**
  `WebEnvironment.is_production` is `PRODUCTION` alone and S-15 refuses only in
  production, so no staging-marked process can observe that refusal; and
  `WEB_ENVIRONMENT=production` is itself refused on this host before the lifespan
  runs. A-05 gates public exposure, so a criterion satisfiable only after exposure
  could never close.
- **N-13 is unchanged and no control is weakened.** Two enabled credentials are
  still required and retirement below two is still refused.
- **Traceable and reversible by construction.** The original criterion wording is
  retained **struck through rather than deleted** in execution plan §13.2, with
  rationale, explicit non-effects and a reversal procedure. All three decisions —
  D-l, D-m, D-n — carry a per-decision reversal table in change-log **C-P3.5-T**,
  which also records reasons, alternatives rejected, scope, dependency, risk,
  security and operational effects.
- **Neither Codex pass has seen these decisions.** Both required P3.5 review passes
  remain outstanding and will see them.
- **A-05 now has one open executable criterion (4a) plus criterion 10.** SG-2 is
  the only thing gating execution of every remaining I-06 procedure, and it is
  **not** granted by the D-n approval, which was a wording decision carrying no
  host authorization.

Update 2026-08-25 (sixty-fourth) — the two blocking P3.5 decisions are taken.

- **D-l — real Foundry data in staging: approved by the Data Owner.** A real
  `the-guild` Actor folder may be submitted to `freedom_staging` as a supervised
  operational input for TC-PERF-01/02 and TC-OPS-03, under the Rehearsal A/B
  discipline: never committed, no Actor name or payload in any artifact, artifact
  shredded and import tables truncated at teardown. §8.2's synthetic-only rule is
  superseded **for those procedures only**. `Characters (active)` is the primary
  folder, being the one the contract names and the only one with a real baseline.
- **D-m — TC-PERF-02 repeat runs: option (b).** One real-folder apply reported
  honestly as **n = 1**, plus two bounded-synthetic applies. Three runs against one
  input is impossible by design: the commit fence returns runs 2 and 3 as
  duplicates.
- **Four procedures unblocked.** SP-11, SP-15, SP-16 and the A-06 input rule move
  from Blocked to Not Run. About two hours of supervised work is released.
- **A-05 criterion 4 re-analysed against the code, not assumed.**
  `WebEnvironment.is_production` is `PRODUCTION` alone, so a staging-marked process
  cannot produce S-15's refusal however it is configured — confirming the earlier
  analysis and exposing a circular dependency, since A-05 gates the very exposure
  its criterion 4 needs to exist. Recommendation recorded: split into **4a**
  (re-observable on a disposable database under the staging marker and the accepted
  C2-1 health contract, which the existing observation predates) and **4b** (moved
  to the deployment gate). **Only the Security Reviewer may record that split; it
  has not been applied.**
- **Still nothing closed.** No RAID disposition moved, SG-2 remains unrequested,
  and Phase 4 remains prohibited.

Update 2026-08-25 (sixty-third) — P3.5 evidence inventory produced; nothing closed.

- **The inventory is complete and closes nothing.** Every remaining SP and TC item
  is recorded with its status under the execution plan's strict vocabulary, the
  exact existing evidence that bears on it, and what is missing from its full
  contract. No partial observation was converted into a pass. See
  `docs/review/phase-3-p3-5-evidence-inventory-2026-08-25.md`.
- **The environmental blockers are gone; the procedures are not done.** A staging
  build exists and is healthy, the worker is active, `freedom_staging` is at head
  `0013` with a genuinely restricted runtime role, and two real passkeys
  authenticate against the deployed origin. What remains is execution of the named
  procedures. TC-BG-02's browser half is **Passed**; plan-SP-23's browser work is
  passed in part and recorded Not Run against its full contract.
- **Five findings raised, two Important.** `SP-23` now names two different
  procedures across accepted documents (N-1); TC-PERF-02's three-run method is not
  executable against one input because the commit fence makes repeats duplicates
  (N-2); the deployed portal has no snapshot-submission route, so TC-OPS-03 and
  TC-PERF-01/02 need a supervised transport step first (N-3); the accepted
  documents conflict on whether a real Foundry folder may be used in staging (N-4,
  **referred to the Data Owner, not chosen**); and `freedom_staging` shares its
  owner role with the disposable databases (N-5).
- **Two decisions block about two hours of supervised work.** N-4 (real-folder
  data rule) and N-2 (repeat-run method). Both are Peter's, and both cost minutes.
- **Nothing is authorized by this.** SG-2 and SG-3 are unrequested, no RAID
  disposition moved, no gate decision is requested, and Phase 4 remains
  prohibited.

Update 2026-08-25 (sixty-second) — Phase 3 gate audited; closure refused on
missing mandatory evidence.

- **Phase 3 remains open.** Peter requested closure and a Phase 4 start. The
  accepted P3.5 criteria still have mandatory Not Run evidence: I-06's staging,
  browser, operations and performance procedures; A-05 criteria 4 and 10; and
  final A-06/R-23 dispositions and gate artifacts.
- **Phase 4 implementation did not start.** The implementation plan and accepted
  Phase 3 delivery plan prohibit it before the Phase 3 gate is validly recorded.
  See `docs/review/phase-3-gate-disposition-2026-08-25.md`.
- **Current executable work:** complete the P3.5 staging evidence package. The
  deployed staging services and filesystem cutover are valid inputs, but they do
  not substitute for TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05 or
  TC-PERF-01…03.

Update 2026-08-25 (sixty-first) — C2 health-contract correction accepted.

- **C2 accepted.** Peter Duscha accepted the additive VM-16
  `break_glass_credentials` check after Codex's independent and security-focused
  recommendation. The signal remains boolean-only, freshly queried, fail-closed
  and loopback-only; `VIEW_MODEL_VERSION` remains `vm-1`.
- **No broader acceptance inferred.** A-05 criterion 4 still needs its remaining
  deployed observation/production-refusal evidence, and criterion 10 remains the
  Security Reviewer's final confirmation. The Phase 3 gate, public exposure and
  Phase 4 remain unauthorized.

Status date: 2026-08-25 (sixtieth update: Codex independently re-reviewed the
operational evidence produced by the filesystem cutover and recommends closing
F5/S-2. The supported installer ran, the worker is active, and systemd reports the
shared and worker environment files in the required order. C2 remains proposed;
A-05 criteria 4 and 10, the Phase 3 gate, public exposure and Phase 4 remain open
or unauthorized.)

Update 2026-08-25 (sixtieth) — F5/S-2 operational evidence independently
re-reviewed.

- **F5/S-2 closure recommended.** The filesystem cutover executed the supported
  installer with unit regeneration. Codex independently observed
  `freedom-worker.service` active from the product-owned runtime and repository,
  with `/etc/freedom-blades/portal.env` followed by
  `/etc/freedom-blades/worker.env` in systemd's effective configuration.
- **Focused verification passed.** The installer/worker-file suite passed 34
  tests and the health/provider suite passed 26 tests against the disposable
  PostgreSQL database. The preserved review environment was used because the
  fresh production runtime deliberately does not contain pytest.
- **Authority boundaries unchanged.** This technical recommendation does not
  approve C2, close A-05 criteria 4 or 10, close the Phase 3 gate, authorize
  public exposure, or release Phase 4. See
  `docs/review/phase-3-p3-5-f5-s2-operational-re-review-2026-08-25.md`.

Status date: 2026-08-25 (fifty-ninth update: the filesystem-layout migration is
executed and directly verified. The accepted target is
`/opt/freedom-blades/{platform,runtime,reference,workspace}` with service data at
`/srv/freedom-blades` and configuration at `/etc/freedom-blades`. The bot, portal
and worker are active from the fresh target environments; Caddy, PostgreSQL,
assets, endpoints and durable queue state passed direct checks. Historical
evidence is unchanged.)

Update 2026-08-25 (fifty-ninth) — product-owned filesystem layout cut over.

- **Cutover complete.** The repository, offline Actor exports, service data and
  configuration moved by same-host rename to their accepted product-owned paths.
  Every legacy source path is absent and the repository-local virtual-environment
  links resolve to the fresh runtime environments.
- **Direct runtime evidence.** `freedom-bot`, `freedom-web` and `freedom-worker`
  are active with their effective working directories, executables and
  environment files under the new layout. The emergency and health endpoints
  answer `200` with the accepted Host header, the Caddy password gate answers
  `401`, PostgreSQL is active, the durable queue is empty and asset integrity is
  4/4.
- **Cutover corrections recorded.** Existing repository-local symlinks require
  `ln -sfnT` rather than plain `ln -s`, and the preserved portal environment file
  requires a controlled `/srv/freedom/` to `/srv/freedom-blades/` path-prefix
  update. Four runtime inputs whose legacy `0600` modes refused the service
  account were restored to tracked-file mode `0644`; no secret value was read or
  printed.
- **Rollback hold remains.** Obsolete environments and review trees under
  `/opt/discord-bots` are not removed until the Operations Owner releases the
  observation hold. Existing product gates remain unchanged.

Update 2026-08-25 (fifty-eighth) — product-owned filesystem layout prepared; cutover held.

- **Administrative scope only.** The repository directory stops presenting the
  platform as a Discord bot. Process names, databases, roles, accounts, DNS and
  the Git remote are unchanged.
- **Prepared target.** Repository `/opt/freedom-blades/platform`; virtual
  environments below `/opt/freedom-blades/runtime`; offline actor exports below
  `/opt/freedom-blades/reference`; artifacts and kill switch below
  `/srv/freedom-blades`; environment files below `/etc/freedom-blades`.
- **Reproducible and reversible.** Active deployment files carry the new paths,
  a regression refuses legacy roots in that active set, and
  `docs/operations/filesystem-layout-migration.md` gives preconditions, fresh-
  virtualenv preparation, cutover, direct verification, rollback and delayed
  cleanup. Historical review records retain the paths that were true when their
  evidence was collected.
- **Hold point.** No directory has moved, no virtual environment has been
  created, and no service or Caddy configuration has changed. Cutover requires
  focused/full verification followed by the Operations Owner's privileged
  maintenance authorization.
- **Existing gates unchanged.** F5/S-2 and A-05 remain open; this administrative
  rename cannot close operational or security evidence.

Status date before this update: 2026-08-25 (fifty-seventh update: Codex accepted the C3/C4
repository remediation with no blocking finding. Its one Low diagnostic finding
is corrected: the byte-exact sentinel now preserves `cat`'s read-failure status,
suppresses raw stderr and emits the controlled refusal, with an executable
regression. **Nothing is closed:** F5/S-2 still await the authorized installer run,
A-05 criteria 4 and 10 remain open, and the C2 contract change still awaits the
Acceptance Authority. No public exposure or Phase 4 start is authorized.)

Update 2026-08-25 (fifty-seventh) — C3/C4 accepted; Low read-failure diagnostic corrected.

- **C3 and C4 repository remediation accepted.** Codex found no blocking defect:
  strict worker-file validation and the corrected redundancy/readiness semantics
  stand. The C2 boolean health signal remains recommended for approval.
- **Low diagnostic correction.** `worker_env_file_problem` appended a sentinel to
  preserve trailing newlines, but the sentinel's successful `printf` hid a failed
  `cat`; the file was still refused, with the wrong content-mismatch explanation
  and raw `cat` stderr. The substitution now exits with `cat`'s status, suppresses
  raw stderr and emits only `could not be read.`. A twenty-second C3 regression
  exercises an unreadable regular file and asserts status, stdout and empty stderr.
- **Boundaries unchanged.** The supported installer still needs its authorized
  staging run and direct worker evidence. The C2 build still needs deployment and
  observation, the Acceptance Authority's contract decision, and A-05 criteria 4
  and 10.

Status date before this update: 2026-08-25 (fifty-sixth update: Codex re-reviewed the C1/C2
remediation, accepted both core mechanisms and recommended approving the health
contract change, and requested changes on two further findings. C3 — an existing
worker environment file was confirmed only for the value of `WORKER_ENABLED`, so a
file carrying extra assignments would have been adopted and would have overridden
portal configuration — is remediated with a strict, executable validation. C4 — the
documentation equated "fewer than two credentials" with "the emergency route cannot
be used", which is false for exactly one — is corrected everywhere it appeared.
**Nothing is closed:** F5/S-2 still wait on the authorized installer run on the
staging host, A-05 criteria 4 and 10 remain open, and the C2 contract change still
awaits the Acceptance Authority. No public exposure or Phase 4 start is
authorized.)

Update 2026-08-25 (fifty-sixth) — Codex re-review: C1/C2 mechanisms accepted, C3 and C4 remediated.

- **Codex accepted both core mechanisms.** The installer now connects the worker
  template to its executable consumer, the generated unit agrees with the deployed
  one at directive level, and the C2 health check is boolean-only, fresh,
  fail-closed and discloses no credential material. **Codex recommends approving
  the additive C2 health-contract change** once C4's language is corrected — a
  specialist recommendation, not the Acceptance Authority's approval.
- **C3 (High) — an existing `worker.env` was not safely confirmed.** The check
  read the last `WORKER_ENABLED=` assignment and accepted the file if it said
  `true`. Because the worker unit reads that file **after** the shared portal file,
  every other assignment in it overrides the portal's: a file carrying
  `WEB_DATABASE_URL=…` and `WORKER_ARTIFACT_ROOT=…` above a `WORKER_ENABLED=true`
  passed, silently redirecting the worker's database and artifact store. Ownership,
  mode and symlink shape were not checked at all.
- **C3 is remediated with a validation that can be executed.** The check now
  refuses anything but a regular file (never a symlink), owned `root` and the
  service group at mode `0640`, whose complete content is exactly one line reading
  `WORKER_ENABLED=true` with a final newline. It lives in
  `infra/staging/lib/worker-env-file.sh` so that 21 tests run the operator's own
  check rather than grepping the script for statements — extra variables,
  duplicates, comments, `false`, wrong case, empty, missing and extra newlines,
  five wrong modes, a wrong group, a symlink, a directory and a missing file. The
  installer still refuses rather than repairing, and still never overwrites.
- **C4 (Medium) — "cannot be used" was wrong for one credential.** A single
  enabled credential still authenticates; it is below N-13's redundancy floor, and
  a lost or broken key is then a lockout. Telling an operator mid-incident that the
  authenticator in their hand is unusable would be worse than telling them nothing.
  The guide now carries a three-state table (two or more / exactly one / none or no
  account), and the claim is corrected in the health check's docstrings, the
  lifespan comment, the S-15 rationale in the configuration contract, the VM-16
  block, the earlier return package and this register. A test asserts the corrected
  wording so the next edit cannot quietly restore it.
- **Nothing closed.** F5/S-2 remain pending the authorized installer re-run on the
  staging host and Codex's re-review; A-05 criterion 4 stays open on both halves;
  criterion 10 is untouched; the C2 contract change remains proposed.
- **Verification.** Portal suite 2339 passed / 80 skipped, bot suite 2106 passed /
  267 skipped and 2373 with the disposable database configured, `node --test` 50
  passed, asset integrity 4/4 OK, `git diff --check` clean. Both suites run
  serially against the one shared disposable database.

Update 2026-08-25 (fifty-fifth) — Codex requested changes; C1 remediated, C2 implemented as a proposed contract change.

- **Codex requested changes on the executed handover.** Two High findings. The
  full return package is
  `docs/review/phase-3-p3-5-codex-c1-c2-remediation-2026-08-25.md`.
- **C1 — the F5 repair was not integrated into the staging installer.** The
  corrected template asked for a second environment-file placeholder that
  `infra/staging/setup-portal-host.sh` had never heard of, so the supported
  provisioning path would have written a literal
  `EnvironmentFile=__WORKER_ENVIRONMENT_FILE__` into `/etc/systemd/system` and kept
  appending the same losing `Environment=WORKER_ENABLED=true`. The finding is
  correct and the cause is worth naming: a unit template is an input to a program,
  and nothing in the suite connected the two. The installer now defines and writes
  `/etc/freedom-web/worker.env` (one line, `root:freedomweb`, `0640`), substitutes
  the placeholder, appends no `Environment=` line, refuses to install a unit whose
  directives still carry a placeholder, and asks systemd for the effective
  configuration after `daemon-reload`. Five repository tests render each unit
  through the installer's own substitutions; four of them fail against the
  installer as reviewed.
- **The generated unit is the deployed unit.** Rendering the template through the
  corrected installer and comparing against the running, manually repaired
  `freedom-worker.service`: every directive identical, differing only in comment
  text. The repository can now reproduce the repair it could not reproduce on
  2026-08-25.
- **F5 and S-2 are not closed.** They are remediated in the repository and await
  Codex's re-review and one root-held step: re-running the supported installer on
  the staging host and observing `freedom-worker` active from the journal — not
  from `/healthz`'s `worker_heartbeat`, which cannot tell an idle worker from an
  absent one.
- **C2 — F6 is a failure of A-4, not a new concern.** Accepted. Of the two paths
  Codex offered, this package takes the first: `/healthz` gains
  `break_glass_credentials`, false while the protected administrator holds fewer
  than two enabled credentials, and the lifespan logs the S-15 warning it used to
  only assign. Amending A-4 instead would have accepted a manual credential count
  as the only channel on exactly the hosts where S-15 is deliberately not a
  refusal, and would have closed the third instance of one pattern — S-4,
  `worker_heartbeat`, F6 — by lowering the question.
- **The contract change is additive and proposed, not approved.**
  `VIEW_MODEL_VERSION` stays `vm-1`: a name is added to a closed vocabulary,
  nothing is removed, renamed or narrowed. No route, view-model field, status code,
  template, migration or schema changes. The check carries a boolean, never the
  count, and is re-asked on every request rather than remembered from startup.
  Approval and the security review of its disclosure and availability effects are
  the Acceptance Authority's and the Security Reviewer's.
- **Expect `degraded` and `503` on any host where nobody has enrolled**, including
  staging until A-05's ceremony. That is the endpoint answering the question A-05
  exists to close, and it is documented where an operator will read it.
- **A-05 criterion 4 remains open.** Its `/healthz` half now exists in the
  repository and has been observed on no host; its production-refusal half stays
  unobservable before an authorized production deployment. Criterion 10 is
  untouched.
- **Verification.** Portal suite 2338 passed / 80 skipped (baseline 2330/80), bot
  suite 2085 passed / 267 skipped (baseline 2080/267) and 2352 passed with the
  disposable database configured, `node --test` 50 passed, asset integrity 4/4 OK,
  `git diff --check` clean. Both suites were run serially against the one shared
  disposable database. No migration.

Update 2026-08-25 (fifty-fourth) — handover executed; three A-05 criteria evidenced; two findings raised.

- **The reviewed package is committed and deployed.** `0bef692` carries the
  accepted S-4/S-5/S-6/S-7/S-9 remediation, both Codex re-reviews and the N-32a
  approval records. The portal was restarted onto it, and the running process is
  proved to postdate the commit by a mechanism rather than a favourable
  timestamp: every tracked source file predates the process start, and CPython
  validates cached bytecode against source mtime and size, so no `__pycache__`
  entry can serve pre-remediation code. **S-1 is satisfied for this deployment.**
- **A-05 criterion 6 is evidenced in full.** R-41 and R-46, addressed directly
  from inside an authenticated page of a live break-glass session with synthetic
  identifiers, both refused `403 emergency_surface_refused` — N-65's
  continuity-surface check, which `authorize()` evaluates *before* the route's
  capability requirement and long before any handler object lookup. **F3 is
  answered.**
- **Criterion 3 is evidenced.** Retiring below two enabled credentials is refused
  before any write, exit status 1. This is a different property from the
  already-recorded refusal of a *retired* credential at login: it is that a
  **live** credential cannot be made dead while it is the second-to-last one.
- **Criterion 9 is satisfied.** `docs/operations/break-glass-credential-custody.md`
  documents custody, replacement, loss and recovery without credential material,
  and Peter Duscha accepted it on 2026-08-25.
- **S-4 is closed end to end.** Under a real provider outage isolated to the
  portal's service account — the same `iptables` method as 2026-08-24 — `/healthz`
  reported `identity_provider: false`, `degraded` and `503`. The same rule on the
  same host reported `ok` and `200` throughout the outage a day earlier. The
  isolation was re-proved in both directions and the rule removed in the same
  sitting.
- **S-2 is resolved, and its cause was ours.** `freedom-worker.service` had never
  started, and could not have: the unit set `Environment=WORKER_ENABLED=true`
  while reading the shared portal `EnvironmentFile`, and systemd gives the file
  precedence, so the shared file's required `WORKER_ENABLED=false` silently won.
  **The arrangement came from this repository's own operations guide**, which
  offered it explicitly. Recorded as **F5**; the guide and the unit template are
  corrected, and the worker is running.
- **F6 raised, no fix proposed.** A below-threshold credential count is detected
  and then reported to nobody outside production: the warning is assigned to
  `composition.startup_warnings`, which nothing reads, is never logged, and never
  reaches VM-16. A staging account down to one credential answers `/healthz`
  byte-identically to a healthy one. This is the third instance of one pattern
  after S-4 and `worker_heartbeat`, which is why it is a finding rather than a
  note. The route surface is frozen and VM-16 is an accepted closed vocabulary,
  so the disposition is the Security Reviewer's.
- **Criterion 4's production half is not observable before production exists.**
  Tested 2026-08-25 rather than assumed: `WEB_ENVIRONMENT=production` pins the
  public origin, the OAuth redirect URI and the Discord guild to their **real**
  production values, and configuration is refused before the lifespan runs — so
  S-15's production branch is never reached. The obstacle is not the database
  name, which was the earlier analysis and was wrong. Either A-4 is amended to
  what a non-production host can observe, or criterion 4 stays open until
  production configuration exists; that is the Security Reviewer's judgment.
- **All five code findings are now closed end to end.** S-4, S-5, S-6, S-7 and
  S-9 are each accepted in the repository **and** observed behaving on the
  deployed build (SP-25, SP-26). S-5 is the one the package began with: limiter
  refusals used to answer `429` with a correlation reference and write nothing.
  Three references were shown to the operator during the re-observation sitting
  and all three resolve to their audit rows.
- **No gate moved.** Criterion 4 (blocked on wording, not work), criterion 10 and
  every I-06 procedure remain outstanding. Public exposure and Phase 4 remain
  unauthorized.

Previous status date: 2026-08-24 (fifty-third update: Codex independent and security
re-reviews accepted the supervised-session repository remediation, and Peter
Duscha, Acceptance Authority, accepted N-32a at 10 WebAuthn challenge issuances
per source IP per 10 minutes. The accepted challenge budget is separate from
N-32's unchanged assertion budgets. Remaining live evidence and operational work
keeps A-05, I-06, A-06, R-23 and the Phase 3 gate open. No public exposure or
Phase 4 start is authorized.)

Update 2026-08-24 (fifty-third) — remediation re-reviewed; N-32a accepted.

- **Repository remediation accepted.** Codex's independent and distinct security
  re-reviews closed the prior S-5/S-6 code blockers and accepted the repository
  corrections for S-4, S-7 and S-9. No new Important or Blocking code defect was
  found. The full portal suite independently passed 2,330 tests with 80 documented
  caller-matrix skips.
- **N-32a accepted.** Peter Duscha, Acceptance Authority, accepted 10 WebAuthn
  challenge issuances per source IP per 10 minutes. Challenge issuance no longer
  spends N-32's stricter verification budget; N-32 remains 5 assertions per
  source IP per 10 minutes and 10 per platform account per 60 minutes.
- **No gate moved.** Live R-41/R-46 denial observations, evidence-record operator
  fields, S-1/S-2 operational work and the remaining A-05/I-06 criteria are still
  open. Public exposure and Phase 4 remain unauthorized.

Previous status date: 2026-08-24 (fifty-second update: the supervised browser and
authenticator session ran in full and raised nine findings, **none of which any
test suite had caught**. Codex's independent and security reviews held two of
them blocking for A-05 criterion 7. All six code findings were remediated with 44
new tests and awaited re-review. F-15/F-17's operational half was discharged;
TC-UI-01/02 held for one browser on one platform. A-05, I-06, A-06, R-23 and the
Phase 3 gate remained open. No public exposure or Phase 4 start was authorized.)

Update 2026-08-24 (fifty-second) — supervised session executed; its findings remediated.

- **The session ran.** Two real WebAuthn ceremonies on two distinct enabled
  credentials, in Chrome on macOS 26, against the deployed staging origin, under
  a Discord outage verified in both directions and isolated to the portal's
  service account. Sign-out invalidated server-side; a retired credential was
  refused; cancellation was neutral. SP-21 issued a recovery grant, used it once,
  and had it refused on replay and again after expiry. SP-22 observed three
  withheld routes refusing at the route rather than only in the frame. Evidence:
  `docs/review/phase-3-p3-5-supervised-session-evidence-2026-08-24.md`.
- **Nine findings, none found by a test.** All were found by observing the
  running system — by fetching a page, by reading the audit rows a real ceremony
  wrote, by checking a service the health endpoint had already called healthy.
  That is the argument for this kind of session existing at all.
- **Codex reviewed both the evidence and its security posture** and held **S-5**
  (rate-limited emergency refusals write no audit record while showing a
  correlation reference that resolves to nothing) and **S-6** (every logout
  audited as `guild_member`, including a break-glass administrator with no guild
  membership) **blocking for A-05 criterion 7**.
- **All six code findings are remediated**, with 44 new tests across five new
  traceability rows: the emergency refusal audit boundary (S-5), logout
  attribution derived from the persisted authentication method (S-6), N-32's
  issuance and assertion budgets separated (S-7), failed recovery redemptions
  classified for the audit and not for the caller (S-9), and `/healthz` probing
  the identity provider rather than asserting it (S-4). Submission:
  `docs/review/phase-3-p3-5-supervised-session-remediation-submission.md`.
- **What the repository cannot close.** The two POST routes of A-05 criterion 6
  (R-41, R-46) need the Operations Owner and a live break-glass session. The
  evidence record's exact end timestamp and the SP-21 grant record ids need the
  host. S-1's deploy/reload gap and S-2's inactive worker are operational.
- **At this update, one decision was before the Acceptance Authority:** N-32a, a
  separate budget for WebAuthn challenge issuance. It was subsequently accepted
  in the fifty-third update above.
- **Governance:** remediation does not close a finding. Independent and security
  re-review are required. A-05, I-06, A-06 and the Phase 3 gate remain open;
  R-23 remains active; public exposure and Phase 4 remain unauthorized.

Previous status date: 2026-08-24 (fifty-first update: Codex accepted the completed
P3.5 frontend repository remediation for F-15/F-17 after independent implementation
and security-focused review. Strict refusal/UUID and Base64URL counterexamples
were corrected and independently probed. The real-browser and physical-
authenticator session was planned for later on 2026-08-24 and was Not Run at that
time; therefore F-15/F-17, TC-UI-01/02, TC-BG-02, A-05, R-23 and the Phase 3 gate
remained open. No public exposure or Phase 4 start was authorized.)

Update 2026-08-24 (fifty-first) — frontend code accepted; supervised evidence queued.

- **Codex accepted the repository/frontend implementation** for F-15 and F-17.
  The final review found no remaining code defect in progressive enhancement,
  CSP-safe state changes, the WebAuthn ceremony, refusal presentation, strict
  Base64URL handling, safe redirects, duplicate activation, VM-23 shell
  presentation or static-asset integrity.
- **Independent evidence:** 50 committed Node tests and 9 targeted structural
  tests passed; 10,240 independent randomized Base64URL vectors and independent
  refusal-vocabulary probes passed; 4/4 static assets verified; `git diff --check`
  was clean. Gemini's full sequential handoff reports web 2,286 passed/80 skipped,
  bot 2,346 and Foundry 155.
- **No manual evidence is pre-claimed.** TC-UI-01/02 and the physical browser/
  authenticator path of TC-BG-02/A-05 remain Not Run. A supervised isolated-
  staging session is planned for later on 2026-08-24.
- **Bounded session plan:**
  `docs/review/phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md`.
  It records prerequisites, viewport/zoom/keyboard checks, two-credential
  authentication with Discord unavailable, sign-out, cancellation, evidence
  hygiene and stop conditions.
- **Governance:** repository acceptance does not close an operational finding.
  F-15/F-17, I-06, A-05, A-06 and the Phase 3 gate remain open; R-23 remains
  active; public exposure and Phase 4 remain unauthorized.

Previous status date: 2026-08-23 (forty-second update: the portal ran for the first time on a
deployed host under its restricted service account. Four defects appeared within the
first hour, **none of which any test caught, with every suite green before and after** —
which is RAID I-06 evidenced rather than asserted. One blocking defect is fixed and
regression-tested; one blocking defect is routed to Gemini and blocks A-05 and exposure.
Two real WebAuthn credentials are enrolled — the first in the project's history — and
that is a rehearsal, not A-05's closure. No RAID item is closed, no gate decision is
requested, and Codex's two review passes are requested. The forty-first update stands
unchanged below.)

Update 2026-08-23 (fiftieth) — public-shell failure boundary typed; package resubmitted.

- **R35-32 — a broad `except Exception` hid infrastructure failure.** `_attach_public_shell()`
  caught everything and returned, with a comment claiming any failure meant "no session". It
  did not: a database outage, a repository fault or a programming error rendered a
  **healthy-looking anonymous page**. The consequence was not the wrong navigation — it was
  that a portal whose session store was unreachable would have looked fine to everyone, while
  the signed-in operator best placed to notice was quietly logged out instead of told.
- **The policy is now typed and catches `SessionAbsent` alone**, verified by AST rather than by
  reading: no cookie means no lookup at all; unknown, malformed, expired and revoked tokens
  give the anonymous shell; `ServiceDegraded` gives VM-03 with `503`, security headers and
  `no-store`; database, repository and programming failures reach the safe-error boundary as
  `500` with a correlation id and nothing else; cancellation is never caught.
- **No second renderer was added.** A public page had no handler for `ServiceDegraded`, so one
  was registered at the app boundary producing the same view, status and headers the protected
  side already gives. A test asserts a protected request still resolves its session exactly
  once.
- **19 new failure-class cases** (67 in the boundary module), including no-cookie-no-lookup,
  four unusable-token shapes, degraded store, unexpected error, cancellation, and disclosure
  checks covering cookie value, account id, session id, capability and provider detail.
- **Falsified** with the mutation asserted by AST before and after: restoring the broad catch
  fails four cases; the corrected form catches `['SessionAbsent']` and all 67 pass.
- **Verification:** web **2277 passed**, bot **2346 passed**, Foundry 155, focused web package
  157, focused script package 104, ASGI health 10 with **0 skipped**, manifests OK, compilation
  clean, `git diff --check` clean.
- **Live-host actions restated as attestations.** H-1 to H-3 were performed by Peter and
  observed by Claude; they have **not** been independently reviewed, and no RAID or gate state
  changes on the strength of them. H-4 remains Not Run.
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15 and F-17 open. Gemini remains
  unreleased. No browser has rendered this frame.

Update 2026-08-23 (forty-ninth) — shell lifecycle completed on every full page.

- **R35-26 (blocking) — public pages made a signed-in caller look signed out.** `/v1/login`
  and `/v1/auth/emergency` run no protected preamble, so they rendered the **anonymous**
  frame to everybody: a member with a live session was offered "Login" and shown no way to
  sign out. That was the remaining half of F-17, in the two pages a confused user is most
  likely to visit. Public pages now attach their caller's own frame, with exactly one owner
  per route class and no request resolving its session twice.
- **A defect the tests found, not the code review:** the first version of that fix keyed
  "is this authority current?" off `gate.refresh`, which is `None` whenever no provider token
  is stored — so it reported a **stale** Council caller as fresh and gave them the full frame.
  It now reads the projection's own freshness.
- **R35-27 — a Discord outage told people they were logged out.** A refusal raised by a failed
  refresh rendered its 503 with the anonymous frame, though the session was valid. It now
  carries the conservative session-only frame: sign-out available, and only the destination
  that needs no capability — never a privileged link resting on the refresh that just failed.
- **R35-28 — housekeeping failures were swallowed.** `find` and `sort` ran in a pipeline whose
  status nobody inspected, so superseded verifier generations accumulated while the rotation
  reported success. Each step is now attributable and each failure is named by operation
  class, with the password never printed twice and a tidy-up problem never reported as a
  failed rotation.
- **R35-29 — 48 request-boundary cases**, all database-backed, now cover public pages for
  anonymous, malformed, empty, expired, revoked, member, administrator and break-glass
  callers; the conservative frame for a stale caller; logout from a public page; and the
  degraded-503 frame with its leakage assertions.
- **All three falsified** with the mutation asserted before the result was read: 8, 1 and 3
  failures respectively against the defective forms.
- **Verification:** web **2258 passed**, bot **2346 passed**, Foundry 155, focused web package
  90, focused script package 104, ASGI health 10 with **0 skipped**, manifests OK, compilation
  clean, `git diff --check` clean.
- **`docs/review/Handover information` now contains the completion handoff** rather than the
  prior prompt (R35-31).
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15 and F-17 open. Gemini remains
  unreleased. No browser has rendered this frame.

Update 2026-08-23 (forty-eighth) — shell boundary defects fixed; rotation commit made safe.

- **R35-19 (blocking) — the rotation script could lose the new password.** After a
  successful reload it did fallible retention work *before* printing, so under `set -e` a
  failed `mv`/`find`/`sort`/`rm` exited with **the new gate serving and its plaintext never
  shown**. The password is now displayed immediately after a confirmed reload; housekeeping
  runs afterwards and reports failures as warnings that name no verifier. Eight injection
  cases; falsified against the old ordering.
- **R35-20 — the shell read the pre-refresh authority.** It was built from `gate.context`
  rather than the `context` handed to `authorize()`, so a caller whose Council role had just
  been removed kept Council navigation while the routes refused them. Now derived from the
  final context; falsified.
- **R35-21 — the shell was attached after the decision.** A valid caller *denied* a route
  received the **anonymous** frame on their 403: "Login" offered, sign-out hidden,
  mid-session. Now attached before the capability decision; falsified.
- **R35-22 — the brand link was a literal** `/v1/characters`, which R-20 refuses to an
  administrator-without-Council. It is now `shell.home_href`, always one of that caller's own
  destinations.
- **A fourth defect, found by writing the tests:** the navigation rules had been derived from
  the prose matrix and offered `Characters` to a member holding the admin role. They now
  mirror `access_control._member_read` and `Requirement.COUNCIL_OR_ADMINISTRATOR` directly.
- **R35-23 — 28 request-boundary cases** through the real preamble, refresh, `authorize()`,
  render, template and logout route: anonymous/malformed/expired/revoked sessions, all seven
  authenticated states, authenticated 403 rendering, logout with the rendered token, refusal
  of missing/empty/wrong/**another session's** token, and refresh adding and removing
  authority. Stated honestly: the refresh is driven at the `_close` seam, not through a real
  Discord round trip, because the seeded callers have no stored OAuth grant.
- **Seven no-JavaScript flow expectations corrected** — they required an administrator's page
  to link to `/v1/characters`, a page R-20 refuses them: the same defect as R35-22, expressed
  as a test expectation.
- **Verification:** web **2238 passed**, bot **2346 passed**, Foundry 155, shell unit 30,
  request boundary 28, rotation 33, ASGI health 10 with **0 skipped**, manifests OK,
  compilation clean, `git diff --check` clean.
- **Host actions:** three of the four are **done** and verified — gate rotated, corrected
  configuration installed and reloaded with `/healthz` confirmed refused publicly, and both
  emergency credentials replaced under the corrected ceremony with the unproven pair retired
  and audited. Only the Cloudflare ingress restriction remains, and it is a deployment-gate
  item.
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15 and F-17 open. Gemini remains
  unreleased. No browser has rendered this frame.

Update 2026-08-23 (forty-seventh) — the shell contract is implemented; Gemini prompt revised.

- **R35-17 / C35-05 is done.** A typed immutable shell view is supplied on every full-page
  render, derived at the request boundary from the accepted session and capability authority,
  with a closed navigation vocabulary and a matrix taken row by row from the accepted route
  contract. Logout is `POST` with the session's own CSRF token and exists only for a valid
  session — structurally, because no gate means no token.
- **Two findings the work itself produced.** Continuity scope (N-65) had to be read rather
  than capability alone: a break-glass caller holds administrator, so a capability-only rule
  offered it Snapshots, which R-40 refuses for `BG`. And the P3.4 scope guard
  `test_no_unrelated_production_files_modified` had a parsing defect — it stripped the line
  before slicing the two-column status field, so **it never caught a modification to a tracked
  file for the whole of P3.4**. Both corrected.
- **Deliberate updates to accepted P3.4 evidence,** each recorded: the header's frozen digest
  re-frozen with the old value written beside it; the "no button" assertion narrowed to its
  intent, since sign-out must be a POST submit; three read-only-page assertions scoped to the
  page body rather than the shared frame.
- **Contracts:** VM-23 added to the view-model contract and TC-SHELL-01…11 to traceability,
  both **by addition**; no accepted row rewritten.
- **Gemini prompt revised** against the real field names and narrowed to styling and
  presentation, since the backend half of F-17 is complete. It keeps its **NOT RELEASED**
  banner pending Codex review.
- **Verification:** web **2199 passed**, bot **2337 passed**, Foundry 155, shell contract 21,
  manifests OK, compilation clean, `git diff --check` clean.
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15 and F-17 open pending review
  and real browser evidence. No browser has rendered this frame.

Update 2026-08-23 (forty-sixth) — R35-13…R35-16, R35-18 done; R35-17 remains the blocker.

- **R35-13 (blocking) — the rotation script was not interruption-safe.** After the atomic
  move, `INT` or `TERM` left an **unvalidated verifier on disk whose password had never been
  shown**, and a later unrelated Caddy reload would have activated a gate nobody knew the
  password to. Rewritten as an explicit three-state transaction (`none`/`candidate`/
  `committed`) whose rollback restores the exact pre-run state, is idempotent, captures the
  exit status before running so it cannot mask the original failure, and becomes a no-op once
  committed. **Falsified with the mutation asserted before the result was read.**
- **R35-14 — verifier backups are bounded on every path.** The rollback copy is
  transaction-owned and always removed; a retained recovery generation is created only on
  successful commit, and exactly one is kept. Failed attempts no longer leave credential
  material behind, and a pre-existing retained generation survives a rollback that still needs
  the working gate.
- **R35-15 — 24 hermetic tests**, including interruption by `SIGINT` and `SIGTERM` with and
  without a previous gate, using a deterministic synchronization hook rather than a timing
  guess: the fake `caddy validate` announces it has been reached and blocks.
- **R35-16 — the ASGI skip explained exactly.** Reproduced Codex's observation (6 passed,
  4 skipped without a database) and recorded the non-skipped run (10 passed). The database
  boundary is intrinsic: `/healthz` checks the database, so the real endpoint cannot be
  exercised without an engine.
- **R35-18 — one canonical handoff.** `phase-3-p3-5-c35-remediation-handoff.md` is now the
  cumulative current document and leads with blockers; the R35 handoff redirects to it.
- **R35-17 — STILL NOT IMPLEMENTED.** No accepted-contract conflict exists; it is unstarted
  work, now scoped concretely: `RequestAuthority.render()` passes only `{"view": view}`, there
  are **30 render call sites** (portal 15, import 11, app 4) and **20 full-page templates**,
  and no `fragments/` directory, so the full-page/fragment distinction must come from the
  accepted route contract. It was not attempted rather than attempted badly.
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15, F-17 open. Gemini unreleased.
- **Peter-only host actions, all outstanding:** rotate the spent gate (now actually possible),
  install and reload the corrected Caddy configuration, re-enroll both emergency credentials,
  restrict origin ingress to Cloudflare ranges.

Update 2026-08-23 (forty-fifth) — R35 remediation partial; the rotation script was broken.

- **Codex's re-review did not accept the C35 remediation.** R35-08…R35-12 raised; the Gemini
  prompt stays unreleased.
- **R35-08 (blocking) — the gate-rotation script could never have run.** `tr … | head -c 20`
  under `set -o pipefail` exits 141: `head` closes the pipe, `tr` dies of SIGPIPE. Reproduced
  before fixing. **The gate has therefore never been rotated, and the committed password is
  still active and still spent.** Also fixed: the plaintext no longer passes through a child
  process command line. The stdin interface was established by running it — without a trailing
  newline Caddy fails with `Error: EOF`, and with one the terminator is stripped rather than
  hashed, verified against a real Caddy where the exact password answered 200 and the password
  with a newline answered 401. The whole operation is now transactional: atomic install,
  validate before reload, restore on failure, no password printed unless it is actually active,
  and a truthful statement that the OLD password remains active if a reload fails.
- **R35-09 — 11 hermetic tests** that execute the script against a temporary filesystem with
  controlled host commands. Falsified against both original defects. One falsification attempt
  silently tested the wrong thing (a `sed` delimiter collision, masked by a `grep` matching a
  comment) and was redone with an assertion-bearing edit; recorded in the handoff.
- **R35-10 — health proved at the ASGI boundary**, not only in the helper: degraded status,
  `kill_switch: false`, exact response shape, and no path, errno, exception or traceback. The
  falsification is kept as a test.
- **R35-11 — NOT STARTED.** The server-owned shell/navigation contract remains the critical
  path; F-17 cannot go to Gemini without it.
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15, F-17 open.
- **Host actions still required, none performed:** rotate the gate (never yet possible),
  reinstall the site file and reload Caddy, re-enroll both credentials, restrict origin ingress.
- **Formal record:** `docs/review/phase-3-p3-5-c35-remediation-handoff.md` (canonical; the R35 handoff now redirects there); change-log `C-P3.5-E`.

Update 2026-08-23 (forty-fourth) — Codex withheld the Gemini prompt; C35 remediation partial.

- **Codex reviewed the P3.5 interim package and did not release the Gemini prompt.** Six
  findings, C35-01…C35-06, plus C35-07 requiring the prompt to be rewritten afterwards.
- **C35-01 (blocking) — a password verifier was committed by this package.** Removed; the
  gate is now a host-local fragment imported fail-closed. **It did enter Git history**,
  verified rather than assumed: a harness checkpoint ref snapshotted the untracked file. It
  is on no branch and no remote-tracking ref, and such refs are not pushed — but Codex read
  it during review, so **the password is spent and rotation is a required Operations Owner
  action**. Neither verifier appears in any document.
- **C35-02 (blocking) — `/healthz` was publishable through the proxy**, against the accepted
  operational contract. The refusal is now the first handle block; ordering proved in the
  adapted configuration (health at route index 2, proxy at 9) and asserted by a falsified
  test. **The deployed host is still unchanged.**
- **C35-03 — F-14 now proved by PostgreSQL**, not by reading SQL: six live cases under the
  restricted role covering the exact S-14 query, effective privileges, each write class
  refused with SQLSTATE 42501, and hostile PUBLIC grants removed. 53 passed; falsified.
- **C35-04 — F-13 fixed.** An unreadable kill switch now fails the check closed and keeps
  `/healthz` answering `degraded` rather than returning 500. 6 tests; falsification kept as
  a test. **The real-ASGI regression Codex asked for is not written.**
- **C35-06 — ceremony corrected** to `residentKey: required` in both spellings, with the
  empty `allowCredentials` preserved as the control it is. **The two enrolled staging
  credentials cannot be proven discoverable** — no column records resident-key state — so
  **Peter must re-enroll both** before the supervised browser login.
- **C35-05 — NOT STARTED.** The server-owned shell/navigation contract is the largest
  remaining P3.5 backend piece, and F-17 cannot go to Gemini without it. The Gemini prompt
  now carries a NOT RELEASED banner.
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active; F-15 and F-17 open.
- **Host actions required, none performed:** rotate the gate, reinstall the site file and
  reload Caddy, re-enroll both credentials, and later restrict origin ingress to
  Cloudflare's ranges.
- **Formal record:** `docs/review/phase-3-p3-5-c35-remediation-handoff.md`; change-log
  entry `C-P3.5-D`.

Update 2026-08-23 (forty-third) — authorization boundary confirmed live; F-17 raised; both handoffs released.

- **First live confirmation of the accepted §5.2 authorization matrix**, against a real
  Discord identity holding real roles rather than a fixture: OAuth login completed and was
  audited; capabilities resolved to `{platform_administrator}` alone because only the
  protected mapping existed; **My Characters (R-20) refused the administrator exactly as
  specified (`A = ✗ 403`)** while **role capabilities (R-32) admitted them (`A = ✓`)**; and
  mapping the Council role through R-33 succeeded and was audited as
  `role_capability.mapped`. **Administrator did not imply Council** — the capability existed
  only once an administrator deliberately created the mapping.
- **F-17 — important:** the shell is static. The header renders the same three links to
  every caller, so a signed-in administrator is shown "Login"; **no template contains a
  logout control** while `POST /v1/auth/logout` exists as accepted route R-05; and no
  privileged surface is linked anywhere, so administration is reachable only by typing a
  URL. **A second scope gap, like F-15:** no P3.4 prompt asked for a capability-aware
  header or a logout control. No authorization boundary is weakened.
- **Handoffs released:** the Gemini prompt now commissions **both** F-15 and F-17
  (`phase-3-p3-5-gemini-security-key-emergency-access-prompt.md`), and the Codex interim
  review request carries all findings plus the live matrix confirmation
  (`phase-3-p3-5-interim-findings-and-review-request.md`).
- **RAID:** unchanged. I-06, A-05, A-06 open; R-23 active. No gate decision requested.

Update 2026-08-23 (forty-second) — first deployed run; F-14 fixed, F-15 routed to Gemini.

- **Environment:** `freedom-blades-test.rpgworld.org`, Cloudflare-proxied, temporary,
  password-gated at the proxy. Separate `freedom_staging` database at revision `0013`,
  restricted `freedomweb` role under peer authentication, a **separate** test Discord
  application and guild, **no real player data** and no production backup. The live
  address and the three Foundry sites were verified still serving after every change.
- **F-15 — blocking, routed to Gemini:** the passkey break-glass login **cannot be
  completed in a browser**. The emergency page renders the security-key section as a
  heading and one sentence with no control, and the site ships no application
  JavaScript at all, so `navigator.credentials.get()` cannot be invoked and routes
  R-07/R-08 are unreachable. The recovery grant — designed as the last resort for when
  every passkey is lost — is currently the only working emergency route. **It is a
  scope gap, not an implementation failure:** P3.4 Step 4 was explicitly instructed not
  to write passkey JavaScript, and no later package was commissioned to supply it.
  Prompt: `phase-3-p3-5-gemini-security-key-emergency-access-prompt.md`.
- **F-14 — blocking, fixed:** the restricted runtime role had no `SELECT` on
  `alembic_version`, the table S-14 must read to establish which schema it serves, so
  the documented restricted-role deployment could never have started anywhere. Fixed in
  the grants template as a separate documented section granting `SELECT` only, with a
  regression test that was **falsified** — removed the fix, watched it fail, restored
  it, watched it pass. 57 grants tests pass.
- **F-16 — important:** nothing in the suite asserts that a human can *complete*
  break-glass login. TC-BG-02's browser half must be carried as **Not Run** beside
  TC-SEC-07's rather than inheriting a pass from the service-level cases.
- **F-13 — minor, not fixed:** `/healthz` raises rather than reporting a fault when the
  kill-switch directory is unreadable. Accepted P3.1/P3.3 surface; raised for Codex.
- **Host findings:** the Cloudflare origin private key was world-readable and has been
  corrected by the Operations Owner (never read by Claude); the origin certificate is
  Cloudflare-issued so proxied DNS is mandatory, and the true visitor address is now
  rewritten at the proxy or the authentication limiter would have treated the entire
  internet as a single source.
- **Artifacts authored because they did not exist:** the `freedom-web` systemd unit
  template, the proxy site block, the WebAuthn registration page and its host-local
  conversion tool, the ASGI entry point, and three operator scripts.
- **A-05:** first real enrollment — two credentials on a deployed host, verified in the
  database as enabled with correct COSE keys. **Not closed:** they are bound to the test
  address's relying-party identifier and cannot authenticate against production, and no
  passkey login has yet succeeded (F-15).
- **RAID:** unchanged. I-06, A-05 and A-06 remain **Open**; R-23 remains an active
  accepted residual.
- **Reviews requested:** Codex independent implementation pass and distinct
  security-focused pass — `phase-3-p3-5-interim-findings-and-review-request.md`, six
  named questions including whether any finding should reopen a closed gate.
- **Formal record:** change-log entry `C-P3.5-C`.

Update 2026-08-23 (forty-first) — SG-1 approved; browser decision taken; F-7 and F-8 raised.

- **Decisions:** Peter approved SG-1 (the P3.5 plan) and P-2 (browser question — his own
  workstation browser against the staging loopback, the recommended option). SG-2 and SG-3
  were not requested and remain unapproved.
- **Released:** repository-scoped execution only — final traceability, the F-1 reconciliation,
  the migration and backup/restore rehearsals against the guarded disposable database, the
  missing deployment artifacts, and the staging runbook and accessibility plan as procedures
  with empty result columns. Nothing outside the repository and `freedom_test` is touched.
- **F-7 (important, blocks the A-05 ceremony):** `tools/webauthn_enrollment.py` directs the
  operator to a registration reference page in `docs/operations/` that **does not exist**, so
  there is currently no supported way to obtain the base64url credential id and COSE public key
  its `enroll` subcommand requires. EX-5 authors the page; the mechanism itself is sound.
- **F-8 (important, operator safety):** `enroll` stores a credential without recording or
  validating the relying-party identifier the browser ceremony used, while authentication
  verifies `expected_rp_id` against the running service's `WEB_WEBAUTHN_RP_ID` — which
  configuration requires to equal the public origin's own host. A credential enrolled at a
  loopback staging origin is therefore accepted and **can never authenticate** against the
  production hostname, and nothing says so until somebody is locked out. Referred to Codex as a
  structural question; no behavior change is made under this plan, because it would touch an
  accepted P3.1 contract surface.
- **A-05 criteria tightened, not weakened:** each credential must have been created under the
  intended target host's relying-party identifier, and at least one must have authenticated
  successfully against a service running that same RP ID, before A-05 can close. A
  staging-loopback enrollment is a rehearsal of the mechanism, not satisfaction of the
  assumption.
- **RAID:** unchanged. I-06, A-05 and A-06 remain **Open**; R-23 remains an active accepted
  residual.
- **Formal record:** `docs/review/phase-3-p3-5-readiness-and-execution-plan.md` §0.2;
  change-log entry `C-P3.5-B`.

Update 2026-08-23 (fortieth) — P3.5 planning opened; readiness audit complete; plan awaiting approval.

- **What was done:** a read-only readiness audit of the repository and this host, the safe
  local checks listed below, and the P3.5 readiness and execution plan
  `docs/review/phase-3-p3-5-readiness-and-execution-plan.md`. Nothing was deployed, enrolled,
  exposed or mutated outside the repository and the disposable `freedom_test` database.
- **Actual readiness — ready:** Python 3.12.3 in both virtualenvs; Node v24.19.0; PostgreSQL
  16.15 on the loopback socket; disposable `freedom_test` and development `freedom_dev`
  databases; the non-login restricted role `freedom_runtime_test`; a single linear Alembic head
  `0013` with no branches; and the socket-pinned, disposable-only backup/restore drill script.
- **Actual readiness — blocked or absent:** no staging database or role (`freedom_staging` does
  not exist); no staging Discord application, guild or credentials; no `freedom-web`,
  `freedom-web-staging` or `freedom-worker` unit on this host, and **no `freedom-web` unit
  template in the repository at all**; no portal Caddy site block artifact; `/srv/freedom` exists
  but is empty and root-owned; **no browser engine and no browser automation on this host**; no
  real device and no identified screen-reader capacity; and **no WebAuthn credential has ever
  been enrolled on any host**, so the protected administrator account does not yet exist.
- **Safe local checks, all passing:** `tests/web` 2,168 passed with 80 intentional matrix skips
  in 124.22 s; bot/domain 2,294 passed in 134.59 s (run sequentially — the two suites share one
  disposable database); Foundry module 155 passed; production asset integrity 3/3 OK; visual
  freeze 14/14 OK; bytecode compilation clean in both virtualenvs; `git diff --check` clean;
  `alembic heads`/`history`/`branches` show one linear head `0013`; `git status` clean before
  and after.
- **Checks recorded as unavailable, not passed:** no formatter, linter or type checker is
  configured in this repository — no configuration file and no such binary in either
  virtualenv. The migration upgrade/downgrade/upgrade rehearsal was **not** run in this
  read-only audit and belongs to the first approved execution step.
- **Findings raised:** F-1, the P3.4 submission's accessibility matrix renumbers the TC-UI rows
  relative to the accepted test-traceability contract, leaving TC-UI-03 and TC-UI-05 without a
  citation under their own IDs (important, traceability only — the tests themselves are named
  for the contract's numbering and pass); F-2, no `freedom-web` systemd unit template exists;
  F-3, no repository artifact defines the portal's proxy site block or its body limits, which
  TC-LIM-02 needs; F-4, no browser engine exists here. **No blocking security, authorization,
  identity, atomicity, data-integrity, recovery or reliability finding was identified**, within
  the limits of a read-only audit — this does not substitute for Codex's two review passes.
- **Forecast:** the accepted 3/5/8 focused-day P3.5 range is **retained unchanged** for the
  implementer stream and decomposed in the plan §3.1 to 3.0/5.0/8.0. Confidence remains
  Medium-low for that stream and **Low for end-to-end P3.5 completion**, because six of the
  eleven deliverables depend on host actions that have never been performed and that Claude
  cannot perform. Peter's own accountable effort — staging build, the A-05 ceremony, the
  real-device check, screen-reader capacity and the gate decision — is estimated separately in
  plan §3.2 and was never inside the accepted implementer range. No calendar date is committed.
- **Blockers awaiting Peter:** approve the plan (SG-1); decide how a browser is supplied for
  the WebAuthn registration ceremony and the browser-observed checks (workstation browser
  recommended, no new dependency); authorize and participate in the staging build (SG-2);
  authorize and participate in the credential ceremony (SG-3); perform the real-device check;
  decide screen-reader capacity; and record availability windows.
- **RAID:** unchanged, deliberately. I-06, A-05 and A-06 remain **Open** and R-23 remains an
  **active accepted residual**. Today's green local suite is activity, not evidence that moves
  any of them; the plan §12 states the exact closure criteria for each.
- **Next bounded step, on approval only:** the final requirements-to-evidence traceability, the
  F-1 reconciliation, and the migration and backup/restore rehearsals against the guarded
  disposable database. Nothing outside the repository and `freedom_test` is touched.
- **Formal record:** `docs/review/phase-3-p3-5-readiness-and-execution-plan.md`; change-log
  entry `C-P3.5-A`.

Update 2026-08-23 (thirty-ninth) — P3.4 and Step 13 accepted; P3.G4 closed; P3.5 released.

- **Acceptance decision:** Peter Duscha, Acceptance Authority, accepted Milestone P3.4
  in full, including Step 13, on 2026-08-23 and closed stop gate P3.G4.
- **Independent review:** Codex completed the independent implementation review and a
  distinct security-focused review. Both passed with no blocking or important findings.
  The final focused security/accessibility/authentication verification was 228 passed,
  99 non-blocking HTTPX deprecation warnings, and zero failures. All five literal evidence-
  validator commands reproduced their recorded exit statuses and complete output.
- **Accepted evidence:** the complete historical suites remain 2,168 web tests passed
  with 80 intentional matrix skips, 2,294 bot/domain tests passed, 155 Foundry tests
  passed, three static-asset hashes verified, 14 visual-freeze hashes verified, bytecode
  compilation clean, and `git diff --check` clean.
- **Next package:** P3.5 may begin only within the approved Phase 3 plan and must produce
  its own gate evidence. This acceptance is not a deployment or exposure decision.
- **Open operational prerequisites:** I-06 remains open pending real isolated-staging,
  browser, device and performance evidence. A-05 remains open pending establishment of
  the protected administrator account and enrollment of at least two WebAuthn credentials
  on the target host.
- **Residual evidence:** TC-UI-01/02, TC-UI-08 and TC-UI-09 remain Not Run. Peter accepts
  P3.4 with those limitations visible; they remain controlled by R-23 and the P3.5/staging
  evidence package rather than being reclassified as passed.
- **Formal record:** `docs/review/phase-3-p3-4-step-13-final-independent-reviews-and-acceptance.md`;
  change-log entry `C-P3.4-E`.

Update 2026-08-23 (thirty-eighth) — P3.4 Step 12 accepted; Step 13 complete verification & remediation submitted.

- **Decision:** Peter Duscha (Acceptance Authority) accepted Step 12 and authorized Step 13
  verification and submission. Following Codex independent review, Peter authorized bounded
  documentation remediation for findings R13-01 through R13-13.
- **Codex Review Evidence & Verification:**
  - Codex bounded focused check: 174 passed, 94 warnings in 8.75s; manifests OK; found no new implementation or focused-security blocker in the exercised surfaces. Not a complete implementation or distinct security review.
  - Complete Historical Verification: `tests/web` (2168 passed, 80 matrix skips, 1063 warnings in 127.20s),
    bot suite (2294 passed in 136.38s), Foundry suite (155 passed in 212.38ms), asset integrity 3/3 OK,
    visual freeze 14/14 OK, bytecode compilation clean in both venvs, `git diff --check` clean, CSS tokens
    (0 undefined), contrast ratios (48/48 PASS AA/AAA, 1 exempt).
- **Remediation Dispositions (R13-01 through R13-13):**
  - **R13-01 (Screen Matrix Rebuild):** Reconstructed screen matrix mechanically from accepted route and
    view-model contracts across all 26 production templates and fragments under `adapters/web/templates/`.
  - **R13-02 & R13-06 (Exact Route & Handler Traceability):** Mapped every route (R-01..R-10, R-20..R-38, R-40..R-49, M-01)
    to its exact handler symbol (`app.py`, `static_assets.py::StaticAssets`, `portal_routes.py`, `import_routes.py`).
  - **R13-07 & R13-10 (Exact Valid Test Symbol Traceability):** Replaced all filename-only or invalid citations with
    exact top-level test symbols in `path/to/test_file.py::test_symbol` notation (`test_oauth_flow.py`, `test_request_authority_and_lifecycle.py`,
    `test_break_glass_login.py`, `test_oauth_refusal_audit.py`).
  - **R13-11 (Material R-01 and R-10 Evidence):** Provided material behavioral test evidence for R-01 (`test_the_session_cookie_looked_up_and_cleared_is_still_graph_as`)
    and R-10 (`test_health_evaluation_still_receives_graph_a`, `test_the_kill_switch_closes_the_portal_and_leaves_health_answering`).
  - **R13-12 (Individual F-SEC-01..11 Traceability):** Individually listed F-SEC-01 through F-SEC-11 in the requirements matrix without range shorthand.
  - **R13-03 & R13-08 (Narrow Presentation Candidate Inventory):** Defined truthful presentation candidate inclusion rule;
    recorded exactly 53 live candidate artifacts plus 1 rename-provenance row (`freedom-blades.b0a1f3305683.css`) = 54 evidence rows,
    with literal Git states, current SHA-256 digests, and explicit naming of excluded unchanged backend modules.
  - **R13-04 (Authoritative RAID Meanings):** Restored authoritative RAID meanings for R-22 (contract drift),
    R-23 (accessibility regression), RR-17 (commit fence lock), RR-18 (recovery publication), and RR-19
    (roll-forward schema boundary); separated factual presentation bounds (character name 120-char bound,
    single-provider linking constraint, static asset delivery) without assigning RAID IDs.
  - **R13-05, R13-09 & R13-13 (Project Records, Literal Extraction Validator & In-Memory Falsification Suite):** Reconciled project records,
    embedded copy/paste-ready standalone inline Python AST-aware validator command in submission (extracting 193 test references across 105 unique node IDs
    and verifying both asset/freeze manifests directly), replaced all placeholder invocations with independently executable literal commands that extract the canonical validator block, verified 3 negative in-memory falsification tests
    (capturing full stack tracebacks and exit status 1 for false test path, false test symbol, prohibited shorthand), verified unquoted-reference extraction coverage, and narrowed Codex review claims.
- **Honest Not-Run Status:**
  - TC-UI-01 & TC-UI-02: Not Run (no browser binary or automation framework installed on host).
  - TC-UI-08: Not Run — Peter/maintainer real-device acceptance.
  - TC-UI-09: Not Run — assistive-technology/screen-reader review.
- **Submission Record:** Rebuilt `docs/review/phase-3-p3-4-submission.md` with complete 26-template screen
  matrix, comprehensive handler/test traceability, verification transcript, 54-row inventory, and external digest design.
- **Stop Condition & Gate State:** Gemini stops at Step 13 submission boundary. Independent Codex
  implementation review and distinct security-focused review of the remediated submission are requested
  and pending. Gate P3.G4 remains open, RAID I-06 and A-05 remain open, and Milestone P3.5 remains held.
- **Boundaries Unchanged:** Zero live services, secrets, staging, deployment, production PostgreSQL, or real
  player data were accessed.

Update 2026-08-23 (thirty-seventh) — P3.4 Step 12 remediation completed (R12-08).

- **Decision:** Peter Duscha (Acceptance Authority) released Step 12 remediation under
  the accepted remediation release-policy clarification to resolve Codex review findings.
- **Remediations Addressed:**
  - **R12-08 (Real Username/Global-Name Presentation Boundary):**
    - Retracted nonnumeric `external_identities.subject` test fixture.
    - Verified `test_account_identity_subject_display_canonical_snowflake` on `GET /v1/account/identities` (R-35) with canonical decimal snowflake.
    - Identified real production provider projection (`discord_users`, `discord_guild_memberships`), service (`identity_search`), view model (`IdentitySearchResultsView`), and template (`identity_search.html`) on route `GET /v1/council/identity-search` (R-24).
    - Exercised all 7 in-bound hostile vectors across `span.candidate-username strong` and `span.candidate-global-name`, verifying inert DOM rendering, literal template non-evaluation, exact code-point sequence matching, and snowflake integrity.
    - Tested over-bound behavior: exact 80-char in-bound representation preserved (`DISCORD_NAME_BOUND=80`), while over-bound 10,000-char strings are refused by database constraint `VARCHAR(80)`.
    - Added falsification probe F-SEC-11 on real ASGI `GET /v1/council/identity-search` responses.
- **Verification Results:**
  - **Dedicated Step 12 Test Suite (`tests/web/test_p3_4_security_and_escaping.py`):** 70 passed, 83 warnings in 6.75s (run 3 times consecutively: 6.66s, 6.57s, 6.75s; all 70 passed).
  - **Six Primary Step 12 Suites:** 298 passed, 0 skipped, 0 failures, 232 warnings in 12.47s (`test_p3_4_security_and_escaping.py`, `test_p3_4_identity_and_role_views.py`, `test_p3_2_request_boundary.py`, `test_security_controls.py`, `test_p3_4_accessibility.py`, `test_structural_guards.py`).
  - **Complete Configured `tests/web` Suite:** 2168 passed, 80 intentional matrix skips, 0 failures, 1063 warnings in 125.38s (0:02:05).
  - **Static Integrity Checks:** `asset-integrity.sha256` 3/3 OK, `phase-3-visual-freeze-manifest.sha256` 14/14 OK, `compileall` 0 errors, `git diff --check` clean.
- **Stop condition:** Gemini stops at Step 12 boundary for independent Codex review and Peter's Step 12 acceptance decision. Gate P3.G4 remains open; Step 13 remains held.
- **Boundaries unchanged:** No live services, secrets, staging, deployment, production PostgreSQL, or real player data were accessed.
- **Record:** `docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md`.

Update 2026-08-23 (thirty-sixth) — P3.4 Step 12 remediation completed (R12-05 through R12-07).

- **Decision:** Peter Duscha (Acceptance Authority) released Step 12 remediation under
  the accepted remediation release-policy clarification to resolve Codex review findings.
- **Remediations Addressed:**
  - **R12-05 (Enforce exact governed text and exact bounds):** `assert_hostile_renders_inert`
    enforces exact string equality (`assert governed_text == expected_text`), exact length
    bounds (`len(governed_text) == len(expected_text)`), exact Unicode code-point sequence
    matching (`[ord(c) for c in governed_text] == [ord(c) for c in expected_text]`), and
    proves full over-bound strings are never leaked. Formatted assertion diagnostics avoid
    echoing raw hostile payloads. Falsification proves failure on 201/199 len, extra suffix,
    and NFD vs NFC code-point mismatch.
  - **R12-06 (Strict Canonical Single Correlation UUID):** Implemented shared validator
    `validate_exact_canonical_correlation_uuid` in `tests/web/no_js_helpers.py`, reused in
    `test_oauth_refusal_audit.py` and `test_p3_4_security_and_escaping.py`. Rejects duplicate
    elements, uppercase UUIDs, braced UUIDs, URN UUIDs, unhyphenated hex, whitespace, child
    elements, comments, prose wrappers, malformed UUIDs, and internal exception leaks.
  - **R12-07 (Real-Response Falsification & Identity-Display Contract Closure):** Refactored
    probes F-SEC-03, F-SEC-06, F-SEC-07, F-SEC-08, F-SEC-09, and F-SEC-10 to use real ASGI
    response baselines. Added `test_hostile_rendering_identity_subject_display` exercising
    `external_identities.subject` against `code.identity-subject` on `GET /v1/account/identities`.
    Documented identity-display disposition under Phase 3 contract §6.3.
- **Verification Results:**
  - **Dedicated Step 12 Test Suite (`tests/web/test_p3_4_security_and_escaping.py`):** 60 passed, 73 warnings in 5.77s (run 3 times consecutively: 6.19s, 6.07s, 5.77s; all 60 passed).
  - **Six Primary Step 12 Suites:** 271 passed, 0 skipped, 0 failures, 135 warnings in 13.40s (`test_oauth_refusal_audit.py`, `test_security_controls.py`, `test_p3_4_security_and_escaping.py`, `test_p3_4_accessibility.py`, `test_p3_3_disclosure_and_bounds.py`, `test_structural_guards.py`).
  - **Complete Configured `tests/web` Suite:** 2158 passed, 80 intentional matrix skips, 0 failures, 1053 warnings in 126.83s (0:02:06).
  - **Static Integrity Checks:** `asset-integrity.sha256` 3/3 OK, `phase-3-visual-freeze-manifest.sha256` 14/14 OK, `compileall` 0 errors, `git diff --check` clean.
- **Stop condition:** Gemini stops at Step 12 boundary for independent Codex review and Peter's Step 12 acceptance decision. Gate P3.G4 remains open; Step 13 remains held.
- **Boundaries unchanged:** No live services, secrets, staging, deployment, production PostgreSQL, or real player data were accessed.
- **Record:** `docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md`.

Update 2026-08-22 (thirty-fifth) — P3.4 Step 12 remediation completed (R12-01 through R12-04).

- **Decision:** Peter Duscha (Acceptance Authority) released Step 12 remediation under
  the accepted remediation release-policy clarification to resolve Codex review findings.
- **Remediations Addressed:**
  - **R12-01 (Deterministic & Value-Bound Hostile Rendering):** `assert_hostile_renders_inert`
    refactored to require explicit container selector and exact expected cardinality. Evaluates
    Jinja `{{7*7}}` non-evaluation strictly within the governed container rather than scanning
    whole-page text/UUIDs. Non-no-op falsification probes verify failure on injected elements,
    evaluated 49, missing value, wrong container, and over-bound mismatch.
  - **R12-02 (Real Hostile Boundaries & Presentation Surfaces):** Governed real application
    surfaces for character names (R-21 `a.char-title-link`, R-22 `h1.page-title`, R-31
    `a.char-title-link strong`), audit event reasons (R-49 `[data-field="fact-after"]`),
    and reconciliation candidate names (R-43 `[data-field="blocked-name"]`). Bounded over-bound
    10,000-char vectors at real boundaries, proving exact truncation to `ACTOR_NAME_BOUND=120`
    and `AUDIT_VALUE_BOUND=200`. Closed-vocabulary query parameters tested under refusal rules.
  - **R12-03 (Consolidated Shared No-JS Validator):** Moved `FlowContract`, `FormContract`,
    `strip_htmx_attributes`, and `validate_rendered_no_js_fallback` to `tests/web/no_js_helpers.py`,
    shared by both `test_p3_4_accessibility.py` and `test_p3_4_security_and_escaping.py`.
    Inventoried all 9 essential flows with exact action, method, CSRF, and hidden field checks.
  - **R12-04 (Exact Safe-Body Contracts & Truthful Handoff):** Real ASGI body-contract evidence
    and falsification implemented for denial (`denied.html`), validation (`validation.html`, 413/415),
    stale (`degraded.html`), and safe error (`error.html` with canonical correlation UUID). Falsification
    probes honestly numbered F-SEC-01 through F-SEC-10.
- **Verification Results:**
  - **Dedicated Step 12 Test Suite (`tests/web/test_p3_4_security_and_escaping.py`):** 53 passed, 61 warnings in 4.74s (run 3 times independently: 5.19s, 4.67s, 4.74s; all 53 passed).
  - **Five Primary Step 12 Suites:** 237 passed, 0 skipped, 0 failures, 123 warnings in 11.14s (`test_security_controls.py`, `test_p3_4_security_and_escaping.py`, `test_p3_4_accessibility.py`, `test_p3_3_disclosure_and_bounds.py`, `test_structural_guards.py`).
  - **Complete Configured `tests/web` Suite:** 2151 passed, 80 intentional matrix skips, 0 failures, 1041 warnings in 123.34s (0:02:03).
  - **Static Integrity Checks:** `asset-integrity.sha256` 3/3 OK, `phase-3-visual-freeze-manifest.sha256` 14/14 OK, `compileall` (venv-web and venv) 0 errors, `git diff --check` clean.
- **Stop condition:** Gemini stops at Step 12 boundary for independent Codex review and Peter's Step 12 acceptance decision. Gate P3.G4 remains open; Step 13 remains held.
- **Boundaries unchanged:** No live services, secrets, staging, deployment, production PostgreSQL, or real player data were accessed.
- **Record:** `docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md`.

- **Decision:** Peter Duscha (Acceptance Authority) released Step 12 whole-corpus security
  and progressive-enhancement pass. Step 11.3 verification accepted and closed.
- **Implementation & Verification Results:**
  - **Dedicated Step 12 Test Suite (`tests/web/test_p3_4_security_and_escaping.py`):** 54 passed in 4.72s.
  - **Five Primary Step 12 Suites:** 238 passed, 0 skipped, 0 failures, 110 warnings in 10.92s (`test_security_controls.py`, `test_p3_4_security_and_escaping.py`, `test_p3_4_accessibility.py`, `test_p3_3_disclosure_and_bounds.py`, `test_structural_guards.py`).
  - **Complete Configured `tests/web` Suite:** 2152 passed, 80 intentional matrix skips, 0 failures, 1028 warnings in 125.21s (0:02:05).
  - **Static Integrity Checks:** `asset-integrity.sha256` 3/3 OK, `phase-3-visual-freeze-manifest.sha256` 14/14 OK, `compileall` (venv-web and venv) 0 errors, `git diff --check` clean.
- **Evidence Status:**
  - TC-SEC-05 exact security headers (CSP N-26, nosniff, Referrer-Policy, COOP, CORP, Permissions-Policy, Cache-Control: no-store, 0 XFO, 0 CORS) verified across all 10 response families.
  - TC-SEC-08 autoescaping enabled and 0 `|safe` / bypasses verified via AST and token inspection across all 26 production templates.
  - TC-SEC-09 hostile input matrix verified inert and bounded across real presentation surfaces.
  - TC-SEC-10 executable context guards verified across all 26 templates (0 `hx-on:`, 0 `on*`, 0 `javascript:`, 0 inline scripts, 0 remote origins).
  - TC-SEC-11 script context invariants verified across all 26 templates.
  - Safe response bodies verified for denial, validation, stale, and safe errors (0 leaks of stack traces, SQL, paths, or secrets).
  - Essential no-JavaScript flow fallback integrity verified with `hx-*` stripped.
  - Controlled falsification probes F-SEC-01 through F-SEC-10 verified against production validators.
  - Host environment checked via read-only discovery: no browser binary or automation framework installed; browser-driven execution marked honestly as Not Run.
- **Stop condition:** Gemini stops at Step 12 boundary for independent Codex review and Peter's Step 12 acceptance decision. Gate P3.G4 remains open; Step 13 remains held.
- **Boundaries unchanged:** No live services, secrets, staging, deployment, production PostgreSQL, or real player data were accessed.
- Record: `docs/review/phase-3-p3-4-step-12-security-and-progressive-enhancement-handoff.md`.

Status date: 2026-08-22 (thirty-third update: Peter/Acceptance Authority and Codex
accepted P3.4 Step 11.2 final closure. Peter explicitly released Step 11.3
verification-only. Gemini executed the complete 17-suite P3.4 regression surface,
the complete tests/web suite, the bot/domain suite, the Foundry-module suite, and
static integrity checks with zero failures and zero errors. P3.G4 remains open and
Steps 12 and 13 remain held.)

Update 2026-08-22 (thirty-third) — P3.4 Step 11.2 accepted, Step 11.3 verification completed.

- **Decision:** Peter and Codex accepted Step 11.2 (findings R11.2-01 through R11.2-05
  reconciled and verified). Peter released Step 11.3 as verification-only.
- **Verification Results:**
  - **17-Suite P3.4 Regression Surface:** Codex's independently retained result is 798 passed, 26 intentional matrix skips, 0 failures and 626 warnings in 36.04s. Gemini's earlier aggregate record reported the same pass/skip result but 638 warnings in 47.90s; that warning count conflicts with its per-module counts (626), and the original output was not retained sufficiently to resolve the discrepancy. The 47.90s value is the aggregate run time, not a per-module sum.
  - **Complete Configured `tests/web` Suite:** 2098 passed, 80 intentional matrix skips, 0 failures, 980 warnings in 123.93s.
  - **Bot / Domain Suite:** 2294 passed, 0 skipped, 0 failures, 1 warning in 134.74s.
  - **Foundry-Module Node Suite:** 155 passed, 0 skipped, 0 failures in 207.71ms.
  - **Static Integrity Checks:** `asset-integrity.sha256` OK, `phase-3-visual-freeze-manifest.sha256` OK, `compileall` (venv-web and venv) 0 errors, `git diff --check` clean.
- **Evidence Status:** Browser capability discovery confirmed no browser binary or automation framework is installed on host; TC-UI-01/02 remain not run, TC-UI-08 remains held for Peter's real-device inspection, TC-UI-09 remains held for human screen-reader traversal.
- **Stop condition:** Gemini stops at Step 11.3 boundary for independent Codex review and Peter's final Step 11 acceptance decision. Gate P3.G4 remains open; Steps 12 and 13 remain held.
- **Boundaries unchanged:** No live services, secrets, staging, deployment, production PostgreSQL, or real player data were accessed.
- Record: `docs/review/phase-3-p3-4-step-11-3-final-verification-handoff.md`.

Status date: 2026-08-22 (thirty-second update: Peter/Acceptance Authority
explicitly released P3.4 Step 11 after accepting Step 10. Gemini is authorized
to perform the bounded whole-corpus accessibility and responsive pass, then must
stop for independent review.)

Update 2026-08-22 (thirty-second) — P3.4 Step 11 released.

- **Decision:** Peter released Step 11 through his instruction to write its
  implementation prompt. Step 10 remains accepted and closed.
- **Scope:** whole-corpus semantic structure, keyboard operation, visible focus,
  320/768/1280 layouts, 200% reflow, reduced motion, state consistency and
  honest TC-UI-01…TC-UI-06 evidence only.
- **Evidence boundary:** browser automation may run only with an already-installed
  browser; no dependency or browser installation is authorized. TC-UI-07 retains
  its supervised rendered-surface portion, TC-UI-08 remains Peter's real-device
  check, and TC-UI-09 remains real screen-reader traversal. Unavailable evidence
  must be reported as not run, never simulated.
- **Stop condition:** Gemini must stop after Step 11 handoff for independent
  Codex review and Peter's acceptance decision. Step 12 and Step 13 remain held.
- **Boundaries unchanged:** P3.G4, I-06 and A-05 remain open. No staging,
  deployment, public exposure, live-service contact, secret access or real-data
  use is authorized.
- Released prompt: `docs/review/Handover information`.

Status date: 2026-08-22 (thirty-first update: Peter/Acceptance Authority accepted
P3.4 Step 10 after independent Codex re-review found no remaining findings and
the complete PostgreSQL-backed Step 10 surface passed. Step 10 is closed; P3.G4
remains open and Step 11 remains held.)

Update 2026-08-22 (thirty-first) — P3.4 Step 10 accepted.

- **Decision:** Peter accepted P3.4 Step 10 and closed its bounded implementation
  gate. The accepted scope is VM-17/R-47 immutable import receipts and
  VM-18/R-48–R-49 bounded audit search/results.
- **Independent review:** the final Codex re-review found no remaining finding.
  The server-accepted page size is carried through VM-18, pagination assertions
  compare exact parsed query values, fixture teardown proves zero tracked
  PostgreSQL residue across the complete Step 10 synthetic topology, and the
  digest registry separates the previously accepted Step 1–9 corpus from the
  Step 10 review candidate until this recorded decision.
- **Evidence:** focused Step 10/P3.3 audit evidence passed **104 tests with 0
  failures and 0 skips**. The complete 16-suite P3.4 surface through Step 10
  passed **815 tests, 26 intentional matrix skips and 0 failures** against
  disposable PostgreSQL. `compileall` and `git diff --check` passed.
- **Accepted Step 10 template hashes:** `audit_results.html`
  `42883ac57fd38b342cb4471c46f001b549818e07faa7c772d8f2a2df09ba0e38`,
  `audit_search.html`
  `6453c99cd068918be029d7f592b8a934654b11f05e324400ef080d83e878ec23`,
  and `import_result.html`
  `15735d60fdb5a5b3c8435a7ee389af7e6ec027c2f386cdee55f3d109bd42c86e`.
- **Next-step boundary:** this decision accepts Step 10 only. It does not close
  P3.G4, release Step 11, authorize staging or deployment, permit live-service
  contact, or authorize secrets, production data, real snapshots or player
  data. I-06 and A-05 remain open.
- Record:
  `docs/review/phase-3-p3-4-step-10-final-independent-review-and-acceptance.md`.

Status date: 2026-08-21 (thirtieth update: Peter/Acceptance Authority explicitly
released P3.4 Step 10 after accepting Step 9. The preserved Step 10 template
drafts were restored, and Gemini is instructed to complete VM-17/R-47 and
VM-18/R-48–R-49 only, then stop for independent review.)

Update 2026-08-21 (thirtieth) — P3.4 Step 10 released.

- **Decision:** Peter released Step 10. Step 9 remains accepted and closed.
- **Scope:** immutable import receipts and bounded audit search/results only
  (VM-17/R-47 and VM-18/R-48–R-49).
- **Restoration:** the three preserved Step 10 template drafts were restored from
  the dedicated stash; that stash was dropped after successful restoration.
- **Evidence required:** a new PostgreSQL-backed
  `tests/web/test_p3_4_import_and_audit_views.py`, corrected full-page/fragment
  cursor evidence, final template hashes, and independent Codex review.
- **Boundaries unchanged:** Step 10 is released, not accepted. P3.G4, I-06 and
  A-05 remain open. Deployment, public exposure, live-service contact and real
  data remain unauthorized.

Status date: 2026-08-21 (twenty-ninth update: Peter/Acceptance Authority accepted
P3.4 Step 9 after the final independent review closed the R-37, R-42 and R-46
findings and the complete PostgreSQL-backed Step 9 gate passed. Step 9 is closed;
P3.G4 remains open and Step 10 remains held.)

Update 2026-08-21 (twenty-ninth) — P3.4 Step 9 accepted.

- **Decision:** Peter accepted P3.4 Step 9 and closed its bounded implementation
  gate.
- **Evidence:** the complete accepted P3.4 surface through Step 9 passed against
  disposable PostgreSQL: **711 passed, 26 intentional matrix skips, 0 failed**.
  `compileall` and `git diff --check` passed.
- **Findings closed:** R-37 concrete transaction/audit orchestration is at the
  adapter boundary; R-42 admits only the accepted server-minted preview nonce;
  R-46 admits only one canonical preview-job UUID nonce.
- **Step 10 remains held.** Its three in-progress templates are preserved in the
  named Git stash `Preserve in-progress P3.4 Step 10 templates before Step 9
  gate`. This acceptance neither releases nor approves those bytes.
- **Boundaries unchanged:** P3.G4, I-06 and A-05 remain open. No deployment,
  public exposure, live-service contact, secret access or real-player-data use
  is authorized.
- Record:
  `docs/review/phase-3-p3-4-step-09-final-independent-review.md`.

Status date: 2026-08-20 (twenty-eighth update: both required Codex reviews of
the bounded D-03 correction passed with no blocking findings. Peter/Acceptance
Authority accepted the corrected backend contract and explicitly released the
Gemini P3.4 implementation prompt. D-03 is closed; P3.G4, I-06 and A-05 remain
open.)

Update 2026-08-20 (twenty-eighth) — D-03 accepted; Gemini prompt released.

- **Independent reviews passed.** The implementation review and the distinct
  security-focused review found no blocking issue in D-03-1 through D-03-6.
  Review verification and its database-environment limitation are recorded in
  `docs/review/phase-3-d-03-codex-reviews-and-acceptance.md`.
- **Peter accepted the corrected backend contract.** D-03 is **closed** and
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` is explicitly
  **released** for the bounded P3.4 production frontend integration.
- **The remaining gates are unchanged.** P3.G4 is open. I-06 isolated-staging
  evidence and A-05 administrator/WebAuthn readiness remain open. No staging
  exposure, deployment, production use, live-service contact or real-player-data
  use is authorized.
- Records: change-log `C-P3.4-C`; RAID D-03 closed; review and acceptance record
  as linked above.

Status date: 2026-08-20 (twenty-seventh update: the bounded D-03 backend-contract
correction authorized by `C-P3.4-A` is **implemented and submitted for review**.
D-03 remains open, both required reviews are pending, and Gemini's prompt remains
held.)

Update 2026-08-20 (twenty-seventh) — D-03 correction implemented and handed off.

- **All six accepted items are delivered.** `/static/` exists as mount **M-01**
  with `GET`/`HEAD` only, no authentication, trusted-host enforcement,
  kill-switch availability and fingerprint-aware caching, and mounts are now
  inside the closed inventory `TC-STRUCT-01` asserts. `ConfirmScope` (eight
  fields) and `CharacterFilters` (two) are defined in `vm-1`. VM-13's `csrf_token`
  is recorded and its false "Recorded in the P3.2 submission" claim is retracted —
  **without** editing the accepted P3.2 submission to manufacture the provenance.
  R-36's table cell now reads `200` HTML · VM-13 (`denied`), matching §5.1's prose
  and the accepted implementation. **VM-22 `DeniedView`** carries `state` and a
  closed-vocabulary `reason` and nothing else, and replaces VM-02 as the generic
  denial carrier at every portal and import boundary.
- **`VIEW_MODEL_VERSION` remains `vm-1`.** Every view-model change is additive
  under §1 rule 5. No field was removed, renamed or narrowed; no enum was
  narrowed; no versioning conflict arose.
- **No production frontend work.** No template, CSS, HTMX file, image or visual
  asset was created or modified. `denied.html` is byte-identical before and after
  — the new view model fits the template it already had. The static root holds one
  zero-byte `.gitkeep` and nothing else.
- **Evidence.** Portal suite **1524 passed, 80 skipped**; bot suite **2294
  passed**; both exit 0, run serially against the approved disposable database.
  `compileall` and `git diff --check` clean. Prototype freeze **14/14** before and
  after. Falsification demonstrated for the mount inventory guard — where the
  pre-existing route guard is shown to **pass** against an undeclared mount, which
  is the blindness D-03-1 identified — and for the denial leakage guard, where 12
  cases across three modules fail; the tree was restored and verified by SHA-256
  in both cases, and the suites above were run after restoration.
- **Not claimed.** No browser, real-device, screen-reader, staging or production
  evidence. No dependency added, no migration added or run outside the disposable
  test database, no network call, no live service, no `.env` or credential read.
  TC-UI-06 is **not** delivered; TC-SEC-14 asserts only the backend half.
- **Still NO-GO for Gemini.** D-03 is **open**. The independent Codex
  implementation review and the distinct security-focused review are **pending**.
  The implementation prompt remains **held**. P3.G4, I-06 and A-05 remain open;
  deployment, public exposure, live-service contact and real-player-data use
  remain unauthorized.
- **The decision waiting for Peter, after both reviews pass:** accept the
  corrected D-03 backend route/view-model contract and explicitly release
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md`.
- Records: `docs/review/phase-3-d-03-backend-contract-correction-submission.md`;
  change-log `C-P3.4-B`; RAID D-03 amended by addition.

Status date: 2026-08-19 (twenty-sixth update: Peter/Acceptance Authority accepted
`C-P3.4-A` as the bounded D-03 correction authorization. The six corrections now
have explicit dispositions. D-03 remains open pending implementation, independent
Codex implementation review, a distinct security-focused review and Peter's
acceptance of the corrected contract. Gemini's prompt remains held.)

Update 2026-08-19 (twenty-sixth) — D-03 correction decisions accepted.

- Application-served `/static/` is the accepted asset surface, with `GET`/`HEAD`,
  no authentication, trusted-host enforcement, kill-switch availability,
  fingerprint-aware caching and structural coverage of mounts.
- `ConfirmScope` and `CharacterFilters` receive the accepted implemented shapes;
  VM-13's CSRF field and R-36's `200` denied response are recorded accurately.
- A dedicated minimal `DeniedView` is required while byte-identical object-denial
  and absent-object `404` responses remain invariant.
- Claude/backend may implement only these bounded corrections. They require an
  independent Codex implementation review and a distinct security-focused review.
- **Still NO-GO for Gemini:** D-03 is not closed and the implementation prompt is
  not released. P3.G4, I-06 and A-05 remain open; deployment, public exposure,
  live-service contact and real-player-data use remain unauthorized.

Status date: 2026-08-19 (twenty-fifth update: the P3.4 implementation handover is
prepared. The accepted P3.1–P3.3 tree was revalidated against the frozen route and
view-model contracts and shows no drift; six remaining backend-contract items are
presented for the D-03 decision as change-log `C-P3.4-A`, which is **proposed, not
accepted**. P3.4 production frontend implementation remains **NO-GO** until Peter
records the D-03 disposition and explicitly releases the prepared Gemini prompt.)

Update 2026-08-19 (twenty-fifth) — P3.4 handover prepared; D-03 decision requested.

- **Revalidated, no drift.** The registered route inventory equals the accepted
  contract exactly (39 = 39, `DEFERRED_ROUTES` empty); the implemented view-model
  set equals the documented `vm-1` set (21 = 21, `DEFERRED_VIEW_MODELS` empty); no
  view-model field is missing, renamed or removed; the absence controls hold; and
  the 24 current templates carry zero `|safe`, zero `hx-on:`, zero inline script,
  zero `design-prototype/` references and zero remote origins.
- **D-03 is not closable on the existing gate record.** `C-P3.3-K` and `C-P3.3-L`
  both restate it as in force, and both were decided after P3.G2 closed and
  alongside the P3.G3 closure. Six concrete items remain; D-03-1 (no accepted
  static-asset surface) and D-03-2 (`ConfirmScope` undefined in `vm-1`) block a
  faithful P3.4 implementation.
- **Deliverables.** `docs/review/phase-3-p3-4-gemini-readiness-report.md` gains a
  dated addendum (§§A1–A10) preserving its historical 2026-08-14 NO-GO analysis;
  `docs/review/phase-3-p3-4-gemini-implementation-prompt.md` is written and
  **held**, released only by Peter's explicit decision.
- **Unchanged boundaries.** No deployment, public exposure, live-service contact
  or live-data use is authorized. I-06 requires isolated staging; A-05 remains an
  exposure prerequisite; P3.G4 is open and only Peter can close it.
- **Verification.** Visual freeze 14/14 before and after; `git diff --check`
  clean. No migration, live service, network call, browser, package installation
  or real player/Actor/guild data was used.

Status date: 2026-08-19 (twenty-fourth update: Peter/Acceptance Authority accepted
the recommended post-gate sequence. P3.4 development may begin; deployment and
public exposure remain unauthorized; I-06 will be addressed through isolated
staging; A-05 remains an exposure prerequisite; and D-03 must close before Gemini
production integration. Recorded as `C-P3.3-L`.)

Update 2026-08-19 (twenty-fourth) — post-gate sequencing decision.

- Begin P3.4 development under the approved plan and its review gates.
- Do not deploy or expose the service publicly under this authorization.
- Build isolated staging and produce the real I-06 evidence there.
- Complete A-05 with a protected administrator account and two independent real
  WebAuthn credentials before exposure.
- Close D-03 on a frozen backend route/view-model contract before Gemini
  production integration.
- Require a later explicit deployment/exposure decision.

Status date: 2026-08-19 (twenty-third update: Peter/Acceptance Authority closed
P3.G3 and authorized P3.4. P3.3 is accepted after the independent implementation
review, distinct security-focused review, acceptance of `C-P3.3-I`, and the
decisions recorded in `C-P3.3-J`. I-06 and A-05 remain open and continue to block
public staging/production exposure; this gate decision authorizes development,
not deployment.)

Update 2026-08-19 (twenty-third) — P3.G3 gate decision.

- **Decision:** Peter/Acceptance Authority accepted P3.3, closed stop gate
  **P3.G3**, and authorized **P3.4** to begin.
- **Basis:** all P3.3 maintainer decisions are recorded; the sixth correction
  passed independent implementation and distinct security-focused reviews; and
  `C-P3.3-I` is accepted.
- **Boundaries unchanged:** I-06 staging/browser/performance evidence and A-05
  protected-administrator/WebAuthn readiness remain open. No public exposure,
  deployment, production contact or live-data use is authorized by this gate.
- **Later gate unchanged:** D-03's backend route/view-model approval continues to
  govern later Gemini production integration.

Status date: 2026-08-19 (twenty-second update: the distinct security-focused
re-review of `C-P3.3-I` found no blocking or major security finding. The complete
rollback module and structural/rejected-scope guards passed, 120 tests total.
Peter/Acceptance Authority accepted `C-P3.3-I`. P3.G3 remains open for its
separate explicit gate decision, and P3.4 has not begun.)

Update 2026-08-19 (twenty-second) — `C-P3.3-I` accepted.

- **Security review passed.** The test-scoped backend termination is restricted
  to the holder identity captured as PID plus `backend_start`, uses bound SQL
  parameters, and is unreachable from production code.
- **Ownership accepted.** The holder is detached before threaded cleanup;
  orphaned calls are recorded and fail the case rather than being hidden.
- **Verification:** 120 passed in 23.16s across the rollback-boundary module,
  structural guards and rejected-scope controls.
- **Decision:** Peter/Acceptance Authority accepted `C-P3.3-I` on 2026-08-19.
  This does not separately accept defective `C-P3.3-H`.
- **Gate unchanged pending explicit decision:** P3.G3 remains open and P3.4 is
  not yet authorized.

Status date: 2026-08-19 (twenty-first update: Peter/Acceptance Authority accepted
the outstanding P3.3 product and operational decisions: D-09's rollback boundary;
I-11's `snapshot_folder_selections`; the narrow R-41/SM-05 exception; the §13
effect-publication recovery amendment; and derived limits 20, 3 and 10,000.
Recorded as `C-P3.3-J`. P3.G3 remains open for the distinct security-focused
review, and P3.4 has not begun.)

Update 2026-08-19 (twenty-first) — Acceptance Authority decisions.

- **D-09 accepted.** While a retained job records a committed apply effect,
  rollback is application rollback or roll-forward rather than schema downgrade
  below `0013`; the boundary reopens under the documented N-24 conditions.
- **I-11 accepted.** `snapshot_folder_selections` is the authoritative mutable,
  versioned current selection; append-only audit events retain its history.
- **R-41/SM-05 accepted.** A completed preview may become `stale` only while no
  apply names it. Completed applies and referenced previews remain immutable.
- **Section 13 accepted.** Effect-publication recovery is ratified with
  `EFFECT_RECOVERY_LIMIT = 20`, `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3`, and
  retention `MAX_LIMIT = 10 000`.
- **Gate unchanged.** This is not acceptance of `C-P3.3-I` or closure of P3.G3;
  the separate security-focused review remains required.

Status date: 2026-08-19 (twentieth update: the independent review of the fifth migration-rollback correction **did not accept** it — its ceiling counted only the subprocess reap and the writer join, while the same release also called `holding.rollback()` and `holder.close()` synchronously with no enforceable timeout, so a blocked rollback prevented the close and the writer join and a blocked close prevented the join, leaving the `alembic_version` row lock live in the shared disposable database. Every database cleanup call is now made on a thread of its own with a bounded wait, the holder is detached from its pool before anything can block it, an orphaned thread is recorded and reported rather than hidden, a new step disposes of the holder's backend independently, and the ceiling now counts all six waits. Three new deterministic cases and three mutation runs prove it. **No production change.** **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (twentieth) — P3.3 sixth migration-rollback correction.
Recorded in section 19 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One major finding, no blocking defect, and no production change.** The
  migration's DDL, guard, emitted SQL, constraints, grants, application statements
  and worker statements are byte-for-byte what the fifth correction left. `0011`,
  `0012`, `0013` and `migrations/env.py` were not edited, verified by SHA-256, and
  `docs/operations/web-portal.md` is unchanged. The diff is one test module's
  cleanup and four new cases, plus controlled-document wording.
- **The fifth correction is *not* accepted.** `C-P3.3-H` remains open. What it got
  right is retained and rerun — the bounded subprocess reap, the release order, the
  `add_note()` behaviour and TC-MIG-38…TC-MIG-41 — and its ceiling claim is
  corrected here rather than rewritten as though it had been right.
- **F1 — the 25-second ceiling omitted the two database calls.**
  `_HeldLockCleanup.release()` also called `holding.rollback()` and
  `holder.close()` synchronously, and neither SQLAlchemy nor psycopg offers an
  enforceable timeout for either. Catching an exception does not bound an
  operation that never returns. A blocked rollback meant the close, and a blocked
  close meant the writer join, were never reached at all — and the resource at
  stake is the externally taken `alembic_version` row lock in the **shared**
  disposable `freedom_test` database, so one stuck cleanup could have produced a
  page of unrelated failures in later cases. **Recorded as an unbounded
  failure-path cleanup defect, not a flake**: neither branch is reachable from
  healthy PostgreSQL, which is precisely why the fifth correction's real-database
  case and its instant fake transaction and connection falsified neither.
- **The correction, and its cost stated rather than hidden.** Each database call
  is made by a daemon thread of its own and it is the **wait** that is bounded,
  because that is the only part a test can control. A call that never returns
  therefore leaves that thread alive — so it is recorded on the cleanup, reported
  as a problem, and never followed by anything that touches what it owns. The
  holder is **detached from its pool at construction**, while only the calling
  thread can be inside it, so no orphaned thread can leave a usable pooled
  connection for a later case, on any path. Because a stuck connection object is
  off limits, a new step disposes of the **backend** from a different connection —
  `pg_terminate_backend()` on the test's own backend, matched on pid *and*
  `backend_start` — which releases the row lock and lets the stuck call return.
  The release runs six steps, records each before entering it, and runs every
  later one regardless of what an earlier one did.
- **The ceiling now counts every wait it performs:** `2 × 5 + 2 × 5 + 5 + 15 =
  40 s`, against the 60-second production-test ceiling, and calculation,
  documentation and tests agree.
- **Proved, not asserted.** TC-MIG-42 and TC-MIG-43 drive the rollback-blocked and
  close-blocked paths with deterministic stand-ins that block exactly where the
  real calls would and record the thread they were called on; TC-MIG-44 is the
  passing-path mirror for both. Each proves the release returns inside its complete
  ceiling and well inside the stand-in's period, reports the blocked step, attempts
  every later step, sets the writer's commit event and joins it, preserves the
  assertion under diagnosis, and accounts for the helper thread it left.
- **Falsified deterministically, three times, without hanging.** An unbounded
  direct `rollback()` fails exactly the two rollback cases (11.31s); an unbounded
  direct `close()` fails exactly the two close cases (11.54s); and the fifth
  correction's `communicate()` mutation is retained and reproduces the same four
  failures (10.52s). All were restored by checksum and none is in the final tree.
- **`_RecordingChild` stays an informal technical concurrence** — Peter's
  direction, applied here: no numbered RAID decision, no change-log decision entry
  of its own, and its existing localized documentation is sufficient.
- **Nothing else changed and nothing is weakened.** No identity assertion,
  queue-fairness assertion, migration, production statement, production pause
  hook, production timeout policy, marker, sidecar, tombstone, retention rule,
  runtime grant or hidden schema object was touched, and no test was relaxed,
  skipped, deleted or renamed away.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, `C-P3.3-F`, `C-P3.3-G`, `C-P3.3-H`, **`C-P3.3-I` new**), and Peter's
  two unchanged decisions: **RAID I-11** (`snapshot_folder_selections`) and the
  **R-41 / SM-05 controlled-contract amendment**.
- **I-06 and A-05 are unchanged and still open.**


Status date at that update: 2026-08-19 (nineteenth update: the independent review of the fourth migration-rollback correction accepted the writer-identity remediation as sound and reran the rollback module against disposable PostgreSQL, and found one major defect — TC-MIG-37's failure-path cleanup killed a surviving migration subprocess and then collected it with an unbounded `communicate()`, so a stall could hang cleanup before the `alembic_version` row lock, the holder connection and the fence writer were released. Cleanup is now one ordered, bounded release owned by a test-local object, it reports rather than replaces the assertion under diagnosis, and four new deterministic cases prove it. **No production change.** **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (nineteenth) — P3.3 fifth migration-rollback correction.
Recorded in section 18 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One major finding, no blocking defect, and no production change.** The
  migration's DDL, guard, emitted SQL, constraints, grants, application statements
  and worker statements are byte-for-byte what the fourth correction left. `0011`,
  `0012`, `0013` and `migrations/env.py` were not edited. The diff is one test
  module's cleanup and four new cases, plus controlled-document wording.
- **The fourth correction's writer-identity result stands accepted as sound.**
  The reviewer confirmed the observed request is restricted to the announced
  writer pid, matched to the production `hold_for_effect` statement, and tied
  through `pid`, `virtualtransaction`, `backend_xid` and `xact_start` to the
  transaction that later commits, and that the recorded falsification checksum
  matches the current file. Their two passing runs are **historical**: a passing
  happy path is not evidence about failure cleanup.
- **F1 — TC-MIG-37 had an unbounded subprocess reap on failure.** Its `finally`
  block killed a surviving migration child and then called
  `migration.communicate()` with no timeout, so a stall in termination or pipe
  collection could hang cleanup indefinitely — before the externally held
  `alembic_version` row lock was rolled back, before the holder was closed and
  before the writer was joined. **Recorded as an unbounded failure-path cleanup
  defect, not a flake**: the passing case never executes that path.
- **The correction.** One test-local object owns every resource the case holds and
  runs a single ordered release on every exit path: release the writer's commit
  event first; end and boundedly reap a surviving migration child **before** the
  row lock is released, so a migration that is *released* rather than *ended*
  cannot commit its drops and a writer queued behind its table lock is freed; roll
  back the row lock; close the holder; then join the writer, bounded, and only if
  it was started and is still alive. The reap kills and collects with an explicit
  timeout, twice, and never waits without one; a child surviving both is reported
  and stepped over rather than stranding the resources that are still releasable.
  The release **never raises** — its problems are attached to the failing
  assertion with `add_note()`, so the primary failure stays diagnosable while
  cleanup failures are still reported. The same bounded reap replaces the
  identical unbounded shape in the module's three sibling concurrency cases.
- **Proved, not asserted.** TC-MIG-38 drives a **controlled** assertion failure
  against real PostgreSQL — the production revision, the production fence
  statement, the real Alembic child and the real writer all live — at two named
  points, and measures the release from the moment of failure: bounded, child
  reaped, writer and holder released, and no matching lock or activity left in
  `pg_locks`/`pg_stat_activity`. TC-MIG-39…TC-MIG-41 cover the timeout, pre-start
  and error-preservation branches deterministically.
- **Falsified deterministically, including by the real PostgreSQL case.** Against
  the pre-fix `kill(); communicate()` shape four of the five new cases fail in
  under ten seconds and without hanging: **both** TC-MIG-38 parameters — the
  surviving child collected with `timeout=None`, and the already-exited child not
  collected at all — plus TC-MIG-39 and TC-MIG-41. The bound is asserted at the
  *call*, because `SIGKILL` collects a real Alembic child immediately and an
  unbounded collection returns at once, so no timing assertion could see it. The
  mutation was restored by checksum and is not in the final tree.
- **Nothing else changed and nothing is weakened.** No identity assertion, queue-
  fairness assertion, migration, production statement, production pause hook,
  marker, sidecar, tombstone, retention rule or hidden schema object was touched.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, `C-P3.3-F`, `C-P3.3-G`, **`C-P3.3-H` new**), and Peter's two
  unchanged decisions: **RAID I-11** (`snapshot_folder_selections`) and the
  **R-41 / SM-05 controlled-contract amendment**.
- **I-06 and A-05 are unchanged and still open.**


Status date at that update: 2026-08-19 (eighteenth update: the independent review of the third migration-rollback correction confirmed the controlled-document correction and the exact rollback-module count, and found one major defect — the new held-lock regression did not identify the ungranted lock it asserted on as belonging to its own fence writer. The assertion is now bound to the writer's announced backend pid and to its re-observed transaction identity, and is falsified deterministically against an unrelated queued session. **No production change.** **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (eighteenth) — P3.3 fourth migration-rollback correction.
Recorded in section 17 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One major finding, no blocking defect, and no production change.** The
  migration's DDL, guard, emitted SQL, constraints, grants, application statements
  and worker statements are byte-for-byte what the third correction left. The diff
  is one test case's identity assertions and controlled-document wording.
- **F1 — TC-MIG-37 did not identify its ungranted lock as the test writer.** It
  polled every ungranted `RowExclusiveLock` on `reconciliation_jobs` and asserted
  only that the migration holder's pid was absent, so an unrelated queued session
  could satisfy it while the intended writer was still awaiting scheduling, opening
  its connection or inside `seed_import()`. **This is recorded as a defective
  assertion, not as a timing flake**: it passed because the disposable database is
  quiet enough that the intended writer normally wins the race, which is precisely
  why a passing run was not evidence.
- **The correction.** The writer announces its PostgreSQL backend pid over a
  bounded queue, from inside its own transaction and before any production
  statement. The poll is scoped `AND l.pid = :pid`, and additionally requires
  `pg_stat_activity.query` for that pid to be the production `hold_for_effect`
  fence — matched by statement shape, not by driver placeholder spelling — rather
  than `seed_import`, connection setup or an unrelated statement. The transaction
  identity seen while the request is queued (`pid`, `virtualtransaction`,
  `backend_xid`, `xact_start`) is re-observed, still open and uncommitted, on the
  transaction that then commits the fence, so the queued request and the committing
  transaction are proved to be one — not inferred from thread liveness. The
  migration holder and the fence writer are named separately throughout. **No
  production pause hook, no revision change, no change to emitted SQL, no sleep
  used as proof, no unbounded wait.**
- **Falsified deterministically.** With the writer held on an event before its
  fence and only an unrelated session queued for the same mode on the same
  relation, the old broad predicate is satisfied — and its one identity assertion
  still holds — while the corrected predicate cannot be, and the case fails. The
  mutation was restored by checksum and is not in the final tree.
- **The queue-fairness case is not weakened.** TC-MIG-32 keeps every assertion and
  its deliberately broader observation, which proves a different condition; a
  narrowly named helper was added rather than the shared one being repurposed.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, `C-P3.3-F`, **`C-P3.3-G` new**), and Peter's two unchanged decisions:
  **RAID I-11** (`snapshot_folder_selections`) and the **R-41 / SM-05
  controlled-contract amendment**.
- **I-06 and A-05 are unchanged and still open.** No marker, sidecar, tombstone,
  retention-policy change, production pause hook or hidden schema object was added.


Status date at that update: 2026-08-19 (seventeenth update: the independent review of the second migration-rollback remediation found three major defects and no new blocking defect. The controlled documents now state the retention-aware predicate consistently, the held-lock exclusion is proved from a **granted** `AccessExclusiveLock` by a new regression, the mis-named queue-fairness case is renamed to what it proves, and every required command is rerun against the final tree with internally consistent counts. **Re-submitted** for independent implementation review and a distinct security-focused review; P3.G3 remains open and P3.4 has not begun)

Update 2026-08-19 (seventeenth) — P3.3 third migration-rollback correction.
Recorded in section 16 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **No blocking defect this round, and no production change.** The migration's
  DDL, guard, emitted SQL, constraints, grants, application statements and worker
  statements are byte-for-byte what the second remediation left. The diff is one
  new test case, one renamed and re-scoped test case, two test-cleanup
  corrections, and controlled-document wording.
- **F1 — the controlled documents still stated the superseded boundary.** The
  predicate had been corrected in the migration and the runbook headline, and
  left standing as present-tense prose in the submission's answers, the
  logical-schema constraint note, the SM-05 subsection, this status record, RAID
  `I-18` and `RR-19`, the `C-P3.3-D` amendment bullet and the rollback-boundary
  test module. Every one of those now states: **downgrade below 0013 is refused
  while any *retained* reconciliation job records a committed effect, and becomes
  available only when no such job exists** — with the four database states
  (never-applied; retained completed; retained committed-but-unpublished, which
  no age makes retention-eligible; and retention-emptied with `snapshot_imports`
  and audit history preserved) distinguished wherever the rule is stated.
  Historical wording survives only where it is labelled superseded and paired
  with the corrected rule. **Retention is not a rollback technique**, and manual
  deletion, truncation, a shortened period and an early sweep are named as
  unsupported in the runbook.
- **F2 — the mandatory concurrency regression proved the wrong condition.** The
  case named `…a_fence_writer_arriving_after_the_lock_cannot_commit_until_it_finishes`
  held the migration's lock request **ungranted** throughout, so it established
  PostgreSQL lock-queue fairness, not the named condition. It is renamed
  `…arriving_behind_a_pending_lock_request_cannot_overtake_it` and kept as
  coverage of what it does prove (TC-MIG-32). **TC-MIG-37 is new** and proves the
  held-lock condition from observable state: a **granted** `AccessExclusiveLock`
  held by the production downgrade transaction, unchanged pid/`virtualtransaction`/
  `xact_start` across the writer's arrival, the production fence's `ROW
  EXCLUSIVE` request observed ungranted with nothing committed, the migration
  transaction ending, and only then the fence committing. The migration is held
  after the grant by locking Alembic's own `alembic_version` row from the test —
  **no production pause hook, no revision change, no change to emitted SQL, no
  sleep used as proof**.
- **F3 — the completion report contained impossible counts.** §15.4 reported 17
  passed for the rollback module alone and 15 passed for that module plus
  `test_migration_0013_round_trip.py`. Every required command is rerun against
  the final corrected tree and reported with its literal invocation and exact
  count; pre-fix results are kept and labelled historical.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, ratification
  of the retention-aware rollback policy (**D-09**, change-log `C-P3.3-D`,
  `C-P3.3-E`, **`C-P3.3-F` new**), and Peter's two unchanged decisions: **RAID
  I-11** (`snapshot_folder_selections`) and the **R-41 / SM-05 controlled-contract
  amendment**.
- **I-06 and A-05 are unchanged and still open.** No marker, sidecar, tombstone,
  retention-policy change, production pause hook or hidden schema object was
  added.


Update 2026-08-18 (fifteenth) — P3.3 migration-rollback remediation. Recorded in
section 14 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **One blocking finding, fixed and regression-tested against real PostgreSQL:
  migration `0013` could not round-trip a database that had processed a normal
  apply.** The commit fence writes `effect_result` inside the effect's own
  transaction and a check constraint makes the pair inseparable, so
  `downgrade 0012` — which correctly keeps `effect_committed_at`, that being
  `0012`'s column — destroyed the payload `upgrade 0013` then demanded back. Every
  truthfully completed apply failed the re-upgrade guard, and the database was
  **stranded one revision below head** with no permitted remedy. The rollback
  evidence the previous submission cited exercised only an **empty** schema.
- **The fix is a refusal, not a weakening.** `downgrade()` now counts the
  committed effects **before it changes anything** and refuses, naming the
  `completed` and committed-but-unpublished populations separately and the
  operator's action. Offline (`--sql`) scripts carry the same guard as executable
  SQL rather than a comment. **No constraint weakened, no invariant amended, no
  history deleted, no grant changed, no application or worker statement touched**
  — and `alembic check` still reports no metadata difference.
- **The evidence is now classified so neither class can be read as the other.**
  `test_migration_0013_round_trip.py` is retained and relabelled as empty-schema
  evidence; `test_migration_0013_rollback_boundary.py` is new and data-bearing,
  with every committed effect produced by the production apply path.
  TC-MIG-24…TC-MIG-30. All failed against the pre-remediation migration first.
- **One operational-contract amendment is proposed, not self-approved:** while
  any **retained** reconciliation job records a committed apply effect, rolling
  P3.3 back is application rollback or roll-forward rather than schema
  downgrade; the boundary reopens once no such job survives — either because no
  apply has committed, or because approved N-24 retention has removed every
  completed committed-effect job and its result and no committed-but-unpublished
  job remains. (Wording corrected 2026-08-19; the earlier "past the first
  committed apply effect" phrasing described a historical event the guard does
  not record, and retention is not a rollback technique.) Change-log `C-P3.3-D`, RAID **D-09**,
  runbook `docs/operations/web-portal.md` §3.6. The refusal itself is implemented
  because it is correct under either policy.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, D-09, and
  Peter's two unchanged decisions: **RAID I-11** (`snapshot_folder_selections`)
  and the **R-41 / SM-05 controlled-contract amendment**. New RAID rows: **I-18
  closed**, **RR-19** recorded, **D-09** open.
- **I-06 and A-05 are unchanged and still open.**

Update 2026-08-18 (fourteenth) — P3.3 effect-publication remediation. Recorded in
section 13 of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **Two blocking findings against the previous remediation, both fixed and both
  regression-tested against real PostgreSQL.** Both were cases where a job could
  still deny an import the database was holding.
  1. **A committed effect could be cancelled after reaping.** Only the `running`
     branch of R-45's cancel statement carried the fence predicate, and the reaper
     deliberately requeued a job whose effect had committed but whose result had
     not been published. Both branches now carry it, so do `fail`,
     `cancel_under_lease` and `mark_stale_under_lease`, and migration `0013` adds
     `CHECK (effect_committed_at IS NULL OR state NOT IN ('failed','cancelled',
     'stale'))` — so the row is refused whatever statement writes it, including
     direct runtime-role SQL. The route answers the truthful `409`
     (`already_applied`) and **writes no audit event claiming a cancellation was
     requested**.
  2. **A committed effect could become `failed` on attempt three.** Neither reaper
     branch can describe a committed effect. The commit fence now stores the
     bounded result the run produced, in the same statement as
     `effect_committed_at`, and an explicit **effect-publication recovery** takes
     the expired lease instead: one transaction under the job row's write lock
     reads that payload and the immutable `snapshot_imports` receipt, inserts the
     result, completes the job and records the completion event. No artifact is
     re-parsed, no authority re-resolved, no lease minted and `attempts` is
     untouched, so **N-43 is neither spent nor disguised**.
- **RR-16 is withdrawn, not carried.** The previous remediation recorded finding
  2's condition as an accepted residual risk. The reviewer refused it as one, and
  was right to; it is now RAID **I-17, closed**.
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, and Peter's
  two unchanged decisions: **RAID I-11** (`snapshot_folder_selections`) and the
  **R-41 / SM-05 controlled-contract amendment**.
- **One further contract amendment is proposed, not self-approved**, and it is
  larger than the last: SM-05 gains **one transition** (`running → completed`,
  performed by the recovery pass), three forbidden transitions, one column and two
  check constraints. **No state is added** — a seventh state `recovering` was
  considered and rejected — and no accepted numeric value changes. Recorded as
  change-log `C-P3.3-C` for Peter, alongside one new derived constant
  (`EFFECT_RECOVERY_LIMIT = 20`) and one new residual risk (**RR-18**).
- **I-06 and A-05 are unchanged and still open.**

Update 2026-08-18 (thirteenth) — P3.3 remediation. Recorded in the dated
remediation section of
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **Two blocking findings, both fixed and both regression-tested.**
  1. **The import effect was not fenced.** `SnapshotImportService.apply` committed
     the import, characters, mappings and success audit in one transaction, and
     the worker published the job's terminal state in a *second* one. In between,
     a cancellation, a timeout self-abandon, a kill-switch self-abandon or a
     reaper requeue could transition the job while the abandoned execution thread
     went on to commit real state — so a job could say `cancelled`, `queued`,
     `stale` or `failed` over a durable import. Migration `0012` adds
     `reconciliation_jobs.effect_committed_at`, written **inside the effect's own
     transaction** by a commit fence whose row lock serialises against all three
     writers. Seven race cases (TC-JOB-17…23) assert the actual import,
     character, mapping and audit rows, not a runtime return string.
  2. **The N-24 retention command could not run.** Its
     `UPDATE reconciliation_jobs SET result_id = NULL` violated
     `CHECK ((state = 'completed') = (result_id IS NOT NULL))` for every completed
     job, and it ignored the `parent_job_id … RESTRICT` graph. It is rewritten as
     one bounded atomic operation with a fixed-point retained-graph rule, and
     covered by twelve real-PostgreSQL cases (TC-OPS-06…17).
- **Nothing is accepted.** P3.G3 remains open pending the independent
  implementation re-review, the distinct security-focused re-review, and Peter's
  two decisions: **RAID I-11** (`snapshot_folder_selections`) and the **R-41 /
  SM-05 controlled-contract amendment** for the completed-unconfirmed-preview →
  `stale` exception.
- **One contract amendment is proposed, not self-approved.** SM-05's
  "cancelling a committed apply" mechanism cell described something the code did
  not do; it is corrected to name the fence. No state, transition or accepted
  numeric value changes. Recorded as change-log `C-P3.3-A` for Peter.
- **I-06 and A-05 are unchanged and still open.**

Update 2026-08-18 (twelfth) — P3.3 submitted. Recorded in
[`../review/phase-3-p3-3-submission.md`](../review/phase-3-p3-3-submission.md).

- **Starting authority.** P3.G2 was accepted on 2026-08-18 by change-log entry
  `C-P3.2-D`. That decision authorized P3.3 to begin and accepted no later gate.
- **Delivered.** The closed R-40…R-49 surface; migration `0011` and its three
  tables; the durable six-state job model of SM-05 with `FOR UPDATE SKIP LOCKED`
  claiming, per-claim lease fencing, the two-branch reaper and the worker
  self-abandon that shares it; a separate `freedom-worker` process and its
  systemd unit; bounded audit search; VM-14/15/17/18; the N-24 retention command;
  and the retirement of the inert Phase 2 preview endpoint.
- **Nothing here is accepted.** P3.3 is **submitted**. Its gate P3.G3 is open,
  and P3.4 has not started.
- **Three findings raised rather than resolved silently**, and one of them needs
  a maintainer decision: **RAID I-11** — the accepted schema names no table for
  the administrator's folder selection and the table it would belong to is
  append-only, so P3.3 added `snapshot_folder_selections` on the precedent P3.2
  set. **I-12** and **I-13** are closed by the package: S-11 is now
  process-aware in both directions, and a portal-applied import records the
  stable platform account rather than only a Discord snowflake.
- **I-06 stays open and is widened.** TC-PERF-02 — *measure a real-folder apply
  end to end* — has **never been measured at all**, and P3.3 delivers the job
  model that measurement needs without simulating the measurement. TC-PERF-01,
  TC-PERF-03, TC-LIM-02, TC-SEC-07's browser half and TC-OPS-01…05 remain unrun
  because staging does not exist.
- **A-05 stays open.** No public staging or production exposure is authorized
  until the protected administrator account and two real WebAuthn credentials are
  established and attested by Operations.


Update 2026-08-16 (eleventh, later the same day) — P3.G1 gate decision. The
complete independent implementation and distinct security-focused re-review is
recorded in
[`../review/phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md`](../review/phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md).

- **Review outcome:** no remaining blocking or important implementation or
  security finding. Fresh evidence: **712 portal tests** and **2260 bot tests**,
  no failures and no skips; changed Python modules compile; `git diff --check` is
  clean.
- **Decision:** Peter Duscha accepted P3.1 and closed stop gate **P3.G1** on
  2026-08-16. RAID I-07, I-09 and I-10 are closed. **P3.2 is authorized to
  begin.** P3.3 remains behind P3.G2 and is not authorized by this decision.
- **TC-BG-16 wording corrected:** enrolled and invented credential IDs produce
  the same externally meaningful outcomes — statuses and coarse error codes at
  the same attempts under the same configured window. Literal body equality is
  not claimed because correlation identifiers intentionally differ; literal
  `Retry-After` equality is timing-dependent and is not claimed.
- **I-06 remains open.** No staging environment exists, so TC-LIM-02,
  TC-SEC-07's browser half, TC-OPS-01…05 and TC-PERF-01…03 remain unrun. This
  does not block P3.2; it blocks staging/production exposure and final Phase 3
  production-readiness acceptance until the owning checks pass.
- **A-05 remains open.** The enrollment mechanism is accepted, but two real
  WebAuthn credentials have not been validated on a deployment host. This does
  not block P3.2; it blocks public staging/production exposure until the
  Operations Owner validates the prerequisite.


Update 2026-08-16 (tenth, later the same day) — appended, not rewritten. This one
records the **distinct security-focused review** and its remediation. Recorded in
[`../review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md),
against
[`../review/phase-3-p3-g1-security-review-2026-08-16.md`](../review/phase-3-p3-g1-security-review-2026-08-16.md).

- **Two blocking findings, both accepted.** N-32 requires a per-address **and** a
  per-account WebAuthn assertion budget; the second was implemented, validated and
  unit-tested, and **no production call site invoked it**, so attempts spread over
  fresh source addresses were bounded only per address. N-33 requires a per-address
  **and** a per-grant recovery budget; the second was incremented inside the
  redemption transaction, which every refusal rolls back, so an attempt matching a
  real but expired, invalidated or consumed grant counted for nothing and the cap
  could be walked past from new addresses.
- **The suite reported on the mechanisms, not on a request.** The account budget's
  only caller was a test calling it directly, and the per-grant case presented a
  token matching no grant row and asserted the stored count stayed **zero** — an
  assertion the defect satisfies perfectly. That case has been renamed and
  re-scoped to the property it really held rather than deleted.
- **One rule, applied twice.** An attempt counter must be spent in a transaction
  that commits whether or not the attempt succeeds. Both budgets are now consumed
  in their own committed transactions before the unit of work they bound — beside
  `_consume_rate_limit()`, which has always worked this way — with the account
  budget charged after the presented credential is resolved and before anything is
  verified, and the per-grant attempt charged through a service method that
  **returns** its refusal instead of raising it.
- **The limit is not an oracle.** A credential id that resolves to no account
  spends an equivalent keyed per-credential budget, so an enrolled credential and
  an invented one are refused at the same attempt with the same externally
  meaningful status and coarse error code. Correlation identifiers intentionally
  differ, and literal retry-hint equality is not claimed.
- **Evidence.** TC-BG-16 and TC-BG-17 added by addition, both direct HTTP against
  real PostgreSQL and both spending their budget from several source addresses;
  **712 portal and 2260 bot tests pass with no failures and no skips**, run
  serially against the guarded disposable database; four falsification mutations
  killed, including one that reintroduces the original rollback mechanism at the
  new boundary, every mutation reverted and verified byte-for-byte. **No accepted
  value, environment variable, route, schema, migration, dependency, deployment
  value or visual asset changed.**
- **Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain open; P3.2
  and P3.3 have not started, and the security review's outcome stands until an
  independent security re-review says otherwise.


Update 2026-08-16 (ninth, later the same day) — appended, not rewritten. This one
**corrects the lifecycle contract recorded as complete by the third update**,
found by fresh independent implementation re-review
(`../review/Handover information`). Recorded in
[`../review/phase-3-p3-g1-composition-lifecycle-claim-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-composition-lifecycle-claim-remediation-submission-2026-08-16.md).

- **The cleanup was right; nothing guarded the way in.** `WebComposition.aclose()`
  is permanent — it closes the provider's HTTP client and disposes an owned engine
  — and the ASGI lifespan performed no live-or-closed check before running the
  startup checks and yielding. A composition passed to two applications, or one
  application whose lifespan was entered again, answered
  `lifespan.startup.complete` and began serving with a closed Discord client behind
  R-03 and R-04. The first failure would have been an OAuth request, not a startup.
- **The resource checks were never going to catch it.** They never receive the
  provider, and `Engine.dispose()` does not invalidate an engine — it discards the
  pool and lets the next checkout build a replacement — so S-14 would have
  connected successfully and reported health for resources nobody may use.
- **The suite required the unsafe outcome.** The repeated-shutdown case entered a
  second lifespan over a closed composition and asserted
  `lifespan.startup.complete` from it, under the name of idempotency. That is not a
  repeated *shutdown*; it is a new *startup* after shutdown. This is I-09's shape in
  its lifecycle form — release one way, admit the other — and having the exit right
  is what made the entry look already handled.
- **Corrected by an explicit one-way lifecycle.** `CompositionLifecycle` runs
  `new -> started -> closing -> closed`; `claim_for_startup()` is the only
  transition out of `new` and is the lifespan's **first** statement — before the
  checks and **outside** the cleanup `try`, so an application that is refused a
  composition closes nothing belonging to the one still serving from it.
  `__setattr__` refuses every backward or sideways write to that state, so a spent
  composition cannot be reset and re-claimed. `aclose()`'s at-most-once,
  ownership, `finally` and re-raise behaviour is unchanged.
- **Evidence.** TC-STRUCT-11 amended by addition; the codifying case corrected and
  six new cases added, all driving the real ASGI lifespan protocol; **707 portal
  and 2260 bot tests pass with no failures and no skips**, run serially against the
  guarded disposable PostgreSQL database; five falsification mutations killed and
  one non-killing mutation disclosed with its explanation; every mutation reverted
  and verified byte-for-byte. **No accepted value, environment variable, route,
  schema, migration, dependency, deployment value or visual asset changed.**
- **Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain open; P3.2
  and P3.3 have not started.

Update 2026-08-16 (eighth, later the same day) — appended, not rewritten. This
one **corrects the boundary the seventh update declared beside its own
correction**, found by fresh independent implementation re-review. Recorded in §16
of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **The unwrapping was right; the limit stated beside it was not.** The seventh
  update excluded every selection in a callable position because "the source does
  not say which body runs", and said closing it would need a set-valued analysis.
  Both hold for `if flag`. Neither holds for an AST literal:
  `NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()`
  captures an instant at import, and `IfExp(test=Constant(True), …)` names the
  branch that runs. The detector returned nothing, because `_invoked_lambda()` did
  not handle `ast.IfExp` at all — and the control offered as evidence for the limit
  used a **name** as its test, so it never exercised the claim it was cited for.
  This is I-10's shape once more, now in a declared *limit*.
- **The detector was corrected to the invariant, and the limit narrowed to the
  truth.** A callable position now selects the reachable branch of a conditional
  whose test is an **exact** boolean literal, then continues through the lambda,
  call and named-expression chain already supported — one body, decidable from one
  node, no set-valued analysis. The boundary is **identity, not truthiness**: `1`,
  `1.0`, `'yes'`, `None`, a comparison, a `not`, a name and `or` are all left
  exactly where they were, each asserted as a case.
- **Ordinary evaluation is preserved, including what Python does not evaluate.**
  The conditional's test always runs and is always walked. When the test is a
  literal only the selected branch is walked, because the other expression is never
  evaluated — it builds no lambda and runs none of its defaults. A capture written
  there is therefore no longer reported; that is the one behaviour this correction
  removes, it is disclosed rather than left to be found, and it narrows no
  invariant, since no instant is captured by an expression that does not run.
- **Proved failing first, then proved on the real module.** With only the helper
  branch removed, the added case reports `{'true': [], 'false': []}` — the false
  negative reproduced. Inserted into the real module after `pytestmark`, each
  literal reproducer then failed TC-STRUCT-08 naming line 119, while the
  name-conditioned selection correctly did not fail. The literal-`False` run
  carries corroboration from outside this guard: CPython emitted
  `DeprecationWarning: datetime.datetime.utcnow() is deprecated` at line 119 during
  collection, which is the interpreter reporting the capture. Each mutation was
  restored byte-for-byte, verified by digest and by `cmp`, and the clean module
  reports nothing under both the pre-correction and the corrected detector.
- **The limit that remains is stated for the condition that creates it.** A
  selection whose test is not an exact boolean literal still executes one of two
  bodies at import and is still not reported; so is a lambda called through a name
  in a later statement. Both are asserted as cases, and closing either needs the
  data-flow analysis this task excludes.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime, both live PostgreSQL expiry constraints and every
  earlier accepted example are untouched; no dependency, configuration value,
  schema or migration changed.

Verification: 701 portal tests and 2260 bot tests pass with **no failures and —
every run executed with `-rs` — no skips** against the guarded disposable
PostgreSQL database, run serially because both suites share it; the affected
module is 63 passed and the TC-STRUCT-08/10/11 selection 94 passed. `git diff
--check` is clean, `compileall` passes under both required interpreters, and the
visual-freeze manifest verifies 14/14. `alembic check` was **not** re-run and is
not re-claimed: no schema, migration, table or model was touched. No formatter,
linter or type checker is configured.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (seventh, later the same day) — appended, not rewritten.
**Superseded in part by the eighth update above:** the boundary this update
declared beside its correction — that a selection in a callable position can
never be unwrapped — is true of `if flag` and false of `if True`/`if False`. The
named-expression correction itself stands; the text below is left as it was
written.

This
one **corrects the reach of the detector the sixth update corrected**, found by
fresh independent implementation re-review that took the sixth update's own rule
at its word. Recorded in §14 of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **The rule was right; the code did not recognise all of it.** The sixth update
  said a lambda is decided by *when its body runs*, and that a lambda invoked where
  it is written is decidable from the AST with no name resolution. But
  `_invoked_lambda()` knew only `ast.Lambda` and a chain of `ast.Call`, so
  `NOW = (reader := lambda: datetime.now(timezone.utc))()` and the curried
  `NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()` were reported
  clean. Both bodies execute during the import; neither needs a separately stored
  name resolved. This is I-10's shape once more, now in a claim about how far a
  corrected control reaches — verified against the constructs already raised rather
  than the ones it announced.
- **The detector was widened to its own rule, not the rule trimmed to the code.**
  A callable position is now read **through** an `ast.NamedExpr`: `(reader := L)`
  evaluates `L`, binds it as a side effect, and answers that same object to the call
  standing beside it. Three lines, recursive, so a walrus around a direct lambda,
  around a curried one, or nested in another walrus is one rule. The unwrapping
  decides only *whether the body runs* — the target is still walked (a target that
  is itself an instant name is still reported, and reported first) and the lambda's
  defaults are still walked, once each and in source order.
- **The boundary is closed and stated.** `ast.NamedExpr` is the only expression
  that yields its single operand, evaluated at that point, with neither a selection
  nor a lookup. A **selection** — `(f if flag else g)()` — is deliberately not
  unwrapped, because the source does not say which body runs.
- **Proved failing first, then proved on the real module.** With only the new
  branch removed, the added case reports `{'direct': [], 'curried': []}` — the false
  negative reproduced. Inserted into the real module after `pytestmark`, each
  reproducer then failed TC-STRUCT-08 naming line 119, while a lambda **stored and
  called through its name** correctly did not fail. Each mutation was restored
  byte-for-byte, verified by digest and by `cmp`, and the clean module reports
  nothing under both the pre-correction and the corrected detector.
- **Two limits are declared rather than left to be found.** A lambda called through
  a name in a later statement, and a lambda reached through a selection, are both
  live false negatives; both are asserted as cases so neither can be mistaken for
  coverage, and closing either needs the data-flow analysis this task excludes.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime, both live PostgreSQL expiry constraints and every
  earlier accepted example are untouched; no dependency, configuration value,
  schema or migration changed.

Verification: 700 portal tests and 2260 bot tests pass with **no failures and —
every run executed with `-rs` — no skips** against the guarded disposable
PostgreSQL database, run serially because both suites share it; the affected
module is 62 passed and the TC-STRUCT-08/10/11 selection 93 passed. `git diff
--check` is clean, `compileall` passes under both required interpreters, and the
visual-freeze manifest verifies 14/14. `alembic check` was **not** re-run and is
not re-claimed: no schema, migration, table or model was touched. No formatter,
linter or type checker is configured.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (sixth, later the same day) — appended, not rewritten.
**Superseded in part by the seventh update above:** the corrected detector this
update describes recognised an invoked lambda only where it was written bare, so
its "invoked where it is written" claim was wider than the check it announced. The
lambda rule itself stands; the text below is left as it was written.

This one **corrects the detector the fifth update added**, found by fresh independent
implementation re-review that read the code rather than the claim. Recorded in
§12 of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **The guard did not enforce the invariant it stated.** The fifth update's
  detector claimed to report *any* code that reads or constructs an instant while
  the module is imported, and its `visit_Lambda()` always skipped the lambda body.
  So `NOW = (lambda: datetime.now(timezone.utc))()` — a lambda invoked where it is
  written, whose body therefore runs during the import — produced no finding. The
  offered explanation ("a lambda body runs only when a test calls it") is true of a
  stored lambda and false of an invoked one. This is I-10's shape once more: the
  control was narrower than the claim made for it, and the gap was visible in the
  AST.
- **The detector was corrected to the invariant, not the invariant narrowed to the
  detector.** A lambda is now decided by **when its body runs**. Invoked in place —
  including the curried `(lambda: lambda: ...)()()` — its body is import-time code
  and is walked; stored, returned or passed, its body stays excluded; its defaults
  run at import and are walked either way. Function and method bodies, imports,
  annotations, class bodies, decorators, `timedelta` and `timezone` are unchanged.
- **Proved on the real module, before and after.** With the pre-correction
  detector the reproducer reported nothing; with the corrected one it reports
  `datetime.now` at its own source line. Inserted into the real module after
  `pytestmark`, the invoked form and the curried form each failed TC-STRUCT-08 with
  line 119 named, while a **stored** lambda reading the same clock correctly did
  not fail — the negative control that shows the fix did not simply widen the net.
  Each mutation was restored byte-for-byte, verified by digest and by `cmp`, and
  the clean module reports nothing under either detector.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime, both live PostgreSQL expiry constraints and every
  earlier accepted example are untouched; no dependency was added.

Verification: 699 portal tests and 2260 bot tests pass with **no failures and —
every run executed with `-rs` — no skips** against the guarded disposable
PostgreSQL database, run serially because both suites share it; the affected
module is 61 passed and the TC-STRUCT-08/10/11 selection 92 passed. `git diff
--check` is clean, `compileall` passes under both required interpreters, and the
visual-freeze manifest verifies 14/14. `alembic check` was **not** re-run and is
not re-claimed: no schema, migration, table or model was touched. The declared
limits are unchanged and one is restated: the detector is name-based and
syntactic, so a clock reached through an indirectly named helper, or a lambda
called through a variable, is still outside it.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (fifth, later the same day) — appended, not rewritten.
**Superseded in part by the sixth update above:** the detector this update
describes did not report an immediately invoked lambda, so its "any code that runs
at import" statement was broader than the check it announced. The text below is
left as it was written.

This one **corrects a claim made in the fourth update's submission**, found by fresh
independent implementation re-review. Recorded in §10 of
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **"Asked of the AST rather than of a reader" was not true when it was written.**
  §3.1 of the clock submission described the absence of a module-level datetime as
  asserted over the AST, and the change-log entry repeated it. Nothing asserted it:
  `tests/web/test_canonical_settings_graph.py` did not import `ast`, no case parsed
  the module, and a module-import clock could have come back without failing
  anything. The absence was real and the `OperationClock` correction was
  unaffected — the defect was in the evidence, not in the fix — but it is I-10's
  own shape one level out: a property established by reading, then described as
  established by a control.
- **The regression was added rather than the claim withdrawn.** A case now parses
  the module and fails if any code that runs **at import** reads or constructs an
  instant: module-level statements, class bodies, decorator expressions and
  default arguments are all in scope; function bodies, imports and annotations
  deliberately are not, being respectively the operation's own clock, not a clock,
  and unevaluated. `timedelta` and `timezone` are not findings, because a duration
  and a fixed offset are not instants and banning them would state a broader
  invariant than the one claimed.
- **The detector is proved, not merely run.** Three mutations of the real module —
  the reintroduced `NOW = datetime.now(timezone.utc)`, a fixed module-scope
  `datetime(...)` constructor, and a capture hidden in a default argument — each
  failed the case with the offending line named, and each was restored
  byte-for-byte, verified by digest and by `cmp`. A second committed case falsifies
  the detector against synthetic sources on every run. It reads AST semantics
  rather than text by necessity: the clean module contains seven literal
  occurrences of `datetime.now(timezone.utc)` in comments, docstrings and test
  inputs, none of them executable.
- **Nothing was weakened, and no production file changed.** `OperationClock`,
  N-04's accepted lifetime and both live PostgreSQL expiry constraints are
  untouched; no dependency was added, since the guard uses the standard library's
  `ast`.

Verification: 698 portal tests and 2260 bot tests pass with **no failures and — every
run executed with `-rs` — no skips** against the guarded disposable PostgreSQL
database, run serially because both suites share it; the whole affected module is
60 passed, the TC-STRUCT-08/10/11 selection 91 passed, and the OAuth/WebAuthn/clock
selection 575 passed. `git diff --check` is clean, `compileall` passes under both
required interpreters, and the visual-freeze manifest verifies 14/14. `alembic
check` was **not** re-run and is not re-claimed: no schema, migration, table or
model was touched. One limit is declared rather than smoothed over — the detector
is name-based, so a capture reached through an indirectly named helper is not seen;
both forms that have actually occurred here, and the alias form, are caught.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (fourth, later the same day) — appended, not rewritten. This
one **corrects a claim made in the third update below**, found by fresh
independent re-review. Submitted in
[`../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](../review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

- **"The constant is now anchored to the run's own clock" was a postponement, not
  a fix.** `NOW = datetime.now(timezone.utc)` in
  `tests/web/test_canonical_settings_graph.py` was evaluated at **module import**,
  while `created_at` is stamped later by two other authorities:
  `adapters.web.repositories.utcnow()` for `oauth_transactions`, and PostgreSQL's
  `server_default = now()` for `webauthn_challenges`. `expires_at` came from the
  injected instant, the two expiry check constraints compare them, and so the
  module still had **two clocks** and still depended on elapsed wall time — the
  failure simply moved from "noon on the day it was written" to "whenever more
  than N-04's ten minutes elapse between import and execution", which collection,
  an earlier case, a debugger pause or a slow worker can each produce.
- **The correction removes the second clock rather than widening the gap.** The
  constant is gone. A function-scoped fixture reads the instant from inside the
  operation's own transaction — PostgreSQL's transaction timestamp, which is by
  definition what the database will stamp `created_at` with — and binds the
  repository's clock to the same reading, so `expires_at - created_at` is exactly
  the configured lifetime no matter how much wall time passed beforehand. No
  sleep, no margin, no extended lifetime, no relaxed constraint, no module- or
  session-scoped timestamp, and **no production file changed**. Every original
  assertion, including N-04's accepted value, is preserved.
- **Two regressions name the defect.** One asserts on both affected tables that a
  row's expiry is exactly the accepted lifetime after that row's own creation —
  false for any non-zero elapsed time under the import-time model. The other
  injects a deliberately stale instant and requires PostgreSQL to refuse both
  rows, which proves the constraint is live rather than mocked away.

Verification: 696 portal tests and 2260 bot tests pass with **no skips and no
failures** against the guarded disposable PostgreSQL database, run serially;
`alembic check` reports no new upgrade operations; `compileall` is clean under both
required interpreters; the visual-freeze manifest verifies 14/14; and two
falsification runs restored the import-time model and reproduced both the
discriminator's failure and the original `expiry_after_creation` violation, then
restored the module byte-for-byte. A production observation is recorded rather than
acted on: `OAuthTransactionRepository.create()` re-reads the clock instead of
deriving `created_at` from the operation's `now`. It is not observable as a defect,
because every production caller injects the same process clock microseconds
earlier, and broadening this task to change it was not authorised.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (third, later the same day) — appended, not rewritten. This
one **corrects two claims made in the second update above**, both found by fresh
independent re-review, and both the same shape as the findings they were
correcting: a property established for one object or one path and then described
as established generally. Submitted in
[`../review/phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md`](../review/phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md).

- **"The routes are bound to the composition the factory accepted rather than to
  `app.state`" was true of the composition and false of the settings graph.**
  `create_app()` assigned the canonical graph to `app.state.settings`, and a
  `_settings(request)` helper read `request.app.state.settings` on **every call** —
  for the client and user-agent digests, mutation-origin validation, the session
  and login cookie names and attributes, CSRF key selection and the health view.
  Starlette's `State` is an ordinary mutable namespace, so one assignment gave an
  already-validated application a second complete settings graph to serve from: a
  different accepted `Origin`, a different CSRF key, a different cookie contract
  and different keyed audit and rate-limit identities. The correction is **which
  object the handler holds**: one frozen `RequestAuthority` built from the accepted
  graph, passed into route registration and the exception handler, with the four
  `app.state` references kept as diagnostics and proved inert against a second
  independently valid graph.
- **"`aclose()` is wired to the ASGI lifecycle" was true of a normal shutdown and
  false of a refused startup.** `create_app()` ran `run_resource_checks()` at
  factory time — after the composition had built the provider's `httpx.AsyncClient`
  and its owned SQLAlchemy engine, and before the `FastAPI` object the lifespan is
  installed on existed. A refusal therefore raised out of the factory with both
  resources live, no application returned, no lifespan able to execute and no
  caller for `aclose()` on the one path where the process was being told not to
  run. The checks now run **inside** the lifespan that owns the exact accepted
  composition, so a refusal is an ASGI startup failure that never reaches
  `lifespan.startup.complete`, still closes the provider exactly once and disposes
  an owned engine exactly once, leaves a lent engine alone, and surfaces the
  original typed `ConfigurationError` even when releasing the provider also fails.

A third, smaller correction was made in the same pass rather than deferred:
`WebComposition.__init__` builds an owned engine and can then raise while building
the envelope or the provider. No composition exists on that path, so nothing could
ever have released that engine; the constructor now disposes it before re-raising.
A provider that was constructed and then rejected is deliberately **not** closed
there — its `aclose()` is a coroutine and a synchronous constructor has no loop to
await it on — and that limit is recorded rather than papered over.

Verification: 694 portal tests and 2260 bot tests pass with **no skips and no
failures** against the guarded disposable PostgreSQL database, `alembic check`
reports no new upgrade operations, the visual-freeze manifest verifies 14/14, and
six falsification mutations each failed the intended regression for the intended
reason and were restored byte-for-byte. One defect was found and fixed in the
previous remediation's own uncommitted test module while running this sweep:
`tests/web/test_canonical_settings_graph.py` pinned its clock to a literal
`datetime(2026, 8, 16, 12, 0)`, which made five database cases start failing at
12:00 UTC on the day they were written, because the repositories stamp `created_at`
from the real clock and the expiry check constraints refuse a row that expires
before it was created. The constant is now anchored to the run's own clock; no
assertion changed.

**Nothing here is accepted.** P3.G1, RAID I-09 and RAID I-10 remain **open**
pending a fresh independent implementation review and a distinct security-focused
review. P3.2 and P3.3 have not been started.

Update 2026-08-16 (second, later the same day) — appended, not rewritten. This
one **corrects three claims made in the first update below**, which independent
re-review found were stated rather than established. Submitted in
[`../review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md`](../review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md).

- **"A test double still can" was not a type, only a name.** The composition kept
  a `provider_double: IdentityProvider` parameter and refused only a concrete
  `DiscordIdentityProvider`. `IdentityProvider` is a **structural protocol**, so a
  wrapper, a delegating adapter or an alternate implementation holding a second
  graph's client id, client secret, redirect URI, scopes, guild id and endpoints
  passed that exclusion and then built R-03's authorization URL and R-04's token
  exchange. The parameter is **removed**: production construction takes a settings
  graph and an optional HTTP transport, and nothing else.
- **The provider was checked once and remained replaceable.** `create_app()`
  compared it at startup while `WebComposition.provider` stayed publicly
  assignable and both routes dereferenced it per request, so an already-built
  application could be made to authenticate through a graph nothing validated —
  reproduced before the fix, with the replacement provider answering R-03.
  `settings`, `engine` and `provider` are now write-once behind read-only
  properties, the routes are bound to the composition the factory accepted rather
  than to `app.state`, and the startup comparison is **deleted** rather than kept
  as a check with nothing left to detect.
- **The engine seam was justified with the wrong argument.** The first update
  recorded that `settings.database.url` has exactly one reader, so an injected
  engine could not disagree with a second consumer. One reader and an injected
  engine do not make one authority — they make the configured database selection
  **ignorable**, and the S-14/S-15 checks then prove the injected engine is usable
  rather than that it is the database the graph names. Reproduced before the fix.
  The engine is now derived from the canonical graph, with ownership stated
  explicitly so a lent engine is never disposed by an application.

Test substitution is a `WebComposition` subclass in
`tests/web/composition_harness.py`, reached by overriding two protected hooks
rather than by passing an argument, importing nothing into production and
re-asking the suite's existing two-layer disposable-database guards about the
engine it lends.

Evidence is TC-STRUCT-09 and the amended TC-STRUCT-08, now 56 cases in
`tests/web/test_canonical_settings_graph.py`; **663 portal and 2260 bot tests with
no skips**; compilation under both configured interpreters; `alembic check` clean;
the visual freeze intact; four recorded falsification runs and two before/after
reproductions, each followed by a byte-for-byte checksum comparison of the
worktree.

**Nothing is accepted by this remediation.** No accepted numeric value moved, no
configuration variable was added, renamed or removed, `.env.example` is
unchanged, no schema, migration, route, service, worker behaviour or deployment
value changed, and the visual freeze is untouched. **I-09 and I-10 both remain
open**, **P3.G1 remains open**, and **P3.2 and P3.3 have not started.**

Previous status date: 2026-08-16 (one canonical settings graph per web process, including the identity provider; the graph's completeness proved independently of its declaration; I-09 and I-10 amended again; P3.G1 open)

Update 2026-08-16 (first) — appended, not rewritten. Submitted in
[`../review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md`](../review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md).

- **A web process now has one settings authority, not several (I-09/I-10).** The
  corrections below made each settings *type* valid by construction. That is a
  property of an object, not of a process: `WebComposition` still retained the
  caller's `WebSettings`, `create_app(settings_a, composition=composition_b)`
  gave middleware, cookies, digests and startup checks A while every service used
  B, and the two services that keep a graph re-read it per operation. The graph
  is now canonicalised **once**, at the composition root, all the way down —
  every field read once, every exact base type rebuilt through the constructor
  that holds the register — `create_app` takes exactly one configuration
  authority, and a consumer that retains settings requires that one object.
- **The identity provider was the last place two authorities could meet.** The
  composition accepted a ready-made provider, so a genuine
  `DiscordIdentityProvider` built from a second valid graph — its own client id,
  client secret, redirect URI, scopes, guild id, endpoints and timeout — could
  build R-03's authorization URL and R-04's token exchange for an application
  that had validated a different graph. S-05 checks the redirect URI against the
  public origin on the graph the process validated, so the check and the value
  used could diverge. The adapter is now **built by the composition** from its
  own `settings.discord` and cannot be injected; a test double, which holds no
  Discord configuration, still can, and an injected HTTP client supplies
  transport only.
- **The graph's completeness is no longer tested against itself.** The previous
  check iterated the entries the declaration already had, so a settings-valued
  field added to a dataclass and omitted from the table passed. The expected
  topology is now derived from the dataclasses' own annotations, with a narrow,
  explicit container grammar that fails closed; and canonicalising a settings
  type the graph does not declare is a runtime refusal rather than a silent
  "nothing nested here".
- **The adversarial suite offered as evidence for the first two points did not
  reach them.** Ten of its cases engaged their lie *before* calling the genuine
  constructor, so the object refused during test construction and the
  canonicalisation boundary was never exercised; its environment case used a
  variable name the reader does not recognise and a value inside its accepted
  range, so two of its four "problems" were never problems. Both are corrected
  and both corrections are falsified rather than asserted.

Evidence is TC-STRUCT-08, a new 46-case
`tests/web/test_canonical_settings_graph.py`; **653 portal and 2260 bot tests
with no skips**; compilation under both configured interpreters; `alembic check`
clean; the visual freeze intact; and four recorded falsification runs — the
mismatched-provider path restored, the premature-engagement harness restored, one
nested classification deleted, and the unrecognised variable name restored — each
followed by a byte-for-byte checksum comparison of the worktree.

**Nothing is accepted by this remediation.** No accepted numeric value moved, no
configuration variable was added, renamed or removed, `.env.example` is
unchanged, no schema, migration, route, service, worker behaviour or deployment
value changed, and the visual freeze is untouched. **I-09 and I-10 both remain
open**, **P3.G1 remains open**, and **P3.2 and P3.3 have not started.** The
residuals stated below are unchanged.

Previous status date: 2026-08-15 (N-23's worker lease corrected to an exact 60 seconds and the lease/heartbeat ordering question withdrawn; exact built-in `int` required at every register gate; the five I-10 settings types made valid by construction; I-09 and I-10 amended; P3.G1 open)

Update 2026-08-15 (seventh, later the same day) — appended, not rewritten. This
one **corrects a claim made in the sixth update below**, which independent review
found wrong. Submitted in
[`../review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md`](../review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md).

- **N-23's worker lease is a value, not a ceiling.** The settings-construction
  remediation defined `lease_seconds` as `PolicyBound(minimum=1, maximum=60)`,
  which accepted every exact integer from 1 to 60 as a lease. The accepted row
  states `60 seconds, heartbeat at most every 20 seconds` — one sentence, a lease
  **value** and a heartbeat **maximum** — and SM-05's
  `lease_expires_at = now() + 60s`, the logical schema's claim and renewal
  statements and the operational contract's `N-23 + N-44` recovery bound all read
  it as a fixed 60. A one-second lease was therefore a contradiction of the
  accepted documents, not a permitted tightening, and would have lost a live
  claim to ordinary heartbeat scheduling. The runtime entry is now
  `PolicyBound(minimum=60, maximum=60, policy="N-23")`; `heartbeat_seconds` is
  **unchanged** at 1…20.
- **The lease/heartbeat ordering question recorded below is withdrawn, not
  answered.** `lease_seconds=1, heartbeat_seconds=20` was cited as an
  in-register configuration proving an ordering rule was missing. It was never in
  the register — it was in the implementation. With the lease exactly 60 every
  accepted heartbeat is already far inside it, so **no ordering rule was added
  and none is needed**, **no relationship involving N-45 has been accepted**, and
  **nothing about N-23 blocks P3.3.** What P3.3 still owns is the *consumer*
  evidence for the worker's lease, heartbeat, attempt, timeout and queue bounds.

Evidence is TC-STRUCT-07 and TC-LIM-06 as corrected, with 20 further cases in
`tests/web/test_settings_construction_validation.py` (165 total, up from 145);
607 portal and 2260 bot tests with no skips; `alembic check` clean; the visual
freeze intact; and a falsification run restoring only the `1…60` entry in memory,
in which 10 of the new cases fail while every other portal test stays green and
`git status --short` is identical before and after.

**Nothing is accepted by this correction.** No accepted numeric value moved —
N-23's lease was and remains 60 seconds — no configuration variable was added,
renamed or removed, `.env.example` is unchanged (it already shipped
`WORKER_LEASE_SECONDS=60`), and no state machine, schema, migration, route,
service, worker behaviour or deployment topology changed. **I-09 and I-10 both
remain open**, **P3.G1 remains open**, and **P3.2 and P3.3 have not started.**
The other residuals stated below are unchanged and still stand:
`WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated
but read by no runtime consumer, N-09/N-10 have no P3.1 route consumer, N-21/N-22
have no consumer at all, and the worker's lease/heartbeat/attempt consumers are
P3.3's.

Update 2026-08-15 (sixth, later the same day) — appended, not rewritten. Two
connected corrections, submitted together in
[`../review/phase-3-p3-1-settings-construction-validation-remediation-submission.md`](../review/phase-3-p3-1-settings-construction-validation-remediation-submission.md).

- **The session validator did not require an exact `int` (I-09, sixth amendment).**
  The fifth remediation made both gates share one definition, and that
  definition still said `isinstance(value, int) and not isinstance(value, bool)`.
  That refuses `bool` and every float and accepts **every other subclass of
  `int`** — and an `int` subclass may override its rich comparisons, which
  Python consults in preference to the left operand's when the right-hand type
  is a subclass. `dataclasses.replace(settings, max_sessions_per_account=LyingInt(10))`
  therefore survived construction *and* `SessionPolicy.derive()`, and
  `len(live) >= maximum` was false for every live-session count: **N-66
  inoperative for the third time**, through the supported public constructor.
  The accepted rule is now the exact built-in type, `type(value) is int`.
- **The five I-10 settings types are now valid by construction (I-10).**
  `RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`,
  `DatabasePoolSettings` and `WorkerSettings` each enforce their accepted
  register in `__post_init__`, from one runtime `PolicyBound` per field that the
  environment reader and the constructor both call. The accepted non-numeric
  shapes are enforced with them, N-21's one cross-field rule is enforced at the
  object owning both fields, and every seam that re-reads a settings value reads
  each attribute once and validates that read.

Evidence is TC-AUTH-19(m), TC-STRUCT-07 and TC-LIM-06; 587 portal and 2260 bot
tests with no skips; `alembic check` clean; the visual freeze intact; and two
recorded falsification runs in which 16 of 22 new session cases fail against the
reviewed `isinstance` predicate and 81 of 145 new settings cases fail against the
previous reader-only model, while every pre-existing test stays green — neither
existing suite contained a counterexample.

**Nothing is accepted by this remediation.** No accepted numeric value moved, no
configuration variable was added, renamed or removed, no schema or migration
changed, and no deployment value changed. **I-09 and I-10 both remain open**,
**P3.G1 remains open**, and **P3.2 and P3.3 have not started.** Stated residuals:
N-09/N-10 have no P3.1 route consumer and N-21/N-22 have no consumer at all;
`WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated
but read by no runtime consumer; the worker's lease/attempt consumers are P3.3's;
and no ordering relationship between N-23's lease and heartbeat is enforced,
because no accepted document states one — that is an open maintainer question,
not a decision taken in a constructor.

Deferred validation gap recorded 2026-08-15: RAID **I-10** now tracks five
public `WebSettings` sub-dataclasses whose accepted numeric and related policy is
enforced by the environment reader but not by their own construction boundaries:
`RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`,
`DatabasePoolSettings` and `WorkerSettings`. This is not reported as an
environment-string bypass and no implementation change is claimed. It is a
future scoped remediation with security priority for rate limits, web bounds and
WebAuthn, availability priority for the database pool, and a mandatory pre-P3.3
condition for worker bounds. The acceptance contract explicitly requires exact
built-in integers (`type(value) is int`), direct/`replace`/subclass and real
consumer tests, preservation of aggregated redacted environment errors, and
independent review. See
[`../review/phase-3-settings-construction-validation-gap.md`](../review/phase-3-settings-construction-validation-gap.md).

Update 2026-08-15 (fifth, later the same day) — appended, not rewritten. Codex's
independent re-review of the session-bounds-construction remediation returned
**one blocking counterexample**, reported from two perspectives: F1 in the
implementation review and S1 in the distinct security-focused pass. They describe
the same defect, and it is a defect of *where the rule is defined* rather than of
what the rule says.

- `SESSION_CEILINGS` gave both enforcement gates the same **bounds** and left each
  to state independently what a value of these fields may **be**.
  `SessionSettings.__post_init__` required an actual `int`, never a `bool`,
  positive and within its ceiling. The derived-policy gate restated the rule as
  the two ordering comparisons `value < 1` and `value > ceiling`, and dropped the
  type half.
- Two ordering comparisons are not a whole-number rule, because `float("nan")`
  makes both of them false. A non-finite `max_sessions_per_account` therefore
  survived `SessionPolicy.derive()`, and `len(live) >= maximum` in
  `_enforce_session_limit` was false for **every** live-session count — **N-66
  revoked nothing**, and the bound on how many stolen or forgotten session
  credentials can be live for one account was inoperative.
- The route was ordinary, not forgery: `derive()` accepts `SessionSettings`
  subclasses deliberately, so a subclass whose inherited `__post_init__` observes
  the valid stored integer can answer differently on the single later derivation
  read. No `object.__new__`, no mutation of a frozen instance, no forged
  `SessionPolicy` and no private helper was needed.

Remediated on 2026-08-15 in
`docs/review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md`
with **one authoritative runtime definition** rather than a third restatement.
`session_policy_problem` / `session_policy_problems` sit beside `SESSION_CEILINGS`
in `application/web/config.py`, and both `SessionSettings.__post_init__` and
`_validate_policy_values` in `application/web/sessions.py` — the function
`SessionPolicy.__post_init__` and `SessionPolicy.derive()` both go through — call
them. The accepted type is an `int` and never a `bool`, which refuses floats as a
class: integral-looking, fractional, infinite and NaN alike, rather than naming
the one non-finite value a review happened to find. Evidence is TC-AUTH-19(l) and
the new TC-SESS-08b in `tests/web/test_session_policy_numeric_validation.py`, 420
portal tests and 2260 bot tests passing with no skips, `alembic check` clean, and
a **recorded falsification run**: with the reviewed two-comparison validator
restored in memory, nine of the new cases fail while the whole pre-existing
54-test session-lifetime suite stays green — the earlier suite contained no
counterexample.
**Nothing is accepted by this remediation.** It is submitted for a fresh
independent implementation re-review and a separately reported security-focused
re-review; **P3.G1 remains open, and P3.2 has not started.** I-09 is amended
rather than closed. No accepted numeric value moved, no configuration variable was
added or renamed, no schema or migration change was made, and no deployment value
changed. The stated residual is that the other `WebSettings` sub-dataclasses have
**not** been audited for the same divergent-gate shape.

Previous update 2026-08-15 (fourth, later the same day) — appended, not rewritten. Codex's
independent re-review of the idle-policy-construction remediation returned **three
blocking counterexamples**, and together they say that an extensible policy object
was the wrong authority boundary rather than one that needed another guard.

- **F1.** `SessionIdlePolicy.from_settings()` validated only positivity, and
  `SessionSettings` was a public frozen dataclass with no construction-time
  validation. `SessionSettings(..., emergency_idle_minutes=60, ...)` was therefore
  an accepted object, and the policy derived from it returned sixty minutes for
  both break-glass methods. Closing the policy's constructor achieved nothing
  while the numbers it read were unconstrained, and environment-reader validation
  cannot make invalid instances of a public settings type impossible.
- **F2.** The refresh statement was generated by iterating the policy's public,
  overridable `__iter__`. An ordinary subclass inherited the supported factory and
  replaced the SQL's mapping while `for_method()` went on reporting fifteen
  minutes; the reproduction bound `idle_seconds = 3600.0` for all three methods.
  This is ordinary Python subclassing, not forgery, and the previous submission
  was wrong to treat it as out of scope.
- **F3.** `SessionService.__init__()` accepted a repository *and* an independently
  supplied policy and never required them to be the same. Correct wiring at the
  two production sites was true and was not an invariant of the boundary.

Remediated on 2026-08-15 in
`docs/review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`
by simplifying the construction model rather than adding guards.
**`SessionIdlePolicy` is deleted.** `SessionSettings` validates the accepted
numeric register in `__post_init__`, so an out-of-register instance cannot exist
however it was built (F1). `SessionRepository` **derives** a `SessionPolicy` from
settings, reading each configured number exactly once, and accepts no policy
object; the `CASE` branches are generated by walking `AuthMethod` and asking an
explicit classification table, so there is nothing to iterate and nothing to
subclass into the SQL (F2). `SessionService` reads its bounds from the repository
and has no policy argument, so a graph with two independently configured bounds
sources is not constructible (F3). An authentication method with no explicit
classification now refuses at import and at repository construction instead of
inheriting the shorter window by inference. Evidence is TC-AUTH-19(k), 392 portal
tests and 2260 bot tests passing with no skips, `alembic check` clean, and the
recorded before/after reproductions of all three counterexamples.
**Nothing is accepted by this remediation.** It is submitted for a fresh
independent implementation re-review and a separately reported security-focused
re-review; **P3.G1 remains open, and P3.2 has not started.** I-09 is amended
rather than closed. Reachability is unchanged and still stated plainly: no P3.1
HTTP route calls `touch()`, so this correction is proven at the service and
repository boundary and not in request handling. No schema change, no migration
edit, no configuration-variable rename and no deployment-value change was
involved.

Previous update 2026-08-15 (third, later the same day) — appended, not rewritten. Codex's
independent re-review of the session-touch policy remediation returned **one
blocking finding**, and it is the same authority in a third position rather than a
new defect. Removing `idle` and `expected_auth_method` from
`SessionRepository.touch()` had moved the method-to-duration pairing into
`SessionIdlePolicy`'s public dataclass constructor: the mapping that gives *every*
authentication method N-06's 60-minute window is complete, duplicate-free and
positive, so the constructor accepted it, and a repository built with it selected
60 minutes for persisted WebAuthn and recovery-grant rows — N-15's 15-minute idle
limit bypassed again, up to the 60-minute emergency absolute bound. The policy
tests proved completeness, uniqueness and positivity and never attempted a
complete but semantically false mapping, so the previous submission's claims that
no supported API could pair a method with another policy's duration, and that
policy was built once and injected, were both false. A related composition defect
was found with it: `WebComposition.services()` built one policy for the repository
while `SessionService.__init__()` built another from settings — equivalent in
production, but two derivations rather than one instance. Remediated on 2026-08-15
in
`docs/review/phase-3-p3-1-od-44-session-idle-policy-construction-remediation-submission.md`:
the policy has **no public constructor**, its one factory takes `SessionSettings`,
which methods receive the emergency window is classification derived inside it
from `AuthMethod.is_break_glass`, and one instance is built at the composition
root and injected into the repository *and* the service. `SessionSettings` remains
the sole numeric source and every pair of values its contract accepts — including
an ordinary window shorter than the emergency one — maps by classification.
Evidence is TC-AUTH-19(j), 16 killed mutants with byte-identical restoration
verified by digest, 381 portal tests and 2260 bot tests passing with no skips.
**Nothing is accepted by this remediation.** It is submitted for a new Codex
independent implementation re-review and a separately reported security-focused
re-review; **P3.G1 remains open, and P3.2 has not started.** I-09 is amended
rather than closed. Reachability is unchanged and still stated plainly: no P3.1
HTTP route calls `touch()`, so this correction is proven at the service and
repository boundary and not in request handling — it is required now because P3.2
is intended to consume this API. No schema change, no migration edit and no
configuration change was involved.

Previous update 2026-08-15 (second, later the same day) — appended, not rewritten. Codex's
independent implementation and security re-reviews of the session-lifetime
remediation returned **one blocking finding**: the break-glass idle-policy
correction had been made in `SessionService` only. `SessionRepository.touch()`
still accepted `idle` and `expected_auth_method` as independent arguments and
verified only that the method matched the row, so a caller supplying a
break-glass session's **correct** method beside N-06's 60-minute duration matched
and extended that session's idle window to its absolute bound — N-15's 15 minutes
bypassed through the supported lower-level API, with every stated check passing.
The repository test offered as proof supplied a *mismatched* method and never
exercised that pairing; it has been replaced, not retained. Remediated on
2026-08-15 in
`docs/review/phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md`:
the refresh duration is no longer a parameter at any layer, being selected inside
the atomic `UPDATE` by `CASE auth_method` from an immutable validated
`SessionIdlePolicy` built from configuration and injected once at the composition
root. Evidence is the rewritten TC-AUTH-19, 13 killed mutants with byte-identical
restoration verified by digest, 362 portal tests and 2260 bot tests passing with
no skips. **Nothing is accepted by this remediation.** It is submitted for a new
Codex independent implementation re-review and a separately reported
security-focused re-review; **P3.G1 remains open, and P3.2 has not started.**
I-09 is amended rather than closed. Reachability is unchanged and still stated
plainly: no P3.1 HTTP route calls `touch()`, so this correction is proven at the
service and repository boundary and not in request handling — it is required now
because P3.2 is intended to consume this API.

Previous update 2026-08-15 — appended, not rewritten. Codex's independent re-review of the
provider-binding and rotation-integrity remediation returned **two further
blocking findings**, both in the session idle refresh: `touch()` could revive an
idle-expired session from a stale record, and it gave WebAuthn and recovery-grant
sessions N-06's 60-minute idle window instead of N-15's 15-minute one. A refused
refresh was additionally reported as success. Both are remediated on 2026-08-15
(`docs/review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md`)
together with the documentation the rotation-lifetime correction left
outstanding: liveness is now enforced inside each conditional write, neither
continuation writes `absolute_expires_at`, the idle duration follows the persisted
authentication method, and both refusals are typed. Evidence is TC-AUTH-18 and
TC-AUTH-19, nine killed mutants with byte-identical restoration, 354 portal tests
and 2260 bot tests passing with no skips. **Nothing is accepted by this
remediation.** It is submitted for a new Codex independent implementation
re-review and a separately reported security-focused re-review; **P3.G1 remains
open, and P3.2 has not started.** New issue **I-09** tracks it. Note for the
reader: no P3.1 HTTP route calls `touch()`, so that half of the correction is
proven at the service and repository boundary and not in request handling.

Previous status date: 2026-08-14 (I-07 and I-08 ruled; OD-44 implemented, re-reviewed by Codex, and remediated again for provider binding and rotation integrity; P3.G1 open)

Baseline: v1.5; accepted by Peter Duscha on 2026-08-02

Overall health: Amber — Phases 0–2, the frontend visual-design track, Phase 3
readiness and P3.0 are accepted. P3.G0 is closed. **P3.1 was implemented,
reviewed by Codex, and partly remediated; it is not accepted.** The disposable
PostgreSQL prerequisite was confirmed on 2026-08-14 and the package's database
evidence was executed against it. Codex returned three blocking findings and one
important finding; two are remediated and Peter has now ruled **I-07** and
**I-08**. The OD-44 durable completion binding is now **implemented** as
migration 0009, with real-PostgreSQL concurrency, constraint, rollback and
mutation evidence, and is resubmitted. Codex's independent and security re-reviews
of that package returned two further blocking items — the completion claim did not
bind the transaction's recorded **provider**, and the partial unique index Peter
approved needed rotation integrity behind it — and both are now remediated in the
same revision 0009 and the OAuth, session and provider boundaries, with
TC-AUTH-15/16/17 and six killed mutations. P3.G1 now requires a Codex independent
implementation re-review plus a distinct security-focused pass before P3.2 may
start. Staging does not exist, so
every staging-class check in the traceability contract remains unrun. Gemini
production integration remains blocked.

## Decisions ruled on 2026-08-14

| # | Decision | Note | Blocks |
|---|---|---|---|
| I-07 / OD-44 | Durable one-way completion binding approved, with one authoritative unique `sessions.oauth_transaction_id` and no reverse FK | [`../review/phase-3-p3-1-sm-01-completion-binding-decision.md`](../review/phase-3-p3-1-sm-01-completion-binding-decision.md) | **Implemented 2026-08-14** as migration 0009; re-review still blocks P3.G1. See [`../review/phase-3-p3-1-od-44-remediation-submission.md`](../review/phase-3-p3-1-od-44-remediation-submission.md) |
| I-07 / OD-44 §8 | The scoped partial unique index confirmed as authoritative, **conditionally** on rotation-chain integrity; the completion claim must also bind the transaction's recorded provider | [`../review/phase-3-p3-1-sm-01-completion-binding-decision.md`](../review/phase-3-p3-1-sm-01-completion-binding-decision.md) §8 | **Implemented 2026-08-14** in the same uncommitted revision 0009 and the OAuth, session and provider boundaries; re-review still blocks P3.G1. See [`../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md`](../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md) |
| I-08 / OD-45 | Service/constraint evidence remains at P3.G1; direct-HTTP portions of TC-BG-05b/c/e are mandatory at P3.G2 | [`../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md) | P3.G2 evidence; no waiver |

## Milestone status

| Milestone | State | Gate | Evidence / next condition |
|---|---|---|---|
| Phase 0 — Discovery and architecture | Accepted | Closed 2026-07-30 | `docs/discovery/phase-0-handoff.md`, `docs/review/phase-0-submission.md` |
| Phase 1 — Database foundation | Accepted | Closed 2026-07-31 | Maintainer acceptance at the head of `docs/review/phase-1-submission.md` |
| Phase 2 — Import and reconciliation | Accepted | Closed 2026-08-12 | C-24 and B-1 closed after independent re-review returned no findings; Peter Duscha accepted the data-integrity, identity and migration-safety gate. See `docs/review/phase-2-c-24-independent-re-review-2026-08-12.md` and change-log C-24-R. |
| §12.1 frontend visual-design track | Accepted | Closed 2026-08-13 | Peter accepted Steps 1–5, including real-mobile inspection. Fourteen frozen implementation/asset files verify against `docs/review/phase-3-visual-freeze-manifest.sha256`; current token and contrast tools pass. See `docs/review/phase-3-visual-prototype-handoff.md`. |
| Phase 3 — authentication, read-only portal and Council administration | P3.0 through **P3.4 accepted; P3.5 active** | P3.G0–P3.G4 closed; overall Phase 3 gate open | P3.4 and its frontend gate were accepted on 2026-08-23. C2-1 is accepted and Codex recommends F5/S-2 closure, but mandatory P3.5 staging/operations/performance/browser evidence and A-05 criteria 4/10 remain incomplete. See `docs/review/phase-3-gate-disposition-2026-08-25.md`. |
| Phase 4 and later | Not ready | Predecessor gates apply | No later implementation is authorized. Follow implementation-plan §12.0 and package-specific definitions of ready. |

## Current critical path

1. **P3.0 contract/security design package — delivered 2026-08-13.** Produced
   from `docs/review/phase-3-p3-0-claude-prompt.md`. It adds no protected route
   and no framework scaffold. Five proposals need Peter's decision: a separate
   `freedom-worker` service, the tighter break-glass route boundary, apply-as-a
   -durable-job, the P3.0-proposed numeric values, and ADR 0010.
2. **P3.G1 — closed 2026-08-16; P3.2 is the current package.** P3.1 was
   delivered on 2026-08-14 from `docs/review/phase-3-p3-1-claude-prompt.md`,
   against a confirmed guarded disposable PostgreSQL database, and reviewed by
   Codex the same day. Two findings were remediated — the incomplete OAuth
   refusal auditing and the inaccurate migration reporting — and are recorded in
   `docs/review/phase-3-p3-1-remediation-submission.md`. Peter approved the
   durable one-way completion binding (OD-44) and moved only the unavailable
   HTTP evidence to P3.G2 (OD-45). The completion binding **was implemented on
   2026-08-14** as migration 0009 with the required concurrency, constraint,
   rollback and mutation evidence, recorded in
   `docs/review/phase-3-p3-1-od-44-remediation-submission.md`.
   Codex completed the independent implementation review and distinct
   security-focused pass on 2026-08-16; Peter accepted the package and closed
   P3.G1. P3.2 may now implement the member reads, identity evidence and access
   administration package. P3.3 remains behind P3.G2.
3. **Coordinated implementation.** Claude owns the backend foundation;
   Gemini owns production Jinja/static/HTMX integration only against accepted
   route/view-model contracts; Codex supplies independent and separate
   security-focused review recommendations. Peter records gate decisions.
4. **Backend contract package.** Authentication and server-side authorization
   precede every protected route. The measured 9.57-second, 32-Actor preview
   requires a durable asynchronous/progressive design rather than a synchronous
   HTTP handler or restart-unsafe in-memory queue.
5. **Stop at the contract/security review.** Gemini production integration does
   not begin until Claude's route/view-model contracts are stable and accepted.

## Closed readiness inputs

- Project reconciliation and accepted visual baseline commit: completed
  2026-08-13 without production implementation.
- Phase 2 gate: accepted 2026-08-12.
- OD-16 and OD-17: closed 2026-08-12.
- Backend/frontend/review delivery-agent allocation: Claude/Gemini/Codex.
- §12.1 visual direction: accepted 2026-08-13.
- Visual implementation freeze: 14/14 manifest entries verified.
- Static evidence tools on 2026-08-13: CSS tokens 71 defined, 62 referenced,
  zero undefined; contrast self-tests 11 passed; contrast matrix 49 pairs, 48
  passed, one disabled-state exemption, zero failures.

## Open Phase 3 conditions

- maintainer/reviewer availability windows before calendar forecasting;
- confirmed development, disposable PostgreSQL and staging environments — the
  disposable database was **confirmed on 2026-08-14** (`freedom_test`, reached
  over the local Unix-domain socket, proven through the repository's own
  `assert_disposable_target` / `verify_connected_unix_socket_target` guards) and
  the separate `freedom-web` virtualenv now exists; **staging still does not**,
  so every staging-class check in the traceability contract is unrun;
- expansion of the accepted traceability categories to exact implemented tests
  and evidence during each implementation handoff;
- accepted backend route/view-model contracts before production frontend work —
  accepted at P3.G0, with the later P3.G2/P3.G3 freeze gates still required;
- implementation and verification of the accepted configuration, deployment,
  monitoring and rollback contracts for the new `freedom-web` process; and
- ~~two quantities remain unmeasured and block no P3.0 acceptance but must be
  measured before production: real-folder apply duration and worker peak
  memory~~ — **both measured 2026-08-27** (TC-PERF-02 real-folder apply
  19,927 ms; TC-PERF-01 worker peak 302 MiB). What remains unmeasured is peak
  memory anywhere near N-20's 64 MiB input ceiling, where the only figure is an
  extrapolation from two real points and no corpus exists to measure. Their
  residual rows RR-06 and RR-05 are proposed for closure at the gate and are not
  closed here; and
- **deployment task 4 is outstanding**: no real Foundry export, preview or
  compatibility check has been run against module 1.0.9, which is installed on
  all three instances but not yet loaded by any running instance. Nothing yet
  demonstrates the scoped version ranges behaving on real data; and
- **one deployed comment lags the repository**: the worker unit's file header on
  the host still calls peak memory unmeasured. Comment-only, no runtime effect,
  needs `daemon-reload` and no restart.

## Scope controls

- `design-prototype/` remains static reference material and must not be imported
  or served by production code.
- Phase 3 remains read-only for character game state. Council character-link
  management and snapshot-import control are authorized administrative flows;
  generic character corrections and controlled-vocabulary editors remain with
  their owning later typed packages.
- The former Claude contrast-tooling prompt is superseded without execution. It
  is not a backend implementation prompt.
- No deployment, Caddy change, OAuth registration, production database change,
  Foundry mutation or Google Sheet mutation is authorized by reconciliation.
  **The 2026-08-27 deployments of HSTS, module 1.0.9 and `MemoryMax=2G` were
  each authorized explicitly by Peter Duscha** and are recorded in
  `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` §5O. They
  authorize nothing further, and no Foundry world data was read or mutated.

## Historical evidence

The detailed Phase 2 remediation chronology remains in the dated records under
`docs/review/`, `docs/operations/` and `docs/project-management/change-log.md`.
This current-status document intentionally does not repeat superseded open-gate
statements; Git history retains the earlier status narrative.

## Next status update

Update when P3.2 is submitted to P3.G2, or earlier if a new decision, critical
risk or environment constraint emerges. I-06 and A-05 must remain visible until
their staging/production-exposure acceptance criteria are satisfied.
