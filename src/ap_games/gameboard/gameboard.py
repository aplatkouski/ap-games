from __future__ import annotations

import functools
import weakref
from dataclasses import dataclass
from typing import TYPE_CHECKING

# from ap_games.log import log
from ap_games.ap_types import Cell
from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY

if TYPE_CHECKING:
    from typing import ClassVar
    from typing import Dict
    from typing import Final
    from typing import Literal
    from typing import Tuple
    from typing import Union
    from ap_games.ap_types import Side

__ALL__ = ["SquareGameboard"]


@dataclass(frozen=True)
class BColors:
    HEADER: Final[str] = "\033[35m"
    BLUE: Final[str] = "\033[34m"
    GREEN: Final[str] = "\033[32m"
    YELLOW: Final[str] = "\033[33m"
    TURQUOISE: Final[str] = "\033[36m"
    ENDC: Final[str] = "\033[0m"
    BOLD: Final[str] = "\033[1m"
    UNDERLINE: Final[str] = "\033[4m"


def memoized_method(*self_attrs):  # type: ignore
    """Decorator to wrap a method with a memoizing callable that saves
    up to the ``999`` most recent calls.

    :param method_name: name of decorated method as first argument;
    :param self_attrs: attributes of instance that can be used as
    arguments of ``cached_method``. The instance attributes from
    variable ``self_attrs`` MUST be hashable.

    TODO: Add type annotation

    """

    def decorator(meth):  # type: ignore
        @functools.wraps(meth)
        def wrapped_method(self, *args, **kwargs):  # type: ignore
            # We're storing the wrapped method inside the instance. If we had
            # a strong reference to self the instance would never die.
            self_weak = weakref.ref(self)

            keywords = dict()
            for attr_name in self_attrs:
                keywords[attr_name] = getattr(self_weak(), attr_name, None)
            method_name = meth.__name__
            keywords[method_name] = method_name
            new_keywords = {**keywords, **kwargs}

            @functools.wraps(meth)
            @functools.lru_cache(maxsize=999)
            def cached_method(*args, **new_keywords):  # type: ignore
                """Attributes from ``self_attrs`` are added as keyword
                parameters to ``cached_method``."""
                return meth(self_weak(), *args, **kwargs)

            setattr(self, meth.__name__, cached_method)
            return cached_method(*args, **kwargs)

        return wrapped_method

    return decorator


