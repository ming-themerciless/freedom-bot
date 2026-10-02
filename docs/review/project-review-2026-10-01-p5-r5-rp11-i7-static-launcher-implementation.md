# Codex review — I-7 zero-`ret` static-launcher implementation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-I7-R1`

Date: 2026-10-01

Implementer: Claude

Independent reviewer: Codex

Reviewed handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)

Disposition: **one Blocking finding. Return for narrow remediation and
independent re-review.** The image, XD/T-L11/T-L10 chain and Codex's XD-11
decode pass as reviewed; IC-1 does not yet establish the exact environment
closure required by LD-8. Peter Duscha remains the acceptance authority.

Nothing was installed, wired or run operationally. No SSH, `oracle-test`,
database, service, protected-artifact, harness `--execute`, R-5, H-1/H-2,
controlled-write, reboot, commit or push action was performed. PO-9 and PO-14
remain open; RP-11 remains unwired and unmet; `plan.is_executable=False`;
P5.0-R5 remains Blocking; OD-62 G-A remains conditional; Package 5.0 remains
not ready.

## Finding

### I7-R1-1 — Blocking — IC-1 admits non-exact class-B environments

`infra/rp11-launch/verify/ic1check.py::_check_env` checks that the four base
variables have expected values and rejects names outside an allowed set. It
does **not** require the allowed additions to be present. Apart from `PWD` when
present, it does not validate their values. Consequently all of these can pass
the environment check:

* the entry `env` process without `PWD`;
* ordinary build tools without `PWD` or `OLDPWD`;
* `cc1` without the four driver additions; and
* `cc1` with arbitrary values for `COLLECT_GCC`, `COLLECT_GCC_OPTIONS`,
  `OFFLOAD_TARGET_NAMES` and `OFFLOAD_TARGET_DEFAULT`.

That is permission, not the exact environment asserted by IC-1 condition 3
and the handback. LD-8 makes a passing IC-1 a condition of accepting the bound
build-root claim. The implementation cannot use an under-constrained checker
to establish that condition, especially where the newly admitted values reach
a class-B process.

Required remediation:

1. specify the exact expected name/value set for each process class and check
   equality, not only absence of unknown names;
2. derive or pin the expected driver-added values without accepting arbitrary
   trace contents as their own authority;
3. add negative tests for each missing required addition and each changed
   value, including `OLDPWD` and every driver-added variable;
4. rerun IC-1 on a fresh pinned-root build and show byte-identical R-2 outputs;
   and
5. return the narrow change for independent re-review.

The design discrepancy D-2 should be accepted only after that remediation.
Naming deterministic additions is a reasonable clarification; admitting
unconstrained additions is not.

## Independent decoding and launcher result

Before opening XD, its spelling table/corpus, or the committed listing, Codex
reproduced the expected image from the committed lock and wrote a separate,
narrow ELF64/x86-64 decoder from the actual `.text` bytes. The frozen decoder
SHA-256 was `48594e412b06c65315fa6de8ae0546da3561a9e1013f687a4d5e73d1f5c04e3e`;
its emitted stream SHA-256 was
`eb9c584a91f811a54d4e79ccd1f9dccd592038d91d976b538584793eff500b1a`.
These scratch files were outside the repository and are not proposed as
product tooling.

The independent result was:

* image SHA-256 `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`;
* `.text` `0x4000b0..0x4005bf`, 1,295 bytes, completely tiled by 332
  instructions;
* 332/332 agreement with XD on starts, lengths/byte fields, mnemonics,
  registers, effective addresses, encoded immediates, operand order and direct
  targets;
* every direct target is an instruction boundary;
* exactly three direct `jmp` instructions, including the one `_start` entry
  edge; and
* no `call`, `ret`, indirect transfer or transfer target read from machine
  state.

This satisfies XD-11/LD-9 option (i) for the returned image. Review of XD's
closed table, decoder, citations, corpus and failure paths found no independent
decoding defect. XD reads the image through its own ELF parser, the spelling
table cannot affect boundaries/bytes/targets, T-L12 exercises every table row,
the forbidden forms and XD-5 classes, and T-L11 binds the same expected image
and listing digests before accepting T-L10. XD-9 and the T-L11 → T-L10 binding
pass this review.

The raw stream and T-L10 tables also support HR-1 … HR-6 as returned: two
functions tile `.text`; the maximum calculated stack depth is 223 bytes; all
stores are fixed frame stores; loads are limited to the initial `argc` and the
bounded input-derived reads; the 29 syscall sites resolve to the nine-call
inventory; old-action/output pointers are NULL; and each failure path writes
its fixed diagnostic, calls `exit_group` with the specified status and ends in
`ud2`.

## Other review dispositions

* **D-1, R-1/R-2 “same session”: recommend acceptance.** One `enter.py build`
  invocation performs the manifest vectors and build as consecutive entries
  over the same read-only root, with the intervening entry mechanism already
  named as HA-3. This preserves the intended bound-root check; it does not
  claim to eliminate HA-3.
* **D-3 … D-17:** no additional finding. The PCH refusal closes the checkout
  probe; T-L4 is correctly described as coarse while T-L10 proves syscall
  constants; X-12/X-13 are necessarily traced because the build creates the
  listing; manifest coverage remains explicit; T-L2 accurately leaves the I-6
  half owed; and the remaining items are recorded residuals or clarifications.
* **R-5:** not performed. This review is not R-5 and varies none of HA-1 …
  HA-3. LD-8 still requires an independent rebuild that actually varies and
  records at least one of those inputs.

## Checks performed

* isolated provisioning from `toolchain.lock`, followed by the pinned-root R-2
  build: exit 0; all five returned output digests matched;
* independent XD-11 decode and semantic comparison: 332/332 agreement;
* `verify/tl11.py` on the reproduced image and committed listing: pass,
  `tl10_evidence: true`, T-L10 table digest `25779797...e341`;
* `tests/test_rp11_launch_source.py`: 275 passed;
* `tests/test_rp11_launch_toolchain.py` with the pinned root: 10 passed;
* `tests/phase_5_0_evidence`: 3,370 passed, zero skipped;
* Python compilation of the new Python sources: pass; and
* `git diff --check`: pass.

The pytest runs emitted the two pre-existing unknown asyncio configuration
warnings. The unrestricted bot/web/Foundry suites were not run: they are not
the narrow repository-local suites affected by this return, and the active
restriction forbids the documented test-server path. No claim is made for
them.

## Re-review boundary

Remediation should be confined to the exact IC-1 environment contract,
checker, negative tests, any corresponding pinned manifest data and regenerated
review artifacts. It must not change the accepted image, decoder contract,
operational wiring or authority. Any image/listing/XD digest change requires
the complete decoding and T-L11/T-L10 review again rather than this narrow
re-review path.
