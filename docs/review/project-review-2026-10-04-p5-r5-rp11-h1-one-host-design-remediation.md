# Independent re-review — `oracle-test` one-host H-1 design remediation

Date: 2026-10-04  
Reviewer: Codex  
Design author: Claude  
Work ID: `C-P5.0-R5-RP11-H1-D3-R1`

Reviewed return:
[`phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md`](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md).

## Outcome

Claude's **DESIGN REMEDIATION READY FOR RE-REVIEW** return is valid, but the
revised proposal is not yet decision-ready. `OH-H1-D3-1` is remediated: the
write-ahead identity protocol closes the final-name attribution window and
keeps H-1 rollback separately authorized. `OH-H1-D3-2` remains open because
the proposed activation cleanup does not enforce the accepted one-boot and
post-pass grant boundary after process/session loss or reboot.

I raise one Blocking finding. No Important or Optional finding is raised.
Nothing in this review accepts or activates the proposal.

## Finding

### Blocking `OH-H1-D3-R1-1` — cleanup after death or reboot is deferred, leaving a live grant after the authorized boot/pass

OH-D-7 says A-2 authorizes `ACT` for exactly one pass and one boot, `DEACT` is
mandatory at every terminal state, and no live Polkit grant may remain after
the pass. The remediation prompt correspondingly requires automatic cleanup
at every terminal state and handling for reboot and process death.

The revised design does not enforce that boundary. Section 4.2.5-R1(e)(3)
says that after death of `ACT`, loss of the executor session, or reboot,
`DEACT` is merely the first RP-11 action when an actor later reaches the host.
AC-10 and residual RR-2 explicitly allow the persistent rule to be loaded and
usable after reboot until that later action. The bootstrap's boot-ID refusal
does not disable the Polkit authorization and the proposal correctly declines
to credit it as prevention. Thus a grant authorized for the previous boot can
exist and be usable in the next boot, after the activation/pass has
terminated. Human-first-action cleanup is pre-authorized cleanup, but it is
not automatic cleanup and it does not make the one-boot boundary true.

This is a security and authorization defect, so it remains Blocking even on a
disposable host and even though `ubuntu` independently has unrestricted
`sudo`. OH-D-6 requires that limitation to be stated; it does not waive
OH-D-7 or U-8.

Required remediation: make the active grant mechanically incapable of
surviving its authorized boot/pass, or provide an automatically invoked,
fail-closed cleanup mechanism whose ordering and crash behavior are specified
at the same level as CL. The revised design must cover loss of the ACT/pass
process and session, power loss and reboot without depending on a later human
action. Any selected rule location or startup cleanup mechanism requires the
version-bound Polkit/systemd citations and host facts already contemplated by
PO-11/PO-20. It must still remove the grant first, retain immutable evidence,
and distinguish activation cleanup from separately authorized RB-1.

## What held

- `OH-H1-D3-1` is ready for Peter to close on this recommendation. PF records
  a durable inode identity before `linkat`; PT records and seals the temporary
  tree before `RENAME_NOREPLACE`; RS-1 never mutates; and RB-1 removes only an
  identity- and digest-proven object under separate authority.
- The ACT/DEACT identifier, record schema, publication protocol, partial-state
  table, grant-first removal, guarded idempotence and retained evidence are
  otherwise specified at the required mechanical level.
- OH-D-1 through OH-D-9 are consistently treated as decided, and the
  production workspace host is not used as source, controller, relay,
  destination, fallback or rollback target.
- Claude stayed within the repository-only authority and preserved the
  inactive status of the proposal.

## Required successor

Peter should accept this re-review, close `OH-H1-D3-1`, keep
`OH-H1-D3-2` open under Blocking successor `OH-H1-D3-R1-1`, and authorize one
narrow repository-only design remediation of the death/reboot cleanup gap.
The result requires another independent Codex re-review before any H-1 design
is accepted or any H-0, implementation, retrieval, host or activation work is
authorized.

## Checks and authority boundary

I read the canonical working agreement, the implementation plan's required
sections, the active Handover and disposable-server restriction, the
remediation authority and prompt, the accepted OH-D decision record, the prior
review, and the complete revised proposal. I inspected repository status and
the documentation diff. Review checks were repository-local and read-only.

No SSH, network/Git retrieval, credential, retained-path inspection, upstream
research, implementation, build, installation, H-0/H-1/H-2, ACT/DEACT,
rollback, cleanup, test suite, commit or push was performed. Tests are
inapplicable to this documentation-only review and prohibited host checks were
not run.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18,
PO-19, PO-20 and H-1 remain open. RP-11 remains unwired and unmet; package
RAID item `P5.0-R5` remains Blocking; `plan.is_executable=False`; Package 5.0
remains not ready.
