from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from ap_games.log import log
from ap_games.types import Cell
from ap_games.types import Coordinate
from ap_games.types import EMPTY

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Iterable
    from typing import List
    from typing import Tuple
    from ap_games.types import Side

__ALL__ = ['SquareGameboard']


class SquareGameboard:
    """Implementation square game board with size from 2 to 9.

    :param surface: The surface or board, represented as a string, where
     each character is mapped to a cell left to right top to bottom.
    :param gap: ``" "`` by default.  Defines the gap that will be
     printed between cells in a row.
    :param axis: ``False`` by default.  If ``True`` print axis.

    :ivar _size: The size of gameboard from 2 to 9.

    """

    undefined_coordinate: ClassVar[Coordinate] = Coordinate(x=-1, y=-1)
    undefined_cell: ClassVar[Cell] = Cell(coordinate=undefined_coordinate, label="")

    def __init__(
        self, *, surface: str = EMPTY * 9, gap: str = " ", axis: bool = False
    ) -> None:

        size: int = int(len(surface) ** (1 / 2))
        if (size <= 1) or (size > 9):
            raise ValueError("The size of the gameboard must be between 2 and 9!")
        if size ** 2 != len(surface):
            raise ValueError(
                f"The gameboard must be square ({size}^2 != {len(surface)})!"
            )
        self._size: int = size

        self._surface: str = surface
        self._gap: str = gap
        self._axis: bool = axis

    def __str__(self) -> str:
        horizontal_border: str = (
            ("  " if self._axis else "")
            + "-" * (self._size + len(self._gap) * (self._size + 1) + 2)
        )

        surface: str = f"\n".join(
            (f"{self._size - num} " if self._axis else "")
            + f"|{self._gap}"
            + f"{self._gap}".join(cell.label for cell in row)
            + f"{self._gap}|"
            for num, row in enumerate(self.rows)
        )

        col_nums: str = f"{self._gap}".join(map(str, range(1, self._size + 1)))

        board: str = (
            f"{horizontal_border}\n"
            f"{surface}\n"
            f"{horizontal_border}"
            + (f"\n   {self._gap}{col_nums}{self._gap}" if self._axis else "")
        )
        return board

    def __iter__(self) -> Iterable[str]:
        return iter(self._surface)

    def __len__(self) -> int:
        return len(self._surface)

    def __call__(self, x: int, y: int) -> Cell:
        """Return cell by coordinates as namedtuple with two fields:
        ``coordinate`` and ``label``.

        :param x: Column number starts with 1 from left side of
         gameboard.
        :param y: Row number starts with 1 from bottom of gameboard.

        :return: The cell by the coordinates or
         :attr:`.SquareGameboard.undefined_cell` if coordinates are
         incorrect.

        """
        if (1 <= y <= self._size) and (1 <= x <= self._size):
            index: int = self._coordinate_to_index(x=x, y=y)
            return Cell(coordinate=Coordinate(x, y), label=self._surface[index])
        return self.undefined_cell

    @cached_property
    def size(self) -> int:
        return self._size

    @property
    def surface(self) -> str:
        return self._surface

    @property
    def columns(self) -> Tuple[Side, ...]:
        """Return all columns of gameboard as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        first_index_of_each_column = range(self._size)
        columns: List[Side] = list()
        for index in first_index_of_each_column:
            columns.append(self.cells[index :: self._size])
        return tuple(columns)

    @property
    def rows(self) -> Tuple[Side, ...]:
        """Return all rows of gameboard as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        first_index_of_each_row = range(0, self._size ** 2 - 1, self._size)
        rows: List[Side] = list()
        for index in first_index_of_each_row:
            rows.append(self.cells[index : index + self._size])
        return tuple(rows)

    @property
    def diagonals(self) -> Tuple[Side, ...]:
        """Return main and reverse diagonals as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        main_diagonal: Side = tuple(
            self.cells[i * (self._size + 1)] for i in range(self._size)
        )
        reverse_diagonal: Side = tuple(
            self.cells[(i + 1) * (self._size - 1)] for i in range(self._size)
        )
        return main_diagonal, reverse_diagonal

    @property
    def all_sides(self) -> Tuple[Side, ...]:
        """Return all rows, columns and diagonals as a tuple of all
        sides.  Where each side is a tuple of cells of the corresponding
        side.

        """
        return self.rows + self.columns + self.diagonals

    @property
    def cells(self) -> Tuple[Cell, ...]:
        """Return tuple of cells of the gameboard where each cell is
        a namedtuple with two fields:
         * ``coordinate``;
         * ``label`` (as string).

        """
        return tuple(
            Cell(coordinate=self._index_to_coordinate(index), label=label)
            for index, label in enumerate(self._surface)
        )

    @property
    def available_steps(self) -> Tuple[Coordinate, ...]:
        """Return coordinates of all available steps.  By default,
        coordinates of all ``EMPTY`` cells.

        """
        return tuple(cell.coordinate for cell in self.cells if cell.label == EMPTY)

    @property
    def copy(self) -> SquareGameboard:
        return SquareGameboard(surface=self._surface, gap=self._gap, axis=self._axis)

    def count(self, label: str) -> int:
        """Returns the number of occurrences of a :param:`label` on the
        gameboard.

        """
        return self._surface.count(label)

    def _coordinate_to_index(self, x: int, y: int) -> int:
        """Translates the cell coordinates represented by :param:`x` and
        :param:`y` into the index of this cell.

        :param x: Column number from left to right;
        :param y: Row number from bottom to top.

        Where an example for a 3x3 ``self._surface``::

            (1, 3) (2, 3) (3, 3)         0  1  2
            (1, 2) (2, 2) (3, 2)  ==>    3  4  5
            (1, 1) (2, 1) (3, 1)         6  7  8

        :return: the index of the corresponding cell between 1 and the
        size of the gameboard, or "-1" if the coordinates are incorrect.

        """
        if (1 <= x <= self._size) and (1 <= y <= self._size):
            return (x - 1) + self._size * (self._size - y)
        else:
            print(f"Coordinates should be from 1 to {self._size}!")
        return -1

    def _index_to_coordinate(self, index: int) -> Coordinate:
        """Convert the index to the coordinate.

        For details see :meth:`.SquareGameboard._coordinate_to_index`.

        """
        if 0 <= index < len(self._surface):
            x, y = divmod(index, self._size)
            column = y + 1
            row = self._size - x
            return Coordinate(column, row)
        return self.undefined_coordinate

    def get_offset_cell(self, coordinate: Coordinate, shift: Coordinate) -> Cell:
        """Return "Cell" (as tuple of coordinate and label) by
        coordinate calculated as algebraic sum of vectors:
        :param:`coordinate` and :param:`shift`.

        """
        return self(x=coordinate.x + shift.x, y=coordinate.y + shift.y)

    def print(self, indent: str = "") -> None:
        """Print gameboard."""
        if indent:
            result: str = "\n".join(f"{indent}{line}" for line in str(self).split("\n"))
        else:
            result = str(self)
        log.info(result)
        print(result)

    def label(self, coordinate: Coordinate, label: str, *, force: bool = False,) -> int:
        """Label cell of the gameboard with the ``coordinate``.

        :param coordinate: Position of cell as instance of namedtuple
         Coordinate(x, y).
        :param label: New label.  It will be set if ``force=True`` or
         cell with :param:`coordinate` is **empty** (``EMPTY``).
        :param force: ``False`` by default.  When ``True`` it doesn't
         matter if cell is **empty** or not.

        :return: count of labeled cell with :param:`label`.

        """
        index: int = self._coordinate_to_index(*coordinate)
        if 0 <= index < len(self._surface):
            if force or self._surface[index] == EMPTY:
                self._surface = label.join(
                    (self._surface[:index], self._surface[index + 1 :])
                )
                return 1
            print("This cell is occupied! Choose another one!")
        return 0
