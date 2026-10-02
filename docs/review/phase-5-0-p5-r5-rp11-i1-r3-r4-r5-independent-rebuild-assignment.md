# Active assignment — R-5 independent static-launcher rebuild

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5`

Prepared: 2026-10-01 by Codex, under Peter Duscha's authority to prepare the
assignment

Status: **accepted and assigned to Gemini by Peter Duscha on 2026-10-01**

Activation record:
[`project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md`](project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md).
The exact Antigravity-reviewed proposal is preserved separately with SHA-256
`c6204c2dcc63a72a32f486dbdfb0f463fb19352a5a799b8191c2206da59b579a`.

Resume amendment, 2026-10-01: the first attempt stopped correctly because
`/usr/bin/bwrap` was absent. Peter separately authorizes Gemini to install only
Ubuntu's `bubblewrap` package under the exact bounded authority below, then
resume with entirely fresh disposable directories:
[`project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md`](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md).
Gemini must also correct finding `R5-R1-1` from the
[`stopped-handback review`](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md).

## 1. Decision requested

Peter Duscha accepted this prompt and named Gemini, a party independent of
Claude, the I-7/I-7-R1 implementer. That decision activates only the bounded
authority in §4 for Gemini. No other person or agent inherits it.

The proposed execution target is the disposable `oracle-test` host. Its
documented kernel differs from Claude's I-7-R1 repository-host build, making
HA-1 the intended variation. The assignee must observe the facts afresh. A
documented value is not execution evidence, and a run in which none of HA-1 …
HA-3 actually differs is not R-5 and does not pass.

## 2. Objective and independence

Perform the accepted design's R-5: a second party independently provisions a
fresh build root from the accepted `toolchain.lock`, performs R-1 … R-3, and
shows that the output is byte-identical while at least one of HA-1 … HA-3
actually differs from Claude's accepted build.

The assignee must not reuse Claude's provisioned root, package cache, build
checkout, build output, trace or scratch evidence. Repository source and
committed/returned contract artifacts are inputs; Claude's narrative results
are comparison context, not substitutes for the assignee's observations.

This assignment is independent reproducibility evidence only. It is not a new
decoder review and does not repeat or replace XD-9/XD-11.

## 3. Controlling inputs

Before acting, read completely or by their governing reading maps:

1. `.agents/AGENTS.md`;
2. `docs/implementation-plan.md`, especially the reading map, §0, §13, §16,
   §17 and §20;
3. `docs/review/Handover information`;
4. `docs/operations/disposable-test-server.md`, including its restriction
   banner;
5. the accepted D2 design, especially §§5.3.2–5.3.8, §5.11, §5.12.3 and LD-8;
6. the I-7 implementation and I-7-R1 handbacks;
7. Codex's I-7 and I-7-R1 reviews; and
8. the I-7-R1 acceptance record.

Inspect `git status` and preserve the returned worktree exactly. Stop if the
accepted launcher inputs, lock, build-root manifest, expected digests, listing,
checker or contract differ from the accepted version-28 state and the
difference is not already part of the accepted worktree.

The accepted comparison values are:

| Item | Accepted value |
|---|---|
| review-manifest version | `28` |
| aggregate digest | `02d660c3bb8cd030a36ae1ece70da0de1756ca3052f3de74c89a15279a5c5abb` |
| `toolchain.lock` | `f92380735e32f9d7747834d684657d4087f14c7a22c0178703a50a70eef784cf` |
| `build-root.manifest` | `f08ba9de4374374fa91012021ce12fb83f6370be5547ee4e214232100c38e76f` |
| image | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` |
| listing | `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188` |
| map | `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d` |
| `launch.s` | `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706` |

Claude's accepted comparison facts are kernel `6.8.0-139-generic`, CPU model
`AMD EPYC-Milan`, and entry mechanism bubblewrap `0.9.0`. Treat these as the
first party's recorded facts; do not rewrite them from the R-5 environment.

## 4. Proposed execution authority after acceptance

Under Peter's acceptance naming Gemini, Gemini may:

* synchronize the current repository worktree to `oracle-test` using the
  canonical secret-excluding procedure;
* inspect the target's kernel release, CPU model/features and bubblewrap
  identity/configuration needed to record HA-1 … HA-3;
* create new, uniquely named disposable root, cache, checkout, output, trace
  and evidence directories under `/tmp` on `oracle-test`;
* download the lock's packages from its pinned signed snapshot into the new
  cache and verify every recorded digest;
* use the repository's existing `provision.py`, `enter.py`, build and verifier
  tooling for R-1 … R-3 and the existing repository/toolchain checks; and
* write one repository handback documenting the results and then stop.

