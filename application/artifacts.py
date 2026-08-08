"""Where an immutable snapshot artifact is kept, as an application-level port.

The database holds a snapshot's **identity** — checksum, provenance, counts —
and never its bytes. The bytes are every exported Actor's mechanics, and plan
§6.4 requires them to live in restricted storage with their own retention, read
separately from the permanent audit record.

The port is deliberately three methods wide. There is no `list`, no `delete` and
no `open`:

- **no `list`** because nothing in the application has a use for enumerating
  stored artifacts, and an enumeration is the first half of an exfiltration;
- **no `delete`** because retention is an operator decision taken against the
  filesystem with the host's own tools, not an application use case that a bug
  or a forged request could reach. The checksum and the audit record survive a
  deletion, which is what makes deletion safe to do outside the application;
- **no `open`** returning a handle, because a handle is a way for bytes to be
  streamed somewhere this application did not decide to stream them to.

`store` is **idempotent on content**. The same bytes stored twice occupy one
location and produce one identity, which is what makes a retry, a re-submission
under a different request key, and a crash between storing and committing all
safe to repeat.

## What a storage failure is allowed to claim

Implementation review I-1 found the previous arrangement building *every*
`ArtifactStorageError` with the sentence "Nothing was stored or served". That is
false for `durability_unconfirmed`, whose entire deliberate contract is the
opposite: publication may already have put a correct target under the checksum
name without its directory entry being acknowledged as durable, and that target
has to survive for the retry that completes the guarantee.

So the outcome is a declared property of each failure rather than a sentence
every failure inherits. `StorageOutcome` names what a failure establishes, the
raising code chooses one, and the message is derived from it.

The second review of I-1 found the remaining defect in the same shape one level
down: `UNRESOLVED` — the **default**, and therefore the sentence an
unclassified reason inherits — still asserted that "nothing already held was
changed or removed". A default may not make a positive claim about durable
state, because it is the sentence attached to paths nobody has examined. Each
value below now says only what follows structurally from every path that can
reach it:

| Outcome | Established by every path that uses it |
|---|---|
| `UNCHANGED` | the refusal happened before publication, and it neither wrote nor removed a checksum entry |
| `PRESERVED` | the same, **plus** an entry that was already under that name was refused and deliberately left exactly as it was found |
| `UNRESOLVED` | nothing about the checksum entry, beyond the store's own content-addressing |

`PRESERVED` exists because the two ways a store can decline are operationally
different and were previously indistinguishable. "There was nothing there" and
"there was something there, it was wrong, and it is still there for you to look
at" send an operator to different procedures
(`docs/operations/foundry-snapshot-submission.md` §5.6, §9).

The default is `UNRESOLVED`, the weakest of the three: forgetting to classify a
reason can never produce a false claim, only a vaguer true one.
`tests/test_artifact_store.py` walks the adapter's syntax tree and asserts every
raise names its outcome explicitly, so the default is a safety net rather than
the normal path — and the behaviour tests in the same file tie each sentence to
the filesystem state that actually exists when it is raised, because a syntax
walk proves that a choice was made and not that it was the right one.
"""
from __future__ import annotations

from enum import Enum
from typing import Protocol

from application.foundry.artifact import SnapshotArtifact


class StorageOutcome(Enum):
    """What a storage failure establishes about the store's durable contents.

    Each sentence must be true on **every** path that raises with it, not merely
    on the path someone had in mind. That is the rule the second I-1 review
    stated, and it is why the conservative default below says less than it used
    to rather than more.
    """

    #: The refusal happened before publication: no checksum entry was created,
    #: and none was changed or removed. A discarded temporary file is not an
    #: artifact and does not make this untrue.
    UNCHANGED = (
        "No artifact was published, and no artifact already held was changed or "
        "removed."
    )

    #: The same, and additionally: an entry was already present under that
    #: checksum name, it failed validation, and it was left alone rather than
    #: repaired or overwritten. This is the outcome that tells an operator there
    #: is something on the filesystem to look at.
    PRESERVED = (
        "No artifact was published. An entry was already present under that "
        "checksum and was refused; it has been left exactly as it was found, so "
        "that it can be examined."
    )

    #: Nothing about the checksum entry is established. `durability_unconfirmed`
    #: is the case this exists for — publication may have completed and its
    #: durability was not acknowledged — and it is also the default, so it may
    #: not assert anything about durable state that an unexamined path could
    #: contradict.
    UNRESOLVED = (
        "Publication under that checksum may or may not have completed, and its "
        "durability was not confirmed. Retrying the same content is safe: the "
        "store is content-addressed, so a retry resolves to the same artifact "
        "and cannot create a second one."
    )

    @property
    def sentence(self) -> str:
        return self.value


class ArtifactStorageError(RuntimeError):
    """The artifact could not be stored or read back.

    Written, not derived: the message never carries a path, a filesystem error
    string or any part of the artifact. `reason` is a fixed classification an
    operator can act on, and `outcome` is what the failure is allowed to claim
    about the bytes — see the module docstring for why that is not one sentence
    for all of them.
    """

    def __init__(
        self, reason: str, outcome: StorageOutcome = StorageOutcome.UNRESOLVED
    ) -> None:
        super().__init__(
            "The snapshot artifact store could not complete this operation "
            f"({reason}). {outcome.sentence}"
        )
        self.reason = reason
        self.outcome = outcome


class ArtifactNotStored(ArtifactStorageError):
    """No artifact is held for that checksum.

    A read that found nothing published nothing and removed nothing, so this is
    `UNCHANGED` — the one place the stronger statement is both true and useful.
    """

    def __init__(self) -> None:
        super().__init__("not_stored", StorageOutcome.UNCHANGED)


class ArtifactStore(Protocol):
    def store(self, artifact: SnapshotArtifact) -> str:
        """Persist `artifact` and return an opaque storage reference.

        Idempotent on content: storing the same bytes again returns the same
        reference and writes nothing new. The reference is what
        `foundry_snapshots.artifact_location` holds; it is never a
        caller-supplied name and never something rendered to a user.
        """
        ...

    def load(self, checksum: str) -> SnapshotArtifact:
        """Read back the artifact identified by `checksum`.

        Raises `ArtifactNotStored` when it is absent — including when it was
        retained, used and then deleted under the documented retention rule,
        which is an ordinary outcome rather than an error in the platform.

        The bytes are re-hashed on the way out, so a store whose content no
        longer matches its name cannot be served as the snapshot that checksum
        identifies.
        """
        ...

    def contains(self, checksum: str) -> bool:
        ...
