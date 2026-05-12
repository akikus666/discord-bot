import discord
from discord.ext import commands
from datetime import datetime
import random
import os

# =========================
# ⚙️ Bot 基本設定
# =========================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 💡 在一起日期
# =========================

start_date = datetime(2025, 2, 24)

def get_days():
    return (datetime.now() - start_date).days

# =========================
# 📌 主選單
# =========================

class MainView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="💞 情侶系統", style=discord.ButtonStyle.primary)
    async def couple(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="💞 情侶系統",
            view=CoupleView()
        )

    @discord.ui.button(label="🎁 驚喜系統", style=discord.ButtonStyle.success)
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="🎁 驚喜系統",
            view=GiftView()
        )

    @discord.ui.button(label="💬 日常互動", style=discord.ButtonStyle.secondary)
    async def chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="💬 日常互動",
            view=ChatView()
        )

# =========================
# 💞 情侶系統
# =========================

class CoupleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="💞 days", style=discord.ButtonStyle.primary)
    async def days(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(
            content="💞 情侶系統（days）",
            view=self
        )

        await interaction.channel.send(
            f"💞 我們已經在一起 {get_days()} 天了"
        )

    @discord.ui.button(label="💗 love", style=discord.ButtonStyle.primary)
    async def love(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(
            content="💞 情侶系統（love）",
            view=self
        )

        await interaction.channel.send("💗 今天也很想你")

    @discord.ui.button(label="🤗 hug", style=discord.ButtonStyle.primary)
    async def hug(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(
            content="💞 情侶系統（hug）",
            view=self
        )

        await interaction.channel.send("🤗 抱抱 💖")

    @discord.ui.button(label="🔙 返回", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📌 主選單",
            view=MainView()
        )

# =========================
# 🎁 驚喜系統
# =========================

class GiftView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="🎁 小驚喜", style=discord.ButtonStyle.success)
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):

        gifts = [
            "🎁 你收到一杯奶茶 🧋",
            "💖 偷偷給你一個抱抱 🤗",
            "🌟 今天會有好事發生喔",
            "🍫 送你一塊巧克力",
            "🌙 你是最重要的人",
            "💌 一封匿名情書",
            "✨ 幸運值 +100%",
            "💞 今天也要想我一下喔"
        ]

        await interaction.response.edit_message(
            content="🎁 驚喜系統（已觸發）",
            view=self
        )

        await interaction.channel.send(random.choice(gifts))

    @discord.ui.button(label="🔙 返回", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📌 主選單",
            view=MainView()
        )

# =========================
# 💬 日常互動
# =========================

class ChatView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="☀️ 早安", style=discord.ButtonStyle.secondary)
    async def morning(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(
            content="💬 日常互動（早安）",
            view=self
        )

        await interaction.channel.send("☀️ 早安～今天也要開心 💖")

    @discord.ui.button(label="🌙 晚安", style=discord.ButtonStyle.secondary)
    async def night(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.edit_message(
            content="💬 日常互動（晚安）",
            view=self
        )

        await interaction.channel.send("🌙 晚安～夢裡見 💕")

    @discord.ui.button(label="🔙 返回", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📌 主選單",
            view=MainView()
        )

# =========================
# 🚀 /start
# =========================

@bot.tree.command(name="start", description="開啟主選單")
async def start(interaction: discord.Interaction):

    await interaction.response.send_message(
        "📌 主選單",
        view=MainView(),
        ephemeral=True
    )

# =========================
# 🤖 啟動
# =========================

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"✅ 已同步 {len(synced)} 個指令")
    print(f"💖 登入：{bot.user}")

# =========================
# 🔑 啟動 Bot
# =========================

# ❗ 啟動 Bot
bot.run(os.getenv("TOKEN"))