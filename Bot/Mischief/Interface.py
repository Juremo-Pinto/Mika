from Modules.reloadable import ReloadableComponent
from Modules.enableable import Enableable
from discord.ext.commands import Cog

class BaseMischief(Enableable, ReloadableComponent):
    mischief_name = None
    bot = None
    
    def __init__(self, bot):
        self.bot = bot
    
    def _set_bot(self, bot):
        if self.bot is None:
            self.bot = bot


class TextMischief(BaseMischief):
    async def validate(self, msg):
        raise NotImplementedError
    
    async def execute(self, validated_msg):
        raise NotImplementedError


class CogMischief(BaseMischief, Cog):
    pass