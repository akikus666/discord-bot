import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from collections import deque
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# MUSIC CONFIG
# =========================
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))
def spotify_search(query: str):
    try:
        res = spotify.search(q=query, type="track", limit=1)
        item = res["tracks"]["items"][0]

        title = item["name"]
        artist = item["artists"][0]["name"]

        return f"{title} {artist}"

    except:
        return query  # fallback

queues = {}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "ytsearch",
    "extract_flat": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    }
}

# =========================
# COUPLE SYSTEM
# =========================

start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# =========================
# QUEUE
# =========================

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]

# =========================
# PLAY NEXT
# =========================

async def play_next(guild_id, vc):
    queue = get_queue(guild_id)

    if not queue:
        return

    song = queue.popleft()

    try:
        source = discord.FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS)
        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
            play_next(guild_id, vc), bot.loop
        ))
    except Exception as e:
        print("play_next error:", e)

# =========================
# PLAY SONG
# =========================

async def play_song(interaction: discord.Interaction, query: str):

    if not interaction.user.voice:
        await interaction.followup.send("❌ 你要先進語音頻道", ephemeral=True)
        return

    channel = interaction.user.voice.channel

    vc = interaction.guild.voice_client

    if not vc:
        vc = await channel.connect(reconnect=True, timeout=60)

    await interaction.followup.send("🔍 搜尋中...")

    try:
        # Spotify 增強搜尋
        search_query = spotify_search(query)

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(search_query, download=False)

            if "entries" in info:
                info = info["entries"][0]

            url = info.get("url")
            title = info.get("title", "Unknown")

            if not url:
                await interaction.channel.send("❌ 找不到音樂")
                return

    except Exception as e:
        await interaction.channel.send(f"❌ 播放失敗：{str(e)[:200]}")
        return

    queue = get_queue(interaction.guild.id)
    queue.append({"url": url, "title": title})

    await interaction.channel.send(f"🎵 已加入：{title}")

    if not vc.is_playing():
        await play_next(interaction.guild.id, vc)

# =========================
# UI
# =========================

class MusicModal(discord.ui.Modal, title="搜尋音樂"):
    song = discord.ui.TextInput(label="歌曲名稱或連結")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await play_song(interaction, self.song.value)


class MusicView(discord.ui.View):

    @discord.ui.button(label="搜尋", style=discord.ButtonStyle.primary)
    async def search(self, interaction, button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
        await interaction.response.send_message("已暫停", ephemeral=True)

    @discord.ui.button(label="繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
        await interaction.response.send_message("已繼續", ephemeral=True)

    @discord.ui.button(label="跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
        await interaction.response.send_message("已跳過", ephemeral=True)

    @discord.ui.button(label="離開", style=discord.ButtonStyle.danger)
    async def leave(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("已離開語音", ephemeral=True)

# =========================
# MAIN COMMAND
# =========================

@bot.tree.command(name="start")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        "主選單",
        view=MusicView(),
        ephemeral=True
    )

# =========================
# READY
# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"💖 Logged in as {bot.user}")

# =========================
# RUN
# =========================

bot.run(os.getenv("TOKEN"))