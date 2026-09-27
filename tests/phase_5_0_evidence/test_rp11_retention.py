"""RP-11, C-P5.0-R5-RP11-I1 — B0-RA, the read-only Pass A retention check,
against §7.1 of the R5-amended operational-evidence draft (SHA-256 `5e06a388…`).

Every test builds a real Pass A capture root under a pytest temporary
directory with the real mechanism, writes a Pass A handback carrying its binding
block, then does one hostile thing to the handback, the supplied root or the
retained tree — or races the verifier while it runs — and asserts:

* the stop's condition and reason, and every name in either set difference;
* that B0-RA changed nothing: the suite's own no-follow snapshot of the tree,
  including inode numbers, link counts, sizes, modification and change times
  and admitted content, is identical before and after; and
* that no unadmitted object was ever opened.
"""
from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path

import pytest

from tests.phase_5_0_evidence.rp11_fixtures import (
    PASS_A,
    PASS_B,
    FaultFilesystem,
    Host,
    RecordingReadOnlyFilesystem,
    ScriptedLauncher,
    act,
    open_session,
    tree,
    write_handback,
    writes,
)
from tools.phase_5_0_evidence.capture_contract import (
    HandbackBinding,
    IndexState,
    canonical_bytes,
    parse_canonical,
)
from tools.phase_5_0_evidence.execution.retention_check import (
    CONDITION_FINAL_DIGEST,
    CONDITION_HANDBACK,
    CONDITION_NAME_AGREEMENT,
    CONDITION_PRESENCE,
    CONDITION_ROOT_EQUALITY,
    CONDITION_X4,
    EVIDENTIARY_LIMIT,
    PosixReadOnlyFilesystem,
    RetentionCheck,
    RetentionRefused,
)

REPOSITORY = Path(__file__).resolve().parents[2]
UNADMITTED = ("streams/stdout/000002", "streams/stderr/000002")


