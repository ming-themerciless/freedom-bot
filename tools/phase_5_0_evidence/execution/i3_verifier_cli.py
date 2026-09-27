"""The operator entry point for the I3 controlled-write verifier, and nothing else.

    python -m tools.phase_5_0_evidence.execution.i3_verifier_cli
    python -m tools.phase_5_0_evidence.execution.i3_verifier_cli \\
        --arm-i3-controlled-write --identity root
    python -m tools.phase_5_0_evidence.execution.i3_verifier_cli \\
        --arm-i3-controlled-write --identity ubuntu

## Why this module exists

Runner contract r6 §9.3's **I3** closes only through a controlled write in the
exact target filesystem. The C-P5.0-LAB-I3 pass stopped because no reviewed
operator route reached the `linkat` primitive without V7 initialization, a
participant, the harness or `--execute`. This is that route, and it is the only
one: **C-P5.0-LAB-I3-R2**, under Peter's C-P5.0-LAB-I3-D1 ruling.

It is a **separate program from the evidence harness**. It imports neither
`cli.py` nor the executor, the materializer, the case program, the lifecycle
record, the ledger, the lock or any participant, and it defines no option that
could ask for a run, a digest or a target. It takes `SystemIdentityLookup` from
`boundary` — the repository's one reader of the host's accounts — and the
reviewed mechanism from `i3_verifier`.

## Two invocations, two identities, no identity change

`--identity root` runs T1 under V4, §2.3.3 under V5 and P2 under canonical
`R/bin`; `--identity ubuntu` runs T6 under V9. **The program changes no
identity and no capability.** Each invocation proves, before its first write,
that the process already is the named identity — real, effective, saved and
filesystem uid and gid — and records its capability masks. An operator runs the
two invocations separately, each as the identity it names.

## Two gates

**The arm is the command-line flag itself**, not a constant, a default or
anything derived from the environment, and without it this program returns
before it constructs a lookup, a probe or a verifier: it reads no account
database and no filesystem. The verifier it constructs is armed from the same
flag and refuses on its own when it is not, so deleting the early return still
writes nothing — two independent points.

## What it prints, and what it may never print

Every field is a member of a closed vocabulary or a value rebuilt from
integers: statuses, stages, classifications and fates are enumeration values
admitted by membership; object identities are `st_dev:st_ino` rebuilt from two
integers; masks are sixteen hexadecimal digits rebuilt from an integer; the
nonce is thirty-two hexadecimal digits admitted by shape. **No path, no account
name or number read from a host, no directory listing, no environment value and
no exception or operating-system text** can reach standard output or standard
error. The fixed statements `i3_verifier.NOT_ATTRIBUTION` and
`SECUREBITS_NOT_OBSERVED` are printed verbatim, because they are constants.

## Exit status

| Status | Meaning |
|---|---|
| `0` | verified: every context of this invocation published, observed and removed; no residue; every barrier and descriptor finished |
| `3` | not armed. Nothing was read and nothing was written |
| `4` | refused before the first write. Nothing was written |
| `5` | failed after a write, and every object this invocation created was removed through its identity guard, with every barrier and descriptor finished and a clean survey |
| `6` | a condition this program does not classify. Nothing about it is printed |
| `7` | failed and needs an operator: residue, a foreign or replaced object, an occupied name, or a cleanup, barrier, descriptor or survey failure |

Zero never means *"the command ran"*, and zero does not close I3: closing it is
a maintainer decision on reviewed evidence.
"""
from __future__ import annotations

import argparse
import sys
from typing import Collection, Sequence

from .boundary import SystemIdentityLookup
from .i3_verifier import (
    ADMISSION_REFUSALS,
    INVOCATION_CONTEXTS,
    NOT_ATTRIBUTION,
    SECUREBITS_NOT_OBSERVED,
    STAGE_FAILURES,
    CapabilityEvidence,
    ContextId,
    ContextOutcome,
    ContextStatus,
    I3ControlledWriteVerifier,
    Invocation,
    ObjectFate,
    ObjectKind,
    ProcHostProbe,
    Stage,
    Status,
    VerificationRun,
)

#: The flag that arms the verifier. I3-specific on purpose: no other program in
#: the package accepts it, and it arms nothing else.
ARM_FLAG = "--arm-i3-controlled-write"

VERIFIED_EXIT_CODE = 0
NOT_ARMED_EXIT_CODE = 3
REFUSED_EXIT_CODE = 4
FAILED_NO_RESIDUE_EXIT_CODE = 5
UNCLASSIFIED_EXIT_CODE = 6
OPERATOR_ATTENTION_EXIT_CODE = 7

EXIT_CODES: dict[Status, int] = {
    Status.VERIFIED: VERIFIED_EXIT_CODE,
    Status.NOT_ARMED: NOT_ARMED_EXIT_CODE,
    Status.REFUSED_BEFORE_WRITE: REFUSED_EXIT_CODE,
    Status.FAILED_NO_RESIDUE: FAILED_NO_RESIDUE_EXIT_CODE,
    Status.FAILED_OPERATOR_ATTENTION: OPERATOR_ATTENTION_EXIT_CODE,
}

