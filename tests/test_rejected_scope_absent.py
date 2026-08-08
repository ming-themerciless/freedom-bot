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

## What these guards prove, and what they do not (finding I-4)

Independent review noted that the AST-unparse table scan can be evaded by
string concatenation, and asked for each guard to say what it is worth. So:

**Source scans are hygiene, not a security boundary.** `_code_of` parses each
module, drops docstrings and folds adjacent and `+`-concatenated string
constants, which catches the accident and the careless rename. It cannot catch
`getattr`, a name assembled at runtime, a table created from a config file, or
anything reached through an import this scan does not follow. Nobody determined
to reintroduce the rejected storage would be stopped by it, and it is not here
for that. It is here so that a *reintroduction by inattention* fails a test run
rather than waiting for a reviewer's eye. Deliberately no raw-text search: both
`migrations/versions/0002_*.py` and `application/snapshots.py` explain what was
rejected and why, and a text scan would flag exactly the documentation that
makes the decision legible.

**The decisive evidence is elsewhere, and is asserted here too.**

- `test_no_orm_metadata_defines_a_rejected_table` — the ORM metadata is what
  `create_all` and Alembic autogenerate actually read.
- `test_the_migrated_schema_contains_no_rejected_table` — the inventory of a
  PostgreSQL database migrated from empty to head. A table that does not exist
  after a real migration cannot be written to by anything, whatever the source
  says.
- `test_the_public_import_graph_reaches_no_rejected_module` — what the running
  application can actually import, resolved by importing it rather than by
  reading it.
- `test_an_import_writes_no_character_game_state_field` and
  `test_a_second_import_of_a_changed_actor_still_writes_no_field` — behavioural,
  against PostgreSQL: an Actor carrying every game-state value the profile knows
  about is imported, and the character row is compared field by field before and
  after. This is the property the whole guard file exists to protect, and it is
  the only one of these tests that would fail if a write path were added by a
  route none of the scans can see.
"""
from __future__ import annotations

import ast
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


class _FoldStrings(ast.NodeTransformer):
    """Fold `"a" + "b"` into `"ab"` before the source is searched.

    Adjacent literals (`"a" "b"`) are already folded by the parser; explicit
    concatenation is not, and unparsing it leaves `'character_' + 'state_values'`
    — which does not contain the table name. That was the evasion the
    independent review named (I-4). Folding is bounded and honest: it closes the
    one obvious gap without pretending the scan is a boundary. `"".join(...)`,
    `%`-formatting, f-strings over variables and `getattr` are all still beyond
    it, which is why the decisive evidence is the migrated schema and the
    behavioural tests rather than this.
    """

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.op, ast.Add)
            and isinstance(node.left, ast.Constant)
            and isinstance(node.right, ast.Constant)
            and isinstance(node.left.value, str)
            and isinstance(node.right.value, str)
        ):
            return ast.copy_location(
                ast.Constant(value=node.left.value + node.right.value), node
            )
        return node


def _code_of(path: Path) -> str:
    """The module's source with docstrings removed and string joins folded."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ) and ast.get_docstring(node):
            node.body = node.body[1:]
    return ast.unparse(ast.fix_missing_locations(_FoldStrings().visit(tree)))


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


# -- the decisive evidence (I-4) ------------------------------------------------
#
# Everything above reads source. These read the database, the import graph and
# the behaviour, which is what the scans are a cheap early warning for.


def test_the_folding_scan_catches_a_concatenated_table_name(tmp_path: Path):
    """The evasion the review named, shown closed.

    A guard nobody has attacked is a guard nobody knows the strength of. This
    writes the evasion into a throwaway module and checks that `_code_of` now
    sees through it — and the assertion below records what it still cannot see.
    """
    module = tmp_path / "sneaky.py"
    module.write_text(
        "TABLE = 'character_' + 'state_values'\n"
        "OTHER = 'character_' 'balances'\n",
        encoding="utf-8",
    )

    code = _code_of(module)

    assert "character_state_values" in code
    assert "character_balances" in code


def test_the_folding_scan_does_not_claim_to_catch_a_runtime_name(tmp_path: Path):
    """Stated as a test so the limit is recorded rather than assumed."""
    module = tmp_path / "sneakier.py"
    module.write_text(
        "PARTS = ['character', 'state', 'values']\n"
        "TABLE = '_'.join(PARTS)\n",
        encoding="utf-8",
    )

    code = _code_of(module)

    # Not a defect: it is why this file does not rest on source scanning.
    assert "character_state_values" not in code


@pytest.mark.database
@pytest.mark.parametrize("table", REMOVED_TABLES)
def test_the_migrated_schema_contains_no_rejected_table(migrated_database, table: str):
    """The inventory of a real database migrated from empty to head.

    A table that does not exist after the deployed migrations have run cannot be
    written to by anything, whatever any module's source happens to say.
    """
    from sqlalchemy import text

    with migrated_database.begin() as connection:
        exists = connection.execute(
            text(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = :table)"
            ),
            {"table": table},
        ).scalar_one()

    assert not exists, f"{table} exists in the migrated schema"