class PassA:
    """A retained Pass A root and its digest-pinned handback."""

    def __init__(self, tmp_path: Path, *, acts: int = 2, unadmitted: bool = True) -> None:
        self.host = Host.under(tmp_path)
        self.root = self.host.root()
        filesystem = FaultFilesystem()
        self.session = open_session(self.host, filesystem=filesystem, launcher=ScriptedLauncher())
        for index in range(1, acts + 1):
            if unadmitted and index == acts:
                filesystem.stage = "P-6:file-barrier"
            self.session.run_act(act(f"A1-{index:02d}", writes(b"", b"")))
        if self.session.outcome is None:
            self.session.complete()
        assert self.session.outcome.x4_validity == "valid"
        self.handback = tmp_path / "pass-a-handback.md"
        self.handback_sha256 = write_handback(self.handback, self.session)
        self.binding = self.session.binding()

    def path(self, name: str) -> Path:
        return Path(self.root) / name

    def check(
        self,
        *,
        root: str | None = None,
        sha256: str | None = None,
        filesystem=None,  # type: ignore[no-untyped-def]
        pass_id: str = PASS_A,
    ):  # type: ignore[no-untyped-def]
        return RetentionCheck(
            handback_path=str(self.handback),
            handback_sha256=sha256 or self.handback_sha256,
            capture_root=self.root if root is None else root,
            expected_pass_id=pass_id,
            filesystem=filesystem,
        ).run()

    def rebind(self, **changes) -> None:  # type: ignore[no-untyped-def]
        """A new, internally consistent handback with changed binding fields."""
        fields = dict(
            pass_id=self.binding.pass_id,
            capture_root=self.binding.capture_root,
            x3_outcome=self.binding.x3_outcome,
            x4_validity=self.binding.x4_validity,
            final_state=self.binding.final_state,
            capture_index_sha256=self.binding.capture_index_sha256,
        )
        fields.update(changes)
        self.binding = HandbackBinding(**fields)
        self.handback.write_bytes(("# handback\n\n" + self.binding.render()).encode())
        self.handback_sha256 = hashlib.sha256(self.handback.read_bytes()).hexdigest()

    def forge_final(self, mutate) -> None:  # type: ignore[no-untyped-def]
        """Rewrite F and re-pin a consistent handback: a forged pair."""
        path = self.path(self.binding.final_state)
        document = parse_canonical(path.read_bytes())
        mutate(document)
        path.write_bytes(canonical_bytes(document))
        self.rebind(capture_index_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def _assert_stopped(result, condition: int, reason: str | None = None) -> None:  # type: ignore[no-untyped-def]
    assert not result.passed
    assert result.failed_condition == condition, result
    if reason is not None:
        assert result.reason == reason, result


# ===========================================================================
# The passing case, one-shot, and non-mutation
# ===========================================================================


def test_b0_ra_passes_on_an_intact_root_and_changes_nothing(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    before = tree(pass_a.root)
    recording = RecordingReadOnlyFilesystem()
    result = pass_a.check(filesystem=recording)
    assert result.passed, result
    assert (result.observed_not_recorded, result.recorded_not_observed, result.type_mismatches) == ((), (), ())
    assert result.evidentiary_limit == EVIDENTIARY_LIMIT
    assert tree(pass_a.root) == before
    # Exactly the admitted regular files were opened: F, its chain, record 1
    # and the two streams it binds. Act 2's unadmitted streams never were.
    admitted = {"000000.open.json", "000001.open.json", "000002.final.json", "000001.json", "000001"}
    assert {name.decode() for name in recording.opened_files} == admitted
    assert recording.opened_files.count(b"000001") == 2  # stdout and stderr of act 1


def test_b0_ra_never_opens_an_unadmitted_object(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    for name in UNADMITTED:
        pass_a.path(name).chmod(0o000)
    recording = RecordingReadOnlyFilesystem()
    result = pass_a.check(filesystem=recording)
    assert result.passed, result
    assert b"000002" not in recording.opened_files


def test_b0_ra_runs_once(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    check = RetentionCheck(
        handback_path=str(pass_a.handback),
        handback_sha256=pass_a.handback_sha256,
        capture_root=pass_a.root,
        expected_pass_id=PASS_A,
    )
    assert check.run().passed
    with pytest.raises(RetentionRefused):
        check.run()


def test_the_verifier_module_cannot_write() -> None:
    """Structural: no call or flag in `retention_check.py` can change a file."""
    source = (REPOSITORY / "tools/phase_5_0_evidence/execution/retention_check.py").read_text(encoding="utf-8")
    tree_ = ast.parse(source)
    mutating = {
        "write", "pwrite", "writev", "unlink", "remove", "rename", "replace", "renames",
        "mkdir", "makedirs", "rmdir", "removedirs", "link", "symlink", "chmod", "fchmod",
        "lchmod", "chown", "fchown", "lchown", "truncate", "ftruncate", "utime", "fsync",
        "fdatasync", "mkfifo", "mknod", "setxattr", "removexattr", "copy_file_range",
        "sendfile", "posix_fallocate",
    }
    for node in ast.walk(tree_):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ("os", "shutil"):
                assert node.func.attr not in mutating, node.func.attr
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open"
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "os":
            assert node.attr not in {"O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC", "O_APPEND", "O_TMPFILE", "O_EXCL"}
    imported = {
        alias.name for node in ast.walk(tree_) if isinstance(node, ast.ImportFrom) for alias in node.names
    }
    assert "capture_store" not in {
        node.module.split(".")[-1] for node in ast.walk(tree_) if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imported & {"CaptureRootStore", "PosixCaptureFilesystem", "link_unnamed_descriptor"}


# ===========================================================================
# Condition 0 and 1 — the handback and the supplied root
# ===========================================================================


def test_a_tampered_handback_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    before = tree(pass_a.root)
    data = pass_a.handback.read_bytes()
    pass_a.handback.write_bytes(data.replace(b"fixture", b"fixturE"))
    _assert_stopped(pass_a.check(), CONDITION_HANDBACK, "handback-digest-mismatch")
    assert tree(pass_a.root) == before


@pytest.mark.parametrize(
    "changes, reason",
    [
        ({"x3_outcome": "failed", "final_state": None, "capture_index_sha256": None}, "handback-records-no-successful-x3"),
        ({"x3_outcome": "not-made", "final_state": None, "capture_index_sha256": None}, "handback-records-no-successful-x3"),
        ({"x4_validity": "inconclusive"}, "handback-records-no-valid-x4"),
        ({"final_state": None}, "handback-records-no-final-state"),
        ({"capture_index_sha256": None}, "handback-records-no-final-state"),
        ({"pass_id": PASS_B}, "handback-pass-id-mismatch"),
    ],
)
def test_a_handback_that_records_no_admissible_final_state_stops(tmp_path: Path, changes, reason) -> None:  # type: ignore[no-untyped-def]
    pass_a = PassA(tmp_path)
    pass_a.rebind(**changes)
    _assert_stopped(pass_a.check(), CONDITION_HANDBACK, reason)


def test_a_handback_without_or_with_two_binding_blocks_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    block = pass_a.binding.render()
    for text, reason in (
        ("# no block\n", "handback-binding-binding-absent"),
        ("# two\n" + block + block, "handback-binding-binding-ambiguous"),
    ):
        pass_a.handback.write_text(text)
        sha = hashlib.sha256(pass_a.handback.read_bytes()).hexdigest()
        _assert_stopped(pass_a.check(sha256=sha), CONDITION_HANDBACK, reason)


@pytest.mark.parametrize("variant", ["trailing-slash", "sibling", "relative", "double-slash"])
def test_a_supplied_root_that_is_not_byte_for_byte_the_record_stops(tmp_path: Path, variant: str) -> None:
    pass_a = PassA(tmp_path)
    supplied = {
        "trailing-slash": pass_a.root + "/",
        "sibling": pass_a.root + "-b",
        "relative": os.path.relpath(pass_a.root),
        "double-slash": pass_a.root.replace("/host/", "/host//"),
    }[variant]
    _assert_stopped(pass_a.check(root=supplied), CONDITION_ROOT_EQUALITY, "capture-root-differs-from-the-record")


def test_an_absent_root_stops_at_presence(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    os.rename(pass_a.root, pass_a.root + "-moved")
    _assert_stopped(pass_a.check(), CONDITION_PRESENCE, "root-absent-or-not-a-directory")


# ===========================================================================
# Conditions 2, 3 and 4 — F, its digest, the chain, records and streams
# ===========================================================================


def test_an_absent_final_state_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    pass_a.path(pass_a.binding.final_state).unlink()
    _assert_stopped(pass_a.check(), CONDITION_PRESENCE, "final-state-absent")


def test_a_second_final_state_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    pass_a.path("index/000009.final.json").write_bytes(pass_a.path(pass_a.binding.final_state).read_bytes())
    _assert_stopped(pass_a.check(), CONDITION_X4, "not-the-only-final-state")


def test_a_stale_capture_index_digest_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    pass_a.rebind(capture_index_sha256="0" * 64)
    _assert_stopped(pass_a.check(), CONDITION_FINAL_DIGEST, "final-state-digest-mismatch")


def test_a_broken_chain_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    path = pass_a.path("index/000000.open.json")
    document = parse_canonical(path.read_bytes())
    document["tool_sha256"] = "6" * 64
    path.write_bytes(canonical_bytes(document))
    _assert_stopped(pass_a.check(), CONDITION_X4, "chain-broken")


def test_a_missing_chain_state_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    pass_a.path("index/000001.open.json").unlink()
    _assert_stopped(pass_a.check(), CONDITION_X4, "chain-state-absent")


def test_a_forged_final_state_with_a_record_gap_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path, acts=3, unadmitted=False)

    def gap(document) -> None:  # type: ignore[no-untyped-def]
        document["records"] = [document["records"][0], document["records"][2]]
        document["state_number"] = 3

    pass_a.forge_final(gap)
    _assert_stopped(pass_a.check(), CONDITION_X4, "final-state-invalid")


def test_a_forged_final_state_that_disagrees_with_its_chain_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path, acts=2, unadmitted=False)
    pass_a.forge_final(lambda document: document["records"].pop())
    result = pass_a.check()
    _assert_stopped(result, CONDITION_X4)
    assert result.reason in ("final-state-invalid", "chain-broken", "chain-inconsistent")


@pytest.mark.parametrize(
    "target, action, reason",
    [
        ("records/000001.json", "delete", "record-absent"),
        ("records/000001.json", "change", "record-digest-mismatch"),
        ("streams/stdout/000001", "delete", "stream-absent"),
        ("streams/stderr/000001", "change", "stream-digest-mismatch"),
    ],
)
def test_a_missing_or_changed_record_or_stream_stops(tmp_path: Path, target, action, reason) -> None:  # type: ignore[no-untyped-def]
    pass_a = PassA(tmp_path)
    path = pass_a.path(target)
    if action == "delete":
        path.unlink()
    else:
        data = path.read_bytes()
        path.write_bytes(data[:-1] + (b"X" if data[-1:] != b"X" else b"Y") if data else b"Z")
    _assert_stopped(pass_a.check(), CONDITION_X4, reason)


def test_an_unexpected_published_record_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    pass_a.path("records/000009.json").write_bytes(pass_a.path("records/000001.json").read_bytes())
    result = pass_a.check()
    _assert_stopped(result, CONDITION_X4, "published-record-not-accounted")
    assert result.observed_not_recorded == ("records/000009.json",)


# ===========================================================================
# Condition 5 — the bidirectional name and type comparison
# ===========================================================================


@pytest.mark.parametrize(
    "extra, is_directory",
    [
        ("stray", False),
        ("index/stray", False),
        ("streams/stdout/stray", False),
        ("streams/extra-directory", True),
        ("streams/stdout/nested", True),
    ],
)
def test_an_observed_name_not_recorded_stops_at_any_depth(tmp_path: Path, extra: str, is_directory: bool) -> None:
    pass_a = PassA(tmp_path)
    path = pass_a.path(extra)
    path.mkdir() if is_directory else path.write_bytes(b"")
    before = tree(pass_a.root)
    result = pass_a.check()
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "name-sets-disagree")
    assert result.observed_not_recorded == (extra,)
    assert result.recorded_not_observed == ()
    assert tree(pass_a.root) == before


def test_a_name_nested_inside_an_unexpected_directory_is_reported_by_its_full_path(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    deep = pass_a.path("streams/stdout/a/b")
    deep.mkdir(parents=True)
    (deep / "c").write_bytes(b"")
    result = pass_a.check()
    assert result.observed_not_recorded == (
        "streams/stdout/a",
        "streams/stdout/a/b",
        "streams/stdout/a/b/c",
    )


@pytest.mark.parametrize("name", UNADMITTED)
def test_a_deleted_unadmitted_object_stops(tmp_path: Path, name: str) -> None:
    pass_a = PassA(tmp_path)
    pass_a.path(name).unlink()
    result = pass_a.check()
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "name-sets-disagree")
    assert result.recorded_not_observed == (name,)
    assert result.observed_not_recorded == ()


def test_a_replaced_unadmitted_object_of_the_same_type_passes_and_is_not_read(tmp_path: Path) -> None:
    """The evidentiary limit, exercised: presence, name and type — not content."""
    pass_a = PassA(tmp_path)
    target = pass_a.path(UNADMITTED[0])
    target.unlink()
    target.write_bytes(b"entirely different bytes")
    target.chmod(0o600)
    recording = RecordingReadOnlyFilesystem()
    result = pass_a.check(filesystem=recording)
    assert result.passed
    assert "not established" in result.evidentiary_limit
    assert b"000002" not in recording.opened_files


def test_a_deleted_recorded_subdirectory_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path, acts=0, unadmitted=False)
    os.rmdir(pass_a.path("streams/stderr"))
    result = pass_a.check()
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "name-sets-disagree")
    assert result.recorded_not_observed == ("streams/stderr",)


def _replace(path: Path, kind: str, outside: Path) -> None:
    path.unlink() if path.is_file() or path.is_symlink() else path.rmdir()
    if kind == "directory":
        path.mkdir()
    elif kind == "symlink":
        path.symlink_to(outside)
    elif kind == "fifo":
        os.mkfifo(path)
    elif kind == "regular":
        path.write_bytes(b"")


@pytest.mark.parametrize(
    "name, kind, expected, observed",
    [
        (UNADMITTED[0], "directory", "regular", "directory"),
        (UNADMITTED[0], "symlink", "regular", "symlink"),
        (UNADMITTED[1], "fifo", "regular", "fifo"),
        ("records/000001.json", "symlink", "regular", "symlink"),
    ],
)
def test_every_type_mismatch_stops_and_nothing_is_followed(tmp_path: Path, name, kind, expected, observed) -> None:  # type: ignore[no-untyped-def]
    pass_a = PassA(tmp_path)
    outside = tmp_path / "outside-the-root"
    outside.write_bytes(pass_a.path("records/000001.json").read_bytes() if name.startswith("records") else b"x")
    _replace(pass_a.path(name), kind, outside)
    recording = RecordingReadOnlyFilesystem()
    result = pass_a.check(filesystem=recording)
    if name.startswith("records"):
        # An admitted record replaced by a link is refused at X-4 before the
        # comparison: it is not a regular file, so it is never opened.
        _assert_stopped(result, CONDITION_X4, "admitted-object-absent-or-not-regular")
    else:
        _assert_stopped(result, CONDITION_NAME_AGREEMENT, "name-sets-disagree")
        assert result.type_mismatches == (f"{name}: expected {expected}, observed {observed}",)
    # Nothing was followed: neither the replaced name nor the link's target
    # was ever opened.
    assert name.rpartition("/")[2].encode() not in recording.opened_files
    assert b"outside-the-root" not in recording.opened_files


def test_an_empty_recorded_subdirectory_replaced_by_a_file_is_a_type_mismatch(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path, acts=0, unadmitted=False)
    _replace(pass_a.path("streams/stdout"), "regular", tmp_path)
    result = pass_a.check()
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "name-sets-disagree")
    assert result.type_mismatches == ("streams/stdout: expected directory, observed regular",)


