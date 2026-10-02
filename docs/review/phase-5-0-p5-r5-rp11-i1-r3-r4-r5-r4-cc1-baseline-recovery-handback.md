# Handback — R-5 R4 `cc1.v` Baseline Recovery

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-R4`

Date: 2026-10-01

Assignee: **Gemini** (independent rebuilder)

Controlling Prompt:
[`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-gemini-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-gemini-prompt.md)

Accepted Target Digest:
```text
b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b
```

Status: **Branch B — exact artifact not recovered (failure of recovery). Gemini has stopped without creating a fixture or modifying existing files.**

> [!NOTE]
> **R4-R1 Correction Note (2026-10-01, Work ID `C-P5.0-R5-RP11-I1-R3-R4-R5-R4-R1`):**
> This handback was corrected under maintainer direction to address two accuracy defects:
> 1. Statements regarding repository worktree inspection were bounded to the exact filename and path searches recorded in §2. Differently named content across the repository worktree was not exhaustively hashed, and R4 did not authorize an expanded content scan. The finding confirms that no candidate path was identified by the recorded bounded searches.
> 2. The byte length of Gemini's stopped-run `cc1.v` candidate in the §3 table was corrected from "Recorded in stopped run" to `Unknown — artifact not retained and no byte length recorded` because no numeric byte length was retained in the cited record.
>
> The substantive Branch B disposition (baseline artifact not recovered, no fixture created, R-5 remains stopped) remains unchanged.

---

## 1. Result Branch and Outcome Summary

**Result Branch: Branch B — exact artifact not recovered.**

The baseline `cc1.v` file from Claude's accepted I-7 or I-7-R1 run, matching the sole accepted digest `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`, could not be recovered within the authorized sources and boundaries.

In accordance with Prompt §1, §4, §5 (Branch B), §6, and §7:
- No fixture was created under `infra/rp11-launch/verify/fixtures/` (no placeholder or empty fixture).
- No file was rebuilt, regenerated, or substituted.
- Gemini's stopped-run output `cdc0fe11…45f9` was rejected and not used as a baseline.
- No existing source, test, manifest, lock, listing, governance document, handback, or accepted artifact was modified.
- Gemini stops here. Baseline recovery failed, and a separate maintainer decision by Peter Duscha is required before any reference reproduction or next action.

---

## 2. Authorized Sources Inspected and Exact Bounded Operations

All inspections were strictly read-only and confined to the three authorized sources in Prompt §3:

### Source 1: Repository Worktree (including untracked files, excluding `.git` object contents)

* **Inspection Operations:**
  1. `git status --porcelain`: Inspected all tracked modifications and untracked files in the repository.
  2. `find /opt/freedom-blades/platform -path '*/.git' -prune -o -name '*cc1*' -print`: Located all paths matching `*cc1*` outside `.git`.
  3. `find /opt/freedom-blades/platform -path '*/.git' -prune -o -name '*.v' -print`: Located any files ending in `.v` outside `.git`.
  4. `find /opt/freedom-blades/platform -name 'build-out'`: Checked for any local `build-out` directory.
  5. `find tests -name '*cc1*' -o -name '*.baseline*' -o -name '*.v'`: Checked test fixtures and test directories.
  6. `find infra/rp11-launch`: Inspected the paths within the launcher directory tree.
* **Findings:**
  - Files matching `*cc1*`: Only documentation (`phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-gemini-prompt.md`, `phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md`, `phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md`), python helper `infra/rp11-launch/verify/cc1check.py`, and compiled bytecode `cc1check.cpython-312.pyc`.
  - Files matching `*.v`: None.
  - Directory `build-out`: None.
  - Fixture directory `infra/rp11-launch/verify/fixtures`: Does not exist.
  - No candidate path was identified by those recorded searches. Differently named content across the repository worktree was not exhaustively hashed, and R4 did not authorize an expanded content scan.
* **Disposition:** Bounded name and path searches completed; zero candidate baseline files were identified by the recorded searches in the repository worktree.

