"""No message may claim the filesystem is unchanged unless it can prove it.

Implementation review I-1, twice. The first remediation corrected the messages a
reviewer had named and left the rest, which is exactly the failure mode a
one-off fix has: the phrase is cheap to write, reads as reassuring, and is
false on every path that runs after `SnapshotSubmissionService._store_and_record`
has already published bytes.

So this is a **repository-wide** check rather than a set of per-message
assertions. It fails if the prohibited phrase is reintroduced anywhere a user,
an operator or an audit reader could be shown it.

## What it looks at, and what it deliberately does not

The distinction that makes this usable is between *asserting* the claim and
*discussing* it. The remediation is unreviewable if nobody may write down what
the defect was, so:

| Where | Rule |
|---|---|
| Python string literals that are not docstrings | **banned** — these are messages |
| Python docstrings and `#` comments | allowed — these are the explanation |
| JavaScript string literals in `foundry-module/scripts/` | **banned** |
| JavaScript comments | allowed |
| `tests/` and `foundry-module/tests/` | not scanned: a test that forbids a phrase has to name it |
| Markdown under `docs/operations/` and `docs/adr/` | allowed only inside quotation marks, which is what marks a phrase as being quoted rather than asserted |
| `docs/review/`, `docs/project-management/` | not scanned: they are the review record, and quoting a finding is their job |

A docstring can still lie, and no textual rule can stop that. What this rule
does buy is that the *messages* — the things that reach a Foundry client, an
HTTP body, an operations table or a log — cannot carry the phrase at all, and
that reintroducing it in one is a failing test rather than a review finding
nobody happened to make twice.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[1]

#: The claims a failing path cannot establish. Written as patterns rather than
#: literals so that "nothing was stored", "nothing is stored", "nothing was
#: stored or served" and "no bytes were written" are all one rule.
PROHIBITED = re.compile(
    r"""
    nothing \s+ (?:was|is|has \s+ been) \s+ (?:stored|saved|persisted)
    | no \s+ bytes \s+ (?:were|was|are|have \s+ been) \s+ (?:written|stored|saved)
    | (?:the \s+)? (?:file ?system|disk) \s+ (?:is|was) \s+ unchanged
    | nothing \s+ reached \s+ the \s+ (?:file ?system|disk)
    """,
    re.IGNORECASE | re.VERBOSE,
)

#: Every directory whose *messages* are covered. The submission path is the one
#: with the defect, but the rule is the repository's, not the package's: a claim
#: like this is wrong wherever it cannot be established.
PYTHON_ROOTS = ("application", "adapters", "domain", "tools", "migrations")

#: Operator-facing prose. `docs/review/` and `docs/project-management/` are the
#: review record and are deliberately out of scope — see the module docstring.
MARKDOWN_ROOTS = ("docs/operations", "docs/adr", "docs/rules")


def python_sources() -> list[Path]:
    found: list[Path] = []
    for root in PYTHON_ROOTS:
        found.extend(sorted((REPOSITORY / root).rglob("*.py")))
    return found


def javascript_sources() -> list[Path]:
    """The module's shipped code.

    `foundry-module/tests/` is excluded for the same reason `tests/` is excluded
    on the Python side: a test that asserts the phrase is absent has to be able
    to name it. `foundry-module/tests/claims.test.mjs` applies this same rule to
    the same files from the module's own suite.
    """
    scripts = REPOSITORY / "foundry-module" / "scripts"
    return sorted(scripts.rglob("*.js")) + sorted(scripts.rglob("*.mjs"))


def markdown_sources() -> list[Path]:
    found: list[Path] = []
    for root in MARKDOWN_ROOTS:
        found.extend(sorted((REPOSITORY / root).rglob("*.md")))
    return found


def message_literals(source: str) -> list[str]:
    """Every string constant that is not a docstring.

    A docstring is the explanation of a decision; every other literal is, or can
    become, something a person is shown. `ast` is what separates them reliably —
    a regular expression over the file cannot tell a message from the paragraph
    describing why the message says what it does.
    """
    tree = ast.parse(source)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                docstrings.add(id(first.value))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def without_comments(source: str) -> str:
    """JavaScript with `//` and `/* */` removed, so prose is not scanned.

    Crude on purpose: it does not parse, so a `//` inside a string literal is
    also treated as a comment. That direction of error can only make this check
    look at *less* text, never at text it should have skipped, and every real
    message in the module is a plain sentence.
    """
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", source)


@pytest.mark.parametrize(
    "path", python_sources(), ids=lambda path: str(path.relative_to(REPOSITORY))
)
def test_no_python_message_claims_the_filesystem_is_unchanged(path: Path) -> None:
    offending = [
        literal
        for literal in message_literals(path.read_text(encoding="utf-8"))
        if PROHIBITED.search(literal)
    ]
    assert not offending, (
        f"{path.relative_to(REPOSITORY)} builds a message claiming nothing was "
        "stored. Review finding I-1: the artifact is written before the "
        "transaction commits, so a path that runs after the store cannot "
        "establish that. Say what is known instead — nothing was recorded or "
        "confirmed, and retrying with the same idempotency key is safe because "
        f"a retry cannot create a second snapshot. Offending: {offending}"
    )


@pytest.mark.parametrize(
    "path", javascript_sources(), ids=lambda path: str(path.relative_to(REPOSITORY))
)
def test_no_module_message_claims_the_filesystem_is_unchanged(path: Path) -> None:
    body = without_comments(path.read_text(encoding="utf-8"))
    assert not PROHIBITED.search(body), (
        f"{path.relative_to(REPOSITORY)} tells the submitting GM that nothing "
        "was stored. The module cannot know that: it is one network failure "
        "away from a server that stored the bytes and could not record them. "
        "Say that nothing was recorded or confirmed and that resubmitting is "
        "safe."
    )


@pytest.mark.parametrize(
    "path", markdown_sources(), ids=lambda path: str(path.relative_to(REPOSITORY))
)
def test_operator_documentation_only_quotes_the_old_claim(path: Path) -> None:
    """Explaining the defect is required; asserting it is the defect.

    A quoted occurrence — `"nothing was stored"` — is the documentation saying
    what the wording used to be and why it changed, which §5.7 and §9 of the
    operations document have to be able to do. An unquoted one is an operations
    table telling an operator that a `503` left the store untouched, which is
    the incident-model error the finding is about.
    """
    unquoted: list[str] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for match in PROHIBITED.finditer(line):
            if not _is_quoted(line, match.start(), match.end()):
                unquoted.append(f"{number}: {line.strip()}")
    assert not unquoted, (
        f"{path.relative_to(REPOSITORY)} asserts that nothing was stored "
        "outside a quotation. Quote the old wording if the point is to explain "
        f"the change; do not state it as the current contract. {unquoted}"
    )


def _is_quoted(line: str, start: int, end: int) -> bool:
    """Whether the match sits inside a pair of double quotes or backticks."""
    for opening, closing in (('"', '"'), ("“", "”"), ("`", "`")):
        before = line.rfind(opening, 0, start)
        if before == -1:
            continue
        after = line.find(closing, end)
        if after != -1:
            return True
    return False


# -- the check is worth having only if it actually catches things -------------


def test_the_rule_catches_a_reintroduction_in_a_message() -> None:
    """A guard nobody has seen fail is a guard nobody knows works."""
    source = (
        '"""Nothing was stored: explaining the old defect is allowed."""\n'
        "# and so is a comment saying nothing was stored\n"
        'raise RuntimeError("The submission failed. Nothing was stored.")\n'
    )
    literals = message_literals(source)

    assert [literal for literal in literals if PROHIBITED.search(literal)] == [
        "The submission failed. Nothing was stored."
    ]


def test_the_rule_does_not_ban_the_explanation() -> None:
    """The docstring and the comment above are both untouched by the rule."""
    source = (
        '"""Not "nothing was stored" (review finding I-1)."""\n'
        "# The old wording said nothing was stored, which it could not prove.\n"
        'MESSAGE = "No submission was recorded or confirmed."\n'
    )

    assert [
        literal for literal in message_literals(source) if PROHIBITED.search(literal)
    ] == []


@pytest.mark.parametrize(
    "line, quoted",
    [
        ('The row said "nothing was stored", which was false.', True),
        ("The table used `nothing was stored` as its wording.", True),
        ("A 503 means nothing was stored; retry the same key.", False),
    ],
)
def test_the_markdown_rule_separates_quoting_from_asserting(
    line: str, quoted: bool
) -> None:
    match = PROHIBITED.search(line)
    assert match is not None
    assert _is_quoted(line, match.start(), match.end()) is quoted
