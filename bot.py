import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from datetime import datetime
from collections import deque

# =========================
# TOKEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN missing")

# =========================
# INTENTS
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
# 🎵 QUEUE
# =========================
queues = {}

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = deque()
    return queues[guild_id]

# =========================
# YT-DLP
# =========================
ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
}

ffmpeg_opts = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

# =========================
# SAFE VC CONNECT（修 4006）
# =========================
async def safe_connect(channel):
    vc = channel.guild.voice_client

    if vc and vc.is_connected():
        return vc

    try:
        return await channel.connect(timeout=60, reconnect=True)
    except Exception as e:
        print("VOICE CONNECT FAIL:", e)
        return None

# =========================
# PLAY NEXT
# =========================
async def play_next(guild_id, vc):
    queue = get_queue(guild_id)

    if not queue:
        return

    song = queue.popleft()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song["url"], download=False)
            audio = info["url"]

        source = discord.FFmpegPCMAudio(audio, **ffmpeg_opts)

    except Exception as e:
        print("YT ERROR:", e)
        return await play_next(guild_id, vc)

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

# =========================
# 🎵 SEARCH (YT + Spotify fallback)
# =========================
async def search_song(query: str):
    # Spotify link → ignore extract only keyword
    if "spotify" in query:
        query = query.split("/")[-1]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        return {
            "title": info["entries"][0]["title"],
            "url": info["entries"][0]["url"]
        }

# =========================
# 🎵 MODAL
# =========================
class MusicModal(discord.ui.Modal, title="🎵 搜尋音樂"):
    song = discord.ui.TextInput(label="輸入歌曲 / Spotify / YouTube")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        vc = await safe_connect(interaction.user.voice.channel)
        if not vc:
            await interaction.followup.send("❌ 連線失敗", ephemeral=True)
            return

        data = await search_song(self.song.value)

        queue = get_queue(interaction.guild.id)
        queue.append(data)

        await interaction.followup.send(f"🎵 已加入：{data['title']}")

        if not vc.is_playing():
            await play_next(interaction.guild.id, vc)

# =========================
# 🎮 MUSIC UI
# =========================
class MusicView(discord.ui.View):

    @discord.ui.button(label="🔍 搜尋音樂", style=discord.ButtonStyle.primary)
    async def search(self, interaction, button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="⏸ 暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.pause()
        await interaction.response.send_message("⏸", ephemeral=True)

    @discord.ui.button(label="▶ 繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.resume()
        await interaction.response.send_message("▶", ephemeral=True)

    @discord.ui.button(label="⏭ 跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
        await interaction.response.send_message("⏭", ephemeral=True)

    @discord.ui.button(label="👋 離開", style=discord.ButtonStyle.danger)
    async def leave(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("👋", ephemeral=True)

# =========================
# 💞 情侶 UI
# =========================
class CoupleView(discord.ui.View):

    @discord.ui.button(label="💞 days", style=discord.ButtonStyle.primary)
    async def days(self, interaction, button):
        await interaction.response.send_message(f"💞 {get_days()} 天")

    @discord.ui.button(label="💗 love", style=discord.ButtonStyle.primary)
    async def love(self, interaction, button):
        await interaction.response.send_message("💗 想你")

    @discord.ui.button(label="🤗 hug", style=discord.ButtonStyle.primary)
    async def hug(self, interaction, button):
        await interaction.response.send_message("🤗 抱抱")

    @discord.ui.button(label="🎵 音樂", style=discord.ButtonStyle.success)
    async def music(self, interaction, button):
        await interaction.response.send_message(
            "🎵 音樂系統",
            view=MusicView(),
            ephemeral=True
        )

# =========================
# 🎁 驚喜 UI
# =========================
class GiftView(discord.ui.View):

    @discord.ui.button(label="🎁 開啟", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        gifts = ["🧋 奶茶", "💖 抱抱", "🍫 巧克力", "✨ 幸運+100%"]
        await interaction.response.send_message(random.choice(gifts))

# =========================
# 💬 日常 UI
# =========================
class ChatView(discord.ui.View):

    @discord.ui.button(label="☀️ 早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️ 早安")

    @discord.ui.button(label="🌙 晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙 晚安")

# =========================
# 📌 主選單
# =========================
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

# =========================
# /start
# =========================
@bot.tree.command(name="start", description="主選單")
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
    print(f"💖 Logged in as {bot.user}")

# =========================
# RUN
# =========================
bot.run(TOKEN)