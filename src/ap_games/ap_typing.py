from __future__ import annotations

from typing import Dict
from typing import Literal
from typing import Tuple

from ap_games.ap_collections import Cell
from ap_games.ap_collections import Coordinate
from ap_games.ap_collections import Node

Mark = Literal['X', 'O', ' ', '']
Empty = Literal[' ']
PlayerMark = Literal['X', 'O']
UndefinedMark = Literal['']

Coordinates = Tuple[Coordinate, ...]
Directions = Tuple[Coordinate, ...]
PlayerType = Literal['easy', 'hard', 'medium', 'nightmare', 'user']
Side = Tuple[Cell, ...]
Size = int
Tree = Dict[str, Node]
