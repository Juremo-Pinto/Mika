import re

from modules.utils import StringTools, Utils
from mischief.interface import TextMischief


class prefixError(TextMischief):
    mischief_name = "insult"
    mischief_description = "makes people realize how stupid they are for misstyping the prefix"
    
    async def check(self, normalized_text:str, message):
        unprefixes = tuple(await self._bot.get_prefix(message))
        
        if normalized_text.startswith("acorda ai e") and not any(message.content.startswith(prefix) for prefix in unprefixes):
            return True
        pattern = r"^acorda\w?\s?ai\w?\s?e\w?\s?"
        return not normalized_text.startswith("acorda ai e ") and re.search(pattern, normalized_text) is not None
     
    async def execute(self, normalized_text, message):
        await message.reply("You just got the prefix wrong dude...")