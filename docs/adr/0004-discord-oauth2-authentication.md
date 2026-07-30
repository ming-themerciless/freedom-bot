# ADR 0004 — Discord OAuth2 authentication and server-side sessions

Status: **Accepted** — approved by the maintainer 2026-07-30. That satisfies the
Phase 0 acceptance criterion *"maintainer approves architecture ADRs"* (plan §12).
The independent Codex review required by plan §16.4 approved Phase 0 on
2026-07-30, and the maintainer accepted the milestone. This ADR is the contract
Phase 1 will be reviewed against.

Date: 2026-07-29

## Context

The community's identity lives in Discord. Plan §9.1 requires Discord OAuth2 with
minimum scopes, guild-membership verification, role resolution through stable
role IDs, server-side sessions, rotation on privilege change, and revocation.

Phase 0 discovery found that the bot has **no authorization at all** beyond
channel-ID checks. Any guild member can run any mutating command against any
character by typing its name
([command-inventory.md §5](../discovery/command-inventory.md#5-cross-cutting-gaps),
G-1 and G-2). `/sale` is the sole exception and it matches a Discord role by
lowercase **name**, which `.agents/AGENTS.md` forbids.

The web application therefore cannot inherit an authorization model. It has to
establish one, and that model becomes the one the bot adopts in Phase 5.

## Decision

### Authentication

Discord OAuth2 authorization-code flow with PKCE.

**Scopes: `identify` and `guilds.members.read` only.** Not `email`, not `guilds`
beyond what membership verification needs. Plan §9.4: collect only necessary
Discord identity and role data.

On callback, before a session is created:

1. verify the `state` parameter (CSRF for the OAuth flow itself);
2. exchange the code server-side;
3. fetch the member object for the configured guild;
4. **reject if the user is not a current member** of that guild;
5. resolve capabilities from the member's role **snowflakes**;
6. create the session.

### Authorization

**Capabilities, not role names.** The application resolves a Discord member into
the capability set described in plan §4.1 (Visitor, Guild Member, Character
Owner, DM, Guild Council, Platform Administrator, Service Principal).
Configuration holds role **IDs**; role names are presentation only
(`.agents/AGENTS.md`, plan §4.1).

**Cached roles are never proof.** A `discord_role_snapshots` row records what was
observed and when; it is display and audit data. Effective privilege for a
mutation is verified server-side at the time of the request, with a short
revalidation TTL. Plan §4.3: *"Removing a Discord role or guild membership must
revoke effective authorization promptly."*

**Character access is separate from role.** Being a Guild Member says nothing
about which characters a user may act for. That comes exclusively from
`character_access` (plan §4.2), which is Council-managed and audited. Every
character-scoped operation checks: authenticated → current guild member →
active `character_access` row for this character → capability permits this
action.

That four-step check is the thing the bot has never had.

### Sessions

- **Server-side.** The cookie carries an opaque, high-entropy identifier; all
  session state lives in PostgreSQL (`sessions`, plan §7.1). No user data, no
  role claims and no OAuth token in the cookie.
- Cookie attributes: `Secure`, `HttpOnly`, `SameSite=Lax`, host-only, path `/`.
  `Lax` rather than `Strict` so the OAuth redirect back from Discord works.
- **Rotate the session identifier on login and on any privilege change**
  (plan §9.1).
- Absolute and idle expiry, both enforced server-side.
- Logout deletes the server-side record; it does not merely clear the cookie.
- An administrator can revoke any session, and revocation is immediate because
  the record is server-side.

### Token handling

Discord access and refresh tokens are stored server-side, encrypted at rest, with
a defined retention (plan §9.4). They are **never** sent to the browser and never
logged. A token is used to verify membership and roles, not as a session.

### CSRF

Every cookie-authenticated mutation carries a synchroniser token bound to the
session. `SameSite=Lax` is defence in depth, not the control — it does not
protect against same-site request forgery, and the application will host
user-supplied text (item names, report bodies).

### Service principals

The bot, the Foundry module and any import worker authenticate as
`service_principals` with scoped, individually revocable credentials
(plan §7.1, §9.3). A service principal is never a user session and never carries
Council capability implicitly.

## Consequences

**Positive.**

- One authorization model, established in Phase 3, adopted by the bot in Phase 5.
  Plan §12 Phase 5's "no command can mutate an unlinked character" becomes
  achievable because `character_access` already exists.
- Server-side sessions make revocation real, which is what plan §12 Phase 3's
  "revoked membership/role is handled" acceptance criterion actually requires.
- Nothing security-relevant is computed from data the browser can edit.

**Negative.**

- A Discord API call on the membership-revalidation path. Needs a cache with a
  short TTL, a rate-limit budget, and a defined behaviour when Discord is
  unreachable — **fail closed** for mutations, degrade to read-only for queries.
- Sessions in PostgreSQL mean a database read per authenticated request. Fine at
  this community's scale; noted so it is a measured decision rather than a
  discovered surprise.
- Users linked to multiple characters need an explicit character selector on
  every character-scoped action. The Sheet's `default-character` flag
  (plan §4.2) helps but does not remove the need.

**Risk this ADR does not remove.** The bot keeps its current
no-authorization behaviour until Phase 5 migrates each command. Phase 3 does not
fix `/trade`. That gap is real, is documented in
[command-inventory.md §5](../discovery/command-inventory.md#5-cross-cutting-gaps),
and its acceptable duration is a maintainer decision
([OD-17](../discovery/open-decisions.md)).

## Alternatives considered

**JWT sessions.** Rejected: revocation requires a server-side denylist, which
reintroduces the state that JWTs were supposed to avoid, and plan §9.1 requires
rotation on privilege change. A stateless token whose claims outlive a role
removal is precisely the failure mode `.agents/AGENTS.md` warns about.

**Discord bot DM-based login codes.** Rejected: worse UX than OAuth and a new
credential to protect, with no benefit over the standard flow.

**Trusting role claims from the OAuth token.** Rejected: it is exactly the
*"Cached roles are not permanent proof"* case in plan §4.3.

## Open questions

- Guild and Council role snowflakes ([OD-18](../discovery/open-decisions.md)).
- Which roles grant DM capability ([OD-18](../discovery/open-decisions.md)).
- OAuth token and session retention periods ([OD-23](../discovery/open-decisions.md)).
- Whether a Platform Administrator may act with Council capability in a
  break-glass case, and how that is audited ([OD-24](../discovery/open-decisions.md)).
