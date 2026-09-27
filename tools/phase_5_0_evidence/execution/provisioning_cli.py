"""The operator entry point for the reviewed directory provisioner, and nothing else.

    python -m tools.phase_5_0_evidence.execution.provisioning_cli
    python -m tools.phase_5_0_evidence.execution.provisioning_cli --apply

## Why this module exists

`execution/provisioner.py` is the reviewed applier for the four directory items
of the released prerequisite subset — V12, V4, V9 and V5. It has no `main`, and
until this module there was **no repository-owned way for an operator to reach
it as approved**: the only armed construction anywhere was a test's, over a
temporary directory with an injected account lookup. That gap is RAID
**LAB-V6-P1**, it stopped the C-P5.0-LAB-V6-P operational pass before its first
mutation, and this module is the bounded thing Peter authorized to close it
(**C-P5.0-LAB-V6-P-R1**).

It is a **separate program from the evidence harness**. `cli.py` is the only
entry point that can reach the executing runner and owns `--execute`; this one
imports neither it nor the executor, the materializer, the case program, the
lifecycle record, the ledger, the lock or any participant, and it defines no
option that could ask for a run. The one thing it takes from `boundary` is
`SystemIdentityLookup`, which is the account-database seam the provisioner
declares — so the repository still has exactly one class that reads the host's
accounts, and this program does not become a second one.

## The whole production path, in four statements

1. `directory_targets()` — **called with no arguments**, so the production V12,
   V4, V9 and V5 values and their reviewed order are the ones applied. There is
   no option, environment variable or default in this module that could supply
   an alternate layout, path, owner, group or mode. Not one of those values is
   written down here: restating them would make this file a second definition of
   what the maintainer approved;
2. `SystemIdentityLookup()` over the host account database. Constructing it
   reads nothing; the two reads it performs happen inside the provisioner, at
   the moment an item's owner and group are resolved;
3. `DirectoryProvisioner(lookup=…, armed=args.apply)`. **The arm is the
   command-line flag itself**, not a constant, not a default and not anything
   derived from the environment. A provisioner is never constructed at all on
   the path that has no flag, and if that early return were deleted the
   construction that followed would still be unarmed — two independent points,
   because a single-point reversal is what a guard like this exists to survive;
   and
4. `apply(targets)`, whose returned `ProvisioningRun` is rendered complete.

## What `--apply` does not do

It does not `sudo`, change identity, consult the environment, start a process or
shell out. **The process must already be effective UID 0**, as the reviewed
provisioner requires: `_require_provisioning_identity` refuses before the first
`mkdirat` when it is not, and this program has no way to make it so.

V1 (`groupadd`), V2 (`usermod`) and V3 (the `systemd-tmpfiles` fragment) are the
separately reviewed **operator** steps and are not implemented, executed or
wrapped here. This entry point owns V12, V4, V9 and V5 and no other item; the
later operational pass retains the approved whole-subset order V1, V2, V3, V12,
V4, V9, V5. V7 stays excluded and the provisioner refuses it by name, so nothing
here initializes `lifecycle.json`.

There is no repair mode and **no automatic rollback**. Reversing a partly
provisioned host is the operator's decision, taken on each item's reviewed
`rollback` field; this program renders what is on disk and stops.

## What it prints, and what it may never print

The complete account of the run goes to standard output — every applied item
with its `created` / `already-provisioned` outcome and recorded object identity,
the refusal's item, classification and detail when there is one, and every item
that was never attempted. A refused run additionally puts one fixed line on
standard error, so a run whose output was redirected still says so.

Every fragment of that account comes from a **closed vocabulary**, and every
one of them is admitted by **being exactly a member of it** rather than by
looking like one. That distinction is the whole of this section. A rule that
admitted a value because its characters were ordinary would print `hunter2`, a
token and a database password read out of a crash, because those are ordinary
characters; so no field here is admitted on its characters.

* **An item identifier and a path are admitted only by identity with what this
  program handed to the applier.** The targets `directory_targets()` built are
  the vocabulary, this module writes none of their values down, and anything
  arriving back that is not one of them is named as unrecognized or withheld.
* **A classification is checked against the provisioner's closed set**, imported
  rather than restated. One that is not in it renders as
  `unrecognized-classification` and says nothing else.
* **A detail is admitted only by `provisioner.is_reviewed_refusal_detail`,
  asked about the value exactly as supplied** — the applier's own contract,
  which answers *is this, in whole, a detail I produce?*. Every fixed detail is
  a named constant there; the two that carry finite variation are built from
  the closed observation vocabulary and are admitted by reconstructing them
  exactly. Ordinary prose that no refusal raises is withheld **whole**, however
  harmless its characters look — and so is a value that is merely one space,
  tab or newline away from a reviewed detail, because **nothing normalizes a
  candidate before the contract is asked** (`PR-20260918-LAB-V6P-R2-1`).
* **An object identity is admitted by rebuilding it** from the two integers it
  is, so `st_dev:st_ino` is the only thing that shape can carry.
* **Every admitted field is then collapsed to one line, stripped of
  non-printable characters and truncated at `FIELD_WIDTH`.** That is defence in
  depth over values already established as safe — it is never what establishes
  them, and it never runs on a value the contract has not already admitted. It
  rewrites no reviewed value; a later one it would rewrite fails the suite
  rather than weakening the exact contract in silence.

So no raw exception text, no operating-system message, no traceback, no
account-database record, no directory listing, no environment value and no
secret can reach this surface. Adding a detail to the applier does not make it
printable here either: it is printable when it is admitted to the applier's
`REVIEWED_DETAILS`, which is an act rather than a side effect.

## Exit status

| Status | Meaning |
|---|---|
| `0` | every one of the four items was created or verified already compliant |
| `3` | nothing was applied, because `--apply` was not given. No account database and no filesystem was read |
| `4` | the run refused or was incomplete. What exists is in the account on standard output |
| `6` | a condition this program does not classify. Nothing about it is printed, because nothing about it is known to be safe to print |

Zero means the whole reviewed delta this tool owns is in place. It never means
*"the command ran"*.
"""
from __future__ import annotations

