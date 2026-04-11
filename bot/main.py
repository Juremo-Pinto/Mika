# main.py

import os, time, resources_path

from modules.utils import Utils

NAME = os.path.join(resources_path.LOCK, 'AutismBOT_LOCK')
lock = Utils.is_duplicate(NAME) # Checks if a instance of Teto is already running in the system

if lock is None: # if it is, exits the program. Makes sure two instances of the same code arent running simultaneously
    print(f"Process is a duplicate, exting...")
    time.sleep(1)
    
    exit()


# Main package import
from discord import Intents
from bot import BotClient

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

#Bot Instantiation
intents = Intents.default() # Discord intents, tells discord what the bot will do 

intents.message_content = True # lets Tato see message contents
intents.members = True # lets Tato see members


has_terminal = Utils.has_terminal() # checks if the code is running with terminal open, if not, enable sending error to the devs DMs.
bot = BotClient( # Custom bot instance, defined on bot.py
    command_prefix=['Acorda ai e ', 'acorda ai e ', '??'], # prefixes
    intents=intents, # the intents
    send_errors_to_developer_dm= not has_terminal, # the send to dev dm thing that worked sometimes
    help_command= None, # no default help command, creates room for a custom one
    case_insensitive=True) # case insensitive because its literally just better

def run():
    bot.run(os.environ['MIKU_DISCORD_TOKEN']) # runs the bot with the secret discord token used to connect the script to the discord servers

if __name__ == '__main__':
    run() # starts the bot