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

Results 1 and 2 are each other's control: one episode, one line of difference.
Deleting `proxy.terminate()` from the second makes it fail at
`assert not proxy.dialled`, where the proxy forwards across the restart.

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

## What none of this establishes

- an operator following §9 under time pressure;
- step 4's retirement inside a **public** site block, where the fall-through would
  reach Foundry rather than the rig's empty `200`. That is phase 2 of
  [`phase-2-step-4-retirement-validation-plan.md`](phase-2-step-4-retirement-validation-plan.md),
  which re-creates the exposure reverted on 2026-08-09 and is not run;
- anything about settlement itself. These are observations about a proxy, a
  socket and a route. The settlement rule is in §9.
