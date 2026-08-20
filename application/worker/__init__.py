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
2. **Peak memory is per-job and unmeasured.** A 16.3 MB artifact becomes a Python
   object graph several times larger, and the accepted upload bound is 64 MiB.
   `MemoryMax=1G` on a dedicated unit (N-47) protects the bot, three Foundry
   worlds and PostgreSQL on the shared host; the same ceiling on `freedom-web`
   would kill the portal instead of the job.
3. **Deploy and restart semantics differ.** A web deploy should be quick and
   frequent; a worker holding a 60-second lease should drain.

The queue itself stays in PostgreSQL, so this introduces a **process**, not a
technology: no broker, no second datastore, no new dependency.

Both processes run the same code from the same virtualenv, differing only by
`WORKER_ENABLED` — and startup refusal S-11 refuses the mistake of setting it
wrongly.
"""

__all__: tuple[str, ...] = ()
