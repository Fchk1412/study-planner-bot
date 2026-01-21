import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create intents
intents = discord.Intents.default()
intents.message_content = True  # needed for !commands

# Create the bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")

# Get token and run bot
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
