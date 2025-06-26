import logging


class DiscordStyleFormatter(logging.Formatter):
    RESET = "\033[0m"
    DIM = "\033[2m"
    BOLD = "\033[1m"

    COLORS = {
        "DEBUG": "\033[0;96m",     # Cyan
        "INFO": "\033[34m",      # Blue
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[41m",  # Red background
    }

    NAME_COLOR = "\033[35m"  # Purple/magenta
    TIME_COLOR = "\033[90m"  # Dim gray

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, "")
        timestamp = f"{self.TIME_COLOR}{self.formatTime(record, self.datefmt)}{self.RESET}"
        levelname = f"{level_color}{record.levelname:<8}{self.RESET}"
        name = f"{self.NAME_COLOR}{record.name}{self.RESET}"

        return f"{timestamp} {levelname} {name} {record.getMessage()}"