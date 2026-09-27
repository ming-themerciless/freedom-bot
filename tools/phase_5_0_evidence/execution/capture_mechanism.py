"""RP-11's capture mechanism: one pass's acts, stop transition and finalization.

A `CaptureSession` is one pass's capture: its own root, genesis state, index
chain and final state (C-6, C-14). It is created by `create_capture_session`,
which performs X-1 — exclusive creation of the root and its subdirectories, then
durable publication of the genesis state *I*-0 — before any command can run.
Each `run_act` then issues **one** exact argument vector through the injected
launcher with no shell, and publishes its evidence in the draft's order:

| Step | What happens | Where |
|---|---|---|
| P-1 | both stream files created exclusively; the vector runs; each channel is copied raw into its own file | `capture_store`, `boundary.StreamCaptureLauncher` |
| P-2 | each file closed to writing, reopened read-only by name, identity-checked, file barrier | `CaptureRootStore.complete_stream` |
| P-3 | directory barrier on `streams/stdout` and `streams/stderr` | `CaptureRootStore.directory_barrier` |
| P-4 | SHA-256 of exactly the completed bytes | `CaptureRootStore.digest_stream` |
| P-5 … P-8 | the record, unnamed, written, file barrier, exclusive link, directory barrier | `CaptureRootStore.publish` |
| X-2 | open state *I*-*n* by the same sequence; only then may act *n* + 1 begin | `CaptureRootStore.publish` |

## The one stop transition (§9.5.3)

Every stop takes the same path, `_stop_transition`, in this order:

1. **Stop commands.** The session leaves `OPEN` before anything else happens,
   and every later `run_act` refuses without touching the filesystem or the
   launcher. Nothing is retried, repaired or reissued.
2. **One X-3 attempt, only where possible.** Only if the session has a durable
   genesis state and was not interrupted. `_x3_attempted` is set **before** the
   attempt's first call, so no path can make a second.
3. **One outcome.** Success is the directory barrier after *F*'s link.
   Anything else — including a failed barrier — is the attempt's failure, and
   it is recorded, not retried and not cured.
4. **Read-only.** The session is sealed: its directory descriptors are released
   and every writing method refuses. Maintainer decision, 2026-09-27: read-only
   is this behavioural seal. No `chmod` is issued, so C-7's `0700`/`0600` modes
   stand and X-3 stays the only write after a stop.
5. **X-4, never reconstruction.** If the attempt succeeded, X-4 is re-applied to
   the bytes on disk by `retention_check.verify_final_state`. If it failed or
   was not made, there is no admissible final state and X-4 is `inconclusive`;
   nothing is written to make it otherwise.

A pass that **completes** takes steps 2 to 5 the same way.

## Interruption

`CaptureInterrupted` from any seam marks the session `INTERRUPTED` and
propagates; nothing else is called, not even a close. An interrupted session
refuses every later call, including `complete()` and `stop()`, so no X-3 attempt
is made "after recovery". There is no function that opens an existing root:
`create_capture_session` creates a root exclusively or fails, so a new process
cannot adopt, resume or finalize a root it did not create in X-1.

## What *F* records

*F* lists exactly the last durable open state's records and carries its SHA-256,
the terminal status, the five subdirectories, and **every unadmitted object the
store knows exists**, by exact relative name and type, with no digest: every
name the store created or positively probed that is not the chain, an admitted
record or a stream file an admitted record binds.

## Not wired

Nothing in the repository constructs a session outside `tests/`. There is no
command-line entry point, and no operational command is named here. How the
§5 synchronization would be issued through this mechanism without changing
what `guard-secrets.py` inspects (C-11) is returned as an open question.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping, Protocol, Sequence

from ..capture_contract import (
    FINAL,
    INDEX_DIRECTORY,
    MAX_STREAM_BOUND_BYTES,
    OPEN,
    STDERR,
    STDERR_DIRECTORY,
    STDOUT,
    STDOUT_DIRECTORY,
    SUBDIRECTORIES,
    X3_FAILED,
    X3_NOT_MADE,
    X3_SUCCEEDED,
    X4_INCONCLUSIVE,
    X4_VALID,
    CaptureContractRefused,
    CaptureRecord,
    ExitOutcome,
    HandbackBinding,
    IndexEntry,
    IndexState,
    ObjectType,
    StreamBinding,
    Terminal,
    UnadmittedObject,
    format_utc,
    parse_capture_root,
    record_name,
    require_identifier,
    require_sha256,
    stream_name,
    validate_argv,
)
from ..errors import HarnessError
from .boundary import CAPTURE_DRAIN_SECONDS, StreamCaptureResult, StreamSink
from .capture_store import (
    ADVANCE_STAGES,
    CLEANUP_STAGE,
    FINAL_STAGES,
    GENESIS_STAGES,
    RECORD_STAGES,
    CaptureFilesystem,
    CaptureInterrupted,
    CaptureRootStore,
    RootPolicy,
    StoreFailure,
)
from .retention_check import (
    PosixReadOnlyFilesystem,
    ReadOnlyFilesystem,
    verify_final_state,
)

#: Every stage label an act can fail at, in the order they are reached. The
#: suite fails each one in turn.
ACT_STAGES = (
    "P-1:create-stdout",
    "P-1:verify-stdout",
    "P-1:create-stderr",
    "P-1:verify-stderr",
    "P-1:write-stdout",
    "P-1:write-stderr",
    "P-2:close-stdout",
    "P-2:reopen-stdout",
    "P-2:verify-stdout",
    "P-2:file-barrier-stdout",
    "P-2:close-stderr",
    "P-2:reopen-stderr",
    "P-2:verify-stderr",
    "P-2:file-barrier-stderr",
    "P-3:directory-barrier-stdout",
    "P-3:directory-barrier-stderr",
    "P-4:digest-stdout",
    "P-4:close-stdout",
    "P-4:digest-stderr",
    "P-4:close-stderr",
    RECORD_STAGES.create,
    RECORD_STAGES.verify,
    RECORD_STAGES.write,
    RECORD_STAGES.file_barrier,
    RECORD_STAGES.publish,
    RECORD_STAGES.directory_barrier,
    RECORD_STAGES.close,
    ADVANCE_STAGES.create,
    ADVANCE_STAGES.verify,
    ADVANCE_STAGES.write,
    ADVANCE_STAGES.file_barrier,
    ADVANCE_STAGES.publish,
    ADVANCE_STAGES.directory_barrier,
    ADVANCE_STAGES.close,
)

#: The act-level failures that are not a storage stage.
LAUNCH_STAGE = "P-1:launch"
REQUEST_STAGE = "P-0:request"


class SessionState(str, Enum):
    OPEN = "open"
    SEALED = "sealed"
    INTERRUPTED = "interrupted"
    NO_GENESIS = "no-genesis"


class CaptureRefused(HarnessError):
    """The session does not accept this call in its current state."""


class UtcClock(Protocol):
    """C-4's client clock. `source` names it in every record."""

    source: str

    def now(self) -> datetime: ...


