import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

client = commands.Bot(command_prefix='.')
load_dotenv()

@client.event # tell host the bot is running
async def on_ready():
    print('Logged in as {0.user}\n'.format(client))
    await client.change_presence(activity=discord.Game(name="stealing all your info"))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('token'))