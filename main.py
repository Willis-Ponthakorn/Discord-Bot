import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as, {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await message.channel.send("@here", delete_after=1)

    await bot.process_commands(message)


bot.run(token)


