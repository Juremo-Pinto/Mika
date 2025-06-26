from discord.ext.commands import Bot

from Modules.utils import Utils

import logging

"""
# Summon the logger of thine choosing
logger = logging.getLogger('MyBot')  # or __name__, or 'discord' for Discord.py itself

# Prepare the ritual formatting
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt='%(asctime)s %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)

# Bind the spell to the logger
logger.addHandler(handler)
logger.setLevel(logging.INFO)
"""

class Logging:
    _bot: Bot = None
    _has_terminal = Utils.has_terminal()
    
    @classmethod
    def set_bot(cls, bot: Bot):
        cls._bot = bot
    
    
    @staticmethod
    async def log(message: str, dev_fallback: bool):
        pass
    


if __name__ == "__main__":
    pass