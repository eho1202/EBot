import discord
from discord.ext import commands

class ping(commands.Cog):
    def __init__(self, client):
        self.client=client
        
    @commands.command()   # Check bot latency
    async def ping(self, ctx): 
        await ctx.send(f'Pong! 🏓 `{round(self.client.latency * 1000)}ms`')
    
def setup(client):
    client.add_cog(ping(client))        
