from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.gameboard.gameboard import SquareGameboard
from .conftest import SIZE_2  # noqa: T484

if TYPE_CHECKING:
    from typing import Tuple

    from ap_games.ap_types import Cell
    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import Side


def test_size(square_gameboard_2x2: SquareGameboard) -> None:
    assert SIZE_2 == square_gameboard_2x2.size


def test_grid(
    square_gameboard_2x2: SquareGameboard, grid_2x2_as_str: str
) -> None:
    assert grid_2x2_as_str == square_gameboard_2x2.grid_as_string


def test_columns(
    square_gameboard_2x2: SquareGameboard, columns: Tuple[Side, ...]
) -> None:
    assert columns == square_gameboard_2x2.columns


def test_rows(
    square_gameboard_2x2: SquareGameboard, rows: Tuple[Side, ...]
) -> None:
    assert rows == square_gameboard_2x2.rows


def test_diagonals(
    square_gameboard_2x2: SquareGameboard, diagonals: Tuple[Side, ...]
) -> None:
    assert diagonals == square_gameboard_2x2.diagonals


def test_cells(
    square_gameboard_2x2: SquareGameboard, cells: Tuple[Cell, ...]
) -> None:
    assert cells == square_gameboard_2x2.cells


def test_get_available_moves(
    square_gameboard_2x2: SquareGameboard, coordinate_1_1_empty: Coordinate
) -> None:
    assert (coordinate_1_1_empty,) == square_gameboard_2x2.available_moves


def test_count(square_gameboard_2x2: SquareGameboard) -> None:
    assert 1 == square_gameboard_2x2.count(mark=' ')
    assert 1 == square_gameboard_2x2.count(mark='O')
    assert 2 == square_gameboard_2x2.count(mark='X')


def test_get_offset_cell(
    square_gameboard_2x2: SquareGameboard,
    cell_2_2_o: Cell,
    coordinate_1_1_empty: Coordinate,
) -> None:
    assert cell_2_2_o == square_gameboard_2x2.get_offset_cell(
        start_coordinate=coordinate_1_1_empty, direction=coordinate_1_1_empty
    )


def test_mark(
    square_gameboard_2x2: SquareGameboard, coordinate_1_1_empty: Coordinate
) -> None:
    assert 1 == square_gameboard_2x2.place_mark(
        coordinate=coordinate_1_1_empty, mark='X'
    )


def test_gameboard_1x1_too_small() -> None:
    with pytest.raises(ValueError, match='between 2 and 9') as e:
        SquareGameboard(grid=' ')
    assert 'The size of the gameboard must be between 2 and 9!' == str(e.value)


def test_gameboard_10x10_too_large() -> None:
    with pytest.raises(ValueError, match='between 2 and 9') as e:
        SquareGameboard(grid=' ' * 100)
    assert 'The size of the gameboard must be between 2 and 9!' == str(e.value)


def test_not_square_gameboard() -> None:
    grid: str = ' ' * 5
    with pytest.raises(ValueError, match='must be square') as e:
        SquareGameboard(grid=grid)
    assert 'The gameboard must be square (2^2 != 5)!' == str(e.value)
