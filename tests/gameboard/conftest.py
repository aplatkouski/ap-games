import pytest
from ap_games.gameboard.gameboard import SquareGameboard

SIZE = 2


@pytest.fixture
def square_gameboard_2x2() -> SquareGameboard:
    return SquareGameboard(surface=" " * (SIZE ** 2))
