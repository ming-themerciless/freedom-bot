"""The evidence record, its closed outcome grammar, its deterministic
serialization, and the one classification rule every band shares.

## The two rules a record cannot be constructed around

**EH-R1 — the classifier is authoritative.** A record's `status` and `reason`
are *derived*, never asserted. `EvidenceRecord.for_case()` computes them from the
expected outcome, the observation, the identity assertion and the positive
control; direct construction and `from_mapping()` recompute them and **refuse any
supplied value that disagrees**. There is no unchecked and no test-only path,
because the check lives in `__post_init__` and every route into the class passes
through it. Evidence used at a security gate must not be able to contradict its
own observations, and the previous version — which accepted a caller-supplied
`status` and compared it with nothing — could serialize `passed` for an observed
refusal.

**EH-R2 — one closed outcome grammar.** `Outcome` previously said that exactly
one of `errno_name`, `exit_status` and `value` was meaningful and validated only
that a success carried no errno, so a failed result could carry `EPERM`, exit
status `0` and a value at once. It now carries an `OperationKind`, and each kind
admits **exactly one** result representation:

| Kind | Success | Refusal |
|---|---|---|
| `SYSCALL` | the call returned; no errno, no exit status, no value | `errno_name`, a symbolic name this platform knows |
| `COMMAND` | `exit_status == 0` | a non-zero `exit_status` |
| `OBSERVATION` | `value`, the thing that was read or derived | *not representable* — a read that failed is a `SYSCALL` refusal |

Everything outside that table is refused on construction and on deserialization,
and nothing is silently discarded: `from_mapping()` rejects an unknown key and a
missing one alike.

**EH-R2-1 — the positive control is a cross-record fact.** A record used to carry
both `positive_control_case_id` and a caller-supplied `positive_control_status`,
and classification trusted the status. An artifact could therefore hold a failed,
inconclusive or not-run control **and** a dependent record asserting
`positive_control_status="passed"`, and that record classified as passed;
recomputing the status from the same duplicated field proved nothing. The
duplicated status is now gone from the schema. A dependent record carries the
**control record**, `resolve_control_status()` reads the status off it, and
`deserialize_records()` resolves `positive_control_case_id` against the other
records in the same artifact before it constructs anything. Every reference that
would not be evidence — missing, duplicated, self-referential, cyclic,
cross-band, or naming a case the band did not declare a control — is refused, and
`CaseRole` makes "is this a control?" a declared, validated and serialized fact
rather than a case-name prefix or a sentence in a docstring.

## The classification rule

`classify()` checks the two ways a refusal can be meaningless **before** it reads
the refusal:

1. **The identity assertion.** Package plan §2.13.5c: *"Every case asserts its
   identity before it asserts its result … A case whose identity assertion fails
   is `inconclusive` — never a pass, never a refusal."*
2. **The positive control.** Stop conditions **10i** and **10m**: a negative case
   is interpreted only beside a control that succeeded and differs from it in
   exactly the one privilege, path, inode or mount under test. §2.13.2a Stage 1
   is that control for Stage 2, `S4-0` for `S4-2`, `E6` for `E4`, `E2` for `E1`.

Only when both hold is the observed result compared with the expected one. A
missing observation is `NOT_RUN`; it is never a pass.

## The serialization

`to_mapping()` produces a JSON-ready mapping with a fixed key order and no clock
reading of its own — every timestamp is an injected, explicit field.
`serialize_records()` renders a list with sorted keys and a trailing newline, so
two runs over the same observations produce byte-identical artifacts.
`deserialize_records()` reads them back **through the same constructor**, which is
what makes a tampered `status` or `reason` in a stored artifact a refusal rather
than a value.

`records_digest()` is SHA-256 over those exact bytes in the canonical, typed,
length-delimited encoding `application/idempotency.py` establishes.

## What a record deliberately does not carry

No file content, no environment, no credential, no command output beyond an
`errno` name, an exit status or a bounded read value, and no path outside the
disposable target. `detail` is a mapping of **scalars**, validated on
construction, so a caller cannot attach a blob of unrelated host configuration to
an artifact.
"""
from __future__ import annotations

import errno as _errno
import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from application.idempotency import canonical_request_hash

from . import EVIDENCE_SCHEMA_VERSION
from .errors import ObservationRefused


class Status(str, Enum):
    """The four outcomes a case may have. There is no fifth, and no default."""

    PASSED = "passed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"
    NOT_RUN = "not_run"


class CleanupState(str, Enum):
    """What the case left behind.

    `NOT_APPLICABLE` is for a case that creates nothing — a read, a parse, a
    derivation. `RESIDUE` is a stop condition (§2.13.2b state **S-B**): the
    harness reports the residue by absolute path and refuses to continue, and it
    never cleans or reuses it.
    """

    NOT_APPLICABLE = "not_applicable"
    CLEAN = "clean"
    RESIDUE = "residue"
    UNKNOWN = "unknown"


class CaseRole(str, Enum):
    """What a case *is*, with respect to the positive-control contract.

    This is EH-R2-1's "explicit validated contract". Before it, whether a record
    was a control, a read or a case needing a control was inferred from whether a
    caller had filled in two optional fields — and whether a *referenced* record
    was an admissible control was inferred from nothing at all, because the
    reference was never resolved. A case-name prefix (`C-…` for a control) and a
    sentence in a docstring are not a contract: `filesystem` and `identity` both
    have a case called `C-1`, and prose cannot be validated.

    The role is declared by the band, serialized with the record, and checked on
    every construction and every read-back:

    * `CONTROL` — this case **is** a positive control. It may be referenced by a
      dependent case in the same band, and it names no control of its own.
    * `DEPENDENT` — this case is interpreted only beside a control. It **must**
      name one, and the named record must exist in the same artifact, be in the
      same band, and be a `CONTROL`.
    * `STANDALONE` — a read, a derivation, or a case the design requires no
      control for. It names no control and may not be referenced as one.

    A `STANDALONE` is therefore inert in the reference graph in both directions,
    which is what makes it the safe role and `CONTROL` the one a band has to
    choose deliberately.
    """

    CONTROL = "control"
    DEPENDENT = "dependent"
    STANDALONE = "standalone"


