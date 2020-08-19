from __future__ import annotations

from configparser import ConfigParser
from importlib import resources
import random
import sys
from typing import NamedTuple
from typing import TYPE_CHECKING

from ap_games.game.reversi import Reversi
from ap_games.game.tictactoe import TicTacToe
from ap_games.log import logger

__all__ = ('main',)


if sys.version_info < (3, 8):
    raise RuntimeError('This package requires Python 3.8+!')


if TYPE_CHECKING:
    from typing import Dict
    from typing import Tuple
    from typing import Type

    from ap_games.ap_types import OptionalPlayerTypes
    from ap_games.game.game_base import TwoPlayerBoardGame


TEST_MODE: bool = False


class Game(NamedTuple):
    """Game(name: str, game_class: Type[TwoPlayerBoardGame])."""

    name: str
    game_class: Type[TwoPlayerBoardGame]


supported_games: Dict[str, Game] = {
    '1': Game(name='Tic-Tac-Toe', game_class=TicTacToe),
    '2': Game(name='Reversi', game_class=Reversi),
}


def main() -> None:
    """Aks user about desired game and run it."""
    choice: str
    player_types: OptionalPlayerTypes

    read_config()
    if TEST_MODE:
        run_test_mode_and_exit()
    choice, player_types = read_argv()
    games: str = ";\n\t".join(
        f'{num} - {game.name}' for num, game in supported_games.items()
    )
    message: str = (
        f'Please choose the game:\n\t{games}.\n'
        'Print "exit" to exit the program.\n\nInput command: '
    )
    while choice != 'exit':
        if choice in supported_games:
            logger.debug(f'{choice=}')
            game: TwoPlayerBoardGame = supported_games[choice].game_class()
            game.cli(player_types=player_types)
        logger.info(message)
        choice = sys.stdin.readline().strip()


def read_config() -> None:
    """Read the log level from the config.ini and set it."""
    cfg = ConfigParser()
    cfg.read_string(
        resources.read_text(package='ap_games', resource='config.ini')
    )
    log_level: str = cfg.get('ap-games', 'log_level').upper()
    logger.setLevel(log_level if log_level == 'DEBUG' else 'INFO')
    global TEST_MODE
    TEST_MODE = cfg.getboolean('ap-games', 'test_mode')


def run_test_mode_and_exit() -> None:
    """Run the predefined configuration if ``TEST_MODE=True`` and exit."""
    random.seed(42)
    logger.debug(f'{TEST_MODE=}')
    game: TwoPlayerBoardGame = Reversi(player_types=('medium', 'hard'))
    game.play()
    game = TicTacToe(player_types=('easy', 'hard'))
    game.play()
    sys.exit()


def read_argv() -> Tuple[str, OptionalPlayerTypes]:
    """Read command-line arguments and return them.

    :returns: Two-element tuple, where:

        * ``game_num`` - a value from ``supported_games.keys()`` or
            empty string;
        * ``player_types`` - a two-element tuple, where each element is
          a player-type string or empty tuple.

    """
    sys.argv.pop(0)
    game_num: str = ''
    player_types: OptionalPlayerTypes = ()
    if len(sys.argv) >= 1:
        game_num = sys.argv[0]
        game_num = game_num.title()
        for num, game in supported_games.items():
            game_num = game_num.replace(game.name, num)
        if len(sys.argv) >= 3:
            player_types = (sys.argv[1], sys.argv[2])
    return (game_num, player_types)


if __name__ == '__main__':
    main()
