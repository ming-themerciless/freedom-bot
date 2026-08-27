# C-8 — proposed staging target for the backup/restore drill

**Date:** 2026-08-26 · **Author:** Claude, P3.5 working Technical Lead ·
**Status when written:** PROPOSED, not applied.

**Status now: ACCEPTED AS ROUTE A AND APPLIED, 2026-08-26.** Peter Duscha, as
Operations Owner, chose route A the same day; the change and its three
falsifying tests are in `infra/postgresql/backup-restore-drill.sh` and
`tests/test_database_backup_restore.py`, and the bot suite ran **2420 passed**
after them. Recorded as decision **D-q**, change-log **C-P3.5-V**. The text below
is left exactly as it was proposed, so the decision can be read against what was
actually put to him.

**Why it exists:** SP-10 — TC-OPS-02's **staging half** — needs a backup, restore
and rollback rehearsal against `freedom_staging`. `infra/postgresql/backup-restore-drill.sh`
is the tested instrument for exactly that round trip, and it **refuses any target
but `freedom_dev` and `freedom_test`, by design**. Its own header says so:

> It refuses to run against staging or production. Recovering those means
> restoring a verified off-host backup under the procedure in
> `docs/operations/database-development.md`, never running a drill script.

So SP-10 has two honest routes, and I am not choosing between them alone:

| Route | What it costs | What it risks |
|---|---|---|
| **A — extend the guard**, as proposed below | one reviewed change to a safety-critical script | the script's documented "never staging" property becomes "staging only deliberately". That is a real weakening of a stated invariant, however carefully it is fenced |
| **B — a separate written procedure**, run by hand | the operator types the same six steps the script already performs, with no inventory comparison unless he does it manually | human error in the destroy/restore step, and weaker evidence: the script's inventory comparison is what makes TC-OPS-02 a *verified* restore rather than a successful dump |

**My recommendation is A**, because the evidence quality difference is the whole
point of TC-OPS-02 — plan §14.3 asks for "restore tests, not merely backup
success messages" — and because a hand-run procedure has no falsifying test at
all. But A changes a security-relevant refusal, so it is Peter's decision with
Codex's review, not mine.

---

## 1. The change

Two defects in the current shape are worth fixing while the file is open, and
both are visible in the diff:

1. **The allowlist is written twice** — once for the requested name (§0a) and
   once for the *connected* name (§0c). Two places to edit is one place to
   forget, and the second one is the security-relevant one.
2. **A staging target must be a deliberate act, not a typo.** The proposal
   requires **two independent, non-default signals**: the environment variable
   `FREEDOM_DRILL_ALLOW_STAGING=1`, and `FREEDOM_DRILL_STAGING_CONFIRM` set to
   the exact database name. Neither alone is enough, and neither is a default.
   A mistyped positional argument cannot reach the staging path.

```diff
--- a/infra/postgresql/backup-restore-drill.sh
+++ b/infra/postgresql/backup-restore-drill.sh
@@
-# It refuses to run against staging or production. Recovering those means
-# restoring a verified off-host backup under the procedure in
-# docs/operations/database-development.md, never running a drill script.
+# It refuses production outright. It refuses staging *by default*, and accepts
+# it only when the operator supplies two independent, non-default signals
+# (FREEDOM_DRILL_ALLOW_STAGING and FREEDOM_DRILL_STAGING_CONFIRM naming the
+# exact database). That path exists for one accepted procedure — P3.5's SP-10,
+# TC-OPS-02's staging half — and is announced loudly when it is taken.
+#
+# Recovering production means restoring a verified off-host backup under the
+# procedure in docs/operations/database-development.md, never running a drill
+# script.
@@
 DATABASE="${1:-freedom_dev}"

 # ---------------------------------------------------------------------------
 # 0a. Only disposable databases, by name
 # ---------------------------------------------------------------------------

-case "${DATABASE}" in
-  freedom_dev | freedom_test) ;;
-  *)
-    echo "Refusing to drill against '${DATABASE}': only freedom_dev and freedom_test" \
-         "are disposable." >&2
-    exit 2
-    ;;
-esac
+# Computed once and reused by the connected-database gate below (§0c). The
+# previous shape repeated the list, and the copy that matters for safety is the
+# second one — the one that checks where the connection actually landed.
+PERMITTED_DATABASES="freedom_dev freedom_test"
+
+if [[ "${DATABASE}" == "freedom_staging" ]]; then
+  # Two independent signals, neither a default, and the second one has to name
+  # the database: a stray "export FREEDOM_DRILL_ALLOW_STAGING=1" in a shell
+  # profile cannot by itself turn a mistyped argument into a staging drill.
+  if [[ "${FREEDOM_DRILL_ALLOW_STAGING:-}" == "1" \
+        && "${FREEDOM_DRILL_STAGING_CONFIRM:-}" == "freedom_staging" ]]; then
+    PERMITTED_DATABASES="${PERMITTED_DATABASES} freedom_staging"
+    echo "=====================================================================" >&2
+    echo "STAGING DRILL. This DESTROYS AND RESTORES the freedom_staging schema." >&2
+    echo "Authorized for SP-10 (TC-OPS-02 staging half) under SG-2 only." >&2
+    echo "The dump taken in step 1 is the only thing standing between this run" >&2
+    echo "and a lost staging database. Verify it before step 3." >&2
+    echo "=====================================================================" >&2
+  else
+    echo "Refusing to drill against 'freedom_staging': it needs both" \
+         "FREEDOM_DRILL_ALLOW_STAGING=1 and FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging." >&2
+    exit 2
+  fi
+fi
+
+if [[ " ${PERMITTED_DATABASES} " != *" ${DATABASE} "* ]]; then
+  echo "Refusing to drill against '${DATABASE}': only ${PERMITTED_DATABASES}" \
+       "may be drilled." >&2
+  exit 2
+fi
@@
-case "${CONNECTED_DATABASE}" in
-  freedom_dev | freedom_test) ;;
-  *) refuse_connection "'${CONNECTED_DATABASE}' is not a disposable database." ;;
-esac
+# The same list, not a second copy of it. This gate is the security-relevant
+# one: it checks where libpq actually landed, after every redirection.
+if [[ " ${PERMITTED_DATABASES} " != *" ${CONNECTED_DATABASE} "* ]]; then
+  refuse_connection "'${CONNECTED_DATABASE}' is not a permitted drill target."
+fi
```

