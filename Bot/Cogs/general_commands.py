import os, discord, resources_path
from typing import List

from discord.ext import commands
from discord.ext.commands import Context

from Modules.utils import StringTools
from Modules.command_permissions import is_moderator
from Modules.Logging.logger import logger

class GeneralCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def cog_load(self):
        logger.info(f"Cog Loaded: {self.__cog_name__}")
    
    @commands.command(name = "repita", aliases = ['repete'])
    async def sendMessage(self, ctx, *, message):
        await ctx.send(message)
        await ctx.message.delete()
    
    
    async def getEmojis(self):
        bot_test_guild_id = 1263933229367562251
        
        main_server = await self.bot.fetch_guild(bot_test_guild_id)
        if main_server:
            emojis = main_server.emojis
        return emojis
    
    
    @commands.command(name = "test")
    async def test(self, ctx):
        #emojis = await self.getEmojis()
        #for x in emojis:
        #    print(f"{x}")
        await ctx.author.send(f"<:trol:968658017086242897>")
    
    
    @commands.command(name = "userid")
    async def getid(self, ctx):
        logger.info(f"user id is: {ctx.author.id}")
    
    
    @commands.command(name = "autista")
    async def sendImage(self, ctx):
        file = discord.File(f"{resources_path.IMAGES}/autismo.jpg", filename="autismo.png")
        await ctx.send(file=file)
        await ctx.message.delete()
    
    
    # Comando de Ajuda
    @commands.command(name = "ayuda", aliases = ['ajuda', 'helpa', 'help'])
    async def help_command(self, ctx: Context, *, args = None):
        reply_messages = await self.get_help_messages(ctx, args)
        
        for message in reply_messages:
            if len(message) != 0:
                await ctx.author.send(message)
    
    
    HELP_TEXT_PATH = os.path.join(resources_path.TEXTS, "Help_message.txt")
    async def get_help_messages(self, ctx: Context, args) -> List[str]:
        help_text = await self.get_help_text(ctx, args)
        help_text = help_text.replace('<prefix> ', (await self.bot.get_prefix(ctx))[0])
        help_text = help_text.split('--NEWMSG--')
        
        return help_text
    
    
    async def get_help_text(self, ctx: Context, args) -> str:
        with open(self.HELP_TEXT_PATH, encoding='UTF-8') as f:
            help_text = f.read()
        
        is_mod = await is_moderator(ctx)
        only_mod = args is not None and 'so mod' in StringTools.normalize_str(args)
        
        if not is_mod:
            return help_text.split('--MODERATORCOMMANDS--')[0]
        
        if only_mod:
            return help_text.split('--MODERATORCOMMANDS--')[1]
        
        return help_text.replace('--MODERATORCOMMANDS--', '--NEWMSG--')



async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCommands(bot))
