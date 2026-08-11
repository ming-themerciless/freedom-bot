# Step 4 route retirement — production validation plan

Date drafted: 2026-08-10
Drafted by: Claude, at the maintainer's request
Status: **phase 1 executed 2026-08-10 and passed** — see "Phase 1 result" below.
Phase 2 remains a plan only, and authorizes nothing.
Relates to: finding **B-1**, change-log **C-18**,
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md)
§ "B-1, fourth remediation"

## Why this exists

C-18's step 4 brings the endpoint back behind a single-use `/recovery/<nonce>/…`
path with the episode's own path **replaced** by an explicit refusal. Everything
else in C-18 has now been observed. This has not, and it is the last unobserved
claim in the settlement rule.

It needs a plan rather than a command because it is the one part that changes the
**production Caddy configuration**, and because the route it would add is the same
temporary public exposure that was deliberately reverted on 2026-08-09.

### What is already established, so that none of it is repeated

| Established | Where |
|---|---|
| a request the proxy holds and has not dialled upstream for commits across an endpoint-only restart, and does not when the proxy is terminated | isolated Caddy 2.10.2 rig, 2026-08-10 |
| `uri strip_prefix` presents `/api/v1/foundry/snapshots` upstream; `caddy adapt` orders the handlers without an `order` directive | same rig |
| a **deleted** `handle` block falls through to an empty `200`; a block **replaced** by `respond 410` answers `410` | same rig |
| S-I.1–S-I.4 against the production Caddy: listeners gone in 0.5 ms, process at 4.3 s with one request held, held connection closed with nothing delivered, `521` from Cloudflare, `Restart=no`, UDP `:443` present | production, 2026-08-10 |

### The one claim left, stated precisely

> On the **production** Caddy, with its real configuration file and its real
> reload path, replacing the submission route with `respond 410` and adding the
> recovery route causes the retired path to answer `410` and the recovery path to
> reach the application — and the retired path cannot reach the application.

Note what the rig could not settle: on these hostnames each site block ends in a
`reverse_proxy` to Foundry, so a *deleted* block would fall through to **Foundry**
rather than to the empty `200` the rig produced. That is the specific reason the
retirement is an explicit `respond 410` and the specific thing worth confirming
here.

## Phase 1 — loopback only, no public exposure

**This is the default, and it is enough for the claim above.** It exercises the
production Caddy's own binary, configuration file, `validate` and reload path,
and adds **no** internet-reachable route.

Add a fourth site block bound to loopback, alongside the three existing ones:

```caddyfile
http://127.0.0.1:9080 {
	handle /api/v1/foundry/snapshots {
		respond 410
	}

	handle /recovery/<nonce>/api/v1/foundry/snapshots {
		request_body {
			max_size 64MiB
		}
		uri strip_prefix /recovery/<nonce>
		reverse_proxy 127.0.0.1:8757 {
			transport http {
				read_timeout 180s
				write_timeout 60s
			}
		}
	}
}
```

1. **Back up first, and verify the backup.** The 2026-08-09 revert failed on its
   first attempt because the backup had been captured *after* the change it was
   meant to undo. So: copy to `/etc/caddy/Caddyfile.pre-step4-<date>`, then
   confirm the copy contains **no** `recovery` and **no** `foundry/snapshots`
   before touching the original. A backup that already contains the change is not
   a backup.
2. **Start the endpoint** per §5.5, against the disposable `freedom_test`
   database, with `APP_ENVIRONMENT=test`. No credential is needed for this
   validation and none should be issued. If it refuses to start, stop and resolve
   that first — the refusal is §5.6 doing its job.
3. `caddy validate --config /etc/caddy/Caddyfile` **before** reloading. A failed
   validate is an abort, not a prompt to edit further.
4. `sudo systemctl reload caddy`, then confirm the three existing sites still
   answer. A reload that breaks Foundry is the only outcome here that costs
   anyone anything.
