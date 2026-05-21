import discord
from discord.ext import commands
import wavelink
import os
import random
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

# =========================
# BOT
# =========================
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        node = wavelink.Node(
            uri="http://127.0.0.1:8080",
            password="youshallnotpass"
        )

        await wavelink.Pool.connect(
            nodes=[node],
            client=self
        )

        print("✅ Lavalink connected")

bot = Bot()

# =========================
# 💞 情侶系統
# =========================
start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# =========================
# 🎵 SAFE CONNECT
# =========================
async def safe_connect(channel):
    vc = channel.guild.voice_client

    if vc:
        return vc

    return await channel.connect(cls=wavelink.Player)

# =========================
# 🎵 MUSIC MODAL
# =========================
class MusicModal(discord.ui.Modal, title="🎵 搜尋音樂"):
    song = discord.ui.TextInput(label="輸入歌曲 / YouTube / 關鍵字")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not interaction.user.voice:
            return await interaction.followup.send("❌請先進語音", ephemeral=True)

        vc: wavelink.Player = await safe_connect(interaction.user.voice.channel)

        tracks = await wavelink.Playable.search(self.song.value)

        if not tracks:
            return await interaction.followup.send("❌找不到音樂")

        track = tracks[0]

        # queue
        if not vc.playing:
            await vc.play(track)
            return await interaction.followup.send(f"🎵播放：{track.title}")

        await vc.queue.put_wait(track)
        await interaction.followup.send(f"📥加入隊列：{track.title}")

# =========================
# 🎵 MUSIC UI
# =========================
class MusicView(discord.ui.View):

    @discord.ui.button(label="🔍搜尋", style=discord.ButtonStyle.primary)
    async def search(self, interaction, button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="⏸暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.pause(True)
        await interaction.response.send_message("⏸", ephemeral=True)

    @discord.ui.button(label="▶繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.pause(False)
        await interaction.response.send_message("▶", ephemeral=True)

    @discord.ui.button(label="⏭跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        vc: wavelink.Player = interaction.guild.voice_client
        if vc:
            await vc.stop()
        await interaction.response.send_message("⏭", ephemeral=True)

    @discord.ui.button(label="👋離開", style=discord.ButtonStyle.danger)
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
            "🎵音樂系統",
            view=MusicView(),
            ephemeral=True
        )

# =========================
# 🎁 驚喜 UI
# =========================
class GiftView(discord.ui.View):

    @discord.ui.button(label="🎁開啟", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        gifts = ["🧋奶茶", "💖抱抱", "🍫巧克力", "✨幸運+100%"]
        await interaction.response.send_message(random.choice(gifts))

# =========================
# 💬 日常 UI
# =========================
class ChatView(discord.ui.View):

    @discord.ui.button(label="☀️早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️早安")

    @discord.ui.button(label="🌙晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙晚安")

# =========================
# 📌 主選單
# =========================
class MainView(discord.ui.View):

    @discord.ui.button(label="💞情侶", style=discord.ButtonStyle.primary)
    async def couple(self, interaction, button):
        await interaction.response.edit_message(
            content="💞情侶系統",
            view=CoupleView()
        )

    @discord.ui.button(label="🎁驚喜", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        await interaction.response.edit_message(
            content="🎁驚喜",
            view=GiftView()
        )

    @discord.ui.button(label="💬日常", style=discord.ButtonStyle.secondary)
    async def chat(self, interaction, button):
        await interaction.response.edit_message(
            content="💬日常",
            view=ChatView()
        )

# =========================
# /start
# =========================
@bot.tree.command(name="start", description="主選單")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📌主選單",
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