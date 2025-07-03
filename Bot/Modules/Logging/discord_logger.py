from discord import User
from discord.ext.commands import Bot

from Modules.information_manager import InformationManager
from Modules.utils import Utils

import logging


class DiscordLogger(logging.Logger):
    _bot: Bot = None
    
    _has_terminal = Utils.has_terminal()
    _bot_dev: User = None
    
    def __init__(self, name, level = 0, fallback_level = 0):
        self.fallback_level = fallback_level
        super().__init__(name, level)
    
    
    @classmethod
    async def set_bot(cls, bot: Bot):
        cls._bot = bot
        info = InformationManager(bot)
        cls._bot_dev = await info.get_bot_dev()
    
    def setFallbackLevel(self, level: int):
        self.fallback_level = level
    
    def isFallbackEnabledFor(self, level: int):
        return level >= self.fallback_level
    
    def log(self, level, msg, dev_fallback: bool | None = None, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        if DiscordLogger._has_terminal:
            return super().log(level, msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
        
        if dev_fallback is None:
            dev_fallback = self.isFallbackEnabledFor(level)
        
        if dev_fallback and DiscordLogger._bot_dev is not None and DiscordLogger._bot is not None:
            DiscordLogger._bot.loop.create_task(DiscordLogger._bot_dev.send(msg))
    
    
    def info(self, msg, dev_fallback: bool | None = None, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return self.log(logging.INFO, msg, dev_fallback=dev_fallback, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    
    def warning(self, msg, dev_fallback: bool | None = None, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return self.log(logging.WARNING, msg, dev_fallback=dev_fallback, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    
    def debug(self, msg, dev_fallback: bool | None = None, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return self.log(logging.DEBUG, msg, dev_fallback=dev_fallback, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    
    def error(self, msg, dev_fallback: bool | None = None, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return self.log(logging.ERROR, msg, dev_fallback=dev_fallback, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
    
    def critical(self, msg, dev_fallback: bool | None = None, *args, exc_info = None, stack_info = False, stacklevel = 1, extra = None):
        return self.log(logging.CRITICAL, msg, dev_fallback=dev_fallback, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)


_levelValues = logging.getLevelNamesMapping()
def getLevelValue(name: str):
    """
    Retrieve the numeric value associated with a given logging level name.

    Args:
        name (str): The name of the logging level (e.g., 'INFO', 'DEBUG').

    Returns:
        int: The numeric value corresponding to the specified logging level name.

    Raises:
        KeyError: If the provided name does not exist in the _levelValues dictionary.
    """
    return _levelValues[name.upper()]


if __name__ == "__main__":
    DiscordLogger.setup("AutismBOT")
    DiscordLogger.log("Teste bizonho", level=logging.INFO)
    DiscordLogger.log("Teste bizonho", level=logging.ERROR)
    DiscordLogger.log("Teste bizonho", level=logging.DEBUG)
    DiscordLogger.log("Teste bizonho", level=logging.WARNING)
    DiscordLogger.log("Teste bizonho", level=logging.CRITICAL)