5. Observe, recording each verbatim:

   | Request | Expected | What another answer means |
   |---|---|---|
   | `POST http://127.0.0.1:9080/api/v1/foundry/snapshots` | **`410`** | `401` — the retirement did not take and the old path still reaches the application: **the claim fails**. Empty `200` — the block was deleted rather than replaced |
   | `POST http://127.0.0.1:9080/recovery/<nonce>/api/v1/foundry/snapshots`, **no** `Authorization` | **`401`** | `410` or `404` — `strip_prefix` did not present the upstream path. `502` — the endpoint is not running |
   | the same, with the endpoint stopped | **`502`** | anything else — the route is not reaching the endpoint at all, and the `401` above proved less than it seemed |

   The unauthenticated `401` is deliberate and is the whole point: it proves the
   route reaches the application **while writing nothing**. `adapters/http/wsgi.py`
   returns `401` before it reads a body, establishes a principal or calls any
   service, and does not audit the refusal — with the comment saying why, so that
   an unauthenticated caller cannot append to permanent history. Recovery must not
   write, and this does not.
6. **Revert**: restore the backup, `caddy validate`, reload, and confirm the
   loopback port answers nothing and the three sites still serve. Stop the
   endpoint.

**No Actor data, no credential, no artifact, no submission, no real database.**

### Phase 1 result — executed 2026-08-10, passed

Run against the production Caddy with the endpoint up on `:8757`. The backup was
taken first and verified free of the change, `caddy validate` passed, the reload
took, and the revert ran from a `trap`:

| Check | Wanted | Got |
|---|---|---|
| `foundry1/2/3.rpgworld.org` after the reload | unaffected | `302`, `302`, `302` |
| retired path, `POST http://127.0.0.1:9080/api/v1/foundry/snapshots` | `410` | **`410`** |
| recovery path, unauthenticated | `401` | **`401`** |
| after the revert, the loopback port | nothing | connection refused |

So the retirement holds and the recovery route reaches the application, on the
production instance's own configuration file, `validate` and reload path. The
unauthenticated `401` wrote nothing: no credential exists for the principal that
was configured, and `adapters/http/wsgi.py:297` returns before any body read,
principal or service call.

The endpoint-down variant — recovery path answering `502` — was **not** run here.
It is established on the rig (observation 6 in the appendix) and running it would
have cost a second reload window for a claim already covered. Recorded as a
deliberate omission rather than an oversight.

Full log:
[`phase-2-b-1-settlement-observations-2026-08-10.md`](phase-2-b-1-settlement-observations-2026-08-10.md).

## Phase 2 — the public site block, maintainer-gated

Only if the maintainer wants the retirement confirmed **through Cloudflare**, on
the hostname a stranded request would actually carry. It re-creates a temporary
public route to the submission endpoint, which is the exposure reverted on
2026-08-09, so it is a deliberate decision and not a continuation of phase 1.

The difference that justifies it: phase 1 cannot show what the *foundry1* site
does with the retired path, because that site ends in a catch-all `reverse_proxy`
to Foundry. Phase 1 proves the directives work; phase 2 proves the retirement wins
against the fall-through that would otherwise hand the path to Foundry.

If it is run:

- fold it into **Rehearsal A step 10**, which already stands up a temporary route
  under supervision, rather than opening a second window for it;
- keep the endpoint bound to loopback and reachable only through the nonce path;
- issue no credential; the same unauthenticated `401`/`410` pair is the evidence;
- confirm from off the host, through Cloudflare, and record the status codes
  verbatim — including what the **retired** path answers, which is the number this
  phase exists for;
- revert within the same window, verify with the §5.4 configuration restored, and
  re-confirm no `via: 1.1 Caddy` and no body from that hostname, exactly as the
  2026-08-09 revert was verified.

## Abort conditions

Stop, restore the backup, and escalate if any of these occur:

- `caddy validate` fails, or a reload does not take;
- any of the three Foundry sites stops answering;
- the retired path answers `401`, or anything else only the application could give;
- the endpoint refuses to start for a §5.6 storage reason;
- in phase 2, the route is reachable without the nonce, or the revert does not
  verify clean on its first attempt.

## What this will not establish

- **Nothing about settlement.** This is a routing and configuration validation.
  S-A, S-I and S-D are established elsewhere and are not re-run here.
- Nothing about an operator following §9 under time pressure, which remains the
  part no test and no rehearsal in this package reaches.
- Phase 1 establishes nothing about Cloudflare or about the fall-through on the
  real hostnames; only phase 2 does, and it is optional.

## Where the result goes

A short record under `docs/review/`, the observation rows in
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md)
§ "B-1, fourth remediation", and the C-18 observation bullet. **B-1 stays open
either way**: closing it is the independent reviewer's to do, and this plan
changes nothing about that.
