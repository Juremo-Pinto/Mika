from Modules.reloadable import ReloadableComponent
from Modules.enableable import Enableable


class BaseMischief(Enableable, ReloadableComponent):
    mischief_name = None
    bot = None
    
    def _set_bot(self, bot):
        self.bot = bot


class TextMischief(BaseMischief):
    async def validate(self, msg):
        raise NotImplementedError
    
    async def execute(self, validated_msg):
        raise NotImplementedError