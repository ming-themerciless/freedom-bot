# Gemini prompt — `cc1.v` reference-reproduction record remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R1`

Date: 2026-10-01

Assignee: Gemini

Status: **authorized documentation-only correction; no rerun or new inspection**

## 1. Objective and findings

Codex independently verified the retained Branch A artifacts: source and
fixture are byte-identical, both are 5,120 bytes with SHA-256
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`,
the regenerated manifest equals the committed manifest, and the four normative
outputs match. Three record defects nevertheless require correction:

1. **Missing preflight CPU-feature evidence.** The B1 prompt required the
   complete CPU model and relevant feature output from `lscpu`. The retained
   execution log contains architecture, model name, family, model and topology,
   but no CPU flags/features. This is an evidence omission and cannot be
   retroactively described as pre-provisioning evidence.
2. **Wrong snapshot transport.** Handback §7 says
   `http://snapshot.ubuntu.com/...`; `provision.py` and `toolchain.lock` use
   `https://snapshot.ubuntu.com/...`.
3. **Wrong directory-mode generalization.** Handback §3 says all fresh run
   directories have mode `0700`. The cache, work and evidence directories are
   `0700`, but provisioning deliberately leaves the build-root directory at
   `0755` through `provision.py`'s accepted post-install behavior.

Correct the record without rerunning, reprovisioning, inspecting new host
facts, or changing the substantive Branch A bytes.

## 2. Required context

Before editing, read:

1. `.agents/AGENTS.md` completely;
2. the implementation-plan reading map, §0, §13, §16, §17 and §20;
3. `docs/review/Handover information`;
4. the B1 prompt and B1 handback;
5. `provision.py` lines defining `SNAPSHOT_BASE` and the root-mode
   post-install behavior;
6. `toolchain.lock`'s `archive_base`; and
7. this prompt.

Inspect `git status` and preserve every unrelated change.

## 3. Required corrections

Edit only the B1 handback:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md`

Make all of the following changes:

* add a dated B1-R1 correction note naming all three defects;
* state that the retained preflight evidence did **not** include CPU
  flags/features, although it did record the model/family/topology shown;
* do not reconstruct, infer, quote from a later observation, or claim that
  current CPU flags are the missing preflight record;
* distinguish the verified exact CPU model required by the B1 proceed/stop
  condition from the omitted additional feature-detail record;
* correct the snapshot URL to
  `https://snapshot.ubuntu.com/ubuntu/20261001T000000Z`;
* correct the directory modes to build root `0755`, cache/work/evidence
  `0700`, and explain that `provision.py` deliberately sets the root to
  `0755` during accepted post-install processing;
* narrow any statement that B1 met every procedural requirement: the core
  Branch A result remains verified, but the CPU-feature preflight record is
  incomplete;
* retain the exact input, manifest, output, source and fixture hashes;
* retain the exact 5,120-byte length and `cc1check.py` result;
* retain Gemini's reported test results as Gemini's results; and
* retain the stop gate and the statement that R-5 was not performed.

Do not add fresh observations or commands to the B1 record. Do not convert the
missing preflight evidence into a post-run check.

## 4. Authority and restrictions

Gemini may modify only:

* the B1 handback named in §3; and
* the B1-R1 remediation handback named in §5.

No filesystem or host inspection beyond opening the specifically named
repository documents is authorized. Do not access the retained `/tmp` run,
run `lscpu`, hash or compare artifacts again, execute tests, provision, build,
download, use network access, SSH, rsync, `oracle-test`, `sudo`, package
operations, services, databases, or harness `--execute`.

Do not modify the fixture, launcher source, tests, lock, manifest, expected
digests, listing, governance documents, archive snapshots, accepted decisions,
other handbacks, commit state or staging area. No commit or push is authorized.

## 5. Required handback and stop gate

Write:

`docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r1-reference-reproduction-record-remediation-handback.md`

Include:

* the exact before/after statements for all three corrections;
* before/after SHA-256 of the amended B1 handback;
* an explicit statement that CPU flags/features remain absent from the
  retained preflight evidence;
* confirmation that no command, inspection, test, build or provisioning was
  repeated;
* confirmation that the fixture and retained `/tmp` evidence were untouched;
* `git diff --check` limited to the two authorized documentation files; and
* the unchanged Branch A digest result, incomplete procedural-evidence note,
  and R-5 stop state.

Stop after the handback. Do not start a fresh B1 reproduction or R-5.
