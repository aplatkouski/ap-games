import pytest

from ap_games.game.game_base import GameBase
from ap_games.player.player import Player
from ap_games.types import Coordinate


@pytest.fixture
def game() -> GameBase:
    return GameBase(surface="XO X")


@pytest.fixture
def player(game) -> Player:
    return Player("user", game=game, label="X")


def test_construction(player):
    assert player


def test_game(game, player):
    assert game == player.game


def test_label(player):
    assert "X" == player.label


def test_go(player):
    assert Coordinate(x=1, y=1) == player.go()
