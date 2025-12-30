# main.py

import os, time, resources_path

from Modules.utils import Utils

NAME = os.path.join(resources_path.LOCK, 'AutismBOT_LOCK')
lock = Utils.is_duplicate(NAME)

if lock is None:
    print(f"Process is a duplicate, exiting...")
    time.sleep(1)
    exit()


# Main package import
from discord import Intents
from bot import BotClient

from dotenv import load_dotenv

load_dotenv()

from keep_alive import keep_alive

keep_alive()

#Bot Instantiation
intents = Intents.default()

intents.message_content = True
intents.members = True


has_terminal = Utils.has_terminal()
bot = BotClient(
    command_prefix=['aproveita e ', 'Aproveita e ', '!!'], 
    intents=intents,
    send_errors_to_developer_dm= not has_terminal,
    help_command= None, 
    case_insensitive=True)

def run():
    bot.run(os.environ['TETO_DISCORD_TOKEN'])

if __name__ == '__main__':
    run()