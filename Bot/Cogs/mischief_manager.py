from typing import Dict
from discord.ext.commands import Cog, Context, Bot
from discord.ext import commands
from discord import Message

from Modules.utils import StringTools
from Modules.enableable import Enableable
from Modules.Logging.logger import logger
from Modules.Mischief.mischief import Mischief

class MischiefManager(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.trolling: Dict[str, Enableable] = {
            "call": Mischief(bot)
        }
    
    def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    @commands.command(name="t_enable")
    async def enable_trol(self, ctx: Context, trolling):
        mischife = self.trolling.get(trolling, None)
        
        if mischife is None:
            return await ctx.reply("nuh uh")
        
        mischife.enable()
        await ctx.message.add_reaction("<:cat:1264072257433632789>")
    
    @commands.command(name="t_disable")
    async def disable_trol(self, ctx: Context, trolling):
        mischife = self.trolling.get(trolling, None)
        
        if mischife is None:
            return await ctx.reply("nuh uh")
        
        mischife.disable()
        await ctx.message.add_reaction("<:cat:1264072257433632789>")
    
    @commands.Cog.listener()
    async def on_ready(self):
        for mischife in self.trolling.values():
            await mischife.initiate()
    
    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        content = msg.content
        content = StringTools.clean(content)
        
        await self.MINIGAMES(msg, content)
    
    # Text Mischief Lmfao
    
    async def MINIGAMES(self, msg: Message, normalized_content: str):
        if 'minigame' in normalized_content:
            await msg.add_reaction("<:MINIGAMES:1400192834073530400>")




async def setup(bot: Bot):
    await bot.add_cog(MischiefManager(bot))