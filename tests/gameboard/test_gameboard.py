from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore

from ap_games.ap_collections import Coordinate
from ap_games.ap_collections import Offset
from ap_games.ap_constants import EMPTY
from ap_games.ap_constants import O_MARK
from ap_games.ap_constants import X_MARK
from ap_games.gameboard.gameboard import _GameboardRegistry
from ap_games.gameboard.gameboard import SquareGameboard

if TYPE_CHECKING:
    from typing import List
    from typing import Tuple

    from ap_games.ap_collections import Cell
    from ap_games.ap_typing import Mark
    from ap_games.ap_typing import Side


class TestGameboardRegistry:
    @pytest.mark.parametrize('size', [2, 9], ids=lambda size: f'{size=}')
    def test_correct_size(self, size: int) -> None:
        assert size == _GameboardRegistry(size=size).size

    def test_wrong_size(self, wrong_size: int) -> None:
        with pytest.raises(ValueError, match='between 2 and 9') as e:
            _GameboardRegistry(size=wrong_size)
        assert 'The size of the gameboard must be between 2 and 9!' == str(
            e.value
        )

    @pytest.mark.parametrize(
        ('index', 'coordinate'),
        [
            (0, Coordinate(x=1, y=2)),
            (1, Coordinate(x=2, y=2)),
            (2, Coordinate(x=1, y=1)),
            (3, Coordinate(x=2, y=1)),
        ],
        ids=lambda arg: f'{arg}',
    )
    def test_index_to_coordinate(
        self,
        index: int,
        coordinate: Coordinate,
        gameboard_registry_2x2: _GameboardRegistry,
    ) -> None:
        assert coordinate == gameboard_registry_2x2.index_to_coordinate[index]

    def test_all_coordinates(
        self,
        all_coordinates_2x2: List[Coordinate],
        gameboard_registry_2x2: _GameboardRegistry,
    ) -> None:
        assert all_coordinates_2x2 == sorted(
            gameboard_registry_2x2.all_coordinates
        )


