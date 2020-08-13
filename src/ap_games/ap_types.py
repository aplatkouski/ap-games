from __future__ import annotations

from typing import Dict
from typing import Final
from typing import Literal
from typing import NamedTuple
from typing import Tuple
from typing import Type
from typing import Union

from ap_games.player.player import Player

EMPTY: Final[Literal[' ']] = ' '
O_MARK: Final[Literal['O']] = 'O'
X_MARK: Final[Literal['X']] = 'X'
UNDEFINED_MARK: Final[Literal['']] = ''

PlayerMark = Literal['X', 'O']
Mark = Union[Literal['X'], Literal['O'], Literal[' '], Literal['']]

SupportedPlayers = Dict[str, Type[Player]]
OptionalPlayerTypes = Union[Tuple[str, str], Tuple[()]]
Size = int


class Coordinate(NamedTuple):
    """Coordinate(x: int, y: int)."""

    x: int  # noqa: WPS111
    y: int  # noqa: WPS111


class Cell(NamedTuple):
    """Cell(coordinate: Coordinate, mark: str)."""

    coordinate: Coordinate
    mark: Mark


class Offset(NamedTuple):
    """Offset(coordinate: Coordinate, direction: Coordinate)."""

    coordinate: Coordinate
    direction: Coordinate


class GameStatus(NamedTuple):
    """GameStatus(active: bool, message: str, must_skip: bool)."""

    active: bool
    message: str
    must_skip: bool


class Move(NamedTuple):
    """Move(coordinate: Coordinate, score: int, percentage: int, last: bool).

    :ivar coordinate:  The coordinate of selected cell or
        ``undefined_coordinate`` if game status is ``False``.
    :ivar score:  The terminal game score.
    :ivar percentage:  The percentage to reach ``score`` as a number
        greater 0 and less than or equal to 100.  See description above.
    :ivar last:  ``True`` if current move finishes the game, ``False`` -
        otherwise.

    """

    coordinate: Coordinate
    score: int
    percentage: int
    last: bool


class Node(NamedTuple):
    """Move(player_mark: PlayerMark, move: Move, sub_tree: Tree)."""

    player_mark: PlayerMark
    move: Move
    sub_tree: 'Tree'  # type: ignore


UNDEFINED_MOVE = Move(Coordinate(x=0, y=0), score=0, percentage=0, last=False)

Side = Tuple[Cell, ...]
Directions = Tuple[Coordinate, ...]
Coordinates = Tuple[Coordinate, ...]
Tree = Dict[str, Node]  # type: ignore
