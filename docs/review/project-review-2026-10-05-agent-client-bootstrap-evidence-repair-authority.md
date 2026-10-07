# Authority — retained bootstrap-remediation evidence repair

Date: 2026-10-05

Authority: Peter Duscha, Product Owner and Acceptance Authority

Work ID: `C-P5.0-ORACLE-AGENT-CLIENT-BOOTSTRAP-R1-20261005-03`

Peter Duscha authorizes Claude Code to execute the exact bounded assignment in
[`phase-5-0-agent-clients-bootstrap-remediation-evidence-repair-claude-prompt.md`](phase-5-0-agent-clients-bootstrap-remediation-evidence-repair-claude-prompt.md).

Claude may use the current workspace host only as an SSH controller for
`oracle-test`, inspect the fixed retained evidence and bounded absence metadata,
and write only the exclusive repair-evidence directory named by the prompt.
This overrides the current handover's general prohibition on an evidence pass
only for this work ID and exact assignment.

The authority does not permit rerunning bootstrap or remediation commands,
running either client, inspecting the installed prefix, accessing the remote
repository, authenticating, using credentials or `sudo`, installing or updating
anything, using services or databases, running tests or builds, performing
cleanup, or beginning H-0, H-1/H-2, activation or rollback.

The assignment terminates at its first defined outcome:
`EVIDENCE REPAIR COMPLETE` or `HARD STOP`. It is one-shot: no retry, repair or
extension is authorized. H-0 remains unauthorized pending a separate recorded
assignment.