class SystemUtcClock:
    source = "repository-host CLOCK_REALTIME via datetime.now(timezone.utc)"

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class ProcessLauncher(Protocol):
    def launch(
        self,
        argv: Sequence[str],
        *,
        environment: Mapping[str, str],
        stdout: StreamSink,
        stderr: StreamSink,
        stream_bound_bytes: int,
        drain_seconds: float = ...,
    ) -> StreamCaptureResult: ...


@dataclass(frozen=True, slots=True)
class GenesisRequest:
    capture_root: str
    pass_id: str
    tool_sha256: str
    policy: RootPolicy


@dataclass(frozen=True, slots=True)
class ActRequest:
    step_or_case_id: str
    argv: tuple[str, ...]
    environment: Mapping[str, str]
    stream_bound_bytes: int
    drain_seconds: float = CAPTURE_DRAIN_SECONDS


@dataclass(frozen=True, slots=True)
class ActFailure:
    stage: str
    classification: str
    #: True when the vector may have started, so a remote effect may exist
    #: without admissible evidence (C-10).
    host_act_may_have_run: bool


@dataclass(frozen=True, slots=True)
class FinalizationOutcome:
    """Steps 2 … 5 of the stop transition, as the handback states them."""

    x3_outcome: str
    x3_failure_stage: str | None
    x3_failure_classification: str | None
    terminal: Terminal | None
    final_state: str | None
    final_state_sha256: str | None
    #: True when a failed attempt left *F*'s name in place. That file is not
    #: admissible and is reported, never repaired.
    final_name_present: bool
    x4_validity: str
    x4_reason: str
    admitted_records: int
    subdirectories: tuple[str, ...]
    unadmitted: tuple[UnadmittedObject, ...]