def test_an_unsupported_object_type_is_never_accounted(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    os.mkfifo(pass_a.path("index/pipe"))
    result = pass_a.check()
    assert result.observed_not_recorded == ("index/pipe",)


def test_a_duplicate_category_in_a_forged_final_state_stops(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)

    def duplicate(document) -> None:  # type: ignore[no-untyped-def]
        document["unadmitted"] = sorted(
            document["unadmitted"] + [{"name": "records/000001.json", "type": "regular"}],
            key=lambda item: item["name"],
        )

    pass_a.forge_final(duplicate)
    _assert_stopped(pass_a.check(), CONDITION_NAME_AGREEMENT, "duplicate-accounted-name")


@pytest.mark.parametrize("hostile", ["../escape", "/abs", "streams/stdout/../x", "records/000001.JSON"])
def test_a_traversing_or_non_canonical_recorded_name_is_refused(tmp_path: Path, hostile: str) -> None:
    pass_a = PassA(tmp_path)

    def inject(document) -> None:  # type: ignore[no-untyped-def]
        document["unadmitted"] = sorted(
            document["unadmitted"] + [{"name": hostile, "type": "regular"}], key=lambda item: item["name"]
        )

    pass_a.forge_final(inject)
    _assert_stopped(pass_a.check(), CONDITION_X4, "final-state-invalid")


def test_names_are_compared_as_raw_bytes_without_normalization(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    directory = os.open(pass_a.path("index"), os.O_RDONLY | os.O_DIRECTORY)
    try:
        for raw in (b"\xff.json", "é".encode(), "é".encode(), b"000001.OPEN.json"):
            fd = os.open(raw, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=directory)
            os.close(fd)
    finally:
        os.close(directory)
    result = pass_a.check()
    assert set(result.observed_not_recorded) == {
        "index/\\xff.json",
        "index/\\xc3\\xa9",
        "index/e\\xcc\\x81",
        "index/000001.OPEN.json",
    }


def test_a_symbolic_link_to_an_admitted_object_is_an_unexpected_name(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    pass_a.path("records/alias.json").symlink_to(pass_a.path("records/000001.json"))
    recording = RecordingReadOnlyFilesystem()
    result = pass_a.check(filesystem=recording)
    assert result.observed_not_recorded == ("records/alias.json",)
    assert b"alias.json" not in recording.opened_files


@pytest.mark.parametrize(
    "existing, alias",
    [
        ("streams/stdout/000001", "streams/stdout/000009"),
        ("records/000001.json", "index/000009.open.json"),
        (UNADMITTED[0], "stray"),
    ],
)
def test_a_hard_link_alias_stops(tmp_path: Path, existing: str, alias: str) -> None:
    pass_a = PassA(tmp_path)
    os.link(pass_a.path(existing), pass_a.path(alias))
    _assert_stopped(pass_a.check(), CONDITION_NAME_AGREEMENT, "path-alias")


class _Twisted(PosixReadOnlyFilesystem):
    """A read-only filesystem whose answers are made hostile on purpose."""

    def __init__(self, *, listing=None, device_of=None, fail_listing_of=None) -> None:  # type: ignore[no-untyped-def]
        self._listing = listing
        self._device_of = device_of
        self._fail_listing_of = fail_listing_of
        self._lists = 0

    def list_names(self, dir_fd):  # type: ignore[no-untyped-def]
        self._lists += 1
        names = super().list_names(dir_fd)
        if self._fail_listing_of == self._lists:
            raise OSError("injected incomplete listing")
        return self._listing(names) if self._listing else names

    def lstat_at(self, dir_fd, name):  # type: ignore[no-untyped-def]
        facts = super().lstat_at(dir_fd, name)
        if self._device_of is not None and name == self._device_of:
            values = list(facts)
            values[2] = facts.st_dev + 1
            return os.stat_result(values)
        return facts


@pytest.mark.parametrize(
    "listing",
    [
        lambda names: names + names[:1],
        lambda names: names + (b"..",),
        lambda names: names + (b"a/b",),
        lambda names: names + (b"",),
    ],
)
def test_an_ambiguous_listing_stops(tmp_path: Path, listing) -> None:  # type: ignore[no-untyped-def]
    pass_a = PassA(tmp_path)
    _assert_stopped(pass_a.check(filesystem=_Twisted(listing=listing)), CONDITION_NAME_AGREEMENT, "ambiguous-name")


def test_an_entry_on_another_device_escapes_the_root(tmp_path: Path) -> None:
    pass_a = PassA(tmp_path)
    result = pass_a.check(filesystem=_Twisted(device_of=b"records"))
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "escapes-the-root")


@pytest.mark.parametrize("which", [1, 2, 4])
def test_an_incomplete_enumeration_stops(tmp_path: Path, which: int) -> None:
    pass_a = PassA(tmp_path)
    result = pass_a.check(filesystem=_Twisted(fail_listing_of=which))
    assert not result.passed
    assert result.reason.startswith("verification-incomplete")


# ===========================================================================
# Races: change during enumeration and verification fails closed
# ===========================================================================


def _race(tmp_path: Path, trigger: str, count: int, mutate) -> object:  # type: ignore[no-untyped-def]
    pass_a = PassA(tmp_path)
    fired = []

    def hook(method: str, seen: int, arguments: tuple) -> None:
        if method == trigger and seen == count and not fired:
            fired.append(arguments)
            mutate(pass_a)

    result = pass_a.check(filesystem=RecordingReadOnlyFilesystem(hook=hook))
    assert fired, "the race was never triggered"
    return result


def test_a_name_added_while_the_root_is_listed_stops(tmp_path: Path) -> None:
    result = _race(tmp_path, "list_names", 1, lambda p: p.path("late").write_bytes(b""))
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "changed-during-enumeration")


def test_a_directory_swapped_between_lstat_and_open_stops(tmp_path: Path) -> None:
    def swap(p) -> None:  # type: ignore[no-untyped-def]
        os.rename(p.path("records"), p.path("records-old"))
        p.path("records").mkdir(mode=0o700)

    pass_a = PassA(tmp_path)
    fired = []

    def hook(method: str, seen: int, arguments: tuple) -> None:
        if method == "open_directory" and arguments == (b"records",) and not fired:
            fired.append(True)
            swap(pass_a)

    result = pass_a.check(filesystem=RecordingReadOnlyFilesystem(hook=hook))
    assert fired
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "changed-during-enumeration")


