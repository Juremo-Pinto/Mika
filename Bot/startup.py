from discord.ext import commands
from discord.ext.commands import Context

from Modules.reloadable import ReloadableComponent
from Modules.settings import Settings
from Modules.Logging.logger import logger
from Modules.Mischief.mischief import Mischief
from Modules.database_manager import DatabaseManager
from Modules.command_permissions import Permission, developer

class startup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def _object_startup(self):
        await logger.set_bot(self.bot)
        
        self.fnuuy = Mischief(self.bot)
    
    
    async def cog_load(self):
        await self._object_startup()
        
        await DatabaseManager.connect()
        logger.info("DatabaseManager: Database has Connected")
        
        await Permission.database_init()
        logger.info("Permission: Permission database has been Setup")
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Bot is online! Username: {self.bot.user.name} | ID: {self.bot.user.id}")
        logger.info("Connected to the following guilds:")
        for guild in self.bot.guilds:
            logger.info(f" - {guild.name} (ID: {guild.id})")
        
        await self.fnuuy.commence_moderate_mischief()
    
    
    @commands.command(name="reload")
    @developer()
    async def reload(self, ctx: Context):
        '''
        Reloads internal bot components or configurations.
        
        Intended for development and debugging purposes. The exact behavior of
        this command depends on the implementation — it may reload modules,
        refresh settings, update caches, or apply recent code changes.
        '''
        await ctx.author.send("Reloading...")
        
        logger.info("Reloading bot configurations", dev_fallback=True)
        Settings.reload()
        
        ReloadableComponent.reload_all_instances()


async def setup(bot: commands.Bot):
    await bot.add_cog(startup(bot))
