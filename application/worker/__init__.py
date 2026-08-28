"""`freedom-worker`: the process that executes durable reconciliation jobs.

Why this is a **process** and not a thread pool inside `freedom-web`, restated
where the code is rather than only in the operational contract (§3):

1. **The work holds the GIL for the whole of its ~9.6 seconds.** The parser is
   `json.loads` plus pure-Python NFC normalization and canonical-key ordering.
   Neither releases the GIL, so offloading to a thread inside the web process
   does not free the event loop — it stalls every other request, including the
   N-22 status polls that exist to report the job's progress and the `/healthz`
   check monitoring uses to decide the process is alive. A design in which
   watching a job prevents the job from being watched is not a design.
2. **Peak memory is per-job, and now measured at one real point.** A 16.3 MB
   artifact becomes a Python object graph several times larger, and the accepted
   upload bound is 64 MiB (N-20). `MemoryMax=2G` on a dedicated unit (N-47)
   protects the bot, three Foundry worlds and PostgreSQL on the shared host; the
   same ceiling on `freedom-web` would kill the portal instead of the job.

   **Measured, on 2026-08-27 (TC-PERF-01), closing RR-05:** a real 32-Actor
   folder peaked at **302 MiB**. That is one sampled peak from one real corpus —
   the whole of what has been measured.

   **Extrapolated, and it is not the same kind of statement:** real Actor data
   cost ~13-15x its input size where the synthetic fixture cost ~7.5x (N-26), so
   applying that ratio to N-20's 64 MiB input ceiling reaches **~1 GiB**. Nothing
   near that ceiling has ever been run, because no corpus near it exists; the
   figure is arithmetic on two real points, not an observation, and must not be
   cited as one.

   **`MemoryMax` was raised from 1G to 2G on 2026-08-27** (C-P3.5-Z) on that
   extrapolation, which had reached the old bound. It is a runaway guard rather
   than a budget: a job killed by it is an abandoned attempt, not a failure
   verdict — the lease expires, the reaper requeues it while an attempt remains,
   and the durable effect is fenced by the import's own unique constraints
   either way. `infra/systemd/freedom-worker.service.tmpl` is the single source
   of the number; this paragraph restates it and must not become a second one.
3. **Deploy and restart semantics differ.** A web deploy should be quick and
   frequent; a worker holding a 60-second lease should drain.

The queue itself stays in PostgreSQL, so this introduces a **process**, not a
technology: no broker, no second datastore, no new dependency.

Both processes run the same code from the same virtualenv, differing only by
`WORKER_ENABLED` — and startup refusal S-11 refuses the mistake of setting it
wrongly.
"""

__all__: tuple[str, ...] = ()
