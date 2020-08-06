from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_types import Cell
from ap_games.ap_types import Coordinate
from ap_games.ap_types import Side
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import Tuple

SIZE_2: int = 2


@pytest.fixture()
def grid_2x2_as_str() -> str:
    return 'XO X'


@pytest.fixture()
def cell_1_2_x() -> Cell:
    return Cell(Coordinate(x=1, y=2), mark='X')


@pytest.fixture()
def cell_2_2_o() -> Cell:
    return Cell(Coordinate(x=2, y=2), mark='O')


@pytest.fixture()
def cell_1_1_empty() -> Cell:
    return Cell(Coordinate(x=1, y=1), mark=' ')


@pytest.fixture()
def cell_2_1_x() -> Cell:
    return Cell(Coordinate(x=2, y=1), mark='X')


@pytest.fixture()
def coordinate_1_1_empty() -> Coordinate:
    return Coordinate(x=1, y=1)


@pytest.fixture()
def square_gameboard_2x2(grid_2x2_as_str: str) -> SquareGameboard:
    return SquareGameboard(grid=grid_2x2_as_str)


@pytest.fixture()
def cells(
    cell_1_2_x: Cell, cell_2_2_o: Cell, cell_1_1_empty: Cell, cell_2_1_x: Cell
) -> Tuple[Cell, ...]:
    return cell_1_2_x, cell_2_2_o, cell_1_1_empty, cell_2_1_x


@pytest.fixture()
def columns(cells: Tuple[Cell, ...]) -> Tuple[Side, ...]:
    return (cells[0], cells[2]), (cells[1], cells[3])


@pytest.fixture()
def rows(cells: Tuple[Cell, ...]) -> Tuple[Side, ...]:
    return (cells[0], cells[1]), (cells[2], cells[3])


@pytest.fixture()
def diagonals(cells: Tuple[Cell, ...]) -> Tuple[Side, Side]:
    return (cells[0], cells[3]), (cells[2], cells[1])
