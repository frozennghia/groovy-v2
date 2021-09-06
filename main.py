import asyncio
import os
import discord
from discord.ext import commands, tasks
import youtube_dl


def main(name):
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents().all()
    client = discord.Client(intents=intents)
    bot = commands.Bot(command_prefix="-", intents=intents)
    youtube_dl.utils.bug_reports_message = lambda: ''
    song_queue = asyncio.Queue()

    ytdl_format_options = {
        'format': 'bestaudio/best',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
    }

    ffmpeg_options = {
        'options': '-vn'
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

    class YTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = ""

        @classmethod
        async def from_url(cls, url, *, loop=None, stream=False):
            loop = loop or asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]
            filename = data['title'] if stream else ytdl.prepare_filename(data)
            return filename

    @bot.command(name='join', help='Tells the bot to join the voice channel')
    async def join(ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @bot.command(name='leave', help='To make the bot leave the voice channel')
    async def leave(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    @bot.command(name='play', help='Play song')
    async def queue_play(ctx, url):
        await join(ctx)
        song_queue.put_nowait([ctx, url])
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await ctx.send('Queued {}'.format(url))
            return
        while not song_queue.empty():
            next_song = await song_queue.get()
            await asyncio.create_task(play(next_song[0], next_song[1]))

    async def play(ctx, song_url):
        voice_client = ctx.message.guild.voice_client
        if ctx.message.author.voice and not voice_client.is_playing():
            server = ctx.message.guild
            voice_channel = server.voice_client
            async with ctx.typing():
                filename = await YTDLSource.from_url(song_url, loop=bot.loop)
                voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
            await ctx.send('**Now playing:** {}'.format(filename))
            await wait_to_finish(ctx)
        else:
            await ctx.send("Unknown Error")

    async def wait_to_finish (ctx):
        voice_client = ctx.message.guild.voice_client
        while voice_client.is_playing():
            await asyncio.sleep(1)

    @bot.command(name='pause', help='This command pauses the song')
    async def pause(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @bot.command(name='resume', help='Resumes the song')
    async def resume(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")

    @bot.command(name='stop', help='Stops the song')
    async def stop(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main('PyCharm')
