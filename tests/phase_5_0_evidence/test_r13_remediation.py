"""R13's five findings, each with the reproduction that found it.

Every test here drives the real generated plan across an **injected** boundary.
Nothing starts a process, opens a socket, reads an account database or touches a
file outside pytest's own `tmp_path`; `test_no_execution.py` scans this file
along with every other `*.py` in the directory.

The boundary is stateful. R13's first two findings are about what cleanup
**does to objects**, and a fake that only records calls cannot tell a run that
deleted somebody's group from one that did not — the review's own reproduction
had to say *"these are requested commands observed at a fake boundary, not real
deletions"*. `FakeHost` therefore keeps a set of objects, applies each command to
it, and answers from it, so the assertions are about what is on the host at the
end rather than about which vectors were requested.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import capability, case_runtime
from tools.phase_5_0_evidence.approved_target import CONFIRMATION_TOKEN
from tools.phase_5_0_evidence.capture import CapturePolicy, sanitize
from tools.phase_5_0_evidence.case_runtime import (
    CASE_PROGRAM_SOURCE_PATH,
    INTERPRETER_PATH,
)
from tools.phase_5_0_evidence.journal import (
    RECOVERY_PROCEDURE as RESIDUE_RECOVERY_PROCEDURE,
)
from tools.phase_5_0_evidence.cleanup import (
    NOT_ATTEMPTED,
    NOT_OWNED,
    OWNERSHIP_WITHDRAWN,
    RECOVERY_INPUT_RETAINED,
    RECOVERY_PROCEDURE,
    CleanupStepKind,
)
from tools.phase_5_0_evidence.concrete_plan import (
    COORDINATOR_ROLE,
    TRANSIENT_UNIT,
    ConcretePlan,
    UnresolvedStep,
    build_concrete_plan,
)
from tools.phase_5_0_evidence.execution.artifact import (
    CANONICAL_CONFIGURATION_RECOVERY,
    CANONICAL_RESIDUE_RECOVERY,
    CLEANUP_FIELDS,
    CONFIGURATION_PROCEDURE_NOT_CANONICAL,
    CONFIGURATION_PROCEDURE_WITHOUT_RETENTION,
    DOCUMENT_FIELDS,
    DOCUMENT_TYPE,
    NOT_ADMISSIBLE,
    NOT_THE_DOCUMENT_WRITTEN,
    RESIDUE_PROCEDURE_MALFORMED,
    RESIDUE_PROCEDURE_NOT_CANONICAL,
    RESIDUE_PROCEDURE_WITHOUT_RESIDUE,
    RUN_RECORD_SCHEMA_VERSION,
    RunRecordRefused,
    build_run_record,
    validate_run_record,
    write_run_record,
)
from tools.phase_5_0_evidence.execution import artifact as artifact_module
from tools.phase_5_0_evidence.execution.boundary import (
    CommandResult,
    IdentityAbsent,
)
from tools.phase_5_0_evidence.execution.executor import (
    EFFECT_IDENTITY_MISMATCH,
    EFFECT_IDENTITY_NOT_RECORDED,
    EFFECT_OBJECT_ABSENT,
    EffectRefused,
    ExecutingRunner,
    ExecutorRefused,
)
from tools.phase_5_0_evidence.execution.materializer import (
    RESTORATION_BARRIERS,
    MaterializationResult,
    RestorationOutcome,
)
from tools.phase_5_0_evidence.execution.recovery_store import (
    BARRIER_ORDER,
    StorePublication,
)
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    RecordingEffects,
    cleanup_observations_for,
    bound_argv,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}
REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"
ROOT = "/var/lib/fb-evidence-p5-0"
EVIDENCE_DATABASE = "fb_evidence_p5_0"

#: The host identities §2.12.2 records as already present. The run reads them and
#: never creates or modifies them, so `FakeHost` starts with them and the
#: ownership baseline is asked about them nowhere.
#: **R14, EH-R14-1.** The two catalog listings the ownership baselines read, and
#: the object prefix each one lists. The vectors carry no name, so the fake keys
#: on the whole reviewed command rather than on an argument.
CATALOG_QUERIES = {
    "SELECT datname FROM pg_database": "database:",
    "SELECT rolname FROM pg_roles": "role:",
}

#: What each catalog carries on any PostgreSQL instance, whatever this run has
#: done. `postgres` is in both, and it is the **control** both baselines compare:
#: a listing without it was not read, which is *unknown* and never *absent*.
ALWAYS_PRESENT = {
    "SELECT datname FROM pg_database": frozenset(
        {"postgres", "template0", "template1"}
    ),
    "SELECT rolname FROM pg_roles": frozenset(
        {"postgres", "pg_monitor", "pg_read_all_data"}
    ),
}

PRE_EXISTING = frozenset(
    {
        "group:discordbot",
        "group:sudo",
        "account:discordbot",
        "account:freedomweb",
        "account:foundry",
        "account:postgres",
    }
)


@pytest.fixture(autouse=True)
def _reviewed_target_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_REAL_PATH", REVIEWED_INTERPRETER_REAL_PATH
    )
    supply_reviewed_e7_facts(monkeypatch)


PLAN = runnable_plan()


@dataclass
class FakeIdentityLookup:
    accounts: dict = field(
        default_factory=lambda: {
            "freedomcoord": (5001, 5001),
            "freedomsheet": (5002, 5002),
            "fbprobe": (5003, 5003),
            # `postgres` is **pre-existing**, not disposable. The reviewed
            # restoration `fchown`s the configuration back to it — r6 §2.4 —
            # so the injected NSS boundary has to answer for it. The numbers
            # are this file's, like every other one here.
            "postgres": (900, 900),
        }
    )
    groups: dict = field(
        default_factory=lambda: {
            "freedomcoord": 5001,
            "freedomsheet": 5002,
            "fbprobe": 5003,
            "postgres": 900,
            "freedomjournal": 5004,
        }
    )

    def account(self, name: str) -> tuple[int, int]:
        if name not in self.accounts:
            raise IdentityAbsent(name)
        return self.accounts[name]

    def group_id(self, name: str) -> int:
        if name not in self.groups:
            raise IdentityAbsent(name)
        return self.groups[name]

    def supplementary_group_names(self, name, primary_gid):  # pragma: no cover
        raise AssertionError("the executor resolves ids, never memberships")

    def effective_ids(self) -> tuple[int, int]:  # pragma: no cover
        return 0, 0


@dataclass(frozen=True)
class Consumption:
    """One effect, and the **object or bytes** it actually acted on.

    **Project-review finding PR-20260909-R2-1/2.** A call log records that
    `install` was asked to copy a pathname. It cannot say whether the bytes it
    copied were the ones this run wrote, and a test that asserts only the
    command name cannot distinguish an original from a replacement. This record
    carries the identity of the object the fake resolved the pathname to and,
    where the effect reads or writes a file, the bytes it moved — so an
    assertion can name what an effect would consume rather than that it ran.
    """

    step_id: str
    action: str
    path: str
    identity: int | None
    content: bytes | None = None


#: The two live PostgreSQL configuration files the run captures before it
#: changes them, with the bytes that are on the host before the run starts. They
#: are the recovery inputs, so a reproduction has to be able to say which bytes
#: reached the live file at the end.
LIVE_CONFIG_FILES = {
    "/etc/postgresql/16/main/pg_hba.conf": b"# original pg_hba.conf\n",
    "/etc/postgresql/16/main/pg_ident.conf": b"# original pg_ident.conf\n",
}


@dataclass
class FakeMaterializer:
    applied: bool = True
    host: "FakeHost | None" = None

    def materialize(self, *, step_id, destination, content, sha256, owner, group, mode):
        if self.applied and self.host is not None:
            self.host.objects.add(f"path:{destination}")
            # The materializer replaces the live file's bytes, which is what
            # makes the capture taken before it the only route back.
            self.host.write(destination, content, step_id=step_id, action="materialize")
        return (
            MaterializationResult(applied=True)
            if self.applied
            else MaterializationResult(applied=False, failure="materializer-not-armed")
        )


@dataclass
class FakeHost:
    """A host with a set of objects, and commands that change it.

    Only the vectors this plan actually uses are interpreted; everything else
    answers from `scripted`, which is the reviewed satisfying result. An
    unrecognised **mutating or removing** vector is an error rather than a
    silent success, so a reversal added later cannot pass this suite by being
    ignored.
    """

    plan: ConcretePlan
    objects: set[str] = field(default_factory=set)
    scripted: dict = field(default_factory=dict)
    overrides: dict = field(default_factory=dict)
    calls: list = field(default_factory=list)
    vectors: list = field(default_factory=list)
    #: **PR-20260909-R2-1/2.** Path key → the identity of the object currently at
    #: that name, and the bytes currently in it. A *set of names* cannot model a
    #: substitution: the name is still there afterwards, which is exactly the
    #: property the finding is about. These two make an object distinguishable
    #: from its replacement.
    identities: dict = field(default_factory=dict)
    contents: dict = field(default_factory=dict)
    #: What each effect actually acted on, in order — `Consumption` records.
    consumed: list = field(default_factory=list)
    #: `step_id` → a callable applied to this host **immediately before** that
    #: step runs. This is the injection point: a substitution performed here
    #: happens between the previous step's effect and this one's, which is where
    #: the review asks the replacement to be injected.
    injections: dict = field(default_factory=dict)
    _next_identity: int = 8000000

    def __post_init__(self) -> None:
        # Identity and bytes only. These two files are on the host before the
        # run and the run never creates them, so they are deliberately **not**
        # added to `objects`: that set models what this run made and would be
        # entitled to remove, and EH-R13-1 is about not conflating the two.
        for path, content in LIVE_CONFIG_FILES.items():
            key = f"path:{path}"
            self.identities.setdefault(key, self._allocate())
            self.contents.setdefault(key, content)
        # The identities §2.12.2 records as **existing** on the host. The run
        # never creates them, never modifies them and reads three of them back,
        # so a host without them is not the reviewed target.
        self.objects.update(PRE_EXISTING)
        for step in self.plan.steps:
            status = 1 if step.refusal_required else step.satisfying_statuses[0]
            self.scripted.setdefault(
                step.step_id,
                CommandResult(
                    exit_status=status,
                    timed_out=False,
                    observations=observations_for(step, bound_argv(step), SOURCES),
                ),
            )
        for step in self.plan.cleanup_plan.steps:
            status = 1 if step.refusal_required else step.satisfying_statuses[0]
            self.scripted.setdefault(
                step.step_id, CommandResult(exit_status=status, timed_out=False)
            )

    #: **R16, conflict C-8.** The device and inode this fake gives the directory
    #: `mkroot` creates. Two numbers, stated here, so `statroot` reports the same
    #: pair and the executor's comparison is exercised against agreement — and so
    #: a test that wants the replaced-path case changes exactly one of them.
    root_device: int = 66306
    root_inode: int = 1441793

    # -- the object model -------------------------------------------------

    def _root_identity(self, verb: str, *, created: bool):
        pairs = [
            ("errno", "none"),
            ("result", "returned"),
            ("root_device", str(self.root_device)),
            ("root_inode", str(self.root_inode)),
            ("verb", verb),
        ]
        if created:
            pairs.append(("created", "yes"))
        return tuple(sorted(pairs))

    def has(self, key: str) -> bool:
        return key in self.objects

    # -- object identity and content — PR-20260909-R2-1/2 ------------------

    def _allocate(self) -> int:
        """A fresh inode number. The kernel allocates these; so does this."""
        self._next_identity += 1
        return self._next_identity

    def identity_of(self, path: str) -> int | None:
        """The identity of the object currently at `path`, or `None`."""
        return self.identities.get(f"path:{path}")

    def content_of(self, path: str) -> bytes | None:
        return self.contents.get(f"path:{path}")

    def write(
        self, path: str, content: bytes, *, step_id: str, action: str
    ) -> None:
        """Put `content` at `path`, allocating an identity if it is new."""
        key = f"path:{path}"
        self.objects.add(key)
        identity = self.identities.setdefault(key, self._allocate())
        self.contents[key] = content
        self.consumed.append(
            Consumption(step_id, action, path, identity, content)
        )

    def substitute(self, path: str, *, content: bytes | None = None) -> int:
        """Replace the object at `path` with a **different** one of the same name.

        The name stays, the parent stays, and the identity changes — which is
        what `unlink` followed by a fresh creation does, and what a
        `freedomsheet` member may do in the two `0770` directories the plan
        creates. Returns the replacement's identity so a test can assert against
        it by value rather than by "not the original".
        """
        key = f"path:{path}"
        replacement = self._allocate()
        self.objects.add(key)
        self.identities[key] = replacement
        if content is not None:
            self.contents[key] = content
        return replacement

    def substitute_root(self) -> int:
        """Replace the whole disposable root, leaving its pathname resolvable.

        `statroot` reads `root_device`/`root_inode` when it is asked, so moving
        the inode here is the substitution: every later reading reports the
        replacement, and the identity `mkroot` recorded no longer matches.
        """
        self.root_inode += 1
        key = f"path:{self.plan.target.root_path}"
        self.objects.add(key)
        self.identities[key] = self.root_inode
        return self.root_inode

    def _create(self, key: str) -> int:
        if key in self.objects:
            return 9
        self.objects.add(key)
        return 0

    def _remove(self, key: str, absent_status: int) -> int:
        if key not in self.objects:
            return absent_status
        self.objects.discard(key)
        return 0

    def _interpret(self, argv: tuple[str, ...], step_id: str) -> CommandResult | None:
        executable, rest = argv[0], list(argv[1:])
        if executable == "/usr/bin/getent":
            kind = "group" if rest[0] == "group" else "account"
            return CommandResult(
                exit_status=0 if self.has(f"{kind}:{rest[1]}") else 2, timed_out=False
            )
        if executable == "/usr/bin/stat" and rest[0].startswith("--format=%F"):
            return CommandResult(
                exit_status=0 if self.has(f"path:{rest[1]}") else 1, timed_out=False
            )
        if executable == "/usr/sbin/groupadd":
            return CommandResult(exit_status=self._create(f"group:{rest[-1]}"), timed_out=False)
        if executable == "/usr/sbin/useradd":
            return CommandResult(exit_status=self._create(f"account:{rest[-1]}"), timed_out=False)
        if executable == "/usr/sbin/gpasswd":
            key = f"membership:{rest[1]}@{rest[2]}"
            if rest[0] == "--add":
                self.objects.add(key)
                return CommandResult(exit_status=0, timed_out=False)
            return CommandResult(exit_status=self._remove(key, 3), timed_out=False)
        if executable == "/usr/sbin/groupdel":
            return CommandResult(exit_status=self._remove(f"group:{rest[0]}", 6), timed_out=False)
        if executable == "/usr/sbin/userdel":
            return CommandResult(exit_status=self._remove(f"account:{rest[0]}", 6), timed_out=False)
        if executable == INTERPRETER_PATH and argv[3] == CASE_PROGRAM_SOURCE_PATH:
            # **R16, conflict C-8.** The two bootstrap verbs, modelled as the
            # kernel calls they are rather than as a scripted status.
            #
            # `mkroot` is `mkdir(2)`: it creates the directory or reports EEXIST,
            # and the identity it reports is the identity of the object it made.
            # `statroot` re-reads that identity. Modelling either as *"the read
            # failed, so it is absent"* would be the assumption EH-R14-1 is
            # about, one level along.
            verb, path = argv[4], f"path:{argv[5]}"
            if verb == "mkroot":
                if self.has(path):
                    return CommandResult(
                        exit_status=15,
                        timed_out=False,
                        observations=(
                            ("errno", "EEXIST"),
                            ("result", "refused"),
                            ("verb", "mkroot"),
                        ),
                    )
                self.objects.add(path)
                self.identities[path] = self.root_inode
                return CommandResult(
                    exit_status=0,
                    timed_out=False,
                    observations=self._root_identity("mkroot", created=True),
                )
            if not self.has(path):
                return CommandResult(
                    exit_status=16,
                    timed_out=False,
                    observations=(
                        ("errno", "ENOENT"),
                        ("result", "refused"),
                        ("verb", "statroot"),
                    ),
                )
            return CommandResult(
                exit_status=0,
                timed_out=False,
                observations=self._root_identity("statroot", created=False),
            )
        if executable == "/usr/bin/install":
            destination = rest[-1]
            # **PR-20260909-R2-2.** `install` copies **bytes**, and which bytes
            # it copies is decided when it opens the source — not when anything
            # checked the source. The fake therefore reads the source's current
            # content at this moment, so a substitution injected before this
            # step is the content that lands at the destination.
            source = rest[-2] if "--directory" not in rest else ""
            if source:
                content = self.contents.get(
                    f"path:{source}", f"# unmodelled source {source}\n".encode()
                )
                self.consumed.append(
                    Consumption(
                        step_id,
                        "install-source",
                        source,
                        self.identities.get(f"path:{source}"),
                        content,
                    )
                )
                self.write(
                    destination, content, step_id=step_id, action="install"
                )
            else:
                key = f"path:{destination}"
                self.objects.add(key)
                self.identities.setdefault(key, self._allocate())
                self.consumed.append(
                    Consumption(
                        step_id, "install-directory", destination,
                        self.identities[key],
                    )
                )
            return CommandResult(exit_status=0, timed_out=False)
        if executable == "/usr/bin/rm":
            path = rest[-1]
            key = f"path:{path}"
            self.consumed.append(
                Consumption(
                    step_id, "rm", path,
                    self.identities.get(key), self.contents.get(key),
                )
            )
            self.objects.discard(key)
            self.identities.pop(key, None)
            self.contents.pop(key, None)
            return CommandResult(exit_status=0, timed_out=False)
        if executable == "/usr/bin/rmdir":
            path = rest[-1]
            key = f"path:{path}"
            status = self._remove(key, 1)
            self.consumed.append(
                Consumption(step_id, "rmdir", path, self.identities.get(key))
            )
            if status == 0:
                self.identities.pop(key, None)
            return CommandResult(exit_status=status, timed_out=False)
        if executable == "/usr/bin/systemd-run":
            unit = next(
                argument[len("--unit=") :]
                for argument in rest
                if argument.startswith("--unit=")
            )
            self.objects.add(f"unit:{unit}")
            return None
        if executable == "/usr/bin/systemctl" and rest[0] == "stop":
            return CommandResult(exit_status=self._remove(f"unit:{rest[1]}", 5), timed_out=False)
        if executable == "/usr/bin/systemctl" and rest[0] == "show":
            state = "loaded" if self.has(f"unit:{rest[-1]}") else "not-found"
            if "--property=LoadState" in rest and len(rest) == 3:
                return CommandResult(
                    exit_status=0,
                    timed_out=False,
                    observations=(("LoadState", state),),
                )
            return None
        if executable == "/usr/bin/psql":
            command = argv[argv.index("--command") + 1]
            dbname = argv[argv.index("--dbname") + 1]
            if command == "SELECT 1" and "--username" not in argv:
                if dbname == "postgres":
                    return CommandResult(exit_status=0, timed_out=False)
                return CommandResult(
                    exit_status=0 if self.has(f"database:{dbname}") else 2,
                    timed_out=False,
                )
            if command in CATALOG_QUERIES:
                # **R14, EH-R14-1.** The catalog answers from the host's objects
                # and from the names every PostgreSQL instance carries. It is a
                # *listing*, not a lookup: the query names nothing, because the
                # reviewed grammar admits no string literal, so the fake returns
                # what is there and `capture` decides what that means. Modelling
                # it as a lookup — or as *"the read failed, so it is absent"* —
                # is the assumption the finding is about.
                names = ALWAYS_PRESENT[command] | {
                    key.split(":", 1)[1]
                    for key in self.objects
                    if key.startswith(CATALOG_QUERIES[command])
                }
                return CommandResult(
                    exit_status=0,
                    timed_out=False,
                    observations=sanitize(
                        CapturePolicy.CATALOG_MEMBERSHIP,
                        "\n".join(sorted(names)) + "\n",
                        catalog=step_named(self.plan, step_id).catalog_question,
                    ),
                )
            if command.startswith("SET ROLE "):
                role = command.split()[-1]
                return CommandResult(
                    exit_status=0 if self.has(f"role:{role}") else 3, timed_out=False
                )
            if command.startswith("CREATE DATABASE "):
                self.objects.add(f"database:{command.split()[-1]}")
                return CommandResult(exit_status=0, timed_out=False)
            if command.startswith("CREATE ROLE "):
                self.objects.add(f"role:{command.split()[2]}")
                return CommandResult(exit_status=0, timed_out=False)
            if command.startswith("DROP DATABASE IF EXISTS "):
                self.objects.discard(f"database:{command.split()[-1]}")
                return CommandResult(exit_status=0, timed_out=False)
            if command.startswith("DROP ROLE IF EXISTS "):
                self.objects.discard(f"role:{command.split()[-1]}")
                return CommandResult(exit_status=0, timed_out=False)
            return None
        return None

    def run(
        self,
        *,
        step_id,
        argv,
        run_as,
        capture,
        timeout_seconds,
        catalog=None,
        descriptors=(),
    ):
        # **PR-20260909-R2-1.** The injection point, applied before the step's
        # own effect, so a scripted substitution happens in the interval
        # between the previous step and this one rather than at set-up time.
        injection = self.injections.pop(step_id, None)
        if injection is not None:
            injection(self)
        self.calls.append(step_id)
        self.vectors.append(tuple(argv))
        if step_id in self.overrides:
            override = self.overrides[step_id]
            if isinstance(override, BaseException):
                raise override
            return override
        interpreted = self._interpret(tuple(argv), step_id)
        if interpreted is not None:
            scripted = self.scripted.get(step_id)
            if scripted is not None and scripted.observations and not (
                interpreted.observations
            ):
                return CommandResult(
                    exit_status=interpreted.exit_status,
                    timed_out=False,
                    observations=scripted.observations,
                )
            return interpreted
        return self.scripted[step_id]


@dataclass
class HostEffects:
    """r6 §1.4's effect issuer, over the same fake host — **and bound like it**.

    `harness_fixtures.RecordingEffects` records and writes nothing, which is
    right for a module that only needs the run to get past an effect step. This
    module models the host, so its issuer has to change it — and, more
    importantly, has to carry the **binding** the real issuer carries, or every
    reproduction in `test_r16_1_ownership_reproduction.py` would be a statement
    about a double that was more permissive than the thing it stands for.

    Two properties are modelled and both are load-bearing:

    * **the parent is held, not re-resolved.** Every effect is issued relative
      to the descriptor the creating step opened. The fake spells that as: the
      identity the parent had when it was created is remembered, and an effect
      whose parent has since been replaced reaches **the object the descriptor
      holds** rather than what the pathname now resolves to; and
    * **the object is the one the creating step recorded.** A flag, a removal
      and a restoration each compare the current identity with the recorded one
      and refuse on anything but equality — PR-20260913-LABI-2.

    What it does **not** model, because r6 §1.4.4 says the mechanism does not
    cover it either: in-place mutation of a file whose inode is unchanged.
    """

    host: FakeHost
    refuse: set = field(default_factory=set)
    #: `path` → the identity the creating effect recorded for it.
    recorded: dict = field(default_factory=dict)
    #: The **independent** recovery store: destination → the captured bytes and
    #: the identity they were read from. It is a separate dictionary from the
    #: host's objects on purpose — that separation is r6 §2.2's whole point.
    store: dict = field(default_factory=dict)
    issued: list = field(default_factory=list)
    steps: list = field(default_factory=list)
    #: Set when the last publication crossed every barrier.
    published: bool = False

    # -- the paths an effect names -------------------------------------------

    @property
    def root(self) -> str:
        return self.host.plan.target.root_path

    def _path(self, directory_role: str, name: str) -> str:
        if directory_role == "root":
            return f"{self.root}/{name}"
        return f"{self.root}/{directory_role}/{name}"

    def _parent(self, directory_role: str) -> str:
        return self.root if directory_role == "root" else f"{self.root}/{directory_role}"

    # -- what the executor calls ---------------------------------------------

    def declared_transfer(self) -> tuple:
        return ()

    def create_directory_object(
        self, *, parent_role, name, role="", mode=0o700, step_id=""
    ):
        path = self._path(parent_role, name)
        self._refuse_if_asked(step_id, "create_directory")
        if self.host.has(f"path:{path}"):
            raise EffectRefused(
                "exclusive creation refused: an entry is already at that name."
            )
        identity = self.host._allocate()
        self.host.objects.add(f"path:{path}")
        self.host.identities[f"path:{path}"] = identity
        self.recorded[path] = identity
        self._note(step_id, "create-directory", path, identity)
        return str(identity)

    def create_object(
        self,
        *,
        directory_role,
        name,
        content=b"",
        uid=None,
        gid=None,
        mode=0o640,
        step_id="",
    ):
        path = self._path(directory_role, name)
        self._refuse_if_asked(step_id, "create_object")
        if self.host.has(f"path:{path}"):
            raise EffectRefused(
                "exclusive creation refused: an entry is already at that name."
            )
        self.host.write(path, content, step_id=step_id, action="create-object")
        identity = self.host.identity_of(path)
        self.recorded[path] = identity
        return str(identity)

    def install_case_program(
        self,
        *,
        content,
        sha256,
        directory_role="bin",
        name="case-program",
        temporary=".case-program.tmp",
        uid=None,
        gid=None,
        mode=0o555,
        step_id="",
    ):
        if hashlib.sha256(content).hexdigest() != sha256:
            raise EffectRefused("the bytes are not the reviewed bytes.")
        path = self._path(directory_role, name)
        self._refuse_if_asked(step_id, "install_payload")
        if self.host.has(f"path:{path}"):
            raise EffectRefused("exclusive publication refused.")
        self.host.write(path, content, step_id=step_id, action="install-payload")
        identity = self.host.identity_of(path)
        self.recorded[path] = identity
        return str(identity)

    def set_inode_flags(self, *, directory_role, name, add, step_id=""):
        self._bound(directory_role, name, step_id, "set_flag")

    def clear_inode_flags(self, *, directory_role, name, remove, step_id=""):
        self._bound(directory_role, name, step_id, "clear_flag")

    def remove_object(self, *, directory_role, name, is_directory=False, step_id=""):
        path = self._bound(directory_role, name, step_id, "remove_object")
        key = f"path:{path}"
        self.host.objects.discard(key)
        self.host.identities.pop(key, None)
        self.host.contents.pop(key, None)
        self.recorded.pop(path, None)
        return path

    def publish_recovery_basis(
        self,
        *,
        run_id,
        reservation_id,
        captured_by,
        capture_set,
        configuration_role,
        evidence_role="",
        step_id="",
    ):
        self._refuse_if_asked(step_id, "capture_configuration")
        for component in capture_set.components:
            destination = capture_set.destination_for(component)
            content = self.host.content_of(destination)
            if content is None:
                raise EffectRefused("the configuration file could not be read.")
            identity = self.host.identity_of(destination)
            # The digest is over the **buffer** the read produced, and the store
            # is outside the host's object set — r6 §2.2.
            self.store[destination] = (content, identity)
            self._note(step_id, "capture-source", destination, identity, content)
        self.published = True
        if evidence_role:
            # r6 §2.5's retained evidence copy, written **from the store** after
            # the basis is durable. It is not the basis, and the fake keeps the
            # two apart for the same reason the mechanism does.
            for component in capture_set.components:
                destination = capture_set.destination_for(component)
                content, _identity = self.store[destination]
                self.create_object(
                    directory_role=evidence_role,
                    name=component,
                    content=content,
                    mode=0o600,
                    step_id=step_id,
                )
        return StorePublication(
            published=True,
            mutation_permitted=True,
            barriers_crossed=BARRIER_ORDER,
            run_directory_name=run_id,
        )

    def restore_configuration(
        self,
        *,
        run_id,
        configuration_role,
        destination_directory,
        owner_uid,
        owner_gid,
        mode=0o640,
        step_id="",
    ):
        self._refuse_if_asked(step_id, "restore_configuration")
        if not self.store:
            raise EffectRefused("the independent store holds no usable basis.")
        renamed = []
        for destination, (content, identity) in sorted(self.store.items()):
            self._note(step_id, "restore-source", destination, identity, content)
            self.host.write(
                destination, content, step_id=step_id, action="restore"
            )
            renamed.append(destination)
        return RestorationOutcome(
            renamed=tuple(renamed),
            durable=True,
            barriers_crossed=RESTORATION_BARRIERS,
        )

    # -- internals ------------------------------------------------------------

    def _refuse_if_asked(self, step_id: str, kind: str) -> None:
        """The injection point and the refusal, in `FakeHost.run`'s own order.

        A substitution scripted for an effect step has to be applied in the
        interval immediately before that effect, exactly as one scripted for a
        command step is applied immediately before the process starts. Doing it
        here rather than at set-up time is what makes an injected replacement a
        replacement rather than a differently-built fixture.
        """
        injection = self.host.injections.pop(step_id, None)
        if injection is not None:
            injection(self.host)
        if step_id and step_id in self.refuse:
            raise EffectRefused(f"the fake issuer was asked to refuse {kind}.")

    def _note(self, step_id, action, path, identity, content=None) -> None:
        self.issued.append((action, path, identity))
        self.steps.append(step_id)
        self.host.consumed.append(
            Consumption(step_id, action, path, identity, content)
        )

    def _bound(self, directory_role: str, name: str, step_id: str, kind: str) -> str:
        """The pre-check: a mandatory record, a present object, and equality."""
        self._refuse_if_asked(step_id, kind)
        path = self._path(directory_role, name)
        recorded = self.recorded.get(path)
        if recorded is None:
            raise EffectRefused(
                "no creating-step identity was recorded for this entry.",
                classification=EFFECT_IDENTITY_NOT_RECORDED,
            )
        found = self.host.identity_of(path)
        if found is None:
            raise EffectRefused(
                "the recorded object is not at that name.",
                classification=EFFECT_OBJECT_ABSENT,
            )
        if found != recorded:
            raise EffectRefused(
                "the object at that name is not the object this run recorded.",
                classification=EFFECT_IDENTITY_MISMATCH,
            )
        self._note(step_id, kind.replace("_", "-"), path, found)
        return path


def _is_effect(plan: ConcretePlan, step_id: str) -> bool:
    """Whether the named step — in either half of the plan — is an effect."""
    return any(
        step.step_id == step_id and step.is_effect
        for step in (*plan.steps, *plan.cleanup_plan.steps)
    )


def runner(plan: ConcretePlan, host: FakeHost, **overrides) -> ExecutingRunner:
    keywords = dict(
        plan=plan,
        boundary=host,
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=FakeMaterializer(host=host),
        identity_lookup=FakeIdentityLookup(),
        effects=HostEffects(host=host),
    )
    keywords.update(overrides)
    return ExecutingRunner(**keywords)


def step_named(plan: ConcretePlan, step_id: str):
    return next(step for step in plan.steps if step.step_id == step_id)


def creation_step_for(plan: ConcretePlan, mutation_id: str) -> str:
    return next(
        step.step_id for step in plan.steps if mutation_id in step.mutation_ids
    )


# ---------------------------------------------------------------------------
# EH-R13-1 — cleanup can delete pre-existing and unreached objects
# ---------------------------------------------------------------------------


def test_the_reviewed_reproduction_deletes_nothing_it_did_not_create() -> None:
    """The review's own synthetic reproduction, against a host with objects.

    `B2-02` — `groupadd --system freedomcoord` — returns 9. R12 stopped there,
    then requested `groupdel freedomcoord`, the other declared group deletions
    and `DROP DATABASE IF EXISTS fb_evidence_p5_0`, none of whose objects the run
    had created and one of which no step had even reached.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    # `freedomcoord` exists already, and so does a database of the same name as
    # the evidence one. Neither is this run's.
    host.objects.update({"group:freedomcoord", f"database:{EVIDENCE_DATABASE}"})
    before = set(host.objects)

    outcome = runner(plan, host).execute()

    # The run stops at the *baseline*, before any mutation: the group is there,
    # so `R-B-G-freedomcoord` never observes the absence it needs.
    assert outcome.stopped_at == "R-B-G-freedomcoord"
    assert outcome.mutations_reached == ()
    assert outcome.cleanup_steps == ()
    assert host.objects == before
    assert not outcome.artifact_admissible


