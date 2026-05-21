import discord
from discord.ext import commands
from datetime import datetime
import random
import os
import wavelink

import discord
from discord.ext import commands
from datetime import datetime
import random
import os
import wavelink

# 👇 就放這裡（最上面、所有東西前）

print("RAW HOST =", repr(os.getenv("LAVALINK_HOST")))
print("RAW PORT =", repr(os.getenv("LAVALINK_PORT")))

# =========================
# BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# ENV（安全版）
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")

LAVALINK_HOST = "lavalink-production-cfa4.up.railway.app"
LAVALINK_PASSWORD = LOVE113
LAVALINK_PORT = 80

print("HOST =", LAVALINK_HOST)
print("PORT =", LAVALINK_PORT)

# =========================
# 情侶系統
# =========================

start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# =========================
# 音樂系統
# =========================

async def get_player(interaction):

    if not interaction.user.voice:
        return None

    channel = interaction.user.voice.channel
    player = interaction.guild.voice_client

    if not player:
        player = await channel.connect(cls=wavelink.Player)

    return player


async def play_song(interaction, query):

    player = await get_player(interaction)

    if not player:
        return await interaction.followup.send(
            "❌ 先加入語音頻道",
            ephemeral=True
        )

    await interaction.followup.send("🔍 搜尋中...")

    tracks = await wavelink.Playable.search(query)

    if not tracks:
        return await interaction.channel.send("❌ 找不到歌曲")

    track = tracks[0]

    await player.play(track)

    await interaction.channel.send(f"🎵 播放中：{track.title}")

# =========================
# MUSIC UI
# =========================

class MusicModal(discord.ui.Modal, title="搜尋音樂"):

    song = discord.ui.TextInput(label="輸入歌曲")

    async def on_submit(self, interaction):
        await interaction.response.defer()
        await play_song(interaction, self.song.value)


class MusicView(discord.ui.View):

    @discord.ui.button(label="🔍 搜尋", style=discord.ButtonStyle.primary)
    async def search(self, interaction, button):
        await interaction.response.send_modal(MusicModal())

    @discord.ui.button(label="⏸ 暫停", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.pause()
        await interaction.response.send_message("⏸ 已暫停", ephemeral=True)

    @discord.ui.button(label="▶ 繼續", style=discord.ButtonStyle.success)
    async def resume(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.resume()
        await interaction.response.send_message("▶ 已繼續", ephemeral=True)

    @discord.ui.button(label="⏭ 停止/跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.current:
            await vc.stop()
        await interaction.response.send_message("⏭ 已停止", ephemeral=True)

    @discord.ui.button(label="👋 離開", style=discord.ButtonStyle.danger)
    async def leave(self, interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("👋 已離開語音", ephemeral=True)

# =========================
# 情侶 UI
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

    @discord.ui.button(label="🎵 音樂", style=discord.ButtonStyle.success)
    async def music(self, interaction, button):
        await interaction.response.send_message(
            "🎵 音樂系統",
            view=MusicView(),
            ephemeral=True
        )

# =========================
# 驚喜
# =========================

class GiftView(discord.ui.View):

    @discord.ui.button(label="🎁 開啟", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):

        gifts = ["🧋 奶茶", "🍫 巧克力", "💖 抱抱", "✨ 幸運+100"]

        await interaction.response.send_message(random.choice(gifts))

# =========================
# 日常
# =========================

class ChatView(discord.ui.View):

    @discord.ui.button(label="☀️早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction, button):
        await interaction.response.send_message("☀️ 早安")

    @discord.ui.button(label="🌙晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction, button):
        await interaction.response.send_message("🌙 晚安")

# =========================
# 主選單
# =========================

class MainView(discord.ui.View):

    @discord.ui.button(label="💞情侶", style=discord.ButtonStyle.primary)
    async def couple(self, interaction, button):
        await interaction.response.edit_message(
            content="💞 情侶系統",
            view=CoupleView()
        )

    @discord.ui.button(label="🎁驚喜", style=discord.ButtonStyle.success)
    async def gift(self, interaction, button):
        await interaction.response.edit_message(
            content="🎁 驚喜",
            view=GiftView()
        )

    @discord.ui.button(label="💬日常", style=discord.ButtonStyle.secondary)
    async def chat(self, interaction, button):
        await interaction.response.edit_message(
            content="💬 日常",
            view=ChatView()
        )

# =========================
# Slash command
# =========================

@bot.tree.command(name="start", description="主選單")
async def start(interaction):
    await interaction.response.send_message(
        "📌 主選單",
        view=MainView(),
        ephemeral=True
    )

# =========================
# READY + Lavalink
# =========================

@bot.event
async def on_ready():

    print(bot.user)
    print("HOST =", LAVALINK_HOST)

    node = wavelink.Node(
        uri=f"http://{LAVALINK_HOST}:{LAVALINK_PORT}",
        password=LAVALINK_PASSWORD
    )

    await wavelink.Pool.connect(
        client=bot,
        nodes=[node]
    )

    await bot.tree.sync()

    print("✅ Lavalink connected")


bot.run(TOKEN)