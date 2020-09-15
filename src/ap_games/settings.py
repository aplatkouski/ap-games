from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.ap_collections import Game
from ap_games.game.reversi import Reversi
from ap_games.game.tictactoe import TicTacToe

if TYPE_CHECKING:
    from typing import Dict

__all__ = ('Settings',)


class Settings:
    """Class introduces the settings of the `ap_games` module."""

    config_file: str = 'config.ini'
    supported_games: Dict[str, Game] = {
        '1': Game(name='Tic-Tac-Toe', game_class=TicTacToe),
        '2': Game(name='Reversi', game_class=Reversi),
    }
    test_mode: bool = False
    log_level: str = 'INFO'
