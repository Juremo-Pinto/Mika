# main.py

# general imports
import os

# Main package import
from nextcord import Intents
from nextcord.ext import commands

# other files import
from Modules.information_manager import InformationManager
from Modules.database_manager import DatabaseManager
from Modules.mischief import Mischief
from Modules.command_permissions import RolePermissionHandler
from resources_path import ResourcesPath

#Bot Initialization
intents = Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=['aproveita e ', 'Aproveita e '], intents=intents)

# class instantiation
resources = ResourcesPath()
info_manager = InformationManager(bot)
database = DatabaseManager()
bot_usage_permission = RolePermissionHandler('forbid_BOT')

i_am_afraid = Mischief(bot,
    servers_with_tomfoolery_present= [
        "Whatsapp 2",
        "Bot Testing Ground",
        "VILA DO CHAVES"
        ],
    playable_audio_list_path= os.listdir(resources('audio')),
    chance_denominator=100,
    interval_in_seconds = 10
    )


# cog importing
bot.load_extensions([
    'Cogs.general_commands',
    'Cogs.general_events',
    'Cogs.voice_channel',
    'Cogs.community_notepad',
    'Cogs.youtube_playback.youtube_playback',
    'Cogs.text_channel_selection',
    'Cogs.mass_message_deletion',
    'Cogs.role_tag_controller',
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
    if msg.content.startswith(tuple(await bot.get_prefix(msg))) and await bot_usage_permission.is_user_role_tagged(msg):
        print(f'Blacklisted user "{msg.author.name}" tried using bot in {msg.guild.name}, {msg.channel.name}')
        return
    
    await bot.process_commands(msg)

if __name__ == '__main__':
    bot.run(os.environ['DISCORD_TOKEN'])
