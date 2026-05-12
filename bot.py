import discord
from discord.ext import commands
from discord.ui import View
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
# ⚙️ Bot
# =========================

intents = discord.Intents.default()
intents.message_content = True  # ⚠️ 一定要開（不然收不到圖片）
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# 🧠 暫存對象
# =========================

pending_target = {}

# =========================
# 📸 手照系統 UI
# =========================

class HandView(View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="📸 開始傳手照", style=discord.ButtonStyle.green)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "👉 請先設定對象：\n`!sethand @對象`\n然後直接傳圖片",
            ephemeral=True
        )

    @discord.ui.button(label="👀 查看手照", style=discord.ButtonStyle.blurple)
    async def view(self, interaction: discord.Interaction, button: discord.ui.Button):

        data = load_data()
        user = str(interaction.user)

        imgs = [h for h in data["hands"] if h["to"] == user]

        if not imgs:
            await interaction.response.send_message("📭 沒有手照", ephemeral=True)
            return

        await interaction.response.send_message("📸 你的手照：", ephemeral=True)

        for img in imgs[-5:]:
            await interaction.followup.send(img["url"])

    @discord.ui.button(label="🔙 返回", style=discord.ButtonStyle.gray)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📌 主選單",
            view=MainView()
        )

# =========================
# 📌 主選單
# =========================

class MainView(View):

    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="💞 情侶系統", style=discord.ButtonStyle.primary)
    async def couple(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("💞 情侶系統（略）", ephemeral=True)

    @discord.ui.button(label="🎁 驚喜系統", style=discord.ButtonStyle.success)
    async def gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎁 驚喜（略）", ephemeral=True)

    @discord.ui.button(label="📸 手照系統", style=discord.ButtonStyle.secondary)
    async def hand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="📸 手照系統",
            view=HandView()
        )

# =========================
# 🚀 /start
# =========================

@bot.tree.command(name="start")
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📌 主選單",
        view=MainView(),
        ephemeral=True
    )

# =========================
# 📍 設定對象
# =========================

@bot.command()
async def sethand(ctx, target: str):
    pending_target[ctx.author.id] = target
    await ctx.send("📸 已設定對象，現在請直接傳圖片")

# =========================
# 📸 自動接收圖片（核心）
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    # 有設定對象 + 有圖片
    if message.author.id in pending_target:

        if message.attachments:

            url = message.attachments[0].url
            target = pending_target[message.author.id]

            data = load_data()

            data["hands"].append({
                "from": str(message.author),
                "to": target,
                "url": url
            })

            save_data(data)

            await message.channel.send("📸 手照已儲存 💖")

            del pending_target[message.author.id]

    await bot.process_commands(message)

# =========================
# 🤖 啟動
# =========================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

bot.run(os.getenv("TOKEN"))