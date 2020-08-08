import logging
import os
import pathlib
import sys

__all__ = ('logger',)

BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve(strict=True)
LOG_LEVEL = os.environ.get('AP_GAMES_LOGLEVEL', 'ERROR')
LOG_FILE = os.environ.get('AP_GAMES_LOGFILE', f'{BASE_DIR}/ap_games.log')


file_handler = logging.FileHandler(LOG_FILE)
console_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, console_handler]
file_handler.setLevel(logging.WARNING)
console_handler.setLevel(logging.DEBUG)
logging.basicConfig(
    format='%(message)s', level=logging.INFO, handlers=handlers,
)

logger = logging.getLogger()