@pytest.mark.database
def test_the_migrated_schema_is_exactly_the_retained_set(migrated_database):
    """…and nothing unexpected arrived alongside them."""
    from sqlalchemy import text

    from adapters.database.metadata import metadata
    from adapters.database import tables  # noqa: F401 - registers tables

    with migrated_database.begin() as connection:
        present = set(
            connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
                )
            ).scalars()
        )

    assert present - {"alembic_version"} == set(metadata.tables)


def test_the_public_import_graph_reaches_no_rejected_module():
    """Resolved by importing the tree, not by reading it.

    An import the source scan does not follow — an alias, a re-export, a
    conditional import — is still an import. If any module in the application,
    adapter or domain layers could reach the rejected storage, importing all of
    them would put it in `sys.modules`.
    """
    import sys

    for directory in ("application", "adapters", "domain"):
        for path in sorted((ROOT / directory).glob("**/*.py")):
            if "__pycache__" in path.parts:
                continue
            name = ".".join(path.relative_to(ROOT).with_suffix("").parts)
            name = name.removesuffix(".__init__")
            importlib.import_module(name)

    for rejected in REMOVED_MODULES:
        assert rejected not in sys.modules


# -- the behavioural proof ------------------------------------------------------


@pytest.fixture()
def imported(committed_database):
    """One real import against PostgreSQL, and the tools to repeat it."""
    from application.foundry.artifact import ingest_bytes
    from application.foundry.import_service import SnapshotImportService
    from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
    from domain.foundry import OBSERVED_DEPLOYMENT
    from domain.foundry_profile import PROFILE
    from domain.identity import DiscordUser
    from tests import foundry_fixtures as fx
    from tests.fakes import FakeAuthorization

    council = 4200000000000000001
    engine = committed_database

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    with factory() as unit:
        unit.discord_users.add(DiscordUser(discord_id=council, username="synthetic"))
        unit.commit()

    service = SnapshotImportService(
        factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=FakeAuthorization.with_council(council),
    )

    def apply(document=None, *, request_key="req-1"):
        source = ingest_bytes(fx.encode(document or fx.bundle()))
        preview = service.preview(source, request_key=request_key)
        return service.apply(source, preview, discord_user_id=council)

    return {"engine": engine, "apply": apply, "fx": fx}


def character_row(engine) -> dict:
    from sqlalchemy import text

    with engine.begin() as connection:
        return dict(
            connection.execute(text("SELECT * FROM characters")).mappings().one()
        )


@pytest.mark.database
def test_an_import_writes_no_character_game_state_field(imported):
    """The property the whole file exists to protect, asserted directly.

    The fixture Actor carries a race, a class, a subclass, a background, a
    level, ability scores, currency, skills, tools, languages, feats and a magic
    item — every kind of value the profile classifies. After a real import
    against PostgreSQL the character row holds an identity and nothing else.
    """
    imported["apply"]()

    row = character_row(imported["engine"])

    assert row["display_name"]
    # Every managed game-state column is untouched: Phase 2 has no way to set
    # one, and this is what says so without reference to any module's source.
    assert row["level"] is None
    assert row["long_name"] is None
    assert row["version"] == 0
    assert row["active"] is True
    # And nothing else is on the table to have been written into.
    assert set(row) == {
        "id",
        "display_name",
        "long_name",
        "level",
        "active",
        "version",
        "created_at",
        "updated_at",
    }


@pytest.mark.database
def test_a_second_import_of_a_changed_actor_still_writes_no_field(imported):
    """Not even when the snapshot's values have visibly changed.

    A first import establishes the character; a second presents the same Actor
    id with a different race, class, level, currency and inventory. If any
    snapshot value could reach a character field, this is where it would.
    """
    fx = imported["fx"]
    imported["apply"]()
    before = character_row(imported["engine"])

    changed = fx.bundle(
        actors=(
            fx.actor(
                fx.FIRST_ACTOR_ID,
                level=17,
                race="Changed Race",
                class_identifier="wizard",
                background="Changed Background",
                currency={"pp": 99, "gp": 999, "sp": 9, "cp": 9, "ep": 0},
                abilities={"str": 3, "dex": 3, "con": 3, "int": 3, "wis": 3, "cha": 3},
            ),
        )
    )
    imported["apply"](changed, request_key="req-2")

    after = character_row(imported["engine"])

    assert after == before, "a snapshot value reached a character game-state field"


@pytest.mark.database
def test_a_renamed_actor_does_not_update_the_display_name_either(imported):
    """The one comparable field is reported, never written (B-2 and I-4 meet)."""
    fx = imported["fx"]
    imported["apply"]()
    before = character_row(imported["engine"])

    renamed = fx.bundle(actors=(fx.actor(fx.FIRST_ACTOR_ID, name="Renamed In Foundry"),))
    outcome = imported["apply"](renamed, request_key="req-2")

    after = character_row(imported["engine"])
    assert after == before
    assert after["display_name"] != "Renamed In Foundry"
    # …and the facts the import recorded said so, in the right direction.
    assert "platform_display_name_stale" in outcome.reconciliation.issue_codes
