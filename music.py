# music.py
# Pycord + Wavelink 3.x + Lavalink v4
# Now with YouTube playlist support via yt-dlp.

import os
import asyncio
import logging
import subprocess
from typing import Optional, Tuple, List

import discord
import wavelink
from discord.commands import Option

LAVALINK_HOST = os.getenv("LAVALINK_HOST", "127.0.0.1")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "2333"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "change-me")

# ---------- small helpers ----------

def _is_url(s: str) -> bool:
    return s.startswith(("http://", "https://"))

def _is_youtube_url(s: str) -> bool:
    s = s.lower()
    return ("youtube.com" in s) or ("youtu.be" in s)

def _is_youtube_playlist_url(url: str) -> bool:
    """Treat as playlist only for explicit /playlist URLs or list= without v= param."""
    if not _is_youtube_url(url):
        return False
    u = url.lower()
    if "youtube.com/playlist" in u:
        return True
    # If the URL has a list= param but no v=, it's a pure playlist link.
    if "list=" in u and "v=" not in u:
        return True
    return False

def _run_cmd(cmd: List[str], timeout: int = 40) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
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
    # Titles for each entry (one per line, in order)
    c1, titles_out, err1 = _run_cmd(
        ["yt-dlp", "--yes-playlist", "-I", f"1:{max_items}", "--get-title", url],
        timeout=120,
    )
    if c1 != 0 or not titles_out:
        logging.warning("yt-dlp playlist titles failed: %s", err1)
        titles: List[Optional[str]] = []
    else:
        titles = [ln.strip() for ln in titles_out.splitlines() if ln.strip()]

    # Direct audio urls for each entry (one per line, in order)
    c2, urls_out, err2 = _run_cmd(
        ["yt-dlp", "-f", "bestaudio", "--yes-playlist", "-I", f"1:{max_items}", "-g", url],
        timeout=180,
    )
    if c2 != 0 or not urls_out:
        logging.warning("yt-dlp playlist urls failed: %s", err2)
        return []

    urls = [ln.strip() for ln in urls_out.splitlines() if ln.strip()]

    # Pair them up by index. If lengths mismatch, pair what we can.
    n = min(len(urls), len(titles) if titles else len(urls))
    out: List[Tuple[str, Optional[str]]] = []
    for i in range(n):
        t = titles[i] if i < len(titles) and titles else None
        out.append((urls[i], t))

    # If we had URLs but no titles at all, still return urls with None titles.
    if not out and urls:
        out = [(u, None) for u in urls[:max_items]]

    return out

# ---------- player ----------

class MusicPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = wavelink.Queue()

# ---------- entry point ----------

