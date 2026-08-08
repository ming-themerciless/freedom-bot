# Claude remediation prompt — Phase 2 I-03 second re-review findings

Date: 2026-08-04
Repository: `/opt/discord-bots/freedom-bot`
Branch: `docs/platform-plan`
Baseline HEAD before the uncommitted Phase 2 work: `c8a3da9`

You are the implementing agent and working Technical Lead. Remediate the two
blocking findings below. Do not claim either finding closed, approve your own
work, cross a phase gate, commit, push, install the Foundry module, issue a real
credential, or run a rehearsal. Peter Duscha remains the Acceptance Authority,
and the result requires independent implementation and security re-review.

Before changing anything, read completely:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`;
3. `docs/review/phase-2-i-03-remediation-review-request.md`;
4. `docs/review/phase-2-i-03-remediation-submission.md`;
5. the relevant implementation, tests, ADR, operations, project-management and
   configuration files; and
6. this working tree's `git status` and diff. Preserve all existing work and
   unrelated user changes.

## Review result to remediate

The first remediation passed its named automated suites, but the package is not
ready for acceptance. Codex found two blocking issues.

### I-1 remains open — false “nothing was stored” claims remain

The remediation claimed every such statement had been corrected, but several
remain. Audit the entire repository for equivalent claims, not just these
examples:

- `application/foundry/submission.py` unresolved concurrency: artifact storage
  has already run through `_store_and_record()`, but the refusal around current
  line 537 says `Nothing was stored`.
- `_replay_stored()` and `_replay()` contain similar statements around current
  lines 672, 732 and 741. Some occur before the current attempt writes bytes,
  but their wording can still be read as a claim about all durable state or the
  earlier winning submission. Make each message say only what that path proves.
- `application/artifacts.py` constructs every `ArtifactStorageError` with
  `Nothing was stored or served`. That is false for
  `durability_unconfirmed`, whose deliberate contract is that a correct target
  may already have been published and must be preserved for retry.

Required outcome:

- No error, response, exception, notification, log guidance, docstring,
  operations table or recovery instruction may claim that no bytes were stored
  on a path that cannot establish that fact.
- Prefer the already established vocabulary: nothing was **recorded or
  confirmed**, retrying with the same idempotency key is safe, and a retry cannot
  create a second snapshot.
- Narrower pre-storage paths may truthfully say the current attempt did not
  write an artifact only when that is useful and unambiguous. Do not use a broad
  phrase merely because it happens to be true in one current implementation
  branch.
- Preserve the bounded, non-sensitive error vocabulary. Do not expose paths,
  exception text, SQL, credentials, artifact bytes or Actor values.
- Keep the orphan-artifact procedure truthful and read-only. Do not add an HTTP
  listing or deletion surface and do not decide the outstanding retention
  policy.

Add regression tests that enumerate every `SubmissionRefused` and
`ArtifactStorageError` path capable of occurring after artifact publication or
against pre-existing durable state. At minimum prove:

1. unresolved uniqueness/concurrency failure makes no false filesystem claim;
2. `durability_unconfirmed` makes no false filesystem claim while the correct
   target remains present;
3. unreadable replay/winning-result paths distinguish the current attempt from
   already-recorded state and make no false broad claim;
4. HTTP and Foundry notification rendering preserve the truthful wording; and
5. a repository-wide regression check catches reintroduction of the prohibited
   phrase in a post-store path without incorrectly banning truthful explanatory
   documentation that quotes the old defect.

Update the remediation submission, review request, operations documentation and
project-management records so they no longer assert that I-1 was fully fixed by
the superseded remediation.

### S-B-2 remains open — artifact-root pathname replacement race

`FilesystemArtifactStore` validates the configured root with pathname-based
`lstat`, then later creates temporary files, opens artifacts, replaces targets
and syncs the directory through the pathname. It does not retain a trusted root
directory descriptor or enforce trusted, non-writable ancestors. If another
account can rename entries in a writable parent, the checked root can be
replaced after `_ensure_root()` succeeds and subsequent operations can be
redirected.

The relevant current locations are approximately:

- `adapters/artifacts/filesystem.py::_ensure_root()`;
- temporary creation in `store()`;
- target verification and `os.replace()` in `store()`;
- `_read_trusted()`; and
- `_fsync_directory()`.

Required security outcome:

- The directory used for create, open, verification, publication and directory
  `fsync` must be the same trusted directory object whose type, owner and mode
  were checked; a pathname swap after validation must not redirect any
  operation.
- Prefer descriptor-relative POSIX operations anchored to a directory FD opened
  with the available Linux protections (`O_DIRECTORY`, `O_NOFOLLOW`, and
  `dir_fd`/equivalent APIs). Do not merely add another pathname check; that
  leaves the same check/use race.
- Define descriptor ownership and lifetime clearly. Avoid leaks on startup,
  request failures and object teardown. If a long-lived descriptor is used,
  provide an explicit lifecycle that composition can close; do not rely only on
  nondeterministic garbage collection.
- Re-check the trusted root state at startup and per store as required by the
  accepted policy, using the anchored descriptor. Decide deliberately whether
  reads also re-check it and document the result.
- Continue to refuse rather than repair unsafe owner/mode/type state.
- Continue to reject symlinked configured paths and symlinked artifact names,
  verify existing files through the descriptor actually read, keep artifacts
  private and service-owned, verify content against the checksum name, preserve
  content-addressed idempotency, and make the publication plus directory sync
  durable.
- Preserve the rule that a failed durability acknowledgement does not delete a
  correctly published target and that retry re-establishes the guarantee.
- Do not weaken containment, move artifacts into the repository, expose paths,
  or add list/delete/open application capabilities.
- If the Python/runtime APIs cannot provide the required anchored semantics,
  stop and present Peter with the exact constraint and alternatives rather than
  silently accepting a residual race.

Add deterministic regression tests that simulate replacement of the configured
root pathname after validation. They must prove that:

1. a store cannot be redirected to the replacement directory;
2. a load cannot read an artifact from the replacement directory;
3. an existing checksum target cannot be swapped through a symlink or other
   pathname race between validation and read;
4. publication and directory `fsync` operate on the anchored trusted directory;
5. unsafe root owner/mode/type changes still fail closed without repair;
6. descriptors are closed on normal completion and every injected failure; and
7. retry after `durability_unconfirmed` still succeeds without duplicating or
   destroying the artifact.

Do not require root privileges or create a real second POSIX account in the
automated suite. Use controlled directory renames, replacement directories,
monkeypatching and descriptor inspection with synthetic data.

Update `docs/operations/foundry-snapshot-submission.md`, `.env.example` and the
remediation records to state the actual enforced storage contract. Ensure the
documented deployment path satisfies it. Do not claim cross-account resistance
beyond what the implementation and tests establish.

## Findings not reopened by this prompt

- B-1 and S-I-1 appear remediated by construction and automated tests. The real
  browser positive and negative check in operations §8.2 remains not run and
  must remain explicitly outstanding.
- I-2 appears remediated, but its durability behavior must remain intact while
  fixing both findings above.
- S-B-1 is independently confirmed as remediated in code, subject to the
  outstanding second-client observation in operations §8.1.

Codex independently inspected only installed Foundry **application source** at
`/home/foundry/foundry1/foundry` and confirmed for Foundry 14.365 that:

- the per-user world payload calls unfiltered `db.Setting.dump()`;
- `Setting.dump()` accepts only an optional sort argument;
- world and user scopes use the delivered `WorldSettings` collection;
- client scope is browser `localStorage`; and
- `SETTINGS_MODIFY` controls modification, not read confidentiality.

Therefore no Foundry setting scope is confidential storage for the reusable
bearer, and the per-submission credential design remains justified. Do not move
the credential back into any setting, flag, document, local/session storage or
other Foundry-persisted state. Do not inspect world storage, LevelDB,
compendiums, or player data.

## Verification and handoff

Run narrow tests first, then the full configured suites. At minimum report exact
commands and results for:

```bash
(cd foundry-module && node --test "tests/*.test.mjs")

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q -rs

./venv/bin/python -m compileall -q application adapters domain tools tests migrations
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/alembic check
git diff --check

for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done
```

Run configured formatting, linting and type checking if they exist. If none is
configured, state that accurately and do not install tools merely to make the
handoff look complete.

Review the final diff for secrets, raw artifacts, Actor/player data, unsafe
logs, descriptor leaks, generated files, unrelated changes and migration drift.
Use synthetic fixtures only. Do not contact live Discord, Sheets, Foundry or a
production database.

Produce an amended remediation submission and a self-contained re-review
request mapping each blocking finding to changed files, named tests, operational
effects, recovery behavior, residual risks and evidence not established. Ask
for two independent re-reviews:

1. implementation re-review of I-1 and preservation of I-2; and
2. security re-review of S-B-2 and preservation of S-B-1/S-I-1.

Do not state that a finding is closed or that a gate passed. Peter records those
decisions after independent recommendations and the outstanding supervised
checks.
