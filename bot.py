import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

print("TOKEN CHECK:", os.getenv("DISCORD_TOKEN"))
print("TEST:", os.getenv("TEST123"))

# ======================
# intents
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# queue
# ======================
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = []
    return queues[guild_id]

# ======================
# yt-dlp settings
# ======================
ydl_opts = {
    "format": "bestaudio",
    "quiet": True,
}

ffmpeg_opts = {
    "options": "-vn"
}

# ======================
# play next
# ======================
async def play_next(ctx):
    queue = get_queue(ctx.guild.id)

    if len(queue) == 0:
        return

    url = queue.pop(0)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_opts)

    def after_play(err):
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except:
            pass

    ctx.voice_client.play(source, after=after_play)

# ======================
# join voice
# ======================
async def join_vc(ctx):
    if ctx.author.voice is None:
        await ctx.send("❌ 你沒有在語音頻道")
        return False

    channel = ctx.author.voice.channel

    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

    return True

# ======================
# play command
# ======================
@bot.command()
async def play(ctx, url: str):
    ok = await join_vc(ctx)
    if not ok:
        return

    queue = get_queue(ctx.guild.id)
    queue.append(url)

    await ctx.send(f"🎵 已加入播放清單：{url}")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

# ======================
# skip
# ======================
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ 已跳過")

# ======================
# pause
# ======================
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ 已暫停")

# ======================
# resume
# ======================
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ 繼續播放")

# ======================
# stop
# ======================
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        queues[ctx.guild.id] = []
        await ctx.send("⏹ 已停止並清空隊列")

# ======================
# Spotify (safe optional)
# ======================
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials

    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

    spotify = None

    if client_id and client_secret:
        spotify = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
        print("Spotify enabled")
    else:
        print("Spotify not configured (ignored)")

except Exception as e:
    print("Spotify disabled:", e)

# ======================
# run bot
# ======================
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)