# B-1 settlement — observation appendix

Date: 2026-08-10
Observed by: Claude
Relates to: finding **B-1**, change-log **C-18**,
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md)

This is the reproducible half of C-18's evidence. The remediation record states
what was observed; this states **how**, in full, so that the reviewer's question
4 -- "reproduce that rather than taking the record's word" -- can actually be
acted on. Nothing here is a claim; the claims are in the remediation record.

Two environments were used:

- an **isolated rig**: a second Caddy 2.10.2 process on high ports with
  `admin off`, and a stub upstream standing in for the endpoint. The production
  Caddy was never stopped, reconfigured or reloaded for any rig run. Every claim
  tested on the rig is about the proxy and the route, not about the application,
  which is why a stub upstream is sufficient and a real one would only add
  failure modes.
- the **production Caddy**, in maintainer-authorized windows, for the three
  things a rig cannot establish: this host's stop behaviour, the Cloudflare edge,
  and the real configuration file and reload path.

## Results, in one table

| # | Environment | Observed |
|---|---|---|
| 1 | rig | a request accepted by the proxy with **no upstream connection made** survived the endpoint stop and was delivered and answered `201` after the restart |
| 2 | rig | the same episode with the proxy terminated: **nothing delivered**, client connection closed |
| 3 | rig | `uri strip_prefix` presented `/api/v1/foundry/snapshots` upstream; `caddy adapt` ordered `request_body` -> `strip_path_prefix` -> `reverse_proxy` with no `order` directive |
| 4 | rig | a **deleted** `handle` block falls through to an empty `200` |
| 5 | rig | a block **replaced** by `respond 410` answers `410`, endpoint up or down |
| 6 | rig | endpoint down, proxy up, live route -> `502` |
| 7 | production | public name answered **`521`** through Cloudflare, submission path and site root alike |
| 8 | production | `systemctl show caddy -p Restart` is **`no`** |
| 9 | production | a **UDP `:443`** listener exists alongside the two TCP ones |
| 10 | production | stop with **nothing in flight**: process and listeners gone in **4 ms** |
| 11 | production | stop with **one request held open**: listeners gone in **0.5 ms**, process gone at **4.3 s**, held connection closed with nothing delivered |
| 12 | production | step 4 phase 1: retired path `410`, recovery path `401`, all three Foundry sites unaffected across the reload |
| 13 | production, **2026-08-11**, read-only | `Restart=no`, `TriggeredBy=`, `BindsTo=`, `OnFailure=`, `DropInPaths=` empty, `WatchdogUSec=0`, `UnitFileState=enabled`; reverse dependencies are `multi-user.target` → `graphical.target` only |
| 14 | production, **2026-08-11**, read-only | 14 timers and 6 path units, **none** referencing Caddy or the endpoint |
| 15 | production, **2026-08-11**, read-only | no second proxy or tunnel process; no Docker, Podman, supervisord, monit or runit; no user crontab; `/etc/cron.d` holds `e2scrub_all` and `sysstat`; `at` not installed |
| 16 | production, **2026-08-11**, read-only | a loopback listener on `127.0.0.1:2019` — Caddy's documented default admin endpoint — while Caddy runs |
| 17 | production, **2026-08-11**, read-only | **LXD is installed** (snap), `snap.lxd.daemon.unix.socket` listening and `snap.lxd.daemon.service` socket-activated. Row 15's "no container runtime" read `docker` and `podman` only and **never looked at the one that is here** |
| 18 | production, **2026-08-11**, read-only | `/etc/crontab`, `/etc/cron.d/*` and `/etc/cron.{daily,weekly}` **read in full**: distribution jobs only, and no job's *contents* reference `caddy`, `snapshot_api`, or `systemctl start`/`restart` |
| 19 | production, **2026-08-11**, read-only | S-D.2's four readings exist and are stable across repeat calls — **and `NRestarts=0` alongside a non-zero `ActiveExitTimestampMonotonic`**, so a stop and a start had happened without the counter moving |
| 20 | production, **2026-08-11**, read-only | `command -v` with several operands exits **`0` when at least one name is found** in `bash` 5.2.21 and in `dash`, and `1` only when all are absent — so row 15's aggregated form printed both LXD paths and produced no false "no container runtime". The per-name loop that replaces it names `lxc` and `lxd` explicitly |
| 21 | this repository, **2026-08-11** | S-D.2's commit-watermark statements compiled against `adapters/database/tables.py` for the PostgreSQL dialect: `foundry_snapshots.received_at`, `audit_events.occurred_at` and `audit_events.entity_type` all exist. **Compiled, not executed** — no database was contacted |
| 22 | disposable `freedom_test`, **2026-08-11**, executed | `LOCK TABLE foundry_snapshots, audit_events IN SHARE MODE` **blocks the real submission service rather than refusing it**: the backend appears as an ungranted `RowExclusiveLock` on `foundry_snapshots` in S-D.3's own `pg_locks` query, the watermark cannot move while it waits, and the submission commits **immediately** on `COMMIT` — the ninth finding, reproduced |
| 23 | disposable `freedom_test`, **2026-08-11**, executed | a second `LOCK TABLE … IN SHARE MODE` is granted **only behind** the writer that was queued: with that writer holding its transaction open after its `INSERT`, the second request is observed **ungranted** from a third session, and the watermark read once granted includes that writer's commit. This is what S-D.4's drain read rests on |
| 24 | disposable `freedom_test`, **2026-08-11**, executed | **`pg_stat_activity` is snapshotted per transaction and `pg_locks` is not.** Inside one settlement transaction, a queue reading joined to `pg_stat_activity` returned **nothing** while `pg_locks` alone showed the waiter, because that backend connected after the transaction's first statistics read; `pg_stat_clear_snapshot()` restored the join. S-D.4's decisive reading is over `pg_locks` alone because of this row |
| 25 | disposable `freedom_test`, **2026-08-11**, executed | a bounded `idle_in_transaction_session_timeout` **ends the platform-wide pause**: the settlement session is terminated, the queued writer commits, and the settlement transaction is gone — so its `COMMIT` cannot succeed, which §9 classifies as Unsettled |

