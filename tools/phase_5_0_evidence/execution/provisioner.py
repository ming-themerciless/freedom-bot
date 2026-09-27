"""The r6 §7 directory items, applied — idempotently, fail-closed, or not at all.

## What this module is

`provisioning.py` holds the reviewed **definitions**: eleven r6 §7 items, each
with an exact owner, group, numeric mode, creation mechanism, persistence
behaviour, rationale, verification and rollback. This module is the one thing in
the repository that would **create** any of them, and it creates exactly four:
`APPLIED_DIRECTORY_ITEMS`, the directory items of the approved prerequisite
subset. It is in the execution tier for that reason and for no other.

**What it does not do**, stated before what it does:

* it does not create a group, add a membership, write under `/etc` or create
  anything on tmpfs. V1, V2 and V3 are operator steps and each item states its
  exact command;
* it does not initialize `lifecycle.json`. **V7 is excluded from this release**
  — `provisioning.V7_EXCLUSION` — and `ensure()` refuses it by name, because
  §5.10's first use is an exclusive `linkat` on the target and **I3** is
  unconfirmed;
* it does not create a parent it was not given an item for. V12 **is** an item —
  the persistent `/var/lib/freedom-blades` V4 and V5 hang from, approved on
  2026-09-17 — and it is created by the same sequence as the other three. Its
  own parent, `/var/lib`, is not, and an absent or unsafe parent anywhere is a
  **refusal**. `provisioning.PREREQUISITE_PARENTS` is now empty, which is what
  that disposition left: no parent of an applied item is undefined;
* it does not repair. An object already at a name with the wrong type, owner,
  group, mode, link count or content refuses and is left exactly as it is; and
* it reaches no path of its own. Every directory it touches comes from a
  `DirectoryTarget` a caller built, which is what lets the whole mechanism be
  driven over a temporary directory without creating one object under `/run`,
  `/var/lib`, `/opt/freedom-blades` or `/etc`.

## Fail-closed, in the two places it matters

**Nothing is armed by default.** `armed` is `False` and an unarmed provisioner
refuses every creation, so an instance assembled by mistake still changes
nothing. Arming is one explicit act by whoever runs it.

**The provisioning process must be the owner the items declare.** Each item says
its object is `root`-owned; `_require_provisioning_identity` refuses unless the
process's own effective UID already **is** the uid that owner resolves to. A run
started as `ubuntu` therefore refuses before it creates anything, rather than
creating four directories it cannot chown and leaving a half-provisioned host.
The same rule is what lets the suite drive the real code: a test injects a
lookup that resolves the declared owner to the test process's own ids, and the
mechanism is unchanged.

**And the parent must already be that identity's alone.** A directory `0700
root:root` under a parent an ordinary identity may write is not a root-only
object: the parent's write permission governs renaming and unlinking the
**entry**, whatever the entry's own mode says. So the precondition is that the
parent is owned by the provisioning identity and carries no group- or
other-write bit. On the target that reads as *root-owned and not group- or
other-writable*, which is exactly r6 §1.4.1's root-only [A].

This is the rule that decided the 2026-09-17 topology. `/opt/freedom-blades`,
observed `1001:1001 0755`, is writable by the identity every participant runs
as, so anything provisioned under it would have had a root-only object behind an
entry `ubuntu` could rename — and the applier refused it `parent-unsafe-ownership`
rather than provisioning under it. **The maintainer withdrew that location
instead of widening the rule**: V11 and `/opt/freedom-blades/evidence` are gone,
no ownership change to `/opt/freedom-blades` is made, and no applied item has a
parent there any more. The four remaining targets sit under `/var/lib`, which
already satisfies the precondition.

## The sequence, once, because every item uses the same one

1. resolve the item's owner and group **names** through the injected lookup;
2. open the parent twice — `O_PATH|O_NOFOLLOW|O_DIRECTORY` for traversal and a
   separately resolved `O_RDONLY|O_NOFOLLOW|O_DIRECTORY` whose `fstat` is
   **compared** with the first's, r6 §1.3.2's rule for a provisioned root;
3. check the parent's ownership and write bits;
4. `fstatat` the name under the traversal descriptor:
   * **present** — verify it completely and return `ALREADY_PROVISIONED`
     without writing a byte. That is the idempotence, and it is a verification
     rather than a `mkdir` whose `EEXIST` is swallowed;
   * **absent** — `mkdirat(parent, name, mode)` **exclusively**, so `EEXIST` is
     a refusal and success is the ownership proof;
5. open the new directory `O_RDONLY|O_NOFOLLOW|O_DIRECTORY` under the traversal
   descriptor and issue `fchown` and `fchmod` on **that descriptor**. The umask
   does not decide the mode, no pathname is resolved a second time between the
   creation and the ownership, and V9's setgid and sticky bits survive — a
   `mkdir` mode argument is masked and cannot carry them predictably;
6. verify the result from the same descriptor, and refuse if it disagrees; and
7. `fsync` the parent's synchronizable descriptor — the containing-entry
   barrier, without which the new entry is visible and would not survive a power
   loss. Whether a directory `fsync` really is that barrier on the target is
   **V8/I2** and is unconfirmed; the call is issued where the contract requires
   it.

## Fail-closed after the `mkdirat`, too — C-P5.0-LAB-V6-R2

The two gates above decide whether anything is created. This one decides what
happens once something **has** been, and it is the repair of Codex Blocking
finding **PR-20260916-LAB-V6R1-1**.

Step 4's `mkdirat` is the line. Before it, a failure means nothing exists and
the refusal is the whole story. After it, a directory is on disk at a
provisioned name, and two rules hold without exception:

* **no expected operating-system failure escapes.** The open of the created
  directory, `fchown`, `fchmod`, the read-back's own `fstat`, a read-back that
  disagrees and the parent's barrier are each translated into
  `POST_CREATION_REFUSALS` — closed classifications that name no path, no
  content and no `errno` text. A raw `OSError` reaching a caller would be a
  refusal nobody classified, about an object nobody recorded; and
* **the object travels with the refusal.** `ProvisioningRefused.partial`
  carries the `AppliedItem`, `apply()` puts it in the returned
  `ProvisioningRun.applied`, and `created` therefore includes it. A result that
  said `applied == ()` while a root-owned directory sat at the target is the
  defect this closes, and the live provisioner's private `_created` list was
  never evidence an operator could read.

**Identity is preserved wherever the object can still be observed, and claimed
nowhere else.** Every failure after the open still holds the descriptor the
creation opened, so `(st_dev, st_ino)` comes from the object itself and a
guarded reversal remains possible. If the open is what failed, there is no such
descriptor and resolving the name again would record an identity this
application cannot attribute to its own `mkdirat`. That case is
`Outcome.CREATED_IDENTITY_UNKNOWN`: reported as residue, counted in `created`,
excluded from `removable`, and `rollback()` refuses the **whole** reversal while
one is present rather than removing what it can and stopping.

Nothing here adds automatic rollback to `apply()`. Reversing a partly
provisioned host stays the operator's decision.

## The last thing each of those does is release a descriptor — C-P5.0-LAB-V6-R3

The six failure points above are the operations. Releasing the descriptor they
were issued through is what comes after each of them, and it is itself an
operation that can fail. Three descriptors are released on the application path:
the one opened on the created object at the end of `_complete_creation`, and the
parent's synchronizable and traversal descriptors in `ensure`. This is the
repair of Codex Blocking finding **PR-20260916-LAB-V6R2-1**, reproduced by
closing the first of them for real and then reporting failure: an
`OSError` escaped raw, `ProvisioningRun` was never returned, and `created` was
empty while the directory sat at the target.

**Releasing reports; it does not raise.** `_release` returns whether the system
said the release worked, which makes two different situations distinguishable
where a `finally: os.close(fd)` conflated them:

* **a refusal is already in flight.** It is the causal one, it already carries
  the object, and it is preserved exactly. A cleanup failure that replaced an
  ownership, mode, read-back, barrier or parent refusal would hand an operator a
  fact about a descriptor in place of the fact about their object. Both
  descriptors are still released, whichever reports first, so a failure on one
  does not leak the other; and
* **nothing else failed.** Then the failure to release is the whole story, and
  it is `DESCRIPTOR_NOT_RELEASED` — a seventh member of
  `POST_CREATION_REFUSALS`, carrying the result the item had already reached.
  The created object keeps the `(st_dev, st_ino)` the read-back established, so
  guarded rollback stays available; an already-provisioned object keeps that
  outcome and stays out of `created`. **No `AppliedItem` is built twice**: the
  refusal carries the one that exists, so the returned run and the provisioner's
  own account of what it created still agree.

**An ambiguous close is treated as ambiguous.** The descriptor is not reused, and
`close()` is not retried on it — a second `close()` of a number the kernel has
already released can close a descriptor something else has since been handed.
Nothing here establishes that the descriptor leaked and nothing establishes that
it did not; what is refused on is this application's inability to say the step
finished cleanly.

## The same rule for verification and for reversal — C-P5.0-LAB-V6-R4

The section above covers the three descriptors the **application** path holds.
Four more were released with a bare `os.close` that still raised, and they are
Codex Blocking finding **PR-20260916-LAB-V6R3-1**: the observed object's and its
parent's in `_verify_one`, and the same pair in `_remove`. Each broke a public
operation in its own way.

**`verify()` returns findings, so a release failure is a finding.** The V6
re-observation's contract is to observe every target and report the whole
picture; raising abandoned every later target, and it could abandon them over a
descriptor rather than over anything about an object. A release that does not
report success is now `DESCRIPTOR_NOT_RELEASED` **appended** to that item's
`ItemObservation.discrepancies` — the owner, group, mode, link count and content
already read stay exactly as true as they were — and the loop goes on to the
next target. `OBSERVATION_DISCREPANCIES` is that closed vocabulary.

**The same condition through `ensure()` is a closed refusal.** `_existing()`
reaches `_verify_one` on the application path, where a raw `OSError` would be a
refusal nobody classified. The object's own findings decide first: if the object
disagrees with its definition, that disagreement is the refusal and the release
failure does not displace it. If the object matches, the release failure is the
whole story — `DESCRIPTOR_NOT_RELEASED`, carrying the `ALREADY_PROVISIONED`
result the verification reached, exactly once, with `created` still empty
because nothing was created.

**A reversal reports what it removed.** `_remove` releases both descriptors
through `_release`, and the `rmdir` is the line either side of which a release
failure is a different fact. Before it, the refusal already in flight — an
identity mismatch, a directory that is not empty — is the causal one and is
preserved; a failure with nothing in flight means the `rmdir` is **not issued**
and nothing is removed, `ROLLBACK_NOT_REMOVED_NOT_RELEASED`. After it, the
object is gone: `RemovalEffect.REMOVED_NOT_FINALIZED` says so, `rollback()`
drops it from `created` and raises `ROLLBACK_REMOVED_NOT_RELEASED` carrying it
in the refusal's `removed` account. `RollbackRefused` makes the disagreeing
combination unconstructible, so a refusal cannot say an object is still on the
host when it is not.

## What a successful application does not establish

Nothing about **I3**: no link is created here, and `fs.protected_hardlinks` is
read by the verification and acted on by nobody. Nothing about **V8**, **V10**,
`plan.is_executable` — which stays `False` — or
`reservation.REAL_EXECUTION_REFUSAL`, which stays unconditional. A provisioned
host is a host on which the refusals can be reached honestly. It is not a host
that may run anything.
"""
from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Collection, Protocol, Sequence