import argparse
import sys
from typing import Collection, Sequence

from ..provisioning import APPLIED_DIRECTORY_ITEMS
from .boundary import SystemIdentityLookup
from .provisioner import (
    PROVISIONER_REFUSALS,
    AppliedItem,
    DirectoryProvisioner,
    DirectoryTarget,
    Outcome,
    ProvisioningRefused,
    ProvisioningRun,
    directory_targets,
    is_reviewed_refusal_detail,
)

#: Every reviewed item completed or was verified already compliant. The only
#: status that says the delta this tool owns is in place.
COMPLETED_EXIT_CODE = 0

#: `--apply` was not given. Distinct from success because nothing was applied,
#: and distinct from a refusal because nothing was attempted: no account
#: database and no filesystem was read on this path.
NOT_APPLIED_EXIT_CODE = 3

#: The run refused, or ended with an item unapplied. Distinct from `1` so that
#: *"the host is not provisioned as reviewed"* is never the same as *"something
#: went wrong in this program"*.
REFUSED_EXIT_CODE = 4

#: A condition this program does not classify. The provisioner classifies every
#: refusal it raises, so reaching this means something outside that vocabulary
#: happened; it is reported as unclassified and **nothing about it is printed**,
#: because an unclassified condition is exactly the one whose text nobody has
#: established is safe for an operator-facing surface.
UNCLASSIFIED_EXIT_CODE = 6

#: The width every rendered field is truncated at. The identifiers, paths,
#: classifications and details this program renders are all fixed values from the
#: reviewed definitions, and it is wide enough that none of them is truncated —
#: `test_no_reviewed_detail_is_truncated_by_the_bound` asserts that against the
#: applier's own details, so a longer one added later fails the suite rather than
#: reaching an operator with its end missing. It is here so that the bound is a
#: property of the renderer rather than of its inputs.
FIELD_WIDTH = 600

#: What an item with no recorded `(st_dev, st_ino)` renders as. An
#: already-provisioned object is somebody else's and was never identified here;
#: a created one without an identity is residue, and saying so is the point.
NO_IDENTITY = "none recorded"

