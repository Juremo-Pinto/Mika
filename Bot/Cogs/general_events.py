from discord import Message
from discord.ext import commands
from Modules.Logging.logger import logger
from Modules.utils import StringTools, Utils
from Modules.information_manager import InformationManager
from Modules.database_manager import DatabaseManager

class GeneralEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.database = DatabaseManager()
        self.info = InformationManager(self.bot)
    
    async def cog_load(self):   
        await self.database.setup(structure={
            'storedLocations': {
                'channel_ID': 'INTEGER',
                'server_ID': 'INTEGER',
                'general_ID': 'INTEGER'
            }
        })
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        fetch_locations_query = "SELECT channel_ID, server_ID FROM storedLocations WHERE general_ID = 0"
        locations_data = await self.database.fetchall(fetch_locations_query)
        
        for location_record in locations_data:
            marked_server = self.bot.get_guild(location_record[1])
            greetings_channel = self.bot.get_channel(location_record[0])
            
            if greetings_channel:
                await greetings_channel.send("Boa tarde")
                logger.info(f"Startup message sent to marked channel: {marked_server.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralEvents(bot))