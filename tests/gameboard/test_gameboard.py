from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_collections import Coordinate
from ap_games.ap_constants import EMPTY
from ap_games.ap_constants import O_MARK
from ap_games.ap_constants import X_MARK
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import Tuple

    from ap_games.ap_collections import Cell
    from ap_games.ap_typing import Mark
    from ap_games.ap_typing import Side


class TestSquareGameboard:
    def test_size(self, gameboard_2x2: SquareGameboard) -> None:
        assert 2 == gameboard_2x2.size

    def test_grid(
        self, gameboard_2x2: SquareGameboard, grid_2x2_as_string: str
    ) -> None:
        assert grid_2x2_as_string == gameboard_2x2.grid_as_string

    def test_columns(
        self, gameboard_2x2: SquareGameboard, columns: Tuple[Side, ...]
    ) -> None:
        assert columns == gameboard_2x2.columns

    def test_rows(
        self, gameboard_2x2: SquareGameboard, rows: Tuple[Side, ...]
    ) -> None:
        assert rows == gameboard_2x2.rows

    def test_diagonals(
        self, gameboard_2x2: SquareGameboard, diagonals: Tuple[Side, ...]
    ) -> None:
        assert diagonals == gameboard_2x2.diagonals

    def test_cells(
        self, gameboard_2x2: SquareGameboard, cells: Tuple[Cell, ...]
    ) -> None:
        assert cells == gameboard_2x2.cells

    def test_get_available_moves(
        self, gameboard_2x2: SquareGameboard, coordinate_1_2_empty: Coordinate
    ) -> None:
        assert (coordinate_1_2_empty,) == gameboard_2x2.available_moves

    @pytest.mark.parametrize(
        ('expected_count', 'mark'), [(1, EMPTY), (1, O_MARK), (2, X_MARK)]
    )
    def test_count(
        self, gameboard_2x2: SquareGameboard, expected_count: int, mark: Mark
    ) -> None:
        assert expected_count == gameboard_2x2.count(mark=mark)

    def test_get_offset_cell(
        self, gameboard_2x2: SquareGameboard, cell_2_2_o: Cell,
    ) -> None:
        assert cell_2_2_o == gameboard_2x2.get_offset_cell(
            coordinate=Coordinate(1, 2), direction=Coordinate(1, 0)
        )

    def test_place_mark_in_empty_cell(
        self, gameboard_2x2: SquareGameboard, coordinate_1_2_empty: Coordinate
    ) -> None:
        assert 1 == gameboard_2x2.place_mark(
            coordinate=coordinate_1_2_empty, mark=X_MARK
        )

    @pytest.mark.parametrize(
        'coordinate',
        [Coordinate(2, 2), Coordinate(1, 1)],
        ids=lambda coordinate: f'{coordinate=}',
    )
    def test_place_mark_in_occupied_cell(
        self, gameboard_2x2: SquareGameboard, coordinate: Coordinate
    ) -> None:
        assert 0 == gameboard_2x2.place_mark(
            coordinate=coordinate, mark=X_MARK
        )

    @pytest.mark.parametrize('size', [2, 9], ids=lambda size: f'{size=}')
    def test_correct_gameboard_size(self, size: int) -> None:
        grid: str = EMPTY * (size ** 2)
        assert grid == SquareGameboard(grid=grid).grid_as_string

    @pytest.mark.parametrize('size', [0, 1, 10], ids=lambda size: f'{size=}')
    def test_wrong_gameboard_size(self, size: int) -> None:
        with pytest.raises(ValueError, match='between 2 and 9') as e:
            SquareGameboard(grid=EMPTY * (size ** 2))
        assert 'The size of the gameboard must be between 2 and 9!' == str(
            e.value
        )

    def test_not_square_gameboard(self) -> None:
        grid: str = EMPTY * 5
        with pytest.raises(ValueError, match='must be square') as e:
            SquareGameboard(grid=grid)
        assert 'The gameboard must be square (2^2 != 5)!' == str(e.value)