def test_an_admitted_file_replaced_after_enumeration_stops(tmp_path: Path) -> None:
    def replace(p) -> None:  # type: ignore[no-untyped-def]
        target = p.path("streams/stdout/000001")
        data = target.read_bytes()
        target.unlink()
        target.write_bytes(data)
        target.chmod(0o600)

    result = _race(tmp_path, "open_file", 1, replace)
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "changed-during-verification")


def test_an_admitted_file_appended_to_while_it_is_read_stops(tmp_path: Path) -> None:
    def append(p) -> None:  # type: ignore[no-untyped-def]
        with open(p.path(p.binding.final_state), "ab") as handle:
            handle.write(b"x")

    result = _race(tmp_path, "read_all", 1, append)
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "changed-during-verification")


def test_a_name_added_after_every_digest_is_caught_by_the_second_enumeration(tmp_path: Path) -> None:
    """Six admitted objects are read — F, I-1, I-0, record 1 and its two
    streams. The listing that follows the sixth read is the second
    enumeration's first; the tree is changed immediately before it."""
    pass_a = PassA(tmp_path)
    reads: list[int] = []
    added: list[bool] = []

    def hook(method: str, seen: int, arguments: tuple) -> None:
        if method == "read_all":
            reads.append(seen)
        if method == "list_names" and len(reads) == 6 and not added:
            added.append(True)
            (pass_a.path("streams/stdout") / "late").write_bytes(b"")

    result = pass_a.check(filesystem=RecordingReadOnlyFilesystem(hook=hook))
    assert added
    _assert_stopped(result, CONDITION_NAME_AGREEMENT)
    assert result.reason in ("changed-during-verification", "changed-during-enumeration")


