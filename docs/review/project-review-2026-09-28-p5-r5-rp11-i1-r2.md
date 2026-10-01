# Codex review — P5.0-R5 RP-11 I1-R2 remediation — 2026-09-28

Reviewer: Codex, independent of the Claude I1-R2 remediation

Reviewed inputs:

* `phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-handback.md`;
* `phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-claude-prompt.md`;
* `tests/phase_5_0_evidence/test_rp11_publication_portability.py`, SHA-256
  `f2845fd655fcca0029e15e2383018c37d947e505ef079e11b359e4333c446f2a`;
* amended `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`,
  SHA-256 `186ff546a7f31ccf16461d0d3fec83978af643bd8d2e63dbac2e9dc2f3a2f9c6`;
* the controlling I1-R1 review and the I1-R2 assignment.

## Result — changes requested

The I1-R2 prototype corrects the omissions named in **RP11-I1-R1-1**: it now
checks probe ownership, exact mode, emptiness and device; performs a checked
complete write; opens and verifies the published object; compares exact bytes;
rechecks identity; and preserves post-publication residue on the tested failure
paths. The dated erratum accurately narrows the I1-R1 handback without editing
that historical record.

One Blocking cleanup defect remains. The prototype and proposed §9.5.4 contract
cannot yet establish that cleanup removes the published inode, rather than an
unrelated replacement. The remediation therefore is not accepted and
**RP11-I1-R1-1 remains Open** pending correction and re-review.

**RP11-I1-2 also remains Open and Blocking.** The publication route again
fails in this independent review context. RP-11 remains unmet; neither
operational pass is executable or authorized; P5.0-R5 remains Blocking,
OD-62 G-A remains conditional, `plan.is_executable=False`, and Package 5.0
remains not ready.

### RP11-I1-R2-1 — Blocking — cleanup can unlink an unchecked replacement

The proposed §9.5.4 step 8 requires removal of “that one fixed name, and
nothing else” after an identity recheck. The prototype performs a no-follow
`stat` and then a separate pathname `unlink`. Another process with the same
effective user can replace the directory entry after the `stat` succeeds and
before `unlink`; the latter then removes the replacement even though its
identity was never checked. Exact `0700` directory mode excludes other users,
but it does not exclude another process running as the operator account.

The existing replacement test covers only replacement **before** the recheck,
where refusal is safe. It does not exercise replacement in the
recheck-to-unlink window. The handback correctly identifies this window in §7,
but incorrectly concludes that no wording contradiction with the draft was
found. The window contradicts both the assignment's “remove exactly that fixed
name” requirement and the draft's “that one fixed name, and nothing else”
claim.

Remediation must make the contract and evidence honest and fail-safe. It may,
for example, redesign cleanup around a reviewed primitive that cannot remove a
different inode, or explicitly change the requirements and operational
isolation model so the race and its consequences are accurately bounded and
accepted. Merely adding another pathname identity check does not close the
race. Add a deterministic regression test that replaces the entry after the
last successful identity check and proves that an unrelated replacement is
not removed.

## Independent test result

The diagnostic module was run serially with `TEST_DATABASE_URL` explicitly
unset, bytecode writes disabled and the pytest cache provider disabled:

```text
25 passed, 5 failed, 0 skipped
```

The five failures are exactly the handback's predicted link-dependent cases:

* `test_the_production_route_names_a_linkable_unnamed_inode_once`;
* `test_the_complete_check_succeeds_here_in_order_and_leaves_the_directory_empty`;
* `test_success_uses_the_production_creation_and_link_functions`;
* `test_published_bytes_that_differ_from_the_payload_refuse_before_cleanup_and_remain`;
* `test_a_name_replaced_before_cleanup_is_refused_and_the_replacement_is_untouched`.

Each stopped because the production link through `/proc/self/fd/N` returned
`ENOENT`; the latter two consequently never reached their injected fault.
The recorded context was CPython 3.12.3, Linux 6.8.0-139-generic, ext4 under
`/tmp`, procfs at `/proc`, and `/proc/self` resolving to the caller. This
validates the handback's context-specific prediction but does not establish
publication portability or a successful complete check here.

## Evidence checks and limits

Performed:

* read the governing agreement, required implementation-plan sections, active
  handover and restriction banner;
* inspected the assignment, handback, proposed contract, diagnostic module and
  production publication functions;
* re-derived the three relevant SHA-256 values; and
* ran the diagnostic module and scoped whitespace checks.

`git diff --check` was clean. The untracked diagnostic also passed
`git diff --no-index --check`; that command's exit 1 indicated content
difference from `/dev/null`, not a whitespace error.

Not performed because the active assignment is repository-only: SSH,
synchronization, network or remote-host inspection, database access, `sudo`,
provisioning, controlled writes, reboot, verifier, evidence band, harness
`--execute`, real capture-root use, protected-artifact access and secrets scan.
The full bot/web suites and `oracle-test` were not run. This review creates no
host, operational or acceptance authority.