def test_an_already_exists_creation_withdraws_ownership_of_that_object() -> None:
    """The case filtering by attempted mutation id does not cover.

    The baseline passes — the group really is absent when it is checked — and
    the `groupadd` then reports exit 9 anyway, which is what a race, a parallel
    operator or a mistaken host looks like. The mutation **was** attempted, so an
    attempt filter would delete the group; ownership is withdrawn instead.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    step_id = creation_step_for(plan, "os_group:freedomcoord")
    host.overrides[step_id] = CommandResult(exit_status=9, timed_out=False)

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id
    assert "os_group:freedomcoord" in outcome.mutations_reached
    skipped = {item.step_id: item for item in outcome.cleanup_skipped}
    withdrawn = [
        item for item in skipped.values() if item.reason == OWNERSHIP_WITHDRAWN
    ]
    assert [item.subject for item in withdrawn] == ["freedomcoord"]
    # And no `groupdel freedomcoord` was requested at all.
    assert not any(
        vector[0] == "/usr/sbin/groupdel" and vector[-1] == "freedomcoord"
        for vector in host.vectors
    )


def test_an_early_stop_reverses_only_what_it_reached() -> None:
    """The unreached half of the finding, asserted on the host's objects."""
    plan = runnable_plan()
    host = FakeHost(plan)
    step_id = creation_step_for(plan, "os_group:freedomsheet")
    host.overrides[step_id] = CommandResult(exit_status=1, timed_out=False)

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id
    # The group this run created is gone; the database no step reached was never
    # created and no `DROP DATABASE` was requested for it.
    assert not host.has("group:freedomjournal")
    assert not host.has(f"database:{EVIDENCE_DATABASE}")
    assert not any(
        "DROP DATABASE IF EXISTS" in argument
        for vector in host.vectors
        for argument in vector
    )
    reasons = {item.reason for item in outcome.cleanup_skipped}
    assert NOT_ATTEMPTED in reasons


