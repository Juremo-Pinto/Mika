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
from mischief.interface import BaseMischief, CogMischief, TextMischief
from Modules.utils import StringTools
from Modules.Logging.logger import logger


_interfaces_mod = importlib.import_module("mischief.interface")
_base_classes = set([
    obj
    for _, obj in inspect.getmembers(_interfaces_mod, inspect.isclass) 
    if issubclass(obj, BaseMischief)
    ])


def _discover_class_inheritance_all(cls):
    return [base for base in cls.__mro__ if base in _base_classes]


def _discover_mischiefs(bot):
    _found = {}
    
    package_name = "mischief.actions"
    import_path = os.path.join(BASE_PATH, "mischief", "actions")
    
    for _, module_name, _ in pkgutil.iter_modules([str(import_path)]):
        module = importlib.import_module(f"{package_name}.{module_name}")
        
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseMischief) and obj.__module__ != 'mischief.interface':
                name = obj.mischief_name or obj.__name__
                
                logger.info(f"Found mischief action: {name}")
                
                instance = obj(bot)
                
                for bucket in _discover_class_inheritance_all(obj):
                    _found.setdefault(bucket, {})[name] = instance
    return _found

class MischiefController(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.mischief_registry: Dict[str, BaseMischief] = _discover_mischiefs(bot)
    
    async def _add_cog_mischiefs(self):
        for name, item in self.mischief_registry[CogMischief].items():
            logger.info(f"Loaded mischief action {name} as cog")
            await self.bot.add_cog(item)
    
    def _get_mischiefs(self, *args):
        return [m for m in (self.mischief_registry[BaseMischief].get(x) for x in args) if m is not None]
    
    async def cog_load(self):
        await self._add_cog_mischiefs()
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    
    @commands.command(name="t_enable", aliases=["troll_disable"])
    async def enable_mischief(self, ctx: Context, *trolling):
        mischife = self._get_mischiefs(*trolling)
        
        if len(mischife) == 0:
            return await ctx.reply("nuh uh")
        
        for item in mischife:
            item.is_enable = True
            item.enable()
        
        await ctx.message.add_reaction("<:cat:1264072257433632789>")
    
    
    @commands.command(name="t_disable", aliases=["troll_enable"])
    async def disable_mischief(self, ctx: Context, *trolling):
        mischife = self._get_mischiefs(*trolling)
        
        if len(mischife) == 0:
            return await ctx.reply("nuh uh")
        
        for item in mischife:
            item.is_enable = False
            item.disable()
        
        await ctx.message.add_reaction("<:cat:1264072257433632789>")
    
    
    @commands.command(name="t_list", aliases=["troll_list"])
    async def troll_list(self, ctx):
        message = ""
        
        for key, value in self.mischief_registry[BaseMischief].items():
            pass
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        for mischife in self.mischief_registry[BaseMischief].values():
            await mischife.initiate()
    
    
    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        content = msg.content
        content = StringTools.normalize_str(content)
        
        for text_mischief in self.mischief_registry[TextMischief].values():
            if await text_mischief._validate(content, msg):
                await TextMischief._async_dispatch_func(text_mischief.execute, content, msg)



async def setup(bot: Bot):
    await bot.add_cog(MischiefController(bot))