from __future__ import annotations

from functools import cached_property
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple

    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import PlayerMark
    from ap_games.game.game_base import TwoPlayerBoardGame

__all__ = ('Player',)


class Player:
    """Class introduces the player in a board game."""

    def __init__(
        self, type_: str, /, *, mark: PlayerMark, game: TwoPlayerBoardGame
    ):
        self._type: str = type_
        self._game: TwoPlayerBoardGame = game
        self._mark: PlayerMark = mark

    def __str__(self) -> str:
        """Return mark."""
        return self._mark

    @cached_property
    def type_(self) -> str:
        """Return type."""
        return self._type

    @cached_property
    def game(self) -> TwoPlayerBoardGame:
        """Return game as instance of :class:`TwoPlayerBoardGame`."""
        return self._game

    @cached_property
    def mark(self) -> PlayerMark:
        """Return mark."""
        return self._mark

    def move(self) -> Coordinate:
        """Return the randomly selected coordinate.

        .. note::

            This method should be overridden by subclasses if there is a
            more complex rule for determining coordinate of move.

        :returns: User-selected cell coordinate.

        """
        return self._random_coordinate()

    def _random_coordinate(self) -> Coordinate:
        """Return randomly selected coordinate on the gameboard.

        :returns: One randomly selected coordinate if there are
            available coordinates, else ``undefined_coordinate``.

        """
        available_moves: Tuple[
            Coordinate, ...
        ] = self.game.get_available_moves()
        return (
            random.choice(available_moves)
            if available_moves
            else self.game.gameboard.undefined_coordinate
        )
