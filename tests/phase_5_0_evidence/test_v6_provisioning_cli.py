"""**C-P5.0-LAB-V6-P-R1** — the operator entry point for the reviewed directory
provisioner, and the guards that keep it the only thing it is.

The mechanism was already reviewed and accepted; what did not exist was any
repository-owned way for an operator to reach it as approved. That gap — RAID
**LAB-V6-P1** — stopped the C-P5.0-LAB-V6-P operational pass before its first
mutation. `execution/provisioning_cli.py` closes it, and this suite is what says
the entry point adds no authority, no alternate input and no second applier to
the thing it reaches.

Four properties, and they are deliberately kept apart.

1. **The default invocation is inert.** No account database, no filesystem, no
   provisioner. It may name the four fixed item identifiers and it may not
   pretend that a run happened.
2. **One explicit flag is the only arm**, it is the flag itself rather than a
   constant, and a single-point reversal that deletes the early return is
   caught — by actually removing it from the module's syntax tree and running
   the result.
3. **The production route is the reviewed one.** `SystemIdentityLookup` over the
   host account database, `directory_targets()` called with no arguments, and
   the V12, V4, V9, V5 order handed to `apply` exactly as that factory built it.
4. **The rendering is complete and bounded.** Every applied item, its `created`
   versus `already-provisioned` outcome and its recorded object identity; the
   refusal's item, classification and detail; every item never attempted — and
   never a raw exception, an operating-system message, a traceback or an
   unbounded field.

**Nothing here touches a provisioned path and nothing here needs privilege.**
Every mutating test drives the real provisioner over `tmp_path` with an injected
account lookup that resolves the reviewed owner and group to this process's own
ids. A directory created here says nothing about whether V12, V4, V9 or V5 has
ever been applied on `oracle-test` — none has — and nothing here observes that
host, creates a link or bears on **I3**.
"""
from __future__ import annotations

import ast
import errno
import io
import os
import stat
import tokenize
from contextlib import contextmanager
from pathlib import Path

import pytest

from tools.phase_5_0_evidence.errors import HarnessError
from tools.phase_5_0_evidence.execution import provisioning_cli
from tools.phase_5_0_evidence.execution import provisioner as provisioner_module
from tools.phase_5_0_evidence.execution.provisioning_cli import (
    COMPLETED_EXIT_CODE,
    FIELD_WIDTH,
    NOT_APPLIED_EXIT_CODE,
    NO_IDENTITY,
    REFUSED_EXIT_CODE,
    UNCLASSIFIED_EXIT_CODE,
    UNRECOGNIZED_ITEM,
    WITHHELD_IDENTITY,
    WITHHELD_PATH,
    build_parser,
    main,
    render_not_applied,
    render_run,
)
from tools.phase_5_0_evidence.execution.provisioner import (
    MODE_NOT_APPLIED,
    OBSERVATION_DISCREPANCIES,
    OBJECT_WRONG_TYPE,
    PROVISIONER_NOT_ARMED,
    PROVISIONER_REFUSALS,
    PROVISIONING_IDENTITY_REFUSED,
    REVIEWED_DETAILS,
    AppliedItem,
    DirectoryProvisioner,
    ItemRefusal,
    Outcome,
    ProvisioningRefused,
    ProvisioningRun,
    directory_targets,
    is_reviewed_detail,
    unexplained_object_detail,
    verification_failed_detail,
)
from tools.phase_5_0_evidence.provisioning import (
    APPLIED_DIRECTORY_ITEMS,
    LaboratoryLayout,
    items_by_id,
)

MODULE = Path(provisioning_cli.__file__)
SOURCE = MODULE.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE, filename=str(MODULE))

#: The message the injected `os` failure carries. It is asserted **absent** from
#: every rendering: an operating-system message is exactly the kind of text an
#: operator-facing surface may not acquire by accident.
INJECTED_MESSAGE = "injected failure, for the operator surface only"


class FakeAccounts:
    """The account-database seam, as the two reads the provisioner performs.

    It resolves the reviewed owner and group to **this process's own** ids, so
    the real `fchown` succeeds without privilege and the real mechanism runs
    unchanged. `uid_shift` moves the answer away from the truth, which is how
    the *this process is not the identity the item declares* refusal is reached
    without a second real account.
    """

    #: Every construction this suite sees, so *the entry point constructs one*
    #: is asserted rather than assumed.
    constructions: list["FakeAccounts"] = []

    def __init__(self, *, uid_shift: int = 0, unknown: str = "") -> None:
        self.uid_shift = uid_shift
        self.unknown = unknown
        FakeAccounts.constructions.append(self)

    def account(self, name: str) -> tuple[int, int]:
        if name == self.unknown:
            raise HarnessError(f"no account named {name!r} exists")
        return os.geteuid() + self.uid_shift, os.getegid()

    def group_id(self, name: str) -> int:
        if name == self.unknown:
            raise HarnessError(f"no group named {name!r} exists")
        return os.getegid()


def model_targets(root: Path):
    """The four reviewed items, at model locations under `root`.

    It calls the production factory with a model layout, so the owner, group,
    mode and order under test are the reviewed ones and only the locations
    differ.
    """
    return directory_targets(
        layout=LaboratoryLayout(
            laboratory_directory=str(root / "var" / "freedom-blades" / "laboratory"),
            runs_directory_name="runs",
            record_name="lifecycle.json",
            recovery_directory=str(root / "var" / "freedom-blades" / "recovery"),
            lock_path=str(root / "run" / "laboratory.lock"),
        ),
    )


@pytest.fixture(autouse=True)
def _forget_previous_lookups():
    """Every test starts with an empty account of the lookups constructed, so
    *the entry point constructed exactly one* is a fact about this test."""
    FakeAccounts.constructions.clear()
    yield
    FakeAccounts.constructions.clear()


@pytest.fixture()
def model(tmp_path: Path) -> Path:
    """A model host: the one parent exists, and nothing below it does."""
    (tmp_path / "var").mkdir(mode=0o700)
    return tmp_path


@pytest.fixture()
def over_the_model(monkeypatch, model: Path):
    """Point the entry point's production route at the model host.

    Two replacements and no third: the layout the reviewed factory is called
    with, and the account database. The provisioner, its arming, its ordering
    and every byte it writes are the real ones.
    """
    targets = model_targets(model)
    monkeypatch.setattr(provisioning_cli, "directory_targets", lambda: targets)
    monkeypatch.setattr(provisioning_cli, "SystemIdentityLookup", FakeAccounts)
    return targets


def _with_dir_fd(*args, **kwargs) -> bool:
    """The post-creation `open` is the only one this mechanism issues with a
    `dir_fd`, which is how an injection reaches it without breaking the parent
    lookups that happen first."""
    return kwargs.get("dir_fd") is not None


@contextmanager
def failing(name: str, *, after: int = 0, when=None):
    """Replace one `os` call with one that fails, for the length of a block.

    `after` lets the failure land on a later item, which is how the *residue
    from an unfinished item* case is reached. The replacement is undone in a
    `finally`, so no test leaves a broken `os` behind for the next one.
    """
    real = getattr(os, name)
    seen = 0

    def injected(*args, **kwargs):
        nonlocal seen
        if when is None or when(*args, **kwargs):
            seen += 1
            if seen > after:
                raise OSError(errno.EIO, INJECTED_MESSAGE)
        return real(*args, **kwargs)

    setattr(os, name, injected)
    try:
        yield
    finally:
        setattr(os, name, real)


