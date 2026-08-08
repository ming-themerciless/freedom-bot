"""The current submission's traceability table must cite tests that exist.

A traceability table is evidence for a review gate. One that names a renamed or
deleted test is worse than none: it reads as proof while proving nothing, and
the drift is invisible until somebody tries to follow a row.

`SUBMISSION` is the submission **currently before the reviewer**. Superseded
submissions are not checked, and deliberately so: each is the evidence record of
the commit it described, and editing one so that it cites today's test names
would falsify it. `test_the_superseded_submission_says_so` keeps the chain
legible instead — a reader landing on the older document is told where the live
one is.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "review"
SUBMISSION = REVIEW / "phase-2-remediation-3-submission.md"
SUPERSEDED = REVIEW / "phase-2-remediation-2-submission.md"

#: `module.py::test_name`, or `…::test_name` continuing the row's last module.
_CITATION = re.compile(r"(?:(test_[a-z0-9_]+\.py)|…)::(test_[a-z0-9_]+)")


def citations() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for line in SUBMISSION.read_text(encoding="utf-8").splitlines():
        current: str | None = None
        for module, test in _CITATION.findall(line):
            if module:
                current = module
            assert current, f"a citation names a test with no module: {test}"
            found.append((current, test))
    return found


def test_the_submission_cites_tests_at_all():
    assert len(citations()) > 50


@pytest.mark.parametrize(
    ("module", "test"), sorted(set(citations())), ids=lambda value: value
)
def test_every_cited_test_exists(module: str, test: str):
    path = ROOT / "tests" / module

    assert path.exists(), f"{module} does not exist"
    assert f"def {test}(" in path.read_text(encoding="utf-8"), (
        f"{module}::{test} is cited by the traceability table but does not exist"
    )


def test_the_submission_does_not_claim_the_gate():
    body = SUBMISSION.read_text(encoding="utf-8")

    assert "Phase 2 is NOT closed" in body
    assert "PENDING" in body  # the supervised rehearsal


def test_the_submission_requests_both_independent_reviews():
    """Plan §16.4 plus ruling D-5: a general pass and a separate security pass."""
    body = SUBMISSION.read_text(encoding="utf-8")

    assert "Independent Reviewer" in body
    assert "security-focused pass" in body
    assert "You recommend; you do not approve." in body


def test_the_superseded_submission_says_so():
    """So a reader landing on the older record is sent to the live one."""
    assert SUPERSEDED.exists()
    assert SUPERSEDED.name in SUBMISSION.read_text(encoding="utf-8")
