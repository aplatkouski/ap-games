from ap_games.player.player import Player
from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY

__ALL__ = ['HumanPlayer']


class HumanPlayer(Player):
    """HumanPlayer class introduces the user in the game with the
    ability to interact through the CLI.

    """

    def go(self) -> Coordinate:
        """Read coordinate from the input and return them.

        :return: Return :attr:`.SquareGameboard.undefined_coordinate`
         if the coordinate is incorrect.

        """
        input_list = input(f"Enter the coordinate [{self._label}]: ").split()
        if len(input_list) >= 2:
            x, y = input_list[:2]
        else:
            x, y = EMPTY, EMPTY
        if x.isdigit() and y.isdigit():
            return Coordinate(int(x), int(y))
        print("You should enter two numbers!")
        return self.game.gameboard.undefined_coordinate
