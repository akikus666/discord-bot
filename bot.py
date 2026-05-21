import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from datetime import datetime
from collections import defaultdict, deque

# =========================
# TOKEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN 沒有設定")

print("BOT STARTING...")
print("TOKEN OK:", bool(TOKEN))

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, reconnect=True)

# =========================
# 💞 情侶系統
# =========================
start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# =========================
# 🎵 QUEUE
# =========================
queues = defaultdict(deque)

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
# SAFE VOICE CONNECT
# =========================
async def safe_connect(channel):
    vc = channel.guild.voice_client

    if vc and vc.is_connected():
        return vc

    try:
        return await channel.connect(timeout=60, reconnect=True)
    except Exception as e:
        print("VOICE CONNECT ERROR:", e)
        return None

# =========================
# PLAY NEXT
# =========================
async def play_next(guild_id, vc):
    queue = queues[guild_id]

    if not queue:
        return

    song = queue.popleft()

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song["url"], download=False)
            audio_url = info["url"]

        source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_opts)

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
# MUSIC FUNCTION
# =========================
async def play_music(ctx, url: str):
    if not ctx.author.voice:
        return await ctx.send("❌ 你沒有在語音頻道")

    vc = await safe_connect(ctx.author.voice.channel)
    if not vc:
        return await ctx.send("❌ 無法加入語音（4006）")

    queue = queues[ctx.guild.id]
    queue.append({"url": url})

    await ctx.send(f"🎵 已加入播放")

    if not vc.is_playing():
        await play_next(ctx.guild.id, vc)

# =========================
# 🎮 TEXT COMMANDS
# =========================
@bot.command()
async def play(ctx, url: str):
    await play_music(ctx, url)

@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏭ skip")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    queues[ctx.guild.id].clear()
    await ctx.send("⏹ stop")

# =========================
# 💞 UI VIEWS
# =========================
class CoupleView(discord.ui.View):

    @discord.ui.button(label="💞 days", style=discord.ButtonStyle.primary)
    async def days(self, interaction, button):
        await interaction.response.send_message(f"💞 在一起 {get_days()} 天")

    @discord.ui.button(label="💗 love", style=discord.ButtonStyle.primary)
    async def love(self, interaction, button):
        await interaction.response.send_message("💗 想你")

    @discord.ui.button(label="🤗 hug", style=discord.ButtonStyle.primary)
    async def hug(self, interaction, button):
        await interaction.response.send_message("🤗 抱抱")

    @discord.ui.button(label="🎵 music", style=discord.ButtonStyle.success)
    async def music(self, interaction, button):
        await interaction.response.send_message("🎵 請用 !play 或貼連結")

class GiftView(discord.ui.View):

    @discord.ui.button(label="🎁 open", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        import random
        gifts = ["🧋 奶茶", "💖 抱抱", "🍫 巧克力", "✨ 幸運+100%"]
        await interaction.response.send_message(random.choice(gifts))

class ChatView(discord.ui.View):

    @discord.ui.button(label="☀️ 早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️ 早安")

    @discord.ui.button(label="🌙 晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙 晚安")

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
# SYNC COMMANDS
# =========================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"💖 Synced {len(synced)} commands")
    except Exception as e:
        print("SYNC ERROR:", e)

    print(f"💖 Logged in as {bot.user}")

# =========================
# RUN
# =========================
bot.run(TOKEN)