#: What a classification outside the provisioner's closed vocabulary renders as.
#: The vocabulary is a frozenset this module imports rather than restates, so
#: *this is not one of the reviewed refusals* is decidable rather than assumed.
UNRECOGNIZED_CLASSIFICATION = "unrecognized-classification"

#: What a detail the applier's contract does not admit renders as. **Withheld
#: whole, never in part.** The rule this replaced admitted a detail whose
#: characters were ordinary, and `hunter2`, a token and a database password are
#: ordinary characters — so the admission is now identity with a detail the
#: applier produces, and everything else is this sentence.
WITHHELD_DETAIL = (
    "withheld — this is not one of the reviewed refusal details, and nothing "
    "established that it is safe to show"
)

#: What an item identifier that is not one of the ones handed to the applier
#: renders as. It is named rather than printed for the same reason a detail is:
#: the identifiers this program may print are the ones it supplied.
UNRECOGNIZED_ITEM = "unrecognized-item"

#: What a path that is not one of the reviewed targets renders as. A path is the
#: field an operating-system message arrives in most often, so it is admitted by
#: identity with what this program handed over and by nothing else.
WITHHELD_PATH = "withheld — not one of the reviewed target paths"

#: What an object identity that is not `st_dev:st_ino` renders as.
WITHHELD_IDENTITY = "withheld — not a recorded object identity"


def _bounded(text: str) -> str:
    """One printable line, at most `FIELD_WIDTH` characters.

    Whitespace is collapsed so a multi-line value cannot become a multi-line
    field, non-printable characters are dropped so nothing can address an
    operator's terminal rather than being read by it, and the result is
    truncated so a field is bounded by this function rather than by its input.
    """
    collapsed = " ".join(str(text).split())
    printable = "".join(character for character in collapsed if character.isprintable())
    if len(printable) <= FIELD_WIDTH:
        return printable
    return printable[: FIELD_WIDTH - 1] + "…"


def _classification(value: str) -> str:
    """The refusal's classification, or the fixed notice that it is not one."""
    if value in PROVISIONER_REFUSALS:
        return value
    return UNRECOGNIZED_CLASSIFICATION


def _admitted(value: str, vocabulary: Collection[str], withheld: str) -> str:
    """`value` when it is exactly a member of a closed set, and `withheld` if not.

    Membership, never resemblance. The bound is applied after the admission and
    to an admitted value only, so it is defence in depth rather than the thing
    that decided the value was safe.
    """
    return _bounded(value) if value in vocabulary else withheld


def _detail(text: str, item_ids: Collection[str] = APPLIED_DIRECTORY_ITEMS) -> str:
    """The refusal's detail when the applier's contract admits it, and nothing if not.

    **The applier owns the answer, and it is asked about the value as supplied.**
    `is_reviewed_refusal_detail` asks whether the complete value is one of the
    details `provisioner.py` produces — in the bare form a raised refusal
    carries or the composed `classification: item_id — detail` form `apply()`
    records — and nothing about the characters it is written in is consulted.
    `item_ids` is the closed set of identifiers this program handed over, so the
    composed form cannot be admitted around an item nobody supplied.

    **Nothing happens to a candidate before that question is answered.**
    `PR-20260918-LAB-V6P-R2-1`: this function used to collapse whitespace and
    ask about the collapsed value, so a value that was *not* a reviewed detail
    became one on the way in — a leading or trailing space, a doubled internal
    space, or a tab, newline or carriage return where a reviewed detail has a
    space, all normalized into the reviewed sentence and were printed as it.
    Whatever is admitted must therefore be the supplied value **character for
    character**: no trim, no split, no collapse, no case-folding, no Unicode
    normalization, no control-character removal and no truncation stands
    between the candidate and the contract. A value that is one space away from
    a reviewed detail is not that detail, and is withheld whole like any other
    unreviewed text.

    `_bounded` still runs — but only on a value the contract has already
    admitted, which is what makes it defence in depth rather than the thing
    that decided the value was safe. It changes no reviewed value:
    `test_the_bound_alters_no_admitted_value` asserts that against every detail
    the applier can actually produce, bare and composed, so a detail added
    later that the bound *would* rewrite fails the suite rather than quietly
    weakening this contract.

    A non-string is withheld rather than converted, for the same reason: `str()`
    is a transformation, and one applied to an object this program has not
    established anything about could render that object's text.
    """
    if isinstance(text, str) and is_reviewed_refusal_detail(text, item_ids):
        return _bounded(text)
    return WITHHELD_DETAIL


