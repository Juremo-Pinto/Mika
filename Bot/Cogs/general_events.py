import asyncio
import signal
from nextcord.ext import commands
from Modules.utils import Utils
from Modules.information_manager import InformationManager
from Modules.database_manager import DatabaseManager

class GeneralEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = DatabaseManager()
        self.info = InformationManager(self.bot)
    
    
    def shutdown_request(self, signal_received, frame):
        self.bot.loop.create_task(DatabaseManager.disconnect_all())
        self.bot.loop.create_task(self.bot.close())
    
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if str.lower(message.content) == 'fat fuck' and message.author.id != self.bot.user.id:
            await message.channel.send(message.content)
    
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if await Utils.has_terminal():
            raise error
        
        dev = await self.info.get_bot_dev()
        
        if dev:
            await dev.send(f'Error in {ctx.guild.name}:\n{error}')
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.database.setup(structure={
            'storedLocations': {
                'channel_ID': 'INTEGER',
                'server_ID': 'INTEGER',
                'general_ID': 'INTEGER'
            }
        })
        
        fetch_locations_query = "SELECT channel_ID, server_ID FROM storedLocations WHERE general_ID = 0"
        locations_data = await self.database.fetchall(fetch_locations_query)
        
        for location_record in locations_data:
            marked_server = self.bot.get_guild(location_record[1])
            greetings_channel = self.bot.get_channel(location_record[0])
            
            if greetings_channel:
                await greetings_channel.send("Boa tarde")
                print(f"Mensage mandada em: {marked_server.name}")
            else:
                print(f'O servidor {marked_server.name} não possue nenhum canal de "boas vindas"')


def setup(bot):
    cog = GeneralEvents(bot)
    
    signal.signal(signal.SIGTERM, cog.shutdown_request)
    signal.signal(signal.SIGINT, cog.shutdown_request)
    
    bot.add_cog(cog)