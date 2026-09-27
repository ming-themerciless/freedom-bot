# Claude prompt — bounded I3 controlled-write verification — 2026-09-19

> **Superseded and consumed.** The assigned pass stopped before the first
> write. C-P5.0-LAB-I3-D1 replaces its unresolved P2/`CAP_FOWNER` premise and
> topology restriction. This historical prompt authorizes no further host
> action.

Authorization: **C-P5.0-LAB-I3**. Peter Duscha assigns Claude as implementing
operator for one bounded I3 controlled-write verification on `oracle-test`.
Codex remains the Independent Technical and Security Reviewer and does not
perform the operation.

## Assignment

Verify whether the repository already contains a reviewed operator procedure
that can perform the authorized I3 check using the reviewed
`linkat`/`unlinkat` sequence in the exact target filesystem. Before any write,
resolve from runner contract r6 and the reviewed implementation:

1. the exact target directory, execution identity, temporary and final naming
   rules, bytes, descriptor custody, barriers and cleanup sequence;
2. whether the procedure exercises every dependency I3 currently contains,
   including r6 §7.2's P2/`CAP_FOWNER` dependency; and
3. the already reviewed invocation that reaches that procedure without V7,
   a participant, the evidence harness, a generated vector or `--execute`.

If any of those is absent, ambiguous, not provisioned or not already reviewed,
**stop before the first write**. Return a blocker handback identifying the exact
missing contract, target, prerequisite or operator route. Do not add source,
invent a shell/Python/`ctypes` probe, reinterpret I3 as narrower than r6, create
`R`, initialize V7 or improvise around the stop.

Only if all three preconditions are established, perform one controlled
verification:

1. re-observe the exact parent and prove the two authorized names are absent;
2. create only one uniquely named temporary test object, exclusively, through
   the reviewed route;
3. write only the reviewed harmless test bytes and synchronize them;
4. publish exactly one hard link with the reviewed `linkat` call;
5. verify byte equality and that both names share the same `(st_dev, st_ino)`;
6. remove both names through the reviewed sequence;
7. synchronize the containing directory; and
8. prove both names are absent and no residue remains.

Stop immediately on a discrepancy, unexpected precondition, syscall failure,
identity mismatch, cleanup failure or unclassified result. If the link exists
when a later step fails, preserve complete evidence and use only an already
reviewed cleanup/recovery route whose identity preconditions are satisfied. Do
not claim success while either name or any unaccounted residue remains.

## Governing context

Before acting, read completely:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 12 (Package 5.0), 13, 14, 16, 17 and 20 of
   `docs/implementation-plan.md`;
3. the active `docs/review/Handover information`;
4. the current restriction banner in
   `docs/operations/disposable-test-server.md`;
5. runner contract r6, especially §§1.3.3, 5.10, 6.2, 7, 7.1, 7.2, 9.2 and
   9.3's I3 row;
6. the V6/I12 operational handback and independent closure review;
7. `tools/phase_5_0_evidence/execution/descriptors.py`, the lifecycle writer
   and every implementation/test path that performs exclusive publication;
8. the current status, RAID, decision and change registers; and
9. this prompt.

Inspect Git status and preserve every unrelated, earlier-pass and
reviewer-authored change. Do not read or print secret files. Do not use the
historical `/opt/discord-bots/` environments.

## Required evidence

Return a dated operational handback containing:

- the exact reviewed procedure and invocation used, or the exact reason no
  such route exists;
- source identity and all relevant reviewed file digests without treating a
  review-input digest as execution authority;
- preconditions, execution identity, groups, relevant capability state,
  filesystem/mount type and `fs.protected_hardlinks`;
- exact commands or reviewed entry points, timestamps, exit statuses and safe
  stdout/stderr;
- the temporary and final names, harmless byte digest, both observed
  `(st_dev, st_ino)` pairs and link counts before and after `linkat`;
- the removal and containing-directory synchronization evidence;
- a final absence/residue survey; and
- a precise statement of which I3 dependencies the operation confirms and
  which remain open, particularly P2/`CAP_FOWNER`.

Do not report I3 closed merely because one `linkat` succeeded. Closure requires
independent Codex review and Peter's decision, and only if the evidence covers
the complete current I3 contract.

## Restrictions and stop point

This assignment authorizes only the necessary read-only inspection and the one
bounded I3 verification above. It does **not** authorize repository source
changes, synchronization, dependency installation, V7 lifecycle
initialization, participant or harness invocation, database access, generated-
vector execution, a real boundary/materializer, `--execute`, V8, V10, service
changes or any production action.

Do not create `R`, broaden owners/groups/modes/capabilities, add a probe or
operator CLI, repair an unexpected object, or retry after a partial or cleanup
failure. Future repository synchronization, if separately authorized, must use
the accepted inline runbook command and never `--exclude-from`.

Stop after the evidence or blocker handback for independent Codex technical,
security and evidence review. Success confirms I3 only; it does not make
`plan.is_executable` true, authorize V7 or advance Package 5.0. LAB-SECRETS-1
remains Open, Low; LAB-V6-P2 remains deferred.
