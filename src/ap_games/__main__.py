from typing import Optional

from ap_games.cli import cli
from ap_games.game.game_base import GameBase
from ap_games.game.reversi import Reversi
from ap_games.game.tictactoe import TicTacToe
from configparser import ConfigParser
from importlib import resources
import sys

from ap_games.log import log


def main() -> None:
    """

    TODO: Add implementation of argparser
    TODO: Import TEST_MODE from config.ini
    """
    cfg = ConfigParser()
    cfg.read_string(
        resources.read_text(package="ap_games", resource="config.ini")
    )
    log_level: str = cfg.get("ap-games", "log_level").upper()
    # test_mode: bool = True if cfg.get(
    #     "ap-games", "test_mode"
    # ).capitalize() == "True" else False
    log.setLevel(
        log_level
        if log_level in ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")
        else "ERROR"
    )

    game: Optional[GameBase] = None
    user_1_type: str = ""
    user_2_type: str = ""
    if len(sys.argv) >= 2:
        game_name: str = sys.argv[1].lower()
        if game_name in ("0", "tic-tac-toe"):
            game = TicTacToe()
        elif game_name in ("1", "reversi"):
            game = Reversi()
    if len(sys.argv) >= 4:
        user_1_type = sys.argv[2]
        user_2_type = sys.argv[3]
    if game is not None:
        game.cli(user_1_type, user_2_type)
    cli()


if __name__ == "__main__":
    main()