Results 1 and 2 are each other's control, and **as originally written this note
overclaimed how**. It said the two tests were one episode with one line of
difference, and that deleting `proxy.terminate()` made the second fail at
`assert not proxy.dialled`. They were two hand-written copies whose sequences
diverged after the endpoint stop, and the deletion blocked at the `proxy.join()`
on the next line instead — the named assertion was never reached, and the mutation
had not been run. The pair was rebuilt on a shared scenario on 2026-08-11, the
mutation executed, and it now fails exactly where this note said it would; see the
[fifth remediation](phase-2-b-1-settlement-remediation.md#b-1-fifth-remediation--the-evidence-for-s-i3-the-mutation-that-was-never-run-and-the-outcomes-that-never-came-back-up).

Rows 22–25 were added on 2026-08-11 with the ninth remediation, and they are the
first rows here obtained from a **database**. Every one of them was taken against
the **disposable `freedom_test`** database over the Unix-domain socket, through
`tests/conftest.py`'s existing two-layer disposability guard, by
`tests/test_snapshot_settlement_postgresql.py`. **No `LOCK TABLE` was executed
against `freedom`**, nothing on production was read or changed, and none of these
rows is a rehearsal of the operator procedure: they establish the PostgreSQL
behaviour S-D.3 and S-D.4 rest on, which is a different and smaller claim.

Rows 13–16 are the S-I.3 checks, added on 2026-08-11 because row 8 (`Restart=no`)
had been offered as evidence for S-I.3 and establishes far less than it claims.
They were read with **Caddy running** — restart *vectors* are readable in that
state — and **nothing was stopped, started, reloaded or reconfigured to obtain
them.** They are a snapshot of this host on that date, not a standing result: §9
makes the operator run the checks during the episode rather than cite this table.

## The rig

`Caddyfile.rig2` -- the retired route and the recovery route together:

```caddyfile
{
	admin off
	auto_https off
	http_port 9080
}

:9080 {
	# The retired route, stated explicitly rather than left to fall through.
	handle /api/v1/foundry/snapshots {
		respond 410
	}

	# Step 4's recovery route.
	handle /recovery/9f3c21/api/v1/foundry/snapshots {
		request_body {
			max_size 64MiB
		}
		uri strip_prefix /recovery/9f3c21
		reverse_proxy 127.0.0.1:8757 {
			transport http {
				read_timeout 180s
				write_timeout 60s
			}
		}
	}
}
```

The stub upstream records the exact path Caddy delivers and answers `201`:

```python
"""A stub upstream that records the exact request path Caddy delivers.

Deliberately not the real snapshot endpoint: every claim under test here is
about Caddy and the route configuration, not about the application. The stub
answers 201 and appends one line per request to a log, so "what path arrived"
and "did anything arrive at all" are both observable.
"""
import http.server
import sys

LOG = sys.argv[2]


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        with open(LOG, "a") as handle:
            handle.write(f"ARRIVED path={self.path} bytes={length}\n")
        body = b'{"ok":true}'
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        return


http.server.HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
```

## The reproduction, and its control

This is result 1 and result 2. Run it twice: `keep` leaves the proxy running,
`terminate` stops it between the endpoint stop and the restart.

```python
"""Does a real Caddy hold a request it has accepted but not dialled upstream for?

That is the whole of B-1's fourth finding, and it has only ever been argued.
Here it is exercised against Caddy 2.10.2:

1. a client opens a connection and sends a partial request -- everything but the
   header terminator, so Caddy has accepted it and cannot yet have routed it;
2. the upstream endpoint is stopped (S-A satisfied: no process, unserved port);
3. the upstream is restarted, which is what step 4 does;
4. the client completes the request.

If the upstream then records an arrival, a request survived the down window
inside the proxy and committed after the restart -- the false miss, reproduced.
The second run repeats it with Caddy terminated between 2 and 3, which is S-I.
"""
import socket
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
PYTHON = "/opt/discord-bots/freedom-bot/venv/bin/python"
LOG = HERE / "arrivals.log"
BODY = b'{"held":"episode"}'
PATH = "/recovery/9f3c21/api/v1/foundry/snapshots"


def arrivals() -> int:
    return len(LOG.read_text().splitlines())


def start_upstream() -> subprocess.Popen:
    process = subprocess.Popen(
        [PYTHON, str(HERE / "upstream.py"), "8757", str(LOG)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.0)
    return process


def upstream_connections() -> str:
    out = subprocess.run(
        ["ss", "-tn", "state", "established", "( dport = :8757 )"],
        capture_output=True, text=True,
    ).stdout.strip().splitlines()
    return "\n".join(out[1:]) if len(out) > 1 else "(none)"


def partial_request(client: socket.socket) -> None:
    """Everything except the header terminator: a request Caddy cannot route."""
    client.sendall(
        f"POST {PATH} HTTP/1.1\r\n"
        "Host: 127.0.0.1:9080\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(BODY)}\r\n".encode("ascii")
    )


def finish_request(client: socket.socket) -> None:
    client.sendall(b"\r\n" + BODY)


def run(terminate_caddy: bool) -> None:
    label = "S-I: endpoint AND proxy stopped" if terminate_caddy else \
            "C-15: endpoint stopped only"
    print(f"\n=== {label} ===")

    upstream = start_upstream()
    before = arrivals()

    client = socket.create_connection(("127.0.0.1", 9080), timeout=10)
    partial_request(client)
    time.sleep(1.0)
    print(f"  request held by Caddy, unterminated headers")
    print(f"  caddy -> upstream connections: {upstream_connections()}")
    print(f"  upstream arrivals: {arrivals() - before}")

    # S-A: the endpoint stops and stays down through the (hypothetical) query.
    upstream.terminate()
    upstream.wait(10)
    print("  endpoint stopped")

    if terminate_caddy:
        subprocess.run(["pkill", "-f", "Caddyfile.rig"], check=False)
        time.sleep(1.5)
        alive = subprocess.run(
            ["pgrep", "-f", "Caddyfile.rig"], capture_output=True, text=True
        ).stdout.strip()
        print(f"  caddy terminated; surviving processes: {alive or '(none)'}")

    # Step 4: the endpoint comes back.
    upstream = start_upstream()
    print("  endpoint restarted")

    # …and only now does the client finish what it was sending.
    try:
        finish_request(client)
        client.settimeout(10)
        answer = client.recv(200)
        print(f"  client got: {answer[:40]!r}")
    except OSError as error:
        print(f"  client could not finish: {type(error).__name__}: {error}")
    finally:
        client.close()

    time.sleep(1.0)
    delivered = arrivals() - before
    print(f"  >>> upstream arrivals after the restart: {delivered}")
    print(f"  >>> {'DELIVERED ACROSS THE DOWN WINDOW' if delivered else 'nothing arrived'}")

    upstream.terminate()
    upstream.wait(10)


if __name__ == "__main__":
    run(terminate_caddy=sys.argv[1] == "terminate")
```

## The production stop, with a request held open

Result 11. The held connection is made **directly to the origin's own listener**
with SNI set, not through Cloudflare: what is being measured is this Caddy's
shutdown.

```python
"""The production stop, with a request genuinely held open.

The two measurements taken so far are each half the picture: the isolated rig
with one request held open (5.4 s), and production with nothing in flight (4 ms).
A lost-pin reconciliation is the held-request case, so this is the number that
actually applies to the procedure.

The held connection is made **directly to the origin's own listener** on
127.0.0.1:443 with SNI set, not through Cloudflare -- what is being measured is
this Caddy's shutdown, and a hop in front would only add noise. TLS verification
is off because the origin certificate is a Cloudflare origin cert and is not
meant to validate here; nothing about trust is under test.

The request is deliberately incomplete: headers without the terminating blank
line, so Caddy has accepted the connection and completed the handshake but has
not routed the request or dialled anything upstream. That is exactly the state
S-I exists to dispose of.

Run as: sudo python3 verify_si_held.py
"""
import socket
import ssl
import subprocess
import time
from pathlib import Path

HOST = "foundry1.rpgworld.org"
LOG = Path(__file__).parent / "si-production-held.log"
DEADLINE = 60.0

lines = []


def say(text=""):
    print(text, flush=True)
    lines.append(text)
    LOG.write_text("\n".join(lines) + "\n")


def sh(*command):
    return subprocess.run(command, capture_output=True, text=True).stdout.strip()


def caddy_running():
    return subprocess.run(["pgrep", "-x", "caddy"], capture_output=True).returncode == 0


def tcp_listeners():
    out = sh("ss", "-ltn", "( sport = :80 or sport = :443 )")
    return out.count("LISTEN")


def udp_listeners():
    return sh("ss", "-lun", "( sport = :443 )").count(":443")


if sh("systemctl", "is-active", "caddy") != "active":
    say("caddy is not active: nothing to measure. Leaving it as found.")
    raise SystemExit(1)

say("=== before ===")
say(f"caddy pids:       {sh('pgrep', '-d,', '-x', 'caddy') or 'none'}")
say(f"tcp listeners:    {tcp_listeners()}")
say(f"udp :443:         {udp_listeners()}")
say(f"foundry sessions: {sh('bash', '-c', 'ss -tn state established | grep -cE :3000[123]')}")
say()

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
raw = socket.create_connection(("127.0.0.1", 443), timeout=15)
held = context.wrap_socket(raw, server_hostname=HOST)
held.sendall(
    f"POST /api/v1/foundry/snapshots HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Content-Type: application/json\r\n"
    f"Content-Length: 18\r\n".encode("ascii")
)
time.sleep(1.0)

say("=== one request held open, accepted and unrouted ===")
say(f"tls established:  {held.version()}")
established = sh("bash", "-c", "ss -tn state established '( sport = :443 )' | grep -c ':443'")
say(f"conns on :443:    {established}")
say()

restored = False
try:
    say(f"=== stopping caddy at {time.strftime('%H:%M:%S')} UTC ===")
    started = time.monotonic()
    stopping = subprocess.Popen(["systemctl", "stop", "caddy"])

    process_gone = tcp_gone = udp_gone = None
    while time.monotonic() - started < DEADLINE:
        now = time.monotonic() - started
        if process_gone is None and not caddy_running():
            process_gone = now
            say(f"  S-I.1 process gone at   {now:7.3f}s")
        if tcp_gone is None and tcp_listeners() == 0:
            tcp_gone = now
            say(f"  S-I.2 tcp listeners at  {now:7.3f}s")
        if udp_gone is None and udp_listeners() == 0:
            udp_gone = now
            say(f"  S-I.2 udp :443 gone at  {now:7.3f}s")
        if None not in (process_gone, tcp_gone, udp_gone):
            break
        time.sleep(0.02)

    say()
    if process_gone is None:
        say(f"  *** process STILL RUNNING after {DEADLINE:.0f}s ***")
        say("  A stop that does not complete is an unsettled episode, not a slow one.")
    say(f"process gone:     {process_gone if process_gone is not None else 'never'}")
    say(f"tcp listeners:    {tcp_gone if tcp_gone is not None else 'never'}")
    say(f"udp :443 gone:    {udp_gone if udp_gone is not None else 'never'}")
    if process_gone is not None and tcp_gone is not None:
        say(f"gap S-I.2 -> S-I.1: {process_gone - tcp_gone:.3f}s")
    say(f"stop command returned: {stopping.poll() is not None}")
    say()

    say("=== the held request, after the stop ===")
    try:
        held.sendall(b"\r\n" + b'{"held":"episode"}')
        held.settimeout(10)
        answer = held.recv(80)
        say(f"  answer: {answer[:60]!r}")
    except OSError as error:
        say(f"  {type(error).__name__}: {error}")
finally:
    try:
        held.close()
    except OSError:
        pass
    say()
    say("--- restoring ---")
    subprocess.run(["systemctl", "start", "caddy"])
    for _ in range(100):
        if tcp_listeners() >= 2:
            break
        time.sleep(0.2)
    restored = True
    say(f"is-active:        {sh('systemctl', 'is-active', 'caddy')}")
    say(f"tcp listeners:    {tcp_listeners()}")
    say(f"udp :443:         {udp_listeners()}")
    say(f"restored:         {restored}")
```

Output:

```text
=== before ===
caddy pids:       2046845
tcp listeners:    2
udp :443:         1
foundry sessions: 0

=== one request held open, accepted and unrouted ===
tls established:  TLSv1.3
conns on :443:    1

=== stopping caddy at 23:07:23 UTC ===
  S-I.2 tcp listeners at    0.000s
  S-I.2 udp :443 gone at    0.000s
  S-I.1 process gone at     4.300s

process gone:     4.3003888060338795
tcp listeners:    0.0004995490307919681
udp :443 gone:    0.0004995490307919681
gap S-I.2 -> S-I.1: 4.300s
stop command returned: True

=== the held request, after the stop ===
  answer: b''

--- restoring ---
is-active:        active
tcp listeners:    2
udp :443:         1
restored:         True
```

## The production stop, and the edge

Results 7-10, from `verify_si.sh`. It records the before state, stops Caddy while
polling process and both socket tables at 100 ms, runs the S-I.4 check through
Cloudflare, and restarts from a `trap`.

The **first run of it measured nothing**: it ran against an already-stopped
service, so every interval read as zero, which looks like a result. It now
refuses to run unless the service is active, and the window was taken again.

The log below is the **second, valid** run. The void run's log is not preserved:
the script truncates its own log on each run, so the re-run overwrote it. That is
a flaw in the script rather than a decision, and it is stated here because a
discarded measurement is exactly the kind of thing a record should not quietly
lose. What it contained is described in
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md):
`is-active: inactive` and `caddy pids: none` in the "before" block, and every
interval reading as `.003s`.

