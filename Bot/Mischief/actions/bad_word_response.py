from Modules.utils import StringTools, Utils
from mischief.interface import TextMischief


class BadWordResponse(TextMischief):
    mischief_name = "insulted"
    
    async def check(self, normalized_text, message):
        if normalized_text.startswith(tuple(await self.bot.get_prefix(message))):
            the_big_forbidden_list_of_bad_words = await Utils.get_the_forbidden_list()
            
            return any(bad_word in normalized_text for bad_word in the_big_forbidden_list_of_bad_words)
    
    async def execute(self, normalized_text, message):
        await message.reply("<:spong_bop:1264260742975197264>")