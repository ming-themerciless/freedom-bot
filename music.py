# music.py
# Pycord + Wavelink 3.x + Lavalink v4
# YouTube single + playlist support via yt-dlp; queue, back, skip, stop.

import os
import asyncio
import logging
import subprocess
from typing import Optional, Tuple, List, Any

import discord
import wavelink
from discord.commands import Option

# ---- Lavalink config (env overrideable) ----
LAVALINK_HOST = os.getenv("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "2333"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "change-me")

# ---- yt-dlp cookies (optional) ----
# Put a Netscape cookie file path here (e.g. ~/.config/yt-dlp/cookies.txt)
YTDLP_COOKIES_FILE = os.getenv("YTDLP_COOKIES_FILE")

# ---------- small helpers ----------

def _is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))

def _is_youtube_url(s: str) -> bool:
    s = s.lower()
    return ("youtube.com" in s) or ("youtu.be" in s)

def _is_youtube_playlist_url(url: str) -> bool:
    """
    Treat as playlist only for explicit /playlist URLs or list= **without** v=.
    (If both list= and v= are present, it's a single video within a playlist.)
    """
    if not _is_youtube_url(url):
        return False
    u = url.lower()
    if "youtube.com/playlist" in u:
        return True
    if "list=" in u and "v=" not in u:
        return True
    return False

def _run_cmd(cmd: List[str], timeout: int = 40) -> Tuple[int, str, str]:
    # Add cookies if configured
    full_cmd = list(cmd)
    if YTDLP_COOKIES_FILE and cmd and cmd[0] == "yt-dlp":
        full_cmd = ["yt-dlp", "--cookies", YTDLP_COOKIES_FILE, *cmd[1:]]
    proc = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout, check=False)
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()

