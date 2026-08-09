# Phase 2 Data Owner attestation — active-folder reconciliation

Date: 2026-08-09
Data Owner: Peter Duscha
Prepared by: Claude from the preview output; **signed by the Data Owner below**

This is the signed reconciliation report the implementation plan requires as
§13.3 operational evidence for the Phase 2 gate. It records identifiers and
counts only. It contains no Actor name, no mechanic, no raw snapshot content and
no unnecessary player data.

## 1. The export

| | |
|---|---|
| Export SHA-256 | `c47723a4bd55c857fc5a22115ddd8038d6cd8b6520c332218fd0bb29a6424055` |
| Artifact size | 16,287,185 bytes |
| Exporter | `freedom-blades-export` **1.0.5** |
| Field profile | **`2026-08-09.1`** |
| World | `the-guild` |
| Selected folder | `/actors/Characters (active)` — `smob5eya6XVBAuIb` |
| Deployment | Foundry `14.365`, `dnd5e` `5.3.3` |
| Submitted | 2026-08-09 22:09:03 UTC, principal `foundry-the-guild-b` |
| Snapshot record | `f6155f61-4c60-42af-a28e-a4bd092b6e17` |
| Canonical encoding | **yes**, under contract §1.0 as amended by change-log C-10 |

## 2. Disposition of every Actor

Total Actors in the selected folder: **32**. Every one is accounted for, and the
dispositions sum exactly to the folder count.

| Disposition | Count |
|---|---|
| Mapped to an existing character | **0** |
| Create-candidate | **32** |
| Explicitly unresolved | **0** |
| Blocked | **0** |
| Absent from this snapshot but previously mapped | **0** |
| **Unexplained identity discrepancies** | **0** |

Every Actor is a create-candidate because the target database held no
characters and no external mappings at the time of the preview — this is the
first reconciliation of this world, so there was nothing for an Actor to map
*to*. That is the expected state before the Phase 2 import has ever been
applied, not an anomaly, and it is why no identity discrepancy could arise:
there are no two records that could disagree.

**No unresolved identity exists, so there is no disposition or reason to
record for one.**

## 3. The 32 stable external Actor identifiers

All 32 are distinct, and every one carries `folderId` = `smob5eya6XVBAuIb`.

```
01rRcoJQ5LU8ZHXA  3hQe3ZIm5FGOLw2d  52ywI3ttEcgf9iBv  7Y578ldCBnRtqM70
9xwsbdSlDeYEANd5  9yHGMmRQZvvSLl6D  C0DSVF54I5nzFHzA  C5uVlri90h7NzD4L
DPd6SZEB60GlK8W1  HrtVSDa9skcz1PMg  JICuQJDsw68DZaHL  N15PwBigLiBNNDjJ
NX4QpFBaCE5vnsS6  OP1nZKo6B3v2Ce0B  PvP9b582XxabDmVu  SiKDDAxWZkDs4deA
T90H7rJEYkCTrGAT  U9UmClnZHq7rgpaO  WlalDqqykG4xbkwJ  a3fGHf3SzMi2ynsr
bC7NfMRiGgDs2n58  c1ECx8x83A7yBwUR  fWtLKguWXUIN1R82  fwQVypP89oyEg94Y
i7jLisefJ7HZpVeY  jK0huiegdEKsEe3p  ncHS7LScoB0BcnMX  qhPdZFyXrgfqBXIl
qsEvbjujDHva7HH7  sjFmdq8IqZLyTlSU  tixQhwGbnijM9iId  w4ytZtMv2n4nhUxf
```

## 4. Preview result

Run in rehearsal mode via `tools.bootstrap_manager`, which writes nothing:

```
0 error(s), 0 warning(s)
actors 32 · would create 32 · already mapped 0 · blocked 0 · absent 0
Rehearsal. Nothing was written.
```

Zero warnings is itself evidence: it confirms field profile `2026-08-09.1` is
exhaustive against this folder — the ten unclassified paths that finding RA-1
found in the 35-Actor non-live folder are classified, and no new unclassified
path appeared here — and it confirms the artifact is in the contract's canonical
encoding under C-10.

Preview elapsed **9.566 s**. That exceeded the 5-second figure accepted in
change-log C-9, which was calibrated against synthetic Actors 233× smaller than
real ones. Throughput was **587 ms/MB against the benchmark's 728 ms/MB** — the
run is faster per megabyte than the corpus the threshold came from.

Raised as finding [RA-5](phase-2-rehearsal-a-findings-2026-08-09.md) and **ruled
the same day as change-log C-11**: the gate criterion is now throughput
≤ 1,200 ms/MB, which this run meets; C-9's wall-clock figures are retained as
synthetic smoke-test context and are no longer gate criteria; and the absolute
9.566 s is recorded as a Phase 3 constraint on the preview route. The breach was
neither waived nor argued away — the criterion was corrected, and the number
stands in the record either way.

## 5. What was and was not persisted

- No character, mapping, import or game-state row was created. Verified after
  the preview: `characters` 0, `external_actor_mappings` 0, `snapshot_imports` 0.
- The database holds one immutable snapshot provenance row and one
  `snapshot_submission.accepted` audit event, both against the disposable
  `freedom_test`.
- **No artifact, Actor payload, Actor name, mechanic or downloaded JSON was
  committed to the repository.** The raw artifact was held only in the restricted
  artifact store outside the repository and is deleted at teardown per the D-c
  retention decision.
- `git status` was clean of artifacts, dumps, logs and Actor content.

## 6. Attestation

> As Data Owner, I attest that the export identified in §1 was produced under my
> supervision from the world and folder named there; that every one of the 32
> Actors is accounted for in §2 and §3 with zero unexplained identity
> discrepancies; and that no artifact or real Actor payload was committed to the
> repository.
>
> I record that the preview exceeded the superseded C-9 wall-clock figure as
> described in §4, that I raised it rather than waiving it, and that the
> criterion was corrected by change-log C-11 on the same day.

Signed: **_______________________** (Peter Duscha, Data Owner)

Date: **_______________**

---

**This attestation is one item of §13.3 evidence. It closes no gate.** The
Acceptance Authority records the Phase 2 gate decision, and the independent
review closure required alongside this attestation does not yet exist.