from ..errors import HarnessError
from ..provisioning import (
    APPLIED_DIRECTORY_ITEMS,
    LABORATORY_LAYOUT,
    LaboratoryLayout,
    ProvisioningItem,
    ProvisioningKind,
    RELEASED_PREREQUISITE_SUBSET,
    items_by_id,
)

# ---------------------------------------------------------------------------
# The closed refusal vocabulary
# ---------------------------------------------------------------------------

#: An operator sees which rule refused and for which **item**. No refusal below
#: carries a pathname, a byte of content or an operating-system message, so a
#: refusal is safe to put in an operator-facing artifact — the same rule
#: `descriptors.DescriptorRefused` follows, for the same reason.
PROVISIONER_NOT_ARMED = "provisioner-not-armed"
PROVISIONING_IDENTITY_REFUSED = "provisioning-identity-refused"
ITEM_NOT_RELEASED = "item-not-in-this-release"
ITEM_NOT_A_DIRECTORY = "item-not-applied-by-this-tool"
IDENTITY_UNKNOWN = "identity-unknown"
PARENT_ABSENT = "parent-absent"
PARENT_NOT_A_DIRECTORY = "parent-not-a-directory"
PARENT_UNSAFE_OWNERSHIP = "parent-unsafe-ownership"
PARENT_REPLACED = "parent-replaced-between-lookups"
OBJECT_WRONG_TYPE = "object-wrong-type"
OBJECT_WRONG_OWNER = "object-wrong-owner"
OBJECT_WRONG_GROUP = "object-wrong-group"
OBJECT_WRONG_MODE = "object-wrong-mode"
OBJECT_WRONG_LINK_COUNT = "object-wrong-link-count"
OBJECT_UNEXPECTED_CONTENT = "object-unexpected-content"
OBJECT_UNREADABLE = "object-unreadable"
CREATION_REFUSED = "creation-refused"
POST_CREATION_OPEN_FAILED = "post-creation-open-failed"
OWNERSHIP_NOT_APPLIED = "post-creation-ownership-not-applied"
MODE_NOT_APPLIED = "post-creation-mode-not-applied"
VERIFICATION_UNREADABLE = "post-creation-verification-unreadable"
VERIFICATION_FAILED = "post-creation-verification-failed"
BARRIER_FAILED = "durability-barrier-failed"
DESCRIPTOR_NOT_RELEASED = "descriptor-not-released"
ROLLBACK_NOT_CREATED_HERE = "rollback-object-not-created-by-this-application"
ROLLBACK_IDENTITY_MISMATCH = "rollback-identity-mismatch"
ROLLBACK_IDENTITY_UNKNOWN = "rollback-identity-never-established"
ROLLBACK_NOT_EMPTY = "rollback-object-not-empty"
ROLLBACK_NOT_REMOVED_NOT_RELEASED = (
    "rollback-descriptor-not-released-nothing-removed"
)
ROLLBACK_REMOVED_NOT_RELEASED = (
    "rollback-descriptor-not-released-object-removed"
)

#: Every value a `ProvisioningRefused.classification` may take. Closed, so an
#: operator-facing refusal cannot acquire a new meaning by being raised.
PROVISIONER_REFUSALS: frozenset[str] = frozenset(
    {
        PROVISIONER_NOT_ARMED,
        PROVISIONING_IDENTITY_REFUSED,
        ITEM_NOT_RELEASED,
        ITEM_NOT_A_DIRECTORY,
        IDENTITY_UNKNOWN,
        PARENT_ABSENT,
        PARENT_NOT_A_DIRECTORY,
        PARENT_UNSAFE_OWNERSHIP,
        PARENT_REPLACED,
        OBJECT_WRONG_TYPE,
        OBJECT_WRONG_OWNER,
        OBJECT_WRONG_GROUP,
        OBJECT_WRONG_MODE,
        OBJECT_WRONG_LINK_COUNT,
        OBJECT_UNEXPECTED_CONTENT,
        OBJECT_UNREADABLE,
        CREATION_REFUSED,
        POST_CREATION_OPEN_FAILED,
        OWNERSHIP_NOT_APPLIED,
        MODE_NOT_APPLIED,
        VERIFICATION_UNREADABLE,
        VERIFICATION_FAILED,
        BARRIER_FAILED,
        DESCRIPTOR_NOT_RELEASED,
        ROLLBACK_NOT_CREATED_HERE,
        ROLLBACK_IDENTITY_MISMATCH,
        ROLLBACK_IDENTITY_UNKNOWN,
        ROLLBACK_NOT_EMPTY,
        ROLLBACK_NOT_REMOVED_NOT_RELEASED,
        ROLLBACK_REMOVED_NOT_RELEASED,
    }
)

#: **Every failure point after a successful `mkdirat`, and the refusal it
#: becomes.** Once the directory exists, an operating-system error is a fact
#: about a partly applied object rather than an exception to propagate: each one
#: below is translated here, carries the created object as
#: `ProvisioningRefused.partial`, and exposes no pathname, no directory content
#: and no operating-system message. Named as a tuple so that a failure point
#: added to `_complete_creation` without a classification is visible, and so
#: that the regressions can assert the set rather than a list of literals.
#:
#: **The seventh is descriptor finalization** — C-P5.0-LAB-V6-R3. Releasing a
#: descriptor is the last thing every one of the six above does, and it can fail
#: on its own: the created object's descriptor at the end of
#: `_complete_creation`, and the parent's two in `ensure`. It is the one member
#: that is not tied to a `mkdirat`, because `ensure` releases the same two parent
#: descriptors after verifying an already-provisioned object; there the refusal
#: carries that verification's item and `created` stays empty, which is truthful
#: for the same reason the other six are.
POST_CREATION_REFUSALS: tuple[str, ...] = (
    POST_CREATION_OPEN_FAILED,
    OWNERSHIP_NOT_APPLIED,
    MODE_NOT_APPLIED,
    VERIFICATION_UNREADABLE,
    VERIFICATION_FAILED,
    BARRIER_FAILED,
    DESCRIPTOR_NOT_RELEASED,
)

#: The six conditions r6's *"refuse an unexplained object"* rule covers, named
#: so a reader can see that all six are implemented and none is a comment.
UNEXPLAINED_OBJECT_REFUSALS: tuple[str, ...] = (
    OBJECT_WRONG_TYPE,
    OBJECT_WRONG_OWNER,
    OBJECT_WRONG_GROUP,
    OBJECT_WRONG_MODE,
    OBJECT_WRONG_LINK_COUNT,
    OBJECT_UNEXPECTED_CONTENT,
)

#: **Every classification a guarded reversal may refuse with** — C-P5.0-LAB-V6-R4.
#: Closed for the same reason `PROVISIONER_REFUSALS` is, and narrower: a reversal
#: is the operation an operator takes after a partial application, and the
#: question they are answering is *what is still on the host*. The first two are
#: not reversal-specific — an unarmed provisioner removes nothing, and a parent
#: that will not open is a reversal that cannot begin — and they are named here
#: rather than left to be discovered.
ROLLBACK_REFUSALS: tuple[str, ...] = (
    PROVISIONER_NOT_ARMED,
    PARENT_ABSENT,
    ROLLBACK_NOT_CREATED_HERE,
    ROLLBACK_IDENTITY_MISMATCH,
    ROLLBACK_IDENTITY_UNKNOWN,
    ROLLBACK_NOT_EMPTY,
    ROLLBACK_NOT_REMOVED_NOT_RELEASED,
    ROLLBACK_REMOVED_NOT_RELEASED,
)

#: **The members of `ROLLBACK_REFUSALS` that say the object is gone.** There is
#: exactly one, and it exists because `rmdir()` succeeding and the parent's
#: descriptor then failing to release are two different facts about one item: the
#: object was removed, and this application cannot state that the reversal
#: finished cleanly. `RollbackRefused` requires the classification and the
#: `removed` account to agree, so *"refused, and it is still there"* cannot be
#: constructed for an object that is not.
ROLLBACK_REMOVING_REFUSALS: frozenset[str] = frozenset(
    {ROLLBACK_REMOVED_NOT_RELEASED}
)

#: **Every finding a read-only observation may report** — C-P5.0-LAB-V6-R4.
#: `ItemObservation.discrepancies` is operator-facing in exactly the way a
#: refusal is, so its vocabulary is closed too and a finding that is not one of
#: these cannot be constructed. The last member is the one this pass adds:
#: releasing a descriptor the observation held is an operation, it can fail, and
#: a verification that raised on it would abort the re-observation of every later
#: item instead of reporting what it found.
OBSERVATION_DISCREPANCIES: tuple[str, ...] = (
    PARENT_ABSENT,
    OBJECT_WRONG_TYPE,
    OBJECT_WRONG_OWNER,
    OBJECT_WRONG_GROUP,
    OBJECT_WRONG_MODE,
    OBJECT_WRONG_LINK_COUNT,
    OBJECT_UNEXPECTED_CONTENT,
    OBJECT_UNREADABLE,
    DESCRIPTOR_NOT_RELEASED,
)


# ---------------------------------------------------------------------------
# The closed safe-detail contract
# ---------------------------------------------------------------------------
#
# **Every detail this module can put on a refusal is written here, once.** The
# classification vocabulary above says *which rule refused*; this one says
# *what an operator may be told about it*, and it exists because the two are
# different guarantees. A renderer that decided the second by looking at the
# characters a value happens to contain would pass `hunter2`, a token and an
# environment value read out of a crash — all of which are ordinary letters,
# digits and spaces — so the decision is not made on shape here. It is made on
# **exact identity with a value this module produces**.
#
# The constants below are the whole vocabulary. Two details carry finite
# modelled variation — the list of closed observation findings — and they are
# built by `unexplained_object_detail()` and `verification_failed_detail()`
# rather than interpolated at the raise site, so the varying part is a list of
# `OBSERVATION_DISCREPANCIES` members and can be nothing else.
#
# `is_reviewed_detail()` and `is_reviewed_refusal_detail()` are what an
# operator-facing renderer asks. A detail added to this module is **not**
# printable until it is added to `REVIEWED_DETAILS`, which is the point: the
# admission is an act, not a side effect of the text looking harmless.

