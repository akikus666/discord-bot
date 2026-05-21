import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
import random
from datetime import datetime
from collections import deque

# ======================
# ENV
# ======================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

print("BOT STARTING...")
print("TOKEN OK:", bool(TOKEN))

# ======================
# INTENTS
# ======================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# 💞 情侶天數
# ======================
start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# ======================
# 🎵 QUEUE
# ======================
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]

# ======================
# YT-DLP
# ======================
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

# ======================
# MUSIC ENGINE
# ======================
async def play_next(guild_id, vc):
    queue = get_queue(guild_id)

    if not queue:
        return

    song = queue.popleft()

    source = discord.FFmpegPCMAudio(song["url"], **FFMPEG_OPTIONS)

    def after(err):
        fut = asyncio.run_coroutine_threadsafe(
            play_next(guild_id, vc),
            bot.loop
        )
        try:
            fut.result()
        except:
            pass

    vc.play(source, after=after)

# ======================
# CONNECT VC
# ======================
async def safe_connect(channel):
    vc = channel.guild.voice_client

    if vc and vc.is_connected():
        return vc

    return await channel.connect()

# ======================
# MUSIC FUNCTION
# ======================
async def play_song(interaction, query):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ 先進語音", ephemeral=True)

    vc = await safe_connect(interaction.user.voice.channel)

    await interaction.response.send_message("🔍 搜尋中...")

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        data = info["entries"][0]

    song = {
        "title": data["title"],
        "url": data["url"]
    }

    get_queue(interaction.guild.id).append(song)

    await interaction.followup.send(f"🎵 已加入：{song['title']}")

    if not vc.is_playing():
        await play_next(interaction.guild.id, vc)

# ======================
# 🎵 MUSIC UI
# ======================
class MusicView(discord.ui.View):

    @discord.ui.button(label="🔍 搜尋", style=discord.ButtonStyle.primary)
    async def search(self, interaction, button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="⏸ 暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.pause()
        await interaction.response.send_message("⏸ 暫停", ephemeral=True)

    @discord.ui.button(label="▶ 繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.resume()
        await interaction.response.send_message("▶ 繼續", ephemeral=True)

    @discord.ui.button(label="⏭ 跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
        await interaction.response.send_message("⏭ 跳過", ephemeral=True)

    @discord.ui.button(label="👋 離開", style=discord.ButtonStyle.danger)
    async def leave(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("👋 離開")

class MusicModal(discord.ui.Modal, title="搜尋音樂"):
    song = discord.ui.TextInput(label="歌曲")

    async def on_submit(self, interaction):
        await play_song(interaction, self.song.value)

# ======================
# 💞 情侶 UI（修正版）
# ======================
class CoupleView(discord.ui.View):

    @discord.ui.button(label="💞 天數", style=discord.ButtonStyle.primary)
    async def days(self, interaction, button):
        await interaction.response.send_message(f"💞 在一起 {get_days()} 天")

    @discord.ui.button(label="💗 love", style=discord.ButtonStyle.primary)
    async def love(self, interaction, button):
        await interaction.response.send_message("💗 想你")

    @discord.ui.button(label="🤗 hug", style=discord.ButtonStyle.primary)
    async def hug(self, interaction, button):
        await interaction.response.send_message("🤗 抱抱")

    @discord.ui.button(label="🎵 音樂", style=discord.ButtonStyle.success)
    async def music(self, interaction, button):
        await interaction.response.send_message("🎵 音樂面板", view=MusicView(), ephemeral=True)

# ======================
# 🎁 驚喜
# ======================
class GiftView(discord.ui.View):

    @discord.ui.button(label="🎁 開啟", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        gifts = ["🧋 奶茶", "💖 抱抱", "🍫 巧克力", "✨ 幸運+100%"]
        await interaction.response.send_message(random.choice(gifts))

# ======================
# 💬 日常
# ======================
class ChatView(discord.ui.View):

    @discord.ui.button(label="☀️ 早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️ 早安")

    @discord.ui.button(label="🌙 晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙 晚安")

# ======================
# 📌 主選單
# ======================
class MainView(discord.ui.View):

    @discord.ui.button(label="💞 情侶", style=discord.ButtonStyle.primary)
    async def couple(self, interaction, button):
        await interaction.response.edit_message(content="💞 情侶系統", view=CoupleView())

    @discord.ui.button(label="🎁 驚喜", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        await interaction.response.edit_message(content="🎁 驚喜", view=GiftView())

    @discord.ui.button(label="💬 日常", style=discord.ButtonStyle.secondary)
    async def chat(self, interaction, button):
        await interaction.response.edit_message(content="💬 日常", view=ChatView())

# ======================
# /start
# ======================
@bot.tree.command(name="start", description="主選單")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📌 主選單",
        view=MainView(),
        ephemeral=True
    )

# ======================
# PREFIX PLAY
# ======================
@bot.command()
async def play(ctx, query: str):
    if not ctx.author.voice:
        return await ctx.send("❌ 先進語音")

    vc = await safe_connect(ctx.author.voice.channel)

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        data = info["entries"][0]

    song = {"title": data["title"], "url": data["url"]}
    get_queue(ctx.guild.id).append(song)

    await ctx.send(f"🎵 加入：{song['title']}")

    if not vc.is_playing():
        await play_next(ctx.guild.id, vc)

# ======================
# RUN
# ======================
bot.run(TOKEN)