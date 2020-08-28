from __future__ import annotations

from ap_games.ap_typing import Coordinate
from ap_games.game.game_base import TwoPlayerBoardGame
from ap_games.player.player import Player


def test_construction(player_user_x: Player) -> None:
    assert player_user_x


def test_game(game: TwoPlayerBoardGame, player_user_x: Player) -> None:
    assert game is player_user_x.game


def test_mark(player_user_x: Player) -> None:
    assert 'X' == player_user_x.mark


def test_move(player_user_x: Player) -> None:
    assert Coordinate(x=1, y=1) == player_user_x.move()
