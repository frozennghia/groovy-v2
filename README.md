# groovy-v2
replacing the good old groovy discord bot


# How to get started

Install the `ffmpeg.exe` (just google how to get it for your OS)
* This is required for converting videos into sound files
* For macos: `brew install ffmpeg`
* There's a comment to the change the path in groovy_commands.py
  * If you're running this one windows then change `voice_channel.play(discord.FFmpegPCMAudio(executable="/usr/local/bin/ffmpeg", source=filename))` to `voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))`

`pip install -r requirements.txt`
If you run into issues related to pip install `py -m pip install -r requirements.txt`

set `DISCORD_TOKEN` in your environmental variable (search up)

If you run into issues related to SSL run `pip3 install certifi`
