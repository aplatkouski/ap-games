from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_collections import Cell
from ap_games.ap_collections import Coordinate
from ap_games.ap_constants import EMPTY
from ap_games.ap_constants import O_MARK
from ap_games.ap_constants import X_MARK
from ap_games.gameboard.gameboard import _GameboardRegistry
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import List
    from typing import Tuple

    from ap_games.ap_typing import Side


@pytest.fixture(scope='session')
def all_coordinates_2x2() -> List[Coordinate]:
    return [
        Coordinate(x=1, y=1),
        Coordinate(x=1, y=2),
        Coordinate(x=2, y=1),
        Coordinate(x=2, y=2),
    ]


@pytest.fixture(scope='session')
def gameboard_registry_2x2() -> _GameboardRegistry:
    return _GameboardRegistry(size=2)


@pytest.fixture(scope='session')
def gameboard_registry_3x3() -> _GameboardRegistry:
    return _GameboardRegistry(size=3)


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
def gameboard_2x2_cells(
    cell_1_2_empty: Cell, cell_2_2_o: Cell, cell_1_1_x: Cell, cell_2_1_x: Cell,
) -> Tuple[Cell, ...]:
    return cell_1_2_empty, cell_2_2_o, cell_1_1_x, cell_2_1_x


@pytest.fixture(scope='module')
def gameboard_2x2_columns(
    gameboard_2x2_cells: Tuple[Cell, ...]
) -> Tuple[Side, ...]:
    return (
        (gameboard_2x2_cells[0], gameboard_2x2_cells[2]),
        (gameboard_2x2_cells[1], gameboard_2x2_cells[3]),
    )


@pytest.fixture(scope='module')
def gameboard_2x2_rows(
    gameboard_2x2_cells: Tuple[Cell, ...]
) -> Tuple[Side, ...]:
    return (
        (gameboard_2x2_cells[2], gameboard_2x2_cells[3]),
        (gameboard_2x2_cells[0], gameboard_2x2_cells[1]),
    )


@pytest.fixture(scope='module')
def gameboard_2x2_diagonals(
    gameboard_2x2_cells: Tuple[Cell, ...]
) -> Tuple[Side, Side]:
    return (
        (gameboard_2x2_cells[0], gameboard_2x2_cells[3]),
        (gameboard_2x2_cells[2], gameboard_2x2_cells[1]),
    )


@pytest.fixture(scope='module')
def grid_2x2_as_string(gameboard_2x2_cells: Tuple[Cell, ...]) -> str:
    return ''.join(cell.mark for cell in gameboard_2x2_cells)


@pytest.fixture()
def gameboard_2x2(grid_2x2_as_string: str) -> SquareGameboard:
    return SquareGameboard(grid=grid_2x2_as_string)


@pytest.fixture(scope='module')
def grid_3x3_as_string() -> str:
    return 'X O X O X'


@pytest.fixture(scope='module')
def grid_3x3_no_colorized() -> str:
    return (
        '  ---------\n'
        '3 | X   O |\n'
        '2 |   X   |\n'
        '1 | O   X |\n'
        '  ---------\n'
        '    1 2 3 '
    )


@pytest.fixture()
def gameboard_3x3_no_colorized(grid_3x3_as_string: str) -> SquareGameboard:
    return SquareGameboard(grid=grid_3x3_as_string, axis=True, colorized=False)
