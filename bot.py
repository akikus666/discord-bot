import discord
from discord.ext import commands
from datetime import datetime
import random
import yt_dlp
import os
import asyncio
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
# 🎵 音樂系統 Queue
# =========================

music_queue = {}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


async def play_next(guild_id, vc):
    if guild_id not in music_queue or len(music_queue[guild_id]) == 0:
        return

    song = music_queue[guild_id].popleft()

    source = discord.FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS)
    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(
        play_next(guild_id, vc), bot.loop
    ))

# =========================
# 播放歌曲
# =========================

async def play_song(interaction, query):

    if not interaction.user.voice:
        await interaction.followup.send("🎤 請先加入語音頻道", ephemeral=True)
        return

    channel = interaction.user.voice.channel

    vc = interaction.guild.voice_client
    if not vc:
        vc = await channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        data = info["entries"][0]

    song = {
        "title": data["title"],
        "url": data["url"]
    }

    guild_id = interaction.guild.id

    if guild_id not in music_queue:
        music_queue[guild_id] = deque()

    music_queue[guild_id].append(song)

    await interaction.followup.send(f"🎵 已加入播放清單：{song['title']}")

    if not vc.is_playing():
        await play_next(guild_id, vc)


# =========================
# 🎵 Music UI
# =========================

class MusicView(discord.ui.View):

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
        await interaction.response.send_message("👋 已離開語音", ephemeral=True)


class MusicModal(discord.ui.Modal, title="搜尋音樂"):

    song = discord.ui.TextInput(label="輸入歌曲")

    async def on_submit(self, interaction):
        await interaction.response.defer()
        await play_song(interaction, self.song.value)


# =========================
# 💞 情侶 UI
# =========================

class CoupleView(discord.ui.View):

    @discord.ui.button(label="💞 days", style=discord.ButtonStyle.primary)
    async def days(self, interaction, button):
        await interaction.response.send_message(
            f"💞 已經在一起 {get_days()} 天了"
        )

    @discord.ui.button(label="💗 love", style=discord.ButtonStyle.primary)
    async def love(self, interaction, button):
        await interaction.response.send_message("💗 今天也很想你")

    @discord.ui.button(label="🤗 hug", style=discord.ButtonStyle.primary)
    async def hug(self, interaction, button):
        await interaction.response.send_message("🤗 抱抱 💖")

    @discord.ui.button(label="🎵 音樂", style=discord.ButtonStyle.success)
    async def music(self, interaction, button):
        await interaction.response.send_message(
            "🎵 音樂系統",
            view=MusicView(),
            ephemeral=True
        )

    @discord.ui.button(label="🔙 返回", style=discord.ButtonStyle.grey)
    async def back(self, interaction, button):
        await interaction.response.edit_message(
            content="📌 主選單",
            view=MainView()
        )


# =========================
# 🎁 驚喜系統
# =========================

class GiftView(discord.ui.View):

    @discord.ui.button(label="🎁 開啟驚喜", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):

        gifts = [
            "🧋 奶茶一杯",
            "💖 偷偷抱抱",
            "🌙 你是最重要的人",
            "🍫 巧克力",
            "💌 情書一封",
            "✨ 幸運+100%"
        ]

        await interaction.response.send_message(random.choice(gifts))


# =========================
# 💬 日常互動
# =========================

class ChatView(discord.ui.View):

    @discord.ui.button(label="☀️ 早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️ 早安～")

    @discord.ui.button(label="🌙 晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙 晚安～")


# =========================
# 📌 主選單
# =========================

class MainView(discord.ui.View):

    @discord.ui.button(label="💞 情侶系統", style=discord.ButtonStyle.primary)
    async def couple(self, interaction, button):
        await interaction.response.edit_message(
            content="💞 情侶系統",
            view=CoupleView()
        )

    @discord.ui.button(label="🎁 驚喜系統", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        await interaction.response.edit_message(
            content="🎁 驚喜系統",
            view=GiftView()
        )

    @discord.ui.button(label="💬 日常互動", style=discord.ButtonStyle.secondary)
    async def chat(self, interaction, button):
        await interaction.response.edit_message(
            content="💬 日常互動",
            view=ChatView()
        )


# =========================
# 🚀 slash command
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
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")


# =========================
# RUN
# =========================

bot.run(os.getenv("TOKEN"))