This authority would permit network acquisition required by the pinned lock
and unprivileged bubblewrap execution on the disposable host. It would not
permit host package installation, replacement of host tools, persistent
system configuration, service operation, database access, launcher
installation, or use of the evidence harness's `--execute` path.

If another required dependency is absent or the unprivileged mechanism fails,
stop and report it. The only exception to the original `sudo` and package-
installation prohibition is Peter's recorded two-command `bubblewrap`
authority. Do not substitute an ambient toolchain or expand that exception.

## 5. Required procedure

1. Record the exact repository state and verify every accepted comparison
   digest in §3 before provisioning.
2. On `oracle-test`, freshly record:
   * kernel machine and release for HA-1;
   * CPU vendor, model and relevant feature flags for HA-2; and
   * entry mechanism name, version and the complete configuration/vector used
     to present the root and start R-2 for HA-3.
3. Compare those facts with Claude's accepted facts. Identify which of HA-1 …
   HA-3 actually differs. If none differs, stop: the run is not R-5.
4. Create an empty, unique root and an empty, unique package cache. Do not use
   any earlier root, cache or build output.
5. Provision from `toolchain.lock`. Verify the signed snapshot and every
   package-file SHA-256 before unpacking.
6. Perform R-1 inside the entered environment and in the same session that
   performs R-2. Require the regenerated manifest to be byte-equal to the
   committed `build-root.manifest`; `/etc/ld.so.preload` absent; and `/tmp` and
   `/var/tmp` empty and read-only inside the root.
7. Perform R-2 exactly as the first process, unprivileged, from the checkout
   root, with the accepted vector and an existing empty `build-out` directory.
   No interactive shell may run in the root first.
8. Perform R-3. Compare the image, listing, map and `launch.s` against
   `expected.sha256`, and compare the listing bytes with the committed listing.
9. Run the existing toolchain-dependent repository tests against this fresh
   root. Their IC-1 variants and T-L11/T-L10 checks are corroborating current-
   tree checks; they do not alter R-5's defined R-1 … R-3 pass condition.
10. Record exact commands, exit statuses, versions, digests and comparison
    results. Preserve no secret, credential or player data in evidence.

All work is serial. Do not reuse or run the platform database suites; R-5 has
no database dependency.

## 6. Pass, stop and difference rules

R-5 passes only if all of these hold:

1. the assignee is independent of Claude's I-7/I-7-R1 implementation;
2. the root and package cache were separately and freshly provisioned;
3. the R-1 manifest is byte-equal to the committed manifest;
4. the image, listing, map and `launch.s` equal the accepted digests;
5. the generated listing is byte-equal to the committed listing; and
6. the record demonstrates that at least one of HA-1 … HA-3 actually differed.

Any unexplained manifest, output, listing, intermediate, trace, environment,
test or digest difference is a hard stop. Do not update `expected.sha256`, the
lock, manifest, listing, contract, source or generated review artifacts to
make a difference pass. A difference correlated with HA-1 … HA-5 is a finding,
not permission to narrow the claim. Report the first difference and return for
independent review and maintainer direction.

## 7. Restrictions

Even after acceptance, this assignment does **not** authorize:

* installation of `rp11-launch` or a write outside disposable `/tmp` evidence
  locations and the single repository handback;
* H-1, H-2, D9-4, D9-5, PO-14, PO-17 or PO-18 discharge;
* RP-11 wiring, pass-configuration changes or making either pass executable;
* a controlled write, reboot, evidence band, real participant, real capture
  root, operational path or harness `--execute`;
* database, Discord, Sheets, Foundry or service access;
* protected-artifact access, secrets scanning, commit or push; or
* changes to launcher source, lock, manifests, expected values, tests,
  operational authorization drafts or project behavior.

Do not claim that R-5 proves decoder correctness, kernel semantics, installed
file identity, PO-9 as a whole, PO-14, RP-11 readiness or a package gate.

## 8. Required handback and stop gate

Write
`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-handback.md`
containing:

* assignee identity and independence statement;
* repository state and all §3 input digests;
* fresh HA-1 … HA-3 facts for both builds and an explicit difference table;
* fresh-root/cache identifiers and a statement that neither was reused;
* exact acquisition, R-1, R-2, R-3 and test commands and results;
* every produced digest and byte-comparison result;
* the R-5 verdict, with each §6 condition answered separately;
* checks not run and why;
* residual HA-1 … HA-5 and TD-1 … TD-4 trust, without claiming elimination;
* cleanup status for the disposable directories;
* security, configuration, deployment and rollback implications; and
* unresolved differences or questions for independent review.

Stop after the handback. R-5 evidence requires independent review and Peter's
acceptance before D9-3 can be treated as complete or any H-1 assignment can be
prepared. Peter's acceptance of this prompt would authorize only the bounded
R-5 run above, not its result or any later step.
