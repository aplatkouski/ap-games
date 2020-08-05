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


class Step(NamedTuple):
    """Step(coordinate: Coordinate, score: int, percentage: int)."""

    coordinate: Coordinate
    score: int
    percentage: int


Side = Tuple[Cell, ...]
Directions = Tuple[Coordinate, ...]
Coordinates = Tuple[Coordinate, ...]
