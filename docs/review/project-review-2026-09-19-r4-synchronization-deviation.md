# Independent review — C-P5.0-LAB-V6-P-R4 synchronization deviation — 2026-09-19

## Disposition

Acceptance recommended and accepted. Peter Duscha accepts the explicitly
authorized, one-time `--exclude-from` synchronization deviation used during
C-P5.0-LAB-V6-P-R4. The supplied rules were identical to the runbook
exclusions, the maintainer performed the final synchronization, no secret-type
file appeared in the transfer evidence, and the target matched all 45 reviewed
source digests.

This acceptance is retrospective and pass-specific. It does not authorize
`--exclude-from` for future synchronization, which must use the accepted inline
runbook command.

## Basis

- The normal runbook command was first attempted and refused by the then-current
  secrets guard; the refusal was treated as a stop condition.
- Peter explicitly authorized the same exclusion policy through a temporary
  `--exclude-from` file for this pass only.
- The temporary file contained the runbook's inclusion and exclusion rules in
  the same order.
- A dry run completed before the real synchronization.
- Peter performed the final synchronization after the agent-side classifier
  refused it.
- The transfer evidence named no environment file, private key, certificate,
  cookie, service-account file or credentials file.
- All 45 reviewed source digests matched on the target after synchronization.
- LAB-V6-P3 subsequently corrected the guard so the inline runbook command is
  now admitted and was independently reviewed and accepted.

This decision approves no general indirect filter-file interface. Permanently
supporting `--exclude-from` would require a separately reviewed, fail-closed
contract for the rules file's identity and contents.
