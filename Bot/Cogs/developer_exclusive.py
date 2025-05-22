from nextcord.ext import commands
from Modules.command_permissions import developer

class dev_exclusive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name = "desliga")
    @developer()
    async def turn_off_bot(self, ctx):
        await ctx.send("ok tchau")
        await self.bot.close()
        print('Desligando')
    
    #@commands.command(name = "idget")
    #async def get_user_id(self, ctx):
    #    print(ctx.author.id)


def setup(bot: commands.Bot):
    bot.add_cog(dev_exclusive(bot))