DETAIL_BARRIER_FAILED = (
    "the containing entry's barrier did not return success, so the new "
    "entry is visible and is not durable. The object exists and is "
    "recorded; nothing after it was attempted"
)
DETAIL_CREATED_OBJECT_DESCRIPTOR_NOT_RELEASED = (
    "the directory this application created carries the ownership and the "
    "mode the item declares, and the descriptor they were applied through "
    "could not be released. The containing entry's barrier was not issued, "
    "so the entry is visible and is not durable. The object exists, its "
    "identity is recorded, and a rollback can remove exactly it"
)
DETAIL_CREATED_OBJECT_NOT_OPENED = (
    "the directory this application created could not be opened, so its "
    "identity was never established. It exists, it is recorded as residue, "
    "and no automatic removal may take it"
)
DETAIL_CREATED_OBJECT_NOT_READ_BACK = (
    "the directory this application created could not be read back, so "
    "nothing establishes that it is the object the item defines. It is "
    "left in place and recorded"
)
DETAIL_CREATION_RACED = (
    "exclusive creation found an entry already at the name between the "
    "check and the creation, so this application cannot establish that the "
    "object is its own"
)
DETAIL_DESCRIPTOR_NOT_RELEASED = (
    "a descriptor this application held on this item could not be released, "
    "so it cannot state that the item finished cleanly. What the item's "
    "outcome records about the object is unchanged and remains true, and "
    "nothing later was attempted"
)
DETAIL_IDENTITY_DOES_NOT_RESOLVE = (
    "the owner or group this item names does not resolve, so there is no "
    "ownership to apply and none to verify"
)
DETAIL_IDENTITY_IS_NOT_THE_PROCESS = (
    "this item is owned by an identity the provisioning process is not, so "
    "the ownership it declares could not be applied"
)
DETAIL_ITEM_IS_AN_OPERATOR_STEP = (
    "this item is in the release and is an operator step: this tool creates "
    "directories and nothing else"
)
DETAIL_ITEM_NOT_RELEASED = (
    "this item is not in the approved prerequisite subset and is not "
    "applied by this release"
)
DETAIL_MODE_NOT_APPLIED = (
    "the directory this application created exists and does not carry the "
    "mode the item declares. It is left in place and recorded, so a "
    "rollback can remove exactly it"
)
DETAIL_MODE_NOT_A_FILE_MODE = "the mode is not a file mode"
DETAIL_NOT_ARMED = (
    "a provisioner writes nothing until it is armed, so an instance "
    "assembled by mistake still creates no directory"
)
DETAIL_NOT_A_DIRECTORY_ITEM = "this tool applies directory items and no other kind"
DETAIL_OWNERSHIP_NOT_APPLIED = (
    "the directory this application created exists and does not carry the "
    "ownership the item declares. It is left in place and recorded, so a "
    "rollback can remove exactly it"
)
DETAIL_PARENT_ABSENT = (
    "the parent this item is created under does not exist, and creating it "
    "would be provisioning an object no item defines"
)
DETAIL_PARENT_REPLACED = (
    "the second lookup of the parent reached a different object from the "
    "one the first recorded, so the barrier would land on something this "
    "application did not verify"
)
DETAIL_PARENT_UNSAFE_OWNERSHIP = (
    "the parent is not owned exclusively by the provisioning identity, so "
    "an identity that is not its owner can rename or unlink this entry "
    "whatever mode the entry itself carries"
)
DETAIL_ROLLBACK_DESCRIPTOR_NOT_RELEASED = (
    "the descriptor this reversal identified the object through could not "
    "be released, so the removal was not issued and **nothing was "
    "removed**. The object is exactly where it was, it is still this "
    "application's to reverse, and nothing after it was attempted"
)
DETAIL_ROLLBACK_IDENTITY_MISMATCH = (
    "the name now resolves to a different object from the one this "
    "application created, so the removal would take an object nobody "
    "identified"
)
DETAIL_ROLLBACK_IDENTITY_NEVER_ESTABLISHED = (
    "this application created an object whose identity it could never "
    "establish, so nothing can show that the object now at the name is the "
    "one it made. It removes nothing at all, here or for any other item, "
    "and the residue is an operator's to account for"
)
DETAIL_ROLLBACK_NOT_CREATED_HERE = (
    "this reversal was asked for an item this application did not create, "
    "or was not given the target that says where it is"
)
DETAIL_ROLLBACK_OBJECT_NOT_A_DIRECTORY = (
    "the name this application created does not resolve to a directory it "
    "can identify, so it removes nothing"
)
DETAIL_ROLLBACK_OBJECT_NOT_EMPTY = (
    "the directory holds something this provisioning did not put there, and "
    "it is somebody's to account for before anything is removed"
)
DETAIL_ROLLBACK_REMOVED_NOT_RELEASED = (
    "this object was removed — `rmdir` returned success — and a descriptor "
    "this reversal held could not be released, so it cannot state that the "
    "reversal finished cleanly. The object is gone, it is in this "
    "refusal's account of what was removed, it is no longer in `created`, "
    "and nothing after it was attempted"
)
DETAIL_TARGET_NOT_ABSOLUTE = "a provisioning target is an absolute path"
DETAIL_TARGET_NOT_A_CREATABLE_NAME = (
    "a provisioning target names a directory to create, not a root and not "
    "a trailing-slash form"
)
DETAIL_V12_NOT_DERIVABLE = (
    "V12's location is derived from the laboratory and recovery "
    "directories, so each must be an absolute path naming a directory "
    "under a parent"
)
DETAIL_V12_PARENTS_DISAGREE = (
    "V12 is the one persistent parent of both V4 and V5, so a layout that "
    "puts the laboratory and recovery directories under different parents "
    "has no single V12 to create"
)
DETAIL_V4_AND_V5_SHARE_A_NAME = "V4 and V5 are two objects, so they cannot share one name under V12"


#: The fixed half of one detail that ends in a list of closed observation
#: findings. Written once so the builder and the admission cannot drift.
_UNEXPLAINED_OBJECT_PREFIX = (
    "an object is already at this name and is not the object this item "
    "defines. It is left exactly as it is: repairing an unexplained object "
    "is a write into a state nobody has established. All disagreements: "
)

#: The same, for the post-creation read-back that disagreed with its item.
_VERIFICATION_FAILED_PREFIX = (
    "the directory this application created does not read back as the object "
    "the item defines. It is left in place and recorded, so a rollback can "
    "remove exactly it: "
)


def unexplained_object_detail(discrepancies: Sequence[str]) -> str:
    """The refusal detail for an object already at a provisioned name.

    The varying part is the list of findings, and every member of it comes
    from `OBSERVATION_DISCREPANCIES`, so the finite variation this detail has
    is the only variation it can have.
    """
    return f"{_UNEXPLAINED_OBJECT_PREFIX}{list(discrepancies)}"


def verification_failed_detail(discrepancies: Sequence[str]) -> str:
    """The refusal detail for a created object that did not read back."""
    return f"{_VERIFICATION_FAILED_PREFIX}{list(discrepancies)}"


#: **Every fixed detail this module raises.** The empty string is a member
#: because a refusal may carry no detail at all, and a renderer asking whether
#: it may print one needs that answered rather than assumed.
REVIEWED_DETAILS: frozenset[str] = frozenset(
    {
        "",
        DETAIL_BARRIER_FAILED,
        DETAIL_CREATED_OBJECT_DESCRIPTOR_NOT_RELEASED,
        DETAIL_CREATED_OBJECT_NOT_OPENED,
        DETAIL_CREATED_OBJECT_NOT_READ_BACK,
        DETAIL_CREATION_RACED,
        DETAIL_DESCRIPTOR_NOT_RELEASED,
        DETAIL_IDENTITY_DOES_NOT_RESOLVE,
        DETAIL_IDENTITY_IS_NOT_THE_PROCESS,
        DETAIL_ITEM_IS_AN_OPERATOR_STEP,
        DETAIL_ITEM_NOT_RELEASED,
        DETAIL_MODE_NOT_APPLIED,
        DETAIL_MODE_NOT_A_FILE_MODE,
        DETAIL_NOT_ARMED,
        DETAIL_NOT_A_DIRECTORY_ITEM,
        DETAIL_OWNERSHIP_NOT_APPLIED,
        DETAIL_PARENT_ABSENT,
        DETAIL_PARENT_REPLACED,
        DETAIL_PARENT_UNSAFE_OWNERSHIP,
        DETAIL_ROLLBACK_DESCRIPTOR_NOT_RELEASED,
        DETAIL_ROLLBACK_IDENTITY_MISMATCH,
        DETAIL_ROLLBACK_IDENTITY_NEVER_ESTABLISHED,
        DETAIL_ROLLBACK_NOT_CREATED_HERE,
        DETAIL_ROLLBACK_OBJECT_NOT_A_DIRECTORY,
        DETAIL_ROLLBACK_OBJECT_NOT_EMPTY,
        DETAIL_ROLLBACK_REMOVED_NOT_RELEASED,
        DETAIL_TARGET_NOT_ABSOLUTE,
        DETAIL_TARGET_NOT_A_CREATABLE_NAME,
        DETAIL_V12_NOT_DERIVABLE,
        DETAIL_V12_PARENTS_DISAGREE,
        DETAIL_V4_AND_V5_SHARE_A_NAME,
    }
)


def _is_discrepancy_detail(text: str, prefix: str) -> bool:
    """Whether `text` is `prefix` followed by a list of closed findings.

    **The authority is the reconstruction on the last line, not the parsing
    above it.** The split only proposes which findings the text might be made
    of; the value is admitted only when rendering those findings back produces
    the identical string, so nothing is admitted that this module could not
    have produced character for character.
    """
    if not text.startswith(prefix):
        return False
    tail = text[len(prefix) :]
    if not (tail.startswith("[") and tail.endswith("]")):
        return False
    inner = tail[1:-1]
    proposed = inner.split(", ") if inner else []
    recovered = [piece[1:-1] for piece in proposed if len(piece) >= 2]
    if any(finding not in OBSERVATION_DISCREPANCIES for finding in recovered):
        return False
    return f"{prefix}{recovered}" == text


def is_reviewed_detail(text: str) -> bool:
    """Whether `text` is, in whole, a detail this module can produce.

    Membership, not resemblance. Ordinary prose that no refusal here raises is
    not a reviewed detail however harmless its characters look, which is what
    keeps a value read out of a crash, an environment or an account record
    from being admitted because it happened to be alphanumeric.
    """
    return (
        text in REVIEWED_DETAILS
        or _is_discrepancy_detail(text, _UNEXPLAINED_OBJECT_PREFIX)
        or _is_discrepancy_detail(text, _VERIFICATION_FAILED_PREFIX)
    )


