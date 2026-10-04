# Independent review — Antigravity delivery redesign and R4 proposal

Date: 2026-10-04  
Reviewer: Codex  
Drafting/implementation assignee: Claude  
Work ID: `C-P5.0-R5-RP11-FRESH-D1`

Reviewed:

- [`phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-handback.md`](phase-5-0-p5-r5-rp11-antigravity-delivery-redesign-handback.md)
- [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r4.md), SHA-256 `12c07e4b0639a436baccee2381dbacdc02396406ff38e9e13bf5e2f09844e8df`, 132,703 bytes
- `tools/r5_runner/r5run.py`, SHA-256 `4ef88bd6059af6624bea9c4155ab895076e6076d031efd6c0fe60f13a63be015`, 58,050 bytes
- the 17 static resources under `tools/r5_runner/blocks/`
- `tests/test_r5_runner.py`, SHA-256 `6bc5320c389f4f816297782436d0f4c97d084ae6dbefdb983e3d2255f26b448f`, 30,835 bytes

## Disposition

The implementation is technically strong and resolves the command-byte,
interactive-stdin, misleading-zero-status and mandatory-closeout defects in
design. One **Important** workflow finding requires narrow remediation before
acceptance or activation. There is no Blocking finding.

### R4-D1-1 — Important — early Antigravity return tells Gemini to stop before the required terminal state

R4 §13 says that if Antigravity returns control before the runner's final line,
Gemini must not wait or poll; it reports that the command did not finish and
stops while the runner continues. This conflicts with the canonical `/goal`
instruction and the user's operating requirement: Gemini must not stop until
PASS, INVALID RUN or HARD STOP and the final handback and closing record are
fully written. It would also make “Gemini finished” ambiguous while an
authorized remote run might still be active.

Remediation: authorize Gemini to use Antigravity's wait facility only for the
same already-started runner task until that task completes and prints its final
line. This is not a second command, process poll, retry, input, EOF or signal.
Gemini must neither yield to the user nor launch another action while waiting.
If the wait facility itself reports a terminal transport failure while the
runner's state is unknown, Gemini reports that condition and stops; it must not
reinvoke or manipulate the process.

The assignment, single-command section and resolved `/goal` explanation must
state this consistently. Add focused tests for any runner or invocation-text
change, but do not alter the substantive R3 blocks.

## Technical review

Subject to `R4-D1-1`, the redesign meets its objective:

- static resources preserve R3's block bodies and are digest/length pinned;
- the runner verifies itself, all resources and the focused test before any
  host action and executes the verified in-memory bytes;
- child standard input is a closed pipe or `/dev/null`, with no terminal,
  shell wrapper, pasted heredoc or manual EOF;
- stdout, stderr and the true child status are captured separately;
- missing output with status 0 becomes a HARD STOP;
- the attempt ledger enforces order and exactly-once attempts;
- first failure prevents later operational steps, preserving the S4b.end
  exception;
- S12.start, body rendering and S12.end are attempted unconditionally;
- the handback is created exclusively, sealed before S12.end and never
  overwritten or edited afterward; and
- the runner performs no cleanup, retry, package change or privilege action.

## Independent checks

- Focused suite: **75 passed**, 0 skipped, with the two disclosed local
  pytest-configuration warnings.
- `/usr/bin/python3`: Python 3.12.3, satisfying the runner's Python 3.10 floor.
- `py_compile` for runner and focused test: pass.
- Recomputed runner, test and R4 identities: match Claude's handback.
- Inspected the single `rsync` argument-vector resource: it preserves the
  documented secret-excluding arguments and `/var/tmp/<RUN>-checkout/`
  destination without shell evaluation.
- Inspected first-failure, INVALID RUN, incomplete-output, signal, renderer
  failure, S12 closeout and immutable-handback paths.
- `git diff --check`: pass.

No R-5 block or remote command was run. Codex did not access `oracle-test`.

## Recommended decisions after remediation

Codex recommends:

1. **U-14:** Gemini waits through Antigravity's wait facility for the same
   runner task until its final line; no user turn, input, EOF, signal, second
   command or retry.
2. **U-15:** a pre-run refusal consumes the activation. This is the clearest
   fail-closed rule and prevents an unreviewed second invocation.
3. **U-16:** retain no runner timeout. A local timeout could terminate SSH
   while leaving remote work alive, weakening the first-stop guarantee. A
   genuinely hung run requires a separately authorized recovery decision.
4. **U-17:** accept invocation-based attestation. Gemini explicitly supplies
   `--executor Gemini --attest-independence`; the verified runner records it
   before Step 1.
5. Confirm the proposed work ID and handback path only after R4-R1 is reviewed.
6. Commit the 19 controlled runner/resource/test files before activation so
   S1.4 can bind them to `HEAD`. The R4 assignment and governance records may
   be committed in the same reviewed administrative change, but no execution
   should be activated while those controlled files are untracked.

R4 remains a proposal. No host access or new run is authorized.
