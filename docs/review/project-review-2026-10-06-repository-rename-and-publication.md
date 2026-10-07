# Decision — repository renamed and made public

Date: 2026-10-06

Authority: Peter Duscha, Product Owner and Acceptance Authority

## Decision

The GitHub repository is renamed from `ming-themerciless/freedom-bot` to
`ming-themerciless/freedom-platform` and is publicly readable. Its canonical
public HTTPS retrieval URL is now:

`https://github.com/ming-themerciless/freedom-platform.git`

The controller Git connection uses:

`git@github.com:ming-themerciless/freedom-platform.git`

This is an administrative repository-identity change. It does not rename the
legacy Freedom bot application, Python/Pycord adapter, systemd service or their
retirement gate. Historical records retain the old slug where it records the
URL actually used by a consumed assignment.

## H-0 effect

R4 remains consumed and is not retried. Public visibility removes its observed
retrieval blocker but does not itself authorize a host action. The next H-0
attempt requires a new work ID, fresh exclusive checkout and evidence paths,
and a new prompt using the canonical `freedom-platform` URL. The pinned commit
remains unchanged unless separately amended and verified.

No OH-S2 or later-slice authority follows from this decision.
