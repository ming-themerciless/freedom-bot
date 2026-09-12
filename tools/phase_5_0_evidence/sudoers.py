"""Check **C-1**: what a `sudoers` drop-in actually grants, analysed from content
an authorized reader supplies.

`/etc/sudoers.d` is `0750` and unreadable without elevation — confirmed again by
the non-elevated preflight on 2026-09-02. **This module reads nothing.** It takes
the text an authorized privileged reader captured, together with the file's
metadata, and answers the four questions §2.12.4 and §2.13.7 rest on:

* is the permitted command **one fixed absolute path**, with no wildcard and no
  path a caller could redirect;
* is `NOPASSWD` absent, so an authority cutover re-authenticates;
* are `env_reset`, `!setenv` and `secure_path` present, so `PYTHONPATH`,
  `LD_PRELOAD` and the `PG*` family are discarded at the boundary; and
* is `log_output` present, so one of the three independent audit records §2.12.7
  requires actually exists.

## What reaches an evidence record, and what never does

A `SudoersAnalysis` carries **finding codes, counts, the file's mode and owner as
supplied, and the SHA-256 of the supplied bytes**. It never carries a line, a
principal, a host pattern or a command from an unrelated drop-in. C-1's whole
purpose is to discover whether *some other rule* widens `foundry`'s authority
(§2.12.6), so this module must be able to say *"drop-in 4 grants `ALL` with
`NOPASSWD`"* without copying that rule into a document under `docs/review/`. It
does: the finding names the drop-in and the class of the rule, and the reviewer
who can read the file reads the file.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Sequence

from .errors import ObservationRefused

#: The two `Cmnd_Alias` targets §2.12.4 and §2.13.7 define.
EXPECTED_COMMANDS = (
    "/opt/freedom-blades/coordinator/bin/migration-authority",
    "/opt/freedom-blades/coordinator/bin/freedom-journal-admin",
)

#: The `Defaults` this design requires on its own alias.
REQUIRED_DEFAULTS = ("env_reset", "!setenv", "log_output", "secure_path=")

_WILDCARD = re.compile(r"[*?\[\]]")
_RUNAS = re.compile(r"\(([^)]*)\)")

#: `sudoers` tags that prefix a command in a rule. They are stripped before a
#: command is resolved, because `NOPASSWD: FREEDOM_ALIAS` is one tagged reference
#: to an alias and not a relative command called `NOPASSWD:`.
_TAG = re.compile(r"\A(?:(?:NOPASSWD|PASSWD|NOEXEC|EXEC|SETENV|NOSETENV|LOG_INPUT|NOLOG_INPUT|LOG_OUTPUT|NOLOG_OUTPUT)\s*:\s*)+")


@dataclass(frozen=True, slots=True)
class SudoersFileFacts:
    """The metadata an authorized reader captures alongside the content.

    Mode and ownership are part of the control: `sudo` refuses a group- or
    world-writable drop-in, and §2.12.5 states `root:root 0440` explicitly *"so a
    deploy cannot get it wrong quietly"*.
    """

    name: str
    owner: str
    group: str
    mode: str
    byte_count: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ObservationRefused("A drop-in has a name.")
        if not re.fullmatch(r"0[0-7]{3}", self.mode or ""):
            raise ObservationRefused(
                f"{self.mode!r} is not an octal mode such as '0440'."
            )


@dataclass(frozen=True, slots=True)
class SudoersFinding:
    code: str
    drop_in: str
    detail: str


@dataclass(frozen=True, slots=True)
class SudoersAnalysis:
    """The verdict for one drop-in. No rule text, ever."""

    drop_in: str
    content_sha256: str
    rule_count: int
    findings: tuple[SudoersFinding, ...]
    grants_to_service_identity: bool
    permits_unrestricted_command: bool

    @property
    def blocking_findings(self) -> tuple[SudoersFinding, ...]:
        return tuple(f for f in self.findings if f.code.startswith("SUDO-B"))

    @property
    def is_safe(self) -> bool:
        return not self.blocking_findings


#: Identities that must never appear as the invoker of a rule reaching a Package
#: 5.0 command. §2.12.4: *"`foundry` only. No service identity is named, and none
#: is in `sudo`."*
SERVICE_IDENTITIES = frozenset({"discordbot", "freedomweb", "freedomsheet", "freedomcoord"})


def _logical_lines(content: str) -> list[str]:
    """`sudoers` continues a line with a trailing backslash, and §2.12.4's own
    `Defaults` line is written that way.

    Joining is not cosmetic: without it the continuation is read as a *rule* whose
    command is not absolute, and the `Defaults` it belongs to is read as missing
    the directive that is sitting on the next line. Both are findings the file
    does not deserve, and a checker that produces them is one nobody will believe
    when it produces a real one.
    """
    joined: list[str] = []
    buffer = ""
    for raw in content.splitlines():
        text = raw.split("#", 1)[0].rstrip()
        if text.endswith("\\"):
            buffer += text[:-1].strip() + " "
            continue
        joined.append((buffer + text.strip()).strip())
        buffer = ""
    if buffer:
        joined.append(buffer.strip())
    return joined


def analyse_sudoers_drop_in(
    facts: SudoersFileFacts, content: str, *, is_package_drop_in: bool
) -> SudoersAnalysis:
    """Analyse one drop-in's supplied content.

    `is_package_drop_in` distinguishes the two files this design installs — which
    must additionally satisfy `REQUIRED_DEFAULTS` and name one of
    `EXPECTED_COMMANDS` — from every other drop-in on the host, which C-1 examines
    only for whether it widens the authority the design assumes is narrow.
    """
    if not isinstance(content, str):
        raise ObservationRefused("Sudoers content is supplied as text.")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    findings: list[SudoersFinding] = []

    if facts.owner != "root" or facts.group != "root":
        findings.append(
            SudoersFinding(
                "SUDO-B1",
                facts.name,
                f"Owned {facts.owner}:{facts.group}; §2.12.5 requires root:root.",
            )
        )
    if facts.mode not in ("0440", "0400"):
        findings.append(
            SudoersFinding(
                "SUDO-B2",
                facts.name,
                f"Mode {facts.mode}; §2.12.5 requires 0440. `sudo` refuses a group- "
                "or world-writable drop-in, so a wider mode is either refused at "
                "run time or is a mode nobody checked.",
            )
        )

    aliases: dict[str, list[str]] = {}
    defaults_text: list[str] = []
    rules: list[str] = []
    for line in _logical_lines(content):
        if not line:
            continue
        if line.startswith("Cmnd_Alias"):
            _, _, body = line.partition("Cmnd_Alias")
            name, _, commands = body.strip().partition("=")
            aliases[name.strip()] = [c.strip() for c in commands.split(",") if c.strip()]
        elif line.startswith("Defaults"):
            defaults_text.append(line)
        else:
            rules.append(line)

    grants_to_service_identity = False
    permits_unrestricted = False

    for rule in rules:
        invoker = rule.split()[0] if rule.split() else ""
        if invoker.lstrip("%") in SERVICE_IDENTITIES:
            grants_to_service_identity = True
            findings.append(
                SudoersFinding(
                    "SUDO-B3",
                    facts.name,
                    "A rule names a service identity as the invoker. §2.12.6's "
                    "second vector rests on no service identity being able to "
                    "`sudo` at all.",
                )
            )
        if "NOPASSWD" in rule:
            findings.append(
                SudoersFinding(
                    "SUDO-B4",
                    facts.name,
                    "A rule carries `NOPASSWD`. §2.12.4 is deliberate about this: "
                    "an authority cutover re-authenticates, because the command "
                    "changes which store the platform believes.",
                )
            )
        commands = rule.split("=", 1)[1] if "=" in rule else ""
        commands = _RUNAS.sub("", commands).strip()
        for token in (c.strip() for c in commands.split(",")):
            token = _TAG.sub("", token).strip()
            if not token:
                continue
            if token == "ALL":
                permits_unrestricted = True
                findings.append(
                    SudoersFinding(
                        "SUDO-B5",
                        facts.name,
                        "A rule permits `ALL`. Whatever else the drop-in says, this "
                        "grants every command to its invoker.",
                    )
                )
                continue
            resolved = aliases.get(token, [token])
            for command in resolved:
                if _WILDCARD.search(command):
                    findings.append(
                        SudoersFinding(
                            "SUDO-B6",
                            facts.name,
                            "A permitted command contains a wildcard. §2.12.4 "
                            "requires one fixed absolute path, because the rule "
                            "permits arguments and the executable must therefore be "
                            "one that cannot be told to run a different file.",
                        )
                    )
                elif not command.startswith("/"):
                    findings.append(
                        SudoersFinding(
                            "SUDO-B7",
                            facts.name,
                            "A permitted command is not an absolute path, so which "
                            "file runs depends on a search path.",
                        )
                    )
                elif is_package_drop_in and command not in EXPECTED_COMMANDS:
                    findings.append(
                        SudoersFinding(
                            "SUDO-B8",
                            facts.name,
                            "A Package 5.0 drop-in permits a command that is neither "
                            "`migration-authority` nor `freedom-journal-admin`.",
                        )
                    )

    if is_package_drop_in:
        joined = " ".join(defaults_text)
        for required in REQUIRED_DEFAULTS:
            if required not in joined:
                findings.append(
                    SudoersFinding(
                        "SUDO-B9",
                        facts.name,
                        f"`{required.rstrip('=')}` is absent from the drop-in's "
                        "`Defaults`. Without it the environment, the search path or "
                        "the I/O log the audit depends on is not what §2.12.4 "
                        "describes.",
                    )
                )
        if not rules:
            findings.append(
                SudoersFinding(
                    "SUDO-B10",
                    facts.name,
                    "The drop-in defines an alias and no rule, so it grants nothing "
                    "and the provisioning step did not complete.",
                )
            )

    return SudoersAnalysis(
        drop_in=facts.name,
        content_sha256=digest,
        rule_count=len(rules),
        findings=tuple(findings),
        grants_to_service_identity=grants_to_service_identity,
        permits_unrestricted_command=permits_unrestricted,
    )


def summarize_c1(analyses: Sequence[SudoersAnalysis]) -> tuple[SudoersFinding, ...]:
    """Every blocking finding across the whole directory, in file order.

    C-1 is a question about the directory rather than about one file — §2.12.6's
    row says *"Whether some **other** rule in `/etc/sudoers.d/` widens it is check
    C-1"* — so the summary is the directory's, and an empty result means every
    supplied drop-in was analysed and none of them did.
    """
    return tuple(finding for analysis in analyses for finding in analysis.blocking_findings)


__all__ = [
    "EXPECTED_COMMANDS",
    "REQUIRED_DEFAULTS",
    "SERVICE_IDENTITIES",
    "SudoersAnalysis",
    "SudoersFileFacts",
    "SudoersFinding",
    "analyse_sudoers_drop_in",
    "summarize_c1",
]
