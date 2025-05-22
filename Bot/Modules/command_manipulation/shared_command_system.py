import functools
from nextcord.ext import commands

from Modules.utils import IterTools, StringTools

#EXTREMELY WIP IT MIGHT NOT EVEN WORK LMAO
#SOME THINGS WERE BROUGHT UP TO MY ATTENTION AND NOW IT MIGHT HAVE THE SMALLEST CHANCE OF WORKING

class SharedCommand(commands.Cog):
    _to_register: set = set()
    
    _group: set = set()
    _bot: commands.bot.Bot = None
    
    def __init__(self, bot):
        self.bot: commands.bot.Bot = bot
        
        if SharedCommand._bot is None:
            SharedCommand._bot = bot
    
    
    @classmethod
    def register():
        pass
    
    
    @classmethod
    def find(word, layer):
        pass
    
    
    def dispatch(self, *full_command, **command_kwargs):
        """Be cautious for the first word of the name, make sure none of them conflict with an regular nextcord command."""
        if not full_command:
            raise ValueError("At least one command name must be provided")
        
        full_command = IterTools.for_each_item(
            full_command,
            StringTools.clean,
            lambda phrase: phrase.split(' ')
        )
        
        def decorator(func):
            group_name = full_command[0][0]
            is_registered = self.bot.get_command(group_name)
            
            print(f"Decorador chamado para função: {func.__name__} (comando: '{group_name}')")
            
            if is_registered:
                return
            
            @commands.command(name = group_name)
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return decorator




def setup(bot):
    bot.add_cog(SharedCommand(bot))