from __future__ import annotations

import random
from functools import cached_property
from random import choice as random_choice
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import Label
    from ap_games.game.game_base import GameBase

TEST_MODE: bool = False

__ALL__ = ["Player", "TEST_MODE"]

if TEST_MODE:
    random.seed(123)


class Player:
    """Class introduces the player in a board game."""

    def __init__(self, type_: str, /, *, game: GameBase, label: Label):
        self._type: str = type_
        self._game: GameBase = game
        self._label: Label = label

    def __str__(self) -> str:
        """Return label."""
        return self._label

    @cached_property
    def type(self) -> str:
        """Return type."""
        return self._type

    @cached_property
    def game(self) -> GameBase:
        """Return game as instance of :class:`GameBase`."""
        return self._game

    @cached_property
    def label(self) -> Label:
        """Return label."""
        return self._label

    def _random_coordinate(self) -> Coordinate:
        """Return coordinate of randomly selected cell on the gameboard.

        If there're no cells available, return ``undefined_coordinate``.

        """
        available_steps: Tuple[Coordinate, ...] = self.game.available_steps()
        return (
            random_choice(available_steps)
            if available_steps
            else self.game.gameboard.undefined_coordinate
        )

    def go(self) -> Coordinate:
        """Return the randomly selected coordinate.

        This method should be overridden by subclasses if there is a
        more complex rule for determining coordinates.

        """
        return self._random_coordinate()
