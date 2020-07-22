from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cached_property
from platform import platform
from typing import TYPE_CHECKING
import logging

from ap_games.ap_types import Cell
from ap_games.ap_types import Coordinate
from ap_games.ap_types import EMPTY
from ap_games.ap_types import O
from ap_games.ap_types import Offset
from ap_games.ap_types import X
from ap_games.log import log

if TYPE_CHECKING:
    from typing import Any
    from typing import ClassVar
    from typing import Counter as typing_Counter
    from typing import Dict
    from typing import Final
    from typing import List
    from typing import Tuple

    from ap_games.ap_types import Directions
    from ap_games.ap_types import Labels
    from ap_games.ap_types import Side
    from ap_games.ap_types import Size

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


class GameboardRegistry:

    __slots__ = [
        "offsets",
        "all_coordinates",
        "index_to_coordinate",
        "__dict__",
    ]

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
        if (size <= 1) or (size > 9):
            raise ValueError(
                "The size of the gameboard must be between 2 and 9!"
            )
        self.index_to_coordinate: Dict[int, Coordinate] = dict()
        self.offsets: Dict[Coordinate, Tuple[Offset, ...]] = dict()
        self._fill_index_to_coordinate(size=size)
        self.all_coordinates: Final[Tuple[Coordinate, ...]] = tuple(
            self.index_to_coordinate.values()
        )
        self._fill_offsets()

    def _fill_index_to_coordinate(self, size: int) -> None:
        """Convert the index of the cell (label of surface) into the
        coordinate of this cell.

        :param size: The size of the corresponding gameboard.

        Where an example for a 3x3 ``self.surface``::

            0 1 2         (1, 3) (2, 3) (3, 3)
            3 4 5   ==>   (1, 2) (2, 2) (3, 2)
            6 7 8         (1, 1) (2, 1) (3, 1)

        :return: Namedtuple ``Coordinate`` where x is column number from
        left to right, and y is row number from bottom to top.

        """
        for index in range(size ** 2):
            a, b = divmod(index, size)
            column: int = b + 1
            row: int = size - a
            self.index_to_coordinate[index] = Coordinate(column, row)

    def _fill_offsets(self) -> None:
        for coordinate in self.all_coordinates:
            offsets: List[Offset] = list()
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

    :param surface: The surface or board, represented as a string, where
     each character is mapped to a cell left to right top to bottom.
    :param gap: ``" "`` by default.  Defines the gap that will be
     printed between cells in a row.
    :param axis: ``False`` by default.  If ``True`` print axis.

    :ivar _size: The size of gameboard from 2 to 9.

    """

    undefined_coordinate: ClassVar[Coordinate] = Coordinate(x=0, y=0)
    undefined_cell: ClassVar[Cell] = Cell(
        coordinate=undefined_coordinate, label=""
    )

    label_colors: Dict[str, str] = {
        X: BColors.BLUE,
        O: BColors.GREEN,
        EMPTY: BColors.HEADER,
    }

    default_surface: str = EMPTY * 9

    _registries: Dict[Size, GameboardRegistry] = dict()

    def __new__(cls, **kwargs: Any) -> Any:
        surface = kwargs.get("surface", cls.default_surface)
        size: int = int(len(surface) ** (1 / 2))
        if size ** 2 != len(surface):
            raise ValueError(
                f"The gameboard must be square ({size}^2 != {len(surface)})!"
            )
        if size not in cls._registries:
            cls._registries[size] = GameboardRegistry(size=size)
        return super(SquareGameboard, cls).__new__(cls)

    def __init__(
        self,
        *,
        surface: str = default_surface,
        gap: str = " ",
        axis: bool = False,
        colorized: bool = True,
        _safety: bool = True,
    ) -> None:

        self.colorized: bool = colorized if _safety and platform().startswith(
            "Linux"
        ) else False

        size: int = int(len(surface) ** (1 / 2))
        self._size: Final[int] = size
        self._gap: Final[str] = gap
        self._axis: Final[bool] = axis

        self._cells_dict: Dict[Tuple[int, int], Cell] = dict()
        self._colors: Dict[Tuple[int, int], str] = dict()
        self._offset_directions_cache: Dict[
            Tuple[Coordinate, str], Directions,
        ] = dict()
        self._surface_cache: str = ""

        if _safety:
            self.registry: GameboardRegistry = self._registries[size]
            for index, label in enumerate(surface):
                coordinate = self.registry.index_to_coordinate[index]
                self._cells_dict[coordinate] = Cell(coordinate, label)
            self._default_paint()

    def __str__(self) -> str:
        horizontal_border: str = (
            ("  " if self._axis else "")
            + "-" * (self._size + len(self._gap) * (self._size + 1) + 2)
        )

        surface: str = "\n".join(
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

    @cached_property
    def size(self) -> int:
        return self._size

    @property
    def counter(self) -> typing_Counter[Labels]:
        return Counter(self.surface)

    @property
    def surface(self) -> str:
        """Return gameboard surface as a string.

        Example::

          -------
          | 0 1 |
          | 2 3 |   ===>   "0123"
          -------

        """
        if not self._surface_cache:
            self._surface_cache = "".join(
                cell.label for cell in self._cells_dict.values()
            )
        return self._surface_cache

    @property
    def columns(self) -> Tuple[Side, ...]:
        """Return all columns of gameboard as a tuple."""
        columns = tuple(
            tuple(
                cell
                for coordinate, cell in self._cells_dict.items()
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
          This behavior of the method is necessary for the correct
          printing ot the gameboard. To get rows in the coordinate order
          from button to top, use ``sorted`` method.

        """
        rows = tuple(
            tuple(
                cell
                for coordinate, cell in self._cells_dict.items()
                if coordinate[1] == row
            )
            for row in reversed(range(1, self._size + 1))
        )
        return tuple(rows)

    @property
    def diagonals(self) -> Tuple[Side, ...]:
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
        return tuple(self._cells_dict.values())

    @property
    def available_steps(self) -> Tuple[Coordinate, ...]:
        """Return coordinates of all available steps.  By default,
        coordinates of all ``EMPTY`` cells.

        """
        return tuple(
            cell.coordinate for cell in self.cells if cell.label == EMPTY
        )

    def labeled_coordinates(self, label: str) -> Tuple[Coordinate, ...]:
        return tuple(
            cell.coordinate for cell in self.cells if cell.label == label
        )

    @property
    def copy(self) -> SquareGameboard:
        """Return copy of current gameboard with exactly the same
        surface.

        """
        sg: SquareGameboard = SquareGameboard(
            surface=self.surface, gap=self._gap, axis=self._axis, _safety=False
        )
        sg._cells_dict = dict(self._cells_dict)
        sg._offset_directions_cache = dict(self._offset_directions_cache)
        sg._surface_cache = self._surface_cache
        sg.registry = self.registry
        return sg

    def count(self, label: str) -> int:
        """Returns the number of occurrences of a :param:`label` on the
        gameboard.

        """
        return self.surface.count(label)

    def offset_directions(
        self, coordinate: Coordinate, *, label: str,
    ) -> Tuple[Coordinate, ...]:
        # Reason for commenting: -7% of processing time.
        # if coordinate not in self.registry.all_coordinates:
        #     raise ValueError(f"The {coordinate}  out of range!")
        if (coordinate, label) not in self._offset_directions_cache:
            self._offset_directions_cache[coordinate, label] = tuple(
                offset_direction
                for coordinate, offset_direction in self.registry.offsets[
                    coordinate
                ]
                if self._cells_dict[coordinate].label == label
            )
        return self._offset_directions_cache[coordinate, label]

    def get_offset_cell(
        self, *, coordinate: Coordinate, shift: Coordinate
    ) -> Cell:
        """Return "Cell" by coordinate calculated as algebraic sum of
        vectors ``coordinate`` and ``shift``.

        :param coordinate: coordinate of init cell;
        :param shift: coordinate of direction.

        """
        return self._cells_dict.get(
            (coordinate.x + shift.x, coordinate.y + shift.y),
            self.undefined_cell,
        )

    def print(self, indent: str = "") -> None:
        """Print gameboard."""
        if indent:
            result: str = "\n".join(
                f"{indent}{line}" for line in str(self).split("\n")
            )
        else:
            result = str(self)
        if logging.INFO >= log.level:
            log.info(result)
        print(result)
        self._default_paint()

    def label(
        self, coordinate: Coordinate, label: str, *, force: bool = False,
    ) -> int:
        """Label cell of the gameboard with the ``coordinate``.

        :param coordinate: Position of cell as instance of namedtuple
         Coordinate(x, y).
        :param label: New label.  It will be set if ``force=True`` or
         cell with :param:`coordinate` is **empty** (``EMPTY``).
        :param force: ``False`` by default.  When ``True`` it doesn't
         matter if cell is **empty** or not.

        :return: count of labeled cell with :param:`label`.

        """
        if (
            force
            or self._cells_dict.get(coordinate, self.undefined_cell).label
            == EMPTY
        ):
            self._cells_dict[coordinate] = Cell(coordinate, label)
            if self.colorized:
                if force:
                    self._colors[coordinate] = BColors.TURQUOISE
                else:
                    self._colors[coordinate] = BColors.BOLD + BColors.TURQUOISE
            self._offset_directions_cache = dict()
            self._surface_cache = ""
            return 1
        print("This cell is occupied! Choose another one!")
        return 0

    def _default_paint(self) -> None:
        if self.colorized:
            self._colors = {
                coordinate: self.label_colors.get(
                    self._cells_dict[coordinate].label, BColors.HEADER
                )
                for coordinate in self._cells_dict
            }
