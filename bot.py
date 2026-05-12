import discord
from discord.ext import commands
from discord.ui import View, Button
import json
from datetime import datetime
import random
import os

# =========================
# 📦 JSON DB
# =========================

DB_FILE = "data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return {"hands": []}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
# 📸 手照系統（新增）
# =========================

class HandView(View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="📸 上傳手照說明", style=discord.ButtonStyle.green)
    async def upload_info(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(
            "📸 用指令上傳：\n`!hand @對象 + 圖片`",
            ephemeral=True
        )

    @discord.ui.button(label="👀 查看我的手照", style=discord.ButtonStyle.blurple)
    async def view(self, interaction: discord.Interaction, button: Button):

        data = load_data()
        user = str(interaction.user)

        imgs = [h for h in data["hands"] if h["to"] == user]

        if not imgs:
            await interaction.response.send_message("📭 沒有手照", ephemeral=True)
            return

        await interaction.response.send_message("📸 你的手照：", ephemeral=True)

        for img in imgs[-5:]:
            await interaction.followup.send(img["url"])

    @discord.ui.button(label="🔙 返回", style=discord.ButtonStyle.grey)
    async def back(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content="📌 主選單",
            view=MainView()
        )

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

    # 🔥 新增：手照系統入口
    @discord.ui.button(label="📸 手照系統", style=discord.ButtonStyle.secondary)
    async def hand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📸 手照系統",
            view=HandView()
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
        await interaction.channel.send(f"💞 我們已經在一起 {get_days()} 天了")

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
# 📌 /start
# =========================

@bot.tree.command(name="start", description="開啟主選單")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📌 主選單",
        view=MainView(),
        ephemeral=True
    )

# =========================
# 📸 手照指令（上傳）
# =========================

@bot.command()
async def hand(ctx, target: str):
    if not ctx.message.attachments:
        await ctx.send("❌ 請附上圖片")
        return

    url = ctx.message.attachments[0].url

    data = load_data()

    data["hands"].append({
        "from": str(ctx.author),
        "to": target,
        "url": url
    })

    save_data(data)

    await ctx.send("📸 手照已保存")

# =========================
# 🚀 啟動
# =========================

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"✅ 已同步 {len(synced)} 個指令")
    print(f"💖 登入：{bot.user}")

bot.run(os.getenv("TOKEN"))