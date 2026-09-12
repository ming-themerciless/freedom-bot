#!/usr/bin/env python3
"""Refuse tool calls that would read, print, copy or publish a secret file.

`.agents/AGENTS.md` "Configuration and secrets" states the rule as prose: never
read, print, commit or modify `.env`, `yt-cookies.txt`, service-account JSON,
Discord tokens, OAuth secrets, database URLs or Foundry credentials. Prose is an
instruction an agent can fail to apply. This hook makes the same rule a refusal.

## Why the Bash rule is narrower than the file-tool rule

For `Read`, `Edit`, `Write` and `NotebookEdit` the path is the whole subject, so
naming a secret artifact is refused outright.

A Bash command is different: the secret's *name* legitimately appears in
documentation, `.gitignore`, rsync exclude lists, test fixtures and this hook's
own tests. Refusing every mention produced immediate false positives, and a
guard with a high false-positive rate gets switched off, which is worse than a
narrower guard that stays on. So a Bash command is refused only when a secret
artifact appears together with a verb that would actually read, copy, publish or
stage it. Writing *about* `.env` is allowed; `cat`ting it is not.

`.env.example` is exempt throughout: AGENTS.md requires it to be kept current
with safe placeholders, so it is tracked, safe and editable.

Exit 2 blocks the call and returns stderr to the model.
"""
from __future__ import annotations

import json
import re
import sys

#: Patterns naming a secret-bearing artifact.
SECRET_PATTERNS = (
    r"(?<![\w.-])\.env(?!\.example\b)(?:\.[\w-]+)?\b",
    r"yt-cookies\.txt",
    r"[\w-]*service[_-]?account[\w-]*\.json",
    r"[\w-]*credentials?[\w-]*\.json",
    r"[\w./-]*\.pem\b",
    r"(?<![\w-])id_(?:rsa|ed25519|ecdsa)(?!\.pub)\b",
    r"\.pgpass\b",
)

#: Commands that would move a secret's *contents* somewhere: onto the terminal,
#: into another file, into Git, or off the host. Closed list, so adding an
#: exfiltration route is a deliberate edit to this file rather than an oversight.
ACCESS_VERBS = (
    r"\b(?:cat|bat|less|more|head|tail|strings|xxd|od|hexdump|base64|nl|tac)\b",
    r"\b(?:cp|mv|dd|tee|install|ln)\b",
    r"\b(?:scp|rsync|sftp|curl|wget|nc|ncat)\b",
    r"\b(?:tar|zip|gzip|7z)\b",
    r"\b(?:grep|rg|egrep|fgrep|sed|awk|cut|sort|uniq)\b",
    r"\bgit\s+(?:add|commit|stash|diff|show|log)\b",
    r"\b(?:source|export|printenv)\b",
    r"(?:^|[|;&`$(]\s*)\.\s",
)

#: The exemption, applied before matching.
EXEMPT = re.compile(r"\.env\.example\b", re.IGNORECASE)

#: Single- and double-quoted spans. A verb inside quotes is data, not a command:
#: `echo 'excluded by rsync'` names no rsync invocation. These spans are removed
#: before the verb search, so documenting a secret's name stays allowed while
#: `cat '.env'` stays refused - the secret is still found in the full text, and
#: the verb is still found outside the quotes.
QUOTED = re.compile(r"'[^']*'|\"[^\"]*\"")

SECRETS = [re.compile(p, re.IGNORECASE) for p in SECRET_PATTERNS]
VERBS = [re.compile(p, re.IGNORECASE) for p in ACCESS_VERBS]

#: Tool-input keys whose value is a path the tool will act on directly.
PATH_KEYS = ("file_path", "path", "notebook_path")


def _first_secret(text: str) -> str | None:
    stripped = EXEMPT.sub("", text)
    for pattern in SECRETS:
        match = pattern.search(stripped)
        if match:
            return match.group(0)
    return None


def _refuse(named: str, why: str) -> int:
    print(
        "Refused by the repository secrets guard "
        "(.agents/AGENTS.md, Configuration and secrets).\n"
        f"The call {why} {named!r}, a secret-bearing artifact that must never be "
        "read, printed, copied, modified or committed.\n"
        "If a secret may have entered Git history or logs, stop and notify a "
        "maintainer: deleting the visible line is insufficient and the "
        "credential must be rotated.\n"
        "`.env.example` is exempt and may be edited with safe placeholders.",
        file=sys.stderr,
    )
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        # A hook that cannot read its input must not silently allow the call.
        print("secrets guard: could not parse hook payload; refusing.", file=sys.stderr)
        return 2

    tool_input = payload.get("tool_input") or {}

    for key in PATH_KEYS:
        value = tool_input.get(key)
        if value:
            named = _first_secret(str(value))
            if named:
                return _refuse(named, "targets")

    command = str(tool_input.get("command") or "")
    if command:
        named = _first_secret(command)
        unquoted = QUOTED.sub(" ", command)
        if named and any(verb.search(unquoted) for verb in VERBS):
            return _refuse(named, "would read or publish")

    return 0


if __name__ == "__main__":
    sys.exit(main())
