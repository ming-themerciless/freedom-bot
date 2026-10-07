# Decision — obsolete music residue removed

Date: 2026-10-06

Decision authority: Peter Duscha, Product Owner and Acceptance Authority

Peter Duscha confirms that `yt-cookies.txt` belonged solely to the obsolete
Freedom-bot music capability, which OD-40 removed rather than deferred, and
directs deletion of every remaining music-capability residue.

The untracked `yt-cookies.txt` was deleted by exact path without being read or
printed. The empty local `infra/lavalink/` directory was also removed. Current
music-specific ignore, synchronization and secret-guard entries were removed;
historical records remain unchanged as evidence.

This deletion closes the repository and controller residue involved in R1-F1.
It does not establish whether an external session represented by the former
cookie had already expired or was revoked. Peter subsequently accepted that
residual risk and required no invalidation or rotation on 2026-10-07. This
decision does not retroactively make R1 conforming. See the
[risk-acceptance record](project-review-2026-10-07-r1-f1-residual-risk-acceptance.md).

The deleted untracked file is not recoverable from Git. Recovery, if ever
needed, would depend on an external backup; the obsolete music capability must
not be restored without a new product decision superseding OD-40.

This record authorizes no host operation, successor assignment, implementation
slice, commit or push.