```text
=== before ===
is-active:        active
caddy pids:       2041640
foundry sessions: 0
restart policy:   no

=== S-I: stopping caddy at 22:59:47 ===
  S-I.1 process gone at    .003748745s
  S-I.2 tcp listeners at   .003748745s
  S-I.2 udp :443 gone at   .003748745s

S-I.1 no caddy process:  yes
S-I.2 tcp :80/:443:      0 listeners
S-I.2 udp :443:          0 listeners
S-I.3 is-active:         inactive
S-I.3 Restart=:          no

=== S-I.4: through Cloudflare, from off the origin's own listener ===
submission path: 521 
site root:       521 

down window ends at 22:59:47

--- restoring ---
is-active:        active
tcp listeners:    2
udp :443:         1
foundry sessions: 0
restored at 22:59:47
```

## Step 4 phase 1, against the production Caddy

Result 12, from `verify_step4.sh`: back up and verify the backup predates the
change, append a **loopback-only** site block, `caddy validate`, reload, check the
three Foundry sites, check the two claims, revert from a `trap`. No public site
block was edited and no internet-reachable route was added.

```text
=== before ===
endpoint on :8757: yes
foundry1 public:   302
foundry2 public:   302
foundry3 public:   302

backup taken:      /etc/caddy/Caddyfile.pre-step4-2026-08-10 (verified free of the change)
caddy validate:    ok
reload:            done, caddy active

=== the three sites, after the reload ===
  foundry1.rpgworld.org: 302
  foundry3.rpgworld.org: 302
  foundry2.rpgworld.org: 302

=== step 4's two claims ===
retired path:      410   (want 410; 401 = it still reaches the app; 200 = deleted not replaced)
recovery path:     401   (want 401, endpoint up=yes)

RESULT: as documented.

--- reverting ---
reverted and reloaded
caddy:            active
loopback :9080:   000ERR (expect 000/ERR: the block is gone)
foundry1 public:  302
```

