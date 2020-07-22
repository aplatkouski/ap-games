from __future__ import annotations

from typing import TYPE_CHECKING

import pytest  # type: ignore
from ap_games.ap_types import Coordinate
from ap_games.game.game_base import GameBase
from ap_games.player.player import Player

if TYPE_CHECKING:
    from typing import Optional
    from typing import NoReturn


@pytest.fixture  # type: ignore
def game() -> GameBase:
    return GameBase(surface="XO X")


@pytest.fixture  # type: ignore
def player(game: GameBase) -> Player:
    return Player("user", game=game, label="X")


def test_construction(player: Player) -> Optional[NoReturn]:
    assert player


def test_game(game: GameBase, player: Player) -> Optional[NoReturn]:
    assert game == player.game


def test_label(player: Player) -> Optional[NoReturn]:
    assert "X" == player.label


def test_go(player: Player) -> Optional[NoReturn]:
    assert Coordinate(x=1, y=1) == player.go()