def is_reviewed_refusal_detail(text: str, item_ids: Collection[str]) -> bool:
    """The same question for the composed form `apply()` records.

    `ProvisioningRun.refusal.detail` is `str(refusal)` — the classification,
    the item and the detail joined — so an operator-facing renderer meets both
    shapes. The composed one is admitted by rebuilding it: a closed
    classification, an item identifier the caller states it handed over, and a
    detail that is itself reviewed. Anything else, including a composed value
    whose detail is arbitrary, is not a reviewed detail.
    """
    if is_reviewed_detail(text):
        return True
    for classification in PROVISIONER_REFUSALS:
        for item_id in item_ids:
            head = f"{classification}: {item_id}"
            if text == head:
                return True
            joined = f"{head} — "
            if text.startswith(joined) and is_reviewed_detail(text[len(joined) :]):
                return True
    return False


class ProvisioningRefused(HarnessError):
    """One provisioning step refused, with a fixed classification and an item.

    `partial` is what makes a refusal after a successful `mkdirat` readable.
    A refusal raised before anything was created or verified carries `None`; a
    refusal raised once this item has a result carries the `AppliedItem`
    recording it, so the object travels with the refusal instead of being left
    only in the live provisioner's private state. `apply()` puts it in the
    returned `ProvisioningRun`, and a caller using `ensure()` directly has it on
    the exception.

    **The item it carries is the one that already exists, never a second copy.**
    A refusal raised while completing an object carries the `AppliedItem` that
    recorded the creation; a refusal raised when a descriptor could not be
    released carries whatever result the item had already reached — the created
    item recorded by `_record`, or the `ALREADY_PROVISIONED` one a verification
    returned. Nothing constructs an `AppliedItem` twice for one object, because
    two entries in `applied` would report one directory as two.
    """

    def __init__(
        self,
        classification: str,
        item_id: str,
        detail: str = "",
        *,
        partial: "AppliedItem | None" = None,
    ) -> None:
        if classification not in PROVISIONER_REFUSALS:
            raise HarnessError(
                f"{classification!r} is not one of the provisioning refusals. "
                "The vocabulary is closed so that an operator-facing refusal "
                "cannot acquire a new meaning by being raised."
            )
        self.classification = classification
        self.item_id = item_id
        self.detail = detail
        self.partial = partial
        message = f"{classification}: {item_id}"
        if detail:
            message = f"{message} — {detail}"
        super().__init__(message)


class RollbackRefused(ProvisioningRefused):
    """A guarded reversal refused, and **what it had already removed**.

    `rollback()` is operator-directed and removes in reverse creation order, so
    a refusal part-way through is a refusal with effects behind it. The
    classification and the item say why it stopped; `removed` is the account of
    every object `rmdir()` reported gone before it did, and it is what
    `DirectoryProvisioner.created` no longer holds. A reversal that refused
    without saying which objects it had already taken would leave an operator to
    guess, and a second attempt would be aimed at objects that are not there.

    **The one combination that would be a lie is unconstructible.**
    `ROLLBACK_REMOVED_NOT_RELEASED` says *this item's object was removed and the
    descriptor could not be released*, so the item must be in `removed`; every
    other classification says the object this refusal is about is still on the
    host, so it must not be. Neither shape can be built the other way round, and
    no object appears in `removed` twice.
    """

    def __init__(
        self,
        classification: str,
        item_id: str,
        detail: str = "",
        *,
        removed: Sequence["AppliedItem"] = (),
    ) -> None:
        if classification not in ROLLBACK_REFUSALS:
            raise HarnessError(
                f"{classification!r} is not one of the reversal refusals. The "
                "vocabulary is closed so that a reversal cannot report a "
                "condition nobody specified for it."
            )
        account = tuple(removed)
        names = [item.item_id for item in account]
        if len(names) != len(set(names)):
            raise HarnessError(
                "a reversal removes one object once, so an item cannot appear "
                "twice in the account of what it removed."
            )
        says_removed = classification in ROLLBACK_REMOVING_REFUSALS
        if says_removed != (item_id in names):
            raise HarnessError(
                "a reversal refusal and its account of what it removed must "
                "agree about the item it refused on. "
                f"{classification!r} says the object was "
                f"{'removed' if says_removed else 'not removed'}, and the "
                "account says the opposite."
            )
        super().__init__(classification, item_id, detail)
        #: Every object this reversal removed before it refused, in removal
        #: order. `DirectoryProvisioner.created` agrees with it.
        self.removed = account


# ---------------------------------------------------------------------------
# What a caller hands this module
# ---------------------------------------------------------------------------


class OwnershipLookup(Protocol):
    """The account-database seam, narrowed to the two reads this module needs.

    `execution.boundary.SystemIdentityLookup` satisfies it structurally, so the
    repository still has exactly one class that reads the host's accounts. It is
    a **required** constructor argument with no default, so importing or
    constructing a provisioner reads nothing.
    """

    def account(self, name: str) -> tuple[int, int]:
        """`(uid, primary gid)` for an account name."""

    def group_id(self, name: str) -> int:
        """The gid of a group name."""


@dataclass(frozen=True, slots=True)
class DirectoryTarget:
    """One directory item, at the exact path this application would create it.

    The owner, group and mode are **read from the reviewed item** by
    `directory_targets` and never restated here, so the thing applied and the
    thing approved are one value. `path` is separate from the item's `subject`
    for one reason: it is what lets a test drive the identical code over a
    temporary directory.
    """

    item_id: str
    path: str
    owner: str
    group: str
    mode: int
    #: The only names this release's provisioning may leave inside it. Anything
    #: else present is an object nobody here accounts for, and it refuses.
    expected_children: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.path.startswith("/"):
            raise ProvisioningRefused(
                CREATION_REFUSED,
                self.item_id,
                DETAIL_TARGET_NOT_ABSOLUTE,
            )
        if self.path.rstrip("/") != self.path or self.path == "/":
            raise ProvisioningRefused(
                CREATION_REFUSED,
                self.item_id,
                DETAIL_TARGET_NOT_A_CREATABLE_NAME,
            )
        if self.mode < 0 or self.mode > 0o7777:
            raise ProvisioningRefused(
                CREATION_REFUSED, self.item_id, DETAIL_MODE_NOT_A_FILE_MODE
            )

    @property
    def parent_path(self) -> str:
        parent = self.path.rsplit("/", 1)[0]
        return parent or "/"

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[1]


def _split(path: str) -> tuple[str, str]:
    """A layout path as `(parent, name)`, refusing anything that is not one.

    `DirectoryTarget` validates the object it is handed; this validates the two
    layout paths V12's location is *derived* from, before either is used to
    build one. A relative path, a root and a trailing-slash form each have no
    parent-and-name reading, and guessing one is how a derived parent stops
    being the object the definition names.
    """
    if not path.startswith("/") or path.rstrip("/") != path or path == "/":
        raise ProvisioningRefused(
            CREATION_REFUSED,
            "V12",
            DETAIL_V12_NOT_DERIVABLE,
        )
    parent, _, name = path.rpartition("/")
    return parent or "/", name


def directory_targets(
    *,
    layout: LaboratoryLayout = LABORATORY_LAYOUT,
) -> tuple[DirectoryTarget, ...]:
    """The four directory items, in application order, at the given locations.

    Parent before child, and every owner, group and mode taken from the reviewed
    definition. The default argument is the production value, so a caller that
    supplies nothing gets exactly the delta a maintainer approved; a test
    supplies a layout under a temporary directory and drives the same code.

    **V12 is derived from both of its children, not from one of them** —
    C-P5.0-LAB-V6-D review. Its definition is *the persistent parent of V4's
    laboratory directory and V5's independent recovery directory*, so both are
    read: the two must share one parent, and the names V12 is verified to
    contain are **their** basenames rather than the two the production layout
    happens to use. Deriving the parent from `laboratory_directory` alone would
    build a V12 that is not V5's parent and then declare children it does not
    have — which is the implicit parent V12 exists to prevent, one level down,
    and it refuses here before anything is created.
    """
    known = items_by_id()
    state_parent, laboratory_name = _split(layout.laboratory_directory)
    recovery_parent, recovery_name = _split(layout.recovery_directory)
    if recovery_parent != state_parent:
        raise ProvisioningRefused(
            CREATION_REFUSED,
            "V12",
            DETAIL_V12_PARENTS_DISAGREE,
        )
    if laboratory_name == recovery_name:
        raise ProvisioningRefused(
            CREATION_REFUSED,
            "V12",
            DETAIL_V4_AND_V5_SHARE_A_NAME,
        )
    locations = {
        "V12": (state_parent, (laboratory_name, recovery_name)),
        "V4": (
            layout.laboratory_directory,
            (layout.runs_directory_name,),
        ),
        "V9": (
            f"{layout.laboratory_directory}/{layout.runs_directory_name}",
            (),
        ),
        "V5": (layout.recovery_directory, ()),
    }
    targets: list[DirectoryTarget] = []
    for item_id in APPLIED_DIRECTORY_ITEMS:
        item = known[item_id]
        if item.kind is not ProvisioningKind.DIRECTORY:
            raise ProvisioningRefused(
                ITEM_NOT_A_DIRECTORY,
                item_id,
                DETAIL_NOT_A_DIRECTORY_ITEM,
            )
        path, children = locations[item_id]
        targets.append(
            DirectoryTarget(
                item_id=item_id,
                path=path,
                owner=item.owner,
                group=item.group,
                mode=item.mode,
                expected_children=children,
            )
        )
    return tuple(targets)


class Outcome(str, Enum):
    """What one item's application did. There is no repair and no fourth value.

    The third value is the honest one. A failure between the `mkdirat` and the
    descriptor that would identify its result leaves an object on disk that this
    application created and **cannot** identify, and that is neither `CREATED` —
    which promises a recorded `(st_dev, st_ino)` a reversal can re-observe — nor
    `ALREADY_PROVISIONED`, which says somebody else's object was verified. It is
    residue, it is reported as residue, and `rollback()` refuses it.
    """

    CREATED = "created"
    CREATED_IDENTITY_UNKNOWN = "created-identity-unknown"
    ALREADY_PROVISIONED = "already-provisioned"


#: The outcomes that mean *this application put the object there*, whether or
#: not it could identify it afterwards. `Outcome.CREATED` alone is the removable
#: subset; this is the residue an operator has to account for.
CREATING_OUTCOMES: frozenset[Outcome] = frozenset(
    {Outcome.CREATED, Outcome.CREATED_IDENTITY_UNKNOWN}
)