## The S-I.3 checks, 2026-08-11

Read-only, with Caddy running. Rows 13–16.

```text
$ systemctl show caddy -p Restart -p RestartSec -p UnitFileState \
    -p TriggeredBy -p Requires -p Wants -p BindsTo
Restart=no
Requires=-.mount system.slice network-online.target sysinit.target
Wants=tmp.mount
BindsTo=
TriggeredBy=
UnitFileState=enabled

$ systemctl show caddy -p DropInPaths -p WatchdogUSec -p OnFailure -p FragmentPath
WatchdogUSec=0
OnFailure=
FragmentPath=/usr/lib/systemd/system/caddy.service
DropInPaths=

$ systemctl list-dependencies --reverse caddy.service
caddy.service
● └─multi-user.target
●   └─graphical.target
```

`TriggeredBy=` empty is the one that matters most and the one `Restart=no` never
addressed: **there is no `caddy.socket`**, so nothing activates the unit when a
connection arrives at a port it used to hold. `WatchdogUSec=0` and an empty
`OnFailure=` and `DropInPaths=` close the other unit-level vectors.
`UnitFileState=enabled` is the reboot vector, and it is not closable — §9 says so.

```text
$ systemctl list-units --type=socket --all --no-legend --no-pager
… 25 units: apport-forward, cloud-init-hotplugd, dbus, dm-event, iscsid,
  lvm2-lvmpolld, lxd-installer, multipathd, snap.lxd.daemon.unix,
  snap.lxd.user-daemon, snapd, ssh, syslog, systemd-fsckd, systemd-initctl,
  systemd-journald{,-audit,-dev-log}, systemd-networkd, systemd-pcrextend,
  systemd-rfkill, systemd-sysext, systemd-udevd-{control,kernel}, uuidd
  → no caddy.socket, and none of these fronts :80, :443 or :8757

$ systemctl list-timers --all --no-pager       # 14 timers
apt-daily-upgrade, apt-daily, man-db, update-notifier-download,
systemd-tmpfiles-clean, motd-news, dpkg-db-backup, logrotate, e2scrub_all,
fstrim, update-notifier-motd, apport-autoreport, snapd.snap-repair, ua-timer
  → none references caddy or snapshot_api

$ systemctl list-units --type=path --all --no-pager      # 6 path units
apport-autoreport, systemd-ask-password-{console,plymouth,wall}, tpm-udev,
whoopsie (not-found)
  → none references caddy or snapshot_api
```

