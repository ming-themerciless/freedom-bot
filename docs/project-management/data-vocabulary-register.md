# Controlled data vocabulary register

Status: Controlled by implementation-plan baseline v1.6, 2026-08-27.

Owner: Data Owner. A package is not ready while a vocabulary it uses has an
unresolved source or identity policy. Display names are aliases, never keys.
Unrecognized legacy values remain explicit migration issues until the Data
Owner maps, adds or rejects them; an importer cannot create definitions merely
because text appeared in a Sheet cell.

| Vocabulary | Owning package | Approved identity/source | Steward and change path | Alias/version/retirement policy | Readiness |
|---|---|---|---|---|---|
| Abilities | 5.1 | Fixed reviewed ability codes used by the supported D&D rules profile | Data Owner; rules change control | stable code; label aliases only; referenced codes restricted from deletion | Ready for schema design |
| Classes | 5.1 | Supported dnd5e class identifiers plus explicitly approved Freedom Blades additions | Data Owner; additions through reviewed migration data decision | aliases map to stable IDs; source/version recorded; retire/disable, never delete referenced rows | Source verification required |
| Subclasses | 5.1 | Supported dnd5e subclass identifiers tied by FK to class plus approved additions | Data Owner | same as classes; class compatibility constrained | Source verification required |
| Feats | 5.1 | Approved Foundry/dnd5e stable identifiers where available; legacy unmatched values unresolved | Data Owner; licensing/provenance review for any imported catalogue metadata | alias table with source/version; referenced definitions retained | Source/licensing decision required |
| Tools | 5.1 | Supported dnd5e tool identifiers plus approved Freedom Blades aliases | Data Owner | stable ID and alias table; retirement preserves character rows | Source verification required |
| Languages | 5.1 | Supported dnd5e identifiers plus Council-approved campaign languages | Data Owner / Product Owner | stable ID; campaign additions attributable; no deletion while referenced | Source and addition workflow required |
| Special weapons | 5.1 | Freedom Blades rules identifiers and approved weapon definitions | Product Owner / Data Owner | stable code; rules/profile version; disable rather than delete | Rule mapping required |
| Artisan disciplines and ranks | 5.5 | Freedom Blades rule catalogue and approved artisan codes | Product Owner / Data Owner | discipline identity separate from constrained rank; versioned aliases | Rule mapping required |
| Magic items | 5.6a | Pinned, licensed catalogue sources governed by §7.4 | Data Owner / Product Owner | definition revisions, aliases and source disablement per §7.4 | Governed by 5.6a gate |
| Campaigns | Phase 8 | Council-created platform campaign records with stable internal IDs; the legacy numeric counter is not a definition source | Product Owner / Data Owner | names are mutable aliases; merge/retire is audited; referenced campaigns retained | Domain workflow required |

Every package plan replaces `required` entries with a dated decision before its
definition of ready. It records exact source version/checksum where applicable,
licensing/provenance limits, seed migration, alias collisions, merge behavior,
who may add definitions after cutover and tests for disabled/referenced rows.
