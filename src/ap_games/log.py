import logging
import sys

from ap_games.settings import Settings

__all__ = ('logger',)


settings: Settings = Settings()

file_handler = logging.FileHandler(settings.path_to_log_file)
console_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, console_handler]
file_handler.setLevel(logging.WARNING)
console_handler.setLevel(logging.DEBUG)
logging.basicConfig(
    format='%(message)s',
    level=settings.log_level,
    handlers=handlers,
)

logger = logging.getLogger()
