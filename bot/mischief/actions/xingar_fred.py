# The one teto code responsible to having a chance to answer fred AND FRED SPECIFICALLY with a gif of a dog showing the middle finger

import random
from modules.logging.logger import logger
from modules.settings.settings import Settings
from mischief.interface import TextMischief

from discord.ext.commands import Context, Bot
from discord import Message


class CACHORROARROMBADO(TextMischief):
    def __init__(self, bot):
        self.bot = bot
        
        self.settings = Settings("fuck_you_fred", section="mischief")
        self.settings.setup(
                chance = 10,
                user_id = 508268780586139648
            )
    
    def check(self, normalized_text, message):
        if message.author.id != self.settings['user_id']:
            return False
        
        rdn = random.uniform(0, 100)
        logger.debug(f"FUCK FRED: chance roll: {rdn}")
        return rdn <= self.settings["chance"]
    
    async def execute(self, normalized_text, message):
        await message.reply("https://tenor.com/view/cachorro-arrombado-gif-7448837797907435519")