import pytest

from ap_games.ap_types import Coordinate
from ap_games.ap_types import GameStatus
from ap_games.game.reversi import Reversi


@pytest.fixture
def reversi_w_2users() -> Reversi:
    return Reversi(player_types=("user", "user"))


def test_construction():
    reversi = Reversi(surface=" " * 64, player_types=("user", "user"))
    assert " " * 64 == reversi.gameboard.surface
    assert "user" == reversi.players[0].type
    assert "user" == reversi.players[1].type


def test_available_steps(reversi_w_2users):
    available_steps = (
        Coordinate(3, 4),
        Coordinate(5, 6),
        Coordinate(6, 5),
        Coordinate(4, 3),
    )
    assert available_steps == reversi_w_2users.available_steps()


def test_get_score(reversi_w_2users):
    assert 0 == reversi_w_2users.get_score(
        gameboard=reversi_w_2users.gameboard, player=reversi_w_2users.players[0]
    )


def test_get_status(reversi_w_2users):
    assert GameStatus(True, '', False) == reversi_w_2users.get_status()