@dataclass(frozen=True, slots=True)
class ActOutcome:
    capture_seq: int
    admitted: bool
    record_sha256: str | None
    exit: ExitOutcome | None
    failure: ActFailure | None
    stop: FinalizationOutcome | None


class _ActFailed(Exception):
    def __init__(self, failure: ActFailure) -> None:
        super().__init__(failure.classification)
        self.failure = failure


class _FileSink:
    """A launcher sink that writes through the store, under one stage label."""

    def __init__(self, store: CaptureRootStore, fd: int, stage: str) -> None:
        self._store = store
        self._fd = fd
        self._stage = stage

    def write(self, data: bytes) -> None:
        self._store.write(self._fd, data, stage=self._stage)


@dataclass(frozen=True, slots=True)
class _Published:
    name: str
    sha256: str
    state: IndexState


class CaptureSession:
    """One pass's capture. Constructed only by `create_capture_session`."""

    def __init__(
        self,
        *,
        request: GenesisRequest,
        store: CaptureRootStore,
        launcher: ProcessLauncher,
        clock: UtcClock,
        verifier_filesystem: ReadOnlyFilesystem,
    ) -> None:
        self._request = request
        self._store = store
        self._launcher = launcher
        self._clock = clock
        self._verifier_filesystem = verifier_filesystem
        self._state = SessionState.NO_GENESIS
        self._genesis_failure: StoreFailure | None = None
        self._chain: list[_Published] = []
        self._records: list[tuple[IndexEntry, CaptureRecord]] = []
        self._x3_attempted = False
        self._outcome: FinalizationOutcome | None = None

    # -- state -----------------------------------------------------------------

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def genesis_failure(self) -> StoreFailure | None:
        return self._genesis_failure

    @property
    def outcome(self) -> FinalizationOutcome | None:
        return self._outcome

    @property
    def admitted_records(self) -> int:
        return len(self._records)

    def binding(self) -> HandbackBinding:
        """The fixed block the handback carries (`capture_contract`)."""
        outcome = self._outcome
        if outcome is None:
            if self._state is SessionState.OPEN:
                raise CaptureRefused("the pass has not ended; there is nothing to bind")
            return HandbackBinding(
                pass_id=self._request.pass_id,
                capture_root=self._request.capture_root,
                x3_outcome=X3_NOT_MADE,
                x4_validity=X4_INCONCLUSIVE,
                final_state=None,
                capture_index_sha256=None,
            )
        succeeded = outcome.x3_outcome == X3_SUCCEEDED
        return HandbackBinding(
            pass_id=self._request.pass_id,
            capture_root=self._request.capture_root,
            x3_outcome=outcome.x3_outcome,
            x4_validity=outcome.x4_validity,
            final_state=outcome.final_state if succeeded else None,
            capture_index_sha256=outcome.final_state_sha256 if succeeded else None,
        )

    # -- X-1 -------------------------------------------------------------------

    def _genesis(self) -> None:
        try:
            self._store.create_root(self._request.policy)
            genesis = IndexState(
                pass_id=self._request.pass_id,
                capture_root=self._request.capture_root,
                tool_sha256=self._request.tool_sha256,
                state_number=0,
                previous_state_sha256=None,
                status=OPEN,
                records=(),
            )
            digest = self._store.publish(genesis.name, genesis.to_bytes(), stages=GENESIS_STAGES)
        except CaptureInterrupted:
            self._state = SessionState.INTERRUPTED
            raise
        except StoreFailure as failure:
            self._genesis_failure = failure
            self._state = SessionState.NO_GENESIS
            self._store.release()
            return
        self._chain.append(_Published(genesis.name, digest, genesis))
        self._state = SessionState.OPEN

    # -- acts --------------------------------------------------------------------

    def run_act(self, request: ActRequest) -> ActOutcome:
        """Issue one exact argv and publish its evidence, or stop the pass."""
        self._require(SessionState.OPEN, "no further command is issued")
        capture_seq = len(self._records) + 1
        try:
            outcome = self._act(capture_seq, request)
        except CaptureInterrupted:
            self._state = SessionState.INTERRUPTED
            raise
        except _ActFailed as failed:
            step = request.step_or_case_id if isinstance(request.step_or_case_id, str) else None
            try:
                step = require_identifier(step, "step")
            except CaptureContractRefused:
                step = None
            stop = self._stop_transition(
                Terminal(
                    status="stopped",
                    capture_seq=capture_seq,
                    step_or_case_id=step,
                    reason=failed.failure.classification,
                )
            )
            return ActOutcome(
                capture_seq=capture_seq,
                admitted=False,
                record_sha256=None,
                exit=None,
                failure=failed.failure,
                stop=stop,
            )
        return outcome

    def complete(self) -> FinalizationOutcome:
        """The pass ended without a stop: one X-3 attempt, then the seal."""
        return self._external_end(Terminal(status="completed"))

    def stop(self, *, reason: str, step_or_case_id: str | None = None) -> FinalizationOutcome:
        """A stop the operator observed — a §11.1 refusal or a §11.2 stop."""
        return self._external_end(
            Terminal(status="stopped", step_or_case_id=step_or_case_id, reason=reason)
        )

    def _external_end(self, terminal: Terminal) -> FinalizationOutcome:
        if self._state is SessionState.NO_GENESIS and self._outcome is None:
            self._outcome = self._not_made("no-durable-genesis")
            return self._outcome
        self._require(SessionState.OPEN, "the pass has already ended")
        return self._stop_transition(terminal)

    def _act(self, capture_seq: int, request: ActRequest) -> ActOutcome:
        try:
            require_identifier(request.step_or_case_id, "step_or_case_id")
            argv = validate_argv(request.argv)
            if not (
                isinstance(request.stream_bound_bytes, int)
                and 0 < request.stream_bound_bytes <= MAX_STREAM_BOUND_BYTES
            ):
                raise CaptureContractRefused("malformed-argv", "stream bound")
        except CaptureContractRefused as refusal:
            raise _ActFailed(ActFailure(REQUEST_STAGE, f"request-{refusal.classification}", False))

        store = self._store
        names = {stream: stream_name(capture_seq, stream) for stream in (STDOUT, STDERR)}
        write_fds: dict[str, int] = {}
        read_fds: dict[str, int] = {}
        launched = False
        try:
            for stream in (STDOUT, STDERR):
                write_fds[stream] = store.create_stream_file(
                    names[stream],
                    create_stage=f"P-1:create-{stream}",
                    verify_stage=f"P-1:verify-{stream}",
                )
            started = format_utc(self._clock.now())
            launched = True
            result = self._launcher.launch(
                argv,
                environment=dict(request.environment),
                stdout=_FileSink(store, write_fds[STDOUT], "P-1:write-stdout"),
                stderr=_FileSink(store, write_fds[STDERR], "P-1:write-stderr"),
                stream_bound_bytes=request.stream_bound_bytes,
                drain_seconds=request.drain_seconds,
            )
            ended = format_utc(self._clock.now())
            if not result.started:
                raise _ActFailed(ActFailure(LAUNCH_STAGE, result.failure or "start-failed", False))
            if result.bound_exceeded:
                raise _ActFailed(ActFailure(LAUNCH_STAGE, "stream-bound-exceeded", True))
            if not result.streams_complete:
                raise _ActFailed(ActFailure(LAUNCH_STAGE, "stream-incomplete", True))
            assert result.returncode is not None

            counts = {STDOUT: result.stdout_bytes, STDERR: result.stderr_bytes}
            for stream in (STDOUT, STDERR):  # P-2
                fd = write_fds.pop(stream)
                read_fds[stream] = store.complete_stream(
                    names[stream],
                    fd,
                    close_stage=f"P-2:close-{stream}",
                    reopen_stage=f"P-2:reopen-{stream}",
                    verify_stage=f"P-2:verify-{stream}",
                    barrier_stage=f"P-2:file-barrier-{stream}",
                )
            store.directory_barrier(STDOUT_DIRECTORY, stage="P-3:directory-barrier-stdout")
            store.directory_barrier(STDERR_DIRECTORY, stage="P-3:directory-barrier-stderr")
            bindings: dict[str, StreamBinding] = {}
            for stream in (STDOUT, STDERR):  # P-4
                digest, size = store.digest_stream(
                    read_fds[stream], counts[stream], stage=f"P-4:digest-{stream}"
                )
                store.close(read_fds.pop(stream), stage=f"P-4:close-{stream}")
                bindings[stream] = StreamBinding(name=names[stream], sha256=digest, size=size)

            record = CaptureRecord(
                pass_id=self._request.pass_id,
                capture_seq=capture_seq,
                step_or_case_id=request.step_or_case_id,
                argv=argv,
                clock_source=self._clock.source,
                started_utc=started,
                ended_utc=ended,
                exit=ExitOutcome.from_returncode(result.returncode),
                stream_bound_bytes=request.stream_bound_bytes,
                stdout=bindings[STDOUT],
                stderr=bindings[STDERR],
            )
            record_digest = store.publish(
                record_name(capture_seq), record.to_bytes(), stages=RECORD_STAGES
            )  # P-5 … P-8
            entry = IndexEntry(capture_seq, record_name(capture_seq), record_digest)
            previous = self._chain[-1]
            state = IndexState(
                pass_id=self._request.pass_id,
                capture_root=self._request.capture_root,
                tool_sha256=self._request.tool_sha256,
                state_number=capture_seq,
                previous_state_sha256=previous.sha256,
                status=OPEN,
                records=(*previous.state.records, entry),
            )
            state_digest = store.publish(state.name, state.to_bytes(), stages=ADVANCE_STAGES)  # X-2
        except StoreFailure as failure:
            self._close_quietly(write_fds, read_fds)
            raise _ActFailed(ActFailure(failure.stage, failure.classification, launched)) from None
        except (_ActFailed, CaptureContractRefused) as failure:
            self._close_quietly(write_fds, read_fds)
            if isinstance(failure, _ActFailed):
                raise
            raise _ActFailed(ActFailure(LAUNCH_STAGE, failure.classification, launched)) from None
        self._chain.append(_Published(state.name, state_digest, state))
        self._records.append((entry, record))
        return ActOutcome(
            capture_seq=capture_seq,
            admitted=True,
            record_sha256=record_digest,
            exit=record.exit,
            failure=None,
            stop=None,
        )

    # -- the stop transition ---------------------------------------------------

    def _stop_transition(self, terminal: Terminal) -> FinalizationOutcome:
        # 1. No further command: the session leaves OPEN before anything else.
        self._state = SessionState.SEALED
        # 2. and 3. One attempt, one outcome.
        outcome = self._finalize_once(terminal)
        # 4. Read-only: the behavioural seal. Descriptors released; no chmod.
        self._store.release()
        # 5. X-4 on the bytes, or inconclusive without reconstruction.
        self._outcome = self._apply_x4(outcome)
        return self._outcome

    def _finalize_once(self, terminal: Terminal) -> FinalizationOutcome:
        if self._x3_attempted:
            raise CaptureRefused("X-3 is attempted exactly once")
        self._x3_attempted = True
        last = self._chain[-1]
        admitted = {published.name for published in self._chain}
        for entry, record in self._records:
            admitted.update({entry.name, record.stdout.name, record.stderr.name})
        unadmitted = tuple(
            UnadmittedObject(name=name, object_type=ObjectType.REGULAR)
            for name, kind in sorted(self._store.known_objects.items())
            if name not in admitted and name not in SUBDIRECTORIES and kind is ObjectType.REGULAR
        )
        final = IndexState(
            pass_id=self._request.pass_id,
            capture_root=self._request.capture_root,
            tool_sha256=self._request.tool_sha256,
            state_number=last.state.state_number + 1,
            previous_state_sha256=last.sha256,
            status=FINAL,
            records=last.state.records,
            terminal=terminal,
            subdirectories=tuple(sorted(SUBDIRECTORIES)),
            unadmitted=unadmitted,
        )
        common = dict(
            terminal=terminal,
            admitted_records=len(self._records),
            subdirectories=tuple(sorted(SUBDIRECTORIES)),
            unadmitted=unadmitted,
            x4_validity=X4_INCONCLUSIVE,
            x4_reason="not-evaluated",
        )
        try:
            digest = self._store.publish(final.name, final.to_bytes(), stages=FINAL_STAGES)
        except CaptureInterrupted:
            # §9.5.3 step 3: an interruption during the attempt is its failure.
            # Recorded in memory only; nothing further is called.
            self._state = SessionState.INTERRUPTED
            self._outcome = FinalizationOutcome(
                x3_outcome=X3_FAILED,
                x3_failure_stage=FINAL_STAGES.create.split(":")[0],
                x3_failure_classification="interrupted",
                final_state=final.name,
                final_state_sha256=None,
                final_name_present=final.name in self._store.known_objects,
                **{**common, "x4_reason": "no-admissible-final-state"},  # type: ignore[arg-type]
            )
            raise
        except StoreFailure as failure:
            return FinalizationOutcome(
                x3_outcome=X3_FAILED,
                x3_failure_stage=failure.stage,
                x3_failure_classification=failure.classification,
                final_state=final.name,
                final_state_sha256=None,
                final_name_present=final.name in self._store.known_objects,
                **common,  # type: ignore[arg-type]
            )
        return FinalizationOutcome(
            x3_outcome=X3_SUCCEEDED,
            x3_failure_stage=None,
            x3_failure_classification=None,
            final_state=final.name,
            final_state_sha256=digest,
            final_name_present=True,
            **common,  # type: ignore[arg-type]
        )

    def _apply_x4(self, outcome: FinalizationOutcome) -> FinalizationOutcome:
        if outcome.x3_outcome != X3_SUCCEEDED:
            return _replace_x4(outcome, X4_INCONCLUSIVE, "no-admissible-final-state")
        assert outcome.final_state is not None and outcome.final_state_sha256 is not None
        result = verify_final_state(
            self._verifier_filesystem,
            capture_root=self._request.capture_root,
            final_state=outcome.final_state,
            final_sha256=outcome.final_state_sha256,
            pass_id=self._request.pass_id,
        )
        if result.passed:
            return _replace_x4(outcome, X4_VALID, "valid")
        return _replace_x4(outcome, X4_INCONCLUSIVE, result.reason)

    def _not_made(self, reason: str) -> FinalizationOutcome:
        return FinalizationOutcome(
            x3_outcome=X3_NOT_MADE,
            x3_failure_stage=None,
            x3_failure_classification=reason,
            terminal=None,
            final_state=None,
            final_state_sha256=None,
            final_name_present=False,
            x4_validity=X4_INCONCLUSIVE,
            x4_reason=reason,
            admitted_records=len(self._records),
            subdirectories=(),
            unadmitted=(),
        )

    # -- internals -------------------------------------------------------------

    def _require(self, state: SessionState, message: str) -> None:
        if self._state is SessionState.INTERRUPTED:
            raise CaptureRefused(
                "the mechanism was interrupted: no command and no X-3 attempt is made, "
                "before or after recovery (C-15)"
            )
        if self._state is not state:
            raise CaptureRefused(f"session is {self._state.value}: {message}")

    def _close_quietly(self, *groups: dict[str, int]) -> None:
        for group in groups:
            for fd in group.values():
                try:
                    self._store.filesystem.close(fd, stage=CLEANUP_STAGE)
                except (OSError, ValueError):
                    pass
            group.clear()


