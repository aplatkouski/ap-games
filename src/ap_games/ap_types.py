from typing import Dict
from typing import NamedTuple
from typing import Tuple
from typing import Type

from typing_extensions import Literal

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

Coordinate = NamedTuple("Coordinate", [("x", int), ("y", int)])
Cell = NamedTuple("Cell", [("coordinate", Coordinate), ("label", str)])
Side = Tuple[Cell, ...]

GameStatus = NamedTuple("GameStatus", [("active", bool), ("message", str)])
Step = NamedTuple(
    "Step", [("coordinate", Coordinate), ("score", int), ("percentage", int)]
)

Label = Literal["X", "O"]
SupportedPlayers = Dict[str, Type["Player"]]
