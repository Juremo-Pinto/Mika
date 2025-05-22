# main.py

import os, time
from Modules.utils import Utils
from resources_path import resources_path

NAME = os.path.join(resources_path('lock'), 'AutismBOT_LOCK')
lock = Utils.is_duplicate(NAME)

if lock is None:
    print(f"Process is a duplicate, exiting...")
    time.sleep(1)
    exit()

# general imports
import asyncio

# Main package import
from nextcord import Intents
from nextcord.ext import commands

# other files import
from Modules.database_manager import DatabaseManager
from Modules.mischief import Mischief
from Modules.command_permissions import Permission, is_user_role_tagged


#Bot Initialization
intents = Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=['aproveita e '], intents=intents, help_command= None, case_insensitive=True)
bot.loop.create_task(Permission.database_init())


i_am_afraid = Mischief(bot,
    servers_with_tomfoolery_present= [
        "Whatsapp 2",
        "Bot Testing Ground",
        "VILA DO CHAVES"
        ],
    chance_denominator=110,
    interval_in_seconds = 12
    )


# cog importing
#bot.load_extension('Modules.command_manipulation.shared_command_system')
#bot.load_extension('Cogs.test')

bot.load_extension('Cogs.developer_exclusive')
bot.load_extensions([
    'Cogs.general_commands',
    'Cogs.general_events',
    'Cogs.voice_channel',
    'Cogs.community_notepad',
    'Cogs.youtube_playback.youtube_playback',
    'Cogs.text_channel_selection',
    'Cogs.mass_message_deletion',
    'Cogs.role_tag_controller'
    ])



@bot.event
async def on_ready():
    print(f"Bot is online! Username: {bot.user.name} | ID: {bot.user.id}")
    print("Connected to the following guilds:")
    for guild in bot.guilds:
        print(f" - {guild.name} (ID: {guild.id})")
    
    await i_am_afraid.commence_moderate_mischief()


@bot.event
async def on_message(msg):
    if msg.content.startswith(tuple(await bot.get_prefix(msg))) and await is_user_role_tagged(msg, 'forbid_BOT'):
        print(f'Blacklisted user "{msg.author.name}" tried using bot in {msg.guild.name}, {msg.channel.name}')
        return
    
    await bot.process_commands(msg)


async def cleanup():
    await i_am_afraid.QUIT_HAVING_FUN()
    await DatabaseManager.disconnect_all()


if __name__ == '__main__':
    bot.run(os.environ['AUTISM_DISCORD_TOKEN'])
    asyncio.run(cleanup())
    print("Shutted down lmao")
    exit()