```text
$ ps -eo pid,user,comm,args --no-headers \
    | grep -Ei 'nginx|haproxy|apache2|httpd|traefik|envoy|cloudflared|ngrok|frpc|socat|stunnel|tailscale|\bssh .*-[LRD]'
(none)

$ docker ps -a          → docker: not installed
$ podman ps -a          → podman: not installed
$ supervisorctl status  → supervisord: not installed
$ monit summary         → monit: not installed
$ crontab -l            → no crontab for foundry
$ ls /etc/cron.d/       → e2scrub_all  sysstat
$ atq                   → at: not installed

$ ss -ltnup      # abridged to the rows S-I.3c is about
tcp LISTEN 127.0.0.1:2019   users:(…)        # Caddy admin API
tcp LISTEN 127.0.0.1:5432                    # PostgreSQL
tcp LISTEN 0.0.0.0:22
tcp LISTEN *:443
udp UNCONN *:443                             # HTTP/3, and row 9's point
```

## The bounded S-I.3d inventory, 2026-08-11

Read-only, second session, with Caddy running. Rows 17–18. This is the check the
sixth review required: sources read **in full** rather than listed, bounded by
[topology §1](../operations/topology.md)'s component table.

```text
$ command -v docker podman lxc lxd nerdctl containerd
/usr/sbin/lxc                     ← and nothing else

$ systemctl list-units --all --no-pager | grep -Ei 'lxd|lxc'
snap.lxd.activate.service        loaded inactive dead      Service for snap application lxd.activate
snap.lxd.daemon.service          loaded inactive dead      Service for snap application lxd.daemon
snap.lxd.user-daemon.service     loaded inactive dead      Service for snap application lxd.user-daemon
lxd-installer.socket             loaded active  listening  Helper to install lxd snap on demand
snap.lxd.daemon.unix.socket      loaded active  listening  Socket unix for snap application lxd.daemon
snap-lxd-40115.mount             loaded active  mounted
snap-lxd-40338.mount             loaded active  mounted

$ lxc list --format compact
Error: LXD unix socket "/var/snap/lxd/common/lxd/unix.socket" not accessible: permission denied

$ getent group lxd
lxd:x:120:                        ← no members; reading it needs root
$ id
uid=1000(foundry) … groups=1000(foundry),27(sudo),100(users)
```

