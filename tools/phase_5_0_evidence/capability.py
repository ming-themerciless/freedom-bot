"""`JNL-49` / `JNL-50`: the eight evidence identities `E1 … E8`, the `capsh(1)`
construction that produces them, and the classification of every case run under
one.

## Why the masks are derived rather than transcribed

Revision 10's identities *"did not exist"*: five of the eight were built with
`setpriv --securebits=+keep_caps,…`, which util-linux 2.39.3 rejects at parsing,
and the declared bounding sets disagreed with what the recipes would have
produced because nobody had derived one from the other. Revision 11 replaced the
mechanism with `capsh`, whose manual page guarantees it acts on options *"in the
order they are provided"*, and re-derived every mask.

This module keeps that property mechanical. `EvidenceIdentity.capability_set` is
the authoritative statement; `expected_masks()` computes `CapPrm`, `CapEff`,
`CapInh`, `CapAmb` and `CapBnd` from it by the seven-step derivation, and
`capsh_argv()` emits the invocation. **The mask and the recipe come from the same
place**, so they cannot drift — which is the failure mode the revision-11
mask-versus-recipe comparison exists to catch.

## The two control forms

* **C-I — vary one capability.** Same uid, gid, supplementary list, securebits,
  case binary, path, inode and mount; one capability differs. `E4 → E6` isolates
  `CAP_FOWNER`; `E1 → E2` isolates `CAP_LINUX_IMMUTABLE`.
* **C-II — vary the inode's owner.** Same identity, same syscall, same directory,
  same mode, same mount; two files created identically by the root harness, one
  root-owned and one `freedomsheet`-owned. This is the control for `JNL-50` case
  4, where no identity one capability apart from `E2` exists.

`control_form_for()` states which form a pair is, and refuses a pair that is
neither — so a case cannot be given a control that differs in more than the thing
under test. That is the revision-11 correction: `E2` as the control for an `E4`
refusal differs in uid, supplementary groups **and two capabilities**, and
isolates nothing.

## The prerequisite nobody can work around

**No tool can add a capability to a bounding set.** `capsh` offers `--drop` and
no addition at all. Every capability any identity needs must therefore already be
in the bounding set of the process that launches the harness, and
`classify_launcher_bounding_set()` reads that set first and returns
`INCONCLUSIVE` when it is short — *"no case is reported as passed or refused"*.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Sequence

from .errors import ObservationRefused, PlanRefused
from .identity import CANONICAL_ACCOUNTS, CANONICAL_GROUPS
from .records import (
    CaseRole,
    CleanupState,
    EvidenceRecord,
    ObservedIdentity,
    Outcome,
)

BAND = "capability"

#: Capability index → name, for the four this design constructs plus the three
#: the construction itself needs. Indices are `capabilities(7)`'s.
CAP_DAC_OVERRIDE = 1
CAP_DAC_READ_SEARCH = 2
CAP_FOWNER = 3
CAP_SETGID = 6
CAP_SETUID = 7
CAP_SETPCAP = 8
CAP_LINUX_IMMUTABLE = 9

CAPABILITY_NAMES: Mapping[int, str] = {
    CAP_DAC_OVERRIDE: "cap_dac_override",
    CAP_DAC_READ_SEARCH: "cap_dac_read_search",
    CAP_FOWNER: "cap_fowner",
    CAP_SETGID: "cap_setgid",
    CAP_SETUID: "cap_setuid",
    CAP_SETPCAP: "cap_setpcap",
    CAP_LINUX_IMMUTABLE: "cap_linux_immutable",
}

#: The seven capabilities that must already be in the launching process's
#: bounding set, because `capsh` can only ever remove.
REQUIRED_LAUNCHER_CAPABILITIES = (
    CAP_LINUX_IMMUTABLE,
    CAP_FOWNER,
    CAP_DAC_OVERRIDE,
    CAP_DAC_READ_SEARCH,
    CAP_SETPCAP,
    CAP_SETUID,
    CAP_SETGID,
)

#: `SECBIT_NO_SETUID_FIXUP`, which is `1 << SECURE_NO_SETUID_FIXUP` and
#: `SECURE_NO_SETUID_FIXUP` is 2. Step 1 of the construction sets exactly this and
#: clears every other securebit. `SECBIT_KEEP_CAPS` is not set, is not needed and
#: is not used.
SECBITS_NO_SETUID_FIXUP = 4

#: `/proc/1/status` on this host on 2026-08-31 (§8.1 **H-6**): every capability
#: 0…40, `CAP_LAST_CAP` being 40 on kernel 6.8.0-138-generic. **On a kernel with a
#: different `CAP_LAST_CAP` this value is wrong**, which is why `classify_root_
#: masks()` compares the document's copy with the host's and reports
#: `INCONCLUSIVE` on disagreement rather than silently preferring either.
DOCUMENTED_ROOT_MASK = 0x000001FFFFFFFFFF
DOCUMENTED_CAP_LAST_CAP = 40

# ---------------------------------------------------------------------------
# `E7`'s reviewed target facts — R13
# ---------------------------------------------------------------------------

#: The sentinel every reviewed `E7` target fact carries until the Operations
#: Owner states it **for the current target** and an independent reviewer
#: verifies it there.
E7_FACT_UNCONFIRMED = "UNCONFIRMED"

#: `E7` is the harness's own root process, and R13 makes it a real `CASE_IDENTITY`
#: step like the other seven: the `identity` verb runs in the final interpreted
#: process, `prctl(PR_GET_SECUREBITS)` reads the securebits there, and the
#: complete twelve-value observation is compared before any operation whose
#: attribution depends on `E7`.
#:
#: **Ten of those twelve values are facts about a host, and this repository does
#: not know them.** `verb` and `result` are the case program's own two literals
#: and are stated in the contract; every other key is `E7`'s *environment* —
#: which is precisely what §2.13.5c says when it labels `E7`'s masks
#: *"environment-derived"* and *"read, not derived"*. There is no seven-step
#: construction to derive them from, because nothing is constructed: no
#: `capsh`, no drop, no `--uid=`, no `--groups=`, and therefore no bound vector
#: to take a number out of. The three sources the other seven identities use do
#: not exist for this one.
#:
#: So each is a **reviewed target fact**, in exactly the sense
#: `case_runtime.EXPECTED_INTERPRETER_SHA256` and
#: `EXPECTED_INTERPRETER_REAL_PATH` are, and it ships `UNCONFIRMED` for exactly
#: the same reason: establishing it requires reading `oracle-test`, which no
#: authorization in force grants. While any one of them is unconfirmed the
#: executor refuses **before it starts any command** — see
#: `ExecutingRunner.__post_init__` — and the contract cannot be built at all, so
#: there is no path on which an unconfirmed fact becomes a comparison that
#: passes.
#:
#: **`DOCUMENTED_ROOT_MASK` is deliberately not used here.** It was read from
#: `/proc/1/status` on *this* host on 2026-08-31 for §8.1 **H-6**; it is a fact
#: about a host and a kernel, and a value observed on another host or another
#: `CAP_LAST_CAP` is not a fact about `oracle-test`. It remains what
#: `classify_root_masks()` compares the host's PID-1 mask with — a documented
#: value under review — and it is never an executable expectation.
#:
#: Values are stated in the **exact text form the case program prints**: decimal
#: for `uid`, `gid` and `no_new_privs`; a comma-separated decimal set for
#: `groups`; lower-case hexadecimal without a `0x` prefix for the five masks and
#: the securebits. `e7_expected_values()` parses them; nothing else reads them.
E7_TARGET_FACTS: Mapping[str, str] = {
    "uid": E7_FACT_UNCONFIRMED,
    "gid": E7_FACT_UNCONFIRMED,
    "groups": E7_FACT_UNCONFIRMED,
    "cap_inh": E7_FACT_UNCONFIRMED,
    "cap_prm": E7_FACT_UNCONFIRMED,
    "cap_eff": E7_FACT_UNCONFIRMED,
    "cap_bnd": E7_FACT_UNCONFIRMED,
    "cap_amb": E7_FACT_UNCONFIRMED,
    "no_new_privs": E7_FACT_UNCONFIRMED,
    "securebits": E7_FACT_UNCONFIRMED,
}

#: The shape each stated fact must have, matched before it is parsed. A fact the
#: capture boundary could never report in that shape is refused here rather than
#: compared against forever — the rule `case_runtime.interpreter_real_path_
#: confirmed()` applies to the resolved interpreter path.
#:
#: The securebits shape admits two hexadecimal digits, which is `0 … 0xff`, which
#: is `case_runtime.SECUREBITS_MAX`: `securebits.h` defines eight bits and a
#: wider value would be evidence that something other than securebits was
#: stated. The bound is expressed as the shape rather than imported, so this
#: module keeps its existing import direction; `tests/phase_5_0_evidence/
#: test_root_identity.py` asserts the two agree.
_E7_FACT_SHAPES: Mapping[str, "re.Pattern[str]"] = {
    "uid": re.compile(r"\A[0-9]{1,10}\Z"),
    "gid": re.compile(r"\A[0-9]{1,10}\Z"),
    "groups": re.compile(r"\A[0-9]{1,10}(?:,[0-9]{1,10})*\Z"),
    "cap_inh": re.compile(r"\A[0-9a-f]{1,16}\Z"),
    "cap_prm": re.compile(r"\A[0-9a-f]{1,16}\Z"),
    "cap_eff": re.compile(r"\A[0-9a-f]{1,16}\Z"),
    "cap_bnd": re.compile(r"\A[0-9a-f]{1,16}\Z"),
    "cap_amb": re.compile(r"\A[0-9a-f]{1,16}\Z"),
    "no_new_privs": re.compile(r"\A[0-9]{1,10}\Z"),
    "securebits": re.compile(r"\A[0-9a-f]{1,2}\Z"),
}


def e7_fact_confirmed(name: str) -> bool:
    """Whether one reviewed `E7` target fact has been stated in its shape."""
    shape = _E7_FACT_SHAPES.get(name)
    if shape is None:
        raise PlanRefused(
            f"{name!r} is not one of E7's reviewed target facts "
            f"{sorted(_E7_FACT_SHAPES)}."
        )
    value = E7_TARGET_FACTS.get(name)
    return isinstance(value, str) and bool(shape.match(value))


def unconfirmed_e7_facts() -> tuple[str, ...]:
    """The names of the `E7` target facts still unstated, in a fixed order.

    **Names only.** They are keys this module declares, so they are safe to
    report; no value from `E7_TARGET_FACTS` and no observed value appears in a
    refusal built from this.
    """
    return tuple(
        name for name in sorted(_E7_FACT_SHAPES) if not e7_fact_confirmed(name)
    )


def e7_target_facts_confirmed() -> bool:
    """Whether **every** reviewed `E7` target fact is stated. Fail-closed: a
    single missing fact makes the whole set unusable, because a contract over
    nine of the ten would compare nine and let the tenth be anything."""
    return not unconfirmed_e7_facts()


def e7_expected_values() -> dict[str, object]:
    """The reviewed `E7` facts, parsed into the typed values the contract compares.

    `int` for `uid`, `gid`, `no_new_privs`, the five masks and the securebits;
    `frozenset[int]` for `groups`, because the kernel holds a set and recording
    its order would compare something no reviewed fact states.

    Raises while any fact is unconfirmed. That is the second of the two
    fail-closed gates: the executor already refuses before it starts anything,
    and if that gate were ever removed this one would still make the contract
    unbuildable, which `ExecutingRunner` records as
    `EXPECTATION_NOT_CONSTRUCTED` and never as a pass.
    """
    missing = unconfirmed_e7_facts()
    if missing:
        raise PlanRefused(
            "E7's reviewed target facts are not all stated for this target: "
            f"{list(missing)}. Each is a fact about the host the harness runs "
            "on — the uid and gid it executes as, its complete supplementary "
            "group set, its five capability masks, its NoNewPrivs and its final "
            "securebits — and establishing one requires reading the disposable "
            "host, which is a maintainer decision and not this harness's to "
            "take. Learning any of them from P-01, P-02 or from E7's own "
            "observation would make the comparison a check against itself."
        )
    values: dict[str, object] = {}
    for name in sorted(_E7_FACT_SHAPES):
        stated = E7_TARGET_FACTS[name]
        if name == "groups":
            values[name] = frozenset(int(part, 10) for part in stated.split(","))
        elif name.startswith("cap_") or name == "securebits":
            values[name] = int(stated, 16)
        else:
            values[name] = int(stated, 10)
    return values


def documented_root_masks() -> dict[str, int]:
    """§2.13.5c's **documented** `E7` row — read on 2026-08-31, not derived.

    It is what `classify_root_masks()` compares this host's PID-1 mask with, and
    what `declared_identity("E7", …)` builds the records tier's `ObservedIdentity`
    from. It is **not** an executable expectation and cannot become one:
    `EvidenceIdentity.expected_masks()` refuses `E7` outright, and the executor's
    contract is built from `E7_TARGET_FACTS` alone.
    """
    return {
        "cap_prm": DOCUMENTED_ROOT_MASK,
        "cap_eff": DOCUMENTED_ROOT_MASK,
        "cap_inh": 0,
        "cap_amb": 0,
        "cap_bnd": DOCUMENTED_ROOT_MASK,
        "securebits": 0,
    }

#: Every capability name from index 0 to `DOCUMENTED_CAP_LAST_CAP`, in index
#: order. `capsh --drop=` takes a **list of names**, and the construction's step 2
#: is `DROP(ALLCAPS \ M)` — a set difference this enumeration is the left-hand
#: side of. It is written out rather than asked of the host for the reason every
#: other reviewed fact is: a bounding set derived from whatever `capsh` happened
#: to know about is not the bounding set a reviewer approved.
#:
#: `capsh` accepts the literal `all`, and it is **not** used: `--drop=all` would
#: remove `M` as well, and no tool can put a capability back into a bounding set.
#: The enumeration is what makes the resulting set exactly `M`.
#:
#: On a kernel whose `CAP_LAST_CAP` is larger than 40 this list is short, and a
#: capability beyond it would survive the drop. That is not silently tolerated:
#: `P-02` decodes the documented mask on the host and `classify_root_masks()`
#: reports `INCONCLUSIVE` when the host and the document disagree, so the whole
#: band stops rather than reporting a bounding set nobody derived.
ALL_CAPABILITY_NAMES: tuple[str, ...] = (
    "cap_chown",
    "cap_dac_override",
    "cap_dac_read_search",
    "cap_fowner",
    "cap_fsetid",
    "cap_kill",
    "cap_setgid",
    "cap_setuid",
    "cap_setpcap",
    "cap_linux_immutable",
    "cap_net_bind_service",
    "cap_net_broadcast",
    "cap_net_admin",
    "cap_net_raw",
    "cap_ipc_lock",
    "cap_ipc_owner",
    "cap_sys_module",
    "cap_sys_rawio",
    "cap_sys_chroot",
    "cap_sys_ptrace",
    "cap_sys_pacct",
    "cap_sys_admin",
    "cap_sys_boot",
    "cap_sys_nice",
    "cap_sys_resource",
    "cap_sys_time",
    "cap_sys_tty_config",
    "cap_mknod",
    "cap_lease",
    "cap_audit_write",
    "cap_audit_control",
    "cap_setfcap",
    "cap_mac_override",
    "cap_mac_admin",
    "cap_syslog",
    "cap_wake_alarm",
    "cap_block_suspend",
    "cap_audit_read",
    "cap_perfmon",
    "cap_bpf",
    "cap_checkpoint_restore",
)


def mask_for(capabilities: Sequence[int]) -> int:
    """The hexadecimal mask §2.13.5c writes, computed from capability indices."""
    mask = 0
    for index in capabilities:
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise ObservationRefused("A capability is a non-negative index.")
        mask |= 1 << index
    return mask


@dataclass(frozen=True, slots=True)
class EvidenceIdentity:
    """One of `E1 … E8`, stated once and derived from thereafter."""

    name: str
    user: str
    primary_group: str
    #: The complete supplementary list, **taken from §2.12.2 through
    #: `identity.CANONICAL_GROUPS` and from nowhere else** — that is R11-B, and
    #: revision 11's `E8` was wrong precisely because it was stated here instead.
    supplementary_groups: tuple[str, ...]
    #: `M` in the construction: the capability set the identity carries.
    capability_set: tuple[int, ...]
    authorities: tuple[str, ...]
    #: True for the three identities §2.12.2 labels as corresponding to no
    #: provisioned identity at all.
    synthetic: bool
    note: str = ""

    def __post_init__(self) -> None:
        for group in self.supplementary_groups:
            if group not in CANONICAL_GROUPS:
                raise PlanRefused(
                    f"{self.name} names supplementary group {group!r}, which is not "
                    "in §2.12.2. Every group name in this table is taken from that "
                    "one and from nowhere else — remediation R11-B."
                )
        if self.user not in CANONICAL_ACCOUNTS and self.user != "root":
            raise PlanRefused(
                f"{self.name} names account {self.user!r}, which §2.12.2 does not "
                "provision."
            )

    @property
    def mask(self) -> int:
        return mask_for(self.capability_set)

    def expected_masks(self) -> dict[str, int]:
        """The five masks and the securebits, derived from `M` by the seven steps.

        Step 2 drops everything outside `M`, so `CapBnd = M`. Step 3 sets
        inheritable to `M`. Step 6 raises exactly `M` into the ambient set. Step 7
        execs a file carrying **no** file capabilities, so `P'(perm)` reduces to
        the ambient set and `P'(eff) = P'(amb)` — which is why the ambient set is
        the carrier, and why the pre-`execve` permitted set appears in no declared
        mask.
        """
        if self.name == "E7":
            raise PlanRefused(
                "E7 has no derivation. Nothing is constructed for it — no "
                "securebit is set, nothing is dropped — so there is no `M` for "
                "the seven steps to act on, and revision 12 returned the "
                "2026-08-31 host reading here as though it were one. It is not: "
                "it is a value read from `/proc/1/status` on **this** host, and "
                "a mask observed on another host or another CAP_LAST_CAP is not "
                "a fact about the target. The documented row is "
                "`documented_root_masks()`, which `classify_root_masks()` "
                "compares the host with; the executable expectation is "
                "`E7_TARGET_FACTS`, which ships unconfirmed. Neither is this."
            )
        mask = self.mask
        return {
            "cap_prm": mask,
            "cap_eff": mask,
            "cap_inh": mask,
            "cap_amb": mask,
            "cap_bnd": mask,
            "securebits": SECBITS_NO_SETUID_FIXUP,
        }

    def capsh_argv(
        self,
        *,
        case_program_argv: Sequence[str],
        all_capability_names: Sequence[str],
        resolve_uid,
        resolve_gid,
    ) -> tuple[str, ...]:
        """The complete invocation, in the order `capsh(1)` acts on options.

        `DROP(M)` is `ALLCAPS` with the members of `M` removed, order preserved —
        a **total** substitution over an enumerated constant, so the resulting
        bounding set is `M` whatever order the names appear in, because a
        bounding-set operation can only ever remove.

        Steps 3 and 6 are omitted when `M` is empty (`E1` and `E8`). Step 1 is
        still executed, so **E1 and E2 differ in `M` and in nothing else**.

        Step 7 is conflict **C-2**'s Option-B vector. `capsh` execs the program
        named by `--shell=` with the arguments after `--` as its `argv[1:]`, so
        `case_program_argv[0]` — the approved interpreter — becomes the shell and
        `case_program_argv[1:]` — `-I -S <case> <verb>` — becomes the rest of the
        vector. **The program the kernel runs is therefore named in this vector**,
        which is what Option B is and what a shebang would have hidden.

        `resolve_uid` and `resolve_gid` are the caller's. Passing the **symbolic
        name straight through** is what a plan does — the reviewed vector carries
        `--uid=freedomsheet` and the declared `binding.BindingSite`s say where the
        executor substitutes a number. Passing a real lookup is what a run does.
        """
        vector = tuple(case_program_argv)
        if len(vector) < 2:
            raise PlanRefused(
                f"{self.name}'s capsh construction execs the case program, so it "
                "is given that program's complete argument vector — the "
                "interpreter, its isolation flags, the program and the verb."
            )
        if self.name == "E7":
            raise PlanRefused(
                "E7 has no invocation. It is the harness's own root identity, "
                "constructed by not dropping, and its masks are read and asserted "
                "rather than constructed."
            )
        held = {CAPABILITY_NAMES[index] for index in self.capability_set}
        dropped = [name for name in all_capability_names if name not in held]
        groups = ",".join(
            str(resolve_gid(name))
            for name in (self.primary_group, *self.supplementary_groups)
        )
        argv: list[str] = [
            "/usr/sbin/capsh",
            f"--secbits={SECBITS_NO_SETUID_FIXUP}",
            f"--drop={','.join(dropped)}",
        ]
        if held:
            argv.append(f"--inh={','.join(sorted(held))}")
        argv.extend(
            [
                f"--gid={resolve_gid(self.primary_group)}",
                f"--groups={groups}",
                f"--uid={resolve_uid(self.user)}",
            ]
        )
        for name in sorted(held):
            argv.append(f"--addamb={name}")
        argv.extend([f"--shell={vector[0]}", "--", *vector[1:]])
        return tuple(argv)


#: `E1 … E8`, exactly as §2.13.5c states them after the revision-12 `E8`
#: correction. Every group name comes from §2.12.2 through `CANONICAL_GROUPS`.
EVIDENCE_IDENTITIES: Mapping[str, EvidenceIdentity] = {
    identity.name: identity
    for identity in (
        EvidenceIdentity(
            "E1", "freedomsheet", "freedomsheet", ("freedomjournal",), (),
            ("A2", "A10"), synthetic=False,
            note="freedomsheet as §2.12.2 provisions it; the writer's production "
                 "identity, whose CapabilityBoundingSet is empty.",
        ),
        EvidenceIdentity(
            "E2", "freedomsheet", "freedomsheet", ("freedomjournal",),
            (CAP_LINUX_IMMUTABLE,), ("A1", "A2", "A10"), synthetic=False,
            note="E1 plus an ambient CAP_LINUX_IMMUTABLE the deployed unit can "
                 "never hold. Differs from E1 in exactly one capability.",
        ),
        EvidenceIdentity(
            "E3", "fbprobe", "fbprobe", (), (CAP_LINUX_IMMUTABLE,), ("A1",),
            synthetic=True,
            note="Flag capability and nothing else. It owns no inode in the "
                 "hierarchy and holds no CAP_FOWNER, so it can change no flag.",
        ),
        EvidenceIdentity(
            "E4", "fbprobe", "fbprobe", (),
            (CAP_DAC_OVERRIDE, CAP_DAC_READ_SEARCH, CAP_LINUX_IMMUTABLE),
            ("A1", "A2", "A3", "A4", "A5", "A6"), synthetic=True,
            note="Every discretionary right and the flag capability, and still no "
                 "flag change: it holds neither A10 nor A11. The isolating case "
                 "for R9-A.",
        ),
        EvidenceIdentity(
            "E5", "fbprobe", "fbprobe", ("freedomcoord",),
            (CAP_FOWNER, CAP_LINUX_IMMUTABLE), ("A1", "A10", "A11"), synthetic=True,
            note="fbprobe plus a freedomcoord membership §2.12.2 provisions for "
                 "nobody. It exists to give a non-root identity …/archive traversal "
                 "while it clears a flag.",
        ),
        EvidenceIdentity(
            "E6", "fbprobe", "fbprobe", (),
            (CAP_DAC_OVERRIDE, CAP_DAC_READ_SEARCH, CAP_FOWNER, CAP_LINUX_IMMUTABLE),
            ("A1", "A2", "A3", "A4", "A5", "A6", "A10", "A11"), synthetic=True,
            note="E4 plus CAP_FOWNER, and identical in every other option. That is "
                 "what makes it the isolating control for E4.",
        ),
        EvidenceIdentity(
            "E7", "root", "root", (), (), ("A7",), synthetic=False,
            note="The harness's own process. No invocation; its masks are read from "
                 "/proc/self/status and asserted.",
        ),
        EvidenceIdentity(
            "E8", "freedomcoord", "freedomcoord", ("freedomjournal",), (),
            ("A8",), synthetic=False,
            note="freedomcoord as §2.12.2 provisions it. Revision 11 gave it "
                 "freedomcoord only, which is not the identity provisioning creates.",
        ),
    )
}


def declared_identity(name: str, *, uid: int, gid: int, group_ids: Sequence[int]) -> ObservedIdentity:
    """The `ObservedIdentity` a case asserts against, built from the declared masks.

    uid, gid and the supplementary gids are resolved on the host at run time —
    `freedomsheet`, `freedomcoord`, `freedomjournal` and `fbprobe` do not exist
    here, so every identifier in §2.13.5c is a **name** and the numeric value is
    substituted by the harness. Passing them in is what keeps this module free of
    a host lookup.
    """
    identity = EVIDENCE_IDENTITIES[name]
    # `E7` is read rather than derived, so the records tier takes the documented
    # §8.1 H-6 row. That row is review material for `CAP-E7-ENVIRONMENT` and is
    # never the executor's expectation — see `E7_TARGET_FACTS`.
    masks = (
        documented_root_masks()
        if identity.name == "E7"
        else identity.expected_masks()
    )
    return ObservedIdentity(
        uid=uid,
        gid=gid,
        groups=frozenset(group_ids),
        cap_prm=masks["cap_prm"],
        cap_eff=masks["cap_eff"],
        cap_inh=masks["cap_inh"],
        cap_amb=masks["cap_amb"],
        cap_bnd=masks["cap_bnd"],
        securebits=masks["securebits"],
        no_new_privs=0,
    )


def classify_launcher_bounding_set(observed_bounding_set: int) -> EvidenceRecord:
    """The prerequisite, asserted before anything is constructed.

    If any required capability is absent — a hardened unit, a container, a reduced
    login path — the run is `INCONCLUSIVE` and **no case is reported as passed or
    refused**.
    """
    missing = [
        CAPABILITY_NAMES[index]
        for index in REQUIRED_LAUNCHER_CAPABILITIES
        if not observed_bounding_set & (1 << index)
    ]
    required = mask_for(REQUIRED_LAUNCHER_CAPABILITIES)
    return EvidenceRecord.for_case(
        case_id="CAP-LAUNCHER-BND",
        band=BAND,
        target_identity="the launching process",
        operation="read CapBnd from /proc/self/status before constructing anything",
        preconditions=(
            "no tool can add a capability to a bounding set; capsh offers --drop "
            "and no addition at all",
        ),
        expected=Outcome.read(f"CapBnd ⊇ 0x{required:x}"),
        observed=Outcome.read(
            f"CapBnd ⊇ 0x{required:x}"
            if not missing
            else f"CapBnd missing {','.join(missing)}"
        ),
        case_role=CaseRole.STANDALONE,
        detail={"observed_bounding_set": f"0x{observed_bounding_set:x}"},
    )


def classify_root_masks(host_mask: int, host_cap_last_cap: int) -> EvidenceRecord:
    """`E7`'s masks are environment-derived, and are labelled as such.

    The harness re-reads `/proc/1/status` on the host it runs on, recomputes the
    expected value, and reports `INCONCLUSIVE` if the document's copy and the host
    disagree — it does not silently prefer either.
    """
    agrees = host_mask == DOCUMENTED_ROOT_MASK and host_cap_last_cap == DOCUMENTED_CAP_LAST_CAP
    return EvidenceRecord.for_case(
        case_id="CAP-E7-ENVIRONMENT",
        band=BAND,
        target_identity="E7",
        operation="compare §8.1 H-6's recorded root mask with this host's",
        preconditions=("E7's masks are read, not derived",),
        expected=Outcome.read(f"0x{DOCUMENTED_ROOT_MASK:x}/CAP_LAST_CAP={DOCUMENTED_CAP_LAST_CAP}"),
        observed=Outcome.read(f"0x{host_mask:x}/CAP_LAST_CAP={host_cap_last_cap}"),
        case_role=CaseRole.STANDALONE,
        detail={
            "documented_on": "2026-08-31, kernel 6.8.0-138-generic",
            "agrees": agrees,
        },
    )


@dataclass(frozen=True, slots=True)
class CapabilityCase:
    """One `JNL-49`/`JNL-50` case.

    `control_case_id` and `control_identity` are both required for a negative
    case, because the classifier will not interpret a refusal without a control
    that passed **and** the control form has to be checkable.
    """

    case_id: str
    identity_name: str
    operation: str
    target_path: str
    expected: Outcome
    control_case_id: str | None = None
    control_identity_name: str | None = None
    #: `"C-I"`, `"C-II"`, or `None` for a case that is itself a control or a read.
    control_form: str | None = None
    inode_owner: str = ""
    note: str = ""
    #: Declared, and checked against `control_case_id` rather than inferred from
    #: it: naming a reference says this case needs a control, and it does not say
    #: whether this case may be used as one.
    role: CaseRole = CaseRole.STANDALONE

    def __post_init__(self) -> None:
        names_control = self.control_case_id is not None
        if (self.role is CaseRole.DEPENDENT) != names_control:
            raise PlanRefused(
                f"Case {self.case_id!r} declares role {self.role.value!r} and "
                f"{'names' if names_control else 'names no'} control. A dependent "
                "case names exactly one; a control or a read names none."
            )


def control_form_for(case_identity: str, control_identity: str) -> str:
    """Which control form a pair is, or a refusal if it is neither.

    **C-I** requires the two identities to differ in exactly one capability and in
    nothing else. **C-II** requires them to be the same identity, the varied thing
    being the inode's owner. Anything else isolates nothing, and this raises
    rather than returning a label — the revision-11 correction is precisely that
    `E2` was named as the isolating control for an `E4` refusal while differing in
    uid, supplementary groups and two capabilities.
    """
    left = EVIDENCE_IDENTITIES[case_identity]
    right = EVIDENCE_IDENTITIES[control_identity]
    if left.name == right.name:
        return "C-II"
    same_process = (
        left.user == right.user
        and left.primary_group == right.primary_group
        and left.supplementary_groups == right.supplementary_groups
    )
    difference = set(left.capability_set) ^ set(right.capability_set)
    if same_process and len(difference) == 1:
        return "C-I"
    raise PlanRefused(
        f"{control_identity} is not an isolating control for {case_identity}: they "
        f"differ in {'the process identity and ' if not same_process else ''}"
        f"{len(difference)} capabilities. A refusal beside a control that differs "
        "in more than the thing under test is consistent with several explanations "
        "and isolates none of them."
    )


def classify_capability_case(
    case: CapabilityCase,
    *,
    observed_identity: ObservedIdentity | None,
    expected_identity: ObservedIdentity,
    observed: Outcome | None,
    control: EvidenceRecord | None = None,
) -> EvidenceRecord:
    """One case, with its identity asserted before its result.

    The order is `records.classify`'s and is not re-implemented here: identity
    first, control second, result third. What this function adds is the case's
    vocabulary — which identity, which control form, which inode owner — so the
    record is checkable against §2.13.5c without the harness.

    `control` is the control's **record** (EH-R2-1). Its status is read off that
    record, so `JNL-50`'s isolating control has to have actually passed for the
    refusal beside it to be interpreted at all — not merely to be asserted to
    have passed by whoever assembled the case.
    """
    if case.control_case_id is not None:
        if case.control_identity_name is None:
            raise PlanRefused(
                f"Case {case.case_id!r} names a control case without the identity "
                "that ran it, so the control form cannot be checked."
            )
        if control is None:
            raise ObservationRefused(
                f"Case {case.case_id!r} names control {case.control_case_id!r}; "
                "that control's record must be supplied, because a refusal beside "
                "a control that did not pass isolates nothing."
            )
        form = control_form_for(case.identity_name, case.control_identity_name)
        if case.control_form is not None and case.control_form != form:
            raise PlanRefused(
                f"Case {case.case_id!r} declares control form {case.control_form!r}; "
                f"the identities make it {form!r}."
            )
    identity = EVIDENCE_IDENTITIES[case.identity_name]
    return EvidenceRecord.for_case(
        case_id=case.case_id,
        band=BAND,
        target_identity=case.identity_name,
        operation=case.operation,
        preconditions=(
            "the launching process's bounding set contains every required capability",
            "the case binary carries no file capability and no set-user-ID bit",
            "every other prerequisite for this operation is satisfied",
        ),
        expected=case.expected,
        observed=observed,
        case_role=case.role,
        identity=observed_identity,
        expected_identity=expected_identity,
        positive_control_case_id=case.control_case_id,
        positive_control=control,
        cleanup_state=CleanupState.NOT_APPLICABLE,
        detail={
            "path": case.target_path,
            "inode_owner": case.inode_owner,
            "control_form": case.control_form,
            "authorities": ",".join(identity.authorities),
            "synthetic_identity": identity.synthetic,
            "note": case.note or identity.note,
        },
    )


__all__ = [
    "BAND",
    "ALL_CAPABILITY_NAMES",
    "CAPABILITY_NAMES",
    "CAP_DAC_OVERRIDE",
    "CAP_DAC_READ_SEARCH",
    "CAP_FOWNER",
    "CAP_LINUX_IMMUTABLE",
    "CAP_SETGID",
    "CAP_SETPCAP",
    "CAP_SETUID",
    "CapabilityCase",
    "DOCUMENTED_CAP_LAST_CAP",
    "DOCUMENTED_ROOT_MASK",
    "E7_FACT_UNCONFIRMED",
    "E7_TARGET_FACTS",
    "EVIDENCE_IDENTITIES",
    "EvidenceIdentity",
    "REQUIRED_LAUNCHER_CAPABILITIES",
    "SECBITS_NO_SETUID_FIXUP",
    "classify_capability_case",
    "classify_launcher_bounding_set",
    "classify_root_masks",
    "control_form_for",
    "declared_identity",
    "documented_root_masks",
    "e7_expected_values",
    "e7_fact_confirmed",
    "e7_target_facts_confirmed",
    "mask_for",
    "unconfirmed_e7_facts",
]
