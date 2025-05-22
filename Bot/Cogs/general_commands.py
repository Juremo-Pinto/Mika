import os, nextcord

from nextcord.ext import commands
from resources_path import resources_path
from Modules.command_permissions import is_moderator

class GeneralCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    
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
    
    
    @commands.command(name = "autista")
    async def sendImage(self, ctx):
        file = nextcord.File(f"{resources_path('image')}/autismo.jpg", filename="autismo.png")
        await ctx.send(file=file)
        await ctx.message.delete()
    
    
    # Comando de Ajuda
    @commands.command(name = "ayuda", aliases = ['ajuda', 'helpa', 'help'])
    async def test(self, ctx, *, args = None):
        help_text_file_path = os.path.join(resources_path('text'), "Help_message.txt")
        is_mod = await is_moderator(ctx)
        only_mod = args is not None and 'só mod' in args.lower()
        
        with open(help_text_file_path, encoding='UTF-8') as f:
            help_text = f.read()
            help_text = await self.get_help_text(help_text, is_mod, only_mod)
            help_text = help_text.replace('<prefix> ', (await self.bot.get_prefix(ctx))[0])
            help_text = help_text.split('--NEWMSG--')
            
            for paragraph in help_text:
                paragraph = paragraph.strip()
                
                if len(paragraph) != 0:
                    await ctx.author.send(paragraph)
    
    
    async def get_help_text(self, help_text, is_mod, only_mod):
        if not is_mod:
            return help_text.split('--MODERATORCOMMANDS--')[0]
        
        if only_mod:
            return help_text.split('--MODERATORCOMMANDS--')[1]
        
        return help_text.replace('--MODERATORCOMMANDS--', '--NEWMSG--')



def setup(bot):
    bot.add_cog(GeneralCommands(bot))
