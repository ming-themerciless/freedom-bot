# Closed defect — NFC key collision in the canonical encoder

Raised: 2026-08-10, by Claude, while remediating independent-review finding I-1
Status: **Closed 2026-08-10 — fixed in both implementations, exporter `1.0.6`,
change-log [C-16](../project-management/change-log.md). No gate is closed by it,
and it carries no independent review.**
Severity proposed: **Important** — potential silent data loss in the exporter,
plus a second cross-language disagreement. Not Blocking only because
reachability against real Foundry data is undemonstrated (see below).

Found incidentally, outside the scope of findings B-1 and I-1, while reading
`foundry-module/scripts/canonical.js` for the array-index boundary. It was
recorded rather than fixed at the time because fixing it changes the bytes of the
installed, rehearsed `1.0.5` build, which the version identity control (CL3-I-2)
forbids doing silently. The independent reviewer subsequently held that leaving
the regression tests as `todo`/`xfail` left the release vulnerable, and the
maintainer directed that both implementations be fixed together, the refusal code
added and the exporter version bumped before Phase 2 closes. That is what C-16
does; the record below is left intact as the description of the defect, with the
resolution appended at the end.

## The defect

`normalise` sorts an object's keys by their **pre-NFC** form and then inserts
them under their **post-NFC** form:

```js
for (const key of Object.keys(value).sort(compareCodePoints)) {
  result[key.normalize("NFC")] = normalise(value[key], `${path}.${key}`, nested);
}
```

Two distinct keys that share an NFC form therefore write to the same property of
`result`. The second write wins and **the first value is silently dropped**.

That is precisely the outcome the same file's header docstring says the contract
exists to prevent:

> A value quietly disappearing from an Actor export is precisely the class of bug
> this contract exists to make impossible, so every unsupported value is a
> refusal instead.

It is also the outcome contract §1.1 makes a refusal everywhere else: an
`undefined` reaching the encoder is `undefined_value`, an `undefined` array
element is `undefined_array_element`. A key collision is the one path that drops
data without refusing.

## Reproduction

`é` as U+00E9 (composed) and as U+0065 U+0301 (decomposed) are distinct
JavaScript keys with the same NFC form.

```bash
node --input-type=module -e "
import {canonicalBytes} from './foundry-module/scripts/canonical.js';
const composed = 'é', decomposed = 'é';
const doc = {[composed]: 'first', [decomposed]: 'second'};
console.log('input keys :', Object.keys(doc).length);
console.log('output     :', new TextDecoder().decode(canonicalBytes(doc)));
"

./venv/bin/python -c "
from application.foundry.parser import canonical_bytes
doc = {'é': 'first', 'é': 'second'}
print('input keys :', len(doc))
print('output     :', repr(canonical_bytes(doc).decode()))
"
```

Observed **on `1.0.5`, before the fix**. Re-run today, both commands refuse with
`nfc_key_collision` instead of printing an output line:

```text
JavaScript  input keys : 2
JavaScript  output     : {"é":"first"}          ← "second" is gone
Python      input keys : 2
Python      output     : {"é":"second","é":"first"}
```

Two separate problems, and the second is the same family as finding I-1:

1. **The exporter loses a value.** Which key survives is decided by the
   code-point order of the *pre*-NFC forms, not by anything about the data. It
   does not refuse, warn, or record that anything happened.
2. **The verifier does not normalise keys at all**, so it emits a document
   carrying the same key twice. That is not a canonical form of anything, and it
   disagrees with the exporter for every non-NFC key — a third cross-language
   disagreement after RA-2 and I-1.

## Reachability — stated honestly

**Not demonstrated against real data, and not claimed.** Neither Rehearsal A nor
Rehearsal B is evidence either way: neither artifact was examined for non-NFC
object keys, and the flag they did carry (`canonical_encoding`) cannot detect
this — the exporter's output is self-consistent, so the loss happens before
anything is compared.

Foundry document keys are predominantly schema field names and document IDs,
which are ASCII. The candidates for a non-ASCII key are `flags` namespaces,
module-authored flag keys, and any user- or system-supplied map key such as a
custom scale-value or resource identifier. Whether the deployed dnd5e `5.3.3`
world contains one is **unknown and was not investigated**, because doing so
would mean reading real Actor data, which the review constraints forbid for this
work.