class RemovalEffect(str, Enum):
    """What one guarded removal did to the object — C-P5.0-LAB-V6-R4.

    **Both members mean the object is gone.** There is no member for a removal
    that did not happen, because `_remove` refuses in that case and a refusal is
    not an effect: an identity mismatch, a directory that is not empty, a
    `rmdir` that did not return success and a descriptor that would not release
    *before* the `rmdir` all leave the object exactly where it was.

    The second member is the one this pass adds. `rmdir()` reported success and
    the parent descriptor the reversal held then failed to release, which is two
    facts and not one: the object **is** removed, and this application cannot
    state that the reversal finished cleanly. Collapsing them into a refusal
    that implied the object was still there would send an operator to look for
    something that is gone, and would offer it for a second removal.
    """

    REMOVED = "removed"
    REMOVED_NOT_FINALIZED = "removed-descriptor-not-released"


@dataclass(frozen=True, slots=True)
class AppliedItem:
    """One item's result, and the identity a rollback would be guarded by.

    **The pairing of outcome and identity is an invariant, not a convention.**
    A `CREATED` item without an identity would be a removal guard that compares
    nothing, and an `ALREADY_PROVISIONED` or `CREATED_IDENTITY_UNKNOWN` item
    with one would be an invitation to remove an object this application cannot
    attribute to itself. Both are refused at construction, so neither shape can
    reach an operator or a reversal.
    """

    item_id: str
    path: str
    outcome: Outcome
    #: `(st_dev, st_ino)` as read from the descriptor this application held.
    #: Empty for an item that was already provisioned — this application did not
    #: create that object and may not remove it — and empty for one it created
    #: and could not re-observe, which is the residual case and refuses removal
    #: for the opposite reason: there is no identity to compare.
    object_id: str = ""

    def __post_init__(self) -> None:
        if self.outcome is Outcome.CREATED:
            parts = self.object_id.split(":")
            if len(parts) != 2 or not all(part.isdigit() for part in parts):
                raise HarnessError(
                    "a created item records the `(st_dev, st_ino)` its removal "
                    "would be guarded by. Without one there is nothing to "
                    "re-observe, and the outcome is "
                    "`CREATED_IDENTITY_UNKNOWN` rather than `CREATED`."
                )
        elif self.object_id:
            raise HarnessError(
                "only an item this application created and identified carries "
                "an identity. An already-provisioned object is somebody else's, "
                "and an unidentified residue has none by definition."
            )

    @property
    def removable(self) -> bool:
        """Whether a guarded reversal could remove it."""
        return self.outcome is Outcome.CREATED


@dataclass(frozen=True, slots=True)
class ItemRefusal:
    """The one refusal that stopped a run, as data rather than as a traceback."""

    item_id: str
    classification: str
    detail: str


@dataclass(frozen=True, slots=True)
class ProvisioningRun:
    """What an application did, what it refused, and what it never reached.

    `apply()` returns one of these rather than raising, because a partial
    application is exactly the state an operator has to be able to read: which
    objects now exist, which one refused and why, and which were never
    attempted. `raise_if_refused()` is there for a caller that wants the
    exception instead.

    **`applied` is the complete account of what is on disk, including the item
    that refused.** An item whose creation succeeded and whose ownership, mode,
    read-back or barrier then failed is in it, because the object is there; it
    is the refusal that says the object is not finished. A result that named
    only the items completed before the failure would tell an operator that
    nothing was created while a root-owned directory sat at the target, which is
    Codex finding PR-20260916-LAB-V6R1-1.
    """

    applied: tuple[AppliedItem, ...]
    refusal: ItemRefusal | None
    not_attempted: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return self.refusal is None and not self.not_attempted

    @property
    def created(self) -> tuple[AppliedItem, ...]:
        """Everything **this** application put on disk, identified or not.

        This is the residue question — *what is there because of this run* — and
        it is deliberately wider than the removal question. `removable` is the
        subset a guarded reversal may take.
        """
        return tuple(
            item for item in self.applied if item.outcome in CREATING_OUTCOMES
        )

    @property
    def removable(self) -> tuple[AppliedItem, ...]:
        """The created objects whose identity a reversal can re-observe."""
        return tuple(item for item in self.applied if item.removable)

    @property
    def unidentified(self) -> tuple[AppliedItem, ...]:
        """Created objects with no recorded identity — residue, not recoverable.

        Non-empty means a directory this application created is at a provisioned
        name and **no automatic reversal may remove it**: nothing establishes
        that the object now at the name is the one the `mkdirat` made. It is an
        operator's object to inspect and remove by hand.
        """
        return tuple(
            item
            for item in self.applied
            if item.outcome is Outcome.CREATED_IDENTITY_UNKNOWN
        )

    @property
    def recoverable(self) -> bool:
        """Whether guarded rollback can reverse everything this run created."""
        return not self.unidentified

    def raise_if_refused(self) -> None:
        refusal = self.refusal
        if refusal is not None:
            raise ProvisioningRefused(
                refusal.classification, refusal.item_id, refusal.detail
            )


@dataclass(frozen=True, slots=True)
class ItemObservation:
    """One item, as the read-only verification found it. **No writes.**"""

    item_id: str
    path: str
    present: bool
    #: Every way the object disagrees with its reviewed definition, by
    #: classification. Empty means it matches.
    discrepancies: tuple[str, ...]
    #: Whether the **entry** is reachable only by the provisioning identity —
    #: the parent's own ownership and write bits, which decide who may rename or
    #: unlink it whatever its own mode says.
    parent_is_exclusive: bool
    observed_owner: int = -1
    observed_group: int = -1
    observed_mode: int = -1
    observed_link_count: int = -1

    def __post_init__(self) -> None:
        for finding in self.discrepancies:
            if finding not in OBSERVATION_DISCREPANCIES:
                raise HarnessError(
                    f"{finding!r} is not one of the observation discrepancies. "
                    "The vocabulary is closed so that a read-only finding "
                    "handed to an operator cannot acquire a new meaning."
                )

    @property
    def matches(self) -> bool:
        return self.present and not self.discrepancies

    def with_discrepancy(self, finding: str) -> "ItemObservation":
        """The same observation with one more finding, and none of its own lost.

        **Additive and idempotent, for one reason each.** A release that did not
        report success is a fact about this observation's own descriptor, and it
        must not displace what the observation established about the operator's
        object — so it is appended rather than substituted, and it is appended
        last, which is what lets `_existing` take the first finding as the
        primary one. And a release failure on both the object's descriptor and
        the parent's is one finding, not two: the discrepancy says this
        application cannot state that the observation finished cleanly, and
        saying it twice would suggest two objects.
        """
        if finding in self.discrepancies:
            return self
        return replace(self, discrepancies=(*self.discrepancies, finding))


_TRAVERSAL_FLAGS = os.O_PATH | os.O_NOFOLLOW | os.O_DIRECTORY
_SYNC_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
#: The write bits that would let an identity other than the object's owner
#: rename or unlink an entry in a directory.
_FOREIGN_WRITE_BITS = stat.S_IWGRP | stat.S_IWOTH


