import discord
import random
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class letsgo(commands.Cog):
    def __init__(self, client):
        self.client=client
        
        self.image_names = []
        self.download_folder = 'images'
        self.update_images()
        
    def update_images(self):
        self.image_names = []
        #store all the names to the files
        for filename in os.listdir('images'):
            self.image_names.append(os.path.join(self.download_folder, filename))
      
    @commands.Cog.listener()
    async def on_message(self, message):
        messageContent = message.content.lower()
        img = self.image_names[random.randint(0, len(self.image_names) - 1)]

        if 'lets go' in messageContent or 'let\'s go' in message.content:
            await message.reply('Let\'s GOOOOOO', file=discord.File(img), mention_author=False)
       
def setup(client):
    client.add_cog(letsgo(client))