**Row 17 is the finding.** The previous check ran `docker ps -a` and `podman ps -a`,
got "not installed" from both, and recorded *"no Docker, Podman, supervisord, monit
or runit"*. Every word of that is true. It is also silent about **the one container
runtime this host has**, because the check was a list of names somebody thought of
rather than an inventory bounded by anything. `snap.lxd.daemon.service` is dead but
**socket-activated** — the same vector S-I.3a names for `caddy.socket` — and
`snap.lxd.activate.service` is what starts `boot.autostart` instances at boot.

Whether LXD holds any instance at all is **unread**: `lxc list` needs `root` or
membership of the `lxd` group, which has no members. Under §9's rule that is
**Unsettled**, not a pass.

```text
$ cat /etc/crontab                    → distribution header, four run-parts lines
$ cat /etc/cron.d/e2scrub_all         → e2scrub_all_cron; /sbin/e2scrub_all -A -r
$ cat /etc/cron.d/sysstat             → debian-sa1 1 1; debian-sa1 60 2
$ for d in hourly daily weekly monthly; do run-parts --list /etc/cron.$d; done
  hourly  → (empty)
  daily   → apport apt-compat dpkg logrotate man-db sysstat
  weekly  → man-db
  monthly → (empty)
$ grep -rniE 'caddy|snapshot_api|systemctl (start|restart)' \
    /etc/crontab /etc/cron.d /etc/cron.hourly /etc/cron.daily \
    /etc/cron.weekly /etc/cron.monthly
  (no match)

$ command -v supervisord supervisorctl monit runsv s6-svscan  → none installed
$ command -v atq                                              → at not installed
$ crontab -l                                                  → no crontab for foundry
$ loginctl list-users                                         → 1000 foundry, LINGER no
```