class SquareGameboard:
    """Implementation square game board with size from 2 to 9.

    :param surface: The surface or board, represented as a string, where
     each character is mapped to a cell left to right top to bottom.
    :param gap: ``" "`` by default.  Defines the gap that will be
     printed between cells in a row.
    :param axis: ``False`` by default.  If ``True`` print axis.

    :ivar _size: The size of gameboard from 2 to 9.

    """

    undefined_coordinate: ClassVar[Coordinate] = Coordinate(x=0, y=0)
    undefined_cell: ClassVar[Cell] = Cell(coordinate=undefined_coordinate, label="")

    _directions: Final[ClassVar[Tuple[Coordinate, ...]]] = (
        Coordinate(0, 1),  # top
        Coordinate(1, 1),  # right-top
        Coordinate(1, 0),  # right and so on
        Coordinate(1, -1),
        Coordinate(0, -1),
        Coordinate(-1, -1),
        Coordinate(-1, 0),
        Coordinate(-1, 1),
    )

    label_colors: Dict[str, str] = {
        "X": BColors.BLUE,
        "O": BColors.GREEN,
        " ": BColors.HEADER,
    }

    def __init__(
        self,
        *,
        surface: str = EMPTY * 9,
        gap: str = " ",
        axis: bool = False,
        colorized: bool = True,
    ) -> None:

        size: int = int(len(surface) ** (1 / 2))
        if (size <= 1) or (size > 9):
            raise ValueError("The size of the gameboard must be between 2 and 9!")
        if size ** 2 != len(surface):
            raise ValueError(
                f"The gameboard must be square ({size}^2 != {len(surface)})!"
            )
        self._size: Final[int] = size
        self._gap: Final[str] = gap
        self._axis: Final[bool] = axis

        self._cells: Dict[Tuple[int, int], Cell] = dict()
        self._colors: Dict[Tuple[int, int], str] = dict()

        for index, label in enumerate(surface):
            x, y = self._index_to_coordinate(index)
            self._cells[x, y] = Cell(coordinate=Coordinate(x=x, y=y), label=label)

        self.colorized: bool = colorized
        self._paint()
        self._offset_directions_cache: Dict[Coordinate, Tuple[Coordinate, ...]] = dict()

    def __str__(self) -> str:
        horizontal_border: str = (
            ("  " if self._axis else "")
            + "-" * (self._size + len(self._gap) * (self._size + 1) + 2)
        )

        surface: str = f"\n".join(
            (f"{self._size - num} " if self._axis else "")
            + f"|{self._gap}"
            + f"{self._gap}".join(
                (
                    self._colors[cell.coordinate.x, cell.coordinate.y]
                    if self.colorized
                    else ""
                )
                + cell.label
                + (BColors.ENDC if self.colorized else "")
                for cell in row
            )
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

    @functools.cached_property
    def size(self) -> int:
        return self._size

    @property
    def _surface(self) -> str:
        return "".join(cell.label for cell in self._cells.values())

    @property
    def columns(self) -> Tuple[Side, ...]:
        """Return all columns of gameboard as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        columns = tuple(
            tuple(
                cell
                for coordinate, cell in self._cells.items()
                if coordinate[0] == column
            )
            for column in range(1, self._size + 1)
        )
        return columns

    @property
    def rows(self) -> Tuple[Side, ...]:
        """Return all rows of gameboard as a tuple.

        Note::

          Rows are returned in the reverse order from top to button.
          To get rows in the coordinate order from button to top, use
          ``sorted`` method.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        rows = tuple(
            tuple(
                cell for coordinate, cell in self._cells.items() if coordinate[1] == row
            )
            for row in reversed(range(1, self._size + 1))
        )
        return tuple(rows)

    @property
    def diagonals(self) -> Tuple[Side, ...]:
        """Return main and reverse diagonals as a tuple.

        For details see :meth:`.SquareGameboard.all_sides`.

        """
        main_diagonal: Side = tuple(
            self._cells[num + 1, self._size - num] for num in range(self._size)
        )
        reverse_diagonal: Side = tuple(
            self._cells[num, num] for num in range(1, self._size + 1)
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
        return tuple(self._cells.values())

    @property
    def available_steps(self) -> Tuple[Coordinate, ...]:
        """Return coordinates of all available steps.  By default,
        coordinates of all ``EMPTY`` cells.

        """
        return tuple(cell.coordinate for cell in self.cells if cell.label == EMPTY)

    @property
    def copy(self) -> SquareGameboard:
        """Return copy of current gameboard with exactly the same
        surface.

        """
        sg: SquareGameboard = SquareGameboard(
            surface=self._surface, gap=self._gap, axis=self._axis
        )
        sg._offset_directions_cache = self._offset_directions_cache
        return sg

    def count(self, label: str) -> int:
        """Returns the number of occurrences of a :param:`label` on the
        gameboard.

        """
        return [cell.label for cell in self._cells.values()].count(label)

    @memoized_method("_size")  # type: ignore
    def _index_to_coordinate(self, index: int) -> Coordinate:
        """Convert the index of the cell (label of surface) into the
        coordinate of this cell.

        :param index: The index of the corresponding cell between 0 and
        the size of the gameboard.

        Where an example for a 3x3 ``self.surface``::

            0 1 2         (1, 3) (2, 3) (3, 3)
            3 4 5   ==>   (1, 2) (2, 2) (3, 2)
            6 7 8         (1, 1) (2, 1) (3, 1)

        :return: Namedtuple ``Coordinate`` where x is column number from
        left to right, and y is row number from bottom to top.

        """
        x, y = divmod(index, self._size)
        column = y + 1
        row = self._size - x
        return Coordinate(column, row)

    @memoized_method("_size")  # type: ignore
    def _offset_directions(self, coordinate: Coordinate) -> Tuple[Coordinate, ...]:
        return tuple(
            shift
            for shift in self._directions
            if (coordinate.x + shift.x, coordinate.y + shift.y) in self._cells
        )

    def offset_directions(
        self,
        coordinate: Coordinate,
        *,
        exclude_labels: Tuple[Union[Literal[" "], str], ...] = (),
    ) -> Tuple[Coordinate, ...]:
        if coordinate in self._offset_directions_cache:
            return self._offset_directions_cache[coordinate]
        if coordinate not in self._cells:
            raise ValueError(f"The {coordinate}  out of range!")
        if exclude_labels:
            result = tuple(
                direction
                for direction in self._offset_directions(coordinate)
                if self._cells[
                    coordinate.x + direction.x, coordinate.y + direction.y
                ].label
                not in exclude_labels
            )
        else:
            result = self._offset_directions(coordinate)
        self._offset_directions_cache[coordinate] = result
        return result

    def get_offset_cell(self, coordinate: Coordinate, shift: Coordinate) -> Cell:
        """Return "Cell" by coordinate calculated as algebraic sum of
        vectors ``coordinate`` and ``shift``.

        :param coordinate: coordinate of init cell;
        :param shift: coordinate of direction.

        """
        return self._cells.get(
            (coordinate.x + shift.x, coordinate.y + shift.y), self.undefined_cell
        )

    def print(self, indent: str = "") -> None:
        """Print gameboard."""
        if indent:
            result: str = "\n".join(f"{indent}{line}" for line in str(self).split("\n"))
        else:
            result = str(self)
        # log.info(result)
        print(result)
        self._paint()

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
        x, y = coordinate
        if force or self._cells.get((x, y), self.undefined_cell).label == EMPTY:
            self._cells[x, y] = Cell(Coordinate(x, y), label)
            if self.colorized:
                if force:
                    self._colors[x, y] = BColors.TURQUOISE
                else:
                    self._colors[x, y] = BColors.BOLD + BColors.TURQUOISE
            self._offset_directions_cache = dict()
            return 1
        print("This cell is occupied! Choose another one!")
        return 0

    def _paint(self) -> None:
        if self.colorized:
            for x, y in self._cells:
                self._colors[x, y] = self.label_colors.get(
                    self._cells[x, y].label, BColors.HEADER
                )
