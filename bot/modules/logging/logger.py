import logging
from modules.settings.settings import Settings
from modules.reloadable import ReloadableComponent
from modules.logging.formatter import DiscordStyleFormatter
from modules.logging.discord_logger import DiscordLogger, getLevelValue


logger = DiscordLogger("MikuBOT", logging.NOTSET, logging.NOTSET)
"""Global logger instance"""

class _logger_set(ReloadableComponent):
    def __init__(self):
        self.config = Settings("debug")
        self.config.setup(       
            log_level = "INFO",
            fallback_level = "ERROR",
        )
    
    def load(self):
        _handler = logging.StreamHandler()
        _formatter = DiscordStyleFormatter(datefmt='%Y-%m-%d %H:%M:%S')
        _handler.setFormatter(_formatter)
        
        logger.addHandler(_handler)
        
        self.set_level()
        self.set_fallback_level()
    
    def set_level(self):
        log_level_str = self.config.get("log_level")
        log_level_value = getLevelValue(log_level_str)
        logger.setLevel(log_level_value)
        logger.info(f"Set logger level to {log_level_str}")
        
    def set_fallback_level(self):
        log_level_str = self.config.get("fallback_level")
        log_level_value = getLevelValue(log_level_str)
        logger.setFallbackLevel(log_level_value)
        logger.info(f"Set fallback level to {log_level_str}")
    
    def reload(self):
        self.set_level()
        self.set_fallback_level()


_log_config = _logger_set()