from modules.utils import StringTools, Utils
from mischief.interface import TextMischief


class BadWordResponse(TextMischief):
    mischief_name = "insulted"
    mischief_description = "gets sad"
    
    async def check(self, normalized_text, message):
        prefixes = tuple(await self._bot.get_prefix(message))
        
        if not normalized_text.startswith(prefixes):
            return False
 in       
        the_big_forbidden_list_of_bad_words = Utils.get_the_forbidden_list()
        
        return any(bad_word in normalized_text for bad_word in the_big_forbidden_list_of_bad_words)
    
    async def execute(self, normalized_text, message):
        await message.reply("D:")