def test_a_root_replaced_during_verification_stops(tmp_path: Path) -> None:
    def move(p) -> None:  # type: ignore[no-untyped-def]
        os.rename(p.root, p.root + "-moved")
        Path(p.root).mkdir(mode=0o700)

    result = _race(tmp_path, "read_all", 6, move)
    _assert_stopped(result, CONDITION_PRESENCE, "root-replaced-during-verification")


def test_a_hard_link_from_outside_the_root_is_an_alias(tmp_path: Path) -> None:
    """Only one name is inside the root, so the alias shows only as a link count."""
    pass_a = PassA(tmp_path)
    os.link(pass_a.path("streams/stdout/000001"), tmp_path / "outside-alias")
    _assert_stopped(pass_a.check(), CONDITION_NAME_AGREEMENT, "path-alias")


def test_a_same_size_rewrite_while_an_admitted_file_is_read_stops(tmp_path: Path) -> None:
    """The size does not move, so only the before/after identity comparison
    sees it: reported as a change, not mistaken for a stale digest."""

    def rewrite(p) -> None:  # type: ignore[no-untyped-def]
        path = p.path(p.binding.final_state)
        data = path.read_bytes()
        with open(path, "r+b") as handle:
            handle.write(b"X" if data[:1] != b"X" else b"Y")

    result = _race(tmp_path, "read_all", 1, rewrite)
    _assert_stopped(result, CONDITION_NAME_AGREEMENT, "changed-during-verification")
