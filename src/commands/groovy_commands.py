import asyncio

import discord
from discord.ext import commands

from discord.ext.commands import bot

from src.youtube_wrap import yt_wrapper

intents = discord.Intents().all()
bot = commands.Bot(command_prefix="-", intents=intents)
bot.is_connected = False
bot.song_queue = asyncio.Queue()
bot.current_song = ''


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


@bot.command(name='leave', help='Leave the channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        bot.is_connected = False
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play', help='Play song')
async def queue_play(ctx, *args, is_skipped=False):
    url = ' '.join(args)
    await join(ctx)
    if not is_skipped:
        bot.song_queue.put_nowait([ctx, url])
    if is_currently_playing(ctx):
        await ctx.send('Queued {}'.format(url))
        return
    while not bot.song_queue.empty():
        next_song = await bot.song_queue.get()
        bot.current_song = next_song[1]  # changed
        await asyncio.create_task(play(next_song[0], next_song[1]))


async def play(ctx, song_url):
    bot.current_song = song_url
    voice_client = ctx.message.guild.voice_client
    if ctx.message.author.voice and not voice_client.is_playing():
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await yt_wrapper.YTDLSource.from_url(song_url, loop=bot.loop)
            # this line only works for mac, will need to change the path to the ffmpeg executable for windows
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        await ctx.send('**Now playing:** {}'.format(format_song_name(filename)))
        await wait_to_finish(ctx)
    else:
        await ctx.send("Unknown Error")


def format_song_name(song_name):
    raw_list = song_name.split('_')
    return ' '.join(raw_list[:len(raw_list) - 2])


async def wait_to_finish(ctx):
    voice_client = ctx.message.guild.voice_client
    while voice_client.is_playing():
        await asyncio.sleep(1)


@bot.command(name='skip', help='Skips the current song that is playing')
async def skip(ctx):
    if is_currently_playing(ctx):
        await stop(ctx)
        asyncio.create_task(queue_play(ctx, "", is_skipped=True))


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


def is_currently_playing(ctx):
    voice_client = ctx.message.guild.voice_client
    return voice_client.is_playing()


@bot.command(name='list', help='Lists all songs')
async def list_songs(ctx):
    if bot.song_queue.empty():
        await ctx.send('No songs in list!\n')
        return
    result_string = 'Song List:\n1: {}\n'.format(bot.current_song)
    for i in range(bot.song_queue.qsize()):
        song = await bot.song_queue.get()
        result_string += str(i + 2)
        result_string += ': '
        result_string += song[1]
        result_string += '\n'
        bot.song_queue.put_nowait(song)
    await ctx.send(result_string)
