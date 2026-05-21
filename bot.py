import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from collections import defaultdict

# ======================
# ENV CHECK
# ======================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in Railway Variables")

print("BOT STARTING...")
print("TOKEN OK:", bool(TOKEN))
print("TEST:", os.getenv("TEST123"))

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# QUEUE
# ======================
queues = defaultdict(list)

# ======================
# YT-DLP SETTINGS
# ======================
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

# ======================
# PLAY NEXT
# ======================
async def play_next(ctx):
    if not ctx.voice_client:
        return

    queue = queues[ctx.guild.id]

    if not queue:
        return

    url = queue.pop(0)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info["url"]

        source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_opts)

    except Exception as e:
        print("ERROR extracting audio:", e)
        return await play_next(ctx)

    def after_play(err):
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except:
            pass

    ctx.voice_client.play(source, after=after_play)

# ======================
# JOIN VC
# ======================
async def join_vc(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ 你沒有在語音頻道")
        return False

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

    return True

# ======================
# PLAY
# ======================
@bot.command()
async def play(ctx, url: str):
    ok = await join_vc(ctx)
    if not ok:
        return

    queues[ctx.guild.id].append(url)

    await ctx.send(f"🎵 已加入播放清單")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

# ======================
# SKIP
# ======================
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ 已跳過")

# ======================
# PAUSE
# ======================
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ 已暫停")

# ======================
# RESUME
# ======================
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ 繼續播放")

# ======================
# STOP
# ======================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        queues[ctx.guild.id].clear()
        await ctx.send("⏹ 已停止並清空隊列")

# ======================
# OPTIONAL SPOTIFY (SAFE)
# ======================
spotify = None

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    cid = os.getenv("SPOTIPY_CLIENT_ID")
    secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    if cid and secret:
        spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=cid,
                client_secret=secret
            )
        )
        print("Spotify enabled")
    else:
        print("Spotify not configured (ignored)")

except Exception as e:
    print("Spotify disabled:", e)

# ======================
# START BOT
# ======================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set in Railway Variables")

bot.run(TOKEN)