### Source 2: Exact Scratch Paths or Retained Artifacts Named in I-7 or I-7-R1 Records

* **Inspection Operations:**
  1. Thorough textual analysis of all I-7 and I-7-R1 documents:
     - `phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md`
     - `phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md`
     - `project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md`
     - `phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md`
     - `phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md`
     - `project-review-2026-10-01-p5-r5-rp11-i7-r1-ic1-environment-remediation.md`
     - `project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md`
* **Findings:**
  - The historical records repeatedly note that build roots, package archives, traces, and intermediate files were ephemeral and kept only in uncommitted session scratchpads:
    - *"Downloads and roots live in the session scratchpad."* (I-7 handback §3, line 139)
    - *"These scratch files were outside the repository and are not proposed as product tooling."* (I-7 review §6, line 72)
    - *"The build roots and downloads live only in the session scratchpad."* (I-7 handback §10, line 403)
    - *"The fresh root, package cache, traces and evidence live only in the session scratchpad."* (I-7-R1 handback §10, line 380)
  - The build paths referenced in the logs (`/rp11/co`, `/rp11/alt/checkout`, `build-out/cc1.v`) were disposable container-internal mount points inside Bubblewrap namespaces.
  - The records name scratch file concepts (e.g. `derived-expectations.txt`), but do **not** document any exact persistent host filesystem path (e.g., no explicit `/path/to/...`).
* **Disposition:** Unavailable. Per Prompt §3: *"If no exact candidate location is documented or directly exposed, that source is unavailable; this is not authority to expand the search."*

### Source 3: Claude I-7/I-7-R1 Session Artifacts or Attachments Directly Exposed to Gemini

* **Inspection Operations:**
  - Inspected incoming invocation parameters, conversation transcript, tool context, and collaborative environment.
* **Findings:**
  - No session artifacts, attachments, or file transfers from Claude's previous sessions were attached or exposed to Gemini by the collaboration client.
* **Disposition:** Unavailable. Per Prompt §3: *"If no exact candidate location is documented or directly exposed, that source is unavailable; this is not authority to expand the search."*

---

## 3. Candidate Provenance, Byte Length, SHA-256, and Disposition

| Candidate Identifier | Provenance | Byte Length | SHA-256 | Disposition |
|---|---|---|---|---|
| **Gemini stopped-run `cc1.v`** | Generated during Gemini's stopped R-5 rebuild on `oracle-test` (2026-10-01) | Unknown — artifact not retained and no byte length recorded | `cdc0fe118866d838a9b399d35975e7627e22b3f43e8ab2bfcdf9ed5ff19045f9` | **REJECTED.** Does not match accepted digest `b77f92dc…`. Explicitly prohibited as baseline by prompt §6. |
| **Documentation digest strings** | Mentions in I-7 handbacks, I-7-R1 handbacks, and R3 acceptance decision | 64 chars (string) | N/A (text string, not artifact bytes) | **REJECTED.** A digest string in documentation is not recoverable content per prompt §1 and §6. |
| **I-7/I-7-R1 retained artifact bytes** | Claude's historical accepted run | Unknown | `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` | **NOT RECOVERED.** Bytes were retained only in ephemeral session scratchpad outside the repository and are not available in any authorized source. |

**Verdict:** Zero authentic candidate artifacts matching `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` were recovered.

---

## 4. Fixture Source/Copy Equality and `cc1check.py` Result

**N/A (Branch B applies).**

Per Prompt §4 and §5:
> *"Creating the fixture is authorized only for an exact digest match. If no match is found, do not create a placeholder or empty fixture."*
> *"State clearly that baseline recovery failed and that a separate maintainer decision would be required before any reference reproduction. Stop without creating a fixture."*

Accordingly, no fixture was created at `infra/rp11-launch/verify/fixtures/cc1.v.baseline`, and no `cc1check.py` run against a fixture was performed.

---

## 5. Checks Not Run and Why

