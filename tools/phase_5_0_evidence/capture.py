"""Turning a command's output into the only observations the evidence schema
admits: a short, fixed list of scalars.

**Planning tier.** This module names no process and reads no file: it is pure
text processing over a string somebody else obtained, which is why it lives
beside the planner rather than in `execution/`. Putting it here has a second
consequence that matters more than tidiness — a step's `CapturePolicy` is part
of the reviewed plan and part of the manifest digest, so *what a run is allowed
to record from a command* is something Codex approves in advance rather than
something the executor decides while running.

## The rule this module exists to make structural

*"Never serialize secrets, configuration contents, arbitrary stdout/stderr,
player data, addresses or credentials."* A rule about what a run must not record
is only as good as the narrowest place it is enforced. Here, the enforcement is
that **raw output has no representation that survives this module**: every policy
returns `tuple[tuple[str, str], ...]` of named scalars, every value is drawn from
a bounded vocabulary, and there is no policy whose output is the input.

`EXIT_STATUS_ONLY` is the default and covers every mutation-bearing step. A step
that creates a group does not need its output recorded; it needs its exit status,
and reading anything more from a command whose whole purpose is a side effect is
an invitation to record something nobody reviewed.

## Why each policy is narrow rather than a parser

None of these is a general parser for its tool's output. `GROUP_MEMBERS` reads
`getent group`'s fourth colon-field and nothing else; `CAPABILITY_MASKS` reads
the two capability name sets, the securebits word and `no-new-privs` that
`capsh --print` prints, and no other line of it; `ATTRIBUTE_FLAGS` reads whether
`lsattr` shows the append-only and immutable flags and nothing to their right — deliberately, because the
path is to the right, and a path is a string the run already knows and does not
need the tool to tell it. An output that does not match the shape produces
`("parse", "unreadable")` rather than a guess: an unreadable observation is
`INCONCLUSIVE` evidence, which is a result, and a guessed one is a fabricated
result.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .capability import ALL_CAPABILITY_NAMES

#: Capability name to capability number, from the one closed table this package
#: has. `ALL_CAPABILITY_NAMES` is written in kernel order, so its index **is**
#: the capability number, which is what makes this a derivation rather than a
#: second table that could disagree with the first.
_CAPABILITY_BITS = {name: index for index, name in enumerate(ALL_CAPABILITY_NAMES)}

#: No captured value may exceed this. A tool that prints more than this about one
#: of these narrow questions is not printing what the policy expects, and
#: truncating quietly would record half of something unexpected.
MAX_VALUE_LENGTH = 120

#: No policy may return more than this many observations from one command.
MAX_OBSERVATIONS = 32

#: The character class a captured value may contain. Deliberately narrow: no
#: quotes, no shell metacharacters, no whitespace beyond a single space, and
#: nothing that could carry a rule, an option string or a credential fragment
#: through into an artifact.
_SAFE_VALUE = re.compile(r"\A[A-Za-z0-9_,.:+=/@ -]{0,120}\Z")

_HEX_MASK = re.compile(r"\A[0-9a-fA-F]{1,16}\Z")
#: A PostgreSQL database or role name as this plan writes one — the same shape
#: `targets.validate_database_name` and `plan._POSTGRES_ROLE_NAME` accept. A
#: catalog line that is not this shape is not a name this plan can compare, and
#: `_catalog_membership` refuses the observation rather than guessing.
_CATALOG_NAME = re.compile(r"\A[a-z][a-z0-9_]{0,62}\Z")
_FLAG_LETTERS = re.compile(r"\A[-a-zA-Z]{1,32}\Z")

#: Per-field shapes. **`_SAFE_VALUE` alone is not enough**, and a test proved it:
#: a hostile first line of `password=… host=10.0.0.1 rule='…'` reached
#: `_mount_facts` and `_file_mode`, whose first whitespace-separated field passed
#: the character class and became the recorded `fstype` and `uid`. A character
#: class says a value is *printable*; it does not say the field is the field. So
#: every extracted value is additionally matched against the shape its field can
#: legitimately have, and a value that is not that shape is `unreadable` — which
#: is an INCONCLUSIVE observation, which is a result, rather than a fabricated
#: one.
_SHAPES = {
    "name": re.compile(r"\A[a-z_][a-z0-9_-]{0,31}\Z"),
    "name_list": re.compile(r"\A(?:[a-z_][a-z0-9_-]{0,31})(?:,[a-z_][a-z0-9_-]{0,31})*\Z"),
    "number": re.compile(r"\A[0-9]{1,10}\Z"),
    "mode": re.compile(r"\A[0-7]{3,4}\Z"),
    "fstype": re.compile(r"\A[a-z0-9._-]{1,32}\Z"),
    "device": re.compile(r"\A(?:/[A-Za-z0-9._/-]{1,96}|[A-Za-z0-9._:-]{1,64})\Z"),
    "words": re.compile(r"\A[a-z ]{1,32}\Z"),
    "flags": re.compile(r"\A[a-zA-Z]{0,24}\Z"),
    # The five shapes the case program's own output can legitimately have. They
    # are as narrow as the six above and for the same reason: the program is
    # trusted to run one reviewed operation, not to decide what an artifact may
    # contain.
    "number_list": re.compile(r"\A[0-9]{1,10}(?:,[0-9]{1,10})*\Z"),
    "errno": re.compile(r"\A(?:[A-Z]{1,16}|none)\Z"),
    "token": re.compile(r"\A[a-z0-9._-]{1,64}\Z"),
    "digest": re.compile(r"\A[0-9a-f]{64}\Z"),
    "mask": re.compile(r"\A[0-9a-fA-F]{1,16}\Z"),
    "version": re.compile(r"\A[0-9]{1,3}\.[0-9]{1,3}\Z"),
    "yes_no": re.compile(r"\A(?:yes|no)\Z"),
    "absolute_path": re.compile(r"\A/[A-Za-z0-9._/-]{1,110}\Z"),
    # The securebits word `prctl(PR_GET_SECUREBITS)` returns, in lower-case
    # hexadecimal. Two digits at most: `securebits.h` defines eight bits, so
    # `0 … 0xff` is the whole legitimate range and anything wider is not a
    # securebits word. Narrower than `mask` on purpose — a sixteen-digit value
    # here would be evidence that something other than securebits was read.
    "securebits": re.compile(r"\A[0-9a-f]{1,2}\Z"),
    # **Conflict C-8.** A `st_dev` or `st_ino` as `fstat(2)` reports it. Both are
    # 64-bit on Linux, so the ten digits `number` admits are not enough — an
    # inode number on a filesystem that issues large ones would be recorded as
    # `unreadable` and the ownership evidence would be missing exactly where the
    # filesystem is least ordinary. Twenty digits is `2**64 - 1`.
    "wide_number": re.compile(r"\A[0-9]{1,20}\Z"),
}


def _shaped(value: str, shape: str) -> str:
    """`value` when it is the shape its field can legitimately have, else the
    marker that it is not."""
    cleaned = _clean(value)
    return cleaned if _SHAPES[shape].match(cleaned) else "unreadable"


class CapturePolicy(str, Enum):
    """What may be read from a step's output. A closed set, by design.

    A step declares its policy in the reviewed plan, so what a run is allowed to
    record from it is part of what Codex approves rather than something the
    executor decides while running.
    """

    #: Record the exit status and nothing else. Every mutation-bearing step.
    EXIT_STATUS_ONLY = "exit_status_only"
    #: `capsh --print`: the bounding and ambient capability **name sets**, the
    #: securebits word and `no-new-privs`, read in the format `capsh` actually
    #: prints — R13, EH-R13-3.
    CAPABILITY_MASKS = "capability_masks"
    #: `getent group NAME`: the group name and its member set.
    GROUP_MEMBERS = "group_members"
    #: `id NAME`: the numeric uid, gid and the supplementary group names.
    ACCOUNT_IDENTITY = "account_identity"
    #: `lsattr`: whether the append-only and immutable flags are set. Nothing to
    #: the right of the flag field, and no other letter — R13.
    ATTRIBUTE_FLAGS = "attribute_flags"
    #: `findmnt --output FSTYPE,SOURCE,OPTIONS`: the filesystem type, the backing
    #: device, and whether the mount is read-only. All three are compared against
    #: the confirmed target facts — R13.
    MOUNT_FACTS = "mount_facts"
    #: `stat --format=%u %g %a %F`: owner, group, mode and file type.
    FILE_MODE = "file_mode"
    #: `getcap`: whether any file capability is set, as a yes/no.
    FILE_CAPABILITIES = "file_capabilities"
    #: The reviewed case program's operation result: the verb, whether the
    #: operation returned or was refused, the exact errno name, and the small
    #: fixed set of size and flag facts the §2.13.2a cases are stated in.
    CASE_RESULT = "case_result"
    #: The case program's `identity` verb: the numeric uid, gid and supplementary
    #: gids, the five capability masks, `NoNewPrivs` and the final securebits.
    CASE_IDENTITY = "case_identity"
    #: The case program's `runtime` verb: the interpreter preflight.
    CASE_RUNTIME = "case_runtime"
    #: `systemctl show --property=…` for the Stage-4 transient unit: the two
    #: sandbox directives §2.13.2a's S4-3 compares and the load state the R13
    #: ownership baseline asks for, and nothing else on the unit's several
    #: hundred other properties. A step declares the subset it asked for.
    UNIT_DIRECTIVES = "unit_directives"
    #: **R14, EH-R14-1.** One PostgreSQL catalog listing, read as two yes/no
    #: answers about names the reviewed plan states: is the subject there, and is
    #: the control — a name the target is known to carry — there too. See
    #: `_catalog_membership` for why the answer is computed here rather than
    #: recorded as the list.
    CATALOG_MEMBERSHIP = "catalog_membership"


@dataclass(frozen=True, slots=True)
class CatalogQuestion:
    """The two names a `CATALOG_MEMBERSHIP` observation answers about.

    **R14, EH-R14-1.** Both come from the reviewed plan and are pinned in the
    review manifest, so *what a catalog reading is asked* is approved beside the
    vector that reads it. `subject` is the object whose absence a baseline needs;
    `control` is a name the catalog must carry, so an empty, truncated or
    unparsed listing cannot read as *"the subject is not there"*.
    """

    subject: str
    control: str

    def __post_init__(self) -> None:
        for field_name in ("subject", "control"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not _CATALOG_NAME.match(value):
                raise ValueError(
                    f"A catalog question's {field_name} is one plain lower-case "
                    "identifier, the shape a PostgreSQL database or role name "
                    "has in this plan."
                )
        if self.subject == self.control:
            raise ValueError(
                "A catalog question's control is a **different** name from its "
                "subject: the control exists to prove the listing was read, and "
                "a control that is the subject would have to be present and "
                "absent at once."
            )


def _clean(value: str) -> str:
    """A value that is safe to put in an artifact, or the marker that it is not."""
    collapsed = " ".join(value.split())
    if len(collapsed) > MAX_VALUE_LENGTH or not _SAFE_VALUE.match(collapsed):
        return "unreadable"
    return collapsed


def _bounded(observations: list[tuple[str, str]]) -> tuple[tuple[str, str], ...]:
    return tuple(observations[:MAX_OBSERVATIONS])


def _name_set(raw: str) -> str:
    """A comma-separated name list, sorted, or the literal `none`.

    `none` rather than the empty string, because an empty *value* is this
    module's marker for *"nothing was read"* and an empty **set** is an
    observation. `expectations.Comparison.TEXT_SET` reads the two apart, and
    could not if they were spelled the same.
    """
    names = sorted(name for name in raw.replace(" ", "").split(",") if name)
    return _shaped(",".join(names), "name_list") if names else "none"


def _capability_mask(raw: str) -> str:
    """A `capsh` capability **name list**, as the hexadecimal mask it stands for.

    `capsh --print` prints names and `capability.E7_TARGET_FACTS` states masks,
    so one of the two has to be converted before they can be compared. It is
    done here, on the observation, for one reason that decides it: the complete
    bounding set of a root process is forty-one names and about seven hundred
    characters, which is six times `MAX_VALUE_LENGTH`. Recording it as text would
    mean either raising that bound — a reviewed limit on how much of a command's
    output may reach an artifact — or recording `unreadable` for the one value
    `P-01` exists to observe.

    The conversion is a **total lookup in a closed table**, never a parse: a name
    the table does not carry makes the whole value `unreadable`, which is an
    inconclusive observation and refuses the step. A newer kernel's forty-second
    capability therefore stops the run instead of being silently dropped from a
    set that is then compared as equal.
    """
    names = [name for name in raw.replace(" ", "").split(",") if name]
    if not names:
        return "0"
    mask = 0
    for name in names:
        index = _CAPABILITY_BITS.get(name)
        if index is None:
            return "unreadable"
        mask |= 1 << index
    return _shaped(format(mask, "x"), "mask")


def _capability_masks(text: str) -> list[tuple[str, str]]:
    """`capsh --print`, read in the format `capsh` actually produces — **R13**.

    ## The defect this replaces — EH-R13-3

    The previous reader looked for `CapInh:`, `CapPrm:`, `CapEff:`, `CapBnd:` and
    `CapAmb:` at the start of a line. Those are `/proc/<pid>/status` field names.
    **`capsh --print` prints none of them.** It prints a textual `Current:`
    capability specification, a `Bounding set =` name list, an `Ambient set =`
    name list and a `Securebits:` line, so against real `capsh` output this
    reader found no mask at all and `P-01`'s observation was a single securebits
    value — which the executor then compared against nothing. A synthetic
    `CapBnd: 0000000000000000` satisfied a reader no `capsh` could satisfy, which
    is the shape of the finding: a capture format checked against an imagined
    producer rather than the named one.

    ## What is read, and what is deliberately not

    Four keys, and they are `P-01`'s stated purpose — *"read the launching
    process's bounding set and securebits"*:

    * `bounding_set` and `ambient_set`, as the **masks** the names `capsh` prints
      stand for — see `_capability_mask` for why the conversion happens on this
      side. They are compared against `E7`'s reviewed `cap_bnd` and `cap_amb`
      target facts, which are the same two facts stated in the same encoding.
    * `securebits`, taken from the line's **hexadecimal** field, so it is the
      same encoding `prctl(PR_GET_SECUREBITS)` reports through the case program
      and the two can be compared against one reviewed fact rather than two.
    * `no_new_privs`, which `capsh` reports on the same line.

    The `Current:` line is **not** read. It is a libcap-formatted specification
    (`=ep`, `cap_net_raw+i`, …) rather than a value, its spelling varies with the
    library version, and no reviewed expectation is stated in it. A key nothing
    compares is a key that should not reach an artifact.

    A libcap old enough not to print `(no-new-privs=…)` produces no
    `no_new_privs` key, the reviewed contract's `MISSING_KEY` refusal fires, and
    the run stops. That is the intended direction: an unread prerequisite is a
    refusal, never a pass.
    """
    found: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Bounding set"):
            _, separator, raw = stripped.partition("=")
            if separator:
                found["bounding_set"] = _capability_mask(raw)
        elif stripped.startswith("Ambient set"):
            _, separator, raw = stripped.partition("=")
            if separator:
                found["ambient_set"] = _capability_mask(raw)
        elif stripped.startswith("Securebits:"):
            fields = stripped[len("Securebits:"):].strip().split("/")
            hexadecimal = fields[1].strip() if len(fields) > 1 else ""
            candidate = hexadecimal[2:] if hexadecimal.startswith("0x") else ""
            found["securebits"] = (
                candidate.lower() if _HEX_MASK.match(candidate) else "unreadable"
            )
            _, separator, tail = stripped.partition("no-new-privs=")
            if separator:
                digits = ""
                for character in tail:
                    if character.isdigit():
                        digits += character
                    else:
                        break
                found["no_new_privs"] = digits if digits else "unreadable"
    return [(key, found[key]) for key in sorted(found)]


def _group_members(text: str) -> list[tuple[str, str]]:
    """`name:x:gid:member,member`. The member list is recorded as a sorted,
    comma-joined set, because `identity.classify_group_membership` compares as a
    set and recording the order would record something the case does not use."""
    line = text.strip().splitlines()[0] if text.strip() else ""
    fields = line.split(":")
    if len(fields) < 4:
        return [("parse", "unreadable")]
    return [
        ("group", _shaped(fields[0], "name")),
        ("gid", _shaped(fields[2], "number")),
        # `none` rather than `""` — R13. An empty *value* is this module's marker
        # for *"nothing was read"*, and `expectations.ObservationContract.check`
        # refuses one as unreadable, so a group with no explicit member — which
        # is what §2.12.2 says `freedomcoord`, `freedomsheet` and `fbprobe` are —
        # could never satisfy a contract while its emptiness was spelled that
        # way. An empty set is an observation, and `EMPTY_SET` says so.
        ("members", _name_set(fields[3])),
    ]


def _account_identity(text: str) -> list[tuple[str, str]]:
    """`uid=113(freedomsheet) gid=118(freedomsheet) groups=…`.

    The **names** are recorded and the numeric ids are recorded; nothing else on
    the line is. Numbers matter because §2.13.5c's `capsh` construction is about
    numeric ids, and names matter because §2.12.2's matrix is about names.
    """
    line = text.strip().splitlines()[0] if text.strip() else ""
    observations: list[tuple[str, str]] = []
    for field in line.split():
        key, _, raw = field.partition("=")
        if key not in ("uid", "gid", "groups") or not raw:
            continue
        if key == "groups":
            names = sorted(
                part.split("(", 1)[1].rstrip(")")
                for part in raw.split(",")
                if "(" in part and part.endswith(")")
            )
            # `none` for the empty set, for `_group_members`' reason — R13.
            observations.append(
                ("groups", _shaped(",".join(names), "name_list") if names else "none")
            )
        else:
            observations.append((key, _shaped(raw.split("(", 1)[0], "number")))
            if "(" in raw:
                observations.append(
                    (f"{key}_name", _shaped(raw.split("(", 1)[1].rstrip(")"), "name"))
                )
    return observations or [("parse", "unreadable")]


def _attribute_flags(text: str) -> list[tuple[str, str]]:
    """`lsattr` prints `-----a--------------- /path`. Only the flag field is
    read: the path to its right is a string the run already knows.

    **R13, EH-R13-3.** The two flags §2.13.3 is about are recorded as a yes/no
    each, and the remaining letters are not recorded at all. The previous version
    recorded the whole sorted letter set, which cannot be compared against a
    reviewed expectation without the plan knowing the host's filesystem: `e` —
    *extent format* — is present on every ext4 inode and absent on other
    filesystems, so the expected letter set was a host fact wearing the clothes
    of a plan constant. `append_only` and `immutable` are exactly what the plan
    sets with `chattr` and exactly what the cases assert, and they are the same
    on every filesystem that implements the flags.
    """
    line = text.strip().splitlines()[0] if text.strip() else ""
    flags = line.split(" ", 1)[0] if line else ""
    if not _FLAG_LETTERS.match(flags):
        return [("parse", "unreadable")]
    letters = {character for character in flags if character != "-"}
    return [
        ("append_only", "yes" if "a" in letters else "no"),
        ("immutable", "yes" if "i" in letters else "no"),
    ]


def _mount_facts(text: str) -> list[tuple[str, str]]:
    """`findmnt --noheadings --output FSTYPE,SOURCE,OPTIONS`.

    The whole option string is **not** recorded — it can be long and carries
    settings unrelated to the question. Only the two facts §2.13.2a Stage 3 asks
    for survive: the filesystem type and whether the mount is read-only.

    **R13, EH-R13-3.** All three are now compared rather than recorded, against
    `approved_target.APPROVED_TARGET_FACTS` — the filesystem type and backing
    device Peter Duscha confirmed for this target on 2026-09-05, which is an
    independent reviewed source and not something this observation supplies.
    Stage 3's whole point is that an append-only result taken on a different
    filesystem attributes nothing, and that claim is only made by comparing.
    """
    line = text.strip().splitlines()[0] if text.strip() else ""
    fields = line.split()
    if len(fields) < 3:
        return [("parse", "unreadable")]
    options = {option.split("=", 1)[0] for option in fields[2].split(",")}
    return [
        ("fstype", _shaped(fields[0], "fstype")),
        ("source", _shaped(fields[1], "device")),
        ("read_only", "yes" if "ro" in options else "no"),
    ]


def _file_mode(text: str) -> list[tuple[str, str]]:
    """`stat --format=%u %g %a %F` — four fields, and no path."""
    fields = (text.strip().splitlines()[0] if text.strip() else "").split(None, 3)
    if len(fields) < 4:
        return [("parse", "unreadable")]
    return [
        ("uid", _shaped(fields[0], "number")),
        ("gid", _shaped(fields[1], "number")),
        ("mode", _shaped(fields[2], "mode")),
        ("file_type", _shaped(fields[3], "words")),
    ]


def _catalog_membership(
    text: str, question: "CatalogQuestion | None"
) -> list[tuple[str, str]]:
    """One PostgreSQL catalog listing, read as two yes/no answers — **R14**.

    ## The defect this exists for — Blocking finding EH-R14-1

    The database and role baselines proved absence with a **failure**: `psql`
    exit 2 for the database and exit 3 for `SET ROLE`. Neither status is an
    absence result. PostgreSQL documents exit 2 as a connection failure, and
    `pg_database.datallowconn = false` stops a connection to a database that is
    plainly there; exit 3 is any statement error under `ON_ERROR_STOP=1`. A
    pre-existing evidence database that refused connections therefore satisfied
    the baseline, granted this run ownership of somebody else's database, and
    left cleanup entitled to `DROP DATABASE` it. The control connection to
    `postgres` said nothing about it: it is a different object.

    The correction is that absence is now proved by a listing the catalog
    **returns**. `SELECT datname FROM pg_database` succeeds or the step is not
    satisfied, and what it returns is compared with two names the reviewed plan
    states.

    ## Why the answer is computed here and the listing is not recorded

    This module's rule is that raw output has no representation that survives it.
    A catalog listing is other people's database and role names — operational
    data this harness has no business putting in an artifact — and it is
    unbounded: `MAX_VALUE_LENGTH` is 120 characters and the predefined `pg_*`
    roles alone are three times that, so recording the list would mean either
    raising a reviewed limit or recording `unreadable` for every real host. Two
    yes/no answers about names a reviewer already approved are the whole
    observation, and nothing else about the catalog reaches an artifact.

    ## Three states, and only one of them is *absent*

    * **absent** — the listing was read, it carries the control, and it does not
      carry the subject: `subject_present=no`, `control_present=yes`;
    * **present** — it carries the subject, so the reviewed expectation fails and
      the run stops before any mutation; and
    * **unknown** — no question was declared, the listing carries a line that is
      not a catalog name, or it does not carry the control. Each emits a marker
      key no contract admits, so the observation is refused, the step is not
      satisfied, and no ownership is established. *Unknown never authorizes a
      deletion*, which is the property EH-R14-1 found missing.
    """
    if question is None:
        # A step whose policy is this one and whose plan carried no question:
        # unknown, and refused rather than answered from an empty pair.
        return [CATALOG_QUESTION_MISSING_MARKER]
    names: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not _CATALOG_NAME.match(stripped):
            return [MALFORMED_LINE_MARKER]
        names.add(stripped)
    return [
        ("control_present", "yes" if question.control in names else "no"),
        ("subject_present", "yes" if question.subject in names else "no"),
    ]


def _file_capabilities(text: str) -> list[tuple[str, str]]:
    """`getcap` prints nothing for a file with no capability. The **presence**
    is recorded as a yes/no rather than the capability string, because the case
    is *"is any set?"* and a set one stops the band regardless of which."""
    return [("file_capability_present", "no" if not text.strip() else "yes")]


#: The three case-program policies, as `key → shape`. **The key set is the
#: policy**, exactly as the colon-field index is `GROUP_MEMBERS`'s: a line whose
#: key is not in the map is dropped rather than recorded, so a future edit to the
#: case program cannot introduce an observation nobody reviewed, and the value is
#: additionally matched against the shape its field can legitimately have.
_KEY_VALUE_KEYS: dict[CapturePolicy, dict[str, str]] = {
    CapturePolicy.CASE_RESULT: {
        "verb": "token",
        "result": "token",
        "errno": "errno",
        "bytes_written": "number",
        "pre_size": "number",
        "post_size": "number",
        "st_rdonly": "number",
        "fs_append_fl": "number",
        # **Conflict C-6.** The immutable flag, reported by `getimmutable` and by
        # `clearimmutable`'s read-back. A separate key from `fs_append_fl`
        # because the two are separate bits reported by separate verbs, and a
        # shared key would let an append-only observation satisfy an
        # immutable-flag expectation.
        "fs_immutable_fl": "number",
        # **Conflict C-8.** `mkroot`'s ownership evidence: that this call created
        # the directory, and which object it created. The two numbers are what
        # ties the ownership to an inode rather than to a name, and `statroot`
        # reports the same two so cleanup can compare them before it removes
        # anything.
        "created": "yes_no",
        "root_device": "wide_number",
        "root_inode": "wide_number",
        "link_target": "token",
    },
    CapturePolicy.CASE_IDENTITY: {
        "verb": "token",
        "result": "token",
        "uid": "number",
        "gid": "number",
        "groups": "number_list",
        "cap_inh": "mask",
        "cap_prm": "mask",
        "cap_eff": "mask",
        "cap_bnd": "mask",
        "cap_amb": "mask",
        "no_new_privs": "number",
        # **R12, EH-R11-2.** The final securebits, observed inside the exec'd
        # process by `prctl(PR_GET_SECUREBITS)` — which is the only way the
        # kernel reports it, `/proc/self/status` carrying no such line. R11
        # asserted this value from the presence of a `capsh --secbits=` option
        # in the vector, which states an intent rather than observing a state.
        "securebits": "securebits",
    },
    CapturePolicy.CASE_RUNTIME: {
        "verb": "token",
        "result": "token",
        "interpreter": "absolute_path",
        "interpreter_real": "absolute_path",
        "python_version": "version",
        "interpreter_sha256": "digest",
        "isolated": "yes_no",
        "no_site": "yes_no",
        "third_party_importable": "yes_no",
        "case_program": "absolute_path",
        "case_program_sha256": "digest",
    },
    CapturePolicy.UNIT_DIRECTIVES: {
        "ProtectSystem": "token",
        "ReadWritePaths": "absolute_path",
        # **R13.** The ownership baseline asks `systemctl show` for this one
        # property and for nothing else: `not-found` is what says the transient
        # unit this run would create is not already loaded, and therefore what
        # says its `systemctl stop` reversal is reversing this run's own unit.
        "LoadState": "token",
    },
}


#: The two policies whose observation is compared, key by key, against a closed
#: semantic contract in `expectations.py`. **They are the strict ones**, and the
#: other two `key=value` policies are deliberately not: `CASE_RESULT` and
#: `UNIT_DIRECTIVES` are read by the bands rather than gated by a contract, and
#: broadening them because they happen to share this parser would change
#: behaviour nobody reviewed.
STRICT_CASE_POLICIES = frozenset(
    {CapturePolicy.CASE_IDENTITY, CapturePolicy.CASE_RUNTIME}
)

#: What a strict policy emits when the output carries a name outside its
#: reviewed key set, and when it carries a non-blank line that is not a
#: `key=value` record at all — finding **PR-20260907-3**.
#:
#: Two properties, and both are the finding:
#:
#: * **the key is outside every contract's reviewed key set**, so
#:   `ObservationContract.check()` classifies the observation `UNEXPECTED_KEY`
#:   and the step is not satisfied. Before this, the offending line was
#:   `continue`d — it vanished, the remaining valid pairs satisfied the
#:   contract, and the run was recorded as a pass. The contract's own
#:   unexpected/malformed classifications could never fire against real process
#:   output; they could only be produced by handing `check()` a tuple, which no
#:   run does.
#: * **neither marker carries one character of the offending line.** The rule
#:   this module exists for is that raw output has no representation that
#:   survives it, and *"record the unexpected text so somebody can see it"*
#:   would be the opposite of that. What survives is the fact that something
#:   unexpected was there.
UNEXPECTED_KEY_MARKER = ("capture_unexpected_key", "refused")
MALFORMED_LINE_MARKER = ("capture_malformed_line", "refused")

#: **R14, EH-R14-1.** What a `CATALOG_MEMBERSHIP` reading emits when the plan
#: declared no question for it. It is a key no contract admits, so the
#: observation is refused and the step is not satisfied — the *unknown* state,
#: which must never read as absence. Like the two markers above it carries no
#: character of the output.
CATALOG_QUESTION_MISSING_MARKER = ("capture_no_catalog_question", "refused")


def _case_observations(policy: CapturePolicy):
    """One `key=value` reader, bound to the key set its policy declares.

    The case program prints its keys sorted, so the observations come back in a
    fixed order without this function sorting anything.

    **A repeated key makes that key unreadable** — R12. A second line claiming a
    different value for a fact the first already stated is not a correction the
    harness may apply, and R11 dropped it silently, which left the first value
    standing as though nothing had happened. An `unreadable` value is an
    INCONCLUSIVE observation, which is a result, and the semantic expectation in
    `expectations.py` refuses it; a silently preferred first value is a result
    nobody could tell apart from a clean one.

    **An unexpected key or a malformed line refuses, for a strict policy** —
    PR-20260907-3. See `UNEXPECTED_KEY_MARKER` above for why, and for why the
    marker carries no text from the line that caused it.

    **The blank-line policy, stated.** A line that is empty or entirely
    whitespace is line termination and is *ignored*: `splitlines()` over
    ordinary output, output with a trailing newline, output with none, and
    output separated by blank lines must all read the same, and a terminator is
    not a record. Every other non-blank line must be `key=value` with a key the
    policy declares.
    """
    keys = _KEY_VALUE_KEYS[policy]
    strict = policy in STRICT_CASE_POLICIES

    def read(text: str) -> list[tuple[str, str]]:
        observations: list[tuple[str, str]] = []
        seen: set[str] = set()
        repeated: set[str] = set()
        unexpected_key = False
        malformed_line = False
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            key, separator, raw = stripped.partition("=")
            if not separator:
                malformed_line = True
                continue
            if key not in keys:
                unexpected_key = True
                continue
            if key in seen:
                repeated.add(key)
                continue
            seen.add(key)
            observations.append((key, _shaped(raw, keys[key])))
        if repeated:
            observations = [
                (key, "unreadable" if key in repeated else value)
                for key, value in observations
            ]
        # **First, not appended.** `_bounded` truncates to `MAX_OBSERVATIONS`, so
        # a marker added at the end could be cut off by a flood of unexpected
        # lines — and the flood would then be accepted, which is the defect with
        # an extra step.
        markers: list[tuple[str, str]] = []
        if strict and malformed_line:
            markers.append(MALFORMED_LINE_MARKER)
        if strict and unexpected_key:
            markers.append(UNEXPECTED_KEY_MARKER)
        return markers + observations or [("parse", "unreadable")]

    return read


_POLICIES = {
    CapturePolicy.EXIT_STATUS_ONLY: lambda text: [],
    CapturePolicy.CAPABILITY_MASKS: _capability_masks,
    CapturePolicy.GROUP_MEMBERS: _group_members,
    CapturePolicy.ACCOUNT_IDENTITY: _account_identity,
    CapturePolicy.ATTRIBUTE_FLAGS: _attribute_flags,
    CapturePolicy.MOUNT_FACTS: _mount_facts,
    CapturePolicy.FILE_MODE: _file_mode,
    CapturePolicy.FILE_CAPABILITIES: _file_capabilities,
    CapturePolicy.CASE_RESULT: _case_observations(CapturePolicy.CASE_RESULT),
    CapturePolicy.CASE_IDENTITY: _case_observations(CapturePolicy.CASE_IDENTITY),
    CapturePolicy.CASE_RUNTIME: _case_observations(CapturePolicy.CASE_RUNTIME),
    CapturePolicy.UNIT_DIRECTIVES: _case_observations(CapturePolicy.UNIT_DIRECTIVES),
}

#: The one policy whose reading needs something from the reviewed plan besides
#: the output: the two names it answers about — **R14, EH-R14-1**. It is a set
#: rather than a flag on the policy so that `sanitize` can refuse a question
#: supplied to any other policy, where it would mean nothing.
QUESTION_BEARING_POLICIES = frozenset({CapturePolicy.CATALOG_MEMBERSHIP})


#: Every key each policy can emit — **R13, EH-R13-3**.
#:
#: It is the *completeness* half of the semantic gate. `expectations` compares an
#: observation key by key and refuses a key outside its contract, so a contract
#: that omitted a key the sanitizer can produce would refuse every real run for
#: the wrong reason, and a contract that covered fewer keys than the policy emits
#: would leave the difference uncompared. `plan.CommandStep` therefore requires a
#: declared expectation for **exactly** this key set, which is checked when the
#: plan is built rather than discovered when a run stops.
#:
#: The two markers a strict policy can prepend — `capture_unexpected_key` and
#: `capture_malformed_line` — are deliberately **not** members: they exist to
#: make an observation fail its contract, so a contract that expected one would
#: undo them.
#:
#: `EXIT_STATUS_ONLY` emits nothing, which is why it is the empty set rather than
#: absent: a policy with no row here could not be checked at all.
POLICY_KEYS: dict[CapturePolicy, frozenset[str]] = {
    CapturePolicy.EXIT_STATUS_ONLY: frozenset(),
    CapturePolicy.CAPABILITY_MASKS: frozenset(
        {"bounding_set", "ambient_set", "securebits", "no_new_privs"}
    ),
    CapturePolicy.GROUP_MEMBERS: frozenset({"group", "gid", "members"}),
    CapturePolicy.ACCOUNT_IDENTITY: frozenset(
        {"uid", "uid_name", "gid", "gid_name", "groups"}
    ),
    CapturePolicy.ATTRIBUTE_FLAGS: frozenset({"append_only", "immutable"}),
    CapturePolicy.MOUNT_FACTS: frozenset({"fstype", "source", "read_only"}),
    CapturePolicy.FILE_MODE: frozenset({"uid", "gid", "mode", "file_type"}),
    CapturePolicy.FILE_CAPABILITIES: frozenset({"file_capability_present"}),
    CapturePolicy.CASE_RESULT: frozenset(_KEY_VALUE_KEYS[CapturePolicy.CASE_RESULT]),
    CapturePolicy.CASE_IDENTITY: frozenset(_KEY_VALUE_KEYS[CapturePolicy.CASE_IDENTITY]),
    CapturePolicy.CASE_RUNTIME: frozenset(_KEY_VALUE_KEYS[CapturePolicy.CASE_RUNTIME]),
    CapturePolicy.UNIT_DIRECTIVES: frozenset(
        _KEY_VALUE_KEYS[CapturePolicy.UNIT_DIRECTIVES]
    ),
    # **R14, EH-R14-1.** Both are compared, and the contract requires both: an
    # observation stating only that the subject is absent would not say whether
    # the catalog was read at all.
    CapturePolicy.CATALOG_MEMBERSHIP: frozenset(
        {"subject_present", "control_present"}
    ),
}

#: The policies whose emitted key set depends on **what was asked for**, so a
#: step declares the subset it produces rather than all of `POLICY_KEYS`. There
#: are two. `CASE_RESULT`'s depends on the verb and on whether the operation
#: returned: `open` reports three keys, a refusal reports the same three, and
#: `pwrite` reports three more. `UNIT_DIRECTIVES`' depends on which `--property=`
#: options the vector carries, and `systemctl show` prints exactly those. Every
#: other policy emits its complete set or nothing.
VARIABLE_KEY_POLICIES = frozenset(
    {CapturePolicy.CASE_RESULT, CapturePolicy.UNIT_DIRECTIVES}
)


def sanitize(
    policy: CapturePolicy,
    output: str,
    *,
    catalog: "CatalogQuestion | None" = None,
) -> tuple[tuple[str, str], ...]:
    """The only route from a command's output to an observation.

    Every value that leaves here has passed `_clean`, so it is at most
    `MAX_VALUE_LENGTH` characters of a narrow character class. A secret sentinel
    planted in a command's output cannot reach an artifact through any policy:
    either it is not in the field the policy reads, or it fails `_SAFE_VALUE`, or
    it is longer than the bound — and in the one case where a sentinel is short
    and alphanumeric enough to survive `_clean`, it can only appear as the value
    of a field whose meaning the reviewed plan already fixed.
    """
    if not isinstance(policy, CapturePolicy):
        raise ValueError("A capture policy is one of the closed set.")
    if catalog is not None and policy not in QUESTION_BEARING_POLICIES:
        raise ValueError(
            "A catalog question is supplied only to the policy that answers "
            "one. Handing it to another policy would mean the plan and the "
            "reading disagree about what this step observes."
        )
    if not isinstance(output, str):
        return (("parse", "unreadable"),)
    if policy in QUESTION_BEARING_POLICIES:
        observations = _catalog_membership(output, catalog)
    else:
        observations = _POLICIES[policy](output)
    return _bounded([(name, _clean(value)) for name, value in observations])


__all__ = [
    "CATALOG_QUESTION_MISSING_MARKER",
    "CapturePolicy",
    "CatalogQuestion",
    "POLICY_KEYS",
    "VARIABLE_KEY_POLICIES",
    "MALFORMED_LINE_MARKER",
    "MAX_OBSERVATIONS",
    "MAX_VALUE_LENGTH",
    "QUESTION_BEARING_POLICIES",
    "STRICT_CASE_POLICIES",
    "UNEXPECTED_KEY_MARKER",
    "sanitize",
]