def test_unreached_configuration_is_not_restored_or_reloaded() -> None:
    """*"Unreached PostgreSQL configuration must not be restored or reloaded
    merely because an OS-group creation was attempted."*"""
    plan = runnable_plan()
    host = FakeHost(plan)
    step_id = creation_step_for(plan, "os_group:freedomsheet")
    host.overrides[step_id] = CommandResult(exit_status=1, timed_out=False)

    outcome = runner(plan, host).execute()

    ran = {step.step_id for step in outcome.cleanup_steps}
    for step in plan.cleanup_plan.steps:
        if step.kind in (
            CleanupStepKind.RESTORE,
            CleanupStepKind.RELOAD,
            CleanupStepKind.VERIFY,
        ):
            assert step.step_id not in ran, step.step_id
    assert not any(
        "pg_reload_conf" in argument
        for vector in host.vectors
        for argument in vector
    )
    # And the outcome does not invent a configuration risk for a file this run
    # never touched.
    assert outcome.cleanup.configuration_risk == ()


@pytest.mark.parametrize(
    "existing,baseline_step",
    [
        ("group:freedomjournal", "R-02"),
        ("account:fbprobe", "R-B-A-fbprobe"),
        (f"path:{ROOT}", "R-B-ROOT"),
        (f"database:{EVIDENCE_DATABASE}", "R-B-DB"),
        (f"role:{COORDINATOR_ROLE}", "R-B-ROLE"),
        (f"unit:{TRANSIENT_UNIT}", "R-B-UNIT"),
    ],
)
def test_every_pre_existing_object_stops_the_run_and_survives(
    existing: str, baseline_step: str
) -> None:
    """One case per cleanup-subject class: accounts, groups, paths, the database,
    the role and the unit. Each is refused **without being deleted**."""
    plan = runnable_plan()
    host = FakeHost(plan)
    host.objects.add(existing)

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == baseline_step
    assert outcome.mutations_reached == ()
    assert host.has(existing)
    assert outcome.cleanup_steps == ()


