import os
import discord
from discord import app_commands
import aiohttp
from keep_alive import keep_alive
from dotenv import load_dotenv

API_KEY = os.getenv("FORTNITE_API_KEY")
BASE_URL = "https://fortnite-api.com/v2"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

headers = {"Authorization": API_KEY}

async def fetch_json(session, url):
    async with session.get(url, headers=headers) as resp:
        return await resp.json()

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="shop", description="現在のBRアイテムショップを表示")
async def shop(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/shop/br")
    if data.get("status") != 200:
        await interaction.response.send_message("ショップ情報の取得に失敗しました。", ephemeral=True)
        return
    entries = data["data"]["featured"]["entries"]
    embed = discord.Embed(title="Fortnite Current Item Shop")
    for item in entries[:10]:
        name = item["items"][0]["name"]
        img = item["items"][0]["images"]["icon"]
        embed.add_field(name=name, value=f"[Icon]({img})", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cosmetic", description="名前でコスメ情報を検索")
@app_commands.describe(name="Name")
async def cosmetic(interaction: discord.Interaction, name: str):
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/cosmetics/br/search?name={name}"
        data = await fetch_json(session, url)
    if data.get("status") != 200 or not data.get("data"):
        await interaction.response.send_message("コスメが見つかりません。", ephemeral=True)
        return
    item = data["data"]
    embed = discord.Embed(title=item["name"], description=item.get("description", "説明なし"))
    embed.set_thumbnail(url=item["images"]["icon"])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="news", description="最新のBRニュースを表示")
async def news(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/news/br")
    if data.get("status") != 200:
        await interaction.response.send_message("ニュースの取得に失敗しました。", ephemeral=True)
        return
    news = data["data"][0]
    embed = discord.Embed(title=news["title"], description=news["body"])
    embed.set_image(url=news["image"])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="map", description="現在のマップPOI画像を表示")
async def map(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/map")
    if data.get("status") != 200:
        await interaction.response.send_message("マップの取得に失敗しました。", ephemeral=True)
        return
    url = data["data"]["images"]["pois"]
    embed = discord.Embed(title="Current Fortnite Map POIs")
    embed.set_image(url=url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="stats", description="名前でプレイヤーステータスを取得")
@app_commands.describe(name="プレイヤー名", platform="プラットフォーム (pc, xbox, psn)")
async def stats(interaction: discord.Interaction, name: str, platform: str):
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/stats/br/v2?name={name}&platform={platform}"
        data = await fetch_json(session, url)
    if data.get("status") != 200 or not data.get("data"):
        await interaction.response.send_message("プレイヤーが見つかりません。", ephemeral=True)
        return
    stats = data["data"]["stats"]["all"]["overall"]
    embed = discord.Embed(title=f"{name}のプレイヤーステータス")
    embed.add_field(name="キル数", value=str(stats["kills"]))
    embed.add_field(name="勝利数", value=str(stats["wins"]))
    embed.add_field(name="試合数", value=str(stats["matches"]))
    embed.add_field(name="キル/死", value=str(stats["kd"]))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="creative", description="クリエイティブコードで島情報を検索")
@app_commands.describe(code="クリエイティブコード")
async def creative(interaction: discord.Interaction, code: str):
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/creative/search?code={code}"
        data = await fetch_json(session, url)
    if data.get("status") != 200 or not data.get("data"):
        await interaction.response.send_message("島が見つかりません。", ephemeral=True)
        return
    island = data["data"]
    embed = discord.Embed(title=island["name"], description=island.get("description", "説明なし"))
    embed.set_image(url=island["images"]["banner"])
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="challenges", description="最新チャレンジを取得")
async def challenges(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/challenges")
    if data.get("status") != 200:
        await interaction.response.send_message("チャレンジ情報の取得に失敗しました。", ephemeral=True)
        return
    embed = discord.Embed(title="最新チャレンジ")
    for challenge in data["data"]["featured"]:
        embed.add_field(name=challenge["title"], value=challenge.get("description", "説明なし"), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="battlepass", description="現シーズンのバトルパス報酬を表示")
async def battlepass(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/battlepass")
    if data.get("status") != 200:
        await interaction.response.send_message("バトルパス情報の取得に失敗しました。", ephemeral=True)
        return
    embed = discord.Embed(title="現シーズンのバトルパス報酬")
    rewards = data["data"]["levels"]
    for lvl in rewards[:10]:
        embed.add_field(name=f"レベル {lvl['level']}", value=lvl["reward"]["name"], inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="events", description="現在のゲーム内イベント情報を表示")
async def events(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/events")
    if data.get("status") != 200:
        await interaction.response.send_message("イベント情報の取得に失敗しました。", ephemeral=True)
        return
    embed = discord.Embed(title="現在のゲーム内イベント")
    for event in data["data"]:
        embed.add_field(name=event["title"], value=event.get("description", "説明なし"), inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="gamemodes", description="現在のゲームモード情報を表示")
async def gamemodes(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/gamemode")
    if data.get("status") != 200:
        await interaction.response.send_message("ゲームモード情報の取得に失敗しました。", ephemeral=True)
        return
    embed = discord.Embed(title="現在のゲームモード")
    for mode in data["data"]["modes"]:
        embed.add_field(name=mode["name"], value=f"ID: {mode['id']}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="status", description="Epic Gamesサーバーステータスを表示")
async def status(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/status")
    if data.get("status") != 200:
        await interaction.response.send_message("サーバーステータスの取得に失敗しました。", ephemeral=True)
        return
    status_data = data["data"]
    embed = discord.Embed(title="Epic Games サーバーステータス")
    for service in status_data:
        embed.add_field(name=service["name"], value=service["status"], inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="store", description="Epic Gamesストア商品一覧を表示")
async def store(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, f"{BASE_URL}/store")
    if data.get("status") != 200:
        await interaction.response.send_message("ストア情報の取得に失敗しました。", ephemeral=True)
        return
    embed = discord.Embed(title="Epic Games ストア商品一覧")
    for item in data["data"]:
        embed.add_field(name=item["title"], value=item.get("description", "説明なし"), inline=False)
    await interaction.response.send_message(embed=embed)

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_TOKEN is None:
    print("DISCORD_BOT_TOKEN が設定されていません。")
else:
    print("Botが正常に起動しました。")

keep_alive()
bot.run(DISCORD_TOKEN)
