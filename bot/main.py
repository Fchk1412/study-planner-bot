import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from bot.store import ExamStore



# Load environment variables from .env
load_dotenv()

# Create intents
intents = discord.Intents.default()

# Create the bot
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

store = ExamStore()

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")
    print("Slash commands synced!")



@tree.command(name="add", description="Add a new exam to your study planner")
@app_commands.describe(
    exam_name="The name of the exam",
    date="The date of the exam (e.g., 2026-01-30)"
)
async def add(interaction: discord.Interaction, exam_name: str, date: str):
    user_id = interaction.user.id
    exam_id = store.add_exam(user_id, exam_name, date)
    await interaction.response.send_message(f"Exam '{exam_name}' added for {interaction.user.name} on {date}.")

@tree.command(name="list", description="List all your scheduled exams")
async def list_exams(interaction: discord.Interaction):
    user_id = interaction.user.id
    exams = store.list_exams(user_id)
    if exams:
        exam_list = "\n".join([f"-{e['name']} - {e['date']} (Prep: {e['prep']}%)" for e in exams])
        await interaction.response.send_message(f"Exams for {interaction.user.name}:\n{exam_list}")
    else:
        await interaction.response.send_message(f"No exams found for {interaction.user.name}.")
        
@tree.command(name="clear", description="Clear all your exams")
async def clear(interaction: discord.Interaction):
    user_id = interaction.user.id
    store.clear_exams(user_id)
    await interaction.response.send_message(f"All exams cleared for {interaction.user.name}.")

# Get token and run bot
store.init_db()  # Initialize the database using the store instance
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