def test_an_unknown_launch_outcome_is_still_reversed() -> None:
    """The conservative half is preserved: a mutation whose outcome is never
    learned is treated as potentially reached and is reversed."""
    plan = runnable_plan()
    host = FakeHost(plan)
    step_id = creation_step_for(plan, "os_group:freedomjournal")
    host.overrides[step_id] = OSError("the call raised")

    outcome = runner(plan, host).execute()

    assert "os_group:freedomjournal" in outcome.mutations_reached
    assert any(
        vector[0] == "/usr/sbin/groupdel" and vector[-1] == "freedomjournal"
        for vector in host.vectors
    )


def test_a_mutation_without_a_baseline_never_reaches_the_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ownership is checked before the change, not before the reversal.

    With the baseline step's satisfying status removed, the run reaches the
    creation with no ownership and stops **before** the command exists — so
    there is no object to decide about afterwards.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides["R-02"] = CommandResult(exit_status=7, timed_out=False)

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "R-02"
    assert not any(vector[0] == "/usr/sbin/groupadd" for vector in host.vectors)
    assert host.objects == set(PRE_EXISTING)


def test_the_generated_plan_gives_every_deleted_object_a_baseline() -> None:
    """Completeness, over the plan rather than over a run.

    A reversal that deletes something must have a claim behind it, and **R16**
    makes that two claims rather than one:

    * a **baseline** that proved its subject absent before anything changed —
      `getent`'s documented *key not found*, or a catalog listing the server
      returned with a control name in it; or
    * an **exclusive creation** that returned — conflict C-8. `mkdir(2)` either
      creates the directory or reports `EEXIST`, so a successful creation is
      itself the proof that nothing was there, with no window between the
      observation and the creation for an object to arrive in. It carries the
      objects **inside** the directory it made with it, because what `mkdir(2)`
      returns is empty.

    R14's third column — a declared blocker saying no baseline can — is gone,
    because the blocker it held is resolved. What the partition still rules out
    is the state that deletes whatever happened to be there: a reversal whose
    subject is neither proved absent nor created by this run.

    A **restore** must have none of them: it reinstalls a capture over a file
    that was there before the run, which is the opposite claim.
    """
    plan = build_concrete_plan()
    owned = {
        mutation_id
        for step in plan.steps
        for mutation_id in step.establishes_ownership_of
    }
    created = {
        mutation_id
        for step in plan.steps
        for mutation_id in (
            *step.establishes_ownership_by_creation,
            *step.establishes_ownership_of_contained,
        )
    }
    blocked = {
        mutation_id
        for item in plan.unresolved
        for mutation_id in item.blocks_mutation_ids
    }
    assert blocked == set()
    assert not (owned & created)
    for step in plan.cleanup_plan.steps:
        if step.kind is CleanupStepKind.REVERSAL:
            assert set(step.mutation_ids) <= owned | created, step.step_id
        elif step.kind is CleanupStepKind.RESTORE:
            assert not (set(step.mutation_ids) & (owned | created)), step.step_id


def test_an_attempted_but_unowned_mutation_is_still_refused_by_cleanup() -> None:
    """Defence in depth, asserted directly on the derivation.

    The executor refuses a mutation-bearing step whose subjects are not owned, so
    an attempted-but-unowned mutation should not arise from a run. The cleanup
    derivation refuses it anyway: if that gate were ever removed, the reversal
    would still not run, and the reason it did not would still be reported.
    """
    plan = build_concrete_plan()
    applicable = plan.cleanup_plan.applicable(
        attempted=["os_group:freedomjournal"], owned=[]
    )
    assert applicable.steps == ()
    reasons = {
        item.reason
        for item in applicable.skipped
        if item.subject == "freedomjournal"
    }
    assert reasons == {NOT_OWNED}


def test_a_baseline_step_performs_no_mutation() -> None:
    """A probe that ran after a change establishes nothing about what was there.

    **R16, conflict C-8** does not weaken this: `CommandStep` refuses a step that
    declares both `establishes_ownership_of` and a mutation, and refuses one that
    declares both a probe and an exclusive creation. The creation is a different
    claim made by a different field, and it is *because* it is the creation that
    it may be mutation-bearing.
    """
    plan = build_concrete_plan()
    for step in plan.steps:
        if step.establishes_ownership_of:
            assert not step.is_mutation_bearing, step.step_id
            assert step.mutation_ids == ()
            assert step.establishes_ownership_by_creation == (), step.step_id
    for step in plan.steps:
        if step.establishes_ownership_by_creation:
            assert step.is_mutation_bearing, step.step_id
            assert step.establishes_ownership_of == (), step.step_id


# ---------------------------------------------------------------------------
# EH-R13-2 — failed configuration recovery deletes its recovery inputs
# ---------------------------------------------------------------------------


def _capture_paths(plan: ConcretePlan) -> tuple[str, str]:
    return (f"{ROOT}/before/pg_hba.conf", f"{ROOT}/before/pg_ident.conf")


def _first_of_kind(plan: ConcretePlan, kind: CleanupStepKind) -> str:
    return next(
        step.step_id for step in plan.cleanup_plan.steps if step.kind is kind
    )


