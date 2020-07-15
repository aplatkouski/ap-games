import pytest
from ap_games.types import Cell
from ap_games.types import Coordinate
from ap_games.gameboard.gameboard import SquareGameboard
from .conftest import SIZE


def test_size(square_gameboard_2x2):
    assert SIZE == square_gameboard_2x2.size


def test_surface(square_gameboard_2x2):
    assert " " * (SIZE ** 2) == square_gameboard_2x2.surface


def test_columns(square_gameboard_2x2):
    columns = (
        (
            Cell(coordinate=Coordinate(x=1, y=2), label=" "),
            Cell(coordinate=Coordinate(x=1, y=1), label=" "),
        ),
        (
            Cell(coordinate=Coordinate(x=2, y=2), label=" "),
            Cell(coordinate=Coordinate(x=2, y=1), label=" "),
        ),
    )
    assert columns == square_gameboard_2x2.columns


def test_rows(square_gameboard_2x2):
    rows = (
        (
            Cell(coordinate=Coordinate(x=1, y=2), label=" "),
            Cell(coordinate=Coordinate(x=2, y=2), label=" "),
        ),
        (
            Cell(coordinate=Coordinate(x=1, y=1), label=" "),
            Cell(coordinate=Coordinate(x=2, y=1), label=" "),
        ),
    )
    assert rows == square_gameboard_2x2.rows


def test_diagonals(square_gameboard_2x2):
    diagonals = (
        (
            Cell(coordinate=Coordinate(x=1, y=2), label=" "),
            Cell(coordinate=Coordinate(x=2, y=1), label=" "),
        ),
        (
            Cell(coordinate=Coordinate(x=2, y=2), label=" "),
            Cell(coordinate=Coordinate(x=1, y=1), label=" "),
        ),
    )
    assert diagonals == square_gameboard_2x2.diagonals


def test_cells(square_gameboard_2x2):
    cells = (
        Cell(coordinate=Coordinate(x=1, y=2), label=' '),
        Cell(coordinate=Coordinate(x=2, y=2), label=' '),
        Cell(coordinate=Coordinate(x=1, y=1), label=' '),
        Cell(coordinate=Coordinate(x=2, y=1), label=' '),
    )
    assert cells == square_gameboard_2x2.cells


def test_available_steps(square_gameboard_2x2):
    available_steps = (
        Coordinate(x=1, y=2),
        Coordinate(x=2, y=2),
        Coordinate(x=1, y=1),
        Coordinate(x=2, y=1),
    )
    assert available_steps == square_gameboard_2x2.available_steps


def test_count(square_gameboard_2x2):
    assert SIZE ** 2 == square_gameboard_2x2.count(label=" ")


def test_get_offset_cell(square_gameboard_2x2):
    x = 1
    y = 1
    coordinate = Coordinate(x=x, y=y)
    cell = Cell(coordinate=Coordinate(x=x + x, y=y + y), label=" ")
    assert cell == square_gameboard_2x2.get_offset_cell(
        coordinate=coordinate, shift=coordinate
    )


def test_label(square_gameboard_2x2):
    square_gameboard_2x2 = SquareGameboard(surface=" " * (SIZE ** 2))
    assert 1 == square_gameboard_2x2.label(coordinate=Coordinate(x=1, y=1), label="X")


def test_gameboard_1x1_too_small():
    with pytest.raises(ValueError) as exc:
        SquareGameboard(surface=" ")
    assert "The size of the gameboard must be between 2 and 9!" == str(exc.value)


def test_gameboard_10x10_too_larg():
    with pytest.raises(ValueError) as exc:
        SquareGameboard(surface=" " * 100)
    assert "The size of the gameboard must be between 2 and 9!" == str(exc.value)


def test_not_square_gameboard():
    surface = " " * 5
    with pytest.raises(ValueError) as exc:
        SquareGameboard(surface=surface)
    assert (
            "The gameboard must be square "
            f"({int(len(surface) ** (1 / 2))}^2 != {len(surface)})!"
            == str(exc.value)
    )