def _code_only(source: str) -> str:
    """`source` with every comment and every string literal removed.

    A module that documents at length what it must never do will contain those
    names as prose. Stripping comments and literals is what lets the guards read
    the code while the documentation says what it needs to.
    """
    pieces: list[str] = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in (tokenize.COMMENT, tokenize.STRING):
            continue
        pieces.append(token.string)
    return " ".join(pieces)


def _main_function() -> ast.FunctionDef:
    for node in TREE.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return node
    raise AssertionError("the entry point defines no `main`")


def _calls_named(name: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(TREE)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    ]


# ---------------------------------------------------------------------------
# 1. The default invocation reads nothing and applies nothing
# ---------------------------------------------------------------------------


class Exploding:
    """A double that fails the test if the inert path reaches it at all."""

    def __init__(self, what: str) -> None:
        self.what = what

    def __call__(self, *args, **kwargs):
        raise AssertionError(
            f"the invocation without the application flag reached {self.what}."
        )


def test_without_the_flag_nothing_is_constructed_read_or_written(
    monkeypatch, model: Path, capsys
) -> None:
    """The whole of property 1, behaviourally.

    The three things the production route uses are replaced with doubles that
    raise on contact, so *it did not read the account database* is a fact about
    the run rather than an inference from the source.
    """
    monkeypatch.setattr(
        provisioning_cli, "directory_targets", Exploding("directory_targets")
    )
    monkeypatch.setattr(
        provisioning_cli, "SystemIdentityLookup", Exploding("SystemIdentityLookup")
    )
    monkeypatch.setattr(
        provisioning_cli, "DirectoryProvisioner", Exploding("DirectoryProvisioner")
    )
    before = sorted(model.rglob("*"))

    assert main([]) == NOT_APPLIED_EXIT_CODE

    assert sorted(model.rglob("*")) == before
    assert FakeAccounts.constructions == []
    printed = capsys.readouterr()
    assert printed.err == ""
    assert printed.out.startswith("NOT APPLIED —")
    # It may name the fixed identifiers, and it may not claim an outcome for one.
    for item_id in APPLIED_DIRECTORY_ITEMS:
        assert item_id in printed.out
    for claim in (
        "items applied",
        "created by this run",
        "unidentified residue",
        "not attempted",
        Outcome.CREATED.value,
        Outcome.ALREADY_PROVISIONED.value,
        "refusal",
    ):
        assert claim not in printed.out


def test_the_inert_rendering_claims_no_run() -> None:
    """The one thing this output must never be mistaken for."""
    rendered = render_not_applied()

    assert "no account database and no filesystem was read" in rendered
    assert "applied              : none. No object was made" in rendered
    # Not one word that could be read as the outcome of an item.
    for claim in (Outcome.CREATED.value, Outcome.ALREADY_PROVISIONED.value):
        assert claim not in rendered
    assert "--apply" in rendered
    for item_id in APPLIED_DIRECTORY_ITEMS:
        assert item_id in rendered


def test_nothing_is_constructed_when_the_module_is_imported() -> None:
    """Import is a declaration, not a run.

    Read from the syntax tree rather than from an import that has already
    happened: a module-level construction would arm nothing today and would be
    the first line of the next accident.
    """
    acting = {
        "DirectoryProvisioner",
        "SystemIdentityLookup",
        "directory_targets",
        "main",
    }
    for statement in TREE.body:
        if isinstance(statement, (ast.FunctionDef, ast.ClassDef, ast.If)):
            # A function body runs when it is called, and the `__main__` block
            # runs only as a program. Neither is module level.
            continue
        for node in ast.walk(statement):
            assert not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in acting
            ), "the entry point constructs or runs something at module level."


# ---------------------------------------------------------------------------
# 2. The flag is the arm, and it is the only one
# ---------------------------------------------------------------------------


def test_the_application_flag_is_the_only_option_and_is_off_by_default() -> None:
    parser = build_parser()
    options = {
        option for action in parser._actions for option in action.option_strings
    }

    assert options == {"--apply", "-h", "--help"}
    assert parser.parse_args([]).apply is False
    assert parser.parse_args(["--apply"]).apply is True


def test_the_arm_is_the_flag_itself_and_never_a_constant() -> None:
    """**The single-point-reversal guard, first half.**

    `armed=` is written as the parsed flag. Written as `True` it would be a
    module whose early return is the *only* thing between an operator and a
    provisioned host; written as the flag, deleting that return still leaves an
    unarmed provisioner — which is the control the second half runs.
    """
    constructions = _calls_named("DirectoryProvisioner")
    assert len(constructions) == 1, "the entry point builds exactly one provisioner."
    keywords = {keyword.arg: keyword.value for keyword in constructions[0].keywords}

    assert set(keywords) == {"lookup", "armed"}
    armed = keywords["armed"]
    assert isinstance(armed, ast.Attribute) and armed.attr == "apply", (
        "the arm must be the parsed command-line flag, not a constant."
    )
    assert not isinstance(armed, ast.Constant)


def test_the_production_route_is_unreachable_before_the_flag_is_checked() -> None:
    """The early return comes first, and everything that acts comes after it."""
    main_fn = _main_function()
    guard = next(node for node in main_fn.body if isinstance(node, ast.If))
    assert any(isinstance(node, ast.Return) for node in ast.walk(guard)), (
        "the flag check must return rather than fall through."
    )
    for name in ("DirectoryProvisioner", "SystemIdentityLookup", "directory_targets"):
        for call in _calls_named(name):
            assert call.lineno > guard.lineno, (
                f"{name} is reached before the application flag is checked."
            )


def _module_with_the_arm_removed():
    """The entry point, recompiled with its flag check deleted.

    **This is the negative control the handover asks for.** A reversal that
    removes or bypasses the explicit arm is a single edit, and a suite that only
    asserted the edit is absent would pass on the day somebody made it and then
    relied on a second guard nobody had tested. So the edit is made here, to the
    syntax tree, and the result is run.
    """
    tree = ast.parse(SOURCE, filename=str(MODULE))
    main_fn = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    guard = next(node for node in main_fn.body if isinstance(node, ast.If))
    main_fn.body = [node for node in main_fn.body if node is not guard]
    ast.fix_missing_locations(tree)
    namespace: dict = {
        "__name__": "provisioning_cli_with_the_arm_removed",
        "__package__": "tools.phase_5_0_evidence.execution",
    }
    exec(compile(tree, "<the arm removed>", "exec"), namespace)  # noqa: S102
    return namespace


def test_removing_the_flag_check_still_creates_nothing(
    monkeypatch, model: Path, capsys
) -> None:
    """**The single-point-reversal guard, second half.**

    With the early return gone, a default invocation reaches the construction —
    and the provisioner it builds is unarmed, because the arm is the flag. It
    refuses `provisioner-not-armed` on the first item, attempts none of the
    others, creates nothing and exits non-zero.
    """
    mutated = _module_with_the_arm_removed()
    targets = model_targets(model)
    mutated["directory_targets"] = lambda: targets
    mutated["SystemIdentityLookup"] = FakeAccounts

    status = mutated["main"]([])

    assert status == REFUSED_EXIT_CODE
    printed = capsys.readouterr()
    assert PROVISIONER_NOT_ARMED in printed.out
    assert [target.item_id for target in targets[1:]] == ["V4", "V9", "V5"]
    for target in targets:
        assert not Path(target.path).exists(), target.item_id


# ---------------------------------------------------------------------------
# 3. The production route is the reviewed one
# ---------------------------------------------------------------------------


