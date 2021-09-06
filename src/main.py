import os
from commands import groovy_commands


def main():
    discord_token = os.getenv('DISCORD_TOKEN')
    bot = groovy_commands.bot
    bot.run(discord_token)


if __name__ == '__main__':
    main()
