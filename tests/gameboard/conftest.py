from typing import Tuple

import pytest
from ap_games.gameboard.gameboard import SquareGameboard
from ap_games.ap_types import Cell, Coordinate, Side

SIZE_2 = 2


@pytest.fixture
def surface_4() -> str:
    return "XO X"


@pytest.fixture
def cell_1_2_x() -> Cell:
    return Cell(Coordinate(x=1, y=2), label="X")


@pytest.fixture
def cell_2_2_o() -> Cell:
    return Cell(Coordinate(x=2, y=2), label="O")


@pytest.fixture
def cell_1_1_empty() -> Cell:
    return Cell(Coordinate(x=1, y=1), label=" ")


@pytest.fixture
def cell_2_1_x() -> Cell:
    return Cell(Coordinate(x=2, y=1), label="X")


@pytest.fixture
def coordinate_1_1_empty() -> Coordinate:
    return Coordinate(x=1, y=1)


@pytest.fixture
def square_gameboard_2x2(surface_4) -> SquareGameboard:
    return SquareGameboard(surface=surface_4)


@pytest.fixture
def cells(cell_1_2_x, cell_2_2_o, cell_1_1_empty, cell_2_1_x) -> Tuple[Side, ...]:
    return cell_1_2_x, cell_2_2_o, cell_1_1_empty, cell_2_1_x


@pytest.fixture
def columns(cells) -> Tuple[Side, ...]:
    return (cells[0], cells[2]), (cells[1], cells[3])


@pytest.fixture
def rows(cells) -> Tuple[Side, ...]:
    return (cells[0], cells[1]), (cells[2], cells[3])


@pytest.fixture
def diagonals(cells) -> Tuple[Side, ...]:
    return (cells[0], cells[3]), (cells[2], cells[1])
