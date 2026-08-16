# Phase 3 deferred settings-construction validation gap

Date recorded: 2026-08-15
Status: open issue for later scoped remediation; no implementation change in this record
Tracking: RAID I-10

> **Remediation submitted 2026-08-15, later the same day.** The finding text below
> is preserved verbatim and **nothing here is closed**. Implementation and
> evidence are in
> [`phase-3-p3-1-settings-construction-validation-remediation-submission.md`](phase-3-p3-1-settings-construction-validation-remediation-submission.md),
> which also closes the explicit non-resolution recorded in the last section:
> the shared session validator's exact-type rule was corrected first, in the same
> package. I-10 remains **open** pending fresh independent implementation review,
> a distinct security-focused pass, an availability review of the pool and worker
> bounds, and maintainer acceptance.

## Finding

Five frozen, public configuration dataclasses currently have no construction-time
validation:

- `RateLimitSettings`;
- `BoundsSettings`;
- `WebAuthnSettings`;
- `DatabasePoolSettings`; and
- `WorkerSettings`.

`WebSettings.from_environment()` validates their configured strings before it
constructs them. That protects the ordinary environment-loading path, but it does
not make these public types valid by construction. Direct construction,
`dataclasses.replace()` or an inherited/subclass attribute read can supply policy
values that the relevant service, middleware, database engine or future worker
then trusts.

This is the same authority-boundary shape found repeatedly in the session-policy
work: validation performed by one producer is not an invariant of a public value
object or of a later derivation boundary. This record does not claim that an
untrusted HTTP caller can directly construct these objects. It records that the
supported Python composition boundary does not enforce the accepted contract and
that tests, operator code and future composition changes can create an invalid
graph without bypassing frozen-object protections.

## Impact and required timing

| Settings type | Principal impact | Required no later than |
|---|---|---|
| `RateLimitSettings` | Authentication and recovery throttles can be weakened, disabled or given unintended windows | Before the P3.G1 security control is accepted, unless the Acceptance Authority explicitly assigns a narrower prerequisite gate after independent review |
| `BoundsSettings` | Request-size, trusted-proxy, membership-cache/grace, audit-page and polling controls can be weakened; consequences include security and resource exhaustion | Before the corresponding P3.1/P3.2 middleware or authorization control is accepted |
| `WebAuthnSettings` | Recovery-grant lifetime and relying-party/origin/user-verification relationships may be inconsistent with the accepted WebAuthn policy | Before break-glass/WebAuthn acceptance at P3.G1 |
| `DatabasePoolSettings` | Pool and statement bounds can cause resource exhaustion or service unavailability | Before P3.G1 operations acceptance and again at staging rehearsal |
| `WorkerSettings` | Lease, heartbeat, attempt, queue and artifact bounds can become unsafe once worker behavior consumes them | Before P3.3 implementation starts; P3.1 currently reads only `enabled` |

The owning remediation must confirm the exact gate assignment against the current
delivery plan. It must not silently broaden the session-policy remediation or
claim these fields are corrected because their environment reader is correct.

## Required remediation contract

1. Inventory every field, accepted type, floor, ceiling, exact value and
   cross-field relationship, citing its `N-nn`/`S-nn` contract and every runtime
   consumer.
2. Define each invariant once at runtime and call that definition at every public
   construction and derivation boundary. Do not copy ordering comparisons between
   the reader, dataclass and consumer.
3. Where the contract requires an integer, accept an exact built-in integer with
   `type(value) is int`. `isinstance(value, int)` is insufficient: it admits
   `bool` and custom `int` subclasses whose comparison methods can lie.
4. Read subclassable inputs once into locals, validate those locals, and store or
   consume those same locals. Do not validate one attribute read and use another.
5. Enforce cross-field relationships at the type that owns the relationship; for
   example, a default page size cannot exceed its maximum and worker heartbeat,
   lease and timeout relationships must match the accepted worker contract.
6. Preserve aggregated, value-redacting `ConfigurationError` behavior at the
   environment boundary. Construction-boundary validation must not cause the
   reader to stop after the first invalid environment variable.
7. Prefer a closed or derived construction model when a caller-supplied policy
   object would create a second source. Do not add guards around an authority that
   remains independently constructible.

## Mandatory evidence

For every affected field or relationship, tests must cover:

- valid direct construction and `dataclasses.replace()` at both accepted
  boundaries;
- refusal of zero, negative, above-ceiling, float, non-finite float, `bool`, and a
  comparison-overriding `int` subclass where applicable;
- a subclass whose construction observes a valid value and whose later read
  returns an invalid value, with the derivation read count asserted;
- environment loading with several simultaneous failures, proving one aggregated
  error names every variable and echoes none of their values;
- the real consumer behavior: limiter decisions, body/proxy/membership bounds,
  WebAuthn/recovery behavior, engine pool arguments, and worker lease/attempt
  behavior as those consumers become active;
- a falsification run demonstrating that the new tests fail against the previous
  reader-only construction model while the pre-existing suite's result is stated
  honestly; and
- narrow, full portal and applicable PostgreSQL evidence, followed by independent
  implementation and security/operations review in proportion to impact.

## Explicit non-resolution

This issue is not fixed by the session numeric-policy shared validator. That
validator itself must separately refuse comparison-overriding `int` subclasses
before its current remediation can close. Reusing it for these five settings
without first correcting its exact-type rule would reproduce the same N-66
bypass shape in additional controls.
