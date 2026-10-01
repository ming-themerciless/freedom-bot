"""RP-11, C-P5.0-R5-RP11-I1 and I1-R3 — the capture mechanism, against §9.5 of
the operational-evidence draft as amended by C-P5.0-R5-RP11-I1-R3 (proposed,
unaccepted; the accepted R5 bytes `5e06a388…` remain the baseline).

What is asserted, and how:

* **C-1 … C-5, P-1 … P-4.** Real launches of the current interpreter with inert
  inline programs: the exact vector, raw non-UTF-8 bytes, empty streams,
  interleaving, non-zero exit, a terminating signal, the bound, a start failure,
  an incomplete channel, and the absence of any shell.
* **C-6, C-7, X-1.** Exclusive root creation under a temporary "host", the
  modes, the fixed layout, the genesis state, the forbidden locations by name
  and by identity, symbolic-link ancestors, and independent Pass A / Pass B
  roots.
* **P-5 … P-8, X-2, X-3.** The retained-alias publication — an exclusive
  staging name, one no-follow exclusive link to the final name, both names
  retained on one inode with link count two — gap-free sequence numbers and an
  intact chain; then **every labelled stage** of an act and of X-3 failed in
  turn, and interrupted in turn, asserting the externally visible result: no
  retry of the stage, no next command, no repair or clean-up, the exact
  publication state, the exact unadmitted set *F* records, X-4, and a root
  B0-RA still admits.

Every assertion is about the files on disk or the calls made, not about a mock
having been called.
"""
from __future__ import annotations

import ast
import errno
import hashlib
import os
import stat
from pathlib import Path

import pytest

from tests.phase_5_0_evidence.rp11_fixtures import (
    INERT_ENVIRONMENT,
    PASS_A,
    PASS_B,
    TOOL_SHA256,
    CountingLauncher,
    FaultFilesystem,
    FixedClock,
    Host,
    ScriptedLauncher,
    act,
    names_under,
    open_session,
    python_argv,
    release_suite_descriptors,
    rp11_release_descriptors,  # noqa: F401 - autouse fixture, active by import
    tree,
    write_handback,
    writes,
)
from tools.phase_5_0_evidence import capture_contract as contract
from tools.phase_5_0_evidence.capture_contract import (
    RP11_SOURCES,
    CaptureContractRefused,
    CaptureRecord,
    HandbackBinding,
    IndexEntry,
    IndexState,
    ObjectType,
    RelativeName,
    SelfPublication,
    StateLink,
    Terminal,
    UnadmittedObject,
    accounted_objects,
    canonical_bytes,
    capture_tool_sha256,
    parse_canonical,
    parse_capture_root,
    parse_handback_binding,
    roots_overlap,
)
from tools.phase_5_0_evidence.execution import capture_mechanism as mechanism_module
from tools.phase_5_0_evidence.execution import descriptors
from tools.phase_5_0_evidence.execution.boundary import (
    CAPTURE_ARGV_REFUSED,
    CAPTURE_NOT_ARMED,
    CAPTURE_START_FAILED,
    StreamCaptureLauncher,
)
from tools.phase_5_0_evidence.execution.capture_mechanism import (
    ACT_STAGES,
    LAUNCH_STAGE,
    REQUEST_STAGE,
    CaptureRefused,
    SessionState,
)
from tools.phase_5_0_evidence.execution.capture_store import (
    ADVANCE_STAGES,
    CaptureInterrupted,
    FINAL_STAGES,
    GENESIS_STAGES,
    RECORD_STAGES,
    PosixCaptureFilesystem,
    PublicationState,
)
from tools.phase_5_0_evidence.execution.retention_check import RetentionCheck
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES

REPOSITORY = Path(__file__).resolve().parents[2]
LAYOUT = {"index", "records", "streams", "streams/stdout", "streams/stderr"}


def _read(root: str, name: str) -> bytes:
    return (Path(root) / name).read_bytes()


def _final(root: str) -> tuple[str, IndexState]:
    finals = sorted(p for p in os.listdir(Path(root) / "index") if p.endswith(".final.json"))
    assert len(finals) == 1, finals
    name = f"index/{finals[0]}"
    return name, IndexState.from_bytes(_read(root, name))


def _b0_ra(tmp_path: Path, session, root: str) -> object:
    handback = tmp_path / "pass-a-handback.md"
    digest = write_handback(handback, session)
    return RetentionCheck(
        handback_path=str(handback),
        handback_sha256=digest,
        capture_root=root,
        expected_pass_id=PASS_A,
    ).run()


# ===========================================================================
# The contract: names, encodings, the binding
# ===========================================================================


def test_canonical_documents_have_exactly_one_accepted_encoding() -> None:
    document = {"b": 1, "a": ["x", None], "c": "é"}
    data = canonical_bytes(document)
    assert data == b'{"a":["x",null],"b":1,"c":"\\u00e9"}\n'
    assert parse_canonical(data) == document
    for variant, classification in (
        (b'{"b":1, "a":["x",null],"c":"\\u00e9"}\n', "non-canonical-document"),
        (b'{"b":1,"a":["x",null],"c":"\\u00e9"}\n', "non-canonical-document"),
        (b'{"a":1,"a":2}\n', "duplicate-key"),
        (b'{"a":1.5}\n', "malformed-document"),
        (b'{"a":NaN}\n', "malformed-document"),
        (b'{"a":1}', "malformed-document"),
        (b'{"a":1}\n{"a":1}\n', "malformed-document"),
        ('{"c":"é"}\n'.encode("utf-8"), "malformed-document"),
    ):
        with pytest.raises(CaptureContractRefused) as refusal:
            parse_canonical(variant)
        assert refusal.value.classification == classification, variant


@pytest.mark.parametrize(
    "components",
    [(b"",), (b".",), (b"..",), (b"a/b",), (b"a\0",), (b"index", b"..", b"x"), ()],
)
def test_a_relative_name_refuses_every_ambiguous_component(components) -> None:
    with pytest.raises(CaptureContractRefused):
        RelativeName(components)


@pytest.mark.parametrize(
    "text",
    ["/index", "index/", "index//x", "./index", "index/../x", "INDEX", "index/é", "a\\b", ""],
)
def test_a_created_name_has_one_spelling(text: str) -> None:
    with pytest.raises(CaptureContractRefused):
        RelativeName.created(text)


def test_the_display_form_is_injective_over_raw_bytes() -> None:
    names = [
        RelativeName((b"aA",)),
        RelativeName((b"a\\x41",)),
        RelativeName((b"a\xc3\xa9",)),
        RelativeName((b"ae\xcc\x81",)),
        RelativeName((b"a b",)),
        RelativeName((b"a", b"b")),
    ]
    displays = [name.display for name in names]
    assert len(set(displays)) == len(displays)
    assert RelativeName((b"a\xff",)).display == "a\\xff"
    assert RelativeName((b"a b",)).display == "a\\x20b"


@pytest.mark.parametrize(
    "root",
    ["relative/x", "/", "/x/", "//x", "/x//y", "/x/./y", "/x/../y", "/x/.hidden", "/x/a b", "/x/a\0b", "/x/é"],
)
def test_a_capture_root_is_absolute_and_unnormalized(root: str) -> None:
    with pytest.raises(CaptureContractRefused):
        parse_capture_root(root)


def test_roots_overlap_when_equal_or_nested_in_either_direction() -> None:
    assert roots_overlap("/c/a", "/c/a")
    assert roots_overlap("/c/a", "/c/a/b")
    assert roots_overlap("/c/a/b", "/c/a")
    assert not roots_overlap("/c/a", "/c/ab")
    assert not roots_overlap("/c/a", "/c/b")


def test_the_binding_block_round_trips_and_nothing_else_is_read() -> None:
    binding = HandbackBinding(
        pass_id=PASS_A,
        capture_root="/srv/capture/a",
        x3_outcome="succeeded",
        x4_validity="valid",
        final_state="index/000003.final.json",
        capture_index_sha256="c" * 64,
    )
    text = "# prose\ncapture_root: /somewhere/else\n\n" + binding.render() + "\nmore prose\n"
    assert parse_handback_binding(text.encode()) == binding