def _replace_x4(outcome: FinalizationOutcome, validity: str, reason: str) -> FinalizationOutcome:
    return FinalizationOutcome(
        x3_outcome=outcome.x3_outcome,
        x3_failure_stage=outcome.x3_failure_stage,
        x3_failure_classification=outcome.x3_failure_classification,
        terminal=outcome.terminal,
        final_state=outcome.final_state,
        final_state_sha256=outcome.final_state_sha256,
        final_name_present=outcome.final_name_present,
        x4_validity=validity,
        x4_reason=reason,
        admitted_records=outcome.admitted_records,
        subdirectories=outcome.subdirectories,
        unadmitted=outcome.unadmitted,
    )


def create_capture_session(
    request: GenesisRequest,
    *,
    filesystem: CaptureFilesystem,
    launcher: ProcessLauncher,
    clock: UtcClock,
    verifier_filesystem: ReadOnlyFilesystem | None = None,
) -> CaptureSession:
    """X-1: create the pass's root exclusively and publish its genesis state.

    The request is validated before any filesystem call. A storage failure
    returns a session in `NO_GENESIS`, which runs no command and makes no X-3
    attempt. An interruption propagates and leaves nothing to finalize.
    """
    require_identifier(request.pass_id, "pass_id")
    require_sha256(request.tool_sha256, "tool_sha256")
    parse_capture_root(request.capture_root)
    session = CaptureSession(
        request=request,
        store=CaptureRootStore(filesystem=filesystem, capture_root=request.capture_root),
        launcher=launcher,
        clock=clock,
        verifier_filesystem=(
            verifier_filesystem if verifier_filesystem is not None else PosixReadOnlyFilesystem()
        ),
    )
    session._genesis()
    return session


__all__ = [
    "ACT_STAGES",
    "LAUNCH_STAGE",
    "REQUEST_STAGE",
    "ActFailure",
    "ActOutcome",
    "ActRequest",
    "CaptureRefused",
    "CaptureSession",
    "FinalizationOutcome",
    "GenesisRequest",
    "ProcessLauncher",
    "SessionState",
    "SystemUtcClock",
    "UtcClock",
    "create_capture_session",
]