#: What any value outside its closed vocabulary renders as.
UNRECOGNIZED = "unrecognized"

#: What an identity that is not `st_dev:st_ino` renders as.
NO_IDENTITY = "none established"

#: The one classification for an armed invocation that did not name an identity.
INVOCATION_NOT_NAMED = "invocation-identity-not-named"

_ARMED_WITHOUT_IDENTITY = (
    "REFUSED — no identity was named. Nothing was read and nothing was written.\n"
    f"  refusal              : {INVOCATION_NOT_NAMED}\n"
    "  to run               : name --identity root or --identity ubuntu, as that "
    "identity\n"
)


def _member(value: object, vocabulary: Collection[str]) -> str:
    """`value` when it is exactly a string member of a closed set."""
    if isinstance(value, str) and value in vocabulary:
        return value
    return UNRECOGNIZED


def _enum(value: object, kind: type) -> str:
    return value.value if isinstance(value, kind) else UNRECOGNIZED


def _identity(value: object) -> str:
    """`st_dev:st_ino`, rebuilt from its two integers, or a fixed notice."""
    if not isinstance(value, str) or not value:
        return NO_IDENTITY
    device, separator, inode = value.partition(":")
    if separator and device.isdigit() and inode.isdigit():
        if f"{int(device)}:{int(inode)}" == value:
            return value
    return UNRECOGNIZED


def _nonce(value: object) -> str:
    if (
        isinstance(value, str)
        and len(value) == 32
        and all(character in "0123456789abcdef" for character in value)
    ):
        return value
    return UNRECOGNIZED


def _mask(value: object) -> str:
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < 1 << 64:
        return f"{value:016x}"
    return UNRECOGNIZED


def _count(value: object) -> str:
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < 1 << 32:
        return str(value)
    return UNRECOGNIZED


def _mode(value: object) -> str:
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 0o7777:
        return f"{value:04o}"
    return UNRECOGNIZED


def _yes(value: object) -> str:
    return "yes" if value is True else "no"


def _capability_lines(evidence: CapabilityEvidence | None, indent: str) -> list[str]:
    if not isinstance(evidence, CapabilityEvidence):
        return [f"{indent}not observed\n"]
    lines = [
        f"{indent}CapInh {_mask(evidence.cap_inh)}  CapPrm {_mask(evidence.cap_prm)}  "
        f"CapEff {_mask(evidence.cap_eff)}\n",
        f"{indent}CapBnd {_mask(evidence.cap_bnd)}  CapAmb {_mask(evidence.cap_amb)}  "
        f"NoNewPrivs {_count(evidence.no_new_privs)}\n",
    ]
    for membership in evidence.memberships:
        lines.append(
            f"{indent}{membership.name:<20} permitted {_yes(membership.permitted):<3} "
            f"effective {_yes(membership.effective):<3} "
            f"bounding {_yes(membership.bounding):<3} "
            f"inheritable {_yes(membership.inheritable):<3} "
            f"ambient {_yes(membership.ambient)}\n"
        )
    return lines


def _context_lines(outcome: ContextOutcome) -> list[str]:
    status = _enum(outcome.status, ContextStatus)
    lines = [f"  context {_enum(outcome.context, ContextId):<13}: {status}\n"]
    if outcome.status is ContextStatus.NOT_ATTEMPTED:
        return lines
    lines.append(f"      nonce              : {_nonce(outcome.nonce)}\n")
    if outcome.failed_stage is not None:
        lines.append(
            f"      failed at          : {_enum(outcome.failed_stage, Stage)} — "
            f"{_member(outcome.failure, STAGE_FAILURES)}\n"
        )
    lines.append(
        f"      object identity    : {_identity(outcome.object_identity)}\n"
        f"      file mode          : {_mode(outcome.file_mode)}"
        + (" (ownership applied on the descriptor)" if outcome.applied_ownership else "")
        + "\n"
        f"      owner condition    : "
        + (
            "observed — the linking process's filesystem uid owns the file"
            if outcome.owner_condition_observed
            else "not observed"
        )
        + "\n"
        f"      link count         : {_count(outcome.link_count_with_both_names)} with "
        f"both names, {_count(outcome.link_count_after_temporary_removed)} after the "
        "temporary was removed\n"
        f"      payload            : "
        + ("matched through both names" if outcome.payload_matched else "not matched")
        + "\n"
        "      capability at link :\n"
    )
    lines.extend(_capability_lines(outcome.capability_at_link, "          "))
    lines.append(
        "      stages completed   : "
        + (", ".join(_enum(stage, Stage) for stage in outcome.completed) or "none")
        + "\n"
    )
    for tracked in outcome.objects:
        lines.append(
            f"      object             : {_enum(tracked.kind, ObjectKind)} "
            f"{_enum(tracked.fate, ObjectFate)} [{_identity(tracked.identity)}]\n"
        )
    lines.append(
        f"      cleanup barriers   : {_count(outcome.cleanup_barrier_failures)} failed; "
        f"descriptors not released: {_count(outcome.descriptor_release_failures)}\n"
    )
    return lines


