import discord
from discord.ext import commands
from datetime import datetime
import random
import yt_dlp
import os
import asyncio
from collections import deque

print("Bot starting...")

# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# COUPLE SYSTEM
# =========================

start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# =========================
# MUSIC SYSTEM
# =========================

queues = {}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0"
    },
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "web"]
        }
    }
}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]

async def play_next(guild_id, vc):
    queue = get_queue(guild_id)

    if len(queue) == 0:
        return

    song = queue.popleft()

    source = discord.FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS)

    def after(error):
        fut = asyncio.run_coroutine_threadsafe(
            play_next(guild_id, vc),
            bot.loop
        )
        try:
            fut.result()
        except:
            pass

    vc.play(source, after=after)

async def play_song(interaction: discord.Interaction, query: str):

    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("🎤 請先加入語音頻道")
        return

    channel = interaction.user.voice.channel

    vc = interaction.guild.voice_client

    # 🔥 修正 voice 4006 / reconnect
    if vc and vc.is_connected():
        await vc.move_to(channel)
    else:
        await asyncio.sleep(1)
        vc = await channel.connect(timeout=30, reconnect=True)

    await interaction.followup.send("🔍 搜尋中...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)

            if not info or "entries" not in info or len(info["entries"]) == 0:
                await interaction.followup.send("❌ 找不到音樂")
                return

            data = info["entries"][0]

    except Exception as e:
        await interaction.followup.send(f"❌ 播放失敗：{e}")
        return

    song = {
        "title": data.get("title", "Unknown"),
        "url": data["url"]
    }

    queue = get_queue(interaction.guild.id)
    queue.append(song)

    await interaction.followup.send(f"🎵 已加入：{song['title']}")

    if not vc.is_playing():
        await play_next(interaction.guild.id, vc)

# =========================
# MUSIC UI
# =========================

class MusicModal(discord.ui.Modal, title="搜尋音樂"):

    song = discord.ui.TextInput(label="輸入歌曲")

    async def on_submit(self, interaction: discord.Interaction):
        await play_song(interaction, self.song.value)

class MusicView(discord.ui.View):

    @discord.ui.button(label="🔍 搜尋播放", style=discord.ButtonStyle.primary)
    async def search(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="⏸ 暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
        await interaction.response.send_message("⏸ 已暫停", ephemeral=True)

    @discord.ui.button(label="▶ 繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
        await interaction.response.send_message("▶ 已繼續", ephemeral=True)

    @discord.ui.button(label="⏭ 跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
        await interaction.response.send_message("⏭ 已跳過", ephemeral=True)

    @discord.ui.button(label="👋 離開", style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("👋 已離開語音", ephemeral=True)

# =========================
# COUPLE UI
# =========================

class CoupleView(discord.ui.View):

    @discord.ui.button(label="💞 days", style=discord.ButtonStyle.primary)
    async def days(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"💞 在一起 {get_days()} 天")

    @discord.ui.button(label="💗 love", style=discord.ButtonStyle.primary)
    async def love(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💗 今天也想你")

    @discord.ui.button(label="🤗 hug", style=discord.ButtonStyle.primary)
    async def hug(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🤗 抱抱 💖")

    @discord.ui.button(label="🎵 音樂", style=discord.ButtonStyle.success)
    async def music(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "🎵 音樂系統",
            view=MusicView(),
            ephemeral=True
        )

# =========================
# MAIN MENU
# =========================

class MainView(discord.ui.View):

    @discord.ui.button(label="💞 情侶系統", style=discord.ButtonStyle.primary)
    async def couple(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💞 情侶系統", view=CoupleView(), ephemeral=True)

# =========================
# START COMMAND
# =========================

@bot.tree.command(name="start", description="開啟主選單")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message("📌 主選單", view=MainView(), ephemeral=True)

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