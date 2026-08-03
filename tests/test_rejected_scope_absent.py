"""The rejected ADR 0008 scope is gone, and cannot come back quietly.

Every other test in the suite checks that something works. This file checks that
a set of things *do not exist*, which is a different and easier property to lose:
nothing fails when a rejected concept is reintroduced, so without a test the
first sign would be a reviewer noticing it by eye.

What was rejected, by the Acceptance Authority on 2026-08-02 (OD-41, controlled
baseline v1.1):

- generic `character_state_values` / `character_balances` /
  `character_transactions` storage and the repositories over it;
- the standard/protected/compensating correction services;
- the Sheet-era value bootstrap; and
- any route by which a snapshot value could reach a character game-state field.

Phase 2 keeps immutable snapshot ingestion, character identity, external Actor
mappings, deterministic reconciliation, `legacy_authority_deferred` reporting,
provenance and audit. Nothing here objects to any of that.
"""
from __future__ import annotations

import importlib
import inspect
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: Modules whose entire subject was rejected scope.
REMOVED_MODULES = (
    "application.character_state",
    "application.corrections",
)

#: Table names that must not appear in the schema, the ORM metadata or a
#: migration. A generic key/value store for character state is the specific
#: thing ADR 0008 proposed and the Acceptance Authority rejected.
REMOVED_TABLES = (
    "character_state_values",
    "character_balances",
    "character_transactions",
)

#: Repository attributes that existed only to serve the rejected storage.
REMOVED_UNIT_OF_WORK_ATTRIBUTES = (
    "character_state",
    "balances",
    "transactions",
)


@pytest.mark.parametrize("name", REMOVED_MODULES)
def test_a_rejected_module_cannot_be_imported(name: str):
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(name)


@pytest.mark.parametrize("name", REMOVED_MODULES)
def test_a_rejected_module_has_no_file_left_behind(name: str):
    assert not (ROOT / (name.replace(".", "/") + ".py")).exists()


@pytest.mark.parametrize("table", REMOVED_TABLES)
def test_no_orm_metadata_defines_a_rejected_table(table: str):
    from adapters.database.tables import metadata

    assert table not in metadata.tables


@pytest.mark.parametrize("table", REMOVED_TABLES)
def test_no_module_in_the_tree_references_a_rejected_table(table: str):
    """Including migrations: a rejected table must not be creatable at all.

    Checked against **code**, not prose. Both the migration and
    `application/snapshots.py` deliberately explain what was rejected and why,
    and a raw text search would flag exactly the documentation that makes the
    decision legible. Docstrings are stripped and comments never reach the AST;
    a table name surviving that is a name the code actually uses — including as
    the string literal a `create_table` would pass.
    """
    offenders = []
    for directory in ("application", "adapters", "domain", "migrations", "tools"):
        for path in sorted((ROOT / directory).glob("**/*.py")):
            if table in _code_of(path):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _code_of(path: Path) -> str:
    """The module's source with docstrings removed."""
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ) and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(tree)


@pytest.mark.parametrize("attribute", REMOVED_UNIT_OF_WORK_ATTRIBUTES)
def test_the_unit_of_work_exposes_no_rejected_repository(attribute: str):
    from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
    from application.repositories import UnitOfWork

    assert not hasattr(SqlAlchemyUnitOfWork, attribute)
    assert attribute not in getattr(UnitOfWork, "__annotations__", {})


def test_the_application_repository_protocols_define_no_rejected_repository():
    import application.repositories as repositories

    for banned in (
        "CharacterStateRepository",
        "BalanceRepository",
        "CharacterTransactionRepository",
    ):
        assert not hasattr(repositories, banned)


def test_no_snapshot_record_type_carries_a_transaction():
    import application.snapshots as snapshots

    for banned in ("CharacterTransaction", "TransactionKind"):
        assert not hasattr(snapshots, banned)


def test_the_import_service_has_no_correction_dependency():
    """Checked against code, not prose.

    The module deliberately *documents* that the correction path was rejected,
    so a raw text search would flag its own explanation. Docstrings and comments
    are stripped first, leaving identifiers, attributes and calls — which is
    where a reintroduced dependency would actually live.
    """
    import ast

    from application.foundry import import_service

    tree = ast.parse(inspect.getsource(import_service))
    for node in ast.walk(tree):
        # Drop docstrings; comments never reach the AST at all.
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ) and ast.get_docstring(node):
            node.body = node.body[1:]

    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    names |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    names |= {
        alias.asname or alias.name
        for n in ast.walk(tree)
        if isinstance(n, (ast.Import, ast.ImportFrom))
        for alias in n.names
    }
    names |= {
        argument.arg
        for n in ast.walk(tree)
        if isinstance(n, ast.arguments)
        for argument in [*n.args, *n.kwonlyargs, *n.posonlyargs]
    }

    # `selected_folder_ids` is deliberately not caught: it is the artifact's own
    # exported folder set, which is snapshot provenance and has nothing to do
    # with a Council selecting fields to write.
    banned = {"selected_corrections", "selections", "FieldSelection"}
    offenders = sorted(
        name for name in names if "orrection" in name or name in banned
    )

    assert offenders == [], (
        f"the import service still references {offenders}; the correction path "
        "was rejected scope"
    )


def test_no_application_module_imports_a_rejected_module():
    offenders = []
    for path in sorted(ROOT.glob("application/**/*.py")) + sorted(
        ROOT.glob("tools/**/*.py")
    ):
        body = path.read_text(encoding="utf-8")
        for name in REMOVED_MODULES:
            if name in body:
                offenders.append(f"{path.relative_to(ROOT)} → {name}")

    assert offenders == []


def test_the_profile_offers_no_field_that_a_snapshot_may_write():
    """The last route: a classification that means "writable".

    Checked at the profile rather than at a caller, because the profile is what
    a caller would consult. If nothing in it can say "this field may be written
    from a snapshot", no caller can act on such a statement.
    """
    from domain.field_profile import FieldAuthority, SnapshotMode
    from domain.foundry_profile import PROFILE

    assert {mode.name for mode in SnapshotMode} == {
        "SNAPSHOT_ONLY",
        "REPORTED",
        "IGNORED",
    }
    assert {authority.name for authority in FieldAuthority} == {
        "DATABASE",
        "LEGACY_DEFERRED",
    }
    assert not hasattr(PROFILE, "snapshot_correctable_fields")


def test_the_sheet_importer_is_the_accepted_committed_tool_and_is_dormant():
    """Ruling D-3: reverted to its committed state, dormant, owned by 5.1.

    The I-02 additions — a profile scope check, a supervisor requirement, a
    one-time gate and exit code 6 — were the Sheet-era bootstrap, which is
    rejected scope. Their absence is what this asserts; the tool's own accepted
    I-01 behaviour is covered by `test_import_cli.py`.
    """
    from tools import import_sheet_characters as importer

    for banned in (
        "SHEET_BOOTSTRAP_FIELDS",
        "assert_within_profile",
        "EXIT_BOOTSTRAP_CLOSED",
    ):
        assert not hasattr(importer, banned), (
            f"{banned} is a Sheet-era bootstrap fence and should have been "
            "reverted with ruling D-3"
        )