class TestSquareGameboard:
    def test_gameboard_interface(
        self, gameboard_2x2: SquareGameboard, public_interface: str
    ) -> None:
        assert hasattr(gameboard_2x2, public_interface)

    def test_size(self, allowed_size: int) -> None:
        assert (
            allowed_size
            == SquareGameboard(grid=EMPTY * (allowed_size ** 2))._size
        )

    def test_not_square_board(self) -> None:
        with pytest.raises(ValueError, match='must be square') as e:
            SquareGameboard(grid=EMPTY * 5)
        assert 'The gameboard must be square (2^2 != 5)!' == str(e.value)

    def test_default_grid(self) -> None:
        assert SquareGameboard.default_grid == SquareGameboard().grid_as_string

    def test_indent(self, indent_symbol: str) -> None:
        assert indent_symbol == SquareGameboard(indent=indent_symbol).indent

    def test_registry_size(self, allowed_size: int) -> None:
        assert (
            allowed_size
            == SquareGameboard(grid=EMPTY * (allowed_size ** 2)).registry.size
        )

    def test_gap(self, gap_symbol: str) -> None:
        assert gap_symbol == SquareGameboard(gap=gap_symbol)._gap

    @pytest.mark.parametrize(
        'axis', [True, False], ids=lambda axis: f'{axis=}'
    )
    def test_axis(self, axis: bool) -> None:
        assert axis == SquareGameboard(axis=axis)._axis

    def test_inappropriate_character(self) -> None:
        character: str = 'A'
        with pytest.raises(ValueError, match='must include characters') as e:
            SquareGameboard(grid=character * 4)
        assert (
            'The "grid" must include characters from the set: '
            f'{set(SquareGameboard.mark_colors.keys())}!'
        ) == str(e.value)

    def test_str(
        self,
        grid_3x3_no_colorized: str,
        gameboard_3x3_no_colorized: SquareGameboard,
    ) -> None:
        assert grid_3x3_no_colorized == str(gameboard_3x3_no_colorized)

    def test_cells(
        self,
        gameboard_2x2: SquareGameboard,
        gameboard_2x2_cells: Tuple[Cell, ...],
    ) -> None:
        assert gameboard_2x2_cells == gameboard_2x2.cells

    def test_getitem(
        self,
        gameboard_2x2: SquareGameboard,
        coordinate_1_2_empty: Coordinate,
        cell_1_2_empty: Cell,
    ) -> None:
        assert cell_1_2_empty == gameboard_2x2[coordinate_1_2_empty]

    def test_property_size(self, gameboard_2x2: SquareGameboard,) -> None:
        assert 2 == gameboard_2x2.size

    def test_grid_as_string(
        self, grid_2x2_as_string: str, gameboard_2x2: SquareGameboard
    ) -> None:
        assert grid_2x2_as_string == gameboard_2x2.grid_as_string

    def test_columns(
        self,
        gameboard_2x2: SquareGameboard,
        gameboard_2x2_columns: Tuple[Side, ...],
    ) -> None:
        assert gameboard_2x2_columns == gameboard_2x2.columns

    def test_rows(
        self,
        gameboard_2x2: SquareGameboard,
        gameboard_2x2_rows: Tuple[Side, ...],
    ) -> None:
        assert gameboard_2x2_rows == gameboard_2x2.rows

    def test_diagonals(
        self,
        gameboard_2x2: SquareGameboard,
        gameboard_2x2_diagonals: Tuple[Side, Side],
    ) -> None:
        assert gameboard_2x2_diagonals == gameboard_2x2.diagonals

    def test_all_sides(
        self,
        gameboard_2x2: SquareGameboard,
        gameboard_2x2_rows: Tuple[Side, ...],
        gameboard_2x2_columns: Tuple[Side, ...],
        gameboard_2x2_diagonals: Tuple[Side, Side],
    ) -> None:
        assert (
            gameboard_2x2_rows
            + gameboard_2x2_columns
            + gameboard_2x2_diagonals
        ) == gameboard_2x2.all_sides

    def test_available_moves(
        self, gameboard_2x2: SquareGameboard, coordinate_1_2_empty: Coordinate
    ) -> None:
        assert (coordinate_1_2_empty,) == gameboard_2x2.available_moves

    def test_place_mark_in_empty_cell(
        self, gameboard_2x2: SquareGameboard, coordinate_1_2_empty: Coordinate
    ) -> None:
        assert 1 == gameboard_2x2.place_mark(
            coordinate=coordinate_1_2_empty, mark=X_MARK
        )

    @pytest.mark.parametrize(
        'coordinate',
        [Coordinate(2, 2), Coordinate(1, 1), Coordinate(2, 1)],
        ids=lambda coordinate: f'{coordinate=}',
    )
    def test_place_mark_in_occupied_cell(
        self, gameboard_2x2: SquareGameboard, coordinate: Coordinate
    ) -> None:
        assert 0 == gameboard_2x2.place_mark(
            coordinate=coordinate, mark=X_MARK
        )

    @pytest.mark.parametrize(
        'coordinate',
        [
            Coordinate(1, 2),
            Coordinate(2, 2),
            Coordinate(1, 1),
            Coordinate(2, 1),
        ],
        ids=lambda coordinate: f'{coordinate=}',
    )
    def test_place_mark_force(
        self, gameboard_2x2: SquareGameboard, coordinate: Coordinate
    ) -> None:
        assert 1 == gameboard_2x2.place_mark(
            coordinate=coordinate, mark=X_MARK, force=True
        )

    @pytest.mark.parametrize(
        ('coordinate', 'direction'),
        [
            (Coordinate(1, 2), Coordinate(1, 0)),
            (Coordinate(1, 1), Coordinate(1, 1)),
            (Coordinate(2, 1), Coordinate(0, 1)),
        ],
        ids=lambda arg: f'{arg}',
    )
    def test_get_offset_cell(
        self,
        gameboard_2x2: SquareGameboard,
        cell_2_2_o: Cell,
        coordinate: Coordinate,
        direction: Coordinate,
    ) -> None:
        assert cell_2_2_o == gameboard_2x2.get_offset_cell(
            coordinate=coordinate, direction=direction
        )

    @pytest.mark.parametrize(
        ('coordinate', 'offsets'),
        [
            (
                Coordinate(x=1, y=1),
                [
                    Offset(Coordinate(x=1, y=2), Coordinate(x=0, y=1)),
                    Offset(Coordinate(x=2, y=1), Coordinate(x=1, y=0)),
                    Offset(Coordinate(x=2, y=2), Coordinate(x=1, y=1)),
                ],
            ),
            (
                Coordinate(x=2, y=2),
                [
                    Offset(Coordinate(x=2, y=3), Coordinate(x=0, y=1),),
                    Offset(Coordinate(x=3, y=1), Coordinate(x=1, y=-1),),
                    Offset(Coordinate(x=3, y=2), Coordinate(x=1, y=0),),
                    Offset(Coordinate(x=3, y=3), Coordinate(x=1, y=1),),
                ],
            ),
            (Coordinate(x=3, y=3), [],),
        ],
        ids=lambda arg: f'{arg}',
    )
    def test_get_offsets(
        self,
        coordinate: Coordinate,
        offsets: List[Offset],
        gameboard_3x3_no_colorized: SquareGameboard,
    ) -> None:
        assert offsets == sorted(
            gameboard_3x3_no_colorized.get_offsets(coordinate)
        )

    @pytest.mark.parametrize(
        'coordinate',
        [Coordinate(0, 0), Coordinate(1, 3), Coordinate(3, 1)],
        ids=lambda coordinate: f'{coordinate=}',
    )
    def test_get_offsets_wrong_coordinate(
        self, gameboard_2x2: SquareGameboard, coordinate: Coordinate
    ) -> None:
        with pytest.raises(ValueError, match='out of range!') as e:
            gameboard_2x2.get_offsets(coordinate=coordinate)
        assert f'The {coordinate} out of range!' == str(e.value)

    @pytest.mark.parametrize(
        ('expected_count', 'mark'), [(1, EMPTY), (1, O_MARK), (2, X_MARK)]
    )
    def test_count(
        self, gameboard_2x2: SquareGameboard, expected_count: int, mark: Mark
    ) -> None:
        assert expected_count == gameboard_2x2.count(mark=mark)

    @pytest.mark.parametrize(
        'attr',
        ['grid_as_string', '_gap', '_axis'],
        ids=lambda attr: f'{attr=}',
    )
    def test_copy(self, gameboard_2x2: SquareGameboard, attr: str) -> None:
        gameboard_2x2_copy: SquareGameboard = gameboard_2x2.copy()
        assert getattr(gameboard_2x2, attr) == getattr(
            gameboard_2x2_copy, attr
        )