def render_not_armed() -> str:
    """The no-flag rendering. It states nothing about a host."""
    return (
        "NOT ARMED — no account database and no filesystem was read, and nothing "
        "was written.\n"
        "  contexts             : root runs "
        + ", ".join(context.value for context in INVOCATION_CONTEXTS[Invocation.ROOT])
        + "; ubuntu runs "
        + ", ".join(
            context.value for context in INVOCATION_CONTEXTS[Invocation.PARTICIPANT]
        )
        + "\n"
        f"  to run               : {ARM_FLAG} --identity root, as root; then "
        f"{ARM_FLAG} --identity ubuntu, as ubuntu. This program changes no identity "
        "and no capability\n"
    )


def render_run(run: VerificationRun) -> str:
    """The complete account of one invocation, in the closed vocabulary."""
    status = _enum(run.status, Status)
    lines = [
        f"I3 CONTROLLED-WRITE VERIFICATION — {status.upper()}\n",
        f"  invocation           : {_enum(run.invocation, Invocation)}\n",
        "  refusal              : "
        + (
            _member(run.refusal, ADMISSION_REFUSALS)
            if run.refusal
            else "none"
        )
        + "\n",
    ]
    if run.status in (Status.NOT_ARMED, Status.REFUSED_BEFORE_WRITE):
        lines.append("  written              : nothing\n")
    else:
        lines.append(
            f"  hard-link policy     : {_count(run.hardlink_policy)}\n"
            "  identity             : proven before the first write — real, "
            "effective, saved and filesystem uid and gid\n"
            "  capability at admission:\n"
        )
        lines.extend(_capability_lines(run.capability_at_admission, "      "))
        for outcome in run.contexts:
            lines.extend(_context_lines(outcome))
        survey = run.survey
        lines.append(
            "  residue survey       : "
            + (
                "not performed"
                if not survey.performed
                else (
                    "failed"
                    if survey.failed
                    else f"{_count(survey.verifier_names_found)} verifier names found; "
                    "canonical root "
                    + ("present" if survey.canonical_root_present else "absent")
                )
            )
            + "\n"
        )
    lines.append(
        f"  descriptors          : {_count(run.unreleased_roles)} directory roles "
        "not released\n"
        f"  statement            : {NOT_ATTRIBUTION}\n"
        f"  not observed         : {SECUREBITS_NOT_OBSERVED}\n"
    )
    return "".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase-5-0-i3-controlled-write",
        description=(
            "The Package 5.0 I3 controlled-write verifier. Without "
            f"{ARM_FLAG} it reads nothing and writes nothing."
        ),
    )
    parser.add_argument(
        ARM_FLAG,
        dest="arm_i3_controlled_write",
        action="store_true",
        help=(
            "Arm the verifier. This is the only route that arms it. It publishes "
            "one fixed harmless payload per context, observes it under both "
            "names, and removes it before reporting."
        ),
    )
    parser.add_argument(
        "--identity",
        choices=tuple(invocation.value for invocation in Invocation),
        default="",
        help=(
            "The identity this process already is. root runs T1, S2.3.3 and P2; "
            "ubuntu runs T6. The program changes no identity."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if not args.arm_i3_controlled_write:
        # **Nothing above this line reads anything, and nothing below it runs.**
        sys.stdout.write(render_not_armed())
        return NOT_ARMED_EXIT_CODE

    if not args.identity:
        sys.stdout.write(_ARMED_WITHOUT_IDENTITY)
        sys.stderr.write(f"REFUSED — {INVOCATION_NOT_NAMED}.\n")
        return REFUSED_EXIT_CODE

    try:
        verifier = I3ControlledWriteVerifier(
            lookup=SystemIdentityLookup(),
            probe=ProcHostProbe(),
            armed=args.arm_i3_controlled_write,
        )
        run = verifier.run(args.identity)
        rendered = render_run(run)
    except Exception:  # noqa: BLE001 - see the status table
        # **Deliberately says nothing about what happened.** The verifier
        # classifies every condition it anticipates; one that escapes it is a
        # condition nobody has established is safe to print.
        sys.stdout.write(
            "UNCLASSIFIED — this program does not classify what stopped the "
            "run, and states nothing about it. Inspect the four publication "
            "directories and canonical R by hand before any retry.\n"
        )
        sys.stderr.write("UNCLASSIFIED — the run did not reach a result.\n")
        return UNCLASSIFIED_EXIT_CODE

    sys.stdout.write(rendered)
    code = EXIT_CODES.get(run.status, UNCLASSIFIED_EXIT_CODE)
    if code != VERIFIED_EXIT_CODE:
        sys.stderr.write(f"NOT VERIFIED — {_enum(run.status, Status)}.\n")
    return code


if __name__ == "__main__":  # pragma: no cover - the entry point itself
    raise SystemExit(main())