def test_the_reviewed_factory_is_called_with_no_alternate_layout() -> None:
    """`directory_targets()` takes a layout, and this module never supplies one.

    That is what makes the applied paths, owners, groups, modes and order the
    production values a maintainer approved rather than something an operator
    could point elsewhere.
    """
    calls = _calls_named("directory_targets")
    assert len(calls) == 1
    assert calls[0].args == [] and calls[0].keywords == []

    lookups = _calls_named("SystemIdentityLookup")
    assert len(lookups) == 1
    assert lookups[0].args == [] and lookups[0].keywords == []


def test_the_production_route_applies_exactly_what_the_factory_built(
    monkeypatch, capsys
) -> None:
    """The reviewed values, in the reviewed order, handed over unaltered.

    The provisioner is replaced with a recorder, so the production
    `directory_targets()` default is the thing under test and **no object is
    created anywhere**: the reviewed production paths are compared, not touched.
    """
    handed: list = []
    built: list[dict] = []

    class Recording:
        def __init__(self, **kwargs) -> None:
            built.append(kwargs)

        def apply(self, targets):
            handed.extend(targets)
            return ProvisioningRun(applied=(), refusal=None, not_attempted=())

    monkeypatch.setattr(provisioning_cli, "SystemIdentityLookup", FakeAccounts)
    monkeypatch.setattr(provisioning_cli, "DirectoryProvisioner", Recording)

    status = main(["--apply"])
    capsys.readouterr()

    assert status == REFUSED_EXIT_CODE  # nothing was applied, so not complete
    assert len(FakeAccounts.constructions) == 1
    assert built == [{"lookup": FakeAccounts.constructions[0], "armed": True}]
    assert tuple(handed) == directory_targets()
    assert [target.item_id for target in handed] == ["V12", "V4", "V9", "V5"]
    known = items_by_id()
    for target in handed:
        item = known[target.item_id]
        assert (target.owner, target.group, target.mode) == (
            item.owner,
            item.group,
            item.mode,
        )


# ---------------------------------------------------------------------------
# 4. A successful application, and the two outcomes it distinguishes
# ---------------------------------------------------------------------------


def test_a_successful_application_renders_every_item_and_exits_zero(
    over_the_model, capsys
) -> None:
    targets = over_the_model

    assert main(["--apply"]) == COMPLETED_EXIT_CODE

    printed = capsys.readouterr()
    assert printed.err == ""
    assert printed.out.startswith("APPLIED —")
    known = items_by_id()
    for target in targets:
        observed = os.stat(target.path, follow_symlinks=False)
        assert stat.S_ISDIR(observed.st_mode), target.item_id
        assert observed.st_mode & 0o7777 == known[target.item_id].mode, target.item_id
        # The item, its outcome and the identity a reversal would be guarded by.
        assert target.item_id in printed.out
        assert target.path in printed.out
        assert f"{observed.st_dev}:{observed.st_ino}" in printed.out
    assert printed.out.count(Outcome.CREATED.value) >= len(targets)
    assert "refusal              : none" in printed.out
    assert "not attempted        : none" in printed.out
    assert "created by this run  : V12, V4, V9, V5" in printed.out
    assert "unidentified residue : none" in printed.out
    # Rendering is not reversing.
    assert "No rollback is performed by this program" in printed.out


def test_an_already_compliant_host_is_not_reported_as_a_creation(
    over_the_model, capsys
) -> None:
    """The second run writes nothing, and says so in a different word.

    An operator who cannot tell *this run created it* from *it was already
    there* cannot tell a first application from a repeat, and the object
    identity is the fact that settles it: an already-provisioned object is
    somebody else's and carries none.
    """
    targets = over_the_model
    assert main(["--apply"]) == COMPLETED_EXIT_CODE
    first = capsys.readouterr().out
    before = {target.path: os.stat(target.path).st_ino for target in targets}

    assert main(["--apply"]) == COMPLETED_EXIT_CODE

    second = capsys.readouterr().out
    assert {target.path: os.stat(target.path).st_ino for target in targets} == before
    assert Outcome.CREATED.value in first
    assert second.count(Outcome.ALREADY_PROVISIONED.value) == len(targets)
    assert second.count(NO_IDENTITY) == len(targets)
    assert "created by this run  : none" in second


# ---------------------------------------------------------------------------
# 5. Refusals — complete, classified and bounded
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("classification", sorted(PROVISIONER_REFUSALS))
def test_every_reviewed_refusal_renders_safely_and_completely(
    classification: str,
) -> None:
    """One rendering per closed classification, and none of them leaks.

    The detail carries the shapes an operator-facing surface must never acquire
    — a traceback, an operating-system message, a path outside the reviewed set
    and an unbounded run of text — and none of them survives the rendering.
    """
    hostile = (
        "Traceback (most recent call last):\n"
        '  File "/opt/freedom-blades/platform/secret.py", line 1\n'
        f"OSError: [Errno 5] {INJECTED_MESSAGE}\n" + "x" * 10_000
    )
    reviewed = directory_targets()
    run = ProvisioningRun(
        applied=(
            AppliedItem(
                item_id=reviewed[0].item_id,
                path=reviewed[0].path,
                outcome=Outcome.CREATED,
                object_id="2049:1",
            ),
        ),
        refusal=ItemRefusal(
            item_id="V4", classification=classification, detail=hostile
        ),
        not_attempted=("V9", "V5"),
    )

    rendered = render_run(run, completed=False, targets=reviewed)

    assert rendered.startswith("REFUSED —")
    assert classification in rendered
    assert "V4" in rendered
    assert "not attempted        : V9, V5" in rendered
    assert "Traceback" not in rendered
    assert "File \"" not in rendered
    assert INJECTED_MESSAGE not in rendered
    assert "secret.py" not in rendered
    for line in rendered.splitlines():
        assert len(line) <= FIELD_WIDTH + 64, line[:80]


def test_an_injected_operating_system_failure_never_reaches_the_operator(
    over_the_model, capsys
) -> None:
    """The same property end to end, through the real mechanism.

    The injection lands on V9's `fchmod`, so the refusal is the reviewed
    `post-creation-mode-not-applied` over a real object, and the message the
    kernel-shaped failure carried is nowhere in what the operator sees.
    """
    targets = over_the_model

    with failing("fchmod", after=2):
        status = main(["--apply"])

    printed = capsys.readouterr()
    assert status == REFUSED_EXIT_CODE
    assert MODE_NOT_APPLIED in printed.out
    # The reviewed detail is shown — the rule withholds what is not one of them,
    # and an operator still learns which object is unfinished and why.
    assert provisioning_cli.WITHHELD_DETAIL not in printed.out
    assert "does not carry the mode the item declares" in printed.out
    assert INJECTED_MESSAGE not in printed.out + printed.err
    assert "Traceback" not in printed.out + printed.err
    assert "Errno" not in printed.out + printed.err
    # The residue is on disk, is reported, and is not reversed.
    residue = Path(targets[2].path)
    assert residue.is_dir()
    assert residue.stat().st_mode & 0o7777 != items_by_id()["V9"].mode


def test_an_unclassified_condition_says_nothing_about_itself(
    monkeypatch, model: Path, capsys
) -> None:
    """The catch-all reports that it does not know, and prints nothing it knows.

    A condition outside the reviewed vocabulary is the one whose text nobody has
    established is safe to show, so none of it is shown.
    """

    class Exploding:
        def __init__(self, **kwargs) -> None:
            pass

        def apply(self, targets):
            raise RuntimeError(INJECTED_MESSAGE)

    monkeypatch.setattr(provisioning_cli, "directory_targets", lambda: ())
    monkeypatch.setattr(provisioning_cli, "SystemIdentityLookup", FakeAccounts)
    monkeypatch.setattr(provisioning_cli, "DirectoryProvisioner", Exploding)

    status = main(["--apply"])

    printed = capsys.readouterr()
    assert status == UNCLASSIFIED_EXIT_CODE
    assert "UNCLASSIFIED" in printed.out and "UNCLASSIFIED" in printed.err
    assert INJECTED_MESSAGE not in printed.out + printed.err
    assert "RuntimeError" not in printed.out + printed.err
    assert "Traceback" not in printed.out + printed.err