class OperationKind(str, Enum):
    """Which result representation a case's operation produces.

    This is the closed grammar of EH-R2. It is a property of the *operation*, not
    of how it turned out, so an expected and an observed outcome that disagree
    about it disagree about what was run — which is a `FAILED` case, not a
    comparison this module tries to make anyway.
    """

    #: A syscall or libc call: it returned, or it set an `errno`.
    SYSCALL = "syscall"
    #: A process the harness would run: it exited with a status.
    COMMAND = "command"
    #: A value read or derived — a mask, a mount property, a digest, a mode.
    OBSERVATION = "observation"


#: What a record's `detail` may hold. Scalars only: a record is evidence about a
#: refusal, not a place to attach file content.
DetailValue = str | int | bool | None

#: A symbolic errno is `E` followed by upper-case letters and digits. The name is
#: additionally required to exist on this platform, so `EPERMM` and `EWOULDBLOCK`
#: are separated from each other rather than both being "a plausible string".
_ERRNO_NAME = re.compile(r"\AE[A-Z0-9]+\Z")


def _validate_errno_name(name: str) -> None:
    if not isinstance(name, str):
        raise ObservationRefused(
            f"An errno is a symbolic name, not {type(name).__name__}."
        )
    if not name.strip():
        raise ObservationRefused(
            "A refusal carries a symbolic errno name. A blank one records that "
            "something was refused without recording what refused it."
        )
    if not _ERRNO_NAME.match(name):
        raise ObservationRefused(
            f"{name!r} is not a symbolic errno name. The package plan's matrices "
            "are written in names — EPERM, EACCES, EROFS, ENOTTY — because a "
            "number invites a platform-dependent comparison."
        )
    if not hasattr(_errno, name):
        raise ObservationRefused(
            f"{name!r} is not an errno this platform knows. An evidence record "
            "naming a cause the kernel cannot produce is not evidence."
        )


