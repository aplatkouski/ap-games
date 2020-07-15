from functools import cached_property
from random import choice

__ALL__ = ['Player']


class Player:
    """Class introduces the player in the game."""

    def __init__(self, type_, /, *, game, label):
        self.type = type_
        self._game = game
        self._label = label

    def __str__(self):
        return self._label

    @cached_property
    def game(self):
        return self._game

    @cached_property
    def label(self):
        return self._label

    def _random_coordinate(self):
        """Return the coordinates of randomly selected available cell on
        the gameboard.

        """
        available_steps = self.game.available_steps()
        if available_steps:
            return choice(available_steps)
        return self.game.gameboard.undefined_coordinate

    def go(self):
        """Return the randomly selected coordinates.

        This method should be overridden by subclasses if there is a
        more complex rule for determining coordinates.

        """
        return self._random_coordinate()