# ---------------------------------------------------------------------------
# 6. A partial application, and the authority the entry point does not have
# ---------------------------------------------------------------------------


def test_a_partial_application_reports_residue_and_what_was_never_tried(
    over_the_model, capsys
) -> None:
    """The state an operator has to read after a refusal, in the output.

    An unexplained object at V9's name refuses; V12 and V4 were created by this
    run and are on disk; V5 was never attempted. Nothing is rolled back.
    """
    targets = over_the_model
    laboratory = Path(targets[1].path)
    laboratory.parent.mkdir(mode=0o755)
    laboratory.mkdir(mode=0o750)
    (laboratory / "runs").write_bytes(b"")

    status = main(["--apply"])

    printed = capsys.readouterr()
    assert status == REFUSED_EXIT_CODE
    assert f"V9 — {OBJECT_WRONG_TYPE}" in printed.out
    assert "not attempted        : V5" in printed.out
    assert "V12" in printed.out and "V4" in printed.out
    assert OBJECT_WRONG_TYPE in printed.err
    # No automatic rollback: the two verified objects and the refusing one are
    # exactly where they were.
    assert Path(targets[0].path).is_dir()
    assert laboratory.is_dir()
    assert (laboratory / "runs").is_file()
    assert not Path(targets[3].path).exists()


def test_an_unidentified_residue_is_reported_and_blocks_a_guarded_reversal(
    over_the_model, capsys
) -> None:
    """The residual case, rendered as residue rather than as a creation.

    Breaking the post-creation `open` leaves a directory this run made and
    cannot identify. It is in the account, it carries no identity, and the
    rendering says a guarded reversal is refused while it is present.
    """
    targets = over_the_model

    with failing("open", when=_with_dir_fd):
        status = main(["--apply"])

    printed = capsys.readouterr()
    assert status == REFUSED_EXIT_CODE
    assert "unidentified residue : V12" in printed.out
    assert Outcome.CREATED_IDENTITY_UNKNOWN.value in printed.out
    assert NO_IDENTITY in printed.out
    assert "refused while an unidentified object" in printed.out
    assert "not attempted        : V4, V9, V5" in printed.out
    assert Path(targets[0].path).is_dir()


def test_an_application_by_the_wrong_identity_refuses_before_any_creation(
    monkeypatch, model: Path, capsys
) -> None:
    """The reviewed provisioner requires the process to already **be** the owner.

    The entry point does not elevate, does not consult a credential and offers
    no way to ask it to. A run started as anything else refuses on the first
    item, before the first `mkdirat`.
    """
    targets = model_targets(model)
    monkeypatch.setattr(provisioning_cli, "directory_targets", lambda: targets)
    monkeypatch.setattr(
        provisioning_cli,
        "SystemIdentityLookup",
        lambda: FakeAccounts(uid_shift=1),
    )

    status = main(["--apply"])

    printed = capsys.readouterr()
    assert status == REFUSED_EXIT_CODE
    assert PROVISIONING_IDENTITY_REFUSED in printed.out
    assert "not attempted        : V4, V9, V5" in printed.out
    for target in targets:
        assert not Path(target.path).exists(), target.item_id


# ---------------------------------------------------------------------------
# 7. What the surface does not offer
# ---------------------------------------------------------------------------


def test_the_entry_point_imports_only_what_its_four_statements_need() -> None:
    """The import graph is the authority argument, not a promise about it.

    It reaches the applier and the account-database seam and nothing else: not
    the harness CLI, not the executor, not the materializer, not the case
    program, not a participant, not the lock, not the reservation record and not
    the ledger. There is therefore no call path from this program to an
    execution, a lifecycle initialization or a second applier.
    """
    absolute: set[str] = set()
    relative: dict[str, set[str]] = {}
    for node in ast.walk(TREE):
        if isinstance(node, ast.Import):
            absolute.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                relative.setdefault(node.module.split(".")[0], set()).update(
                    alias.name for alias in node.names
                )
            elif node.module:
                absolute.add(node.module.split(".")[0])

    assert absolute == {"__future__", "argparse", "sys", "typing"}
    assert set(relative) == {"provisioning", "boundary", "provisioner"}
    # The one thing it takes from the module that may start a process.
    assert relative["boundary"] == {"SystemIdentityLookup"}


def test_the_entry_point_offers_no_second_input_and_no_second_authority() -> None:
    """Scanned with comments and string literals removed.

    This module documents at length what it may not do, by name, so a scan that
    read the prose would fail on the sentence saying the thing is forbidden —
    which trains everyone to stop writing the sentence.
    """
    code = _code_only(SOURCE)
    for forbidden in (
        "sudo",
        "environ",
        "getenv",
        "putenv",
        "setuid",
        "seteuid",
        "setgid",
        "groupadd",
        "usermod",
        "tmpfiles",
        "popen",
        "system",
        "rollback",
        "verify",
        "ensure",
        "LABORATORY_LAYOUT",
        "LaboratoryLayout",
    ):
        assert forbidden not in code, f"the entry point names {forbidden!r} in code."

    options = {
        node.value
        for node in ast.walk(TREE)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("--")
    }
    assert options == {"--apply"}


