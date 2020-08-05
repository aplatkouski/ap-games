from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cached_property
from platform import platform
from typing import cast
from typing import TYPE_CHECKING

from ap_games.ap_types import Cell
from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.ap_types import Mark
from ap_games.ap_types import O_MARK
from ap_games.ap_types import Offset
from ap_games.ap_types import X_MARK
from ap_games.log import logger

if TYPE_CHECKING:
    from typing import Any
    from typing import ClassVar
    from typing import Counter as TypingCounter
    from typing import Dict
    from typing import Final
    from typing import List
    from typing import Tuple

    from ap_games.ap_types import Coordinates
    from ap_games.ap_types import Directions
    from ap_games.ap_types import PlayerMark
    from ap_games.ap_types import Side
    from ap_games.ap_types import Size

__ALL__ = ('SquareGameboard',)


@dataclass(frozen=True)
class _Colors:
    header: Final[str] = '\033[35m'
    blue: Final[str] = '\033[34m'
    green: Final[str] = '\033[32m'
    yellow: Final[str] = '\033[33m'
    turquoise: Final[str] = '\033[36m'
    end: Final[str] = '\033[0m'
    bold: Final[str] = '\033[1m'


class _GameboardRegistry:
    """GameboardRegistry stores basic mapping of SquareGameboard class.

    :param size: The size of SquareGameboard that used in computation
        mappings.

    :ivar index_to_coordinate: Store the mapping of the cell index to
        the coordinate of this cell.  All grid cells are indexed from
        left to right from top to bottom.

        .. seealso::

            :meth:`._fill_index_to_coordinate`

    :ivar offsets: Store the mapping of the grid coordinates to its
        offsets.  Where each offset is a tuple with two fields:

        * ``coordinate`` of the neighboring cell;
        * ``direction`` of the neighboring cell as a coordinate
          with ``-1<=x<=1`` and ``-1<=y<=1`` relatively to the base
          coordinate.

        .. seealso::

            :meth:`._fill_offsets`

    :ivar all_coordinates: Store all possible coordinates of the
        :class:`SquareGameboard` with the given ``size``.

    """

    _directions: Final[ClassVar[Directions]] = (
        Coordinate(0, 1),  # top
        Coordinate(1, 1),  # right-top
        Coordinate(1, 0),  # right and so on
        Coordinate(1, -1),
        Coordinate(0, -1),
        Coordinate(-1, -1),
        Coordinate(-1, 0),
        Coordinate(-1, 1),
    )

    def __init__(self, *, size: int) -> None:
        if (size < 2) or (size > 9):
            raise ValueError(
                'The size of the gameboard must be between 2 and 9!'
            )
        self.size = size
        self.index_to_coordinate: Dict[int, Coordinate] = {}
        self.offsets: Dict[Coordinate, Tuple[Offset, ...]] = {}
        self._fill_index_to_coordinate()
        self.all_coordinates: Final[Coordinates] = tuple(
            self.index_to_coordinate.values()
        )
        self._fill_offsets()

    def _fill_index_to_coordinate(self) -> None:
        """Convert index of cell into coordinate of cell.

        Where an example for a 3x3 ``self.grid``::

            0 1 2         (1, 3) (2, 3) (3, 3)
            3 4 5   ==>   (1, 2) (2, 2) (3, 2)
            6 7 8         (1, 1) (2, 1) (3, 1)

        """
        for index in range(self.size ** 2):
            a, b = divmod(index, self.size)
            column: int = b + 1
            row: int = self.size - a
            self.index_to_coordinate[index] = Coordinate(column, row)

    def _fill_offsets(self) -> None:
        """Fill up :attr:`.offsets` for all coordinates of gameboard."""
        for coordinate in self.all_coordinates:
            offsets: List[Offset] = []
            for shift in self._directions:
                offset_coordinate = Coordinate(
                    x=coordinate.x + shift.x, y=coordinate.y + shift.y
                )
                if offset_coordinate in self.all_coordinates:
                    offsets.append(
                        Offset(coordinate=offset_coordinate, direction=shift)
                    )
            self.offsets[coordinate] = tuple(offsets)


