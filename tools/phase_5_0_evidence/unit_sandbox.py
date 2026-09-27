"""§2.13.2a **S4-3** — which sandbox Stage 4 actually exercised, established from
typed inputs and fail-closed.

## Why this module exists

S4-1 and S4-2 attest that *some* sandbox denied a write. S4-3 is what makes that
a statement about **the writer's** sandbox: the directive set systemd applied to
the transient unit must equal the deployed `freedom-sheet-writer.service`'s,
except for the one recorded `ReadWritePaths=` substitution. The security review
(rev 11, *"Stage 4 remains conditional"*) made four conditions of that
comparison, and the P5.0-R5 reconciliation (matrix row 15) found none of them
implemented. They are, and each is one function below:

1. **A closed allowlist of supported unit directives and drop-ins.**
   `parse_deployed_unit()` accepts three sections, the directives in
   `DIRECTIVES` and the drop-ins in `SUPPORTED_DROP_INS`, and nothing else. A
   continuation line, a specifier, a quoted value or a `~` capability inversion
   is outside the grammar and refused rather than interpreted.
2. **Duplicate or unknown authority-bearing directives are rejected,
   including in drop-ins.** An unknown directive is refused outright, because a
   parser that does not know a directive cannot know it bears no authority; an
   authority-bearing directive assigned twice anywhere across the unit and its
   drop-ins is refused, because systemd's reset-and-accumulate rules are exactly
   the interpretation this comparison must not depend on.
3. **The substituted `ReadWritePaths=` comes from the internally fixed
   canonical probe path.** `CANONICAL_PROBE_PATH` is derived from the approved
   target, no function here accepts a replacement for it, and a report that
   recorded any other substitution is refused.
4. **The complete normalized applied property set is compared, and a
   systemd/package change invalidates the evidence.** Every compared property
   must appear in the applied set exactly once, with no extra property, and
   equal the deployed value after normalization. The attestation records the
   systemd identity it was made under, and `revalidate_sandbox_attestation()`
   refuses it under any other identity — **even when the deployed unit's bytes
   are unchanged**, because the thing S4-3 attests is systemd's *interpretation*
   of those bytes and an upgrade can change it without changing them.

Every refusal makes S4-3 **`inconclusive`**, never `failed` and never `passed`:
§2.13.2a's reading is that a mismatched directive set means the transient unit
did not exercise the writer's sandbox, so S4-1 and S4-2 attest nothing about it.

## What this module does not do

It reads no file, runs no `systemctl`, starts no unit and inspects no live
system. Its inputs are supplied text and supplied identities, and **supplied
text is not trusted**: the unit text must hash to the digest the deployment
manifest recorded, and every value passes the closed grammar before it is
compared. Producing those inputs on a host is Band 4's job under an approved
plan, and the deployed writer unit itself does not exist yet (reconciliation
row 16).
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

from .approved_target import APPROVED_TARGET
from .errors import ObservationRefused
from .filesystem import ALL_CASES
from .filesystem import BAND as FILESYSTEM_BAND
from .records import CleanupState, EvidenceRecord, Outcome, Status

CASE_ID = "S4-3"

#: The deployed writer unit S4-3 compares against (§2.13.3).
WRITER_UNIT = "freedom-sheet-writer.service"

#: **Condition 3.** The one path the transient unit's `ReadWritePaths=` may be
#: substituted with: the arena, `…/probe`, derived from the approved target and
#: from nothing a caller supplies. No function in this module takes a
#: replacement for it.
CANONICAL_PROBE_PATH = f"{APPROVED_TARGET.root_path}/probe"

#: **Condition 1, drop-ins.** The drop-ins S4-3 accepts beside the unit, by
#: file name under `freedom-sheet-writer.service.d/`. §2.13.3 names none, so the
#: set is empty and every drop-in is refused; admitting one is a design change,
#: not a configuration choice.
SUPPORTED_DROP_INS: frozenset[str] = frozenset()

SECTIONS = frozenset({"Unit", "Service", "Install"})


class Authority(str, Enum):
    """Whether a directive can change what the writer is permitted to do."""

    #: Authority-bearing, and part of the sandbox S4-3 compares.
    SANDBOX = "sandbox"
    #: Authority-bearing, and deliberately **not** compared: the transient unit
    #: runs the case program, not the writer, so these differ by construction.
    #: What runs is bound by the deployment digest (W11), not by S4-3.
    EXECUTION = "execution"
    #: Bears no authority: ordering, description and restart policy.
    LIFECYCLE = "lifecycle"


class ValueForm(str, Enum):
    BOOLEAN = "boolean"
    TOKEN = "token"
    ACCOUNT = "account"
    CAPABILITIES = "capabilities"
    PATHS = "paths"
    TEXT = "text"


@dataclass(frozen=True, slots=True)
class DirectiveSpec:
    section: str
    authority: Authority
    form: ValueForm

    @property
    def authority_bearing(self) -> bool:
        return self.authority is not Authority.LIFECYCLE


#: **Condition 1, directives.** The closed allowlist: §2.13.3's hardened unit,
#: plus the lifecycle directives any unit carries. `systemctl show` reports each
#: SANDBOX directive under its own name.
DIRECTIVES: Mapping[str, DirectiveSpec] = {
    "Description": DirectiveSpec("Unit", Authority.LIFECYCLE, ValueForm.TEXT),
    "Documentation": DirectiveSpec("Unit", Authority.LIFECYCLE, ValueForm.TEXT),
    "After": DirectiveSpec("Unit", Authority.LIFECYCLE, ValueForm.TEXT),
    "Wants": DirectiveSpec("Unit", Authority.LIFECYCLE, ValueForm.TEXT),
    "Type": DirectiveSpec("Service", Authority.EXECUTION, ValueForm.TOKEN),
    "ExecStart": DirectiveSpec("Service", Authority.EXECUTION, ValueForm.TEXT),
    "User": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.ACCOUNT),
    "Group": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.ACCOUNT),
    "NoNewPrivileges": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.BOOLEAN),
    "CapabilityBoundingSet": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.CAPABILITIES),
    "AmbientCapabilities": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.CAPABILITIES),
    "ProtectSystem": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.TOKEN),
    "ProtectHome": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.TOKEN),
    "PrivateTmp": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.BOOLEAN),
    "ProtectProc": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.TOKEN),
    "RestrictSUIDSGID": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.BOOLEAN),
    "ReadOnlyPaths": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.PATHS),
    "ReadWritePaths": DirectiveSpec("Service", Authority.SANDBOX, ValueForm.PATHS),
    "KillSignal": DirectiveSpec("Service", Authority.LIFECYCLE, ValueForm.TOKEN),
    "TimeoutStopSec": DirectiveSpec("Service", Authority.LIFECYCLE, ValueForm.TEXT),
    "Restart": DirectiveSpec("Service", Authority.LIFECYCLE, ValueForm.TOKEN),
    "WantedBy": DirectiveSpec("Install", Authority.LIFECYCLE, ValueForm.TEXT),
}

#: The complete compared property set, in a fixed order. Every one must be
#: assigned exactly once by the deployed unit and reported exactly once by
#: `systemctl show` on the transient unit.
COMPARED_PROPERTIES: tuple[str, ...] = tuple(
    name for name, spec in DIRECTIVES.items() if spec.authority is Authority.SANDBOX
)

_KEY = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_ACCOUNT = re.compile(r"[a-z_][a-z0-9_-]*")
_TOKEN = re.compile(r"[a-z][a-z0-9-]*")
_CAPABILITY = re.compile(r"cap_[a-z_]+")
_PATH = re.compile(r"-?/[A-Za-z0-9._/-]*")
_TRUE = frozenset({"1", "yes", "true", "on"})
_FALSE = frozenset({"0", "no", "false", "off"})


def _normalize(name: str, form: ValueForm, raw: str) -> str:
    """One value in the form `systemctl show` would print it, or a refusal.

    Only authority-bearing values reach here. Anything outside the closed
    grammar is refused rather than guessed at.
    """
    value = raw.strip()
    if any(ch in value for ch in ('%', '"', "'", "\\", "$")):
        raise ObservationRefused(
            f"{name}={raw!r} uses a specifier, quote, escape or variable, which "
            "systemd would interpret and this grammar does not."
        )
    if form is ValueForm.BOOLEAN or (form is ValueForm.TOKEN and value.lower() in _TRUE | _FALSE):
        lowered = value.lower()
        if lowered in _TRUE:
            return "yes"
        if lowered in _FALSE:
            return "no"
        raise ObservationRefused(f"{name}={raw!r} is not a boolean.")
    if form is ValueForm.TOKEN:
        if not _TOKEN.fullmatch(value):
            raise ObservationRefused(f"{name}={raw!r} is not a single lower-case token.")
        return value
    if form is ValueForm.ACCOUNT:
        if not _ACCOUNT.fullmatch(value):
            raise ObservationRefused(f"{name}={raw!r} is not an account name.")
        return value
    if form is ValueForm.CAPABILITIES:
        names = value.split()
        if any(item.startswith("~") for item in names):
            raise ObservationRefused(
                f"{name}={raw!r} inverts a set, whose meaning depends on the "
                "kernel's CAP_LAST_CAP; name the capabilities instead."
            )
        lowered = [item.lower() for item in names]
        if not all(_CAPABILITY.fullmatch(item) for item in lowered):
            raise ObservationRefused(f"{name}={raw!r} names something that is not a capability.")
        if len(set(lowered)) != len(lowered):
            raise ObservationRefused(f"{name}={raw!r} names a capability twice.")
        return " ".join(sorted(lowered))
    if form is ValueForm.PATHS:
        paths = value.split()
        if not paths or not all(_PATH.fullmatch(item) for item in paths):
            raise ObservationRefused(f"{name}={raw!r} is not a list of absolute paths.")
        if any("/../" in f"{item}/" or "/./" in f"{item}/" for item in paths):
            raise ObservationRefused(f"{name}={raw!r} is not a normalized path list.")
        if len(set(paths)) != len(paths):
            raise ObservationRefused(f"{name}={raw!r} names a path twice.")
        return " ".join(sorted(paths))
    raise ObservationRefused(f"{name} has form {form.value}, which is never compared.")


@dataclass(frozen=True, slots=True)
class UnitFile:
    """One file's name and exact text, as the deployment manifest covers it."""

    name: str
    text: str


