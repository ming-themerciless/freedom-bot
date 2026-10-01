# Claude prompt — RP-11 I1-R3 retained-alias publication implementation

Prompt ID: `C-P5.0-R5-RP11-I1-R3-I1`

Date: 2026-09-28

State: **assigned by Peter Duscha; repository requirements, source, tests and
evidence only; no host or operational authority**

## 1. Assignment

Claude, implement the accepted RP-11 I1-R3 publication redesign as one coherent
repository slice. Amend the proposed operational-evidence requirements and the
unwired RP-11 implementation together so records and index states use an
exclusively created named staging inode, one non-replacing descriptor-relative
hard link to the final name, and retention and indexing of both names. Remove
RP-11's `O_TMPFILE`/`/proc/self/fd` publication dependency and perform no
automatic unlink, rename, repair or alias cleanup.

Read, in this order, before planning or editing:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 13, 14,
   16 and 20 and Package 5.0's milestone and acceptance criteria;
3. `docs/review/Handover information`;
4. the first restriction banners and applicable contract in
   `docs/operations/disposable-test-server.md`;
5. the [I1-R3 proposal](phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md)
   and [acceptance](project-review-2026-09-28-p5-r5-rp11-i1-r3-redesign-acceptance.md);
6. Codex's [I1-R2 review](project-review-2026-09-28-p5-r5-rp11-i1-r2.md),
   the I1-R2 assignment and handback, and the I1-R1 review chain;
7. `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`, especially
   RP-11, MI inputs, A0-08/B0-08, C-10 through C-15, B0-RA and §§9.5–9.5.4;
8. `tools/phase_5_0_evidence/capture_contract.py`,
   `execution/capture_store.py`, `execution/capture_mechanism.py`,
   `execution/retention_check.py`, `execution/descriptors.py`,
   `execution/boundary.py` and `review_manifest.py`; and
9. the RP-11, retention, no-execution, manifest and directly affected
   structural tests.

The I1-R3 acceptance is the controlling publication decision. Preserve all
unaffected R5, RP-11 and retention requirements. If the retained-alias design
cannot meet a requirement safely, stop and return the exact contradiction;
do not restore the rejected route or weaken the requirement silently.

## 2. Required requirements amendment

Amend the operational-evidence draft coherently. Every RP-11 publication
statement must agree on these semantics:

1. Create one deterministic, object-specific staging name descriptor-relative
   with `O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW | O_CLOEXEC`, mode `0600`.
   Refuse an occupied name without reading, removing or replacing it.
2. Verify the bound inode is regular, operator-owned, exact mode `0600`, link
   count one and on the expected device. Write all bytes with a checked loop;
   verify size and digest; then obtain the file barrier.
3. Create the final name with exactly one call to the existing
   descriptor-relative, no-follow exclusive-link primitive. Do not pre-check
   the final name instead of relying on kernel `EEXIST`.
4. Obtain the containing-directory barrier, then open both names no-follow and
   prove identity, type, owner, mode, device, link count two, bytes, size and
   digest.
5. Account for both exact names, roles and shared inode identity in the next
   durable index state. Only that state admits the object and permits the next
   act.
6. Never unlink, rename, repair, adopt or remove the staging alias.

Remove or replace every RP-11 reference to `O_TMPFILE`, unnamed inode,
`/proc/self/fd`, first-and-only name, link count zero/one, automatic probe
cleanup and §9.5.4's mutating capability probe. Do not alter historical
handbacks or reviews.

There is no separate mutating publication probe. The first real X-1 genesis
publication, before every host command, is the fail-closed capability test.
Its failure follows the same bounded unadmitted-object and stop semantics as
every later publication. Update all affected matrices, MI inputs, stop
conditions, binding fields and cross-references. This supersedes only the
proposed I1-R1 publication amendment; it does not reopen accepted R5 retention
requirements or authorize a pass.

## 3. Publication and interruption behavior

Implement the accepted sequence for every record and immutable index state.
Names must be deterministic from already-bound record/index identity, one
component only, byte-safe and collision-refusing. A staging and final name for
one object form the only permitted expected alias pair.

Represent and fail closed on these states: no staging entry; staging without a
confirmed final link; both names before the directory barrier; both after the
barrier but before verification; both verified but not index-admitted; and both
admitted by a durable index state.

Before admission, every existing staging or staging/final object is
unadmitted. Preserve and report it; never complete, adopt, repair, digest for
admission or use it as evidence. A final-name occupant is not mechanism-owned.
A failed or unconfirmed barrier is never retried or cured later.

The one-shot X-3 and interruption rules remain. Finalization may account for
names already known to have been created, but must not repair publication.
After process/host interruption, discovery is read-only and no X-3 occurs.

## 4. X-4 and B0-RA retained-alias rules

Replace the blanket hard-link-alias refusal with one narrow exception:

