from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_types import Cell
from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.ap_types import O_MARK
from ap_games.ap_types import Side
from ap_games.ap_types import X_MARK
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import Tuple


@pytest.fixture(scope='session')
def coordinate_1_2_empty() -> Coordinate:
    return Coordinate(x=1, y=2)


@pytest.fixture(scope='session')
def cell_1_2_empty(coordinate_1_2_empty: Coordinate) -> Cell:
    return Cell(coordinate=coordinate_1_2_empty, mark=EMPTY)


@pytest.fixture(scope='session')
def cell_2_2_o() -> Cell:
    return Cell(coordinate=Coordinate(x=2, y=2), mark=O_MARK)


@pytest.fixture(scope='session')
def cell_1_1_x() -> Cell:
    return Cell(coordinate=Coordinate(x=1, y=1), mark=X_MARK)


@pytest.fixture(scope='session')
def cell_2_1_x() -> Cell:
    return Cell(coordinate=Coordinate(x=2, y=1), mark=X_MARK)


@pytest.fixture(scope='module')
def cells(
    cell_1_2_empty: Cell, cell_2_2_o: Cell, cell_1_1_x: Cell, cell_2_1_x: Cell,
) -> Tuple[Cell, ...]:
    return cell_1_2_empty, cell_2_2_o, cell_1_1_x, cell_2_1_x


@pytest.fixture(scope='module')
def grid_2x2_as_string(cells: Tuple[Cell, ...]) -> str:
    return ''.join(cell.mark for cell in cells)


@pytest.fixture(scope='module')
def gameboard_2x2(grid_2x2_as_string: str) -> SquareGameboard:
    return SquareGameboard(grid=grid_2x2_as_string)


@pytest.fixture(scope='module')
def columns(cells: Tuple[Cell, ...]) -> Tuple[Side, ...]:
    return (cells[0], cells[2]), (cells[1], cells[3])


@pytest.fixture(scope='module')
def rows(cells: Tuple[Cell, ...]) -> Tuple[Side, ...]:
    return (cells[2], cells[3]), (cells[0], cells[1])


@pytest.fixture(scope='module')
def diagonals(cells: Tuple[Cell, ...]) -> Tuple[Side, Side]:
    return (cells[0], cells[3]), (cells[2], cells[1])