- **Broad filesystem crawling:** Not run. Prompt §3 explicitly restricts inspection and prohibits crawling `/tmp`, home directories, agent configuration, caches, logs belonging to other tasks, shell history, credentials, secret files, process environments, `/proc`, or the full filesystem.
- **Inter-agent contact:** Not run. Prompt §3 prohibits contacting Claude or another agent without separate maintainer authority.
- **Host action or R-5 rerun on `oracle-test`:** Not run. Prompt §6 strictly prohibits SSH, rsync, `oracle-test`, network access, download, `sudo`, package action, provisioning, build-root creation, compiler or launcher build, R-5 rerun, reference-environment reproduction, or service actions.
- **Controlled writes or code changes:** Not run. Prompt §6 strictly prohibits modifying existing sources, tests, manifests, locks, listings, governance documents, or accepted artifacts.
- **Reference-environment reproduction:** Not run. Re-deriving `cc1.v` by rebuilding on a reference host is prohibited by prompt §1 and §6.

---

## 6. Residual Trust and Unresolved Evidence

1. **Baseline Bytes Never Committed:** Claude's accepted I-7 and I-7-R1 runs recorded the SHA-256 digest `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b` in review documentation, but the underlying raw bytes of `build-out/cc1.v` were never checked into the repository or preserved in a durable project location.
2. **Intermediate Difference Unresolved:** Gemini's stopped R-5 build produced `cdc0fe118866d838a9b399d35975e7627e22b3f43e8ab2bfcdf9ed5ff19045f9`. While all four normative frozen outputs (`rp11-launch`, `rp11-launch.map`, `rp11-launch.x86_64.listing`, and `launch.s`) reproduced byte-identically across HA-1, HA-2, and HA-3 variations, the intermediate compiler diagnostic `cc1.v` differed. Under accepted decision LD-8, an unexplained difference is a hard stop.
3. **Automated Diff Blocked:** Because the baseline bytes are absent, `cc1check.py` cannot compute an automated byte-level diff to identify whether the difference stems from GCC's memory-derived GGC heuristics, host environment differences, or other factors.
4. **Maintainer Authority Required:** Proceeding further requires an explicit maintainer decision by Peter Duscha to authorize an agreed path, such as:
   - Providing Claude's retained session bytes if preserved in external maintainer archives; or
   - Authorizing a dedicated reference reproduction under strictly controlled host conditions to capture and commit the baseline `cc1.v` bytes; or
   - Formally determining the required status of intermediate non-normative compiler diagnostic logs under LD-8.

---

## 7. Security, Configuration, Deployment and Rollback Implications

- **Security:** Read-only inspection conformed strictly to the bounded sources. No credentials, secrets, process environments, or unauthorized directories were inspected or exposed.
- **Configuration & Deployment:** No changes were made to host systems, service files, environment configurations, dependencies, or database schemas.
- **Rollback:** Entirely self-contained. The only file created is this handback document (`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-handback.md`). All existing repository files and Git status remain strictly unchanged.

---

## 8. Proposed Independent-Review Focus

Codex and Peter Duscha should focus review on:
1. **Source Search Conformance:** Verifying that the search for `cc1.v` adhered to the bounded repository worktree searches and documented records without violating the search boundaries of Prompt §3.
2. **Strict Adherence to Negative Constraints:** Verifying that no placeholder fixture was created, no unverified candidate was adopted, no files were modified, and no host or build actions occurred.
3. **Branch B Determination:** Confirming that Branch B (recovery failed) is the accurate and required disposition.
4. **Next Decision Authority:** Peter Duscha's determination regarding the mechanism to establish or recover baseline evidence for `cc1.v` before any future R-5 rerun is considered.

---

## 9. Stop Gate

In accordance with Prompt §1, §5 (Branch B), §6, and §7, **Gemini stops here**. No host action, reference reproduction, fixture creation, or R-5 rerun has been performed. Gemini awaits maintainer decision and review.
