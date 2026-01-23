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
    date="The date of the exam (e.g., 30-01-2026)",
    prep="Your preparation percentage for the exam"
)
async def add(interaction: discord.Interaction, exam_name: str, date: str, prep: int = 0):
    user_id = interaction.user.id
    try:
        exam_id = store.add_exam(user_id, exam_name, date, prep)
        embed = discord.Embed(
            title="✅ Exam Added Successfully!",
            description=f"Your exam has been added to your study planner.",
            color=discord.Color.green()
        )
        embed.add_field(name="📚 Exam Name", value=exam_name, inline=False)
        embed.add_field(name="📅 Date", value=date, inline=True)
        embed.add_field(name="📊 Preparation", value=f"{prep}%", inline=True)
        embed.set_footer(text=f"Added by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    except ValueError as e:
        embed = discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="list", description="List all your scheduled exams")
async def list_exams(interaction: discord.Interaction):
    user_id = interaction.user.id
    exams = store.list_exams(user_id)
    
    if exams:
        embed = discord.Embed(
            title="📚 Your Exam Schedule",
            description=f"You have **{len(exams)}** exam{'s' if len(exams) != 1 else ''} scheduled.",
            color=discord.Color.blue()
        )
        
        for index, exam in enumerate(exams, start=1):
            # Create a progress bar
            prep = exam['prep']
            filled = int(prep / 10)
            bar = "🟩" * filled + "⬜" * (10 - filled)
            
            field_value = f"📅 **Date:** {exam['date']}\n📊 **Progress:** {bar} {prep}%"
            embed.add_field(name=f"#{index} 📖 {exam['name']}", value=field_value, inline=False)
        
        embed.set_footer(text=f"Good luck with your studies, {interaction.user.name}! 🎓")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="📚 Your Exam Schedule",
            description="You don't have any exams scheduled yet.\n\nUse `/add` to add your first exam!",
            color=discord.Color.greyple()
        )
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)

@tree.command(name="remove", description="Remove an exam from your study planner")
@app_commands.describe(
    position="The position number of the exam to remove (use /list to see positions)"
)
async def remove(interaction: discord.Interaction, position: int):
    user_id = interaction.user.id
    exams = store.list_exams(user_id)
    
    if position < 1 or position > len(exams):
        embed = discord.Embed(
            title="❌ Error",
            description=f"Invalid position. Please enter a number between 1 and {len(exams)}.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Get the exam at the specified position (position is 1-indexed)
    exam = exams[position - 1]
    exam_id = exam['id']
    exam_name = exam['name']
    
    store.remove_exam(user_id, exam_id)
    embed = discord.Embed(
        title="🗑️ Exam Removed",
        description=f"**{exam_name}** has been successfully removed from your study planner.",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Removed by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@tree.command(name="clear", description="Clear all your exams")
async def clear(interaction: discord.Interaction):
    user_id = interaction.user.id
    store.clear_exams(user_id)
    embed = discord.Embed(
        title="🗑️ Exams Cleared",
        description="All your exams have been successfully removed from your study planner.",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Cleared by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# Get token and run bot
store.init_db()  # Initialize the database using the store instance
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
