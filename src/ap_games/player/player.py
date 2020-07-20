from functools import cached_property
from random import choice as random_choice
import random

TEST_MODE = False

__ALL__ = ["Player", "TEST_MODE"]

if TEST_MODE:
    random.seed(123)


class Player:
    """Class introduces the player in the game."""

    def __init__(self, type_, /, *, game, label):
        self._type = type_
        self._game = game
        self._label = label

    def __str__(self):
        return self._label

    @cached_property
    def type(self):
        return self._type

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
        return (
            random_choice(available_steps)
            if available_steps
            else self.game.gameboard.undefined_coordinate
        )

    def go(self):
        """Return the randomly selected coordinates.

        This method should be overridden by subclasses if there is a
        more complex rule for determining coordinates.

        """
        return self._random_coordinate()