@pytest.mark.parametrize(
    "mutation, classification",
    [
        (lambda block: "no block here\n", "binding-absent"),
        (lambda block: block + "\n" + block, "binding-ambiguous"),
        (lambda block: "  " + block, "binding-ambiguous"),
        (lambda block: block.replace("x3_outcome: succeeded\nx4_validity: valid", "x4_validity: valid\nx3_outcome: succeeded"), "malformed-binding"),
        (lambda block: block.replace("x4_validity: valid", "x4_validity: valid "), "malformed-binding"),
        (lambda block: block.replace("x4_validity: valid", "x4_validity:  valid"), "malformed-binding"),
        (lambda block: block.replace("\n```\n", "\n"), "malformed-binding"),
        (lambda block: block.replace("rp11-capture-binding/1", "rp11-capture-binding/2"), "malformed-binding"),
        (lambda block: block.replace("x3_outcome: succeeded", "x3_outcome: ok"), "malformed-binding"),
        (lambda block: block.replace("/srv/capture/a", "/srv/capture/a/"), "malformed-root"),
    ],
)
def test_the_binding_block_refuses_every_other_shape(mutation, classification) -> None:
    block = HandbackBinding(
        pass_id=PASS_A,
        capture_root="/srv/capture/a",
        x3_outcome="succeeded",
        x4_validity="valid",
        final_state="index/000003.final.json",
        capture_index_sha256="c" * 64,
    ).render()
    with pytest.raises(CaptureContractRefused) as refusal:
        parse_handback_binding(mutation(block).encode())
    assert refusal.value.classification == classification


def _entry(seq: int) -> IndexEntry:
    name = contract.record_name(seq)
    return IndexEntry(seq, name, name + ".staging", "d" * 64, 1, 100 + seq)


def _link(number: int) -> StateLink:
    name = contract.open_state_name(number)
    return StateLink(name, name + ".staging", "e" * 64, 1, 200 + number)


def _self(number: int) -> SelfPublication:
    name = contract.final_state_name(number)
    return SelfPublication(name, name + ".staging", 1, 300 + number)


def _open(number: int, records: tuple[IndexEntry, ...]) -> IndexState:
    return IndexState(
        pass_id=PASS_A,
        capture_root="/c/a",
        tool_sha256=TOOL_SHA256,
        owner_uid=1000,
        state_number=number,
        previous=None if number == 0 else _link(number - 1),
        status="open",
        records=records,
    )


def test_an_index_state_refuses_a_gap_and_a_final_state_its_own_shape() -> None:
    with pytest.raises(CaptureContractRefused) as refusal:
        IndexState(PASS_A, "/c/a", TOOL_SHA256, 1000, 2, _link(1), "open", (_entry(1), _entry(3)))
    assert refusal.value.classification == "record-list-gap"
    base = dict(
        pass_id=PASS_A,
        capture_root="/c/a",
        tool_sha256=TOOL_SHA256,
        owner_uid=1000,
        state_number=2,
        previous=_link(1),
        status="final",
        records=(_entry(1),),
        terminal=Terminal("completed"),
        subdirectories=tuple(sorted(LAYOUT)),
        unadmitted=(),
        publication=_self(2),
    )
    state = IndexState(**base)  # the valid shape
    assert IndexState.from_bytes(state.to_bytes()) == state
    with pytest.raises(CaptureContractRefused):
        IndexState(**{**base, "subdirectories": ("index",)})
    with pytest.raises(CaptureContractRefused):
        IndexState(**{**base, "state_number": 3})
    for broken in ({"publication": None}, {"publication": _self(3)}, {"previous": _link(0)}):
        with pytest.raises(CaptureContractRefused):
            IndexState(**{**base, **broken})
    with pytest.raises(CaptureContractRefused):
        UnadmittedObject("records/000002.json", ObjectType.DIRECTORY)
    with pytest.raises(CaptureContractRefused):
        UnadmittedObject("index/000002.final.json", ObjectType.REGULAR)
    with pytest.raises(CaptureContractRefused):
        UnadmittedObject("../escape", ObjectType.REGULAR)


def test_a_name_in_two_categories_is_refused_when_r_is_formed() -> None:
    record = CaptureRecord(
        pass_id=PASS_A,
        capture_seq=1,
        step_or_case_id="A1-01",
        argv=("/bin/true",),
        clock_source="c",
        started_utc="2026-09-27T12:00:00.000001Z",
        ended_utc="2026-09-27T12:00:00.000002Z",
        exit=contract.ExitOutcome("status", 0),
        stream_bound_bytes=10,
        stdout=contract.StreamBinding("streams/stdout/000001", "0" * 64, 0),
        stderr=contract.StreamBinding("streams/stderr/000001", "0" * 64, 0),
    )
    chain = [_open(0, ()), _open(1, (_entry(1),))]
    for reused in ("records/000001.json", "records/000001.json.staging", "index/000000.open.json.staging"):
        final = IndexState(
            PASS_A, "/c/a", TOOL_SHA256, 1000, 2, _link(1), "final", (_entry(1),),
            Terminal("completed"), tuple(sorted(LAYOUT)),
            (UnadmittedObject(reused, ObjectType.REGULAR),), _self(2),
        )
        with pytest.raises(CaptureContractRefused) as refusal:
            accounted_objects(final, chain, [record])
        assert refusal.value.classification == "duplicate-accounted-name", reused


def test_a_staging_name_is_fixed_by_rule_and_names_only_its_own_object() -> None:
    assert contract.staging_name("records/000007.json") == "records/000007.json.staging"
    assert contract.staging_name("index/000000.open.json") == "index/000000.open.json.staging"
    assert contract.staging_name("index/000003.final.json") == "index/000003.final.json.staging"
    for text in ("streams/stdout/000001", "records/000001.json.staging", "index", "stray"):
        with pytest.raises(CaptureContractRefused):
            contract.staging_name(text)
    assert contract.role_of("records/000007.json") == ("final", "records/000007.json.staging")
    assert contract.role_of("records/000007.json.staging") == ("staging", "records/000007.json")
    assert contract.role_of("streams/stdout/000007") == ("single", None)
    assert contract.role_of("records/000007.json.staging.staging") == ("single", None)
    with pytest.raises(CaptureContractRefused) as refusal:
        IndexEntry(1, "records/000001.json", "records/000002.json.staging", "d" * 64, 1, 1)
    assert refusal.value.classification == "pair-mismatch"
    # A staging name is unadmittable only for a record or an open state.
    UnadmittedObject("records/000001.json.staging", ObjectType.REGULAR)
    UnadmittedObject("index/000000.open.json.staging", ObjectType.REGULAR)
    with pytest.raises(CaptureContractRefused):
        UnadmittedObject("index/000002.final.json.staging", ObjectType.REGULAR)


def test_the_tool_digest_covers_exactly_the_rp11_sources() -> None:
    sources = {name: (REPOSITORY / name).read_bytes() for name in RP11_SOURCES}
    first = capture_tool_sha256(sources)
    assert first == capture_tool_sha256(dict(sources))
    edited = dict(sources)
    edited[RP11_SOURCES[0]] += b"#"
    assert capture_tool_sha256(edited) != first
    with pytest.raises(CaptureContractRefused):
        capture_tool_sha256({name: b"" for name in RP11_SOURCES[1:]})
    assert set(RP11_SOURCES) <= set(COVERED_SOURCES)


# ===========================================================================
# The launcher: one exact vector, no shell, two raw channels
# ===========================================================================


