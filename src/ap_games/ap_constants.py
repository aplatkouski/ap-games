from __future__ import annotations

from typing import TYPE_CHECKING

from ap_games.ap_typing import Cell
from ap_games.ap_typing import Coordinate
from ap_games.ap_typing import Move

if TYPE_CHECKING:
    from typing import Final

    from ap_games.ap_typing import Empty
    from ap_games.ap_typing import PlayerMark
    from ap_games.ap_typing import UndefinedMark

EMPTY: Final[Empty] = ' '
O_MARK: Final[PlayerMark] = 'O'
X_MARK: Final[PlayerMark] = 'X'
UNDEFINED_MARK: Final[UndefinedMark] = ''
UNDEFINED_COORDINATE: Final[Coordinate] = Coordinate(x=0, y=0)
UNDEFINED_CELL: Final[Cell] = Cell(
    coordinate=UNDEFINED_COORDINATE, mark=UNDEFINED_MARK
)
UNDEFINED_MOVE: Final[Move] = Move(
    coordinate=UNDEFINED_COORDINATE, score=0, potential=0, last=False
)
