# Project status

Status date: 2026-08-25 (sixty-second update: the Phase 3 gate was audited after
C2 acceptance. Mandatory P3.5 staging, browser, operations and performance
evidence remains incomplete, so Phase 3 cannot close and Phase 4 implementation
cannot start.)

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
- two quantities remain unmeasured and block no P3.0 acceptance but must be
  measured before production: real-folder apply duration and worker peak memory.

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

## Historical evidence

The detailed Phase 2 remediation chronology remains in the dated records under
`docs/review/`, `docs/operations/` and `docs/project-management/change-log.md`.
This current-status document intentionally does not repeat superseded open-gate
statements; Git history retains the earlier status narrative.

## Next status update

Update when P3.2 is submitted to P3.G2, or earlier if a new decision, critical
risk or environment constraint emerges. I-06 and A-05 must remain visible until
their staging/production-exposure acceptance criteria are satisfied.
