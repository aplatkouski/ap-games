from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from ap_games.ap_types import Coordinate
from ap_games.log import logger
from ap_games.player.player import Player

if TYPE_CHECKING:
    from typing import List

__all__ = ('HumanPlayer',)


class HumanPlayer(Player):
    """HumanPlayer in a game with interaction through the CLI."""

    def move(self) -> Coordinate:
        """Read coordinate of the next move from the input and return it.

        :returns: Return :attr:`.SquareGameboard.undefined_coordinate`
            if the coordinate is incorrect.

        """
        logger.info(f'Enter the coordinate [{self._mark}]: ')
        input_list: List[str] = sys.stdin.readline().strip().split()
        logger.debug(f'{input_list=}')
        if len(input_list) >= 2:
            column, row = input_list[:2]
            if column.isdigit() and row.isdigit():
                return Coordinate(int(column), int(row))
        logger.warning('You should enter two numbers!')
        return self.game.gameboard.undefined_coordinate
