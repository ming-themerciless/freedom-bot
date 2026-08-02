# Sheet character identity import

The Phase 2 importer copies **character identity only** — short name, long
name, level and the active flag — from the `Characters` tab into PostgreSQL. It
does not import money, downtime, skills, items or bastions, and it does not
create character access: who owns a character is a Guild Council decision
([OD-13], [OD-37]), not something the Sheet's player-name column settles.

The Sheet is opened **read-only**. The tool reads one values range and never
calls `batch_update`; the only write it can perform is to the database.

## Sheets credential

The importer depends on a one-method port — read an A1 range — and selects the
narrowest credential the deployment offers:

| `SHEET_READONLY_SERVICE_ACCOUNT_JSON` | What the run uses |
|---|---|
| set | A credential scoped to `.../auth/spreadsheets.readonly` |
| unset | The bot's shared `.../auth/spreadsheets` credential, with a warning on stderr |

The fallback is not a failure: refusing to run would block the import for a
reason the operator cannot fix from the command line. But the shared credential
carries write authority over every character in the Sheet, and the importer
needs none of it.

**Deployment step, not a code change.** Narrowing it requires a second Google
service account with **Viewer** on the spreadsheet, its JSON placed in
`SHEET_READONLY_SERVICE_ACCOUNT_JSON` in the importer's environment only. The
live bot's `connectors.sheets` and its existing credential are untouched by
this and must stay that way while the Sheet is authoritative.

## Running it

```bash
DATABASE_URL='postgresql+psycopg://__APP_USER__@/freedom_dev' \
APP_ENVIRONMENT=development \
  ./venv/bin/python -m tools.import_sheet_characters
```

That is a **dry run**: it reads, plans, writes into a transaction and rolls
back. Add `--apply` to commit. `--tab` and `--range` exist for a differently
named tab; the defaults are `Characters` and `A1:AL150`, and the range must
start at the header row.

The tool does not read `.env`. `DATABASE_URL` is given on the command line so
the target database is visible in the command an operator types, rather than
inherited from a file — the same reasoning as
[database-development.md](database-development.md). `APP_ENVIRONMENT` still
decides which database *name* is permitted, so a development run cannot reach
the production database.

### Exit codes

| Code | Meaning |
|---|---|
| `0` | Clean. A dry run planned without errors, or an apply committed. |
| `1` | The run reported errors and wrote nothing. A dry run that *would* fail exits this way too, so a rehearsal can be scripted without parsing the report. |
| `2` | Refused before importing began: the database target, the Sheets credential or the Sheet layout. |
| `3` | The Sheet could not be read — network, credential, quota or permission. |
| `4` | The database could not be reached or refused the work. |
| `5` | A conflict: a concurrent import, or a row edited while the run was in progress. |

Codes `3`–`5` print a short instruction and nothing else. They deliberately
carry no connection string, credential, SQL statement, Google response body or
traceback: an import is run from a terminal whose scrollback and CI log are not
a safe place for any of those.

