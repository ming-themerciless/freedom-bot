"""Phase 4 — `domain/` imports no infrastructure, and reads no environment.

This is the Phase 4 acceptance criterion *"domain imports no infrastructure
frameworks"*, enforced rather than asserted in prose.

**It is an allowlist, not a denylist, and that is the point.** A test banning
`discord`, `sqlalchemy`, `fastapi` and friends passes the day somebody imports
`httpx`, or `redis`, or the next framework nobody thought to list. Instead:
every top-level import in `domain/` must be either the standard library or
`domain` itself. Anything else fails, including a dependency that does not exist
yet.

The check reads the source with `ast` rather than importing the modules. An
import inside a function or a `TYPE_CHECKING` block is still a dependency of the
package, and importing to inspect `sys.modules` would miss exactly those.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

DOMAIN = Path(__file__).resolve().parent.parent / "domain"

#: The only non-stdlib package `domain/` may import: itself.
PERMITTED_LOCAL_PACKAGES = frozenset({"domain"})


def domain_modules() -> list[Path]:
    modules = sorted(DOMAIN.glob("*.py"))
    assert modules, "no domain modules found; the guard would pass vacuously"
    return modules


def top_level_imports(tree: ast.AST) -> set[str]:
    """Every module `tree` imports, by top-level package name.

    Relative imports are reported as `..`-prefixed names so an import that
    climbs out of `domain/` is visible rather than silently ignored.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    found.add(node.module.split(".")[0])
            elif node.level >= 2:
                # `from ..x import y` leaves the package.
                found.add("." * node.level + (node.module or ""))
    return found


@pytest.mark.parametrize("module", domain_modules(), ids=lambda p: p.name)
def test_domain_module_imports_only_stdlib_or_domain(module):
    imports = top_level_imports(ast.parse(module.read_text(encoding="utf-8")))
    permitted = sys.stdlib_module_names | PERMITTED_LOCAL_PACKAGES
    offending = sorted(name for name in imports if name not in permitted)

    assert not offending, (
        f"{module.name} imports {offending}, which is neither the standard "
        "library nor `domain`. Dependencies point inward: infrastructure, "
        "configuration and the legacy `models`/`helpers` layer may not be "
        "imported by the domain."
    )


@pytest.mark.parametrize("module", domain_modules(), ids=lambda p: p.name)
def test_domain_module_reads_no_environment(module):
    """`os` is standard library, so the allowlist alone would let it through.

    Reading configuration in the domain is the same defect as importing
    `config`: behaviour that depends on ambient state nobody passed in.
    """
    tree = ast.parse(module.read_text(encoding="utf-8"))
    offending: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in {"environ", "getenv"}:
            offending.append(node.attr)
        elif isinstance(node, ast.Name) and node.id in {"environ", "getenv"}:
            offending.append(node.id)

    assert not offending, (
        f"{module.name} reads the environment ({sorted(set(offending))}). "
        "Inject configuration through a constructor instead."
    )


def test_the_guard_covers_the_phase_4_modules():
    """A guard that silently stopped matching files would pass forever."""
    names = {module.name for module in domain_modules()}

    assert {"money.py", "resources.py", "quantities.py", "ledger.py"} <= names