* exactly the recorded staging/final pair for one admitted object may share an
  inode;
* both names, roles, type, owner, mode, device, size, digest and link count two
  must agree with the durable state;
* a name belongs to only one pair and category;
* any third link, cross-object alias, missing member, duplicate/ambiguous
  encoding, unexpected name, identity change, wrong link count or type is a
  fail-closed stop; and
* unadmitted names receive only the accepted R5 presence/name/type checks,
  never content reads or invented digests.

Preserve complete bidirectional enumeration and every no-follow,
descriptor-relative, traversal, symlink, mutation/race and read-only control.
B0-RA remains incapable of writing or cleanup.

## 5. Source constraints

* Reuse the existing named-source descriptor-relative no-follow exclusive link;
  do not add a second `os.link` site.
* Preserve the separately reviewed I3 caller and behavior.
* Remove `link_unnamed_descriptor` if no reviewed caller remains, with stale
  exports and contract text.
* Add no `ctypes`, native helper, shell execution, rename, cleanup fallback or
  alternate publication route.
* Keep RP-11 unwired and unreachable from default/dry-run and operational CLI
  paths.
* Preserve exact argv, separate raw streams, durability order, one-shot
  finalization, handback binding and unaffected retention behavior.

The I1-R2 portability diagnostic has no gate role. Remove it if obsolete, or
retain only clearly labelled historical diagnosis that cannot be mistaken for
current capability evidence.

## 6. Required tests

Use pytest temporary directories only. Prove externally visible state:

* successful genesis, record and index publication creates exactly the pair,
  one inode, link count two, exact bytes and required barriers;
* occupied staging/final names refuse without mutation;
* partial, zero-length and falsely reported writes never admit an object;
* every §3 interruption leaves the exact classified state, never retries,
  repairs or cleans, and prevents the next command/act;
* barrier failure stays terminal;
* X-4/B0-RA accept only a recorded pair and reject missing members, wrong
  identity/link count, third or cross-object aliases, reused names, unexpected
  objects and all existing hostile-tree cases;
* unadmitted states are retained and never read as evidence;
* source/AST guards prove no RP-11 `O_TMPFILE`, `/proc/self/fd`, `ctypes`,
  rename, automatic unlink, duplicate `os.link` or operational wiring; and
* unchanged I3 and shared-primitive tests still pass.

No focused test may skip because a publication feature is absent.

## 7. Manifest, handback and return pointers

Update `review_manifest.py` and regenerate existing review artifacts through
the established dry-run workflow. Increment the manifest version with a
precise reason. The digest is review input only and must never reach
`--execute`.

Create
`phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-handback.md` with
exact files/digests, semantic draft changes and digest, architecture/interface
changes, requirement-to-test mapping, commands and counts, interruption-state
evidence, manifest/artifact effects, unwired confirmation, implications,
checks not run, Git status and independent-review focus.

On return only update the active handover, status, implementation-plan §20 and
first disposable-server banner. Do not add acceptance or close a finding.

## 8. Validation

Run serially with `TEST_DATABASE_URL` explicitly unset,
`PYTHONDONTWRITEBYTECODE=1` and pytest cache disabled:

1. RP-11 capture and retention tests;
2. replacement/current publication diagnostic tests;
3. affected descriptor, I3, boundary, no-execution, manifest, concrete-plan
   and structural tests; and
4. harness CLI dry run only, never `--execute`.

Zero focused skips are required. Do not run full bot/web suites. Run scoped
`git diff --check`, verify links and independently recompute changed-source and
artifact digests. Report only tools actually run.

## 9. Authorization and prohibitions

Authorized: repository reads; coherent edits to the proposed operational
draft, RP-11/narrowly shared source, focused tests, review manifest/generated
review artifacts, handback and current pointers; bounded local synthetic tests
with `TEST_DATABASE_URL` unset.

Not authorized: SSH, rsync, synchronization, network/host inspection, `sudo`,
database access, provisioning, controlled writes, reboot, verifier, evidence
band, harness `--execute`, real participants, real capture roots or operational
paths, protected historical `/tmp` artifacts, secrets scan, guards/hooks,
governing rules, C-11, launcher environment, another RP, MD-1 through MD-6,
unrelated source, operational wiring, acceptance, finding closure, RP-11
satisfaction, `plan.is_executable=True`, pass acceptance, P5.0-R5 closure,
OD-62 binding, Package 5.0 readiness, commit or push.

Do not read secrets or print the environment. Preserve unrelated changes. A
guard/tool refusal is a stop condition and must not be bypassed.

## 10. Return state

Return for independent Codex technical, security, operational and evidence
review, then stop. All three findings remain Open; requirements,
implementation and digest remain unaccepted; RP-11 remains unmet; neither pass
is executable; P5.0-R5 remains Blocking; OD-62 G-A remains conditional;
`plan.is_executable=False`; Package 5.0 remains not ready.
