from typing import Dict
from typing import Literal
from typing import NamedTuple
from typing import Tuple
from typing import Type
from typing import Union

from ap_games.player.player import Player

__ALL__ = [
    "Cell",
    "Coordinate",
    "EMPTY",
    "GameStatus",
    "Label",
    "Side",
    "Step",
    "SupportedPlayers",
]

EMPTY: Literal[" "] = " "
X: Literal["X"] = "X"
O: Literal["O"] = "O"


class Coordinate(NamedTuple):
    """Coordinate(x: int, y: int)."""

    x: int
    y: int


class Cell(NamedTuple):
    """Cell(coordinate: Coordinate, label: str)."""

    coordinate: Coordinate
    label: str


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
Label = Literal["X", "O"]
Labels = Union[Label, str]
SupportedPlayers = Dict[str, Type[Player]]
Size = int
