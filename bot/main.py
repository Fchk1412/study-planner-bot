import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot.store import ExamStore



# Load environment variables from .env
load_dotenv()

# Create intents
intents = discord.Intents.default()
intents.message_content = True  # needed for !commands

# Create the bot
bot = commands.Bot(command_prefix="!", intents=intents)

store = ExamStore()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def add(ctx, date: str, *, exam_name: str):
    user_id = ctx.author.id
    exam_id = store.add_exam(user_id, exam_name, date)
    await ctx.send(f"Exam '{exam_name}' added for {ctx.author.name} on {date}.")

@bot.command()
async def list_exams(ctx):
    user_id = ctx.author.id
    exams = store.list_exams(user_id)
    if exams:
        exam_list = "\n".join([f"-{e['name']} - {e['date']} (Prep: {e['prep']}%)" for e in exams])
        await ctx.send(f"Exams for {ctx.author.name}:\n{exam_list}")
    else:
        await ctx.send(f"No exams found for {ctx.author.name}.")
        
@bot.command()
async def clear(ctx):
    user_id = ctx.author.id
    store.clear_exams(user_id)
    await ctx.send(f"All exams cleared for {ctx.author.name}.")

# Get token and run bot
store.init_db()  # Initialize the database using the store instance
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