def attach_music(bot: discord.Bot, guild_ids: list[int] | None = None) -> None:
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
            logging.info("Wavelink node ready (resumed=%s, session=%s)",
                         getattr(payload, "resumed", None),
                         getattr(payload, "session_id", None))
        except Exception:
            logging.info("Wavelink node ready.")

    bot.add_listener(_on_node_ready, "on_wavelink_node_ready")

    async def _on_track_end(payload: wavelink.TrackEndEventPayload):
        # player kann None sein (z. B. bei stop/replaced/disconnect)
        player = getattr(payload, "player", None)
        if player is None:
            return

        # Nur weiterschalten, wenn der Track regulär zu Ende gespielt wurde
        reason = str(getattr(payload, "reason", "")).lower()
        if reason and reason != "finished":
            return

        q = getattr(player, "queue", None)
        if not q or q.is_empty:
            return

        try:
            nxt = q.get()
            await player.play(nxt)
        except Exception:
            logging.exception("Autoplay of next track failed")

    bot.add_listener(_on_track_end, "on_wavelink_track_end")

    # ---------- /play ----------
    @bot.slash_command(guild_ids=guild_ids, name="play", description="Play a URL/search. Playlists supported for YouTube.")
    async def play_command(
        ctx: discord.ApplicationContext,
        query: Option(str, "YouTube URL/playlist, other URL, or search text", required=True),
        max_items: Option(int, "Max songs to queue from a playlist (1-100)", required=False, default=25),
    ):
        # Ack early (yt-dlp may take a bit)
        try:
            await ctx.defer()
        except Exception:
            pass

        # Voice check
        vc = getattr(ctx.author, "voice", None)
        if not vc or not vc.channel:
            return await ctx.followup.send("Join a voice channel first.", ephemeral=True)

        # Connect or reuse
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
            try:
                await ctx.guild.change_voice_state(channel=vc.channel, self_deaf=True, self_mute=False)
            except Exception:
                pass

        items: List[wavelink.Track] = []
        titles_for_msg: List[str] = []

        try:
            # YouTube playlist?
            if _is_youtube_playlist_url(query):
                # clamp max_items
                max_items = max(1, min(int(max_items or 25), 100))
                pairs = await asyncio.to_thread(_yt_dlp_playlist, query, max_items)
                if not pairs:
                    return await ctx.followup.send("Couldn't load that playlist.")
                # Fetch tracks for each direct url
                for direct_url, title_hint in pairs:
                    tr = await wavelink.Pool.fetch_tracks(direct_url)
                    if isinstance(tr, list) and tr:
                        items.append(tr[0])
                        titles_for_msg.append(title_hint or getattr(tr[0], "title", None) or "Unknown")
                    elif isinstance(tr, wavelink.Track):
                        items.append(tr)
                        titles_for_msg.append(title_hint or getattr(tr, "title", None) or "Unknown")

                if not items:
                    return await ctx.followup.send("Playlist resolved, but no playable audio was found.")

                # Start + queue
                first = items[0]
                rest = items[1:]
                if player.playing:
                    for t in items:
                        player.queue.put(t)
                    return await ctx.followup.send(f"Queued **{len(items)}** tracks from the playlist. First in queue: **{titles_for_msg[0]}**")
                else:
                    await player.play(first)
                    for t in rest:
                        player.queue.put(t)
                    if rest:
                        return await ctx.followup.send(f"Now playing: **{titles_for_msg[0]}**  •  Queued **{len(rest)}** more from the playlist.")
                    else:
                        return await ctx.followup.send(f"Now playing: **{titles_for_msg[0]}**")

            # YouTube single (url or search): use yt-dlp
            if _is_youtube_url(query) or not _is_url(query):
                direct_url, title_hint = await asyncio.to_thread(_yt_dlp_single, query)
                if not direct_url:
                    return await ctx.followup.send("I couldn't resolve that YouTube input. Try another one.")
                tr = await wavelink.Pool.fetch_tracks(direct_url)
                if isinstance(tr, list) and tr:
                    items = [tr[0]]
                elif isinstance(tr, wavelink.Track):
                    items = [tr]
                title = title_hint or (getattr(items[0], "title", None) if items else None) or "Unknown track"
            else:
                # Non-YouTube URL
                tr = await wavelink.Pool.fetch_tracks(query)
                if isinstance(tr, list) and tr:
                    items = [tr[0]]
                elif isinstance(tr, wavelink.Track):
                    items = [tr]
                title = getattr(items[0], "title", None) if items else None
                title = title or "Unknown track"

            if not items:
                return await ctx.followup.send("No playable audio was found for that input.")

            if player.playing:
                player.queue.put(items[0])
                return await ctx.followup.send(f"Queued: **{title}**")
            else:
                await player.play(items[0])
                return await ctx.followup.send(f"Now playing: **{title}**")

        except Exception as e:
            logging.exception("Track/playlist load failed: %r", e)
            return await ctx.followup.send("Sorry, I couldn't load that.")

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
        await player.play(nxt)
        title = getattr(nxt, "title", None) or "Unknown track"
        await ctx.respond(f"Skipped. Now playing: **{title}**")

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