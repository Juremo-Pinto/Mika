# Mischief/controller.py

import importlib
import inspect
import os
import pkgutil
from typing import Dict
from discord.ext.commands import Cog, Context, Bot
from discord.ext import commands
from discord import Message

from resources_path import BASE_PATH
from mischief.interface import BaseMischief, TextMischief
from Modules.utils import StringTools
from Modules.Logging.logger import logger

def _discover_mischiefs(bot):
    mischiefs = {}
    package_name = "mischief.actions"
    
    import_path = os.path.join(BASE_PATH, "mischief", "actions")
    
    for _, module_name, _ in pkgutil.iter_modules([str(import_path)]):
        module = importlib.import_module(f"{package_name}.{module_name}")
        
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseMischief) and obj is not BaseMischief:
                name = obj.mischief_name or obj.__name__
                
                logger.info(f"Found mischief action: {name}")
                
                mischiefs[name] = obj(bot)
    return mischiefs

class MischiefController(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.mischief_registry: Dict[str, BaseMischief] = _discover_mischiefs(bot)
    
    async def _add_mischiefs_if_cog(self):
        for name, item in self.mischief_registry.items():
            if issubclass(item.__class__, Cog):
                logger.info(f"Loaded mischief action {name} as cog")
                await self.bot.add_cog(item)
    
    def _get_mischiefs(self, *args):
        return [m for m in (self.mischief_registry.get(x) for x in args) if m is not None]
    
    async def cog_load(self):
        await self._add_mischiefs_if_cog()
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    
    @commands.command(name="t_enable")
    async def enable_mischief(self, ctx: Context, *trolling):
        mischife = self._get_mischiefs(*trolling)
        
        if len(mischife) == 0:
            return await ctx.reply("nuh uh")
        
        for item in mischife:
            item.enable()
        
        await ctx.message.add_reaction("<:cat:1264072257433632789>")
    
    
    @commands.command(name="t_disable")
    async def disable_mischief(self, ctx: Context, *trolling):
        mischife = self._get_mischiefs(*trolling)
        
        if len(mischife) == 0:
            return await ctx.reply("nuh uh")
        
        for item in mischife:
            item.disable()
        
        await ctx.message.add_reaction("<:cat:1264072257433632789>")
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        for mischife in self.mischief_registry.values():
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
    await bot.add_cog(MischiefController(bot))