from __future__ import annotations

import random
import sys
from typing import cast
from typing import TYPE_CHECKING

from ap_games.ap_collections import Game
from ap_games.ap_typing import PlayerType
from ap_games.game.reversi import Reversi
from ap_games.game.tictactoe import TicTacToe
from ap_games.log import logger
from ap_games.settings import Settings

__all__ = ('main',)


if sys.version_info < (3, 8):
    raise RuntimeError('This package requires Python 3.8+!')


if TYPE_CHECKING:
    from typing import Dict
    from typing import Tuple
    from typing import Union

    from ap_games.game.game_base import TwoPlayerBoardGame


def main() -> None:
    """Aks user about desired game and run it."""
    choice: str
    player_types: tuple[str, str] | tuple[()]

    settings: Settings = Settings()
    if settings.test_mode:
        run_test_mode_and_exit(settings)

    supported_games: dict[str, Game] = {
        '1': Game(name='Tic-Tac-Toe', game_class=TicTacToe),
        '2': Game(name='Reversi', game_class=Reversi),
    }
    choice, player_types = read_argv(supported_games)

    games_menu: str = ";\n\t".join(
        f'{num} - {game.name}' for num, game in supported_games.items()
    )
    message: str = (
        f'Please choose the game:\n\t{games_menu}.\n'
        'Type "exit" to exit the program.\n\nInput command: '
    )
    while choice != 'exit':
        if choice in supported_games:
            logger.debug(f'{choice=}')
            game: TwoPlayerBoardGame = supported_games[choice].game_class()
            game.cli(player_types=player_types)
        player_types = ()
        logger.info(message)
        choice = sys.stdin.readline().strip()


def run_test_mode_and_exit(settings: Settings) -> None:
    """Run the predefined configuration when ``test_mode=True`` and exit.

    :param settings: instance of :class:`Settings`.

    """
    random.seed(42)
    logger.debug(f'{settings.test_mode=}')
    game: TwoPlayerBoardGame = Reversi(
        player_types=(cast(PlayerType, 'medium'), cast(PlayerType, 'hard'))
    )
    game.play()
    game = TicTacToe(
        player_types=(cast(PlayerType, 'easy'), cast(PlayerType, 'hard'))
    )
    game.play()
    sys.exit()


def read_argv(
    supported_games: dict[str, Game]
) -> tuple[str, tuple[str, str] | tuple[()]]:
    """Read command-line arguments and return them.

    :param supported_games: A ``dict`` where the key is the game number
        and the value is an instance of :class:`Game`

    :returns: Two-element tuple, where:

        * ``selected_game`` - a value from ``supported_games.keys()`` or
          empty string;
        * ``player_types`` - an empty or two-element tuple, where each
          element is the player's desired type.

    """
    sys.argv.pop(0)
    selected_game: str = ''
    player_types: tuple[str, str] | tuple[()] = ()
    if len(sys.argv) >= 1:
        selected_game = sys.argv[0]
        selected_game = selected_game.title()
        for num, game in supported_games.items():
            selected_game = selected_game.replace(game.name, num)
        if len(sys.argv) >= 3:
            player_types = (sys.argv[1], sys.argv[2])
    return (selected_game, player_types)


if __name__ == '__main__':
    main()