**Turning logging up does not recover the detail, by design.** At every level,
including `DEBUG`, the only diagnostic recorded is a fixed failure category and
the exception's *class* name — `expected failure category=database_unavailable
exception_type=OperationalError`. Debug logging is still logging: it lands in
journald, a CI job log or a log collector, all of which outlive the run, and
SQLAlchemy's and Google's exception text carries the DSN, the SQL statement and
fragments of the credential document. The category and the class name are enough
to tell one failure apart from another; anything beyond them belongs in a
debugger against synthetic input. See `adapters/safe_logging.py`.

**A refused credential (`2`) follows the same rule**, and for a sharper reason:
Google's own errors quote the offending field back — a malformed `private_key`
produces `InvalidValue("<the value> could not be converted to unicode")` — so
printing the cause would print part of the key. `Sheet credential refused:` is
therefore always followed by one of these fixed sentences:

| What you will see | What to check |
|---|---|
| `…must be valid single-line JSON.` | The value was truncated or mangled by the shell. Re-minify the key file onto one line and quote it. |
| `…must be a JSON object holding the service-account key fields.` | It parsed, but into an array, a string or a number rather than the key document. |
| `…is valid JSON but is not a usable service-account credential.` | It parsed as an object, but Google refused it: required fields missing (`client_email`, `token_uri`, `private_key`), a field of the wrong type, or a `private_key` that is not a key. Re-copy the unedited key file. |
| `…the Google API libraries are not installed…` | The variable is set on a host without the dependencies. `google-auth` and `google-api-python-client` are separate distributions and **either** missing half produces this message, including a partial install that has one but not the other. Install the project requirements, or unset the variable to fall back to the shared credential. |

None of them prints the document, the service-account address or the project,
and neither does any log line at any level: Google's message is discarded rather
than recorded, because it can quote the key. If a credential has to be diagnosed
in detail, do it against a **synthetic** key in a debugger, never by turning up
logging on a host holding the real one.

Every one of these codes means **nothing was written**. The unit of work rolls
back and closes its session on any exception leaving its block, so a failure is
never a partial import.

## What it guarantees

- **Idempotent.** A row is matched through `sheet_row_mappings(sheet_tab,
  row_index)`, so re-running an unchanged import reports every row as
  `unchanged` and writes nothing. The mapping is a database constraint, not a
  convention.
- **All-or-nothing.** One run is one transaction. If any row is blocked, the
  whole run is rolled back — including rows that were individually valid.
  There is no partial import to reconcile afterwards.
- **A dry run is a real rehearsal.** It performs the same reads, the same
  writes and hits the same constraints, then rolls back. The one thing it
  cannot promise is the `character_id` of a row it would create: a rolled-back
  transaction reserves no identity, so applying afterwards generates new ids.
- **Audited.** Every created or updated character writes an `audit_events` row
  with `source='import'`, `actor_capability='system'` and the run's correlation
  id, so one import can be read back as a unit.
- **Nothing is deleted.** A character whose Sheet row has disappeared is
  reported, never removed or deactivated.
- **Identity is never inferred.** A row's character comes from its stored
  mapping and nothing else. The importer does not adopt a character by name, does
  not re-key a mapping, and does not apply a mapped name change — see *A renamed
  character is not imported automatically* below.
- **One comparison rule.** The parser, the import service and both character
  repositories decide "is this the same name?" through a single policy in
  `domain/names.py`. Two layers folding names differently is what let a rename
  pass as a re-capitalisation; see *How two names are compared*.

## Reported codes

Errors block the run. Warnings do not.

| Code | Severity | Meaning and what to do |
|---|---|---|
| `required` | error | The short name is empty. Fix the Sheet row. |
| `invalid_integer` | error | The level is not a whole number. |
| `out_of_range` | error | The level is outside 1–20. |
| `invalid_boolean` | error | `Active` is not `1/0` or `true/false`. |
| `duplicate` | error | Two rows claim one name under the comparison rule below. The importer never resolves this by first-match-wins. |
| `unmapped_name_collision` | error | An unmapped row names a character the platform already holds. Usually a moved row. Decide whether to re-key the mapping or whether this is genuinely a second character, then act deliberately. |
| `row_identity_shift` | error | A mapped row now carries a different name, and the character it maps to appears elsewhere in the same import — the signature of an inserted or deleted Sheet row shifting everything below it. Re-key the mappings before importing. |
| `mapped_name_change` | error | A mapped row's name changed, and nothing else in the run says why. The importer does not apply a mapped name change: reconcile the mapping and the identity deliberately, then import again. See below. |
| `name_collision` | error | A mapped row would rename or re-spell its character into a name a *different* character already claims. Reported for a change of capitalisation alone as well, because that change is looked up like any other. Resolve the duplicate first. |
| `dangling_mapping` | error | A mapping points at a character that no longer exists. Investigate before re-importing; the importer will not silently re-create it. |
| `owner_unresolved` | warning | The row has no player name, so Council has nothing to reconcile ownership against. The character still imports. |
| `absent_from_source` | warning | A mapped row was not in this read. The character is left untouched. |

A `SheetLayoutError` (exit `2`) means the header row no longer matches the
column map in [sheet-inventory.md §3]. The importer refuses the whole read
rather than risk writing one character's data onto another. Re-check the
column map before changing anything here.

## A renamed character is not imported automatically

The Sheet row is an import key, never an identity ([ADR 0005]). But the Sheet
also has no *stable* identity of its own: a row carries a position and a name,
and both are editable in the same sitting.

So when a mapped row's name changes, there are always at least two readings:

- the character the mapping points at was **renamed in place**; or
- the **rows moved** — an insert, a delete, a drag, a sort — and the character
  who used to sit at that row was renamed too, so its old name is nowhere to be
  seen.

Sometimes the run itself says which. If the mapped character's old name turns up
at another row in the same import, the rows demonstrably moved
(`row_identity_shift`). If the new name is already held by a different
character, the change would leave two characters answering to one name
(`name_collision`). Both block.

**When the run says nothing, the readings are not merely hard to tell apart —
they are identical.** Take two mapped rows, swap them, and rename both displaced
characters to names the platform has never held:

| | Row 3 | Row 4 |
|---|---|---|
| Mapped to | character A, `Test Smith A` | character B, `Test Smith B` |
| Now reads | `Test Fresh X` | `Test Fresh Y` |

Nothing was added, nothing removed, nothing malformed, no mapping dangles,
neither old name appears elsewhere and neither new name collides. That input is
*byte-for-byte* what two ordinary renames produce — but by physical row it means
character **B** is now `Test Fresh X` and character **A** is now `Test Fresh Y`,
the exact opposite of what the mappings say. No row-count, index or name check
can separate them, because there is nothing left in the data to separate.

**The importer therefore never applies a mapped name change.** It reports
`mapped_name_change` and the run stops, which is the general case of the two
codes above. Applying it would commit one of two readings on a coin toss, and
the wrong one writes a character's identity onto another player's character
while the audit row records an ordinary rename — a corruption nothing
afterwards can detect.

What still imports without a human:

- **a new row** — an unmapped row whose name no character already claims;
- **long name, level and the active flag** — whenever the short name is
  unchanged;
- **a change of capitalisation alone** — and only after the same collision
  lookup every other spelling change gets. See the next section for exactly
  which changes count.

The trade is deliberate. A refused rename costs somebody a reconciliation; a
wrong one costs a character its identity, permanently and invisibly.

## How two names are compared

Everything above depends on one question — *are these two names the same name?*
— and the importer answers it in exactly one place, `domain/names.py`. The Sheet
parser, the import service and both character repositories call it. Nothing
folds a name for itself.

There are two comparisons, and they are deliberately different:

| Comparison | What it decides | Rule |
|---|---|---|
| **Capitalisation only** | whether a spelling change may be applied without a human | Unicode NFC, then `lower()` |
| **Identity claim** | whether another character already holds the name | Unicode NFC, then `casefold()` |

The identity claim is the **wider** of the two, on purpose. A false collision
costs a reconciliation; a missed one duplicates a player. The capitalisation
exemption is the **narrower** one, on the same reasoning in the other direction:
a change wrongly refused costs a reconciliation, a change wrongly applied costs
a character its identity. Both errors therefore land on *refuse*.

Worked examples, with the stored name on the left:

| Stored | Sheet now reads | Decision |
|---|---|---|
| `Test Smith A` | `Test Smith A` | unchanged; no lookup, no write |
| `Test Smith A` | `TEST SMITH A` | capitalisation only → applied, **if** no other character claims it |
| `Test Smith A` | `TEST SMITH A`, while another character is `test smith a` | `name_collision` — the whole run stops |
| `Test Straße` | `Test STRAẞE` | capitalisation only — `ẞ` is the capital of `ß` |
| `Test Straße` | `Test STRASSE` | **`mapped_name_change`** — one letter became two; this is a rename, not a re-capitalisation |
| `Test Ölrún` | `Test Ölrún` typed with combining accents | the same name in a different Unicode encoding → applied like a re-capitalisation |
| `Test Işık` | `Test IŞIK` | `mapped_name_change` — dotted and dotless `i` are different letters, and the importer applies no language-specific rule |
| *(no character)* | `Test STRASSE`, while `Test Straße` exists unmapped | `unmapped_name_collision` — creation uses the identity claim, so a normalisation difference cannot mint a second character |

**Why the sharp `s` matters enough to write down.** `casefold()` expands `ß`
into `ss`; `lower()` does not. An earlier revision exempted a mapped-name change
as "capitalisation only" using `casefold()` while the platform looked collisions
up using `lower()`. `Test Straße` could therefore be imported as `Test STRASSE`,
be waved through as a re-capitalisation, skip the collision lookup on the
strength of that, and commit **two characters holding the identical display
name** with no issue reported at all. The two folds are now used for two
deliberately different questions, and the capitalisation rule is defined so that
nothing it exempts can escape the collision lookup.

The comparison is language-independent by design. The importer does not apply
Turkish, Azerbaijani or any other locale tailoring, so `I` lowercases to `i`
everywhere. If the community ever needs a name where that is wrong, it is a
maintainer decision recorded as a rule, not a fold changed in passing.

**The database does not enforce this.** `characters.display_name` still carries
no uniqueness constraint, so the importer's refusal is the only thing preventing
a duplicate. Because the comparison is not one PostgreSQL's `lower()` can
express, `find_by_display_name` reads the `characters` rows and compares them in
Python. That is a sequential scan per lookup, which is bounded and acceptable
for a bootstrap population of roughly 150 characters in an occasional operator
tool. Above roughly 2,000 characters, or as soon as a web or Discord request
path calls it, the comparison belongs in the schema: a stored, indexed identity
key plus a decided uniqueness rule. That is a migration and a policy decision,
and it is recorded as an open question rather than made here.

**Reconciling is a deliberate, separately reviewed action, and the importer has
no command for it yet.** A genuine rename, like a moved row, currently blocks
with no in-platform remedy: the mapping and the identity have to be settled
outside this tool before the next automatic import can proceed. That gap is
recorded for the maintainer in
[`docs/review/phase-2-submission.md`](../review/phase-2-submission.md) rather
than closed here, because re-keying a mapping is exactly the guess this refusal
exists to prevent, and it needs an authorization and audit story of its own.

## Rollback

A dry run needs no rollback. An applied run is recoverable by restoring the
backup taken before it, per
[database-development.md](database-development.md); the Sheet is untouched and
remains authoritative throughout Phase 2, so re-importing after a restore is
safe. Because the import is idempotent, re-running it is also the normal way
to recover from a partial *failure* — of which there should be none, the
transaction being all-or-nothing.

[ADR 0005]: ../adr/0005-identifier-and-quantity-representation.md
[OD-13]: ../discovery/open-decisions.md
[OD-37]: ../discovery/open-decisions.md
[sheet-inventory.md §3]: ../discovery/sheet-inventory.md#3-column-map--characters
