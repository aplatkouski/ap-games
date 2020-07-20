import logging.handlers
import os

__ALL__ = ["log"]

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("AP_GAMES_LOGFILE", "./ap_games.log")
)
log = logging.getLogger()
log.setLevel(os.environ.get("AP_GAMES_LOGLEVEL", "ERROR"))
log.addHandler(handler)