@pytest.mark.parametrize(
    "kind",
    [CleanupStepKind.RESTORE, CleanupStepKind.RELOAD, CleanupStepKind.VERIFY],
)
def test_a_failed_restoration_retains_its_recovery_inputs(kind) -> None:
    """The review's reproduction, asserted on the files rather than the calls.

    With the configuration restore failing, R12 reported S-B and nevertheless
    requested `rm --force -- …/before/pg_ident.conf` and `…/pg_hba.conf` — the
    two byte-exact captures an operator would have restored from. The same loss
    followed a failed reload and a failed post-reload verification.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    failing = _first_of_kind(plan, kind)
    overrides = {}
    if _is_effect(plan, failing):
        # **r6 §6.4.** The restore is a descriptor-bound effect since `install`
        # was retired, so it is failed at the issuer rather than scripted at the
        # boundary. The property is unchanged: a restoration that did not
        # complete retains the recovery inputs it would have read.
        overrides["effects"] = HostEffects(host=host, refuse={failing})
    else:
        host.overrides[failing] = CommandResult(exit_status=1, timed_out=False)

    outcome = runner(plan, host, **overrides).execute()

    assert outcome.cleanup.state == "S-B"
    for path in _capture_paths(plan):
        assert host.has(f"path:{path}"), path
        assert path in outcome.cleanup.retained_recovery_inputs
    assert outcome.cleanup.recovery_procedure == RECOVERY_PROCEDURE
    assert not any(
        vector[0] == "/usr/bin/rm" and vector[-1] in _capture_paths(plan)
        for vector in host.vectors
    )
    retained = {
        step.step_id
        for step in outcome.cleanup_steps
        if step.stop_reason == RECOVERY_INPUT_RETAINED
    }
    assert retained


def test_a_successful_restoration_removes_its_recovery_inputs() -> None:
    """The retention is conditional, not a permanent exemption."""
    plan = runnable_plan()
    host = FakeHost(plan)

    outcome = runner(plan, host).execute()

    assert outcome.cleanup.state == "S-C"
    assert outcome.cleanup.retained_recovery_inputs == ()
    for path in _capture_paths(plan):
        assert not host.has(f"path:{path}"), path


def test_a_retained_capture_keeps_the_directories_that_hold_it() -> None:
    plan = runnable_plan()
    host = FakeHost(plan)
    failing = _first_of_kind(plan, CleanupStepKind.RESTORE)

    runner(plan, host, effects=HostEffects(host=host, refuse={failing})).execute()

    assert host.has(f"path:{ROOT}/before")
    assert host.has(f"path:{ROOT}")


def test_the_generated_plan_links_every_capture_removal_to_its_restoration() -> None:
    plan = build_concrete_plan()
    phase = {
        step.step_id
        for step in plan.cleanup_plan.steps
        if step.kind
        in (CleanupStepKind.RESTORE, CleanupStepKind.RELOAD, CleanupStepKind.VERIFY)
    }
    assert phase
    linked = {
        step.removes
        for step in plan.cleanup_plan.steps
        if step.requires_satisfied
    }
    for path in _capture_paths(plan):
        assert path in linked, path
    for step in plan.cleanup_plan.steps:
        if step.requires_satisfied:
            assert set(step.requires_satisfied) == phase, step.step_id


# ---------------------------------------------------------------------------
# EH-R13-3 — non-identity prerequisites ignore their observations
# ---------------------------------------------------------------------------


def _steps_after(plan: ConcretePlan, step_id: str) -> set[str]:
    order = [step.step_id for step in plan.steps]
    return set(order[order.index(step_id) + 1 :])


def test_an_empty_launcher_bounding_set_is_refused() -> None:
    """The review's reproduction: `P-01` exits 0 with an empty bounding set.

    R12 marked the step satisfied, ran every dependent step behind it, and
    returned `completed=True` with `artifact_admissible=True` — for a run in
    which no capability was ever inspected.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides["P-01"] = CommandResult(
        exit_status=0,
        timed_out=False,
        observations=sanitize(
            CapturePolicy.CAPABILITY_MASKS,
            "Current: =\nBounding set =\nAmbient set =\n"
            "Securebits: 00/0x0/1'b0 (no-new-privs=0)\n",
        ),
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "P-01"
    assert not outcome.artifact_admissible
    assert not (set(host.calls) & _steps_after(plan, "P-01"))


def test_a_proc_status_shaped_capsh_observation_is_refused() -> None:
    """The synthetic value R12's reader accepted, through the real sanitizer.

    `CapBnd: …` is a `/proc/<pid>/status` field name. `capsh --print` prints no
    such line, so the old reader found nothing at all against real output and
    the step was decided by its exit status — and a fabricated `/proc`-shaped
    line satisfied a reader no `capsh` could satisfy.
    """
    observations = sanitize(
        CapturePolicy.CAPABILITY_MASKS, "CapBnd: 0000000000000000\n"
    )
    assert observations == ()

    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides["P-01"] = CommandResult(
        exit_status=0, timed_out=False, observations=observations
    )
    outcome = runner(plan, host).execute()
    assert outcome.stopped_at == "P-01"


def test_the_capsh_reader_reads_what_capsh_actually_prints() -> None:
    """The producing executable's real format, transcribed from its output."""
    observations = dict(
        sanitize(
            CapturePolicy.CAPABILITY_MASKS,
            "Current: =\n"
            "Bounding set =cap_chown,cap_dac_override\n"
            "Ambient set =\n"
            "Current IAB: \n"
            "Securebits: 00/0x2a/1'b0 (no-new-privs=1)\n"
            " secure-noroot: no (unlocked)\n"
            "uid=0(root) euid=0(root)\n",
        )
    )
    assert observations == {
        # cap_chown is bit 0 and cap_dac_override bit 1.
        "bounding_set": "3",
        "ambient_set": "0",
        "securebits": "2a",
        "no_new_privs": "1",
    }


def test_an_unexpected_group_member_is_refused() -> None:
    """The review's second reproduction: `B2-10` exits 0 with a member §2.12.2
    gives `freedomjournal` no reason to have."""
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides["B2-10"] = CommandResult(
        exit_status=0,
        timed_out=False,
        observations=sanitize(
            CapturePolicy.GROUP_MEMBERS,
            "freedomjournal:x:5004:freedomcoord,freedomsheet,fbprobe",
        ),
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "B2-10"
    assert not (set(host.calls) & _steps_after(plan, "B2-10"))
    assert not outcome.artifact_admissible


@pytest.mark.parametrize(
    "step_id,raw",
    [
        ("B2-10", "freedomjournal:x:5004:freedomcoord,freedomsheet"),
        ("B2-16", "uid=5001(freedomcoord) gid=5001(freedomcoord) groups=5001(freedomcoord),5004(freedomjournal)"),
        ("B3-19", "-----a-------------- /var/lib/x"),
        ("B4-10", "ext4 /dev/sda1 rw,relatime"),
        ("P-03", ""),
        ("P-04", "0 0 755 regular file"),
    ],
)
def test_a_compliant_observation_from_real_output_satisfies_its_contract(
    step_id: str, raw: str
) -> None:
    """Raw synthetic command output, through the real sanitizer, to the runner.

    The positive direction of the same gate: an observation a compliant producer
    would print satisfies the reviewed expectation, so the refusals above are
    about the values rather than about the contract being unsatisfiable.
    """
    plan = runnable_plan()
    step = step_named(plan, step_id)
    host = FakeHost(plan)
    host.overrides[step_id] = CommandResult(
        exit_status=0,
        timed_out=False,
        observations=sanitize(step.capture, raw),
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "", outcome.stop_reason
    assert outcome.completed


@pytest.mark.parametrize(
    "step_id",
    # `B3-01` is R16's exclusive creation: its observation is the ownership
    # evidence, so a creation that exited 0 and observed nothing is not satisfied
    # either — and, because it is a creation, it is additionally an uncertain one.
    ["R-01", "P-01", "P-03", "P-04", "B2-10", "B2-16", "B3-01", "B3-19", "B4-10", "B4-34"],
)
def test_an_observation_bearing_step_that_observed_nothing_is_not_satisfied(
    step_id: str,
) -> None:
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides[step_id] = CommandResult(exit_status=0, timed_out=False)

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id
    assert not (set(host.calls) & _steps_after(plan, step_id))


@pytest.mark.parametrize("step_id", ["B2-10", "B4-10", "P-04"])
def test_an_unreadable_value_is_refused(step_id: str) -> None:
    plan = runnable_plan()
    step = step_named(plan, step_id)
    host = FakeHost(plan)
    scripted = observations_for(step, bound_argv(step), SOURCES)
    host.overrides[step_id] = CommandResult(
        exit_status=0,
        timed_out=False,
        observations=tuple(
            (key, "unreadable" if index == 0 else value)
            for index, (key, value) in enumerate(scripted)
        ),
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id


@pytest.mark.parametrize("step_id", ["B2-10", "B4-10"])
def test_a_duplicated_key_is_refused(step_id: str) -> None:
    plan = runnable_plan()
    step = step_named(plan, step_id)
    host = FakeHost(plan)
    scripted = observations_for(step, bound_argv(step), SOURCES)
    host.overrides[step_id] = CommandResult(
        exit_status=0, timed_out=False, observations=scripted + scripted[:1]
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id


@pytest.mark.parametrize("step_id", ["B2-10", "B4-10"])
def test_an_unexpected_key_is_refused(step_id: str) -> None:
    plan = runnable_plan()
    step = step_named(plan, step_id)
    host = FakeHost(plan)
    scripted = observations_for(step, bound_argv(step), SOURCES)
    host.overrides[step_id] = CommandResult(
        exit_status=0,
        timed_out=False,
        observations=scripted + (("unreviewed", "value"),),
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id


# ---------------------------------------------------------------------------
# EH-R13-4 — required evidence cases absent from the executable plan
# ---------------------------------------------------------------------------


def test_a_plan_carrying_an_unresolved_conflict_cannot_be_executed_at_all() -> None:
    """No complete-harness success may be produced with required bands missing.

    **R16.** The gate is asserted twice over, because two different things have
    to hold and a single assertion would confuse them.

    First against the **shipped** plan, which carries C-7: Band 7's three
    producers do not exist — EH-R16-4 — so the plan is not executable and the
    executor's second gate refuses it. Second against a plan carrying a
    *synthetic* conflict, so that the gate is shown to refuse for the reason it
    states rather than because of the particular conflict that happens to be
    open today. A test that could only ever pass while something was broken
    would stop testing the gate on the day it was fixed; a test that only ever
    ran against today's blocker would stop testing it on the day the blocker
    changed.

    The completeness of the **evidence** is a separate statement and is asserted
    where it lives: `observations.EvidenceResult.band_7_coverage_complete` is
    false while any in-scope required variant has no validated record, and
    `overall_completeness_established` is false unconditionally — EH-R16-3.
    """
    from dataclasses import replace as _replace

    real = build_concrete_plan()
    assert real.conflicts() == ("C-7",) and real.is_executable is False
    blocked = ConcretePlan(
        execution_plan=real.execution_plan,
        cleanup_plan=real.cleanup_plan,
        unresolved=(
            UnresolvedStep(
                step_ref="SYNTHETIC",
                band="journal",
                conflict_id="C-SYNTHETIC",
                design_requires="a case this plan cannot express",
                why_not_a_vector="it is not a vector",
                what_would_resolve_it="a maintainer decision",
            ),
        ),
        external_cases=real.external_cases,
    )
    assert blocked.is_executable is False
    with pytest.raises(ExecutorRefused):
        runner(blocked, FakeHost(blocked))


# ---------------------------------------------------------------------------
# EH-R13-5 — the CLI reports an artifact written without writing one
# ---------------------------------------------------------------------------


def test_a_reported_run_record_exists_and_reads_back(tmp_path: Path) -> None:
    plan = runnable_plan()
    host = FakeHost(plan)
    built = runner(plan, host)
    outcome = built.execute()
    assert outcome.artifact_admissible

    destination = tmp_path / "run-record.json"
    written = write_run_record(
        outcome,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )

    assert written == destination and destination.exists()
    document = json.loads(destination.read_text(encoding="utf-8"))
    validate_run_record(document, expected_steps=len(outcome.steps))
    assert document["document_type"] == DOCUMENT_TYPE
    assert document["schema_version"] == RUN_RECORD_SCHEMA_VERSION == 3
    assert len(document["steps"]) == len(outcome.steps)
    assert document["cleanup"]["state"] == outcome.cleanup.state
    assert document["cleanup"]["residue_recovery_procedure"] == []
    assert document["review_manifest_digest"] == built.manifest_digest
    # The evidence a reviewer would look for is in it.
    identity_step = next(
        entry for entry in document["steps"] if entry["step_id"] == "P-06"
    )
    assert dict(identity_step["observations"])["verb"] == "identity"

    malformed = {
        **document,
        "cleanup": {
            **document["cleanup"],
            "residue_recovery_procedure": [
                {"order": 1, "action": "inspect", "rationale": ""}
            ],
        },
    }
    with pytest.raises(RunRecordRefused, match="malformed residue-recovery step"):
        validate_run_record(malformed, expected_steps=len(outcome.steps))


def test_a_residue_recovery_procedure_survives_the_run_record(tmp_path: Path) -> None:
    """The populated form of the field the schema went to version 2 for.

    The clean run above encodes an empty residue procedure, which a write that
    dropped the field entirely would also produce. This encodes the five-step
    procedure an S-B run really carries, reads it back off disk and requires the
    validator to accept it — so the encoder is exercised in the state the field
    exists for, not only in the state where it is empty.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    built = runner(plan, host)
    outcome = built.execute()

    stopped = replace(
        outcome,
        cleanup=replace(
            outcome.cleanup,
            residue=("/var/lib/fb-evidence-r1/probe",),
            residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
        ),
    )

    destination = tmp_path / "s-b-run-record.json"
    write_run_record(
        stopped,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )
    document = json.loads(destination.read_text(encoding="utf-8"))
    validate_run_record(document, expected_steps=len(stopped.steps))

    encoded = document["cleanup"]["residue_recovery_procedure"]
    assert [entry["order"] for entry in encoded] == [1, 2, 3, 4, 5]
    assert encoded == [
        {"order": step.order, "action": step.action, "rationale": step.rationale}
        for step in RESIDUE_RECOVERY_PROCEDURE
    ]


def test_a_residue_recovery_procedure_out_of_order_is_refused() -> None:
    """The order is the procedure. A reordered list is a different instruction."""
    plan = runnable_plan()
    host = FakeHost(plan)
    built = runner(plan, host)
    outcome = built.execute()
    stopped = replace(
        outcome,
        cleanup=replace(
            outcome.cleanup,
            residue=("/var/lib/fb-evidence-r1/probe",),
            residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
        ),
    )

    document = build_run_record(
        stopped,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )
    reordered = {
        **document,
        "cleanup": {
            **document["cleanup"],
            "residue_recovery_procedure": list(
                reversed(document["cleanup"]["residue_recovery_procedure"])
            ),
        },
    }
    with pytest.raises(RunRecordRefused, match="malformed residue-recovery step"):
        validate_run_record(
            reordered, expected_steps=len(reordered["steps"])
        )


def test_an_inadmissible_run_writes_nothing(tmp_path: Path) -> None:
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides["B2-10"] = CommandResult(exit_status=0, timed_out=False)
    built = runner(plan, host)
    outcome = built.execute()
    assert not outcome.artifact_admissible

    destination = tmp_path / "run-record.json"
    with pytest.raises(RunRecordRefused) as refusal:
        write_run_record(
            outcome,
            destination,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )
    assert NOT_ADMISSIBLE in str(refusal.value)
    assert not destination.exists()


def test_a_write_that_fails_is_reported_as_a_failure(tmp_path: Path) -> None:
    """A path that cannot be written is a refusal, never a reported artifact."""
    plan = runnable_plan()
    host = FakeHost(plan)
    built = runner(plan, host)
    outcome = built.execute()

    unwritable = tmp_path / "no-such-directory" / "run-record.json"
    with pytest.raises(RunRecordRefused):
        write_run_record(
            outcome,
            unwritable,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )
    assert not unwritable.exists()


def test_a_truncated_run_record_is_refused_on_read_back() -> None:
    """Validation is applied to what came back from disk, not to what was sent."""
    with pytest.raises(RunRecordRefused):
        validate_run_record(
            {
                "schema_version": 1,
                "document_type": DOCUMENT_TYPE,
                "steps": [],
                "cleanup": {"state": "S-C"},
            },
            expected_steps=3,
        )
    with pytest.raises(RunRecordRefused):
        validate_run_record(
            {"schema_version": 99, "document_type": DOCUMENT_TYPE},
            expected_steps=0,
        )


def test_the_cli_distinguishes_eligibility_from_persistence() -> None:
    """The two lines the single misleading one became."""
    from tools.phase_5_0_evidence.execution import cli as cli_module

    source = Path(cli_module.__file__).read_text(encoding="utf-8")
    assert "artifact eligible:" in source
    assert "run record       :" in source
    assert "artifact written : {outcome.artifact_admissible}" not in source


# ---------------------------------------------------------------------------
# PR-20260912-LAB1-1 — the run-record reader accepts a substituted procedure
# ---------------------------------------------------------------------------

#: The re-review's own substitution: one well-shaped, consecutively ordered step
#: whose instruction is the opposite of the procedure it replaced.
ARBITRARY_RESIDUE_PROCEDURE = (
    {
        "order": 1,
        "action": "IGNORE THE RESIDUE AND CONTINUE",
        "rationale": "arbitrary replacement",
    },
)

RESIDUE_PATH = "/var/lib/fb-evidence-p5-0/probe"
RETAINED_CAPTURE = "/var/lib/fb-evidence-p5-0/before/pg_hba.conf"


def _built_run():
    plan = runnable_plan()
    host = FakeHost(plan)
    built = runner(plan, host)
    return plan, built, built.execute()


def _outcome_and_document(**cleanup_fields):
    """A real run outcome with the named cleanup fields, and its run record."""
    plan, built, outcome = _built_run()
    stopped = replace(outcome, cleanup=replace(outcome.cleanup, **cleanup_fields))
    document = build_run_record(
        stopped,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )
    return stopped, document


def _with_cleanup(document: dict, **fields) -> dict:
    return {**document, "cleanup": {**document["cleanup"], **fields}}


def test_a_substituted_residue_procedure_is_refused_on_read_back() -> None:
    """PR-20260912-LAB1-1, in the re-review's own words.

    A schema-2 record whose five-step residue recovery was replaced by one
    arbitrary ordered instruction was **accepted**: the reader checked the shape
    and the order of each entry and never compared the value with
    `journal.RECOVERY_PROCEDURE` or with the residue that requires it. The
    record then said the run named the operator recovery when it named the
    opposite of it.
    """
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    substituted = _with_cleanup(
        document, residue_recovery_procedure=[dict(ARBITRARY_RESIDUE_PROCEDURE[0])]
    )

    with pytest.raises(RunRecordRefused):
        validate_run_record(substituted, expected_steps=len(stopped.steps))


def test_the_reproduction_holds_for_a_record_with_no_steps() -> None:
    """The reproduction exactly as it was run: `expected_steps=0`.

    `expected_steps` constrains the step list and says nothing about cleanup, so
    a record that satisfies it can still carry a substituted procedure. Stating
    it at zero steps keeps the two claims from being confused.
    """
    _stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    minimal = _with_cleanup(
        {**document, "steps": []},
        steps=[],
        residue_recovery_procedure=[dict(ARBITRARY_RESIDUE_PROCEDURE[0])],
    )

    with pytest.raises(RunRecordRefused):
        validate_run_record(minimal, expected_steps=0)


CANONICAL_RESIDUE_ENTRIES = [
    {"order": step.order, "action": step.action, "rationale": step.rationale}
    for step in RESIDUE_RECOVERY_PROCEDURE
]


def _changed_action() -> list[dict]:
    entries = [dict(entry) for entry in CANONICAL_RESIDUE_ENTRIES]
    entries[2]["action"] = "as root, remove whatever is in the way"
    return entries


def _changed_rationale() -> list[dict]:
    entries = [dict(entry) for entry in CANONICAL_RESIDUE_ENTRIES]
    entries[0]["rationale"] = "because the run said so"
    return entries


def _shorter_procedure() -> list[dict]:
    return [dict(entry) for entry in CANONICAL_RESIDUE_ENTRIES[:3]]


def _additional_step() -> list[dict]:
    entries = [dict(entry) for entry in CANONICAL_RESIDUE_ENTRIES]
    entries.append(
        {
            "order": len(entries) + 1,
            "action": "declare the host recovered",
            "rationale": "an extra ordered step is still an ordered list",
        }
    )
    return entries


#: Every substitution that keeps the shape the version-2 reader checked. Each row
#: is a document a shape check accepts and a content check must not.
SUBSTITUTED_RESIDUE_PROCEDURES = [
    ("arbitrary replacement", [dict(ARBITRARY_RESIDUE_PROCEDURE[0])]),
    ("changed action text", _changed_action()),
    ("changed rationale text", _changed_rationale()),
    ("shorter, consecutively ordered", _shorter_procedure()),
    ("one additional ordered step", _additional_step()),
    ("empty while residue remains", []),
]


@pytest.mark.parametrize(
    "label, procedure",
    SUBSTITUTED_RESIDUE_PROCEDURES,
    ids=[label for label, _ in SUBSTITUTED_RESIDUE_PROCEDURES],
)
def test_a_residue_procedure_that_is_not_the_canonical_one_is_refused(
    label: str, procedure: list
) -> None:
    """Content, compared against the canonical value — not shape, not length.

    Each row survives every check version 2 made: three keys, consecutive order,
    non-empty strings. What separates them from the procedure an operator is
    actually told to follow is the text, so the text is what is compared.
    """
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    substituted = _with_cleanup(document, residue_recovery_procedure=procedure)

    with pytest.raises(RunRecordRefused, match="canonical"):
        validate_run_record(substituted, expected_steps=len(stopped.steps))


def test_a_residue_procedure_out_of_order_is_still_refused() -> None:
    """The preserved version-2 case. Order is the procedure; it refuses first."""
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    reordered = _with_cleanup(
        document,
        residue_recovery_procedure=list(
            reversed(document["cleanup"]["residue_recovery_procedure"])
        ),
    )

    with pytest.raises(RunRecordRefused, match=RESIDUE_PROCEDURE_MALFORMED):
        validate_run_record(reordered, expected_steps=len(stopped.steps))


def test_a_missing_residue_procedure_field_is_refused() -> None:
    """A dropped field is a missing claim, not a claim about nothing."""
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    without = {
        key: value for key, value in document["cleanup"].items()
        if key != "residue_recovery_procedure"
    }

    with pytest.raises(RunRecordRefused, match="exactly the fields"):
        validate_run_record(
            {**document, "cleanup": without}, expected_steps=len(stopped.steps)
        )


def test_a_residue_procedure_without_residue_is_refused() -> None:
    """The mirror clause: a procedure with no cause is an unexplained claim."""
    stopped, document = _outcome_and_document(residue=())
    assert document["cleanup"]["residue_recovery_procedure"] == []
    planted = _with_cleanup(
        document, residue_recovery_procedure=[dict(entry) for entry in CANONICAL_RESIDUE_ENTRIES]
    )

    with pytest.raises(RunRecordRefused, match=RESIDUE_PROCEDURE_WITHOUT_RESIDUE):
        validate_run_record(planted, expected_steps=len(stopped.steps))


#: The configuration cause, given the same treatment. `cleanup.RECOVERY_PROCEDURE`
#: is four lines of text rather than ordered steps, so the substitutions are the
#: ones that shape carries no information about.
SUBSTITUTED_CONFIGURATION_PROCEDURES = [
    ("empty while captures are retained", []),
    (
        "changed text",
        list(CANONICAL_CONFIGURATION_RECOVERY[:-1]) + ["4. Re-run the harness."],
    ),
    ("shorter", list(CANONICAL_CONFIGURATION_RECOVERY[:2])),
    (
        "the residue procedure in its place",
        [entry["action"] for entry in CANONICAL_RESIDUE_ENTRIES],
    ),
]


@pytest.mark.parametrize(
    "label, procedure",
    SUBSTITUTED_CONFIGURATION_PROCEDURES,
    ids=[label for label, _ in SUBSTITUTED_CONFIGURATION_PROCEDURES],
)
def test_a_configuration_procedure_that_is_not_canonical_is_refused(
    label: str, procedure: list
) -> None:
    stopped, document = _outcome_and_document(
        retained_recovery_inputs=(RETAINED_CAPTURE,),
        recovery_procedure=RECOVERY_PROCEDURE,
    )
    substituted = _with_cleanup(document, recovery_procedure=procedure)

    with pytest.raises(RunRecordRefused, match=CONFIGURATION_PROCEDURE_NOT_CANONICAL):
        validate_run_record(substituted, expected_steps=len(stopped.steps))


def test_a_missing_configuration_procedure_field_is_refused() -> None:
    stopped, document = _outcome_and_document(
        retained_recovery_inputs=(RETAINED_CAPTURE,),
        recovery_procedure=RECOVERY_PROCEDURE,
    )
    without = {
        key: value for key, value in document["cleanup"].items()
        if key != "recovery_procedure"
    }

    with pytest.raises(RunRecordRefused, match="exactly the fields"):
        validate_run_record(
            {**document, "cleanup": without}, expected_steps=len(stopped.steps)
        )


def test_a_configuration_procedure_without_retained_captures_is_refused() -> None:
    stopped, document = _outcome_and_document(retained_recovery_inputs=())
    assert document["cleanup"]["recovery_procedure"] == []
    planted = _with_cleanup(document, recovery_procedure=list(RECOVERY_PROCEDURE))

    with pytest.raises(
        RunRecordRefused, match=CONFIGURATION_PROCEDURE_WITHOUT_RETENTION
    ):
        validate_run_record(planted, expected_steps=len(stopped.steps))


def test_neither_procedure_answers_for_the_other() -> None:
    """LAB-1's clause inside the record — runner contract r6 §8.1.

    Residue present and only the configuration procedure carried, and then the
    mirror: a retained capture with only the residue procedure carried. Each is
    a complete, well-shaped, canonical procedure — for the other cause. Both are
    refused, which is what *"neither answers for the other"* has to mean in a
    reader as well as in the operator message.
    """
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    configuration_only = _with_cleanup(
        document,
        residue_recovery_procedure=[],
        recovery_procedure=list(RECOVERY_PROCEDURE),
    )
    with pytest.raises(RunRecordRefused, match=RESIDUE_PROCEDURE_NOT_CANONICAL):
        validate_run_record(configuration_only, expected_steps=len(stopped.steps))

    stopped, document = _outcome_and_document(
        retained_recovery_inputs=(RETAINED_CAPTURE,),
        recovery_procedure=RECOVERY_PROCEDURE,
    )
    residue_only = _with_cleanup(
        document,
        recovery_procedure=[],
        residue_recovery_procedure=[dict(entry) for entry in CANONICAL_RESIDUE_ENTRIES],
    )
    with pytest.raises(RunRecordRefused, match=RESIDUE_PROCEDURE_WITHOUT_RESIDUE):
        validate_run_record(residue_only, expected_steps=len(stopped.steps))


#: The three cause combinations that must be **accepted**, so the repair is shown
#: to refuse substitutes rather than to refuse everything. Each is exactly what
#: `cleanup.classify_cleanup` attaches for that combination.
ACCEPTED_CAUSE_COMBINATIONS = [
    (
        "residue alone",
        {
            "residue": (RESIDUE_PATH,),
            "residue_recovery_procedure": RESIDUE_RECOVERY_PROCEDURE,
        },
    ),
    (
        "configuration alone",
        {
            "retained_recovery_inputs": (RETAINED_CAPTURE,),
            "recovery_procedure": RECOVERY_PROCEDURE,
        },
    ),
    (
        "both causes",
        {
            "residue": (RESIDUE_PATH,),
            "residue_recovery_procedure": RESIDUE_RECOVERY_PROCEDURE,
            "retained_recovery_inputs": (RETAINED_CAPTURE,),
            "recovery_procedure": RECOVERY_PROCEDURE,
        },
    ),
    ("neither cause", {}),
]


@pytest.mark.parametrize(
    "label, fields",
    ACCEPTED_CAUSE_COMBINATIONS,
    ids=[label for label, _ in ACCEPTED_CAUSE_COMBINATIONS],
)
def test_the_exact_procedures_for_the_causes_present_are_accepted(
    label: str, fields: dict, tmp_path: Path
) -> None:
    """Through the public write/read-back function, not only through the reader.

    `write_run_record` requires `artifact_admissible`, which requires S-C, so the
    populated forms are constructed here the way the version-2 round-trip test
    constructs them: a real run outcome with the cleanup fields replaced. That is
    the only way this document carries a recovery procedure at all today, and it
    is stated rather than implied.
    """
    plan, built, outcome = _built_run()
    stopped = replace(outcome, cleanup=replace(outcome.cleanup, **fields))

    destination = tmp_path / f"{label.replace(' ', '-')}.json"
    write_run_record(
        stopped,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )

    document = json.loads(destination.read_text(encoding="utf-8"))
    validate_run_record(document, expected_steps=len(stopped.steps))
    assert document["cleanup"]["residue_recovery_procedure"] == [
        {"order": step.order, "action": step.action, "rationale": step.rationale}
        for step in fields.get("residue_recovery_procedure", ())
    ]
    assert document["cleanup"]["recovery_procedure"] == list(
        fields.get("recovery_procedure", ())
    )


class _TamperingDestination:
    """A destination that writes faithfully and reads back something else.

    A substituted read-back cannot be produced by writing a different document:
    the writer serializes what it compares. This supplies the only other thing
    that can differ — the bytes that come back — so the whole-document comparison
    is exercised against a file the writer really wrote.
    """

    def __init__(self, path: Path, tamper) -> None:
        self.path = path
        self._tamper = tamper
        #: What the writer handed over, and what it got back. Recorded so a
        #: regression can state what the two byte strings actually were rather
        #: than assert only that a refusal happened — PR-20260912-LAB1-2.
        self.written: bytes | None = None
        self.read_back: bytes | None = None

    def write_bytes(self, data: bytes) -> int:
        self.written = data
        return self.path.write_bytes(data)

    def read_bytes(self) -> bytes:
        self.read_back = self._tamper(self.path.read_bytes())
        return self.read_back


def _substitute(field_path: tuple[str, ...], value):
    def tamper(raw: bytes) -> bytes:
        document = json.loads(raw.decode("utf-8"))
        target = document
        for key in field_path[:-1]:
            target = target[key]
        target[field_path[-1]] = value
        return json.dumps(document, indent=2, sort_keys=True).encode("utf-8")

    return tamper


#: Emitted values the reader does not otherwise constrain. Each one substituted
#: for something well-shaped, so only the whole-document comparison refuses it.
UNCONSTRAINED_SUBSTITUTIONS = [
    ("target identity", ("target_identity",), "somebody-else"),
    ("manifest digest", ("review_manifest_digest",), "0" * 64),
    ("stop reason", ("stop_reason",), "nothing went wrong"),
    ("completed flag", ("completed",), False),
    ("mutations reached", ("mutations_reached",), ["M-01"]),
    ("cleanup exit code", ("cleanup", "exit_code"), 3),
    # `False == 0` in Python, so mapping equality alone would accept this.
    # The byte comparison is what refuses it.
    ("exit code written as a boolean", ("cleanup", "exit_code"), False),
    ("preserved list", ("cleanup", "preserved"), ["/var/lib/fb-evidence-p5-0/kept"]),
    (
        "configuration risk",
        ("cleanup", "configuration_risk"),
        ["the risk that was not reported"],
    ),
]


@pytest.mark.parametrize(
    "label, field_path, value",
    UNCONSTRAINED_SUBSTITUTIONS,
    ids=[label for label, _, _ in UNCONSTRAINED_SUBSTITUTIONS],
)
def test_any_other_substituted_value_is_refused_on_read_back(
    label: str, field_path: tuple, value, tmp_path: Path
) -> None:
    """`expected_steps` still matches, and the document is still refused."""
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(
        tmp_path / "run-record.json", _substitute(field_path, value)
    )

    with pytest.raises(RunRecordRefused, match=NOT_THE_DOCUMENT_WRITTEN):
        write_run_record(
            outcome,
            destination,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )


def test_a_partially_flushed_run_record_is_refused(tmp_path: Path) -> None:
    """Half a document is not a document, and it is not a written artifact."""
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(
        tmp_path / "run-record.json", lambda raw: raw[: len(raw) // 2]
    )

    with pytest.raises(RunRecordRefused, match=NOT_THE_DOCUMENT_WRITTEN):
        write_run_record(
            outcome,
            destination,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )


def test_a_version_2_run_record_is_refused_by_version_rather_than_reinterpreted() -> None:
    """The incompatible contract refuses by name — it is not read both ways.

    Under version 2 an arbitrary ordered procedure was a **valid** record. Under
    version 3 it is not. Accepting both under one version number would be the
    weak meaning surviving beside the corrected one, so the version moves.
    """
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    version_2 = {
        **_with_cleanup(
            document,
            residue_recovery_procedure=[dict(ARBITRARY_RESIDUE_PROCEDURE[0])],
        ),
        "schema_version": 2,
    }

    with pytest.raises(RunRecordRefused, match="another schema"):
        validate_run_record(version_2, expected_steps=len(stopped.steps))


def test_the_validated_field_set_is_the_set_the_encoder_emits() -> None:
    """The two key sets are pinned to `build_run_record`, not written beside it.

    A field added to the encoder and not to the validated set would be a value
    written into the record and never checked on the way back.
    """
    _stopped, document = _outcome_and_document()

    assert set(document) == DOCUMENT_FIELDS
    assert set(document["cleanup"]) == CLEANUP_FIELDS


def test_the_canonical_values_are_the_procedures_the_operator_is_given() -> None:
    """Derived from `journal` and `cleanup`, so the two cannot drift apart."""
    assert CANONICAL_RESIDUE_RECOVERY == tuple(
        (step.order, step.action, step.rationale)
        for step in RESIDUE_RECOVERY_PROCEDURE
    )
    assert CANONICAL_CONFIGURATION_RECOVERY == tuple(RECOVERY_PROCEDURE)
    assert len(CANONICAL_RESIDUE_RECOVERY) == 5


# ---------------------------------------------------------------------------
# The negative controls for the two comparisons the repair rests on
# ---------------------------------------------------------------------------


def test_gutting_the_canonical_comparison_makes_the_regression_fail(monkeypatch) -> None:
    """The control for `_matches_canonical`.

    With the comparison hardcoded to `True` — the way an unimplemented check is
    made to look implemented — the re-review's reproduction is accepted again.
    Every canonical-content regression above therefore constrains that function
    and not something adjacent to it.
    """
    monkeypatch.setattr(
        artifact_module, "_matches_canonical", lambda read, canonical: True
    )
    stopped, document = _outcome_and_document(
        residue=(RESIDUE_PATH,),
        residue_recovery_procedure=RESIDUE_RECOVERY_PROCEDURE,
    )
    substituted = _with_cleanup(
        document, residue_recovery_procedure=[dict(ARBITRARY_RESIDUE_PROCEDURE[0])]
    )

    validate_run_record(substituted, expected_steps=len(stopped.steps))


def test_gutting_the_read_back_comparison_makes_the_regression_fail(
    monkeypatch, tmp_path: Path
) -> None:
    """The control for `_read_back_matches`, stated the same way.

    The signature gained `raw` under PR-20260912-LAB1-2, so the hardcoded
    replacement takes it too. The substituted `target_identity` below is refused
    by the raw comparison as well as by the mapping comparison, so this control
    now shows the whole read-back seam is load-bearing rather than isolating the
    mapping half; the conjunct-level control is the next test.
    """
    monkeypatch.setattr(
        artifact_module,
        "_read_back_matches",
        lambda raw, written, document, serialized: True,
    )
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(
        tmp_path / "run-record.json",
        _substitute(("target_identity",), "somebody-else"),
    )

    write_run_record(
        outcome,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )


# ---------------------------------------------------------------------------
# PR-20260912-LAB1-2 — the raw bytes read back were never compared
# ---------------------------------------------------------------------------

#: The R2 re-review's finding, in one sentence: `write_run_record` decoded and
#: parsed the bytes it read and then compared only the resulting **mapping** and
#: a fresh canonical re-serialization of it. The bytes that came back were
#: discarded at the moment they arrived, so every difference JSON parsing
#: collapses — surrounding whitespace, re-indentation, a repeated member name —
#: survived a function whose documented claim was *"the bytes are the ones that
#: were written"*.
#:
#: Each tamper below therefore produces bytes that are **not** the bytes written
#: and that **do** parse to the same mapping. That combination is what separates
#: a raw-byte comparison from every weaker check, and it is asserted in each
#: regression rather than implied.


def _identity_bytes(raw: bytes) -> bytes:
    """The destination behaving correctly: the bytes written, unchanged."""
    return raw


def _surround(prefix: bytes = b"", suffix: bytes = b""):
    def tamper(raw: bytes) -> bytes:
        return prefix + raw + suffix

    return tamper


def _reindent(raw: bytes) -> bytes:
    """Same document, different serialization. No member name or value changes."""
    return json.dumps(json.loads(raw.decode("utf-8")), indent=4, sort_keys=True).encode(
        "utf-8"
    )


def _duplicate_member(container_path: tuple[str, ...], key: str):
    """Emit one member a second time, with the value it already has.

    Duplicate JSON member names are not an error to `json.loads`, which keeps the
    last occurrence — so a duplicate carrying the *same* value parses to exactly
    the mapping the writer serialized. It is nonetheless a different document:
    RFC 8259 leaves duplicate names' handling to the implementation, so two
    readers may legitimately disagree about what this file says. A writer that
    claims the read-back is the document it wrote may not accept it.
    """

    def tamper(raw: bytes) -> bytes:
        text = raw.decode("utf-8")
        container = json.loads(text)
        for part in container_path:
            container = container[part]
        rendered = json.dumps(container[key])
        if container_path:
            opening = f'"{container_path[-1]}": {{\n'
            indent = "  " * (len(container_path) + 1)
        else:
            opening = "{\n"
            indent = "  "
        cut = text.index(opening) + len(opening)
        return (text[:cut] + f'{indent}"{key}": {rendered},\n' + text[cut:]).encode(
            "utf-8"
        )

    return tamper


#: Every read-back the submitted writer accepted, and the two the re-review
#: reproduced by hand. Each row is bytes that differ from what was written and
#: parse to the mapping that was written.
COLLAPSING_TAMPERS = [
    ("a leading newline", _surround(prefix=b"\n")),
    ("a trailing newline", _surround(suffix=b"\n")),
    ("a newline at each end", _surround(prefix=b"\n", suffix=b"\n")),
    ("trailing spaces", _surround(suffix=b"   ")),
    ("leading whitespace of several kinds", _surround(prefix=b" \t\r\n")),
    ("a different indent", _reindent),
    ("a duplicate schema_version", _duplicate_member((), "schema_version")),
    ("a duplicate document_type", _duplicate_member((), "document_type")),
    ("a duplicate nested cleanup state", _duplicate_member(("cleanup",), "state")),
    (
        "a duplicate nested cleanup exit code",
        _duplicate_member(("cleanup",), "exit_code"),
    ),
]


@pytest.mark.parametrize(
    "label, tamper",
    COLLAPSING_TAMPERS,
    ids=[label for label, _ in COLLAPSING_TAMPERS],
)
def test_read_back_bytes_that_are_not_the_bytes_written_are_refused(
    label: str, tamper, tmp_path: Path
) -> None:
    """PR-20260912-LAB1-2, through the public writer.

    The refusal must be the existing fixed one, and it must happen before the
    function can return a path — a written artifact is reported for these bytes
    or it is not reported at all.
    """
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(tmp_path / "run-record.json", tamper)

    with pytest.raises(RunRecordRefused, match=NOT_THE_DOCUMENT_WRITTEN):
        write_run_record(
            outcome,
            destination,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )

    # Why the mapping comparison could not refuse it: the bytes differ and the
    # documents do not.
    assert destination.read_back != destination.written
    assert json.loads(destination.read_back.decode("utf-8")) == json.loads(
        destination.written.decode("utf-8")
    )


def test_the_duplicate_key_reproduction_is_the_one_the_re_review_ran(
    tmp_path: Path,
) -> None:
    """The reviewer's second reproduction, stated as bytes rather than by name.

    A second `"schema_version": 3` member, with the value unchanged. The point of
    requiring the same value is that it removes every explanation but the raw
    bytes: the mapping is identical, the canonical re-serialization is identical,
    the schema check passes, and `validate_run_record` passes. Only a comparison
    that kept the bytes can tell these two files apart.
    """
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(
        tmp_path / "run-record.json", _duplicate_member((), "schema_version")
    )

    with pytest.raises(RunRecordRefused, match=NOT_THE_DOCUMENT_WRITTEN):
        write_run_record(
            outcome,
            destination,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )

    read_back = destination.read_back.decode("utf-8")
    assert read_back.count('"schema_version"') == 2
    parsed = json.loads(read_back)
    assert parsed["schema_version"] == RUN_RECORD_SCHEMA_VERSION == 3
    # Everything the writer used to check still holds of these bytes.
    assert parsed == json.loads(destination.written.decode("utf-8"))
    assert json.dumps(parsed, indent=2, sort_keys=True).encode("utf-8") == (
        destination.written
    )
    validate_run_record(parsed, expected_steps=len(outcome.steps))


def test_the_whitespace_reproduction_is_the_one_the_re_review_ran(
    tmp_path: Path,
) -> None:
    """The reviewer's first reproduction: `b"\\n" + serialized + b"\\n"`."""
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(
        tmp_path / "run-record.json", _surround(prefix=b"\n", suffix=b"\n")
    )

    with pytest.raises(RunRecordRefused, match=NOT_THE_DOCUMENT_WRITTEN):
        write_run_record(
            outcome,
            destination,
            target_identity=plan.target.identity,
            manifest_digest=built.manifest_digest,
        )

    assert destination.read_back == b"\n" + destination.written + b"\n"


def test_the_exact_bytes_written_and_returned_are_accepted(tmp_path: Path) -> None:
    """The positive half: a faithful destination still yields a written record.

    Without this the correction could be a writer that refuses everything, which
    would satisfy every regression above and write no evidence at all.
    """
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(tmp_path / "run-record.json", _identity_bytes)

    returned = write_run_record(
        outcome,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )

    assert returned is destination
    assert destination.read_back == destination.written
    assert destination.path.read_bytes() == destination.written
    validate_run_record(
        json.loads(destination.path.read_text(encoding="utf-8")),
        expected_steps=len(outcome.steps),
    )


@pytest.mark.parametrize(
    "label, fields",
    ACCEPTED_CAUSE_COMBINATIONS,
    ids=[label for label, _ in ACCEPTED_CAUSE_COMBINATIONS],
)
def test_the_accepted_cause_combinations_survive_the_raw_byte_binding(
    label: str, fields: dict, tmp_path: Path
) -> None:
    """The four accepted combinations, re-stated against the byte comparison.

    They are already accepted through a real `Path` destination above. This runs
    them through the recording destination as well, so the evidence that the four
    still pass is evidence about the same comparison the refusals exercise.
    """
    plan, built, outcome = _built_run()
    stopped = replace(outcome, cleanup=replace(outcome.cleanup, **fields))
    destination = _TamperingDestination(
        tmp_path / f"{label.replace(' ', '-')}.json", _identity_bytes
    )

    write_run_record(
        stopped,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )

    assert destination.read_back == destination.written
    validate_run_record(
        json.loads(destination.path.read_text(encoding="utf-8")),
        expected_steps=len(stopped.steps),
    )


# ---------------------------------------------------------------------------
# The negative controls for the raw-byte binding
# ---------------------------------------------------------------------------


def _without_the_raw_comparison(raw, written, document, serialized) -> bool:
    """`_read_back_matches` exactly as it was before PR-20260912-LAB1-2.

    Not a weakened stand-in written for the control: the two conjuncts are the
    submitted implementation, and `raw` is accepted and ignored the way the
    submitted writer ignored it by never passing it.
    """
    return (
        written == document
        and json.dumps(written, indent=2, sort_keys=True).encode("utf-8") == serialized
    )


@pytest.mark.parametrize(
    "label, tamper",
    COLLAPSING_TAMPERS,
    ids=[label for label, _ in COLLAPSING_TAMPERS],
)
def test_reversing_only_the_raw_byte_conjunct_accepts_every_collapsing_tamper(
    label: str, tamper, monkeypatch, tmp_path: Path
) -> None:
    """The negative control PR-20260912-LAB1-2 asks for, at conjunct level.

    Hardcoding the whole comparison to `True` proves the seam matters and does not
    say **which** conjunct does the work. This removes only `raw == serialized`
    and leaves the mapping and re-serialization comparisons exactly as they were
    submitted — and every row the writer now refuses is accepted again. So the
    regressions above constrain the raw-byte comparison specifically, and the
    mapping comparison demonstrably cannot do that job.
    """
    monkeypatch.setattr(
        artifact_module, "_read_back_matches", _without_the_raw_comparison
    )
    plan, built, outcome = _built_run()
    destination = _TamperingDestination(tmp_path / "run-record.json", tamper)

    write_run_record(
        outcome,
        destination,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )


def test_the_raw_comparison_is_the_first_thing_the_read_back_seam_states(
    tmp_path: Path,
) -> None:
    """Called directly, with the two reproductions as its inputs.

    `_read_back_matches` is the one named comparison the binding lives in, and
    the bytes are one of its inputs. Stating that here as well as through the
    writer means a change to the seam's contract cannot pass by leaving the
    writer's call site untouched.
    """
    plan, built, outcome = _built_run()
    document = build_run_record(
        outcome,
        target_identity=plan.target.identity,
        manifest_digest=built.manifest_digest,
    )
    serialized = json.dumps(document, indent=2, sort_keys=True).encode("utf-8")

    assert artifact_module._read_back_matches(
        serialized, json.loads(serialized.decode("utf-8")), document, serialized
    )
    for tampered in (
        b"\n" + serialized + b"\n",
        _duplicate_member((), "schema_version")(serialized),
    ):
        parsed = json.loads(tampered.decode("utf-8"))
        # The two weaker conjuncts hold; the seam still refuses.
        assert _without_the_raw_comparison(tampered, parsed, document, serialized)
        assert not artifact_module._read_back_matches(
            tampered, parsed, document, serialized
        )
