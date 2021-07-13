import asyncio
import discord
import itertools
from discord.ext import commands
from async_timeout import timeout
import youtube_dl
import os
import sys

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.data = data

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')
    
    def __getitem__(self, item: str):
        return self.__getattribute__(item)
    
    @classmethod
    async def get_song(cls, ctx, search: str, *, loop, download=False):
        vc = ctx.voice_client
        loop = loop or asyncio.get_event_loop()
        
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=search, download=download))
        
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        
        if vc.is_playing():
            embed = discord.Embed(title="", description=f'Queued [{data["title"]}]({data["webpage_url"]}) [{ctx.author.mention}]')
            await ctx.send(embed=embed, delete_after=20)
        
        if download:
            source = ytdl.prepare_filename(data)
        else: 
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author.mention, 'title': data['title']}
        
        return cls(discord.FFmpegPCMAudio(source, **ffmpeg_options), data=data, requester=ctx.author.mention)

    @classmethod
    async def regather_song(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']
        
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url=data['webpage_url'], download=False))
        
        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)
            
class MusicPlayer:
    
    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np')
    
    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog
        
        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        
        self.np = None
        self.current = None
        
        ctx.bot.loop.create_task(self.player_loop())
        
    async def player_loop(self):
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            self.next.clear()
        
            try:
                async with timeout(300):
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)
            
            if not isinstance(source, YTDLSource):
                try:
                    source = await YTDLSource.regather_song(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                                f'```css\n[{e}]\n```')
                    continue
            
            self.current = source
            
            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            embed = discord.Embed(title='Now Playing', description=f'[{source.title}]({source.web_url}) [{source.requester}]', colour=0xffa500)
            self.np = await self._channel.send(embed=embed)
            
            await self.next.wait()
            
            source.cleanup()
            self.current = None 
            
            try:
                await self.np.delete()
            except discord.HTTPException:
                pass
                
    def destroy(self, guild):
        return self.client.loop.create_task(self._cog.cleanup(guild))
    
class music(commands.Cog):
    
    __slots__ = ('client', 'players')
    
    def __init__(self, client):
        self.client = client
        self.players = {}
    
    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        
        try:
            del self.players[guild.id]
        except KeyError:
            pass
    
    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
            
        return player
    
    @commands.command(pass_context=True, aliases=['j', 'alive', 'connect'])
    async def join(self, ctx):
        if ctx.author.voice is None: # if user is not in a vc
            embed = discord.Embed(description='Connect to a voice channel!', colour=0xc80000)
            await ctx.send(embed=embed, delete_after=20)
        
        vc = ctx.author.voice.channel
        
        if ctx.voice_client is None: # if bot is not in a vc
            await vc.connect()
            await ctx.guild.change_voice_state(channel=vc, self_deaf=True)
        else: # if bot has to move to another channel
            await ctx.voice_client.move_to(vc)
    
    @commands.command(pass_context=True, aliases=['die', 'dc', 'l', 'disconnect'])
    async def leave(self, ctx):
        if ctx.author.voice is None:
            embed = discord.Embed(description='Connect to the voice channel I\'ve been left in!', colour=0xc80000)
            await ctx.send(embed=embed, delete_after=20)
        else:
            await ctx.voice_client.disconnect()
            await ctx.message.add_reaction('👋')
 
    @commands.command(pass_context=True)
    async def pause(self, ctx): 
        vc = ctx.voice_client
        
        if not vc or not vc.is_playing():
            embed = discord.Embed(description='Nothing is currently playing rn', colour=0x3498db)
            return await ctx.send(embed=embed, delete_after=20)
        elif vc.is_paused():
            return
         
        vc.pause()
        await ctx.message.add_reaction('👌')
    
    @commands.command(pass_context=True)
    async def stop(self, ctx):
        vc = ctx.voice_client
        
        if not vc or not vc.is_connected():
            embed = discord.Embed(description='Nothing is currently playing rn', colour=0x3498db)
            return await ctx.send(embed=embed, delete_after=20)
        
        await self.cleanup(ctx.guild)
        
    @commands.command(pass_context=True, aliases=['r'])
    async def resume(self, ctx): 
        vc = ctx.voice_client
        
        if not vc or not vc.is_playing():
            embed = discord.Embed(description='Nothing is currently playing rn', colour=0x3498db)
            return await ctx.send(embed=embed, delete_after=20)
        elif vc.is_paused():
            return 
        
        vc.resume()
        await ctx.message.add_reaction('👌')

    @commands.command(pass_context=True, aliases=['p'])
    async def play(self, ctx, *, search: str):
        vc = ctx.voice_client
        
        await ctx.trigger_typing()
        
        if not vc:
            await ctx.invoke(self.join)
            
        player = self.get_player(ctx)
        
        source = await YTDLSource.get_song(ctx, search, loop=self.client.loop, download=False)
            
        await player.queue.put(source)
    
    @commands.command(pass_context=True, aliases=['q'])
    async def queue(self, ctx):
        vc = ctx.voice_client
        
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('No songs are queued at the moment')
        
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        
        seconds = vc.source.duration % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        if hour > 0:
            duration = "%dh %02dm %02ds" % (hour, minutes, seconds)
        else:
            duration = "%02dm %02ds" % (minutes, seconds)
        
        upcoming = list(itertools.islice(player.queue._queue, 0, int(len(player.queue._queue))))
        fmt = '\n'.join(f"{(upcoming.index(_)) + 2}) {_['title']} | ` {duration}`\n" for _ in upcoming)
        fmt = f"```ml\n1) {vc.source.title} | {duration} \n\n" + fmt + "```"
        
        await ctx.send(fmt)
    
    @commands.command(pass_context=True, aliases=['np'])
    async def nowplaying(self, ctx):
        vc = ctx.voice_client
        
        player = self.get_player(ctx)
        if not player.current:
            embed = discord.Embed('Nothing is being played')
            return await ctx.send(embed=embed)
        
        try:
            await player.np.delete()
        except discord.HTTPException:
            pass
        
        player.np = await ctx.send(f'**Now Playing:** `[{vc.source.title}]({vc.source.web_url}) [{vc.source.requester}]`')
    
    @commands.command(pass_context=True)
    async def skip(self, ctx):
        vc = ctx.voice_client
        
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return
        
        vc.stop()
        await ctx.send(f'Song skipped: [{vc.source.title}]({vc.source.url})')
    
def setup(client):
    client.add_cog(music(client))