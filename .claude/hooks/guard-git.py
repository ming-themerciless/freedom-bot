#!/usr/bin/env python3
"""Refuse Git operations the working agreement forbids an agent to take alone.

Two rules from `.agents/AGENTS.md` and the standing review restrictions:

* history is evidence and is never rewritten, and
* an agent does not commit or push on the default branch on its own initiative.

Both are currently prose. This hook makes them refusals. A maintainer who wants
one of these operations can run it themselves, which is the intended route.

Exit 2 blocks the call and returns stderr to the model.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

DEFAULT_BRANCHES = {"main", "master"}

#: Operations that rewrite or discard recorded history. Refused on any branch.
HISTORY_REWRITE = (
    (r"\bgit\b[^|;&]*\bpush\b[^|;&]*(--force\b|--force-with-lease\b|(?<![\w-])-f\b)",
     "a force push"),
    (r"\bgit\b[^|;&]*\breset\b[^|;&]*--hard\b", "a hard reset"),
    (r"\bgit\b[^|;&]*\bfilter-branch\b", "a history filter"),
    (r"\bgit\b[^|;&]*\bfilter-repo\b", "a history filter"),
    (r"\bgit\b[^|;&]*\brebase\b", "a rebase"),
    (r"\bgit\b[^|;&]*\breflog\b[^|;&]*\bdelete\b", "a reflog deletion"),
    (r"\bgit\b[^|;&]*\bcommit\b[^|;&]*--amend\b", "an amended commit"),
)

#: Operations that publish. Refused only on the default branch.
PUBLISHING = (
    (r"\bgit\b[^|;&]*\bcommit\b", "a commit"),
    (r"\bgit\b[^|;&]*\bpush\b", "a push"),
)


def current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print("git guard: could not parse hook payload; refusing.", file=sys.stderr)
        return 2

    command = str((payload.get("tool_input") or {}).get("command", ""))
    if not command:
        return 0

    for pattern, described in HISTORY_REWRITE:
        if re.search(pattern, command):
            print(
                f"Refused by the repository Git guard: this is {described}.\n"
                "Recorded history is evidence in this project and is not "
                "rewritten by an agent. Audit and review history is append-only; "
                "corrections are explicit compensating changes.\n"
                "If this is genuinely required, a maintainer runs it themselves.",
                file=sys.stderr,
            )
            return 2

    branch = current_branch()
    if branch in DEFAULT_BRANCHES:
        for pattern, described in PUBLISHING:
            if re.search(pattern, command):
                print(
                    f"Refused by the repository Git guard: this is {described} on "
                    f"the default branch {branch!r}.\n"
                    "Branch first, or ask the maintainer to publish. Commit and "
                    "push only when explicitly asked.",
                    file=sys.stderr,
                )
                return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
