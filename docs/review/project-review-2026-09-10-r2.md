# Project review — 2026-09-10, second pass

Disposition: **changes requested**. Review of the current working tree, concentrating on the uncommitted skills change, evidence-harness execution/cleanup, current VM proposal and existing review gates, with sampled web authorization code and local regression checks. This is not an exhaustive security audit or a gate approval. Existing user changes were preserved; no implementation was changed.

## 1. Blocking — unresolved harness ownership defect remains reproducible

Existing finding **EH-R16-1**, not a new finding. In
`tools/phase_5_0_evidence/execution/executor.py:729`, cleanup revalidation validates
the command vector, not the identity of the object that the pathname currently
resolves to. Execution and cleanup can therefore affect replacement objects,
including configuration recovery inputs, after initial ownership was recorded.
The later root identity check does not protect earlier descendant operations.

Independently reran `test_r16_1_ownership_reproduction.py` with injected effects.
Its tests reproduce root replacement before provisioning and later experiments,
descendant removal under an unchanged root, and substituted recovery inputs.
Passing these tests confirms the defect in the model; it is not live-host exploit
evidence or a passed ownership invariant.

Keep execution withheld until a reviewed mechanism protects ownership-dependent
effects throughout the lifecycle and independently safe recovery remains available.
The current target/plan refusals are not a repair. The VM proposal's statement
that the old executor is “disabled” at design line 251 remains too strong:
executor construction at line 443 refuses conditional plan facts, rather than
unconditionally refusing on EH-R16-1. Existing VM-5 tracks this distinction.

## 2. Blocking — crafting aliases disagree between CRP reads and writes

New finding **PR-20260910-R2-1**. Locations: `models/skills.py:260`,
`models/skills.py:395`, `models/skills.py:417` and the Master-learning gate at
`models/skills.py:536`.

The new aliases make `Herbalist` and `Herbalism` the same tool, but
`get_tool_crp()` returns only the first matching entry. `add_tool_crp()` sums
all matching entries. A synthetic Sheet CRP cell containing
`60 (Herbalist), 50 (Herbalism)` loads both entries unchanged. Reading CRP for
`Herbalism Kit` returns **60**, while adding **1** returns **111**. Reversing
entry order would instead make the initial read 50.

The Master-learning prerequisite uses that read, so a character whose equivalent
entries total 110 is refused at the 100-point gate until another craft happens
to consolidate the entries. This is a rule-correctness defect, rather than a
presentation issue. The same inconsistency applies to the other new aliases
when both spellings occur.

Required correction: use consistent aggregation of equivalent CRP entries for
reads and writes without introducing persistence during a read. Add regression
coverage for both entry orders, alias families, the Master-learning threshold,
and the invariant that earning one increases the prior read total by one.
Preserve the accepted handling of untagged and unreadable CRP.

## 3. Existing VM design blockers remain unresolved

The proposal is still **Proposed**, and its independent review has requested
changes. In particular, design lines 81–99 rely on an exclusive management
writer population, while the candidate host's documented profile grants several
agents unrestricted administrative access. This does not establish that
interference occurred, but the required exclusion is not established by the
proposed deployment contract. Registry publication and disposal safety depend
on that premise. Existing VM-1 through VM-3 track these issues; this review does
not independently close or replace that review, nor approve the alternative.

See `phase-5-0-evidence-vm-independent-review.md` for the complete five Blocking,
ten Important and three Optional design findings. Package 5.0 remains not ready,
P5.0-R5 Blocking and OD-62 Open. Test counts do not advance those gates.

## Verification and limits

The repository is `/opt/freedom-blades/platform`; the canonical test interpreter
is `/opt/freedom-blades/runtime/venv-web/bin/python` **on oracle-test**. This pass
used the active handover's verified local fallback interpreters because its
restriction prohibits SSH, synchronization and operational execution.
`TEST_DATABASE_URL` was explicitly unset; bot and web suites ran serially.

Commands and results against this working tree:

* `env -u TEST_DATABASE_URL /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/phase_5_0_evidence/test_no_execution.py tests/phase_5_0_evidence/test_r16_1_ownership_reproduction.py`: **209 passed**.
* Same interpreter and flags, `tests/phase_5_0_evidence`: **1391 passed**.
* `env -u TEST_DATABASE_URL /opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py`: **2991 passed, 326 skipped, one warning**.
* Web fallback interpreter and same flags, `tests/web`: **1610 passed, 1362 skipped**.
* `node --test 'foundry-module/tests/'*.test.mjs`: **171 passed, no failures or skips**.
* Synthetic direct `Skills` invocation confirmed the 60-to-111 inconsistency above.
* `git diff --check`: passed, including after adding this report.

Database skips are unverified assertions. The canonical database-enabled web
run expects 80 skips, not 1362; these results establish no PostgreSQL migration,
constraint, concurrency or recovery evidence. No host inspection, service change,
database execution, privileged vector, deployment or execution approval occurred.
No formatter, linter, type checker or compileall was run in this review-only pass.
This report adds no migration, configuration or rollback requirement.