# ---------------------------------------------------------------------------
# The mechanism
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class DirectoryProvisioner:
    """Applies the directory items, verifies them, and reverses exactly its own.

    Unarmed by default. Every creation is exclusive, every existing object is
    verified rather than repaired, and every removal is guarded by the identity
    this application recorded when it created the object.
    """

    lookup: OwnershipLookup
    armed: bool = False
    _created: list[AppliedItem] = field(default_factory=list, init=False)

    # -- gates ----------------------------------------------------------------

    def _require_armed(self, item_id: str) -> None:
        if not self.armed:
            raise ProvisioningRefused(
                PROVISIONER_NOT_ARMED,
                item_id,
                DETAIL_NOT_ARMED,
            )

    def _resolve(self, target: DirectoryTarget) -> tuple[int, int]:
        """The item's owner and group **names**, through the injected lookup."""
        try:
            uid, _primary = self.lookup.account(target.owner)
            gid = self.lookup.group_id(target.group)
        except ProvisioningRefused:
            raise
        except HarnessError as refusal:
            raise ProvisioningRefused(
                IDENTITY_UNKNOWN,
                target.item_id,
                DETAIL_IDENTITY_DOES_NOT_RESOLVE,
            ) from refusal
        return uid, gid

    def _require_provisioning_identity(self, target: DirectoryTarget, uid: int) -> None:
        """The process must already **be** the owner the item declares.

        A run started as anything else would create directories it cannot chown
        and leave a half-provisioned host, so it refuses before the first
        `mkdirat` rather than after it.
        """
        if os.geteuid() != uid:
            raise ProvisioningRefused(
                PROVISIONING_IDENTITY_REFUSED,
                target.item_id,
                DETAIL_IDENTITY_IS_NOT_THE_PROCESS,
            )

    # -- the parent -----------------------------------------------------------

    def _open_parent(self, target: DirectoryTarget) -> tuple[int, int]:
        """Hold the parent twice and check that it is the identity's alone.

        Returns `(traversal_fd, synchronizable_fd)`. The second descriptor is
        obtained by resolving the same pathname a second time and **comparing**
        its `fstat` with the first's, which is r6 §1.3.2's rule for a
        provisioned root: a genuine comparison, because it is a second lookup.

        The ownership it requires is the **provisioning process's own** effective
        UID, not the uid the item's owner name resolves to. The two are the same
        thing on the target, because `_require_provisioning_identity` refuses a
        run that is not already the declared owner — but they are different
        questions, and this is the one that decides who may rename or unlink the
        entry. Asking it about the running identity is also what keeps the
        wrong-owner refusal reachable: an item whose declared owner does not
        match the object is a disagreement about the object, and it must not be
        masked by a refusal about the parent.
        """
        try:
            traversal = os.open(target.parent_path, _TRAVERSAL_FLAGS)
        except FileNotFoundError:
            raise ProvisioningRefused(
                PARENT_ABSENT,
                target.item_id,
                DETAIL_PARENT_ABSENT,
            ) from None
        except NotADirectoryError:
            raise ProvisioningRefused(
                PARENT_NOT_A_DIRECTORY, target.item_id
            ) from None
        except OSError:
            raise ProvisioningRefused(OBJECT_UNREADABLE, target.item_id) from None
        try:
            facts = os.fstat(traversal)
            if not stat.S_ISDIR(facts.st_mode):
                raise ProvisioningRefused(PARENT_NOT_A_DIRECTORY, target.item_id)
            if (
                facts.st_uid != os.geteuid()
                or facts.st_mode & _FOREIGN_WRITE_BITS
            ):
                raise ProvisioningRefused(
                    PARENT_UNSAFE_OWNERSHIP,
                    target.item_id,
                    DETAIL_PARENT_UNSAFE_OWNERSHIP,
                )
            synchronizable = os.open(target.parent_path, _SYNC_FLAGS)
        except BaseException:
            self._release(traversal)
            raise
        try:
            second = os.fstat(synchronizable)
            if (second.st_dev, second.st_ino) != (facts.st_dev, facts.st_ino):
                raise ProvisioningRefused(
                    PARENT_REPLACED,
                    target.item_id,
                    DETAIL_PARENT_REPLACED,
                )
        except BaseException:
            # Both, unconditionally, and neither able to replace the refusal
            # that is already established: `_release` reports instead of
            # raising, so a failure on the first does not skip the second and
            # a `PARENT_REPLACED` refusal is not overwritten by a `close`.
            self._release(synchronizable)
            self._release(traversal)
            raise
        return traversal, synchronizable

    # -- verification ---------------------------------------------------------

    def _discrepancies(
        self, fd: int, target: DirectoryTarget, uid: int, gid: int
    ) -> tuple[tuple[str, ...], os.stat_result]:
        """Every way the held object disagrees with its reviewed definition.

        All six of `UNEXPLAINED_OBJECT_REFUSALS`, collected rather than
        short-circuited: an operator reading a refused object wants the whole
        disagreement, not the first field that differed.
        """
        facts = os.fstat(fd)
        found: list[str] = []
        if not stat.S_ISDIR(facts.st_mode):
            return (OBJECT_WRONG_TYPE,), facts
        if facts.st_uid != uid:
            found.append(OBJECT_WRONG_OWNER)
        if facts.st_gid != gid:
            found.append(OBJECT_WRONG_GROUP)
        if facts.st_mode & 0o7777 != target.mode:
            found.append(OBJECT_WRONG_MODE)
        try:
            entries = tuple(sorted(os.listdir(fd)))
        except OSError:
            return (*found, OBJECT_UNREADABLE), facts
        if set(entries) - set(target.expected_children):
            found.append(OBJECT_UNEXPECTED_CONTENT)
        subdirectories = 0
        for entry in entries:
            if entry not in target.expected_children:
                continue
            try:
                child = os.stat(entry, dir_fd=fd, follow_symlinks=False)
            except OSError:
                found.append(OBJECT_UNREADABLE)
                continue
            if stat.S_ISDIR(child.st_mode):
                subdirectories += 1
        # A directory's link count is `.` plus its parent's entry plus one per
        # subdirectory. A count that does not agree with what the listing showed
        # is a disagreement between two kernel-reported facts, and it refuses
        # rather than being reconciled by whichever one the caller preferred.
        if facts.st_nlink != 2 + subdirectories:
            found.append(OBJECT_WRONG_LINK_COUNT)
        return tuple(found), facts

    def verify(
        self, targets: Sequence[DirectoryTarget]
    ) -> tuple[ItemObservation, ...]:
        """**The post-provision V6 re-observation, for the directory items.**

        Read-only from end to end: it opens every descriptor `O_PATH` or
        `O_RDONLY`, creates nothing, removes nothing, takes no lock and creates
        **no link**. It therefore cannot close **I3** and does not report on it.
        It returns every finding rather than raising on the first, because an
        operator verifying a provisioned host needs the whole picture. **That
        includes a descriptor of its own it could not release** — a finding
        about the observation, appended to the findings about the object, and
        never an exception that abandons every later target unobserved
        (C-P5.0-LAB-V6-R4). One `ItemObservation` is returned for every target
        given, in the order they were given.

        `provisioning.VERIFICATION_PROCEDURE` is the complete procedure this is
        one step of; the mount, sysctl, capability and account-database
        observations are the operator's and are named there.
        """
        observations: list[ItemObservation] = []
        for target in targets:
            observations.append(self._verify_one(target))
        return tuple(observations)

    def _verify_one(self, target: DirectoryTarget) -> ItemObservation:
        """One item, observed — and **returned**, including its own failures.

        **Releasing a descriptor is an operation here too — C-P5.0-LAB-V6-R4.**
        This is Codex Blocking finding **PR-20260916-LAB-V6R3-1**, and the two
        descriptors it names are the one opened on the observed object and the
        one opened on its parent. A bare `os.close` on either raised, which broke
        both of this method's callers in a different way: `verify()` is the
        read-only V6 re-observation and its contract is to return every finding,
        so a raise abandoned every **later** target unobserved; and `_existing()`
        reaches the same code inside `ensure()`, where a raw `OSError` is a
        refusal nobody classified. The object's release was also replaceable by
        the parent's, because the parent's close sat in the `finally` the
        object's raised through.

        So both are released through `_release`, which reports, and a release
        that did not report success is the closed discrepancy
        `DESCRIPTOR_NOT_RELEASED`, **appended** to whatever this observation
        already found. It is a finding about the observation, not about the
        object: the owner, group, mode, link count and content it read are
        exactly as true as they were, and they are still returned. `_existing`
        reads it as the subordinate finding it is.
        """
        uid, gid = self._resolve(target)
        try:
            parent = os.open(target.parent_path, _TRAVERSAL_FLAGS)
        except OSError:
            return ItemObservation(
                item_id=target.item_id,
                path=target.path,
                present=False,
                discrepancies=(PARENT_ABSENT,),
                parent_is_exclusive=False,
            )
        try:
            observed = self._observe_under(parent, target, uid, gid)
        except BaseException:
            # Whatever is unwinding reached here holding the parent. It is the
            # causal one, `_release` reports instead of raising, and it is
            # preserved exactly.
            self._release(parent)
            raise
        if not self._release(parent):
            return observed.with_discrepancy(DESCRIPTOR_NOT_RELEASED)
        return observed

    def _observe_under(
        self, parent: int, target: DirectoryTarget, uid: int, gid: int
    ) -> ItemObservation:
        """Everything `_verify_one` observes while holding the parent.

        Separated from it so that the parent's release is one statement on every
        path out of the observation, rather than a `finally` that the object's
        own release can raise through — which is how a close on the object could
        be replaced by a close on the parent.
        """
        parent_facts = os.fstat(parent)
        exclusive = bool(
            stat.S_ISDIR(parent_facts.st_mode)
            and parent_facts.st_uid == os.geteuid()
            and not parent_facts.st_mode & _FOREIGN_WRITE_BITS
        )
        try:
            fd = os.open(target.name, _SYNC_FLAGS, dir_fd=parent)
        except FileNotFoundError:
            return ItemObservation(
                item_id=target.item_id,
                path=target.path,
                present=False,
                discrepancies=(),
                parent_is_exclusive=exclusive,
            )
        except OSError:
            return ItemObservation(
                item_id=target.item_id,
                path=target.path,
                present=True,
                discrepancies=(OBJECT_WRONG_TYPE,),
                parent_is_exclusive=exclusive,
            )
        try:
            found, facts = self._discrepancies(fd, target, uid, gid)
        except BaseException:
            self._release(fd)
            raise
        if not self._release(fd):
            found = (*found, DESCRIPTOR_NOT_RELEASED)
        return ItemObservation(
            item_id=target.item_id,
            path=target.path,
            present=True,
            discrepancies=found,
            parent_is_exclusive=exclusive,
            observed_owner=facts.st_uid,
            observed_group=facts.st_gid,
            observed_mode=facts.st_mode & 0o7777,
            observed_link_count=facts.st_nlink,
        )

    # -- application ----------------------------------------------------------

    def ensure(self, target: DirectoryTarget) -> AppliedItem:
        """One item: verify it, or create it exactly. Never repair it.

        Raises `ProvisioningRefused` on every condition in
        `PROVISIONER_REFUSALS`. It is the single-item form; `apply()` is the
        ordered one that records a partial application.

        **The two parent descriptors are released here, and the release is a
        step that can fail.** It is handled in the two orders it can arrive in,
        and they are different questions:

        * **with a refusal already in flight**, the refusal is the causal one
          and is preserved exactly. A `close` that failed while unwinding an
          ownership, mode, read-back, barrier or parent refusal would replace a
          fact about the object with a fact about a descriptor, and an operator
          would read the wrong cause; and
        * **with the item complete**, there is no other refusal, and a
          descriptor this application could not release means it cannot state
          that the item finished cleanly. That is `DESCRIPTOR_NOT_RELEASED`,
          carrying the result the item had already reached.

        Either way both descriptors are released, whatever the first one
        reports: a failure on the synchronizable descriptor must not skip the
        traversal descriptor and leak it.
        """
        self._require_released(target.item_id)
        uid, gid = self._resolve(target)
        traversal, synchronizable = self._open_parent(target)
        try:
            existing = self._existing(target, traversal)
            if existing is not None:
                applied = existing
            else:
                self._require_armed(target.item_id)
                self._require_provisioning_identity(target, uid)
                applied = self._create(target, traversal, synchronizable, uid, gid)
        except BaseException:
            self._release(synchronizable)
            self._release(traversal)
            raise
        # Two statements rather than one `and`, so that neither release is
        # skipped by short-circuit evaluation.
        released_synchronizable = self._release(synchronizable)
        released_traversal = self._release(traversal)
        if not (released_synchronizable and released_traversal):
            raise self._unreleased(target, applied)
        return applied

    def _require_released(self, item_id: str) -> None:
        """V7, and anything else outside this release, refuses **by name**.

        `provisioning.V7_EXCLUSION` is why: §5.10's first use is an exclusive
        `linkat` on the target, that is the first real exclusive publication
        there, and **I3** is unconfirmed. An absent lifecycle record leaves
        every participant refusing, which is the fail-closed state this release
        is meant to end in.
        """
        if item_id not in RELEASED_PREREQUISITE_SUBSET:
            raise ProvisioningRefused(
                ITEM_NOT_RELEASED,
                item_id,
                DETAIL_ITEM_NOT_RELEASED,
            )
        if item_id not in APPLIED_DIRECTORY_ITEMS:
            raise ProvisioningRefused(
                ITEM_NOT_A_DIRECTORY,
                item_id,
                DETAIL_ITEM_IS_AN_OPERATOR_STEP,
            )

    def _existing(
        self, target: DirectoryTarget, traversal: int
    ) -> AppliedItem | None:
        """`ALREADY_PROVISIONED`, or a refusal, or `None` for absent.

        **The idempotence is here, and it is a verification.** An `EEXIST` a
        caller swallowed would report success for an object nobody checked, and
        `install --directory` succeeding on a pre-existing directory is exactly
        the failure r6 §1.4.2 replaced with an exclusive `mkdirat`.
        """
        try:
            os.stat(target.name, dir_fd=traversal, follow_symlinks=False)
        except FileNotFoundError:
            return None
        except OSError:
            raise ProvisioningRefused(OBJECT_UNREADABLE, target.item_id) from None
        observation = self._verify_one(target)
        # **The object's findings decide, and the observation's own do not
        # displace them** — C-P5.0-LAB-V6-R4. A descriptor the verification
        # could not release says nothing about the owner, group, mode, link
        # count or content it read; those are the disagreement an operator has
        # to act on, and the first of them is the refusal. The release failure
        # is the refusal only when it is the whole story, and then it is the
        # same `DESCRIPTOR_NOT_RELEASED` the application path raises, carrying
        # the `ALREADY_PROVISIONED` result this verification reached — once,
        # because two `AppliedItem`s would report one directory as two.
        about_the_object = tuple(
            finding
            for finding in observation.discrepancies
            if finding != DESCRIPTOR_NOT_RELEASED
        )
        if about_the_object:
            raise ProvisioningRefused(
                about_the_object[0],
                target.item_id,
                unexplained_object_detail(observation.discrepancies),
            )
        verified = AppliedItem(
            item_id=target.item_id,
            path=target.path,
            outcome=Outcome.ALREADY_PROVISIONED,
        )
        if DESCRIPTOR_NOT_RELEASED in observation.discrepancies:
            raise self._unreleased(target, verified)
        return verified

    def _create(
        self,
        target: DirectoryTarget,
        traversal: int,
        synchronizable: int,
        uid: int,
        gid: int,
    ) -> AppliedItem:
        """Create the object exclusively, then finish it or account for it.

        The `mkdirat` is the line either side of which the failure handling is a
        different question. **Before it**, a failure means nothing was created
        and `CREATION_REFUSED` is the whole story. **After it**, an object is on
        disk under a provisioned name, so no failure may escape as a raw
        `OSError` and none may leave without recording what now exists —
        `_complete_creation` is that half.
        """
        try:
            os.mkdir(target.name, 0o700, dir_fd=traversal)
        except FileExistsError:
            raise ProvisioningRefused(
                CREATION_REFUSED,
                target.item_id,
                DETAIL_CREATION_RACED,
            ) from None
        except OSError:
            raise ProvisioningRefused(CREATION_REFUSED, target.item_id) from None
        return self._complete_creation(target, traversal, synchronizable, uid, gid)

    def _complete_creation(
        self,
        target: DirectoryTarget,
        traversal: int,
        synchronizable: int,
        uid: int,
        gid: int,
    ) -> AppliedItem:
        """Everything after a successful `mkdirat`, with the object accounted for.

        Six things can fail here and each one is translated rather than raised:
        opening the created directory, `fchown`, `fchmod`, the read-back's own
        `fstat`, a read-back that disagrees, and the parent's barrier. Releasing
        the descriptor those were issued through is the seventh, and it is the
        one that can fail with one of the other six already in flight —
        `_release` reports instead of raising so that it cannot replace them.
        `POST_CREATION_REFUSALS` is the closed set, and every one of them
        carries the created object on the refusal.

        The descriptor is opened on the object the `mkdirat` just made, and every
        remaining operation is issued on it. The umask does not decide the mode,
        no pathname is resolved a second time, and V9's setgid and sticky bits
        arrive through `fchmod` — a `mkdir` mode argument is masked and cannot
        carry them predictably.

        **The open is the one failure that costs the identity.** Every later
        failure still holds the descriptor the creation opened, so
        `(st_dev, st_ino)` is read from the object itself and a guarded reversal
        remains possible. If the open fails there is no such descriptor, and
        resolving the name a second time would record an identity this
        application cannot attribute to its own `mkdirat` — exactly the
        substitution the reversal guard exists to catch. So the identity is
        reported as unknown and the residue is left for an operator.
        """
        try:
            fd = os.open(target.name, _SYNC_FLAGS, dir_fd=traversal)
        except OSError:
            raise self._residue(
                target,
                "",
                POST_CREATION_OPEN_FAILED,
                DETAIL_CREATED_OBJECT_NOT_OPENED,
            ) from None
        try:
            try:
                os.fchown(fd, uid, gid)
            except OSError:
                raise self._residue(
                    target,
                    self._identity_of(fd),
                    OWNERSHIP_NOT_APPLIED,
                    DETAIL_OWNERSHIP_NOT_APPLIED,
                ) from None
            try:
                os.fchmod(fd, target.mode)
            except OSError:
                raise self._residue(
                    target,
                    self._identity_of(fd),
                    MODE_NOT_APPLIED,
                    DETAIL_MODE_NOT_APPLIED,
                ) from None
            try:
                found, facts = self._discrepancies(fd, target, uid, gid)
            except OSError:
                raise self._residue(
                    target,
                    self._identity_of(fd),
                    VERIFICATION_UNREADABLE,
                    DETAIL_CREATED_OBJECT_NOT_READ_BACK,
                ) from None
            if found:
                raise self._residue(
                    target,
                    self._identity_of(fd),
                    VERIFICATION_FAILED,
                    verification_failed_detail(found),
                )
            object_id = f"{facts.st_dev}:{facts.st_ino}"
        except BaseException:
            # The ownership, mode or read-back refusal above is the causal one
            # and already carries the object. Releasing the descriptor may not
            # replace it, so the release reports and the refusal propagates.
            self._release(fd)
            raise
        if not self._release(fd):
            raise self._residue(
                target,
                object_id,
                DESCRIPTOR_NOT_RELEASED,
                DETAIL_CREATED_OBJECT_DESCRIPTOR_NOT_RELEASED,
            )
        try:
            os.fsync(synchronizable)
        except OSError:
            raise self._residue(
                target,
                object_id,
                BARRIER_FAILED,
                DETAIL_BARRIER_FAILED,
            ) from None
        return self._record(target, object_id)

    def _record(self, target: DirectoryTarget, object_id: str) -> AppliedItem:
        """Add one created object to this application's own account of them."""
        applied = AppliedItem(
            item_id=target.item_id,
            path=target.path,
            outcome=Outcome.CREATED if object_id else Outcome.CREATED_IDENTITY_UNKNOWN,
            object_id=object_id,
        )
        self._created.append(applied)
        return applied

    def _residue(
        self,
        target: DirectoryTarget,
        object_id: str,
        classification: str,
        detail: str,
    ) -> ProvisioningRefused:
        """Record what the failed creation left, and build the refusal for it.

        Returned rather than raised so that each caller above keeps its own
        `raise ... from None`, which is what keeps the operating system's
        message off an operator-facing refusal.
        """
        return ProvisioningRefused(
            classification,
            target.item_id,
            detail,
            partial=self._record(target, object_id),
        )

    def _unreleased(
        self, target: DirectoryTarget, applied: AppliedItem
    ) -> ProvisioningRefused:
        """The refusal for a descriptor that could not be released.

        **It records nothing.** `applied` is the result this item already
        reached — the `AppliedItem` `_record` made when the creation completed,
        or the `ALREADY_PROVISIONED` one a verification returned — and it is
        carried unchanged. Building a second one because the finalization
        observed the same object would put one directory in `applied` twice and
        make the returned run disagree with `created`.

        What the refusal says is narrow and true: the object is whatever its
        outcome already records, and this application cannot state that the
        item finished cleanly. It exposes no path, no content and no
        operating-system message, like every other member of the vocabulary.
        """
        return ProvisioningRefused(
            DESCRIPTOR_NOT_RELEASED,
            target.item_id,
            DETAIL_DESCRIPTOR_NOT_RELEASED,
            partial=applied,
        )

    @staticmethod
    def _release(fd: int) -> bool:
        """Release one descriptor, and report whether the system said it worked.

        **It reports rather than raises, and it never tries twice.** A failed
        `close()` is ambiguous: the error is usually a deferred write-back
        failure reported at the last moment rather than a refusal to release,
        and on Linux the descriptor is gone either way — but that is one
        kernel's behaviour and nothing here depends on it. So the number is
        treated as spent: it is not reused, and `close()` is not retried on it.
        A second `close()` of a descriptor the kernel has already released can
        close a descriptor something else has since been handed, which turns a
        reported failure into a real one somewhere else.

        **Nothing here disproves a leak, and nothing here claims to.** The
        caller learns one fact — that the release did not report success — and
        that is a fact about whether this application may say the step finished
        cleanly. Whether the descriptor survives is not observable from here and
        is asserted in neither direction.
        """
        try:
            os.close(fd)
        except OSError:
            return False
        return True

    @staticmethod
    def _identity_of(fd: int) -> str:
        """`(st_dev, st_ino)` from the held descriptor, or empty if unreadable.

        Empty is a real answer here and not a swallowed error: it is what makes
        the outcome `CREATED_IDENTITY_UNKNOWN` instead of a `CREATED` item whose
        removal guard would compare against nothing.
        """
        try:
            facts = os.fstat(fd)
        except OSError:
            return ""
        return f"{facts.st_dev}:{facts.st_ino}"

    def apply(self, targets: Sequence[DirectoryTarget]) -> ProvisioningRun:
        """Every item, in order, stopping at the first refusal.

        It returns rather than raising because the state after a partial
        application is what an operator has to read: what now exists, which item
        refused and why, and what was never attempted. Nothing is rolled back
        automatically — reversing a partially provisioned host is the operator's
        decision, and `rollback()` is the guarded way to take it.

        **The refusing item is in `applied` whenever it created something.** A
        failure between the `mkdirat` and the barrier leaves a directory on
        disk, and the refusal carries it as `ProvisioningRefused.partial`; it
        goes into the same collection as the items that completed, because
        `applied` answers *what is on disk* and the object is. Whether it is
        finished is what the refusal says; whether it can be reversed is what
        its outcome says.
        """
        applied: list[AppliedItem] = []
        ordered = list(targets)
        for index, target in enumerate(ordered):
            try:
                applied.append(self.ensure(target))
            except ProvisioningRefused as refusal:
                if refusal.partial is not None:
                    applied.append(refusal.partial)
                return ProvisioningRun(
                    applied=tuple(applied),
                    refusal=ItemRefusal(
                        item_id=refusal.item_id,
                        classification=refusal.classification,
                        detail=str(refusal),
                    ),
                    not_attempted=tuple(
                        later.item_id for later in ordered[index + 1 :]
                    ),
                )
        return ProvisioningRun(
            applied=tuple(applied), refusal=None, not_attempted=()
        )

    # -- reversal -------------------------------------------------------------

    @property
    def created(self) -> tuple[AppliedItem, ...]:
        """Exactly what this application created, in creation order.

        Including any object it created and could not identify. That object is
        residue rather than a rollback candidate, and `rollback()` refuses the
        whole reversal while one is present.
        """
        return tuple(self._created)

    def rollback(
        self, targets: Sequence[DirectoryTarget]
    ) -> tuple[AppliedItem, ...]:
        """Remove exactly the directories **this application** created.

        In reverse creation order, so a child is removed before its parent, and
        each removal guarded by three conditions that all refuse rather than
        proceed:

        * the item is one this application created. An item it merely verified
          is an object somebody else provisioned, and removing it would be
          deleting state this application never owned;
        * the `(st_dev, st_ino)` recorded at creation is **re-observed
          immediately before the removal**, and a mismatch refuses. This is the
          same guard `lifecycle_storage.remove_publication_temporary` takes, and
          it has the same honest limit: a substitution in the window between the
          comparison and the `rmdir` is detected by nothing, because
          `rmdir` is not bindable to a previously observed inode; and
        * the directory is empty. `rmdir` removes an empty directory and
          nothing else, so a run directory, a ledger entry or a recovery basis
          inside one stops the reversal instead of being deleted with it.

        **An unidentified residue stops the whole reversal before it starts.**
        If a creation failed before its identity could be read, there is no
        `(st_dev, st_ino)` for the first guard to re-observe, so that object is
        an operator's to inspect by hand. The refusal is raised before the first
        `rmdir` rather than when the reversal reaches that item, because a
        partial reversal that removed the identified objects and then stopped
        would leave a host in a third state nobody asked for.

        **Every refusal says what was already removed — C-P5.0-LAB-V6-R4.** A
        reversal that stops part-way has effects behind it, and they are on the
        `RollbackRefused` it raises and out of `created` by the time it is
        raised. The one case that used to be reported untruthfully is a `rmdir`
        that succeeded followed by a parent descriptor that would not release:
        the removal is real, so `ROLLBACK_REMOVED_NOT_RELEASED` carries the
        object in `removed`, `created` no longer holds it, and a second reversal
        cannot aim at it. Where the object's own descriptor is what would not
        release, the `rmdir` was never issued — `ROLLBACK_NOT_REMOVED_NOT_RELEASED`,
        the object is still there, and it is still this application's to
        reverse.
        """
        by_id = {target.item_id: target for target in targets}
        unidentified = [
            applied
            for applied in self._created
            if applied.outcome is Outcome.CREATED_IDENTITY_UNKNOWN
        ]
        if unidentified:
            raise RollbackRefused(
                ROLLBACK_IDENTITY_UNKNOWN,
                unidentified[0].item_id,
                DETAIL_ROLLBACK_IDENTITY_NEVER_ESTABLISHED,
            )
        removed: list[AppliedItem] = []
        for applied in list(reversed(self._created)):
            target = by_id.get(applied.item_id)
            if target is None or applied.outcome is not Outcome.CREATED:
                raise RollbackRefused(
                    ROLLBACK_NOT_CREATED_HERE,
                    applied.item_id,
                    DETAIL_ROLLBACK_NOT_CREATED_HERE,
                    removed=removed,
                )
            try:
                effect = self._remove(target, applied)
            except ProvisioningRefused as refusal:
                raise RollbackRefused(
                    refusal.classification,
                    refusal.item_id,
                    refusal.detail,
                    removed=removed,
                ) from None
            # **The account is updated per removal, not at the end.** The object
            # is gone; leaving it in `_created` until the loop finished meant a
            # reversal that refused on a *later* item reported objects that were
            # no longer there, and offered them for a second attempt.
            self._forget(applied)
            removed.append(applied)
            if effect is RemovalEffect.REMOVED_NOT_FINALIZED:
                raise RollbackRefused(
                    ROLLBACK_REMOVED_NOT_RELEASED,
                    applied.item_id,
                    DETAIL_ROLLBACK_REMOVED_NOT_RELEASED,
                    removed=removed,
                )
        return tuple(removed)

    def _forget(self, applied: AppliedItem) -> None:
        """Drop exactly one removed object from the live created account.

        By identity rather than by equality, and exactly one entry: two items
        with the same fields would be one object recorded twice, and removing
        both for one `rmdir` would make the account claim a removal that did not
        happen.
        """
        for index, recorded in enumerate(self._created):
            if recorded is applied:
                del self._created[index]
                return

    def _remove(
        self, target: DirectoryTarget, applied: AppliedItem
    ) -> RemovalEffect:
        """One guarded removal, and the effect it had — C-P5.0-LAB-V6-R4.

        **The two descriptors this holds are released as operations**, which is
        the second half of Codex Blocking finding **PR-20260916-LAB-V6R3-1**.
        Bare `os.close` calls made two different things go wrong here, and the
        `rmdir` is the line between them, exactly as the `mkdirat` is on the
        application path:

        * **before it**, a release failure could replace the identity-mismatch
          or not-empty refusal that was unwinding through the same `finally`,
          handing an operator a fact about a descriptor in place of the reason
          their object was not removed. The first causal refusal wins, and both
          descriptors are still released; and
        * **after it**, the object is gone. A parent release that then failed
          raised before `rollback()` updated its account, so the live
          provisioner went on saying an object existed that it had just removed
          and offered it for a second attempt. That case returns
          `REMOVED_NOT_FINALIZED` — the removal is real and is reported as
          real — and `rollback()` raises `ROLLBACK_REMOVED_NOT_RELEASED` with
          the object in its removed account and out of `created`.

        A release failure on the object's own descriptor, with nothing else in
        flight, is the case in between: **the `rmdir` is not issued**, because
        this application refuses before an effect rather than after it. Nothing
        is removed, the live account stays exactly as it was, and the refusal is
        `ROLLBACK_NOT_REMOVED_NOT_RELEASED`.
        """
        self._require_armed(target.item_id)
        try:
            parent = os.open(target.parent_path, _TRAVERSAL_FLAGS)
        except OSError:
            raise ProvisioningRefused(PARENT_ABSENT, target.item_id) from None
        try:
            try:
                fd = os.open(target.name, _SYNC_FLAGS, dir_fd=parent)
            except OSError:
                raise ProvisioningRefused(
                    ROLLBACK_IDENTITY_MISMATCH,
                    target.item_id,
                    DETAIL_ROLLBACK_OBJECT_NOT_A_DIRECTORY,
                ) from None
            try:
                if self._identity_of(fd) != applied.object_id:
                    raise ProvisioningRefused(
                        ROLLBACK_IDENTITY_MISMATCH,
                        target.item_id,
                        DETAIL_ROLLBACK_IDENTITY_MISMATCH,
                    )
                # **Defence in depth, and said so rather than claimed.** The
                # kernel enforces this too — `rmdir(2)` fails with `ENOTEMPTY`
                # and the fallback below raises the same classification — so a
                # single-point reversal that deletes this check is caught by no
                # test, and must not be, because the behaviour does not change.
                # What it buys is the refusal happening *before* the call, which
                # is the discipline every other effect in this design follows.
                if os.listdir(fd):
                    raise ProvisioningRefused(
                        ROLLBACK_NOT_EMPTY,
                        target.item_id,
                        DETAIL_ROLLBACK_OBJECT_NOT_EMPTY,
                    )
            except BaseException:
                # Subordinate to the refusal in flight, and released either way.
                self._release(fd)
                raise
            if not self._release(fd):
                raise ProvisioningRefused(
                    ROLLBACK_NOT_REMOVED_NOT_RELEASED,
                    target.item_id,
                    DETAIL_ROLLBACK_DESCRIPTOR_NOT_RELEASED,
                )
            try:
                os.rmdir(target.name, dir_fd=parent)
            except OSError:
                raise ProvisioningRefused(
                    ROLLBACK_NOT_EMPTY, target.item_id
                ) from None
        except BaseException:
            self._release(parent)
            raise
        if not self._release(parent):
            return RemovalEffect.REMOVED_NOT_FINALIZED
        return RemovalEffect.REMOVED


