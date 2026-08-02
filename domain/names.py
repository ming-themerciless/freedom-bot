"""The one rule the platform uses to compare two character display names.

A display name is not an identity (ADR 0005) — a character's identity is its
stable id, and a Sheet row resolves to that id through its stored mapping. But
the platform still has to answer two different questions about names, and the
Phase 2 importer was answering them with two different Unicode folds:

1. *Is this the same name, only re-capitalised?* If it is, rewriting the stored
   spelling changes no identity and may be applied without a human.
2. *Is this name already claimed by somebody else?* If it is, writing it would
   leave two characters answering to one name.

Answering (1) with `str.casefold()` and (2) with SQL `lower()` is unsound,
because `casefold()` is **wider** than capitalisation: it expands `ß` to `ss`,
so `Test Straße` and `Test STRASSE` fold together under `casefold()` and apart
under `lower()`. A mapped row could therefore be exempted from the identity
refusal as "capitalisation only" *and* skip the collision lookup that would have
caught it, committing two characters under one display name.

The correction is to make the two relations deliberately asymmetric, and to make
the asymmetry point the same way in both cases — towards refusing:

| Relation | Fold | Errs |
|---|---|---|
| exact | none | — |
| capitalisation-only | `lower()` | **narrow**: fewer changes apply without a human |
| identity claim / collision | `casefold()` | **wide**: more names count as already taken |

Both folds are applied to the NFC-normalised name, so two canonically equivalent
spellings of the same text — a precomposed `é` and an `e` followed by a
combining acute — are one name rather than two. Without that, an import could
mint a second character for a name the platform already holds, which is the
same defect in a different alphabet.

The narrow relation is defined *through* the wide one (see
`differs_only_in_capitalization`), so the containment is structural: nothing can
be exempted as a capitalisation fix that the collision key would not also see.

This module holds no infrastructure and imports nothing outside the standard
library. The Sheet parser, the import service, the fake repository and the
PostgreSQL repository all compare names through it, so there is exactly one
answer to "are these the same name?" in the platform.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

#: Unicode normalisation form applied before and after either fold. NFC is the
#: composed form: it makes canonically equivalent spellings identical without
#: merging characters that are merely similar, which NFKC would do.
_NORMAL_FORM = "NFC"


def _normalize(value: str) -> str:
    return unicodedata.normalize(_NORMAL_FORM, value)


@dataclass(frozen=True, slots=True)
class DisplayName:
    """A character display name, together with the rules for comparing it.

    The raw text is preserved exactly: this value object decides whether two
    names are the same, and never rewrites what is stored or displayed.
    """

    raw: str

    @property
    def identity_key(self) -> str:
        """The canonical key under which a name is *claimed*.

        Two characters may not both hold this key: it is what a collision lookup
        compares, and what a repository must match on. It uses full case folding
        deliberately, so it is wide — `Test Straße` and `Test STRASSE` claim the
        same identity — because a false collision costs a reconciliation while a
        missed one costs a duplicated character.
        """
        return _normalize(_normalize(self.raw).casefold())

    @property
    def _capitalization_key(self) -> str:
        """The key under which two names are the same word, differently cased.

        Narrower than `identity_key` by design: `lower()` maps a letter to its
        lowercase form and does not expand it into other letters.
        """
        return _normalize(_normalize(self.raw).lower())

    def is_exactly(self, other: DisplayName) -> bool:
        """The same name, character for character. Never an identity change."""
        return self.raw == other.raw

    def claims_same_identity_as(self, other: DisplayName) -> bool:
        """Both names claim one identity, so two characters may not hold both."""
        return self.identity_key == other.identity_key

    def differs_only_in_capitalization(self, other: DisplayName) -> bool:
        """A spelling change that alters capitalisation and nothing else.

        The `claims_same_identity_as` term is not redundant. It makes the
        containment structural rather than an assumption about Unicode: nothing
        can be exempted here that the collision key would not also see, whatever
        the two folds do to some future character.
        """
        return (
            not self.is_exactly(other)
            and self.claims_same_identity_as(other)
            and self._capitalization_key == other._capitalization_key
        )

    def is_semantic_change_from(self, other: DisplayName) -> bool:
        """This name means a *different* character from `other`.

        The complement of the two identity-neutral cases: an exact match, and a
        change of capitalisation alone.
        """
        return not self.is_exactly(other) and not self.differs_only_in_capitalization(
            other
        )