def _identity(value: str) -> str:
    """The recorded `st_dev:st_ino`, rebuilt, or the fixed notice that it is not one.

    The applier records an object's identity as two integers joined by a colon.
    This admits it by **parsing those two integers and rendering them back**: a
    value is shown only when doing so reproduces it character for character, so
    the field cannot carry anything a pair of integers cannot.
    """
    if not value:
        return NO_IDENTITY
    device, separator, inode = value.partition(":")
    if separator and device.isdigit() and inode.isdigit():
        if f"{int(device)}:{int(inode)}" == value:
            return value
    return WITHHELD_IDENTITY


def _item_line(
    item: AppliedItem, item_ids: Collection[str], paths: Collection[str]
) -> str:
    return (
        f"      · {_admitted(item.item_id, item_ids, UNRECOGNIZED_ITEM):<4} "
        f"{_bounded(item.outcome.value):<24} "
        f"{_admitted(item.path, paths, WITHHELD_PATH)}  "
        f"[{_identity(item.object_id)}]\n"
    )


def _names(items: Sequence[AppliedItem], item_ids: Collection[str]) -> str:
    return (
        ", ".join(
            _admitted(item.item_id, item_ids, UNRECOGNIZED_ITEM) for item in items
        )
        or "none"
    )


def render_not_applied() -> str:
    """The no-flag rendering: the fixed identifiers, and no claim about a host.

    It names the four items this tool owns, because they are a constant of the
    reviewed release and reading them is not reading a host. It states that
    nothing was read and nothing was applied, because the one thing this output
    must never be mistaken for is the account of a run.
    """
    return (
        "NOT APPLIED — no account database and no filesystem was read.\n"
        f"  items this tool owns : {', '.join(APPLIED_DIRECTORY_ITEMS)}\n"
        "  applied              : none. No object was made, adopted, repaired "
        "or removed, and this program states nothing about the host\n"
        "  to apply             : re-run with --apply, as effective UID 0. The "
        "reviewed operator steps V1, V2 and V3 are not performed by this "
        "program\n"
    )


