from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.player.player import Player

if TYPE_CHECKING:
    from typing import List

__ALL__ = ['HumanPlayer']


class HumanPlayer(Player):
    """HumanPlayer in a game with interaction through the CLI."""

    def go(self) -> Coordinate:
        """Read coordinate of the next step from the input and return it.

        :return: Return :attr:`.SquareGameboard.undefined_coordinate`
         if the coordinate is incorrect.

        """
        input_list: List[str] = input(
            f"Enter the coordinate [{self._label}]: "
        ).split()
        x: str
        y: str
        if len(input_list) >= 2:
            x, y = input_list[:2]
        else:
            x, y = EMPTY, EMPTY
        if x.isdigit() and y.isdigit():
            return Coordinate(int(x), int(y))
        print("You should enter two numbers!")
        return self.game.gameboard.undefined_coordinate