def released_operator_steps() -> tuple[ProvisioningItem, ...]:
    """The released items this tool does **not** apply, with their commands.

    V1, V2 and V3: a group, a membership and a `systemd-tmpfiles` fragment. Each
    item's `creation` field is the exact operator step, and each is stated here
    rather than performed, because this repository creates no account, writes
    nothing under `/etc` and creates nothing on tmpfs.
    """
    known = items_by_id()
    return tuple(
        known[item_id]
        for item_id in RELEASED_PREREQUISITE_SUBSET
        if item_id not in APPLIED_DIRECTORY_ITEMS
    )


__all__ = [
    "APPLIED_DIRECTORY_ITEMS",
    "BARRIER_FAILED",
    "CREATING_OUTCOMES",
    "CREATION_REFUSED",
    "DESCRIPTOR_NOT_RELEASED",
    "IDENTITY_UNKNOWN",
    "ITEM_NOT_A_DIRECTORY",
    "ITEM_NOT_RELEASED",
    "MODE_NOT_APPLIED",
    "OBJECT_UNEXPECTED_CONTENT",
    "OBJECT_UNREADABLE",
    "OBJECT_WRONG_GROUP",
    "OBJECT_WRONG_LINK_COUNT",
    "OBJECT_WRONG_MODE",
    "OBJECT_WRONG_OWNER",
    "OBJECT_WRONG_TYPE",
    "OBSERVATION_DISCREPANCIES",
    "OWNERSHIP_NOT_APPLIED",
    "PARENT_ABSENT",
    "PARENT_NOT_A_DIRECTORY",
    "PARENT_REPLACED",
    "PARENT_UNSAFE_OWNERSHIP",
    "POST_CREATION_OPEN_FAILED",
    "POST_CREATION_REFUSALS",
    "PROVISIONER_NOT_ARMED",
    "PROVISIONER_REFUSALS",
    "REVIEWED_DETAILS",
    "PROVISIONING_IDENTITY_REFUSED",
    "ROLLBACK_IDENTITY_MISMATCH",
    "ROLLBACK_IDENTITY_UNKNOWN",
    "ROLLBACK_NOT_CREATED_HERE",
    "ROLLBACK_NOT_EMPTY",
    "ROLLBACK_NOT_REMOVED_NOT_RELEASED",
    "ROLLBACK_REFUSALS",
    "ROLLBACK_REMOVED_NOT_RELEASED",
    "ROLLBACK_REMOVING_REFUSALS",
    "UNEXPLAINED_OBJECT_REFUSALS",
    "VERIFICATION_FAILED",
    "VERIFICATION_UNREADABLE",
    "AppliedItem",
    "DirectoryProvisioner",
    "DirectoryTarget",
    "ItemObservation",
    "ItemRefusal",
    "Outcome",
    "OwnershipLookup",
    "ProvisioningRefused",
    "ProvisioningRun",
    "RemovalEffect",
    "RollbackRefused",
    "directory_targets",
    "is_reviewed_detail",
    "is_reviewed_refusal_detail",
    "released_operator_steps",
    "unexplained_object_detail",
    "verification_failed_detail",
]