Row 18 is the difference between `ls -la /etc/cron.d/` and this: the earlier
listing produced two names, and the sixth review's point was that a name is not a
job. The names were in fact benign — but that is a fact established here, by
reading them, and not by the listing that was offered as evidence for it.

**`run-parts --list` takes one directory per call.** The first draft of the §9
command passed four and it fails with `missing operand`; §9 now loops. That is the
fifth documented case of a §9 command being wrong until it was run.

### S-D.2's readings, and the one that does not do what it looks like it does

```text
$ systemctl show caddy -p InvocationID -p NRestarts \
    -p ActiveEnterTimestampMonotonic -p ActiveExitTimestampMonotonic
NRestarts=0
ActiveEnterTimestampMonotonic=300753623280
ActiveExitTimestampMonotonic=300749250429
InvocationID=7d8b04f15c454181a4ddc73f4ea3a0a6

$ # …repeated immediately: identical in every field.
```

Row 19, and it is the **sixth** case of this package claiming something the host
then contradicted. The first draft of S-D.2 offered `NRestarts` as one of the
readings that catches a mid-episode restart. It does not: it counts restarts
performed by the unit's own `Restart=` logic, and this unit is `Restart=no`. The
host says so directly — `NRestarts=0` sitting next to a **non-zero**
`ActiveExitTimestampMonotonic`, which is the 2026-08-10 authorized stop and the
start after it. The counter did not move for a real stop and a real start.

A `systemctl start` issued by cron, by a supervisor or by a second operator is
exactly that shape, so `NRestarts` would have been silent for the case S-D.2
exists to catch. §9 now says this in the check itself and leans on `InvocationID`,
which is minted fresh on every start regardless of who asked for it.

**What row 19 does not establish** is that the comparison catches a restart. That
needs a real down window at both ends, and none has been run since S-D.2 was
written. All that is established is that the readings exist, are stable when
nothing happens, and that one of the four is weaker than it looks.

### `command -v` with several operands, measured rather than assumed

Row 20. The re-review of C-20 held that `command -v` "fails if any requested
command is absent — even if it printed paths for commands that are installed", so
an installed `lxc` could be followed by `no container runtime`. Run on this host:

```text
$ bash -c 'command -v bash nope1; echo "exit=$?"'
/usr/bin/bash
exit=0
$ bash -c 'command -v nope1 nope2; echo "exit=$?"'
exit=1
$ dash -c 'command -v bash nope1; echo "dash mixed exit=$?"'
/usr/bin/bash
dash mixed exit=0
```

