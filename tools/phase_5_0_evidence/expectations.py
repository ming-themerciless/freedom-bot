"""The typed, closed **semantic expectation** contracts, and the comparison that
makes an observation evidence rather than a stored string.

## The defect this module exists to remove — EH-R11-1 and EH-R11-2

R11 gave the harness two observation verbs and a capture boundary that
sanitizes what they print. It did not give the executor anything to compare that
output *with*. `P-05` — the interpreter preflight — was declared satisfied from
its exit status alone, so a run in which the case program printed a different
interpreter, a different digest, `isolated=no` or a third-party-importable
`sys.path` was recorded as a **pass**: the observation reached the artifact and
nothing ever read it. The same was true of the identities: exit 0 and the
presence of a `capsh --secbits=` argument stood in for *"the process that ran the
operation actually had this identity"*.

R12 then fixed that for seven of the eight and left `E7` with no contract at all,
which was Blocking finding **EH-R12-1**. R13 gives it one — the same twelve keys,
built from reviewed target facts rather than from a derivation it has no `M` for
— so `E1 … E8` now means all eight here.

An observation nobody compares is not evidence. This module is the comparison,
and `ExecutingRunner` applies it to the `CommandResult` it receives —
immediately after capture sanitation and **before** `StepOutcome.satisfied`,
`state.satisfied_steps` or any dependent execution decision exists.

## Expectations are kept apart from observations, structurally

Every expected value here comes from one of five places, and from nowhere else:

1. a **reviewed constant** in `case_runtime` — the interpreter path, its
   isolation contract, its major/minor version, its expected executable digest
   and its expected resolved path, each an externally supplied reviewed target
   fact;
2. a **reviewed derivation** in `capability` — `EvidenceIdentity.expected_
   masks()`, which computes the five masks and the securebits from `M` by
   §2.13.5c's seven-step construction;
3. the **review manifest's own covered-source digest** for
   `case_runtime.CASE_PROGRAM_SOURCE`, which `install` copies byte for byte, so
   the source digest is simultaneously the installation digest;
4. the **numbers in the vector that was executed** — `--uid=`, `--gid=` and
   `--groups=`, resolved by the late-binding boundary from the four reviewed
   names before `execve`; and
5. **`capability.E7_TARGET_FACTS`** — the ten reviewed target facts `E7` is
   compared against, new in R13. `E7` constructs nothing, so it has neither a
   derivation nor a bound vector to take a number from, and its uid, gid,
   supplementary set, five masks, `NoNewPrivs` and securebits are facts about
   the host stated from outside and verified by an independent reviewer. They
   ship `UNCONFIRMED`, and while any one of them is, the contract cannot be
   built and the executor refuses before it starts anything.

None of them is read from the output being judged. There is no code path in this
module that takes a value out of an observation and then treats it as the
expectation for that same observation, which is the property that makes a
preflight a check rather than a tautology.

## Fail-closed, with a fixed vocabulary of refusals

`ObservationContract.check()` returns the empty string when — and only when —
**every** expected key is present exactly once, is readable, and equals its
expected value. Anything else is a refusal drawn from the fixed list below:
missing, duplicated, unreadable, malformed, unexpected or unequal. The refusal
names the **reviewed key** whose comparison failed, because that name is part of
the contract a reviewer approved; it never names the observed value, path,
digest, identifier or an exception's text, because those are host facts and a
classification is not where a host fact may reach an artifact.

A refusal makes the step unsatisfied, which stops the run at that step. It is
never downgraded to a warning, never recorded as a pass, and never merely stored
for something later to interpret.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from . import capability, case_runtime
from .capability import EVIDENCE_IDENTITIES
from .capture import VARIABLE_KEY_POLICIES, CapturePolicy
from .errors import PlanRefused

# ---------------------------------------------------------------------------
# The fixed refusal vocabulary
# ---------------------------------------------------------------------------

#: Every one of these is a complete classification on its own. None interpolates
#: an observed value; the four that name a key interpolate a **reviewed** key
#: from the contract's own declared set, which is a name a reviewer approved and
#: not something the host said.
NO_OBSERVATIONS = (
    "the step recorded no observation at all, so the reviewed expectation for "
    "its capture policy was compared against nothing"
)
MALFORMED_OBSERVATIONS = (
    "the step's recorded observations are not the sanitized name/value pairs the "
    "capture boundary produces"
)
UNEXPECTED_KEY = (
    "the step's observation carries a name outside the reviewed key set for its "
    "capture policy"
)
MISSING_KEY = "the step's observation omits a reviewed key"
DUPLICATED_KEY = "the step's observation carries a reviewed key more than once"
UNREADABLE_VALUE = (
    "the capture boundary could not read a reviewed key's value, so it is an "
    "inconclusive observation rather than a comparable one"
)
UNEQUAL_VALUE = (
    "the step's observation does not equal the reviewed expected value for a key"
)
#: What the executor records when the contract itself could not be built — a
#: `CASE_IDENTITY` step naming no identity, an identity the closed table does not
#: carry, or a bound vector that does not carry exactly one of each numeric
#: identity option. Fail-closed: no contract means no comparison, and no
#: comparison means not satisfied.
EXPECTATION_NOT_CONSTRUCTED = (
    "the reviewed semantic expectation for this step could not be constructed, "
    "so its observation was not compared and the step is not satisfied"
)

#: The marker `capture.sanitize` writes when a value is not the shape its field
#: can legitimately have. It is an inconclusive observation, which is a result,
#: and it is never comparable.
UNREADABLE = "unreadable"

_DECIMAL = re.compile(r"\A[0-9]{1,10}\Z")
_HEXADECIMAL = re.compile(r"\A[0-9a-fA-F]{1,16}\Z")
_DECIMAL_LIST = re.compile(r"\A[0-9]{1,10}(?:,[0-9]{1,10})*\Z")
#: One name in a `TEXT_SET`. Deliberately narrower than `capture`'s value class:
#: a set member is an account, group, capability or flag name, never a path, a
#: digest or a sentence.
_NAME = re.compile(r"\A[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}\Z")
_NAME_LIST = re.compile(
    r"\A[A-Za-z0-9_][A-Za-z0-9_.-]{0,63}(?:,[A-Za-z0-9_][A-Za-z0-9_.-]{0,63})*\Z"
)
#: A token whose value a reviewed prerequisite does not state. It still has to be
#: a value the capture boundary produced rather than a marker it wrote, and
#: `check()` has already refused `unreadable` and the empty string before a
#: comparison is reached.
_TOKEN = re.compile(r"\A[A-Za-z0-9_][A-Za-z0-9_ .:/-]{0,127}\Z")

#: The literal a `TEXT_SET` observation carries for the empty set. `capsh` prints
#: `Ambient set =` with nothing after it and `getent group` prints an empty
#: fourth field; an empty *value* is `capture`'s marker for *"nothing was read"*,
#: so the two would be indistinguishable if the sanitizers did not write this.
EMPTY_SET = "none"


# ---------------------------------------------------------------------------
# The four comparisons
# ---------------------------------------------------------------------------


class Comparison(str, Enum):
    """How one expected value is compared with one observed value.

    Four kinds, closed. There is no *"contains"*, no *"starts with"* and no
    regular-expression kind: a comparison that admits more than one observed
    value is a comparison that admits one nobody reviewed.
    """

    #: Exact string equality, after the capture boundary's own cleaning.
    TEXT = "text"
    #: Decimal text, compared as an integer.
    NUMBER = "number"
    #: Hexadecimal text, compared as an integer — so `0000000000000200` and
    #: `200` are the same mask, which they are, and `0x200` is not this shape.
    HEX = "hex"
    #: A comma-separated decimal list, compared as a **set**: the supplementary
    #: group list is a set in the kernel and recording its order would compare
    #: something the case does not state.
    NUMBER_SET = "number_set"
    #: A comma-separated **name** list, compared as a set, with the literal
    #: `none` meaning the empty set. §2.12.2's membership matrix and `capsh`'s
    #: bounding/ambient sets are sets of names, and recording their order would
    #: compare something no case states. **R13, EH-R13-3.**
    TEXT_SET = "text_set"
    #: The observed text must be one of a **closed reviewed list**. It exists
    #: for exactly one situation and is refused for any other: the reviewed
    #: design itself admits more than one value, as §5.2 does for the negative
    #: access cases' `errno` — it states `EPERM` in one sentence and `EACCES`
    #: in another for the same kernel check, and `_ACCESS_DENIAL_STATUSES`
    #: already admits both exit statuses for that reason. The list is written
    #: in the plan and pinned in the review manifest, so it is as reviewed as a
    #: single value; what it is not is open-ended. **R13, EH-R13-3.**
    TEXT_ANY_OF = "text_any_of"
    #: The value must be **present, unique and well-formed decimal**, and its
    #: value is not compared, because the reviewed prerequisite does not state
    #: one. It is for run-time-allocated numbers only — a `--system` uid or gid
    #: the plan cannot know before `useradd` runs — and it is deliberately not a
    #: way to avoid writing an expectation down: `test_expectations.py`
    #: enumerates every step that uses it and asserts the reason. **R13.**
    NUMBER_PRESENT = "number_present"
    #: `NUMBER_PRESENT` for a token whose value the reviewed prerequisite does
    #: not state. Same rule, same enumeration, same reason. **R13.**
    TEXT_PRESENT = "text_present"


@dataclass(frozen=True, slots=True)
class Expectation:
    """One reviewed key, its comparison, and the value it must equal."""

    key: str
    comparison: Comparison
    #: `str` for `TEXT`, `int` for `NUMBER`/`HEX`, `frozenset[int]` for
    #: `NUMBER_SET`. Constructed here and never mutated.
    expected: object

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise PlanRefused("An expectation names a reviewed observation key.")
        if not isinstance(self.comparison, Comparison):
            raise PlanRefused(
                f"Expectation {self.key!r} names one of the closed comparisons."
            )
        if self.comparison is Comparison.TEXT:
            if not isinstance(self.expected, str) or not self.expected:
                raise PlanRefused(
                    f"Expectation {self.key!r} compares text and needs a "
                    "non-empty expected value."
                )
        elif self.comparison is Comparison.TEXT_SET:
            if not isinstance(self.expected, frozenset) or not all(
                isinstance(member, str) and _NAME.match(member)
                for member in self.expected
            ):
                raise PlanRefused(
                    f"Expectation {self.key!r} compares a set of names, each one "
                    "an account, group, capability or flag name."
                )
        elif self.comparison is Comparison.TEXT_ANY_OF:
            if (
                not isinstance(self.expected, tuple)
                or len(self.expected) < 2
                or not all(
                    isinstance(member, str) and member for member in self.expected
                )
                or len(set(self.expected)) != len(self.expected)
            ):
                raise PlanRefused(
                    f"Expectation {self.key!r} admits one of a closed reviewed "
                    "list of at least two distinct values. A list of one is a "
                    "`TEXT` comparison written the long way, and a list with a "
                    "repeat states the same admission twice."
                )
        elif self.comparison in (Comparison.NUMBER_PRESENT, Comparison.TEXT_PRESENT):
            # **The value here is illustrative and is never compared.** It is
            # what a rendered plan, a review manifest and the suite's positive
            # fixture write down for a key whose value the reviewed prerequisite
            # does not state, so it has to be a value the shape admits — and
            # `matches()` checks the shape and nothing else.
            if not isinstance(self.expected, str) or not self.expected:
                raise PlanRefused(
                    f"Expectation {self.key!r} does not compare a value and still "
                    "writes down a representative one, so a reviewer reads the "
                    "shape that is checked rather than a blank."
                )
            pattern = (
                _DECIMAL
                if self.comparison is Comparison.NUMBER_PRESENT
                else _TOKEN
            )
            if not pattern.match(self.expected):
                raise PlanRefused(
                    f"Expectation {self.key!r} writes down a representative value "
                    "that its own shape would refuse."
                )
        elif self.comparison is Comparison.NUMBER_SET:
            if not isinstance(self.expected, frozenset) or not all(
                isinstance(member, int) and not isinstance(member, bool) and member >= 0
                for member in self.expected
            ):
                raise PlanRefused(
                    f"Expectation {self.key!r} compares a set of non-negative "
                    "integers."
                )
        else:
            if (
                not isinstance(self.expected, int)
                or isinstance(self.expected, bool)
                or self.expected < 0
            ):
                raise PlanRefused(
                    f"Expectation {self.key!r} compares a non-negative integer."
                )

    @property
    def is_value_compared(self) -> bool:
        """False for the two `*_PRESENT` shapes, and True for every other.

        It exists so a reviewer, a rendered plan and the suite can enumerate the
        keys whose value the reviewed prerequisite does not state, rather than
        having to notice a comparison kind in a table of twelve.
        """
        return self.comparison not in (
            Comparison.NUMBER_PRESENT,
            Comparison.TEXT_PRESENT,
        )

    @property
    def canonical(self) -> str:
        """The expected value in the exact text form the case program prints.

        It is what the review manifest renders and what a reviewer reads. It is
        **not** used to decide a match — `matches()` compares values, so a mask
        the kernel zero-pads and one it does not are the same mask — but it is
        the one form in which the expectation is written down.
        """
        if self.comparison in (
            Comparison.TEXT,
            Comparison.NUMBER_PRESENT,
            Comparison.TEXT_PRESENT,
        ):
            return str(self.expected)
        if self.comparison is Comparison.NUMBER:
            return str(self.expected)
        if self.comparison is Comparison.HEX:
            return format(int(self.expected), "x")
        if self.comparison is Comparison.TEXT_ANY_OF:
            return "|".join(self.expected)  # type: ignore[arg-type]
        if self.comparison is Comparison.TEXT_SET:
            return (
                ",".join(sorted(self.expected))  # type: ignore[arg-type]
                if self.expected
                else EMPTY_SET
            )
        return ",".join(str(member) for member in sorted(self.expected))  # type: ignore[arg-type]

    @property
    def satisfying_example(self) -> str:
        """One observed value this expectation admits.

        It is **not** the canonical written form for the two comparisons whose
        written form is not itself an admissible observation: `TEXT_ANY_OF`
        writes `EPERM|EACCES`, which no capture boundary would ever produce.
        Nothing in the harness compares against this; it exists so the suite's
        positive fixture can script an observation that a real compliant
        producer could have printed, and `test_expectations.py` asserts that
        every one of them satisfies its own expectation.
        """
        if self.comparison is Comparison.TEXT_ANY_OF:
            return str(self.expected[0])  # type: ignore[index]
        return self.canonical

    def matches(self, observed: str) -> bool:
        """Whether one sanitized observed value equals this expectation."""
        if not isinstance(observed, str):
            return False
        if self.comparison is Comparison.TEXT:
            return observed == self.expected
        if self.comparison is Comparison.TEXT_ANY_OF:
            return observed in self.expected  # type: ignore[operator]
        if self.comparison is Comparison.NUMBER_PRESENT:
            return bool(_DECIMAL.match(observed))
        if self.comparison is Comparison.TEXT_PRESENT:
            return bool(_TOKEN.match(observed))
        if self.comparison is Comparison.TEXT_SET:
            if observed == EMPTY_SET:
                return not self.expected
            if not _NAME_LIST.match(observed):
                return False
            return set(observed.split(",")) == set(self.expected)  # type: ignore[arg-type]
        if self.comparison is Comparison.NUMBER:
            return bool(_DECIMAL.match(observed)) and int(observed, 10) == self.expected
        if self.comparison is Comparison.HEX:
            return (
                bool(_HEXADECIMAL.match(observed))
                and int(observed, 16) == self.expected
            )
        if not _DECIMAL_LIST.match(observed):
            return False
        return {int(part, 10) for part in observed.split(",")} == set(
            self.expected  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# The contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ObservationContract:
    """Every expectation one step's observation must satisfy, and the check.

    `subject` is a short reviewed label — `case-runtime` or an `E` identity name
    — carried so a rendered plan and a manifest can say which contract applies
    to which step. It is never taken from a host.
    """

    policy: CapturePolicy
    subject: str
    expectations: tuple[Expectation, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.policy, CapturePolicy):
            raise PlanRefused("A contract names one of the closed capture policies.")
        if not self.expectations:
            raise PlanRefused(
                f"The {self.subject!r} contract declares no expectation. A "
                "contract that compares nothing would make every observation "
                "satisfy it, which is the defect this module removes."
            )
        keys = [expectation.key for expectation in self.expectations]
        if len(set(keys)) != len(keys):
            raise PlanRefused(
                f"The {self.subject!r} contract states two expectations for one "
                "key, so which one decides the comparison would depend on order."
            )
        if self.policy is CapturePolicy.CASE_IDENTITY and set(keys) != set(
            IDENTITY_KEYS
        ):
            # **EH-R12-1.** Every identity is compared against the *same* twelve
            # keys, whichever constructor built the contract. A narrower `E7`
            # contract — one that quietly omitted the securebits it has no
            # reviewed fact for — would be the finding again in a new shape, so
            # it is refused here rather than left to a reviewer to notice.
            raise PlanRefused(
                f"The {self.subject!r} identity contract compares "
                f"{sorted(set(keys))}; §2.13.5c's assertion table is "
                f"{list(IDENTITY_KEYS)}, and every identity is compared against "
                "all of it."
            )

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(expectation.key for expectation in self.expectations)

    def expected_observations(self) -> tuple[tuple[str, str], ...]:
        """The complete expected observation, in the case program's own sorted
        order. It is the canonical written form of the contract."""
        return tuple(
            sorted(
                (expectation.key, expectation.canonical)
                for expectation in self.expectations
            )
        )

    def satisfying_observations(self) -> tuple[tuple[str, str], ...]:
        """A complete observation this contract accepts, in sorted key order.

        For the suite's positive fixture, and for nothing else. `check()` is what
        decides a run; this is what a compliant producer could have printed.
        """
        return tuple(
            sorted(
                (expectation.key, expectation.satisfying_example)
                for expectation in self.expectations
            )
        )

    def check(self, observations: Sequence[tuple[str, str]]) -> str:
        """The empty string when the observation satisfies every expectation,
        else one fixed classification.

        Exactly one readable value is required for **every** expected key, and
        no key outside the expected set may be present. There is no partial
        satisfaction and no key whose absence is tolerated.
        """
        if not isinstance(observations, (tuple, list)):
            return MALFORMED_OBSERVATIONS
        if not observations:
            return NO_OBSERVATIONS
        seen: dict[str, list[str]] = {}
        for pair in observations:
            if (
                not isinstance(pair, (tuple, list))
                or len(pair) != 2
                or not isinstance(pair[0], str)
                or not isinstance(pair[1], str)
            ):
                return MALFORMED_OBSERVATIONS
            seen.setdefault(pair[0], []).append(pair[1])
        if set(seen) - set(self.keys):
            # The key itself is deliberately not named: an unexpected key is a
            # string the observed output supplied, and no host-supplied string
            # belongs in a classification.
            return UNEXPECTED_KEY
        for expectation in self.expectations:
            values = seen.get(expectation.key)
            if values is None:
                return f"{MISSING_KEY} ({expectation.key})"
            if len(values) != 1:
                return f"{DUPLICATED_KEY} ({expectation.key})"
            value = values[0]
            if not value or value == UNREADABLE:
                return f"{UNREADABLE_VALUE} ({expectation.key})"
            if not expectation.matches(value):
                return f"{UNEQUAL_VALUE} ({expectation.key})"
        return ""


# ---------------------------------------------------------------------------
# `P-05` — the interpreter preflight
# ---------------------------------------------------------------------------

#: A covered-source digest, as the review manifest writes one.
_SOURCE_DIGEST = re.compile(r"\A[0-9a-f]{64}\Z")


def case_runtime_contract(
    *, case_program_installed_path: str, case_program_sha256: str
) -> ObservationContract:
    """`CapturePolicy.CASE_RUNTIME`'s complete expectation set.

    Two of the eleven values are supplied by the caller rather than read from a
    constant, and each has one legitimate source:

    * `case_program_installed_path` is `case_runtime.case_program_path(target)`,
      derived from the **approved target's** validated root; and
    * `case_program_sha256` is the review manifest's covered-source digest for
      `case_runtime.CASE_PROGRAM_SOURCE` — the bytes the reviewer approved, which
      `install` copies unchanged, so the source digest is the installation
      digest. It is **not** read from the installed file and **not** learned from
      `P-05`'s own output.

    The remaining nine come from `case_runtime`'s reviewed constants, read
    through the module rather than bound at import so that supplying a reviewed
    target fact takes effect where it is supplied.
    """
    if not isinstance(case_program_installed_path, str) or not (
        case_program_installed_path.startswith("/")
    ):
        raise PlanRefused(
            "The case program's installed path is an absolute path derived from "
            "the approved target's validated root."
        )
    if not isinstance(case_program_sha256, str) or not _SOURCE_DIGEST.match(
        case_program_sha256
    ):
        raise PlanRefused(
            "The expected case-program digest is the review manifest's "
            "covered-source digest — 64 lower-case hexadecimal characters. It is "
            "never learned from the observation it is compared with."
        )
    return ObservationContract(
        policy=CapturePolicy.CASE_RUNTIME,
        subject="case-runtime",
        expectations=(
            Expectation("verb", Comparison.TEXT, "runtime"),
            Expectation("result", Comparison.TEXT, "returned"),
            Expectation("interpreter", Comparison.TEXT, case_runtime.INTERPRETER_PATH),
            Expectation(
                "interpreter_real",
                Comparison.TEXT,
                case_runtime.EXPECTED_INTERPRETER_REAL_PATH,
            ),
            Expectation(
                "python_version",
                Comparison.TEXT,
                case_runtime.INTERPRETER_PYTHON_VERSION,
            ),
            Expectation(
                "interpreter_sha256",
                Comparison.TEXT,
                case_runtime.EXPECTED_INTERPRETER_SHA256,
            ),
            Expectation("isolated", Comparison.TEXT, "yes"),
            Expectation("no_site", Comparison.TEXT, "yes"),
            Expectation("third_party_importable", Comparison.TEXT, "no"),
            Expectation("case_program", Comparison.TEXT, case_program_installed_path),
            Expectation("case_program_sha256", Comparison.TEXT, case_program_sha256),
        ),
    )


# ---------------------------------------------------------------------------
# `E1 … E8` — the eight observed identities
# ---------------------------------------------------------------------------

#: `E7`, the one identity §2.13.5c builds by **not** dropping: the harness's own
#: root process. It is named once here and referred to by this constant, because
#: R12 spelled it as a literal in five places and every one of them excluded it.
ROOT_IDENTITY = "E7"

#: The twelve reviewed keys **every** identity contract compares, in the order a
#: reader of §2.13.5c's assertion table meets them. Both constructors below build
#: exactly this key set, and `test_root_identity.py` asserts they agree — so
#: `E7`'s contract cannot be a narrower one that happens to pass.
IDENTITY_KEYS: tuple[str, ...] = (
    "verb",
    "result",
    "uid",
    "gid",
    "groups",
    "cap_inh",
    "cap_prm",
    "cap_eff",
    "cap_bnd",
    "cap_amb",
    "no_new_privs",
    "securebits",
)

#: The three `capsh` options that carry a late-bound number. The executor
#: substitutes them from the four reviewed names immediately before `execve`, so
#: they are the identity the vector actually asked the kernel for — an
#: independent source from the observation, and the only one available, because
#: the accounts do not exist until Band 2 creates them.
UID_PREFIX = "--uid="
GID_PREFIX = "--gid="
GROUPS_PREFIX = "--groups="


def identity_numbers(argv: Sequence[str]) -> tuple[int, int, frozenset[int]]:
    """The uid, gid and supplementary group set the bound vector asked for.

    Exactly one of each option, each parsing as decimal, is required. A vector
    with none, with two, or with a non-numeric value is refused rather than
    guessed at — the guess would be an expectation nobody reviewed.
    """
    if isinstance(argv, (str, bytes)) or not isinstance(argv, Sequence):
        raise PlanRefused("An identity vector is a sequence of separate arguments.")
    found: dict[str, str] = {}
    for prefix in (UID_PREFIX, GID_PREFIX, GROUPS_PREFIX):
        matches = [
            argument[len(prefix) :]
            for argument in argv
            if isinstance(argument, str) and argument.startswith(prefix)
        ]
        if len(matches) != 1:
            raise PlanRefused(
                f"The bound identity vector carries {len(matches)} {prefix!r} "
                "arguments; the reviewed construction emits exactly one."
            )
        found[prefix] = matches[0]
    if not _DECIMAL.match(found[UID_PREFIX]) or not _DECIMAL.match(found[GID_PREFIX]):
        raise PlanRefused(
            "The bound identity vector's uid and gid are decimal numbers the "
            "late-binding boundary resolved."
        )
    if not _DECIMAL_LIST.match(found[GROUPS_PREFIX]):
        raise PlanRefused(
            "The bound identity vector's group list is a comma-separated set of "
            "decimal numbers."
        )
    return (
        int(found[UID_PREFIX], 10),
        int(found[GID_PREFIX], 10),
        frozenset(int(part, 10) for part in found[GROUPS_PREFIX].split(",")),
    )


def constructed_identity_contract(
    name: str, *, uid: int, gid: int, group_ids: frozenset[int]
) -> ObservationContract:
    """`CapturePolicy.CASE_IDENTITY`'s expectation set for one **capsh-constructed**
    identity — `E1 … E6` and `E8`.

    Twelve values, and every one of them is compared before the identity's case
    may be satisfied: effective uid, effective gid, the complete supplementary
    group set, `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, `CapAmb`, `NoNewPrivs`
    and the **final securebits**, plus the verb and result that say the
    observation is the one the vector asked for.

    The five masks, `NoNewPrivs` and the securebits come from
    `EvidenceIdentity.expected_masks()` — §2.13.5c's seven-step derivation from
    `M` — and the three numbers come from the bound vector. Neither source is
    the observation.

    `E7` is refused here and has its own constructor, `root_identity_contract()`,
    because its twelve values have a different — and equally independent —
    source. It is **not** refused because it is unobservable: R12 believed that,
    and EH-R12-1 is the finding that it is false.
    """
    identity = EVIDENCE_IDENTITIES.get(name)
    if identity is None:
        raise PlanRefused(
            f"{name!r} is not one of the reviewed evidence identities "
            f"{sorted(EVIDENCE_IDENTITIES)}."
        )
    if name == ROOT_IDENTITY:
        raise PlanRefused(
            "E7 is constructed by no capsh vector, so it has no --uid=, --gid= "
            "or --groups= to take its three numbers from and no `M` to derive "
            "its masks from. Its contract is `root_identity_contract()`, built "
            "from the reviewed target facts in `capability.E7_TARGET_FACTS`, and "
            "it observes the same twelve values through the same `identity` verb "
            "in the same interpreted process."
        )
    for label, value in (("uid", uid), ("gid", gid)):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise PlanRefused(
                f"{name}'s expected {label} is a non-negative integer the "
                "late-binding boundary resolved."
            )
    if not isinstance(group_ids, frozenset) or not group_ids:
        raise PlanRefused(
            f"{name}'s expected supplementary group set is a non-empty frozenset "
            "of the numbers the bound vector asked for."
        )
    masks = identity.expected_masks()
    return ObservationContract(
        policy=CapturePolicy.CASE_IDENTITY,
        subject=name,
        expectations=(
            Expectation("verb", Comparison.TEXT, "identity"),
            Expectation("result", Comparison.TEXT, "returned"),
            Expectation("uid", Comparison.NUMBER, uid),
            Expectation("gid", Comparison.NUMBER, gid),
            Expectation("groups", Comparison.NUMBER_SET, group_ids),
            Expectation("cap_inh", Comparison.HEX, masks["cap_inh"]),
            Expectation("cap_prm", Comparison.HEX, masks["cap_prm"]),
            Expectation("cap_eff", Comparison.HEX, masks["cap_eff"]),
            Expectation("cap_bnd", Comparison.HEX, masks["cap_bnd"]),
            Expectation("cap_amb", Comparison.HEX, masks["cap_amb"]),
            Expectation("no_new_privs", Comparison.NUMBER, 0),
            Expectation("securebits", Comparison.HEX, masks["securebits"]),
        ),
    )


def root_identity_contract() -> ObservationContract:
    """`E7`'s expectation set — the same twelve keys, from reviewed target facts.

    ## What EH-R12-1 found, and what this is

    R12 created `CASE_IDENTITY` steps for `E1 … E6` and `E8`, excluded `E7`, and
    said `P-01` and `P-02` classified it instead. They do not. `P-01` is
    `capsh --print` and `P-02` is `capsh --decode=…`: neither runs the case
    program, neither runs in the process the reviewed vector produces, and
    neither reads securebits with `prctl(PR_GET_SECUREBITS)` — `capsh --print`
    prints the securebits of **`capsh`'s own** process, which is not the final
    interpreted one. Between them they cover the launcher's bounding set and a
    name-by-name expansion of a documented mask; they do not cover `E7`'s uid,
    gid, complete supplementary set, five masks, `NoNewPrivs` or final
    securebits as one compared observation. So `E7` is now a step like the other
    seven, and `P-01`/`P-02` are retained unchanged beside it as the separate
    preflight evidence they always were.

    ## Where the twelve values come from

    `verb` and `result` are the case program's own literals, exactly as they are
    for the other seven. The remaining ten come from
    `capability.E7_TARGET_FACTS` — reviewed target facts about the host, stated
    from outside and verified by an independent reviewer, in the sense
    `case_runtime.EXPECTED_INTERPRETER_SHA256` already is.

    They are read through the `capability` module rather than bound at import,
    so supplying a reviewed fact takes effect where it is supplied — the rule
    `case_runtime_contract()` follows for the two interpreter facts.

    **Nothing here can learn a value from the run being judged.** Not from
    `P-01`, not from `P-02`, not from `E7`'s own observation, not from `/proc`,
    `id` or `capsh`. While any fact is unconfirmed this raises, the executor has
    already refused before starting any command, and a contract that cannot be
    built is `EXPECTATION_NOT_CONSTRUCTED` — never a pass.
    """
    values = capability.e7_expected_values()
    return ObservationContract(
        policy=CapturePolicy.CASE_IDENTITY,
        subject=ROOT_IDENTITY,
        expectations=(
            Expectation("verb", Comparison.TEXT, "identity"),
            Expectation("result", Comparison.TEXT, "returned"),
            Expectation("uid", Comparison.NUMBER, values["uid"]),
            Expectation("gid", Comparison.NUMBER, values["gid"]),
            Expectation("groups", Comparison.NUMBER_SET, values["groups"]),
            Expectation("cap_inh", Comparison.HEX, values["cap_inh"]),
            Expectation("cap_prm", Comparison.HEX, values["cap_prm"]),
            Expectation("cap_eff", Comparison.HEX, values["cap_eff"]),
            Expectation("cap_bnd", Comparison.HEX, values["cap_bnd"]),
            Expectation("cap_amb", Comparison.HEX, values["cap_amb"]),
            Expectation("no_new_privs", Comparison.NUMBER, values["no_new_privs"]),
            Expectation("securebits", Comparison.HEX, values["securebits"]),
        ),
    )


# ---------------------------------------------------------------------------
# `P-01` — the launching process's capability state
# ---------------------------------------------------------------------------


def launcher_capability_contract() -> ObservationContract:
    """`CapturePolicy.CAPABILITY_MASKS`'s expectation — **R13, EH-R13-3**.

    `P-01` observes the **launching process**, and `P-06` observes `E7`. They are
    the same process: §2.13.5c's `E7` *"is the harness's own root identity,
    constructed by not dropping"*, and the harness's own root process is what
    launches every step. So the four values `capsh --print` reports about it are
    four of `E7`'s ten reviewed target facts, and they are read from
    `capability.E7_TARGET_FACTS` rather than declared a second time: two
    statements of one fact are two things that can disagree.

    That is also why this contract is **derived** rather than declared on the
    step. The facts ship `UNCONFIRMED`; a plan that wrote them down would either
    have to carry the unconfirmed marker into a comparison or invent a value, and
    the executor's fourth gate exists precisely so neither happens. While any
    fact is unconfirmed this raises, and the executor records
    `EXPECTATION_NOT_CONSTRUCTED` — never a pass.

    `capsh` prints capability **names** and the reviewed facts are **masks**;
    `capture._capability_mask` converts the observation, in a total lookup over
    the one closed name table, so an unknown name is `unreadable` rather than a
    silently smaller set. The expectation is never converted from the thing it
    judges.

    `no_new_privs` and `securebits` are compared here **and** in `P-06`, from the
    same two facts, and that is deliberate: `P-01` reads them from the launching
    process before anything is constructed, `P-06` reads the securebits through
    `prctl(PR_GET_SECUREBITS)` in the final interpreted process after `execve`,
    and a disagreement between the two is a fact about the run worth stopping on.
    """
    values = capability.e7_expected_values()
    return ObservationContract(
        policy=CapturePolicy.CAPABILITY_MASKS,
        subject="launcher-capabilities",
        expectations=(
            Expectation("bounding_set", Comparison.HEX, values["cap_bnd"]),
            Expectation("ambient_set", Comparison.HEX, values["cap_amb"]),
            Expectation("securebits", Comparison.HEX, values["securebits"]),
            Expectation("no_new_privs", Comparison.NUMBER, values["no_new_privs"]),
        ),
    )


# ---------------------------------------------------------------------------
# The declared contracts — every other observation-bearing policy, R13
# ---------------------------------------------------------------------------

#: The policies whose contract is built from reviewed constants rather than from
#: the plan. `CASE_RUNTIME`'s eleven values come from `case_runtime`, the review
#: manifest and the approved target; `CASE_IDENTITY`'s twelve come from the
#: §2.13.5c derivation or from `capability.E7_TARGET_FACTS`. Neither is declared
#: on a step, because the plan is not where either expectation may be written.
DERIVED_CONTRACT_POLICIES = frozenset(
    {
        CapturePolicy.CASE_RUNTIME,
        CapturePolicy.CASE_IDENTITY,
        CapturePolicy.CAPABILITY_MASKS,
    }
)


@dataclass(frozen=True, slots=True)
class DeclaredExpectation:
    """One reviewed key, comparison and value, **written in the plan**.

    ## Why this exists — Blocking finding EH-R13-3

    R12 gave two capture policies a semantic contract and left the other nine
    with none. Every step declaring one of those nine was satisfied by its exit
    status alone, so an observation that flatly contradicted the step's stated
    prerequisite — an empty bounding set from `P-01`, a `freedomjournal` carrying
    a member §2.12.2 gives it no reason to have — was recorded as a pass, and the
    dependent steps that assume the prerequisite ran anyway. Describing those
    observations as *"classified later by the bands"* did not make them a gate:
    the band classifiers exist, and the execution loop never called them.

    The correction is not a ninth bespoke contract builder. It is that a step
    **declares** its expectation in the reviewed plan, in the same closed
    comparison vocabulary the two derived contracts use, and the executor
    compares it at the same point and with the same fail-closed rules. The
    declaration is pinned in the review manifest, so *what a prerequisite means*
    is reviewed alongside *what it runs*.

    ## Values are text here, and typed by `to_expectation()`

    The plan writes `("gid", NUMBER_PRESENT, "5001")`, not a `frozenset[int]`.
    Two reasons, and both are about review rather than convenience: the manifest
    renders and digests the exact text a reviewer reads, and the parse from text
    to value happens in one place that refuses a value its comparison cannot
    hold, rather than at each of the forty-odd declaration sites.
    """

    key: str
    comparison: Comparison
    #: The expected value in the canonical text form the capture boundary
    #: produces. For `TEXT_SET` and `NUMBER_SET`, a comma-separated list or the
    #: literal `none`; for `TEXT_ANY_OF`, the admitted values joined with `|`;
    #: for `HEX`, lower-case hexadecimal with no `0x`; for the two `*_PRESENT`
    #: shapes, a **representative** value that is written down and not compared.
    value: str
    #: Why the reviewed prerequisite does not state a value. Required for the two
    #: `*_PRESENT` comparisons and refused for every other, so *"this one is not
    #: compared"* is never an unexplained entry in a table.
    uncompared_because: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key.strip():
            raise PlanRefused("A declared expectation names an observation key.")
        if not isinstance(self.comparison, Comparison):
            raise PlanRefused(
                f"Declared expectation {self.key!r} names one of the closed "
                "comparisons."
            )
        if not isinstance(self.value, str) or not self.value.strip():
            raise PlanRefused(
                f"Declared expectation {self.key!r} states no value. A key with "
                "no expectation is the defect EH-R13-3 found, written down."
            )
        uncompared = self.comparison in (
            Comparison.NUMBER_PRESENT,
            Comparison.TEXT_PRESENT,
        )
        if uncompared and not self.uncompared_because.strip():
            raise PlanRefused(
                f"Declared expectation {self.key!r} does not compare its value "
                "and does not say why. The two shape-only comparisons exist for "
                "run-time-allocated numbers and for host facts no reviewed "
                "prerequisite states; an unexplained one is a comparison "
                "somebody skipped."
            )
        if not uncompared and self.uncompared_because:
            raise PlanRefused(
                f"Declared expectation {self.key!r} compares its value and "
                "carries a reason for not comparing it."
            )
        # Built once here so a declaration that cannot become an `Expectation` is
        # refused when the plan is built, not when a run reaches the step.
        self.to_expectation()

    def to_expectation(self) -> Expectation:
        """The typed comparison, or a refusal naming the key."""
        raw = self.value.strip()
        try:
            if self.comparison in (
                Comparison.TEXT,
                Comparison.TEXT_PRESENT,
                Comparison.NUMBER_PRESENT,
            ):
                expected: object = raw
            elif self.comparison is Comparison.NUMBER:
                expected = int(raw, 10)
            elif self.comparison is Comparison.HEX:
                expected = int(raw, 16)
            elif self.comparison is Comparison.TEXT_ANY_OF:
                expected = tuple(part for part in raw.split("|") if part)
            elif self.comparison is Comparison.TEXT_SET:
                expected = frozenset(
                    () if raw == EMPTY_SET else (part for part in raw.split(",") if part)
                )
            else:
                expected = frozenset(
                    ()
                    if raw == EMPTY_SET
                    else (int(part, 10) for part in raw.split(",") if part)
                )
        except ValueError as exc:  # a malformed number in a declared list
            raise PlanRefused(
                f"Declared expectation {self.key!r} states a value its "
                f"{self.comparison.value} comparison cannot hold."
            ) from exc
        return Expectation(self.key, self.comparison, expected)


def declared_contract(
    *, policy: CapturePolicy, subject: str, declared: Sequence[DeclaredExpectation]
) -> ObservationContract:
    """The contract a step's own declaration makes, checked against its policy.

    Two guards, and each closes a way the declaration could be weaker than it
    looks:

    1. **the declared keys are exactly the policy's**, for every policy whose
       emitted key set is fixed. A declaration that omitted a key the sanitizer
       produces would leave that key uncompared at the one moment it matters, and
       `ObservationContract.check` would refuse the observation for carrying an
       unexpected key rather than for the reason the reviewer cares about; and
    2. **a variable-key policy declares a subset**, never a key outside the
       policy. `CASE_RESULT` is the only one: which keys the case program prints
       depends on the verb and on whether the operation returned, so the step
       declares the set its own vector produces.
    """
    keys = [item.key for item in declared]
    if len(set(keys)) != len(keys):
        raise PlanRefused(
            f"The {subject!r} declaration states two expectations for one key."
        )
    permitted = capture_policy_keys(policy)
    if policy in VARIABLE_KEY_POLICIES:
        outside = sorted(set(keys) - permitted)
        if outside:
            raise PlanRefused(
                f"The {subject!r} declaration states expectations for {outside}, "
                f"which {policy.value} cannot produce."
            )
    elif set(keys) != permitted:
        raise PlanRefused(
            f"The {subject!r} declaration compares {sorted(set(keys))}; "
            f"{policy.value} produces {sorted(permitted)}, and every key it "
            "produces is compared."
        )
    return ObservationContract(
        policy=policy,
        subject=subject,
        expectations=tuple(item.to_expectation() for item in declared),
    )


def capture_policy_keys(policy: CapturePolicy) -> frozenset[str]:
    """The keys `policy` can emit, read through `capture` so there is one table."""
    from .capture import POLICY_KEYS

    if policy not in POLICY_KEYS:  # pragma: no cover - the table is exhaustive
        raise PlanRefused(f"{policy!r} declares no emitted key set.")
    return POLICY_KEYS[policy]


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def contract_for(
    *,
    capture: CapturePolicy,
    identity_name: str,
    argv: Sequence[str],
    case_program_installed_path: str,
    case_program_sha256: str,
    declared: Sequence[DeclaredExpectation] = (),
    subject: str = "",
) -> ObservationContract | None:
    """The contract one step's observation is compared against, or `None`.

    `None` means **`EXIT_STATUS_ONLY` and nothing else** — a step with no
    observation to compare, whose exit status is the whole of what the reviewed
    plan says about it. Every other policy produces a contract: the two derived
    ones from reviewed constants, and the remaining nine from the step's own
    declaration.

    That is the R13 correction. R12 returned `None` for those nine, so a step
    that recorded an observation was satisfied by its exit status while the
    observation reached the artifact uncompared — Blocking finding EH-R13-3. A
    policy that carries a contract and cannot produce one raises, and the
    executor turns that into `EXPECTATION_NOT_CONSTRUCTED` rather than into a
    pass: no contract means no comparison, and no comparison means not satisfied.
    """
    if capture is CapturePolicy.EXIT_STATUS_ONLY:
        return None
    if capture not in DERIVED_CONTRACT_POLICIES:
        if not declared:
            raise PlanRefused(
                f"A {capture.value} step declares no reviewed expectation for the "
                "observation it records. An observation nobody compares is not "
                "evidence, and exit status alone does not decide a step that "
                "makes one."
            )
        return declared_contract(
            policy=capture,
            subject=subject or capture.value,
            declared=declared,
        )
    if capture is CapturePolicy.CAPABILITY_MASKS:
        return launcher_capability_contract()
    if capture is CapturePolicy.CASE_RUNTIME:
        return case_runtime_contract(
            case_program_installed_path=case_program_installed_path,
            case_program_sha256=case_program_sha256,
        )
    if capture is CapturePolicy.CASE_IDENTITY:
        if not isinstance(identity_name, str) or not identity_name:
            raise PlanRefused(
                "A step that observes an identity names which of `E1 … E8` it "
                "observes; the expectation cannot be chosen otherwise."
            )
        if identity_name == ROOT_IDENTITY:
            # `E7` reaches the kernel through no capsh construction, so the
            # vector carries no `--uid=`, `--gid=` or `--groups=` and
            # `identity_numbers()` is not asked for any. Its three credentials
            # are reviewed target facts like its masks are.
            return root_identity_contract()
        uid, gid, group_ids = identity_numbers(argv)
        return constructed_identity_contract(
            identity_name, uid=uid, gid=gid, group_ids=group_ids
        )
    raise PlanRefused(  # pragma: no cover - the two branches above are exhaustive
        f"{capture!r} is a derived-contract policy with no builder."
    )


#: The seven identities a `capsh` vector constructs — §2.13.5c's seven-step
#: procedure, parameterised by `U`, `G`, `S` and `M`. `E7` is not one of them
#: because nothing is constructed for it, which is a statement about **how it is
#: produced** and says nothing about whether it is observed.
CAPSH_CONSTRUCTED_IDENTITIES: frozenset[str] = frozenset(
    name for name in EVIDENCE_IDENTITIES if name != ROOT_IDENTITY
)

#: Every identity a `CASE_IDENTITY` step may name — **all eight**. That is
#: EH-R12-1's correction: R12's set was the seven above under a name that read as
#: though it were this one, and the shape guard in `plan.CommandStep`, the review
#: manifest and the suite all inherited the exclusion from it. Each of the eight
#: runs the `identity` verb in the final interpreted process and is compared
#: against the same twelve reviewed keys.
OBSERVED_IDENTITIES: frozenset[str] = frozenset(EVIDENCE_IDENTITIES)


__all__ = [
    "CAPSH_CONSTRUCTED_IDENTITIES",
    "Comparison",
    "DERIVED_CONTRACT_POLICIES",
    "DeclaredExpectation",
    "EMPTY_SET",
    "capture_policy_keys",
    "declared_contract",
    "launcher_capability_contract",
    "DUPLICATED_KEY",
    "EXPECTATION_NOT_CONSTRUCTED",
    "Expectation",
    "GID_PREFIX",
    "GROUPS_PREFIX",
    "IDENTITY_KEYS",
    "MALFORMED_OBSERVATIONS",
    "MISSING_KEY",
    "NO_OBSERVATIONS",
    "OBSERVED_IDENTITIES",
    "ObservationContract",
    "ROOT_IDENTITY",
    "UID_PREFIX",
    "UNEQUAL_VALUE",
    "UNEXPECTED_KEY",
    "UNREADABLE_VALUE",
    "case_runtime_contract",
    "constructed_identity_contract",
    "contract_for",
    "identity_numbers",
    "root_identity_contract",
]
