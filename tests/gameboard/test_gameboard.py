from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore
from ap_games.gameboard.gameboard import SquareGameboard

from .conftest import SIZE_2

if TYPE_CHECKING:
    from typing import NoReturn
    from typing import Optional
    from typing import Tuple

    from ap_games.ap_types import Cell
    from ap_games.ap_types import Coordinate
    from ap_games.ap_types import Side


def test_size(square_gameboard_2x2: SquareGameboard) -> Optional[NoReturn]:
    assert SIZE_2 == square_gameboard_2x2.size


def test_surface(
    square_gameboard_2x2: SquareGameboard, surface_4: str
) -> Optional[NoReturn]:
    assert surface_4 == square_gameboard_2x2.surface


def test_columns(
    square_gameboard_2x2: SquareGameboard, columns: Tuple[Side, ...]
) -> Optional[NoReturn]:
    assert columns == square_gameboard_2x2.columns


def test_rows(
    square_gameboard_2x2: SquareGameboard, rows: Tuple[Side, ...]
) -> Optional[NoReturn]:
    assert rows == square_gameboard_2x2.rows


def test_diagonals(
    square_gameboard_2x2: SquareGameboard, diagonals: Tuple[Side, ...]
) -> Optional[NoReturn]:
    assert diagonals == square_gameboard_2x2.diagonals


def test_cells(
    square_gameboard_2x2: SquareGameboard, cells: Tuple[Cell, ...]
) -> Optional[NoReturn]:
    assert cells == square_gameboard_2x2.cells


def test_available_steps(
    square_gameboard_2x2: SquareGameboard, coordinate_1_1_empty: Coordinate
) -> Optional[NoReturn]:
    assert (coordinate_1_1_empty,) == square_gameboard_2x2.available_steps


def test_count(square_gameboard_2x2: SquareGameboard) -> Optional[NoReturn]:
    assert 1 == square_gameboard_2x2.count(label=" ")
    assert 1 == square_gameboard_2x2.count(label="O")
    assert 2 == square_gameboard_2x2.count(label="X")


def test_get_offset_cell(
    square_gameboard_2x2: SquareGameboard,
    cell_2_2_o: Cell,
    coordinate_1_1_empty: Coordinate,
) -> Optional[NoReturn]:
    assert cell_2_2_o == square_gameboard_2x2.get_offset_cell(
        coordinate=coordinate_1_1_empty, shift=coordinate_1_1_empty
    )


def test_label(
    square_gameboard_2x2: SquareGameboard, coordinate_1_1_empty: Coordinate
) -> Optional[NoReturn]:
    assert 1 == square_gameboard_2x2.label(
        coordinate=coordinate_1_1_empty, label="X"
    )


def test_gameboard_1x1_too_small() -> Optional[NoReturn]:
    with pytest.raises(ValueError) as exc:
        SquareGameboard(surface=" ")
    assert "The size of the gameboard must be between 2 and 9!" == str(
        exc.value
    )


def test_gameboard_10x10_too_large() -> Optional[NoReturn]:
    with pytest.raises(ValueError) as exc:
        SquareGameboard(surface=" " * 100)
    assert "The size of the gameboard must be between 2 and 9!" == str(
        exc.value
    )


def test_not_square_gameboard() -> Optional[NoReturn]:
    surface: str = " " * 5
    with pytest.raises(ValueError) as exc:
        SquareGameboard(surface=surface)
    assert (
        "The gameboard must be square "
        f"({int(len(surface) ** (1 / 2))}^2 != {len(surface)})!"
        == str(exc.value)
    )
