from __future__ import annotations

from typing import cast
from typing import TYPE_CHECKING

from ap_games.ap_collections import Coordinate
from ap_games.ap_collections import GameStatus
from ap_games.ap_typing import PlayerType
from ap_games.game.reversi import Reversi

if TYPE_CHECKING:
    from ap_games.ap_typing import Coordinates


def test_construction() -> None:
    user: PlayerType = cast(PlayerType, 'user')
    reversi: Reversi = Reversi(grid=' ' * 64, player_types=(user, user))
    assert ' ' * 64 == reversi.gameboard.grid_as_string
    assert 'user' == reversi.players[0].type_
    assert 'user' == reversi.players[1].type_


def test_get_available_moves(reversi_user_user: Reversi) -> None:
    available_moves: Coordinates = (
        Coordinate(6, 5),
        Coordinate(3, 4),
        Coordinate(5, 6),
        Coordinate(4, 3),
    )
    assert available_moves == reversi_user_user.get_available_moves()


def test_get_score(reversi_user_user: Reversi) -> None:
    assert 0 == reversi_user_user.get_score(
        gameboard=reversi_user_user.gameboard,
        player_mark=reversi_user_user.players[0].mark,
    )


def test_get_status(reversi_user_user: Reversi) -> None:
    assert (
        GameStatus(active=True, message='', must_skip=False)
        == reversi_user_user.get_status()
    )