def test_the_entry_point_writes_down_no_reviewed_value_of_its_own() -> None:
    """Not one path, owner, group or mode. A second statement of an approved
    value is a second definition of it, and the reviewed items are the only
    definition there is."""
    literals = [
        node.value
        for node in ast.walk(TREE)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    known = items_by_id()
    for item_id in APPLIED_DIRECTORY_ITEMS:
        item = known[item_id]
        for value in literals:
            assert item.subject not in value, f"{item_id}'s path is written here."
        assert not any(
            isinstance(node, ast.Constant) and node.value == item.mode
            for node in ast.walk(TREE)
        ), f"{item_id}'s mode is written here."
    assert not any(
        isinstance(node, ast.Constant) and node.value in {"freedomlab", "root"}
        for node in ast.walk(TREE)
    ), "an owner or group name is written here."


def test_the_exit_codes_distinguish_the_four_outcomes() -> None:
    """Zero means the delta is in place. It never means *the command ran*."""
    assert COMPLETED_EXIT_CODE == 0
    assert len({COMPLETED_EXIT_CODE, NOT_APPLIED_EXIT_CODE, REFUSED_EXIT_CODE,
                UNCLASSIFIED_EXIT_CODE}) == 4
    for status in (NOT_APPLIED_EXIT_CODE, REFUSED_EXIT_CODE, UNCLASSIFIED_EXIT_CODE):
        assert status != 0
        assert status != 1  # never the same as *something went wrong in here*


# ---------------------------------------------------------------------------
# 8. The detail rule — exact admission, in both directions
# ---------------------------------------------------------------------------
#
# **PR-20260918-LAB-V6P-R1-1.** The rule this section replaced admitted a detail
# whose characters were ASCII alphanumerics and a little punctuation, so
# `hunter2`, `DiscordToken ABCDEFG1234567890` and an environment value supplied
# without its variable name were all rendered unchanged. Ordinary characters are
# exactly what a secret is written in, so the admission is no longer made on
# characters at all: a detail is printed only when it is, in whole, one the
# applier produces.


def _details_the_applier_raises() -> dict[int, str]:
    """Every fixed detail the reviewed provisioner can raise, from its source.

    Read from the syntax tree rather than listed here, so a detail added to the
    applier is covered by this suite on the day it is added — and, because
    `test_the_admitted_vocabulary_is_exactly_what_the_applier_raises` compares
    this against `REVIEWED_DETAILS`, a detail added without being admitted fails
    the suite instead of silently being withheld from an operator.

    The call sites now name a constant rather than writing the prose inline, so
    a name is resolved against the module. A site that still carries an inline
    literal is collected as it stands, which is what makes an unadmitted one
    visible.
    """
    source = Path(provisioner_module.__file__)
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    found: dict[int, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name, index = node.func.id, 2
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
            index = 3 if name == "_residue" else None
        else:
            continue
        if name not in {"ProvisioningRefused", "RollbackRefused", "_residue"}:
            continue
        detail = node.args[index] if (index is not None and len(node.args) > index) else None
        for keyword in node.keywords:
            if keyword.arg == "detail":
                detail = keyword.value
        if isinstance(detail, ast.Constant) and isinstance(detail.value, str):
            found[detail.lineno] = detail.value
        elif isinstance(detail, ast.Name) and detail.id.startswith("DETAIL_"):
            found[detail.lineno] = getattr(provisioner_module, detail.id)
    return found


def _builder_call_sites() -> set[str]:
    """The detail builders a refusal is raised with.

    Only the `detail` position is read, so this names what the applier hands to
    a refusal rather than every function in the module whose name ends in
    `_detail`. An interpolation written inline at a raise site would appear
    here as no builder at all, and the assertion below would fail.
    """
    source = Path(provisioner_module.__file__)
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    builders: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            name, index = node.func.id, 2
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
            index = 3 if name == "_residue" else None
        else:
            continue
        if name not in {"ProvisioningRefused", "RollbackRefused", "_residue"}:
            continue
        detail = node.args[index] if (index is not None and len(node.args) > index) else None
        for keyword in node.keywords:
            if keyword.arg == "detail":
                detail = keyword.value
        if isinstance(detail, ast.Call) and isinstance(detail.func, ast.Name):
            builders.add(detail.func.id)
        else:
            assert not isinstance(detail, ast.JoinedStr), (
                "a detail is interpolated at a raise site; the varying part "
                "belongs in a builder the closed contract can admit."
            )
    return builders


def test_every_reviewed_detail_survives_the_renderer_unchanged() -> None:
    """**The other direction of the withholding rule, and the one that makes it
    honest.**

    A renderer that withheld everything would satisfy *no unsafe text is
    emitted* and tell an operator nothing. Every detail the reviewed applier can
    actually raise passes through intact — including the
    `classification: item_id — detail` form `apply()` builds — so what is
    withheld is exactly what is not one of them.
    """
    details = _details_the_applier_raises()
    assert len(details) >= 20, "the reviewed details were not found in the applier"

    # **Submitted exactly as the applier writes them.** `PR-20260918-LAB-V6P-R2-1`
    # was masked here by collapsing every detail before submitting it, which
    # asked the renderer a question no refusal ever asks it. Each value now goes
    # in as it stands, so this proves the admitted vocabulary is reachable
    # rather than proving that normalization reaches it.
    for detail in details.values():
        assert provisioning_cli._detail(detail) == detail, detail
        # The form `apply()` puts in `ItemRefusal.detail`, built by the real
        # refusal type rather than by re-stating its composition here.
        composed = str(ProvisioningRefused(OBJECT_WRONG_TYPE, "V9", detail))
        assert provisioning_cli._detail(composed) == composed, detail


def test_the_admitted_vocabulary_is_exactly_what_the_applier_raises() -> None:
    """**Explicit admission, proved in both directions.**

    `REVIEWED_DETAILS` is the act that makes a detail printable. This asserts it
    holds exactly the fixed details the applier's call sites carry, so neither a
    new detail that nobody admitted nor an admitted string that no refusal
    raises can survive unnoticed.
    """
    raised = set(_details_the_applier_raises().values())
    admitted = set(REVIEWED_DETAILS) - {""}

    assert raised == admitted
    # The empty detail is admitted deliberately: a refusal may carry none.
    assert "" in REVIEWED_DETAILS
    assert provisioning_cli._detail("") == ""
    # The two varying details are built, not interpolated at the raise site.
    assert _builder_call_sites() == {
        "unexplained_object_detail",
        "verification_failed_detail",
    }


def test_a_new_provisioner_detail_is_not_printable_until_it_is_admitted(
    monkeypatch,
) -> None:
    """**The finding's actual question.**

    A plausible new detail — prose about an object, in exactly the register the
    reviewed ones are written in — is withheld while it is not in the closed
    contract, and printed once it is. Admission is therefore an act, and not
    something a detail acquires by being written harmlessly.
    """
    invented = (
        "the directory this application created carries an extended attribute "
        "the item does not define, and it is left exactly as it is"
    )
    assert invented not in REVIEWED_DETAILS
    assert provisioning_cli._detail(invented) == provisioning_cli.WITHHELD_DETAIL
    # Raising it through the real refusal type does not admit it either: the
    # applier will carry any detail it is given, and the renderer is what asks.
    refusal = ProvisioningRefused(OBJECT_WRONG_TYPE, "V9", invented)
    assert provisioning_cli._detail(str(refusal)) == provisioning_cli.WITHHELD_DETAIL

    monkeypatch.setattr(
        provisioner_module,
        "REVIEWED_DETAILS",
        frozenset(REVIEWED_DETAILS | {invented}),
    )
    assert provisioning_cli._detail(invented) == invented


@pytest.mark.parametrize(
    "ordinary",
    [
        "hunter2",
        "DiscordToken ABCDEFG1234567890",
        "AWS SECRET ACCESS KEY abc def",
        "correcthorsebatterystaple",
        "s3cr3t db password for the laboratory account",
        "MIIEowIBAAKCAQEAr4nGZLMVihUP1zUbQFqLnAcKrHhBEoAhEVN0itsD",
        "ok",
        "the run finished",
        "freedomlab 1001 1001",
    ],
)
def test_an_arbitrary_alphanumeric_value_is_withheld_whole(ordinary: str) -> None:
    """**The regression for PR-20260918-LAB-V6P-R1-1, stated as its examples.**

    Every one of these is letters, digits and spaces, which is what the replaced
    rule admitted on. None of them is a detail the applier raises, so none of
    them is printed and no fragment of one survives.
    """
    rendered = provisioning_cli._detail(ordinary)

    assert rendered == provisioning_cli.WITHHELD_DETAIL
    for fragment in ordinary.split():
        if len(fragment) > 3:
            assert fragment not in rendered


def test_classification_membership_alone_cannot_make_a_detail_printable() -> None:
    """A value's being a reviewed *classification* says nothing about printing it.

    The two vocabularies answer different questions — *which rule refused* and
    *what may an operator be told* — and one is not a licence for the other.
    """
    for classification in sorted(PROVISIONER_REFUSALS):
        assert classification not in REVIEWED_DETAILS
        assert (
            provisioning_cli._detail(classification)
            == provisioning_cli.WITHHELD_DETAIL
        )
    for finding in OBSERVATION_DISCREPANCIES:
        assert (
            provisioning_cli._detail(finding) == provisioning_cli.WITHHELD_DETAIL
        )


def test_a_composed_detail_cannot_carry_an_unadmitted_detail() -> None:
    """The composed form is rebuilt, not pattern-matched.

    A real classification and a real item identifier in front of arbitrary text
    do not admit the text behind them, and a composed value naming an item this
    program never handed over is not admitted at all.
    """
    reviewed = provisioner_module.DETAIL_BARRIER_FAILED

    assert (
        provisioning_cli._detail(f"{OBJECT_WRONG_TYPE}: V9 — {reviewed}")
        == f"{OBJECT_WRONG_TYPE}: V9 — {reviewed}"
    )
    for hostile in (
        f"{OBJECT_WRONG_TYPE}: V9 — hunter2",
        f"{OBJECT_WRONG_TYPE}: V9 — PGPASSWORD is hunter2",
        f"invented-classification: V9 — {reviewed}",
        # An item this program did not hand over.
        f"{OBJECT_WRONG_TYPE}: V99 — {reviewed}",
        # The separator alone is not the contract.
        f"{OBJECT_WRONG_TYPE} V9 — {reviewed}",
    ):
        assert (
            provisioning_cli._detail(hostile) == provisioning_cli.WITHHELD_DETAIL
        ), hostile
    # A composed refusal with no detail at all is still a complete statement.
    assert (
        provisioning_cli._detail(f"{OBJECT_WRONG_TYPE}: V9")
        == f"{OBJECT_WRONG_TYPE}: V9"
    )


def test_the_finite_discrepancy_variation_is_admitted_and_nothing_else_is() -> None:
    """The two details that vary, across the whole closed observation vocabulary.

    Every list the applier can build from `OBSERVATION_DISCREPANCIES` is
    admitted — including the empty one and a repeated finding, both of which
    `_discrepancies` can produce — and a list holding anything else is not.
    """
    builders = (unexplained_object_detail, verification_failed_detail)
    for build in builders:
        assert provisioning_cli._detail(build(())) == build(())
        for finding in OBSERVATION_DISCREPANCIES:
            assert provisioning_cli._detail(build((finding,))) == build((finding,))
        whole = tuple(OBSERVATION_DISCREPANCIES)
        assert provisioning_cli._detail(build(whole)) == build(whole)
        repeated = (OBSERVATION_DISCREPANCIES[0],) * 3
        assert provisioning_cli._detail(build(repeated)) == build(repeated)

        # The varying part cannot carry anything but closed findings.
        for smuggled in ("hunter2", "/var/lib/freedom-blades", "PGPASSWORD=x"):
            forged = build((OBSERVATION_DISCREPANCIES[0], smuggled))
            assert is_reviewed_detail(forged) is False
            assert (
                provisioning_cli._detail(forged)
                == provisioning_cli.WITHHELD_DETAIL
            ), forged
        # Nor can the fixed half be rewritten around a real list.
        tampered = build(whole).replace("It is left", "It was repaired")
        assert (
            provisioning_cli._detail(tampered) == provisioning_cli.WITHHELD_DETAIL
        )


def test_no_reviewed_detail_is_truncated_by_the_bound() -> None:
    """The bound is wide enough for every detail the applier can raise.

    A bound that cut one of them would hand an operator a sentence with its end
    missing, which is the half of *bounded and safe* that is easy to lose. A
    longer detail added to the applier later fails here.
    """
    candidates = list(_details_the_applier_raises().values())
    candidates.append(unexplained_object_detail(OBSERVATION_DISCREPANCIES))
    candidates.append(verification_failed_detail(OBSERVATION_DISCREPANCIES))
    widest = max(
        len(f"{OBJECT_WRONG_TYPE}: V12 — {' '.join(detail.split())}")
        for detail in candidates
    )
    assert widest <= FIELD_WIDTH


@pytest.mark.parametrize(
    "hostile",
    [
        "Traceback (most recent call last):",
        "OSError: [Errno 5] Input/output error",
        "/var/lib/freedom-blades/laboratory/runs",
        "PGPASSWORD=hunter2",
        "uid=0(root) gid=0(root) groups=0(root)",
        "ordinary prose, then " + "x" * 10_000 + " /var/lib/freedom-blades",
        "ééé 一二三 😀",
        "drwxr-xr-x 2 freedomlab freedomlab 4096 Sep 18 runs",
    ],
)
def test_a_detail_outside_the_reviewed_vocabulary_is_withheld_whole(
    hostile: str,
) -> None:
    """Withheld whole, never in part: no fragment of the input survives.

    The long case is why the admission is decided **before** the bound: a check
    applied after truncation would have judged only the first `FIELD_WIDTH`
    characters of the ten thousand in front of it.
    """
    rendered = provisioning_cli._detail(hostile)

    assert rendered == provisioning_cli.WITHHELD_DETAIL
    assert len(rendered) <= FIELD_WIDTH
    for fragment in hostile.split():
        if len(fragment) > 3:
            assert fragment not in rendered


def test_a_control_character_never_reaches_the_operators_terminal() -> None:
    """An escape sequence is defanged rather than merely withheld.

    Every field goes through the same stripping, including the paths and
    identities the withholding rule does not apply to, so nothing this program
    prints can address a terminal instead of being read by it.
    """
    hostile = "\x1b[2J\x1b[H you are root now\r\nAPPLIED — all four items"

    for rendered in (
        provisioning_cli._detail(hostile),
        provisioning_cli._bounded(hostile),
    ):
        assert "\x1b" not in rendered
        assert "\r" not in rendered and "\n" not in rendered
    # A reviewed detail wrapped in control characters is not admitted around
    # them either: the value **as supplied** is what is asked about, and a value
    # with an escape sequence in it is not the reviewed detail. Stripping the
    # sequence first would have admitted it, which is PR-20260918-LAB-V6P-R2-1
    # in its control-character form.
    reviewed = provisioner_module.DETAIL_BARRIER_FAILED
    assert (
        provisioning_cli._detail(f"\x1b[2J{reviewed}")
        == provisioning_cli.WITHHELD_DETAIL
    )


def test_a_classification_outside_the_closed_set_is_named_as_unrecognized() -> None:
    """The vocabulary is imported, so *this is not one of them* is decidable."""
    assert provisioning_cli._classification(OBJECT_WRONG_TYPE) == OBJECT_WRONG_TYPE
    for invented in ("repaired-it-for-you", "ok", "", "provisioner-armed"):
        assert invented not in PROVISIONER_REFUSALS
        assert (
            provisioning_cli._classification(invented)
            == provisioning_cli.UNRECOGNIZED_CLASSIFICATION
        )


# ---------------------------------------------------------------------------
# 8a. The admission is made on the value as supplied — PR-20260918-LAB-V6P-R2-1
# ---------------------------------------------------------------------------
#
# **The finding.** `_detail()` collapsed whitespace and asked the applier's
# contract about the *collapsed* value, so a value that was not a reviewed
# detail became one on the way in. A leading or trailing space, a doubled
# internal space, or a tab, newline or carriage return substituted for a space
# in an otherwise reviewed sentence all normalized into that sentence and were
# printed as the admitted fixed detail. The exact-membership and whole-value
# claims the surface rests on were therefore false: the contract was being
# asked about a string the caller never supplied.
#
# The rule now is that the **complete supplied value itself** must be one the
# applier produces. Bounding, single-line rendering and control-character
# removal remain, strictly **after** admission, as defence in depth over a
# value the contract has already accepted. The tests below hold both halves:
# every value the applier can actually produce survives unchanged, and every
# value one whitespace alteration away from one is withheld whole.

#: The six alteration classes the finding names, as functions of a candidate.
#: Each produces a value that is **not** a detail the applier can raise, but
#: which the collapsing rule turned into one.
WHITESPACE_ALTERATIONS = (
    ("leading-space", lambda text: " " + text),
    ("trailing-space", lambda text: text + " "),
    ("doubled-internal-space", lambda text: text.replace(" ", "  ", 1)),
    ("tab-for-space", lambda text: text.replace(" ", "\t", 1)),
    ("newline-for-space", lambda text: text.replace(" ", "\n", 1)),
    ("carriage-return-for-space", lambda text: text.replace(" ", "\r", 1)),
)


def _every_admissible_bare_detail() -> list[str]:
    """Every bare detail the reviewed applier can produce, fixed and varying.

    The fixed ones are read from the applier's own call sites; the two that
    carry finite variation are produced by their builders across the whole
    closed observation vocabulary, including the empty and repeated lists
    `_discrepancies` can build.
    """
    details = list(_details_the_applier_raises().values())
    details.append("")
    for build in (unexplained_object_detail, verification_failed_detail):
        details.append(build(()))
        details.append(build(tuple(OBSERVATION_DISCREPANCIES)))
        details.append((build((OBSERVATION_DISCREPANCIES[0],) * 3)))
        details.extend(build((finding,)) for finding in OBSERVATION_DISCREPANCIES)
    return details


def _every_admissible_composed_detail() -> list[str]:
    """Every composed detail the real `apply()` path can record.

    `apply()` stores `str(refusal)` in `ItemRefusal.detail`, so the composition
    is built by the real refusal type over the real closed vocabularies — each
    provisioning classification, each identifier this program hands over, and
    each bare detail above — rather than by restating its shape here.
    """
    return [
        str(ProvisioningRefused(classification, item_id, detail))
        for classification in sorted(PROVISIONER_REFUSALS)
        for item_id in APPLIED_DIRECTORY_ITEMS
        for detail in _every_admissible_bare_detail()
    ]


def test_every_bare_detail_the_applier_produces_is_submitted_and_rendered_unchanged() -> None:
    """**The positive half, with nothing done to the value on the way in.**

    Each detail is submitted exactly as the applier writes it and must come
    back identical. A renderer that withheld everything would satisfy the
    finding and tell an operator nothing, so this is what keeps the withholding
    rule honest.
    """
    details = _every_admissible_bare_detail()
    assert len(details) >= 20, "the reviewed details were not found in the applier"

    for detail in details:
        assert provisioning_cli._detail(detail) == detail, detail


def test_every_composed_detail_the_apply_path_records_is_rendered_unchanged() -> None:
    """The same, for the `classification: item_id — detail` form `apply()` records."""
    composed = _every_admissible_composed_detail()
    assert len(composed) >= 100

    for value in composed:
        assert provisioning_cli._detail(value) == value, value


def test_a_real_refusal_from_apply_renders_its_detail_unchanged(model: Path) -> None:
    """The positive half again, driven through the real applier rather than built.

    `apply()` records `str(refusal)`, and this is that value arriving at the
    renderer from an actual refused run over the model host — so the composed
    form the tests above construct is the one the production path really
    produces, rather than one this suite composed and then agreed with.
    """
    targets = model_targets(model)
    provisioner = DirectoryProvisioner(lookup=FakeAccounts(), armed=False)

    run = provisioner.apply(targets)

    assert run.refusal is not None
    recorded = run.refusal.detail
    item_ids = frozenset(target.item_id for target in targets)
    assert provisioning_cli._detail(recorded, item_ids) == recorded
    assert provisioner_module.DETAIL_NOT_ARMED in recorded


@pytest.mark.parametrize("alteration,alter", WHITESPACE_ALTERATIONS, ids=lambda value: value if isinstance(value, str) else "")
def test_a_whitespace_altered_bare_detail_is_withheld_whole(
    alteration: str, alter
) -> None:
    """**The regression for PR-20260918-LAB-V6P-R2-1.**

    One space, tab, newline or carriage return away from a reviewed detail is
    not that detail. The whole value is withheld — not trimmed back to the
    reviewed sentence, not partially printed — because a rule that normalized
    first would admit a value nobody reviewed on the strength of a value
    nobody supplied.
    """
    for detail in _every_admissible_bare_detail():
        altered = alter(detail)
        if altered == detail:
            continue  # nothing to alter: the empty detail has no space in it
        assert provisioning_cli._detail(altered) == provisioning_cli.WITHHELD_DETAIL, (
            alteration,
            detail,
        )


@pytest.mark.parametrize("alteration,alter", WHITESPACE_ALTERATIONS, ids=lambda value: value if isinstance(value, str) else "")
def test_a_whitespace_altered_composed_detail_is_withheld_whole(
    alteration: str, alter
) -> None:
    """The same six alteration classes, for the composed form `apply()` records.

    Codex reproduced the finding on the bare form; the composed form reaches an
    operator by the same path and had the same defect, including alterations
    landing in the classification and the identifier rather than the detail.
    """
    for value in _every_admissible_composed_detail():
        altered = alter(value)
        if altered == value:
            continue
        assert provisioning_cli._detail(altered) == provisioning_cli.WITHHELD_DETAIL, (
            alteration,
            value,
        )


#: Whitespace `str.split()` also collapsed, beyond the space, tab, newline and
#: carriage return the finding names. Every one of these substituted for a space
#: in a reviewed detail was admitted by the replaced rule.
UNICODE_WHITESPACE = (
    ("no-break-space", "\xa0"),
    ("form-feed", "\x0c"),
    ("vertical-tab", "\x0b"),
    ("ogham-space-mark", "\u1680"),
    ("en-quad", "\u2000"),
    ("line-separator", "\u2028"),
    ("ideographic-space", "\u3000"),
)


@pytest.mark.parametrize("name,character", UNICODE_WHITESPACE)
def test_unicode_whitespace_cannot_normalize_into_a_reviewed_detail(
    name: str, character: str
) -> None:
    """The finding's closure, not just its six named examples.

    `str.split()` splits on everything `str.isspace()` accepts, so the replaced
    rule admitted a reviewed detail carrying a no-break space, a form feed or an
    ideographic space just as readily as one carrying a tab. The rule is now
    identity with the supplied value, so all of them are withheld for the same
    single reason rather than each needing its own defence.
    """
    reviewed = provisioner_module.DETAIL_BARRIER_FAILED
    altered = reviewed.replace(" ", character, 1)
    assert altered != reviewed
    # The replaced rule would have collapsed this back onto the reviewed value.
    assert " ".join(altered.split()) == reviewed, name
    assert provisioning_cli._detail(altered) == provisioning_cli.WITHHELD_DETAIL
    composed = str(ProvisioningRefused(OBJECT_WRONG_TYPE, "V9", altered))
    assert provisioning_cli._detail(composed) == provisioning_cli.WITHHELD_DETAIL


def test_the_admitted_reviewed_detail_is_not_recoverable_from_a_withheld_one() -> None:
    """Withheld **whole**: no fragment of the altered value survives.

    The finding's severity is that the operator was shown the reviewed
    sentence for input that was not it. The withholding notice must therefore
    carry none of the submitted text, not a shortened version of it.
    """
    reviewed = provisioner_module.DETAIL_BARRIER_FAILED
    notice = provisioning_cli.WITHHELD_DETAIL
    for _, alter in WHITESPACE_ALTERATIONS:
        rendered = provisioning_cli._detail(alter(reviewed))
        assert rendered == notice
        # Every distinctive word of the reviewed sentence is gone. Words the
        # fixed notice itself contains are excluded, so this measures what
        # survived from the input rather than what the constant always says.
        for fragment in reviewed.split():
            if len(fragment) > 6 and fragment not in notice:
                assert fragment not in rendered


def test_the_bound_alters_no_admitted_value() -> None:
    """**The stop condition the assignment names, made mechanical.**

    Bounding is defence in depth *after* admission, so it may never be what
    changes an admitted reviewed constant: if it rewrote one, the value an
    operator saw would differ from the value the contract admitted, and the
    exact rule would be weakened in silence. Nothing the applier can produce is
    altered today — bare or composed — and a detail added later that this bound
    *would* rewrite fails here rather than passing quietly.
    """
    for value in _every_admissible_bare_detail():
        assert provisioning_cli._bounded(value) == value, value
    for value in _every_admissible_composed_detail():
        assert provisioning_cli._bounded(value) == value, value
        assert len(value) <= FIELD_WIDTH, value


def test_no_normalization_stands_between_a_candidate_and_the_contract() -> None:
    """**The structural second line of evidence.**

    The behavioral tests above are the authority; this is what names the defect
    if it is reintroduced in a form that happens to pass them. `_detail` may
    call the contract and the bound and nothing else: a `.split()`, `.strip()`,
    `.lower()`, `.replace()`, `.join()`, `unicodedata.normalize()` or a slice
    anywhere in it would be a transformation applied to a candidate, and the
    only transformation permitted is the one the contract has already admitted.
    """
    function = next(
        node
        for node in ast.walk(TREE)
        if isinstance(node, ast.FunctionDef) and node.name == "_detail"
    )
    called: list[str] = []
    # The body only: the signature carries `Collection[str]`, and an annotation
    # is not a path a candidate travels.
    for statement in function.body:
        for node in ast.walk(statement):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called.append(node.func.attr)
            assert not isinstance(node, ast.Subscript), (
                "`_detail` slices a candidate; a truncation may not participate "
                "in deciding that a value is admitted."
            )
    assert set(called) <= {"isinstance", "is_reviewed_refusal_detail", "_bounded"}, called
    # The contract is asked before the bound is ever reached.
    assert called.index("is_reviewed_refusal_detail") < called.index("_bounded")


def test_the_admission_is_asked_about_the_argument_itself(monkeypatch) -> None:
    """The contract receives the caller's value, character for character.

    This is the finding stated as a property rather than as its examples: for
    every hostile, altered and reviewed value, whatever `_detail` hands to
    `is_reviewed_refusal_detail` is exactly what `_detail` was given.
    """
    seen: list[str] = []

    def recording(text: str, item_ids) -> bool:
        seen.append(text)
        return provisioner_module.is_reviewed_refusal_detail(text, item_ids)

    monkeypatch.setattr(provisioning_cli, "is_reviewed_refusal_detail", recording)

    reviewed = provisioner_module.DETAIL_BARRIER_FAILED
    submitted = [
        reviewed,
        " " + reviewed,
        reviewed.replace(" ", "\n", 1),
        "hunter2",
        "  ordinary   prose  ",
        "\x1b[2J" + reviewed,
        str(ProvisioningRefused(OBJECT_WRONG_TYPE, "V9", reviewed)),
    ]
    for value in submitted:
        provisioning_cli._detail(value)

    assert seen == submitted


def test_a_non_string_detail_is_withheld_rather_than_converted() -> None:
    """`str()` is a transformation too, and it can render an object's text.

    The contract is asked about strings. Anything else is withheld without
    being converted, so no object's `__str__` can reach the operator surface
    by way of the admission — and the renderer stays total, which matters
    because `render_run` is called outside the handler that catches everything.
    """

    class Talkative:
        def __str__(self) -> str:  # pragma: no cover - must never be called
            raise AssertionError("the candidate was converted before admission")

    assert provisioning_cli._detail(Talkative()) == provisioning_cli.WITHHELD_DETAIL
    for value in (None, 17, b"bytes", ["a", "list"]):
        assert provisioning_cli._detail(value) == provisioning_cli.WITHHELD_DETAIL


def test_the_finite_discrepancy_details_admit_only_what_the_builders_produce() -> None:
    """The two varying details, altered in each of the places they vary.

    A whitespace change in the fixed prefix, in the list separator, against the
    brackets, against the quoting or inside a member all make a value the
    builders cannot produce, so all of them are withheld whole while the
    builders' own output is admitted unchanged.
    """
    finding = OBSERVATION_DISCREPANCIES[0]
    for build in (unexplained_object_detail, verification_failed_detail):
        genuine = build((finding, OBSERVATION_DISCREPANCIES[1]))
        assert provisioning_cli._detail(genuine) == genuine

        forgeries = (
            genuine.replace(": [", ":  [", 1),          # before the list
            genuine.replace("', '", "',  '", 1),        # the separator
            genuine.replace("[", "[ ", 1),              # inside the bracket
            genuine.replace("]", " ]", 1),              # inside the bracket
            genuine.replace("'" + finding, "' " + finding, 1),  # after a quote
            genuine.replace(finding, finding.replace(" ", "  ", 1), 1)
            if " " in finding
            else genuine + " ",                          # inside a member
        )
        for forged in forgeries:
            if forged == genuine:
                continue
            assert is_reviewed_detail(forged) is False, forged
            assert (
                provisioning_cli._detail(forged) == provisioning_cli.WITHHELD_DETAIL
            ), forged


# ---------------------------------------------------------------------------
# 9. The rest of the operator surface is closed the same way
# ---------------------------------------------------------------------------


def test_an_identifier_or_path_this_program_did_not_supply_is_not_printed() -> None:
    """Identifiers and paths are admitted by identity with the handed targets.

    They are the fields an operating-system message and a directory listing
    arrive in, and the reviewed targets are the only values this program ever
    supplied, so anything else is named or withheld rather than rendered.
    """
    reviewed = directory_targets()
    run = ProvisioningRun(
        applied=(
            AppliedItem(
                item_id="V99",
                path="/etc/shadow",
                outcome=Outcome.CREATED,
                object_id="2049:7",
            ),
        ),
        refusal=ItemRefusal(
            item_id="V99",
            classification=OBJECT_WRONG_TYPE,
            detail=provisioner_module.DETAIL_BARRIER_FAILED,
        ),
        not_attempted=("V98",),
    )

    rendered = render_run(run, completed=False, targets=reviewed)

    assert "V99" not in rendered and "V98" not in rendered
    assert "/etc/shadow" not in rendered and "shadow" not in rendered
    assert UNRECOGNIZED_ITEM in rendered
    assert WITHHELD_PATH in rendered
    # And the reviewed ones still render, so this is admission and not silence.
    reviewed_run = ProvisioningRun(
        applied=tuple(
            AppliedItem(
                item_id=target.item_id,
                path=target.path,
                outcome=Outcome.CREATED,
                object_id="2049:1",
            )
            for target in reviewed
        ),
        refusal=None,
        not_attempted=(),
    )
    complete = render_run(reviewed_run, completed=True, targets=reviewed)
    for target in reviewed:
        assert target.item_id in complete
        assert target.path in complete
    assert UNRECOGNIZED_ITEM not in complete and WITHHELD_PATH not in complete


@pytest.mark.parametrize(
    "recorded, shown",
    [
        ("2049:97831", "2049:97831"),
        ("0:0", "0:0"),
        ("", NO_IDENTITY),
        ("2049:97831 /var/lib/freedom-blades", WITHHELD_IDENTITY),
        ("uid=0(root)", WITHHELD_IDENTITY),
        ("02049:1", WITHHELD_IDENTITY),  # rebuilding it does not reproduce it
        ("١:٢", WITHHELD_IDENTITY),  # Unicode digits, rebuilt as ASCII
        ("2049", WITHHELD_IDENTITY),
        ("-1:-1", WITHHELD_IDENTITY),
    ],
)
def test_an_object_identity_is_admitted_only_by_being_rebuilt(
    recorded: str, shown: str
) -> None:
    """Two integers and a colon, reconstructed, or nothing."""
    assert provisioning_cli._identity(recorded) == shown