`bash` 5.2.21 and `dash` both succeed when **at least one** name is found, so the
inverted conclusion the finding describes did not occur, and row 15's line printed
both LXD paths with no `no container runtime` after them. **The finding's remedy is
adopted anyway**, on two grounds this measurement does not touch: POSIX defines
`command -v` for a single `command_name`, so the exit status of the multi-operand
form is an extension and §9 does not control the operator's shell; and the
aggregated output answers six names with however many paths, which is the reading
that let row 15's LXD gap stand in the first place. The replacement:

```text
$ for c in docker podman lxc lxd nerdctl containerd; do
      if p=$(command -v "$c"); then echo "present $c $p"; else echo "absent  $c"; fi
  done
absent  docker
absent  podman
present lxc /usr/sbin/lxc
present lxd /usr/sbin/lxd
absent  nerdctl
absent  containerd
```

The supervisor loop returns `absent` for all five. This is C-19's row 15 finding
stated by the command rather than by a reader who happened to look.

### The commit watermark's columns, compiled and not executed

Row 21. S-D.2's third reading is a claim about the database, so the columns it
names were checked against the schema the application actually defines — the two
statements were built over `adapters/database/tables.py`'s metadata and compiled
for the PostgreSQL dialect, which resolves `foundry_snapshots.received_at`,
`audit_events.occurred_at` and `audit_events.entity_type` or fails.

**No database was contacted, and nothing here establishes what the statements
return against real data.** `tests/test_snapshot_recovery_documentation.py` holds
the standing form of this check, including that the entity type and both action
names in §9's prose are the constants the submission service writes — so a rename
fails the suite instead of silently emptying the query.

### What these checks did not establish

**Neither session had passwordless `sudo`:**

```text
$ sudo -n true
sudo: a password is required
```

So `ss -ltnup` could not attribute the **root-owned** listeners (`:80`, `:443`,
`:22`, `:5432`) to processes, and **root's crontab was not read**. Row 16 names the
`:2019` listener as Caddy's admin endpoint from the port and Caddy's documentation,
**not** from process attribution.

The second session adds three more unread readings, all for the same reason:
**LXD's instance list and their `boot.autostart` flags**, `/var/spool/cron/crontabs/`
(permission denied, so *who has a crontab* is itself unknown), and the other users'
crontabs and per-user systemd managers.

Under §9's rule none of that is a partial pass — it is **Unsettled**, and it is the
first worked example in this package of an operator reaching that outcome for a
reason other than a process still running. An operator with `sudo` should run these
commands once outside an episode and record the result, so that the first time they
are read is not under time pressure. **LXD in particular should be read before the
next review**, because it is the only unread item that is known to exist rather than
merely possible.

## What none of this establishes

- an operator following §9 under time pressure;
- step 4's retirement inside a **public** site block, where the fall-through would
  reach Foundry rather than the rig's empty `200`. That is phase 2 of
  [`phase-2-step-4-retirement-validation-plan.md`](phase-2-step-4-retirement-validation-plan.md),
  which re-creates the exposure reverted on 2026-08-09 and is not run;
- anything about settlement itself. These are observations about a proxy, a
  socket and a route. The settlement rule is in §9;
- **the privileged half of S-I.3c and S-I.3d**, which neither session could read —
  and which now includes **LXD's instance list**, a runtime known to be installed;
- **S-D.2's closing comparison**, added 2026-08-11. It has never been run: taking
  it requires a real down window at both ends, and no episode has been run since
  it was written. What is established is only that the readings it compares exist
  and are stable while Caddy runs — `InvocationID`, `NRestarts`,
  `ActiveEnterTimestampMonotonic` — not that the comparison catches a restart,
  which is the claim that matters and is **not** made here. The **commit
  watermark** added the same day is in the same position and one step further back:
  row 21 establishes that its columns exist, and nothing here establishes that the
  statements return what they should against real data, because no database was
  contacted. What *is* established, in the suite rather than on this host, is the
  counterexample it exists for — an ingress that is not `caddy.service`, serving
  and committing entirely between the two readings, with every Caddy figure and
  both listener samples identical across the window;
- **step 4's hit and unresolved restoration branches**, added 2026-08-11. Neither
  has been followed by an operator, and neither branch's off-host check — the hit
  branch's `401`, the unresolved branch's `410` — has been run in the configuration
  that branch describes. Row 12 exercised the same `410`/`401` pair on the
  production config, validate and reload path, which is the closest thing to it.
