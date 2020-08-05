from __future__ import annotations

from configparser import ConfigParser
from importlib import resources
import sys
from typing import TYPE_CHECKING

from ap_games.game.reversi import Reversi
from ap_games.game.tictactoe import TicTacToe
from ap_games.log import logger
from ap_games.player.player import TEST_MODE

__ALL__ = ('main',)


if sys.version_info < (3, 8):
    raise RuntimeError('This package requires Python 3.8+!')


if TYPE_CHECKING:
    from typing import Optional

    from ap_games.game.game_base import TwoPlayerBoardGame


def read_config() -> None:
    """Read config and argv params and pass them to ``cli`` of the game.

    TODO: Add implementation of argparser or click
    TODO: Import TEST_MODE from config.ini

    """
    cfg = ConfigParser()
    cfg.read_string(
        resources.read_text(package='ap_games', resource='config.ini')
    )
    log_level: str = cfg.get('ap-games', 'log_level').upper()
    logger.setLevel(log_level if log_level == 'DEBUG' else 'INFO')

    game: Optional[TwoPlayerBoardGame] = None
    user1_type: str = ''
    user2_type: str = ''
    if len(sys.argv) >= 2:
        game_name: str = sys.argv[1].lower()
        if game_name in {'0', 'tic-tac-toe'}:
            game = TicTacToe()
        elif game_name in {'1', 'reversi'}:
            game = Reversi()
    if len(sys.argv) >= 4:
        user1_type = sys.argv[2]
        user2_type = sys.argv[3]
    if game is not None:
        game.cli(user1_type, user2_type)


def main() -> None:
    """Aks user about desired game and run it."""
    read_config()
    choice: str = ''
    while choice != 'exit':
        if TEST_MODE:
            choice = '1'
        else:
            logger.info(
                'Please choose the game:\n\t0 - Tic-Tac-Toe;\n\t1 - Reversi.\n'
                'Print "exit" to exit the program.\n\nInput command: '
            )
            choice = sys.stdin.readline().strip()
        logger.debug(f'{choice=}')
        if choice == '0':
            TicTacToe.cli()
        elif choice == '1':
            Reversi.cli()
        if TEST_MODE:
            choice = 'exit'


if __name__ == '__main__':
    main()
