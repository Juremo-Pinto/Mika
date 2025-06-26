import asyncio
from discord.ext.commands import Bot

from Modules.information_manager import InformationManager
from Modules.utils import Utils

import logging


class Logging:
    _bot: Bot = None
    _logger: logging.Logger = None
    _has_terminal = Utils.has_terminal()
    _info: InformationManager = None
    
    @classmethod
    def setup(cls, logger_name: str | None = None):
        cls._logger = logging.getLogger(logger_name)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Bind the spell to the logger
        cls._logger.addHandler(handler)
        cls._logger.setLevel(logging.INFO)
    
    
    @classmethod
    def set_bot(cls, bot: Bot):
        cls._bot = bot
        cls._info = InformationManager(bot)
    
    
    @staticmethod
    async def log(message: str, dev_fallback: bool = True, level: int = logging.INFO):
        if Logging._logger is None:
            print("No logger present")
            return
        if Logging._has_terminal:
            Logging._logger.log(level, message)
        if dev_fallback and Logging._info is not None:
            dev = await Logging._info.get_bot_dev()
            await dev.send(message)

    


if __name__ == "__main__":
    Logging.setup("Ttests")
    asyncio.run(Logging.log("Teste bizonho"))