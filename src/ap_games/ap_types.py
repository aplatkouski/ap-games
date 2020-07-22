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

Coordinate = NamedTuple("Coordinate", [("x", int), ("y", int)])
Cell = NamedTuple("Cell", [("coordinate", Coordinate), ("label", str)])
Side = Tuple[Cell, ...]
Directions = Tuple[Coordinate, ...]
Offset = NamedTuple(
    "Offset", [("coordinate", Coordinate), ("direction", Coordinate)]
)

GameStatus = NamedTuple(
    "GameStatus", [("active", bool), ("message", str), ("must_skip", bool)]
)
Step = NamedTuple(
    "Step", [("coordinate", Coordinate), ("score", int), ("percentage", int)]
)

Label = Literal["X", "O"]
Labels = Union[Label, str]
SupportedPlayers = Dict[str, Type[Player]]

Size = int