class SquareGameboard:
    """Implementation square game board with size from 2 to 9.

    TODO: rewrite _cells_dict as Dict[Coordinate, PlayerMarkOrEmpty]

    :param grid: The grid or board, represented as a string, where
        each character is mapped to a cell left to right top to bottom.
    :param gap: ``' '`` by default.  Defines the gap that will be
        printed between cells in a row.
    :param axis: ``False`` by default.  If ``True`` print axis.

    :ivar _size: The size of gameboard from 2 to 9.
    :ivar _grid_cache: Save the grid of the gameboard as a string with
        cell labels. This cache is cleaned in :meth:`.place_mark`.

        .. note::

            This attribute adds 25% processing speed.

    :ivar _marked_directions_cache:  Store the mapping of the coordinate
        and the desired mark to the coordinates of adjacent cells with
        this mark.  This cache is cleaned in :meth:`.place_mark`.

    """

    undefined_coordinate: Final[ClassVar[Coordinate]] = Coordinate(x=0, y=0)
    undefined_cell: Final[ClassVar[Cell]] = Cell(
        coordinate=undefined_coordinate, mark=''
    )

    mark_colors: ClassVar[Dict[str, str]] = {
        X_MARK: _Colors.blue,
        O_MARK: _Colors.green,
        EMPTY: _Colors.header,
    }

    default_grid: ClassVar[str] = EMPTY * 9

    _registries: Dict[Size, _GameboardRegistry] = {}

    def __new__(cls, **kwargs: Any) -> Any:
        """Create instance and set :attr:`_registries[size]` if necessary."""
        grid: str = kwargs.get('grid', cls.default_grid)
        size: int = int(len(grid) ** (1 / 2))
        if size ** 2 != len(grid):
            raise ValueError(
                f'The gameboard must be square ({size}^2 != {len(grid)})!'
            )
        if size not in cls._registries:
            cls._registries[size] = _GameboardRegistry(size=size)
        return super().__new__(cls)

    def __init__(
        self,
        *,
        grid: str = default_grid,
        gap: str = ' ',
        axis: bool = False,
        colorized: bool = True,
        _safety: bool = True,
    ) -> None:

        self.colorized: bool = colorized if _safety and platform().startswith(
            'Linux'
        ) else False

        size: int = int(len(grid) ** (1 / 2))
        self._size: Final[int] = size
        self._gap: Final[str] = gap
        self._axis: Final[bool] = axis

        self._cells_dict: Dict[Tuple[int, int], Cell] = {}
        self._colors_dict: Dict[Tuple[int, int], str] = {}
        self._marked_directions_cache: Dict[
            Tuple[Coordinate, str], Directions,
        ] = {}
        self._grid_cache: str = ''
        if _safety:
            self.registry: _GameboardRegistry = self._registries[size]
            for index, mark in enumerate(grid):
                coordinate = self.registry.index_to_coordinate[index]
                mark = cast(Mark, mark)
                self._cells_dict[coordinate] = Cell(coordinate, mark)
            self._default_paint()

    def __str__(self) -> str:
        """Return SquareGameboard as a grid drawn with ASCII characters.

        See example with ``size=4``, ``gap=' '`` and ``axis=True``::

              -----------
            4 |         |
            3 |   X O   |
            2 |   O X   |
            1 |         |
              -----------
                1 2 3 4

        """
        horizontal_border: str = (
            ('  ' if self._axis else '')
            + '-' * (self._size + len(self._gap) * (self._size + 1) + 2)
        )

        grid: str = '\n'.join(
            (f'{self._size - num} ' if self._axis else '')
            + f'|{self._gap}'
            + f'{self._gap}'.join(
                (self._colors_dict[cell.coordinate] if self.colorized else '')
                + cell.mark
                + (_Colors.end if self.colorized else '')
                for cell in row
            )
            + f'{self._gap}|'
            for num, row in enumerate(self.rows)
        )

        col_nums: str = f'{self._gap}'.join(map(str, range(1, self._size + 1)))

        return f'{horizontal_border}\n{grid}\n{horizontal_border}' + (
            f'\n   {self._gap}{col_nums}{self._gap}' if self._axis else ''
        )

    @cached_property
    def size(self) -> int:
        """Return size of gameboard."""
        return self._size

    @property
    def grid(self) -> str:
        """Return all marks of the gameboard as a string.

        Example::

            -------
            | 0 1 |
            | 2 3 |   ===>   '0123'
            -------

        """
        if not self._grid_cache:
            self._grid_cache = ''.join(
                cell.mark for cell in self._cells_dict.values()
            )
        return self._grid_cache

    @property
    def counter(self) -> TypingCounter[str]:
        """Count marks on the gameboard and return ``Counter``."""
        return Counter(self.grid)

    @property
    def columns(self) -> Tuple[Side, ...]:
        """Return all columns of gameboard as a tuple."""
        return tuple(
            tuple(
                filter(
                    lambda cell: cell.coordinate.x == column,
                    self._cells_dict.values(),
                )
            )
            for column in range(1, self._size + 1)
        )

    @property
    def rows(self) -> Tuple[Side, ...]:
        """Return all rows of gameboard as a tuple.

        .. note::

            Rows are returned in the reverse order from top to button.
            This behavior of the method is necessary for the correct
            printing ot the gameboard. To get rows in the coordinate order
            from button to top, use ``sorted`` method.

        """
        return tuple(
            tuple(
                filter(
                    lambda cell: cell.coordinate.y == row,
                    self._cells_dict.values(),
                )
            )
            for row in reversed(range(1, self._size + 1))
        )

    @property
    def diagonals(self) -> Tuple[Side, Side]:
        """Return main and reverse diagonals as a tuple."""
        main_diagonal: Side = tuple(
            self._cells_dict[num + 1, self._size - num]
            for num in range(self._size)
        )
        reverse_diagonal: Side = tuple(
            self._cells_dict[num, num] for num in range(1, self._size + 1)
        )
        return main_diagonal, reverse_diagonal

    @property
    def all_sides(self) -> Tuple[Side, ...]:
        """Return all rows, columns and diagonals as tuple of all sides.

        Where each side is a tuple of cells of the corresponding side.

        """
        return self.rows + self.columns + self.diagonals

    @property
    def cells(self) -> Tuple[Cell, ...]:
        """Return all cells of the gameboard.

        Where each cell is a namedtuple with two fields:

        * ``coordinate`` - as namedtuple ``Coordinate`` with two
          ``int`` fields ``x`` and ``y``;
        * ``mark`` of cell as a one-character string.

        """
        return tuple(self._cells_dict.values())

    @property
    def available_moves(self) -> Coordinates:
        """Return coordinates of all ``EMPTY`` cells."""
        return tuple(
            cell.coordinate for cell in self.cells if cell.mark == EMPTY
        )

    def place_mark(
        self, coordinate: Coordinate, mark: PlayerMark, *, force: bool = False,
    ) -> int:
        """Mark cell of the gameboard with the ``coordinate``.

        :param coordinate:  Position of cell as instance of namedtuple
            Coordinate(x, y).
        :param mark:  New mark.  It will be set if ``force=True`` or
            cell with ``coordinate`` is **empty** (``EMPTY``).
        :param force:  ``False`` by default.  When ``True`` it doesn't
            matter if cell is **empty** or not.

        :returns:  Count of marked cell with ``mark``.

        """
        if (
            force
            or self._cells_dict.get(coordinate, self.undefined_cell).mark
            == EMPTY
        ):
            self._cells_dict[coordinate] = Cell(coordinate, mark)
            if self.colorized:
                if force:
                    self._colors_dict[coordinate] = _Colors.turquoise
                else:
                    self._colors_dict[
                        coordinate
                    ] = f'{_Colors.bold}{_Colors.turquoise}'
            self._marked_directions_cache = {}
            self._grid_cache = ''
            return 1
        logger.warning('This cell is occupied! Choose another one!')
        return 0

    def get_offset_cell(
        self, start_coordinate: Coordinate, direction: Coordinate
    ) -> Cell:
        """Return cell by coordinate calculated as algebraic sum of parameters.

        :param start_coordinate: Coordinate of starting cell;
        :param direction: Shift as a coordinate with ``-1<=x<=1`` and
            ``-1<=y<=1``.

        :returns: adjacent cell as instance of :class:`.Cell` if cell
            exist on the gameboard else :attr:`.undefined_cell`.

        """
        return self._cells_dict.get(
            (
                start_coordinate.x + direction.x,
                start_coordinate.y + direction.y,
            ),
            self.undefined_cell,
        )

    def get_marked_coordinates(self, mark: str) -> Coordinates:
        """Return coordinates of all cells with the given ``mark``.

        :param mark:  The mark relative to which the cell will be
            matched by.

        """
        return tuple(
            cell.coordinate for cell in self.cells if cell.mark == mark
        )

    def get_directions(
        self, start_coordinate: Coordinate, offset_cell_mark: Mark
    ) -> Directions:
        """Return coordinates of offset cells with the given ``mark``.

        :param start_coordinate:  The coordinate, adjacent cells that
            will be checked.
        :param offset_cell_mark:  The mark of adjacent cells whose
                directions are returned.

        :raises ValueError: If ``start_coordinate`` out of range.

        :returns: Shifts as a coordinates with ``-1<=x<=1`` and
            ``-1<=y<=1``.

        """
        if start_coordinate not in self.registry.all_coordinates:
            raise ValueError(f'The {start_coordinate} out of range!')
        if (
            start_coordinate,
            offset_cell_mark,
        ) not in self._marked_directions_cache:
            self._marked_directions_cache[
                start_coordinate, offset_cell_mark
            ] = tuple(
                direction
                for coordinate, direction in self.registry.offsets[
                    start_coordinate
                ]
                if self._cells_dict[coordinate].mark == offset_cell_mark
            )
        return self._marked_directions_cache[
            start_coordinate, offset_cell_mark
        ]

    def count(self, mark: str) -> int:
        """Return the number of occurrences of ``mark`` on the gameboard.

        :param mark:  The mark relative to which the cell will be
            matched by.

        """
        return self.grid.count(mark)

    def copy(self) -> SquareGameboard:
        """Return copy of current gameboard with exactly the same grid."""
        sg: SquareGameboard = SquareGameboard(
            grid=self.grid, gap=self._gap, axis=self._axis, _safety=False
        )
        sg._cells_dict = dict(self._cells_dict)
        sg._marked_directions_cache = dict(self._marked_directions_cache)
        sg._grid_cache = self._grid_cache
        sg.registry = self.registry
        return sg

    def print_grid(self, indent: str = '') -> None:
        """Print gameboard.

        :param indent:  Indent which will be added before each line.

        """
        if indent:
            grid: str = '\n'.join(
                f'{indent}{line}' for line in str(self).split('\n')
            )
        else:
            grid = str(self)
        logger.info(grid)
        self._default_paint()

    def _default_paint(self) -> None:
        if self.colorized:
            self._colors_dict = {
                coordinate: self.mark_colors[self._cells_dict[coordinate].mark]
                for coordinate in self._cells_dict
            }
