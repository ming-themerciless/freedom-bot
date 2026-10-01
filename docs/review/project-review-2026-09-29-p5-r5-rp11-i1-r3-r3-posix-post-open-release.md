# Codex independent review — PosixFilesystem post-open descriptor release

Review ID: `C-P5.0-R5-RP11-I1-R3-R3-REV1`

Date: 2026-09-29

Reviewed return:
[`phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r3-posix-post-open-release-handback.md)

Disposition: **no Blocking, Important or Optional finding. Recommend
acceptance.** Peter Duscha remains the acceptance authority.

## Review conclusion

The bounded remediation satisfies its assignment. `PosixFilesystem.create_file`
and `PosixFilesystem.openat` retain ownership of the descriptor returned by
`os.open` until successful hand-off. Every failure after acquisition and before
return removes any tracked entry, attempts exactly one close and re-raises the
first causal failure. The repair does not retry a failed close, release an
inventory descriptor, or unlink, rename, truncate, repair or otherwise alter a
pathname. A failed optional initial write leaves the exclusively created name
and written prefix exactly as the failing operation left them.

The use of `except BaseException` is appropriate: ownership cleanup also
applies to non-`Exception` exits while the original exception propagates
unchanged. `_abandon` deliberately swallows a close error and adds no exception
note; that matches the assigned first-causal-failure rule and avoids retrying a
descriptor number the kernel may already have released.

The test oracle is adequate. It wraps only `descriptors.py`'s `os` binding,
performs real kernel operations, records acquisitions and closes, proves the
abandoned number is absent from the filesystem object's table, excludes
inventory descriptors and supplements those assertions with `/proc/self/fd`
counts where available. The success-path cases prove ownership still transfers
to callers.

## Exact review inputs

The returned hashes match the workspace:

* `descriptors.py`: `fbf37a86599c502aad81c44b4434dd892f855d6e3ad82d7ab4b822dc7205fb89`;
* `review_manifest.py`: `be0dd079980530f24cad39acc21efb4067b6d6fa7cf140a52a03526de1f05117`;
* generated manifest: `add5524b82ee44d25cd09ef335c936b24f2ce94014912444d30e3bc17678595e`;
* generated plan: `c3591e654f759892a7aab5d4b895c2234b370c46a72234715cde8b12bcc33237`;
* `test_lab_integration.py`: `266212e8d94a7adaff83ed0e936a7f4120d5d81d22e88fdb5c6cdaf5b4249f51`;
* `test_r16_remediation.py`: `949fba3046206a065f164b64d39843c000bd02dfac0f79622d5b205439fc7302`;
* manifest version: **26**; and
* review-input digest: `526dd44648833ecb5b7bc5de111478323bf6b44c3ea076916896ba883c7f2f28`.

The operational draft remains byte-unchanged at `5c6046fc…`.

## Independent verification

All pytest processes ran serially on the repository host with
`TEST_DATABASE_URL` unset, bytecode disabled and pytest's cache provider
disabled.

* 16 focused R3 regressions: **16 passed, 0 skipped**.
* Entire `tests/phase_5_0_evidence` package with soft descriptor limit 1024:
  **3364 passed, 0 skipped**.
* Entire package at the default descriptor limit: **3364 passed, 0 skipped**.
* Harness dry run only: digest `526dd446…`, 138 steps, 43 mutations, 47 cleanup
  steps, four unresolved conflicts and `executable=False`.
* Scratchpad manifest and plan were byte-identical to the checked-in artifacts;
  their SHA-256 values were `add5524b…` and `c3591e65…` respectively.
* `git diff --check`: clean.

Each pytest run emitted only the two disclosed unknown-pytest-option warnings
for `asyncio_default_fixture_loop_scope` and `asyncio_mode`.

## Limits and recommendation

This review recommends that Peter Duscha accept the R3 remediation and version
26 review inputs. It does not itself approve a digest for execution, wire or
satisfy RP-11, resolve C-11 or the pinned launcher environment, authorize an
operational pass, or change a package gate.

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

No SSH, synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push occurred.
