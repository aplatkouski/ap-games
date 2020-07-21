import logging.handlers
import os
from pathlib import Path

__ALL__ = ["log"]

BASE_DIR = Path(__file__).parent.parent.parent.resolve(strict=True)

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("AP_GAMES_LOGFILE", f"{BASE_DIR}/ap_games.log")
)
log = logging.getLogger()
log.setLevel(os.environ.get("AP_GAMES_LOGLEVEL", "ERROR"))
log.addHandler(handler)