**What does not change:** every connection proof — the libpq-configuration
refusals, the `PGHOSTADDR` refusal, the loopback-TCP refusal, the Unix-socket
requirement, the landed-database comparison — is untouched and still runs before
anything is dumped or dropped. The staging path is gated *in addition to* those,
never instead of them. `freedom_production` remains refused with no override at
all.

---

## 2. The falsifying tests that must accompany it

Written to the existing harness in `tests/test_database_backup_restore.py`, which
already runs the script in a subprocess with a cleaned libpq environment.

The important one is the **third**: it proves the staging name gate *opens*
without ever letting a staging drill run, by supplying both signals and then a
hostile `PGHOSTADDR`. Exit `2` means the name was refused; exit `3` means the
name was accepted and the **connection** was refused with nothing touched. The
two are distinguishable, so the test can assert the gate opened without
destroying anything.

```python
def test_staging_is_refused_without_both_signals(tmp_path):
    require_postgresql_tools()

    for environment in (
        {},
        {"FREEDOM_DRILL_ALLOW_STAGING": "1"},
        {"FREEDOM_DRILL_STAGING_CONFIRM": "freedom_staging"},
        {"FREEDOM_DRILL_ALLOW_STAGING": "1",
         "FREEDOM_DRILL_STAGING_CONFIRM": "freedom_dev"},
    ):
        completed = run_drill("freedom_staging", tmp_path, environment)
        assert completed.returncode == 2, environment
        assert "needs both" in completed.stderr
        assert not list(tmp_path.iterdir()), "nothing may be written by a refusal"


def test_production_has_no_override_at_all(tmp_path):
    require_postgresql_tools()

    completed = run_drill(
        "freedom_production",
        tmp_path,
        {"FREEDOM_DRILL_ALLOW_STAGING": "1",
         "FREEDOM_DRILL_STAGING_CONFIRM": "freedom_production"},
    )

    assert completed.returncode == 2
    assert not list(tmp_path.iterdir())


def test_both_signals_open_the_name_gate_and_the_connection_gate_still_refuses(tmp_path):
    """The gate opens — proved without ever drilling staging.

    Exit 2 is "the name was refused"; exit 3 is "the name was accepted and the
    connection could not be proven safe, so nothing was touched". Asserting 3
    here is what shows the staging path is reachable, while the hostile
    PGHOSTADDR guarantees the drill itself never begins.
    """
    require_postgresql_tools()

    completed = run_drill(
        "freedom_staging",
        tmp_path,
        {"FREEDOM_DRILL_ALLOW_STAGING": "1",
         "FREEDOM_DRILL_STAGING_CONFIRM": "freedom_staging",
         "PGHOSTADDR": "203.0.113.5"},
    )

    assert completed.returncode == 3
    assert "Nothing was dumped, dropped or restored." in completed.stderr
    assert not list(tmp_path.iterdir())
```

---

## 3. What I am asking for

1. **Codex** — review the weakening on its merits: is the two-signal gate
   sufficient fencing for turning a "never staging" refusal into a "staging only
   deliberately" one, and is route A the right call against route B?
2. **Peter, Operations Owner** — decide A or B. If A, the change is applied,
   the three tests above land with it, and the full suite is re-run before SP-10
   is executed. If B, I write the manual procedure instead and SP-10's evidence
   is correspondingly weaker, which the submission will say plainly.

**Until that decision, SP-10 stays `Not Run` and nothing is applied.**
