# The one teto python file responsible to having a chance to answer cath AND cath SPECIFICALLY with a gif of a horse showing the middle finger

import random
from modules.logging.logger import logger
from modules.settings.settings import Settings
from mischief.interface import TextMischief

from discord.ext.commands import Context, Bot
from discord import Message


class THEHORSEAPPEARS(TextMischief):
    mischief_name = "Xingar a cath fds"
    mischief_description = "Random chance (defined in settings) to send that fuckass dog gif to cath every time he sends a message"

    def __init__(self, bot):
        self.bot = bot
        
        self.settings = Settings("fuck_you_cath", section="mischief")
        self.settings.setup(
                chance = 10,
                user_id = 604384249096699914
            )
    
    def check(self, normalized_text, message):
        if message.author.id != self.settings['user_id']:
            return False
        
        rdn = random.uniform(0, 100)
        logger.debug(f"FUCK cath: chance roll: {rdn}")
        return rdn <= self.settings["chance"]
    
    async def execute(self, normalized_text, message):
        await message.reply("https://tenor.com/bgHlnQoNIGl.gif")