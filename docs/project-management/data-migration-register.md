# Legacy data migration register

Status: Controlled by implementation-plan baseline v1.6, 2026-08-27.

Owner: Data Owner. Update authority: §0.2 change control. This register assigns
every known legacy Sheet field to exactly one accountable migration package.
`Legacy` means the accepted production path remains authoritative; it does not
authorize the new platform to write the Sheet. A package may split a source
value into several typed records, but one package remains accountable for
complete source disposition and reconciliation.

No row may move to `Database` until its package records the typed target,
deterministic transformation, source and target totals, explicit unresolved
records, recovery evidence, cutover decision and Data Owner acceptance. No row
may have two write-authoritative targets.

All authoritative multi-valued domain sources follow plan §7.3.1: reference/definition tables plus
foreign-keyed junction rows, or typed foreign-keyed child rows for owned
entries. Delimited text, JSON/JSONB collections, PostgreSQL arrays and generic
key/value storage are prohibited migration targets for those facts. Immutable
evidence, audit context, bounded diagnostics, preserved external payloads and
disposable presentation caches are governed by the explicit §7.3.1 exceptions
and cannot count as migrated operational state.

## Character fields

| Profile field | Sheet source | Accountable package | Current state | Required typed target / disposition |
|---|---|---|---|---|
| `character.display_name` | Characters A | 5.1 | Legacy | character profile identity/display record |
| `character.long_name` | Characters B | 5.1 | Legacy | character profile |
| `wallet.inspiration` | Characters D | 5.2 | Legacy | typed wallet ledger and opening transaction |
| `character.level` | Characters F | 5.1 | Legacy | constrained character progression profile |
| `missions.count` | Characters G | Phase 8 | Legacy | immutable typed opening mission-count fact at cutover; never synthesize historical missions; post-cutover count derives from real mission rows plus the accepted baseline |
| `character.last_played` | Characters H | Phase 8 | Legacy | typed last-played baseline fact; normalized session history begins at cutover and may supersede display only when supported by real records |
| `downtime.thousandth_days` | Characters I | 5.5 | Legacy | typed downtime ledger and opening transaction |
| `lifestyle.living_cost_weeks` | Characters J | 5.3 | Legacy | typed lifestyle ledger and cutover instant |
| `bastion.owned` | Characters K | 5.9 | Legacy | typed Bastion state |
| `bastion.maintenance_weeks` | Characters L | 5.9 | Legacy | typed Bastion maintenance ledger |
| `bastion.turn_available` | Characters M | 5.9 | Legacy | typed Bastion state/history |
| `lifestyle.type` | Characters N | 5.3 | Legacy | typed lifestyle state |
| `lifestyle.aristocratic_lockout` | Characters O | 5.3 | Legacy | typed lifestyle state/history |
| `wallet.balance_copper` | Characters P–S | 5.2 | Legacy | integer-copper wallet ledger and opening transaction |
| `wallet.moradinium` | Characters T | 5.2 | Legacy | typed resource ledger and opening transaction |
| `lifestyle.weekly_expenses_copper` | Characters U | 5.3 | Legacy | typed lifestyle expense policy/state |
| `character.downtime_progress` | Characters V | 5.5 | Legacy | one foreign-keyed `learning_projects` row per project plus explicit typed crafting rows handed to 5.6b; opaque-text persistence forbidden |
| `crafting.crp_thousandths` | Characters W | 5.6b | Legacy | typed per-artisan CRP ledger/history |
| `crafting.artisan_ranks` | Characters X | 5.5 | Legacy | artisan definitions plus foreign-keyed character-artisan rank rows with constrained rank |
| `proficiencies.tools` | Characters Y | 5.1 | Legacy | tool definitions plus foreign-keyed `character_proficiencies` junction rows |
| `proficiencies.languages` | Characters Z | 5.1 | Legacy | language definitions plus foreign-keyed `character_languages` junction rows |
| `inventory.magic_items` | Characters AA | 5.6a | Legacy | foreign-keyed catalogue definitions plus character-item rows and inventory transactions; unresolved identity explicit |
| `character.masterpiece` | Characters AB | 5.6b | Legacy | typed crafting/masterpiece record |
| `wallet.debt_copper` | Characters AC | 5.2 | Legacy | typed debt ledger; 5.3 consumes it for scheduled interest without owning migration |
| `character.background` | Characters AD | 5.1 | Legacy | constrained character profile |
| `character.class` | Characters AE | 5.1 | Legacy | `class_definitions` plus foreign-keyed `character_classes`, with typed level/order facts where present |
| `character.subclass` | Characters AE | 5.1 | Legacy | `subclass_definitions` plus foreign-keyed character-class association; multiclass/subclass ambiguity explicit |
| `character.race` | Characters AF | 5.1 | Legacy | constrained character profile |
| `character.ability_scores` | Characters AG | 5.1 | Legacy | `ability_definitions` plus foreign-keyed `character_ability_scores`, unique per character/ability, constrained integer score and provenance |
| `character.feats` | Characters AH | 5.1 | Legacy | `feat_definitions` plus foreign-keyed `character_feats`; unresolved identity stays explicit |
| `character.specials` | Characters AI | 5.1 | Legacy | one typed foreign-keyed `character_specials` child row per reviewed fact/note, not executable rules |
| `missions.no_shows` | Characters AK | Phase 8 | Legacy | immutable typed opening no-show count; never synthesize attendance; post-cutover aggregate combines baseline with real confirmed mission rows by a documented rule |
| `character.active` | Characters AL | 5.1 | Legacy | effective-dated character activation history |
| `proficiencies.special_weapons` | no direct column | 5.1 | Legacy/unavailable | weapon definitions plus foreign-keyed proficiency rows only from an approved source; never inferred |

Characters column C (`Player Name`) is identity linkage evidence, not a
character-state field. Phase 3 owns its Council-reviewed migration into player
identity and foreign-keyed `character_access`; it never grants authorization by
itself.

## Player fields

| Legacy field | Sheet source | Accountable package | Current state | Required typed target / disposition |
|---|---|---|---|---|
| Player name | Players A | Phase 3 | Legacy | player identity evidence and reviewed linkage |
| Discord name | Players B | Phase 3 | Legacy | matching evidence only; Council links a Discord snowflake |
| Last date played | Players C | Phase 8 | Legacy | typed player last-played baseline; reconcile against available real records without inventing sessions |
| Active DM | Players D | Phase 3 | Legacy | display/reconciliation evidence only; Discord role IDs remain authorization |
| Last date DMed | Players E | Phase 8 | Legacy | typed last-DMed baseline; normalized DM/session history begins at cutover |
| Latest date to DM | Players F | Phase 8 | Legacy/unruled | preserve and report; no behavior until a rule decision exists |
| Campaign Counter | Players G | Phase 8 | Legacy/unresolved semantics | preserve as a typed numeric baseline only after Data Owner confirms meaning; do not infer campaign identities or memberships; future memberships use definitions plus foreign-keyed rows from real records |
| No shows | Players H | Phase 8 | Legacy | immutable typed opening no-show count; reconcile against character baselines/real records without inventing attendance |

## Control totals and gate rule

The register is rendered policy for the controlled machine-readable
`data-migration-manifest.json`. Automated checks fail when the field profile or
Sheet inventory adds a field without one disposition, assigns an unknown
package, duplicates a target or omits the character-to-player linkage or any of
the eight player fields. Before Sheet retirement, the Data Owner signs a final
report showing every row in `Database` or explicitly removed through approved
scope change; `Legacy`, `Shadow` and unexplained states block retirement.