The defect is worth fixing regardless of current reachability: the contract's
whole claim is that data cannot disappear from an export without a refusal, and
this is a path where it can.

## Why it was not fixed when it was found

- The fix belongs in `canonical.js`, and editing it changes the bytes of the
  installed and rehearsed `1.0.5` build. **CL3-I-2 exists precisely because two
  behaviourally different builds once shared a version string**, and
  `exporter.version` reaches checksum-bearing audit history.
- Fixing only the Python verifier would replace one cross-language disagreement
  with a different one. The two halves have to move together.
- It is outside findings B-1 and I-1, which are what the package was returned
  for. Widening the remediation would put an unreviewed behaviour change into a
  package already waiting on an independent re-review.

## Proposed fix, for whoever schedules it

Normalise **before** sorting, and refuse a collision rather than resolving it:

1. map each own key to its NFC form;
2. if two distinct source keys produce the same NFC form, throw a
   `CanonicalError` with a new code — `nfc_key_collision` — naming the path and
   never the key's value;
3. sort the normalised keys with `compareCodePoints`;
4. insert.

A refusal is the right resolution, not a merge: the two source keys are
different properties of a Foundry document, and no rule in this repository says
which one an operator meant. It matches how §1.1 treats every other
inexpressible value.

The verifier needs the matching change — normalise keys to NFC in
`_canonical_key_order`/`_ordered`, and treat a collision as a
`SnapshotRejected`. `parser.py`'s new refusal code must be added to
`ARTIFACT_REFUSAL_CODES` in `application/foundry/submission.py`, which
`tests/test_snapshot_submission.py` already enforces by walking both modules'
syntax trees.

Both changes together are a module version bump, a change-log entry, and a
cross-language boundary test in the shape C-12 established.

## Tracking, and how it was closed

Two tests held this open so it could not be forgotten, and neither failed the
suite while it was open:

- `foundry-module/tests/canonical.test.mjs` — a `{ todo: true }` test asserting
  the collision is refused;
- `tests/test_snapshot_parser.py` — a `@pytest.mark.xfail(strict=True)` test
  asserting the verifier does not emit a duplicate key.

Both were written against the **corrected** behaviour, so both started passing
the moment the defect was fixed. Both holds are now removed: the node test runs
as an ordinary test and the strict `xfail` is gone, which is what the strict
marker was there to force.

## Resolution — 2026-08-10, change-log C-16

Exactly the proposed fix above, in both halves at once:

- `canonical.js` maps each own key to its NFC form **before** sorting, refuses
  two distinct source keys that share one form with a new `CanonicalError` code
  `nfc_key_collision` naming the path and never a value, then sorts the
  normalised keys with `compareCodePoints` and inserts. The module is
  **`1.0.6`** in both manifests; `1.0.5` is superseded, and `1.0.6` was installed
  on `foundry1` and `foundry3` on 2026-08-10
  ([record](phase-2-module-1.0.6-install-2026-08-10.md)) though neither instance
  has been restarted yet. For every document whose keys are already NFC —
  every ASCII key, and so every artifact either rehearsal produced — the emitted
  bytes are unchanged.
- `parser.py` normalises keys to NFC in `_ordered` (via a new `_nfc_keys`) and
  raises `SnapshotRejected("nfc_key_collision", …)`; `parse_snapshot` re-raises
  it with the artifact's checksum, so the refusal is auditable against the exact
  bytes. It also normalises **string values**, which §1 always required and the
  verifier never did — without that the two implementations still disagreed for
  a decomposed value.
- `nfc_key_collision` is declared in `submission.ARTIFACT_REFUSAL_CODES` and in
  the module's `SERVER_ARTIFACT_CODES`; `tests/test_snapshot_submission.py`
  enforces that all three agree.
- The contract gains **§1.2**, which states the refusal, why a merge is not
  available, and that a *single* non-NFC key is normalised rather than refused.
- `canonical.js`'s header comment about key order — carried against the next
  version bump by C-12 — is corrected in the same build.

Cross-language agreement is asserted in `tests/test_exporter_contract.py` in the
shape C-12 established: five NFC boundary documents through the shipped exporter
and the real verifier, and one document both must refuse with the same code.

Reachability against real data is still **not** demonstrated and still not
claimed; see the section above. What changed is that the export can no longer
lose a value without saying so.