@dataclass(frozen=True, slots=True)
class ObservedIdentity:
    """What the process that ran a case actually was, read from the host.

    Every field is what §2.13.5c's assertion contract requires a case to read from
    `/proc/self/status` and `prctl(PR_GET_SECUREBITS)` **before** the operation
    under test. `securebits` is separate because `/proc/self/status` does not
    report it.

    `groups` is a frozenset because the contract compares it *as a set*: the order
    `Groups:` prints is not part of the identity.
    """

    uid: int
    gid: int
    groups: frozenset[int]
    cap_prm: int
    cap_eff: int
    cap_inh: int
    cap_amb: int
    cap_bnd: int
    securebits: int
    no_new_privs: int

    _FIELDS = (
        "uid",
        "gid",
        "groups",
        "cap_prm",
        "cap_eff",
        "cap_inh",
        "cap_amb",
        "cap_bnd",
        "securebits",
        "no_new_privs",
    )

    def __post_init__(self) -> None:
        for name in ("uid", "gid", "cap_prm", "cap_eff", "cap_inh", "cap_amb",
                     "cap_bnd", "securebits", "no_new_privs"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ObservationRefused(
                    f"Identity field {name!r} is a whole number; this one is "
                    f"{type(value).__name__}. A mask that is not an integer "
                    "cannot be compared with a declared mask."
                )
            if value < 0:
                raise ObservationRefused(f"Identity field {name!r} cannot be negative.")
        if not isinstance(self.groups, frozenset):
            raise ObservationRefused(
                "Supplementary groups are compared as a set, so they are held as "
                "a frozenset rather than an order-bearing sequence."
            )
        for gid in self.groups:
            if isinstance(gid, bool) or not isinstance(gid, int) or gid < 0:
                raise ObservationRefused("A supplementary gid is a whole number.")

    def matches(self, expected: "ObservedIdentity") -> bool:
        return not self.differences(expected)

    def differences(self, expected: "ObservedIdentity") -> tuple[str, ...]:
        """Which fields disagree, so an `inconclusive` says why it is one."""
        return tuple(
            name
            for name in ObservedIdentity._FIELDS
            if getattr(self, name) != getattr(expected, name)
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "uid": self.uid,
            "gid": self.gid,
            "groups": sorted(self.groups),
            "cap_prm": _hexmask(self.cap_prm),
            "cap_eff": _hexmask(self.cap_eff),
            "cap_inh": _hexmask(self.cap_inh),
            "cap_amb": _hexmask(self.cap_amb),
            "cap_bnd": _hexmask(self.cap_bnd),
            "securebits": _hexmask(self.securebits),
            "no_new_privs": self.no_new_privs,
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ObservedIdentity":
        _require_exact_keys(raw, set(ObservedIdentity._FIELDS), "identity")
        return cls(
            uid=_require_int(raw["uid"], "uid"),
            gid=_require_int(raw["gid"], "gid"),
            groups=frozenset(_require_int(g, "groups") for g in raw["groups"]),
            cap_prm=_unhex(raw["cap_prm"], "cap_prm"),
            cap_eff=_unhex(raw["cap_eff"], "cap_eff"),
            cap_inh=_unhex(raw["cap_inh"], "cap_inh"),
            cap_amb=_unhex(raw["cap_amb"], "cap_amb"),
            cap_bnd=_unhex(raw["cap_bnd"], "cap_bnd"),
            securebits=_unhex(raw["securebits"], "securebits"),
            no_new_privs=_require_int(raw["no_new_privs"], "no_new_privs"),
        )


def _hexmask(value: int) -> str:
    """`0x200`, not `512`. Every mask in the package plan is written in hex and a
    reviewer comparing a record with §2.13.5c should not have to convert."""
    return f"0x{value:x}"


def _unhex(raw: object, name: str) -> int:
    if not isinstance(raw, str) or not raw.startswith("0x"):
        raise ObservationRefused(
            f"Serialized identity field {name!r} is a hexadecimal string such as "
            f"'0x200'; this one is {raw!r}."
        )
    try:
        return int(raw, 16)
    except ValueError as exc:  # pragma: no cover - re-raised as a refusal
        raise ObservationRefused(f"Field {name!r} is not a hexadecimal mask.") from exc


def _require_int(raw: object, name: str) -> int:
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ObservationRefused(f"Field {name!r} is a whole number.")
    return raw


def _require_exact_keys(raw: Mapping[str, Any], expected: set[str], what: str) -> None:
    """No key is silently discarded, and none is silently defaulted.

    An artifact read back with a field this schema does not know was written by a
    different harness, and one missing a field this schema requires was truncated.
    Both are refusals rather than a best-effort parse, because the whole purpose
    of reading an artifact back is to detect that it changed.
    """
    if not isinstance(raw, Mapping):
        raise ObservationRefused(f"A serialized {what} is a mapping.")
    keys = set(raw)
    unknown = sorted(keys - expected)
    missing = sorted(expected - keys)
    if unknown or missing:
        raise ObservationRefused(
            f"A serialized {what} does not match this schema: "
            f"unknown {unknown}, missing {missing}."
        )


@dataclass(frozen=True, slots=True)
class Outcome:
    """What a case's operation did, in the one form its `kind` admits.

    Use the factories — `Outcome.returned()`, `Outcome.refused()`,
    `Outcome.exited()`, `Outcome.read()` — rather than the constructor. The
    constructor is validated to the same grammar, so a direct construction that
    contradicts itself is refused; the factories exist because naming the four
    admissible shapes is clearer than assembling one and being told it is wrong.
    """

    kind: OperationKind
    succeeded: bool
    errno_name: str | None = None
    exit_status: int | None = None
    value: str | None = None
    #: Required, and required to be non-blank, when a `COMMAND` outcome calls a
    #: non-zero exit a success. There is no such case in the currently authorized
    #: bands; the field exists so that a future one has to say in the artifact why
    #: the exit status means what it claims, rather than being waved through.
    nonzero_success_rationale: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, OperationKind):
            raise ObservationRefused(
                "An outcome names the kind of operation that produced it."
            )
        if not isinstance(self.succeeded, bool):
            raise ObservationRefused("`succeeded` is a boolean.")

        present = {
            "errno_name": self.errno_name is not None,
            "exit_status": self.exit_status is not None,
            "value": self.value is not None,
        }
        carried = sorted(name for name, is_set in present.items() if is_set)
        if len(carried) > 1:
            raise ObservationRefused(
                f"An outcome carries one result representation; this one carries "
                f"{carried}. A record that is simultaneously an errno, an exit "
                "status and a value is ambiguous evidence, and the field the "
                "comparison ignores survives into the artifact anyway."
            )

        if self.exit_status is not None:
            if isinstance(self.exit_status, bool) or not isinstance(self.exit_status, int):
                raise ObservationRefused("An exit status is a whole number.")
            if not 0 <= self.exit_status <= 255:
                raise ObservationRefused(
                    f"An exit status is 0…255; this one is {self.exit_status}."
                )
        if self.value is not None and not isinstance(self.value, str):
            raise ObservationRefused(
                "An observed value is rendered as text at the point it is read, "
                "so the artifact records the reading rather than a Python object."
            )
        if self.errno_name is not None:
            _validate_errno_name(self.errno_name)
            if self.succeeded:
                raise ObservationRefused(
                    "An outcome cannot both succeed and carry an errno. A "
                    "successful call sets none, and recording one would make a "
                    "positive control indistinguishable from a refusal."
                )

        if self.kind is OperationKind.SYSCALL:
            if carried not in ([], ["errno_name"]):
                raise ObservationRefused(
                    "A syscall outcome is either a plain return or an errno; it "
                    f"carries no exit status and no value. This one carries {carried}."
                )
            if not self.succeeded and self.errno_name is None:
                raise ObservationRefused(
                    "A refused syscall records the errno that refused it. Without "
                    "one the outcome has no usable result representation, and a "
                    "refusal whose cause is unrecorded attributes nothing."
                )
        elif self.kind is OperationKind.COMMAND:
            if carried != ["exit_status"]:
                raise ObservationRefused(
                    "A command outcome is exactly an exit status; this one "
                    f"carries {carried}."
                )
            if self.exit_status == 0 and not self.succeeded:
                raise ObservationRefused(
                    "Exit status 0 is a success. Recording it as a refusal would "
                    "let a command that did what it was asked stand as evidence "
                    "that it was refused."
                )
            if self.exit_status != 0 and self.succeeded:
                if not (self.nonzero_success_rationale or "").strip():
                    raise ObservationRefused(
                        f"Exit status {self.exit_status} is a refusal unless a "
                        "documented evidence case requires the other reading, in "
                        "which case `nonzero_success_rationale` states which case "
                        "and why. No currently authorized band does."
                    )
        else:  # OperationKind.OBSERVATION
            if carried != ["value"]:
                raise ObservationRefused(
                    "An observation outcome is exactly the value that was read; "
                    f"this one carries {carried}. A read that *failed* is a "
                    "syscall refusal and is recorded as one."
                )
            if not self.succeeded:
                raise ObservationRefused(
                    "An observation that did not succeed produced no value to "
                    "observe. Record the failing read as a syscall refusal, whose "
                    "errno says why there is nothing here."
                )

        if self.nonzero_success_rationale is not None:
            if not isinstance(self.nonzero_success_rationale, str):
                raise ObservationRefused("A rationale is text.")
            if self.kind is not OperationKind.COMMAND or self.exit_status in (None, 0):
                raise ObservationRefused(
                    "`nonzero_success_rationale` explains a non-zero command exit "
                    "read as a success. It has no meaning on any other outcome, "
                    "and carrying it there would hide which case it excuses."
                )

    # -- the four admissible shapes -------------------------------------------

    @classmethod
    def returned(cls) -> "Outcome":
        """A syscall that returned without setting an errno."""
        return cls(kind=OperationKind.SYSCALL, succeeded=True)

    @classmethod
    def refused(cls, errno_name: str) -> "Outcome":
        """A syscall refused with a named, symbolic errno."""
        return cls(kind=OperationKind.SYSCALL, succeeded=False, errno_name=errno_name)

    @classmethod
    def exited(cls, status: int, *, nonzero_success_rationale: str | None = None) -> "Outcome":
        """A command that exited. Zero is a success; anything else is a refusal
        unless a documented case supplies a rationale for the other reading."""
        succeeded = status == 0 or bool((nonzero_success_rationale or "").strip())
        return cls(
            kind=OperationKind.COMMAND,
            succeeded=succeeded,
            exit_status=status,
            nonzero_success_rationale=nonzero_success_rationale,
        )

    @classmethod
    def read(cls, value: str) -> "Outcome":
        """A value read or derived — a mask, a mount property, a digest, a mode."""
        return cls(kind=OperationKind.OBSERVATION, succeeded=True, value=value)

    # -- rendering -------------------------------------------------------------

    def to_mapping(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "succeeded": self.succeeded,
            "errno_name": self.errno_name,
            "exit_status": self.exit_status,
            "value": self.value,
            "nonzero_success_rationale": self.nonzero_success_rationale,
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Outcome":
        _require_exact_keys(
            raw,
            {
                "kind",
                "succeeded",
                "errno_name",
                "exit_status",
                "value",
                "nonzero_success_rationale",
            },
            "outcome",
        )
        try:
            kind = OperationKind(raw["kind"])
        except ValueError as exc:
            raise ObservationRefused(
                f"{raw['kind']!r} is not an operation kind this harness records."
            ) from exc
        return cls(
            kind=kind,
            succeeded=raw["succeeded"],
            errno_name=raw["errno_name"],
            exit_status=raw["exit_status"],
            value=raw["value"],
            nonzero_success_rationale=raw["nonzero_success_rationale"],
        )

    @property
    def summary(self) -> str:
        if self.kind is OperationKind.SYSCALL:
            return "returned" if self.succeeded else str(self.errno_name)
        if self.kind is OperationKind.COMMAND:
            return f"exit {self.exit_status}"
        return f"value {self.value!r}"

    def result_signature(self) -> tuple[object, ...]:
        """Everything a comparison reads. The rationale is deliberately excluded:
        it explains a reading, and two runs that agree on the reading agree."""
        return (self.kind, self.succeeded, self.errno_name, self.exit_status, self.value)


def classify(
    *,
    expected: Outcome,
    observed: Outcome | None,
    identity: ObservedIdentity | None = None,
    expected_identity: ObservedIdentity | None = None,
    positive_control_status: Status | None = None,
    attribution_refusal: str | None = None,
) -> tuple[Status, str]:
    """Decide a case's status, checking the three prerequisites before the result.

    Returns the status and the reason, so the reason is part of the record rather
    than a log line. The order is the whole point:

    1. no observation                       -> `NOT_RUN`
    2. identity asserted and mismatched     -> `INCONCLUSIVE`
    3. a positive control that did not pass -> `INCONCLUSIVE`
    4. an unattributable observation        -> `INCONCLUSIVE`
    5. observed != expected                 -> `FAILED`
    6. otherwise                            -> `PASSED`

    `attribution_refusal` is §2.13.2a's attribution table reaching this function:
    an `EACCES` where Stage 1 has already proved discretionary access permits the
    operation says the *target* is mis-provisioned, and the section's answer is
    `inconclusive` rather than `failed` — a probe that cannot demonstrate the
    positive has no standing to interpret the negative, and it equally has no
    standing to call it a refusal of the wrong thing. It is a *reason string*
    rather than a flag so the artifact says why, it is computed by the band from
    the observation rather than chosen by a caller, and **it can only ever move a
    result away from `PASSED`** — no value of it produces a pass.

    A case with no positive control named is not thereby excused: naming one is
    the band's responsibility, declared as its `CaseRole`.
    `positive_control_status=None` means *this case is itself a control or a
    read*, which is why it is a distinct value from `Status.NOT_RUN`.

    This function takes the control's status rather than the control's record
    because it is the pure comparison and nothing else. **Where that status comes
    from is the load-bearing question**, and it is answered one level up by
    `resolve_control_status()`, which reads it off the control's own record. No
    caller of `EvidenceRecord` can supply it.
    """
    if observed is None:
        return Status.NOT_RUN, "No observation was supplied for this case."

    if expected_identity is not None:
        if identity is None:
            return (
                Status.INCONCLUSIVE,
                "The case declares an expected identity and asserted none. Its "
                "result is not attributable to that identity.",
            )
        if not identity.matches(expected_identity):
            fields = ", ".join(identity.differences(expected_identity))
            return (
                Status.INCONCLUSIVE,
                f"The constructed identity differs from the declared one ({fields}). "
                "Package plan §2.13.5c: an unasserted identity yields inconclusive, "
                "never a pass and never a refusal.",
            )

    if positive_control_status is not None and positive_control_status is not Status.PASSED:
        return (
            Status.INCONCLUSIVE,
            "The positive control did not pass "
            f"({positive_control_status.value}), so this refusal is not "
            "attributable to the boundary under test.",
        )

    if attribution_refusal is not None:
        return (Status.INCONCLUSIVE, attribution_refusal)

    if observed.kind is not expected.kind:
        return (
            Status.FAILED,
            f"Expected a {expected.kind.value} result; observed a "
            f"{observed.kind.value} result ({observed.summary}).",
        )

    if observed.result_signature() != expected.result_signature():
        return (
            Status.FAILED,
            f"Expected {expected.summary}; observed {observed.summary}.",
        )

    return Status.PASSED, f"Observed {observed.summary}, as expected."


def resolve_control_status(
    *,
    case_id: str,
    band: str,
    case_role: CaseRole,
    positive_control_case_id: str | None,
    positive_control: "EvidenceRecord | None",
) -> Status | None:
    """The control's status, **derived from the control record**, or `None`.

    EH-R2-1: a dependent case used to carry a caller-supplied copy of its
    control's status, and classification trusted that copy. An artifact could
    therefore hold a failed control and a dependent record that said
    `positive_control_status="passed"` and classified as passed, and recomputing
    the status from the same duplicated field proved nothing.

    There is now no duplicated status to trust. A dependent case carries the
    control **record**, this function reads the status off it, and every way of
    naming a control that would not be evidence is refused first:

    * a `DEPENDENT` that names no control, or names one it was not given;
    * a control record whose `case_id` is not the one the case declares;
    * a self-reference;
    * a control in a different band — `filesystem` and `identity` both have a
      case called `C-1`, so an unscoped id is ambiguous, and a control that ran
      in a different band did not hold the case's other variables fixed;
    * a referenced record that is not a `CONTROL`, which is what "inadmissible
      control reference" means; and
    * a `CONTROL` or `STANDALONE` that names a control at all.

    Returns `None` for the two non-dependent roles, which is what tells
    `classify()` that this case *is* a control or a read — a distinct value from
    `Status.NOT_RUN`, which would mean a control that was named and did not run.
    """
    if not isinstance(case_role, CaseRole):
        raise ObservationRefused(
            f"Case {case_id!r} declares no case role. A record that does not say "
            "whether it is a control, a read or a case requiring a control cannot "
            "be placed in the reference graph, and a control contract that is not "
            "declared is a control contract that cannot be checked."
        )

    if case_role is not CaseRole.DEPENDENT:
        if positive_control_case_id is not None or positive_control is not None:
            raise ObservationRefused(
                f"Case {case_id!r} is a {case_role.value} and names a positive "
                "control. Only a dependent case is interpreted beside one; a "
                "control or a read that carried a control reference would be "
                "claiming an attribution its own role says it does not have."
            )
        return None

    if positive_control_case_id is None:
        raise ObservationRefused(
            f"Case {case_id!r} is dependent and names no positive control. A "
            "dependent case is interpreted only beside the control that isolates "
            "it, so one that names none has nothing to be interpreted beside."
        )
    if positive_control_case_id == case_id:
        raise ObservationRefused(
            f"Case {case_id!r} names itself as its own positive control. A case "
            "cannot be the control that makes its own result attributable."
        )
    if positive_control is None:
        raise ObservationRefused(
            f"Case {case_id!r} names control {positive_control_case_id!r} and was "
            "not given that record. Its status is read from the control's own "
            "record and from nowhere else, so without the record there is no "
            "control status — and a dependent case with no control status is not "
            "evidence about the boundary under test."
        )
    if positive_control.case_id != positive_control_case_id:
        raise ObservationRefused(
            f"Case {case_id!r} names control {positive_control_case_id!r} but was "
            f"given case {positive_control.case_id!r}. A case interpreted beside "
            "the wrong control is interpreted beside a control that holds "
            "different variables fixed."
        )
    if positive_control.band != band:
        raise ObservationRefused(
            f"Case {case_id!r} in band {band!r} names control "
            f"{positive_control_case_id!r} from band {positive_control.band!r}. A "
            "control reference is scoped to its band: case ids repeat across "
            "bands, and a control that ran in another band did not hold this "
            "case's identity, path, inode or mount fixed."
        )
    if positive_control.case_role is not CaseRole.CONTROL:
        raise ObservationRefused(
            f"Case {case_id!r} names {positive_control_case_id!r} as its positive "
            f"control, but that case is a {positive_control.case_role.value}. Only "
            "a case the band declared a control is admissible as one."
        )
    return positive_control.status


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """One case, with everything a reviewer needs to check it without the harness.

    `expected` and `observed` are both `Outcome`s so that the comparison the
    status rests on is visible in the artifact rather than implied by the status.

    **`status` and `reason` are derived.** Prefer `for_case()`, which computes
    them. Supplying them directly is permitted only so that `from_mapping()` can
    reconstruct a stored record, and both routes recompute and compare: a value
    that disagrees with the classifier is refused rather than stored.
    """

    case_id: str
    band: str
    target_identity: str
    preconditions: tuple[str, ...]
    operation: str
    expected: Outcome
    observed: Outcome | None
    status: Status
    cleanup_state: CleanupState
    #: What this case is, with respect to the control contract. Declared by the
    #: band, serialized, and validated on every route into the class.
    case_role: CaseRole
    identity: ObservedIdentity | None = None
    expected_identity: ObservedIdentity | None = None
    #: The control this case is interpreted beside, named so a reviewer can find
    #: it. Required for `DEPENDENT`, refused for every other role.
    positive_control_case_id: str | None = None
    #: **The control record itself**, not a copy of its status. This is EH-R2-1:
    #: the control's result is a cross-record fact, so it is read from the record
    #: that observed it. There is no duplicated status to disagree with it, and a
    #: forged control has to be a whole record that classifies as passed from its
    #: own observations. It is deliberately **not serialized**: an artifact stores
    #: the reference, and `deserialize_records()` resolves it.
    positive_control: "EvidenceRecord | None" = None
    #: Why this observation is not attributable to the boundary under test, or
    #: `None` when it is. Set by the band from the observation, never by a caller
    #: choosing a status: it can only move a result away from `PASSED`.
    attribution_refusal: str | None = None
    reason: str = ""
    detail: Mapping[str, DetailValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ObservationRefused("A record needs a case id.")
        if not isinstance(self.band, str) or not self.band.strip():
            raise ObservationRefused(f"Case {self.case_id!r} needs a band.")
        if not isinstance(self.operation, str) or not self.operation.strip():
            raise ObservationRefused(
                f"Case {self.case_id!r} needs the operation it performed."
            )
        if not isinstance(self.status, Status):
            raise ObservationRefused(f"Case {self.case_id!r} has no status.")
        if not isinstance(self.cleanup_state, CleanupState):
            raise ObservationRefused(f"Case {self.case_id!r} has no cleanup state.")
        if not isinstance(self.preconditions, tuple):
            raise ObservationRefused(
                "Preconditions are an ordered tuple, so two runs of the same case "
                "serialize identically."
            )
        for key, value in self.detail.items():
            if not isinstance(key, str):
                raise ObservationRefused("Detail keys are field names, so they are text.")
            if not isinstance(value, (str, int, bool)) and value is not None:
                raise ObservationRefused(
                    f"Detail field {key!r} holds {type(value).__name__}. A record "
                    "carries scalars: file content, command output and host "
                    "configuration do not belong in an evidence artifact."
                )

        control_status = resolve_control_status(
            case_id=self.case_id,
            band=self.band,
            case_role=self.case_role,
            positive_control_case_id=self.positive_control_case_id,
            positive_control=self.positive_control,
        )

        derived_status, derived_reason = classify(
            expected=self.expected,
            observed=self.observed,
            identity=self.identity,
            expected_identity=self.expected_identity,
            positive_control_status=control_status,
            attribution_refusal=self.attribution_refusal,
        )
        if self.status is not derived_status or self.reason != derived_reason:
            raise ObservationRefused(
                f"Case {self.case_id!r} asserts status {self.status.value!r} with "
                f"reason {self.reason!r}; its own observations classify as "
                f"{derived_status.value!r} ({derived_reason}). Evidence used at a "
                "gate does not get to contradict itself."
            )

    @classmethod
    def for_case(
        cls,
        *,
        case_id: str,
        band: str,
        target_identity: str,
        operation: str,
        expected: Outcome,
        observed: Outcome | None,
        preconditions: Sequence[str] = (),
        case_role: CaseRole,
        cleanup_state: CleanupState = CleanupState.NOT_APPLICABLE,
        identity: ObservedIdentity | None = None,
        expected_identity: ObservedIdentity | None = None,
        positive_control_case_id: str | None = None,
        positive_control: "EvidenceRecord | None" = None,
        attribution_refusal: str | None = None,
        detail: Mapping[str, DetailValue] | None = None,
    ) -> "EvidenceRecord":
        """Build a record whose status and reason are the classifier's.

        This is the only construction the bands use. It cannot produce a record
        whose status disagrees with its observations, because it does not accept
        one — and since EH-R2-1 it cannot produce one whose control status
        disagrees with the control either, because it does not accept that
        status: it takes the **control record** and reads the status off it.
        """
        control_status = resolve_control_status(
            case_id=case_id,
            band=band,
            case_role=case_role,
            positive_control_case_id=positive_control_case_id,
            positive_control=positive_control,
        )
        status, reason = classify(
            expected=expected,
            observed=observed,
            identity=identity,
            expected_identity=expected_identity,
            positive_control_status=control_status,
            attribution_refusal=attribution_refusal,
        )
        return cls(
            case_id=case_id,
            band=band,
            target_identity=target_identity,
            preconditions=tuple(preconditions),
            operation=operation,
            expected=expected,
            observed=observed,
            status=status,
            cleanup_state=cleanup_state,
            case_role=case_role,
            identity=identity,
            expected_identity=expected_identity,
            positive_control_case_id=positive_control_case_id,
            positive_control=positive_control,
            attribution_refusal=attribution_refusal,
            reason=reason,
            detail=dict(detail or {}),
        )

    def to_mapping(self) -> dict[str, object]:
        return {
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "case_id": self.case_id,
            "band": self.band,
            "target_identity": self.target_identity,
            "preconditions": list(self.preconditions),
            "operation": self.operation,
            "expected": self.expected.to_mapping(),
            "observed": None if self.observed is None else self.observed.to_mapping(),
            "status": self.status.value,
            "cleanup_state": self.cleanup_state.value,
            "case_role": self.case_role.value,
            "identity": None if self.identity is None else self.identity.to_mapping(),
            "expected_identity": (
                None
                if self.expected_identity is None
                else self.expected_identity.to_mapping()
            ),
            "positive_control_case_id": self.positive_control_case_id,
            "attribution_refusal": self.attribution_refusal,
            "reason": self.reason,
            "detail": {key: self.detail[key] for key in sorted(self.detail)},
        }

    @classmethod
    def from_mapping(
        cls,
        raw: Mapping[str, Any],
        *,
        positive_control: "EvidenceRecord | None" = None,
    ) -> "EvidenceRecord":
        """Read a stored record back through the same validation that wrote it.

        This is where a tampered artifact is caught: `status` and `reason` are
        recomputed from the stored expectation, observation, identity assertion
        and — since EH-R2-1 — the **resolved** control record, and a stored value
        that disagrees is refused.

        `positive_control` is supplied by `deserialize_records()`, which resolves
        the artifact's reference graph before it constructs anything. A stored
        record that names a control cannot be read back on its own, because on
        its own there is nothing to resolve the name against: a single record
        carries no evidence about what its control actually did.
        """
        _require_exact_keys(
            raw,
            {
                "schema_version",
                "case_id",
                "band",
                "target_identity",
                "preconditions",
                "operation",
                "expected",
                "observed",
                "status",
                "cleanup_state",
                "case_role",
                "identity",
                "expected_identity",
                "positive_control_case_id",
                "attribution_refusal",
                "reason",
                "detail",
            },
            "record",
        )
        if raw["schema_version"] != EVIDENCE_SCHEMA_VERSION:
            raise ObservationRefused(
                f"This artifact is schema version {raw['schema_version']!r}; this "
                f"harness reads {EVIDENCE_SCHEMA_VERSION}. An artifact produced by "
                "another version is not silently compared with one produced by this."
            )
        return cls(
            case_id=raw["case_id"],
            band=raw["band"],
            target_identity=raw["target_identity"],
            preconditions=tuple(raw["preconditions"]),
            operation=raw["operation"],
            expected=Outcome.from_mapping(raw["expected"]),
            observed=(
                None if raw["observed"] is None else Outcome.from_mapping(raw["observed"])
            ),
            status=_status(raw["status"]),
            cleanup_state=_cleanup_state(raw["cleanup_state"]),
            case_role=_case_role(raw["case_role"]),
            identity=(
                None
                if raw["identity"] is None
                else ObservedIdentity.from_mapping(raw["identity"])
            ),
            expected_identity=(
                None
                if raw["expected_identity"] is None
                else ObservedIdentity.from_mapping(raw["expected_identity"])
            ),
            positive_control_case_id=raw["positive_control_case_id"],
            positive_control=positive_control,
            attribution_refusal=raw["attribution_refusal"],
            reason=raw["reason"],
            detail=dict(raw["detail"]),
        )


def _status(raw: object) -> Status:
    try:
        return Status(raw)
    except ValueError as exc:
        raise ObservationRefused(f"{raw!r} is not an evidence status.") from exc


def _cleanup_state(raw: object) -> CleanupState:
    try:
        return CleanupState(raw)
    except ValueError as exc:
        raise ObservationRefused(f"{raw!r} is not a cleanup state.") from exc


def _case_role(raw: object) -> CaseRole:
    try:
        return CaseRole(raw)
    except ValueError as exc:
        raise ObservationRefused(
            f"{raw!r} is not a case role. A record whose role this harness does "
            "not know cannot be placed in the control graph, and a record outside "
            "the control graph is not admissible evidence."
        ) from exc


def index_by_case_id(records: Sequence[EvidenceRecord]) -> dict[str, EvidenceRecord]:
    """Case id → record, refusing a duplicate.

    A duplicate case id makes *"resolve the reference to exactly one record"*
    unanswerable: two records claiming the same id are two different results
    under one name, and choosing either would be choosing which evidence to read.
    """
    index: dict[str, EvidenceRecord] = {}
    for record in records:
        if record.case_id in index:
            raise ObservationRefused(
                f"Case id {record.case_id!r} appears twice in this artifact. A "
                "control reference resolves to exactly one record, and a repeated "
                "id makes which one it resolves to a matter of position."
            )
        index[record.case_id] = record
    return index


def validate_artifact(records: Sequence[EvidenceRecord]) -> None:
    """Every control reference in this artifact resolves, here, to its own record.

    Each record has already checked its own control on construction. What only an
    artifact can check is that the control a dependent record *holds* is the same
    record the artifact *contains* under that id — a record built beside a
    fabricated control, or carried over from a different artifact, satisfies
    every per-record rule and still is not evidence about this run.
    """
    index = index_by_case_id(records)
    for record in records:
        if record.case_role is not CaseRole.DEPENDENT:
            continue
        reference = record.positive_control_case_id
        resolved = index.get(reference or "")
        if resolved is None:
            raise ObservationRefused(
                f"Case {record.case_id!r} names control {reference!r}, which this "
                "artifact does not contain. A control in another artifact is a "
                "control this artifact cannot show the result of, so the reference "
                "fails closed rather than being taken on trust."
            )
        if resolved != record.positive_control:
            raise ObservationRefused(
                f"Case {record.case_id!r} was classified beside a control that is "
                f"not the {reference!r} this artifact holds. The control a record "
                "is read against and the control the artifact publishes are the "
                "same record or the artifact is not self-describing."
            )


def serialize_records(records: Sequence[EvidenceRecord]) -> bytes:
    """Deterministic bytes for a validated artifact.

    `sort_keys=True` and a fixed separator set mean the only thing that can change
    the bytes is the evidence. The trailing newline is there so the artifact is a
    well-formed text file rather than a JSON blob a reader has to `cat -A`.

    The artifact is validated before it is written, so an incoherent set of
    records — a duplicate id, a dependent whose control is absent — cannot be
    produced and then discovered later by whoever reads it.
    """
    validate_artifact(records)
    payload = [record.to_mapping() for record in records]
    text = json.dumps(payload, sort_keys=True, indent=2, separators=(",", ": "))
    return (text + "\n").encode("utf-8")


def _raw_case_id(item: object, position: int) -> str:
    if not isinstance(item, Mapping):
        raise ObservationRefused(
            f"Record {position} of this artifact is not a mapping."
        )
    case_id = item.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise ObservationRefused(
            f"Record {position} of this artifact has no usable case id, so it "
            "cannot be placed in the control graph."
        )
    return case_id


def _resolve_reference_graph(payload: Sequence[object]) -> dict[str, object]:
    """Index the stored records and refuse every unresolvable reference shape.

    Run **before** anything is constructed, because a cycle would otherwise be
    discovered by recursing into it. The order is deliberate: existence and
    uniqueness first, then self-reference, then cycles, and only then the role
    and band rules — so a two-record cycle is reported as a cycle rather than as
    whichever of its two edges happens to be checked first.
    """
    index: dict[str, object] = {}
    for position, item in enumerate(payload):
        case_id = _raw_case_id(item, position)
        if case_id in index:
            raise ObservationRefused(
                f"Case id {case_id!r} appears twice in this artifact. A control "
                "reference resolves to exactly one record."
            )
        index[case_id] = item

    edges: dict[str, str] = {}
    for case_id, item in index.items():
        reference = item.get("positive_control_case_id")  # type: ignore[union-attr]
        if reference is None:
            continue
        if not isinstance(reference, str) or not reference.strip():
            raise ObservationRefused(
                f"Case {case_id!r} carries a control reference that is not a case "
                "id."
            )
        if reference == case_id:
            raise ObservationRefused(
                f"Case {case_id!r} names itself as its own positive control."
            )
        if reference not in index:
            raise ObservationRefused(
                f"Case {case_id!r} names control {reference!r}, which this artifact "
                "does not contain. The reference fails closed."
            )
        edges[case_id] = reference

    for start in edges:
        seen = [start]
        current = start
        while current in edges:
            current = edges[current]
            if current in seen:
                raise ObservationRefused(
                    "The control references in this artifact form a cycle "
                    f"({' -> '.join(seen + [current])}). A cycle means no case in "
                    "it has a control whose result was established independently, "
                    "so none of them attributes anything."
                )
            seen.append(current)
    return index


def deserialize_records(raw: bytes) -> tuple[EvidenceRecord, ...]:
    """Read an artifact back, re-validating every record **and every reference**.

    A stored `status` or `reason` that disagrees with the stored observations is
    an `ObservationRefused`, which is what makes reading an artifact back a check
    rather than a parse. Since EH-R2-1 the control a dependent case was read
    against is resolved here, from the artifact, and its status is read off the
    record that observed it — there is no stored control status to compare, and
    therefore none to tamper with.

    Records are constructed control-first, so the order they appear in the file
    does not affect what any of them resolves to.
    """
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ObservationRefused("The evidence artifact is not readable JSON.") from exc
    if not isinstance(payload, list):
        raise ObservationRefused("An evidence artifact is a list of records.")

    index = _resolve_reference_graph(payload)
    built: dict[str, EvidenceRecord] = {}

    def build(case_id: str) -> EvidenceRecord:
        if case_id in built:
            return built[case_id]
        item: Mapping[str, Any] = index[case_id]  # type: ignore[assignment]
        reference = item.get("positive_control_case_id")
        control = build(reference) if isinstance(reference, str) else None
        record = EvidenceRecord.from_mapping(item, positive_control=control)
        built[case_id] = record
        return record

    records = tuple(build(_raw_case_id(item, position))
                    for position, item in enumerate(payload))
    validate_artifact(records)
    return records


def records_digest(records: Sequence[EvidenceRecord]) -> str:
    """SHA-256 over `serialize_records()`, in the package's canonical encoding.

    The digest is over a **typed, named, length-delimited** field list rather than
    over the raw bytes alone, so it cannot collide with a digest of some other
    artifact that happens to share those bytes — the property
    `application/idempotency.py` documents and this package reuses rather than
    re-implements.
    """
    body = serialize_records(records)
    return canonical_request_hash(
        "phase-5-0-evidence-records",
        (
            ("schema_version", EVIDENCE_SCHEMA_VERSION),
            ("record_count", len(records)),
            ("body_sha256", hashlib.sha256(body).hexdigest()),
        ),
    ).hex()


def summarize(records: Sequence[EvidenceRecord]) -> dict[str, int]:
    """Counts per status, in a fixed key order, for a plan or handback table."""
    counts = {status.value: 0 for status in Status}
    for record in records:
        counts[record.status.value] += 1
    return counts


__all__ = [
    "CaseRole",
    "CleanupState",
    "DetailValue",
    "EvidenceRecord",
    "ObservedIdentity",
    "OperationKind",
    "Outcome",
    "Status",
    "classify",
    "deserialize_records",
    "index_by_case_id",
    "records_digest",
    "resolve_control_status",
    "serialize_records",
    "summarize",
    "validate_artifact",
]