@dataclass(frozen=True, slots=True)
class DeployedUnit:
    """The deployed writer unit and its drop-ins, as **supplied** — untrusted."""

    unit: UnitFile
    drop_ins: tuple[UnitFile, ...] = ()

    def digest(self) -> str:
        """SHA-256 over every file's name and bytes, drop-ins in name order."""
        payload = json.dumps(
            [[self.unit.name, self.unit.text]]
            + [[item.name, item.text] for item in sorted(self.drop_ins, key=lambda f: f.name)],
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class SystemdIdentity:
    """What interprets the unit: systemd's version and the package providing it."""

    systemd_version: str
    package: str
    package_version: str

    def __post_init__(self) -> None:
        for name in ("systemd_version", "package", "package_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip() or any(ch.isspace() for ch in value):
                raise ObservationRefused(f"A systemd identity's {name} is one non-blank token.")


@dataclass(frozen=True, slots=True)
class ParsedUnit:
    """The outcome of the closed-grammar parse. `refusals` empty means valid."""

    sandbox: tuple[tuple[str, str], ...]
    refusals: tuple[str, ...]


def _parse_file(
    file: UnitFile, assigned: dict[str, str], sandbox: dict[str, str], refusals: list[str]
) -> None:
    section: str | None = None
    for number, line in enumerate(file.text.split("\n"), start=1):
        where = f"{file.name}:{number}"
        stripped = line.strip()
        if "\r" in line:
            refusals.append(f"{where}: carriage return outside the grammar")
            continue
        if not stripped or stripped[0] in "#;":
            continue
        if stripped.endswith("\\"):
            refusals.append(f"{where}: continuation lines are outside the grammar")
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1]
            if section not in SECTIONS:
                refusals.append(f"{where}: unsupported section [{section}]")
                section = None
            continue
        key, sep, value = stripped.partition("=")
        key = key.strip()
        if not sep or not _KEY.fullmatch(key):
            refusals.append(f"{where}: not a Key=Value line")
            continue
        spec = DIRECTIVES.get(key)
        if spec is None:
            refusals.append(f"{where}: unknown directive {key}= is refused")
            continue
        if section != spec.section:
            refusals.append(f"{where}: {key}= outside [{spec.section}]")
            continue
        if not spec.authority_bearing:
            continue
        if key in assigned:
            refusals.append(
                f"{where}: duplicate authority-bearing {key}= (first in {assigned[key]})"
            )
            continue
        assigned[key] = where
        if spec.authority is Authority.SANDBOX:
            try:
                sandbox[key] = _normalize(key, spec.form, value)
            except ObservationRefused as refusal:
                refusals.append(f"{where}: {refusal}")


def parse_deployed_unit(deployed: DeployedUnit) -> ParsedUnit:
    """**Conditions 1 and 2**: the closed-grammar parse of unit and drop-ins.

    Every refusal is collected rather than stopping at the first, so a report
    names each reason — a drop-in outside the allowlist is refused by name *and*
    its contents are still checked for duplicates and unknown directives.
    """
    refusals: list[str] = []
    if deployed.unit.name != WRITER_UNIT:
        refusals.append(f"the unit is {deployed.unit.name!r}, not {WRITER_UNIT!r}")
    assigned: dict[str, str] = {}
    sandbox: dict[str, str] = {}
    _parse_file(deployed.unit, assigned, sandbox, refusals)
    seen_drop_ins: set[str] = set()
    for drop_in in sorted(deployed.drop_ins, key=lambda f: f.name):
        if drop_in.name in seen_drop_ins:
            refusals.append(f"drop-in {drop_in.name!r} is supplied twice")
        seen_drop_ins.add(drop_in.name)
        if drop_in.name not in SUPPORTED_DROP_INS:
            refusals.append(f"drop-in {drop_in.name!r} is not in the supported drop-in allowlist")
        _parse_file(drop_in, assigned, sandbox, refusals)
    for name in COMPARED_PROPERTIES:
        if name not in assigned:
            refusals.append(f"the deployed unit does not assign {name}=")
    return ParsedUnit(
        sandbox=tuple((name, sandbox[name]) for name in COMPARED_PROPERTIES if name in sandbox),
        refusals=tuple(refusals),
    )


def expected_applied_properties(parsed: ParsedUnit) -> tuple[tuple[str, str], ...]:
    """The applied property set the transient unit must show.

    The deployed unit's normalized sandbox, with **only** `ReadWritePaths=`
    replaced — and replaced by `CANONICAL_PROBE_PATH`, which this function takes
    from the module and from no argument (**condition 3**).
    """
    if parsed.refusals:
        raise ObservationRefused("A refused unit has no expected property set.")
    return tuple(
        (name, CANONICAL_PROBE_PATH if name == "ReadWritePaths" else value)
        for name, value in parsed.sandbox
    )


def normalize_applied_show(text: str) -> tuple[dict[str, str], tuple[str, ...]]:
    """`systemctl show` output for the compared properties, normalized.

    **Condition 4**: omitted, duplicated or unrequested properties are refusals,
    and so is any value outside the closed grammar.
    """
    refusals: list[str] = []
    values: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        key, sep, value = line.partition("=")
        if not sep or key not in COMPARED_PROPERTIES:
            refusals.append(f"applied:{number}: unrequested or malformed property {key!r}")
            continue
        if key in values:
            refusals.append(f"applied:{number}: property {key} reported twice")
            continue
        try:
            values[key] = _normalize(key, DIRECTIVES[key].form, value)
        except ObservationRefused as refusal:
            values[key] = "\x00refused"
            refusals.append(f"applied:{number}: {refusal}")
    for name in COMPARED_PROPERTIES:
        if name not in values:
            refusals.append(f"applied: property {name} was not reported")
    return values, tuple(refusals)


def _property_digest(properties: Sequence[tuple[str, str]]) -> str:
    payload = json.dumps(list(properties), separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class SandboxAttestation:
    """What a passing S4-3 establishes, and what invalidates it."""

    deployed_unit_digest: str
    systemd: SystemdIdentity
    substitution: str
    applied_properties: tuple[tuple[str, str], ...]

    @property
    def applied_property_digest(self) -> str:
        return _property_digest(self.applied_properties)


def _compare(expected: Sequence[tuple[str, str]], applied_show: str) -> list[str]:
    applied, refusals = normalize_applied_show(applied_show)
    problems = list(refusals)
    for name, value in expected:
        if name in applied and applied[name] != "\x00refused" and applied[name] != value:
            problems.append(
                f"{name}: applied {applied[name]!r}, expected {value!r}"
            )
    return problems


_EXPECTED = ALL_CASES[CASE_ID].expected


def classify_sandbox_attestation(
    *,
    deployed: DeployedUnit,
    recorded_unit_digest: str,
    recorded_substitution: str,
    applied_show: str,
    systemd: SystemdIdentity,
) -> tuple[EvidenceRecord, SandboxAttestation | None]:
    """S4-3, classified. The only path by which S4-3 can pass.

    `recorded_unit_digest` is what the deployment manifest recorded for the unit
    and its drop-ins; the supplied text must hash to it, or it is not the
    deployed unit. `recorded_substitution` is the `ReadWritePaths=` the probe
    report recorded; it must be `CANONICAL_PROBE_PATH`.
    """
    problems: list[str] = []
    digest = deployed.digest()
    if digest != recorded_unit_digest:
        problems.append(
            "the supplied unit text does not hash to the recorded deployed-unit digest"
        )
    if recorded_substitution != CANONICAL_PROBE_PATH:
        problems.append(
            f"the recorded ReadWritePaths= substitution {recorded_substitution!r} is "
            f"not the canonical probe path {CANONICAL_PROBE_PATH!r}"
        )
    parsed = parse_deployed_unit(deployed)
    problems.extend(parsed.refusals)
    expected: tuple[tuple[str, str], ...] = ()
    if not parsed.refusals:
        expected = expected_applied_properties(parsed)
        problems.extend(_compare(expected, applied_show))

    attestation = None
    if not problems:
        attestation = SandboxAttestation(
            deployed_unit_digest=digest,
            systemd=systemd,
            substitution=CANONICAL_PROBE_PATH,
            applied_properties=expected,
        )
    refusal = None
    if problems:
        refusal = (
            "S4-3 did not establish that the transient unit applied the deployed "
            "writer unit's sandbox, so S4-1 and S4-2 attest nothing about it: "
            + "; ".join(problems)
        )
    record = EvidenceRecord.for_case(
        case_id=CASE_ID,
        band=FILESYSTEM_BAND,
        target_identity="root, reading the transient unit and the deployed unit",
        operation=ALL_CASES[CASE_ID].operation,
        preconditions=(
            "the deployed unit text hashes to the digest the deployment manifest recorded",
            "the transient unit's ReadWritePaths= is the canonical probe path",
        ),
        expected=_EXPECTED,
        observed=_EXPECTED if attestation is not None else Outcome.read(
            f"{len(problems)} S4-3 refusal(s)"
        ),
        case_role=ALL_CASES[CASE_ID].role,
        attribution_refusal=refusal,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail={
            "stage": 4,
            "deployed_unit_digest": digest,
            "systemd_version": systemd.systemd_version,
            "systemd_package": f"{systemd.package}={systemd.package_version}",
            "applied_property_digest": None if attestation is None
            else attestation.applied_property_digest,
            "first_refusal": problems[0] if problems else None,
            "refusal_count": len(problems),
        },
    )
    return record, attestation


def revalidate_sandbox_attestation(
    attestation: SandboxAttestation, *, systemd: SystemdIdentity, applied_show: str
) -> tuple[Status, str]:
    """Whether an earlier S4-3 still describes this host — **condition 4**.

    A different systemd identity invalidates it **whatever the deployed bytes
    are**, because the attestation is about systemd's interpretation of them. A
    re-read applied property set that no longer matches invalidates it too. The
    only answers are `PASSED` and `INCONCLUSIVE`; a fresh `verify-capability`
    run, which is a rotation, is the only way back.
    """
    if systemd != attestation.systemd:
        return (
            Status.INCONCLUSIVE,
            f"invalidated: S4-3 was attested under systemd "
            f"{attestation.systemd.systemd_version} ({attestation.systemd.package}="
            f"{attestation.systemd.package_version}) and this host now runs "
            f"{systemd.systemd_version} ({systemd.package}={systemd.package_version}); "
            "an unchanged deployed unit does not carry the attestation across an "
            "interpreter change",
        )
    problems = _compare(attestation.applied_properties, applied_show)
    if problems:
        return Status.INCONCLUSIVE, "invalidated: " + "; ".join(problems)
    return Status.PASSED, "the recorded systemd identity and applied property set still hold"


__all__ = [
    "Authority",
    "CANONICAL_PROBE_PATH",
    "CASE_ID",
    "COMPARED_PROPERTIES",
    "DIRECTIVES",
    "DeployedUnit",
    "DirectiveSpec",
    "ParsedUnit",
    "SECTIONS",
    "SUPPORTED_DROP_INS",
    "SandboxAttestation",
    "SystemdIdentity",
    "UnitFile",
    "ValueForm",
    "WRITER_UNIT",
    "classify_sandbox_attestation",
    "expected_applied_properties",
    "normalize_applied_show",
    "parse_deployed_unit",
    "revalidate_sandbox_attestation",
]
