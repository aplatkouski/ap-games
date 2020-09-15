from __future__ import annotations

from typing import Dict
from typing import NamedTuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type
    from typing import Any

    from ap_games.ap_typing import Mark
    from ap_games.ap_typing import PlayerMark
    from ap_games.game.game_base import TwoPlayerBoardGame


class Coordinate(NamedTuple):
    """Coordinate(x: int, y: int)."""

    x: int  # noqa: WPS111
    y: int  # noqa: WPS111


class Cell(NamedTuple):
    """Cell(coordinate: Coordinate, mark: str)."""

    coordinate: Coordinate
    mark: Mark


class Game(NamedTuple):
    """Game(name: str, game_class: Type[TwoPlayerBoardGame])."""

    name: str
    game_class: Type[TwoPlayerBoardGame]


class GameStatus(NamedTuple):
    """GameStatus(active: bool, message: str, must_skip: bool)."""

    active: bool
    message: str
    must_skip: bool


class Move(NamedTuple):
    """Move(coordinate: Coordinate, score: int, potential: int, last: bool).

    :ivar coordinate:  The coordinate of selected cell or
        ``undefined_coordinate`` if game status is ``False``.
    :ivar score:  The terminal game score.
    :ivar potential:  The potential to reach ``score`` as a number
        between 0 and 10000.  See description in ``AIPlayer._minimax``
        method.
    :ivar last:  ``True`` if current move finishes the game, ``False`` -
        otherwise.

    """

    coordinate: Coordinate
    score: int
    potential: int
    last: bool


class Node(NamedTuple):
    """Move(player_mark: PlayerMark, move: Move, sub_tree: Tree)."""

    player_mark: PlayerMark
    move: Move
    sub_tree: Dict[str, Any]


class Offset(NamedTuple):
    """Offset(coordinate: Coordinate, direction: Coordinate)."""

    coordinate: Coordinate
    direction: Coordinate
