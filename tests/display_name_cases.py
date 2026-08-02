"""The display-name comparison table every layer is checked against.

One table, imported by the policy unit tests, the parser, the fake repository,
the import service and the PostgreSQL repository. The point is not that each
layer is individually correct: it is that they cannot drift apart, because the
Phase 2 normalisation defect was precisely a disagreement between two layers
that each looked right on its own.

Every name here is synthetic.
"""
from __future__ import annotations

from dataclasses import dataclass

#: `Ölrún` written two ways: precomposed (NFC), and `O`/`u` followed by
#: combining diaeresis and combining acute (NFD). Identical on screen, different
#: byte for byte. Spelled with escapes so the difference survives an editor.
OLRUN_COMPOSED = "Test \u00d6lr\u00fan"
OLRUN_DECOMPOSED = "Test O\u0308lru\u0301n"


@dataclass(frozen=True, slots=True)
class NameCase:
    """One stored name, one imported name, and what the platform must decide."""

    label: str
    stored: str
    imported: str
    #: `exact`, `capitalization` or `semantic`.
    relation: str
    #: Whether the two names claim one identity, so two characters may not hold
    #: both. Always true for `exact` and `capitalization`; the interesting
    #: entries are the `semantic` ones where it is *also* true.
    claims_same_identity: bool

    @property
    def is_exact(self) -> bool:
        return self.relation == "exact"

    @property
    def is_capitalization_only(self) -> bool:
        return self.relation == "capitalization"

    @property
    def is_semantic(self) -> bool:
        return self.relation == "semantic"


CASES: tuple[NameCase, ...] = (
    # --- unchanged ------------------------------------------------------- #
    NameCase("exact ASCII", "Test Smith A", "Test Smith A", "exact", True),
    NameCase("exact sharp s", "Test Straße", "Test Straße", "exact", True),
    NameCase("exact accented", OLRUN_COMPOSED, OLRUN_COMPOSED, "exact", True),
    # --- capitalisation alone: may apply, after a collision lookup -------- #
    NameCase("upper ASCII", "Test Smith A", "TEST SMITH A", "capitalization", True),
    NameCase("lower ASCII", "Test Smith A", "test smith a", "capitalization", True),
    NameCase("upper accented", OLRUN_COMPOSED, "TEST \u00d6LR\u00daN", "capitalization", True),
    # `ẞ` (U+1E9E) is the capital of `ß`, so this is the same word in capitals
    # rather than a different spelling of it.
    NameCase("capital sharp s", "Test Straße", "Test STRAẞE", "capitalization", True),
    # The same text in a different Unicode encoding. Not a capitalisation
    # change in the ordinary sense, but identity-neutral for the same reason:
    # the letters are the same, and refusing it would refuse a name for how it
    # was typed.
    NameCase(
        "canonically equivalent",
        OLRUN_COMPOSED,
        OLRUN_DECOMPOSED,
        "capitalization",
        True,
    ),
    # --- semantic changes ------------------------------------------------- #
    # The reported defect. `casefold()` folds these together, which is why it
    # cannot be what "capitalisation only" means — but the collision key uses
    # `casefold()` deliberately, so the two names still claim one identity and
    # two characters may not hold both.
    NameCase("sharp s expansion", "Test Straße", "Test STRASSE", "semantic", True),
    NameCase("sharp s expansion, lower", "Test Straße", "test strasse", "semantic", True),
    NameCase("different name", "Test Smith A", "Test Smith B", "semantic", False),
    # Turkish dotted and dotless `i` are different letters in Unicode without a
    # locale tailoring, and the platform applies none: this is two names, not
    # one re-cased. Pinned so a future locale-aware fold cannot arrive quietly.
    NameCase("dotless i", "Test Işık", "Test IŞIK", "semantic", False),
)
