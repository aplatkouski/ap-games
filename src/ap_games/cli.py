from __future__ import annotations

from configparser import ConfigParser
from importlib import resources
import random
import sys
from typing import cast
from typing import NamedTuple
from typing import TYPE_CHECKING

from ap_games.ap_typing import PlayerType
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
    from typing import Union

    from ap_games.game.game_base import TwoPlayerBoardGame


class Game(NamedTuple):
    """Game(name: str, game_class: Type[TwoPlayerBoardGame])."""

    name: str
    game_class: Type[TwoPlayerBoardGame]


class Settings:
    config_file: str = 'config.ini'
    supported_games: Dict[str, Game] = {
        '1': Game(name='Tic-Tac-Toe', game_class=TicTacToe),
        '2': Game(name='Reversi', game_class=Reversi),
    }
    test_mode: bool = False
    log_level: str = 'INFO'


def main() -> None:
    """Aks user about desired game and run it."""
    choice: str
    player_types: Union[Tuple[str, str], Tuple[()]]

    read_config()
    logger.setLevel(Settings.log_level)
    if Settings.test_mode:
        run_test_mode_and_exit()
    choice, player_types = read_argv()
    games_menu: str = ";\n\t".join(
        f'{num} - {game.name}'
        for num, game in Settings.supported_games.items()
    )
    message: str = (
        f'Please choose the game:\n\t{games_menu}.\n'
        'Type "exit" to exit the program.\n\nInput command: '
    )
    while choice != 'exit':
        if choice in Settings.supported_games:
            logger.debug(f'{choice=}')
            game: TwoPlayerBoardGame = Settings.supported_games[
                choice
            ].game_class()
            game.cli(player_types=player_types)
        logger.info(message)
        choice = sys.stdin.readline().strip()


def read_config() -> None:
    """Read the log level from the config.ini and set it."""
    cfg = ConfigParser()
    cfg.read_string(
        resources.read_text(package='ap_games', resource=Settings.config_file)
    )
    log_level: str = cfg.get('ap-games', 'log_level').upper()
    Settings.log_level = log_level if log_level == 'DEBUG' else 'INFO'
    Settings.test_mode = cfg.getboolean('ap-games', 'test_mode')


def run_test_mode_and_exit() -> None:
    """Run the predefined configuration when ``test_mode=True`` and exit."""
    random.seed(42)
    logger.debug(f'{Settings.test_mode=}')
    game: TwoPlayerBoardGame = Reversi(
        player_types=(cast(PlayerType, 'medium'), cast(PlayerType, 'hard'))
    )
    game.play()
    game = TicTacToe(
        player_types=(cast(PlayerType, 'easy'), cast(PlayerType, 'hard'))
    )
    game.play()
    sys.exit()


def read_argv() -> Tuple[str, Union[Tuple[str, str], Tuple[()]]]:
    """Read command-line arguments and return them.

    :returns: Two-element tuple, where:

        * ``selected_game`` - a value from ``supported_games.keys()`` or
          empty string;
        * ``player_types`` - an empty or two-element tuple, where each
          element is the player's desired type.

    """
    sys.argv.pop(0)
    selected_game: str = ''
    player_types: Union[Tuple[str, str], Tuple[()]] = ()
    if len(sys.argv) >= 1:
        selected_game = sys.argv[0]
        selected_game = selected_game.title()
        for num, game in Settings.supported_games.items():
            selected_game = selected_game.replace(game.name, num)
        if len(sys.argv) >= 3:
            player_types = (sys.argv[1], sys.argv[2])
    return (selected_game, player_types)


if __name__ == '__main__':
    main()