def test_exact_argv_and_separate_raw_streams_are_captured(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    launcher = CountingLauncher()
    session = open_session(host, launcher=launcher)
    out = b"\xff\xfe\x00not utf-8\r\n\x80"
    err = b"\x00\x01stderr\xc3"
    argv = writes(out, err, 7)
    outcome = session.run_act(act("A1-01", argv))
    assert outcome.admitted and outcome.exit == contract.ExitOutcome("status", 7)
    assert launcher.calls == [argv]
    root = host.root()
    assert _read(root, "streams/stdout/000001") == out
    assert _read(root, "streams/stderr/000001") == err
    record = CaptureRecord.from_bytes(_read(root, "records/000001.json"))
    assert record.argv == argv
    assert record.stdout.sha256 == hashlib.sha256(out).hexdigest()
    assert record.stderr.sha256 == hashlib.sha256(err).hexdigest()
    assert (record.stdout.size, record.stderr.size) == (len(out), len(err))
    assert record.as_document()["shell"] == "none"
    assert record.clock_source == FixedClock.source
    assert record.started_utc < record.ended_utc


def test_empty_streams_are_stream_files_with_the_empty_digest(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    assert session.run_act(act("A1-02", writes(b"", b""))).admitted
    record = CaptureRecord.from_bytes(_read(host.root(), "records/000001.json"))
    empty = hashlib.sha256(b"").hexdigest()
    assert (record.stdout.sha256, record.stderr.sha256) == (empty, empty)
    assert (record.stdout.size, record.stderr.size) == (0, 0)
    assert _read(host.root(), "streams/stdout/000001") == b""


def test_interleaved_writes_stay_in_their_own_channel(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    program = (
        "import sys\n"
        "for i in range(200):\n"
        "    sys.stdout.buffer.write(b'O%03d' % i); sys.stdout.flush()\n"
        "    sys.stderr.buffer.write(b'E%03d' % i); sys.stderr.flush()\n"
    )
    assert session.run_act(act("A1-03", python_argv(program), bound=10_000)).admitted
    assert _read(host.root(), "streams/stdout/000001") == b"".join(b"O%03d" % i for i in range(200))
    assert _read(host.root(), "streams/stderr/000001") == b"".join(b"E%03d" % i for i in range(200))


def test_a_terminating_signal_is_recorded_as_a_signal(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    outcome = session.run_act(act("A1-04", python_argv("import os; os.kill(os.getpid(), 9)")))
    assert outcome.admitted
    assert outcome.exit == contract.ExitOutcome("signal", 9)


def test_no_shell_interprets_any_element(tmp_path: Path) -> None:
    """Metacharacters reach the child as literal bytes; nothing is expanded."""
    host = Host.under(tmp_path)
    marker = tmp_path / "shell-ran"
    hostile = f"; touch {marker} && echo $HOME `id` $(id) > {marker} | cat *"
    session = open_session(host, launcher=CountingLauncher())
    program = "import sys; sys.stdout.buffer.write(sys.argv[1].encode())"
    assert session.run_act(act("A1-05", python_argv(program, hostile))).admitted
    assert _read(host.root(), "streams/stdout/000001") == hostile.encode()
    assert not marker.exists()


def test_the_environment_is_exactly_the_one_supplied(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    program = "import sys; sys.stdout.buffer.write(open('/proc/self/environ', 'rb').read())"
    assert session.run_act(act("A1-06", python_argv(program))).admitted
    block = _read(host.root(), "streams/stdout/000001")
    assert sorted(block.split(b"\0")[:-1]) == sorted(
        f"{key}={value}".encode() for key, value in INERT_ENVIRONMENT.items()
    )


def test_the_launcher_is_unarmed_by_default_and_refuses_a_relative_vector() -> None:
    sink = []

    class Sink:
        def write(self, data: bytes) -> None:
            sink.append(data)

    result = StreamCaptureLauncher().launch(
        ("/bin/true",), environment={}, stdout=Sink(), stderr=Sink(), stream_bound_bytes=1
    )
    assert (result.started, result.failure) == (False, CAPTURE_NOT_ARMED)
    for argv in (("true",), (), ("/bin/true", "a\0b")):
        result = StreamCaptureLauncher(armed=True).launch(
            argv, environment={}, stdout=Sink(), stderr=Sink(), stream_bound_bytes=1
        )
        assert (result.started, result.failure) == (False, CAPTURE_ARGV_REFUSED)
    assert sink == []


def test_exceeding_a_bound_stops_the_pass_without_truncating(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    launcher = CountingLauncher()
    session = open_session(host, launcher=launcher)
    payload = b"x" * 5000
    outcome = session.run_act(act("A1-07", writes(payload, b""), bound=1000))
    assert not outcome.admitted
    assert (outcome.failure.stage, outcome.failure.classification) == (LAUNCH_STAGE, "stream-bound-exceeded")
    assert outcome.failure.host_act_may_have_run
    retained = _read(host.root(), "streams/stdout/000001")
    assert len(retained) > 1000 and payload.startswith(retained)
    _, final = _final(host.root())
    assert final.records == ()
    assert {item.name for item in final.unadmitted} == {"streams/stdout/000001", "streams/stderr/000001"}
    with pytest.raises(CaptureRefused):
        session.run_act(act("A1-08", writes(b"", b"")))
    assert len(launcher.calls) == 1


def test_a_start_failure_is_inconclusive_and_nothing_ran(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    outcome = session.run_act(act("A1-09", (str(tmp_path / "no-such-program"),)))
    assert (outcome.failure.stage, outcome.failure.classification) == (LAUNCH_STAGE, CAPTURE_START_FAILED)
    assert not outcome.failure.host_act_may_have_run
    assert outcome.stop.x3_outcome == "succeeded" and outcome.stop.x4_validity == "valid"
    assert {item.name for item in outcome.stop.unadmitted} == {
        "streams/stdout/000001",
        "streams/stderr/000001",
    }


def test_a_channel_held_open_past_the_drain_limit_is_an_incomplete_stream(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    program = (
        "import os, sys, time\n"
        "if os.fork() == 0:\n"
        "    time.sleep(1.5); os._exit(0)\n"
        "sys.stdout.buffer.write(b'parent'); sys.stdout.flush()\n"
    )
    outcome = session.run_act(act("A1-10", python_argv(program), drain=0.2))
    assert (outcome.failure.stage, outcome.failure.classification) == (LAUNCH_STAGE, "stream-incomplete")
    assert outcome.failure.host_act_may_have_run


def test_a_malformed_request_stops_the_pass_before_any_file_or_process(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    launcher = CountingLauncher()
    session = open_session(host, launcher=launcher)
    before = names_under(host.root())
    outcome = session.run_act(act("A1-11", ("relative",)))
    assert (outcome.failure.stage, outcome.failure.classification) == (REQUEST_STAGE, "request-malformed-argv")
    assert launcher.calls == []
    after = names_under(host.root())
    assert after - before == {outcome.stop.final_state, outcome.stop.final_state + ".staging"}


# ===========================================================================
# X-1: the root, its subdirectories and the genesis state
# ===========================================================================


def test_the_root_is_created_exclusively_with_the_fixed_layout_and_modes(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host)
    assert session.state is SessionState.OPEN
    root = host.root()
    facts = tree(root)
    assert set(facts) == LAYOUT | {"index/000000.open.json", "index/000000.open.json.staging"}
    assert stat.S_IMODE(os.lstat(root).st_mode) == 0o700
    for name in LAYOUT:
        assert facts[name][0] == stat.S_IFDIR and facts[name][1] == 0o700
    genesis_final = facts["index/000000.open.json"]
    genesis_staging = facts["index/000000.open.json.staging"]
    assert genesis_final == genesis_staging  # one inode, both names retained
    assert genesis_final[1] == 0o600 and genesis_final[3] == 2
    assert session.publication_states == {"index/000000.open.json": PublicationState.VERIFIED}
    genesis = IndexState.from_bytes(_read(root, "index/000000.open.json"))
    assert (genesis.state_number, genesis.previous_state_sha256, genesis.records) == (0, None, ())
    assert (genesis.pass_id, genesis.capture_root, genesis.tool_sha256) == (PASS_A, root, TOOL_SHA256)


def test_an_existing_root_is_refused_and_left_untouched(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    Path(host.root()).mkdir()
    (Path(host.root()) / "earlier").write_bytes(b"not ours")
    before = tree(host.root())
    launcher = ScriptedLauncher()
    session = open_session(host, launcher=launcher)
    assert session.state is SessionState.NO_GENESIS
    assert session.genesis_failure.classification == "object-exists"
    assert tree(host.root()) == before
    with pytest.raises(CaptureRefused):
        session.run_act(act("A1-01", writes(b"", b"")))
    outcome = session.complete()
    assert (outcome.x3_outcome, outcome.x4_validity) == ("not-made", "inconclusive")
    assert session.binding().x3_outcome == "not-made"
    assert launcher.calls == []


@pytest.mark.parametrize("where", ["worktree", "forbidden_tmp"])
def test_a_root_inside_a_forbidden_location_is_refused_before_creation(tmp_path: Path, where: str) -> None:
    host = Host.under(tmp_path)
    forbidden = getattr(host, where)
    root = str(forbidden / "capture-a")
    session = open_session(host, root=root)
    assert session.state is SessionState.NO_GENESIS
    assert session.genesis_failure.classification == "forbidden-location"
    assert not Path(root).exists()


def test_a_forbidden_location_is_also_refused_by_identity(tmp_path: Path) -> None:
    """A differently spelt path to the same directory is still forbidden."""
    host = Host.under(tmp_path)
    parent_facts = os.stat(host.base)
    filesystem = FaultFilesystem(
        stat_path_override=lambda path: parent_facts if path == str(host.worktree) else None
    )
    session = open_session(host, filesystem=filesystem)
    assert session.genesis_failure.classification == "forbidden-location"
    assert not Path(host.root()).exists()


def test_a_symbolic_link_anywhere_on_the_root_path_is_refused(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    real = host.base / "real"
    real.mkdir()
    (host.base / "alias").symlink_to(real)
    session = open_session(host, root=str(host.base / "alias" / "capture-a"))
    assert session.genesis_failure.classification == "open-refused"
    assert list(real.iterdir()) == []


def test_pass_a_and_pass_b_roots_are_independent_and_never_nested(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    a = open_session(host, root=host.root("capture-a"))
    a.run_act(act("A1-01", writes(b"", b"")))
    a.complete()
    before_a = tree(host.root("capture-a"))
    for nested in (host.root("capture-a"), host.root("capture-a") + "/inner"):
        refused = open_session(host, root=nested, pass_id=PASS_B, others=(host.root("capture-a"),))
        assert refused.state is SessionState.NO_GENESIS
        assert refused.genesis_failure.classification == "overlapping-root"
    b = open_session(host, root=host.root("capture-b"), pass_id=PASS_B, others=(host.root("capture-a"),))
    assert b.state is SessionState.OPEN
    genesis_b = IndexState.from_bytes(_read(host.root("capture-b"), "index/000000.open.json"))
    assert genesis_b.previous_state_sha256 is None and genesis_b.pass_id == PASS_B
    b.run_act(act("B1-01", writes(b"", b"")))
    b.complete()
    assert tree(host.root("capture-a")) == before_a


def _x1_stages(tmp_path: Path) -> list[str]:
    host = Host.under(tmp_path / "probe")
    filesystem = FaultFilesystem()
    open_session(host, filesystem=filesystem)
    ordered: list[str] = []
    for stage in filesystem.stages():
        if stage.startswith("X-1") and stage not in ordered:
            ordered.append(stage)
    return ordered


def test_x1_has_the_stages_the_suite_fails(tmp_path: Path) -> None:
    (tmp_path / "probe").mkdir()
    stages = _x1_stages(tmp_path)
    assert "X-1:create-root" in stages and "X-1:root-entry-barrier" in stages
    assert "X-1:subdirectory-entry-barrier" in stages
    assert "X-1:genesis:directory-barrier" in stages
    assert stages.index("X-1:subdirectory-entry-barrier") < stages.index("X-1:genesis:create")


X1_STAGES = (
    "X-1:forbidden-identity",
    "X-1:open-ancestor",
    "X-1:verify-ancestor",
    "X-1:create-root",
    "X-1:verify-root",
    "X-1:root-entry-barrier",
    "X-1:create-subdirectory",
    "X-1:verify-subdirectory",
    "X-1:subdirectory-entry-barrier",
    *GENESIS_STAGES.ordered(),
)


def test_the_suites_x1_stage_list_is_complete(tmp_path: Path) -> None:
    (tmp_path / "probe").mkdir()
    assert set(_x1_stages(tmp_path)) == set(X1_STAGES)


@pytest.mark.parametrize("stage", X1_STAGES)
def test_a_failed_x1_stage_leaves_no_genesis_and_no_x3(tmp_path: Path, stage: str) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem(stage=stage)
    launcher = ScriptedLauncher()
    session = open_session(host, filesystem=filesystem, launcher=launcher)
    assert filesystem.triggered
    assert session.state is SessionState.NO_GENESIS
    assert session.genesis_failure.stage == stage
    assert filesystem.stages().count(stage) == 1
    outcome = session.complete()
    assert outcome.x3_outcome == "not-made"
    assert launcher.calls == []
    if Path(host.root()).exists():
        assert not [n for n in names_under(host.root()) if n.endswith(".final.json")]
    with pytest.raises(CaptureRefused):
        session.complete()


@pytest.mark.parametrize("stage", X1_STAGES)
def test_an_interruption_during_x1_makes_no_further_call(tmp_path: Path, stage: str) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem(stage=stage, mode="interrupt")
    with pytest.raises(CaptureInterrupted):
        open_session(host, filesystem=filesystem)
    assert filesystem.after_interrupt == []


# ===========================================================================
# Acts: gap-free publication and an intact chain
# ===========================================================================


def test_three_acts_publish_a_gap_free_chain_and_a_valid_final_state(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    digests = []
    for index in range(3):
        outcome = session.run_act(act(f"A1-0{index + 1}", writes(b"o%d" % index, b"e%d" % index)))
        assert outcome.admitted and outcome.capture_seq == index + 1
        digests.append(outcome.record_sha256)
    final_outcome = session.complete()
    assert (final_outcome.x3_outcome, final_outcome.x4_validity) == ("succeeded", "valid")
    root = host.root()
    name, final = _final(root)
    assert name == "index/000004.final.json" == final_outcome.final_state
    assert hashlib.sha256(_read(root, name)).hexdigest() == final_outcome.final_state_sha256
    assert [(e.capture_seq, e.name, e.sha256) for e in final.records] == [
        (n + 1, f"records/{n + 1:06d}.json", digests[n]) for n in range(3)
    ]
    previous = final.previous_state_sha256
    for number in (3, 2, 1, 0):
        data = _read(root, f"index/{number:06d}.open.json")
        assert hashlib.sha256(data).hexdigest() == previous
        state = IndexState.from_bytes(data)
        assert state.records == final.records[:number]
        previous = state.previous_state_sha256
    assert previous is None
    assert final.terminal == Terminal("completed") and final.unadmitted == ()
    for seq, digest in enumerate(digests, start=1):
        assert hashlib.sha256(_read(root, f"records/{seq:06d}.json")).hexdigest() == digest
    facts = tree(root)
    for name, entry in facts.items():
        if entry[0] == stat.S_IFREG:
            paired = name.startswith(("records/", "index/"))
            assert entry[1] == 0o600 and entry[3] == (2 if paired else 1), name
            if paired and not name.endswith(".staging"):
                assert facts[name + ".staging"] == entry, name
    # Every record and state is two names; every stream file is one.
    assert sum(1 for n in facts if n.endswith(".staging")) == 3 + 4 + 1
    assert final.publication.identity == (os.stat(root).st_dev, facts[name_of_f := "index/000004.final.json"][2])
    assert facts[name_of_f + ".staging"][2] == final.publication.inode
    assert all(state is PublicationState.ADMITTED for state in session.publication_states.values())
    assert _b0_ra(tmp_path, session, root).passed


def test_the_suites_act_stage_list_is_complete(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    session = open_session(host, filesystem=filesystem, launcher=ScriptedLauncher())
    start = len(filesystem.calls)
    session.run_act(act("A1-01", writes(b"", b"")))
    seen = {stage for _, stage in filesystem.calls[start:]}
    assert seen == set(ACT_STAGES)


def test_an_occupied_final_name_is_never_replaced(tmp_path: Path) -> None:
    """P-7: an object already at the final name refuses the act by the kernel's
    EEXIST; its bytes stay, it is not recorded as ours, and the staging name
    is retained as unadmitted — never removed."""
    host = Host.under(tmp_path)
    session = open_session(host)
    planted = Path(host.root()) / "records" / "000001.json"
    planted.write_bytes(b"planted")
    before = os.lstat(planted)
    outcome = session.run_act(act("A1-01", writes(b"", b"")))
    assert (outcome.failure.stage, outcome.failure.classification) == ("P-7:publish", "publication-exists")
    assert planted.read_bytes() == b"planted"
    after = os.lstat(planted)
    assert (after.st_ino, after.st_nlink, after.st_mtime_ns) == (before.st_ino, 1, before.st_mtime_ns)
    _, final = _final(host.root())
    unadmitted = {item.name for item in final.unadmitted}
    assert "records/000001.json" not in unadmitted
    assert "records/000001.json.staging" in unadmitted
    assert (Path(host.root()) / "records" / "000001.json.staging").exists()
    assert session.publication_states["records/000001.json"] is PublicationState.STAGING_ONLY
    # The occupant is not the mechanism's, so B0-RA fails closed on it.
    assert not _b0_ra(tmp_path, session, host.root()).passed


def test_an_occupied_staging_name_refuses_without_reading_or_removing_it(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host)
    planted = Path(host.root()) / "records" / "000001.json.staging"
    planted.write_bytes(b"someone else's")
    planted.chmod(0o000)  # it is never opened, so an unreadable occupant changes nothing
    before = os.lstat(planted)
    outcome = session.run_act(act("A1-01", writes(b"", b"")))
    assert (outcome.failure.stage, outcome.failure.classification) == ("P-5:create", "object-exists")
    after = os.lstat(planted)
    assert (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) == (
        before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns,
    )
    assert not (Path(host.root()) / "records" / "000001.json").exists()
    _, final = _final(host.root())
    assert "records/000001.json.staging" not in {item.name for item in final.unadmitted}
    assert session.publication_states["records/000001.json"] is PublicationState.NO_STAGING
    planted.chmod(0o600)


# ===========================================================================
# Every act stage, failed and interrupted
# ===========================================================================

STREAMS_2 = {"streams/stdout/000002", "streams/stderr/000002"}
RECORD_2 = "records/000002.json"
RECORD_2S = RECORD_2 + ".staging"
STATE_2 = "index/000002.open.json"
STATE_2S = STATE_2 + ".staging"

#: The state a publication reaches when the named stage of it fails (or is
#: interrupted) — and so what a stop there leaves on disk.
REACHED = {
    "create": PublicationState.NO_STAGING,
    "verify": PublicationState.STAGING_ONLY,
    "write": PublicationState.STAGING_ONLY,
    "verify-content": PublicationState.STAGING_ONLY,
    "file-barrier": PublicationState.STAGING_ONLY,
    "publish": PublicationState.STAGING_ONLY,
    "directory-barrier": PublicationState.LINKED,
    "verify-pair": PublicationState.BARRIERED,
    "close": PublicationState.VERIFIED,
}
NAMES_LEFT = {
    PublicationState.NO_STAGING: (),
    PublicationState.STAGING_ONLY: ("staging",),
    PublicationState.LINKED: ("staging", "final"),
    PublicationState.BARRIERED: ("staging", "final"),
    PublicationState.VERIFIED: ("staging", "final"),
}


def _left(final_name: str, state: PublicationState) -> set[str]:
    return {final_name + ".staging" if role == "staging" else final_name for role in NAMES_LEFT[state]}


def _reached(stage: str, mode: str) -> PublicationState:
    reached = REACHED[stage.split(":", 1)[1]]
    if mode == "after" and stage.endswith((":create",)):
        return PublicationState.STAGING_ONLY
    if mode == "after" and stage.endswith(":publish"):
        return PublicationState.LINKED
    return reached


def _expected_unadmitted(stage: str, mode: str) -> set[str]:
    if stage == "P-1:create-stdout":
        return {"streams/stdout/000002"} if mode == "after" else set()
    if stage in ("P-1:verify-stdout", "P-1:create-stderr"):
        return {"streams/stdout/000002"}
    if stage.startswith(("P-1", "P-2", "P-3", "P-4")):
        return set(STREAMS_2)
    if stage.startswith(("P-5", "P-6", "P-7", "P-8")):
        return STREAMS_2 | _left(RECORD_2, _reached(stage, mode))
    return STREAMS_2 | {RECORD_2, RECORD_2S} | _left(STATE_2, _reached(stage, mode))


FAIL_CASES = [(stage, "fail") for stage in ACT_STAGES] + [
    ("P-5:create", "after"),
    ("P-7:publish", "after"),
    ("X-2:create", "after"),
    ("X-2:publish", "after"),
    ("P-1:create-stdout", "after"),
]


@pytest.mark.parametrize("stage, mode", FAIL_CASES, ids=[f"{s}-{m}" for s, m in FAIL_CASES])
def test_every_act_stage_fails_closed_once_with_the_correct_final_state(
    tmp_path: Path, stage: str, mode: str
) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem(stage=stage, mode=mode, occurrence=1)
    launcher = CountingLauncher()
    # Act 1 is admitted before the fault is armed, so it must stay admitted.
    filesystem.stage = None
    session = open_session(host, filesystem=filesystem, launcher=launcher)
    assert session.run_act(act("A1-01", writes(b"out1", b"err1"))).admitted
    filesystem.stage = stage
    start = len(filesystem.calls)
    outcome = session.run_act(act("A1-02", writes(b"out2", b"err2")))

    assert filesystem.triggered
    assert not outcome.admitted
    assert outcome.failure.stage == stage
    assert outcome.stop.terminal.reason == outcome.failure.classification
    assert outcome.stop.terminal.capture_seq == 2
    # No retry: the failed stage was reached exactly once in act 2.
    assert [s for _, s in filesystem.calls[start:]].count(stage) == 1
    # No next command, ever.
    launches = len(launcher.calls)
    assert launches == (1 if stage.startswith(("P-1:create", "P-1:verify")) else 2)
    with pytest.raises(CaptureRefused):
        session.run_act(act("A1-03", writes(b"", b"")))
    with pytest.raises(CaptureRefused):
        session.complete()
    assert len(launcher.calls) == launches
    # One X-3 attempt, which succeeded, and X-4 holds for the retained root.
    assert filesystem.stages().count("X-3:create") == 1
    assert (outcome.stop.x3_outcome, outcome.stop.x4_validity) == ("succeeded", "valid")
    root = host.root()
    name, final = _final(root)
    assert name == "index/000002.final.json"
    assert [entry.capture_seq for entry in final.records] == [1]
    assert {item.name for item in final.unadmitted} == _expected_unadmitted(stage, mode)
    assert all(item.object_type is ObjectType.REGULAR for item in final.unadmitted)
    # The exact classified state of the publication the stop interrupted; it
    # was never advanced, repaired or cleaned up afterwards.
    if stage.startswith(("P-5", "P-6", "P-7", "P-8", "X-2")):
        subject = RECORD_2 if stage.startswith("P-") else STATE_2
        assert session.publication_states[subject] is _reached(stage, mode)
        present = names_under(root)
        expected_left = _left(subject, _reached(stage, mode))
        assert expected_left <= present
        assert not (_left(subject, PublicationState.VERIFIED) - expected_left) & present
    # Act 1's record and I-1 stay admitted; nothing unadmitted became admitted.
    assert session.publication_states["records/000001.json"] is PublicationState.ADMITTED
    assert session.publication_states.get(RECORD_2) is not PublicationState.ADMITTED
    # No repair: the act's stream files hold what the child wrote and nothing
    # else — all of it once both channels completed (P-2 onwards), a prefix of
    # it where the copy itself failed and the child was stopped.
    for stream, expected in (("stdout", b"out2"), ("stderr", b"err2")):
        path = Path(root) / "streams" / stream / "000002"
        if path.exists():
            retained = path.read_bytes()
            assert expected.startswith(retained)
            if not stage.startswith("P-1"):
                assert retained == expected
    # And B0-RA, applied to this root, admits it: every name is accounted for.
    assert _b0_ra(tmp_path, session, root).passed


@pytest.mark.parametrize("stage", ACT_STAGES)
def test_an_interruption_at_any_act_stage_ends_the_pass_with_no_x3(tmp_path: Path, stage: str) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    launcher = CountingLauncher()
    session = open_session(host, filesystem=filesystem, launcher=launcher)
    assert session.run_act(act("A1-01", writes(b"out1", b"err1"))).admitted
    filesystem.stage, filesystem.mode = stage, "interrupt"
    with pytest.raises(CaptureInterrupted):
        session.run_act(act("A1-02", writes(b"out2", b"err2")))
    assert filesystem.triggered
    assert filesystem.after_interrupt == []
    assert session.state is SessionState.INTERRUPTED
    launches = len(launcher.calls)
    for call in (
        lambda: session.run_act(act("A1-03", writes(b"", b""))),
        session.complete,
        lambda: session.stop(reason="operator-refusal"),
    ):
        with pytest.raises(CaptureRefused):
            call()
    assert filesystem.after_interrupt == []
    assert len(launcher.calls) == launches
    assert not [n for n in names_under(host.root()) if n.endswith(".final.json")]
    binding = session.binding()
    assert (binding.x3_outcome, binding.x4_validity, binding.final_state) == ("not-made", "inconclusive", None)


# ===========================================================================
# X-3: exactly one attempt, one outcome, then the seal
# ===========================================================================

X3_STAGES = FINAL_STAGES.ordered()


@pytest.mark.parametrize("stage", X3_STAGES)
def test_a_failed_x3_attempt_is_recorded_not_retried_and_x4_is_inconclusive(
    tmp_path: Path, stage: str
) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    session = open_session(host, filesystem=filesystem)
    session.run_act(act("A1-01", writes(b"", b"")))
    filesystem.stage = stage
    before = tree(host.root())
    outcome = session.complete()
    assert filesystem.triggered
    assert (outcome.x3_outcome, outcome.x3_failure_stage) == ("failed", stage)
    assert outcome.x4_validity == "inconclusive"
    assert filesystem.stages().count("X-3:create") == 1
    reached = REACHED[stage.split(":", 1)[1]]
    left = _left("index/000002.final.json", reached)
    assert outcome.final_name_present is ("index/000002.final.json" in left)
    assert outcome.final_staging_present is ("index/000002.final.json.staging" in left)
    assert session.publication_states["index/000002.final.json"] is reached
    after = tree(host.root())
    # X-3 created at most F's two names; every earlier object is untouched.
    for name, facts in before.items():
        if name != "index":
            assert after[name] == facts, name
    assert set(after) - set(before) == left
    with pytest.raises(CaptureRefused):
        session.complete()
    with pytest.raises(CaptureRefused):
        session.stop(reason="retry")
    assert filesystem.stages().count("X-3:create") == 1
    binding = session.binding()
    assert (binding.x3_outcome, binding.final_state, binding.capture_index_sha256) == ("failed", None, None)


@pytest.mark.parametrize("stage", X3_STAGES)
def test_an_interruption_during_x3_is_its_failure_and_nothing_follows(tmp_path: Path, stage: str) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    session = open_session(host, filesystem=filesystem)
    session.run_act(act("A1-01", writes(b"", b"")))
    filesystem.stage, filesystem.mode = stage, "interrupt"
    with pytest.raises(CaptureInterrupted):
        session.complete()
    assert filesystem.after_interrupt == []
    assert session.state is SessionState.INTERRUPTED
    with pytest.raises(CaptureRefused):
        session.complete()
    assert filesystem.after_interrupt == []
    assert session.binding().x3_outcome == "failed"


def test_an_operator_stop_is_one_transition_and_seals_the_session(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    launcher = ScriptedLauncher()
    session = open_session(host, launcher=launcher)
    session.run_act(act("A1-01", writes(b"", b"")))
    outcome = session.stop(reason="guard-refusal", step_or_case_id="A1-02")
    assert outcome.terminal == Terminal("stopped", None, "A1-02", "guard-refusal")
    assert (outcome.x3_outcome, outcome.x4_validity) == ("succeeded", "valid")
    assert session.state is SessionState.SEALED
    with pytest.raises(CaptureRefused):
        session.run_act(act("A1-02", writes(b"", b"")))
    assert len(launcher.calls) == 1
    _, final = _final(host.root())
    assert final.terminal.reason == "guard-refusal"


def test_there_is_no_way_to_resume_or_finalize_an_existing_root(tmp_path: Path) -> None:
    """After an interruption, a new process cannot adopt the root it left."""
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    session = open_session(host, filesystem=filesystem)
    session.run_act(act("A1-01", writes(b"", b"")))
    filesystem.stage, filesystem.mode = "P-6:file-barrier", "interrupt"
    with pytest.raises(CaptureInterrupted):
        session.run_act(act("A1-02", writes(b"", b"")))
    before = tree(host.root())
    recovered = open_session(host)
    assert recovered.state is SessionState.NO_GENESIS
    assert recovered.genesis_failure.classification == "object-exists"
    assert recovered.complete().x3_outcome == "not-made"
    assert tree(host.root()) == before
    public = [name for name in dir(mechanism_module) if not name.startswith("_")]
    assert not [name for name in public if any(w in name.lower() for w in ("open_", "resume", "adopt", "attach"))]


# ===========================================================================
# The suite's own descriptors — RP11-I1-R3-2
# ===========================================================================


def _own_descriptors() -> set[str]:
    """This pytest process's open descriptor numbers, and nothing else's."""
    return set(os.listdir("/proc/self/fd"))


def test_the_suite_releases_every_descriptor_it_leaves_open_on_purpose(tmp_path: Path) -> None:
    """An interruption, an unended session and a withheld close hold descriptors
    in this process by design. Released, the process is back where it began —
    the leak that exhausted a 1024 limit in one whole-package run."""
    for name in ("unended", "interrupted", "fail", "after"):
        (tmp_path / name).mkdir()
    release_suite_descriptors()
    before = _own_descriptors()
    unended = open_session(Host.under(tmp_path / "unended"))
    assert unended.state is SessionState.OPEN
    host = Host.under(tmp_path / "interrupted")
    interrupted = FaultFilesystem()
    session = open_session(host, filesystem=interrupted)
    interrupted.stage, interrupted.mode = "P-6:file-barrier", "interrupt"
    with pytest.raises(CaptureInterrupted):
        session.run_act(act("A1-01", writes(b"", b"")))
    assert interrupted.after_interrupt == []
    for stage, mode in (("P-8:close", "fail"), ("P-5:create", "after")):
        faulty = FaultFilesystem(stage=stage, mode=mode)
        stopped = open_session(Host.under(tmp_path / mode), filesystem=faulty)
        assert not stopped.run_act(act("A1-01", writes(b"", b""))).admitted
    assert _own_descriptors() - before, "the scenarios no longer hold anything"
    release_suite_descriptors()
    assert interrupted.after_interrupt == []
    assert _own_descriptors() == before


# ===========================================================================
# Structural: no execution, no network, not wired
# ===========================================================================

RP11_MODULES = (
    "tools/phase_5_0_evidence/capture_contract.py",
    "tools/phase_5_0_evidence/execution/capture_store.py",
    "tools/phase_5_0_evidence/execution/capture_mechanism.py",
    "tools/phase_5_0_evidence/execution/retention_check.py",
)


@pytest.mark.parametrize("path", RP11_MODULES)
def test_the_rp11_modules_are_inert_on_import_and_have_no_entry_point(path: str) -> None:
    tree_ = ast.parse((REPOSITORY / path).read_text(encoding="utf-8"))
    for node in tree_.body:
        assert not isinstance(node, ast.If), f"{path} has a module-level conditional"
        assert not isinstance(node, ast.Expr) or isinstance(node.value, ast.Constant)
    imported = set()
    for node in ast.walk(tree_):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])
    assert not imported & {"socket", "ssl", "http", "urllib", "requests", "psycopg", "sqlalchemy", "asyncio", "select"}


def test_nothing_outside_tests_arms_the_launcher_or_creates_a_session() -> None:
    offenders = []
    for path in sorted((REPOSITORY / "tools").rglob("*.py")):
        tree_ = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree_):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else (
                node.func.attr if isinstance(node.func, ast.Attribute) else ""
            )
            if name == "create_capture_session" and path.name != "capture_mechanism.py":
                offenders.append(f"{path.name}:{node.lineno}")
            if name == "StreamCaptureLauncher":
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == []


def test_the_harness_cli_does_not_reach_the_capture_mechanism() -> None:
    text = (REPOSITORY / "tools/phase_5_0_evidence/execution/cli.py").read_text(encoding="utf-8")
    for module in ("capture_mechanism", "capture_store", "retention_check", "capture_contract"):
        assert module not in text


def _functions(path: str) -> dict[str, ast.FunctionDef]:
    tree_ = ast.parse((REPOSITORY / path).read_text(encoding="utf-8"))
    return {n.name: n for n in ast.walk(tree_) if isinstance(n, ast.FunctionDef)}


def test_the_package_has_one_link_call_it_never_follows_and_two_callers_reach_it() -> None:
    functions = _functions("tools/phase_5_0_evidence/execution/descriptors.py")
    site = functions["_exclusive_link"]
    assert [a.arg for a in site.args.args + site.args.kwonlyargs] == [
        "source", "destination", "source_dir_fd", "destination_dir_fd",
    ]
    (call,) = [n for n in ast.walk(site) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "link"]
    follow = next(k for k in call.keywords if k.arg == "follow_symlinks")
    assert isinstance(follow.value, ast.Constant) and follow.value.value is False
    callers = sorted(
        name
        for name, node in functions.items()
        if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_exclusive_link" for n in ast.walk(node))
    )
    assert callers == ["link_named_exclusive", "linkat"]
    assert "link_unnamed_descriptor" not in functions
    assert not hasattr(descriptors, "link_unnamed_descriptor")
    assert not hasattr(descriptors, "UNNAMED_PUBLICATION")
    assert "link_named_exclusive" in descriptors.__all__


def test_a_real_named_link_refuses_to_replace_and_keeps_both_names(tmp_path: Path) -> None:
    fs = PosixCaptureFilesystem()
    directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fd = fs.create_exclusive(directory, "first.staging", 0o600, stage="t")
        fs.write_all(fd, b"first", stage="t")
        os.close(fd)
        fs.link_exclusive(directory, "first.staging", "published", stage="t")
        other = fs.create_exclusive(directory, "second.staging", 0o600, stage="t")
        fs.write_all(other, b"second", stage="t")
        os.close(other)
        with pytest.raises(FileExistsError):
            fs.link_exclusive(directory, "second.staging", "published", stage="t")
        (tmp_path / "link").symlink_to(tmp_path / "second.staging")
        fs.link_exclusive(directory, "link", "not-followed", stage="t")
        for bad in ("a/b", "..", ""):
            with pytest.raises(ValueError):
                fs.link_exclusive(directory, "first.staging", bad, stage="t")
    finally:
        os.close(directory)
    assert (tmp_path / "published").read_bytes() == b"first"
    assert os.stat(tmp_path / "published").st_ino == os.stat(tmp_path / "first.staging").st_ino
    assert os.stat(tmp_path / "published").st_nlink == 2
    assert os.lstat(tmp_path / "not-followed").st_ino == os.lstat(tmp_path / "link").st_ino
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "first.staging", "link", "not-followed", "published", "second.staging",
    ]


def test_an_injected_error_is_the_errno_the_suite_claims() -> None:
    """The fault filesystem raises what a failing kernel call would."""
    filesystem = FaultFilesystem(stage="s")
    with pytest.raises(OSError) as raised:
        filesystem._invoke("fsync", "s", lambda: None)
    assert raised.value.errno == errno.EIO


# ===========================================================================
# C-P5.0-R5-RP11-I1-R3 — the retained-alias publication, stage by stage
# ===========================================================================

#: One publication, as the filesystem sees it: (method, stage suffix). The
#: staging name is created, checked and synchronized **before** the one link;
#: the directory barrier follows the link; both names are verified after it.
PUBLICATION_CALLS = [
    ("create_exclusive", "create"),
    ("fstat", "verify"),
    ("write_all", "write"),
    ("open_read", "verify-content"),
    ("fstat", "verify-content"),
    ("digest", "verify-content"),
    ("close", "verify-content"),
    ("fsync", "file-barrier"),
    ("link_exclusive", "publish"),
    ("fsync", "directory-barrier"),
    *[
        call
        for _ in ("staging", "final")
        for call in (
            ("open_read", "verify-pair"),
            ("fstat", "verify-pair"),
            ("digest", "verify-pair"),
            ("close", "verify-pair"),
        )
    ],
    ("close", "close"),
]


def _calls_for(filesystem: FaultFilesystem, stages) -> list[tuple[str, str]]:  # type: ignore[no-untyped-def]
    wanted = set(stages.ordered())
    return [(method, stage.split(":")[-1]) for method, stage in filesystem.calls if stage in wanted]


@pytest.mark.parametrize("stages", [GENESIS_STAGES, RECORD_STAGES, ADVANCE_STAGES, FINAL_STAGES], ids=lambda s: s.create)
def test_each_publication_is_exactly_the_accepted_sequence(tmp_path: Path, stages) -> None:  # type: ignore[no-untyped-def]
    """Staging created, verified, written, content-checked and synchronized;
    **one** link, no pre-check of the final name, no rename, no unlink; the
    directory barrier; both names verified; then the close."""
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    session = open_session(host, filesystem=filesystem)
    session.run_act(act("A1-01", writes(b"out", b"err")))
    session.complete()
    assert _calls_for(filesystem, stages) == PUBLICATION_CALLS
    methods = {method for method, _ in filesystem.calls}
    assert not methods & {"rename", "unlink", "remove", "replace", "link_unnamed", "create_unnamed"}
    assert [m for m, _ in filesystem.calls].count("link_exclusive") == 4  # I-0, record, I-1, F
    assert "lstat_at" not in {m for m, stage in filesystem.calls if stage in set(stages.ordered())}


def test_a_successful_publication_is_one_inode_with_two_names_and_exact_bytes(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    session = open_session(host, launcher=CountingLauncher())
    outcome = session.run_act(act("A1-01", writes(b"o", b"e")))
    root = Path(host.root())
    for final_name in ("index/000000.open.json", "records/000001.json", "index/000001.open.json"):
        final_path, staging_path = root / final_name, root / (final_name + ".staging")
        a, b = os.lstat(final_path), os.lstat(staging_path)
        assert stat.S_ISREG(a.st_mode) and (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino)
        assert a.st_nlink == 2 and stat.S_IMODE(a.st_mode) == 0o600 and a.st_uid == os.geteuid()
        assert final_path.read_bytes() == staging_path.read_bytes()
    record_bytes = (root / "records/000001.json").read_bytes()
    assert hashlib.sha256(record_bytes).hexdigest() == outcome.record_sha256
    state = IndexState.from_bytes((root / "index/000001.open.json").read_bytes())
    (entry,) = state.records
    record_facts = os.lstat(root / "records/000001.json")
    assert (entry.staging, entry.device, entry.inode) == (
        "records/000001.json.staging", record_facts.st_dev, record_facts.st_ino,
    )
    genesis_facts = os.lstat(root / "index/000000.open.json")
    assert state.previous.identity == (genesis_facts.st_dev, genesis_facts.st_ino)
    assert state.previous.staging == "index/000000.open.json.staging"
    assert state.previous.sha256 == hashlib.sha256((root / "index/000000.open.json").read_bytes()).hexdigest()
    assert state.owner_uid == os.geteuid()


@pytest.mark.parametrize("mode", FaultFilesystem.FALSE_WRITES)
@pytest.mark.parametrize("stage", [RECORD_STAGES.write, ADVANCE_STAGES.write, GENESIS_STAGES.write])
def test_a_partial_empty_or_falsely_reported_write_never_admits(tmp_path: Path, stage: str, mode: str) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem(stage=stage, mode=mode)
    launcher = ScriptedLauncher()
    session = open_session(host, filesystem=filesystem, launcher=launcher)
    subject = {
        GENESIS_STAGES.write: "index/000000.open.json",
        RECORD_STAGES.write: "records/000001.json",
        ADVANCE_STAGES.write: "index/000001.open.json",
    }[stage]
    if stage == GENESIS_STAGES.write:
        assert session.state is SessionState.NO_GENESIS
        failure = session.genesis_failure
    else:
        outcome = session.run_act(act("A1-01", writes(b"", b"")))
        assert not outcome.admitted
        failure = outcome.failure
    assert filesystem.triggered
    prefix = stage.rsplit(":", 1)[0]
    expected = "content-mismatch" if mode == "corrupt" else "size-mismatch"
    assert (failure.stage, failure.classification) == (f"{prefix}:verify-content", expected)
    # No link was attempted: only the retained staging name exists.
    assert not [c for c in filesystem.calls if c[0] == "link_exclusive" and c[1].startswith(prefix)]
    assert session.publication_states[subject] is PublicationState.STAGING_ONLY
    assert (Path(host.root()) / (subject + ".staging")).exists()
    assert not (Path(host.root()) / subject).exists()
    if stage != GENESIS_STAGES.write:
        assert session.admitted_records == 0
        _, final = _final(host.root())
        assert subject + ".staging" in {item.name for item in final.unadmitted}
        assert final.records == ()
        assert _b0_ra(tmp_path, session, host.root()).passed


def test_the_write_loop_completes_short_writes_and_refuses_no_progress(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    fs = PosixCaptureFilesystem()
    real_write = os.write
    target = tmp_path / "f"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        monkeypatch.setattr(os, "write", lambda f, view: real_write(f, bytes(view[:3])))
        fs.write_all(fd, b"0123456789", stage="t")
        monkeypatch.setattr(os, "write", lambda f, view: 0)
        with pytest.raises(OSError):
            fs.write_all(fd, b"more", stage="t")
    finally:
        monkeypatch.undo()
        os.close(fd)
    assert target.read_bytes() == b"0123456789"


INTERRUPTIBLE = [
    *[(stage, "records/000002.json") for stage in RECORD_STAGES.ordered()],
    *[(stage, "index/000002.open.json") for stage in ADVANCE_STAGES.ordered()],
]


@pytest.mark.parametrize("stage, subject", INTERRUPTIBLE, ids=[s for s, _ in INTERRUPTIBLE])
def test_every_publication_interruption_leaves_its_exact_classified_state(
    tmp_path: Path, stage: str, subject: str
) -> None:
    """§3: an interruption at any step leaves exactly the names that step had
    created, classifies them, and nothing afterwards — not a close, a retry, a
    clean-up, an X-3 or a next command — touches the filesystem."""
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    launcher = CountingLauncher()
    session = open_session(host, filesystem=filesystem, launcher=launcher)
    assert session.run_act(act("A1-01", writes(b"o1", b"e1"))).admitted
    filesystem.stage, filesystem.mode = stage, "interrupt"
    before = tree(host.root())
    with pytest.raises(CaptureInterrupted):
        session.run_act(act("A1-02", writes(b"o2", b"e2")))
    reached = REACHED[stage.split(":", 1)[1]]
    assert session.publication_states[subject] is reached
    present = names_under(host.root())
    assert _left(subject, reached) <= present
    assert not (_left(subject, PublicationState.VERIFIED) - _left(subject, reached)) & present
    if subject == "index/000002.open.json":
        assert session.publication_states["records/000002.json"] is PublicationState.VERIFIED
        assert session.publication_states["index/000001.open.json"] is PublicationState.VERIFIED
    assert session.publication_states["records/000001.json"] is PublicationState.ADMITTED
    for call in (session.complete, lambda: session.run_act(act("A1-03", writes(b"", b"")))):
        with pytest.raises(CaptureRefused):
            call()
    assert filesystem.after_interrupt == []
    assert len(launcher.calls) == 2
    assert not [n for n in present if ".final.json" in n]
    # Everything that existed before act 2 is untouched.
    after = tree(host.root())
    for name, facts in before.items():
        if name not in LAYOUT:
            assert after[name] == facts, name


@pytest.mark.parametrize("stage", GENESIS_STAGES.ordered())
def test_the_first_genesis_publication_is_the_fail_closed_capability_test(tmp_path: Path, stage: str) -> None:
    """There is no separate probe. If X-1's genesis publication fails at any
    step, no command runs, no X-3 is made, and what X-1 left is reported by
    exact name as bounded residue — retained, never cleaned up."""
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem(stage=stage)
    launcher = CountingLauncher()
    session = open_session(host, filesystem=filesystem, launcher=launcher)
    assert session.state is SessionState.NO_GENESIS
    assert session.genesis_failure.stage == stage
    outcome = session.complete()
    assert outcome.x3_outcome == "not-made" and outcome.final_state is None
    assert launcher.calls == []
    with pytest.raises(CaptureRefused):
        session.run_act(act("A1-01", writes(b"", b"")))
    on_disk = {n for n, f in tree(host.root()).items() if f[0] == stat.S_IFREG}
    assert {item.name for item in outcome.unadmitted} == on_disk
    assert on_disk == _left("index/000000.open.json", REACHED[stage.split(":", 2)[2]])
    assert set(outcome.subdirectories) == LAYOUT
    binding = session.binding()
    assert (binding.x3_outcome, binding.final_state, binding.capture_index_sha256) == ("not-made", None, None)


def test_a_failed_barrier_is_terminal_and_never_cured(tmp_path: Path) -> None:
    host = Host.under(tmp_path)
    filesystem = FaultFilesystem()
    session = open_session(host, filesystem=filesystem)
    session.run_act(act("A1-01", writes(b"", b"")))
    filesystem.stage = RECORD_STAGES.directory_barrier
    outcome = session.run_act(act("A1-02", writes(b"", b"")))
    assert outcome.failure.stage == RECORD_STAGES.directory_barrier
    # The one later directory barrier is X-3's own, on F's directory.
    failed_at = max(i for i, call in enumerate(filesystem.calls) if call == ("fsync", RECORD_STAGES.directory_barrier))
    later = filesystem.calls[failed_at + 1 :]
    assert [stage for method, stage in later if method == "fsync"] == [
        FINAL_STAGES.file_barrier, FINAL_STAGES.directory_barrier,
    ]
    assert session.publication_states["records/000002.json"] is PublicationState.LINKED
    with pytest.raises(ValueError):
        session._store.mark_admitted("records/000002.json")
    assert session.publication_states["records/000002.json"] is PublicationState.LINKED


RP11_SOURCE_MODULES = (
    *RP11_MODULES,
    "tools/phase_5_0_evidence/execution/descriptors.py",
)


@pytest.mark.parametrize("path", RP11_SOURCE_MODULES)
def test_no_unnamed_inode_procfs_ctypes_rename_or_removal_on_the_rp11_route(path: str) -> None:
    tree_ = ast.parse((REPOSITORY / path).read_text(encoding="utf-8"))
    for node in ast.walk(tree_):
        if isinstance(node, ast.Attribute):
            assert node.attr != "O_TMPFILE", path
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] + [getattr(node, "module", None) or ""]
            assert not any("ctypes" in name for name in names), path
        if isinstance(node, ast.JoinedStr):
            text = "".join(v.value for v in node.values if isinstance(v, ast.Constant))
            assert not text.startswith("/proc"), path
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            assert not node.value.startswith("/proc/self/fd"), path
    if path == "tools/phase_5_0_evidence/execution/descriptors.py":
        return  # I3's reviewed renameat/unlinkat live here, unchanged
    for node in ast.walk(tree_):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {
                "rename", "renames", "replace", "unlink", "remove", "rmdir", "removedirs",
                "link", "symlink", "truncate", "ftruncate", "chmod", "fchmod",
            } or not (isinstance(node.func.value, ast.Name) and node.func.value.id in ("os", "shutil")), (path, node.func.attr)


def test_the_store_links_only_through_the_shared_named_primitive() -> None:
    source = (REPOSITORY / "tools/phase_5_0_evidence/execution/capture_store.py").read_text(encoding="utf-8")
    tree_ = ast.parse(source)
    imported = {
        (node.module, alias.name)
        for node in ast.walk(tree_)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert ("descriptors", "link_named_exclusive") in imported
    assert not {name for _, name in imported} & {"link_unnamed_descriptor", "_exclusive_link", "PosixFilesystem"}
    publish = _functions("tools/phase_5_0_evidence/execution/capture_store.py")["publish"]
    links = [n for n in ast.walk(publish) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "link_exclusive"]
    assert len(links) == 1
    flags = PosixCaptureFilesystem.create_exclusive.__code__.co_names
    assert {"O_WRONLY", "O_CREAT", "O_EXCL", "O_NOFOLLOW", "O_CLOEXEC"} <= set(flags)