def render_run(
    run: ProvisioningRun, completed: bool, targets: Sequence[DirectoryTarget]
) -> str:
    """The complete account of one application: applied, refused, not attempted.

    `targets` is what this program handed to the applier, and it is the closed
    vocabulary every identifier and path in the account is admitted against.
    Passing it rather than consulting the reviewed definitions again keeps this
    module free of a second statement of an approved value, and makes *"the
    applier answered about an item nobody supplied"* visible instead of printed.
    """
    item_ids = frozenset(target.item_id for target in targets)
    paths = frozenset(target.path for target in targets)
    header = (
        "APPLIED — every item this tool owns is in place.\n"
        if completed
        else "REFUSED — the run did not complete. Nothing was rolled back.\n"
    )
    lines = [header, f"  items applied        : {len(run.applied)}\n"]
    lines.extend(_item_line(item, item_ids, paths) for item in run.applied)
    refusal = run.refusal
    if refusal is None:
        lines.append("  refusal              : none\n")
    else:
        lines.append(
            "  refusal              : "
            f"{_admitted(refusal.item_id, item_ids, UNRECOGNIZED_ITEM)} "
            f"— {_classification(refusal.classification)}\n"
            f"      detail: {_detail(refusal.detail, item_ids)}\n"
        )
    lines.append(
        "  not attempted        : "
        + (
            ", ".join(
                _admitted(name, item_ids, UNRECOGNIZED_ITEM)
                for name in run.not_attempted
            )
            or "none"
        )
        + "\n"
    )
    lines.append(f"  created by this run  : {_names(run.created, item_ids)}\n")
    lines.append(f"  unidentified residue : {_names(run.unidentified, item_ids)}\n")
    lines.append(
        "  guarded reversal     : "
        + (
            f"available for {_names(run.removable, item_ids)}"
            if run.recoverable
            else "refused while an unidentified object created by this run is "
            "present"
        )
        + ". No rollback is performed by this program; reversing a partly "
        "provisioned host is the operator's decision\n"
    )
    return "".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase-5-0-provision-directories",
        description=(
            "Apply the reviewed Package 5.0 directory items V12, V4, V9 and V5 "
            "through the reviewed provisioner, as effective UID 0. Without "
            "--apply it reads nothing and applies nothing."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Arm the reviewed provisioner and apply the four directory items at "
            "their production locations. This is the only route that arms it. "
            "The process must already be effective UID 0; this program does not "
            "elevate, and it performs the operator steps V1, V2 and V3 for "
            "nobody."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if not args.apply:
        # **Nothing above this line reads anything, and nothing below it runs.**
        # No lookup is constructed, no provisioner is assembled and no target is
        # built, so a default invocation cannot read the account database, cannot
        # touch the filesystem and has nothing to report about a host.
        sys.stdout.write(render_not_applied())
        return NOT_APPLIED_EXIT_CODE

    try:
        targets = directory_targets()
        provisioner = DirectoryProvisioner(
            lookup=SystemIdentityLookup(), armed=args.apply
        )
        run = provisioner.apply(targets)
    except ProvisioningRefused as refusal:
        # The reviewed classifications are a closed vocabulary and their details
        # are fixed prose, so this is the one exception whose text is safe to
        # show. `apply()` returns its refusals rather than raising; this covers
        # the ones raised while the targets are being built.
        # No target was built, so the identifiers this program supplied are the
        # four fixed ones the reviewed release names — the same closed set the
        # inert rendering prints.
        sys.stdout.write(
            "REFUSED — no item was attempted.\n"
            "  refusal              : "
            f"{_admitted(refusal.item_id, APPLIED_DIRECTORY_ITEMS, UNRECOGNIZED_ITEM)} "
            f"— {_classification(refusal.classification)}\n"
            f"      detail: {_detail(refusal.detail)}\n"
            "  applied              : none\n"
        )
        sys.stderr.write(
            f"REFUSED — {_classification(refusal.classification)} on "
            f"{_admitted(refusal.item_id, APPLIED_DIRECTORY_ITEMS, UNRECOGNIZED_ITEM)}.\n"
        )
        return REFUSED_EXIT_CODE
    except Exception:  # noqa: BLE001 - see the status table and the comment below
        # **Deliberately says nothing about what happened.** Every condition the
        # reviewed mechanism anticipates arrives as a classified refusal; one
        # that does not is a condition nobody has established is safe to put in
        # front of an operator, and an exception's text can carry a path, an
        # account record, a directory's contents or an operating-system message.
        # It is reported as unclassified, with the state of the host unstated
        # because this program does not know it.
        sys.stdout.write(
            "UNCLASSIFIED — this program does not classify what stopped the "
            "run, and states nothing about it.\n"
            "  applied              : unknown to this program. Inspect the "
            "items by hand before any retry\n"
        )
        sys.stderr.write("UNCLASSIFIED — the run did not reach a result.\n")
        return UNCLASSIFIED_EXIT_CODE

    completed = (
        run.complete
        and len(run.applied) == len(targets)
        and not run.unidentified
        and all(
            item.outcome is Outcome.CREATED
            or item.outcome is Outcome.ALREADY_PROVISIONED
            for item in run.applied
        )
    )
    sys.stdout.write(render_run(run, completed, targets))
    if completed:
        return COMPLETED_EXIT_CODE
    if run.refusal is not None:
        supplied = frozenset(target.item_id for target in targets)
        sys.stderr.write(
            f"REFUSED — {_classification(run.refusal.classification)} on "
            f"{_admitted(run.refusal.item_id, supplied, UNRECOGNIZED_ITEM)}.\n"
        )
    else:
        sys.stderr.write("REFUSED — the run did not complete.\n")
    return REFUSED_EXIT_CODE


if __name__ == "__main__":  # pragma: no cover - the entry point itself
    raise SystemExit(main())