def _yt_dlp_single(query_or_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Resolve a *single* YouTube video (by url or search) to (direct_audio_url, title).
    Returns (None, None) on failure.
    """
    target = query_or_url if _is_url(query_or_url) else f"ytsearch1:{query_or_url}"

    # Title
    c1, title_out, err1 = _run_cmd(["yt-dlp", "--no-playlist", "--get-title", target], timeout=40)
    if c1 != 0 or not title_out:
        logging.warning("yt-dlp title failed: %s", err1)
        title_out = None

    # Direct stream URL (bestaudio)
    c2, url_out, err2 = _run_cmd(["yt-dlp", "-f", "bestaudio", "--no-playlist", "-g", target], timeout=60)
    if c2 != 0 or not url_out:
        logging.warning("yt-dlp url failed: %s", err2)
        return None, title_out

    lines = [ln for ln in url_out.splitlines() if ln.strip()]
    direct_url = lines[-1] if lines else None
    return direct_url, title_out

def _yt_dlp_playlist(url: str, max_items: int = 50) -> List[Tuple[str, Optional[str]]]:
    """
    Resolve a YouTube PLAYLIST URL to a list of (direct_audio_url, title) for up to max_items.
    Returns [] on failure.
    """
    # Titles per entry
    c1, titles_out, err1 = _run_cmd(
        ["yt-dlp", "--yes-playlist", "-I", f"1:{max_items}", "--get-title", url],
        timeout=120,
    )
    if c1 != 0 or not titles_out:
        logging.warning("yt-dlp playlist titles failed: %s", err1)
        titles: List[Optional[str]] = []
    else:
        titles = [ln.strip() for ln in titles_out.splitlines() if ln.strip()]

    # Direct audio URLs per entry
    c2, urls_out, err2 = _run_cmd(
        ["yt-dlp", "-f", "bestaudio", "--yes-playlist", "-I", f"1:{max_items}", "-g", url],
        timeout=180,
    )
    if c2 != 0 or not urls_out:
        logging.warning("yt-dlp playlist urls failed: %s", err2)
        return []

    urls = [ln.strip() for ln in urls_out.splitlines() if ln.strip()]
    n = min(len(urls), len(titles) if titles else len(urls))

    out: List[Tuple[str, Optional[str]]] = []
    for i in range(n):
        t = titles[i] if (titles and i < len(titles)) else None
        out.append((urls[i], t))

    if not out and urls:
        out = [(u, None) for u in urls[:max_items]]
    return out

# ---------- player ----------

class MusicPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = wavelink.Queue()
        self.history: List[Any] = []
        self.current_track: Any | None = None

# ---------- entry point ----------

def attach_music(bot: discord.Bot, guild_ids: List[int] | None = None) -> None:
    def _track_title(t: Any) -> str:
        # Best-effort title getter
        title = getattr(t, "title", None)
        if title:
            return str(title)
        info = getattr(t, "info", None)
        if isinstance(info, dict):
            return str(info.get("title") or "Unknown title")
        return "Unknown title"

    async def _start_play(player: MusicPlayer, track: Any):
        if player.current_track is not None:
            player.history.append(player.current_track)
        await player.play(track)
        player.current_track = track

    async def _music_on_ready():
        try:
            if not wavelink.Pool.nodes:
                node = wavelink.Node(
                    uri=f"http://{LAVALINK_HOST}:{LAVALINK_PORT}",
                    password=LAVALINK_PASSWORD,
                    identifier="MAIN",
                    client=bot,
                )
                await wavelink.Pool.connect(nodes=[node], client=bot)
            logging.info("Lavalink node connected.")
        except Exception as e:
            logging.exception(f"Failed to connect Lavalink: {e}")

    bot.add_listener(_music_on_ready, "on_ready")

    async def _on_node_ready(payload: wavelink.NodeReadyEventPayload):
        try:
            logging.info(
                "Wavelink node ready (resumed=%s, session=%s)",
                getattr(payload, "resumed", None),
                getattr(payload, "session_id", None),
            )
        except Exception:
            logging.info("Wavelink node ready.")

    bot.add_listener(_on_node_ready, "on_wavelink_node_ready")

    async def _on_track_end(payload: wavelink.TrackEndEventPayload):
        player: MusicPlayer = payload.player  # type: ignore
        reason = str(getattr(payload, "reason", "")).lower()

        # Only auto-advance on natural finish
        if reason and reason != "finished":
            return

        q = getattr(player, "queue", None)
        if not q or q.is_empty:
            return

        try:
            nxt = q.get()
            await _start_play(player, nxt)
        except Exception:
            logging.exception("Autoplay of next track failed")

    bot.add_listener(_on_track_end, "on_wavelink_track_end")

    # ---------- /play ----------
    @bot.slash_command(
        guild_ids=guild_ids,
        name="play",
        description="Play a URL/search. YouTube playlists supported via yt-dlp.",
    )
    async def play_command(
        ctx: discord.ApplicationContext,
        query: Option(str, "YouTube URL/playlist, other URL, or search text", required=True),
        max_items: Option(int, "Max songs to queue from a playlist (1-100)", required=False, default=25),
    ):
        # Try to defer (yt-dlp can be slow); but don't die if it fails
        try:
            await ctx.defer()
        except Exception:
            pass

        # Helper to send regardless of whether we deferred successfully
        sender = ctx.followup.send if ctx.response.is_done() else ctx.respond

        # Voice check
        vc = getattr(ctx.author, "voice", None)
        if not vc or not vc.channel:
            return await sender("Join a voice channel first.", ephemeral=True)

        # Connect or reuse existing player
        player: MusicPlayer
        if ctx.voice_client and isinstance(ctx.voice_client, MusicPlayer):
            player = ctx.voice_client  # type: ignore
        else:
            try:
                player = await vc.channel.connect(cls=MusicPlayer)  # type: ignore
            except discord.ClientException:
                if ctx.voice_client:
                    await ctx.voice_client.disconnect(force=True)
                player = await vc.channel.connect(cls=MusicPlayer)  # type: ignore
            # best-effort self-deafen
            try:
                await ctx.guild.change_voice_state(channel=vc.channel, self_deaf=True, self_mute=False)
            except Exception:
                pass

        items: List[Any] = []
        titles_for_msg: List[str] = []

        try:
            # --- YouTube PLAYLIST (url) ---
            if _is_youtube_playlist_url(query):
                # Clamp max_items (1..100)
                max_items = max(1, min(int(max_items or 25), 100))

                # Resolve playlist to direct audio URLs (with title hints) via yt-dlp
                pairs = await asyncio.to_thread(_yt_dlp_playlist, query, max_items)
                if not pairs:
                    return await sender("Couldn't load that playlist.")

                # For each direct URL, fetch a Wavelink track
                for direct_url, title_hint in pairs:
                    fetched = await wavelink.Pool.fetch_tracks(direct_url)
                    if isinstance(fetched, wavelink.Playlist):
                        tracks = fetched.tracks or []
                    elif isinstance(fetched, list):
                        tracks = fetched
                    else:
                        tracks = []
                    if tracks:
                        t = tracks[0]
                        items.append(t)
                        titles_for_msg.append(title_hint or _track_title(t))

                if not items:
                    return await sender("Playlist resolved, but no playable audio was found.")

                # Start + queue while preserving history via _start_play
                first, rest = items[0], items[1:]
                if player.playing:
                    for t in items:
                        player.queue.put(t)
                    return await sender(
                        f"Queued **{len(items)}** tracks from the playlist. "
                        f"First in queue: **{titles_for_msg[0]}**"
                    )
                else:
                    await _start_play(player, first)
                    for t in rest:
                        player.queue.put(t)
                    if rest:
                        return await sender(
                            f"Now playing: **{titles_for_msg[0]}**  •  Queued **{len(rest)}** more from the playlist."
                        )
                    else:
                        return await sender(f"Now playing: **{titles_for_msg[0]}**")

            # --- YouTube SINGLE (url or plain search) via yt-dlp ---
            if _is_youtube_url(query) or not _is_url(query):
                direct_url, title_hint = await asyncio.to_thread(_yt_dlp_single, query)
                if not direct_url:
                    return await sender("I couldn't resolve that YouTube input. Try another one.")

                fetched = await wavelink.Pool.fetch_tracks(direct_url)
                if isinstance(fetched, wavelink.Playlist):
                    tracks = fetched.tracks or []
                elif isinstance(fetched, list):
                    tracks = fetched
                else:
                    tracks = []

                if not tracks:
                    return await sender("No playable audio was found for that input.")

                title = title_hint or _track_title(tracks[0])

                if player.playing:
                    player.queue.put(tracks[0])
                    return await sender(f"Queued: **{title}**")
                else:
                    await _start_play(player, tracks[0])
                    return await sender(f"Now playing: **{title}**")

            # --- Non-YouTube DIRECT URL (let Lavalink handle) ---
            fetched = await wavelink.Pool.fetch_tracks(query)
            if isinstance(fetched, wavelink.Playlist):
                tracks = fetched.tracks or []
            elif isinstance(fetched, list):
                tracks = fetched
            else:
                tracks = []

            if not tracks:
                return await sender("No playable audio was found for that input.")

            title = _track_title(tracks[0])

            if player.playing:
                player.queue.put(tracks[0])
                return await sender(f"Queued: **{title}**")
            else:
                await _start_play(player, tracks[0])
                return await sender(f"Now playing: **{title}**")

        except Exception as e:
            logging.exception("Track/playlist load failed: %r", e)
            return await sender("Sorry, I couldn't load that.")

    # ---------- /skip ----------
    @bot.slash_command(guild_ids=guild_ids, name="skip", description="Skip the current track.")
    async def skip_command(ctx: discord.ApplicationContext):
        if not ctx.voice_client or not isinstance(ctx.voice_client, MusicPlayer):
            return await ctx.respond("I'm not in a voice channel.", ephemeral=True)
        player: MusicPlayer = ctx.voice_client  # type: ignore

        if player.queue.is_empty:
            await player.stop()
            return await ctx.respond("Stopped (queue empty).")
        nxt = player.queue.get()
        await _start_play(player, nxt)
        await ctx.respond(f"Skipped. Now playing: **{_track_title(nxt)}**")

    # ---------- /back ----------
    @bot.slash_command(guild_ids=guild_ids, name="back", description="Go back to the previous track.")
    async def back_command(ctx: discord.ApplicationContext):
        if not ctx.voice_client or not isinstance(ctx.voice_client, MusicPlayer):
            return await ctx.respond("I'm not in a voice channel.", ephemeral=True)

        player: MusicPlayer = ctx.voice_client  # type: ignore
        if not player.history:
            return await ctx.respond("No previous track in history.", ephemeral=True)

        prev = player.history.pop()

        # Optional: re-queue the current one at the end so you can /skip forward to it
        if player.current_track is not None:
            try:
                player.queue.put(player.current_track)
            except Exception:
                pass

        await _start_play(player, prev)
        await ctx.respond(f"Back to: **{_track_title(prev)}**")

    # --- helpers for queue ops (no wavelink.Track annotations) ---
    def _queue_snapshot(q) -> List[Any]:
        """Return a list of upcoming items without mutating the queue."""
        # Try to read underlying deque if present (non-destructive).
        dq = getattr(q, "_queue", None)
        if dq is not None:
            try:
                return list(dq)
            except Exception:
                pass
        # Fallback: drain and restore (safe but a bit heavier).
        items: List[Any] = []
        try:
            while not q.is_empty:
                items.append(q.get())
        finally:
            for it in items:
                q.put(it)
        return items

    def _queue_rebuild(q, items: List[Any]) -> None:
        """Replace queue contents with given items."""
        # Drain everything
        drained: List[Any] = []
        try:
            while not q.is_empty:
                drained.append(q.get())
        except Exception:
            pass
        # Refill
        for it in items:
            q.put(it)

    # ---------- /queue ----------
    @bot.slash_command(guild_ids=guild_ids, name="queue", description="Show the upcoming queue.")
    async def queue_command(ctx: discord.ApplicationContext):
        if not ctx.voice_client or not isinstance(ctx.voice_client, MusicPlayer):
            return await ctx.respond("I'm not in a voice channel.", ephemeral=True)
        player: MusicPlayer = ctx.voice_client  # type: ignore

        upcoming = _queue_snapshot(player.queue)
        now = _track_title(player.current_track) if player.current_track else "(nothing)"
        if not upcoming:
            return await ctx.respond(f"**Now playing:** {now}\nQueue is empty.")

        lines = []
        for i, tr in enumerate(upcoming[:20], start=1):
            lines.append(f"{i}. **{_track_title(tr)}**")
        more = "" if len(upcoming) <= 20 else f"\n…and {len(upcoming)-20} more."
        txt = f"**Now playing:** {now}\n**Up next ({len(upcoming)}):**\n" + "\n".join(lines) + more
        await ctx.respond(txt)

    # ---------- /remove ----------
    @bot.slash_command(
        guild_ids=guild_ids,
        name="remove",
        description="Remove a song from the queue by its 1-based index (see /queue).",
    )
    async def remove_command(
        ctx: discord.ApplicationContext,
        index: Option(int, "1-based index in the upcoming queue", required=True),
    ):
        if not ctx.voice_client or not isinstance(ctx.voice_client, MusicPlayer):
            return await ctx.respond("I'm not in a voice channel.", ephemeral=True)
        player: MusicPlayer = ctx.voice_client  # type: ignore

        upcoming = _queue_snapshot(player.queue)
        if not upcoming:
            return await ctx.respond("Queue is empty.", ephemeral=True)

        if index < 1 or index > len(upcoming):
            return await ctx.respond(f"Index must be between 1 and {len(upcoming)}.", ephemeral=True)

        # Remove chosen item and rebuild
        removed = upcoming.pop(index - 1)
        _queue_rebuild(player.queue, upcoming)
        await ctx.respond(f"Removed **{_track_title(removed)}** from the queue.")

    # ---------- /stop ----------
    @bot.slash_command(guild_ids=guild_ids, name="stop", description="Stop and disconnect.")
    async def stop_command(ctx: discord.ApplicationContext):
        if not ctx.voice_client:
            return await ctx.respond("Not connected.", ephemeral=True)
        try:
            if isinstance(ctx.voice_client, MusicPlayer):
                await ctx.voice_client.stop()
        finally:
            await ctx.voice_client.disconnect(force=True)
        await ctx.respond("Disconnected.")