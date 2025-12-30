from typing import Any
from discord.ext import commands
from discord.ext.commands import Context
from Modules.Logging.discord_logger import DevFallback
from Modules.command_permissions import developer
from Modules.Logging.logger import logger

class DevOnlyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    @commands.command(name = "desliga", aliases=["sybau", "morra", "morre"])
    @developer()
    async def turn_off_bot(self, ctx: Context[Any]):
        await ctx.send("ok tchau")
        await self.bot.close()
    
    @commands.command(name = "emoji")
    async def get_emoji(self, ctx: Context, emoji: str):
        logger.info(f"Requested emogi: {emoji}", dev_fallback= DevFallback.YES_IF_NO_TERMINAL)
    
    #@commands.command(name = "idget")
    #async def get_user_id(self, ctx):
    #    print(ctx.author.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(DevOnlyCommands(bot))