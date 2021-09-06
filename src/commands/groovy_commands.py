import asyncio

import discord
from discord.ext import commands

from youtube_wrap import yt_wrapper
from discord.ext.commands import bot

intents = discord.Intents().all()
song_queue = asyncio.Queue()
bot = commands.Bot(command_prefix="-", intents=intents)
bot.is_connected = False

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        if bot.is_connected:
            return
        channel = ctx.message.author.voice.channel
    await channel.connect()
    bot.is_connected = True


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
            filename = await yt_wrapper.YTDLSource.from_url(song_url, loop=bot.loop)
            # this line only works for mac, will need to change the path to the ffmpeg executable for windows
            voice_channel.play(discord.FFmpegPCMAudio(executable="/usr/local/bin/ffmpeg", source=filename))
        await ctx.send('**Now playing:** {}'.format(filename))
        await wait_to_finish(ctx)
    else:
        await ctx.send("Unknown Error")


async def wait_to_finish(ctx):
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
