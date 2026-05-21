import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio
from datetime import datetime
from collections import deque

# =========================
# BOT SETUP
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 💞 情侶系統
# =========================

start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days


# =========================
# 🎵 音樂系統
# =========================

queues = {}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -nostdin",
    "options": "-vn"
}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "extract_flat": False,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"]
        }
    }
}


def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]


async def play_next(guild_id, vc):
    queue = get_queue(guild_id)

    if not queue:
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

    if not interaction.user.voice:
        return await interaction.followup.send("🎤 請先加入語音頻道", ephemeral=True)

    channel = interaction.user.voice.channel

    vc = interaction.guild.voice_client

    try:
        if not vc:
            vc = await channel.connect(
                timeout=60,
                reconnect=True,
                self_deaf=True
            )
    except:
        vc = interaction.guild.voice_client

    await interaction.followup.send("🔍 搜尋中...")

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            video = info["entries"][0]

        song = {
            "title": video.get("title", "Unknown"),
            "url": video["url"]
        }

        queue = get_queue(interaction.guild.id)
        queue.append(song)

        await interaction.channel.send(f"🎵 已加入：{song['title']}")

        if not vc.is_playing():
            await play_next(interaction.guild.id, vc)

    except Exception as e:
        await interaction.channel.send(f"❌ 播放失敗：{e}")


# =========================
# 🎵 MUSIC UI
# =========================

class MusicModal(discord.ui.Modal, title="搜尋音樂"):

    song = discord.ui.TextInput(label="輸入歌曲")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await play_song(interaction, self.song.value)


class MusicView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔍 搜尋播放", style=discord.ButtonStyle.primary)
    async def search(self, interaction, button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="⏸ 暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
        await interaction.response.send_message("⏸ 已暫停", ephemeral=True)

    @discord.ui.button(label="▶ 繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
        await interaction.response.send_message("▶ 已繼續", ephemeral=True)

    @discord.ui.button(label="⏭ 跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
        await interaction.response.send_message("⏭ 已跳過", ephemeral=True)

    @discord.ui.button(label="👋 離開", style=discord.ButtonStyle.danger)
    async def leave(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("👋 已離開", ephemeral=True)


# =========================
# 💞 情侶 UI
# =========================

class CoupleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💞 天數", style=discord.ButtonStyle.primary)
    async def days(self, interaction, button):
        await interaction.response.send_message(f"💞 {get_days()} 天", ephemeral=True)

    @discord.ui.button(label="💗 想你", style=discord.ButtonStyle.primary)
    async def love(self, interaction, button):
        await interaction.response.send_message("💗 想你", ephemeral=True)

    @discord.ui.button(label="🤗 抱抱", style=discord.ButtonStyle.primary)
    async def hug(self, interaction, button):
        await interaction.response.send_message("🤗 抱抱", ephemeral=True)

    @discord.ui.button(label="🎵 音樂", style=discord.ButtonStyle.success)
    async def music(self, interaction, button):
        await interaction.response.send_message(
            "🎵 音樂系統",
            view=MusicView(),
            ephemeral=True
        )


# =========================
# 💬 日常 UI
# =========================

class ChatView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="☀️ 早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️ 早安", ephemeral=True)

    @discord.ui.button(label="🌙 晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙 晚安", ephemeral=True)


# =========================
# 🎁 驚喜
# =========================

class GiftView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎁 開啟", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):

        import random

        gifts = [
            "🧋 奶茶",
            "💖 抱抱",
            "🌙 你很重要",
            "🍫 巧克力",
            "💌 情書"
        ]

        await interaction.response.send_message(random.choice(gifts))


# =========================
# 📌 主選單
# =========================

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💞 情侶", style=discord.ButtonStyle.primary)
    async def couple(self, interaction, button):
        await interaction.response.send_message(
            "💞 情侶系統",
            view=CoupleView(),
            ephemeral=True
        )

    @discord.ui.button(label="🎁 驚喜", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        await interaction.response.send_message(
            "🎁 驚喜",
            view=GiftView(),
            ephemeral=True
        )

    @discord.ui.button(label="💬 日常", style=discord.ButtonStyle.secondary)
    async def chat(self, interaction, button):
        await interaction.response.send_message(
            "💬 日常",
            view=ChatView(),
            ephemeral=True
        )


# =========================
# 🚀 START COMMAND
# =========================

@bot.tree.command(name="start", description="開啟主選單")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📌 主選單",
        view=MainView(),
        ephemeral=True
    )


# =========================
# READY
# =========================

@bot.event
async def on_ready():
    await asyncio.sleep(2)

    try:
        synced = await bot.tree.sync()
        print(f"✅ synced {len(synced)} commands")
    except Exception as e:
        print("sync error:", e)

    print(f"💖 Logged in as {bot.user}")


# =========================
# RUN
# =========================

bot.run(os.getenv("TOKEN"))